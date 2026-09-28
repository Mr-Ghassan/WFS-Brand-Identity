# WFS typography — v1.0

## Typefaces

| Script | Family | Source | Licence | Weights used |
|---|---|---|---|---|
| Latin | **Instrument Sans** | Google Fonts / Fontsource (`@fontsource/instrument-sans`) | SIL Open Font License 1.1 | Regular 400 · Medium 500 · SemiBold 600 · Bold 700 |
| Arabic | **Myriad Arabic** (مايرى) | Adobe (Adobe Fonts / licensed desktop files) | Adobe commercial licence | Regular · Semibold · Bold (PostScript `MyriadArabic-Regular`, `MyriadArabic-Semibold`, `MyriadArabic-Bold`) |

Font files are **referenced, not redistributed** in this repository. The build scripts read fonts from `$WFS_FONT_DIR` (default `~/.wfs-fonts`):

```
$WFS_FONT_DIR/InstrumentSans-{Regular,Medium,SemiBold,Bold}-latin.ttf   (and -latin-ext)
$WFS_FONT_DIR/MyriadArabic-*.otf|ttf                                     (licensed Adobe files)
```

### Arabic font status in this build

The identified approved Arabic typeface is **Myriad Arabic** (the name given as "مايرى"). The licensed font file was **not available** in the environment that produced version 1.0 of the package, and Adobe Fonts kit access was not entitled for this account. Therefore:

- No Arabic text was converted to outlines in any logo file; `WFS_Logo_Full_Bilingual` was **not generated** (no substitute font used).
- Arabic specimens in the guidelines PDF are rendered with a **clearly labelled proxy** (Noto Sans Arabic, OFL) and a visible note on the Arabic pages.
- To finalise: copy the Myriad Arabic font files into `$WFS_FONT_DIR`, then run `source/build_all.sh`. The bilingual lockup is produced and the guidelines switch to Myriad Arabic automatically.

## Code

Code samples (developer portal, API docs) use **IBM Plex Mono** (SIL OFL 1.1), Regular and Medium.

## Hierarchy (digital, px)

| Style | Size / line | Weight | Tracking |
|---|---|---|---|
| Display | 56 / 58 | SemiBold 600 | −0.035 em |
| H1 | 40 / 44 | SemiBold 600 | −0.03 em |
| H2 | 28 / 32 | SemiBold 600 | −0.02 em |
| H3 | 20 / 26 | SemiBold 600 | −0.01 em |
| Body L | 17 / 26 | Regular 400 | 0 |
| Body | 15 / 22 | Regular 400 | 0 |
| Small | 13 / 18 | Regular 400 | 0 |
| Label | 11 / 14, caps | SemiBold 600 | +0.14 em |
| Caption | 11 / 15 | Regular 400 | 0 |
| UI number (KPI) | 24–32 | SemiBold 600, tabular | −0.01 em |
| Table figures | 13–14 | Regular 400, tabular | 0 |

Print: Display 36–48 pt · H1 26 pt · Body 9–10 pt / 1.5 · Caption 7 pt.
Arabic: set ~1.15 × the Latin size, line-height 1.6, never letter-spaced, no faux bold/italic. Layouts mirror in RTL; numerals, ISO currency codes and the WFS wordmark stay LTR.

## Financial numerals

- Always `font-feature-settings: "tnum" 1, "lnum" 1` (CSS token `--wfs-numeric`) in tables, KPIs, statements, chart axes.
- Right-align numeric columns; fixed decimals per currency (USD/EUR/GBP 2 · OMR/BHD/KWD 3 · JPY 0).
- Negatives: parentheses in statements `(5,318,950.00)`; true minus `−` (U+2212) in UI deltas. Never rely on colour alone.
- Currency: ISO code after the value (`48,612,480.25 USD`). Symbols only in local consumer contexts.
- Percentages: one decimal, explicit sign for change (`+4.9 %`).
- Abbreviate large values only in charts and tiles (`48.6M`), never in ledgers.
- Western digits (0–9) by default in financial UI; Eastern Arabic digits only when the user's locale requests them.

## Web embedding

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<!-- Myriad Arabic: serve via your Adobe Fonts web project (kit) -->
```
