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

### CI/CD 最终状态 (2026-05-02)
- ✅ **三平台构建全部通过**: Linux (45MB) / macOS (30MB) / Windows (70MB)
- ✅ **v0.1.0 已发布**: https://github.com/HDILP/cherrydrop/releases/tag/v0.1.0
- ⚠️ **体积说明**: PyQt5 核心库 ~50-70MB 基线, `--nofollow-import-to=PyQt5.QtWebEngine,PyQt5.QtMultimedia` 已排除大模块

**CI 踩坑记录:**
- Release job 必须加 `actions/checkout@v4` (gh CLI 需要 git 上下文)
- 构建后必须清理 `dist/*.onefile-build dist/*.dist dist/*.build` 防止上传垃圾文件
- Nuitka 4.0.8 不支持 `--upx` / `--strip` / `--include-data-dir` (单文件)
- Release 用 `if ! gh release view; then create; fi` 而非 `|| true` (防静默吞错误)

### 进行中
- [ ] 暂无 — 所有迭代已完成 🎉

## Plan

完整开发计划见 `PLAN.md` (2498 行)