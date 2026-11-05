"""Normalisasi loudness harus tepat -14 LUFS juga untuk suara yang dinamis (suara asli, bukan TTS rata)."""
import re
import subprocess

import numpy as np
import soundfile as sf

from scripts import campur


def _lufs(p):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(p), "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    ringkas = out[out.rindex("Summary:"):]
    return float(re.search(r"I:\s+(-?[\d.]+) LUFS", ringkas).group(1)), float(re.search(r"Peak:\s+(-?[\d.]+) dBFS", ringkas).group(1))


def test_normalkan_dinamis_tepat_sasaran(tmp_path):
    sr, rng = 44100, np.random.default_rng(1)
    potong = []
    for i in range(40):                        # frasa keras-pelan bergantian + jeda, seperti narasi asli
        n = int(sr * rng.uniform(0.4, 1.6))
        t = np.arange(n) / sr
        amp = [0.02, 0.3, 0.06, 0.5][i % 4]
        potong += [amp * np.sin(2 * np.pi * rng.uniform(120, 300) * t) * np.hanning(n), np.zeros(int(sr * 0.25))]
    masuk = tmp_path / "m.wav"
    sf.write(masuk, np.concatenate(potong).astype(np.float32), sr)
    keluar = tmp_path / "k.wav"
    campur.normalkan(masuk, keluar)
    i, puncak = _lufs(keluar)
    assert abs(i - campur.SASARAN_LUFS) <= 0.5, i
    assert puncak <= -1.0, puncak


def test_normalkan_suara_serak_berekor_tebal(tmp_path):
    """Meniru suara ElevenLabs asli (serak, ±-24 LUFS, puncak tajam): loudnorm dinamis berhenti di bawah sasaran."""
    sr, rng = 44100, np.random.default_rng(3)
    potong = []
    for _ in range(70):
        n = int(sr * rng.uniform(0.3, 1.2))
        x = np.convolve(rng.laplace(0, 1, n), np.ones(8) / 8, "same")
        potong += [0.3 * x * np.hanning(n) * rng.choice([0.4, 1.0, 0.6]), np.zeros(int(sr * 0.12))]
    masuk, keluar = tmp_path / "m.wav", tmp_path / "k.wav"
    sf.write(masuk, np.clip(np.concatenate(potong), -1, 1).astype(np.float32), sr)
    assert -30 < _lufs(masuk)[0] < -20
    campur.normalkan(masuk, keluar)
    i, puncak = _lufs(keluar)
    assert abs(i - campur.SASARAN_LUFS) <= 0.5, i
    assert puncak <= -1.0, puncak
