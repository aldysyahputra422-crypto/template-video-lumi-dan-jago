"""Periksa siap pakai (untuk sesi baru di akun utama): daftar centang, kode 0 hanya bila semua penting lulus."""
from scripts import periksa_siap as ps


def test_daftar_periksa_lengkap_dan_lulus_di_repo_ini():
    h = ps.periksa(jalankan_test=False)
    nama = {c["nama"] for c in h["cek"]}
    for wajib in ("python", "ffmpeg", "node_playwright", "font", "pose_ata", "sfx", "skill", "contoh_lint"):
        assert wajib in nama, wajib
    assert all(set(c) >= {"nama", "lulus", "keterangan"} for c in h["cek"])
    assert h["lulus"], [c for c in h["cek"] if not c["lulus"]]
