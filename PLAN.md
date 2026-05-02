# CherryDrop (樱花下载器) 完整开发计划

> 🎯 **目标:** 基于 PyQt5 + aria2 + amule 的轻量全协议下载器
>
> **架构:** PyQt5 GUI ↔ aria2p (JSON-RPC) ↔ aria2c 后台进程；可选 amulecmd 处理 ed2k
>
> **设计风格:** 浅色主题，#ffaab2 樱花粉主色，毛玻璃质感，图标按钮唤起独立窗口
>
> **技术栈:** Python 3.10+, PyQt5, aria2p, PyInstaller/Nuitka, GitHub Actions
>
> **仓库建议:** `cherrydrop`

---

## 迭代 0: 项目脚手架

### Task 0.1: 创建项目目录和虚拟环境

**目标:** 项目骨架立起来

**步骤:**

```bash
mkdir -p cherrydrop
cd cherrydrop
python3 -m venv .venv
source .venv/bin/activate
```

### Task 0.2: 创建项目目录结构

**目标:** 所有目录就位

**文件：**
- 创建整个树

```bash
mkdir -p app/engine app/widgets app/dialogs app/utils resources/icons resources/themes
```

最终结构：
```
cherrydrop/
├── main.py                  # 入口
├── app/
│   ├── __init__.py
│   ├── engine/
│   │   ├── __init__.py
│   │   ├── aria2_client.py   # aria2p 封装
│   │   └── amule_client.py   # amulecmd 封装 (ed2k)
│   ├── widgets/
│   │   ├── __init__.py
│   │   ├── task_list.py      # 下载任务列表
│   │   └── progress_bar.py   # 自定义毛玻璃进度条
│   ├── dialogs/
│   │   ├── __init__.py
│   │   ├── add_task.py       # 添加下载对话框
│   │   └── settings.py       # 设置窗口
│   └── utils/
│       ├── __init__.py
│       ├── config.py         # settings.json 读写
│       └── theme.py          # QSS 样式表加载
├── resources/
│   ├── icons/                # SVG 图标
│   └── themes/
│       └── cherry.qss        # 全局 QSS 样式
└── requirements.txt
```

### Task 0.3: 写 requirements.txt

**文件：** 创建 `cherrydrop/requirements.txt`

```
PyQt5>=5.15.0
aria2p>=0.12.0
requests>=2.28.0
```

### Task 0.4: 各 `__init__.py` 文件写空

**文件：** 所有 `__init__.py` 只需包含一行或为空

```python
# app/__init__.py
"""CherryDrop - 樱色轻量下载器"""

# app/engine/__init__.py
# app/widgets/__init__.py
# app/dialogs/__init__.py
# app/utils/__init__.py
# 这些文件留空即可
```

### Task 0.5: 写 .gitignore

**文件：** 创建 `cherrydrop/.gitignore`

```
# Python
__pycache__/
*.py[cod]
.venv/
venv/
*.egg-info/
dist/
build/
*.spec

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Config
settings.json
aria2.session
```

### Task 0.6: 创建 main.py 骨架

**文件：** 创建 `cherrydrop/main.py`

```python
"""CherryDrop 入口"""
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("CherryDrop")
    app.setOrganizationName("CherryDrop")

    # 后面会逐步替换为真正的 MainWindow
    from PyQt5.QtWidgets import QLabel
    w = QLabel("CherryDrop loading...")
    w.setAlignment(Qt.AlignCenter)
    w.resize(400, 60)
    w.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
```

**验证:** `python main.py` 应弹出一个小窗口显示文字

---

## 迭代 1: 配置与主题系统

### Task 1.1: config.py — JSON 配置读写

**文件：** 创建 `cherrydrop/app/utils/config.py`

```python
"""JSON 配置管理器"""
import json
import os
from pathlib import Path


DEFAULT_CONFIG = {
    "download_dir": str(Path.home() / "Downloads"),
    "aria2_rpc_url": "http://localhost:6800/rpc",
    "aria2_rpc_token": "",
    "max_concurrent_downloads": 5,
    "max_connection_per_server": 16,
    "split": 5,
    "speed_limit_download": 0,    # 0 = unlimited (KB/s)
    "speed_limit_upload": 0,      # 0 = unlimited (KB/s)
    "theme": "cherry",
    "auto_start_aria2": True,
    "minimize_to_tray": True,
    "language": "zh_CN",
    # ── BT 网络优化 ──
    "bt_tracker": "",              # 逗号分隔的 tracker 列表
    "bt_tracker_auto_update": True,# 每日自动更新 tracker
    "bt_tracker_sources": [        # tracker 数据源
        "https://cdn.jsdelivr.net/gh/XIU2/TrackersListCollection@master/best.txt",
        "https://cdn.jsdelivr.net/gh/ngosang/trackerslist@master/trackers_best.txt",
    ],
    "bt_max_peers": 50,
    "bt_enable_dht": True,
    "bt_enable_pex": True,
    "bt_enable_lpd": True,
    "bt_listen_port": "6881-6999",
    # ── 代理 ──
    "proxy_enable": False,
    "proxy_type": "socks5",        # http / socks5 / https
    "proxy_host": "127.0.0.1",
    "proxy_port": 1080,
    "proxy_user": "",
    "proxy_pass": "",
    "proxy_scope_download": True,  # 下载走代理
    "proxy_scope_tracker": True,   # tracker 更新走代理
}


class Config:
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "settings.json"
            )
        self._path = config_path
        self._data = DEFAULT_CONFIG.copy()
        self._load()

    def _load(self):
        if os.path.exists(self._path):
            try:
                with open(self._path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    self._data.update(loaded)
            except (json.JSONDecodeError, IOError):
                pass

    def save(self):
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)

    def get(self, key: str, default=None):
        return self._data.get(key, default)

    def set(self, key: str, value):
        self._data[key] = value
        self.save()

    @property
    def data(self):
        return self._data.copy()

    def get_download_dir(self) -> str:
        dd = self._data.get("download_dir", "")
        dd = os.path.expanduser(dd)
        os.makedirs(dd, exist_ok=True)
        return dd
```

### Task 1.2: cherry.qss — 毛玻璃浅色主题 QSS

**文件：** 创建 `cherrydrop/resources/themes/cherry.qss`

```css
/* CherryDrop 浅色毛玻璃主题 */
/* 主色调: #ffaab2 (樱花粉) */

/* 全局默认 */
QWidget {
    font-family: "SF Pro Display", "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
    font-size: 13px;
    color: #2d2d2d;
    background-color: transparent;
}

/* 主窗口 - 毛玻璃效果 */
#MainWindow {
    background-color: rgba(255, 255, 255, 0.75);
    border: 1px solid rgba(255, 170, 178, 0.3);
}

/* 工具栏区域 */
QFrame#ToolBar {
    background-color: rgba(255, 255, 255, 0.5);
    border-bottom: 1px solid rgba(0, 0, 0, 0.06);
    padding: 4px;
}

/* 按钮 - 纯图标，悬停变色 */
QPushButton#IconButton {
    background-color: transparent;
    border: none;
    border-radius: 8px;
    padding: 8px;
    min-width: 36px;
    min-height: 36px;
}

QPushButton#IconButton:hover {
    background-color: rgba(255, 170, 178, 0.2);
}

QPushButton#IconButton:pressed {
    background-color: rgba(255, 170, 178, 0.35);
}

/* 任务列表 */
QListWidget#TaskList {
    background-color: transparent;
    border: none;
    outline: none;
}

QListWidget#TaskList::item {
    border-radius: 10px;
    padding: 10px 14px;
    margin: 2px 8px;
    background-color: rgba(255, 255, 255, 0.6);
    border: 1px solid rgba(0, 0, 0, 0.04);
}

QListWidget#TaskList::item:hover {
    background-color: rgba(255, 255, 255, 0.85);
    border: 1px solid rgba(255, 170, 178, 0.25);
}

QListWidget#TaskList::item:selected {
    background-color: rgba(255, 170, 178, 0.15);
    border: 1px solid rgba(255, 170, 178, 0.4);
}

/* 对话框 */
QDialog {
    background-color: rgba(255, 255, 255, 0.92);
    border: 1px solid rgba(0, 0, 0, 0.08);
    border-radius: 14px;
}

/* 输入框 */
QLineEdit {
    background-color: rgba(255, 255, 255, 0.8);
    border: 1px solid rgba(0, 0, 0, 0.1);
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
}

QLineEdit:focus {
    border: 1px solid #ffaab2;
    background-color: rgba(255, 255, 255, 0.95);
}

/* 进度条 */
QProgressBar {
    background-color: rgba(224, 224, 224, 0.5);
    border: none;
    border-radius: 4px;
    height: 6px;
    text-align: center;
    font-size: 0px;
}

QProgressBar::chunk {
    background: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 0,
        stop: 0 #ffaab2,
        stop: 1 #ff8a95
    );
    border-radius: 4px;
}

/* 滚动条 */
QScrollBar:vertical {
    background-color: transparent;
    width: 6px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background-color: rgba(0, 0, 0, 0.12);
    border-radius: 3px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: rgba(255, 170, 178, 0.5);
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* 下拉框 */
QComboBox {
    background-color: rgba(255, 255, 255, 0.8);
    border: 1px solid rgba(0, 0, 0, 0.1);
    border-radius: 8px;
    padding: 6px 12px;
}

QComboBox:on {
    border: 1px solid #ffaab2;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

/* 标签 */
QLabel#SpeedLabel {
    color: rgba(0, 0, 0, 0.5);
    font-size: 11px;
}

QLabel#FilenameLabel {
    font-size: 13px;
    font-weight: 500;
    color: #1a1a1a;
}

QLabel#PercentLabel {
    font-size: 12px;
    font-weight: 600;
    color: #ffaab2;
}

/* 右键菜单 */
QMenu {
    background-color: rgba(255, 255, 255, 0.95);
    border: 1px solid rgba(0, 0, 0, 0.08);
    border-radius: 10px;
    padding: 4px;
}

QMenu::item {
    padding: 8px 24px;
    border-radius: 6px;
}

QMenu::item:selected {
    background-color: rgba(255, 170, 178, 0.2);
}

QMenu::separator {
    height: 1px;
    background-color: rgba(0, 0, 0, 0.06);
    margin: 4px 8px;
}

/* 系统托盘菜单 */
QMenu#TrayMenu {
    background-color: rgba(255, 255, 255, 0.95);
    border: 1px solid rgba(0, 0, 0, 0.1);
    border-radius: 10px;
}

/* 状态栏 */
QStatusBar {
    background-color: rgba(255, 255, 255, 0.5);
    border-top: 1px solid rgba(0, 0, 0, 0.04);
    font-size: 11px;
    color: rgba(0, 0, 0, 0.45);
}
```

### Task 1.3: theme.py — 样式加载器

**文件：** 创建 `cherrydrop/app/utils/theme.py`

```python
"""主题管理器 - 加载 QSS 文件"""
import os


def load_theme(theme_name: str = "cherry") -> str:
    """加载 QSS 样式表"""
    theme_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "resources", "themes"
    )
    qss_path = os.path.join(theme_dir, f"{theme_name}.qss")

    if not os.path.exists(qss_path):
        return ""

    with open(qss_path, "r", encoding="utf-8") as f:
        return f.read()


def apply_theme(app, theme_name: str = "cherry"):
    """将样式表应用到 QApplication"""
    qss = load_theme(theme_name)
    if qss:
        app.setStyleSheet(qss)
```

---

## 迭代 2: aria2 引擎层

### Task 2.1: aria2_client.py — 核心封装

**文件：** 创建 `cherrydrop/app/engine/aria2_client.py`

```python
"""aria2 RPC 客户端封装"""
import subprocess
import time
import threading
import logging
from typing import Optional, Callable, Dict, Any

import aria2p

from app.utils.config import Config

logger = logging.getLogger(__name__)


class Aria2Client:
    """管理 aria2c 进程 + aria2p API 调用"""

    def __init__(self, config: Config):
        self.config = config
        self._process: Optional[subprocess.Popen] = None
        self._api: Optional[aria2p.API] = None
        self._running = False

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
        import platform, sys
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
        """构建 aria2c 命令行参数，包含 BT/DHT 加速优化"""
        args = [
            self._find_aria2_binary() or "aria2c",
            # ── RPC ──
            "--enable-rpc",
            "--rpc-listen-all",
            "--rpc-allow-origin-all",
            "--daemon=false",
            # ── 会话持久化 ──
            f"--save-session={self._session_path()}",
            f"--save-session-interval=30",
            f"--input-file={self._session_path()}",
            f"--continue=true",
            # ── 基础下载参数 ──
            f"--max-concurrent-downloads={self.config.get('max_concurrent_downloads', 5)}",
            f"--max-connection-per-server={self.config.get('max_connection_per_server', 16)}",
            f"--split={self.config.get('split', 5)}",
            f"--dir={self.config.get_download_dir()}",
            # ── BT/DHT 网络优化 (参考 motrix-next) ──
            "--enable-dht=true",
            "--enable-dht6=true",
            "--dht-listen-port=6881-6999",
            f"--dht-file-path={self._dht_path()}",
            "--dht-entry-point=dht.transmissionbt.com:6881",
            "--enable-peer-exchange=true",
            "--bt-enable-lpd=true",
            "--listen-port=6881-6999",
            "--bt-max-peers=128",
            "--bt-request-peer-speed-limit=100K",    # 防 ISP QoS 限速标记
            "--bt-detach-seed-only=true",              # 做种不计入活跃任务
            "--bt-save-metadata=true",                 # 磁力转 .torrent 缓存
            "--bt-load-saved-metadata=true",           # 重启时加载缓存的 .torrent
            "--bt-prioritize-piece=head",              # 优先下载首尾块 (预览)
            "--bt-seed-unverified=true",               # session 恢复时秒做种
            "--bt-remove-unselected-file=true",        # 清理未选文件
            "--bt-hash-check-seed=true",               # 完整性检查后继续做种
            "--peer-id-prefix=-TR3000-",               # 伪装成 Transmission 3.0
            "--peer-agent=Transmission/3.00",          # 伪装 UA
            "--user-agent=Transmission/3.00",
            # ── 性能优化 ──
            "--disk-cache=64M",
            "--auto-save-interval=10",
            "--file-allocation=none",
            "--no-file-allocation-limit=64M",
            "--min-split-size=1M",
            "--http-accept-gzip=true",
            "--content-disposition-default-utf8=true",
            "--remote-time=true",
            "--connect-timeout=10",
            "--timeout=10",
            "--max-tries=0",
            "--retry-wait=10",
            "--max-file-not-found=10",
            "--check-certificate=false",
        ]
        # 从 config 读取 tracker 列表注入
        bt_tracker = self.config.get("bt_tracker", "")
        if bt_tracker:
            args.append(f"--bt-tracker={bt_tracker}")
        # 代理支持
        proxy = self.config.get("proxy", "")
        if proxy:
            args.append(f"--all-proxy={proxy}")
        return args

    def start(self) -> bool:
        """启动 aria2c 后台进程并连接 RPC"""
        if self._running:
            return True

        try:
            # 启动 aria2c 子进程
            self._process = subprocess.Popen(
                self._build_aria2_args(),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            # 等 aria2c 启动 (轮询端口，最多等 5 秒)
            import socket
            rpc_port = 6800
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

    def __del__(self):
        self.stop()
```

### Task 2.2: amule_client.py — ed2k 接口（骨架）

**文件：** 创建 `cherrydrop/app/engine/amule_client.py`

```python
"""amulecmd 客户端封装 - 处理 ed2k 下载"""
import subprocess
import shutil
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class AmuleClient:
    """ed2k 下载引擎 - 通过 amulecmd 控制 aMule 后台"""

    def __init__(self):
        self._available = self._check_amule()

    def _check_amule(self) -> bool:
        """检查系统是否安装了 amulecmd"""
        return shutil.which("amulecmd") is not None

    @property
    def is_available(self) -> bool:
        return self._available

    def add_uri(self, ed2k_link: str) -> bool:
        """添加 ed2k 链接"""
        if not self._available:
            logger.warning("amulecmd 未安装，无法处理 ed2k 链接")
            return False
        try:
            result = subprocess.run(
                ["amulecmd", "-c", f"Add {ed2k_link}"],
                capture_output=True, text=True, timeout=30
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"amulecmd 添加 ed2k 失败: {e}")
            return False

    def get_install_guide(self) -> str:
        """返回各平台安装指南"""
        return (
            "ed2k 下载需要 aMule。请安装：\n"
            "  Linux: sudo apt install amule-daemon amule-utils\n"
            "  macOS: brew install amule\n"
            "  Windows: 请从我们的镜像站下载 (将在后续提供)"
        )
```

---

## 迭代 3: 进度条与任务列表组件

### Task 3.1: ProgressBar — 自定义毛玻璃进度条

**文件：** 创建 `cherrydrop/app/widgets/progress_bar.py`

```python
"""自定义毛玻璃质感进度条"""
from PyQt5.QtWidgets import QProgressBar
from PyQt5.QtCore import Qt


class GlassProgressBar(QProgressBar):
    """毛玻璃风格进度条，支持百分比文字"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("GlassProgressBar")
        self.setTextVisible(False)  # 由外层 Label 显示百分比
        self.setFixedHeight(6)

    def set_progress(self, completed: int, total: int):
        """兼容 aria2p 的 completed/total 数值"""
        if total <= 0:
            self.setValue(0)
            return
        pct = int(completed / total * 100)
        self.setValue(min(pct, 100))
```

### Task 3.2: TaskList — 下载任务列表

**文件：** 创建 `cherrydrop/app/widgets/task_list.py`

```python
"""下载任务列表 - 每个任务一行：文件名、进度条、速率"""
from PyQt5.QtWidgets import (
    QListWidget, QListWidgetItem, QWidget,
    QVBoxLayout, QHBoxLayout, QLabel, QMenu, QAction
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from app.widgets.progress_bar import GlassProgressBar


class TaskItemWidget(QWidget):
    """单个下载任务的自定义 widget"""

    def __init__(self, gid: str, filename: str, parent=None):
        super().__init__(parent)
        self.gid = gid
        self.filename = filename

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 4)
        layout.setSpacing(4)

        # 第一行：文件名 + 百分比
        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)

        self.name_label = QLabel(filename)
        self.name_label.setObjectName("FilenameLabel")
        self.name_label.setWordWrap(False)
        self.name_label.setStyleSheet("font-size: 13px; font-weight: 500; color: #1a1a1a;")

        self.percent_label = QLabel("0%")
        self.percent_label.setObjectName("PercentLabel")
        self.percent_label.setStyleSheet("font-size: 12px; font-weight: 600; color: #ffaab2;")
        self.percent_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        top_row.addWidget(self.name_label, 1)
        top_row.addWidget(self.percent_label)
        layout.addLayout(top_row)

        # 进度条
        self.progress_bar = GlassProgressBar()
        layout.addWidget(self.progress_bar)

        # 速率 + 状态
        self.speed_label = QLabel("等待中...")
        self.speed_label.setObjectName("SpeedLabel")
        self.speed_label.setStyleSheet("font-size: 11px; color: rgba(0,0,0,0.45);")
        layout.addWidget(self.speed_label)

        self.setLayout(layout)

    def update_status(self, completed: int, total: int, speed: str, status: str):
        """更新任务状态显示"""
        self.progress_bar.set_progress(completed, total)
        if total > 0:
            pct = int(completed / total * 100)
            self.percent_label.setText(f"{pct}%")
        else:
            self.percent_label.setText("--")

        if speed:
            self.speed_label.setText(f"↓ {speed}")
        else:
            self.speed_label.setText(status)


class TaskList(QListWidget):
    """下载任务列表组件"""

    # 信号
    pause_requested = pyqtSignal(str)    # gid
    resume_requested = pyqtSignal(str)
    remove_requested = pyqtSignal(str)
    open_folder_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TaskList")
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        self.setSelectionMode(self.SingleSelection)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollMode(self.ScrollPerPixel)
        self.setSpacing(2)

    def add_task(self, gid: str, filename: str) -> TaskItemWidget:
        """添加新任务到列表"""
        widget = TaskItemWidget(gid, filename)
        item = QListWidgetItem(self)
        item.setSizeHint(widget.sizeHint())
        # 保存 gid 到 item 的 data 中
        item.setData(Qt.UserRole, gid)
        self.addItem(item)
        self.setItemWidget(item, widget)
        return widget

    def get_task_widget(self, gid: str) -> TaskItemWidget:
        """根据 gid 找对应的 widget"""
        for i in range(self.count()):
            item = self.item(i)
            if item.data(Qt.UserRole) == gid:
                w = self.itemWidget(item)
                if isinstance(w, TaskItemWidget):
                    return w
        return None

    def remove_task(self, gid: str):
        """移除任务"""
        for i in range(self.count()):
            if self.item(i).data(Qt.UserRole) == gid:
                self.takeItem(i)
                break

    def _show_context_menu(self, pos):
        item = self.itemAt(pos)
        if not item:
            return
        gid = item.data(Qt.UserRole)

        menu = QMenu(self)
        menu.setObjectName("TaskMenu")

        pause_act = QAction("⏸ 暂停", self)
        pause_act.triggered.connect(lambda: self.pause_requested.emit(gid))

        resume_act = QAction("▶ 继续", self)
        resume_act.triggered.connect(lambda: self.resume_requested.emit(gid))

        remove_act = QAction("🗑 删除", self)
        remove_act.triggered.connect(lambda: self.remove_requested.emit(gid))

        open_act = QAction("📂 打开文件夹", self)
        open_act.triggered.connect(lambda: self.open_folder_requested.emit(gid))

        menu.addAction(pause_act)
        menu.addAction(resume_act)
        menu.addSeparator()
        menu.addAction(open_act)
        menu.addAction(remove_act)

        menu.exec_(self.mapToGlobal(pos))
```

---

## 迭代 4: 对话框

### Task 4.1: 添加下载对话框

**文件：** 创建 `cherrydrop/app/dialogs/add_task.py`

```python
"""添加下载任务对话框"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QLabel, QGroupBox, QComboBox, QCheckBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont


class AddTaskDialog(QDialog):
    """轻量添加下载对话框"""

    url_submitted = pyqtSignal(str, str)  # url, engine

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加下载")
        self.setFixedWidth(520)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)

        self._init_ui()
        self._apply_styles()

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # 标题
        title = QLabel("添加下载")
        title.setFont(QFont("", 16, QFont.Bold))
        title.setStyleSheet("color: #2d2d2d; margin-bottom: 4px;")
        layout.addWidget(title)

        # URL 输入
        url_label = QLabel("下载链接 (URL / 磁力链 / ed2k)")
        url_label.setStyleSheet("font-size: 12px; color: rgba(0,0,0,0.5);")
        layout.addWidget(url_label)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("http://... 或 magnet:?xt=... 或 ed2k://...")
        self.url_input.setFixedHeight(40)
        layout.addWidget(self.url_input)

        # 引擎选择
        engine_row = QHBoxLayout()
        engine_label = QLabel("下载引擎:")
        engine_label.setStyleSheet("font-size: 12px; color: rgba(0,0,0,0.5);")
        self.engine_combo = QComboBox()
        self.engine_combo.addItems(["自动检测", "aria2 (HTTP/BT/磁力)", "amule (ed2k)"])
        engine_row.addWidget(engine_label)
        engine_row.addWidget(self.engine_combo, 1)
        layout.addLayout(engine_row)

        # --- 高级选项 (默认折叠) ---
        self.advanced_check = QCheckBox("高级选项")
        self.advanced_check.setStyleSheet("font-size: 12px; color: rgba(0,0,0,0.4);")
        layout.addWidget(self.advanced_check)

        self.advanced_group = QGroupBox()
        self.advanced_group.setVisible(False)
        self.advanced_check.toggled.connect(self.advanced_group.setVisible)

        adv_layout = QVBoxLayout()

        # 下载路径
        path_row = QHBoxLayout()
        path_label = QLabel("保存到:")
        path_label.setStyleSheet("font-size: 12px;")
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("默认下载目录")
        path_row.addWidget(path_label)
        path_row.addWidget(self.path_input, 1)
        adv_layout.addLayout(path_row)

        # 重命名
        name_row = QHBoxLayout()
        name_label = QLabel("重命名:")
        name_label.setStyleSheet("font-size: 12px;")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("留空使用原文件名")
        name_row.addWidget(name_label)
        name_row.addWidget(self.name_input, 1)
        adv_layout.addLayout(name_row)

        self.advanced_group.setLayout(adv_layout)
        layout.addWidget(self.advanced_group)

        # 按钮行
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        cancel_btn = QPushButton("取消")
        cancel_btn.setFixedSize(90, 36)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(0,0,0,0.05);
                border: 1px solid rgba(0,0,0,0.1);
                border-radius: 8px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: rgba(0,0,0,0.08);
            }
        """)
        cancel_btn.clicked.connect(self.reject)

        confirm_btn = QPushButton("开始下载")
        confirm_btn.setFixedSize(120, 36)
        confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffaab2;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 600;
                color: white;
            }
            QPushButton:hover {
                background-color: #ff8a95;
            }
            QPushButton:pressed {
                background-color: #f07a85;
            }
        """)
        confirm_btn.clicked.connect(self._on_confirm)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(confirm_btn)
        layout.addLayout(btn_row)

        self.setLayout(layout)

    def _apply_styles(self):
        self.setStyleSheet("""
            QDialog {
                background-color: rgba(255,255,255,0.95);
                border: 1px solid rgba(0,0,0,0.08);
                border-radius: 14px;
            }
        """)

    def _on_confirm(self):
        url = self.url_input.text().strip()
        if not url:
            return
        engine = self.engine_combo.currentText()
        self.url_submitted.emit(url, engine)
        self.accept()

    def keyPressEvent(self, event):
        from PyQt5.QtGui import QKeyEvent
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self._on_confirm()
        else:
            super().keyPressEvent(event)
```

### Task 4.2: 设置对话框

**文件：** 创建 `cherrydrop/app/dialogs/settings.py`

```python
"""设置对话框"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QSpinBox, QGroupBox, QCheckBox,
    QFileDialog, QTabWidget, QWidget, QPlainTextEdit, QComboBox
)
from PyQt5.QtCore import Qt

from app.utils.config import Config


class SettingsDialog(QDialog):
    """程序设置窗口"""

    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("设置")
        self.setFixedSize(480, 420)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self._init_ui()
        self._load_config()

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("设置")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2d2d2d;")
        layout.addWidget(title)

        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: transparent;
            }
            QTabBar::tab {
                padding: 8px 16px;
                font-size: 12px;
                border: none;
            }
            QTabBar::tab:selected {
                color: #ffaab2;
                border-bottom: 2px solid #ffaab2;
            }
            QTabBar::tab:hover {
                color: #ff8a95;
            }
        """)

        # 下载页
        download_tab = QWidget()
        dl_layout = QVBoxLayout()

        # 下载路径
        path_row = QHBoxLayout()
        path_row.addWidget(QLabel("下载目录"))
        self.path_edit = QLineEdit()
        self.path_btn = QPushButton("浏览...")
        self.path_btn.setFixedWidth(60)
        self.path_btn.clicked.connect(self._browse_dir)
        path_row.addWidget(self.path_edit, 1)
        path_row.addWidget(self.path_btn)
        dl_layout.addLayout(path_row)

        # 并发数
        conc_row = QHBoxLayout()
        conc_row.addWidget(QLabel("最大并发下载"))
        self.concurrent_spin = QSpinBox()
        self.concurrent_spin.setRange(1, 20)
        conc_row.addWidget(self.concurrent_spin, 1)
        dl_layout.addLayout(conc_row)

        # 连接数
        conn_row = QHBoxLayout()
        conn_row.addWidget(QLabel("每服务器连接数"))
        self.conn_spin = QSpinBox()
        self.conn_spin.setRange(1, 64)
        conn_row.addWidget(self.conn_spin, 1)
        dl_layout.addLayout(conn_row)

        # 速度限制
        speed_row = QHBoxLayout()
        speed_row.addWidget(QLabel("下载限速 (KB/s, 0=不限)"))
        self.dl_speed_spin = QSpinBox()
        self.dl_speed_spin.setRange(0, 100000)
        self.dl_speed_spin.setSingleStep(100)
        speed_row.addWidget(self.dl_speed_spin, 1)
        dl_layout.addLayout(speed_row)

        dl_layout.addStretch()
        download_tab.setLayout(dl_layout)
        tabs.addTab(download_tab, "下载")

        # ── BT 网络页 ──
        bt_tab = QWidget()
        bt_layout = QVBoxLayout()

        # Tracker 自动更新
        self.tracker_auto = QCheckBox("每日自动更新 Tracker 列表")
        bt_layout.addWidget(self.tracker_auto)

        # 手动编辑 Tracker
        bt_layout.addWidget(QLabel("Tracker 列表 (每行一个，留空使用自动更新)"))
        self.tracker_edit = QPlainTextEdit()
        self.tracker_edit.setPlaceholderText("udp://tracker.opentrackr.org:1337/announce\nhttps://tracker.xxx.com/announce")
        self.tracker_edit.setFixedHeight(100)
        bt_layout.addWidget(self.tracker_edit)

        # BT 高级选项
        bt_form = QGroupBox("BT 协议选项")
        btf_layout = QVBoxLayout()

        dht_row = QHBoxLayout()
        self.bt_dht = QCheckBox("启用 DHT")
        self.bt_dht.setChecked(True)
        dht_row.addWidget(self.bt_dht)
        self.bt_pex = QCheckBox("启用 PEX")
        self.bt_pex.setChecked(True)
        dht_row.addWidget(self.bt_pex)
        self.bt_lpd = QCheckBox("启用 LPD")
        self.bt_lpd.setChecked(True)
        dht_row.addWidget(self.bt_lpd)
        btf_layout.addLayout(dht_row)

        peers_row = QHBoxLayout()
        peers_row.addWidget(QLabel("最大 Peers:"))
        self.bt_peers_spin = QSpinBox()
        self.bt_peers_spin.setRange(10, 200)
        peers_row.addWidget(self.bt_peers_spin)
        peers_row.addStretch()
        btf_layout.addLayout(peers_row)

        bt_form.setLayout(btf_layout)
        bt_layout.addWidget(bt_form)

        bt_layout.addStretch()
        bt_tab.setLayout(bt_layout)
        tabs.addTab(bt_tab, "BT 网络")

        # ── 代理页 ──
        proxy_tab = QWidget()
        proxy_layout = QVBoxLayout()

        self.proxy_enable = QCheckBox("启用代理")
        proxy_layout.addWidget(self.proxy_enable)

        proxy_type_row = QHBoxLayout()
        proxy_type_row.addWidget(QLabel("类型:"))
        self.proxy_type_combo = QComboBox()
        self.proxy_type_combo.addItems(["socks5", "http", "https"])
        proxy_type_row.addWidget(self.proxy_type_combo)
        proxy_layout.addLayout(proxy_type_row)

        proxy_host_row = QHBoxLayout()
        proxy_host_row.addWidget(QLabel("服务器:"))
        self.proxy_host_edit = QLineEdit()
        self.proxy_host_edit.setPlaceholderText("127.0.0.1")
        proxy_host_row.addWidget(self.proxy_host_edit, 1)
        proxy_host_row.addWidget(QLabel("端口:"))
        self.proxy_port_spin = QSpinBox()
        self.proxy_port_spin.setRange(1, 65535)
        self.proxy_port_spin.setValue(1080)
        proxy_host_row.addWidget(self.proxy_port_spin)
        proxy_layout.addLayout(proxy_host_row)

        proxy_auth_group = QGroupBox("认证 (可选)")
        proxy_auth_layout = QHBoxLayout()
        proxy_auth_layout.addWidget(QLabel("用户名:"))
        self.proxy_user_edit = QLineEdit()
        proxy_auth_layout.addWidget(self.proxy_user_edit, 1)
        proxy_auth_layout.addWidget(QLabel("密码:"))
        self.proxy_pass_edit = QLineEdit()
        self.proxy_pass_edit.setEchoMode(QLineEdit.Password)
        proxy_auth_layout.addWidget(self.proxy_pass_edit, 1)
        proxy_auth_group.setLayout(proxy_auth_layout)
        proxy_layout.addWidget(proxy_auth_group)

        proxy_scope_group = QGroupBox("代理作用域")
        proxy_scope_layout = QVBoxLayout()
        self.proxy_scope_dl = QCheckBox("下载流量走代理")
        self.proxy_scope_dl.setChecked(True)
        proxy_scope_layout.addWidget(self.proxy_scope_dl)
        self.proxy_scope_tr = QCheckBox("Tracker 更新走代理")
        self.proxy_scope_tr.setChecked(True)
        proxy_scope_layout.addWidget(self.proxy_scope_tr)
        proxy_scope_group.setLayout(proxy_scope_layout)
        proxy_layout.addWidget(proxy_scope_group)

        proxy_layout.addStretch()
        proxy_tab.setLayout(proxy_layout)
        tabs.addTab(proxy_tab, "代理")

        # 常规页
        general_tab = QWidget()
        gen_layout = QVBoxLayout()

        self.auto_aria2 = QCheckBox("自动启动 aria2")
        gen_layout.addWidget(self.auto_aria2)

        self.minimize_tray = QCheckBox("最小化到系统托盘")
        gen_layout.addWidget(self.minimize_tray)

        gen_layout.addStretch()
        general_tab.setLayout(gen_layout)
        tabs.addTab(general_tab, "常规")

        layout.addWidget(tabs)

        # 按钮
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        cancel_btn = QPushButton("取消")
        cancel_btn.setFixedSize(90, 36)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(0,0,0,0.05);
                border: 1px solid rgba(0,0,0,0.1);
                border-radius: 8px;
            }
            QPushButton:hover { background-color: rgba(0,0,0,0.08); }
        """)
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("保存")
        save_btn.setFixedSize(90, 36)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffaab2;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                color: white;
            }
            QPushButton:hover { background-color: #ff8a95; }
        """)
        save_btn.clicked.connect(self._save)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

        self.setLayout(layout)

    def _load_config(self):
        self.path_edit.setText(self.config.get("download_dir", ""))
        self.concurrent_spin.setValue(self.config.get("max_concurrent_downloads", 5))
        self.conn_spin.setValue(self.config.get("max_connection_per_server", 16))
        self.dl_speed_spin.setValue(self.config.get("speed_limit_download", 0))
        self.auto_aria2.setChecked(self.config.get("auto_start_aria2", True))
        self.minimize_tray.setChecked(self.config.get("minimize_to_tray", True))
        # BT 网络
        self.tracker_auto.setChecked(self.config.get("bt_tracker_auto_update", True))
        bt_tracker = self.config.get("bt_tracker", "")
        if bt_tracker:
            self.tracker_edit.setPlainText("\n".join(bt_tracker.split(",")))
        self.bt_dht.setChecked(self.config.get("bt_enable_dht", True))
        self.bt_pex.setChecked(self.config.get("bt_enable_pex", True))
        self.bt_lpd.setChecked(self.config.get("bt_enable_lpd", True))
        self.bt_peers_spin.setValue(self.config.get("bt_max_peers", 50))
        # 代理
        self.proxy_enable.setChecked(self.config.get("proxy_enable", False))
        proxy_type = self.config.get("proxy_type", "socks5")
        idx = self.proxy_type_combo.findText(proxy_type)
        if idx >= 0:
            self.proxy_type_combo.setCurrentIndex(idx)
        self.proxy_host_edit.setText(self.config.get("proxy_host", "127.0.0.1"))
        self.proxy_port_spin.setValue(self.config.get("proxy_port", 1080))
        self.proxy_user_edit.setText(self.config.get("proxy_user", ""))
        self.proxy_pass_edit.setText(self.config.get("proxy_pass", ""))
        self.proxy_scope_dl.setChecked(self.config.get("proxy_scope_download", True))
        self.proxy_scope_tr.setChecked(self.config.get("proxy_scope_tracker", True))

    def _save(self):
        self.config.set("download_dir", self.path_edit.text())
        self.config.set("max_concurrent_downloads", self.concurrent_spin.value())
        self.config.set("max_connection_per_server", self.conn_spin.value())
        self.config.set("speed_limit_download", self.dl_speed_spin.value())
        self.config.set("auto_start_aria2", self.auto_aria2.isChecked())
        self.config.set("minimize_to_tray", self.minimize_tray.isChecked())
        # BT 网络
        self.config.set("bt_tracker_auto_update", self.tracker_auto.isChecked())
        tracker_text = self.tracker_edit.toPlainText().strip()
        self.config.set("bt_tracker", ",".join(
            line.strip() for line in tracker_text.split("\n") if line.strip()
        ) if tracker_text else "")
        self.config.set("bt_enable_dht", self.bt_dht.isChecked())
        self.config.set("bt_enable_pex", self.bt_pex.isChecked())
        self.config.set("bt_enable_lpd", self.bt_lpd.isChecked())
        self.config.set("bt_max_peers", self.bt_peers_spin.value())
        # 代理
        self.config.set("proxy_enable", self.proxy_enable.isChecked())
        self.config.set("proxy_type", self.proxy_type_combo.currentText())
        self.config.set("proxy_host", self.proxy_host_edit.text())
        self.config.set("proxy_port", self.proxy_port_spin.value())
        self.config.set("proxy_user", self.proxy_user_edit.text())
        self.config.set("proxy_pass", self.proxy_pass_edit.text())
        self.config.set("proxy_scope_download", self.proxy_scope_dl.isChecked())
        self.config.set("proxy_scope_tracker", self.proxy_scope_tr.isChecked())
        self.accept()

    def _browse_dir(self):
        d = QFileDialog.getExistingDirectory(self, "选择下载目录", self.path_edit.text())
        if d:
            self.path_edit.setText(d)
```

---

## 迭代 5: 主窗口

### Task 5.1: MainWindow — 主界面组装

**文件：** 创建 `cherrydrop/app/main_window.py`

```python
"""CherryDrop 主窗口"""
import os
import logging
from typing import Optional

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSystemTrayIcon, QMenu, QAction,
    QApplication, QStatusBar, QFrame
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QFont

from app.widgets.task_list import TaskList
from app.dialogs.add_task import AddTaskDialog
from app.dialogs.settings import SettingsDialog
from app.engine.aria2_client import Aria2Client
from app.engine.amule_client import AmuleClient
from app.utils.config import Config

logger = logging.getLogger(__name__)


def human_speed(bytes_per_sec: int) -> str:
    """将字节/秒转换为人类可读的速度"""
    if bytes_per_sec >= 1024 * 1024:
        return f"{bytes_per_sec / 1024 / 1024:.1f} MB/s"
    elif bytes_per_sec >= 1024:
        return f"{bytes_per_sec / 1024:.0f} KB/s"
    else:
        return f"{bytes_per_sec} B/s"


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self, config: Config, aria2: Aria2Client, amule: AmuleClient):
        super().__init__()
        self.config = config
        self.aria2 = aria2
        self.amule = amule

        self.setObjectName("MainWindow")
        self.setWindowTitle("CherryDrop")
        self.resize(540, 640)
        self.setMinimumSize(400, 400)

        # 窗口属性 — 圆角（仅macOS/Win）
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        # 居中
        self._center()

        # 初始化 UI
        self._init_toolbar()
        self._init_task_list()
        self._init_statusbar()

        # 系统托盘
        self._init_tray()

        # 自动启动 aria2
        if self.config.get("auto_start_aria2", True):
            QTimer.singleShot(500, self._start_aria2)

        # 定时刷新
        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self._refresh_tasks)
        self._refresh_timer.start(2000)  # 每2秒刷新

    def _center(self):
        screen = QApplication.primaryScreen().geometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )

    def _init_toolbar(self):
        """顶栏 - 纯图标按钮"""
        toolbar = QFrame()
        toolbar.setObjectName("ToolBar")
        toolbar.setFixedHeight(52)

        layout = QHBoxLayout()
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(4)

        # 添加任务按钮
        self.add_btn = QPushButton("➕")
        self.add_btn.setObjectName("IconButton")
        self.add_btn.setToolTip("添加下载")
        self.add_btn.clicked.connect(self._show_add_dialog)

        # 设置按钮
        self.settings_btn = QPushButton("⚙️")
        self.settings_btn.setObjectName("IconButton")
        self.settings_btn.setToolTip("设置")
        self.settings_btn.clicked.connect(self._show_settings)

        # 弹性空间 — 标题居中或留空
        title_label = QLabel("🌸 CherryDrop")
        title_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #ffaab2;")
        title_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.add_btn)
        layout.addStretch()
        layout.addWidget(title_label)
        layout.addStretch()
        layout.addWidget(self.settings_btn)

        toolbar.setLayout(layout)
        self.setMenuWidget(toolbar)

    def _init_task_list(self):
        central = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.task_list = TaskList()
        self.task_list.pause_requested.connect(self._on_pause)
        self.task_list.resume_requested.connect(self._on_resume)
        self.task_list.remove_requested.connect(self._on_remove)
        self.task_list.open_folder_requested.connect(self._on_open_folder)

        layout.addWidget(self.task_list, 1)
        central.setLayout(layout)
        self.setCentralWidget(central)

    def _init_statusbar(self):
        self.status_bar = QStatusBar()
        self.status_bar.setObjectName("StatusBar")
        self.status_label = QLabel("🌸 就绪")
        self.speed_label = QLabel("↓ 0 B/s")
        self.status_bar.addWidget(self.status_label, 1)
        self.status_bar.addPermanentWidget(self.speed_label)
        self.setStatusBar(self.status_bar)

    def _init_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        # 用文字图标凑合，可后续替换为真实图标
        icon = QIcon.fromTheme("document-save")
        self.tray_icon.setIcon(icon)
        self.tray_icon.setToolTip("CherryDrop")

        tray_menu = QMenu()
        tray_menu.setObjectName("TrayMenu")

        show_action = QAction("显示窗口", self)
        show_action.triggered.connect(self.show_and_activate)
        tray_menu.addAction(show_action)

        quit_action = QAction("退出", self)
        quit_action.triggered.connect(self._quit_app)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

    def show_and_activate(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_and_activate()

    def _start_aria2(self):
        ok = self.aria2.start()
        if ok:
            self.status_label.setText("🌸 aria2 已连接")
        else:
            self.status_label.setText("⚠️ aria2 启动失败，请检查是否已安装")

    def _show_add_dialog(self):
        dialog = AddTaskDialog(self)
        dialog.url_submitted.connect(self._on_add_url)
        dialog.exec_()

    def _on_add_url(self, url: str, engine: str):
        gid = self.aria2.add_uri(url)
        if gid:
            # 从 URL 提取文件名
            filename = url.split("/")[-1] if "://" in url else url[:30] + "..."
            if "magnet" in url:
                filename = "磁力链接 - 等待元数据..."
            self.task_list.add_task(gid, filename)

    def _show_settings(self):
        dialog = SettingsDialog(self.config, self)
        dialog.exec_()

    def _on_pause(self, gid: str):
        self.aria2.pause(gid)

    def _on_resume(self, gid: str):
        self.aria2.resume(gid)

    def _on_remove(self, gid: str):
        self.aria2.remove(gid)
        self.task_list.remove_task(gid)

    def _on_open_folder(self, gid: str):
        import subprocess, platform
        download_dir = self.config.get_download_dir()
        if platform.system() == "Darwin":
            subprocess.Popen(["open", download_dir])
        elif platform.system() == "Windows":
            subprocess.Popen(["explorer", download_dir])
        else:
            subprocess.Popen(["xdg-open", download_dir])

    def _refresh_tasks(self):
        """每2秒刷新任务列表"""
        if not self.aria2.is_running:
            return

        downloads = self.aria2.get_downloads()
        if not downloads:
            return

        for dl in downloads:
            widget = self.task_list.get_task_widget(dl.gid)
            if widget:
                widget.update_status(
                    completed=dl.completed_length,
                    total=dl.total_length,
                    speed=human_speed(dl.download_speed),
                    status=dl.status,
                )
            else:
                # 新任务（可能是 session 恢复的）
                filename = dl.name or dl.gid[:8]
                w = self.task_list.add_task(dl.gid, filename)
                w.update_status(
                    completed=dl.completed_length,
                    total=dl.total_length,
                    speed=human_speed(dl.download_speed),
                    status=dl.status,
                )

        # 更新状态栏速度
        stats = self.aria2.get_global_stats()
        total_speed = human_speed(stats.get("download_speed", 0))
        self.speed_label.setText(f"↓ {total_speed}")

    def closeEvent(self, event):
        if self.config.get("minimize_to_tray", True):
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "CherryDrop",
                "已最小化到系统托盘",
                QSystemTrayIcon.Information,
                2000
            )
        else:
            self.aria2.stop()
            event.accept()

    def _quit_app(self):
        self.aria2.stop()
        QApplication.quit()
```

### Task 5.2: 更新 main.py — 整合所有组件

**文件：** 修改 `cherrydrop/main.py`

```python
"""CherryDrop 入口"""
import sys
import logging

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from app.utils.config import Config
from app.utils.theme import apply_theme
from app.engine.aria2_client import Aria2Client
from app.engine.amule_client import AmuleClient
from app.main_window import MainWindow


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(name)s: %(message)s",
    )


def main():
    setup_logging()

    app = QApplication(sys.argv)
    app.setApplicationName("CherryDrop")
    app.setOrganizationName("CherryDrop")

    # 高DPI支持
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # 加载配置
    config = Config()

    # 加载主题
    apply_theme(app, config.get("theme", "cherry"))

    # 初始化引擎
    aria2 = Aria2Client(config)
    amule = AmuleClient()

    # 创建主窗口
    window = MainWindow(config, aria2, amule)
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
```

---

## 迭代 6: BT 网络加速与 Tracker 管理

> **背景:** 中国网络环境下 P2P 下载面临 GFW 封锁、ISP 限速、CGNAT 等问题。
> 参考 motrix-next 的方案：Tracker 自动更新 + DHT/PEX/LPD 优化 + 代理支持。
> 本迭代新增：Tracker 自动更新模块、Peer 可视化、BT 参数 UI。

### Task 6.1: Tracker 自动更新模块

**文件：** 创建 `cherrydrop/app/engine/tracker_updater.py`

```python
"""BT Tracker 列表自动更新器

定时从开源 Tracker 集合拉取最新列表，注入 aria2 的 --bt-tracker 参数。
数据源：
  - XIU2/TrackersListCollection (CDN 镜像优先)
  - ngosang/trackerslist (CDN 镜像优先)
"""
import logging
import threading
import time
from typing import Optional, Callable
import requests

logger = logging.getLogger(__name__)

# 默认 Tracker 数据源 (CDN 镜像，国内可访问)
DEFAULT_SOURCES = [
    "https://cdn.jsdelivr.net/gh/XIU2/TrackersListCollection@master/best.txt",
    "https://cdn.jsdelivr.net/gh/ngosang/trackerslist@master/trackers_best.txt",
]

# aria2 的 --bt-tracker 参数长度限制 (~4KB 可用空间)
MAX_BT_TRACKER_LENGTH = 4000

# 更新间隔 (秒)
UPDATE_INTERVAL = 24 * 60 * 60  # 每天


class TrackerUpdater:
    """Tracker 列表管理器"""

    def __init__(self, sources: list = None, proxy: str = None):
        self.sources = sources or DEFAULT_SOURCES.copy()
        self._proxy = proxy
        self._trackers: list[str] = []
        self._last_update = 0.0
        self._timer: Optional[threading.Timer] = None
        self._running = False

    def set_proxy(self, proxy: str):
        self._proxy = proxy

    def set_sources(self, sources: list):
        self.sources = sources

    def fetch(self) -> list[str]:
        """从所有数据源拉取 tracker 列表，合并去重"""
        all_trackers: list[str] = []
        failures: list[str] = []

        for url in self.sources:
            try:
                proxies = {"http": self._proxy, "https": self._proxy} if self._proxy else None
                resp = requests.get(url, timeout=10, proxies=proxies)
                if resp.status_code == 200:
                    trackers = [
                        line.strip()
                        for line in resp.text.splitlines()
                        if line.strip() and not line.strip().startswith("#")
                    ]
                    all_trackers.extend(trackers)
                    logger.info(f"Tracker: 从 {url} 获取到 {len(trackers)} 个")
                else:
                    failures.append(f"{url} -> HTTP {resp.status_code}")
            except Exception as e:
                failures.append(f"{url} -> {e}")
                logger.warning(f"Tracker: 获取 {url} 失败: {e}")

        # 去重
        seen = set()
        unique = []
        for t in all_trackers:
            if t not in seen:
                seen.add(t)
                unique.append(t)

        self._trackers = unique
        self._last_update = time.time()
        logger.info(f"Tracker: 合并去重后共 {len(unique)} 个，失败 {len(failures)} 个")
        return unique

    def get_tracker_string(self) -> str:
        """返回逗号分隔的 tracker 字符串（限制长度）"""
        if not self._trackers:
            return ""
        result = ",".join(self._trackers)
        if len(result) <= MAX_BT_TRACKER_LENGTH:
            return result
        # 截断到最后一个完整的 tracker
        truncated = result[:MAX_BT_TRACKER_LENGTH]
        last_comma = truncated.rfind(",")
        if last_comma > 0:
            return truncated[:last_comma]
        return truncated

    def start_auto_update(self, callback: Callable = None):
        """启动定时自动更新"""
        self._running = True
        self._schedule_next(callback)

    def _schedule_next(self, callback: Callable = None):
        if not self._running:
            return
        now = time.time()
        if now - self._last_update >= UPDATE_INTERVAL:
            trackers = self.fetch()
            if callback:
                callback(self.get_tracker_string())
        self._timer = threading.Timer(3600, self._schedule_next, args=[callback])
        self._timer.daemon = True
        self._timer.start()

    def stop(self):
        self._running = False
        if self._timer:
            self._timer.cancel()
            self._timer = None
```

**验证:** 可以在 Python 中测试导入并调用 `fetch()` 看能否拉取到 tracker 列表。

### Task 6.2: 更新 aria2_client.py — 集成 TrackerUpdater

在 `Aria2Client` 中集成 Tracker 自动更新：

```python
# 在 __init__ 中新增
from app.engine.tracker_updater import TrackerUpdater

class Aria2Client:
    def __init__(self, config: Config):
        self.config = config
        self._process: Optional[subprocess.Popen] = None
        self._api: Optional[aria2p.API] = None
        self._running = False
        # Tracker 管理器
        self.tracker_updater = TrackerUpdater(
            sources=config.get("bt_tracker_sources", DEFAULT_SOURCES),
        )

    def _on_tracker_updated(self, tracker_str: str):
        """Tracker 更新回调：将新列表写入配置并注入 aria2"""
        if not tracker_str:
            return
        self.config.set("bt_tracker", tracker_str)
        # 如果 aria2 正在运行，通过 changeGlobalOption 热更新
        if self._api:
            try:
                self._api.change_global_option({"bt-tracker": tracker_str})
                logger.info("Tracker: 已热更新到 aria2")
            except Exception as e:
                logger.warning(f"Tracker: 热更新失败: {e}")

    def start(self) -> bool:
        """... 原有逻辑后追加 ..."""
        # 启动后拉取最新 tracker
        if self.config.get("bt_tracker_auto_update", True):
            trackers = self.tracker_updater.fetch()
            if trackers:
                self._on_tracker_updated(self.tracker_updater.get_tracker_string())
            self.tracker_updater.start_auto_update(callback=self._on_tracker_updated)
```

### Task 6.3: aria2_client.py — 新增 Peer 查询接口

在 `Aria2Client` 中新增获取 peer 信息的方法：

```python
    def get_peers(self, gid: str) -> list:
        """获取指定任务的 peer 列表"""
        if not self._api:
            return []
        try:
            # aria2p 不直接暴露 peers，通过原始 RPC 调用
            result = self._api.client.call("aria2.getPeers", gid)
            return result if isinstance(result, list) else []
        except Exception:
            return []
```

### Task 6.4: TaskItemWidget 扩展 — 显示 Peer 信息

在任务项中添加 peer 数量显示，右键菜单增加"查看 Peers"：

在 `cherrydrop/app/widgets/task_list.py` 中修改：

```python
# 在 TaskItemWidget.__init__ 中，speed_label 后增加
        self.peer_label = QLabel("")
        self.peer_label.setObjectName("PeerLabel")
        self.peer_label.setStyleSheet("font-size: 10px; color: rgba(0,0,0,0.35);")
        layout.addWidget(self.peer_label)

# 在 update_status 方法末尾
    def update_status(self, completed: int, total: int, speed: str, status: str, peers: list = None):
        """... 原有逻辑 ..."""
        if peers is not None:
            seeds = sum(1 for p in peers if p.get("amChoking", True) is False)
            leechs = len(peers) - seeds
            self.peer_label.setText(f"种子 {seeds} | 用户 {leechs}")
        else:
            self.peer_label.setText("")
```

### Task 6.5: 更新 _refresh_tasks — 传递 Peer 信息

在 `main_window.py` 的 `_refresh_tasks` 中：

```python
    def _refresh_tasks(self):
        """... 原有逻辑 ..."""
        for dl in downloads:
            peers = self.aria2.get_peers(dl.gid) if dl.status == "active" else []
            widget.update_status(
                completed=dl.completed_length,
                total=dl.total_length,
                speed=human_speed(dl.download_speed),
                status=dl.status,
                peers=peers,
            )
```

---

## 迭代 7: 便携打包与 aria2 二进制管理

> **目标:** CherryDrop 打包为单文件便携程序，内置 aria2 二进制，开箱即用。
> 用户无需单独安装 aria2，下载单文件即可运行。

### Task 7.1: aria2 二进制目录结构

在项目中创建 aria2 二进制目录：

```bash
# 各平台二进制存放位置
cherrydrop/resources/bin/
├── linux/
│   └── aria2c          # x86_64 Linux 静态编译
├── win32/
│   └── aria2c.exe      # Windows 32-bit
├── win64/
│   └── aria2c.exe      # Windows 64-bit
└── darwin/
    └── aria2c           # macOS x86_64 + arm64 (universal)
```

**获取二进制:** 从 aria2 官方 Release 下载:
- https://github.com/aria2/aria2/releases
- Linux: 使用静态编译版本 (musl 编译)
- macOS: `brew install aria2` 后复制 binary 或使用 Homebrew 的 bottle
- Windows: 使用官方发布的 exe

### Task 7.2: aria2 二进制下载脚本

**文件：** 创建 `scripts/download_aria2.py`

```python
"""下载各平台 aria2 二进制到 resources/bin/"""
import os
import sys
import platform
import urllib.request
import shutil
import tarfile
import zipfile

BASE_URL = "https://github.com/aria2/aria2/releases/download/release-1.37.0"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BIN_DIR = os.path.join(SCRIPT_DIR, "..", "resources", "bin")


def download_linux():
    url = f"{BASE_URL}/aria2-1.37.0-linux-x86_64-static.tar.gz"
    dest = os.path.join(BIN_DIR, "linux", "aria2c")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    print(f"下载 Linux aria2c...")
    urllib.request.urlretrieve(url, "/tmp/aria2-linux.tar.gz")
    with tarfile.open("/tmp/aria2-linux.tar.gz") as tf:
        for m in tf.getmembers():
            if m.name.endswith("aria2c"):
                tf.extract(m, "/tmp/")
                shutil.move(f"/tmp/{m.name}", dest)
    os.chmod(dest, 0o755)
    print(f"  -> {dest}")


def download_macos():
    url = f"{BASE_URL}/aria2-1.37.0-macos-universal-static.tar.gz"
    dest = os.path.join(BIN_DIR, "darwin", "aria2c")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    print(f"下载 macOS aria2c...")
    urllib.request.urlretrieve(url, "/tmp/aria2-macos.tar.gz")
    with tarfile.open("/tmp/aria2-macos.tar.gz") as tf:
        for m in tf.getmembers():
            if m.name.endswith("aria2c"):
                tf.extract(m, "/tmp/")
                shutil.move(f"/tmp/{m.name}", dest)
    os.chmod(dest, 0o755)
    print(f"  -> {dest}")


def download_windows():
    for arch, suffix in [("win64", "win-64bit"), ("win32", "win-32bit")]:
        url = f"{BASE_URL}/aria2-1.37.0-{suffix}.zip"
        dest_dir = os.path.join(BIN_DIR, arch)
        os.makedirs(dest_dir, exist_ok=True)
        dest = os.path.join(dest_dir, "aria2c.exe")
        print(f"下载 Windows {arch} aria2c...")
        urllib.request.urlretrieve(url, f"/tmp/aria2-{arch}.zip")
        with zipfile.ZipFile(f"/tmp/aria2-{arch}.zip") as zf:
            for name in zf.namelist():
                if name.endswith("aria2c.exe"):
                    with zf.open(name) as src, open(dest, "wb") as dst:
                        dst.write(src.read())
        print(f"  -> {dest}")


if __name__ == "__main__":
    system = platform.system().lower()
    if system == "linux":
        download_linux()
    elif system == "darwin":
        download_macos()
    elif system == "windows":
        download_windows()
    else:
        print(f"不支持的平台: {system}")
        sys.exit(1)
    print("完成!")
```

**验证:** `python scripts/download_aria2.py` 执行后检查 `resources/bin/` 下是否有对应文件。

### Task 7.3: 更新 .gitignore

```gitignore
# aria2 binary (CI 会下载，不提交到 git)
resources/bin/linux/
resources/bin/win32/
resources/bin/win64/
resources/bin/darwin/

# 保留目录结构
!resources/bin/*/.gitkeep
```

创建 `resources/bin/.gitkeep` 保持目录在 git 中。

### Task 7.4: 更新 GitHub Actions CI/CD — 含 aria2 二进制打包

**文件：** 更新 `.github/workflows/build.yml`

```yaml
name: Build CherryDrop

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:

jobs:
  build:
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
    runs-on: ${{ matrix.os }}

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python 3.10
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install nuitka
          pip install requests

      - name: Install Nuitka dependencies (Linux)
        if: runner.os == 'Linux'
        run: sudo apt-get install -y patchelf ccache

      - name: Download aria2 binary
        run: python scripts/download_aria2.py

      - name: Build with Nuitka (onefile)
        run: |
          python -m nuitka \
            --standalone \
            --onefile \
            --enable-plugin=pyqt5 \
            --follow-imports \
            --include-data-dir=resources/bin=resources/bin \
            --include-data-dir=resources/icons=resources/icons \
            --include-data-dir=resources/themes=resources/themes \
            --output-dir=dist \
            --product-name=CherryDrop \
            --file-version=${{ github.ref_name }} \
            --company-name=CherryDrop \
            main.py

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: CherryDrop-${{ matrix.os }}-${{ github.ref_name }}
          path: dist/*

      - name: Create release
        if: startsWith(github.ref, 'refs/tags/')
        uses: softprops/action-gh-release@v2
        with:
          files: dist/**
```

### Task 7.5: 本地构建脚本

**文件：** 创建 `scripts/build.sh` 和 `scripts/build.bat`

**Linux/macOS (`scripts/build.sh`):**
```bash
#!/bin/bash
set -e
echo "=== CherryDrop Build ==="

# 下载 aria2 二进制
echo ">>> 下载 aria2..."
python scripts/download_aria2.py

# 构建
echo ">>> 构建单文件..."
python -m nuitka \
    --standalone \
    --onefile \
    --enable-plugin=pyqt5 \
    --follow-imports \
    --include-data-dir=resources/bin=resources/bin \
    --include-data-dir=resources/icons=resources/icons \
    --include-data-dir=resources/themes=resources/themes \
    --output-dir=dist \
    --product-name=CherryDrop \
    --file-version=$(git describe --tags --always) \
    main.py

echo "=== 构建完成: dist/main.bin ==="
```

**Windows (`scripts/build.bat`):**
```batch
@echo off
echo === CherryDrop Build ===
echo >>> 下载 aria2...
python scripts/download_aria2.py

echo >>> 构建单文件...
python -m nuitka ^
    --standalone ^
    --onefile ^
    --enable-plugin=pyqt5 ^
    --follow-imports ^
    --include-data-dir=resources/bin=resources/bin ^
    --include-data-dir=resources/icons=resources/icons ^
    --include-data-dir=resources/themes=resources/themes ^
    --output-dir=dist ^
    --product-name=CherryDrop ^
    --file-version=%APPVEYOR_REPO_TAG_NAME% ^
    main.py

echo === 构建完成 ===
```

---

## 迭代 8: 系统托盘完善

### Task 8.1: 生成资源文件图标（SVG）

**文件：** 创建 `cherrydrop/resources/icons/cherrydrop.svg`

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">
  <!-- 简单樱花图标 -->
  <circle cx="24" cy="24" r="22" fill="#ffaab2" opacity="0.2"/>
  <text x="24" y="32" text-anchor="middle" font-size="28" fill="#ffaab2">🌸</text>
</svg>
```

### Task 8.2: MainWindow 中改用真实图标

需要将 `_init_tray` 中的图标改成加载 SVG 图标文件：

```python
# 在 _init_tray 中
import os
icon_path = os.path.join(os.path.dirname(__file__), "..", "resources", "icons", "cherrydrop.svg")
if os.path.exists(icon_path):
    self.tray_icon.setIcon(QIcon(icon_path))
```

---

## 迭代 9: GitHub Actions CI/CD

### Task 9.1: Nuitka 编译工作流

**文件：** 创建 `.github/workflows/build.yml`

```yaml
name: Build CherryDrop

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:

jobs:
  build:
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
    runs-on: ${{ matrix.os }}

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python 3.10
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install nuitka

      - name: Install Nuitka dependencies (Linux)
        if: runner.os == 'Linux'
        run: sudo apt-get install -y patchelf ccache

      - name: Build with Nuitka
        run: |
          python -m nuitka \
            --standalone \
            --enable-plugin=pyqt5 \
            --follow-imports \
            --include-data-dir=resources=resources \
            --output-dir=dist \
            --product-name=CherryDrop \
            --file-version=${{ github.ref_name }} \
            main.py

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: CherryDrop-${{ matrix.os }}-${{ github.ref_name }}
          path: dist/*

      - name: Create release
        if: startsWith(github.ref, 'refs/tags/')
        uses: softprops/action-gh-release@v2
        with:
          files: dist/**
```

### Task 9.2: README.md

**文件：** 创建 `cherrydrop/README.md`

```markdown
# 🌸 CherryDrop

> 樱色轻量下载器 — Python + PyQt5 + aria2

支持 HTTP/HTTPS/FTP/SFTP/BitTorrent/磁力链接，可选 ed2k 支持。
内置 BT 网络加速优化 (DHT/PEX/LPD/Tracker 自动更新)，
打包为单文件便携程序，开箱即用。

## 快速开始

```bash
pip install -r requirements.txt
python main.py
```

## 构建

```bash
pip install nuitka
python -m nuitka --standalone --enable-plugin=pyqt5 main.py
```

## 协议

MIT
```

---

## 迭代 10: 错误处理与边界情况

### Task 10.1: 核心异常处理

需要在以下地方增加 try/except：
- `aria2_client.py` 中 `start()` 检测 aria2c 是否已安装
- `task_list.py` 中空状态提示（无下载任务时显示"暂无下载任务"）
- `main_window.py` 中 network 超时处理

```python
# aria2_client.py start() 增加
if not shutil.which("aria2c"):
    logger.error("aria2c 未安装，请先安装 aria2")
    return False
```

```python
# task_list.py 增加空状态文字
self.empty_label = QLabel("🌸 暂无下载任务\n点击 ➕ 添加一个吧")
self.empty_label.setAlignment(Qt.AlignCenter)
self.empty_label.setStyleSheet("color: rgba(0,0,0,0.2); font-size: 14px;")
# 在数量变化时显示/隐藏
```

### Task 10.2: aria2 session 文件冲突

如果同时运行多个 CherryDrop 实例，session 文件会冲突。解决方案：

```python
# main.py 中使用单例锁
import socket
def check_single_instance():
    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.bind(f"\0cherrydrop_{os.getuid()}")
        return True
    except OSError:
        return False
```

---

## 迭代 11: 性能优化与打磨

### Task 11.1: 刷新优化

当前刷新间隔固定 2s，可优化为自适应：
- 有活跃下载时 → 1s
- 只有已完成/暂停的任务 → 3s
- 无任务 → 5s

### Task 11.2: 拖拽支持

用户在 TaskList 中可以直接拖拉 URL 或文件到窗口即可添加下载。

### Task 11.3: 剪贴板监听

后台检测剪贴板中的 URL，若有匹配则弹出"检测到下载链接，是否添加？"提示。

---

## 执行路线图总览

```
迭代 0:  项目脚手架           ████████░░░░  █ 1小时
迭代 1:  配置+主题            ████████████  █ 1.5小时
迭代 2:  aria2 引擎+BT优化   ████████████  █ 1.5小时
迭代 3:  进度条+任务列表      ████████████  █ 1.5小时
迭代 4:  对话框(BT/代理)     ████████████  █ 1.5小时
迭代 5:  主窗口整合           ████████████  █ 2小时
迭代 6:  BT 网络加速+Tracker  ████████████  █ 2小时  🔥 NEW
迭代 7:  便携打包+aria2二进制 ████████████  █ 1.5小时 🔥 NEW
迭代 8:  系统托盘             ██████░░░░░░  █ 0.5小时
迭代 9:  CI/CD               ████████░░░░  █ 1小时
迭代 10: 错误处理             ████████░░░░  █ 1小时
迭代 11: 打磨优化             ████████░░░░  █ 1小时
───────────────────────────────────
总计:                       约 16 小时
```

每个迭代都独立可运行，建议按顺序执行。

> 💡 **下一步建议:** 告诉我"开始执行"，我就按迭代 0 → 迭代 1 → ... 的顺序，用子代理逐一帮你写出所有代码文件，每完成一个迭代你都可以跑起来看看效果 nya~ (ฅ^•ﻌ•^ฅ)
