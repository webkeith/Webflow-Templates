from pathlib import Path

HERE = Path(__file__).parent

ICONS = {
    'arrow': '<path d="M5 12h14M13 18l6-6M13 6l6 6"/>',
    'chevron': '<path d="M6 9l6 6 6-6"/>',
    'menu': '<path d="M4 6h16M4 12h16M4 18h16"/>',
    'check': '<path d="M5 12l5 5L20 7"/>',
    'shield': '<path d="M12 3l8 4v5c0 4.5-3.4 8.3-8 9-4.6-.7-8-4.5-8-9V7z"/><path d="M9 12l2 2 4-4"/>',
    'badge': '<circle cx="12" cy="9" r="6"/><path d="M9 14.5L8 21l4-2 4 2-1-6.5"/>',
    'flag': '<path d="M5 21V4M5 4h11l-2 4 2 4H5"/>',
    'search': '<circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/>',
    'image': '<rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="9" cy="10" r="2"/><path d="M21 16l-5-5-9 9"/>',
    'play': '<path d="M8 5v14l11-7z" fill="currentColor"/>',
    'quote': '<path d="M10 7H6a2 2 0 0 0-2 2v4h6V7zM10 13c0 3-2 5-5 5M20 7h-4a2 2 0 0 0-2 2v4h6V7zM20 13c0 3-2 5-5 5"/>',
    'cube': '<path d="M12 3l8 4.5v9L12 21l-8-4.5v-9z"/><path d="M12 12l8-4.5M12 12v9M12 12L4 7.5"/>',
    'x': '<path d="M4 4l16 16M20 4L4 20"/>',
    'linkedin': '<rect x="3" y="3" width="18" height="18" rx="3"/><path d="M8 10v7M8 7v.01M12 17v-4a2 2 0 0 1 4 0v4M12 10v7"/>',
    'instagram': '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><path d="M17.5 6.5v.01"/>',
    'youtube': '<rect x="2" y="5" width="20" height="14" rx="4"/><path d="M10 9l5 3-5 3z"/>',
}

def sprite():
    out = ['<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">']
    for k, v in ICONS.items():
        out.append(f'<symbol id="i-{k}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">{v}</symbol>')
    out.append('</svg>')
    return '\n'.join(out)

def icon(name, cls='icon-embed-xsmall'):
    return f'<span class="{cls}" aria-hidden="true"><svg viewBox="0 0 24 24"><use href="#i-{name}"/></svg></span>'

def logo_svg(cls, label='Logo'):
    return f'<span class="{cls}" aria-hidden="true"><svg viewBox="0 0 112 32"><rect x="1" y="6" width="20" height="20" rx="5" fill="none" stroke="currentColor" stroke-width="2"/><text x="28" y="22" font-family="Inter, Arial, sans-serif" font-size="16" font-weight="700" fill="currentColor">{label}</text></svg></span>'

import json
REGISTRY = json.loads((HERE.parent.parent / 'images.json').read_text())

def placeholder(cls, key='placeholder', eager=False):
    alt = REGISTRY.get(key, {}).get('alt', '')
    loading = 'eager' if eager else 'lazy'
    return f'<img src="lib-image:{key}" alt="{alt}" class="{cls}" loading="{loading}">'

A = icon('arrow')

def navbar():
    def links(n, prefix='Link'):
        words = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen']
        return ''.join(f'<a href="#" class="navbar1_dropdown-link">{prefix} {words[i]}</a>' for i in range(n))
    def dd(label, key, body, mega=False):
        cls = 'navbar1_dropdown is-mega' if mega else 'navbar1_dropdown'
        return (f'<div class="{cls}"><button type="button" class="navbar1_dropdown-toggle" aria-expanded="false" aria-controls="dd-{key}">{label}'
                f'<svg class="navbar1_dropdown-icon" viewBox="0 0 24 24" aria-hidden="true"><use href="#i-chevron"/></svg></button>'
                f'<div class="navbar1_dropdown-list" id="dd-{key}">{body}</div></div>')
    return f'''
<header class="navbar1_component">
  <div class="padding-global">
    <div class="container-large">
      <div class="navbar1_container">
        <a href="#" class="navbar1_logo-link" aria-label="Home">{logo_svg('navbar1_logo')}</a>
        <nav class="navbar1_menu" id="navbar1-menu" aria-label="Main">
          {dd('Solutions', 'solutions', links(5))}
          {dd('Services', 'services', '<div class="navbar1_mega-grid">' + links(16, 'Service') + '</div>', mega=True)}
          {dd('Industries', 'industries', '<div class="navbar1_mega-grid">' + links(12, 'Industry') + '</div>', mega=True)}
          {dd('Resources', 'resources', links(4))}
          <a href="#" class="navbar1_link">About</a>
        </nav>
        <div class="navbar1_button-wrapper">
          <a href="#" class="navbar1_link">Log in</a>
          <a href="#" class="navbar1_link">Pricing</a>
          <a href="#" class="button is-small">Contact us</a>
          <button type="button" class="navbar1_menu-button" aria-expanded="false" aria-controls="navbar1-menu" aria-label="Open menu">{icon('menu', 'icon-embed-small')}</button>
        </div>
      </div>
    </div>
  </div>
</header>'''

def header1():
    trust = ''.join(f'''
              <div class="header1_trust-item">
                <div class="header1_trust-icon">{icon(ic, 'icon-embed-xsmall')}</div>
                <div><p class="text-weight-semibold">{t}</p><p class="text-size-small text-style-muted">{s}</p></div>
              </div>''' for ic, t, s in [('badge', 'Accreditation', 'Short supporting line'), ('shield', 'Certification', 'Short supporting line'), ('flag', 'Local team', 'Short supporting line'), ('search', 'Licensed', 'Short supporting line')])
    return f'''
<section class="section_header1 background-color-black">
  <div class="header1_background">
    {placeholder('header1_background-media', 'hero-team', eager=True)}
    <div class="header1_overlay"></div>
  </div>
  <div class="padding-global">
    <div class="container-large">
      <div class="padding-section-large">
        <div class="header1_component">
          <div class="header1_content">
            <div class="margin-bottom margin-medium">
              <h1 class="heading-style-h1">Medium length hero headline goes here</h1>
            </div>
            <div class="margin-bottom margin-large">
              <p class="text-size-medium text-style-muted">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse varius enim in eros elementum tristique. Duis cursus, mi quis viverra ornare.</p>
            </div>
            <div class="button-group">
              <a href="#" class="button is-alternate">Get started</a>
              <a href="#" class="button is-secondary-alternate">Schedule a call</a>
            </div>
          </div>
          <div class="header1_trust-list">{trust}
          </div>
        </div>
      </div>
    </div>
  </div>
</section>'''

def process1():
    steps = ''.join(f'''
                <li class="process1_item">
                  <div class="process1_marker"><span class="process1_number">{i}</span>{'<span class="process1_line"></span>' if i < 4 else ''}</div>
                  <div>
                    <p class="text-size-small text-weight-semibold">Step {i}</p>
                    <div class="margin-top margin-xxsmall"><h3 class="heading-style-h5">Short step heading goes here</h3></div>
                    <div class="margin-top margin-xsmall"><p class="text-style-muted">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse varius enim in eros elementum tristique.</p></div>
                  </div>
                </li>''' for i in range(1, 5))
    return f'''
<section class="section_process1 background-color-white">
  <div class="padding-global">
    <div class="container-large">
      <div class="padding-section-large">
        <div class="process1_component">
          <div class="process1_content">
            <div class="margin-bottom margin-small"><p class="text-style-tagline">Tagline</p></div>
            <div class="margin-bottom margin-small"><h2 class="heading-style-h2">Short heading for a step-by-step process</h2></div>
            <div class="margin-bottom margin-xlarge"><p class="text-size-medium text-style-muted">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse varius enim in eros elementum tristique.</p></div>
            <ul class="process1_list">{steps}
            </ul>
            <a href="#" class="button is-link">See a demo{A}</a>
          </div>
          {placeholder('process1_image', 'mobile-hand')}
        </div>
      </div>
    </div>
  </div>
</section>'''

def feature1():
    items = ''.join(f'''
              <div class="feature1_item">
                <h3 class="heading-style-h6">Feature name {n}</h3>
                <div class="margin-top margin-xxsmall"><p class="text-style-muted">Short description of what this feature does for the customer.</p></div>
                <div class="margin-top margin-xsmall"><a href="#" class="button is-link">Learn more{A}</a></div>
              </div>''' for n in ('one', 'two', 'three'))
    rows = ''.join(f'<div class="feature1_stat-row"><span class="text-style-muted">{l}</span><span class="text-weight-semibold">{v}</span></div>' for l, v in [('Metric label', 'Up to 90%'), ('Metric label', '100%'), ('Metric label', '24/7')])
    return f'''
<section class="section_feature1 background-color-gray">
  <div class="padding-global">
    <div class="container-large">
      <div class="padding-section-large">
        <div class="feature1_component">
          <div class="feature1_content">
            <div class="margin-bottom margin-small"><p class="text-style-tagline">Tagline</p></div>
            <div class="margin-bottom margin-small"><h2 class="heading-style-h2">Medium length section heading goes here</h2></div>
            <div class="margin-bottom margin-large"><p class="text-size-medium text-style-muted">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse varius enim in eros elementum tristique. Duis cursus, mi quis viverra ornare, eros dolor interdum nulla.</p></div>
            <div class="feature1_list">{items}
            </div>
          </div>
          <div class="feature1_visual">
            {placeholder('feature1_image', 'feature-laptop')}
            <div class="feature1_stat-card">
              <p class="text-size-small text-style-muted">Card label</p>
              <div class="margin-top margin-xxsmall margin-bottom margin-small"><p class="heading-style-h6">Dashboard summary</p></div>
              {rows}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>'''

def signup1():
    form = '''<form class="form_inline" action="#" method="post"><label class="hide" for="signup1-email">Email</label><input class="form_input" type="email" id="signup1-email" name="email" placeholder="Enter your email" autocomplete="email" required><button class="form_button" type="submit">Get report</button></form><p class="form_note">No spam. Unsubscribe anytime.</p>'''
    return f'''
<section class="section_signup1 background-color-white">
  <div class="padding-global">
    <div class="container-medium">
      <div class="padding-section-medium">
        <div class="signup1_component">
          <div class="margin-bottom margin-xsmall"><h2 class="heading-style-h4">Short heading for a lead magnet</h2></div>
          <div class="margin-bottom margin-medium"><p class="text-style-muted">Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p></div>
          <div class="signup1_form" data-wf-embed>{form}</div>
          <div class="margin-top margin-small"><a href="#" class="button is-link">Learn more about this offer{A}</a></div>
        </div>
      </div>
    </div>
  </div>
</section>'''

def layout1():
    return f'''
<section class="section_layout1 background-color-white">
  <div class="padding-global">
    <div class="container-large">
      <div class="padding-section-large">
        <div class="layout1_component">
          <div class="layout1_media">
            {placeholder('layout1_image', 'meeting-conversation')}
            <a href="#" class="layout1_play" aria-label="Play video">{icon('play', 'icon-embed-small')}</a>
          </div>
          <div class="layout1_content">
            <div class="margin-bottom margin-small"><p class="text-style-tagline">Tagline</p></div>
            <div class="margin-bottom margin-small"><h2 class="heading-style-h2">Medium length section heading goes here</h2></div>
            <p class="text-size-medium text-style-muted">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse varius enim in eros elementum tristique. Duis cursus, mi quis viverra ornare, eros dolor interdum nulla, ut commodo diam libero vitae erat.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>'''

def check_items(n, text='Short benefit statement goes here'):
    return ''.join(f'<li class="check-list_item"><span class="check-list_icon" aria-hidden="true"><svg viewBox="0 0 24 24"><use href="#i-check"/></svg></span><span>{text}</span></li>' for _ in range(n))

def feature2():
    return f'''
<section class="section_feature2 background-color-gray">
  <div class="padding-global">
    <div class="container-large">
      <div class="padding-section-large">
        <div class="feature2_component">
          <div class="feature2_content">
            <div class="margin-bottom margin-small"><p class="text-style-tagline">Tagline</p></div>
            <div class="margin-bottom margin-small"><h2 class="heading-style-h2">Every feature you need. One platform.</h2></div>
            <div class="margin-bottom margin-large"><p class="text-size-medium text-style-muted">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse varius enim in eros elementum tristique.</p></div>
            <ul class="check-list">{check_items(3)}</ul>
          </div>
          <div>
            {placeholder('feature2_map', 'placeholder')}
            <div class="margin-top margin-small"><a href="#" class="button is-link">View all locations{A}</a></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>'''

def layout2():
    items = ''.join(f'''
              <div class="layout2_item">
                {icon('cube', 'icon-embed-medium')}
                <div>
                  <h3 class="heading-style-h5">Short heading goes here</h3>
                  <div class="margin-top margin-xsmall"><p class="text-style-muted">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse varius enim in eros elementum tristique.</p></div>
                </div>
              </div>''' for _ in range(3))
    return f'''
<section class="section_layout2 background-color-white">
  <div class="padding-global">
    <div class="container-large">
      <div class="padding-section-large">
        <div class="margin-bottom margin-xxlarge">
          <div class="layout2_header">
            <div class="margin-bottom margin-small"><h2 class="heading-style-h2">Medium length section heading goes here</h2></div>
            <p class="text-size-medium text-style-muted">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse varius enim in eros elementum tristique.</p>
          </div>
        </div>
        <div class="layout2_component">
          {placeholder('layout2_image', 'portrait-support')}
          <div class="layout2_list">{items}
            <div><a href="#" class="button is-secondary">Learn more</a></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>'''

def testimonial1():
    cards = ''.join(f'''
          <div class="testimonial1_card">
            <div>
              <span class="testimonial1_quote-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><use href="#i-quote"/></svg></span>
              <div class="margin-top margin-small"><h3 class="heading-style-h6">Short testimonial title</h3></div>
              <div class="margin-top margin-xsmall"><p class="text-style-muted">"Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse varius enim in eros elementum tristique."</p></div>
            </div>
            <div class="testimonial1_client">
              <div class="testimonial1_avatar" aria-hidden="true">{i}</div>
              <div><p class="text-weight-semibold">Name Surname</p><p class="text-size-small text-style-muted">Position, Company name</p></div>
            </div>
          </div>''' for i in ('A', 'B', 'C'))
    return f'''
<section class="section_testimonial1 background-color-gray">
  <div class="padding-global">
    <div class="container-large">
      <div class="padding-section-large">
        <div class="margin-bottom margin-xxlarge">
          <div class="max-width-large align-center text-align-center">
            <div class="margin-bottom margin-small"><h2 class="heading-style-h2">Customer testimonials</h2></div>
            <p class="text-size-medium text-style-muted">Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>
          </div>
        </div>
        <div class="testimonial1_list">{cards}
        </div>
      </div>
    </div>
  </div>
</section>'''

def pricing1():
    def card(name, price, featured=False):
        feats = ''.join(f'<li class="pricing1_feature"><span class="check-list_icon" aria-hidden="true"><svg viewBox="0 0 24 24"><use href="#i-check"/></svg></span><span>Feature text goes here</span></li>' for _ in range(6))
        badge = '<span class="pricing1_badge">Most popular</span>' if featured else ''
        cls = 'pricing1_card is-featured' if featured else 'pricing1_card'
        btn = 'button is-full' if featured else 'button is-secondary is-full'
        return f'''
          <div class="{cls}">
            {badge}
            <h3 class="heading-style-h6">{name}</h3>
            <div class="margin-top margin-small"><div class="pricing1_price"><span class="pricing1_price-value">{price}</span><span class="text-style-muted">/ unit</span></div></div>
            <div class="margin-top margin-xsmall"><p class="text-size-small text-style-muted">Short qualifier line</p></div>
            <div class="pricing1_divider"></div>
            <ul class="pricing1_feature-list">{feats}</ul>
            <a href="#" class="{btn}">Get started</a>
          </div>'''
    return f'''
<section class="section_pricing1 background-color-white">
  <div class="padding-global">
    <div class="container-large">
      <div class="padding-section-large">
        <div class="margin-bottom margin-xxlarge">
          <div class="pricing1_header">
            <div class="margin-bottom margin-small"><p class="text-style-tagline">Tagline</p></div>
            <div class="margin-bottom margin-small"><h2 class="heading-style-h2">Simple pricing</h2></div>
            <p class="text-size-medium text-style-muted">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse varius enim in eros elementum tristique.</p>
          </div>
        </div>
        <div class="pricing1_list">{card('Basic plan', '$19')}{card('Business plan', '$29', True)}{card('Enterprise plan', '$49')}
        </div>
      </div>
    </div>
  </div>
</section>'''

def logo1():
    logos = ''.join(logo_svg('logo1_logo', 'Logo') for _ in range(8))
    return f'''
<section class="section_logo1 background-color-white">
  <div class="padding-global">
    <div class="container-large">
      <div class="padding-section-medium">
        <div class="margin-bottom margin-large"><h2 class="heading-style-h6 text-align-center">Trusted by the world's best companies</h2></div>
      </div>
    </div>
  </div>
  <div class="logo1_marquee" aria-label="Partner logos">
    <div class="logo1_track">{logos}</div>
    <div class="logo1_track" aria-hidden="true">{logos}</div>
  </div>
  <div class="padding-section-small"></div>
</section>'''

def feature3():
    feats = ''.join(f'''
          <div>
            <h3 class="heading-style-h5">Short feature heading goes here</h3>
            <div class="margin-top margin-xsmall"><p class="text-style-muted">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse varius enim in eros elementum tristique. Duis cursus, mi quis viverra ornare.</p></div>
          </div>''' for _ in range(4))
    stats = ''.join(f'<div><p class="feature3_stat-value">{v}</p><p class="text-style-muted">Short stat label</p></div>' for v in ('100%', '50+', '0', '24/7'))
    return f'''
<section class="section_feature3 background-color-white">
  <div class="padding-global">
    <div class="container-large">
      <div class="padding-section-large">
        <div class="margin-bottom margin-xxlarge">
          <div class="feature3_header">
            <div class="margin-bottom margin-small"><p class="text-style-tagline">Tagline</p></div>
            <h2 class="heading-style-h2">Medium length section heading goes here</h2>
          </div>
        </div>
        <div class="feature3_grid">{feats}
        </div>
        <div class="margin-top margin-xxlarge margin-bottom margin-xxlarge"><div class="feature3_stats">{stats}</div></div>
        {placeholder('feature3_image', 'architecture')}
        <div class="margin-top margin-small"><p class="text-size-small text-style-muted text-align-center">Short image caption goes here.</p></div>
      </div>
    </div>
  </div>
</section>'''

def blog1():
    items = ''.join(f'''
          <article class="blog1_item" role="listitem">
            <div class="blog1_image-wrapper">{placeholder('blog1_image', img)}</div>
            <div class="blog1_content">
              <div class="blog1_meta"><span class="blog1_tag">Category</span><span class="text-style-muted">5 min read</span></div>
              <h3 class="heading-style-h5"><a href="#" class="blog1_title-link">Blog title heading will go here</a></h3>
              <p class="text-style-muted">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse varius enim in eros.</p>
              <div class="blog1_footer"><span>Author Name · Jan 1, 2026</span><span class="text-weight-semibold">Read</span></div>
            </div>
          </article>''' for img in ('workspace-flatlay', 'architecture', 'landscape-dusk'))
    return f'''
<section class="section_blog1 background-color-gray">
  <div class="padding-global">
    <div class="container-large">
      <div class="padding-section-large">
        <div class="margin-bottom margin-xxlarge">
          <div class="blog1_header">
            <div class="max-width-large">
              <div class="margin-bottom margin-small"><p class="text-style-tagline">Blog</p></div>
              <div class="margin-bottom margin-small"><h2 class="heading-style-h2">Short heading goes here</h2></div>
              <p class="text-size-medium text-style-muted">Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>
            </div>
            <a href="#" class="button is-secondary">View all</a>
          </div>
        </div>
        <div class="blog1_list" role="list">{items}
        </div>
      </div>
    </div>
  </div>
</section>'''

def contact1():
    form = '''<form action="#" method="post"><div class="form_field-grid">
<div class="form_field"><label class="form_label" for="c1-name">Full name</label><input class="form_input" id="c1-name" name="name" type="text" autocomplete="name" required></div>
<div class="form_field"><label class="form_label" for="c1-company">Company</label><input class="form_input" id="c1-company" name="company" type="text" autocomplete="organization"></div>
<div class="form_field"><label class="form_label" for="c1-email">Work email</label><input class="form_input" id="c1-email" name="email" type="email" autocomplete="email" required></div>
<div class="form_field"><label class="form_label" for="c1-phone">Phone</label><input class="form_input" id="c1-phone" name="phone" type="tel" autocomplete="tel"></div>
<div class="form_field"><label class="form_label" for="c1-size">Select one</label><select class="form_input" id="c1-size" name="size"><option value="">Select one…</option><option>First choice</option><option>Second choice</option><option>Third choice</option></select></div>
<div class="form_field"><label class="form_label" for="c1-industry">Select one</label><select class="form_input" id="c1-industry" name="industry"><option value="">Select one…</option><option>First choice</option><option>Second choice</option><option>Third choice</option></select></div>
<div class="form_field is-full"><label class="form_label" for="c1-message">Message</label><textarea class="form_input is-textarea" id="c1-message" name="message" placeholder="Type your message…"></textarea></div>
<div class="form_field is-full"><button class="form_button is-full" type="submit">Send message</button><p class="form_note">Short consent or privacy note goes here.</p></div>
</div></form>'''
    return f'''
<section class="section_contact1 background-color-black">
  <div class="padding-global">
    <div class="container-large">
      <div class="padding-section-large">
        <div class="contact1_component">
          <div class="contact1_content">
            <div class="margin-bottom margin-small"><p class="text-style-tagline">Contact</p></div>
            <div class="margin-bottom margin-small"><h2 class="heading-style-h2">Medium length heading for a contact form</h2></div>
            <div class="margin-bottom margin-large"><p class="text-size-medium text-style-muted">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse varius enim in eros elementum tristique.</p></div>
            <ul class="check-list">{check_items(4)}</ul>
          </div>
          <div class="contact1_card">
            <div class="margin-bottom margin-xsmall"><h3 class="heading-style-h5">Send us a message</h3></div>
            <div class="margin-bottom margin-medium"><p class="text-style-muted">Short line about response time.</p></div>
            <div class="contact1_form" data-wf-embed>{form}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>'''

def footer1():
    cols = ''.join(f'''
            <div>
              <p class="footer1_menu-heading">Column {n}</p>
              <ul class="footer1_link-list">{''.join('<li><a href="#" class="footer1_link">Link text</a></li>' for _ in range(c))}</ul>
            </div>''' for n, c in (('one', 4), ('two', 4), ('three', 5), ('four', 2), ('five', 3)))
    socials = ''.join(f'<a href="#" class="footer1_social-link" aria-label="{lbl}"><svg viewBox="0 0 24 24" aria-hidden="true"><use href="#i-{k}"/></svg></a>' for k, lbl in (('x', 'X'), ('linkedin', 'LinkedIn'), ('instagram', 'Instagram'), ('youtube', 'YouTube')))
    return f'''
<footer class="footer1_component">
  <div class="padding-global">
    <div class="container-large">
      <div class="padding-section-medium">
        <div class="footer1_top">
          <div>
            <div class="margin-bottom margin-medium"><a href="#" class="footer1_logo-link" aria-label="Home">{logo_svg('footer1_logo')}</a></div>
            <div class="margin-bottom margin-medium"><p class="text-size-small text-style-muted">Short company description goes here. Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p></div>
            <div class="footer1_social-list">{socials}</div>
          </div>
          <nav class="footer1_menu" aria-label="Footer">{cols}
          </nav>
        </div>
        <div class="margin-top margin-xxlarge">
          <div class="footer1_bottom padding-top padding-medium">
            <p>© 2026 Company name. All rights reserved.</p>
            <div class="footer1_legal"><a href="#" class="footer1_link">Terms</a><a href="#" class="footer1_link">Privacy Policy</a><a href="#" class="footer1_link">Cookies</a><a href="#" class="footer1_link">Sitemap</a></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</footer>'''


TRUST = [('badge', 'Accreditation', 'Short supporting line'), ('shield', 'Certification', 'Short supporting line'), ('flag', 'Local team', 'Short supporting line'), ('search', 'Licensed', 'Short supporting line')]

def header2():
    trust = ''.join(f'<div class="header2_trust-item"><span class="header2_trust-icon">{icon(ic, "icon-embed-xsmall")}</span><div><p class="text-weight-semibold">{t}</p><p class="text-size-small text-style-muted">{s}</p></div></div>' for ic, t, s in TRUST)
    return f'''
<section class="section_header2 background-color-gray">
  <div class="padding-global">
    <div class="container-large">
      <div class="header2_component">
        <div class="header2_content">
          <div class="margin-bottom margin-small"><p class="text-style-tagline">Tagline</p></div>
          <div class="margin-bottom margin-medium"><h1 class="heading-style-h1">Medium length hero headline goes here</h1></div>
          <div class="margin-bottom margin-large"><p class="text-size-medium text-style-muted">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse varius enim in eros elementum tristique. Duis cursus, mi quis viverra ornare.</p></div>
          <div class="button-group">
            <a href="#" class="button">Primary action</a>
            <a href="#" class="button is-secondary">Secondary action</a>
          </div>
        </div>
        <div class="header2_visual">
          {placeholder('header2_image', 'feature-laptop', eager=True)}
          <div class="header2_status">
            <span class="header2_status-icon">{icon('check', 'icon-embed-xsmall')}</span>
            <div>
              <p class="text-size-small text-weight-semibold">Status label</p>
              <p class="text-size-small text-style-muted">Name S. · Approved</p>
              <p class="text-size-tiny text-style-muted">Short detail line</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div class="header2_trust">
    <div class="padding-global">
      <div class="container-large">
        <div class="header2_trust-list">{trust}</div>
      </div>
    </div>
  </div>
</section>'''

def feature4():
    def item(n):
        return f'''<div class="feature4_item">
              <span class="feature4_icon">{icon('cube', 'icon-embed-xsmall')}</span>
              <h3 class="heading-style-h6">Feature name {n}</h3>
              <p class="text-style-muted">Short description of the benefit. Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>
            </div>'''
    return f'''
<section class="section_feature4 background-color-white">
  <div class="padding-global">
    <div class="container-large">
      <div class="padding-section-large">
        <div class="margin-bottom margin-xxlarge">
          <div class="max-width-large align-center text-align-center">
            <div class="margin-bottom margin-small"><p class="text-style-tagline">Tagline</p></div>
            <h2 class="heading-style-h2">Medium length section heading goes here</h2>
          </div>
        </div>
        <div class="feature4_component">
          <div class="feature4_column">{item('one')}{item('two')}</div>
          <div class="feature4_visual">{placeholder('feature4_image', 'workspace-flatlay')}</div>
          <div class="feature4_column">{item('three')}{item('four')}{item('five')}</div>
        </div>
      </div>
    </div>
  </div>
</section>'''

def stats1():
    stats = ''.join(f'<div class="stats1_item"><p class="stats1_value">{v}</p><p class="text-weight-semibold">Short stat label</p><p class="text-size-small text-style-muted">Supporting detail</p></div>' for v in ('90%', '$0', '5 min', '24/7'))
    return f'''
<section class="section_stats1 background-color-black">
  <div class="padding-global">
    <div class="container-large">
      <div class="padding-section-medium">
        <div class="stats1_list">{stats}</div>
      </div>
    </div>
  </div>
</section>'''

def process2():
    steps = ''.join(f'''
          <div class="process2_item">
            <div class="process2_marker"><span class="process2_number">{i}</span><span class="process2_line" aria-hidden="true"></span></div>
            <p class="text-size-small text-weight-semibold text-style-muted">Step {i}</p>
            <h3 class="heading-style-h5">Short step heading</h3>
            <p class="text-style-muted">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse varius enim in eros.</p>
          </div>''' for i in range(1, 5))
    return f'''
<section class="section_process2 background-color-gray">
  <div class="padding-global">
    <div class="container-large">
      <div class="padding-section-large">
        <div class="margin-bottom margin-xxlarge">
          <div class="max-width-large">
            <div class="margin-bottom margin-small"><p class="text-style-tagline">How it works</p></div>
            <div class="margin-bottom margin-small"><h2 class="heading-style-h2">Short process heading goes here</h2></div>
            <p class="text-size-medium text-style-muted">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse varius enim in eros elementum tristique.</p>
          </div>
        </div>
        <div class="process2_list">{steps}
        </div>
      </div>
    </div>
  </div>
</section>'''

def layout3():
    rows = [('architecture', ''), ('portrait-support', ' is-reversed'), ('meeting-conversation', '')]
    out = ''
    for i, (img, mod) in enumerate(rows, 1):
        out += f'''
          <div class="layout3_row{mod}">
            <div class="layout3_media">{placeholder('layout3_image', img)}</div>
            <div class="layout3_content">
              <div class="margin-bottom margin-xsmall"><p class="text-style-tagline">Tagline</p></div>
              <div class="margin-bottom margin-small"><h3 class="heading-style-h3">Medium length heading goes here</h3></div>
              <div class="margin-bottom margin-medium"><p class="text-size-medium text-style-muted">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse varius enim in eros elementum tristique. Duis cursus, mi quis viverra ornare, eros dolor interdum nulla, ut commodo diam libero vitae erat.</p></div>
              <p class="layout3_note">Short highlighted takeaway for this row.</p>
            </div>
          </div>'''
    return f'''
<section class="section_layout3 background-color-white">
  <div class="padding-global">
    <div class="container-large">
      <div class="padding-section-large">
        <div class="margin-bottom margin-xxlarge">
          <div class="max-width-large align-center text-align-center">
            <div class="margin-bottom margin-small"><p class="text-style-tagline">Tagline</p></div>
            <h2 class="heading-style-h2">Medium length section heading goes here</h2>
          </div>
        </div>
        <div class="layout3_list">{out}
        </div>
      </div>
    </div>
  </div>
</section>'''

def signup2():
    form = '<form class="form_inline" action="#" method="post"><label class="hide" for="signup2-email">Email</label><input class="form_input" type="email" id="signup2-email" name="email" placeholder="Enter your email" autocomplete="email" required><button class="form_button" type="submit">Sign up</button></form><p class="form_note">By signing up you agree to our Terms and Conditions.</p>'
    return f'''
<section class="section_signup2 background-color-white">
  <div class="padding-global">
    <div class="container-large">
      <div class="padding-section-large">
        <div class="signup2_component">
          {placeholder('signup2_image', 'landscape-dusk')}
          <div class="signup2_content">
            <div class="margin-bottom margin-small"><p class="text-style-tagline">Newsletter</p></div>
            <div class="margin-bottom margin-small"><h2 class="heading-style-h2">Subscribe to our newsletter</h2></div>
            <div class="margin-bottom margin-large"><p class="text-size-medium text-style-muted">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse varius enim in eros elementum tristique.</p></div>
            <div class="signup2_form" data-wf-embed>{form}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>'''

FONTS = 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap'

def build():
    body = '\n'.join([navbar(), '<main class="main-wrapper">', header1(), process1(), feature1(), signup1(), layout1(), feature2(), layout2(), testimonial1(), pricing1(), logo1(), feature3(), blog1(), contact1(), header2(), feature4(), stats1(), process2(), layout3(), signup2(), '</main>', footer1()])
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SaaS / B2B services — wireframe template</title>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="style.css">
</head>
<body>
{sprite()}
<div class="page-wrapper">
{body}
</div>
<script src="nav.js"></script>
</body>
</html>'''
    (HERE / 'index.html').write_text(html)

if __name__ == '__main__':
    build()
