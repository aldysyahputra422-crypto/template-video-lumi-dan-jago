import json
import shutil
from pathlib import Path

import yaml

from scripts import lembar, naskah_format as nf, prompt_naskah as pn

ROOT = Path(__file__).resolve().parents[1]
CONTOH = ROOT / "contoh/tenggat-planning-fallacy"


def _folder(tmp_path):
    f = tmp_path / "rapat-bmc"
    f.mkdir()
    shutil.copy(CONTOH / "kartu-riset.yaml", f / "kartu-riset.yaml")
    return f


def test_prompt_memuat_semua_bahan(tmp_path):
    p = pn.buat(_folder(tmp_path), topik="tenggat tugas")
    k = yaml.safe_load((ROOT / "config/kosakata.yaml").read_text(encoding="utf-8"))
    for bagian in ("latar", "peran", "aksi", "props"):
        assert all(n in p for n in k[bagian]), bagian
    assert all(e in p for e in k["ekspresi"])
    assert all(f"`{s}`" in p for s in k["sisipan"]) and "SISIPAN:" in p and "geser" in p and "hook diam" in p.lower() or False
    assert "33.9" in p and "Buehler" in p and "tenggat tugas" in p and "rapat-bmc" in p
    assert "Ata" in p and "plester" in p
    for frasa in ("hook", "KARTU", "callback", "FAKTA", "@kata"):
        assert frasa in p, frasa
    assert "—" not in p


def test_contoh_di_prompt_lolos_parser(tmp_path):
    p = pn.buat(_folder(tmp_path))
    contoh = p.split("```text\n", 1)[1].split("```", 1)[0]
    assert nf.urai(contoh).galat == []


def test_prompt_tanpa_kartu_riset_ditolak(tmp_path, capsys):
    f = tmp_path / "kosong"
    f.mkdir()
    assert pn.main([str(f)]) == 3


def test_lembar_satu_suara_hanya_ucapan(tmp_path):
    f = _folder(tmp_path)
    shutil.copy(CONTOH / "tempelan.txt", f / "tempelan.txt")
    assert nf.main([str(f)]) == 0
    teks = lembar.tulis(f).read_text(encoding="utf-8")
    blok = teks.split("```text\n", 1)[1].split("```", 1)[0]
    assert blok.startswith("[curious]\nKamu bilang tugas ini kelar tiga hari.\n\n")   # tag di baris sendiri, siap tempel
    assert "[shouting]\nMalam tenggat" in blok
    assert (f / "lembar-elevenlabs.txt").read_text(encoding="utf-8") == blok   # versi teks polos untuk disalin
    for terlarang in ("LATAR", "AKSI", "@", "kamar", "TEKS"):
        assert terlarang not in blok, terlarang
    assert blok.count("\n\n") == 16 and blok.count("[") == sum(1 for b in blok.split("\n\n") if b.startswith("["))
    assert "suara.mp3" in teks and "belum terverifikasi" in teks.lower()


def test_contoh_prompt_adalah_patokan_root_cause(tmp_path):
    contoh = pn.buat(_folder(tmp_path)).split("```text\n", 1)[1].split("```", 1)[0]
    assert "akar masalah" in contoh and "kedai" in contoh and "jam_cepat" in contoh
