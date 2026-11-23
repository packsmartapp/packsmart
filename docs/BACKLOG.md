# PackSmart: backlog

Status as of 22 Nov 2026. Known bugs, open questions, tech debt and next features, highest priority first. "Owner" means it needs Ari (a decision, a real device, an account or a photo). Paid plans were removed on 22 Nov (`DECISIONS.md` D43).

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
| B7 | Privacy policy: one sentence on the Pocket Guide's anonymous counting and the off switch. | Done 22 Nov (with the paid-plan removal). |
| B8 | **Pilot review around 3 Dec:** GA4 Placement against Travelpayouts clicks per Sub ID (including `klook-browse-*`), car-block position (USA mid-article vs others), Airalo test (Germany vs France), real DiscoverCars payouts, Radical Storage rate (15% ends 30 Nov). | GA4 groups all car widgets as `Car_Rental_Widget`; use Travelpayouts for the provider split. |
| B9 | Volatile-fact fixes: Malaysia visa-free rule (ends 31 Dec 2026) and its budget total (may include the old eVisa fee); Thailand itinerary USD prices at about 33.5 baht per US$; Singapore visa fee against the official ICA page; international-travel-checklist wording on Singapore; visa-free page rows beyond the five re-checked; line-by-line check of the 41 re-dated pages. | Source: `GEMINI_REVIEW_FIXES_15NOV2026.md` in the Project. |
| B30 | **Leftovers from the 15 Nov LLM review (not yet verified or fixed).** Maldives visa stay (30 vs 90 days on the same page); Sri Lanka ETA fee ($35 vs $50 on the same page, and whether Indians now get a free ETA); Nepal rule on Indian ₹500 notes; Kansai last-train times (the guide says "we did not confirm"); Vietnam FAQ ($25 single/multiple entry); Spain Mallorca driving side; Greece passport-validity and ETIAS wording; itinerary "under $X" headlines below their own table totals (Italy, Spain, Bali, Vietnam); Mexico Day 1 timing (Tulum at 8 am after an early flight); Vietnam Day 4/5 arrival repeated; travel-insurance pre-existing-condition wording. | Fixed 22 Nov: summer destinations (Iceland, Scotland, Bali visa), Nepal (Aadhaar, INR peg and budget table), Switzerland (Matterhorn, Douro, ETIAS URL), Sri Lanka malaria, Spain "Gracias", toiletries aerosol limits, eSIM "80%", solo "70%", Hyperdia (2 Japan guides), MeinFernbus. Needs official sites the sandbox cannot reach, or the owner. |
| B10 | Wording waiting on the owner's yes: Haruka price wording (Kansai guide, Osaka station guide and pocket, then re-run the chain). Check the Kyoto city-bus fare wording. | |
| B11 | **January re-checks:** South Korea K-ETA exemption (to 31 Dec 2026), UK ETA and Standard Visitor fee, Sri Lanka free-ETA list (40 countries), Thailand 30-day rule. Re-read Airalo tile prices every few weeks. | |
| B12 | Search Console: request indexing and watch the "crawled, not indexed" guides (New Zealand, Canada, South Korea, Road Trip, Mexico, cruise). Baseline about 56 indexed. | Owner clicks in GSC. |
| B13 | Real-phone check of the Greece budget tables and the GetYourGuide widgets. | Owner. |
| B26 | **Fix the Plan My Trip links in `api/generate-plan.js`.** The Asia Klook block still uses the plain `klook.com/en-US/?aid=116473` link (that Klook account is deactivated, so the clicks earn nothing; see D18). Replace with a tracked `klook.tpx.li` link or drop the block, in line with D33. | Done 23 Nov: Klook block removed; the planner's GetYourGuide link now searches the trip destination (cmp ps-plan). |
| B27 | **Does the SafetyWing widget's on-page detail drive the clicks?** Compare GA4 placement events with Travelpayouts clicks per Sub ID for the SafetyWing widget against the plain links. If the visible price and options are what works, give car rental, Tiqets and the other partners the same "see it, then decide" format (B28). | Owner's question, 21 Nov. Fold into the B8 pilot review. |
| B14 | Small checks: Costa Rica Pickups widget wording ("San Jose" is unconfirmed, the widget also lists San Jose, CA); whether Tripadvisor is still a partner (on `/about`, not on the disclosure list). | Owner. |

## P2: next features and content

| # | Item | Notes |
|---|---|---|
| B28 | **Affiliate restructure: contextual offers instead of the generic grid.** Replace the identical Travel Essentials grid at the bottom of all 68 articles with 2 to 3 offers that fit each page, placed in the relevant section. | Pilot built 23 Nov (`tools/w61_b28_city_tours_pilot.py`): Italy, Spain and Portugal lose the generic grid and gain a GetYourGuide city box (gyg-<country>-cities, one cmp per city); Germany and France already had this layout and are the comparison pages. Measure at the 3 Dec review (B8), then roll out. |
| B29 | **GetYourGuide deep links.** 79 of 83 GetYourGuide links on articles go to the homepage (`getyourguide.com?...cmp=share_to_earn`), even next to specific activities. Point them at the city or activity page. | Done 23 Nov (`tools/w60_gyg_deep_links.py`): 80 links on 56 pages now search for what they name or the page destination; every link has its own cmp (`ps-<page>` or `ps-<page>-<n>`). |
| B31 | **Shinjuku Station guide (article + Pocket Guide).** Highest confusion and footfall on the Golden Route; target live by mid-January so the article can be indexed before cherry blossom season (late March). Started 22 Nov (owner's go-ahead, D45). Other new guides wait for pilot data (B8). | Built 22 Nov (`w58`, `w59`, sources in `docs/research/shinjuku-sources.md`); partner blocks as on Tokyo Station (Airalo, Welcome Pickups, DiscoverCars, Japan Bullet Train) plus a GetYourGuide Mt Fuji and Hakone day-tour widget (`gyg-shinjuku-daytrips`, same three tours as the Japan itinerary's Mt Fuji tab); no Pocket Guide partners. Odakyū has no affiliate programme on its site (checked 22 Nov); on the preview branch `shinjuku-guide`, waiting for the owner's real-device check. |
| B32 | **Station Pocket Guides: add a Money and ATM tile** (Tokyo, Kyoto, Shin-Osaka and Umeda; the airports and Shinjuku already have one) and a **"Which exit?"** lookup for the big stations (Tokyo, Umeda, Shinjuku). | From the 15 Nov review template. Official sources only. Done 23 Nov for Tokyo, Kyoto, Shin-Osaka and Umeda (`w42`, `w39`, `w36`): "Money and ATMs" finder item and "Which exit?" tile and sheet in each Pocket Guide, plus `#exits` and `#money` article sections. Sources in `docs/research/station-atm-exits-sources.md` (checked 23 Nov); its "Not verified" items are left out. |
| B33 | **Install wording: "Open it again the day before you fly."** iPhone can clear saved site data for guides not opened for a while. Add to the install sheet and the "Ready offline" note on all guides (w44 or w56). | Done 23 Nov (w44: iPhone note and the general install steps, all seven guides). |
| B34 | **Freshness tracking:** store each guide's "checked" date in `tools/pocket_guides.json` and list guides older than 90 days (for example in `make_inventory.py`). Optionally count "Tell us" corrections. | Small. |
| B35 | **Replacement photos (step 2 of the 23 Nov photo fix).** w62 removed about 90 photos that showed the wrong place or thing; pages most affected: the Spain, Vietnam, Bali and Mexico itineraries, the Spain, Italy and Costa Rica guides, first-time flying, toiletries. Add correct photos where a page now has none or the section needs one, each checked visually (CLAUDE.md photo rule). Needs Unsplash search in the `packsmart` environment, or PAKUTASO for Japan. | Next. |
| B36 | **No partner names in our own words (D47).** Stage 1 done 23 Nov (Shinjuku). Stage 2 done 23 Nov: the Japan airport, station and city guides, the Japan guide and the 7-day itinerary, via `tools/w65_no_partner_names_japan.py` (end of the chain; fails if a name is left outside the exceptions). Stage 3: the other articles. SafetyWing box last. | Names in copy read as adverts and go stale; exceptions in D47. | Stage 3 script; SafetyWing brand guidelines check. |
| ~~B39~~ | **Fixed 23 Nov: Japan 7-day itinerary had a doubled `<script>` tag** before the nav script (since April 2026), so the page threw a script error and the phone menu button and the scrolled-nav style did not work. Found by the 390px test. | - | - |
| ~~B40~~ | **Done 23 Nov: airport-hotel boxes say who each hotel suits** (Narita, Haneda T1/T2/T3, Kansai), from the hotels' own sites, checked 23 Nov, with a source line. Narita check-in corrected to the hotel's own 2 pm to 5 am. No Klook photos (CLAUDE.md). | - | - |
| ~~B37~~ | **Closed 23 Nov: SafetyWing price widget on phones.** The headless browser at 390px showed it shifted right and clipped; Ari checked the Japan guide on a real device and it looks fine, so it is a headless-rendering artefact. Reopen only if a real device shows it. | - | - |
| ~~B38~~ | **Done 23 Nov: SafetyWing block on the 11 articles that never had it** (Japan airport, station and city guides; budget destinations; carry-on list), via `tools/w64_safetywing_everywhere.py`, which also fails if any article lacks it. | Missed when those pages were built; found by Ari. | - |
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
| B25 | Email capture, country-scoped. Owner's plan (22 Nov): a list for premium travel offers, trips above about ¥50,000. Needs a provider, a consent line and a Privacy Policy section before it goes live. | Owner decision (PRD F21, D43). Later. |

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
| T8 | Git on the Project-mounted folder leaves `HEAD.lock` and `tmp_obj_*`; `device_commit_files` sometimes writes a stale copy (check the byte size every time). | Mostly avoided since 21 Nov: work in the `~/packsmart` SSH clone or a cloud session (see `CLAUDE.md`). |
| T9 | Dated clean-ups: Yesim promo copy after 28 Feb 2027; Klook footnotes after 1 Jan 2027; Klook 12% boost ends 31 Dec 2026; Klook thumbnail approval pending. | |
| T10 | Vercel Web Analytics returns nothing, so traffic comes from GA4, Search Console and Travelpayouts. | Enable or ignore. |
| T11 | Docs upkeep: `PRD.md`, `DECISIONS.md`, `BACKLOG.md` and `INVENTORY.md` do not update themselves. | Done 22 Nov: rule added to `CLAUDE.md` ("Docs upkeep"). |
| T15 | `tools/w24_mobile_safetywing_footer.py` reads `public/pricing.html`, which no longer exists. It was a one-off; do not re-run it. | Note added here; add a docstring line if the script is touched. |
| T13 | **Compiled Python files are deployed.** `public/images/__pycache__/*.pyc` (w22, w23, w25) are committed under `public/`, so the site serves them. | Done 23 Nov: removed. |
| T14 | **`tools/w31_haneda_airport_page.py` is behind the live Haneda article.** A full regeneration brings back `haneda-airport-hero.jpg` (live uses `haneda-airport-hero-1600.jpg` in og:image, twitter:image, the hero and the Pinterest link) and an older sitemap `lastmod`. | Fixed 22 Nov: generators reuse an existing `-1600` hero when `sips` is missing. |
| T12 | `tools/w32_japan_sakura_block.py` had a syntax error (an unescaped apostrophe, introduced in commit 1047e5c) so it could not run. Fixed and pushed in c836d89 (21 Nov). The live pages already carried that text, so nothing changed on the site. | Done. |
