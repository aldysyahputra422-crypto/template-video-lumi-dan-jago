import json
import shutil
import subprocess
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

from scripts import campur, naskah_format as nf, olah, qa

ROOT = Path(__file__).resolve().parents[1]
CONTOH = ROOT / "contoh/tenggat-planning-fallacy"


def _timeline_sederhana(f: Path, durasi=4.0):
    tl = {"durasi": durasi, "sfx": [{"nama": "pop", "t": 0.5}, {"nama": "whoosh", "t": 2.0}], "kata": [{"w": "halo", "a": 0.2, "b": 0.6, "ketukan": 1}]}
    (f / "timeline.json").write_text(json.dumps(tl))
    sr = 44100
    tt = np.arange(int(3.5 * sr)) / sr
    sf.write(f / "suara.wav", (0.3 * np.sin(2 * np.pi * 220 * tt)).astype(np.float32), sr)


def test_campur_mencapai_target_loudness(tmp_path):
    _timeline_sederhana(tmp_path)
    p = campur.jalankan(tmp_path)
    y, sr = sf.read(p)
    assert sr == 44100 and abs(len(y) / sr - 4.0) < 0.05
    r = qa.loudness(p)
    assert abs(r["lufs"] + 14) <= 1.0 and r["puncak_dbfs"] <= -1.0


def test_qa_menilai_video(tmp_path):
    _timeline_sederhana(tmp_path)
    campur.jalankan(tmp_path)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=black:s=720x1280:r=30:d=4", "-i", str(tmp_path / "campur.wav"),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(tmp_path / "video.mp4")], check=True)
    h = qa.periksa(tmp_path)
    assert not h["lulus"] and any("gerak" in m for m in h["masalah"]), h   # layar diam = membosankan, ditolak
    assert h["resolusi"] == [720, 1280] and abs(h["durasi"] - 4.0) < 0.2
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "life=s=720x1280:r=30:mold=10:ratio=0.3", "-t", "4", "-i", str(tmp_path / "campur.wav"),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(tmp_path / "video.mp4")], check=True)
    h = qa.periksa(tmp_path)
    assert h["lulus"], h["masalah"]
    assert {"gerak_rata", "persen_diam", "diam_terpanjang", "beda_3dtk"} <= set(h["gerak"])


def _ep(tmp_path):
    f = tmp_path / "ep"
    f.mkdir()
    shutil.copy(CONTOH / "tempelan.txt", f / "tempelan.txt")
    shutil.copy(CONTOH / "kartu-riset.yaml", f / "kartu-riset.yaml")
    return f


def test_olah_berhenti_di_titik_pemilik(tmp_path):
    kosong = tmp_path / "kosong"
    kosong.mkdir()
    assert olah.maju(kosong)["kode"] == 6                      # belum ada tempelan
    f = _ep(tmp_path)
    (f / "tempelan.txt").write_text((CONTOH / "tempelan.txt").read_text().replace("LATAR: kamar", "LATAR: planet_mars"))
    h = olah.maju(f)
    assert h["kode"] == 6 and (f / "koreksi-chatgpt.md").exists()
    shutil.copy(CONTOH / "tempelan.txt", f / "tempelan.txt")
    h = olah.maju(f)
    assert h["kode"] == 4 and (f / "lembar-elevenlabs.md").exists() and "disetujui" in h["instruksi"]
    n = json.loads((f / "naskah.json").read_text())
    n["disetujui"] = True
    (f / "naskah.json").write_text(json.dumps(n))
    h = olah.maju(f)
    assert h["kode"] == 5 and "suara.mp3" in h["instruksi"]


def test_olah_lint_gagal_ditulis_ke_koreksi(tmp_path):
    f = _ep(tmp_path)
    (f / "tempelan.txt").write_text((CONTOH / "tempelan.txt").read_text().replace("Rata-rata nebak 34 hari.", "Rata-rata nebak 44 hari.").replace("@34", "@44"))
    h = olah.maju(f)
    assert h["kode"] == 6 and "44" in (f / "koreksi-chatgpt.md").read_text()


@pytest.mark.lambat
def test_ujung_ke_ujung_render_video(tmp_path):
    """Tempelan → naskah → (disetujui) → suara palsu + transkrip palsu → linimasa → render → mix → QA."""
    f = _ep(tmp_path)
    olah.maju(f)
    n = json.loads((f / "naskah.json").read_text())
    n["disetujui"] = True
    (f / "naskah.json").write_text(json.dumps(n))
    # suara dan transkrip palsu: 0,35 dtk per kata
    from scripts import selaras
    t, kata = 0.3, []
    for k in n["ketukan"]:
        for w in selaras.kata_tampil(k["ucap"]):
            kata.append({"k": w, "a": t, "b": t + 0.3})
            t += 0.35
        t += 0.15
    sr = 44100
    sf.write(f / "suara.wav", (0.2 * np.sin(2 * np.pi * 200 * np.arange(int((t + 0.5) * sr)) / sr)).astype(np.float32), sr)
    h = olah.maju(f, transkrip_fn=lambda p: kata, fps=10)
    assert h["kode"] == 0, h
    q = json.loads((f / "qa.json").read_text())
    assert q["lulus"], q["masalah"]
    assert (f / "video.mp4").exists()


def test_olah_menolak_ucap_yang_beda_dari_rekaman(tmp_path):
    f = _ep(tmp_path)
    n = nf.urai((f / "tempelan.txt").read_text(encoding="utf-8")).naskah
    kal = [k["ucap_el"] for k in n["ketukan"]]
    kal[0] = kal[0].replace("tiga hari", "dua hari")
    (f / "rekaman-pemilik.txt").write_text("\n\n".join(kal) + "\n", encoding="utf-8")
    h = olah.maju(f)
    assert h["kode"] == 6 and "rekaman" in h["instruksi"] and "ketukan 1" in (f / "koreksi-chatgpt.md").read_text(encoding="utf-8")


def test_olah_berhenti_untuk_aset_baru_sesudah_persetujuan(tmp_path, monkeypatch):
    monkeypatch.setattr(olah.lint_naskah, "periksa", lambda n, k: {"galat": [], "peringatan": [], "perkiraan_durasi": 50})   # fixture minimal
    F = ROOT / "tests/fixtures/aset_uji"
    f = tmp_path / "aset"
    f.mkdir()
    shutil.copy(F / "tempelan.txt", f / "tempelan.txt")
    assert olah.maju(f)["kode"] == 4                                   # persetujuan naskah dulu
    n = json.loads((f / "naskah.json").read_text(encoding="utf-8"))
    n["disetujui"] = True
    (f / "naskah.json").write_text(json.dumps(n), encoding="utf-8")
    h = olah.maju(f)
    assert h["kode"] == 8 and h["berhenti_di"] == "aset" and (f / "aset-dibutuhkan.md").exists()
    shutil.copy(F / "aset.js", f / "aset.js")
    assert olah.maju(f)["kode"] == 5                                   # aset lengkap: lanjut ke suara
