# Bryan Junks It Away

A mobile-first, one-page HTML/CSS/JavaScript site. No build, packages, tracking, external fonts, paid assets, backend, or form service. Open `index.html` to preview.

## Before publishing

1. Contact is configured for **626-346-6254** and **bryanjunksitaway@gmail.com**. Test the text/email links on your phone. No message is sent automatically; customers attach photos in their messaging app.
2. Tire removal is currently unavailable and has been removed from the site.
3. The supplied first mascot/logo and all eight job photos are included. Bryan confirmed the truck photos are junk-side jobs. Originals on the Desktop are unchanged.

## Free deployment: Cloudflare Pages

The files are portable to GitHub Pages and Vercel, but their free hosting policies are not a good fit for this commercial site. Vercel Hobby is non-commercial; GitHub Pages restricts online-business/commercial-transaction sites. Keep the $0 requirement with a static Cloudflare Pages upload instead.

1. Sign in to a free Cloudflare account. Open **Workers & Pages**.
2. Choose **Create application → Pages → Use direct upload** (wording may vary).
3. Name the project `bryan-junks-it-away` or another available name.
4. Upload this folder's site contents, with `index.html` at the upload root. Include `styles.css`, `config.js`, `script.js`, and `assets/`. The README need not be uploaded.
5. Deploy and use the supplied `pages.dev` address. Do not buy a domain or enable paid features. No build command or server is needed.
6. For updates, edit your local files and upload a new production deployment in the same project.

Official guide: https://developers.cloudflare.com/pages/get-started/direct-upload/
Free limits: https://developers.cloudflare.com/pages/platform/limits/

## GitHub Pages / Vercel compatibility

All asset paths are relative, so project subdirectories work. No special routing is required.

- GitHub Pages (only where your use complies with its policy): put files in a public repository root; Settings → Pages → Deploy from a branch → main → / (root) → Save. `.nojekyll` is included. Guide: https://docs.github.com/en/pages/quickstart . Business-use restrictions: https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits . This is not the recommended public business host.
- Vercel: import as framework “Other”, no build command, output directory `.`. Technically compatible, but do not deploy this business site on Hobby or upgrade to a paid plan under the $0 requirement. Policy: https://vercel.com/docs/plans/hobby .

## Editing

- Text, pricing, sections and image captions: `index.html`.
- Colors, spacing and responsive layout: `styles.css`.
- Contact destinations: `config.js`.
- Quote-message preparation and copy fallback: `script.js`.
- Photos: `assets/`. Keep filenames or update HTML references and descriptive alt text.

There is no payment, booking confirmation, data storage, or automatic quote calculation. Quote details remain in the page until visitors choose to copy or send them through their own app. Nothing has been published as part of this download.
