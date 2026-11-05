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
SASARAN_LUFS, PUNCAK_TP = -14.0, -1.5
MUSIK = ROOT / "aset/audio/musik_tegang.mp3"


def _baca(p: Path) -> np.ndarray:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def _ukur(masuk: Path, f: str) -> dict:
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(masuk), "-af", f + ":print_format=json", "-f", "null", "-"],
                         capture_output=True, text=True, check=True).stderr
    return json.loads(err[err.rindex("{"):err.rindex("}") + 1])


def normalkan(masuk: Path, keluar: Path) -> None:
    """Narasi ke -14 LUFS, true peak <= -1,5 dBTP.
    1) kompresor ringan + gain ke sasaran + limiter -3 dBFS (suara asli ElevenLabs bisa -24 LUFS dengan puncak -3 dBTP:
       loudnorm saja jatuh ke mode dinamis dan berhenti 1 sampai 2 LU di bawah sasaran);
    2) koreksi akhir loudnorm dua kali jalan, linear (kini mungkin karena puncak sudah diberi ruang)."""
    tengah = Path(keluar).with_name("_norm_tengah.wav")
    f = f"loudnorm=I={SASARAN_LUFS}:TP={PUNCAK_TP}:LRA=20"
    kompres = "acompressor=threshold=0.05:ratio=2.5:attack=5:release=120"
    i_awal = float(_ukur(masuk, kompres + "," + f)["input_i"])
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(masuk), "-af",
                    f"{kompres},volume={SASARAN_LUFS - i_awal:.2f}dB,alimiter=limit=0.7:attack=3:release=60:level=false",
                    "-ar", str(SR), str(tengah)], check=True)
    m = _ukur(tengah, f)
    f2 = (f + f":measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
          f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tengah), "-af", f2, "-ar", str(SR), "-ac", "2", str(keluar)], check=True)
    tengah.unlink()


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
    normalkan(mentah, keluar)
    mentah.unlink()
    return keluar


if __name__ == "__main__":
    print(jalankan(Path(sys.argv[1])))
