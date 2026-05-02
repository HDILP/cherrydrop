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
