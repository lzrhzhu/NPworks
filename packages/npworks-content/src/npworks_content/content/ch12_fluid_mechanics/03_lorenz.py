"""
Lorenz model: from Rayleigh-Benard convection to chaos (Ch. 12).
Integrates the three-variable Lorenz equations with RK4 for several
values of the reduced Rayleigh number r, plots the z(t) time series,
the strange attractor at r=28, and measures the largest Lyapunov
exponent from the divergence of two nearby trajectories.
"""
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

sigma = 10.0
b = 8.0 / 3.0


def lorenz(state, r):
    x, y, z = state
    return np.array([
        sigma * (y - x),
        x * (r - z) - y,
        x * y - b * z,
    ])


def rk4_step(state, dt, r):
    k1 = lorenz(state, r)
    k2 = lorenz(state + 0.5 * dt * k1, r)
    k3 = lorenz(state + 0.5 * dt * k2, r)
    k4 = lorenz(state + dt * k3, r)
    return state + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)


dt = 0.005
t = np.arange(0.0, 50.0, dt)

# --- Figure 1: z(t) time series for r = 5, 10, 28 ---
r_values = [5.0, 10.0, 28.0]
fig, axes = plt.subplots(3, 1, figsize=(6.4, 6.4), sharex=True)
for ax, r in zip(axes, r_values):
    state = np.array([1.0, 1.0, 1.0])
    z_hist = np.zeros(len(t))
    for i in range(len(t)):
        z_hist[i] = state[2]
        state = rk4_step(state, dt, r)
    ax.plot(t, z_hist, linewidth=1.0)
    ax.set_ylabel('Z')
    ax.set_title(f'r = {r:.0f}', loc='right')
axes[-1].set_xlabel('t')
fig.tight_layout()
fig.suptitle('lorenz_timeseries')

# --- Figure 2: strange attractor at r = 28 ---
r = 28.0
state = np.array([1.0, 1.0, 1.0])
traj = np.zeros((len(t), 3))
for i in range(len(t)):
    traj[i] = state
    state = rk4_step(state, dt, r)

fig = plt.figure(figsize=(6.4, 5.2))
ax = fig.add_subplot(projection='3d')
ax.plot(traj[:, 0], traj[:, 1], traj[:, 2], linewidth=0.5)
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title(f'Lorenz attractor (r = {r:.0f})')
for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
    axis.set_tick_params(direction='in')
fig.tight_layout()
fig.suptitle('lorenz_attractor')

# --- Figure 3: largest Lyapunov exponent from two nearby trajectories ---
# warm up first so that both trajectories start on the attractor
state_a = np.array([1.0, 1.0, 1.0])
for _ in range(20000):
    state_a = rk4_step(state_a, dt, r)

d0 = 1e-5
state_b = state_a + np.array([d0, 0.0, 0.0])
ln_d = np.zeros(len(t))
for i in range(len(t)):
    ln_d[i] = np.log(np.linalg.norm(state_a - state_b))
    state_a = rk4_step(state_a, dt, r)
    state_b = rk4_step(state_b, dt, r)

# fit slope in the exponential-growth window (before saturation)
fit_mask = (t >= 1.0) & (t <= 10.0)
fit_coeff = np.polyfit(t[fit_mask], ln_d[fit_mask], 1)
lam_direct = fit_coeff[0]

# cross-check with the renormalization method (as in Ch. 4)
state_a = np.array([1.0, 1.0, 1.0])
for _ in range(20000):
    state_a = rk4_step(state_a, dt, r)
state_b = state_a + np.array([d0, 0.0, 0.0])
s = 0.0
n_renorm, n_blocks = 200, 500  # renormalize every 1 time unit, 500 blocks
for _ in range(n_blocks):
    for _ in range(n_renorm):
        state_a = rk4_step(state_a, dt, r)
        state_b = rk4_step(state_b, dt, r)
    d = np.linalg.norm(state_a - state_b)
    s += np.log(d / d0)
    state_b = state_a + (d0 / d) * (state_b - state_a)
lam_renorm = s / (n_blocks * n_renorm * dt)
print(f"lambda_max (direct fit)         = {lam_direct:.3f}")
print(f"lambda_max (renormalization)    = {lam_renorm:.3f}")

fig, ax = plt.subplots(figsize=(6.4, 4.0))
ax.plot(t, ln_d, linewidth=1.0, label='ln d(t)')
ax.plot(t[fit_mask], np.polyval(fit_coeff, t[fit_mask]),
        '--', linewidth=1.5,
        label=f'fit slope = {lam_direct:.2f}')
ax.set_xlabel('t')
ax.set_ylabel('ln d')
ax.set_title('Divergence of nearby trajectories (r = 28)')
ax.legend(frameon=False)
fig.tight_layout()
fig.suptitle('lorenz_lyapunov')

print("03_lorenz.py done")

plt.show()
