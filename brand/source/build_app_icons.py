"""WFS app icon + favicon system."""
import os, json, io
import cairosvg
from PIL import Image
import brand_config as B
import logo_lib as L

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
APP = os.path.join(ROOT, 'icon', 'app'); FAV = os.path.join(ROOT, 'icon', 'favicon')
for p in (APP, FAV): os.makedirs(p, exist_ok=True)
P = B.ICON_COLOURWAYS
REC = []

def png(svg, path, size):
    cairosvg.svg2png(bytestring=svg.encode(), write_to=path, output_width=size, output_height=size)

def square(inner_bg, icon_inner, icon_d, title, canvas=1024):
    """Full-bleed square app artwork (no corner rounding: platforms apply their own mask)."""
    s = icon_d / 1000.0
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {canvas} {canvas}" width="{canvas}" height="{canvas}">'
            f'<title>{title}</title>{inner_bg}<g transform="translate({canvas/2} {canvas/2}) scale({s:.5f})">{icon_inner}</g></svg>\n')

def bg_dark(c=1024, glow=True):
    g = (f'<radialGradient id="amb" gradientUnits="userSpaceOnUse" cx="{c*0.62}" cy="{c*0.30}" r="{c*0.75}">'
         f'<stop offset="0" stop-color="#14B8A6" stop-opacity="0.30"/><stop offset="0.55" stop-color="#0E3D42" stop-opacity="0"/></radialGradient>') if glow else ''
    return (f'<defs><linearGradient id="deep" x1="0" y1="0" x2="0.35" y2="1"><stop offset="0" stop-color="#0E3D42"/>'
            f'<stop offset="1" stop-color="#022329"/></linearGradient>{g}</defs>'
            f'<rect width="{c}" height="{c}" fill="url(#deep)"/>' + (f'<rect width="{c}" height="{c}" fill="url(#amb)"/>' if glow else ''))

def bg_light(c=1024):
    return (f'<defs><linearGradient id="lt" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFFFF"/>'
            f'<stop offset="1" stop-color="#F3F5F2"/></linearGradient></defs><rect width="{c}" height="{c}" fill="url(#lt)"/>')

def rec(name, purpose, fmt, variant, bg):
    REC.append(dict(asset=name, group='icon', purpose=purpose, format=fmt, variant=variant, backgrounds=bg))

# ---- master app icons (1024, full bleed, platform masks applied by OS)
ICON_D = 600      # 58.6 % of canvas: inside the iOS squircle and Android 66 dp safe zone
masters = {
    'WFS_AppIcon_Dark': square(bg_dark(), L.icon_paths(P['reverse']['blades']), ICON_D, 'WFS app icon — dark (primary)'),
    'WFS_AppIcon_Light': square(bg_light(), L.icon_paths(P['primary']['blades']), ICON_D, 'WFS app icon — light'),
    'WFS_AppIcon_Premium': square(bg_dark(), L.icon_premium('dark', 'ap'), ICON_D, 'WFS app icon — premium (store / marketing)'),
}
# compact artwork for <= 64 px: larger icon, no glow, one flat ground
compact = square(f'<rect width="1024" height="1024" fill="#022329"/>', L.icon_paths(P['reverse']['blades']), 800, 'WFS app icon — compact (64 px and below)')
for name, svg in masters.items():
    open(f'{APP}/{name}_master.svg', 'w').write(svg)
    for s in (1024, 512, 256, 128):
        png(svg, f'{APP}/{name}_{s}.png', s)
    rec(f'{name}_master.svg + 1024/512/256/128 PNG', 'App icon master (square, unmasked)', 'SVG, PNG', name.split('_')[-1], 'n/a (opaque)')
open(f'{APP}/WFS_AppIcon_Compact_master.svg', 'w').write(compact)
for s in (64, 48, 32, 16):
    png(compact, f'{APP}/WFS_AppIcon_Dark_{s}.png', s)
rec('WFS_AppIcon_Dark_64/48/32/16.png', 'Small app icon sizes (compact artwork)', 'PNG', 'Dark compact', 'n/a (opaque)')

# ---- Android adaptive icon layers (108 dp canvas @4x = 432 px; safe zone 66 dp)
fg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 432 432" width="432" height="432"><title>WFS adaptive icon — foreground</title>'
      f'<g transform="translate(216 216) scale(0.24)">{L.icon_paths(P["reverse"]["blades"])}</g></svg>\n')
bgl = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 432 432" width="432" height="432"><title>WFS adaptive icon — background</title>{bg_dark(432)}</svg>\n'
mono = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 432 432" width="432" height="432"><title>WFS adaptive icon — monochrome (themed)</title>'
        f'<g transform="translate(216 216) scale(0.24)">{L.icon_mono("#FFFFFF", "gap32")}</g></svg>\n')
for n, s in (('foreground', fg), ('background', bgl), ('monochrome', mono)):
    open(f'{APP}/WFS_Android_Adaptive_{n}.svg', 'w').write(s); png(s, f'{APP}/WFS_Android_Adaptive_{n}_432.png', 432)
rec('WFS_Android_Adaptive_foreground/background/monochrome', 'Android adaptive + themed icon layers (108 dp @4x)', 'SVG, PNG', 'Adaptive', 'layered')

# ---- favicons
# adaptive SVG favicon: follows the browser/OS colour scheme, transparent
pr, rv = P['primary']['blades'], P['reverse']['blades']
css = ''.join(f'#b{i+1}{{fill:{c}}}' for i, c in enumerate(pr))
css_d = ''.join(f'#b{i+1}{{fill:{c}}}' for i, c in enumerate(rv))
paths = ''.join(f'<path id="b{i+1}" d="{L.ICON["blades"][b]["paths"]["solid"]}"/>' for i, b in enumerate(L.BLADES))
bx = L.icon_box(0.02)
fav_svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{L.f(bx[0])} {L.f(bx[1])} {L.f(bx[2])} {L.f(bx[3])}">'
           f'<style>{css}@media (prefers-color-scheme:dark){{{css_d}}}</style>{paths}</svg>\n')
open(f'{FAV}/favicon.svg', 'w').write(fav_svg)
rec('favicon.svg', 'Adaptive SVG favicon (light/dark aware, transparent)', 'SVG', 'Primary / Inverse', 'browser tabs, light + dark')

# raster favicon tile: rounded dark tile keeps the mark visible in light and dark tabs
def tile(size, icon_frac, variant='solid'):
    c = 1024; r = c * 0.22
    inner = (f'<rect width="{c}" height="{c}" rx="{r}" fill="#022329"/>'
             f'<g transform="translate(512 512) scale({icon_frac * c / 1000:.5f})">{L.icon_paths(P["reverse"]["blades"], variant)}</g>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {c} {c}" width="{c}" height="{c}">{inner}</svg>'
for s in (16, 32, 48):
    png(tile(s, 0.84), f'{FAV}/favicon-{s}x{s}.png', s)
imgs = [Image.open(f'{FAV}/favicon-{s}x{s}.png') for s in (16, 32, 48)]
imgs[2].save(f'{FAV}/favicon.ico', sizes=[(16, 16), (32, 32), (48, 48)], append_images=imgs[:2])
rec('favicon.ico (16/32/48) + favicon-16/32/48 PNG', 'Legacy / raster favicon', 'ICO, PNG', 'Dark tile', 'browser tabs, light + dark')
png(masters['WFS_AppIcon_Dark'], f'{FAV}/apple-touch-icon.png', 180)
png(masters['WFS_AppIcon_Dark'], f'{FAV}/android-chrome-192x192.png', 192)
png(masters['WFS_AppIcon_Dark'], f'{FAV}/android-chrome-512x512.png', 512)
maskable = square(bg_dark(), L.icon_paths(P['reverse']['blades']), 520, 'WFS maskable icon')
png(maskable, f'{FAV}/maskable-512x512.png', 512)
rec('apple-touch-icon.png (180), android-chrome 192/512, maskable 512', 'Home-screen / PWA icons', 'PNG', 'Dark', 'n/a (opaque)')
json.dump({'name': 'WFS — Wusool Financial System', 'short_name': 'WFS',
           'icons': [{'src': 'android-chrome-192x192.png', 'sizes': '192x192', 'type': 'image/png'},
                     {'src': 'android-chrome-512x512.png', 'sizes': '512x512', 'type': 'image/png'},
                     {'src': 'maskable-512x512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'maskable'}],
           'theme_color': '#022329', 'background_color': '#022329', 'display': 'standalone'},
          open(f'{FAV}/site.webmanifest', 'w'), indent=2)
open(f'{FAV}/head-snippet.html', 'w').write(
    '<link rel="icon" href="/favicon.ico" sizes="48x48">\n<link rel="icon" href="/favicon.svg" type="image/svg+xml">\n'
    '<link rel="apple-touch-icon" href="/apple-touch-icon.png">\n<link rel="manifest" href="/site.webmanifest">\n'
    '<meta name="theme-color" content="#022329">\n')
rec('site.webmanifest, head-snippet.html', 'Web integration', 'JSON, HTML', '-', '-')
json.dump(REC, open(os.path.join(ROOT, 'source', 'master', 'asset_records_appicons.json'), 'w'), indent=1)
print('app/favicon done', len(os.listdir(APP)), len(os.listdir(FAV)))
