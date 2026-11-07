"""Caption IG mekanis: hook, trik dari KARTU, sumber jurnal, tagar; TANPA ajakan jualan (akun tanpa CTA)."""
from pathlib import Path

import yaml

from scripts import caption, lint_naskah as ln, naskah_format as nf

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "contoh/kedai-5whys"


def test_caption_dari_naskah_dan_kartu():
    n = nf.urai((D / "tempelan.txt").read_text(encoding="utf-8")).naskah
    kartu = yaml.safe_load((D / "kartu-riset.yaml").read_text(encoding="utf-8"))
    c = caption.buat(n, kartu)
    assert c.startswith("Ratusan mahasiswa lewat depan kedai Raka. Nol yang beli.")
    assert "Kenapa terjadi?" in c and "Card (2016)" in c and "#atangulik" in c
    assert not ln.AJAKAN.search(c) and "—" not in c and "[" not in c
    assert len(c) <= 2200 and c.count("#") <= 5
