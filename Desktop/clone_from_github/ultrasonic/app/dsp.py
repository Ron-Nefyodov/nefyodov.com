import numpy as np
from scipy.signal import butter, lfilter


def normalize_audio(samples: np.ndarray, peak: float = 0.9) -> np.ndarray:
    if samples.size == 0:
        return samples
    m = np.max(np.abs(samples))
    if m == 0:
        return samples
    return samples * (peak / m)


def lowpass(signal: np.ndarray, sample_rate: int, cutoff_hz: float, order: int = 6) -> np.ndarray:
    nyq = 0.5 * sample_rate
    norm_cutoff = cutoff_hz / nyq
    b, a = butter(order, norm_cutoff, btype='low', analog=False)
    return lfilter(b, a, signal)


def amplitude_modulate_ultrasonic(baseband: np.ndarray, sample_rate: int, carrier_hz: float) -> np.ndarray:
    baseband = lowpass(baseband, sample_rate, cutoff_hz=min(8000.0, 0.45 * sample_rate))
    t = np.arange(baseband.shape[0]) / sample_rate
    carrier = np.cos(2 * np.pi * carrier_hz * t)
    mod = (1.0 + baseband) * carrier
    mod = normalize_audio(mod, 0.9)
    return mod.astype(np.float32)


def sine_tone(freq_hz: float, seconds: float, sample_rate: int) -> np.ndarray:
    t = np.arange(int(seconds * sample_rate)) / sample_rate
    return np.sin(2 * np.pi * freq_hz * t).astype(np.float32)


def estimate_pitch_hz(samples: np.ndarray, sample_rate: int, min_hz: float = 60.0, max_hz: float = 400.0) -> float:
    if samples.size == 0:
        return 0.0
    samples = samples - np.mean(samples)
    max_lag = int(sample_rate / min_hz)
    min_lag = int(sample_rate / max_hz)
    corr = np.correlate(samples, samples, mode='full')
    corr = corr[corr.size // 2:]
    corr[:min_lag] = 0
    lag = np.argmax(corr[:max_lag])
    if lag <= 0:
        return 0.0
    return float(sample_rate / lag)
