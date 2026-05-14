# NPworks — Numerical Physics Works

[![PyPI](https://img.shields.io/pypi/v/npworks.svg)](https://pypi.org/project/npworks/)
[![Python](https://img.shields.io/pypi/pyversions/npworks.svg)](https://pypi.org/project/npworks/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/lzrhzhu/NPworks/blob/main/LICENSE)
[![GitHub](https://img.shields.io/badge/GitHub-lzrhzhu%2FNPworks-blue)](https://github.com/lzrhzhu/NPworks)

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

## 教材章节

共 **7 章 27 节**，每节一个独立可运行的 Python 脚本：

| 章 | 内容 |
|----|------|
| 第1章 Python 基础 | Hello World, 变量与数据类型, 控制流, 函数, 文件读写 |
| 第2章 数值计算 | NumPy 基础, 梯形积分, 辛普森积分, 欧拉法 ODE, Runge-Kutta, Matplotlib |
| 第3章 经典力学 | 抛体运动, 行星轨道, 简谐振子, 阻尼振子, 双摆 |
| 第4章 电磁学 | 电场, 磁场 |
| 第5章 热力学与统计物理 | 随机行走, 分子动力学, 热传导 |
| 第6章 量子力学 | 波函数, 薛定谔方程, 量子隧穿 |
| 第7章 波动与光学 | 波动方程, 干涉, 衍射 |

## 项目结构

三包 Monorepo 结构，IDE 与内容松耦合，可独立更新：

- **npworks** — 元包，安装后自动引入 IDE 和教材内容
- **npworks-ide** — 基于 PyQt5 + QScintilla 的 IDE 界面
- **npworks-content** — 教材内容（7 章 27 个 .py 脚本 + YAML 元数据）

独立更新示例：

```bash
pip install --upgrade npworks-content    # 仅更新教材内容
pip install --upgrade npworks-ide        # 仅更新 IDE 界面
pip install --upgrade npworks            # 同时更新
```

## 依赖

| 包 | 用途 |
|----|------|
| PyQt5 >= 5.15 | GUI 框架 |
| QScintilla >= 2.13 | 代码编辑器 |
| NumPy >= 1.20 | 数值计算 |
| SciPy >= 1.7 | 科学计算 |
| Matplotlib >= 3.4 | 绘图 |
| qtconsole >= 5.0 | IPython 终端 |
| Pygments >= 2.0 | 语法高亮 |
| PyYAML >= 6.0 | 内容元数据 |

## 链接

- **源代码**: <https://github.com/lzrhzhu/NPworks>
- **问题反馈**: <https://github.com/lzrhzhu/NPworks/issues>
- **PyPI**: <https://pypi.org/project/npworks/>

## License

[MIT](https://github.com/lzrhzhu/NPworks/blob/main/LICENSE)
