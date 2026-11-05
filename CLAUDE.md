# template-video-lumi-dan-jago: catatan untuk Claude

Bahasa kerja: Indonesia. Merek: Sobat Ambis (mentoring lomba dan les privat, https://sobatambis.netlify.app/); maskotnya **Ata, panda merah** (profil: `docs/profil-maskot.md`, terstruktur: `config/tokoh.yaml`, pose: `aset/maskot/panda/pose/`). Duo naga Lumi dan Jago diarsipkan (`docs/arsip/`). Repo ini mandiri dari repo `sobatambis-marketing`: kode dari sana hanya disalin bila dibutuhkan dan digeneralkan, repo itu tidak diubah.

## Aturan dari pemilik
- **Akun IG baru = murni personal branding maskot, TANPA CTA**: tidak ada ajakan daftar, harga, klaim prestasi, kartu CTA, atau "komen kata kunci". Satu-satunya jembatan ke merek adalah post Collab dengan @mentoringsobatambis. Karena post Collab tampil juga di profil resmi, topik harus aman untuk merek: tanpa politik, agama, tuduhan, atau orang sungguhan.
- Aturan keras Ata (`config/tokoh.yaml`): hanya meledek situasi, berhenti bercanda bila topiknya menyangkut orang yang down, trik hanya yang legal, klaim riset wajib bersumber dan dicek.
- Naskah: temuan jurnal internasional (yang sudah direplikasi) dibungkus cerita orang kedua atau alegori; standar di `.claude/skills/standar-naskah/SKILL.md`, diperiksa `scripts/lint_naskah.py`. Angka nyata HANYA dari `kartu-riset.yaml`. Sumber jurnal TIDAK ditampilkan di video (hanya di kartu riset, dan caption bila perlu). Ata muncul hanya di momen tertentu, satu suara per video.
- Alur produksi: `/naskah <nama> "<topik>"` lalu `/olah <nama>` (lihat README). Visual: stickman di latar gelap sesuai tempat (`render/mesin.html`, kosakata `config/kosakata.yaml`; `tests/test_mesin.py` menjaga keduanya sama).
- Semua visual dibuat Claude (latar, grafik, kartu); gaya animasi mengikuti `referensi/ringkasan.md`.
- **Latar wajib sesuai tempat cerita** (kota ya kota, pasar ya pasar, sekolah ya sekolah, desa ya desa): langit, bangunan, benda, dan warna alaminya. Bidang krem/peach polos BUKAN latar adegan; hanya untuk kartu, judul, dan grafik data.
- Jangan memanggil API ElevenLabs atau layanan berbayar lain tanpa izin pemilik di sesi itu. Suara dibuat pemilik sendiri; uji memakai fixture dan audio palsu.
- Hemat token: pekerjaan mekanis (parse naskah, lembar tempel, potong audio, timeline, render, QA) lewat script Python deterministik, bukan LLM. LLM hanya untuk hal kreatif (prompt naskah, analisis gaya).
- Aset sumber di `aset/maskot/asli/` dan `aset/maskot/panda/asli/` tidak boleh diubah. Pose Ata dibuat ulang dengan `python -m scripts.potong_pose`.
- Gaya edit dan pola naskah berasal dari analisis video referensi pemilik (angka terukur, simpan di `gaya.yaml`); jangan mengarang. Pola dari sedikit sampel adalah hipotesis, bukan bukti.
- Tag ekspresi ElevenLabs hanya ditandai berfungsi setelah pemilik mengujinya.

## Kerja
- Skill dari katalog Sobat Ambis yang dipakai di sini dicatat di `katalog/skill.yaml` (terkunci ke commit, gratis, tanpa API key) dan dipasang sendiri tiap sesi oleh hook SessionStart (`scripts/hook_mulai.sh`). Semua bisa diambil kapan saja: `python -m scripts.pasang_otomatis --wajib`, atau satu per satu `--id <id>`. Pin hanya diganti pemilik. Mode lisensi di `config/kebijakan.yaml` (eksplorasi sampai menghasilkan uang).
- TDD dengan pytest. Satu tugas, satu commit kecil. Tanpa tanda pisah panjang (—) di teks yang diucapkan atau ditampilkan.
