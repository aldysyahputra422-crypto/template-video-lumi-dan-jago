"""Pustaka SFX: buat SFX dan musik latar sintetis (deterministik, bebas lisensi) dan unduh SFX Mixkit terkatalog.

python -m scripts.sfx sintetis   → aset/audio/sintetis/<nama>.wav (dibuat ulang, tidak masuk git)
python -m scripts.sfx unduh      → aset/audio/unduhan/<nama>.mp3 dari Mixkit (lisensi di katalog/sfx.yaml, tidak masuk git)
python -m scripts.sfx semua      → keduanya (dipakai hook SessionStart)
Tanpa LLM dan tanpa API berbayar. Sintetis selalu ada sebagai cadangan bila unduhan gagal.
"""
import subprocess
import sys
import zlib
from pathlib import Path

import numpy as np
import soundfile as sf
import yaml

ROOT = Path(__file__).resolve().parents[1]
KATALOG = ROOT / "katalog/sfx.yaml"
SINTETIS = ROOT / "aset/audio/sintetis"
UNDUHAN = ROOT / "aset/audio/unduhan"
PEMILIK = ROOT / "aset/audio"
SR = 44100
URL_MIXKIT = "https://assets.mixkit.co/active_storage/sfx/{id}/{id}-preview.mp3"


def katalog() -> dict:
    return yaml.safe_load(KATALOG.read_text(encoding="utf-8"))


# ---------- bahan dasar ----------
def _t(d):
    return np.arange(int(SR * d)) / SR


def _rng(nama):
    return np.random.default_rng(zlib.crc32(nama.encode()))


def _turun(n, laju):
    return np.exp(-np.arange(n) / SR * laju)


def _pita(x, lo, hi):
    """Filter pita lewat FFT (cukup untuk derau)."""
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(X, len(x))


def _sapuan(r, d, f0, f1, lebar=0.6):
    """Derau yang pusat frekuensinya bergeser f0 → f1 (whoosh, swipe), per potongan 1024 sampel."""
    n, x, k = int(SR * d), r.standard_normal(int(SR * d)), 1024
    y = np.zeros(n)
    for i in range(0, n, k):
        fc = f0 + (f1 - f0) * (i / n)
        y[i:i + k] = _pita(x[i:i + k], fc * (1 - lebar), fc * (1 + lebar))[: len(y[i:i + k])]
    return y


def _nada(f, d, laju=8.0):
    t = _t(d)
    return np.sin(2 * np.pi * np.cumsum(np.broadcast_to(f, t.shape)) / SR) * _turun(len(t), laju)


def _taruh(dasar, x, detik):
    i = int(detik * SR)
    k = min(len(x), len(dasar) - i)
    if k > 0:
        dasar[i:i + k] += x[:k]
    return dasar


# ---------- SFX ----------
def _sfx(nama: str) -> np.ndarray:
    r = _rng(nama)
    if nama == "whoosh":
        d = .6; return _sapuan(r, d, 300, 2600) * np.sin(np.pi * _t(d) / d) ** 2
    if nama == "swipe":
        d = .25; return _sapuan(r, d, 1800, 6000, .4) * np.sin(np.pi * _t(d) / d)
    if nama in ("pop", "jumput"):
        d = .12 if nama == "pop" else .09; t = _t(d); f0 = 900 if nama == "pop" else 1300
        return _nada(f0 * np.exp(-t * 18), d, 30) + .3 * r.standard_normal(len(t)) * _turun(len(t), 400)
    if nama == "tok":
        d = .08; return _nada(1200, d, 60) + .4 * _pita(r.standard_normal(int(SR * d)), 2000, 6000) * _turun(int(SR * d), 300)
    if nama == "tik_cepat":
        y = np.zeros(int(SR * 2.0))
        for i in range(16):
            klik = _nada(3200 if i % 2 else 2500, .03, 200) + .5 * _pita(r.standard_normal(int(SR * .03)), 3000, 8000) * _turun(int(SR * .03), 300)
            _taruh(y, klik, i * .125)
        return y
    if nama == "sobek":
        d = .35; x = _pita(r.standard_normal(int(SR * d)), 1500, 7000)
        return x * (r.random(len(x)) > .6) * np.sin(np.pi * _t(d) / d) * 2
    if nama in ("gores", "ketik"):
        d = 1.5; y = np.zeros(int(SR * d))
        if nama == "gores":
            x = _pita(r.standard_normal(len(y)), 2500, 7500); return x * np.abs(np.sin(2 * np.pi * 3.2 * _t(d))) ** 2
        s = 0.0
        while s < d - .05:
            _taruh(y, _pita(r.standard_normal(int(SR * .03)), 1500, 6000) * _turun(int(SR * .03), 250), s); s += .06 + .09 * r.random()
        return y
    if nama == "detak":
        y = np.zeros(int(SR * .8))
        _taruh(y, _nada(55, .2, 18), 0); _taruh(y, .7 * _nada(48, .2, 20), .24)
        return y
    if nama == "stinger":
        d = 1.0; t = _t(d)
        return _nada(48, d, 4) + .6 * _pita(r.standard_normal(len(t)), 40, 900) * _turun(len(t), 8) + .25 * _nada(200 * np.exp(t * 1.4), d, 3)
    if nama == "boing":
        d = .5; t = _t(d); return _nada(220 + 140 * np.sin(2 * np.pi * 12 * t) * np.exp(-t * 5), d, 6)
    if nama == "langkah":
        d = .25; return .8 * _pita(r.standard_normal(int(SR * d)), 60, 900) * _turun(int(SR * d), 30) + _nada(110, d, 30)
    if nama == "notif":
        y = np.zeros(int(SR * .4)); _taruh(y, _nada(880, .2, 18), 0); _taruh(y, _nada(1320, .25, 14), .1); return y
    if nama == "benar":
        y = np.zeros(int(SR * .55))
        for i, f in enumerate((660, 830, 990)):
            _taruh(y, _nada(f, .3, 10), i * .08)
        return y
    if nama == "salah":
        d = .5; t = _t(d); return np.sign(np.sin(2 * np.pi * 150 * t)) * .5 * _turun(len(t), 4)
    if nama == "printer":
        d = 1.6; t = _t(d); gerigi = 2 * ((t * 100) % 1) - 1
        return .4 * gerigi * (np.sin(2 * np.pi * 8 * t) > 0) + .2 * _pita(r.standard_normal(len(t)), 500, 3000)
    if nama == "brak":
        d = .5; return _pita(r.standard_normal(int(SR * d)), 40, 700) * _turun(int(SR * d), 12) * 1.5 + _nada(70, d, 10)
    if nama == "kilau":
        y = np.zeros(int(SR * .6))
        for i in range(7):
            _taruh(y, .5 * _nada(2000 + 2000 * r.random(), .15, 25), i * .07)
        return y
    if nama == "tumbuh":
        d = 1.5; return _sapuan(r, d, 100, 1200, .5) * np.linspace(.2, 1, int(SR * d)) + .2 * _nada(80 + 40 * _t(d), d, 1)
    raise KeyError(nama)


# ---------- musik latar (loop 16 dtk) ----------
def _pad(akor, d, tremolo=.15, laju_trem=.25):
    t = _t(d)
    y = sum(np.sin(2 * np.pi * f * t) + .3 * np.sin(2 * np.pi * 2 * f * t) for f in akor) / len(akor)
    return y * (1 - tremolo + tremolo * np.sin(2 * np.pi * laju_trem * t))


def _musik(nama: str) -> np.ndarray:
    r, d = _rng(nama), 16.0
    t = _t(d)
    if nama == "musik_normal":
        y = .5 * _pad((261.6, 329.6, 392.0, 493.9), d)
        for i in range(16):
            _taruh(y, .25 * _nada((523.3, 659.3, 784.0, 659.3)[i % 4], .5, 6), i)
        return y
    if nama == "musik_tegang":
        y = .6 * _pad((110.0, 116.5, 164.8), d, .3, 2)
        for i in range(32):
            _taruh(y, .5 * _nada(55, .2, 15), i * .5)
        return y
    if nama == "musik_ceria":
        y = .35 * _pad((261.6, 329.6, 392.0), d)
        for i in range(64):
            _taruh(y, .3 * _nada((523.3, 587.3, 659.3, 784.0)[i % 4], .2, 12), i * .25)
        return y
    if nama == "musik_horor":
        y = .7 * _pad((55.0, 58.3), d, .4, .13) + .25 * _sapuan(r, d, 150, 400, .5) * (.6 + .4 * np.sin(2 * np.pi * .07 * t))
        for i in range(13):
            _taruh(y, _sfx("detak"), .4 + i * 1.2)
        return y
    if nama == "musik_sedih":
        return .55 * _pad((220.0, 261.6, 329.6), d, .1, .12) + .2 * _pad((174.6, 220.0, 261.6), d, .1, .09)
    if nama == "musik_misterius":
        y = .5 * _pad((146.8, 207.7, 293.7), d, .25, .2)
        for i in range(8):
            _taruh(y, .3 * _nada(1174.7 + 300 * r.random(), .8, 3), i * 2 + .7)
        return y
    raise KeyError(nama)


def _tulis(p: Path, x: np.ndarray) -> None:
    x = np.asarray(x, dtype=np.float64)
    x = x / max(1e-9, np.abs(x).max()) * 0.7     # puncak -3 dBFS
    p.parent.mkdir(parents=True, exist_ok=True)
    sf.write(p, x.astype(np.float32), SR, subtype="PCM_16")


def buat_sintetis(folder: Path = SINTETIS) -> list[Path]:
    k, hasil = katalog(), []
    for nama in k["sfx"]:
        _tulis(Path(folder) / f"{nama}.wav", _sfx(nama)); hasil.append(Path(folder) / f"{nama}.wav")
    for nama in k["musik"]:
        _tulis(Path(folder) / f"{nama}.wav", _musik(nama)); hasil.append(Path(folder) / f"{nama}.wav")
    return hasil


def unduh(folder: Path = UNDUHAN) -> dict:
    """Unduh pratinjau MP3 Mixkit yang terkatalog. Gagal jaringan = dilewati (sintetis tetap dipakai)."""
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    hasil = {"terunduh": [], "sudah_ada": [], "gagal": []}
    for nama, e in katalog()["sfx"].items():
        if "mixkit" not in e:
            continue
        p = folder / f"{nama}.mp3"
        if p.exists() and p.stat().st_size > 1000:
            hasil["sudah_ada"].append(nama); continue
        r = subprocess.run(["curl", "-sSfL", "-m", "60", "-o", str(p), URL_MIXKIT.format(id=e["mixkit"])], capture_output=True)
        ok = r.returncode == 0 and p.exists() and p.stat().st_size > 1000
        if not ok:
            p.unlink(missing_ok=True)
        hasil["terunduh" if ok else "gagal"].append(nama)
    return hasil


def cari(nama: str, sintetis: Path = SINTETIS, unduhan: Path = UNDUHAN, pemilik: Path = PEMILIK) -> Path | None:
    """Unduhan Mixkit → aset pemilik → sintetis."""
    for p in (Path(unduhan) / f"{nama}.mp3", Path(pemilik) / f"{nama}.mp3", Path(sintetis) / f"{nama}.wav"):
        if p.exists():
            return p
    return None


def gain(nama: str) -> float:
    k = katalog()
    return float((k["sfx"].get(nama) or k["musik"].get(nama) or {}).get("gain", 0))


if __name__ == "__main__":
    perintah = sys.argv[1] if len(sys.argv) > 1 else "semua"
    if perintah in ("sintetis", "semua"):
        print(f"sintetis: {len(buat_sintetis())} berkas")
    if perintah in ("unduh", "semua"):
        print(unduh())
