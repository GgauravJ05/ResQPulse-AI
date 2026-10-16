"""Word error rate of the demo's Whisper path on synthetic speech (text-to-speech voices), clean and phone-noisy.

Why synthetic: we have no recorded human test set. The reports are the held-out call-style test reports (never used for
training), spoken by macOS `say` voices, then also degraded (300-3400 Hz phone band + pink noise). This is NOT human speech,
so treat the numbers as a lower bound on difficulty and say so. Needs the backend running on :8000 and ffmpeg.

Run from the repo root:  .venv/bin/python scripts/eval_whisper.py --n 20
"""
import argparse
import json
import re
import subprocess
import tempfile
from pathlib import Path

import pandas as pd
import requests

VOICES = ["Daniel", "Aman (English (India))", "Samantha", "Eddy (English (UK))"]


def words(t: str) -> list:
    return re.findall(r"[a-z0-9']+", t.lower().replace("-", " "))


def wer(ref: list, hyp: list) -> tuple:
    d = list(range(len(hyp) + 1))
    for i, r in enumerate(ref, 1):
        prev, d[0] = d[0], i
        for j, h in enumerate(hyp, 1):
            prev, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, prev + (r != h))
    return d[-1], len(ref)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument("--api", default="http://localhost:8000")
    ap.add_argument("--out", default="reports/whisper_wer.json")
    a = ap.parse_args()
    df = pd.read_csv("data/processed/test_synth.csv").sample(a.n, random_state=7)
    tmp = Path(tempfile.mkdtemp())
    tot = {"clean": [0, 0], "noisy": [0, 0]}
    rows = []
    for k, (rid, text) in enumerate(zip(df["id"], df["text"])):
        voice = VOICES[k % len(VOICES)]
        aiff, clean, noisy = tmp / f"{k}.aiff", tmp / f"{k}_clean.wav", tmp / f"{k}_noisy.wav"
        subprocess.run(["say", "-v", voice, "-o", str(aiff), text], check=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(aiff), "-ar", "16000", "-ac", "1", str(clean)], check=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(clean), "-f", "lavfi", "-i",
                        "anoisesrc=color=pink:amplitude=0.08:sample_rate=16000", "-filter_complex",
                        "[0:a]highpass=f=300,lowpass=f=3400[v];[v][1:a]amix=inputs=2:duration=first:weights=1 0.9",
                        "-ac", "1", str(noisy)], check=True)
        row = {"id": rid, "voice": voice, "reference": text}
        for kind, path in (("clean", clean), ("noisy", noisy)):
            hyp = requests.post(f"{a.api}/transcribe", files={"file": (path.name, path.read_bytes())}, timeout=120).json()["transcript"]
            e, n = wer(words(text), words(hyp))
            tot[kind][0] += e
            tot[kind][1] += n
            row[f"{kind}_hyp"], row[f"{kind}_wer"] = hyp, round(e / max(n, 1), 3)
        rows.append(row)
        print(k + 1, voice, row["clean_wer"], row["noisy_wer"], flush=True)
    res = {"n_clips": len(rows), "wer_clean": round(tot["clean"][0] / tot["clean"][1], 4),
           "wer_noisy": round(tot["noisy"][0] / tot["noisy"][1], 4), "voices": VOICES,
           "note": "text-to-speech audio, not human speech", "clips": rows}
    Path(a.out).parent.mkdir(exist_ok=True)
    Path(a.out).write_text(json.dumps(res, indent=2))
    print(f"WER clean {res['wer_clean']:.3f}  noisy {res['wer_noisy']:.3f}  ({len(rows)} clips)")


if __name__ == "__main__":
    main()
