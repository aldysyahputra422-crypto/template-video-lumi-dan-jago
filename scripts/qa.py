"""QA video jadi: resolusi, durasi vs linimasa, loudness, puncak, dan gerak (target dari config/gaya.yaml). Angka, bukan klaim.

python -m scripts.qa <folder>  → <folder>/qa.json. Kode 0 lulus, 1 ada masalah.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

from scripts import ukur_fx, ukur_gerak

ROOT = Path(__file__).resolve().parents[1]


def loudness(p: Path) -> dict:
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", str(p), "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    s = r[r.rindex("Summary:"):]
    return {"lufs": float(re.search(r"I:\s+(-?[0-9.]+) LUFS", s).group(1)), "puncak_dbfs": float(re.search(r"Peak:\s+(-?[0-9.]+) dBFS", s).group(1))}


def periksa(folder: Path) -> dict:
    folder = Path(folder)
    v = folder / "video.mp4"
    masalah = []
    if not v.exists():
        return {"lulus": False, "masalah": ["video.mp4 tidak ada"]}
    j = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(v)], capture_output=True, text=True).stdout)
    vid = next((s for s in j["streams"] if s["codec_type"] == "video"), None)
    aud = next((s for s in j["streams"] if s["codec_type"] == "audio"), None)
    durasi = float(j["format"]["duration"])
    h = {"resolusi": [vid["width"], vid["height"]] if vid else None, "durasi": round(durasi, 2), "ukuran_mb": round(int(j["format"]["size"]) / 1e6, 2)}
    if h["resolusi"] != [720, 1280]:
        masalah.append(f"resolusi {h['resolusi']}, harus 720x1280")
    if not aud:
        masalah.append("tidak ada audio")
    else:
        h.update(loudness(v))
        if abs(h["lufs"] + 14) > 1:
            masalah.append(f"loudness {h['lufs']} LUFS, harus -14 ±1")
        if h["puncak_dbfs"] > -1:
            masalah.append(f"puncak {h['puncak_dbfs']} dBFS, harus di bawah -1")
    g = ukur_gerak.ukur(v)
    h["gerak"] = g
    gaya = yaml.safe_load((ROOT / "config/gaya.yaml").read_text(encoding="utf-8"))
    T = gaya["target_gerak"]
    h["visual"] = fx = ukur_fx.ukur(v)
    h["catatan_visual"] = [f"{k} {fx[k]} di luar rentang referensi {r}" for k, r in gaya.get("target_visual", {}).items() if not r[0] <= fx[k] <= r[1]]
    if g["gerak_rata"] < T["gerak_rata_min"]:
        masalah.append(f"gerak rata-rata {g['gerak_rata']}, minimal {T['gerak_rata_min']} (vt3 9,4): adegan kurang bergerak")
    if g["persen_diam"] > T["persen_diam_maks"]:
        masalah.append(f"layar diam {g['persen_diam']}% dari durasi, maksimal {T['persen_diam_maks']}% (vt3 0%): gerak kurang")
    if g["diam_terpanjang"] > T["diam_terpanjang_maks"]:
        masalah.append(f"diam terpanjang {g['diam_terpanjang']} dtk, maksimal {T['diam_terpanjang_maks']} dtk: gerak kurang")
    if g["beda_3dtk"] < T["beda_3dtk_min"]:
        masalah.append(f"beda gambar tiap 3 dtk {g['beda_3dtk']}, minimal {T['beda_3dtk_min']}: komposisi jarang berganti (gerak kamera/adegan)")
    tl = folder / "timeline.json"
    if tl.exists():
        dt = json.loads(tl.read_text(encoding="utf-8"))["durasi"]
        h["durasi_linimasa"] = dt
        if abs(durasi - dt) > 0.5:
            masalah.append(f"durasi video {durasi:.2f} dtk, linimasa {dt} dtk")
    h["masalah"], h["lulus"] = masalah, not masalah
    (folder / "qa.json").write_text(json.dumps(h, ensure_ascii=False, indent=1), encoding="utf-8")
    return h


if __name__ == "__main__":
    r = periksa(Path(sys.argv[1]))
    print(json.dumps(r, ensure_ascii=False))
    sys.exit(0 if r["lulus"] else 1)
