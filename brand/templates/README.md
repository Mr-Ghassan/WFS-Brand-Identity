# WFS templates — v1.0

HTML templates built from the brand components; each has a rendered PDF and PNG previews.
Edit text directly in the HTML (fonts load from Google Fonts; Arabic from your Adobe Fonts kit), then print to PDF from Chromium or re-render with `node ../source/render.mjs <file.html> <out.pdf> --width … --height …`.

| Folder | Template | Format |
|---|---|---|
| presentation | WFS_Presentation_Template | 1920 × 1080 (16:9), title + content |
| report | WFS_Report_Template | A4 portrait, cover + statement page |
| social | WFS_Social_Launch_1080 · WFS_Social_Announcement_1200x1500 · WFS_Social_Cover_1584x396 | 1:1 · 4:5 · 4:1 |
| email-signature | WFS_Email_Signature | HTML table |

The sample figures, names ("Northwind Group", "Leila Haddad") and addresses (`*.example`) are fictional placeholders.
