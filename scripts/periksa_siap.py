"""Periksa apakah repo siap memproduksi video di sesi baru (mis. akun utama). Mekanis, tanpa LLM.

python -m scripts.periksa_siap [--tanpa-test]  → daftar centang; kode 0 bila semua yang penting lulus.
Yang bisa diperbaiki sendiri diperbaiki (SFX sintetis dibuat ulang); sisanya diberi petunjuk.
"""
import importlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def _cek(nama, lulus, keterangan, penting=True):
    return {"nama": nama, "lulus": bool(lulus), "keterangan": keterangan, "penting": penting}


def periksa(jalankan_test: bool = True) -> dict:
    c = []
    kurang = [m for m in ("yaml", "numpy", "soundfile", "jsonschema", "faster_whisper") if importlib.util.find_spec(m) is None]
    c.append(_cek("python", not kurang, "modul lengkap" if not kurang else f"kurang: {', '.join(kurang)} (pip install -r requirements.txt)"))
    c.append(_cek("ffmpeg", shutil.which("ffmpeg") and shutil.which("ffprobe"), "ffmpeg dan ffprobe ada" if shutil.which("ffmpeg") else "pasang ffmpeg"))
    pw = (ROOT / "render/node_modules/playwright").exists() or subprocess.run(["node", "-e", "require('playwright')"], cwd=ROOT / "render", capture_output=True).returncode == 0
    c.append(_cek("node_playwright", shutil.which("node") and pw, "node + playwright siap" if pw else "npm install --prefix render"))
    font = list((ROOT / "render/node_modules/@fontsource").glob("*/files/*.woff2")) if (ROOT / "render/node_modules/@fontsource").exists() else []
    c.append(_cek("font", font, f"{len(font)} berkas font" if font else "npm install --prefix render (Montserrat, Baloo 2)"))
    pose = yaml.safe_load((ROOT / "config/tokoh.yaml").read_text(encoding="utf-8"))["tokoh"]["ata"]["pose"]
    hilang = [p for p in pose if not (ROOT / f"aset/maskot/panda/pose/{p}.svg").exists()]
    c.append(_cek("pose_ata", not hilang, f"{len(pose)} pose" if not hilang else f"hilang: {hilang} (python -m scripts.potong_pose)"))
    from scripts import sfx
    if not (sfx.SINTETIS / "whoosh.wav").exists():
        sfx.buat_sintetis()
    kat = sfx.katalog()
    ada = [n for n in list(kat["sfx"]) + list(kat["musik"]) if sfx.cari(n)]
    unduhan = len(list(sfx.UNDUHAN.glob("*.mp3"))) if sfx.UNDUHAN.exists() else 0
    c.append(_cek("sfx", len(ada) == len(kat["sfx"]) + len(kat["musik"]), f"{len(ada)} siap, {unduhan} dari Mixkit (sisanya sintetis)"))
    from scripts import pasang_otomatis as po
    skill = [e for e in po.muat(ROOT / "katalog/skill.yaml") if e.otomatis]
    belum = [e.id for e in skill if not po.sudah_terpasang(e, po.SKILLS, po.RUJUKAN)]
    c.append(_cek("skill", not belum, "skill otomatis terpasang" if not belum else f"belum: {belum} (python -m scripts.pasang_otomatis)", penting=False))
    from scripts import lint_naskah as ln, naskah_format as nf
    gagal = []
    for d in sorted((ROOT / "contoh").iterdir()):
        h = nf.urai((d / "tempelan.txt").read_text(encoding="utf-8"))
        r = ln.periksa(h.naskah, yaml.safe_load((d / "kartu-riset.yaml").read_text(encoding="utf-8"))) if h.naskah else {"galat": h.galat}
        if r["galat"]:
            gagal.append(d.name)
    c.append(_cek("contoh_lint", not gagal, "semua contoh lolos standar" if not gagal else f"contoh gagal lint: {gagal}"))
    if jalankan_test:
        r = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=ROOT, capture_output=True, text=True)
        c.append(_cek("test", r.returncode == 0, (r.stdout.strip().splitlines() or ["?"])[-1]))
    return {"lulus": all(x["lulus"] for x in c if x["penting"]), "cek": c}


if __name__ == "__main__":
    h = periksa(jalankan_test="--tanpa-test" not in sys.argv)
    for x in h["cek"]:
        print(f"{'✓' if x['lulus'] else '✗'} {x['nama']}: {x['keterangan']}")
    print("SIAP" if h["lulus"] else "BELUM SIAP")
    sys.exit(0 if h["lulus"] else 1)
