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

# 构建
echo ">>> 构建单文件..."
python -m nuitka \
    --mode=onefile \
    --enable-plugin=pyqt5 \
    --follow-imports \
    --include-data-dir="$BIN_DIR" \
    --include-data-dir=resources/icons=resources/icons \
    --include-data-dir=resources/themes=resources/themes \
    --output-dir=dist \
    --product-name=CherryDrop \
    --file-version=$(git describe --tags --always 2>/dev/null || echo "dev") \
    main.py

echo "=== ✅ 构建完成: dist/main.bin ==="
