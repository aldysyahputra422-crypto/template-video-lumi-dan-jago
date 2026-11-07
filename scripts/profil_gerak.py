"""Profil gerak per ketukan: ketukan mana yang bergerak dan mana yang seperti slide.

python -m scripts.profil_gerak <folder>   (butuh video.mp4 dan timeline.json)
Cetak 'no:skor' per ketukan; tanda * = ada sisipan. Skor ketukan tanpa aksi biasanya 9 sampai 12, ketukan bersisipan atau bergerak
besar 16 sampai 37 (video uang-keranjang). Ketukan dengan skor rendah berturut-turut perlu AKSI gerak, SISIPAN, atau bidikan lebih dekat.
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np


def profil(folder: Path) -> list[dict]:
    folder = Path(folder)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(folder / "video.mp4"), "-vf", "fps=4,scale=180:320,format=gray", "-f", "rawvideo", "-"],
                         capture_output=True, check=True).stdout
    a = np.frombuffer(raw, np.uint8).reshape(-1, 320, 180).astype(float)
    d = np.abs(np.diff(a, axis=0)).mean(axis=(1, 2)) * 2
    out = []
    for k in json.loads((folder / "timeline.json").read_text(encoding="utf-8"))["ketukan"]:
        i0, i1 = int(k["mulai"] * 4), min(len(d), int(k["selesai"] * 4))
        out.append({"no": k["no"], "skor": round(float(d[i0:i1].mean()), 1) if i1 > i0 else 0.0, "sisipan": bool(k.get("sisipan"))})
    return out


if __name__ == "__main__":
    p = profil(Path(sys.argv[1]))
    print(" ".join(f"{x['no']}:{x['skor']}{'*' if x['sisipan'] else ''}" for x in p))
    lemah = [x["no"] for x in p if x["skor"] < 12 and not x["sisipan"]]
    print("lemah (<12, tanpa sisipan):", lemah)
