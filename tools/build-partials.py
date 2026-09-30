"""Stamp the shared page chrome into every page as static HTML.

Usage (normally via build.py):
    python tools/build-partials.py

Each page keeps only its own content. Between these markers the build
writes generated HTML (never edit inside them; the next run overwrites):

    <!-- partial:head:start -->        <title>, meta, canonical, fonts, CSS
    <!-- partial:top:start -->         skip link, umber strip (nav + Book), logo row, drawer
    <!-- partial:breadcrumb:start -->  breadcrumb trail (inner pages)
    <!-- partial:hours:start -->       weekly hours table
    <!-- partial:holidays:start -->    upcoming holiday hours (next 12 months)
    <!-- partial:bottom:start -->      "Ready to book?" window, footer, scripts

It also fills live values from the page content, so numbers never drift:
    <span data-count="team">          number of team cards on our-team.html
    <span data-count="dept-hair">     team cards whose data-dept includes "hair"
    <span data-range="salon.html#cuts-women">   "$37–60" from that group or item
    <span data-from="facials.html#facials">     "from $55" (lowest price)
    <span data-level-price="salon.html#cuts-women@Master">   "$60" (one level's price)
    <span data-level-price="...#gel-manicure-without-removal@madison">  "$49" (that person's level)
    <span data-level-who="hair@Senior">  linked first names of the Senior hair stylists
                                      (from the titles on our-team.html)
    <small data-artist="madison" data-anchor="tips-and-toes.html#gel-manicure-without-removal"
           data-anchor-label="gel manicure">   "senior · gel manicure $49" (or the title)
    <p data-level-line="austyn">      "women's cut $48 · all-over color $75" (team card; empty
                                      without a verified level); add data-level-prefix for
                                      the bio's "At Senior level: ..."
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

# Services menu (Option B, docs/DESIGN-OPTIONS.md B5 and section 0):
# (panel column, panel label, short label, file, price spec, range prefix).
# Every range names its anchor service; the price is read from the page content
# by nav_price(), so it never drifts from the menus.
SERVICES = [
    ('Hair', 'Haircuts, color & extensions', 'Hair', 'salon.html', 'range:salon.html#cuts-women', "women's cut "),
    ('Hair', "Men's cuts & grooming", "Men's", 'mens-care.html', 'from:salon.html#cuts-men', "men's cut "),
    ('Nails', 'Manicures & pedicures', 'Nails', 'tips-and-toes.html', 'range:tips-and-toes.html#classic-manicure', 'manicures '),
    ('Skin & body', 'Dermalogica facials', 'Facials', 'facials.html', 'from:facials.html#focus-facial', 'focus facial '),
    ('Skin & body', 'Massage', 'Massage', 'massages.html', 'range:massages.html#relaxation', 'relaxation massage '),
    ('Skin & body', 'Waxing', 'Waxing', 'hair-removal.html', 'from:hair-removal.html', 'waxing '),
    ('Skin & body', 'Brows, lashes & makeup', 'Brows, lashes & makeup', 'makeup-and-eyes.html', 'from:makeup-and-eyes.html#brows', 'brows, lashes & makeup '),
    ('Skin & body', 'Spray tans', 'Spray tans', 'spray-tans.html', 'from:spray-tans.html', 'spray tans '),
    ('Occasions & medical', 'Bridal hair & makeup', 'Bridal', 'brides.html', 'from:brides.html#bridal-hair-style', 'bridal style '),
    ('Occasions & medical', 'Slay Aesthetics', 'Slay Aesthetics', 'slay-aesthetics.html', 'text:medical aesthetics · Fridays', ''),
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


SLASH_LEVELS = ['Associate', 'Senior', 'Expert']  # default order of "$a / b / c" prices (nail and skin menus)
LEVELS = ['Jr Associate', 'Associate', 'Senior', 'Expert', 'Master']
LEVEL_RE = re.compile(r'\b(Jr Associate|Associate|Senior|Expert|Master)\b')


def _tier_levels(ref):
    """The level order of a slash-price group, read from its p.tier-head
    ("Associate / Senior"), so two-price skin menus map correctly."""
    file, _, frag = ref.partition('#')
    try:
        page = read(file)
    except FileNotFoundError:
        return SLASH_LEVELS
    m = re.search(r'\bid="%s"' % re.escape(frag), page) if frag else None
    if not m:
        return SLASH_LEVELS
    start = page.rfind('class="menu-group', 0, m.end())
    if start < 0:
        return SLASH_LEVELS
    nxt = re.search(r'class="menu-group\b|</section>', page[start + 20:])
    group = page[start: start + 20 + (nxt.start() if nxt else len(page))]
    th = re.search(r'<p class="tier-head"[^>]*>(.*?)</p>', group, re.S)
    if not th:
        return SLASH_LEVELS
    levels = [html.unescape(re.sub(r'<[^>]+>', '', t)).strip() for t in th.group(1).split('/')]
    return levels if all(l in LEVELS for l in levels) else SLASH_LEVELS


def level_price(spec):
    """One level's price, read from the menus (section 0: level facts are derived).

    'salon.html#cuts-women@Jr Associate'                -> '$37'  (ladder row by level)
    'tips-and-toes.html#gel-manicure-without-removal@Senior' -> '$49'  (slash price, by tier-head position)
    'tips-and-toes.html#gel-manicure-without-removal@madison' -> '$49' (a team slug: that person's level)
    """
    ref, _, level = spec.partition('@')
    if level and level not in LEVELS:
        level = (PEOPLE.get(level) or {}).get('level')
    frag = _fragment(ref)
    if frag is None or not level:
        return None
    tiers = _tier_levels(ref)
    for li in PRICE_ITEM.findall(frag):
        m_name = re.search(r'<span class="name">(.*?)<span class="dots">', li, re.S)
        m_price = re.search(r'<span class="price">(.*?)</span>', li, re.S)
        if not (m_name and m_price):
            continue
        name = html.unescape(re.sub(r'<[^>]+>', '', m_name.group(1))).replace(' Stylist', '').strip()
        price = html.unescape(re.sub(r'<[^>]+>', '', m_price.group(1))).strip()
        if level in [p.strip() for p in name.split('/')]:
            return price
        parts = _numbers(price)
        if '/' in price and len(parts) == len(tiers) and level in tiers:
            return f'${_fmt(parts[tiers.index(level)])}'
    return None


# ------------------------------------------------------------------ team levels (section 0: derived, never typed)
def _first_name(name):
    """'Ashley Basham' -> 'Ashley'; 'Taylor F' -> 'Taylor F' (a surname initial stays)."""
    parts = name.split()
    if len(parts) > 1 and re.fullmatch(r'[A-Z]\.?', parts[1]):
        return ' '.join(parts[:2])
    return parts[0] if parts else name


def team_people():
    """Every team card on our-team.html, in page order: slug, name, first name,
    departments, title (span.role) and the level word found in the title."""
    try:
        page = read('our-team.html')
    except FileNotFoundError:
        return {}
    starts = list(re.finditer(r'<li\b[^>]*class="team-item\b[^"]*"[^>]*>', page))
    people = {}
    for i, m in enumerate(starts):
        end = starts[i + 1].start() if i + 1 < len(starts) else page.find('</ul>', m.end())
        card = page[m.end(): end]
        slug = re.search(r'\bid="([^"]+)"', m.group(0))
        if not slug:
            continue
        dept = re.search(r'data-dept="([^"]*)"', m.group(0))
        h3 = re.search(r'<h3\b[^>]*>(.*?)</h3>', card, re.S)
        role = re.search(r'<span class="role">(.*?)</span>', card, re.S)
        name = html.unescape(re.sub(r'<[^>]+>', '', h3.group(1))).strip() if h3 else slug.group(1)
        title = html.unescape(re.sub(r'<[^>]+>', '', role.group(1))).strip() if role else ''
        lvl = LEVEL_RE.search(title)
        people[slug.group(1)] = {
            'slug': slug.group(1), 'name': name, 'first': _first_name(name),
            'depts': dept.group(1).split() if dept else [], 'title': title,
            'level': lvl.group(1) if lvl else None,
            'chair_note': bool(re.search(r'behind the chair one day a week', card, re.I)),
        }
    return people


PEOPLE = team_people()


def level_who(spec):
    """'hair@Senior' -> linked first names of everyone in that department whose
    team title carries that level, in our-team.html order (empty if nobody)."""
    dept, _, level = spec.partition('@')
    names = [p for p in PEOPLE.values() if dept in p['depts'] and p['level'] == level]
    return ', '.join(f'<a href="our-team.html#{p["slug"]}">{esc(p["first"])}</a>' for p in names)


def artist_line(slug, anchor, label):
    """The level line under a "Your artists" frame (B7 #2): "senior · gel manicure $49"
    when the title carries a level and the page's anchor menu prices it; otherwise
    the person's title. Ashley's and Lisa's "behind the chair one day a week"
    comes from their team cards."""
    p = PEOPLE.get(slug)
    if not p:
        return ''
    price = level_price(f'{anchor}@{slug}') if (anchor and p['level']) else None
    if price:
        out = (f'<span class="af-lvl">{esc(p["level"].lower())}</span><span class="af-sep"> · </span>'
               f'<span class="af-price">{esc(label)} {esc(price)}</span>')
    else:
        out = f'<span class="af-lvl">{esc(p["title"])}</span>'
    if p['chair_note']:
        out += '<span class="af-note">behind the chair one day a week</span>'
    return out


# B7 team cards and bios: the anchor prices a person's level buys (section 0 table).
LEVEL_LINE_ANCHORS = {
    'hair': [('salon.html#cuts-women', 'women’s cut'), ('salon.html#color-all-over', 'all-over color')],
    'nails': [('tips-and-toes.html#gel-manicure-without-removal', 'gel manicure')],
}


def level_line(slug, prefix=False):
    """'austyn' -> "women's cut $48 · all-over color $75" (prefix: "At Senior level: ...").
    Empty when the title carries no verified level (Emma and Mia until owner
    question 8) or the department is priced another way (massage by duration)."""
    p = PEOPLE.get(slug)
    if not p or not p['level']:
        return ''
    for dept, anchors in LEVEL_LINE_ANCHORS.items():
        if dept not in p['depts']:
            continue
        parts = []
        for ref, label in anchors:
            price = level_price(f'{ref}@{p["level"]}')
            if price:
                parts.append(f'{esc(label)} {esc(price)}')
        if parts:
            if prefix:  # the bio line stays plain text (build-schema skips it as div.bio-level)
                return f'At {esc(p["level"])} level: ' + ' · '.join(parts)
            return ' · '.join(f'<span>{x}</span>' for x in parts)  # each pair unbroken on narrow cards
    return ''


def nav_price(spec, prefix):
    kind, _, arg = spec.partition(':')
    if kind == 'text':
        return arg
    val = price_value(kind, arg)
    if not val:
        return ''
    return f'{prefix}{val}'  # set in lowercase role type (B2 --b-role)


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
# Option B, House Light (docs/DESIGN-OPTIONS.md B5): a thin sticky umber strip
# carries the caps nav and Book at every width; a plaster logo row scrolls away
# under it; the drawer is a right-hand sheet; every page closes on the inset
# "Ready to book?" window and the umber footer. There is no bottom bar.

def book_link(page, placement, cls='btn btn--book', label=None, label_html=None, extra=''):
    """Book link for a placement. Chrome placements (strip, drawer) keep Bellezza
    booking except on Slay and gift cards (section 0 overrides); body placements
    follow the page's bookOverride."""
    ov = page.get('bookOverride')
    chrome = placement in ('header', 'drawer')
    if ov and (not chrome or ov['cta'] in ('slay', 'gift')):
        cls = cls.replace('btn--book', 'btn--strong')
        tgt = ov['href']
        lab = label_html if label_html else esc(label or ov['label'])
        return (f'<a class="{cls}" href="{esc(tgt)}" data-cta="{ov["cta"]}" data-placement="{placement}"{extra}>'
                f'{lab}</a>')
    lab = label_html if label_html else esc(label or 'Book an appointment')
    return (f'<a class="{cls}" href="{esc(U["book"])}" data-book data-cta="book" data-placement="{placement}"{extra}>'
            f'{lab}</a>')


def egift(text):
    """Caps labels keep the e of eGift lowercase (section 0)."""
    return esc(text).replace('eGift', '<span class="nocase">e</span>Gift')


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
        '<meta name="theme-color" content="#504a40">',
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
        f'<link rel="preload" href="{v("assets/fonts/arsenal-400-latin.woff2")}" as="font" type="font/woff2" crossorigin>',
        f'<link rel="stylesheet" href="{v("assets/css/styles.css")}">',
    ]
    if file in ('new-guests.html', 'book-online.html'):
        lines.append(f'<meta name="apple-itunes-app" content="app-id={U["iosAppId"]}">')
    if file == 'index.html':
        # the first hero frame (Ashley) is the desktop LCP image
        lines.append('<link rel="preload" as="image" href="assets/img/team/ashley-basham-720.avif" '
                     'imagesrcset="assets/img/team/ashley-basham-360.avif 360w, assets/img/team/ashley-basham-540.avif 540w, '
                     'assets/img/team/ashley-basham-720.avif 720w" '
                     'imagesizes="(min-width: 1024px) 30vw, 54vw" type="image/avif" fetchpriority="high" media="(min-width: 1024px)">')
    if not noindex:
        lines.append('<script type="speculationrules">{"prefetch":[{"where":{"and":['
                     '{"href_matches":{"pathname":"/*.html","search":""}},'
                     '{"not":{"href_matches":["/brides.html","/pick-up-orders.html","/join-our-team.html"]}},'
                     '{"not":{"selector_matches":"[data-no-prefetch]"}}]},'
                     '"eagerness":"moderate"}]}</script>')
    return '\n'.join(lines)


def keep_dot(text):
    """A wrapped range never opens a line with its middle dot: the word before " · " and the dot
    stay together ("medical <span class="nowrap">aesthetics ·</span> Fridays"). Characters unchanged."""
    if ' · ' not in text:
        return text
    left, right = text.split(' · ', 1)
    head, _, last = left.rpartition(' ')
    return f'{head}{" " if head else ""}<span class="nowrap">{last} ·</span> {right}'


def services_panel():
    """Mega panel: four hairline-divided columns with centered caps heads (B5)."""
    cols = {}
    for col, label, _short, file, spec, prefix in SERVICES:
        cols.setdefault(col, []).append((label, file, nav_price(spec, prefix)))
    out = []
    for col, items in cols.items():
        lis = ''.join(f'<li><a href="{f}"><span class="pl-name">{esc(l)}</span><span class="pl-range">{keep_dot(esc(p))}</span></a></li>'
                      for l, f, p in items)
        out.append(f'<div class="panel-col"><h2>{esc(col)}</h2><ul>{lis}</ul></div>')
    foot = ('<div class="panel-foot">'
            '<a class="btn btn--outline" href="services.html">All services &amp; prices</a>'
            '<a class="btn btn--outline" href="new-guests.html#levels">How pricing works</a></div>')
    return f'<div class="panel-cols">{"".join(out)}</div>{foot}'


def part_top(file, page):
    nav = page.get('nav')
    ov = page.get('bookOverride') or {}

    def navlink(key, href, label):
        if href == file:
            attr = ' aria-current="page"'
        elif key == nav and key in ('services', 'about', 'bridal', 'team', 'guests', 'contact'):
            attr = ' aria-current="true"'
        else:
            attr = ''
        return f'<a href="{href}"{attr}>{label}</a>'

    special = next(iter(SITE.get('specials') or []), None)
    services_cur = ' aria-current="page"' if file == 'services.html' else (' aria-current="true"' if nav == 'services' else '')

    # strip Book: "Book now" (desktop) / "Book" (phones); the section 0 overrides
    # on Slay and gift cards become non-gold pills with their own label
    if ov.get('cta') == 'slay':
        strip_book = book_link(page, 'header', cls='btn btn--book strip-book',
                               label_html='Book<span class="bk-long"> with Slay</span>',
                               extra=' aria-label="Book with Slay Aesthetics"')
    elif ov.get('cta') == 'gift':
        strip_book = book_link(page, 'header', cls='btn btn--book strip-book',
                               label_html='<span class="bk-long">Buy an </span><span class="nocase">e</span>Gift<span class="bk-long"> card</span>',
                               extra=' aria-label="Buy an eGift card"')
    else:
        strip_book = book_link(page, 'header', cls='btn btn--book strip-book',
                               label_html='Book<span class="bk-long"> now</span>')

    header = f'''<header class="site-header" id="top">
<div class="container strip">
<a class="strip-brand" href="index.html"><img src="assets/img/brand/wordmark-on-dark.png" alt="Bellezza &amp; Co., home" width="369" height="56"></a>
<nav class="nav-main" aria-label="Main">
<ul>
<li class="nav-services"><a href="services.html"{services_cur}>Services &amp; prices</a><button class="chev" type="button" aria-expanded="false" aria-controls="nav-services" hidden>{icon('chevron')}<span class="sr-only">Show services</span></button>
<div class="nav-panel" id="nav-services" hidden><div class="container">{services_panel()}</div></div></li>
<li>{navlink('team', 'our-team.html', 'Meet the team')}</li>
<li>{navlink('guests', 'new-guests.html', 'New guests')}</li>
<li>{navlink('bridal', 'brides.html', 'Bridal')}</li>
<li>{navlink('about', 'about.html', 'Our story')}</li>
<li>{navlink('contact', 'contact-us.html', 'Visit')}</li>
</ul>
</nav>
{strip_book}
<a class="menu-toggle" href="#footer-nav" data-menu-toggle>{icon('menu')}<span>Menu</span></a>
</div>
</header>'''

    logo_row = f'''<div class="logo-row">
<div class="container">
<a class="lockup" href="index.html" aria-label="Bellezza &amp; Co., home"><img src="assets/img/brand/wordmark.png" alt="" width="369" height="56"><span class="lockup-rule"></span><span class="lockup-est" aria-hidden="true"><span>Est.</span><span>2009</span></span></a>
<div class="logo-meta">
<p class="meta-stack"><span class="status-slot" data-status="utility"><a href="contact-us.html#hours">Hours &amp; holidays</a></span><a class="meta-tel" href="{SITE['tel']}" data-cta="call" data-placement="utility">{SITE['phone']}</a><a class="meta-addr" href="{esc(U['directions'])}" data-cta="directions" data-placement="utility">{esc(ADDR['street'])}, {esc(ADDR['city'])}</a></p>
<a class="btn btn--outline new-here" href="new-guests.html" data-cta="new-guests" data-placement="header">New here?</a>
</div>
</div>
</div>'''

    svc_links = ''.join(f'<li><a href="{f}"><span>{esc(short)}</span><small>{keep_dot(esc(nav_price(s, p)))}</small></a></li>'
                        for _, _l, short, f, s, p in SERVICES)
    special_link = f'<a href="specials.html">{esc(special["title"])}</a>' if special else ''
    if ov.get('cta') in ('slay', 'gift'):
        drawer_book = book_link(page, 'drawer', label_html=egift(ov['label']))
    else:
        drawer_book = book_link(page, 'drawer', label='Book an appointment')
    drawer = f'''<dialog class="drawer" id="drawer" aria-label="Menu">
<div class="drawer-inner">
<div class="drawer-top"><a class="drawer-brand" href="index.html"><img src="assets/img/brand/wordmark.png" alt="Bellezza &amp; Co., home" width="369" height="56"></a><button class="icon-btn" type="button" data-drawer-close autofocus>{icon('close')}<span class="sr-only">Close menu</span></button></div>
<div class="drawer-ctas">{drawer_book}
<a class="btn btn--outline" href="{SITE['tel']}" data-cta="call" data-placement="drawer" data-call-label>Call {SITE['phone']}</a></div>
<div class="drawer-extras"><a href="gift-cards.html" data-gift-label="on" hidden data-cta="gift" data-placement="drawer">Send a Bellezza <span class="nocase">e</span>Gift card</a>{special_link}</div>
<nav class="drawer-nav" aria-label="Menu">
<h2>Services &amp; prices</h2>
<ul class="drawer-services">{svc_links}<li><a href="services.html"><span>All services &amp; prices</span></a></li></ul>
<h2>Bellezza &amp; Co.</h2>
<ul><li><a href="our-team.html">Meet the team</a></li><li><a href="new-guests.html">New guests</a></li><li><a href="brides.html">Bridal</a></li><li><a href="about.html">Our story</a></li><li><a href="contact-us.html">Visit</a></li></ul>
<h2>Plan your visit</h2>
<ul class="drawer-small"><li><a href="gift-cards.html">Gift cards</a></li><li><a href="specials.html">Specials</a></li><li><a href="products.html">Boutique</a></li><li><a href="pick-up-orders.html">Pick-up orders</a></li><li><a href="join-our-team.html">Careers</a></li><li><a href="policies.html">Policies</a></li></ul>
</nav>
<h2>Hours</h2>
<p class="drawer-status"><span class="status" data-status="drawer">Hours &amp; holidays below</span></p>
<p class="drawer-today">Today: <span data-today-hours>see the hours below</span></p>
{hours_table(caption=False)}
<address class="drawer-addr"><a href="{esc(U['directions'])}" data-cta="directions" data-placement="drawer">{esc(ADDR['street'])}, {esc(ADDR['city'])}, {ADDR['region']} {ADDR['zip']}</a></address>
<div class="social drawer-social"><a href="{U['instagram']}" aria-label="Bellezza on Instagram">{icon('instagram')}</a><a href="{U['facebook']}" aria-label="Bellezza on Facebook">{icon('facebook')}</a></div>
</div>
</dialog>'''
    return f'<a class="skip-link" href="#main">Skip to main content</a>\n{header}\n{logo_row}\n{drawer}'


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


BAND_SIZES = '(min-width: 1440px) 1280px, 90vw'
BAND_PHOTO = ('<picture class="band-photo">'
              f'<source media="(min-width: 768px)" type="image/avif" srcset="assets/img/team/contact-sheet-1100.avif 1100w, assets/img/team/contact-sheet-1540.avif 1540w" sizes="{BAND_SIZES}" width="1540" height="1173">'
              f'<source media="(min-width: 768px)" type="image/webp" srcset="assets/img/team/contact-sheet-1100.webp 1100w, assets/img/team/contact-sheet-1540.webp 1540w" sizes="{BAND_SIZES}" width="1540" height="1173">'
              f'<source media="(min-width: 768px)" srcset="assets/img/team/contact-sheet-1100.jpg 1100w, assets/img/team/contact-sheet-1540.jpg 1540w" sizes="{BAND_SIZES}" width="1540" height="1173">'
              '<source type="image/avif" srcset="assets/img/team/contact-sheet-800.avif" width="800" height="800">'
              '<source type="image/webp" srcset="assets/img/team/contact-sheet-800.webp" width="800" height="800">'
              '<img src="assets/img/team/contact-sheet-800.jpg" width="800" height="800" alt="" loading="lazy" decoding="async"></picture>')


def _work_print(slug, label, alt):
    s = 'assets/img/work/brows-' + slug
    sizes = '(min-width: 768px) 300px, 44vw'
    return (f'<figure><picture><source type="image/avif" srcset="{s}-400.avif 400w, {s}-470.avif 470w" sizes="{sizes}">'
            f'<source type="image/webp" srcset="{s}-400.webp 400w, {s}-470.webp 470w" sizes="{sizes}">'
            f'<img src="{s}-470.jpg" srcset="{s}-400.jpg 400w, {s}-470.jpg 470w" sizes="{sizes}" width="470" height="260" '
            f'alt="{esc(alt)}" loading="lazy" decoding="async"></picture><span class="ba-label">{label}</span></figure>')


# B7 #7: on makeup-and-eyes the closing window holds the Bella Brows before/after
# as two framed prints (the caption is HTML, not baked into the image).
BAND_WORK = {
    'makeup-and-eyes.html': (
        '<!-- OWNER: please confirm written client consent for this before/after pair (owner question 14), '
        'and tell us who did the service so the caption can name them. -->\n'
        '<figure class="band-work" id="brows-result">'
        + _work_print('before', 'Before', "Close-up of a client's eyebrows before the service: sparse, uneven hairs growing in different directions.")
        + _work_print('after', 'After', 'The same eyebrows after the service: shaped, tinted darker, with the hairs brushed up and set.')
        + '<figcaption>Bella Brows: brow lamination, eyebrow wax and tint. <a href="#bella-brows">Bella Brows on the menu</a></figcaption>'
        '</figure>\n'),
}


def part_bottom(file, page):
    ov = page.get('bookOverride') or {}
    slay = ov.get('cta') == 'slay'
    gift = ov.get('cta') == 'gift'
    band = ''
    if file != '404.html':
        heading = 'Give time at Bellezza' if gift else 'Ready to book?'
        if ov:
            primary = book_link(page, 'band', label_html=egift(page['bookLabel']))
        else:
            primary = book_link(page, 'band', label=page['bookLabel'])
        call = '' if slay else (f'<a class="btn btn--outline" href="{SITE["tel"]}" data-cta="call" '
                                f'data-placement="band">Call {SITE["phone"]}</a>')
        if slay:
            micro = ('<p class="microcopy">Booking opens the Slay Aesthetics website. Bellezza gift cards '
                     'are not accepted at Slay Aesthetics.</p>')
        elif gift:
            micro = ('<p class="microcopy">eGift cards are sold on our online gift card page (Meevo) and can&rsquo;t be used '
                     'at Slay Aesthetics. <a href="policies.html#gift-cards">Gift card policy</a></p>')
        else:
            micro = booking_microcopy(True)
        work = BAND_WORK.get(file, '')
        photo = '' if (slay or work) else BAND_PHOTO
        mod = ' cta-band--plain' if (slay or work) else ''
        band = f'''<section class="cta-band{mod}" aria-labelledby="band-h" data-band>
<div class="container">
<div class="band-window">
{photo}
<div class="band-inner">
{work}<p class="band-status" data-status="band" hidden></p>
<h2 id="band-h">{heading}</h2>
<div class="btn-row">{primary}{call}</div>
{micro}
</div>
</div>
</div>
</section>'''
    svc_links = ''.join(f'<li><a href="{f}">{esc(short)}</a></li>' for _, _l, short, f, _, _ in SERVICES)
    year = TODAY.year
    footer = f'''<footer class="site-footer">
<div class="container">
<div class="footer-lockup-wrap"><img class="footer-lockup" src="assets/img/brand/logo-on-dark.png" alt="Bellezza &amp; Co." width="786" height="257" loading="lazy" decoding="async"><p class="footer-lockup-tag">Est. 2009 &bull; Salon &bull; Spa &bull; Boutique</p></div>
<div class="footer-grid">
<div class="f-visit"><h2>Visit</h2>
<address><a href="{esc(U['directions'])}" data-cta="directions" data-placement="footer">{esc(ADDR['street'])}<br>{esc(ADDR['city'])}, {ADDR['region']} {ADDR['zip']}</a><br><a href="{SITE['tel']}" data-cta="call" data-placement="footer">{SITE['phone']}</a></address>
{hours_table(caption=False)}
<p class="footer-holidays"><a href="policies.html#holidays">Holiday hours</a></p>
<p class="footer-bridal">Bridal inquiries:<br><a href="mailto:{SITE['bridalEmail']}">{SITE['bridalEmail']}</a></p>
</div>
<nav class="footer-nav" id="footer-nav" aria-label="Footer">
<div><h2>Services</h2><ul>{svc_links}<li><a href="services.html">All services &amp; prices</a></li></ul></div>
<div><h2>Plan</h2><ul><li><a href="new-guests.html">New guests</a></li><li><a href="book-online.html">Book online</a></li><li><a href="gift-cards.html">Gift cards</a></li><li><a href="specials.html">Specials</a></li><li><a href="products.html">Boutique</a></li><li><a href="pick-up-orders.html">Pick-up orders</a></li></ul>
<div class="badges"><a href="{U['ios']}"><img src="assets/img/badge-app-store.jpg" alt="Download the Bellezza app on the App Store" width="438" height="156" loading="lazy" decoding="async"></a><a href="{U['android']}"><img src="assets/img/badge-google-play.png" alt="Get the Bellezza app on Google Play" width="461" height="135" loading="lazy" decoding="async"></a></div></div>
<div><h2>About</h2><ul><li><a href="about.html">Our story</a></li><li><a href="our-team.html">Meet the team</a></li><li><a href="join-our-team.html">Careers <small>we&rsquo;re hiring</small></a></li><li><a href="policies.html">Policies</a></li><li><a href="policies.html#privacy">Privacy</a></li><li><a href="policies.html#sms-privacy">SMS privacy</a></li><li><a href="contact-us.html">Contact</a></li></ul></div>
</nav>
</div>
<div class="footer-bottom"><span class="social"><a href="{U['instagram']}" aria-label="Bellezza on Instagram">{icon('instagram')}</a><a href="{U['facebook']}" aria-label="Bellezza on Facebook">{icon('facebook')}</a></span><span>&copy; {year} Bellezza &amp; Co. (formerly Bellezza Salon and Day Spa)</span></div>
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

    def lvl(m):
        val = level_price(m.group(2))
        return m.group(1) + (val or m.group(3)) + m.group(4)

    def who(m):
        return m.group(1) + level_who(m.group(2)) + m.group(4)

    def artist(m):
        tag = m.group(1)
        anchor = re.search(r'data-anchor="([^"]*)"', tag)
        label = re.search(r'data-anchor-label="([^"]*)"', tag)
        line = artist_line(m.group(2), anchor.group(1) if anchor else '',
                           html.unescape(label.group(1)) if label else '')
        return tag + (line or m.group(3)) + m.group(4)

    text = re.sub(r'(<span\b[^>]*data-level-price="([^"]+)"[^>]*>)(.*?)(</span>)', lvl, text)
    text = re.sub(r'(<span\b[^>]*data-level-who="([^"]+)"[^>]*>)(.*?)(</span>)', who, text, flags=re.S)
    text = re.sub(r'(<small\b[^>]*data-artist="([^"]+)"[^>]*>)(.*?)(</small>)', artist, text, flags=re.S)
    text = re.sub(r'(<(p|div)\b[^>]*data-level-line="([^"]+)"[^>]*>)(.*?)(</\2>)',
                  lambda m: m.group(1) + level_line(m.group(3), 'data-level-prefix' in m.group(1)) + m.group(5),
                  text, flags=re.S)
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
        if 'data-bookbar' not in new:  # Option B has no bottom bar: the strip carries Book
            new = new.replace('<body class="has-bookbar">', '<body>', 1)
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
