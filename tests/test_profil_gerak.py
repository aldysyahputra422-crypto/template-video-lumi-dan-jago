import json
import subprocess

from scripts import profil_gerak


def test_profil_membedakan_ketukan_bergerak_dan_diam(tmp_path):
    # 4 dtk diam, 4 dtk gambar bergerak (noise berubah tiap frame)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=gray:s=180x320:d=4:r=10", "-f", "lavfi", "-i", "testsrc2=s=180x320:d=4:r=10",
                    "-filter_complex", "[0][1]concat=n=2:v=1:a=0", "-pix_fmt", "yuv420p", str(tmp_path / "video.mp4")], check=True)
    (tmp_path / "timeline.json").write_text(json.dumps({"ketukan": [{"no": 1, "mulai": 0, "selesai": 3.5}, {"no": 2, "mulai": 4.5, "selesai": 7.5, "sisipan": {"nama": "x"}}]}), encoding="utf-8")
    p = profil_gerak.profil(tmp_path)
    assert p[0]["skor"] < 1 and p[1]["skor"] > 3 and p[1]["sisipan"] is True
