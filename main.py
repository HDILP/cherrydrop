#!/usr/bin/env python3
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
