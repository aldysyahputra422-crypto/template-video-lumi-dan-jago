from pathlib import Path

import pytest
import yaml

from scripts import lint_naskah as ln
from scripts import naskah_format as nf

ROOT = Path(__file__).resolve().parents[1]
CONTOH = ROOT / "contoh/ep01-planning-fallacy"
TEKS = (CONTOH / "tempelan.txt").read_text(encoding="utf-8")
KARTU = yaml.safe_load((CONTOH / "kartu-riset.yaml").read_text(encoding="utf-8"))


def _lint(t=TEKS, kartu=KARTU):
    h = nf.urai(t)
    assert h.galat == [], [str(g) for g in h.galat]
    return ln.periksa(h.naskah, kartu)


def test_contoh_lolos_tanpa_galat():
    r = _lint()
    assert r["galat"] == [], r["galat"]
    assert 40 <= r["perkiraan_durasi"] <= 60


@pytest.mark.parametrize("teks,hasil", [
    ("Tahun 1994, 37 mahasiswa", [1994, 37]), ("Rata-rata nebak 34 hari", [34]), ("Kenyataannya 55 setengah", [55.5]),
    ("kenyataannya 1,6 kali", [1.6]), ("tiga puluh empat hari", [34]), ("lima puluh lima setengah", [55.5]),
    ("Satu, tulis. Dua, cek. Tiga, pakai angka", []), ("seribu sembilan ratus sembilan puluh empat", [1994]), ("sembilan belas sembilan puluh empat", [1994]), ("tiga belas", [13]),
])
def test_baca_angka(teks, hasil):
    assert ln.angka_dari_teks(teks) == hasil


def test_angka_fakta_harus_ada_di_kartu():
    r = _lint(TEKS.replace("Rata-rata nebak 34 hari.", "Rata-rata nebak 44 hari.").replace("@34", "@44"))
    assert any("44" in g["pesan"] and "kartu riset" in g["pesan"] for g in r["galat"])


def test_data_harus_cocok_kartu():
    r = _lint(TEKS.replace("Kenyataan=55.5 hari", "Kenyataan=65 hari"))
    assert any("65" in g["pesan"] for g in r["galat"])


def test_wajib_kartu_simpan():
    t = TEKS.replace("KARTU: Simpan ini | Tulis tebakanmu @tulis | Cek tugas mirip, beneran selesai berapa hari @cek | Pakai angka yang lebih besar (1,6x) @pakai\n", "")
    assert any("KARTU" in g["pesan"] for g in _lint(t)["galat"])


def test_hook_kepanjangan():
    t = TEKS.replace("UCAP: [curious] Kamu bilang tugas ini kelar tiga hari.",
                     "UCAP: [curious] Kamu bilang tugas ini pasti kelar tiga hari karena kamu merasa sudah sangat siap sekali.")
    assert any("hook" in g["pesan"] for g in _lint(t)["galat"])


def test_kata_kasar_dilarang():
    t = TEKS.replace("Otakmu barusan bohong.", "Otakmu barusan bohong, dasar bodoh.")
    assert any("bodoh" in g["pesan"] for g in _lint(t)["galat"])


def test_ketukan_tanpa_visual():
    t = TEKS.replace("TEKS: final_beneran.docx @beneran\nEKSPRESI: kamu capek @kesepuluh\n", "")
    assert any("visual" in g["pesan"] for g in _lint(t)["galat"])


def test_sumber_wajib_bila_ada_fakta():
    t = TEKS.replace("##SUMBER buehler1994\n", "")
    assert any("SUMBER" in g["pesan"] for g in _lint(t)["galat"])


def test_peringatan_callback_dan_pola_klise():
    t = TEKS.replace("UCAP: [laughs] Biar file-mu cukup satu nama, final.", "UCAP: [laughs] Rencana bukan harapan, tapi pengalaman.")
    t = t.replace("TEKS: final.docx @final\nPROPS: centang atas muncul @final\nEKSPRESI: kamu bangga @final", "EKSPRESI: kamu bangga @rencana")
    r = _lint(t)
    assert any("callback" in p["pesan"] for p in r["peringatan"])
