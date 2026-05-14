# NPworks — Numerical Physics Works

计算物理交互式教材，基于 PyQt5 + QScintilla 的桌面 IDE 应用，内置 **7 章 27 节** Python 物理计算示例。

## 安装与启动

```bash
pip install npworks
npworks
```

启动后左侧显示中文章节目录，右侧为多标签页代码编辑器，底部为输出/IPython/终端面板。点击章节加载对应 Python 程序，可直接编辑和运行。

## 核心特性

- **零配置**：`pip install` 一键安装，命令行直接启动
- **内置教材**：7 章 27 节 Python 物理计算示例，打包在安装包中
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
│           └── content/              # 7 章 27 个 .py 脚本
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

共 **7 章 27 节**，每节一个独立可运行的 Python 脚本：

### 第1章 Python 基础 (5 节)

| 节 | 内容 |
|----|------|
| 1.1 Hello World | `print()`, f-string, 基本输出 |
| 1.2 变量与数据类型 | int, float, str, bool, list, 物理常量字典 |
| 1.3 控制流 | if/elif/else, for, while (放射性衰变), 列表推导 |
| 1.4 函数 | `kinetic_energy()`, `potential_energy()`, 装饰器 |
| 1.5 文件读写 | 文件读写, CSV, tempfile |

### 第2章 数值计算 (6 节)

| 节 | 内容 |
|----|------|
| 2.1 NumPy 基础 | 数组创建、切片、运算、矩阵 (inv, det, eig) |
| 2.2 梯形积分 | 梯形法则数值积分, O(h²) 收敛 |
| 2.3 辛普森积分 | 辛普森法则, 与梯形法对比, O(h⁴) 收敛 |
| 2.4 欧拉法 ODE | 欧拉法解 ODE, 放射性衰变和振荡 |
| 2.5 Runge-Kutta | RK4 方法, Lorenz 吸引子, Euler vs RK4 误差 |
| 2.6 Matplotlib | 2×2 子图: 三角函数, exp/log, 柱状图, 散点+回归 |

### 第3章 经典力学 (5 节)

| 节 | 内容 |
|----|------|
| 3.1 抛体运动 | 多角度轨迹, 射程/最大高度 vs 角度 |
| 3.2 行星轨道 | Velocity Verlet, 万有引力轨道, 能量守恒 |
| 3.3 简谐振子 | RK4 简谐运动, 位移/速度, 相图, 能量守恒 |
| 3.4 阻尼振子 | 欠阻尼/临界/过阻尼, 包络线, 相图 |
| 3.5 双摆 | 运动方程, RK4, 混沌 (初值敏感性) |

### 第4章 电磁学 (2 节)

| 节 | 内容 |
|----|------|
| 4.1 电场 | 点电荷电场 (quiver + 等势线), 偶极子 |
| 4.2 磁场 | Biot-Savart 定律, streamplot, 平行导线 |

### 第5章 热力学与统计物理 (3 节)

| 节 | 内容 |
|----|------|
| 5.1 随机行走 | 一维/二维随机行走, 高斯分布收敛, MSD |
| 5.2 分子动力学 | 2D Lennard-Jones, PBC, Maxwell-Boltzmann |
| 5.3 热传导 | 一维热传导方程, 有限差分, CFL 稳定性 |

### 第6章 量子力学 (3 节)

| 节 | 内容 |
|----|------|
| 6.1 波函数 | 平面波, 高斯波包演化, 波包叠加 |
| 6.2 薛定谔方程 | 矩阵法解一维薛定谔方程, 无限深势阱, 谐振子 |
| 6.3 量子隧穿 | 矩形势垒隧穿, 透射系数, T vs E |

### 第7章 波动与光学 (3 节)

| 节 | 内容 |
|----|------|
| 7.1 波动方程 | 一维波动方程, 有限差分, CFL 条件 |
| 7.2 干涉 | 双缝干涉, 衍射包络, 二维强度图 |
| 7.3 衍射 | 单缝衍射, 圆孔衍射 (Airy 斑), 径向强度 |

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
