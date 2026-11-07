"""Percepat suara.* secara lokal (ffmpeg atempo, nada tetap) bila tempo bicara di bawah sasaran. Gratis, tanpa API.

python -m scripts.tempo <folder>
Latar: ElevenLabs v3 tidak punya pengaturan kecepatan, dan tag seperti [whispers] memperlambat bacaan (video menara: 211 kata dibaca
1:44 = 2,0 kata/dtk, referensi 2,7 sampai 3,45). Faktor = durasi suara / (jumlah kata / sasaran), dibatasi `suara.faktor_maks`.
Berkas pemilik disimpan sebagai suara-asli.<ext>; hasilnya suara.wav + tempo.json (sidik jari hasil, supaya tidak dipercepat dua kali
dan rekaman pengganti diproses ulang).
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import yaml

from scripts import selaras
from scripts.naskah_format import token

ROOT = Path(__file__).resolve().parents[1]


def konfig() -> dict:
    g = yaml.safe_load((ROOT / "config/gaya.yaml").read_text(encoding="utf-8")) or {}
    return {"tempo_sasaran": 2.7, "faktor_maks": 1.35, "faktor_min": 1.06, **(g.get("suara") or {})}


def durasi(p: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(p)], capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def _sidik(p: Path) -> str:
    return hashlib.sha1(p.read_bytes()).hexdigest()


def sesuaikan(folder: Path) -> dict:
    folder = Path(folder)
    k = konfig()
    p = selaras.cari_suara(folder)
    if p is None:
        return {"diubah": False, "alasan": "belum ada suara"}
    n = json.loads((folder / "naskah.json").read_text(encoding="utf-8"))
    kata = sum(len(token(x["ucap"])) for x in n["ketukan"])
    marka = folder / "tempo.json"
    if marka.exists() and p.name == "suara.wav" and json.loads(marka.read_text(encoding="utf-8")).get("sidik") == _sidik(p):
        return {"diubah": False, "alasan": "sudah dipercepat", **json.loads(marka.read_text(encoding="utf-8"))}
    dur = durasi(p)
    wps = kata / dur if dur else 0.0
    faktor = dur / (kata / k["tempo_sasaran"]) if kata else 1.0
    info = {"kata": kata, "durasi_asal": round(dur, 1), "kata_per_detik_asal": round(wps, 2)}
    if faktor < k["faktor_min"]:
        return {"diubah": False, "alasan": "tempo sudah cukup cepat", **info}
    faktor = min(faktor, k["faktor_maks"])
    asli = folder / f"suara-asli{p.suffix}"
    asli.unlink(missing_ok=True)
    p.rename(asli)
    keluar = folder / "suara.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(asli), "-filter:a", f"atempo={faktor:.4f}", "-ar", "44100", "-ac", "1", str(keluar)], check=True)
    hasil = {**info, "faktor": round(faktor, 3), "durasi_baru": round(durasi(keluar), 1), "sidik": _sidik(keluar)}
    marka.write_text(json.dumps(hasil), encoding="utf-8")
    return {"diubah": True, **hasil}


if __name__ == "__main__":
    print(json.dumps(sesuaikan(Path(sys.argv[1])), ensure_ascii=False))
