# Bellezza & Co. — static rebuild

Static (no-WordPress) rebuild of bellezzaspaonline.com. No build step: open `index.html` in a browser
(or run `python -m http.server` in this folder and open http://localhost:8000 so the map embed loads).

Every page loads exactly two assets: `assets/css/styles.css` and `assets/js/site.js`.
`site.js` injects the shared top bar, header/nav and footer into the `#site-topbar`,
`#site-header` and `#site-footer` placeholders, so nav/footer edits happen in one place.
New interior pages start from `PAGE-TEMPLATE.html`.

## Pages

| Group      | Files |
|------------|-------|
| Home       | `index.html` |
| Services   | `brides` `salon` `tips-and-toes` `massages` `makeup-and-eyes` `facials` `hair-removal` `spray-tans` `mens-care` `slay-aesthetics` |
| Booking    | `specials` `book-online` `gift-cards` `pick-up-orders` |
| Products   | `products` + `products-{dermalogica,ref,lakme,voesh,olaplex,smashbox,calecim,ecru-new-york}` |
| About      | `our-team` (bios open in a pop-up) `join-our-team` `jobs` (application form) `contact-us` `policies` |
| Other      | `404.html` `sitemap.xml` `robots.txt` `_redirects` |

Content and prices were copied from the live site on 2026-09-29.

## Structured data (SEO)

Each page's `<head>` has a JSON-LD block that tells Google what the page is about: the business
profile (hours, address, map coordinates, phone, booking link), every service with its price,
all staff, and each job opening (for Google Jobs). It is **generated from the page content**. After
editing prices, staff or job listings, rerun:

```
python tools/build-schema.py
```

Never edit between the `<!-- schema:start -->` / `<!-- schema:end -->` markers by hand; the next run
overwrites it. When a job listing changes, update `JOBS_DATE_POSTED` at the top of the script.
Once the site is live, check pages with Google's Rich Results Test: https://search.google.com/test/rich-results

## What replaced each WordPress part

| WordPress                      | Here                                  |
|--------------------------------|---------------------------------------|
| Aviana theme + Visual Composer | hand-written HTML + styles.css        |
| Revolution Slider              | 2-slide CSS/JS fader in site.js       |
| WP Google Maps plugin          | keyless Google Maps iframe embed      |
| Contact Form 7 (broken)        | Formspree / Netlify Forms / Basin     |
| WooCommerce (unused)           | removed                               |
| Team member pages (28)         | bio pop-ups on `our-team.html`        |
| Portfolio items (products)     | `products-*.html`                     |
| jQuery + ~40 plugins           | ~150 lines of vanilla JS              |

## External services (keep linking to)

- Booking (Meevo): https://login.meevo.com/bellezza/ob?locationId=103245
- Gift cards (Meevo eGift): https://na0.meevo.com/EgiftApp/home?tenantId=100947
- Ratings (Meevo Five Star): https://na0.meevo.com/FiveStarRatingApp/five-star-rating?t=100947&l=103245
- Matchmaking quiz (Mya): https://app.joinmya.com/bellezza
- Promo video (Google Drive — move to YouTube or self-host MP4): https://drive.google.com/file/d/1JCgblUKUQaMK7inTu6HOUOTIZq1pUTcr/view
- iOS app: https://apps.apple.com/us/app/bellezza-salon-day-spa/id1314312155
- Android app: https://play.google.com/store/apps/details?id=com.webappclouds.bellezzaspa
- Slay Aesthetics: https://www.slay-aesthetics.com
- Facebook: https://www.facebook.com/BellezzaSpaOnline — Instagram: https://instagram.com/bellezza_newark
- Phone 740-366-1604 · Bridal dsabo@bellezzaspaonline.com · 206 Deo Drive, Newark, Ohio 43055

## Redirects

`_redirects` maps every old WordPress URL (`/salon/`, `/cancellation-policy/`, `/portfolio-item/*`,
`/team-member/*`, `/jobs/`, the two aftercare PDFs, …) to its new page. It works as-is on Netlify and
Cloudflare Pages; on any other host, recreate the same rules in its redirect settings.
Configure the host to serve `404.html` for missing pages.

## To do

- [ ] **Forms** — replace `https://formspree.io/f/REPLACE-ME` in three places:
      `assets/js/site.js` (footer contact), `pick-up-orders.html`, `jobs.html`.
      The jobs form has a resume upload; that needs a provider that accepts files.
- [ ] **Bridal form** — the "Bridal Party Info" button on `brides.html` currently jumps to the price list; point it at a real form.
- [ ] **Specials** — `specials.html` shows 4 images in `assets/img/specials/`; swap them as offers change.
- [ ] **og-image.jpg** — add a 1200×630 share image at `assets/img/og-image.jpg` (referenced by `index.html`).
- [ ] **Google Maps key** — rotate/restrict the key exposed on the old WordPress site.
- [ ] **Promo video** — move off Google Drive (YouTube or self-hosted MP4).
- [ ] Six staff have no bio on the live site (Kat, Shannon, Melissa, Aubree, Grace, Aeriannah); their cards show photo and title only.
