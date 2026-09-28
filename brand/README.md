# WFS — Brand Identity 1.0 (2026)

**WFS — Wusool Financial System · نظام وصول المالي** — a global financial operating system. *A WUSOOL Tech Product.*

Brand direction **Concept C — Unified Financial Field** (form) · colour family **Concept A** (`#022329` `#0E3D42` `#14B8A6` `#7FE3D6` `#F3F5F2`) · typography **Instrument Sans** + **Myriad Arabic**.

| Start here | |
|---|---|
| Brand guidelines (A4 landscape, 53 pp) | [`guidelines/WFS_Brand_Guidelines_2026.pdf`](guidelines/WFS_Brand_Guidelines_2026.pdf) |
| Every file, what it's for | [`WFS_BRAND_ASSET_INDEX.md`](WFS_BRAND_ASSET_INDEX.md) |
| Primary logo | [`logo/svg/WFS_Logo_Horizontal_Primary.svg`](logo/svg/WFS_Logo_Horizontal_Primary.svg) · Inverse: [`WFS_Logo_Horizontal_Inverse.svg`](logo/svg/WFS_Logo_Horizontal_Inverse.svg) |
| Icon | [`icon/svg/WFS_Icon_Primary.svg`](icon/svg/WFS_Icon_Primary.svg) |
| Colour tokens | [`color/tokens/wfs-tokens.css`](color/tokens/wfs-tokens.css) · [`color/README.md`](color/README.md) |
| Typography | [`typography/README.md`](typography/README.md) |
| QA report | [`source/qa/QA_REPORT.md`](source/qa/QA_REPORT.md) |

```
brand/
├── guidelines/      WFS_Brand_Guidelines_2026.pdf · source/ (HTML + builder) · preview/ (page PNGs)
├── logo/            svg · pdf · png · ai (README) · preview        — lockups
├── icon/            svg · pdf · png · app · favicon                  — icon, app icons, favicons
├── wordmark/        svg · pdf · png · ai (README)
├── graphic-system/  patterns · fields · gradients · backgrounds · preview
├── color/           tokens (CSS/SCSS/JSON) · swatches (ASE/GPL/SVG)
├── typography/      README.md
├── motion/          WFS_Logo_Reveal.html (SVG + CSS reference prototype)
├── templates/       presentation · report · social · email-signature
├── source/          vector masters (JSON) · build scripts · approved reference art · QA
└── WFS_BRAND_ASSET_INDEX.md
```

## Rebuilding

Everything is generated from the vector masters by open-source tooling:

```bash
cd brand/source
pip install -r requirements.txt && npm install
WFS_FONT_DIR=/path/to/fonts ./build_all.sh      # ~1 minute; ends with the QA report
```

Fonts are referenced, not redistributed — see `typography/README.md`.

## Known limitations (v1.0)

- **Arabic font file not available at build time.** The approved Arabic typeface is Myriad Arabic (Adobe). Its licensed font file was not present, so the bilingual lockup was not generated and Arabic specimens in the guidelines use a clearly labelled proxy. Add the font files to `$WFS_FONT_DIR` and rerun `build_all.sh`.
- **No native `.ai` files.** They can only be written by Adobe Illustrator; run `source/illustrator/export_ai.jsx` in Illustrator to create them from the SVG masters. SVG and vector PDF masters open as editable paths in Illustrator.
- **CMYK values are approximations** (no ICC profile) — proof physically before print production.
