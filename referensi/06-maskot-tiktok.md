# Referensi 06: avatar 2D kreator gim (TikTok)

Sumber: file video dari pemilik. Isi videonya pengumuman kreator gim (bukan edukasi); yang diambil HANYA cara maskot/avatar dipakai. Teks lengkap di `transkrip.json` lokal (tidak di-commit).

## Teknis (terukur)
- 82,0 dtk, 576×1024, 30 fps. −8,0 LUFS dengan puncak +5,9 dBFS (unduhan TikTok, terpotong); target kita tetap −14 LUFS.
- 251 kata, 3,08 kata/dtk, tanpa jeda ≥ 0,45 dtk.
- **31 potongan keras (±23 per menit, satu shot rata-rata 2,6 dtk)**: jauh lebih cepat dari referensi 01–05 (0–8 per menit).

## Cara avatar dipakai (dari frame 1 fps dan 8 fps)
- **Muncul sekitar separuh waktu**, bergantian dengan b-roll (cuplikan gim, layar, ikon, meme). Lebih sering di paruh awal.
- **Pustaka pose, bukan rig**: ±8 gambar statis (jas dan kacamata melambai, kemeja menggaruk kepala, menunjuk ke atas, duduk di kursi, wajah close-up dengan beberapa ekspresi, kepala mengintip). Gerak terasa hidup karena pose berganti.
- **Gerak hanya transformasi gambar utuh**, tanpa lengan bergerak:
  1. *Pop-in*: muncul dari kecil ke ukuran penuh dalam 1 sampai 2 frame, sering dengan lingkaran kejut di tanah.
  2. *Masuk dari tepi*: menggeser dari bawah (dari balik meja atau dari bawah layar) atau dari samping.
  3. *Sapuan miring jadi transisi*: avatar kedua masuk terbalik dari pojok atas, berputar, lalu membesar sampai memenuhi layar (±0,4 dtk), dan potongan berikutnya terjadi di balik wajahnya.
  4. *Tumpang di atas footage*: avatar naik dari bawah dan membesar perlahan di atas video lain.
  5. *Flip dan rotasi bebas*; latar garis kecepatan ala manga di momen kaget.
- Gaya gambar: kartun datar, garis hitam bersih, warna rata, sedikit bayangan. Tidak bertekstur lukisan, sehingga tidak terasa "buatan AI".
- Caption satu kata kecil di tengah layar.

## Pelajaran untuk Lumi dan Jago
- Gambar ulang maskot ke gaya datar bergaris bersih, lalu buat pustaka pose (±8 per tokoh) sebagai SVG terpisah.
- Maskot muncul di momen tertentu (hook, reaksi, momen penamaan, penutup), bukan sepanjang video.
- Semua gerak di atas bisa dibuat lewat kode dari pose statis: pop-in, geser dari tepi, sapuan jadi transisi, flip, rotasi, close-up.
