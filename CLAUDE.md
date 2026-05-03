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

### CI/CD 状态 (2026-05-03) ✅ 全平台通过
- ✅ **触发方式**: push main / push tag v* / workflow_dispatch
- ✅ **Linux** (ubuntu-latest) — 构建 + smoke test 通过
  - `main.bin` (Nuitka standalone 产出名，非 `main`)
  - Qt 运行时清理: `libQt5*.so.5` 剔除无用模块
  - UPX 压缩: `main.bin` + `aria2c`
  - 最终产物: `CherryDrop.tar.xz` (~40MB)
  - Smoke: `--version` ✓ + GUI(xvfb) ⚠ xcb 插件容错 + 真实下载 ✓
- ✅ **macOS ARM** (macos-latest) — 构建 + smoke test 通过
- ✅ **macOS Intel** (macos-15-intel) — 构建 + smoke test 通过
  - Qt 运行时清理: 裸文件名 `Qt*`
  - 最终产物: `.app.zip` (~25MB, 只含对应架构 aria2c)
  - Smoke: `--version` ✓ + aria2c 捆绑检查 ✓ + 真实下载 ✓
- ✅ **Windows** (windows-latest) — 构建 + smoke test 通过
  - Qt 运行时清理: `qt5*.dll`（小写 + qt5 前缀）
  - UPX 压缩: `main.exe` + `aria2c.exe`
  - 最终产物: 7z SFX 自解压 `CherryDrop.exe` (~15MB)
  - Smoke: `--version` ✓ + 真实下载 ✓
- ✅ **自动发布**: 每次 push/main 构建 → 预发布 `build-<run_number>`；tag 推送 → 正式 release
  - Release job 需 `actions/checkout@v4` + `download-artifact@v4`
  - `upload-artifact@v4` 多路径需用 YAML 多行格式（空格分隔在 v4 中不生效）
- ✅ **Smoke test** 覆盖:
  - `--version` 验证二进制可执行
  - Linux: xvfb GUI 5s 不崩溃（xcb 插件缺失时跳过） + 真实 HTTP 下载
  - macOS: .app bundle 完整性 + aria2c 捆绑检查 + 真实 HTTP 下载
  - Windows: --version + 真实 HTTP 下载
  - 测试 URL: repo 自身 README.md (GitHub raw)
- ✅ **PyQt5 黑名单全覆盖**: 44 个无用模块全部列在 `--nofollow-import-to`，只留 QtWidgets/Core/Gui
- ✅ **Qt 运行时清理三平台命名差异**:
  - Linux: `libQt5<Module>.so.5` → 搜 `libQt5${m}.so*`
  - Windows: `qt5<module>.dll` → 搜 `qt5$(echo ...).dll`（tr 小写，兼容 macOS bash 3.2）
  - macOS: `Qt<Module>` → 搜 `Qt${m}`
- ✅ **UPX 压缩**: 在 Prepare artifacts 阶段手动 UPX（非 Nuitka 内置）

**CI 踩坑记录:**
- **Nuitka bug #3777** (Intel macOS): Nuitka 4.0.8 dylib 扫描器遇见链接 Homebrew OpenSSL 的 Python 会 FATAL crash。最终方案：**全线 macOS 用 uv Python**（uv standalone Python 自带 OpenSSL，不依赖 Homebrew）。修了 ~10 次才搞定，别走回头路。
- Release job 必须加 `actions/checkout@v4` (gh CLI 需要 git 上下文)
- 构建后清理 `dist/*.onefile-build dist/*.build`（注意：**不要删 `dist/*.dist`**，那会删掉 standalone 输出 `main.dist`）
- Nuitka 4.0.8 `--mode=standalone` 支持 `--include-data-dir`；UPX 在 Prepare artifacts 阶段手动执行（非 Nuitka 内置 `--upx`）
- Release 用 `if ! gh release view; then create; fi` 而非 `|| true` (防静默吞错误)
- macOS 双 runner 方案参考 motrix-next: `macos-latest` (ARM) + `macos-15-intel` (x86_64)
- brew 的 `$XZ_DIR` 变量名在 GitHub Actions YAML 中会被特殊处理 → 用绝对路径替代
- `bash -e` 模式下 if 条件为 false 会直接退出 → 加 `|| true`
- **macOS `.app` 内部二进制名来自源文件名**：`main.py` → `CherryDrop.app/Contents/MacOS/main`。Smoke test 中路径必须写 `main` 而非 `CherryDrop`
- **Linux standalone 产出 `main.bin` 而非 `main`**：Nuitka 4.0.8 `--mode=standalone` 在 Linux 上编译出的主二进制名为 `main.bin`（macOS/Windows 上为 `.app/main` / `main.exe`）。UPX、smoke test 中必须写 `main.bin`
- **Qt 清理三平台命名差异**：
  - Linux: `libQt5<Module>.so.5`（需搜 `libQt5${m}.so*`）
  - Windows: `qt5<module>.dll`（小写 + qt5 前缀）
  - macOS: `Qt<Module>`（裸文件名）
- **Nuitka 4.0.8 通配符不覆盖白名单**：`--nofollow-import-to=PyQt5.*` + `--follow-import-to=QtWidgets` 不可行，通配符会连带白名单模块也排除。必须用显式黑名单逐项列出不需要的模块

### 发布
- ✅ **v0.1.0 已发布**: https://github.com/HDILP/cherrydrop/releases/tag/v0.1.0
  - 🐧 Linux: CherryDrop (45 MB)
  - 🍎 macOS Intel: CherryDrop-macOS-x86_64.zip (28 MB)
  - 🍏 macOS ARM: CherryDrop-macOS-arm64.zip (26 MB)
  - 🪟 Windows: CherryDrop.exe (70 MB)

## Plan

完整开发计划见 `PLAN.md` (2498 行)
