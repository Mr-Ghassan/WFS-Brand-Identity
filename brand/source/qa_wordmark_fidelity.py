"""QA: compare wordmark vector master with the approved reference raster."""
import json, io, os, sys, numpy as np, cairosvg
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
out_dir = sys.argv[1] if len(sys.argv) > 1 else '/tmp'
g = json.load(open(f'{HERE}/master/wordmark_geometry.json'))
ref = np.array(Image.open(f'{HERE}/reference/approved_wordmark_reference.png').convert('RGBA'))
H, W = ref.shape[:2]; s = g['reference']['px_per_unit']; o = g['reference']['origin_px']
d = ' '.join(v['d'] for v in g['letters'].values())
svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"><g transform="translate({o[0]},{o[1]}) scale({s})"><path d="{d}" fill-rule="nonzero"/></g></svg>'
m = np.array(Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode()))))[..., 3] >= 128
A = ref[..., 3] >= 128
print('wordmark IoU', round(float((A & m).sum() / (A | m).sum()), 4), 'xor px', int((A ^ m).sum()))
viz = np.full((H, W, 3), 255, np.uint8)
viz[A & m] = (60, 60, 70); viz[A & ~m] = (255, 0, 0); viz[~A & m] = (0, 140, 255)
Image.fromarray(viz).crop((200, 150, 1950, 580)).save(f'{out_dir}/wm_xor.png')
# outline overlay with nodes
nodes = []
import re
svg2 = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W*2}" height="{H*2}"><rect width="100%" height="100%" fill="#fff"/><g transform="scale(2) translate({o[0]},{o[1]}) scale({s})"><path d="{d}" fill="#dfe6ea" stroke="#d0103a" stroke-width="{0.6/s}"/></g></svg>'
Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg2.encode()))).convert('RGB').save(f'{out_dir}/wm_outline.png')
