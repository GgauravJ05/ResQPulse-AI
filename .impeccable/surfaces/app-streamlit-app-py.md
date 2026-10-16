---
version: 1
slug: "app-streamlit-app-py"
primary_target: "app/streamlit_app.py"
related_targets: ["app/components.py","app/styles.py"]
---

# Dispatcher dashboard (Streamlit app)

Scope: the whole Streamlit app, all five screens. Mode: Operate. Audience: a 112 dispatcher; on demo day, judges watching on a projector. Task: submit a report (typed or voice), read the alert, see why, work the severity-sorted queue, check the model metrics. Constraints: behaviour, test-facing labels and API unchanged; no emoji; light ground.

## Direction contract

THESIS: A dispatcher console with the evaluation-grade calm of a Kaggle competition page, not a "command centre" costume. Refuses the dark cockpit, emoji tiles, gradient mastheads and the cream-and-italic-serif editorial look.

OWN-WORLD: Light grey ground #F5F5F3, white surfaces with 1px #E4E4E1 hairlines, no drop shadows. Ink #141414. Black pill buttons (Kaggle). One signal yellow #FFCC00 (Motion, Impeccable) for the live dot, active navigation, focus and the attention heatmap. Severity colours only where they mean severity. Figtree for all text; JetBrains Mono, small and uppercase-tracked, only for IDs, coordinates, scores and field labels.

STORY: The dispatcher sees what happened, how bad it is and where, with the evidence beside it, then confirms, dispatches or dismisses.

FIRST VIEWPORT: Kaggle-style white left rail with plain-text nav and a yellow-tinted active row; slim top bar with wordmark and a mono live/mock status pill; page title and one-line description; content in white panels. Alert card: type title and mono ID, severity pill right; left column summary and the severity ruler; right meta column (location, people, confidence, response time, responders, SDGs) like Kaggle's competition sidebar.

FORM: Pinned by the user (kaggle.com, motion.dev, impeccable.style); no concept roll. Signature move: the severity ruler, five segmented cells filled to the score with the value in mono, repeated in the alert card and every queue row. Seed key: none (user-pinned direction).

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
