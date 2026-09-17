# Local search rollout — September 16, 2026

## Scope

164 pages are eligible for indexing: the existing 22 main pages plus 142 primary local guides at `/junk-removal/{location}/`. The 994 specialist service/location pages remain `noindex,follow`, along with the five utility/coming-soon pages. Eligibility is not a claim of Google indexing or ranking.

Primary guides include all 11 offered service categories, the existing load-price bands, booking links carrying the selected city, preparation guidance, nearby service locations, and official public disposal resources. No local offices, reviews, job histories, travel times, or same-day availability have been invented. Much of the business guidance is intentionally shared; this rollout does not claim 142 independently researched local case studies.

`site-tools/content/local-guides.json` records public-resource links and the editorial review date. County resources are referrals, not a promise that a specific customer or commercial hauler is eligible. Local collection details are included for Baldwin Park, Pasadena, and LA City areas with a link to the relevant official program. Other communities are told to check their own collection provider, without invented free-pickup allowances.

The existing regional directories link to the primary guides. Canonical URLs are self-referencing. The narrower service pages remain accessible for customers who want more detail, but are excluded from sitemaps.

## Sitemaps

- `/sitemap.xml`: the existing submitted index, now containing three child sitemaps.
- `/sitemap-pages.xml`: main non-service pages.
- `/sitemap-services.xml`: 11 parent service pages.
- `/sitemap-locations.xml`: 142 primary local guides, with the actual content-review date as lastmod.

Only advance lastmod after meaningful content changes. Do not stamp every build with today's date. Resubmit the existing sitemap index in Search Console after production verification. Google controls crawling, indexing and rankings; do not report discovery as indexing.

## Validation

`python3 site-tools/build.py && python3 site-tools/audit.py` checks all generated routes, internal links, anchors, metadata, canonical URLs, schema, assets and sitemap parity. It also requires one primary indexed guide per location, all guide sections, a public resource, and local booking context, while keeping specialist copies excluded.

Browser verification checks desktop/mobile presentation and confirms city carryover without preselecting estimate answers. Existing pricing regression tests must still pass. No booking or customer notification needs to be sent for this rollout.

## Ongoing improvements

Use Search Console impressions and enquiries to identify useful pages to expand. Add authentic completed-job photos, customer-approved examples, and verified address-specific pickup information when available. Do not create artificial uniqueness through city-name substitutions, made-up neighbourhood claims or synonym swapping. Review public-program links periodically.

Official guidance: https://developers.google.com/search/docs/essentials/spam-policies and https://developers.google.com/search/docs/crawling-indexing/ask-google-to-recrawl.
