import json, html as H, sys
from pathlib import Path
from bs4 import BeautifulSoup, Tag
sys.path.insert(0, str(Path(__file__).parent / 'engine'))
from webflow import Template, Builder, IX, build_block, build_global, validate_ix

ROOT = Path(__file__).parent
DIST = ROOT / 'dist'
(DIST / 'json').mkdir(parents=True, exist_ok=True)

TEMPLATE_ORDER = ['saas-b2b', 'csw-redesign', 'csw-client-first']
CATEGORY_ORDER = ['Navbar', 'Hero Header', 'How It Works', 'Feature', 'Stats', 'Layout', 'Signup Form', 'Logo List', 'Testimonial', 'Pricing', 'Blog', 'Contact', 'CTA', 'Footer']

import shutil, re as _re
REGISTRY = json.loads((ROOT / 'images.json').read_text())
(DIST / 'images').mkdir(parents=True, exist_ok=True)
for key, img in REGISTRY.items():
    f = ROOT / 'images' / img['file']
    img['ready'] = f.exists()
    if img['ready']:
        shutil.copy(f, DIST / 'images' / img['file'])
for extra in ('placeholder.svg', 'placeholder.webp'):
    if (ROOT / 'images' / extra).exists():
        shutil.copy(ROOT / 'images' / extra, DIST / 'images' / extra)

def local_path(key):
    img = REGISTRY.get(key) or REGISTRY['placeholder']
    return 'images/' + (img['file'] if img.get('ready') else REGISTRY['placeholder']['file'])

def resolve_local(html):
    return _re.sub(r'lib-image:([\w-]+)', lambda m: local_path(m.group(1)), html)

templates, blocks = [], []
for slug in TEMPLATE_ORDER:
    tpl = Template(ROOT / 'templates' / slug)
    templates.append(tpl)
    g = build_global(tpl)
    gid = f'{slug}-global'
    (DIST / 'json' / f'{gid}.json').write_text(json.dumps(g, ensure_ascii=False))
    blocks.append({'id': gid, 'tpl': tpl, 'name': 'Global styles + page structure', 'category': 'Global', 'desc': f"Paste first, once per project. page-wrapper > global-styles embed (fonts: {tpl.meta.get('font_names', '')}, custom CSS Webflow can't style natively) + main-wrapper.", 'html': None, 'json': g, 'json_plain': None, 'ix_docs': []})
    for meta in tpl.meta['blocks']:
        r = build_block(tpl, meta)
        bid = f"{slug}-{meta['key']}"
        (DIST / 'json' / f'{bid}.json').write_text(json.dumps(r['json'], ensure_ascii=False))
        blocks.append({'id': bid, 'tpl': tpl, **meta, **r})

def js_safe(obj):
    return json.dumps(obj, ensure_ascii=False).replace('</', '<\\/')

def preview_doc(b):
    tpl = b['tpl']
    sprite = tpl.soup.find('svg')
    css = tpl.css_text
    fonts = tpl.meta.get('fonts', '')
    if b['html'] is None:
        body = '<div style="font:15px/1.6 system-ui;padding:1.25rem 1.5rem;color:#333">No visual output. Adds <code>page-wrapper</code> &gt; <code>global-styles</code> (embed) + <code>main-wrapper</code>.</div>'
    else:
        body = (str(sprite) if sprite else '') + '<div class="page-wrapper">' + resolve_local(b['html']) + '</div>'
        if b.get('nav'):
            body += '<div style="height:22rem"></div>' + tpl.nav_script
    return ('<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            + (f'<link rel="stylesheet" href="{fonts}">' if fonts else '')
            + f'<style>{css}</style><base target="_blank"></head><body>{body}</body></html>')

TEST_CSS = """
.t-pad { padding: 3rem; }
.t-button.is-dark { background-color: #3b634d; }
.t-button.is-large { font-size: 1.25rem; padding: 1rem 1.5rem; }
.t-panel { overflow: hidden; }
.t-box { padding: 1.5rem; background-color: #f3e4cb; color: #142238; }
.t-box.is-dark { background-color: #142238; color: #ffffff; }
.t-box.is-dark:hover { background-color: #3b634d; }
.t-button { display: inline-block; padding: 0.5rem 1rem; background-color: #142238; color: #ffffff; text-decoration: none; }
.t-image { width: 12rem; height: auto; }
.t-icon { display: flex; width: 2rem; height: 2rem; }
@media screen and (max-width: 767px) { .t-box { background-color: #edf0ea; } }
"""
TEST_IMG = 'https://cdn.prod.website-files.com/699d0d5e19379cf37d6d6f80/6a85ba5e7c26a3b73f0ccc2d_hero-bg.png'
TEST_HTML = '<svg><symbol id="i-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M13 18l6-6M13 6l6 6"/></symbol></svg>'
test_tpl = Template(css=TEST_CSS, html=TEST_HTML + '<div class="t-box is-dark"></div><a class="t-button is-dark is-large"></a>')

def test_payload(markup, ix=False):
    frag = BeautifulSoup(markup, 'html.parser')
    el = next(c for c in frag.children if isinstance(c, Tag))
    b = Builder(test_tpl)
    rid = b.conv(el)
    data = b.payload([rid])
    if ix:
        x = IX(b, 'paste-test-' + ix['type'])
        x.add(ix, 'Paste test / ' + ix['type'])
        data['payload']['ix2'] = x.data()
        errs = validate_ix(data['payload'])
        if errs:
            raise ValueError(errs)
    return data

TESTS = [
    ('t1', 'Div + text', test_payload('<div class="t-box">Test 1 — div with text</div>')),
    ('t2', 'Heading, paragraph, text link, button', test_payload('<div class="t-box"><h2>Test 2</h2><p>Paragraph text.</p><a href="#">Text link</a> <a href="#" class="t-button">Button</a></div>')),
    ('t3', 'Combo class + hover + mobile style', test_payload('<div class="t-box is-dark">Test 3 — combo is-dark, hover turns green</div>')),
    ('t4', 'Section element', test_payload('<section class="t-box">Test 4 — section tag</section>')),
    ('t5', 'List', test_payload('<ul class="t-box"><li>Test 5 — item one</li><li>Item two</li></ul>')),
    ('t6', 'HTML embed (SVG icon)', test_payload('<div class="t-box"><span class="t-icon"><svg viewBox="0 0 24 24"><use href="#i-arrow"/></svg></span></div>')),
    ('t7', 'Image by URL', test_payload(f'<div class="t-box"><img class="t-image" src="{TEST_IMG}" alt="Test image"></div>')),
    ('t8', 'Embedded HTML form', test_payload('<div class="t-box" data-wf-embed><form><label for="t8">Email</label><input id="t8" type="email"><button type="submit">Send</button></form></div>')),
    ('t9', 'Classic interaction — hover (mouse over/out)', test_payload('<div class="t-box"><div class="t-label">Test 9 — hover me: text scales up</div></div>', ix={'type': 'hover-zoom', 'trigger': 't-box', 'image': 't-label'})),
    ('t10', 'Classic interaction — click (first/second click)', test_payload('<div class="t-box"><p class="t-label">Test 10 — click this box</p><div class="t-panel"><p>This panel collapses on the first click and opens again on the second.</p></div></div>', ix={'type': 'click', 'trigger': 't-box', 'first': [{'type': 'size', 'target': 't-panel', 'value': 0, 'duration': 300, 'easing': 'outQuart'}, {'type': 'opacity', 'target': 't-panel', 'value': 0, 'duration': 200}], 'second': [{'type': 'size', 'target': 't-panel', 'value': 'auto', 'duration': 300, 'easing': 'outQuart'}, {'type': 'opacity', 'target': 't-panel', 'value': 1, 'duration': 200}]})),
    ('t11', 'Classic interaction — scroll into view', test_payload('<div class="t-box"><p class="t-label">Test 11 — fades up when scrolled into view</p></div>', ix={'type': 'scroll-into-view', 'trigger': 't-box', 'initial': [{'type': 'opacity', 'target': 't-label', 'value': 0}, {'type': 'move', 'target': 't-label', 'y': 20}], 'animate': [{'type': 'opacity', 'target': 't-label', 'value': 1, 'duration': 600, 'easing': 'outQuart'}, {'type': 'move', 'target': 't-label', 'y': 0, 'duration': 600, 'easing': 'outQuart'}]})),
    ('t12', 'Combo classes — 2 and 3 classes, stacked utility', test_payload('<div class="t-box t-pad"><a href="#" class="t-button is-dark">Two classes</a> <a href="#" class="t-button is-dark is-large">Three classes</a></div>')),
]

cats_present = [c for c in ['Global'] + CATEGORY_ORDER if any(b['category'] == c for b in blocks)]
UI = ROOT / 'ui'
LEAF = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 19c0-8 5-14 14-14 0 9-6 14-14 14z"/><path d="M5 19l8-8"/></svg>'
COPY_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15V6a2 2 0 0 1 2-2h9"/></svg>'

def block_markup(b):
    k, p = b['id'], b['json']['payload']
    classes = sorted({s['name'] for s in p['styles'] if not s['comb']})
    more = []
    if b['json_plain']:
        more.append(f'<button type="button" class="link-btn" data-copy="wfp-{k}">Copy without interactions</button>')
    if b['html']:
        more.append(f'<button type="button" class="link-btn" data-copy-html="html-{k}">Copy HTML</button>')
    more.append(f'<a class="link-btn" href="json/{k}.json" download>Download JSON</a>')
    ix = ''
    if b['ix_docs']:
        rows = ''.join(f'<li><strong>{H.escape(n)}</strong> — {H.escape(t)}. {H.escape(d)}</li>' for n, t, d in b['ix_docs'])
        kinds = sorted({t.split(' on ')[0].split(' of ')[0] for _, t, _ in b['ix_docs']})
        ix = f'<details><summary><span class="badge">{H.escape(", ".join(kinds))} interaction</span></summary><ul class="ix_list">{rows}</ul></details>'
    if b.get('ix_unsupported'):
        ix += ''.join(f'<p class="block_warn">Not included: {H.escape(u)}</p>' for u in b['ix_unsupported'])
    if b['html'] is None:
        preview = '<div class="preview"><p class="preview_empty">No visual output. Adds <code>page-wrapper</code> &gt; <code>global-styles</code> (embed) + <code>main-wrapper</code>.</p></div>'
    else:
        preview = f'''<div class="preview">
          <div class="preview_bar"><div class="segmented" role="group" aria-label="Preview width" data-vp-control>
            <button type="button" class="segmented_btn" data-vp="desktop" aria-pressed="true">Desktop</button>
            <button type="button" class="segmented_btn" data-vp="tablet" aria-pressed="false">Tablet</button>
            <button type="button" class="segmented_btn" data-vp="mobile" aria-pressed="false">Mobile</button>
          </div></div>
          <div class="preview_stage" data-vp="desktop"><iframe class="preview_frame" title="{H.escape(b['name'])} preview" data-preview="pv-{k}" tabindex="-1"></iframe></div>
        </div>'''
    n_ix = len(p['ix2']['events'])
    stats = f'{len(p["nodes"])} elements · {len(classes)} classes' + (f' · {n_ix} interaction triggers' if n_ix else '')
    return f'''
      <article class="block" id="c-{k}" data-cat="{H.escape(b['category'])}" data-tpl-slug="{b['tpl'].meta['slug']}" aria-labelledby="t-{k}">
        <div class="block_top">
          <div>
            <p class="block_eyebrow">{H.escape(b['category'])} · {H.escape(b['tpl'].meta['name'])}</p>
            <h2 class="block_title" id="t-{k}">{H.escape(b['name'])}</h2>
            <p class="block_desc">{H.escape(b.get('desc', ''))}</p>
          </div>
          <div class="block_actions">
            <button type="button" class="btn" data-copy="wf-{k}">{COPY_ICON}Copy to Webflow</button>
            <div class="block_more">{''.join(more)}</div>
          </div>
        </div>
        {preview}
        <div class="block_foot">
          {ix}
          <details><summary>{stats}</summary><p class="block_classes">{' '.join(f'<code>{H.escape(c)}</code>' for c in classes)}</p></details>
        </div>
      </article>'''

scripts = []
for b in blocks:
    k = b['id']
    scripts.append(f'<script type="application/json" id="wf-{k}">{js_safe(b["json"])}</script>')
    if b['html'] is not None:
        scripts.append(f'<script type="application/json" id="pv-{k}">{js_safe(preview_doc(b))}</script>')
        scripts.append(f'<script type="application/json" id="html-{k}">{js_safe(b["html"])}</script>')
    if b['json_plain']:
        scripts.append(f'<script type="application/json" id="wfp-{k}">{js_safe(b["json_plain"])}</script>')
for k, _, d in TESTS:
    scripts.append(f'<script type="application/json" id="wft-{k}">{js_safe(d)}</script>')
    (DIST / 'json' / f'paste-test-{k}.json').write_text(json.dumps(d))
availability = {k: ('images/' + v['file'] if v.get('ready') else 'images/' + REGISTRY['placeholder']['file']) for k, v in REGISTRY.items()}
scripts.append(f'<script type="application/json" id="lib-avail">{js_safe(availability)}</script>')

def image_row(key, img):
    if key == 'placeholder':
        state, ok = 'Reusable placeholder', True
    elif img.get('ready'):
        state, ok = 'Photo ready', True
    elif img.get('figma'):
        state, ok = 'Generated in Figma — export to images/', False
    else:
        state, ok = 'Using placeholder until generated', False
    figma = f' · <a href="{img["figma"]}" target="_blank" rel="noopener">Open in Figma</a> ({img.get("size", "")})' if img.get('figma') else ''
    prompt = (f'<details class="prompt"><summary>Generation prompt</summary><p>{H.escape(img["prompt"])}</p>'
              f'<button type="button" class="link-btn" data-copy-text="{H.escape(img["prompt"])}">Copy prompt</button></details>') if img.get('prompt') else ''
    return f'''
        <li class="img_row">
          <img src="{local_path(key)}" alt="" class="img_thumb" loading="lazy">
          <div>
            <p class="img_head"><span class="img_key">{key}</span><code>{img["ratio"]}</code><span class="img_state{' is-ok' if ok else ''}">{state}</span></p>
            <p class="img_meta">{H.escape(img["use"])} · file <code>{img["file"]}</code>{figma}</p>
            <label class="field_label" for="url-{key}">Webflow asset URL</label>
            <input class="field" id="url-{key}" data-img-key="{key}" type="url" placeholder="https://cdn.prod.website-files.com/…/{img['file']}" autocomplete="off">
            {prompt}
          </div>
        </li>'''

def side_item(label, count, view, cat=''):
    count_html = f'<span class="side_count">{count}</span>' if count is not None else ''
    return f'<li><button type="button" class="side_item" data-view="{view}" data-cat="{H.escape(cat)}">{H.escape(label)}{count_html}</button></li>'

side_blocks = side_item('All blocks', len(blocks), 'blocks') + ''.join(side_item(c, sum(1 for b in blocks if b['category'] == c), 'blocks', c) for c in cats_present)
side_tools = (f'<li><button type="button" class="side_item" data-view="images">Images<span class="side_count" data-img-count></span></button></li>'
              + side_item('Paste checks', None, 'checks'))
tpl_buttons = '<button type="button" class="segmented_btn" data-tpl="" aria-pressed="true">All templates</button>' + ''.join(
    f'<button type="button" class="segmented_btn" data-tpl="{t.meta["slug"]}" aria-pressed="false">{H.escape(t.meta["name"])}</button>' for t in templates)
tpl_notes = ''.join(f'<li><strong>{H.escape(t.meta["name"])}</strong> — {H.escape(t.meta.get("source", ""))}. Fonts: {H.escape(t.meta.get("font_names", ""))}.</li>' for t in templates)
tests_html = ''.join(f'<li><button type="button" class="btn is-quiet" data-copy="wft-{k}">{k.upper()}</button><span>{H.escape(n)}</span><span class="test_result" data-result="wft-{k}"></span></li>' for k, n, _ in TESTS)

page = (UI / 'template.html').read_text()
for token, value in {
    '{{CSS}}': (UI / 'dashboard.css').read_text(),
    '{{JS}}': (UI / 'dashboard.js').read_text(),
    '{{LEAF}}': LEAF,
    '{{SIDE_BLOCKS}}': side_blocks,
    '{{SIDE_TOOLS}}': side_tools,
    '{{TPL_BUTTONS}}': tpl_buttons,
    '{{TPL_NOTES}}': tpl_notes,
    '{{BLOCKS}}': ''.join(block_markup(b) for b in blocks),
    '{{IMAGES}}': ''.join(image_row(k, v) for k, v in REGISTRY.items()),
    '{{TESTS}}': tests_html,
    '{{DATA}}': ''.join(scripts),
}.items():
    page = page.replace(token, value)
(DIST / 'index.html').write_text(page)

for b in blocks:
    p = b['json']['payload']
    print(f"{b['id']:28} nodes {len(p['nodes']):4} styles {len(p['styles']):3} ix {len(p['ix2']['events'])}")
print('library', len(page) // 1024, 'KB')
