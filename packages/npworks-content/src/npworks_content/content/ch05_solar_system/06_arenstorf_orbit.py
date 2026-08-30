import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

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

mu = 0.012277471
mu_prime = 1.0 - mu
period = 17.06521656
state0 = np.array([0.994, 0.0, 0.0, -2.001585106])


def derivative(_, state):
    x, y, vx, vy = state
    r1 = np.sqrt((x + mu) ** 2 + y ** 2)
    r2 = np.sqrt((x - mu_prime) ** 2 + y ** 2)
    ax = x + 2.0 * vy - mu_prime * (x + mu) / r1 ** 3 - mu * (x - mu_prime) / r2 ** 3
    ay = y - 2.0 * vx - mu_prime * y / r1 ** 3 - mu * y / r2 ** 3
    return np.array([vx, vy, ax, ay])


def explicit_euler(steps):
    dt = period / steps
    states = np.empty((steps + 1, 4))
    states[0] = state0
    for i in range(steps):
        states[i + 1] = states[i] + dt * derivative(i * dt, states[i])
    return states


euler_steps = 24000
euler = explicit_euler(euler_steps)
solutions = {
    'RK23': solve_ivp(derivative, (0.0, period), state0, method='RK23',
                      rtol=1e-9, atol=1e-12),
    'DOP853': solve_ivp(derivative, (0.0, period), state0, method='DOP853',
                        rtol=1e-9, atol=1e-12),
}

closure_errors = {
    'Euler': np.linalg.norm(euler[-1, :2] - state0[:2]),
    **{name: np.linalg.norm(sol.y[:2, -1] - state0[:2])
       for name, sol in solutions.items()},
}

fig, axes = plt.subplots(1, 2, figsize=(8.0, 4.0))
ax = axes[0]
ax.plot(euler[:, 0], euler[:, 1], color='#D55E00', linestyle='-', label='Euler')
ax.plot(solutions['RK23'].y[0], solutions['RK23'].y[1],
        color='#009E73', linestyle='-.', label='RK23')
ax.plot(solutions['DOP853'].y[0], solutions['DOP853'].y[1],
        color='#0072B2', linestyle='--', label='DOP853')
ax.plot(state0[0], state0[1], 'ko', label='Initial point')
ax.set_xlim(-1.5, 1.5)
ax.set_ylim(-1.5, 1.5)
ax.set_aspect('equal')
ax.set_xlabel(r'$x^*$')
ax.set_ylabel(r'$y^*$')
ax.set_title('(a) Trajectory')
ax.legend(frameon=False, loc='upper left')

ax = axes[1]
names = list(closure_errors)
values = [closure_errors[name] for name in names]
colors = ['#D55E00', '#009E73', '#0072B2']
ax.bar(names, values, color=colors, width=0.65)
ax.set_yscale('log')
ax.set_ylabel(r'Position closure error $|\Delta \mathbf{r}|$')
ax.set_title('(b) Error after one period')
ax.tick_params(axis='x', top=False)

plt.tight_layout()
plt.suptitle('arenstorf_orbit')

print('Arenstorf diagnostics:')
print(f'  Euler: steps={euler_steps}, closure={closure_errors["Euler"]:.6e}')
for name, sol in solutions.items():
    print(f'  {name}: accepted_steps={len(sol.t) - 1}, nfev={sol.nfev}, '
          f'closure={closure_errors[name]:.6e}')

plt.show()
