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


def ising_2d_mc(L, T, N_therm, N_measure, seed=42):
    rng = np.random.default_rng(seed)
    N = L * L
    beta = 1.0 / T
    s = np.ones((L, L), dtype=np.int8)
    exp_table = {dE: np.exp(-beta * dE) for dE in [-8, -4, 0, 4, 8]}

    for _ in range(N_therm):
        for _ in range(N):
            i, j = int(rng.integers(L)), int(rng.integers(L))
            nb = (int(s[(i - 1) % L, j]) + int(s[(i + 1) % L, j]) +
                  int(s[i, (j - 1) % L]) + int(s[i, (j + 1) % L]))
            dE = 2 * int(s[i, j]) * nb
            if dE <= 0 or rng.random() < exp_table[dE]:
                s[i, j] = np.int8(-s[i, j])

    E_arr = np.zeros(N_measure)
    M_arr = np.zeros(N_measure)
    for k in range(N_measure):
        for _ in range(N):
            i, j = int(rng.integers(L)), int(rng.integers(L))
            nb = (int(s[(i - 1) % L, j]) + int(s[(i + 1) % L, j]) +
                  int(s[i, (j - 1) % L]) + int(s[i, (j + 1) % L]))
            dE = 2 * int(s[i, j]) * nb
            if dE <= 0 or rng.random() < exp_table[dE]:
                s[i, j] = np.int8(-s[i, j])
        E_arr[k] = -np.sum(s * (np.roll(s, 1, axis=0) + np.roll(s, 1, axis=1)))
        M_arr[k] = np.sum(s)

    E_avg = np.mean(E_arr) / N
    m_avg = np.mean(np.abs(M_arr)) / N
    C = np.var(E_arr) / (T ** 2 * N)
    chi = np.var(M_arr) / (T * N)
    return E_avg, m_avg, C, chi


L = 16
T_range = np.linspace(1.0, 4.0, 20)
E_list, m_list, C_list, chi_list = [], [], [], []
for tidx, T in enumerate(T_range):
    E, m, C, chi = ising_2d_mc(L, T, N_therm=800, N_measure=1500, seed=42 + tidx)
    E_list.append(E); m_list.append(m); C_list.append(C); chi_list.append(chi)
    print(f"  T={T:.2f} done")


def _save(stem, ylabel, vals, color='C0', title=''):
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(T_range, vals, 'o-', color=color, markersize=4)
    ax.axvline(2.269, color='gray', linestyle='--', label=r'$T_c \approx 2.269$')
    ax.set_xlabel(r'$T^* = k_B T/J$')
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend(frameon=False)
    plt.tight_layout()
    plt.suptitle(stem)


_save("2d_ising_observables", r'$\langle E \rangle / N$', E_list, title='Energy')
_save("2d_ising_mag", r'$\langle |m| \rangle$', m_list, 'red', 'Magnetization')
_save("2d_ising_heat", r'$C / N$', C_list, 'green', 'Specific Heat')
_save("2d_ising_chi", r'$\chi$', chi_list, 'purple', 'Susceptibility')

print("02_2d_ising_observables.py done")

plt.show()
