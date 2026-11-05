"""Kemas dua skill portabel: naskah-reels (MD saja) dan olah-reels (MD + mesin produksi, profil filosofi, tanpa Ata)."""
import re
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
    assert tokoh["akun"]["nama_akun"] == "@ata.ngulik" and set(tokoh) == {"akun"}
    teks = [o.read(x).decode() for x in nama if x.endswith((".md", ".yaml"))] + [n.read(x).decode() for x in n.namelist()]
    assert not any(re.search(r"\bAta\b|panda|maskot Ata", x) for x in teks)
    bm = n.read("naskah-reels/benchmark.md").decode()
    assert "Kerangka DNA" in bm and "P3" in bm and "`benchmark.md`" in md


def test_naskah_wajib_lembar_elevenlabs_dan_topik(tmp_path):
    hasil = ks.kemas(tmp_path)
    md = zipfile.ZipFile(hasil["naskah-reels"]).read("naskah-reels/SKILL.md").decode()
    assert "lembar ElevenLabs" in md and "topik-reels" in md
    contoh = (ks.ROOT / "skills/naskah-reels/contoh-sunk-cost.txt").read_text(encoding="utf-8")
    lembar = ks.lembar_dari_teks(contoh)
    blok = lembar.split("\n\n")
    assert len(blok) == contoh.count("UCAP:") and all(re.fullmatch(r"\[[a-z ]+\]\n[^\[\n]+", b) for b in blok)
    assert lembar in md
    tp = zipfile.ZipFile(hasil["topik-reels"]).read("topik-reels/SKILL.md").decode()
    assert tp.startswith("---\nname: topik-reels") and "TOPIK:" in tp and "SKOR" in tp


def test_parser_abaikan_lembar_sesudah_akhir(tmp_path):
    from scripts import naskah_format as nf
    contoh = (ks.ROOT / "skills/naskah-reels/contoh-sunk-cost.txt").read_text(encoding="utf-8")
    (tmp_path / "tempelan.txt").write_text(contoh + "\n\n" + ks.lembar_dari_teks(contoh) + "\n", encoding="utf-8")
    kode, galat, _ = nf.proses(tmp_path)
    assert kode == 0, galat


def test_mesin_paket_tanpa_maskot_dan_latar_lama(tmp_path):
    o = zipfile.ZipFile(ks.kemas(tmp_path)["olah-reels"])
    html = o.read("olah-reels/mesin/render/mesin.html").decode()
    assert not re.search(r"panda|POSE_ATA|ataA|id=\"ata\"|perpustakaan:|kamar:|kelas:", html)
    assert "kosong: t =>" in html and "function stickman" in html
    kos = yaml.safe_load(o.read("olah-reels/mesin/config/kosakata.yaml"))
    assert list(kos["latar"]) == ["kosong"] and "ata_tempat" not in kos
    assert not any(x.endswith(("gambar_jago_datar.py", "potong_pose.py")) for x in o.namelist())


def test_skill_memuat_totalitas_visual(tmp_path):
    hasil = ks.kemas(tmp_path)
    md = zipfile.ZipFile(hasil["naskah-reels"]).read("naskah-reels/SKILL.md").decode()
    assert "Totalitas visual" in md and "raksasa" in md and "panggung|tinggi|naikNNN" in md and "ilmuwan" in md
    o = zipfile.ZipFile(hasil["olah-reels"])
    olah = o.read("olah-reels/SKILL.md").decode()
    assert "motion_blur" in olah and "kepalaPenonton" in olah and "tanganBoneka" in olah
    html = o.read("olah-reels/mesin/render/mesin.html").decode()
    assert "function tanganBoneka" in html and "lapisLatar" in html
