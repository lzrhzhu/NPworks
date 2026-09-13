import numpy as np
import matplotlib.pyplot as plt

plt.rcParams.update({
    'savefig.dpi': 300, 'figure.figsize': (6.4, 4.0), 'font.size': 11,
    'axes.titlesize': 12, 'axes.labelsize': 11, 'xtick.labelsize': 10,
    'ytick.labelsize': 10, 'legend.fontsize': 10, 'xtick.direction': 'in',
    'ytick.direction': 'in', 'xtick.top': True, 'ytick.right': True,
    'axes.linewidth': 0.8, 'lines.linewidth': 1.5, 'axes.grid': False,
    'axes.unicode_minus': False,
})

L = 4.0
central = np.array([[0.35, 0.55], [3.65, 3.45], [1.8, 2.0]])
fig, ax = plt.subplots(figsize=(5.2, 5.2))
for ix in (-1, 0, 1):
    for iy in (-1, 0, 1):
        shifted = central + L * np.array([ix, iy])
        is_central = ix == 0 and iy == 0
        ax.scatter(shifted[:, 0], shifted[:, 1], s=30 if is_central else 18,
                   color='#0072B2' if is_central else '#A6CEE3',
                   alpha=1.0 if is_central else 0.85)
        ax.add_patch(plt.Rectangle((ix * L, iy * L), L, L, fill=False,
                                   edgecolor='0.75', linewidth=0.8))

ax.plot([0.35, 3.65 - L], [0.55, 3.45 - L], color='#D55E00',
        linestyle='--', linewidth=1.4, label='nearest image displacement')
ax.set_xlim(-L, 2 * L)
ax.set_ylim(-L, 2 * L)
ax.set_aspect('equal')
ax.set_xlabel(r'$x/\sigma$')
ax.set_ylabel(r'$y/\sigma$')
ax.set_title('central cell and eight periodic images')
ax.legend(frameon=False, loc='upper left')
fig.tight_layout()
fig.suptitle('periodic_9cell')
print('Nearest-image separation: {:.3f} sigma'.format(np.linalg.norm(np.array([0.35, 0.55]) - np.array([-0.35, -0.55]))))
plt.show()
