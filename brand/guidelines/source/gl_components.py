"""Reusable HTML/SVG building blocks for the WFS Brand Guidelines (mockups, charts, icons).
Everything is built from brand tokens; no stock imagery."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'source'))
import brand_config as B

A = '../..'   # brand root relative to guidelines/source

def logo(name, group='logo', style=''):
    return f'<img src="{A}/{group}/svg/{name}.svg" style="{style}" alt="">'

def mock(inner, w, h, width_mm, radius=0, shadow=True, cls=''):
    """Scale a fixed-size design (w x h px) into width_mm."""
    s = width_mm * 3.7795275591 / w
    hmm = h * s / 3.7795275591
    sh = 'box-shadow:0 1.2mm 4mm rgba(2,35,41,.18),0 .2mm .6mm rgba(2,35,41,.12);' if shadow else ''
    return (f'<div class="mock {cls}" style="width:{width_mm:.2f}mm;height:{hmm:.2f}mm;border-radius:{radius}mm;{sh}">'
            f'<div style="width:{w}px;height:{h}px;transform:scale({s:.5f});transform-origin:0 0">{inner}</div></div>')

# ------------------------------------------------------------------ UI icons (24 grid, 1.5 stroke)
ICONS = {
    'overview':   '<rect x="3.5" y="3.5" width="7" height="7" rx="1.5"/><rect x="13.5" y="3.5" width="7" height="4.5" rx="1.5"/><rect x="13.5" y="11" width="7" height="9.5" rx="1.5"/><rect x="3.5" y="13.5" width="7" height="7" rx="1.5"/>',
    'ledger':     '<path d="M5 4.5h11.5a2 2 0 0 1 2 2v13H7a2 2 0 0 1-2-2z"/><path d="M5 17.5a2 2 0 0 1 2-2h11.5"/><path d="M9 8.5h6M9 11.5h4"/>',
    'treasury':   '<rect x="3.5" y="4.5" width="17" height="15" rx="2"/><circle cx="12" cy="12" r="3.6"/><path d="M12 8.4V7M12 17v-1.4M15.6 12H17M7 12h1.4M6.5 19.5v1M17.5 19.5v1"/>',
    'receivable': '<path d="M4 13.5v4a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-4"/><path d="M12 4v10M8 10l4 4 4-4"/>',
    'payable':    '<path d="M4 13.5v4a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-4"/><path d="M12 14V4M8 8l4-4 4 4"/>',
    'payroll':    '<circle cx="9" cy="8.5" r="3"/><path d="M3.5 19a5.5 5.5 0 0 1 11 0"/><circle cx="17" cy="9.5" r="2.3"/><path d="M15.5 14.2a4.5 4.5 0 0 1 5 4.8"/>',
    'approval':   '<circle cx="12" cy="12" r="8.5"/><path d="M8 12.3l2.7 2.7L16.2 9.5"/>',
    'document':   '<path d="M6.5 3.5h7l4 4v11a2 2 0 0 1-2 2h-9a2 2 0 0 1-2-2v-13a2 2 0 0 1 2-2z"/><path d="M13.5 3.5v4h4M8.5 12.5h7M8.5 15.5h5"/>',
    'report':     '<path d="M4 20h16"/><rect x="5.5" y="11" width="3" height="6.5" rx="1"/><rect x="10.5" y="6.5" width="3" height="11" rx="1"/><rect x="15.5" y="13.5" width="3" height="4" rx="1"/>',
    'analytics':  '<path d="M3.5 17l5-5.5 3.5 3 7.5-8"/><path d="M15 6.5h4.5V11"/>',
    'cheque':     '<rect x="3.5" y="6" width="17" height="12" rx="2"/><path d="M7 14.5h5"/><circle cx="16" cy="11" r="2.2"/><path d="M16 10v1.1l.8.6"/>',
    'deal':       '<circle cx="9" cy="12" r="5"/><circle cx="15" cy="12" r="5"/>',
    'commission': '<circle cx="12" cy="12" r="8.5"/><path d="M9 15l6-6"/><circle cx="9.3" cy="9.3" r="1"/><circle cx="14.7" cy="14.7" r="1"/>',
    'cash':       '<path d="M12 3.5l8.5 4.3L12 12 3.5 7.8z"/><path d="M3.5 12.2L12 16.5l8.5-4.3"/><path d="M3.5 16.3L12 20.5l8.5-4.2"/>',
    'integration':'<circle cx="6" cy="12" r="2.3"/><circle cx="18" cy="6" r="2.3"/><circle cx="18" cy="18" r="2.3"/><path d="M8.2 11l7.6-4M8.2 13l7.6 4"/>',
    'entities':   '<rect x="9" y="3.5" width="6" height="5" rx="1.2"/><rect x="3.5" y="15.5" width="6" height="5" rx="1.2"/><rect x="14.5" y="15.5" width="6" height="5" rx="1.2"/><path d="M12 8.5v3.5M6.5 15.5V12h11v3.5"/>',
    'control':    '<rect x="5" y="10.5" width="14" height="10" rx="2"/><path d="M8.5 10.5V8a3.5 3.5 0 0 1 7 0v2.5"/><path d="M12 14.5v2.2"/>',
    'search':     '<circle cx="10.5" cy="10.5" r="6"/><path d="M15 15l5 5"/>',
    'bell':       '<path d="M6.5 16.5V11a5.5 5.5 0 0 1 11 0v5.5l1.5 1.5H5z"/><path d="M10 20.5h4"/>',
    'calendar':   '<rect x="4" y="5.5" width="16" height="14.5" rx="2"/><path d="M4 10h16M8.5 3.5v4M15.5 3.5v4"/>',
    'settings':   '<path d="M4 7h9M17 7h3M4 17h3M11 17h9"/><circle cx="15" cy="7" r="2"/><circle cx="9" cy="17" r="2"/>',
    'bank':       '<rect x="3.5" y="5.5" width="17" height="13" rx="2"/><path d="M3.5 9.5h17M7 14.5h3.5"/>',
    'fx':         '<path d="M4 8.5h13l-3-3M20 15.5H7l3 3"/>',
    'arrow_up':   '<path d="M7 14l5-5 5 5"/>',
    'arrow_down': '<path d="M7 10l5 5 5-5"/>',
    'chevron':    '<path d="M10 7l5 5-5 5"/>',
    'plus':       '<path d="M12 5v14M5 12h14"/>',
}
ICON_LABELS = {'overview': 'Overview', 'ledger': 'Ledger', 'treasury': 'Treasury', 'receivable': 'Receivables',
               'payable': 'Payables', 'payroll': 'Payroll', 'approval': 'Approvals', 'document': 'Documents',
               'report': 'Reports', 'analytics': 'Analytics', 'cheque': 'PDC / Cheques', 'deal': 'Deals',
               'commission': 'Commissions', 'cash': 'Cash', 'integration': 'Integrations', 'entities': 'Entities',
               'control': 'Controls', 'bank': 'Bank accounts', 'fx': 'FX / Transfers', 'calendar': 'Periods'}

def icon(name, size=18, color='currentColor', sw=1.5):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{sw}" '
            f'stroke-linecap="round" stroke-linejoin="round" style="display:block;flex:none">{ICONS[name]}</svg>')

# ------------------------------------------------------------------ small logo marks for mockups
def mark(size_px, theme='dark'):
    name = 'WFS_Icon_Inverse' if theme == 'dark' else 'WFS_Icon_Primary'
    return f'<img src="{A}/icon/svg/{name}.svg" style="width:{size_px}px;height:{size_px}px;display:block">'

def wordmark(h_px, theme='dark'):
    name = 'WFS_Wordmark_Inverse' if theme == 'dark' else 'WFS_Wordmark_Primary'
    return f'<img src="{A}/wordmark/svg/{name}.svg" style="height:{h_px}px;display:block">'

def lockup(h_px, theme='dark'):
    name = 'WFS_Logo_Horizontal_Inverse' if theme == 'dark' else 'WFS_Logo_Horizontal_Primary'
    return f'<img src="{A}/logo/svg/{name}.svg" style="height:{h_px}px;display:block">'

# ------------------------------------------------------------------ charts (static, brand data palette)
def area_chart(w, h, series, theme='light', labels=None, ymax=None, fmt=lambda v: f'{v:.1f}M'):
    t = TH[theme]; col = B.DATAVIZ[theme][0]
    pad_l, pad_b, pad_t, pad_r = 44, 24, 10, 8
    ymax = ymax or max(series) * 1.15
    n = len(series)
    X = lambda i: pad_l + (w - pad_l - pad_r) * i / (n - 1)
    Y = lambda v: pad_t + (h - pad_t - pad_b) * (1 - v / ymax)
    grid = ''.join(f'<line x1="{pad_l}" x2="{w-pad_r}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="{t["grid"]}" stroke-width="1"/>'
                   f'<text x="{pad_l-8}" y="{Y(v)+3.5:.1f}" text-anchor="end" class="tn" fill="{t["muted"]}" font-size="10">{fmt(v)}</text>'
                   for v in [ymax * k / 4 for k in range(0, 5)])
    pts = ' '.join(f'{X(i):.1f},{Y(v):.1f}' for i, v in enumerate(series))
    area = f'{X(0):.1f},{Y(0):.1f} ' + pts + f' {X(n-1):.1f},{Y(0):.1f}'
    xl = ''.join(f'<text x="{X(i):.1f}" y="{h-6}" text-anchor="middle" fill="{t["muted"]}" font-size="10">{l}</text>'
                 for i, l in enumerate(labels or []) if i % max(1, n // 6) == 0)
    gid = f'ag{theme}{w}{h}'
    last = f'<circle cx="{X(n-1):.1f}" cy="{Y(series[-1]):.1f}" r="4" fill="{col}" stroke="{t["surface"]}" stroke-width="2"/>'
    return (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}"><defs><linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{col}" stop-opacity="0.22"/><stop offset="1" stop-color="{col}" stop-opacity="0"/></linearGradient></defs>'
            f'{grid}<polygon points="{area}" fill="url(#{gid})"/><polyline points="{pts}" fill="none" stroke="{col}" stroke-width="2" stroke-linejoin="round"/>{last}{xl}</svg>')

def bar_pairs(w, h, a, b, labels, theme='light', names=('Receivables', 'Payables')):
    t = TH[theme]; ca, cb = B.DATAVIZ[theme][0], B.DATAVIZ[theme][1]
    pad_l, pad_b, pad_t = 34, 22, 26
    ymax = max(a + b) * 1.15; n = len(a)
    gw = (w - pad_l - 6) / n; bw = min(12, gw * 0.28)
    Y = lambda v: pad_t + (h - pad_t - pad_b) * (1 - v / ymax)
    out = [f'<line x1="{pad_l}" x2="{w-6}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="{t["grid"]}"/>'
           f'<text x="{pad_l-6}" y="{Y(v)+3.5:.1f}" text-anchor="end" class="tn" fill="{t["muted"]}" font-size="10">{v:.0f}</text>' for v in [ymax * k / 3 for k in range(4)]]
    for i in range(n):
        x = pad_l + gw * i + gw / 2
        for j, (v, c) in enumerate(((a[i], ca), (b[i], cb))):
            xx = x - bw - 1 + j * (bw + 2)
            y = Y(v); hh = Y(0) - y
            out.append(f'<path d="M{xx:.1f},{Y(0):.1f} V{y+3:.1f} a3,3 0 0 1 3,-3 h{bw-6:.1f} a3,3 0 0 1 3,3 V{Y(0):.1f} Z" fill="{c}"/>')
        out.append(f'<text x="{x:.1f}" y="{h-6}" text-anchor="middle" fill="{t["muted"]}" font-size="10">{labels[i]}</text>')
    leg = (f'<g font-size="10" fill="{t["text2"]}"><rect x="{pad_l}" y="4" width="9" height="9" rx="2" fill="{ca}"/><text x="{pad_l+14}" y="12">{names[0]}</text>'
           f'<rect x="{pad_l+96}" y="4" width="9" height="9" rx="2" fill="{cb}"/><text x="{pad_l+110}" y="12">{names[1]}</text></g>')
    return f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}">{"".join(out)}{leg}</svg>'

def spark(w, h, series, color):
    mn, mx = min(series), max(series); n = len(series)
    pts = ' '.join(f'{w*i/(n-1):.1f},{h-2-(h-4)*(v-mn)/(mx-mn or 1):.1f}' for i, v in enumerate(series))
    return f'<svg width="{w}" height="{h}"><polyline points="{pts}" fill="none" stroke="{color}" stroke-width="1.6" stroke-linejoin="round"/></svg>'

# ------------------------------------------------------------------ themes for mockups
TH = {
    'light': dict(bg='#F3F5F2', surface='#FFFFFF', side='#FFFFFF', text='#022329', text2='#4A5E61', muted='#80918F',
                  line='#E3E9E7', grid='#EDF1EF', accent='#0F7C74', chip='#DDF5F1', pos='#0F7C74', neg='#B4232F', sel='#DDF5F1'),
    'dark': dict(bg='#022329', surface='#0A3237', side='#031E23', text='#F3F5F2', text2='#9DB5B3', muted='#6F8987',
                 line='#1E4A4F', grid='#123F44', accent='#7FE3D6', chip='#0E3D42', pos='#4FD1BF', neg='#F08A8A', sel='#0E3D42'),
}

CASH = [38.2, 39.1, 38.6, 40.4, 41.2, 40.8, 42.5, 43.9, 43.1, 44.8, 46.2, 45.7, 47.9, 48.6]
MONTHS = ['Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep']

def dashboard(theme='light', w=1440, h=900):
    t = TH[theme]; dv = B.DATAVIZ[theme]
    nav = [('overview', 'Overview', True), ('entities', 'Entities', False), ('ledger', 'Ledger', False), ('treasury', 'Treasury', False),
           ('receivable', 'Receivables', False), ('payable', 'Payables', False), ('payroll', 'Payroll', False),
           ('approval', 'Approvals', False), ('cheque', 'PDC / Cheques', False), ('deal', 'Deals', False),
           ('report', 'Reports', False), ('integration', 'Integrations', False)]
    navh = ''.join(f'<div style="display:flex;align-items:center;gap:12px;height:36px;padding:0 12px;border-radius:8px;'
                   f'{"background:" + t["sel"] + ";color:" + t["text"] + ";font-weight:600" if a else "color:" + t["text2"]}">'
                   f'{icon(k, 18, t["accent"] if a else t["muted"])}<span style="font-size:13.5px">{l}</span></div>' for k, l, a in nav)
    kpis = [('Group cash position', '48,612,480.25', 'USD', '+2.4%', True, CASH),
            ('Receivables outstanding', '12,904,117.60', 'USD', '−3.1%', True, [14, 13.8, 13.9, 13.4, 13.1, 12.9]),
            ('Payables due · 30 days', '7,318,950.00', 'USD', '+6.8%', False, [6.1, 6.4, 6.3, 6.8, 7.0, 7.3]),
            ('Pending approvals', '27', 'items', '9 urgent', None, [31, 29, 33, 30, 28, 27])]
    kh = ''
    for lab, val, unit, delta, good, s in kpis:
        dcol = t['muted'] if good is None else (t['pos'] if good else t['neg'])
        arrow = '' if good is None else icon('arrow_up' if delta.startswith('+') else 'arrow_down', 14, dcol, 2)
        kh += (f'<div style="flex:1;background:{t["surface"]};border:1px solid {t["line"]};border-radius:12px;padding:18px 20px">'
               f'<div style="font-size:12.5px;color:{t["text2"]}">{lab}</div>'
               f'<div style="display:flex;align-items:baseline;gap:6px;margin-top:10px"><span class="tn" style="font-size:25px;font-weight:600;letter-spacing:-.01em;color:{t["text"]}">{val}</span>'
               f'<span style="font-size:12px;color:{t["muted"]}">{unit}</span></div>'
               f'<div style="display:flex;justify-content:space-between;align-items:center;margin-top:12px">'
               f'<span style="display:flex;align-items:center;gap:3px;font-size:12px;color:{dcol}" class="tn">{arrow}{delta}</span>{spark(90, 24, s, dv[0])}</div></div>')
    rows = [('WFS Holding Ltd', 'USD', '21,480,120.00', '+4.2%', True), ('Muscat Operations LLC', 'OMR', '3,912,440.50', '+1.1%', True),
            ('London Trading Ltd', 'GBP', '5,208,775.10', '−0.8%', False), ('Singapore Pte Ltd', 'SGD', '9,604,300.00', '+2.9%', True),
            ('Dubai Services FZ-LLC', 'AED', '14,221,090.75', '+0.4%', True)]
    th = f'font-size:11.5px;color:{t["muted"]};font-weight:500;text-transform:uppercase;letter-spacing:.06em;text-align:left;padding:0 0 10px'
    tr = ''.join(f'<tr style="border-top:1px solid {t["line"]}"><td style="padding:11px 0;font-size:13.5px;color:{t["text"]}">{n}</td>'
                 f'<td style="font-size:12.5px;color:{t["text2"]}">{c}</td><td class="tn" style="text-align:right;font-size:13.5px;color:{t["text"]}">{v}</td>'
                 f'<td class="tn" style="text-align:right;font-size:12.5px;color:{t["pos"] if g else t["neg"]}">{d}</td></tr>' for n, c, v, d, g in rows)
    appr = [('Supplier payment · Batch 0412', '2,418,000.00 USD', 'Treasury'), ('Payroll · September', '1,106,540.25 OMR', 'HR / Finance'),
            ('PDC deposit · 14 cheques', '386,200.00 AED', 'Receivables'), ('Commission run · Q3', '92,410.80 GBP', 'Sales ops')]
    ah = ''.join(f'<div style="display:flex;gap:12px;align-items:center;padding:11px 0;border-top:1px solid {t["line"]}">'
                 f'<div style="width:30px;height:30px;border-radius:8px;background:{t["chip"]};display:flex;align-items:center;justify-content:center">{icon("approval", 16, t["accent"])}</div>'
                 f'<div style="flex:1"><div style="font-size:13px;color:{t["text"]}">{a}</div><div style="font-size:11.5px;color:{t["muted"]}">{c}</div></div>'
                 f'<div class="tn" style="font-size:12.5px;color:{t["text"]}">{b}</div></div>' for a, b, c in appr)
    return f'''<div style="width:{w}px;height:{h}px;background:{t["bg"]};display:flex;font-family:var(--en);color:{t["text"]}">
  <div style="width:236px;background:{t["side"]};border-right:1px solid {t["line"]};padding:22px 16px;display:flex;flex-direction:column;gap:4px">
    <div style="padding:2px 10px 22px">{lockup(26, theme)}</div>
    <div style="margin:0 4px 14px;padding:10px 12px;border:1px solid {t["line"]};border-radius:10px;display:flex;align-items:center;gap:10px">
      {icon("entities", 16, t["accent"])}<div style="flex:1"><div style="font-size:11px;color:{t["muted"]}">Scope</div><div style="font-size:13px;font-weight:600">All entities · 5</div></div>{icon("chevron", 14, t["muted"])}</div>
    {navh}
  </div>
  <div style="flex:1;padding:24px 30px;display:flex;flex-direction:column;gap:18px">
    <div style="display:flex;align-items:center;justify-content:space-between">
      <div><div style="font-size:12.5px;color:{t["muted"]}">Executive overview · Consolidated in USD</div><div style="font-size:26px;font-weight:600;letter-spacing:-.015em;margin-top:2px">Good morning, Leila</div></div>
      <div style="display:flex;gap:10px;align-items:center">
        <div style="display:flex;align-items:center;gap:8px;height:36px;padding:0 14px;border:1px solid {t["line"]};border-radius:9px;background:{t["surface"]};width:250px;color:{t["muted"]};font-size:13px">{icon("search", 16, t["muted"])}Search records, entities, documents</div>
        <div style="display:flex;align-items:center;gap:8px;height:36px;padding:0 14px;border:1px solid {t["line"]};border-radius:9px;background:{t["surface"]};font-size:13px">{icon("calendar", 16, t["muted"])}Sep 2026</div>
        <div style="height:36px;padding:0 16px;border-radius:9px;background:#14B8A6;color:#022329;font-size:13px;font-weight:600;display:flex;align-items:center;gap:6px">{icon("plus", 15, "#022329", 2)}New entry</div>
      </div>
    </div>
    <div style="display:flex;gap:16px">{kh}</div>
    <div style="display:flex;gap:16px;flex:1">
      <div style="flex:1.55;background:{t["surface"]};border:1px solid {t["line"]};border-radius:12px;padding:18px 20px">
        <div style="display:flex;justify-content:space-between"><div><div style="font-size:15px;font-weight:600">Cash position</div><div style="font-size:12px;color:{t["muted"]}">All entities · 14 months · USD millions</div></div>
        <div style="display:flex;gap:4px;font-size:12px">{''.join(f'<span style="padding:5px 10px;border-radius:7px;{"background:" + t["sel"] + ";color:" + t["text"] + ";font-weight:600" if p == "1Y" else "color:" + t["muted"]}">{p}</span>' for p in ("1M", "3M", "1Y", "All"))}</div></div>
        <div style="margin-top:8px">{area_chart(620, 230, CASH, theme, MONTHS, ymax=56, fmt=lambda v: f"{v:.0f}")}</div>
      </div>
      <div style="flex:1;background:{t["surface"]};border:1px solid {t["line"]};border-radius:12px;padding:18px 20px">
        <div style="font-size:15px;font-weight:600">Awaiting your approval</div><div style="font-size:12px;color:{t["muted"]};margin-bottom:6px">Four-eyes control · policy v3</div>{ah}
      </div>
    </div>
    <div style="display:flex;gap:16px">
      <div style="flex:1.55;background:{t["surface"]};border:1px solid {t["line"]};border-radius:12px;padding:16px 20px">
        <table style="width:100%;border-collapse:collapse"><tr><th style="{th}">Entity</th><th style="{th}">Ccy</th><th style="{th};text-align:right">Balance</th><th style="{th};text-align:right">30d</th></tr>{tr}</table>
      </div>
      <div style="flex:1;background:{t["surface"]};border:1px solid {t["line"]};border-radius:12px;padding:16px 20px">
        <div style="font-size:15px;font-weight:600;margin-bottom:6px">Receivables vs payables</div>{bar_pairs(400, 170, [8.2, 9.1, 8.7, 9.6, 10.2, 9.8], [6.4, 6.9, 7.2, 6.8, 7.5, 7.3], ["Apr", "May", "Jun", "Jul", "Aug", "Sep"], theme)}
      </div>
    </div>
  </div>
</div>'''

def login(theme='dark', w=1440, h=900):
    return f'''<div style="width:{w}px;height:{h}px;display:flex;font-family:var(--en)">
  <div style="flex:1.1;position:relative;overflow:hidden;background:linear-gradient(160deg,#0E3D42,#022329)">
    <img src="{A}/graphic-system/fields/WFS_Overlay_Convergence_OnDark.svg" style="position:absolute;left:-380px;top:-60px;width:1600px">
    <div style="position:absolute;left:64px;top:56px">{lockup(34, "dark")}</div>
    <div style="position:absolute;left:64px;bottom:72px;color:#F3F5F2;max-width:520px">
      <div style="font-size:15px;color:#7FE3D6;letter-spacing:.14em;text-transform:uppercase;font-weight:600">Global financial operating system</div>
      <div style="font-size:52px;line-height:1.05;letter-spacing:-.025em;font-weight:600;margin-top:18px">One financial view across every entity and operation.</div></div>
  </div>
  <div style="flex:1;background:#F3F5F2;display:flex;align-items:center;justify-content:center">
    <div style="width:400px;color:#022329">
      <div style="font-size:30px;font-weight:600;letter-spacing:-.015em">Sign in to WFS</div>
      <div style="font-size:15px;color:#4A5E61;margin-top:8px">Use your organisation account.</div>
      <div style="margin-top:36px;font-size:13px;color:#4A5E61">Work email</div>
      <div style="margin-top:8px;height:48px;border:1px solid #D6DEDB;background:#fff;border-radius:10px;display:flex;align-items:center;padding:0 16px;font-size:15px">leila.haddad@northwind-group.com</div>
      <div style="margin-top:18px;font-size:13px;color:#4A5E61">Password</div>
      <div style="margin-top:8px;height:48px;border:1.5px solid #14B8A6;background:#fff;border-radius:10px;display:flex;align-items:center;padding:0 16px;font-size:20px;letter-spacing:.2em;box-shadow:0 0 0 4px #DDF5F1">••••••••••</div>
      <div style="margin-top:28px;height:50px;border-radius:10px;background:#022329;color:#F3F5F2;font-size:15px;font-weight:600;display:flex;align-items:center;justify-content:center">Continue</div>
      <div style="margin-top:16px;height:50px;border-radius:10px;border:1px solid #D6DEDB;background:#fff;font-size:15px;display:flex;align-items:center;justify-content:center;gap:10px">{icon("control", 18, "#0F7C74")}Single sign-on (SAML / OIDC)</div>
      <div style="margin-top:40px;font-size:12px;color:#80918F">WFS · A WUSOOL Tech Product · Encrypted session · Region: EU-West</div>
    </div>
  </div>
</div>'''

def phone(inner, w=390, h=844, frame='#0B0F10'):
    return (f'<div style="width:{w+28}px;height:{h+28}px;border-radius:62px;background:{frame};padding:14px;'
            f'box-shadow:inset 0 0 0 2px #2a3436">'
            f'<div style="width:{w}px;height:{h}px;border-radius:48px;overflow:hidden;position:relative">{inner}'
            f'<div style="position:absolute;top:11px;left:50%;transform:translateX(-50%);width:124px;height:36px;border-radius:20px;background:#000"></div></div></div>')

def splash(w=390, h=844):
    return (f'<div style="width:{w}px;height:{h}px;background:linear-gradient(170deg,#0E3D42,#022329);position:relative;overflow:hidden">'
            f'<img src="{A}/graphic-system/fields/WFS_Overlay_Unified_Field_OnDark.svg" style="position:absolute;left:-890px;top:120px;width:1700px;opacity:.9">'
            f'<div style="position:absolute;left:50%;top:44%;transform:translate(-50%,-50%)">{mark(128, "dark")}</div>'
            f'<div style="position:absolute;left:50%;top:60%;transform:translateX(-50%)">{wordmark(30, "dark")}</div>'
            f'<div style="position:absolute;bottom:46px;width:100%;text-align:center;font-family:var(--en);font-size:12px;letter-spacing:.14em;color:#7FE3D6">A WUSOOL TECH PRODUCT</div></div>')

def mobile_home(w=390, h=844, theme='dark'):
    t = TH[theme]
    items = [('Cash', '48.61M', '+2.4%', True), ('Receivables', '12.90M', '−3.1%', True), ('Payables · 30d', '7.32M', '+6.8%', False)]
    cards = ''.join(f'<div style="display:flex;justify-content:space-between;align-items:center;padding:14px 16px;border-radius:14px;background:{t["surface"]};border:1px solid {t["line"]};margin-top:10px">'
                    f'<div><div style="font-size:12px;color:{t["muted"]}">{a}</div><div class="tn" style="font-size:20px;font-weight:600;color:{t["text"]};margin-top:4px">{b} <span style="font-size:11px;color:{t["muted"]};font-weight:400">USD</span></div></div>'
                    f'<div class="tn" style="font-size:12px;color:{t["pos"] if g else t["neg"]}">{c}</div></div>' for a, b, c, g in items)
    return (f'<div style="width:{w}px;height:{h}px;background:{t["bg"]};font-family:var(--en);padding:62px 18px 0">'
            f'<div style="display:flex;justify-content:space-between;align-items:center">{lockup(20, theme)}{icon("bell", 20, t["text2"])}</div>'
            f'<div style="font-size:13px;color:{t["muted"]};margin-top:26px">All entities · USD</div>'
            f'<div style="font-size:28px;font-weight:600;letter-spacing:-.02em;color:{t["text"]};margin-top:2px">Today</div>'
            f'<div style="margin-top:12px;border-radius:16px;background:{t["surface"]};border:1px solid {t["line"]};padding:12px 8px 4px">{area_chart(338, 150, CASH, theme, None, ymax=56, fmt=lambda v: f"{v:.0f}")}</div>'
            f'{cards}'
            f'<div style="margin-top:14px;padding:14px 16px;border-radius:14px;background:#14B8A6;color:#022329;display:flex;justify-content:space-between;align-items:center">'
            f'<div><div style="font-size:12px;font-weight:600">9 urgent approvals</div><div style="font-size:11.5px;opacity:.8">Batch 0412 · 2,418,000.00 USD</div></div>{icon("chevron", 18, "#022329", 2)}</div></div>')

def website(w=1440, h=900):
    return f'''<div style="width:{w}px;height:{h}px;background:linear-gradient(170deg,#0E3D42 0%,#022329 60%);position:relative;overflow:hidden;font-family:var(--en);color:#F3F5F2">
  <img src="{A}/graphic-system/fields/WFS_Overlay_Unified_Field_OnDark.svg" style="position:absolute;left:260px;top:-300px;width:1500px;opacity:.8">
  <div style="position:absolute;left:72px;right:72px;top:34px;display:flex;align-items:center;justify-content:space-between">
    {lockup(30, "dark")}<div style="display:flex;gap:34px;font-size:15px;color:#9DB5B3"><span>Platform</span><span>Solutions</span><span>Security</span><span>Customers</span><span>Company</span></div>
    <div style="display:flex;gap:12px"><span style="padding:11px 18px;font-size:14px">Sign in</span><span style="padding:11px 20px;border-radius:10px;background:#14B8A6;color:#022329;font-size:14px;font-weight:600">Book a demo</span></div></div>
  <div style="position:absolute;left:72px;top:160px;width:880px">
    <div style="font-size:14px;color:#7FE3D6;letter-spacing:.16em;font-weight:600">GLOBAL FINANCIAL OPERATING SYSTEM</div>
    <div style="font-size:66px;line-height:1.02;letter-spacing:-.035em;font-weight:600;margin-top:22px">One financial system.<br>Every operation in view.</div>
    <div style="font-size:19px;line-height:1.5;color:#9DB5B3;margin-top:26px;width:600px">Accounting, treasury, payables, receivables, payroll and approvals — unified across every entity, currency and bank, with controlled execution built in.</div>
    <div style="display:flex;gap:14px;margin-top:34px"><span style="padding:16px 26px;border-radius:12px;background:#14B8A6;color:#022329;font-size:16px;font-weight:600">Book a demo</span><span style="padding:16px 26px;border-radius:12px;border:1px solid #1E4A4F;font-size:16px">See the platform</span></div></div>
  <div style="position:absolute;left:690px;top:560px;border-radius:14px;overflow:hidden;box-shadow:0 30px 80px rgba(0,0,0,.45);border:1px solid #1E4A4F;transform:scale(.58);transform-origin:0 0">{dashboard("dark")}</div>
</div>'''

def slide(w=1920, h=1080):
    return f'''<div style="width:{w}px;height:{h}px;background:linear-gradient(160deg,#0E3D42,#022329);position:relative;overflow:hidden;font-family:var(--en);color:#F3F5F2">
  <img src="{A}/graphic-system/fields/WFS_Overlay_Convergence_OnDark.svg" style="position:absolute;left:640px;top:-120px;width:1900px">
  <div style="position:absolute;left:120px;top:100px">{lockup(46, "dark")}</div>
  <div style="position:absolute;left:120px;bottom:150px;width:1000px">
    <div style="font-size:24px;color:#7FE3D6;letter-spacing:.16em;font-weight:600">INVESTOR BRIEFING · Q3 2026</div>
    <div style="font-size:108px;line-height:1.0;letter-spacing:-.035em;font-weight:600;margin-top:30px">One financial truth, at global scale.</div></div>
  <div style="position:absolute;left:120px;right:120px;bottom:64px;display:flex;justify-content:space-between;font-size:20px;color:#9DB5B3"><span>A WUSOOL Tech Product</span><span>Confidential · 01</span></div>
</div>'''

def social(w=1080, h=1080):
    return f'''<div style="width:{w}px;height:{h}px;background:#022329;position:relative;overflow:hidden;font-family:var(--en);color:#F3F5F2">
  <img src="{A}/graphic-system/fields/WFS_Overlay_Convergence_OnDark.svg" style="position:absolute;left:-420px;top:-40px;width:1920px">
  <div style="position:absolute;left:50%;top:40%;transform:translate(-50%,-50%)"><img src="{A}/icon/svg/WFS_Icon_Premium.svg" style="width:300px"></div>
  <div style="position:absolute;left:84px;right:84px;bottom:150px;text-align:center"><div style="font-size:72px;line-height:1.04;letter-spacing:-.03em;font-weight:600">Global by design.</div>
  <div style="font-size:26px;color:#9DB5B3;margin-top:18px">Multi-entity. Multi-currency. One view.</div></div>
  <div style="position:absolute;bottom:60px;left:0;right:0;display:flex;justify-content:center">{lockup(34, "dark")}</div>
</div>'''

def announcement(w=1200, h=1500):
    return f'''<div style="width:{w}px;height:{h}px;background:#F3F5F2;position:relative;overflow:hidden;font-family:var(--en);color:#022329">
  <img src="{A}/graphic-system/fields/WFS_Overlay_Aperture_Crop_OnLight.svg" style="position:absolute;left:-240px;top:-200px;width:1900px">
  <div style="position:absolute;left:90px;top:90px">{lockup(40, "light")}</div>
  <div style="position:absolute;left:90px;top:300px;width:900px"><div style="display:inline-block;padding:10px 18px;border-radius:30px;background:#022329;color:#7FE3D6;font-size:20px;font-weight:600;letter-spacing:.08em">NOW AVAILABLE</div>
  <div style="font-size:96px;line-height:1.0;letter-spacing:-.035em;font-weight:600;margin-top:36px">Multi-entity treasury.</div>
  <div style="font-size:30px;line-height:1.4;color:#4A5E61;margin-top:26px;width:820px">Every bank, account and currency in one controlled cash view — with approvals built in.</div></div>
  <div style="position:absolute;left:90px;right:90px;bottom:90px;border-radius:18px;overflow:hidden;height:560px;border:1px solid #D6DEDB;box-shadow:0 24px 60px rgba(2,35,41,.18)"><div style="transform:scale(.705);transform-origin:0 0">{dashboard("light")}</div></div>
</div>'''

def report_cover(w=794, h=1123):
    return f'''<div style="width:{w}px;height:{h}px;background:linear-gradient(165deg,#0E3D42,#022329);position:relative;overflow:hidden;font-family:var(--en);color:#F3F5F2">
  <img src="{A}/graphic-system/fields/WFS_Overlay_Unified_Field_OnDark.svg" style="position:absolute;left:-560px;top:-120px;width:1700px">
  <div style="position:absolute;left:64px;top:64px">{lockup(28, "dark")}</div>
  <div style="position:absolute;left:64px;bottom:200px;width:600px"><div style="font-size:15px;letter-spacing:.16em;color:#7FE3D6;font-weight:600">CONSOLIDATED FINANCIAL REPORT</div>
  <div style="font-size:58px;line-height:1.02;letter-spacing:-.03em;font-weight:600;margin-top:18px">Q3 2026<br>Group performance</div>
  <div style="font-size:16px;color:#9DB5B3;margin-top:22px">Northwind Group · 5 entities · Reporting currency USD</div></div>
  <div style="position:absolute;left:64px;right:64px;bottom:64px;display:flex;justify-content:space-between;font-size:12px;color:#9DB5B3;border-top:1px solid #1E4A4F;padding-top:16px"><span>Generated by WFS · 30 Sep 2026 18:04 UTC</span><span>Confidential</span></div>
</div>'''

def report_page(w=794, h=1123):
    rows = [('Revenue', '84,210,440.12', '79,106,002.40', '+6.5%'), ('Cost of sales', '(41,882,905.30)', '(40,011,250.88)', '+4.7%'),
            ('Gross profit', '42,327,534.82', '39,094,751.52', '+8.3%'), ('Operating expenses', '(21,440,118.07)', '(20,970,334.19)', '+2.2%'),
            ('EBITDA', '20,887,416.75', '18,124,417.33', '+15.2%'), ('Depreciation & amortisation', '(3,105,882.00)', '(2,998,140.00)', '+3.6%'),
            ('Net finance cost', '(1,204,550.41)', '(1,410,275.66)', '−14.6%'), ('Profit before tax', '16,577,000.34', '13,716,001.67', '+20.9%')]
    body = ''.join(f'<tr style="border-top:1px solid #E3E9E7{";font-weight:600" if n in ("Gross profit", "EBITDA", "Profit before tax") else ""}"><td style="padding:9px 0">{n}</td><td class="tn" style="text-align:right">{a}</td><td class="tn" style="text-align:right;color:#4A5E61">{b}</td><td class="tn" style="text-align:right;color:{"#B4232F" if c.startswith("−") else "#0F7C74"}">{c}</td></tr>' for n, a, b, c in rows)
    return f'''<div style="width:{w}px;height:{h}px;background:#fff;position:relative;font-family:var(--en);color:#022329">
  <div style="height:64px;display:flex;align-items:center;justify-content:space-between;padding:0 56px;border-bottom:1px solid #E3E9E7">{lockup(18, "light")}<span style="font-size:11px;color:#80918F;letter-spacing:.12em">CONSOLIDATED FINANCIAL REPORT · Q3 2026</span></div>
  <div style="padding:44px 56px"><div style="font-size:11px;letter-spacing:.14em;color:#0F7C74;font-weight:600">02 · INCOME STATEMENT</div>
  <div style="font-size:30px;font-weight:600;letter-spacing:-.02em;margin-top:8px">Profit and loss, consolidated</div>
  <div style="font-size:13px;color:#4A5E61;margin-top:6px">USD · nine months ended 30 September · unaudited</div>
  <table style="width:100%;border-collapse:collapse;margin-top:26px;font-size:13px"><tr style="font-size:10.5px;color:#80918F;text-transform:uppercase;letter-spacing:.08em"><td style="padding-bottom:8px">Line item</td><td style="text-align:right">2026</td><td style="text-align:right">2025</td><td style="text-align:right">Δ</td></tr>{body}</table>
  <div style="margin-top:30px;padding:16px 18px;background:#F3F5F2;border-radius:8px;font-size:12px;color:#4A5E61;line-height:1.55">Negative values are shown in parentheses; percentage change is computed on absolute values. All figures reconcile to the WFS general ledger snapshot #GL-2026-09-30-1804.</div></div>
  <div style="position:absolute;left:56px;right:56px;bottom:36px;display:flex;justify-content:space-between;font-size:10.5px;color:#80918F;border-top:1px solid #E3E9E7;padding-top:12px"><span>WFS · Wusool Financial System</span><span>Confidential · Page 4 of 38</span></div>
</div>'''

def event_screen(w=1920, h=1080):
    return f'''<div style="width:{w}px;height:{h}px;background:radial-gradient(120% 90% at 50% 20%,#0A2A2F,#010D10 70%);position:relative;overflow:hidden;font-family:var(--en)">
  <div style="position:absolute;left:210px;top:120px;width:1500px;height:620px;background:#022329;border-radius:6px;overflow:hidden;box-shadow:0 0 120px rgba(20,184,166,.25)">
    <img src="{A}/graphic-system/fields/WFS_Overlay_Convergence_OnDark.svg" style="position:absolute;left:0;top:-230px;width:1500px">
    <div style="position:absolute;left:50%;top:50%;transform:translate(-50%,-50%)"><img src="{A}/logo/svg/WFS_Logo_Horizontal_Premium.svg" style="height:150px"></div></div>
  <div style="position:absolute;left:0;right:0;top:760px;height:320px;background:linear-gradient(#051a1e,#010a0c)"></div>
  <div style="position:absolute;left:680px;top:760px;width:560px;height:18px;background:#0B2A2E;border-radius:4px"></div>
  {''.join(f'<div style="position:absolute;left:{x}px;top:{880 + (i % 3) * 38}px;width:{90 + (i % 2) * 20}px;height:{140 + (i % 3) * 20}px;border-radius:50px 50px 8px 8px;background:#020c0e"></div>' for i, x in enumerate(range(40, 1900, 118)))}
</div>'''

def business_card(front=True, w=1050, h=600):
    if front:
        return (f'<div style="width:{w}px;height:{h}px;background:linear-gradient(160deg,#0E3D42,#022329);position:relative;overflow:hidden">'
                f'<img src="{A}/graphic-system/fields/WFS_Overlay_Unified_Field_OnDark.svg" style="position:absolute;left:-300px;top:-420px;width:1600px">'
                f'<div style="position:absolute;left:50%;top:50%;transform:translate(-50%,-50%)">{lockup(70, "dark")}</div></div>')
    return (f'<div style="width:{w}px;height:{h}px;background:#F3F5F2;position:relative;font-family:var(--en);color:#022329">'
            f'<div style="position:absolute;left:80px;top:80px">{mark(80, "light")}</div>'
            f'<div style="position:absolute;left:80px;bottom:90px"><div style="font-size:40px;font-weight:600;letter-spacing:-.01em">Leila Haddad</div>'
            f'<div style="font-size:24px;color:#0F7C74;margin-top:6px">Chief Financial Officer</div>'
            f'<div style="font-size:21px;color:#4A5E61;margin-top:28px;line-height:1.55">leila.haddad@wfs.example<br>+968 0000 0000 · wfs.example</div></div>'
            f'<div style="position:absolute;right:80px;bottom:90px;font-size:17px;color:#80918F;letter-spacing:.12em">A WUSOOL TECH PRODUCT</div></div>')


def slide_content(w=1920, h=1080):
    t = TH['light']
    kp = ''.join(f'<div style="flex:1;border-top:3px solid {c};padding-top:22px"><div style="font-size:26px;color:#4A5E61">{a}</div><div class="tn" style="font-size:78px;font-weight:600;letter-spacing:-.02em;margin-top:8px">{b}</div><div class="tn" style="font-size:24px;color:{d}">{e}</div></div>'
                 for a, b, c, d, e in (('Group cash', '48.6M', '#14B8A6', '#0F7C74', '+2.4 % · USD'), ('Entities live', '5', '#022329', '#80918F', 'OM · AE · GB · SG'), ('Close time', '3.5 d', '#022329', '#0F7C74', '−41 % vs 2025')))
    return f'''<div style="width:{w}px;height:{h}px;background:#F3F5F2;position:relative;overflow:hidden;font-family:var(--en);color:#022329">
  <div style="position:absolute;left:120px;top:90px;right:120px;display:flex;justify-content:space-between;align-items:center">{lockup(34, "light")}<span style="font-size:20px;color:#80918F;letter-spacing:.14em">Q3 2026 · 04</span></div>
  <div style="position:absolute;left:120px;top:210px;width:1100px"><div style="font-size:22px;letter-spacing:.16em;color:#0F7C74;font-weight:600">GROUP PERFORMANCE</div>
  <div style="font-size:64px;line-height:1.05;letter-spacing:-.03em;font-weight:600;margin-top:18px">Five entities. One close. One view of cash.</div></div>
  <div style="position:absolute;left:120px;top:520px;width:880px;display:flex;gap:50px">{kp}</div>
  <div style="position:absolute;left:1080px;top:470px;width:720px;height:420px;background:#fff;border-radius:18px;border:1px solid #E3E9E7;padding:28px">
    <div style="font-size:24px;font-weight:600">Cash position · USD millions</div>{area_chart(664, 330, CASH, "light", MONTHS, ymax=56, fmt=lambda v: f"{v:.0f}")}</div>
  <div style="position:absolute;left:120px;right:120px;bottom:60px;display:flex;justify-content:space-between;font-size:18px;color:#80918F"><span>Source: WFS consolidated ledger, 30 Sep 2026</span><span>A WUSOOL Tech Product</span></div>
</div>'''

def banner(w=1584, h=396):
    return (f'<div style="width:{w}px;height:{h}px;background:linear-gradient(160deg,#0E3D42,#022329);position:relative;overflow:hidden;font-family:var(--en);color:#F3F5F2">'
            f'<img src="{A}/graphic-system/fields/WFS_Overlay_Convergence_OnDark.svg" style="position:absolute;left:760px;top:-420px;width:1300px">'
            f'<div style="position:absolute;left:330px;top:120px"><div style="font-size:54px;font-weight:600;letter-spacing:-.03em">One financial view.</div>'
            f'<div style="font-size:24px;color:#9DB5B3;margin-top:10px">The global financial operating system for multi-entity organisations.</div></div>'
            f'<div style="position:absolute;right:80px;bottom:60px">{lockup(40, "dark")}</div></div>')

def email_header(w=1200, h=400):
    return (f'<div style="width:{w}px;height:{h}px;background:#F3F5F2;position:relative;overflow:hidden;font-family:var(--en);color:#022329">'
            f'<img src="{A}/graphic-system/fields/WFS_Overlay_Aperture_Crop_OnLight.svg" style="position:absolute;left:260px;top:-160px;width:1300px">'
            f'<div style="position:absolute;left:64px;top:56px">{lockup(30, "light")}</div>'
            f'<div style="position:absolute;left:64px;bottom:64px"><div style="font-size:18px;letter-spacing:.16em;color:#0F7C74;font-weight:600">PRODUCT UPDATE · SEPTEMBER 2026</div>'
            f'<div style="font-size:48px;font-weight:600;letter-spacing:-.03em;margin-top:10px">Approvals, now across entities.</div></div></div>')
