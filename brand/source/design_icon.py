"""WFS icon v2 — original parametric design (Unified Financial Field).

Five identical blades with exact 72-degree rotational symmetry form an aperture.
Every curve is a true circular arc:
  * outer boundary   : circle R centred at the origin
  * aperture         : circle r centred at the origin
  * blade edges      : circle of radius rho, externally tangent to the aperture
                       at the blade tip, rotated 5x by 72 degrees
The edge leaves the aperture tangentially (a perfectly smooth, sharp tip) and meets
the outer circle cleanly. Writes master/icon_geometry.json (same schema as before,
so every downstream builder is unchanged)."""
import json, os, math
import numpy as np
from shapely.geometry import Polygon, Point, LineString
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
R, r, RHO, N = 500.0, 190.0, 520.0, 5
ROT0 = -54.0          # orientation of blade 1 tip (degrees)

def fmt(v):
    s = f'{v:.2f}'.rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s

def ang(c, p): return math.atan2(p[1] - c[1], p[0] - c[0])

def arc_span(c, a, b, sweep):
    d = (ang(c, b) - ang(c, a)) % (2 * math.pi)
    return d if sweep == 1 else (2 * math.pi - d) % (2 * math.pi)

def arc_cmd(c, rad, a, b, sweep):
    span = arc_span(c, a, b, sweep)
    return f'A {fmt(rad)} {fmt(rad)} 0 {1 if span > math.pi else 0} {sweep} {fmt(b[0])} {fmt(b[1])}'

def sweep_through(c, a, b, via):
    return 1 if arc_span(c, a, via, 1) <= arc_span(c, a, b, 1) else 0

def circ_circ(c1, r1, c2, r2, near):
    c1, c2 = np.asarray(c1, float), np.asarray(c2, float)
    d = np.linalg.norm(c2 - c1)
    if d < 1e-9 or d > r1 + r2 or d < abs(r1 - r2): return None
    x = (d * d + r1 ** 2 - r2 ** 2) / (2 * d); h = math.sqrt(max(r1 ** 2 - x * x, 0))
    u = (c2 - c1) / d; base = c1 + x * u; p = np.array([-u[1], u[0]])
    return min([base + h * p, base - h * p], key=lambda q: np.linalg.norm(q - near))

def rot(p, deg):
    t = math.radians(deg); c, s = math.cos(t), math.sin(t)
    return np.array([c * p[0] - s * p[1], s * p[0] + c * p[1]])

def disc(c, rad, n=4096):
    t = np.linspace(0, 2 * math.pi, n, endpoint=False)
    return Polygon(np.c_[c[0] + rad * np.cos(t), c[1] + rad * np.sin(t)])

# ---------------------------------------------------------------- primitives
edge_centres = [rot(np.array([r + RHO, 0.0]), ROT0 + 72 * k) for k in range(N)]   # tangent at tip angle ROT0+72k
tips = [rot(np.array([r, 0.0]), ROT0 + 72 * k) for k in range(N)]
outer_pts = [circ_circ((0, 0), R, c, RHO, rot(np.array([R, 0]), ROT0 + 72 * k - 47)) for k, c in enumerate(edge_centres)]

def arc_pts(c, rad, a, b, sweep, n=600):
    span = arc_span(c, a, b, sweep); t0 = ang(c, a)
    t = t0 + (np.linspace(0, span, n) if sweep == 1 else -np.linspace(0, span, n))
    return np.c_[c[0] + rad * np.cos(t), c[1] + rad * np.sin(t)]

def edge_sweep(k):
    c = edge_centres[k]; mid = (tips[k] + outer_pts[k]) / 2
    via = c + RHO * (mid - c) / np.linalg.norm(mid - c)
    return sweep_through(c, tips[k], outer_pts[k], via)

O = np.zeros(2)
solid_paths, blades = [], []
for k in range(N):
    k1 = (k + 1) % N
    c0, c1 = edge_centres[k], edge_centres[k1]
    s0, s1 = edge_sweep(k), edge_sweep(k1)
    so = sweep_through(O, outer_pts[k], outer_pts[k1], rot(np.array([R, 0]), ROT0 + 72 * k - 10))
    si = sweep_through(O, tips[k1], tips[k], rot(np.array([r, 0]), ROT0 + 72 * k + 36))
    d = (f'M {fmt(tips[k][0])} {fmt(tips[k][1])} ' + arc_cmd(c0, RHO, tips[k], outer_pts[k], s0) + ' '
         + arc_cmd(O, R, outer_pts[k], outer_pts[k1], so) + ' ' + arc_cmd(c1, RHO, outer_pts[k1], tips[k1], 1 - s1) + ' '
         + arc_cmd(O, r, tips[k1], tips[k], si) + ' Z')
    poly = Polygon(np.vstack([arc_pts(c0, RHO, tips[k], outer_pts[k], s0), arc_pts(O, R, outer_pts[k], outer_pts[k1], so),
                              arc_pts(c1, RHO, outer_pts[k1], tips[k1], 1 - s1), arc_pts(O, r, tips[k1], tips[k], si)])).buffer(0)
    solid_paths.append(d); blades.append(poly)
cover = unary_union(blades)
coverage = cover.area / disc((0, 0), R).difference(disc((0, 0), r)).area

def poly_to_arcs(poly, prims):
    pts = np.array(poly.exterior.coords)[:-1]
    Dm = np.array([np.abs(np.linalg.norm(pts - np.asarray(c), axis=1) - rad) for c, rad in prims])
    lab = Dm.argmin(0)
    ch = np.nonzero(lab != np.roll(lab, 1))[0]
    pts = np.roll(pts, -ch[0], axis=0); lab = np.roll(lab, -ch[0])
    ch = list(np.nonzero(lab != np.roll(lab, 1))[0]) + [len(lab)]
    runs = [(lab[a], a, b) for a, b in zip(ch[:-1], ch[1:]) if b - a >= 3]
    merged = []
    for q in runs:
        if merged and merged[-1][0] == q[0]: merged[-1] = (q[0], merged[-1][1], q[2])
        else: merged.append(q)
    if len(merged) > 1 and merged[0][0] == merged[-1][0]:
        f = merged.pop(); merged[0] = (f[0], f[1] - len(pts), merged[0][2])
    n = len(merged); corners = []
    for k in range(n):
        (ca, ra), (cb, rb) = prims[merged[k][0]], prims[merged[(k + 1) % n][0]]
        near = pts[merged[(k + 1) % n][1] % len(pts)]
        p = circ_circ(ca, ra, cb, rb, near)
        corners.append(p if p is not None and np.linalg.norm(p - near) < 3 else near)
    d = [f'M {fmt(corners[-1][0])} {fmt(corners[-1][1])}']
    for k in range(n):
        c, rad = prims[merged[k][0]]
        a, b = corners[k - 1], corners[k]
        via = pts[((merged[k][1] + merged[k][2]) // 2) % len(pts)]
        d.append(arc_cmd(c, rad, a, b, sweep_through(c, a, b, via)))
    d.append('Z')
    return ' '.join(d)

def edge_line(k, ext=80):
    c = edge_centres[k]; s0 = edge_sweep(k)
    p = arc_pts(c, RHO, tips[k], outer_pts[k], s0, 900)
    t0 = p[0] - p[3]; t0 /= np.linalg.norm(t0); t1 = p[-1] - p[-4]; t1 /= np.linalg.norm(t1)
    return np.vstack([p, p[-1] + t1 * ext])       # extend only beyond the outer circle; tips stay intact

def variant(gap):
    if gap == 0: return solid_paths
    out = []
    for k in range(N):
        k1 = (k + 1) % N
        b = blades[k]
        for e in (k, k1):
            b = b.difference(LineString(edge_line(e)).buffer(gap / 2, cap_style=2, join_style=1, resolution=64))
        b = b.buffer(-0.3, join_style=2, mitre_limit=40).buffer(0.3, join_style=2, mitre_limit=40)
        if b.geom_type != 'Polygon': b = max(b.geoms, key=lambda g: g.area)
        prims = [((0, 0), R), ((0, 0), r)] + [(tuple(edge_centres[e]), RHO + sg * gap / 2) for e in (k, k1) for sg in (1, -1)]
        out.append(poly_to_arcs(b, prims))
    return out

if __name__ == '__main__':
    variants = {'solid': variant(0)}
    for g in (12, 20, 32, 56): variants[f'gap{g}'] = variant(g)
    labels = [f'B{k + 1}' for k in range(N)]
    # edges as open arcs tip -> outer point (used by premium lighting and graphics)
    edges = {}
    stacking = {}
    for k in range(N):
        c = edge_centres[k]; a = tips[k]; b = outer_pts[k]
        mid = rot(np.array([R * 0.72, 0]), ROT0 + 72 * k - 24)
        near_mid = c + RHO * (mid - c) / np.linalg.norm(mid - c)
        sw = sweep_through(c, a, b, near_mid)
        key = f'{labels[(k - 1) % N]}|{labels[k]}'
        edges[key] = dict(d=f'M {fmt(a[0])} {fmt(a[1])} ' + arc_cmd(c, RHO, a, b, sw), p0=[round(float(x), 2) for x in a], p1=[round(float(x), 2) for x in b],
                          centre=[round(float(x), 3) for x in c], radius=RHO)
        stacking[key] = labels[k]          # blade k sits over blade k-1 along edge k
    geo = dict(title='WFS icon master geometry v2.0 (original parametric design)',
               units='master units; outer circle radius 500 (diameter 1000), centre (0,0), y down',
               parameters=dict(R=R, r=r, rho=RHO, blades=N, symmetry='5-fold rotational (72 deg)', rotation_deg=ROT0),
               construction='outer circle R; aperture circle r; each blade edge is a circle of radius rho externally tangent to the aperture at the blade tip',
               coverage=round(coverage, 5),
               reference=dict(file=None, px_per_unit=1.0, centre_px=[0, 0], radius_px=R),
               blades={l: dict(paths={v: variants[v][k] for v in variants}) for k, l in enumerate(labels)},
               circles=[dict(role='outer', centre=[0, 0], radius=R), dict(role='aperture', centre=[0, 0], radius=r)]
                       + [dict(role=f'edge {k + 1}', centre=[round(float(x), 3) for x in edge_centres[k]], radius=RHO) for k in range(N)],
               edges=edges, stacking=stacking)
    os.makedirs(os.path.join(HERE, 'master'), exist_ok=True)
    json.dump(geo, open(os.path.join(HERE, 'master', 'icon_geometry.json'), 'w'), indent=1)
    print('coverage of annulus', round(coverage, 5), '| path lengths', [len(p) for p in variants['solid']])
