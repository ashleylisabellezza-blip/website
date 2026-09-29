# Bellezza & Co. Redesign Brief

**Version 1.1 · 29 September 2026 · Design lead brief for the static site in `C:\Users\mtdev\Projects_Main\Bellezza`**

This is the spec for building the redesign. It revises v1.0 using four reviews: art direction/template risk, conversion, truth/E-E-A-T, and accessibility/performance. The owner-approved mockup is still the basis for the tone, the palette and the hero headline. Everything fabricated in the mockup has been removed (full list in §10.3). Every fact used below is on the verified list in §10.2. Anything not on that list goes to the owner as a question (§10.4) and is not published until it is answered.

---

## 0. Decisions at a glance

| Question | Decision |
|---|---|
| Visual direction | Editorial "printed salon menu". Paper grounds, hairline rules, big Didone type and real faces. The signature element is a typeset price card inside the logo's broken-frame device. The team sits on a true-black wall. |
| Palette | The existing palette is kept exactly. It gains only same-hue tints and shades so that every text pairing passes WCAG AA. No grain texture. |
| Primary button | Gold `#b8985f` with ink `#1c1c1c` text (6.24:1). Gold fill is used only for **booking at Bellezza**. |
| Fonts | **Bodoni Moda** (instanced variable roman plus italic) replaces Prata. **Hanken Grotesk** replaces Open Sans. Both are self-hosted WOFF2. |
| Header and footer | Static HTML, stamped into every page by a Python build (`tools/build.py`). No npm. `site.js` only adds behavior. |
| Hosting | Decided in Phase 0. The default is Netlify (`_redirects`, `_headers`, Netlify Forms). §3.5 gives the Cloudflare Pages path. |
| Book links | Every Book CTA goes straight to Meevo in the same tab. Placement is tracked with cookieless analytics events, not UTM tags. `book-online.html` is an explainer page and is never a step in the booking path. |
| Hero image | A contact sheet built from the real studio portraits, on black: 28 on desktop, 12 on mobile. `join-1.jpg` moves to About. No stock photos anywhere. |
| Hero headline | The owner's line "Beauty & relaxation, *tailored to you.*" stays as the H1. The eyebrow moves out of the H1, and a folio line of facts sits directly under the hero. |
| Services on home | A typeset menu card showing real price ranges by level. It replaces the mockup's 6-photo mosaic and v1.0's hover index. |
| Reviews on home | Real public Google reviews, quoted verbatim with permission. The section is built now and ships only once at least 3 have been collected. No review schema. |
| Transformations | Left out until consented before/after pairs exist. |
| Carousels and scroll animation | None anywhere on the site. |
| New pages | `services.html`, `about.html`, `new-guests.html` and up to five job pages (`job-*.html`, only for open roles). |
| Removed pages | Thin `products-{brand}.html` pages are merged into `products.html` with 301s, unless Search Console shows real traffic (§5.8). `jobs.html` gets a 301 to `join-our-team.html#apply`. |
| Mobile | A sticky header with the wordmark and "Menu", and no Book button below 768px. A bottom bar with a contextual **Book** and **Call** appears once the hero CTAs have scrolled away. |
| Slay Aesthetics | Visually and functionally separate. Its CTAs go to Slay's own site, never to Bellezza's Meevo. There are no outcome claims. |

---

## 1. Design principles

1. **Real or nothing.** Every face, name, number, price, review and photo is real and verifiable. An honest typographic layout beats a stock photo. A missing section beats a fake one. A single fake element undermines all the real ones.
2. **Gold means book.** The gold fill is reserved for booking at Bellezza. A visitor who sees gold knows it is the way to book. Other actions use ink or outline buttons. Pages without Bellezza booking (Slay Aesthetics) use no gold button.
3. **The menu is the brand.** Bellezza publishes its prices by level, which most salons won't do. That openness gets the best typography on the site: a framed printed menu, hairline rules, dotted leaders, tabular numbers and honest ranges. The same system runs from the home menu card to every service page.
4. **People before rooms.** The strongest assets are the studio portraits and a founding story told by two sisters. Empty rooms are retired. Every service links to the people who perform it.
5. **One thumb, one decision.** At 360×640, the headline, a short lede, and side-by-side Book and Call buttons fit in the first screen. On every page, Book is one tap away at any scroll depth.
6. **Quiet confidence.** The layout is left-aligned and asymmetric, with generous white space and no icon rows. Nothing moves on scroll. Italic appears in at most three headings on the whole site. The site reads as a magazine from Newark, not a theme.
7. **Everything in the HTML.** Name, address, phone, hours, nav, prices and credentials are visible text in the page source. They are not in images, not injected by JS, and not only in JSON-LD.
8. **The logo is the style guide.** The broken rectangular frame, the widely tracked caps with bullet separators, and the "& Co" script are the brand's own devices. The design reuses them instead of borrowing theme conventions.

---

## 2. Design tokens

### 2.1 Color

The hue family stays at 38 to 40 degrees (the existing gold). All ratios below were computed with the WCAG 2.x relative-luminance formula.

| Token | Hex | Status | Role | Verified contrast |
|---|---|---|---|---|
| `--paper` | `#faf8f5` | existing (cream) | Default page ground | ink 16.08 · text 7.03 |
| `--white` | `#ffffff` | existing | Inputs, dialog body, dropdown panel, bottom bar | ink 17.04 · text 7.46 |
| `--sand` | `#f1ece3` | **new tint** | **Inline panels and chips only** (quiz panel, notes, map facade, price notes). Never a full-width band. | ink 14.48 · text 6.34 · gold-text 4.93 |
| `--line` | `#e7e2d9` | existing | Hairlines and dividers. **Decorative only.** | 1.22 on paper (never the only boundary of a control) |
| `--line-strong` | `#9c7f4c` | = gold-dk | Input, chip and checkbox borders | 3.57 paper · 3.78 white · 3.21 sand (meets the 3:1 UI minimum) |
| `--gold` | `#b8985f` | existing | Book button fill, rules, text **on dark only** | ink on gold 6.24 · gold on ink 6.24 · gold on black 7.69 · gold on ink-2 5.68 |
| `--gold-lt` | `#c9ae7c` | **new tint** | Hover fill of the Book button | ink on it 7.98 |
| `--gold-dk` | `#9c7f4c` | existing | **Borders and icons only. Never text.** | 3.57 paper · 3.21 sand |
| `--gold-text` | `#7a6232` | **new shade** | All small gold text on light: eyebrows, prose links, price accents | 5.47 paper · 5.80 white · 4.93 sand |
| `--gold-deep` | `#6a552f` | **new shade** | Link hover and pressed, error bar, owner photo-slot labels | 6.71 paper · 6.04 sand |
| `--ink` | `#1c1c1c` | existing | Headings, all display text on light, CTA band, text on gold | — |
| `--ink-2` | `#262420` | **new shade** | Raised surface on ink (owners panel) | paper on it 14.61 |
| `--black` | `#000000` | existing | Utility bar, hero contact-sheet column, team wall, footer | gold 7.69 · paper 19.8 · on-ink 16.28 · on-ink-muted 8.20 |
| `--text` | `#555555` | **new shade** | Body copy on light grounds | 7.03 paper · 6.34 sand · 7.46 white |
| `--muted` | `#6b6b6b` | existing | Meta and secondary text on paper and white | 5.03 paper · 5.33 white · 4.53 sand (on sand only at 16px and up) |
| `--on-ink` | `#e7e2d9` | = line | Body text on ink and black | 13.21 ink · 16.28 black · 12.01 ink-2 |
| `--on-ink-muted` | `#a8a196` | **new tint** | Captions on ink and black | 6.66 ink · 8.20 black · 6.05 ink-2 |

**Usage rules (hard):**
- `#b8985f` never appears as text on paper, sand or white (2.32 to 2.73). It is not used for eyebrows, links or prices on light grounds.
- `--gold-dk` is never used as text on any ground. Display text on light grounds is always `--ink`.
- White text never goes on gold (2.73). Button text on gold is always `--ink`.
- `#8a8a8a` and weight-300 body text are retired.
- `--muted` never goes on `--line` (4.13, which fails).
- Forms, inputs and chips sit only on `--paper` or `--white`.
- Links in running text use `--gold-text` with a 1px underline at a 3px offset. Color is never the only signal.
- There is no error red and no success green. States use ink text, an icon, a text prefix and a 2px `--gold-deep` bar.
- Gold should cover about 5% of the pixels on any screen.
- **Home ground sequence:** paper (hero, with a black contact-sheet column) → paper (menu) → [paper (reviews, once live)] → **black** (team) → paper (story, with an ink owners panel) → paper (bridal) → paper (visit) → **ink** (CTA band) → **black** footer. Consecutive paper sections are separated by a full-width `--rule`. A 1px `--gold` rule separates the ink band from the black footer.
- **No texture.** The grain overlay is deleted, because it pushed approved pairs below AA.

```css
:root{
  --paper:#faf8f5; --white:#fff; --sand:#f1ece3; --line:#e7e2d9; --line-strong:#9c7f4c;
  --gold:#b8985f; --gold-lt:#c9ae7c; --gold-dk:#9c7f4c; --gold-text:#7a6232; --gold-deep:#6a552f;
  --ink:#1c1c1c; --ink-2:#262420; --black:#000; --text:#555; --muted:#6b6b6b;
  --on-ink:#e7e2d9; --on-ink-muted:#a8a196;
  --focus-light:#1c1c1c; --focus-dark:#b8985f;
}
```

### 2.2 Typography

**Families: 2 families, 3 files, self-hosted WOFF2, Latin subset, `font-display:swap`.**

| Role | Family | Why |
|---|---|---|
| Display (H1 to H3, menu heads, names, folio numerals) | **Bodoni Moda**: variable roman, instanced to `opsz` 11–96 and `wght` 400–500, plus the variable italic instanced the same way | Prata has no italic, so the mockup's "*tailored to you.*" would be a faked oblique. Bodoni Moda keeps the Didone voice of Prata and the logo, and adds a true italic and optical sizing. Display weight is 400 to match the logo's light wordmark. `font-optical-sizing:auto`. |
| Text and UI | **Hanken Grotesk**: variable roman, instanced to `wght` 400–600 | A warm, current grotesque with clear numerals and tabular figures. It is more legible on phones than Open Sans 300. |

- **Size budget:** Bodoni roman ≤ 70KB, Bodoni italic ≤ 45KB, Hanken ≤ 45KB.
- **Building the files:** use `fontTools.varLib.instancer` and then `pyftsubset` (both pip installs). Source the variable files from the Google Fonts ZIP or the Fontsource files on jsDelivr.
- **Loading:**
  - The italic `@font-face` is declared globally, so it downloads only on pages that use it.
  - Preload `bodoni-moda-roman-latin.woff2` on every page.
  - Also preload `bodoni-moda-italic-latin.woff2` on `index.html` and `about.html`, the only pages with italic headings.
- **Fallback fonts:** add metric-matched fallbacks, each with `size-adjust` and the ascent, descent and line-gap overrides:
  - `'Bodoni Fallback'` (Georgia)
  - `'Bodoni Fallback Italic'` (Georgia Italic)
  - `'Hanken Fallback'` (Arial)
- Compute the override values with `tools/font-metrics.py` (fontTools). Don't guess them.
- Remove the `@import` from `styles.css`.
- Hanken is shipped without an italic, so body text never uses `<em>`. Emphasis in running text uses `<strong>`.
- `font-variant-numeric: tabular-nums lining-nums` on every price, time and hours table.
- `text-wrap: balance` on headings and `text-wrap: pretty` on paragraphs.

**Fluid scale (from 360px to 1440px, Utopia method):**

| Token | clamp() | Size range | Use | Family / weight | Line-height | Tracking |
|---|---|---|---|---|---|---|
| `--step--1` | `clamp(.8125rem, .79rem + .1vw, .875rem)` | 13–14px | Eyebrows, folio, captions, legal, level labels | Hanken 500 (eyebrow and folio, uppercase) / 400 | 1.5 | eyebrow and folio **.32em**; else 0 |
| `--step-0` | `clamp(1.0625rem, 1.0417rem + .0926vw, 1.125rem)` | 17–18px | Body, price rows, buttons (16px fixed) | Hanken 400; buttons 600 | 1.6 | 0 (buttons .01em) |
| `--step-1` | `clamp(1.25rem, 1.17rem + .37vw, 1.5rem)` | 20–24px | Lede, team names | Bodoni 400 (names) / Hanken 400 (lede) | 1.35 | 0 |
| `--step-2` | `clamp(1.5rem, 1.35rem + .74vw, 2rem)` | 24–32px | H3, menu-card heads, menu-group heads | Bodoni 400 | 1.2 | -.005em |
| `--step-3` | `clamp(1.875rem, 1.6rem + 1.3vw, 2.75rem)` | 30–44px | H2 on inner pages | Bodoni 400 | 1.1 | -.01em |
| `--step-4` | `clamp(2.25rem, 1.75rem + 2.22vw, 3.75rem)` | 36–60px | H2 on home | Bodoni 400 | 1.08 | -.015em |
| `--step-5` | `clamp(2.75rem, 2rem + 3.3vw, 5rem)` | 44–80px | H1 | Bodoni 400 | 1.04 | -.02em |

- **Measure:** 64ch for prose and 44ch for ledes.
- **Eyebrows copy the logo tagline.** They are tracked caps with "•" separators (for example "Hair salon & day spa • Newark, Ohio"), in `--gold-text` on light grounds and `--gold` on dark.
- **Italic rule:** italic appears in at most **three headings on the whole site**:
  1. The home H1: "Beauty & relaxation, *tailored to you.*"
  2. The home story H2: "Lisa and Ashley bought a Newark house *in 2008.*"
  3. The About H1: "From an 1,800 sq ft house *to Bellezza & Co.*"

  Every other heading is roman. `check.py` counts `<em>` inside `h1`/`h2` across the site and fails the build above 3.
- **Headline formula ban:** no two-fragment parallel headlines ("X. One Y.", "Real people. Real experiences.").
- **Script:** no script or handwriting fonts. The only script on the site is the logo's own "& Co", lifted as an SVG path from the vector logo (§2.7). A scan of Lisa and Ashley's real signatures may appear on About if supplied.
- **Minimums:** body text 17px, form input text 16px (prevents iOS zoom), and no text under 13px.

### 2.3 Spacing, layout and breakpoints

- **Base unit 4px:** `--s-1:4px --s-2:8px --s-3:12px --s-4:16px --s-5:24px --s-6:32px --s-7:48px --s-8:64px --s-9:96px`.
- **Section padding:** `--section: clamp(4.5rem, 3rem + 6.5vw, 10rem)` (72 to 160px). The hero's top padding is `clamp(1.5rem, 1rem + 3vw, 5rem)`.
- **Gutter:** `--gutter: clamp(1.25rem, .8rem + 2vw, 2.5rem)` (20 to 40px).
- **Grid:** 12 columns within a 1320px maximum, gap `--gutter`. Named lines `full-start / content-start / content-end / full-end` let images bleed to one viewport edge.
- **Breakpoints:** 480, 768, 1024 and 1280px. Build for 360px first.
- **Alignment:** everything is left-aligned. There are no centered sections.
- **Section heads vary.** The 7/5 split (H2 in columns 1–7, intro in 8–12) is used at most twice per page. Other heads are a single column with the intro below at 44ch. Eyebrows are plain labels, not numbered.

### 2.4 Radii, borders, shadows

| Token | Value | Use |
|---|---|---|
| `--r-0` | 0 | Images, panels, cards |
| `--r-1` | 2px | Buttons, inputs, dialog |
| `--r-pill` | 999px | Filter and jump chips only |
| `--rule` | `1px solid var(--line)` | Row dividers, section separators, header bottom edge |
| `--rule-gold` | `1px solid var(--gold)` | Menu-group head rule, band/footer seam |
| `--frame` | `1px solid var(--ink)` (`--gold` on dark) | The broken-frame device (§2.7) |
| `--shadow-pop` | `0 12px 32px rgb(28 28 28/.12)` | Services dropdown only |
| `--shadow-dialog` | `0 24px 64px rgb(28 28 28/.28)` | Bio dialog, mobile drawer |

Cards get no shadows and no 16px rounding. Hairlines and white space do the separating.

### 2.5 Motion

**There is no scroll-triggered motion. Content is on the page when it loads.** All motion below sits inside `@media (prefers-reduced-motion: no-preference)`. Only `transform` and `opacity` are animated.

1. **Link feedback:** a gold underline draws left to right over 250ms, and color swaps take 150ms. Buttons change fill color only. Buttons have no arrows.
2. **Header:** the desktop header box is a fixed 72px and never changes height. After 80px of scroll, the wordmark scales to `.85` with `transform` and a hairline fades in with `opacity`, over 200ms. `--header-h` is a constant.
3. **Overlays:** the dropdown, drawer and dialogs fade in over 150ms. The `<details>` chevron rotates.

Nothing else animates: no reveal on scroll, no image unmask, no parallax, no autoplay, no scroll-jacking, no cursor followers and no WebGL. Under `reduce`, all durations are set to `.01ms` and `scroll-behavior:auto`.

### 2.6 Image treatment

- **Ratios:** 3:4 (portraits), 4:5 (editorial), 4:3 (group photo), 1:1 (details), 21:16 (desktop contact sheet), 4:3 (mobile contact sheet).
- **Grade, applied once before export:**
  - True blacks, with no black lift.
  - Reduce clarity and the HDR look, and remove every vignette.
  - Neutralize the cyan/teal backdrop cast to neutral-warm (b* ≥ 0).
  - Keep skin tones accurate, with no global desaturation.
- **Portraits:**
  - All 28 are re-cropped to 3:4 at their native resolution. Some sources are 720×960, 679×960 or 600×800. None are upscaled.
  - Variants: 180w, 360w and 540w. A 720w variant is made only where the source is at least 720 wide.
  - `build-images.py` samples each portrait's outer 8px and fails if its mean luminance is above 3%, so portraits sit seamlessly on `--black`.
- **Team surfaces:** the team wall, the hero contact sheet and the home roster sit on `--black` (#000), not `--ink`.
- **Contact sheet (hero):** `build-images.py` composes the graded portraits, tiles butted together on #000, in the default team order (§5.4).
  - Desktop: all 28, 7×4, 1540w, AVIF ≤ 160KB (plus WebP and JPEG).
  - Mobile: 12 people, 4×3, 800w, AVIF ≤ 70KB. The 12 are Ashley, Lisa, Devon, Stephanie, Moriah, Emilie, Austyn, Paige, Madison, Jesyca, Emma and Mia.
  - It is rebuilt whenever the roster changes.
- **`join-1.jpg`:** used on About only. Neutralize the HDR and vignette, and re-crop to 1120×840 from center-top, excluding the ceiling ducts, camera and speaker where possible.
- **Dark logo:** `tools/build-images.py` generates `logo-on-dark.png` by recoloring the alpha mask of `logo.png` to `--paper`. It is superseded by the SVG once the vector logo arrives.
- **Room photos** (manicure, mani room, facial room, massage room) are retired from public pages.

### 2.7 Brand devices (from the logo)

- **(a) The broken frame:** a 1px `--frame` rectangle with a gap in its top edge holding a tracked-caps label, as in the logo's "EST. 2009". It is used for exactly three things:
  1. The home and `services.html` menu card (label "The menu • Prices as of {Month YYYY}")
  2. The About timeline head (label "Est. 2009 • Newark, Ohio")
  3. The footer lockup
- **(b) Tracked caps with bullets:** eyebrows and the folio copy the tagline "SALON • SPA • BOUTIQUE" (Hanken 500, .32em tracking, "•" separators). Text is sentence case in the source and uppercase via CSS.
- **(c) The "& Co" script:** an SVG path from the vector logo. It appears once on the whole site, as a 20%-opacity gold mark on the About story panel, `aria-hidden`.
- **Header lockup:** the wordmark only ("BELLEZZA & Co", no frame, no tagline), cut from the vector logo: 28px tall on desktop and 24px on mobile. Until the vector arrives, `build-images.py` crops the wordmark from `logo.png` as a 2× raster. The full framed lockup appears only in the footer and on About at 200px wide or more.

---

## 3. Architecture decision

**Decision: move to static HTML stamped by a Python build script in `tools/`. `site.js` becomes behavior-only.**

**Why:**
1. NAP (name, address, phone), hours and nav links must be in the HTML source. AI crawlers do not run JavaScript, and Google's link discovery needs real `<a href>`.
2. The late-injected header is the largest likely source of CLS on every page.
3. With JS off, the site currently has no navigation.
4. WCAG 3.2.6 (Consistent Help) requires repeated help mechanisms (phone, contact) to appear in the same relative order on every page. We also keep Book in the same place for consistency.
5. The project already uses this pattern (`build-schema.py` stamps JSON-LD in place), so this adds no toolchain, server or npm.

### 3.1 Files

```
tools/
  site.json            single source of truth: NAP, geo, hours, holidays, URLs, trick-or-treat dates, seasons,
                       specials, reviews (+ rating/count/date), allowedNumbers, pricesConfirmed per page,
                       team roster order, analytics switch
  pages.json           page registry: slug, nav label, parent (breadcrumb), family, lead practitioners,
                       range anchor item, book_label, book_override, noindex, open (jobs)
  partials/            utility-bar, header, drawer, breadcrumb, folio, menu-card, reviews, bookbar, cta-band,
                       footer, hours-table, holiday-table, level-legend, apply-form, privacy-note
  build.py             orchestrator: images (only with --images) -> partials -> schema -> check; --check = dry run, fail on diff
  build-images.py      Pillow >= 11.2: grade checks, AVIF/WebP/JPEG variants, contact sheets, EXIF strip, logo recolor/crop
  build-partials.py    stamps partials between markers; fills data-count / data-range / data-price / data-asof; content-hash ?v=
  build-schema.py      existing, hardened (3.3)
  font-metrics.py      fontTools: fallback size-adjust and ascent/descent/line-gap overrides
  check.py             launch gate (3.4); exit code 1 on any failure
assets/js/site.js      behavior (nav, drawer, dialogs, filters, scrollspy, status, seasons, analytics events)
assets/js/forms.js     validation + submit; loaded only on brides, join-our-team, job-*, pick-up-orders
netlify.toml           build command = "python3 tools/build.py --check"
```

The command is `python tools/build.py`. Output is written in place and is idempotent, so running it twice changes nothing.

### 3.2 Stamping rules

- **Markers:** `<!-- partial:NAME:start -->` … `<!-- partial:NAME:end -->`.
- **Current page:** `aria-current="page"` goes on the matching nav link. For service pages, `aria-current="true"` goes on "Services & Prices".
- **Book links:** every `<a data-book data-cta="book" data-placement="PLACEMENT">` gets its `href` set to the Meevo booking URL. The Slay Aesthetics page uses its `pages.json` `book_override` instead (§5.3). `site.json.utm` defaults to `false`: UTM tags on a link to another domain don't reach our analytics. It is turned on only if Meevo confirms it reports on them.
- **Analytics events:**
  - Every CTA carries `data-cta="book|call|gift|quiz|directions|text|slay"` plus `data-placement`.
  - `site.js` sends these as custom events to the cookieless analytics tool (Plausible, decided in Phase 0).
- **Counts, prices, dates:**
  - `<span data-count="team">` is filled with the number of `.card` elements on `our-team.html` (28).
  - `<span data-count="providers">` is filled with the number of cards whose `data-dept` includes hair, nails, skin, massage or makeup (22).
  - `<span data-count="dept-hair">` and the other department counts are filled the same way.
  - `<span data-range="salon:womens-haircut">` is filled with the lowest-to-highest level price of that item ("$37–60"). Items without levels render "from $X".
  - `<span data-price="PAGE:ITEM">` is filled with that item's price text, so the menu card can never drift from the service pages.
  - `<time data-asof>` reads "Prices as of {Month YYYY}". The date comes from `site.json.pricesConfirmed[page]`, the date the owner confirmed that page's menu. After that it changes only when the hash of the price block changes.
- **Asset versions:** every local `src`, `srcset`, `href` and preload gets `?v={8-char content hash}`. The build-date version and the `-v2` rename rule are dropped.
- **Year:** the © year is filled at build time.
- **JS config:** `site.js` receives a generated config block between `/* config:start */` and `/* config:end */`, built from `site.json` (hours, holidays, URLs, seasons, specials end dates). URLs are defined in exactly one place.

### 3.3 Parser contract (must be preserved) and required hardening of `build-schema.py`

**Class contract:**
- `.menu-group > h3`
- `li.price-item` containing `.price-head > span.name + span.price`, followed by the description `<p>`
- `.card` with a heading for the name (**`h3`** in the new markup), plus `dialog.bio#bio-SLUG` containing `span.role` then `<p>`
- `article.job#ID` containing `h2`
- `a.brand-card`
- `li.price-ref`: a new class for cross-referenced rows (men's page, §5.3). The parser ignores it.

The script's regexes are currently literal-string matches. Harden them so the redesign can add ids, modifier classes and attributes without changing output:

| Function | Current | Replace with |
|---|---|---|
| `h1_of` | `<h1>(.*?)</h1>` | `<h1\b[^>]*>(.*?)</h1>` |
| `first_image` | `page.split('<main>',1)` / `<img src="…"` | `re.split(r'<main\b[^>]*>', page, 1)` / `<img\b[^>]*?\bsrc="(assets/img/(?!badge)[^"]+)"`; default image `assets/img/team/contact-sheet-1540.jpg` |
| `price_catalog` | `<div class="menu-group">`, `<h3>`, `<p class="center">`, `<li class="price-item">`, description via `</div>\s*<p>` | `<div class="menu-group\b[^"]*"[^>]*>`, `<h3\b[^>]*>`, `<p class="(?:center|group-intro)\b[^"]*">`, `<li class="price-item\b[^"]*"[^>]*>`; description = first `<p\b(?![^>]*class="note")[^>]*>` after `.price-head` |
| price values | any text | a price cell reading `$$` or `Consultation` emits **no** Offer price; `$$` is never emitted |
| team cards | `<div class="card">.*?</div>`, `<h4>`, first `<span>` = role, `<img src="` | `<div class="card\b[^"]*"[^>]*>.*?</div>`; name `<h([2-4])\b[^>]*>(.*?)</h\1>`; role = `<span class="role">` first, falling back to the first span; `<img\b[^>]*?\bsrc="…"`; slug = image basename with `-\d+$` stripped (`devon-540.webp` becomes `devon`) |
| bio dialogs | `<dialog class="bio" id=` | `<dialog\b(?=[^>]*\bclass="bio\b)(?=[^>]*\bid="bio-SLUG")[^>]*>` |
| jobs | branch on `join-our-team.html`, `<article class="job" id=`, `<h2>` | branch on `fname.startswith('job-')` (one JobPosting per leaf page); `<article\b[^>]*class="job\b[^"]*"[^>]*id="…"` and `<h2\b[^>]*>`; no JobPosting on the list page |
| brand pages | `products-*` branch | removed; the `products.html` ItemList uses `<a\b[^>]*class="brand-card\b[^"]*"[^>]*href="…">` with `#anchors` |

**Markup rules that follow from the parser:**
- A `.card` contains no nested `<div>`. Use `span`, `p`, `ul` and `button` inside it.
- Filter data attributes go on the wrapping `<li class="team-item">`, not on `.card`.
- Item notes go after the description as `<p class="note">`. They never sit between `.price-head` and the description.
- The `meta name="description"` attribute stays before `content`.
- Nothing is ever added inside `span.price`.

**Regression tests:**
1. Run the old and new `build-schema.py` on an untouched copy of the current pages. The JSON-LD must be byte-identical before any redesign markup lands.
2. After each phase, diff the JSON-LD of the old site against the new site page by page. Only the additions listed below are allowed.

**Additions to `build-schema.py`:**
- LocalBusiness `name`: exactly "Bellezza & Co.". `slogan`: "Salon · Spa · Boutique". `alternateName`: "Bellezza Salon and Day Spa". WebSite `alternateName` is the same.
- `foundingDate` 2009, and `founder` as two Person entries (Lisa Jeffries, Ashley Basham).
- `award`: "Voted the Number 1 spa in Licking County every year since 2016", **emitted only after owner question 1 is answered.**
- Holiday `openingHoursSpecification` entries for the next 12 months (with `validFrom`/`validThrough`, and `00:00`/`00:00` for full-day closures), generated from `site.json`.
- A warning when a meta description's "from $X" differs from the anchor price.
- `dateModified` taken from the page's "prices as of" date.
- The Slay MedicalBusiness node contains only name, provider, services, days and hours. No descriptions with outcome language.
- **No** `aggregateRating` or `Review`, ever.

### 3.4 `check.py`: the launch gate

The build fails on any of the following:
- A page that doesn't have exactly one H1.
- A skipped heading level.
- A title over 60 or under 45 characters.
- A description outside 120 to 160 characters. Pages with `noindex` are exempt from both length checks.
- A duplicate title or description.
- More than 3 `<em>` inside `h1`/`h2` across the whole site.
- An `<img>` missing `width`, `height` or `alt`.
- `loading="lazy"` on the hero image or on any image in the first viewport.
- Any internal link that doesn't resolve, including `#anchors`. `#filter-*` hashes on `our-team.html` are accepted.
- A `tel:` link that isn't `tel:+17403661604`.
- Any phone-number pattern (`\(?\d{3}\)?[-. ]\d{3}-\d{4}`) other than 740-366-1604, unless it is listed with a label in `site.json.allowedNumbers`.
- Two `li.price-item` elements on different pages with the same normalized name and different prices.
- Any `.ph` element without the `hidden` attribute (photo slots are owner-view only, §4.16).
- A `data-dept` slug in `pages.json` (the "Your artists" mappings) with no matching card on `our-team.html`.
- Staleness:
  - Fewer than 60 days of the holiday window remain.
  - An entry in `site.json.specials` has an end date in the past.
  - `site.json.trickOrTreat` is missing the current year after 1 September.
  - The review rating/count date in `site.json` is more than 90 days old (this one is a warning).
- White text on `#b8985f`. Scan the CSS for `color:#fff` inside rules whose background is `var(--gold)`.
- A Strong (ink) button inside an ink or black section.
- Any banned string. These are matched case-insensitively and with word boundaries, only in the deployed `*.html`, `*.css` and `*.js` files (never in `tools/` or the README):
  - `522-4173`, `522.4173`, `5224173`, `200 Deo`
  - `\b(Kelsey|Morgan|Abby|Tori)\b`
  - `Emily R`, `Jessica M`, `Caitlin B`
  - `© 2024`
  - `Salon + Day Spa`, `20+ beauty`, `more than 20`, `a more beautiful you`, `Good Hair Brighter Days`, `Beauty Looks Good On You`, `Right here in Newark`, `Design with purpose`, `from real clients`, `Skilled hands. Kind people`, `Complete beauty. Total well-being`
  - `9:00 AM – 6:00 PM`, `9–6`, `9–4`, `Sat 9`
  - `lorem`, `ipsum`, `Sed ut perspiciatis`, `REPLACE-ME`, `TODO`
  - `aggregateRating`
  - `smooth away`, `restore youthful`, `refreshed look`, `visible results`, `semaglutide`

`check.py` also prints two reports for the owner: the photo-slot report (page, slot, shot number) and the owner-question status (which gated items are still unanswered).

### 3.5 Hosting, deploy and URLs

- **Host decision in Phase 0.** The default is Netlify.
- **Netlify path:**
  - Turn "Pretty URLs" off. After the first deploy, verify that `/salon.html` returns 200 with no redirect.
  - The current `.html` URLs stay canonical everywhere: canonicals, the sitemap and internal links.
  - Enable form detection. It is off by default on newer sites.
  - Check the plan's monthly limits for form submissions and file uploads against expected volume. Résumé uploads can exceed the free tier; if they would, the careers form asks for an emailed link instead.
  - JS-submitted forms with files use a multipart `FormData` POST.
- **Cloudflare Pages path (if chosen):** canonicals, the sitemap and internal links become extensionless (Pages 308-redirects `.html` by default). Forms move to a form service with the same honeypot (Formspree or Basin).
- **Deploy:**
  - Put the site in a Git repo.
  - Deploy only from Git. `netlify.toml` runs `python3 tools/build.py --check`, which fails the deploy if stamping would change any file or if `check.py` fails.
  - Drag-and-drop deploys are not allowed, because they skip the check.
  - A scheduled job (for example a GitHub Actions cron hitting the build hook) rebuilds monthly, which keeps the © year, holiday window and specials current.
  - Pillow is needed only with `--images`, so the deploy never installs it.
- **`_headers`:**
  - `/assets/img/*` and `/assets/fonts/*`: `public, max-age=31536000, immutable`. This is safe because every reference carries a content-hash `?v=`.
  - `/assets/css/*` and `/assets/js/*`: the same, for the same reason.
  - HTML: the host default. Never `no-store`.
- **`_redirects`:**
  - Add the merged brand pages (§5.8) and `jobs.html`.
  - Repoint the old WordPress rules straight to their final destinations, with no chains. For example, `/portfolio-item/dermalogica/*` goes to `/products.html#dermalogica`.
- **Sitemap:** update `sitemap.xml`, add the new pages and remove the redirected ones.

---

## 4. Global components

Each component lists its anatomy, behavior and accessibility requirements. All touch targets are at least 44×44px, and all Book, Call and bottom-bar targets are at least 48px.

### 4.1 Utility bar (black, scrolls away)

- **Desktop, 40px:**
  - Left: map-pin icon with "206 Deo Drive, Newark, OH" (links to Google Maps directions, `data-cta="directions"`), then the phone icon with "740-366-1604" as a tel link, then the status slot.
  - Right: the gift slot, the active special if there is one ("{Offer} · ends {date}" linking to `specials.html`), Instagram and Facebook.
  - Text is `--on-ink` at 13–14px. Links are `--gold` (7.69) with a hover underline.
- **Mobile (below 768px), 36px:** the status slot only. Gift cards and specials move into the drawer.
- **Status slot:**
  - Stamped with static fallback text "Hours & holidays" that links to `contact-us.html#hours`.
  - `site.js` replaces it with the live status (§4.15).
  - It sits in a fixed-height row with `white-space:nowrap; overflow:hidden; text-overflow:ellipsis`.
  - It never uses `aria-live`.
- **Gift slot:** both labels, "Gift cards" and "Send a Bellezza eGift card", are in the HTML inside a fixed-width slot. `site.js` toggles them with `hidden` according to `site.json.seasons`: **Nov 1–Dec 24, Feb 1–14, and the 14 days before Mother's Day**, evaluated in America/New_York.
- The bar is not sticky.

### 4.2 Header

- **Desktop (1024px and up):**
  - Sticky, `--paper` background, a fixed 72px tall. After scrolling, the wordmark scales and a `--rule` fades in (§2.5).
  - Left: the wordmark (§2.7), alt "Bellezza & Co.", linking home.
  - Nav (Hanken 500, 16px, ink): **Services & Prices ▾ · Meet the Team · New Guests · Bridal · About**.
  - Right: the text link "Gift cards" (hidden below 1200px, since it is in the utility bar), then the gold **Book now** button (`data-placement="header"`).
- **Services & Prices ▾** (APG disclosure pattern):
  - "Services & Prices" is a real link to `services.html`. A separate chevron `<button aria-expanded="false" aria-controls="nav-services">` opens the panel.
  - The panel is controlled only by JS through that button's `aria-expanded`. No CSS `:hover` or `:focus-within` rule shows it.
  - Hover is an enhancement in JS: the panel opens after 150ms of hover intent and closes 300ms after the pointer leaves both the trigger and the panel. Every change sets `aria-expanded`.
  - Esc closes the panel, returns focus to the button, and keeps it closed until the pointer leaves.
  - Never use `role=menu`. Without JS, the link still goes to `services.html`.
  - The panel is `--white` with `--shadow-pop` and four columns:

    | Column | Links |
    |---|---|
    | **Hair** | Hair · Men's |
    | **Nails** | Nails |
    | **Skin & Body** | Facials · Massage · Waxing · Brows, Lashes & Makeup · Spray Tans |
    | **Occasions & Medical** | Bridal · Slay Aesthetics (medical, separate practice) |

  - Each link shows its price range or "from" price in `--muted`.
  - The panel footer links to "All services & prices".
- **Tablet (768–1023px):** sticky, 56px. Wordmark on the left. On the right, a compact gold "Book" button (at least 44px tall, `data-placement="header-t"`) and the Menu control.
- **Mobile (below 768px):** sticky, 56px, and always visible (no hide-on-scroll). Wordmark on the left and the Menu control on the right. **There is no Book button in the mobile header.** Booking is covered by the hero CTAs and then the bottom bar, so two gold buttons are never on screen together.
- **Menu control:**
  - In the static HTML it is `<a class="menu-toggle" href="#footer-nav">Menu</a>`, so it works with JS off.
  - `site.js` swaps it for `<button aria-expanded="false" aria-controls="drawer">`, which opens the drawer.
  - It always shows the hamburger icon **plus the visible word "Menu"**.
- **Short viewports:** `@media (max-height: 31.25rem){ .site-header, .jump-chips, .team-filters { position: static } }`. At that height, the bottom bar is the only sticky element.
- **Anchor offsets:** `html{scroll-padding-top: calc(var(--header-h) + var(--chips-h,0px) + 16px); scroll-padding-bottom: calc(var(--bookbar-h,0px) + 16px)}`. As a fallback, on `focusin` `site.js` checks whether the focused element's rect overlaps the header or bottom bar and calls `scrollBy` to clear it. Safari doesn't reliably apply scroll-padding when focus moves by keyboard.
- **Skip link:** "Skip to main content" is the first element in `<body>`. `<main id="main" tabindex="-1">`, and `main:focus{outline:none}` applies only to that element.

### 4.3 Mobile menu drawer

- A full-screen sheet on `--paper`, built on `<dialog>` with `showModal()` so it is modal and the page behind it is inert.
  - It traps focus, closes on Esc and with a 44px close button, locks body scroll, and hides the bottom bar while open.
- **Order:**
  1. Book an appointment (gold)
  2. Call 740-366-1604 (outline)
  3. Text us (only if owner question 18 confirms it); Send an eGift card (in gift seasons only); the active special (if any)
  4. **Services & Prices:** all 10 links listed flat, each with its range or "from" price, plus "All services & prices"
  5. Meet the Team · New Guests · Bridal · About
  6. Gift Cards · Specials · Boutique · Pick-up Orders · Careers · Contact
  7. Live status, address and hours table (compact)
  8. App Store and Google Play badges
  9. Instagram and Facebook
- There are no nested accordions.

### 4.4 Mobile bottom action bar (below 768px, every page)

- **Anatomy:** a two-cell grid.
  - The **Book cell** is gold with ink text, 64% of the width, `data-placement="bookbar"`. Its label comes from `pages.json.book_label` ("Book an appointment", "Book a massage", "Book nails", and so on).
  - The **Call cell** is outline ink, with a phone icon plus the word "Call", linking to `tel:+17403661604`.
- **Overrides (`pages.json.book_override`):**
  - `slay-aesthetics.html`: the Book cell becomes an ink Strong button "Book with Slay" linking to Slay's site.
  - `gift-cards.html`: the Book cell becomes an ink Strong button "Buy an eGift card".
- **Size and spacing:** 56px plus `padding-bottom: env(safe-area-inset-bottom)`, on `--white` with a `--line` top border. Body gets `padding-bottom: calc(72px + env(safe-area-inset-bottom))`.
- **Visibility:**
  - Hidden until the hero CTAs have scrolled out of view.
  - Hidden while the CTA band or the footer is in view (IntersectionObserver).
  - Hidden while the drawer or a dialog is open.
  - It never animates in or out based on scroll direction.
- **When closed:** the Call cell reads "Call · opens 9am", using the next opening time from the hours logic. The Book cell never changes.
- **Focus rings:** inside the bar, `outline-offset:-5px` in `--ink`.
- The bar is stamped in static HTML, so it causes no layout shift.

### 4.5 Buttons and links

| Variant | Use | Default | Hover / active | Focus |
|---|---|---|---|---|
| **Book** (`.btn--book`) | **Booking at Bellezza only** | bg `--gold`, text `--ink`, 1px `--gold` border | bg `--gold-lt` (7.98) | 3px `--ink` outline, 3px offset |
| **Strong** (`.btn--strong`) | Other primary actions on light grounds: Buy eGift, Send inquiry, Apply, Book with Slay | bg `--ink`, text `--paper` | bg `--ink-2` | 3px `--ink` outline, 3px offset |
| **Outline** (`.btn--outline`) | Secondary on light: Call, Directions | 1px `--ink` border, text `--ink` | bg `--ink`, text `--paper` | as above |
| **Outline on dark** | All non-book buttons on ink or black | 1px `--gold` border, text `--on-ink` | bg `--gold`, text `--ink` | 3px `--gold` outline |
| **Text link** | Inline links, "Full hair menu", "Meet all 28" | `--gold-text` (`--gold` on dark), 1px underline, 3px offset | `--gold-deep`, 2px underline | outline |

- **Buttons:**
  - Minimum height 48px, padding 14px 24px, `--r-1`, Hanken 600, 16px, sentence case (no all-caps buttons).
  - **No trailing arrows on buttons.** A "→" appears only on menu-card text links ("Full hair menu →").
  - A Strong (ink) button is never placed on an ink or black ground.
- **Focus inside scrolling rows:** inside any `overflow` container (jump chips, filter chips, artist strips), use `outline-offset:-5px`, and give scroll rows `padding-block:6px`.
- **Labels:**
  - "Book an appointment" in the hero and CTA band.
  - "Book now" in the desktop header only.
  - Contextual labels on service pages ("Book a massage", "Book a facial", "Book nails", "Book hair").
  - "Call 740-366-1604" always shows the digits.
- **Banned labels:** "Learn more", "Click here" and "Submit".
- **Booking microcopy** goes under the hero and band CTAs, in `--muted` at 14px: *"Book online 24/7 on our online booking page (Meevo), in the Bellezza app, or call us. Changes need 24 hours' notice. [Policies]"*.
  - Add "You'll sign in or create a free account" only after the Phase 0 Meevo test confirms it.
  - If Meevo can't pre-select a service, service-page microcopy adds "Choose '{Massage}' on the next screen."

### 4.6 Folio line (replaces the mockup's icon trust bar and v1.0's proof band)

- A single line set directly under the hero, on paper, between two `--rule` hairlines. It uses tracked caps (§2.7b) in `--ink`, at `--step--1` on mobile and 15px on desktop.
  - Content: "Est. 2009 • Newark, Ohio • Voted the Number 1 spa in Licking County every year since 2016 • <span data-count="team">28</span> people".
  - Once owner question 1 is answered, the award becomes a text link to its source.
  - Once owner question 2 is answered, "• {4.9} on Google from {312} reviews, as of {Month YYYY}" is appended, from `site.json`, with no stars.
- On mobile the separators become line breaks, so the items stack as a short list.
- It is marked up as `<ul class="folio">`. The bullets are CSS, not text.
- No icons, no slogan and no square footage (that stays on About).

### 4.7 Menu card (the signature element: home and `services.html`)

- A broken-frame card (§2.7a) labeled "The menu • Prices as of {Month YYYY}". It has two columns from 1024px and one column below.
- **Nine groups**, each with:
  - A head in Bodoni `--step-2` `--ink`.
  - A count link in `--gold-text` ("12 hair stylists", linking to `our-team.html#filter-hair`).
  - 2 or 3 real line items: `span.name`, a dotted leader, then the price in Hanken 600 tabular `--ink`. Every value is stamped with `data-price` or `data-range`.
  - "by level" in `--muted` after leveled prices.
  - A closing text link "Full {hair} menu →".

  | Group | Line items (stamped) | Count link | Portrait |
  |---|---|---|---|
  | Hair | Women's cut & finish $37–60 by level · All-over color $70–90 by level | 12 hair stylists | Devon, Salon Manager |
  | Nails | Classic manicure $31–40 by level · Gel manicure $44–58 by level · Pedicures from $48 | 8 nail artists | Stephanie, Spa Manager |
  | Facials | Focus facial from $62 · Custom signature facial $90–96 | 2 skin therapists | Emma |
  | Massage | Relaxation massage, 30–75 min, $42–80 | Jesyca, Senior Massage Therapist | Jesyca |
  | Waxing | Brows from $24 · Brazilian $75–82 by level | Mia and Emma | — |
  | Brows, lashes & makeup | Brow lamination $55 · Lash lift $55 · Special occasion makeup $65 | Makeup artists | — |
  | Spray tans | Single session $35 · Package of 3 $90 · Half body $25 | — | — |
  | Men's | Men's cut from $25 | — | — |
  | Bridal | Bridal style from $75 · Bridal makeup $75 | Plan your bridal beauty → | — |

- **Portraits:** a small 48×64 rectangular portrait sits beside a head only where the table lists one. It is captioned with name and title, never "led by" or "with". Other groups get no image and no placeholder.
- **Price cells:** a cell reading "$$" or "Consultation" on a service page renders as "Priced at consultation", with the chip "Consultation required". It never appears on the card.
- **Below the card, in order:**
  1. **Slay line:** under a `--rule`, set apart from the beauty menu: "Also in the building: Slay Aesthetics, medical aesthetics by Shannon Francis, CNP, on Fridays. [Slay Aesthetics at Bellezza →]" (links to `slay-aesthetics.html`).
  2. **Brand sentence:** "In our boutique: Dermalogica, Olaplex, REF, Lakmé, Smashbox, VOESH, Calecim and ECRU New York." (links to `products.html`).
  3. **Quiz line:** "Not sure who to book? [Take the match quiz] or call 740-366-1604." Shown only once owner question 4 confirms the quiz is live and ends in a booking link.
  4. **Special line:** the active special, if any ("{Offer} · ends {date} · [See the special]").
  5. **Link:** "See all services & prices".
- **Mobile:** groups stack, and each keeps its full line items. There is no hover behavior anywhere.

### 4.8 Price menu (service pages; mobile-first)

- **Section head:** `<h2 id="prices">Menu & prices</h2>` comes before the chips, so menu-group `<h3>`s nest correctly in the outline.
- **Jump chips:** on pages with 3 or more groups, a row labeled "On this page".
  - Sticky at `top: var(--header-h)`, with 44px chips on `--paper` and a bottom rule. It stops being sticky on short viewports (§4.2).
  - It scrolls horizontally with a fade on the right edge and ends with an "All sections" chip.
  - Scrollspy marks the current chip with `aria-current="true"` in the selected style: `--ink` fill, `--paper` text and a check icon. Unselected chips are paper with a 1px `--line-strong` border.
  - `@media (forced-colors: active)`: the selected chip gets `outline:2px solid Highlight`.
  - Chip text matches the target heading text exactly.
  - A chip exists only if a `.menu-group` with that id exists.
- **Level legend (`partials/level-legend.html`):** words only, no tick marks or bars.
  - Text: "Prices depend on your provider's level: Jr Associate · Associate · Senior · Expert · Master. Levels set the price."
  - Add "Levels reflect experience. Every level is fully trained." only after owner question 23 confirms it.
  - Each level word links to `new-guests.html#level-{slug}`, with `min-height:24px` and padding.
  - Nail and skin pages show Associate · Senior · Expert only.
- **Group:** `<div class="menu-group" id="SLUG">`, then `<h3>` in Bodoni `--step-2` with a 1px gold rule underneath, an optional `<p class="group-intro">`, the list, and then a "Book this" text link with a contextual label.
- **Standard rows:** a flex row with `span.name` (Hanken 500, ink), a `.dots` leader (1px dotted `--line-strong` at 40% opacity, decorative), and `span.price` (Hanken 600, tabular, ink). The following `<p>` is the description in `--text` at 16px.
- **Slash-price groups (nail, skin, wax):**
  - A right-aligned column header above the list: `<p id="tiers-PAGE-GROUP" class="tier-head">Associate / Senior / Expert</p>` in `--step--1` `--gold-text`.
  - The list gets `aria-describedby="tiers-PAGE-GROUP"`.
  - The price text itself is not changed.
- **Level ladder groups** (salon groups whose rows are stylist levels): `<ul class="price-list price-list--ladder">`.
  - From 480px, the five items render as equal cells, with the level name at 13px uppercase above the price at 22px.
  - Below 480px, they render as a compact two-column table with 36px rows.
  - The word "Stylist" is wrapped in `<span class="lvl-suffix">` and hidden visually in cells. Schema text is unaffected.
- **Notes:** item-level policy notes go under the description as `<p class="note">` in a sand chip. Example: "Consultation required · $50 deposit" on GK Keratin.
- **No accordions and no tabs** for prices. Every price is visible and searchable with Ctrl+F.
- **Foot of the menu:** `<time data-asof>` ("Prices as of {Month YYYY}"), then the policy strip "24-hour notice for changes · Repeat no-shows may require a deposit · [Full policies]".

### 4.9 Team card and bio

```html
<li class="team-item" id="devon" data-dept="hair bridal leadership" data-level="5">
  <div class="card">
    <img src="assets/img/team/devon-540.webp?v=…" srcset="…180w,…360w,…540w" sizes="(min-width:1024px) 22vw,(min-width:768px) 30vw,46vw"
         width="540" height="720" alt="Devon, Salon Manager and Director of Education at Bellezza & Co." loading="lazy" decoding="async">
    <h3>Devon</h3>
    <span class="role">Salon Manager, Director of Education &amp; Master Stylist</span>
    <ul class="tags"><li>Hand-sewn extensions</li><li>Blonding</li><li>Special occasion</li></ul>
    <button type="button" class="card-bio" data-bio="bio-devon" aria-haspopup="dialog">Read Devon's bio</button>
    <a data-book data-cta="book" data-placement="team-devon" href="…">Book<span class="sr-only"> an appointment (ask for Devon)</span></a>
    <a href="https://www.instagram.com/…">See Devon's work on Instagram</a>
  </div>
</li>
```

- **Card:**
  - Portrait 3:4 on `--black`. Name in Bodoni `--step-1` `--paper`. Role in Hanken 500 14px `--on-ink`. Tags in `--on-ink-muted`.
  - The level is shown only as the word in the role title ("Senior", "Master"). There are no level bars or ticks.
  - On hover, the image scales to 1.03 and a gold underline draws under the name.
- **Book link:**
  - Present only on cards whose `data-dept` includes hair, nails, skin, massage or makeup. Janet and the four Client Services team members get no Book link. Shannon's card links to `slay-aesthetics.html` ("Slay Aesthetics at Bellezza").
  - It goes to the general Meevo URL. It is labeled "Book with Devon" only after Meevo confirms a provider deep link. Until then the label is "Book", and the dialog says "Ask for Devon when you book."
- **Owners:** Lisa's and Ashley's cards and bios say "Behind the chair one day a week."
- **Instagram:** only the 18 links that already exist, placed after Book, labeled "See {name}'s work on Instagram".
- **`dialog.bio`:** `<dialog class="bio" id="bio-devon" aria-labelledby="bio-devon-h" closedby="any">`.
  - The first element is a 44px close button with `autofocus`.
  - Then the image (same `src` as the card, `loading="lazy"`, with `width`/`height`), `<h2 id="bio-devon-h">`, `<span class="role">`, then `<p>` bio text (100 to 200 words, facts only, from the existing bio).
  - Then a credential list (school, year, years of experience, year joined), links to the service pages this person performs, Instagram, and Book.
  - Backdrop is `rgb(28 28 28/.6)`. `body:has(dialog[open]){overflow:hidden}`. The JS backdrop-click close stays as a fallback.
- **No-JS:** `<noscript><style>dialog.bio{display:block;position:static}</style></noscript>` renders every bio inline after the grid. The bio button falls back to an in-page link.

### 4.10 "Your artists" strip (service pages)

- Heading: "Your artists for this service". It shows 3 to 8 people as 56×75 rectangular portraits (3:4), each with first name and title, linking to `our-team.html#slug`.
- On mobile it scrolls horizontally, with a "Meet all" link at the end.
- Only people whose verified title or bio names that service are included (mapping in §5.3).

### 4.11 CTA band (final section, every page)

- Ink ground, **left-aligned**, section padding.
- H2 (static HTML): "Book online any time, or call 740-366-1604." It is roman, `--paper`, and has no eyebrow.
- `site.js` puts the status line above the H2, in `--gold`:
  - When open: "Open now until 8pm."
  - When closed: "Book online 24/7 · We open Mon at 9am."
- Below, a two-column row: today's hours (linking to the full table), and the address as a directions link.
- Buttons: **Book an appointment** (gold, `data-placement="band"`, or the page's `book_override`) and **Call 740-366-1604** (outline on dark).
- Booking microcopy follows.
- Stamped as a partial. The bottom bar hides while the band is in view.

### 4.12 Footer (black)

- **Four columns on desktop, two on mobile.** Plain links, no accordions. The nav is `<nav id="footer-nav" aria-label="Footer">`.
  1. **Visit:**
     - The framed logo lockup on dark, and "Est. 2009 • Salon • Spa • Boutique".
     - The address, linking to directions, and the phone as a tel link.
     - The hours table, with today marked (§4.15), and a "Holiday hours" link to `policies.html#holidays`.
     - The line "Bridal inquiries: dsabo@bellezzaspaonline.com", as text with a mailto link.
  2. **Services & Prices:** all 10 service pages plus "All services & prices".
  3. **Plan your visit:** New Guests · Book Online · Gift Cards · Specials · Boutique · Pick-up Orders · the App Store and Google Play badges.
  4. **About:** Our Story · Meet the Team · Careers · Policies · Privacy · SMS Privacy · Contact.
     - Add "Review us on Google" (GBP review URL) once owner question 2 is answered.
     - Add "Rate your visit" (Meevo Five Star) **only** after owner question 21 confirms, in writing, that the flow offers the Google review link after every rating.
- **Bottom row:** "© {year} Bellezza & Co. (formerly Bellezza Salon and Day Spa)", the legal entity name once owner question 20 supplies it, Instagram and Facebook.
- Headings in `--gold` (7.69), links in `--on-ink`, with 44px link rows on mobile.

### 4.13 Forms (bridal inquiry, careers application, pick-up orders)

- **Handling:**
  - Netlify Forms (`data-netlify="true"`, `netlify-honeypot="bot-field"`). The honeypot field sits inside `<p hidden>` with `autocomplete="off" tabindex="-1"`. If Cloudflare is chosen, a form service replaces Netlify (§3.5).
  - `forms.js` handles submission and shows a `role="status"` success panel. The static POST works without JS.
- **Fields:**
  - A visible `<label>` above each field (Hanken 600, 15px, ink).
  - Inputs 48px tall, 16px text, `--white` background, 1px `--line-strong` border, `--r-1`.
  - Forms sit only on paper or white.
  - Mark **optional** fields in text; required fields are not marked.
  - `autocomplete` tokens: `given-name`, `family-name`, `email`, `tel` (with `type=tel inputmode=tel`), and `postal-code` only where relevant.
- **Validation:**
  - Runs on blur and on submit.
  - Invalid fields get `aria-invalid="true"` and `aria-describedby` pointing to an inline message: "Error:" prefix, icon, 2px `--gold-deep` left bar, ink text.
  - On submit, focus moves to an error summary that links to each field.
- **Privacy:** every form shows the line "How we use this information", linking to `policies.html#privacy`.
- **Routing:** before launch, notifications are routed to the confirmed recipients and each form is test-submitted: bridal goes to dsabo@bellezzaspaonline.com, and careers goes to the hiring inbox the owner names.
- **Bridal inquiry:**
  - Fields: name, email, phone, wedding date (`type=date`), party size, services (checkboxes: bridal hair, bridal makeup, party hair, party makeup, travel team), message (optional).
  - Success message: "Thank you. Our Bridal Coordinator will reply by email."
  - No timeframe unless owner question 6 supplies one. "A copy is on its way to your inbox" only if an auto-reply is set up.
- **Careers:**
  - Position as a `<fieldset><legend>` group of radios, pre-selected via `?position=` (keeps 3.3.7).
  - A file input with the accepted types and maximum size written out. It replaces the `REPLACE-ME` provider placeholder.
  - **Never collect** date of birth, age, a photo, or any protected-class data. If the owner needs an age check, ask "Are you 18 or older? Yes / No".
- **Pick-up orders:** the existing fields, restyled, plus a plain process list: "Request online → we send you a payment link → pay → pick up in the salon or curbside. Allow 24 hours for processing."

### 4.14 Breadcrumbs

- On every page except home: `<nav aria-label="Breadcrumb"><ol>` at 14px in `--muted`, with the current page marked `aria-current="page"`.
- The trail (for example Home / Services & Prices / Nails) comes from `pages.json` and matches the BreadcrumbList. It wraps on mobile rather than truncating.

### 4.15 Hours, live status and holidays

- **Status (`site.js`):** computed with `Intl.DateTimeFormat('en-US',{timeZone:'America/New_York'})`, never the device clock.
- **Strings:**

  | State | Text |
  |---|---|
  | Open | "Open now · until 8pm" |
  | Before opening | "Opens today at 12pm" |
  | Closing early | "Closing early today at 12pm" |
  | Closed (utility bar, Visit) | "Book online 24/7 · We open Mon at 9am" |
  | Holiday | "Closed today for Labor Day · Book online 24/7" |

  The status never leads with "Closed".
- **Regular hours:** Mon 9–8, Tue 9–8, Wed 12–8, Thu 9–8, Fri 9–7, Sat 8–3, Sun closed.
- **Holidays:**
  - Closed Jan 1, Memorial Day (last Monday of May, computed), Jul 4, Labor Day (first Monday of September, computed), and Dec 25 and 26.
  - Close at 12pm on Dec 24 and Dec 31.
  - Close at 5pm on Jul 3.
  - Close at 5pm on Newark Trick-or-Treat night. The date comes from `site.json.trickOrTreat` for each year. If a year's date is missing, the holiday table says "Trick-or-Treat night (date set by the city): closing at 5pm", and the status logic ignores it.
- **Static tables:** the hours table and holiday table are static HTML partials (`id="hours"`). JS marks today's row with font-weight 600, a visible "Today" label and `aria-current="date"`. `openingHoursSpecification` comes from the same `site.json`.
- **Status slots:** each has static fallback text (§4.1).

### 4.16 Photo slots (owner view only)

**Rule:** public pages never show a placeholder. Every template has a no-image variant, and missing photos simply aren't there.

```html
<div class="ph" hidden aria-hidden="true" data-ph="09" data-ph-note="Men's cut mid-service, 4:5, min 1600px tall" style="--ar:4/5"></div>
```

- **Owner view:** loading any page with `?photos=1` (or on localhost) adds `html.show-ph`. That removes `hidden` from `.ph` slots and shows each as a sand plate with a dashed 2px `--gold-deep` outline and the label "PHOTO NEEDED · Shot 09 · Men's cut mid-service · 4:5 · min 1600px".
- **No-image variant (page heads):** a single column, with the H1 at `--step-5`, the "Your artists" strip moved up into the head, and no image column.
- `check.py` fails on any `.ph` without `hidden` and lists every slot for the owner. The shot list is in §10.5.

### 4.17 Other components

- **Quiz callout** (our-team and new-guests only, once owner question 4 confirms the quiz):
  - A sand panel with the H3 "Not sure who to book? Find your match."
  - One line of copy, then a Strong button "Take the match quiz" linking to `https://app.joinmya.com/bellezza` in the same tab (`data-cta="quiz"`).
  - The text line "Or call 740-366-1604 and our front desk will match you."
- **Gift section:** a paper section with gold hairlines top and bottom.
  - H2 "Give an afternoon at Bellezza." and the four real price ideas (custom signature facial $90, relaxation massage from $42, spray tan $35, gel manicure from $44).
  - A Strong button "Send an eGift card" (`data-cta="gift"`).
  - It appears on home only in gift seasons, and permanently on the massages, facials and spray-tans pages.
  - The Slay exclusion is not repeated here. It appears on `gift-cards.html` directly under the buy button, and on Slay, New Guests and Policies.
- **Brand logos:** on `products.html` only, in full color at full opacity, each linking to its `#anchor`.
- **Before/after pair:** a static side-by-side pair on paper (stacked on mobile), labeled "Before" and "After" in HTML. The caption gives the service, and the practitioner once known. No slider and no carousel.
- **Recent work grid** (service pages): 3 to 6 consented work photos at 1:1, each captioned "By Austyn · Senior Hair Stylist" and linking to `our-team.html#austyn`. It is omitted entirely when fewer than 3 consented images exist.
- **Reviews section** (partial `reviews`, rendered only when `site.json.reviews` holds at least 3 entries with `permission: true`):
  - H2 "What clients say on Google".
  - Three verbatim quotes (trimmed only with an ellipsis). Each is attributed with the first name and last initial as shown on Google, month and year, and service if the review names it.
  - Then the line "{rating} on Google from {count} reviews · as of {Month YYYY}" and a text link "Read all our Google reviews".
  - The section is labeled "A selection of our Google reviews".
  - No star icons and no schema.
- **FAQ:** `<details name="faq-PAGE"><summary>` with a 48px summary row and a CSS chevron. Answers are quoted from Policies. No FAQPage schema.
- **Map facade:** a sand panel with the address and a "Show map" button, which injects the Google Maps iframe on click (`loading="lazy"`, title "Map to Bellezza & Co., 206 Deo Drive"). A "Get directions" link sits beside it.

---

## 5. Page-by-page blueprint

**Conventions:**
- **Book** means a `data-book` link to Meevo.
- **(real)** means an existing photo.
- Every page ends with the CTA band (§4.11) and the footer, and every inner page starts with a breadcrumb. These are not repeated below.
- Existing page copy is reused only after the legacy copy audit (§10.6).

### 5.1 `index.html`: Home

**Primary CTA:** Book an appointment.

| # | Section | Content (facts only) | Visual |
|---|---|---|---|
| 0 | Utility bar and header | §4.1, §4.2 | — |
| 1 | **Hero** (paper, 5/7 split) | `<p class="eyebrow">Hair salon & day spa • Newark, Ohio</p>` `<h1>Beauty &amp; relaxation, <em>tailored to you.</em></h1>` **Lede** (max 3 lines at 360px): "Hair, nails, skin, massage and bridal on Deo Drive, from two Newark sisters and their team of <span data-count="team">28</span>." **Buttons**, side by side on every width: **Book an appointment** (gold, 60%, `hero`) and **Call** (outline, 40%, `tel:`). Below: the text link "Explore services & prices" to `#services`, then the status line, then the booking microcopy. | **Contact sheet** (real portraits, §2.6) on `--black`, in columns 6 to 12 bleeding to the right edge. `<picture>` art direction: 28-person sheet from 1024px, 12-person sheet below. Desktop: `<link rel="preload" as="image" imagesrcset="…" imagesizes="58vw" fetchpriority="high" media="(min-width:1024px)">`. Mobile: the image comes after the text, eager, no `fetchpriority`. Alt: "Studio portraits of the Bellezza & Co. team." Figcaption link: "Meet all <span data-count="team">28</span> →" to `our-team.html`. |
| 2 | **Folio** | §4.6 | Type only |
| 3 | **Services** (`#services`, paper) | Eyebrow "Salon • Spa • Boutique". H2 "Our full menu, priced by level." Intro: "Prices depend on your provider's level and are listed for nearly every service. Most can be booked online; keratin, fantasy color and bridal start with a consultation." Then the menu card (§4.7) and the lines below it. | Framed card; small real portraits |
| 3b | **Gift section** (gift seasons only) | §4.17 | — |
| 4 | **Reviews** (only when at least 3 permitted quotes exist) | §4.17 | Type only |
| 5 | **The team** (**black**) | H2 "Meet the <span data-count="team">28</span> people behind Bellezza." A typeset roster, one line per department, in tracked caps with a count, followed by first names linking to `our-team.html#slug`: **Hair (12):** Ashley, Lisa, Devon, Moriah, Emilie, Austyn, Lizbeth, Cherish, Liv, Taylor F, Mya, Kat · **Nails (8):** Stephanie, Paige, Madison, Shelbi, Raegan, Rissa, Hope, Emma · **Skin & waxing (2):** Emma, Mia · **Massage (1):** Jesyca · **Medical aesthetics (1):** Shannon Francis, CNP (Slay Aesthetics) · **Business office (1):** Janet · **Front desk (4):** Melissa, Aubree, Grace, Aeriannah. Then the text link "Meet the team: bios, training and specialties" (in gold on black). | No images: the hero already shows every face |
| 6 | **Our story** (paper) | H2 "Lisa and Ashley bought a Newark house *in 2008.*" Copy: Lisa Jeffries and Ashley Basham were born and raised in Newark and grew up in a family-owned business. After cosmetology school they each worked in other salons. In 2008 they bought an 1,800 sq ft house, opened in 2009, and have grown it to 5,500 sq ft, adding the boutique and the name Bellezza & Co. in 2022. Both are still behind the chair one day a week. Mini timeline 2008 · 2009 · 2022 · Today. Outline button "Read our story" to `about.html`. | `lisa-jeffries.jpg` and `ashley-basham.jpg` (real) side by side, offset 10% vertically, on an `--ink-2` panel, captioned "Lisa Jeffries & Ashley Basham, owners". |
| 7 | **Bridal** (paper, single-column head) | H2 "Bridal hair and makeup for you and your party." Copy: in the salon or with our travel team (fee applies). "Devon, our Salon Manager and Master Stylist, works with our brides." Contact: "our Bridal Coordinator" at dsabo@bellezzaspaonline.com. Strong button "Plan your bridal beauty" (`brides.html#inquiry`) and the text link "See bridal prices". | Devon portrait (real, 3:4, small) |
| 8 | **Visit** (paper) | H2 "206 Deo Drive, Newark." Left: status, address, **Call**, **Get directions**, **Book**. Right: hours table with today marked, and the holiday note linking to Policies. Below: the map facade. | No storefront image (none exists) |
| 9 | CTA band and footer | | |

- **Removed from home:** the permanent gift band, the brand logo strip, the stand-alone quiz section, the transformations section and the proof numerals.
- **Launch check:** at 360×640, the bottom edge of the Book button is ≤ 600px from the top of the page, checked with Playwright.

### 5.2 `services.html` (new): all services and prices

- **H1:** "Services & prices", with the eyebrow "Salon • Spa • Boutique".
- **Lede:** "Every service on our menu, with prices by level." Then the level legend.
- **Body:**
  1. The menu card (§4.7), expanded: each group also shows its descriptor (table below) and its artist count.
  2. "Also at Bellezza": Boutique, Pick-up orders, Gift cards, Specials.
  3. The Slay line.
  4. The quiz line (if confirmed).
- **Primary CTA:** Book an appointment.

| Group | Page | Descriptor | Range shown |
|---|---|---|---|
| Hair | salon | Cuts, color, blonding, keratin, extensions | Women's cut $37–60 by level |
| Nails | tips-and-toes | Manicures, pedicures, gel, dip, Gel X | Manicures $31–40 by level |
| Facials | facials | Dermalogica facials, dermaplaning, nano needling, peels | From $62 |
| Massage | massages | Relaxation, deep tissue, hot stone, Ashiatsu, reflexology, mother-to-be | $42–80 |
| Bridal | brides | Bridal hair and makeup, in the salon or on location | Bridal style from $75 |
| Brows, lashes & makeup | makeup-and-eyes | HD brows, lamination, lash lifts, tinting, makeup | From $20 |
| Waxing | hair-removal | Brows to Brazilian | From $10 |
| Spray tans | spray-tans | Full or half body | From $25 |
| Men's | mens-care | Cuts, manly mani and pedi, fitness facials | Cut from $25 |
| *(separate line)* Slay Aesthetics | slay-aesthetics | Wrinkle relaxers, dermal filler, medication-assisted weight loss · Shannon Francis, CNP · Fridays | Botox $12/unit |

### 5.3 Service page template (all 10 service pages)

1. **Page head** (paper, 7/5 split, or the no-image variant from §4.16):
   - Eyebrow (brand label, for example "Tips & Toes").
   - A bare roman `<h1>`.
   - A 2 to 3 sentence intro, taken from the existing page intro after the audit (§10.6).
   - The range line.
   - **Contextual Book** (gold) and a text link "Send as an eGift card" (not on Slay).
   - Booking microcopy.
   - Right column: the head image per the table below, or the no-image variant.
2. **Your artists for this service** (§4.10), H2.
3. **Recent work** (§4.17), H2. Only when at least 3 consented images exist.
4. `<h2 id="prices">Menu & prices</h2>`, **jump chips** (3 or more groups) and the **level legend**.
5. **Price menu** (§4.8), with "Book this" after each group.
6. **Service notes** (policy chips and verified facts, per the table below).
7. **FAQ** (2 to 4 `<details>`, answers quoted from Policies, including the walk-in answer on nails and men's once owner question 19 is answered).
8. **Gift section** (massages, facials, spray-tans only).
9. **Related services:** 3 text links with descriptive anchors.
10. CTA band and footer.

| Page | H1 | Jump chips (only for existing group ids) | Your artists | Head image | Notes on page | Book label |
|---|---|---|---|---|---|---|
| salon | Haircuts, Color & Extensions | Cuts · Styling · Color · Blonding · Fantasy · Add-ons · Texture · Treatments · Extensions | Ashley, Lisa, Devon, Moriah, Emilie, Austyn, Cherish, Liv (plus "Meet all 12") | No-image variant until shot 02 or work photos exist | GK Keratin: "Consultation required · $50 deposit". Fantasy Color: "Priced at consultation". Specialty Braiding: "Priced at consultation". Extensions: pricing as stated in the Extensions section (consultation requirement pending owner question 25). Level ladder on all level groups. | Book hair |
| tips-and-toes | Manicures & Pedicures (eyebrow "Tips & Toes") | Manicures · Pedicures · Add-ons | Stephanie, Paige, Madison, Shelbi, Raegan (pedicure specialist), Rissa, Hope, Emma | No-image variant until shot 03 or work photos exist | Associate / Senior / Expert tier header | Book nails |
| massages | Massage Therapy | Relaxation · Reflexology · Deep tissue · Hot stone · Ashiatsu · Mother-to-be | Jesyca (Associate degree in massage therapy, Hocking College, 2015) | Jesyca portrait (real) | Rows shown as "60 min · $70". Mother-to-be copy limited per §10.6. | Book a massage |
| facials | Dermalogica Facials | none (1 group) | Emma, Mia | Emma and Mia portraits (real) | Dermalogica and Face Mapping named, with a link to the Dermalogica section of the Boutique | Book a facial |
| hair-removal | Waxing, Brows to Brazilian | none | Mia, Emma | Mia portrait (real) | Fix the spelling "Brazillian" to "Brazilian" in visible text and schema | Book waxing |
| makeup-and-eyes | Brows, Lashes & Makeup | Brows · Brows & lashes · Makeup | Emilie, Lizbeth, Cherish (makeup); brow providers per owner question 8 | `bella-brows.png` re-cropped into a matched **Before/After pair** (real). Caption: "Bella Brows: brow lamination, eyebrow wax and tint." The text baked into the graphic moves to HTML. | — | Book brows or makeup |
| spray-tans | Spray Tanning | none | Per owner question 8 (the strip is omitted until answered) | No-image variant | Service names, prices and "custom shade" only (§10.6) | Book a spray tan |
| mens-care | Men's Cuts & Grooming | none | Per owner question 8 | No-image variant | **Until owner question 7 is answered**, rows are `li.price-ref` items reading "from $X" (the lowest tier on the canonical salon, tips-and-toes or facials page) and linking there. Schema emits only the canonical prices. | Book a men's service |
| brides | Bridal Hair & Makeup | Bridal hair · Bridal makeup · Inquiry | Devon; Emilie, Lizbeth, Cherish (makeup) | Devon portrait (real) | Travel team available for a fee. "Our Bridal Coordinator" and the email as text. **The inquiry form** (§4.13) at `#inquiry` is the primary CTA ("Plan your bridal beauty", Strong). Secondary: "Call 740-366-1604". | Plan your bridal beauty |
| slay-aesthetics | Botox, Fillers & Weight Loss (eyebrow "Slay Aesthetics at Bellezza") | Wrinkle relaxers · Dermal filler · Weight loss | Shannon Francis, CNP | `services/shannon-francis.jpg` plus `slay-logo.png` | See below | Book with Slay (override) |

**Slay Aesthetics (YMYL) rules:**
- **Provider block** near the top: "Shannon Francis, CNP, Certified Nurse Practitioner".
- **Required statement:** "Shannon Francis, CNP, of Slay Aesthetics, offers these treatments at Bellezza & Co. on Fridays, 10am–6pm."
- **Gift cards:** "Bellezza gift cards are not accepted at Slay Aesthetics."
- **Intro:** rewritten as a factual list of services and prices only. Every outcome phrase is removed ("smooth away", "restore youthful contours", "refreshed look", "effectively support"). The weight-loss item uses the menu wording "Medication-assisted weight loss program, $349/month". No drug is named until owner question 11 confirms the medication and whether it is FDA-approved or compounded.
- **Only after owner question 11 confirms them:** "an independent medical aesthetics practice", "Bellezza stylists and therapists do not perform these treatments", "Treatment starts with a consultation", and the Ohio Board of Nursing license verification link.
- **CTAs:**
  - The primary CTA is a Strong (ink) button "Book with Slay Aesthetics", linking to `https://www.slay-aesthetics.com` (swapped for Slay's booking URL when supplied), with `data-cta="slay"`.
  - "Or call 740-366-1604" appears only if the owner confirms the front desk books Slay.
  - The bottom bar and the CTA band use the same override. No gold button appears on this page.
- No results promises, no before/afters and no testimonials.
- Keep the separate MedicalBusiness node (facts only).

### 5.4 `our-team.html`: Meet the Team

- **Head (paper):**
  - H1 "Meet the team".
  - Lede: "<span data-count="team">28</span> people: <span data-count="providers">22</span> stylists, nail artists, skin and massage therapists, our business manager, Shannon Francis, CNP, of Slay Aesthetics, and our four-person front desk."
  - Link "How our levels work" to `new-guests.html#levels`.
  - The text "Team updated {Month YYYY}".
- **Quiz callout** (if confirmed).
- **Filter chips:** sticky (static on short viewports), `aria-pressed`, synced to `#filter-{dept}` hashes, with an aria-live count ("Showing 8 nail artists"). Chips: All · Hair · Nails · Skin & Waxing · Massage · Makeup · Bridal · Aesthetics · Leadership · Client Services.
- **Grid on `--black`:** preceded by `<h2 class="sr-only">The team</h2>`. 2 columns on mobile, 3 on tablet, 4 on desktop.
- **Default order:** owners, then managers (Devon, Stephanie, Janet), Hair by level (Master to Jr Associate), Nails by level, Skin, Massage, Aesthetics, Client Services.
- **Department mapping (`data-dept`):**

  | Department | People |
  |---|---|
  | Hair | Ashley, Lisa, Devon, Moriah, Emilie, Austyn, Lizbeth, Cherish, Liv, Taylor F, Mya, Kat |
  | Nails | Stephanie, Paige, Madison, Shelbi, Raegan, Rissa, Hope, Emma |
  | Skin & Waxing | Emma, Mia |
  | Massage | Jesyca |
  | Makeup | Emilie, Lizbeth, Cherish |
  | Bridal | Devon |
  | Aesthetics | Shannon |
  | Leadership | Ashley, Lisa, Devon, Stephanie, Janet |
  | Client Services | Melissa, Aubree, Grace, Aeriannah |

- **Credential lines (verified only):**
  - Ashley and Lisa: owners since 2009 · behind the chair one day a week
  - Stephanie: American School of Hair Design 2002 · 20+ years · with Bellezza since March 2010 · Spa Manager since 2015
  - Moriah: nearly two decades
  - Emilie: 14+ years · former cosmetology instructor · CCAD Fashion Show
  - Austyn: C-TEC graduate · with Bellezza since 2021 · lived-in color, blonding, ethnic hair, extensions
  - Cherish: joined 2023
  - Taylor F: Salon Institute 2023
  - Mya: Paul Mitchell The School Columbus
  - Paige: C-TEC 2021 · started at Bellezza as an intern
  - Madison: C-TEC 2019
  - Shelbi: C-TEC 2023
  - Rissa: C-TEC 2024
  - Hope: Mason Anthony's
  - Jesyca: Associate degree in massage therapy, Hocking College, 2015
  - Shannon: CNP · Slay Aesthetics · Fridays 10–6
- **Instagram:** only the 18 links that already exist, labeled "See {name}'s work on Instagram".
- **Book links:** per §4.9 (providers only).
- **Roster upkeep:** when someone leaves, remove their card, bio, Instagram link and "Your artists" entries in the same week, and rebuild the contact sheets. `check.py` enforces the mappings.
- **Then:** the "Join the team" band (links to Careers), and the CTA band.

### 5.5 `about.html` (new): Our story

- **Head:**
  - Framed timeline head (§2.7a), labeled "Est. 2009 • Newark, Ohio".
  - H1 "From an 1,800 sq ft house *to Bellezza & Co.*"
  - Lede: "Two Newark sisters, an 1,800 sq ft house bought in 2008, and a salon that has grown to 5,500 sq ft."
- **Founders:** Lisa and Ashley headshots side by side (real, never composited), with names and the title "Owners & Master Hair Stylists". The "& Co" SVG mark sits on this panel (§2.7c).
- **Timeline** (a vertical rule with Bodoni years):
  - **2008:** bought an 1,800 sq ft house.
  - **2009:** opened as Bellezza Salon and Day Spa.
  - **{Year from owner question 9}:** first addition. Until answered, this entry reads "Since then: two additions."
  - **2016:** voted the Number 1 spa in Licking County, and every year since.
  - **2022:** the last addition, the rebrand to Bellezza & Co. and the opening of the boutique.
  - **Today:** 5,500 sq ft, <span data-count="team">28</span> people, and both owners still behind the chair one day a week.
- **"Grew up in a family business":** a one-paragraph fact statement. After cosmetology school, Lisa and Ashley each worked in other salons before opening their own. Add an owner quote only if one is supplied.
- **The team today:** `join-1.jpg`, full width. The caption is "The Bellezza & Co. team, {year taken}" and the alt text is "The Bellezza & Co. team, dressed in black, in a group photo", until owner question 22 confirms the roster and location. Also `join/gallery-1.jpg` (candid), with links to Meet the Team and Careers.
- **Promo video:** a click-to-load facade, only after it is re-hosted on YouTube.
- **CTAs:** primary Book an appointment; secondary Meet the team.

### 5.6 `new-guests.html` (new): Your first visit

- **H1:** "Your first visit".
- **Sections (with jump chips):**
  1. **Choose who:** the quiz callout (if confirmed); "Call and our front desk will match you"; and "Browse the team by specialty", linking to `our-team.html#filter-hair` and the other filters.
  2. **How pricing works** (`#levels`): the five levels in order, each with its own id (`#level-jr-associate`, `#level-associate`, `#level-senior`, `#level-expert`, `#level-master`), with a real example:
     - Women's haircut: $37 (Jr Associate), $40, $48, $50, $60 (Master).
     - Gel manicure without removal: $44 / $49 / $53 (Associate / Senior / Expert).
     - Then "Levels set the price. Book the level that fits your budget." There are no invented criteria.
  3. **How to book:** online 24/7 on our online booking page (Meevo); in the Bellezza app (badges); or call 740-366-1604.
  4. **Changes and cancellations:** 24 hours' notice. After a no-show or same-day cancellation: first a reminder, then a 50% deposit for future bookings, then 100% prepayment.
  5. **Salon etiquette:** silence phones, no speakerphone, quiet voices, and arrange childcare for your own appointments.
  6. **Good to know:**
     - Keratin needs a consultation and a $50 deposit.
     - Slay Aesthetics does not accept Bellezza gift cards.
     - The bridal travel team is available for a fee.
     - Walk-ins, payment methods, gratuity, accessibility, children as clients and arrival time are added once owner question 19 is answered.
  7. **FAQ** (`<details>`) restating sections 1 to 6 as questions.
- Parking and arrival details appear **only after the owner confirms them** (owner question 5).
- `<meta name="apple-itunes-app" content="app-id=…">`, using the App Store id from the URL already in `site.js`.
- **Primary CTA:** Book an appointment.

### 5.7 `book-online.html`: How online booking works

- **H1:** "Book online".
- **Content:**
  - What happens next: "You'll choose your service, provider and time on our online booking page (Meevo)", plus the verified steps from the Phase 0 Meevo test.
  - A big **Book an appointment** button.
  - The app badges.
  - "Prefer to call? 740-366-1604".
  - A policy summary and the quiz line.
- `<meta name="apple-itunes-app">`, as on New Guests.
- The page is linked from the footer and New Guests, never from a Book button.
- Keep the ReserveAction schema.

### 5.8 Boutique, gift cards, pick-up, specials

- **`products.html`: The Boutique.**
  - H1 "The Boutique". Lede: "Professional brands we carry in our Newark boutique."
  - `a.brand-card` elements at the top act as an index, with `href="products.html#slug"`, full-color logos.
  - Eight anchored brand sections (`#dermalogica`, `#ref`, `#lakme`, `#voesh`, `#olaplex`, `#smashbox`, `#calecim`, `#ecru-new-york`). Each has the logo and 1 or 2 rewritten sentences.
  - In-salon usage is stated only where verified: Dermalogica (Face Mapping in our facials) and Lakmé (K2.0 Bond Restoration on the salon menu).
  - Then the link "Order for pickup".
  - **Before any 301:** check 12 months of Search Console data for each `products-{brand}.html`. A page with more than 50 impressions a month stays as a standalone page with unique copy and a contextual Book CTA (for example "Book a Dermalogica facial"). The rest get a 301 to `/products.html#{brand}`.
- **`gift-cards.html`:**
  - H1 "Gift cards".
  - A Strong button "Buy an eGift card" (Meevo eGift, same tab, `data-cta="gift"`). Directly under it: "Not valid at Slay Aesthetics."
  - Say "Delivered by email", "instant delivery" or "schedule it for the big day" only once owner question 15 confirms each.
  - Ideas tied to real prices: custom signature facial $90, relaxation massage from $42, spray tan $35, gel manicure from $44.
  - A phone and questions line.
  - The bottom bar override (§4.4).
  - Keep BuyAction.
- **`pick-up-orders.html`:**
  - H1 "Pick-up orders".
  - The process list (§4.13), the form, "Allow 24 hours for processing", the phone number and a curbside note.
- **`specials.html`:**
  - H1 "Current specials".
  - Each offer comes from `site.json.specials` and is shown as HTML text: title, what's included, price, **visible end date** (`data-ends`), and a contextual Book button.
  - Transcribe the text from `specials/*.jpg` into HTML. The images then become decorative with `alt=""`, or are removed.
  - Expired offers fail the build. `site.js` also hides any offer whose `data-ends` is in the past, as a backstop.
  - If no offer is active: "No specials right now. Send a gift card or get the app for member news."
  - Specials appear in the desktop utility bar, the drawer, the home menu card and the footer. They are not in the main nav.

### 5.9 Careers

- **`join-our-team.html`: Careers.**
  - H1 "Careers at Bellezza".
  - A lede, then the benefits: paid training and assisting program, paid vacation, 401K. Which roles get which benefits is stated only once owner question 12 answers it.
  - Proof line: "Paige, now an Expert Nail Artist, started here as an intern."
  - One job card for each role marked open in `pages.json` (title, one-line summary, link to its page).
  - Photos: `join-2.jpg` and `join-3.jpg` (education, real) and `gallery-1..4` (candid).
  - `#apply`: a general application form (§4.13).
  - **No `article.job` on this page.**
  - Primary CTA: "See open roles" / "Apply".
- **Job pages** (built only for roles the owner confirms are open): `job-massage-therapist.html`, `job-nail-therapist.html`, `job-experienced-hair-stylist.html`, `job-new-talent.html`, `job-internship.html`.
  - Each contains one `<article class="job" id="…">` with an `<h2>` and the current copy moved over.
  - Benefits appear per owner question 12.
  - New Talent and Experienced Hair Stylist carry "This position requires a license from the Ohio State Cosmetology and Barber Board."
  - The internship page says "For students with 750 hours completed, adding to the total hours towards their program completion."
  - The apply form is pre-selected for that role.
  - `datePosted`, and `validThrough` from the owner.
- **301:** `/jobs.html` goes to `/join-our-team.html#apply`. Update `/jobs/*` in `_redirects` the same way.

### 5.10 `contact-us.html`: Visit & contact

- **H1:** "Visit us".
- **Order:**
  1. Live status
  2. **Call 740-366-1604**
  3. Text us (if owner question 18 confirms it)
  4. **Get directions** (206 Deo Drive, Newark, OH 43055)
  5. **Book online**
  6. Hours table (`#hours`, today marked)
  7. **Upcoming holiday hours** (generated)
  8. Map facade
  9. Bridal Coordinator email
  10. Social links
  11. "Review us on Google" (after owner question 2)
  12. "Rate your visit" (only after owner question 21)
- No lead form.

### 5.11 `policies.html`

- **H1:** "Policies & guest information".
- **Anchored sections:**
  - `#changes` (24 hours' notice)
  - `#no-shows` (the escalation)
  - `#etiquette`
  - `#deposits` (Keratin $50)
  - `#gift-cards` (the Slay exclusion)
  - `#holidays` (generated table)
  - `#privacy` (website forms: only practices the owner confirms under question 16: what is collected, the form processor, retention, and how to request deletion)
  - `#sms-privacy` (the existing text; the (718) 921-6100 number stays only if owner question 18 confirms it, and is listed in `allowedNumbers`)
- Plain language, with jump chips.
- **Primary CTA:** Book.

### 5.12 `404.html`

- H1 "We can't find that page."
- Links: Services & prices, Book an appointment, Call, Meet the team, Contact.
- `noindex`, so it is exempt from the title and description checks.

---

## 6. SEO, local and CTR

### 6.0 Google Business Profile launch checklist (owner + dev, by launch day)

The map pack and the Google Business Profile (GBP) take most local clicks, so the profile is treated as part of the launch.

**Required at launch:**
- The name is exactly "Bellezza & Co."
- Website link: `https://bellezzaspaonline.com/?utm_source=google&utm_medium=organic&utm_campaign=gbp`.
- Appointment link: the Meevo booking URL. Turn on Reserve with Google through MeevoXchange → Integrations.
- Regular hours, plus holiday Special Hours 12 months ahead.
- Services with prices that match the site.

**Categories:**
- Primary: Beauty salon.
- Secondary: Hair salon, Nail salon, Day spa, Massage spa, Facial spa, Waxing hair removal service, Eyebrow bar, Tanning salon, and a bridal hair/makeup category if GBP offers one.
- Do not add Medical spa to Bellezza's profile. Any listing for Slay is Slay's decision.

**Ongoing (recommended):**
- At least 20 real photos (work, team, interior), then about 4 new ones a month, using the same graded images as the site.
- One Update post a month (specials, gift cards).
- Reply to every review within 7 days.
- Send Meevo's post-visit message to every client with the direct Google review link, and no happy-client filter.
- Apple Business Connect and Bing Places get identical NAP.
- The Instagram and Facebook bio links use `?utm_source=instagram&utm_medium=social` (and `facebook`).
- Rename the app store listings from "Bellezza Salon & Day Spa" to "Bellezza & Co." (owner question 26).

### 6.1 Formulas

- **Title:** `{What people search} in Newark, OH | Bellezza & Co.`, 45 to 60 characters.
  - The city is named once and the brand goes last, spelled exactly. No town lists.
  - The H1 says the same thing in natural words. Internal labels ("Tips & Toes") become eyebrows.
- **Meta description:** 120 to 160 characters, aiming for 140 to 160: `{proof or real price hook}` + `{2–4 specifics}` + `{next step}`.
  - Any "from $X" must equal the build-computed anchor price.
  - Every description is unique.
  - Award wording appears only in the home description, and only after owner question 1 is answered.

### 6.2 Titles and descriptions

| Page | Title | Meta description |
|---|---|---|
| index | Hair Salon & Day Spa in Newark, Ohio \| Bellezza & Co. | Hair, nails, facials, massage and bridal in Newark, OH, from a 28-person team family-owned since 2009. Prices listed by level. Book online anytime. *(After owner question 1: "Voted the Number 1 spa in Licking County every year since 2016. Hair, nails, facials, massage and bridal in Newark, OH. Book online anytime.")* |
| services | All Services & Prices in Newark, OH \| Bellezza & Co. | Our full menu with prices by level: haircuts from $37, manicures from $31, massage from $42, facials from $62, plus waxing, brows, spray tans and bridal. |
| salon | Haircuts, Color & Extensions in Newark, OH \| Bellezza & Co. | Women's cuts from $37 and all-over color from $70, plus blonding, keratin and hand-sewn extensions. Prices by stylist level. Book online anytime. |
| tips-and-toes | Nail Salon & Pedicures in Newark, OH \| Bellezza & Co. | Gel manicures from $44, plus dip, Gel X, structure gel and pedicures from $48 in Newark, OH. Prices listed by nail artist level. Book online anytime. |
| massages | Massage & Day Spa in Newark, OH \| Bellezza & Co. | Relaxation massage from $42 for 30 minutes, plus deep tissue, hot stone, Ashiatsu, reflexology and mother-to-be massage in Newark, OH. Book online anytime. |
| facials | Dermalogica Facials in Newark, OH \| Bellezza & Co. | Dermalogica facials from $62, plus dermaplaning, nano needling and Pro Power Peels by our skin therapists in Newark, OH. See every price and book online. |
| hair-removal | Waxing in Newark, OH: Brows to Brazilian \| Bellezza & Co. | Face and body waxing in Newark, OH: brows from $24, full leg from $80, Brazilian from $75. Prices by therapist level. Book your wax online anytime. |
| makeup-and-eyes | Brows, Lashes & Makeup in Newark, OH \| Bellezza & Co. | Brow lamination $55, lash lifts $55, brow and lash tinting and special-occasion makeup from $65 in Newark, OH. See a real brow result and book online. |
| spray-tans | Spray Tans & Tanning in Newark, OH \| Bellezza & Co. | Spray tans in Newark, OH: a single session is $35, a package of 3 is $90 and a half-body tan is $25. Book online anytime or call 740-366-1604. |
| mens-care | Men's Haircuts & Grooming in Newark, OH \| Bellezza & Co. | Men's cuts from $25, plus manly manicures, pedicures, fitness facials and back treatments in Newark, OH. See every price and book online anytime. |
| brides | Bridal Hair & Makeup in Newark, OH \| Bellezza & Co. | Bridal hair from $75 and bridal makeup $75 for you and your party, in the salon or with our travel team (fee applies). Start with our bridal coordinator. |
| slay-aesthetics | Botox & Fillers in Newark, OH \| Slay Aesthetics at Bellezza | Botox, Xeomin, dermal filler and medication-assisted weight loss by Shannon Francis, CNP, of Slay Aesthetics. Fridays 10-6 inside Bellezza & Co. in Newark. |
| specials | Salon & Spa Specials in Newark, OH \| Bellezza & Co. | Current offers on salon, spa and boutique services at Bellezza & Co. in Newark, OH. Each offer shows its end date. Book online or call 740-366-1604. |
| book-online | Book a Salon or Spa Appointment Online \| Bellezza & Co. | Book hair, nails, facials, massage and more online 24/7, in the Bellezza app or by phone at 740-366-1604. What to expect, and our 24-hour change policy. |
| products | Dermalogica, Olaplex & More in Newark, OH \| Bellezza & Co. | Shop Dermalogica, Olaplex, REF, Lakme, Smashbox, VOESH, Calecim and ECRU New York at our Newark boutique. Order online for in-salon or curbside pickup. |
| our-team | Our Stylists, Nail Artists & Therapists \| Bellezza & Co. | Meet the 28-person team at Bellezza & Co. in Newark, OH: stylists, nail artists, skin and massage therapists, with training, specialties and levels. |
| about | Our Story: Two Sisters, Newark Since 2009 \| Bellezza & Co. | Sisters Lisa Jeffries and Ashley Basham grew a Newark house into a 5,500 sq ft salon, spa and boutique. Both still work behind the chair one day a week. |
| new-guests | Your First Visit: New Guest Guide \| Bellezza & Co. | New to Bellezza & Co.? How to choose a stylist, how our level pricing works, our 24-hour change policy and salon etiquette. Then book online or call. |
| join-our-team | Salon & Spa Jobs in Newark, OH \| Bellezza & Co. Careers | Careers at Bellezza & Co. in Newark, OH: stylists, nail and massage therapists, new talent and cosmetology interns. See open roles and apply. *(Roles listed are generated from those marked open.)* |
| job-massage-therapist | Massage Therapist Job in Newark, OH \| Bellezza & Co. | Massage therapist role at Bellezza & Co., a 28-person salon and day spa in Newark, OH, family-owned since 2009. Read the role details and apply online. |
| job-nail-therapist | Nail Therapist Job in Newark, OH \| Bellezza & Co. | Nail therapist role at Bellezza & Co., a 28-person salon and day spa in Newark, OH, family-owned since 2009. Read the role details and apply online. |
| job-experienced-hair-stylist | Hair Stylist Job in Newark, OH \| Bellezza & Co. | Experienced hair stylist role at Bellezza & Co., a 28-person salon with a Director of Education in Newark, OH. Ohio cosmetology license required. Apply. |
| job-new-talent | New Talent Stylist Position in Newark, OH \| Bellezza & Co. | New Talent stylist role at Bellezza & Co., a 28-person salon and day spa in Newark, OH. Ohio cosmetology license required. Read the details and apply. |
| job-internship | Cosmetology Internship in Newark, OH \| Bellezza & Co. | For cosmetology students with 750 hours completed. Earn hours toward your program alongside our team at Bellezza & Co. in Newark, OH. Apply online. |
| contact-us | Hours, Directions & Contact \| Bellezza & Co., Newark OH | 206 Deo Drive, Newark, OH 43055. Call 740-366-1604. Open Mon-Tue 9-8, Wed 12-8, Thu 9-8, Fri 9-7, Sat 8-3. Holiday hours and directions inside. |
| gift-cards | Salon & Spa eGift Cards in Newark, OH \| Bellezza & Co. | Buy a Bellezza & Co. eGift card online for massage, facials, nails, hair and more. Not valid at Slay Aesthetics. Questions? Call 740-366-1604. |
| pick-up-orders | Order Products for Pickup or Curbside \| Bellezza & Co. | Request salon products online, pay by link and pick up in the salon or curbside at 206 Deo Drive, Newark. Allow 24 hours for processing. |
| policies | Booking & Cancellation Policies \| Bellezza & Co. | 24-hour notice for changes, how no-shows and same-day cancellations are handled, deposits, salon etiquette and our privacy policies, in plain language. |
| 404 | Page Not Found \| Bellezza & Co. | (none; `noindex`) |

- `check.py` validates the lengths.
- The "28" in descriptions is stamped at build time from `data-count`.
- After 8 weeks of Search Console data, re-check each title against that page's top impression queries and adjust.

### 6.3 Heading structure

- One `<h1>` per page. It is bare (an inner `em` is allowed only in the three permitted places) and matches the title's meaning.
- `<h2>` for each section. `<h3>` for menu groups and team card names (parser contract). The bio dialog heading is `<h2>`.
- Headings never skip levels, and eyebrows are never headings. `check.py` enforces both.

### 6.4 Internal linking

- Every service page is linked from the header dropdown, the drawer, the footer, `services.html` and the home menu card.
- **Service pages** link to their artists (`our-team.html#slug`), Policies, Gift cards (where relevant), New Guests (the levels section), 3 related services and relevant Boutique brands.
- **Team page:** each bio links to the service pages that person performs.
- **About** links to Team, Careers and Home. **New Guests** links to Team (filtered), Policies, Book Online and Gift cards.
- **Anchor text** is descriptive ("Hair color & extensions", "Meet our nail artists"), never "Learn more".
- **Canonical form:** identical in canonicals, the sitemap and links (`.html` on Netlify).

### 6.5 Images

- **Filenames:** `lowercase-hyphenated-descriptive`, for example `bellezza-team-contact-sheet.jpg`, `devon-salon-manager.jpg`, `bella-brows-before.jpg`. Rename files as they are processed and update references.
- **Alt text:** describe what is visible, in context, with no keyword lists. Decorative images get `alt=""`.
- **Text in images:** meaningful text is never baked into images. The specials graphics and spray-tan promo text move to HTML.
- **Formats and loading:**
  - AVIF, WebP and JPEG via `<picture>` with `srcset`/`sizes`. Every image gets `width`/`height`.
  - The desktop hero is preloaded with `media="(min-width:1024px)"`. The mobile hero image is eager with no priority hint.
  - Images below the fold get `loading="lazy" decoding="async"`.

### 6.6 Other off-site owner actions

- Request brand-locator listings (Dermalogica, Olaplex, Lakmé and the other brands) and listings with the training schools.
- Re-host the promo video on YouTube, then embed it on About with VideoObject markup.

---

## 7. E-E-A-T implementation checklist

**Identity and NAP**
- [ ] Full NAP ("Bellezza & Co.", "206 Deo Drive, Newark, OH 43055", "(740) 366-1604" as a tel link) plus hours in the static footer on every page. The spelling is identical everywhere: site, schema name, GBP, social and app listings.
- [ ] "Formerly Bellezza Salon and Day Spa" appears in the footer and About text, and as `alternateName` in the schema.
- [ ] The only phone number shown is 740-366-1604, plus any number listed with a label in `allowedNumbers`.
- [ ] The About page exists with the verified timeline and founders named, and is linked from the nav, footer, home and Team.
- [ ] Organization details: `foundingDate`, `founder`, `sameAs` (Facebook, Instagram, app listings). `award` is added only once the award source is confirmed.

**Award and reviews**
- [ ] The award uses the exact wording "Voted the Number 1 spa in Licking County every year since 2016".
  - Before launch, the owner names the voting body and the most recent year won. Once named, the source is linked.
  - Until then, the award appears only in the folio and on About. It stays out of meta descriptions, job copy and schema.
  - No badge art.
- [ ] Reviews are quoted verbatim, with permission, under §10.3. The rating and count carry an "as of" date that is less than 90 days old. No star icons, no `aggregateRating`, no `Review` schema.
- [ ] "Rate your visit" is published only after written confirmation that the Meevo flow offers the Google link after every rating. Otherwise the site links "Review us on Google" instead.

**People**
- [ ] Every provider shows name, title and level word, specialties from the facts, school and year where known, years of experience where known, and Instagram where it exists.
- [ ] "Team updated {Month YYYY}" is shown. Departed staff are removed the same week.
- [ ] Every service page shows "Your artists for this service" linking to bios, and bios link back to their services.
- [ ] Team counts are generated from the team page (no "20+").

**Prices and policies**
- [ ] The level system is explained once (New Guests `#levels`) and linked from every price menu.
- [ ] Every listed price is visible with a "Prices as of" date. Consultation-priced items say so plainly.
- [ ] Price lists match across pages (`check.py`). Schema prices equal visible prices.
- [ ] Deposit and consultation requirements sit beside the relevant items.
- [ ] The gift card exclusion appears on Slay, Gift Cards, New Guests and Policies.
- [ ] Policies are in plain language and linked beside every Book CTA. The privacy notice covers the website forms, and the SMS privacy policy is linked.
- [ ] Pages that take money (Gift Cards, Pick-up, Specials) show the phone number, the process and the exclusions.

**Slay Aesthetics (YMYL)**
- [ ] Provider credential, the live-wording practice statement, days and hours, no outcome claims, no drug names until confirmed, its own booking destination, and a separate MedicalBusiness node.

**Content hygiene**
- [ ] Legacy health and efficacy claims have been audited (§10.6).
- [ ] Only real photos are used. Stock images (`hero-1/2`, candle and lily tiles, `about-bg`, `about-parallax`, `search-bg`, `footer-bg`, `tile-*`) and the empty-room photos are removed from every page.
- [ ] JobPosting appears on open-role pages only. Benefits are stated per role only once confirmed.
- [ ] Every specials offer has a visible end date, and expired offers are removed.
- [ ] Licensing (salon and individual licenses, massage licensure) is shown with lookup links once owner question 20 supplies it.

**Phase 4 (after launch)**
- [ ] 4 to 6 care guides by named staff, each with a byline, date, original photos, and links to service and team pages. Each is written or reviewed by the named expert.

---

## 8. Accessibility and performance: hard rules

### 8.1 Accessibility (WCAG 2.2 AA; a failure blocks launch)

1. **Contrast:** text is at least 4.5:1 (large text at least 3:1). UI boundaries and focus rings are at least 3:1. Only the token pairings in §2.1 are used.
2. **Focus ring:** a visible `:focus-visible` ring on everything: 3px `--ink` with a 3px offset on light grounds, and 3px `--gold` on dark. Inside overflow containers and the bottom bar, the offset is `-5px` (§4.5). `outline:none` without a replacement is banned.
3. **Focus not obscured (2.4.11):** `scroll-padding-top` and `scroll-padding-bottom`, the `focusin` fallback, and non-sticky chrome on short viewports keep focused elements clear of the header, chips and bottom bar.
4. **Target size:** at least 24×24px everywhere, at least 44×44px for nav, chips, close buttons, footer links and legend links, and at least 48px for Book and Call.
5. **Skip link and landmarks:** the skip link comes first. Landmarks: `header`, `nav[aria-label="Main"]`, `main#main`, `nav[aria-label="Breadcrumb"]`, and `footer` containing `nav#footer-nav[aria-label="Footer"]`.
6. **Navigation:** APG disclosure pattern, controlled only through JS `aria-expanded`, Esc to close, and `aria-current="page"`. Content opened by hover can be dismissed (1.4.13). No `role=menu`, and the parent link is never hijacked. Without JS, the mobile Menu control jumps to the footer nav.
7. **Dialogs:** native `<dialog>` with `showModal()`, `aria-labelledby`, an autofocused close button, Esc and backdrop close, and a scroll lock. Bios render inline without JS. The drawer works the same way.
8. **No auto-moving content:** no carousels, no scroll-triggered motion, and before/after pairs are static. Motion runs only under `prefers-reduced-motion: no-preference`.
9. **Forms:** visible labels, `autocomplete`, fieldset/legend for groups, errors identified in text plus an icon (3.3.1 and 3.3.3), `aria-invalid`/`aria-describedby`, an error summary, a `role="status"` success message, and the pre-selected position kept (3.3.7).
10. **Not color alone:** prose links are underlined. Selected chips, today's hours and price tiers are conveyed in text or structure, not by color alone. Price tiers use `aria-describedby`.
11. **Reflow:** everything works at 320px width, at 200% and 400% zoom (1.4.10), and with text-spacing overrides (1.4.12). No fixed heights on text containers.
12. **Consistent help:** phone and contact appear in the same relative order on every page (3.2.6). Book is also kept in the same place.
13. **Images:** alt text for all meaningful images and `alt=""` for decoration. Signatures, the "& Co" mark and photo slots are `aria-hidden`.
14. **Link purpose:** repeated "Book" links carry hidden context (`<span class="sr-only"> an appointment (ask for Devon)</span>`).
15. **No third-party widgets:** no accessibility overlays, chat widgets or cookie banners. The analytics tool is cookieless.

### 8.2 Performance (mobile, 75th percentile; a failure blocks launch)

| Metric | Budget |
|---|---|
| LCP | ≤ 2.0s on simulated 4G (target), with ≤ 2.5s as the ceiling for field data |
| INP | ≤ 200ms |
| CLS | ≤ 0.05 |
| Home transfer weight | ≤ 900KB |
| Hero contact sheet | ≤ 160KB AVIF at 1540w (desktop); ≤ 70KB at 800w (mobile) |
| Portrait | ≤ 45KB at 540w; ≤ 6KB at 180w |
| CSS | 1 file, ≤ 60KB unminified / ≤ 12KB brotli as served |
| JS | `site.js` deferred, ≤ 40KB unminified / ≤ 12KB brotli; `forms.js` only on form pages |
| Fonts | 3 files, ≤ 160KB total; 1 preload (2 on home and About) |
| Third-party scripts on load | 0, apart from the analytics script (≤ 1KB, deferred) |

**Rules:**
- The hero is an `<img>` in the HTML. It is never lazy, never a CSS background and never injected by JS. It is preloaded on desktop only.
- `width`/`height` on every image, and `aspect-ratio` on cropped slots.
- The `.page-banner` CSS backgrounds are removed.
- Fonts are self-hosted with metric-matched fallbacks (including the italic) and `font-display:swap`. No Google Fonts `@import` and no CDN.
- Maps, video, Meevo, Mya and Instagram load only as links or click-to-load facades.
- No `content-visibility` on pages with deep links.
- Speculation rules: `prefetch` with `moderate` eagerness for same-origin `*.html`, and `prerender` only with `conservative`. Exclude `?photos=1` and pages with forms.
- No `unload` handlers and no `no-store` on HTML, so the back/forward cache works.
- Cache headers per §3.5.
- Before launch, test with PageSpeed Insights (mobile) on home, salon, our-team and contact. After launch, watch Search Console Core Web Vitals.

---

## 9. Anti-template checklist: we will NOT

1. Put a stock photo anywhere: no cotton, towels, candles, lilies, stones, orchids or empty treatment rooms, and no AI images of people, rooms, storefronts or results.
2. Use icon rows or icon badges in content. Icons are utility-only (phone, pin, clock, close, menu, social, gift, chevron, check), from one Lucide set at a 1.5px stroke.
3. Use script or handwriting fonts, or overlay text on busy photos.
4. Center anything. There are no centered sections.
5. Use carousels, sliders, auto-rotating heroes, drag comparisons, parallax, scroll-triggered reveals, scroll-jacking, cursor effects or WebGL.
6. Use rounded 16px cards with drop shadows, the "three feature cards" pattern, stat-counter numeral bands, or a greyscale "trusted by" logo wall.
7. Use slogans with no facts behind them ("a more beautiful you, always", "where beauty meets relaxation", "highly trained experts", "one standard").
8. Use two-fragment parallel headlines ("X. One Y.").
9. Use italic in more than three headings site-wide, or italicize a single decorative word.
10. Use gold for anything except booking, rules and on-dark text. Two gold buttons never appear in one view.
11. Use trailing arrows on buttons, all-caps buttons, "Learn more", "Click here" or "Submit".
12. Number the homepage sections, or repeat the same 7/5 section head more than twice on one page.
13. Ship empty or placeholder "Transformations", "Testimonials" or photo sections, or show photo slots to the public.
14. Use pop-ups, newsletter modals, chat bubbles, accessibility overlays or promo interstitials.
15. Hide prices behind "call for pricing", render "$$", or put price menus in accordions or tabs.
16. Put a hamburger menu on desktop, or use an unlabeled hamburger on mobile.
17. Use badge art that implies certification (laurels, seals, level bars or skill meters).
18. Use generic section names. Every section contains a Bellezza-specific name, number, price or photo. If a section could be moved to a dentist's site unchanged, it gets rewritten.
19. Load more than two type families, or use weight-300 body text.

---

## 10. Content rules

### 10.1 Never fabricate

Never fabricate any of the following:
- Reviews, testimonials, star ratings or review counts.
- Staff names, titles, levels or credentials.
- Years, statistics, awards or award sources, or press logos.
- Photos, including AI or composite images of the owners together or of the storefront, and before/afters.
- Response times, parking or arrival instructions, or delivery promises.
- Licensing claims, practice-structure claims or medical outcomes.
- Per-provider booking links or quiz durations.
- Benefits per role.

If a fact is not listed in §10.2, it is not published. It goes on the owner question list (§10.4).

### 10.2 Facts available to use (verified from bellezzaspaonline.com and the current page files, 2026-09-29)

**Business**
- Bellezza & Co. (Salon · Spa · Boutique), formerly Bellezza Salon and Day Spa. The logo reads "EST. 2009 BELLEZZA & Co SALON · SPA · BOUTIQUE".
- 206 Deo Drive, Newark, Ohio 43055 · geo 40.086310, -82.422132 · 740-366-1604 (`tel:+17403661604`) · bridal coordinator email dsabo@bellezzaspaonline.com (the coordinator's name is unconfirmed; do not publish Devon's surname).
- Hours: Mon–Tue 9am–8pm, Wed 12pm–8pm, Thu 9am–8pm, Fri 9am–7pm, Sat 8am–3pm, Sun closed.
- Holidays: closed Jan 1, Memorial Day, July 4, Labor Day and Dec 25–26. Close at 12pm on Dec 24 and Dec 31. Close at 5pm on July 3 and on Newark Trick-or-Treat night.
- "Voted the Number 1 spa in Licking County every year since 2016." The source and most recent year are unconfirmed.

**Story**
- Founded in 2009 by sisters Lisa Jeffries and Ashley Basham, born and raised in Newark, who grew up in a family-owned business. After cosmetology school they each worked in different salons.
- In 2008 they bought a 1,800 sq ft house, which has become a 5,500 sq ft salon and spa. It opened in 2009, with two additions since.
- The last addition was in 2022, when they rebranded to Bellezza & Co. and added the boutique.
- Both owners still work behind the chair one day a week.

**Team:** 28 members, with the titles, specialties, schools and years as listed in §5.4. Corrections and additions taken from the current bios:
- Austyn has been with Bellezza since 2021.
- Stephanie joined in March 2010.
- Emilie began her career in Columbus, was on a bridal styling team, and showed work at the CCAD Fashion Show.
- Paige started at Bellezza as an intern.
- Jesyca holds an Associate degree in massage therapy (Hocking College, 2015).
- Devon's bio says she assists brides.
- There are 18 staff Instagram accounts.

**Services and prices:** as published in the `.price-item` markup of the 10 service pages. The anchor prices used in this brief:

| Service | Price |
|---|---|
| Women's cut | $37–60 by level |
| All-over color | $70–90 by level |
| Classic manicure | $31 / 37 / 40 |
| Gel manicure | $44–58 |
| Pedicures | from $48 |
| Relaxation massage | $42 (30 min) to $80 (75 min) |
| Focus facial | from $62 |
| Custom signature facial | $90 / 96 |
| Brow wax | from $24 |
| Full leg wax | $80 / 88 |
| Brazilian wax | $75 / 82 |
| Brow lamination | $55 |
| Lash lift | $55 |
| Special occasion makeup | $65 |
| Spray tan | $35 (package of 3 $90, half body $25) |
| Men's cut | from $25 |
| Bridal style | from $75 |
| Bridal makeup | $75 |
| Botox | $12/unit |
| Slay: medication-assisted weight loss program | $349/month |

- Fantasy Color is listed as "Investment determined at consultation" with a price of "$$". Specialty Braiding is listed as "Consultation".
- Levels: Jr Associate / Associate / Senior / Expert / Master (hair); Associate / Senior / Expert (nail and skin).

**Slay Aesthetics:** "Shannon Francis, CNP, of Slay Aesthetics" offers treatments at Bellezza on Fridays, 10am–6pm. The current page links to `https://www.slay-aesthetics.com`.

**Brands:** Dermalogica (Face Mapping used in-salon), REF, Lakmé (K2.0 Bond Restoration on the menu), VOESH, Olaplex, Smashbox, Calecim, ECRU New York.

**Links:**
- Meevo booking: `https://login.meevo.com/bellezza/ob?locationId=103245`
- eGift: `https://na0.meevo.com/EgiftApp/home?tenantId=100947`
- Ratings (publish only per owner question 21): `https://na0.meevo.com/FiveStarRatingApp/five-star-rating?t=100947&l=103245`
- Mya quiz: `https://app.joinmya.com/bellezza`
- iOS and Android apps (URLs in `site.js`)
- Facebook BellezzaSpaOnline, Instagram bellezza_newark

**Policies:**
- 24 hours' notice for changes.
- No-show and same-day cancellation escalation: a reminder, then a 50% deposit, then 100% prepayment.
- Etiquette: silence phones, no speakerphone, quiet voices, childcare for your own appointments.
- SMS privacy policy (it contains the number (718) 921-6100, which is unexplained).
- Keratin requires a consultation and a $50 deposit.
- Slay Aesthetics does not accept Bellezza gift cards.
- Pick-up orders: request online, pay via a link, pick up in the salon or curbside, 24 hours' processing.
- The bridal travel team is available for a fee.

**Careers:**
- Roles: Massage Therapist, New Talent, Nail Therapist, Internship (750 hours completed; "adding to the total hours towards their program completion"), Experienced Hair Stylist.
- New Talent and Experienced Hair Stylist require a license from the Ohio State Cosmetology and Barber Board.
- Benefits listed site-wide: paid training and assisting program, paid vacation, 401K. Which roles get which is unconfirmed.

**Real photos:**
- 28 headshots (mixed native sizes).
- `join-1` (full team; roster and location unconfirmed), `join-2` and `join-3` (education), `gallery-1..4` (candid).
- The Bella Brows before/after.
- The spray-tan and specials graphics (their text must be transcribed).
- Shannon's photo and the Slay logo.
- Brand logos, `logo.png`, `b-mark.png` and the app badges.
- The empty-room photos exist but are retired from public pages.

### 10.3 Banned mockup content and review rules

**Never publish:**
- The phone number (740) 522-4173, in any format.
- "200 Deo Drive".
- The mockup's hours (Mon–Thu 9–8, Fri 9–6, Sat 9–4).
- Staff names "Kelsey", "Morgan", "Abby" and "Tori".
- The testimonials by "Emily R.", "Jessica M." and "Caitlin B.".
- The AI before/afters, AI storefront, AI owners photo and AI stylist-with-client hero.
- "20+ beauty professionals" and "Salon + Day Spa".
- "© 2024".
- The mockup's lines: "Good Hair Brighter Days", "Beauty Looks Good On You", "Right here in Newark", "a more beautiful you, always", "Design with purpose", "Complete beauty. Total well-being.", "Skilled hands. Kind people.", "Real people. Real experiences." and "from real clients".
- The "Lisa + Ashley" script signature, unless real signatures are supplied.

**Real reviews (FTC 16 CFR 465):**
- Quote them verbatim (or trimmed with an ellipsis), with first name and last initial as shown, platform, month and year, and service if named.
- Get the reviewer's permission before quoting on the site.
- Label the section as a selection and link "Read all our Google reviews".
- No incentives for reviews and no gating. Staff or family reviews must disclose the connection.
- No review schema.

### 10.4 Owner questions (publish only after an answer)

**Launch-gating** (the site launches only when each is answered or its stated fallback is applied): 1, 2, 11, 12, 14, 16, 17, 21.

1. Who runs the "Number 1 spa in Licking County" vote, and what is the most recent year won? Is there a link or official badge? *Fallback:* the claim appears in the folio and on About only.
2. The GBP URL and the GBP review link. Confirm the GBP name is exactly "Bellezza & Co." What are the current Google rating and review count? Collect 6 public Google reviews to quote (at least 2 hair, 2 nails, 1 spa, 1 bridal), with each reviewer's permission. *Fallback:* the reviews section and the rating are omitted.
3. The Meevo test results (Phase 0): Is an account required? Can a URL pre-select a service category or a provider? This is needed for "Book with {name}" and for service deep links.
4. Is the Mya quiz active, and does it end with a booking link? How long does it take? *Fallback:* the quiz is dropped.
5. Parking and arrival guidance for New Guests.
6. The Bridal Coordinator's name, the reply time for inquiries, and whether an auto-reply exists.
7. **Price mismatches to reconcile:**
   - `mens-care.html` shows Men's cut $25–30, Manly Manicure $31–37, Manly Pedicure $44–53, Men's Fitness Facial $55 and Back Cleansing $65.
   - The salon, nail and facials pages show $25/30/33/35, $31/37/40, $48/53/56, $55/60 and $65/72.
8. Who performs spray tans, brow services and men's services (for the "Your artists" strips)? What are Emma's and Mia's levels?
9. The year of the first addition. Optionally, an owner quote and a scan of both signatures.
10. The Newark Trick-or-Treat night date each year.
11. **Slay Aesthetics:**
    - Is it a separate legal entity?
    - Who is the collaborating physician (Ohio standard care arrangement)?
    - Shannon's Ohio Board of Nursing license number, for a public verification link.
    - Is a consultation required first?
    - Which weight-loss medication is used, and is it FDA-approved or compounded?
    - Is Slay's booking URL different from slay-aesthetics.com? Does the Bellezza front desk book Slay?

    *Fallback:* the live-wording statement only, and CTAs to slay-aesthetics.com.
12. Which of the 5 jobs are open now, their `validThrough` dates, which benefits apply to which roles, whether pay may be published, and the hiring inbox address.
13. The current specials, with end dates.
14. Written permission from each staff member for their photo (including the contact sheet) and Instagram link. Client consent for any client photo, including work photos taken from staff Instagram accounts.
15. Is eGift delivery instant? Can the buyer schedule the delivery date? Do you sell physical gift cards in the salon?
16. The host (Netlify or Cloudflare), approval of Plausible's cost for analytics, and the privacy practices for form data (what is collected, the processor, retention, deletion contact).
17. A vector logo file (SVG or AI). *Fallback:* the raster wordmark crop.
18. What is (718) 921-6100 (the SMS provider?)? Can clients text 740-366-1604?
19. Are walk-ins accepted, and for which services? Payment methods? Gratuity policy? Wheelchair access? Children as clients (Tiny Tips/Toes exist)? How early should new guests arrive?
20. Licensing to display: Cosmetology and Barber Board salon and individual licenses, massage licensure (State Medical Board of Ohio), with lookup links. The legal entity name for the footer.
21. Written confirmation that the Meevo Five Star flow offers the Google review link after every rating, not only 4–5 stars. *Fallback:* the link is omitted and "Review us on Google" is used instead.
22. Does `join-1.jpg` show the current team? Where and when was it taken?
23. May we say "Levels reflect experience. Every level is fully trained."?
24. Optional: is there budget for a licensed display face (for example Roslindale Display Condensed or GT Super Display)?
25. Do extensions require a consultation, and how are they priced?
26. Rename the App Store and Google Play listings to "Bellezza & Co.".
27. Substantiation for any legacy claim to be kept (spray-tan ingredient claims, mother-to-be benefits). Approval to add "Please check with your healthcare provider before booking" to the mother-to-be massage.

### 10.5 Shot list (targets for the photo slots and future upgrades)

Shoot everything with one light setup and one grade: warm window or softbox light at about 4500 to 5000K, with cream, black and brass in the frame. Get written client consent for any face.

| # | Shot | Ratio(s) | Replaces or adds |
|---|---|---|---|
| 01 | Stylist and client at the chair, 3/4 over-the-shoulder | 4:5, 3:2 | Candidate alternative hero, to be A/B tested against the contact sheet after launch |
| 02 | Hair color mid-service (foils or brush) | 4:5 | salon head |
| 03 | Gel application close-up | 4:5, 1:1 | tips-and-toes head |
| 04 | Facial, hands on skin | 4:5 | facials head |
| 05 | Massage, therapist's hands, client draped | 3:2 | massages head |
| 06 | Bridal updo detail and mirror reveal | 4:5 | brides head and the home Bridal section |
| 07 | Brow or lash service | 1:1 | makeup-and-eyes |
| 08 | Spray tan booth or product detail | 4:5 | spray-tans head |
| 09 | Men's cut | 4:5 | mens-care head |
| 10 | Lisa and Ashley together | 3:2, 4:5 | About and the home Our Story section (the side-by-side headshots stay as a secondary) |
| 11 | Exterior at golden hour with signage | 3:2 | Visit section and Contact |
| 12 | Boutique shelf with the real brands | 3:2 | products.html |
| 13 | Front desk welcome (Client Services) | 3:2 | New Guests |
| 14+ | Consented before/after pairs: same angle, light and crop, tagged with stylist and service | 4:5 pairs | "Recent work" on each service page, and a future static Transformations grid on home |

### 10.6 Legacy copy audit (before any existing copy is reused)

Before reuse, remove every health, efficacy or ingredient-benefit claim, or get written substantiation for it (owner question 27).

| Page | Rule |
|---|---|
| Spray tans | Keep only service names, prices and "custom shade". Remove the "micro-nutrient technology … vitamins and antioxidants" claim and the "works with all skin types regardless of color or tone" claim. |
| Massage, Mother-to-be | Keep "Designed for clients in their 2nd and 3rd trimester; side-lying with supportive pillows." Remove the symptom-relief list. Add the healthcare-provider line once approved. |
| Facials | Remove "visible results". |
| Slay Aesthetics | Per §5.3. |
| All pages | Replace "secure" in process descriptions with plain facts ("online booking page", "payment link"). |

---

## 11. Build order and acceptance

1. **Phase 0, foundation:**
   - **Decisions and inputs:**
     - Decide the host and analytics (owner question 16). Get the vector logo (owner question 17).
     - Put the site in Git and connect deploys.
   - **Meevo test:** book a real test appointment on iOS Safari and Android Chrome. Record the steps, whether an account is required, and whether deep links are possible (owner question 3).
   - **Baseline:** export the 28 days before launch from:
     - Search Console: clicks, impressions, and CTR by page and query.
     - GBP Performance: calls, website clicks, direction requests and bookings.
     - Meevo: online bookings (new vs returning) and gift card sales.
   - **Build system:**
     - Harden `build-schema.py` and pass the byte-identical regression test.
     - Add `site.json`, `pages.json`, the partials, `build-partials.py`, `check.py`, `font-metrics.py`, `_headers`, `netlify.toml`, the fonts and the image pipeline (grade check, contact sheets).
     - Remove the `site.js` injection.
2. **Phase 0.5, consented work photos:**
   - Collect at least 6 real work photos each for hair, nails, and brows/lashes from staff Instagram accounts, with written staff permission and client consent for any face.
   - Store them in `assets/img/work/{service}/{stylist}-{n}.jpg`, with the credit recorded in `site.json`.
3. **Phase 1, system:** tokens, base, all §4 components and the home page. Get owner review.
4. **Phase 2, pages:** the service template across all 10 pages (after the §10.6 audit), then Team, About, New Guests, Contact and Policies (including `#privacy`).
5. **Phase 3, consolidation:** the Boutique merge (after the Search Console check) and redirects, Careers and the open-role job pages, the Specials transcription, Gift Cards, Pick-up, Book Online and the 404.
6. **Phase 4, after launch:**
   - Swap in photos from the shoot via the photo-slot ids.
   - Add the reviews section when at least 3 permitted quotes exist, and Transformations once consented pairs exist.
   - Write the care guides.
   - Re-check titles against query data at 8 weeks.
   - Review KPIs at 30, 60 and 90 days.

**Definition of done for launch:**
- `python tools/build.py --check` exits 0 on the host.
- Rich Results Test passes on home, salon, our-team, a job page and slay-aesthetics.
- Mobile PageSpeed is green on the four pages in §8.2.
- At 360×640, the bottom edge of the home Book button is ≤ 600px from the top (Playwright).
- A keyboard-only walkthrough of the header, dropdown, drawer, dialogs, filters and forms passes, including with JS disabled for navigation.
- VoiceOver and TalkBack spot checks pass.
- Every Bellezza Book link reaches Meevo and fires a `book` analytics event with its placement. Slay CTAs reach Slay's site.
- A test submission of each form reaches its confirmed inbox.
- The GBP required items (§6.0) are done.
- A KPI table records baseline values for: Book clicks per session, Call taps, eGift clicks, Meevo online bookings, GBP calls and website clicks, and organic CTR for the top 20 queries.
- The owner has signed off on every §10.4 item the launch content uses, and every gated fallback not yet answered is in place.

---

## Rejected critique

- **Template 1, replace the H1 with "Family-run on Deo Drive since 2009":** rejected. It is the owner-approved mockup headline. With the eyebrow moved out of the H1, the lede and folio carry the facts, and "tailored" is backed by the level-priced menu.
- **Template 4, upscale the three 600×800 portraits:** rejected. Upscaling adds no detail. Portraits are served at native size with a 540w maximum variant, which all sources cover.
- **Template 9, the one permitted motion (contact-sheet tiles fading in 30ms apart):** rejected. The sheet is a single image file and is the desktop LCP element, so fading it would delay LCP.
- **Template 13, lock `opsz` to its maximum at display sizes:** rejected. `font-optical-sizing:auto` already maps `opsz` to the pixel size up to 96. Locking it would thin the hairlines on the 20–24px names.
- **Template 15, portrait strips per department on home:** rejected in that form. The hero now shows every face, so repeating the portraits adds weight and duplicate imagery. The department roster is kept as typeset lines with counts and linked names.
- **Conversion 1, make reviews launch-blocking and replace a proof cell with the rating:** partly rejected. Launch can't wait on third-party reviewers' permission, so the section ships only once at least 3 permitted quotes exist. The rating goes into the folio because the proof band no longer exists.
- **Conversion 3, "Slay keeps its own profile":** rejected as written. Slay's listing is Slay's decision. The brief only keeps Medical spa off Bellezza's profile.
- **Conversion 9, a visually hidden colon inside the H1 eyebrow:** superseded. The eyebrow now sits outside the H1 as its own `<p>`.
- **Conversion 14, the massages title "… | Bellezza & Co. Day Spa":** rejected. The brand suffix must be the exact name, so the title is "Massage & Day Spa in Newark, OH | Bellezza & Co." instead.
- **Conversion 14, the facials title "Facials in Newark, OH: Dermalogica Skin Care | Bellezza & Co.":** rejected. At 61 characters it breaks the 60-character gate, and the current title already contains "Facials".
- **Conversion 17, a specials strip under the header on home and service pages:** rejected. On mobile it pushes Book below the 360×640 fold. Specials appear instead in the desktop utility bar, the drawer, the menu card and the footer.
- **a11y-perf 1, a mid-grey grain kept on the hero and proof band:** superseded. The grain is deleted entirely (template 5), which removes the contrast risk.
- **a11y-perf 3, the bio fallback as `<a href="our-team.html#devon">`:** replaced by a `<noscript>` style that renders every bio inline. On the team page that link would only point back to the same card.