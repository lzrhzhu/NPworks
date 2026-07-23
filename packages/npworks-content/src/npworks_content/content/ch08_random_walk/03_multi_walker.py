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


IMG_DIR = _img_dir("ch08")

np.random.seed(42)
M = 1000
N = 500
l = 1.0

steps = np.random.choice([-l, l], size=(M, N))
x_final = np.sum(steps, axis=1)

rms_sim = np.sqrt(np.mean(x_final ** 2))
rms_theory = l * np.sqrt(N)

# --- 图1：末态位置分布 ---
fig, ax = plt.subplots(figsize=(8, 5))
ax.hist(x_final, bins=50, density=True, edgecolor='black', alpha=0.7, label='Simulation')
sigma = l * np.sqrt(N)
x_range = np.linspace(x_final.min(), x_final.max(), 300)
gaussian = (1.0 / (sigma * np.sqrt(2 * np.pi))) * np.exp(-x_range ** 2 / (2 * sigma ** 2))
ax.plot(x_range, gaussian, 'r-', linewidth=2, label='Gaussian fit')
ax.set_xlabel('Final Position x_N')
ax.set_ylabel('Probability Density')
ax.set_title('Final Position Distribution (M={}, N={})'.format(M, N))
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "ch08_multi_walker.png"), dpi=130)
plt.close(fig)

# --- 图2：RMS vs sqrt(N) ---
n_vals = np.arange(1, N + 1, 10)
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(n_vals, l * np.sqrt(n_vals), 'r-', linewidth=2, label='Theory: sqrt(N)')
ax.axhline(y=rms_sim, color='b', linestyle='--', label='Sim RMS = {:.2f}'.format(rms_sim))
ax.axhline(y=rms_theory, color='r', linestyle=':', alpha=0.5, label='Theory RMS = {:.2f}'.format(rms_theory))
ax.set_xlabel('Step N')
ax.set_ylabel('RMS Position')
ax.set_title('RMS vs sqrt(N)')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "ch08_multi_walker_rms.png"), dpi=130)
plt.close(fig)

print('Sim RMS = {:.4f}, Theory RMS = {:.4f}'.format(rms_sim, rms_theory))
print("03_multi_walker.py done")
