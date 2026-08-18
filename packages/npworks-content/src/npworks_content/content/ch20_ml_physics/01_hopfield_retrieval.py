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

for data, title, fname, color in [
    (patterns[0], 'Original pattern', 'ml_physics_hopfield_patterns', 'blue'),
    (test_pattern, 'Corrupted (30% flipped)', 'ml_physics_hopfield_patterns_corrupted', 'red'),
    (sigma, 'Retrieved (500 steps)', 'ml_physics_hopfield_patterns_retrieved', 'green')]:
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.bar(range(N), data, color=color, alpha=0.7)
    ax.set_title(title); ax.set_ylim(-1.5, 1.5); ax.set_xlabel('Neuron index')
    plt.tight_layout(); plt.suptitle(fname)

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(overlap_history); ax.set_xlabel('Update step'); ax.set_ylabel('Overlap with target')
ax.set_title('Retrieval dynamics'); ax.grid(True, alpha=0.3)
plt.tight_layout(); plt.suptitle('ml_physics_hopfield_dynamics')
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(energy_history); ax.set_xlabel('Update step'); ax.set_ylabel('Energy')
ax.set_title('Energy evolution'); ax.grid(True, alpha=0.3)
plt.tight_layout(); plt.suptitle('ml_physics_hopfield_dynamics_energy')
print("01_hopfield_retrieval.py done")

plt.show()
