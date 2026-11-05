---
name: standar-naskah
description: Standar naskah video Ata (berguna sampai disimpan, tapi tidak membosankan). Pakai saat menilai, menyunting, atau menulis contoh naskah, dan saat pemilik bertanya kenapa naskah ditolak.
---

# Standar naskah Ata

Sebagian besar diperiksa otomatis oleh `scripts/lint_naskah.py`. Skill ini untuk penilaian yang tidak bisa dihitung.

## Syarat (diperiksa program)
1. Hook di ketukan pertama, maksimal 10 kata, menyapa "kamu" atau membalik dugaan; premis lengkap di kalimat pertama.
2. Cerita orang kedua yang dekat dengan pelajar (atau alegori singkat untuk konsep abstrak), minimal dua detail spesifik yang lucu, dan meningkat.
3. Momen penamaan konsep sesudah cerita, definisi satu kalimat.
4. Angka nyata HANYA dari `kartu-riset.yaml`, kontras jelas, ketukannya ditandai `FAKTA: ya`.
5. Tepat satu `KARTU`, maksimal 3 langkah konkret yang bisa dipakai hari ini. Tanpa ajakan simpan, bagikan, follow, atau komen (terasa jualan); judul KARTU netral.
6. Penutup callback ke lelucon atau hook awal; pola "bukan X, tapi Y" maksimal sekali.
7. 40 sampai 55 detik; satu ketukan maksimal 16 kata supaya visual berganti tiap 2 sampai 5 detik.
8. Tidak kaku: detik pertama wajib gerak besar (SISIPAN, atau aktor masuk/pindah/lari/lompat); komposisi berganti paling lambat tiap 2 ketukan (kamera dekat/geser/dorong, aktor pindah, latar, SISIPAN). Aktor yang berdiri di satu tempat lama dengan gerak sederhana = ditolak.
9. Kata yang bisa digambar, digambar harfiah dengan SISIPAN (minimal 2): "scroll video kucing" berarti HP muncul dan feed kucing benar-benar digulir, bukan ikon kucing kecil. Sumber jurnal tidak tampil di layar.
10. Ata hanya di ketukan lapang (maksimal 1 aktor, tanpa SISIPAN/KARTU/DATA), maksimal 3 kali; mesin juga menyembunyikannya otomatis di adegan ramai.
11. Tidak mudah ditebak: nama konsep (`nama_konsep` di kartu riset) baru disebut sesudah 40% naskah; 4 ketukan berturut dengan kata pembuka sama ditolak.

## Cara bercerita (pola video referensi 03, dinilai manusia)
- Penonton harus ikut tertipu seperti tokohnya. Tanam petunjuk sejak awal (benda di layar, detail sambil lalu), lalu satu putaran sederhana membalik arti kejadian sebelumnya. Contoh baik: kerumunan di hook lewat saat kedai belum buka; jam di layar sudah menunjukkan pukul tujuh.
- Jangan memperagakan teori sebelum putaran. "Kenapa?" lima kali untuk menjelaskan 5 Whys = penonton yang paham sudah tahu jawabannya.
- Satu kalimat pembalik sesudah putaran ("Raja tidak sedang memberi, hanya mengembalikan"), baru nama konsep.
- Tutup dengan pemetaan ke dunia penonton (tugas, lomba) lalu callback.

## Topik
Pilar: skill yang tidak diajarkan di sekolah atau kampus, dan komponen lomba. Uji perhatian: klaim provokatif atau menyalahi dugaan, kegagalan yang dekat dengan penonton, tidak bisa ditebak dari judul. Lihat `docs/strategi-topik.md`.

## Penilaian manusia (tidak dihitung program)
- Apakah detailnya benar-benar dialami penonton (contoh baik: nama file "final_beneran_revisi_fix")? Detail generik ("lalu tukang sakit, lalu batu kurang") = membosankan.
- Apakah setiap ketukan menaikkan taruhan atau tawa? Daftar datar = gagal.
- Apakah langkah di KARTU bisa dilakukan tanpa alat atau biaya, hari ini?
- Apakah Ata hanya meledek situasi, tidak pernah penonton?
- Apakah klaim di cerita tidak melebihi temuan makalah (lihat `batas` di kartu riset)?

## Contoh yang lolos
`contoh/kedai-5whys/tempelan.txt` (patokan alur: cerita gagal, bertanya sampai akar, teori, kritik, trik, callback). Contoh lain: `contoh/tenggat-planning-fallacy/tempelan.txt`.
