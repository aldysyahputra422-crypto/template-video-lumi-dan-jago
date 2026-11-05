from PIL import Image, ImageDraw

from scripts import potong_pose as pp

LATAR = (246, 229, 210)


def _lembar(tmp_path):
    im = Image.new("RGB", (600, 400), LATAR)
    d = ImageDraw.Draw(im)
    d.ellipse((40, 40, 200, 220), fill=(200, 86, 43), outline=(30, 30, 30), width=6)     # pose 1 (baris atas, kiri)
    d.rectangle((300, 50, 450, 230), fill=(43, 50, 69))                                   # pose 2 (baris atas, kanan)
    d.ellipse((120, 270, 280, 380), fill=(246, 233, 216), outline=(30, 30, 30), width=6)  # pose 3 (baris bawah)
    d.line((150, 250, 160, 262), fill=(30, 30, 30), width=4)                              # coretan kecil dekat pose 3
    p = tmp_path / "lembar.png"
    im.save(p)
    return p


def test_mendeteksi_tiga_pose_urut_baris_lalu_kolom(tmp_path):
    kotak = pp.cari_pose(Image.open(_lembar(tmp_path)))
    assert len(kotak) == 3
    assert kotak[0][0] < kotak[1][0] and kotak[2][1] > kotak[0][3] - 10   # urut: atas-kiri, atas-kanan, bawah


def test_coretan_kecil_digabung_ke_pose_terdekat(tmp_path):
    k3 = pp.cari_pose(Image.open(_lembar(tmp_path)))[2]
    assert k3[1] <= 250   # kotak pose 3 ikut mencakup coretan di atasnya


def test_potongan_berlatar_transparan(tmp_path):
    hasil = pp.potong(_lembar(tmp_path), tmp_path / "keluar")
    assert len(hasil) == 3
    im = Image.open(hasil[0]).convert("RGBA")
    assert im.getpixel((0, 0))[3] == 0                      # pojok = latar → transparan
    w, h = im.size
    assert im.getpixel((w // 2, h // 2))[3] == 255          # tengah = tokoh → utuh


def test_vektor_menghasilkan_svg(tmp_path):
    png = pp.potong(_lembar(tmp_path), tmp_path / "keluar")[1]
    svg = pp.vektor(png, tmp_path / "keluar" / "p2.svg")
    teks = svg.read_text()
    assert teks.lstrip().startswith("<?xml") or "<svg" in teks
    assert "<path" in teks


def test_kuantisasi_membatasi_warna_dan_menjaga_alpha(tmp_path):
    import numpy as np
    a = np.zeros((40, 40, 4), dtype=np.uint8)
    a[..., :3] = np.random.default_rng(1).integers(0, 255, (40, 40, 3))
    a[..., 3] = 255
    a[:5, :5, 3] = 0
    p = tmp_path / "acak.png"
    Image.fromarray(a).save(p)
    q = pp.kuantisasi(Image.open(p), warna=8)
    b = np.asarray(q)
    assert len({tuple(x) for x in b[..., :3][b[..., 3] > 0].reshape(-1, 3)}) <= 8
    assert b[0, 0, 3] == 0 and b[20, 20, 3] == 255


def test_serpihan_tetangga_dibuang(tmp_path):
    im = Image.new("RGB", (400, 200), LATAR)
    d = ImageDraw.Draw(im)
    d.rectangle((20, 20, 180, 180), fill=(200, 86, 43))
    d.rectangle((196, 20, 380, 180), fill=(43, 50, 69))   # tetangga sangat dekat (celah 15 px < PAD+...)
    p = tmp_path / "rapat.png"
    im.save(p)
    hasil = pp.potong(p, tmp_path / "k")
    a = Image.open(hasil[0]).convert("RGBA")
    w, h = a.size
    assert a.getpixel((w - 1, h // 2))[3] == 0   # tepi kanan potongan pose 1 tidak berisi warna tetangga


def test_palet_bersama_menjaga_warna_aksen_kecil(tmp_path):
    im = Image.new("RGB", (300, 300), LATAR)
    d = ImageDraw.Draw(im)
    for i in range(3):
        d.rectangle((10 + i * 100, 10, 90 + i * 100, 290), fill=(200, 86, 43))
        d.ellipse((40 + i * 100, 20, 52 + i * 100, 32), fill=(242, 184, 75))   # aksen kecil (api)
    pal = pp.palet(im, 6)
    warna = {tuple(pal.getpalette()[i:i + 3]) for i in range(0, 18, 3)}
    assert any(abs(r - 242) + abs(g - 184) + abs(b - 75) < 40 for r, g, b in warna)
