"""统一比较蛙跳、Crank--Nicolson 和 SO-FFT 的自由波包传播。

三种方法使用相同的物理参数、空间网格、时间步长和总传播时间；
计算域足够大，使边界对比较区间内的波包中心影响可忽略。
"""
import time

import numpy as np
import matplotlib.pyplot as plt
from scipy import sparse
from scipy.sparse.linalg import factorized

plt.rcParams.update({
    'savefig.dpi': 300,
    'figure.figsize': (6.4, 4.0),
    'font.size': 11,
    'axes.titlesize': 12,
    'axes.labelsize': 11,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'xtick.direction': 'in',
    'ytick.direction': 'in',
    'xtick.top': True,
    'ytick.right': True,
    'axes.linewidth': 0.8,
    'lines.linewidth': 1.5,
    'axes.grid': False,
    'axes.unicode_minus': False,
})

hbar = m = 1.0
x_min, x_max = -40.0, 40.0
N = 512
x = np.linspace(x_min, x_max, N, endpoint=False)
dx = x[1] - x[0]
dt = 0.01
Nt = 250
x0, sigma, k0 = -10.0, 2.0, 2.0
V = np.zeros(N)

psi0 = np.exp(-(x - x0) ** 2 / (4 * sigma ** 2)) * np.exp(1j * k0 * x)
psi0 /= np.sqrt(np.sum(np.abs(psi0) ** 2) * dx)


def apply_h(f):
    result = np.zeros_like(f)
    result[1:-1] = -0.5 * (f[2:] - 2 * f[1:-1] + f[:-2]) / dx ** 2
    return result


def diagnostics(psi, norms, centers):
    norm = np.sum(np.abs(psi) ** 2) * dx
    center = np.sum(x * np.abs(psi) ** 2) * dx / norm
    norms.append(norm)
    centers.append(center)


def run_leapfrog():
    u, v0 = psi0.real.copy(), psi0.imag.copy()
    v = v0 + 0.5 * dt * apply_h(u)
    norms, centers = [], []
    start = time.perf_counter()
    for _ in range(Nt):
        v_new = v - dt * apply_h(u)
        u_new = u + dt * apply_h(v_new)
        u_new[[0, -1]] = 0
        v_new[[0, -1]] = 0
        v_int = 0.5 * (v + v_new)
        diagnostics(u_new + 1j * v_int, norms, centers)
        u, v = u_new, v_new
    return np.asarray(norms), np.asarray(centers), time.perf_counter() - start


def run_cn():
    inner = slice(1, -1)
    M = N - 2
    alpha = 1j * dt / (4 * dx ** 2)
    A = sparse.diags([-alpha * np.ones(M - 1),
                      (1 + 2 * alpha) * np.ones(M),
                      -alpha * np.ones(M - 1)], [-1, 0, 1], format='csc')
    B = sparse.diags([alpha * np.ones(M - 1),
                      (1 - 2 * alpha) * np.ones(M),
                      alpha * np.ones(M - 1)], [-1, 0, 1], format='csc')
    solve = factorized(A)
    psi = psi0.copy()
    psi[[0, -1]] = 0
    psi_inner = psi[inner].copy()
    norms, centers = [], []
    start = time.perf_counter()
    for _ in range(Nt):
        psi_inner = solve(B @ psi_inner)
        psi[inner] = psi_inner
        diagnostics(psi, norms, centers)
    return np.asarray(norms), np.asarray(centers), time.perf_counter() - start


def run_sofft():
    psi = psi0.copy()
    k = 2 * np.pi * np.fft.fftfreq(N, d=dx)
    phase_t = np.exp(-0.5j * k ** 2 * dt)
    norms, centers = [], []
    start = time.perf_counter()
    for _ in range(Nt):
        psi = np.fft.ifft(phase_t * np.fft.fft(psi))
        diagnostics(psi, norms, centers)
    return np.asarray(norms), np.asarray(centers), time.perf_counter() - start


results = {
    'Leapfrog': run_leapfrog(),
    'Crank--Nicolson': run_cn(),
    'SO-FFT': run_sofft(),
}
t = dt * np.arange(1, Nt + 1)
exact_center = x0 + k0 * t

fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.4))
styles = {'Leapfrog': '-', 'Crank--Nicolson': '--', 'SO-FFT': '-.'}
for name, (norms, centers, elapsed) in results.items():
    axes[0].plot(t, np.abs(norms - 1), ls=styles[name], label=name)
    axes[1].plot(t, np.abs(centers - exact_center), ls=styles[name], label=name)
    print(f'{name}: max norm error={np.max(np.abs(norms - 1)):.2e}, '
          f'max center error={np.max(np.abs(centers - exact_center)):.2e}, '
          f'time={elapsed:.3f} s')
axes[0].set_xlabel('t (a.u.)')
axes[0].set_ylabel(r'$|N(t)-1|$')
axes[0].set_title('(a) Norm error')
axes[1].set_xlabel('t (a.u.)')
axes[1].set_ylabel(r'$|\langle x\rangle-x_{\rm exact}|$ (a.u.)')
axes[1].set_title('(b) Center error')
axes[1].legend(frameon=False)
fig.tight_layout()
fig.suptitle('method_comparison_free_wave_packet')
plt.show()
