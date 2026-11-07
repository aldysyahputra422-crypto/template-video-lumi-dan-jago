"""Render frame dengan render/mesin.html lalu gabungkan dengan campur.wav → video.mp4 (720x1280).

python -m scripts.render <folder> [fps]
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Grain film halus seperti video referensi (grain terukur 1,9 sampai 4,7; median 2,8). Diberikan saat encode agar deterministik per frame.
GRAIN = "noise=alls=6:allf=t"


def mode() -> dict:
    """config/gaya.yaml → render: {motion_blur: true}. Motion blur = render 2x fps lalu tiap 2 frame dicampur (gaya render Remotion)."""
    import yaml
    return (yaml.safe_load((ROOT / "config/gaya.yaml").read_text(encoding="utf-8")) or {}).get("render", {}) or {}


def saring(fps: int, blur: bool) -> tuple[int, str]:
    """(fps sumber frame, filter ffmpeg). Dengan blur: sumber 2x fps, tmix 2 frame, turunkan ke fps, lalu grain."""
    return (fps * 2, f"tmix=frames=2:weights='1 1',fps={fps},{GRAIN}") if blur else (fps, GRAIN)


def jalankan(folder: Path, fps: int = 30) -> Path:
    folder = Path(folder).resolve()
    sumber, vf = saring(fps, bool(mode().get("motion_blur")))
    frame = folder / "_frame"
    shutil.rmtree(frame, ignore_errors=True)
    r = subprocess.run(["node", str(ROOT / "render/render.js"), str(folder), str(frame), str(sumber)], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"render gagal: {r.stderr[-500:] or r.stdout[-500:]}")
    keluar = folder / "video.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(sumber), "-i", str(frame / "f%05d.jpg"), "-i", str(folder / "campur.wav"),
                    "-vf", vf, "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-maxrate", "3500k", "-bufsize", "7000k", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest",
                    "-movflags", "+faststart", str(keluar)], check=True)
    info = json.loads(r.stdout.strip().splitlines()[-1])
    shutil.rmtree(frame, ignore_errors=True)
    print(f"video.mp4: {info['frame']} frame dalam {info['detik']} dtk")
    return keluar


if __name__ == "__main__":
    jalankan(Path(sys.argv[1]), int(sys.argv[2]) if len(sys.argv) > 2 else 30)
