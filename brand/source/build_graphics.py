"""WFS graphic system: patterns, fields, gradients, backgrounds — all derived from
the icon's own geometry (construction circles, blade edges, aperture)."""
import os, json, math
import cairosvg
import brand_config as B
import logo_lib as L

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
GS = os.path.join(ROOT, 'graphic-system')
for d in ('patterns', 'fields', 'gradients', 'backgrounds'): os.makedirs(os.path.join(GS, d), exist_ok=True)
REC = []
f = L.f
EDGES = [e['d'] for e in L.ICON['edges'].values()]
CIRCLES = L.ICON['circles']
def _edge_len(e):
    import numpy as np
    return float(np.hypot(e['p1'][0] - e['p0'][0], e['p1'][1] - e['p0'][1])) + abs(np.hypot(*e['p0']) - np.hypot(*e['p1']))
LONG_EDGE = max(L.ICON['edges'].values(), key=lambda e: abs(__import__('math').hypot(*e['p0']) - __import__('math').hypot(*e['p1'])))['d']

def doc(w, h, inner, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
            f'<title>{title}</title>{inner}</svg>\n')

def write(sub, name, svg, purpose, png_w=None, variant='', bg=''):
    p = os.path.join(GS, sub, name + '.svg'); open(p, 'w').write(svg)
    files = [f'graphic-system/{sub}/{name}.svg']
    if png_w:
        cairosvg.svg2png(bytestring=svg.encode(), write_to=p[:-4] + '.png', output_width=png_w)
        files.append(f'graphic-system/{sub}/{name}.png')
    REC.append(dict(asset=name, group=f'graphic-system/{sub}', purpose=purpose, files=files, variant=variant, backgrounds=bg))

def ground(w, h, kind):
    if kind == 'dark':
        return (f'<defs><linearGradient id="gd" x1="0" y1="0" x2="0.4" y2="1"><stop offset="0" stop-color="#0E3D42"/>'
                f'<stop offset="1" stop-color="#022329"/></linearGradient></defs><rect width="{w}" height="{h}" fill="url(#gd)"/>')
    return f'<rect width="{w}" height="{h}" fill="#F3F5F2"/>'

INK = {'dark': ('#7FE3D6', '#14B8A6'), 'light': ('#0E3D42', '#14B8A6')}

# ---------------------------------------------------------------- Pattern 01 — Unified Field
def unified_field(w, h, kind, cx=None, cy=None, scale=None):
    """The icon's 20 construction circles, enlarged: many centres, one field."""
    cx = cx if cx is not None else w * 0.68; cy = cy if cy is not None else h * 0.5
    s = scale or (min(w, h) * 1.05 / 1000)
    a, b = INK[kind]
    rings = []
    for k, c in enumerate(CIRCLES):
        op = 0.34 if c['role'] in ('outer', 'aperture') else 0.16
        col = a if c['role'] == 'outer' else b
        rings.append(f'<circle cx="{f(c["centre"][0])}" cy="{f(c["centre"][1])}" r="{f(c["radius"])}" stroke="{col}" stroke-opacity="{op}"/>')
    # echo rings: the field extends beyond the mark
    for r in (620, 760, 920, 1100, 1320):
        rings.append(f'<circle cx="0" cy="0" r="{r}" stroke="{a}" stroke-opacity="{0.18 * 500 / r:.3f}"/>')
    return (f'<g fill="none" stroke-width="{f(1.2 / s)}" transform="translate({f(cx)} {f(cy)}) scale({s:.5f})">' + ''.join(rings) + '</g>')

def unified_tile(kind, t=240):
    a, b = INK[kind]
    circ = ''.join(f'<circle cx="{x}" cy="{y}" r="{t/2}"/>' for x, y in ((0, 0), (t, 0), (0, t), (t, t), (t/2, t/2)))
    inner = ''.join(f'<circle cx="{x}" cy="{y}" r="{t*0.2}"/>' for x, y in ((0, 0), (t, 0), (0, t), (t, t), (t/2, t/2)))
    bgc = '#022329' if kind == 'dark' else '#F3F5F2'
    return doc(t, t, f'<rect width="{t}" height="{t}" fill="{bgc}"/><g fill="none" stroke="{a}" stroke-opacity="0.22" stroke-width="1">{circ}</g>'
                     f'<g fill="none" stroke="{b}" stroke-opacity="0.35" stroke-width="1">{inner}</g>', 'WFS Pattern 01 — Unified Field (seamless tile)')

# ---------------------------------------------------------------- Pattern 02 — Financial Convergence
def convergence(w, h, kind, cx=None, cy=None, scale=None, n=40):
    """The icon's blade edges rotated around the aperture: many flows converge into one view."""
    cx = cx if cx is not None else w * 0.62; cy = cy if cy is not None else h * 0.52
    s = scale or (h * 1.0 / 1000)
    a, b = INK[kind]
    lines = []
    base = LONG_EDGE
    for k in range(n):
        ang = 360 * k / n
        op = 0.10 + 0.22 * (0.5 + 0.5 * math.cos(math.radians(ang - 35)))
        col = a if k % 5 else b
        lines.append(f'<path transform="rotate({ang:.2f})" d="{base}" stroke="{col}" stroke-opacity="{op:.3f}"/>')
    ap = f'<circle r="205" stroke="{b}" stroke-opacity="0.55" stroke-width="{f(2.0 / s)}"/>'
    cid = f'cv{kind}{int(cx)}{int(cy)}'
    clip = (f'<defs><clipPath id="{cid}"><path clip-rule="evenodd" d="M -3000 -3000 H 3000 V 3000 H -3000 Z '
            f'M 212 0 A 212 212 0 1 0 -212 0 A 212 212 0 1 0 212 0 Z"/></clipPath></defs>')
    return (f'<g fill="none" stroke-width="{f(1.1 / s)}" transform="translate({f(cx)} {f(cy)}) scale({s:.5f})">'
            + clip + f'<g clip-path="url(#{cid})">' + ''.join(lines) + '</g>' + ap + '</g>')

# ---------------------------------------------------------------- Pattern 03 — Structured Orbit
def orbit(w, h, kind, cx=None, cy=None, unit=None):
    """Orbits on a structured grid: 5 axes (one per blade), nodes where orbit meets axis."""
    cx = cx if cx is not None else w * 0.5; cy = cy if cy is not None else h * 0.5
    u = unit or min(w, h) / 14
    a, b = INK[kind]
    out = []
    # base grid
    g = u
    for x in range(0, int(w / g) + 2): out.append(f'<line x1="{f(x*g)}" y1="0" x2="{f(x*g)}" y2="{h}" stroke="{a}" stroke-opacity="0.06"/>')
    for y in range(0, int(h / g) + 2): out.append(f'<line x1="0" y1="{f(y*g)}" x2="{w}" y2="{f(y*g)}" stroke="{a}" stroke-opacity="0.06"/>')
    for k in range(1, 9):
        out.append(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(k*u)}" fill="none" stroke="{a}" stroke-opacity="{0.30 - k*0.025:.3f}"/>')
    for i in range(5):
        th = math.radians(-90 + 72 * i + 18)
        out.append(f'<line x1="{f(cx)}" y1="{f(cy)}" x2="{f(cx + math.cos(th)*9*u)}" y2="{f(cy + math.sin(th)*9*u)}" stroke="{a}" stroke-opacity="0.16"/>')
        for k in range(1, 9):
            if (k + i) % 3 == 0 or k == 8:
                x, y = cx + math.cos(th) * k * u, cy + math.sin(th) * k * u
                out.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(u*0.07)}" fill="{b}" fill-opacity="{0.9 if k < 8 else 0.5}"/>')
    out.append(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(u*0.12)}" fill="{b}"/>')
    return '<g stroke-width="1">' + ''.join(out) + '</g>'

def orbit_tile(kind, t=200):
    a, b = INK[kind]; bgc = '#022329' if kind == 'dark' else '#F3F5F2'
    inner = (f'<rect width="{t}" height="{t}" fill="{bgc}"/>'
             f'<g fill="none" stroke="{a}" stroke-width="1"><circle cx="0" cy="0" r="{t*0.5}" stroke-opacity="0.18"/>'
             f'<circle cx="{t}" cy="{t}" r="{t*0.5}" stroke-opacity="0.18"/><circle cx="0" cy="0" r="{t*0.25}" stroke-opacity="0.12"/>'
             f'<circle cx="{t}" cy="{t}" r="{t*0.25}" stroke-opacity="0.12"/></g>'
             f'<g fill="{b}"><circle cx="{t/2}" cy="{t/2}" r="2.2"/><circle cx="0" cy="{t}" r="2.2" fill-opacity="0.5"/>'
             f'<circle cx="{t}" cy="0" r="2.2" fill-opacity="0.5"/></g>')
    return doc(t, t, inner, 'WFS Pattern 03 — Structured Orbit (seamless tile)')

# ---------------------------------------------------------------- fields
def ambient(w, h, kind, cx=0.68, cy=0.42, r=0.75):
    if kind == 'dark':
        return (f'<defs><radialGradient id="amb" gradientUnits="userSpaceOnUse" cx="{w*cx}" cy="{h*cy}" r="{max(w,h)*r}">'
                f'<stop offset="0" stop-color="#14B8A6" stop-opacity="0.28"/><stop offset="0.45" stop-color="#0E3D42" stop-opacity="0.0"/></radialGradient></defs>'
                f'<rect width="{w}" height="{h}" fill="url(#amb)"/>')
    return (f'<defs><radialGradient id="amb" gradientUnits="userSpaceOnUse" cx="{w*cx}" cy="{h*cy}" r="{max(w,h)*r}">'
            f'<stop offset="0" stop-color="#7FE3D6" stop-opacity="0.35"/><stop offset="0.5" stop-color="#F3F5F2" stop-opacity="0"/></radialGradient></defs>'
            f'<rect width="{w}" height="{h}" fill="url(#amb)"/>')

def aperture_crop(w, h, kind, cx=None, cy=None, scale=None, opacity=None):
    """The icon at architectural scale, cropped by the frame."""
    cx = cx if cx is not None else w * 0.86; cy = cy if cy is not None else h * 0.5
    s = scale or (h * 1.25 / 1000)
    if kind == 'dark':
        body = f'<g opacity="{opacity or 0.16}">{L.icon_mono("#14B8A6", "gap12")}</g>'
    else:
        body = f'<g opacity="{opacity or 0.10}">{L.icon_mono("#0E3D42", "gap12")}</g>'
    return f'<g transform="translate({f(cx)} {f(cy)}) scale({s:.5f})">{body}</g>'

def glint(w, h, kind):
    """A single controlled light trajectory (the lit edge of a blade)."""
    s = h * 1.0 / 1000
    return (f'<defs><linearGradient id="gl" gradientUnits="userSpaceOnUse" x1="-500" y1="0" x2="500" y2="0">'
            f'<stop offset="0" stop-color="#7FE3D6" stop-opacity="0"/><stop offset="0.55" stop-color="#7FE3D6" stop-opacity="0.9"/>'
            f'<stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></linearGradient></defs>'
            f'<g transform="translate({f(w*0.62)} {f(h*0.5)}) scale({s:.5f})" fill="none" stroke="url(#gl)" stroke-linecap="round">'
            + ''.join(f'<path d="{e}" stroke-width="{f(2.2/s)}"/><path d="{e}" stroke-width="{f(16/s)}" stroke-opacity="0.10"/>' for e in EDGES) + '</g>')

def construction_lines(w, h, kind):
    return unified_field(w, h, kind, cx=w * 0.5, cy=h * 0.5, scale=min(w, h) * 0.7 / 1000)

# ---------------------------------------------------------------- gradients
def gradient_svg(key, w=1200, h=600):
    g = B.GRADIENTS[key]
    if g.get('kind') == 'radial':
        inner = (f'<rect width="{w}" height="{h}" fill="{g["base"]}"/><defs><radialGradient id="g" cx="0.68" cy="0.4" r="0.8">'
                 + ''.join(f'<stop offset="{o/100}" stop-color="{c}" stop-opacity="{a}"/>' for c, o, a in g['stops'])
                 + f'</radialGradient></defs><rect width="{w}" height="{h}" fill="url(#g)"/>')
    else:
        a = math.radians(g['angle'])
        dx, dy = math.sin(a), -math.cos(a)            # CSS angle convention
        x1, y1, x2, y2 = 0.5 - dx / 2, 0.5 - dy / 2, 0.5 + dx / 2, 0.5 + dy / 2
        inner = (f'<defs><linearGradient id="g" x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}">'
                 + ''.join(f'<stop offset="{o/100}" stop-color="{c}"/>' for c, o in g['stops'])
                 + f'</linearGradient></defs><rect width="{w}" height="{h}" fill="url(#g)"/>')
    return doc(w, h, inner, f'WFS {g["name"]}')

def gradients_css():
    out = ['/* WFS Brand Identity v1.0 — gradient system */', ':root {']
    for k, g in B.GRADIENTS.items():
        if g.get('kind') == 'radial':
            stops = ', '.join(f'rgba({",".join(str(x) for x in B.hex_rgb(c))},{a}) {o}%' for c, o, a in g['stops'])
            out.append(f'  --wfs-gradient-{k}: radial-gradient(120% 90% at 68% 40%, {stops}), {g["base"]};')
        else:
            stops = ', '.join(f'{c} {o}%' for c, o in g['stops'])
            out.append(f'  --wfs-gradient-{k}: linear-gradient({g["angle"]}deg, {stops});')
    out.append('}')
    return '\n'.join(out) + '\n'

# ---------------------------------------------------------------- build
if __name__ == '__main__':
    W, H = 1920, 1080
    for kind in ('dark', 'light'):
        K = kind.capitalize()
        write('patterns', f'WFS_Pattern_01_Unified_Field_{K}', doc(W, H, ground(W, H, kind) + ambient(W, H, kind) + unified_field(W, H, kind), f'WFS Pattern 01 — Unified Field ({kind})'),
              'Presentation / cover / web section background', 1920, kind, kind)
        write('patterns', f'WFS_Pattern_01_Unified_Field_Tile_{K}', unified_tile(kind), 'Seamless repeat tile (240 px)', 480, kind, kind)
        write('patterns', f'WFS_Pattern_02_Financial_Convergence_{K}', doc(W, H, ground(W, H, kind) + ambient(W, H, kind, 0.62, 0.52, 0.5) + convergence(W, H, kind), f'WFS Pattern 02 — Financial Convergence ({kind})'),
              'Launch graphics, event screens, report covers', 1920, kind, kind)
        write('patterns', f'WFS_Pattern_03_Structured_Orbit_{K}', doc(W, H, ground(W, H, kind) + orbit(W, H, kind, cx=W * 0.7), f'WFS Pattern 03 — Structured Orbit ({kind})'),
              'Data / analytics contexts, dashboards, section dividers', 1920, kind, kind)
        write('patterns', f'WFS_Pattern_03_Structured_Orbit_Tile_{K}', orbit_tile(kind), 'Seamless repeat tile (200 px)', 400, kind, kind)
        # fields
        write('fields', f'WFS_Field_Ambient_{K}', doc(W, H, ground(W, H, kind) + ambient(W, H, kind), f'WFS Field — Ambient ({kind})'), 'Soft light field behind hero content', 1920, kind, kind)
        write('fields', f'WFS_Field_Aperture_Crop_{K}', doc(W, H, ground(W, H, kind) + ambient(W, H, kind) + aperture_crop(W, H, kind), f'WFS Field — Aperture crop ({kind})'), 'Cropped icon geometry at architectural scale', 1920, kind, kind)
        write('fields', f'WFS_Field_Construction_Rings_{K}', doc(W, H, ground(W, H, kind) + construction_lines(W, H, kind), f'WFS Field — Construction rings ({kind})'), 'Line structure from the icon construction circles', 1920, kind, kind)
        write('fields', f'WFS_Field_Glint_{K}', doc(W, H, ground(W, H, kind) + glint(W, H, kind), f'WFS Field — Glint trajectory ({kind})'), 'Controlled light effect (lit blade edge)', 1920, kind, kind)
        write('fields', f'WFS_Field_Grid_Nodes_{K}', doc(W, H, ground(W, H, kind) + orbit(W, H, kind, cx=W * 0.5, unit=H / 9), f'WFS Field — Grid + nodes ({kind})'), 'Structured grid with system nodes', 1920, kind, kind)
    # transparent overlays (no ground) for compositing
    write('fields', 'WFS_Overlay_Unified_Field_OnDark', doc(W, H, unified_field(W, H, 'dark'), 'WFS overlay — Unified Field for dark grounds (transparent)'), 'Transparent overlay', 1920, 'overlay', 'dark')
    write('fields', 'WFS_Overlay_Convergence_OnDark', doc(W, H, convergence(W, H, 'dark'), 'WFS overlay — Convergence for dark grounds (transparent)'), 'Transparent overlay', 1920, 'overlay', 'dark')
    write('fields', 'WFS_Overlay_Aperture_Crop_OnLight', doc(W, H, aperture_crop(W, H, 'light'), 'WFS overlay — Aperture crop for light grounds (transparent)'), 'Transparent overlay', 1920, 'overlay', 'light')
    # gradients
    for k in B.GRADIENTS:
        write('gradients', f'WFS_Gradient_{k.capitalize()}', gradient_svg(k), B.GRADIENTS[k]['use'], 1200, k, '')
    open(os.path.join(GS, 'gradients', 'wfs-gradients.css'), 'w').write(gradients_css())
    # backgrounds (ready-to-use compositions)
    comps = [
        ('WFS_Background_16x9_Dark_Field', 1920, 1080, lambda w, h: ground(w, h, 'dark') + ambient(w, h, 'dark') + aperture_crop(w, h, 'dark') + unified_field(w, h, 'dark', cx=w*0.86, scale=h*1.25/1000)),
        ('WFS_Background_16x9_Dark_Convergence', 1920, 1080, lambda w, h: ground(w, h, 'dark') + ambient(w, h, 'dark', .75, .5, .5) + convergence(w, h, 'dark', cx=w*0.78)),
        ('WFS_Background_16x9_Light_Field', 1920, 1080, lambda w, h: ground(w, h, 'light') + ambient(w, h, 'light') + aperture_crop(w, h, 'light', opacity=0.07) + unified_field(w, h, 'light', cx=w*0.86, scale=h*1.25/1000)),
        ('WFS_Background_1x1_Dark_Convergence', 1080, 1080, lambda w, h: ground(w, h, 'dark') + ambient(w, h, 'dark', .5, .45, .6) + convergence(w, h, 'dark', cx=w*0.5, cy=h*0.5, scale=w*1.1/1000)),
        ('WFS_Background_A4_Dark_Cover', 2480, 3508, lambda w, h: ground(w, h, 'dark') + ambient(w, h, 'dark', .7, .35, .6) + aperture_crop(w, h, 'dark', cx=w*0.95, cy=h*0.34, scale=w*1.3/1000)),
        ('WFS_Background_A4_Light_Cover', 2480, 3508, lambda w, h: ground(w, h, 'light') + ambient(w, h, 'light', .7, .3, .6) + aperture_crop(w, h, 'light', cx=w*0.95, cy=h*0.34, scale=w*1.3/1000)),
    ]
    for name, w, h, fn in comps:
        write('backgrounds', name, doc(w, h, fn(w, h), name.replace('_', ' ')), 'Ready-to-use background composition', min(w, 1920), 'dark' if 'Dark' in name else 'light', '')
    # thumbnail-scale previews (720 x 405 canvas keeps line weights legible when reduced)
    os.makedirs(os.path.join(GS, 'preview'), exist_ok=True)
    w, h = 720, 405
    prev = {
        'Pattern_01_Unified_Field': lambda k: ground(w, h, k) + ambient(w, h, k) + unified_field(w, h, k),
        'Pattern_02_Financial_Convergence': lambda k: ground(w, h, k) + ambient(w, h, k, .62, .52, .5) + convergence(w, h, k),
        'Pattern_03_Structured_Orbit': lambda k: ground(w, h, k) + orbit(w, h, k, cx=w * 0.7),
        'Field_Ambient': lambda k: ground(w, h, k) + ambient(w, h, k),
        'Field_Construction_Rings': lambda k: ground(w, h, k) + construction_lines(w, h, k),
        'Field_Aperture_Crop': lambda k: ground(w, h, k) + ambient(w, h, k) + aperture_crop(w, h, k),
        'Field_Glint': lambda k: ground(w, h, k) + glint(w, h, k),
        'Field_Grid_Nodes': lambda k: ground(w, h, k) + orbit(w, h, k, cx=w * 0.5, unit=h / 9),
    }
    for name, fn in prev.items():
        for k in ('dark', 'light'):
            svg = doc(w, h, fn(k), f'WFS preview — {name} ({k})')
            cairosvg.svg2png(bytestring=svg.encode(), write_to=os.path.join(GS, 'preview', f'WFS_{name}_{k.capitalize()}_preview.png'), output_width=1440)
    REC.append(dict(asset='graphic-system/preview/*_preview.png', group='graphic-system/preview', purpose='Thumbnail-scale previews (for documents and overviews, not production)', files=[], variant='preview', backgrounds=''))
    json.dump(REC, open(os.path.join(ROOT, 'source', 'master', 'asset_records_graphics.json'), 'w'), indent=1)
    print(len(REC), 'graphic assets')
