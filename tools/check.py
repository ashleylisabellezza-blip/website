"""check.py: the Bellezza & Co. launch gate (REDESIGN-BRIEF.md section 3.4).

Usage (from the project root):

    python tools/check.py                 run every enabled check; exit 1 on any FAIL
    python tools/check.py --quiet         print only FAIL lines and the final count
    python tools/check.py --owner-report  print the photo-slot report and the
                                          owner-question status, then exit 0
    python tools/check.py --skip sitemap,skip-link   turn checks off for one run
    python tools/check.py --only banned-strings      run just these checks
    python tools/check.py --list          list the checks and whether they are on
    python tools/check.py --today 2026-11-01         pretend it is another day
                                                     (staleness checks)

Output lines read "FAIL <file>: <rule>: <detail>" or "WARN <file>: <rule>: <detail>",
grouped by rule. Only FAIL lines block the launch; WARN lines are for review.

Pages checked: every *.html file in the project root except PAGE-TEMPLATE.html.
Other deployed files scanned: assets/css/*.css and assets/js/*.js.
Optional input: tools/site.json (allowedNumbers, specials, trickOrTreat, reviews,
ownerAnswers). The script never writes any file, so it is safe to run any time.

Standard library only. Runs in well under a second on the whole site.
"""

import argparse
import html
import json
import os
import re
import sys
from datetime import date, datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

# ---------------------------------------------------------------------------
# The checks. Set the middle value to False to turn a check off permanently.
# (Use --skip / --only to change them for a single run.)
# ---------------------------------------------------------------------------
CHECKS = [
    # id                    on?    what it enforces
    ("h1-count",            True,  "Exactly one <h1> on every page"),
    ("heading-levels",      True,  "No skipped heading levels inside <main> (a <dialog> restarts at h2; <template> ignored)"),
    ("title-length",        True,  "<title> is 45-60 characters (noindex pages exempt)"),
    ("description-length",  True,  "Meta description is 120-160 characters (noindex pages exempt)"),
    ("duplicate-meta",      True,  "No two pages share a title or a meta description"),
    ("em-in-headings",      True,  "At most 3 <em> inside h1/h2 across the whole site"),
    ("img-attributes",      True,  "Every <img> has width, height and alt (alt may be empty)"),
    ("lazy-hero",           True,  "No loading=lazy on the first <img> in <main> or on fetchpriority=high images"),
    ("internal-links",      True,  "Every internal link resolves, including #anchors"),
    ("asset-refs",          True,  "Every local src/srcset/stylesheet/url() file exists"),
    ("tel-links",           True,  "Every tel: link is tel:+17403661604"),
    ("phone-numbers",       True,  "No phone number other than 740-366-1604 unless in site.json allowedNumbers"),
    ("price-consistency",   True,  "Same service name on two pages shows the same price (WARN; li.price-ref exempt)"),
    ("photo-slots-hidden",  True,  "Every .ph photo slot carries the hidden attribute"),
    ("white-on-gold",       True,  "No white text on a gold (#b8985f / --gold) background in the CSS"),
    ("banned-strings",      True,  "No banned mockup/legacy strings in deployed HTML, CSS or JS"),
    ("staleness",           True,  "site.json specials, trick-or-treat and review dates are current"),
    ("canonical",           True,  "<link rel=canonical> matches https://bellezzaspaonline.com/<file>"),
    ("sitemap",             True,  "Every indexable page is in sitemap.xml; no sitemap URL points to a missing file"),
    ("main-landmark",       True,  "Exactly one <main id=\"main\"> per page"),
    ("skip-link",           True,  "First focusable element in <body> is a.skip-link href=\"#main\""),
    ("owner-questions",     True,  "Launch-gating owner questions answered in site.json ownerAnswers (WARN)"),
    ("h3-parity",           True,  "Every .menu-group > h3 is byte-identical (tags stripped) to main (design branches; WARN and skip without git)"),
]

SITE = "https://bellezzaspaonline.com/"
SITE_HOSTS = {"bellezzaspaonline.com", "www.bellezzaspaonline.com"}
PHONE_TEL = "tel:+17403661604"
PHONE_DIGITS = "7403661604"
PHONE_OK_FORMS = {"740-366-1604", "740.366.1604", "(740) 366-1604"}
EXCLUDED_PAGES = {"PAGE-TEMPLATE.html"}
NOT_IN_SITEMAP = {"404.html"}
IGNORED_FRAGMENTS = {"main", "top"}
MAX_EM_IN_HEADINGS = 3

# Owner questions that gate launch (brief section 10.4), with their fallbacks.
GATING_QUESTIONS = {
    "1": ("Who runs the 'Number 1 spa in Licking County' vote; most recent year won; link or badge",
          "claim appears in the folio and on About only"),
    "2": ("GBP URL and review link; GBP name; current Google rating and count; 6 permitted reviews",
          "reviews section and rating omitted"),
    "11": ("Slay Aesthetics: legal entity, collaborating physician, license number, consult, medication, booking URL",
           "live-wording statement only, CTAs to slay-aesthetics.com"),
    "12": ("Which of the 5 jobs are open, validThrough dates, benefits, pay, hiring inbox",
           "none stated in the brief"),
    "14": ("Written permission from each staff member for photos and Instagram; client photo consent",
           "none stated in the brief"),
    "16": ("Host (Netlify or Cloudflare), Plausible cost approval, form-data privacy practices",
           "none stated in the brief"),
    "17": ("A vector logo file (SVG or AI)",
           "the raster wordmark crop"),
    "21": ("Written confirmation the Meevo Five Star flow offers the Google link after every rating",
           "link omitted; 'Review us on Google' used instead"),
}


def _phrase(p):
    """Case-insensitive regex for a literal phrase, with word boundaries only
    where the phrase begins/ends with a word character."""
    body = re.escape(p).replace(r"\ ", r"\s+")
    start = r"\b" if re.match(r"\w", p) else ""
    end = r"\b" if re.search(r"\w$", p) else ""
    return start + body + end


# Brief section 3.4, verbatim list. Matched case-insensitively.
BANNED = [
    ("522-4173", _phrase("522-4173")),
    ("522.4173", _phrase("522.4173")),
    ("5224173", _phrase("5224173")),
    ("200 Deo", _phrase("200 Deo")),
    ("Kelsey|Morgan|Abby|Tori", r"\b(?:Kelsey|Morgan|Abby|Tori)\b"),
    ("Emily R", _phrase("Emily R")),
    ("Jessica M", _phrase("Jessica M")),
    ("Caitlin B", _phrase("Caitlin B")),
    ("(c) 2024", r"©\s*2024\b"),
    ("Salon + Day Spa", _phrase("Salon + Day Spa")),
    ("20+ beauty", _phrase("20+ beauty")),
    ("more than 20", _phrase("more than 20")),
    ("a more beautiful you", _phrase("a more beautiful you")),
    ("Good Hair Brighter Days", _phrase("Good Hair Brighter Days")),
    ("Beauty Looks Good On You", _phrase("Beauty Looks Good On You")),
    ("Right here in Newark", _phrase("Right here in Newark")),
    ("Design with purpose", _phrase("Design with purpose")),
    ("from real clients", _phrase("from real clients")),
    ("Skilled hands. Kind people", _phrase("Skilled hands. Kind people")),
    ("Complete beauty. Total well-being", _phrase("Complete beauty. Total well-being")),
    ("9:00 AM - 6:00 PM", r"\b9:00\s*AM\s*[–—-]\s*6:00\s*PM\b"),
    # The brief lists the en-dash forms; hyphen and em-dash spellings of the same
    # fake hours are caught too. Real ranges (9-8, 9-7, 12-8, 8-3, 10-6) never match.
    ("9-6", r"(?<![\w.$/:,])9\s?[–—-]\s?6(?![\w:/%]|[.,]\d)"),
    ("9-4", r"(?<![\w.$/:,])9\s?[–—-]\s?4(?![\w:/%]|[.,]\d)"),
    ("Sat 9", r"\bSat(?:urday)?s?\.?,?\s+9(?!\d)"),
    ("lorem", _phrase("lorem")),
    ("ipsum", _phrase("ipsum")),
    ("Sed ut perspiciatis", _phrase("Sed ut perspiciatis")),
    ("REPLACE-ME", _phrase("REPLACE-ME")),
    ("TODO", r"\bTODO\b"),
    ("aggregateRating", _phrase("aggregateRating")),
    ("smooth away", _phrase("smooth away")),
    ("restore youthful", _phrase("restore youthful")),
    ("refreshed look", _phrase("refreshed look")),
    ("visible results", _phrase("visible results")),
    ("semaglutide", _phrase("semaglutide")),
]
BANNED_RE = [(label, re.compile(rx, re.I)) for label, rx in BANNED]
OWNER_COMMENT_RE = re.compile(r"<!--\s*OWNER:.*?-->", re.S)

PHONE_RE = re.compile(r"(?<![\d(])(?:\(\d{3}\)\s?|\d{3}[-. ])\d{3}[-.]\d{4}(?!\d)")
TEL_JS_RE = re.compile(r"(?<![\w-])tel:[^\"'\s<>)`]+")
WHITE_RE = re.compile(r"(?:#fff|#ffff|#ffffff|#ffffffff|white|var\(--white\)"
                      r"|rgba?\(255,255,255(?:,(?:1|1\.0+|100%))?\))(?:!important)?$")
CSS_URL_RE = re.compile(r"url\(\s*(['\"]?)([^'\")]+)\1\s*\)")

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta",
        "param", "source", "track", "wbr", "keygen"}
HEADINGS = {"h1": 1, "h2": 2, "h3": 3, "h4": 4, "h5": 5, "h6": 6}


# ---------------------------------------------------------------------------
# One-pass page parser
# ---------------------------------------------------------------------------
class Page(HTMLParser):
    def __init__(self, name, text):
        super().__init__(convert_charrefs=True)
        self.name = name
        self.text = text
        self.stack = []
        self.n_main = self.n_template = self.n_hidden = self.n_h12 = 0
        self.dialogs = []          # open <dialog> entries (heading context)
        self.main_prev = 1         # heading level baseline inside <main>
        self.capture = []          # open text-capture lists
        self.price_item = None

        self.title = None
        self._title_parts = None
        self.description = None
        self.robots = ""
        self.canonicals = []
        self.h1_lines = []
        self.heading_skips = []    # dicts: line, prev, level, text
        self.em_lines = []
        self.imgs = []             # (line, attrs, in_main, in_template)
        self.links = []            # (line, tag, href)
        self.assets = []           # (line, what, url)
        self.ids = set()
        self.phs = []              # (line, hidden?, data-ph, data-ph-note)
        self.price_items = []      # dicts: line, ref, name, price
        self.mains = []            # (line, id)
        self.body_seen = False
        self.first_focusable = None

        self.feed(text)
        self.close()
        while self.stack:
            self._pop()

    # -- helpers ----------------------------------------------------------
    @property
    def noindex(self):
        return "noindex" in self.robots.lower()

    def _pop(self):
        e = self.stack.pop()
        if e.get("main"):
            self.n_main -= 1
        if e.get("template"):
            self.n_template -= 1
        if e.get("hidden"):
            self.n_hidden -= 1
        if e.get("h12"):
            self.n_h12 -= 1
        if e.get("dialog"):
            self.dialogs.pop()
        if "capture" in e:
            self.capture.remove(e["capture"])
        if e.get("skip") is not None:
            e["skip"]["text"] = " ".join("".join(e["capture"]).split())[:60]
        if e.get("price_item"):
            rec = self.price_item
            rec["name"] = " ".join("".join(rec["name"]).split())
            rec["price"] = " ".join("".join(rec["price"]).split())
            self.price_items.append(rec)
            self.price_item = None
        if e.get("title"):
            self.title = " ".join("".join(self._title_parts).split())
            self._title_parts = None
        return e

    # -- parser callbacks -------------------------------------------------
    def handle_starttag(self, tag, attrs):
        a = {k: (v if v is not None else "") for k, v in attrs}
        present = {k for k, _ in attrs}
        line = self.getpos()[0]
        classes = a.get("class", "").split()
        e = {"tag": tag}

        if tag == "body":
            self.body_seen = True
        if "id" in a and not self.n_template:
            self.ids.add(a["id"])
        if tag == "a" and "name" in a and not self.n_template:
            self.ids.add(a["name"])

        # focus order: first focusable element in <body>
        if self.body_seen and self.first_focusable is None and not self.n_hidden \
                and "hidden" not in present and "disabled" not in present:
            focusable = (
                (tag in ("a", "area") and "href" in a)
                or tag in ("button", "select", "textarea", "iframe", "summary")
                or (tag == "input" and a.get("type", "").lower() != "hidden")
            )
            ti = a.get("tabindex")
            if ti is not None:
                try:
                    focusable = int(ti) >= 0
                except ValueError:
                    pass
            if focusable:
                self.first_focusable = (line, tag, a)

        if tag == "title" and self.title is None:
            self._title_parts = []
            e["title"] = True
        elif tag == "meta":
            n = a.get("name", "").lower()
            if n == "description" and self.description is None:
                self.description = " ".join(a.get("content", "").split())
            elif n == "robots":
                self.robots += " " + a.get("content", "")
        elif tag == "link":
            rel = a.get("rel", "").lower().split()
            href = a.get("href", "")
            if "canonical" in rel:
                self.canonicals.append((line, href))
            elif href and set(rel) & {"stylesheet", "icon", "preload", "apple-touch-icon",
                                      "manifest", "modulepreload", "shortcut"}:
                self.assets.append((line, "link href", href))
        elif tag == "main":
            self.mains.append((line, a.get("id")))
            e["main"] = True
        elif tag in HEADINGS and not self.n_template:
            level = HEADINGS[tag]
            if level == 1:
                self.h1_lines.append(line)
            ctx = self.dialogs[-1] if self.dialogs else None
            if ctx is not None or self.n_main:
                prev = ctx["prev"] if ctx is not None else self.main_prev
                if level > prev + 1:
                    skip = {"line": line, "prev": prev, "level": level, "text": ""}
                    self.heading_skips.append(skip)
                    e["skip"] = skip
                    e["capture"] = []
                    self.capture.append(e["capture"])
                if ctx is not None:
                    ctx["prev"] = level
                else:
                    self.main_prev = level
            if level <= 2:
                e["h12"] = True
        elif tag == "em" and self.n_h12 and not self.n_template:
            self.em_lines.append(line)
        elif tag == "img":
            self.imgs.append((line, a, present, bool(self.n_main), bool(self.n_template)))
            if a.get("src"):
                self.assets.append((line, "img src", a["src"]))
            if a.get("srcset"):
                self._srcset(line, "img srcset", a["srcset"])
        elif tag == "source":
            if a.get("srcset"):
                self._srcset(line, "source srcset", a["srcset"])
            if a.get("src"):
                self.assets.append((line, "source src", a["src"]))
        elif tag in ("script", "video", "audio", "iframe", "embed", "track"):
            if a.get("src"):
                self.assets.append((line, tag + " src", a["src"]))
            if a.get("poster"):
                self.assets.append((line, tag + " poster", a["poster"]))

        if tag in ("a", "area") and "href" in a:
            self.links.append((line, tag, a["href"].strip()))
        if "style" in a:
            for m in CSS_URL_RE.finditer(a["style"]):
                self.assets.append((line, "style url()", m.group(2).strip()))

        if "ph" in classes:
            self.phs.append((line, "hidden" in present, a.get("data-ph", ""), a.get("data-ph-note", "")))

        if tag == "li" and "price-item" in classes and self.price_item is None:
            self.price_item = {"line": line, "ref": "price-ref" in classes, "name": [], "price": []}
            e["price_item"] = True
        elif tag == "span" and self.price_item is not None and "capture" not in e:
            if "name" in classes:
                e["capture"] = self.price_item["name"]
                self.capture.append(e["capture"])
            elif "price" in classes:
                e["capture"] = self.price_item["price"]
                self.capture.append(e["capture"])

        if tag in VOID:
            return
        if tag == "template":
            e["template"] = True
            self.n_template += 1
        if "hidden" in present or tag == "template" or (tag == "dialog" and "open" not in present):
            e["hidden"] = True
            self.n_hidden += 1
        if tag == "dialog":
            e["dialog"] = True
            self.dialogs.append({"prev": 1})
        if e.get("main"):
            self.n_main += 1
        if e.get("h12"):
            self.n_h12 += 1
        self.stack.append(e)

    def _srcset(self, line, what, value):
        for part in value.split(","):
            url = part.strip().split(" ")[0]
            if url:
                self.assets.append((line, what, url))

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i]["tag"] == tag:
                while len(self.stack) > i:
                    self._pop()
                return

    def handle_data(self, data):
        if self._title_parts is not None:
            self._title_parts.append(data)
        for c in self.capture:
            c.append(data)


# ---------------------------------------------------------------------------
# Result collection
# ---------------------------------------------------------------------------
class Results:
    def __init__(self):
        self.items = []

    def fail(self, file, rule, detail):
        self.items.append(("FAIL", rule, file, detail))

    def warn(self, file, rule, detail):
        self.items.append(("WARN", rule, file, detail))

    def count(self, level):
        return sum(1 for i in self.items if i[0] == level)


def rel(path, root):
    return path.relative_to(root).as_posix()


def is_external(href):
    parts = urlsplit(href)
    if parts.scheme in ("http", "https") and parts.netloc.lower() in SITE_HOSTS:
        return False
    return bool(parts.scheme or parts.netloc)


def local_target(root, base_file, url):
    """Resolve a local URL (no scheme) to a Path; None for external URLs."""
    parts = urlsplit(url)
    if parts.scheme in ("http", "https") and parts.netloc.lower() in SITE_HOSTS:
        path = parts.path or "/"
    elif parts.scheme or parts.netloc:
        return None, parts.fragment
    else:
        path = parts.path
    path = unquote(path)
    if path == "":
        return base_file, parts.fragment
    if path.startswith("/"):
        target = root / path.lstrip("/")
    else:
        target = base_file.parent / path
    if path.endswith("/"):
        target = target / "index.html"
    return target, parts.fragment


def load_json(path, results, rule):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        results.fail(rel(path, path.parents[1]), rule, "cannot read JSON: %s" % exc)
        return None


def parse_date(value):
    if not isinstance(value, str):
        return None
    try:
        return datetime.strptime(value.strip()[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def norm_name(s):
    s = html.unescape(s).replace("’", "'").replace("‘", "'").lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return " ".join(s.split())


def norm_price(s):
    s = re.sub(r"\s*[–—-]\s*", "-", s)
    return " ".join(s.split())


def expected_canonical(name):
    return SITE if name == "index.html" else SITE + name


# ---------------------------------------------------------------------------
# The checks
# ---------------------------------------------------------------------------
def run_checks(root, enabled, today):
    R = Results()
    on = enabled.__contains__
    tools = root / "tools"
    site = load_json(tools / "site.json", R, "staleness") or {}
    if not isinstance(site, dict):
        site = {}

    page_files = sorted(p for p in root.glob("*.html") if p.name not in EXCLUDED_PAGES)
    pages = {}
    for p in page_files:
        pages[p.name] = Page(p.name, p.read_text(encoding="utf-8", errors="replace"))
    extra_pages = {}

    def ids_of(path):
        if path.name in pages and path.parent == root:
            return pages[path.name].ids
        key = str(path)
        if key not in extra_pages:
            extra_pages[key] = Page(path.name, path.read_text(encoding="utf-8", errors="replace")).ids
        return extra_pages[key]

    listing = {}

    def exact(path):
        """True if path exists with exactly this spelling. Windows is
        case-insensitive but the web host is not, so 'Our-Team.html' must fail."""
        p = Path(os.path.normpath(os.path.abspath(path)))
        try:
            parts = p.relative_to(root).parts
        except ValueError:
            return p.exists()
        cur = root
        for part in parts:
            if cur not in listing:
                try:
                    listing[cur] = set(os.listdir(cur))
                except OSError:
                    listing[cur] = set()
            if part not in listing[cur]:
                return False
            cur = cur / part
        return True

    def resolve_file(path):
        """(ok, why) for a local URL target: it must be a file (or a folder
        holding index.html) spelled with the exact letter case used on disk."""
        if path.is_dir():
            path = path / "index.html"
        if not path.is_file():
            return False, "file not found"
        if not exact(path):
            return False, "letter case differs from the file on disk (breaks on the web host)"
        return True, ""

    css_files = sorted((root / "assets" / "css").glob("*.css"))
    js_files = sorted((root / "assets" / "js").glob("*.js"))

    for name, pg in pages.items():
        # h1-count
        if on("h1-count") and len(pg.h1_lines) != 1:
            where = (" (lines %s)" % ", ".join(map(str, pg.h1_lines))) if pg.h1_lines else ""
            R.fail(name, "h1-count", "found %d <h1>%s" % (len(pg.h1_lines), where))

        # heading-levels
        if on("heading-levels"):
            for s in pg.heading_skips:
                R.fail(name, "heading-levels", "line %d: h%d follows h%d (\"%s\")"
                       % (s["line"], s["level"], s["prev"], s["text"]))

        # title / description lengths
        if on("title-length"):
            if not pg.title:
                R.fail(name, "title-length", "missing <title>")
            elif not pg.noindex and not 45 <= len(pg.title) <= 60:
                R.fail(name, "title-length", "%d chars (45-60): \"%s\"" % (len(pg.title), pg.title))
        if on("description-length") and not pg.noindex:
            if not pg.description:
                R.fail(name, "description-length", "missing <meta name=\"description\">")
            elif not 120 <= len(pg.description) <= 160:
                R.fail(name, "description-length", "%d chars (120-160): \"%s\""
                       % (len(pg.description), pg.description))

        # img-attributes / lazy-hero
        if on("img-attributes"):
            for line, a, present, _, _ in pg.imgs:
                missing = [k for k in ("width", "height", "alt") if k not in present]
                if missing:
                    R.fail(name, "img-attributes", "line %d: <img src=\"%s\"> missing %s"
                           % (line, a.get("src", ""), ", ".join(missing)))
        if on("lazy-hero"):
            first_main = next((i for i in pg.imgs if i[3] and not i[4]), None)
            for img in pg.imgs:
                line, a = img[0], img[1]
                if a.get("loading", "").lower() != "lazy":
                    continue
                if img is first_main:
                    R.fail(name, "lazy-hero", "line %d: first image in <main> is loading=lazy (%s)"
                           % (line, a.get("src", "")))
                elif a.get("fetchpriority", "").lower() == "high":
                    R.fail(name, "lazy-hero", "line %d: fetchpriority=high image is loading=lazy (%s)"
                           % (line, a.get("src", "")))

        # internal-links / tel-links
        page_path = root / name
        for line, tag, href in pg.links:
            low = href.lower()
            if low.startswith("tel:"):
                if on("tel-links") and href != PHONE_TEL:
                    R.fail(name, "tel-links", "line %d: href=\"%s\" (must be %s)" % (line, href, PHONE_TEL))
                continue
            if not on("internal-links"):
                continue
            if href == "#":
                R.fail(name, "internal-links", "line %d: href=\"#\" goes nowhere" % line)
                continue
            if href == "":
                R.fail(name, "internal-links", "line %d: empty href" % line)
                continue
            if low.startswith(("javascript:", "mailto:", "sms:", "data:")) or is_external(href):
                continue
            target, frag = local_target(root, page_path, href)
            if target is None:
                continue
            ok, why = resolve_file(target)
            if not ok:
                R.fail(name, "internal-links", "line %d: %s -> %s" % (line, href, why))
                continue
            frag = unquote(frag)
            if not frag or frag in IGNORED_FRAGMENTS or frag.startswith(":~:"):
                continue
            if target.name == "our-team.html" and frag.startswith("filter-"):
                continue
            if target.suffix.lower() == ".html" and target.is_file():
                if frag not in ids_of(target):
                    R.fail(name, "internal-links", "line %d: %s -> no id=\"%s\" in %s"
                           % (line, href, frag, target.name))

        # asset-refs
        if on("asset-refs"):
            for line, what, url in pg.assets:
                if url.startswith(("data:", "#", "blob:")) or is_external(url):
                    continue
                target, _ = local_target(root, page_path, url.split("?")[0])
                if target is not None:
                    ok, why = resolve_file(target)
                    if not ok:
                        R.fail(name, "asset-refs", "line %d: %s \"%s\": %s" % (line, what, url, why))

        # photo-slots-hidden
        if on("photo-slots-hidden"):
            for line, hidden, ph, note in pg.phs:
                if not hidden:
                    R.fail(name, "photo-slots-hidden", "line %d: .ph slot %s is visible (add hidden)"
                           % (line, ph or "(no data-ph)"))

        # canonical
        if on("canonical"):
            want = expected_canonical(name)
            if not pg.canonicals:
                (R.warn if pg.noindex else R.fail)(name, "canonical", "missing <link rel=\"canonical\">")
            elif len(pg.canonicals) > 1:
                R.fail(name, "canonical", "%d canonical links" % len(pg.canonicals))
            elif pg.canonicals[0][1] != want:
                R.fail(name, "canonical", "href=\"%s\" (expected %s)" % (pg.canonicals[0][1], want))

        # main-landmark
        if on("main-landmark"):
            if len(pg.mains) != 1:
                R.fail(name, "main-landmark", "found %d <main> elements" % len(pg.mains))
            elif pg.mains[0][1] != "main":
                R.fail(name, "main-landmark", "line %d: <main> has id=%r (expected \"main\")"
                       % (pg.mains[0][0], pg.mains[0][1]))

        # skip-link
        if on("skip-link"):
            ff = pg.first_focusable
            if ff is None:
                R.fail(name, "skip-link", "no focusable element in <body>")
            else:
                line, tag, a = ff
                if not (tag == "a" and "skip-link" in a.get("class", "").split() and a.get("href") == "#main"):
                    desc = "<%s%s%s>" % (tag, (' class="%s"' % a["class"]) if a.get("class") else "",
                                         (' href="%s"' % a["href"]) if "href" in a else "")
                    R.fail(name, "skip-link", "line %d: first focusable element is %s, not a.skip-link href=\"#main\""
                           % (line, desc))

    # duplicate-meta (site-wide)
    if on("duplicate-meta"):
        for field, label in (("title", "title"), ("description", "description")):
            seen = {}
            for name, pg in pages.items():
                v = getattr(pg, field)
                if v:
                    seen.setdefault(v.lower(), []).append(name)
            for v, names in seen.items():
                if len(names) > 1:
                    for n in names:
                        R.fail(n, "duplicate-meta", "same %s as %s" % (label, ", ".join(x for x in names if x != n)))

    # em-in-headings (site-wide)
    if on("em-in-headings"):
        total = [(n, l) for n, pg in pages.items() for l in pg.em_lines]
        if len(total) > MAX_EM_IN_HEADINGS:
            R.fail("(site)", "em-in-headings", "%d <em> inside h1/h2 (max %d): %s"
                   % (len(total), MAX_EM_IN_HEADINGS, ", ".join("%s:%d" % t for t in total)))

    # price-consistency (site-wide, WARN)
    if on("price-consistency"):
        by_name = {}
        for name, pg in pages.items():
            for it in pg.price_items:
                if it["ref"] or not it["name"]:
                    continue
                by_name.setdefault(norm_name(it["name"]), []).append((name, it))
        for key, entries in sorted(by_name.items()):
            prices = {norm_price(it["price"]) for _, it in entries}
            files = {n for n, _ in entries}
            if len(prices) > 1 and len(files) > 1:
                desc = "; ".join("%s:%d %s" % (n, it["line"], it["price"]) for n, it in entries)
                R.warn(entries[0][0], "price-consistency", "\"%s\" priced differently: %s"
                       % (entries[0][1]["name"], desc))

    # h3-parity (DESIGN-OPTIONS section 0): group heads may gain spans in a design branch,
    # but their text must stay byte-identical to main, because the schema and the stamped
    # ranges read them. Compared with `git show main:<file>`; skipped when that fails.
    if on("h3-parity"):
        import subprocess

        def menu_h3s(text):
            out = []
            starts = [m.end() for m in re.finditer(r'<div\b[^>]*class="menu-group\b[^"]*"[^>]*>', text)]
            for i, a in enumerate(starts):
                b = starts[i + 1] if i + 1 < len(starts) else len(text)
                m = re.search(r"<h3\b[^>]*>(.*?)</h3>", text[a:b], re.S)
                if m:
                    out.append(html.unescape(re.sub(r"<[^>]+>", "", m.group(1))))
            return out

        skipped = None
        for name, pg in sorted(pages.items()):
            here = menu_h3s(pg.text)
            if not here:
                continue
            try:
                r = subprocess.run(["git", "show", "main:" + name], cwd=str(root), capture_output=True, timeout=20)
            except (OSError, subprocess.SubprocessError) as e:
                skipped = str(e)
                break
            if r.returncode != 0:
                if b"exists on disk, but not in" in r.stderr or b"does not exist in" in r.stderr:
                    continue  # a page that main does not have
                skipped = r.stderr.decode("utf-8", "replace").strip().splitlines()[0] if r.stderr else "git show failed"
                break
            there = menu_h3s(r.stdout.decode("utf-8", "replace"))
            if here != there:
                for i in range(max(len(here), len(there))):
                    a = here[i] if i < len(here) else "(none)"
                    b = there[i] if i < len(there) else "(none)"
                    if a != b:
                        R.fail(name, "h3-parity", "group head %d is %r here but %r on main" % (i + 1, a, b))
                        break
        if skipped:
            R.warn("(site)", "h3-parity", "skipped: main not readable with git (%s)" % skipped)

    # sitemap
    if on("sitemap"):
        sm = root / "sitemap.xml"
        if not sm.exists():
            R.fail("sitemap.xml", "sitemap", "sitemap.xml not found")
        else:
            locs = re.findall(r"<loc>\s*(.*?)\s*</loc>", sm.read_text(encoding="utf-8"))
            listed = set()
            for loc in locs:
                if not loc.startswith(SITE):
                    R.fail("sitemap.xml", "sitemap", "URL outside the site: %s" % loc)
                    continue
                f = unquote(loc[len(SITE):].split("#")[0].split("?")[0]) or "index.html"
                listed.add(f)
                ok, why = resolve_file(root / f)
                if not ok:
                    R.fail("sitemap.xml", "sitemap", "%s -> %s: %s" % (loc, f, why))
                elif f in pages and pages[f].noindex:
                    R.warn("sitemap.xml", "sitemap", "%s is noindex but listed" % loc)
            for name, pg in pages.items():
                if name in NOT_IN_SITEMAP or pg.noindex:
                    continue
                if name not in listed:
                    R.fail(name, "sitemap", "not listed in sitemap.xml")

    # deployed text files (pages + CSS + JS) for strings and numbers
    deployed = [(root / n, pg.text, True) for n, pg in pages.items()]
    deployed += [(p, p.read_text(encoding="utf-8", errors="replace"), False) for p in css_files + js_files]

    allowed_digits = set()
    for entry in site.get("allowedNumbers", []) or []:
        num = entry.get("number", "") if isinstance(entry, dict) else str(entry)
        d = re.sub(r"\D", "", num)
        if len(d) == 11 and d.startswith("1"):
            d = d[1:]
        if d:
            allowed_digits.add(d)

    for path, raw, is_html in deployed:
        fname = rel(path, root)
        text = html.unescape(raw) if is_html else raw

        if on("banned-strings"):
            owner_spans = [m.span() for m in OWNER_COMMENT_RE.finditer(text)] if is_html else []
            for label, rx in BANNED_RE:
                for m in rx.finditer(text):
                    if label == "TODO" and any(s <= m.start() < e for s, e in owner_spans):
                        continue
                    line = text.count("\n", 0, m.start()) + 1
                    R.fail(fname, "banned-strings", "line %d: \"%s\" (rule: %s)" % (line, m.group(0), label))

        if on("phone-numbers"):
            for m in PHONE_RE.finditer(text):
                s = m.group(0)
                d = re.sub(r"\D", "", s)
                if s in PHONE_OK_FORMS or d in allowed_digits:
                    continue
                line = text.count("\n", 0, m.start()) + 1
                why = "non-standard format of our number" if d == PHONE_DIGITS else "not in site.json allowedNumbers"
                R.fail(fname, "phone-numbers", "line %d: \"%s\" (%s)" % (line, s, why))

        if on("tel-links") and not is_html:
            for m in TEL_JS_RE.finditer(text):
                if m.group(0) != PHONE_TEL:
                    line = text.count("\n", 0, m.start()) + 1
                    R.fail(fname, "tel-links", "line %d: \"%s\" (must be %s)" % (line, m.group(0), PHONE_TEL))

    # CSS: white-on-gold and url() assets
    for css in css_files:
        raw = css.read_text(encoding="utf-8", errors="replace")
        fname = rel(css, root)
        clean = re.sub(r"/\*.*?\*/", lambda m: "\n" * m.group(0).count("\n"), raw, flags=re.S)
        if on("white-on-gold"):
            for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", clean):
                sel, body = m.group(1).strip(), m.group(2)
                gold = white = False
                for decl in body.split(";"):
                    if ":" not in decl:
                        continue
                    prop, val = decl.split(":", 1)
                    prop, val = prop.strip().lower(), val.strip().lower().replace(" ", "")
                    if prop in ("background", "background-color") and (
                            re.search(r"var\(--gold\)", val) or "#b8985f" in val):
                        gold = True
                    elif prop == "color" and WHITE_RE.match(val):
                        white = True
                if gold and white:
                    line = clean.count("\n", 0, m.start(2)) + 1
                    R.fail(fname, "white-on-gold", "line %d: `%s` sets white text on gold" % (line, " ".join(sel.split())))
        if on("asset-refs"):
            for m in CSS_URL_RE.finditer(clean):
                url = m.group(2).strip()
                if url.startswith(("data:", "#")) or is_external(url):
                    continue
                target, _ = local_target(root, css, url.split("?")[0])
                if target is not None:
                    ok, why = resolve_file(target)
                    if not ok:
                        line = clean.count("\n", 0, m.start()) + 1
                        R.fail(fname, "asset-refs", "line %d: url(%s): %s" % (line, url, why))

    # staleness (site.json)
    if on("staleness"):
        if not (tools / "site.json").exists():
            R.warn("tools/site.json", "staleness", "not found; specials/trick-or-treat/review checks skipped")
        else:
            specials = site.get("specials") or []
            if isinstance(specials, dict):
                specials = [dict(v, name=k) if isinstance(v, dict) else {"name": k} for k, v in specials.items()]
            for i, sp in enumerate(specials):
                if not isinstance(sp, dict):
                    continue
                label = sp.get("name") or sp.get("title") or sp.get("id") or "#%d" % (i + 1)
                ends = sp.get("ends")
                if ends is None:
                    R.warn("tools/site.json", "staleness", "special \"%s\" has no end date (ends: null)" % label)
                    continue
                d = parse_date(ends)
                if d is None:
                    R.fail("tools/site.json", "staleness", "special \"%s\" has an unreadable end date %r" % (label, ends))
                elif d < today:
                    R.fail("tools/site.json", "staleness", "special \"%s\" ended %s" % (label, d.isoformat()))
            if today >= date(today.year, 9, 1):
                tot = site.get("trickOrTreat")
                if str(today.year) not in json.dumps(tot):
                    R.warn("tools/site.json", "staleness", "trickOrTreat has no %d entry (owner question 10)" % today.year)
            reviews = site.get("reviews")
            if isinstance(reviews, dict):
                for k in ("asOf", "date", "updated", "ratingDate"):
                    d = parse_date(reviews.get(k))
                    if d:
                        if (today - d).days > 90:
                            R.warn("tools/site.json", "staleness", "review rating/count dated %s is over 90 days old"
                                   % d.isoformat())
                        break

    # owner-questions (WARN)
    if on("owner-questions"):
        answers = site.get("ownerAnswers") or {}
        for q in GATING_QUESTIONS:
            if not answers.get(q):
                R.warn("tools/site.json", "owner-questions", "gating question %s unanswered: %s"
                       % (q, GATING_QUESTIONS[q][0]))

    return R, pages, site


# ---------------------------------------------------------------------------
# Reports and output
# ---------------------------------------------------------------------------
def owner_report(pages, site):
    out = []
    slots = [(ph, name, line, note, hidden) for name, pg in pages.items() for line, hidden, ph, note in pg.phs]
    slots.sort(key=lambda s: (s[0].zfill(4), s[1], s[2]))
    out.append("PHOTO SLOTS (%d)  -- see the shot list in docs/REDESIGN-BRIEF.md section 10.5" % len(slots))
    if not slots:
        out.append("  (no .ph photo slots on any page yet)")
    for ph, name, line, note, hidden in slots:
        out.append("  Shot %-4s %-28s line %-5d %s%s" % (ph or "?", name, line, note or "(no data-ph-note)",
                                                        "" if hidden else "   [VISIBLE: missing hidden]"))
    out.append("")
    answers = site.get("ownerAnswers") or {}
    open_q = [q for q in GATING_QUESTIONS if not answers.get(q)]
    out.append("OWNER QUESTIONS THAT GATE LAUNCH (brief section 10.4): %d of %d unanswered"
               % (len(open_q), len(GATING_QUESTIONS)))
    if not answers:
        out.append("  (no answers recorded yet: add \"ownerAnswers\": {\"1\": true, ...} to tools/site.json)")
    for q, (text, fallback) in GATING_QUESTIONS.items():
        state = "answered  " if answers.get(q) else "UNANSWERED"
        out.append("  Q%-3s %s  %s" % (q, state, text))
        if not answers.get(q):
            out.append("        fallback: %s" % fallback)
    return "\n".join(out)


def print_results(R, quiet):
    order = [c[0] for c in CHECKS]
    items = sorted(R.items, key=lambda i: (order.index(i[1]), i[0] != "FAIL", i[2]))
    if quiet:
        for level, rule, file, detail in items:
            if level == "FAIL":
                print("FAIL %s: %s: %s" % (file, rule, detail))
    else:
        desc = {c[0]: c[2] for c in CHECKS}
        current = None
        for level, rule, file, detail in items:
            if rule != current:
                current = rule
                print("\n== %s: %s" % (rule, desc[rule]))
            print("%s %s: %s: %s" % (level, file, rule, detail))
        print("\n== Summary (FAIL / WARN per rule)")
        for rid, _, _ in CHECKS:
            f = sum(1 for i in R.items if i[1] == rid and i[0] == "FAIL")
            w = sum(1 for i in R.items if i[1] == rid and i[0] == "WARN")
            print("  %-20s %4d / %-4d%s" % (rid, f, w, "" if (f or w) else "  ok"))


def main(argv=None):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    ap = argparse.ArgumentParser(description="Bellezza & Co. launch gate (brief section 3.4).")
    ap.add_argument("--quiet", action="store_true", help="print only FAIL lines and the final count")
    ap.add_argument("--owner-report", action="store_true", help="print the photo-slot and owner-question reports only")
    ap.add_argument("--skip", default="", help="comma-separated check ids to turn off for this run")
    ap.add_argument("--only", default="", help="comma-separated check ids to run (all others off)")
    ap.add_argument("--list", action="store_true", help="list the checks and exit")
    ap.add_argument("--today", default="", help="YYYY-MM-DD to use as today (staleness checks)")
    ap.add_argument("--root", default="", help=argparse.SUPPRESS)
    args = ap.parse_args(argv)

    ids = [c[0] for c in CHECKS]
    if args.list:
        for rid, enabled, text in CHECKS:
            print("%-3s %-20s %s" % ("on" if enabled else "off", rid, text))
        return 0

    enabled = {rid for rid, en, _ in CHECKS if en}
    for opt in (args.skip, args.only):
        for rid in filter(None, (s.strip() for s in opt.split(","))):
            if rid not in ids:
                ap.error("unknown check %r (see --list)" % rid)
    if args.only:
        enabled = {s.strip() for s in args.only.split(",") if s.strip()}
    enabled -= {s.strip() for s in args.skip.split(",") if s.strip()}

    today = parse_date(args.today) if args.today else date.today()
    if today is None:
        ap.error("--today must be YYYY-MM-DD")
    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parent.parent

    if args.owner_report:
        _, pages, site = run_checks(root, set(), today)
        print(owner_report(pages, site))
        return 0

    R, pages, site = run_checks(root, enabled, today)
    print_results(R, args.quiet)
    fails, warns = R.count("FAIL"), R.count("WARN")
    if not args.quiet:
        n_slots = sum(len(pg.phs) for pg in pages.values())
        answers = site.get("ownerAnswers") or {}
        n_open = sum(1 for q in GATING_QUESTIONS if not answers.get(q))
        print("\nOwner: %d photo slot(s); %d launch-gating question(s) unanswered. Run with --owner-report for details."
              % (n_slots, n_open))
    print("check.py: %d page(s), %d FAIL, %d WARN -> %s"
          % (len(pages), fails, warns, "BLOCKED" if fails else "PASS"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
