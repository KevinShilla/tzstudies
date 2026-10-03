"""Original TZStudies instrumental: synthesized here, with no third-party samples."""

import wave
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfilt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "public" / "audio"
OUT.mkdir(parents=True, exist_ok=True)
SR = 48000
BPM = 110
BEAT = 60 / BPM
RNG = np.random.default_rng(1421)


def filt(a, cutoff, order=2, kind="lowpass"):
    return sosfilt(butter(order, cutoff, kind, fs=SR, output="sos"), a)


def hz(midi):
    return 440 * 2 ** ((midi - 69) / 12)


def tone(midi, duration, kind="keys"):
    t = np.arange(int(SR * duration)) / SR
    f = hz(midi)
    if kind == "keys":
        # A soft, struck electric-piano timbre, with a brief mallet transient.
        a = (
            np.sin(2 * np.pi * f * t + 1.8 * np.sin(2 * np.pi * f * t) * np.exp(-t * 7))
            + 0.26 * np.sin(2 * np.pi * f * 2.003 * t) * np.exp(-t * 3.8)
            + 0.10 * np.sin(2 * np.pi * f * 3.01 * t) * np.exp(-t * 6)
        )
        a *= (1 - np.exp(-t * 500)) * np.exp(-t * 2.8)
        a = filt(a, 6000)
    elif kind == "pluck":
        a = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) + 0.13 * np.sin(2 * np.pi * 3 * f * t)
        a *= (1 - np.exp(-t * 300)) * np.exp(-t * 5)
        a = filt(a, 4800)
    elif kind == "pad":
        a = (
            sum(np.sin(2 * np.pi * f * detune * t + phase) for detune, phase in [(0.996, 0.1), (1, 0.7), (1.004, 1.3)])
            / 3
        )
        a += 0.08 * np.sin(2 * np.pi * 2 * f * t)
        envelope = np.minimum(t / 0.55, 1) * np.minimum((duration - t) / 0.8, 1)
        a *= np.maximum(envelope, 0)
    else:
        a = np.sin(2 * np.pi * f * t) + 0.18 * np.sin(2 * np.pi * 2 * f * t)
        a *= np.minimum(t / 0.015, 1) * np.maximum(np.minimum((duration - t) / 0.11, 1), 0)
    return a


def write(name, audio):
    peak = np.max(np.abs(audio))
    audio = np.tanh(audio * 0.9)
    audio *= 0.86 / max(np.max(np.abs(audio)), 0.01)
    with wave.open(str(OUT / name), "wb") as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(SR)
        wav.writeframes((audio * 32767).astype("<i2").tobytes())
    print(name, "seconds", round(len(audio) / SR, 3), "raw peak", round(float(peak), 3))


def score(seconds, bars, name, short=False):
    audio = np.zeros((int(seconds * SR), 2), dtype=np.float64)
    ambience = np.zeros_like(audio)

    def add(signal, start, gain, pan=0, wet=False):
        i = int(start * SR)
        if i < 0 or i >= len(audio):
            return
        n = min(len(signal), len(audio) - i)
        destination = ambience if wet else audio
        destination[i : i + n, 0] += signal[:n] * gain * np.sqrt((1 - pan) / 2)
        destination[i : i + n, 1] += signal[:n] * gain * np.sqrt((1 + pan) / 2)

    chords = [[50, 57, 60, 64, 69], [46, 53, 57, 60, 65], [48, 53, 57, 60, 67], [48, 55, 60, 62, 67]]
    roots = [38, 34, 29, 36]
    melody = [74, 77, 76, 69, 72, 74, 77, 81, 79, 77, 76, 72, 74, 76, 69, 72]
    for bar in range(bars):
        start = bar * 4 * BEAT
        # A distinct restrained middle eight lets the answer-key demonstration breathe.
        quiet = (14 <= bar < 20) and not short
        intro = bar < (1 if short else 3)
        closing = bar >= bars - 2
        chord = chords[(bar // 2) % 4]
        if closing:
            chord = [50, 57, 60, 65, 69]
        for j, note in enumerate(chord):
            add(tone(note, 4 * BEAT + 0.8, "pad"), start, 0.034 if intro else 0.022, pan=(j - 2) * 0.24, wet=True)
            for beat in [0, 2.5] if quiet else [0, 1.5, 2.5]:
                add(
                    tone(note + 12, 1.5, "keys"), start + (beat + 0.025 * j) * BEAT, 0.026, pan=(j - 2) * 0.20, wet=True
                )
        if bar >= 2 or short:
            for k in range(8):
                if closing and k > 3:
                    continue
                note = chord[[0, 2, 3, 4, 2, 1, 3, 4][k]] + 24
                swing = 0.04 if k % 2 else 0
                add(
                    tone(note, 0.65, "pluck"),
                    start + (k * 0.5 + swing) * BEAT,
                    0.021 if quiet else 0.029,
                    pan=(-0.45 if k % 2 else 0.45),
                    wet=True,
                )
        if bar >= 7 or short:
            for beat in [0, 1.5, 3]:
                note = melody[(bar * 3 + int(beat * 2)) % len(melody)]
                if closing:
                    note = 74 if beat == 0 else 69
                add(tone(note, 0.85, "keys"), start + beat * BEAT, 0.041, pan=0.12, wet=True)
        if not intro and not closing:
            for beat in [0, 1, 2, 3]:
                t = np.arange(int(0.42 * SR)) / SR
                kick = np.sin(2 * np.pi * (46 * t + (135 - 46) * 0.026 * (1 - np.exp(-t / 0.026)))) * np.exp(-t * 12)
                kick += filt(RNG.normal(0, 1, len(t)), 2800) * np.exp(-t * 180) * 0.13
                add(kick, start + beat * BEAT, 0.17 if quiet else 0.26)
            for beat in [1, 3]:
                t = np.arange(int(0.22 * SR)) / SR
                noise = filt(filt(RNG.normal(0, 1, len(t)), 850, kind="highpass"), 8500)
                clap = noise * (np.exp(-t * 25) + 0.45 * np.exp(-np.maximum(t - 0.018, 0) * 40) * (t > 0.018))
                clap += 0.18 * np.sin(2 * np.pi * 180 * t) * np.exp(-t * 30)
                add(clap, start + beat * BEAT, 0.067 if quiet else 0.09, pan=0.06)
            for k in range(8):
                t = np.arange(int(0.13 * SR)) / SR
                hat = filt(RNG.normal(0, 1, len(t)), 7000, kind="highpass") * np.exp(-t * (60 if k % 2 == 0 else 35))
                add(
                    hat,
                    start + (k * 0.5 + (0.025 if k % 2 else 0)) * BEAT,
                    0.023 if k % 2 else 0.014,
                    pan=(-0.28 if k % 2 else 0.28),
                )
            root = roots[(bar // 2) % 4]
            for beat, length in [(0, 0.75), (1.5, 0.45), (2.5, 0.8), (3.5, 0.35)]:
                add(tone(root, 0.9 * BEAT * length, "bass"), start + beat * BEAT, 0.105)
    # Multi-tap stereo room and tempo delay, deliberately quiet below the dry mix.
    audio += ambience
    for delay, gain in [(0.087, 0.10), (0.139, 0.08), (BEAT * 0.75, 0.15), (BEAT * 1.5, 0.07)]:
        offset = int(delay * SR)
        audio[offset:] += ambience[:-offset, ::-1] * gain
    # Original subtle transitions and click accents; no downloaded sound effects.
    times = [6.55, 10.91, 17.45, 30.55, 43.64, 52.36, 61.09, 65.45] if not short else [3.0, 6.0, 12.0, 18.0, 22.0]
    for time in times:
        t = np.arange(int(0.5 * SR)) / SR
        air = filt(RNG.normal(0, 1, len(t)), 3200) * np.sin(np.pi * t / 0.5) ** 2
        add(air, time - 0.24, 0.022, pan=-0.2)
        add(tone(86, 0.35, "pluck"), time, 0.024, pan=0.2)
    t = np.arange(len(audio)) / SR
    fade = np.minimum(t / 0.08, 1) * np.minimum((seconds - t) / 1.45, 1)
    audio *= np.maximum(fade, 0)[:, None]
    write(name, audio)


score(72, 33, "main-raw.wav")
score(26, 12, "social-raw.wav", short=True)
