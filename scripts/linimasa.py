"""naskah.json + kata.json (+ kartu-riset.yaml) → timeline.json untuk mesin render. Deterministik.

python -m scripts.linimasa <folder>
Setiap isyarat @kata diubah menjadi detik; pemeran, posisi, dan ekspresi dibawa antar ketukan; data dan kartu ditata.
"""
import json
import sys
from pathlib import Path

import yaml

from scripts.selaras import normal

AWAL, EKOR = 0.12, 1.3


def _t(kata: list[dict], cue: str | None, bawaan: float) -> float:
    if not cue:
        return round(bawaan, 3)
    c = "".join(normal(cue))
    for w in kata:
        n = "".join(normal(w["w"]))
        if n == c or w["w"].lower() == cue or (len(cue) >= 4 and w["w"].lower().startswith(cue)):
            return w["a"]
    return round(bawaan, 3)


def susun(n: dict, kj: dict, kartu: dict | None) -> dict:
    ks, KJ = n["ketukan"], kj["ketukan"]
    mulai = [0.0] + [max(0.0, KJ[i]["kata"][0]["a"] - AWAL) for i in range(1, len(ks))]
    akhir = KJ[-1]["kata"][-1]["b"] + EKOR
    selesai = mulai[1:] + [round(akhir, 3)]
    out, sfx = [], []
    pemeran: dict[str, dict] = {}
    data_aktif: list[dict] = []
    latar_lalu = None
    for i, k in enumerate(ks):
        kata, m0, m1 = KJ[i]["kata"], round(mulai[i], 3), round(selesai[i], 3)
        if k["latar"] != latar_lalu and i > 0:
            sfx.append({"nama": "whoosh", "t": m0})
        if i == 0 or k["latar"] != latar_lalu:   # latar berganti: pemeran lama keluar
            pemeran = {}
        latar_lalu = k["latar"]
        for a in k["aktor"]:
            pemeran[a["id"]] = {"peran": a["peran"], "posisi": a["posisi"], "ekspresi": a["ekspresi"]}
        for i_keluar in k["keluar"]:
            pemeran.pop(i_keluar, None)
        awal_pemeran = {i_: dict(v) for i_, v in pemeran.items()}
        aksi = [dict(a, t=_t(kata, a["kata"], m0 + 0.05)) for a in k["aksi"]]
        ekspresi = [dict(e, t=_t(kata, e["kata"], m0 + 0.05)) for e in k["ekspresi"]]
        for a in aksi:                      # posisi akhir dibawa ke ketukan berikutnya
            if a.get("ke") and a["id"] in pemeran:
                pemeran[a["id"]]["posisi"] = a["ke"]
        for e in ekspresi:
            if e["id"] in pemeran:
                pemeran[e["id"]]["ekspresi"] = e["ekspresi"]
        props = [dict(p, t=_t(kata, p["kata"], m0 + 0.05)) for p in k["props"]]
        teks = [dict(x, t=_t(kata, x["kata"], m0 + 0.05)) for x in k["teks"]]
        if k["data"]:
            data_aktif += [dict(d, t=_t(kata, d["kata"], m0 + 0.1)) for d in k["data"]]
            sfx += [{"nama": "tok", "t": d["t"]} for d in data_aktif if m0 <= d["t"] <= m1]
        else:
            data_aktif = []
        kt = None
        if k["kartu"]:
            butir, cari_dari = [], i
            for b in k["kartu"]["butir"]:
                t_b = None
                for j in range(i, min(len(ks), i + 4)):
                    t_cari = _t(KJ[j]["kata"], b["kata"], -1) if b["kata"] else -1
                    if t_cari >= 0 and (not butir or t_cari >= butir[-1]["t"]):
                        t_b, cari_dari = t_cari, j
                        break
                if t_b is None:
                    t_b = (butir[-1]["t"] + 1.2) if butir else m0 + 0.6
                butir.append({"teks": b["teks"], "t": round(t_b, 3)})
                sfx.append({"nama": "tok", "t": round(t_b, 3)})
            j_tahan = min(len(ks) - 1, cari_dari + 1)
            kt = {"judul": k["kartu"]["judul"], "butir": butir, "mulai": m0 + 0.1, "selesai": max(round(selesai[j_tahan], 3), butir[-1]["t"] + 2.0)}
        ata = None
        if k["ata"]:
            ata = dict(k["ata"], mulai=round(m0 - (0.35 if k["ata"]["masuk"] == "sapuan" else 0), 3), selesai=m1)
            sfx.append({"nama": "whoosh" if k["ata"]["masuk"] == "sapuan" else "pop", "t": ata["mulai"]})
        sis = None
        if k.get("sisipan"):
            sis = dict(k["sisipan"], t=_t(kata, k["sisipan"]["kata"], m0 + 0.05), selesai=m1)
            sfx.append({"nama": "whoosh", "t": sis["t"]})
        if k["kamera"] and k["kamera"]["jenis"] == "goyang":
            sfx.append({"nama": "brak", "t": round(m0 + 0.1, 3)})
        out.append({"no": k["no"], "mulai": m0, "selesai": m1, "latar": k["latar"], "pemeran": awal_pemeran, "aksi": aksi, "ekspresi": ekspresi,
                    "props": props, "teks": teks, "data": [dict(d) for d in data_aktif], "kartu": kt, "ata": ata, "kamera": k["kamera"], "fakta": k["fakta"], "sisipan": sis})
    kata = [dict(w, ketukan=K["no"]) for K in KJ for w in K["kata"]]
    return {"id": n["id"], "judul": n["judul"], "fps": 30, "durasi": round(akhir + 0.3, 3), "ketukan": out, "kata": kata,
            "sfx": sorted(sfx, key=lambda s: s["t"])}


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    f = Path(argv[0])
    n = json.loads((f / "naskah.json").read_text(encoding="utf-8"))
    kj = json.loads((f / "kata.json").read_text(encoding="utf-8"))
    kp = f / "kartu-riset.yaml"
    L = susun(n, kj, yaml.safe_load(kp.read_text(encoding="utf-8")) if kp.exists() else None)
    (f / "timeline.json").write_text(json.dumps(L, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"timeline.json: {len(L['ketukan'])} ketukan, {L['durasi']} dtk, {len(L['sfx'])} sfx")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
