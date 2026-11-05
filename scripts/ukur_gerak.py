"""Ukur gerak sebuah video secara deterministik (tanpa LLM), untuk dibandingkan dengan video referensi.

python -m scripts.ukur_gerak <video> [video ...]   → tabel JSON per video
- gerak_rata: rata-rata selisih piksel antar frame (skala 0-255, gambar diperkecil 90x160, 10 fps)
- persen_diam: persen jendela 0,5 dtk yang selisih maksimalnya < AMBANG_DIAM (layar nyaris tidak berubah)
- diam_terpanjang: rentang diam berturut terpanjang (dtk)
- beda_3dtk: rata-rata selisih gambar t dan t+3 dtk (seberapa sering komposisi berganti)
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

FPS, W, H = 10, 90, 160
AMBANG_DIAM = 1.0


def _frame(p: Path) -> np.ndarray:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-vf", f"fps={FPS},scale={W}:{H},format=gray", "-f", "rawvideo", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.uint8).reshape(-1, H, W).astype(np.float32)


def ukur(p: Path) -> dict:
    f = _frame(Path(p))
    d = np.abs(np.diff(f, axis=0)).mean(axis=(1, 2))
    jendela = FPS // 2
    maks = [d[i:i + jendela].max() for i in range(0, len(d) - jendela + 1, jendela)]
    diam = [m < AMBANG_DIAM for m in maks]
    terpanjang = run = 0
    for x in diam:
        run = run + 1 if x else 0
        terpanjang = max(terpanjang, run)
    b3 = np.abs(f[3 * FPS:] - f[:-3 * FPS]).mean(axis=(1, 2)) if len(f) > 3 * FPS else np.array([0.0])
    return {"durasi": round(len(f) / FPS, 1), "gerak_rata": round(float(d.mean()), 2), "persen_diam": round(100 * sum(diam) / max(1, len(diam))),
            "diam_terpanjang": round(terpanjang * 0.5, 1), "beda_3dtk": round(float(b3.mean()), 1)}


if __name__ == "__main__":
    for a in sys.argv[1:]:
        print(json.dumps({"video": Path(a).name[:40], **ukur(Path(a))}, ensure_ascii=False))
