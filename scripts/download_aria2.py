"""下载各平台 aria2 二进制到 resources/bin/

数据源: motrix-next (https://github.com/AnInsomniacy/motrix-next)
预编译静态二进制，开箱即用。
"""
import os
import sys
import platform
import urllib.request
import stat

BASE_URL = "https://github.com/AnInsomniacy/motrix-next/raw/main/src-tauri/binaries"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BIN_DIR = os.path.join(SCRIPT_DIR, "..", "resources", "bin")

# 平台映射: (arch, os) -> 文件名
PLATFORM_MAP = {
    ("x86_64", "linux"):   ("linux", "motrixnext-aria2c-x86_64-unknown-linux-gnu"),
    ("aarch64", "linux"):  ("linux", "motrixnext-aria2c-aarch64-unknown-linux-gnu"),
    ("x86_64", "darwin"):  ("darwin", "motrixnext-aria2c-x86_64-apple-darwin"),
    ("aarch64", "darwin"): ("darwin", "motrixnext-aria2c-aarch64-apple-darwin"),
    ("x86_64", "windows"): ("win64", "motrixnext-aria2c-x86_64-pc-windows-msvc.exe"),
    ("aarch64", "windows"):("win64", "motrixnext-aria2c-aarch64-pc-windows-msvc.exe"),
}


def get_platform_key():
    machine = platform.machine().lower()
    system = platform.system().lower()
    if machine in ("amd64", "x86_64"):
        machine = "x86_64"
    elif machine in ("arm64", "aarch64"):
        machine = "aarch64"
    return (machine, system)


def download_aria2(arch_dir: str, filename: str):
    """下载 aria2 二进制到指定目录"""
    dest_dir = os.path.join(BIN_DIR, arch_dir)
    os.makedirs(dest_dir, exist_ok=True)

    dest = os.path.join(dest_dir, "aria2c.exe" if arch_dir.startswith("win") else "aria2c")
    url = f"{BASE_URL}/{filename}"

    print(f"📥 下载 {filename}...")
    urllib.request.urlretrieve(url, dest)

    # 设置可执行权限 (非 Windows)
    if not arch_dir.startswith("win"):
        os.chmod(dest, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

    size = os.path.getsize(dest) // 1024
    print(f"   ✅ -> {dest} ({size}KB)")
    return dest


def download_aria2_conf():
    """下载 aria2.conf"""
    conf_dir = os.path.join(SCRIPT_DIR, "..", "resources")
    url = f"{BASE_URL}/aria2.conf"
    dest = os.path.join(conf_dir, "aria2.conf")
    print(f"📥 下载 aria2.conf...")
    urllib.request.urlretrieve(url, dest)
    print(f"   ✅ -> {dest}")
    return dest


if __name__ == "__main__":
    key = get_platform_key()
    match = PLATFORM_MAP.get(key)

    if not match:
        print(f"❌ 不支持的平台: {key}")
        print("支持的平台:")
        for (arch, os_name), (dir_name, fn) in sorted(PLATFORM_MAP.items()):
            print(f"   {arch}-{os_name} -> {dir_name}/{fn}")
        sys.exit(1)

    arch_dir, filename = match
    download_aria2(arch_dir, filename)
    download_aria2_conf()
    print("\n🎉 下载完成！")
