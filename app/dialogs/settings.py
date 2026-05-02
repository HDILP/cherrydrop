"""设置对话框"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QSpinBox, QGroupBox, QCheckBox,
    QFileDialog, QTabWidget, QWidget, QPlainTextEdit, QComboBox
)
from PyQt5.QtCore import Qt

from app.utils.config import Config


class SettingsDialog(QDialog):
    """程序设置窗口"""

    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("设置")
        self.setFixedSize(480, 420)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self._init_ui()
        self._load_config()

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("设置")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2d2d2d;")
        layout.addWidget(title)

        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: transparent;
            }
            QTabBar::tab {
                padding: 8px 16px;
                font-size: 12px;
                border: none;
            }
            QTabBar::tab:selected {
                color: #ffaab2;
                border-bottom: 2px solid #ffaab2;
            }
            QTabBar::tab:hover {
                color: #ff8a95;
            }
        """)

        # ── 下载页 ──
        download_tab = QWidget()
        dl_layout = QVBoxLayout()

        # 下载路径
        path_row = QHBoxLayout()
        path_row.addWidget(QLabel("下载目录"))
        self.path_edit = QLineEdit()
        self.path_btn = QPushButton("浏览...")
        self.path_btn.setFixedWidth(60)
        self.path_btn.clicked.connect(self._browse_dir)
        path_row.addWidget(self.path_edit, 1)
        path_row.addWidget(self.path_btn)
        dl_layout.addLayout(path_row)

        # 并发数
        conc_row = QHBoxLayout()
        conc_row.addWidget(QLabel("最大并发下载"))
        self.concurrent_spin = QSpinBox()
        self.concurrent_spin.setRange(1, 20)
        conc_row.addWidget(self.concurrent_spin, 1)
        dl_layout.addLayout(conc_row)

        # 连接数
        conn_row = QHBoxLayout()
        conn_row.addWidget(QLabel("每服务器连接数"))
        self.conn_spin = QSpinBox()
        self.conn_spin.setRange(1, 64)
        conn_row.addWidget(self.conn_spin, 1)
        dl_layout.addLayout(conn_row)

        # 速度限制
        speed_row = QHBoxLayout()
        speed_row.addWidget(QLabel("下载限速 (KB/s, 0=不限)"))
        self.dl_speed_spin = QSpinBox()
        self.dl_speed_spin.setRange(0, 100000)
        self.dl_speed_spin.setSingleStep(100)
        speed_row.addWidget(self.dl_speed_spin, 1)
        dl_layout.addLayout(speed_row)

        dl_layout.addStretch()
        download_tab.setLayout(dl_layout)
        tabs.addTab(download_tab, "下载")

        # ── BT 网络页 ──
        bt_tab = QWidget()
        bt_layout = QVBoxLayout()

        # Tracker 自动更新
        self.tracker_auto = QCheckBox("每日自动更新 Tracker 列表")
        bt_layout.addWidget(self.tracker_auto)

        # 手动编辑 Tracker
        bt_layout.addWidget(QLabel("Tracker 列表 (每行一个，留空使用自动更新)"))
        self.tracker_edit = QPlainTextEdit()
        self.tracker_edit.setPlaceholderText(
            "udp://tracker.opentrackr.org:1337/announce\n"
            "https://tracker.xxx.com/announce"
        )
        self.tracker_edit.setFixedHeight(100)
        bt_layout.addWidget(self.tracker_edit)

        # BT 高级选项
        bt_form = QGroupBox("BT 协议选项")
        btf_layout = QVBoxLayout()

        dht_row = QHBoxLayout()
        self.bt_dht = QCheckBox("启用 DHT")
        self.bt_dht.setChecked(True)
        dht_row.addWidget(self.bt_dht)
        self.bt_pex = QCheckBox("启用 PEX")
        self.bt_pex.setChecked(True)
        dht_row.addWidget(self.bt_pex)
        self.bt_lpd = QCheckBox("启用 LPD")
        self.bt_lpd.setChecked(True)
        dht_row.addWidget(self.bt_lpd)
        btf_layout.addLayout(dht_row)

        peers_row = QHBoxLayout()
        peers_row.addWidget(QLabel("最大 Peers:"))
        self.bt_peers_spin = QSpinBox()
        self.bt_peers_spin.setRange(10, 200)
        peers_row.addWidget(self.bt_peers_spin)
        peers_row.addStretch()
        btf_layout.addLayout(peers_row)

        bt_form.setLayout(btf_layout)
        bt_layout.addWidget(bt_form)

        bt_layout.addStretch()
        bt_tab.setLayout(bt_layout)
        tabs.addTab(bt_tab, "BT 网络")

        # ── 代理页 ──
        proxy_tab = QWidget()
        proxy_layout = QVBoxLayout()

        self.proxy_enable = QCheckBox("启用代理")
        proxy_layout.addWidget(self.proxy_enable)

        proxy_type_row = QHBoxLayout()
        proxy_type_row.addWidget(QLabel("类型:"))
        self.proxy_type_combo = QComboBox()
        self.proxy_type_combo.addItems(["socks5", "http", "https"])
        proxy_type_row.addWidget(self.proxy_type_combo)
        proxy_layout.addLayout(proxy_type_row)

        proxy_host_row = QHBoxLayout()
        proxy_host_row.addWidget(QLabel("服务器:"))
        self.proxy_host_edit = QLineEdit()
        self.proxy_host_edit.setPlaceholderText("127.0.0.1")
        proxy_host_row.addWidget(self.proxy_host_edit, 1)
        proxy_host_row.addWidget(QLabel("端口:"))
        self.proxy_port_spin = QSpinBox()
        self.proxy_port_spin.setRange(1, 65535)
        self.proxy_port_spin.setValue(1080)
        proxy_host_row.addWidget(self.proxy_port_spin)
        proxy_layout.addLayout(proxy_host_row)

        proxy_auth_group = QGroupBox("认证 (可选)")
        proxy_auth_layout = QHBoxLayout()
        proxy_auth_layout.addWidget(QLabel("用户名:"))
        self.proxy_user_edit = QLineEdit()
        proxy_auth_layout.addWidget(self.proxy_user_edit, 1)
        proxy_auth_layout.addWidget(QLabel("密码:"))
        self.proxy_pass_edit = QLineEdit()
        self.proxy_pass_edit.setEchoMode(QLineEdit.Password)
        proxy_auth_layout.addWidget(self.proxy_pass_edit, 1)
        proxy_auth_group.setLayout(proxy_auth_layout)
        proxy_layout.addWidget(proxy_auth_group)

        proxy_scope_group = QGroupBox("代理作用域")
        proxy_scope_layout = QVBoxLayout()
        self.proxy_scope_dl = QCheckBox("下载流量走代理")
        self.proxy_scope_dl.setChecked(True)
        proxy_scope_layout.addWidget(self.proxy_scope_dl)
        self.proxy_scope_tr = QCheckBox("Tracker 更新走代理")
        self.proxy_scope_tr.setChecked(True)
        proxy_scope_layout.addWidget(self.proxy_scope_tr)
        proxy_scope_group.setLayout(proxy_scope_layout)
        proxy_layout.addWidget(proxy_scope_group)

        proxy_layout.addStretch()
        proxy_tab.setLayout(proxy_layout)
        tabs.addTab(proxy_tab, "代理")

        # ── 常规页 ──
        general_tab = QWidget()
        gen_layout = QVBoxLayout()

        self.auto_aria2 = QCheckBox("自动启动 aria2")
        gen_layout.addWidget(self.auto_aria2)

        self.minimize_tray = QCheckBox("最小化到系统托盘")
        gen_layout.addWidget(self.minimize_tray)

        gen_layout.addStretch()
        general_tab.setLayout(gen_layout)
        tabs.addTab(general_tab, "常规")

        layout.addWidget(tabs)

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
            }
            QPushButton:hover { background-color: rgba(0,0,0,0.08); }
        """)
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("保存")
        save_btn.setFixedSize(90, 36)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffaab2;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                color: white;
            }
            QPushButton:hover { background-color: #ff8a95; }
        """)
        save_btn.clicked.connect(self._save)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

        self.setLayout(layout)

    def _load_config(self):
        self.path_edit.setText(self.config.get("download_dir", ""))
        self.concurrent_spin.setValue(self.config.get("max_concurrent_downloads", 5))
        self.conn_spin.setValue(self.config.get("max_connection_per_server", 16))
        self.dl_speed_spin.setValue(self.config.get("speed_limit_download", 0))
        self.auto_aria2.setChecked(self.config.get("auto_start_aria2", True))
        self.minimize_tray.setChecked(self.config.get("minimize_to_tray", True))
        # BT 网络
        self.tracker_auto.setChecked(self.config.get("bt_tracker_auto_update", True))
        bt_tracker = self.config.get("bt_tracker", "")
        if bt_tracker:
            self.tracker_edit.setPlainText("\n".join(bt_tracker.split(",")))
        self.bt_dht.setChecked(self.config.get("bt_enable_dht", True))
        self.bt_pex.setChecked(self.config.get("bt_enable_pex", True))
        self.bt_lpd.setChecked(self.config.get("bt_enable_lpd", True))
        self.bt_peers_spin.setValue(self.config.get("bt_max_peers", 50))
        # 代理
        self.proxy_enable.setChecked(self.config.get("proxy_enable", False))
        proxy_type = self.config.get("proxy_type", "socks5")
        idx = self.proxy_type_combo.findText(proxy_type)
        if idx >= 0:
            self.proxy_type_combo.setCurrentIndex(idx)
        self.proxy_host_edit.setText(self.config.get("proxy_host", "127.0.0.1"))
        self.proxy_port_spin.setValue(self.config.get("proxy_port", 1080))
        self.proxy_user_edit.setText(self.config.get("proxy_user", ""))
        self.proxy_pass_edit.setText(self.config.get("proxy_pass", ""))
        self.proxy_scope_dl.setChecked(self.config.get("proxy_scope_download", True))
        self.proxy_scope_tr.setChecked(self.config.get("proxy_scope_tracker", True))

    def _save(self):
        self.config.set("download_dir", self.path_edit.text())
        self.config.set("max_concurrent_downloads", self.concurrent_spin.value())
        self.config.set("max_connection_per_server", self.conn_spin.value())
        self.config.set("speed_limit_download", self.dl_speed_spin.value())
        self.config.set("auto_start_aria2", self.auto_aria2.isChecked())
        self.config.set("minimize_to_tray", self.minimize_tray.isChecked())
        # BT 网络
        self.config.set("bt_tracker_auto_update", self.tracker_auto.isChecked())
        tracker_text = self.tracker_edit.toPlainText().strip()
        self.config.set("bt_tracker", ",".join(
            line.strip() for line in tracker_text.split("\n") if line.strip()
        ) if tracker_text else "")
        self.config.set("bt_enable_dht", self.bt_dht.isChecked())
        self.config.set("bt_enable_pex", self.bt_pex.isChecked())
        self.config.set("bt_enable_lpd", self.bt_lpd.isChecked())
        self.config.set("bt_max_peers", self.bt_peers_spin.value())
        # 代理
        self.config.set("proxy_enable", self.proxy_enable.isChecked())
        self.config.set("proxy_type", self.proxy_type_combo.currentText())
        self.config.set("proxy_host", self.proxy_host_edit.text())
        self.config.set("proxy_port", self.proxy_port_spin.value())
        self.config.set("proxy_user", self.proxy_user_edit.text())
        self.config.set("proxy_pass", self.proxy_pass_edit.text())
        self.config.set("proxy_scope_download", self.proxy_scope_dl.isChecked())
        self.config.set("proxy_scope_tracker", self.proxy_scope_tr.isChecked())
        self.accept()

    def _browse_dir(self):
        d = QFileDialog.getExistingDirectory(self, "选择下载目录", self.path_edit.text())
        if d:
            self.path_edit.setText(d)
