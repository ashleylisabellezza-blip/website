# Bellezza & Co.: design directions B, C and D

**30 September 2026 · for branches `design-b`, `design-c` and `design-d` · Option A = `main` (kept as is)**

Each option restyles and re-lays out the same site. These all carry over from A: the pages, copy, ids, `data-*` attributes, schema, forms, `site.js` behaviors (live status, hours and holidays, gift slot, disclosure menu, dialogs, filters, scrollspy) and the photo-slot owner view (`?photos=1`). What changes per branch is the tokens in `styles.css`, the header, footer and band partials stamped by `tools/build.py`, and the page templates.

---

## 0. Rules shared by B, C and D

- **Facts:** only the facts in REDESIGN-BRIEF §10.2 are used. Anything gated in A stays gated:
  - Reviews wait for owner question 2.
  - The Licking County award waits for Q1. Until then it appears only on About.
  - "Book with {name}" deep links: Q3.
  - The match quiz: Q4.
  - Emma's and Mia's levels: Q8.
  - The group-photo roster and caption: Q22.
  - "Levels reflect experience": Q23.
  - **Slay wording:** Slay is always "Slay Aesthetics · medical aesthetics · Fridays". "Separate practice", "independent" and any other statement about how the practice is structured waits for Q11 (§10.1).
- **Photos:** real only.
  - **Off public pages:** the empty-room photos (`services/facial.jpg`, `massage.jpg`, `manicure.jpg`, `mani-room.jpg`, `facial-room.jpg`), `hero-1/2.jpg`, `banner-interior.jpg`, `tile-*.jpg`, `about-*.png`, `footer-bg.jpg`, `search-bg.jpg`, `book-online.jpg` and `services/spray-tan-bg.jpg` (decor graphics), `pick-up.png` (text baked into the image), `services/spray-tan.jpg` (a stock model plus third-party rating claims) and `gift-card.png` (stock).
  - **Consent:** every candid (`join/gallery-*`, `join/join-*`) is published only after Q14. `join/gallery-3` also needs C-1.
  - **Crops:**
    - `join/gallery-3` is only ever used as a 1:1 crop from the top. That keeps the sign and both faces and drops the retail packaging and the "$70" counter card lower in the frame.
    - `join/gallery-2` has a white vignette baked in, so crop it to the center 80%.
  - **Product shots:** set with `object-fit:contain` on white. The REF files sit on a #e5e5e5 ground, so they stay out of mixed product grids. `dermalogica-1` (289px wide) is never shown larger than 180 CSS px.
  - **Resolution:** every `srcset` offers at least 2× the rendered width, up to the source's native size. Nothing is upscaled.
- **Gold still means booking at Bellezza.** A gold fill is used only for Book. On every page, the sticky chrome Book (strip, header or thumb bar) counts as chrome, and **at most one other gold button may be in view at a time.**
  - Per-group and per-department Book links are text links, never gold buttons.
  - **Overrides** (`pages.json.book_override`, as in A §4.4):
    - On `slay-aesthetics.html` the chrome Book becomes that branch's non-gold primary, "Book with Slay", linking to slay-aesthetics.com. That page has no gold at all and keeps A's Slay rules (§5.3).
    - On `gift-cards.html` the chrome Book becomes the non-gold "Buy an eGift card".
- **Ranges shown in nav panels, drawers, tiles and cards** always name their anchor service and are stamped by `tools/build.py` from the service pages: Women's cut $37–60 · Manicures $31–40 · Facials from $62 · Relaxation massage $42–80 · Waxing from $10 · Brows, lashes & makeup from $20 · Spray tans from $25 · Men's cut from $25 · Bridal style from $75 · Botox $12/unit (Slay). A bare category range such as "Hair $37–60" is never shown.
- **Parser contract (unchanged):** `.menu-group > h3`, `li.price-item > .price-head > span.name + .dots + span.price` (then the description `<p>`), team `li.team-item > .card` + `dialog.bio`, `article.job > h2` and `a.brand-card`.
  - The `.dots` element stays in the markup in every branch. A branch may restyle it or hide it.
  - Extra elements in a `li.price-item` go **after** `.price-head` and are never a `<p>`: use `<div class="who">` (names) or `<div class="unit">` (package per-unit price). `build-schema.py` reads the first non-`.note` `<p>` after `.price-head` as the description.
  - **Group heads:** each `h3`'s text must stay byte-identical to `main`. Spans (`.h3-pre`, `.h3-main`, `.h3-sub`) may wrap existing substrings, but must not reorder, add or remove characters, spaces or parentheses. `check.py` compares every `h3` against `main`.
  - **Team markup:** the team may be split into one `<ul>` per block, each preceded by an `<h2>`. Every person still appears exactly once (one `li.team-item`, one id). The filter code hides blocks with no visible cards. A branch that uses jump chips instead of filters sets `data-team-mode="jump"` on the team section, and `site.js` then skips filtering and lets `#filter-*` hashes scroll to the block with that id.
- **Motion:**
  - No auto-rotating anything, no scroll-jacking, no scroll-triggered reveals, and no parallax.
  - Only `opacity`, `transform` and color transitions, inside `@media (prefers-reduced-motion: no-preference)`. Under `reduce`, durations are `.01ms`.
  - Underline draws use a pseudo-element with `transform:scaleX()`, never `background-size` or `width`.
- **Accessibility:** WCAG 2.2 AA. Every ratio below was computed with the WCAG 2.x formula.
  - Touch targets are at least 44px. Book and Call targets are at least 48px on touch layouts: under `@media (pointer:coarse)`, every chrome Book gets a 48px hit area (a pseudo-element) whatever its drawn height.
  - Every page has a visible H1.
  - A's `scroll-padding` and `focusin` fallback keep focused elements clear of every sticky bar (2.4.11).
  - In caps labels, the "e" of eGift sits in `<span class="nocase">` so it stays lowercase.
- **Fonts:** self-hosted WOFF2, Latin subset, `font-display:swap`. Build them with the existing `tools/build-fonts.py` (the fontTools instancer plus `pyftsubset`). Metric-matched fallbacks come from `tools/font-metrics.py`. The figure and feature claims in B2, C2 and D2 were checked against the Fontsource builds of each family.
- **Derived level facts** are stamped by `tools/build.py` from the menus and the `our-team.html` titles, never typed by hand. B, C and D all use them:

| Level | Women's cut & finish | All-over color | Gel manicure, no removal | Who (from `our-team.html` titles) |
|---|---|---|---|---|
| Master | $60 | $90 | — | Ashley, Lisa, Devon, Moriah |
| Expert | $50 | $77 | $53 | Emilie · Stephanie, Paige |
| Senior | $48 | $75 | $49 | Austyn, Cherish, Liv · Madison, Shelbi |
| Associate | $40 | $72 | $44 | Lizbeth, Taylor F · Raegan, Rissa, Hope |
| Jr Associate | $37 | $70 | — | Mya, Kat |

  - Emma and Mia get no level or price line until owner question 8 is answered.
  - Jesyca's massage is priced by duration, not level.
  - Ashley and Lisa always carry the note "behind the chair one day a week".
  - The Men's Cut and Style ladder has four cells ("Expert / Master" is one cell, `cols-4`), and every ladder layout must support that.

- **Specialties** (from the `ul.tags` on each profile, used by D's matrix and the cards in B and C):

| Specialty | People |
|---|---|
| Blonding | Devon, Emilie, Austyn, Liv (Cherish: soft blondes) |
| Lived-in color, balayage and highlights | Devon, Austyn, Liv, Taylor F |
| Customized color | Moriah |
| Extensions | Devon (hand-sewn), Austyn |
| Precision cutting | Moriah, Emilie |
| Updos and special occasion | Devon, Liv, Cherish, Lizbeth |
| Fashion color | Cherish |
| Ethnic hair | Austyn |
| Nail art | Paige, Madison (stamping), Shelbi, Hope |
| Natural nail designs | Rissa |
| Gel manicures and manicures | Stephanie (gel), Shelbi |
| Pedicures | Stephanie, Shelbi, Raegan |
| Custom facials and dermaplaning | Emma |
| Facials and waxing | Mia |
| Relaxation massage | Jesyca |
| Makeup (department) | Emilie, Lizbeth, Cherish |

---

## At a glance: A / B / C / D

| | **A · Editorial menu** (main) | **B · House Light** (led by The Lane) | **C · Bronze & Sand** (led by Yukie Natori NY) | **D · Open Door** (led by Element) |
|---|---|---|---|---|
| Feel | Printed salon menu; magazine polish | Quiet, airy, slow; a warm room with framed pictures | Bold, graphic, banded; one confident system | Bright, friendly, direct; a front desk that routes you |
| Dominant ground | Paper cream, a black team wall, an ink CTA band | Warm plaster (CSS light-fall) under a thin taupe-umber strip | White cut by full-bleed sand bands and deep bronze panels | White and fog grey, framed top and bottom by gold bars |
| Type | Bodoni Moda + Hanken Grotesk | Arsenal (flared caps, wide tracking) + Mulish | Manrope only (400/600), two-tone headlines | Archivo (expanded heavy caps) + one Allura greeting |
| Hero | 28-portrait contact sheet on black | Two tall framed portraits of Lisa and Ashley; H1 bottom-left | Front-desk photo under the gold wall sign, flush left (the owners' portraits if C-1 is declined); arrow capsules | Script greeting, H1, two front doors, team group strip |
| Services | Framed typeset menu card, dotted leaders | 3×3 hairline grid, centered caps heads, a "who's at each level" row | Face-avatar tiles; 1/3–2/3 leader-line lists | Expanded caps between rules; "Who does what" matrix |
| Team | Black wall, 4-up 3:4, typeset roster | 3-up 4:5 on plaster, very large gaps, name left and role right, level price on each card | 1/3–2/3 department blocks, bracket hover, credentials band | Black-and-white 1:1 grid, leadership first, color bio |
| Book chrome | Paper header; mobile bottom bar (Book + Call) | Book pill inside the sticky strip at every width | Gold arrow capsule in the sticky bronze header at every width | Gold header button; mobile thumb bar (Menu · Call · Book) |
| Best for | Showing every face and every price, editorially | Spa and relaxation clients; the founders' story | Comparison shoppers who want prices, credentials and a system | First-timers and phone bookers; the fastest routing |

---

# Option B · House Light

*Led by The Lane Salon (San Francisco)*

## B1. Concept

In 2008 Lisa and Ashley bought an 1,800 sq ft house, and Bellezza opened in it in 2009. House Light makes the site feel like stepping into that house on a bright afternoon:

- A warm plaster ground stays still while the content scrolls over it.
- A thin taupe-umber strip runs across the top.
- Headings are flared, widely tracked capitals.
- Every photo is framed like a picture on a wall. The black-backed studio portraits become dark framed prints on a light wall.

It is the calmest and most "spa" of the four: low density, one idea per screen, big gaps. It keeps The Lane's mood and fixes its conversion gaps:

- Book lives inside the sticky strip at every width.
- The home page asks for the booking twice in the body (hero and band).
- Every price is on the page.
- Hours are in the footer.
- Recruiting never takes the closing slot.

| Signature move | Borrowed from | Where in B |
|---|---|---|
| A "room" ground fixed behind the content | The Lane | Every page (CSS until Bellezza's own wall is photographed) |
| Thin sticky taupe-umber strip with caps nav spread edge to edge | The Lane (with Book added inside it) | Global header |
| Vertical-hairline lockup and split title (`ABOUT \| US`) | The Lane | Logo, inner H1s, up to 3 section heads per page |
| Ghost pills with "›"; one solid fill reserved | The Lane | All buttons |
| Headline-bottom-left hero with two tall portrait frames | The Lane | Home hero: the two founding sisters |
| Name left, role right on one baseline; very large row gaps | The Lane | Team grid |
| Inset "window" CTA band | The Lane | "Ready to book?" closing band on every page |
| Per-stylist price and "Anyone" range in the booking step | The Lane (Mangomint) | Level price on each card; a "who's at each level" row under the level legend |
| Second front door for new clients | Element | "New here?" pill in the logo row and a home section |
| Specialists named per service | Element | "Your artists" row on service pages |
| Book beside every price group, repeated at each decision point | Yukie | A Book text link closes every `.menu-group`; the band closes every page (all go straight to Meevo) |

## B2. Typography

**Files (2, about 48KB):**
1. `arsenal-400-latin.woff2`: Arsenal Regular (OFL, about 18KB). Display only.
2. `mulish-var-latin.woff2`: Mulish variable, instanced to `wght` 400–700 (32KB or less). Text, UI and every number that must align.

Preload the Arsenal file on every page. Font stacks:
- `Arsenal, 'Arsenal Fallback', Optima, Candara, sans-serif`
- `Mulish, 'Mulish Fallback', 'Segoe UI', Arial, sans-serif`

Mulish's default figures are tabular (every digit is 600 units wide), so prices and hours align without `tnum`. Arsenal's figures are proportional and it has no `tnum`. **Arsenal never sets a price, time, phone number or count.** Years and "1,800 sq ft" inside display headings are allowed.

| Token | clamp() | px | Family / weight | Case / tracking | LH | Use |
|---|---|---|---|---|---|---|
| `--b-label` | `clamp(0.8125rem, 0.7917rem + 0.0926vw, 0.875rem)` | 13–14 | Mulish 600 | CAPS · .18em | 1.4 | Strip nav, utility stack, kickers, jump links |
| `--b-role` | `0.875rem` | 14 | Mulish 400 | lowercase · .12em | 1.4 | Roles ("owner & master hair stylist"), level words, "by level", counts |
| `--b-body` | `clamp(1.0625rem, 1.0417rem + 0.0926vw, 1.125rem)` | 17–18 | Mulish 400 | · .01em | 1.8 | Body, price rows |
| `--b-lede` | `clamp(1.125rem, 1.0625rem + 0.2778vw, 1.3125rem)` | 18–21 | Mulish 400 | — | 1.75 | Ledes, review quotes |
| `--b-name` | `clamp(1.0625rem, 1rem + 0.2778vw, 1.25rem)` | 17–20 | Mulish 600 | CAPS · .15em | 1.3 | Stylist names |
| `--b-h3` | `clamp(1.25rem, 1.125rem + 0.5556vw, 1.625rem)` | 20–26 | Arsenal 400 | CAPS · .15em | 1.25 | Menu group heads (centered) |
| `--b-h2` | `clamp(1.5rem, 1.25rem + 1.1111vw, 2.25rem)` | 24–36 | Arsenal 400 | CAPS · .12em | 1.2 | Section heads |
| `--b-title` | `clamp(2.25rem, 1.8333rem + 1.8519vw, 3.5rem)` | 36–56 | Arsenal 400 | Sentence case as written, no transform · .01em | 1.1 | Split titles (inner-page H1s) |
| `--b-h1` | `clamp(2.25rem, 1.7083rem + 2.4074vw, 3.875rem)` | 36–62 | Arsenal 400 | Sentence case · 0 | 1.08 | Home H1 |
| `--b-band` | `clamp(1.75rem, 1.3333rem + 1.8519vw, 3rem)` | 28–48 | Arsenal 400 | CAPS · .1em | 1.15 | Inset band line |
| Buttons | `0.875rem` | 14 | Mulish 700 | CAPS · .1em | 1 | Pills |

- Hierarchy comes from case, tracking and the switch between Arsenal and Mulish, never from weight. There is no bold display type and no italic anywhere.
- Text is written in sentence case in the source and set in caps with `text-transform`. Caps are used only for strings of 4 words or fewer, button labels included.
- Service item names (`span.name`) stay in sentence case (Mulish 600) so long names stay readable.
- Long group heads wrap their existing parenthetical in `<span class="h3-sub">` (a block line in `--b-role`, with the parentheses kept). Example: "COLOR SERVICES – PARTIAL FOIL" / "(face frame & crown brightening)". The text is byte-identical per §0.
- Measures: 38ch in split sections (The Lane's narrow column), 62ch for long-form text.

## B3. Color

- **Proportion:** about 75% plaster ground, 15% framed portraits (their black is the only dark mass), 8% umber and 2% gold.
- **Umber** is a taupe at the gold hue (37–38°, 11% saturation), close to The Lane's #5D564B. It stays visibly greyer than C's bronze (39% saturation), so B's and C's chrome never read as the same brown.
- **New tints** (all on the gold hue, 37–39°):

```css
:root{
  --plaster-hi:#faf8f5; --plaster:#f1ece3; --plaster-lo:#e7e2d9;   /* = cream, sand, line */
  --umber:#504a40; --umber-2:#39352e;                                 /* strip, footer, strong pills */
  --on-umber:#faf8f5; --on-umber-muted:#d8d0c2;
  --b-text:#3d3830; --b-muted:#5e574b; --ink:#1c1c1c;
  --gold:#b8985f; --gold-lt:#c9ae7c; --white:#fff; --black:#000;
  --hair: rgb(80 74 64 / .35);                                        /* decorative hairlines */
}
html{background:var(--plaster)}          /* ground on html so body::before (z -1) always paints above it */
body{background:transparent}
body::before{content:"";position:fixed;inset:0 0 auto 0;height:100lvh;z-index:-1;pointer-events:none;
  background:
    linear-gradient(118deg, transparent 0 36%, rgb(250 248 245 / .85) 52%, transparent 68%),   /* window-light patch */
    repeating-linear-gradient(180deg, transparent 0 calc(5.5rem - 1px), rgb(80 74 64 / .05) calc(5.5rem - 1px) 5.5rem), /* shiplap, optional */
    radial-gradient(120% 90% at 85% 8%, var(--plaster-hi) 0%, var(--plaster) 55%, var(--plaster-lo) 100%);}
@media (prefers-reduced-motion: reduce){ body{position:relative} body::before{position:absolute;inset:0;height:auto} }
```

- `100lvh` stops the ground from jumping when the mobile address bar shows or hides.
- The shiplap lines copy the white board wall behind the front desk (`join/gallery-3`). Drop them if they read as ruled paper in review.
- There is no grain and no image texture.

**Home ground sequence:** umber strip → plaster (every section, each separated by a centered 40×1px umber rule, not a full-width line) → the inset photo band → umber footer.

**Buttons (pills, `border-radius:999px`, 44px on desktop and 48px on touch, a "›" glyph after the label):**

| Variant | Default | Hover / active | Use |
|---|---|---|---|
| **Book** | `--gold` fill, `--ink` text (6.24) | `--gold-lt` (7.98) | Booking at Bellezza only |
| **Ghost** | 1px `--umber` border, `--umber` text | `--umber` fill, `--on-umber` text (8.27), 200ms | Every other action on plaster |
| **Strong** | `--umber` fill, cream text (8.27) | `--umber-2` (11.50) | Non-book primaries: Plan your bridal beauty, Send an eGift card, Book with Slay (including the Slay chrome override) |
| **Ghost on dark** | 1px cream border, cream text | Cream fill, umber text | Strip, band, footer |
| **Text link** | `--umber` text, 1px underline at a 3px offset | 2px underline | Inline links, per-group "Book nails ›" |

**Contrast-safe pairings:**

| Foreground | Background | Ratio |
|---|---|---|
| `--ink` | Plaster, lightest to darkest stop | 16.08 → 13.21 |
| `--b-text` #3d3830 | Plaster | 10.96 → 9.01 |
| `--b-muted` #5e574b | Plaster | 6.74 → 5.54 |
| `--umber` #504a40 (links, ghost text and border) | Plaster | 8.27 → 6.80 |
| Cream | `--umber` / `--umber-2` | 8.27 / 11.50 |
| `--on-umber-muted` #d8d0c2 | `--umber` | 5.73 |
| `--ink` | `--gold` / `--gold-lt` | 6.24 / 7.98 |
| Gold pill edge | Umber strip | 3.21 (meets the 3:1 UI minimum) |
| Cream | Band photo under `rgb(28 28 28/.7)` | ≥ 5.93, even over a pure-white pixel |

**Banned pairings:**
- `--gold-text` #7a6232 on plaster: only 4.50 at the darkest stop.
- Gold as text on umber: 3.21.
- `#a8a196` on umber: 3.43.
- Any text on the band photo without the 70% overlay.

## B4. Layout system

- **Container:** max 1360px, side padding `clamp(1.25rem, 5.5556vw, 5rem)` (20 to 80px). **Grid:** 12 columns, gutter `clamp(1.25rem, 0.6667rem + 2.5926vw, 3rem)` (20 to 48px).
- **Spacing scale:** 8 · 16 · 24 · 40 · 64 · 104 · 168.
  - Section padding: `clamp(5rem, 3.1667rem + 8.1481vw, 10.5rem)` (80 to 168px).
  - Team row gap: `clamp(4rem, 2.4167rem + 7.037vw, 8.75rem)` (64 to 140px).
- **Rhythm:** low density, about 8 blocks on home, and asymmetric splits:
  - Hero: text in columns 1–4, frames in columns 6–12.
  - Split sections: 5/7 or 6/6, with the photo pinned to the container edge.
- **Image ratios:**
  - Hero and bridal frames: 3:5 (tall). Cropping a 3:4 source to 3:5 trims only the sides.
  - Team cards: 4:5.
  - Group photo: 4:3 (native).
  - Inset band: `aspect-ratio:18/7` on desktop, 4/3 on mobile.
  - "Your artists" mini frames: 3:5 at 88px wide, `srcset` 180w/360w, `sizes="88px"`.
- **Headshots:** always a black rectangle on plaster. They are never full-bleed, never circles, and never under text. Use `object-fit:cover; object-position:50% 20%`.
  - The 3:5 hero crop uses the 720w files for Ashley and Lisa (the only people with a 720 variant) and 540w elsewhere.
  - The black backdrop plays the role of The Lane's cognac seamless: 28 people read as one set.
- **Graphic devices:**
  1. **Split title:** `display:grid; grid-template-columns:auto 2px minmax(0,38ch); column-gap:clamp(1.5rem,3vw,2.5rem)`, with an `--umber` rule and the title right-aligned. At most 3 per page. **Below 768px it stacks:** the title left-aligned, then a 40×2px umber rule, then the text.
  2. A 40×1px umber rule under caps heads and between a quote and its attribution.
  3. `--hair` vertical dividers between grid columns (services grid, mega panel, level row).
  4. The shiplap ground.
- **Where future photos slot in:**
  - A new shot, "Bellezza wall" (the white board wall in window light, no people, 2400×1500), becomes the `body::before` image. The CSS gradient stays as its fallback.
  - Shot 01 (stylist and client) takes the left hero frame, and the sisters move to About.
  - Shots 02–09 add a 3:5 frame at the far left of each service head.
  - Shot 11 (exterior) becomes the Visit frame.
  - Shot 12 (boutique) goes on `products.html`.

## B5. Header, navigation, footer

**Desktop (1024px and up):**
- **Tier 1, the strip (sticky):** 44px, `--umber`, `position:sticky; top:0`.
  - Links in `--b-label` cream, `display:flex; justify-content:space-between` across the container: **SERVICES & PRICES ▾ · MEET THE TEAM · NEW GUESTS · BRIDAL · OUR STORY · VISIT**, then a **BOOK NOW ›** gold pill (drawn 36px tall, `data-placement="header"`).
  - The current page gets a 1px cream underline at a 4px offset, plus `aria-current`.
- **Tier 2, the logo row (scrolls away):** 104px on plaster.
  - **Left, the lockup:**
    - the wordmark (`assets/img/brand/wordmark.png`, SVG once the vector logo arrives) at 30px tall
    - a 1px umber vertical rule, 44px tall
    - "EST." stacked over "2009" (Mulish 600, 12px caps, .2em, `aria-hidden`)
    
    The link is named "Bellezza & Co., home".
  - **Right:** a right-aligned stack in `--b-label`:
    - the live status slot
    - `740-366-1604` (tel)
    - "206 Deo Drive, Newark" (directions)
  - Beside the stack, the ghost pill **NEW HERE? ›**, linking to `new-guests.html`.
- **Services & prices ▾:** A's APG disclosure behavior (a link plus a separate chevron button, JS-only open, 150ms/300ms hover intent, Esc).
  - The panel is a solid `--plaster-hi` sheet directly under the strip, with 4 columns separated by `--hair` rules.
  - Column heads are centered Arsenal caps: **HAIR / NAILS / SKIN & BODY / OCCASIONS & MEDICAL**.
  - Each link is Mulish 16px, with its named range from §0 in `--b-role` ("focus facial from $62").
  - Slay reads "Slay Aesthetics · medical aesthetics · Fridays".
  - Panel foot: ghost pills **ALL SERVICES & PRICES ›** and **HOW PRICING WORKS ›**.

**Tablet (768–1023px):** the strip grows to 60px and holds `brand/wordmark-on-dark.png` on the left, then Book (48px) and a **MENU** button. The logo row is replaced by a 36px plaster line (status · phone · address) that scrolls away.

**Mobile (below 768px):**
- The strip is 60px and sticky from load. It holds wordmark-on-dark (22px tall), the gold **BOOK ›** pill (48px) and **MENU** (icon plus word, 48×48).
- One plaster line under it (status and phone, `--b-label`) scrolls away. After that, Call is the first item in the drawer. D is the phone-first option.
- **There is no bottom bar.** The strip carries Book at every width and scroll depth.
- On short viewports (`max-height:31.25rem`) the strip drops to 44px (Book keeps its 48px hit area) and nothing else is sticky.

**Drawer:**
- A `<dialog>` modal right sheet, `min(88vw, 420px)`, on the same light-fall ground. Content is right-aligned (The Lane).
- **Order:**
  1. Book (gold) and Call 740-366-1604 (ghost) pills at the top.
  2. The 10 services, flat, each with its named range in `--b-role`.
  3. Meet the team · New guests · Bridal · Our story · Visit.
  4. A smaller group: Gift cards · Specials · Boutique · Pick-up orders · Careers · Policies.
  5. Compact hours, then social links.
- Links are Mulish 600, 18px caps .15em, in 52px rows. The sheet slides in with `translateX` over 240ms (instant under reduced motion).

**Footer:**
- An umber band with a centered `brand/logo-on-dark.png` at 200px wide and "EST. 2009 • SALON • SPA • BOUTIQUE".
- Then four left-aligned columns inside a 1060px measure:
  - **VISIT:** directions, tel, the hours table with today marked, a holiday link, the bridal email.
  - **SERVICES:** the 10 pages plus "All services & prices".
  - **PLAN:** New guests, Book online, Gift cards, Specials, Boutique, Pick-up orders, app badges.
  - **ABOUT:** Our story, Team, Careers ("We're hiring" lives here), Policies, Privacy, SMS privacy, Contact.
- Bottom row: Instagram and Facebook glyphs, then ©.
- Text is cream (8.27) and `--on-umber-muted` (5.73). There is no gold text.

## B6. Home page

| # | Section (ground) | Content, all real | Images | Conversion purpose |
|---|---|---|---|---|
| 1 | **Hero** (plaster, one viewport) | Left column, bottom-aligned on desktop:<br>• Kicker "HAIR SALON & DAY SPA • NEWARK, OHIO".<br>• H1 "Beauty & relaxation, tailored to you." (`--b-h1`, roman).<br>• Lede (A's): "Hair, nails, skin, massage and bridal on Deo Drive, from two Newark sisters and their team of 28."<br>• **BOOK AN APPOINTMENT ›** (gold, 60%) and **CALL** (ghost) side by side. Below 420px they stack full width, Book first.<br>• Text link "See the menu & prices" to `#menu`, the status line, and A's booking microcopy. | Two 3:5 frames, 48px apart, in columns 6–12: `team/ashley-basham-{360,540,720}.{avif,webp,jpg}` then `team/lisa-jeffries-{360,540,720}.{…}`. Under each, on one baseline: "ASHLEY BASHAM" (`--b-name`) on the left and "owner & master hair stylist" (`--b-role`) on the right. On desktop the first frame is preloaded (`fetchpriority="high"`). On mobile the frames sit side by side after the text. | Founder trust and Book in the first screen. At 360×640 the hero Book's bottom edge sits at ≤ 480px (A's Playwright gate is ≤ 600), and the strip Book is visible from load. |
| 2 | **THE TEAM** (plaster) | H2 caps plus a 40px rule. A's verified line: "28 people: 22 stylists, nail artists, skin and massage therapists, our business manager, Shannon Francis, CNP, of Slay Aesthetics, and our four-person front desk." Ghost **MEET THE TEAM ›** and the text link "How pricing works". | `about/team-group-{560,1120}.{avif,webp,jpg}` framed at 4:3 in columns 1–6. Caption "The Bellezza & Co. team" (Q22 fallback). | People first; routes to the team page. |
| 3 | **Services & prices** `#menu` (plaster) | Split title "Services / & prices" with A's intro sentence. Then a **3×3 grid** of the nine groups and line items from A §4.7:<br>• Each cell has a centered Arsenal caps head, a 40px rule, 2–3 rows and **FULL HAIR MENU ›**. Each row has the name on the left in Mulish 400, the price on the right in Mulish 600, a 1px `--hair` rule under it, and "by level" under the price in `--b-role`.<br>• Cells are divided by `--hair` rules. The grid is 3 columns from 1024px, 2 from 768px, and 1 below.<br>• Below the grid, left-aligned: the Slay line (A's wording), the brand sentence, the quiz line (Q4), the special (if active), and the ghost pill **ALL SERVICES & PRICES ›**. | Type only | Price transparency before the click, where The Lane hid its prices. |
| 3b | **Give an afternoon** (gift seasons only) | Split title plus A's four real price ideas. Strong **SEND AN eGIFT CARD ›**. "Not valid at Slay Aesthetics." | — | Seasonal revenue |
| 4 | **FROM OUR CLIENTS** (Q2 gate) | Up to 3 quotes stacked (no carousel), centered at 40ch in `--b-lede`. Each has a 40px rule, then "{First name} {Initial}. \| GOOGLE REVIEW · {Month YYYY}" plus "· {service}" when the review names one. A stylist named in a quote links to `our-team.html#slug`. The section is labeled "A selection of our Google reviews" and ends with "Read all our Google reviews ›". | — | Proof that sells individual stylists (The Lane's strongest trust device). |
| 5 | **NEW HERE?** (plaster) | Split title "New / here?", then three facts:<br>• "Levels set the price: a women's cut is $37 with a Jr Associate and $60 with a Master."<br>• "Book online 24/7, in the Bellezza app, or call 740-366-1604."<br>• "Changes need 24 hours' notice."<br>Ghost **YOUR FIRST VISIT ›** and "Take the match quiz" (Q4). | — | Element's second door: reassures first-timers. |
| 6 | **BRIDAL HAIR & MAKEUP** (plaster) | A's verified copy: in the salon or with the travel team (fee applies); "Devon, our Salon Manager and Master Stylist, works with our brides"; "our Bridal Coordinator" at dsabo@bellezzaspaonline.com. Strong **PLAN YOUR BRIDAL BEAUTY ›** and the text link "See bridal prices". | A 3:5 frame of `team/devon-{360,540}.{…}` in columns 1–4 | High-value inquiry |
| 7 | **Visit us** (plaster) | Split title "Visit / us". Status, address and the hours table (today marked), ghost **GET DIRECTIONS ›** and **CALL ›**, then the map facade in a 16:9 frame with a `--hair` border. | — (the future exterior shot goes here) | Local intent |
| 8 | **READY TO BOOK?** inset band | Inset to the container edges, `aspect-ratio:18/7`, under an overlay of `rgb(28 28 28/.7)`. Centered, all cream: the status line (from `site.js`), "READY TO BOOK?" in `--b-band`, **BOOK AN APPOINTMENT ›** (gold, `data-placement="band"`), **CALL 740-366-1604 ›** (ghost on dark), and the microcopy. | `team/contact-sheet-{1100,1540}.{avif,webp,jpg}` (on mobile, `contact-sheet-800`), `object-fit:cover`, `loading="lazy"` | Closing conversion. It replaces A's ink band and The Lane's recruiting band. |
| 9 | Footer (umber) | §B5 | — | — |

## B7. Inner pages

**Service page template:**
1. **Head** (no-image default, like The Lane's services page, which looks finished without photos): a split title. The right-aligned H1 is in `--b-title` (e.g. "Manicures & / pedicures"), then a 2px umber rule, then:
   - the eyebrow ("TIPS & TOES")
   - the intro and the range line
   - the contextual **BOOK NAILS ›** (gold), the text link "Send as an eGift card", and the microcopy
2. **Your artists** (The Lane's stylist picker, made static). A wrapping row of 3:5 mini frames, 88px wide. Each frame carries the name in caps, the level in `--b-role`, and the level price ("senior · gel manicure $49"), and links to `our-team.html#slug`.
   - The row wraps into a 2-column grid on mobile, with no horizontal scroller.
   - People are included only per A's §5.3 mapping.
3. `<h2 id="prices">Menu & prices</h2>` as a centered Arsenal caps head.
   - Jump links are a centered caps row separated by hairlines ("CUTS | STYLING | COLOR | …"), with 44px targets.
   - From 768px the row is sticky under the strip, with a scrollspy underline and `aria-current`. Below 768px it wraps and is not sticky.
4. **Level legend** in one Mulish sentence. The level words are set in `--b-role` and link to `new-guests.html#level-*`.
   - Directly under it, once per page, the **who's-at-each-level row**: a 5-cell hairline row (4 on nail and skin pages). Each cell holds the level word, the page's anchor price ("women's cut $48" or "gel manicure $49"), and the linked first names from the §0 table.
   - On the salon page the row ends with "Ashley and Lisa are behind the chair one day a week."
   - It stacks to a 2-column list below 480px.
5. **Price menu:**
   - `.menu-group > h3` is centered Arsenal caps, followed by a full-width 1px umber rule (The Lane).
   - **Standard items** sit in a 2-column grid inside a 1060px measure (1 column below 768px). `.price-head` is a flex row with `space-between`. `.dots` is hidden, and each item gets a 1px `--hair` bottom rule so the eye tracks from name to price. The description `<p>` follows at 16px/1.7.
   - **Ladder groups** span the full measure: 5 (or 4) equal cells, each with the level in `--b-role` above the price at 22px in Mulish 600. Below 480px a ladder becomes a 2-column table with 44px rows. Ladders carry no name lists; the who's-at-each-level row covers them.
   - **Slash-price groups:** a right-aligned `p.tier-head` "associate / senior / expert".
   - `p.note` is a cream inline panel with a `--hair` border ("Consultation required · $50 deposit").
   - Each group ends with **BOOK NAILS ›** as an umber caps text link.
6. **Service notes, then the FAQ:**
   - `<details>` with a caps Mulish 600 summary and a +/– glyph, in rows separated by umber rules.
   - The gift section appears on the massage, facials and spray-tans pages only.
   - Then 3 related-service text links.
7. **The inset READY TO BOOK? band** with the contextual label.
   - **Slay:** the band is plain umber with no photo. The Strong pill **BOOK WITH SLAY AESTHETICS ›** links to slay-aesthetics.com, and the strip's Book follows the §0 override.
   - **makeup-and-eyes:** `work/brows-before-470` and `brows-after-470` as two framed prints labeled "BEFORE" and "AFTER", with the caption in HTML.

**`services.html`:**
- The split-title H1 "Services / & prices".
- The home 3×3 grid, expanded with each group's descriptor and artist count (the counts in Mulish).
- An "Also at Bellezza" row (Boutique · Pick-up orders · Gift cards · Specials), then the Slay line.

**Team (`our-team.html`):**
- **Head:** the split title "Meet / the team", then the lede, **HOW OUR LEVELS WORK ›** and "Team updated {Month YYYY}". The quiz callout (Q4) sits in a cream panel with a hairline frame.
- **Filters:** caps text buttons separated by hairlines (ALL · HAIR · NAILS · SKIN & WAXING · MASSAGE · MAKEUP · BRIDAL · AESTHETICS · LEADERSHIP · FRONT DESK), each 44px tall.
  - They use `aria-pressed`. The selected button is umber with an underline; the rest are `--b-muted`.
  - They sit in a sticky plaster bar under the strip (static on short viewports).
  - They keep the `#filter-{dept}` hashes and update an aria-live count.
- **Grid:** one `<ul>` per block (§0), 3 columns from 1024px and 2 below.
  - The column gap is `clamp(1.5rem, 0.6rem + 4vw, 5.375rem)` and the row gap is B's team row gap.
  - Block heads are centered Arsenal caps with a 40px rule, and carry no numbers: OWNERS & MANAGERS · HAIR · NAILS · SKIN & WAXING · MASSAGE · AESTHETICS · FRONT DESK.
  - The order follows A's default.
- **`.card`:**
  - A 4:5 frame.
  - One baseline row: the `h3` name (`--b-name`) on the left and `span.role` (`--b-role`, `--b-muted`) on the right. The role wraps under the name below 420px.
  - A level-price line in umber `--b-role`, only where the level is verified. Hair shows "women's cut $48 · all-over color $75"; nails show "gel manicure $49".
  - `ul.tags` shown as one lowercase comma-separated line.
  - **Actions:**
    - `button.card-bio` "BIO ›" (ghost pill, 44px)
    - `a[data-book]` "BOOK ›" (umber text link; gold stays in the strip, the bio sheet and the band)
    - "instagram ›" (only the 18 existing links)
  - Janet, Client Services and Shannon follow A's Book rules.
- **`dialog.bio`:** a right side sheet, `min(100vw, 480px)`, on the plaster light-fall ground.
  - A 44px close button with `autofocus`.
  - A 3:5 frame, then the `h2` in Arsenal caps .12em and the role in `--b-role`.
  - The level-price line in Mulish: **"At Senior level: women's cut $48 · all-over color $75"**.
  - The bio (100–200 words, facts only) and a credential list in hairline rows.
  - "Ask for {name} when you book" (until Q3), a gold Book pill (the only gold on the sheet), Instagram, and service links.

**About:**
- The split-title H1 "From an 1,800 sq ft house / to Bellezza & Co." (roman).
- A timeline row of 5 cells separated by hairlines: 2008 · 2009 · 2016 (the award, allowed on About per the Q1 fallback) · 2022 · Today. The years are in Arsenal caps; the facts are A's §5.5.
- The founders as two 3:5 frames.
- `about/team-group-1120` as a static inset window, captioned.
- A candid bento like The Lane's gallery (Q14): rows alternating 1/3 + 2/3 widths with 10px gutters, using `join/gallery-1-800`, `join/gallery-3-800` (1:1 from the top) and `join/gallery-4-800`. `join-2`/`join-3` stay on Careers.

**Contact:**
- The split-title H1 "Visit / us" (The Lane's "Say hello").
- The live status, **CALL** (ghost), **GET DIRECTIONS** (ghost), **BOOK** (gold) and the address.
- The hours and holiday tables in a hairline-framed panel.
- A framed map facade, the bridal email and social links. No form.

**New guests:** each of A's §5.6 sections opens with a split title (at most 3 on the page; the rest use `--b-h2` heads). The levels show as the 5-cell who's-at-each-level row.

## B8. Interaction

- **Pills:** background and color change over 200ms. The "›" moves 2px right on hover (no-preference only).
- **Strip links:** an underline pseudo-element scales from `scaleX(0)` to `scaleX(1)` over 250ms, starting from the left.
- **Mega panel:** fades in over 150ms. The drawer and the bio sheet slide in with `translateX` over 240ms.
- **Cards:** on hover and focus-within, the frame gains `outline:1px solid var(--umber); outline-offset:8px`, and only the outline color transitions (150ms). There is no image zoom.
- **Strip Book:** the gold fill never changes. There is no shrinking header and nothing reacts to scroll direction.
- **Fixed ground:** under reduced motion it becomes `position:absolute`. The inset band's photo is static (The Lane's sticky-image reveal is not used).
- **Focus:** a 3px ink outline at a 3px offset on plaster; a 3px cream outline on umber and on the band.

## B9. Anti-template guardrails (B)

1. Arsenal only at 400, never bold, never italic. It never sets a price, time, phone number or count. Years and "1,800 sq ft" in display headings are allowed.
2. Caps only for heads, labels and buttons of 4 words or fewer. Sentences, ledes, bios and service names are never in caps.
3. Plaster is CSS only (no stock textures, grain or noise PNGs) until Bellezza's own wall is photographed.
4. Photos are always framed rectangles: never full-bleed, never circles, never under text. The only exception is the inset band with its fixed 70% overlay.
5. The strip's Book plus at most one in-body gold pill per viewport. Every other button is a ghost or umber pill, and per-group Book links are text.
6. Centered text only for caps heads, reviews, the inset band and the footer lockup. Anything longer than two lines is left-aligned.
7. At most 3 split titles per page, and never two in a row.
8. Recruiting never appears in the body or the closing band (footer and About only).
9. No chat bubble, carousel, hidden H1, or Salon Policies in the primary nav.
10. Every section carries a Bellezza name, price, date or photo, the same test as A (§9.18).

---

# Option C · Bronze & Sand

*Led by Yukie Natori New York*

## C1. Concept

A confident, graphic site where the brand gold is deepened into **bronze** (`#6a552f`, A's own `--gold-deep`):
- White pages are cut by full-bleed **sand** bands and deep bronze panels.
- A single geometric sans is set big and semibold in sentence case.
- There is a single button shape everywhere: the **arrow capsule**.
- Every list uses the same 1/3–2/3 leader-line layout (price menus, team departments, even the mega menu), so the whole site reads as one system.
- The three tones have jobs: **white** for reading, **sand** for decisions (prices, levels, booking), **bronze** for people and story.

It keeps Yukie's polish and fixes its failures:
- Every Book goes straight to Meevo: no request form, and no paying first and scheduling later.
- Book sits in the sticky header at every width and viewport height.
- The menu has one canonical home.
- The team is profiled by name.
- There is no slideshow, marquee or press wall.
- The H1 is real.

| Signature move | Borrowed from | Where in C |
|---|---|---|
| Strict three-tone full-bleed banding | Yukie | Every page's ground sequence |
| Zig-zag 50/50 splits, photo flush to the viewport edge, text aligned to the grid | Yukie | Hero, founders, bridal, About timeline |
| Arrow capsule as the only button shape | Yukie | All CTAs |
| Leader-line lists: title in the left third, items in the right two-thirds, bracketed sub-notes | Yukie | Service menus, team departments, mega menu |
| Ghost word behind a floating card | Yukie | Levels explainer, no-image service heads, team and About heads |
| Offset corner-bracket frame | Yukie | Credentials portrait, map, bio portrait; card hover |
| Highlighter block and two-tone headline | Yukie | `services.html` H1; up to 3 section heads per page |
| Stat tiles and credentials list | Yukie (founder credentials) | Home and About, verified facts only, static |
| Treatment-as-ritual steps | Yukie (head spa) | Bridal, Keratin, first visit; the signature facial once the owner supplies its steps |
| Faces on the service choice (stylist picker avatars) | The Lane | Avatar stacks on the home service tiles |
| Per-level names under price rows | The Lane | `div.who` bracket sub-labels on ladders |
| "New to Bellezza?" second door | Element | Hero text link, drawer |
| Honest pricing line up front | Element (the "prices vary" disclaimer) | The levels card |

## C2. Typography

**File (1, about 25KB):** `manrope-var-latin.woff2`, Manrope variable, instanced to `wght` 400–700. The weights used are 400 and 600.
- Stack: `Manrope, 'Manrope Fallback', 'Segoe UI', Arial, sans-serif`.
- Manrope's default figures are proportional, but the font ships `tnum`. Prices and hours use `font-variant-numeric: tabular-nums lining-nums`.

| Token | clamp() | px | Weight | Case / tracking | LH | Use |
|---|---|---|---|---|---|---|
| `--c-eyebrow` | `clamp(0.9375rem, 0.9167rem + 0.0926vw, 1rem)` | 15–16 | 400, `--text` | Sentence case, 0 | 1.4 | Plain eyebrows ("Services", "Our story"), bracket notes |
| `--c-body` | `clamp(1.0625rem, 1.0417rem + 0.0926vw, 1.125rem)` | 17–18 | 400 | — | 1.6 | Body |
| `--c-row` | `clamp(1.1875rem, 1.0833rem + 0.463vw, 1.5rem)` | 19–24 | 600 | — | 1.25 | Price rows (name and price), tile ranges |
| `--c-h3` | `clamp(1.375rem, 1.25rem + 0.5556vw, 1.75rem)` | 22–28 | 600 | — | 1.2 | `h3`, menu-group titles, card names |
| `--c-h2` | `clamp(1.875rem, 1.5417rem + 1.4815vw, 2.875rem)` | 30–46 | 600 | -.01em | 1.1 | Section heads |
| `--c-display` | `clamp(2.5rem, 1.8333rem + 2.963vw, 4.5rem)` | 40–72 | 600 | -.02em | 1.02 | H1s, "Book an appointment" band |
| `--c-numeral` | `clamp(2.75rem, 2.1667rem + 2.5926vw, 4.5rem)` | 44–72 | 400 | — | 1 | Static stat tiles |
| `--c-ghost` | `clamp(5.5rem, 3.1667rem + 10.3704vw, 12.5rem)` | 88–200 | 600 | -.03em | .9 | Ghost words (`aria-hidden`) |
| Buttons | `1rem` | 16 | 600 | Sentence case | 1 | Capsule labels |

- **Two-tone headlines** (at most 3 per page, never parallel fragments):
  - On white or sand, the first clause is `--text` #555 and the payoff is `--ink`.
  - On bronze, the first clause is sand and the payoff is white.
- **Highlighter:** exactly one on the whole site, the `services.html` H1.
  - Source: `Services &amp; <span class="hl">prices</span>`, uppercased with CSS.
  - `span.hl` is a sand block (`padding:.02em .2em`) with bronze text (6.04). It is a span, not `<mark>`, so screen readers don't announce "highlighted".
  - It is the only uppercase headline anywhere.
- **Bracket notes** ("[by level]", "[Associate / Senior / Expert]", "[Consultation required · $50 deposit]") use `--c-eyebrow` in `--text`, or bronze where they carry a price.
- No italics, no tracked caps and no second family.

## C3. Color

- **Proportion:** about 55% white, 20% bronze, 15% sand, 10% photography. Gold stays at or below 3% (Book capsules only).

```css
:root{
  --white:#fff; --sand:#f1ece3; --bronze:#6a552f; --bronze-2:#574625; --bronze-band:#7a6232;
  --ink:#1c1c1c; --text:#555; --cream:#faf8f5; --line:#e7e2d9;
  --gold:#b8985f; --gold-lt:#c9ae7c;
  --leader: rgb(28 28 28 / .25);           /* decorative hairline leaders */
  --card-shadow: 0 5px 30px -10px rgb(28 28 28 / .5);  /* the floating card only */
}
```

**Home ground sequence:**
1. white (hero)
2. white (services intro and tiles)
3. **sand** (levels card)
4. **bronze** split (founders)
5. white (stat row)
6. **sand** (credentials)
7. white (reviews, Q2)
8. **bronze** split (bridal)
9. white (gifts and boutique)
10. **sand** (final "Book an appointment")
11. white (Visit)
12. **bronze** footer

Two bronze sections are never adjacent. Sand is always full-bleed.

**Arrow capsule** (`border-radius:999px; min-height:48px; padding:3px 3px 3px 28px`): a 16px 600 label, then a 42px circle holding a Lucide `arrow-right` icon at 18px with a 1.5px stroke. There is also a **small text-link form**: a label plus a 28px bronze circle, used for per-group and per-department Book links.

| Variant | Default | Hover | Use |
|---|---|---|---|
| **Book** | `--gold` fill, ink label (6.24), ink circle with a gold arrow | `--gold-lt` (7.98); arrow moves +3px | Booking at Bellezza |
| **Book on bronze** | As above, plus a `box-shadow:0 0 0 2px var(--bronze), 0 0 0 3px var(--cream)` ring so its edge reads (cream against bronze is 6.71) | As above | Header, bronze panels |
| **Primary** (on white or sand) | Bronze fill, white label (7.11), white circle with a bronze arrow | White fill, 1px bronze border, bronze label; the circle turns bronze | Non-book actions |
| **On bronze** | Cream fill, bronze label (6.71), bronze circle with a cream arrow | Transparent, 1px cream border, cream label | Non-book actions on bronze, including the Slay chrome override |
| **Text link** | Ink with a 1px underline (white on bronze) | 2px bronze underline | Inline, per-group "Book nails" |

**Contrast-safe pairings:**

| Foreground | Background | Ratio |
|---|---|---|
| `--ink` | White / sand | 17.04 / 14.48 |
| `--text` #555 | White / sand | 7.46 / 6.34 |
| Bronze | White / sand / cream | 7.11 / 6.04 / 6.71 |
| White, cream, sand, line | Bronze | 7.11 / 6.71 / 6.04 / 5.51 |
| White | `--bronze-band` #7a6232 | 5.80 |
| White | `--bronze-2` | 9.10 |
| Ink | Gold / gold-lt | 6.24 / 7.98 |

**Banned pairings:** ink on bronze (2.40), and gold as text or as the only edge on bronze (2.61).

## C4. Layout system

- **Container:** boxed 1200px (Yukie uses 1140), side padding `clamp(1.25rem, 5.5556vw, 7.5rem)`.
- **Grid:** 12 columns with a 20px gap (Yukie's widget gap). Tile and gallery gutters are 10px.
- **Spacing scale:** 4 · 8 · 12 · 20 · 28 · 40 · 64 · 96 · 140. Section padding is `clamp(4rem, 2.4167rem + 7.037vw, 8.75rem)` (64 to 140px).
- **Compositions:**
  1. **Intro row:** eyebrow in columns 1–2 | H2 in columns 3–7 | paragraph in columns 8–12. It stacks below 1024px.
  2. **Flush split:** `grid-template-columns:1fr 1fr` at full width, inside a `container-type:inline-size` wrapper.
     - The photo cell touches the viewport edge (no radius).
     - The text cell pads to the container line: `padding-inline: max(var(--side), calc((100cqi - 1200px)/2))` on its outer side, and 64px on its inner side. `cqi` is used instead of `vw` so the scrollbar can't misalign it.
     - It stacks below 768px, photo first except in the hero.
  3. **4/8 list:** the title, bracket note and capsule on the left; leader rows on the right; `1px solid var(--leader)` between groups.
  4. **Tiles:** 3×3 with 10px gaps.
  5. **Stat row:** 4 squares alternating photo and bronze tile (2×2 on mobile).
  6. **Floating card:** max 912px, white, `--card-shadow`, 48px padding. The ghost word is absolutely positioned behind the card's top half.
- **Image ratios:**
  - Hero 1:1.
  - Founder and bridal portraits 3:4.
  - Team cards 3:4.
  - Stat and candid photos 1:1.
  - Tile avatars: 44px circles.
  - Brand product shots 1:1, contained on white.
- **Headshots:**
  - In bronze splits, a portrait's black meets the bronze with no frame.
  - In the team grid, 3:4 on white; corner brackets appear on hover and focus.
  - On the home tiles, 44px circles (`team/{slug}-180`, `alt=""`) overlapping by -10px with a 2px white ring (a bronze ring when the tile is inverted).
  - The credentials and bio portraits carry permanent brackets.
- **Corner brackets:** `::before` at top-right and `::after` at bottom-left: 64×64px L-shapes of 8px bronze borders, offset -14px, `z-index:-1`, decorative. At most 2 bracketed photos or groups per page.
- **Ghost word:** `<span aria-hidden="true">`, `--c-ghost`, `rgb(28 28 28/.035)` on white and `rgb(106 85 47/.08)` on sand, `user-select:none`.
- **Where future photos slot in:**
  - The hero cell takes shot 13 (front-desk welcome) or shot 11 (exterior) at 1600px or more.
  - Each service tile gains a 4:5 image on top from shots 02–09. The tile hover then darkens the image by 25% (never blurs it).
  - No-image service heads become flush splits.
  - The About panels without photos get shots 11, 12 and 13.
  - "Recent work" (shot 14 onward) becomes a 3×2 grid with 10px gutters in bracket frames.

## C5. Header, navigation, footer

**Desktop (1024px and up):**
- A sticky 76px `--bronze` bar inside the 1200px container, split into 3 cells by full-height 1px `rgb(255 255 255/.25)` rules (Yukie):
  1. The logo: `brand/logo-on-dark.png`, the framed lockup at 52px tall.
  2. The nav in 16px 400 white sentence case, with 28px gaps: **Services & prices ▾ · Meet the team · New guests · Bridal · About · Gift cards** (Gift cards is hidden below 1200px).
  3. The phone with an icon (from 1280px), then the **Book now** capsule (gold with the cream ring).
- The bar never changes height.

**Services & prices ▾ (mega panel):**
- A's disclosure behavior. The panel is full-width white under the bar, laid out as a 4/8 list.
- **Left:** "Services & prices" (30px 600), the bracket note "[Prices by level, published for nearly every service]", and the primary capsule "All services & prices".
- **Right:** two columns of leader rows: the named anchor at 18px 600, a flex-grow `--leader` hairline, then the price at 18px 400 in tnum.

  | | | |
  |---|---|---|
  | Women's cut $37–60 | Manicures $31–40 | Facials from $62 |
  | Relaxation massage $42–80 | Waxing from $10 | Brows, lashes & makeup from $20 |
  | Spray tans from $25 | Men's cut from $25 | Bridal style from $75 |

  Each row links to its service page.
- Under a rule: "Slay Aesthetics · medical aesthetics · Fridays".

**Tablet and mobile:**
- A 64px bronze bar, sticky from load, with the cells split by vertical rules. It holds:
  - logo-on-dark (36px)
  - the compact **Book** capsule (the label plus a 36px circle, 48px tall, gold with the ring)
  - **Menu** (icon plus word)
- **Menu** opens a full-screen `<dialog>` in bronze with its own bar (logo, close).
  - Links are left-aligned 20px white in 56px rows, separated by `rgb(255 255 255/.18)` rules.
  - The services list is flat, with sand named ranges (6.04). The current page sits on `--bronze-band` (white text, 5.80).
  - The dialog then continues: the Call capsule (on bronze), Gift cards, Specials, Boutique, Pick-up orders, Careers, Policies, hours and social links.
- **No bottom bar.** On short viewports (`max-height:31.25rem`) the bar stays sticky at 56px (logo 28px, Book 48px), and the jump chips go static.

**Footer (bronze):**
- Four columns plus the logo on the right (Yukie's layout, with the Visit facts it lacked):
  - **Visit:** directions, tel, the hours table with today marked, a holiday link, the bridal email.
  - **Services & prices:** 10 links plus "All".
  - **Plan your visit:** New guests, Book online, Gift cards, Specials, Boutique, Pick-up orders, app badges.
  - **About:** Our story, Team, Careers, Policies, Privacy, SMS privacy, Contact.
- Headings are 16px 600 sand; links are 16px white (7.11); rules are `rgb(255 255 255/.25)`.
- Bottom row: © and the social icons.

## C6. Home page

| # | Section (ground) | Content | Images | Conversion purpose |
|---|---|---|---|---|
| 1 | **Hero** (white, flush split, `grid-template-columns:min(44vw, 35rem) 1fr`) | Text cell:<br>• Eyebrow "Hair salon & day spa in Newark, Ohio".<br>• H1, two-tone: "Beauty & relaxation," (#555) / "tailored to you." (ink), in `--c-display`.<br>• A's lede.<br>• Capsules **Book an appointment** (gold) and **Call 740-366-1604** (primary). They stack below 600px, Book first.<br>• The text link "New to Bellezza? Start with your first visit", then the status line and the microcopy. | A flush-left 1:1 of `join/gallery-3-{400,800,900}.{avif,webp,jpg}` with `object-position:50% 0`. Add a 900w variant from the 900×1200 source; it is displayed at 560px or less.<br>• The crop shows the gold wall sign "BELLEZZA & Co · EST 2009 · SALON • SPA • BOUTIQUE" and two team members at the front desk, and leaves out the retail packaging and price card lower in the frame.<br>• Alt: "Two Bellezza team members at the front desk under the Bellezza & Co. sign" (names added once C-1 is answered).<br>• Mobile: the text first, then the photo.<br>• **If C-1 is declined:** the cell holds `team/lisa-jeffries-720` and `team/ashley-basham-720` side by side at 3:4, flush left, and section 5 swaps to the group photo. | Place, welcome and Book in one screen. The real sign proves the place. At 360×640 the Book capsule's bottom edge sits at ≤ 480px. |
| 2 | **Services intro** (white) | Intro row: "Services" · H2 "Hair, nails, skin, massage and bridal, priced by level." · A's services intro paragraph. | — | Frames the menu |
| 3 | **Service tiles** (white ground, sand tiles) | 3×3 with 10px gaps (2 columns on tablet, 1 on mobile). Each tile is one `<a>` (min-height 240px, 28px padding) containing:<br>• the `h3` category name<br>• the named range from §0 in `--c-row` bronze, plus "[by level]" where it applies<br>• an avatar stack (up to 5) with a visible bracket label naming who it shows<br>• a 34px bronze arrow circle<br>The avatars follow A's §5.3 mapping:<br>• Hair: Ashley, Lisa, Devon, Moriah, Emilie, "[12 hair stylists]".<br>• Nails: Stephanie, Paige, Madison, Shelbi, Raegan, "[8 nail artists]".<br>• Facials: Emma, Mia "[Emma, Mia]".<br>• Waxing: Mia, Emma "[Mia, Emma]".<br>• Massage: Jesyca "[Jesyca]".<br>• Brows, lashes & makeup: Emilie, Lizbeth, Cherish "[makeup: Emilie, Lizbeth, Cherish]".<br>• Bridal: Devon, Emilie, Lizbeth, Cherish "[Devon; makeup: Emilie, Lizbeth, Cherish]".<br>• Spray tans and Men's: no avatars until Q8.<br>Below the grid: the Slay line (after a rule), the boutique line, the quiz line (Q4), and the primary capsule "All services & prices". | `team/{slug}-180.{avif,webp,jpg}`, `alt=""` (the label carries the names) | Choose a category by price and by the faces who'd do it (The Lane's picker). |
| 3b | **Gifts** (gift seasons only, white) | The eGift card from #9 moves here, with the four price ideas, the primary capsule "Send an eGift card" and "Not valid at Slay Aesthetics." #9 then keeps Boutique and Pick-up orders. | — | Seasonal revenue |
| 4 | **Levels** (sand band) | The ghost word "Levels" behind the floating card, which holds:<br>• H2 "Your provider's level sets the price."<br>• A five-cell ladder: "Women's cut & finish: Jr Associate $37 · Associate $40 · Senior $48 · Expert $50 · Master $60".<br>• The line "Prices are listed on our menu for nearly every service."<br>• The primary capsule "How pricing works", linking to `new-guests.html#levels`. | Type only | Explains Bellezza's open pricing up front (Element's honest disclaimer, done better). |
| 5 | **Founders** (bronze split, photo flush right) | Eyebrow "Our story" (sand). Two-tone H2: "Lisa and Ashley bought" / "an 1,800 sq ft house in 2008." A's verified story: opened in 2009, grown to 5,500 sq ft, the boutique and the new name in 2022, and both still behind the chair one day a week. Capsule on bronze: "Read our story". | `team/lisa-jeffries-{360,540,720}` and `team/ashley-basham-{360,540,720}` side by side at 3:4 against the right viewport edge. Caption in sand: "Lisa Jeffries & Ashley Basham, owners". (If C-1 is declined: `about/team-group-1120` at 4:3 with the Q22 caption.) | Founder trust |
| 6 | **Stat row** (white) | Four 1:1 cells:<br>1. Photo.<br>2. Bronze tile: "2009" / "Opened on Deo Drive".<br>3. Photo.<br>4. Bronze tile: "5,500 sq ft" / "Grown from an 1,800 sq ft house".<br>Numerals are `--c-numeral` white; labels are 16px sand. The text is static.<br>**Without Q14 consent,** the photo cells become sand tiles reading "28" / "people on our team" and "2022" / "The boutique opens". | `join/gallery-1-800` (1:1 center crop) and `join/gallery-4-800` (1:1 top crop) | Proof with real numbers only |
| 7 | **Credentials** (sand) | Eyebrow "Training". H2 "Where our team trained". A ruled list of verified lines, each name linking to its card:<br>• Stephanie: American School of Hair Design, 2002.<br>• C-TEC: Austyn; Paige 2021; Madison 2019; Shelbi 2023; Rissa 2024.<br>• Taylor F: Salon Institute, 2023.<br>• Mya: Paul Mitchell The School Columbus.<br>• Hope: Mason Anthony's.<br>• Jesyca: Associate degree in massage therapy, Hocking College, 2015.<br>• Shannon Francis, CNP (Slay Aesthetics).<br>Then a second short list, **"Who teaches"**: Devon, Director of Education; Emilie, former cosmetology instructor (CCAD Fashion Show).<br>Primary capsule "Meet the team". | `team/stephanie-{360,540}` at 3:4 with permanent brackets. Caption: "Stephanie, Spa Manager · with Bellezza since March 2010". | Stylist credibility (E-E-A-T) |
| 8 | **Reviews** (white, Q2 gate) | 3 columns separated by rules. Quotes in `--c-row` 400. Attribution: "{First name} {Initial}. [Google · {Month YYYY} · {service}]". "Read all our Google reviews". | — | Proof |
| 9 | **Bridal** (bronze split, photo flush left) | Two-tone H2: "Bridal hair and makeup," / "in the salon or with our travel team." **Ritual steps:**<br>1. Send the inquiry form.<br>2. Our Bridal Coordinator replies by email.<br>3. Hair and makeup in the salon, or our travel team comes to you (fee applies).<br>"Devon, our Salon Manager and Master Stylist, works with our brides." Capsule on bronze: "Plan your bridal beauty". | `team/devon-{360,540}` at 3:4, flush | High-value lead |
| 10 | **Gifts & boutique** (white) | An intro row, then 3 cards with a 1px `--line` border and no shadow:<br>• **eGift:** the four price ideas; primary capsule "Send an eGift card"; "Not valid at Slay Aesthetics." (moves to 3b in gift seasons).<br>• **Boutique:** "Dermalogica, Olaplex, REF, Lakmé, Smashbox, VOESH, Calecim, ECRU New York"; "Visit the boutique".<br>• **Pick-up orders:** the process line; "Order for pickup".<br>Plus the active special, if any. | `brands/gallery/lakme-1.jpg` and `dermalogica-1.jpg` (1:1, contained on white, 180px max) on the boutique card | Revenue beyond booking |
| 11 | **Book an appointment** (sand) | The eyebrow is the live status (fallback "Book online 24/7"). Display line "Book an appointment". **Book** (gold) and **Call 740-366-1604** (primary) capsules. Microcopy. | — | Closing conversion |
| 12 | **Visit** (white) | Left: H2 "206 Deo Drive, Newark", then ruled detail rows (directions, phone, hours with today marked, a holiday link, the bridal email). Right: the map facade in a sand panel with brackets. | — (the future exterior goes in the right cell) | Local intent |
| 13 | Footer (bronze) | §C5 | | |

## C7. Inner pages

**Service page template:**
1. **Head (no-image variant):** a white band with the ghost word (the category name, e.g. "Nails") behind the floating card. The card holds:
   - the eyebrow (brand label)
   - the H1 in `--c-display`
   - a one-line value taken from the audited intro, and the range in `--c-row` bronze
   - the contextual **Book nails** capsule (gold), the text link "Send as an eGift card", and the microcopy
   
   Once shots 02–09 exist, the head becomes a flush split.
2. **Your artists:** an intro row, then 3:4 cards 4-up (2-up on mobile). Each shows the name, the level word, and bracketed specialties ("[Nail art · Nail stamping]"). Brackets appear on hover.
3. `<h2 id="prices">Menu & prices</h2>`, then the level legend as a bracket line.
   - Jump chips are 44px sand capsules (selected: bronze with white text and a check icon).
   - They are sticky under the header and use scrollspy.
4. **Price menu, 4/8:**
   - **Left:** the `.menu-group > h3` (`--c-h3`), the `p.tier-head` in brackets ("[Associate / Senior / Expert]") or "[by stylist level]", the `p.group-intro`, and a **Book nails** text link with a 28px arrow circle (not a gold capsule, so two gold capsules can never stack up in one view).
   - **Right:** each `li.price-item > .price-head` holds `span.name` (`--c-row` 600), the `.dots` element restyled as a flex-grow 1px `--leader` hairline on the baseline, then `span.price` (`--c-row` 600, tnum). The description `<p>` follows at 16px `--text`.
   - `p.note` renders as a bronze bracket line ("[Consultation required · $50 deposit]").
   - **Ladders:** each level row gets a `<div class="who">` bracket sub-label in plain text ("[Ashley, Lisa, Devon, Moriah]"), the way Yukie shows "Senior Hairstylist". The linked names live in "Your artists".
   - **Package rows** carry a `<div class="unit">` with the per-unit price, computed by `tools/build.py`: "Gel Manicure Package of 5 · $245 [$49 each]" and "Package of 3 · $90 [$30 each]". No "save" claims.
5. **Ritual block** (Yukie's head-spa layout). Left: the treatment name, description, price and Book capsule. Right: "Step 1…" rows. Used only with verified steps:
   - **Keratin:** consultation → $50 deposit → service.
   - **Bridal:** the 3 steps above.
   - **Custom signature facial:** only after the owner supplies its steps (question C-2).
6. **"How Slay Aesthetics works at Bellezza":** a two-column bronze explainer on `slay-aesthetics.html` only, using verified facts:
   - who: Shannon Francis, CNP
   - when: Fridays, 10am–6pm
   - how to book: slay-aesthetics.com (not Bellezza's Meevo)
   - gift cards: Bellezza gift cards are not accepted
7. **FAQ:** a sand accordion. The open row turns bronze with white text (Yukie).
8. The gift section (3 pages), related links, the sand "Book an appointment" band, and the footer.

- **Slay:** no gold. The primary capsule "Book with Slay Aesthetics" links to Slay's site, and the header Book follows the §0 override (an "On bronze" capsule reading "Book with Slay"). Uses `slay/shannon-{360,497}` in brackets, plus `slay-logo-240`.
- **makeup-and-eyes:** `work/brows-{before,after}-470` side by side inside one bracket frame, labeled "Before" and "After" in HTML.

**`services.html`:** the highlighter H1, the levels card, the 3×3 tiles (with descriptors), "Also at Bellezza" cards, and the Slay line.

**`specials.html`:** each active offer is a 4/8 block on sand: title and end date on the left; what's included and the price on the right. There is no struck-through "regular" price unless the owner supplies one.

**Team (`data-team-mode="jump"`):**
- **Head:** the ghost word "Team" plus the floating card (H1 "Meet the team", the lede, "How our levels work", "Team updated {Month YYYY}"). The quiz callout (Q4) sits in a sand band with a primary capsule.
- **Chips:** sand capsules that jump to department blocks, sticky under the header, with scrollspy. The blocks carry the ids `filter-hair`, `filter-nails` and so on, so every existing `our-team.html#filter-*` link still lands.
- **Owners:** Ashley's and Lisa's `li.team-item` sit in their own `<ul class="team-lead">`, rendered as one bronze flush split.
  - Both portraits at 3:4 inside their `.card`s.
  - A sibling text block: "Lisa Jeffries & Ashley Basham · Owners & Master Hair Stylists · owners since 2009 · behind the chair one day a week".
  - Their bio buttons and a Book capsule (gold with the ring).
- **Departments:** each is a 4/8 block.
  - **Left:** the `h2` "Hair", a bracket "[12 stylists · Jr Associate to Master · women's cut $37–60]", and a **Book hair** text link with its arrow circle.
  - **Right:** a 3-column grid (2-column on mobile).
  - Each card sits in the first department in its `data-dept`, and the owners stay in the lead split. Other departments list cross-listed people in a bracket line of linked names ("[Also in Hair: Ashley, Lisa]", "[Makeup: Emilie, Lizbeth, Cherish]"), so there are no duplicate cards.
- **`.card`:**
  - A 3:4 image, the `h3` name, and `span.role` in #555.
  - A bracket level line "[Senior · women's cut $48]".
  - `ul.tags` as bracket text.
  - Actions: `button.card-bio` (a text link with an arrow circle), `a[data-book]` "Book" (a text link; gold stays in the chrome), and Instagram.
- **`dialog.bio`:** a centered modal, max 880px, white; full-screen below 768px.
  - Left: a 3:4 portrait with brackets.
  - Right: the name at 30px 600, the role, the bracket level-price line, the bio, and a credential list as leader rows ("School ——— C-TEC", "With Bellezza since ——— 2021").
  - Then service links, the gold **Book** capsule, and Instagram.

**About:**
- The ghost word "2009" plus the floating card with the H1 "From an 1,800 sq ft house to Bellezza & Co."
- **The house, year by year:** Yukie's floor-by-floor tour, turned into zig-zag panels. Panels with a real photo are flush splits. Panels without one are full-width bands with the year in `--c-numeral`, never a split with an empty cell.
  - **2008** (bronze split): the house, with a sand numeral "1,800 sq ft", beside the owners' portraits.
  - **2009 and 2016** (one white band): opened as Bellezza Salon and Day Spa; voted the Number 1 spa in Licking County, and every year since (About only, per Q1).
  - **2022** (white split): the addition, the boutique and the rebrand, beside a 2×2 of `brands/gallery/{lakme-1,olaplex-1,dermalogica-1,voesh-1}`, contained on white.
  - **Today** (bronze split): 5,500 sq ft and 28 people, beside a flush `about/team-group-1120`.
- The stat row, then a candid 3×2 gallery with 10px gutters and brackets (Q14): `join/gallery-{1,2,4}-800` (gallery-2 cropped inside its vignette) and `join/join-{2,3}-800`.

**Contact:** two columns.
- **Left:** H1 "Visit us", then ruled rows (status, Call, Text if Q18, Directions, Book) and the hours table.
- **Right:** the map facade with brackets.
- Below: a sand band of upcoming holiday hours. No form.

**New guests:**
- The first visit as a ritual layout: Choose who → Book online, in the app, or by phone → Changes need 24 hours' notice. Arrival details are added after Q5 and Q19.
- Then the levels card, and A's remaining sections, each as a 4/8 block.

## C8. Interaction

- **Capsules:** fill and color swap over 180ms. The arrow circle moves `translateX(3px)` (no-preference only).
- **Tiles:** on hover and `:focus-visible`, a tile inverts to bronze with white and sand text over 200ms, and the avatar rings change color.
- **Cards:** brackets fade in over 150ms on hover and focus-within. No zoom, no blur.
- **Mega panel and dialogs:** fade over 150ms. The FAQ's open row changes background (no height animation).
- **Header:** never shrinks. Nothing moves on scroll. There is no Ken Burns, slideshow, press marquee or product carousel.
- **Focus:** a 3px ink outline at a 3px offset on white and sand; a 3px white outline at a 4px offset on bronze (so it clears the Book ring).

## C9. Anti-template guardrails (C)

1. One family (Manrope) in two weights, 400 and 600. No italics, no tracked caps. The only uppercase headline is the `services.html` highlighter.
2. One button shape (the arrow capsule, plus its small text-link form). No square buttons and no ghost pills on photos.
3. Bronze never carries ink or gold text. Book on bronze always has the cream ring.
4. Never two bronze sections in a row. Sand is always full-bleed. White is at least 50% of every page.
5. No slideshow, Ken Burns, marquee, press logos, product carousel or request-appointment form. Every Book goes straight to Meevo.
6. Stat tiles show only verified facts (2009, 1,800 sq ft, 5,500 sq ft, 28, 2022). No summed "years of expertise" and no count-up animation.
7. At most 2 ghost-word cards per page, 1 highlighter on the whole site, 3 two-tone heads per page, and 2 bracketed photo groups per page.
8. The menu has one home: the service pages. Tiles, the mega panel and `services.html` show only named ranges stamped from those pages by `tools/build.py`. Never a hand-typed second list (Yukie's four drifting copies).
9. No bolded SEO keywords in paragraphs, and no keyword-stuffed FAQ.
10. Floating-card shadows only on the ghost-word card. Every other card is flat with a 1px `--line` border.

---

# Option D · Open Door

*Led by Element Salon (Nashville)*

## D1. Concept

The wall behind Bellezza's front desk reads "BELLEZZA & Co" in gold letters on white boards (`join/gallery-3`). Open Door builds the site like that wall:
- A bright white page framed top and bottom by bands of gold.
- Crisp black type in a wide grotesk.
- The team in a cohesive black-and-white grid.

It is the friendliest and most direct of the four:
- One greeting.
- Two front doors: Book, or "New here?".
- Three intent doors below.
- Every service says who does it.

Density is medium-high and brochure-like, with centered section heads. It keeps Element's routing clarity and personality and fixes its misses:
- Book and Call are always one thumb away on mobile (a thumb bar).
- Every Book goes straight to Meevo, with no interstitial page.
- Levels and prices are explained on the site.
- Profiles show level, price and specialties.
- The new-client door is a page, not an exit-intent popup.
- No consent box is pre-checked, and there is no hidden H1.
- Recruiting is out of the primary nav.

| Signature move | Borrowed from | Where in D |
|---|---|---|
| One brand color as a frame: a top utility bar and a footer band | Element | Gold bar on desktop and tablet, a 6px gold edge on mobile, gold footer band |
| Physical echo of the brand color in the salon | Element (the yellow "e" disc) | The gold wall sign photo in Visit and on Contact |
| One script greeting, plain grotesk everywhere else | Element | The home hero only |
| Two front doors in the hero | Element | Book / "New here? Start with your first visit" |
| Three intent cards with label bars | Element | Home: Meet your stylist · Services & prices · Gifts & boutique |
| Uniform black-and-white studio headshots, leadership first | Element | Team page, service "Who does this" rows |
| Restaurant-style menu: heavy caps word between rules | Element | `services.html` and service pages |
| Specialist matrix | Element (extensions) | "Who does what", on home and `services.html` |
| Matchmaking quiz as a door | Element (Mya; Bellezza already uses Mya) | Utility bar, mega panel, team page (Q4 gate) |
| Per-level price on each person | The Lane | Bio dialog; the level key with faces |
| Reviews that name the stylist, linked to them | The Lane | Reviews (Q2) |
| Ritual steps; package per-unit rows | Yukie | "Your first visit, in three steps"; package rows |

## D2. Typography

**Files (2):**
1. `archivo-var-latin.woff2`: Archivo variable. The Latin file with both axes is about 90KB; instance it to `wght` 400–800 and `wdth` 100–125, with a target of 70KB or less. Used for everything except the greeting.
2. `allura-greeting.woff2`: Allura 400 (OFL), subset with `pyftsubset --text="Hello from Deo Drive!"` to only those glyphs (about 3–5KB). It is used once. It was chosen for its closeness to the logo's "& Co"; confirm the two side by side.

- Stacks: `Archivo, 'Archivo Fallback', 'Helvetica Neue', Arial, sans-serif` and `Allura, cursive`.
- Archivo's default figures are already near-tabular and it ships `tnum`, so prices use `tabular-nums`.

| Token | clamp() | px | Settings | Case / tracking | LH | Use |
|---|---|---|---|---|---|---|
| `--d-util` | `0.8125rem` | 13 | 600, wdth 100 | CAPS · .04em | 1 | Utility bar |
| `--d-label` | `clamp(0.875rem, 0.8542rem + 0.0926vw, 0.9375rem)` | 14–15 | 700, wdth 112 | CAPS · .06em | 1.2 | Nav, buttons, label bars, table heads |
| `--d-body` | `clamp(1.0625rem, 1.0417rem + 0.0926vw, 1.125rem)` | 17–18 | 400, wdth 100 | — | 1.65 | Body |
| `--d-lede` | `clamp(1.1875rem, 1.0833rem + 0.463vw, 1.5rem)` | 19–24 | 400, wdth 100 | — | 1.45 | Positioning line, ledes |
| `--d-h3` | `clamp(1.1875rem, 1.125rem + 0.2778vw, 1.375rem)` | 19–22 | 700, wdth 100 | — | 1.25 | `h3`, matrix rows, card names |
| `--d-cat` | `clamp(1.5rem, 1.25rem + 1.1111vw, 2.25rem)` | 24–36 | 800, **wdth 125** | CAPS · .02em | 1 | Menu category words, department heads, banners |
| `--d-h2` | `clamp(1.625rem, 1.3333rem + 1.2963vw, 2.5rem)` | 26–40 | 700, wdth 112 | Sentence case · -.01em | 1.12 | Section heads (centered) |
| `--d-h1` | `clamp(2rem, 1.5rem + 2.2222vw, 3.5rem)` | 32–56 | 800, wdth 118 | Sentence case · -.015em | 1.05 | H1 |
| `--d-script` | `clamp(2.125rem, 1.5rem + 2.7778vw, 4rem)` | 34–64 | Allura 400, `--gold-text` | — | 1 | The greeting only |
| `--d-spaced` | `0.8125rem` | 13 | 600, wdth 100 | CAPS · .3em | 1.3 | Role line in the bio ("SENIOR HAIR STYLIST") |
| Thumb bar | `1rem` | 16 | 700, wdth 100 | Sentence case | 1.2 | Thumb bar cells |

- **Width rules:** display widths (wdth 118 and above) only for caps of 3 words or fewer. `--d-label` (wdth 112) caps run to 4 words at most. Body text is always wdth 100.
- **Long `.menu-group > h3` names** are split by wrapping, never by reordering (§0):
  - `.h3-pre` is the lead-in (Archivo 400, 16px, own line, source case kept).
  - `.h3-main` is the expanded caps part.
  - `.h3-sub` is the parenthetical (Archivo 400, 16px, own line).
  - Example: `Color Services &ndash; <span class="h3-main">Root Retouch</span> <span class="h3-sub">(Maintenance Color)</span>`, with the lead-in wrapped in `.h3-pre`, renders as "Color Services –" / "ROOT RETOUCH" / "(Maintenance Color)".

## D3. Color

- **Proportion:** about 70% white, 12% fog panels, 10% ink (buttons, label bars, footer), 5–8% gold (bars and Book). Bellezza headshots are black and white outside the bio dialog.

```css
:root{
  --white:#fff; --fog:#f2f2f2;                                  /* neutral tint of ink */
  --sheen: linear-gradient(154deg,#e6e6e6 0%,#fafafa 38%,#ececec 100%); /* Element's "mirror", in greys */
  --ink:#1c1c1c; --ink-2:#262420; --d-text:#4a4a4a; --muted:#6b6b6b; --hover-grey:#c4c4c4;
  --gold:#b8985f; --gold-lt:#c9ae7c; --gold-text:#7a6232;
  --on-ink:#e7e2d9; --on-ink-muted:#a8a196;
  --dots: rgb(28 28 28 / .35);                                  /* dotted leaders, decorative */
}
```

**Home ground sequence:**
1. **gold** utility bar
2. white header
3. white hero with the team strip
4. white positioning line
5. white intent cards
6. fog proof band (Q1 or Q2)
7. **sheen** expertise split
8. white "Who does what"
9. fog quiz band (Q4)
10. white reviews (Q2)
11. white first-visit steps
12. **sheen** Visit and FAQ
13. **ink** footer
14. **gold** bottom band

At most 2 sheen panels per page.

**Buttons (square, `border-radius:0`, 52px tall, padding 16px 28px, `--d-label`, no shadows, no arrows):**

| Variant | Default | Hover | Use |
|---|---|---|---|
| **Book** | `--gold` fill, ink text (6.24) | `--gold-lt` (7.98) | Booking at Bellezza only |
| **Primary** | Ink fill, white text (17.04) | White fill, 1px ink border, ink text | Other main actions, including the Slay and gift-card chrome overrides |
| **Outline** | 1px ink border, ink text | Ink fill, white text | Secondary: Call, Directions, "New here?" |
| **On ink** | 1px white border, white text | White fill, ink text | Footer |
| **Label bar** (intent cards, matrix headers, the hero's second door) | Ink bar, white caps (17.04), subline in `--on-ink` (13.21) | `--hover-grey` bar, ink text (9.77) | Card labels |
| **Text link** | Ink, 1px underline at a 3px offset | 2px underline | Inline, and per-group "Book hair →" |

Gold is never a hover state (unlike Element's all-yellow hovers).

**Contrast-safe pairings:**

| Foreground | Background | Ratio |
|---|---|---|
| Ink | Gold bar / gold band | 6.24 |
| `--d-text` #4a4a4a | White / fog / sheen at its darkest (#e6e6e6) | 8.86 / 7.92 / 7.10 |
| `--muted` #6b6b6b | White / fog | 5.33 / 4.76 (never on sheen: 4.27) |
| Ink | White / fog / sheen | 17.04 / 15.22 / ≥ 13.65 |
| `--gold-text` (the greeting) | White | 5.80 |
| White / `--on-ink` / `--on-ink-muted` / gold | Ink | 17.04 / 13.21 / 6.66 / 6.24 |
| Ink | `--hover-grey` | 9.77 |

**Banned pairings:** gold as text on white or fog (2.73 / 2.44).

## D4. Layout system

- **Container:** 1200px (Element uses 1080). Wide rows (intent cards, the hero strip) go up to 1320px. Side padding is `clamp(1rem, 4.4444vw, 4rem)`.
- **Grid:** 12 columns, 24px gap. The team grid gap is 16px, a tight wall like Element's.
- **Spacing scale:** 4 · 8 · 12 · 16 · 24 · 32 · 48 · 64 · 88. Section padding is `clamp(2.5rem, 1.5rem + 4.4444vw, 5.5rem)` (40 to 88px), denser than A, B or C.
- **Rhythm:** stacked brochure sections, each with a centered H2 plus a one-line intro (60ch max). Body copy inside columns is left-aligned.
- **Image ratios:**
  - Team: 1:1. Leadership: 1:1, larger.
  - Hero strip: 21:9 on desktop, 4:3 on mobile.
  - Intent cards: 1:1.
  - Expertise portrait: 4:5.
  - Sign photo: 1:1, cropped from the top.
  - Product shots: 1:1, contained on white.
  - Future results tiles: 4:5.
- **Headshots:** black and white via CSS: `.bw{filter:grayscale(1) contrast(1.12)}`, with `aspect-ratio:1; object-fit:cover; object-position:50% 18%`. No new files are needed. Pre-rendered `-bw` AVIF variants from `tools/build-images.py` are an optional later saving.
  - The black backdrops stay black, so the grid reads as one studio session (Element's herringbone wall, Bellezza's black seamless).
  - Every Bellezza headshot outside the bio dialog is black and white: grids, matrix squares, the level key and the expertise split. **Color appears only when you open a person** (in `dialog.bio`).
  - Shannon's portrait on `slay-aesthetics.html` (a single-provider page) stays in color.
  - Group photos, candids, the sign photo and product shots stay in natural color.
  - Squares of 120px use the 360w file; 32–40px squares use the 180w file.
- **Graphic devices:**
  1. The gold frame: a 36px bar on top, a 48px band at the bottom, and a 6px gold rule under every inner-page banner.
  2. A heavy expanded caps word between two 1px ink rules (`display:flex; gap:24px`, with the rules at `flex:1`).
  3. Dotted leaders: `.dots{border-bottom:1px dotted var(--dots)}`.
  4. Label bars overlapping the bottom of card images by 50% of their height.
  5. ⊕ accordion icons.
  6. Gold map pins on ink (6.24).
- **Where future photos slot in:**
  - The intent-card images.
  - A "Recent work" strip of 4 consented, credited 4:5 results ("By Austyn · Senior Hair Stylist") under the expertise split. It stays out until 4 exist.
  - Menu panels get their category shot (02–09) washed out behind `rgb(255 255 255/.88)`.
  - The hero strip takes shot 01 or 11 with the same crop.
  - The expertise portrait becomes shot 02.

## D5. Header, navigation, footer

**Desktop (1024px and up):** both tiers are pinned when the viewport is at least 800px tall. Below that, only the white header is pinned.
- **Gold utility bar, 36px:**
  - Left: "206 Deo Drive, Newark" (directions).
  - Right, in `--d-util` ink: the live status · `740-366-1604` · **Find your match** (Mya, Q4) · Gift cards · Specials (if active) · Boutique · an Instagram icon.
  - Links underline on hover. The focus ring is a 2px ink outline.
- **White header, a fixed 76px box:**
  - Left: the full framed logo lockup (`brand/logo.png`, SVG later) at 56px tall.
  - Right: the nav in `--d-label` ink, **SERVICES ▾ · TEAM ▾ · NEW GUESTS · BRIDAL · ABOUT**, then the gold square **BOOK NOW** (`data-placement="header"`).
  - After 80px of scroll, the logo scales to .72 with `transform` and a 1px bottom rule fades in. The box height never changes.
- **SERVICES ▾:** A's disclosure behavior. A white full-width panel with 5 columns:
  - **HAIR / NAILS / SKIN & BODY / OCCASIONS:** heads in `--d-cat` at 18px, with a 2px ink rule. Links show their named range from §0 in `--muted`. Slay reads "Slay Aesthetics · medical aesthetics · Fridays".
  - **NOT SURE?** (the doors column): "Take the match quiz" (Q4), "New to Bellezza? Start here", and "All services & prices".
- **TEAM ▾:** Hair (12) · Nails (8) · Skin & Waxing (2) · Massage (1) · Makeup (3) · Bridal · Front desk (4), each linking to `our-team.html#filter-*`, plus "All 28".

**Tablet (768–1023px):** the gold bar (36px, status and phone only) and a 64px header (logo, Book at 48px, **Menu**) are both pinned.

**Mobile (below 768px):**
- A 6px gold top edge, then a 60px white header (the framed logo at 40px tall) that **scrolls away**.
- **Thumb bar:** sticky from load, and hidden only while a dialog is open. Three cells, 60px plus `env(safe-area-inset-bottom)`, white with a 1px `rgb(28 28 28/.12)` top border:
  - **Menu** (icon plus word, 25%)
  - **Call** (icon plus word, 25%, `tel:`). When the salon is closed it shows a second 13px line, "opens 9am".
  - **Book** (gold, 50%). The label comes from `pages.json.book_label`. Below 400px wide it uses `book_label_short` ("Book now", "Book nails", "Book a massage").
- `body{padding-bottom:calc(76px + env(safe-area-inset-bottom))}`. A's `scroll-padding-bottom` and `focusin` fallback keep focused form fields above the bar.
- Overrides as in §0: on Slay the Book cell becomes an ink "Book with Slay"; on gift cards, an ink "Buy an eGift card".
- **Menu** opens a full-screen white `<dialog>`, in this order:
  1. The two doors: Book (gold) and "New here? Start here" (outline).
  2. Services, flat, with named ranges.
  3. Team by department.
  4. New guests · Bridal · About.
  5. Gift cards · Specials · Boutique · Pick-up orders · Careers · Policies · Contact.
  6. Hours, then social links.
  
  Element buries Book 7th in its list; D puts it first.

**Footer:**
- An ink band with 4 columns:
  - **VISIT:** a gold pin plus "206 DEO DRIVE", the address, tel, the hours table with today marked, a holiday link, the bridal email, and an On-ink **GET DIRECTIONS** button.
  - **SERVICES & PRICES**
  - **PLAN YOUR VISIT** (with app badges)
  - **ABOUT** (Careers lives here)
- Headings in `--d-label` gold (6.24); links in `--on-ink`, in 44px rows on mobile.
- Then the **gold band**, 48px: round ink social icons and "© {year} Bellezza & Co. (formerly Bellezza Salon and Day Spa)" in ink. No agency credit.

## D6. Home page

| # | Section (ground) | Content | Images | Conversion purpose |
|---|---|---|---|---|
| 1 | **Hero** (white, centered) | • The greeting `<p class="greeting">Hello from Deo Drive!</p>` (`--d-script`, `--gold-text`; wording pending owner question D-1).<br>• H1 "Beauty & relaxation, tailored to you." (`--d-h1`, max 18ch).<br>• A's lede (`--d-lede`, `--d-text`, 46ch).<br>• **Two front doors** side by side (stacked below 480px): **BOOK AN APPOINTMENT** (gold, `hero`), and a two-line outline door, "NEW HERE?" in `--d-label` over "Start with your first visit" in Archivo 400 15px, linking to `new-guests.html`. No popup and no exit intent.<br>• The status line and the microcopy.<br>• Then the photo strip. | `about/team-group-{560,1120}.{avif,webp,jpg}`, **contained** (max 1120px, the source's width), 21:9 with `object-position:50% 25%` on desktop (keeps the back row's heads and the front row's hands) and 4:3 (the full frame) on mobile, in color. Figcaption: "The Bellezza & Co. team · Meet all 28" (Q22 fallback caption).<br>**If Q22 says the photo is outdated:** a 7×2 CSS grid of black-and-white 1:1 squares (`team/{slug}-180/360`) of the 14 hair and nail providers, butted together. | Returning clients book; new ones take the gentle door. The whole team appears in the first scroll. At 360×640 the hero Book's bottom edge sits at ≤ 450px, and the thumb bar is visible from load. |
| 2 | **Positioning** (white) | One centered `--d-lede` line: "Hair salon, day spa and boutique on Deo Drive since 2009." | — | Local relevance |
| 3 | **Three intent doors** (white, wide row) | Each card is one `<a>` with a 1:1 image and a label bar overlapping its bottom edge:<br>• **MEET YOUR STYLIST**: "Bios, levels and specialties for all 28", to `our-team.html`.<br>• **SERVICES & PRICES**: "Prices for nearly every service, by level", to `services.html`.<br>• **GIFTS & BOUTIQUE**: "eGift cards, Dermalogica, Olaplex & more", to `gift-cards.html`. | 1. `team/contact-sheet-800` in black and white (12 faces).<br>2. A **type-only fog panel**: "Women's cut $37–60 · Gel manicure $44–58 · Relaxation massage $42–80" in `--d-cat` at 22px, stamped.<br>3. A 2×2 of `brands/gallery/{lakme-1,olaplex-1,dermalogica-1,voesh-1}`, contained on white. | Clear doors for the three reasons people visit (Book is already the hero door and the chrome). |
| 4 | **Proof** (fog, centered; Q1 or Q2 gate) | The award H2, "Voted the Number 1 spa in Licking County every year since 2016.", with its source link, **only after Q1**. The rating line, "{rating} on Google from {count} reviews · as of {Month YYYY}", **only after Q2**. The section is omitted until at least one of them is answered. | — | Third-party trust, only when it can be sourced |
| 5 | **Expertise split** (sheen) | H2 "Blonding, lived-in color, extensions and special-occasion styling." Copy: "Our hair team of 12 runs from Jr Associate to Master, with Devon, our Salon Manager and Director of Education." Buttons: **HAIR SERVICES** (primary) and **BRIDAL** (outline). | `team/devon-{360,540}` at 4:5 in black and white, left 40% | Routes to the two big-ticket paths |
| 6 | **Who does what** (white) | Centered H2 "Who does what at Bellezza" plus "Specialties as listed on each team profile." Three cards with ink header bars. Names link to `our-team.html#slug`:<br>• **HAIR COLOR & CUTTING:** Blonding · Lived-in color & balayage · Customized color · Extensions · Fashion color · Precision cutting · Updos & special occasion · Ethnic hair.<br>• **NAILS:** Nail art · Nail stamping · Natural nail designs · Gel manicures & manicures · Pedicures.<br>• **SKIN, MASSAGE & MAKEUP:** Custom facials & dermaplaning · Facials & waxing · Relaxation massage · Makeup · Medical aesthetics, Fridays (Shannon Francis, CNP, linking to `slay-aesthetics.html`).<br>Rows read "Specialty ········ names", with names from the specialty table in §0. Each card ends with a text link: "Book hair →", "Book nails →" or "Book skin & massage →". | 32px black-and-white squares before each name (`team/{slug}-180`, `alt=""`) | Answers "who can do this?" at a glance (Element's extensions matrix, site-wide). |
| 7 | **Match quiz** (fog, Q4 gate) | A decorative row (`alt=""`) of 6 small black-and-white squares from different departments (Paige, Austyn, Emma, Jesyca, Cherish, Madison). H2 "Not sure who to book? Take the match quiz." **TAKE THE MATCH QUIZ** (primary, `data-cta="quiz"`), and "or call 740-366-1604 and our front desk will match you." No duration claims. | `team/{slug}-180` | A second new-client path |
| 8 | **Reviews** (white, Q2 gate) | 3 columns. The quote at 18px. Attribution "{First name} {Initial}. · Google · {Month YYYY}" plus "· {service}" when named. A named stylist links to their card. "A selection of our Google reviews" and "Read all our Google reviews". | — | Proof |
| 9 | **Your first visit, in three steps** (white) | Three numbered cells in an ink outline (the numbers are steps, not section numbering):<br>1. Choose your provider (team, quiz or call).<br>2. Book online 24/7, in the Bellezza app, or call 740-366-1604.<br>3. Need a change? Give 24 hours' notice.<br>A fourth step (arrival) is added after Q5 and Q19. **YOUR FIRST VISIT** (outline). | — | Lowers first-visit anxiety (Yukie's ritual, factual). |
| 10 | **Visit & FAQ** (sheen) | **Left:** the photo, then the address, status, hours table, **GET DIRECTIONS** (outline) and the map facade.<br>**Right:** an FAQ accordion (white rows, ⊕): How do I book? · What does my provider's level mean? · What is the cancellation policy? · Can I use a gift card at Slay Aesthetics? · Parking (after Q5). Answers are quoted from Policies and New guests.<br>Then a centered **BOOK AN APPOINTMENT** (gold, `band`). | `join/gallery-3-800` as a 1:1 crop from the top, in color: the gold wall sign, the physical echo of the frame. Alt as in C. If C-1 is declined, the map facade takes the photo's place. | Local intent plus objection handling, then the close |
| 11 | Footer (ink) + gold band | §D5 | | |

## D7. Inner pages

**Banner (every inner page):** an ink band (180px on desktop, 140px on mobile).
- The eyebrow is in `--d-util` gold (6.24 on ink).
- The H1 is white and centered: `--d-cat` caps when it is 3 words or fewer ("MANICURES & PEDICURES"), otherwise `--d-h1` sentence case ("Botox, fillers & weight loss", "Waxing, brows to Brazilian").
- A 6px gold rule runs under the band.
- There is no photo until shots 02–13 exist. After that, the shot sits at 30% opacity under the ink.

**`services.html`:**
- The banner "SERVICES & PRICES".
- Element's honest line in a fog panel, reworded to Bellezza facts: "Prices depend on your provider's level. Levels set the price: a women's cut is $37 with a Jr Associate and $60 with a Master. Changes need 24 hours' notice."
- A **2-column grid of fog panels**, one per group:
  - The category word between rules, with a right-aligned "BY LEVEL" or "STARTING AT" in `--d-util`.
  - Rows: the name in 700, a dotted leader, the price in 700 tnum, and a description of at most 3 lines.
  - A panel footer with "Book hair →" and "Full hair menu →".
- Slay gets its own panel with an ink header, "SLAY AESTHETICS · MEDICAL · FRIDAYS", and no gold.
- Then "Who does what" (as on home), and the closing fog band: H2 plus **BOOK AN APPOINTMENT** (gold) and **CALL** (outline).

**Service page template:**
1. Banner (H1, e.g. "MANICURES & PEDICURES", eyebrow "TIPS & TOES").
2. **Intro row** (white, left-aligned): the intro, the range line, **BOOK NAILS** (gold), "Send as an eGift card", and the microcopy.
3. **Who does this:** a row of 1:1 black-and-white squares (120px). Each shows the first name, the level word and one specialty line, and links to `our-team.html#slug` (Element's matrix, per page).
4. **Level key:** 5 (or 3) square cells with ink outlines.
   - Each cell shows the level in caps and an example price ("SENIOR · $48").
   - Under each cell, 40px black-and-white squares with the first names of the people at that level, from the §0 table. This appears once per page.
   - Then "Levels set the price." No bars or meters.
5. `<h2 id="prices">Menu & prices</h2>`, then jump links in a sticky fog bar: horizontally scrolling caps links separated by "|" (44px targets, `outline-offset:-5px`).
6. **Price menu:**
   - Each `.menu-group` is a fog panel. The `h3` is the expanded word between rules, with `.h3-pre` and `.h3-sub` per D2.
   - Rows: `li.price-item > .price-head > span.name + .dots + span.price`, then the description `<p>`.
   - `p.note` is a white chip with a 3px ink left border.
   - **Ladders:** 5 (or 4) square cells, each with the level in caps above the price. No faces under ladder cells; the level key carries them.
   - **Package rows:** `div.unit` "[$49 each]" (as in C).
   - One contextual text link, "Book this →", per group. No per-item Book links until Q3 confirms Meevo deep links.
7. The FAQ (⊕ rows); the gift section on massage, facials and spray tans (a fog panel with a primary **SEND AN eGIFT CARD**); related services as 3 mini label-bar doors without images; the closing fog band; the footer.

- **makeup-and-eyes:** `work/brows-{before,after}-470` side by side, each with a label bar ("BEFORE" / "AFTER", in HTML).
- **Slay:** `slay/shannon-{360,497}` in color (a single provider portrait, not a grid), `slay-logo-240`, and an ink primary **BOOK WITH SLAY AESTHETICS**. The header Book and the thumb bar follow the §0 override.

**Team:**
- The banner "MEET THE TEAM"; a centered intro (A's lede), "How our levels work", and "Team updated {Month YYYY}".
- **Filter row:** centered caps text buttons separated by "|" (Element's "Green Hills | Brentwood | Elliston", here by department).
  - They use `aria-pressed` and the `#filter-*` hashes, sit in a sticky white bar, and update an aria-live count.
  - Filtering hides non-matching cards in every block and hides empty blocks (§0).
  - The quiz callout (Q4) is a fog panel directly beneath.
- **Leadership first** (its own `<ul>`): Ashley and Lisa 2-up at about 420px square, then Devon, Stephanie and Janet 3-up at about 320px. Names and titles are centered.
- **Departments:** the caps word between rules ("HAIR · 12"), then a 4-up (2-up on mobile) black-and-white 1:1 grid with 16px gaps.
  - The grid lists only the people not already shown above, followed by a line "Also in hair: Ashley, Lisa, Devon (above)", so each person has exactly one card.
- **`.card`:**
  - The first name (`--d-h3`, centered) and `span.role` (14px, `--d-text`).
  - `button.card-bio` is stretched over the whole card (`::after{inset:0}`), with the visible text "Bio & booking".
  - `a[data-book]` and the Instagram link sit above the stretched area (`position:relative; z-index:1`) so each stays separately focusable.
  - `ul.tags` is visually hidden on the card (shown in the dialog) to keep the wall clean. It stays in the DOM for the filters and schema.
  - Janet, the front desk and Shannon follow A's Book rules.
- **`dialog.bio`** (Element's stylist page, fixed): 960px centered on desktop, full-screen on mobile, a fog panel.
  - **Left:** the **color** 3:4 portrait (`team/{slug}-540`).
  - **Right:**
    - the name in 32px caps (800, wdth 118) and the role line in `--d-spaced`
    - one factual hook line in 700, taken from the verified credential line ("C-TEC graduate · with Bellezza since 2021"). It is left out for people who have no credential line.
    - the bio, and the specialties as square outlined caps chips
    - "At Senior level: women's cut $48 · all-over color $75"
    - a round 44px ink Instagram button, the gold **BOOK** ("Book · ask for Austyn" until Q3), and service page links

**About:**
- The banner, with the eyebrow "OUR STORY" and the H1 "From an 1,800 sq ft house to Bellezza & Co." (sentence case, `--d-h1`).
- 40/60 splits alternating sides (Element):
  - The owners as two black-and-white squares, with the story.
  - A timeline as a horizontal 5-step row with ink dots (2008 · 2009 · 2016 · 2022 · Today).
  - `about/team-group-1120` wide, in color.
  - A 3-up candid strip in color (Q14): `join/gallery-{1,2,4}-800`, with gallery-2 cropped inside its vignette.
  - **Join our team** (Element's home recruiting split, moved here): `join/join-2-800` and `join-3-800` with an outline **SEE OPEN ROLES**.

**Contact:**
- The banner "VISIT US".
- Three columns: (1) status, Call, Text (Q18), Book; (2) the hours and holiday tables; (3) the map facade and Directions.
- Then `join/gallery-3-800` (1:1 from the top; C-1) and the FAQ accordion. No form.

**New guests:** the banner "YOUR FIRST VISIT", the three-step row, the level key with A's §5.6 examples, and the policies and FAQ as ⊕ rows.

## D8. Interaction

- **Buttons:** fill inverts over 150ms. Label bars turn `--hover-grey` with ink text over 150ms. Nothing turns gold on hover, and no image flips from black and white to color on hover.
- **Header:** the logo scales to .72 with a transform and the rule fades in (under reduced motion: no scale, rule only). The box height is constant, so there is no layout shift.
- **Dropdown panels and dialogs:** fade over 150ms.
- **Accordion:** the ⊕ rotates 45° to × over 150ms; the height does not animate.
- **Thumb bar:** it never animates in or out and does not react to scroll direction. There are no Divi-style scroll fade-ins, no video hero and no autoplay.
- **Focus:** a 3px ink outline at a 3px offset; a 3px gold outline on ink; a 2px ink outline on the gold bar; `outline-offset:-5px` inside the thumb bar and scrolling rows.

## D9. Anti-template guardrails (D)

1. The script appears exactly once on the whole site (the home greeting): 5 words or fewer, never a heading, name or price, and not Element's catchphrase.
2. Gold appears only as:
   - the utility bar, the mobile top edge and the footer band
   - 6px banner rules
   - gold text on ink (footer headings, banner eyebrows) and map pins on ink
   - Book buttons
   
   It is never a hover state, and never text on white (the greeting uses `--gold-text`).
3. No drop shadows (Element's `5px 5px 16px`), no rounded cards, and no gradients except the sheen panel (at most 2 per page).
4. The intent-card row appears once (on home). Label bars are used only on intent cards, matrix headers, the hero's second door and the before/after labels.
5. Bellezza headshots are black and white everywhere except inside `dialog.bio`. Shannon stays in color on her own page. No color-on-hover reveal and no silhouette placeholders.
6. No per-item Book links (one per group) until Meevo deep links are confirmed. Every Book goes straight to Meevo, with no `/book-now/` interstitial.
7. No popups, exit intent or pre-checked consent. "New here?" is a page.
8. Centered only for the hero, section heads (2 lines at most), banner titles and intent labels. Paragraphs longer than 2 lines are left-aligned.
9. Display widths (wdth 118 and above) only for caps of 3 words or fewer; `--d-label` caps up to 4 words; never a sentence in caps.
10. Recruiting stays out of the primary nav and the home body (About and footer only). No "Look Book" link that just opens Instagram.
11. Matrix names come only from profile tags and titles. No "specialist" or "expert in" claims beyond them.
12. No hidden or 2px SEO H1, no location-stuffed FAQ, and no placeholder phone numbers.

---

## Owner questions these directions add

These come on top of A's §10.4. The existing questions that gate content in B, C and D are Q1, Q2, Q3, Q4, Q5, Q8, Q11, Q14, Q18, Q19, Q22 and Q23.

- **B-1:** Approve Lisa and Ashley as the two tall hero frames. Approve a new shot of the white board wall in window light, to replace the CSS plaster ground.
- **C-1:** The names of the two people in `join/gallery-3.jpg`, and their permission for the photo to be used as the home hero (C) and in Visit and on Contact (D).
  - *Fallback if declined:* C's hero uses the owners' two portraits, and D uses the map facade.
- **C-2:** The actual steps of the custom signature facial, for the ritual layout.
  - *Fallback:* facials get no ritual block.
- **D-1:** Approve the greeting wording ("Hello from Deo Drive!") or supply another of 5 words or fewer.
- **D-2:** Approve black-and-white conversion of the headshots outside the bio dialog (color stays in bios). Confirm that the profile tags are current specialties before the "Who does what" matrix ships.

---

## Changes made

- **§0:**
  - Added the chrome-Book overrides for Slay and gift cards. The sticky gold Book would otherwise have broken "no gold on Slay".
  - Ranges now always name their anchor service ("Hair $37–60" and "Nails $31–40" were misleading).
  - "Separate practice" is removed from the Slay wording until Q11.
  - `h3` text must stay byte-identical (D's "ROOT RETOUCH" example reordered it).
  - Extra price-item elements are fixed as `div.who` and `div.unit`.
  - Added the one-card-per-person and jump-mode team rules.
  - The banned-photo list now includes the stock spray-tan model and the decor graphics.
  - Added crop rules for `gallery-3` (retail packaging and a "$70" card lower in the frame) and `gallery-2` (baked vignette), plus product-shot handling (REF's grey ground, `dermalogica-1`'s 289px width).
  - Added a 48px coarse-pointer hit area for every chrome Book, and the underline via `transform`.
  - The specialty table gains Moriah (customized color) and Stephanie and Shelbi (gel and manicures). Added the 4-cell men's ladder rule.
- **B:**
  - Umber changed to the taupe #504a40 / #39352e (re-verified ratios) so B's chrome no longer reads as C's bronze.
  - Fixed the fixed-ground stacking (ground on `html`) and added `100lvh`.
  - Mobile and tablet strip are 60px with a 48px Book (was 44px, under the 48px rule).
  - Hero pills stack below 420px.
  - Arsenal numeral rule clarified; department heads lose Arsenal counts.
  - `--b-title` is now sentence case, and split titles stack on mobile.
  - "How levels set the price" (5 words) becomes "How pricing works".
  - Price grid gets row hairlines. Ladders get a mobile table. The "who" list moves to one row under the legend instead of repeating under every ladder.
  - Bento drops `join-2`. Concept wording fixed ("began in 2008").
- **C:**
  - Added a hero fallback if C-1 is declined, plus an asymmetric hero split, a 900w variant and a 560px cap.
  - Compact Book raised to 48px, and the header stays sticky on short viewports (Book was lost there before).
  - Tile avatars get visible labels. The brows tile names only the makeup artists.
  - Per-group and per-department Book become text links (they risked two gold capsules in one view).
  - Credentials split into "trained" and "who teaches".
  - The highlighter is a `span`, not `<mark>`. Owners get their own `ul`.
  - About panels without photos become numeral bands.
  - 3b reference corrected. Added a Q14 fallback for the stat row. Specials added. The Slay explainer is retitled.
- **D:**
  - Both desktop tiers pinned only at 800px tall or more.
  - The "New here?" door becomes a two-line label bar (the caps rule was broken).
  - Hero crop fixed to 50% 25%. The Q22 fallback is no longer A's contact sheet.
  - Intent sublines made accurate. REF removed from the product grid.
  - The award waits strictly for Q1.
  - The Devon "leads" claim is removed. The Visit sign photo is a 1:1 top crop.
  - Thumb bar gets short labels, a two-line closed Call, and body padding and focus clearance.
  - Banner caps rule by word count.
  - Ladder faces move to the level key.
  - Leadership is no longer duplicated in the department grids.
  - Black-and-white headshot rule unified. Gold list includes gold text on ink.
  - About strip drops the repeated sign photo.