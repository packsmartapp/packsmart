# PackSmart: product spec (PRD)

Status as of 25 Nov 2026. Source of truth for what the site does today and what is next. Statuses: **Built** (live), **In progress** (partly live or being checked), **Planned** (not started). Anything marked "owner decision" needs the owner's go-ahead before work starts.

## 1. Product

**What it is:** a free travel-prep site for a global audience. Readers get destination guides, packing lists, itineraries and visa and cost information, plus offline "Pocket Guides" for airports and stations in Japan.

**How it earns:** affiliate commissions on partner links (insurance, eSIM, airport transfers, car rental, luggage storage, tours). There are no accounts, no ads and no paid tier in use.

**Who it is for**
- First-time visitors planning a trip abroad (the main reader).
- Travellers about to land or change trains in Japan who need quick, accurate, offline help (Pocket Guides).
- An India-origin segment with its own guides (INR costs, Indian-passport visa steps).

**Principles (apply to every feature)**
1. Useful first, monetised second: a partner block only appears where the reader is thinking about that job.
2. Neutral by default: no India framing outside pages designed for India.
3. Facts come from official sources, carry a "checked" date, and "Last updated" moves only after a real fact check.
4. Light: no sign-up, no pop-ups, no notifications. "Pocket Guide", never "app".
5. Measured: every channel and partner placement can be counted.

## 2. Feature index

| # | Feature | Status |
|---|---|---|
| F1 | Destination guides | Built |
| F2 | India-segment guides | Built |
| F3 | Itineraries, lists and tips | Built |
| F4 | Trip plan generator | Built |
| F5 | Shareable plan link | Built (limited) |
| F6 | Flights, hotels and ground transport | Built |
| F7 | Navigation and Travel Essentials hub | Built |
| F8 | Japan airport, station and city guides | Built |
| F9 | Pocket Guides (ten) | Built |
| F10 | Pocket Guide install and offline flow | Built, real-device checks in progress |
| F11 | Pocket Guide hub block and trip picker | Built |
| F12 | Pocket Guide sharing (WhatsApp) | Built |
| F13 | Pocket Guide analytics | Built, GA4 follow-ups in progress |
| F14 | Partner placement system | Built |
| F15 | Neutral content rule | Built, scan of remaining pages planned |
| F16 | SEO and indexing | Built, indexing work in progress |
| F17 | Web stories | Built |
| F18 | Content freshness process | In progress |
| F19 | Pricing page and paid plans | Removed 22 Nov (D43) |
| F20 | More Pocket Guides (Japan extras, other countries) | Planned |
| F21 | Email capture (inside Packy only) | Built 25 Nov (D58) |
| F22 | Japan hub `/japan` | Built 25 Nov |
| F23 | Packy, the travel helper (Japan) | Built 25 Nov, beta |
| F24 | Japan trip cost calculator `/japan-budget` | Built 27 Nov |

## 3. Features

### F1 Destination guides (Built)
**User:** someone planning a trip to a country. **Flow:** search or homepage card or Destinations index → guide → packing list, visa, best time, cities, budget, apps, FAQ → optional partner blocks.
**Acceptance criteria**
- Each guide follows the article template (`BLOG_STYLE_GUIDE.md`): title `{Country} Travel & Packing Guide 2026: ... | PackSmart`, canonical, OG and Twitter tags, Article, Breadcrumb and FAQ JSON-LD.
- Hero shows date and read time; "Last updated" reflects the last real fact check.
- Page is listed on `public/blog.html` and `sitemap.xml`.
- No horizontal scroll at 390px wide.
- Visa and entry statements are hedged ("check current rules") and link to the official page.
**Notes:** about 68 pages in `public/blog/`. Six guides were renamed without `-from-india` on 16 Nov, with 301s from old URLs.

### F2 India-segment guides (Built)
**User:** a traveller from India. **Criteria:** these are the only pages allowed to use INR, Indian-passport visa text and India-only IDs or application centres (list in F15). They are linked from the Destinations index, not from neutral pages' cards or CTAs.

### F3 Itineraries, lists and tips (Built)
**User:** a reader who wants a day plan or a checklist. **Criteria:** same template and rules as F1; checklists use the `checklist-table` style (teal header, card layout on phones); internal link callouts point to the matching guide.

### F4 Trip plan generator (Built)
**User:** a visitor who wants a personalised plan. **Flow:** homepage form (destination, route, dates, departure time, budget, currency, adults, kids and ages, special requests) → `POST /api/generate-plan` (Gemini) → seven sections (packing checklist, destination briefing, local customs, activities, timeline reminders and more) shown on the page.
**Acceptance criteria**
- A destination is required; otherwise a clear error shows and nothing is sent.
- The result renders without a page reload and survives a refresh (stored in the browser as `ps_plan`).
- If the API key is missing or the call fails, the user sees an error, not a blank page.
**Resolved 22 Nov:** there is no plan limit; the pricing page is gone (D43).

### F5 Shareable plan link (Built, limited)
**Flow:** result → share → `POST /api/share-plan` returns an ID → `/share?id=...` shows the plan. `/share` is `noindex`.
**Criteria:** a link opens the plan on any device while it is stored.
**Known limit:** plans are kept in server memory, so a link lasts only while that serverless instance stays warm (minutes to hours). Permanent links need a store (Vercel KV or similar). Planned only if usage justifies it.

### F6 Flights, hotels and ground transport (Built)
**Pages:** `/flights` (Trip.com search widgets, Travelpayouts white label), `/book` (buses, trains and ferries through the 12Go white label on `book.packsmartapp.com`).
**Criteria:** widgets load; the page carries the affiliate disclosure; `book.packsmartapp.com` is not indexed (blocked in Search Console on purpose).

### F7 Navigation and Travel Essentials hub (Built)
**Menu (since 25 Nov, `w76`):** 🇯🇵 Japan (`/japan`) | Destinations ▾ (`/blog`; dropdown Germany, France, All destinations) | Packing Lists (`/travel-essentials#packing`) | Travel Essentials | Plan My Trip. Flights & Hotels left the menu (page and footer link stay). Footer links Destinations, Flights & Hotels, Travel Essentials, legal pages.
**Criteria:** `/travel-essentials` lists non-destination articles in groups plus the Japan guides and the Pocket Guide block; the blog index lists destination guides only; every page has the same menu.

### F8 Japan airport, station and city guides (Built)
**Pages (12):** Narita, Haneda, Kansai and New Chitose airport guides; Tokyo, Shinjuku, Ueno, Kyoto, Osaka and Sapporo station guides; Kyoto and Osaka city guides. New Chitose has a plain colour hero (no suitable photo).
**User:** someone arriving in or moving around Japan. **Criteria**
- Facts come from the operator's own pages; fare and time figures are rounded ranges; each page states when it was checked.
- Hero line reads "Japan · Published D Mon 2026 · N min read".
- Body copy carries no prices and no partner names; blocks carry them.
- Each page links to its Pocket Guide (airport and station pages) and the trip picker (F11) where it applies.
- Photos are own or licensed, with a credit line and no identifiable people.
**Open:** Haruka price wording awaits the owner; Kyoto city-bus fare wording check; optional own USJ photo.

### F9 Pocket Guides (Built)
**Guides:** Tokyo Station, Shinjuku Station, Ueno Station, Narita, Haneda, Kansai (KIX), Kyoto Station, Shin-Osaka and Umeda, New Chitose Airport and Sapporo Station at `/<key>-pocket`. Registry: `tools/pocket_guides.json`.
**User:** a traveller on a phone at the airport or station, possibly with no signal. **Shell (all guides)**
- Single-file page with a bottom tab bar and info sheets; works at 360px and 390px with no horizontal scroll.
- Airport guides: Find (tiles, slide with More/Back), Terminals, Arrive and Depart checklists (tick-off steps), Help (everyday Japanese phrases with a Play button, then phone numbers).
- Emergency block labels are exact: "Emergency, anywhere in Japan (free, 24 hours)" for 119 and 110; "At X only (not for emergencies)" for the airport number.
- Narita and Haneda have an "I'm connecting" sheet that follows each airport's official connection pages and a line pointing to the other airports.
- Each guide shows its "checked" date and links to the official source pages.
- Partner links are labelled "(partner link)" with `rel="nofollow noopener sponsored"`; there is no sponsor and no other monetisation inside the guide.
**Open:** Kansai connecting sheet (optional, needs Kansai's own connection pages first); native check of the Japanese phrases.

### F10 Install and offline flow (Built; real-device checks in progress)
**Flow (iPhone):** Share → Add to Home Screen → Add → open from the new icon while online → wait for "Ready offline ✓". Android: one-tap Install when the browser allows, otherwise menu steps. In-app browsers (Instagram, Facebook and similar) show "open in Safari or Chrome" with a Copy link button.
**Acceptance criteria**
- The status pill reads "Ready offline ✓" only after the guide is cached.
- Header shows "Saved on this phone: <date>" once a saved copy exists, separate from the "checked" date.
- Service worker is network-first with cache fallback; cache name `<key>-pocket-v7`; reopening in airplane mode loads the guide.
- The install sheet says the saved copy may be cleared if the guide is not opened for a while.
**Not yet verified:** a real iPhone or iPad pass (add, open from the icon, wait for "Ready offline", airplane-mode reopen). The owner tests on iPads.

### F11 Hub block and trip picker (Built)
**Hub:** "Your pocket guides" card on `/travel-essentials` (phone-style home screen, one page per country, tappable icons). **Picker:** two chips in each Japan article ("where do you land", "where are you going") that show the matching guides, arrival airport first with "Start here".
**Criteria:** driven by `tools/pocket_guides.json`; the six airport and station articles omit their own guide; links carry `?src=art_<tag>`; the picker contains no partner links.
The phone shows up to 12 icons per country (three rows of four; tighter spacing once there are more than 8), so the ten Japan guides fit without the "See all" button.
**Planned:** a `/pocket-guides` index page (the hub's "See all" button needs it before it is shown).

### F12 Sharing (Built)
**Flow:** tap the green "Share this" pill (bottom right, above the tab bar) → WhatsApp opens with a ready message and the guide link ending `?src=wa`.
**Criteria:** pill never covers the last lines of a panel; hidden in print; sits below the sheet scrim; tap sends `pg_share` with `via=whatsapp`; opens from the link record `src=wa`.

### F13 Pocket Guide analytics (Built; follow-ups in progress)
**Principle:** anonymous taps only: no name, no account, no location, no free text. GA4 property `G-0C4Z7VVGPE`, separated by `guide` and `airport`.
**Criteria**
- Browser Do Not Track and Global Privacy Control are respected (nothing sent). A visible "Turn off counting" link stores the choice.
- Events taken offline are queued (max 60, 7 days) and sent on reconnect with `queued=1`.
- `?pgdebug` logs events to the console and GA4 DebugView.
- Events: `pg_open`, `pg_first_app_open`, `pg_install_*`, `pg_tab`, `pg_tile`, `pg_slide`, `pg_terminal`, `pg_phrase*`, `pg_play`, `pg_step`, `pg_call`, `pg_partner`, `pg_outbound`, `pg_internal`, `pg_share`, `pg_connect`, `pg_xguide_tap`, `pg_error`. Full dictionary in the Project doc `POCKET_GUIDE_ANALYTICS_17NOV2026.md`.
- `src` codes sanitised to `[a-z0-9_-]`, lower-case, 40 characters.
**In progress:** mark key events in GA4 (`pg_call`, `pg_partner`, `pg_first_app_open`, `pg_installed`, `pg_install_claimed`); optionally register `via`; add one sentence about the counting to the privacy policy.

### F14 Partner placement system (Built)
**User-facing rule:** each block sits where the reader thinks about that job and never touches another widget.
**Criteria**
- Every partner link is a tracked Travelpayouts link with a Sub ID (Sakura Mobile uses its own programme link), labelled "(partner link)", `rel="nofollow noopener sponsored"`.
- Blocks carry `data-ps-placement="<slug>"`; pages with blocks load the GA4 placement script.
- One car-rental widget per page: DiscoverCars where it serves the country, EconomyBookings where it does not. None for Maldives, Nepal, Singapore, China, Baku or the Schengen guide.
- Airalo plan tiles for eSIM; Welcome Pickups for airport transfers; Radical Storage one line per city; Klook only where it already exists.
- Claims match what the provider states; no "free cancellation" or "no hidden fees" as our own promise.
- `/affiliate-disclosure` and the `/about` partner pills list every live partner.
**Gaps:** add Sakura Mobile to the disclosure page and About pills; confirm whether Tripadvisor is still a partner.

### F15 Neutral content rule (Built; scan planned)
**Criteria:** outside the India-designed pages, no "from India" callouts, Indian-passport visa sentences, INR or lakh wording, India-only IDs, or cards and CTAs pointing at India guides. Titles, meta, Open Graph, JSON-LD and URL slugs are included. India as a place (IRCTC, drives on the left, Indian restaurants) is fine.
**Applied to:** 14 blog pages, six country guides, five web stories, homepage, Pricing, Narita and the later Japan guides.
**Planned:** scan Terms, Privacy, Contact, Flights, the disclosure page and the blog index.

### F16 SEO and indexing (Built; in progress)
**Criteria:** `cleanUrls`; 301s for every renamed or removed page; sitemap lists every indexable page (about 83 URLs); JSON-LD parses on all article pages; `robots.txt` allows all.
**In progress:** Search Console shows about 56 indexed pages and several "crawled, not indexed" guides; internal links were added to four of them on 20 Nov. Ranking, not indexing, is the main problem.

### F17 Web stories (Built)
Five stories (Vietnam, Thailand, Sri Lanka, Malaysia, Bali) in `public/web-stories/`, written neutral with USD budgets. **Criteria:** valid AMP story markup, correct dates, CTAs go to a neutral page (Malaysia and Sri Lanka go to the homepage until a neutral guide exists).

### F18 Content freshness process (In progress)
**Criteria:** a page's "Last updated" changes only after its volatile facts (visa, fees, passes, transit) are checked against an official source. Refresh order is by Search Console impressions.
**Dated follow-ups:** Malaysia visa-free rule (31 Dec 2026), South Korea K-ETA exemption (31 Dec 2026), UK ETA and visa fee, Sri Lanka ETA list, Thailand 30-day rule (all January), Yesim promo (28 Feb 2027), Radical Storage rate (early December).

### F19 Pricing page and paid plans (Removed 22 Nov)
PackSmart is free: no paid plans, accounts or payments (D43). `/pricing` was deleted and 301s to the homepage; the footer Pricing link and the "Try PackSmart Pro" prompts were removed from every page; Terms, Privacy, Contact and About were rewritten to match. A future email list for premium offers is the owner's call (D43).

### F20 More Pocket Guides (Planned)
Candidates: other Japan stops; airports outside Japan (Heathrow, Mumbai, Dubai, Frankfurt and others). **Criteria for any new guide:** an entry in `tools/pocket_guides.json`; facts from that operator's own pages; the same analytics event names; re-run the hub and picker scripts. **Owner decision:** no new airport, partner application or outreach without the owner's go-ahead.

### F21 Email capture (Built 25 Nov, inside Packy only)
Newsletter boxes were removed on 10 Nov 2026 and stay removed. The only email capture is Packy's email (D58): "Email me this chat", (28 Nov) "Email it to me" on the budget calculator, and (26 Nov) "Email me these words" on the lucky cat's word card on the Japan hub, which sends the cat's 8 starter phrases (`api/_japan_words.js`, the same list the card shows) with a link back to hear them (`/japan#words`), the ten Pocket Guides as their own home-screen icons (airports, then stations; 80+ phrases in each) and Packy, with the same trip-tips steps and guards. For the chat email: the traveller gets the chat from hello@ (Hostinger SMTP, `api/email-chat.js`), with each answer's guide link, booking button (partner link) and the matching Pocket Guide, plus a "Continue this chat with Packy" link that carries the chat in the link itself (nothing stored on a server). Packy remembers the address on that device for a one-tap updated chat. Trip tips are a separate, explicit yes with an optional trip month; signups land in hello@ until an email marketing service is chosen (B54). Since 26 Nov the trip-tips list itself is MailerLite: an explicit "Yes please" adds the reader (upsert: first door kept, topic tags merged, a known trip month kept on "Not sure") to the group "Japan · trip tips"; the hello@ note stays as a backup. Nothing is sent from MailerLite until the gift sequence is approved and enabled. Privacy policy updated (`packy-email-privacy`, `packy-email-remember`, `packy-email-words`, `packy-email-mailerlite`).
**Criteria:** site-only and rate-limited; only Packy's own chat and booking buttons from `api/_offers.js` can be sent; no email address in logs.

### F22 Japan hub `/japan` (Built 25 Nov)
Built by `tools/w73_japan_hub.py`. Top to bottom: a drawn seasonal Mt Fuji (spring, summer, autumn, winter from the Japan date; "Fuji through the seasons" switcher), Packy's Konnichiwa, a live strip (Japan time, Tokyo and Sapporo weather, the season), the Ask Packy box with a waving lucky cat that says こんにちは (device voice on tap); Plan your trip; airport boarding passes; station train tickets with 確認 checked stamps; Pocket Guides; Hokkaido and seasons. A compact welcome band with the Ask box stays under the menu after scrolling. Washi pink with a seigaiha pattern, sakura branches and seasonal falling petals on wide screens. The 12 Japan guides carry a matching band under their hero (`w77`). GA4 `hub_japan` events: `pass_tap`, `pass_packy`, `ticket_tap`, `ticket_packy`, `season_view`, `cat_hello`, `cat_voice`, `mini_ask`, `hero_packy`.
**Criteria:** checked at 2000, 1280, 1024, 390 and 360px with no sideways scroll; checked dates are read from the guides and Pocket Guides at build time; original drawings only (no copyrighted characters).

### F23 Packy, the travel helper (Built 25 Nov, beta)
`public/packy.js` (pop-up on `/japan` and 8 Japan guides via `w75`), `api/ask.js` (Gemini, answers only from `api/_japan_kb.js`, built by `w74` from `docs/research/*-sources.md`). Each answer: the answer, our guide link, a booking button from `api/_offers.js` (region-aware, labelled partner link), then the official sources in small text; 2–3 follow-up questions; a Pocket Guide card after the 2nd answer; the email card after the 3rd. Approximate prices with the checked date and an official link (D57).
**Criteria:** official sources only; locked to the site and its previews; rate-limited; the AI never chooses or names a partner.

### F24 Japan trip cost calculator (Built 27 Nov)
`/japan-budget`, generated by `tools/w86_japan_budget.py`. The reader enters adults, teenagers, children and little ones; nights in Tokyo, Kyoto, Osaka and Hokkaido; airports and the way into town; taxi rides; Tokyo Disney days, Sanrio Puroland, Ueno Zoo and the Japan Rail Pass; and optionally their own hotel, food and flight figures. The result is itemised: checked prices (from `docs/research/japan-prices-sources.md`, each with its source and checked date), ticket-seller prices labelled as such (Disney children and juniors, Sanrio), the reader's own numbers, and "not priced yet" lines with a way to find each (flights and hotels go to `/flights`). Yen only. Partner lines carry `data-ps-placement="budget-…"`. Entry points: Step 1 on `/japan` (Step 2 is Plan My Trip), Packy's "Work out your trip budget" button (prefilled from the question), and the calculator hands over to Plan My Trip with the group. A guided multi-day tours ending (TourRadar) is built but off (`TOURS_ON`) until TourRadar confirms.
Since 28 Nov it works like a basket ("My trip"): the basics are always in, extras are cards with "+ Add", a tray at the bottom shows what is in and the estimate, and "Review" opens the itemised list with the booking links. Before that it was tap-based (people and nights keep steppers; everything else is a chip or tile, with each section's lines folded under "See the breakdown"). It is one screen: "Your trip" asks three questions (who, nights per area, travel style: Budget, Mid-range or Comfort, which sets hotel, food and the airport transfer), then each section (Things to do; Flights, hotel and food; Getting around; Before you go) shows its choices with their own cost lines and a subtotal, and a floating bar shows the estimated budget at all times. Before that, the result read top to bottom: a small "Estimated budget" line (and a floating one while the form is filled in), the breakdown with sources as plain text (no links out), "Your estimated budget" at the bottom, then "Ready to book?": a checklist of every booking with the partner links in one place, ticks remembered on the device, and the guided tour as the second way when tours are on. Under it, "Keep it, share it": WhatsApp, Copy link (the address rebuilds the exact budget), Save as PDF (print layout) and "Email it to me" (`api/email-chat.js`, `kind: 'budget'`: the total, the trip, a link back and the checklist; trip tips only after "Yes please"). Plan My Trip is a small text link; official sources sit in a folded "Where these prices come from".
**Criteria:** no made-up numbers; every price says where it is from; the total says it covers only the costs listed; works at 360px.

## 4. Cross-cutting acceptance criteria
- Every changed page is checked at 390px for overflow before it is called done.
- Generated pages are changed by editing the script in `tools/`, then re-running the chain (order in `CLAUDE.md`).
- Nothing is deployed without a preview and a push command shown to the owner.
- The repo is public: no secrets, earnings or partner negotiations are committed.
