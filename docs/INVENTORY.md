# PackSmart: file inventory

Generated 27 Nov 2026 by `tools/make_inventory.py` (re-run it after adding scripts, pages or docs).
Every file below is already saved in git (`packsmartapp/packsmart`, branch `main`); `git clone` is the full backup.
This page says what exists and where. It does not repeat file contents, because git always has the latest version.

## Where things live

| Place | What is there |
|---|---|
| This repo, `public/` | everything deployed to packsmartapp.com |
| This repo, `tools/` | Python generators and post-processors, plus `pocket_guides.json` |
| This repo, `api/` | Vercel serverless functions |
| This repo, `docs/` | product spec, decisions, backlog, this inventory |
| This repo, root | `CLAUDE.md` (loaded every Claude Code session), `BLOG_STYLE_GUIDE.md`, `vercel.json`, `package.json` |
| Claude Project "Packsmart" | about 170 dated build notes, fact sheets and link requests (`AFFILIATE_*`, `POCKET_*`, `*_BUILD_NOTES`, `*_FACTS`, `KLOOK_*`); not in the repo |
| Gitignored, not in this folder | `PROJECT_CONTEXT.md` (private context; only the Claude Project copy was found on 21 Nov, last written 10 Nov), `backlink-outreach/`, `pinterest-pins/` |

## Root files

- `BLOG_STYLE_GUIDE.md`
- `CLAUDE.md`
- `add-ga4-fix.sh`
- `add-ga4.sh`
- `add-schema.sh`
- `package.json`
- `vercel.json`
- `.gitignore`

## api/ (Vercel functions)

- `api/_japan_kb.js`
- `api/_japan_lessons.js`
- `api/_japan_words.js`
- `api/_offers.js`
- `api/_packy_png.js`
- `api/ask.js`
- `api/email-chat.js`
- `api/generate-plan.js`
- `api/share-plan.js`
- `api/subscribe.js`
- `api/weather.js`

## docs/

- `docs/BACKLOG.md`
- `docs/DECISIONS.md`
- `docs/INVENTORY.md`
- `docs/PRD.md`

## tools/

Run order for a full rebuild of the Japan pages is in `CLAUDE.md` ("Generator scripts"). Regenerating a page wipes edits made by later post-processors.

| Script | What it does (first docstring line) |
|---|---|
| `w5_china_portugal_costa_rica.py` | Wave 2c: Airalo eSIM tiles on China, Portugal, Costa Rica; Radical Storage lines on Portugal and Costa Rica; |
| `w6_baku_mexico_sri_lanka.py` | Wave 2d: Airalo eSIM tiles on Baku, Mexico (guide + 7-day itinerary), Sri Lanka; Radical Storage lines on all of them; |
| `w7_sri_lanka_discovercars.py` | Sri Lanka: replace the Localrent car widget with the DiscoverCars search form (Colombo airport, CMB). |
| `w8_klook_browse.py` | w8: replace untracked generic Klook search links (aid=116473) with tracked |
| `w9_click_label_disclosure.py` | w9: (1) rename the click-tracker label 'tpwdg.com': 'Localrent' to 'Car_Rental_Widget' |
| `w10_about_partners.py` | w10: update the 'Trusted partners' pills on the About page. |
| `w11_car_image_usa.py` | w11: add the road-trip image to the USA DiscoverCars block (same layout as Germany/France/Italy/Japan/Spain). |
| `w12_usa_move_car_block.py` | w12: USA guide: move the DiscoverCars block up so it no longer sits directly in front of the Klook block. |
| `w13_car_images_australia_portugal.py` | w13: add the road-trip image to the Australia and Portugal DiscoverCars blocks (same layout as Germany/France/Italy/Japan/Spain). |
| `w14_car_images_nz_canada.py` | w14: add the road-trip image to the New Zealand and Canada EconomyBookings blocks (same layout as Germany/France/Italy/Japan/Spain). |
| `w15_car_images_greece_costa_rica.py` | w15: add the road-trip image to the Greece and Costa Rica DiscoverCars blocks (same layout as Germany/France/Italy/Japan/Spain). |
| `w16_car_images_uk_dubai.py` | w16: add the road-trip image to the UK and Dubai DiscoverCars blocks (same layout as Germany/France/Italy/Japan/Spain). |
| `w17_car_images_thailand.py` | w17: add the road-trip image to the Thailand guide and 7-day itinerary DiscoverCars blocks (same layout as Germany/France/Italy/Japan/Spain) |
| `w18_car_images_malaysia.py` | w18: add the road-trip image to the Malaysia DiscoverCars block (same layout as Germany/France/Italy/Japan/Spain). |
| `w19_car_images_south_korea_mexico.py` | w19: add the road-trip image to the South Korea guide, Mexico guide and Mexico 7-day itinerary DiscoverCars blocks (same layout as Germany/F |
| `w20_move_car_blocks.py` | w20: move the car-rental block so it never sits directly after another widget. |
| `w21_neutral_articles.py` | w21: make the non-India articles neutral (no 'from India' framing). |
| `w22_neutral_country_guides.py` | w22: make six country guides neutral (no 'from India' framing) and move them to neutral URLs. |
| `w23_neutral_stories_home_pricing.py` | w23: neutral web stories (Vietnam, Thailand, Sri Lanka, Malaysia, Bali), homepage guide cards, and Pricing. |
| `w24_mobile_safetywing_footer.py` | w24: mobile layout fixes found by measuring every page at 390px wide. |
| `w25_narita_airport_page.py` | w25: new page /blog/narita-airport-guide (neutral, plain-English airport guide, pilot page #1). |
| `w26_narita_links.py` | w26: more internal links to /blog/narita-airport-guide from the Japan articles. |
| `w27_travel_essentials_nav.py` | w27: new top menu + Travel Essentials hub page. |
| `w28_narita_card_image.py` | w28: Travel Essentials hub, Narita card: use a real Narita photo instead of the stand-in transfer image. |
| `w29_narita_card_badge.py` | w29: Travel Essentials hub, Narita card: a small "Download to your phone / Narita Pocket Guide / Works offline" |
| `w30_narita_card_strip.py` | w30 (v3): Travel Essentials hub, Narita card. A one-block mint strip, no icon: |
| `w31_haneda_airport_page.py` | w31: new page /blog/haneda-airport-guide + offline /haneda-pocket (neutral, plain-English airport guide, pilot page #2). |
| `w32_japan_sakura_block.py` | w32: add the Sakura Mobile travel SIM + pocket Wi-Fi block to the 3 Japan articles. |
| `w33_itinerary_klook_transport.py` | w33: add the Klook Narita train/bus ticket cards to the Japan 7-day itinerary (Day 1 arrival). |
| `w34_japan_shinkansen_box.py` | w34: add the Shinkansen box (picture, route, partner button) to the three Japan articles. |
| `w35_kansai_airport_page.py` | w35: new page /blog/kansai-airport-guide + offline /kix-pocket (neutral, plain-English airport guide, pilot page #3). |
| `w36_osaka_station_page.py` | w36: new page /blog/osaka-station-guide + offline /osaka-pocket (neutral, plain-English station guide for Shin-Osaka and Osaka/Umeda, pilot  |
| `w37_travel_essentials_cards.py` | w37: Travel Essentials hub: add the Kansai Airport (KIX) card to Airports and a new Stations section with the Osaka station card. |
| `w38_osaka_city_page.py` | w38: Osaka city guide (article only, no pocket guide). |
| `w39_kyoto_station_page.py` | w39: new page /blog/kyoto-station-guide + offline /kyoto-pocket (neutral, plain-English station guide for Kyoto Station, pilot page #6). |
| `w40_kyoto_station_card.py` | w40: Travel Essentials hub: add the Kyoto Station card to the Stations section (after the Osaka station card). |
| `w41_kyoto_city_page.py` | w41: Kyoto city guide (article only, no pocket guide). |
| `w42_tokyo_station_page.py` | w42: new page /blog/tokyo-station-guide + offline /tokyo-pocket (neutral, plain-English station guide for Tokyo Station, station pilot page  |
| `w43_tokyo_station_card.py` | w43: Travel Essentials hub: add the Tokyo Station card to the Stations section (after the Kyoto Station card). |
| `w44_pocket_install.py` | w44: easier install for every offline pocket guide (Haneda, Narita, KIX, Osaka, Kyoto, Tokyo). |
| `w45_pocket_crosslinks.py` | w45: cross-links between the offline pocket guides (Haneda, Narita, KIX, Osaka, Kyoto, Tokyo). |
| `w46_hub_and_desktop.py` | w46: (1) livelier "Offline pocket guides" block on the Travel Essentials hub, built from tools/pocket_guides.json; |
| `w47_hub_phone.py` | w47: "Your pocket guides" block on the Travel Essentials hub, version 3: white card, plain-English explanation of what a |
| `w48_japan_articles_block.py` | w48: "Pocket guides" journey-line card inside the Japan articles. |
| `w49_trip_picker.py` | w49: trip picker ("which guides do you need?") in the Japan articles. Replaces the w48 journey-line card. |
| `w50_safetywing_complete_box.py` | w50: add a short 'Nomad Insurance Complete' box INSIDE the SafetyWing Essential card, under the price widget (v2). |
| `w51_internal_links.py` | w51: internal links to four guides Google crawled but did not index (GSC "Crawled - currently not indexed", 20 Nov 2026): |
| `w52_internal_links_mexico_cruise.py` | w52: internal links to two more guides Google crawled but did not index (GSC "Crawled - currently not indexed", |
| `w53_city_pickups_cars.py` | w53: Welcome Pickups and DiscoverCars blocks for the Osaka and Kyoto city guides. |
| `w54_airport_review_fixes.py` | w54: fixes from the 20 Nov 2026 reviewer feedback on the airport guides. |
| `w55_pocket_whatsapp.py` | w55: a WhatsApp share button, always visible at the bottom right of every Pocket Guide. |
| `w56_pocket_review_fixes.py` | w56: fixes from the reviewer's Pocket Guide feedback (21 Nov 2026). |
| `w57_osaka_guide_rename.py` | w57: rename the "Osaka Station" Pocket Guide to "Shin-Osaka and Umeda" on pages that earlier scripts |
| `w58_shinjuku_station_page.py` | w58: new page /blog/shinjuku-station-guide + offline /shinjuku-pocket (neutral, plain-English station guide for Shinjuku Station). |
| `w59_shinjuku_station_card.py` | w59: Travel Essentials hub: add the airport- and station-guide cards that are not built by an earlier script, each |
| `w60_gyg_deep_links.py` | w60: GetYourGuide deep links (backlog B29, 23 Nov 2026). |
| `w61_b28_city_tours_pilot.py` | w61: backlog B28 pilot (23 Nov 2026): contextual offers instead of the generic grid, on the Italy, Spain and |
| `w62_fix_article_photos.py` | w62: fix article photos that do not show what they say, and move out-of-place cross-links (23 Nov 2026). |
| `w63_partner_link_labels.py` | w63: partner-link compliance on the articles (23 Nov 2026). |
| `w64_safetywing_everywhere.py` | w64: the SafetyWing travel medical insurance block on every article, and a check that keeps it there (23 Nov 2026). |
| `w65_no_partner_names_japan.py` | w65: no partner names in our own words on the Japan pages (D47, stage 2; 23 Nov 2026). |
| `w66_no_partner_names_articles.py` | w66: no partner names in our own words on the other articles and top-level pages (D47, stage 3; 23 Nov 2026). |
| `w67_disclosure_partners.py` | w67: keep the Affiliate Disclosure page and the About page's partner pills in step with the partners we link to |
| `w68_ueno_station_page.py` | w68: new page /blog/ueno-station-guide + offline /ueno-pocket (neutral, plain-English station guide for Ueno Station). |
| `w69_read_times.py` | w69: honest read times (24 Nov 2026, owner's request). |
| `w70_new_chitose_airport_page.py` | w70: new page /blog/new-chitose-airport-guide + offline /new-chitose-pocket (neutral, plain-English airport guide for |
| `w71_sapporo_station_page.py` | w71: new page /blog/sapporo-station-guide + offline /sapporo-pocket (neutral, plain-English station guide for JR Sapporo |
| `w72_partner_link_rel.py` | w72: partner links tell the partner where the click came from (24 Nov 2026, D54). |
| `w73_japan_hub.py` | w73: the Japan hub page /japan, and a "Welcome to Japan" banner on /blog when the Japan chip is picked (24 Nov 2026). |
| `w74_japan_ask_kb.py` | w74: the knowledge for "Ask about Japan" (/api/ask), built from the official-source research notes (24 Nov 2026). |
| `w75_packy_rollout.py` | w75: Packy, the pop-up travel helper, on the pages where its knowledge is solid (24 Nov 2026, D56). |
| `w76_focused_menu.py` | w76: the focused top menu on every page (25 Nov 2026, B57). |
| `w77_japan_guide_band.py` | w77: a light Japan band at the top of the Japan station, airport and city guides, and the three general Japan articles |
| `w78_pickups_button.py` | w78: the airport-transfer box's Continue button in our own button style, on every page that has the box (25 Nov 2026). |
| `w79_hub_card.py` | w79: a "Japan hub" card near the end of the 15 Japan pages, so readers find the /japan hub (25 Nov 2026). |
| `w80_klook_tidy.py` | w80: tidy the "tours and tickets" tile boxes (class ps-kd, Klook partner links) (26 Nov 2026). |
| `w81_fuku_phrasebook.py` | w81: Fuku's Phrasebook (27 Nov 2026), the one interactive home for Fuku's Japanese: /japan-phrasebook. |
| `w82_esim_compare_links.py` | w82: a "Compare travel eSIMs" line in every eSIM block (27 Nov 2026, owner: readers could not find the eSIM comparison). |
| `w83_pocket_share_tags.py` | w83: share tags (Open Graph and Twitter) on every Pocket Guide (27 Nov 2026, a tester: /sapporo-pocket had none). |
| `w84_japan_2027_facts.py` | w84: the departure tax and cherry blossoms 2027 on the three general Japan articles (27 Nov 2026, a tester). |
| `make_inventory.py` | make_inventory: regenerate docs/INVENTORY.md from the repo (what exists, where, and what each script does). |
| `packy_eval.mjs` | data file read by the scripts above |
| `pocket_guides.json` | data file read by the scripts above |
| `w62_photo_fixes.json` | data file read by the scripts above |

## public/ pages

**Top-level pages (14):** `about.html`, `affiliate-disclosure.html`, `blog.html`, `book.html`, `contact.html`, `flights.html`, `gyg-preview.html`, `index.html`, `japan-phrasebook.html`, `japan.html`, `privacy-policy.html`, `share.html`, `terms.html`, `travel-essentials.html`

**Pocket Guides (10):** `haneda-pocket.html`, `kix-pocket.html`, `kyoto-pocket.html`, `narita-pocket.html`, `new-chitose-pocket.html`, `osaka-pocket.html`, `sapporo-pocket.html`, `shinjuku-pocket.html`, `tokyo-pocket.html`, `ueno-pocket.html`
Each also has `<key>-sw.js` (service worker) and `<key>-pocket.webmanifest`.

**Blog and guides (`public/blog/`, 72 pages).** Japan-related (11): `haneda-airport-guide.html`, `japan-7-day-itinerary-budget.html`, `japan-travel-packing-guide-from-india.html`, `japan-travel-packing-guide.html`, `kansai-airport-guide.html`, `kyoto-station-guide.html`, `kyoto-travel-guide.html`, `narita-airport-guide.html`, `osaka-station-guide.html`, `osaka-travel-guide.html`, `tokyo-station-guide.html`

**Web stories (5):** `bali-travel-guide.html`, `malaysia-travel-guide.html`, `sri-lanka-travel-guide.html`, `thailand-travel-guide.html`, `vietnam-travel-guide.html`

**Images:** 170 files in `public/images/`; site icons and logos in `public/`.

**Other public files:** `favicon.ico`, `packsmart-icon.svg`, `packsmart-logo-white.svg`, `packsmart-logo.svg`, `packsmart-phase1.js`, `packsmart-widgets.js`, `packy.js`, `robots.txt`, `sitemap.xml`

## How to save everything to disk

```
git clone git@github.com-packsmart:packsmartapp/packsmart.git   # or your usual remote alias
```
The Project notes are not in git: open the Claude Project "Packsmart" and download or copy the ones you want.
