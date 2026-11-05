# template-video-lumi-dan-jago: catatan untuk Claude

Bahasa kerja: Indonesia. Merek: Sobat Ambis (mentoring lomba dan les privat, https://sobatambis.netlify.app/); Lumi dan Jago adalah maskotnya (profil: `docs/profil-maskot.md`, terstruktur: `config/tokoh.yaml`). Repo ini mandiri dari repo `sobatambis-marketing`: kode dari sana hanya disalin bila dibutuhkan dan digeneralkan, repo itu tidak diubah.

## Aturan dari pemilik
- **Akun IG baru = murni personal branding maskot, TANPA CTA**: tidak ada ajakan daftar, harga, klaim prestasi, kartu CTA, atau "komen kata kunci". Satu-satunya jembatan ke merek adalah post Collab dengan @mentoringsobatambis. Karena post Collab tampil juga di profil resmi, topik harus aman untuk merek: tanpa politik, agama, tuduhan, atau orang sungguhan.
- Aturan keras Jago (`config/tokoh.yaml`): hanya meledek situasi dan Lumi, berhenti meledek bila murid down, trik hanya yang legal.
- Hook memuat premis dalam kalimat pertama; pola 3 ketukan (Jago meledek, Lumi meluruskan, Jago membocorkan trik legal) dimulai SESUDAH hook.
- Semua visual dibuat Claude (latar, grafik, kartu); gaya animasi mengikuti `referensi/ringkasan.md`.
- Jangan memanggil API ElevenLabs atau layanan berbayar lain tanpa izin pemilik di sesi itu. Suara dibuat pemilik sendiri; uji memakai fixture dan audio palsu.
- Hemat token: pekerjaan mekanis (parse naskah, lembar tempel, potong audio, timeline, render, QA) lewat script Python deterministik, bukan LLM. LLM hanya untuk hal kreatif (prompt naskah, analisis gaya).
- SVG di `aset/maskot/asli/` tidak boleh diubah. Versi bersih dibuat ulang dengan `scripts/bersihkan_svg.py`.
- Gaya edit dan pola naskah berasal dari analisis video referensi pemilik (angka terukur, simpan di `gaya.yaml`); jangan mengarang. Pola dari sedikit sampel adalah hipotesis, bukan bukti.
- Tag ekspresi ElevenLabs hanya ditandai berfungsi setelah pemilik mengujinya.

## Kerja
- TDD dengan pytest. Satu tugas, satu commit kecil. Tanpa tanda pisah panjang (—) di teks yang diucapkan atau ditampilkan.
