#!/bin/bash
# CherryDrop 本地构建脚本
set -e

echo "=== 🌸 CherryDrop Build ==="

# 检测当前平台
case "$(uname -s)" in
  Linux*)  BIN_DIR="resources/bin/linux=resources/bin/linux" ;;
  Darwin*) BIN_DIR="resources/bin/darwin=resources/bin/darwin" ;;
  *)       echo "Unknown platform"; exit 1 ;;
esac

# macOS 用 app 模式，其他用 onefile
if [[ "$(uname -s)" == "Darwin" ]]; then
  NUITKA_MODE="--mode=app"
  LTO_FLAG=""
else
  NUITKA_MODE="--mode=onefile"
  LTO_FLAG="--lto=yes"
fi

# 构建
echo ">>> 构建单文件..."
python -m nuitka \
    $NUITKA_MODE \
    $LTO_FLAG \
    --strip \
    --remove-output \
    --enable-plugin=pyqt5 \
    --noinclude-qt-plugins=sensible,styles,translations \
    --nofollow-import-to=PyQt5.QtWebEngine \
    --nofollow-import-to=PyQt5.QtMultimedia \
    --follow-imports \
    --include-data-dir="$BIN_DIR" \
    --include-data-dir=resources/aria2.conf=resources/aria2.conf \
    --include-data-dir=resources/icons=resources/icons \
    --include-data-dir=resources/themes=resources/themes \
    --nofollow-import-to=tkinter,unittest,pdb,test,distutils,ensurepip,venv,lib2to3,idlelib,turtle,cgi,smtplib,poplib,imaplib,ftplib,telnetlib,nntplib \
    --output-dir=dist \
    --product-name=CherryDrop \
    --file-version=$(git describe --tags --always 2>/dev/null || echo "dev") \
    main.py

echo "=== ✅ 构建完成: dist/main.bin ==="
