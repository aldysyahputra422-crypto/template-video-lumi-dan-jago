# template-video-lumi-dan-jago: catatan untuk Claude

Bahasa kerja: Indonesia. Proyek mandiri, tidak terkait merek atau repo lain; kode dari proyek lain hanya disalin bila dibutuhkan dan digeneralkan.

## Aturan dari pemilik
- Jangan memanggil API ElevenLabs atau layanan berbayar lain tanpa izin pemilik di sesi itu. Suara dibuat pemilik sendiri; uji memakai fixture dan audio palsu.
- Hemat token: pekerjaan mekanis (parse naskah, lembar tempel, potong audio, timeline, render, QA) lewat script Python deterministik, bukan LLM. LLM hanya untuk hal kreatif (prompt naskah, analisis gaya).
- SVG di `aset/maskot/asli/` tidak boleh diubah. Versi bersih dibuat ulang dengan `scripts/bersihkan_svg.py`.
- Gaya edit dan pola naskah berasal dari analisis video referensi pemilik (angka terukur, simpan di `gaya.yaml`); jangan mengarang. Pola dari sedikit sampel adalah hipotesis, bukan bukti.
- Tag ekspresi ElevenLabs hanya ditandai berfungsi setelah pemilik mengujinya.

## Kerja
- TDD dengan pytest. Satu tugas, satu commit kecil. Tanpa tanda pisah panjang (—) di teks yang diucapkan atau ditampilkan.
