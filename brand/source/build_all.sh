#!/usr/bin/env bash
# WFS Brand Identity 1.0 — full, reproducible build.
# Requirements: Python 3.10+ (pillow numpy scipy scikit-image opencv-python-headless shapely
#   fonttools brotli uharfbuzz potracer cairosvg pypdf), Node 18+ (npm install here), Chromium.
# Fonts are referenced from $WFS_FONT_DIR (default ~/.wfs-fonts); see ../typography/README.md.
set -euo pipefail
cd "$(dirname "$0")"
export WFS_FONT_DIR="${WFS_FONT_DIR:-$HOME/.wfs-fonts}"
[ -d node_modules ] || npm install --silent
python3 vectorize_icon.py          # approved icon  -> master/icon_geometry.json (all-circle construction)
python3 vectorize_wordmark.py      # approved wordmark -> master/wordmark_geometry.json
python3 build_logos.py             # icon / wordmark / lockup matrix: SVG + PDF + PNG
python3 build_app_icons.py         # app icons, adaptive layers, favicons, manifest
python3 build_graphics.py          # patterns, fields, gradients, backgrounds, previews
python3 build_extras.py            # colour tokens & swatches, typography, motion, templates, AI docs, previews
(cd ../guidelines/source && python3 make_art_direction.py)
(cd ../guidelines/source && python3 build_guidelines.py)   # guidelines HTML -> PDF + page previews
python3 build_index.py             # WFS_BRAND_ASSET_INDEX.md
python3 qa.py                      # qa/QA_REPORT.md
