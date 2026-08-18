"""FFT convolution vs direct convolution (convolution theorem)."""
import numpy as np
import matplotlib.pyplot as plt
import time as _time


N = 2 ** 18
np.random.seed(0)
x = np.random.randn(N)
kernel_len = 256
h = np.exp(-np.linspace(-5, 5, kernel_len) ** 2)
h = h / h.sum()

t0 = _time.time()
y_direct = np.convolve(x[:5000], h, mode='same')
t_direct = _time.time() - t0

t0 = _time.time()
conv_len = N + len(h) - 1
fft_len = int(2 ** np.ceil(np.log2(conv_len)))
Y_fft = np.fft.ifft(np.fft.fft(x, n=fft_len) * np.fft.fft(h, n=fft_len)).real
y_fft = Y_fft[:N]
t_fft = _time.time() - t0
print(f"Direct (N=5000): {t_direct:.4f} s ; FFT (N={N}): {t_fft:.4f} s")

fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(x[:500], alpha=0.5, label='Original'); ax.set_xlabel('Sample index'); ax.set_ylabel('Amplitude')
ax.set_title('Original Signal'); ax.legend(); ax.grid(True)
plt.tight_layout(); plt.suptitle('fft_convolution')
fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(y_fft[:500], 'C1', label='After Gaussian smoothing'); ax.set_xlabel('Sample index'); ax.set_ylabel('Amplitude')
ax.set_title('After FFT Convolution with Gaussian Kernel'); ax.legend(); ax.grid(True)
plt.tight_layout(); plt.suptitle('fft_convolution_smoothed')
print("03_fft_convolution.py done")

plt.show()
