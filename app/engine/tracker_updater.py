"""BT Tracker 列表自动更新器

定时从开源 Tracker 集合拉取最新列表，注入 aria2 的 --bt-tracker 参数。
数据源：
  - XIU2/TrackersListCollection (CDN 镜像优先)
  - ngosang/trackerslist (CDN 镜像优先)
"""
import logging
import threading
import time
from typing import List, Optional, Callable
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
        self._trackers: List[str] = []
        self._last_update = 0.0
        self._timer: Optional[threading.Timer] = None
        self._running = False

    def set_proxy(self, proxy: str):
        self._proxy = proxy

    def set_sources(self, sources: list):
        self.sources = sources

    def fetch(self) -> List[str]:
        """从所有数据源拉取 tracker 列表，合并去重"""
        all_trackers: List[str] = []
        failures: List[str] = []

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
