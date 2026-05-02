# 🌸 CherryDrop

> 樱色轻量下载器 — 便携单文件，开箱即用

基于 **Python + PyQt5 + aria2** 的跨平台全协议下载器。内置 BT 网络加速优化、Tracker 自动更新、代理支持。打包为单文件，**无需安装 aria2**（二进制已内置）。

## 特性

- **全协议支持**: HTTP/HTTPS/FTP/SFTP/BitTorrent/磁力链接，可选 ed2k
- **BT 加速**: DHT/PEX/LPD 三管齐下 + Tracker 每日自动更新
- **中国网络优化**: CDN Tracker 源、伪装 Transmission 客户端、代理支持
- **毛玻璃 UI**: 樱花粉色主题，纯图标操作，系统托盘常驻
- **便携单文件**: Nuitka 编译，aria2 二进制内置，开箱即用

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
# 下载 aria2 二进制 (仅首次构建需要)
python scripts/download_aria2.py

# 单文件打包
python -m nuitka \
    --standalone --onefile \
    --enable-plugin=pyqt5 \
    --include-data-dir=resources/bin=resources/bin \
    --include-data-dir=resources/icons=resources/icons \
    --include-data-dir=resources/themes=resources/themes \
    --output-dir=dist --product-name=CherryDrop \
    main.py
```

## 项目结构

```
cherrydrop/
├── main.py                    # 入口
├── app/
│   ├── engine/
│   │   ├── aria2_client.py    # aria2 RPC 客户端 (BT 优化)
│   │   ├── tracker_updater.py # Tracker 自动更新 (规划中)
│   │   └── amule_client.py    # ed2k 支持 (骨架)
│   ├── widgets/
│   │   ├── task_list.py       # 下载任务列表 (规划中)
│   │   └── progress_bar.py    # 毛玻璃进度条 (规划中)
│   ├── dialogs/
│   │   ├── add_task.py        # 添加下载 (规划中)
│   │   └── settings.py        # 设置含 BT/代理 (规划中)
│   └── utils/
│       ├── config.py          # JSON 配置管理
│       └── theme.py           # QSS 主题加载
├── resources/
│   ├── aria2.conf             # aria2 配置 (来自 motrix-next)
│   ├── bin/linux/aria2c       # 内置二进制
│   ├── icons/
│   └── themes/cherry.qss      # 毛玻璃主题
└── scripts/
    └── download_aria2.py      # 多平台二进制下载
```

## 依赖

- Python 3.10+
- PyQt5
- aria2p
- requests

## 协议

MIT
