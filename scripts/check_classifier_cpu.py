"""Laptop CPU check for src/models/classifier.py.

Runs classify() on the first N rows of test_synth.csv and compares with the predictions CSV made on Kaggle
(GPU, fp16). Checks: same pred_type, probabilities and severity within a small tolerance, and the time per call.

    python scripts/check_classifier_cpu.py --model models/classifier \
        --data data/test_synth.csv --preds test_synth_predictions.csv --n 10
"""
import argparse
import os
import sys
import time
from pathlib import Path

os.environ["CUDA_VISIBLE_DEVICES"] = ""          # force CPU, like the laptop/API server

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="models/classifier")
    ap.add_argument("--data", default="test_synth.csv", help="test_synth.csv (id, text, ...)")
    ap.add_argument("--preds", default="test_synth_predictions.csv", help="predictions CSV from Kaggle")
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--prob_tol", type=float, default=0.02, help="GPU fp16 vs CPU fp32 differences")
    ap.add_argument("--sev_tol", type=float, default=0.05)
    ap.add_argument("--max_seconds", type=float, default=3.0)
    args = ap.parse_args()
    os.environ["CLASSIFIER_DIR"] = str(Path(args.model).resolve())

    import pandas as pd
    t0 = time.perf_counter()
    from src.models import classifier
    load_s = time.perf_counter() - t0
    print(f"model load (import): {load_s:.1f}s  ready={classifier.is_ready()}  device={classifier._device}")
    if not classifier.is_ready():
        sys.exit(f"model not loaded: {classifier._load_error}")

    data = pd.read_csv(args.data, dtype={"id": str}, keep_default_na=False).head(args.n)
    preds = pd.read_csv(args.preds, dtype={"id": str}).set_index("id")
    labels = classifier.LABELS

    classifier.classify("warm up call")                # first call includes one-off setup
    times, failures = [], 0
    for _, row in data.iterrows():
        t = time.perf_counter()
        r = classifier.classify(row["text"])
        times.append(time.perf_counter() - t)
        ref = preds.loc[row["id"]]
        max_dp = max(abs(r.probs[l] - float(ref[f"p_{l}"])) for l in labels)
        dsev = abs(r.severity - float(ref["pred_severity"]))
        ok = r.incident_type == ref["pred_type"] and max_dp <= args.prob_tol and dsev <= args.sev_tol
        failures += not ok
        print(f"{'OK ' if ok else 'BAD'} {row['id']:<22} {r.incident_type:<20} (kaggle {ref['pred_type']:<20}) "
              f"max|dp|={max_dp:.4f} sev {r.severity:.2f} vs {float(ref['pred_severity']):.2f}  {times[-1] * 1000:.0f} ms")

    slowest = max(times)
    print(f"\n{args.n - failures}/{args.n} match Kaggle predictions | per call: mean {sum(times) / len(times) * 1000:.0f} ms, "
          f"max {slowest * 1000:.0f} ms (limit {args.max_seconds:.1f} s)")
    if failures or slowest > args.max_seconds:
        sys.exit("CHECK FAILED")
    print("CHECK PASSED")


if __name__ == "__main__":
    main()
