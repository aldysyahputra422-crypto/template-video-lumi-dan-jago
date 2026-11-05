"""Lembar tempel ElevenLabs: SATU suara (Ata), semua UCAP berurutan dengan tag audio, siap salin.

python -m scripts.lembar <folder>  → <folder>/lembar-elevenlabs.md
"""
import json
import sys
from pathlib import Path

from scripts import tag as tag_mod


def tulis(folder: Path) -> Path:
    folder = Path(folder)
    n = json.loads((folder / "naskah.json").read_text(encoding="utf-8"))
    kamus = tag_mod.muat()["tag"]
    blok = "\n\n".join(k["ucap_el"] for k in n["ketukan"])
    dipakai = sorted({t for k in n["ketukan"] for t in k["tag"]})
    belum = [(t, kamus[t]) for t in dipakai if kamus[t]["terverifikasi"] == "belum"]
    b = [f"# Lembar ElevenLabs {n['id']}: {n['judul']}", "",
         "Satu kali generate dengan voice Ata (model Eleven v3). Salin seluruh blok di bawah apa adanya, termasuk baris kosong.",
         f"Unduh hasilnya dan simpan sebagai `{folder.name}/suara.mp3`, lalu jalankan `/olah {folder.name}` lagi.",
         "Tag dalam kurung siku adalah arahan suara, bukan teks ucapan. Visual tidak ada di sini (diurus mesin).", "",
         "```text", blok, "```"]
    if belum:
        b += ["", "## Tag belum terverifikasi di naskah ini", "Bila tidak berpengaruh, ganti dengan cadangan lalu generate ulang:", ""]
        b += [f"- {t}: {v['elevenlabs']} → cadangan {v.get('cadangan', '-')}" for t, v in belum]
    p = folder / "lembar-elevenlabs.md"
    p.write_text("\n".join(b) + "\n", encoding="utf-8")
    return p


if __name__ == "__main__":
    print(tulis(Path(sys.argv[1])))
