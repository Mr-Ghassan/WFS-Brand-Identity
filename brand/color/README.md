# WFS colour system — v1.0

Generated from `source/brand_config.py`. The five **core** colours are fixed; derived tones are controlled intermediate steps and are **not** core colours.

> **Print note:** CMYK values are uncalibrated approximations converted from sRGB without an ICC profile. Printed colour depends on process, substrate and profile — always proof physically against the HEX/RGB master. One CMYK value does not guarantee identical output across printers.

| Group | Name | HEX | RGB | CMYK (approx.) | Usage |
|---|---|---|---|---|---|
| Core | WFS Dark | `#022329` | 2 35 41 | 95 15 0 84 | Near-black teal. Primary dark ground, primary text on light. |
| Core | WFS Deep Teal | `#0E3D42` | 14 61 66 | 79 8 0 74 | Secondary dark ground, surfaces on dark, depth in the icon. |
| Core | WFS Primary Teal | `#14B8A6` | 20 184 166 | 89 0 10 28 | Signature brand colour. Icon, accents, data highlights. |
| Core | WFS Light Mint | `#7FE3D6` | 127 227 214 | 44 0 6 11 | Light accent. Icon light blade, accents on dark, highlights. |
| Core | WFS Soft Off-White | `#F3F5F2` | 243 245 242 | 1 0 1 4 | Primary light ground and text on dark. |
| Derived | Teal 800 | `#115E5F` | 17 94 95 | 82 1 0 63 | Derived. Icon dark blade on dark grounds; deep data series. |
| Derived | Teal 700 | `#0F7C74` | 15 124 116 | 88 0 6 51 | Derived. Accessible teal for text/links on light grounds. |
| Derived | Teal 600 | `#11998B` | 17 153 139 | 89 0 9 40 | Derived. Hover / pressed state of Primary Teal. |
| Derived | Mint 200 | `#B9EFE7` | 185 239 231 | 23 0 3 6 | Derived. Tints, selection, chart fills on light. |
| Derived | Mint 100 | `#DDF5F1` | 221 245 241 | 10 0 2 4 | Derived. Subtle tinted surfaces on light. |
| Derived | Slate 600 | `#4A5E61` | 74 94 97 | 24 3 0 62 | Derived neutral. Secondary text on light. |
| Derived | Slate 400 | `#80918F` | 128 145 143 | 12 0 1 43 | Derived neutral. Tertiary text, captions, disabled. |
| Derived | Line 200 | `#D6DEDB` | 214 222 219 | 4 0 1 13 | Derived neutral. Borders and dividers on light. |
| Derived | White | `#FFFFFF` | 255 255 255 | 0 0 0 0 | Pure white surface (cards, documents). |
| Derived | Line Dark | `#1E4A4F` | 30 74 79 | 62 6 0 69 | Derived. Borders and dividers on dark. |
| Derived | Mist 300 | `#9DB5B3` | 157 181 179 | 13 0 1 29 | Derived. Secondary text on dark. |
| Functional | Positive | `#0F7C74` | 15 124 116 | 88 0 6 51 | Gains, credits, success (Teal 700). |
| Functional | Negative | `#B4232F` | 180 35 47 | 0 81 74 29 | Losses, debits in deficit, errors. |
| Functional | Warning | `#B7791F` | 183 121 31 | 0 34 83 28 | Pending approvals, due soon. |
| Functional | Info | `#2F6F9F` | 47 111 159 | 70 30 0 38 | Neutral system information. |

## Data visualisation

Light surfaces: `#11A393`, `#3067C9`, `#C8691E`, `#B94E8A` · Dark surfaces: `#12A594`, `#5A8CE0`, `#D6782C`, `#C95C9E`

Validated for lightness band, chroma floor, colour-vision-deficiency and normal-vision separation (adjacent pairs), and ≥ 3:1 contrast against #FFFFFF, #0E3D42 and #022329. Assign in fixed order; teal is always series 1.

## Files

- `tokens/wfs-tokens.css` · `tokens/_wfs-tokens.scss` · `tokens/wfs-tokens.json`
- `swatches/WFS_Colors.ase` (Adobe apps) · `swatches/WFS_Colors.gpl` (GIMP / Inkscape / Krita) · `swatches/WFS_Core_Colors.svg`
