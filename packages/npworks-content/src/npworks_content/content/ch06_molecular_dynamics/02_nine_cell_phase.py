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

# 二维中心盒及周围八个周期镜像：所有力都由显式九格子计算。
N = 16
L = 4.8
dt = 0.003
rc = 2.2
n_equil = 500
n_sample = 700
sample_stride = 5
temperatures = (0.10, 1.50)
shifts = np.array([(sx, sy) for sx in (-1, 0, 1) for sy in (-1, 0, 1)], dtype=float)


def force_energy(pos):
    force = np.zeros_like(pos)
    potential = 0.0
    rc2 = rc * rc
    # 对中心盒中的每个粒子，显式检查另外八个盒及中心盒粒子。
    for i in range(N):
        for j in range(N):
            if i == j:
                continue
            for shift in shifts:
                dr = pos[i] - (pos[j] + L * shift)
                r2 = np.dot(dr, dr)
                if r2 < rc2:
                    inv2 = 1.0 / r2
                    inv6 = inv2 ** 3
                    inv12 = inv6 ** 2
                    fij = 24.0 * (2.0 * inv12 - inv6) * inv2 * dr
                    force[i] += fij
                    potential += 4.0 * (inv12 - inv6)
    return force, 0.5 * potential


def initial_positions():
    axis = np.linspace(0.0, L, 4, endpoint=False) + L / 8
    return np.array([[x, y] for x in axis for y in axis], dtype=float)


def run(target, seed):
    rng = np.random.default_rng(seed)
    pos = initial_positions()
    vel = rng.normal(0.0, np.sqrt(target), size=(N, 2))
    vel -= vel.mean(axis=0)
    vel *= np.sqrt(target / (np.sum(vel * vel) / (2 * N - 2)))
    unwrapped = pos.copy()
    force, _ = force_energy(pos)
    energies, temperatures, trajectory = [], [], []
    origin = unwrapped.copy()

    for step in range(n_equil + n_sample):
        old_pos = pos.copy()
        pos = (pos + vel * dt + 0.5 * force * dt * dt) % L
        displacement = pos - old_pos
        displacement -= L * np.round(displacement / L)
        unwrapped += displacement
        new_force, potential = force_energy(pos)
        vel += 0.5 * (force + new_force) * dt
        force = new_force

        # 只在平衡化阶段轻微重标定速度；采样阶段保持 NVE。
        if step < n_equil and step % 20 == 0:
            kinetic = 0.5 * np.sum(vel * vel)
            instant_temperature = 2.0 * kinetic / (2 * N - 2)
            vel *= np.sqrt(target / instant_temperature)

        if step >= n_equil and step % sample_stride == 0:
            kinetic = 0.5 * np.sum(vel * vel)
            energies.append((kinetic, potential, kinetic + potential))
            temperatures.append(2.0 * kinetic / (2 * N - 2))
            trajectory.append(unwrapped.copy())

    trajectory = np.asarray(trajectory)
    origin = trajectory[0]
    msd = np.mean(np.sum((trajectory - origin) ** 2, axis=2), axis=1)
    return pos, np.asarray(energies), np.asarray(temperatures), msd


results = [run(temp, 100 + index) for index, temp in enumerate(temperatures)]
time = np.arange(len(results[0][1])) * sample_stride * dt

for target, (pos, _, _, _) in zip(temperatures, results):
    fig, ax = plt.subplots()
    ax.scatter(pos[:, 0], pos[:, 1], s=32, color='#0072B2')
    ax.set_xlim(0, L)
    ax.set_ylim(0, L)
    ax.set_aspect('equal')
    ax.set_xlabel(r'$x/\sigma$')
    ax.set_ylabel(r'$y/\sigma$')
    ax.set_title(r'$T^*={:.2f}$'.format(target))
    fig.tight_layout()
    fig.suptitle('nine_cell_snapshot_T{:.2f}'.format(target))

fig, ax = plt.subplots()
for target, (_, energy, _, _) in zip(temperatures, results):
    ax.plot(time, energy[:, 2] / N, label=r'$T^*={:.2f}$'.format(target))
ax.set_xlabel(r'$t/\tau$')
ax.set_ylabel(r'$E/(N\epsilon)$')
ax.set_title('NVE total energy')
ax.legend(frameon=False)
fig.tight_layout()
fig.suptitle('nine_cell_nve_energy')

fig, ax = plt.subplots()
for target, (_, _, temp, _) in zip(temperatures, results):
    ax.plot(time, temp, label=r'$T^*={:.2f}$'.format(target))
ax.set_xlabel(r'$t/\tau$')
ax.set_ylabel(r'$T^*$')
ax.set_title('NVE instantaneous temperature')
ax.legend(frameon=False)
fig.tight_layout()
fig.suptitle('nine_cell_nve_temperature')

fig, ax = plt.subplots()
for target, (_, _, _, msd) in zip(temperatures, results):
    ax.plot(time, msd, label=r'$T^*={:.2f}$'.format(target))
ax.set_xlabel(r'$t/\tau$')
ax.set_ylabel(r'$\mathrm{MSD}/\sigma^2$')
ax.set_title('Trajectory diagnostic')
ax.legend(frameon=False)
fig.tight_layout()
fig.suptitle('nine_cell_msd')

for target, (_, energy, temp, msd) in zip(temperatures, results):
    print('T*={:.2f}: <E>/N={:.5f}, <T>={:.5f}, final MSD={:.5f}, energy range={:.3e}'.format(
        target, np.mean(energy[:, 2]) / N, np.mean(temp), msd[-1],
        (np.max(energy[:, 2]) - np.min(energy[:, 2])) / N))
plt.show()




