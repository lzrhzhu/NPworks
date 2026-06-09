# NPworks 改进计划

> 版本: 1.0 | 日期: 2026-05-14 | 状态: 草案

本文档基于对整个代码库（IDE 包 ~4,500 行、Content 包 ~54 行、测试 ~400 行）的全面审查，按阶段和优先级组织改进工作。

---

## 阶段一：架构重构（高优先级）

### 1.1 拆分 MainWindow God Class

**问题**: `main_window.py`（790 行 / 60+ 方法）承担了菜单构建、文件IO、运行管理、查找替换、主题切换、状态持久化等所有职责。

**方案**: 按职责域拆分为独立控制器类，MainWindow 仅保留布局和对象装配。

| 新文件 | 职责 | 从 MainWindow 迁出的方法 |
|--------|------|--------------------------|
| `ide/menu_builder.py` | 菜单/快捷键构建 | `_build_menu_bar()`, `_add_action()` |
| `ide/run_controller.py` | 代码运行/停止/终端管理 | `_run_code()`, `_stop_code()`, `_reset_code()`, `_run_line_in_terminal()`, `_run_line_in_shell()`, `_on_execution_started()`, `_on_execution_finished()`, `_send_input()` |
| `ide/find_controller.py` | 查找/替换逻辑 | `_find_next()`, `_find_prev()`, `_replace_one()`, `_replace_all()`, `_clear_find_highlight()` |
| `ide/edit_controller.py` | 编辑操作代理 | `_undo()`, `_redo()`, `_cut()`, `_copy()`, `_paste()`, `_select_all()`, `_toggle_comment()`, `_go_to_line()` |
| `ide/theme_controller.py` | 主题切换与传播 | `_set_theme()`, 主题传播逻辑 |

**重构后 MainWindow 保留**: `__init__`, `_setup_layout`, `_setup_activity_bar`, `_build_status_bar`, `_connect_signals`, `_on_tab_changed`, `_on_file_selected`, `_open_file_by_path`, `closeEvent`, 状态恢复/保存。

**目标**: MainWindow 降至 ~400 行，每个控制器 80-150 行。

### 1.2 QSS 外部化

**问题**: `theme.py` 内嵌 437 行 QSS 模板字符串，维护困难。

**方案**:

```
src/npworks_ide/ide/themes/
├── __init__.py          # apply_theme(), get_colors()
├── variables.py         # _LIGHT_VARS, _DARK_VARS, LIGHT, DARK
├── light.qss            # 亮色主题样式
├── dark.qss             # 暗色主题样式
└── palette.py           # QPalette 配置
```

- `.qss` 文件使用 `{var_name}` 占位符，运行时通过 `string.Template` 替换
- 消除所有 `{{`/`}}` 双花括号转义，提升可读性
- 按组件分块注释（`/* === Menu === */`, `/* === TabBar === */`）

**修复硬编码颜色**（当前在 QSS 模板中）:

| 位置 | 当前值 | 改为变量 |
|------|--------|----------|
| QMenu::item:selected color | `#FFFFFF` | `{menu_selection_fg}` |
| QStatusBar background | `#007ACC` | `{statusbar_bg}` |
| QTabBar::close-button:hover color | `#FFFFFF` | `{close_fg}` |
| #terminal_display background | `#1E1E1E` | `{terminal_bg}` |
| #terminal_display color | `#CCCCCC` | `{terminal_fg}` |
| QStackedWidget background | `#1E1E1E` | `{terminal_bg}` |
| #terminal_prompt color | `#6A9955` | `{terminal_prompt_fg}` |

### 1.3 跨平台兼容性修复

**问题**: `shell_terminal.py:13-14` 无条件 `from winpty import PTY; import pyte`，非 Windows 启动即崩溃。

**方案**:

```python
import sys
if sys.platform == "win32":
    from winpty import PTY
    import pyte
    _HAS_WINPTY = True
else:
    _HAS_WINPTY = False
```

- `ShellTerminalWidget.__init__` 中检查 `_HAS_WINPTY`，不可用时显示 "Shell 终端仅支持 Windows" 提示
- 为 Linux/macOS 添加基于 `QProcess` + `/bin/bash` 的备选终端实现（可后续阶段）

---

## 阶段二：代码质量（中优先级）

### 2.1 消除跨类私有方法访问

**当前违规调用**:

| 调用位置 | 目标 | 改为公共方法 |
|----------|------|-------------|
| `main_window.py:419,429,439,456` | `self._actions._add_recent_file(path)` | `ActionManager.add_recent_file(path)` |
| `main_window.py:494` | `self._bottom_panel._ensure_terminal()` | `BottomPanel.ensure_terminal()` |
| `main_window.py:507` | `self._bottom_panel._ensure_shell()` | `BottomPanel.ensure_shell()` |
| `main_window.py:785` | `self._actions._save_open_folders()` | `ActionManager.save_open_folders()` |

### 2.2 统一主题到预览组件

**问题**: `preview_pdf.py`、`preview_markdown.py`、`preview_image.py` 始终使用暗色主题硬编码颜色。

| 文件 | 硬编码位置 | 修复方式 |
|------|-----------|----------|
| `preview_pdf.py:35-59` | toolbar background `#2D2D2D`, button styles | 改为 `get_colors()` 驱动 |
| `preview_image.py:29` | `background: #1E1E1E` | 改为主题变量 |
| `preview_markdown.py:29-50` | `_CSS` 使用暗色值 | 根据主题选择 CSS |

### 2.3 消除重复代码

| 重复模式 | 出现位置 | 统一方案 |
|----------|----------|----------|
| `os.makedirs(os.path.expanduser("~/npworks"), exist_ok=True)` | `main_window.py:383`, `actions.py:28,83,103` | 提取为 `utils.ensure_default_dir()` |
| 编辑器信号连接（3 行） | `main_window.py:378-380, 453-455` | 提取为 `_wire_editor_signals(editor)` |
| `QFont("Consolas", 11)` | `editor.py:53,58,106`, `shell_terminal.py:24` | 提取为 `config.EDITOR_FONT` |
| `QFont("Segoe UI", 9/10)` | `main_window.py:247,255,263,272`, `app.py:19` | 提取为 `config.UI_FONT` |

### 2.4 消除静默异常吞没

| 位置 | 当前行为 | 改进 |
|------|----------|------|
| `file_tree.py:127` | `shutil.move` 失败静默 | `QMessageBox.warning()` |
| `file_tree.py:221` | `init_textbook` 异常静默 | 日志 + 状态栏提示 |
| `tab_manager.py:74` | 保存失败静默 | `QMessageBox.warning()` |
| `preview_markdown.py:63,120,166` | 文件读写失败静默 | 状态栏提示 |
| `loader.py:31` | 无 FileNotFoundError 处理 | 返回友好错误消息 |

### 2.5 可配置化硬编码常量

```python
# config.py（新建）
EDITOR_FONT_FAMILY = "Consolas"
EDITOR_FONT_SIZE = 11
UI_FONT_FAMILY = "Segoe UI"
UI_FONT_SIZE = 9
ACTIVITY_BAR_WIDTH = 48
SIDEBAR_WIDTH = 260
DEFAULT_WINDOW_SIZE = (1280, 860)
DEFAULT_WORKSPACE = "~/npworks"
```

---

## 阶段三：测试补全（中优先级）

### 3.1 测试基础设施

- 创建 `tests/conftest.py`，配置 `sys.path` 和 pytest fixture
- 在 `packages/npworks-ide/pyproject.toml` 添加:

```toml
[tool.pytest.ini_options]
testpaths = ["../../tests"]
python_files = ["test_*.py"]
```

### 3.2 迁移现有 print-based 测试

| 文件 | 迁移操作 |
|------|----------|
| `test_editor_basic.py` | `print(...)` → `assert ...` |
| `test_editor_static.py` | `print(...)` → `assert ...` |
| `test_app.py` | 保留 smoke test 结构，加 assert |
| `test_gui.py`, `test_gui2.py`, `test_gui3.py` | 合并为 `test_editor_widget.py` |
| `test_migration.py` | `print(...)` → `assert ...` |

### 3.3 新增测试用例

| 模块 | 缺失测试 | 优先级 |
|------|----------|--------|
| `actions.py` | save, save_as, recent files | 高（数据安全） |
| `tab_manager.py` | tab lifecycle, close-with-unsaved | 高 |
| `executor.py` | 实际代码执行、stdout/stderr 捕获 | 高 |
| `find_replace.py` | find_next, find_prev, replace_all | 中 |
| `theme.py` | apply_theme 输出、QSS 正确性 | 中 |
| `output_panel.py` | traceback 链接生成 | 中 |
| `file_tree.py` | add_root, populate, drag-drop | 低 |
| `loader.py` | meta.yaml 验证、缺失文件处理 | 低 |

---

## 阶段四：类型标注与文档（低优先级）

### 4.1 添加类型标注

优先在公共接口和复杂方法上添加:

- `content/loader.py`: `get_chapters() -> list[dict[str, Any]]`
- `ide/editor.py`: `_on_char_added(self, char: int) -> None`
- `ide/actions.py`: 所有公开方法参数和返回值
- `ide/tab_manager.py`: 所有方法
- `ide/theme.py`: `get_colors(theme_name: str | None = None) -> dict`

### 4.2 添加 docstrings

按优先级:

1. Content 包公共 API（`__init__.py` 的 4 个函数）
2. Editor 公共方法（`set_code`, `get_code`, `toggle_comment` 等）
3. MainWindow 控制器方法
4. 内部工具方法

---

## 阶段五：功能增强（远期）

### 5.1 大纲视图（已有占位）

当前 `main_window.py:77` 仅显示"开发中"占位符。实现思路:
- 解析当前编辑器中的 `class`、`def` 定义
- 使用 `QTreeWidget` 显示符号树
- 点击跳转到对应行

### 5.2 设置面板

Activity Bar 已有"⚙ 设置"按钮（`main_window.py:132`），但无功能。可配置项:
- 字体/字号
- 主题
- 快捷键
- 默认工作目录

### 5.3 内容包增强

- `meta.yaml` schema 验证
- `get_section_code()` 缓存
- 缺失文件友好错误消息

---

## 实施顺序建议

```
阶段 1.3  跨平台修复          ← 影响最大，改动最小
阶段 2.1  公共方法重命名        ← 无风险重构
阶段 2.3  消除重复代码          ← 提取 config.py + utils.py
阶段 2.5  可配置化常量
阶段 3.1  测试基础设施
阶段 3.2  迁移现有测试
阶段 1.2  QSS 外部化           ← 大改动，先有测试保障
阶段 2.2  预览组件主题统一
阶段 2.4  错误处理改进
阶段 1.1  MainWindow 拆分       ← 最大重构，最后做
阶段 3.3  新增测试
阶段 4.x  类型标注与文档
阶段 5.x  功能增强
```

---

## 检查清单

每个阶段完成后的验证标准:

- [ ] 所有现有测试通过 (`pytest tests/`)
- [ ] IDE 正常启动 (`python -m npworks_ide`)
- [ ] 亮色/暗色主题切换正常
- [ ] 打开文件、运行代码、查找替换功能正常
- [ ] 教材章节加载和显示正常
- [ ] 无新增 `import` 错误或运行时异常
