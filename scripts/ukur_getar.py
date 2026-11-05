"""Ukur getar: gerak yang bolak-balik cepat (bergetar) lawan gerak yang mengalir ke satu arah.

python -m scripts.ukur_getar <video.mp4> [...]
Untuk tiap frame bergerak: r = |f(t+3) - f(t)| / (|f(t+1) - f(t)| + |f(t+2) - f(t+1)| + |f(t+3) - f(t+2)|).
Gerak searah (kamera dorong, tokoh berjalan) memberi r mendekati 1; getar (maju-mundur tiap beberapa frame) memberi r kecil karena gambar
kembali ke posisi semula. Frame di-blur dan diperkecil dulu agar grain tidak terhitung.
- searah: median r pada frame yang bergerak (besar = halus)
- persen_getar: porsi petak bergerak (grid 9 x 16) dengan r < 0,3; getar tokoh kecil tetap terlihat walau kamera bergerak
"""
import subprocess
import sys

import numpy as np


def _frame(p: str) -> np.ndarray:
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-vf", "scale=90:160,gblur=sigma=1.2,format=gray", "-f", "rawvideo", "-"],
                       capture_output=True, check=True).stdout
    return np.frombuffer(r, np.uint8).reshape(-1, 160, 90).astype(np.float32)


def ukur(p) -> dict:
    f = _frame(p)
    n = f.shape[0]
    sel = f[:, :, :].reshape(n, 16, 10, 9, 10).mean(axis=(2, 4))      # petak 10 x 10 piksel (grid 9 x 16)
    d1 = np.abs(np.diff(sel, axis=0))
    d3 = np.abs(sel[3:] - sel[:-3])
    jalur = d1[:-2] + d1[1:-1] + d1[2:]
    gerak = jalur > 1.5                     # petak yang bergerak; abaikan diam dan grain
    r = d3[gerak] / jalur[gerak]
    return {"searah": round(float(np.median(r)), 2) if r.size else 1.0,
            "persen_getar": round(100 * float((r < 0.3).mean()), 1) if r.size else 0.0}

if __name__ == "__main__":
    for x in sys.argv[1:]:
        print(x.split("/")[-1][:40], ukur(x))
