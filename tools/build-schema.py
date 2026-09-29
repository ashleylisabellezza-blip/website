"""Generate schema.org JSON-LD for every page from the page's own HTML.

Run after editing prices, staff or job listings (tools/build.py runs it for you):
    python tools/build-schema.py              # stamp every *.html in the project root
    python tools/build-schema.py --root DIR   # stamp the *.html files in DIR instead (used by tests)

Each page gets one <script type="application/ld+json"> block in <head>,
between <!-- schema:start --> and <!-- schema:end --> markers (replaced on
every run, so never hand-edit inside them). Running it twice changes nothing,
except that the holiday hours roll forward as dates pass. What each page gets:

  every page         WebPage + BreadcrumbList, linked to the business by @id.
                     The trail is read from <nav aria-label="Breadcrumb"><ol>
                     when the page has one, so it matches the visible crumbs.
                     dateModified comes from <time data-asof datetime="YYYY-MM">.
  index.html         full business profile (DaySpa/HairSalon/NailSalon) + WebSite
  contact-us.html    full business profile on a ContactPage
  about.html         AboutPage about the business, with founders
  services.html      CollectionPage with an ItemList of the service pages
  service pages      Service + OfferCatalog built from the price lists
  our-team.html      Person for each staff member, linked as employees
  job-*.html         one JobPosting per page (Google Jobs); none on join-our-team
  products.html      ItemList of brands from a.brand-card
  products-*.html    Brand (kept while those pages exist)
  noindex pages      nothing (any old block is removed), e.g. thank-you.html

Holiday hours for the next 12 months are read from tools/site.json
("holidays" and "trickOrTreat"). If that file or section is missing they are
skipped. Set SCHEMA_TODAY=YYYY-MM-DD to pin "today" (tests).

Parser contract (see docs/REDESIGN-BRIEF.md 3.3): .menu-group > h3,
li.price-item > .price-head > span.name + span.price then the description <p>,
.card with an h2-h4 name + span.role, dialog.bio#bio-SLUG, article.job#ID > h2,
a.brand-card. Classes are matched as tokens and attributes in any order, so
ids, modifier classes and extra attributes do not change the output.
Never emits aggregateRating or Review.
"""
import datetime
import html
import json
import os
import re
import sys
from urllib.parse import urljoin, urlsplit

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_JSON = os.path.join(ROOT, 'tools', 'site.json')
SITE = 'https://bellezzaspaonline.com/'
BIZ_ID = SITE + '#business'
SITE_ID = SITE + '#website'
BOOKING = 'https://login.meevo.com/bellezza/ob?locationId=103245'

BIZ_NAME = 'Bellezza & Co.'
BIZ_FORMERLY = 'Bellezza Salon and Day Spa'
BIZ_SLOGAN = 'Salon · Spa · Boutique'

# The award claim is NOT emitted until the owner confirms who runs the vote and
# the most recent year won (brief 10.4, owner question 1). Once confirmed, set:
#   AWARD = 'Voted the Number 1 spa in Licking County every year since 2016'
# and it is added as the business's `award`. Keep it out of descriptions.
AWARD = None

# Default page image when a page's <main> has no image of its own.
DEFAULT_IMAGE = 'assets/img/team/contact-sheet-1540.jpg'

# Date the current job listings went up. Update when a posting changes:
# Google treats postings with old dates as stale.
JOBS_DATE_POSTED = '2026-09-29'

ADDRESS = {
    '@type': 'PostalAddress',
    'streetAddress': '206 Deo Drive',
    'addressLocality': 'Newark',
    'addressRegion': 'OH',
    'postalCode': '43055',
    'addressCountry': 'US',
}

AREA_SERVED = [
    {'@type': 'City', 'name': 'Newark, Ohio'},
    {'@type': 'AdministrativeArea', 'name': 'Licking County, Ohio'},
]

DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

# Regular hours, used when tools/site.json has no "hours" list.
# Day -> (opens, closes); None = closed.
DEFAULT_HOURS = {
    'Monday': ('09:00', '20:00'), 'Tuesday': ('09:00', '20:00'), 'Wednesday': ('12:00', '20:00'),
    'Thursday': ('09:00', '20:00'), 'Friday': ('09:00', '19:00'), 'Saturday': ('08:00', '15:00'),
    'Sunday': None,
}

# Brief 4.15: Newark Trick-or-Treat night closes at 5pm (used only when
# site.json lists trickOrTreat dates but no holiday entry with that rule).
TRICK_OR_TREAT_CLOSES = '17:00'


def hours(days, opens, closes):
    return {'@type': 'OpeningHoursSpecification', 'dayOfWeek': days, 'opens': opens, 'closes': closes}


# ------------------------------------------------------------------ site.json
def load_site():
    """tools/site.json as a dict, or {} if it is missing or unreadable."""
    try:
        with open(SITE_JSON, encoding='utf-8') as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def today():
    pinned = os.environ.get('SCHEMA_TODAY')
    if pinned:
        return datetime.date.fromisoformat(pinned)
    return datetime.date.today()


def regular_hours(site):
    """Day -> (opens, closes) or None, from site.json "hours" or the defaults."""
    rows = site.get('hours')
    if not isinstance(rows, list) or not rows:
        return dict(DEFAULT_HOURS)
    out = {d: None for d in DAYS}
    for row in rows:
        if isinstance(row, dict) and row.get('day') in out and row.get('opens') and row.get('closes'):
            out[row['day']] = (row['opens'], row['closes'])
    return out


def weekly_specs(site):
    """Regular weekly hours; consecutive days with the same hours share one entry."""
    reg = regular_hours(site)
    specs, run = [], []
    for day in DAYS + [None]:
        if run and (day is None or reg.get(day) != reg[run[0]]):
            opens, closes = reg[run[0]]
            specs.append(hours(run if len(run) > 1 else run[0], opens, closes))
            run = []
        if day is not None and reg.get(day):
            run.append(day)
    return specs


def nth_weekday(year, month, weekday, n):
    """n-th (1-based) weekday of a month; n = -1 for the last one. weekday: Monday = 0."""
    if n > 0:
        d = datetime.date(year, month, 1)
        d += datetime.timedelta(days=(weekday - d.weekday()) % 7)
        return d + datetime.timedelta(weeks=n - 1)
    nxt = datetime.date(year + (month == 12), month % 12 + 1, 1)
    d = nxt - datetime.timedelta(days=1)
    return d - datetime.timedelta(days=(d.weekday() - weekday) % 7)


ORDINALS = {'first': 1, 'second': 2, 'third': 3, 'fourth': 4, 'last': -1}
MONTHS = {m.lower(): i for i, m in enumerate(
    ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
     'September', 'October', 'November', 'December'], 1)}


def holiday_date(h, year, site):
    """Date of holiday entry `h` in `year`, or None if it cannot be resolved."""
    rule = str(h.get('rule') or '').lower()
    try:
        if rule == 'trick-or-treat':
            raw = (site.get('trickOrTreat') or {}).get(str(year))
            return datetime.date.fromisoformat(raw) if raw else None
        if rule:
            # "last-monday-may", "first-monday-september" (month may be abbreviated: "sep")
            m = re.fullmatch(r'(first|second|third|fourth|last)-(monday|tuesday|wednesday|thursday|friday|'
                             r'saturday|sunday)-([a-z]{3,})', rule)
            month = next((num for full, num in MONTHS.items() if m and full.startswith(m.group(3))), None)
            if not month:
                return None
            weekday = DAYS.index(m.group(2).capitalize())
            return nth_weekday(year, month, weekday, ORDINALS[m.group(1)])
        return datetime.date(year, int(h['month']), int(h['day']))
    except (KeyError, TypeError, ValueError):
        return None


def holiday_specs(site=None, start=None):
    """Special-hours entries for every holiday in the 12 months from `start`.

    Full-day closures are 00:00-00:00; early closings keep that weekday's
    regular opening time. A holiday on a day we are closed anyway is skipped,
    and so is an early close that is not earlier than the regular close.
    """
    site = load_site() if site is None else site
    entries = site.get('holidays')
    if not isinstance(entries, list) or not entries:
        return []
    entries = [h for h in entries if isinstance(h, dict)]
    if site.get('trickOrTreat') and not any(str(h.get('rule', '')).lower() == 'trick-or-treat' for h in entries):
        entries.append({'name': 'Trick-or-Treat night', 'rule': 'trick-or-treat', 'closes': TRICK_OR_TREAT_CLOSES})
    start = start or today()
    try:
        end = start.replace(year=start.year + 1)
    except ValueError:  # 29 February
        end = start.replace(year=start.year + 1, day=28)
    reg = regular_hours(site)
    found = {}
    for year in (start.year, start.year + 1):
        for h in entries:
            d = holiday_date(h, year, site)
            if not d or not (start <= d < end):
                continue
            regular = reg.get(DAYS[d.weekday()])
            if not regular:
                continue
            if h.get('closed'):
                opens, closes = '00:00', '00:00'
            elif h.get('closes'):
                opens, closes = regular[0], str(h['closes'])
                if closes >= regular[1]:
                    continue
                if closes <= opens:  # closes before we would open: closed all day
                    opens, closes = '00:00', '00:00'
            else:
                continue
            iso = d.isoformat()
            # Two entries on one date (should not happen): keep the shorter day.
            rank = '' if closes == '00:00' else closes  # a full-day closure ranks shortest
            if iso not in found or rank < ('' if found[iso][1] == '00:00' else found[iso][1]):
                found[iso] = (opens, closes)
    return [{'@type': 'OpeningHoursSpecification', 'opens': o, 'closes': c, 'validFrom': d, 'validThrough': d}
            for d, (o, c) in sorted(found.items())]


# ------------------------------------------------------------------ business
FOUNDERS = [
    {'@type': 'Person', '@id': SITE + 'our-team.html#lisa-jeffries', 'name': 'Lisa Jeffries'},
    {'@type': 'Person', '@id': SITE + 'our-team.html#ashley-basham', 'name': 'Ashley Basham'},
]


def business_full():
    site = load_site()
    node = {
        '@type': ['DaySpa', 'HairSalon', 'NailSalon'],
        '@id': BIZ_ID,
        'name': BIZ_NAME,
        'alternateName': BIZ_FORMERLY,
        'slogan': BIZ_SLOGAN,
        'description': ('Full-service salon, spa and boutique in Newark, Ohio offering hair, color and '
                        'extensions, manicures and pedicures, massage, facials, waxing, brows and lashes, '
                        'makeup, spray tans and bridal services.'),
        'url': SITE,
        'logo': {'@type': 'ImageObject', 'url': SITE + 'assets/img/logo.png', 'width': 786, 'height': 257},
        'image': [SITE + 'assets/img/team/contact-sheet-1540.jpg', SITE + 'assets/img/about/team-group-1120.jpg',
                  SITE + 'assets/img/logo.png'],
        'telephone': '+1-740-366-1604',
        'address': ADDRESS,
        'geo': {'@type': 'GeoCoordinates', 'latitude': 40.08631, 'longitude': -82.422132},
        'hasMap': 'https://www.google.com/maps/search/?api=1&query=206+Deo+Drive+Newark+OH+43055',
        'openingHoursSpecification': weekly_specs(site) + holiday_specs(site),
        'priceRange': '$$',
        'currenciesAccepted': 'USD',
        'foundingDate': '2009',
        'founder': [dict(f) for f in FOUNDERS],
        'areaServed': AREA_SERVED,
        'contactPoint': [
            {'@type': 'ContactPoint', 'contactType': 'customer service', 'telephone': '+1-740-366-1604',
             'areaServed': 'US', 'availableLanguage': 'English'},
            {'@type': 'ContactPoint', 'contactType': 'bridal inquiries', 'email': 'dsabo@bellezzaspaonline.com'},
        ],
        'sameAs': [
            'https://www.facebook.com/BellezzaSpaOnline',
            'https://instagram.com/bellezza_newark',
            'https://apps.apple.com/us/app/bellezza-salon-day-spa/id1314312155',
            'https://play.google.com/store/apps/details?id=com.webappclouds.bellezzaspa',
        ],
        'potentialAction': {
            '@type': 'ReserveAction',
            'name': 'Book an appointment',
            'target': {'@type': 'EntryPoint', 'urlTemplate': BOOKING,
                       'actionPlatform': ['http://schema.org/DesktopWebPlatform',
                                          'http://schema.org/MobileWebPlatform']},
        },
        'hasOfferCatalog': {
            '@type': 'OfferCatalog',
            'name': 'Salon & Spa Services',
            'itemListElement': [
                {'@type': 'OfferCatalog', 'name': name, 'url': SITE + slug}
                for name, slug in SERVICE_PAGES.items()
            ],
        },
    }
    if AWARD:
        node['award'] = AWARD
    return node


def business_ref():
    """Short copy of the business for pages that only need to point at it."""
    return {
        '@type': ['DaySpa', 'HairSalon', 'NailSalon'],
        '@id': BIZ_ID,
        'name': BIZ_NAME,
        'url': SITE,
        'telephone': '+1-740-366-1604',
        'address': ADDRESS,
        'image': SITE + 'assets/img/logo.png',
        'priceRange': '$$',
    }


# Page file -> Service name
SERVICE_PAGES = {
    'Bridal Hair & Makeup': 'brides.html',
    'Hair Salon': 'salon.html',
    'Manicures & Pedicures': 'tips-and-toes.html',
    'Massage': 'massages.html',
    'Brows, Lashes & Makeup': 'makeup-and-eyes.html',
    'Facials': 'facials.html',
    'Waxing & Hair Removal': 'hair-removal.html',
    'Spray Tans': 'spray-tans.html',
    "Men's Grooming": 'mens-care.html',
    'Aesthetic Injectables & Weight Loss': 'slay-aesthetics.html',
}
SERVICE_BY_FILE = {v: k for k, v in SERVICE_PAGES.items()}

SKIP = {'404.html', 'PAGE-TEMPLATE.html'}


# ------------------------------------------------------------------ markup helpers
ATTR = re.compile(r'''([^\s=/>"']+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>"']+)))?''')


def attrs(tag):
    """Attributes of an opening tag string, as a dict (values entity-decoded)."""
    inner = re.sub(r'^<\s*[\w-]+|/?>$', '', tag)
    out = {}
    for m in ATTR.finditer(inner):
        val = next((g for g in m.groups()[1:] if g is not None), '')
        out.setdefault(m.group(1).lower(), html.unescape(val))
    return out


def has_class(tag_attrs, cls):
    return cls in tag_attrs.get('class', '').split()


def tags(page, tag, cls=None, **want):
    """Yield (match, attrs) for every opening <tag ...> with class token `cls` and the
    given attribute values. Keyword names map to attributes with '_' -> '-'
    (aria_label='Breadcrumb'); True means "present" (data_asof=True)."""
    for m in re.finditer(r'<%s\b[^>]*>' % tag, page, re.I):
        a = attrs(m.group(0))
        if cls and not has_class(a, cls):
            continue
        ok = True
        for key, val in want.items():
            key = key.replace('_', '-')
            if val is True:
                ok = ok and key in a
            else:
                ok = ok and a.get(key) == val
        if ok:
            yield m, a


def elements(page, tag, cls=None, **want):
    """Yield (match, attrs, inner_html) for each matching element. The element ends at
    the first </tag>, so it must not contain another <tag> (parser contract)."""
    close = re.compile(r'</%s\s*>' % tag, re.I)
    for m, a in tags(page, tag, cls, **want):
        end = close.search(page, m.end())
        if end:
            yield m, a, page[m.end():end.start()]


def text(fragment):
    """Strip tags and decode entities."""
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', fragment))).strip()


def meta(page, name):
    for _, a in tags(page, 'meta', name=name):
        return a.get('content', '')
    return ''


def title_of(page):
    """<title> text; falls back to the h1 (a page whose head partial is not stamped yet)."""
    m = re.search(r'<title\b[^>]*>(.*?)</title>', page, re.S)
    if m:
        return text(m.group(1))
    m = re.search(r'<h1\b[^>]*>(.*?)</h1>', page, re.S)
    return text(m.group(1)) if m else ''


def h1_of(page):
    m = re.search(r'<h1\b[^>]*>(.*?)</h1>', page, re.S)
    return text(m.group(1)) if m else title_of(page).split('|')[0].strip()


def heading(fragment, levels='2-4'):
    m = re.search(r'<h([%s])\b[^>]*>(.*?)</h\1>' % levels, fragment, re.S)
    return text(m.group(2)) if m else ''


def local_asset(src):
    """'assets/img/x.jpg?v=1a2b3c4d' -> 'assets/img/x.jpg' (cache-busting query dropped)."""
    return src.split('?', 1)[0].split('#', 1)[0]


IMG_SRC = re.compile(r'<img\b[^>]*?(?<![\w-])src="([^"]+)"', re.S)


def main_of(page):
    """The page's <main> content (after <main ...>, cut at </main>); the whole page if it has none."""
    main = re.split(r'<main\b[^>]*>', page, maxsplit=1)[-1]
    return re.split(r'</main\s*>', main, maxsplit=1)[0]


def first_image(page):
    main = main_of(page)
    for src in IMG_SRC.findall(main):
        src = local_asset(src)
        if src.startswith('assets/img/') and not src.startswith('assets/img/badge'):
            return SITE + src
    return SITE + DEFAULT_IMAGE


def abs_url(base, href):
    """Resolve a page-relative href to an absolute site URL (index.html -> root)."""
    u = urljoin(base, href.strip())
    parts = urlsplit(u)
    if parts.path.endswith('/index.html'):
        u = u.replace('/index.html', '/', 1)
    return u


# ------------------------------------------------------------------ prices
LEVEL_OR_TIME = re.compile(r'(stylist|\bmin(?:ute)?s?\b|investment determined)', re.I)


def price_spec(raw):
    """'$31 / 37 / 40' -> min/max range, '$75+' -> minimum, '$12 per unit' -> unit price.
    '$$', 'Consultation' and anything without a number -> None (no price emitted)."""
    if re.fullmatch(r'\s*\$\$\s*', raw) or re.search(r'consult', raw, re.I):
        return None
    nums = [float(n) for n in re.findall(r'\d+(?:\.\d+)?', raw.replace(',', ''))]
    if not nums:
        return None
    fmt = lambda n: int(n) if n == int(n) else n
    unit = re.search(r'(per unit|/\s*month|/\s*1\s*ml)', raw, re.I)
    if unit:
        label = {'per unit': 'per unit'}.get(unit.group(1).lower(), unit.group(1).replace('/', 'per').strip())
        return {'@type': 'UnitPriceSpecification', 'price': fmt(nums[0]), 'priceCurrency': 'USD',
                'unitText': re.sub(r'\s+', ' ', label)}
    spec = {'@type': 'PriceSpecification', 'priceCurrency': 'USD'}
    if len(nums) == 1 and not raw.strip().endswith('+'):
        spec['price'] = fmt(nums[0])
    else:
        spec['minPrice'] = fmt(min(nums))
        if len(nums) > 1:
            spec['maxPrice'] = fmt(max(nums))
    return spec


def balanced_inner(fragment, start, tag):
    """Inner HTML from `start` (just after an opening <tag>) to its matching </tag>,
    counting nested <tag>s (e.g. span.name > span.lvl-suffix). '' if unclosed."""
    depth = 1
    for m in re.finditer(r'<(/?)%s\b[^>]*>' % tag, fragment[start:], re.I):
        depth += -1 if m.group(1) else 1
        if depth == 0:
            return fragment[start:start + m.start()]
    return ''


def span_text(fragment, cls):
    for m, _ in tags(fragment, 'span', cls):
        return text(balanced_inner(fragment, m.end(), 'span'))
    return ''


def price_catalog(page, service_name):
    """Build OfferCatalogs from every .menu-group on the page."""
    starts = [m.start() for m, _ in tags(page, 'div', 'menu-group')]
    groups = []
    for i, start in enumerate(starts):
        block = page[start:starts[i + 1] if i + 1 < len(starts) else len(page)]
        block = block[block.index('>') + 1:]
        m_h3 = re.search(r'<h3\b[^>]*>(.*?)</h3>', block, re.S)
        if not m_h3:
            continue
        group = text(m_h3.group(1))
        intro = ''
        m_intro = re.match(r'\s*<p\b([^>]*)>(.*?)</p>', block[m_h3.end():], re.S)
        if m_intro and set(attrs('<p' + m_intro.group(1) + '>').get('class', '').split()) & {'center', 'group-intro'}:
            intro = text(m_intro.group(2))
        offers = []
        for _, _, li in elements(block, 'li', 'price-item'):
            name = span_text(li, 'name')
            price = span_text(li, 'price')
            desc = ''
            head = next(tags(li, 'div', 'price-head'), None)
            if head:
                close = li.find('</div>', head[0].end())
                rest = li[close + 6:] if close >= 0 else ''
                m_desc = re.search(r'<p\b(?![^>]*class="[^"]*\bnote\b)[^>]*>(.*?)</p>', rest, re.S)
                desc = text(m_desc.group(1)) if m_desc else ''
            # Rows like "Senior Stylist $48" or "60 Minutes $70" are levels of
            # the group's service, so name the offer "<group> (<level>)".
            if name.lower().startswith('investment'):  # "Investment Determined at Consultation"
                svc_name, svc_desc = group, intro
            elif LEVEL_OR_TIME.search(name):
                svc_name, svc_desc = f'{group} ({name})', intro
            else:
                svc_name, svc_desc = name, desc
            service = {'@type': 'Service', 'name': svc_name}
            if svc_desc:
                service['description'] = svc_desc
            offer = {'@type': 'Offer', 'itemOffered': service}
            spec = price_spec(price)
            if spec:
                offer['priceSpecification'] = spec
            offers.append(offer)
        if offers:
            groups.append({'@type': 'OfferCatalog', 'name': group, 'itemListElement': offers})
    return {'@type': 'OfferCatalog', 'name': service_name, 'itemListElement': groups}


# ------------------------------------------------------------------ page parts
def page_crumbs(page, url):
    """[(name, url)] from <nav aria-label="Breadcrumb"><ol>, or None if absent."""
    for _, _, nav in elements(page, 'nav', aria_label='Breadcrumb'):
        ol = re.search(r'<ol\b[^>]*>(.*?)</ol>', nav, re.S)
        if not ol:
            continue
        items = []
        for li_attrs, li in re.findall(r'<li\b([^>]*)>(.*?)</li>', ol.group(1), re.S):
            name = text(li)
            if not re.search(r'\w', name) or attrs('<li' + li_attrs + '>').get('aria-hidden') == 'true':
                continue  # separators
            link = next(tags(li, 'a', href=True), None)
            href = link[1]['href'] if link else ''
            items.append((name, abs_url(url, href) if href and not href.startswith('#') else url))
        if items:
            return items
    return None


def breadcrumbs(url, name, parent=None, page=None):
    items = page_crumbs(page, url) if page else None
    if not items:
        items = [('Home', SITE)]
        if parent:
            items.append(parent)
        if url != SITE:
            items.append((name, url))
    return {
        '@type': 'BreadcrumbList',
        '@id': url + '#breadcrumb',
        'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': u}
                            for i, (n, u) in enumerate(items)],
    }


def date_modified(page):
    """'YYYY-MM' or 'YYYY-MM-DD' from <time data-asof datetime="...">."""
    for _, a in tags(page, 'time', data_asof=True):
        dt = a.get('datetime', '').strip()
        if re.fullmatch(r'\d{4}-\d{2}(-\d{2})?', dt):
            return dt
    return ''


def webpage(url, page, kind='WebPage', **extra):
    node = {
        '@type': kind,
        '@id': url + '#webpage',
        'url': url,
        'name': title_of(page),
        'isPartOf': {'@id': SITE_ID},
        'about': {'@id': BIZ_ID},
        'breadcrumb': {'@id': url + '#breadcrumb'},
        'inLanguage': 'en-US',
        'primaryImageOfPage': {'@type': 'ImageObject', 'url': first_image(page)},
    }
    desc = meta(page, 'description')
    if desc:
        node['description'] = desc
    modified = date_modified(page)
    if modified:
        node['dateModified'] = modified
    node.update(extra)
    return node


def team_people(page, url):
    """Person nodes from .card elements (div or a) on the team page."""
    people = []
    # div.card and a.card (Shannon's card links to the Slay page), in document order
    cards = sorted([(m.start(), inner) for m, _, inner in elements(page, 'div', 'card')] +
                   [(m.start(), inner) for m, _, inner in elements(page, 'a', 'card')])
    for _, card in cards:
        pname = heading(card)
        if not pname:
            continue
        role = span_text(card, 'role')
        if not role:
            first = re.search(r'<span\b(?![^>]*class="[^"]*\bsr-only\b)[^>]*>(.*?)</span>', card, re.S)
            role = text(first.group(1)) if first else ''
        m_img = IMG_SRC.search(card)
        if not m_img:
            continue
        img = local_asset(m_img.group(1))
        slug = re.sub(r'-\d+$', '', os.path.splitext(os.path.basename(img))[0])
        person = {'@type': 'Person', '@id': url + '#' + slug, 'name': pname, 'jobTitle': role,
                  'image': SITE + img, 'worksFor': {'@id': BIZ_ID}}
        if slug == 'shannon-francis':  # Slay Aesthetics provider, not Bellezza staff (brief 5.3, owner Q11)
            person['worksFor'] = {'@type': 'MedicalBusiness', '@id': 'https://www.slay-aesthetics.com/#business',
                                  'name': 'Slay Aesthetics & Wellness', 'url': 'https://www.slay-aesthetics.com'}
        for _, _, dlg in elements(page, 'dialog', 'bio', id='bio-' + slug):
            bio = re.search(r'<span\b[^>]*class="[^"]*\brole\b[^"]*"[^>]*>.*?</span>\s*<p\b[^>]*>(.*?)</p>', dlg, re.S)
            if bio:
                person['description'] = text(bio.group(1))
            break
        ig = re.search(r'href="(https://www\.instagram\.com/[^"]+)"', card)
        if ig:
            person['sameAs'] = [ig.group(1)]
        people.append(person)
    return people


# Only employment types the job copy actually states (the massage role says
# full-time or part-time; an internship is inherently INTERN). Others are left
# out rather than guessed; add them here once the owner confirms (brief Q12).
JOB_TYPES = {'massage-therapist': ['FULL_TIME', 'PART_TIME'], 'internship': ['INTERN']}


def job_postings(page, url):
    out = []
    for _, a, body in elements(page, 'article', 'job'):
        job_id = a.get('id')
        m_title = re.search(r'<h2\b[^>]*>(.*?)</h2>', body, re.S)
        if not job_id or not m_title:
            continue
        desc_html = re.sub(r'<h2\b[^>]*>.*?</h2>|<a\b[^>]*class="[^"]*\bbtn\b[^"]*"[^>]*>.*?</a>', '', body,
                           flags=re.S)
        desc_html = re.sub(r'\s+', ' ', html.unescape(desc_html)).strip()
        out.append({
            '@type': 'JobPosting',
            '@id': url + '#' + job_id,
            'title': text(m_title.group(1)),
            'description': desc_html,
            'datePosted': JOBS_DATE_POSTED,
            'hiringOrganization': {'@type': 'Organization', 'name': BIZ_NAME, 'sameAs': SITE,
                                   'logo': SITE + 'assets/img/logo.png'},
            'jobLocation': {'@type': 'Place', 'address': ADDRESS},
            'industry': 'Beauty and personal care',
            'directApply': True,
            'url': url + '#' + job_id,
        })
        if job_id in JOB_TYPES:
            out[-1]['employmentType'] = JOB_TYPES[job_id]
    return out[:1]  # one JobPosting per job page


def brand_list(page, url):
    items = []
    for _, a, inner in elements(page, 'a', 'brand-card'):
        href = a.get('href', '')
        if not href:
            continue
        name = heading(inner)
        m_img = next(tags(inner, 'img'), None)
        if not name and m_img:
            name = re.sub(r'\s+logo$', '', m_img[1].get('alt', ''), flags=re.I).strip()
        if not name:
            continue
        link = abs_url(url, href)
        brand = {'@type': 'Brand', 'name': name}
        src = local_asset(m_img[1].get('src', '')) if m_img else ''
        if src:
            brand['logo'] = SITE + src
        brand['url'] = link
        items.append({'@type': 'ListItem', 'position': len(items) + 1, 'url': link, 'item': brand})
    return items


# ------------------------------------------------------------------ page builders
def build(fname, page):
    url = SITE if fname == 'index.html' else SITE + fname
    name = h1_of(page)
    graph = []

    if fname == 'index.html':
        graph += [
            {'@type': 'WebSite', '@id': SITE_ID, 'url': SITE, 'name': BIZ_NAME,
             'alternateName': BIZ_FORMERLY, 'publisher': {'@id': BIZ_ID}, 'inLanguage': 'en-US'},
            business_full(),
            webpage(url, page),  # name = the page's <title>, as on every other page
            breadcrumbs(url, name, page=page),
        ]
        return graph

    parent = None  # fallback when the page has no breadcrumb nav: Home > Page
    if fname.startswith('products-'):
        parent = ('Products', SITE + 'products.html')
    if fname == 'jobs.html':
        parent = ('Join Our Team', SITE + 'join-our-team.html')
    if fname.startswith('job-'):
        parent = ('Careers', SITE + 'join-our-team.html')

    kind = {'contact-us.html': 'ContactPage', 'our-team.html': 'AboutPage', 'about.html': 'AboutPage',
            'products.html': 'CollectionPage', 'services.html': 'CollectionPage'}.get(fname, 'WebPage')
    wp = webpage(url, page, kind)
    graph += [wp, breadcrumbs(url, name, parent, page)]

    if fname == 'contact-us.html':
        graph.append(business_full())
        wp['mainEntity'] = {'@id': BIZ_ID}
        return graph

    graph.append(business_ref())

    if fname in SERVICE_BY_FILE:
        svc_name = SERVICE_BY_FILE[fname]
        service = {
            '@type': 'Service',
            '@id': url + '#service',
            'name': svc_name,
            'serviceType': svc_name,
            'description': meta(page, 'description'),
            'url': url,
            'image': first_image(page),
            'provider': {'@id': BIZ_ID},
            'areaServed': AREA_SERVED,
            'hasOfferCatalog': price_catalog(page, svc_name),
            'potentialAction': {'@type': 'ReserveAction',
                                'target': {'@type': 'EntryPoint', 'urlTemplate': BOOKING}},
        }
        if fname == 'slay-aesthetics.html':
            # Slay is its own medical business, operating inside Bellezza on Fridays.
            # Facts only: no descriptions (YMYL, brief 5.3).
            service['provider'] = {
                '@type': 'MedicalBusiness', '@id': 'https://www.slay-aesthetics.com/#business',
                'name': 'Slay Aesthetics & Wellness', 'url': 'https://www.slay-aesthetics.com',
                'address': ADDRESS,
                'employee': {'@id': SITE + 'our-team.html#shannon-francis'},
                'openingHoursSpecification': hours('Friday', '10:00', '18:00'),
            }
            service['broker'] = {'@id': BIZ_ID}
            del service['potentialAction']
        if not service['description']:  # page without a meta description (head not stamped yet)
            del service['description']
        wp['mainEntity'] = {'@id': service['@id']}
        graph.append(service)

    elif fname == 'services.html':
        linked = []
        for _, a in tags(main_of(page), 'a', href=True):  # not the header/drawer nav links
            target = a['href'].split('#', 1)[0].split('?', 1)[0]
            if target in SERVICE_BY_FILE and target not in linked:
                linked.append(target)
        files = linked or list(SERVICE_PAGES.values())
        wp['mainEntity'] = {
            '@type': 'ItemList', 'name': 'Services at Bellezza & Co.',
            'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': SERVICE_BY_FILE[f],
                                 'url': SITE + f} for i, f in enumerate(files)],
        }

    elif fname == 'about.html':
        graph[-1]['foundingDate'] = '2009'
        graph[-1]['founder'] = [dict(f) for f in FOUNDERS]
        wp['mainEntity'] = {'@id': BIZ_ID}

    elif fname == 'our-team.html':
        people = team_people(page, url)
        graph[-1]['employee'] = [{'@id': p['@id']} for p in people]
        wp['mainEntity'] = {'@type': 'ItemList', 'name': 'Bellezza & Co. team',
                            'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'item': {'@id': p['@id']}}
                                                for i, p in enumerate(people)]}
        graph += people

    elif fname.startswith('job-'):
        graph += job_postings(page, url)

    elif fname == 'products.html':
        wp['mainEntity'] = {
            '@type': 'ItemList', 'name': 'Professional brands carried at Bellezza & Co.',
            'itemListElement': brand_list(page, url),
        }

    elif fname.startswith('products-'):
        brand = {'@type': 'Brand', 'name': name}
        m_logo = next((local_asset(s) for s in IMG_SRC.findall(page) if local_asset(s).startswith('assets/img/brands/')
                       and '/gallery/' not in s), None)
        if m_logo:
            brand['logo'] = SITE + m_logo
        # brand copy: the section headed h2#about-h (current pages), else the old centered block
        m_about = re.search(r'<h2[^>]*id="about-h"[^>]*>.*?</h2>(.*?)</section>', page, re.S)
        blocks = [m_about.group(1)] if m_about else             [inner for _, a, inner in elements(page, 'div', 'narrow') if has_class(a, 'center')]
        if blocks:
            about = ' '.join(text(p) for p in re.findall(r'<p\b[^>]*>(.*?)</p>', blocks[0], re.S) if '<a' not in p)
            if about:
                brand['description'] = about
        wp['about'] = [{'@id': BIZ_ID}, brand]

    elif fname == 'book-online.html':
        wp['potentialAction'] = {'@type': 'ReserveAction', 'name': 'Book an appointment',
                                 'target': {'@type': 'EntryPoint', 'urlTemplate': BOOKING},
                                 'provider': {'@id': BIZ_ID}}

    elif fname == 'gift-cards.html':
        wp['potentialAction'] = {'@type': 'BuyAction', 'name': 'Buy a gift card',
                                 'target': 'https://na0.meevo.com/EgiftApp/home?tenantId=100947',
                                 'seller': {'@id': BIZ_ID}}

    return graph


# ------------------------------------------------------------------ checks
def price_warnings(fname, page, graph):
    """Warn when the meta description's "from $X" is not a price on the page's menu."""
    m = re.search(r'from \$(\d+(?:\.\d+)?)', meta(page, 'description'), re.I)
    service = next((n for n in graph if n.get('@type') == 'Service'), None)
    if not m or not service:
        return []
    want = float(m.group(1))
    seen = set()
    for group in service['hasOfferCatalog']['itemListElement']:
        for offer in group['itemListElement']:
            spec = offer.get('priceSpecification', {})
            seen.update(float(spec[k]) for k in ('price', 'minPrice') if k in spec)
    if seen and want not in seen:
        return [f'warning: {fname}: meta description says "from ${m.group(1)}" but no menu item starts at that price']
    return []


# ------------------------------------------------------------------ write
BLOCK = re.compile(r'\n?<!-- schema:start.*?<!-- schema:end -->', re.S)
OLD_LD = re.compile(r'\n?<script type="application/ld\+json">.*?</script>', re.S)


def strip_schema(page):
    return OLD_LD.sub('', BLOCK.sub('', page))


def render(fname, page):
    """(graph data, page text with a fresh schema block)."""
    clean = strip_schema(page)
    data = {'@context': 'https://schema.org', '@graph': build(fname, clean)}
    block = ('\n<!-- schema:start: generated by tools/build-schema.py, do not edit by hand -->\n'
             '<script type="application/ld+json">\n'
             + json.dumps(data, ensure_ascii=False, indent=1).replace('</', '<\\/')
             + '\n</script>\n<!-- schema:end -->')
    if '\n</head>' in clean:
        return data, clean.replace('\n</head>', block + '\n</head>', 1)
    # </head> not on its own line (minified or hand-edited head): still stamp it.
    return data, re.sub(r'</head>', lambda m: block + '\n</head>', clean, count=1, flags=re.I)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    root = ROOT
    if '--root' in argv:
        root = os.path.abspath(argv[argv.index('--root') + 1])
    count = 0
    for fname in sorted(os.listdir(root)):
        if not fname.endswith('.html') or fname in SKIP:
            continue
        path = os.path.join(root, fname)
        with open(path, encoding='utf-8') as f:
            page = f.read()
        if 'noindex' in meta(page, 'robots').lower():
            # Not in search (e.g. thank-you.html): no structured data; drop any old block.
            out = strip_schema(page)
            if out != page:
                with open(path, 'w', encoding='utf-8', newline='\n') as f:
                    f.write(out)
            print(f'{fname:32} noindex, no schema')
            continue
        data, out = render(fname, page)
        for w in price_warnings(fname, strip_schema(page), data['@graph']):
            print(w, file=sys.stderr)
        if '<!-- schema:start' not in out:
            print(f'warning: {fname}: no </head> found, schema not stamped', file=sys.stderr)
        if out != page:
            with open(path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(out)
        count += 1
        print(f'{fname:32} {len(data["@graph"])} nodes')
    print(count, 'pages updated')


if __name__ == '__main__':
    main()
