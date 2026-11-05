"""Potong lembar pose (satu gambar berisi banyak pose di atas latar polos) menjadi PNG transparan per pose, lalu SVG.

python -m scripts.potong_pose <lembar.png|webp> <folder_keluar> [nama1,nama2,...]
Deterministik, lokal (vtracer), tanpa layanan berbayar. Urutan pose: per baris dari atas, lalu dari kiri.
"""
import sys
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image

AMBANG = 14          # jarak warna dari latar yang dianggap bukan latar
LUAS_MIN = 1500      # piksel; komponen lebih kecil dianggap coretan dan digabung ke pose terdekat
JARAK_GABUNG = 70
PAD = 6


def _latar(a: np.ndarray) -> np.ndarray:
    pojok = np.concatenate([a[:8, :8].reshape(-1, 3), a[:8, -8:].reshape(-1, 3), a[-8:, :8].reshape(-1, 3), a[-8:, -8:].reshape(-1, 3)])
    return np.median(pojok, axis=0)


def _topeng(im: Image.Image) -> np.ndarray:
    a = np.asarray(im.convert("RGB")).astype(int)
    return np.sqrt(((a - _latar(a)) ** 2).sum(axis=2)) > AMBANG


def _komponen(m: np.ndarray) -> list[tuple[int, int, int, int, int]]:
    """Komponen terhubung (4-arah) pada topeng; kembalikan (x0, y0, x1, y1, luas)."""
    h, w = m.shape
    lihat = np.zeros_like(m, dtype=bool)
    hasil = []
    for y0, x0 in zip(*np.nonzero(m)):
        if lihat[y0, x0]:
            continue
        q = deque([(y0, x0)])
        lihat[y0, x0] = True
        xs, ys, n = [x0, x0], [y0, y0], 0
        while q:
            y, x = q.popleft()
            n += 1
            xs[0], xs[1], ys[0], ys[1] = min(xs[0], x), max(xs[1], x), min(ys[0], y), max(ys[1], y)
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                yy, xx = y + dy, x + dx
                if 0 <= yy < h and 0 <= xx < w and m[yy, xx] and not lihat[yy, xx]:
                    lihat[yy, xx] = True
                    q.append((yy, xx))
        hasil.append((xs[0], ys[0], xs[1] + 1, ys[1] + 1, n))
    return hasil


def cari_pose(im: Image.Image) -> list[tuple[int, int, int, int]]:
    kom = _komponen(_topeng(im))
    besar = [list(k[:4]) for k in kom if k[4] >= LUAS_MIN]
    for x0, y0, x1, y1, n in kom:
        if n >= LUAS_MIN or n < 20:
            continue
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        jarak = lambda b: max(b[0] - cx, 0, cx - b[2]) + max(b[1] - cy, 0, cy - b[3])
        b = min(besar, key=jarak, default=None)
        if b is not None and jarak(b) <= JARAK_GABUNG:
            b[0], b[1], b[2], b[3] = min(b[0], x0), min(b[1], y0), max(b[2], x1), max(b[3], y1)
    # urut per baris: kelompokkan menurut pusat y (toleransi setengah tinggi rata-rata), lalu x
    tinggi = np.mean([b[3] - b[1] for b in besar]) if besar else 1
    besar.sort(key=lambda b: (b[1] + b[3]) / 2)
    baris, kini = [], []
    for b in besar:
        if kini and (b[1] + b[3]) / 2 - (kini[0][1] + kini[0][3]) / 2 > tinggi / 2:
            baris.append(kini)
            kini = []
        kini.append(b)
    if kini:
        baris.append(kini)
    return [tuple(b) for r in baris for b in sorted(r, key=lambda b: b[0])]


def _milik_pose(sub: np.ndarray, asal: tuple[int, int], kotak: tuple) -> np.ndarray:
    """Topeng piksel yang milik pose ini: komponen terbesar + komponen kecil yang seluruhnya di dalam kotak pose."""
    h, w = sub.shape
    label = np.zeros((h, w), dtype=np.int32)
    info, n = [], 0
    for y0, x0 in zip(*np.nonzero(sub)):
        if label[y0, x0]:
            continue
        n += 1
        q = deque([(y0, x0)])
        label[y0, x0] = n
        bx = [x0, y0, x0, y0]
        luas = 0
        while q:
            y, x = q.popleft()
            luas += 1
            bx = [min(bx[0], x), min(bx[1], y), max(bx[2], x), max(bx[3], y)]
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                yy, xx = y + dy, x + dx
                if 0 <= yy < h and 0 <= xx < w and sub[yy, xx] and not label[yy, xx]:
                    label[yy, xx] = n
                    q.append((yy, xx))
        info.append((n, luas, bx))
    if not info:
        return np.ones_like(sub)
    utama = max(info, key=lambda z: z[1])[0]
    kx0, ky0, kx1, ky1 = kotak[0] - asal[0], kotak[1] - asal[1], kotak[2] - asal[0], kotak[3] - asal[1]
    simpan = {utama} | {i for i, luas, b in info if luas >= 80 and b[0] >= kx0 and b[1] >= ky0 and b[2] < kx1 and b[3] < ky1}
    milik = np.isin(label, list(simpan))
    # lubang latar yang terkurung tokoh tetap milik pose
    return milik | (label == 0)


def potong(lembar: Path, folder: Path, nama: list[str] | None = None) -> list[Path]:
    im = Image.open(lembar).convert("RGB")
    m = _topeng(im)
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    hasil = []
    kotak_asli = cari_pose(im)
    for i, (x0, y0, x1, y1) in enumerate(kotak_asli):
        x0, y0 = max(0, x0 - PAD), max(0, y0 - PAD)
        x1, y1 = min(im.width, x1 + PAD), min(im.height, y1 + PAD)
        rgba = im.crop((x0, y0, x1, y1)).convert("RGBA")
        sub = m[y0:y1, x0:x1]
        # latar luar = piksel latar yang terhubung ke tepi potongan; latar yang terkurung di dalam tokoh tetap dipertahankan
        luar = np.zeros_like(sub)
        q = deque([(y, x) for y in range(sub.shape[0]) for x in (0, sub.shape[1] - 1)] + [(y, x) for x in range(sub.shape[1]) for y in (0, sub.shape[0] - 1)])
        while q:
            y, x = q.popleft()
            if 0 <= y < sub.shape[0] and 0 <= x < sub.shape[1] and not sub[y, x] and not luar[y, x]:
                luar[y, x] = True
                q.extend(((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)))
        a = np.asarray(rgba).copy()
        a[luar, 3] = 0
        a[~_milik_pose(sub, (x0, y0), kotak_asli[i]), 3] = 0
        p = folder / f"{(nama or [])[i] if nama and i < len(nama) else f'pose{i + 1:02d}'}.png"
        Image.fromarray(a).save(p)
        hasil.append(p)
    return hasil


def palet(lembar: Image.Image, warna: int = 16, jarak_min: float = 36.0, jumlah_min: int = 80) -> Image.Image:
    """Palet bersama dari warna yang BERBEDA NYATA di lembar (bukan median-cut, yang menghabiskan slot untuk nuansa
    warna dominan). Urut dari yang paling sering; warna diambil bila cukup jauh dari yang sudah terpilih, sehingga
    aksen kecil (api, lidah) dan warna gelap (kaki navy) tetap punya tempat."""
    a = np.asarray(lembar.convert("RGB")).astype(int)
    px = a[np.sqrt(((a - _latar(a)) ** 2).sum(axis=2)) > AMBANG]
    kotak, balik, jumlah = np.unique(px // 16, axis=0, return_inverse=True, return_counts=True)
    rata = np.zeros((len(kotak), 3))
    np.add.at(rata, balik.ravel(), px)
    rata /= jumlah[:, None]          # wakil tiap kelompok = warna rata-rata anggotanya
    pilih: list[np.ndarray] = []
    for i in np.argsort(-jumlah):
        if jumlah[i] < jumlah_min or len(pilih) >= warna:
            break
        c = rata[i]
        if all(np.sqrt(((c - p) ** 2).sum()) > jarak_min for p in pilih):
            pilih.append(c)
    flat = [int(v) for c in pilih for v in c]
    pal = Image.new("P", (1, 1))
    pal.putpalette(flat + flat[:3] * (256 - len(pilih)))
    return pal


def kuantisasi(im: Image.Image, warna: int = 14, pal: Image.Image | None = None) -> Image.Image:
    """Ratakan warna ke palet kecil (gaya warna rata) supaya artefak kompresi tidak jadi ratusan path. Alpha dijaga."""
    im = im.convert("RGBA")
    alpha = im.getchannel("A")
    rgb = im.convert("RGB")
    rgb = (rgb.quantize(palette=pal, dither=Image.Dither.NONE) if pal is not None else
           rgb.quantize(colors=warna, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)).convert("RGB")
    rgb.putalpha(alpha.point(lambda v: 255 if v > 127 else 0))
    return rgb


def vektor(png: Path, keluar: Path, skala: int = 2, warna: int = 14, pal: Image.Image | None = None) -> Path:
    import vtracer
    im = Image.open(png).convert("RGBA")
    besar = Path(keluar).with_suffix(".besar.png")
    kuantisasi(im.resize((im.width * skala, im.height * skala), Image.LANCZOS), warna, pal).save(besar)
    vtracer.convert_image_to_svg_py(str(besar), str(keluar), colormode="color", hierarchical="stacked", mode="spline",
                                    filter_speckle=6, color_precision=6, layer_difference=20, corner_threshold=60,
                                    length_threshold=4.0, max_iterations=10, splice_threshold=45, path_precision=2)
    besar.unlink()
    return Path(keluar)


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    nama = argv[2].split(",") if len(argv) > 2 else None
    pal = palet(Image.open(argv[0]))
    for png in potong(Path(argv[0]), Path(argv[1]), nama):
        svg = vektor(png, png.with_suffix(".svg"), pal=pal)
        print(png.name, Image.open(png).size, svg.name, svg.read_text().count("<path"), "path")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
