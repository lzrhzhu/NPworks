# NPworks — Numerical Physics Works

计算物理交互式教材，基于 PyQt5 的桌面 IDE 应用，内置计算物理教材内容。

## 安装

```bash
pip install npworks
```

## 使用

```bash
npworks
```

启动后左侧显示教材章节目录，右侧为代码编辑器，点击章节加载对应 Python 程序，可直接编辑和运行。

## 项目结构

本项目由三个 PyPI 包组成：

- **npworks** — 元包，安装后自动引入 IDE 和教材内容
- **npworks-ide** — 基于 PyQt5 的 IDE 界面
- **npworks-content** — 教材内容（Python 示例代码 + YAML 元数据）

## 教材章节

1. Python 基础
2. 数值计算（NumPy、积分、ODE）
3. 经典力学（抛体运动、行星轨道、双摆）
4. 电磁学（电场、磁场）
5. 热力学与统计物理（随机行走、分子动力学、热传导）
6. 量子力学（波函数、薛定谔方程、量子隧穿）
7. 波动与光学（波动方程、干涉、衍射）

## 依赖

- PyQt5 >= 5.15
- NumPy >= 1.20
- SciPy >= 1.7
- Matplotlib >= 3.4
- Pygments >= 2.0
- PyYAML >= 6.0

## License

MIT
