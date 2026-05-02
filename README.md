# 🌸 CherryDrop

> 樱色轻量下载器 — 便携单文件，开箱即用

基于 **Python + PyQt5 + aria2** 的跨平台全协议下载器。内置 BT 网络加速优化、Tracker 自动更新、代理支持。打包为单文件，**无需安装 aria2**（二进制已内置）。

## 特性

- **全协议支持**: HTTP/HTTPS/FTP/SFTP/BitTorrent/磁力链接，可选 ed2k
- **BT 加速**: DHT/PEX/LPD 三管齐下 + Tracker 每日自动更新（从 CDN 镜像拉取）
- **中国网络优化**: CDN Tracker 源、伪装 Transmission 客户端、代理支持、防 QoS 限速
- **毛玻璃 UI**: 樱花粉色 (`#ffaab2`) 主题，纯图标操作，系统托盘常驻，2 秒实时刷新
- **便携单文件**: Nuitka 编译，aria2 二进制内置，开箱即用
- **CI/CD**: GitHub Actions 三平台自动构建

## 快速开始

```bash
# 开发模式
git clone <repo>
cd cherrydrop
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## 构建

```bash
# 方式一: 本地构建脚本
bash scripts/build.sh          # Linux/macOS
.\scripts\build.bat            # Windows

# 方式二: 手动构建
pip install nuitka requests
python -m nuitka \
    --standalone --onefile \
    --enable-plugin=pyqt5 \
    --include-data-dir=resources/bin=resources/bin \
    --include-data-dir=resources/icons=resources/icons \
    --include-data-dir=resources/themes=resources/themes \
    --output-dir=dist --product-name=CherryDrop \
    main.py

# 方式三: GitHub Actions
# 推送 tag v* 即可自动构建
git tag v0.1.0
git push origin v0.1.0
```

## 项目结构

```
cherrydrop/
├── main.py                    # 入口 (整合 Config/主题/引擎/MainWindow)
├── app/
│   ├── main_window.py         # 主窗口 (工具栏/任务列表/状态栏/系统托盘)
│   ├── engine/
│   │   ├── aria2_client.py    # aria2 进程管理 + RPC (BT/DHT 优化)
│   │   ├── tracker_updater.py # Tracker 自动更新拉取 + 热注入
│   │   └── amule_client.py    # ed2k 支持 (骨架)
│   ├── widgets/
│   │   ├── task_list.py       # 下载任务列表 (右键菜单 + Peer 显示)
│   │   └── progress_bar.py    # 毛玻璃进度条
│   ├── dialogs/
│   │   ├── add_task.py        # 添加下载对话框 (URL/引擎/高级选项)
│   │   └── settings.py        # 设置窗口 (4 Tab: 下载/BT/代理/常规)
│   └── utils/
│       ├── config.py          # JSON 配置管理 (settings.json)
│       └── theme.py           # QSS 主题加载
├── resources/
│   ├── aria2.conf             # aria2 配置 (来自 motrix-next)
│   ├── bin/linux/aria2c       # 内置 aria2 二进制 (各平台)
│   ├── bin/darwin/aria2c
│   ├── bin/win64/aria2c.exe
│   ├── icons/cherrydrop.svg   # SVG 樱花图标
│   └── themes/cherry.qss      # 浅色毛玻璃主题
├── scripts/
│   ├── build.sh               # Linux/macOS 构建脚本
│   └── build.bat              # Windows 构建脚本
├── .github/workflows/
│   └── build.yml              # GitHub Actions 三平台 CI/CD
├── PLAN.md                    # 完整开发计划 (11 迭代, 2498 行)
├── CLAUDE.md                  # AI 协作指南
└── requirements.txt           # Python 依赖 (PyQt5, aria2p, requests)
```

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| GUI | PyQt5 5.15+ | Qt 5 稳定版，资料丰富 |
| 下载引擎 | aria2 1.36.0 | 静态编译，内置免安装 |
| RPC 通信 | aria2p 0.12+ | JSON-RPC 封装，简洁 API |
| BT 优化 | motrix-next 参数 | DHT/PEX/LPD，伪装 Transmission |
| Tracker | 每日自动更新 | CDN 镜像源，热注入 aria2 |
| 打包 | Nuitka --onefile | 单文件便携分发 |
| CI/CD | GitHub Actions | Ubuntu/macOS/Windows 三平台 |

## 依赖

- Python 3.10+
- PyQt5 >= 5.15.0
- aria2p >= 0.12.0
- requests >= 2.28.0

## 协议

MIT
