---
description: "Periksa repo siap produksi di sesi ini (dependensi, render, font, SFX, skill, contoh, test). Tanpa argumen."
---

Jalankan `.venv/bin/python -m scripts.periksa_siap` (bila `.venv` belum ada: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt && npm install --prefix render` dulu). Sampaikan hasilnya ke pemilik apa adanya (baris ✓/✗ dan SIAP/BELUM SIAP). Untuk ✗, jalankan perbaikan yang tertulis di keterangannya lalu periksa sekali lagi. Lihat `docs/serah-terima.md`.
