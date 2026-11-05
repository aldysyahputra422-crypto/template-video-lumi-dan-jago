# Referensi 01: "Kos-kosan rumahan juga butuh sistem"

Sumber: file video dari pemilik + dua tangkapan layar profil akun. Isi video tidak disalin ke repo; hanya angka dan pola turunan. Tujuan: mengambil STRUKTUR dan gaya, bukan karakter atau isi pihak lain.

## Data tayangan (dari tangkapan layar, belum diverifikasi lain)
- Akun: 18 post, 6.416 pengikut. Kotak profil yang terlihat: 2,3 juta, 494 ribu, 607 ribu tayangan (tayangan jauh di atas jumlah pengikut: distribusi ke non-pengikut).
- Video ini (2,3 juta): 206 ribu suka, 6.806 komentar, 5.832 repost, 19 ribu kirim, 58,1 ribu simpan. Rasio terhadap tayangan: suka ±9%, simpan ±2,5%, kirim ±0,8%, komentar ±0,3%.
- **Tanggal unggah belum diketahui**, jadi syarat "1 juta dalam 7 hari" belum bisa diperiksa. Perlu dari pemilik.
- Seri berformat sama (judul sampul "Dari X jadi Y digital") dengan beberapa tayangan 494K+ menunjukkan format berulang, bukan sekali kebetulan. Itu bukti lebih kuat daripada satu video, tapi tetap hipotesis.

## Teknis (terukur)
- 82,6 dtk, 720×1280, 24 fps, 10 MB. Audio AAC 44,1 kHz stereo.
- Loudness −14,1 LUFS, puncak −0,6 dBFS, rentang dinamika 2,5 LU (suara dipadatkan).
- Potongan keras hanya 3 dalam 82 dtk: kamera bergerak kontinu (dolly, zoom, turun ke bawah tanah), bukan montase cepat. Metrik "potongan per detik" tidak cocok untuk gaya ini.
- Suara kontinu tanpa jeda ≥ 0,45 dtk; 200 kata, 2,5 kata/dtk (±150 kata per menit).

## Struktur naskah (dengan waktu)
| Detik | Bagian | Pola |
|---|---|---|
| 0,0 | Hook | "Kalau [situasi pemilik] di rumahmu, kamu [identitas]": menyapa audiens spesifik, tanpa salam |
| 4,9 | Masalah 1 | "Tapi [rasa sakit konkret]." |
| 10,2 | Solusi 1 | "Jadi [apa yang berubah]." + "Ini namanya [nama sistem]." |
| 12,0 – 52,7 | Siklus 2 sampai 4 | Ulang "Tapi … Jadi … Ini namanya …" (±12 dtk per siklus) |
| 57,7 | Mitos | "Kebanyakan [orang] kira … Nggak, [kenyataan]." |
| 65,1 | Bonus + wawasan | satu fitur tambahan + satu kalimat insight |
| 72,0 | Hasil | "Disitulah [keuntungan yang diinginkan]." |
| 74,2 | Penutup | "Selamat, kamu sudah [identitas baru]." |
| 77,2 | CTA | "Mau dibuatin … ? Komen KATA" (kata kunci tunggal untuk dikomentari) |

Ciri naskah: kalimat pendek, kosakata sehari-hari, setiap bagian diberi nama ("Ini namanya X") sehingga mudah diingat dan dijadikan label di layar. Angka dan contoh spesifik (Rp900.000, tagihan kamar 2, 5 kamar).

## Visual
- Latar diorama 3D low-poly yang sama sepanjang video; satu karakter pemandu bergestur menjelaskan.
- **Chip label** di tengah atas: judul topik, lalu "1 MASALAH: …" → "1 [NAMA SOLUSI]" dan seterusnya, ditutup "MITOS" dan "5 KONTRAK DIGITAL". Chip bernomor memberi rasa kemajuan.
- **Caption satu kata per satu kata**, besar, putih bergaris gelap, di tengah layar, mengikuti ucapan.
- **Kartu UI** muncul sebagai bukti visual: bubble WhatsApp, tabel status, kartu listing, formulir tiket, papan kanban, kontrak. Visual kuat untuk topik "sistem".
- Garis bercahaya di bawah tanah sebagai metafora sistem yang menyambung.
- Kartu CTA di akhir: pertanyaan, kata kunci disorot dalam kotak warna, tawaran gratis, nama merek.
- Sampul seri: strip label topik ("… · MANUAL → DIGITAL"), judul "Dari '…' jadi … digital", kata terakhir disorot warna.

## Yang bisa dipindah ke Lumi dan Jago (usulan, belum diputuskan)
- Struktur naskah masalah → solusi → "Ini namanya" dan CTA kata kunci: langsung bisa.
- Chip label, caption satu kata, kartu UI, kartu CTA: semuanya elemen 2D, mudah dibuat dengan Remotion.
- Gerak kamera kontinu: bisa ditiru dengan zoom/pan pada latar 2D berlapis.
- Latar diorama 3D: TIDAK bisa dengan SVG datar; butuh latar ilustrasi 2D per topik (keputusan latar masih terbuka).
