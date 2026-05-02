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

        # 自适应刷新
        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self._refresh_tasks)
        self._refresh_timer.start(2000)  # 初始 2s，由 _refresh_tasks 动态调整

    def _adjust_refresh_interval(self, downloads: list):
        """根据当前任务状态自适应刷新间隔"""
        if not downloads:
            # 无任务 → 5s
            if self._refresh_timer.interval() != 5000:
                self._refresh_timer.setInterval(5000)
            return
        has_active = any(
            getattr(dl, "status", "") in ("active", "waiting")
            for dl in downloads
        )
        if has_active:
            # 有活跃下载 → 1s
            if self._refresh_timer.interval() != 1000:
                self._refresh_timer.setInterval(1000)
        else:
            # 只有已完成/暂停 → 3s
            if self._refresh_timer.interval() != 3000:
                self._refresh_timer.setInterval(3000)

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
        self.task_list.url_dropped.connect(self._on_dropped_url)

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
        # 加载 SVG 图标
        icon_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "resources", "icons", "cherrydrop.svg"
        )
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            self.tray_icon.setIcon(QIcon.fromTheme("document-save"))
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
        # macOS 下如果窗口状态为最小化/隐藏，仅 show() 可能不会把主窗体带到前台
        self.setWindowState((self.windowState() & ~Qt.WindowMinimized) | Qt.WindowActive)
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

    def _on_dropped_url(self, url: str):
        """处理拖拽放入的 URL"""
        gid = self.aria2.add_uri(url)
        if gid:
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
        """根据定时刷新任务状态"""
        if not self.aria2.is_running:
            return

        downloads = self.aria2.get_downloads()
        self._adjust_refresh_interval(downloads)
        if not downloads:
            return

        for dl in downloads:
            widget = self.task_list.get_task_widget(dl.gid)
            # 活跃下载才查询 peer 信息
            peers = self.aria2.get_peers(dl.gid) if dl.status == "active" else []
            if widget:
                widget.update_status(
                    completed=dl.completed_length,
                    total=dl.total_length,
                    speed=human_speed(dl.download_speed),
                    status=dl.status,
                    peers=peers,
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
                    peers=peers,
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
