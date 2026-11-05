import re
from pathlib import Path

import pytest

from scripts import bersihkan_svg as b

ROOT = Path(__file__).resolve().parents[1]
ASLI = ROOT / "aset/maskot/asli"


def _jumlah_path(svg: str) -> int:
    return len(re.findall(r"<path\b", svg))


@pytest.mark.parametrize("nama", ["lumi", "jago"])
def test_buang_bingkai_putih_maskot_asli(nama):
    svg = (ASLI / f"{nama}.svg").read_text(encoding="utf-8")
    bersih = b.buang_bingkai(svg)
    assert _jumlah_path(bersih) == _jumlah_path(svg) - 1
    assert b.punya_bingkai(svg) and not b.punya_bingkai(bersih)


def test_tidak_mengubah_svg_tanpa_bingkai():
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"><path d="M10,10 L50,10 L50,50 Z" fill="red"/></svg>'
    assert b.buang_bingkai(svg) == svg


def test_hanya_path_pertama_yang_dibuang():
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">'
           '<path d="M0,100 L0,0 L100,0 L100,100 Z" fill="white"/>'
           '<path d="M0,100 L0,0 L100,0 L100,100 Z" fill="blue"/></svg>')
    assert _jumlah_path(b.buang_bingkai(svg)) == 1 and "blue" in b.buang_bingkai(svg)


def test_hasil_xml_valid(tmp_path):
    import xml.etree.ElementTree as ET
    for nama in ("lumi", "jago"):
        ET.fromstring(b.buang_bingkai((ASLI / f"{nama}.svg").read_text(encoding="utf-8")))


def test_cli_menulis_berkas_bersih(tmp_path):
    keluar = tmp_path / "lumi.svg"
    assert b.main([str(ASLI / "lumi.svg"), str(keluar)]) == 0
    assert not b.punya_bingkai(keluar.read_text(encoding="utf-8"))


def _svg(*isi):
    return '<svg xmlns="http://www.w3.org/2000/svg" width="2000" height="2000">' + "".join(isi) + "</svg>"


PUTIH_BESAR = '<path d="M100,100 L300,100 L300,300 L100,300 Z" fill="rgb(254, 254, 254)"/>'
PUTIH_KECIL = '<path d="M100,100 L120,100 L120,115 L100,115 Z" fill="rgb(255,255,255)"/>'
KRIM_BESAR = '<path d="M100,100 L300,100 L300,300 L100,300 Z" fill="rgb(253,238,224)"/>'


def test_pulau_putih_besar_dibuang_kilau_kecil_dan_krim_disimpan():
    svg = _svg(PUTIH_BESAR, PUTIH_KECIL, KRIM_BESAR)
    bersih = b.buang_pulau_putih(svg)
    assert _jumlah_path(bersih) == 2 and "255,255,255" in bersih and "253,238,224" in bersih and "254, 254, 254" not in bersih


@pytest.mark.parametrize("nama,dibuang", [("lumi", 1), ("jago", 2)])
def test_pulau_putih_maskot_asli(nama, dibuang):
    svg = b.buang_bingkai((ASLI / f"{nama}.svg").read_text(encoding="utf-8"))
    assert _jumlah_path(svg) - _jumlah_path(b.buang_pulau_putih(svg)) == dibuang


def test_bersihkan_gabungan_dan_cli(tmp_path):
    keluar = tmp_path / "jago.svg"
    assert b.main([str(ASLI / "jago.svg"), str(keluar)]) == 0
    asli = (ASLI / "jago.svg").read_text(encoding="utf-8")
    assert _jumlah_path(keluar.read_text(encoding="utf-8")) == _jumlah_path(asli) - 3
