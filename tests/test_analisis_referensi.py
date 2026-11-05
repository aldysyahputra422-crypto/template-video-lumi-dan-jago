import json
import subprocess
from pathlib import Path

import pytest

from scripts import analisis_referensi as a


@pytest.fixture(scope="module")
def video(tmp_path_factory):
    """4 dtk 360x640 @24 fps: 2 dtk merah lalu 2 dtk biru (satu potongan keras di 2,0), audio sinus."""
    d = tmp_path_factory.mktemp("v")
    out = d / "uji.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y",
                    "-f", "lavfi", "-i", "color=c=red:s=360x640:r=24:d=2",
                    "-f", "lavfi", "-i", "color=c=blue:s=360x640:r=24:d=2",
                    "-f", "lavfi", "-i", "sine=frequency=440:duration=4",
                    "-filter_complex", "[0:v][1:v]concat=n=2:v=1:a=0[v]", "-map", "[v]", "-map", "2:a",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(out)], check=True)
    return out


def test_probe(video):
    p = a.probe(video)
    assert (p["lebar"], p["tinggi"], p["fps"]) == (360, 640, 24.0)
    assert 3.8 < p["durasi"] < 4.3 and p["ada_audio"] and p["ukuran_mb"] > 0


def test_potongan_keras_terdeteksi(video):
    t = a.potongan(video)
    assert len(t) == 1 and abs(t[0] - 2.0) < 0.1


def test_loudness(video):
    r = a.loudness(video)
    assert set(r) == {"lufs", "rentang_lu", "puncak_dbfs"} and r["lufs"] < 0 and r["puncak_dbfs"] <= 0


KATA = [{"k": "Kalau", "a": 0.0, "b": 0.3}, {"k": "kamar", "a": 0.3, "b": 0.6}, {"k": "kosong", "a": 0.6, "b": 1.0},
        {"k": "Tapi", "a": 2.0, "b": 2.3}, {"k": "tiap", "a": 2.3, "b": 2.6}, {"k": "hari", "a": 2.6, "b": 3.0}]


def test_statistik_kata():
    s = a.statistik_kata(KATA)
    assert s["jumlah_kata"] == 6 and s["kata_per_detik"] == 2.0
    assert s["jeda_terpanjang"] == 1.0 and s["jeda_di_atas_0_45"] == 1


def test_kalimat_dipecah_pada_jeda():
    k = a.kalimat(KATA)
    assert [x["teks"] for x in k] == ["Kalau kamar kosong", "Tapi tiap hari"]
    assert k[1]["mulai"] == 2.0 and k[1]["selesai"] == 3.0


def test_hook_tiga_detik_pertama():
    assert a.hook(KATA, 1.5) == "Kalau kamar kosong"


def test_analisis_lengkap_dengan_transkrip_palsu(video, tmp_path):
    h = a.analisis(video, tmp_path, transkrip_fn=lambda wav: KATA, lembar=True)
    assert (tmp_path / "analisis.json").exists() and (tmp_path / "lembar.png").exists()
    j = json.loads((tmp_path / "analisis.json").read_text())
    assert j["teknis"]["lebar"] == 360 and j["potongan_keras"]["jumlah"] == 1
    assert j["suara"]["jumlah_kata"] == 6 and j["hook"] == "Kalau kamar kosong Tapi tiap hari" and len(j["kalimat"]) == 2  # hook = 3 dtk pertama
    assert h == j


def test_cli_kode_salah_pakai(capsys):
    assert a.main([]) == 2
