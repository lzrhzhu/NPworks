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


IMG_DIR = _img_dir("ch03")

K = 1.0          # 弹簧常数
a = 1.0          # 晶格常数（单原子）或原胞长度（双原子）

# ---------- (1) 一维单原子链色散关系 ----------
# omega(k) = 2 sqrt(K/m) |sin(k a / 2)|, k in [-pi/a, pi/a]
m = 1.0
k_mono = np.linspace(-np.pi / a, np.pi / a, 400)
omega_mono = 2.0 * np.sqrt(K / m) * np.abs(np.sin(k_mono * a / 2.0))

fig1, ax = plt.subplots(figsize=(8, 5))
ax.plot(k_mono * a / np.pi, omega_mono, 'b-', linewidth=2)
ax.set_xlabel(r'$ka/\pi$')
ax.set_ylabel(r'$\omega(k)$')
ax.set_title('Monatomic Chain: Acoustic Dispersion')
ax.set_xlim(-1, 1)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "ch03_dispersion_monoatomic.png"), dpi=130)
plt.close(fig1)

# ---------- (2) 一维双原子链：声学支与光学支 ----------
# omega^2 = K(1/m1 + 1/m2) +/- K sqrt((1/m1+1/m2)^2 - 4 sin^2(ka/2)/(m1 m2))
m1, m2 = 1.0, 2.0
k_di = np.linspace(0.0, np.pi / a, 400)
s2 = np.sin(k_di * a / 2.0) ** 2
base = K * (1.0 / m1 + 1.0 / m2)
disc = K * np.sqrt((1.0 / m1 + 1.0 / m2) ** 2 - 4.0 * s2 / (m1 * m2))
omega_aco = np.sqrt(np.maximum(base - disc, 0.0))   # 声学支（低频）
omega_opt = np.sqrt(base + disc)                     # 光学支（高频）

fig2, ax = plt.subplots(figsize=(8, 5))
ax.plot(k_di * a / np.pi, omega_aco, 'b-', linewidth=2, label='acoustic branch')
ax.plot(k_di * a / np.pi, omega_opt, 'r-', linewidth=2, label='optical branch')
ax.axhspan(2 * np.sqrt(K / m2), 2 * np.sqrt(K / m1), alpha=0.12, color='gray',
           label='gap')
ax.set_xlabel(r'$ka/\pi$')
ax.set_ylabel(r'$\omega(k)$')
ax.set_title('Diatomic Chain (m2 = 2 m1): Acoustic & Optical Branches')
ax.set_xlim(0, 1)
ax.legend(loc='upper left')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "ch03_dispersion_diatomic.png"), dpi=130)
plt.close(fig2)

print("07_lattice_dispersion.py done")
