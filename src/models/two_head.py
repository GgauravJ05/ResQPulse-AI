"""DistilBERT encoder with two heads (SCHEMA §1.1, §1.2):
  * type head     : 8-way softmax (cross-entropy)
  * severity head : one value in 0-1 via sigmoid (MSE, masked for rows without severity)

Saved folder layout (models/classifier/):
  config.json + model.safetensors   <- encoder, Hugging Face save_pretrained format
  tokenizer files                    <- tokenizer.save_pretrained
  heads.pt                           <- type + severity head weights
  label_map.json                     <- SCHEMA §9, fixed order
"""
import json
from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import AutoModel

LABEL_MAP = {"FIRE": 0, "FLOOD": 1, "STORM_CYCLONE": 2, "EARTHQUAKE_COLLAPSE": 3,
             "TRANSPORT_ACCIDENT": 4, "MEDICAL": 5, "VIOLENCE_CRIME": 6, "NON_EMERGENCY": 7}
try:  # prefer the repo's single source of truth
    from src.data.labels import LABEL_MAP  # noqa: F811
except ImportError:
    pass
LABELS = sorted(LABEL_MAP, key=LABEL_MAP.get)


def sev_to_unit(s):
    """1-5 -> 0-1 (training scale)."""
    return (s - 1.0) / 4.0


def unit_to_sev(u):
    """0-1 -> 1-5 (output scale), clipped."""
    return (u * 4.0 + 1.0).clamp(1.0, 5.0) if torch.is_tensor(u) else min(5.0, max(1.0, u * 4.0 + 1.0))


class TwoHeadClassifier(nn.Module):
    def __init__(self, encoder, n_types=len(LABELS), dropout=0.1):
        super().__init__()
        self.encoder = encoder
        hidden = encoder.config.hidden_size if hasattr(encoder.config, "hidden_size") else encoder.config.dim
        self.dropout = nn.Dropout(dropout)
        self.type_head = nn.Linear(hidden, n_types)
        self.sev_head = nn.Linear(hidden, 1)
        self.n_types, self.p_drop = n_types, dropout

    @classmethod
    def from_encoder(cls, name_or_path, attn_implementation="sdpa", **kw):
        enc = AutoModel.from_pretrained(name_or_path, attn_implementation=attn_implementation)
        return cls(enc, **kw)

    def forward(self, input_ids, attention_mask, output_attentions=False):
        out = self.encoder(input_ids=input_ids, attention_mask=attention_mask, output_attentions=output_attentions)
        cls = self.dropout(out.last_hidden_state[:, 0])           # [CLS] vector
        type_logits = self.type_head(cls)
        sev_unit = torch.sigmoid(self.sev_head(cls)).squeeze(-1)  # 0-1
        return type_logits, sev_unit, (out.attentions if output_attentions else None)

    # ------------------------------------------------------------ save / load
    def save(self, folder, tokenizer=None):
        folder = Path(folder)
        folder.mkdir(parents=True, exist_ok=True)
        self.encoder.save_pretrained(folder)
        if tokenizer is not None:
            tokenizer.save_pretrained(folder)
        torch.save({"type_head": self.type_head.state_dict(), "sev_head": self.sev_head.state_dict(),
                    "n_types": self.n_types, "dropout": self.p_drop}, folder / "heads.pt")
        (folder / "label_map.json").write_text(json.dumps(LABEL_MAP, indent=2))

    @classmethod
    def load(cls, folder, device="cpu", attn_implementation="eager"):
        """eager attention so output_attentions works (needed for the rollout heatmap)."""
        folder = Path(folder)
        saved_map = json.loads((folder / "label_map.json").read_text())
        if saved_map != LABEL_MAP:
            raise ValueError(f"label_map.json in {folder} does not match LABEL_MAP")
        heads = torch.load(folder / "heads.pt", map_location=device)
        model = cls.from_encoder(folder, attn_implementation=attn_implementation,
                                 n_types=heads["n_types"], dropout=heads["dropout"])
        model.type_head.load_state_dict(heads["type_head"])
        model.sev_head.load_state_dict(heads["sev_head"])
        return model.to(device).eval()


def two_head_loss(type_logits, sev_unit, y_type, y_sev_unit, sev_weight=1.0):
    """Cross-entropy for type + masked MSE for severity.
    y_sev_unit is NaN where severity is missing; those rows add 0 and the MSE is divided by
    max(number of rows with severity, 1)."""
    ce = F.cross_entropy(type_logits, y_type)
    mask = ~torch.isnan(y_sev_unit)
    target = torch.where(mask, y_sev_unit, torch.zeros_like(y_sev_unit))
    sq = (sev_unit.float() - target.float()) ** 2 * mask.float()
    n = mask.sum()
    mse = sq.sum() / n.clamp(min=1)
    return ce + sev_weight * mse, ce.detach(), mse.detach(), int(n)
