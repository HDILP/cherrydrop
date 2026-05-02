#!/usr/bin/env python3
"""CherryDrop 入口"""
import sys
import os
import socket
import logging

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt

from app.utils.config import Config
from app.utils.theme import apply_theme
from app.engine.aria2_client import Aria2Client
from app.engine.amule_client import AmuleClient
from app.main_window import MainWindow


# ── 单例锁 ──
def _try_lock() -> bool:
    """尝试获取单例锁，防止多开"""
    lock_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cherrydrop.lock")
    # Windows 不支持 AF_UNIX 抽象命名空间；同时 os.getuid 在 Windows 不可用。
    # 在这种情况下回退到 PID 文件检查，避免启动时直接崩溃。
    uid = getattr(os, "getuid", lambda: 0)()
    try:
        if hasattr(socket, "AF_UNIX"):
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.bind(f"\0cherrydrop_{uid}")
            sock.close()
            return True
    except OSError:
        pass

    try:
        with open(lock_path) as f:
            pid = f.read().strip()
        os.kill(int(pid), 0)
        return False
    except (OSError, ValueError, FileNotFoundError):
        pass

    # 锁文件存在但进程已死，移除后重试
    try:
        os.unlink(lock_path)
    except OSError:
        pass
    try:
        if hasattr(socket, "AF_UNIX"):
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.bind(f"\0cherrydrop_{uid}")
            sock.close()
        return True
    except OSError:
        return False


def write_pid_file():
    pid_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cherrydrop.lock")
    try:
        with open(pid_path, "w") as f:
            f.write(str(os.getpid()))
    except OSError:
        pass


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

    write_pid_file()

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
