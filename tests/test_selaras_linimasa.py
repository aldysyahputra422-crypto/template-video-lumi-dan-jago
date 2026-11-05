import json
import shutil
from pathlib import Path

import pytest

from scripts import linimasa, naskah_format as nf, selaras

ROOT = Path(__file__).resolve().parents[1]
CONTOH = ROOT / "contoh/tenggat-planning-fallacy"


def _naskah(tmp_path):
    shutil.copy(CONTOH / "tempelan.txt", tmp_path / "tempelan.txt")
    shutil.copy(CONTOH / "kartu-riset.yaml", tmp_path / "kartu-riset.yaml")
    assert nf.main([str(tmp_path)]) == 0
    return json.loads((tmp_path / "naskah.json").read_text())


def _transkrip_palsu(n, buang=(), angka_kata=True):
    """Seolah Whisper: kata naskah berurutan, 0,35 dtk per kata, jeda 0,2 antar ketukan; angka diucapkan sebagai kata."""
    t, out = 0.4, []
    for k in n["ketukan"]:
        for w in nf.token(k["ucap"]):
            for sub in (selaras.normal(w) if angka_kata else [w]):
                if sub in buang:
                    continue
                out.append({"k": sub, "a": round(t, 2), "b": round(t + 0.3, 2)})
                t += 0.35
        t += 0.2
    return out


@pytest.mark.parametrize("w,hasil", [("34", ["tiga", "puluh", "empat"]), ("1,6", ["satu", "koma", "enam"]), ("1994", ["seribu", "sembilan", "ratus", "sembilan", "puluh", "empat"]),
                                     ("Kamu,", ["kamu"]), ("file-mu", ["file", "mu"])])
def test_normal(w, hasil):
    assert selaras.normal(w) == hasil


def test_selaras_semua_kata_dapat_waktu_urut(tmp_path):
    n = _naskah(tmp_path)
    k = selaras.selaraskan(n, _transkrip_palsu(n))
    semua = [w for kt in k["ketukan"] for w in kt["kata"]]
    assert len(semua) == sum(len(nf.token(x["ucap"])) for x in n["ketukan"])
    assert all(a["a"] <= b["a"] for a, b in zip(semua, semua[1:]))
    assert k["skor"] > 0.95


def test_kata_hilang_diinterpolasi(tmp_path):
    n = _naskah(tmp_path)
    k = selaras.selaraskan(n, _transkrip_palsu(n, buang={"bohong"}))
    kt2 = k["ketukan"][1]["kata"]
    w = next(x for x in kt2 if x["w"] == "bohong")
    assert kt2[1]["a"] < w["a"] <= kt2[-1]["b"] + 0.5


def test_linimasa_isyarat_ke_waktu_kata(tmp_path):
    n = _naskah(tmp_path)
    kj = selaras.selaraskan(n, _transkrip_palsu(n))
    kartu = __import__("yaml").safe_load((CONTOH / "kartu-riset.yaml").read_text())
    L = linimasa.susun(n, kj, kartu)
    k1 = L["ketukan"][0]
    t_kelar = next(w["a"] for w in kj["ketukan"][0]["kata"] if w["w"] == "kelar")
    assert k1["aksi"][1]["t"] == t_kelar and k1["aksi"][0]["ke"] == "tengah"
    assert all(a["selesai"] == b["mulai"] for a, b in zip(L["ketukan"], L["ketukan"][1:]))   # ketukan bersambung
    kartu_k = next(k for k in L["ketukan"] if k["kartu"])
    t_items = [b["t"] for b in kartu_k["kartu"]["butir"]]
    assert t_items == sorted(t_items) and kartu_k["kartu"]["selesai"] > t_items[-1] + 1.5
    assert "sumber_layar" not in L and L["durasi"] > L["ketukan"][-1]["selesai"] - 0.01
    assert any(s["nama"] == "whoosh" for s in L["sfx"]) and any(s["nama"] == "pop" for s in L["sfx"])


def test_cli_selaras_dengan_transkrip_palsu(tmp_path):
    n = _naskah(tmp_path)
    (tmp_path / "suara.wav").write_bytes(b"x")
    assert selaras.main([str(tmp_path)], transkrip_fn=lambda p: _transkrip_palsu(n)) == 0
    assert (tmp_path / "kata.json").exists()
    assert linimasa.main([str(tmp_path)]) == 0
    assert json.loads((tmp_path / "timeline.json").read_text())["ketukan"][0]["latar"] == "kamar"


def test_linimasa_sisipan_punya_waktu(tmp_path):
    n = _naskah(tmp_path)
    kj = selaras.selaraskan(n, _transkrip_palsu(n))
    L = linimasa.susun(n, kj, None)
    s = next(x for x in L["ketukan"] if (x["sisipan"] or {}).get("nama") == "hp_scroll")
    t_nonton = next(w["a"] for K in kj["ketukan"] for w in K["kata"] if w["w"] == "nonton")
    assert s["sisipan"]["t"] == t_nonton and s["sisipan"]["selesai"] == s["selesai"]
    assert any(x["nama"] == "whoosh" and abs(x["t"] - t_nonton) < 0.01 for x in L["sfx"])
