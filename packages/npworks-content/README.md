# npworks-content — NPworks 教材内容

[![PyPI](https://img.shields.io/pypi/v/npworks-content.svg)](https://pypi.org/project/npworks-content/)
[![Python](https://img.shields.io/pypi/pyversions/npworks-content.svg)](https://pypi.org/project/npworks-content/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/lzrhzhu/NPworks/blob/main/LICENSE)

计算物理交互式教材的内容包，包含 **7 章 27 节** Python 物理计算示例代码及 YAML 元数据。

> 通常无需单独安装此包，请安装元包 `pip install npworks`。

## 教材章节

| 章 | 节数 | 内容 |
|----|------|------|
| 第1章 Python 基础 | 5 | Hello World, 变量, 控制流, 函数, 文件读写 |
| 第2章 数值计算 | 6 | NumPy, 梯形积分, 辛普森积分, 欧拉法, RK4, Matplotlib |
| 第3章 经典力学 | 5 | 抛体运动, 行星轨道, 简谐振子, 阻尼振子, 双摆 |
| 第4章 电磁学 | 2 | 电场, 磁场 |
| 第5章 热力学与统计物理 | 3 | 随机行走, 分子动力学, 热传导 |
| 第6章 量子力学 | 3 | 波函数, 薛定谔方程, 量子隧穿 |
| 第7章 波动与光学 | 3 | 波动方程, 干涉, 衍射 |

## 独立安装

```bash
pip install npworks-content
```

## 公共接口

```python
import npworks_content

npworks_content.get_chapters()                              # → list[dict]
npworks_content.get_section_code(chapter_id, filename)      # → str
npworks_content.get_section_path(chapter_id, filename)      # → Path
npworks_content.get_version()                                # → str
```

## 内容格式

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

## 链接

- **源代码**: <https://github.com/lzrhzhu/NPworks>
- **问题反馈**: <https://github.com/lzrhzhu/NPworks/issues>
- **PyPI**: <https://pypi.org/project/npworks-content/>

## License

[MIT](https://github.com/lzrhzhu/NPworks/blob/main/LICENSE)
