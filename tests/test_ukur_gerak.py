"""Alat ukur gerak video: membedakan video diam dari video yang terus bergerak."""
import subprocess

from scripts import ukur_gerak as ug


def _video(p, filter_):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", filter_, "-t", "6", "-pix_fmt", "yuv420p", str(p)], check=True)


def test_diam_lawan_bergerak(tmp_path):
    diam, gerak = tmp_path / "d.mp4", tmp_path / "g.mp4"
    _video(diam, "color=c=gray:s=180x320:r=30")
    _video(gerak, "testsrc2=s=180x320:r=30")
    a, b = ug.ukur(diam), ug.ukur(gerak)
    assert a["persen_diam"] == 100 and a["diam_terpanjang"] >= 5
    assert b["persen_diam"] < 20 and b["gerak_rata"] > a["gerak_rata"] + 1
    assert set(a) >= {"gerak_rata", "persen_diam", "diam_terpanjang", "beda_3dtk", "durasi"}
