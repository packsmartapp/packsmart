# PackSmart (packsmartapp.com)

Travel-prep site for a **global** audience (since 10 Nov 2026; India-specific guides are one segment, not the brand). It earns from affiliate links, not from users: free packing guides, visa and cost info, itineraries, plus offline "Pocket Guides" for airports and stations in Japan. No sign-up, no newsletter, no accounts.

Owner: Ari (solo; reviews and pushes everything). The repo is **public**: never commit secrets, earnings, partner negotiations or strategy notes.

## Start of every session
1. Read `PROJECT_CONTEXT.md` (private, gitignored, on Ari's Mac): account IDs, history, open to-dos. If missing, ask.
2. Dated decision and fix notes (`AFFILIATE_CURRENT_STATE_15NOV2026.md`, `POCKET_REVIEW_FIXES_21NOV2026.md`, etc.) live in the Claude Project "Packsmart", not in the repo.
3. `BLOG_STYLE_GUIDE.md` is the article template (head order, CSS, nav, footer, blocks). Its Localrent, Yesim-broken and newsletter sections are OUTDATED; where it conflicts with this file, this file wins.
4. Unexplained scripts at the root (`add-ga4*.sh`, `add-schema.sh`): ask Ari before running.

## Tech stack
- Static HTML, CSS and vanilla JS. **No framework, no build step.** Edit the file, push, done.
- Hosting: Vercel (team packsmartapps-projects, project `packsmart`), auto-deploys from `main`. `vercel.json`: `cleanUrls`, no trailing slash, 301 redirects.
- `api/*.js`: Vercel serverless (Node, ESM). `generate-plan` (Gemini), `weather` (OpenWeather), `share-plan`, `subscribe` (unused since newsletter removal). Keys are Vercel env vars.
- `tools/`: Python 3 scripts that generate and patch pages (see "Generator scripts").
- Analytics: GA4 `G-0C4Z7VVGPE`. Affiliates via Travelpayouts (marker `711400`, TRS `508747`; its verification script sits in every `<head>`).
- Fonts and colours: DM Sans; `--primary #00C9A7`, `--accent #E94560`, `--dark #0f0f23`. Never the purple `#667eea` or system font stacks.

## Folder structure
- `public/`: everything deployed. Top-level pages (index, blog, flights, about, pricing, legal), `<key>-pocket.html` + `<key>-sw.js` + `<key>-pocket.webmanifest` per Pocket Guide, `images/`, `web-stories/`, `sitemap.xml`.
- `public/blog/`: ~68 articles: `<country>-travel-packing-guide`, `...-from-india` variants, itineraries, lists, and the Japan airport and station guides.
- `tools/`: numbered scripts `wNN_*.py` and `pocket_guides.json` (guide registry). **Never put scripts or registries under `public/`** (they would be served).
- `api/`: serverless functions. Gitignored and private: `PROJECT_CONTEXT.md`, `backlink-outreach/`, `pinterest-pins/`.

## Pocket Guides (Tokyo, Narita, Haneda, Kansai/KIX, Kyoto, Osaka)
Call them "Pocket Guides", never "app". Each is one self-contained HTML file: flex-column shell, `.panels` scroll area, bottom `.tabs`, `.sheet` info sheets via `openInfo(icon,title,html,btn)`.
- **Offline:** per-guide service worker, cache `<key>-pocket-v7`, network-first with cache fallback. Facts refresh when online; saved copy still works in a tunnel or at immigration.
- **Install wording matters:** on iPhone the home-screen icon keeps its own copy. Tell people to add to Home Screen first, open from the icon while online, and wait for "Ready offline ✓".
- Header shows "Saved on this phone: date" (localStorage `pgSavedOn`, per home-screen copy) next to "checked <date>". The two dates mean different things.
- Facts come from official sources (airport and operator sites), written as "checked 21 November 2026" with a link. Narita and Haneda have an "I'm connecting" sheet that follows the airports' own transit pages.
- Floating bottom-right "Share this" WhatsApp pill (`id="waShare"`).
- **GA4 events** via `pgTrack(name, params)`: `pg_open`, `pg_share` (`via`), `pg_connect` (`from`), `pg_xguide_tap`, `pg_partner`, `pg_install_view`. `via` and `from` are not registered as custom dimensions.
- **`?src=` codes** (sanitised to `[a-z0-9_-]`, 40 chars): `bar box share wa hub qr card pk_<guide>`. Future channels: `yt-<creator>`, `agent-<name>`, `wa-<name>`.
- Test on a phone-width viewport (390px and 360px). Ari tests on iPads (no iPhone), so say what was and was not tested on a real device.

## Generator scripts (`tools/wNN_*.py`)
Most Japan pages, the Pocket Guides and affiliate blocks are produced by scripts, not hand-edited. **Regenerating a page wipes edits made by later post-processors**, so a fix goes into the script that owns it, then re-run the chain.
- Order: page generators (w36, w38, w39, w41, w42, w35, w25, w31, w32) → `w53` (city pickups and cars) → `w54` (airport review fixes) → pocket chain `w44`–`w49` → `w55` (WhatsApp) → `w56` (reviewer fixes, always last).
- Post-processors must be **idempotent** (check a marker string) and use asserting substitution helpers, so a changed page fails loudly instead of silently half-patching.
- Each script's docstring says what it does and when to run it. Read it before re-running. New guide = add it to `tools/pocket_guides.json`, then re-run w46–w48.

## Conventions
- New article: copy the structure of `public/blog/portugal-travel-packing-guide.html`; add a card to `public/blog.html` and a URL to `sitemap.xml`. Titles `{Country} Travel & Packing Guide 2026: Complete Checklist | PackSmart Blog`.
- **Neutral by default:** no India framing outside pages designed for India. Use "from India" titles only on the India-segment guides.
- Only bump "Last updated" after a real fact check of that page. Date bumps without content changes are not allowed.
- Verify every Unsplash ID returns HTTP 200 before committing. Photos on Japan pages are Ari's own or licensed, with a credit line and no identifiable people. Never scrape Klook photos; never download photos of public figures.
- Body copy carries no prices and no partner names (they go stale; the blocks carry them). Claim only what the provider itself states.
- Hedge visa and entry rules ("check current rules") and link the official page for fees.
- Mobile first: check pages at 390px for overflow before calling a change done.

## Article template quick reference
Full CSS, nav, footer, share row, FAQ and closing script are in `BLOG_STYLE_GUIDE.md`; match them exactly.

```css
:root { --primary:#00C9A7; --accent:#E94560; --dark:#0f0f23; --light-gray:#f5f5f5; --text:#333; }
font-family: 'DM Sans', sans-serif;   /* NEVER #667eea purple or -apple-system stacks */
```
Table header bg is `--primary`, not `--dark`. CTA box is a green gradient with a red button, not navy.

`<head>` order: charset, viewport, title, description (160 max), keywords, canonical, OG tags, Twitter tags, `article:author` + `article:section` (Pinterest), Google Fonts (DM Sans 400/500/700), GA4 script, Travelpayouts verification script, Article JSON-LD (`"@name"` for author/publisher), BreadcrumbList JSON-LD, `<style>`, FAQPage JSON-LD last before `</head>`. `og:image` and `twitter:image` are always `https://www.packsmartapp.com/og-default.png`, never an Unsplash URL.

Body order: `.content` opens, affiliate disclosure, share row, sections (visa, best time, packing, cities, budget, apps), inline images, internal link callouts, share row again, FAQ (`<details>/<summary>`), CTA box, `.content` closes, car rental block, related posts, Travel Essentials grid, SafetyWing widget, footer, nav JS, GA4 placement script. No newsletter CTA.

Hero (update the date on every new article; Last updated only after a fact check):
```html
<div class="hero-blog" style="background: linear-gradient(rgba(15,15,35,0.7), rgba(26,26,62,0.7)), url('{HERO_IMAGE_URL}'); background-size: cover; background-position: center;">
    <h1>{Article Title}</h1>
    <div class="meta">{Date} · {Read Time}</div>
    <div class="meta">Destination Guide</div>
    <div class="meta">Last updated: {Month Year}</div>
</div>
```
Internal link callout:
```html
<p style="background:#f0faf7;border-left:3px solid #00C9A7;padding:12px 16px;border-radius:0 8px 8px 0;font-size:0.92rem;margin:20px 0;"><a href="/flights.html" style="color:#00C9A7;text-decoration:underline;">Compare flight prices</a> to {Country}.</p>
```
Inline image (verify the Unsplash ID returns HTTP 200 first):
```html
<figure style="margin:28px 0;text-align:center;">
    <img src="https://images.unsplash.com/{PHOTO_ID}?w=800&h=450&fit=crop&auto=format&q=75" alt="{descriptive alt}" style="width:100%;border-radius:12px;object-fit:cover;" loading="lazy">
    <figcaption style="font-size:0.82rem;color:#999;margin-top:8px;font-style:italic;">{Caption text}</figcaption>
</figure>
```
Card for `public/blog.html` (`&amp;` and `&mdash;` as entities):
```html
<a href="/blog/{filename}.html" class="blog-card">
    <img class="blog-card-img" src="https://images.unsplash.com/{PHOTO_ID}?w=800&h=400&fit=crop&auto=format&q=75" alt="{Title}" loading="lazy">
    <div class="blog-card-body">
        <span class="tag">Destination Guide</span>
        <h2>{Title}</h2>
        <p>{Short description}</p>
        <span class="meta">{Date} &middot; {Read Time}</span>
        <br><span class="read-more">Read more &rarr;</span>
    </div>
</a>
```

## Affiliate rules (details: `AFFILIATE_CURRENT_STATE_15NOV2026.md` in the Project)
- Every partner link is a Travelpayouts tracked link with a Sub ID, labelled "(partner link)" with `rel="nofollow noopener sponsored"`. Blocks carry `data-ps-placement="<slug>"` and need the GA4 placement script before `</body>`.
- Placement order: GetYourGuide, Airalo, SafetyWing, Welcome Pickups, car rental, Radical Storage, Klook. Prefer DiscoverCars and Welcome Pickups; **avoid adding Klook placements; skip Booking.com.**
- Car rental: DiscoverCars (campaign 117, promo 3873) where it serves the country, EconomyBookings (campaign 10, promo 4480) where it does not. One per page. Always `powered_by=false`.
- eSIM: Airalo plan tiles (`esim-<country>-<size>`). Yesim only as the promo link `yesim.tpx.li/Bc6pLC09` (20% first order, ends 28 Feb 2027; remove the copy after).
- SafetyWing widget on destination articles; "travel medical insurance" wording, price per day, no "best" or "recommended". Never write "no hidden fees" or "free cancellation" as our own promise.
- Other IDs: GetYourGuide `D7IXONS`, SafetyWing ref `26492686`, 12Go agent `15357692`, Trip.com widget `S14633845` (index and flights only).
- **No self-referral** (Ari's own purchases). **No new partner applications, outreach, or contact with SafetyWing without Ari's go-ahead.** Never store payout email, phone or address.

## Key decisions and why
- **Static site, no build:** one owner, Claude edits files directly; nothing to break between edit and deploy.
- **Pocket Guides as web pages, not a native app:** no store, no install friction, shareable by link, works offline once saved. Airports have weak signal and roaming costs.
- **Network-first service worker:** facts (gates, buses, hours) go stale; the cache is a fallback, not the source.
- **Scripts over hand edits:** 60+ pages must stay consistent across waves; each wave was verified live at 390px before the next.
- **Official sources only for transit facts,** with a visible "checked" date, because wrong gate or bus info costs the traveller real time.
- **Global positioning:** from-India guides stay as a segment. Japan is the lead growth topic.
- **Distribution over more articles:** Ari prefers shares, hubs and cross-links to new content that cannibalises existing pages.
- **`?src=` on every shared link** so each channel can be measured per 100 opens before investing more.

## Tried and rejected (do not re-propose without asking)
- Newsletter and sign-up boxes: removed site-wide 10 Nov 2026 (some forms were broken or fake). Any return of email capture is Ari's call.
- Localrent widget: retired (not in USA or Canada, unreliable). Yesim old program: broken, redirected to Airalo.
- Klook city deep links (`klook.com/en-US/city/...`): redirect to the homepage. Klook's own `aid=116473`: deactivated. Old `affiliate.klook.com/redirect` format: deprecated.
- All FIFA 2026 content: removed with 301s. Long-weekends-2027 article: cancelled. Japan kids section, Reddit re-enable, site redesign, Pinterest: skipped or parked.
- WhatsApp icon in the Pocket Guide header: replaced by the labelled bottom-right pill. "Open it, then add to home screen" wording: wrong on iPhone.
- Hand-editing generated pages: lost on the next regeneration.

## How changes reach the live site (since 21 Nov 2026)
- **Ari's Mac:** the working clone is `~/packsmart` (a real git clone, not the Project mount). Its remote is `git@github.com-packsmart:packsmartapp/packsmart.git` (SSH alias with its own key, pushes as `packsmartapp`). Run `git pull` before editing there, because Claude may have pushed from elsewhere.
- **Claude Code cloud session:** clones `packsmartapp/packsmart` with push access, edits, checks pages at 390px and 360px in a headless browser, shows the diff, and pushes only after Ari's OK. It can also push a side branch for a Vercel preview URL first. The sandbox cannot open packsmartapp.com or Unsplash, so the final look at the live page is Ari's; Vercel deploy status is checked through the Vercel connector.
- **Claude chat with the Project:** the GitHub and Vercel connectors act as `packsmartapp` and the `packsmartapps-projects` team. Otherwise the chat prepares the change and gives Ari the commit and push commands.
- **Project-mounted folder (legacy):** git there is flaky. It leaves `tmp_obj_*` warnings and `.git/HEAD.lock` (after a commit run `mv .git/HEAD.lock .git/stale-head-lock-$(date +%s)`); `git checkout <file>` fails (restore with `git show <commit>:path > path`); `device_commit_files` copies can lag, so check the byte size on the Mac. Prefer `~/packsmart` or a cloud session.
- Other projects (CareerTalks, TPG, AITT) have their own SSH aliases and accounts. Never point a PackSmart remote at them or theirs at PackSmart.

## Search Console notes
- Indexed about 56 pages; ranking, not indexing, is the main problem.
- **Ignore "Blocked by robots.txt"** URLs on `book.packsmartapp.com` (the 12Go booking subdomain; its own robots.txt blocks crawlers, which is what we want). The main site's robots.txt blocks nothing. Do not validate those rows.
- Ignore old `.html` duplicates (`cleanUrls` 301s them; canonicals are clean), FIFA redirect URLs and `favicon.ico` in "Crawled, not indexed". "Page with redirect" is expected.
- For real "Crawled, not indexed" pages: request indexing only after a real refresh (quota about 10 a day), and add internal links from indexed pages. Generic evergreen topics need something distinctive (original checklist, real trip data).
- After adding URLs to `sitemap.xml`, resubmit it in Search Console. `share.html` (noindex) and `book.html` are left out of the sitemap on purpose.

## Docs upkeep
- `docs/PRD.md`, `docs/DECISIONS.md` and `docs/BACKLOG.md` do not update themselves. When a session changes a feature, makes or reverses a decision, or finishes or finds an open item, it updates the matching doc **in the same commit**. Regenerate `docs/INVENTORY.md` with `python3 -I tools/make_inventory.py` when files are added or removed.
- The repo is public: earnings, traffic numbers, partner talks and outreach stay in the private Project notes, never in these docs.

## Known constraints
- Commit as `git -c user.name="Ari" -c user.email="aricheck@gmail.com"`. Always show a preview (diff summary, what goes live) and wait for Ari's OK before anything is pushed to `main`, because `main` deploys to the live site.
- The sandbox cannot reach most sites (proxy allowlist); some pages cannot be fetched at all. Say so instead of guessing.
- Vercel Web Analytics returns nothing; traffic numbers come from Ari (GA4, Search Console, Travelpayouts).
- GA4 has 13 custom dimensions registered; adding new params needs registration to appear in reports.
- Large files (index.html ~106 KB) are impractical to push through the GitHub connector; use git (Terminal or a cloud session).
- Facts that expire: Malaysia visa-free rule (31 Dec 2026), Yesim promo (28 Feb 2027), Klook boost (31 Dec 2026), Radical Storage rate (30 Nov 2026).
