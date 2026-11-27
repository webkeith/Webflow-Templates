# Block library — Client-First sections for Webflow

A Relume-style library: browse blocks by category or template, preview them at desktop, tablet and mobile widths, and paste them into the Webflow Designer.

**Templates in this version**

| Template | Blocks | Source |
|---|---|---|
| SaaS / B2B services (`saas-b2b`) | Global + 21 | Section patterns from 3rddegreescreening.com (homepage and Small Business page), rebuilt as a neutral wireframe with placeholder copy and library images. See `templates/saas-b2b/ANALYSIS.md`. |
| Come See Why — Light at dusk (`csw-redesign`) | Global + 11 | The csw-redesign homepage, with its live copy preserved. |
| Come See Why — Client-First refactor (`csw-client-first`) | Global + 11 | The current homepage layout restructured to Client-First. |

Categories: Navbar, Hero Header, How It Works, Feature, Stats, Layout, Signup Form, Logo List, Testimonial, Pricing, Blog, Contact, CTA, Footer.

## Version control

See **[GIT_GUIDE.md](GIT_GUIDE.md)** for the first commit, pushing to GitHub, the daily workflow, branches, releases, and optional hosting on GitHub Pages. Changes are listed in **[CHANGELOG.md](CHANGELOG.md)**.

## Run

```bash
unzip block-library.zip && cd block-library
npx serve dist
```

Open http://localhost:3000 in **Chrome or Edge**, or double-click `dist/index.html`. Copying is blocked inside preview panes, and in Safari and Firefox.

## Images

The library has one shared image system, `images.json` plus the `images/` folder:

- **`placeholder`** is a neutral image (PNG, WebP and SVG) that works at any aspect ratio. Every image slot falls back to it.
- **Eight photo slots:** `hero-team`, `feature-laptop`, `meeting-conversation`, `portrait-support`, `mobile-hand`, `landscape-dusk`, `architecture`, `workspace-flatlay`. Each has an intended use, an aspect ratio, alt text and a photorealistic generation prompt. The saas-b2b blocks already point at these keys: the header uses `hero-team`, blog cards use `workspace-flatlay` / `architecture` / `landscape-dusk`, and so on. Until a photo exists, its slot shows the placeholder.

**The eight photos are generated** in the Figma file [Block library images](https://www.figma.com/design/pwSvLlltqsaba96s3F3T8v/Block-library-images). Each frame is named after its slot and already has a JPG export setting.

**To add them to the library:**
1. In Figma, select all eight frames (Cmd/Ctrl + A on the page). In the right panel, click **Export 8 layers**. The files come out as `hero-team.jpg`, `feature-laptop.jpg` and so on.
2. Put the exported files in `images/` and run `python3 build.py`. The library swaps the placeholder for each photo automatically.

**To add more photos later:** save them into `images/` using the file names in `images.json`, then run `python3 build.py`.

**To use them in Webflow:**
1. Upload the files from `dist/images` to your Webflow Assets.
2. Open **Images** in the library sidebar and paste each asset's URL into its slot. The URLs are saved in your browser.
3. Every block you copy afterwards uses your hosted images. If a slot has no URL, it uses the placeholder's URL. If that's empty too, the block points at the local file, and the library warns you when you copy it.

The two csw templates use their existing Webflow CDN images and aren't affected.

## Pasting

1. **Add the fonts.** In Site Settings → Fonts, add the template's fonts: Inter for saas-b2b; Fraunces and Work Sans for csw-redesign.
2. **Paste Global styles first.** Select Body and paste the template's **Global styles** block, once per project.
3. **Paste the navbar.** Select `global-styles`, then paste.
4. **Paste sections.** Select `main-wrapper` and paste the first section, then select each section and paste the next one after it.
5. **Paste the footer.** Select `main-wrapper`, then paste.

## The paste format is still unverified

The earlier csw blocks didn't paste for you, and I haven't seen the result of the Paste checks yet. These blocks use the same format, with the fixes from last round. Before using the library for real work:

1. Click **Copy to Webflow** on any block, then paste into the **Paste checks** box (in the sidebar under Help). It should report "OK — Webflow data found".
2. If it does, paste T1–T9 into an empty Webflow page and tell me which ones appear. Each test isolates one element type. The answer tells me exactly which part of the format to fix, and the fix lands in `engine/webflow.py` for every block at once.

## Template conventions

- **One Client-First system per template.** Utility classes (`button`, `heading-style-h2`, `padding-section-large` …) differ between templates. Don't mix two templates in one Webflow project: whichever pastes first owns the shared class names, and Webflow may create `button 2` copies. The next step toward a full Relume-style library is one shared core with per-project themes (see "Roadmap").
- **Numbered component names** (`header1_`, `pricing1_`, …) keep blocks independent, so a future `pricing2` won't collide with `pricing1`.
- **Images in saas-b2b** are real Image elements bound to the shared registry, so you can swap the file in Webflow and keep the component class. For a Background Video in `header1`, replace `header1_background-media` and keep the overlay.
- **Forms in saas-b2b** (`signup1`, `contact1`) are HTML embeds, which preview and publish exactly as designed but don't send submissions to Webflow. To capture submissions, add a native Form Block, give its elements the same classes (`form_input`, `form_label`, `form_field-grid`, `form_button`), and delete the embed. The form styles live in the global embed, so they keep working on native form elements.
- **Navbars** use Div/Link blocks plus a small script embed for the dropdowns (keyboard, `aria-expanded`, Escape). It runs in preview and on the published site, not on the Designer canvas.
- **Classic interactions** follow the structure Webflow publishes (ids `e-N`/`a-N`, full class chains in targets, every trigger and target inside the copied block). See "Interactions" below.
- **Logo marquee** (`logo1`) is pure CSS in the global embed. It pauses on hover and stops under reduced motion.

## Combo classes

Every class after the first is pasted as a combo (`comb: "&"`) nested under the class before it, matching Webflow's model of one base class plus combos. Each combo carries:
- the compound rules it has with any earlier class (`.a.c` and `.b.c` both apply to `class="a b c"`)
- its standalone rules, but only where they won the original CSS cascade, so the element looks the same as the source

Paste check **T12** covers two- and three-class chains and a stacked utility.

## Interactions

| Trigger | Status |
|---|---|
| Hover (mouse over / out) | Generated; verified on Webflow's IX2 runtime |
| Click (first / second click) | Generated; verified on Webflow's IX2 runtime |
| Scroll into view (with initial state) | Generated; verified on Webflow's IX2 runtime |
| Page load, page scroll | Not supported: Webflow doesn't add page triggers on paste (Webflow help, "Copy and paste between sites"). Use a CSS animation in the global embed instead. |
| While scrolling, mouse move | Not generated until a calibrated Designer sample confirms the format |

Declare interactions per block in `meta.json` under `ix`:

```json
{"type": "hover", "trigger": "card", "in": [{"type": "scale", "target": "card_image", "value": 1.04, "duration": 400, "easing": "ease"}], "out": [...]}
{"type": "click", "trigger": "faq_question", "initial": [...], "first": [...], "second": [...]}
{"type": "scroll-into-view", "trigger": "section_x", "initial": [...], "animate": [...], "offset": 10}
```

- **Step types:** `opacity`, `move` (`x`/`y`, `unit`), `scale`, `rotate`, `size` (`value` 0 or `"auto"`).
- **Step options:** `duration`, `delay` and `easing`.
- **Validation:** the build fails if any trigger or target doesn't resolve inside the block.

Never rely on CSS to hide content that only an interaction reveals. Start states are set by the interaction, so if it's missing the content stays visible. CSS hover effects on interaction targets are kept behind `html:not(.w-mod-ix)` as a fallback.

**In Webflow:**
- Switch the Interactions panel to **Classic** to see pasted interactions.
- Run **Paste checks → step 3 (calibrate)** once by copying a real element with a Classic hover interaction. The library adapts how it references elements to match, and you can download the sample to send back.

## Dashboard UI

The library page is built from `ui/template.html`, `ui/dashboard.css` and `ui/dashboard.js`, which `build.py` inlines into `dist/index.html`. Block rows, image rows and sidebar items are generated by small functions in `build.py` (`block_markup`, `image_row`, `side_item`). Change the look in the CSS and the behaviour in the JS, then rebuild.

## Adding a template

1. Create `templates/<slug>/` with `index.html`, `style.css`, `meta.json` and an optional `nav.js`.
2. In `meta.json`, list each block's `key`, CSS `selector`, `name`, `category`, `desc`, and optionally `"nav": true` or `"ix": [{"type": "hover-zoom", "trigger": "...", "image": "..."}]`.
3. Mark any element that should paste as raw HTML (forms, complex widgets) with a `data-wf-embed` attribute.
4. Add the slug to `TEMPLATE_ORDER` in `build.py`, then:

```bash
pip install -r requirements.txt
python3 build.py
```

The engine handles the CSS conversion automatically:
- Single-class and combo rules, `:hover`, and the 991/767/479 breakpoints become native Webflow styles.
- Shorthands are expanded and CSS variables are resolved.
- Everything else goes into the template's global embed: tag selectors, descendant selectors, pseudo-elements, `!important`, keyframes, JavaScript state classes, classes used only inside embeds, and reduced-motion / hover media queries.

## Roadmap (Relume-style)

1. **Confirm the paste format** with the T1–T9 results.
2. **Shared core:** one Client-First utility set plus theme tokens, so blocks from any template can mix in one project.
3. **More variants per category** (header1–header10, …) generated from the same core.
4. **Page builder:** a sitemap and wireframe planner that assembles chosen blocks into a page and copies the whole page at once.
