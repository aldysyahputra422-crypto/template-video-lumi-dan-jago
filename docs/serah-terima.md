# Serah terima: memakai repo ini di akun utama

Repo ini sudah melewati uji coba (naskah, suara asli, gerak, kostum, letak benda, suasana, SFX). Tujuan dokumen ini: sesi baru di akun utama bisa langsung produksi tanpa revisi besar dan tanpa membuang token untuk mempelajari ulang.

## 1. Mulai sesi (sekali per sesi)
```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
npm install --prefix render
.venv/bin/python -m scripts.periksa_siap
```
Hook SessionStart (`.claude/settings.json` → `scripts/hook_mulai.sh`) memasang skill katalog dan menyiapkan SFX sendiri. `/periksa` harus berakhir `SIAP`.

## 2. Alur satu video (3 titik pemilik)
1. `/naskah <nama> "<topik>"`: riset jurnal (Consensus), `kartu-riset.yaml` (angka + `nama_konsep` + batas), uji premis, `prompt-chatgpt.md`.
2. Pemilik menempel prompt ke ChatGPT dan menempel jawabannya ke chat (disimpan sebagai `tempelan.txt`).
3. `/olah <nama>`: format + lint standar. Galat → `koreksi-chatgpt.md` (tempel balik ke ChatGPT). Lulus → ulasan Claude maksimal 5 butir (`ulasan-naskah.md`) + `lembar-elevenlabs.txt` (tag di baris sendiri, siap salin). **Titik 1: pemilik menyetujui naskah.**
4. Pemilik generate suara di ElevenLabs (satu suara Ata, tag ekspresi berpengaruh; pertimbangkan Speed ±1,15 karena suara Bowo lambat), simpan `suara.mp3`. **Titik 2: suara.**
5. `/olah <nama>`: selaras kata (Whisper lokal) → linimasa (SFX otomatis, musik per suasana) → campur (-14 LUFS) → render → QA (resolusi, durasi, loudness, puncak, gerak). **Titik 3: pemilik menonton video.**

## 3. Gerbang otomatis (jangan dilonggarkan tanpa pemilik)
| Gerbang | Isi | Sumber angka |
|---|---|---|
| Lint naskah | hook ≤10 kata dan tidak diam, durasi 40 sampai 55 dtk, visual tiap ketukan, satu KARTU, tanpa ajakan jualan, angka hanya dari kartu riset, UCAP bisa diucapkan, komposisi berganti ≤2 ketukan, Ata hanya di adegan lapang (≤3), pola tidak mudah ditebak, nama konsep sesudah 40% | standar pemilik + video referensi |
| QA audio | -14 ±1 LUFS, puncak ≤ -1 dBFS | referensi (semua ±-14) |
| QA gerak | gerak rata-rata ≥6, layar diam ≤10%, diam terpanjang ≤1,5 dtk, beda gambar 3 dtk ≥30 | `config/gaya.yaml` (6 video referensi) |

## 4. Keputusan pemilik yang sudah final
- Akun IG baru: personal branding Ata, TANPA CTA; jembatan ke merek hanya post Collab @mentoringsobatambis. Topik aman merek.
- Pilar: skill yang tidak diajarkan di sekolah/kampus dan komponen lomba. Patokan alur: video referensi 03 (petunjuk ditanam → putaran → kalimat pembalik → nama konsep → bukti dan batas → trik legal → pemetaan → callback).
- Visual: stickman gaya video referensi 03, latar gelap sesuai tempat, kostum sesuai gender dan profesi, figuran hanya di pasar/kota/jalan. Sumber jurnal tidak tampil di video (boleh di caption: `kutipan_caption`).
- Nama video per topik (bukan nomor episode). Hindari "simpan ini" dan ajakan sejenis.
- Tag ekspresi ElevenLabs yang sudah diuji pemilik ditandai `pemilik` di `config/tag_ekspresi.yaml`.

## 5. Menambah kosakata (tanpa merusak)
Tambah nama di `config/kosakata.yaml` DAN implementasinya di `render/mesin.html` (latar, peran, aksi, props + `LETAK_PROPS`, sisipan, suasana). `tests/test_mesin.py` menolak bila keduanya tidak sama. Props baru wajib punya letak alami (lantai, meja, dinding, ikon). Jalankan `.venv/bin/python -m pytest -q` lalu render cek frame:
```bash
node render/render.js video/<nama> /tmp/cek 30 1.0,5.0,9.0
```

## 6. Hemat token
- Satu video per sesi; pekerjaan mekanis lewat script, bukan dibaca LLM. Jangan membuka `render/mesin.html` utuh kecuali mengubah mesin.
- Cek visual memakai 5 sampai 10 frame (`render.js` mode cek), bukan render penuh.
- Perbaikan audio saja: mix ulang + ganti trek audio (tanpa render ulang frame).

## 7. Batas yang diketahui
- Musik latar masih sintetis atau sementara (`aset/audio/katalog.yaml`); bisa diganti file berlisensi jelas dengan nama yang sama.
- Freesound, Pixabay, Zapsplat, Sonniss diblokir (403) dari lingkungan cloud; SFX memakai Mixkit (tidak masuk git) + sintetis.
- Target gerak dan pola naskah berasal dari 6 video yang semuanya sukses: hipotesis, bukan bukti. Ukur ulang bila referensi bertambah (`python -m scripts.ukur_gerak <video>`).
