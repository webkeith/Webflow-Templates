import json, re, uuid
from pathlib import Path
import tinycss2
from bs4 import BeautifulSoup, NavigableString, Tag

BREAKPOINTS = {'991': 'medium', '767': 'small', '479': 'tiny'}
EMBED_ONLY_PROPS = {'isolation', 'text-underline-offset', 'text-decoration-thickness', '-webkit-text-size-adjust',
                    'scroll-behavior', 'animation', 'animation-delay', 'animation-play-state', 'font-variation-settings',
                    '-webkit-font-smoothing', 'resize', 'color-scheme'}
UNITLESS = {'z-index', 'opacity', 'flex-grow', 'flex-shrink', 'order', 'font-weight', 'line-height', 'flex'}
SIMPLE = re.compile(r'^\.([\w-]+)(?:\.([\w-]+))?(:hover)?$')
IX_TIME = 1764115200000


def uid():
    return str(uuid.uuid4())


def split_top(value):
    parts, depth, cur = [], 0, ''
    for ch in value:
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
        if ch == ' ' and depth == 0:
            if cur:
                parts.append(cur)
            cur = ''
        else:
            cur += ch
    if cur:
        parts.append(cur)
    return parts


def split_commas(value):
    parts, depth, cur = [], 0, ''
    for ch in value:
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
        if ch == ',' and depth == 0:
            parts.append(cur.strip())
            cur = ''
        else:
            cur += ch
    parts.append(cur.strip())
    return parts


def four(vals):
    if len(vals) == 1:
        return vals * 4
    if len(vals) == 2:
        return [vals[0], vals[1], vals[0], vals[1]]
    if len(vals) == 3:
        return [vals[0], vals[1], vals[2], vals[1]]
    return vals[:4]


def to_ms(t):
    if t.endswith('ms'):
        return t
    if t.endswith('s'):
        return str(int(round(float(t[:-1]) * 1000))) + 'ms'
    return t


def expand(prop, val):
    p = prop.lower()
    if p in ('margin', 'padding'):
        t, r, b, l = four(split_top(val))
        return [(f'{p}-top', t), (f'{p}-right', r), (f'{p}-bottom', b), (f'{p}-left', l)]
    if p == 'inset':
        t, r, b, l = four(split_top(val))
        return [('top', t), ('right', r), ('bottom', b), ('left', l)]
    if p == 'gap':
        vals = split_top(val)
        return [('grid-row-gap', vals[0]), ('grid-column-gap', vals[1] if len(vals) > 1 else vals[0])]
    if p == 'border-radius':
        a, b, c, d = four(split_top(val))
        return [('border-top-left-radius', a), ('border-top-right-radius', b), ('border-bottom-right-radius', c), ('border-bottom-left-radius', d)]
    if p == 'border-width':
        t, r, b, l = four(split_top(val))
        return [('border-top-width', t), ('border-right-width', r), ('border-bottom-width', b), ('border-left-width', l)]
    if p in ('border', 'border-top', 'border-bottom', 'border-left', 'border-right'):
        sides = ['top', 'right', 'bottom', 'left'] if p == 'border' else [p.split('-')[1]]
        if val.strip() in ('0', 'none'):
            return [(f'border-{s}-style', 'none') for s in sides] + [(f'border-{s}-width', '0px') for s in sides]
        width, style, color = '1px', 'solid', 'currentColor'
        for part in split_top(val):
            if re.match(r'^[\d.]+(px|rem|em)?$', part):
                width = part
            elif part in ('solid', 'dashed', 'dotted', 'none', 'double'):
                style = part
            else:
                color = part
        out = []
        for s in sides:
            out += [(f'border-{s}-width', width), (f'border-{s}-style', style), (f'border-{s}-color', color)]
        return out
    if p == 'border-color':
        return [(f'border-{s}-color', val) for s in ['top', 'right', 'bottom', 'left']]
    if p == 'flex':
        v = val.strip()
        if v == 'none':
            return [('flex-grow', '0'), ('flex-shrink', '0'), ('flex-basis', 'auto')]
        if re.fullmatch(r'\d+', v):
            return [('flex-grow', v), ('flex-shrink', '1'), ('flex-basis', '0%')]
    if p == 'background':
        return [('background-color', 'transparent' if val.strip() == 'none' else val)]
    if p == 'transition':
        items = []
        for item in split_commas(val):
            bits = split_top(item)
            items.append(f'{bits[0]} {to_ms(bits[1]) if len(bits) > 1 else "200ms"} {bits[2] if len(bits) > 2 else "ease"} {to_ms(bits[3]) if len(bits) > 3 else "0ms"}')
        return [('transition', ', '.join(items))]
    return [(p, val)]


def norm(p, v):
    if p not in UNITLESS:
        v = ' '.join('0px' if t == '0' else t for t in split_top(v))
    return v


def style_less(decls):
    seen = {}
    for p, v in decls:
        seen[p] = norm(p, v)
    return ' '.join(f'{p}: {v};' for p, v in seen.items())


class Template:
    def __init__(self, folder=None, css=None, html=None, meta=None):
        if folder:
            folder = Path(folder)
            self.meta = json.loads((folder / 'meta.json').read_text())
            css = (folder / 'style.css').read_text()
            html = (folder / 'index.html').read_text()
            nav = folder / 'nav.js'
            self.nav_script = ('<script>\n' + nav.read_text() + '</script>') if nav.exists() else ''
        else:
            self.meta = meta or {'slug': 'test', 'name': 'Test', 'fonts': '', 'blocks': []}
            self.nav_script = ''
        self.css_text = css
        self.soup = BeautifulSoup(html, 'lxml')
        self.root_vars = {}
        for m in re.finditer(r':root\s*\{([^}]*)\}', css):
            for d in m.group(1).split(';'):
                if ':' in d and d.strip().startswith('--'):
                    k, v = d.split(':', 1)
                    self.root_vars[k.strip()] = v.strip()
        self.style_rules = {}
        self.decl_order = {}
        self._order = 0
        self.embed = {'main': [], 'medium': [], 'small': [], 'tiny': [], 'other': [], 'raw': []}
        self.symbols = {}
        for s in self.soup.find_all('symbol'):
            attrs = ' '.join(f'{k}="{v}"' for k, v in s.attrs.items() if k != 'id')
            self.symbols[s['id']] = f'<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" {attrs} aria-hidden="true">' + ''.join(str(c) for c in s.contents) + '</svg>'
        self.embed_only_classes = self._embed_only_classes()
        self._parse()
        self._route_unused_combos()
        self.ix_specs = {b['key']: b.get('ix', []) for b in self.meta.get('blocks', [])}
        self._apply_ix_overrides()

    def resolve(self, v):
        for _ in range(8):
            nv = re.sub(r'var\((--[\w-]+)(?:\s*,\s*([^)]+))?\)', lambda m: self.root_vars.get(m.group(1), m.group(2) or ''), v)
            if nv == v:
                break
            v = nv
        return v

    def _embed_only_classes(self):
        inside, outside = set(), set()
        for el in self.soup.find_all(class_=True):
            target = inside if el.find_parent(attrs={'data-wf-embed': True}) else outside
            target.update(el.get('class', []))
        return inside - outside

    def add_embed(self, bucket, selector, decls, media=None):
        body = '; '.join(f'{p}: {v}{" !important" if imp else ""}' for p, v, imp in decls)
        rule = f'{selector} {{ {body}; }}'
        if bucket == 'other':
            self.embed['other'].append((media, rule))
        else:
            self.embed[bucket].append(rule)

    def parse_decls(self, content):
        out = []
        for d in tinycss2.parse_blocks_contents(content, skip_whitespace=True, skip_comments=True):
            if d.type == 'declaration':
                out.append((d.lower_name, self.resolve(tinycss2.serialize(d.value).strip()), d.important))
        return out

    def handle_rule(self, prelude, content, bucket, media_text=None):
        selectors = [s.strip() for s in split_commas(tinycss2.serialize(prelude))]
        decls = self.parse_decls(content)
        for sel in selectors:
            m = SIMPLE.match(sel)
            if bucket == 'other' or not m or m.group(1) in self.embed_only_classes:
                self.add_embed(bucket, sel, decls, media_text)
                continue
            base, combo, hover = m.group(1), m.group(2), m.group(3)
            variant = bucket + ('_hover' if hover else '')
            keep, rest = [], []
            for p, v, imp in decls:
                if imp or p in EMBED_ONLY_PROPS or v.strip() == 'clip' or p.startswith('--'):
                    rest.append((p, v, imp))
                else:
                    keep.append((p, v))
            if rest:
                self.add_embed(bucket, sel, rest)
            lst = self.style_rules.setdefault((base, combo), {}).setdefault(variant, [])
            self._order += 1
            for p, v in keep:
                for ep, ev in expand(p, v):
                    lst.append((ep, ev))
                    if combo is None:
                        self.decl_order[(base, variant, ep)] = self._order

    def _parse(self):
        for rule in tinycss2.parse_stylesheet(self.css_text, skip_whitespace=True, skip_comments=True):
            if rule.type == 'qualified-rule':
                if tinycss2.serialize(rule.prelude).strip() == ':root':
                    continue
                self.handle_rule(rule.prelude, rule.content, 'main')
            elif rule.type == 'at-rule' and rule.lower_at_keyword == 'media':
                mt = tinycss2.serialize(rule.prelude).strip()
                bp = re.search(r'max-width:\s*(\d+)px', mt)
                bucket = BREAKPOINTS.get(bp.group(1)) if bp and 'screen' in mt else None
                for inner in tinycss2.parse_rule_list(rule.content, skip_whitespace=True, skip_comments=True):
                    if inner.type == 'qualified-rule':
                        self.handle_rule(inner.prelude, inner.content, bucket or 'other', mt)
            elif rule.type == 'at-rule' and rule.lower_at_keyword == 'keyframes':
                self.embed['raw'].append(self.resolve(tinycss2.serialize([rule])))

    def _route_unused_combos(self):
        used = set()
        for el in self.soup.find_all(class_=True):
            cl = el.get('class', [])
            for i, c in enumerate(cl):
                for earlier in cl[:i]:
                    used.add((earlier, c))
        for key in list(self.style_rules):
            base, combo = key
            if combo and key not in used:
                for variant, decls in self.style_rules.pop(key).items():
                    sel = f'.{base}.{combo}' + (':hover' if variant.endswith('_hover') else '')
                    self.add_embed(variant.replace('_hover', ''), sel, [(p, v, False) for p, v in decls])

    def _apply_ix_overrides(self):
        """Interactions animate inline styles, so CSS transitions/hover rules on the same targets would fight them.
        Move those rules behind html:not(.w-mod-ix): they still work as a fallback on pages where Webflow's
        interaction engine is not running (for example if a paste dropped the interaction data)."""
        triggers, targets = set(), set()
        for specs in self.ix_specs.values():
            for spec in specs:
                triggers.add(spec.get('trigger'))
                if spec['type'] == 'hover-zoom':
                    targets.add(spec['image'])
                for key in ('in', 'out', 'first', 'second', 'initial', 'animate'):
                    for step in spec.get(key, []):
                        targets.add(step['target'])
        for cls in targets:
            for variant, decls in self.style_rules.get((cls, None), {}).items():
                moved = [(p, v) for p, v in decls if p == 'transition']
                if moved and variant == 'main':
                    self.embed['main'].append(f'html:not(.w-mod-ix) .{cls} {{ ' + '; '.join(f'{p}: {v}' for p, v in moved) + '; }')
                decls[:] = [(p, v) for p, v in decls if p != 'transition']
        def guard(rule):
            for t in triggers:
                if t and rule.startswith(f'.{t}:hover ') and any(f' .{c} ' in rule or f' .{c}{{' in rule for c in targets):
                    return 'html:not(.w-mod-ix) ' + rule
            return rule
        self.embed['main'] = [guard(r) for r in self.embed['main']]

    def global_embed(self):
        out = [f"@import url('{self.meta['fonts']}');"] if self.meta.get('fonts') else []
        out += self.embed['raw']
        out += self.embed['main']
        for b, mw in (('medium', 991), ('small', 767), ('tiny', 479)):
            if self.embed[b]:
                out.append(f'@media screen and (max-width: {mw}px) {{ ' + ' '.join(self.embed[b]) + ' }')
        groups = {}
        for media, rule in self.embed['other']:
            groups.setdefault(media, []).append(rule)
        for media, rules in groups.items():
            out.append(f'@media {media} {{ ' + ' '.join(rules) + ' }')
        return '<style>\n' + '\n'.join(out) + '\n</style>'

    def svg_html(self, svg):
        use = svg.find('use')
        if use and use.get('href', '').lstrip('#') in self.symbols:
            return self.symbols[use['href'].lstrip('#')]
        return str(svg)


class Builder:
    def __init__(self, tpl):
        self.t = tpl
        self.nodes, self.styles, self.style_order = [], {}, []

    def _rules_for(self, chain):
        """Styles for the last class in a chain.

        Compound rules that pair it with any earlier class (.a.c, .b.c) always apply: they are more specific.
        Its standalone rules apply only where they win the original cascade: in Webflow a combo overrides its
        parent, but in the source CSS an equally specific earlier-declared class may have won. Losing
        declarations are dropped so the combo inherits the parent's value, exactly as the browser did."""
        name = chain[-1]
        own = self.t.style_rules.get((name, None), {})
        if len(chain) == 1:
            return own
        merged = {}
        for variant, decls in own.items():
            for p, v in decls:
                mine = self.t.decl_order.get((name, variant, p), 0)
                beaten = any(self.t.decl_order.get((e, variant, p), -1) > mine for e in chain[:-1])
                if not beaten:
                    merged.setdefault(variant, []).append((p, v))
        for earlier in chain[:-1]:
            for variant, decls in self.t.style_rules.get((earlier, name), {}).items():
                merged.setdefault(variant, []).extend(decls)
        return merged

    def chain_style(self, chain):
        chain = tuple(chain)
        if chain in self.styles:
            return self.styles[chain]['_id']
        if len(chain) > 1:
            self.chain_style(chain[:-1])
        main, variants = '', {}
        for var, decls in self._rules_for(chain).items():
            sl = style_less(decls)
            if var == 'main':
                main = sl
            else:
                variants[var] = {'styleLess': sl}
        st = {'_id': uid(), 'fake': False, 'type': 'class', 'name': chain[-1], 'namespace': '',
              'comb': '&' if len(chain) > 1 else '', 'styleLess': main, 'variants': variants, 'children': [],
              'createdBy': '', 'origin': None, 'selector': None}
        self.styles[chain] = st
        self.style_order.append(chain)
        if len(chain) > 1:
            self.styles[chain[:-1]]['children'].append(st['_id'])
        return st['_id']

    def style_id(self, base, combo=None):
        return self.chain_style((base,) if combo is None else (base, combo))

    def class_ids(self, classes):
        seen, chain = set(), []
        for c in classes:
            if c not in seen:
                seen.add(c)
                chain.append(c)
        return [self.chain_style(chain[:i + 1]) for i in range(len(chain))]

    def chain_ids_for(self, cls):
        for key in self.style_order:
            if key[-1] == cls:
                return [self.styles[key[:i + 1]]['_id'] for i in range(len(key))], key
        raise KeyError(cls)

    def add(self, node):
        self.nodes.append(node)
        return node['_id']

    def text(self, value):
        return self.add({'_id': uid(), 'text': True, 'v': value})

    def xattrs(self, el):
        skip = {'class', 'href', 'src', 'style', 'type', 'id', 'alt', 'width', 'height', 'loading', 'fetchpriority', 'data-wf-embed'}
        return [{'name': k, 'value': v if isinstance(v, str) else ' '.join(v)} for k, v in el.attrs.items() if k not in skip]

    def children(self, el):
        ids = []
        for c in el.children:
            if isinstance(c, NavigableString):
                t = re.sub(r'\s+', ' ', str(c))
                if t.strip():
                    ids.append(self.text(t.lstrip() if not ids else t))
            elif isinstance(c, Tag):
                nid = self.conv(c)
                if nid:
                    ids.append(nid)
        by = {n['_id']: n for n in self.nodes}
        merged = []
        for i in ids:
            if merged and by[i].get('text') and by[merged[-1]].get('text'):
                by[merged[-1]]['v'] = re.sub(r'\s+', ' ', by[merged[-1]]['v'] + by[i]['v'])
            else:
                merged.append(i)
        if merged and by[merged[-1]].get('text'):
            by[merged[-1]]['v'] = by[merged[-1]]['v'].rstrip()
        return merged

    def base_data(self, el, tag):
        data = {'tag': tag, 'attr': {'id': el.get('id', '')}}
        xa = self.xattrs(el)
        if xa:
            data['xattr'] = xa
        return data

    def embed(self, html, classes, xattr=None):
        data = {'embed': {'type': 'html', 'meta': {'html': html, 'div': False, 'script': '<script' in html, 'compilable': False, 'iframe': False}},
                'insideRTE': False, 'search': {'exclude': True}}
        if xattr:
            data['xattr'] = xattr
        return self.add({'_id': uid(), 'type': 'HtmlEmbed', 'tag': 'div', 'classes': self.class_ids(classes), 'children': [], 'data': data})

    def is_text_only(self, el):
        return all(isinstance(c, NavigableString) or (isinstance(c, Tag) and c.name == 'br') for c in el.children)

    def node(self, ntype, tag, el, data=None, text_children=True):
        nid = uid()
        n = {'_id': nid, 'type': ntype, 'tag': tag, 'classes': self.class_ids(el.get('class', [])), 'children': [], 'data': data or self.base_data(el, tag)}
        self.add(n)
        n['children'] = self.children(el)
        return nid

    def conv(self, el):
        name, classes = el.name, el.get('class', [])
        if name in ('script', 'style', 'symbol', 'defs', 'title', 'meta', 'link'):
            return None
        if el.has_attr('data-wf-embed'):
            return self.embed(el.decode_contents(), classes, self.xattrs(el))
        if name == 'br':
            return self.text(' ')
        if name == 'svg':
            return self.embed(self.t.svg_html(el), classes)
        if name == 'span' and el.find('svg') and not el.get_text(strip=True):
            return self.embed(self.t.svg_html(el.find('svg')), classes)
        if name == 'img':
            src = el.get('src', '')
            if src.startswith('lib-image:'):
                src = '__LIBIMG:' + src.split(':', 1)[1] + '__'
            attr = {'src': src, 'loading': el.get('loading', 'eager'), 'width': el.get('width', 'auto'),
                    'height': el.get('height', 'auto'), 'alt': el.get('alt', ''), 'id': ''}
            data = {'attr': attr, 'srcsetDisabled': False, 'sizes': []}
            xa = self.xattrs(el)
            if el.get('fetchpriority'):
                xa.append({'name': 'fetchpriority', 'value': el['fetchpriority']})
            if xa:
                data['xattr'] = xa
            return self.add({'_id': uid(), 'type': 'Image', 'tag': 'img', 'classes': self.class_ids(classes), 'children': [], 'data': data})
        if name == 'button':
            data = self.base_data(el, 'a')
            data['xattr'] = data.get('xattr', []) + [{'name': 'role', 'value': 'button'}]
            data['link'] = {'mode': 'external', 'url': '#'}
            data['block'] = 'block'
            data['button'] = False
            nid = uid()
            n = {'_id': nid, 'type': 'Link', 'tag': 'a', 'classes': self.class_ids(classes), 'children': [], 'data': data}
            self.add(n)
            n['children'] = self.wrap_loose_text(el)
            return nid
        if name == 'a':
            text_only = self.is_text_only(el)
            data = self.base_data(el, 'a')
            data['link'] = {'mode': 'external', 'url': el.get('href', '#')}
            data['button'] = bool(text_only and 'button' in classes)
            data['block'] = '' if text_only else 'block'
            nid = uid()
            n = {'_id': nid, 'type': 'Link', 'tag': 'a', 'classes': self.class_ids(classes), 'children': [], 'data': data}
            self.add(n)
            n['children'] = self.children(el) if text_only else self.wrap_loose_text(el)
            return nid
        if name in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            return self.node('Heading', name, el)
        if name == 'p':
            return self.node('Paragraph', 'p', el)
        if name in ('ul', 'ol'):
            return self.node('List', name, el)
        if name == 'li':
            return self.node('ListItem', 'li', el)
        if name in ('span', 'strong', 'em') and self.is_text_only(el) and el.parent and el.parent.name in ('p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a'):
            t = {'strong': 'Strong', 'em': 'Emphasized', 'span': 'Span'}[name]
            return self.node(t, name, el, data={'tag': name})
        tag = name if name in ('div', 'header', 'footer', 'nav', 'main', 'section', 'article', 'aside', 'figure', 'address') else 'div'
        data = self.base_data(el, tag)
        if self.is_text_only(el) and el.get_text(strip=True):
            data['text'] = True
        ntype = 'Block'
        if tag == 'section':
            ntype = 'Section'
            data['grid'] = {'type': 'section'}
        nid = uid()
        n = {'_id': nid, 'type': ntype, 'tag': tag, 'classes': self.class_ids(classes), 'children': [], 'data': data}
        self.add(n)
        n['children'] = self.children(el)
        return nid

    def wrap_loose_text(self, el):
        kids = []
        for c in el.children:
            if isinstance(c, NavigableString):
                t = re.sub(r'\s+', ' ', str(c)).strip()
                if t:
                    kids.append(self.add({'_id': uid(), 'type': 'Block', 'tag': 'div', 'classes': [], 'children': [self.text(t)], 'data': {'tag': 'div', 'text': True}}))
            elif isinstance(c, Tag):
                k = self.conv(c)
                if k:
                    kids.append(k)
        return kids

    def payload(self, root_ids, ix=None):
        by_id = {n['_id']: n for n in self.nodes}
        ordered = []

        def normalise(n):
            if n.get('text'):
                return {'_id': n['_id'], 'text': True, 'v': n['v']}
            d = n.setdefault('data', {})
            d.setdefault('devlink', {'runtimeProps': {}, 'slot': ''})
            d.setdefault('displayName', '')
            d.setdefault('attr', {})
            d['attr'].setdefault('id', '')
            d.setdefault('xattr', [])
            d.setdefault('search', {'exclude': n['type'] == 'HtmlEmbed'})
            d.setdefault('visibility', {'conditions': []})
            if n['type'] == 'Link':
                d.setdefault('button', False)
                d.setdefault('block', '')
            return n

        def walk(i):
            ordered.append(normalise(by_id[i]))
            for c in by_id[i].get('children', []):
                walk(c)

        for r in root_ids:
            walk(r)
        return {'type': '@webflow/XscpData',
                'payload': {'nodes': ordered, 'styles': [self.styles[k] for k in self.style_order], 'assets': [], 'ix1': [],
                            'ix2': ix or {'interactions': [], 'events': [], 'actionLists': []}},
                'meta': {'unlinkedSymbolCount': 0, 'droppedLinks': 0, 'dynBindRemovedCount': 0, 'dynListBindRemovedCount': 0,
                         'paginationRemovedCount': 0, 'universalBindingsRemovedCount': 0, 'codeComponentsRemovedCount': 0}}


import hashlib

EASINGS = {'', 'ease', 'easeIn', 'easeOut', 'easeInOut', 'outQuad', 'outCubic', 'outQuart', 'outQuint', 'outExpo', 'inOutQuart', 'outBack'}
ACTION_TYPES = {'opacity': 'STYLE_OPACITY', 'move': 'TRANSFORM_MOVE', 'scale': 'TRANSFORM_SCALE', 'rotate': 'TRANSFORM_ROTATE', 'size': 'STYLE_SIZE'}
SUPPORTED_TRIGGERS = {'hover', 'hover-zoom', 'click', 'scroll-into-view'}
UNSUPPORTED_TRIGGERS = {
    'page-load': 'Page triggers are not added to the site you paste into (Webflow help: Copy and paste between sites).',
    'page-scroll': 'Page triggers are not added to the site you paste into (Webflow help: Copy and paste between sites).',
    'while-scrolling': 'Continuous triggers need calibration against a real Designer copy before they can be generated safely.',
    'mouse-move': 'Continuous triggers need calibration against a real Designer copy before they can be generated safely.',
}


class IX:
    """Classic interactions (IX2) in the shape Webflow itself publishes.

    Ids follow Webflow's own pattern (events e-N, action lists a-N, items a-N-n, a-N-n-2 ...).
    Triggers and targets reference style ids of the full class chain (base + combos) and an
    element id that exists in the same payload, so nothing points at stale or foreign elements."""

    def __init__(self, b, seed):
        self.b = b
        base = int(hashlib.sha1(seed.encode()).hexdigest()[:8], 16) % 800000 + 100000
        self.next_event = base
        self.next_list = base
        self.events, self.lists = [], []

    def _eid(self):
        self.next_event += 1
        return f'e-{self.next_event}'

    def _lid(self):
        self.next_list += 1
        return f'a-{self.next_list}'

    def target(self, cls, scope='CHILDREN'):
        ids, chain = self.b.chain_ids_for(cls)
        t = {'selector': '.' + '.'.join(chain), 'selectorGuids': ids}
        if scope == 'CHILDREN':
            t = {'useEventTarget': 'CHILDREN', **t}
        return t

    def trigger(self, cls):
        ids, chain = self.b.chain_ids_for(cls)
        last = ids[-1]
        node = next(n for n in self.b.nodes if n.get('classes') and n['classes'][:len(ids)] == ids)
        return {'id': node['_id'], 'appliesTo': 'CLASS', 'styleBlockIds': ids}

    def item(self, lid, n, step):
        action = ACTION_TYPES[step['type']]
        easing = step.get('easing', 'ease')
        if easing not in EASINGS:
            raise ValueError(f'unsupported easing {easing}')
        c = {'delay': int(step.get('delay', 0)), 'easing': easing if step.get('duration', 0) else '',
             'duration': int(step.get('duration', 0)), 'target': self.target(step['target'], step.get('scope', 'CHILDREN'))}
        t = step['type']
        if t == 'opacity':
            c.update({'value': step['value'], 'unit': ''})
        elif t == 'scale':
            c.update({'xValue': step['value'], 'yValue': step['value'], 'locked': True})
        elif t == 'rotate':
            c.update({'zValue': step['value'], 'xUnit': 'DEG', 'yUnit': 'DEG', 'zUnit': 'deg'})
        elif t == 'move':
            c.update({'xValue': step.get('x'), 'yValue': step.get('y'), 'xUnit': step.get('unit', 'px') if step.get('x') is not None else 'PX',
                      'yUnit': step.get('unit', 'px') if step.get('y') is not None else 'PX', 'zUnit': 'PX'})
            c = {k: v for k, v in c.items() if v is not None}
        elif t == 'size':
            if step['value'] == 'auto':
                c.update({'widthUnit': 'PX', 'heightUnit': 'AUTO', 'locked': False})
            else:
                c.update({'heightValue': step['value'], 'widthUnit': 'PX', 'heightUnit': 'px', 'locked': False})
        iid = f'{lid}-n' if n == 1 else f'{lid}-n-{n}'
        return {'id': iid, 'actionTypeId': action, 'config': c}

    def action_list(self, title, groups, initial=False):
        lid = self._lid()
        n, out = 0, []
        for g in groups:
            items = []
            for step in g:
                n += 1
                items.append(self.item(lid, n, step))
            out.append({'actionItems': items})
        self.lists.append({'id': lid, 'title': title, 'actionItemGroups': out, 'useFirstGroupAsInitialState': initial, 'createdOn': IX_TIME})
        return lid

    def event(self, etype, trigger_cls, list_id, media, config=None, stop=None):
        t = self.trigger(trigger_cls)
        ev = {'id': self._eid(), 'name': '', 'animationType': 'custom', 'eventTypeId': etype,
              'action': {'id': '', 'actionTypeId': 'GENERAL_START_ACTION',
                         'config': {'delay': 0, 'easing': '', 'duration': 0, 'actionListId': list_id, 'affectedElements': {},
                                    'playInReverse': False, 'autoStopEventId': stop}},
              'mediaQueries': media, 'target': t, 'targets': [dict(t)],
              'config': config or {'loop': False, 'playInReverse': False, 'scrollOffsetValue': None, 'scrollOffsetUnit': None,
                                   'delay': None, 'direction': None, 'effectIn': None},
              'createdOn': IX_TIME}
        self.events.append(ev)
        return ev

    def pair(self, first_type, second_type, trigger, list_a, list_b, media):
        a = self.event(first_type, trigger, list_a, media)
        b = self.event(second_type, trigger, list_b, media)
        a['action']['config']['autoStopEventId'] = b['id']
        b['action']['config']['autoStopEventId'] = a['id']

    def add(self, spec, title):
        kind = spec['type']
        if kind in UNSUPPORTED_TRIGGERS:
            raise ValueError(f'{kind}: {UNSUPPORTED_TRIGGERS[kind]}')
        media = spec.get('media', ['main', 'medium', 'small', 'tiny'])
        if kind == 'hover-zoom':
            spec = {'type': 'hover', 'trigger': spec['trigger'],
                    'in': [{'type': 'scale', 'target': spec['image'], 'value': 1.04, 'duration': 400, 'easing': 'ease'}],
                    'out': [{'type': 'scale', 'target': spec['image'], 'value': 1, 'duration': 400, 'easing': 'ease'}],
                    'media': spec.get('media', ['main', 'medium'])}
            kind, media = 'hover', spec['media']
        if kind == 'hover':
            a = self.action_list(f'{title} — hover in', [spec['in']])
            b = self.action_list(f'{title} — hover out', [spec['out']])
            self.pair('MOUSE_OVER', 'MOUSE_OUT', spec['trigger'], a, b, media)
            return f'Mouse hover on .{spec["trigger"]}', ('main' not in media or 'small' in media)
        if kind == 'click':
            groups = ([spec['initial']] if spec.get('initial') else []) + [spec['first']]
            a = self.action_list(f'{title} — first click', groups, initial=bool(spec.get('initial')))
            b = self.action_list(f'{title} — second click', [spec['second']])
            self.pair('MOUSE_CLICK', 'MOUSE_SECOND_CLICK', spec['trigger'], a, b, media)
            return f'Mouse click (tap) on .{spec["trigger"]}', False
        if kind == 'scroll-into-view':
            groups = [spec['initial'], spec['animate']]
            a = self.action_list(f'{title} — scroll into view', groups, initial=True)
            cfg = {'loop': False, 'playInReverse': False, 'scrollOffsetValue': spec.get('offset', 10), 'scrollOffsetUnit': '%',
                   'delay': None, 'direction': None, 'effectIn': None}
            ev = self.event('SCROLL_INTO_VIEW', spec['trigger'], a, media, cfg)
            self.next_event += 1
            ev['action']['config']['autoStopEventId'] = f'e-{self.next_event}'
            return f'Scroll into view of .{spec["trigger"]}', False
        raise ValueError(f'unknown interaction type {kind}')

    def data(self):
        return {'interactions': [], 'events': self.events, 'actionLists': self.lists}


def validate_ix(payload):
    """Every trigger and target must resolve inside this payload; ids must follow Webflow's patterns."""
    errors = []
    node_ids = {n['_id'] for n in payload['nodes']}
    style_ids = {s['_id'] for s in payload['styles']}
    ix = payload['ix2']
    list_ids = {a['id'] for a in ix['actionLists']}
    for e in ix['events']:
        if not re.fullmatch(r'e(-\d+)?', e['id']):
            errors.append(f'event id {e["id"]}')
        t = e['target']
        if t.get('id') not in node_ids:
            errors.append(f'{e["id"]} trigger element not in payload')
        if any(g not in style_ids for g in t.get('styleBlockIds', [])):
            errors.append(f'{e["id"]} trigger class not in payload')
        if e['action']['config']['actionListId'] not in list_ids:
            errors.append(f'{e["id"]} action list missing')
    for a in ix['actionLists']:
        if not re.fullmatch(r'a(-\d+)?', a['id']):
            errors.append(f'list id {a["id"]}')
        for g in a['actionItemGroups']:
            for it in g['actionItems']:
                if not re.fullmatch(re.escape(a['id']) + r'-n(-\d+)?', it['id']):
                    errors.append(f'item id {it["id"]}')
                tg = it['config']['target']
                if 'selectorGuids' in tg and any(x not in style_ids for x in tg['selectorGuids']):
                    errors.append(f'{it["id"]} target class not in payload')
    return errors


def build_block(tpl, block):
    el = tpl.soup.select_one(block['selector'])
    if el is None:
        raise ValueError(f"{tpl.meta['slug']}: selector not found {block['selector']}")
    html = str(el)
    b = Builder(tpl)
    rid = b.conv(el)
    if block.get('nav') and tpl.nav_script:
        sid = b.embed(tpl.nav_script, [])
        next(n for n in b.nodes if n['_id'] == rid)['children'].append(sid)
    plain = b.payload([rid])
    ix_docs, unsupported = [], []
    specs = block.get('ix', [])
    with_ix = None
    if specs:
        x = IX(b, f"{tpl.meta['slug']}-{block['key']}")
        for i, spec in enumerate(specs):
            title = spec.get('title') or f"{tpl.meta['name']} / {block['name']}{' ' + str(i + 1) if len(specs) > 1 else ''}"
            try:
                trig, _ = x.add(spec, title)
                ix_docs.append((title, trig, spec.get('note', '')))
            except ValueError as err:
                unsupported.append(str(err))
        if x.events:
            with_ix = json.loads(json.dumps(plain))
            with_ix['payload']['ix2'] = x.data()
            errs = validate_ix(with_ix['payload'])
            if errs:
                raise ValueError(f"{tpl.meta['slug']}-{block['key']} ix2 invalid: {errs[:5]}")
    return {'html': html, 'json': with_ix or plain, 'json_plain': plain if with_ix else None, 'ix_docs': ix_docs, 'ix_unsupported': unsupported}


def build_global(tpl):
    b = Builder(tpl)
    pw = uid()
    b.add({'_id': pw, 'type': 'Block', 'tag': 'div', 'classes': b.class_ids(['page-wrapper']), 'children': [], 'data': {'tag': 'div'}})
    gs = b.embed(tpl.global_embed(), ['global-styles'])
    mw = uid()
    b.add({'_id': mw, 'type': 'Block', 'tag': 'main', 'classes': b.class_ids(['main-wrapper']), 'children': [], 'data': {'tag': 'main'}})
    next(n for n in b.nodes if n['_id'] == pw)['children'] = [gs, mw]
    return b.payload([pw])
