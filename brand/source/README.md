# Brand source

| File | Role |
|---|---|
| `design_icon.py` | **Icon v2 generator**: original parametric aperture — outer circle R 500, aperture r 190, edge circle ρ 520 tangent at each tip, exact 5-fold symmetry; writes `master/icon_geometry.json` (solid + one-colour gap variants) |
| `reference/` | Concept study (retired) and approved wordmark artwork |
| `vectorize_wordmark.py` | Rebuilds the wordmark (3× super-sampled potrace + straight-stroke clean-up + axis snapping). Writes `master/wordmark_geometry.json` |
| `qa_wordmark_fidelity.py` | Overlay comparison of the masters against the approved art (IoU) |
| `brand_config.py` | Single source of truth: colours, roles, gradients, data palette, lockup proportions, fonts |
| `logo_lib.py`, `text_outline.py`, `geom.py` | SVG generation, HarfBuzz text-to-outline, Bézier/arc geometry |
| `build_logos.py`, `build_app_icons.py`, `build_graphics.py`, `build_extras.py`, `build_index.py` | Asset builders |
| `render.mjs` | Chromium (playwright-core) HTML → PDF/PNG renderer |
| `qa.py` | Package validation → `qa/QA_REPORT.md` |
| `illustrator/export_ai.jsx` | Illustrator script: SVG masters → native `.ai` |
| `build_all.sh` | Runs everything in order |
