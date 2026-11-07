---
description: "Produksi video Ata dari tempelan ChatGPT sampai video.mp4, berhenti di titik yang butuh pemilik. Argumen: <nama-video>"
---

Jalankan `.venv/bin/python -m scripts.olah video/$ARGUMENTS` (Bash `run_in_background: true` bila sudah sampai render; satu menit video ±2,5 menit render). Keluarannya satu baris JSON. Sampaikan `instruksi` ke pemilik apa adanya, maksimal 5 baris, dengan angka (durasi, LUFS, puncak), bukan klaim "bagus".

| Kode | Arti | Pemilik melakukan |
|---|---|---|
| 6 | belum ada `tempelan.txt`, format salah, atau melanggar standar naskah (galat per baris di `koreksi-chatgpt.md`) | tempel `koreksi-chatgpt.md` ke ChatGPT, simpan jawaban sebagai `tempelan.txt` |
| 4 | **Approval 1**: naskah lulus format dan standar | baca `naskah.json`, set `"disetujui": true`, generate `lembar-elevenlabs.md` di ElevenLabs |
| 5 | belum ada `suara.mp3` atau suaranya tidak cocok dengan naskah | simpan audio ElevenLabs sebagai `video/<nama>/suara.mp3` |
| 8 | naskah memakai aset baru (`##ASET`) yang belum digambar | tidak ada: Claude menggambar `aset.js` (lihat bawah) |
| 0 | `video.mp4` jadi dan lulus QA (**Approval 2**) | tonton |
| 1 | gagal teknis | baca `alasan`; perbaiki mesin, bukan naskah |

Saat kode 4 (Approval 1), sebelum menyampaikan ke pemilik: nilai naskah dengan bagian "Cara bercerita" di skill `standar-naskah`, teori skill `screenwriting-lint` (putaran, petunjuk yang ditanam, eskalasi; abaikan bagian vault Obsidian), dan skill `humanizer` untuk kalimat UCAP. Tulis maksimal 5 temuan konkret ke `video/<nama>/ulasan-naskah.md` dalam bentuk permintaan koreksi yang bisa ditempel ke ChatGPT, lalu sebutkan jumlah temuannya ke pemilik. Tidak ada temuan = tulis "tidak ada".

Bila pemilik sudah merekam suara dari teks ucapan saja (ChatGPT tidak memberi format blok): simpan teks rekamannya sebagai `video/<nama>/rekaman-pemilik.txt` (tag di baris sendiri, lalu kalimat), jalankan `.venv/bin/python -m scripts.prompt_visual video/<nama>`, dan minta pemilik menempel `prompt-visual.md` ke ChatGPT. `/olah` lalu memastikan setiap UCAP sama persis dengan rekaman.

Saat kode 8: baca `video/<nama>/aset-dibutuhkan.md` dan `docs/gaya-visual.md`, gambar semua aset di `video/<nama>/aset.js` (SVG, gaya terkunci, isi sesuai deskripsi dan cerita), jalankan `.venv/bin/python -m scripts.cek_aset video/<nama>`, lihat `aset-cek.png` (Read), perbaiki sampai lolos dan enak dilihat, lalu `/olah` lagi.

Aturan: jangan memanggil API ElevenLabs; jangan mengubah naskah secara kreatif (perbaikan naskah lewat ChatGPT memakai `koreksi-chatgpt.md`); jangan menandai `disetujui` atas nama pemilik.
