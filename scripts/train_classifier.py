"""Train the DistilBERT two-head classifier (type + severity) and write prediction CSVs.

Kaggle (GPU, Internet on):
    python scripts/train_classifier.py --data /kaggle/input/<dataset folder> --out /kaggle/working/classifier_run

Writes:
    <out>/model/                        encoder + tokenizer + heads.pt + label_map.json
    <out>/predictions/<split>_predictions.csv   id, pred_type, p_<TYPE> x8, pred_severity
    <out>/train_metrics.json            per-epoch losses and val scores (for monitoring only)

Final metrics are computed by the lead from the prediction CSVs.
"""
import argparse
import json
import math
import os
import random
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader, Dataset
from transformers import AutoTokenizer, get_linear_schedule_with_warmup

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from src.models.two_head import LABEL_MAP, LABELS, TwoHeadClassifier, sev_to_unit, two_head_loss, unit_to_sev  # noqa: E402

NON_EMERGENCY = "NON_EMERGENCY"


def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)


def load_csv(path, require_labels=True):
    df = pd.read_csv(path, dtype={"id": str}, keep_default_na=False)
    df["text"] = df["text"].astype(str)
    if "severity" in df.columns:
        df["severity"] = pd.to_numeric(df["severity"], errors="coerce")   # empty -> NaN
    else:
        df["severity"] = np.nan
    if require_labels or "incident_type" in df.columns:
        if "incident_type" in df.columns:
            bad = set(df["incident_type"]) - set(LABELS)
            if bad and require_labels:
                raise ValueError(f"{path}: labels not in LABEL_MAP: {sorted(bad)}")
            df["y"] = df["incident_type"].map(LABEL_MAP).fillna(-1).astype(int)
        elif require_labels:
            raise ValueError(f"{path}: no incident_type column")
    return df


class ReportDataset(Dataset):
    def __init__(self, df, tokenizer, max_len):
        self.enc = tokenizer(df["text"].tolist(), truncation=True, max_length=max_len)
        self.y = df["y"].tolist() if "y" in df.columns else [-1] * len(df)
        sev = df["severity"].to_numpy(dtype=float)
        self.sev = [float(sev_to_unit(s)) if not math.isnan(s) else float("nan") for s in sev]

    def __len__(self):
        return len(self.y)

    def __getitem__(self, i):
        return {"input_ids": self.enc["input_ids"][i], "attention_mask": self.enc["attention_mask"][i],
                "y": self.y[i], "sev": self.sev[i]}


def make_collate(pad_id):
    def collate(items):
        T = max(len(x["input_ids"]) for x in items)
        ids = torch.full((len(items), T), pad_id, dtype=torch.long)
        mask = torch.zeros((len(items), T), dtype=torch.long)
        for i, x in enumerate(items):
            n = len(x["input_ids"])
            ids[i, :n] = torch.tensor(x["input_ids"])
            mask[i, :n] = 1
        return {"input_ids": ids, "attention_mask": mask,
                "y": torch.tensor([x["y"] for x in items]), "sev": torch.tensor([x["sev"] for x in items], dtype=torch.float)}
    return collate


@torch.no_grad()
def predict(model, loader, device, use_amp):
    model.eval()
    probs, sevs = [], []
    for b in loader:
        with torch.autocast(device_type=device.type, dtype=torch.float16, enabled=use_amp):
            logits, sev_unit, _ = model(b["input_ids"].to(device), b["attention_mask"].to(device))
        probs.append(torch.softmax(logits.float(), -1).cpu())
        sevs.append(sev_unit.float().cpu())
    return torch.cat(probs).numpy(), torch.cat(sevs).numpy()


def macro_f1_present(y_true, y_pred):
    present = sorted(set(y_true))
    f1s = []
    for c in present:
        tp = int(((y_pred == c) & (y_true == c)).sum())
        fp = int(((y_pred == c) & (y_true != c)).sum())
        fn = int(((y_pred != c) & (y_true == c)).sum())
        p = tp / (tp + fp) if tp + fp else 0.0
        r = tp / (tp + fn) if tp + fn else 0.0
        f1s.append(2 * p * r / (p + r) if p + r else 0.0)
    return float(np.mean(f1s)) if f1s else 0.0


def write_predictions(df, probs, sev_unit, path):
    pred_idx = probs.argmax(1)
    pred_type = [LABELS[i] for i in pred_idx]
    sev = np.clip(sev_unit * 4.0 + 1.0, 1.0, 5.0)
    sev = np.where(np.array(pred_type) == NON_EMERGENCY, 1.0, sev)   # SCHEMA §1.2: NON_EMERGENCY is always 1.0
    out = pd.DataFrame({"id": df["id"], "pred_type": pred_type})
    for i, lab in enumerate(LABELS):
        out[f"p_{lab}"] = probs[:, i].round(6)
    out["pred_severity"] = sev.round(2)
    path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(path, index=False)
    print(f"wrote {path} ({len(out)} rows)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="/kaggle/input/resqpulse-data")
    ap.add_argument("--train_file", default="public_train.csv")
    ap.add_argument("--val_file", default="public_val.csv")
    ap.add_argument("--predict_files", nargs="*", default=["public_val.csv", "public_test.csv"],
                    help="CSV files (in --data) to write predictions for, e.g. public_val.csv public_test.csv test_synth.csv")
    ap.add_argument("--model_name", default="distilbert-base-uncased")
    ap.add_argument("--out", default="/kaggle/working/classifier_run")
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--lr", type=float, default=2e-5)
    ap.add_argument("--batch_size", type=int, default=32)
    ap.add_argument("--max_len", type=int, default=128)
    ap.add_argument("--warmup_ratio", type=float, default=0.06)
    ap.add_argument("--weight_decay", type=float, default=0.01)
    ap.add_argument("--sev_weight", type=float, default=1.0)
    ap.add_argument("--select", choices=["last", "best_val"], default="last",
                    help="which epoch to keep; default last because v0 val shares events with train")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--no_fp16", action="store_true")
    args = ap.parse_args()

    set_seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    use_amp = device.type == "cuda" and not args.no_fp16
    out = Path(args.out)
    data = Path(args.data)
    print(f"device={device} fp16={use_amp} model={args.model_name}")

    train_df = load_csv(data / args.train_file)
    val_df = load_csv(data / args.val_file)
    n_sev = int(train_df["severity"].notna().sum())
    print(f"train {len(train_df)} rows ({n_sev} with severity) | val {len(val_df)} rows")
    if n_sev == 0:
        print("NOTE: no training row has severity -> severity head receives no gradient (expected on v0)")

    tok = AutoTokenizer.from_pretrained(args.model_name)
    collate = make_collate(tok.pad_token_id)
    g = torch.Generator().manual_seed(args.seed)
    train_loader = DataLoader(ReportDataset(train_df, tok, args.max_len), batch_size=args.batch_size,
                              shuffle=True, collate_fn=collate, generator=g, num_workers=2)
    val_loader = DataLoader(ReportDataset(val_df, tok, args.max_len), batch_size=128, collate_fn=collate)

    model = TwoHeadClassifier.from_encoder(args.model_name).to(device)
    no_decay = ("bias", "LayerNorm.weight", "layer_norm.weight")
    params = [{"params": [p for n, p in model.named_parameters() if not any(k in n for k in no_decay)], "weight_decay": args.weight_decay},
              {"params": [p for n, p in model.named_parameters() if any(k in n for k in no_decay)], "weight_decay": 0.0}]
    opt = torch.optim.AdamW(params, lr=args.lr)
    total = args.epochs * len(train_loader)
    sched = get_linear_schedule_with_warmup(opt, int(args.warmup_ratio * total), total)
    scaler = torch.amp.GradScaler("cuda", enabled=use_amp)

    history, best = [], -1.0
    model_dir = out / "model"
    for ep in range(1, args.epochs + 1):
        model.train()
        t0 = time.time()
        sums = {"loss": 0.0, "ce": 0.0, "mse": 0.0, "n_sev": 0}
        for step, b in enumerate(train_loader, 1):
            ids, mask = b["input_ids"].to(device), b["attention_mask"].to(device)
            with torch.autocast(device_type=device.type, dtype=torch.float16, enabled=use_amp):
                logits, sev_unit, _ = model(ids, mask)
            loss, ce, mse, n = two_head_loss(logits.float(), sev_unit.float(), b["y"].to(device), b["sev"].to(device), args.sev_weight)
            opt.zero_grad(set_to_none=True)
            scaler.scale(loss).backward()
            scaler.unscale_(opt)
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            scaler.step(opt)
            scaler.update()
            sched.step()
            sums["loss"] += loss.item(); sums["ce"] += ce.item(); sums["mse"] += mse.item(); sums["n_sev"] += n
            if step % 100 == 0:
                print(f"  epoch {ep} step {step}/{len(train_loader)} loss {sums['loss'] / step:.4f}", flush=True)
        steps = len(train_loader)

        probs, sev_unit = predict(model, val_loader, device, use_amp)
        y = val_df["y"].to_numpy()
        f1 = macro_f1_present(y, probs.argmax(1))
        acc = float((probs.argmax(1) == y).mean())
        vs = val_df["severity"].to_numpy()
        has = ~np.isnan(vs)
        val_sev_mae = float(np.abs((sev_unit[has] * 4 + 1) - vs[has]).mean()) if has.any() else None
        rec = {"epoch": ep, "train_loss": sums["loss"] / steps, "train_ce": sums["ce"] / steps,
               "train_sev_mse_unit": sums["mse"] / steps, "train_rows_with_severity": sums["n_sev"],
               "val_acc": acc, "val_macro_f1_present": f1, "val_sev_mae": val_sev_mae, "seconds": round(time.time() - t0)}
        history.append(rec)
        print(f"epoch {ep}: loss {rec['train_loss']:.4f} (ce {rec['train_ce']:.4f}, sev mse {rec['train_sev_mse_unit']:.4f}) | "
              f"val acc {acc:.4f} macro-F1 {f1:.4f} sev MAE {val_sev_mae} | {rec['seconds']}s", flush=True)

        if args.select == "last" or f1 > best:
            best = f1
            model.save(model_dir, tok)
            print(f"  saved model -> {model_dir}")

    (out / "train_metrics.json").write_text(json.dumps({"args": vars(args), "history": history}, indent=2))

    # ---------------- predictions with the saved model
    model = TwoHeadClassifier.load(model_dir, device=device, attn_implementation="sdpa")
    for fname in args.predict_files:
        path = data / fname
        if not path.exists():
            print(f"skip {fname}: not found in {data}")
            continue
        df = load_csv(path, require_labels=False)
        loader = DataLoader(ReportDataset(df, tok, args.max_len), batch_size=128, collate_fn=collate)
        probs, sev_unit = predict(model, loader, device, use_amp)
        write_predictions(df, probs, sev_unit, out / "predictions" / f"{Path(fname).stem}_predictions.csv")
    print("done")


if __name__ == "__main__":
    main()
