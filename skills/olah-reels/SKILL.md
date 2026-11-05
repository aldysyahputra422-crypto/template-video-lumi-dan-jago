---
name: olah-reels
description: Olah naskah format blok (dari skill naskah-reels) menjadi video reels animasi 9:16 bergaya gelap-hangat dengan caption per kata, SFX, musik suasana, dan QA otomatis. Pakai saat pengguna menempel naskah ##VIDEO ... ##AKHIR atau meminta naskahnya dijadikan video. Butuh Claude Code atau Claude Desktop yang bisa menjalankan perintah di komputer.
---

# Olah naskah menjadi video

Mesin produksinya ada di folder `mesin/` di samping berkas ini. Semua langkah mekanis dikerjakan script (hemat token); Claude hanya
mengerjakan bagian kreatif: menggambar aset khusus video dan memeriksa hasil.

## Siapkan sekali per komputer
Jalankan dari folder `mesin/`:
```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
npm install --prefix render
npx --prefix render playwright install chromium
```
Butuh Python 3.11+, Node 18+, dan ffmpeg (macOS: `brew install ffmpeg`; Windows: `winget install ffmpeg`). Ganti nama akun watermark di
`config/tokoh.yaml` (`akun.nama_akun`). Cek kesiapan: `.venv/bin/python -m scripts.periksa_siap --tanpa-test`.

## Alur satu video
1. Buat folder `mesin/video/<nama>/` (folder `video/` dibuat sendiri bila belum ada), simpan naskah apa adanya sebagai `tempelan.txt` (garis miring sisa salin dibuang otomatis).
   Bila ada angka riset, tulis `kartu-riset.yaml` (contoh: `mesin/docs/`), atau hapus baris `FAKTA: ya`.
2. Jalankan `.venv/bin/python -m scripts.olah video/<nama>`. Hasilnya satu baris JSON; ikuti `kode`:

| kode | arti | yang dilakukan |
|---|---|---|
| 6 | format atau standar naskah dilanggar | kirim isi `koreksi-chatgpt.md` ke penulis naskah (atau perbaiki baris yang disebut), simpan ulang, jalankan lagi |
| 4 | naskah lolos: tunggu persetujuan | tunjukkan ringkasan ke pengguna; bila setuju ubah `"disetujui": true` di `naskah.json`, jalankan lagi |
| 8 | naskah memakai aset baru (`##ASET`) | baca `aset-dibutuhkan.md` dan `docs/gaya-visual.md`, gambar semua aset di `video/<nama>/aset.js` (SVG, gaya terkunci, isi sesuai cerita), jalankan `.venv/bin/python -m scripts.cek_aset video/<nama>`, lihat `aset-cek.png`, perbaiki sampai lolos dan bagus, jalankan lagi |
| 5 | butuh suara | pengguna menyalin `lembar-elevenlabs.txt` ke ElevenLabs (Eleven v3, satu suara narator, Speed ±1,15 supaya ±2,8 kata/dtk), menyimpan hasilnya sebagai `video/<nama>/suara.mp3`; jalankan lagi |
| 0 | video jadi dan lulus QA | serahkan `video.mp4` dan `caption.txt` dengan angka QA (durasi, LUFS, gerak) |
| 1 | gagal teknis atau QA | baca `masalah`; perbaiki mesin atau aset, bukan naskah |

3. Render penuh butuh ±2 sampai 5 menit; jalankan di latar belakang bila bisa. Untuk memeriksa visual cukup render beberapa frame:
   `node render/render.js video/<nama> /tmp/cek 30 2.0,10.0,25.0` lalu lihat PNG-nya.

## Yang dijaga otomatis
- Naskah: hook bergerak, komposisi berganti, kata yang bisa diucapkan, tanpa ajakan jualan, angka hanya dari kartu riset.
- Gaya: palet terukur dari video referensi, tanpa gambar luar (`cek_aset`).
- Gerak dan audio (QA, gerbang): gerak rata-rata ≥6, layar diam ≤10%, beda gambar 3 dtk ≥24, -14 LUFS, puncak ≤ -1 dBFS.
- Rasa gambar (QA, info `visual` + `catatan_visual`): terang 11 sampai 49, sudut/tengah 0,03 sampai 0,34 (vinyet), grain 1,8 sampai 4,8.

## Gaya editing yang dikunci (terukur dari video referensi)
- Caption satu kata, Roboto Bold ±27 px, putih dengan bayangan lembut, di tengah pada 43% tinggi layar.
- Watermark Roboto Bold ±40 px, abu-abu setengah transparan, berpindah di pita atas tiap 9 dtk sambil bergeser pelan.
- Vinyet kuat di tepi, tengah tetap terang (sorot); grain film halus saat encode; kamera selalu bergerak; pergantian komposisi ±3 dtk.
- Figur dasar: kepala ±22% tinggi, kaki panjang, badan blok, garis tipis. TEKS jadi papan tulisan di dalam adegan.
- Setiap latar adalah dunia khusus video ini (dari ##ASET, digambar di aset.js); hanya `kosong` yang bawaan.
- Palet hitam hangat, cokelat, krem, emas (`config/gaya.yaml` palet). Tokoh, latar, dan benda digambar baru per video; jangan meniru
  tokoh kreator lain.

## Aturan
- Jangan memanggil API berbayar (ElevenLabs, generator gambar) tanpa izin pengguna di sesi itu; suara dibuat pengguna.
- Semua visual digambar sendiri dengan SVG di `aset.js`; jangan memakai gambar dari internet.
- Laporkan angka QA, bukan klaim "bagus"; pengguna yang menilai video.
