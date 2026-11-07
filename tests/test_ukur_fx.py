import subprocess

from scripts import ukur_fx


def test_vinyet_dan_grain_terbaca(tmp_path):
    polos, vin = tmp_path / "polos.mp4", tmp_path / "vin.mp4"
    dasar = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=0x404040:s=720x1280:d=3:r=10"]
    subprocess.run(dasar + ["-pix_fmt", "yuv420p", str(polos)], check=True)
    subprocess.run(dasar + ["-vf", "vignette=PI/3,noise=alls=12:allf=t", "-pix_fmt", "yuv420p", str(vin)], check=True)
    a, b = ukur_fx.ukur(polos), ukur_fx.ukur(vin)
    assert a["sudut_per_tengah"] > 0.95 and b["sudut_per_tengah"] < 0.7
    assert b["grain"] > a["grain"] + 1
