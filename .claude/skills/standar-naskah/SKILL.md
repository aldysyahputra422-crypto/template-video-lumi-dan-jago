---
name: standar-naskah
description: Standar naskah video Ata (berguna sampai disimpan, tapi tidak membosankan). Pakai saat menilai, menyunting, atau menulis contoh naskah, dan saat pemilik bertanya kenapa naskah ditolak.
---

# Standar naskah Ata

Sebagian besar diperiksa otomatis oleh `scripts/lint_naskah.py`. Skill ini untuk penilaian yang tidak bisa dihitung.

## Tujuh syarat (diperiksa program)
1. Hook di ketukan pertama, maksimal 10 kata, menyapa "kamu" atau membalik dugaan; premis lengkap di kalimat pertama.
2. Cerita orang kedua yang dekat dengan pelajar (atau alegori singkat untuk konsep abstrak), minimal dua detail spesifik yang lucu, dan meningkat.
3. Momen penamaan konsep sesudah cerita, definisi satu kalimat.
4. Angka nyata HANYA dari `kartu-riset.yaml`, kontras jelas, ketukannya ditandai `FAKTA: ya`.
5. Tepat satu `KARTU`, maksimal 3 langkah konkret yang bisa dipakai hari ini. Tanpa ajakan simpan, bagikan, follow, atau komen (terasa jualan); judul KARTU netral.
6. Penutup callback ke lelucon atau hook awal; pola "bukan X, tapi Y" maksimal sekali.
7. 40 sampai 55 detik; satu ketukan maksimal 16 kata supaya visual berganti tiap 2 sampai 5 detik.

## Topik
Pilar: skill yang tidak diajarkan di sekolah atau kampus, dan komponen lomba. Uji perhatian: klaim provokatif atau menyalahi dugaan, kegagalan yang dekat dengan penonton, tidak bisa ditebak dari judul. Lihat `docs/strategi-topik.md`.

## Penilaian manusia (tidak dihitung program)
- Apakah detailnya benar-benar dialami penonton (contoh baik: nama file "final_beneran_revisi_fix")? Detail generik ("lalu tukang sakit, lalu batu kurang") = membosankan.
- Apakah setiap ketukan menaikkan taruhan atau tawa? Daftar datar = gagal.
- Apakah langkah di KARTU bisa dilakukan tanpa alat atau biaya, hari ini?
- Apakah Ata hanya meledek situasi, tidak pernah penonton?
- Apakah klaim di cerita tidak melebihi temuan makalah (lihat `batas` di kartu riset)?

## Contoh yang lolos
`contoh/ep02-root-cause/tempelan.txt` (patokan alur: cerita gagal, bertanya sampai akar, teori, kritik, trik, callback). Contoh lain: `contoh/ep01-planning-fallacy/tempelan.txt`.
