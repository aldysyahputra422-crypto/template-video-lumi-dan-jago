"""Kemas dua skill portabel untuk diimpor ke Claude: naskah-reels (MD saja) dan olah-reels (MD + mesin produksi).

python -m scripts.kemas_skill [folder_keluar]   (bawaan: dist/)  → naskah-reels.zip, olah-reels.zip
- naskah-reels: skills/naskah-reels/SKILL.template.md + kosakata terbaru + contoh naskah.
- olah-reels: skills/olah-reels/SKILL.md + salinan mesin (scripts, render tanpa node_modules, config, schemas, katalog, aset audio,
  docs gaya) dengan profil naskah filosofi dan nama akun pengganti. Tanpa video, transkrip pihak ketiga, atau maskot.
"""
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SALIN = ["scripts", "render", "config", "schemas", "katalog/sfx.yaml", "aset/audio", "requirements.txt",
         "docs/gaya-visual.md", "docs/pola-mindwander.md", "tests/fixtures/aset_uji"]
ABAIKAN = shutil.ignore_patterns("node_modules", "__pycache__", "*.pyc", "sintetis", "unduhan", "_frame*")


def _kosakata() -> str:
    k = yaml.safe_load((ROOT / "config/kosakata.yaml").read_text(encoding="utf-8"))
    tag = yaml.safe_load((ROOT / "config/tag_ekspresi.yaml").read_text(encoding="utf-8"))["tag"]
    daftar = lambda d: ", ".join(d) if isinstance(d, list) else ", ".join(f"{n} ({v})" if isinstance(v, str) else n for n, v in d.items())
    teruji = [n for n, v in tag.items() if v.get("terverifikasi") == "pemilik"]
    return "\n".join([
        "## Kosakata bawaan (nama lain dideklarasikan di ##ASET)",
        f"- LATAR: {daftar(k['latar'])}",
        f"- PERAN: {daftar(k['peran'])}",
        f"- EKSPRESI: {', '.join(k['ekspresi'])}",
        f"- AKSI: {daftar(k['aksi'])}",
        f"- POSISI: {', '.join(k['posisi'])}",
        f"- PROPS: {daftar(k['props'])}",
        f"- GERAK PROPS: {', '.join(k['gerak_props'])}",
        f"- SISIPAN: {', '.join(f'{n} ({v['arti']})' for n, v in k['sisipan'].items())}",
        f"- SUASANA: {', '.join(k['suasana'])}",
        f"- TAG SUARA teruji: {', '.join(f'[{t}]' for t in teruji)}; lainnya: {', '.join(f'[{t}]' for t in tag if t not in teruji)}",
    ])


def _zip(folder: Path, keluar: Path) -> Path:
    with zipfile.ZipFile(keluar, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(folder.rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(folder.parent))
    return keluar


def kemas(keluar: Path) -> dict:
    keluar = Path(keluar)
    keluar.mkdir(parents=True, exist_ok=True)
    hasil = {}
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        n = tmp / "naskah-reels"
        n.mkdir()
        md = (ROOT / "skills/naskah-reels/SKILL.template.md").read_text(encoding="utf-8")
        md = md.replace("{{KOSAKATA}}", _kosakata()).replace("{{CONTOH}}", (ROOT / "skills/naskah-reels/contoh-sunk-cost.txt").read_text(encoding="utf-8").strip())
        (n / "SKILL.md").write_text(md, encoding="utf-8")
        shutil.copy(ROOT / "skills/naskah-reels/benchmark.md", n / "benchmark.md")
        hasil["naskah-reels"] = _zip(n, keluar / "naskah-reels.zip")

        o = tmp / "olah-reels"
        m = o / "mesin"
        m.mkdir(parents=True)
        shutil.copy(ROOT / "skills/olah-reels/SKILL.md", o / "SKILL.md")
        for s in SALIN:
            src, dst = ROOT / s, m / s
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(src, dst, ignore=ABAIKAN) if src.is_dir() else shutil.copy(src, dst)
        g = yaml.safe_load((m / "config/gaya.yaml").read_text(encoding="utf-8"))
        g["naskah"]["profil"] = "filosofi"
        g["naskah"]["profil_isi"] = {"filosofi": g["naskah"]["profil_isi"]["filosofi"]}
        (m / "config/gaya.yaml").write_text(yaml.safe_dump(g, allow_unicode=True, sort_keys=False), encoding="utf-8")
        akun = yaml.safe_load((m / "config/tokoh.yaml").read_text(encoding="utf-8"))["akun"]
        akun["nama_akun"] = "@akunmu"
        (m / "config/tokoh.yaml").write_text("# Hanya identitas akun: watermark dan tagar caption. Ganti nama_akun dengan akunmu.\n"
                                             + yaml.safe_dump({"akun": akun}, allow_unicode=True, sort_keys=False), encoding="utf-8")
        tag = m / "config/tag_ekspresi.yaml"
        tag.write_text(tag.read_text(encoding="utf-8").replace("suara Ata", "suara narator"), encoding="utf-8")
        (m / "video").mkdir()
        hasil["olah-reels"] = _zip(o, keluar / "olah-reels.zip")
    return hasil


if __name__ == "__main__":
    for nama, p in kemas(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "dist").items():
        print(f"{nama}: {p} ({p.stat().st_size // 1024} KB)")
