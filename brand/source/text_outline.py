"""Convert text to vector outlines (SVG path data) with real shaping.
Uses HarfBuzz (kerning, features, Arabic joining/RTL) and the font's own outlines."""
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

class Font:
    def __init__(self, path):
        self.file = path
        self.tt = TTFont(path)
        self.gs = self.tt.getGlyphSet()
        self.upm = self.tt['head'].unitsPerEm
        os2 = self.tt['OS/2']
        self.cap = getattr(os2, 'sCapHeight', 0) or int(self.upm * 0.7)
        self.xh = getattr(os2, 'sxHeight', 0) or int(self.upm * 0.5)
        blob = hb.Blob.from_file_path(path)
        self.hbfont = hb.Font(hb.Face(blob))
        self.order = self.tt.getGlyphOrder()

    def path(self, text, size, x=0.0, y=0.0, tracking=0.0, features=None, direction=None, script=None, lang=None):
        """Return (svg_d, advance) for `text` with baseline at y, starting at x.
        size = font size in output units; tracking in em."""
        buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties()
        if direction: buf.direction = direction
        if script: buf.script = script
        if lang: buf.language = lang
        hb.shape(self.hbfont, buf, features or {'kern': True, 'liga': True})
        s = size / self.upm
        pen = SVGPathPen(self.gs, ntos=lambda v: f'{v:.2f}'.rstrip('0').rstrip('.'))
        cx = 0.0
        n = len(buf.glyph_infos)
        for k, (info, pos) in enumerate(zip(buf.glyph_infos, buf.glyph_positions)):
            name = self.order[info.codepoint]
            tp = TransformPen(pen, (s, 0, 0, -s, x + (cx + pos.x_offset) * s, y - pos.y_offset * s))
            self.gs[name].draw(tp)
            cx += pos.x_advance + (tracking * self.upm if k < n - 1 else 0)
        return pen.getCommands(), cx * s

    def cap_height(self, size): return self.cap * size / self.upm
