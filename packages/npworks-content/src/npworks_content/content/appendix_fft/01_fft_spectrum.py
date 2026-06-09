"""
FFT of a composite signal (3 frequencies).
Shows time domain signal and frequency spectrum.
"""
import numpy as np
import matplotlib.pyplot as plt

N = 1024
dt = 0.001
t = np.arange(N) * dt

f1, f2, f3 = 50, 120, 300
A1, A2, A3 = 1.0, 0.5, 0.3
signal = A1 * np.sin(2 * np.pi * f1 * t) \
       + A2 * np.sin(2 * np.pi * f2 * t) \
       + A3 * np.sin(2 * np.pi * f3 * t)

F = np.fft.fft(signal)
freqs = np.fft.fftfreq(N, d=dt)

pos_mask = freqs > 0
freqs_pos = freqs[pos_mask]
amplitude = 2.0 * np.abs(F[pos_mask]) / N

fig, axes = plt.subplots(2, 1, figsize=(10, 6))

axes[0].plot(t[:200], signal[:200])
axes[0].set_xlabel('Time (s)')
axes[0].set_ylabel('Amplitude')
axes[0].set_title('Composite Signal (50 + 120 + 300 Hz)')
axes[0].grid(True)

axes[1].stem(freqs_pos, amplitude, basefmt=' ')
axes[1].set_xlabel('Frequency (Hz)')
axes[1].set_ylabel('Amplitude')
axes[1].set_title('Frequency Spectrum via FFT')
axes[1].set_xlim(0, 500)
axes[1].grid(True)

fig.tight_layout()

plt.suptitle('fft_spectrum')
plt.show()
print("01_fft_spectrum.py done")
