"""FFT of a composite signal (3 frequencies)."""
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


IMG_DIR = _img_dir("appendix")

N = 1024
dt = 0.001
t = np.arange(N) * dt
f1, f2, f3 = 50, 120, 300
A1, A2, A3 = 1.0, 0.5, 0.3
signal = A1 * np.sin(2 * np.pi * f1 * t) + A2 * np.sin(2 * np.pi * f2 * t) + A3 * np.sin(2 * np.pi * f3 * t)

F = np.fft.fft(signal)
freqs = np.fft.fftfreq(N, d=dt)
pos_mask = freqs > 0
freqs_pos = freqs[pos_mask]
amplitude = 2.0 * np.abs(F[pos_mask]) / N

fig, ax = plt.subplots(figsize=(9, 4.5))
ax.plot(t[:200], signal[:200]); ax.set_xlabel('Time (s)'); ax.set_ylabel('Amplitude')
ax.set_title('Composite Signal (50 + 120 + 300 Hz)'); ax.grid(True)
plt.tight_layout(); plt.savefig(os.path.join(IMG_DIR, "appendix_fft_spectrum.png"), dpi=130); plt.close(fig)

fig, ax = plt.subplots(figsize=(9, 4.5))
ax.stem(freqs_pos, amplitude, basefmt=' '); ax.set_xlabel('Frequency (Hz)'); ax.set_ylabel('Amplitude')
ax.set_title('Frequency Spectrum via FFT'); ax.set_xlim(0, 500); ax.grid(True)
plt.tight_layout(); plt.savefig(os.path.join(IMG_DIR, "appendix_fft_signal.png"), dpi=130); plt.close(fig)
print("01_fft_spectrum.py done")
