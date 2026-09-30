# Page authoring guide

How to write or edit a page so it works with the build (`python tools/build.py`),
the stylesheet and the structured-data generator. The full design rationale is
in `REDESIGN-BRIEF.md`; this file is the practical contract. `index.html` is the
reference implementation: copy its patterns.

## 1. Skeleton (every page)

```html
<!DOCTYPE html>
<html lang="en">
<head>
<!-- partial:head:start -->
<!-- partial:head:end -->
</head>
<body>
<!-- partial:top:start -->
<!-- partial:top:end -->
<main id="main" tabindex="-1">
<!-- partial:breadcrumb:start -->
<!-- partial:breadcrumb:end -->

  ...page sections...

</main>
<!-- partial:bottom:start -->
<!-- partial:bottom:end -->
</body>
</html>
```

- The build fills the markers: `<title>`, meta description, canonical, fonts and
  CSS (head), the utility bar, header, nav and mobile menu (top), the breadcrumb,
  the booking band, footer, mobile Book/Call bar and scripts (bottom). Never write
  any of those by hand, and never put content inside the markers.
- Titles, descriptions, breadcrumb parents and the page's Book label live in
  `tools/pages.json`. Business facts live in `tools/site.json`.
- The home page has no breadcrumb markers. Every other page has them.
- `<!-- partial:hours:start --><!-- partial:hours:end -->` stamps the weekly
  hours table; `<!-- partial:holidays:start --><!-- partial:holidays:end -->`
  stamps the upcoming holiday table.
- JSON-LD is added afterwards by `tools/build-schema.py` (between
  `<!-- schema:start` and `<!-- schema:end -->` in the head). Don't write any.

## 2. Hard rules

- **Facts only.** Use only facts in `REDESIGN-BRIEF.md` §10.2 and in the current
  page content. No invented reviews, stats, credentials, parking, response times,
  outcomes. Missing photo → leave it out (optionally add a hidden photo slot, §5).
- **Gold = booking at Bellezza.** `.btn--book` only for links to the Meevo booking
  URL (`https://login.meevo.com/bellezza/ob?locationId=103245`) with
  `data-book data-cta="book" data-placement="…"`. Other primary actions use
  `.btn--strong` (ink). Secondary: `.btn--outline`. Never two gold buttons in one view.
- **Button labels:** sentence case, no arrows, never "Learn more", "Click here",
  "Submit". Call buttons show the digits: "Call 740-366-1604". Links to the phone are
  exactly `tel:+17403661604`.
- **Headings:** exactly one `<h1>`; no skipped levels (h1 → h2 → h3). Eyebrows are
  `<p class="eyebrow">`, never headings. No `<em>` in headings (only 3 allowed
  site-wide and they are used on home and about).
- **Nothing centered.** Left-aligned layouts only. No carousels, sliders, parallax,
  scroll animation, icon rows, testimonials, stock photos, or the retired room
  photos (`services/mani-room.jpg`, `manicure.jpg`, `facial-room.jpg`, `facial.jpg`,
  `massage.jpg`, `derma.jpg`), `hero-*.jpg`, `tile-*.jpg`, `about-*.png`,
  `search-bg.jpg`, `footer-bg.jpg`, `banner-interior.jpg`.
- **Images:** every `<img>` has `width`, `height` and `alt` (`alt=""` if decorative).
  First image in `<main>` is NOT `loading="lazy"`; all others are
  `loading="lazy" decoding="async"`. Use `<picture>` with AVIF + WebP + JPEG.
- **Links:** internal links are relative file names (`salon.html`,
  `our-team.html#devon`). Every `#anchor` must exist in the target page.
- **Copy audit (brief §10.6):** remove health/efficacy claims when reusing copy:
  spray tan "micro-nutrient technology… vitamins and antioxidants" and "works with
  all skin types regardless of color or tone"; mother-to-be symptom list (keep "2nd
  and 3rd trimester; side-lying with supportive pillows"); "visible results";
  every Slay outcome phrase ("smooth away", "restore youthful contours",
  "refreshed look", "effectively support") and the drug name "Semaglutide";
  "secure" in process descriptions. Fix "Brazillian" → "Brazilian".
- Owner-facing notes go in HTML comments starting `<!-- OWNER: … -->`.

## 3. Page head (inner pages)

```html
<section class="page-head" aria-labelledby="page-h">
  <div class="container grid-7-5">
    <div>
      <p class="eyebrow">Tips &amp; Toes</p>
      <h1 id="page-h">Manicures &amp; Pedicures</h1>
      <p class="lede">Two or three sentences from the existing intro, audited.</p>
      <p class="range">Gel manicures <span data-from="tips-and-toes.html#gel-manicure-without-removal">from $44</span> · Pedicures <span data-from="tips-and-toes.html#pedicures">from $35</span></p>
      <div class="btn-row" data-hero-ctas>
        <a class="btn btn--book" href="https://login.meevo.com/bellezza/ob?locationId=103245" data-book data-cta="book" data-placement="head">Book nails</a>
        <a class="btn btn--outline" href="tel:+17403661604" data-cta="call" data-placement="head">Call 740-366-1604</a>
      </div>
      <p class="microcopy">Book online 24/7 on our online booking page (Meevo), in the Bellezza app, or call us. Changes need 24 hours&rsquo; notice. <a href="policies.html#changes">Policies</a></p>
    </div>
    <figure class="head-media">…portrait(s) or nothing (no-image variant)…</figure>
  </div>
</section>
```

`data-hero-ctas` marks the CTA row the mobile bottom bar waits to scroll past.
No-image variant: drop the `<figure>`; the grid collapses to one column.

## 4. Components (use these classes; the CSS exists)

**Portrait (team member, 3:4):**
```html
<picture><source type="image/avif" srcset="assets/img/team/devon-360.avif 360w, assets/img/team/devon-540.avif 540w" sizes="(min-width:1024px) 22vw, 46vw"><source type="image/webp" srcset="assets/img/team/devon-360.webp 360w, assets/img/team/devon-540.webp 540w" sizes="(min-width:1024px) 22vw, 46vw"><img src="assets/img/team/devon-360.jpg" srcset="assets/img/team/devon-360.jpg 360w, assets/img/team/devon-540.jpg 540w" sizes="(min-width:1024px) 22vw, 46vw" width="360" height="480" alt="Devon, Salon Manager and Master Stylist" loading="lazy" decoding="async"></picture>
```
Sizes available for every team slug: `-180`, `-360`, `-540` in `.avif`, `.webp`,
`.jpg` (180 = 180×240, 360 = 360×480, 540 = 540×720).

**Team slugs** (also the `id` of each card on `our-team.html`):
ashley-basham, lisa-jeffries, devon, stephanie, janet, moriah, emilie, austyn,
lizbeth, cherish, liv, taylor-f, mya, kat, paige, madison, shelbi, raegan, rissa,
hope, jesyca, emma, mia, shannon-francis, melissa, aubree, grace, aeriannah.

**Artists strip** (service pages):
```html
<section class="section section--tight artists" aria-labelledby="artists-h">
  <div class="container">
    <h2 id="artists-h">Your artists for this service</h2>
    <ul>
      <li><a href="our-team.html#stephanie"><img src="assets/img/team/stephanie-180.jpg" width="56" height="75" alt="" loading="lazy" decoding="async"><span><b>Stephanie</b><small>Spa Manager &amp; Expert Nail Artist</small></span></a></li>
      …
      <li class="meet-all"><a class="text-link" href="our-team.html#filter-nails" style="display:inline">Meet all nail artists</a></li>
    </ul>
  </div>
</section>
```

**Price menu** — the structured-data parser depends on this exact shape:
```html
<section class="section" aria-labelledby="prices">
  <div class="container">
    <h2 id="prices">Menu &amp; prices</h2>
    <p class="level-legend">Prices depend on your provider&rsquo;s level: <a href="new-guests.html#level-associate">Associate</a> · <a href="new-guests.html#level-senior">Senior</a> · <a href="new-guests.html#level-expert">Expert</a>. Levels set the price.</p>

    <div class="menu-group" id="manicures">
      <h3>Manicures</h3>
      <p class="group-intro">Optional group intro.</p>
      <p class="tier-head" id="tiers-manicures">Associate / Senior / Expert</p>
      <ul class="price-list" aria-describedby="tiers-manicures">
        <li class="price-item" id="classic-manicure">
          <div class="price-head"><span class="name">Classic Manicure</span><span class="dots"></span><span class="price">$31 / 37 / 40</span></div>
          <p>Description.</p>
          <p class="note">Optional item note, e.g. Consultation required · $50 deposit</p>
        </li>
      </ul>
      <a class="book-this" href="https://login.meevo.com/bellezza/ob?locationId=103245" data-book data-cta="book" data-placement="menu-manicures">Book a manicure</a>
    </div>

    <time data-asof></time>
    <p class="policy-strip">24-hour notice for changes · Repeat no-shows may require a deposit · <a href="policies.html">Full policies</a></p>
  </div>
</section>
```
- Keep every service name, price text and description exactly as on the current
  page (after the copy audit). Never put anything inside `span.price`.
- Level ladder (groups whose rows are stylist levels, salon page only):
  `<ul class="price-list price-list--ladder">`, and wrap the word "Stylist" in
  `<span class="lvl-suffix"> Stylist</span>` (e.g. `Senior<span class="lvl-suffix"> Stylist</span>`).
  Use `cols-4` on the 4-row men's group.
- Price text "$$" renders as "Priced at consultation" (keep it in span.price as
  "Priced at consultation"); add `<p class="note">Consultation required</p>`.
- Jump chips (pages with 3+ groups), placed right after the `<h2 id="prices">`:
```html
<nav class="jump-chips" aria-label="On this page"><div class="container"><span class="chips-label">On this page</span><ul class="chips"><li><a href="#manicures">Manicures</a></li>…</ul></div></nav>
```
  The jump-chips nav must be OUTSIDE `.container` of the section (close the
  container before it and reopen after), so it can span the viewport.

**Required ids** (the home page and nav read prices from these; keep exactly):

| Page | Group ids (`div.menu-group`) | Item ids (`li.price-item`) |
|---|---|---|
| salon.html | cuts-women, cuts-men, styling, color-all-over, color-root, color-mini-foil, color-partial-foil, color-all-over-foils, color-hi-impact, color-specialized, color-platinum, fantasy, add-ons, texture, treatments | — (section `id="extensions"` for Hair Extensions) |
| tips-and-toes.html | manicures, pedicures, add-ons | classic-manicure, gel-manicure-with-removal, gel-manicure-without-removal, classic-pedicure |
| massages.html | relaxation, reflexology, deep-tissue, hot-stone, ashiatsu, mother-to-be | — |
| facials.html | facials | focus-facial, custom-signature-facial, mens-fitness-facial |
| hair-removal.html | waxing | eyebrows, full-leg, brazilian |
| makeup-and-eyes.html | brows, brows-lashes, makeup | brow-lamination, eyelash-lift, special-occasion-makeup |
| spray-tans.html | spray-tans | single-spray, package-of-3, half-body |
| mens-care.html | mens | — |
| brides.html | bridal-hair, bridal-makeup-group | bridal-hair-style, bridal-makeup |
| slay-aesthetics.html | wrinkle-relaxers, dermal-filler, weight-loss | botox |

**Live values** (filled by the build from the pages; write a sensible default):
`<span data-count="team">28</span>`, `data-count="providers"`, `data-count="dept-hair"`
(and dept-nails, dept-skin, dept-massage, dept-makeup, dept-client-services…);
`<span data-range="salon.html#cuts-women">$37–60</span>`;
`<span data-from="massages.html">from $42</span>`; `<time data-asof></time>`;
`<time data-team-updated></time>`.

**Status line:** `<span data-status="name" hidden></span>` becomes "Open now · until
8pm" etc.

**FAQ:** `<div class="faq"><details name="faq-PAGE"><summary>Question</summary><div><p>Answer.</p></div></details>…</div>` (answers quoted from Policies; no FAQ schema).

**Related services:** `<ul class="link-list"><li><a href="facials.html">Dermalogica facials<small>from $55</small></a></li>…</ul>`

**Before/after:** see `.ba` in CSS: `<figure class="ba"><figure>…img…<span class="ba-label">Before</span></figure><figure>…<span class="ba-label">After</span></figure><figcaption>…</figcaption></figure>`.

**Quiz callout:** `<div class="quiz-callout"><h2>Not sure who to book? Find your match.</h2><p>…</p><p><a class="btn btn--strong" href="https://app.joinmya.com/bellezza" data-cta="quiz" data-placement="…">Take the match quiz</a></p><p>Or call <a href="tel:+17403661604">740-366-1604</a> and our front desk will match you.</p></div>` (heading level fits context).

**Gift section** (massages, facials, spray-tans): copy the home `.gift` section but
without `hidden`/`data-gift-season`.

**Forms** (Netlify Forms): `<form class="form" name="bridal-inquiry" method="POST" action="/thank-you.html" data-netlify="true" netlify-honeypot="bot-field" data-success-title="…" data-success="…">`
with `<input type="hidden" name="form-name" value="bridal-inquiry">` and
`<p hidden><label>Don’t fill this out: <input name="bot-field" autocomplete="off" tabindex="-1"></label></p>`.
Fields: `<div class="field"><label for="x">Label</label><input id="x" name="x" …></div>`,
groups `<fieldset class="fieldset"><legend>…</legend><div class="choices"><label><input type="radio" …> Text</label>…</div></fieldset>`,
optional fields labeled `<span class="opt">(optional)</span>`, required fields get
`required` (no asterisk), `autocomplete` tokens. End with
`<p class="privacy-note">How we use this information: <a href="policies.html#privacy">privacy</a>.</p>`
and `<button class="btn btn--strong" type="submit">Send inquiry</button>` (never "Submit").

**Photo slot** (owner-only, never public): `<div class="ph" hidden aria-hidden="true" data-ph="03" data-ph-note="Gel application close-up, 4:5, min 1600px" style="--ar:4/5"></div>`.

## 5. Available real images

- Team portraits: `assets/img/team/{slug}-{180,360,540}.{avif,webp,jpg}`.
- Owners: as above (`lisa-jeffries`, `ashley-basham`).
- About: `assets/img/about/team-group-{560,1120}.{avif,webp,jpg}` (4:3, whole team).
- Careers: `assets/img/join/{join-2,join-3,gallery-1,gallery-2,gallery-3,gallery-4}-{400,800}.{avif,webp,jpg}`.
- Brows before/after: `assets/img/work/brows-{before,after}-{400,800}.{avif,webp,jpg}`.
- Slay: `assets/img/slay/shannon-{360,540}.{avif,webp,jpg}`, `assets/img/slay/slay-logo-{240,480}.png`.
- Brand logos: `assets/img/brands/{dermalogica,ref,lakme}-logo.jpg`, `voesh-logo.jpg`, `olaplex-logo.png`, `smashbox-logo.jpg`, `calecim-logo.jpg`, `ecru-logo.jpg`; product shots in `assets/img/brands/gallery/`.
- App badges: `assets/img/badge-app-store.jpg` (438×156), `assets/img/badge-google-play.png` (461×135).
- Check real pixel sizes with Python/Pillow before writing width/height.

## 6. Option B (branch design-b): service-page template

The 10 service pages and `services.html` follow docs/DESIGN-OPTIONS.md B7. The
blocks below replace the head, artists strip and level legend shown in section 4.

**Head (no image), a split title:** H1 right, a 2px umber rule, then a 38ch column.
```html
<section class="page-head page-head--split" aria-labelledby="page-h">
  <div class="container"><div class="split-title">
    <h1 id="page-h"><span class="st-line">Manicures &amp;</span> <span class="st-line">pedicures</span></h1>
    <p class="eyebrow">Tips &amp; Toes</p>
    <p class="lede">…</p>
    <ul class="range-list"><li><span>Classic manicure</span><span data-range="tips-and-toes.html#classic-manicure">$31–40</span></li>…</ul>
    <div class="btn-row" data-hero-ctas>(gold Book) <a class="text-link" …>Send as an eGift card</a></div>
    <p class="microcopy">…</p>
  </div></div>
</section>
```
At most 3 split titles per page (`.split-title`, `.split-title--long` for notes), never two in a row.

**Your artists:** a row of 3:5 mini frames (88px, `srcset` 180w/360w, `sizes="88px"`,
`src` the 360 file). The line under each name is stamped by the build from the
team titles and the page's anchor menu, so never type a level or price there:
```html
<li><a href="our-team.html#madison"><span class="af-frame"><picture>…</picture></span><span class="af-name">Madison</span>
<small class="af-line" data-artist="madison" data-anchor="tips-and-toes.html#gel-manicure-without-removal" data-anchor-label="gel manicure"></small></a></li>
```
It becomes "senior · gel manicure $49"; a person whose title carries no level (Emma,
Mia until owner question 8) shows the title instead. Use `artist-row--many` for 8
people and `artist-row--solo` for one.

**Who's at each level** (once per page, under `.level-legend`):
```html
<div class="level-key"><p class="lk-caption" id="lk-cap">Who’s at each level</p>
<ul class="lk-row lk-row--3" aria-labelledby="lk-cap">
  <li><span class="lk-level">Senior</span><span class="lk-price">gel manicure <span data-level-price="tips-and-toes.html#gel-manicure-without-removal@Senior">$49</span></span><span class="lk-who" data-level-who="nails@Senior"></span></li>
</ul></div>
```
`data-level-who="dept@Level"` is filled with linked first names from the titles on
`our-team.html`; `data-level-price` reads ladders by row and slash prices by the
group's `p.tier-head` order. Changing a title or a price and rebuilding updates
every row.

**Menu:** per-group Book links are umber caps text links with the page's Book label
(4 words or fewer). Long group heads may wrap existing substrings in
`span.h3-pre` / `span.h3-sub`; `check.py` (menu-h3-vs-main) fails if the text
differs from `main`.

## 7. Option B (branch design-b): team, about, new guests, contact

`our-team.html`, `about.html`, `new-guests.html` and `contact-us.html` follow
docs/DESIGN-OPTIONS.md B7. Each opens with the split-title head from section 6.

**Team blocks:** the team is one `div.dept` per department, each with its own
`<h2>` and `ul.team-grid`, all inside `.team-blocks` (a 3-column grid from 1024px,
2 below; the lists are subgrids so every card lines up). Every person appears once,
in A's default order. `dept--1` / `dept--2` let a small block share a row
(Skin & waxing beside Massage), `dept--center` hangs Shannon's single print in the
middle column and `dept--desk` sets the front desk four across. `site.js` hides a
block (`data-team-block`) when a filter leaves it with no visible card.

**Team card** (the parser contract still holds: `div.card` contains no other `div`):
```html
<li class="team-item" id="austyn" data-dept="hair">
  <div class="card">
    <span class="ph-frame"><picture>… 360/540/720w …</picture></span>
    <header class="card-id"><h3>Austyn</h3><span class="role">Senior Hair Stylist</span></header>
    <p class="card-level" data-level-line="austyn"></p>
    <ul class="tags">…</ul>
    <p class="creds">…</p>
    <span class="card-actions"><button type="button" class="card-bio" data-bio="bio-austyn" aria-haspopup="dialog"><span class="sr-only">Read Austyn&rsquo;s </span>bio</button><a data-book …>Book<span class="sr-only"> an appointment (ask for Austyn)</span></a><a class="card-ig" href="…" rel="noopener"><span class="sr-only">See Austyn&rsquo;s work on </span>Instagram</a></span>
  </div>
</li>
```
`data-level-line` is stamped by the build from the title's level and the menus:
"women's cut $48 · all-over color $75" for hair, "gel manicure $49" for nails, and
nothing for a title without a level (Emma and Mia until owner question 8) or for
massage (priced by duration). Put it only on hair and nail cards.

**Bio sheet:** the frame, `h2`, `span.role`, then `<div class="bio-level"
data-level-line="austyn" data-level-prefix></div>` ("At Senior level: …"), then the
bio `<p>`. `build-schema.py` skips that div, so the bio stays the Person description.
The gold Book pill in `.bio-foot` is the only gold on the sheet.

**New guests levels** (`#level-jr-associate` … `#level-master` sit on the cells):
`ul.lk-row.lk-row--guide`, each cell with `.lk-level`, `.lk-prices` (one `.lk-price`
per anchor) and `.lk-whos` (one `.lk-who` per department: a `.lk-dept` label and a
`data-level-who` span). Jr Associate and Master carry the hair line only.

**About bento** (`ul.bento`, 10px gutters): `bn-tall` (1/3) + `bn-wide` (2/3), then
`bn-note` (2/3) + `bn-square` (1/3). `join/gallery-3` only ever appears as the
`gallery-3-sq-*` 1:1 top crop.

## 8. Option B (branch design-b): every other page

The boutique, brand, specials, gift card, pick-up, book online, careers, job,
policies, 404 and thank-you pages also open with the split-title head from
section 6. In these heads the primary is one pill (gold Book, or Strong for a
non-book action: Order for pickup, Buy an eGift card, Apply for this role) and the
second action is a text link (Call, Book a facial, See all roles). At most 3
split titles per page, never two in a row.

**Brand labels** (`products.html` and "More from The Boutique"): keep `a.brand-card >
img + h3.brand-name + span.brand-cat`. The logo becomes a white-matted print; the
name sits left and the category right on one baseline (stacked on narrow cards).
`aria-current="page"` outlines the current brand.

**Brand pages:** `.brand-about` = `figure.brand-mat` (the logo on a white mat, the
first image in `<main>`, so never lazy) beside `.brand-copy` (caps `h2.b-head`, text,
the salon link row). Product shots sit in `ul.product-row` (white ground,
`object-fit:contain`); `product-row--ref` keeps REF's #e5e5e5 ground and
`product-row--small` caps the 289px Dermalogica shots at 180 CSS px. Pickup is the
shared `split-title.pickup-split` with `ol.steps.steps--rule`.

**Specials:** `.offers > article.offer` rows (title left in Arsenal sentence case,
`ul.offer-terms` hairline rows, `.dates`, `.offer-links` right). Keep `id` and
`data-ends` on each article.

**Forms:** `.form-sheet` (a bone sheet on the wall) holds `.form-sheet-intro`
(left, sticky from 1200px) and the form column (right, underlined fields). Netlify
attributes, the honeypot and every field name stay as they are.

**Careers:** the head carries `join-3` as a wide print (`fp-img--pano`,
`join-3-1200` set). "Life at Bellezza" is `ul.bento.bento--life`: `bn-note` (the h2
and the Paige line) placed first in the DOM, `bn-wide` gallery-1, `bn-tall`
gallery-4, `bn-sq--a` gallery-3 (1:1 top crop only) and `bn-sq--b` gallery-2 (the
`gallery-2-c80-*` centre-80% crop only).

**Job pages:** `article.job > h2` stays (with `class="b-head"`); `h3` labels are
caps Mulish, lists are hairline rows. The glance sheet (`aside.job-aside`) is
sticky beside it. The person section is a 3:5 `frame-print` (`person-frame`), whose
`img src` stays the 360 file so the JSON-LD page image does not change.

**Policies:** `.doc-list > .doc-row` = caps `h2` left (sticky from 1024px), `.prose`
right; the no-show steps are `ul.escalation` (three hairline cells).

**Phone numbers in heads** (Arsenal never sets one): wrap the digits in
`span.h-num` (Mulish).
