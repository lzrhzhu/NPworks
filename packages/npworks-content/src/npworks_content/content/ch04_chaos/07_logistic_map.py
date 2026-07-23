import numpy as np
import matplotlib.pyplot as plt
import os


def _img_dir(ch):
    d = os.path.dirname(os.path.abspath(__file__))
    for _ in range(10):
        if os.path.isdir(os.path.join(d, "markdown")):
            return os.path.join(d, "markdown", "images", ch)
        d = os.path.dirname(d)
    out = os.path.join(os.path.expanduser("~"), "npworks_figures", ch)
    os.makedirs(out, exist_ok=True)
    return out


IMG_DIR = _img_dir("ch04")

mu_ts_list = [2.0, 3.1, 3.45, 3.8]
n_iter = 80

# 每个参数一张时间序列图
first = True
for mu in mu_ts_list:
    x = 0.5
    xs = np.zeros(n_iter)
    for i in range(n_iter):
        xs[i] = x
        x = mu * x * (1.0 - x)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(range(n_iter), xs, 'b.-', markersize=3, linewidth=0.5)
    ax.set_xlabel('n'); ax.set_ylabel(r'$x_n$')
    ax.set_title(r'$\mu={}$'.format(mu)); ax.grid(True, alpha=0.3)
    plt.tight_layout()
    fname = "ch04_logistic_map.png" if first else "ch04_logistic_map_mu{}.png".format(mu)
    plt.savefig(os.path.join(IMG_DIR, fname), dpi=130); plt.close(fig)
    first = False

# Feigenbaum 分岔图
mu_values = np.linspace(2.5, 4.0, 1000)
n_relay = 200; n_sample = 100
all_mu = []; all_x = []
for mu in mu_values:
    x = 0.5
    for i in range(n_relay):
        x = mu * x * (1.0 - x)
    for i in range(n_sample):
        x = mu * x * (1.0 - x)
        all_mu.append(mu); all_x.append(x)

fig, ax = plt.subplots(figsize=(8, 5.5))
ax.plot(all_mu, all_x, 'k.', markersize=0.1)
ax.set_xlabel(r'$\mu$'); ax.set_ylabel(r'$x$')
ax.set_title('Feigenbaum Bifurcation Diagram')
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "ch04_logistic_map_feigenbaum.png"), dpi=130); plt.close(fig)
print("07_logistic_map.py done")
