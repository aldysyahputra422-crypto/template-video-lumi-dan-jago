import subprocess

from scripts import ukur_palet as up


def test_palet_dominan_terukur(tmp_path):
    v = tmp_path / "v.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=0x101010:s=180x320:d=3,drawbox=x=0:y=0:w=180:h=80:color=0xE8A847:t=fill",
                    "-pix_fmt", "yuv420p", str(v)], check=True)
    p = up.ukur(v, n=4)
    warna = [x["hex"] for x in p]
    assert any(up.jarak(w, "#101010") < 30 for w in warna) and any(up.jarak(w, "#E8A847") < 40 for w in warna)
    assert abs(sum(x["porsi"] for x in p) - 1) < 0.05 and p[0]["porsi"] > 0.6
