"""Build the WFS Brand Guidelines (A4 landscape) as HTML, then render to PDF with Chromium.

usage:  WFS_FONT_DIR=/path/to/fonts python3 build_guidelines.py
Fonts are referenced from WFS_FONT_DIR (not redistributed). If the approved Arabic
typeface (Myriad Arabic) is not present, Arabic specimens are rendered with a clearly
labelled proxy and the report says so."""
import os, sys, glob, re, json, math, subprocess, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'source'))
import brand_config as B
import logo_lib as L
import gl_components as C
import gl_ui as U
from gl_components import A, icon, mock

FONT_DIR = B.font_dir()
AR_FILES = sorted(p for p in glob.glob(os.path.join(FONT_DIR, '**', '*'), recursive=True)
                  if re.search(r'myriad.?arabic', os.path.basename(p), re.I) and p.lower().endswith(('.otf', '.ttf', '.woff', '.woff2')))
AR_NATIVE = bool(AR_FILES)

# ---------------------------------------------------------------- fonts
def font_faces():
    link = os.path.join(HERE, 'fonts')
    if os.path.islink(link) or os.path.exists(link):
        if os.path.islink(link): os.unlink(link)
    os.symlink(FONT_DIR, link)
    ff = []
    for w, n in ((400, 'Regular'), (500, 'Medium'), (600, 'SemiBold'), (700, 'Bold')):
        for sub, rng in (('latin', 'U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+2000-206F,U+2074,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD'),
                         ('latin-ext', 'U+0100-02AF,U+0304,U+0308,U+0329,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF')):
            ff.append(f"@font-face{{font-family:'Instrument Sans';font-weight:{w};src:url('fonts/InstrumentSans-{n}-{sub}.ttf');unicode-range:{rng}}}")
    for w, n in ((400, 'Regular'), (500, 'Medium')):
        ff.append(f"@font-face{{font-family:'IBM Plex Mono';font-weight:{w};src:url('fonts/IBMPlexMono-{n}-latin.ttf')}}")
    if AR_NATIVE:
        for p in AR_FILES:
            b = os.path.basename(p).lower()
            w = 700 if 'bold' in b else 600 if 'semi' in b else 300 if 'light' in b else 400
            rel = os.path.relpath(p, FONT_DIR)
            ff.append(f"@font-face{{font-family:'Myriad Arabic';font-weight:{w};src:url('fonts/{rel}')}}")
    else:
        for w, n in ((400, 'Regular'), (500, 'Medium'), (600, 'SemiBold'), (700, 'Bold')):
            ff.append(f"@font-face{{font-family:'WFS Arabic Proxy';font-weight:{w};src:url('fonts/proxy/NotoSansArabic-{n}.ttf')}}")
    return '\n'.join(ff)

AR_STACK = "'Myriad Arabic', 'MyriadArabic-Regular'" + ("" if AR_NATIVE else ", 'WFS Arabic Proxy'") + ", 'Instrument Sans'"
PROXY_NOTE = ('' if AR_NATIVE else
              '<div class="proxy">Arabic specimens in this edition are rendered with a labelled proxy (Noto Sans Arabic) because the licensed '
              'Myriad Arabic font file was not available in the build environment. Place the Myriad Arabic files in the font directory and rebuild — '
              'the layout switches automatically. The approved Arabic typeface remains Myriad Arabic.</div>')

CSS = r'''
@page { size: 297mm 210mm; margin: 0 }
:root { --en: 'Instrument Sans', system-ui, sans-serif; --ar: %AR%; --dark:#022329; --deep:#0E3D42; --teal:#14B8A6; --mint:#7FE3D6; --off:#F3F5F2;
        --t700:#0F7C74; --t800:#115E5F; --s600:#4A5E61; --s400:#80918F; --line:#D6DEDB; --mist:#9DB5B3; --ldark:#1E4A4F }
* { box-sizing: border-box; margin: 0; padding: 0 }
code, pre { font-family: "IBM Plex Mono", monospace }
html, body { background: #555 }
body { font-family: var(--en); -webkit-font-smoothing: antialiased; font-kerning: normal }
.page { width: 297mm; height: 210mm; position: relative; overflow: hidden; background: var(--off); color: var(--dark); break-after: page; page-break-after: always }
.page.dark { background: var(--dark); color: var(--off) }
.page.deep { background: linear-gradient(160deg, var(--deep), var(--dark)); color: var(--off) }
.page.white { background: #fff }
.rh { position: absolute; top: 8.5mm; left: 14mm; right: 14mm; display: flex; justify-content: space-between; font-size: 6.2pt; letter-spacing: .14em; text-transform: uppercase; color: var(--s400); z-index: 5 }
.rf { position: absolute; bottom: 8mm; left: 14mm; right: 14mm; display: flex; gap: 4mm; align-items: baseline; font-size: 6.4pt; color: var(--s400); z-index: 5 }
.rf .n { font-weight: 600; color: var(--t700); font-variant-numeric: tabular-nums; font-size: 7.4pt; letter-spacing: .02em }
.dark .rf .n, .deep .rf .n { color: var(--mint) }
.rf .sp { flex: 1 }
.dark .rh, .deep .rh, .dark .rf, .deep .rf { color: #5F7C7A }
.c { position: absolute; top: 19mm; left: 14mm; right: 14mm; bottom: 17mm }
.eb { font-size: 6.8pt; letter-spacing: .16em; text-transform: uppercase; font-weight: 600; color: var(--t700) }
.dark .eb, .deep .eb { color: var(--mint) }
h1 { font-size: 27pt; line-height: 1.02; letter-spacing: -.028em; font-weight: 600; margin-top: 2.5mm }
h1.xl { font-size: 44pt; letter-spacing: -.035em }
h2 { font-size: 13pt; line-height: 1.15; letter-spacing: -.012em; font-weight: 600 }
h3 { font-size: 8.4pt; font-weight: 600; letter-spacing: .01em }
p, li { font-size: 8.3pt; line-height: 1.55; color: var(--s600) }
.dark p, .deep p, .dark li, .deep li { color: var(--mist) }
p.lead { font-size: 11pt; line-height: 1.45; color: var(--dark); letter-spacing: -.005em }
.dark p.lead, .deep p.lead { color: var(--off) }
.cap { font-size: 6.4pt; line-height: 1.45; color: var(--s400) }
.dark .cap, .deep .cap { color: #6F8987 }
.tn { font-variant-numeric: tabular-nums lining-nums; font-feature-settings: "tnum" 1, "lnum" 1 }
.ar { font-family: var(--ar); direction: rtl }
.row { display: flex; gap: 5mm }
.col { display: flex; flex-direction: column }
.g12 { display: grid; grid-template-columns: repeat(12, 1fr); column-gap: 5mm }
.panel { background: #fff; border-radius: 2.5mm }
.dark .panel, .deep .panel { background: var(--deep) }
.rule { height: 0; border-top: .25mm solid var(--line) }
.dark .rule, .deep .rule { border-color: var(--ldark) }
.mock { overflow: hidden; position: relative; flex: none }
.tag { display: inline-block; font-size: 5.8pt; letter-spacing: .12em; text-transform: uppercase; font-weight: 600; padding: .8mm 1.8mm; border-radius: 1mm; background: #DDF5F1; color: var(--t700) }
.dark .tag, .deep .tag { background: var(--deep); color: var(--mint) }
.proxy { margin-top: 3mm; padding: 2.4mm 3mm; border-radius: 1.6mm; border: .25mm dashed #C8691E; color: #8A4A12; font-size: 6.4pt; line-height: 1.45; background: #FFF8F0 }
ul.clean { list-style: none } ul.clean li { padding: 1.2mm 0; border-top: .2mm solid var(--line) }
.dark ul.clean li, .deep ul.clean li { border-color: var(--ldark) }
table.spec { border-collapse: collapse; width: 100% } table.spec td, table.spec th { font-size: 7pt; padding: 1.5mm 3mm 1.5mm 0; text-align: left; border-top: .2mm solid var(--line); vertical-align: top }
table.spec th { font-size: 6pt; letter-spacing: .12em; text-transform: uppercase; color: var(--s400); font-weight: 600; border-top: none }
.dark table.spec td, .deep table.spec td { border-color: var(--ldark); color: var(--mist) }
.sw { border-radius: 2mm; position: relative; overflow: hidden }
.x { position: absolute; inset: 0 }
.no { position: relative } .no:after { content: ''; position: absolute; right: 2mm; top: 2mm; width: 4.2mm; height: 4.2mm; border-radius: 50%;
  background: #B4232F url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='3' stroke-linecap='round'><path d='M7 7l10 10M17 7L7 17'/></svg>") center/60% no-repeat }
.yes { position: relative } .yes:after { content: ''; position: absolute; right: 2mm; top: 2mm; width: 4.2mm; height: 4.2mm; border-radius: 50%;
  background: #0F7C74 url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'><path d='M6 12.5l4 4 8-9'/></svg>") center/60% no-repeat }
'''.replace('%AR%', AR_STACK)

PAGES = []
TOC = []
def page(chapter, title, body, theme='', toc=None, chrome=True):
    n = len(PAGES) + 1
    if toc: TOC.append((n, chapter, toc))
    rh = rf = ''
    if chrome:
        rh = f'<div class="rh"><span>WFS — Brand Identity · Version {B.VERSION} · {B.YEAR}</span><span>{chapter}</span></div>'
        rf = f'<div class="rf"><span class="n">{n:02d}</span><span>{title}</span><span class="sp"></span><span>Wusool Financial System · <span class="ar" style="direction:rtl;unicode-bidi:isolate">نظام وصول المالي</span></span></div>'
    PAGES.append(f'<section class="page {theme}">{rh}{body}{rf}</section>')

def img(path, style=''): return f'<img src="{A}/{path}" style="{style}" alt="">'
def mm(px): return px / 3.7795275591

P = B.ICON_COLOURWAYS
AP_W, AP_H, _ = L.aperture_width()      # aperture width in icon units (D = 1000)
AP = AP_W / 1000                          # clear-space unit as fraction of icon diameter

# ================================================================= 01 COVER
page('Cover', 'Cover', f'''
<img src="{A}/graphic-system/fields/WFS_Overlay_Convergence_OnDark.svg" style="position:absolute;left:95mm;top:-62mm;width:360mm;opacity:1">
<div style="position:absolute;left:176mm;top:30mm;width:150mm;height:150mm;border-radius:50%;background:radial-gradient(closest-side,rgba(20,184,166,.28),rgba(20,184,166,0))"></div>
<img src="{A}/icon/svg/WFS_Icon_Premium.svg" style="position:absolute;left:196mm;top:48mm;width:112mm">
<div style="position:absolute;left:18mm;top:18mm">{img("logo/svg/WFS_Logo_Horizontal_Premium.svg", "height:15mm")}</div>
<div style="position:absolute;left:18mm;bottom:40mm;width:165mm">
  <div class="eb">Brand Identity System · Guidelines</div>
  <h1 class="xl" style="margin-top:5mm">One financial view across every entity and operation.</h1>
</div>
<div style="position:absolute;left:18mm;right:18mm;bottom:14mm;display:flex;justify-content:space-between;font-size:6.8pt;color:#6F8987;letter-spacing:.08em">
  <span>WFS — Wusool Financial System</span><span class="ar" style="font-size:9pt;letter-spacing:0">نظام وصول المالي</span><span>Version {B.VERSION} · {B.YEAR}</span><span>A WUSOOL Tech Product</span></div>
''', 'deep', chrome=False)

# ================================================================= 02 OVERVIEW + CONTENTS (contents filled later)
CONTENTS_SLOT = len(PAGES)
page('Introduction', 'Brand overview & contents', '%CONTENTS%', '', toc='Brand overview & contents')

# ================================================================= 03 POSITIONING
mods = ['Accounting', 'Treasury', 'Expenses', 'Receivables', 'Payables', 'Payroll', 'Approvals', 'Cash', 'Banks', 'PDC / Cheques',
        'Deals', 'Commissions', 'Documents', 'Reporting', 'Analytics', 'External data', 'Integrations']
nodes = ''
for i, m_ in enumerate(mods):
    a = -math.pi / 2 + 2 * math.pi * i / len(mods)
    x, y = 150 + 118 * math.cos(a), 150 + 118 * math.sin(a)
    anchor = 'start' if math.cos(a) > 0.2 else 'end' if math.cos(a) < -0.2 else 'middle'
    tx, ty = 150 + 134 * math.cos(a), 150 + 134 * math.sin(a) + 3
    nodes += (f'<path d="M{x:.1f},{y:.1f} Q{150 + 60 * math.cos(a + .5):.1f},{150 + 60 * math.sin(a + .5):.1f} {150 + 44 * math.cos(a + .9):.1f},{150 + 44 * math.sin(a + .9):.1f}" fill="none" stroke="#14B8A6" stroke-opacity=".45" stroke-width=".8"/>'
              f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.6" fill="#022329"/><text x="{tx:.1f}" y="{ty:.1f}" text-anchor="{anchor}" font-size="7.4" fill="#4A5E61" font-family="Instrument Sans">{m_}</text>')
page('01 · Brand', 'Product positioning', f'''
<div class="c g12">
  <div style="grid-column:1/6">
    <div class="eb">Category</div><h1>Global financial<br>operating system</h1>
    <p class="lead" style="margin-top:6mm">WFS connects every financial operation of a modern organisation inside one structured environment — so leadership sees one truth and teams execute under control.</p>
    <div class="row" style="margin-top:8mm;gap:6mm">
      <div style="flex:1"><h3>WFS is</h3><ul class="clean" style="margin-top:2mm"><li>A financial operating system</li><li>Multi-entity, multi-currency by design</li><li>One record, one workflow, many interfaces</li><li>Controlled execution with approvals</li><li>Powerful alone, connected when needed</li></ul></div>
      <div style="flex:1"><h3>WFS is not</h3><ul class="clean" style="margin-top:2mm"><li>Bookkeeping or accounting software only</li><li>A local-market ERP</li><li>A bank, wallet or payments app</li><li>An investment or trading platform</li><li>A regional or single-currency product</li></ul></div>
    </div>
  </div>
  <div style="grid-column:7/13;display:flex;align-items:center;justify-content:center">
    <svg viewBox="-20 -5 340 310" style="width:150mm">
      <circle cx="150" cy="150" r="118" fill="none" stroke="#D6DEDB" stroke-width=".6"/>{nodes}
      <g transform="translate(150 150) scale(.052)">{L.icon_paths(P["primary"]["blades"], ids=False)}</g>
    </svg>
  </div>
</div>''', toc='Product positioning')

# ================================================================= 04 BRAND IDEA
def fields_diagram():
    st = []
    labels = ['Multiple fields', 'Converge', 'Align', 'Lock', 'One financial view']
    for k in range(5):
        cx = 60 + k * 118
        t = k / 4
        g = ''
        for j, b in enumerate(L.BLADES):
            ang = 72 * j + 20
            off = (1 - t) ** 1.4 * 300
            rot = (1 - t) * 60 * (1 if j % 2 else -1)
            dx, dy = off * math.cos(math.radians(ang)), off * math.sin(math.radians(ang))
            col = P['reverse']['blades'][j]
            g += f'<path transform="translate({dx:.1f} {dy:.1f}) rotate({rot:.1f})" d="{L.ICON["blades"][b]["paths"]["solid"]}" fill="{col}" fill-opacity="{0.55 + 0.45 * t:.2f}"/>'
        st.append(f'<g transform="translate({cx} 70) scale(.075)">{g}</g><text x="{cx}" y="150" text-anchor="middle" font-size="7" fill="#9DB5B3" font-family="Instrument Sans" letter-spacing=".6">{labels[k].upper()}</text>')
        if k < 4: st.append(f'<path d="M{cx + 44} 70 h26" stroke="#7FE3D6" stroke-width=".8" stroke-opacity=".6" marker-end="url(#ar)"/>')
    return (f'<svg viewBox="0 0 600 160" style="width:100%"><defs><marker id="ar" viewBox="0 0 6 6" refX="5" refY="3" markerWidth="6" markerHeight="6" orient="auto">'
            f'<path d="M0,0 L6,3 L0,6" fill="none" stroke="#7FE3D6" stroke-width="1"/></marker></defs>{"".join(st)}</svg>')
page('01 · Brand', 'Brand idea — Unified Financial Field', f'''
<img src="{A}/graphic-system/fields/WFS_Overlay_Unified_Field_OnDark.svg" style="position:absolute;left:120mm;top:-70mm;width:260mm;opacity:.7">
<div class="c">
  <div class="eb">Brand idea · Concept C</div><h1 style="width:160mm">The Unified Financial Field</h1>
  <p class="lead" style="width:150mm;margin-top:5mm">Entities, accounts, currencies, operations and data sources are separate fields of motion. WFS brings them into one controlled field — a single, precise view.</p>
  <div style="margin-top:12mm">{fields_diagram()}</div>
  <div class="row" style="margin-top:6mm;gap:6mm">
    {''.join(f'<div style="flex:1;border-top:.3mm solid #1E4A4F;padding-top:2.5mm"><h3 style="color:#7FE3D6">{a}</h3><p style="margin-top:1mm">{b}</p></div>' for a, b in (
      ('Unity', 'Five blades, one ring. Every part belongs to the whole.'), ('Convergence', 'All blade edges resolve into one aperture — one point of view.'),
      ('Control', 'Built only from circles: measured, repeatable, precise.'), ('Scale', 'The same geometry works at 16 px and on a 20 m event screen.'),
      ('Continuity', 'A closed, rotating system: always operating, never finished.')))}
  </div>
</div>''', 'dark', toc='Brand idea')

# ================================================================= 05 PERSONALITY
pers = [('Control', 'التحكم', 'Every action accountable, every number traceable. Calm authority, never restriction.'),
        ('Clarity', 'الوضوح', 'Complex structures made legible. We remove noise before we add anything.'),
        ('Flow', 'التدفق', 'Operations move without friction across entities, currencies and teams.'),
        ('Intelligence', 'الذكاء', 'Insight that is earned from structured data — never decorative, never hype.')]
def _motif(kind):
    st = 'fill="none" stroke="#14B8A6" stroke-width="1.2"'
    if kind == 0:   # control: grid + locked node
        g = ''.join(f'<line x1="{x}" y1="10" x2="{x}" y2="90" stroke="#D6DEDB"/>' for x in range(10, 91, 20)) + ''.join(f'<line x1="10" y1="{y}" x2="90" y2="{y}" stroke="#D6DEDB"/>' for y in range(10, 91, 20))
        return f'<svg viewBox="0 0 100 100" style="width:30mm">{g}<rect x="30" y="30" width="40" height="40" {st}/><circle cx="50" cy="50" r="4" fill="#022329"/></svg>'
    if kind == 1:   # clarity: the aperture
        return f'<svg viewBox="-60 -60 120 120" style="width:30mm"><circle r="50" stroke="#D6DEDB" fill="none"/><circle r="21" {st}/><circle r="3" fill="#022329"/></svg>'
    if kind == 2:   # flow: blade edges
        return f'<svg viewBox="-560 -560 1120 1120" style="width:30mm"><g fill="none" stroke="#14B8A6" stroke-width="16">' + ''.join(f'<path d="{e["d"]}"/>' for e in L.ICON['edges'].values()) + '</g></svg>'
    return (f'<svg viewBox="-60 -60 120 120" style="width:30mm"><g fill="none" stroke="#D6DEDB">' + ''.join(f'<circle r="{r}"/>' for r in (18, 34, 50)) + '</g>'
            + ''.join(f'<circle cx="{r*math.cos(math.radians(a)):.1f}" cy="{r*math.sin(math.radians(a)):.1f}" r="3" fill="{c}"/>' for r, a, c in ((18, -40, '#14B8A6'), (34, 60, '#022329'), (50, 170, '#14B8A6'), (34, 200, '#7FE3D6'), (50, -90, '#022329'))) + '</svg>')
MOTIFS = [_motif(i) for i in range(4)]
attrs = ['Global', 'Premium', 'Enterprise', 'Intelligent', 'Controlled', 'Scalable', 'Modern', 'Precise']
page('01 · Brand', 'Brand personality', f'''
<div class="c">
  <div class="eb">Brand personality</div><h1>Control · Clarity · Flow · Intelligence</h1>
  <div class="row" style="margin-top:9mm;gap:5mm">
  {''.join(f'<div class="panel" style="flex:1;padding:6mm 5mm;height:104mm;display:flex;flex-direction:column"><div class="tn" style="font-size:7pt;color:#0F7C74;font-weight:600">0{i+1}</div><h2 style="font-size:17pt;margin-top:3mm">{a}</h2><div class="ar" style="font-size:12pt;color:#0F7C74;margin-top:1.5mm;text-align:left">{b}</div><div style="flex:1;display:flex;align-items:center;justify-content:center">{MOTIFS[i]}</div><p>{c}</p></div>' for i, (a, b, c) in enumerate(pers))}
  </div>
  <div style="margin-top:7mm;display:flex;gap:2.5mm;flex-wrap:wrap">{''.join(f'<span style="font-size:8pt;padding:1.6mm 3.4mm;border-radius:10mm;border:.25mm solid #D6DEDB">{a}</span>' for a in attrs)}
  <span style="font-size:8pt;padding:1.6mm 3.4mm;color:#80918F">— and never: loud, playful, speculative, regional, generic.</span></div>
</div>''', toc='Brand personality')

# ================================================================= 06 LOGO CONCEPT
IP = L.ICON['parameters']
def step_svg(k):
    R_, r_, rho = IP['R'], IP['r'], IP['rho']
    e0 = L.ICON['circles'][2]
    g = f'<circle r="{R_}" fill="none" stroke="#9DB5B3" stroke-width="16"/><circle r="{r_}" fill="none" stroke="#9DB5B3" stroke-width="16"/>'
    if k >= 1:
        g += f'<circle cx="{e0["centre"][0]}" cy="{e0["centre"][1]}" r="{rho}" fill="none" stroke="#14B8A6" stroke-width="14" stroke-dasharray="40 26"/>'
        e = list(L.ICON['edges'].values())[0]
        g += f'<path d="{e["d"]}" fill="none" stroke="#022329" stroke-width="30" stroke-linecap="round"/><circle cx="{e["p0"][0]}" cy="{e["p0"][1]}" r="34" fill="#14B8A6"/>'
    if k >= 2:
        g += ''.join(f'<path d="{e["d"]}" fill="none" stroke="#022329" stroke-width="30" stroke-linecap="round"/>' for e in L.ICON['edges'].values())
    if k >= 3:
        g = L.icon_paths(P['primary']['blades'], ids=False)
    vb = '-1300 -1300 2600 2600' if k == 1 else '-620 -620 1240 1240'
    return f'<svg viewBox="{vb}" style="width:100%;aspect-ratio:1">{g}</svg>'
steps = [('Field', 'Two concentric circles: the outer field (R 500) and the aperture (r 190).'),
         ('Edge', 'One circle (ρ 520) tangent to the aperture: the edge leaves the opening without a kink.'),
         ('Rotate', 'The edge repeats five times at exactly 72° — five entities, one system.'),
         ('Unify', 'Five blades, a tonal ramp from Mint to WFS Dark: many fields, one view.')]
page('02 · Logo', 'Logo concept — designed from first principles', f'''
<div class="c g12">
  <div style="grid-column:1/5">
    <div class="eb">Logo concept · v2</div><h1>Five fields,<br>one aperture</h1>
    <p style="margin-top:5mm">The WFS icon is an original, parametric aperture. It keeps the approved idea — separate financial fields converging into one controlled view — and rebuilds it with perfect geometry: exact five-fold symmetry and nothing but circular arcs.</p>
    <ul class="clean" style="margin-top:5mm">
      <li><b>Precision</b> — every curve is an arc of one of seven circles; every tip is a true tangent.</li>
      <li><b>Balance</b> — rotational symmetry means the mark is equally weighted at every size.</li>
      <li><b>Depth</b> — the premium version adds light and soft contact shadows, built from gradients only.</li>
    </ul>
    <div style="margin-top:5mm;display:flex;align-items:center;gap:3mm"><img src="{A}/source/reference/approved_icon_reference.png" style="width:16mm;filter:grayscale(1);opacity:.55"><span class="cap">Concept study that defined the idea (retired artwork and colours).</span></div>
  </div>
  <div style="grid-column:5/13;display:grid;grid-template-columns:repeat(4,1fr);gap:4mm;align-content:center">
    {''.join(f'<div class="panel" style="padding:4mm"><div class="tn" style="font-size:7pt;color:#0F7C74;font-weight:600">0{i+1}</div><div style="margin:2mm 0">{step_svg(i)}</div><h3>{a}</h3><p style="font-size:6.8pt;margin-top:1mm">{b}</p></div>' for i, (a, b) in enumerate(steps))}
    <div class="panel" style="grid-column:1/5;padding:5mm;display:flex;align-items:center;justify-content:space-around;background:#022329">
      {img("icon/svg/WFS_Icon_Premium.svg", "width:44mm")}{img("icon/svg/WFS_Icon_Primary.svg", "width:30mm;background:#F3F5F2;border-radius:50%;padding:2mm")}{img("icon/svg/WFS_Icon_Inverse.svg", "width:30mm")}{img("icon/svg/WFS_Icon_White.svg", "width:30mm")}</div>
  </div>
</div>''', toc='Logo concept')

# ================================================================= 07 PRIMARY LOGO
page('02 · Logo', 'Primary logo', f'''
<div class="c">
  <div class="eb">Primary logo · Horizontal lockup</div>
  <div style="position:absolute;left:0;right:0;top:22mm;bottom:22mm;display:flex;align-items:center;justify-content:center">{img("logo/svg/WFS_Logo_Horizontal_Primary.svg", "width:205mm")}</div>
  <div class="row" style="position:absolute;left:0;right:0;bottom:0;gap:8mm">
    <p style="flex:1">The horizontal lockup — icon + WFS wordmark — is the primary signature. Use it wherever space allows.</p>
    <p style="flex:1">The icon leads; the wordmark cap-height is 0.46 × icon diameter and the gap is 0.30 × diameter. Never rebuild the lockup: use the master files.</p>
    <p style="flex:1">Default colourway on light grounds. On dark grounds use the Inverse version (page 16).</p>
  </div>
</div>''', 'white', toc='Primary logo')

# ================================================================= 08 ARCHITECTURE
arch = [('Primary', 'WFS_Logo_Horizontal_Primary', 'logo', 'Horizontal lockup. Default for product, web, documents, presentations.', '#fff', '44mm'),
        ('Secondary', 'WFS_Logo_Full_English', 'logo', 'Full lockup with descriptor for first contact and formal materials.', '#fff', '44mm'),
        ('Stacked', 'WFS_Logo_Stacked_Primary', 'logo', 'Square and vertical formats, splash screens, social avatars (large).', '#fff', '24mm'),
        ('Compact', 'WFS_Icon_Primary', 'icon', 'The icon alone once WFS is established in context (UI, favicons).', '#fff', '20mm'),
        ('App / digital', None, 'app', 'App icon artwork: dark field, inverse icon, platform-masked.', '#fff', '22mm'),
        ('Monochrome', 'WFS_Logo_Horizontal_Dark', 'logo', 'One colour for single-ink print, forms, engraving, embroidery.', '#fff', '44mm'),
        ('Inverse', 'WFS_Logo_Horizontal_Inverse', 'logo', 'Full colour for dark grounds (#022329, #0E3D42, dark imagery).', '#022329', '44mm'),
        ('Premium display', 'WFS_Logo_Horizontal_Premium', 'logo', 'Dimensional version for launch, keynote and event use only.', '#022329', '44mm')]
cells = ''
for name, f_, g, d, bg, w in arch:
    art = (img(f"icon/app/WFS_AppIcon_Dark_512.png", "width:22mm;border-radius:5mm") if g == 'app' else img(f"{g}/svg/{f_}.svg", f"width:{w};max-height:30mm"))
    cells += (f'<div style="display:flex;flex-direction:column"><div style="height:44mm;border-radius:2mm;background:{bg};display:flex;align-items:center;justify-content:center;border:.2mm solid #E3E9E7">{art}</div>'
              f'<h3 style="margin-top:2.5mm">{name}</h3><p style="font-size:7pt;margin-top:.8mm">{d}</p></div>')
page('02 · Logo', 'Logo architecture', f'''
<div class="c"><div class="eb">Logo architecture</div><h1>One system, eight roles</h1>
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:5mm 5mm;margin-top:7mm">{cells}</div></div>''', toc='Logo architecture')

# ================================================================= 09 ICON ANATOMY
cen = L._blade_centroids()
labels_svg = ''
for i, b in enumerate(L.BLADES):
    cx, cy = cen[b]; r = math.hypot(cx, cy); ux, uy = cx / r, cy / r
    lx, ly = ux * 640, uy * 640
    labels_svg += (f'<line x1="{cx:.0f}" y1="{cy:.0f}" x2="{lx:.0f}" y2="{ly:.0f}" stroke="#80918F" stroke-width="2"/><circle cx="{cx:.0f}" cy="{cy:.0f}" r="9" fill="#022329" stroke="#fff" stroke-width="3"/>'
                   f'<text x="{lx + (20 if ux > 0 else -20):.0f}" y="{ly + 14:.0f}" text-anchor="{"start" if ux > 0 else "end"}" font-size="44" font-family="Instrument Sans" font-weight="600" fill="#022329">{b}</text>')
page('02 · Logo', 'The icon', f'''
<div class="c g12">
  <div style="grid-column:1/5">
    <div class="eb">The icon</div><h1>Five fields.<br>One aperture.</h1>
    <p style="margin-top:5mm">The icon is an aperture of five interlocking blades. Each blade is a curvilinear surface running from the outer field into the central opening — separate operations resolving into one controlled view.</p>
    <ul class="clean" style="margin-top:5mm">
      <li>Tonal ramp clockwise: <b>B1</b> Mint · <b>B2</b> Teal · <b>B3</b> Teal 700 · <b>B4</b> Deep Teal · <b>B5</b> WFS Dark.</li>
      <li>Exact 72° rotational symmetry; outer circle and aperture share one centre.</li>
      <li>Aperture Ø = 0.38 × icon Ø — it is also the clear-space unit.</li>
      <li>Blade tips meet the aperture tangentially; never round or cut them.</li>
      <li>On dark grounds use the Inverse ramp (Mint 100 → Teal 800).</li>
    </ul>
  </div>
  <div style="grid-column:5/13;display:flex;align-items:center;justify-content:center">
    <svg viewBox="-900 -620 1800 1240" style="width:175mm"><g>{L.icon_paths(P["primary"]["blades"], ids=False)}</g>{labels_svg}</svg>
  </div>
</div>''', 'white', toc='The icon')

# ================================================================= 10 WORDMARK
page('02 · Logo', 'The wordmark', f'''
<div class="c">
  <div class="eb">The wordmark</div><h1>Custom letterforms — never typeset</h1>
  <div style="position:absolute;left:0;right:0;top:22mm;bottom:26mm;display:flex;align-items:center;justify-content:center">{img("wordmark/svg/WFS_Wordmark_Primary.svg", "width:215mm")}</div>
  <div class="row" style="position:absolute;left:0;right:0;bottom:0;gap:6mm">
    <div style="flex:1"><h3>Ribbon construction</h3><p>W, F and S are drawn as continuous folded ribbons: sheared diagonals, a sweeping F bar and an S built from two horizontal bands.</p></div>
    <div style="flex:1"><h3>Geometry</h3><p class="tn">Stroke angles 60° / 63.5° / 120° / 123° / 125°; true horizontals and verticals; cap height = 1000 master units; width 4 680.</p></div>
    <div style="flex:1"><h3>Relationship to type</h3><p>Instrument Sans supports the wordmark; it never replaces it. Do not recreate "WFS" in any font.</p></div>
    <div style="flex:1"><h3>Colour</h3><p>WFS Dark (#022329) on light, Off-White (#F3F5F2) on dark. One colour only — the premium version is for display use.</p></div>
  </div>
</div>''', 'white', toc='The wordmark')

# ================================================================= 11 LOCKUPS
page('02 · Logo', 'Lockups', f'''
<div class="c"><div class="eb">Lockups</div><h1>Lockup family</h1>
  <div style="display:grid;grid-template-columns:1.25fr 1fr;grid-template-rows:1fr 1fr;gap:5mm;margin-top:6mm;height:128mm">
    <div class="panel" style="grid-column:1;grid-row:1;padding:5mm;display:flex;flex-direction:column"><span class="tag" style="align-self:flex-start">Horizontal · primary</span><div style="flex:1;display:flex;align-items:center;justify-content:center">{img("logo/svg/WFS_Logo_Horizontal_Primary.svg", "width:98mm")}</div></div>
    <div class="panel" style="grid-column:2;grid-row:1/3;padding:5mm;display:flex;flex-direction:column"><span class="tag" style="align-self:flex-start">Stacked</span><div style="flex:1;display:flex;align-items:center;justify-content:center">{img("logo/svg/WFS_Logo_Stacked_Primary.svg", "width:56mm")}</div>
      <p style="font-size:7pt">Icon centred above the wordmark; wordmark cap = 0.40 D, gap = 0.26 D.</p></div>
    <div class="panel" style="grid-column:1;grid-row:2;padding:5mm;display:flex;flex-direction:column"><span class="tag" style="align-self:flex-start">Full · with descriptor</span><div style="flex:1;display:flex;align-items:center;justify-content:center">{img("logo/svg/WFS_Logo_Full_English.svg", "width:98mm")}</div>
      <p style="font-size:7pt">Descriptor: Instrument Sans Medium, all caps, justified to the wordmark width. The bilingual descriptor (English + <span class="ar">نظام وصول المالي</span>) is produced only with the licensed Arabic font.</p></div>
  </div></div>''', toc='Lockups')

# ================================================================= 12 CONSTRUCTION
circ = ''
for c in L.ICON['circles']:
    col = '#14B8A6' if c['role'] == 'outer' else '#0F7C74' if c['role'] == 'aperture' else '#B94E8A'
    circ += (f'<circle cx="{c["centre"][0]}" cy="{c["centre"][1]}" r="{c["radius"]}" fill="none" stroke="{col}" stroke-width="3" stroke-opacity=".8" stroke-dasharray="{"none" if c["role"] in ("outer", "aperture") else "14 10"}"/>'
             f'<circle cx="{c["centre"][0]}" cy="{c["centre"][1]}" r="9" fill="{col}"/>')
axes = ''.join(f'<line x1="0" y1="0" x2="{1150 * math.cos(math.radians(IP["rotation_deg"] + 72 * k)):.1f}" y2="{1150 * math.sin(math.radians(IP["rotation_deg"] + 72 * k)):.1f}" stroke="#80918F" stroke-width="2" stroke-dasharray="4 8"/>' for k in range(5))
outline = ''.join(f'<path d="{L.ICON["blades"][b]["paths"]["solid"]}" fill="#F3F5F2" stroke="#022329" stroke-width="4"/>' for b in L.BLADES)
page('02 · Logo', 'Construction & geometry', f'''
<div class="c g12">
  <div style="grid-column:1/5">
    <div class="eb">Construction</div><h1>Seven circles,<br>one mark</h1>
    <p style="margin-top:5mm">The icon is fully defined by three numbers on a 1 000-unit grid. The five edge circles are one circle rotated in 72° steps; each is externally tangent to the aperture at a blade tip.</p>
    <table class="spec" style="margin-top:5mm">
      <tr><th>Element</th><th>Value</th></tr>
      <tr><td><span style="color:#14B8A6">●</span> Outer circle R</td><td class="tn">500 (Ø 1 000)</td></tr>
      <tr><td><span style="color:#0F7C74">●</span> Aperture r</td><td class="tn">{IP["r"]:.0f}</td></tr>
      <tr><td><span style="color:#B94E8A">●</span> Edge circle ρ</td><td class="tn">{IP["rho"]:.0f} · centre at r + ρ = {IP["r"] + IP["rho"]:.0f}</td></tr>
      <tr><td>Symmetry</td><td class="tn">5-fold · 72° · first tip at {IP["rotation_deg"]:.0f}°</td></tr>
      <tr><td>Blade sweep</td><td class="tn">tip → rim ≈ 47° clockwise</td></tr>
      <tr><td>Watertight</td><td class="tn">blades cover the ring exactly ({L.ICON["coverage"]:.3f})</td></tr>
    </table>
    <p class="cap" style="margin-top:3mm">Numeric master: brand/source/master/icon_geometry.json · generator: brand/source/design_icon.py</p>
  </div>
  <div style="grid-column:5/13;display:flex;align-items:center;justify-content:center;overflow:hidden">
    <svg viewBox="-1180 -1000 2360 2000" style="width:170mm;height:144mm"><rect x="-1180" y="-1000" width="2360" height="2000" fill="#fff"/>
      <g stroke="#EDF1EF" stroke-width="2">{''.join(f'<line x1="{x}" y1="-1000" x2="{x}" y2="1000"/>' for x in range(-1150, 1160, 125))}{''.join(f'<line x1="-1180" y1="{y}" x2="1180" y2="{y}"/>' for y in range(-1000, 1001, 125))}</g>
      {axes}{outline}{circ}</svg>
  </div>
</div>''', toc='Construction & geometry')

# ================================================================= 13 CLEAR SPACE
def clearspace_svg():
    inner, box = L.lockup('horizontal', L.icon_paths(P['primary']['blades'], ids=False), L.wordmark_paths('#022329', ids=False))
    x0, y0, w, h = box; a = AP_W
    pad = a * 1.35
    vb = f'{x0 - pad} {y0 - pad} {w + 2 * pad} {h + 2 * pad}'
    zone = f'<rect x="{x0 - a}" y="{y0 - a}" width="{w + 2 * a}" height="{h + 2 * a}" fill="#DDF5F1" stroke="#14B8A6" stroke-width="4" stroke-dasharray="18 12"/>'
    bbox = f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="#fff" stroke="#80918F" stroke-width="2"/>'
    ap_marks = ''
    for (cx, cy) in ((x0 - a / 2, y0 + h / 2), (x0 + w + a / 2, y0 + h / 2), (x0 + w / 2, y0 - a / 2), (x0 + w / 2, y0 + h + a / 2)):
        ap_marks += (f'<circle cx="{cx}" cy="{cy}" r="{a / 2 - 6}" fill="none" stroke="#0F7C74" stroke-width="4"/>'
                     f'<text x="{cx}" y="{cy + 26}" text-anchor="middle" font-size="80" font-weight="600" font-family="Instrument Sans" fill="#0F7C74">A</text>')
    return f'<svg viewBox="{vb}" style="width:100%;height:100%">{zone}{bbox}{inner}{ap_marks}</svg>'
page('02 · Logo', 'Clear space', f'''
<div class="c g12">
  <div style="grid-column:1/5">
    <div class="eb">Clear space</div><h1>Measured by<br>the aperture</h1>
    <p style="margin-top:5mm">The clear-space unit <b>A</b> is the width of the icon's central aperture ({AP:.3f} × icon diameter). Keep at least <b>1 A</b> free of text, edges and other graphics on every side of any lockup or of the icon.</p>
    <ul class="clean" style="margin-top:5mm"><li><b>Minimum:</b> 1 A on all sides.</li><li><b>Preferred (brand-led layouts):</b> 2 A.</li>
      <li><b>UI chrome</b> (headers, nav bars): 0.5 A is permitted when the logo is vertically centred in a bar of ≥ 2.2 × icon height.</li>
      <li><b>Text:</b> body text or headings never enter the clear-space zone; align text to the zone edge, not the artwork.</li></ul>
    <p class="cap" style="margin-top:3mm">Because A is part of the icon, clear space scales automatically with the logo — no pixel values needed.</p>
  </div>
  <div style="grid-column:5/13;height:150mm;display:flex;align-items:center">{clearspace_svg()}</div>
</div>''', 'white', toc='Clear space')

# ================================================================= 14 MINIMUM SIZES
def at_px(path, px, dim='width'): return f'<img src="{A}/{path}" style="{dim}:{px}px;display:block">'
minrows = [('Icon · full colour', 'icon/svg/WFS_Icon_Primary.svg', 'height', 16, '16 px', '5 mm', 'Favicon, tabs, dense UI. Below 24 px prefer the favicon tile.'),
           ('Icon · one colour', 'icon/svg/WFS_Icon_Dark.svg', 'height', 24, '24 px', '6 mm', '16–23 px: use the micro version (gap 56) from the favicon set.'),
           ('Wordmark', 'wordmark/svg/WFS_Wordmark_Primary.svg', 'width', 64, '64 px wide', '15 mm wide', 'Counters in W and S remain open at 64 px.'),
           ('Horizontal lockup', 'logo/svg/WFS_Logo_Horizontal_Primary.svg', 'width', 96, '96 px wide', '25 mm wide', 'Below this, use the icon alone.'),
           ('Full lockup (descriptor)', 'logo/svg/WFS_Logo_Full_English.svg', 'width', 220, '220 px wide', '55 mm wide', 'Descriptor cap height ≥ 6 px / 1.4 mm.'),
           ('App icon', 'icon/app/WFS_AppIcon_Dark_512.png', 'width', 16, '16 px', '—', 'Sizes ≤ 64 px use the compact artwork.')]
page('02 · Logo', 'Minimum sizes', f'''
<div class="c"><div class="eb">Minimum sizes</div><h1>Tested, not theoretical</h1>
<p style="width:175mm;margin-top:3mm">Minimums were set by rendering every version at decreasing sizes and checking that the aperture stays open, blade separation is visible and the wordmark counters don't close. Samples below are shown at their true minimum size (1 px = 1/96 in).</p>
<table class="spec" style="margin-top:6mm"><tr><th style="width:44mm">Version</th><th style="width:70mm">Actual-size sample</th><th>Screen</th><th>Print</th><th>Note</th></tr>
{''.join(f'<tr><td style="padding:3mm 0">{a}</td><td style="padding:3mm 0">{at_px(p, px, dim)}</td><td class="tn">{s}</td><td class="tn">{pr}</td><td>{n}</td></tr>' for a, p, dim, px, s, pr, n in minrows)}
</table>
<div class="row" style="margin-top:6mm;align-items:flex-end;gap:7mm">{''.join(f'<div style="text-align:center">{at_px("icon/svg/WFS_Icon_Primary.svg", s, "height")}<div class="cap tn" style="margin-top:1.5mm">{s}px</div></div>' for s in (16, 24, 32, 48, 64, 96))}
<div style="text-align:center">{at_px("icon/favicon/favicon-16x16.png", 16, "height")}<div class="cap" style="margin-top:1.5mm">favicon 16</div></div>
<div style="text-align:center">{at_px("icon/favicon/favicon-32x32.png", 32, "height")}<div class="cap" style="margin-top:1.5mm">favicon 32</div></div></div>
</div>''', 'white', toc='Minimum sizes')

# ================================================================= 15 BACKGROUNDS
bgs = [('#022329', 'WFS_Logo_Horizontal_Inverse', 'WFS Dark #022329', True), ('#0E3D42', 'WFS_Logo_Horizontal_Inverse', 'Deep Teal #0E3D42', True),
       ('#F3F5F2', 'WFS_Logo_Horizontal_Primary', 'Off-White #F3F5F2', True), ('#FFFFFF', 'WFS_Logo_Horizontal_Primary', 'White', True),
       ('#000000', 'WFS_Logo_Horizontal_White', 'Black · one-colour white', True), ('#14B8A6', 'WFS_Logo_Horizontal_Dark', 'Primary Teal · one-colour dark', True),
       ('url', 'WFS_Logo_Horizontal_Inverse', 'Dark imagery · inverse', True), ('urll', 'WFS_Logo_Horizontal_Primary', 'Light imagery · primary', True)]
cells = ''
for bg, f_, lab, ok in bgs:
    style = (f"background:url('img/art_photo_ground_dark.jpg') center/cover" if bg == 'url' else
             f"background:url('img/art_photo_ground_light.jpg') center/cover" if bg == 'urll' else f'background:{bg}')
    cells += (f'<div><div style="height:56mm;border-radius:2mm;{style};display:flex;align-items:center;justify-content:center;border:.2mm solid #E3E9E7">{img(f"logo/svg/{f_}.svg", "width:44mm")}</div>'
              f'<div class="cap" style="margin-top:1.5mm">{lab}</div></div>')
page('02 · Logo', 'Logo on backgrounds', f'''
<div class="c"><div class="eb">Backgrounds</div><h1>Choose the version by the ground</h1>
<p style="width:190mm;margin-top:3mm">Primary on light grounds, Inverse on dark grounds, one-colour versions on colour fields and on busy imagery. On photography, place the logo on the calmest area and keep contrast ≥ 3 : 1 against the local background.</p>
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:5mm;margin-top:6mm">{cells}</div></div>''', toc='Logo on backgrounds')

# ================================================================= 16 COLOUR VERSIONS
vers = [('Primary', 'icon/svg/WFS_Icon_Primary.svg', 'logo/svg/WFS_Logo_Horizontal_Primary.svg', '#F3F5F2'),
        ('Inverse', 'icon/svg/WFS_Icon_Inverse.svg', 'logo/svg/WFS_Logo_Horizontal_Inverse.svg', '#022329'),
        ('Flat teal', 'icon/svg/WFS_Icon_Flat_Teal.svg', None, '#022329'),
        ('Dark', 'icon/svg/WFS_Icon_Dark.svg', 'logo/svg/WFS_Logo_Horizontal_Dark.svg', '#FFFFFF'),
        ('White', 'icon/svg/WFS_Icon_White.svg', 'logo/svg/WFS_Logo_Horizontal_White.svg', '#0E3D42'),
        ('Black', 'icon/svg/WFS_Icon_Black.svg', 'logo/svg/WFS_Logo_Horizontal_Black.svg', '#FFFFFF'),
        ('Monochrome', 'icon/svg/WFS_Icon_Monochrome.svg', 'logo/svg/WFS_Logo_Horizontal_Monochrome.svg', '#FFFFFF'),
        ('Monochrome light', 'icon/svg/WFS_Icon_Monochrome_Light.svg', 'logo/svg/WFS_Logo_Horizontal_Monochrome_Light.svg', '#111')]
cells = ''.join(f'<div><div style="height:55mm;border-radius:2mm;background:{bg};border:.2mm solid #E3E9E7;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:5mm">'
                f'{img(i, "height:20mm")}{img(l, "width:40mm") if l else "<span class=cap>icon only · accent use</span>"}</div><div class="cap" style="margin-top:1.5mm">{n}</div></div>' for n, i, l, bg in vers)
page('02 · Logo', 'Colour versions', f'''
<div class="c"><div class="eb">Colour versions</div><h1>Full colour, one colour, greyscale</h1>
<p style="width:200mm;margin-top:3mm">One-colour icons separate the blades with a knockout gap derived from the blade edges (gap = 2 % of D; 3.2 % at 24–47 px; 5.6 % below 24 px). Greyscale versions keep the full-colour tonal order for single-channel print.</p>
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:5mm;margin-top:6mm">{cells}</div></div>''', toc='Colour versions')

# ================================================================= 17 PREMIUM
page('02 · Logo', 'Premium display version', f'''
<img src="{A}/graphic-system/fields/WFS_Overlay_Unified_Field_OnDark.svg" style="position:absolute;left:40mm;top:-50mm;width:300mm;opacity:.55">
<div class="c g12">
  <div style="grid-column:1/5">
    <div class="eb">Premium display</div><h1>Depth without decoration</h1>
    <p style="margin-top:5mm">The premium version uses the same master geometry. Each blade carries a gradient from a shaded tip to a lit rim; every overlap casts a soft contact shadow that follows the edge circle exactly; the upper blade catches a fine lit edge; a key light falls from the top-left. All of it is built with gradients — no raster effects.</p>
    <ul class="clean" style="margin-top:5mm"><li><b>Use for:</b> launch visuals, keynote title slides, event screens, store artwork, hero sections.</li>
      <li><b>Never use for:</b> UI chrome, favicons, documents, small sizes (&lt; 64 px / 20 mm), one-colour print.</li>
      <li>No chrome, no glare, no bevel, no drop shadow. No gold or blue.</li></ul>
  </div>
  <div style="grid-column:5/13;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:9mm">
    {img("icon/svg/WFS_Icon_Premium.svg", "width:92mm")}{img("wordmark/svg/WFS_Wordmark_Premium.svg", "width:110mm")}
  </div>
</div>''', 'dark', toc='Premium display version')

# ================================================================= 18 MISUSE
def mis(inner, label, bg='#fff'):
    return f'<div style="min-width:0"><div class="no" style="height:52mm;border-radius:2mm;background:{bg};border:.2mm solid #E3E9E7;display:flex;align-items:center;justify-content:center;overflow:hidden">{inner}</div><div class="cap" style="margin-top:1.3mm">{label}</div></div>'
LG = f'{A}/logo/svg/WFS_Logo_Horizontal_Primary.svg'
def separated():
    g = ''
    for i, (b, c) in enumerate(zip(L.BLADES, P['primary']['blades'])):
        dx, dy = 120 * math.cos(math.radians(72 * i + 30)), 120 * math.sin(math.radians(72 * i + 30))
        g += f'<path transform="translate({dx:.0f} {dy:.0f})" d="{L.ICON["blades"][b]["paths"]["solid"]}" fill="{c}"/>'
    return f'<svg viewBox="-680 -680 1360 1360" style="height:26mm">{g}</svg>'
misuse = [
    mis(f'<img src="{LG}" style="width:28mm;transform:scale(1.28,.6)">', 'Do not stretch or distort'),
    mis(f'<img src="{LG}" style="width:34mm;transform:rotate(-12deg)">', 'Do not rotate'),
    mis(f'<img src="{LG}" style="width:34mm;filter:hue-rotate(160deg) saturate(1.4)">', 'Do not recolour arbitrarily'),
    mis(f'<div style="display:flex;align-items:center;gap:2mm">{img("icon/svg/WFS_Icon_Primary.svg", "height:15mm")}{img("wordmark/svg/WFS_Wordmark_Primary.svg", "height:4mm")}</div>', 'Do not change proportions'),
    mis(f'<div style="display:flex;align-items:center;gap:9mm">{img("icon/svg/WFS_Icon_Primary.svg", "height:8mm")}{img("wordmark/svg/WFS_Wordmark_Primary.svg", "height:4mm")}</div>', 'Do not alter spacing'),
    mis(f'<img src="{LG}" style="width:34mm;filter:drop-shadow(1.2mm 1.4mm 1mm rgba(0,0,0,.55))">', 'Do not add drop shadows'),
    mis(f'<img src="{A}/logo/svg/WFS_Logo_Horizontal_Primary.svg" style="width:32mm">', 'Do not place on low-contrast grounds', '#14B8A6'),
    mis(f'<div style="display:flex;align-items:center;gap:3mm">{img("icon/svg/WFS_Icon_Primary.svg", "height:10mm")}<span style="font:700 25pt Georgia,serif;color:#022329">WFS</span></div>', 'Do not typeset the wordmark'),
    mis(separated(), 'Do not separate the blades'),
    mis(f'<div style="position:relative"><img src="{LG}" style="width:34mm;display:block"><div style="position:absolute;inset:0;background:linear-gradient(90deg,#ff4d8d,#ffc53d,#3dd6ff);mix-blend-mode:color"></div></div>', 'Do not apply random gradients'),
    mis(f'<img src="{A}/source/reference/approved_icon_reference.png" style="height:24mm">', 'Do not use retired concept colours'),
    mis(f'<img src="{LG}" style="width:34mm;outline:.5mm solid #022329;outline-offset:1.5mm;border-radius:1mm">', 'Do not box, outline or badge the logo'),
]
page('02 · Logo', 'Incorrect usage', f'''
<div class="c"><div class="eb">Incorrect usage</div><h1>Protect the mark</h1>
<div style="display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:5mm 4mm;margin-top:7mm">{"".join(misuse)}</div>
<p class="cap" style="margin-top:4mm">Always use the master artwork from brand/logo, brand/icon and brand/wordmark. When in doubt, use the Primary or Inverse horizontal lockup.</p></div>''', 'white', toc='Incorrect usage')

# ================================================================= 19 COLOUR CORE
def core_card(key, big=False):
    c = B.CORE[key]; h = c['hex']; r, g, b = B.hex_rgb(h); cmyk = B.rgb_cmyk(h)
    dark_txt = B.rel_lum(h) > 0.3
    fg = '#022329' if dark_txt else '#F3F5F2'
    return (f'<div class="sw" style="background:{h};color:{fg};flex:{2.2 if big else 1};padding:4mm;display:flex;flex-direction:column;justify-content:space-between;{"border:.2mm solid #D6DEDB" if key == "wfs-offwhite" else ""}">'
            f'<div><div style="font-size:6pt;letter-spacing:.14em;text-transform:uppercase;opacity:.75">Core</div><div style="font-size:11pt;font-weight:600;margin-top:1mm">{c["name"]}</div></div>'
            f'<div class="tn" style="font-size:7pt;line-height:1.6"><div style="font-size:10pt;font-weight:600">{h}</div>RGB {r} {g} {b}<br>CMYK≈ {cmyk[0]} {cmyk[1]} {cmyk[2]} {cmyk[3]}</div></div>')
page('03 · Colour', 'Colour system — core palette', f'''
<div class="c"><div class="eb">Colour system</div><h1>Five core colours</h1>
<p style="width:210mm;margin-top:3mm">The core palette is fixed. Dark teal grounds and a single luminous teal carry the brand; mint lights it; off-white gives it air. Proportions guide every layout: roughly 60 % dark or off-white ground, 25 % deep/neutral surfaces, 10 % teal, 5 % mint.</p>
<div class="row" style="margin-top:6mm;height:92mm;gap:3mm">{core_card("wfs-dark", True)}{core_card("wfs-deep", True)}{core_card("wfs-teal", True)}{core_card("wfs-mint")}{core_card("wfs-offwhite")}</div>
<div class="row" style="margin-top:4mm;height:4mm;gap:0;border-radius:1mm;overflow:hidden"><div style="flex:60;background:#022329"></div><div style="flex:25;background:#0E3D42"></div><div style="flex:10;background:#14B8A6"></div><div style="flex:5;background:#7FE3D6"></div></div>
<p class="cap" style="margin-top:3mm">CMYK values are uncalibrated approximations from sRGB for reference only. Printed colour varies with process, substrate and ICC profile — always proof physically against the HEX/RGB master before production.</p></div>''', toc='Colour system')

# ================================================================= 20 COLOUR EXTENDED + ROLES + CONTRAST + DATAVIZ
der = ''.join(f'<div style="display:flex;align-items:center;gap:2.5mm;padding:1.3mm 0;border-top:.2mm solid #E3E9E7"><span style="width:7mm;height:7mm;border-radius:1.5mm;background:{v["hex"]};border:.2mm solid #D6DEDB"></span>'
              f'<span style="font-size:7pt;font-weight:600;width:20mm">{v["name"]}</span><span class="tn" style="font-size:7pt;width:15mm">{v["hex"]}</span><span style="font-size:6.3pt;color:#80918F;flex:1">{v["desc"].replace("Derived. ", "").replace("Derived neutral. ", "")}</span></div>'
              for k, v in B.DERIVED.items() if k != 'paper-0')
pairs = [('#022329', '#F3F5F2'), ('#022329', '#FFFFFF'), ('#4A5E61', '#FFFFFF'), ('#0F7C74', '#FFFFFF'), ('#14B8A6', '#022329'), ('#7FE3D6', '#022329'),
         ('#F3F5F2', '#0E3D42'), ('#9DB5B3', '#022329'), ('#14B8A6', '#FFFFFF')]
ct = ''.join(f'<tr><td><span style="display:inline-block;padding:.6mm 2mm;border-radius:1mm;background:{b};color:{a};font-weight:600;border:.2mm solid #E3E9E7">Aa</span></td><td class="tn">{a} on {b}</td><td class="tn">{B.contrast(a, b):.1f} : 1</td>'
             f'<td>{"AAA" if B.contrast(a, b) >= 7 else "AA" if B.contrast(a, b) >= 4.5 else "AA large / UI" if B.contrast(a, b) >= 3 else "Decorative only"}</td></tr>' for a, b in pairs)
dv = ''.join(f'<span style="display:inline-flex;align-items:center;gap:1mm;font-size:6.3pt;margin-right:2.5mm"><span style="width:4mm;height:4mm;border-radius:1mm;background:{c}"></span><span class="tn">{c}</span></span>' for c in B.DATAVIZ['light'])
dvd = ''.join(f'<span style="display:inline-flex;align-items:center;gap:1mm;font-size:6.3pt;margin-right:2.5mm;color:#9DB5B3"><span style="width:4mm;height:4mm;border-radius:1mm;background:{c}"></span><span class="tn">{c}</span></span>' for c in B.DATAVIZ['dark'])
fn = ''.join(f'<span style="display:inline-flex;align-items:center;gap:1mm;font-size:6.3pt;margin-right:2.5mm"><span style="width:4mm;height:4mm;border-radius:1mm;background:{v["hex"]}"></span>{v["name"]} <span class="tn">{v["hex"]}</span></span>' for v in B.FUNCTIONAL.values())
page('03 · Colour', 'Colour system — extended, roles, accessibility', f'''
<div class="c g12">
  <div style="grid-column:1/6"><div class="eb">Derived tones</div><h2 style="margin-top:2mm">Controlled intermediate steps</h2>
    <p style="font-size:7pt;margin-top:1.5mm">Derived tones are not core colours. They exist for accessibility, UI states and depth, and are always used next to the core palette.</p>
    <div style="margin-top:3mm">{der}</div>
    <h3 style="margin-top:4mm">Functional colours (product UI)</h3><div style="margin-top:1.5mm;line-height:2">{fn}</div>
  </div>
  <div style="grid-column:6/13">
    <div class="eb">Roles</div>
    <div class="row" style="margin-top:2mm;gap:3mm">
      {''.join(f'<div style="flex:1;border-radius:2mm;padding:3mm;background:{r["background"]};border:.2mm solid #D6DEDB"><div style="font-size:7pt;font-weight:600;color:{r["text"]}">{m.capitalize()} mode</div>' + ''.join(f'<div style="display:flex;align-items:center;gap:1.5mm;margin-top:1.2mm"><span style="width:3.5mm;height:3.5mm;border-radius:.8mm;background:{v};border:.2mm solid {r["border"]}"></span><span style="font-size:6pt;color:{r["text_2"]};width:20mm">{k.replace("_", " ")}</span><span class="tn" style="font-size:6pt;color:{r["text"]}">{v}</span></div>' for k, v in r.items()) + '</div>' for m, r in B.ROLES.items())}
    </div>
    <div class="eb" style="margin-top:4mm">Contrast (WCAG 2.2)</div>
    <table class="spec" style="margin-top:1mm"><tr><th>Sample</th><th>Pair</th><th>Ratio</th><th>Use</th></tr>{ct}</table>
    <div class="eb" style="margin-top:3mm">Data visualisation</div>
    <div style="margin-top:1.5mm">{dv}<span class="cap"> light</span></div>
    <div style="margin-top:1.2mm;background:#0E3D42;border-radius:1mm;padding:1mm 2mm;display:inline-block">{dvd}<span class="cap" style="color:#6F8987"> dark</span></div>
    <p class="cap" style="margin-top:1.5mm">Validated for lightness band, chroma, colour-vision-deficiency and normal-vision separation, and ≥ 3 : 1 against the chart surface. Assign in fixed order; teal is always series 1.</p>
  </div>
</div>''', 'white', toc='Colour — extended & accessibility')

# ================================================================= 21 GRADIENTS
gcards = ''
for k, g in B.GRADIENTS.items():
    if g.get('kind') == 'radial':
        css = f'radial-gradient(120% 90% at 68% 40%, rgba(20,184,166,.28) 0%, rgba(14,61,66,0) 45%), {g["base"]}'
        spec = 'Radial · centre 68 % / 40 % · ' + ' → '.join(f'{c} {int(a*100)}% @ {o}%' for c, o, a in g['stops']) + f' · on {g["base"]}'
    else:
        css = f'linear-gradient({g["angle"]}deg, ' + ', '.join(f'{c} {o}%' for c, o in g['stops']) + ')'
        spec = f'{g["angle"]}° · ' + ' → '.join(f'{c} {o}%' for c, o in g['stops'])
    gcards += (f'<div style="flex:1;display:flex;flex-direction:column"><div style="height:86mm;border-radius:2mm;background:{css};border:.2mm solid #D6DEDB"></div>'
               f'<h3 style="margin-top:2.5mm">{g["name"]}</h3><p class="tn" style="font-size:6.3pt;margin-top:.8mm;color:#0F7C74">{spec}</p><p style="font-size:6.6pt;margin-top:1mm">{g["use"]}</p></div>')
page('03 · Colour', 'Gradient system', f'''
<div class="c"><div class="eb">Gradient system</div><h1>Restrained light</h1>
<p style="width:210mm;margin-top:3mm">Gradients describe light falling on the Unified Financial Field. They use only core and derived teals, move in one direction, and never sit behind body text except the Deep and Light grounds. No rainbow, purple or neon gradients.</p>
<div class="row" style="margin-top:6mm;gap:4mm">{gcards}</div>
<p class="cap" style="margin-top:4mm">CSS tokens: brand/graphic-system/gradients/wfs-gradients.css · SVG swatches in the same folder.</p></div>''', toc='Gradient system')

# ================================================================= 22 TYPE EN
weights = [(400, 'Regular'), (500, 'Medium'), (600, 'SemiBold'), (700, 'Bold')]
scale = [('Display', '56 / 58', 600, '-0.035em', 56), ('H1', '40 / 44', 600, '-0.03em', 40), ('H2', '28 / 32', 600, '-0.02em', 28), ('H3', '20 / 26', 600, '-0.01em', 20),
         ('Body L', '17 / 26', 400, '0', 17), ('Body', '15 / 22', 400, '0', 15), ('Small', '13 / 18', 400, '0', 13), ('Label', '11 / 14 · caps', 600, '0.14em', 11), ('Caption', '11 / 15', 400, '0', 11)]
page('04 · Typography', 'Typography — English', f'''
<div class="c g12">
  <div style="grid-column:1/6">
    <div class="eb">Typeface · Latin</div><h1 style="font-size:48pt;letter-spacing:-.04em">Instrument Sans</h1>
    <p style="margin-top:4mm">A contemporary grotesque with precise, slightly condensed proportions — neutral enough for dense financial UI, distinctive enough for display. Open Font License. Four weights only: Regular, Medium, SemiBold, Bold.</p>
    <div style="margin-top:5mm;font-size:22pt;line-height:1.25;letter-spacing:-.01em">Aa Bb Cc Dd Ee Ff Gg<br>0123456789 %&amp;.,:()</div>
    <div class="row" style="margin-top:5mm;gap:4mm">{''.join(f'<div style="flex:1;border-top:.25mm solid #D6DEDB;padding-top:2mm"><div style="font-size:18pt;font-weight:{w}">Ag</div><div class="cap">{n} {w}</div></div>' for w, n in weights)}</div>
    <div style="margin-top:6mm;padding:4mm 5mm;background:#F3F5F2;border-radius:2mm"><div class="eb" style="font-size:6pt">Treasury · Group cash</div><div style="font-size:14pt;font-weight:600;letter-spacing:-.015em;margin-top:1.5mm">Liquidity is consolidated across five entities.</div><div style="font-size:8.5pt;line-height:1.5;color:#4A5E61;margin-top:1.5mm">Cash rose <span class="tn">2.4 %</span> to <span class="tn">48,612,480.25 USD</span>. Two payment batches await approval before the <span class="tn">16:00</span> cut-off.</div></div>
  </div>
  <div style="grid-column:7/13">
    <div class="eb">Type scale (px, digital)</div>
    <table class="spec" style="margin-top:2mm">{''.join(f'<tr><td style="width:18mm" class="cap">{n}<br><span class="tn">{s} · {ls}</span></td><td style="font-size:{px * 0.62:.1f}pt;font-weight:{w};letter-spacing:{ls};line-height:1.1;{"text-transform:uppercase" if n == "Label" else ""};padding:1.6mm 0">Every entity in view</td></tr>' for n, s, w, ls, px in scale)}</table>
    <p class="cap" style="margin-top:2mm">Print: Display 36–48 pt · H1 26 pt · Body 9–10 pt / 1.5. Max line length 72 characters. Sentence case for headings; caps only for labels.</p>
  </div>
</div>''', 'white', toc='Typography — English')

# ================================================================= 23 TYPE AR
page('04 · Typography', 'Typography — Arabic', f'''
<div class="c g12">
  <div style="grid-column:1/6">
    <div class="eb">Typeface · Arabic</div><h1 style="font-size:40pt">Myriad Arabic</h1>
    <div class="ar" style="font-size:22pt;color:#0F7C74;margin-top:2mm;text-align:left">مايرى عربي</div>
    <p style="margin-top:4mm">The approved Arabic typeface is <b>Myriad Arabic</b> (Adobe; PostScript family <span class="tn">MyriadArabic-*</span>). Its humanist sans construction pairs with Instrument Sans in stroke contrast, openness and colour on the page.</p>
    <ul class="clean" style="margin-top:4mm"><li>Arabic runs right-to-left; layouts mirror, numerals and brand names stay LTR.</li><li>Set Arabic ~ 1.15 × the Latin size for equal optical weight; line height 1.6.</li>
      <li>Never letter-space Arabic; never apply faux bold or italic.</li><li>Use Western digits (0–9) in financial UI for global consistency; Eastern Arabic digits only on user locale request.</li></ul>
    {PROXY_NOTE}
  </div>
  <div style="grid-column:7/13" dir="rtl">
    <div class="ar" style="font-size:30pt;line-height:1.35;font-weight:600;color:#022329">رؤية مالية واحدة لكل كيان وكل عملية.</div>
    <div class="ar" style="font-size:12.5pt;line-height:1.7;color:#4A5E61;margin-top:4mm">نظام وصول المالي هو نظام تشغيل مالي عالمي يمنح المؤسسات الحديثة رؤية موحدة وتنفيذًا منضبطًا لعملياتها المالية، عبر جميع الكيانات والعملات والبنوك.</div>
    <div style="margin-top:6mm;display:grid;grid-template-columns:1fr 1fr;gap:3mm">
      {''.join(f'<div class="panel" style="padding:3mm;background:#F3F5F2"><div class="ar" style="font-size:13pt;font-weight:600">{a}</div><div class="cap" style="direction:ltr;text-align:left">{b}</div></div>' for a, b in (('التحكم', 'Control'), ('الوضوح', 'Clarity'), ('التدفق', 'Flow'), ('الذكاء', 'Intelligence')))}
    </div>
    <div class="panel" style="margin-top:5mm;padding:3mm 4mm;background:#022329;color:#F3F5F2;display:flex;justify-content:space-between;align-items:center">
      <span class="ar" style="font-size:11pt">الرصيد النقدي للمجموعة</span><span class="tn" style="direction:ltr;font-size:13pt;font-weight:600">48,612,480.25 USD</span></div>
  </div>
</div>''', 'white', toc='Typography — Arabic')

# ================================================================= 24 FINANCIAL TYPOGRAPHY
fin_rows = [('Operating cash', '12,480,920.40', '11,902,114.75', '+4.9%'), ('Accounts receivable', '8,204,117.60', '8,466,002.10', '−3.1%'),
            ('Accounts payable', '(5,318,950.00)', '(4,980,221.38)', '+6.8%'), ('FX revaluation', '(114,208.93)', '42,881.00', '—'),
            ('Net position', '15,251,879.07', '15,430,776.47', '−1.2%')]
fin = ''.join(f'<tr style="{"font-weight:600;border-top:.4mm solid #022329" if n == "Net position" else ""}"><td>{n}</td><td class="tn" style="text-align:right">{a}</td><td class="tn" style="text-align:right;color:#4A5E61">{b}</td>'
              f'<td class="tn" style="text-align:right;color:{"#B4232F" if d.startswith("−") else "#0F7C74" if d.startswith("+") else "#80918F"}">{d}</td></tr>' for n, a, b, d in fin_rows)
page('04 · Typography', 'Financial typography', f'''
<div class="c g12">
  <div style="grid-column:1/6">
    <div class="eb">Numbers are the brand</div><h1>Financial typography</h1>
    <ul class="clean" style="margin-top:5mm">
      <li><b>Tabular lining figures</b> (<span class="tn">font-feature-settings: "tnum", "lnum"</span>) in every table, KPI, statement and chart axis.</li>
      <li><b>Right-align</b> numeric columns on the decimal; fixed decimals per currency (USD 2 · OMR 3 · JPY 0).</li>
      <li><b>Negatives</b> in parentheses in statements; a true minus (−, U+2212) in UI deltas. Colour is never the only signal.</li>
      <li><b>Currency</b> as ISO code after the amount (<span class="tn">48,612,480.25 USD</span>); symbols only in local consumer contexts.</li>
      <li><b>Percentages</b> with one decimal and a thin space before % in print; sign always shown for change (+4.9 %).</li>
      <li><b>Large values</b> abbreviate only in charts and tiles (48.6M), never in ledgers.</li>
      <li><b>Hierarchy:</b> KPI values SemiBold, labels Regular in Slate 600, units in Slate 400.</li></ul>
  </div>
  <div style="grid-column:6/13">
    <div class="panel" style="padding:5mm 6mm;background:#fff">
      <div class="row" style="gap:6mm">
        {''.join(f'<div style="flex:1"><div class="cap">{a}</div><div class="tn" style="font-size:19pt;font-weight:600;letter-spacing:-.01em;margin-top:1mm">{b}<span style="font-size:7pt;color:#80918F;font-weight:400"> {u}</span></div><div class="tn" style="font-size:7pt;color:{c}">{d}</div></div>' for a, b, u, c, d in (("Cash position", "48.61M", "USD", "#0F7C74", "▲ +2.4 %  vs last month"), ("Days sales outstanding", "41.2", "days", "#B4232F", "▼ −1.8 days  (lower is better)"), ("Approval SLA", "96.4 %", "", "#80918F", "Target 95 %")))}
      </div>
      <table class="spec" style="margin-top:6mm"><tr><th>Position · USD</th><th style="text-align:right">Q3 2026</th><th style="text-align:right">Q2 2026</th><th style="text-align:right">Δ</th></tr>{fin}</table>
      <div class="row" style="margin-top:5mm;gap:3mm">
        <div style="flex:1" class="cap"><b style="color:#B4232F">Proportional figures</b><div style="font-size:12pt;color:#022329;margin-top:1mm;font-variant-numeric:proportional-nums">1,111.11<br>9,999.99</div></div>
        <div style="flex:1" class="cap"><b style="color:#0F7C74">Tabular figures</b><div class="tn" style="font-size:12pt;color:#022329;margin-top:1mm">1,111.11<br>9,999.99</div></div>
        <div style="flex:2" class="cap">Tabular figures give every digit the same advance width so columns align and values don't jitter when they update live.</div>
      </div>
    </div>
  </div>
</div>''', toc='Financial typography')

# ================================================================= 25 GRAPHIC LANGUAGE
els = [('Fields', 'graphic-system/preview/WFS_Field_Ambient_Dark_preview.png', 'Soft light fields in teal on dark or mint on off-white.'),
       ('Rings', 'graphic-system/preview/WFS_Field_Construction_Rings_Dark_preview.png', 'The 20 construction circles as hairline structure.'),
       ('Cropped icon', 'graphic-system/preview/WFS_Field_Aperture_Crop_Dark_preview.png', 'The icon at architectural scale, cropped by the frame.'),
       ('Trajectories', 'graphic-system/preview/WFS_Field_Glint_Dark_preview.png', 'Lit blade edges as controlled lines of light.'),
       ('Grid & nodes', 'graphic-system/preview/WFS_Field_Grid_Nodes_Dark_preview.png', 'Structured grid with five axes and system nodes.'),
       ('Convergence', 'graphic-system/preview/WFS_Pattern_02_Financial_Convergence_Dark_preview.png', 'Blade edges rotated into one aperture.')]
page('05 · Graphic language', 'Graphic language', f'''
<div class="c"><div class="eb">Graphic language</div><h1>Everything comes from the icon</h1>
<p style="width:210mm;margin-top:3mm">The graphic system is built from the icon's own geometry — its circles, edges and aperture — so WFS is recognisable without the logo. Use one element per composition, at low contrast, and let content lead.</p>
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:5mm;margin-top:6mm">{''.join(f'<div><div style="height:50mm;border-radius:2mm;background:url({A}/{p}) center/cover"></div><h3 style="margin-top:2mm">{a}</h3><p style="font-size:7pt">{b}</p></div>' for a, p, b in els)}</div></div>''', 'white', toc='Graphic language')

# ================================================================= 26 PATTERNS
pats = [('Pattern 01 — Unified Field', 'WFS_Pattern_01_Unified_Field', 'The icon\'s construction circles, extended as a field of near-concentric rings. Covers, presentation grounds, website sections.'),
        ('Pattern 02 — Financial Convergence', 'WFS_Pattern_02_Financial_Convergence', '40 blade edges rotated around the aperture. Launch graphics, event screens, hero moments.'),
        ('Pattern 03 — Structured Orbit', 'WFS_Pattern_03_Structured_Orbit', 'Orbits on a base grid with five axes and nodes. Data, analytics and technical contexts.')]
page('05 · Graphic language', 'Patterns', f'''
<div class="c"><div class="eb">Patterns</div><h1>Three brand patterns</h1>
<div class="row" style="margin-top:6mm;gap:5mm">{''.join(f'<div style="flex:1"><div style="height:62mm;border-radius:2mm;background:url({A}/graphic-system/preview/WFS_{f[4:]}_Dark_preview.png) center/cover"></div><div style="height:44mm;border-radius:2mm;margin-top:2.5mm;background:url({A}/graphic-system/preview/WFS_{f[4:]}_Light_preview.png) center/cover;border:.2mm solid #D6DEDB"></div><h3 style="margin-top:2.5mm">{a}</h3><p style="font-size:7pt">{b}</p></div>' for a, f, b in pats)}</div>
<p class="cap" style="margin-top:4mm">Editable SVG (dark, light, seamless tiles for 01 and 03) in brand/graphic-system/patterns. Line weight 1–1.5 px at 1920 px width; opacity 10–35 %.</p></div>''', toc='Patterns')

# ================================================================= 27 ICONOGRAPHY
ic_grid = ''.join(f'<div style="display:flex;flex-direction:column;align-items:center;gap:1mm"><div style="width:11mm;height:11mm;border-radius:1.8mm;background:#fff;border:.2mm solid #E3E9E7;display:flex;align-items:center;justify-content:center">{icon(k, 22, "#022329")}</div><span class="cap" style="font-size:5.4pt">{k.replace("_", " ")}</span></div>' for k in U.ICON_SET)
construct = ('<svg viewBox="-2 -2 28 28" style="width:52mm">' + ''.join(f'<line x1="{i}" y1="0" x2="{i}" y2="24" stroke="#E3E9E7" stroke-width=".06"/><line x1="0" y1="{i}" x2="24" y2="{i}" stroke="#E3E9E7" stroke-width=".06"/>' for i in range(25))
             + '<rect x="2" y="2" width="20" height="20" fill="none" stroke="#7FE3D6" stroke-width=".12" stroke-dasharray=".4 .3"/><circle cx="12" cy="12" r="10" fill="none" stroke="#7FE3D6" stroke-width=".12" stroke-dasharray=".4 .3"/>'
             + f'<g fill="none" stroke="#022329" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">{C.ICONS["ledger"]}</g></svg>')
page('05 · Graphic language', 'Iconography', f'''
<div class="c g12">
  <div style="grid-column:1/5"><div class="eb">Product iconography</div><h1>Quiet, precise, outline-first</h1><p class="cap" style="margin-top:1mm">52-icon core set · extend using the same grid and stroke.</p>
    <p style="margin-top:4mm">UI icons are functional and deliberately quieter than the brand icon: outline, geometric, one weight. They never reuse the aperture mark or blade shapes.</p>
    <div style="margin-top:4mm">{construct}</div>
    <table class="spec" style="margin-top:2mm"><tr><td>Grid</td><td class="tn">24 × 24 px · 2 px padding · live area 20 px</td></tr><tr><td>Stroke</td><td class="tn">1.5 px · round caps & joins</td></tr>
      <tr><td>Corners</td><td class="tn">1–2 px radius on rectangles</td></tr><tr><td>Sizes</td><td class="tn">16 · 20 · 24 px (stroke 1.5 at all)</td></tr><tr><td>Colour</td><td>Slate 400 idle · Teal 700 active · text colour in content</td></tr></table>
  </div>
  <div style="grid-column:6/13"><div style="display:grid;grid-template-columns:repeat(9,1fr);gap:2.6mm 2mm;margin-top:2mm">{ic_grid}</div>
    <p class="cap" style="margin-top:5mm">No coins, dollar signs, piggy banks, bank columns, trading candles or AI sparkles — actions and objects only (receive, pay, approve, reconcile, report).</p></div>
</div>''', toc='Iconography')

# ================================================================= 28 IMAGERY
page('05 · Graphic language', 'Imagery direction', f'''
<div class="c g12">
  <div style="grid-column:1/4"><div class="eb">Imagery</div><h1>Precision, not stock clichés</h1>
    <h3 style="margin-top:5mm">Choose</h3><ul class="clean" style="margin-top:1mm"><li>Architectural precision, light and structure</li><li>Global infrastructure and networks</li><li>Macro materials — glass, anodised metal, stone</li><li>Real WFS product UI as the hero</li></ul>
    <h3 style="margin-top:4mm">Avoid</h3><ul class="clean" style="margin-top:1mm"><li>Handshakes, stock office teams, pointing at screens</li><li>Coins, calculators, cards, bank buildings</li><li>Trading charts, crypto, AI robots or sparkles</li><li>Region-specific landmarks as brand imagery</li></ul>
    <p class="cap" style="margin-top:3mm">Grade: cool, low-saturation, teal-shifted shadows, controlled highlights. The frames shown are procedural art-direction renders, not photography — commission or license imagery to these criteria.</p></div>
  <div style="grid-column:4/13;display:grid;grid-template-columns:1.3fr 1fr;grid-template-rows:1fr 1fr;gap:4mm;height:160mm">
    <div class="yes" style="grid-row:1/3;border-radius:2mm;background:url(img/art_architecture.jpg) center/cover"><span class="tag" style="position:absolute;left:3mm;bottom:3mm">Architectural precision</span></div>
    <div class="yes" style="border-radius:2mm;background:url(img/art_network.jpg) center/cover"><span class="tag" style="position:absolute;left:3mm;bottom:3mm">Global network</span></div>
    <div class="row" style="gap:4mm"><div class="yes" style="flex:1;border-radius:2mm;background:url(img/art_material.jpg) center/cover"><span class="tag" style="position:absolute;left:3mm;bottom:3mm">Macro material</span></div>
      <div class="yes" style="flex:1;border-radius:2mm;overflow:hidden;background:#022329">{mock(C.dashboard("dark"), 1440, 900, 62, shadow=False)}<span class="tag" style="position:absolute;left:3mm;bottom:3mm">Product UI</span></div></div>
  </div>
</div>''', toc='Imagery')

# ================================================================= 29 MOTION
def motion_frames():
    labels = [('0 ms', 'Fields'), ('240 ms', 'Converge'), ('520 ms', 'Align'), ('760 ms', 'Lock'), ('1 100 ms', 'One view')]
    out = ''
    for k, (tms, lab) in enumerate(labels):
        t = [0, .45, .8, 1, 1][k]
        g = ''
        for j, b in enumerate(L.BLADES):
            ang = 72 * j + 20; off = (1 - t) ** 1.5 * 360; rot = (1 - t) * 90
            dx, dy = off * math.cos(math.radians(ang)), off * math.sin(math.radians(ang))
            g += f'<path transform="translate({dx:.1f} {dy:.1f}) rotate({rot:.1f})" d="{L.ICON["blades"][b]["paths"]["gap20" if k < 3 else "solid"]}" fill="{P["reverse"]["blades"][j]}" fill-opacity="{0.35 + 0.65 * t:.2f}"/>'
        wm = f'<g transform="translate(560 -115) scale(.23)">{L.wordmark_paths("#F3F5F2", ids=False)}</g>' if k == 4 else ''
        out += (f'<div style="flex:{1.6 if k == 4 else 1}"><div style="height:46mm;border-radius:2mm;background:#0E3D42;display:flex;align-items:center;justify-content:center">'
                f'<svg viewBox="{-700} -700 {1400 + (1200 if k == 4 else 0)} 1400" style="height:40mm">{g}{wm}</svg></div>'
                f'<div class="row" style="justify-content:space-between;margin-top:1.5mm"><span style="font-size:7pt;font-weight:600;color:#7FE3D6">{lab}</span><span class="cap tn">{tms}</span></div></div>')
    return out
page('06 · Motion', 'Motion language', f'''
<div class="c"><div class="eb">Motion</div><h1>Converge · Align · Lock</h1>
<p style="width:210mm;margin-top:3mm">Motion shows many financial fields becoming one view. It is controlled and precise — never bouncy, never chaotic. Blades travel along their own arcs, align to the aperture and lock with a short settle.</p>
<div class="row" style="margin-top:6mm;gap:3mm">{motion_frames()}</div>
<div class="row" style="margin-top:6mm;gap:6mm">
  <table class="spec" style="flex:1.3"><tr><th>Token</th><th>Value</th><th>Use</th></tr>
    <tr><td>wfs-ease-standard</td><td class="tn">cubic-bezier(0.2, 0, 0, 1)</td><td>UI transitions, panels, charts</td></tr>
    <tr><td>wfs-ease-converge</td><td class="tn">cubic-bezier(0.65, 0, 0.35, 1)</td><td>Logo formation, field convergence</td></tr>
    <tr><td>wfs-ease-lock</td><td class="tn">cubic-bezier(0.3, 1.2, 0.4, 1) · ≤ 4 % overshoot</td><td>The lock moment only</td></tr>
    <tr><td>Durations</td><td class="tn">120 · 200 · 320 ms UI · 1 100 ms logo reveal</td><td>Never exceed 1.4 s</td></tr></table>
  <div style="flex:1"><h3 style="color:#7FE3D6">Principles</h3><ul class="clean" style="margin-top:1mm"><li>Rotation only around the aperture centre.</li><li>One movement at a time; stagger 40 ms per blade.</li><li>Ring rotation for loading: 360° / 2.4 s linear.</li><li>Respect prefers-reduced-motion: cross-fade only.</li></ul>
  <p class="cap" style="margin-top:2mm">Reference prototype: brand/motion/WFS_Logo_Reveal.html (SVG + CSS, no dependencies).</p></div>
</div></div>''', 'dark', toc='Motion')

# ================================================================= UI SYSTEM (new chapter)
def kit_page(title, h1, body_html, intro, theme='white'):
    page('07 · UI system', title, f'''<div class="c"><div class="row" style="justify-content:space-between;align-items:flex-end"><div><div class="eb">UI system</div><h1>{h1}</h1></div>
<p style="width:125mm">{intro}</p></div><div style="margin-top:5mm;display:flex;justify-content:center">{body_html}</div></div>''', theme, toc=title)
kit_page('Buttons', 'Buttons & actions', mock(U.ui_buttons('light'), 1400, 560, 240, radius=2.5),
         'One Primary Teal action per view. Secondary for alternatives, Tertiary for low emphasis, Dark for confirmations on light surfaces, Danger only for destructive steps. Radius 10 px, heights 32 · 40 · 48, focus ring 2 px Teal with 2 px offset.')
kit_page('Forms & controls', 'Forms, selection & navigation', mock(U.ui_forms('light'), 1400, 470, 240, radius=2.5),
         'Inputs are 42 px with a 1.5 px border; focus adds a Mint 100 halo, errors use Negative with a message — never colour alone. Amounts and codes use tabular figures. Status chips always pair colour with a label.')
kit_page('Feedback', 'Feedback, dialogs & states', mock(U.ui_feedback('light'), 1400, 480, 240, radius=2.5),
         'Alerts carry an icon, a title and one sentence. Toasts confirm and offer Undo. Dialogs state the consequence and the amount. Loading uses skeletons and the rotating one-colour icon; empty states are calm and actionable.')
kit_page('Data tables', 'Data tables', mock(U.ui_table('light'), 1400, 520, 240, radius=2.5),
         'Tables are the core surface of WFS: 48 px rows, uppercase 11.5 px headers, right-aligned tabular amounts, negatives in parentheses, references in Teal 700, status as labelled chips, bulk selection tinted Mint 100.')
page('07 · UI system', 'UI system — dark', f'''<div class="c"><div class="eb">UI system</div><h1>Dark theme components</h1>
<div class="row" style="margin-top:5mm;gap:5mm"><div>{mock(U.ui_buttons('dark'), 1400, 560, 132, radius=2)}</div><div>{mock(U.ui_forms('dark'), 1400, 470, 132, radius=2)}</div></div>
<div class="row" style="margin-top:5mm;gap:5mm"><div>{mock(U.ui_feedback('dark'), 1400, 480, 132, radius=2)}</div><div>{mock(U.ui_table('dark'), 1400, 520, 132, radius=2)}</div></div></div>''', 'dark', toc='UI system — dark')

# ================================================================= 30 APP ICON
def components(theme):
    t = C.TH[theme]
    btn = lambda bg, fg, txt, bd='transparent': f'<span style="font-size:7pt;font-weight:600;padding:1.8mm 3.4mm;border-radius:1.6mm;background:{bg};color:{fg};border:.25mm solid {bd}">{txt}</span>'
    chip = lambda bg, fg, txt: f'<span style="font-size:6.2pt;padding:.8mm 2.2mm;border-radius:5mm;background:{bg};color:{fg}">{txt}</span>'
    return (f'<div style="flex:1;border-radius:2mm;padding:3.5mm 4mm;background:{t["bg"]};border:.2mm solid {t["line"]};display:flex;gap:3mm;align-items:center;flex-wrap:wrap">'
            + btn('#14B8A6', '#022329', 'Approve batch') + btn(t['surface'], t['text'], 'Reconcile', t['line']) + btn('transparent', t['accent'], 'View ledger')
            + f'<span style="font-size:7pt;padding:1.6mm 3mm;border-radius:1.6mm;background:{t["surface"]};border:.25mm solid #14B8A6;color:{t["text"]};width:34mm" class="tn">48,612,480.25</span>'
            + chip(t['chip'], t['accent'], 'Posted') + chip('#FBEAD8' if theme == 'light' else '#3A2A14', '#B7791F' if theme == 'light' else '#E7B25B', 'Pending') + chip('#F7E1E3' if theme == 'light' else '#3A1A1E', t['neg'], 'Overdue') + '</div>')

def squircle(src, size_mm, radius='22.4%'):
    return f'<img src="{A}/{src}" style="width:{size_mm}mm;height:{size_mm}mm;border-radius:{radius};display:block;box-shadow:0 .6mm 2mm rgba(2,35,41,.25)">'
page('08 · Applications', 'App icon', f'''
<div class="c g12">
  <div style="grid-column:1/5"><div class="eb">App icon</div><h1>Deep field, luminous aperture</h1>
    <p style="margin-top:4mm">The app icon places the inverse icon on the Deep gradient with a soft ambient field. The master is a full-bleed 1024 px square — platforms apply their own masks; never bake corners into production files.</p>
    <table class="spec" style="margin-top:4mm"><tr><td>Master</td><td class="tn">1024 × 1024 · icon Ø 600 (58.6 %)</td></tr><tr><td>Exports</td><td class="tn">1024 · 512 · 256 · 128 · 64 · 48 · 32 · 16</td></tr>
      <tr><td>≤ 64 px</td><td>Compact artwork: flat ground, icon Ø 78 %</td></tr><tr><td>Android</td><td class="tn">Adaptive foreground / background / themed monochrome (108 dp)</td></tr>
      <tr><td>Variants</td><td>Dark (default) · Light · Premium (store & marketing)</td></tr></table></div>
  <div style="grid-column:5/13">
    <div class="row" style="gap:7mm;align-items:flex-end;margin-top:6mm">
      <div style="text-align:center">{squircle("icon/app/WFS_AppIcon_Dark_1024.png", 54)}<div class="cap" style="margin-top:2mm">iOS / iPadOS mask</div></div>
      <div style="text-align:center">{squircle("icon/app/WFS_AppIcon_Premium_1024.png", 38)}<div class="cap" style="margin-top:2mm">Premium (store)</div></div>
      <div style="text-align:center">{squircle("icon/app/WFS_AppIcon_Dark_512.png", 28, "50%")}<div class="cap" style="margin-top:2mm">Android circle</div></div>
      <div style="text-align:center">{squircle("icon/app/WFS_AppIcon_Light_512.png", 28)}<div class="cap" style="margin-top:2mm">Light variant</div></div></div>
    <div class="row" style="gap:6mm;align-items:flex-end;margin-top:16mm">{''.join(f'<div style="text-align:center"><img src="{A}/icon/app/WFS_AppIcon_Dark_{s}.png" style="width:{s if s <= 64 else 64 * s / 128}px;height:{s if s <= 64 else 64 * s / 128}px;border-radius:22%;display:block"><div class="cap tn" style="margin-top:1.5mm">{s}</div></div>' for s in (128, 64, 48, 32, 16))}
      <div style="flex:1"></div>
      <div style="display:flex;gap:3mm;align-items:center;padding:3mm 4mm;border-radius:3mm;background:#DDE6E4"><div style="width:14mm;height:14mm;border-radius:50%;overflow:hidden;background:url({A}/icon/app/WFS_Android_Adaptive_background_432.png) center/cover"><img src="{A}/icon/app/WFS_Android_Adaptive_foreground_432.png" style="width:100%"></div>
        <div style="width:14mm;height:14mm;border-radius:50%;background:#394a4d;overflow:hidden"><img src="{A}/icon/app/WFS_Android_Adaptive_monochrome_432.png" style="width:100%"></div><span class="cap">Adaptive<br>+ themed</span></div></div>
  </div>
</div>''', 'white', toc='App icon')

# ================================================================= 31 DESKTOP PRODUCT
page('08 · Applications', 'Digital product — executive dashboard', f'''
<div class="c"><div class="row" style="justify-content:space-between;align-items:flex-end"><div><div class="eb">Digital product</div><h1>The product is the hero</h1></div>
<p style="width:120mm">Executive financial dashboard: multi-entity scope, tabular figures, one teal action, data palette in fixed order, WFS Dark sidebar mark. The brand is present through restraint.</p></div>
<div style="margin-top:6mm;display:flex;justify-content:center">{mock(C.dashboard("light"), 1440, 900, 238, radius=2.5)}</div></div>''', toc='Digital product')

# ================================================================= PRODUCT SCREENS (new)
def screen_page(title, h1, html_, intro):
    page('08 · Applications', title, f'''<div class="c"><div class="row" style="justify-content:space-between;align-items:flex-end"><div><div class="eb">Product screens</div><h1>{h1}</h1></div>
<p style="width:120mm">{intro}</p></div><div style="margin-top:5mm;display:flex;justify-content:center">{mock(html_, 1440, 900, 232, radius=2.5)}</div></div>''', toc=title)
screen_page('Screen — Approvals', 'Approvals with control', U.screen_approvals('light'), 'Four-eyes approvals: queue on the left, the decision on the right with the full approval chain, amount in tabular figures and one Teal action.')
screen_page('Screen — Treasury', 'Treasury in one view', U.screen_treasury('dark'), 'Consolidated cash across banks and currencies, exposure bar in the data palette, live FX, bank connections — shown in the dark theme.')
page('08 · Applications', 'Screens — reports & mobile', f'''<div class="c"><div class="eb">Product screens</div><h1>Reports & mobile</h1>
<div class="row" style="margin-top:5mm;gap:5mm;align-items:flex-start"><div>{mock(U.screen_reports('light'), 1440, 900, 158, radius=2)}<div class="cap" style="margin-top:2mm">Report library — cards with icon, cadence and trend.</div></div>
<div>{mock(C.phone(U.mobile_approvals()), 418, 872, 44, radius=7, shadow=False)}<div class="cap" style="margin-top:2mm">Mobile approvals</div></div>
<div>{mock(C.phone(U.push_notification()), 418, 872, 44, radius=7, shadow=False)}<div class="cap" style="margin-top:2mm">Push notification</div></div></div></div>''', toc='Screens — reports & mobile')

# ================================================================= 32 LOGIN + MOBILE
page('08 · Applications', 'Login, launch & mobile', f'''
<div class="c"><div class="eb">Launch & access</div><h1>First impressions</h1>
<div class="row" style="margin-top:6mm;gap:6mm;align-items:flex-start">
  <div>{mock(C.login(), 1440, 900, 166, radius=2)}<div class="cap" style="margin-top:2mm">Web sign-in: convergence field, positioning line, off-white form panel.</div></div>
  <div>{mock(C.phone(C.splash()), 418, 872, 44, radius=7, shadow=False)}<div class="cap" style="margin-top:2mm">Mobile splash</div></div>
  <div>{mock(C.phone(C.mobile_home()), 418, 872, 44, radius=7, shadow=False)}<div class="cap" style="margin-top:2mm">Mobile · today</div></div>
</div></div>''', toc='Login, launch & mobile')

# ================================================================= 33 LIGHT / DARK
page('08 · Applications', 'Light & dark usage', f'''
<div class="c"><div class="eb">Light & dark</div><h1>Two modes, one system</h1>
<div class="row" style="margin-top:5mm;gap:5mm">
  <div style="flex:1">{mock(C.dashboard("light"), 1440, 900, 132, radius=2)}<h3 style="margin-top:2.5mm">Light mode</h3><p style="font-size:7pt">Off-White ground, white surfaces, WFS Dark text, Teal 700 for text accents, Primary logo.</p></div>
  <div style="flex:1">{mock(C.dashboard("dark"), 1440, 900, 132, radius=2)}<h3 style="margin-top:2.5mm">Dark mode</h3><p style="font-size:7pt">WFS Dark ground, Deep-tinted surfaces, Off-White text, Mint for text accents, Inverse logo. Data colours step up for the dark surface.</p></div>
</div>
<div class="row" style="margin-top:4mm;gap:5mm">{components("light")}{components("dark")}</div></div>''', toc='Light & dark usage')

# ================================================================= TECH USES (new)
page('08 · Applications', 'Developer portal', f'''<div class="c"><div class="row" style="justify-content:space-between;align-items:flex-end"><div><div class="eb">Technical applications</div><h1>Developer portal & API</h1></div>
<p style="width:125mm">Docs use the light theme with a WFS Dark code panel. Code is set in the system monospace; keys in Mint, values in Warning amber. Resource names, amounts and ISO codes are documented exactly as the API returns them.</p></div>
<div style="margin-top:5mm;display:flex;justify-content:center">{mock(U.dev_portal(), 1440, 900, 232, radius=2.5)}</div></div>''', toc='Developer portal')
page('08 · Applications', 'System communications', f'''<div class="c"><div class="eb">Technical applications</div><h1>System communications</h1>
<div class="row" style="margin-top:5mm;gap:5mm;align-items:flex-start">
  <div>{mock(U.email_notification(), 720, 860, 78, radius=2)}<div class="cap" style="margin-top:2mm">Transactional email</div></div>
  <div style="flex:1;display:flex;flex-direction:column;gap:5mm">{mock(U.status_page(), 1200, 760, 176, radius=2)}<div class="cap">Status page</div>
  <div class="row" style="gap:5mm">{mock(U.empty_404(), 1200, 760, 86, radius=2)}<p class="cap" style="flex:1">Error pages keep the brand calm and helpful: Deep ground, the Convergence pattern, a plain sentence and a clear way back.</p></div></div>
</div></div>''', 'white', toc='System communications')

# ================================================================= 34 REPORTS
page('08 · Applications', 'Reports & documents', f'''
<div class="c g12">
  <div style="grid-column:1/4"><div class="eb">Reports & documents</div><h1>Authority on paper</h1>
    <p style="margin-top:4mm">Covers use the Deep ground with the Unified Field; inside pages are white with a quiet header, tabular statements and a controlled footer carrying generation metadata.</p>
    <table class="spec" style="margin-top:4mm"><tr><td>Header</td><td>Primary lockup 18 px · report title in caps label</td></tr><tr><td>Body</td><td class="tn">Instrument Sans 9.5 / 14 pt</td></tr><tr><td>Tables</td><td>Tabular figures · negatives in ( ) · subtotals SemiBold</td></tr><tr><td>Footer</td><td>Source, snapshot ID, confidentiality, page x of y</td></tr></table></div>
  <div style="grid-column:4/13;display:flex;gap:6mm;justify-content:flex-end;align-items:flex-start;margin-top:0">
    {mock(C.report_cover(), 794, 1123, 94, radius=1)}{mock(C.report_page(), 794, 1123, 94, radius=1)}
  </div>
</div>''', 'white', toc='Reports & documents')

# ================================================================= 35 MARKETING I
page('08 · Applications', 'Marketing — web & presentation', f'''
<div class="c"><div class="eb">Marketing applications</div><h1>Web hero & presentation</h1>
<div class="row" style="margin-top:5mm;gap:5mm">
  <div>{mock(C.website(), 1440, 900, 165, radius=2)}<h3 style="margin-top:2.5mm">Website hero</h3><p style="font-size:7pt">Positioning headline, one primary CTA, product UI as proof.</p></div>
  <div style="flex:1;display:flex;flex-direction:column;gap:2mm">{mock(C.slide(), 1920, 1080, 98, radius=2)}<h3>Presentation · title</h3>{mock(C.slide_content(), 1920, 1080, 98, radius=2)}<h3>Presentation · content</h3></div>
</div></div>''', toc='Marketing — web & presentation')

# ================================================================= 36 MARKETING II
page('08 · Applications', 'Marketing — social, announcement, event', f'''
<div class="c"><div class="eb">Marketing applications</div><h1>Launch, social & event</h1>
<div class="row" style="margin-top:5mm;gap:5mm;align-items:flex-start">
  <div>{mock(C.social(), 1080, 1080, 78, radius=2)}<h3 style="margin-top:2mm">Social / launch 1:1</h3></div>
  <div>{mock(C.announcement(), 1200, 1500, 62, radius=2)}<h3 style="margin-top:2mm">Product announcement 4:5</h3></div>
  <div style="flex:1">{mock(C.event_screen(), 1920, 1080, 115, radius=2)}<h3 style="margin-top:2mm">Event / keynote screen</h3><p style="font-size:7pt">Premium lockup on the Convergence pattern; black stage, teal ambient spill.</p></div>
</div>
<div class="row" style="margin-top:5mm;gap:5mm;align-items:flex-start">
  <div>{mock(C.banner(), 1584, 396, 150, radius=1.5)}<h3 style="margin-top:2mm">LinkedIn / social cover 4:1</h3></div>
  <div style="flex:1">{mock(C.email_header(), 1200, 400, 109, radius=1.5)}<h3 style="margin-top:2mm">Product update email header 3:1</h3></div>
</div></div>''', toc='Marketing — social, announcement, event')

# ================================================================= SOCIAL MEDIA (new chapter)
feed = [U.sm_quote(), U.sm_stat(), U.sm_carousel(0), U.sm_carousel(3), U.sm_avatar(1080, 1080), U.sm_carousel(1)]
feed_html = ''.join(mock(f_, 1080, 1080 if i in (0, 1, 4) else 1350, 41, radius=0, shadow=False) if i in (0, 1, 4) else f'<div style="width:41mm;height:41mm;overflow:hidden">{mock(f_, 1080, 1350, 41, radius=0, shadow=False)}</div>' for i, f_ in enumerate(feed))
page('09 · Social media', 'Social media system', f'''<div class="c g12">
  <div style="grid-column:1/6"><div class="eb">Social media</div><h1>One feed,<br>one field</h1>
    <p style="margin-top:4mm">Every post is built from the same four parts: a ground (Deep or Off-White), one graphic element from the icon, one message, the lockup. Alternate dark and light to give the grid rhythm.</p>
    <table class="spec" style="margin-top:4mm"><tr><th>Pillar</th><th>Content</th><th>Ground</th></tr>
      <tr><td>Product</td><td>launches, features, screens</td><td>Deep + Convergence</td></tr><tr><td>Proof</td><td>numbers, customer quotes</td><td>Off-White + Aperture crop</td></tr>
      <tr><td>Perspective</td><td>finance leadership insight</td><td>Deep + Unified Field</td></tr><tr><td>Company</td><td>events, hiring, partners</td><td>Either · endorsement allowed</td></tr></table>
    <table class="spec" style="margin-top:4mm"><tr><th>Rule</th><th>Value</th></tr><tr><td>Margins / safe zone</td><td class="tn">7.8 % of width (84 px on 1080)</td></tr>
      <tr><td>Headline</td><td class="tn">Instrument Sans SemiBold 66–100 px · −0.035 em</td></tr><tr><td>Label</td><td class="tn">SemiBold 22–26 px caps · +0.16 em · Mint / Teal 700</td></tr>
      <tr><td>Lockup</td><td class="tn">bottom-left, 32–44 px high</td></tr><tr><td>Copy</td><td>≤ 12 words on image; details go in the caption</td></tr></table></div>
  <div style="grid-column:7/13;display:flex;justify-content:center;align-items:center"><div style="display:grid;grid-template-columns:repeat(3,41mm);gap:1.2mm;padding:3mm;background:#fff;border-radius:3mm;box-shadow:0 1mm 4mm rgba(2,35,41,.15)">{feed_html}</div></div>
</div>''', toc='Social media system')
page('09 · Social media', 'Social templates — posts & stories', f'''<div class="c"><div class="eb">Social media</div><h1>Carousel & story</h1>
<div class="row" style="margin-top:5mm;gap:3.5mm;align-items:flex-start">
{''.join(f'<div>{mock(U.sm_carousel(i), 1080, 1350, 52, radius=1.5)}<div class="cap" style="margin-top:1.5mm">Carousel {i+1}/4 · 1080×1350</div></div>' for i in range(4))}
<div>{mock(U.sm_story(), 1080, 1920, 36.5, radius=1.5)}<div class="cap" style="margin-top:1.5mm">Story · 1080×1920</div></div></div>
<p class="cap" style="margin-top:4mm">Carousels open and close on Deep grounds with a pattern; middle slides are Off-White with product proof. Keep the top 14 % and bottom 20 % of stories free of text (platform UI).</p></div>''', toc='Social templates — posts & stories')
page('09 · Social media', 'Social templates — channels', f'''<div class="c"><div class="eb">Social media</div><h1>Channel formats</h1>
<div class="row" style="margin-top:5mm;gap:5mm;align-items:flex-start">
  <div style="display:flex;flex-direction:column;gap:2mm">{mock(U.sm_linkedin(), 1200, 627, 118, radius=1.5)}<div class="cap">LinkedIn link post · 1200×627</div>{mock(U.sm_youtube(), 1280, 720, 118, radius=1.5)}<div class="cap">YouTube thumbnail · 1280×720</div></div>
  <div style="flex:1;display:flex;flex-direction:column;gap:2mm">{mock(U.sm_x_header(), 1500, 500, 144, radius=1.5)}<div class="cap">X / Twitter header · 1500×500</div>
    {mock(C.banner(), 1584, 396, 144, radius=1.5)}<div class="cap">LinkedIn cover · 1584×396</div>
    <div class="row" style="gap:5mm;align-items:center;margin-top:2mm">{mock(U.sm_avatar(), 800, 800, 30, radius=15, shadow=False)}{mock(U.sm_avatar(theme='light'), 800, 800, 30, radius=15, shadow=False)}<p class="cap" style="flex:1">Profile avatars: icon only, centred at 60 % inside the circular crop; Premium on Deep (default) or Primary on Off-White.</p></div></div>
</div></div>''', toc='Social templates — channels')

# ================================================================= 37 ENDORSEMENT
page('10 · Architecture', 'WUSOOL Tech endorsement', f'''
<div class="c g12">
  <div style="grid-column:1/5"><div class="eb">Brand architecture</div><h1>A WUSOOL Tech Product</h1>
    <p style="margin-top:4mm">WFS is an independent product brand created by WUSOOL Tech. The endorsement adds provenance in corporate, investor and partner contexts; it is never part of the primary logo and never borrows WUSOOL Investment styling.</p>
    <ul class="clean" style="margin-top:4mm"><li><b>Use:</b> investor decks, partner agreements, press releases, footers, sign-in pages, splash screens.</li>
      <li><b>Don't use:</b> in-product navigation, app icons, favicons, social avatars.</li>
      <li><b>Forms:</b> "A WUSOOL Tech Product" (preferred) · "WFS by WUSOOL Tech" (running text).</li>
      <li>Endorsement text: Instrument Sans Medium caps, tracking 0.12 em, Slate 600 / Mist 300, divided by a hairline.</li></ul></div>
  <div style="grid-column:5/13;display:flex;flex-direction:column;gap:5mm">
    <div class="panel" style="height:40mm;background:#fff;border:.2mm solid #E3E9E7;display:flex;align-items:center;justify-content:center">{img("logo/svg/WFS_Logo_Endorsed_Primary.svg", "width:118mm")}</div>
    <div class="panel" style="height:40mm;background:#022329;display:flex;align-items:center;justify-content:center">{img("logo/svg/WFS_Logo_Endorsed_Inverse.svg", "width:118mm")}</div>
    <div class="row" style="gap:5mm;align-items:center">{mock(C.business_card(True), 1050, 600, 66, radius=1.5)}{mock(C.business_card(False), 1050, 600, 66, radius=1.5)}<p class="cap" style="flex:1">Business card (85 × 55 mm): included only as a reference for the endorsement footer. WFS remains digital-first.</p></div>
  </div>
</div>''', toc='WUSOOL Tech endorsement')

# ================================================================= 38 VOICE
msgs = [('One financial view.', 'رؤية مالية واحدة.'), ('One financial truth.', 'حقيقة مالية واحدة.'), ('Global by design.', 'عالمي بالتصميم.'),
        ('Powerful on its own. Connected when you need it.', 'قوي بذاته. ومتصل عندما تحتاج.'), ('One financial system. Every operation in view.', 'نظام مالي واحد. كل عملية أمامك بوضوح.')]
page('10 · Architecture', 'Brand voice & messaging', f'''
<div class="c g12">
  <div style="grid-column:1/6"><div class="eb">Positioning statement</div>
    <p class="lead" style="font-size:16pt;line-height:1.32;margin-top:3mm;letter-spacing:-.012em">WFS is a global financial operating system designed to give modern organisations a unified view and controlled execution of their financial operations.</p>
    <div class="ar" style="font-size:13pt;line-height:1.7;color:#0F7C74;margin-top:4mm">نظام وصول المالي نظام تشغيل مالي عالمي يمنح المؤسسات الحديثة رؤية موحدة وتنفيذًا منضبطًا لعملياتها المالية.</div>
    <h3 style="margin-top:6mm">Voice</h3>
    <table class="spec" style="margin-top:1mm"><tr><th>We are</th><th>We are not</th></tr><tr><td>Precise — numbers, specifics, verbs</td><td>Vague, hyped, "revolutionary"</td></tr>
      <tr><td>Calm and assured</td><td>Loud, urgent, fearful</td></tr><tr><td>Global and plain-spoken</td><td>Local idiom, jargon, acronyms unexplained</td></tr><tr><td>About control and clarity</td><td>About speculation, returns, "AI magic"</td></tr></table></div>
  <div style="grid-column:7/13"><div class="eb">Messaging directions</div>
    {''.join(f'<div style="border-top:.25mm solid #D6DEDB;padding:2.6mm 0"><div style="font-size:13pt;font-weight:600;letter-spacing:-.01em">{a}</div><div class="ar" style="font-size:11pt;color:#0F7C74;margin-top:1mm">{b}</div></div>' for a, b in msgs)}
    <p class="cap" style="margin-top:3mm">These are messaging directions, not a fixed tagline. Recommended option for the primary tagline: <b style="color:#022329">"One financial system. Every operation in view."</b> — to be confirmed by WUSOOL Tech leadership.</p>
    {PROXY_NOTE if not AR_NATIVE else ''}</div>
</div>''', toc='Brand voice & messaging')

# ================================================================= 39 ASSET LIBRARY
tree = '''brand/
├─ guidelines/   WFS_Brand_Guidelines_2026.pdf · source/
├─ logo/         svg · pdf · png · ai (see README) · preview
├─ icon/         svg · pdf · png · app · favicon
├─ wordmark/     svg · pdf · png · ai (see README)
├─ graphic-system/ patterns · fields · gradients · backgrounds
├─ color/        tokens (CSS · JSON · SCSS) · swatches (ASE · GPL)
├─ typography/   README.md
├─ motion/       WFS_Logo_Reveal.html
├─ templates/    slide · report · social · email signature
├─ source/       vector masters · build scripts · references
└─ WFS_BRAND_ASSET_INDEX.md'''
TREE = [('guidelines/', 'WFS_Brand_Guidelines_2026.pdf · source/ (HTML + build) · preview/'), ('logo/', 'svg · pdf · png · ai (README) · preview'),
        ('icon/', 'svg · pdf · png · app · favicon'), ('wordmark/', 'svg · pdf · png · ai (README)'), ('graphic-system/', 'patterns · fields · gradients · backgrounds · preview'),
        ('color/', 'tokens (CSS · SCSS · JSON) · swatches (ASE · GPL)'), ('typography/', 'README.md — fonts, weights, scale, numerals'), ('motion/', 'WFS_Logo_Reveal.html · motion tokens'),
        ('templates/', 'presentation · report · social (15 formats) · email · signature (HTML, PDF, PNG)'), ('source/', 'vector masters · build scripts · approved references'), ('WFS_BRAND_ASSET_INDEX.md', 'every file: purpose · format · variant · colour · background')]
USE = [('Website, product UI', 'SVG'), ('Word, PowerPoint, Google', 'PNG 2048 · or PDF'), ('Professional print', 'PDF (vector) · proof colour'), ('Social avatar', 'Icon PNG on WFS Dark / App icon'),
       ('Favicon / PWA', 'icon/favicon set + head-snippet.html'), ('Video, keynote, events', 'Premium PNG 4096 · SVG'), ('Signage, embroidery', 'One-colour PDF / SVG')]
page('11 · Assets', 'Asset library', f'''
<div class="c g12">
  <div style="grid-column:1/6"><div class="eb">Asset library</div><h1>Files & naming</h1>
    <table class="spec" style="margin-top:5mm">{"".join(f'<tr><td style="width:34mm;font-weight:600;color:#022329">{a}</td><td>{b}</td></tr>' for a, b in TREE)}</table></div>
  <div style="grid-column:7/13">
    <h3>Naming</h3><p class="tn" style="margin-top:1mm">WFS_[Asset]_[Layout]_[Colourway]_[size]px.[ext] — e.g. WFS_Logo_Horizontal_Inverse_2048px.png</p>
    <table class="spec" style="margin-top:4mm"><tr><th>Format</th><th>Use</th></tr>
      <tr><td>SVG</td><td>Master artwork: web, product, and editing (vector, outlined, no embedded images)</td></tr>
      <tr><td>PDF</td><td>Print & Office; vector, opens as editable paths in Illustrator</td></tr>
      <tr><td>PNG</td><td>Transparent raster at 512 / 1024 / 2048 / 4096 px where useful</td></tr>
      <tr><td>AI</td><td>Native .ai requires Adobe Illustrator — run source/illustrator/export_ai.jsx to convert the SVG masters; no renamed files are shipped</td></tr>
      <tr><td>ICO / webmanifest</td><td>Favicon and PWA integration</td></tr></table>
    <p class="cap" style="margin-top:4mm">The full index with purpose, variant, colourway and background compatibility of every file: brand/WFS_BRAND_ASSET_INDEX.md. Fonts are referenced, not redistributed (see typography/README.md).</p>
    <h3 style="margin-top:6mm">Which file do I use?</h3><table class="spec" style="margin-top:1mm">{"".join(f'<tr><td style="width:48mm">{a}</td><td style="color:#0F7C74">{b}</td></tr>' for a, b in USE)}</table></div>
</div>''', 'white', toc='Asset library')

# ================================================================= 40 PRINCIPLES / BACK
princ = [('Unity', 'One field, one truth. Design every touchpoint as part of the same system.'), ('Control', 'Measured geometry, measured words. Nothing accidental.'),
         ('Clarity', 'Structure first. Remove before adding.'), ('Precision', 'Tabular numbers, exact alignment, honest data.'),
         ('Global scale', 'Neutral in geography, fluent in every market.'), ('Intelligence', 'Insight that is earned, never decorative.')]
page('11 · Assets', 'Brand principles', f'''
<img src="{A}/graphic-system/fields/WFS_Overlay_Convergence_OnDark.svg" style="position:absolute;left:110mm;top:-10mm;width:300mm;opacity:1">
<img src="{A}/icon/svg/WFS_Icon_Premium.svg" style="position:absolute;left:212mm;top:58mm;width:112mm">
<div class="c"><div class="eb">Final brand principles</div><h1 class="xl" style="width:160mm">Every operation in view.</h1>
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:4mm 6mm;margin-top:10mm;width:190mm">{''.join(f'<div style="border-top:.25mm solid #1E4A4F;padding-top:2.5mm"><h3 style="color:#7FE3D6">{a}</h3><p style="font-size:7pt;margin-top:1mm">{b}</p></div>' for a, b in princ)}</div>
<div style="position:absolute;left:0;bottom:0">{img("logo/svg/WFS_Logo_Endorsed_Inverse.svg", "height:13mm")}</div></div>''', 'deep', toc='Brand principles')

# ================================================================= CONTENTS fill
toc_items = ''.join(f'<div style="display:flex;gap:3mm;padding:1.25mm 0;border-top:.2mm solid #E3E9E7;font-size:7.2pt"><span class="tn" style="width:7mm;color:#0F7C74;font-weight:600">{n:02d}</span><span style="flex:1">{t}</span><span class="cap">{c}</span></div>' for n, c, t in TOC)
contents = f'''<div class="c g12">
  <div style="grid-column:1/6"><div class="eb">Brand overview</div><h1>WFS — Wusool Financial System</h1>
    <div class="ar" style="font-size:16pt;color:#0F7C74;margin-top:2mm;text-align:left">نظام وصول المالي</div>
    <p class="lead" style="margin-top:6mm">A global financial operating system that gives modern organisations a unified view and controlled execution of their financial operations.</p>
    <p style="margin-top:4mm">These guidelines define version 1.0 of the WFS identity: the approved icon and wordmark rebuilt as precise vector masters, the Concept A colour family, Instrument Sans and Myriad Arabic typography, and a graphic language derived entirely from the icon. They are written for product, marketing and partner teams — and for anyone building with WFS.</p>
    <div class="row" style="margin-top:7mm;gap:4mm">{''.join(f'<div style="flex:1;border-top:.3mm solid #022329;padding-top:2mm"><div class="tn" style="font-size:16pt;font-weight:600">{a}</div><div class="cap">{b}</div></div>' for a, b in (('5', 'core colours'), ('20', 'construction circles'), ('3', 'brand patterns'), ('1', 'financial view')))}</div></div>
  <div style="grid-column:7/13"><div class="eb">Contents</div><div style="margin-top:2mm;column-count:2;column-gap:6mm">{toc_items}</div></div>
</div>'''
PAGES[CONTENTS_SLOT] = PAGES[CONTENTS_SLOT].replace('%CONTENTS%', contents)

# symbols not present in Instrument Sans are drawn as inline SVG glyphs (no fallback fonts)
def _g(vb, body, w='.9em', h='.7em', va='-.02em'):
    return f'<svg viewBox="{vb}" style="display:inline-block;width:{w};height:{h};vertical-align:{va};overflow:visible" aria-hidden="true">{body}</svg>'
_st = 'fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"'
GLYPHS = {
    '→': _g('0 0 16 10', f'<path {_st} d="M1.5 5h12.5M10.5 1.5L14 5l-3.5 3.5"/>'),
    '●': _g('0 0 10 10', '<circle cx="5" cy="5" r="4" fill="currentColor"/>', '.55em', '.55em', '.02em'),
    '▲': _g('0 0 10 10', '<path d="M5 1.5L9 8.5H1z" fill="currentColor"/>', '.6em', '.6em', '0'),
    '▼': _g('0 0 10 10', '<path d="M1 1.5h8L5 8.5z" fill="currentColor"/>', '.6em', '.6em', '0'),
    '≤': _g('0 0 10 12', f'<path {_st} d="M8.5 1.5L1.5 5l7 3.5M1.5 11h7"/>', '.62em', '.78em', '-.08em'),
    '≥': _g('0 0 10 12', f'<path {_st} d="M1.5 1.5L8.5 5l-7 3.5M1.5 11h7"/>', '.62em', '.78em', '-.08em'),
    '≈': _g('0 0 12 10', f'<path {_st} d="M1 3.5c2-2 3.5 0 5 0s3-2 5 0M1 7.5c2-2 3.5 0 5 0s3-2 5 0"/>', '.72em', '.62em', '.02em'),
    'ρ': _g('0 0 10 12', f'<path {_st} d="M2.6 11.5V6.2a3.1 3.1 0 1 1 3.1 3.1H2.6"/>', '.55em', '.72em', '-.2em'),
    'Δ': _g('0 0 10 10', f'<path {_st} d="M5 1.2L9 8.8H1z"/>', '.62em', '.62em', '0'),
}
def glyphs(h):
    parts = re.split(r'(<style>.*?</style>|<[^>]+>)', h, flags=re.S)
    out = []
    for p in parts:
        if p.startswith('<'): out.append(p); continue
        for k, v in GLYPHS.items(): p = p.replace(k, v)
        out.append(p)
    return ''.join(out)
PAGES = [glyphs(p) for p in PAGES]

html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>WFS Brand Guidelines {B.YEAR} — v{B.VERSION}</title>
<style>{font_faces()}{CSS}</style></head><body>{"".join(PAGES)}</body></html>'''
out_html = os.path.join(HERE, 'WFS_Brand_Guidelines.html')
open(out_html, 'w').write(html)
print('pages', len(PAGES), '| arabic font:', 'Myriad Arabic (native)' if AR_NATIVE else 'NOT FOUND -> labelled proxy')
if '--no-render' not in sys.argv:
    pdf = os.path.join(HERE, '..', 'WFS_Brand_Guidelines_2026.pdf')
    prev = os.path.join(HERE, '..', 'preview')
    src_dir = os.path.join(HERE, '..', '..', 'source')
    r = subprocess.run(['node', os.path.join(src_dir, 'render.mjs'), out_html, pdf, '--png', prev, '--scale', '1'], capture_output=True, text=True, cwd=src_dir)
    print(r.stdout[-3000:], r.stderr[-3000:])
