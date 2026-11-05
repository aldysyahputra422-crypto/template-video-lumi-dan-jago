"""Periksa aset per video (video/<nama>/aset.js): isi bebas, gaya terkunci. Mekanis, tanpa LLM.

python -m scripts.cek_aset <folder> [--tanpa-lembar]  → kode 0 lulus, 1 ada galat
- menulis aset-dibutuhkan.md (aset yang dideklarasikan naskah di ##ASET, dipakai di ketukan mana, deskripsinya)
- semua aset terdeklarasi wajib ada di aset.js
- tanpa sumber luar (gambar, URL, fetch, import, akses halaman)
- setiap warna hex dekat palet terukur (config/gaya.yaml) atau warna mesin; maksimal 3 aksen khusus (`aksen: [...]`)
- lembar pratinjau aset-cek.png: tiap aset dirender di mesin (latar, tokoh tunggal + kerumunan, props, sisipan)
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import yaml

from scripts import linimasa, naskah_format as nf, selaras

ROOT = Path(__file__).resolve().parents[1]
TOLERANSI = 60
MAKS_AKSEN = 3
LABEL = {"latar": "LATAR", "peran": "AKTOR", "props": "PROPS", "sisipan": "SISIPAN"}
LARANGAN = re.compile(r"<image|https?://|\bfetch\s*\(|\bimport\s*\(|\beval\s*\(|document\.|window\.|XMLHttpRequest|localStorage")


def _hex(w: str) -> str:
    w = w.upper()
    return "#" + "".join(c * 2 for c in w[1:]) if len(w) == 4 else w


def _rgb(w: str) -> np.ndarray:
    w = _hex(w)
    return np.array([int(w[i:i + 2], 16) for i in (1, 3, 5)], float)


def palet() -> list[str]:
    g = yaml.safe_load((ROOT / "config/gaya.yaml").read_text(encoding="utf-8"))["palet"]
    mesin = re.findall(r"#[0-9A-Fa-f]{6}\b", (ROOT / "render/mesin.html").read_text(encoding="utf-8"))
    return sorted({_hex(w) for daftar in g.values() for w in daftar} | {_hex(w) for w in mesin})


def dekat(w: str, daftar: list[str]) -> bool:
    x = _rgb(w)
    return any(np.linalg.norm(x - _rgb(p)) <= TOLERANSI for p in daftar)


def kebutuhan(n: dict) -> list[dict]:
    hasil = []
    for a in n.get("aset", []):
        dipakai = []
        for k in n["ketukan"]:
            nama = a["nama"]
            if (a["jenis"] == "latar" and k["latar"] == nama) or (a["jenis"] == "peran" and any(x["peran"] == nama for x in k["aktor"])) \
                    or (a["jenis"] == "props" and any(p["nama"] == nama for p in k["props"])) or (a["jenis"] == "sisipan" and (k.get("sisipan") or {}).get("nama") == nama):
                dipakai.append(k)
        hasil.append({**a, "ketukan": [{"no": k["no"], "ucap": k["ucap"]} for k in dipakai]})
    return hasil


def tulis_kebutuhan(folder: Path, n: dict) -> Path:
    b = [f"# Aset yang dibutuhkan: {n['id']}", "",
         "Claude menggambar setiap aset di `aset.js` (folder ini) mengikuti `docs/gaya-visual.md`, lalu menjalankan",
         f"`.venv/bin/python -m scripts.cek_aset {folder}` dan melihat `aset-cek.png` sebelum `/olah` lagi.", ""]
    for a in kebutuhan(n):
        b.append(f"## {LABEL[a['jenis']]} `{a['nama']}`")
        b.append(f"- deskripsi: {a['deskripsi']}")
        for k in a["ketukan"]:
            b.append(f"- dipakai di ketukan {k['no']}: \"{k['ucap']}\"")
        b.append("")
    p = Path(folder) / "aset-dibutuhkan.md"
    p.write_text("\n".join(b), encoding="utf-8")
    return p


def _lembar(folder: Path, n: dict) -> Path:
    """Render tiap aset di mesin lewat naskah sintetis, lalu jadikan satu lembar pratinjau."""
    baris = ["##VIDEO cek_aset | Cek aset", "##ASET"] + [f"{LABEL[a['jenis']]} {a['nama']}: {a['deskripsi']}" for a in n["aset"]]
    ketukan = []
    for a in n["aset"]:
        j, nama = a["jenis"], a["nama"]
        if j == "latar":
            ketukan.append([f"LATAR: {nama}", "KAMERA: lebar"])
        elif j == "peran":
            ketukan.append(["LATAR: kosong", f"AKTOR: a=peran_x tengah datar".replace("peran_x", nama), "KAMERA: lebar"])
            ketukan.append(["LATAR: kosong", f"AKTOR: c={nama} tengah datar x7", "KAMERA: lebar"])
        elif j == "props":
            ketukan.append(["LATAR: kosong", f"PROPS: {nama} tengah muncul", "KAMERA: lebar"])
        else:
            ketukan.append(["LATAR: kosong", f"SISIPAN: {nama}"])
    while len(ketukan) < 3:
        ketukan.append(["LATAR: kosong"])
    for i, isi in enumerate(ketukan, 1):
        baris += [f"##KETUKAN {i:02d}", "UCAP: Ini adalah adegan pemeriksaan gaya untuk aset video ini."] + isi
    baris.append("##AKHIR")
    h = nf.urai("\n".join(baris))
    if h.galat:
        raise RuntimeError("naskah sintetis gagal: " + "; ".join(map(str, h.galat[:3])))
    ns, t, kata = h.naskah, 0.4, []
    for k in ns["ketukan"]:
        for w in nf.token(k["ucap"]):
            for sub in selaras.normal(w):
                kata.append({"k": sub, "a": round(t, 2), "b": round(t + 0.3, 2)})
                t += 0.35
        t += 0.2
    L = linimasa.susun(ns, selaras.selaraskan(ns, kata), None)
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "timeline.json").write_text(json.dumps(L), encoding="utf-8")
        shutil.copy(Path(folder) / "aset.js", tmp / "aset.js")
        waktu = ",".join(str(round(k["mulai"] + 1.6, 2)) for k in L["ketukan"])
        r = subprocess.run(["node", str(ROOT / "render/render.js"), str(tmp), str(tmp / "f"), "30", waktu], capture_output=True, text=True, timeout=300)
        if r.returncode != 0:
            raise RuntimeError("render aset gagal: " + (r.stderr or r.stdout)[-600:])
        keluar = Path(folder) / "aset-cek.png"
        kolom = min(4, len(L["ketukan"]))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-pattern_type", "glob", "-i", str(tmp / "f/cek_*.png"),
                        "-vf", f"scale=240:-1,tile={kolom}x{-(-len(L['ketukan']) // kolom)}", "-frames:v", "1", str(keluar)], check=True)
    return keluar


_MUAT = """
const stub = new Proxy(function () { return ''; }, {get: (o, k) => k === 'C' ? new Proxy({}, {get: () => '#000000'}) : k === 'G' ? 1085 : stub, apply: () => ''});
const m = await import(process.argv[1]);
const a = m.default(stub) || {};
console.log(JSON.stringify(Object.fromEntries(['latar', 'peran', 'props', 'sisipan'].map(j => [j, Object.keys(a[j] || {})]))));
"""


def _kunci(js: Path) -> dict:
    """Muat modul aset di Node (tanpa menggambar) dan baca nama aset per bagian."""
    r = subprocess.run(["node", "--input-type=module", "-e", _MUAT, Path(js).resolve().as_uri()], capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout).strip().splitlines()[-1][:300] if (r.stderr or r.stdout).strip() else "galat tak dikenal")
    return json.loads(r.stdout.strip().splitlines()[-1])


def periksa(folder: Path, lembar: bool = True) -> dict:
    folder = Path(folder)
    n = json.loads((folder / "naskah.json").read_text(encoding="utf-8"))
    if not n.get("aset"):
        return {"galat": [], "peringatan": [], "lembar": None}
    tulis_kebutuhan(folder, n)
    js = folder / "aset.js"
    if not js.exists():
        return {"galat": [f"aset.js belum ada: gambar {len(n['aset'])} aset di {folder}/aset.js (lihat aset-dibutuhkan.md)"], "peringatan": [], "lembar": None}
    teks = js.read_text(encoding="utf-8")
    galat = []
    try:
        kunci = _kunci(js)
    except RuntimeError as e:
        return {"galat": [f"aset.js tidak bisa dimuat: {e}"], "peringatan": [], "lembar": None}
    for a in n["aset"]:
        if a["nama"] not in kunci.get(a["jenis"], []):
            galat.append(f"{LABEL[a['jenis']]} '{a['nama']}' belum digambar di aset.js (bagian {a['jenis']})")
    if LARANGAN.search(teks):
        galat.append(f"sumber luar atau akses halaman dilarang di aset.js: '{LARANGAN.search(teks).group(0)}' (semua visual digambar sendiri dengan SVG)")
    m = re.search(r"aksen\s*:\s*\[([^\]]*)\]", teks)
    aksen = [_hex(w) for w in re.findall(r"#[0-9A-Fa-f]{6}\b|#[0-9A-Fa-f]{3}\b", m.group(1))] if m else []
    if len(aksen) > MAKS_AKSEN:
        galat.append(f"aksen khusus {len(aksen)} warna, maksimal {MAKS_AKSEN}")
    boleh = palet() + aksen
    for w in sorted({_hex(x) for x in re.findall(r"#[0-9A-Fa-f]{6}\b|#[0-9A-Fa-f]{3}\b", teks)}):
        if not dekat(w, boleh):
            galat.append(f"warna {w} di luar palet gaya (config/gaya.yaml); pakai token C, warna palet, atau daftarkan sebagai aksen (maks {MAKS_AKSEN})")
    hasil = {"galat": galat, "peringatan": [], "lembar": None}
    if lembar and not galat:
        hasil["lembar"] = str(_lembar(folder, n))
    return hasil


if __name__ == "__main__":
    h = periksa(Path(sys.argv[1]), lembar="--tanpa-lembar" not in sys.argv)
    print(json.dumps(h, ensure_ascii=False, indent=1))
    sys.exit(1 if h["galat"] else 0)
