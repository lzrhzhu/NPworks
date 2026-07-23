import numpy as np
import matplotlib.pyplot as plt


def ising_2d_mc(L, T, N_therm, N_measure, seed=42):
    rng = np.random.default_rng(seed)
    beta = 1.0 / T
    s = np.ones((L, L), dtype=np.int8)
    ii, jj = np.indices((L, L))
    red = ((ii + jj) % 2 == 0)

    def sweep():
        for color in (red, ~red):
            nb = (np.roll(s, 1, 0) + np.roll(s, -1, 0) +
                  np.roll(s, 1, 1) + np.roll(s, -1, 1))
            dE = 2 * s * nb
            r = rng.random((L, L))
            accept = (dE <= 0) | (r < np.exp(-beta * np.maximum(dE, 0)))
            s[color & accept] = -s[color & accept]

    for _ in range(N_therm):
        sweep()
    for _ in range(N_measure):
        sweep()
    return s.copy()


L = 16
T_range = np.linspace(1.5, 3.5, 15)
n_samples_per_T = 15

print("Generating Ising configurations...")
all_configs = []
all_temps = []

for tidx, T in enumerate(T_range):
    for s_idx in range(n_samples_per_T):
        config = ising_2d_mc(L, T, N_therm=500, N_measure=300,
                             seed=42 + tidx * 100 + s_idx)
        all_configs.append(config.flatten().astype(float))
        all_temps.append(T)
    print(f"  T={T:.2f} done ({(tidx+1)}/{len(T_range)})")

X = np.array(all_configs)
T_data = np.array(all_temps)

X_mean = np.mean(X, axis=0)
X_centered = X - X_mean

cov_matrix = X_centered.T @ X_centered / len(X)

eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)
idx = np.argsort(eigenvalues)[::-1]
eigenvalues = eigenvalues[idx]
eigenvectors = eigenvectors[:, idx]

X_pca = X_centered @ eigenvectors[:, :2]

var_explained = eigenvalues[:2] / np.sum(eigenvalues)
print(f"Variance explained: PC1={var_explained[0]:.4f}, PC2={var_explained[1]:.4f}")

import os
_d = os.path.dirname(os.path.abspath(__file__))
for _ in range(10):
    if os.path.isdir(os.path.join(_d, "markdown")):
        IMG_DIR = os.path.join(_d, "markdown", "images", "ch21"); break
    _d = os.path.dirname(_d)
else:
    IMG_DIR = os.path.join(os.path.expanduser("~"), "npworks_figures", "ch21"); os.makedirs(IMG_DIR, exist_ok=True)

fig, ax = plt.subplots(figsize=(8, 6))
scatter = ax.scatter(X_pca[:, 0], X_pca[:, 1], c=T_data, cmap='coolwarm', s=15, alpha=0.7)
plt.colorbar(scatter, ax=ax, label='Temperature $T$')
ax.set_xlabel(f'PC1 ({var_explained[0]*100:.1f}% variance)')
ax.set_ylabel(f'PC2 ({var_explained[1]*100:.1f}% variance)')
ax.set_title('PCA: Ising configurations colored by temperature')
plt.tight_layout(); plt.savefig(os.path.join(IMG_DIR, "ch21_ml_physics_ising_pca.png"), dpi=130); plt.close(fig)

pc1_vs_T = []
for T in T_range:
    mask = np.abs(T_data - T) < 0.05
    if mask.sum() > 0:
        pc1_vs_T.append((T, np.mean(X_pca[mask, 0])))
T_arr, pc1_arr = zip(*pc1_vs_T)
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(T_arr, pc1_arr, 'o-', color='blue', markersize=6)
ax.axvline(2.269, color='red', linestyle='--', label=r'$T_c \approx 2.269$')
ax.set_xlabel('Temperature $T$'); ax.set_ylabel('Mean PC1')
ax.set_title('First principal component vs temperature'); ax.legend(); ax.grid(True, alpha=0.3)
plt.tight_layout(); plt.savefig(os.path.join(IMG_DIR, "ch21_ml_physics_ising_pca_pc1.png"), dpi=130); plt.close(fig)
print("04_ising_pca.py done")
