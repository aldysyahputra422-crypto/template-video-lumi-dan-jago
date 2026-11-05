import re
from pathlib import Path

import pytest
import yaml

from scripts import lint_naskah as ln
from scripts import naskah_format as nf

ROOT = Path(__file__).resolve().parents[1]
CONTOH = ROOT / "contoh/tenggat-planning-fallacy"
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


PROFIL_ATA = {"wajib_kartu": True, "maskot": "Ata"}


def test_wajib_kartu_simpan(monkeypatch):
    monkeypatch.setattr(ln, "_profil", lambda: PROFIL_ATA)
    t = TEKS.replace("KARTU: Triknya | Tulis tebakanmu @tulis | Cek tugas mirip, beneran selesai berapa hari @cek | Pakai angka yang lebih besar (1,6x) @pakai\n", "")
    assert any("KARTU" in g["pesan"] for g in _lint(t)["galat"])


def test_hook_kepanjangan():
    t = TEKS.replace("UCAP: [curious] Kamu bilang tugas ini kelar tiga hari.",
                     "UCAP: [curious] Kamu bilang tugas ini pasti kelar tiga hari karena kamu merasa sudah sangat siap sekali.")
    assert any("hook" in g["pesan"] for g in _lint(t)["galat"])


def test_kata_kasar_dilarang():
    t = TEKS.replace("Otakmu barusan bohong.", "Otakmu barusan bohong, dasar bodoh.")
    assert any("bodoh" in g["pesan"] for g in _lint(t)["galat"])


def test_ketukan_tanpa_visual():
    t = TEKS.replace("TEKS: final_beneran.docx @beneran\nEKSPRESI: kamu capek @kesepuluh\nKAMERA: dekat kamu\n", "")
    assert any("visual" in g["pesan"] for g in _lint(t)["galat"])


def test_sumber_wajib_bila_ada_fakta():
    t = TEKS.replace("##SUMBER buehler1994\n", "")
    assert any("SUMBER" in g["pesan"] for g in _lint(t)["galat"])


def test_peringatan_callback_dan_pola_klise(monkeypatch):
    monkeypatch.setattr(ln, "_profil", lambda: PROFIL_ATA)
    t = TEKS.replace("UCAP: [laughs] Biar file-mu cukup satu nama, final.", "UCAP: [laughs] Rencana bukan harapan, tapi pengalaman.")
    t = t.replace("TEKS: final.docx @final\nPROPS: centang atas muncul @final\nEKSPRESI: kamu bangga @final", "EKSPRESI: kamu bangga @rencana")
    r = _lint(t)
    assert any("callback" in p["pesan"] for p in r["peringatan"])


@pytest.mark.parametrize("kalimat", ["Jadi simpan ini.", "Share ke temanmu ya.", "Jangan lupa follow."])
def test_ajakan_jualan_ditolak(kalimat):
    t = TEKS.replace("UCAP: Triknya cuma tiga.", f"UCAP: {kalimat}")
    assert any("ajakan" in g["pesan"] for g in _lint(t)["galat"])


def test_kartu_berjudul_ajakan_ditolak():
    t = TEKS.replace("KARTU: Triknya |", "KARTU: Simpan ini |")
    assert any("ajakan" in g["pesan"] for g in _lint(t)["galat"])


def test_patokan_root_cause_lolos_tanpa_peringatan():
    d = ROOT / "contoh/kedai-5whys"
    n = nf.urai((d / "tempelan.txt").read_text(encoding="utf-8")).naskah
    r = ln.periksa(n, yaml.safe_load((d / "kartu-riset.yaml").read_text(encoding="utf-8")))
    assert r["galat"] == [] and r["peringatan"] == []


def _statis(t):
    """Buang semua penanda perubahan komposisi dari naskah contoh."""
    t = re.sub(r"^(KAMERA|SISIPAN):.*\n", "", t, flags=re.M)
    return re.sub(r" (lari|lompat)\b", " sorak", re.sub(r" ke \w+", "", t))


def test_hook_wajib_gerak_besar_atau_sisipan():
    r = _lint(_statis(TEKS))
    assert any("hook diam" in g["pesan"] for g in r["galat"])


def test_tiga_ketukan_berturut_komposisi_sama_ditolak():
    r = _lint(_statis(TEKS))
    assert any("kaku" in g["pesan"] for g in r["galat"])


def test_ata_tidak_boleh_muncul_di_adegan_ramai():
    t = TEKS.replace("SISIPAN: hp_scroll kucing @nonton\n", "SISIPAN: hp_scroll kucing @nonton\nATA: kaget kanan pop\n")
    assert any("Ata" in g["pesan"] and "ramai" in g["pesan"] for g in _lint(t)["galat"])


def test_kalimat_pembuka_berulang_ditolak():
    r = ln.periksa({"id": "x", "sumber": None, "ketukan": [
        dict(k, ucap=f"Kenapa {k['ucap']}") if 2 <= i <= 5 else k for i, k in enumerate(nf.urai(TEKS).naskah["ketukan"])]}, KARTU)
    assert any("mudah ditebak" in g["pesan"] for g in r["galat"])


def test_nama_konsep_terlalu_awal_ditolak():
    kartu = dict(KARTU, nama_konsep=["Otakmu"])
    assert any("nama konsep" in g["pesan"] for g in _lint(kartu=kartu)["galat"])


@pytest.mark.parametrize("kalimat", ["Larsen dkk. (2009) menguji 40 orang.", "Hasilnya 39%/26% saja.", "Skor tes_berulang naik."])
def test_ucap_yang_tidak_bisa_diucapkan_ditolak(kalimat):
    t = TEKS.replace("UCAP: [deadpan] Otakmu barusan bohong.", f"UCAP: {kalimat}")
    t = t.replace("@bohong", "@" + kalimat.split()[0].lower())
    assert any("diucapkan" in g["pesan"] for g in _lint(t)["galat"])


def test_kalimat_tanpa_tag_ekspresi_diperingatkan():
    t = TEKS.replace("UCAP: [deadpan] Otakmu barusan bohong.", "UCAP: Otakmu barusan bohong.")
    assert any("tag ekspresi" in p["pesan"] for p in _lint(t)["peringatan"])


def test_saran_keluar_menyebut_aktor_yang_bukan_tokoh_ketukan():
    n = nf.urai(TEKS).naskah
    k = n["ketukan"][-1]
    k["ata"] = {"pose": "tertawa", "tempat": "kanan", "masuk": "pop"}
    k["aktor"] = [{"id": "kamu", "peran": "pelajar", "posisi": "tengah", "ekspresi": "senang"}, {"id": "x", "peran": "guru", "posisi": "kanan", "ekspresi": "datar"}]
    k["aktor"] = k["aktor"][:1]
    sebelum = n["ketukan"][-2]
    sebelum["aktor"] = sebelum["aktor"] + [{"id": "x", "peran": "guru", "posisi": "kanan", "ekspresi": "datar"}]
    g = [x["pesan"] for x in ln.periksa(n, KARTU)["galat"] if "Ata dipaksa" in x["pesan"]]
    assert g and "KELUAR: x" in g[0]


def test_profil_filosofi_tanpa_kartu_dan_tanpa_ata(monkeypatch):
    """Profil 'filosofi' (formula mindwander): tidak wajib KARTU trik dan tidak meminta Ata."""
    t = re.sub(r"^KARTU:.*\n", "", TEKS, flags=re.M)
    t = re.sub(r"^ATA:.*\n", "", t, flags=re.M)
    monkeypatch.setattr(ln, "_profil", lambda: PROFIL_ATA)
    assert any("KARTU" in g["pesan"] for g in _lint(t)["galat"])                    # profil ata (lama)
    monkeypatch.setattr(nf, "profil", lambda: {"wajib_kartu": False, "maskot": None, "latar_bawaan": True})   # filosofi; fixture memakai latar bawaan
    monkeypatch.setattr(ln, "_profil", lambda: {"wajib_kartu": False, "maskot": None})
    r = _lint(t)
    assert not any("KARTU" in g["pesan"] for g in r["galat"]) and not any("Ata" in p["pesan"] for p in r["peringatan"])


def test_sisipan_dihitung_sebagai_visual():
    n = nf.urai(TEKS).naskah
    k = n["ketukan"][4]
    for f in ("aksi", "ekspresi", "props", "teks", "data"):
        k[f] = []
    k["kartu"] = k["ata"] = k["kamera"] = None
    k["aktor"] = []
    k["sisipan"] = {"nama": "jam_cepat", "isi": None, "kata": None}
    assert not any(f"ketukan {k['no']} tanpa isyarat visual" in g["pesan"] for g in ln.periksa(n, KARTU)["galat"])
