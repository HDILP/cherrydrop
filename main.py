#!/usr/bin/env python3
"""CherryDrop 入口"""
import sys
import os
import tempfile

try:
    import fcntl
except ImportError:
    fcntl = None
import logging

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt, QTimer

from app.utils.config import Config
from app.utils.theme import apply_theme
from app.engine.aria2_client import Aria2Client
from app.engine.amule_client import AmuleClient
from app.main_window import MainWindow


# 持有文件描述符，保证进程存活期间锁不释放
_LOCK_FILE = None


# ── 单例锁 ──
def _try_lock() -> bool:
    """尝试获取单例锁，防止多开。

    在 macOS/Linux 优先使用 flock 避免 PID 复用导致的误判。
    """
    global _LOCK_FILE

    lock_path = os.path.join(tempfile.gettempdir(), "cherrydrop.lock")
    try:
        lock_file = open(lock_path, "a+")
    except OSError:
        return True

    if fcntl is None:
        _LOCK_FILE = lock_file
        return True

    try:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        lock_file.seek(0)
        lock_file.truncate()
        lock_file.write(str(os.getpid()))
        lock_file.flush()
        _LOCK_FILE = lock_file
        return True
    except OSError:
        lock_file.close()
        return False


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(name)s: %(message)s",
    )


def main():
    setup_logging()
    logger = logging.getLogger(__name__)

    app = QApplication(sys.argv)
    app.setApplicationName("CherryDrop")
    app.setOrganizationName("CherryDrop")

    # 高DPI支持
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # 单例检查
    if not _try_lock():
        logger.warning("CherryDrop 已在运行")
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("CherryDrop")
        msg.setText("CherryDrop 已在运行中")
        msg.setInformativeText("请检查系统托盘区域。")
        msg.exec_()
        sys.exit(0)


    # 加载配置
    config = Config()

    # 加载主题
    apply_theme(app, config.get("theme", "cherry"))

    # 初始化引擎
    aria2 = Aria2Client(config)
    amule = AmuleClient()

    # 创建主窗口
    window = MainWindow(config, aria2, amule)
    # 延迟到事件循环开始后再激活窗口，避免 macOS 首次启动只驻留托盘不弹主窗
    QTimer.singleShot(0, window.show_and_activate)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
