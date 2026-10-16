---
name: ResQPulse AI
description: A light, flat dispatcher console that turns a messy emergency report into a prioritised, explainable alert.
colors:
  ground: "#F5F5F3"
  surface: "#FFFFFF"
  ink: "#141414"
  ink-2: "#4D4D4D"
  ink-3: "#6B6B68"
  hair: "#E4E4E1"
  hair-2: "#D4D4D0"
  signal: "#FFCC00"
  signal-tint: "#FFF4CC"
  hover-wash: "#F2F2F0"
  track: "#ECECE9"
  ink-hover: "#2E2E2E"
  disabled-ink: "#A3A3A0"
  disabled-fill: "#B8B8B4"
  disabled-wash: "#FAFAF9"
  severity-critical: "#D92D20"
  severity-high: "#C4320A"
  severity-high-bar: "#E8590C"
  severity-medium: "#F5B301"
  severity-medium-bar: "#E0A100"
  severity-low: "#2F7D4F"
  severity-none: "#5C5C59"
  severity-none-bar: "#8A8A86"
typography:
  headline:
    fontFamily: "Figtree, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "2.35rem"
    fontWeight: 600
    letterSpacing: "-0.02em"
  alert-title:
    fontFamily: "Figtree, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "1.75rem"
    fontWeight: 600
    lineHeight: 1.15
    letterSpacing: "-0.025em"
  title:
    fontFamily: "Figtree, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "1.15rem"
    fontWeight: 600
    letterSpacing: "-0.02em"
  summary:
    fontFamily: "Figtree, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "1.22rem"
    fontWeight: 500
    lineHeight: 1.55
  body:
    fontFamily: "Figtree, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
  numeral:
    fontFamily: "Figtree, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "1.45rem"
    fontWeight: 600
    letterSpacing: "-0.02em"
    fontFeature: "tnum"
  label:
    fontFamily: "JetBrains Mono, ui-monospace, SFMono-Regular, Menlo, monospace"
    fontSize: "0.68rem"
    fontWeight: 400
    letterSpacing: "0.1em"
  button:
    fontFamily: "Figtree, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "0.93rem"
    fontWeight: 600
rounded:
  cell-mini: "2px"
  cell: "3px"
  token: "6px"
  flag: "10px"
  control: "12px"
  row: "14px"
  panel: "16px"
  pill: "999px"
spacing:
  hairline-gap: "4px"
  xs: "0.5rem"
  sm: "0.9rem"
  md: "1rem"
  lg: "1.6rem"
  xl: "1.8rem"
components:
  button-primary:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.surface}"
    typography: "{typography.button}"
    rounded: "{rounded.pill}"
    padding: "0.5rem 1.15rem"
  button-primary-hover:
    backgroundColor: "{colors.ink-hover}"
    textColor: "{colors.surface}"
  button-primary-disabled:
    backgroundColor: "{colors.disabled-fill}"
    textColor: "{colors.surface}"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.button}"
    rounded: "{rounded.pill}"
    padding: "0.5rem 1.15rem"
  button-secondary-disabled:
    backgroundColor: "{colors.disabled-wash}"
    textColor: "{colors.disabled-ink}"
  input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
  nav-item:
    textColor: "{colors.ink-2}"
    rounded: "{rounded.control}"
    padding: "0.62rem 0.9rem"
  nav-item-hover:
    backgroundColor: "{colors.hover-wash}"
  nav-item-active:
    backgroundColor: "{colors.signal-tint}"
    textColor: "{colors.ink}"
  panel:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.panel}"
    padding: "1.5rem 1.6rem"
  queue-row:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.row}"
    padding: "1.05rem 1.25rem"
  metric-tile:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.row}"
    padding: "1rem 1.15rem"
  severity-pill:
    backgroundColor: "{colors.severity-critical}"
    textColor: "{colors.surface}"
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    padding: "0.38rem 0.9rem"
  status-pill:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    padding: "0.38rem 0.85rem"
  tag:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.pill}"
    padding: "0.32rem 0.8rem"
  notice:
    backgroundColor: "{colors.signal-tint}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "0.85rem 1.1rem"
---

# Design System: ResQPulse AI

## Overview

**Creative North Star: "The Competition Page"**

ResQPulse is a dispatcher console with the evaluation-grade calm of a Kaggle competition page. A light grey ground carries white panels drawn with single hairlines; nothing floats, nothing glows. Black pill buttons do the acting, one signal yellow marks what is live, current or under attention, and every other colour on screen is a severity colour that means severity. The world is built for a projector in a lit hall as much as for a dispatcher's desk, so contrast stays high and ornament stays out.

Hierarchy comes from type weight, size and position rather than colour. Figtree sets everything a person reads; JetBrains Mono, small, uppercase and tracked, is reserved for machine facts: IDs, coordinates, scores, field labels and the live status. The signature is the severity ruler, five segmented cells filled to a continuous score with the value beside it in mono, repeated at full size on the alert and in miniature on every queue row.

The system rejects the dark command-centre cockpit, emoji tiles, gradient mastheads and the cream-and-italic-serif editorial look the previous build used.

**Key Characteristics:**
- Light grey ground, white surfaces, 1px hairlines, no elevation shadows.
- Black pill buttons; one signal yellow for live state, active navigation, selection and attention.
- Severity colours appear only where they encode severity.
- Figtree for reading, JetBrains Mono only for machine facts.
- The five-cell severity ruler as the recurring signature.
- Words, never pictograms or emoji.

## Colors

A near-achromatic console with one yellow signal and a five-step severity scale that only ever speaks about severity.

### Primary
- **Console Ink** (ink): text, headings, primary buttons, the focus outline, and the probability bars. The acting colour; black pills are where the dispatcher does something.
- **Signal Yellow** (signal): the live-status dot, text selection, the attention heatmap shading (as alpha of the same yellow) and the brand mark stroke. Never a fill for buttons or large areas.
- **Signal Tint** (signal-tint): the active navigation row and the inline notice background (low-confidence transcript warning).

### Secondary (severity scale)
- **Critical Red** (severity-critical): critical pill fill, ruler fill, map marker, injury tag dot.
- **High Rust** (severity-high) for the pill and map marker; **High Orange** (severity-high-bar) for the ruler fill.
- **Medium Amber** (severity-medium) for the pill (with ink text) and map marker; **Medium Ochre** (severity-medium-bar) for the ruler fill and the hazard tag dot.
- **Low Green** (severity-low): pill, ruler and marker.
- **Non-emergency Slate** (severity-none) for the pill; **Slate Grey** (severity-none-bar) for the ruler.

### Neutral
- **Ground** (ground): the app background behind every panel.
- **Surface** (surface): panels, queue rows, metric tiles, inputs, the left rail, secondary buttons, tags.
- **Ink 2** (ink-2): body copy, ledes, inactive navigation labels.
- **Ink 3** (ink-3): captions, field labels, IDs, coordinates, crumbs.
- **Hairline** (hair): panel and row borders, dividers, rail edge.
- **Hairline Strong** (hair-2): control borders, tag and pill outlines, hover border on rows, dashed empty-state border.
- **Hover Wash** (hover-wash): navigation row hover.
- **Track** (track): the empty part of ruler cells and probability bars.
- **Ink Hover** (ink-hover), **Disabled Ink** (disabled-ink), **Disabled Fill** (disabled-fill), **Disabled Wash** (disabled-wash): button states only.

### Named Rules
**The One Signal Rule.** Signal yellow marks live state, the active place, selection and model attention. It is never a button, a heading colour or decoration; if a screen has yellow, the yellow means "this is live, current, or what the model looked at".

**The Severity Means Severity Rule.** The five severity colours appear only on severity pills, ruler fills, map markers and the injury/hazard dots. A green success or a red error that is not a severity is not drawn in the severity palette.

## Typography

**Display Font:** Figtree (with -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif)
**Body Font:** Figtree
**Label/Mono Font:** JetBrains Mono (with ui-monospace, SFMono-Regular, Menlo, monospace)

**Character:** A friendly, open geometric sans carries every human sentence at confident weights with tight tracking; a technical mono, small and uppercase, labels the machine's facts so the two voices never blur.

### Hierarchy
- **Headline** (600, 2.35rem, -0.02em): the one page title per screen, balanced wrap.
- **Alert Title** (600, 1.75rem, line-height 1.15, -0.025em): the incident type on the alert panel. The non-emergency card uses a quieter 1.5rem.
- **Title** (600, 1.15rem): section headings within a screen (Queue, Incident map, metric groups). Sub-sections step down to 0.98rem.
- **Summary** (500, 1.22rem, line-height 1.55, max 60ch): the alert's one-sentence summary in ink; the most-read line on the alert.
- **Body** (400, 1rem, ink-2, max 72ch): ledes (1.02rem), queue summaries (0.97rem), captions in ink-3.
- **Numeral** (600, 1.45rem, tabular figures): people affected, confidence, response time; units in a small 0.85rem ink-3 suffix.
- **Label** (JetBrains Mono, 0.68 to 0.74rem, 0.06 to 0.1em tracking, uppercase, ink-3): field labels, metric labels, alert ID line, severity and status pills, the live pill, heatmap legend.
- **Button** (600, 0.93rem): every button label.

### Named Rules
**The Machine Voice Rule.** Mono is only for things a machine produced or keys on: IDs, coordinates, scores, field and metric labels, status. A sentence a person reads is never set in mono.

**The Tabular Number Rule.** Every number that can change between alerts (scores, counts, percentages, latencies) uses tabular figures so values do not jitter across rows.

## Layout

A left rail plus a single content column capped at 1200px. The rail is a white surface with a hairline right edge: brand mark, plain-text navigation, a hairline divider, the backend settings expander and a small footer. The content column opens with a slim top bar (breadcrumb left, mono status pill right, hairline below), then the page headline and a one-line lede, then content in white panels stacked with roughly 1rem between them.

The alert panel is a two-column grid: a flexible main column (summary, severity ruler, injuries, hazards, responders) and a 300px meta aside separated by a hairline and padded 1.6rem, with a 1.8rem gutter. Meta rows stack with 0.75rem vertical padding and hairline separators, like a competition page sidebar. Queue rows are full-width cards; their right cluster (mini ruler, severity pill, status tag, duplicate tag) wraps under the title on narrow widths. Queue actions sit directly beneath each row as a horizontal button group with a small gap, Dispatch the only black pill among them.

Below 900px the alert grid collapses to one column, the aside loses its left hairline and gains a top hairline, and probability rows put the bar on its own line. Spacing is rem-based and moderate: 4px between ruler cells, 0.5 to 0.9rem inside clusters, 1 to 1.6rem around panels.

## Elevation & Depth

Flat. Depth is tonal and linear: white surfaces on a grey ground, separated by 1px hairlines. No element casts an elevation shadow, and Streamlit's native button shadow is removed. The only shadow-like device is the expanding ring on the live status dot, which is motion signalling liveness, not depth, and stops under reduced motion.

### Shadow Vocabulary
- **Live pulse** (`box-shadow: 0 0 0 8px rgba(255, 204, 0, 0)` animated from `0 0 0 0 rgba(255, 204, 0, 0.7)` over 2.2s): the live-status dot only.

### Named Rules
**The Hairline Rule.** Surfaces separate by a 1px hairline and a change of tone, never by a drop shadow. Hover strengthens a border (hair to hair-2, or to ink on buttons); it does not lift.

## Shapes

Soft rectangles and full pills. Containers round in steps by scale: panels and the heatmap 16px, queue rows, metric tiles, map and uploaders 14px, inputs, selects, expanders, tables, nav rows and notices 12px. Everything a person can press or that labels a state is a full pill: buttons, severity pills, status tags, entity tags, the live pill. Small data marks keep tight corners: ruler cells 3px (2px in the mini ruler), heatmap word chips 6px. Empty states use a dashed hair-2 border with no fill. The brand mark is a black rounded square with a yellow pulse line.

## Components

### Buttons
Quiet, confident pills; black means act.
- **Shape:** full pill (999px), 0.5rem 1.15rem padding, label 600 at 0.93rem.
- **Primary:** ink fill, white label, ink border. Used for Analyze Report and Dispatch: one primary per action group.
- **Secondary:** white fill, ink label, hair-2 border.
- **Hover / Focus:** secondary border shifts to ink; primary fill lifts to ink-hover. Background and border transition 0.2s on the console ease. Focus is a 2px ink outline, 2px offset.
- **Disabled:** secondary goes to the disabled wash with disabled-ink label and hairline border; primary goes to disabled-fill with a white label. Opacity stays at 1 so disabled text remains legible.
- **Scope:** the rule targets Streamlit base buttons excluding header controls, so the sidebar collapse chevron keeps its native, unboxed treatment.

### Chips
- **Severity pill:** filled with the severity's pill colour, white label (ink on Medium Amber), mono uppercase 0.74rem, 600, 0.08em tracking. The alert-card pill carries the score after the label.
- **Status tag:** white, hair-2 outline, mono uppercase 0.7rem in ink-2 (NEW, CONFIRMED, DISPATCHED). A duplicate tag uses the same form with an ink outline and ink label.
- **Entity tag:** white, hair-2 outline, Figtree 0.88rem in ink; injuries carry a 7px critical-red dot, hazards a medium-ochre dot, responders are 600 weight, SDG tags lead with a mono target number.

### Cards / Containers
- **Corner Style:** 16px panels, 14px rows and tiles.
- **Background:** surface on ground.
- **Shadow Strategy:** none (see Elevation & Depth).
- **Border:** 1px hair; queue rows strengthen to hair-2 on hover.
- **Internal Padding:** panels 1.5rem 1.6rem; queue rows 1.05rem 1.25rem; metric tiles 1rem 1.15rem.

### Inputs / Fields
- **Style:** white fill, hair-2 border, 12px radius, 1rem ink text; widget labels 600 at 0.88rem in ink. File and audio drop zones use a dashed hair-2 border at 14px.
- **Focus:** border shifts to ink.

### Navigation
- **Left rail:** plain-text items, Figtree 500 at 0.97rem in ink-2, 0.62rem 0.9rem padding, 12px rounded rows with 2px between them; the radio dot is hidden. Hover takes the hover wash; the active row takes signal tint with ink 600 text. On mobile the rail collapses behind Streamlit's native control.
- **Top bar:** breadcrumb in ink-3 with the current screen in ink 600, and a mono status pill (yellow pulsing dot when live, grey dot for mock data).

### Severity Ruler (signature)
Five equal cells on a 4px gap, track-coloured, filled left to right to a continuous 1 to 5 score in the severity's ruler colour (a 3.4 fills three cells and 40% of the fourth), with the value in mono 600 and a lighter "/ 5". Full size on the alert (12px cells, up to 420px); mini on queue rows (7px cells, fixed 110px). It carries an accessible label stating the score.

### Attention Heatmap
The report set at 1.2rem with generous 2.5 line height in a white panel; each word is a 6px-rounded chip shaded by signal yellow at an alpha stretched within the report, with a mono legend and a yellow ramp. Class probabilities follow as rows of name, an 8px ink bar on a track, and a mono percentage.

### Metric Tile
White, hairline, 14px radius; mono uppercase label in ink-3 that wraps rather than truncates, value 600 with tabular figures.

## Do's and Don'ts

### Do:
- **Do** put content in white panels with a 1px hair border on the ground; separate meta rows with hairlines.
- **Do** make the single most consequential action in a group the only black pill (Analyze Report, Dispatch).
- **Do** use the severity ruler wherever a severity score is shown, full size on detail views and mini in lists.
- **Do** set IDs, coordinates, scores and field labels in small uppercase tracked JetBrains Mono, and everything a person reads in Figtree.
- **Do** use tabular figures for every changing number.
- **Do** keep disabled controls at full opacity with a lighter label, so they stay readable on a projector.
- **Do** stop the live pulse under prefers-reduced-motion.

### Don't:
- **Don't** add drop shadows or lift on hover; depth is tone and hairline.
- **Don't** use signal yellow as a button, heading or decorative fill.
- **Don't** use severity colours for anything that is not severity.
- **Don't** use emoji or pictogram icons for incident types or responders; name them in words.
- **Don't** go dark, add gradient mastheads, or bring back cream grounds with italic serif display type.
