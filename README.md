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
still gate launch content (award source, Google reviews, Slay details, open jobs,
staff photo permission, form privacy, vector logo, review flow), each with the
fallback currently in place.
