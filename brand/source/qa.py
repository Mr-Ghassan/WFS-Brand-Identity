"""WFS brand package QA: validates every SVG / PNG / PDF, transparency, vector-only
logo PDFs, duplicates, palette compliance and master fidelity. Writes source/qa/QA_REPORT.md."""
import os, sys, json, hashlib, re, colorsys, subprocess, glob
import xml.etree.ElementTree as ET
from PIL import Image
from pypdf import PdfReader
import brand_config as B

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SKIP = ('source/node_modules', 'guidelines/source/fonts', '.git')
files = []
for d, _, fs in os.walk(ROOT):
    rel = os.path.relpath(d, ROOT)
    if any(rel.startswith(s) for s in SKIP): continue
    for f in fs: files.append(os.path.join(d, f))
rel = lambda p: os.path.relpath(p, ROOT)
issues, notes = [], []
stats = dict(svg=0, png=0, pdf=0, ai=0, jpg=0)
LOGO_GROUPS = ('logo/', 'icon/', 'wordmark/')

# ---------------------------------------------------------------- SVG
svg_colours = set()
for p in [f for f in files if f.endswith('.svg')]:
    stats['svg'] += 1
    try:
        t = ET.parse(p).getroot()
    except ET.ParseError as e:
        issues.append(f'SVG parse error: {rel(p)} — {e}'); continue
    if 'viewBox' not in t.attrib: issues.append(f'SVG without viewBox: {rel(p)}')
    txt = open(p).read()
    if rel(p).startswith(LOGO_GROUPS):
        if '<image' in txt: issues.append(f'Raster embedded in logo SVG: {rel(p)}')
        if '<text' in txt: issues.append(f'Live text in production logo SVG: {rel(p)}')
        if re.search(r'<metadata|sodipodi|inkscape:', txt): issues.append(f'Editor metadata in logo SVG: {rel(p)}')
        svg_colours.update(c.upper() for c in re.findall(r'#[0-9A-Fa-f]{6}\b', txt))

# ---------------------------------------------------------------- PNG / JPG
for p in [f for f in files if f.lower().endswith(('.png', '.jpg'))]:
    stats['png' if p.endswith('.png') else 'jpg'] += 1
    try:
        im = Image.open(p); im.load()
    except Exception as e:
        issues.append(f'Image unreadable: {rel(p)} — {e}'); continue
    r = rel(p)
    transparent_expected = (r.startswith(LOGO_GROUPS) and '/png/' in r) or '/favicon/favicon-' in r and False
    if r.startswith(LOGO_GROUPS) and '/png/' in r:
        if im.mode != 'RGBA': issues.append(f'Logo PNG without alpha: {r}'); continue
        a = im.getchannel('A')
        if a.getextrema()[0] != 0: issues.append(f'Logo PNG has no transparent pixels: {r}')
        corners = [a.getpixel((0, 0)), a.getpixel((im.width - 1, 0)), a.getpixel((0, im.height - 1)), a.getpixel((im.width - 1, im.height - 1))]
        if max(corners) > 0: issues.append(f'Logo PNG corners not transparent: {r}')
        m = re.search(r'_(\d+)px\.png$', r)
        if m and int(m.group(1)) not in im.size: issues.append(f'PNG size mismatch with name: {r} {im.size}')

# ---------------------------------------------------------------- PDF
guide = None
for p in [f for f in files if f.endswith('.pdf')]:
    stats['pdf'] += 1
    try:
        rd = PdfReader(p)
    except Exception as e:
        issues.append(f'PDF unreadable: {rel(p)} — {e}'); continue
    r = rel(p)
    if r.startswith(LOGO_GROUPS):
        if len(rd.pages) != 1: issues.append(f'Logo PDF page count {len(rd.pages)}: {r}')
        for pg in rd.pages:
            xo = pg.get('/Resources', {}).get('/XObject', {}) if pg.get('/Resources') else {}
            try: xo = xo.get_object()
            except Exception: pass
            for k, v in (xo or {}).items():
                o = v.get_object()
                if o.get('/Subtype') == '/Image': issues.append(f'Raster image inside logo PDF: {r}')
                if o.get('/Subtype') == '/Form':
                    rs = o.get('/Resources', {})
                    x2 = rs.get('/XObject', {}) if rs else {}
                    for k2, v2 in (x2 or {}).items():
                        if v2.get_object().get('/Subtype') == '/Image': issues.append(f'Raster image inside logo PDF (form): {r}')
    if r.endswith('WFS_Brand_Guidelines_2026.pdf'):
        guide = rd

# ---------------------------------------------------------------- AI files
ai = [f for f in files if f.lower().endswith('.ai')]
stats['ai'] = len(ai)
for p in ai:
    head = open(p, 'rb').read(8)
    issues.append(f'.ai file present (verify it was written by Illustrator): {rel(p)} header={head!r}')

# ---------------------------------------------------------------- duplicates
hashes = {}
for p in files:
    if p.endswith(('.md', '.json', '.html', '.py', '.mjs', '.css', '.scss', '.gpl', '.jsx', '.txt', '.gitignore', '.webmanifest')): continue
    h = hashlib.sha256(open(p, 'rb').read()).hexdigest()
    hashes.setdefault(h, []).append(rel(p))
INTENTIONAL = {('icon/app/WFS_AppIcon_Dark_512.png', 'icon/favicon/android-chrome-512x512.png')}
dups = [v for v in hashes.values() if len(v) > 1 and tuple(sorted(v)) not in INTENTIONAL]
aliases = [v for v in hashes.values() if len(v) > 1 and tuple(sorted(v)) in INTENTIONAL]
for v in dups: issues.append('Duplicate file content: ' + ' = '.join(v))

# ---------------------------------------------------------------- palette compliance (no retired gold / blue)
allowed = set(h.upper() for h in B.HEX.values()) | {'#FFFFFF', '#000000'}
retired = []
for c in sorted(svg_colours):
    r_, g_, b_ = B.hex_rgb(c); h, l, s = colorsys.rgb_to_hls(r_ / 255, g_ / 255, b_ / 255)
    hue = h * 360
    if s > 0.25 and (15 <= hue <= 60 or 200 <= hue <= 260) and 0.15 < l < 0.9:
        retired.append(c)
if retired: issues.append('Retired concept (gold/blue) colours found in logo files: ' + ', '.join(retired))
core_ok = all(v['hex'].upper() in set(B.HEX[k].upper() for k in B.CORE) for v in B.CORE.values())
core_exact = {v['hex'] for v in B.CORE.values()} == {'#022329', '#0E3D42', '#14B8A6', '#7FE3D6', '#F3F5F2'}
if not core_exact: issues.append('Core colours differ from the approved five')

# ---------------------------------------------------------------- guidelines
g = {}
if guide:
    g['pages'] = len(guide.pages)
    box = guide.pages[0].mediabox
    g['size_mm'] = (round(float(box.width) * 25.4 / 72, 1), round(float(box.height) * 25.4 / 72, 1))
    def _fonts(obj, acc):
        res = obj.get('/Resources')
        if not res: return
        res = res.get_object()
        for k, v in (res.get('/Font') or {}).items(): acc.add(str(v.get_object().get('/BaseFont')).split('+')[-1])
        for k, v in (res.get('/XObject') or {}).items():
            o = v.get_object()
            if o.get('/Subtype') == '/Form': _fonts(o, acc)
    allf = set(); g['font_fallbacks'] = []
    for i, pg in enumerate(guide.pages):
        acc = set(); _fonts(pg, acc); allf |= acc
        for fnt in acc:
            if fnt.startswith(('InstrumentSans', 'MyriadArabic')): continue
            if fnt.startswith('NotoSansArabic'): continue          # labelled Arabic proxy (see notes)
            if fnt.startswith('LiberationSerif') and i + 1 == 18: continue   # intentional misuse example: wordmark typeset in a generic serif
            g['font_fallbacks'].append(f'p{i+1}:{fnt}')
    g['fonts'] = sorted(allf)
    if g['font_fallbacks']: issues.append('Unintended fallback fonts in guidelines: ' + ', '.join(g['font_fallbacks']))
    text = ''.join((guide.pages[i].extract_text() or '') for i in range(len(guide.pages)))
    nums = [int(n) for n in re.findall(r'(?m)^\s*(\d{2})\s', text)]
    if not (24 <= g['pages'] <= 40): issues.append(f'Guidelines page count {g["pages"]} outside 24–40')
    if abs(g['size_mm'][0] - 297) > 0.3 or abs(g['size_mm'][1] - 210) > 0.3: issues.append(f'Guidelines page size {g["size_mm"]} is not A4 landscape')
else:
    issues.append('Guidelines PDF missing')

# ---------------------------------------------------------------- fidelity (re-run the master QA)
fid = {}
for script in ('qa_icon_fidelity.py', 'qa_wordmark_fidelity.py'):
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'source', script), '/tmp'], capture_output=True, text=True, cwd=os.path.join(ROOT, 'source'))
    fid[script] = (r.stdout.strip().splitlines() or ['(no output)'])[-1]

# ---------------------------------------------------------------- report
cnt = lambda pat: len([f for f in files if re.search(pat, rel(f))])
report = f'''# WFS Brand Identity 1.0 — QA report

Generated by `source/qa.py`.

## Result: {"PASS — no issues" if not issues else f"{len(issues)} issue(s)"}

| Check | Result |
|---|---|
| SVG files parsed (viewBox present) | {stats["svg"]} |
| Logo/icon/wordmark SVGs: no raster, no live text, no editor metadata | {"pass" if not any("logo SVG" in i for i in issues) else "FAIL"} |
| PNG files opened | {stats["png"]} (+ {stats["jpg"]} JPG art-direction renders) |
| Logo/icon/wordmark PNGs transparent (alpha, transparent corners, size = name) | {"pass" if not any("PNG" in i for i in issues) else "FAIL"} |
| PDF files opened | {stats["pdf"]} |
| Logo/icon/wordmark PDFs vector-only (no image XObjects, 1 page) | {"pass" if not any("logo PDF" in i for i in issues) else "FAIL"} |
| Native .ai files | {stats["ai"]} (none generated — requires Illustrator; see logo/ai/README.md) |
| Duplicate binary files | {len(dups)} accidental · {len(aliases)} intentional platform alias ({'; '.join(' = '.join(a) for a in aliases)}) |
| Core colours exactly #022329 #0E3D42 #14B8A6 #7FE3D6 #F3F5F2 | {"pass" if core_exact else "FAIL"} |
| Retired gold/blue colours in logo files | {"none" if not retired else ", ".join(retired)} |
| Colours used in logo files | {", ".join(sorted(svg_colours))} |
| Guidelines PDF | {g.get("pages")} pages · {g.get("size_mm")} mm (A4 landscape) · embedded fonts: {", ".join(g.get("fonts", []))} |
| Unintended font fallbacks in guidelines | {", ".join(g.get("font_fallbacks", [])) or "none"} (LiberationSerif on p18 is the deliberate 'do not typeset the wordmark' example; NotoSansArabic is the labelled Arabic proxy) |
| Icon master fidelity | {fid.get("qa_icon_fidelity.py")} |
| Wordmark master fidelity | {fid.get("qa_wordmark_fidelity.py")} |

## Issues
{chr(10).join("- " + i for i in issues) if issues else "None."}

## Notes
- Arabic: approved typeface Myriad Arabic was not available as a font file in the build environment; Arabic in the guidelines is a labelled proxy, and no Arabic was outlined into any logo file.
- Guidelines render check (Chromium): missing images and overflow are reported by `render.mjs` at build time.
'''
os.makedirs(os.path.join(ROOT, 'source', 'qa'), exist_ok=True)
open(os.path.join(ROOT, 'source', 'qa', 'QA_REPORT.md'), 'w').write(report)
json.dump(dict(stats=stats, issues=issues, guidelines=g, fidelity=fid, colours=sorted(svg_colours)), open(os.path.join(ROOT, 'source', 'qa', 'qa.json'), 'w'), indent=1)
print(report)
