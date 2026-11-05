"""Buang bingkai putih seukuran kanvas dari SVG hasil trace, supaya maskot transparan di atas latar apa pun.

python -m scripts.bersihkan_svg <masuk.svg> <keluar.svg>
Bingkai = path PERTAMA yang subpath awalnya menutupi seluruh kanvas (karakter hanya berupa lubang di dalamnya).
Pulau putih = path berisi putih murni (252-255) yang luasnya > 2000 px persegi (sisa trace di celah antar-kaki dst).
Kilau kecil (mata) dan warna krim tidak disentuh.
"""
import re
import sys
from pathlib import Path

PATH_PERTAMA = re.compile(r"<path\b[^>]*?/>", re.S)
TOLERANSI = 1.5


def _kanvas(svg: str) -> tuple[float, float]:
    kepala = svg[: svg.index("<", svg.index("<svg") + 1)] if "<svg" in svg else ""
    w = re.search(r'\bwidth="([\d.]+)"', kepala)
    h = re.search(r'\bheight="([\d.]+)"', kepala)
    return (float(w.group(1)), float(h.group(1))) if w and h else (0.0, 0.0)


def _menutupi_kanvas(tag: str, lebar: float, tinggi: float) -> bool:
    d = re.search(r'\bd="([^"]*)"', tag)
    if not d or not lebar:
        return False
    sub = re.split(r"[Zz]", d.group(1), maxsplit=1)[0]
    angka = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", sub)]
    if len(angka) < 8:
        return False
    xs, ys = angka[0::2], angka[1::2]
    return min(xs) <= TOLERANSI and min(ys) <= TOLERANSI and max(xs) >= lebar - TOLERANSI and max(ys) >= tinggi - TOLERANSI


def punya_bingkai(svg: str) -> bool:
    m = PATH_PERTAMA.search(svg)
    return bool(m) and _menutupi_kanvas(m.group(0), *_kanvas(svg))


def buang_bingkai(svg: str) -> str:
    if not punya_bingkai(svg):
        return svg
    m = PATH_PERTAMA.search(svg)
    return svg[: m.start()] + svg[m.end():]


PUTIH = re.compile(r'fill="rgb\(\s*(25[2-5])\s*,\s*(25[2-5])\s*,\s*(25[2-5])\s*\)"')
LUAS_MIN = 2000.0


def _luas_kotak(tag: str) -> float:
    d = re.search(r'\bd="([^"]*)"', tag)
    angka = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", d.group(1))] if d else []
    if len(angka) < 4:
        return 0.0
    xs, ys = angka[0::2], angka[1::2]
    return (max(xs) - min(xs)) * (max(ys) - min(ys))


def buang_pulau_putih(svg: str, luas_min: float = LUAS_MIN) -> str:
    def ganti(m: re.Match) -> str:
        tag = m.group(0)
        return "" if PUTIH.search(tag) and _luas_kotak(tag) > luas_min else tag
    return PATH_PERTAMA.sub(ganti, svg)


def bersihkan(svg: str) -> str:
    return buang_pulau_putih(buang_bingkai(svg))


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("pakai: python -m scripts.bersihkan_svg <masuk.svg> <keluar.svg>")
        return 2
    svg = Path(argv[0]).read_text(encoding="utf-8")
    hasil = bersihkan(svg)
    Path(argv[1]).write_text(hasil, encoding="utf-8")
    print(f"path dibuang: {svg.count('<path') - hasil.count('<path')}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
