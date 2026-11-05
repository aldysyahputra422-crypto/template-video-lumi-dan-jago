# template-video-lumi-dan-jago

Template video pendek dengan maskot **Ata**, panda merah Sobat Ambis (mentoring lomba). (Duo naga Lumi dan Jago diarsipkan.) Akunnya murni personal branding maskot, tanpa CTA; jembatan ke merek hanya lewat post Collab. Naskah ditulis di ChatGPT, suara dibuat di ElevenLabs oleh pemilik, dan Claude Code hanya merakit videonya dengan script deterministik (hemat token, konsisten).

## Pakai (dari nol sampai video)
```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
npm install --prefix render
```
Butuh `ffmpeg`, Node, dan Chromium Playwright (sudah ada di Claude Code web). Cek kesiapan: `/periksa` (`python -m scripts.periksa_siap`). Panduan sesi baru: `docs/serah-terima.md`.

1. `/naskah <nama> "<topik>"`: Claude meriset dan memverifikasi jurnal, menulis `video/<nama>/kartu-riset.yaml`, lalu `prompt-chatgpt.md`.
2. Tempel prompt ke ChatGPT, simpan jawabannya sebagai `video/<nama>/tempelan.txt`.
3. `/olah <nama>`: impor format blok → lint standar naskah (angka riset dicek ke kartu) → ulasan Claude → **Approval 1** (`"disetujui": true`) → `lembar-elevenlabs.txt` (siap salin).
4. Generate di ElevenLabs (satu suara Ata), simpan sebagai `video/<nama>/suara.mp3`.
5. `/olah <nama>` lagi: selaras per kata (Whisper lokal) → linimasa (SFX otomatis, musik per SUASANA) → campur (-14 LUFS) → render stickman → QA audio dan gerak → `video.mp4` (**Approval 2**).

Semua langkah mekanis deterministik, tanpa LLM dan tanpa API berbayar. Contoh lengkap: `contoh/tenggat-planning-fallacy/`.

## Visual
Figur gaya video referensi 03 (kepala bulat besar, badan kotak berwarna, lengan dan kaki tabung, wajah garis tipis) di latar hitam sesuai tempat cerita dengan cahaya amber, caption kecil putih, close-up, dan transisi double exposure (`config/kosakata.yaml`: 12 latar, 12 peran, 11 ekspresi, 19 aksi, 26 props), isyarat visual per kata (`@kata`), SISIPAN layar penuh yang memvisualkan kata secara harfiah (HP yang feed-nya digulir, jam berputar kencang, kalender tersobek, layar laptop, chat, struk tagihan, akar tumbuh), kamera yang tidak pernah diam, grafik data, kartu, dan Ata (9 pose) muncul di momen tertentu. Juga: kostum sesuai gender dan profesi (siswa, siswi, siswi berkerudung, mahasiswi, dokter, petani, pengusaha, tokoh kuning `kamu`), letak benda alami (lantai, meja, dinding, di atas kepala), tanda emosi gaya komik, cutaway tangan bersarung putih, figuran hanya di tempat ramai, dan SUASANA (normal, tegang, horor, ceria, sedih, misterius) yang mengatur warna, cahaya, gerak tokoh, dan musik. Gerak dijaga gerbang QA dari 6 video referensi (`config/gaya.yaml`). Mesin: `render/mesin.html`.

## Audio
Suara Ata dari ElevenLabs (pemilik). SFX otomatis dari isyarat visual (`scripts/linimasa.py`), diambil dari pustaka `katalog/sfx.yaml`: Mixkit (lisensi bebas komersial, tidak masuk git) lalu sintetis (`python -m scripts.sfx`). Musik latar per SUASANA, crossfade antarbagian. Loudness -14 LUFS dua tahap (`scripts/campur.py`).

## Sudah ada
- `aset/maskot/asli/`: SVG asli Lumi dan Jago (tidak diubah).
- `aset/maskot/`: versi bersih (latar putih dan tambalan putih sisa trace dibuang, jadi transparan). Dibuat dengan `python -m scripts.bersihkan_svg`.
- `config/tokoh.yaml` dan `docs/profil-maskot.md`: profil Ata (kepribadian, aturan keras, pose per momen, palet, struktur naskah).
- `aset/maskot/panda/pose/`: 9 pose Ata (PNG transparan + SVG), dibuat dari lembar pose dengan `python -m scripts.potong_pose`.
- `scripts/analisis_referensi.py` dan `referensi/`: analisis lima video referensi dan ringkasan pola.
- `docs/rencana.md`: rencana, urutan kerja, daftar pose, dan yang dibutuhkan dari pemilik.

## Pengembangan
```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest -q
```
