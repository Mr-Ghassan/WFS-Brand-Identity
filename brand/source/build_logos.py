"""Export the complete WFS logo matrix (SVG master files, vector PDF, transparent PNG)."""
import os, json, io, sys
import cairosvg
import brand_config as B
import logo_lib as L

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RECORDS = []   # asset index rows

def save(group, name, inner, box, title, sizes, variant, colour, backgrounds, purpose, size_axis='width', pad=0.0):
    d = {k: os.path.join(ROOT, group, k) for k in ('svg', 'pdf', 'png')}
    for p in d.values(): os.makedirs(p, exist_ok=True)
    svg = L.svg_doc(inner, box, title, pad=pad)
    open(f"{d['svg']}/{name}.svg", 'w').write(svg)
    cairosvg.svg2pdf(bytestring=svg.encode(), write_to=f"{d['pdf']}/{name}.pdf")
    pngs = []
    x0, y0, w, h = box
    for s in sizes:
        kw = dict(output_width=s) if (size_axis == 'width' or w >= h) else dict(output_height=s)
        if size_axis == 'height': kw = dict(output_height=s)
        out = f"{d['png']}/{name}_{s}px.png"
        cairosvg.svg2png(bytestring=svg.encode(), write_to=out, **kw)
        pngs.append(os.path.basename(out))
    RECORDS.append(dict(asset=name, group=group, purpose=purpose, variant=variant, colour=colour,
                        backgrounds=backgrounds, svg=f'{group}/svg/{name}.svg', pdf=f'{group}/pdf/{name}.pdf',
                        png=[f'{group}/png/{p}' for p in pngs]))

P = B.ICON_COLOURWAYS
MAIN = [512, 1024, 2048, 4096]; SEC = [512, 1024, 2048]
LIGHT_BG = '#F3F5F2, white, light photography'
DARK_BG = '#022329, #0E3D42, black, dark photography'

def icons():
    box = L.icon_box()
    spec = [
        ('WFS_Icon_Primary', L.icon_paths(P['primary']['blades']), 'Full colour (flat)', 'Mint / Teal / Deep / Teal / Dark', LIGHT_BG, 'Primary icon, light grounds', MAIN),
        ('WFS_Icon_Inverse', L.icon_paths(P['reverse']['blades']), 'Full colour inverse (flat)', 'Mint / Teal / Teal 800 / Teal / Teal 700', DARK_BG, 'Primary icon, dark grounds', MAIN),
        ('WFS_Icon_Flat_Teal', L.icon_mono(B.HEX['wfs-teal']), 'One colour', '#14B8A6', '#022329, #0E3D42, white, #F3F5F2', 'One-colour brand teal', SEC),
        ('WFS_Icon_Dark', L.icon_mono(B.HEX['wfs-dark']), 'One colour', '#022329', LIGHT_BG, 'One-colour dark (documents, UI, print)', SEC),
        ('WFS_Icon_White', L.icon_mono('#FFFFFF'), 'One colour', '#FFFFFF', DARK_BG, 'One-colour reversed', SEC),
        ('WFS_Icon_Black', L.icon_mono('#000000'), 'One colour', '#000000', 'white, light neutral grounds', 'Black-only reproduction (fax, stamps, engraving)', SEC),
        ('WFS_Icon_Monochrome', L.icon_paths(L.MONO_TONES['mono_dark']), 'Greyscale tonal', 'Greys', 'white, light grounds', 'Greyscale print (light grounds)', SEC),
        ('WFS_Icon_Monochrome_Light', L.icon_paths(L.MONO_TONES['mono_light']), 'Greyscale tonal (light)', 'Light greys', 'black, dark grounds', 'Greyscale print (dark grounds)', SEC),
        ('WFS_Icon_Premium', L.icon_premium('dark', 'ip'), 'Premium display', 'Premium gradient set (dark ground)', DARK_BG, 'Launch, keynote, hero and event use only', MAIN),
        ('WFS_Icon_Premium_Light', L.icon_premium('light', 'ipl'), 'Premium display', 'Premium gradient set (light ground)', LIGHT_BG, 'Premium display on light grounds', MAIN),
    ]
    for name, inner, var, col, bg, purpose, sizes in spec:
        save('icon', name, inner, box, f'WFS icon — {var}', sizes, var, col, bg, purpose, size_axis='height')

def wordmarks():
    box = L.word_box()
    spec = [
        ('WFS_Wordmark_Primary', L.wordmark_paths(B.HEX['wfs-dark']), 'Primary (WFS Dark)', '#022329', LIGHT_BG, 'Primary wordmark', [1024, 2048, 4096]),
        ('WFS_Wordmark_Inverse', L.wordmark_paths(B.HEX['wfs-offwhite']), 'Inverse (Off-White)', '#F3F5F2', DARK_BG, 'Wordmark on dark grounds', [1024, 2048, 4096]),
        ('WFS_Wordmark_White', L.wordmark_paths('#FFFFFF'), 'One colour', '#FFFFFF', DARK_BG, 'Pure white reproduction', [1024, 2048]),
        ('WFS_Wordmark_Black', L.wordmark_paths('#000000'), 'One colour / monochrome', '#000000', 'white, light grounds', 'Black-only / greyscale reproduction', [1024, 2048]),
        ('WFS_Wordmark_Teal', L.wordmark_paths(B.HEX['wfs-teal']), 'One colour', '#14B8A6', '#022329, #0E3D42', 'Accent use on dark grounds only', [1024, 2048]),
        ('WFS_Wordmark_Premium', L.wordmark_premium('dark', 'wp'), 'Premium display', 'Off-white → Mint 200 + teal folds', DARK_BG, 'Launch / hero display only', [1024, 2048, 4096]),
        ('WFS_Wordmark_Premium_Light', L.wordmark_premium('light', 'wpl'), 'Premium display', 'Deep → Dark + mint folds', LIGHT_BG, 'Premium display on light grounds', [1024, 2048, 4096]),
    ]
    for name, inner, var, col, bg, purpose, sizes in spec:
        save('wordmark', name, inner, box, f'WFS wordmark — {var}', sizes, var, col, bg, purpose)

def lockups():
    D, O, T, M = B.HEX['wfs-dark'], B.HEX['wfs-offwhite'], B.HEX['wfs-teal'], B.HEX['wfs-mint']
    spec = [
        ('WFS_Logo_Horizontal_Primary', 'horizontal', L.icon_paths(P['primary']['blades']), L.wordmark_paths(D), {}, 'PRIMARY — full colour', 'Primary icon + #022329', LIGHT_BG, 'Primary logo', [1024, 2048, 4096]),
        ('WFS_Logo_Horizontal_Inverse', 'horizontal', L.icon_paths(P['reverse']['blades']), L.wordmark_paths(O), {}, 'Inverse — full colour', 'Inverse icon + #F3F5F2', DARK_BG, 'Primary logo on dark grounds', [1024, 2048, 4096]),
        ('WFS_Logo_Horizontal_Dark', 'horizontal', L.icon_mono(D), L.wordmark_paths(D), {}, 'One colour dark', '#022329', LIGHT_BG, 'Documents, forms, one-colour print', [1024, 2048]),
        ('WFS_Logo_Horizontal_White', 'horizontal', L.icon_mono('#FFFFFF'), L.wordmark_paths('#FFFFFF'), {}, 'One colour white', '#FFFFFF', DARK_BG, 'Reversed one colour, photography', [1024, 2048]),
        ('WFS_Logo_Horizontal_Black', 'horizontal', L.icon_mono('#000000'), L.wordmark_paths('#000000'), {}, 'One colour black', '#000000', 'white, light grounds', 'Black-only reproduction', [1024, 2048]),
        ('WFS_Logo_Horizontal_Monochrome', 'horizontal', L.icon_paths(L.MONO_TONES['mono_dark']), L.wordmark_paths('#1B1F1F'), {}, 'Greyscale', 'Greys', 'white, light grounds', 'Greyscale print', [1024, 2048]),
        ('WFS_Logo_Horizontal_Monochrome_Light', 'horizontal', L.icon_paths(L.MONO_TONES['mono_light']), L.wordmark_paths('#FFFFFF'), {}, 'Greyscale (light)', 'Light greys', 'black, dark grounds', 'Greyscale print on dark', [1024, 2048]),
        ('WFS_Logo_Horizontal_Premium', 'horizontal', L.icon_premium('dark', 'hp'), L.wordmark_premium('dark', 'hw'), {}, 'Premium display', 'Premium gradients', DARK_BG, 'Launch, keynote, event screens', [1024, 2048, 4096]),
        ('WFS_Logo_Horizontal_Premium_Light', 'horizontal', L.icon_premium('light', 'hpl'), L.wordmark_premium('light', 'hwl'), {}, 'Premium display (light)', 'Premium gradients', LIGHT_BG, 'Premium display on light grounds', [1024, 2048]),
        ('WFS_Logo_Full_English', 'full', L.icon_paths(P['primary']['blades']), L.wordmark_paths(D), dict(text_colour=B.HEX['wfs-deep']), 'Full lockup (descriptor)', 'Primary + Deep Teal descriptor', LIGHT_BG, 'Formal / first-contact communication', [1024, 2048, 4096]),
        ('WFS_Logo_Full_English_Inverse', 'full', L.icon_paths(P['reverse']['blades']), L.wordmark_paths(O), dict(text_colour=M), 'Full lockup (descriptor) inverse', 'Inverse + Mint descriptor', DARK_BG, 'Formal use on dark grounds', [1024, 2048]),
        ('WFS_Logo_Stacked_Primary', 'stacked', L.icon_paths(P['primary']['blades']), L.wordmark_paths(D), {}, 'Stacked', 'Primary', LIGHT_BG, 'Square / vertical formats', [1024, 2048]),
        ('WFS_Logo_Stacked_Inverse', 'stacked', L.icon_paths(P['reverse']['blades']), L.wordmark_paths(O), {}, 'Stacked inverse', 'Inverse', DARK_BG, 'Splash screens, square formats', [1024, 2048]),
        ('WFS_Logo_Endorsed_Primary', 'horizontal', L.icon_paths(P['primary']['blades']), L.wordmark_paths(D), dict(endorse_colour=B.HEX['slate-600']), 'Endorsed (A WUSOOL Tech Product)', 'Primary + Slate 600', LIGHT_BG, 'Corporate / investor contexts only', [1024, 2048]),
        ('WFS_Logo_Endorsed_Inverse', 'horizontal', L.icon_paths(P['reverse']['blades']), L.wordmark_paths(O), dict(endorse_colour=B.HEX['text-dark-2']), 'Endorsed inverse', 'Inverse + Mist 300', DARK_BG, 'Corporate contexts on dark', [1024, 2048]),
    ]
    if L.arabic_font_available():
        spec.append(('WFS_Logo_Full_Bilingual', 'bilingual', L.icon_paths(P['primary']['blades']), L.wordmark_paths(D),
                     dict(text_colour=B.HEX['wfs-deep']), 'Full bilingual', 'Primary', LIGHT_BG, 'Bilingual formal use', [1024, 2048]))
    else:
        print('NOTE: Myriad Arabic not found in', B.font_dir(), '-> WFS_Logo_Full_Bilingual not generated (no substitute font used).')
    for name, kind, icon, wm, kw, var, col, bg, purpose, sizes in spec:
        inner, box = L.lockup(kind, icon, wm, **kw)
        save('logo', name, inner, box, f'WFS logo — {var}', sizes, var, col, bg, purpose)

if __name__ == '__main__':
    icons(); wordmarks(); lockups()
    json.dump(RECORDS, open(os.path.join(ROOT, 'source', 'master', 'asset_records_logos.json'), 'w'), indent=1)
    print(len(RECORDS), 'logo assets')
