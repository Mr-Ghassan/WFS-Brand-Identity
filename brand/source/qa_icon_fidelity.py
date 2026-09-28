"""QA: compare the icon vector master against the approved reference raster.
Reports silhouette IoU and per-blade IoU, writes overlay/tip-crop previews."""
import json, io, sys, os, numpy as np, cairosvg
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
sys.argv += [] ; out_dir = sys.argv[1] if len(sys.argv) > 1 else '/tmp'
g = json.load(open(f'{HERE}/master/icon_geometry.json'))
ref = g['reference']; s = ref['px_per_unit']; C = ref['centre_px']
import vectorize_icon as V   # re-uses the segmentation of the reference
res = {}
for var in ('solid',):
    tot = None
    ious = {}
    for lbl, b in g['blades'].items():
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="1254" height="1254"><g transform="translate({C[0]},{C[1]}) scale({s})"><path d="{b["paths"][var]}"/></g></svg>'
        m = np.array(Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode()))))[..., 3] >= 128
        i = [k for k, v in V.__dict__.get('_ring_map', {}).items()] if False else None
        tot = m if tot is None else (tot | m)
        ious[lbl] = m
    A = V.inside
    sil = (A & tot).sum() / (A | tot).sum()
    # per blade: best matching reference region
    per = {}
    for lbl, m in ious.items():
        best = max(((V.full == i) & m).sum() / ((V.full == i) | m).sum() for i in range(1, 6))
        per[lbl] = round(float(best), 4)
    print(var, 'silhouette IoU', round(float(sil), 4), 'blade IoU', per, 'mean', round(float(np.mean(list(per.values()))), 4))
# hi-res preview with tip crops
cols = {'B1': '#dcdcdc', 'B2': '#e8b04a', 'B3': '#9c6b35', 'B4': '#d69a45', 'B5': '#333333'}
for var in ('solid', 'gap20'):
    body = ''.join(f'<path d="{g["blades"][l]["paths"][var]}" fill="{c}"/>' for l, c in cols.items())
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1200" viewBox="-560 -560 1120 1120"><rect x="-560" y="-560" width="1120" height="1120" fill="#fff"/>{body}</svg>'
    Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode()))).convert('RGB').save(f'{out_dir}/icon_{var}.png')
