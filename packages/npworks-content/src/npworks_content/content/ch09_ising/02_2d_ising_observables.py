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


def _save(fname, ylabel, vals, color='C0', title=''):
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(T_range, vals, 'o-', color=color, markersize=4)
    ax.axvline(2.269, color='gray', linestyle='--', label=r'$T_c \approx 2.269$')
    ax.set_xlabel(r'$T$')
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(IMG_DIR, fname), dpi=130)
    plt.close(fig)


_save("ch09_2d_ising_observables.png", r'$\langle E \rangle / N$', E_list, title='Energy')
_save("ch09_2d_ising_mag.png", r'$\langle |m| \rangle$', m_list, 'red', 'Magnetization')
_save("ch09_2d_ising_heat.png", r'$C / N$', C_list, 'green', 'Specific Heat')
_save("ch09_2d_ising_chi.png", r'$\chi$', chi_list, 'purple', 'Susceptibility')

print("02_2d_ising_observables.py done")
