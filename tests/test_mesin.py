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
