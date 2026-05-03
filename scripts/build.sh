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

# macOS 用 app 模式，其他用 standalone
if [[ "$(uname -s)" == "Darwin" ]]; then
  NUITKA_MODE="--mode=app"
else
  NUITKA_MODE="--standalone"
fi

# 构建
echo ">>> 构建单文件..."
python -m nuitka \
    $NUITKA_MODE \
    --enable-plugin=pyqt5 \
    --follow-imports \
    --nofollow-import-to=PyQt5.QtNetwork,PyQt5.QtWebEngine,PyQt5.QtMultimedia,PyQt5.QtMultimediaWidgets,PyQt5.QtPrintSupport,PyQt5.QtSvg,PyQt5.QtWebSockets,PyQt5.QtQuick,PyQt5.QtQuick3D,PyQt5.QtQuickWidgets,PyQt5.QtQml,PyQt5.QtQmlModels,PyQt5.QtDBus,PyQt5.QtBluetooth,PyQt5.QtNfc,PyQt5.QtSensors,PyQt5.QtPositioning,PyQt5.QtLocation,PyQt5.QtSql,PyQt5.QtXml,PyQt5.QtXmlPatterns,PyQt5.QtHelp,PyQt5.QtDesigner,PyQt5.QtUiTools,PyQt5.QtTest,PyQt5.QtSerialPort,PyQt5.QtRemoteObjects,PyQt5.QtTextToSpeech,PyQt5.QtX11Extras,PyQt5.QtOpenGL,PyQt5.QtWebChannel,PyQt5.QtConcurrent \
    --nofollow-import-to=tkinter,unittest,pdb,test,distutils,ensurepip,venv,lib2to3,idlelib,turtle,cgi,smtplib,poplib,imaplib,ftplib,telnetlib,nntplib \
    --include-data-dir="$BIN_DIR" \
    --include-data-file=resources/aria2.conf=resources/aria2.conf \
    --include-data-dir=resources/icons=resources/icons \
    --include-data-dir=resources/themes=resources/themes \
    --output-dir=dist \
    --product-name=CherryDrop \
    --file-version=$(git describe --tags --always 2>/dev/null || echo "dev") \
    main.py

echo "=== ✅ 构建完成 ==="
echo "dist/ 内容:"
ls -lh dist/
