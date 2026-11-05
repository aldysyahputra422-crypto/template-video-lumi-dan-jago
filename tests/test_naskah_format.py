import json
from pathlib import Path

import jsonschema
import pytest

from scripts import naskah_format as nf

ROOT = Path(__file__).resolve().parents[1]
CONTOH = ROOT / "contoh/tenggat-planning-fallacy"
TEKS = (CONTOH / "tempelan.txt").read_text(encoding="utf-8")


def _ubah(lama, baru, t=TEKS):
    assert lama in t, lama
    return t.replace(lama, baru, 1)


def _baris(t, potongan):
    return next(i for i, b in enumerate(t.splitlines(), 1) if potongan in b)


def test_contoh_lolos_dan_sesuai_skema():
    h = nf.urai(TEKS)
    assert h.galat == [], [str(g) for g in h.galat]
    n = h.naskah
    jsonschema.validate(n, nf.SKEMA)
    assert n["id"] == "tenggat-tugas" and n["sumber"] == "buehler1994" and n["disetujui"] is False
    assert len(n["ketukan"]) == 17


def test_ucap_bersih_tag_terpisah():
    k = nf.urai(TEKS).naskah["ketukan"][0]
    assert k["ucap"] == "Kamu bilang tugas ini kelar tiga hari."
    assert k["tag"] == ["curious"] and k["ucap_el"] == "[curious] Kamu bilang tugas ini kelar tiga hari." and k["latar"] == "kamar"
    assert k["aktor"] == [{"id": "kamu", "peran": "pelajar", "posisi": "jauh_kiri", "ekspresi": "senang"}]
    assert k["aksi"][0] == {"id": "kamu", "aksi": "lari", "ke": "tengah", "kata": "bilang"}
    assert k["ata"] == {"pose": "mengintip", "tempat": "kanan", "masuk": "intip"}


def test_isyarat_kata_dan_data():
    ks = nf.urai(TEKS).naskah["ketukan"]
    assert {"label": "Tebakan rata-rata", "nilai": 33.9, "satuan": "hari", "kata": "34"} in ks[10]["data"]
    assert ks[13]["kartu"]["butir"][0] == {"teks": "Tulis tebakanmu", "kata": "tulis"}
    assert ks[9]["fakta"] is True and ks[10]["fakta"] is True and ks[2]["fakta"] is False   # ketukan ber-DATA otomatis fakta


def test_latar_mewarisi_ketukan_sebelumnya():
    ks = nf.urai(TEKS).naskah["ketukan"]
    assert ks[1]["latar"] == "kamar" and ks[8]["latar"] == "kosong" and ks[10]["latar"] == "perpustakaan"


@pytest.mark.parametrize("lama,baru,cari,potongan", [
    ("LATAR: kamar", "LATAR: planet_mars", "latar tidak dikenal", "planet_mars"),
    ("kamu sorak @kelar", "kamu terbang @kelar", "aksi tidak dikenal", "terbang"),
    ("PROPS: laptop tengah muncul @bikin", "PROPS: roket tengah muncul @bikin", "props tidak dikenal", "roket"),
    ("EKSPRESI: kamu kaget @bohong", "EKSPRESI: kamu histeris @bohong", "ekspresi tidak dikenal", "histeris"),
    ("UCAP: [curious] Kamu", "UCAP: [terrified] Kamu", "tag tidak dikenal", "terrified"),
    ("kamu sorak @kelar", "kamu sorak @libur", "@libur tidak ada", "@libur"),
    ("EKSPRESI: m3 takut @merinding", "EKSPRESI: siapa takut @merinding", "aktor belum ada", "siapa takut"),
    ("ATA: tertawa kanan pop", "ATA: kayang kanan pop", "pose ata tidak dikenal", "kayang"),
    ("Kamu nggak malas.", "Kamu nggak malas — sumpah.", "tanda pisah panjang", "sumpah"),
])
def test_galat_per_baris(lama, baru, cari, potongan):
    t = _ubah(lama, baru)
    h = nf.urai(t)
    g = [x for x in h.galat if cari in x.pesan]
    assert g, [str(x) for x in h.galat]
    assert g[0].baris == _baris(t, potongan)
    assert h.naskah is None


def test_aktor_hilang_saat_latar_berganti():
    t = _ubah("AKSI: kamu garuk_kepala @nebak", "AKSI: kamu garuk_kepala @nebak")
    t = _ubah("AKSI: m2 menunjuk @34", "AKSI: kamu menunjuk @34", t)   # 'kamu' tidak ada di perpustakaan
    assert any("aktor belum ada" in g.pesan for g in nf.urai(t).galat)


def test_toleran_gaya_chatgpt():
    t = "```\n" + TEKS.replace("UCAP:", "**UCAP:**").replace("LATAR:", "- LATAR:") + "\n```"
    assert nf.urai(t).galat == []


def test_cli_menulis_naskah_dan_koreksi(tmp_path, capsys):
    (tmp_path / "tempelan.txt").write_text(TEKS, encoding="utf-8")
    assert nf.main([str(tmp_path)]) == 0
    assert json.loads((tmp_path / "naskah.json").read_text())["id"] == "tenggat-tugas"
    (tmp_path / "tempelan.txt").write_text(_ubah("LATAR: kamar", "LATAR: planet_mars"), encoding="utf-8")
    assert nf.main([str(tmp_path)]) == 1
    assert "planet_mars" in (tmp_path / "koreksi-chatgpt.md").read_text()


def test_tidak_menimpa_naskah_disetujui(tmp_path):
    (tmp_path / "tempelan.txt").write_text(TEKS, encoding="utf-8")
    nf.main([str(tmp_path)])
    n = json.loads((tmp_path / "naskah.json").read_text())
    n["disetujui"] = True
    (tmp_path / "naskah.json").write_text(json.dumps(n))
    assert nf.main([str(tmp_path)]) == 7


def test_sisipan_dibaca_dan_divalidasi():
    h = nf.urai(TEKS)
    assert h.galat == [], [str(g) for g in h.galat]
    k = next(k for k in h.naskah["ketukan"] if (k["sisipan"] or {}).get("nama") == "hp_scroll")
    assert k["sisipan"] == {"nama": "hp_scroll", "isi": "kucing", "kata": "nonton"}
    jsonschema.validate(h.naskah, nf.SKEMA)
    assert any("sisipan tidak dikenal" in str(g) for g in nf.urai(_ubah("SISIPAN: hp_scroll kucing @nonton", "SISIPAN: hp_terbang")).galat)
    assert any("isi sisipan" in str(g) for g in nf.urai(_ubah("SISIPAN: hp_scroll kucing @nonton", "SISIPAN: hp_scroll naga")).galat)


def test_label_data_garis_bawah_jadi_spasi():
    t = _ubah("DATA: Tebakan rata-rata=33.9 hari @34", "DATA: tebakan_rata_rata=33.9 hari @34")
    k = next(k for k in nf.urai(t).naskah["ketukan"] if k["data"])
    assert k["data"][0]["label"] == "tebakan rata rata"
