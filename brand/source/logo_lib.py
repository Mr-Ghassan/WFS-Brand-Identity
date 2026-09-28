"""WFS logo library: builds clean SVG markup for every icon / wordmark / lockup
variant from the vector masters (master/*.json) and brand_config colours."""
import json, os, io, re, glob
import numpy as np
import brand_config as B

HERE = os.path.dirname(os.path.abspath(__file__))
ICON = json.load(open(f'{HERE}/master/icon_geometry.json'))
WORD = json.load(open(f'{HERE}/master/wordmark_geometry.json'))
BLADES = ['B1', 'B2', 'B3', 'B4', 'B5']

def f(v):
    s = f'{v:.2f}'.rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s

def mix(a, b, t):
    """Blend hex a -> b by t (0..1)."""
    ra, rb = B.hex_rgb(a), B.hex_rgb(b)
    return '#' + ''.join(f'{int(round(x + (y - x) * t)):02X}' for x, y in zip(ra, rb))

# ----------------------------------------------------------------- measurement
def _raster_bbox(svg_inner, vb, px=4000):
    import cairosvg
    from PIL import Image
    x0, y0, w, h = vb
    s = px / max(w, h)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{int(w * s)}" height="{int(h * s)}" '
           f'viewBox="{x0} {y0} {w} {h}">{svg_inner}</svg>')
    a = np.array(Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode()))))[..., 3]
    ys, xs = np.nonzero(a > 8)
    return (x0 + xs.min() / s, y0 + ys.min() / s, x0 + (xs.max() + 1) / s, y0 + (ys.max() + 1) / s)

_cache = {}
def icon_bbox():
    if 'icon' not in _cache:
        inner = ''.join(f'<path d="{ICON["blades"][b]["paths"]["solid"]}"/>' for b in BLADES)
        _cache['icon'] = _raster_bbox(inner, (-600, -600, 1200, 1200))
    return _cache['icon']

def aperture_width():
    """Horizontal width of the central aperture (defines the clear-space unit)."""
    if 'ap' not in _cache:
        import cairosvg
        from PIL import Image
        inner = ''.join(f'<path d="{ICON["blades"][b]["paths"]["solid"]}"/>' for b in BLADES)
        s = 4
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{1200*s}" height="{1200*s}" viewBox="-600 -600 1200 1200">{inner}</svg>'
        a = np.array(Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode()))))[..., 3] > 128
        from scipy import ndimage as ndi
        lab, n = ndi.label(~a)
        hole = lab == lab[600 * s, 600 * s]
        ys, xs = np.nonzero(hole)
        _cache['ap'] = ((xs.max() - xs.min() + 1) / s, (ys.max() - ys.min() + 1) / s,
                        (xs.mean() / s - 600, ys.mean() / s - 600))
    return _cache['ap']

# ----------------------------------------------------------------- icon markup
def icon_paths(colours, variant='solid', ids=True):
    out = []
    for b, c in zip(BLADES, colours):
        idattr = f' id="blade-{b[1]}"' if ids else ''
        out.append(f'<path{idattr} fill="{c}" d="{ICON["blades"][b]["paths"][variant]}"/>')
    return ''.join(out)

def icon_mono(colour, variant=None):
    variant = variant or B.MONO_GAP
    return f'<g fill="{colour}">' + ''.join(f'<path d="{ICON["blades"][b]["paths"][variant]}"/>' for b in BLADES) + '</g>'

MONO_TONES = {
    'mono_dark':  ['#B8BDBC', '#7B8281', '#3E4443', '#7B8281', '#1B1F1F'],   # greyscale, light grounds
    'mono_light': ['#FFFFFF', '#CDD2D1', '#7F8786', '#CDD2D1', '#A3AAA9'],   # greyscale, dark grounds
}

def _blade_centroids():
    if 'cent' in _cache: return _cache['cent']
    import cairosvg
    from PIL import Image
    res = {}
    for b in BLADES:
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="600" height="600" viewBox="-600 -600 1200 1200">'
               f'<path d="{ICON["blades"][b]["paths"]["solid"]}"/></svg>')
        a = np.array(Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode()))))[..., 3] > 128
        ys, xs = np.nonzero(a)
        res[b] = (xs.mean() * 2 - 600, ys.mean() * 2 - 600)
    _cache['cent'] = res
    return res

PREMIUM_TONES = {
    # (outer/lit tone, inner/shaded tone) per blade — WFS palette only
    'dark':  {'B1': ('#D9F7F2', '#57C9BA'), 'B2': ('#8AE8DC', '#0F9E8F'), 'B3': ('#138A80', '#0C4447'),
              'B4': ('#6ADDCE', '#0F7C74'), 'B5': ('#1C7473', '#07343B')},
    'light': {'B1': ('#A9EDE3', '#43BEAE'), 'B2': ('#5FD9CA', '#0F8F82'), 'B3': ('#0F6E69', '#062E33'),
              'B4': ('#3FCDBC', '#0F7C74'), 'B5': ('#10474C', '#021A1F')},
}

def icon_premium(on='dark', uid='p'):
    """Premium display icon: same geometry, controlled gradients, layered edge light."""
    cen = _blade_centroids()
    tones = PREMIUM_TONES[on]
    defs = []; body = []
    for b in BLADES:
        cx, cy = cen[b]; r = np.hypot(cx, cy); ux, uy = cx / r, cy / r
        # outer (lit) -> inner along the blade's radial direction, biased toward the top-right light
        x1, y1 = ux * 520 + 120, uy * 520 - 120
        x2, y2 = ux * 180, uy * 180
        lit, shade = tones[b]
        defs.append(f'<linearGradient id="{uid}g{b}" gradientUnits="userSpaceOnUse" x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}">'
                    f'<stop offset="0" stop-color="{lit}"/><stop offset="1" stop-color="{shade}"/></linearGradient>')
        defs.append(f'<clipPath id="{uid}c{b}"><path d="{ICON["blades"][b]["paths"]["solid"]}"/></clipPath>')
        body.append(f'<path id="blade-{b[1]}" fill="url(#{uid}g{b})" d="{ICON["blades"][b]["paths"]["solid"]}"/>')
    # layered light: shade falls on the lower blade, a fine highlight runs along the upper blade's edge
    shade_col = '#06363A' if on == 'dark' else '#0E3D42'
    for key, e in ICON['edges'].items():
        a_, b_ = key.split('|'); upper = ICON['stacking'][key]; lower = b_ if upper == a_ else a_
        body.append(f'<g clip-path="url(#{uid}c{lower})" fill="none" stroke="{shade_col}" stroke-linecap="round">'
                    f'<path d="{e["d"]}" stroke-width="60" stroke-opacity="0.08"/>'
                    f'<path d="{e["d"]}" stroke-width="48" stroke-opacity="0.10"/>'
                    f'<path d="{e["d"]}" stroke-width="20" stroke-opacity="0.14"/></g>')
        body.append(f'<g clip-path="url(#{uid}c{upper})" fill="none" stroke="#EFFFFC" stroke-linecap="round">'
                    f'<path d="{e["d"]}" stroke-width="16" stroke-opacity="0.10"/>'
                    f'<path d="{e["d"]}" stroke-width="5" stroke-opacity="{0.60 if on == "dark" else 0.45}"/></g>')
    # soft key light from the top-right
    defs.append(f'<radialGradient id="{uid}key" gradientUnits="userSpaceOnUse" cx="260" cy="-300" r="620">'
                f'<stop offset="0" stop-color="#FFFFFF" stop-opacity="0.22"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></radialGradient>')
    defs.append(f'<clipPath id="{uid}all">' + ''.join(f'<path d="{ICON["blades"][b]["paths"]["solid"]}"/>' for b in BLADES) + '</clipPath>')
    body.append(f'<rect clip-path="url(#{uid}all)" x="-600" y="-600" width="1200" height="1200" fill="url(#{uid}key)"/>')
    return f'<defs>{"".join(defs)}</defs>' + ''.join(body)

# ----------------------------------------------------------------- wordmark markup
def wordmark_paths(colour, ids=True):
    paths = []
    for k, v in WORD['letters'].items():
        idattr = f' id="letter-{k}"' if ids else ''
        paths.append(f'<path{idattr} d="{v["d"]}"/>')
    return f'<g fill="{colour}">' + ''.join(paths) + '</g>'

def wordmark_premium(on='light', uid='w'):
    W = WORD['width']
    d_all = ' '.join(v['d'] for v in WORD['letters'].values())
    if on == 'light':
        stops = [('#0E3D42', 0), ('#022329', 0.55), ('#0B3237', 1)]; hl = '#7FE3D6'; hlo = 0.85
    else:
        stops = [('#FFFFFF', 0), ('#DDF5F1', 0.55), ('#B9EFE7', 1)]; hl = '#14B8A6'; hlo = 0.55
    defs = (f'<defs><linearGradient id="{uid}g" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{f(W * 0.35)}" y2="1400">'
            + ''.join(f'<stop offset="{o}" stop-color="{c}"/>' for c, o in stops) + '</linearGradient>'
            f'<clipPath id="{uid}c"><path d="{d_all}"/></clipPath></defs>')
    folds = ''.join(f'<path d="{fo["d"]}"/>' for fo in WORD['folds'])
    return (defs + f'<path fill="url(#{uid}g)" d="{d_all}"/>'
            f'<g clip-path="url(#{uid}c)" fill="none" stroke="{hl}" stroke-linecap="round">'
            f'<g stroke-width="26" stroke-opacity="0.10">{folds}</g>'
            f'<g stroke-width="7" stroke-opacity="{hlo}">{folds}</g></g>')

# ----------------------------------------------------------------- text
_fonts = {}
def font(weight='Medium', script='latin'):
    from text_outline import Font
    key = (weight, script)
    if key not in _fonts:
        if script == 'arabic':
            cands = [p for p in glob.glob(os.path.join(B.font_dir(), '**', '*'), recursive=True)
                     if re.search(r'myriad.?arabic', os.path.basename(p), re.I) and re.search(weight.replace('SemiBold', 'Semi'), os.path.basename(p), re.I)]
            if not cands: return None
            _fonts[key] = Font(cands[0])
        else:
            _fonts[key] = Font(os.path.join(B.font_dir(), f'InstrumentSans-{weight}-latin.ttf'))
    return _fonts[key]

def arabic_font_available():
    return font('Regular', 'arabic') is not None

# ----------------------------------------------------------------- lockups
def _wm_block(scale, x, y, content):
    return f'<g transform="translate({f(x)} {f(y)}) scale({f(scale)})">{content}</g>'

def lockup(kind, icon_markup, wm_markup, text_colour=None, desc=True, endorse_colour=None):
    """Return (inner_svg, (x0, y0, w, h)) in icon units (D = 1000)."""
    bx0, by0, bx1, by1 = icon_bbox()
    W = WORD['width']
    parts = [f'<g id="icon">{icon_markup}</g>']
    if kind == 'horizontal':
        L = B.LOCKUP['horizontal']; cap = L['cap'] * 1000; s = cap / 1000
        x = bx1 + L['gap'] * 1000; y = -cap / 2
        parts.append(f'<g id="wordmark">{_wm_block(s, x, y, wm_markup)}</g>')
        box = (bx0, by0, x + W * s - bx0, by1 - by0)
    elif kind == 'full':
        L = B.LOCKUP['full']; cap = L['cap'] * 1000; s = cap / 1000
        fnt = font('Medium'); dcap = L['desc_cap'] * 1000; size = dcap / (fnt.cap / fnt.upm)
        text = B.NAME_EN.upper()
        _, adv0 = fnt.path(text, size)
        wm_w = W * s
        track = (wm_w - adv0) / (len(text) - 1) / size   # justify descriptor to wordmark width
        block_h = cap + L['desc_gap'] * 1000 + dcap
        x = bx1 + L['gap'] * 1000; y = -block_h / 2
        d, adv = fnt.path(text, size, x=x, y=y + block_h, tracking=track)
        parts.append(f'<g id="wordmark">{_wm_block(s, x, y, wm_markup)}</g>')
        parts.append(f'<path id="descriptor" fill="{text_colour}" d="{d}"/>')
        box = (bx0, by0, x + max(wm_w, adv) - bx0, by1 - by0)
    elif kind == 'stacked':
        L = B.LOCKUP['stacked']; cap = L['cap'] * 1000; s = cap / 1000
        wm_w = W * s
        x = -wm_w / 2; y = by1 + L['gap'] * 1000
        parts.append(f'<g id="wordmark">{_wm_block(s, x, y, wm_markup)}</g>')
        x0 = min(bx0, x); x1 = max(bx1, x + wm_w)
        box = (x0, by0, x1 - x0, y + cap - by0)
    elif kind == 'bilingual':
        L = B.LOCKUP['full']; cap = L['cap'] * 1000; s = cap / 1000
        fe = font('Medium'); fa = font('Regular', 'arabic')
        dcap = L['desc_cap'] * 1000; size = dcap / (fe.cap / fe.upm)
        wm_w = W * s
        de, adv_e = fe.path(B.NAME_EN.upper(), size)
        track = (wm_w - adv_e) / (len(B.NAME_EN) - 1) / size
        asize = size * 1.25
        block_h = cap + L['desc_gap'] * 1000 + dcap + 0.16 * 1000 + dcap
        x = bx1 + L['gap'] * 1000; y = -block_h / 2
        de, adv_e = fe.path(B.NAME_EN.upper(), size, x=x, y=y + cap + L['desc_gap'] * 1000 + dcap, tracking=track)
        da, adv_a = fa.path(B.NAME_AR, asize, x=0, y=0)
        da, adv_a = fa.path(B.NAME_AR, asize, x=x + wm_w - adv_a, y=y + block_h)
        parts.append(f'<g id="wordmark">{_wm_block(s, x, y, wm_markup)}</g>')
        parts.append(f'<path id="descriptor-en" fill="{text_colour}" d="{de}"/>')
        parts.append(f'<path id="descriptor-ar" fill="{text_colour}" d="{da}"/>')
        box = (bx0, by0 - 40, x + wm_w - bx0, by1 - by0 + 80)
    else:
        raise ValueError(kind)
    if endorse_colour:
        # endorsement: hairline divider + "A WUSOOL TECH PRODUCT"
        fnt = font('Medium'); ecap = 0.085 * 1000; size = ecap / (fnt.cap / fnt.upm)
        gx = box[0] + box[2] + 0.30 * 1000
        rule_h = B.LOCKUP['horizontal']['cap'] * 1000
        parts.append(f'<rect id="endorsement-rule" fill="{endorse_colour}" x="{f(gx)}" y="{f(-rule_h / 2)}" width="6" height="{f(rule_h)}"/>')
        d1, a1 = fnt.path('A WUSOOL TECH', size, x=gx + 0.26 * 1000, y=-ecap * 0.35, tracking=0.12)
        d2, a2 = fnt.path('PRODUCT', size, x=gx + 0.26 * 1000, y=ecap * 1.35 + ecap * 0.35, tracking=0.12)
        parts.append(f'<path id="endorsement" fill="{endorse_colour}" d="{d1} {d2}"/>')
        box = (box[0], box[1], gx + 0.26 * 1000 + max(a1, a2) - box[0], box[3])
    return ''.join(parts), box

# ----------------------------------------------------------------- document
def svg_doc(inner, box, title, pad=0.0, width_px=None, desc=None):
    x0, y0, w, h = box
    x0 -= pad; y0 -= pad; w += 2 * pad; h += 2 * pad
    wpx = width_px or w; hpx = wpx * h / w
    d = f'<desc>{desc}</desc>' if desc else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{f(x0)} {f(y0)} {f(w)} {f(h)}" '
            f'width="{f(wpx)}" height="{f(hpx)}"><title>{title}</title>{d}{inner}</svg>\n')

def icon_box(pad_frac=0.01):
    bx0, by0, bx1, by1 = icon_bbox()
    p = (bx1 - bx0) * pad_frac
    return (bx0 - p, by0 - p, bx1 - bx0 + 2 * p, by1 - by0 + 2 * p)

def word_box(pad_frac=0.004):
    W = WORD['width']; p = 1000 * pad_frac * 2
    return (-p, -p, W + 2 * p, 1000 + 2 * p)
