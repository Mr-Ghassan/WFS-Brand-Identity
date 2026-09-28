# Adobe Illustrator (.ai) files

**No `.ai` files are shipped in this version, deliberately.**

A genuine native `.ai` file can only be written by Adobe Illustrator. Illustrator was not available in the environment that produced WFS Brand Identity 1.0, and no legitimate open-source tool writes native AI files. Renaming an SVG or PDF to `.ai` would be a fake file, so it was not done.

What is provided instead:

- **SVG masters** (`../svg/`) — clean, outlined, fully editable vector paths; open directly in Illustrator.
- **Vector PDFs** (`../pdf/`) — open in Illustrator as editable paths (no embedded rasters).

## Create native .ai files (one step, requires Illustrator)

1. Open Adobe Illustrator.
2. `File → Scripts → Other Script…` and choose `brand/source/illustrator/export_ai.jsx`.
3. Select the `brand` folder when prompted. The script opens every SVG master in `logo/svg`, `icon/svg` and `wordmark/svg` and saves a native, PDF-compatible `.ai` next to it in the matching `ai/` folder.
