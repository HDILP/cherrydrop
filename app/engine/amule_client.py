"""amulecmd 客户端封装 - 处理 ed2k 下载"""
import subprocess
import shutil
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class AmuleClient:
    """ed2k 下载引擎 - 通过 amulecmd 控制 aMule 后台"""

    def __init__(self):
        self._available = self._check_amule()

    def _check_amule(self) -> bool:
        """检查系统是否安装了 amulecmd"""
        return shutil.which("amulecmd") is not None

    @property
    def is_available(self) -> bool:
        return self._available

    def add_uri(self, ed2k_link: str) -> bool:
        """添加 ed2k 链接"""
        if not self._available:
            logger.warning("amulecmd 未安装，无法处理 ed2k 链接")
            return False
        try:
            result = subprocess.run(
                ["amulecmd", "-c", f"Add {ed2k_link}"],
                capture_output=True, text=True, timeout=30
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"amulecmd 添加 ed2k 失败: {e}")
            return False

    def get_install_guide(self) -> str:
        """返回各平台安装指南"""
        return (
            "ed2k 下载需要 aMule。请安装：\n"
            "  Linux: sudo apt install amule-daemon amule-utils\n"
            "  macOS: brew install amule\n"
            "  Windows: 请从我们的镜像站下载 (将在后续提供)"
        )
