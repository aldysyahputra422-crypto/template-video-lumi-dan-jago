"""/olah: jalankan seluruh produksi satu episode dan berhenti di titik yang butuh pemilik.

python -m scripts.olah <folder>   → satu baris JSON {kode, berhenti_di, instruksi, ...}
Kode: 0 video jadi dan lulus QA, 1 gagal teknis, 4 Approval 1 (naskah), 5 butuh suara / suara tidak cocok, 6 butuh tempelan atau koreksi.
Urutan: tempelan → naskah.json → lint standar → Approval 1 + lembar ElevenLabs → suara.mp3 → selaras → linimasa → campur → render → QA.
"""
import json
import os
import sys
from pathlib import Path

import yaml

from scripts import campur, lembar, lint_naskah, linimasa, naskah_format, qa, render, selaras


def _baru(a: Path, b: Path) -> bool:
    return a.exists() and (not b.exists() or a.stat().st_mtime > b.stat().st_mtime)


def maju(folder: Path, transkrip_fn=None, fps: int = 30) -> dict:
    f = Path(folder)
    tempel, naskah = f / "tempelan.txt", f / "naskah.json"
    if not tempel.exists() and not naskah.exists():
        return {"kode": 6, "berhenti_di": "tempelan", "instruksi": f"Tempel prompt-chatgpt.md ke ChatGPT, simpan jawabannya sebagai {f}/tempelan.txt, lalu /olah lagi."}
    if _baru(tempel, naskah):
        kode, keluar, _ = naskah_format.proses(f)
        if kode == 7:
            return {"kode": 6, "berhenti_di": "tempelan", "instruksi": "tempelan.txt berubah sesudah naskah disetujui. Kembalikan tempelan, atau set disetujui: false dulu lalu jalankan dengan --timpa."}
        if kode != 0:
            return {"kode": 6, "berhenti_di": "koreksi", "galat": keluar[:12], "instruksi": f"Tempel isi {f}/koreksi-chatgpt.md ke ChatGPT, simpan jawabannya sebagai tempelan.txt, lalu /olah lagi."}
    n = json.loads(naskah.read_text(encoding="utf-8"))
    kp = f / "kartu-riset.yaml"
    lint = lint_naskah.periksa(n, yaml.safe_load(kp.read_text(encoding="utf-8")) if kp.exists() else None)
    (f / "lint.json").write_text(json.dumps(lint, ensure_ascii=False, indent=1), encoding="utf-8")
    if lint["galat"]:
        gal = [naskah_format.Galat(g["baris"], g["pesan"]) for g in lint["galat"]]
        (f / "koreksi-chatgpt.md").write_text(naskah_format.pesan_koreksi(gal), encoding="utf-8")
        if not n.get("disetujui"):
            naskah.unlink()   # naskah yang gagal standar tidak boleh menunggu persetujuan
        return {"kode": 6, "berhenti_di": "koreksi", "galat": [str(g) for g in gal], "instruksi": f"Naskah melanggar standar. Tempel isi {f}/koreksi-chatgpt.md ke ChatGPT, simpan jawabannya sebagai tempelan.txt, lalu /olah lagi."}
    lembar.tulis(f)
    if not n.get("disetujui"):
        return {"kode": 4, "berhenti_di": "approval_1", "perkiraan_durasi": lint["perkiraan_durasi"], "peringatan": [p["pesan"] for p in lint["peringatan"]],
                "instruksi": f"Baca {f}/naskah.json. Bila setuju, ubah \"disetujui\" menjadi true, lalu generate {f}/lembar-elevenlabs.md di ElevenLabs dan simpan sebagai suara.mp3."}
    if not selaras.cari_suara(f):
        return {"kode": 5, "berhenti_di": "suara", "instruksi": f"Generate {f}/lembar-elevenlabs.md di ElevenLabs (voice Ata, Eleven v3), simpan sebagai {f}/suara.mp3, lalu /olah lagi."}
    if selaras.main([str(f)], transkrip_fn=transkrip_fn) != 0:
        return {"kode": 5, "berhenti_di": "suara", "instruksi": "Suara tidak cocok dengan naskah (lihat kata.json). Pastikan seluruh blok lembar ikut di-generate, lalu ganti suara.mp3."}
    try:
        linimasa.main([str(f)])
        campur.jalankan(f)
        render.jalankan(f, fps)
    except Exception as e:  # noqa: BLE001
        return {"kode": 1, "berhenti_di": "render", "alasan": str(e)[:400], "instruksi": "Render gagal; lihat alasan."}
    h = qa.periksa(f)
    return {"kode": 0 if h["lulus"] else 1, "berhenti_di": "selesai" if h["lulus"] else "qa", "qa": h,
            "instruksi": f"Tonton {f}/video.mp4 (Approval 2). Angka QA: {h.get('lufs')} LUFS, puncak {h.get('puncak_dbfs')} dBFS, {h.get('durasi')} dtk."}


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    h = maju(Path(argv[0]))
    print(json.dumps(h, ensure_ascii=False))
    return h["kode"]


if __name__ == "__main__":
    os.chdir(Path(__file__).resolve().parents[1])
    sys.exit(main(sys.argv[1:]))
