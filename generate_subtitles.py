import json
import os
import subprocess
from pathlib import Path
import pandas as pd

BASE_DIR = Path(r"C:\cstuff\AI\Lab3 SR")
DATASET_DIR = BASE_DIR / "dataset"
SUBTITLES_DIR = BASE_DIR / "subtitles"
WHISPER_DIR = Path(r"C:\whisper\whisper.cpp")
WHISPER_EXE = WHISPER_DIR / "build" / "bin" / "Release" / "whisper-cli.exe"
MODEL_PATH = WHISPER_DIR / "models" / "ggml-large-v3-turbo.bin"

SUBTITLES_DIR.mkdir(exist_ok=True)

env = os.environ.copy()
env["PATH"] = r"C:\whisper\flexmlrt\lib;" + env.get("PATH", "")

wav_files = sorted(DATASET_DIR.glob("F*.wav"), key=lambda p: int(p.stem[1:]))[:42]  

rows = []
for wav in wav_files:
    title = wav.stem
    srt_path = SUBTITLES_DIR / f"{title}.srt"

    if not srt_path.exists():
        subprocess.run(
            [
                str(WHISPER_EXE),
                "-m", str(MODEL_PATH),
                "-f", str(wav),
                "-l", "ru",
                "-t", "10",
                "-osrt",
                "-of", str(SUBTITLES_DIR / title),
            ],
            cwd=str(WHISPER_DIR),
            env=env,
            check=True,
        )

    rows.append({
        "title": title,
        "link": f"subtitles/{title}.srt",
        "srt": srt_path.read_text(encoding="utf-8"),
    })

df = pd.DataFrame(rows)
df.to_excel(BASE_DIR / "subtitles.xlsx", index=False)
df.assign(srt=df["srt"].str.replace("\r\n", "\n", regex=False).str.replace("\n", r"\n", regex=False)).to_csv(
    BASE_DIR / "subtitles.csv", index=False, encoding="utf-8-sig"
)
(BASE_DIR / "subtitles.json").write_text(
    json.dumps(rows, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
