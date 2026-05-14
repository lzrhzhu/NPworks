# npworks-ide — NPworks IDE 界面

[![PyPI](https://img.shields.io/pypi/v/npworks-ide.svg)](https://pypi.org/project/npworks-ide/)
[![Python](https://img.shields.io/pypi/pyversions/npworks-ide.svg)](https://pypi.org/project/npworks-ide/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/lzrhzhu/NPworks/blob/main/LICENSE)

计算物理交互式教材的 IDE 界面包，基于 PyQt5 + QScintilla，提供 VS Code 风格的桌面编辑器体验。

> 通常无需单独安装此包，请安装元包 `pip install npworks`。

## 功能

- QScintilla 代码编辑器：语法高亮、代码折叠、自动补全、括号匹配、智能缩进
- 多标签页管理：同时打开多个文件，标签页可拖拽排序
- 双主题系统：VS Code 风格亮色/暗色主题
- 三面板底部区：输出面板、IPython 终端 (Jupyter 内核)、Shell 终端
- 查找替换面板
- 文件浏览器 + 教材目录树
- QProcess 异步代码执行，不阻塞 GUI
- Markdown/PDF/图片预览

## 作为独立安装

```bash
pip install npworks-ide
npworks-ide
```

## 依赖

- PyQt5 >= 5.15
- QScintilla >= 2.13
- NumPy >= 1.20, SciPy >= 1.7, Matplotlib >= 3.4
- qtconsole >= 5.0
- pywinpty >= 2.0 (Windows)
- npworks-content >= 0.0.1

## 链接

- **源代码**: <https://github.com/lzrhzhu/NPworks>
- **问题反馈**: <https://github.com/lzrhzhu/NPworks/issues>
- **PyPI**: <https://pypi.org/project/npworks-ide/>

## License

[MIT](https://github.com/lzrhzhu/NPworks/blob/main/LICENSE)
