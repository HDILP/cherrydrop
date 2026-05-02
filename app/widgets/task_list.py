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
