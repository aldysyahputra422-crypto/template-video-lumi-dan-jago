import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
T = yaml.safe_load((ROOT / "config/tokoh.yaml").read_text(encoding="utf-8"))
WAJIB = {"nama", "arti_nama", "spesies", "peran", "kepribadian", "kelemahan_lucu", "gaya_bicara", "kalimat_khas",
         "ciri_wajib", "pose", "palet", "aturan_keras", "muncul_di"}


def test_satu_maskot_ata_lengkap():
    assert list(T["tokoh"]) == ["ata"]
    assert WAJIB <= set(T["tokoh"]["ata"])
    assert T["tokoh"]["ata"]["spesies"] == "panda merah"


def test_setiap_pose_punya_file_svg_dan_png():
    folder = ROOT / "aset/maskot/panda/pose"
    for nama in T["tokoh"]["ata"]["pose"]:
        assert (folder / f"{nama}.svg").exists() and (folder / f"{nama}.png").exists(), nama


def test_palet_hex_valid():
    for nama, hx in T["tokoh"]["ata"]["palet"].items():
        assert re.fullmatch(r"#[0-9A-Fa-f]{6}", hx), (nama, hx)


def test_ciri_wajib_dan_aturan_keras():
    ciri = " ".join(T["tokoh"]["ata"]["ciri_wajib"]).lower()
    assert "api" in ciri and "plester" in ciri
    aturan = " ".join(T["tokoh"]["ata"]["aturan_keras"]).lower()
    assert "situasi" in aturan and "legal" in aturan and "sumber" in aturan


def test_akun_tanpa_cta_dan_struktur_naskah():
    assert T["akun"]["cta"] is False and T["akun"]["kolaborasi"] == "@mentoringsobatambis"
    assert T["struktur_naskah"][0].startswith("hook") and any("konsep" in s for s in T["struktur_naskah"])


def test_tanpa_tanda_pisah_panjang():
    assert "—" not in (ROOT / "config/tokoh.yaml").read_text(encoding="utf-8")
