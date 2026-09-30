"""Stamp the shared page chrome into every page as static HTML.

Usage (normally via build.py):
    python tools/build-partials.py

Each page keeps only its own content. Between these markers the build
writes generated HTML (never edit inside them; the next run overwrites):

    <!-- partial:head:start -->        <title>, meta, canonical, fonts, CSS
    <!-- partial:top:start -->         skip link, bronze header bar, mega panel, menu dialog
    <!-- partial:breadcrumb:start -->  breadcrumb trail (inner pages)
    <!-- partial:hours:start -->       weekly hours table
    <!-- partial:holidays:start -->    upcoming holiday hours (next 12 months)
    <!-- partial:band:start -->        the sand booking band, where a page places it (home);
                                       on every other page the bottom partial carries it
    <!-- partial:bottom:start -->      booking band, footer, scripts

It also fills live values from the page content, so numbers never drift:
    <span data-count="team">          number of team cards on our-team.html
    <span data-count="dept-hair">     team cards whose data-dept includes "hair"
    <span data-range="salon.html#cuts-women">   "$37–60" from that group or item
    <span data-from="facials.html#facials">     "from $55" (lowest price)
    <span data-unit="slay-aesthetics.html#botox">          "$12/unit"
    <span data-level-price="salon.html#cuts-women" data-level="Senior">   "$48"
    <time data-asof>                  "Prices as of September 2026"
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
        'arrow': '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
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
    'index.html': 'Home', 'services.html': 'Services & prices', 'salon.html': 'Hair',
    'tips-and-toes.html': 'Nails', 'massages.html': 'Massage', 'facials.html': 'Facials',
    'hair-removal.html': 'Waxing', 'makeup-and-eyes.html': 'Brows, lashes & makeup',
    'spray-tans.html': 'Spray tans', 'mens-care.html': "Men's", 'brides.html': 'Bridal',
    'slay-aesthetics.html': 'Slay Aesthetics', 'specials.html': 'Specials',
    'book-online.html': 'Book online', 'products.html': 'The boutique',
    'products-dermalogica.html': 'Dermalogica', 'products-ref.html': 'REF', 'products-lakme.html': 'Lakmé',
    'products-voesh.html': 'VOESH', 'products-olaplex.html': 'Olaplex', 'products-smashbox.html': 'Smashbox',
    'products-calecim.html': 'Calecim', 'products-ecru-new-york.html': 'ECRU New York',
    'our-team.html': 'Meet the team', 'about.html': 'Our story', 'new-guests.html': 'New guests',
    'join-our-team.html': 'Careers', 'job-massage-therapist.html': 'Massage therapist',
    'job-nail-therapist.html': 'Nail therapist', 'job-experienced-hair-stylist.html': 'Experienced hair stylist',
    'job-new-talent.html': 'New talent', 'job-internship.html': 'Internship', 'contact-us.html': 'Visit & contact',
    'gift-cards.html': 'Gift cards', 'pick-up-orders.html': 'Pick-up orders', 'policies.html': 'Policies',
    '404.html': 'Page not found', 'thank-you.html': 'Thank you',
}

# Services: (label, file, anchor, price spec, bracket). The named range always
# names its anchor service (DESIGN-OPTIONS section 0: never a bare "Hair $37-60")
# and is stamped from the service page by nav_price(), so it can never drift.
SERVICES = [
    ('Hair', 'salon.html', "Women's cut", 'range:salon.html#cuts-women', 'by level'),
    ('Nails', 'tips-and-toes.html', 'Manicures', 'range:tips-and-toes.html#classic-manicure', 'by level'),
    ('Facials', 'facials.html', 'Facials', 'from:facials.html#focus-facial', 'by level'),
    ('Massage', 'massages.html', 'Relaxation massage', 'range:massages.html#relaxation', '30–75 min'),
    ('Waxing', 'hair-removal.html', 'Waxing', 'from:hair-removal.html', 'by level'),
    ('Brows, lashes & makeup', 'makeup-and-eyes.html', 'Brows, lashes & makeup', 'from:makeup-and-eyes.html#brows', ''),
    ('Spray tans', 'spray-tans.html', 'Spray tans', 'from:spray-tans.html', ''),
    ("Men's", 'mens-care.html', "Men's cut", 'from:salon.html#cuts-men', 'by level'),
    ('Bridal', 'brides.html', 'Bridal style', 'from:brides.html#bridal-hair-style', ''),
    ('Slay Aesthetics', 'slay-aesthetics.html', 'Botox', 'unit:slay-aesthetics.html#botox', 'Slay'),
]
SLAY_LINE = 'Slay Aesthetics · medical aesthetics · Fridays'


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


def unit_value(spec):
    """'slay-aesthetics.html#botox' ("$12 per unit") -> "$12/unit"."""
    frag = _fragment(spec)
    m = frag and re.search(r'<span class="price">(.*?)</span>', frag, re.S)
    if not m:
        return None
    txt = html.unescape(re.sub(r'<[^>]+>', '', m.group(1))).strip()
    return re.sub(r'\s*per\s+unit$', '/unit', txt)


def level_price(spec, level):
    """Price of one level row in a ladder group: ('salon.html#cuts-women', 'Senior') -> '$48'.
    DESIGN-OPTIONS section 0: derived level facts are stamped, never typed."""
    frag = _fragment(spec)
    if frag is None:
        return None
    for li in PRICE_ITEM.findall(frag):
        n = re.search(r'<span class="name">(.*?)</span>(?=<span class="dots")', li, re.S)
        p = re.search(r'<span class="price">(.*?)</span>', li, re.S)
        if not (n and p):
            continue
        name = html.unescape(re.sub(r'<[^>]+>', '', n.group(1))).strip()
        name = re.sub(r'\s+Stylist$', '', name)
        if name == level:
            return html.unescape(re.sub(r'<[^>]+>', '', p.group(1))).strip()
    return None


def nav_price(spec):
    kind, _, arg = spec.partition(':')
    if kind == 'text':
        return arg
    if kind == 'unit':
        return unit_value(arg) or ''
    return price_value(kind, arg) or ''


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
# Option C (Bronze & Sand), docs/DESIGN-OPTIONS.md section C5: a sticky bronze bar
# with the Book capsule at every width, a 4/8 mega panel, a full-screen bronze
# drawer, a sand booking band and a bronze footer. No utility bar, no bottom bar.

# Chrome Book (header, drawer) follows the page's override only on these pages
# (DESIGN-OPTIONS section 0); elsewhere it stays gold Bellezza booking.
CHROME_OVERRIDES = ('slay', 'gift')
# Short chrome labels, so the compact mobile capsule fits beside the logo and Menu.
# The long part stays in the accessible name (visually hidden when narrow).
CHROME_LABELS = {
    None: ('Book', ' now'),
    'slay': ('Book', ' with Slay'),
    'gift': ('eGift card', ''),
}


def book_link(page, placement, cls='btn btn--book', label=None, extra='', chrome=False):
    ov = page.get('bookOverride')
    if ov and (not chrome or ov['cta'] in CHROME_OVERRIDES):
        # an override is never gold: Slay has no gold at all, gift cards are not booking
        cls = cls.replace('btn--book', 'btn--strong')
        lab = label or ov['label']
        ext = ' rel="noopener"' if ov.get('external') else ''
        return (f'<a class="{cls}" href="{esc(ov["href"])}" data-cta="{ov["cta"]}" '
                f'data-placement="{placement}"{ext}{extra}>{lab if "<" in lab else esc(lab)}</a>')
    lab = label or 'Book an appointment'
    return (f'<a class="{cls}" href="{esc(U["book"])}" data-book data-cta="book" data-placement="{placement}"{extra}>'
            f'{lab if "<" in lab else esc(lab)}</a>')


def chrome_book(page, placement):
    ov = page.get('bookOverride') or {}
    key = ov.get('cta') if ov.get('cta') in CHROME_OVERRIDES else None
    short, long = CHROME_LABELS[key]
    if key == 'gift':
        label = '<span class="bk-long">Buy an </span><span class="nocase">e</span>Gift card'
    else:
        label = f'{short}<span class="bk-long">{long}</span>'
    return book_link(page, placement, cls='btn btn--book btn--compact chrome-book', label=label, chrome=True)


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
        '<meta name="theme-color" content="#6a552f">',
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
        f'<link rel="preload" href="{v("assets/fonts/manrope-var-latin.woff2")}" as="font" type="font/woff2" crossorigin>',
        f'<link rel="stylesheet" href="{v("assets/css/styles.css")}">',
    ]
    if file in ('new-guests.html', 'book-online.html'):
        lines.append(f'<meta name="apple-itunes-app" content="app-id={U["iosAppId"]}">')
    if file == 'index.html':
        lines.append('<link rel="preload" as="image" href="assets/img/join/gallery-3-sq-800.avif" '
                     'imagesrcset="assets/img/join/gallery-3-sq-400.avif 400w, assets/img/join/gallery-3-sq-800.avif 800w, '
                     'assets/img/join/gallery-3-sq-900.avif 900w" '
                     'imagesizes="(min-width: 768px) min(44vw, 560px), 100vw" type="image/avif" fetchpriority="high">')
    if not noindex:
        lines.append('<script type="speculationrules">{"prefetch":[{"where":{"and":['
                     '{"href_matches":{"pathname":"/*.html","search":""}},'
                     '{"not":{"href_matches":["/brides.html","/pick-up-orders.html","/join-our-team.html"]}},'
                     '{"not":{"selector_matches":"[data-no-prefetch]"}}]},'
                     '"eagerness":"moderate"}]}</script>')
    return '\n'.join(lines)


def leader_row(href, name, price, cur=''):
    return (f'<li><a href="{href}"{cur}><span class="lr-name">{esc(name)}</span>'
            f'<span class="lr-rule" aria-hidden="true"></span><span class="lr-price">{esc(price)}</span></a></li>')


def services_panel(file):
    rows = ''.join(leader_row(f, anchor, nav_price(spec), ' aria-current="page"' if f == file else '')
                   for label, f, anchor, spec, _ in SERVICES if f != 'slay-aesthetics.html')
    return (f'<div class="nav-panel" id="nav-services" hidden><div class="panel-inner">'
            f'<div class="panel-head"><p class="panel-title">Services &amp; prices</p>'
            f'<p class="bracket">[Prices by level, published for nearly every service]</p>'
            f'<a class="btn btn--strong" href="services.html">All services &amp; prices</a></div>'
            f'<ul class="panel-list">{rows}</ul>'
            f'<p class="panel-slay"><a href="slay-aesthetics.html">Slay Aesthetics</a> · medical aesthetics · Fridays</p>'
            f'</div></div>')


def part_top(file, page):
    nav = page.get('nav')

    def navlink(key, href, label):
        attr = ' aria-current="page"' if href == file else (' aria-current="true"' if key == nav and key in ('services', 'about', 'bridal', 'team', 'guests') else '')
        return f'<a href="{href}"{attr}>{label}</a>'

    services_cur = ' aria-current="page"' if file == 'services.html' else (' aria-current="true"' if nav == 'services' else '')
    logo = ('<a class="brand" href="index.html"><img src="assets/img/brand/logo-on-dark.png" '
            'alt="Bellezza &amp; Co. home" width="786" height="257"></a>')
    header = f'''<header class="site-header" id="top">
<div class="bar">
<div class="cell cell-brand">{logo}</div>
<nav class="cell nav-main" aria-label="Main">
<ul>
<li class="nav-services"><a href="services.html"{services_cur}>Services &amp; prices</a><button class="chev" type="button" aria-expanded="false" aria-controls="nav-services" hidden>{icon('chevron')}<span class="sr-only">Show services</span></button>
{services_panel(file)}</li>
<li>{navlink('team', 'our-team.html', 'Meet the team')}</li>
<li>{navlink('guests', 'new-guests.html', 'New guests')}</li>
<li>{navlink('bridal', 'brides.html', 'Bridal')}</li>
<li>{navlink('about', 'about.html', 'About')}</li>
<li class="nav-gift">{navlink('gift', 'gift-cards.html', 'Gift cards')}</li>
</ul>
</nav>
<div class="cell cell-book">
<a class="header-tel" href="{SITE['tel']}" data-cta="call" data-placement="header">{icon('phone')}{SITE['phone']}</a>
{chrome_book(page, 'header')}
</div>
<div class="cell cell-menu"><a class="menu-toggle" href="#footer-nav" data-menu-toggle>{icon('menu')}<span>Menu</span></a></div>
</div>
</header>'''

    def drow(href, name, small=''):
        cur = ' aria-current="page"' if href == file else ''
        sm = f'<small>{esc(small)}</small>' if small else ''
        return f'<li><a href="{href}"{cur}><span>{esc(name)}</span>{sm}</a></li>'

    def named(label, anchor, spec):
        # the row label names the anchor when they match ("Waxing"), so only the price follows
        text = nav_price(spec) if anchor == label else f'{anchor} {nav_price(spec)}'
        return text + (' · Fridays' if spec.startswith('unit:') else '')

    svc = ''.join(drow(f, label, named(label, anchor, spec)) for label, f, anchor, spec, _ in SERVICES)
    special = next(iter(SITE.get('specials') or []), None)
    drawer = f'''<dialog class="drawer" id="drawer" aria-label="Menu">
<div class="drawer-bar">
<div class="cell cell-brand"><a class="brand" href="index.html"><img src="assets/img/brand/logo-on-dark.png" alt="Bellezza &amp; Co. home" width="786" height="257"></a></div>
<div class="cell cell-book">{chrome_book(page, 'drawer')}</div>
<div class="cell cell-menu"><button class="menu-toggle drawer-close" type="button" data-drawer-close autofocus>{icon('close')}<span>Close</span></button></div>
</div>
<div class="drawer-inner">
<p class="drawer-door"><a href="new-guests.html">New to Bellezza? Start with your first visit</a></p>
<h2 class="drawer-h">Services &amp; prices</h2>
<ul class="drawer-list drawer-services">{svc}{drow('services.html', 'All services & prices')}</ul>
<h2 class="drawer-h">Bellezza &amp; Co.</h2>
<ul class="drawer-list">{drow('our-team.html', 'Meet the team')}{drow('new-guests.html', 'New guests')}{drow('brides.html', 'Bridal')}{drow('about.html', 'About')}</ul>
<a class="btn btn--light drawer-call" href="{SITE['tel']}" data-cta="call" data-placement="drawer">Call {SITE['phone']}</a>
<ul class="drawer-list drawer-more"><li><a href="gift-cards.html"{' aria-current="page"' if file == 'gift-cards.html' else ''} data-cta="gift" data-placement="drawer"><span>Gift cards</span></a></li>{drow('specials.html', 'Specials', special['title'] if special else '')}{drow('products.html', 'The boutique')}{drow('pick-up-orders.html', 'Pick-up orders')}{drow('join-our-team.html', 'Careers')}{drow('policies.html', 'Policies')}{drow('contact-us.html', 'Visit & contact')}</ul>
<h2 class="drawer-h">Hours</h2>
<p class="drawer-status"><span data-status="drawer">Book online 24/7</span></p>
<address class="addr"><a href="{esc(U['directions'])}" data-cta="directions" data-placement="drawer">{esc(ADDR['street'])}, {esc(ADDR['city'])}, {ADDR['region']} {ADDR['zip']}</a></address>
{hours_table(caption=False)}
<div class="badges"><a href="{U['ios']}"><img src="assets/img/badge-app-store.jpg" alt="Download the Bellezza app on the App Store" width="123" height="44" loading="lazy"></a><a href="{U['android']}"><img src="assets/img/badge-google-play.png" alt="Get the Bellezza app on Google Play" width="150" height="44" loading="lazy"></a></div>
<div class="social"><a href="{U['instagram']}" aria-label="Bellezza on Instagram">{icon('instagram')}</a><a href="{U['facebook']}" aria-label="Bellezza on Facebook">{icon('facebook')}</a></div>
</div>
</dialog>'''
    return f'<a class="skip-link" href="#main">Skip to main content</a>\n{header}\n{drawer}'


def part_breadcrumb(file, page):
    crumbs = page.get('crumbs')
    if crumbs is None or file in ('index.html', '404.html'):
        return ''
    items = ['<li><a href="index.html">Home</a></li>']
    items += [f'<li><a href="{c["href"]}">{esc(LABELS.get(c["href"].split("#")[0], c["label"]))}</a></li>' for c in crumbs]
    items.append(f'<li><span aria-current="page">{esc(LABELS.get(file, page["title"]))}</span></li>')
    return f'<nav class="breadcrumb container" aria-label="Breadcrumb"><ol>{"".join(items)}</ol></nav>'


def booking_microcopy(dark=False):
    return ('<p class="microcopy">Book online 24/7 on our online booking page (Meevo), in the Bellezza app, '
            'or call us. Changes need 24 hours&rsquo; notice. <a href="policies.html#changes">Policies</a></p>')


def part_band(file, page):
    """The sand "Book an appointment" band (DESIGN-OPTIONS C6 #11). Stamped at the end of
    every page, or wherever a page places <!-- partial:band:start/end --> (home)."""
    if file == '404.html':
        return ''
    ov = page.get('bookOverride')
    cta = ov.get('cta') if ov else None
    status = '<p class="band-status" data-status="band">Book online 24/7</p>'
    heading = 'Book an appointment'
    call = f'<a class="btn btn--strong" href="{SITE["tel"]}" data-cta="call" data-placement="band">Call {SITE["phone"]}</a>'
    micro = booking_microcopy()
    if cta == 'slay':
        status = '<p class="band-status">Slay Aesthetics · Fridays, 10am–6pm</p>'
        heading = 'Book with Slay Aesthetics'
        call = ''
        micro = ('<p class="microcopy">Booking opens the Slay Aesthetics website. '
                 'Bellezza gift cards are not accepted at Slay Aesthetics.</p>')
    elif cta == 'gift':
        heading = 'Give time at Bellezza'
        call = f'<a class="btn btn--outline" href="{SITE["tel"]}" data-cta="call" data-placement="band">Call {SITE["phone"]}</a>'
        micro = ('<p class="microcopy">eGift cards are sold on our online gift card page (Meevo) and can&rsquo;t be used '
                 'at Slay Aesthetics. <a href="policies.html#gift-cards">Gift card policy</a></p>')
    elif cta:
        heading = page['bookLabel']
        call = f'<a class="btn btn--outline" href="{SITE["tel"]}" data-cta="call" data-placement="band">Call {SITE["phone"]}</a>'
    return f'''<section class="cta-band" aria-labelledby="band-h" data-band>
<div class="container">
{status}
<h2 id="band-h">{esc(heading)}</h2>
<div class="band-actions">
<div class="btn-row">{book_link(page, 'band', label=page['bookLabel'] if ov else 'Book an appointment')}{call}</div>
{micro}
</div>
</div>
</section>'''


def part_bottom(file, page):
    band = '' if '<!-- partial:band:start -->' in read(file) else part_band(file, page)
    svc_links = ''.join(f'<li><a href="{f}">{esc(l)}</a></li>' for l, f, _, _, _ in SERVICES)
    year = TODAY.year
    footer = f'''<footer class="site-footer">
<div class="container">
<div class="footer-grid">
<div class="f-col f-visit">
<h2>Visit</h2>
<address><a href="{esc(U['directions'])}" data-cta="directions" data-placement="footer">{esc(ADDR['street'])}<br>{esc(ADDR['city'])}, {ADDR['region']} {ADDR['zip']}</a><br><a href="{SITE['tel']}" data-cta="call" data-placement="footer">{SITE['phone']}</a></address>
{hours_table(caption=False)}
<p class="footer-holidays"><a href="policies.html#holidays">Holiday hours</a></p>
<p class="footer-bridal">Bridal inquiries: <a href="mailto:{SITE['bridalEmail']}">{SITE['bridalEmail']}</a></p>
</div>
<nav class="footer-nav" id="footer-nav" aria-label="Footer">
<div class="f-col"><h2>Services &amp; prices</h2><ul>{svc_links}<li><a href="services.html">All services &amp; prices</a></li></ul></div>
<div class="f-col"><h2>Plan your visit</h2><ul><li><a href="new-guests.html">New guests</a></li><li><a href="book-online.html">Book online</a></li><li><a href="gift-cards.html">Gift cards</a></li><li><a href="specials.html">Specials</a></li><li><a href="products.html">The boutique</a></li><li><a href="pick-up-orders.html">Pick-up orders</a></li></ul>
<div class="badges"><a href="{U['ios']}"><img src="assets/img/badge-app-store.jpg" alt="Download the Bellezza app on the App Store" width="112" height="40" loading="lazy"></a><a href="{U['android']}"><img src="assets/img/badge-google-play.png" alt="Get the Bellezza app on Google Play" width="137" height="40" loading="lazy"></a></div></div>
<div class="f-col"><h2>About</h2><ul><li><a href="about.html">Our story</a></li><li><a href="our-team.html">Meet the team</a></li><li><a href="join-our-team.html">Careers</a></li><li><a href="policies.html">Policies</a></li><li><a href="policies.html#privacy">Privacy</a></li><li><a href="policies.html#sms-privacy">SMS privacy</a></li><li><a href="contact-us.html">Contact</a></li></ul></div>
</nav>
<a class="footer-logo" href="index.html"><img src="assets/img/brand/logo-on-dark.png" alt="Bellezza &amp; Co., established 2009. Salon, spa, boutique." width="786" height="257" loading="lazy"></a>
</div>
<div class="footer-bottom"><span>&copy; {year} Bellezza &amp; Co. (formerly Bellezza Salon and Day Spa)</span><span class="social"><a href="{U['instagram']}" aria-label="Bellezza on Instagram">{icon('instagram')}</a><a href="{U['facebook']}" aria-label="Bellezza on Facebook">{icon('facebook')}</a></span></div>
</div>
</footer>'''
    scripts = f'<script src="{v("assets/js/site.js")}" defer></script>'
    if file in ('brides.html', 'join-our-team.html', 'pick-up-orders.html'):
        scripts += f'\n<script src="{v("assets/js/forms.js")}" defer></script>'
    return '\n'.join(x for x in (band, footer, scripts) if x)


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

    def unit(m):
        val = unit_value(m.group(2))
        return m.group(1) + (esc(val) if val else m.group(3)) + m.group(4)

    def lvl(m):
        val = level_price(m.group(2), html.unescape(m.group(3)))
        return m.group(1) + (esc(val) if val else m.group(4)) + m.group(5)

    text = re.sub(r'(<span\b[^>]*data-range="([^"]+)"[^>]*>)(.*?)(</span>)', rng, text)
    text = re.sub(r'(<span\b[^>]*data-from="([^"]+)"[^>]*>)(.*?)(</span>)', frm, text)
    # <span data-unit="slay-aesthetics.html#botox">$12/unit</span>
    text = re.sub(r'(<span\b[^>]*data-unit="([^"]+)"[^>]*>)(.*?)(</span>)', unit, text)
    # <span data-level-price="salon.html#cuts-women" data-level="Senior">$48</span>
    text = re.sub(r'(<span\b[^>]*data-level-price="([^"]+)"[^>]*data-level="([^"]+)"[^>]*>)(.*?)(</span>)', lvl, text)
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
        new = stamp(new, 'band', part_band(file, page))
        new = stamp(new, 'hours', hours_table())
        new = stamp(new, 'holidays', holiday_table())
        new = fill_values(new, counts)
        # Option C has no mobile bottom bar (DESIGN-OPTIONS C5): Book lives in the header
        new = new.replace('<body class="has-bookbar">', '<body>')
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
