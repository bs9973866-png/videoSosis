#!/usr/bin/env python3
"""Render the vertical story video. Requires ffmpeg in PATH."""
from pathlib import Path
import subprocess, sys

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
OUT = ROOT / "output.mp4"
VOICE = ASSETS / "voice.mp3"
CAPTIONS = ASSETS / "captions.ass"
SCENES = ASSETS / "scenes"
DURATION = 87.484
SCENE_COUNT = 6
FPS = 30

def run(args):
    subprocess.run(args, check=True)

def main():
    required = [VOICE, CAPTIONS, *(SCENES / f"scene{i}.jpg" for i in range(1, SCENE_COUNT + 1))]
    for path in required:
        if not path.exists():
            sys.exit(f"Missing asset: {path}")
    work = ROOT / ".render"
    work.mkdir(exist_ok=True)
    seg_duration = DURATION / SCENE_COUNT
    segments = []
    for i in range(1, SCENE_COUNT + 1):
        segment = work / f"segment{i}.mp4"
        frames = round(seg_duration * FPS)
        run([
            "ffmpeg", "-y", "-loop", "1", "-i", str(SCENES / f"scene{i}.jpg"),
            "-t", str(seg_duration),
            "-vf", f"zoompan=z='min(zoom+0.00018,1.055)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1080x1920:fps={FPS},format=yuv420p",
            "-r", str(FPS), "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "24", str(segment)
        ])
        segments.append(segment)
    concat = work / "concat.txt"
    concat.write_text("".join(f"file '{p.as_posix()}'\\n" for p in segments), encoding="utf-8")
    silent = work / "silent.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat), "-c", "copy", str(silent)])
    run([
        "ffmpeg", "-y", "-i", str(silent), "-i", str(VOICE),
        "-vf", f"ass='{CAPTIONS.as_posix()}'",
        "-map", "0:v:0", "-map", "1:a:0", "-c:v", "libx264",
        "-preset", "veryfast", "-crf", "23", "-c:a", "aac", "-b:a", "160k",
        "-shortest", "-movflags", "+faststart", str(OUT)
    ])
    print(f"Created: {OUT}")

if __name__ == "__main__":
    main()
