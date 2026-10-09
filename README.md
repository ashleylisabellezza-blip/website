# Bellezza & Co. — website

Static site for bellezzaspaonline.com: plain HTML, one stylesheet, two small
scripts, no framework and no npm. Built for Netlify.

- **Design spec:** [docs/REDESIGN-BRIEF.md](docs/REDESIGN-BRIEF.md) (the why: principles,
  tokens, components, page blueprints, SEO/E-E-A-T, accessibility and performance rules,
  and the list of owner questions).
- **How to write or edit a page:** [docs/PAGE-GUIDE.md](docs/PAGE-GUIDE.md).

## Everyday editing

1. Edit a page's content (between `<main>` and `</main>`), or the business facts in
   `tools/site.json` (hours, holidays, specials, phone, links), or titles and
   descriptions in `tools/pages.json`.
2. Run the build from the project root:
   ```
   python tools/build.py
   ```
   It stamps the shared header, menu, footer and booking bar into every page,
   fills live prices and team counts from the pages themselves, writes the
   structured data (JSON-LD) and `sitemap.xml`, then runs the launch checks.
   Running it twice changes nothing.
3. Commit and push. Netlify runs the same build on every deploy and refuses to
   publish if `tools/check.py` finds a problem.

Never edit between `<!-- partial:… -->` or `<!-- schema:… -->` markers — the build
overwrites them. Owner notes in pages look like `<!-- OWNER: … -->`.

## Tools

| Command | What it does |
|---|---|
| `python tools/build.py` | Build everything and run the checks |
| `python tools/build.py --images` | Also regenerate images (needs Pillow) |
| `python tools/check.py --owner-report` | List photo slots and unanswered owner questions |
| `python tools/build-images.py` | Portraits, contact sheets, logos, OG image (AVIF/WebP/JPEG) |
| `python tools/build-fonts.py --print-css` | Rebuild the self-hosted fonts and print their CSS |
| `python tools/test_schema.py` | Tests for the structured-data generator |

View any page with `?photos=1` (or on localhost) to see the hidden photo slots,
each labelled with the shot it needs.

## Deploying (Netlify)

- Connect the GitHub repo; `netlify.toml` sets the build command and publishes the root.
- Keep **Pretty URLs off** (the `.html` URLs are canonical).
- Turn on **form detection**; set notification emails for the `bridal-inquiry`,
  `careers` and `pick-up-order` forms, then test-submit each one.
- `_redirects` maps every old WordPress URL to its new page and hides `tools/` and `docs/`.
- `_headers` sets long-lived caching for CSS, JS and fonts (they carry content hashes).

## External services

- Booking (Meevo): https://login.meevo.com/bellezza/ob?locationId=103245
- eGift cards: https://na0.meevo.com/EgiftApp/home?tenantId=100947
- Matchmaking quiz (Mya): https://app.joinmya.com/bellezza
- Slay Aesthetics: https://www.slay-aesthetics.com
- iOS / Android apps, Facebook and Instagram: see `tools/site.json`

## Before launch

Run `python tools/check.py --owner-report`. It lists the owner questions that
still gate launch content, each with the fallback currently in place. The owners'
completed answers (docs/"What We Need From You", 2026-10-05) are in the pages and in
`tools/site.json`. Still open after that round:

- Staff photo releases: still missing on 2026-10-06 for Janet, Austyn, Liv, Lizbeth,
  Mya, Madison, Shelbi, Raegan, Emma, Melissa and Grace (all portraits are the new
  2026-10-07 studio set except Grace's). Also a new current-team group photo.
- **Home page photos (owners' design, 2026-10-08).** HP-01 (hero), HP-02 and HP-07
  (styling stations), HP-03 (facial room) and HP-12 (exterior, also in the footer on
  every page) are AI-edited versions supplied by the owners. HP-01 and HP-12 show
  "Est. 2016" signage (Bellezza opened in 2009). Replace each `assets/img/home/hp*.jpg`
  with the original photo and run `python tools/build-images.py --only home`. Still
  to come: HP-04 nails, HP-05 massage, HP-06 Slay (tiles use stand-ins). HP-09 bridal
  and HP-10 gift card use the owners' 480px previews from their design doc (soft on
  sharp screens; the gift card also shows "Est. 2016") until full-size photos arrive.
- The vector logo (`New logo 3.pdf`) and the owners' signature images are not in the
  repo yet. (The 2026 award artwork and the PNG logos arrived 2026-10-08:
  `assets/img/brand/*-src.png`.)
- Written confirmation of Meevo's rating flow (the site links straight to Google).
- Domain registrar / DNS access for bellezzaspaonline.com.
- The rest of the owners' 2026-10-06 answers ("What We Still Need - UPDATED"): Kat's and
  Hope's license numbers, hair level names (Jr Hair Stylist, Associate, Senior,
  Expert, Master), Instagram links, removing pick-up orders, Anna M.'s review date
  ("Updated September 2026"), and the results-claims trims. Barbara G.'s and
  Stephanie L.'s reviews are published.
- Netlify form notifications: careers and bridal to Lisa (ljeffries@bellezzaspaonline.com),
  with a bridal auto-reply saying Devon replies within 2 business days.

Google reviews shown on the site come from `tools/site.json` "reviews": set a quote's
`publish` to true once its reviewer has given permission, then run the build.

## Archived design options

The owners chose Option A (this branch) on 2026-10-05. Options B, C and D are kept on
their branches (`design-b`, `design-c`, `design-d`) and fixed by the tags
`archive/option-b-house-light`, `archive/option-c-bronze-sand` and
`archive/option-d-open-door`. Restore one with `git checkout <tag>`. They predate the
owners' 2026-10-05 answers, so they would need the same content updates.
