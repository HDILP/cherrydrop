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
