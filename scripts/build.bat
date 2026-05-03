@echo off
REM CherryDrop Windows 本地构建脚本

echo === 🌸 CherryDrop Build ===

echo ^>^>^> 构建单文件...
python -m nuitka ^
    --mode=onefile ^
    --enable-plugin=pyqt5 ^
    --follow-imports ^
    --nofollow-import-to=PyQt5.QtNetwork,PyQt5.QtWebEngine,PyQt5.QtMultimedia,PyQt5.QtMultimediaWidgets,PyQt5.QtPrintSupport,PyQt5.QtSvg,PyQt5.QtWebSockets,PyQt5.QtQuick,PyQt5.QtQuick3D,PyQt5.QtQuickWidgets,PyQt5.QtQml,PyQt5.QtQmlModels,PyQt5.QtDBus,PyQt5.QtBluetooth,PyQt5.QtNfc,PyQt5.QtSensors,PyQt5.QtPositioning,PyQt5.QtLocation,PyQt5.QtSql,PyQt5.QtXml,PyQt5.QtXmlPatterns,PyQt5.QtHelp,PyQt5.QtDesigner,PyQt5.QtUiTools,PyQt5.QtTest,PyQt5.QtSerialPort,PyQt5.QtRemoteObjects,PyQt5.QtTextToSpeech,PyQt5.QtX11Extras,PyQt5.QtOpenGL,PyQt5.QtWebChannel,PyQt5.QtConcurrent ^
    --include-data-dir=resources/bin=resources/bin ^
    --include-data-dir=resources/icons=resources/icons ^
    --include-data-dir=resources/themes=resources/themes ^
    --output-dir=dist ^
    --product-name=CherryDrop ^
    --file-version=%APPVEYOR_REPO_TAG_NAME% ^
    main.py

echo === ✅ 构建完成 ===
