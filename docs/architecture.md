# CherryDrop 架构

> 樱色轻量下载器 — 便携单文件，开箱即用

## 技术栈

| 层 | 组件 |
|---|------|
| 前端 | PyQt5 (毛玻璃主题 QSS) |
| 引擎 | aria2 RPC (内置 aria2c 二进制) |
| CLI 模式 | `--version`, `--help`, `-d <URL>` (无头) |
| 打包 | Nuitka 4.0.8 → 单文件 / .app |
| CI/CD | GitHub Actions (4 平台矩阵 + smoke test + 自动发布) |

## 项目结构

```
cherrydrop/
├── main.py                  # 入口：CLI 参数 → 单例锁 → 配置 → 主题 → 引擎 → 主窗口
├── app/
│   ├── main_window.py       # 主窗口整合 (工具栏/任务列表/系统托盘)
│   ├── engine/
│   │   ├── aria2_client.py  # aria2 RPC 封装 (启动/停止/添加任务/Tracker热更新)
│   │   ├── amule_client.py  # ed2k 协议封装 (可选, 依赖 amulecmd)
│   │   └── tracker_updater.py  # BT Tracker 自动更新 (CDN 镜像源)
│   ├── widgets/
│   │   ├── task_list.py     # 任务列表组件 (右键菜单 + Peer 显示)
│   │   └── progress_bar.py  # 毛玻璃进度条
│   ├── dialogs/
│   │   ├── add_task.py      # 添加下载对话框
│   │   └── settings.py      # 设置窗口 (4 Tab)
│   └── utils/
│       ├── config.py        # JSON 配置管理 (settings.json)
│       └── theme.py         # QSS 毛玻璃主题加载
├── resources/
│   ├── aria2.conf           # aria2 静态参数 (motrix-next 原版)
│   ├── bin/                 # aria2c 二进制 (各平台)
│   ├── icons/               # SVG 图标
│   └── themes/              # QSS 主题文件
├── scripts/
│   ├── build.sh             # Linux/macOS 构建脚本
│   └── build.bat            # Windows 构建脚本
└── .github/workflows/
    └── build.yml            # CI/CD: 4 平台构建 + GitHub Release
```

## 关键设计决策

### aria2 配置分离
- 静态参数 → `resources/aria2.conf` (motrix-next 原版)
- 动态参数 → 代码中通过 RPC 传入 (下载目录、tracker、代理)
- 好处：aria2 自带 session 管理，无需额外数据库

### BT 网络加速
- DHT/PEX/LPD 三管齐下
- Tracker 列表每日自 CDN 镜像拉取 (XIU2/TrackersListCollection)
- 伪装 Transmission 客户端标识
- 参数参考 motrix-next 的 BT 优化

### 单例锁
- UNIX flock + PID 文件
- 防止多开 (已在 v0.1.0 中实现)

### CLI 模式（无 GUI）
在 QApplication 创建前截获参数，无需显示器：
- `--version` / `--help` — 快速验证二进制可执行
- `-d <URL>` — 完整下载链路测试：启动 aria2c RPC → add_uri → 轮询 → 验证文件
- 用于 CI smoke test、本地快速验证

### 打包策略
- Nuitka 4.0.8 → `--mode=app` (macOS) / `--mode=onefile` (Linux/Windows)
- macOS 双 runner: `macos-latest` (ARM) + `macos-15-intel` (x86_64)
- 每个 .app 只含对应架构的 aria2c
- 体积优化：排除 QtWebEngine/QtMultimedia/无用 Qt 插件

## 已知修复

### PR #1 — 启动崩溃 + Windows 兼容
- `_try_lock()`: Windows 回退 (AF_UNIX 不可用时改 PID 文件)
- `main()`: QApplication 创建移到单例检查前（否则 MessageBox 无法弹出）
- 高 DPI 支持 (`AA_EnableHighDpiScaling`, `AA_UseHighDpiPixmaps`)
- `Config.save()`: 加 try/except 防写失败崩溃
- `Config.get_download_dir()`: 目录创建失败时回退 `~/Downloads`

### PR #2 — 每次构建自动发布到 GitHub Releases + Smoke test
- 移除 Release job 的 `if: startsWith(github.ref, 'refs/tags/')` 限制
- 非 tag 构建 → 创建预发布 `build-<run_number>`（带 CI 运行链接）
- tag 构建 → 正常发布（`--generate-notes`）
- 所有平台产物自动上传到对应 release
- ✅ **Smoke test**（构建后、上传前执行，失败则不上传）：
  - Linux: xvfb GUI 5s + 真实 HTTP 下载
  - macOS: .app bundle 完整性 + aria2c 检查 + 真实 HTTP 下载
  - Windows: --version + 真实 HTTP 下载
- ✅ **触发方式**: push main / push tag v* / workflow_dispatch

## CI 踩坑 (Nuitka #3777)

Intel macOS 的 Nuitka 4.0.8 dylib 扫描器遇见链接 Homebrew OpenSSL 的 Python 会 FATAL crash。
**最终方案**：全线 macOS 使用 uv Python (standalone Python 自带 OpenSSL，不依赖 Homebrew)。
详见 `CLAUDE.md` 踩坑记录。

## 发布

v0.1.0: https://github.com/HDILP/cherrydrop/releases/tag/v0.1.0

> **自动发布机制:** 每次 push 到 main → CI 自动构建并创建 `build-<run_number>` 预发布（含产物下载链接）；
> 推送 tag → 创建正式 release。无需手动发布。详见 PR #2。
