"""Bound states of finite and double wells found with RK4 shooting."""
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import brentq

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


def rk4_shoot(energy, potential, x_max, parity, step=0.002, keep_path=False):
    """Integrate psi'' = 2(V-E)psi from x=0 to x=x_max."""
    n_steps = int(round(x_max / step))
    step = x_max / n_steps
    psi, slope = (1.0, 0.0) if parity == 'even' else (0.0, 1.0)
    if keep_path:
        x_values = np.linspace(0.0, x_max, n_steps + 1)
        psi_values = np.empty(n_steps + 1)
        psi_values[0] = psi

    def rhs(x_value, state):
        return np.array([state[1], 2.0 * (potential(x_value) - energy) * state[0]])

    state = np.array([psi, slope], dtype=float)
    x_value = 0.0
    for index in range(n_steps):
        k1 = rhs(x_value, state)
        k2 = rhs(x_value + 0.5 * step, state + 0.5 * step * k1)
        k3 = rhs(x_value + 0.5 * step, state + 0.5 * step * k2)
        k4 = rhs(x_value + step, state + step * k3)
        state += step * (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0
        x_value += step
        if keep_path:
            psi_values[index + 1] = state[0]

    if keep_path:
        return x_values, psi_values
    return state[0]


def find_levels(potential, x_max, energy_min, energy_max, scan_step, count):
    """Locate even and odd shooting residual zeros, then merge by energy."""
    levels = []
    scan = np.arange(energy_min, energy_max + scan_step, scan_step)
    for parity in ('even', 'odd'):
        previous_energy = scan[0]
        previous_residual = rk4_shoot(previous_energy, potential, x_max, parity)
        for energy in scan[1:]:
            residual = rk4_shoot(energy, potential, x_max, parity)
            if np.isfinite(previous_residual) and np.isfinite(residual) and previous_residual * residual < 0.0:
                root = brentq(
                    lambda trial: rk4_shoot(trial, potential, x_max, parity),
                    previous_energy,
                    energy,
                    xtol=1e-11,
                )
                if not levels or all(abs(root - item[0]) > 1e-7 for item in levels):
                    levels.append((root, parity))
            previous_energy, previous_residual = energy, residual
    return sorted(levels, key=lambda item: item[0])[:count]


finite_depth = 50.0
finite_half_width = 1.0


def finite_well(x_value):
    return -finite_depth if abs(x_value) < finite_half_width else 0.0


barrier_height = 5.0
well_position = 1.5


def double_well(x_value):
    return barrier_height * ((x_value / well_position) ** 2 - 1.0) ** 2


finite_levels = find_levels(finite_well, 3.0, -49.9, -0.001, 0.10, 7)
double_levels = find_levels(double_well, 5.0, 0.0, 7.0, 0.05, 4)

print("Finite-well levels:", [energy for energy, _ in finite_levels])
print("Double-well levels:", [energy for energy, _ in double_levels])
print("Double-well splittings:",
      double_levels[1][0] - double_levels[0][0],
      double_levels[3][0] - double_levels[2][0])

fig, axes = plt.subplots(1, 2, figsize=(9.0, 4.0))
styles = ['-', '--', '-.', ':']

ax = axes[0]
x_potential = np.linspace(-3.0, 3.0, 1201)
ax.plot(x_potential, np.array([finite_well(value) for value in x_potential]),
        color='black', linewidth=1.8, label='V(x)')
for state_index, (energy, parity) in enumerate(finite_levels[:4]):
    x_half, psi_half = rk4_shoot(energy, finite_well, 3.0, parity, keep_path=True)
    sign = 1.0 if parity == 'even' else -1.0
    x_full = np.concatenate((-x_half[:0:-1], x_half))
    psi_full = np.concatenate((sign * psi_half[:0:-1], psi_half))
    psi_full /= np.sqrt(np.trapz(psi_full ** 2, x_full))
    ax.plot(x_full, energy + 2.0 * psi_full, linestyle=styles[state_index],
            label=f'n={state_index}, E={energy:.2f}')
ax.set_xlim(-3.0, 3.0)
ax.set_ylim(-52.0, 2.0)
ax.set_xlabel('x (natural units)')
ax.set_ylabel('E and scaled psi(x) (natural units)')
ax.set_title('Finite Well')
ax.legend(frameon=False, fontsize=7, loc='upper right')
ax.minorticks_on()
ax.text(0.03, 0.94, '(a)', transform=ax.transAxes)

ax = axes[1]
x_potential = np.linspace(-5.0, 5.0, 1601)
ax.plot(x_potential, np.array([double_well(value) for value in x_potential]),
        color='black', linewidth=1.8, label='V(x)')
for state_index, (energy, parity) in enumerate(double_levels):
    # The root is located with x_max=5; plot only the physically localized region
    # so that tiny growing-mode contamination in the far forbidden tail does not
    # dominate the normalization.
    x_half, psi_half = rk4_shoot(energy, double_well, 3.2, parity, keep_path=True)
    sign = 1.0 if parity == 'even' else -1.0
    x_full = np.concatenate((-x_half[:0:-1], x_half))
    psi_full = np.concatenate((sign * psi_half[:0:-1], psi_half))
    psi_full /= np.sqrt(np.trapz(psi_full ** 2, x_full))
    ax.plot(x_full, energy + 1.0 * psi_full, linestyle=styles[state_index],
            label=f'n={state_index}, E={energy:.3f}')
ax.set_xlim(-3.2, 3.2)
ax.set_ylim(-0.5, 9.0)
ax.set_xlabel('x (natural units)')
ax.set_ylabel('E and scaled psi(x) (natural units)')
ax.set_title('Symmetric Double Well')
ax.legend(frameon=False, fontsize=7, loc='upper center', ncol=2)
ax.minorticks_on()
ax.text(0.03, 0.94, '(b)', transform=ax.transAxes)

plt.tight_layout()
plt.suptitle('shooting_bound_states')
plt.show()
