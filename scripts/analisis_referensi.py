"""Analisis satu video referensi menjadi angka terukur, deterministik, tanpa LLM dan tanpa layanan berbayar.

python -m scripts.analisis_referensi <video> <folder_keluar> [--tanpa-lembar]
Keluaran di folder: analisis.json (angka turunan, aman masuk repo) dan lembar.png (kontak frame tiap 3 dtk,
untuk dilihat; berisi cuplikan video pihak lain, jangan di-commit).
Transkrip memakai faster-whisper lokal (model unduhan sekali). Audio diberikan sebagai array numpy karena
decode_audio bawaan faster-whisper bentrok dengan versi PyAV tertentu.
"""
import json
import re
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path

AMBANG_POTONGAN = 0.25
JEDA_KALIMAT = 0.45
LEMBAR_TIAP = 3
LEMBAR_KOLOM = 7


def _jalankan(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, check=True)


def probe(video: Path) -> dict:
    j = json.loads(_jalankan(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(video)]).stdout)
    v = next(s for s in j["streams"] if s["codec_type"] == "video")
    au = next((s for s in j["streams"] if s["codec_type"] == "audio"), None)
    n, d = v["r_frame_rate"].split("/")
    return {"durasi": round(float(j["format"]["duration"]), 2), "lebar": int(v["width"]), "tinggi": int(v["height"]),
            "fps": round(int(n) / int(d), 2), "ukuran_mb": round(int(j["format"]["size"]) / 1e6, 2),
            "ada_audio": au is not None, "audio_hz": int(au["sample_rate"]) if au else None}


def potongan(video: Path, ambang: float = AMBANG_POTONGAN) -> list[float]:
    """Waktu potongan keras (perubahan adegan). Gaya kamera kontinu menghasilkan sedikit potongan."""
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", str(video), "-vf", f"select='gt(scene,{ambang})',showinfo", "-an", "-f", "null", "-"],
                       capture_output=True, text=True)
    return [round(float(x), 2) for x in re.findall(r"pts_time:([0-9.]+)", r.stderr)]


def loudness(video: Path) -> dict:
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", str(video), "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True)
    ringkas = r.stderr[r.stderr.rindex("Summary:"):]
    ambil = lambda pola: float(re.search(pola, ringkas).group(1))
    return {"lufs": ambil(r"I:\s+(-?[0-9.]+) LUFS"), "rentang_lu": ambil(r"LRA:\s+(-?[0-9.]+) LU"), "puncak_dbfs": ambil(r"Peak:\s+(-?[0-9.]+) dBFS")}


def transkrip_lokal(wav: Path) -> list[dict]:
    import numpy as np  # noqa: F401
    import soundfile as sf
    from faster_whisper import WhisperModel
    y, sr = sf.read(wav, dtype="float32")
    assert sr == 16000
    seg, _ = WhisperModel("small", device="cpu", compute_type="int8").transcribe(y, language="id", word_timestamps=True, beam_size=5)
    return [{"k": w.word.strip(), "a": round(w.start, 2), "b": round(w.end, 2)} for s in seg for w in (s.words or [])]


def statistik_kata(kata: list[dict]) -> dict:
    if not kata:
        return {"jumlah_kata": 0, "kata_per_detik": 0.0, "jeda_terpanjang": 0.0, "jeda_di_atas_0_45": 0}
    durasi = kata[-1]["b"] - kata[0]["a"]
    jeda = [b["a"] - a["b"] for a, b in zip(kata, kata[1:])]
    return {"jumlah_kata": len(kata), "kata_per_detik": round(len(kata) / durasi, 2) if durasi else 0.0,
            "rata2_durasi_kata": round(statistics.mean(k["b"] - k["a"] for k in kata), 2),
            "jeda_terpanjang": round(max(jeda, default=0.0), 2), "jeda_di_atas_0_45": sum(g >= JEDA_KALIMAT for g in jeda)}


def kalimat(kata: list[dict], jeda: float = JEDA_KALIMAT) -> list[dict]:
    """Kelompok kata yang dipisah jeda >= `jeda` detik: pendekatan kasar atas frasa/kalimat."""
    if not kata:
        return []
    grup = [[kata[0]]]
    for a, b in zip(kata, kata[1:]):
        (grup.append([b]) if b["a"] - a["b"] >= jeda else grup[-1].append(b))
    return [{"mulai": g[0]["a"], "selesai": g[-1]["b"], "teks": " ".join(x["k"] for x in g)} for g in grup]


def hook(kata: list[dict], detik: float = 3.0) -> str:
    return " ".join(k["k"] for k in kata if k["a"] < detik)


def lembar(video: Path, keluar: Path, tiap: int = LEMBAR_TIAP, kolom: int = LEMBAR_KOLOM) -> Path:
    total = probe(video)["durasi"]
    baris = max(1, -(-int(total / tiap) // kolom))
    _jalankan(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-vf", f"fps=1/{tiap},scale=180:-1,tile={kolom}x{baris}", "-frames:v", "1", str(keluar)])
    return keluar


def analisis(video: Path, folder: Path, transkrip_fn=None, lembar_png: bool = True, **kw) -> dict:
    video, folder = Path(video), Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    lembar_png = kw.get("lembar", lembar_png)
    p = probe(video)
    kata: list[dict] = []
    if p["ada_audio"]:
        with tempfile.TemporaryDirectory() as t:
            wav = Path(t) / "a.wav"
            _jalankan(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-ac", "1", "-ar", "16000", str(wav)])
            kata = (transkrip_fn or transkrip_lokal)(wav)
    cut = potongan(video)
    hasil = {"berkas": video.name[:60], "teknis": p, "loudness": loudness(video) if p["ada_audio"] else None,
             "potongan_keras": {"jumlah": len(cut), "waktu": cut, "per_menit": round(len(cut) / p["durasi"] * 60, 1)},
             "suara": statistik_kata(kata), "hook": hook(kata), "kalimat": kalimat(kata), "kata": kata}
    (folder / "analisis.json").write_text(json.dumps(hasil, ensure_ascii=False, indent=1), encoding="utf-8")
    if lembar_png:
        lembar(video, folder / "lembar.png")
    return hasil


def main(argv: list[str]) -> int:
    pos = [x for x in argv if not x.startswith("--")]
    if len(pos) != 2:
        print("pakai: python -m scripts.analisis_referensi <video> <folder_keluar> [--tanpa-lembar]")
        return 2
    h = analisis(Path(pos[0]), Path(pos[1]), lembar_png="--tanpa-lembar" not in argv)
    s, t = h["suara"], h["teknis"]
    print(f"{t['durasi']} dtk {t['lebar']}x{t['tinggi']} {t['fps']}fps | {s['jumlah_kata']} kata, {s['kata_per_detik']}/dtk | "
          f"potongan keras {h['potongan_keras']['jumlah']} | {h['loudness']['lufs'] if h['loudness'] else '-'} LUFS | hook: {h['hook']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
