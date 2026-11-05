"""Selaraskan SATU file suara (ElevenLabs) dengan naskah per kata, lokal (faster-whisper), tanpa API.

python -m scripts.selaras <folder>   → <folder>/kata.json. Kode 0 lulus, 5 suara belum ada atau tidak cocok dengan naskah.
Angka disamakan dulu ("34" = "tiga puluh empat") lalu urutan kata dicocokkan; kata yang tak terdengar diinterpolasi.
"""
import json
import re
import subprocess
import sys
from difflib import SequenceMatcher
from pathlib import Path

import numpy as np

EKSTENSI = (".mp3", ".wav", ".m4a", ".ogg", ".aac", ".flac", ".webm")
SKOR_MIN = 0.6
SAT = ["nol", "satu", "dua", "tiga", "empat", "lima", "enam", "tujuh", "delapan", "sembilan"]


def angka_ke_kata(n: int) -> list[str]:
    if n < 10:
        return [SAT[n]]
    if n == 10:
        return ["sepuluh"]
    if n == 11:
        return ["sebelas"]
    if n < 20:
        return [SAT[n - 10], "belas"]
    if n < 100:
        p, s = divmod(n, 10)
        return [SAT[p], "puluh"] + (angka_ke_kata(s) if s else [])
    if n < 1000:
        r, s = divmod(n, 100)
        return (["seratus"] if r == 1 else [SAT[r], "ratus"]) + (angka_ke_kata(s) if s else [])
    if n < 1_000_000:
        r, s = divmod(n, 1000)
        return (["seribu"] if r == 1 else angka_ke_kata(r) + ["ribu"]) + (angka_ke_kata(s) if s else [])
    return [str(n)]


def normal(w: str) -> list[str]:
    w = w.lower().strip(".,!?;:\"'()[]")
    if re.fullmatch(r"[0-9]+(?:[.,][0-9]+)?", w):
        bulat, _, pecah = w.replace(".", ",").partition(",")
        return angka_ke_kata(int(bulat)) + (["koma"] + [SAT[int(d)] for d in pecah] if pecah else [])
    return [x for x in re.split(r"[^\w]+", w) if x]


def kata_tampil(ucap: str) -> list[str]:
    return [w.strip(".,!?;:\"'()") for w in ucap.split() if re.search(r"\w", w)]


def selaraskan(naskah: dict, transkrip: list[dict]) -> dict:
    tampil = [(ki, w) for ki, k in enumerate(naskah["ketukan"]) for w in kata_tampil(k["ucap"])]
    S = [(i, s) for i, (_, w) in enumerate(tampil) for s in normal(w)]
    W = []
    for x in transkrip:
        subs = normal(x["k"]) or [x["k"].lower()]
        d = (x["b"] - x["a"]) / len(subs)
        W += [(x["a"] + j * d, x["a"] + (j + 1) * d, s) for j, s in enumerate(subs)]
    sm = SequenceMatcher(None, [s for _, s in S], [s for _, _, s in W], autojunk=False)
    waktu: dict[int, list[float]] = {}
    cocok = 0
    for blk in sm.get_matching_blocks():
        for q in range(blk.size):
            i = S[blk.a + q][0]
            a, b, _ = W[blk.b + q]
            waktu.setdefault(i, [a, b])
            waktu[i] = [min(waktu[i][0], a), max(waktu[i][1], b)]
            cocok += 1
    # interpolasi kata tanpa pasangan: bagi celah antar kata yang cocok menurut panjang huruf
    n = len(tampil)
    i = 0
    akhir_total = W[-1][1] if W else 0.3 + 0.38 * n
    while i < n:
        if i in waktu:
            i += 1
            continue
        j = i
        while j < n and j not in waktu:
            j += 1
        kiri = waktu[i - 1][1] if i > 0 else (W[0][0] if W else 0.3)
        kanan = waktu[j][0] if j < n else max(akhir_total, kiri + 0.38 * (j - i))
        tot = sum(len(tampil[x][1]) for x in range(i, j)) or 1
        c = kiri
        for x in range(i, j):
            d = (kanan - kiri) * len(tampil[x][1]) / tot
            waktu[x] = [c, c + d]
            c += d
        i = j
    hasil = {"skor": round(cocok / max(1, len(S)), 3), "ketukan": [{"no": k["no"], "kata": []} for k in naskah["ketukan"]]}
    for x, (ki, w) in enumerate(tampil):
        hasil["ketukan"][ki]["kata"].append({"w": w, "a": round(waktu[x][0], 3), "b": round(waktu[x][1], 3)})
    return hasil


def cari_suara(folder: Path) -> Path | None:
    for e in EKSTENSI:
        if (folder / f"suara{e}").exists():
            return folder / f"suara{e}"
    return None


def transkrip_lokal(p: Path) -> list[dict]:
    from faster_whisper import WhisperModel
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True, check=True).stdout
    seg, _ = WhisperModel("small", device="cpu", compute_type="int8").transcribe(np.frombuffer(raw, dtype=np.float32), language="id", word_timestamps=True, beam_size=5)
    return [{"k": w.word.strip(), "a": float(w.start), "b": float(w.end)} for s in seg for w in (s.words or [])]


def main(argv: list[str], transkrip_fn=None) -> int:
    if not argv:
        print(__doc__)
        return 2
    folder = Path(argv[0])
    p = cari_suara(folder)
    if not p:
        print(f"belum ada suara: simpan audio ElevenLabs sebagai {folder}/suara.mp3")
        return 5
    n = json.loads((folder / "naskah.json").read_text(encoding="utf-8"))
    h = selaraskan(n, (transkrip_fn or transkrip_lokal)(p))
    (folder / "kata.json").write_text(json.dumps(h, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"skor kecocokan {h['skor']}")
    if h["skor"] < SKOR_MIN:
        print("suara tidak cocok dengan naskah (skor rendah): pastikan seluruh blok lembar ElevenLabs ikut di-generate")
        return 5
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
