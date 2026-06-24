import numpy as np
import matplotlib.pyplot as plt


def ising_1d_mc(N, T, N_therm, N_measure, seed=42):
    rng = np.random.default_rng(seed)
    J = 1.0
    beta = 1.0 / T
    s = np.ones(N, dtype=np.int8)

    def total_energy():
        return -J * np.sum(s * np.roll(s, -1))

    for _ in range(N_therm):
        for _ in range(N):
            i = rng.integers(N)
            neighbors = s[(i - 1) % N] + s[(i + 1) % N]
            dE = 2.0 * J * s[i] * neighbors
            if dE <= 0 or rng.random() < np.exp(-beta * dE):
                s[i] = -s[i]

    E_arr = np.zeros(N_measure)
    M_arr = np.zeros(N_measure)
    for k in range(N_measure):
        for _ in range(N):
            i = rng.integers(N)
            neighbors = s[(i - 1) % N] + s[(i + 1) % N]
            dE = 2.0 * J * s[i] * neighbors
            if dE <= 0 or rng.random() < np.exp(-beta * dE):
                s[i] = -s[i]
        E_arr[k] = total_energy()
        M_arr[k] = np.sum(s)

    E_avg = np.mean(E_arr) / N
    m_avg = np.mean(np.abs(M_arr)) / N
    C = np.var(E_arr) / (T**2 * N)
    chi = np.var(np.abs(M_arr)) / (T * N)
    return E_avg, m_avg, C, chi


N = 100
T_range = np.linspace(0.5, 5.0, 30)

E_list, m_list, C_list, chi_list = [], [], [], []
for T in T_range:
    E, m, C, chi = ising_1d_mc(N, T, N_therm=3000, N_measure=5000)
    E_list.append(E)
    m_list.append(m)
    C_list.append(C)
    chi_list.append(chi)

fig, axes = plt.subplots(2, 2, figsize=(10, 8))

axes[0, 0].plot(T_range, E_list, 'o-', markersize=4)
axes[0, 0].set_ylabel(r'$\langle E \rangle / N$')
axes[0, 0].set_title('Energy')

axes[0, 1].plot(T_range, m_list, 'o-', color='red', markersize=4)
axes[0, 1].set_ylabel(r'$\langle |m| \rangle$')
axes[0, 1].set_title('Magnetization')

axes[1, 0].plot(T_range, C_list, 'o-', color='green', markersize=4)
axes[1, 0].set_ylabel(r'$C / N$')
axes[1, 0].set_title('Specific Heat')
axes[1, 0].set_xlabel(r'$T$')

axes[1, 1].plot(T_range, chi_list, 'o-', color='purple', markersize=4)
axes[1, 1].set_ylabel(r'$\chi$')
axes[1, 1].set_title('Susceptibility')
axes[1, 1].set_xlabel(r'$T$')

for ax in axes.flat:
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.suptitle('1d_ising')
plt.show()
