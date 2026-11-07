"""Ukur palet dominan sebuah video (deterministik, tanpa LLM) untuk mengunci gaya warna dari referensi.

python -m scripts.ukur_palet <video> [n]  → JSON daftar {hex, porsi}
Frame tiap 1 dtk diperkecil 90x160, warna dikuantisasi 4 bit per kanal, lalu warna mirip (jarak < 40) digabung.
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

W, H = 90, 160


def jarak(a: str, b: str) -> float:
    x = np.array([int(a[i:i + 2], 16) for i in (1, 3, 5)], float)
    y = np.array([int(b[i:i + 2], 16) for i in (1, 3, 5)], float)
    return float(np.linalg.norm(x - y))


def ukur(p: Path, n: int = 12) -> list[dict]:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-vf", f"fps=1,scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    px = np.frombuffer(raw, np.uint8).reshape(-1, 3)
    q = (px // 16) * 16 + 8
    kunci, hitung = np.unique(q, axis=0, return_counts=True)
    urut = np.argsort(-hitung)
    kelompok: list[list] = []          # [warna_rata, jumlah]
    for i in urut:
        c, k = kunci[i].astype(float), hitung[i]
        for g in kelompok:
            if np.linalg.norm(g[0] - c) < 40:
                g[0] = (g[0] * g[1] + c * k) / (g[1] + k); g[1] += k
                break
        else:
            kelompok.append([c, k])
    total = sum(g[1] for g in kelompok)
    kelompok.sort(key=lambda g: -g[1])
    return [{"hex": "#" + "".join(f"{int(round(v)):02X}" for v in g[0]), "porsi": round(g[1] / total, 3)} for g in kelompok[:n]]


if __name__ == "__main__":
    print(json.dumps(ukur(Path(sys.argv[1]), int(sys.argv[2]) if len(sys.argv) > 2 else 12)))
