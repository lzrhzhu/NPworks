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

np.random.seed(42)

N_particles = 50
L = 10.0
dt = 0.005
n_equil = 2000
n_sample = 3000
n_total = n_equil + n_sample
r_cut = L / 2.0
T_target = 1.0

n_side = int(np.ceil(np.sqrt(N_particles)))
spacing = L / n_side
pos = np.zeros((N_particles, 2))
idx = 0
for ix in range(n_side):
    for iy in range(n_side):
        if idx < N_particles:
            pos[idx, 0] = (ix + 0.5) * spacing
            pos[idx, 1] = (iy + 0.5) * spacing
            idx += 1

vel = np.random.normal(0, np.sqrt(T_target), (N_particles, 2))
vel -= np.mean(vel, axis=0)
KE0 = 0.5 * np.sum(vel ** 2)
f_dof = 2 * N_particles - 2
T_actual = 2.0 * KE0 / f_dof
vel *= np.sqrt(T_target / T_actual)


def compute_forces(pos, L, r_cut):
    N = pos.shape[0]
    forces = np.zeros_like(pos)
    PE = 0.0
    V_cut = 4.0 * ((1.0 / r_cut) ** 12 - (1.0 / r_cut) ** 6)
    for i in range(N):
        for j in range(i + 1, N):
            rij = pos[i] - pos[j]
            rij = rij - L * np.round(rij / L)
            r2 = np.dot(rij, rij)
            if r2 < r_cut ** 2:
                inv_r2 = 1.0 / r2
                inv_r6 = inv_r2 ** 3
                inv_r12 = inv_r6 ** 2
                fmag = 24.0 * (2.0 * inv_r12 - inv_r6) * inv_r2
                fij = fmag * rij
                forces[i] += fij
                forces[j] -= fij
                PE += 4.0 * (inv_r12 - inv_r6) - V_cut
    return forces, PE


acc, _ = compute_forces(pos, L, r_cut)

sample_KE = []
sample_PE = []
sample_E = []
sample_pos = []
sample_speeds = []

for step in range(n_total):
    pos = pos + vel * dt + 0.5 * acc * dt ** 2
    pos = pos - L * np.floor(pos / L)
    acc_new, PE = compute_forces(pos, L, r_cut)
    vel = vel + 0.5 * (acc + acc_new) * dt
    acc = acc_new

    if step >= n_equil:
        KE = 0.5 * np.sum(vel ** 2)
        sample_KE.append(KE)
        sample_PE.append(PE)
        sample_E.append(KE + PE)
        speeds = np.sqrt(np.sum(vel ** 2, axis=1))
        sample_speeds.extend(speeds.tolist())
        if step % 500 == 0:
            sample_pos.append(pos.copy())

sample_KE = np.array(sample_KE)
sample_PE = np.array(sample_PE)
sample_E = np.array(sample_E)
sample_speeds = np.array(sample_speeds)
ts = np.arange(len(sample_E)) * dt

# --- 图1：粒子快照 ---
fig, ax = plt.subplots(figsize=(5.2, 5.2))
ax.scatter(sample_pos[-1][:, 0], sample_pos[-1][:, 1], s=30,
           color='#0072B2', marker='o')
ax.set_xlim(0, L)
ax.set_ylim(0, L)
ax.set_aspect('equal')
ax.set_xlabel(r'$x/\sigma$')
ax.set_ylabel(r'$y/\sigma$')
plt.tight_layout()
plt.suptitle('2d_md_snapshot')

# --- 图2：能量随时间演化（动能/势能/总能量） ---
fig, ax = plt.subplots()
ax.plot(ts, sample_KE, color='#D55E00', linestyle='-', label='Kinetic')
ax.plot(ts, sample_PE, color='#0072B2', linestyle='--', label='Potential')
ax.plot(ts, sample_E, color='black', linestyle='-.', label='Total')
ax.set_xlabel(r'$t/\tau$')
ax.set_ylabel(r'$E/\epsilon$')
ax.legend(frameon=False)
plt.tight_layout()
plt.suptitle('2d_md_energy')

# --- 图3：速度分布 vs Maxwell-Boltzmann ---
T_avg = 2.0 * np.mean(sample_KE) / f_dof
fig, ax = plt.subplots()
ax.hist(sample_speeds, bins=40, density=True, alpha=0.65,
        color='#56B4E9', edgecolor='black', label='Simulation')
v_range = np.linspace(0, np.max(sample_speeds) * 1.1, 300)
MB_2d = (1.0 / T_avg) * v_range * np.exp(-v_range ** 2 / (2.0 * T_avg))
ax.plot(v_range, MB_2d, color='#D55E00', linestyle='-',
        label='Maxwell-Boltzmann (2D)')
ax.set_xlabel(r'$|v|/\sqrt{\epsilon/m}$')
ax.set_ylabel('Probability density')
ax.legend(frameon=False)
plt.tight_layout()
plt.suptitle('2d_md_speed')

# --- 图4：总能量守恒（放大） ---
fig, ax = plt.subplots()
ax.plot(ts, sample_E, color='black', linestyle='-')
ax.set_xlabel(r'$t/\tau$')
ax.set_ylabel(r'$E/\epsilon$')
plt.tight_layout()
plt.suptitle('2d_md_energy_conservation')

print('Average T = {:.4f}'.format(T_avg))
print('Energy drift = {:.6f}'.format((sample_E[-1] - sample_E[0]) / abs(sample_E[0])))
print('Mean KE = {:.6f}'.format(np.mean(sample_KE)))
print('Mean PE = {:.6f}'.format(np.mean(sample_PE)))
print('Mean total E = {:.6f}'.format(np.mean(sample_E)))
print('Relative energy range = {:.6e}'.format(
    (sample_E.max() - sample_E.min()) / abs(np.mean(sample_E))))
print("02_2d_md.py done")

plt.show()
