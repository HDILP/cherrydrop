#!/usr/bin/env python3
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
    w = QLabel("🌸 CherryDrop loading...")
    w.setAlignment(Qt.AlignCenter)
    w.resize(400, 60)
    w.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
