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

x = np.linspace(0, 2 * np.pi, 100)

fig, ax = plt.subplots()
ax.plot(x, np.sin(x), 'b-', linewidth=1.8, label=r'$\sin(x)$')
ax.plot(x, np.cos(x), 'r--', linewidth=1.5, label=r'$\cos(x)$')
ax.set_xlabel('x (radians)')
ax.set_ylabel('y')
ax.set_xticks([0, np.pi / 2, np.pi, 3 * np.pi / 2, 2 * np.pi])
ax.set_xticklabels(['0', r'$\pi/2$', r'$\pi$', r'$3\pi/2$', r'$2\pi$'])
ax.set_ylim(-1.2, 1.2)
ax.legend(frameon=False, loc='lower left')
plt.tight_layout()
plt.suptitle('plot_2d')

print("01_plot_2d.py done")

plt.show()
