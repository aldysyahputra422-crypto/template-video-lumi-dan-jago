"""Ukur 'rasa gambar' video: kegelapan, vinyet, dan grain, dengan cara yang sama untuk referensi dan hasil kita.

python -m scripts.ukur_fx <video.mp4> [...]
- gelap: porsi piksel luma < 25 (rata-rata per frame)
- terang: rata-rata luma
- sudut_per_tengah: terang 4 sudut dibagi terang tengah (median); kecil = vinyet kuat
- grain: selisih rata-rata frame dengan versi blur-nya di area gelap (luma 8 sampai 70)
Rentang referensi ada di config/gaya.yaml `target_visual`.
"""
import subprocess
import sys

import numpy as np
from PIL import Image, ImageFilter


def _frames(p: str, fps: int = 1) -> np.ndarray:
    r = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(p), "-vf", f"fps={fps},scale=360:640", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                       capture_output=True, check=True).stdout
    return np.frombuffer(r, np.uint8).reshape(-1, 640, 360, 3)


def ukur(p) -> dict:
    F = _frames(p)
    F = F[1:-1] if len(F) > 2 else F
    gelap, terang, vin, grain = [], [], [], []
    for f in F:
        y = f.astype(float) @ [.299, .587, .114]
        gelap.append((y < 25).mean())
        terang.append(y.mean())
        sudut = np.mean([y[:96, :54].mean(), y[:96, -54:].mean(), y[-96:, :54].mean(), y[-96:, -54:].mean()])
        vin.append(sudut / (y[240:400, 120:240].mean() + 1e-6))
        b = np.asarray(Image.fromarray(y.astype(np.uint8)).filter(ImageFilter.GaussianBlur(2)), float)
        m = (y > 8) & (y < 70)
        if m.sum() > 500:
            grain.append(np.abs(y - b)[m].mean())
    return {"gelap": round(float(np.mean(gelap)), 2), "terang": round(float(np.mean(terang)), 1),
            "sudut_per_tengah": round(float(np.median(vin)), 2), "grain": round(float(np.median(grain)), 2) if grain else 0.0}


if __name__ == "__main__":
    for x in sys.argv[1:]:
        print(x, ukur(x))
