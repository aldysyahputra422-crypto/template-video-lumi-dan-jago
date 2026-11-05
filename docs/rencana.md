# Rencana

## Tujuan
Dua maskot sebagai narator video pendek. Hemat token dan konsisten: semua yang mekanis dikerjakan script; Claude tidak "mengarang ulang" gaya tiap video.

## Urutan kerja
1. **Fondasi** (selesai): aset maskot bersih, aturan kerja, draf kepribadian.
2. **Analisis referensi**: pemilik mengirim 10+ video referensi (file, bukan link) beserta data tayangan (views 7 hari, tanggal, platform). Script mengekstrak frame, deteksi potongan, dan transkrip berkata-waktu, lalu menulis angka gaya ke `gaya.yaml` (durasi hook, potongan per detik, posisi/ukuran caption, zoom/getar, waktu SFX). Pola naskah (struktur hook, panjang, penutup) ditulis ke `pola-naskah.md`.
3. **Pose maskot**: lihat daftar di bawah.
4. **Mesin**: parser naskah (baris bertag tokoh), lembar tempel ElevenLabs per tokoh, pemotong audio per baris dari transkrip lokal, timeline, ganti pose mengikuti suara, caption per kata, render, QA. Disalin dan digeneralkan dari proyek lain yang sudah teruji.
5. **Skill**: `/naskah` (prompt ChatGPT) dan `/olah` (naskah + audio jadi video).

## Keputusan (5 November 2026)
Topik opsi A, dialog dua tokoh dengan pola 3 ketukan setelah hook, semua visual oleh Claude, akun tanpa CTA dengan Collab ke @mentoringsobatambis. Rincian di `referensi/ringkasan.md` dan `CLAUDE.md`.

## Pose maskot (SVG terpisah per pose)
Versi pertama (MVP) 3 pose per tokoh: Lumi (tenang-bicara, mikir, bangga) dan Jago (smirk, ngeledek, mode juri). Jago juga punya tiga posisi kacamata (turun, naik, di dahi). Percobaan pertama: mata dan mulut buatan di atas SVG untuk pose "bicara" (belum diuji).

Hasil uji: SVG sekarang adalah hasil trace datar (±1.650 path, tanpa grup) dan tidak bisa dipotong per bagian dengan bersih. Jalan termurah: beberapa pose utuh yang ditukar mengikuti suara.

Per maskot: `diam`, `bicara` (mulut terbuka), `senang`, `kaget`, `berpikir`. Opsional: `menunjuk`.
Aturan berkas: kanvas 2000×2000, posisi dan skala karakter sama di semua pose (kaki di titik yang sama), latar transparan atau berupa path pertama berbentuk bingkai putih (dibuang otomatis oleh `bersihkan_svg`), nama `<tokoh>-<pose>.svg`.
Bila nanti ingin gerak bagian (lengan melambai, kepala miring), minta versi berlapis dari sumbernya: kepala tanpa mata dan mulut, mata, alis, mulut, telinga, kumis, lengan kiri/kanan, badan, syal/bandana, tas, ekor, api; tiap bagian utuh sampai ke area yang biasanya tertutup.

## Dibutuhkan dari pemilik
- Video referensi + data tayangan.
- Pose tambahan Lumi dan Jago.
- Keputusan: apa yang tampil di belakang narator (latar polos, ilustrasi, atau gambar generasi yang berbiaya).
- Voice ElevenLabs untuk tiap tokoh dan sunting `config/tokoh.yaml`.
