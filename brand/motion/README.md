# WFS motion — v1.0

`WFS_Logo_Reveal.html` is a dependency-free reference prototype (inline SVG + CSS keyframes). Open it in any modern browser.

| Token | Value | Use |
|---|---|---|
| `--wfs-ease-standard` | `cubic-bezier(0.2, 0, 0, 1)` | UI transitions, panels, charts |
| `--wfs-ease-converge` | `cubic-bezier(0.65, 0, 0.35, 1)` | Logo formation, field convergence |
| `--wfs-ease-lock` | `cubic-bezier(0.3, 1.2, 0.4, 1)` (≤ 4 % overshoot) | The lock moment only |
| Durations | 120 · 200 · 320 ms (UI) · 1 100 ms (logo reveal) | Never exceed 1.4 s |

Sequence: **Fields** (0 ms) → **Converge** (0–760 ms, blades travel inward and unwind 90°, 40 ms stagger) → **Lock** (760–1 100 ms, 0.965 → 1.0 settle) → **One view** (wordmark enters 780–1 200 ms).
Loading state: the one-colour icon rotates 360° every 2.4 s, linear. `prefers-reduced-motion`: cross-fade only.
