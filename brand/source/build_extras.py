"""WFS brand extras: colour tokens & swatch libraries, typography README, motion
prototype, templates, AI-format README + Illustrator conversion script."""
import os, sys, json, struct, subprocess, io
import cairosvg
from PIL import Image
import brand_config as B
import logo_lib as L

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
REC = []
def rec(asset, group, purpose, fmt, variant='', bg=''):
    REC.append(dict(asset=asset, group=group, purpose=purpose, format=fmt, variant=variant, backgrounds=bg))
def w(path, text):
    p = os.path.join(ROOT, path); os.makedirs(os.path.dirname(p), exist_ok=True); open(p, 'w').write(text); return p

# =================================================================== colour
def colour():
    allc = B.ALL()
    css = ['/* WFS Brand Identity v1.0 — colour tokens (generated from source/brand_config.py) */', ':root {']
    for k, v in allc.items(): css.append(f'  --wfs-{k}: {v["hex"]};  /* {v["name"]} */')
    for mode, r in B.ROLES.items():
        for k, v in r.items(): css.append(f'  --wfs-{mode}-{k.replace("_", "-")}: {v};')
    for i, c in enumerate(B.DATAVIZ['light']): css.append(f'  --wfs-data-{i+1}: {c};')
    for i, c in enumerate(B.DATAVIZ['dark']): css.append(f'  --wfs-data-{i+1}-dark: {c};')
    css.append('  --wfs-font-en: "Instrument Sans", system-ui, sans-serif;')
    css.append(f'  --wfs-font-ar: "{B.FONT_AR}", sans-serif;')
    css.append('  --wfs-numeric: "tnum" 1, "lnum" 1;')
    css.append('  --wfs-ease-standard: cubic-bezier(0.2, 0, 0, 1);')
    css.append('  --wfs-ease-converge: cubic-bezier(0.65, 0, 0.35, 1);')
    css.append('  --wfs-ease-lock: cubic-bezier(0.3, 1.2, 0.4, 1);')
    css.append('}')
    w('color/tokens/wfs-tokens.css', '\n'.join(css) + '\n')
    scss = ['// WFS Brand Identity v1.0 — colour tokens (generated)'] + [f'$wfs-{k}: {v["hex"]};' for k, v in allc.items()]
    w('color/tokens/_wfs-tokens.scss', '\n'.join(scss) + '\n')
    js = {'version': B.VERSION, 'core': {}, 'derived': {}, 'functional': {}, 'roles': B.ROLES, 'gradients': B.GRADIENTS, 'dataviz': B.DATAVIZ}
    for grp, src in (('core', B.CORE), ('derived', B.DERIVED), ('functional', B.FUNCTIONAL)):
        for k, v in src.items():
            js[grp][k] = dict(name=v['name'], hex=v['hex'], rgb=list(B.hex_rgb(v['hex'])), cmyk_approx=list(B.rgb_cmyk(v['hex'])), usage=v['desc'])
    w('color/tokens/wfs-tokens.json', json.dumps(js, indent=2, ensure_ascii=False) + '\n')
    # Adobe Swatch Exchange (.ase)
    def ase_block_color(name, hexv):
        r, g, b = [x / 255 for x in B.hex_rgb(hexv)]
        nm = (name + '\0').encode('utf-16-be')
        body = struct.pack('>H', len(name) + 1) + nm + b'RGB ' + struct.pack('>fff', r, g, b) + struct.pack('>H', 0)
        return struct.pack('>HI', 0x0001, len(body)) + body
    def ase_group(name, items):
        nm = (name + '\0').encode('utf-16-be')
        body = struct.pack('>H', len(name) + 1) + nm
        out = struct.pack('>HI', 0xC001, len(body)) + body
        for n, h in items: out += ase_block_color(n, h)
        return out + struct.pack('>HI', 0xC002, 0), 2 + len(items)
    blocks = b''; count = 0
    for gname, src in (('WFS Core', B.CORE), ('WFS Derived', B.DERIVED), ('WFS Functional', B.FUNCTIONAL)):
        bb, n = ase_group(gname, [(f'{v["name"]} {v["hex"]}', v['hex']) for v in src.values()]); blocks += bb; count += n
    os.makedirs(os.path.join(ROOT, 'color/swatches'), exist_ok=True)
    open(os.path.join(ROOT, 'color/swatches/WFS_Colors.ase'), 'wb').write(b'ASEF' + struct.pack('>HHI', 1, 0, count) + blocks)
    gpl = ['GIMP Palette', 'Name: WFS Brand Identity 1.0', 'Columns: 5', '#']
    for v in list(B.CORE.values()) + list(B.DERIVED.values()) + list(B.FUNCTIONAL.values()):
        r, g, b = B.hex_rgb(v['hex']); gpl.append(f'{r:3d} {g:3d} {b:3d}\t{v["name"]} {v["hex"]}')
    w('color/swatches/WFS_Colors.gpl', '\n'.join(gpl) + '\n')
    # swatch sheet (SVG + PNG)
    cells = ''
    for i, (k, v) in enumerate(B.CORE.items()):
        x = 40 + i * 300; fg = '#022329' if B.rel_lum(v['hex']) > .3 else '#F3F5F2'
        r, g, b = B.hex_rgb(v['hex']); cm = B.rgb_cmyk(v['hex'])
        cells += (f'<rect x="{x}" y="40" width="280" height="380" rx="14" fill="{v["hex"]}" stroke="#D6DEDB"/>'
                  f'<text x="{x+22}" y="84" fill="{fg}" font-family="Instrument Sans, sans-serif" font-size="22" font-weight="600">{v["name"]}</text>'
                  f'<text x="{x+22}" y="340" fill="{fg}" font-family="Instrument Sans, sans-serif" font-size="26" font-weight="600">{v["hex"]}</text>'
                  f'<text x="{x+22}" y="370" fill="{fg}" font-family="Instrument Sans, sans-serif" font-size="16">RGB {r} {g} {b}</text>'
                  f'<text x="{x+22}" y="394" fill="{fg}" font-family="Instrument Sans, sans-serif" font-size="16">CMYK≈ {cm[0]} {cm[1]} {cm[2]} {cm[3]}</text>')
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1560 460" width="1560" height="460"><title>WFS core colours</title><rect width="1560" height="460" fill="#FFFFFF"/>{cells}</svg>\n'
    w('color/swatches/WFS_Core_Colors.svg', svg)
    lines = ['# WFS colour system — v1.0', '', 'Generated from `source/brand_config.py`. The five **core** colours are fixed; derived tones are controlled intermediate steps and are **not** core colours.', '',
             '> **Print note:** CMYK values are uncalibrated approximations converted from sRGB without an ICC profile. Printed colour depends on process, substrate and profile — always proof physically against the HEX/RGB master. One CMYK value does not guarantee identical output across printers.', '',
             '| Group | Name | HEX | RGB | CMYK (approx.) | Usage |', '|---|---|---|---|---|---|']
    for grp, src in (('Core', B.CORE), ('Derived', B.DERIVED), ('Functional', B.FUNCTIONAL)):
        for v in src.values():
            r, g, b = B.hex_rgb(v['hex']); c = B.rgb_cmyk(v['hex'])
            lines.append(f'| {grp} | {v["name"]} | `{v["hex"]}` | {r} {g} {b} | {c[0]} {c[1]} {c[2]} {c[3]} | {v["desc"]} |')
    lines += ['', '## Data visualisation', '', f'Light surfaces: {", ".join(f"`{c}`" for c in B.DATAVIZ["light"])} · Dark surfaces: {", ".join(f"`{c}`" for c in B.DATAVIZ["dark"])}',
              '', 'Validated for lightness band, chroma floor, colour-vision-deficiency and normal-vision separation (adjacent pairs), and ≥ 3:1 contrast against #FFFFFF, #0E3D42 and #022329. Assign in fixed order; teal is always series 1.',
              '', '## Files', '', '- `tokens/wfs-tokens.css` · `tokens/_wfs-tokens.scss` · `tokens/wfs-tokens.json`', '- `swatches/WFS_Colors.ase` (Adobe apps) · `swatches/WFS_Colors.gpl` (GIMP / Inkscape / Krita) · `swatches/WFS_Core_Colors.svg`', '']
    w('color/README.md', '\n'.join(lines))
    rec('color/tokens/wfs-tokens.css · _wfs-tokens.scss · wfs-tokens.json', 'color', 'Design tokens (colour, roles, data palette, type, motion easing)', 'CSS, SCSS, JSON')
    rec('color/swatches/WFS_Colors.ase · WFS_Colors.gpl', 'color', 'Swatch libraries for Adobe apps and GIMP/Inkscape/Krita', 'ASE, GPL')
    rec('color/swatches/WFS_Core_Colors.svg', 'color', 'Core palette sheet with HEX / RGB / CMYK≈', 'SVG')

# =================================================================== typography
def typography():
    txt = f'''# WFS typography — v1.0

## Typefaces

| Script | Family | Source | Licence | Weights used |
|---|---|---|---|---|
| Latin | **Instrument Sans** | Google Fonts / Fontsource (`@fontsource/instrument-sans`) | SIL Open Font License 1.1 | Regular 400 · Medium 500 · SemiBold 600 · Bold 700 |
| Arabic | **Myriad Arabic** (مايرى) | Adobe (Adobe Fonts / licensed desktop files) | Adobe commercial licence | Regular · Semibold · Bold (PostScript `MyriadArabic-Regular`, `MyriadArabic-Semibold`, `MyriadArabic-Bold`) |

Font files are **referenced, not redistributed** in this repository. The build scripts read fonts from `$WFS_FONT_DIR` (default `~/.wfs-fonts`):

```
$WFS_FONT_DIR/InstrumentSans-{{Regular,Medium,SemiBold,Bold}}-latin.ttf   (and -latin-ext)
$WFS_FONT_DIR/MyriadArabic-*.otf|ttf                                     (licensed Adobe files)
```

### Arabic font status in this build

The identified approved Arabic typeface is **Myriad Arabic** (the name given as "مايرى"). The licensed font file was **not available** in the environment that produced version 1.0 of the package, and Adobe Fonts kit access was not entitled for this account. Therefore:

- No Arabic text was converted to outlines in any logo file; `WFS_Logo_Full_Bilingual` was **not generated** (no substitute font used).
- Arabic specimens in the guidelines PDF are rendered with a **clearly labelled proxy** (Noto Sans Arabic, OFL) and a visible note on the Arabic pages.
- To finalise: copy the Myriad Arabic font files into `$WFS_FONT_DIR`, then run `source/build_all.sh`. The bilingual lockup is produced and the guidelines switch to Myriad Arabic automatically.

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
'''
    w('typography/README.md', txt)
    rec('typography/README.md', 'typography', 'Typefaces, licences, hierarchy, financial numerals, Arabic status', 'Markdown')

# =================================================================== motion
def motion():
    blades = ''
    for j, b in enumerate(L.BLADES):
        blades += f'<g class="blade b{j+1}"><path fill="{B.ICON_COLOURWAYS["reverse"]["blades"][j]}" d="{L.ICON["blades"][b]["paths"]["solid"]}"/></g>'
    import math
    kf = ''
    for j in range(5):
        ang = 72 * j + 20; off = 380; rot = 90
        dx, dy = off * math.cos(math.radians(ang)), off * math.sin(math.radians(ang))
        kf += (f'.play .b{j+1}{{animation:conv{j+1} 760ms var(--ease-converge) {40*j}ms both}}'
               f'@keyframes conv{j+1}{{0%{{transform:translate({dx:.0f}px,{dy:.0f}px) rotate({rot}deg);opacity:0}}'
               f'70%{{opacity:1}}100%{{transform:none;opacity:1}}}}')
    wm = L.wordmark_paths('#F3F5F2', ids=False)
    html = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>WFS — Logo reveal (motion reference)</title>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;600&display=swap" rel="stylesheet">
<style>
:root{{--ease-standard:cubic-bezier(0.2,0,0,1);--ease-converge:cubic-bezier(0.65,0,0.35,1);--ease-lock:cubic-bezier(0.3,1.2,0.4,1)}}
html,body{{margin:0;height:100%;background:radial-gradient(90% 80% at 60% 35%,#0E3D42,#022329 70%);color:#F3F5F2;font-family:"Instrument Sans",system-ui,sans-serif}}
main{{display:grid;place-items:center;height:100%}}
svg{{width:min(86vw,900px);height:auto;overflow:visible}}
.blade{{transform-origin:0 0}}
.lock{{transform-origin:0 0}}
.play .lock{{animation:lock 340ms var(--ease-lock) 760ms both}}
@keyframes lock{{0%{{transform:scale(.965)}}100%{{transform:scale(1)}}}}
.wm{{opacity:0}}
.play .wm{{animation:wm 420ms var(--ease-standard) 780ms both}}
@keyframes wm{{0%{{opacity:0;transform:translateX(-40px)}}100%{{opacity:1;transform:none}}}}
{kf}
.loader{{position:fixed;left:24px;bottom:24px;display:flex;gap:12px;align-items:center;font-size:13px;color:#9DB5B3}}
.loader svg{{width:28px;height:28px;animation:spin 2.4s linear infinite}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
button{{position:fixed;right:24px;bottom:24px;background:#14B8A6;color:#022329;border:0;border-radius:10px;padding:12px 18px;font:600 14px "Instrument Sans",sans-serif;cursor:pointer}}
.spec{{position:fixed;left:24px;top:20px;font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:#7FE3D6}}
@media (prefers-reduced-motion: reduce){{
  .play .blade,.play .lock{{animation:none}}
  .play .wm{{animation:fade 400ms linear both}} .loader svg{{animation:none}}
  @keyframes fade{{from{{opacity:0}}to{{opacity:1}}}}
}}
</style></head><body>
<div class="spec">WFS motion · converge → align → lock → one view · 1 100 ms</div>
<main><svg id="stage" viewBox="-620 -620 3500 1240" aria-label="WFS logo reveal">
  <g class="lock">{blades}</g>
  <g class="wm"><g transform="translate(820 -230) scale(.46)">{wm}</g></g>
</svg></main>
<div class="loader"><svg viewBox="-520 -520 1040 1040">{L.icon_mono('#14B8A6', 'gap32')}</svg>Loading · ring rotation 360° / 2.4 s</div>
<button onclick="replay()">Replay</button>
<script>
function replay(){{const s=document.getElementById('stage');s.classList.remove('play');void s.getBoundingClientRect();s.classList.add('play');}}
window.addEventListener('load',()=>setTimeout(replay,250));
</script>
</body></html>
'''
    w('motion/WFS_Logo_Reveal.html', html)
    w('motion/README.md', '''# WFS motion — v1.0

`WFS_Logo_Reveal.html` is a dependency-free reference prototype (inline SVG + CSS keyframes). Open it in any modern browser.

| Token | Value | Use |
|---|---|---|
| `--wfs-ease-standard` | `cubic-bezier(0.2, 0, 0, 1)` | UI transitions, panels, charts |
| `--wfs-ease-converge` | `cubic-bezier(0.65, 0, 0.35, 1)` | Logo formation, field convergence |
| `--wfs-ease-lock` | `cubic-bezier(0.3, 1.2, 0.4, 1)` (≤ 4 % overshoot) | The lock moment only |
| Durations | 120 · 200 · 320 ms (UI) · 1 100 ms (logo reveal) | Never exceed 1.4 s |

Sequence: **Fields** (0 ms) → **Converge** (0–760 ms, blades travel inward and unwind 90°, 40 ms stagger) → **Lock** (760–1 100 ms, 0.965 → 1.0 settle) → **One view** (wordmark enters 780–1 200 ms).
Loading state: the one-colour icon rotates 360° every 2.4 s, linear. `prefers-reduced-motion`: cross-fade only.
''')
    rec('motion/WFS_Logo_Reveal.html', 'motion', 'Logo reveal + loading reference prototype (SVG/CSS, no dependencies)', 'HTML')

# =================================================================== templates
def templates():
    sys.path.insert(0, os.path.join(ROOT, 'guidelines', 'source'))
    import gl_components as C
    head = ('<meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">'
            '<style>:root{--en:"Instrument Sans",system-ui,sans-serif;--ar:"Myriad Arabic",sans-serif}*{box-sizing:border-box;margin:0;padding:0}'
            'body{font-family:var(--en);background:#555}.tn{font-variant-numeric:tabular-nums lining-nums}.page{break-after:page;overflow:hidden}</style>')
    items = [
        ('presentation', 'WFS_Presentation_Template', '1920px', '1080px', [C.slide(), C.slide_content()], 'Presentation (16:9): title + content slide'),
        ('report', 'WFS_Report_Template', '210mm', '297mm', [C.report_cover(), C.report_page()], 'A4 report: cover + statement page with header/footer'),
        ('social', 'WFS_Social_Launch_1080', '1080px', '1080px', [C.social()], 'Social / launch post 1:1'),
        ('social', 'WFS_Social_Announcement_1200x1500', '1200px', '1500px', [C.announcement()], 'Product announcement 4:5'),
        ('social', 'WFS_Social_Cover_1584x396', '1584px', '396px', [C.banner()], 'LinkedIn / social cover 4:1'),
    ]
    render = os.path.join(ROOT, 'source', 'render.mjs')
    for folder, name, wd, ht, pages, purpose in items:
        scale = ''
        if wd.endswith('mm'):   # A4 designs are 794 x 1123 px -> exact A4 at 96 dpi
            body = ''.join(f'<section class="page" style="width:210mm;height:297mm"><div style="transform:scale(1.0);transform-origin:0 0">{p}</div></section>' for p in pages)
        else:
            body = ''.join(f'<section class="page" style="width:{wd};height:{ht}">{p}</section>' for p in pages)
        html = f'<!doctype html><html lang="en"><head>{head}<title>{name}</title><style>@page{{size:{wd} {ht};margin:0}}</style></head><body>{body}</body></html>\n'
        p = w(f'templates/{folder}/{name}.html', html)
        # render from a temporary copy that uses the local font files (headless Chromium has no web-font network access)
        fd = B.font_dir()
        local = ''.join(f"@font-face{{font-family:'Instrument Sans';font-weight:{wt};src:url('file://{fd}/InstrumentSans-{n}-latin.ttf')}}"
                        for wt, n in ((400, 'Regular'), (500, 'Medium'), (600, 'SemiBold'), (700, 'Bold')))
        tmp = p[:-5] + '.render.html'
        open(tmp, 'w').write(html.replace('<style>', f'<style>{local}', 1))
        r = subprocess.run(['node', render, tmp, p[:-5] + '.pdf', '--png', os.path.join(ROOT, 'templates', folder, '_pages'), '--width', wd, '--height', ht, '--scale', '1'],
                           capture_output=True, text=True, cwd=os.path.join(ROOT, 'source'))
        if r.returncode: print(r.stderr[-800:])
        os.remove(tmp)
        pdir = os.path.join(ROOT, 'templates', folder, '_pages')
        for i, f in enumerate(sorted(os.listdir(pdir))):
            os.replace(os.path.join(pdir, f), os.path.join(ROOT, 'templates', folder, f'{name}_preview_{i+1}.png'))
        os.rmdir(pdir)
        rec(f'templates/{folder}/{name}.html (+ .pdf, preview PNG)', 'templates', purpose, 'HTML, PDF, PNG')
    # email signature (table layout, absolute image URL placeholder)
    sig = '''<!-- WFS email signature. Host WFS_Logo_Horizontal_Primary_1024px.png and replace LOGO_URL. Text stays live for accessibility. -->
<table cellpadding="0" cellspacing="0" border="0" style="font-family:'Instrument Sans',Arial,Helvetica,sans-serif;color:#022329;font-size:13px;line-height:1.45">
  <tr><td style="padding:0 0 10px 0"><strong style="font-size:15px">Full Name</strong><br><span style="color:#0F7C74">Job Title</span></td></tr>
  <tr><td style="padding:0 0 12px 0;color:#4A5E61">name@company.example · +000 0000 0000</td></tr>
  <tr><td style="border-top:1px solid #D6DEDB;padding-top:12px"><img src="LOGO_URL" alt="WFS — Wusool Financial System" width="132" style="display:block;border:0"></td></tr>
  <tr><td style="padding-top:8px;font-size:10px;letter-spacing:1.2px;color:#80918F">A WUSOOL TECH PRODUCT</td></tr>
</table>
'''
    w('templates/email-signature/WFS_Email_Signature.html', sig)
    rec('templates/email-signature/WFS_Email_Signature.html', 'templates', 'Email signature (table layout, live text)', 'HTML')
    w('templates/README.md', '''# WFS templates — v1.0

HTML templates built from the brand components; each has a rendered PDF and PNG previews.
Edit text directly in the HTML (fonts load from Google Fonts; Arabic from your Adobe Fonts kit), then print to PDF from Chromium or re-render with `node ../source/render.mjs <file.html> <out.pdf> --width … --height …`.

| Folder | Template | Format |
|---|---|---|
| presentation | WFS_Presentation_Template | 1920 × 1080 (16:9), title + content |
| report | WFS_Report_Template | A4 portrait, cover + statement page |
| social | WFS_Social_Launch_1080 · WFS_Social_Announcement_1200x1500 · WFS_Social_Cover_1584x396 | 1:1 · 4:5 · 4:1 |
| email-signature | WFS_Email_Signature | HTML table |

The sample figures, names ("Northwind Group", "Leila Haddad") and addresses (`*.example`) are fictional placeholders.
''')

# =================================================================== AI format
def ai_docs():
    txt = '''# Adobe Illustrator (.ai) files

**No `.ai` files are shipped in this version, deliberately.**

A genuine native `.ai` file can only be written by Adobe Illustrator. Illustrator was not available in the environment that produced WFS Brand Identity 1.0, and no legitimate open-source tool writes native AI files. Renaming an SVG or PDF to `.ai` would be a fake file, so it was not done.

What is provided instead:

- **SVG masters** (`../svg/`) — clean, outlined, fully editable vector paths; open directly in Illustrator.
- **Vector PDFs** (`../pdf/`) — open in Illustrator as editable paths (no embedded rasters).

## Create native .ai files (one step, requires Illustrator)

1. Open Adobe Illustrator.
2. `File → Scripts → Other Script…` and choose `brand/source/illustrator/export_ai.jsx`.
3. Select the `brand` folder when prompted. The script opens every SVG master in `logo/svg`, `icon/svg` and `wordmark/svg` and saves a native, PDF-compatible `.ai` next to it in the matching `ai/` folder.
'''
    for g in ('logo', 'wordmark', 'icon'):
        w(f'{g}/ai/README.md', txt)
    jsx = r'''// WFS Brand Identity 1.0 — batch-convert SVG masters to native Adobe Illustrator (.ai)
// Run from Illustrator: File > Scripts > Other Script... ; select the /brand folder when asked.
#target illustrator
(function () {
    var root = Folder.selectDialog('Select the WFS /brand folder');
    if (!root) return;
    var groups = ['logo', 'icon', 'wordmark'];
    var done = 0, failed = [];
    app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;
    for (var g = 0; g < groups.length; g++) {
        var src = new Folder(root.fsName + '/' + groups[g] + '/svg');
        var dst = new Folder(root.fsName + '/' + groups[g] + '/ai');
        if (!src.exists) continue;
        if (!dst.exists) dst.create();
        var files = src.getFiles('*.svg');
        for (var i = 0; i < files.length; i++) {
            try {
                var doc = app.open(files[i]);
                var opts = new IllustratorSaveOptions();
                opts.compatibility = Compatibility.ILLUSTRATOR17;   // CC; PDF-compatible
                opts.pdfCompatible = true;
                opts.embedICCProfile = false;
                opts.compressed = true;
                var name = files[i].name.replace(/\.svg$/i, '.ai');
                doc.saveAs(new File(dst.fsName + '/' + name), opts);
                doc.close(SaveOptions.DONOTSAVECHANGES);
                done++;
            } catch (e) { failed.push(files[i].name + ': ' + e); }
        }
    }
    app.userInteractionLevel = UserInteractionLevel.DISPLAYALERTS;
    alert('WFS: saved ' + done + ' native .ai files.' + (failed.length ? '\nFailed:\n' + failed.join('\n') : ''));
})();
'''
    w('source/illustrator/export_ai.jsx', jsx)
    rec('logo|icon|wordmark/ai/README.md + source/illustrator/export_ai.jsx', 'ai', 'Explains AI status; Illustrator script to create genuine .ai from the SVG masters', 'Markdown, JSX')

# =================================================================== logo preview sheet
def preview_sheet():
    import glob
    rows = [('WFS_Logo_Horizontal_Primary', '#F3F5F2'), ('WFS_Logo_Horizontal_Inverse', '#022329'), ('WFS_Logo_Horizontal_Premium', '#022329'),
            ('WFS_Logo_Horizontal_Premium_Light', '#FFFFFF'), ('WFS_Logo_Full_English', '#FFFFFF'), ('WFS_Logo_Full_English_Inverse', '#0E3D42'),
            ('WFS_Logo_Horizontal_Dark', '#FFFFFF'), ('WFS_Logo_Horizontal_White', '#000000'), ('WFS_Logo_Horizontal_Black', '#FFFFFF'),
            ('WFS_Logo_Horizontal_Monochrome', '#FFFFFF'), ('WFS_Logo_Horizontal_Monochrome_Light', '#111111'), ('WFS_Logo_Stacked_Primary', '#F3F5F2'),
            ('WFS_Logo_Stacked_Inverse', '#022329'), ('WFS_Logo_Endorsed_Primary', '#FFFFFF'), ('WFS_Logo_Endorsed_Inverse', '#022329')]
    tw, th = 900, 420
    sheet = Image.new('RGB', (tw * 3, th * 5), 'white')
    for k, (n, bg) in enumerate(rows):
        im = Image.open(os.path.join(ROOT, 'logo', 'png', f'{n}_1024px.png')).convert('RGBA')
        s = min((tw - 180) / im.width, (th - 150) / im.height); im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
        tile = Image.new('RGBA', (tw, th), bg); tile.alpha_composite(im, ((tw - im.width) // 2, (th - im.height) // 2))
        sheet.paste(tile.convert('RGB'), ((k % 3) * tw, (k // 3) * th))
    os.makedirs(os.path.join(ROOT, 'logo', 'preview'), exist_ok=True)
    sheet.save(os.path.join(ROOT, 'logo', 'preview', 'WFS_Logo_Matrix_Preview.png'), optimize=True)
    icons = ['Primary', 'Inverse', 'Flat_Teal', 'Dark', 'White', 'Black', 'Monochrome', 'Monochrome_Light', 'Premium', 'Premium_Light']
    bgs = ['#F3F5F2', '#022329', '#022329', '#FFFFFF', '#0E3D42', '#FFFFFF', '#FFFFFF', '#111111', '#022329', '#FFFFFF']
    sheet = Image.new('RGB', (400 * 5, 400 * 2), 'white')
    for k, (n, bg) in enumerate(zip(icons, bgs)):
        im = Image.open(os.path.join(ROOT, 'icon', 'png', f'WFS_Icon_{n}_512px.png')).convert('RGBA').resize((280, 280), Image.LANCZOS)
        tile = Image.new('RGBA', (400, 400), bg); tile.alpha_composite(im, (60, 60)); sheet.paste(tile.convert('RGB'), ((k % 5) * 400, (k // 5) * 400))
    sheet.save(os.path.join(ROOT, 'logo', 'preview', 'WFS_Icon_Matrix_Preview.png'), optimize=True)
    rec('logo/preview/WFS_Logo_Matrix_Preview.png · WFS_Icon_Matrix_Preview.png', 'logo/preview', 'Contact sheets: every lockup / icon on its intended ground (preview, not for reproduction)', 'PNG (opaque)')

if __name__ == '__main__':
    colour(); typography(); motion(); templates(); ai_docs(); preview_sheet()
    json.dump(REC, open(os.path.join(ROOT, 'source', 'master', 'asset_records_extras.json'), 'w'), indent=1)
    print(len(REC), 'extra records')
