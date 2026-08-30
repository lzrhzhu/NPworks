import numpy as np
import matplotlib.pyplot as plt

plt.rcParams.update({'savefig.dpi': 300, 'figure.figsize': (6.4, 4.0), 'font.size': 11,
                     'axes.titlesize': 12, 'axes.labelsize': 11, 'xtick.labelsize': 10,
                     'ytick.labelsize': 10, 'xtick.direction': 'in', 'ytick.direction': 'in',
                     'xtick.top': True, 'ytick.right': True, 'axes.grid': False,
                     'axes.unicode_minus': False})

def ising_2d_mc(L, T, N_therm, N_relax, seed):
    rng = np.random.default_rng(seed); beta = 1.0 / T
    s = rng.choice([-1, 1], size=(L, L)).astype(np.int8)
    ii, jj = np.indices((L, L)); red = ((ii + jj) % 2 == 0)
    def sweep():
        for color in (red, ~red):
            nb = np.roll(s, 1, 0) + np.roll(s, -1, 0) + np.roll(s, 1, 1) + np.roll(s, -1, 1)
            dE = 2 * s * nb; r = rng.random((L, L))
            accept = (dE <= 0) | (r < np.exp(-beta * np.maximum(dE, 0)))
            s[color & accept] *= -1
    for _ in range(N_therm + N_relax): sweep()
    if rng.random() < 0.5: s *= -1
    return s

L = 16; Tc = 2.269; T_range = np.linspace(1.5, 3.5, 15); n_samples_per_T = 20
X, T_data = [], []
for tidx, T in enumerate(T_range):
    for sample_idx in range(n_samples_per_T):
        X.append(ising_2d_mc(L, T, 800, 200, 42 + tidx * 1000 + sample_idx).ravel())
        T_data.append(T)
X = np.asarray(X, dtype=float); T_data = np.asarray(T_data)
Xc = X - X.mean(axis=0); cov = Xc.T @ Xc / len(Xc)
eigenvalues, eigenvectors = np.linalg.eigh(cov); order = np.argsort(eigenvalues)[::-1]
eigenvalues, eigenvectors = eigenvalues[order], eigenvectors[:, order]
X_pca = Xc @ eigenvectors[:, :2]; var_explained = eigenvalues[:2] / eigenvalues.sum()
print(f'Variance explained: PC1={var_explained[0]:.4f}, PC2={var_explained[1]:.4f}')

fig, ax = plt.subplots(figsize=(8, 6))
scatter = ax.scatter(X_pca[:, 0], X_pca[:, 1], c=T_data, cmap='viridis', s=15, alpha=0.7)
plt.colorbar(scatter, ax=ax, label='Temperature $T$ (reduced units)')
ax.set_xlabel(f'PC1 ({var_explained[0]*100:.1f}% variance)'); ax.set_ylabel(f'PC2 ({var_explained[1]*100:.1f}% variance)')
ax.set_title('PCA: Ising configurations colored by temperature'); ax.minorticks_on()
plt.tight_layout(); plt.suptitle('ml_physics_ising_pca')

pc1_abs = []
for T in T_range:
    vals = np.abs(X_pca[np.isclose(T_data, T), 0]); pc1_abs.append((T, vals.mean(), vals.std(ddof=1) / np.sqrt(len(vals))))
pc1_abs = np.asarray(pc1_abs)
fig, ax = plt.subplots(figsize=(8, 5))
ax.errorbar(pc1_abs[:, 0], pc1_abs[:, 1], yerr=pc1_abs[:, 2], fmt='o-', capsize=3, label='Mean $|$PC1$|$')
ax.axvline(Tc, color='black', linestyle='--', label=r'$T_c \approx 2.269$')
ax.set_xlabel('Temperature $T$ (reduced units)'); ax.set_ylabel('Mean $|$PC1$|$'); ax.set_title('PCA order-parameter proxy'); ax.legend(frameon=False); ax.minorticks_on()
plt.tight_layout(); plt.suptitle('ml_physics_ising_pca_pc1')
print('04_ising_pca.py done')
plt.show()
