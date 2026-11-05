"""Draf Jago bergaya datar (kepala dan bahu), digambar lewat kode dan berlapis supaya alis, mata, mulut, dan kacamata bisa diganti.

python -m scripts.gambar_jago_datar  → aset/maskot/datar/jago-{smirk,kaget,juri}.svg
Palet dari config/tokoh.yaml. Draf untuk dinilai pemilik, belum final.
"""
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT, NAVY, NAVY_D, KREM, KREM_D = "#1C2130", "#2B3245", "#232A3B", "#F6E9D8", "#E6CFB2"
COKLAT, ORANYE, PUTIH = "#7A5230", "#D8622B", "#FFFFFF"
G = 'stroke="%s" stroke-width="10" stroke-linejoin="round" stroke-linecap="round"' % OUT


def kepala_berduri(cx=500, cy=500, rx=240, ry=215):
    duri = [(195, 14, 58), (215, 12, 46), (-15, 14, 58), (-35, 12, 46), (78, 11, 52), (98, 12, 60), (118, 10, 44), (60, 10, 42)]
    pts = []
    for d in range(0, 360, 2):
        r = 1.0
        for a, w, h in duri:
            dd = (d - a + 180) % 360 - 180
            if abs(dd) < w:
                r += (1 - abs(dd) / w) * h / ((rx + ry) / 2)
        t = math.radians(d)
        pts.append((cx + rx * r * math.cos(t), cy - ry * r * math.sin(t)))
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + " Z"


def tanduk(sisi):
    m = lambda x: 1000 - x if sisi > 0 else x
    batang = f"M{m(395)},330 C{m(370)},250 {m(345)},200 {m(330)},120"
    cabang = f"M{m(362)},225 C{m(330)},215 {m(305)},205 {m(285)},180 M{m(340)},165 C{m(360)},140 {m(372)},120 {m(380)},95"
    d = batang + " " + cabang
    return (f'<path d="{d}" fill="none" stroke="{OUT}" stroke-width="46" stroke-linecap="round"/>'
            f'<path d="{d}" fill="none" stroke="{COKLAT}" stroke-width="32" stroke-linecap="round"/>')


def telinga(sisi):
    m = lambda x: 1000 - x if sisi > 0 else x
    return (f'<path d="M{m(330)},420 L{m(300)},290 L{m(415)},360 Z" fill="{NAVY}" {G}/>'
            f'<path d="M{m(338)},395 L{m(320)},322 L{m(390)},365 Z" fill="{KREM_D}"/>')


def kumis(sisi):
    m = lambda x: 1000 - x if sisi > 0 else x
    d = f"M{m(404)},612 C{m(330)},606 {m(250)},650 {m(180)},620 C{m(140)},600 {m(150)},556 {m(190)},566"
    return f'<path d="{d}" fill="none" stroke="{OUT}" stroke-width="16" stroke-linecap="round"/><path d="{d}" fill="none" stroke="#4A5372" stroke-width="7" stroke-linecap="round"/>'


def api():
    return (f'<path d="M760,840 C700,800 720,720 760,690 C770,730 790,720 790,690 C830,730 850,800 800,850 Z" fill="{ORANYE}" {G}/>'
            f'<path d="M772,826 C748,800 756,762 772,746 C780,770 792,764 794,750 C812,780 812,812 792,830 Z" fill="#F2B84B"/>')


def badan():
    pola = (f'<pattern id="lurik" width="36" height="36" patternUnits="userSpaceOnUse" patternTransform="rotate(18)">'
            f'<rect width="36" height="36" fill="{NAVY}"/><rect width="14" height="36" fill="{ORANYE}"/></pattern>')
    return (f'<defs>{pola}</defs>'
            f'<path d="M232,1000 C238,862 300,782 400,762 L600,762 C700,782 762,862 768,1000 Z" fill="{NAVY}" {G}/>'
            f'<ellipse cx="500" cy="985" rx="132" ry="112" fill="{KREM}" {G}/>'
            f'<path d="M332,772 Q500,806 668,772 L522,958 Q500,982 478,958 Z" fill="url(#lurik)" {G}/>'
            f'<path d="M652,770 L716,742 L708,800 Z M652,770 L700,812 L650,822 Z" fill="{ORANYE}" {G}/><circle cx="652" cy="778" r="16" fill="{NAVY}" {G}/>'
            f'<path d="M486,928 q14,-18 28,0 q10,12 -4,20 h-20 q-14,-8 -4,-20z" fill="{KREM}" stroke="{OUT}" stroke-width="5"/>')


def wajah_dasar():
    return (f'<path d="{kepala_berduri()}" fill="{NAVY}" {G}/>'
            f'<path d="M330,455 Q500,410 670,455 Q680,540 620,585 L380,585 Q320,540 330,455 Z" fill="#3A4462"/>'
            f'<path d="M398,600 Q400,560 440,552 L560,552 Q600,560 602,600 Q600,690 500,700 Q400,690 398,600 Z" fill="{KREM}" {G}/>'
            f'<ellipse cx="474" cy="578" rx="10" ry="6" fill="{OUT}"/><ellipse cx="526" cy="578" rx="10" ry="6" fill="{OUT}"/>')


def alis(gaya):
    if gaya == "naik":
        kiri, kanan = "M378,410 Q420,385 468,402", "M532,402 Q580,385 622,410"
    elif gaya == "tegas":
        kiri, kanan = "M382,430 L470,458", "M530,458 L618,430"
    else:  # smirk: satu naik, satu datar
        kiri, kanan = "M382,440 L468,452", "M532,446 Q580,420 622,428"
    s = ""
    for d in (kiri, kanan):
        s += f'<path d="{d}" fill="none" stroke="{OUT}" stroke-width="40" stroke-linecap="round"/><path d="{d}" fill="none" stroke="{KREM}" stroke-width="26" stroke-linecap="round"/>'
    return s


def mata(gaya):
    if gaya == "lebar":
        return "".join(f'<circle cx="{x}" cy="492" r="40" fill="{PUTIH}" {G}/><circle cx="{x}" cy="495" r="13" fill="{OUT}"/>' for x in (438, 562))
    # setengah tertutup, melirik (mode jahil)
    s = ""
    for x in (438, 562):
        s += (f'<ellipse cx="{x}" cy="486" rx="34" ry="24" fill="{PUTIH}" {G}/><circle cx="{x + 10}" cy="490" r="12" fill="{OUT}"/>'
              f'<path d="M{x - 38},478 Q{x},464 {x + 38},478 L{x + 38},470 Q{x},456 {x - 38},470 Z" fill="{NAVY}" stroke="{OUT}" stroke-width="8"/>')
    return s


def kacamata(posisi):
    y, rot = {"moncong": (548, 0), "mata": (502, 0), "terbang": (318, -16)}[posisi]
    lensa = "".join(f'<rect x="{x}" y="{y - 32}" width="112" height="64" rx="22" fill="#0E1119" stroke="#9AA3C0" stroke-width="7"/>'
                    f'<path d="M{x + 20},{y - 14} l34,0 M{x + 16},{y + 4} l18,0" stroke="#B9C1DA" stroke-width="8" stroke-linecap="round"/>' for x in (382, 506))
    gagang = f'<path d="M494,{y - 10} Q500,{y - 18} 506,{y - 10}" fill="none" stroke="#9AA3C0" stroke-width="8"/><path d="M392,{y - 14} L300,{y - 30} M608,{y - 14} L700,{y - 30}" stroke="{OUT}" stroke-width="9" stroke-linecap="round"/>'
    return f'<g transform="rotate({rot} 500 {y})">{gagang}{lensa}</g>'


def mulut(gaya):
    if gaya == "o":
        return f'<ellipse cx="500" cy="650" rx="34" ry="28" fill="{OUT}"/><ellipse cx="500" cy="664" rx="20" ry="10" fill="#E07B6A"/>'
    if gaya == "datar":
        return f'<path d="M456,650 Q500,642 544,652" fill="none" stroke="{OUT}" stroke-width="10" stroke-linecap="round"/>'
    return (f'<path d="M440,640 Q500,676 578,628" fill="none" stroke="{OUT}" stroke-width="10" stroke-linecap="round"/>'
            f'<path d="M548,650 L560,676 L570,644 Z" fill="{PUTIH}" stroke="{OUT}" stroke-width="5" stroke-linejoin="round"/>')


def tangan_dua_jari():
    lengan = "M310,860 C270,800 240,740 222,676"
    jari = [("M196,622 L172,528", 0), ("M232,620 L246,524", 0)]
    s = f'<path d="{lengan}" fill="none" stroke="{OUT}" stroke-width="86" stroke-linecap="round"/><path d="{lengan}" fill="none" stroke="{NAVY}" stroke-width="66" stroke-linecap="round"/>'
    for d, _ in jari:
        s += f'<path d="{d}" fill="none" stroke="{OUT}" stroke-width="44" stroke-linecap="round"/><path d="{d}" fill="none" stroke="{KREM}" stroke-width="28" stroke-linecap="round"/>'
    return s + f'<circle cx="214" cy="650" r="50" fill="{KREM}" {G}/><path d="M188,660 q26,14 52,0" fill="none" stroke="{KREM_D}" stroke-width="8"/>'


def kaget_tambahan():
    return (f'<path d="M712,392 q22,34 0,48 q-22,-14 0,-48z" fill="#9CC7E8" stroke="{OUT}" stroke-width="6"/>'
            f'<path d="M250,300 l-40,-30 M232,350 l-52,-6 M760,300 l40,-30 M770,350 l52,-6" stroke="{OUT}" stroke-width="10" stroke-linecap="round"/>')


def svg(isi, transform=""):
    g = f'<g transform="{transform}">{isi}</g>' if transform else isi
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="1000" viewBox="0 0 1000 1000">{g}</svg>'


def pose(nama):
    dasar = api() + badan() + tanduk(-1) + tanduk(1) + telinga(-1) + telinga(1) + wajah_dasar() + kumis(-1) + kumis(1)
    if nama == "smirk":
        return svg(dasar + alis("smirk") + mata("jahil") + kacamata("moncong") + mulut("smirk") + tangan_dua_jari())
    if nama == "kaget":
        return svg(dasar + alis("naik") + mata("lebar") + kacamata("terbang") + mulut("o") + kaget_tambahan())
    if nama == "juri":  # close-up, kacamata menutup mata
        return svg(dasar + alis("tegas") + kacamata("mata") + mulut("datar"), "translate(500 560) scale(1.32) translate(-500 -560)")
    raise ValueError(nama)


def main():
    d = ROOT / "aset/maskot/datar"
    d.mkdir(parents=True, exist_ok=True)
    for n in ("smirk", "kaget", "juri"):
        (d / f"jago-{n}.svg").write_text(pose(n), encoding="utf-8")
        print(d / f"jago-{n}.svg")


if __name__ == "__main__":
    main()
