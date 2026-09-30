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

## 6. Option C · Bronze & Sand components (branch `design-c`)

Spec: `docs/DESIGN-OPTIONS.md` sections 0 and C1-C9. Manrope only (400/600), no
italics, no tracked caps. `index.html` is the reference implementation.

- **Grounds:** white by default; `section--sand` (decisions: prices, levels,
  booking) and `section--bronze` (people and story). Never two bronze sections in a
  row. `.dark` renders as bronze.
- **Arrow capsule** (`.btn`, the only button shape): `btn--book` gold (booking at
  Bellezza only), `btn--strong` bronze primary, `btn--outline` outlined, `btn--light`
  cream on bronze. On bronze, `btn--strong` turns cream and `btn--book` gets the
  cream ring automatically. Labels are plain text (no arrow characters); the CSS
  draws the circle and arrow.
- **Small text-link form:** `.book-this` / `.arrow-link` (label + 28px bronze circle)
  for per-group and per-department Book links.
- **Devices:** `.bracket` ("[by level]" notes), `.brackets` (offset corner frame on a
  wrapper around a photo; max 2 per page), `.ghost-card` > `span.ghost[aria-hidden]` +
  `.float-card` (max 2 per page), `h1/h2.two-tone` > `span.tt-lead` + payoff (max 3
  per page), `span.hl` (the one highlighter, services.html H1 only).
- **Layouts:** `.intro-row` (eyebrow | H2 | paragraph), `.flush-split` +
  `--media-start`/`--media-end` with `.fs-text` and `.fs-media` (photo to the
  viewport edge), `.split-48` (4/8), leader rows (`.lead-list`, `.detail-rows`,
  `.lr-rule`), `.ritual` steps on bronze, `.line-cards` (flat 1px cards).
- **Price menus:** `.menu-group` renders as the 4/8 list automatically (heading,
  tier and intro left; `.price-list` right). `.dots` is drawn as a hairline leader;
  `p.note`, `p.tier-head` and `.level-legend` render as bracket lines.
- **Stamped values** (never type these): `data-range`, `data-from`,
  `data-unit="slay-aesthetics.html#botox"` ("$12/unit") and
  `data-level-price="salon.html#cuts-women" data-level="Senior"` ("$48").
- **Booking band:** stamped at the end of every page by the bottom partial, or
  wherever a page places `<!-- partial:band:start --><!-- partial:band:end -->`
  (home). There is no mobile bottom bar: Book lives in the sticky bronze header.

### 6.1 Service pages and `services.html` (C7)

`tips-and-toes.html` is the reference service page; `salon.html` adds ladders, the
level key, the extensions split and the keratin ritual.

- **Head (no-image variant):** `section.svc-head > .container > .ghost-card.ghost-card--head`
  holding `span.ghost[aria-hidden]` (the category word: Hair, Nails, Massage…) and
  `.float-card.head-card`: `p.eyebrow`, the `h1`, one `p.lede` line from the audited
  intro, `ul.head-range` (leader rows: `span.hr-name`, `span.lr-rule`, a stamped
  `span.hr-price[data-range|data-from|data-unit]`), then `.head-actions` with the
  `.btn-row[data-hero-ctas]` (the contextual gold Book; `btn--strong` on bridal and Slay),
  `p.head-links` (eGift, Call) and the microcopy. Desktop lays the card out as lede and
  actions left, the range right.
- **Your artists (3 or more people):** `section.artists-c` = `.intro-row` + `ul.artist-cards`
  (`artist-cards--3` for exactly three). Each `a.artist` holds `span.ph-frame > picture`
  (360/540/native srcset; brackets on hover), `h3.a-name`, `span.a-role[data-team-role="slug"]`
  and `span.a-tags[data-team-tags="slug"]`; the owners also carry `span.a-note`
  ("Behind the chair one day a week"). The first card image is not lazy.
- **One or two providers** (massage, facials, waxing): a bronze
  `section.flush-split.flush-split--media-start.people-split` with `.fs-solo` or `.fs-duo`
  portraits and a `ul.lead-list` of facts (`.ll-sub.brk[data-team-tags]` for specialties).
- **Level key** (salon, nails, services): `section.levels--key` (sand, ghost "Levels") with
  `table.level-key.level-key--{2|3}`. Rows: `th[role=rowheader]` = `span.lk-level` +
  `span.lk-who[data-who="hair|nails|hair nails"][data-level]`; cells
  `td[data-label][role=cell] > span[data-level-price][data-level]`. The explicit table
  roles stay: below 600px each row becomes a grid and some browsers drop native table
  semantics when display changes.
- **Ladders:** every level row gets `<div class="who" data-who="hair" data-level="Senior"></div>`
  after `.price-head`; each ladder group gets `<p class="tier-head">by stylist level</p>`
  after its `p.group-intro` (the intro must stay the first element after the `h3`: the
  schema reads it as the group description).
- **Packages:** `<div class="unit" data-unit-price></div>` after `.price-head` in a
  "Package of N" row: the build writes "$49 each". No "save" claims.
- **Ritual block** (keratin on salon, bridal): `section.section--bronze.ritual-block >
  .split-48`: the treatment, `p.rb-price` (stamped) and one capsule left; `ol.ritual`
  "Step n" rows right. Verified steps only.
- **4/8 sections:** FAQ, gift and related use `.container.split-48` with `.split-head`
  (eyebrow + `h2`) left. The gift section (massages, facials, spray tans) is
  `section.section--sand.gift.gift-c`. FAQ rows are the sand accordion.
- **services.html:** `section.svc-head--hl` with the only highlighter
  (`Services &amp; <span class="hl">prices</span>`, uppercased by CSS), the level key with
  linked level names, `ul.tiles.tiles--menu` (`span.tile-desc`, `span.tile-rows > span.trow`
  stamped leader rows, the home avatar stack) and `ul.line-cards.line-cards--4`.
- **Team facts stamped by the build** (`fill_team` in `tools/build-partials.py`, from the
  `our-team.html` titles; never typed): `data-who` + `data-level` (names at a level,
  owners with their note, several disciplines joined by " · ", a combined
  "Expert / Master" cell as "Expert names; Master names"), `data-team-role`,
  `data-team-tags`, `data-unit-price`, and `data-level-price` on a tiered item
  (`tips-and-toes.html#gel-manicure-without-removal` + "Senior" = "$49", read by position
  from the group's `p.tier-head`). Skin therapists and massage have no level line
  (owner question 8; massage is priced by length).
- **`check.py` h3-parity:** every `.menu-group > h3` must match `main` once tags are
  stripped (it runs `git show main:<file>`; without git it warns and skips).

### 6.2 People & place pages (C7: team, About, New guests, Contact)

- **Photo slots on this branch** take a ratio class instead of an inline style
  (`class="ph ph--3x2"`); no page carries a `style=""` attribute.
- **`our-team.html` (jump mode).** The wrapper `div.team-block[data-team-mode="jump"]` holds
  the sticky `nav.jump-chips` (links to `#filter-hair` … `#filter-client-services`), the
  owners' bronze split and `div.team-depts`. `site.js` then skips filtering; an old
  `our-team.html#filter-*` link lands on the block with that id.
  - **Owners:** `section.flush-split.team-lead-split#owners`: `.fs-text` (h2, a `lead-list`
    of facts, the one gold Book capsule) and `.fs-media > ul.team-lead` with Ashley's and
    Lisa's `li.team-item`.
  - **Departments:** one `section.dept#filter-{key}` per department, in the chip order:
    `.container.dept-grid` = `.dept-head` (h2, `p.bracket.dept-facts` with stamped counts
    and ranges, `p.bracket.dept-also` naming cross-listed people, `p.dept-actions` with a
    `.book-this` text link) + `ul.team-grid`. A card sits in the **first** department of
    its `data-dept`; the others name the person in brackets. A department with no cards
    of its own (makeup, bridal) shows `ul.dept-roster` leader rows instead
    (44px avatar, name linking to the card, `span.ro-role[data-team-role]`).
  - **Card** (`li.team-item > div.card`, no `<div>` inside the card: the schema reads the
    card up to its first `</div>`): `span.ph-frame > picture`, `h3`, `span.role`,
    `span.lvl-line[data-team-level="slug"]` (stamped "Senior · women's cut $48"),
    `ul.tags`, `p.creds`, `span.card-actions` (`button.card-bio`, `span.card-links` with the
    `a[data-book]` text link and Instagram).
  - **Bio** (`dialog.bio#bio-{slug}`): `.bio-photo.brackets > picture` and `.bio-body`:
    `h2`, `span.role`, the `span.lvl-line`, then the bio `<p>` (it must stay the first `<p>`
    after `span.role`; `build-schema.py` reads it), `ul.creds-list.lead-list` rows (label,
    `lr-rule`, value; "Specialties" is `data-team-tags`), `p.bio-services`, the
    "Ask for …" microcopy and `.bio-actions` (gold Book, Instagram).
  - **Stamp:** `<span data-team-level="slug">` gives the level from the person's title and
    the price at that level from `salon.html#cuts-women` (stylists) or
    `tips-and-toes.html#classic-manicure` (nail artists). No level line for the skin
    therapists (owner question 8), massage (priced by length), leadership or front desk.
- **`about.html`:** ghost word "2009" + `.head-card--duo` (lede left, actions right); the
  house year by year as `.year-split` flush splits (2008 bronze with the owners,
  2022 white with `.prod-grid` product shots never wider than 180 CSS px, Today bronze with
  `.fs-wide` group photo) and one `.years-band` (`ol.year-row` numerals) where there is no
  photo; `p.year-n` is the `--c-numeral` line. Then the stat row and `ul.gallery-3x2.brackets`
  (`li.g-wide` spans two columns). Below 1024px the splits stack, photo first.
- **`new-guests.html`:** head card (ghost "Welcome"), the bronze `.ritual-block.first-visit`
  (`span.step-d` under each step), the chips, then 4/8 `split-48` sections. The levels card
  is a `level-key` table whose rows keep the ids `level-jr-associate` … `level-master`;
  prices (`data-level-price`) and names (`data-who="hair nails"`) are stamped.
- **`contact-us.html`:** `.visit-grid.contact-grid`: H1, `ul.detail-rows.contact-rows`
  (status row hides itself without JS, Call, Directions, Book) and `#hours` (the stamped
  table) left; `.map-panel.brackets.contact-map` (sticky from 1024px) right. Then the sand
  `section#holidays` with the stamped holiday table, and the other ways to reach us.
- **Chip rows** scroll sideways on their own (`revealChip` in `site.js`); the scrollspy never
  calls `scrollIntoView()`, which cancelled smooth scrolls to far sections.
