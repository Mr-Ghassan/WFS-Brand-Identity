# WFS templates — v1.0

HTML templates built from the brand components; each has a rendered PDF and PNG previews.
Edit text directly in the HTML (fonts load from Google Fonts; Arabic from your Adobe Fonts kit), then print to PDF from Chromium or re-render with `node ../source/render.mjs <file.html> <out.pdf> --width … --height …`.

| Folder | Template | Format |
|---|---|---|
| presentation | WFS_Presentation_Template | 1920 × 1080 (16:9), title + content |
| report | WFS_Report_Template | A4 portrait, cover + statement page |
| social | posts (quote, statistic, launch) 1:1 · carousel ×4 4:5 · announcement 4:5 · story 9:16 · LinkedIn post · LinkedIn cover · X header · YouTube thumbnail · avatars | see file names |
| email | WFS_Email_Notification_720 | transactional email |
| email-signature | WFS_Email_Signature | HTML table |

The sample figures, names ("Northwind Group", "Leila Haddad") and addresses (`*.example`) are fictional placeholders.
