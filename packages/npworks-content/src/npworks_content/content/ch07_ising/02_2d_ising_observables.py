import numpy as np
import matplotlib.pyplot as plt


def ising_2d_mc(L, T, N_therm, N_measure, seed=42):
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
                s[i, j] = np.int8(-s[i, j])

    E_arr = np.zeros(N_measure)
    M_arr = np.zeros(N_measure)
    for k in range(N_measure):
        for _ in range(N):
            i, j = int(rng.integers(L)), int(rng.integers(L))
            nb = (int(s[(i-1) % L, j]) + int(s[(i+1) % L, j]) +
                  int(s[i, (j-1) % L]) + int(s[i, (j+1) % L]))
            dE = 2 * int(s[i, j]) * nb
            if dE <= 0 or rng.random() < exp_table[dE]:
                s[i, j] = np.int8(-s[i, j])
        E_arr[k] = -np.sum(s * (np.roll(s, 1, axis=0) + np.roll(s, 1, axis=1)))
        M_arr[k] = np.sum(s)

    E_avg = np.mean(E_arr) / N
    m_avg = np.mean(np.abs(M_arr)) / N
    C = np.var(E_arr) / (T**2 * N)
    chi = np.var(M_arr) / (T * N)
    return E_avg, m_avg, C, chi


L = 16
T_range = np.linspace(1.0, 4.0, 20)

E_list, m_list, C_list, chi_list = [], [], [], []
for tidx, T in enumerate(T_range):
    E, m, C, chi = ising_2d_mc(L, T, N_therm=800, N_measure=1500, seed=42 + tidx)
    E_list.append(E)
    m_list.append(m)
    C_list.append(C)
    chi_list.append(chi)
    print(f"  T={T:.2f} done")

fig, axes = plt.subplots(2, 2, figsize=(10, 8))

axes[0, 0].plot(T_range, E_list, 'o-', markersize=4)
axes[0, 0].axvline(2.269, color='gray', linestyle='--', label=r'$T_c \approx 2.269$')
axes[0, 0].set_ylabel(r'$\langle E \rangle / N$')
axes[0, 0].legend()
axes[0, 0].set_title('Energy')

axes[0, 1].plot(T_range, m_list, 'o-', color='red', markersize=4)
axes[0, 1].axvline(2.269, color='gray', linestyle='--')
axes[0, 1].set_ylabel(r'$\langle |m| \rangle$')
axes[0, 1].set_title('Magnetization')

axes[1, 0].plot(T_range, C_list, 'o-', color='green', markersize=4)
axes[1, 0].axvline(2.269, color='gray', linestyle='--')
axes[1, 0].set_ylabel(r'$C / N$')
axes[1, 0].set_title('Specific Heat')
axes[1, 0].set_xlabel(r'$T$')

axes[1, 1].plot(T_range, chi_list, 'o-', color='purple', markersize=4)
axes[1, 1].axvline(2.269, color='gray', linestyle='--')
axes[1, 1].set_ylabel(r'$\chi$')
axes[1, 1].set_title('Susceptibility')
axes[1, 1].set_xlabel(r'$T$')

for ax in axes.flat:
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.suptitle('2d_ising_observables')
plt.show()
