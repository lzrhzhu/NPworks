import numpy as np
import matplotlib.pyplot as plt
import os


def _img_dir(ch):
    d = os.path.dirname(os.path.abspath(__file__))
    for _ in range(10):
        if os.path.isdir(os.path.join(d, "markdown")):
            return os.path.join(d, "markdown", "images", ch)
        d = os.path.dirname(d)
    out = os.path.join(os.path.expanduser("~"), "npworks_figures", ch)
    os.makedirs(out, exist_ok=True)
    return out


IMG_DIR = _img_dir("ch09")


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
    C = np.var(E_arr) / (T ** 2 * N)
    chi = np.var(np.abs(M_arr)) / (T * N)
    return E_avg, m_avg, C, chi


N = 100
T_range = np.linspace(0.5, 5.0, 30)
E_list, m_list, C_list, chi_list = [], [], [], []
for T in T_range:
    E, m, C, chi = ising_1d_mc(N, T, N_therm=3000, N_measure=5000)
    E_list.append(E); m_list.append(m); C_list.append(C); chi_list.append(chi)


def _save(fname, ylabel, vals, color='C0', title=''):
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(T_range, vals, 'o-', color=color, markersize=4)
    ax.set_xlabel(r'$T$')
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(IMG_DIR, fname), dpi=130)
    plt.close(fig)


_save("ch09_1d_ising.png", r'$\langle E \rangle / N$', E_list, title='Energy')
_save("ch09_1d_ising_mag.png", r'$\langle |m| \rangle$', m_list, 'red', 'Magnetization')
_save("ch09_1d_ising_heat.png", r'$C / N$', C_list, 'green', 'Specific Heat')
_save("ch09_1d_ising_chi.png", r'$\chi$', chi_list, 'purple', 'Susceptibility')

print("01_1d_ising.py done")
