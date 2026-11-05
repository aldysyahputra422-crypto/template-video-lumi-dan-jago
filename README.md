# template-video-lumi-dan-jago

Template video pendek dengan dua maskot narator, **Lumi** dan **Jago**, maskot Sobat Ambis (mentoring lomba). Akunnya murni personal branding maskot, tanpa CTA; jembatan ke merek hanya lewat post Collab. Naskah ditulis di ChatGPT, suara dibuat di ElevenLabs oleh pemilik, dan Claude Code hanya merakit videonya dengan script deterministik (hemat token, konsisten).

## Alur yang dituju
1. `/naskah` membuat prompt ChatGPT dari kartu kepribadian tokoh, pola naskah yang terbukti, dan kosakata tag ekspresi.
2. Pemilik menempel naskah ke ElevenLabs per tokoh (lembar tempel dibuat otomatis).
3. `/olah` menerima naskah + audio, memotong audio per baris, mengganti pose maskot mengikuti suara, memasang caption per kata dan gaya edit dari `gaya.yaml`, lalu render dan QA.

## Sudah ada
- `aset/maskot/asli/`: SVG asli Lumi dan Jago (tidak diubah).
- `aset/maskot/`: versi bersih (latar putih dan tambalan putih sisa trace dibuang, jadi transparan). Dibuat dengan `python -m scripts.bersihkan_svg`.
- `config/tokoh.yaml` dan `docs/profil-maskot.md`: profil maskot dari pemilik (kepribadian, aturan keras Jago, palet, pola dialog).
- `scripts/analisis_referensi.py` dan `referensi/`: analisis lima video referensi dan ringkasan pola.
- `docs/rencana.md`: rencana, urutan kerja, daftar pose, dan yang dibutuhkan dari pemilik.

## Pengembangan
```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest -q
```
