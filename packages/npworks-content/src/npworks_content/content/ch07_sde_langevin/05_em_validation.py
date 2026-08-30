"""Euler–Maruyama 的自由扩散与收敛性验证。"""
import numpy as np
import matplotlib.pyplot as plt


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
    'lines.markersize': 5,
    'axes.grid': False,
    'axes.unicode_minus': False,
})

rng = np.random.default_rng(7)

# --- 实验 1：自由扩散的 MSD ---
D = 1.0
dt = 1.0e-3
n_steps = 1000
n_traj = 10000
t = np.arange(n_steps + 1) * dt
x = np.zeros(n_traj)
msd = np.zeros(n_steps + 1)

for n in range(n_steps):
    x += np.sqrt(2 * D * dt) * rng.standard_normal(n_traj)
    msd[n + 1] = np.mean(x ** 2)

slope, intercept = np.polyfit(t, msd, 1)
D_fit = slope / 2

fig, ax = plt.subplots()
ax.plot(t, msd, '-', label='simulation MSD')
ax.plot(t, 2 * D * t, '--', label=r'theory $2Dt$')
ax.set_xlabel('$t$ (reduced time)')
ax.set_ylabel(r'$\langle [x(t)-x(0)]^2\rangle$ (reduced length$^2$)')
ax.set_title(fr'Free diffusion: $D_{{fit}}={D_fit:.3f}$, $D={D:.1f}$')
ax.legend(frameon=False)
plt.tight_layout()
plt.suptitle('free_diffusion')

# --- 实验 4：加性噪声 OU 方程的强/弱收敛 ---
gamma = 2.0
sigma = np.sqrt(2 * gamma)
x0 = 1.0
T = 1.0
n_paths = 50000
dt_list = 2.0 ** (-np.arange(3, 9))
strong_error = []
weak_error = []

exact_second_moment = (
    x0 ** 2 * np.exp(-2 * gamma * T)
    + sigma ** 2 * (1 - np.exp(-2 * gamma * T)) / (2 * gamma)
)

for h in dt_list:
    n = int(round(T / h))
    decay = np.exp(-gamma * h)
    var_i = (1 - np.exp(-2 * gamma * h)) / (2 * gamma)
    cov_dw_i = (1 - np.exp(-gamma * h)) / gamma
    residual_std = np.sqrt(var_i - cov_dw_i ** 2 / h)

    x_em = np.full(n_paths, x0)
    x_exact = np.full(n_paths, x0)
    for _ in range(n):
        dW = np.sqrt(h) * rng.standard_normal(n_paths)
        z = rng.standard_normal(n_paths)
        ito_integral = (cov_dw_i / h) * dW + residual_std * z
        x_em += -gamma * x_em * h + sigma * dW
        x_exact = decay * x_exact + sigma * ito_integral

    strong_error.append(np.mean(np.abs(x_em - x_exact)))

    a = 1 - gamma * h
    em_mean = a ** n * x0
    em_var = sigma ** 2 * h * (1 - a ** (2 * n)) / (1 - a ** 2)
    weak_error.append(abs(em_mean ** 2 + em_var - exact_second_moment))

strong_error = np.array(strong_error)
weak_error = np.array(weak_error)
strong_order = np.polyfit(np.log(dt_list), np.log(strong_error), 1)[0]
weak_order = np.polyfit(np.log(dt_list), np.log(weak_error), 1)[0]

fig, ax = plt.subplots()
ax.loglog(dt_list, strong_error, 'o-', label=fr'strong error, slope {strong_order:.2f}')
ax.loglog(dt_list, weak_error, 's--', label=fr'weak error, slope {weak_order:.2f}')
ax.set_xlabel(r'$\Delta t$ (reduced time)')
ax.set_ylabel('error')
ax.set_title('Euler–Maruyama convergence for additive noise')
ax.legend(frameon=False)
plt.tight_layout()
plt.suptitle('em_convergence')

print(f'free diffusion: D_fit={D_fit:.4f}, D={D:.4f}')
print(f'EM convergence: strong order={strong_order:.3f}, weak order={weak_order:.3f}')
print('05_em_validation.py done')

plt.show()
