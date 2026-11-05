"""Jalur penyelamat: suara sudah direkam dari teks ucapan saja (tanpa format blok). Buat prompt agar ChatGPT HANYA
menambahkan isyarat visual ke kalimat rekaman yang dikunci, lalu periksa bahwa kalimatnya tidak berubah.

python -m scripts.prompt_visual <folder>   (butuh <folder>/rekaman-pemilik.txt: tag di baris sendiri, lalu kalimat)
→ <folder>/prompt-visual.md
"""
import re
import sys
from pathlib import Path

from scripts import prompt_naskah as pn


def rekaman(folder: Path) -> list[str]:
    """Kalimat rekaman pemilik sebagai UCAP ('[tag] kalimat'), urut."""
    hasil = []
    for blok in Path(folder, "rekaman-pemilik.txt").read_text(encoding="utf-8").strip().split("\n\n"):
        baris = [b.strip() for b in blok.strip().splitlines() if b.strip()]
        if baris:
            hasil.append(" ".join(baris))
    return hasil


def _normal(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("“", '"').replace("”", '"')).strip()


def bandingkan(folder: Path, ucap_el: list[str]) -> list[str]:
    """Selisih antara UCAP tempelan dan rekaman pemilik (kosong = sama persis)."""
    rek = rekaman(folder)
    beda = []
    if len(rek) != len(ucap_el):
        beda.append(f"jumlah ketukan {len(ucap_el)}, rekaman {len(rek)} kalimat")
    for i, (a, b) in enumerate(zip(rek, ucap_el), 1):
        if _normal(a) != _normal(b):
            beda.append(f"ketukan {i}: UCAP harus persis '{a}', bukan '{b}'")
    return beda


def buat(folder: Path) -> str:
    folder = Path(folder)
    lengkap = pn.buat(folder)
    a, b = lengkap.index("## 4. Standar naskah"), lengkap.index("## 6. Sebelum mengirim")
    kerangka = "\n\n".join(f"##KETUKAN {i:02d}\nUCAP: {u}\n(isyarat visual di sini)" for i, u in enumerate(rekaman(folder), 1))
    return f"""# Tugas: tambahkan isyarat visual ke naskah "{folder.name}" yang SUARANYA SUDAH DIREKAM

{pn.FORMAT_WAJIB}

Kalimat UCAP di bawah sudah direkam. JANGAN mengubah, menambah, menghapus, atau menggabungkan UCAP dan tagnya, satu huruf pun.
Tugasmu hanya mengisi isyarat visual setiap ketukan (LATAR, AKTOR, AKSI, EKSPRESI, PROPS, SISIPAN, TEKS, DATA, KARTU, ATA, KAMERA,
SUASANA, FAKTA) memakai kosakata dan aturan di bawah. `@kata` harus kata yang ada di UCAP ketukan itu.

## Kerangka (salin, lalu ganti "(isyarat visual di sini)")
```text
##VIDEO {folder.name} | <judul pendek>
##SUMBER <id kartu riset di bawah>

{kerangka}

##AKHIR
```

{lengkap[a:b]}
{pn.FORMAT_WAJIB}
"""


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    f = Path(argv[0])
    p = f / "prompt-visual.md"
    p.write_text(buat(f), encoding="utf-8")
    print(p)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
