"""Standar naskah Ata, diperiksa MEKANIS (tanpa LLM). Galat menghentikan produksi; peringatan hanya dicatat.

python -m scripts.lint_naskah <folder>   → baca naskah.json + kartu-riset.yaml, tulis lint.json. Kode 0 lulus, 1 ada galat.
"""
import json
import re
import sys
from pathlib import Path

import yaml

from scripts.naskah_format import token

KATA_PER_DETIK = 2.6
HOOK_MAKS_KATA = 10
TERLARANG = re.compile(r"\b(bodoh|goblok|tolol|bego|idiot|iblis|setan)\b", re.I)
SAPAAN = re.compile(r"\b(kamu|lu|lo|kau|anda)\b|\w+mu\b", re.I)
KONTRADIKSI = re.compile(r"\b(ternyata|bukan|justru|padahal|bohong|salah)\b", re.I)
SATUAN = {"nol": 0, "satu": 1, "dua": 2, "tiga": 3, "empat": 4, "lima": 5, "enam": 6, "tujuh": 7, "delapan": 8, "sembilan": 9}
KATA_ANGKA = set(SATUAN) | {"sepuluh", "sebelas", "belas", "puluh", "seratus", "ratus", "seribu", "ribu", "juta"}


def _kata_ke_angka(kata: list[str]) -> float:
    """Kelompok ribuan, ratusan, puluhan. 'X belas Y puluh Z' dibaca gaya tahun (sembilan belas sembilan puluh empat = 1994)."""
    total = grup = kini = 0
    belas = None
    for x in kata:
        if x in SATUAN:
            kini += SATUAN[x]
        elif x == "sepuluh":
            kini += 10
        elif x == "sebelas":
            kini += 11
        elif x == "belas":
            belas = kini + 10
            grup += belas
            kini = 0
        elif x == "puluh":
            if belas is not None and grup == belas:   # gaya tahun
                grup = belas * 100 + (kini or 1) * 10
            else:
                grup += (kini or 1) * 10
            kini = 0
        elif x == "seratus":
            grup += 100
        elif x == "ratus":
            grup += (kini or 1) * 100
            kini = 0
        elif x == "seribu":
            total += 1000
        elif x in ("ribu", "juta"):
            total += ((grup + kini) or 1) * (1000 if x == "ribu" else 1_000_000)
            grup = kini = 0
    return total + grup + kini


HENTI = {"yang", "dari", "kamu", "itu", "ini", "dan", "atau", "dengan", "untuk", "pada", "karena", "tapi", "juga", "masih", "sudah", "akan"}


def angka_dari_teks(teks: str) -> list[float]:
    """Angka dalam kalimat Indonesia: digit (1,6 / 55) dan kata (tiga puluh empat, lima puluh lima setengah).
    Kata satu/dua/tiga di awal kalimat diikuti koma dianggap penanda daftar, bukan angka."""
    t = re.sub(r"(^|[.!?]\s+)(satu|dua|tiga|empat|lima)\s*,", r"\1", teks.strip(), flags=re.I)
    tk = re.findall(r"[0-9]+(?:,[0-9]+)?|[a-zA-Z]+", t.lower())
    hasil: list[float] = []
    i = 0
    while i < len(tk):
        w = tk[i]
        if w[0].isdigit():
            v = float(w.replace(",", "."))
            if i + 1 < len(tk) and tk[i + 1] == "setengah":
                v += 0.5
                i += 1
            hasil.append(v)
        elif w in KATA_ANGKA:
            kumpul = []
            while i < len(tk) and tk[i] in KATA_ANGKA:
                kumpul.append(tk[i])
                i += 1
            v = _kata_ke_angka(kumpul)
            if i < len(tk) and tk[i] == "setengah":
                v += 0.5
                i += 1
            hasil.append(v)
            continue
        i += 1
    return [int(v) if float(v).is_integer() else round(v, 3) for v in hasil]


def _cocok(v: float, kartu: dict) -> bool:
    nilai = [a["nilai"] for a in kartu.get("angka", [])] + [a["nilai"] for a in kartu.get("turunan", [])] + [kartu.get("tahun")]
    return any(c is not None and abs(v - c) <= max(0.6, 0.02 * abs(c)) for c in nilai)


def periksa(n: dict, kartu: dict | None) -> dict:
    galat, peringatan = [], []
    G = lambda k, pesan: galat.append({"baris": k["baris"] if k else None, "pesan": pesan})
    P = lambda k, pesan: peringatan.append({"baris": k["baris"] if k else None, "pesan": pesan})
    ks = n["ketukan"]
    kata = [len(token(k["ucap"])) for k in ks]
    durasi = round(sum(kata) / KATA_PER_DETIK + 0.15 * len(ks), 1)
    # 1 hook
    if kata[0] > HOOK_MAKS_KATA:
        G(ks[0], f"hook {kata[0]} kata (±{kata[0] / KATA_PER_DETIK:.1f} dtk); maksimal {HOOK_MAKS_KATA} kata supaya selesai dalam 3 detik")
    if not (SAPAAN.search(ks[0]["ucap"]) or KONTRADIKSI.search(ks[0]["ucap"])):
        P(ks[0], "hook tidak menyapa penonton (kamu/-mu) dan tidak membalik dugaan")
    # 2 durasi
    if not 30 <= durasi <= 70:
        G(None, f"perkiraan durasi {durasi} dtk di luar 30 sampai 70 dtk")
    elif not 40 <= durasi <= 55:
        P(None, f"perkiraan durasi {durasi} dtk; sasaran 40 sampai 55 dtk")
    # 3 visual tiap ketukan, panjang ketukan
    for k, nk in zip(ks, kata):
        if not any(k[f] for f in ("aksi", "ekspresi", "props", "teks", "data", "kartu", "ata", "kamera", "aktor")):
            G(k, f"ketukan {k['no']} tanpa isyarat visual (AKSI/EKSPRESI/PROPS/TEKS/DATA/KARTU/ATA/KAMERA)")
        if nk > 16:
            P(k, f"ketukan {k['no']} {nk} kata; pecah supaya visual berganti tiap 2 sampai 5 detik")
        if TERLARANG.search(k["ucap"]):
            G(k, f"kata kasar atau terlarang: {TERLARANG.search(k['ucap']).group(0)}")
    # 4 alat yang disimpan
    if not any(k["kartu"] for k in ks):
        G(None, "tidak ada KARTU (alat maksimal 3 langkah yang membuat penonton menyimpan video)")
    # 5 fakta dan sumber
    fakta = [k for k in ks if k["fakta"]]
    if fakta and not n.get("sumber"):
        G(None, "ada ketukan fakta tetapi tidak ada ##SUMBER <id kartu riset>")
    if fakta and kartu is None:
        G(None, "ada ketukan fakta tetapi kartu-riset.yaml tidak ada")
    if kartu is not None and n.get("sumber") and n["sumber"] != kartu.get("id"):
        G(None, f"##SUMBER {n['sumber']} tidak sama dengan id kartu riset {kartu.get('id')}")
    if kartu is not None:
        for k in fakta:
            for v in angka_dari_teks(k["ucap"]):
                if not _cocok(v, kartu):
                    G(k, f"angka {v} di ketukan fakta {k['no']} tidak ada di kartu riset (angka nyata hanya dari kartu-riset.yaml)")
            for d in k["data"]:
                if not _cocok(d["nilai"], kartu) or not any(abs(d["nilai"] - a["nilai"]) <= 0.05 for a in kartu.get("angka", []) + kartu.get("turunan", [])):
                    G(k, f"DATA {d['label']}={d['nilai']:g} tidak sama persis dengan angka di kartu riset")
    # 6 gaya
    klise = sum(len(re.findall(r"\bbukan\b[^.!?]*,?\s*(tapi|melainkan)\b", k["ucap"], re.I)) for k in ks)
    if klise > 1:
        P(None, f"pola 'bukan X, tapi Y' muncul {klise} kali; maksimal sekali")
    isi = lambda k: {t for t in token(k["ucap"]) if len(t) >= 4 and t not in HENTI}
    if not isi(ks[-1]) & set().union(*(isi(k) for k in ks[: max(3, len(ks) // 2)])):
        P(ks[-1], "penutup tidak melakukan callback ke hook atau cerita awal (tidak ada kata kunci yang sama dengan separuh pertama)")
    ata = sum(1 for k in ks if k["ata"])
    if ata < 2:
        P(None, f"Ata hanya muncul {ata} kali; sasaran di hook, momen penamaan, reaksi, dan penutup")
    elif ata > 0.6 * len(ks):
        P(None, f"Ata muncul di {ata} dari {len(ks)} ketukan; terlalu sering, cerita yang jadi bintang")
    return {"galat": galat, "peringatan": peringatan, "perkiraan_durasi": durasi, "jumlah_ketukan": len(ks), "kata": sum(kata)}


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    folder = Path(argv[0])
    n = json.loads((folder / "naskah.json").read_text(encoding="utf-8"))
    kp = folder / "kartu-riset.yaml"
    r = periksa(n, yaml.safe_load(kp.read_text(encoding="utf-8")) if kp.exists() else None)
    (folder / "lint.json").write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    for g in r["galat"]:
        print(f"GALAT baris {g['baris']}: {g['pesan']}")
    for p in r["peringatan"]:
        print(f"catatan baris {p['baris']}: {p['pesan']}")
    print(f"perkiraan durasi {r['perkiraan_durasi']} dtk, {r['jumlah_ketukan']} ketukan, {r['kata']} kata")
    return 1 if r["galat"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
