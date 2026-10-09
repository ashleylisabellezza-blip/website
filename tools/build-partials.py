"""Stamp the shared page chrome into every page as static HTML.

Usage (normally via build.py):
    python tools/build-partials.py

Each page keeps only its own content. Between these markers the build
writes generated HTML (never edit inside them; the next run overwrites):

    <!-- partial:head:start -->        <title>, meta, canonical, fonts, CSS
    <!-- partial:top:start -->         skip link, utility bar, header, mobile menu
    <!-- partial:breadcrumb:start -->  breadcrumb trail (inner pages)
    <!-- partial:hours:start -->       weekly hours table
    <!-- partial:holidays:start -->    upcoming holiday hours (next 12 months)
    <!-- partial:bottom:start -->      booking band, footer, mobile book bar, scripts

It also fills live values from the page content, so numbers never drift:
    <span data-count="team">          number of team cards on our-team.html
    <span data-count="dept-hair">     team cards whose data-dept includes "hair"
    <span data-range="salon.html#cuts-women">   "$37–60" from that group or item
    <span data-from="facials.html#facials">     "from $55" (lowest price)
    <time data-asof>                  "Prices as of September 2026"
    <span data-google-rating>         "4.8 on Google from 761 reviews, as of October 2026"
    <!-- partial:reviews:start -->    permitted Google review quotes (reviews-bridal: Bridal only)
and the /* config:start */ block in assets/js/site.js (hours, holidays, URLs).

Data lives in tools/site.json (business facts) and tools/pages.json (titles,
descriptions, breadcrumbs, Book labels).
"""
import calendar
import datetime as dt
import hashlib
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, 'tools')
SITE = json.load(open(os.path.join(TOOLS, 'site.json'), encoding='utf-8'))
PAGES = {p['file']: p for p in json.load(open(os.path.join(TOOLS, 'pages.json'), encoding='utf-8'))['pages']}
U = SITE['urls']
TODAY = dt.date.today()

esc = lambda s: html.escape(s, quote=True)

# ------------------------------------------------------------------ icons (Lucide, 1.5 stroke)
def icon(name, label=None):
    paths = {
        'phone': '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.8 19.8 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.12 4.18 2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.1 9.9a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.9.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"/>',
        'pin': '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/>',
        'menu': '<line x1="4" y1="7" x2="20" y2="7"/><line x1="4" y1="12" x2="20" y2="12"/><line x1="4" y1="17" x2="20" y2="17"/>',
        'close': '<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>',
        'chevron': '<polyline points="6 9 12 15 18 9"/>',
        'instagram': '<rect x="2" y="2" width="20" height="20" rx="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/><line x1="17.5" y1="6.5" x2="17.51" y2="6.5"/>',
        'facebook': '<path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/>',
        'gift': '<rect x="3" y="8" width="18" height="4" rx="1"/><path d="M12 8v13"/><path d="M19 12v7a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2v-7"/><path d="M7.5 8a2.5 2.5 0 0 1 0-5C11 3 12 8 12 8s1-5 4.5-5a2.5 2.5 0 0 1 0 5"/>',
        'clock': '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    }
    a11y = f' role="img" aria-label="{esc(label)}"' if label else ' aria-hidden="true" focusable="false"'
    return (f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" '
            f'stroke-linecap="round" stroke-linejoin="round"{a11y}>{paths[name]}</svg>')


# ------------------------------------------------------------------ helpers
def read(path):
    return open(os.path.join(ROOT, path), encoding='utf-8').read()


def content_hash(path):
    try:
        return hashlib.sha1(open(os.path.join(ROOT, path), 'rb').read()).hexdigest()[:8]
    except FileNotFoundError:
        return '0'


def v(path):
    return f'{path}?v={content_hash(path)}'


def fmt_time(hhmm):
    h, m = map(int, hhmm.split(':'))
    suffix = 'am' if h < 12 else 'pm'
    h12 = h % 12 or 12
    return f'{h12}{suffix}' if m == 0 else f'{h12}:{m:02d}{suffix}'


def month_year(yyyymm):
    y, m = map(int, yyyymm.split('-'))
    return f'{calendar.month_name[m]} {y}'


ADDR = SITE['address']
ADDR_LINE = f"{ADDR['street']}, {ADDR['city']}, {ADDR['region']} {ADDR['zip']}"

# Short page labels for breadcrumbs and nav
LABELS = {
    'index.html': 'Home', 'services.html': 'Services & Prices', 'salon.html': 'Hair',
    'tips-and-toes.html': 'Nails', 'massages.html': 'Massage', 'facials.html': 'Facials',
    'hair-removal.html': 'Waxing', 'makeup-and-eyes.html': 'Brows, Lashes & Makeup',
    'spray-tans.html': 'Spray Tans', 'mens-care.html': "Men's", 'brides.html': 'Bridal',
    'slay-aesthetics.html': 'Slay Aesthetics', 'specials.html': 'Specials',
    'book-online.html': 'Book Online', 'products.html': 'The Boutique',
    'products-dermalogica.html': 'Dermalogica', 'products-ref.html': 'REF', 'products-lakme.html': 'Lakmé',
    'products-voesh.html': 'VOESH', 'products-olaplex.html': 'Olaplex', 'products-smashbox.html': 'Smashbox',
    'products-calecim.html': 'Calecim', 'products-ecru-new-york.html': 'ECRU New York', 'products-om.html': 'O&M',
    'our-team.html': 'Meet the Team', 'about.html': 'Our Story', 'new-guests.html': 'New Guests',
    'join-our-team.html': 'Careers', 'job-massage-therapist.html': 'Massage Therapist',
    'job-nail-therapist.html': 'Nail Therapist', 'job-experienced-hair-stylist.html': 'Experienced Hair Stylist',
    'job-new-talent.html': 'New Talent', 'job-internship.html': 'Internship', 'contact-us.html': 'Visit & Contact',
    'gift-cards.html': 'Gift Cards', 'pick-up-orders.html': 'Pick-up Orders', 'policies.html': 'Policies',
    '404.html': 'Page not found', 'thank-you.html': 'Thank you',
}

# ------------------------------------------------------------------ price data from pages
PRICE_ITEM = re.compile(r'<li\b[^>]*class="price-item\b[^"]*"[^>]*>(.*?)</li>', re.S)


def _numbers(text):
    return [float(n) for n in re.findall(r'\d+(?:\.\d+)?', text.replace(',', ''))]


def _prices_in(fragment):
    out = []
    for li in PRICE_ITEM.findall(fragment):
        m = re.search(r'<span class="price">(.*?)</span>', li, re.S)
        if not m:
            continue
        txt = html.unescape(re.sub(r'<[^>]+>', '', m.group(1)))
        if re.search(r'unit|month|ml', txt, re.I):
            continue  # per-unit prices are not comparable
        out += _numbers(txt)
    return out


def _fragment(spec):
    """'salon.html#cuts-women' -> HTML of that group/item; 'massages.html' -> whole menu."""
    file, _, frag = spec.partition('#')
    try:
        page = read(file)
    except FileNotFoundError:
        return None
    if not frag:
        return page
    m = re.search(r'<(div|li)\b[^>]*\bid="%s"[^>]*>' % re.escape(frag), page)
    if not m:
        return None
    tag = m.group(1)
    if tag == 'li':
        end = page.find('</li>', m.end())
        return page[m.start():end + 5]
    # a menu-group div: up to the next menu-group or section end
    nxt = re.search(r'<div\b[^>]*class="menu-group\b|</section>', page[m.end():])
    return page[m.start(): m.end() + (nxt.start() if nxt else len(page))]


def _fmt(n):
    return str(int(n)) if n == int(n) else f'{n:.2f}'


def price_value(kind, spec):
    frag = _fragment(spec)
    if frag is None:
        return None
    nums = _prices_in(frag)
    if not nums:
        return None
    lo, hi = min(nums), max(nums)
    if kind == 'from':
        return f'from ${_fmt(lo)}'
    return f'${_fmt(lo)}' if lo == hi else f'${_fmt(lo)}–{_fmt(hi)}'


def nav_price(spec, prefix):
    kind, _, arg = spec.partition(':')
    if kind == 'text':
        return arg
    val = price_value(kind, arg)
    if not val:
        return ''
    text = f'{prefix}{val}'
    return text[0].upper() + text[1:]


# ------------------------------------------------------------------ team counts
def team_counts():
    try:
        page = read('our-team.html')
    except FileNotFoundError:
        return {}
    items = re.findall(r'<li\b[^>]*class="team-item\b[^"]*"[^>]*>', page)
    counts = {'team': len(items)}
    providers = 0
    for tag in items:
        m = re.search(r'data-dept="([^"]*)"', tag)
        depts = m.group(1).split() if m else []
        for d in depts:
            counts['dept-' + d] = counts.get('dept-' + d, 0) + 1
        if set(depts) & {'hair', 'nails', 'skin', 'massage', 'makeup'}:
            providers += 1
    counts['providers'] = providers
    return counts


# ------------------------------------------------------------------ hours & holidays
def hours_rows():
    rows = []
    for h in SITE['hours']:
        when = f"{fmt_time(h['opens'])}–{fmt_time(h['closes'])}" if h['opens'] else 'Closed'
        rows.append((h['day'], when))
    return rows


def resolve_holidays(start, days=366):
    """Concrete dated holiday entries between start and start+days."""
    out = []
    for year in (start.year, start.year + 1):
        for h in SITE['holidays']:
            rule = h.get('rule')
            if rule == 'last-monday-may':
                d = max(dt.date(year, 5, day) for day in range(25, 32) if dt.date(year, 5, day).weekday() == 0)
            elif rule == 'first-monday-september':
                d = min(dt.date(year, 9, day) for day in range(1, 8) if dt.date(year, 9, day).weekday() == 0)
            elif rule == 'trick-or-treat':
                iso = SITE.get('trickOrTreat', {}).get(str(year))
                d = dt.date.fromisoformat(iso) if iso else None
            else:
                d = dt.date(year, h['month'], h['day'])
            if d and start <= d <= start + dt.timedelta(days=days):
                out.append({'date': d.isoformat(), 'name': h['name'],
                            'closed': bool(h.get('closed')), 'closes': h.get('closes')})
    return sorted(out, key=lambda x: x['date'])


def hours_table(caption=True, dark=False):
    rows = ''.join(f'<tr data-day="{d}"><th scope="row">{d}</th><td>{w}</td></tr>' for d, w in hours_rows())
    cap = '<caption>Hours</caption>' if caption else ''
    return f'<table class="hours">{cap}<tbody>{rows}</tbody></table>'


def holiday_table():
    rows = []
    for h in resolve_holidays(TODAY):
        d = dt.date.fromisoformat(h['date'])
        when = 'Closed' if h['closed'] else f"Closing at {fmt_time(h['closes'])}"
        rows.append(f'<tr><th scope="row">{esc(h["name"])} · {d.strftime("%a %b")} {d.day}, {d.year}</th><td>{when}</td></tr>')
    tot = SITE.get('trickOrTreat', {})
    note = ''
    if not any(str(y) in tot for y in (TODAY.year, TODAY.year + 1)):
        note = ('<p class="microcopy">Newark Trick-or-Treat night (date set by the city): we close at 5pm.</p>')
    return f'<table class="holidays"><caption class="sr-only">Upcoming holiday hours</caption><tbody>{"".join(rows)}</tbody></table>{note}'


# ------------------------------------------------------------------ partials
def book_link(page, placement, cls='btn btn--book', label=None, extra=''):
    ov = page.get('bookOverride')
    # Header and drawer keep Bellezza booking, except on Slay (no gold anywhere there)
    if ov and (placement not in ('header', 'drawer', 'header-t') or ov['cta'] == 'slay'):
        cls = cls.replace('btn--book', 'btn--strong')
        tgt = ov['href']
        lab = label or ov['label']
        return (f'<a class="{cls}" href="{esc(tgt)}" data-cta="{ov["cta"]}" data-placement="{placement}"{extra}>'
                f'{esc(lab)}</a>')
    lab = label or 'Book an appointment'
    return (f'<a class="{cls}" href="{esc(U["book"])}" data-book data-cta="book" data-placement="{placement}"{extra}>'
            f'{esc(lab)}</a>')


def part_head(file, page):
    url = U['site'] if file == 'index.html' else U['site'] + file
    noindex = page.get('noindex')
    lines = [
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">',
    ]
    if file == '404.html':
        lines.append('<base href="/">')
    lines += [
        f'<title>{esc(page["title"])}</title>',
    ]
    if page['description']:
        lines.append(f'<meta name="description" content="{esc(page["description"])}">')
    if noindex:
        lines.append('<meta name="robots" content="noindex">')
    else:
        lines.append(f'<link rel="canonical" href="{url}">')
    lines += [
        '<meta name="theme-color" content="#faf8f5">',
        '<meta property="og:type" content="website">',
        '<meta property="og:site_name" content="Bellezza &amp; Co.">',
        f'<meta property="og:title" content="{esc(page["title"])}">',
    ]
    if page['description']:
        lines.append(f'<meta property="og:description" content="{esc(page["description"])}">')
    lines += [
        f'<meta property="og:url" content="{url}">',
        f'<meta property="og:image" content="{U["site"]}assets/img/og-image.jpg">',
        '<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<link rel="icon" href="{v("assets/img/favicon.png")}">',
        f'<link rel="preload" href="{v("assets/fonts/italiana-latin.woff2")}" as="font" type="font/woff2" crossorigin>',
        f'<link rel="preload" href="{v("assets/fonts/montserrat-latin.woff2")}" as="font" type="font/woff2" crossorigin>',
    ]
    lines.append(f'<link rel="stylesheet" href="{v("assets/css/styles.css")}">')
    # Plausible analytics (owner-approved): cookieless, no banner; site.js sends CTA click events
    lines.append('<script defer data-domain="bellezzaspaonline.com" src="https://plausible.io/js/script.js"></script>')
    if file in ('new-guests.html', 'book-online.html'):
        lines.append(f'<meta name="apple-itunes-app" content="app-id={U["iosAppId"]}">')
    if file == 'index.html':
        lines.append('<link rel="preload" as="image" href="assets/img/home/hero-1448.avif" '
                     'imagesrcset="assets/img/home/hero-800.avif 800w, assets/img/home/hero-1448.avif 1448w" '
                     'imagesizes="100vw" type="image/avif" fetchpriority="high" media="(min-width: 1024px)">')
    if not noindex:
        lines.append('<script type="speculationrules">{"prefetch":[{"where":{"and":['
                     '{"href_matches":{"pathname":"/*.html","search":""}},'
                     '{"not":{"href_matches":["/brides.html","/join-our-team.html"]}},'
                     '{"not":{"selector_matches":"[data-no-prefetch]"}}]},'
                     '"eagerness":"moderate"}]}</script>')
    return '\n'.join(lines)


# Main nav per the owners' homepage design (2026-10-08):
#   Services v | New Clients | Our Team | Bridal | Gift Cards | Products | About v | Book an appointment
# Services dropdown: (label, file, price spec, price prefix); the first five are the
# homepage service tiles, the rest are listed under "More services".
NAV_SERVICES = [
    ('Hair', 'salon.html', 'range:salon.html#cuts-women', "Women's cuts "),
    ('Spa & Skincare', 'facials.html', 'from:facials.html#focus-facial', 'Facials '),
    ('Nails', 'tips-and-toes.html', 'range:tips-and-toes.html#classic-manicure', 'Manicures '),
    ('Massage', 'massages.html', 'from:massages.html', ''),
    ('Medical Aesthetics', 'slay-aesthetics.html', 'text:With Slay Aesthetics · Mon & Fri', ''),
]
NAV_SERVICES_MORE = [
    ('Waxing', 'hair-removal.html'), ('Brows, Lashes & Makeup', 'makeup-and-eyes.html'),
    ('Spray Tans', 'spray-tans.html'), ("Men's", 'mens-care.html'), ('Bridal', 'brides.html'),
]
NAV_ABOUT = [
    ('Our Story', 'about.html'), ('Careers', 'join-our-team.html'),
    ('Contact', 'contact-us.html'), ('Policies', 'policies.html'),
]
LOGO_IMG = ('<img src="assets/img/brand/logo-header.png" alt="Bellezza &amp; Co. home" '
            'width="{w}" height="{h}">')


def services_panel():
    main = ''.join(f'<li><a href="{f}"><span>{esc(l)}</span><small>{esc(nav_price(s, p))}</small></a></li>'
                   for l, f, s, p in NAV_SERVICES)
    more = ''.join(f'<li><a href="{f}">{esc(l)}</a></li>' for l, f in NAV_SERVICES_MORE)
    return (f'<div class="drop-col"><ul>{main}</ul></div>'
            f'<div class="drop-col drop-more"><h2>More services</h2><ul>{more}'
            f'<li><a href="services.html">All services &amp; prices</a></li></ul></div>')


def about_panel():
    return '<ul>' + ''.join(f'<li><a href="{f}">{esc(l)}</a></li>' for l, f in NAV_ABOUT) + '</ul>'


def part_top(file, page):
    nav = page.get('nav')
    if nav == 'contact':
        nav = 'about'  # Contact sits in the About dropdown
    elif file.startswith('products-'):
        nav = 'products'

    def navlink(key, href, label):
        attr = ' aria-current="page"' if href == file else (' aria-current="true"' if key == nav else '')
        return f'<a href="{href}"{attr}>{label}</a>'

    def drop(key, href, label, panel):
        cur = ' aria-current="page"' if href == file else (' aria-current="true"' if key == nav else '')
        return (f'<li class="nav-drop"><a href="{href}"{cur}>{label}</a>'
                f'<button class="chev" type="button" aria-expanded="false" aria-controls="nav-{key}" hidden>{icon("chevron")}'
                f'<span class="sr-only">Show {label.lower()} links</span></button>'
                f'<div class="nav-panel nav-panel--{key}" id="nav-{key}" hidden>{panel}</div></li>')

    special = next(iter(SITE.get('specials') or []), None)
    book_label = 'Book with Shannon' if page.get('bookOverride', {}).get('cta') == 'slay' else 'Book an appointment'
    header = f"""<header class="site-header" id="top">
<div class="container">
<a class="wordmark" href="index.html">{LOGO_IMG.format(w=274, h=56)}</a>
<nav class="nav-main" aria-label="Main">
<ul>
{drop('services', 'services.html', 'Services', services_panel())}
<li>{navlink('guests', 'new-guests.html', 'New Clients')}</li>
<li>{navlink('team', 'our-team.html', 'Our Team')}</li>
<li>{navlink('bridal', 'brides.html', 'Bridal')}</li>
<li>{navlink('gift', 'gift-cards.html', 'Gift Cards')}</li>
<li>{navlink('products', 'products.html', 'Products')}</li>
{drop('about', 'about.html', 'About', about_panel())}
</ul>
</nav>
<div class="header-actions">
{book_link(page, 'header', cls='btn btn--book header-book', label=book_label)}
<a class="menu-toggle" href="#footer-nav" data-menu-toggle>{icon('menu')}<span>Menu</span></a>
</div>
</div>
</header>"""

    svc_links = ''.join(f'<li><a href="{f}">{esc(l)}<small>{esc(nav_price(s, p))}</small></a></li>'
                        for l, f, s, p in NAV_SERVICES)
    svc_links += ''.join(f'<li><a href="{f}">{esc(l)}</a></li>' for l, f in NAV_SERVICES_MORE)
    about_links = ''.join(f'<li><a href="{f}">{esc(l)}</a></li>' for l, f in NAV_ABOUT)
    special_link = f'<a href="specials.html">{esc(special["title"])}</a>' if special else ''
    drawer = f"""<dialog class="drawer" id="drawer" aria-label="Menu">
<div class="drawer-inner">
<div class="drawer-top"><a class="wordmark" href="index.html">{LOGO_IMG.format(w=215, h=44)}</a><button class="icon-btn" type="button" data-drawer-close autofocus>{icon('close')}<span class="sr-only">Close menu</span></button></div>
{book_link(page, 'drawer')}
<a class="btn btn--outline" href="{SITE['tel']}" data-cta="call" data-placement="drawer">Call {SITE['phone']}</a>
<div class="drawer-extras"><a href="gift-cards.html" data-gift-label="on" hidden data-cta="gift" data-placement="drawer">Send a Bellezza eGift card</a>{special_link}</div>
<h2>Services</h2>
<ul>{svc_links}<li><a href="services.html">All services &amp; prices</a></li></ul>
<h2>Bellezza &amp; Co.</h2>
<ul><li><a href="new-guests.html">New Clients</a></li><li><a href="our-team.html">Our Team</a></li><li><a href="brides.html">Bridal</a></li><li><a href="gift-cards.html">Gift Cards</a></li><li><a href="products.html">Products</a></li></ul>
<h2>About</h2>
<ul>{about_links}</ul>
<h2>Visit</h2>
<p><span class="status" data-status="drawer">Hours &amp; holidays below</span></p>
<address class="addr">{esc(ADDR['street'])}<br>{esc(ADDR['city'])}, {ADDR['region']} {ADDR['zip']}</address>
{hours_table(caption=False)}
<div class="badges"><a href="{U['ios']}"><img src="assets/img/badge-app-store.jpg" alt="Book in the MeGo Client app on the App Store" width="123" height="44" loading="lazy"></a><a href="{U['android']}"><img src="assets/img/badge-google-play.png" alt="Get the MeGo Client app on Google Play" width="150" height="44" loading="lazy"></a></div>
<div class="social drawer-social"><a href="{U['instagram']}" aria-label="Instagram">{icon('instagram')}</a><a href="{U['facebook']}" aria-label="Facebook">{icon('facebook')}</a></div>
</div>
</dialog>"""
    return f'<a class="skip-link" href="#main">Skip to main content</a>\n{header}\n{drawer}'


def part_breadcrumb(file, page):
    crumbs = page.get('crumbs')
    if crumbs is None or file in ('index.html', '404.html'):
        return ''
    items = ['<li><a href="index.html">Home</a></li>']
    items += [f'<li><a href="{c["href"]}">{esc(c["label"])}</a></li>' for c in crumbs]
    items.append(f'<li><span aria-current="page">{esc(LABELS.get(file, page["title"]))}</span></li>')
    return f'<nav class="breadcrumb container" aria-label="Breadcrumb"><ol>{"".join(items)}</ol></nav>'


def booking_microcopy(dark=False):
    return ('<p class="microcopy">Book online 24/7 on our online booking page (Meevo), in the MeGo Client app, '
            'or call us. Changes need 24 hours&rsquo; notice. <a href="policies.html#changes">Policies</a></p>')


def part_bottom(file, page):
    ov = page.get('bookOverride')
    slay = bool(ov) and ov.get('cta') == 'slay'
    band_h = (f"Book with Shannon online, or call {SITE['phone']}." if slay
              else f"Book online any time, or call {SITE['phone']}.")
    band_call = f'<a class="btn btn--outline" href="{SITE["tel"]}" data-cta="call" data-placement="band">Call {SITE["phone"]}</a>'
    band_micro = ('<p class="microcopy">Slay Aesthetics appointments book through our online booking page (Meevo), '
                  'or our front desk can book you. Bellezza gift cards are not accepted at Slay Aesthetics.</p>'
                  if slay else booking_microcopy(True))
    if ov and ov.get('cta') == 'gift':
        band_h = f"Give time at Bellezza, or call {SITE['phone']}."
        band_micro = ('<p class="microcopy">eGift cards are sold on our online gift card page (Meevo) and can&rsquo;t be used '
                      'at Slay Aesthetics. <a href="policies.html#gift-cards">Gift card policy</a></p>')
    band = ''
    # The home page ends on the Visit footer itself (owners' homepage design, 2026-10-08).
    if file not in ('404.html', 'index.html'):
        band = f'''<section class="cta-band dark" aria-labelledby="band-h" data-band>
<div class="container">
<p class="band-status" data-status="band" hidden></p>
<h2 id="band-h">{band_h}</h2>
<div class="band-facts"><p>Today: <span data-today-hours>see our <a href="contact-us.html#hours">hours</a></span></p><p><a href="{esc(U['directions'])}" data-cta="directions" data-placement="band">{esc(ADDR_LINE)}</a></p></div>
<div class="btn-row">{book_link(page, 'band', label=page['bookLabel'] if ov else 'Book an appointment')}{band_call}</div>
{band_micro}
</div>
</section>'''
    year = TODAY.year
    links = [('services.html', 'Services'), ('new-guests.html', 'New Clients'), ('our-team.html', 'Our Team'),
             ('brides.html', 'Bridal'), ('gift-cards.html', 'Gift Cards'), ('products.html', 'Products'),
             ('specials.html', 'Specials'), ('book-online.html', 'Book Online'), ('about.html', 'Our Story'),
             ('join-our-team.html', 'Careers'), ('contact-us.html', 'Contact'), ('policies.html', 'Policies'),
             ('policies.html#privacy', 'Privacy'), ('policies.html#sms-privacy', 'SMS Privacy')]
    link_items = ''.join(f'<li><a href="{h}">{esc(l)}</a></li>' for h, l in links)
    phone_display = '({}) {}'.format(*SITE['phone'].split('-', 1))  # (740) 366-1604, as in the owners' design
    # Exterior photo: assets/img/home/exterior-* from build-images.py (group "home"). OWNER: temporary
    # stand-in (HP-12, AI-edited); swap the source for an original photo before launch.
    photo = ('<figure class="footer-photo"><picture>'
             '<source type="image/avif" srcset="assets/img/home/exterior-600.avif 600w, assets/img/home/exterior-1000.avif 1000w" sizes="(min-width:1024px) 30vw, 100vw">'
             '<source type="image/webp" srcset="assets/img/home/exterior-600.webp 600w, assets/img/home/exterior-1000.webp 1000w" sizes="(min-width:1024px) 30vw, 100vw">'
             '<img src="assets/img/home/exterior-600.jpg" srcset="assets/img/home/exterior-600.jpg 600w, assets/img/home/exterior-1000.jpg 1000w" sizes="(min-width:1024px) 30vw, 100vw" '
             'width="600" height="400" alt="Outside Bellezza &amp; Co. at 206 Deo Drive, with the salon sign" loading="lazy" decoding="async">'
             '</picture></figure>')
    footer = f"""<footer class="site-footer">
<div class="footer-visit">
{photo}
<div class="f-col f-contact">
<h2>Visit Bellezza &amp; Co.</h2>
<address><a href="{esc(U['directions'])}" data-cta="directions" data-placement="footer">{icon('pin')}<span>{esc(ADDR['street'])}<br>{esc(ADDR['city'])}, {ADDR['region']} {ADDR['zip']}</span></a>
<a href="{SITE['tel']}" data-cta="call" data-placement="footer">{icon('phone')}<span>{phone_display}</span></a></address>
<div class="social"><a href="{U['facebook']}" aria-label="Bellezza on Facebook">{icon('facebook')}</a><a href="{U['instagram']}" aria-label="Bellezza on Instagram">{icon('instagram')}</a></div>
</div>
<div class="f-col f-hours">
<h2>Hours</h2>
{hours_table(caption=False)}
<p class="footer-holidays"><a href="policies.html#holidays">Holiday hours</a></p>
</div>
<div class="f-col f-book">
{book_link(page, 'footer', label='Book an appointment')}
<p class="f-small"><a href="contact-us.html">Contact</a><span aria-hidden="true"> · </span><a href="policies.html">Policies</a></p>
</div>
</div>
<div class="footer-bottom">
<nav class="footer-nav" id="footer-nav" aria-label="Footer"><ul>{link_items}</ul></nav>
<p>&copy; {year} Bellezza &amp; Co. (formerly Bellezza Salon and Day Spa) · {esc(SITE['legalName'])} · Ohio salon license <a href="{esc(U['licenseLookup'])}">{SITE['salonLicense']}</a></p>
</div>
</footer>"""
    bar = ''
    if file != '404.html':
        bar = (f'<nav class="bookbar" aria-label="Book or call" data-bookbar data-hidden="true">'
               f'{book_link(page, "bookbar", label=page["bookLabel"])}'
               f'<a class="btn btn--outline" href="{SITE["tel"]}" data-cta="call" data-placement="bookbar" data-call-label>{icon("phone")}Call</a></nav>')
    scripts = f'<script src="{v("assets/js/site.js")}" defer></script>'
    if file in ('brides.html', 'join-our-team.html'):
        scripts += f'\n<script src="{v("assets/js/forms.js")}" defer></script>'
    return '\n'.join(x for x in (band, footer, bar, scripts) if x)


# ------------------------------------------------------------------ Google reviews
def google_rating():
    """'4.8 on Google from 761 reviews, as of October 2026' from site.json, or ''."""
    r = SITE.get('reviews') or {}
    if not (r.get('rating') and r.get('count') and r.get('asOf')):
        return ''
    return f"{r['rating']} on Google from {r['count']:,} reviews, as of {month_year(r['asOf'][:7])}"


def reviews_list(service=None):
    """Published review quotes (word for word, with permission). Optional service filter,
    e.g. <!-- partial:reviews-bridal:start --> shows only the Bridal quotes;
    <!-- partial:reviews-home:start --> shows the quotes marked "home": true."""
    quotes = [q for q in (SITE.get('reviews') or {}).get('quotes', []) if q.get('publish')
              and (service is None or (q.get('home') if service == 'home'
                                       else q.get('service', '').lower() == service))]
    if not quotes:
        return ''
    items = ''.join(f'<li><blockquote><p>&ldquo;{esc(q["text"])}&rdquo;</p></blockquote>'
                    f'<p class="review-meta">{esc(q["name"])} · {esc(q["service"])} · {month_year(q["date"])} · Google</p></li>'
                    for q in quotes)
    return f'<ul class="reviews">{items}</ul>'


# ------------------------------------------------------------------ stamping
def stamp(text, name, content):
    pat = re.compile(r'(<!-- partial:%s:start -->)(.*?)(<!-- partial:%s:end -->)' % (name, name), re.S)
    return pat.sub(lambda m: m.group(1) + '\n' + content + '\n' + m.group(3), text)


def fill_values(text, counts):
    def rng(m):
        val = price_value('range', m.group(2))
        return m.group(1) + (val or m.group(3)) + m.group(4)

    def frm(m):
        val = price_value('from', m.group(2))
        return m.group(1) + (val or m.group(3)) + m.group(4)

    text = re.sub(r'(<span\b[^>]*data-range="([^"]+)"[^>]*>)(.*?)(</span>)', rng, text)
    text = re.sub(r'(<span\b[^>]*data-from="([^"]+)"[^>]*>)(.*?)(</span>)', frm, text)
    for key, n in counts.items():
        text = re.sub(r'(<span\b[^>]*data-count="%s"[^>]*>)[^<]*(</span>)' % re.escape(key),
                      lambda m, n=n: f'{m.group(1)}{n}{m.group(2)}', text)
    asof = SITE['pricesConfirmed']
    text = re.sub(r'<time\b[^>]*data-asof[^>]*>.*?</time>',
                  f'<time class="asof" data-asof datetime="{asof}">Prices as of {month_year(asof)}</time>', text)
    team = SITE['teamUpdated']
    text = re.sub(r'<time\b[^>]*data-team-updated[^>]*>.*?</time>',
                  f'<time data-team-updated datetime="{team}">Team updated {month_year(team)}</time>', text)
    text = re.sub(r'(<span\b[^>]*data-year[^>]*>)[^<]*(</span>)', lambda m: f'{m.group(1)}{TODAY.year}{m.group(2)}', text)
    rating = google_rating()
    if rating:
        text = re.sub(r'(<span\b[^>]*data-google-rating[^>]*>)[^<]*(</span>)',
                      lambda m: f'{m.group(1)}{esc(rating)}{m.group(2)}', text)
    return text


def stamp_js_config():
    path = os.path.join(ROOT, 'assets', 'js', 'site.js')
    if not os.path.exists(path):
        return
    js = open(path, encoding='utf-8').read()
    cfg = {
        'tz': 'America/New_York',
        'hours': {h['short']: [h['opens'], h['closes']] if h['opens'] else None for h in SITE['hours']},
        'holidays': resolve_holidays(TODAY - dt.timedelta(days=1), 400),
        'giftSeasons': gift_windows(),
        'phone': SITE['phone'],
    }
    block = '/* config:start */\n  var CONFIG = ' + json.dumps(cfg, ensure_ascii=False) + ';\n  /* config:end */'
    new = re.sub(r'/\* config:start \*/.*?/\* config:end \*/', lambda m: block, js, flags=re.S)
    if new != js:
        open(path, 'w', encoding='utf-8', newline='\n').write(new)


def gift_windows():
    """Concrete [from, to] ISO date pairs for gift seasons this year and next."""
    out = []
    for year in (TODAY.year, TODAY.year + 1):
        for s in SITE.get('giftSeasons', []):
            if s.get('rule') == 'mothers-day':
                sundays = [dt.date(year, 5, d) for d in range(1, 15) if dt.date(year, 5, d).weekday() == 6]
                md = sundays[1]
                out.append([(md - dt.timedelta(days=s['daysBefore'])).isoformat(), md.isoformat()])
            else:
                out.append([f"{year}-{s['from']}", f"{year}-{s['to']}"])
    return out


def main():
    stamp_js_config()  # first: pages embed site.js's content hash
    counts = team_counts()
    changed = 0
    for file in sorted(PAGES):
        path = os.path.join(ROOT, file)
        if not os.path.exists(path):
            continue
        page = PAGES[file]
        text = open(path, encoding='utf-8').read()
        new = stamp(text, 'head', part_head(file, page))
        new = stamp(new, 'top', part_top(file, page))
        new = stamp(new, 'breadcrumb', part_breadcrumb(file, page))
        new = stamp(new, 'bottom', part_bottom(file, page))
        new = stamp(new, 'hours', hours_table())
        new = stamp(new, 'holidays', holiday_table())
        for name in set(re.findall(r'<!-- partial:(reviews(?:-[a-z]+)?):start -->', new)):
            new = stamp(new, name, reviews_list(name.partition('-')[2] or None))
        new = fill_values(new, counts)
        if 'data-bookbar' in new and 'class="has-bookbar"' not in new:
            new = re.sub(r'<body\b([^>]*)>', lambda m: '<body class="has-bookbar">' if 'class=' not in m.group(1) else m.group(0), new, count=1)
        if new != text:
            open(path, 'w', encoding='utf-8', newline='\n').write(new)
            changed += 1
    write_sitemap()
    print(f'partials: {changed} page(s) updated, team counts {counts}')


def write_sitemap():
    """sitemap.xml from pages.json: every indexable page that exists."""
    urls = []
    for file, page in PAGES.items():
        if page.get('noindex') or not os.path.exists(os.path.join(ROOT, file)):
            continue
        loc = U['site'] if file == 'index.html' else U['site'] + file
        mtime = dt.date.fromtimestamp(os.path.getmtime(os.path.join(ROOT, file))).isoformat()
        urls.append(f'  <url><loc>{loc}</loc><lastmod>{mtime}</lastmod></url>')
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + '\n'.join(urls) + '\n</urlset>\n')
    path = os.path.join(ROOT, 'sitemap.xml')
    old = open(path, encoding='utf-8').read() if os.path.exists(path) else ''
    # only rewrite when the URL set changes, so lastmod churn doesn't dirty every build
    if re.findall(r'<loc>(.*?)</loc>', old) == re.findall(r'<loc>(.*?)</loc>', xml):
        return
    open(path, 'w', encoding='utf-8', newline='\n').write(xml)


if __name__ == '__main__':
    main()
