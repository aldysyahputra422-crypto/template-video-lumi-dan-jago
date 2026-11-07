import json
import subprocess

from scripts import tempo


def _nada(p, detik):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"sine=frequency=220:duration={detik}", str(p)], check=True)


def _naskah(folder, jumlah_kata):
    ucap = " ".join(["kata"] * jumlah_kata)
    (folder / "naskah.json").write_text(json.dumps({"ketukan": [{"no": 1, "ucap": ucap}]}), encoding="utf-8")


def test_suara_lambat_dipercepat_lokal(tmp_path):
    _naskah(tmp_path, 54)            # 54 kata pada 2,0 kata/dtk = 27 dtk; sasaran 2,7 kata/dtk = 20 dtk
    _nada(tmp_path / "suara.mp3", 27)
    h = tempo.sesuaikan(tmp_path)
    assert h["diubah"] and 1.3 < h["faktor"] <= 1.35
    assert (tmp_path / "suara-asli.mp3").exists() and (tmp_path / "suara.wav").exists()
    assert not (tmp_path / "suara.mp3").exists()
    assert 19.5 < tempo.durasi(tmp_path / "suara.wav") < 21.5     # 27 / 1,35 = 20 dtk


def test_suara_sudah_cepat_tidak_disentuh_dan_idempoten(tmp_path):
    _naskah(tmp_path, 54)
    _nada(tmp_path / "suara.mp3", 19)
    assert tempo.sesuaikan(tmp_path)["diubah"] is False
    assert (tmp_path / "suara.mp3").exists()
    _nada(tmp_path / "suara.mp3", 27)
    assert tempo.sesuaikan(tmp_path)["diubah"] is True
    assert tempo.sesuaikan(tmp_path)["diubah"] is False           # sudah diproses: tidak dipercepat dua kali


def test_suara_pengganti_diproses_ulang(tmp_path):
    _naskah(tmp_path, 54)
    _nada(tmp_path / "suara.mp3", 27)
    tempo.sesuaikan(tmp_path)
    _nada(tmp_path / "suara.mp3", 30)                               # pemilik merekam ulang
    h = tempo.sesuaikan(tmp_path)
    assert h["diubah"] is True and (tmp_path / "suara-asli.mp3").exists()
