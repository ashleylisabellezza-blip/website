"""Generate schema.org JSON-LD for every page from the page's own HTML.

Run after editing prices, staff or job listings:
    python tools/build-schema.py

Each page gets one <script type="application/ld+json"> block in <head>,
between <!-- schema:start --> and <!-- schema:end --> markers (replaced on
every run, so never hand-edit inside them). What each page gets:

  every page       WebPage + BreadcrumbList, linked to the business by @id
  index.html       full business profile (DaySpa/HairSalon/NailSalon) + WebSite
  contact-us.html  full business profile on a ContactPage
  service pages    Service + OfferCatalog built from the price lists
  our-team.html    Person for each staff member, linked as employees
  join-our-team    JobPosting for each open position (Google Jobs)
  products pages   Brand / ItemList of brands
"""
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://bellezzaspaonline.com/'
BIZ_ID = SITE + '#business'
SITE_ID = SITE + '#website'
BOOKING = 'https://login.meevo.com/bellezza/ob?locationId=103245'

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


def hours(days, opens, closes):
    return {'@type': 'OpeningHoursSpecification', 'dayOfWeek': days, 'opens': opens, 'closes': closes}


def business_full():
    return {
        '@type': ['DaySpa', 'HairSalon', 'NailSalon'],
        '@id': BIZ_ID,
        'name': 'Bellezza & Co. Salon, Spa & Boutique',
        'alternateName': ['Bellezza & Co.', 'Bellezza Salon and Day Spa', 'Bellezza Spa'],
        'description': ('Full-service salon, spa and boutique in Newark, Ohio offering hair, color and '
                        'extensions, manicures and pedicures, massage, facials, waxing, brows and lashes, '
                        'makeup, spray tans and bridal services. Voted the number one spa in Licking '
                        'County every year since 2016.'),
        'url': SITE,
        'logo': {'@type': 'ImageObject', 'url': SITE + 'assets/img/logo.png', 'width': 786, 'height': 257},
        'image': [SITE + 'assets/img/hero-1.jpg', SITE + 'assets/img/services/mani-room.jpg',
                  SITE + 'assets/img/services/facial-room.jpg', SITE + 'assets/img/logo.png'],
        'telephone': '+1-740-366-1604',
        'address': ADDRESS,
        'geo': {'@type': 'GeoCoordinates', 'latitude': 40.08631, 'longitude': -82.422132},
        'hasMap': 'https://www.google.com/maps/search/?api=1&query=206+Deo+Drive+Newark+OH+43055',
        'openingHoursSpecification': [
            hours(['Monday', 'Tuesday'], '09:00', '20:00'),
            hours('Wednesday', '12:00', '20:00'),
            hours('Thursday', '09:00', '20:00'),
            hours('Friday', '09:00', '19:00'),
            hours('Saturday', '08:00', '15:00'),
        ],
        'priceRange': '$$',
        'currenciesAccepted': 'USD',
        'foundingDate': '2009',
        'founder': [
            {'@type': 'Person', '@id': SITE + 'our-team.html#ashley-basham', 'name': 'Ashley Basham'},
            {'@type': 'Person', '@id': SITE + 'our-team.html#lisa-jeffries', 'name': 'Lisa Jeffries'},
        ],
        'award': 'Voted #1 Spa in Licking County, every year since 2016',
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


def business_ref():
    """Short copy of the business for pages that only need to point at it."""
    return {
        '@type': ['DaySpa', 'HairSalon', 'NailSalon'],
        '@id': BIZ_ID,
        'name': 'Bellezza & Co. Salon, Spa & Boutique',
        'url': SITE,
        'telephone': '+1-740-366-1604',
        'address': ADDRESS,
        'image': SITE + 'assets/img/logo.png',
        'priceRange': '$$',
    }


# Page file -> Service name (and breadcrumb parent "Services")
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


# ------------------------------------------------------------------ helpers
def text(fragment):
    """Strip tags and decode entities."""
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', fragment))).strip()


def meta(page, name):
    m = re.search(r'<meta name="%s" content="([^"]*)"' % name, page)
    return html.unescape(m.group(1)) if m else ''


def title_of(page):
    return text(re.search(r'<title>(.*?)</title>', page, re.S).group(1))


def h1_of(page):
    m = re.search(r'<h1>(.*?)</h1>', page, re.S)
    return text(m.group(1)) if m else title_of(page).split('|')[0].strip()


def first_image(page):
    main = page.split('<main>', 1)[-1]
    m = re.search(r'<img src="(assets/img/(?!badge)[^"]+)"', main)
    return SITE + m.group(1) if m else SITE + 'assets/img/banner-interior.jpg'


LEVEL_OR_TIME = re.compile(r'(stylist|minutes?|investment determined)', re.I)


def price_spec(raw):
    """'$31 / 37 / 40' -> min/max range, '$75+' -> minimum, '$12 per unit' -> unit price."""
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


def price_catalog(page, service_name):
    """Build OfferCatalogs from every .menu-group on the page."""
    groups = []
    for block in re.split(r'<div class="menu-group">', page)[1:]:
        group = text(re.search(r'<h3>(.*?)</h3>', block, re.S).group(1))
        intro = re.search(r'<h3>.*?</h3>\s*<p class="center">(.*?)</p>', block, re.S)
        intro = text(intro.group(1)) if intro else ''
        offers = []
        for li in re.findall(r'<li class="price-item">(.*?)</li>', block, re.S):
            name = text(re.search(r'<span class="name">(.*?)</span>', li, re.S).group(1))
            price = text(re.search(r'<span class="price">(.*?)</span>', li, re.S).group(1))
            desc = re.search(r'</div>\s*<p>(.*?)</p>', li, re.S)
            desc = text(desc.group(1)) if desc else ''
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


def breadcrumbs(url, name, parent=None):
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
    node.update(extra)
    return node


# ------------------------------------------------------------------ page builders
def build(fname, page):
    url = SITE if fname == 'index.html' else SITE + fname
    name = h1_of(page)
    graph = []

    if fname == 'index.html':
        graph += [
            {'@type': 'WebSite', '@id': SITE_ID, 'url': SITE, 'name': 'Bellezza & Co.',
             'alternateName': 'Bellezza Salon and Day Spa', 'publisher': {'@id': BIZ_ID}, 'inLanguage': 'en-US'},
            business_full(),
            webpage(url, page, name='Bellezza & Co. | Salon, Spa & Boutique in Newark, Ohio'),
            breadcrumbs(url, name),
        ]
        return graph

    parent = None  # there is no standalone Services page, so services are Home > Page
    if fname.startswith('products-'):
        parent = ('Products', SITE + 'products.html')
    if fname == 'jobs.html':
        parent = ('Join Our Team', SITE + 'join-our-team.html')

    kind = {'contact-us.html': 'ContactPage', 'our-team.html': 'AboutPage',
            'products.html': 'CollectionPage'}.get(fname, 'WebPage')
    wp = webpage(url, page, kind)
    graph += [wp, breadcrumbs(url, name, parent)]

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
            service['provider'] = {
                '@type': 'MedicalBusiness', '@id': 'https://www.slay-aesthetics.com/#business',
                'name': 'Slay Aesthetics & Wellness', 'url': 'https://www.slay-aesthetics.com',
                'address': ADDRESS, 'telephone': '+1-740-366-1604',
                'employee': {'@id': SITE + 'our-team.html#shannon-francis'},
                'openingHoursSpecification': hours('Friday', '10:00', '18:00'),
            }
            service['broker'] = {'@id': BIZ_ID}
            del service['potentialAction']
        wp['mainEntity'] = {'@id': service['@id']}
        graph.append(service)

    elif fname == 'our-team.html':
        people = []
        for card in re.findall(r'<div class="card">.*?</div>|<a class="card".*?</a>', page, re.S):
            m_name = re.search(r'<h4>(.*?)</h4>', card, re.S)
            if not m_name:
                continue
            pname = text(m_name.group(1))
            role = text(re.search(r'<span>(.*?)</span>', card, re.S).group(1))
            img = re.search(r'<img src="([^"]+)"', card).group(1)
            slug = os.path.splitext(os.path.basename(img))[0]
            person = {'@type': 'Person', '@id': url + '#' + slug, 'name': pname, 'jobTitle': role,
                      'image': SITE + img, 'worksFor': {'@id': BIZ_ID}}
            dlg = re.search(r'<dialog class="bio" id="bio-%s".*?</dialog>' % re.escape(slug), page, re.S)
            if dlg:
                bio = re.search(r'<span class="role">.*?</span>\s*<p>(.*?)</p>', dlg.group(0), re.S)
                if bio:
                    person['description'] = text(bio.group(1))
            ig = re.search(r'href="(https://www\.instagram\.com/[^"]+)"', card)
            if ig:
                person['sameAs'] = [ig.group(1)]
            people.append(person)
        graph[-1]['employee'] = [{'@id': p['@id']} for p in people]
        wp['mainEntity'] = {'@type': 'ItemList', 'name': 'Bellezza & Co. team',
                            'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'item': {'@id': p['@id']}}
                                                for i, p in enumerate(people)]}
        graph += people

    elif fname == 'join-our-team.html':
        types = {'massage-therapist': ['FULL_TIME', 'PART_TIME'], 'internship': ['INTERN'],
                 'new-talent': ['FULL_TIME'], 'nail-therapist': ['FULL_TIME', 'PART_TIME'],
                 'experienced-stylist': ['FULL_TIME']}
        for job_id, body in re.findall(r'<article class="job" id="([^"]+)">(.*?)</article>', page, re.S):
            jtitle = text(re.search(r'<h2>(.*?)</h2>', body, re.S).group(1))
            desc_html = re.sub(r'<h2>.*?</h2>|<a class="btn"[^>]*>.*?</a>', '', body, flags=re.S)
            desc_html = re.sub(r'\s+', ' ', html.unescape(desc_html)).strip()
            graph.append({
                '@type': 'JobPosting',
                '@id': url + '#' + job_id,
                'title': jtitle,
                'description': desc_html,
                'datePosted': JOBS_DATE_POSTED,
                'employmentType': types.get(job_id, ['FULL_TIME']),
                'hiringOrganization': {'@type': 'Organization', 'name': 'Bellezza & Co.', 'sameAs': SITE,
                                       'logo': SITE + 'assets/img/logo.png'},
                'jobLocation': {'@type': 'Place', 'address': ADDRESS},
                'industry': 'Beauty and personal care',
                'directApply': True,
                'url': url + '#' + job_id,
            })

    elif fname == 'products.html':
        brands = re.findall(r'<a class="brand-card" href="([^"]+)">.*?<img src="([^"]+)".*?<h3>(.*?)</h3>', page, re.S)
        wp['mainEntity'] = {
            '@type': 'ItemList', 'name': 'Professional brands carried at Bellezza & Co.',
            'itemListElement': [
                {'@type': 'ListItem', 'position': i + 1, 'url': SITE + href,
                 'item': {'@type': 'Brand', 'name': text(n), 'logo': SITE + logo, 'url': SITE + href}}
                for i, (href, logo, n) in enumerate(brands)],
        }

    elif fname.startswith('products-'):
        logo = re.search(r'<img src="(assets/img/brands/[^"]+)"', page).group(1)
        paras = re.findall(r'<div class="narrow center">.*?</div>', page, re.S)[0]
        about = ' '.join(text(p) for p in re.findall(r'<p>(.*?)</p>', paras, re.S) if '<a' not in p)
        wp['about'] = [{'@id': BIZ_ID}, {'@type': 'Brand', 'name': name, 'logo': SITE + logo, 'description': about}]

    elif fname == 'book-online.html':
        wp['potentialAction'] = {'@type': 'ReserveAction', 'name': 'Book an appointment',
                                 'target': {'@type': 'EntryPoint', 'urlTemplate': BOOKING},
                                 'provider': {'@id': BIZ_ID}}

    elif fname == 'gift-cards.html':
        wp['potentialAction'] = {'@type': 'BuyAction', 'name': 'Buy a gift card',
                                 'target': 'https://na0.meevo.com/EgiftApp/home?tenantId=100947',
                                 'seller': {'@id': BIZ_ID}}

    return graph


# ------------------------------------------------------------------ write
BLOCK = re.compile(r'\n?<!-- schema:start.*?<!-- schema:end -->', re.S)
OLD_LD = re.compile(r'\n?<script type="application/ld\+json">.*?</script>', re.S)


def main():
    count = 0
    for fname in sorted(os.listdir(ROOT)):
        if not fname.endswith('.html') or fname in SKIP:
            continue
        path = os.path.join(ROOT, fname)
        page = open(path, encoding='utf-8').read()
        clean = OLD_LD.sub('', BLOCK.sub('', page))
        data = {'@context': 'https://schema.org', '@graph': build(fname, clean)}
        block = ('\n<!-- schema:start: generated by tools/build-schema.py, do not edit by hand -->\n'
                 '<script type="application/ld+json">\n'
                 + json.dumps(data, ensure_ascii=False, indent=1).replace('</', '<\\/')
                 + '\n</script>\n<!-- schema:end -->')
        out = clean.replace('\n</head>', block + '\n</head>', 1)
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(out)
        count += 1
        print(f'{fname:32} {len(data["@graph"])} nodes')
    print(count, 'pages updated')


if __name__ == '__main__':
    main()
