"""Original 120 BPM instrumental and synchronized SFX; no samples or TTS."""

import json
import subprocess
from pathlib import Path

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "public" / "audio"
QA = ROOT / "qa" / "math-short"
SR = 48000
SECONDS = 52
BEAT = .5
RNG = np.random.default_rng(202410)
MIX = np.zeros((SECONDS * SR, 2), np.float64)
ROOM = np.zeros_like(MIX)


def filter_signal(signal, frequency, kind="lowpass"):
    return sosfilt(butter(2, frequency, fs=SR, btype=kind, output="sos"), signal)


def note(midi, seconds, kind="pluck"):
    t = np.arange(int(seconds * SR)) / SR
    hz = 440 * 2 ** ((midi - 69) / 12)
    if kind == "bass":
        signal = np.sin(2 * np.pi * hz * t) + .17 * np.sin(4 * np.pi * hz * t)
        envelope = (1 - np.exp(-t * 160)) * np.exp(-t * 4)
    elif kind == "pad":
        signal = (np.sin(2 * np.pi * hz * t) + .48 * np.sin(2 * np.pi * hz * 1.0025 * t)
                  + .12 * np.sin(2 * np.pi * hz * 2 * t))
        envelope = np.minimum(t / .14, 1) * np.minimum((seconds - t) / .45, 1)
    else:
        signal = (np.sin(2 * np.pi * hz * t + .75 * np.sin(2 * np.pi * hz * 2 * t) * np.exp(-t * 9))
                  + .20 * np.sin(2 * np.pi * hz * 2.001 * t) * np.exp(-t * 11))
        envelope = (1 - np.exp(-t * 550)) * np.exp(-t * 6.2)
    return signal * np.maximum(envelope, 0)


def add(signal, time, gain=1, pan=0, room=False):
    start = round(time * SR)
    if start < 0:
        signal = signal[-start:]
        start = 0
    count = min(len(signal), len(MIX) - start)
    if count <= 0:
        return
    stereo = signal[:count, None] * gain * np.array([np.sqrt((1 - pan) / 2), np.sqrt((1 + pan) / 2)])
    MIX[start:start + count] += stereo
    if room:
        ROOM[start:start + count] += stereo


chords = [[62, 65, 69, 72], [58, 62, 65, 69], [60, 64, 67, 72], [57, 60, 64, 67]]
roots = [38, 34, 36, 33]
melody = [77, 74, 72, 69, 74, 77, 81, 77]
for bar in range(26):
    time = bar * 2
    chord = chords[(bar // 2) % 4]
    # A calm harmonic bed under bright, syncopated plucks and a crisp beat.
    for i, midi in enumerate(chord):
        add(note(midi - 12, 2.3, "pad"), time, .021, pan=(i - 1.5) * .22, room=True)
    for k in range(8):
        add(note(chord[[0, 2, 1, 3, 2, 0, 3, 1][k]] + 12, .65),
            time + (k * .5 + (.045 if k % 2 else 0)) * BEAT,
            .049 if k % 2 else .038, pan=(-.38 if k % 2 else .38), room=True)
    if bar % 2 == 0:
        for k in [0, 1.5, 3]:
            add(note(melody[(bar + int(k * 2)) % 8], .8), time + k * BEAT, .04, .15, True)
    for beat in [0, 1, 2, 3]:
        t = np.arange(int(.34 * SR)) / SR
        kick = np.sin(2 * np.pi * (47 * t + 82 * .019 * (1 - np.exp(-t / .019)))) * np.exp(-t * 14)
        add(kick, time + beat * BEAT, .23)
    for beat in [1, 3]:
        t = np.arange(int(.16 * SR)) / SR
        clap = filter_signal(filter_signal(RNG.normal(size=len(t)), 900, "highpass"), 8200) * np.exp(-t * 29)
        add(clap, time + beat * BEAT, .065, .10)
    for k in range(8):
        t = np.arange(int(.075 * SR)) / SR
        hat = filter_signal(RNG.normal(size=len(t)), 6500, "highpass") * np.exp(-t * 65)
        add(hat, time + k * BEAT / 2, .018 if k % 2 else .012, (-.25 if k % 2 else .25))
    for beat, length in [(0, .7), (1.5, .45), (2.5, .7), (3.5, .35)]:
        add(note(roots[(bar // 2) % 4], length, "bass"), time + beat * BEAT, .13)

for seconds, gain in [(.09, .07), (.16, .06), (.375, .12), (.75, .055)]:
    offset = round(seconds * SR)
    MIX[offset:] += ROOM[:-offset, ::-1] * gain

# Light transitions, close to scene cuts, without covering important maths.
for time in [5, 11, 18, 24, 31, 36, 44.5]:
    t = np.arange(int(.32 * SR)) / SR
    whoosh = filter_signal(RNG.normal(size=len(t)), 2800) * np.sin(np.pi * t / .32) ** 2
    add(whoosh, time - .16, .033, -.2)

for time in [7.2, 13.27, 18.94, 21.04, 26.24, 27.74, 33.20, 41.14, 46.8]:
    add(note(86, .18), time, .050, .12, True)

# Two distinct, pleasant major arpeggios for the final answer and checked result.
for time in [36.06, 42]:
    for k, midi in enumerate([74, 78, 81, 86]):
        add(note(midi, .72), time + k * .075, .083, (k - 1.5) * .17, True)

t = np.arange(len(MIX)) / SR
MIX *= (np.minimum(t / .025, 1) * np.minimum((SECONDS - t) / 1.1, 1))[:, None]
MIX = np.tanh(MIX * 1.1)
OUT.mkdir(parents=True, exist_ok=True)
QA.mkdir(parents=True, exist_ok=True)
raw = OUT / "math-short-raw.wav"
wavfile.write(raw, SR, (MIX * 30000).astype(np.int16))

# Two-pass EBU R128 normalization. The small true-peak margin survives AAC.
probe = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(raw), "-af",
                        "loudnorm=I=-15.5:TP=-1.5:LRA=8:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True, check=True)
measurements, _ = json.JSONDecoder().raw_decode(probe.stderr[probe.stderr.rfind("{"):])
options = (f"loudnorm=I=-15.5:TP=-1.5:LRA=8:measured_I={measurements['input_i']}:"
           f"measured_TP={measurements['input_tp']}:measured_LRA={measurements['input_lra']}:"
           f"measured_thresh={measurements['input_thresh']}:offset={measurements['target_offset']}:"
           "linear=true:print_format=json")
result = subprocess.run(["ffmpeg", "-hide_banner", "-y", "-i", str(raw), "-af", options,
                         "-ar", str(SR), "-c:a", "pcm_s16le", str(OUT / "math-short.wav")],
                        capture_output=True, text=True, check=True)
normalized, _ = json.JSONDecoder().raw_decode(result.stderr[result.stderr.rfind("{"):])
(QA / "soundtrack-normalization.json").write_text(json.dumps(normalized, indent=2), encoding="utf-8")
print("Original 52-second stereo soundtrack + synchronized SFX exported.")
