"""Fill the GenHack template (docs/Final minihackathon genhack template.pptx) with the ResQPulse AI content.

The template's header band, section labels, section titles, footer, logos and slide numbers are kept exactly as given.
Only the body of each slide is rebuilt (same colours and fonts as the template: Poppins headings, Inter text, red C5221F
accent, F8FAFC cards). The instructions slide is removed, so the deck is the title slide + 6 content slides.

Run from the repo root:  .venv/bin/python scripts/build_deck.py
Output: docs/ResQPulse_AI_GenHack.pptx
Set FONT_DIR to a folder with Inter[opsz,wght].ttf and Poppins-*.ttf to get text-fit warnings measured with the real fonts.
"""
import copy
import os
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt
from lxml import etree

SRC = Path("docs/Final minihackathon genhack template.pptx")
OUT = Path("docs/ResQPulse_AI_GenHack.pptx")
TEAM = "P 25"

RED, NAVY, TEXT, MUTED = "C5221F", "0F172A", "1E293B", "64748B"
CARD, BORDER, WHITE = "F8FAFC", "CBD5E1", "FFFFFF"

# ---------------------------------------------------------------- text fit check (optional, needs the real fonts)
_FONT_DIR = os.environ.get("FONT_DIR")
_warnings = []


def _measure(text: str, size: float, bold: bool, font: str, width_in: float) -> int:
    """Number of wrapped lines for text at `size` pt in a box `width_in` inches wide."""
    from PIL import ImageFont
    if font == "Poppins":
        path = Path(_FONT_DIR) / ("Poppins-Bold.ttf" if bold else "Poppins-Regular.ttf")
        f = ImageFont.truetype(str(path), int(size * 10))
    else:
        f = ImageFont.truetype(str(Path(_FONT_DIR) / "Inter[opsz,wght].ttf"), int(size * 10))
        f.set_variation_by_name("Bold" if bold else "Regular")
    max_px = width_in * 72 * 10
    lines, cur = 1, ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if f.getlength(trial) <= max_px:
            cur = trial
        else:
            lines, cur = lines + 1, word
    return lines


# ---------------------------------------------------------------- helpers
def rgb(h: str) -> RGBColor:
    return RGBColor.from_string(h)


def clear_body(slide, top=Inches(1.3), bottom=Inches(6.75)):
    """Remove everything between the header band and the footer."""
    for sh in list(slide.shapes):
        if top <= sh.top < bottom:
            sh._element.getparent().remove(sh._element)


def card(slide, x, y, w, h, accent=True):
    s = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    s.adjustments[0] = 0.025
    s.fill.solid()
    s.fill.fore_color.rgb = rgb(CARD)
    s.line.color.rgb = rgb("E2E8F0")
    s.line.width = Pt(0.75)
    s.shadow.inherit = False
    if accent:
        bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x + 0.25), Inches(y), Inches(0.9), Inches(0.05))
        bar.fill.solid()
        bar.fill.fore_color.rgb = rgb(RED)
        bar.line.fill.background()
        bar.shadow.inherit = False
    return s


def box(slide, x, y, w, h, border=BORDER, fill=WHITE, lw=0.75):
    s = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    s.adjustments[0] = 0.08
    s.fill.solid()
    s.fill.fore_color.rgb = rgb(fill)
    s.line.color.rgb = rgb(border)
    s.line.width = Pt(lw)
    s.shadow.inherit = False
    return s


def _bullet(p, char="•", indent=0.17):
    pPr = p._p.get_or_add_pPr()
    pPr.set("marL", str(int(Inches(indent))))
    pPr.set("indent", str(-int(Inches(indent))))
    for tag in ("a:buNone", "a:buChar", "a:buAutoNum"):
        for el in pPr.findall(qn(tag)):
            pPr.remove(el)
    clr = etree.SubElement(pPr, qn("a:buClr"))
    etree.SubElement(clr, qn("a:srgbClr")).set("val", RED)
    etree.SubElement(pPr, qn("a:buChar")).set("char", char)


def text(slide, x, y, w, h, paras, size=11.25, font="Inter", color=TEXT, align=None, anchor=None, name=""):
    """paras: list of items. An item is a string, or a dict:
       {"runs": [(text, {"bold":bool,"color":hex,"size":pt,"font":name})...] | "t": str, "bullet": bool, "space": pt, "bold": bool,
        "size": pt, "font": name, "color": hex}"""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.04)
    tf.margin_top = tf.margin_bottom = Inches(0.02)
    if anchor:
        tf.vertical_anchor = anchor
    used = 0.0
    first = True
    for item in paras:
        if isinstance(item, str):
            item = {"t": item}
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        if align or item.get("align"):
            p.alignment = item.get("align", align)
        p.space_before = Pt(item.get("space", 0))
        runs = item.get("runs") or [(item["t"], {})]
        p_size = item.get("size", size)
        if item.get("bullet"):
            _bullet(p)
        line_text, any_bold = "", False
        for t, o in runs:
            r = p.add_run()
            r.text = t
            f = r.font
            f.name = o.get("font", item.get("font", font))
            f.size = Pt(o.get("size", p_size))
            f.bold = o.get("bold", item.get("bold", False))
            f.color.rgb = rgb(o.get("color", item.get("color", color)))
            line_text += t
            any_bold = any_bold or bool(f.bold)
        if _FONT_DIR:
            inner = w - 0.08 - (0.17 if item.get("bullet") else 0)
            n = _measure(line_text, p_size, any_bold, item.get("font", font), inner)
            used += n * p_size * 1.2 / 72 + item.get("space", 0) / 72
    if _FONT_DIR and used > h + 0.02:
        _warnings.append(f"OVERFLOW {name or paras[0] if isinstance(paras[0], str) else name}: needs {used:.2f}in, has {h:.2f}in")
    return tb


def heading(slide, x, y, w, t):
    return text(slide, x, y, w, 0.38, [{"t": t, "font": "Poppins", "size": 15, "bold": True, "color": NAVY}], name=t)


def sub(slide, x, y, w, t):
    return text(slide, x, y, w, 0.3, [{"t": t, "size": 11.25, "bold": True, "color": NAVY}], name=t)


def set_run_text(shape, new: str):
    """Replace the text of a template text box, keeping the first run's formatting."""
    tf = shape.text_frame
    p = tf.paragraphs[0]
    runs = p.runs
    runs[0].text = new
    for r in runs[1:]:
        r._r.getparent().remove(r._r)
    for extra in tf.paragraphs[1:]:
        extra._p.getparent().remove(extra._p)


def find(slide, startswith):
    for sh in slide.shapes:
        if sh.has_text_frame and sh.text_frame.text.strip().startswith(startswith):
            return sh
    raise KeyError(startswith)


def B(label, rest, **kw):
    return {"runs": [(label, {"bold": True, "color": NAVY}), (rest, {})], "bullet": True, "space": kw.get("space", 5)}


def Bp(t, space=5):
    return {"t": t, "bullet": True, "space": space}


# ---------------------------------------------------------------- slides
def slide_title(s):
    set_run_text(find(s, "[ Insert Problem Statement Title"), "EmergencyScribe (ResQPulse AI)")
    set_run_text(find(s, "[ e.g., AI"), "Generative AI / Public Safety")
    set_run_text(find(s, "[ Insert SDG"), "SDG 11.5 · 3.6 · 13.1 · 16.1")


def slide_solution(s):
    clear_body(s)
    card(s, 0.54, 1.42, 6.55, 5.15)
    heading(s, 0.78, 1.62, 6.0, "Solution Overview")
    sub(s, 0.78, 2.08, 6.0, "Core Concept & Approach:")
    text(s, 0.78, 2.42, 6.1, 4.0, [
        B("One alert from one messy report. ", "ResQPulse AI turns an emergency report, typed or spoken, into a structured, prioritised, explainable alert for a 112 dispatcher.", space=0),
        B("Three models, one pipeline. ", "Whisper transcribes the voice, DistilBERT classifies the incident (8 types) and scores severity 1 to 5, Flan-T5 extracts location, people, injuries, hazards and a summary."),
        B("Built for the dispatcher. ", "Severity-sorted queue, map pins, suggested responders and SDG tags. A human confirms, dispatches or dismisses every alert."),
        B("Working prototype. ", "FastAPI backend and Streamlit app running real models offline on a laptop, tested end to end with typed and voice input."),
    ], size=13.5, name="solution-left")
    card(s, 7.25, 1.42, 5.54, 5.15)
    heading(s, 7.5, 1.62, 5.0, "Innovation & Uniqueness")
    sub(s, 7.5, 2.08, 5.0, "Key Differentiators:")
    text(s, 7.5, 2.42, 5.1, 4.0, [
        B("A full alert, not just a label: ", "type, continuous severity, fields and summary.", space=0),
        B("Explainable: ", "an attention heatmap shows which words drove the decision."),
        B("Voice in: ", "editable transcript so the dispatcher can fix a misheard word."),
        B("Duplicate reports flagged ", "so ten messages about one fire do not become ten alerts."),
        B("Small models, no cloud: ", "DistilBERT and Flan-T5-base run offline."),
        B("Honest evaluation: ", "scored on 144 real reports the models never saw."),
    ], size=13.5, name="solution-right")


def slide_tech(s):
    clear_body(s)
    card(s, 0.54, 1.42, 4.55, 5.15)
    heading(s, 0.78, 1.62, 4.0, "Technology Stack")
    text(s, 0.78, 2.15, 4.1, 4.3, [
        B("Frontend: ", "Streamlit, Folium map", space=0),
        B("Backend: ", "Python FastAPI"),
        B("Database: ", "in-memory store with JSONL logs for alerts and dispatcher corrections"),
        B("Hardware/IoT: ", "none, runs on a laptop with a microphone"),
        B("AI / Cloud: ", "PyTorch and Hugging Face: DistilBERT, Flan-T5-base, faster-whisper small.en, MiniLM duplicate check; scikit-learn baseline; trained on Kaggle T4 GPUs"),
        B("Maps: ", "offline gazetteer, OpenStreetMap Nominatim"),
    ], size=13, name="tech-left")
    card(s, 5.25, 1.42, 7.54, 5.15)
    heading(s, 5.5, 1.62, 7.0, "System Architecture / Flow Diagram")
    # 4 columns
    cw, gap, x0 = 1.55, 0.3, 5.5
    cx = [x0 + i * (cw + gap) for i in range(4)]
    y1, y2, bh = 2.3, 4.2, 1.65

    def stage(x, y, w, h, title, lines, accent=False):
        b = box(s, x, y, w, h, border=RED if accent else BORDER, lw=1.25 if accent else 0.75)
        text(s, x + 0.05, y + 0.08, w - 0.1, h - 0.12,
             [{"t": title, "font": "Poppins", "bold": True, "size": 11, "color": NAVY, "align": PP_ALIGN.CENTER}] +
             [{"t": ln, "size": 10, "color": "334155", "space": 3} for ln in lines], size=10, name=f"stage-{title}")
        return b

    stage(cx[0], y1, cw, bh, "Typed report", ["Text from the call taker or a message"])
    stage(cx[0], y2, cw, bh, "Voice call", ["Whisper small.en turns speech into text", "Dispatcher can edit it"])
    stage(cx[1], y1, cw, bh, "DistilBERT", ["Incident type (8 classes)", "Severity 1 to 5", "Attention heatmap"], accent=True)
    stage(cx[1], y2, cw, bh, "Flan-T5", ["Location, people, injuries, hazards, summary"], accent=True)
    mid_h = (y2 + bh) - y1
    stage(cx[2], y1, cw, mid_h, "FastAPI", ["Builds the alert", "Geocodes the place", "Suggests responders", "Tags SDGs", "Flags duplicates", "Logs corrections"])
    stage(cx[3], y1, cw, mid_h, "Streamlit dashboard", ["Alert card", "Attention heatmap", "Severity-sorted queue", "Incident map", "Confirm, dispatch or dismiss"])
    for col in range(3):
        for yy in ([y1, y2] if col < 2 else [y1 + mid_h / 2 - bh / 2]):
            a = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(cx[col] + cw + 0.04), Inches(yy + (bh / 2 - 0.12 if col < 2 else 0.0)),
                                   Inches(gap - 0.08), Inches(0.24))
            a.fill.solid()
            a.fill.fore_color.rgb = rgb(RED)
            a.line.fill.background()
            a.shadow.inherit = False
    text(s, 5.5, 6.05, 7.0, 0.4, [{"t": "Typed reports go to both models; voice goes through Whisper first. A human reviews every alert.",
                                   "size": 9.5, "color": MUTED}], size=9.5, name="diagram-caption")


def slide_method(s):
    clear_body(s)
    card(s, 0.54, 1.42, 6.95, 5.15)
    heading(s, 0.78, 1.62, 6.4, "Methodology")
    steps = [
        ("1. Data. ", "Real crisis tweets (HumAID, CrisisLexT26, Kaggle negatives, about 37,000 after cleaning) plus 710 call-style reports written by Claude, with a fixed schema: 8 incident types, severity 1 to 5."),
        ("2. Train. ", "DistilBERT with two heads (type: cross-entropy, severity: masked MSE). Flan-T5-base fine-tuned to write the alert fields. TF-IDF + logistic regression as the baseline."),
        ("3. Serve. ", "Whisper, then classify with attention rollout, then extract fields (retry, rule fallback, people-count rule), then geocode, suggest responders and check for duplicates."),
        ("4. Evaluate. ", "One script on held-out sets: 107 call-style reports, 7,755 real tweets (6 crises never seen) and a 144-report gold set audited by a person."),
        ("5. Human in the loop. ", "The dispatcher confirms, dispatches or dismisses; every correction is logged for later learning."),
    ]
    text(s, 0.78, 2.12, 6.5, 4.35, [B(a, b, space=0 if i == 0 else 6) for i, (a, b) in enumerate(steps)], size=12.5, name="method")
    card(s, 7.65, 1.42, 5.14, 5.15)
    heading(s, 7.9, 1.62, 4.6, "Measurable Impact")
    kpis = [("91%", "of real emergencies caught (baseline 71%)"),
            ("98%", "of the most severe reports not dismissed (baseline 75%)"),
            ("0.77", "macro F1 on real reports (baseline 0.56)"),
            ("0.75", "severity RMSE on call-style reports (MSE 0.57)"),
            ("~3 s", "per report on a laptop, fully offline")]
    for i, (big, lab) in enumerate(kpis):
        y = 2.2 + i * 0.86
        text(s, 7.9, y, 1.35, 0.6, [{"t": big, "font": "Poppins", "bold": True, "size": 20, "color": RED}], name="kpi-" + big)
        text(s, 9.3, y + 0.05, 3.35, 0.7, [{"t": lab, "size": 12.5}], size=12.5, name="kpi-lab-" + big)


def _table(slide, x, y, w, col_w, rows, header=True, size=10, row_h=0.3):
    shape = slide.shapes.add_table(len(rows), len(rows[0]), Inches(x), Inches(y), Inches(w), Inches(row_h * len(rows)))
    tbl = shape.table
    tblPr = tbl._tbl.tblPr
    for attr in ("bandRow", "firstRow"):
        tblPr.set(attr, "0")
    sid = tblPr.find(qn("a:tableStyleId"))
    if sid is not None:
        sid.text = "{2D5ABB26-0587-4C30-8999-92F81FD0307C}"   # No Style, No Grid
    for j, cw in enumerate(col_w):
        tbl.columns[j].width = Inches(cw)
    for i, row in enumerate(rows):
        tbl.rows[i].height = Inches(row_h)
        for j, val in enumerate(row):
            c = tbl.cell(i, j)
            c.margin_left = c.margin_right = Inches(0.06)
            c.margin_top = c.margin_bottom = Inches(0.02)
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            c.fill.solid()
            c.fill.fore_color.rgb = rgb(NAVY if (header and i == 0) else (WHITE if i % 2 else "F1F5F9"))
            p = c.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT if j == 0 else PP_ALIGN.CENTER
            r = p.add_run()
            r.text = val
            r.font.name = "Inter"
            r.font.size = Pt(size)
            r.font.bold = (header and i == 0) or j == 0
            r.font.color.rgb = rgb(WHITE if (header and i == 0) else TEXT)
    return shape


def slide_results(s):
    clear_body(s)
    card(s, 0.54, 1.42, 7.55, 5.15)
    heading(s, 0.78, 1.62, 7.0, "Result")
    sub(s, 0.78, 2.05, 7.0, "Incident type: baseline → our DistilBERT")
    _table(s, 0.78, 2.35, 7.07, [2.6, 1.49, 1.49, 1.49], [
        ["Test set", "Macro precision", "Macro recall", "Macro F1"],
        ["Gold: 144 real reports", "0.61 → 0.76", "0.59 → 0.79", "0.56 → 0.77"],
        ["Call-style: 107 reports", "0.89 → 0.96", "0.86 → 0.96", "0.87 → 0.96"],
        ["Real tweets: 7,755", "0.73 → 0.79", "0.62 → 0.75", "0.63 → 0.75"],
    ], size=10, row_h=0.32)
    sub(s, 0.78, 3.7, 7.0, "Safety, severity, extraction and voice")
    _table(s, 0.78, 4.02, 7.07, [4.9, 2.17], [
        ["Metric", "Value"],
        ["Real emergencies caught / severe reports not dismissed (gold)", "0.91 / 0.98"],
        ["False alarms on non-emergencies (gold)", "0.38"],
        ["Severity RMSE / MSE, call-style reports (107)", "0.75 / 0.57"],
        ["Severity RMSE / MSE, real reports (gold 144)", "1.33 / 1.77"],
        ["Field extraction: output parses / location F1 (call-style)", "100% / 0.78"],
        ["Whisper word error rate, synthetic voices (clean / noisy)", "9.9% / 15.5%"],
    ], size=9.5, row_h=0.28)
    text(s, 0.78, 6.05, 7.1, 0.45, [{"t": "Gold labels were written by Claude and checked by a person (30 of 30 agreed). Voice was tested on text-to-speech audio, not real callers.",
                                    "size": 9, "color": MUTED}], size=9, name="results-note")
    card(s, 8.25, 1.42, 4.54, 5.15)
    heading(s, 8.5, 1.62, 4.0, "Confusion Matrix (Gold)")
    pic = s.shapes.add_picture("reports/confusion_matrix_gold_ml2.png", Inches(8.45), Inches(2.1))
    scale = min(4.14 / (pic.width / 914400), 3.7 / (pic.height / 914400))
    pic.width, pic.height = int(pic.width * scale), int(pic.height * scale)
    pic.left = int(Inches(8.25 + (4.54 - pic.width / 914400) / 2))
    text(s, 8.45, 5.85, 4.15, 0.6, [{"t": "DistilBERT on 144 real reports. Strongest gains: violent crime and fire, where word counting fails.",
                                    "size": 9, "color": MUTED}], size=9, name="cm-note")


def slide_feasibility(s):
    clear_body(s)
    cols = [
        ("Feasibility", [
            ("Built and tested in 12 hours: ", "data, three models, API and dashboard, 52 automated tests."),
            ("Small models: ", "DistilBERT and Flan-T5-base run on a laptop, about 3 s per report."),
            ("Free tools only: ", "Kaggle T4 GPUs, Hugging Face, open datasets."),
            ("Demonstrated: ", "typed and voice reports through the real models to a prioritised queue and map."),
        ]),
        ("Potential Risks", [
            ("False alarms: ", "38% of non-emergency tweets flagged on the gold set."),
            ("Severity: ", "weaker on news-style text (RMSE 1.33)."),
            ("Data: ", "no real 112 calls; MEDICAL is synthetic only; gold labels by Claude."),
            ("Voice: ", "place names and numbers misheard (word error 10 to 16%)."),
            ("Scope: ", "English only."),
        ]),
        ("Mitigation Plan", [
            ("Human in the loop: ", "a dispatcher confirms every alert and can edit the transcript."),
            ("Recall first: ", "98% of severe reports kept; false alarms cost less than misses."),
            ("Fallbacks: ", "rule-based extractor, offline models, mock mode, backup demo video."),
            ("Next: ", "real anonymised 112 transcripts, Hindi, Marathi and Hinglish, learning from logged corrections."),
        ]),
    ]
    w, gap = 3.9, 0.265
    for i, (title, items) in enumerate(cols):
        x = 0.54 + i * (w + gap)
        card(s, x, 1.42, w, 5.15)
        heading(s, x + 0.22, 1.62, w - 0.4, title)
        text(s, x + 0.22, 2.15, w - 0.42, 4.3, [B(a, b, space=0 if k == 0 else 7) for k, (a, b) in enumerate(items)],
             size=14, name=f"feas-{title}")


def slide_refs(s):
    clear_body(s)
    find(s, "RESEARCH & REFERENCES").width = Inches(8)   # the template box is narrow enough to wrap this title
    card(s, 0.54, 1.42, 12.25, 5.15)
    heading(s, 0.78, 1.62, 11.0, "Key Reference Sources")
    groups = [
        ("Dataset Sources: ", [
            "HumAID, Alam et al., ICWSM 2021: crisisnlp.qcri.org/humaid_dataset",
            "CrisisLexT26, Olteanu et al., 2015: crisislex.org/data-collections.html",
            "Kaggle, Natural Language Processing with Disaster Tweets (negatives): kaggle.com/competitions/nlp-getting-started",
            "Ours: 710 call-style reports and a 144-report gold set: kaggle.com/datasets/ggauravj05/resqpulse-data",
        ]),
        ("Research Papers / Patent References: ", [
            "Vaswani et al., Attention Is All You Need, 2017; Sanh et al., DistilBERT, 2019",
            "Chung et al., Scaling Instruction-Finetuned Language Models (Flan-T5), 2022",
            "Abnar and Zuidema, Quantifying Attention Flow in Transformers (attention rollout), ACL 2020",
            "Radford et al., Robust Speech Recognition via Large-Scale Weak Supervision (Whisper), 2022",
        ]),
        ("Open Source Libraries & APIs: ", [
            "PyTorch, Hugging Face Transformers, faster-whisper, sentence-transformers (all-MiniLM-L6-v2), scikit-learn",
            "FastAPI, Streamlit, Folium, rapidfuzz; OpenStreetMap Nominatim for geocoding",
        ]),
    ]
    paras = []
    for gi, (label, lines) in enumerate(groups):
        paras.append({"runs": [(label, {"bold": True, "color": NAVY})], "bullet": True, "space": 0 if gi == 0 else 12})
        for ln in lines:
            paras.append({"t": ln, "size": 12, "color": "334155", "space": 4})
    # sub-lines are indented via left margin on a separate text frame: keep simple, indent with spaces
    tb = text(s, 0.78, 2.12, 11.7, 4.3, paras, size=12, name="refs")
    for p in tb.text_frame.paragraphs:
        pPr = p._p.get_or_add_pPr()
        if pPr.find(qn("a:buChar")) is None:
            pPr.set("marL", str(int(Inches(0.4))))
            pPr.set("indent", "0")


# ---------------------------------------------------------------- main
def main() -> None:
    prs = Presentation(str(SRC))
    slides = list(prs.slides)
    builders = {0: slide_title, 2: slide_solution, 3: slide_tech, 4: slide_method, 5: slide_results, 6: slide_feasibility, 7: slide_refs}
    for idx, fn in builders.items():
        fn(slides[idx])
    # remove the instructions slide (index 1)
    sldIdLst = prs.slides._sldIdLst
    sld = sldIdLst[1]
    prs.part.drop_rel(sld.rId)
    sldIdLst.remove(sld)
    # footer: team number and slide numbers
    for n, slide in enumerate(prs.slides, 1):
        for sh in slide.shapes:
            if not sh.has_text_frame:
                continue
            t = sh.text_frame.text.strip()
            if t.startswith("[ Team No"):
                set_run_text(sh, f"Team {TEAM}")
            elif t.startswith("Slide 0"):
                set_run_text(sh, f"Slide {n:02d} of 07")
    OUT.parent.mkdir(exist_ok=True)
    prs.save(str(OUT))
    print("saved", OUT, "slides:", len(prs.slides))
    for w in _warnings:
        print(w)


if __name__ == "__main__":
    main()
