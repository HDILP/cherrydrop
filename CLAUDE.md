# CherryDrop — Agent Guide

## Tech Stack

- **语言**: Python 3.10+
- **GUI**: PyQt5 (Qt 5.15)
- **下载引擎**: aria2 (v1.36.0, 预编译静态二进制)
- **RPC 客户端**: aria2p (v0.12.1)
- **打包**: Nuitka (--standalone --onefile)
- **CI**: GitHub Actions (3 平台)

## Project Structure

```
cherrydrop/
├── main.py              # 入口
├── app/engine/          # 下载引擎
├── app/widgets/         # UI 组件
├── app/dialogs/         # 对话框
├── app/utils/           # 工具 (config, theme)
├── resources/
│   ├── aria2.conf       # aria2 配置 (来自 motrix-next)
│   ├── bin/<platform>/  # 预编译 aria2c 二进制
│   └── themes/          # QSS 样式
├── scripts/             # 构建/下载脚本
└── PLAN.md             # 完整开发计划
```

## Key Design Decisions

### aria2 参数 (47 个)
- RPC 端口 6800，通过 `aria2p.Client(port=6800)` 连接
- BT/DHT 优化：DHT+PEX+LPD，伪装 Transmission/3.00
- Tracker 通过 `--bt-tracker` 注入，每日自动更新
- 代理通过 `--all-proxy` 注入
- session 持久化：`--save-session` + 条件性 `--input-file`

### 中国网络优化
- Tracker 数据源用 CDN 镜像 (`cdn.jsdelivr.net`)
- Peer ID 伪装 `-TR3000-`，User-Agent `Transmission/3.00`
- 启动参数 `--bt-request-peer-speed-limit=100K` 防 QoS
- DHT 入口点 `dht.transmissionbt.com:6881`
- `--check-certificate=false` (国内网络环境)

### 打包策略
- aria2 二进制存放在 `resources/bin/<platform>/`
- `scripts/download_aria2.py` 从 motrix-next 仓库拉取预编译版本
- Nuitka `--onefile` 打包，aria2 二进制内嵌
- 6 平台覆盖: x86_64/aarch64 × Linux/macOS/Windows

### 启动流程 (aria2_client.py)
1. `_find_aria2_binary()` → 逐级检查打包二进制 → fallback PATH
2. `_build_aria2_args()` → 动态组装参数（含 BT/tracker/proxy）
3. `start()` → Popen → 端口轮询等待 (5s) → aria2p.Client 连接 → version 验证

## Conventions

- 配置管理: `app/utils/config.py`，`settings.json` 持久化
- UI 样式: QSS 文件 `resources/themes/cherry.qss`，主色 `#ffaab2`
- 日志: Python `logging` 模块
- Git: `main` 分支，commit message 前缀: 🎉 🔧 ✨ 🐛 🔄

## 项目状态 (2026-05-02)

### 已完成
- [x] 迭代 0: 项目骨架 (虚拟环境、目录结构、main.py)
- [x] 迭代 1: 配置系统 + 毛玻璃主题 QSS
- [x] 迭代 2: aria2 引擎层 (RPC 客户端 + BT/DHT 优化 + ed2k 骨架)
- [x] aria2 二进制 (Linux x86_64 v1.36.0) 下载 & 测试

### 进行中
- [ ] 迭代 3: 进度条与任务列表组件
- [ ] 迭代 4: 对话框 (BT 网络/代理 设置)
- [ ] 迭代 5: 主窗口整合
- [ ] 迭代 6: BT 网络加速 + Tracker 管理
- [ ] 迭代 7: 便携打包 + aria2 二进制管理
- [ ] 迭代 8-11: 系统托盘、CI/CD、错误处理、打磨

## Plan

完整开发计划见 `PLAN.md` (2498 行)
