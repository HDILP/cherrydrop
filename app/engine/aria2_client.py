"""aria2 RPC 客户端封装"""
import subprocess
import time
import threading
import logging
from typing import Optional, Callable, Dict, Any

import aria2p

from app.utils.config import Config
from app.engine.tracker_updater import TrackerUpdater, DEFAULT_SOURCES

logger = logging.getLogger(__name__)


class Aria2Client:
    """管理 aria2c 进程 + aria2p API 调用"""

    def __init__(self, config: Config):
        self.config = config
        self._process: Optional[subprocess.Popen] = None
        self._api: Optional[aria2p.API] = None
        self._running = False
        # Tracker 管理器
        self.tracker_updater = TrackerUpdater(
            sources=config.get("bt_tracker_sources", DEFAULT_SOURCES),
        )

    @property
    def api(self) -> Optional[aria2p.API]:
        return self._api

    @property
    def is_running(self) -> bool:
        return self._running

    def _find_aria2_binary(self) -> Optional[str]:
        """查找 aria2c 可执行文件路径（优先使用打包的二进制）"""
        import shutil
        # 1. 检查打包的二进制（resources/bin/ 目录）
        import os
        base = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "resources", "bin")
        import platform
        system = platform.system().lower()
        if system == "windows":
            candidates = [
                os.path.join(base, "win32", "aria2c.exe"),
                os.path.join(base, "win64", "aria2c.exe"),
            ]
        elif system == "darwin":
            candidates = [os.path.join(base, "darwin", "aria2c")]
        else:
            candidates = [os.path.join(base, "linux", "aria2c")]
        for c in candidates:
            if os.path.exists(c):
                if system != "windows":
                    os.chmod(c, 0o755)
                return c
        # 2. fallback: 系统 PATH
        return shutil.which("aria2c")

    def _resources_path(self) -> str:
        """获取 resources 目录的绝对路径"""
        import os
        return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "resources")

    def _conf_path(self) -> str:
        """获取 aria2.conf 路径"""
        return os.path.join(self._resources_path(), "aria2.conf")

    def _session_path(self) -> str:
        import os
        return os.path.join(
            os.path.dirname(self.config._path),
            "aria2.session"
        )

    def _dht_path(self) -> str:
        import os
        return os.path.join(
            os.path.dirname(self.config._path),
            "dht.dat"
        )

    def _build_aria2_args(self) -> list:
        """构建 aria2c 命令行参数（静态参数由 aria2.conf 提供，此处只传动态参数）"""
        args = [
            self._find_aria2_binary() or "aria2c",
            # 加载 motrix-next 配置文件
            f"--conf-path={self._conf_path()}",
            # ── RPC（不与 conf 冲突）──
            "--enable-rpc",
            "--rpc-listen-all",
            "--rpc-allow-origin-all",
            "--daemon=false",
            # ── 会话持久化 ──
            f"--save-session={self._session_path()}",
            f"--save-session-interval=30",
            f"--continue=true",
        ]
        import os
        if os.path.exists(self._session_path()):
            args.append(f"--input-file={self._session_path()}")

        # ── 基础下载参数（覆盖 conf 的默认值）──
        args += [
            f"--max-concurrent-downloads={self.config.get('max_concurrent_downloads', 5)}",
            f"--max-connection-per-server={self.config.get('max_connection_per_server', 16)}",
            f"--split={self.config.get('split', 5)}",
            f"--dir={self.config.get_download_dir()}",
        ]
        # 从 config 读取 tracker 列表注入
        bt_tracker = self.config.get("bt_tracker", "")
        if bt_tracker:
            args.append(f"--bt-tracker={bt_tracker}")
        # 代理支持（从分字段配置拼接完整地址）
        proxy_enable = self.config.get("proxy_enable", False)
        if proxy_enable:
            proxy_type = self.config.get("proxy_type", "socks5")
            proxy_host = self.config.get("proxy_host", "127.0.0.1")
            proxy_port = self.config.get("proxy_port", 1080)
            proxy_user = self.config.get("proxy_user", "")
            proxy_pass = self.config.get("proxy_pass", "")
            proxy_url = f"{proxy_type}://{proxy_host}:{proxy_port}"
            if proxy_user and proxy_pass:
                proxy_url = f"{proxy_type}://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}"
            elif proxy_user:
                proxy_url = f"{proxy_type}://{proxy_user}@{proxy_host}:{proxy_port}"
            args.append(f"--all-proxy={proxy_url}")
        return args

    def start(self) -> bool:
        """启动 aria2c 后台进程并连接 RPC"""
        if self._running:
            return True

        # 检查 aria2c 二进制是否存在
        binary = self._find_aria2_binary()
        if not binary:
            logger.error("aria2c 未找到（内置二进制缺失且系统 PATH 中无 aria2c）")
            return False

        try:
            # 启动 aria2c 子进程
            self._process = subprocess.Popen(
                self._build_aria2_args(),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            # 等 aria2c 启动 (轮询端口，最多等 5 秒)
            import socket
            rpc_port = int(self.config.get("aria2_rpc_url", "http://localhost:6800/rpc").split(":")[-1].split("/")[0])
            for _ in range(10):
                try:
                    s = socket.create_connection(("127.0.0.1", rpc_port), timeout=0.5)
                    s.close()
                    break
                except (ConnectionRefusedError, OSError):
                    time.sleep(0.5)
            else:
                raise RuntimeError(f"aria2c 在 5 秒内未在端口 {rpc_port} 上启动")

            # 连接 RPC
            client = aria2p.Client(port=6800)

            self._api = aria2p.API(client)
            # 测试连接
            client.get_version()
            self._running = True
            logger.info("aria2c 启动成功")

            # 启动后拉取最新 tracker 并开始定时更新
            if self.config.get("bt_tracker_auto_update", True):
                trackers = self.tracker_updater.fetch()
                if trackers:
                    self._on_tracker_updated(self.tracker_updater.get_tracker_string())
                self.tracker_updater.start_auto_update(callback=self._on_tracker_updated)

            return True

        except Exception as e:
            logger.error(f"aria2c 启动失败: {e}")
            self.stop()
            return False

    def stop(self):
        """停止 aria2c"""
        self._running = False
        if self._api:
            try:
                self._api.client.shutdown()
            except Exception:
                pass
            self._api = None
        if self._process:
            try:
                self._process.terminate()
                self._process.wait(timeout=5)
            except Exception:
                self._process.kill()
            self._process = None

    def add_uri(self, uri: str, options: Dict = None) -> Optional[str]:
        """添加下载任务，返回 GID"""
        if not self._api:
            return None
        try:
            result = self._api.add(uri, options=options or {})
            if isinstance(result, list) and len(result) > 0:
                return result[0].gid
            return result.gid
        except Exception as e:
            logger.error(f"添加任务失败: {e}")
            return None

    def pause(self, gid: str) -> bool:
        try:
            self._api.pause(gid)
            return True
        except Exception:
            return False

    def resume(self, gid: str) -> bool:
        try:
            self._api.resume(gid)
            return True
        except Exception:
            return False

    def remove(self, gid: str) -> bool:
        try:
            self._api.remove(gid)
            return True
        except Exception:
            return False

    def get_downloads(self) -> list:
        """获取所有活跃下载"""
        if not self._api:
            return []
        try:
            return self._api.get_downloads()
        except Exception:
            return []

    def get_global_stats(self) -> Dict[str, Any]:
        """获取全局统计"""
        if not self._api:
            return {"download_speed": 0, "upload_speed": 0, "num_active": 0}
        try:
            stats = self._api.get_global_stat()
            return {
                "download_speed": stats.download_speed,
                "upload_speed": stats.upload_speed,
                "num_active": stats.num_active,
                "num_waiting": stats.num_waiting,
                "num_stopped": stats.num_stopped,
            }
        except Exception:
            return {"download_speed": 0, "upload_speed": 0, "num_active": 0}

    def _on_tracker_updated(self, tracker_str: str):
        """Tracker 更新回调：将新列表写入配置并注入 aria2"""
        if not tracker_str:
            return
        self.config.set("bt_tracker", tracker_str)
        # 如果 aria2 正在运行，通过 changeGlobalOption 热更新
        if self._api:
            try:
                self._api.client.call("system.changeGlobalOption", {"bt-tracker": tracker_str})
                logger.info("Tracker: 已热更新到 aria2")
            except Exception as e:
                logger.warning(f"Tracker: 热更新失败: {e}")

    def get_peers(self, gid: str) -> list:
        """获取指定任务的 peer 列表"""
        if not self._api:
            return []
        try:
            # 通过原始 RPC 调用获取 peers
            result = self._api.client.call("aria2.getPeers", gid)
            return result if isinstance(result, list) else []
        except Exception:
            return []

    def __del__(self):
        self.stop()
