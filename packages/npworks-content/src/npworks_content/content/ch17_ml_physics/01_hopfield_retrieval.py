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

fig, axes = plt.subplots(1, 3, figsize=(15, 4))

axes[0].bar(range(N), patterns[0], color='blue', alpha=0.7)
axes[0].set_title('Original pattern')
axes[0].set_ylim(-1.5, 1.5)
axes[0].set_xlabel('Neuron index')

axes[1].bar(range(N), test_pattern, color='red', alpha=0.7)
axes[1].set_title('Corrupted (30% flipped)')
axes[1].set_ylim(-1.5, 1.5)
axes[1].set_xlabel('Neuron index')

axes[2].bar(range(N), sigma, color='green', alpha=0.7)
axes[2].set_title('Retrieved (500 steps)')
axes[2].set_ylim(-1.5, 1.5)
axes[2].set_xlabel('Neuron index')

plt.tight_layout()
plt.suptitle('hopfield_patterns')
plt.show()

fig, axes = plt.subplots(1, 2, figsize=(12, 4))

axes[0].plot(overlap_history)
axes[0].set_xlabel('Update step')
axes[0].set_ylabel('Overlap with target')
axes[0].set_title('Retrieval dynamics')
axes[0].grid(True, alpha=0.3)

axes[1].plot(energy_history)
axes[1].set_xlabel('Update step')
axes[1].set_ylabel('Energy')
axes[1].set_title('Energy evolution')
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.suptitle('hopfield_dynamics')
plt.show()
