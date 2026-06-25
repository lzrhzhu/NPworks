# NPworks — Numerical Physics Works

计算物理交互式教材，基于 PyQt5 + QScintilla 的桌面 IDE 应用，内置 **20 章 71 节** Python 物理计算示例。

## 安装与启动

```bash
pip install npworks
npworks
```

启动后左侧显示中文章节目录，右侧为多标签页代码编辑器，底部为输出/IPython/终端面板。点击章节加载对应 Python 程序，可直接编辑和运行。

## 核心特性

- **零配置**：`pip install` 一键安装，命令行直接启动
- **内置教材**：20 章 71 节 Python 物理计算示例，打包在安装包中
- **QScintilla 编辑器**：代码折叠、自动补全、括号匹配、智能缩进、缩进参考线
- **多标签页**：同时打开多个文件/章节，标签页可拖拽排序和关闭
- **双向导航**：目录树与标签页联动，点击目录打开代码，切换标签高亮目录
- **三面板底部区**：输出面板（stdout/stderr）、IPython 终端（Jupyter 内核）、Shell 终端（PowerShell）
- **查找替换**：支持查找/替换/全部替换，大小写敏感开关
- **亮色/暗色主题**：VS Code 风格双主题，偏好自动持久化
- **代码执行**：QProcess 异步执行，不阻塞 GUI，支持 stdin 交互
- **中文支持**：matplotlib 自动配置中文字体

## 项目结构

三包 Monorepo 结构，IDE 与内容松耦合，可独立更新：

```
npworks/
├── packages/
│   ├── npworks/                  # 元包 — 安装后自动引入 IDE 和内容
│   │   └── pyproject.toml
│   ├── npworks-ide/              # IDE 界面包
│   │   └── src/npworks_ide/
│   │       ├── app.py            # 入口: QApplication + 主题 + MainWindow
│   │       ├── ide/
│   │       │   ├── main_window.py    # 主窗口 (950 行)
│   │       │   ├── activity_bar.py   # 活动栏 (48px 固定左侧)
│   │       │   ├── file_tree.py      # 多根文件浏览器
│   │       │   ├── editor.py         # QScintilla 代码编辑器
│   │       │   ├── output_panel.py   # 输出面板
│   │       │   ├── find_replace.py   # 查找替换
│   │       │   ├── theme.py          # 双主题系统 (1007 行 QSS)
│   │       │   ├── terminal.py       # IPython 终端
│   │       │   └── shell_terminal.py # Shell 终端 (PowerShell)
│   │       └── runner/
│   │           └── executor.py       # QProcess 代码执行器
│   └── npworks-content/          # 教材内容包
│       └── src/npworks_content/
│           ├── loader.py             # 内容加载器
│           └── content/              # 20 章 71 个 .py 脚本
└── tests/
```

### 包间依赖

```
npworks
├── npworks-ide
│   ├── PyQt5 >= 5.15
│   ├── QScintilla >= 2.13
│   ├── NumPy, SciPy, Matplotlib
│   ├── qtconsole >= 5.0
│   ├── pywinpty >= 2.0, pyte >= 0.8
│   └── npworks-content
└── npworks-content
    └── PyYAML >= 6.0
```

独立更新示例：

```bash
pip install --upgrade npworks-content    # 仅更新教材内容
pip install --upgrade npworks-ide        # 仅更新 IDE 界面
pip install --upgrade npworks            # 同时更新
```

### 公共接口

IDE 通过以下接口加载 content 包，两者松耦合：

```python
import npworks_content

npworks_content.get_chapters()                              # → list[dict]
npworks_content.get_section_code(chapter_id, filename)     # → str
npworks_content.get_section_path(chapter_id, filename)     # → Path
npworks_content.get_version()                               # → str
```

## IDE 界面布局

VS Code 风格布局，纯 QSplitter 实现（活动栏固定 48px 不随侧边栏开关移动）：

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
│  ├──────────┴───────────────────────────────────┴────────────┤
│  │  [输出] [IPython] [终端]                          [▲] [✕]  │
│  │  >>> 运行中...                                             │
│  │  Hello, Computational Physics!                             │
├──┴───────────────────────────────────────────────────────────┤
│  状态栏:  ● 运行中 | 行 5, 列 12 | UTF-8 | Python 3.10        │
└──────────────────────────────────────────────────────────────┘
```

### 菜单栏

| 菜单 | 功能 |
|------|------|
| 文件 | 新建、打开、打开文件夹、最近文件、关闭文件夹、保存、另存为、退出 |
| 编辑 | 撤销、重做、剪切、复制、粘贴、全选、注释/取消注释、查找、替换 |
| 运行 | 运行(F5)、停止(Shift+F5)、重置代码(Ctrl+R)、运行当前行、新建/关闭终端 |
| 视图 | 文件浏览器、大纲、底部面板(Ctrl+`)、IPython/Shell终端、亮色/暗色主题 |
| 帮助 | 关于 |

## 教材章节

共 **20 章 71 节**，每章一个目录、每节一个独立可运行的 Python 脚本（与《计算物理》教材第 0–20 章一一对应）：

| 章 | 主题 | 代表脚本/方法 |
|----|------|--------------|
| 0 | 绪论 | — |
| 1 | 编程基础与计算思维 | 变量、控制流、函数、NumPy、可视化 |
| 2 | 物体在空气中的运动 | Euler 法、RK4、打靶 |
| 3 | 振动——从单摆到晶格 | 辛积分、简正模、声子 |
| 4 | 非线性动力学与混沌 | Lyapunov 指数、分叉图 |
| 5 | 太阳系的天体运动 | velocity Verlet、辛算法 |
| 6 | 分子动力学 | LJ 势、周期边界、MSD |
| 7 | 随机微分方程与朗之万动力学 | 维纳过程、OU、Arrhenius、Langevin 恒温 |
| 8 | 随机游走与扩散 | 随机数、随机游走、MSD |
| 9 | 相变与 Ising 模型 | Metropolis、Wolff、有限尺度标度 |
| 10 | 静电场 | Jacobi、SOR、电容器 |
| 11 | 热传导 | FTCS、Crank-Nicolson、ADI |
| 12 | 流体力学 | 投影法、MAC 网格、Kármán 涡街 |
| 13 | 电磁波 | FDTD、Yee 网格、PML |
| 14 | 复杂几何中的场问题（有限元） | 弱形式、刚度矩阵组装 |
| 15 | 等离子体物理与粒子模拟 | PIC、德拜屏蔽、双流不稳定性、朗道阻尼 |
| 16 | 定态薛定谔方程 | 矩阵对角化、打靶、Chebyshev 谱 |
| 17 | 含时薛定谔方程 | 蛙跳、CN、分裂算符 FFT |
| 18 | Hartree-Fock 方法 | SCF、Roothaan、DIIS |
| 19 | 密度泛函理论 | KS 方程、LDA、平面波 |
| 20 | 机器学习与物理 | Hopfield、MLP、PINN |

另有附录脚本（FFT 等）。

## 技术要点

### QScintilla vs QPlainTextEdit

本项目选择 QScintilla 以获得开箱即用的专业编辑体验：代码折叠、自动补全、语法着色（`QsciLexerPython`）、括号匹配、缩进参考线、行号，无需自行实现。

### 代码执行安全

- QProcess 子进程执行，用户代码崩溃不影响 IDE
- 临时文件注入 matplotlib 中文字体配置
- 设置 `PYTHONIOENCODING=utf-8` 统一输出编码
- 启动时自动清理残留临时文件

### 内容格式

每章一个目录，包含 `meta.yaml` 和 Python 脚本：

```yaml
title: "第1章 Python 基础"
description: "Python 编程语言基础入门"
sections:
  - file: "01_hello.py"
    title: "1.1 Hello World"
  - file: "02_variables.py"
    title: "1.2 变量与数据类型"
```

## 依赖

| 包 | 用途 |
|----|------|
| PyQt5 >= 5.15 | GUI 框架 |
| QScintilla >= 2.13 | 代码编辑器 |
| NumPy >= 1.20 | 数值计算 |
| SciPy >= 1.7 | 科学计算 |
| Matplotlib >= 3.4 | 绑图 |
| qtconsole >= 5.0 | IPython 终端 |
| Pygments >= 2.0 | 语法高亮（兼容） |
| PyYAML >= 6.0 | 内容元数据 |
| pywinpty >= 2.0 | Shell 终端 (Windows) |
| pyte >= 0.8 | 终端模拟 |

## License

MIT
