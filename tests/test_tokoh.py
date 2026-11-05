import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
T = yaml.safe_load((ROOT / "config/tokoh.yaml").read_text(encoding="utf-8"))
WAJIB = {"nama", "arti_nama", "warna", "peran", "membawa", "falsafah", "kepribadian", "kelemahan_lucu", "gaya_bicara",
         "kalimat_khas", "gestur_khas", "ciri_wajib", "ekspresi", "palet"}


def test_dua_tokoh_lengkap():
    for k in ("lumi", "jago"):
        assert WAJIB <= set(T["tokoh"][k]), k
        assert len(T["tokoh"][k]["ekspresi"]) == 6, k
        assert T["tokoh"][k]["ciri_wajib"], k


def test_palet_hex_valid():
    for k in ("lumi", "jago"):
        for nama, hx in T["tokoh"][k]["palet"].items():
            assert re.fullmatch(r"#[0-9A-Fa-f]{6}", hx), (k, nama, hx)


def test_aturan_keras_jago_empat():
    assert len(T["tokoh"]["jago"]["aturan_keras"]) == 4
    assert any("meledek" in a.lower() and "situasi" in a.lower() for a in T["tokoh"]["jago"]["aturan_keras"])


def test_pola_dialog_tiga_ketukan_dan_aturan_akun_tanpa_cta():
    assert T["dinamika"]["pola"] == ["Jago meledek", "Lumi meluruskan", "Jago membocorkan trik legal"]
    assert T["akun"]["cta"] is False and T["akun"]["kolaborasi"] == "@mentoringsobatambis"


def test_tanpa_tanda_pisah_panjang():
    assert "—" not in (ROOT / "config/tokoh.yaml").read_text(encoding="utf-8")
