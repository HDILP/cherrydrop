### 已完成
- [x] 迭代 0: 项目骨架 (虚拟环境、目录结构、main.py)
- [x] 迭代 1: 配置系统 + 毛玻璃主题 QSS
- [x] 迭代 2: aria2 引擎层 (RPC 客户端 + BT/DHT 优化 + ed2k 骨架)
- [x] 迭代 3: 进度条 (GlassProgressBar) + 任务列表 (TaskList/TaskItemWidget)
- [x] 迭代 4: 对话框 (添加下载 + 设置窗口, 4 Tab)
- [x] 迭代 5: 主窗口整合 + main.py 更新
- [x] 迭代 6: BT 网络加速 + Tracker 管理
- [x] 迭代 7: 便携打包 + aria2 二进制管理
- [x] aria2 二进制 (Linux x86_64 v1.36.0) 内置 + 6 平台二进制全部提交到仓库
- [x] 迭代 8: 系统托盘完善 (SVG 图标)
- [x] 迭代 9: CI/CD 与 README 完善
- [x] 迭代 10: 错误处理 (aria2c 检测、空状态提示、单例锁、代理拼接修复)
- [x] 迭代 11: 打磨优化 (自适应刷新、拖拽支持)
- [x] aria2 配置改用 `--conf-path=resources/aria2.conf` (motrix-next 原版参数), 代码只传动态参数
- [x] **PR #1** (codex/find-and-fix-catastrophic-bugs): 启动崩溃修复 + Windows 兼容
  - `_try_lock()`: Windows 回退 (AF_UNIX 不可用时改用 PID 文件)
  - `main()`: QApplication 移到单例检查前 (否则 MessageBox 无法弹出)
  - 高 DPI 支持 (`AA_EnableHighDpiScaling`, `AA_UseHighDpiPixmaps`)
  - `config.py`: save() 加 try/except; get_download_dir() 失败时回退 ~/Downloads
- [x] **PR #2** (codex/modify-ci-release-process-for-github): 每次构建都发布到 GitHub Releases
  - 移除 `if: startsWith(github.ref, 'refs/tags/')` 限制
  - 非 tag 构建 → 创建预发布 `build-<run_number>`，带 CI 链接
  - tag 构建 → 正常发布，`--generate-notes`
  - 所有平台产物自动上传对应 release

### 全部迭代已完成 🎉

### CLI 参数 (v0.1.0+)
- `CherryDrop --version` — 显示版本号并退出（无需显示器）
- `CherryDrop -h / --help` — 显示帮助
- `CherryDrop -d <URL> / --download-url <URL>` — 无 GUI 下载测试（CI 用）
  - 启动 aria2c RPC → add_uri → 轮询完成 → 验证文件存在
  - 失败时 exit 1，不创建临时文件残留
- 这三个参数在 `QApplication` 创建前截获，无需显示器

### CI/CD 状态 (2026-05-03)
- ✅ **触发方式**: push main / push tag v* / workflow_dispatch
- ✅ Linux (ubuntu-latest) — 构建通过
- ✅ Windows (windows-latest) — 构建通过
- ✅ macOS ARM64 (macos-latest) — 构建通过
- ✅ macOS Intel (macos-15-intel) — ✅ Run #47 通过 (uv Python 方案)
- ✅ **双 macOS 矩阵**: Intel + ARM 各产一个 .zip, 含对应架构 aria2c
- ✅ **自动发布**: 每次 push/main 构建 → 预发布 `build-<run_number>`；tag 推送 → 正式 release
- ✅ **Smoke test** (构建后自动执行，失败 = 不上传 artifact):
  - `--version` 验证二进制可执行
  - Linux: xvfb GUI 5s 不崩溃 + 真实 HTTP 下载测试
  - macOS: .app bundle 完整性 + aria2c 捆绑检查 + 真实 HTTP 下载测试
  - Windows: --version + 真实 HTTP 下载测试
  - 测试 URL: repo 自身 README.md (GitHub raw)
- ⚠️ **体积**: PyQt5 ~50-70MB 基线, `--nofollow-import-to=PyQt5.QtWebEngine,...` 已排除大模块

**CI 踩坑记录:**
- **Nuitka bug #3777** (Intel macOS): Nuitka 4.0.8 dylib 扫描器遇见链接 Homebrew OpenSSL 的 Python 会 FATAL crash。最终方案：**全线 macOS 用 uv Python**（uv standalone Python 自带 OpenSSL，不依赖 Homebrew）。修了 ~10 次才搞定，别走回头路。
- Release job 必须加 `actions/checkout@v4` (gh CLI 需要 git 上下文)
- 构建后必须清理 `dist/*.onefile-build dist/*.dist dist/*.build` 防止上传垃圾文件
- Nuitka 4.0.8 不支持 `--upx` / `--strip` / `--include-data-dir` (单文件)
- Release 用 `if ! gh release view; then create; fi` 而非 `|| true` (防静默吞错误)
- macOS 双 runner 方案参考 motrix-next: `macos-latest` (ARM) + `macos-15-intel` (x86_64)
- brew 的 `$XZ_DIR` 变量名在 GitHub Actions YAML 中会被特殊处理 → 用绝对路径替代
- `bash -e` 模式下 if 条件为 false 会直接退出 → 加 `|| true`

### 发布
- ✅ **v0.1.0 已发布**: https://github.com/HDILP/cherrydrop/releases/tag/v0.1.0
  - 🐧 Linux: CherryDrop (45 MB)
  - 🍎 macOS Intel: CherryDrop-macOS-x86_64.zip (28 MB)
  - 🍏 macOS ARM: CherryDrop-macOS-arm64.zip (26 MB)
  - 🪟 Windows: CherryDrop.exe (70 MB)

## Plan

完整开发计划见 `PLAN.md` (2498 行)
