"""Pasang skill dan rujukan dari katalog/skill.yaml, dengan aturan ketat. Disalin dan dirampingkan dari repo Sobat Ambis.

python -m scripts.pasang_otomatis            → pasang entri otomatis: true (dipakai hook SessionStart)
python -m scripts.pasang_otomatis --wajib    → ambil semua entri wajib: true
python -m scripts.pasang_otomatis --id <id>  → ambil satu entri

Selalu ditolak: yang butuh API key atau tidak gratis, yang tidak terkunci ke commit (pin SHA 40 huruf), jenis selain
git_skill / git_subskill / rujukan. Clone mengambil persis commit pin lalu memverifikasi HEAD == pin.
Mode config/kebijakan.yaml: eksplorasi (lisensi tidak membatasi) atau komersial (hanya lisensi bebas komersial).
Skill → ~/.claude/skills, rujukan → rujukan/<id> (diabaikan git). Log → katalog/terpasang.md (diabaikan git).
"""
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, fields
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILLS = Path.home() / ".claude/skills"
RUJUKAN = ROOT / "rujukan"
LOG = ROOT / "katalog/terpasang.md"
CACHE = Path.home() / ".cache/ata-skill"
SHA = re.compile(r"[0-9a-f]{40}")
LISENSI_BEBAS = ("mit", "apache-2.0", "bsd", "isc", "lgpl")
JENIS = ("git_skill", "git_subskill", "rujukan")


@dataclass
class Entri:
    id: str
    sumber: str
    fungsi: str
    alasan_dipakai: str
    lisensi: str
    biaya: str
    butuh_key: str | None
    ukuran: str
    pasang: dict
    otomatis: bool = False
    wajib: bool = False
    catatan: str = ""


def muat(path: Path) -> list[Entri]:
    nama = {f.name for f in fields(Entri)}
    return [Entri(**{k: v for k, v in d.items() if k in nama}) for d in yaml.safe_load(Path(path).read_text(encoding="utf-8")) or []]


def mode() -> str:
    try:
        return yaml.safe_load((ROOT / "config/kebijakan.yaml").read_text(encoding="utf-8")).get("mode", "komersial")
    except OSError:
        return "komersial"


def alasan_tidak_boleh(e: Entri) -> str | None:
    if e.butuh_key:
        return f"berbayar: butuh {e.butuh_key}"
    if (e.biaya or "").lower() != "gratis":
        return f"berbayar: {e.biaya}"
    if mode() == "komersial" and not (e.lisensi or "").lower().startswith(LISENSI_BEBAS):
        return f"lisensi {e.lisensi} tidak untuk komersial (mode komersial)"
    if (e.pasang or {}).get("jenis") not in JENIS:
        return f"jenis pasang tidak diizinkan: {(e.pasang or {}).get('jenis')} (hanya {', '.join(JENIS)})"
    if not SHA.fullmatch(str(e.pasang.get("pin", ""))):
        return "belum dikunci ke commit (pin SHA 40 huruf)"
    return None


def _nama_skill(e: Entri) -> list[str]:
    return e.pasang.get("skills") or [e.id]


def sudah_terpasang(e: Entri, skills_dir: Path, rujukan: Path) -> bool:
    if e.pasang["jenis"] == "rujukan":
        return (rujukan / e.id).is_dir() and any((rujukan / e.id).iterdir())
    return all((skills_dir / n / "SKILL.md").exists() for n in _nama_skill(e))


def _klon(run, url: str, tujuan: Path, pin: str, induk: list[str] | None = None) -> bool:
    cmd = ["git", "clone", "--depth", "1", "--no-checkout"] + (["--filter=blob:none", "--sparse"] if induk else []) + [url, str(tujuan)]
    if run(cmd, capture_output=True, text=True, timeout=300).returncode != 0:
        return False
    langkah = ([["sparse-checkout", "set", *induk]] if induk else []) + [["fetch", "--depth", "1", "origin", pin], ["checkout", "-q", "--detach", "FETCH_HEAD"]]
    for x in langkah:
        if run(["git", "-C", str(tujuan), *x], capture_output=True, text=True, timeout=300).returncode != 0:
            return False
    r = run(["git", "-C", str(tujuan), "rev-parse", "HEAD"], capture_output=True, text=True, timeout=60)
    return r.returncode == 0 and r.stdout.strip() == pin


def _catat(log: Path, e: Entri, hasil: str) -> None:
    log.parent.mkdir(parents=True, exist_ok=True)
    if not log.exists():
        log.write_text("# Skill terpasang\n\n| Waktu (UTC) | id | hasil |\n|---|---|---|\n", encoding="utf-8")
    with log.open("a", encoding="utf-8") as f:
        f.write(f"| {datetime.now(timezone.utc).isoformat(timespec='minutes')} | {e.id} | {hasil} |\n")


def pasang_satu(e: Entri, skills_dir: Path | None = None, runner=subprocess.run, log: Path | None = None,
                cache: Path | None = None, rujukan: Path | None = None) -> dict:
    skills_dir, log, cache, rujukan = Path(skills_dir or SKILLS), Path(log or LOG), Path(cache or CACHE), Path(rujukan or RUJUKAN)
    alasan = alasan_tidak_boleh(e)
    if alasan:
        return {"id": e.id, "status": "ditolak", "alasan": alasan}
    if sudah_terpasang(e, skills_dir, rujukan):
        return {"id": e.id, "status": "sudah_ada"}
    p, ok = e.pasang, False
    try:
        if p["jenis"] == "git_subskill":
            tujuan = cache / e.id
            shutil.rmtree(tujuan, ignore_errors=True)
            tujuan.parent.mkdir(parents=True, exist_ok=True)
            if _klon(runner, p["url"], tujuan, p["pin"], p["paths"]):
                skills_dir.mkdir(parents=True, exist_ok=True)
                for path in p["paths"]:
                    if (tujuan / path / "SKILL.md").exists():
                        shutil.copytree(tujuan / path, skills_dir / Path(path).name, dirs_exist_ok=True)
                ok = sudah_terpasang(e, skills_dir, rujukan)
        else:
            dasar = rujukan if p["jenis"] == "rujukan" else skills_dir
            dasar.mkdir(parents=True, exist_ok=True)
            ok = _klon(runner, p["url"], dasar / e.id, p["pin"]) and sudah_terpasang(e, skills_dir, rujukan)
            if not ok:
                shutil.rmtree(dasar / e.id, ignore_errors=True)
    except (OSError, subprocess.TimeoutExpired):
        ok = False
    _catat(log, e, "terpasang" if ok else "gagal")
    return {"id": e.id, "status": "terpasang" if ok else "gagal"}


def main(argv: list[str]) -> int:
    kat = muat(ROOT / "katalog/skill.yaml")
    if "--id" in argv:
        i = argv[argv.index("--id") + 1]
        pilih = [e for e in kat if e.id == i]
        if not pilih:
            print(json.dumps({"id": i, "status": "ditolak", "alasan": "tidak ada di katalog"}, ensure_ascii=False))
            return 1
    else:
        pilih = [e for e in kat if (e.wajib if "--wajib" in argv else e.otomatis)]
    hasil: dict[str, list[str]] = {}
    for e in pilih:
        h = pasang_satu(e)
        hasil.setdefault(h["status"], []).append(e.id + (f" ({h['alasan']})" if "alasan" in h else ""))
    print(json.dumps(hasil, ensure_ascii=False))
    return 1 if "gagal" in hasil or "ditolak" in hasil else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
