"""Procedural art-direction renders for the guidelines (no stock imagery).
These illustrate the imagery criteria; production photography is commissioned/licensed separately."""
import numpy as np
from PIL import Image, ImageFilter
rng = np.random.default_rng(7)
OUT = 'img'

def grade(g, lo=(2, 35, 41), mid=(14, 110, 104), hi=(210, 245, 238)):
    g = np.clip(g, 0, 1)[..., None]
    lo, mid, hi = [np.array(c, float) for c in (lo, mid, hi)]
    return np.where(g < 0.5, lo + (mid - lo) * (g / 0.5), mid + (hi - mid) * ((g - 0.5) / 0.5))

def save(a, name):
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(f'{OUT}/{name}.jpg', quality=90)

W, H = 1800, 1200
y, x = np.mgrid[0:H, 0:W].astype(float)

# 1. architectural precision: ray-cast corridor with receding light fins
vx, vy = W * 0.58, H * 0.46
dx, dy = (x - vx), (y - vy)
aw, ah, fz = 1.0, 0.62, 520.0
tx = aw / np.maximum(np.abs(dx), 1e-3); ty = ah / np.maximum(np.abs(dy), 1e-3)
t = np.minimum(tx, ty) * fz                       # depth along the corridor (world units)
t = t / 1.0
wall = tx < ty
fins = (np.cos(2 * np.pi * t / 0.9) > 0.955) & wall & (t > 0.8)             # vertical light fins on the walls
slot = (~wall) & (dy < 0) & (np.abs(dx * t / fz) < 0.035)   # ceiling light slot
floor_ = (~wall) & (dy > 0)
fog = np.exp(-t / 9.0)
g = 0.10 + 0.22 * fog
g = g + fins * 0.55 * fog + slot * 0.55 * fog - 0.08 * wall * np.exp(-t / 2.0)
g = g + floor_ * (0.05 + 0.18 * np.exp(-(np.abs(dx) / 260) ** 2) * fog)
g = g + 0.35 * np.exp(-np.hypot(dx, dy) / 160)
img = grade(g) + rng.normal(0, 3.0, (H, W, 1))
im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.3))
im.save(f'{OUT}/art_architecture.jpg', quality=90)

# 2. macro material: anisotropic brushed surface with a curved lit edge (from the icon's blade)
n = rng.normal(0, 1, (H, W))
n = np.array(Image.fromarray(((n - n.min()) / np.ptp(n) * 255).astype(np.uint8)).filter(ImageFilter.BoxBlur(0)).resize((W, H)))
brushed = np.array(Image.fromarray(n).resize((W // 60, H), Image.BILINEAR).resize((W, H), Image.BICUBIC)).astype(float) / 255
cx, cy, r = W * 0.35, H * 1.35, H * 1.15
d = np.hypot(x - cx, y - cy) - r
edge = np.exp(-(d / 10) ** 2) * 0.9 + np.exp(-(d / 70) ** 2) * 0.25
base = np.where(d < 0, 0.62 - 0.35 * (y / H), 0.18 + 0.1 * (x / W))
g = base + (brushed - 0.5) * 0.10 + edge
save(grade(g, lo=(2, 30, 36), mid=(20, 150, 136), hi=(225, 250, 246)), 'art_material')

# 3. global infrastructure: orthographic globe as a node network
img = np.zeros((H, W)); R = 470; gx, gy = W * 0.58, H * 0.52
canvas = Image.new('L', (W, H), 0)
from PIL import ImageDraw
dr = ImageDraw.Draw(canvas)
tilt = np.radians(-18)
def proj(lat, lon):
    lat, lon = np.radians(lat), np.radians(lon)
    X = np.cos(lat) * np.sin(lon); Y = np.sin(lat); Z = np.cos(lat) * np.cos(lon)
    Y2 = Y * np.cos(tilt) - Z * np.sin(tilt); Z2 = Y * np.sin(tilt) + Z * np.cos(tilt)
    return gx + R * X, gy - R * Y2, Z2
for lat in range(-75, 90, 15):
    pts = [proj(lat, lo) for lo in range(-180, 181, 3)]
    for a, b in zip(pts[:-1], pts[1:]):
        if a[2] > 0 and b[2] > 0: dr.line([a[:2], b[:2]], fill=70, width=1)
for lon in range(-180, 180, 15):
    pts = [proj(la, lon) for la in range(-90, 91, 3)]
    for a, b in zip(pts[:-1], pts[1:]):
        if a[2] > 0 and b[2] > 0: dr.line([a[:2], b[:2]], fill=70, width=1)
nodes = [(rng.uniform(-60, 70), rng.uniform(-180, 180)) for _ in range(90)]
vis = [proj(*p) for p in nodes]; vis = [v for v in vis if v[2] > 0.1]
for i, a in enumerate(vis):
    for b in vis[i + 1:]:
        if np.hypot(a[0] - b[0], a[1] - b[1]) < 150: dr.line([a[:2], b[:2]], fill=120, width=1)
for v in vis: dr.ellipse([v[0] - 4, v[1] - 4, v[0] + 4, v[1] + 4], fill=255)
g = np.array(canvas.filter(ImageFilter.GaussianBlur(0.6))).astype(float) / 255
halo = np.exp(-np.abs(np.hypot(x - gx, y - gy) - R) / 40) * 0.25 + np.exp(-np.hypot(x - gx, y - gy) / 600) * 0.2
save(grade(0.06 + halo + g * 0.85), 'art_network')

# 4. photographic-style ground for logo-on-image tests: soft architectural light (dark) and daylight (light)
g = 0.35 + 0.35 * np.exp(-((x - W * 0.3) ** 2) / (2 * 420 ** 2)) - 0.18 * (y / H) + (np.cos(x / 38) > 0.96) * 0.05
im = Image.fromarray(np.clip(grade(g) + rng.normal(0, 3, (H, W, 1)), 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6))
im.save(f'{OUT}/art_photo_ground_dark.jpg', quality=90)
g = 0.78 + 0.14 * np.exp(-((x - W * 0.7) ** 2) / (2 * 500 ** 2)) - 0.1 * (y / H)
im = Image.fromarray(np.clip(grade(g, lo=(120, 150, 148), mid=(200, 222, 218), hi=(248, 250, 248)) + rng.normal(0, 2.5, (H, W, 1)), 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(5))
im.save(f'{OUT}/art_photo_ground_light.jpg', quality=90)
print('ok')
