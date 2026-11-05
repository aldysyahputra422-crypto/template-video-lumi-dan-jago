"""Pustaka SFX: sintetis deterministik (bebas lisensi) + Mixkit terkatalog (diunduh, tidak masuk git)."""
import hashlib
from pathlib import Path

import soundfile as sf
import yaml

from scripts import sfx

ROOT = Path(__file__).resolve().parents[1]
KAT = yaml.safe_load((ROOT / "katalog/sfx.yaml").read_text(encoding="utf-8"))


def test_sintetis_lengkap_deterministik_dan_tidak_senyap(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    sfx.buat_sintetis(a)
    sfx.buat_sintetis(b)
    for nama in KAT["sfx"]:
        fa = a / f"{nama}.wav"
        assert fa.exists(), nama
        x, sr = sf.read(fa)
        assert 0.05 < len(x) / sr < 30 and abs(x).max() > 0.1, nama
        assert hashlib.md5(fa.read_bytes()).digest() == hashlib.md5((b / f"{nama}.wav").read_bytes()).digest(), nama
    for musik in KAT["musik"]:
        assert (a / f"{musik}.wav").exists(), musik


def test_katalog_mixkit_tercatat_lisensinya():
    lis = KAT["lisensi"]["mixkit"]
    assert lis["komersial"] is True and lis["atribusi"] is False and "disebarkan" in lis["larangan"]
    for nama, e in KAT["sfx"].items():
        if "mixkit" in e:
            assert str(e["mixkit"]).isdigit() and e.get("judul"), nama


def test_cari_file_utamakan_unduhan_lalu_sintetis(tmp_path):
    sin, und = tmp_path / "sin", tmp_path / "und"
    sin.mkdir(); und.mkdir()
    (sin / "pop.wav").write_bytes(b"x")
    p = tmp_path / "pemilik"
    p.mkdir()
    assert sfx.cari("pop", sintetis=sin, unduhan=und, pemilik=p) == sin / "pop.wav"
    (und / "pop.mp3").write_bytes(b"x")
    assert sfx.cari("pop", sintetis=sin, unduhan=und, pemilik=p) == und / "pop.mp3"
    assert sfx.cari("tidak_ada", sintetis=sin, unduhan=und, pemilik=p) is None
