"""Quantum harmonic oscillator: E_n = (n + 0.5)*hbar*omega."""
import math
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


IMG_DIR = _img_dir("ch16")

hbar = 1.0; m = 1.0; omega = 1.0
x_min, x_max = -8.0, 8.0
N = 500
x = np.linspace(x_min, x_max, N + 1)
dx = x[1] - x[0]
V = 0.5 * m * omega ** 2 * x[1:-1] ** 2
diag_val = 1.0 / dx ** 2 + V
offdiag_val = -0.5 / dx ** 2 * np.ones(N - 2)
H = np.diag(diag_val) + np.diag(offdiag_val, 1) + np.diag(offdiag_val, -1)
eigenvalues, eigenvectors = np.linalg.eigh(H)
n_states = 6
E_num = eigenvalues[:n_states]
E_ana = np.array([(n + 0.5) * hbar * omega for n in range(n_states)])
x_inner = x[1:-1]
colors = plt.cm.tab10(np.linspace(0, 1, n_states))

# --- 图1：波函数 ---
fig, ax = plt.subplots(figsize=(8, 5.5))
x_plot = np.linspace(x_min, x_max, 300)
ax.plot(x_plot, 0.5 * m * omega ** 2 * x_plot ** 2, 'k-', linewidth=2, label="V(x)")
for n in range(n_states):
    psi = eigenvectors[:, n]
    sign = np.sign(psi[np.argmin(np.abs(x_inner - 0.0))])
    psi = sign * psi / np.sqrt(np.trapz(psi ** 2, x_inner))
    ax.plot(x_inner, psi * 2 + E_num[n], color=colors[n], label=f"n={n}, E={E_num[n]:.3f}")
    ax.axhline(E_num[n], color=colors[n], linestyle='--', alpha=0.3)
ax.set_xlim(-6, 6); ax.set_ylim(-0.5, n_states + 1.5)
ax.set_xlabel("x"); ax.set_ylabel("Energy / psi(x)")
ax.set_title("Harmonic Oscillator Wavefunctions"); ax.legend(fontsize=7, loc='upper right'); ax.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "ch16_harmonic_oscillator.png"), dpi=130)
plt.close(fig)

# --- 图2：能级 ---
n_plot = min(15, len(E_num))
ns = np.arange(n_plot)
fig, ax = plt.subplots(figsize=(8, 5.5))
ax.plot(ns, E_num[:n_plot], 'ro', markersize=6, label="Numerical")
ax.plot(ns, E_ana[:n_plot], 'b-', label="Analytical (n+0.5)*hbar*w")
ax.set_xlabel("Quantum number n"); ax.set_ylabel("Energy")
ax.set_title("Energy Levels"); ax.legend(); ax.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "ch16_harmonic_oscillator_levels.png"), dpi=130)
plt.close(fig)

print("02_harmonic_oscillator.py done")
