"""
PSD of a noisy signal: extract hidden 80 Hz sine from white noise.
"""
import numpy as np
import matplotlib.pyplot as plt

N = 4096
dt = 0.001
t = np.arange(N) * dt

signal = 0.5 * np.sin(2 * np.pi * 80 * t)

np.random.seed(42)
noise = np.random.randn(N)
noisy_signal = signal + noise

F = np.fft.fft(noisy_signal)
freqs = np.fft.fftfreq(N, d=dt)
psd = np.abs(F) ** 2 / N

pos = freqs > 0

fig, axes = plt.subplots(3, 1, figsize=(10, 9))

axes[0].plot(t[:500], signal[:500], 'b', label='Clean signal')
axes[0].set_xlabel('Time (s)')
axes[0].set_ylabel('Amplitude')
axes[0].set_title('Clean Signal (80 Hz)')
axes[0].legend()
axes[0].grid(True)

axes[1].plot(t[:500], noisy_signal[:500], 'r', alpha=0.7, label='Noisy signal')
axes[1].set_xlabel('Time (s)')
axes[1].set_ylabel('Amplitude')
axes[1].set_title('Signal + White Noise')
axes[1].legend()
axes[1].grid(True)

axes[2].semilogy(freqs[pos], psd[pos], 'k', linewidth=0.5)
axes[2].set_xlabel('Frequency (Hz)')
axes[2].set_ylabel('PSD')
axes[2].set_title('Power Spectral Density (log scale)')
axes[2].set_xlim(0, 500)
axes[2].axvline(x=80, color='r', linestyle='--', alpha=0.7, label='80 Hz')
axes[2].legend()
axes[2].grid(True)

fig.tight_layout()

plt.suptitle('fft_noisy')
plt.show()
print("02_fft_noisy.py done")
