"""Buat prompt-chatgpt.md: prompt agar ChatGPT menulis naskah Ata dalam format blok yang bisa diproses mesin.

python -m scripts.prompt_naskah <folder> [--topik "teks"]
Butuh <folder>/kartu-riset.yaml (angka nyata hanya dari sini). Kode 3 bila kartu belum ada.
Semua daftar dibaca dari config (tidak ditulis ulang). Tanpa LLM.
"""
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
# Perintah format di AWAL dan AKHIR prompt: ChatGPT pernah menjawab teks ucapan saja (2026-11-05).
FORMAT_WAJIB = """## FORMAT JAWABAN (WAJIB, dibaca program)
Jawab HANYA dengan naskah format blok: baris pertama `##VIDEO <id> | <judul>`, lalu `##SUMBER <id kartu riset>`, lalu setiap
`##KETUKAN` berisi `UCAP:` dan isyarat visualnya (`LATAR:`, `AKTOR:`, `AKSI:`, `EKSPRESI:`, `PROPS:`, `SISIPAN:`, `KAMERA:` dst),
dan baris terakhir `##AKHIR`. JANGAN menjawab dengan teks ucapan saja, lembar suara, tabel, atau JSON: jawaban tanpa baris
`LATAR:` dan `AKTOR:` dianggap salah dan ditolak program."""
CONTOH = ROOT / "contoh/kedai-5whys/tempelan.txt"


def _y(p: Path) -> dict:
    return yaml.safe_load(p.read_text(encoding="utf-8"))


def buat(folder: Path, topik: str = "") -> str:
    folder = Path(folder)
    k, t, tag = _y(ROOT / "config/kosakata.yaml"), _y(ROOT / "config/tokoh.yaml"), _y(ROOT / "config/tag_ekspresi.yaml")
    riset = (folder / "kartu-riset.yaml").read_text(encoding="utf-8")
    ata = t["tokoh"]["ata"]
    contoh = CONTOH.read_text(encoding="utf-8")
    contoh = contoh[contoh.index("##VIDEO"):]
    daftar = lambda d: "\n".join(f"- `{n}`: {v}" for n, v in d.items())
    tags = "\n".join(f"- [{n}] ({'emosi ' + v['emosi'] if v['jenis'] == 'suara' else 'pengubah'}){' (teruji pemilik)' if v['terverifikasi'] == 'pemilik' else '' if v['terverifikasi'] == 'dokumentasi' else ' belum terverifikasi'}" for n, v in tag["tag"].items())
    return f"""# Tugas: tulis naskah video pendek "{folder.name}" untuk maskot Ata

{FORMAT_WAJIB}

Kamu penulis naskah video vertikal 40 sampai 55 detik untuk akun personal branding maskot. Penontonnya pelajar dan mahasiswa Indonesia.
Tujuan: video yang DISIMPAN penonton karena berguna, tapi tidak membosankan. Bahasa sehari-hari, kalimat pendek.
{f"{chr(10)}TOPIK DARI PEMILIK: {topik}{chr(10)}" if topik else ""}
## 1. Tokoh: Ata
{t['lore']['ata']}. Ciri: {', '.join(ata['ciri_wajib'])}.
Kepribadian: {', '.join(ata['kepribadian'])}. Gaya bicara: {ata['gaya_bicara']}.
Kalimat khas: {' / '.join(ata['kalimat_khas'])}
Aturan keras:
{chr(10).join('- ' + a for a in ata['aturan_keras'])}
Ata adalah narator (satu suara). Di layar, Ata hanya muncul di momen tertentu (hook, momen penamaan, reaksi angka, trik, penutup); sisanya aktor stickman.

## 2. Bahan riset (SATU-SATUNYA sumber angka nyata)
```yaml
{riset.strip()}
```
Angka nyata di naskah HARUS dari kartu ini (boleh dibulatkan wajar, mis. 33,9 jadi 34). Jangan menambah angka atau klaim riset lain.

## 3. Pilar topik dan uji perhatian
Pilar: skill yang TIDAK diajarkan di sekolah atau kampus (berpikir, belajar, bicara, menjual, memecahkan masalah) dan komponen lomba (business plan, BMC, riset pasar, presentasi juri).
Sudut harus lolos uji perhatian, kalau tidak, pilih sudut lain:
- klaim yang menyalahi dugaan atau provokatif di kalimat pertama (mis. "menyontek itu bagus", lalu dibelokkan ke versi yang legal),
- ada kegagalan atau taruhan yang dekat dengan penonton (bisnis sepi, presentasi dibantai juri, nilai jeblok),
- isinya tidak bisa ditebak dari judul. Hindari nasihat generik ("rajin belajar", "percaya diri").
Patokan alur (pola video referensi terbaik): hook paradoks → cerita kegagalan yang memburuk, dengan PETUNJUK yang ditanam diam-diam (terlihat di layar atau disebut sambil lalu) → PUTARAN: satu pertanyaan atau temuan sederhana membalik arti kejadian sebelumnya, dan petunjuk tadi ternyata jawabannya → satu kalimat pembalik ("Mereka bukan menolak kopinya. Mereka tidak pernah melihatnya buka.") → nama konsep SESUDAH putaran → bukti jurnal termasuk kritik atau batasnya → trik legal → pemetaan ke dunia penonton (tugas, lomba) → callback.
JANGAN memperagakan teorinya terang-terangan sebelum putaran (mis. bertanya "kenapa" lima kali berturut untuk menjelaskan 5 Whys): penonton yang paham sudah menebak duluan. Penonton harus ikut tertipu seperti tokohnya, lalu sadar bersama.

## 4. Standar naskah (diperiksa program; naskah yang melanggar ditolak)
1. Hook di KETUKAN 01, maksimal 10 kata, menyapa "kamu" atau membalik dugaan. Premis sudah lengkap di kalimat pertama, tanpa salam.
2. Cerita orang kedua yang dekat dengan pelajar, minimal dua detail spesifik yang lucu, dan MENINGKAT (bukan daftar datar). Untuk konsep abstrak boleh alegori singkat.
3. Momen penamaan: sebut nama konsep sesudah cerita, lalu definisi satu kalimat.
4. Angka nyata dari kartu riset dengan kontras jelas. Tandai ketukan yang memuat angka riset dengan `FAKTA: ya` (ketukan ber-DATA otomatis fakta).
5. Alat yang berguna: tepat satu `KARTU` berisi maksimal 3 langkah konkret yang bisa dipakai hari ini. JANGAN menyuruh penonton menyimpan, membagikan, follow, atau komen (terasa jualan); cukup tunjukkan alatnya. Judul KARTU netral, mis. "Triknya".
6. Penutup = callback ke lelucon atau hook awal, bukan moral umum. Pola "bukan X, tapi Y" maksimal sekali.
7. Durasi 40 sampai 55 detik (±2,6 kata per detik). Satu ketukan = satu kalimat pendek (maksimal 16 kata) supaya visual berganti tiap 2 sampai 5 detik.
   Ganti komposisi minimal tiap 2 ketukan (KAMERA dekat/geser/dorong, aktor pindah `ke <posisi>`, LATAR/AKTOR baru, atau SISIPAN). Program menolak 3 ketukan berturut yang komposisinya sama.
8. Hook diam ditolak: detik pertama wajib gerak besar, yaitu SISIPAN atau aktor masuk/pindah (`AKSI: id lari ke tengah @kata`, jalan ke, lompat), bukan aktor berdiri.
9. Visualkan secara harfiah benda atau kegiatan yang diucapkan dengan SISIPAN (minimal 2 per video). Contoh: "malah nonton video kucing" → `SISIPAN: hp_scroll kucing @nonton` (HP naik, jempol menggulir feed kucing);
   "begadang" → `SISIPAN: jam_cepat @begadang`; "tagihan listrik naik" → `SISIPAN: tagihan @listrik`. Sumber jurnal tidak ditulis di layar.
10. Ata hanya muncul di ketukan lapang (maksimal 1 aktor, tanpa SISIPAN/KARTU/DATA), maksimal 3 kali. Jangan memaksanya tampil di atas adegan yang sudah ramai.
11. Nama konsep tidak boleh disebut sebelum 40% naskah; 4 ketukan berturut dengan kata pembuka sama ditolak (pola mudah ditebak).
12. Pakai SUASANA untuk membangun rasa: misterius saat penonton dibuat curiga, tegang menjelang putaran, ceria sesudah trik, horor hanya bila ceritanya menakutkan. Ganti paling banyak tiap 2 ketukan. SFX dipasang otomatis oleh mesin dari isyarat visual, jangan ditulis.
13. Cutaway tangan (`SISIPAN: tangan_ambil <props>`, `tangan_beri <props>`, `tangan_tulis`) untuk aksi tangan yang diucapkan; tokoh yang mewakili penonton ("kamu") memakai peran `kamu`.
Jangan menyebut nama peneliti di UCAP (cukup "peneliti", "penelitian tahun 2001", atau "63 penelitian"); nama masuk caption otomatis.
UCAP adalah teks yang langsung dibacakan suara: tulis seperti diucapkan ("Larsen dan rekan-rekannya, tahun 2009", "39 persen"), tanpa kurung, singkatan (dkk., et al.), garis miring, atau garis bawah.
Tanpa tanda pisah panjang. Tanpa kata kasar. Tanpa politik, agama, tuduhan, atau orang sungguhan. Tanpa ajakan daftar, harga, atau "follow".

## 5. Format keluaran (blok bertanda, BUKAN JSON, BUKAN tabel)
Setiap ketukan punya UCAP (yang diucapkan Ata) dan isyarat visual. Visual memakai aktor stickman di latar gelap sesuai tempat cerita.
Isyarat bisa dipicu tepat di satu kata dengan `@kata` (kata itu harus ada di UCAP ketukan yang sama), supaya setiap kata penting punya visualnya.

```
##VIDEO <id> | <judul>
##SUMBER <id kartu riset>
##KETUKAN 01
UCAP: [tag] kalimat yang diucapkan
LATAR: <latar>                        (wajib di ketukan pertama; ganti bila tempat berubah, aktor lama hilang)
AKTOR: id=peran posisi ekspresi; id2=peran posisi ekspresi
AKSI: id aksi [ke posisi] [@kata]; ...
EKSPRESI: id ekspresi [@kata]; ...
PROPS: benda tempat [gerak] [@kata]; ...   (tempat: kiri|tengah|kanan|atas|jauh_kiri|jauh_kanan|tangan:id|kepala:id)
TEKS: tulisan besar maks 32 huruf [@kata]
DATA: label=angka satuan [@kata]; ...      (grafik batang; angka dari kartu riset)
KARTU: judul | langkah 1 [@kata] | langkah 2 [@kata] | langkah 3 [@kata]
ATA: pose [kiri|tengah|kanan] [intip|pop|sapuan]
KAMERA: lebar | dekat id | dorong | goyang | geser
SISIPAN: nama [isi] [@kata]          (potongan layar penuh: benda besar bergerak, dari @kata sampai akhir ketukan; maksimal satu per ketukan)
SUASANA: nama                        (berlaku sampai diganti; mengatur warna, cahaya, gerak tokoh, dan musik)
KELUAR: id
FAKTA: ya
##KETUKAN 02
...
##AKHIR
```

### Kosakata (di luar daftar ditolak program)
LATAR:
{daftar(k['latar'])}
PERAN aktor (pilih yang cocok dengan gender dan profesi tokoh: tokoh perempuan memakai siswi/mahasiswi/ibu, dokter memakai dokter, petani memakai petani; dua tokoh sejenis boleh, mesin membedakan warnanya):
{daftar(k['peran'])}
EKSPRESI: {', '.join(k['ekspresi'])}
AKSI:
{daftar(k['aksi'])}
POSISI: {', '.join(k['posisi'])}
PROPS: {', '.join(k['props'])}
GERAK PROPS: {', '.join(k['gerak_props'])}
SUASANA:
{chr(10).join(f"- `{n}`: {v['arti']}" for n, v in k['suasana'].items())}
SISIPAN:
{chr(10).join(f"- `{n}`: {v['arti']}" + (" (isi: nama props mana pun)" if v['isi'] == 'props' else f" (isi: {' | '.join(v['isi'])})" if v['isi'] else '') for n, v in k['sisipan'].items())}
POSE ATA: {', '.join(ata['pose'])} (pemetaan: {', '.join(f'{m}={p}' for m, p in ata['pemetaan_momen'].items())})
TAG SUARA (WAJIB satu di depan SETIAP kalimat UCAP, boleh lebih dari satu: [tense, slowly]; utamakan yang teruji pemilik):
{tags}

### Contoh naskah lengkap yang lolos standar
```text
{contoh.strip()}
```

## 6. Sebelum mengirim, periksa sendiri
Hook maksimal 10 kata dan tidak diam; tiap 2 ketukan komposisi berganti; minimal 2 SISIPAN; setiap @kata ada di UCAP-nya; setiap ketukan punya minimal satu isyarat visual; angka riset sama dengan kartu;
satu KARTU maksimal 3 langkah; penutup callback; semua nama dari kosakata.
Bila nanti kuberi daftar galat, perbaiki hanya baris yang disebut dan kirim ulang seluruh naskah.

{FORMAT_WAJIB}
"""


def main(argv: list[str]) -> int:
    pos = [a for i, a in enumerate(argv) if not a.startswith("--") and (i == 0 or argv[i - 1] != "--topik")]
    if not pos:
        print(__doc__)
        return 2
    folder = Path(pos[0])
    if not (folder / "kartu-riset.yaml").exists():
        print(f"{folder}/kartu-riset.yaml belum ada: riset dan verifikasi makalah dulu (lihat /naskah)")
        return 3
    topik = argv[argv.index("--topik") + 1] if "--topik" in argv else ""
    p = folder / "prompt-chatgpt.md"
    p.write_text(buat(folder, topik), encoding="utf-8")
    print(p)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
