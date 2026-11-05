"""Campur suara Ata + SFX + musik pelan → campur.wav pada -14 LUFS, puncak di bawah -1 dBFS. Deterministik.

python -m scripts.campur <folder>   (butuh timeline.json dan suara.*)
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

from scripts.selaras import cari_suara

ROOT = Path(__file__).resolve().parents[1]
SR = 44100
SFX_DB, MUSIK_DB = -13.0, -27.0
MUSIK = ROOT / "aset/audio/musik_tegang.mp3"


def _baca(p: Path) -> np.ndarray:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def jalankan(folder: Path, musik: Path | None = MUSIK) -> Path:
    folder = Path(folder)
    tl = json.loads((folder / "timeline.json").read_text(encoding="utf-8"))
    n = int(tl["durasi"] * SR)
    mix = np.zeros(n, dtype=np.float32)
    suara = _baca(cari_suara(folder))[:n]
    mix[: len(suara)] += suara
    for s in tl.get("sfx", []):
        p = ROOT / f"aset/audio/{s['nama']}.mp3"
        if not p.exists():
            continue
        x = _baca(p) * 10 ** (SFX_DB / 20)
        i = int(s["t"] * SR)
        k = max(0, min(len(x), n - i))
        mix[i:i + k] += x[:k]
    if musik and Path(musik).exists():
        m = _baca(musik) * 10 ** (MUSIK_DB / 20)
        m = np.tile(m, int(np.ceil(n / len(m))))[:n]
        f = np.ones(n, dtype=np.float32)
        h = min(n, int(1.2 * SR))
        f[-h:] = np.linspace(1, 0, h)
        mix += m * f
    mentah = folder / "_campur_mentah.wav"
    sf.write(mentah, mix, SR)
    keluar = folder / "campur.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(mentah), "-af", "loudnorm=I=-14:TP=-1.5:LRA=7", "-ar", str(SR), "-ac", "2", str(keluar)], check=True)
    mentah.unlink()
    return keluar


if __name__ == "__main__":
    print(jalankan(Path(sys.argv[1])))
