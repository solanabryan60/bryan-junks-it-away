# Bryan Junks It Away

Static HTML/CSS/JavaScript website published through GitHub → Vercel. Business phone: **626-386-5623**. Email: **bryanjunksitaway@gmail.com**. One service-area business based in Baldwin Park; no public residential address.

## Build and audit

```sh
python3 site-tools/build.py
python3 site-tools/audit.py
```

Python 3.9+ standard library only. Generated output is in `public/`, ignored by Git. Vercel runs the build and serves that directory. Do not publish the repository root.

Root HTML files remain the source for the homepage and functional pages. The build adds shared navigation, footer, metadata, and homepage/pricing enhancements. Regional and service pages use shared templates in `site-tools/build.py`. `expansion.css` extends the original `styles.css` design.

## Content sources

- `site-tools/content/services.json`: eight core services and three previously advertised services; copy, proposed starting prices, related services, and FAQs.
- `site-tools/content/regions.json`: exact owner-supplied service groupings, not claims about administrative boundaries.
- `site-tools/content/locations.json`: 142 normalized locations, region membership, geographic references, and nearby links. GeoNames postal centroids and linked geographic references are approximate, imply no travel time, and are not business-office coordinates.
- `pricing.js`: existing estimator source of truth. The load table is generated from its bands. Review service starting-price copy alongside any calculator price changes.

## Indexing policy

All 1,159 public pages allow indexing, including 1,136 service/location routes, at the owner's request. Five functional/account/coming-soon pages remain noindexed. Indexing is eligibility, not a promise of search placement. Shared service guidance is intentionally reused without invented local reviews, jobs, offices, or facts.

The `/junk-removal-questions/` guide provides direct customer answers, linked sitewide. Business identity uses the verified Google Maps CID, confirmed 24/7 hours, and consistent WebSite/WebPage/Service relationships. Keep schema aligned with visible copy. The robots wildcard allows search crawlers; no special AI file or FAQ rich-result promise is required. Update `CONTENT_REVIEWED` only after substantive content review, not on every build.

`site-tools/manifest.json` and `site-tools/audit-results.json` record decisions/results. Submit `https://www.bryanjunksitaway.com/sitemap.xml` to Search Console. Only indexable routes enter the sitemap.

## Functional systems

- `pricing.js`, `script.js`: questionnaire and estimate carryover.
- `booking.js`: availability, review/edit, attachments, submission, confirmation.
- `account.js`: account and rewards client.
- `supabase/`: existing backend source/migrations. The static build does not alter backend functions.
- Google Apps Script receives backend notifications. Keep its shared secret exclusively in server settings, never in version control.

## Browser checks

`tests/expansion-browser.cjs` uses Playwright with Chrome. Set `PLAYWRIGHT_MODULE` to your installed module path. It tests representative mobile/desktop pages and both navigation paths, then exercises estimates and review/confirmation with booking POST mocked. It creates no real reservation. `LIVE=1` verifies deployed content; submission stays mocked.

## Deployment

`vercel.json` preserves existing `.html` URLs and uses trailing slashes for new nested routes. Homepage and new directory `index.html` aliases redirect to canonical routes. Canonical domain: `https://www.bryanjunksitaway.com`. Booking query parameters are preserved, but canonical tags exclude them.

After pushing, verify production build completion and test live routes, redirects, sitemap, robots, and availability. Test real account authentication and notification delivery separately when their code or settings change.
