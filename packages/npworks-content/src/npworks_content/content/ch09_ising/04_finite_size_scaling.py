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

    M_arr = np.zeros(N_measure)
    for k in range(N_measure):
        for _ in range(N):
            i, j = int(rng.integers(L)), int(rng.integers(L))
            nb = (int(s[(i-1) % L, j]) + int(s[(i+1) % L, j]) +
                  int(s[i, (j-1) % L]) + int(s[i, (j+1) % L]))
            dE = 2 * int(s[i, j]) * nb
            if dE <= 0 or rng.random() < exp_table[dE]:
                s[i, j] = np.int8(-s[i, j])
        M_arr[k] = np.sum(s)

    return np.mean(np.abs(M_arr)) / N


L_values = [10, 20, 30]
T_range = np.linspace(1.5, 3.5, 15)

results = {}
for L in L_values:
    print(f"L={L}")
    m_vals = []
    for idx, T in enumerate(T_range):
        m = ising_2d_mc(L, T, N_therm=500, N_measure=1000, seed=42 + idx)
        m_vals.append(m)
    results[L] = np.array(m_vals)

plt.figure(figsize=(8, 5))
colors = ['blue', 'red', 'green']
for L, color in zip(L_values, colors):
    plt.plot(T_range, results[L], 'o-', color=color, markersize=4, label=f'$L = {L}$')
plt.axvline(2.269, color='gray', linestyle='--', label='$T_c$ (exact)')
plt.xlabel(r'$T$')
plt.ylabel(r'$\langle |m| \rangle$')
plt.title('Finite-Size Scaling: Magnetization vs Temperature')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.suptitle('finite_size_scaling')
plt.show()
