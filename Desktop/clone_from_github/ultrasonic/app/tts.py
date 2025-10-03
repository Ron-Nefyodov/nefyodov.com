import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf
import pyttsx3

from .audio_io import DEFAULT_SAMPLE_RATE


def tts_to_array(text: str, sample_rate: int = DEFAULT_SAMPLE_RATE) -> np.ndarray:
    engine = pyttsx3.init()
    with tempfile.TemporaryDirectory() as td:
        out_path = Path(td) / "tts.wav"
        engine.save_to_file(text, str(out_path))
        engine.runAndWait()
        data, sr = sf.read(str(out_path), dtype='float32')
        if data.ndim == 2:
            data = data[:, 0]
        if sr != sample_rate:
            factor = sample_rate / sr
            idx = (np.arange(int(len(data) * factor)) / factor).astype(int)
            idx = np.clip(idx, 0, len(data) - 1)
            data = data[idx]
        return data.astype(np.float32)
