import numpy as np
import matplotlib.pyplot as plt

plt.rcParams.update({
    'savefig.dpi': 300, 'figure.figsize': (6.4, 4.0), 'font.size': 11,
    'axes.titlesize': 12, 'axes.labelsize': 11, 'xtick.labelsize': 10,
    'ytick.labelsize': 10, 'legend.fontsize': 10, 'xtick.direction': 'in',
    'ytick.direction': 'in', 'xtick.top': True, 'ytick.right': True,
    'axes.linewidth': 0.8, 'lines.linewidth': 1.5, 'axes.grid': False,
    'axes.unicode_minus': False,
})

dt, nsteps = 0.002, 2500
r = np.array([[-0.85, 0.0], [0.85, 0.0]], dtype=float)
v = np.array([[0.0, 0.28], [0.0, -0.28]], dtype=float)


def force_energy(r):
    dr = r[0] - r[1]
    r2 = np.dot(dr, dr)
    inv2 = 1.0 / r2
    inv6 = inv2 ** 3
    inv12 = inv6 ** 2
    fij = 24.0 * (2.0 * inv12 - inv6) * inv2 * dr
    return np.array([fij, -fij]), 4.0 * (inv12 - inv6)


force, potential = force_energy(r)
distance, kinetic, potential_history, total = [], [], [], []
for _ in range(nsteps):
    r += v * dt + 0.5 * force * dt ** 2
    new_force, potential = force_energy(r)
    v += 0.5 * (force + new_force) * dt
    force = new_force
    distance.append(np.linalg.norm(r[0] - r[1]))
    ke = 0.5 * np.sum(v * v)
    kinetic.append(ke)
    potential_history.append(potential)
    total.append(ke + potential)

time = dt * np.arange(nsteps)
fig, ax = plt.subplots()
ax.plot(time, distance, color='#0072B2')
ax.set_xlabel(r'$t/\tau$')
ax.set_ylabel(r'$r/\sigma$')
ax.set_title('two-particle separation')
fig.tight_layout()
fig.suptitle('two_particle_distance')

fig, ax = plt.subplots()
ax.plot(time, kinetic, label='Kinetic', color='#D55E00')
ax.plot(time, potential_history, label='Potential', color='#0072B2', linestyle='--')
ax.plot(time, total, label='Total', color='black', linestyle='-.')
ax.set_xlabel(r'$t/\tau$')
ax.set_ylabel(r'$E/\epsilon$')
ax.set_title('two-particle energy exchange')
ax.legend(frameon=False)
fig.tight_layout()
fig.suptitle('two_particle_energy')
print('Two-particle relative energy range: {:.3e}'.format(
    (max(total) - min(total)) / abs(np.mean(total))))
plt.show()
