---
name: topik-reels
description: Cari dan pilih topik reels "cerita yang bikin mikir" dengan metode yang sama dengan akun referensi - konsep berpikir yang punya nama, dibungkus alegori atau kisah nyata, dengan putaran gelap dan pemetaan ke hidup penonton. Pakai saat diminta ide topik, bank topik mingguan, atau sebelum skill naskah-reels.
---

# Cari topik reels

Langkah pertama dari alur **topik-reels → naskah-reels → olah-reels**. Keluarannya adalah kartu topik yang langsung bisa diberikan ke
skill `naskah-reels`.

## Metode (diturunkan dari 6 video referensi yang sukses)
Keenamnya berangkat dari **satu konsep berpikir yang punya nama** (salience bias, survivorship bias, appeal to authority, spotlight
effect, pecah belah, ilusi "aku aman"). Konsep itu tidak diajarkan langsung. Ia dibungkus **kendaraan cerita**, dan penonton baru
diberi namanya sesudah merasa ikut tertipu. Empat dari enam memakai alegori kerajaan atau hewan; dua memakai kisah nyata yang
mengejutkan (perang dunia, eksperimen 1970-an).

### Langkah 0: mulai dari kejadian nyata, baru cari teorinya
Urutan yang terbukti di akun referensi: **pengalaman atau kejadian nyata yang sedang dirasakan orang → mekanisme di baliknya → konsep
bernama**. Contoh: pajak yang terselip di harga dan bantuan yang dipamerkan (kejadian), lalu nama konsepnya salience bias. Jadi mulai dari
berita dan keluhan yang sedang ramai, bukan dari daftar konsep. Contoh arah: kebakaran hutan yang selalu disalahkan pada terik matahari
(banyak penyebab, satu kambing hitam), pegawai yang bekerja keras tapi atasan yang dipuji (siapa yang dihitung jasanya), harga yang naik
pelan-pelan.
**Politik dan jenuh:** berita Indonesia didominasi politik, dan orang jenuh melihatnya langsung. Yang masih menarik adalah *rasa* yang
sama dibungkus alegori. Aturannya: pakai **mekanismenya, bukan orangnya**. Tanpa nama tokoh, partai, atau lembaga sungguhan; ceritakan
sebagai kerajaan, desa, atau perusahaan fiktif; pelajarannya berlaku untuk siapa pun. Ini juga menjaga akun aman untuk post Collab merek.
Kejadian nyata dipakai sebagai *pemicu pilihan topik*, bukan sebagai isi yang disebut di video.

Pengumpulan sinyal (langkah di bawah memakai `python -m scripts.tren`: berita utama Indonesia, Google Trends, dan Bilibili Tiongkok).
### Langkah 0b: sinyal dari X lewat Grok (opsional, dikerjakan pemilik)
Claude tidak bisa membaca X (wajib login). Grok bisa. Alurnya: **pemilik menyalin prompt di bawah ke Grok, menempel hasilnya ke chat ini,
lalu Claude memetakan, memverifikasi, dan memilih konsep.** Untuk Tiongkok jangan memakai X (diblokir di sana): pakai Bilibili lewat
`scripts.tren`.
```text
Kamu membantu riset topik konten edukasi psikologi populer di Indonesia. Dari percakapan di X (bahasa Indonesia) dalam 48 jam terakhir, cari 10 keluhan atau isu yang sedang ramai dan dirasakan orang biasa: harga, kerja, sekolah, uang, birokrasi, hubungan, kejujuran, keadilan. Abaikan isu yang hanya soal partai, tokoh, atau pertandingan.
Untuk tiap isu tulis satu baris dengan format:
ISU (maksimal 12 kata, tanpa nama orang) | RASA YANG DOMINAN (marah/cemas/iri/pasrah/lucu) | KENAPA RAMAI (satu kalimat) | SEBERAPA RAMAI (tinggi/sedang) | 2 TAUTAN POSTINGAN SEBAGAI BUKTI
Jangan mengarang. Kalau kamu tidak yakin sesuatu benar-benar ramai, tulis "tidak yakin". Pisahkan fakta dari tebakanmu.
```
Saat menerima hasil Grok: (1) anggap **petunjuk, bukan fakta**; tautan X tidak bisa dibuka Claude. (2) Silangkan isu terbesar dengan berita
publik (`scripts.tren` atau pencarian berita); yang tidak muncul di sumber publik ditandai belum terverifikasi. (3) Isu yang menyangkut
lembaga atau orang nyata dengan penyebab yang belum jelas **dilewati**, jangan dijadikan topik. (4) Pilih isu yang pengalamannya dirasakan
semua orang, petakan ke mekanisme dan konsep, verifikasi konsep ke jurnal, beri skor, serahkan 2 sampai 3 kartu topik.

### Pengumpulan sinyal tren (Indonesia dan Tiongkok)
Pasar video pendek kedua negara relatif mirip, dan format "cerita yang bikin mikir" sendiri banyak dipakai di keduanya (kesan saya,
belum terukur). Sebelum memilih konsep, kumpulkan sinyal tren:
1. **Indonesia**: Google Trends Indonesia (`https://trends.google.com/trending/rss?geo=ID`), trending YouTube atau X bila bisa dibuka,
   dan topik yang ramai di komentar akun sejenis.
2. **Tiongkok**: Bilibili Populer (`https://api.bilibili.com/x/web-interface/popular`), dan daftar populer Douyin, Xiaohongshu, atau
   Weibo hanya lewat halaman publik tanpa login. Di Claude Code, `python -m scripts.tren` mengambil Google Trends dan Bilibili sekaligus.
   Penerjemahan judul Tiongkok dilakukan sendiri; jangan menyalin video atau naskah mereka.
3. **Saring jadi tema, bukan topik.** Tren mentah mayoritas olahraga dan berita. Tarik: apa yang diributkan orang (harga naik,
   kerja, sekolah, uang, hubungan, kuasa, kejujuran) dan emosinya (marah, cemas, iri, lega). Lalu tanyakan: konsep bernama apa yang
   menjelaskan fenomena itu? Itulah kandidatmu, dibungkus kendaraan cerita. Contoh: ramai soal harga yang naik pelan-pelan → konsep
   boiling frog atau anchoring, kendaraan fabel pasar.
4. **Tren bukan bukti.** Tren memberi waktu yang tepat, bukan jaminan. Tetap lewat saring status ilmiah dan skor di bawah. Hindari
   kejadian yang melibatkan orang sungguhan atau politik praktis; pakai alegori. Tren cepat basi: pilih yang masih naik, buat dalam
   1 sampai 3 hari.

### Bahan tambahan dari skill gratis (bila terpasang di Claude Code)
Repo `marketingskills` (MIT, gratis, tanpa API key, terkunci ke versi di katalog) dipasang otomatis oleh hook SessionStart. Empat skill
berikut membantu langkah 0 dan skor. Bukan wajib; di claude.ai yang tidak punya skill itu, lewati.
- **marketing-psychology**: daftar sekitar 70 model mental dan bias bernama (bahasa Inggris). Pakai sebagai bank konsep tambahan; baca
  bagian "Understanding Buyers & Human Psychology" dan "Behavioral Economics". Konsepnya tetap lewat saring status ilmiah di bawah.
- **content-strategy**, bagian "Shareable content": konten yang dibagikan membawa wawasan baru atau sudut berlawanan dengan dugaan umum,
  membuat orang merasa sesuatu, dan **dibagikan supaya pengirimnya tampak pintar atau untuk menolong orang lain**; juga "konsep yang
  dirasakan semua orang tapi belum punya nama" (itu persis slot penamaan kita). Pakai sebagai penguji kriteria "dikirim".
- **social**: naskah video pendek dan hook untuk Reels dan Shorts; bandingkan hook kandidat dengan panduannya.
- **marketing-ideas**: cadangan bila kehabisan sudut.

### Langkah
1. **Kumpulkan 10 sampai 15 kandidat konsep** dari bank di bawah, dari buku sains populer (Thinking Fast and Slow, Predictably
   Irrational, The Art of Thinking Clearly, Nudge, Influence), atau dari daftar bias kognitif dan sesat pikir. Bila ada alat pencarian
   atau konektor riset (Consensus, Elicit, Semantic Scholar), cari makalah klasik dan meta-analisisnya.
2. **Saring status ilmiah**: pakai hanya yang direplikasi atau didukung meta-analisis. Yang diperdebatkan boleh dipakai sebagai
   "kebenaran gelap" tanpa istilah ilmiah dan tanpa angka (varian kebenaran gelap), atau dibuang. Jangan pakai yang gagal direplikasi
   sebagai fakta (power pose, ego depletion, efek Mozart, Stanford Prison sebagai bukti, Zeigarnik sebagai hukum).
3. **Untuk tiap konsep, cari dua kendaraan cerita**:
   - alegori: kerajaan, desa, pasar, hewan (sumur, hutan, kawanan, sarang), benda (jembatan, lumbung, menara); atau
   - kisah nyata: eksperimen terkenal, peristiwa sejarah, penemuan. Kisah nyata wajib benar: siapa, kapan, angka.
   Cerita harus bisa digambar: tokoh, tempat, dan satu benda yang menjadi simbol.
4. **Tulis putaran dalam satu kalimat** ("Dan bagian paling ngeri? ..."). Bila putarannya tidak membuat penonton merasa ikut tertipu,
   ganti kendaraan.
5. **Tulis dua contoh pemetaan**: satu umum, satu yang sedikit tidak nyaman (uang, kuliah, kerja, keluarga, media sosial, takut tampil,
   orang berkuasa). Bila penonton tidak bisa mengenali dirinya dalam 3 detik, buang konsepnya.
6. **Beri skor** (tabel di bawah), urutkan, serahkan 3 teratas sebagai kartu topik.

### Skor (0 sampai 2 per kriteria, maksimal 14)
| kriteria | 2 | 1 | 0 |
|---|---|---|---|
| universal | hampir semua orang pernah mengalaminya | sebagian kelompok | khusus profesi |
| ikut tertipu | penonton akan melakukan kesalahan yang sama dengan tokoh | penonton hanya menonton orang lain salah | tidak ada putaran |
| bisa digambar | satu simbol kuat (beras, jembatan, bulu, pesawat) | bisa tapi abstrak | hanya bisa dijelaskan |
| kebenaran gelap | ironis, sedikit menyakitkan, terasa seperti kearifan | menarik saja | terasa seperti tips |
| bukti | direplikasi atau meta-analisis, atau peristiwa terdokumentasi | ada tapi diperdebatkan (pakai tanpa angka) | lemah atau gagal replikasi |
| aman | tanpa politik praktis, agama, tuduhan ke orang hidup | perlu dibungkus alegori | berisiko |
| dikirim | penonton langsung teringat orang atau pihak tertentu untuk dikirimi ("ini bos gue", "ini pejabat", "ini temen yang suka ghosting"), konten menyindir sistem atau pihak lain | menyentuh banyak orang tapi hanya menyindir diri sendiri | tidak ada alasan mengirimnya ke siapa pun |

Ambil yang skornya ≥10. Data akun nyata (video menara, planning fallacy): 1.374 penonton, penonton bertahan, tapi nol kiriman, nol komentar, nol follow, karena topiknya hanya menyindir diri sendiri. Konten yang menyindir pihak lain atau sistem lebih sering dikirim. Pemetaan boleh menyentuh pajak, kekuasaan, atau media, tetapi lewat alegori dan tanpa menunjuk tokoh atau
partai sungguhan.

## Bank konsep awal (verifikasi lagi sebelum menulis angka)
Sudah dipakai akun referensi, **hindari** supaya tidak terlihat meniru: salience bias, survivorship bias, appeal to authority, spotlight
effect, pecah belah (sumur tikus), ilusi "kamu aman" (ular di sumur).

| konsep | status | ide kendaraan |
|---|---|---|
| sunk cost fallacy (jebakan biaya hangus) | kuat untuk keputusan sehari-hari (Arkes dan Blumer 1985); detail diperdebatkan | raja membangun jembatan ke pulau kosong |
| anchoring (jangkar angka) | kuat, direplikasi luas (Tversky dan Kahneman 1974) | pedagang pasar yang selalu menyebut harga pertama setinggi langit |
| loss aversion (takut rugi) | kuat secara umum; besaran efek diperdebatkan | petani yang tak mau menjual sapi sakit |
| availability heuristic | kuat (Tversky dan Kahneman 1973) | desa yang takut hiu, padahal yang membunuh kelapa jatuh (pakai tanpa angka bila tak terverifikasi) |
| confirmation bias | kuat | peramal kerajaan yang hanya mencatat ramalan yang benar |
| planning fallacy | kuat (Buehler dkk. 1994) | menara yang "selesai bulan depan" selama sepuluh tahun |
| hindsight bias (sudah kuduga) | kuat (Fischhoff 1975) | para tetua yang semuanya "sudah tahu" setelah banjir |
| fundamental attribution error | kuat, besaran beda antarbudaya | pengembara yang dikira malas, ternyata kakinya patah |
| halo effect | kuat (Nisbett dan Wilson 1977) | pangeran tampan yang ucapannya selalu dianggap bijak |
| framing effect | kuat (Tversky dan Kahneman 1981) | dua tabib menawarkan obat yang sama dengan kata berbeda |
| base rate neglect | kuat | penjaga gerbang yang mencurigai semua pendatang berjubah hitam |
| gambler's fallacy | kuat | nelayan yang yakin hari ini pasti dapat ikan karena kemarin kosong |
| regression to the mean | kuat (statistika) | pelatih yang mengira teriakan membuat pemanah membaik |
| Goodhart's law (target merusak ukuran) | prinsip ekonomi, bukan eksperimen | kerajaan yang membayar per ekor ular mati |
| endowment effect | ada, besarannya diperdebatkan | anak yang menolak menukar batu biasa miliknya |
| IKEA effect | direplikasi (Norton dkk. 2012) | tukang yang menganggap kursi reyotnya paling indah |
| mere exposure effect | kuat (Zajonc 1968, meta-analisis) | lagu yang dibenci desa lalu jadi lagu kebanggaan |
| bystander effect | ada; meta-analisis menunjukkan melemah dalam bahaya nyata | rumah terbakar di tengah kerumunan penonton |
| Matthew effect (yang kaya makin kaya) | terdokumentasi (Merton 1968) | dua benih di ladang yang sama |
| tragedy of the commons | model teoretis; Ostrom menunjukkan bisa dihindari | padang rumput desa yang habis |
| Streisand effect | fenomena terdokumentasi, bukan eksperimen | raja yang melarang sebuah lagu |
| Peltzman effect (rasa aman membuat ceroboh) | diperdebatkan, pakai tanpa angka | ksatria berbaju zirah yang makin nekat |
| Parkinson's law | pengamatan, bukan eksperimen | pekerjaan yang membengkak sesuai waktu yang diberikan |
| Cobra effect (insentif yang memperparah masalah) | konsepnya kuat; kisah kobra di Delhi diperdebatkan sejarawan, tikus Hanoi 1902 terdokumentasi (Vann 2003) | pakai Hanoi; sudah dipakai di akun, jangan ulang |
| Peak-end rule | kuat (Kahneman dkk. 1993) | pasien kolonoskopi yang menderita lebih lama tapi mengingatnya lebih baik |
| Hyperbolic discounting | kuat | tukang yang memilih upah hari ini daripada dua kali lipat bulan depan |
| Mental accounting | kuat (Thaler) | pedagang yang menghabiskan uang hadiah tapi menimbun uang gaji |
| Curse of knowledge | kuat (Newton 1990, studi mengetuk lagu) | tabib tua yang tak sabar pada muridnya |
| Goal-gradient effect | ada (Kivetz dkk. 2006) | pelari yang makin cepat saat garis akhir terlihat |
| Paradox of choice | diperdebatkan (meta-analisis efek rata-rata kecil); pakai tanpa angka | pasar dengan terlalu banyak kios |
| Mimetic desire | teori Girard, bukan eksperimen; pakai tanpa angka | satu desa mendadak berebut sepatu yang sama |
| Semmelweis reflex | peristiwa sejarah terdokumentasi | dokter yang ditertawakan karena menyuruh cuci tangan |

## Keluaran: kartu topik (satu per topik, 3 teratas)
```text
TOPIK: <judul kerja, maks 8 kata>
KONSEP: <istilah> (<terjemahan>) | status: <kuat/diperdebatkan> | sumber: <Penulis Tahun, judul singkat>
VARIAN: penuh | kebenaran gelap | kisah nyata
KENDARAAN: <alegori atau kisah nyata, 1 kalimat; simbol utama>
HOOK: <kalimat pertama 9 sampai 15 kata, situasi + hasil berlawanan>
PUTARAN: <1 kalimat>
PEMBALIK: <X tidak sedang A. X hanya B.>
PEMETAAN: <contoh umum> / <contoh tidak nyaman>
PENUTUP: <draf antitesis 2 kalimat>
DIKIRIM KE: <siapa yang akan dikirimi penonton, 1 frasa>
SKOR: <n>/14 (universal, ikut tertipu, digambar, gelap, bukti, aman, dikirim)
PERLU DICEK: <fakta atau angka yang harus diverifikasi sebelum naskah>
```
Lalu teruskan kartu yang dipilih pengguna ke skill `naskah-reels`.
