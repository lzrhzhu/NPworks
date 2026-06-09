"""
FFT convolution vs direct convolution.
Demonstrates the convolution theorem for fast computation.
"""
import numpy as np
import matplotlib.pyplot as plt
import time as _time

N = 2 ** 18
np.random.seed(0)
x = np.random.randn(N)

kernel_len = 256
h = np.exp(-np.linspace(-5, 5, kernel_len) ** 2)
h = h / h.sum()

N_test = 5000
t0 = _time.time()
y_direct = np.convolve(x[:N_test], h, mode='same')
t_direct = _time.time() - t0

t0 = _time.time()
conv_len = N + len(h) - 1
fft_len = int(2 ** np.ceil(np.log2(conv_len)))
X_fft = np.fft.fft(x, n=fft_len)
H_fft = np.fft.fft(h, n=fft_len)
Y_fft = np.fft.ifft(X_fft * H_fft).real
y_fft = Y_fft[:N]
t_fft = _time.time() - t0

fft_verify_len = N_test + len(h) - 1
y_fft_full = np.fft.ifft(
    np.fft.fft(x[:N_test], n=fft_verify_len)
    * np.fft.fft(h, n=fft_verify_len)
).real
start = (len(h) - 1) // 2
y_fft_same = y_fft_full[start:start + N_test]

max_diff = np.max(np.abs(y_direct - y_fft_same))
print(f"Direct convolution (N={N_test}): {t_direct:.4f} s")
print(f"FFT convolution (N={N}): {t_fft:.4f} s")
print(f"Max difference (verification): {max_diff:.2e}")

fig, axes = plt.subplots(2, 1, figsize=(10, 5))

axes[0].plot(x[:500], alpha=0.5, label='Original')
axes[0].set_xlabel('Sample index')
axes[0].set_ylabel('Amplitude')
axes[0].set_title('Original Signal')
axes[0].legend()
axes[0].grid(True)

axes[1].plot(y_fft[:500], 'C1', label='After Gaussian smoothing')
axes[1].set_xlabel('Sample index')
axes[1].set_ylabel('Amplitude')
axes[1].set_title('After FFT Convolution with Gaussian Kernel')
axes[1].legend()
axes[1].grid(True)

fig.tight_layout()

plt.suptitle('fft_convolution')
plt.show()
print("03_fft_convolution.py done")
