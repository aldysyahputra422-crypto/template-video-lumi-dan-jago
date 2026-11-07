"""Caption IG mekanis (tanpa LLM): hook, trik dari KARTU, sumber jurnal, tagar. TANPA CTA (aturan akun).

python -m scripts.caption <folder>  → <folder>/caption.txt
Collab dengan @mentoringsobatambis diatur di aplikasi IG saat unggah, bukan ditulis di caption.
"""
import json
import re
import sys
from pathlib import Path

import yaml

from scripts.lint_naskah import AJAKAN

ROOT = Path(__file__).resolve().parents[1]
MAKS_TAGAR = 5


def _akun() -> dict:
    return yaml.safe_load((ROOT / "config/tokoh.yaml").read_text(encoding="utf-8"))["akun"]


def buat(n: dict, kartu: dict | None) -> str:
    bersih = lambda s: re.sub(r"\s+", " ", s.replace("—", ",")).strip()
    bagian = [bersih(n["ketukan"][0]["ucap"])]
    k = next((x["kartu"] for x in n["ketukan"] if x["kartu"]), None)
    if k:
        butir = [bersih(b["teks"]) for b in k["butir"] if not AJAKAN.search(b["teks"])]
        bagian.append(f"{bersih(k['judul'])}:\n" + "\n".join(f"{i}. {b}" for i, b in enumerate(butir, 1)))
    if kartu and kartu.get("kutipan_caption"):
        bagian.append(f"Sumber: {bersih(kartu['kutipan_caption'])}")
    tagar = list(dict.fromkeys(_akun().get("tagar", []) + list((kartu or {}).get("tagar", []))))[:MAKS_TAGAR]
    bagian.append(" ".join(tagar))
    return "\n\n".join(bagian)[:2200]


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    f = Path(argv[0])
    n = json.loads((f / "naskah.json").read_text(encoding="utf-8"))
    kp = f / "kartu-riset.yaml"
    teks = buat(n, yaml.safe_load(kp.read_text(encoding="utf-8")) if kp.exists() else None)
    (f / "caption.txt").write_text(teks + "\n", encoding="utf-8")
    print(f / "caption.txt")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
