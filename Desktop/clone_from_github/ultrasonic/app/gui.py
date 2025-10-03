from typing import Optional

import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QSlider,
    QFileDialog,
)

from .audio_io import AudioPlayer, AudioRecorder, DEFAULT_SAMPLE_RATE, write_wav
from .tts import tts_to_array
from .dsp import amplitude_modulate_ultrasonic, sine_tone, normalize_audio, estimate_pitch_hz


class UltrasonicApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ultrasonic TTS & Analyzer")
        self.player = AudioPlayer(sample_rate=DEFAULT_SAMPLE_RATE)
        self.recorder: Optional[AudioRecorder] = None

        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Type your sentence here...")

        self.sound_type = QComboBox()
        self.sound_type.addItems(["Voice (TTS)", "Sine Tone"])

        self.freq_slider = QSlider(Qt.Orientation.Horizontal)
        self.freq_slider.setMinimum(16000)
        self.freq_slider.setMaximum(24000)
        self.freq_slider.setValue(20000)
        self.freq_label = QLabel("Carrier: 20000 Hz")
        self.freq_slider.valueChanged.connect(
            lambda v: self.freq_label.setText(f"Carrier: {v} Hz")
        )

        self.play_normal_btn = QPushButton("Play Normal")
        self.play_ultra_btn = QPushButton("Play Ultrasonic")
        self.save_btn = QPushButton("Save WAV…")
        self.record_btn = QPushButton("Record && Analyze")
        self.pitch_label = QLabel("Pitch: -- Hz")

        self.play_normal_btn.clicked.connect(self.play_normal)
        self.play_ultra_btn.clicked.connect(self.play_ultrasonic)
        self.save_btn.clicked.connect(self.save_wav)
        self.record_btn.clicked.connect(self.record_and_analyze)

        root = QVBoxLayout()
        root.addWidget(QLabel("Input Text:"))
        root.addWidget(self.text_input)

        h1 = QHBoxLayout()
        h1.addWidget(QLabel("Sound Type:"))
        h1.addWidget(self.sound_type)
        root.addLayout(h1)

        root.addWidget(self.freq_label)
        root.addWidget(self.freq_slider)

        h2 = QHBoxLayout()
        h2.addWidget(self.play_normal_btn)
        h2.addWidget(self.play_ultra_btn)
        h2.addWidget(self.save_btn)
        root.addLayout(h2)

        h3 = QHBoxLayout()
        h3.addWidget(self.record_btn)
        h3.addWidget(self.pitch_label)
        root.addLayout(h3)

        self.setLayout(root)

    def _synthesize(self) -> np.ndarray:
        mode = self.sound_type.currentText()
        if mode == "Voice (TTS)":
            text = self.text_input.text().strip() or "Hello"
            samples = tts_to_array(text, DEFAULT_SAMPLE_RATE)
        else:
            samples = sine_tone(freq_hz=440.0, seconds=2.0, sample_rate=DEFAULT_SAMPLE_RATE)
        return normalize_audio(samples)

    def play_normal(self):
        samples = self._synthesize()
        self.player.play(samples)

    def play_ultrasonic(self):
        samples = self._synthesize()
        carrier = self.freq_slider.value()
        mod = amplitude_modulate_ultrasonic(samples, DEFAULT_SAMPLE_RATE, carrier)
        self.player.play(mod)

    def save_wav(self):
        samples = self._synthesize()
        path, _ = QFileDialog.getSaveFileName(self, "Save WAV", "output.wav", "WAV files (*.wav)")
        if path:
            write_wav(path, samples, DEFAULT_SAMPLE_RATE)

    def record_and_analyze(self):
        if self.recorder is not None:
            self.recorder.stop()
            self.recorder = None
            self.record_btn.setText("Record && Analyze")
            return

        self.recorder = AudioRecorder(sample_rate=DEFAULT_SAMPLE_RATE)
        buf: list[np.ndarray] = []

        def on_chunk(chunk: np.ndarray):
            buf.append(chunk)
            # Analyze rolling buffer
            window = int(DEFAULT_SAMPLE_RATE * 0.5)
            flat = np.concatenate(buf)[-window:]
            if flat.size >= window // 2:
                pitch = estimate_pitch_hz(flat, DEFAULT_SAMPLE_RATE)
                self.pitch_label.setText(f"Pitch: {pitch:.1f} Hz")

        self.recorder.start(on_chunk)
        self.record_btn.setText("Stop Recording")


def run_app():
    import sys
    app = QApplication(sys.argv)
    w = UltrasonicApp()
    w.resize(600, 240)
    w.show()
    sys.exit(app.exec())
