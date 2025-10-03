import queue
import threading
from dataclasses import dataclass
from typing import Optional, Callable

import numpy as np
import sounddevice as sd
import soundfile as sf


DEFAULT_SAMPLE_RATE = 48000


@dataclass
class AudioBuffer:
    samples: np.ndarray
    sample_rate: int


class AudioPlayer:
    def __init__(self, sample_rate: int = DEFAULT_SAMPLE_RATE):
        self.sample_rate = sample_rate
        self._q: queue.Queue[np.ndarray] = queue.Queue()
        self._stream: Optional[sd.OutputStream] = None

    def _callback(self, outdata, frames, time, status):
        if status:
            print(status)
        try:
            data = self._q.get_nowait()
        except queue.Empty:
            outdata.fill(0)
            return
        if len(data) < frames:
            outdata[:len(data), 0] = data
            outdata[len(data):, 0] = 0
        else:
            outdata[:, 0] = data[:frames]

    def start(self):
        if self._stream is None:
            self._stream = sd.OutputStream(
                samplerate=self.sample_rate, channels=1, callback=self._callback
            )
            self._stream.start()

    def stop(self):
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None

    def play(self, samples: np.ndarray):
        self.start()
        self._q.put(samples.astype(np.float32))


class AudioRecorder:
    def __init__(self, sample_rate: int = DEFAULT_SAMPLE_RATE, block_size: int = 2048):
        self.sample_rate = sample_rate
        self.block_size = block_size
        self._q: queue.Queue[np.ndarray] = queue.Queue()
        self._stream: Optional[sd.InputStream] = None
        self._thread: Optional[threading.Thread] = None
        self._running = threading.Event()
        self._on_chunk: Optional[Callable[[np.ndarray], None]] = None

    def _callback(self, indata, frames, time, status):
        if status:
            print(status)
        self._q.put(indata.copy().reshape(-1))

    def start(self, on_chunk: Optional[Callable[[np.ndarray], None]] = None):
        self._on_chunk = on_chunk
        if self._stream is None:
            self._stream = sd.InputStream(
                samplerate=self.sample_rate, channels=1, callback=self._callback,
                blocksize=self.block_size
            )
            self._stream.start()
        self._running.set()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def _loop(self):
        while self._running.is_set():
            try:
                chunk = self._q.get(timeout=0.2)
                if self._on_chunk is not None:
                    self._on_chunk(chunk)
            except queue.Empty:
                pass

    def stop(self):
        self._running.clear()
        if self._thread:
            self._thread.join(timeout=1)
            self._thread = None
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None


def write_wav(path: str, samples: np.ndarray, sample_rate: int = DEFAULT_SAMPLE_RATE):
    sf.write(path, samples.astype(np.float32), sample_rate)


def read_wav(path: str) -> AudioBuffer:
    data, sr = sf.read(path, dtype='float32')
    if data.ndim == 2:
        data = data[:, 0]
    return AudioBuffer(samples=data, sample_rate=sr)
