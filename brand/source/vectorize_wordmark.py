"""WFS wordmark — vector master reconstruction.

Production method: potrace + cleanup (trace_letters). The line/fillet
construction helpers (build) are kept for reference and analysis.

Input : reference/approved_wordmark_reference.png (approved raster artwork)
Output: master/wordmark_geometry.json

Method
------
1. Sub-pixel outline of each letter from the anti-aliased alpha channel.
2. Straight runs are detected and fitted as exact least-squares lines.
3. Near-parallel strokes are unified (angle clusters), near-vertical /
   near-horizontal strokes are snapped to exact 90/0 degrees.
4. Everything between straight runs (fillets, bowls, terminals) is fitted as
   cubic Beziers with tangent (G1) continuity to the adjacent lines, or as a
   sharp corner where the reference has one.
5. Internal ribbon folds (used only by the premium display version) are
   extracted from the reference shading and fitted as smooth curves.
"""
import json, os, numpy as np, cv2
from PIL import Image
from scipy import ndimage as ndi
from skimage.measure import find_contours, label
from skimage.morphology import skeletonize
from geom import fit_curve, bez, fmt

HERE = os.path.dirname(os.path.abspath(__file__))
im = np.array(Image.open(f'{HERE}/reference/approved_wordmark_reference.png').convert('RGBA')).astype(float)
alpha = im[..., 3]
ys, xs = np.nonzero(alpha >= 128)
X0, Y0, Y1 = xs.min(), ys.min(), ys.max()
CAP_PX = (Y1 - Y0 + 1)
UNIT = 1000.0 / CAP_PX            # cap height = 1000 master units
def M(p): return (np.asarray(p, float) - [X0, Y0]) * UNIT

LINE_TOL = 0.9     # px: max deviation for a point to belong to a straight run
MIN_RUN = 26        # px: minimum straight run length
CURVE_TOL = 0.55    # px: Bezier fitting tolerance
SNAP_DEG = 1.6      # degrees: angle clustering / axis snapping threshold

def tls_line(p):
    c = p.mean(0); u, s, vt = np.linalg.svd(p - c); d = vt[0]
    dev = np.abs((p - c) @ np.array([-d[1], d[0]]))
    return c, d, dev

def contour_pts():
    a = ndi.gaussian_filter(alpha, 0.6)
    cs = [c[:, ::-1] for c in find_contours(a, 127.5) if len(c) > 200]
    out = []
    for c in cs:
        # resample at 0.75 px spacing
        s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(c, axis=0), axis=1))]
        ss = np.arange(0, s[-1], 0.75)
        out.append(np.c_[np.interp(ss, s, c[:, 0]), np.interp(ss, s, c[:, 1])])
    return out

def curved(p):
    """True if the run bends systematically (best-fit circle sagitta > 0.3 px)."""
    from geom import fit_circle
    c, r, res = fit_circle(p)
    L = np.linalg.norm(p[-1] - p[0])
    return (L * L / (8 * r)) > 0.6 and np.abs(res).max() < np.abs(tls_line(p)[2]).max() * 0.7

def straight_runs(P):
    n = len(P); w = 14
    ok = np.zeros(n, bool)
    for i in range(n):
        idx = np.arange(i - w, i + w + 1) % n
        _, _, dev = tls_line(P[idx]); ok[i] = dev.max() < LINE_TOL * 0.45
    # grow runs from seeds
    runs = []
    if ok.all(): return [(0, n)]
    start = np.argmin(ok)            # begin at a non-straight point
    order = (np.arange(n) + start) % n
    i = 0
    while i < n:
        if not ok[order[i]]: i += 1; continue
        j = i
        while j + 1 < n and ok[order[j + 1]]: j += 1
        a, b = i, j
        # extend while still straight
        while b + 1 < n:
            _, _, dev = tls_line(P[order[a:b + 2]])
            if dev.max() < LINE_TOL: b += 1
            else: break
        while a - 1 >= 0:
            _, _, dev = tls_line(P[order[a - 1:b + 1]])
            if dev.max() < LINE_TOL: a -= 1
            else: break
        if (b - a) * 0.75 >= MIN_RUN and not curved(P[order[a:b + 1]]): runs.append((order[a], (b - a + 1)))
        i = b + 1
    return runs


def fillet(l, nx, between):
    """Circular fillet tangent to lines l and nx that best matches the reference points."""
    from geom import arc_to_beziers, Arc
    d1, d2 = l['d'], nx['d']
    cr = d1[0] * d2[1] - d1[1] * d2[0]
    if abs(cr) < 1e-6: return None
    sgn = np.sign(cr)
    n1 = sgn * np.array([-d1[1], d1[0]]); n2 = sgn * np.array([-d2[1], d2[0]])
    def geo(r):
        A = np.c_[d1, -d2]
        t, _ = np.linalg.solve(A, (nx['c'] + r * n2) - (l['c'] + r * n1))
        C = l['c'] + r * n1 + t * d1
        return C, C - r * n1, C - r * n2
    def err(r):
        C, T1, T2 = geo(r)
        e = []
        for p in between:
            s1 = (p - T1) @ d1; s2 = (p - T2) @ d2
            if s1 <= 0: e.append(abs((p - l['c']) @ n1))
            elif s2 >= 0: e.append(abs((p - nx['c']) @ n2))
            else: e.append(abs(np.linalg.norm(p - C) - r))
        return np.array(e)
    rs = np.exp(np.linspace(np.log(0.8), np.log(400), 220))
    errs = [np.sqrt(np.mean(err(r) ** 2)) for r in rs]
    k = int(np.argmin(errs)); r = rs[k]
    lo, hi = rs[max(k - 1, 0)], rs[min(k + 1, len(rs) - 1)]
    for _ in range(40):
        m1, m2 = lo + (hi - lo) / 3, hi - (hi - lo) / 3
        if np.sqrt(np.mean(err(m1) ** 2)) < np.sqrt(np.mean(err(m2) ** 2)): hi = m2
        else: lo = m1
    r = (lo + hi) / 2
    if err(r).max() > 0.9: return None
    C, T1, T2 = geo(r)
    # tangent points must lie on the forward side of each run
    if (T1 - l['p0']) @ d1 <= 0 or (nx['p1'] - T2) @ d2 <= 0: return None
    arc = Arc(C, r, 0)
    a0 = np.arctan2(T1[1] - C[1], T1[0] - C[0]); a1 = np.arctan2(T2[1] - C[1], T2[0] - C[0])
    span = (a1 - a0) % (2 * np.pi); sweep = 1
    if span > np.pi: span = 2 * np.pi - span; sweep = 0
    return T1, T2, arc_to_beziers(arc, T1, sweep, span)

def simplify_path(d, tol=1.5, min_len=60.0):
    """Clean-up pass (master units): near-straight Beziers -> lines, merge collinear lines."""
    import re
    toks = re.findall(r'[MLCZ][^MLCZ]*', d)
    start = np.array(list(map(float, toks[0][1:].split())))
    segs = []; cur = start
    for t in toks[1:]:
        if t[0] == 'Z': break
        v = np.array(list(map(float, t[1:].split())))
        if t[0] == 'L': segs.append(['L', cur, v]); cur = v
        else:
            c = v.reshape(3, 2); segs.append(['C', cur, c[0], c[1], c[2]]); cur = c[2]
    def dist_line(p, a, b):
        u = b - a; L = np.linalg.norm(u)
        return abs((p - a) @ np.array([-u[1], u[0]]) / L) if L > 0 else np.linalg.norm(p - a)
    # greedy: runs of consecutive segments that all lie within tol of one chord -> single line
    out_segs = []; i = 0
    while i < len(segs):
        best = None
        for j in range(i, len(segs)):
            a = segs[i][1]; b = segs[j][-1]
            if np.linalg.norm(b - a) < min_len: continue
            pts_ = [p for s_ in segs[i:j + 1] for p in s_[1:]]
            if max(dist_line(p, a, b) for p in pts_) < tol and all(((p - a) @ (b - a)) >= -1 for p in pts_):
                best = j
            elif best is not None and j > best + 2:
                break
        if best is not None and best > i:
            out_segs.append(['L', segs[i][1], segs[best][-1]]); i = best + 1
        else:
            out_segs.append(segs[i]); i += 1
    segs = out_segs
    for s_ in segs:
        if s_[0] == 'C':
            a, c1, c2, b = s_[1:]
            if np.linalg.norm(b - a) > min_len and max(dist_line(c1, a, b), dist_line(c2, a, b)) < tol \
               and (c1 - a) @ (b - a) >= 0 and (c2 - b) @ (a - b) >= 0:
                s_[:] = ['L', a, b]
    # remove micro-segments (< 6 units): absorb into the previous segment
    clean = []
    for s_ in segs:
        if clean and np.linalg.norm(s_[-1] - s_[1]) < 6.0:
            prev = clean[-1]; delta = s_[-1] - prev[-1]
            if prev[0] == 'C': prev[3] = prev[3] + delta
            prev[-1] = s_[-1]; continue
        clean.append(s_)
    segs = clean
    merged = []
    for s_ in segs:
        if merged and s_[0] == 'L' and merged[-1][0] == 'L':
            a = merged[-1][1]; m = merged[-1][2]; b = s_[2]
            if dist_line(m, a, b) < tol * 0.5:
                merged[-1] = ['L', a, b]; continue
        merged.append(s_)
    # snap near-axis lines (< 0.8 deg) to exact horizontal / vertical, carrying neighbours' handles
    nseg = len(merged)
    for k, s_ in enumerate(merged):
        if s_[0] != 'L': continue
        a, b = s_[1].copy(), s_[2].copy(); v = b - a
        angd = np.degrees(np.arctan2(v[1], v[0])) % 180
        if min(angd, 180 - angd) < 0.8: axis = 1          # horizontal: equalise y
        elif abs(angd - 90) < 0.8: axis = 0              # vertical: equalise x
        else: continue
        m_ = (a[axis] + b[axis]) / 2
        da = np.zeros(2); db = np.zeros(2); da[axis] = m_ - a[axis]; db[axis] = m_ - b[axis]
        prev = merged[k - 1]; nxt = merged[(k + 1) % nseg]
        s_[1] = a + da; s_[2] = b + db
        prev[-1] = prev[-1] + da
        if prev[0] == 'C': prev[3] = prev[3] + da
        nxt[1] = nxt[1] + db
        if nxt[0] == 'C': nxt[2] = nxt[2] + db
        if k == 0: start = start + da
    start = merged[-1][-1]
    out = [f'M {fmt(start[0])} {fmt(start[1])}']
    for s_ in merged:
        if s_[0] == 'L': out.append(f'L {fmt(s_[2][0])} {fmt(s_[2][1])}')
        else: out.append('C ' + ' '.join(f'{fmt(p[0])} {fmt(p[1])}' for p in s_[2:]))
    out.append('Z')
    return ' '.join(out), len(merged)

def build():
    letters = []
    for P in contour_pts():
        runs = straight_runs(P)
        n = len(P)
        lines = []
        for s0, ln in runs:
            idx = (s0 + np.arange(ln)) % n
            c, d, _ = tls_line(P[idx])
            if d @ (P[idx[-1]] - P[idx[0]]) < 0: d = -d
            lines.append(dict(idx=idx, c=c, d=d, len=ln * 0.75))
        letters.append(dict(P=P, lines=lines))
    # ---- angle clustering across the whole wordmark
    all_lines = [l for L in letters for l in L['lines']]
    def angle(d): return np.degrees(np.arctan2(d[1], d[0])) % 180
    for l in all_lines: l['a'] = angle(l['d'])
    clusters = []
    for l in sorted(all_lines, key=lambda l: -l['len']):
        for cl in clusters:
            da = abs((l['a'] - cl['a'] + 90) % 180 - 90)
            if da < SNAP_DEG:
                cl['m'].append(l); break
        else:
            clusters.append(dict(a=l['a'], m=[l]))
    for cl in clusters:
        # length-weighted circular mean on the 180-degree circle
        th = np.radians(np.array([m['a'] for m in cl['m']]) * 2); w = np.array([m['len'] for m in cl['m']])
        a = np.degrees(np.arctan2((w * np.sin(th)).sum(), (w * np.cos(th)).sum()) / 2) % 180
        for ax in (0, 90, 180):
            if abs(a - ax) < SNAP_DEG: a = ax % 180
        cl['a'] = a
        for m in cl['m']:
            d = np.array([np.cos(np.radians(a)), np.sin(np.radians(a))])
            if d @ m['d'] < 0: d = -d
            # keep the line through the centroid of its points
            m['d'] = d; m['c'] = m['letterP'][m['idx']].mean(0) if 'letterP' in m else m['c']
    # ---- assemble paths
    out = []
    for L in letters:
        P = L['P']; n = len(P); lines = sorted(L['lines'], key=lambda l: l['idx'][0])
        segs = []   # list of ('L', p0, p1) or ('C', ctrl array)
        # endpoints of each line: projections of run ends, possibly replaced by corners
        def proj(l, p): return l['c'] + ((p - l['c']) @ l['d']) * l['d']
        for l in lines:
            l['p0'] = proj(l, P[l['idx'][0]]); l['p1'] = proj(l, P[l['idx'][-1]])
        k = len(lines)
        for t in range(k):
            l, nx = lines[t], lines[(t + 1) % k]
            a = l['idx'][-1]; b = nx['idx'][0]
            gap = (b - a) % n
            between = P[(a + np.arange(gap + 1)) % n]
            turn = np.degrees(np.arccos(np.clip(l['d'] @ nx['d'], -1, 1)))
            # sharp corner: short gap -> intersect the lines
            A = np.c_[l['d'], -nx['d']]
            if gap * 0.75 < 9 and abs(np.linalg.det(A)) > 1e-6:
                s, _ = np.linalg.solve(A, nx['c'] - l['c'])
                X = l['c'] + s * l['d']
                if np.linalg.norm(X - P[a]) < 12:
                    l['p1'] = X; nx['p0'] = X; l['next'] = None; continue
            # (2) circular fillet tangent to both lines
            fil = fillet(l, nx, between) if turn > 8 and turn < 172 else None
            if fil is not None:
                T1, T2, segs = fil
                l['p1'] = T1; nx['p0'] = T2; l['next'] = segs; continue
            # (3) free transition: Bezier chain, G1 with the lines where the departure is tangential
            inner = between[(np.linalg.norm(between - l['p1'], axis=1) > 5) & (np.linalg.norm(between - nx['p0'], axis=1) > 5)]
            pts = np.vstack([l['p1'], inner, nx['p0']]) if len(inner) > 3 else np.vstack([l['p1'], nx['p0']])
            t1 = l['d']; t2 = -nx['d']
            l['next'] = fit_curve(pts, CURVE_TOL, t1, t2)
        # emit
        d = [f"M {fmt(M(lines[0]['p0'])[0])} {fmt(M(lines[0]['p0'])[1])}"]
        nodes = 0
        for t in range(k):
            l = lines[t]
            p1 = M(l['p1']); d.append(f"L {fmt(p1[0])} {fmt(p1[1])}"); nodes += 1
            if l.get('next'):
                for c in l['next']:
                    c = M(c); d.append(f"C {fmt(c[1][0])} {fmt(c[1][1])} {fmt(c[2][0])} {fmt(c[2][1])} {fmt(c[3][0])} {fmt(c[3][1])}"); nodes += 1
        d.append('Z')
        xmin = P[:, 0].min()
        dd, nodes = simplify_path(' '.join(d))
        out.append(dict(x=float(xmin), d=dd, nodes=nodes, lines=k))
    out.sort(key=lambda o: o['x'])
    return out, clusters

def folds():
    """Internal ribbon folds (premium display version only)."""
    rgb = im[..., :3] * (alpha[..., None] / 255) + 255 * (1 - alpha[..., None] / 255)
    g = cv2.cvtColor(rgb.astype(np.uint8), cv2.COLOR_RGB2GRAY)
    e = cv2.Canny(cv2.GaussianBlur(g, (3, 3), 0), 15, 45) > 0
    inner = ndi.binary_erosion(alpha >= 128, iterations=7)
    e &= inner
    e = ndi.binary_dilation(e, iterations=2)
    sk = skeletonize(e)
    lab = label(sk, connectivity=2)
    res = []
    for i in range(1, lab.max() + 1):
        yy, xx = np.nonzero(lab == i)
        if len(xx) < 60: continue
        p = np.c_[xx, yy].astype(float)
        # order points along the principal direction of a smooth curve
        c = p.mean(0); u = np.linalg.svd(p - c)[2][0]
        p = p[np.argsort((p - c) @ u)]
        p = ndi.gaussian_filter1d(p, 4, axis=0, mode='nearest')
        L = np.r_[0, np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1))]
        if L[-1] < 110: continue                     # fragments are not structural folds
        p = p[(L > 0.08 * L[-1]) & (L < 0.92 * L[-1])][::2]
        segs = fit_curve(p, 1e9)                     # one cubic: the fold's overall gesture
        s0 = segs[0]
        d = f"M {fmt(M(s0[0])[0])} {fmt(M(s0[0])[1])} C {fmt(M(s0[1])[0])} {fmt(M(s0[1])[1])} {fmt(M(s0[2])[0])} {fmt(M(s0[2])[1])} {fmt(M(s0[3])[0])} {fmt(M(s0[3])[1])}"
        res.append(dict(x=float(p[:, 0].mean()), len=len(xx), d=d))
    return sorted(res, key=lambda r: r['x'])

def trace_letters(up=3, sigma=2.0):
    """Production silhouette: potrace on a 3x super-sampled, edge-smoothed alpha, then cleanup."""
    import potrace, re
    a = Image.open(f'{HERE}/reference/approved_wordmark_reference.png').split()[3]
    x0, y0 = X0 - 10, Y0 - 10
    a = a.crop((x0, y0, xs.max() + 11, Y1 + 11)); a = a.resize((a.width * up, a.height * up), Image.BICUBIC)
    arr = ndi.gaussian_filter(np.array(a).astype(float), sigma)
    plist = potrace.Bitmap(arr >= 127.5).trace(turdsize=50, turnpolicy=potrace.POTRACE_TURNPOLICY_MINORITY,
                                                alphamax=1.0, opticurve=True, opttolerance=0.35)
    def m(p): return ((np.array([p.x, p.y]) / up + [x0, y0]) - [X0, Y0]) * UNIT
    out = []
    for curve in plist:
        st = m(curve.start_point); d = [f'M {fmt(st[0])} {fmt(st[1])}']
        for seg in curve.segments:
            if seg.is_corner:
                c = m(seg.c); e = m(seg.end_point); d.append(f'L {fmt(c[0])} {fmt(c[1])} L {fmt(e[0])} {fmt(e[1])}')
            else:
                c1 = m(seg.c1); c2 = m(seg.c2); e = m(seg.end_point)
                d.append(f'C {fmt(c1[0])} {fmt(c1[1])} {fmt(c2[0])} {fmt(c2[1])} {fmt(e[0])} {fmt(e[1])}')
        d.append('Z')
        dd, n = simplify_path(' '.join(d))
        nums = np.array(list(map(float, re.findall(r'-?\d+\.?\d*', dd)))).reshape(-1, 2)
        if nums[:, 0].min() < -5: continue            # potrace frame path
        out.append((nums[:, 0].min(), dd, n))
    return [dict(d=dd, nodes=n) for _, dd, n in sorted(out)]

if __name__ == '__main__':
    letters = trace_letters()
    fl = folds()
    W_units = (xs.max() - X0 + 1) * UNIT
    geo = dict(title='WFS wordmark master geometry v1.0',
               units='master units; cap height = 1000, origin at top-left of the letterforms',
               method='potrace (3x super-sampled, edge-smoothed alpha) + straight-stroke cleanup + axis snapping',
               width=round(float(W_units), 2), height=1000.0,
               reference=dict(file='reference/approved_wordmark_reference.png', px_per_unit=1 / UNIT,
                              origin_px=[int(X0), int(Y0)]),
               letters={k: l for k, l in zip(['W', 'F', 'S'], letters)},
               folds=[dict(d=f['d']) for f in fl])
    assert len(letters) == 3
    json.dump(geo, open(f'{HERE}/master/wordmark_geometry.json', 'w'), indent=1)
    print('letters', {k: v['nodes'] for k, v in geo['letters'].items()}, 'folds', len(fl))
