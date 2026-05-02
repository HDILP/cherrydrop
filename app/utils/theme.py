"""主题管理器 - 加载 QSS 文件"""
import os


def load_theme(theme_name: str = "cherry") -> str:
    """加载 QSS 样式表"""
    theme_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "resources", "themes"
    )
    qss_path = os.path.join(theme_dir, f"{theme_name}.qss")

    if not os.path.exists(qss_path):
        return ""

    with open(qss_path, "r", encoding="utf-8") as f:
        return f.read()


def apply_theme(app, theme_name: str = "cherry"):
    """将样式表应用到 QApplication"""
    qss = load_theme(theme_name)
    if qss:
        app.setStyleSheet(qss)
