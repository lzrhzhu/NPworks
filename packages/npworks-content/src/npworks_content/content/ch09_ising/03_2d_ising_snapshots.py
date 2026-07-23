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


def equilibrate_checkerboard(L, T, n_sweeps, rng):
    """Vectorized Metropolis with checkerboard (red-black) updates."""
    beta = 1.0 / T
    s = np.ones((L, L), dtype=np.int8)
    ii, jj = np.indices((L, L))
    red = ((ii + jj) % 2 == 0)
    # 预计算接受概率表（dE ∈ {-8,-4,0,4,8}）
    dE_vals = np.array([-8, -4, 0, 4, 8])
    prob = np.exp(-beta * dE_vals)
    prob_map = {int(d): p for d, p in zip(dE_vals, prob)}

    def sweep():
        for color in (red, ~red):
            nb = (np.roll(s, 1, 0) + np.roll(s, -1, 0) +
                  np.roll(s, 1, 1) + np.roll(s, -1, 1))
            dE = 2 * s * nb
            r = rng.random((L, L))
            # dE<=0 接受；dE>0 按 exp(-beta*dE) 接受
            accept = (dE <= 0) | (r < np.exp(-beta * np.maximum(dE, 0)))
            flip = color & accept
            s[flip] = -s[flip]

    for _ in range(n_sweeps):
        sweep()
    return s.copy()


rng = np.random.default_rng(42)
L = 50
temps = [1.0, 2.269, 4.0]
labels = ['T1_ordered', 'Tc_critical', 'T4_disordered']

for T, lab in zip(temps, labels):
    config = equilibrate_checkerboard(L, T, n_sweeps=2000, rng=rng)
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.imshow(config, cmap='binary', vmin=-1, vmax=1, origin='lower')
    ax.set_title(rf'$T = {T}$', fontsize=12)
    ax.set_xlabel('$j$')
    ax.set_ylabel('$i$')
    plt.tight_layout()
    plt.savefig(os.path.join(IMG_DIR, f"ch09_2d_ising_snapshots_{lab}.png"), dpi=130)
    plt.close(fig)

print("03_2d_ising_snapshots.py done")
