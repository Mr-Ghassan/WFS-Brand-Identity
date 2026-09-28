"""WFS Brand Identity v1.0 — single source of truth for colour, typography and
logo proportions. Every build script imports this module."""
import os

VERSION = '1.0'
YEAR = '2026'
NAME = 'WFS'
NAME_EN = 'Wusool Financial System'
NAME_AR = 'نظام وصول المالي'
ENDORSEMENT = 'A WUSOOL Tech Product'

# ---------------------------------------------------------------------------
# COLOUR — the five official core colours (never altered)
# ---------------------------------------------------------------------------
CORE = {
    'wfs-dark':     dict(hex='#022329', name='WFS Dark',      desc='Near-black teal. Primary dark ground, primary text on light.'),
    'wfs-deep':     dict(hex='#0E3D42', name='WFS Deep Teal', desc='Secondary dark ground, surfaces on dark, depth in the icon.'),
    'wfs-teal':     dict(hex='#14B8A6', name='WFS Primary Teal', desc='Signature brand colour. Icon, accents, data highlights.'),
    'wfs-mint':     dict(hex='#7FE3D6', name='WFS Light Mint', desc='Light accent. Icon light blade, accents on dark, highlights.'),
    'wfs-offwhite': dict(hex='#F3F5F2', name='WFS Soft Off-White', desc='Primary light ground and text on dark.'),
}

# Derived tonal steps (NOT core colours — controlled intermediate steps)
DERIVED = {
    'teal-800': dict(hex='#115E5F', name='Teal 800', desc='Derived. Icon dark blade on dark grounds; deep data series.'),
    'teal-700': dict(hex='#0F7C74', name='Teal 700', desc='Derived. Accessible teal for text/links on light grounds.'),
    'teal-600': dict(hex='#11998B', name='Teal 600', desc='Derived. Hover / pressed state of Primary Teal.'),
    'teal-200': dict(hex='#B9EFE7', name='Mint 200', desc='Derived. Tints, selection, chart fills on light.'),
    'teal-100': dict(hex='#DDF5F1', name='Mint 100', desc='Derived. Subtle tinted surfaces on light.'),
    'slate-600': dict(hex='#4A5E61', name='Slate 600', desc='Derived neutral. Secondary text on light.'),
    'slate-400': dict(hex='#80918F', name='Slate 400', desc='Derived neutral. Tertiary text, captions, disabled.'),
    'line-200': dict(hex='#D6DEDB', name='Line 200', desc='Derived neutral. Borders and dividers on light.'),
    'paper-0':  dict(hex='#FFFFFF', name='White', desc='Pure white surface (cards, documents).'),
    'line-dark': dict(hex='#1E4A4F', name='Line Dark', desc='Derived. Borders and dividers on dark.'),
    'text-dark-2': dict(hex='#9DB5B3', name='Mist 300', desc='Derived. Secondary text on dark.'),
}

# Functional (semantic) colours for product UI — not brand colours
FUNCTIONAL = {
    'positive': dict(hex='#0F7C74', name='Positive', desc='Gains, credits, success (Teal 700).'),
    'negative': dict(hex='#B4232F', name='Negative', desc='Losses, debits in deficit, errors.'),
    'warning':  dict(hex='#B7791F', name='Warning', desc='Pending approvals, due soon.'),
    'info':     dict(hex='#2F6F9F', name='Info', desc='Neutral system information.'),
}

def ALL():
    d = {}
    d.update(CORE); d.update(DERIVED); d.update(FUNCTIONAL)
    return d

HEX = {k: v['hex'] for k, v in ALL().items()}

# Data visualisation (validated: lightness band, chroma, CVD & normal-vision separation, contrast)
DATAVIZ = {
    'light': ['#11A393', '#3067C9', '#C8691E', '#B94E8A'],   # on #FFFFFF / #F3F5F2
    'dark':  ['#12A594', '#5A8CE0', '#D6782C', '#C95C9E'],   # on #0E3D42 / #022329
    'sequential': ['#DDF5F1', '#B9EFE7', '#7FE3D6', '#14B8A6', '#0F7C74', '#0E3D42'],
}

# Semantic roles
ROLES = {
    'light': dict(background='#F3F5F2', surface='#FFFFFF', surface_alt='#DDF5F1', text='#022329', text_2='#4A5E61',
                  text_3='#80918F', border='#D6DEDB', primary='#14B8A6', primary_text='#0F7C74', accent='#7FE3D6', inverse='#022329'),
    'dark': dict(background='#022329', surface='#0E3D42', surface_alt='#115E5F', text='#F3F5F2', text_2='#9DB5B3',
                 text_3='#80918F', border='#1E4A4F', primary='#14B8A6', primary_text='#7FE3D6', accent='#7FE3D6', inverse='#F3F5F2'),
}

# Gradient system (angles CSS convention: 0deg = to top, 90deg = to right)
GRADIENTS = {
    'primary':  dict(name='Primary Gradient', angle=135, stops=[('#14B8A6', 0), ('#7FE3D6', 100)],
                     use='Accent surfaces, key data highlights, CTA backgrounds on dark. Never behind body text.'),
    'deep':     dict(name='Deep Gradient', angle=160, stops=[('#0E3D42', 0), ('#022329', 100)],
                     use='Default dark background for covers, launch screens, presentation grounds.'),
    'light':    dict(name='Light Gradient', angle=180, stops=[('#FFFFFF', 0), ('#F3F5F2', 100)],
                     use='Light page grounds and documents; barely perceptible depth.'),
    'ambient':  dict(name='Ambient Field', angle=None, kind='radial',
                     stops=[('#14B8A6', 0, 0.28), ('#0E3D42', 45, 0.0)], base='#022329',
                     use='Soft light field behind the icon or hero UI on dark grounds.'),
    'premium':  dict(name='Premium Display Gradient', angle=145,
                     stops=[('#7FE3D6', 0), ('#14B8A6', 38), ('#0E3D42', 78), ('#022329', 100)],
                     use='Premium display logo, launch graphics and event screens only.'),
}

# ---------------------------------------------------------------------------
# LOGO COLOUR SPECIFICATIONS — icon blades B1..B5 (clockwise from light blade)
# ---------------------------------------------------------------------------
ICON_COLOURWAYS = {
    'primary':   dict(blades=['#7FE3D6', '#14B8A6', '#0E3D42', '#14B8A6', '#022329'], on='light',
                      desc='Primary full-colour icon for light grounds (#F3F5F2, white, light photography).'),
    'reverse':   dict(blades=['#7FE3D6', '#14B8A6', '#115E5F', '#14B8A6', '#0F7C74'], on='dark',
                      desc='Full-colour icon for dark grounds (#022329, #0E3D42, dark photography).'),
}
ICON_MONO = {
    'teal':  '#14B8A6', 'dark': '#022329', 'deep': '#0E3D42', 'white': '#FFFFFF',
    'black': '#000000', 'offwhite': '#F3F5F2', 'mint': '#7FE3D6',
}
# gap (master units, icon diameter = 1000) used for one-colour versions
MONO_GAP = 'gap20'        # standard (>= 48 px / 12 mm)
MONO_GAP_SMALL = 'gap32'  # 24-47 px / 6-12 mm
MONO_GAP_MICRO = 'gap56'  # < 24 px (favicon 16 px)

WORDMARK_COLOURS = {'dark': '#022329', 'white': '#FFFFFF', 'black': '#000000',
                    'offwhite': '#F3F5F2', 'teal': '#14B8A6', 'deep': '#0E3D42'}

# Lockup proportions (in units of icon diameter D)
LOCKUP = dict(
    horizontal=dict(cap=0.46, gap=0.30),                        # wordmark cap height, icon-to-wordmark gap
    full=dict(cap=0.44, gap=0.30, desc_cap=0.098, desc_gap=0.16, desc_track=0.06),
    stacked=dict(cap=0.40, gap=0.26),
)

# ---------------------------------------------------------------------------
# TYPOGRAPHY
# ---------------------------------------------------------------------------
FONT_EN = 'Instrument Sans'
FONT_AR = 'Myriad Arabic'           # "مايرى" — Adobe Myriad Arabic (PostScript: MyriadArabic-*)
FONT_AR_POSTSCRIPT = ['MyriadArabic-Regular', 'MyriadArabic-Semibold', 'MyriadArabic-Bold']

def font_dir():
    """Local font directory (fonts are referenced, not redistributed)."""
    return os.environ.get('WFS_FONT_DIR', os.path.expanduser('~/.wfs-fonts'))

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def hex_rgb(h):
    h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def rgb_cmyk(h):
    """Uncalibrated device-independent approximation (no ICC profile). Proof physically."""
    r, g, b = [x / 255 for x in hex_rgb(h)]
    k = 1 - max(r, g, b)
    if k >= 1: return (0, 0, 0, 100)
    c, m, y = [(1 - x - k) / (1 - k) for x in (r, g, b)]
    return tuple(int(round(v * 100)) for v in (c, m, y, k))

def rel_lum(h):
    def ch(v):
        v /= 255; return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = hex_rgb(h); return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)

def contrast(a, b):
    la, lb = sorted([rel_lum(a), rel_lum(b)], reverse=True)
    return (la + 0.05) / (lb + 0.05)
