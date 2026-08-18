"""PSD of a noisy signal: extract hidden 80 Hz sine from white noise."""
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

fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(t[:500], signal[:500], 'b', label='Clean signal'); ax.set_xlabel('Time (s)'); ax.set_ylabel('Amplitude')
ax.set_title('Clean Signal (80 Hz)'); ax.legend(); ax.grid(True)
plt.tight_layout(); plt.suptitle('fft_clean')
fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(t[:500], noisy_signal[:500], 'r', alpha=0.7, label='Noisy signal'); ax.set_xlabel('Time (s)'); ax.set_ylabel('Amplitude')
ax.set_title('Signal + White Noise'); ax.legend(); ax.grid(True)
plt.tight_layout(); plt.suptitle('fft_noisy')
fig, ax = plt.subplots(figsize=(9, 4))
ax.semilogy(freqs[pos], psd[pos], 'k', linewidth=0.5); ax.set_xlabel('Frequency (Hz)'); ax.set_ylabel('PSD')
ax.set_title('Power Spectral Density (log scale)'); ax.set_xlim(0, 500)
ax.axvline(x=80, color='r', linestyle='--', alpha=0.7, label='80 Hz'); ax.legend(); ax.grid(True)
plt.tight_layout(); plt.suptitle('fft_psd')
print("02_fft_noisy.py done")

plt.show()
