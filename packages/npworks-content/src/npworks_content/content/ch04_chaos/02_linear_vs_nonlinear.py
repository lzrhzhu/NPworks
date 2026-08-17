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

g = 9.81
l = 1.0
Omega2 = g / l
dt = 0.001
t_end = 10.0
t = np.arange(0, t_end, dt)
N = len(t)


def simulate(theta0, nonlinear):
    # Euler-Cromer（半隐式欧拉）：先用旧角度更新角速度，再用新角速度更新角度
    theta = np.zeros(N)
    omega = np.zeros(N)
    theta[0] = theta0
    omega[0] = 0.0
    for i in range(N - 1):
        if nonlinear:
            omega[i + 1] = omega[i] - Omega2 * np.sin(theta[i]) * dt
        else:
            omega[i + 1] = omega[i] - Omega2 * theta[i] * dt
        theta[i + 1] = theta[i] + omega[i + 1] * dt
    return theta


fig, axes = plt.subplots(2, 1, figsize=(9, 7), sharex=True)
for ax, theta0 in zip(axes, [0.2, 2.5]):
    th_lin = simulate(theta0, nonlinear=False)
    th_nl = simulate(theta0, nonlinear=True)
    ax.plot(t, th_lin, 'b-', linewidth=1.0,
            label=r'Linear ($\sin\theta \approx \theta$)')
    ax.plot(t, th_nl, 'r--', linewidth=1.0,
            label=r'Nonlinear ($\sin\theta$)')
    ax.set_ylabel(r'$\theta$ (rad)')
    ax.set_title(r'$\theta_0 = {}$ rad'.format(theta0))
    ax.legend()
    ax.grid(True, alpha=0.3)
axes[1].set_xlabel('t (s)')
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "ch04_linear_vs_nonlinear.png"), dpi=130)
plt.close(fig)
print("02_linear_vs_nonlinear.py done")
