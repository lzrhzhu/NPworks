# NPworks — Numerical Physics Works

## 一、项目概述

### 1.1 目标

构建一个基于 PyQt5 + QScintilla 的桌面 IDE 应用，内置计算物理教材内容。学生通过以下方式即可使用：

```bash
pip install npworks
npworks
```

启动后左侧显示中文章节目录，右侧为多标签页代码编辑器，底部为输出/IPython/终端面板。点击章节加载对应 Python 程序，可直接编辑和运行。

### 1.2 核心特性

- **零配置**：`pip install` 一键安装，命令行直接启动
- **内置教材**：7 章 27 节 Python 物理计算示例，打包在安装包中
- **QScintilla 编辑器**：专业代码编辑体验（代码折叠、自动补全、括号匹配、智能缩进）
- **多标签页**：同时打开多个文件/章节，标签页可拖拽排序和关闭
- **双向导航**：目录树与标签页联动，点击目录打开代码，切换标签高亮目录
- **防重复打开**：再次点击同一章节自动跳转到已打开的标签页
- **三面板底部区**：输出面板（stdout/stderr）、IPython 终端（Jupyter 内核）、Shell 终端（PowerShell）
- **查找替换**：支持查找/替换/全部替换，大小写敏感开关
- **亮色/暗色主题**：完整的 VS Code 风格双主题（834 行 QSS 样式表）
- **代码执行**：QProcess 异步执行，不阻塞 GUI，支持 stdin 交互
- **中文支持**：matplotlib 自动配置中文字体（SimHei/Microsoft YaHei）

---

## 二、项目架构

### 2.1 三包 Monorepo 结构

```
npworks/                                # 本仓库
├── PLAN.md                             # 本文件
├── packages/
│   ├── README.md
│   ├── LICENSE                         # MIT
│   ├── npworks/                        # 元包（Meta Package）
│   │   ├── pyproject.toml              # 依赖: npworks-ide + npworks-content
│   │   └── README.md
│   ├── npworks-ide/                    # IDE 界面包
│   │   ├── pyproject.toml
│   │   └── src/npworks_ide/
│   │       ├── __init__.py             # __version__
│   │       ├── __main__.py             # python -m 支持
│   │       ├── app.py                  # 入口: QApplication + 主题 + MainWindow
│   │       ├── ide/
│   │       │   ├── main_window.py      # 主窗口 — VS Code 布局 (950 行)
│   │       │   ├── activity_bar.py     # 活动栏 (68 行)
│   │       │   ├── file_tree.py        # 多根文件浏览器 (416 行)
│   │       │   ├── editor.py           # QScintilla 代码编辑器 (321 行)
│   │       │   ├── chapter_tree.py     # 章节目录树 (56 行) — 已弃用
│   │       │   ├── output_panel.py     # 输出面板 (104 行)
│   │       │   ├── find_replace.py     # 查找替换 (140 行)
│   │       │   ├── theme.py            # 双主题系统 (1007 行)
│   │       │   ├── terminal.py         # IPython 终端 (81 行)
│   │       │   ├── shell_terminal.py   # Shell 终端 (439 行)
│   │       │   ├── highlighter.py      # 旧版 Pygments 高亮器（已弃用）
│   │       │   ├── line_number_area.py # 旧行号栏（已弃用）
│   │       │   └── toolbar.py          # 工具栏定义（未使用）
│   │       └── runner/
│   │           └── executor.py         # QProcess 代码执行器 (93 行)
│   └── npworks-content/                # 教材内容包
│       ├── pyproject.toml
│       └── src/npworks_content/
│           ├── __init__.py             # 公共 API
│           ├── loader.py               # 内容加载器 (37 行)
│           └── content/
│               ├── ch01_python_basics/ (5 个 .py)
│               ├── ch02_numerical/     (6 个 .py)
│               ├── ch03_mechanics/     (5 个 .py)
│               ├── ch04_electromagnetism/ (2 个 .py)
│               ├── ch05_thermodynamics/ (3 个 .py)
│               ├── ch06_quantum/       (3 个 .py)
│               └── ch07_waves/         (3 个 .py)
└── tests/
    ├── test_loader.py
    ├── test_executor.py
    ├── test_app.py
    ├── test_gui.py
    ├── test_gui2.py
    ├── test_gui3.py
    ├── test_migration.py
    ├── test_editor_static.py
    └── test_editor_basic.py
```

### 2.2 包间依赖关系

```
pip install npworks
    ├── npworks-ide
    │   ├── PyQt5 >= 5.15
    │   ├── QScintilla >= 2.13
    │   ├── pygments >= 2.0
    │   ├── numpy >= 1.20
    │   ├── scipy >= 1.7
    │   ├── matplotlib >= 3.4
    │   ├── qtconsole >= 5.0
    │   ├── pywinpty >= 2.0
    │   ├── pyte >= 0.8
    │   └── npworks-content >= 0.0.1
    └── npworks-content
        └── pyyaml >= 6.0
```

### 2.3 公共接口

IDE 通过以下标准接口加载 content 包，两者松耦合：

```python
import npworks_content

npworks_content.get_chapters()                              # → list[dict]
npworks_content.get_section_code(chapter_id, filename)     # → str
npworks_content.get_section_path(chapter_id, filename)     # → Path
npworks_content.get_version()                               # → str
```

---

## 三、IDE 界面布局

VS Code 风格布局：纯 QSplitter 实现（无 QDockWidget），活动栏固定 48px 不随侧边栏开关移动。

```
┌─────────────────────────────────────────────────────────────┐
│  菜单栏: 文件 | 编辑 | 运行 | 视图 | 帮助                      │
┌──┬──────────┬──────────────────────────────────┬────────────┐
│  │ 文件浏览器│  [查找替换面板] (Ctrl+F / Ctrl+H)   │  大纲       │
│  ├──────────┤                                  ├────────────┤
│活│          │  标签栏: [1.1 Hello World ×]       │            │
│动│  📖教材   │                                  │  大纲视图   │
│栏│  📂项目   │  # QScintilla 代码编辑区           │  （开发中）  │
│  │          │  import numpy as np               │            │
│  │          │  import matplotlib.pyplot as plt  │            │
│  │          │                                   │            │
│  ├──────────┴───────────────────────────────────┴────────────┤
│  │  [输出] [IPython] [终端]                          [▲] [✕]  │
│  │  >>> 运行中...                                             │
│  │  Hello, Computational Physics!                             │
│  │  [运行完毕] 退出码=0 耗时=0.12s                              │
├──┴───────────────────────────────────────────────────────────┤
│  状态栏:  ● 运行中 | 行 5, 列 12 | UTF-8 | Python 3.10        │
└──────────────────────────────────────────────────────────────┘

QSplitter 布局结构：
  _v_splitter (Vertical)
    ├── _h_splitter (Horizontal)
    │     ├── _activity_container  [固定 48px, stretch=0]
    │     ├── _sidebar1 (文件浏览器)  [默认 260px, stretch=0, 可折叠到 0]
    │     ├── _editor_area           [stretch=1, 自动填充]
    │     └── _sidebar2 (大纲)       [默认 0px, stretch=0, 可展开到 260px]
    └── _bottom_panel              [输出/IPython/终端]
```

---

## 四、各模块详细说明

### 4.1 `app.py` — 应用入口 (30 行)

程序入口点，负责初始化 Qt 应用并显示主窗口。

- 创建 `QApplication`，设置应用名称和组织名
- 设置全局字体为 Segoe UI 10pt
- 从 `QSettings` 读取上次主题偏好并应用
- 实例化 `MainWindow` 并进入事件循环

入口函数：`main()`，由 `pyproject.toml` 的 `console_scripts` 调用。

### 4.2 `ide/main_window.py` — 主窗口 (950 行)

VS Code 风格主窗口，使用纯 QSplitter 布局（活动栏 + 侧边栏 + 编辑区 + 底部面板）。

**主要组件**：
- `ActivityBar`：48px 固定宽度活动栏（文件浏览器/大纲/设置图标）
- `FileTree`：多根文件浏览器（教材 + 用户打开的文件夹，中文标题）
- `QTabWidget`：多标签页编辑器区域
- `BottomPanel`：底部三面板（输出/IPython/Shell终端）
- `FindReplacePanel`：查找替换面板

**布局结构（QSplitter 嵌套）**：
```
_v_splitter (Vertical)
  _h_splitter (Horizontal): [ActivityBar 48px] [Sidebar1] [EditorArea] [Sidebar2]
  BottomPanel
```
- 活动栏固定 48px，stretch=0，不随侧边栏开关移动
- 侧边栏通过设置 splitter sizes 为 0 折叠，展开时恢复 260px
- 分隔器大小通过 QSettings 持久化

**菜单栏**：
| 菜单 | 功能 |
|------|------|
| 文件 | 新建、打开、打开文件夹、最近文件、关闭文件夹、保存、另存为、退出 |
| 编辑 | 撤销、重做、剪切、复制、粘贴、全选、注释/取消注释、查找、替换 |
| 运行 | 运行(F5)、停止(Shift+F5)、重置代码(Ctrl+R)、运行当前行、新建/关闭终端 |
| 视图 | 文件浏览器、大纲、底部面板(Ctrl+`)、IPython/Shell终端、亮色/暗色主题 |
| 帮助 | 关于 |

**关键机制**：
- **活动栏切换**：点击图标切换侧边栏显示/隐藏，再次点击隐藏
- **标签页去重**：点击文件时遍历已有标签页，若已打开则切换过去
- **文件树同步**：切换标签页时自动在文件树中定位并高亮对应文件
- **多根文件树**：教材为默认根（不可关闭），用户可通过菜单打开多个文件夹

**状态栏**：运行状态、光标位置、编码、Python 版本。

### 4.3 `ide/editor.py` — 代码编辑器 (321 行)

基于 **QScintilla** (`QsciScintilla`) 的专业代码编辑器，非 QPlainTextEdit。

**内置类 `PythonLexer`** (`QsciLexerPython`)：
- 根据 theme.py 的颜色配置为 Python 各语法元素着色
- 关键字（蓝色粗体）、函数名（棕色）、类名（青色粗体）、字符串（红色）、注释（绿色斜体）、数字（绿色）

**编辑器功能**：
- 行号显示（Margin 0）、代码折叠（Margin 2，BoxedTree 样式）
- 自动补全（基于 `QsciAPIs`，包含 Python 关键字、内置函数、numpy/matplotlib 常用名称）
- 括号匹配高亮（黄色背景）
- 当前行高亮
- Tab = 4 空格，自动缩进
- 智能缩进：Enter 后继承上一行缩进，上一行以 `:` 结尾时自动增加 4 空格
- 智能退格：行首空白处 Backspace 一次删除 4 空格
- 注释切换：`Ctrl+/` 对选中行或当前行添加/移除 `# ` 前缀
- 拖放打开 `.py` 文件
- 双主题适配（亮色/暗色缩进参考线、折叠图标、边距颜色等）

**关键方法**：
- `set_code(code, original)` — 设置代码并记录原始版本
- `get_code()` — 获取当前代码文本
- `reset_to_original()` — 恢复为原始代码
- `toggle_comment()` — 切换注释
- `apply_theme()` — 应用当前主题颜色

### 4.4 `ide/activity_bar.py` — 活动栏 (68 行)

VS Code 风格垂直图标条，固定 48px 宽度。

- 继承 `QWidget`，顶部按钮区 + 弹性间距 + 底部按钮区
- 每个按钮为 48×48 可选中 `QPushButton`，使用 emoji 图标
- 点击按钮发射 `button_clicked(int)` 信号，再次点击取消选中
- `set_checked(index)` 设置当前选中按钮（蓝色左边框高亮）

### 4.5 `ide/file_tree.py` — 多根文件浏览器 (416 行)

统一的多根目录文件树，替代原有 `chapter_tree.py`。

- 继承 `QWidget`，包含 `QTreeWidget` + 底部工具栏
- **多根支持**：教材为默认根（不可关闭），用户可通过菜单/工具栏打开额外文件夹
- **中文标题**：解析 `meta.yaml` 显示教材章节/小节中文标题
- **延迟加载**：目录首次展开时才读取文件系统，展开前显示 "..." 占位符
- **自定义排序**：`_sort_key()` 支持数字前缀排序（01_ → 02_ → ...）
- **右键菜单**：打开、关闭文件夹、在资源管理器中打开、新建文件/文件夹
- **文件定位**：`select_file(path)` 自动展开目录树定位到指定文件
- **信号**：`file_selected(str)` 点击文件时发射，`open_folder_requested()` 点击打开文件夹按钮时发射
- 自定义数据角色：`_ROLE_PATH=1000, _ROLE_IS_DIR=1001, _ROLE_LOADED=1002, _ROLE_IS_ROOT=1003, _ROLE_IS_TEXTBOOK=1004`

### 4.6 `ide/chapter_tree.py` — 章节目录树 (56 行) — 已弃用

继承 `QTreeWidget`，显示教材章节结构。**已弃用**——已被 `file_tree.py` 替代，主窗口不再使用此组件。

~继承 `QTreeWidget`，显示教材章节结构。~

- 顶层节点为章（ch01, ch02, ...），子节点为各小节
- 通过 `npworks_content.get_chapters()` 获取元数据
- 使用 emoji 图标：📖（章节）、📄（小节）
- 点击小节时发射 `section_selected(chapter_id, filename)` 信号
- 章节节点存储 `chapter_id`（role 1000），小节节点额外存储 `filename`（role 1001）

### 4.7 `ide/output_panel.py` — 输出面板 (104 行)

底部面板中的"输出"标签页，显示代码运行结果。

- 继承 `QWidget`，包含只读 `QTextEdit` + 输入行
- 三种输出类型：stdout（深灰）、stderr（红色）、系统消息（蓝色斜体）
- 运行时显示 stdin 输入行（QLineEdit + 发送按钮），支持交互式程序
- 等宽字体 Consolas 10pt

### 4.8 `ide/find_replace.py` — 查找替换 (140 行)

编辑区上方的内嵌搜索面板。

- 查找输入框 + 上一个/下一个按钮 + 匹配计数 + 大小写开关
- 可展开替换行：替换 + 全部替换
- Escape 关闭，Enter 查找下一个
- 发射 `closed` 信号通知清除高亮

### 4.9 `ide/theme.py` — 主题系统 (1007 行)

完整的 VS Code 风格双主题系统。

**颜色定义**：
- `LIGHT` 字典：白色背景，VS Code 默认浅色配色
- `DARK` 字典：深灰背景，VS Code Dark+ 配色
- 每种颜色包含：background, foreground, current_line, line_number_bg/fg, selection_bg, keyword, function, class_, builtin, decorator, string, comment, number, operator

**QSS 样式表**：
- `_LIGHT_QSS` 和 `_DARK_QSS` 各约 400 行
- 覆盖所有 Qt 控件的样式：菜单栏、工具栏、标签页、按钮、输入框、树形控件、滚动条、分隔器、状态栏等
- `apply_theme(app, name)` — 根据 `QSettings` 持久化主题偏好
- 侧边栏样式：`#sidebar_panel`（背景色）、`#sidebar_title`（标题栏）、`#sidebar_separator`（分隔线）
- 活动栏样式：`#activity_bar_container`、`#activity_bar`、`#activity_btn`（含选中蓝色左边框）
- 文件树工具栏样式：`#file_tree_toolbar`、`#file_tree_btn`

### 4.10 `ide/terminal.py` — IPython 终端 (81 行)

底部面板中的"IPython"标签页，嵌入 Jupyter 交互内核。

- 使用 `qtconsole` 的 `RichJupyterWidget` + `QtInProcessKernelManager`
- 内核启动时自动预导入 `numpy`, `scipy`, `matplotlib.pyplot`
- 支持主题切换（LightBG/Linux 配色）
- `execute_command(code)` — 执行代码片段
- `cleanup()` — 关闭内核和通道

### 4.11 `ide/shell_terminal.py` — Shell 终端 (439 行)

底部面板中的"终端"标签页，提供原生 Shell 体验。

**三个类**：
- `_TermView(QWidget)` — 自绘终端视图，使用 pyte 虚拟终端模拟器
  - 支持：光标闪烁、滚动条、鼠标滚轮、Shift+PageUp/Down、Ctrl 快捷键、Ctrl+Shift+V 粘贴
- `ShellTerminalWidget(QWidget)` — PTY 管理器
  - Windows 下使用 `winpty` 连接 PowerShell（无 Logo/无 Profile）
  - 后台线程读取 PTY 输出，30ms 定时器刷新屏幕
- `TerminalPanel(QWidget)` — 多终端管理器
  - 标签栏 + 堆叠组件，支持新建/关闭终端
  - 至少保留一个终端实例

### 4.12 `runner/executor.py` — 代码执行器 (93 行)

在子进程中异步执行 Python 代码，不阻塞 GUI。

- 将编辑器代码写入临时文件（前缀注入 matplotlib 中文字体配置）
- 使用 `sys.executable` 启动子进程
- `QProcess.SeparateChannels` 分离 stdout/stderr
- 实时通过信号转发输出：`stdout_ready(str)`, `stderr_ready(str)`
- 进程结束信号：`execution_finished(exit_code, exit_status)`
- 支持 `send_input(text)` 向运行中的程序发送 stdin
- 支持 `stop()` 强制终止
- 初始化时清理残留临时文件

### 4.13 `ide/highlighter.py` — 旧版语法高亮器 (71 行)

基于 Pygments + `QSyntaxHighlighter` 的高亮器。**已弃用**——编辑器已迁移到 QScintilla 内置的 `QsciLexerPython`。此文件保留仅为兼容性参考。

### 4.14 `ide/line_number_area.py` — 旧行号栏 (15 行)

为 `QPlainTextEdit` 设计的行号栏组件。**已弃用**——QScintilla 自带行号功能。

### 4.15 `ide/toolbar.py` — 工具栏 (46 行)

定义了运行、停止、撤销、重做、重置、保存按钮。**目前未集成到 MainWindow**（主窗口使用菜单栏代替）。

### 4.16 `content/loader.py` — 内容加载器 (37 行)

扫描 `content/` 目录，解析 `meta.yaml`，提供章节元数据和代码内容。

**meta.yaml 格式**：
```yaml
title: "第1章 Python 基础"
description: "Python 编程语言基础入门"
sections:
  - file: "01_hello.py"
    title: "1.1 Hello World"
  - file: "02_variables.py"
    title: "1.2 变量与数据类型"
```

---

## 五、教材内容详情

共 **7 章 27 节**，每节一个独立可运行的 Python 脚本。

### 第1章 Python 基础 (5 节)

| 节 | 文件 | 内容 |
|----|------|------|
| 1.1 | `01_hello.py` | `print()`, f-string, 基本输出 |
| 1.2 | `02_variables.py` | int, float, str, bool, list, 物理常量字典 |
| 1.3 | `03_control_flow.py` | if/elif/else, for, while (放射性衰变), 列表推导 |
| 1.4 | `04_functions.py` | `kinetic_energy()`, `potential_energy()`, 装饰器 |
| 1.5 | `05_file_io.py` | 文件读写, CSV, tempfile |

### 第2章 数值计算 (6 节)

| 节 | 文件 | 内容 |
|----|------|------|
| 2.1 | `01_numpy_basics.py` | 数组创建、切片、运算、矩阵 (inv, det, eig) |
| 2.2 | `02_integration_trap.py` | 梯形法则数值积分, O(h²) 收敛 |
| 2.3 | `03_integration_simpson.py` | 辛普森法则, 与梯形法对比, O(h⁴) 收敛 |
| 2.4 | `04_ode_euler.py` | 欧拉法解 ODE, 放射性衰变和振荡 |
| 2.5 | `05_ode_runge_kutta.py` | RK4 方法, Lorenz 吸引子, Euler vs RK4 误差 |
| 2.6 | `06_matplotlib.py` | 2×2 子图: 三角函数, exp/log, 柱状图, 散点+回归 |

### 第3章 经典力学 (5 节)

| 节 | 文件 | 内容 |
|----|------|------|
| 3.1 | `01_projectile_motion.py` | 抛体运动, 多角度轨迹, 射程/最大高度 vs 角度 |
| 3.2 | `02_planet_orbit.py` | Velocity Verlet, 万有引力轨道 (圆/椭圆), 能量守恒 |
| 3.3 | `03_harmonic_oscillator.py` | RK4 简谐运动, 位移/速度, 相图, 能量守恒 |
| 3.4 | `04_damped_oscillator.py` | 欠阻尼/临界/过阻尼, 包络线, 相图 |
| 3.5 | `05_double_pendulum.py` | 双摆运动方程, RK4, 混沌 (初值敏感性) |

### 第4章 电磁学 (2 节)

| 节 | 文件 | 内容 |
|----|------|------|
| 4.1 | `01_electric_field.py` | 点电荷电场 (quiver + 等势线), 偶极子 |
| 4.2 | `02_magnetic_field.py` | Biot-Savart 定律, streamplot, 平行导线 |

### 第5章 热力学与统计物理 (3 节)

| 节 | 文件 | 内容 |
|----|------|------|
| 5.1 | `01_random_walk.py` | 一维/二维随机行走, 高斯分布收敛, MSD |
| 5.2 | `02_molecular_dynamics.py` | 2D Lennard-Jones 分子动力学, PBC, Maxwell-Boltzmann |
| 5.3 | `03_heat_equation.py` | 一维热传导方程, 有限差分, CFL 稳定性 |

### 第6章 量子力学 (3 节)

| 节 | 文件 | 内容 |
|----|------|------|
| 6.1 | `01_wave_function.py` | 平面波, 高斯波包演化, 波包叠加 |
| 6.2 | `02_schrodinger.py` | 矩阵法解一维薛定谔方程, 无限深势阱, 谐振子 |
| 6.3 | `03_tunneling.py` | 矩形势垒隧穿, 透射系数, T vs E |

### 第7章 波动与光学 (3 节)

| 节 | 文件 | 内容 |
|----|------|------|
| 7.1 | `01_wave_equation.py` | 一维波动方程, 有限差分, CFL 条件 |
| 7.2 | `02_interference.py` | 双缝干涉, 衍射包络, 二维强度图 |
| 7.3 | `03_diffraction.py` | 单缝衍射, 圆孔衍射 (Airy 斑), 径向强度 |

---

## 六、技术要点

### 6.1 为什么选 QScintilla 而非 QPlainTextEdit

| 特性 | QPlainTextEdit | QScintilla |
|------|---------------|------------|
| 代码折叠 | 需自行实现 | 内置 (BoxedTreeFoldStyle) |
| 自动补全 | 需自行实现 | 内置 (QsciAPIs) |
| 语法着色 | 需 QSyntaxHighlighter | 内置 QsciLexerPython |
| 括号匹配 | 需自行实现 | 内置 (SloppyBraceMatch) |
| 缩进参考线 | 需自行绘制 | 内置 (setIndentationGuides) |
| 行号 | 需自行实现 | 内置 Margin |

### 6.2 代码执行安全

- 使用 QProcess 子进程执行，用户代码崩溃不影响 IDE
- 临时文件注入 matplotlib 中文字体配置，确保图表中文正常显示
- 设置 `PYTHONIOENCODING=utf-8`，统一输出编码
- 清理机制：启动时删除残留的临时文件

### 6.3 双包架构优势

```bash
pip install --upgrade npworks-content    # 仅更新教材内容
pip install --upgrade npworks-ide        # 仅更新 IDE 界面
pip install --upgrade npworks            # 同时更新
```

---

## 七、已完成功能清单

### Phase 1: 基础框架 ✅
- [x] 三包 monorepo 结构 + pyproject.toml
- [x] `app.py` 入口 + QApplication 初始化
- [x] `MainWindow` 三面板布局 (QSplitter)
- [x] QScintilla 代码编辑器 (语法高亮、行号、折叠)
- [x] QProcess 代码执行器 + 输出捕获
- [x] `__main__.py` 支持 `python -m`

### Phase 2: 教材内容系统 ✅
- [x] ContentLoader + meta.yaml 解析
- [x] 章节目录树 (ChapterTree)
- [x] 标签页去重 + 中文标题
- [x] 目录树与标签页双向同步
- [x] 启动时展开第一章
- [x] 重置代码功能
- [x] 另存为功能 + 最近文件

### Phase 3: 教材内容 ✅
- [x] 第1章 Python 基础 (5 个脚本)
- [x] 第2章 数值计算 (6 个脚本)
- [x] 第3章 经典力学 (5 个脚本)
- [x] 第4章 电磁学 (2 个脚本)
- [x] 第5章 热力学 (3 个脚本)
- [x] 第6章 量子力学 (3 个脚本)
- [x] 第7章 波动与光学 (3 个脚本)

### Phase 4: 体验优化 ✅
- [x] 亮色/暗色主题切换 (QSettings 持久化)
- [x] 查找替换面板 (Ctrl+F / Ctrl+H)
- [x] 多标签页编辑器 (可关闭、可拖拽排序)
- [x] 注释/取消注释 (Ctrl+/)
- [x] 智能缩进 (冒号后自动缩进、智能退格)
- [x] 拖放打开 .py 文件
- [x] 缩进参考线
- [x] IPython 终端 (Jupyter 内核, 预导入 numpy/scipy/matplotlib)
- [x] Shell 终端 (PowerShell, 多标签)
- [x] 窗口大小/位置记忆 (QSettings)
- [x] stdin 交互支持

### Phase 5: VS Code 布局迁移 ✅
- [x] ActivityBar 活动栏 (48px 固定左侧, 顶部/底部按钮)
- [x] FileTree 多根文件浏览器 (延迟加载, 中文标题, 右键菜单)
- [x] 纯 QSplitter 布局替代 QDockWidget (活动栏不随侧边栏移动)
- [x] Sidebar1/Sidebar2 折叠展开 (splitter sizes 0 ↔ 260px)
- [x] 侧边栏样式 (#sidebar_panel, #sidebar_title, #sidebar_separator)
- [x] 布局持久化 (h_splitter_sizes, v_splitter_sizes via QSettings)
- [x] 底部面板三标签 (输出/IPython/终端, 懒加载)
- [x] chapter_tree.py 弃用 (教材内容整合到 file_tree.py)

---

## 八、待开发功能（按优先级排序）

### P0: 编辑器与运行增强

| 功能 | 说明 | 涉及文件 |
|------|------|---------|
| 拖放 .py 文件时创建新标签 | 当前拖放到已有标签会替换内容，应新建标签 | `editor.py`, `main_window.py` |
| 选中代码运行 | Shift+F5 运行编辑器中选中的代码片段 | `main_window.py`, `executor.py` |
| 运行超时机制 | QTimer 检测，默认 30s，超时弹出终止确认 | `executor.py`, `main_window.py` |
| 错误行号跳转 | 解析 traceback，输出面板错误行号可点击跳转 | `output_panel.py`, `main_window.py` |
| 修改检测 + 关闭提示 | 关闭已修改标签页时弹出确认对话框 | `main_window.py` |

### P1: 教学功能

| 功能 | 说明 | 涉及文件 |
|------|------|---------|
| 学习进度追踪 | QSettings 记录完成状态，章节树显示图标 | `chapter_tree.py`, `main_window.py` |
| 代码说明面板 | meta.yaml 扩展 explanation 字段，Markdown 渲染 | 新增 `explanation_panel.py` |
| Diff 视图 | 当前代码 vs 原始教材代码对比 | 新增 `diff_view.py` |
| 练习模式 | meta.yaml 新增 exercise 块，TODO 标记 + 答案检查 | 新增 `exercise_panel.py` |

### P2: 界面增强

| 功能 | 说明 | 涉及文件 |
|------|------|---------|
| 输出面板搜索 | Ctrl+F 内嵌搜索栏 | `output_panel.py` |
| 输出面板清屏与历史 | 清屏按钮 + 运行历史回溯 | `output_panel.py` |
| 命令面板 | Ctrl+Shift+P 模糊搜索执行命令 | 新增 `command_palette.py` |
| 右键上下文菜单 | 编辑器/章节树/输出面板各自右键菜单 | `editor.py`, `chapter_tree.py`, `output_panel.py` |
| 欢迎页 | 无文件打开时显示富文本欢迎页 | `main_window.py` |
| 工具栏集成 | 将 toolbar.py 集成到主窗口 | `toolbar.py`, `main_window.py` |

### P3: 扩展与发布

| 功能 | 说明 | 涉及文件 |
|------|------|---------|
| 设置面板 | 字体、Tab 宽度、超时时间等可配置 | 新增 `settings_dialog.py` |
| 导出 HTML/PDF | 代码 + 高亮 + 输出导出 | 新增 `export.py` |
| 在线更新检查 | 启动时检查 content 包新版本 | 新增 `update_checker.py` |
| 清理弃用文件 | 删除 highlighter.py, line_number_area.py, toolbar.py | 项目清理 |
| 修复测试 | test_loader.py/test_executor.py 仍引用旧包名 | `tests/` |
| PyPI 发布 | CI + build + twine upload | GitHub Actions |

---

## 九、已知问题

1. **测试文件过时**：`test_loader.py` 和 `test_executor.py` 仍引用旧包名 `pyphysbook`，需更新为 `npworks`
2. **toolbar.py 未集成**：定义了工具栏但 MainWindow 使用菜单栏，该文件处于弃用状态
3. **highlighter.py / line_number_area.py 已弃用**：迁移到 QScintilla 后不再需要，保留仅为兼容性
4. **chapter_tree.py 已弃用**：被 file_tree.py 替代，主窗口不再使用
5. **仅支持 Windows**：Shell 终端使用 `pywinpty`，非 Windows 平台需适配
6. **IPython 内核预导入较重**：启动时导入 numpy/scipy/matplotlib 可能较慢
7. **大纲视图占位**：sidebar2 目前仅显示"大纲视图（开发中）"
