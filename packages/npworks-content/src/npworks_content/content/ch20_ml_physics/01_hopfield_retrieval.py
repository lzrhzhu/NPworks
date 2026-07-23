import numpy as np
import matplotlib.pyplot as plt


class HopfieldNetwork:
    def __init__(self, N):
        self.N = N
        self.W = np.zeros((N, N))

    def store_patterns(self, patterns):
        for xi in patterns:
            self.W += np.outer(xi, xi) / self.N
        np.fill_diagonal(self.W, 0)

    def energy(self, sigma):
        return -0.5 * sigma @ self.W @ sigma


np.random.seed(42)
N = 100
net = HopfieldNetwork(N)

patterns = [np.random.choice([-1, 1], size=N) for _ in range(5)]
net.store_patterns(patterns)

test_pattern = patterns[0].copy()
flip_idx = np.random.choice(N, size=30, replace=False)
test_pattern[flip_idx] *= -1

overlap_history = [np.dot(test_pattern, patterns[0]) / N]
energy_history = [net.energy(test_pattern)]
sigma = test_pattern.copy()

for step in range(500):
    i = np.random.randint(N)
    h_eff = net.W[i] @ sigma
    new_sign = np.sign(h_eff) if h_eff != 0 else sigma[i]
    sigma[i] = new_sign
    overlap_history.append(np.dot(sigma, patterns[0]) / N)
    energy_history.append(net.energy(sigma))

import os
_d = os.path.dirname(os.path.abspath(__file__))
for _ in range(10):
    if os.path.isdir(os.path.join(_d, "markdown")):
        IMG_DIR = os.path.join(_d, "markdown", "images", "ch21"); break
    _d = os.path.dirname(_d)
else:
    IMG_DIR = os.path.join(os.path.expanduser("~"), "npworks_figures", "ch21"); os.makedirs(IMG_DIR, exist_ok=True)

for data, title, fname, color in [
    (patterns[0], 'Original pattern', "ch21_ml_physics_hopfield_patterns.png", 'blue'),
    (test_pattern, 'Corrupted (30% flipped)', "ch21_ml_physics_hopfield_patterns_corrupted.png", 'red'),
    (sigma, 'Retrieved (500 steps)', "ch21_ml_physics_hopfield_patterns_retrieved.png", 'green')]:
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.bar(range(N), data, color=color, alpha=0.7)
    ax.set_title(title); ax.set_ylim(-1.5, 1.5); ax.set_xlabel('Neuron index')
    plt.tight_layout(); plt.savefig(os.path.join(IMG_DIR, fname), dpi=130); plt.close(fig)

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(overlap_history); ax.set_xlabel('Update step'); ax.set_ylabel('Overlap with target')
ax.set_title('Retrieval dynamics'); ax.grid(True, alpha=0.3)
plt.tight_layout(); plt.savefig(os.path.join(IMG_DIR, "ch21_ml_physics_hopfield_dynamics.png"), dpi=130); plt.close(fig)

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(energy_history); ax.set_xlabel('Update step'); ax.set_ylabel('Energy')
ax.set_title('Energy evolution'); ax.grid(True, alpha=0.3)
plt.tight_layout(); plt.savefig(os.path.join(IMG_DIR, "ch21_ml_physics_hopfield_dynamics_energy.png"), dpi=130); plt.close(fig)
print("01_hopfield_retrieval.py done")
