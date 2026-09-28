"""WFS brand geometry toolkit: Bezier fitting (Schneider), cubic Bezier chains,
circular arcs, curve intersection and SVG path emission.
Pure numpy; used by the logo master build scripts."""
import numpy as np

# ---------------------------------------------------------------- cubic helpers
def bez(P, t):
    t = np.asarray(t, float)[..., None]
    mt = 1 - t
    return (mt**3) * P[0] + 3 * mt**2 * t * P[1] + 3 * mt * t**2 * P[2] + t**3 * P[3]

def bez_d(P, t):
    t = np.asarray(t, float)[..., None]
    mt = 1 - t
    return 3 * mt**2 * (P[1] - P[0]) + 6 * mt * t * (P[2] - P[1]) + 3 * t**2 * (P[3] - P[2])

def split(P, t):
    """De Casteljau split (valid for t outside [0,1] -> extrapolation)."""
    P = [np.asarray(p, float) for p in P]
    a = P[0] + (P[1] - P[0]) * t; b = P[1] + (P[2] - P[1]) * t; c = P[2] + (P[3] - P[2]) * t
    d = a + (b - a) * t; e = b + (c - b) * t; f = d + (e - d) * t
    return [P[0], a, d, f], [f, e, c, P[3]]

def sub(P, t0, t1):
    if abs(t1 - t0) < 1e-12:
        p = bez(np.array(P), t0); return [p, p, p, p]
    _, right = split(P, t0)
    s = (t1 - t0) / (1 - t0) if abs(1 - t0) > 1e-12 else 1.0
    left, _ = split(right, s)
    return left

# ---------------------------------------------------------------- Schneider fit
def _chord_params(pts):
    d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))]
    return d / d[-1]

def _fit_one(pts, u, t1, t2):
    p0, p3 = pts[0], pts[-1]
    A1 = (3 * (1 - u)**2 * u)[:, None] * t1
    A2 = (3 * (1 - u) * u**2)[:, None] * t2
    C = np.array([[np.sum(A1 * A1), np.sum(A1 * A2)], [np.sum(A1 * A2), np.sum(A2 * A2)]])
    base = bez(np.array([p0, p0, p3, p3]), u)
    X = np.array([np.sum(A1 * (pts - base)), np.sum(A2 * (pts - base))])
    det = C[0, 0] * C[1, 1] - C[0, 1] * C[1, 0]
    seg = np.linalg.norm(p3 - p0)
    if abs(det) > 1e-12:
        a1 = (X[0] * C[1, 1] - X[1] * C[0, 1]) / det
        a2 = (C[0, 0] * X[1] - C[1, 0] * X[0]) / det
    else:
        a1 = a2 = seg / 3
    if a1 < 1e-6 * seg or a2 < 1e-6 * seg:
        a1 = a2 = seg / 3
    return np.array([p0, p0 + t1 * a1, p3 + t2 * a2, p3])

def _reparam(P, pts, u):
    for _ in range(1):
        d = bez(P, u) - pts
        d1 = bez_d(P, u)
        # second derivative
        t = u[:, None]
        d2 = 6 * (1 - t) * (P[2] - 2 * P[1] + P[0]) + 6 * t * (P[3] - 2 * P[2] + P[1])
        num = np.sum(d * d1, 1); den = np.sum(d1 * d1 + d * d2, 1)
        u = np.clip(u - np.where(np.abs(den) > 1e-12, num / den, 0), 0, 1)
    return u

def fit_curve(pts, tol, t1=None, t2=None, _depth=0):
    """Fit a G1-continuous chain of cubic Beziers to ordered points."""
    pts = np.asarray(pts, float)
    if t1 is None:
        t1 = pts[min(4, len(pts) - 1)] - pts[0]; t1 /= np.linalg.norm(t1)
    if t2 is None:
        t2 = pts[max(-5, -len(pts))] - pts[-1]; t2 /= np.linalg.norm(t2)
    if len(pts) == 2:
        dist = np.linalg.norm(pts[1] - pts[0]) / 3
        return [np.array([pts[0], pts[0] + t1 * dist, pts[1] + t2 * dist, pts[1]])]
    u = _chord_params(pts)
    P = _fit_one(pts, u, t1, t2)
    for _ in range(12):
        err = np.linalg.norm(bez(P, u) - pts, axis=1)
        if err.max() < tol: return [P]
        u = _reparam(P, pts, u)
        P = _fit_one(pts, u, t1, t2)
    err = np.linalg.norm(bez(P, u) - pts, axis=1)
    if err.max() < tol or len(pts) < 8 or _depth > 12: return [P]
    k = int(np.clip(err.argmax(), 3, len(pts) - 4))
    tc = pts[k - 3] - pts[k + 3]; tc /= np.linalg.norm(tc)
    return fit_curve(pts[:k + 1], tol, t1, tc, _depth + 1) + fit_curve(pts[k:], tol, -tc, t2, _depth + 1)

# ---------------------------------------------------------------- curve objects
class Chain:
    """Cubic Bezier chain, global parameter u in [0, n] (extrapolates outside)."""
    kind = 'chain'
    def __init__(self, segs): self.segs = [np.array(s, float) for s in segs]
    @property
    def n(self): return len(self.segs)
    def _loc(self, u):
        i = int(np.clip(np.floor(u), 0, self.n - 1)); return i, u - i
    def at(self, u):
        i, t = self._loc(u); return bez(self.segs[i], t)
    def dense(self, u0=-0.25, u1=None, step=1e-3):
        if u1 is None: u1 = self.n + 0.25
        us = np.arange(u0, u1 + step, step)
        idx = np.clip(np.floor(us), 0, self.n - 1).astype(int)
        t = (us - idx)[:, None]; S = np.array(self.segs)[idx]
        mt = 1 - t
        pts = mt**3 * S[:, 0] + 3 * mt**2 * t * S[:, 1] + 3 * mt * t**2 * S[:, 2] + t**3 * S[:, 3]
        return us, pts
    def subpath(self, u0, u1):
        """Return list of cubic segments from u0 to u1 (either direction)."""
        rev = u1 < u0
        a, b = (u1, u0) if rev else (u0, u1)
        i0, t0 = self._loc(a); i1, t1 = self._loc(b)
        out = []
        if i0 == i1:
            out.append(sub(self.segs[i0], t0, t1))
        else:
            out.append(sub(self.segs[i0], t0, 1.0))
            for k in range(i0 + 1, i1): out.append(self.segs[k])
            out.append(sub(self.segs[i1], 0.0, t1))
        if rev: out = [s[::-1] for s in out[::-1]]
        return [np.array(s) for s in out]
    def offset(self, dist, tol=0.05):
        """Offset curve (left normal positive) refit as a chain."""
        us, p = self.dense(-0.3, self.n + 0.3, 2e-3)
        d = np.gradient(p, axis=0); d /= np.linalg.norm(d, axis=1, keepdims=True)
        nrm = np.c_[-d[:, 1], d[:, 0]]
        return Chain(fit_curve(p + dist * nrm, tol))

class Arc:
    kind = 'arc'
    def __init__(self, c, r, ref_angle):
        self.c = np.asarray(c, float); self.r = float(r); self.ref = ref_angle  # angle inside observed run
    def point(self, ang): return self.c + self.r * np.array([np.cos(ang), np.sin(ang)])
    def angle(self, p): return np.arctan2(p[1] - self.c[1], p[0] - self.c[0])
    def offset(self, dist): return Arc(self.c, self.r + dist, self.ref)

def fit_circle(p):
    p = np.asarray(p, float)
    A = np.c_[2 * p[:, 0], 2 * p[:, 1], np.ones(len(p))]; b = (p**2).sum(1)
    cx, cy, k = np.linalg.lstsq(A, b, rcond=None)[0]
    r = np.sqrt(k + cx * cx + cy * cy)
    res = np.hypot(p[:, 0] - cx, p[:, 1] - cy) - r
    return np.array([cx, cy]), r, res

def intersect_arc_chain(arc, chain, near):
    """Intersection of a circle and a chain closest to `near`; returns (point, u)."""
    us, pts = chain.dense(-0.6, chain.n + 0.6, 5e-4)
    f = np.hypot(*(pts - arc.c).T) - arc.r
    idx = np.nonzero(np.sign(f[:-1]) != np.sign(f[1:]))[0]
    if len(idx) == 0:
        raise ValueError('no intersection')
    best = None
    for i in idx:
        a, b = us[i], us[i + 1]
        for _ in range(60):
            m = (a + b) / 2
            fm = np.hypot(*(chain.at(m) - arc.c)) - arc.r
            fa = np.hypot(*(chain.at(a) - arc.c)) - arc.r
            if np.sign(fm) == np.sign(fa): a = m
            else: b = m
        u = (a + b) / 2; p = chain.at(u)
        d = np.linalg.norm(p - near)
        if best is None or d < best[0]: best = (d, p, u)
    return best[1], best[2]

# ---------------------------------------------------------------- SVG emission
def fmt(v, nd=2):
    s = f'{v:.{nd}f}'.rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s

def P(p, nd=2): return f'{fmt(p[0], nd)} {fmt(p[1], nd)}'

def arc_cmd(arc, p_from, p_to, ccw_hint):
    """SVG arc command from p_from to p_to on `arc` passing through ref angle side."""
    a0 = arc.angle(p_from); a1 = arc.angle(p_to); ar = arc.ref
    def norm(x): return x % (2 * np.pi)
    # positive (increasing angle, SVG sweep=1 in y-down coords) span
    span_pos = norm(a1 - a0); ref_pos = norm(ar - a0)
    if ref_pos <= span_pos:
        sweep, span = 1, span_pos
    else:
        sweep, span = 0, 2 * np.pi - span_pos
    large = 1 if span > np.pi else 0
    return f'A {fmt(arc.r)} {fmt(arc.r)} 0 {large} {sweep} {P(p_to)}', span, sweep

def arc_dense(arc, p_from, p_to, sweep, span, n=400):
    a0 = arc.angle(p_from)
    angs = a0 + (np.linspace(0, span, n) if sweep == 1 else -np.linspace(0, span, n))
    return np.c_[arc.c[0] + arc.r * np.cos(angs), arc.c[1] + arc.r * np.sin(angs)]

def arc_to_beziers(arc, p_from, sweep, span):
    """Approximate an arc by cubic segments (<= 90deg each)."""
    n = max(1, int(np.ceil(span / (np.pi / 2) - 1e-9)))
    a0 = arc.angle(p_from); d = (span / n) * (1 if sweep == 1 else -1)
    k = 4 / 3 * np.tan(d / 4)
    segs = []
    for i in range(n):
        t0 = a0 + i * d; t1 = t0 + d
        p0 = arc.point(t0); p3 = arc.point(t1)
        v0 = np.array([-np.sin(t0), np.cos(t0)]) * arc.r * k
        v1 = np.array([-np.sin(t1), np.cos(t1)]) * arc.r * k
        segs.append(np.array([p0, p0 + v0, p3 - v1, p3]))
    return segs

def segs_cmd(segs):
    return ' '.join(f'C {P(s[1])} {P(s[2])} {P(s[3])}' for s in segs)
