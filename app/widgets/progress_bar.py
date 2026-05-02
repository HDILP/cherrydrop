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
