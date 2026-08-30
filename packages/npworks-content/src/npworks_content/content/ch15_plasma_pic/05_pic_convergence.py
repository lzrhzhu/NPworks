"""PIC 收敛性、粒子噪声与网格分辨率诊断。"""
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams.update({
    'savefig.dpi': 300, 'figure.figsize': (6.4, 4.0), 'font.size': 11,
    'axes.titlesize': 12, 'axes.labelsize': 11, 'xtick.labelsize': 10,
    'ytick.labelsize': 10, 'legend.fontsize': 10, 'xtick.direction': 'in',
    'ytick.direction': 'in', 'xtick.top': True, 'ytick.right': True,
    'axes.linewidth': 0.8, 'lines.linewidth': 1.5, 'lines.markersize': 5,
    'axes.grid': False, 'axes.unicode_minus': False,
})

L = 2 * np.pi
v0 = 0.5
n0 = 1.0


def run_two_stream(dt, npp, ng, nsteps=260, seed=7):
    """返回线性区振幅增长率、初始噪声和末段场能。"""
    rng = np.random.default_rng(seed)
    dx = L / ng
    w = n0 * L / (2 * npp)
    x1 = np.linspace(0, L, npp, endpoint=False) + (rng.random(npp) - 0.5) * dx
    x2 = np.linspace(0, L, npp, endpoint=False) + (rng.random(npp) - 0.5) * dx
    x1 += 0.01 * L * np.cos(x1)
    x1 %= L
    x2 %= L
    x = np.concatenate([x1, x2])
    v = np.concatenate([np.full(npp, v0), np.full(npp, -v0)])
    k = 2 * np.pi * np.fft.fftfreq(ng, d=dx)
    k2 = k ** 2
    k2[0] = 1.0

    def deposit(xp):
        rho = np.zeros(ng)
        g = xp / dx
        i = np.floor(g).astype(int) % ng
        f = g - np.floor(g)
        np.add.at(rho, i, w * (1 - f) / dx)
        np.add.at(rho, (i + 1) % ng, w * f / dx)
        return rho

    def field(xp):
        rho = -deposit(xp) + n0
        phi_hat = np.fft.fft(rho) / k2
        phi_hat[0] = 0.0
        return np.fft.ifft(-1j * k * phi_hat).real

    def gather(E, xp):
        g = xp / dx
        i = np.floor(g).astype(int) % ng
        f = g - np.floor(g)
        return E[i] * (1 - f) + E[(i + 1) % ng] * f

    e0 = field(x)
    v += 0.5 * gather(e0, x) * dt
    energies = []
    for _ in range(nsteps):
        e = field(x)
        energies.append(0.5 * np.sum(e * e) * dx)
        v -= gather(e, x) * dt
        x = (x + v * dt) % L
    energies = np.asarray(energies)
    t = dt * np.arange(nsteps)
    fit = (t >= 4.0) & (t <= 10.0) & (energies > 0)
    gamma_energy = np.polyfit(t[fit], np.log(energies[fit]), 1)[0]
    noise = np.sqrt(np.mean(energies[:5]))
    tail = np.mean(energies[-20:])
    return 0.5 * gamma_energy, noise, tail


def initial_noise(npp, ng, seed=19):
    """均匀平衡态的初始场噪声；位置随机而不加入不稳定扰动。"""
    rng = np.random.default_rng(seed)
    dx = L / ng
    w = n0 * L / (2 * npp)
    x = rng.random(2 * npp) * L
    rho = np.zeros(ng)
    g = x / dx
    i = np.floor(g).astype(int) % ng
    f = g - np.floor(g)
    np.add.at(rho, i, w * (1 - f) / dx)
    np.add.at(rho, (i + 1) % ng, w * f / dx)
    rho -= rho.mean()
    k = 2 * np.pi * np.fft.fftfreq(ng, d=dx)
    k2 = k ** 2
    k2[0] = 1.0
    phi_hat = np.fft.fft(-rho) / k2
    phi_hat[0] = 0.0
    e = np.fft.ifft(-1j * k * phi_hat).real
    return np.sqrt(0.5 * np.sum(e * e) * dx)


dt_values = np.array([0.05, 0.1, 0.2, 0.3])
gamma_dt = np.array([run_two_stream(dt, 5000, 128)[0] for dt in dt_values])
npp_values = np.array([1000, 2500, 5000, 10000, 20000])
noise_npp = np.array([initial_noise(npp, 128) for npp in npp_values])
ng_values = np.array([32, 64, 128, 256])
tail_ng = np.array([run_two_stream(0.1, 5000, ng)[2] for ng in ng_values])

fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.5))
ax = axes[0]
ax.plot(dt_values, gamma_dt, 'o-', label='PIC')
ax.axhline(gamma_dt[0], color='0.35', linestyle='--', label='小步长参考')
ax.set_xlabel(r'$\Delta t\,(\omega_p^{-1})$')
ax.set_ylabel(r'$\gamma_A\,(\omega_p)$')
ax.set_title('(a) 时间步收敛')
ax.legend(frameon=False)

ax = axes[1]
ax.loglog(npp_values, noise_npp, 'o-', label='PIC noise')
ax.loglog(npp_values, noise_npp[0] * (npp_values[0] / npp_values) ** 0.5,
          '--', label=r'$N_p^{-1/2}$')
ax.set_xlabel(r'$N_p$（每束宏粒子数）')
ax.set_ylabel(r'初始 $W_E^{1/2}$')
ax.set_title('(b) 粒子噪声标度')
ax.legend(frameon=False)

ax = axes[2]
ax.semilogy(ng_values, tail_ng, 's-', label='末段场能')
ax.set_xlabel(r'$N_g$（网格点数）')
ax.set_ylabel(r'$\langle W_E\rangle_{\rm tail}$')
ax.set_title('(c) 网格分辨率')
ax.legend(frameon=False)

fig.suptitle('pic_convergence')
fig.tight_layout()
print('05_pic_convergence.py done')
print('dt scan gamma_A =', np.round(gamma_dt, 4))
print('particle-noise slope expected -0.5')
plt.show()
