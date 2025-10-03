## Ultrasonic TTS & Analyzer

A simple PyQt6 desktop app that:
- Converts input text to speech (TTS) and plays it normally
- Plays an ultrasonic-modulated version using amplitude modulation (AM)
- Lets you choose sound type (Voice or Sine) and carrier frequency (16–24 kHz)
- Records audio from the mic and estimates pitch in real time
- Saves audio to WAV

### Requirements
- macOS or Linux (tested on macOS 14+)
- Python 3.10+
- Working system audio input/output

### Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Run
```bash
python main.py
```

### Features
- Voice (TTS): Type a sentence and play it as normal audio
- Sine Tone: Generate and play a reference tone
- Ultrasonic AM: Modulate your selected signal onto a high-frequency carrier
- Adjustable Carrier: 16 kHz to 24 kHz slider
- Record + Analyze: Capture mic input and display estimated fundamental frequency (pitch)
- Save WAV: Export the synthesized normal audio to a WAV file

### Notes on Ultrasonic Audio
- Many speakers, microphones, and audio interfaces roll off strongly above ~20 kHz. Results depend on your hardware.
- Ultrasonic energy may still be partially audible (intermodulation, device artifacts). Start with moderate levels.
- The current implementation uses amplitude modulation (AM) with a cosine carrier. If you need different mapping (e.g., single-sideband, heterodyne shift, or specific non-audible beacon patterns), open an issue or request and we can add it.

### Troubleshooting
- No audio output: Check OS audio permissions and output device selection.
- Recording doesn’t work: Ensure microphone permission is granted for your terminal/IDE.
- TTS voice missing or slow: pyttsx3 uses system TTS; voices and speed depend on OS settings.

### License
MIT
