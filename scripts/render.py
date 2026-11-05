"""Render frame dengan render/mesin.html lalu gabungkan dengan campur.wav → video.mp4 (720x1280).

python -m scripts.render <folder> [fps]
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def jalankan(folder: Path, fps: int = 30) -> Path:
    folder = Path(folder).resolve()
    frame = folder / "_frame"
    shutil.rmtree(frame, ignore_errors=True)
    r = subprocess.run(["node", str(ROOT / "render/render.js"), str(folder), str(frame), str(fps)], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"render gagal: {r.stderr[-500:] or r.stdout[-500:]}")
    keluar = folder / "video.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(fps), "-i", str(frame / "f%05d.jpg"), "-i", str(folder / "campur.wav"),
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest",
                    "-movflags", "+faststart", str(keluar)], check=True)
    info = json.loads(r.stdout.strip().splitlines()[-1])
    shutil.rmtree(frame, ignore_errors=True)
    print(f"video.mp4: {info['frame']} frame dalam {info['detik']} dtk")
    return keluar


if __name__ == "__main__":
    jalankan(Path(sys.argv[1]), int(sys.argv[2]) if len(sys.argv) > 2 else 30)
