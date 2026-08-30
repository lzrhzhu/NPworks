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

betas = [2.0, 2.01, 2.1, 2.5]
dt = 0.002 * np.pi
total_time = 20.0 * np.pi
steps = int(total_time / dt)


def acceleration(position, beta):
    radius = np.linalg.norm(position)
    return -position / radius ** (beta + 1.0)


def simulate(beta):
    position = np.array([1.0, 0.0])
    velocity = np.array([0.0, 0.8])
    accel = acceleration(position, beta)
    trajectory = np.empty((steps + 1, 2))
    trajectory[0] = position
    for i in range(steps):
        position = position + velocity * dt + 0.5 * accel * dt ** 2
        new_accel = acceleration(position, beta)
        velocity = velocity + 0.5 * (accel + new_accel) * dt
        accel = new_accel
        trajectory[i + 1] = position
    return trajectory


trajectories = [simulate(beta) for beta in betas]
fig, axes = plt.subplots(2, 2, figsize=(6.4, 6.4), sharex=True, sharey=True)
labels = ['(a)', '(b)', '(c)', '(d)']
colors = ['#0072B2', '#009E73', '#D55E00', '#CC79A7']

for ax, beta, trajectory, label, color in zip(
        axes.flat, betas, trajectories, labels, colors):
    ax.plot(trajectory[:, 0], trajectory[:, 1], color=color, linestyle='-')
    ax.plot(0.0, 0.0, 'o', color='#E69F00', markersize=7)
    ax.set_aspect('equal')
    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-1.1, 1.1)
    ax.set_title(f'{label} beta = {beta:g}')

for ax in axes[-1, :]:
    ax.set_xlabel(r'$x^*$')
for ax in axes[:, 0]:
    ax.set_ylabel(r'$y^*$')

plt.tight_layout()
plt.suptitle('power_law_orbits')
print('Power-law orbit diagnostics:')
for beta, trajectory in zip(betas, trajectories):
    radii = np.linalg.norm(trajectory, axis=1)
    print(f'  beta={beta:g}: r_min={radii.min():.6f}, r_max={radii.max():.6f}')

plt.show()
