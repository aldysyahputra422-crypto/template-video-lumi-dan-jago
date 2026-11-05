# template-video-lumi-dan-jago

Template video pendek dengan maskot **Ata**, panda merah Sobat Ambis (mentoring lomba). (Duo naga Lumi dan Jago diarsipkan.) Akunnya murni personal branding maskot, tanpa CTA; jembatan ke merek hanya lewat post Collab. Naskah ditulis di ChatGPT, suara dibuat di ElevenLabs oleh pemilik, dan Claude Code hanya merakit videonya dengan script deterministik (hemat token, konsisten).

## Pakai (dari nol sampai video)
```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
npm install --prefix render
```
Butuh `ffmpeg`, Node, dan Chromium Playwright (sudah ada di Claude Code web).

1. `/naskah <id> "<topik>"`: Claude meriset dan memverifikasi jurnal, menulis `episode/<id>/kartu-riset.yaml`, lalu `prompt-chatgpt.md`.
2. Tempel prompt ke ChatGPT, simpan jawabannya sebagai `episode/<id>/tempelan.txt`.
3. `/olah <id>`: impor format blok → lint standar naskah (angka riset dicek ke kartu) → **Approval 1** (`"disetujui": true`) → `lembar-elevenlabs.md`.
4. Generate di ElevenLabs (satu suara Ata), simpan sebagai `episode/<id>/suara.mp3`.
5. `/olah <id>` lagi: selaras per kata (Whisper lokal) → linimasa → campur (-14 LUFS) → render stickman → QA → `video.mp4` (**Approval 2**).

Semua langkah mekanis deterministik, tanpa LLM dan tanpa API berbayar. Contoh lengkap: `contoh/ep01-planning-fallacy/`.

## Visual
Stickman berkepala putih di latar gelap sesuai tempat cerita (`config/kosakata.yaml`: 12 latar, 12 peran, 11 ekspresi, 19 aksi, 26 props), isyarat visual per kata (`@kata`), grafik data, kartu simpan, dan Ata (9 pose) muncul di momen tertentu. Mesin: `render/mesin.html`.

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
