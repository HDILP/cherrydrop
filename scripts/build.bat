@echo off
REM CherryDrop Windows 本地构建脚本
echo === 🌸 CherryDrop Build ===

echo ^>^>^> 下载 aria2...
python scripts/download_aria2.py

echo ^>^>^> 构建单文件...
python -m nuitka ^
    --standalone ^
    --onefile ^
    --enable-plugin=pyqt5 ^
    --follow-imports ^
    --include-data-dir=resources/bin=resources/bin ^
    --include-data-dir=resources/icons=resources/icons ^
    --include-data-dir=resources/themes=resources/themes ^
    --output-dir=dist ^
    --product-name=CherryDrop ^
    --file-version=%APPVEYOR_REPO_TAG_NAME% ^
    main.py

echo === ✅ 构建完成 ===
