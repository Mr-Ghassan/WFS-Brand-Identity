"""WFS UI kit, product screens, technical applications and social media system
(HTML/SVG, built from brand tokens) for the guidelines and templates."""
import os, sys, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'source'))
import brand_config as B
import gl_components as C
from gl_components import A, icon, TH, lockup, mark, wordmark, area_chart, bar_pairs, spark, CASH, MONTHS

# ------------------------------------------------------------------ extra UI icons (24 grid, 1.5 stroke)
C.ICONS.update({
    'wallet_off': '<path d="M4 7.5h14a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2z"/><path d="M4 7.5l11-3v3M16 13h1.5"/>',
    'invoice':    '<path d="M6.5 3.5h11v17l-2.2-1.4-2.2 1.4-2.1-1.4-2.2 1.4-2.3-1.4z"/><path d="M9 8.5h6M9 11.5h6M9 14.5h3.5"/>',
    'reconcile':  '<path d="M5 9a7 7 0 0 1 12.2-3.5L19 7.5M19 15a7 7 0 0 1-12.2 3.5L5 16.5"/><path d="M19 3.5v4h-4M5 20.5v-4h4"/>',
    'budget':     '<circle cx="12" cy="12" r="8.5"/><path d="M12 12V3.5M12 12l6 6"/>',
    'forecast':   '<path d="M3.5 17l5-5 3.5 3 3-3"/><path d="M15 12l5.5-5.5" stroke-dasharray="1.5 2.5"/>',
    'audit':      '<path d="M12 3.5l7 3v5.2c0 4.3-3 7.6-7 8.8-4-1.2-7-4.5-7-8.8V6.5z"/><path d="M9 12l2.2 2.2L15.5 10"/>',
    'user':       '<circle cx="12" cy="8.5" r="3.5"/><path d="M5 20a7 7 0 0 1 14 0"/>',
    'team':       '<circle cx="8.5" cy="9" r="3"/><circle cx="16.5" cy="10" r="2.5"/><path d="M3.5 19a5 5 0 0 1 10 0M14 15.3a4.3 4.3 0 0 1 6.5 3.7"/>',
    'globe':      '<circle cx="12" cy="12" r="8.5"/><path d="M3.5 12h17M12 3.5c2.5 2.6 3.5 5.4 3.5 8.5s-1 5.9-3.5 8.5c-2.5-2.6-3.5-5.4-3.5-8.5s1-5.9 3.5-8.5z"/>',
    'currency':   '<circle cx="9" cy="10" r="5"/><path d="M13.5 8.2A5 5 0 1 1 10.8 16"/>',
    'filter':     '<path d="M4 5.5h16l-6 7.5v5.5l-4 1.5v-7z"/>',
    'download':   '<path d="M12 4v11M7.5 10.5L12 15l4.5-4.5M4.5 19.5h15"/>',
    'upload':     '<path d="M12 15V4M7.5 8.5L12 4l4.5 4.5M4.5 19.5h15"/>',
    'link':       '<path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/>',
    'api':        '<path d="M8 8l-4 4 4 4M16 8l4 4-4 4M13.5 5.5l-3 13"/>',
    'shield':     '<path d="M12 3.5l7 3v5.2c0 4.3-3 7.6-7 8.8-4-1.2-7-4.5-7-8.8V6.5z"/>',
    'key':        '<circle cx="8" cy="15" r="4"/><path d="M11 12l8.5-8.5M16.5 6.5l2 2M14.5 8.5l1.5 1.5"/>',
    'clock':      '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>',
    'check':      '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
    'close':      '<path d="M6 6l12 12M18 6L6 18"/>',
    'more':       '<circle cx="5.5" cy="12" r="1.2"/><circle cx="12" cy="12" r="1.2"/><circle cx="18.5" cy="12" r="1.2"/>',
    'info':       '<circle cx="12" cy="12" r="8.5"/><path d="M12 11v5.5M12 7.8v.2"/>',
    'warning':    '<path d="M12 4l9 15.5H3z"/><path d="M12 10v4.5M12 17.2v.2"/>',
    'error':      '<circle cx="12" cy="12" r="8.5"/><path d="M9 9l6 6M15 9l-6 6"/>',
    'mail':       '<rect x="3.5" y="5.5" width="17" height="13" rx="2"/><path d="M4 7l8 6 8-6"/>',
    'home':       '<path d="M4 11l8-6.5 8 6.5v8.5a1 1 0 0 1-1 1h-4.5V15h-5v5.5H5a1 1 0 0 1-1-1z"/>',
    'edit':       '<path d="M4.5 19.5l1-4.2L15.8 5a2 2 0 0 1 2.8 0l.4.4a2 2 0 0 1 0 2.8L8.7 18.5z"/><path d="M13.8 7l3.2 3.2"/>',
    'trash':      '<path d="M4.5 7h15M9.5 7V4.5h5V7M6.5 7l1 12.5h9l1-12.5"/>',
    'eye':        '<path d="M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12z"/><circle cx="12" cy="12" r="3"/>',
})
ICON_SET = ['overview', 'entities', 'ledger', 'treasury', 'bank', 'cash', 'receivable', 'payable', 'invoice', 'payroll', 'approval', 'cheque',
            'deal', 'commission', 'reconcile', 'budget', 'forecast', 'report', 'analytics', 'document', 'audit', 'control', 'integration', 'api',
            'fx', 'currency', 'globe', 'user', 'team', 'calendar', 'clock', 'search', 'filter', 'bell', 'mail', 'settings', 'download', 'upload',
            'link', 'edit', 'trash', 'eye', 'key', 'shield', 'info', 'warning', 'error', 'check', 'close', 'more', 'home', 'plus']

# ------------------------------------------------------------------ primitives (px, for scaled mocks)
def btn(label, kind='primary', size='md', theme='light', ic=None, state=''):
    t = TH[theme]
    h, px, fs = {'sm': (32, 12, 13), 'md': (40, 16, 14), 'lg': (48, 20, 15)}[size]
    styles = {
        'primary':   (B.HEX['wfs-teal'], '#022329', 'transparent'),
        'secondary': (t['surface'], t['text'], t['line']),
        'tertiary':  ('transparent', t['accent'], 'transparent'),
        'dark':      ('#022329' if theme == 'light' else '#F3F5F2', '#F3F5F2' if theme == 'light' else '#022329', 'transparent'),
        'danger':    ('#B4232F', '#FFFFFF', 'transparent'),
    }
    bg, fg, bd = styles[kind]
    extra = ''
    if state == 'hover': bg = {'primary': '#11998B', 'secondary': t['sel'], 'tertiary': t['sel'], 'dark': '#0E3D42' if theme == 'light' else '#DDF5F1', 'danger': '#962029'}[kind]
    if state == 'focus': extra = f';box-shadow:0 0 0 3px {t["bg"]},0 0 0 5px #14B8A6'
    if state == 'disabled': bg, fg, bd = (t['line'], t['muted'], 'transparent')
    ic_html = icon(ic, fs + 2, fg, 1.8) if ic else ''
    return (f'<span style="display:inline-flex;align-items:center;justify-content:center;gap:8px;height:{h}px;padding:0 {px}px;border-radius:10px;'
            f'background:{bg};color:{fg};border:1px solid {bd};font:600 {fs}px var(--en);white-space:nowrap{extra}">{ic_html}{label}</span>')

def field(label, value, state='', theme='light', w=260, ic=None, help_=''):
    t = TH[theme]
    bd = {'': t['line'], 'focus': '#14B8A6', 'error': '#B4232F', 'disabled': t['line']}[state]
    ring = ';box-shadow:0 0 0 4px ' + ('#DDF5F1' if theme == 'light' else '#0E3D42') if state == 'focus' else ''
    bg = t['bg'] if state == 'disabled' else t['surface']
    col = t['muted'] if state == 'disabled' else t['text']
    hc = '#B4232F' if state == 'error' else t['muted']
    return (f'<div style="width:{w}px;font-family:var(--en)"><div style="font-size:12.5px;color:{t["text2"]};margin-bottom:6px">{label}</div>'
            f'<div style="height:42px;border:1.5px solid {bd};border-radius:10px;background:{bg};display:flex;align-items:center;gap:8px;padding:0 12px;font-size:14px;color:{col}{ring}" class="tn">'
            f'{icon(ic, 16, t["muted"]) if ic else ""}{value}</div>'
            f'{f"<div style=font-size:11.5px;color:{hc};margin-top:5px>{help_}</div>" if help_ else ""}</div>')

def chip(label, kind='neutral', theme='light'):
    m = {'success': ('#DDF5F1', '#0F7C74') if theme == 'light' else ('#0E3D42', '#7FE3D6'), 'warning': ('#FBEAD8', '#9A6212') if theme == 'light' else ('#3A2A14', '#E7B25B'),
         'danger': ('#F7E1E3', '#B4232F') if theme == 'light' else ('#3A1A1E', '#F08A8A'), 'info': ('#E1ECF5', '#2F6F9F') if theme == 'light' else ('#14283A', '#8DB8E0'),
         'neutral': ('#EDF1EF', '#4A5E61') if theme == 'light' else ('#0E3D42', '#9DB5B3')}
    bg, fg = m[kind]
    return f'<span style="display:inline-flex;align-items:center;gap:6px;height:24px;padding:0 10px;border-radius:12px;background:{bg};color:{fg};font:600 12px var(--en)"><span style="width:6px;height:6px;border-radius:50%;background:{fg}"></span>{label}</span>'

def toggle(on=True, theme='light'):
    t = TH[theme]
    return (f'<span style="display:inline-block;width:40px;height:24px;border-radius:12px;background:{"#14B8A6" if on else t["line"]};position:relative">'
            f'<span style="position:absolute;top:3px;left:{19 if on else 3}px;width:18px;height:18px;border-radius:50%;background:#fff;box-shadow:0 1px 2px rgba(0,0,0,.25)"></span></span>')

def check(on=True, theme='light', radio=False):
    t = TH[theme]; rad = '50%' if radio else '5px'
    inner = (f'<span style="width:8px;height:8px;border-radius:50%;background:#022329"></span>' if radio else icon('check', 14, '#022329', 2.4)) if on else ''
    return (f'<span style="display:inline-flex;align-items:center;justify-content:center;width:20px;height:20px;border-radius:{rad};'
            f'background:{"#14B8A6" if on else t["surface"]};border:1.5px solid {"#14B8A6" if on else t["line"]}">{inner}</span>')

def alert(kind, title, text, theme='light', w=420):
    if theme == 'light':
        m = {'success': ('#DDF5F1', '#0F7C74', 'check'), 'warning': ('#FBEAD8', '#9A6212', 'warning'), 'danger': ('#F7E1E3', '#B4232F', 'error'), 'info': ('#E1ECF5', '#2F6F9F', 'info')}
        tc, sc = '#022329', '#4A5E61'
    else:
        m = {'success': ('#0A3A3C', '#7FE3D6', 'check'), 'warning': ('#2E2614', '#E7B25B', 'warning'), 'danger': ('#331A1E', '#F08A8A', 'error'), 'info': ('#12283A', '#8DB8E0', 'info')}
        tc, sc = '#F3F5F2', '#9DB5B3'
    bg, fg, ic = m[kind]
    return (f'<div style="width:{w}px;display:flex;gap:12px;padding:14px 16px;border-radius:12px;background:{bg};border-left:4px solid {fg};font-family:var(--en)">'
            f'{icon(ic, 20, fg, 1.8)}<div><div style="font-size:14px;font-weight:600;color:{tc}">{title}</div><div style="font-size:13px;color:{sc};margin-top:2px">{text}</div></div></div>')

def card(inner, theme='light', w=None, pad=20):
    t = TH[theme]; ws = f'width:{w}px;' if w else ''
    return f'<div style="{ws}background:{t["surface"]};border:1px solid {t["line"]};border-radius:14px;padding:{pad}px">{inner}</div>'

# ------------------------------------------------------------------ UI kit boards
def ui_buttons(theme='light', w=1400, h=560):
    t = TH[theme]
    rows = []
    for kind in ('primary', 'secondary', 'tertiary', 'dark', 'danger'):
        rows.append(f'<div style="display:flex;align-items:center;gap:22px;height:66px;border-top:1px solid {t["line"]}">'
                    f'<div style="width:120px;font:600 12px var(--en);letter-spacing:.12em;color:{t["muted"]};text-transform:uppercase">{kind}</div>'
                    + ''.join(f'<div style="width:170px">{btn({"primary": "Approve batch", "secondary": "Reconcile", "tertiary": "View ledger", "dark": "Continue", "danger": "Reject"}[kind], kind, "md", theme, None, st)}</div>'
                              for st in ('', 'hover', 'focus', 'disabled'))
                    + f'<div>{btn("", kind, "md", theme, "plus")}</div></div>')
    head = ''.join(f'<div style="width:170px;font:600 12px var(--en);letter-spacing:.12em;color:{t["muted"]};text-transform:uppercase">{s}</div>' for s in ('Default', 'Hover', 'Focus', 'Disabled'))
    sizes = f'<div style="display:flex;align-items:center;gap:18px;margin-top:26px">{btn("Small · 32", "primary", "sm", theme)}{btn("Medium · 40", "primary", "md", theme)}{btn("Large · 48", "primary", "lg", theme)}{btn("Export report", "secondary", "md", theme, "download")}{btn("New entry", "primary", "md", theme, "plus")}{btn("Approve", "primary", "md", theme, "check")}</div>'
    return (f'<div style="width:{w}px;height:{h}px;background:{t["bg"]};padding:40px 48px;font-family:var(--en);color:{t["text"]}">'
            f'<div style="display:flex;gap:22px;height:30px;align-items:center"><div style="width:120px"></div>{head}<div style="font:600 12px var(--en);letter-spacing:.12em;color:{t["muted"]}">ICON</div></div>'
            + ''.join(rows) + sizes + '</div>')

def ui_forms(theme='light', w=1400, h=470):
    t = TH[theme]
    col1 = (field('Amount (USD)', '2,418,000.00', '', theme, 300, 'currency') + '<div style="height:16px"></div>'
            + field('Beneficiary IBAN', 'GB29 NWBK 6016 1331 9268 19', 'focus', theme, 300, 'bank') + '<div style="height:16px"></div>'
            + field('Value date', '32 Sep 2026', 'error', theme, 300, 'calendar', 'Enter a valid business date') + '<div style="height:16px"></div>'
            + field('Entity', 'Muscat Operations LLC', 'disabled', theme, 300, 'entities', 'Locked by approval policy v3'))
    sel = (f'<div style="width:300px"><div style="font-size:12.5px;color:{t["text2"]};margin-bottom:6px">Currency</div>'
           f'<div style="border:1.5px solid #14B8A6;border-radius:10px;background:{t["surface"]};overflow:hidden">'
           f'<div style="height:42px;display:flex;align-items:center;justify-content:space-between;padding:0 12px;font-size:14px">USD — US Dollar{icon("arrow_down", 16, t["muted"])}</div>'
           + ''.join(f'<div style="height:38px;display:flex;align-items:center;justify-content:space-between;padding:0 12px;font-size:13.5px;border-top:1px solid {t["line"]};{"background:" + t["sel"] if c == "USD" else ""}">{c} — {n}{icon("check", 15, "#0F7C74", 2) if c == "USD" else ""}</div>'
                     for c, n in (('USD', 'US Dollar'), ('OMR', 'Omani Rial'), ('GBP', 'Pound Sterling'), ('SGD', 'Singapore Dollar')))
           + '</div></div>')
    ctl = lambda a, b_: f'<div style="display:flex;align-items:center;gap:12px;height:34px;font-size:14px">{a}<span>{b_}</span></div>'
    col3 = (f'<div style="font-size:12.5px;color:{t["text2"]};margin-bottom:8px">Controls</div>'
            + ctl(check(True, theme), 'Require four-eyes approval') + ctl(check(False, theme), 'Allow partial settlement')
            + ctl(check(True, theme, True), 'Book at spot rate') + ctl(check(False, theme, True), 'Book at forward rate')
            + ctl(toggle(True, theme), 'Auto-reconcile bank feeds') + ctl(toggle(False, theme), 'Notify on every posting')
            + f'<div style="font-size:12.5px;color:{t["text2"]};margin:18px 0 8px">Segmented · tabs</div>'
            + f'<div style="display:inline-flex;padding:4px;border-radius:11px;background:{t["line"] if theme == "light" else "#0A3237"}">'
            + ''.join(f'<span style="padding:7px 14px;border-radius:8px;font:600 13px var(--en);{"background:" + t["surface"] + ";box-shadow:0 1px 2px rgba(2,35,41,.15)" if s == "Month" else "color:" + t["muted"]}">{s}</span>' for s in ('Day', 'Week', 'Month', 'Quarter'))
            + '</div>'
            + f'<div style="display:flex;gap:22px;margin-top:18px;border-bottom:1px solid {t["line"]}">' + ''.join(f'<span style="padding:0 0 10px;font:600 14px var(--en);{"color:" + t["text"] + ";border-bottom:2px solid #14B8A6" if s == "Payables" else "color:" + t["muted"]}">{s}</span>' for s in ('Overview', 'Payables', 'Receivables', 'Audit log')) + '</div>'
            + f'<div style="display:flex;gap:8px;margin-top:20px;flex-wrap:wrap">{chip("Posted", "success", theme)}{chip("Pending", "warning", theme)}{chip("Overdue", "danger", theme)}{chip("Draft", "neutral", theme)}{chip("Synced", "info", theme)}</div>')
    return (f'<div style="width:{w}px;height:{h}px;background:{t["bg"]};padding:44px 52px;font-family:var(--en);color:{t["text"]};display:flex;gap:56px">'
            f'<div>{col1}</div><div>{sel}</div><div style="width:420px">{col3}</div></div>')

def ui_feedback(theme='light', w=1400, h=480):
    t = TH[theme]
    toast = (f'<div style="width:380px;display:flex;align-items:center;gap:12px;padding:14px 16px;border-radius:12px;background:#022329;color:#F3F5F2;box-shadow:0 12px 30px rgba(2,35,41,.3)">'
             f'{icon("check", 18, "#7FE3D6", 2)}<div style="flex:1;font-size:13.5px">Batch 0412 approved · 2,418,000.00 USD</div><span style="font:600 13px var(--en);color:#7FE3D6">Undo</span></div>')
    modal = (f'<div style="width:470px;background:{t["surface"]};border-radius:16px;box-shadow:0 24px 60px rgba(2,35,41,.25);border:1px solid {t["line"]};overflow:hidden">'
             f'<div style="padding:22px 24px"><div style="display:flex;justify-content:space-between"><div style="font-size:18px;font-weight:600">Approve payment batch?</div>{icon("close", 18, t["muted"])}</div>'
             f'<div style="font-size:14px;color:{t["text2"]};margin-top:8px;line-height:1.5">14 payments to 9 beneficiaries will be released from <b>Muscat Operations LLC</b>. This action is recorded in the audit log.</div>'
             f'<div style="margin-top:16px;padding:12px 14px;border-radius:10px;background:{t["bg"]};display:flex;justify-content:space-between;font-size:13.5px"><span style="color:{t["text2"]}">Total</span><span class="tn" style="font-weight:600">2,418,000.00 USD</span></div></div>'
             f'<div style="padding:14px 24px;border-top:1px solid {t["line"]};display:flex;justify-content:flex-end;gap:10px">{btn("Cancel", "secondary", "md", theme)}{btn("Approve batch", "primary", "md", theme, "check")}</div></div>')
    prog = (f'<div style="width:380px"><div style="display:flex;justify-content:space-between;font-size:13px;color:{t["text2"]}"><span>Month-end close</span><span class="tn">68 %</span></div>'
            f'<div style="height:8px;border-radius:4px;background:{t["line"]};margin-top:8px;overflow:hidden"><div style="width:68%;height:100%;background:#14B8A6;border-radius:4px"></div></div>'
            f'<div style="display:flex;gap:0;margin-top:22px">' + ''.join(
                f'<div style="flex:1;display:flex;flex-direction:column;align-items:center;gap:6px;position:relative"><span style="width:26px;height:26px;border-radius:50%;display:flex;align-items:center;justify-content:center;font:600 12px var(--en);'
                f'{"background:#14B8A6;color:#022329" if i < 2 else ("border:2px solid #14B8A6;color:" + t["text"]) if i == 2 else "border:1.5px solid " + t["line"] + ";color:" + t["muted"]}">{icon("check", 14, "#022329", 2.4) if i < 2 else i + 1}</span>'
                f'<span style="font-size:11.5px;color:{t["text2"]}">{s}</span></div>' for i, s in enumerate(("Draft", "Review", "Approve", "Post")))
            + '</div></div>')
    skeleton = (f'<div style="width:380px;padding:18px;border-radius:14px;background:{t["surface"]};border:1px solid {t["line"]}">'
                + ''.join(f'<div style="height:{h_}px;width:{w_}%;border-radius:6px;background:linear-gradient(90deg,{t["line"]},{t["grid"]},{t["line"]});margin-top:{m}px"></div>' for h_, w_, m in ((12, 40, 0), (26, 70, 12), (10, 90, 16), (10, 80, 8)))
                + f'<div style="display:flex;align-items:center;gap:10px;margin-top:18px;font-size:12.5px;color:{t["muted"]}"><img src="{A}/icon/svg/WFS_Icon_Flat_Teal.svg" style="width:20px;height:20px">Loading entities…</div></div>')
    empty = (f'<div style="width:380px;padding:28px;border-radius:14px;border:1.5px dashed {t["line"]};text-align:center">{icon("reconcile", 34, "#14B8A6", 1.5)}'
             f'<div style="font-size:16px;font-weight:600;margin-top:10px">All accounts reconciled</div><div style="font-size:13px;color:{t["text2"]};margin-top:4px">Nothing needs your attention today.</div>'
             f'<div style="margin-top:14px">{btn("View history", "secondary", "sm", theme)}</div></div>')
    return (f'<div style="width:{w}px;height:{h}px;background:{t["bg"]};padding:40px 48px;font-family:var(--en);color:{t["text"]};display:grid;grid-template-columns:440px 480px 1fr;gap:34px">'
            f'<div style="display:flex;flex-direction:column;gap:14px">{alert("success", "Bank feed synced", "5 accounts updated 2 min ago.", theme)}{alert("warning", "Approval due today", "Payroll · September must be approved by 16:00.", theme)}'
            f'{alert("danger", "Payment rejected", "IBAN checksum failed for 1 beneficiary.", theme)}{alert("info", "FX rates refreshed", "Rates as of 09:30 UTC from 3 providers.", theme)}{toast}</div>'
            f'<div style="display:flex;flex-direction:column;gap:28px">{modal}{prog}</div><div style="display:flex;flex-direction:column;gap:22px">{skeleton}{empty}</div></div>')

def ui_table(theme='light', w=1400, h=520):
    t = TH[theme]
    rows = [('JE-2026-09-0418', '30 Sep', 'Muscat Operations LLC', 'Accrued payroll — September', '1,106,540.250', 'OMR', 'Posted', 'success'),
            ('JE-2026-09-0417', '30 Sep', 'WFS Holding Ltd', 'Intercompany loan interest', '84,210.00', 'USD', 'Pending', 'warning'),
            ('JE-2026-09-0416', '29 Sep', 'London Trading Ltd', 'FX revaluation — GBP accounts', '(114,208.93)', 'GBP', 'Posted', 'success'),
            ('JE-2026-09-0415', '29 Sep', 'Singapore Pte Ltd', 'Supplier invoice INV-88213', '386,200.00', 'SGD', 'Draft', 'neutral'),
            ('JE-2026-09-0414', '28 Sep', 'Dubai Services FZ-LLC', 'PDC deposit — 14 cheques', '1,418,000.00', 'AED', 'Posted', 'success'),
            ('JE-2026-09-0413', '28 Sep', 'WFS Holding Ltd', 'Commission accrual Q3', '92,410.80', 'GBP', 'Overdue', 'danger')]
    th = f'font:600 11.5px var(--en);letter-spacing:.08em;text-transform:uppercase;color:{t["muted"]};text-align:left;padding:12px 14px;border-bottom:1px solid {t["line"]}'
    body = ''.join(f'<tr style="{"background:" + t["sel"] if i == 1 else ""}"><td style="padding:0 14px;height:48px;border-bottom:1px solid {t["line"]}">{check(i == 1, theme)}</td>'
                   f'<td class="tn" style="padding:0 14px;border-bottom:1px solid {t["line"]};font-size:13.5px;color:{t["accent"]};font-weight:600">{a}</td>'
                   f'<td class="tn" style="padding:0 14px;border-bottom:1px solid {t["line"]};font-size:13.5px;color:{t["text2"]}">{d}</td>'
                   f'<td style="padding:0 14px;border-bottom:1px solid {t["line"]};font-size:13.5px">{e}</td><td style="padding:0 14px;border-bottom:1px solid {t["line"]};font-size:13.5px;color:{t["text2"]}">{m}</td>'
                   f'<td class="tn" style="padding:0 14px;border-bottom:1px solid {t["line"]};font-size:13.5px;text-align:right;font-weight:500">{v}</td>'
                   f'<td style="padding:0 14px;border-bottom:1px solid {t["line"]};font-size:12.5px;color:{t["muted"]}">{c}</td><td style="padding:0 14px;border-bottom:1px solid {t["line"]}">{chip(s, k, theme)}</td>'
                   f'<td style="padding:0 14px;border-bottom:1px solid {t["line"]}">{icon("more", 18, t["muted"])}</td></tr>' for i, (a, d, e, m, v, c, s, k) in enumerate(rows))
    bar = (f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px"><div style="display:flex;gap:10px">'
           f'{field("", "Search journal entries", "", theme, 300, "search").replace("margin-bottom:6px", "margin-bottom:0")}'
           f'</div><div style="display:flex;gap:10px">{btn("Filters · 3", "secondary", "md", theme, "filter")}{btn("Export", "secondary", "md", theme, "download")}{btn("New journal", "primary", "md", theme, "plus")}</div></div>')
    pag = (f'<div style="display:flex;justify-content:space-between;align-items:center;padding:14px;font-size:13px;color:{t["text2"]}"><span>1 selected · 6 of 1,284 entries</span>'
           f'<div style="display:flex;gap:6px">' + ''.join(f'<span style="width:32px;height:32px;border-radius:8px;display:flex;align-items:center;justify-content:center;{"background:#022329;color:#F3F5F2" if p == "1" else "border:1px solid " + t["line"]}" class="tn">{p}</span>' for p in ("1", "2", "3", "…", "214")) + '</div></div>')
    return (f'<div style="width:{w}px;height:{h}px;background:{t["bg"]};padding:40px 48px;font-family:var(--en);color:{t["text"]}">{bar}'
            f'<div style="background:{t["surface"]};border:1px solid {t["line"]};border-radius:14px;overflow:hidden"><table style="width:100%;border-collapse:collapse">'
            f'<tr><th style="{th};width:30px"></th><th style="{th}">Reference</th><th style="{th}">Date</th><th style="{th}">Entity</th><th style="{th}">Memo</th><th style="{th};text-align:right">Amount</th><th style="{th}">Ccy</th><th style="{th}">Status</th><th style="{th}"></th></tr>{body}</table>{pag}</div></div>')

# ------------------------------------------------------------------ product screens
def shell(theme, active, title, subtitle, content, w=1440, h=900, actions=''):
    t = TH[theme]
    nav = [('overview', 'Overview'), ('entities', 'Entities'), ('ledger', 'Ledger'), ('treasury', 'Treasury'), ('receivable', 'Receivables'),
           ('payable', 'Payables'), ('payroll', 'Payroll'), ('approval', 'Approvals'), ('cheque', 'PDC / Cheques'), ('report', 'Reports'), ('integration', 'Integrations'), ('settings', 'Settings')]
    navh = ''.join(f'<div style="display:flex;align-items:center;gap:12px;height:36px;padding:0 12px;border-radius:8px;'
                   f'{"background:" + t["sel"] + ";color:" + t["text"] + ";font-weight:600" if l == active else "color:" + t["text2"]}">'
                   f'{icon(k, 18, t["accent"] if l == active else t["muted"])}<span style="font-size:13.5px">{l}</span>'
                   f'{"<span style=margin-left:auto;font-size:11px;font-weight:600;background:#14B8A6;color:#022329;border-radius:9px;padding:1px 7px>9</span>" if l == "Approvals" else ""}</div>' for k, l in nav)
    return f'''<div style="width:{w}px;height:{h}px;background:{t["bg"]};display:flex;font-family:var(--en);color:{t["text"]}">
  <div style="width:236px;background:{t["side"]};border-right:1px solid {t["line"]};padding:22px 16px;display:flex;flex-direction:column;gap:4px">
    <div style="padding:2px 10px 22px">{lockup(26, theme)}</div>{navh}
    <div style="margin-top:auto;display:flex;align-items:center;gap:10px;padding:10px;border-top:1px solid {t["line"]}"><span style="width:32px;height:32px;border-radius:50%;background:#0E3D42;color:#7FE3D6;display:flex;align-items:center;justify-content:center;font:600 12px var(--en)">LH</span>
    <div><div style="font-size:13px;font-weight:600">Leila Haddad</div><div style="font-size:11.5px;color:{t["muted"]}">Group CFO</div></div></div></div>
  <div style="flex:1;padding:26px 30px;display:flex;flex-direction:column;gap:18px;min-width:0">
    <div style="display:flex;align-items:center;justify-content:space-between"><div><div style="font-size:12.5px;color:{t["muted"]}">{subtitle}</div><div style="font-size:26px;font-weight:600;letter-spacing:-.015em;margin-top:2px">{title}</div></div>
    <div style="display:flex;gap:10px;align-items:center">{actions}</div></div>{content}</div></div>'''

def screen_approvals(theme='light'):
    t = TH[theme]
    items = [('Supplier payment · Batch 0412', 'Treasury · Muscat Operations LLC', '2,418,000.00 USD', 'Due today 16:00', 'warning', True),
             ('Payroll · September', 'HR / Finance · 5 entities', '1,106,540.250 OMR', 'Due today', 'warning', False),
             ('PDC deposit · 14 cheques', 'Receivables · Dubai Services', '386,200.00 AED', 'Due 2 Oct', 'neutral', False),
             ('Commission run · Q3', 'Sales ops · London Trading', '92,410.80 GBP', 'Overdue 1 day', 'danger', False),
             ('Intercompany loan · WFS Holding', 'Treasury · Group', '5,000,000.00 USD', 'Due 4 Oct', 'neutral', False)]
    lst = ''.join(f'<div style="display:flex;align-items:center;gap:14px;padding:14px 16px;border-radius:12px;{"background:" + t["sel"] + ";border:1.5px solid #14B8A6" if a else "border:1px solid " + t["line"] + ";background:" + t["surface"]}">'
                  f'{check(a, theme)}<div style="flex:1"><div style="font-size:14px;font-weight:600">{n}</div><div style="font-size:12.5px;color:{t["muted"]}">{s}</div></div>'
                  f'<div style="text-align:right"><div class="tn" style="font-size:14px;font-weight:600">{v}</div><div style="margin-top:4px">{chip(d, k, theme)}</div></div></div>' for n, s, v, d, k, a in items)
    detail = card(f'''<div style="display:flex;justify-content:space-between;align-items:center"><div style="font-size:17px;font-weight:600">Batch 0412</div>{chip("Awaiting 2nd approver", "warning", theme)}</div>
      <div class="tn" style="font-size:34px;font-weight:600;letter-spacing:-.02em;margin-top:14px">2,418,000.00 <span style="font-size:15px;color:{t["muted"]};font-weight:400">USD</span></div>
      <div style="font-size:13px;color:{t["text2"]};margin-top:4px">14 payments · 9 beneficiaries · from Bank Muscat ·· 4410</div>
      <div style="margin-top:18px;font:600 11.5px var(--en);letter-spacing:.1em;color:{t["muted"]}">APPROVAL CHAIN</div>
      {"".join(f'<div style="display:flex;gap:12px;align-items:center;margin-top:12px"><span style="width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;{c}">{ic}</span><div style="flex:1"><div style="font-size:13.5px;font-weight:600">{n}</div><div style="font-size:12px;color:{t["muted"]}">{r}</div></div><span class="tn" style="font-size:12px;color:{t["muted"]}">{tm}</span></div>' for n, r, tm, c, ic in (("Omar Al-Rashdi", "Treasury manager · prepared", "09:12", "background:#14B8A6", icon("check", 14, "#022329", 2.4)), ("Sara Lindqvist", "Financial controller · approved", "10:40", "background:#14B8A6", icon("check", 14, "#022329", 2.4)), ("Leila Haddad", "Group CFO · you", "—", "border:2px solid #14B8A6", "")))}
      <div style="margin-top:20px;display:flex;gap:10px">{btn("Reject", "secondary", "md", theme)}{btn("Approve batch", "primary", "md", theme, "check")}</div>''', theme, 440, 24)
    content = f'<div style="display:flex;gap:18px"><div style="flex:1;display:flex;flex-direction:column;gap:10px">{lst}</div>{detail}</div>'
    return shell(theme, 'Approvals', 'Approvals', 'Four-eyes control · policy v3 · 9 waiting', content, actions=btn('Delegate', 'secondary', 'md', theme, 'team') + btn('Approve selected', 'primary', 'md', theme, 'check'))

def screen_treasury(theme='light'):
    t = TH[theme]; dv = B.DATAVIZ[theme]
    banks = [('Bank Muscat', '·· 4410', 'OMR', '3,912,440.500', '+1.1%'), ('HSBC UK', '·· 2291', 'GBP', '5,208,775.10', '−0.8%'), ('DBS Singapore', '·· 7765', 'SGD', '9,604,300.00', '+2.9%'),
             ('Emirates NBD', '·· 0934', 'AED', '14,221,090.75', '+0.4%'), ('JPMorgan Chase', '·· 5520', 'USD', '21,480,120.00', '+4.2%')]
    rows = ''.join(f'<div style="display:flex;align-items:center;gap:12px;padding:12px 0;border-top:1px solid {t["line"]}"><span style="width:34px;height:34px;border-radius:9px;background:{t["chip"]};display:flex;align-items:center;justify-content:center">{icon("bank", 17, t["accent"])}</span>'
                   f'<div style="flex:1"><div style="font-size:13.5px;font-weight:600">{n} <span style="color:{t["muted"]};font-weight:400">{a}</span></div><div style="font-size:12px;color:{t["muted"]}">{c} · synced 2 min ago</div></div>'
                   f'<div class="tn" style="font-size:14px;font-weight:600">{v}</div><div class="tn" style="width:60px;text-align:right;font-size:12.5px;color:{t["neg"] if d.startswith("−") else t["pos"]}">{d}</div></div>' for n, a, c, v, d in banks)
    mix_ = [('USD', 44), ('AED', 20), ('SGD', 15), ('GBP', 13), ('OMR', 8)]
    stack = ''.join(f'<div style="width:{p}%;background:{(dv + [B.HEX["wfs-deep"]])[i]};height:100%;{"border-right:2px solid " + t["surface"] if i < 4 else ""}"></div>' for i, (_, p) in enumerate(mix_))
    legend = ''.join(f'<span style="display:inline-flex;align-items:center;gap:6px;font-size:12.5px;color:{t["text2"]};margin-right:14px"><span style="width:9px;height:9px;border-radius:2px;background:{(dv + [B.HEX["wfs-deep"]])[i]}"></span>{c} <span class="tn">{p}%</span></span>' for i, (c, p) in enumerate(mix_))
    fx = ''.join(f'<div style="display:flex;justify-content:space-between;padding:10px 0;border-top:1px solid {t["line"]};font-size:13.5px"><span>{a}</span><span class="tn">{b}</span><span class="tn" style="color:{t["neg"] if c.startswith("−") else t["pos"]}">{c}</span></div>'
                 for a, b, c in (('USD / OMR', '0.38450', '+0.01%'), ('USD / AED', '3.67250', '0.00%'), ('GBP / USD', '1.27415', '−0.22%'), ('USD / SGD', '1.34780', '+0.08%')))
    content = f'''<div style="display:grid;grid-template-columns:1.5fr 1fr;gap:18px;flex:1">
      {card(f'<div style="display:flex;justify-content:space-between"><div><div style="font-size:15px;font-weight:600">Consolidated cash</div><div style="font-size:12px;color:{t["muted"]}">5 banks · 5 currencies · in USD</div></div><div class="tn" style="font-size:28px;font-weight:600">48,612,480.25</div></div>{area_chart(760, 250, CASH, theme, MONTHS, ymax=56, fmt=lambda v: f"{v:.0f}M")}', theme)}
      {card(f'<div style="font-size:15px;font-weight:600">Currency exposure</div><div style="height:14px;border-radius:7px;overflow:hidden;display:flex;margin:18px 0 12px">{stack}</div>{legend}<div style="font-size:15px;font-weight:600;margin-top:26px">FX rates · 09:30 UTC</div>{fx}', theme)}
      <div style="grid-column:1/3">{card(f'<div style="display:flex;justify-content:space-between;align-items:center"><div style="font-size:15px;font-weight:600">Bank accounts</div>{btn("Connect bank", "secondary", "sm", theme, "link")}</div>{rows}', theme)}</div></div>'''
    return shell(theme, 'Treasury', 'Treasury', 'Cash, banks and FX · all entities', content, actions=btn('Transfer', 'secondary', 'md', theme, 'fx') + btn('New payment', 'primary', 'md', theme, 'plus'))

def screen_ledger(theme='light'):
    inner = ui_table(theme, 1160, 700).replace('padding:40px 48px', 'padding:0')
    return shell(theme, 'Ledger', 'General ledger', 'Journal entries · September 2026 · open period', inner, actions=chip('Period open', 'success', theme) + btn('Close period', 'dark', 'md', theme, 'control'))

def screen_reports(theme='light'):
    t = TH[theme]
    rep = [('Consolidated P&L', 'Monthly · 5 entities', 'report'), ('Cash flow statement', 'Weekly · IFRS', 'analytics'), ('Aged receivables', 'Daily · by customer', 'receivable'),
           ('Aged payables', 'Daily · by supplier', 'payable'), ('Budget vs actual', 'Monthly · by cost centre', 'budget'), ('13-week cash forecast', 'Weekly · rolling', 'forecast')]
    grid = ''.join(card(f'<div style="display:flex;justify-content:space-between">{icon(ic, 26, t["accent"])}{icon("more", 18, t["muted"])}</div><div style="font-size:15px;font-weight:600;margin-top:18px">{n}</div>'
                        f'<div style="font-size:12.5px;color:{t["muted"]};margin-top:4px">{s}</div><div style="margin-top:16px">{spark(250, 36, [3, 4, 3.6, 5, 4.8, 6, 5.7, 6.4], B.DATAVIZ[theme][0])}</div>', theme) for n, s, ic in rep)
    content = f'<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:18px">{grid}</div>'
    return shell(theme, 'Reports', 'Reports', 'Scheduled and on-demand · 42 reports', content, actions=btn('Schedule', 'secondary', 'md', theme, 'clock') + btn('New report', 'primary', 'md', theme, 'plus'))

def mobile_approvals(w=390, h=844, theme='light'):
    t = TH[theme]
    items = [('Batch 0412', '2,418,000.00 USD', 'warning', 'Due 16:00'), ('Payroll · Sep', '1,106,540.250 OMR', 'warning', 'Due today'), ('Commission Q3', '92,410.80 GBP', 'danger', 'Overdue')]
    lst = ''.join(f'<div style="padding:14px 16px;border-radius:14px;background:{t["surface"]};border:1px solid {t["line"]};margin-top:10px"><div style="display:flex;justify-content:space-between"><span style="font-size:14px;font-weight:600">{a}</span>{chip(d, k, theme)}</div>'
                  f'<div class="tn" style="font-size:20px;font-weight:600;margin-top:8px">{b}</div><div style="display:flex;gap:8px;margin-top:12px">{btn("Reject", "secondary", "sm", theme)}{btn("Approve", "primary", "sm", theme, "check")}</div></div>' for a, b, k, d in items)
    return (f'<div style="width:{w}px;height:{h}px;background:{t["bg"]};font-family:var(--en);padding:62px 18px 0;color:{t["text"]}">'
            f'<div style="display:flex;justify-content:space-between;align-items:center">{lockup(20, theme)}{icon("bell", 20, t["text2"])}</div>'
            f'<div style="font-size:28px;font-weight:600;letter-spacing:-.02em;margin-top:22px">Approvals</div><div style="font-size:13px;color:{t["muted"]}">9 waiting · 3 due today</div>{lst}</div>')

def push_notification(w=390, h=844):
    return (f'<div style="width:{w}px;height:{h}px;background:url({A}/guidelines/source/img/art_architecture.jpg) center/cover;font-family:var(--en);padding:120px 12px 0;color:#fff">'
            f'<div style="text-align:center;font-size:76px;font-weight:300;letter-spacing:-.02em">09:41</div><div style="text-align:center;font-size:17px;opacity:.85">Monday 30 September</div>'
            f'<div style="margin-top:60px;border-radius:22px;background:rgba(243,245,242,.82);color:#022329;padding:14px 16px;display:flex;gap:12px">'
            f'<img src="{A}/icon/app/WFS_AppIcon_Dark_128.png" style="width:38px;height:38px;border-radius:9px">'
            f'<div style="flex:1"><div style="display:flex;justify-content:space-between;font-size:13px"><b>WFS</b><span style="color:#4A5E61">now</span></div>'
            f'<div style="font-size:14px;font-weight:600;margin-top:2px">Approval needed · Batch 0412</div><div style="font-size:13.5px;color:#4A5E61">2,418,000.00 USD from Muscat Operations LLC is due by 16:00.</div></div></div></div>')

def email_notification(w=720, h=860):
    return f'''<div style="width:{w}px;height:{h}px;background:#EDF1EF;font-family:var(--en);padding:40px 60px;color:#022329">
  <div style="background:#fff;border-radius:14px;overflow:hidden;border:1px solid #D6DEDB">
    <div style="height:84px;background:linear-gradient(160deg,#0E3D42,#022329);display:flex;align-items:center;padding:0 32px">{lockup(24, "dark")}</div>
    <div style="padding:34px 32px"><div style="font-size:12px;letter-spacing:.14em;font-weight:600;color:#0F7C74">APPROVAL REQUEST</div>
    <div style="font-size:26px;font-weight:600;letter-spacing:-.015em;margin-top:10px">Batch 0412 needs your approval</div>
    <div style="font-size:15px;line-height:1.55;color:#4A5E61;margin-top:12px">Omar Al-Rashdi prepared 14 supplier payments from Muscat Operations LLC. Sara Lindqvist has approved. Your approval releases the batch.</div>
    <div style="margin-top:22px;border:1px solid #E3E9E7;border-radius:10px">{"".join(f'<div style="display:flex;justify-content:space-between;padding:12px 16px;font-size:14px;border-top:1px solid #E3E9E7"><span style="color:#4A5E61">{a}</span><span class="tn" style="font-weight:600">{b}</span></div>' for a, b in (("Total", "2,418,000.00 USD"), ("Payments", "14"), ("Due", "30 Sep 2026, 16:00 GST")))}</div>
    <div style="margin-top:26px">{btn("Review in WFS", "primary", "lg")}</div>
    <div style="font-size:12.5px;color:#80918F;margin-top:26px;line-height:1.5">You receive this because you are an approver on policy v3. WFS will never ask for your password by email.</div></div>
    <div style="padding:18px 32px;border-top:1px solid #E3E9E7;font-size:11.5px;color:#80918F;display:flex;justify-content:space-between"><span>WFS · Wusool Financial System</span><span>A WUSOOL Tech Product</span></div></div></div>'''

def dev_portal(w=1440, h=900):
    code = ('<span style="color:#7FE3D6">curl</span> https://api.wfs.example/v1/payments \\\n'
            '  -H <span style="color:#E7B25B">"Authorization: Bearer $WFS_API_KEY"</span> \\\n'
            '  -H <span style="color:#E7B25B">"Idempotency-Key: 7c1e…"</span> \\\n'
            '  -d <span style="color:#E7B25B">\'{\n    "entity_id": "ent_muscat_ops",\n    "amount": "2418000.00",\n    "currency": "USD",\n    "requires_approval": true\n  }\'</span>')
    resp = ('{\n  <span style="color:#7FE3D6">"id"</span>: <span style="color:#E7B25B">"pay_01J9Z…"</span>,\n  <span style="color:#7FE3D6">"status"</span>: <span style="color:#E7B25B">"pending_approval"</span>,\n'
            '  <span style="color:#7FE3D6">"approval_policy"</span>: <span style="color:#E7B25B">"v3"</span>,\n  <span style="color:#7FE3D6">"amount"</span>: <span style="color:#E7B25B">"2418000.00"</span>\n}')
    side = ''.join(f'<div style="padding:7px 12px;border-radius:7px;font-size:13.5px;{"background:#DDF5F1;color:#022329;font-weight:600" if s == "Create a payment" else "color:#4A5E61"}">{s}</div>'
                   for s in ('Introduction', 'Authentication', 'Idempotency', 'Entities', 'Accounts', 'Create a payment', 'Approvals', 'Webhooks', 'Reports', 'Errors'))
    return f'''<div style="width:{w}px;height:{h}px;background:#fff;font-family:var(--en);color:#022329;display:flex;flex-direction:column">
  <div style="height:64px;border-bottom:1px solid #E3E9E7;display:flex;align-items:center;gap:28px;padding:0 32px">{lockup(24, "light")}<span style="font-size:14px;font-weight:600;color:#0F7C74">Developers</span>
  <span style="font-size:14px;color:#4A5E61">API reference</span><span style="font-size:14px;color:#4A5E61">Guides</span><span style="font-size:14px;color:#4A5E61">SDKs</span><span style="font-size:14px;color:#4A5E61">Status</span>
  <span style="margin-left:auto">{field("", "Search docs", "", "light", 260, "search").replace("margin-bottom:6px", "margin-bottom:0")}</span></div>
  <div style="flex:1;display:flex"><div style="width:250px;border-right:1px solid #E3E9E7;padding:22px 16px">{side}</div>
  <div style="flex:1;padding:36px 44px"><div style="font-size:12px;letter-spacing:.14em;font-weight:600;color:#0F7C74">PAYMENTS</div><div style="font-size:34px;font-weight:600;letter-spacing:-.02em;margin-top:8px">Create a payment</div>
  <div style="font-size:15px;line-height:1.6;color:#4A5E61;margin-top:12px;width:520px">Creates a payment on behalf of an entity. When the entity's approval policy requires it, the payment is created in <code style="background:#EDF1EF;padding:2px 6px;border-radius:5px">pending_approval</code> and released only after all approvers sign off.</div>
  <div style="margin-top:22px;font:600 12px var(--en);letter-spacing:.1em;color:#80918F">PARAMETERS</div>
  {"".join(f'<div style="display:flex;gap:16px;padding:12px 0;border-top:1px solid #E3E9E7;width:560px"><code style="width:150px;font-size:13.5px;color:#0F7C74">{a}</code><span style="width:70px;font-size:12.5px;color:#80918F">{b}</span><span style="font-size:13.5px;color:#4A5E61">{c}</span></div>' for a, b, c in (("entity_id", "string", "The paying entity."), ("amount", "decimal", "Positive amount as a string."), ("currency", "ISO 4217", "Three-letter currency code."), ("requires_approval", "boolean", "Defaults to the entity policy.")))}</div>
  <div style="width:560px;background:#022329;padding:30px;color:#F3F5F2"><div style="display:flex;gap:8px">{chip("POST", "success", "dark")}<span style="font-size:13px;color:#9DB5B3;align-self:center">/v1/payments</span></div>
  <pre style="font:13px/1.65 'IBM Plex Mono',ui-monospace,monospace;margin-top:18px;white-space:pre-wrap;color:#DDF5F1">{code}</pre>
  <div style="font:600 12px var(--en);letter-spacing:.1em;color:#6F8987;margin-top:22px">RESPONSE · 201</div><pre style="font:13px/1.65 'IBM Plex Mono',ui-monospace,monospace;margin-top:10px;color:#DDF5F1">{resp}</pre></div></div></div>'''

def status_page(w=1200, h=760):
    comps = [('Web application', 'Operational'), ('Public API', 'Operational'), ('Bank connectivity', 'Degraded · 1 provider'), ('Reporting engine', 'Operational'), ('Webhooks', 'Operational')]
    bars = lambda deg: ''.join(f'<span style="width:6px;height:28px;border-radius:2px;background:{"#E7B25B" if deg and i in (71, 72) else "#14B8A6"}"></span>' for i in range(90))
    return f'''<div style="width:{w}px;height:{h}px;background:#F3F5F2;font-family:var(--en);color:#022329;padding:40px 70px">
  <div style="display:flex;justify-content:space-between;align-items:center">{lockup(26, "light")}<span style="font-size:14px;color:#4A5E61">status.wfs.example</span></div>
  <div style="margin-top:30px;padding:20px 24px;border-radius:14px;background:#FBEAD8;border-left:4px solid #B7791F;display:flex;gap:12px">{icon("warning", 22, "#9A6212", 1.8)}<div><div style="font-weight:600">Partial degradation · bank connectivity</div><div style="font-size:13.5px;color:#4A5E61;margin-top:2px">One provider is returning delayed statements. Balances are delayed up to 15 minutes. Updated 09:52 UTC.</div></div></div>
  <div style="margin-top:22px;background:#fff;border:1px solid #D6DEDB;border-radius:14px">{"".join(f'<div style="padding:16px 22px;border-top:1px solid #E3E9E7"><div style="display:flex;justify-content:space-between;font-size:14.5px"><b style="font-weight:600">{a}</b><span style="color:{"#9A6212" if "Degraded" in b else "#0F7C74"}">{b}</span></div><div style="display:flex;gap:3px;margin-top:10px">{bars("Degraded" in b)}</div></div>' for a, b in comps)}</div>
  <div style="display:flex;justify-content:space-between;font-size:12px;color:#80918F;margin-top:10px"><span>90 days ago</span><span class="tn">99.98 % uptime</span><span>Today</span></div></div>'''

def empty_404(w=1200, h=760):
    return f'''<div style="width:{w}px;height:{h}px;background:linear-gradient(160deg,#0E3D42,#022329);font-family:var(--en);color:#F3F5F2;position:relative;overflow:hidden">
  <img src="{A}/graphic-system/fields/WFS_Overlay_Convergence_OnDark.svg" style="position:absolute;left:260px;top:-160px;width:1300px">
  <div style="position:absolute;left:70px;top:50px">{lockup(26, "dark")}</div>
  <div style="position:absolute;left:70px;top:270px"><div class="tn" style="font-size:120px;font-weight:600;letter-spacing:-.04em;color:#7FE3D6">404</div>
  <div style="font-size:34px;font-weight:600;letter-spacing:-.02em">This view is outside the field.</div><div style="font-size:17px;color:#9DB5B3;margin-top:10px">The page you requested doesn't exist or has moved.</div>
  <div style="display:flex;gap:12px;margin-top:28px">{btn("Back to overview", "primary", "lg", "dark", "home")}{btn("Contact support", "secondary", "lg", "dark")}</div></div></div>'''

# ------------------------------------------------------------------ social media system
def _social_base(w, h, theme='dark', pattern='convergence', inner='', logo_pos='bl', logo_h=34):
    bg = 'linear-gradient(160deg,#0E3D42,#022329)' if theme == 'dark' else '#F3F5F2'
    ov = {'convergence': 'WFS_Overlay_Convergence_OnDark.svg', 'field': 'WFS_Overlay_Unified_Field_OnDark.svg', 'crop': 'WFS_Overlay_Aperture_Crop_OnLight.svg', None: None}[pattern]
    ovh = f'<img src="{A}/graphic-system/fields/{ov}" style="position:absolute;left:{w*0.18:.0f}px;top:{-h*0.12:.0f}px;width:{max(w, h)*1.25:.0f}px">' if ov else ''
    pos = {'bl': f'left:{w*0.075:.0f}px;bottom:{h*0.065:.0f}px', 'tl': f'left:{w*0.075:.0f}px;top:{h*0.065:.0f}px', 'br': f'right:{w*0.075:.0f}px;bottom:{h*0.065:.0f}px', 'c': f'left:50%;bottom:{h*0.065:.0f}px;transform:translateX(-50%)'}[logo_pos]
    return (f'<div style="width:{w}px;height:{h}px;background:{bg};position:relative;overflow:hidden;font-family:var(--en);color:{"#F3F5F2" if theme == "dark" else "#022329"}">'
            f'{ovh}{inner}<div style="position:absolute;{pos}">{lockup(logo_h, theme)}</div></div>')

def sm_quote(w=1080, h=1080):
    inner = (f'<div style="position:absolute;left:84px;right:84px;top:170px"><div style="font-size:26px;letter-spacing:.16em;font-weight:600;color:#7FE3D6">ONE FINANCIAL TRUTH</div>'
             f'<div style="font-size:78px;line-height:1.04;letter-spacing:-.03em;font-weight:600;margin-top:28px">"We closed five entities in three and a half days — with one ledger."</div>'
             f'<div style="font-size:26px;color:#9DB5B3;margin-top:34px">— Group CFO, multi-entity holding</div></div>')
    return _social_base(w, h, 'dark', 'field', inner)

def sm_stat(w=1080, h=1080):
    inner = (f'<div style="position:absolute;left:84px;top:160px;right:84px"><div style="font-size:26px;letter-spacing:.16em;font-weight:600;color:#0F7C74">BY THE NUMBERS</div>'
             f'<div class="tn" style="font-size:250px;font-weight:600;letter-spacing:-.05em;line-height:1;margin-top:40px">−41%</div>'
             f'<div style="font-size:46px;line-height:1.15;letter-spacing:-.02em;font-weight:600;margin-top:26px;width:820px">time to month-end close across every entity.</div>'
             f'<div style="font-size:22px;color:#80918F;margin-top:26px">Median across WFS pilot customers, 2026.</div></div>')
    return _social_base(w, h, 'light', 'crop', inner)

def sm_carousel(i, w=1080, h=1350):
    slides = [
        ('01 / 04', 'Five entities.<br>One view.', 'How multi-entity finance teams run one close with WFS.', 'dark', 'convergence'),
        ('02 / 04', 'Connect every bank', 'Balances from 5 banks and 5 currencies, refreshed continuously.', 'light', None),
        ('03 / 04', 'Approve with control', 'Four-eyes policies on every payment, from any device.', 'light', None),
        ('04 / 04', 'Close in days, not weeks', 'One ledger. One truth. Every operation in view.', 'dark', 'field')]
    n, t_, s, th, pat = slides[i]
    vis = ''
    if i == 1:
        vis = f'<div style="position:absolute;left:84px;right:84px;bottom:190px;border-radius:24px;overflow:hidden;border:1px solid #D6DEDB;height:520px"><div style="transform:scale(.9);transform-origin:0 0">{screen_treasury("light")}</div></div>'
    if i == 2:
        vis = f'<div style="position:absolute;left:50%;bottom:150px;transform:translateX(-50%) scale(1.05);transform-origin:50% 100%">{C.phone(mobile_approvals())}</div>'
    col = '#7FE3D6' if th == 'dark' else '#0F7C74'
    inner = (f'<div style="position:absolute;left:84px;top:90px;right:84px"><div class="tn" style="font-size:24px;letter-spacing:.14em;font-weight:600;color:{col}">{n}</div>'
             f'<div style="font-size:{92 if i in (0, 3) else 66}px;line-height:1.02;letter-spacing:-.035em;font-weight:600;margin-top:26px">{t_}</div>'
             f'<div style="font-size:28px;line-height:1.35;color:{"#9DB5B3" if th == "dark" else "#4A5E61"};margin-top:22px;width:820px">{s}</div></div>{vis}'
             + (f'<div style="position:absolute;right:84px;bottom:92px;display:flex;align-items:center;gap:10px;font:600 22px var(--en);color:{col}">Swipe {icon("chevron", 26, col, 2)}</div>' if i < 3 else ''))
    return _social_base(w, h, th, pat, inner, 'bl', 32)

def sm_story(w=1080, h=1920):
    inner = (f'<div style="position:absolute;left:50%;top:420px;transform:translateX(-50%)"><img src="{A}/icon/svg/WFS_Icon_Premium.svg" style="width:430px"></div>'
             f'<div style="position:absolute;left:90px;right:90px;top:1000px;text-align:center"><div style="font-size:30px;letter-spacing:.16em;font-weight:600;color:#7FE3D6">NOW AVAILABLE</div>'
             f'<div style="font-size:100px;line-height:1.02;letter-spacing:-.035em;font-weight:600;margin-top:30px">Multi-entity treasury</div>'
             f'<div style="font-size:34px;color:#9DB5B3;margin-top:28px">Every bank. Every currency. One view.</div>'
             f'<div style="display:inline-flex;margin-top:60px">{btn("Learn more", "primary", "lg", "dark")}</div></div>')
    return _social_base(w, h, 'dark', 'convergence', inner, 'c', 44)

def sm_linkedin(w=1200, h=627):
    inner = (f'<div style="position:absolute;left:70px;top:70px;width:560px"><div style="font-size:18px;letter-spacing:.16em;font-weight:600;color:#7FE3D6">PRODUCT UPDATE</div>'
             f'<div style="font-size:54px;line-height:1.04;letter-spacing:-.03em;font-weight:600;margin-top:18px">Approvals, now across every entity.</div></div>'
             f'<div style="position:absolute;left:640px;top:80px;width:620px;height:600px;border-radius:18px;overflow:hidden;box-shadow:0 30px 70px rgba(0,0,0,.4)"><div style="transform:scale(.6);transform-origin:0 0">{screen_approvals("light")}</div></div>')
    return _social_base(w, h, 'dark', 'field', inner, 'bl', 30)

def sm_x_header(w=1500, h=500):
    inner = (f'<div style="position:absolute;right:90px;top:170px;text-align:right"><div style="font-size:60px;font-weight:600;letter-spacing:-.03em">One financial view.</div>'
             f'<div style="font-size:24px;color:#9DB5B3;margin-top:10px">The global financial operating system.</div></div>')
    return _social_base(w, h, 'dark', 'convergence', inner, 'br', 0).replace(f'{lockup(0, "dark")}', '')

def sm_youtube(w=1280, h=720):
    inner = (f'<div style="position:absolute;left:70px;top:90px;width:640px"><div style="display:inline-block;padding:10px 18px;border-radius:30px;background:#14B8A6;color:#022329;font-size:22px;font-weight:600">PRODUCT TOUR · 6 MIN</div>'
             f'<div style="font-size:84px;line-height:1.0;letter-spacing:-.035em;font-weight:600;margin-top:26px">Month-end close in one view</div></div>'
             f'<div style="position:absolute;right:-40px;top:120px;width:620px;height:480px;border-radius:18px;overflow:hidden;box-shadow:0 30px 70px rgba(0,0,0,.45)"><div style="transform:scale(.6);transform-origin:0 0">{C.dashboard("dark")}</div></div>')
    return _social_base(w, h, 'dark', 'field', inner, 'bl', 34)

def sm_avatar(w=800, h=800, theme='dark'):
    bg = 'linear-gradient(160deg,#0E3D42,#022329)' if theme == 'dark' else '#F3F5F2'
    ic = 'WFS_Icon_Premium' if theme == 'dark' else 'WFS_Icon_Primary'
    return (f'<div style="width:{w}px;height:{h}px;background:{bg};position:relative;overflow:hidden"><div style="position:absolute;inset:0;background:radial-gradient(closest-side,rgba(20,184,166,.28),rgba(20,184,166,0))"></div>'
            f'<img src="{A}/icon/svg/{ic}.svg" style="position:absolute;left:{w*0.2:.0f}px;top:{h*0.2:.0f}px;width:{w*0.6:.0f}px"></div>')

SOCIAL = [
    ('Instagram / LinkedIn post · quote', 'WFS_Social_Post_Quote_1080x1080', 1080, 1080, lambda: sm_quote()),
    ('Instagram / LinkedIn post · statistic', 'WFS_Social_Post_Stat_1080x1080', 1080, 1080, lambda: sm_stat()),
    ('Carousel slide 1', 'WFS_Social_Carousel_1_1080x1350', 1080, 1350, lambda: sm_carousel(0)),
    ('Carousel slide 2', 'WFS_Social_Carousel_2_1080x1350', 1080, 1350, lambda: sm_carousel(1)),
    ('Carousel slide 3', 'WFS_Social_Carousel_3_1080x1350', 1080, 1350, lambda: sm_carousel(2)),
    ('Carousel slide 4', 'WFS_Social_Carousel_4_1080x1350', 1080, 1350, lambda: sm_carousel(3)),
    ('Story / Reel cover', 'WFS_Social_Story_1080x1920', 1080, 1920, lambda: sm_story()),
    ('LinkedIn link post', 'WFS_Social_LinkedIn_Post_1200x627', 1200, 627, lambda: sm_linkedin()),
    ('X header', 'WFS_Social_X_Header_1500x500', 1500, 500, lambda: sm_x_header()),
    ('YouTube thumbnail', 'WFS_Social_YouTube_Thumbnail_1280x720', 1280, 720, lambda: sm_youtube()),
    ('Profile avatar · dark', 'WFS_Social_Avatar_Dark_800x800', 800, 800, lambda: sm_avatar()),
    ('Profile avatar · light', 'WFS_Social_Avatar_Light_800x800', 800, 800, lambda: sm_avatar(theme='light')),
]
