"""Tag ekspresi suara ElevenLabs dari config/tag_ekspresi.yaml. Deterministik; tag tak dikenal ditolak."""
import functools
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


class TagTidakDikenal(ValueError):
    pass


@functools.lru_cache(maxsize=None)
def muat() -> dict:
    return yaml.safe_load((ROOT / "config/tag_ekspresi.yaml").read_text(encoding="utf-8"))


def pisah(ucap: str) -> tuple[str, list[str], str]:
    """'[tense, slowly] Teks' → (teks bersih, ['tense','slowly'], teks untuk ElevenLabs dengan tag resmi)."""
    kamus = muat()["tag"]
    nama: list[str] = []

    def ganti(m: re.Match) -> str:
        bagian = [p.strip().lower() for p in re.split(r"[,;]", m.group(1)) if p.strip()]
        salah = [p for p in bagian if p not in kamus]
        if salah:
            raise TagTidakDikenal(f"tag tidak dikenal: {', '.join(salah)}. Tag yang dikenal: {', '.join(sorted(kamus))}")
        nama.extend(bagian)
        return " ".join(kamus[p]["elevenlabs"] for p in bagian)

    el = re.sub(r"\[([^\]]*)\]", ganti, ucap)
    bersih = re.sub(r"\s+", " ", re.sub(r"\[[^\]]*\]", " ", ucap)).strip()
    return bersih, nama, re.sub(r"\s+", " ", el).strip()
