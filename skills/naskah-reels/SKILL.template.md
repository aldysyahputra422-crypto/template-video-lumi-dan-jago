---
name: naskah-reels
description: Tulis naskah reels animasi 60 sampai 80 detik bergaya "cerita yang bikin mikir": alegori atau kisah nyata, putaran gelap, nama konsep psikologi, pemetaan ke hidup penonton, penutup paralel yang bisa dikutip. Pakai saat diminta ide topik, naskah reels, atau naskah untuk skill olah-reels.
---

# Naskah reels "cerita yang bikin mikir"

Formula ini diturunkan dari analisis terukur 6 video akun edukasi animasi yang tumbuh sangat cepat (median 66 dtk, 198 kata, 2,9 kata/dtk).
**Wajib baca `benchmark.md` (di folder skill ini) sebelum menulis**: angka, cetak biru per kalimat, dan kerangka DNA.
Keluaranmu adalah **naskah format blok** yang langsung bisa diolah skill `olah-reels` menjadi video.

## Langkah
Alur lengkap: **topik-reels → naskah-reels → olah-reels**. Bila pengguna memberi kartu topik (dari skill `topik-reels`), pakai kartu
itu dan mulai dari langkah 5; bila belum ada topik, jalankan metode `topik-reels` dulu (atau langkah 1 sampai 4 di bawah).

1. **Pilih konsep yang punya nama** (bias kognitif, sesat pikir, efek psikologi sosial, hukum ekonomi perilaku). Utamakan yang ada di buku
   sains populer atau makalah klasik dan sudah direplikasi. Hindari temuan yang gagal direplikasi (power pose, ego depletion, efek Mozart,
   eksperimen penjara Stanford sebagai bukti).
2. **Verifikasi** (bila ada alat pencarian atau konektor riset): siapa, tahun, angka. Angka di naskah hanya yang terverifikasi. Kisah fabel
   boleh fiktif, tapi kisah "nyata" harus nyata.
3. **Pilih kendaraan cerita** yang mewujudkan konsep tanpa menyebut namanya: fabel atau alegori (kerajaan, hewan, desa, sumur, hutan) atau
   kisah nyata yang mengejutkan (perang, eksperimen, penemuan). Cerita harus bisa digambar: tokoh, tempat, dan benda yang jelas.
4. **Uji kebenaran gelap**: putarannya membuat penonton merasa ikut tertipu, dan pelajarannya terasa seperti kearifan, bukan tips.
5. **Isi kerangka DNA** di `benchmark.md` bagian C, slot demi slot (H1, H2, C1 sampai C9, P1 sampai P3, N1, N2, M1 sampai M5, T1, T2),
   dengan posisi persen seperti di tabel. Baca bagian B (cetak biru 6 video) untuk melihat setiap slot bekerja. Pilih satu dari tiga
   varian (penuh, kebenaran gelap, kisah nyata).
6. **Panjang**: 175 sampai 215 kata, 22 sampai 28 kalimat, median 7 sampai 9 kata per kalimat, 3 sampai 8 kalimat pukulan (≤4 kata),
   satu kalimat tanya (putaran). Sekitar 1 dari 4 kalimat dibuka kata sambung (Dan, Tapi, Lalu, Jadi, Padahal). Satu kalimat per ketukan;
   kalimat pukulan boleh digabung dengan kalimat sebelumnya dalam satu ketukan.
7. **Visual per ketukan** (format di bawah): setiap kalimat diberi isyarat visual; aset yang tidak ada di kosakata bawaan dideklarasikan di
   `##ASET` dengan deskripsi singkat (ilustrator menggambarnya dengan gaya yang sama). **Bahasa bidikan (diperiksa lint)**: minimal 3 latar per video; paling lama 4 ketukan berturut-turut di latar yang
   sama tanpa SISIPAN; ketukan penamaan konsep wajib punya SISIPAN atau PROPS sebagai metafora. **Setiap latar wajib dideklarasikan di ##ASET**
   (dunia khusus per video, seperti akun referensi); hanya `kosong` yang bawaan. Tokoh penonton di bagian pemetaan memakai peran `kamu`
   (tokoh kuning). Kerumunan: `xJUMLAH`.
8. **Tag suara**: satu tag ElevenLabs di depan setiap kalimat UCAP.
9. **Caption**: baris pertama = penutup paralel; lalu sumber (Penulis, Tahun, Judul).

## Gaya bahasa
Narator tunggal tenang, kalimat pendek, kosakata sehari-hari. Istilah asing disebut sekali lalu diterjemahkan. Angka konkret di puncak
cerita. Tanpa sapaan "guys", tanpa ajakan di tengah, tanpa tanda pisah panjang. UCAP ditulis seperti diucapkan: tanpa kurung, singkatan,
atau garis miring; nama peneliti cukup di caption.

## Etika
Pakai formula, struktur, tempo, dan frasa fungsional pendek ini. Cerita sumber milik umum (sejarah, eksperimen, fabel) boleh diceritakan
ulang dengan kalimatmu sendiri. Jangan menyalin naskah kreator lain kata per kata. Hindari menuduh orang sungguhan yang masih hidup;
pemetaan ke politik dan agama berisiko untuk akun yang bekerja sama dengan merek.

## Format keluaran (WAJIB: dua blok kode, tanpa teks lain)
**Blok 1, naskah** (dibaca skill `olah-reels`): dari `##VIDEO` sampai `##AKHIR`.
**Blok 2, lembar ElevenLabs** (disalin pengguna ke ElevenLabs apa adanya): setiap kalimat UCAP, berurutan, sebagai tag di baris
sendiri lalu kalimatnya di baris berikut, satu baris kosong di antaranya. Isinya harus **sama persis** dengan UCAP di blok 1 (tanpa
nomor, tanpa nama ketukan, tanpa isyarat visual). Contoh bentuk:
```text
[curious]
Seorang raja membangun jembatan ke pulau kosong.

[serious]
Dan semakin jelas jembatan itu sia-sia, semakin cepat ia membangunnya.
```

Isi blok 1:
```text
##VIDEO <nama-video> | <judul>
##SUMBER <id sumber>
##ASET
LATAR <nama>: <deskripsi tempat>
AKTOR <nama>: <deskripsi tokoh atau hewan>
PROPS <nama>: <deskripsi benda>
SISIPAN <nama>: <deskripsi potongan layar penuh, mis. diagram>
##KETUKAN 01
UCAP: [tag] kalimat yang diucapkan
SUASANA: <suasana>                    (berlaku sampai diganti)
LATAR: <latar>                        (wajib di ketukan pertama)
AKTOR: id=peran posisi ekspresi [xJUMLAH]; ...
AKSI: id aksi [ke posisi] [@kata]; ...
EKSPRESI: id ekspresi [@kata]
PROPS: benda tempat [gerak] [@kata]   (tempat: kiri|tengah|kanan|atas|jauh_kiri|jauh_kanan|tangan:id|kepala:id)
SISIPAN: nama [isi] [@kata]
TEKS: tulisan besar maks 32 huruf [@kata]
KAMERA: lebar | dekat id | dorong | goyang | geser
KELUAR: id
FAKTA: ya                             (ketukan yang memuat angka riset)
##AKHIR
```
`@kata` harus kata yang ada di UCAP ketukan itu.

{{KOSAKATA}}

## Contoh (naskah asli, konsep sunk cost fallacy; Arkes dan Blumer 1985)
```text
{{CONTOH}}
```

Lembar ElevenLabs untuk contoh di atas:
```text
{{CONTOH_LEMBAR}}
```

## Periksa sebelum mengirim
Semua slot DNA terisi pada posisinya (bandingkan dengan tabel A dan C di benchmark.md); kalimat pembalik ada; dua contoh pemetaan berpola
"terlihat. Tapi tak terlihat."; penutup antitesis yang bisa berdiri sendiri; 175 sampai 215 kata; tidak ada kalimat cerita yang
disalin dari video referensi; setiap kalimat bertag dan bervisual; aset baru dideklarasikan di ##ASET; blok 2 (lembar ElevenLabs) ada dan sama persis dengan semua UCAP.
