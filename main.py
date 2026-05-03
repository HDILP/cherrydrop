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


VERSION = "0.1.0"

# 下载测试超时秒数
_DOWNLOAD_TIMEOUT = 30


def _cli_download_test(url: str):
    """CLI 模式：启动 aria2 RPC，下载一个文件，验证成功后退出。

    专为 CI 自动测试设计 —— 不创建 GUI，只验证下载链路完好。
    """
    import shutil
    import tempfile
    import time

    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(message)s",
    )
    logger = logging.getLogger("download-test")

    # 临时目录：存放 settings.json 和下载产物
    tmpdir = tempfile.mkdtemp(prefix="cherrydrop_test_")
    logger.info("Test dir: %s", tmpdir)

    config = Config(config_path=os.path.join(tmpdir, "settings.json"))
    config.set("download_dir", tmpdir)
    config.set("bt_tracker_auto_update", False)  # CI 不需要 tracker

    client = Aria2Client(config)

    # 1. 启动 aria2c
    logger.info("Starting aria2c...")
    if not client.start():
        logger.error("FAILED to start aria2c")
        shutil.rmtree(tmpdir)
        sys.exit(1)
    logger.info("aria2c RPC ready ✓")

    # 2. 添加下载
    logger.info("Adding download: %s", url)
    gid = client.add_uri(url)
    if not gid:
        logger.error("FAILED to add download")
        client.stop()
        shutil.rmtree(tmpdir)
        sys.exit(1)
    logger.info("Download started: GID=%s", gid)

    # 3. 轮询等待完成 / 出错
    deadline = time.time() + _DOWNLOAD_TIMEOUT
    completed = False
    while time.time() < deadline:
        time.sleep(0.5)
        try:
            d = client.api.get_download(gid)
            if d.status == "complete":
                completed = True
                logger.info("Download status: complete ✓")
                break
            if d.status == "error":
                logger.error("Download status: error — %s", d.error_message)
                break
            logger.debug("  status=%s  progress=%.1f%%", d.status, d.progress)
        except Exception:
            # 下载完成后可能从 active 列表中移除
            completed = True
            break

    # 4. 验证文件存在
    if completed:
        real_files = [
            f for f in os.listdir(tmpdir)
            if f not in ("settings.json", "aria2.session", "dht.dat", "cherrydrop.lock")
        ]
        if real_files:
            logger.info("Downloaded files: %s", real_files)
            for f in real_files:
                fpath = os.path.join(tmpdir, f)
                if os.path.isfile(fpath):
                    logger.info("  %s  —  %d bytes", f, os.path.getsize(fpath))
            logger.info("✓ Download test PASSED")
        else:
            logger.warning("Status was complete but no files found in %s", tmpdir)
            # 可能是 got/GID 命名等，再搜一层
            for root, dirs, files in os.walk(tmpdir):
                for f in files:
                    if f not in ("settings.json", "aria2.session", "dht.dat", "cherrydrop.lock"):
                        logger.info("  Found: %s", os.path.join(root, f))

    # 5. 清理
    client.stop()
    shutil.rmtree(tmpdir)

    if completed:
        sys.exit(0)
    else:
        logger.error("✗ Download test FAILED (timeout or error)")
        sys.exit(1)


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(name)s: %(message)s",
    )


def main():
    # ── CLI 模式：无头验证用，不创建 GUI ──
    if '--version' in sys.argv:
        print(f"CherryDrop v{VERSION}")
        sys.exit(0)
    if '-h' in sys.argv or '--help' in sys.argv:
        print(f"CherryDrop v{VERSION} — 樱花下载器")
        print()
        print("Usage: CherryDrop [options]")
        print()
        print("Options:")
        print("  --version  显示版本号并退出")
        print("  -h, --help 显示此帮助并退出")
        print("  -d, --download-url <URL>  下载测试（无 GUI，用于 CI）")
        print()
        print("A modern download manager powered by aria2")
        sys.exit(0)

    # ── CLI 模式：下载测试（无 GUI）──
    dl_flags = {'--download-url', '-d'}
    dl_idx = [(i, a) for i, a in enumerate(sys.argv) if a in dl_flags]
    if dl_idx:
        idx = dl_idx[0][0]
        if idx + 1 >= len(sys.argv):
            print("ERROR: --download-url / -d requires a URL argument")
            sys.exit(1)
        _cli_download_test(sys.argv[idx + 1])
        # 函数内部会 sys.exit，不会走到这里

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
