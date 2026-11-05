"""Kemas dua skill portabel: naskah-reels (MD saja) dan olah-reels (MD + mesin produksi, profil filosofi, tanpa Ata)."""
import zipfile

import yaml

from scripts import kemas_skill as ks


def test_kemas_dua_skill(tmp_path):
    hasil = ks.kemas(tmp_path)
    n = zipfile.ZipFile(hasil["naskah-reels"])
    md = n.read("naskah-reels/SKILL.md").decode()
    assert md.startswith("---\nname: naskah-reels") and "{{" not in md and "##ASET" in md and "jembatan" in md and "jam_cepat" in md
    o = zipfile.ZipFile(hasil["olah-reels"])
    nama = o.namelist()
    assert "olah-reels/SKILL.md" in nama and "olah-reels/mesin/scripts/olah.py" in nama and "olah-reels/mesin/render/mesin.html" in nama
    assert "olah-reels/mesin/docs/gaya-visual.md" in nama and "olah-reels/mesin/requirements.txt" in nama
    assert not any("node_modules" in x or "/video/" in x or ".venv" in x or "__pycache__" in x or "transkrip" in x for x in nama)
    gaya = yaml.safe_load(o.read("olah-reels/mesin/config/gaya.yaml"))
    assert gaya["naskah"]["profil"] == "filosofi"
    tokoh = yaml.safe_load(o.read("olah-reels/mesin/config/tokoh.yaml"))
    assert tokoh["akun"]["nama_akun"] == "@akunmu"
