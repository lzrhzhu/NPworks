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

N_particles = 36
L = 8.0
dt = 0.005
n_equil = 2000
n_sample = 5000
n_total = n_equil + n_sample
sample_stride = 5
r_cut = L / 2.0
T_target = 0.8

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
f_dof = 2 * N_particles - 2
KE0 = 0.5 * np.sum(vel ** 2)
T_act = 2.0 * KE0 / f_dof
vel *= np.sqrt(T_target / T_act)

pos_unwrapped = pos.copy()


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
trajectory = []

for step in range(n_total):
    pos_prev = pos.copy()
    pos = pos + vel * dt + 0.5 * acc * dt ** 2
    delta = pos - pos_prev
    delta = delta - L * np.round(delta / L)
    pos_unwrapped = pos_unwrapped + delta
    pos = pos - L * np.floor(pos / L)
    acc_new, PE = compute_forces(pos, L, r_cut)
    vel = vel + 0.5 * (acc + acc_new) * dt
    acc = acc_new

    if step == n_equil - 1:
        trajectory.append(pos_unwrapped.copy())
    elif step >= n_equil and (step - n_equil + 1) % sample_stride == 0:
        trajectory.append(pos_unwrapped.copy())

trajectory = np.asarray(trajectory)
frame_dt = sample_stride * dt
max_lag = len(trajectory) - 1
lags = np.arange(max_lag + 1)
times = lags * frame_dt
msd_data = np.zeros(max_lag + 1)
for lag in lags[1:]:
    displacements = trajectory[lag:] - trajectory[:-lag]
    msd_data[lag] = np.mean(np.sum(displacements ** 2, axis=2))

# 只对采样窗口后 40% 的正常扩散区做线性拟合。
fit_start = int(0.60 * max_lag)
fit_mask = lags >= fit_start
slope, intercept = np.polyfit(times[fit_mask], msd_data[fit_mask], 1)
D = slope / (2.0 * 2.0)

# --- 图1：MSD 线性图 ---
fig, ax = plt.subplots()
ax.plot(times, msd_data, color='#0072B2', linestyle='-', label='MSD')
ax.plot(times[fit_mask], slope * times[fit_mask] + intercept,
        color='#D55E00', linestyle='--',
        label='Long-time fit')
ax.set_xlabel(r'$t/\tau$')
ax.set_ylabel(r'$\mathrm{MSD}/\sigma^2$')
ax.legend(frameon=False)
plt.tight_layout()
plt.suptitle('msd')

# --- 图2：MSD 双对数图 ---
fig, ax = plt.subplots()
positive = lags > 0
ax.loglog(times[positive], msd_data[positive], color='#0072B2',
          linestyle='-', label='MSD')

# 参考斜率线只表示标度，垂直位置取自数据。
ballistic_ref = msd_data[1] * (times[positive] / times[1]) ** 2
diffusive_anchor = max(fit_start, 1)
diffusive_ref = (msd_data[diffusive_anchor]
                 * times[positive] / times[diffusive_anchor])
ax.loglog(times[positive], ballistic_ref, color='#009E73', linestyle=':',
          label=r'Slope $2$')
ax.loglog(times[positive], diffusive_ref, color='#D55E00', linestyle='--',
          label=r'Slope $1$')
ax.set_xlabel(r'$t/\tau$')
ax.set_ylabel(r'$\mathrm{MSD}/\sigma^2$')
ax.legend(frameon=False)
plt.tight_layout()
plt.suptitle('msd_loglog')

print('D (2D) = {:.6f}'.format(D))
print('MSD fit window = [{:.3f}, {:.3f}]'.format(
    times[fit_mask][0], times[fit_mask][-1]))
print('MSD(t=0) = {:.6e}'.format(msd_data[0]))
print("03_msd.py done")

plt.show()
