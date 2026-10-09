"""Tests for tools/build-schema.py. Never writes to the project's pages.

Usage (from the project root):
    python tools/test_schema.py                  # fixture tests + regression against the baseline
    python tools/test_schema.py --fixtures       # fixture tests only
    python tools/test_schema.py --regression     # regression only
    python tools/test_schema.py --show-diff      # also print a unified diff for every changed page

Regression options:
    --old-script PATH|GITREF   the old build-schema.py (a file, or a git ref whose
                               tools/build-schema.py is used). Default: the repo's root
                               commit, i.e. the pre-redesign baseline.
    --pages DIR|GITREF         the pages both scripts run on. Default: the same root commit,
                               i.e. an untouched copy of the pre-redesign pages.
    --new-pages DIR|GITREF     also run the NEW script on these pages (e.g. "." for the
                               working tree) and report, page by page, how its JSON-LD
                               differs from the old script on --pages (brief 3.3, test 2).
                               Informational unless --strict is given.
    --today YYYY-MM-DD         pin "today" for the holiday hours (default: real today).

What the regression checks (brief 3.3, test 1): the old and new scripts run on the
same pages (copied to a temp dir, existing schema blocks stripped). For every page,
the new JSON-LD must be byte-identical to the old one after applying ONLY the
intentional changes listed in `intentional()` below. It also runs the new script's
writer twice on the temp copies to prove it is idempotent.

The fixture tests feed redesign-style markup (ids, modifier classes, attributes in
any order, <picture>, ?v= hashes, breadcrumb nav, data-asof, job pages, brand
anchors, new pages) and check the parsed result.

Exit code 1 on any failure. Stdlib only.
"""
import copy
import datetime
import difflib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True  # never leave tools/__pycache__ behind

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NEW_SCRIPT = os.path.join(ROOT, 'tools', 'build-schema.py')
SITE = 'https://bellezzaspaonline.com/'
BIZ_ID = SITE + '#business'


# ------------------------------------------------------------------ loading
def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def git(*args):
    return subprocess.run(['git', '-C', ROOT, *args], check=True, capture_output=True).stdout


def root_commit():
    return git('rev-list', '--max-parents=0', 'HEAD').decode().split()[0]


def resolve_script(spec, tmp):
    """Path to a copy of the old build-schema.py from a file path or a git ref."""
    if os.path.isfile(spec):
        return os.path.abspath(spec)
    out = os.path.join(tmp, 'old_build_schema.py')
    with open(out, 'wb') as f:
        f.write(git('show', f'{spec}:tools/build-schema.py'))
    return out


def resolve_pages(spec, dest):
    """Copy the root-level *.html pages from a directory or a git ref into dest."""
    os.makedirs(dest, exist_ok=True)
    if os.path.isdir(spec):
        for fname in os.listdir(spec):
            if fname.endswith('.html'):
                shutil.copyfile(os.path.join(spec, fname), os.path.join(dest, fname))
    else:
        names = git('ls-tree', '--name-only', spec).decode().splitlines()
        for fname in names:
            if fname.endswith('.html'):
                with open(os.path.join(dest, fname), 'wb') as f:
                    f.write(git('show', f'{spec}:{fname}'))
    return sorted(f for f in os.listdir(dest) if f.endswith('.html'))


def dumps(graph):
    return json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False, indent=1)


def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


# ------------------------------------------------------------------ intentional changes
STOCK = r'hero-1\.jpg|mani-room\.jpg|facial-room\.jpg'
OLD_DEFAULT_IMAGE = SITE +'assets/img/banner-interior.jpg'
AWARD_SENTENCE = re.compile(r'\s*Voted the number one spa in Licking County every year since 2016\.', re.I)


def intentional(fname, graph, new):
    """Apply the brief's intentional additions/removals to the OLD graph.
    Returns (expected_graph, [labels of changes applied])."""
    graph = copy.deepcopy(graph)
    changes = []
    out = []
    for node in graph:
        if node.get('@type') == 'JobPosting' and fname == 'join-our-team.html':
            changes.append('JobPosting removed from the list page')
            continue
        if node.get('@id') == BIZ_ID:
            node = business(node, new, changes)
        if node.get('@type') == 'WebSite' and node.get('alternateName') != new.BIZ_FORMERLY:
            node['alternateName'] = new.BIZ_FORMERLY
            changes.append('WebSite alternateName')
        out.append(node)
    text = json.dumps(out, ensure_ascii=False)
    if OLD_DEFAULT_IMAGE in text:
        text = text.replace(OLD_DEFAULT_IMAGE, SITE + new.DEFAULT_IMAGE)
        changes.append('default page image')
    return json.loads(text), sorted(set(changes))


def business(node, new, changes):
    full = 'alternateName' in node
    out = {}
    for key, val in node.items():
        if key == 'name' and val != new.BIZ_NAME:
            val = new.BIZ_NAME
            changes.append('business name')
        if key == 'award':
            changes.append('award removed')
            continue
        if key == 'alternateName':
            out[key] = new.BIZ_FORMERLY
            out['slogan'] = new.BIZ_SLOGAN
            changes.append('alternateName + slogan')
            continue
        if key == 'description' and full and AWARD_SENTENCE.search(val):
            val = AWARD_SENTENCE.sub('', val)
            changes.append('award sentence removed from description')
        if key == 'image' and full:
            val = [SITE + 'assets/img/team/contact-sheet-1540.jpg', SITE + 'assets/img/about/team-group-1120.jpg',
                   SITE + 'assets/img/logo.png']
            changes.append('business image list')
        if key == 'openingHoursSpecification' and full:
            extra = new.holiday_specs(new.load_site())
            if extra:
                val = val + extra
                changes.append(f'{len(extra)} holiday hours')
        out[key] = val
    return out


# ------------------------------------------------------------------ regression
def regression(args):
    failures = 0
    tmp = tempfile.mkdtemp(prefix='schema-test-')
    try:
        base_ref = None
        if not args.old_script or not args.pages:
            base_ref = root_commit()
        old_path = resolve_script(args.old_script or base_ref, tmp)
        old = load_module(old_path, 'old_build_schema')
        new = load_module(NEW_SCRIPT, 'new_build_schema')
        pages_dir = os.path.join(tmp, 'pages')
        pages = resolve_pages(args.pages or base_ref, pages_dir)
        print(f'old script: {args.old_script or base_ref + ":tools/build-schema.py"}')
        print(f'pages:      {args.pages or base_ref} ({len(pages)} files)')
        print(f'today:      {new.today()}\n')

        identical, intended, unexpected = [], [], []
        for fname in pages:
            if fname in new.SKIP or fname in getattr(old, 'SKIP', set()):
                continue
            page = new.strip_schema(read(os.path.join(pages_dir, fname)))
            old_graph = old.build(fname, page)
            new_graph = new.build(fname, page)
            old_json, new_json = dumps(old_graph), dumps(new_graph)
            if old_json == new_json:
                identical.append(fname)
                continue
            expected, labels = intentional(fname, old_graph, new)
            if dumps(expected) == new_json:
                intended.append((fname, labels))
            else:
                unexpected.append(fname)
                failures += 1
                print(f'UNEXPECTED change in {fname}:')
                sys.stdout.writelines(difflib.unified_diff(
                    dumps(expected).splitlines(True), new_json.splitlines(True),
                    'expected (old + intentional)', 'new', n=2))
                print()
            if args.show_diff and old_json != new_json:
                print(f'--- diff {fname} (old -> new)')
                sys.stdout.writelines(difflib.unified_diff(
                    old_json.splitlines(True), new_json.splitlines(True), 'old', 'new', n=1))
                print()

        print(f'byte-identical:            {len(identical)} pages')
        print(f'intentional changes only:  {len(intended)} pages')
        for fname, labels in intended:
            print(f'    {fname:28} {"; ".join(labels)}')
        print(f'unexpected differences:    {len(unexpected)} pages {unexpected if unexpected else ""}')

        # The writer must be idempotent: a second run changes no bytes.
        run_dir = os.path.join(tmp, 'run')
        shutil.copytree(pages_dir, run_dir)
        quiet(new.main, ['--root', run_dir])
        first = {f: read(os.path.join(run_dir, f)) for f in pages}
        quiet(new.main, ['--root', run_dir])
        changed = [f for f in pages if read(os.path.join(run_dir, f)) != first[f]]
        print(f'idempotent writer:         {"yes" if not changed else "NO, changed: " + ", ".join(changed)}')
        failures += bool(changed)
        leaked, stock_pages = [], []
        for f in pages:
            if f in new.SKIP:
                continue
            ld = re.search(r'<script type="application/ld\+json">\n(.*?)\n</script>', first[f], re.S).group(1)
            ld = json.loads(ld.replace('<\\/', '</'))
            blob = json.dumps(ld)
            biz_images = json.dumps([n.get('image') for n in ld['@graph'] if n.get('@id') == BIZ_ID])
            if re.search(r'aggregateRating|"Review"', blob) or re.search(STOCK, biz_images):
                leaked.append(f)
            elif re.search(STOCK, blob):
                stock_pages.append(f)
        print(f'no rating/review, no stock business image: {"yes" if not leaked else "NO: " + ", ".join(leaked)}')
        if stock_pages:
            print(f'note: a stock photo is the page image (taken from page markup) on: {", ".join(stock_pages)}')
        failures += bool(leaked)

        if args.new_pages:
            print('\nOld site vs new site (old script on --pages, new script on --new-pages):')
            new_dir = os.path.join(tmp, 'new-pages')
            new_list = resolve_pages(args.new_pages, new_dir)
            drift = 0
            for fname in sorted(set(pages) | set(new_list)):
                if fname in new.SKIP:
                    continue
                if fname not in new_list:
                    print(f'    {fname:28} removed')
                    continue
                n_json = dumps(new.build(fname, new.strip_schema(read(os.path.join(new_dir, fname)))))
                if fname not in pages:
                    print(f'    {fname:28} new page')
                    continue
                o_graph = old.build(fname, new.strip_schema(read(os.path.join(pages_dir, fname))))
                expected, _ = intentional(fname, o_graph, new)
                if dumps(expected) != n_json:
                    drift += 1
                    diff = list(difflib.unified_diff(dumps(expected).splitlines(True), n_json.splitlines(True),
                                                     'old site', 'new site', n=1))
                    print(f'    {fname:28} {sum(1 for l in diff if l[:1] in "+-") - 2} changed lines')
                    if args.show_diff:
                        sys.stdout.writelines(diff)
            if args.strict:
                failures += drift
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return failures


def quiet(fn, *a):
    import io
    import contextlib
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return fn(*a)


# ------------------------------------------------------------------ fixtures
HEAD = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<title>{title}</title>\n'
        '<meta content="{desc}" name="description">\n</head>\n<body>\n'
        '<header><a href="index.html"><img src="assets/img/logo.png" alt="Bellezza &amp; Co."></a></header>\n{body}\n'
        '</body>\n</html>\n')


def page(title, body, desc='A page.'):
    return HEAD.format(title=title, desc=desc, body=body)


def crumbs(*items):
    lis = ''.join(f'<li><a class="crumb" href="{h}">{n}</a></li>' for n, h in items[:-1])
    return (f'<nav class="breadcrumb" aria-label="Breadcrumb"><ol class="crumbs">{lis}'
            f'<li aria-current="page">{items[-1]}</li></ol></nav>')


SERVICE_PAGE = page('Nail Salon & Pedicures | Bellezza &amp; Co.', crumbs(
    ('Home', 'index.html'), ('Services &amp; Prices', 'services.html'), 'Nails') + '''
<main id="main" class="page page--service">
<h1 class="page-title" id="top">Manicures &amp; Pedicures</h1>
<picture><source type="image/avif" srcset="assets/img/services/nails-540.avif 540w">
<img alt="Nail station" loading="eager" src="assets/img/services/nails-540.jpg?v=1a2b3c4d" width="540" height="720"></picture>
<h2 id="prices">Menu &amp; prices</h2>
<div id="manicures" class="menu-group menu-group--slash" data-group="1">
  <h3 id="manicures-h" class="rule">Manicures</h3>
  <p class="group-intro muted">All manicures include shaping.</p>
  <p id="tiers-nails-manicures" class="tier-head">Associate / Senior / Expert</p>
  <ul class="price-list" aria-describedby="tiers-nails-manicures">
    <li data-item="gel" class="price-item price-item--featured">
      <div class="price-head"><span class="name">Gel Manicure</span><span class="dots" aria-hidden="true"></span><span class="price">$44 / 49 / 53</span></div>
      <p class="desc">Long-lasting gel polish.</p>
      <p class="note">Consultation required · $50 deposit</p>
    </li>
    <li class="price-item"><div class="price-head"><span class="name">Nail Art</span><span class="dots"></span><span class="price">$$</span></div><p class="note">Ask us</p><p>Custom designs.</p></li>
    <li class="price-item"><div class="price-head"><span class="name">Specialty Braiding</span><span class="dots"></span><span class="price">Consultation</span></div></li>
    <li class="price-item"><div class="price-head"><span class="name">Fantasy Color</span><span class="dots"></span><span class="price">Priced at consultation</span></div></li>
    <li class="price-ref"><div class="price-head"><span class="name">Men&#39;s cut</span><span class="price">from $25</span></div></li>
  </ul>
  <a href="#book">Book this</a>
</div>
<div class="menu-group" id="cuts"><h3>Women&#39;s Haircut</h3><p class="center">Cut and finish.</p>
  <ul class="price-list price-list--ladder">
    <li class="price-item"><div class="price-head"><span class="name">Master <span class="lvl-suffix">Stylist</span></span><span class="dots"></span><span class="price">$60</span></div></li>
    <li class="price-item"><div class="price-head"><span class="name">60 min</span><span class="dots"></span><span class="price">$70</span></div></li>
    <li class="price-item"><div class="price-head"><span class="name">Senior <span class="lvl-suffix">Stylist</span> Plus</span><span class="dots"></span><span class="price">$65</span></div></li>
  </ul>
</div>
<p class="asof">Prices as of <time class="x" datetime="2026-09" data-asof>September 2026</time></p>
</main>''', desc='Gel manicures from $44 in Newark, OH.')

TEAM_PAGE = page('Meet the Team | Bellezza &amp; Co.', crumbs(('Home', 'index.html'), 'Meet the team') + '''
<main>
<h1>Meet the team</h1>
<ul class="team-grid">
<li class="team-item" id="devon" data-dept="hair bridal leadership" data-level="5">
  <div class="card">
    <picture><source type="image/avif" srcset="assets/img/team/devon-180.avif 180w, assets/img/team/devon-540.avif 540w">
    <img src="assets/img/team/devon-540.webp?v=abcd1234" srcset="assets/img/team/devon-180.webp 180w" width="540" height="720" alt="Devon" loading="lazy"></picture>
    <h3 class="card-name">Devon</h3>
    <span class="role">Salon Manager, Director of Education &amp; Master Stylist</span>
    <ul class="tags"><li>Blonding</li></ul>
    <button type="button" class="card-bio" data-bio="bio-devon" aria-haspopup="dialog">Read Devon&#39;s bio</button>
    <a data-book data-cta="book" data-placement="team-devon" href="#">Book<span class="sr-only"> an appointment (ask for Devon)</span></a>
    <a href="https://www.instagram.com/devonsabo_hairartist/">See Devon&#39;s work on Instagram</a>
  </div>
</li>
<li class="team-item"><div class="card card--front-desk"><img alt="Melissa, Client Services" src="assets/img/team/melissa.jpg"><h4>Melissa</h4><span>Client Services</span></div></li>
<li class="team-item"><a style="color:inherit" href="slay-aesthetics.html" class="card"><img src="assets/img/team/shannon-francis-540.jpg" alt=""><h3>Shannon Francis CNP</h3><span class="role">Certified Nurse Practitioner</span></a></li>
<li class="team-item"><div class="card"><p>No heading, not a person</p></div></li>
</ul>
<dialog closedby="any" aria-labelledby="bio-devon-h" id="bio-devon" class="bio">
  <button class="bio-close" type="button" autofocus aria-label="Close">x</button>
  <img src="assets/img/team/devon-540.webp" width="540" height="720" alt="" loading="lazy">
  <h2 id="bio-devon-h">Devon</h2>
  <span class="role">Salon Manager</span>
  <p class="bio-text">Devon leads education at the salon.</p>
  <ul class="creds-list"><li data-school="American School of Hair Design">American School of Hair Design, 2004</li><li>Providing services since 2004</li><li data-license="COSA.047959" data-license-type="Advanced Cosmetologist" data-board="Ohio State Cosmetology and Barber Board">Ohio Advanced Cosmetologist license COSA.047959</li><li data-cert="Regional Lakmé Brand Educator">Training: Regional Lakmé Brand Educator</li><li data-specialties="Hand-sewn extensions; Blonding">Specialties: Hand-sewn extensions, Blonding</li><li data-languages="English, Spanish">Speaks English and Spanish</li></ul>
</dialog>
</main>''')

JOB_PAGE = page('Massage Therapist | Careers | Bellezza &amp; Co.', crumbs(
    ('Home', 'index.html'), ('Careers', 'join-our-team.html'), 'Massage Therapist') + '''
<main><h1>Massage Therapist</h1>
<article data-open="true" id="massage-therapist" class="job job--open">
  <h2 class="job-title">Massage Therapist</h2>
  <p>Join our spa team.</p>
  <a href="#apply" class="btn btn--gold">Apply</a>
</article>
</main>''')

JOB_BENEFITS_PAGE = page('New Talent | Careers | Bellezza &amp; Co.', '''<main><h1>New Talent</h1>
<article class="job" id="new-talent"><h2>New Talent Stylist</h2><p>Train with us.</p>
<ul class="benefits"><li>Paid training and assisting program</li><li>Paid vacation and a 401(k) once eligible</li></ul></article></main>''')

JOIN_PAGE = page('Careers | Bellezza &amp; Co.', '''<main><h1>Careers at Bellezza</h1>
<article class="job" id="massage-therapist"><h2>Massage Therapist</h2><p>x</p></article></main>''')

PRODUCTS_PAGE = page('The Boutique | Bellezza &amp; Co.', '''<main><h1>The Boutique</h1>
<a href="#dermalogica" data-cta="brand" class="brand-card brand-card--color">
  <img alt="Dermalogica logo" src="assets/img/brands/dermalogica-logo.png?v=12345678"><h3>Dermalogica</h3></a>
<a class="brand-card" href="products.html#ref"><img src="assets/img/brands/ref-logo.png" alt="REF logo"></a>
</main>''')

SERVICES_PAGE = page('All Services &amp; Prices | Bellezza &amp; Co.', '<nav aria-label="Main">'
    '<a href="brides.html">Bridal</a><a href="massages.html">Massage</a></nav>' + crumbs(
    ('Home', 'index.html'), 'Services &amp; Prices') + '''<main id="main"><h1>Services &amp; prices</h1>
<a href="salon.html">Hair</a> <a class="x" href="tips-and-toes.html#manicures">Nails</a>
<a href="salon.html#cuts">Full hair menu</a> <a href="products.html">Boutique</a></main>''')

ABOUT_PAGE = page('Our Story | Bellezza &amp; Co.', crumbs(('Home', 'index.html'), 'Our story') +
                  '<main><h1>From an 1,800 sq ft house <em>to Bellezza &amp; Co.</em></h1>'
                  '<img src="assets/img/about/team-group-1120.jpg" alt=""></main>')

NEW_GUESTS_PAGE = page('Your First Visit | Bellezza &amp; Co.', crumbs(('Home', 'index.html'), 'Your first visit') +
                       '<main><h1>Your first visit</h1></main>')

INDEX_PAGE = page('Hair Salon &amp; Day Spa in Newark, Ohio | Bellezza &amp; Co.', '<main><h1>Bellezza</h1></main>')

TASK_SITE_JSON = {
    "holidays": [
        {"name": "Christmas", "month": 12, "day": 25, "closed": True},
        {"name": "Memorial Day", "rule": "last-monday-may", "closed": True},
        {"name": "Labor Day", "rule": "first-monday-september", "closed": True},
        {"name": "New Year's Eve", "month": 12, "day": 31, "closes": "12:00"},
    ],
    "trickOrTreat": {"2026": "2026-10-29"},
}


class Fixtures(unittest.TestCase):
    mod = None
    tmp = None

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix='schema-fixtures-')
        os.environ['SCHEMA_TODAY'] = '2026-09-29'
        cls.mod = load_module(NEW_SCRIPT, 'fixture_build_schema')
        cls.site_json(TASK_SITE_JSON)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)
        os.environ.pop('SCHEMA_TODAY', None)

    @classmethod
    def site_json(cls, data):
        path = os.path.join(cls.tmp, 'site.json')
        if data is None:
            if os.path.exists(path):
                os.remove(path)
        else:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f)
        cls.mod.SITE_JSON = path

    def setUp(self):
        self.site_json(TASK_SITE_JSON)

    def graph(self, fname, html_):
        return self.mod.build(fname, html_)

    def node(self, graph, **want):
        for n in graph:
            if all(n.get(k) == v for k, v in want.items()):
                return n
        self.fail(f'no node with {want}')

    # -- service pages
    def test_service_page(self):
        g = self.graph('tips-and-toes.html', SERVICE_PAGE)
        wp = self.node(g, **{'@type': 'WebPage'})
        self.assertEqual(wp['description'], 'Gel manicures from $44 in Newark, OH.')  # attrs in any order
        self.assertEqual(wp['primaryImageOfPage']['url'], SITE + 'assets/img/services/nails-540.jpg')
        self.assertEqual(wp['dateModified'], '2026-09')
        bc = self.node(g, **{'@type': 'BreadcrumbList'})
        self.assertEqual([(i['name'], i['item']) for i in bc['itemListElement']],
                         [('Home', SITE), ('Services & Prices', SITE + 'services.html'),
                          ('Nails', SITE + 'tips-and-toes.html')])
        svc = self.node(g, **{'@type': 'Service'})
        self.assertEqual(svc['potentialAction']['target']['urlTemplate'], self.mod.BOOKING)
        groups = svc['hasOfferCatalog']['itemListElement']
        self.assertEqual([gr['name'] for gr in groups], ['Manicures', "Women's Haircut"])
        offers = groups[0]['itemListElement']
        self.assertEqual([o['itemOffered']['name'] for o in offers],
                         ['Gel Manicure', 'Nail Art', 'Specialty Braiding', 'Fantasy Color'])  # price-ref ignored
        self.assertEqual(offers[0]['itemOffered']['description'], 'Long-lasting gel polish.')
        self.assertEqual(offers[0]['priceSpecification'],
                         {'@type': 'PriceSpecification', 'priceCurrency': 'USD', 'minPrice': 44, 'maxPrice': 53})
        self.assertEqual(offers[1]['itemOffered']['description'], 'Custom designs.')  # note skipped
        for o in offers[1:]:
            self.assertNotIn('priceSpecification', o)  # $$ / Consultation: no price
        ladder = groups[1]['itemListElement']
        self.assertEqual([o['itemOffered']['name'] for o in ladder],
                         ["Women's Haircut (Master Stylist)", "Women's Haircut (60 min)",
                          "Women's Haircut (Senior Stylist Plus)"])  # nested span inside span.name
        self.assertEqual(ladder[0]['itemOffered']['description'], 'Cut and finish.')
        self.assertNotIn('$$', json.dumps(svc['hasOfferCatalog']))
        self.assertEqual(self.mod.price_warnings('tips-and-toes.html', SERVICE_PAGE, g), [])
        bad = SERVICE_PAGE.replace('from $44', 'from $40')
        self.assertEqual(len(self.mod.price_warnings('tips-and-toes.html', bad, self.graph('tips-and-toes.html', bad))), 1)

    def test_slay_node_is_facts_only(self):
        g = self.graph('slay-aesthetics.html', SERVICE_PAGE)
        prov = self.node(g, **{'@type': 'Service'})['provider']
        self.assertEqual(set(prov), {'@type', '@id', 'name', 'url', 'address', 'employee',
                                     'openingHoursSpecification'})

    # -- team
    def test_team_cards(self):
        g = self.graph('our-team.html', TEAM_PAGE)
        people = [n for n in g if n.get('@type') == 'Person']
        self.assertEqual([p['@id'] for p in people],
                         [SITE + 'our-team.html#devon', SITE + 'our-team.html#melissa',
                          SITE + 'our-team.html#shannon-francis'])
        devon, melissa, shannon = people
        self.assertEqual(devon['name'], 'Devon')
        self.assertEqual(devon['jobTitle'], 'Salon Manager, Director of Education & Master Stylist')
        self.assertEqual(devon['image'], SITE + 'assets/img/team/devon-540.webp')
        self.assertEqual(devon['description'], 'Devon leads education at the salon.')
        self.assertEqual(devon['sameAs'], ['https://www.instagram.com/devonsabo_hairartist/'])
        self.assertEqual(devon['alumniOf'], {'@type': 'EducationalOrganization', 'name': 'American School of Hair Design'})
        lic, cert = devon['hasCredential']
        self.assertEqual((lic['credentialCategory'], lic['identifier'], lic['recognizedBy']['name']),
                         ('license', 'COSA.047959', 'Ohio State Cosmetology and Barber Board'))
        self.assertEqual(lic['name'], 'Ohio Advanced Cosmetologist license COSA.047959')
        self.assertEqual((cert['credentialCategory'], cert['name']), ('certificate', 'Regional Lakmé Brand Educator'))
        self.assertEqual(devon['knowsAbout'], ['Hand-sewn extensions', 'Blonding'])
        self.assertEqual(devon['knowsLanguage'], ['English', 'Spanish'])
        self.assertNotIn('hasCredential', melissa)
        self.assertEqual(melissa['jobTitle'], 'Client Services')
        self.assertEqual(shannon['jobTitle'], 'Certified Nurse Practitioner')
        biz = self.node(g, **{'@id': BIZ_ID})
        self.assertEqual(len(biz['employee']), 3)

    # -- careers
    def test_job_page_one_posting(self):
        g = self.graph('job-massage-therapist.html', JOB_PAGE)
        jobs = [n for n in g if n.get('@type') == 'JobPosting']
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]['title'], 'Massage Therapist')
        self.assertEqual(jobs[0]['@id'], SITE + 'job-massage-therapist.html#massage-therapist')
        self.assertEqual(jobs[0]['description'], '<p>Join our spa team.</p>')
        self.assertEqual(jobs[0]['employmentType'], ['FULL_TIME', 'PART_TIME'])
        posted = datetime.date.fromisoformat(jobs[0]['datePosted'])
        self.assertEqual(jobs[0]['validThrough'], (posted + datetime.timedelta(days=90)).isoformat())
        self.assertNotIn('jobBenefits', jobs[0])
        bc = self.node(g, **{'@type': 'BreadcrumbList'})
        self.assertEqual(bc['itemListElement'][1]['item'], SITE + 'join-our-team.html')

    def test_job_benefits(self):
        g = self.graph('job-new-talent.html', JOB_BENEFITS_PAGE)
        job = self.node(g, **{'@type': 'JobPosting'})
        self.assertEqual(job['jobBenefits'], 'Paid training and assisting program; Paid vacation and a 401(k) once eligible')

    def test_no_posting_on_list_page(self):
        g = self.graph('join-our-team.html', JOIN_PAGE)
        self.assertFalse([n for n in g if n.get('@type') == 'JobPosting'])

    # -- boutique
    def test_brand_cards(self):
        g = self.graph('products.html', PRODUCTS_PAGE)
        items = self.node(g, **{'@type': 'CollectionPage'})['mainEntity']['itemListElement']
        self.assertEqual([(i['item']['name'], i['url']) for i in items],
                         [('Dermalogica', SITE + 'products.html#dermalogica'), ('REF', SITE + 'products.html#ref')])
        self.assertEqual(items[0]['item']['logo'], SITE + 'assets/img/brands/dermalogica-logo.png')

    # -- new pages
    def test_services_page(self):
        g = self.graph('services.html', SERVICES_PAGE)
        wp = self.node(g, **{'@type': 'CollectionPage'})
        self.assertEqual([(i['name'], i['url']) for i in wp['mainEntity']['itemListElement']],
                         [('Hair Salon', SITE + 'salon.html'), ('Manicures & Pedicures', SITE + 'tips-and-toes.html')])

    def test_about_page(self):
        g = self.graph('about.html', ABOUT_PAGE)
        wp = self.node(g, **{'@type': 'AboutPage'})
        self.assertEqual(wp['mainEntity'], {'@id': BIZ_ID})
        biz = self.node(g, **{'@id': BIZ_ID})
        self.assertEqual(biz['foundingDate'], '2009')
        self.assertEqual(sorted(f['name'] for f in biz['founder']), ['Ashley Basham', 'Lisa Jeffries'])
        bc = self.node(g, **{'@type': 'BreadcrumbList'})
        self.assertEqual(bc['itemListElement'][-1]['name'], 'Our story')

    def test_new_guests_page(self):
        g = self.graph('new-guests.html', NEW_GUESTS_PAGE)
        self.node(g, **{'@type': 'WebPage'})
        self.assertEqual(self.node(g, **{'@type': 'WebPage'})['primaryImageOfPage']['url'],
                         SITE + 'assets/img/team/contact-sheet-1540.jpg')  # no image in <main>

    # -- business profile
    def test_business_profile(self):
        g = self.graph('index.html', INDEX_PAGE)
        biz = self.node(g, **{'@id': BIZ_ID})
        self.assertEqual(biz['name'], 'Bellezza & Co.')
        self.assertEqual(biz['slogan'], 'Beauty and relaxation tailored to you.')
        self.assertEqual(biz['alternateName'], 'Bellezza Salon and Day Spa')
        self.assertEqual(biz['legalName'], 'Bellezza Salon & Day Spa')
        self.assertEqual(len(biz['award']), 2)
        self.assertTrue(all("Licking County Community's Choice Awards" in a for a in biz['award']))
        self.assertNotIn('Voted', biz['description'])
        self.assertEqual(biz['image'], [SITE + 'assets/img/team/contact-sheet-1540.jpg', SITE + 'assets/img/logo.png'])
        self.assertEqual(biz['hasCredential']['identifier'], '091084')
        self.assertIn('https://g.page/r/CUqbhUZs2e36EBM', biz['sameAs'])
        self.assertFalse([s for s in biz['sameAs'] if 'apps.apple.com' in s or 'play.google.com' in s])
        self.assertTrue(biz['amenityFeature']['value'])
        self.assertEqual(biz['potentialAction']['target']['urlTemplate'], self.mod.BOOKING)
        site = self.node(g, **{'@type': 'WebSite'})
        self.assertEqual(site['alternateName'], 'Bellezza Salon and Day Spa')
        wp = self.node(g, **{'@type': 'WebPage'})
        self.assertEqual(wp['name'], 'Hair Salon & Day Spa in Newark, Ohio | Bellezza & Co.')  # from <title>
        text = json.dumps(g)
        for banned in ('aggregateRating', '"Review"', 'hero-1.jpg', 'mani-room', 'facial-room'):
            self.assertNotIn(banned, text)

    def test_award_constant(self):
        saved = self.mod.AWARD
        self.mod.AWARD = None
        try:
            self.assertNotIn('award', self.mod.business_full())
            self.mod.AWARD = 'Test award'
            self.assertEqual(self.mod.business_full()['award'], 'Test award')
        finally:
            self.mod.AWARD = saved

    def test_holidays(self):
        specs = [s for s in self.mod.business_full()['openingHoursSpecification'] if 'validFrom' in s]
        self.assertEqual([(s['validFrom'], s['opens'], s['closes']) for s in specs], [
            ('2026-10-29', '09:00', '17:00'),   # trick-or-treat (Thu), date from trickOrTreat
            ('2026-12-25', '00:00', '00:00'),   # Christmas (Fri)
            ('2026-12-31', '09:00', '12:00'),   # New Year's Eve (Thu)
            ('2027-05-31', '00:00', '00:00'),   # Memorial Day, last Monday of May
            ('2027-09-06', '00:00', '00:00'),   # Labor Day, first Monday of September
        ])
        for s in specs:
            self.assertEqual(s['validFrom'], s['validThrough'])

    def test_holiday_edge_cases(self):
        m = self.mod
        start = datetime.date(2026, 9, 29)
        site = {'holidays': [
            {'name': 'Sunday closed anyway', 'month': 1, 'day': 3, 'closed': True},      # 2027-01-03 is a Sunday
            {'name': 'Wed noon close', 'month': 12, 'day': 30, 'closes': '12:00'},     # Wed opens at 12
            {'name': 'Late close', 'month': 10, 'day': 1, 'closes': '21:00'},          # later than normal: skip
            {'name': 'Bad rule', 'rule': 'sometime-soon'},
            {'name': 'Missing date', 'closed': True},
            {'name': 'TOT', 'rule': 'trick-or-treat', 'closes': '17:00'},              # no date for the year: skip
        ]}
        self.assertEqual([(s['validFrom'], s['opens'], s['closes']) for s in m.holiday_specs(site, start)],
                         [('2026-12-30', '00:00', '00:00')])
        self.assertEqual(m.nth_weekday(2026, 5, 0, -1), datetime.date(2026, 5, 25))
        self.assertEqual(m.nth_weekday(2026, 9, 0, 1), datetime.date(2026, 9, 7))

    def test_missing_site_json(self):
        self.site_json(None)
        specs = self.mod.business_full()['openingHoursSpecification']
        self.assertFalse([s for s in specs if 'validFrom' in s])
        self.assertEqual(specs, [
            self.mod.hours(['Monday', 'Tuesday'], '09:00', '20:00'), self.mod.hours('Wednesday', '12:00', '20:00'),
            self.mod.hours('Thursday', '09:00', '20:00'), self.mod.hours('Friday', '09:00', '19:00'),
            self.mod.hours('Saturday', '08:00', '15:00')])
        self.site_json({'name': 'no holidays here'})
        self.assertFalse([s for s in self.mod.business_full()['openingHoursSpecification'] if 'validFrom' in s])

    def test_real_site_json_parses(self):
        real = os.path.join(ROOT, 'tools', 'site.json')
        if not os.path.exists(real):
            self.skipTest('tools/site.json not present')
        self.mod.SITE_JSON = real
        specs = self.mod.holiday_specs(self.mod.load_site(), datetime.date(2026, 9, 29))
        for s in specs:
            datetime.date.fromisoformat(s['validFrom'])

    def test_breadcrumb_fallback(self):
        g = self.graph('policies.html', page('Policies | Bellezza', '<main><h1 class="x">Policies</h1></main>'))
        bc = self.node(g, **{'@type': 'BreadcrumbList'})
        self.assertEqual([(i['name'], i['item']) for i in bc['itemListElement']],
                         [('Home', SITE), ('Policies', SITE + 'policies.html')])

    def test_noindex_and_inline_head(self):
        d = os.path.join(self.tmp, 'edge')
        os.makedirs(d, exist_ok=True)
        thanks = page('Thank you', '<main><h1>Thanks</h1></main>').replace(
            '</head>', '<meta name="robots" content="noindex">\n<!-- schema:start x -->old<!-- schema:end -->\n</head>')
        inline = page('Policies | Bellezza', '<main><h1>Policies</h1></main>').replace('\n</head>', '</head>')
        for f, body in {'thank-you.html': thanks, 'policies.html': inline}.items():
            with open(os.path.join(d, f), 'w', encoding='utf-8', newline='\n') as fh:
                fh.write(body)
        quiet(self.mod.main, ['--root', d])
        self.assertNotIn('schema:start', read(os.path.join(d, 'thank-you.html')))
        out = read(os.path.join(d, 'policies.html'))
        self.assertEqual(out.count('<!-- schema:start'), 1)
        quiet(self.mod.main, ['--root', d])
        self.assertEqual(read(os.path.join(d, 'policies.html')), out)

    def test_writer_idempotent(self):
        d = os.path.join(self.tmp, 'pages')
        os.makedirs(d, exist_ok=True)
        pages = {'index.html': INDEX_PAGE, 'tips-and-toes.html': SERVICE_PAGE, 'our-team.html': TEAM_PAGE,
                 'job-massage-therapist.html': JOB_PAGE, 'products.html': PRODUCTS_PAGE,
                 'services.html': SERVICES_PAGE, 'about.html': ABOUT_PAGE, 'new-guests.html': NEW_GUESTS_PAGE}
        for f, body in pages.items():
            with open(os.path.join(d, f), 'w', encoding='utf-8', newline='\n') as fh:
                fh.write(body)
        quiet(self.mod.main, ['--root', d])
        once = {f: read(os.path.join(d, f)) for f in pages}
        quiet(self.mod.main, ['--root', d])
        for f in pages:
            self.assertEqual(read(os.path.join(d, f)), once[f], f)
            self.assertEqual(once[f].count('<!-- schema:start'), 1)


# ------------------------------------------------------------------ main
def main():
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--fixtures', action='store_true', help='fixture tests only')
    ap.add_argument('--regression', action='store_true', help='regression only')
    ap.add_argument('--old-script')
    ap.add_argument('--pages')
    ap.add_argument('--new-pages')
    ap.add_argument('--today')
    ap.add_argument('--strict', action='store_true')
    ap.add_argument('--show-diff', action='store_true')
    args = ap.parse_args()
    failures = 0
    if not args.regression:
        print('== fixture tests')
        result = unittest.TextTestRunner(verbosity=1).run(unittest.defaultTestLoader.loadTestsFromTestCase(Fixtures))
        failures += len(result.failures) + len(result.errors)
    if not args.fixtures:
        print('\n== regression')
        if args.today:
            os.environ['SCHEMA_TODAY'] = args.today
        failures += regression(args)
    print('\nFAILED' if failures else '\nOK')
    sys.exit(1 if failures else 0)


if __name__ == '__main__':
    main()
