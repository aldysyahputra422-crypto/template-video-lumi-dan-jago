"""Penjaga: setiap nama di config/kosakata.yaml harus diterapkan di render/mesin.html (dan sebaliknya)."""
import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
MESIN = (ROOT / "render/mesin.html").read_text(encoding="utf-8")
K = yaml.safe_load((ROOT / "config/kosakata.yaml").read_text(encoding="utf-8"))


def _kunci(nama_obj: str) -> set[str]:
    a = MESIN.index(f"const {nama_obj} = {{")
    b = MESIN.index("\n};", a)
    return set(re.findall(r"^\s{2}(\w+):", MESIN[a:b], re.M)) | set(re.findall(r"[{,]\s*(\w+):\s*(?:\{|r =>|t =>|\(|\(\))", MESIN[a:b]))


@pytest.mark.parametrize("bagian,obj", [("latar", "LATAR"), ("peran", "PERAN"), ("ekspresi", "EKSPRESI"), ("aksi", "AKSI"), ("props", "PROPS"), ("sisipan", "SISIPAN")])
def test_kosakata_sama_dengan_mesin(bagian, obj):
    nama = set(K[bagian]) if isinstance(K[bagian], dict) else set(K[bagian])
    di_mesin = _kunci(obj)
    assert nama <= di_mesin, f"belum ada di mesin: {sorted(nama - di_mesin)}"
    if bagian == "sisipan":
        assert di_mesin <= nama, f"di mesin tapi tidak di kosakata: {sorted(di_mesin - nama)}"


def test_posisi_dan_pose_ata():
    for p in K["posisi"]:
        assert f"{p}:" in MESIN
    pose = yaml.safe_load((ROOT / "config/tokoh.yaml").read_text(encoding="utf-8"))["tokoh"]["ata"]["pose"]
    assert all(f"'{p}'" in MESIN for p in pose)


def test_aktor_beda_peran_sama_dapat_warna_beda():
    """Dua 'pelajar' (mis. Dinda dan Bima) harus bisa dibedakan penonton: varian warna per aktor, urut kemunculan."""
    assert "const VARIAN_BAJU" in MESIN and "warnaAktor(" in MESIN
    a = MESIN.index("const VARIAN_BAJU")
    assert MESIN[a:MESIN.index("\n", a)].count("#") >= 4


def test_kostum_sesuai_profesi_dan_gender():
    """Masukan pemilik: Dinda (cewek) berseragam putih, dokter berjas dokter, petani berpakaian petani."""
    for peran in ("siswa", "siswi", "siswi_kerudung", "mahasiswi", "dokter", "petani", "pengusaha"):
        assert peran in K["peran"], peran
    a = MESIN.index("const PERAN = {")
    blok = MESIN[a:MESIN.index("\n};", a)]
    for peran, ciri in (("siswi", "rambut: 'panjang'"), ("siswi_kerudung", "rambut: 'kerudung'"), ("dokter", "jas:"), ("dokter", "stetoskop"),
                        ("petani", "caping"), ("pengusaha", "dasi:"), ("siswa", "celana:")):
        baris = next(l for l in blok.splitlines() if l.strip().startswith(peran + ":"))
        assert ciri in baris, (peran, ciri)


def test_tangan_dan_tokoh_penonton():
    for s in ("tangan_ambil", "tangan_beri", "tangan_tulis"):
        assert s in K["sisipan"], s
    assert "kamu" in K["peran"]
    a = MESIN.index("const PERAN = {")
    baris = next(l for l in MESIN[a:MESIN.index("\n};", a)].splitlines() if l.strip().startswith("kamu:"))
    assert "kepala: 'kuning'" in baris


def test_setiap_props_punya_letak_alami():
    """Masukan pemilik: buku malah di bawah meja. Setiap props wajib punya kategori letak (lantai, meja, dinding, ikon)."""
    a = MESIN.index("const LETAK_PROPS = {")
    blok = MESIN[a:MESIN.index("};", a)]
    kategori = dict(re.findall(r"(\w+): '(lantai|meja|dinding|ikon)'", blok))
    assert set(K["props"]) <= set(kategori), sorted(set(K["props"]) - set(kategori))


def test_ekspresi_punya_tanda_emosi():
    """Masukan pemilik: ekspresi bingung terlihat datar. Ekspresi kuat diberi tanda emosi yang terbaca di bidikan lebar."""
    a = MESIN.index("const TANDA_EMOSI = {")
    blok = MESIN[a:MESIN.index("\n};", a)]
    for e in ("bingung", "kaget", "takut", "marah", "sedih", "capek", "malu"):
        assert re.search(rf"^\s+{e}:", blok, re.M), e


def test_figuran_hanya_di_tempat_ramai():
    a = MESIN.index("const FIGURAN = {")
    tempat = set(re.findall(r"(\w+):", MESIN[a:MESIN.index("};", a)]))
    assert tempat <= {"pasar", "kota", "jalan"}, tempat


def test_suasana_sama_dengan_mesin():
    a = MESIN.index("const SUASANA = {")
    di_mesin = set(re.findall(r"^\s{2}(\w+):", MESIN[a:MESIN.index("\n};", a)], re.M))
    assert set(K["suasana"]) == di_mesin
