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
        'pinfill': '<path d="M12 2a8 8 0 0 0-8 8c0 6 8 12 8 12s8-6 8-12a8 8 0 0 0-8-8zm0 11a3 3 0 1 1 0-6 3 3 0 0 1 0 6z" fill="currentColor" stroke="none"/>',
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
    'products-calecim.html': 'Calecim', 'products-ecru-new-york.html': 'ECRU New York',
    'our-team.html': 'Meet the Team', 'about.html': 'Our Story', 'new-guests.html': 'New Guests',
    'join-our-team.html': 'Careers', 'job-massage-therapist.html': 'Massage Therapist',
    'job-nail-therapist.html': 'Nail Therapist', 'job-experienced-hair-stylist.html': 'Experienced Hair Stylist',
    'job-new-talent.html': 'New Talent', 'job-internship.html': 'Internship', 'contact-us.html': 'Visit & Contact',
    'gift-cards.html': 'Gift Cards', 'pick-up-orders.html': 'Pick-up Orders', 'policies.html': 'Policies',
    '404.html': 'Page not found', 'thank-you.html': 'Thank you',
}

# Services list (footer, drawer): (column, label, file, price spec, prefix). Price spec
# is filled from the page content by nav_price(). Option D (DESIGN-OPTIONS §0): every
# range names its anchor service ("Women's cut $37–60", never "Hair $37–60").
SERVICES = [
    ('Hair', 'Hair', 'salon.html', 'range:salon.html#cuts-women', "Women's cut "),
    ('Hair', "Men's", 'mens-care.html', 'from:salon.html#cuts-men', "Men's cut "),
    ('Hair', 'Bridal', 'brides.html', 'from:brides.html#bridal-hair-style', 'Bridal style '),
    ('Nails & Skin', 'Nails', 'tips-and-toes.html', 'range:tips-and-toes.html#classic-manicure', 'Manicures '),
    ('Nails & Skin', 'Facials', 'facials.html', 'from:facials.html#focus-facial', 'Facials '),
    ('Nails & Skin', 'Waxing', 'hair-removal.html', 'from:hair-removal.html', 'Waxing '),
    ('Spa & Beauty', 'Massage', 'massages.html', 'range:massages.html#relaxation', 'Relaxation massage '),
    ('Spa & Beauty', 'Brows, Lashes & Makeup', 'makeup-and-eyes.html', 'from:makeup-and-eyes.html#brows', 'Brows, lashes & makeup '),
    ('Spa & Beauty', 'Spray Tans', 'spray-tans.html', 'from:spray-tans.html', 'Spray tans '),
    ('Medical', 'Slay Aesthetics', 'slay-aesthetics.html', 'text:Medical aesthetics · Fridays', ''),
]

# Option D header panel (D5): four service columns plus the "Not sure?" doors.
NAV_SERVICES = [
    ('Hair', [
        ('Cuts &amp; styling', 'salon.html', 'range:salon.html#cuts-women', "Women's cut "),
        ('Color', 'salon.html#color-all-over', 'range:salon.html#color-all-over', 'All-over color '),
        ("Men&rsquo;s cuts", 'mens-care.html', 'from:salon.html#cuts-men', "Men's cut "),
    ]),
    ('Nails', [
        ('Manicures', 'tips-and-toes.html#manicures', 'range:tips-and-toes.html#classic-manicure', 'Manicures '),
        ('Gel manicures', 'tips-and-toes.html#manicures',
         'range:tips-and-toes.html#gel-manicure-without-removal+tips-and-toes.html#gel-manicure-with-removal', 'Gel manicure '),
        ('Pedicures', 'tips-and-toes.html#pedicures', 'from:tips-and-toes.html#classic-pedicure', 'Pedicures '),
    ]),
    ('Skin &amp; body', [
        ('Facials', 'facials.html', 'from:facials.html#focus-facial', 'Facials '),
        ('Massage', 'massages.html', 'range:massages.html#relaxation', 'Relaxation massage '),
        ('Waxing', 'hair-removal.html', 'from:hair-removal.html', 'Waxing '),
        ('Brows, lashes &amp; makeup', 'makeup-and-eyes.html', 'from:makeup-and-eyes.html#brows', 'Brows, lashes & makeup '),
        ('Spray tans', 'spray-tans.html', 'from:spray-tans.html', 'Spray tans '),
    ]),
    ('Occasions', [
        ('Bridal hair &amp; makeup', 'brides.html', 'from:brides.html#bridal-hair-style', 'Bridal style '),
        ('Special occasion makeup', 'makeup-and-eyes.html#makeup', 'range:makeup-and-eyes.html#special-occasion-makeup', 'Special occasion makeup '),
        ('Slay Aesthetics', 'slay-aesthetics.html', 'text:Medical aesthetics · Fridays', ''),
    ]),
]

# Team panel and drawer (D5): department -> our-team.html#filter-* (count stamped)
TEAM_DEPTS = [
    ('Hair', 'hair', 'dept-hair'), ('Nails', 'nails', 'dept-nails'), ('Skin &amp; waxing', 'skin', 'dept-skin'),
    ('Massage', 'massage', 'dept-massage'), ('Makeup', 'makeup', 'dept-makeup'), ('Bridal', 'bridal', None),
    ('Front desk', 'client-services', 'dept-client-services'),
]


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
    frags = [_fragment(part) for part in spec.split('+')]
    if any(f is None for f in frags):
        return None
    frag = ''.join(frags)
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


def level_price(spec):
    """'salon.html#cuts-women|Senior' -> '$48': the price on the ladder row whose name
    starts with that level (derived level facts, DESIGN-OPTIONS §0)."""
    where, _, level = spec.partition('|')
    frag = _fragment(where)
    if not frag or not level:
        return None
    for li in PRICE_ITEM.findall(frag):
        name = re.search(r'<span class="name">(.*?)</span>', li, re.S)
        price = re.search(r'<span class="price">(.*?)</span>', li, re.S)
        if name and price:
            label = html.unescape(re.sub(r'<[^>]+>', '', name.group(1))).strip()
            if label == level or label.startswith(level + ' '):
                return html.unescape(re.sub(r'<[^>]+>', '', price.group(1))).strip()
    return None


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
# Option D (Open Door) chrome: docs/DESIGN-OPTIONS.md D5. Gold utility bar (desktop and
# tablet) or a 6px gold edge (phones), white header with the framed logo, Services and
# Team panels, gold square Book; a full-screen white menu; a fog closing band; an ink
# footer over a gold band; a phone thumb bar (Menu · Call · Book).

# Placements where a pages.json bookOverride does NOT replace the Bellezza Book
# (DESIGN-OPTIONS §0):
#   slay     none: every placement becomes "Book with Slay" (no gold on that page)
#   gift     the menu keeps Bellezza booking; the chrome Book becomes "Buy an eGift card"
#   bridal   the header and menu keep Bellezza booking; the band and thumb bar go to the inquiry
OVERRIDE_SKIP = {
    'slay': set(),
    'gift': {'drawer'},
    'bridal': {'header', 'drawer'},
}


def nocase_egift(text_html):
    """Keep the "e" of eGift lowercase inside caps labels (DESIGN-OPTIONS §0)."""
    return re.sub(r'\beGift', '<span class="nocase">e</span>Gift', text_html)


def overridden(page, placement):
    ov = page.get('bookOverride')
    return ov if ov and placement not in OVERRIDE_SKIP.get(ov['cta'], {'header', 'drawer'}) else None


def book_link(page, placement, cls='btn btn--book', label=None, extra='', label_html=None):
    ov = overridden(page, placement)
    if ov:
        cls = cls.replace('btn--book', 'btn--strong')
        lab = label_html if label_html is not None else nocase_egift(esc(label or ov['label']))
        rel_ = ' rel="noopener"' if ov.get('external') else ''
        return (f'<a class="{cls}" href="{esc(ov["href"])}" data-cta="{ov["cta"]}" data-placement="{placement}"{rel_}{extra}>'
                f'{lab}</a>')
    lab = label_html if label_html is not None else esc(label or 'Book an appointment')
    return (f'<a class="{cls}" href="{esc(U["book"])}" data-book data-cta="book" data-placement="{placement}"{extra}>'
            f'{lab}</a>')


def chrome_label(page, placement):
    """(label, short label) for the chrome Book: the header ('header') or the thumb bar ('bookbar').
    The short label is used below 400px (D5)."""
    ov = overridden(page, placement)
    cta = ov['cta'] if ov else 'book'
    if cta == 'slay':
        return 'Book with Slay', 'Book with Slay'
    if cta == 'gift':
        return 'Buy an eGift card', 'Buy an eGift card'
    if cta == 'bridal':
        return page['bookLabel'], 'Bridal inquiry'
    if placement == 'header':
        return 'Book now', 'Book now'
    long = page['bookLabel'] if not page.get('bookOverride') else 'Book an appointment'
    return long, page.get('bookLabelShort') or (long if len(long) <= 14 else 'Book now')


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
        '<meta name="theme-color" content="#ffffff">',
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
        f'<link rel="preload" href="{v("assets/fonts/archivo-var-latin.woff2")}" as="font" type="font/woff2" crossorigin>',
    ]
    if file == 'index.html':
        # the one script greeting (D2): 4KB, above the fold, home page only
        lines.append(f'<link rel="preload" href="{v("assets/fonts/allura-greeting.woff2")}" as="font" type="font/woff2" crossorigin>')
    lines.append(f'<link rel="stylesheet" href="{v("assets/css/styles.css")}">')
    if file in ('new-guests.html', 'book-online.html'):
        lines.append(f'<meta name="apple-itunes-app" content="app-id={U["iosAppId"]}">')
    if not noindex:
        lines.append('<script type="speculationrules">{"prefetch":[{"where":{"and":['
                     '{"href_matches":{"pathname":"/*.html","search":""}},'
                     '{"not":{"href_matches":["/brides.html","/pick-up-orders.html","/join-our-team.html"]}},'
                     '{"not":{"selector_matches":"[data-no-prefetch]"}}]},'
                     '"eagerness":"moderate"}]}</script>')
    return '\n'.join(lines)


def services_panel():
    out = []
    for col, items in NAV_SERVICES:
        lis = ''.join(f'<li><a href="{f}"><span>{l}</span><small>{esc(nav_price(spec, pre))}</small></a></li>'
                      for l, f, spec, pre in items)
        out.append(f'<div class="panel-col"><h2>{col}</h2><ul>{lis}</ul></div>')
    out.append('<div class="panel-col panel-doors"><h2>Not sure?</h2><ul>'
               f'<li><a href="{esc(U["quiz"])}" data-cta="quiz" data-placement="nav"><span>Take the match quiz</span>'
               '<small>Find your provider</small></a></li>'
               '<li><a href="new-guests.html"><span>New to Bellezza? Start here</span><small>Your first visit</small></a></li>'
               '<li><a href="services.html"><span>All services &amp; prices</span><small>Every menu on one page</small></a></li>'
               '</ul></div>')
    return ''.join(out)


def dept_count(count):
    return f'<small><span data-count="{count}">0</span></small>' if count else ''


def team_panel():
    lis = [f'<li><a href="our-team.html#filter-{key}"><span>{label}</span>{dept_count(count)}</a></li>'
           for label, key, count in TEAM_DEPTS]
    lis.append('<li class="team-all"><a href="our-team.html"><span>All <span data-count="team">28</span></span>'
               '<small>Meet the team</small></a></li>')
    return ('<div class="container panel-team"><p class="panel-lead">Bios, levels and specialties, by department.</p>'
            f'<ul class="team-depts">{"".join(lis)}</ul></div>')


def part_top(file, page):
    nav = page.get('nav')

    def cur(key, href):
        if href == file:
            return ' aria-current="page"'
        return ' aria-current="true"' if key == nav else ''

    special = next(iter(SITE.get('specials') or []), None)
    special_link = ('<a class="u-wide u-xl" href="specials.html" data-cta="special" data-placement="utility">Specials</a>'
                    if special else '')
    util = f'''<div class="utility">
<div class="container">
<a class="u-addr" href="{esc(U['directions'])}" data-cta="directions" data-placement="utility">{icon('pinfill')}{esc(ADDR['street'])}, {esc(ADDR['city'])}</a>
<span class="u-right">
<span class="status-slot" data-status="utility"><a href="contact-us.html#hours">Hours &amp; holidays</a></span>
<a class="u-tel" href="{SITE['tel']}" data-cta="call" data-placement="utility">{SITE['phone']}</a>
<a class="u-wide" href="{esc(U['quiz'])}" data-cta="quiz" data-placement="utility">Find your match</a>
<span class="u-wide gift-slot"><a href="gift-cards.html" data-gift-label="off" data-cta="gift" data-placement="utility">Gift cards</a><a href="gift-cards.html" data-gift-label="on" hidden data-cta="gift" data-placement="utility">Send an <span class="nocase">e</span>Gift card</a></span>
{special_link}
<a class="u-wide u-xl" href="products.html">Boutique</a>
<a class="u-wide u-ig" href="{U['instagram']}" aria-label="Bellezza on Instagram">{icon('instagram')}</a>
</span>
</div>
</div>'''

    head_label, _ = chrome_label(page, 'header')
    header_book = book_link(page, 'header', cls='btn btn--book header-book', label_html=nocase_egift(esc(head_label)))
    header = f'''<header class="site-header" id="top">
<div class="container">
<a class="brand" href="index.html"><img src="assets/img/brand/logo.png" alt="Bellezza &amp; Co. home" width="786" height="257"></a>
<nav class="nav-main" aria-label="Main">
<ul>
<li class="nav-drop nav-services"><a href="services.html"{cur('services', 'services.html')}>Services</a><button class="chev" type="button" aria-expanded="false" aria-controls="nav-services" hidden>{icon('chevron')}<span class="sr-only">Show services</span></button>
<div class="nav-panel" id="nav-services" hidden><div class="container panel-grid">{services_panel()}</div></div></li>
<li class="nav-drop nav-team"><a href="our-team.html"{cur('team', 'our-team.html')}>Team</a><button class="chev" type="button" aria-expanded="false" aria-controls="nav-team" hidden>{icon('chevron')}<span class="sr-only">Show team departments</span></button>
<div class="nav-panel nav-panel--team" id="nav-team" hidden>{team_panel()}</div></li>
<li><a href="new-guests.html"{cur('guests', 'new-guests.html')}>New guests</a></li>
<li><a href="brides.html"{cur('bridal', 'brides.html')}>Bridal</a></li>
<li><a href="about.html"{cur('about', 'about.html')}>About</a></li>
</ul>
</nav>
<div class="header-actions">
{header_book}
<a class="menu-toggle" href="#footer-nav" data-menu-toggle>{icon('menu')}<span>Menu</span></a>
</div>
</div>
</header>'''

    svc_links = ''.join(f'<li><a href="{f}"><span>{esc(l)}</span><small>{esc(nav_price(s, p))}</small></a></li>'
                        for _, l, f, s, p in SERVICES)
    team_links = ''.join(f'<li><a href="our-team.html#filter-{key}"><span>{label}</span>{dept_count(count)}</a></li>'
                         for label, key, count in TEAM_DEPTS)
    drawer = f'''<dialog class="drawer" id="drawer" aria-label="Menu">
<div class="drawer-inner">
<div class="drawer-top"><a class="brand" href="index.html"><img src="assets/img/brand/logo.png" alt="Bellezza &amp; Co. home" width="786" height="257"></a><button class="icon-btn" type="button" data-drawer-close autofocus>{icon('close')}<span class="sr-only">Close menu</span></button></div>
<div class="drawer-doors">{book_link(page, 'drawer')}<a class="btn btn--outline" href="new-guests.html" data-cta="new-guests" data-placement="drawer">New here? Start here</a></div>
<h2>Services &amp; prices</h2>
<ul class="drawer-list">{svc_links}<li><a href="services.html"><span>All services &amp; prices</span></a></li></ul>
<h2>Team</h2>
<ul class="drawer-list drawer-list--team">{team_links}<li><a href="our-team.html"><span>All <span data-count="team">28</span></span></a></li></ul>
<ul class="drawer-list drawer-list--main"><li><a href="new-guests.html"><span>New guests</span></a></li><li><a href="brides.html"><span>Bridal</span></a></li><li><a href="about.html"><span>About</span></a></li></ul>
<ul class="drawer-more"><li><a href="gift-cards.html" data-gift-label="off">Gift cards</a><a href="gift-cards.html" data-gift-label="on" hidden data-cta="gift" data-placement="drawer">Send an eGift card</a></li><li><a href="specials.html">Specials</a></li><li><a href="products.html">Boutique</a></li><li><a href="pick-up-orders.html">Pick-up orders</a></li><li><a href="join-our-team.html">Careers</a></li><li><a href="policies.html">Policies</a></li><li><a href="contact-us.html">Contact</a></li></ul>
<h2>Hours</h2>
<p class="drawer-status"><span class="status" data-status="drawer">Hours &amp; holidays below</span></p>
{hours_table(caption=False)}
<p class="drawer-visit"><a href="{esc(U['directions'])}" data-cta="directions" data-placement="drawer">{esc(ADDR_LINE)}</a><br><a href="{SITE['tel']}" data-cta="call" data-placement="drawer">{SITE['phone']}</a></p>
<div class="social drawer-social"><a href="{U['instagram']}" aria-label="Bellezza on Instagram">{icon('instagram')}</a><a href="{U['facebook']}" aria-label="Bellezza on Facebook">{icon('facebook')}</a></div>
</div>
</dialog>'''
    return f'<a class="skip-link" href="#main">Skip to main content</a>\n{util}\n{header}\n{drawer}'


def part_breadcrumb(file, page):
    crumbs = page.get('crumbs')
    if crumbs is None or file in ('index.html', '404.html'):
        return ''
    items = ['<li><a href="index.html">Home</a></li>']
    items += [f'<li><a href="{c["href"]}">{esc(c["label"])}</a></li>' for c in crumbs]
    items.append(f'<li><span aria-current="page">{esc(LABELS.get(file, page["title"]))}</span></li>')
    return f'<nav class="breadcrumb container" aria-label="Breadcrumb"><ol>{"".join(items)}</ol></nav>'


def booking_microcopy(dark=False):
    return ('<p class="microcopy">Book online 24/7 on our online booking page (Meevo), in the Bellezza app, '
            'or call us. Changes need 24 hours&rsquo; notice. <a href="policies.html#changes">Policies</a></p>')


def part_bottom(file, page):
    ov = page.get('bookOverride')
    slay = bool(ov) and ov.get('cta') == 'slay'
    band_h = 'Book with Slay Aesthetics on its website.' if slay else f"Book online any time, or call {SITE['phone']}."
    band_call = '' if slay else f'<a class="btn btn--outline" href="{SITE["tel"]}" data-cta="call" data-placement="band">Call {SITE["phone"]}</a>'
    band_micro = ('<p class="microcopy">Booking opens the Slay Aesthetics website. Bellezza gift cards are not accepted at Slay Aesthetics.</p>'
                  if slay else booking_microcopy(True))
    if ov and ov.get('cta') == 'gift':
        band_h = f"Give time at Bellezza, or call {SITE['phone']}."
        band_micro = ('<p class="microcopy">eGift cards are sold on our online gift card page (Meevo) and can&rsquo;t be used '
                      'at Slay Aesthetics. <a href="policies.html#gift-cards">Gift card policy</a></p>')
    band = ''
    # The home page closes with its own Visit & FAQ section and a centered Book (D6 row 10).
    if file not in ('404.html', 'index.html'):
        band = f'''<section class="cta-band" aria-labelledby="band-h" data-band>
<div class="container">
<p class="band-status" data-status="band" hidden></p>
<h2 id="band-h">{band_h}</h2>
<div class="btn-row">{book_link(page, 'band', label=page['bookLabel'] if ov else 'Book an appointment')}{band_call}</div>
<div class="band-facts"><p>Today: <span data-today-hours>see our <a href="contact-us.html#hours">hours</a></span></p><p><a href="{esc(U['directions'])}" data-cta="directions" data-placement="band">{esc(ADDR_LINE)}</a></p></div>
{band_micro}
</div>
</section>'''
    svc_links = ''.join(f'<li><a href="{f}">{esc(l)}</a></li>' for _, l, f, _, _ in SERVICES)
    year = TODAY.year
    footer = f'''<footer class="site-footer dark">
<div class="container footer-grid">
<div class="f-visit">
<h2 class="f-pin">{icon('pinfill')}{esc(ADDR['street'])}</h2>
<address><a href="{esc(U['directions'])}" data-cta="directions" data-placement="footer">{esc(ADDR['street'])}<br>{esc(ADDR['city'])}, {ADDR['region']} {ADDR['zip']}</a><br><a href="{SITE['tel']}" data-cta="call" data-placement="footer">{SITE['phone']}</a></address>
{hours_table()}
<p class="footer-holidays"><a href="policies.html#holidays">Holiday hours</a></p>
<p class="footer-bridal">Bridal inquiries: <a href="mailto:{SITE['bridalEmail']}">{SITE['bridalEmail']}</a></p>
<a class="btn btn--on-ink" href="{esc(U['directions'])}" data-cta="directions" data-placement="footer-button">Get directions</a>
</div>
<nav class="footer-nav" id="footer-nav" aria-label="Footer">
<div><h2>Services &amp; prices</h2><ul>{svc_links}<li><a href="services.html">All services &amp; prices</a></li></ul></div>
<div><h2>Plan your visit</h2><ul><li><a href="new-guests.html">New guests</a></li><li><a href="book-online.html">Book online</a></li><li><a href="gift-cards.html">Gift cards</a></li><li><a href="specials.html">Specials</a></li><li><a href="products.html">The Boutique</a></li><li><a href="pick-up-orders.html">Pick-up orders</a></li></ul>
<div class="badges"><a href="{U['ios']}"><img src="assets/img/badge-app-store.jpg" alt="Download the Bellezza app on the App Store" width="112" height="40" loading="lazy"></a><a href="{U['android']}"><img src="assets/img/badge-google-play.png" alt="Get the Bellezza app on Google Play" width="137" height="40" loading="lazy"></a></div></div>
<div><h2>About</h2><ul><li><a href="about.html">Our story</a></li><li><a href="our-team.html">Meet the team</a></li><li><a href="join-our-team.html">Careers</a></li><li><a href="policies.html">Policies</a></li><li><a href="policies.html#privacy">Privacy</a></li><li><a href="policies.html#sms-privacy">SMS privacy</a></li><li><a href="contact-us.html">Contact</a></li></ul></div>
</nav>
</div>
<div class="footer-band">
<div class="container"><span class="social"><a href="{U['instagram']}" aria-label="Bellezza on Instagram">{icon('instagram')}</a><a href="{U['facebook']}" aria-label="Bellezza on Facebook">{icon('facebook')}</a></span><p>&copy; {year} Bellezza &amp; Co. (formerly Bellezza Salon and Day Spa)</p></div>
</div>
</footer>'''
    bar = ''
    if file != '404.html':
        long, short = chrome_label(page, 'bookbar')
        lab = (f'<span class="bl-long">{nocase_egift(esc(long))}</span><span class="bl-short">{nocase_egift(esc(short))}</span>'
               if short != long else nocase_egift(esc(long)))
        bar = (f'<nav class="bookbar" aria-label="Menu, call and book" data-bookbar="always" data-hidden="false">'
               f'<a class="tb-cell tb-menu" href="#footer-nav" data-menu-toggle>{icon("menu")}<span>Menu</span></a>'
               f'<a class="tb-cell tb-call" href="{SITE["tel"]}" data-cta="call" data-placement="bookbar" data-call-label>{icon("phone")}<span>Call</span></a>'
               f'{book_link(page, "bookbar", cls="btn btn--book tb-book", label_html=lab)}</nav>')
    scripts = f'<script src="{v("assets/js/site.js")}" defer></script>'
    if file in ('brides.html', 'join-our-team.html', 'pick-up-orders.html'):
        scripts += f'\n<script src="{v("assets/js/forms.js")}" defer></script>'
    return '\n'.join(x for x in (band, footer, bar, scripts) if x)


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

    def lvl(m):
        val = level_price(html.unescape(m.group(2)))
        return m.group(1) + (esc(val) if val else m.group(3)) + m.group(4)

    text = re.sub(r'(<span\b[^>]*data-range="([^"]+)"[^>]*>)(.*?)(</span>)', rng, text)
    text = re.sub(r'(<span\b[^>]*data-from="([^"]+)"[^>]*>)(.*?)(</span>)', frm, text)
    text = re.sub(r'(<span\b[^>]*data-level="([^"]+)"[^>]*>)(.*?)(</span>)', lvl, text)
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
        new = stamp(new, 'hours', hours_table())
        new = stamp(new, 'holidays', holiday_table())
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
