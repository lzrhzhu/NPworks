import numpy as np
import matplotlib.pyplot as plt

plt.rcParams.update({
    'savefig.dpi': 300,            # 印刷级分辨率
    'figure.figsize': (6.4, 4.0),  # 单图默认宽约 16 cm，成书缩放后字仍可读
    'font.size': 11,
    'axes.titlesize': 12,
    'axes.labelsize': 11,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'xtick.direction': 'in',       # 刻度向内
    'ytick.direction': 'in',
    'xtick.top': True,             # 四周都有刻度
    'ytick.right': True,
    'axes.linewidth': 0.8,
    'lines.linewidth': 1.5,
    'lines.markersize': 5,
    'axes.grid': False,            # 默认无网格线
    'axes.unicode_minus': False,   # 中文字体缺负号字形时不出方块
})

t = np.linspace(0, 10 * np.pi, 500)
x = np.cos(t)
y = np.sin(t)
z = t / 10.0

fig = plt.figure(figsize=(6.4, 4.0))
ax = fig.add_subplot(111, projection='3d')
ax.plot(x, y, z, 'b-', linewidth=1.2)
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z')
ax.set_box_aspect((np.ptp(x), np.ptp(y), np.ptp(z)))
ax.xaxis.set_tick_params(direction='in')
ax.yaxis.set_tick_params(direction='in')
ax.zaxis.set_tick_params(direction='in')
plt.tight_layout()
plt.suptitle('plot_3d')

print("02_plot_3d.py done")

plt.show()
