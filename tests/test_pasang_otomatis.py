"""Pemasang skill dari katalog: hanya yang terkunci ke commit, gratis, tanpa API key."""
import subprocess
from pathlib import Path

import pytest

from scripts import pasang_otomatis as po

ROOT = Path(__file__).resolve().parents[1]
KAT = po.muat(ROOT / "katalog/skill.yaml")
PIN = "a" * 40


def test_katalog_hanya_yang_dibutuhkan_dan_aman():
    ids = {e.id for e in KAT}
    assert {"claude-screenwriting", "humanizer", "motion-design-skill"} <= ids
    for e in KAT:
        assert po.SHA.fullmatch(e.pasang["pin"]), e.id
        assert e.biaya == "gratis" and not e.butuh_key, e.id
        assert e.alasan_dipakai, e.id          # setiap entri harus menjelaskan kenapa repo ini butuh
        assert po.alasan_tidak_boleh(e) is None, e.id


def _e(**kw):
    d = dict(id="x", sumber="s", fungsi="f", alasan_dipakai="a", lisensi="MIT", biaya="gratis", butuh_key=None, ukuran="kecil",
             otomatis=True, wajib=True, pasang={"jenis": "git_skill", "url": "https://github.com/a/b", "pin": PIN})
    d.update(kw)
    return po.Entri(**d)


@pytest.mark.parametrize("ubah,cari", [
    ({"butuh_key": "GEMINI_API_KEY"}, "berbayar"),
    ({"biaya": "berbayar per video"}, "berbayar"),
    ({"pasang": {"jenis": "git_skill", "url": "u", "pin": "main"}}, "dikunci"),
    ({"pasang": {"jenis": "npx_skill", "repo": "a/b"}}, "jenis"),
])
def test_ditolak(ubah, cari):
    assert cari in po.alasan_tidak_boleh(_e(**ubah))


def test_lisensi_nonkomersial_ditolak_hanya_di_mode_komersial(monkeypatch):
    e = _e(lisensi="PolyForm-Noncommercial-1.0.0")
    monkeypatch.setattr(po, "mode", lambda: "eksplorasi")
    assert po.alasan_tidak_boleh(e) is None
    monkeypatch.setattr(po, "mode", lambda: "komersial")
    assert "lisensi" in po.alasan_tidak_boleh(e)


def _runner_palsu(pin_kembali=PIN):
    """Meniru git: clone membuat folder (dan SKILL.md), rev-parse mengembalikan pin_kembali."""
    def run(cmd, **kw):
        if cmd[:2] == ["git", "clone"]:
            tujuan = Path(cmd[-1])
            for d in ("", "skills/satu", "skills/dua"):
                (tujuan / d).mkdir(parents=True, exist_ok=True)
                (tujuan / d / "SKILL.md").write_text("x")
        out = pin_kembali if "rev-parse" in cmd else ""
        return subprocess.CompletedProcess(cmd, 0, stdout=out, stderr="")
    return run


def test_git_skill_terpasang_dan_dicatat(tmp_path):
    h = po.pasang_satu(_e(), skills_dir=tmp_path / "s", runner=_runner_palsu(), log=tmp_path / "log.md", cache=tmp_path / "c", rujukan=tmp_path / "r")
    assert h["status"] == "terpasang" and (tmp_path / "s/x/SKILL.md").exists()
    assert "| x | terpasang |" in (tmp_path / "log.md").read_text()
    assert po.pasang_satu(_e(), skills_dir=tmp_path / "s", runner=_runner_palsu(), log=tmp_path / "log.md")["status"] == "sudah_ada"


def test_subskill_hanya_folder_terpilih(tmp_path):
    e = _e(pasang={"jenis": "git_subskill", "url": "u", "pin": PIN, "paths": ["skills/satu"], "skills": ["satu"]})
    assert po.pasang_satu(e, skills_dir=tmp_path / "s", runner=_runner_palsu(), log=tmp_path / "l", cache=tmp_path / "c")["status"] == "terpasang"
    assert (tmp_path / "s/satu/SKILL.md").exists() and not (tmp_path / "s/dua").exists()


def test_commit_berbeda_dari_pin_gagal(tmp_path):
    h = po.pasang_satu(_e(), skills_dir=tmp_path / "s", runner=_runner_palsu("b" * 40), log=tmp_path / "l")
    assert h["status"] == "gagal"


def test_rujukan_ke_folder_rujukan(tmp_path):
    e = _e(pasang={"jenis": "rujukan", "url": "u", "pin": PIN})
    assert po.pasang_satu(e, runner=_runner_palsu(), log=tmp_path / "l", rujukan=tmp_path / "r")["status"] == "terpasang"
    assert (tmp_path / "r/x").is_dir()
