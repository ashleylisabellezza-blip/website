# Page authoring guide

How to write or edit a page so it works with the build (`python tools/build.py`),
the stylesheet and the structured-data generator. The full design rationale is
in `REDESIGN-BRIEF.md`; this file is the practical contract.

**2026-10-08: the owners' homepage design** (`docs/LatestFromBellezza/`) replaced the
header, nav, footer, fonts and home page: Italiana headings, Montserrat body and
buttons (tracked caps), black booking buttons, ivory/tan/black with no pink. The
owners are sending a design for each page in turn; until a page gets its own, keep
its current layout. For inner pages copy an inner page's patterns (e.g. `salon.html`);
the home page uses its own `.h-*` blocks.

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
- **Booking buttons.** `.btn--book` only for links to the Meevo booking
  URL (`https://login.meevo.com/bellezza/ob?locationId=103245`) with
  `data-book data-cta="book" data-placement="…"`. It is black (tan on dark grounds),
  like `.btn--strong`, which other primary actions use. Secondary: `.btn--outline`.
- **Button labels:** sentence case, no arrows, never "Learn more", "Click here",
  "Submit". Call buttons show the digits: "Call 740-366-1604". Links to the phone are
  exactly `tel:+17403661604`.
- **Headings:** exactly one `<h1>`; no skipped levels (h1 → h2 → h3). Eyebrows are
  `<p class="eyebrow">`, never headings. No `<em>` in headings (only 3 allowed
  site-wide and they are used on home and about).
- **Left-aligned by default** (the owners' design centers only the home service-tile
  captions and the reviews label). No carousels, sliders, parallax,
  scroll animation, icon rows, invented testimonials, stock photos, or the retired room
  photos (`services/manicure.jpg`, `facial.jpg`, `derma.jpg`; `mani-room.jpg` and
  `massage.jpg` stand in on the home tiles only until the owners send HP-04/HP-05),
  `hero-*.jpg`, `tile-*.jpg`, `about-*.png`,
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
  "refreshed look", "effectively support"). Slay's weight-loss medications are
  named only as the owners confirmed them (2026-10-05), and compounded ones are
  always labeled "not FDA-approved";
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
lizbeth, cherish, liv, mya, kat, paige, madison, shelbi, raegan, rissa (shown as
Marissa), hope, jesyca, emma, mia, shannon-francis, melissa, aubree, grace, aeriannah.
Taylor F has left (2026-10); her slug and images are gone. Lisa Jeffries no longer
takes clients, so she is listed under leadership only and has no Book link.

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
