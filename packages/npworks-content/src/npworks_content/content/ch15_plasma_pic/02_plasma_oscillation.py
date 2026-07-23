"""等离子体振荡（Langmuir 振荡）。"""
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


IMG_DIR = _img_dir("ch15")

omega_p = 1.0
x0 = 0.3
T = 4 * 2 * np.pi / omega_p
N = 2000
t = np.linspace(0, T, N)
x = x0 * np.cos(omega_p * t)

dt = T / N
xn, vn = x0, 0.0
x_num = []
for _ in range(N):
    vn += 0.5 * (-omega_p ** 2 * xn) * dt
    xn += vn * dt
    vn += 0.5 * (-omega_p ** 2 * xn) * dt
    x_num.append(xn)
x_num = np.array(x_num)

xs = x - x.mean()
freq = np.fft.rfftfreq(N, d=T / N) * (2 * np.pi)
spec = np.abs(np.fft.rfft(xs))

# --- 图1：集体振荡 ---
fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(t, x, 'b-', linewidth=2, label='解析 $x_0\\cos(\\omega_p t)$')
ax.plot(t, x_num, 'r--', linewidth=1.5, label='数值（Verlet）')
ax.set_xlabel('time $t$'); ax.set_ylabel('位移 $x$')
ax.set_title(r'集体振荡：频率 $\omega_p$')
ax.legend(); ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "ch15_plasma_oscillation.png"), dpi=130)
plt.close(fig)

# --- 图2：FFT 频谱 ---
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(freq, spec, 'g-', linewidth=1.8)
pk = freq[np.argmax(spec)]
ax.axvline(omega_p, color='r', linestyle='--', linewidth=2,
           label=fr'谱峰 $\omega={pk:.2f}\approx\omega_p=1$')
ax.set_xlim(0, 3); ax.set_xlabel(r'角频率 $\omega$'); ax.set_ylabel('振幅谱')
ax.set_title('FFT：单一集体频率 ω_p')
ax.legend(); ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "ch15_plasma_oscillation_fft.png"), dpi=130)
plt.close(fig)

print("02_plasma_oscillation.py done")
