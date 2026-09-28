"""WFS icon — vector master reconstruction (all-circle construction).

Input : reference/approved_icon_reference.png  (approved raster artwork, 1254 px)
Output: master/icon_geometry.json

Construction
------------
The approved icon is a five-blade aperture. Every blade is a curvilinear
quadrilateral bounded by
    * an OUTER arc    (its segment of the silhouette),
    * a LEADING edge  shared with the next blade,
    * an APERTURE arc (its segment of the central opening),
    * a TRAILING edge shared with the previous blade.
Outer and aperture boundaries are fitted as true circular arcs. Shared edges
are fitted as BIARCS - two circular arcs joined with tangent (G1) continuity -
pinned at the triple junctions where they meet the silhouette/aperture.
The whole mark is therefore built exclusively from circles, and neighbouring
blades share identical edges (watertight, no slivers).

Gap variants (for one-colour use) subtract a band of constant width centred
on every shared edge; the band edges are concentric offsets of the edge arcs,
so gap variants are also pure circular-arc geometry.
"""
import json, os, numpy as np, cv2
from PIL import Image
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from scipy.optimize import minimize
from skimage.measure import label, regionprops, find_contours
from shapely.geometry import Polygon, LineString

HERE = os.path.dirname(os.path.abspath(__file__))
BG, HOLE = 10, 11

# ------------------------------------------------------------------ utilities
def fit_circle(p):
    p = np.asarray(p, float)
    A = np.c_[2 * p[:, 0], 2 * p[:, 1], np.ones(len(p))]; b = (p ** 2).sum(1)
    cx, cy, k = np.linalg.lstsq(A, b, rcond=None)[0]
    r = np.sqrt(k + cx * cx + cy * cy)
    return np.array([cx, cy]), r, np.hypot(p[:, 0] - cx, p[:, 1] - cy) - r

def perp(v): return np.array([-v[1], v[0]])
def unit(v): return v / np.linalg.norm(v)
def ang(c, p): return np.arctan2(p[1] - c[1], p[0] - c[0])
def cross(a, b): return a[0] * b[1] - a[1] * b[0]

def circ_circ(c1, r1, c2, r2, near):
    d = np.linalg.norm(c2 - c1)
    if d < 1e-9 or d > r1 + r2 or d < abs(r1 - r2): return None
    x = (d * d + r1 ** 2 - r2 ** 2) / (2 * d); h = np.sqrt(max(r1 ** 2 - x * x, 0))
    u = (c2 - c1) / d; base = c1 + x * u
    return min([base + h * perp(u), base - h * perp(u)], key=lambda p: np.linalg.norm(p - near))

def fmt(v):
    s = f'{v:.2f}'.rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s

def arc_span(c, a, b, sweep):
    """Angular span from a to b around c; sweep=1 -> increasing angle (clockwise on screen)."""
    d = (ang(c, b) - ang(c, a)) % (2 * np.pi)
    return d if sweep == 1 else (2 * np.pi - d) % (2 * np.pi)

def arc_cmd(c, r, a, b, sweep):
    span = arc_span(c, a, b, sweep)
    return f'A {fmt(r)} {fmt(r)} 0 {1 if span > np.pi else 0} {sweep} {fmt(b[0])} {fmt(b[1])}'

def arc_pts(c, r, a, b, sweep, n=None):
    span = arc_span(c, a, b, sweep)
    n = n or max(8, int(span * r / 0.5))
    t = ang(c, a) + (np.linspace(0, span, n) if sweep == 1 else -np.linspace(0, span, n))
    return np.c_[c[0] + r * np.cos(t), c[1] + r * np.sin(t)]

def sweep_through(c, a, b, via):
    """Sweep flag of the arc a->b that passes through (the angle of) `via`."""
    return 1 if arc_span(c, a, via, 1) <= arc_span(c, a, b, 1) else 0

# ------------------------------------------------------------------ biarc
class Biarc:
    """Two tangent-continuous arcs P0 -> Pm -> P1 with unit tangents T0 (at P0), T1 (at P1)."""
    def __init__(self, P0, T0, P1, T1, d1_ratio):
        v = P1 - P0; self.P0, self.P1 = P0, P1
        T0 = unit(T0); T1 = unit(T1)
        d1 = d1_ratio * np.linalg.norm(v)
        den = v @ T1 - d1 * (T0 @ T1 - 1)
        if abs(den) < 1e-9: raise ValueError('degenerate biarc')
        d2 = (0.5 * v @ v - d1 * (v @ T0)) / den
        if d2 <= 0: raise ValueError('degenerate biarc')
        Q1 = P0 + d1 * T0; Q2 = P1 - d2 * T1
        self.Pm = (d2 * Q1 + d1 * Q2) / (d1 + d2)
        self.arcs = []
        for P, T, Q in ((P0, T0, self.Pm), (P1, -T1, self.Pm)):
            n = perp(T); w = Q - P
            k = 2 * (w @ n)
            if abs(k) < 1e-9: raise ValueError('straight segment')
            r = (w @ w) / k
            self.arcs.append((P + n * r, abs(r)))
        (c0, _), (c1, _) = self.arcs
        self.sw = [1 if cross(P0 - c0, T0) > 0 else 0, 1 if cross(P1 - c1, T1) > 0 else 0]

    def dense(self, n=600, ext=0.0):
        (c0, r0), (c1, r1) = self.arcs
        a = arc_pts(c0, r0, self.P0, self.Pm, self.sw[0], n)
        b = arc_pts(c1, r1, self.Pm, self.P1, self.sw[1], n)
        if arc_span(c0, self.P0, self.Pm, self.sw[0]) > np.pi or arc_span(c1, self.Pm, self.P1, self.sw[1]) > np.pi:
            raise ValueError('biarc wraps')
        out = [a, b[1:]]
        if ext > 0:
            def cont(c, r, p, sw, length):
                t0 = ang(c, p); dt = length / r * (1 if sw == 1 else -1)
                t = t0 + np.linspace(0, dt, 60)
                return np.c_[c[0] + r * np.cos(t), c[1] + r * np.sin(t)]
            head = cont(c0, r0, self.P0, 1 - self.sw[0], ext)[::-1]
            tail = cont(c1, r1, self.P1, self.sw[1], ext)
            out = [head[:-1]] + out + [tail[1:]]
        return np.vstack(out)

def fit_biarc(P0, P1, pts):
    """Biarc pinned at P0, P1 minimising deviation from `pts` (ordered P0 -> P1)."""
    base0 = np.arctan2(*(unit(pts[min(12, len(pts) - 1)] - P0))[::-1])
    base1 = np.arctan2(*(unit(P1 - pts[max(-13, -len(pts))]))[::-1])
    tp = cKDTree(pts)
    def build(x):
        T0 = np.array([np.cos(x[0]), np.sin(x[0])]); T1 = np.array([np.cos(x[1]), np.sin(x[1])])
        return Biarc(P0, T0, P1, T1, float(np.clip(x[2], 0.05, 0.95)))
    def cost(x):
        try:
            d = build(x).dense(300)
        except (ValueError, ZeroDivisionError, FloatingPointError):
            return 1e9
        dd, _ = cKDTree(d).query(pts)
        dd2, _ = tp.query(d)
        return np.mean(dd ** 2) + 0.5 * np.mean(dd2 ** 2)
    best = None
    for r0 in (0.25, 0.4, 0.55, 0.7):
        res = minimize(cost, [base0, base1, r0], method='Nelder-Mead',
                       options=dict(xatol=1e-6, fatol=1e-7, maxiter=6000))
        if best is None or res.fun < best.fun: best = res
    ba = build(best.x)
    dd, _ = cKDTree(ba.dense(1500)).query(pts)
    ba.max_dev = float(dd.max()); ba.rms = float(np.sqrt(np.mean(dd ** 2)))
    return ba

# ------------------------------------------------------------------ 1. segmentation
src = np.array(Image.open(f'{HERE}/reference/approved_icon_reference.png').convert('RGBA')).astype(float)
alpha = src[..., 3]; inside = alpha >= 128
rgb = src[..., :3] * (alpha[..., None] / 255) + 128 * (1 - alpha[..., None] / 255)
grey = cv2.cvtColor(rgb.astype(np.uint8), cv2.COLOR_RGB2GRAY)
edgemap = cv2.dilate(cv2.Canny(cv2.GaussianBlur(grey, (5, 5), 0), 20, 60), np.ones((7, 7), np.uint8))
lab = label(inside & (edgemap == 0), connectivity=1)
regs = sorted([r for r in regionprops(lab) if r.area > 800], key=lambda r: -r.area)
assert len(regs) == 5
seed = np.zeros(lab.shape, np.int32)
for i, r in enumerate(regs): seed[lab == r.label] = i + 1
_, (iy, ix) = ndi.distance_transform_edt(seed == 0, return_indices=True)
full = seed[iy, ix]
outl = label(~inside, connectivity=1)
full[~inside] = np.where(outl[~inside] == outl[0, 0], BG, HOLE)

# ------------------------------------------------------------------ 2. boundary runs
H, W = full.shape
runs = {}
for i in range(1, 6):
    m = ndi.gaussian_filter((full == i).astype(float), 1.0)
    c = max(find_contours(m, 0.5), key=len)[:, ::-1]
    t = np.gradient(c, axis=0); t /= np.linalg.norm(t, axis=1, keepdims=True) + 1e-9
    n = np.c_[t[:, 1], -t[:, 0]]
    if np.mean([full[int(round(y)), int(round(x))] == i for x, y in (c + 3 * n)[::40]]) > 0.5: n = -n
    q = np.clip(np.round(c + 5 * n).astype(int), 0, [W - 1, H - 1])
    nb = full[q[:, 1], q[:, 0]]; nb2 = nb.copy()
    for j in range(len(nb)):
        w = np.take(nb, range(j - 15, j + 16), mode='wrap'); v, cnt = np.unique(w, return_counts=True); nb2[j] = v[cnt.argmax()]
    ch = np.nonzero(nb2 != np.roll(nb2, 1))[0]
    c = np.roll(c, -ch[0], axis=0); nb2 = np.roll(nb2, -ch[0])
    ch = list(np.nonzero(nb2 != np.roll(nb2, 1))[0]) + [len(nb2)]
    runs[i] = [(int(nb2[a]), c[a:b]) for a, b in zip(ch[:-1], ch[1:])]
    assert len(runs[i]) == 4

# ------------------------------------------------------------------ 3. master frame
cnt, _ = cv2.findContours(inside.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
C0, R0, _ = fit_circle(max(cnt, key=cv2.contourArea)[:, 0, :].astype(float))
S = 500.0 / R0
def M(p): return (np.asarray(p, float) - C0) * S

# ------------------------------------------------------------------ 4. boundary arcs
bound = {}
for i in range(1, 6):
    for nbk, pts in runs[i]:
        if nbk in (BG, HOLE):
            p = M(pts[14:-14]); c, r, res = fit_circle(p)
            bound[(i, nbk)] = (c, r, float(np.abs(res).max()), p[len(p) // 2])

# ------------------------------------------------------------------ 5. edges (biarcs)
def run_of(i, nbk): return [p for k, p in runs[i] if k == nbk][0]
edges_ = {}
for i in range(1, 6):
    for k, (nbk, pts) in enumerate(runs[i]):
        if nbk in (BG, HOLE) or (min(i, nbk), max(i, nbk)) in edges_: continue
        j = nbk
        other = run_of(j, i)
        d, jj = cKDTree(other).query(pts); ok = d < 16
        mid = (pts[ok] + other[jj[ok]]) / 2
        s_ = np.r_[0, np.cumsum(np.linalg.norm(np.diff(mid, axis=0), axis=1))]
        ss = np.linspace(0, s_[-1], int(s_[-1] / 1.5))
        mid = np.c_[np.interp(ss, s_, mid[:, 0]), np.interp(ss, s_, mid[:, 1])]
        mid = M(ndi.gaussian_filter1d(mid, 3, axis=0, mode='nearest'))
        kinds = (runs[i][(k - 1) % 4][0], runs[i][(k + 1) % 4][0])
        J = []
        for kind, near in zip(kinds, (M(pts[0]), M(pts[-1]))):
            ci, ri = bound[(i, kind)][:2]; cj, rj = bound[(j, kind)][:2]
            p = circ_circ(ci, ri, cj, rj, near)
            if p is None or np.linalg.norm(p - near) > 20:
                p = (ci + ri * unit(near - ci) + cj + rj * unit(near - cj)) / 2
            J.append(p)
        ba = fit_biarc(J[0], J[1], mid[10:-10])
        edges_[(min(i, j), max(i, j))] = dict(ba=ba, kinds=kinds)

# ------------------------------------------------------------------ 6. blade assembly
def blade_solid(i):
    seq = runs[i]
    corners = []
    for k in range(4):
        (n1, p1), (n2, p2) = seq[k], seq[(k + 1) % 4]
        near = M((p1[-1] + p2[0]) / 2)
        bkind, ekey = (n1, (min(i, n2), max(i, n2))) if n1 in (BG, HOLE) else (n2, (min(i, n1), max(i, n1)))
        c, r = bound[(i, bkind)][:2]
        ba = edges_[ekey]['ba']
        (ca, ra), (cb, rb) = ba.arcs
        end = ba.P0 if np.linalg.norm(ba.P0 - near) < np.linalg.norm(ba.P1 - near) else ba.P1
        ce, re_ = (ca, ra) if end is ba.P0 else (cb, rb)
        p = circ_circ(c, r, ce, re_, end)
        if p is None or np.linalg.norm(p - end) > 25: p = end
        corners.append(p)
    d = [f'M {fmt(corners[3][0])} {fmt(corners[3][1])}']; poly = []
    for k in range(4):
        nbk, pts = seq[k]
        a, b = corners[k - 1], corners[k]
        if nbk in (BG, HOLE):
            c, r, _, _ = bound[(i, nbk)]
            sw = sweep_through(c, a, b, M(pts[len(pts) // 2]))
            d.append(arc_cmd(c, r, a, b, sw)); poly.append(arc_pts(c, r, a, b, sw))
        else:
            ba = edges_[(min(i, nbk), max(i, nbk))]['ba']
            (c0, r0), (c1, r1) = ba.arcs
            if np.linalg.norm(a - ba.P0) < np.linalg.norm(a - ba.P1):
                parts = [((c0, r0), a, ba.Pm, ba.sw[0]), ((c1, r1), ba.Pm, b, ba.sw[1])]
            else:
                parts = [((c1, r1), a, ba.Pm, 1 - ba.sw[1]), ((c0, r0), ba.Pm, b, 1 - ba.sw[0])]
            for (c, r), pa, pb, sw in parts:
                if arc_span(c, pa, pb, sw) > np.pi: sw = 1 - sw
                d.append(arc_cmd(c, r, pa, pb, sw)); poly.append(arc_pts(c, r, pa, pb, sw))
    d.append('Z')
    return ' '.join(d), Polygon(np.vstack(poly)).buffer(0)

def poly_to_arcs(poly, prims):
    """Re-express a polygon whose boundary lies on known circles as an exact arc path."""
    pts = np.array(poly.exterior.coords)[:-1]
    D = np.array([np.abs(np.linalg.norm(pts - c, axis=1) - r) for c, r in prims])
    lab_ = D.argmin(0)
    ch = np.nonzero(lab_ != np.roll(lab_, 1))[0]
    pts = np.roll(pts, -ch[0], axis=0); lab_ = np.roll(lab_, -ch[0])
    ch = list(np.nonzero(lab_ != np.roll(lab_, 1))[0]) + [len(lab_)]
    rr = [(lab_[a], a, b) for a, b in zip(ch[:-1], ch[1:]) if b - a >= 3]
    merged = []
    for r_ in rr:
        if merged and merged[-1][0] == r_[0]: merged[-1] = (r_[0], merged[-1][1], r_[2])
        else: merged.append(r_)
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
        c, r = prims[merged[k][0]]
        a, b = corners[k - 1], corners[k]
        via = pts[((merged[k][1] + merged[k][2]) // 2) % len(pts)]
        d.append(arc_cmd(c, r, a, b, sweep_through(c, a, b, via)))
    d.append('Z')
    return ' '.join(d)

def blade_gap(i, gap):
    _, poly = blade_solid(i)
    prims = [bound[(i, BG)][:2], bound[(i, HOLE)][:2]]
    for nbk, _ in runs[i]:
        if nbk in (BG, HOLE): continue
        ba = edges_[(min(i, nbk), max(i, nbk))]['ba']
        band = LineString(ba.dense(800, ext=120)).buffer(gap / 2, cap_style=2, join_style=1, resolution=128)
        poly = poly.difference(band)
        for c, r in ba.arcs: prims += [(c, r + gap / 2), (c, max(r - gap / 2, 1e-3))]
    poly = poly.buffer(-0.4, join_style=2, mitre_limit=40).buffer(0.4, join_style=2, mitre_limit=40)
    if poly.geom_type != 'Polygon': poly = max(poly.geoms, key=lambda g: g.area)
    return poly_to_arcs(poly, prims), poly

# ------------------------------------------------------------------ 7. export
if __name__ == '__main__':
    os.makedirs(f'{HERE}/master', exist_ok=True)
    mat = {}
    for i in range(1, 6):
        c = src[..., :3][full == i].mean(0); mat[i] = (c, c.mean(), c[0] - c[2])
    neutral = [i for i in mat if mat[i][2] < 15]
    silver = max(neutral, key=lambda i: mat[i][1]); graphite = min(neutral, key=lambda i: mat[i][1])
    adj = {i: [nbk for nbk, _ in runs[i] if nbk not in (BG, HOLE)] for i in runs}
    ring = [silver]; prev = graphite
    while len(ring) < 5:
        cur = ring[-1]; nxt = [x for x in adj[cur] if x != prev][0]; prev = cur; ring.append(nxt)
    labels = ['B1', 'B2', 'B3', 'B4', 'B5']
    idx = {i: l for l, i in zip(labels, ring)}
    geo = dict(
        title='WFS icon master geometry v1.0',
        units='master units; nominal outer circle radius = 500 (diameter 1000), centre (0,0), y down',
        reference=dict(file='reference/approved_icon_reference.png', px_per_unit=1 / S,
                       centre_px=[round(float(x), 2) for x in C0], radius_px=round(float(R0), 2)),
        blade_order='B1..B5 clockwise, starting at the light-neutral blade of the reference',
        blades={}, circles=[], edge_fit={})
    variants = {'solid': {i: blade_solid(i) for i in range(1, 6)}}
    for g in (12, 20, 32, 56):
        variants[f'gap{g}'] = {i: blade_gap(i, g) for i in range(1, 6)}
    for lbl, i in zip(labels, ring):
        geo['blades'][lbl] = dict(reference_material='silver' if i == silver else 'graphite' if i == graphite else 'gold',
                                  reference_rgb=[round(float(x)) for x in mat[i][0]],
                                  paths={k: v[i][0] for k, v in variants.items()})
    for (i, kind), (c, r, err, _) in sorted(bound.items()):
        geo['circles'].append(dict(role='outer' if kind == BG else 'aperture', blade=idx[i],
                                   centre=[round(float(x), 3) for x in c], radius=round(float(r), 3),
                                   fit_max_error=round(err, 3)))
    for (i, j), e in sorted(edges_.items()):
        ba = e['ba']
        key = '|'.join(sorted([idx[i], idx[j]]))
        for k, (c, r) in enumerate(ba.arcs):
            geo['circles'].append(dict(role=f'edge {key} arc {k + 1}', centre=[round(float(x), 3) for x in c],
                                       radius=round(float(r), 3)))
        geo['edge_fit'][key] = dict(max_dev=round(ba.max_dev, 2), rms=round(ba.rms, 2))
        (c0, r0), (c1, r1) = ba.arcs
        d = (f'M {fmt(ba.P0[0])} {fmt(ba.P0[1])} ' + arc_cmd(c0, r0, ba.P0, ba.Pm, ba.sw[0]) + ' '
             + arc_cmd(c1, r1, ba.Pm, ba.P1, ba.sw[1]))
        geo.setdefault('edges', {})[key] = dict(d=d, p0=[round(float(x), 2) for x in ba.P0],
                                                p1=[round(float(x), 2) for x in ba.P1])
    # stacking used by the premium display rendering: which blade sits over each shared edge
    geo['stacking'] = {'B1|B2': 'B2', 'B2|B3': 'B2', 'B3|B4': 'B4', 'B4|B5': 'B4', 'B1|B5': 'B1'}
    json.dump(geo, open(f'{HERE}/master/icon_geometry.json', 'w'), indent=1)
    print('ring', ring)
    print('edge fits', geo['edge_fit'])
    print('boundary arc fit max errors', [c['fit_max_error'] for c in geo['circles'] if 'fit_max_error' in c])
