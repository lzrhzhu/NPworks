import numpy as np
import matplotlib.pyplot as plt


def ising_2d_mc_snapshot(L, T, N_therm, N_measure, seed=42):
    rng = np.random.default_rng(seed)
    N = L * L
    beta = 1.0 / T
    s = np.ones((L, L), dtype=np.int8)

    exp_table = {dE: np.exp(-beta * dE) for dE in [-8, -4, 0, 4, 8]}

    for _ in range(N_therm):
        for _ in range(N):
            i, j = int(rng.integers(L)), int(rng.integers(L))
            nb = (int(s[(i-1) % L, j]) + int(s[(i+1) % L, j]) +
                  int(s[i, (j-1) % L]) + int(s[i, (j+1) % L]))
            dE = 2 * int(s[i, j]) * nb
            if dE <= 0 or rng.random() < exp_table[dE]:
                s[i, j] = -s[i, j]

    for _ in range(N_measure):
        for _ in range(N):
            i, j = int(rng.integers(L)), int(rng.integers(L))
            nb = (int(s[(i-1) % L, j]) + int(s[(i+1) % L, j]) +
                  int(s[i, (j-1) % L]) + int(s[i, (j+1) % L]))
            dE = 2 * int(s[i, j]) * nb
            if dE <= 0 or rng.random() < exp_table[dE]:
                s[i, j] = -s[i, j]

    return s.copy()


L = 50
temps = [1.0, 2.269, 4.0]
labels = [r'$T = 1.0$ (Ordered)', r'$T = T_c \approx 2.27$ (Critical)',
          r'$T = 4.0$ (Disordered)']

fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))

for ax, T, label in zip(axes, temps, labels):
    config = ising_2d_mc_snapshot(L, T, N_therm=5000, N_measure=1000, seed=42)
    ax.imshow(config, cmap='binary', vmin=-1, vmax=1, origin='lower')
    ax.set_title(label, fontsize=12)
    ax.set_xlabel('$j$')
    ax.set_ylabel('$i$')

plt.tight_layout()
plt.suptitle('2d_ising_snapshots')
plt.show()
