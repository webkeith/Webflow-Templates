# Changelog

## v1.1.0 — 2026-11-27
- Added six SaaS / B2B blocks from the Small Business page: `header2`, `feature4`, `stats1`, `process2` (with scroll reveal), `layout3`, `signup2`. Added a new **Stats** category.
- The default placeholder is now `placeholder.svg`; PNG and WebP copies are kept.
- Combo classes now paste as proper chains (base class, then each combo nested under the previous one), so every class shows in the Style Selector.
- Classic interactions use Webflow's id format (`e-N`, `a-N`) and full class chains, and are validated at build time.
- Paste checks: added T10 (click), T11 (scroll into view) and T12 (multi-class combos), plus an interaction calibration step.
- Redesigned the dashboard: calm botanical UI, separate views, true-width scaled previews.
- Added `GIT_GUIDE.md`, `.gitignore`, `requirements.txt` and a GitHub Pages workflow.

## v1.0.0
- Block library engine, three templates (saas-b2b, csw-redesign, csw-client-first), image registry with Figma-generated photos, Images panel.
