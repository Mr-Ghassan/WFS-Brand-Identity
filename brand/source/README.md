# Brand source

| File | Role |
|---|---|
| `reference/approved_icon_reference.png`, `reference/approved_wordmark_reference.png` | Approved artwork (source of truth for geometry) |
| `vectorize_icon.py` | Rebuilds the icon as an all-circle construction: 5 outer arcs, 5 aperture arcs, 5 biarc blade edges (G1). Writes `master/icon_geometry.json` incl. solid and one-colour gap variants |
| `vectorize_wordmark.py` | Rebuilds the wordmark (3× super-sampled potrace + straight-stroke clean-up + axis snapping). Writes `master/wordmark_geometry.json` |
| `qa_icon_fidelity.py`, `qa_wordmark_fidelity.py` | Overlay comparison of the masters against the approved art (IoU) |
| `brand_config.py` | Single source of truth: colours, roles, gradients, data palette, lockup proportions, fonts |
| `logo_lib.py`, `text_outline.py`, `geom.py` | SVG generation, HarfBuzz text-to-outline, Bézier/arc geometry |
| `build_logos.py`, `build_app_icons.py`, `build_graphics.py`, `build_extras.py`, `build_index.py` | Asset builders |
| `render.mjs` | Chromium (playwright-core) HTML → PDF/PNG renderer |
| `qa.py` | Package validation → `qa/QA_REPORT.md` |
| `illustrator/export_ai.jsx` | Illustrator script: SVG masters → native `.ai` |
| `build_all.sh` | Runs everything in order |
