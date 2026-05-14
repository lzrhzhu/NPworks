# NPworks — 开发计划

本文件仅保留待开发功能。已完成的功能和项目文档请参阅 [README.md](README.md)。

## 待开发功能

### P0: 编辑器与运行增强

| # | 功能 | 说明 | 涉及文件 |
|---|------|------|---------|
| 1 | 自动配对括号/引号 | `_on_char_added` 空壳，应实现 `()`, `[]`, `{}`, `""`, `''` 自动关闭 | `editor.py` |
| 2 | 拖放 .py 创建新标签 | 当前拖放到已有标签替换内容，应新建标签 | `editor.py`, `main_window.py` |
| 4 | 运行当前行发送到终端 | `_run_line_in_terminal` 提取了文本但未发送 | `main_window.py` |

| 6 | 错误行号跳转 | 解析 traceback，输出面板错误行号可点击跳转 | `output_panel.py`, `main_window.py` |
| 7 | 关闭未保存标签确认 | 关闭已修改标签页时弹出确认对话框 | `tab_manager.py`, `main_window.py` |
| 8 | Go to Line (Ctrl+G) | 跳转到指定行号 | `editor.py`, `main_window.py` |
| 9 | 关闭标签页 (Ctrl+W) | 快捷键关闭当前标签 | `main_window.py` |
| 10 | 关闭其他标签/关闭全部 | 标签右键菜单增加批量关闭 | `tab_manager.py` |

### P1: 文件树与终端

| # | 功能 | 说明 | 涉及文件 |
|---|------|------|---------|
| 1 | 文件树刷新按钮 UI | `refresh_current` 方法存在但未连接到工具栏按钮 | `file_tree.py` |
| 2 | 文件系统监视 | 外部文件变更（创建/删除）不反映到树中 | `file_tree.py` |
| 3 | 文件树复制/剪切/粘贴 | 文件操作缺失 | `file_tree.py` |
| 4 | Shell 终端自适应大小 | PTY 固定 120x30，窗口缩放不生效 | `shell_terminal.py` |
| 5 | Shell 终端文本选择 | 无法选中/复制终端输出 | `shell_terminal.py` |
| 6 | Shell 终端粘贴优化 | 逐字符发送，大段文本极慢，应批量写入 | `shell_terminal.py` |


### P2: 查找替换与输出面板

| # | 功能 | 说明 | 涉及文件 |
|---|------|------|---------|
| 1 | 查找高亮清除 | `_clear_find_highlight` 空壳 `pass`，关闭查找面板后高亮残留 | `main_window.py` |
| 2 | 正则查找 | `is_regex()` 硬编码返回 False | `find_replace.py`, `main_window.py` |
| 3 | 输出面板搜索 | Ctrl+F 内嵌搜索栏 | `output_panel.py` |
| 4 | 输出面板清屏按钮 | `clear_output` 方法存在但无 UI 按钮 | `output_panel.py` |
| 5 | 输出面板缓冲区管理 | 输出无限增长，无截断机制 | `output_panel.py` |

### P3: 界面完善

| # | 功能 | 说明 | 涉及文件 |
|---|------|------|---------|
| 1 | 大纲视图 | sidebar2 目前是占位 QLabel "开发中" | `main_window.py`, 新增 `outline_view.py` |
| 2 | 设置按钮处理 | 活动栏设置图标点击无响应 | `main_window.py` |
| 3 | 设置面板 | 字体、Tab 宽度、超时时间等可配置 | 新增 `settings_dialog.py` |
| 4 | 命令面板 | Ctrl+Shift+P 模糊搜索执行命令 | 新增 `command_palette.py` |
| 5 | 欢迎页 | 无文件打开时显示富文本欢迎页 | `main_window.py` |
| 6 | 右键上下文菜单 | 编辑器/文件树/输出面板各自右键菜单 | `editor.py`, `file_tree.py`, `output_panel.py` |
| 7 | Markdown 预览主题适配 | CSS 硬编码暗色，不随亮色/暗色主题切换 | `preview_markdown.py` |
| 8 | PDF 预览性能优化 | 每次缩放重渲染所有页面，大 PDF 极慢 | `preview_pdf.py` |
| 9 | 图片预览缩放 | 无 zoom 控件，背景硬编码暗色 | `preview_image.py` |

### P4: 教学功能

| # | 功能 | 说明 | 涉及文件 |
|---|------|------|---------|
| 1 | 学习进度追踪 | QSettings 记录完成状态，文件树显示图标 | `file_tree.py`, `main_window.py` |
| 2 | 代码说明面板 | meta.yaml 扩展 explanation 字段，Markdown 渲染 | 新增 `explanation_panel.py` |
| 3 | Diff 视图 | 当前代码 vs 原始教材代码对比 | 新增 `diff_view.py` |
| 4 | 练习模式 | meta.yaml 新增 exercise 块，TODO 标记 + 答案检查 | 新增 `exercise_panel.py` |

### P5: 扩展与发布

| # | 功能 | 说明 | 涉及文件 |
|---|------|------|---------|
| 1 | 导出 HTML/PDF | 代码 + 高亮 + 输出导出 | 新增 `export.py` |
| 2 | 在线更新检查 | 启动时检查 content 包新版本 | 新增 `update_checker.py` |
| 3 | 清理弃用文件 | 删除 highlighter.py, line_number_area.py, toolbar.py, chapter_tree.py | 项目清理 |
| 4 | 版本号同步 | `__init__.py` 0.0.1 vs `pyproject.toml` 0.0.2 | `__init__.py` |
| 5 | 修复测试 | test_loader.py/test_executor.py 引用旧包名 `pyphysbook_*` | `tests/` |
| 6 | 测试硬编码路径 | test_editor_static.py/test_migration.py 硬编码 `G:\npworks\...` | `tests/` |
| 7 | 补充测试覆盖 | 13 个模块无测试（file_tree, output_panel, find_replace 等） | `tests/` |
| 8 | PyPI 发布 | CI + build + twine upload | GitHub Actions |
| 9 | 工具栏集成 | toolbar.py 定义了工具栏但未集成到 MainWindow | `main_window.py` |

## 空壳方法清单

以下方法已定义但实现为 `pass` 或硬编码返回值，需要补全：

| 文件 | 行 | 方法 | 状态 |
|------|---|------|------|
| `editor.py` | 219 | `_on_char_added(char)` | `pass` — 应实现自动配对 |
| `main_window.py` | 619 | `_clear_find_highlight()` | `pass` — 应清除查找高亮 |
| `terminal.py` | 50 | `_on_executed()` | `pass` — 可用于状态更新 |
| `file_tree.py` | 425 | `cleanup()` | `pass` — 可用于释放资源 |
| `find_replace.py` | 137 | `is_regex()` | 硬编码 `return False` |

## 已知问题

1. **仅支持 Windows**：Shell 终端使用 `pywinpty`，非 Windows 平台需适配
2. **IPython 内核预导入较重**：启动时导入 numpy/scipy/matplotlib 可能较慢
3. **字体硬编码**：编辑器 Consolas 11 不可配置
4. **matplotlib RC 注入偏移行号**：每次运行注入 3 行配置，traceback 行号需调整
