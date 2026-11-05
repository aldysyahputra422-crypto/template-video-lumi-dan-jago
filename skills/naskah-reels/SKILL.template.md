---
name: naskah-reels
description: Tulis naskah reels animasi 60 sampai 80 detik bergaya "cerita yang bikin mikir": alegori atau kisah nyata, putaran gelap, nama konsep psikologi, pemetaan ke hidup penonton, penutup paralel yang bisa dikutip. Pakai saat diminta ide topik, naskah reels, atau naskah untuk skill olah-reels.
---

# Naskah reels "cerita yang bikin mikir"

Formula ini diturunkan dari analisis terukur 6 video akun edukasi animasi yang tumbuh sangat cepat (median 66 dtk, 198 kata, 2,9 kata/dtk).
Keluaranmu adalah **naskah format blok** yang langsung bisa diolah skill `olah-reels` menjadi video.

## Langkah
1. **Pilih konsep yang punya nama** (bias kognitif, sesat pikir, efek psikologi sosial, hukum ekonomi perilaku). Utamakan yang ada di buku
   sains populer atau makalah klasik dan sudah direplikasi. Hindari temuan yang gagal direplikasi (power pose, ego depletion, efek Mozart,
   eksperimen penjara Stanford sebagai bukti).
2. **Verifikasi** (bila ada alat pencarian atau konektor riset): siapa, tahun, angka. Angka di naskah hanya yang terverifikasi. Kisah fabel
   boleh fiktif, tapi kisah "nyata" harus nyata.
3. **Pilih kendaraan cerita** yang mewujudkan konsep tanpa menyebut namanya: fabel atau alegori (kerajaan, hewan, desa, sumur, hutan) atau
   kisah nyata yang mengejutkan (perang, eksperimen, penemuan). Cerita harus bisa digambar: tokoh, tempat, dan benda yang jelas.
4. **Uji kebenaran gelap**: putarannya membuat penonton merasa ikut tertipu, dan pelajarannya terasa seperti kearifan, bukan tips.
5. **Tulis dengan 6 bagian** (posisi = persen durasi):
   | bagian | posisi | isi |
   |---|---|---|
   | hook | 0% | 2 kalimat; kalimat pertama 9 sampai 15 kata: situasi konkret + hasil yang berlawanan |
   | cerita | 0 sampai ±50% | kronologis, memburuk, detail yang bisa digambar, pengulangan berirama |
   | putaran | ±40 sampai 60% | "Dan bagian paling ngeri?" (atau menyakitkan, mengejutkan) + fakta pembalik + kalimat "[Tokoh] tidak sedang X. [Tokoh] hanya Y." |
   | penamaan | ±50 sampai 70% | "Dalam psikologi/logika/ekonomi, ini dikenal sebagai [istilah], [arti]." + satu kalimat definisi |
   | pemetaan | ±60 sampai 83% | "Dan manusia juga begitu." + dua contoh sehari-hari (satu umum, satu yang tidak nyaman) |
   | penutup | ±90% sampai akhir | "Jadi ingat ini, ..." + antitesis paralel dua kalimat yang bisa dikutip |
6. **Panjang**: 170 sampai 230 kata, 18 sampai 26 ketukan, satu kalimat pendek per ketukan.
7. **Visual per ketukan** (format di bawah): setiap kalimat diberi isyarat visual; aset yang tidak ada di kosakata bawaan dideklarasikan di
   `##ASET` dengan deskripsi singkat (ilustrator menggambarnya dengan gaya yang sama). Tokoh penonton di bagian pemetaan memakai peran `kamu`
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

## Format keluaran (WAJIB, dibaca program)
Jawab hanya dengan blok dari `##VIDEO` sampai `##AKHIR`:
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

## Periksa sebelum mengirim
Hook 2 kalimat dan paradoks; putaran di tengah dengan kalimat pembalik; nama konsep sesudah putaran; dua contoh pemetaan; penutup
antitesis paralel; 170 sampai 230 kata; setiap kalimat bertag dan bervisual; aset baru dideklarasikan di ##ASET.
