# PackSmart: backlog

Status as of 21 Nov 2026. Known bugs, open questions, tech debt and next features, highest priority first. "Owner" means it needs Ari (a decision, a real device, an account or a photo). Parked by the owner: the pricing page, its copy and the free plan limit (see `DECISIONS.md` D41).

The repo is public, so earnings, partner conversations and outreach are tracked privately, not here.

## P0: the core promise, accuracy of what is live, compliance

| # | Item | Why it matters | Needs |
|---|---|---|---|
| B1 | **Real-device pass on the Pocket Guides.** iPhone or iPad: add to Home Screen, open from the icon online, wait for "Ready offline ✓", check "Saved on this phone: date", reopen in airplane mode. Also Share this, "I'm connecting" (Narita, Haneda), a phone-number tap. Android: one-tap Install. | Offline is the whole promise and has only been tested in simulated browsers. | Owner (iPads available) |
| B2 | **Add Sakura Mobile to `/affiliate-disclosure` and the `/about` partner pills** (both confirmed missing on 21 Nov). Add NINJA WiFi too if its approval arrives. | Disclosure must list every live partner. | Claude, after owner's yes |
| B3 | **Confirm two claims on the Narita article:** "Our founder visited Narita in October 2026" and the 24 Sept 2026 joint kiosk wording. | First-hand claims must be true. | Owner |
| B4 | **Native-speaker check of the 83 Japanese phrases** before promoting the guides. | A wrong phrase fails the traveller exactly when they need it. | Owner |
| B5 | **Check Klook tracking.** Travelpayouts Sub IDs for: osaka-dt-hiroshima-2, osaka-dt-nara, osaka-food-dotonbori, osaka-food-shinsekai, kyoto-haruka, kyoto-tour-temples, kyoto-dt-nara, kyoto-dt-amanohashidate, luggage. Click each of the four Narita `klook.tpx.li` links once and confirm the landing page (Skyliner, N'EX, layover tour, Limousine Bus). | A link that lands on the wrong product, or untracked, earns nothing and misleads. | Owner |

## P1: measurement and fact accuracy

| # | Item | Notes |
|---|---|---|
| B6 | GA4: mark key events (`pg_call`, `pg_partner`, `pg_first_app_open`, `pg_installed`, `pg_install_claimed`); optionally register `via`; confirm `pg_share`, `pg_connect` and `src=wa` opens look sane. | Owner in GA4. |
| B7 | Privacy policy: one sentence on the Pocket Guide's anonymous counting and the off switch. | Claude can draft; owner approves. |
| B8 | **Pilot review around 3 Dec:** GA4 Placement against Travelpayouts clicks per Sub ID (including `klook-browse-*`), car-block position (USA mid-article vs others), Airalo test (Germany vs France), real DiscoverCars payouts, Radical Storage rate (15% ends 30 Nov). | GA4 groups all car widgets as `Car_Rental_Widget`; use Travelpayouts for the provider split. |
| B9 | Volatile-fact fixes: Malaysia visa-free rule (ends 31 Dec 2026) and its budget total (may include the old eVisa fee); Thailand itinerary USD prices at about 33.5 baht per US$; Singapore visa fee against the official ICA page; international-travel-checklist wording on Singapore; visa-free page rows beyond the five re-checked; line-by-line check of the 41 re-dated pages. | Source: `GEMINI_REVIEW_FIXES_15NOV2026.md` in the Project. |
| B10 | Wording waiting on the owner's yes: Haruka price wording (Kansai guide, Osaka station guide and pocket, then re-run the chain). Check the Kyoto city-bus fare wording. | |
| B11 | **January re-checks:** South Korea K-ETA exemption (to 31 Dec 2026), UK ETA and Standard Visitor fee, Sri Lanka free-ETA list (40 countries), Thailand 30-day rule. Re-read Airalo tile prices every few weeks. | |
| B12 | Search Console: request indexing and watch the "crawled, not indexed" guides (New Zealand, Canada, South Korea, Road Trip, Mexico, cruise). Baseline about 56 indexed. | Owner clicks in GSC. |
| B13 | Real-phone check of the Greece budget tables and the GetYourGuide widgets. | Owner. |
| B14 | Small checks: Costa Rica Pickups widget wording ("San Jose" is unconfirmed, the widget also lists San Jose, CA); whether Tripadvisor is still a partner (on `/about`, not on the disclosure list). | Owner. |

## P2: next features and content

| # | Item | Notes |
|---|---|---|
| B15 | `/pocket-guides` index page. The hub's "See all N pocket guides" button needs it before it can appear. | Build before adding more guides. |
| B16 | Install sheet: stop it opening by itself on first visit (`AUTO_INSTALL_SHEET`, currently `True` in the Narita and Haneda generators; recommended `False`). | Owner's yes, then re-run the chain. |
| B17 | Kansai "I'm connecting" sheet. | Needs Kansai Airport's own connection pages first. |
| B18 | First-hand material: own USJ photo, 2 to 3 Narita photos (replace the stand-in card image on `/travel-essentials`), Narita notes for the marked spot on the article. | Owner. |
| B19 | Neutral-content scan of Terms, Privacy, Contact, Flights, the disclosure page and the blog index. A neutral Malaysia and Sri Lanka guide so those two stories get a real CTA. | |
| B20 | GetYourGuide city passes (`gyg-<country>`) beyond Germany and France. | Plan in the placement checklist. |
| B21 | Car-block polish: images for Bali, Sri Lanka and Vietnam (owner decides: "with a driver" version or skip); move the NZ, Costa Rica, Thailand itinerary and Mexico car blocks inside the article. | Optional. |
| B22 | Wave 1 airport list and any airport outside Japan; backlink outreach (not started). | **No work without the owner's go-ahead.** |
| B23 | Add NINJA WiFi as a second Wi-Fi provider when approved. | Waiting on approval. |
| B24 | Permanent shared-plan links (needs a store such as Vercel KV). | Only if people use sharing. |
| B25 | Email capture, country-scoped. | Owner decision (PRD F21). |

## P3: tech debt

| # | Item | Notes |
|---|---|---|
| T1 | `BLOG_STYLE_GUIDE.md` in the repo is out of date (Localrent, "Yesim broken", newsletter CTA). A newer version exists in the Claude Project. | Sync it; until then `CLAUDE.md` wins on conflicts. |
| T2 | `PROJECT_CONTEXT.md` (private, gitignored) is not in the repo folder on the Mac; the only copy found is in the Claude Project, last written 10 Nov and out of date (for example the homepage cards). `CLAUDE.md` tells sessions to read it first. | Restore it from the Project, update it, or change that line in `CLAUDE.md`. |
| T3 | `public/gyg-preview.html` is a preview page that is still deployed. | Remove after the owner's yes. |
| T4 | Old scripts `w8`, `w11` to `w16`, `w19`, `w20` name the old file names (before the 16 Nov renames): never re-run them. Docs mention `w2` to `w4`, which are not in `tools/`. | Add a "do not re-run" note to those docstrings. |
| T5 | Unused code: `/api/subscribe.js`, the dormant sponsor slot (`SPONSOR = None`), superseded `w48`, the `.price-alt` CSS class. | Delete when sure. |
| T6 | Root scripts `add-ga4.sh`, `add-ga4-fix.sh`, `add-schema.sh` are unexplained. | Ask the owner before use. |
| T7 | Breadcrumb JSON-LD on older articles says "Blog" while the visible menu says Destinations. | Invisible; low value. |
| T8 | Git on the Mac mount leaves `HEAD.lock` and `tmp_obj_*`; `device_commit_files` sometimes writes a stale copy (check the byte size every time). | Workaround in `CLAUDE.md`. |
| T9 | Dated clean-ups: Yesim promo copy after 28 Feb 2027; Klook footnotes after 1 Jan 2027; Klook 12% boost ends 31 Dec 2026; Klook thumbnail approval pending. | |
| T10 | Vercel Web Analytics returns nothing, so traffic comes from GA4, Search Console and Travelpayouts. | Enable or ignore. |
| T11 | Docs upkeep: `PRD.md`, `DECISIONS.md`, `BACKLOG.md` and `INVENTORY.md` do not update themselves. | See the rule proposed in `CLAUDE.md`. |
| T12 | `tools/w32_japan_sakura_block.py` had a syntax error (an unescaped apostrophe, introduced in commit 1047e5c) so it could not run. Fixed and pushed in c836d89 (21 Nov). The live pages already carried that text, so nothing changed on the site. | Done. |
