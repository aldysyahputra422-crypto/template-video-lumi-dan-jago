# Gaya visual: yang dikunci dan yang bebas

Pola video referensi (mindwander_dot_id dan video 03, `referensi/`): **gaya terkunci, isi bebas per video**. Tiap video punya dunianya
sendiri (sumur dan tikus, pesawat perang, ruang kuliah, burung merak), tapi palet, cahaya, bentuk, caption, dan editing selalu sama.

## Dikunci (jangan diubah per video)
- **Palet** (diukur `scripts/ukur_palet.py`, disimpan `config/gaya.yaml`): dasar hampir hitam hangat (`#0D0B09` sampai `#1B140D`, 54 sampai 89%
  layar), lapis cokelat gelap (`#312A1C`, `#3E2D20`), terang krem atau putih (`#DFCEAD`, `#F0EBE1`), aksen emas (`#D09C27`, `#F2B80E`).
  Per video boleh maksimal 3 aksen khusus (`aksen: [...]` di aset.js), mis. oranye senja atau biru merak.
- **Bentuk**: datar, garis tepi gelap (`ST(lebar, warna)`, tepi `C.tepi`/`C.tinta`), sudut membulat, tanpa tekstur foto, tanpa gradien selain
  cahaya bawaan (`sorot`). Tokoh: kepala bulat besar, mata titik, tubuh sederhana. Hewan disederhanakan dengan proporsi yang sama lucunya.
- **Cahaya**: latar gelap, satu atau dua sumber cahaya hangat (`sorot(x, y, r, alfa)`), objek penting paling terang.
- **Editing**: kamera, transisi, caption per kata, watermark, SUASANA, gerbang gerak QA (diatur mesin, aset tidak menyentuhnya).

## Bebas per video (`video/<nama>/aset.js`)
Naskah mendeklarasikan aset baru di `##ASET`. `/olah` berhenti di kode 8 dengan `aset-dibutuhkan.md`. Claude menggambar semuanya di
`aset.js`, menjalankan `python -m scripts.cek_aset video/<nama>` (palet, sumber luar, kelengkapan, lembar pratinjau `aset-cek.png`),
melihat lembarnya, memperbaiki, lalu `/olah` lagi.

```js
export default (GAYA) => {
  const {C, ST, G, sorot} = GAYA;          // C = token warna mesin, G = garis lantai (1085), layar 720 x 1280
  return {
    aksen: ['#C1571C'],                     // maks 3 warna di luar palet
    latar: {                                // t = detik; gambar x -200..920, y 0..G, lalu lantai
      sumur_tua: t => `<rect x="-200" y="0" width="1120" height="${G}" fill="${C.s1}"/>...${sorot(360, 0, 420, .4)}`,
    },
    peran: {
      // tokoh non-manusia: kaki di (o.x, o.y), tinggi = tinggi * o.s, menghadap kanan (mesin mencerminkan saat bergerak ke kiri)
      tikus: {tinggi: 70, gambar: o => `<g transform="translate(${o.x} ${o.y}) scale(${o.s})">...</g>`},
      // tokoh manusia berkostum: pakai lapisan stickman (lihat PERAN di render/mesin.html)
      tentara: {baju: '#4E5A3A', celana: '#2E3424', kepala: 'kulit', rambut: 'pendek', aks: r => `...topi...`},
    },
    props: {keju: t => `<path d="..."/>`},  // pusat (0,0), kira-kira 120 x 120
    letak: {keju: 'meja'},                  // lantai | meja | dinding | ikon (wajib untuk props baru)
    sisipan: {peta_perang: (u, isi, t) => `...`},   // potongan layar penuh, pusat (0,0), kira-kira 660 x 700; u = detik sejak muncul
  };
};
```
`GAYA` juga berisi `sorot`, `lantai`, `bintang`, `jendelaKota`, `stickman`, `sarung` (tangan kartun), `caping`, `kacamata`, `ez`, `cl`,
`keluar`, `pantul`, `benih(n)` + `acak()` (acak deterministik: panggil `benih` dulu). Contoh lengkap yang lolos: `tests/fixtures/aset_uji/aset.js`.

## Larangan
- Gambar luar, URL, font lain, `fetch`/`import`/akses halaman: semua visual SVG buatan sendiri.
- Orang sungguhan yang masih hidup, logo merek, atau tokoh milik akun lain.
- Teks panjang di latar (teks besar diatur `TEKS:` di naskah).

## Editing terkunci (terukur, `scripts/ukur_fx.py` dan frame referensi)
- Caption: satu kata, Roboto Bold ±27 px, putih, bayangan lembut, tengah pada tinggi 43%.
- Watermark: Roboto Bold ±40 px, abu-abu ±42% transparan, berpindah di pita atas (7 sampai 11% tinggi) tiap 9 dtk.
- Vinyet tepi kuat, tengah terang; grain film saat encode (`scripts/render.py` GRAIN).
- Rentang referensi: terang 11 sampai 49, sudut/tengah 0,03 sampai 0,34, grain 1,8 sampai 4,8 (`config/gaya.yaml` target_visual).
- Figur dasar (2026-11-05): kepala ±22% tinggi figur, kaki panjang bercelana gelap, badan blok bahu kotak, lengan batang tipis, garis
  tepi tipis, wajah kecil (mata titik, mulut garis). Proporsi diukur dari referensi; desain tokoh tetap milik sendiri.
- TEKS tampil sebagai papan tulisan di dalam adegan (kayu gelap, bingkai emas tipis), bukan judul besar melayang.
- Profil filosofi: setiap LATAR wajib dideklarasikan di ##ASET (dunia khusus per video); hanya `kosong` yang bawaan.

## Totalitas visual (2026-11-05, masukan pemilik)
### Latar berlapis (parallax 3D)
`latar.nama` boleh berupa fungsi (satu lapisan) atau objek lapisan; tiap lapisan `t => svg`:
```js
ruang_kuliah: {
  langit: t => `...`,   // faktor parallax .12 (paling lambat)
  jauh:   t => `...`,   // .45, otomatis sedikit digelapkan (perspektif udara)
  tengah: t => `...`,   // 1, sejajar tokoh (lantai, panggung, podium)
  atas:   t => `...`,   // 1, digambar SESUDAH tokoh (meja depan, tali boneka; boleh pakai GAYA.tokoh(id))
  depan:  t => GAYA.kepalaPenonton(),   // 1,4 (paling cepat): siluet kepala, pagar, dahan
}
```
Lapisan jauh dan depan digambar lebar (x -600..1320) karena bergerak lebih jauh.

### Alat bantu dunia (`GAYA`)
- `kepalaPenonton(n = 12, y = null, skala = 1, t, warna, seed)`: barisan siluet kepala dan bahu; `y = null` dikunci ke bawah layar.
- `panggung(x0, x1, naik = 260, warna, tirai)`: panggung bertingkat; permukaannya cocok dengan token tingkat `panggung`.
- `tanganBoneka(x, y, skala, t, ujung = [[x, y], ...], lengan)`: tangan raksasa dari atas memegang palang dan tali ke titik `ujung`.
- `tokoh(id)`: `{tangan: {l, r}, kepala}` tokoh di frame ini (hanya di lapisan `atas`). `bawahLayar(f, sy)`: y dunia untuk tepi layar.

### Ukuran dan tingkat tokoh (naskah)
`AKTOR: id=peran posisi ekspresi [xN] [mini|kecil|besar|raksasa] [panggung|tinggi|naikNNN]`: skala .45/.7/1,5/2,6; naik 260/480/NNN px.

### Arketipe (field PERAN)
`rambut` (pendek, panjang, klimis, kerudung, mekar, botak, sanggul, gondrong, cepak), `warnaRambut`, `kumis` (tebal, tipis), `jenggot`
(pendek, panjang), `topi` (tinggi, fedora, baret, polisi, pilot, helm, koki, wisuda, peci, caping), `warnaTopi`, `pegang` (tongkat, kapur,
kamera, map, kaca_pembesar, palu, pancing, kuas, kunci), `badan` (gemuk, kurus), `postur` (bungkuk, tegap, santai), `kebiasaan`
(tangan_belakang, tangan_saku), `jalan` (pelan, tegap, tergesa). Peran bawaan: lihat `config/kosakata.yaml` (ilmuwan sampai wisudawan).
Desain generik per profesi; bukan wajah orang sungguhan tertentu.

### Kamera satu bidikan dan render kualitas
- Kamera: titik kunci per kalimat (awal, tengah, akhir rangkaian di dunia yang sama) dilalui kurva Catmull-Rom; drift pelan selalu jalan.
  Pindah dunia: `sambung` (dunia lama keluar, baru masuk sambil kamera menggeser) atau `tembus` (kamera maju menembus dunia lama).
- Gerak tokoh: satu gestur per kalimat (pegas), mulut per suku kata, kedip, jejak gerak; tanpa getar (dijaga test).
- Render: 60 fps dicampur ke 30 fps (motion blur), grain saat encode.
