# PackSmart: decision log

Status as of 22 Nov 2026. Oldest first. Each entry gives what was chosen, what it was chosen over, and why. "Not recorded" means the project notes do not say; nothing has been guessed. Later entries can replace earlier ones (marked **Superseded**).

## Before August 2026

**D01. Static HTML on Vercel, no framework or build step** (date not recorded)
- Chose: plain HTML, CSS and JS, deployed from `main`; a few Vercel serverless functions in `api/`.
- Instead of: a framework or CMS (alternatives not recorded).
- Why: not recorded. In practice it lets one owner and Claude edit a file and push, with nothing to break in between.

**D02. Clean URLs** (May 2026)
- Chose: `cleanUrls` in `vercel.json` and a site-wide cleanup of `.html` links, canonicals and schema (1,303 links).
- Why: not recorded (the cleanup ran alongside the SEO title and meta work). Old `.html` URLs 301 to the clean ones.

**D03. No self-referral on affiliate links** (date not recorded)
- Chose: the owner never buys through his own links.
- Why: it breaks programme terms.

## August to September 2026

**D04. Fix broken affiliate formats** (Aug 2026)
- Chose: replace the dead Yesim `p=8310` links and the hijacked Klook `affiliate.klook.com/redirect` hand-built format (it was seen redirecting to spam).
- Why: those links earned nothing or sent readers somewhere bad.

**D05. `/share` is `noindex`** (1 Aug 2026)
- Why: shared plan pages were reported as soft 404s in Search Console.

**D06. India repositioning of 15 guides** (Aug 2026) — **Superseded by D11**
- Chose: retitle guides "{Country} from India 2026: Visa, Trip Cost in INR & Packing List".
- Why: not recorded.

**D07. Reddit: link-free answers first, linked ones after the account aged** (Aug 2026) — **Superseded by D10**
- Why: not recorded. The plan was to post linked answers after the account had aged about a week.

## November 2026

**D08. Content refresh order and rule** (10 Nov)
- Chose: refresh by Search Console impressions; bump "Last updated" only after a real fact check.
- Instead of: bumping dates without a real update.
- Why: the rule is recorded; the reason is not.

**D09. Skip: Diwali-to-December card swap, long-weekends-2027 article** (9 Nov)
- Chose: revert the card swap; cancel and remove the article; do not re-propose without asking.
- Why: owner's call; the Diwali URL stays and is refreshed mid-2027.

**D10. Skip: Reddit re-enable, Japan kids section** (9 Nov)
- Chose: leave Reddit off; add any kids content to the existing Japan guide, not a new page.
- Why: owner's call; a new page would compete with the existing Japan pages.

**D11. PackSmart is global, not India-only** (10 Nov)
- Chose: global positioning; India guides become one segment; Japan, Germany, France, Switzerland and Portugal lead the homepage strip.
- Instead of: the India-first framing in D06.
- Why: the owner has global plans.

**D12. No sign-up, no newsletter** (10 Nov)
- Chose: remove newsletter boxes from all 67 pages (some forms were broken, one was fake); keep `/api/subscribe` unused.
- Instead of: fixing the forms.
- Why: the owner does not want sign-ups, and a "Join 500+" claim had no list behind it. Any return of email capture is the owner's call (see PRD F21).

**D13. Remove all FIFA 2026 content** (10 Nov)
- Chose: delete five pages, 301 each to the closest remaining guide, strip mentions elsewhere.
- Why: not recorded. Redirects were added so old links still land somewhere useful.

**D14. SafetyWing wording follows the provider's rules** (10 Nov)
- Chose: "travel medical insurance", price per day (about $2), no "best" or "recommended", "partnered" not "sponsored".
- Why: stay within the provider's brand and compliance rules.

**D15. Pilot the affiliate package on Germany and France** (11 Nov)
- Chose: Welcome Pickups, Airalo tiles, GetYourGuide city pills, Tiqets, SafetyWing; measure before rolling out.
- Then: Waves 2 to 2d rolled the same package out across the other guides.

**D16. DiscoverCars as the default car rental; Localrent retired** (14 to 15 Nov)
- Chose: DiscoverCars wherever it serves the country (approved 14 Nov), EconomyBookings where it does not.
- Instead of: Localrent widgets (no coverage for USA or Canada; the owner retired it on 15 Nov).
- Why: wider coverage with one provider; only one DiscoverCars widget per page works.

**D17. Airalo tiles replace Yesim; Yesim only via the promo link** (15 Nov)
- Chose: three Airalo plan tiles per page; keep the Yesim promo link (20% off first order, to 28 Feb 2027) only where a Yesim card remains.
- Why: Yesim's old programme was broken and redirected to Airalo; the tiles name real fixed-data plans.

**D18. Klook only through tracked links** (15 Nov)
- Chose: tracked `klook.tpx.li` links; replace all plain `aid=116473` links.
- Why: Klook's own account was deactivated, so plain links earned nothing; city deep links redirect to the Klook homepage.

**D19. No two widgets back to back; car block mid-article** (15 to 16 Nov)
- Chose: the car block sits between two H2 sections with copy on both sides.
- Instead of: parking it at the end of the article.
- Why: the owner's rule; the USA page was done first and the others followed. Further reasoning not recorded.

**D20. One neutral click label for car widgets** (15 Nov)
- Chose: GA4 label `Car_Rental_Widget` for all providers loaded from `tpwdg.com`.
- Cost: GA4 cannot split DiscoverCars, EconomyBookings and Kiwitaxi; Travelpayouts has the split.

**D21. Neutral articles rule** (16 Nov)
- Chose: outside India-designed pages, no India framing anywhere, including titles, meta, Open Graph, JSON-LD and URLs. Applied to 14 blog pages, six country guides, five web stories, homepage and Pricing.
- Instead of: leaving India callouts on global pages.
- Why: it follows D11; a global reader should not see "Indian passport holders" on a general page.

**D22. Rename six guides, drop `-from-india`** (16 Nov)
- Chose: new URLs with 301s from both clean and `.html` forms; sitemap, index and inbound links updated.
- Cost: the new URLs start fresh history in GA4 and Search Console.

**D23. Airport pages as a traffic pilot, starting with Narita** (16 Nov)
- Chose: one airport first; measure 8 to 12 weeks before a wider wave.
- Why: people decide at the moment of arrival, and facility-specific searches are less crowded than generic ones. SERP checks showed merchant-heavy results at big airports.
- Not decided: the wider airport list awaits the owner's go-ahead.

**D24. Real, licensed photos only** (16 Nov, restated 20 Nov)
- Chose: the owner's own photos or licensed ones (Pakutaso, credited), no identifiable people; never scrape Klook photos; never use photos of public figures.
- Instead of: an AI image of a real airport. It was declined: visible generator mark, garbled signs, real brand names.
- Why: a made-up picture of a real place misleads readers.

**D25. New menu and Travel Essentials hub** (16 Nov)
- Chose: Destinations | Travel Essentials | Flights & Hotels | Plan My Trip; move 21 non-destination articles off the blog index (39 destination cards remain).
- Why: not stated beyond giving non-destination articles their own hub.

**D26. Offline Pocket Guide as a web page, called a "Pocket Guide"** (16 to 17 Nov)
- Chose: an installable offline web page with no accounts or notifications.
- Instead of: a native app (only if the pages show traction) and instead of calling it an "app".
- Why: airport Wi-Fi is uneven, so offline-first; the owner wants a light tool that avoids "the sea of apps", which is why the word "app" is not used.

**D27. Analytics are first-class; anonymous taps only** (17 Nov)
- Chose: GA4 events for every meaningful tap, offline queue, Do Not Track respected, visible off switch, `?src=` on every shared link.
- Why: real numbers are the only thing that can be shown to brands later.
- Also decided: no sponsor exists or is being sought ("zero downloads"); the sponsor slot stays dormant and invisible.

**D28. Partner policy for airports** (17 Nov)
- Chose: Sakura Mobile through its own programme; one provider per job (Airalo for eSIM, Sakura or NINJA for Wi-Fi); a light approved partner line inside the guide; Priority Pass on hold until there is traffic; AirHelp skipped; no new partner application or outreach without the owner's go-ahead.
- Why: avoid two providers for one job, and do not approach partners with no numbers to show.

**D29. Help tab becomes "Say it in Japanese"** (17 Nov)
- Chose: 83 everyday phrases in eight groups with a Play button, then a second screen for phone numbers.
- Instead of: airport-only help. Why: broader value to a first-time visitor. Needs a native check.

**D30. Extend to six guides, driven by a registry** (18 to 19 Nov)
- Chose: Haneda, Kansai, Tokyo, Kyoto, Osaka after Narita; `tools/pocket_guides.json` feeds the hub and the picker.
- Why: adding a guide should be one registry entry and a script re-run.

**D31. Install flow by device** (19 Nov)
- Chose: Android one-tap where the browser allows; copy-link screen in in-app browsers; iPhone steps with the wording "may" about cleared storage.
- Why: Apple gives websites no install button; the steps are the only route.

**D32. Trip picker replaces the journey-line card** (19 Nov)
- Chose: two chips (landing airport, destinations) that show the right guides; no partner links in it.
- Instead of: a fixed route card (w48). Why: the picker asks where the reader lands and where they go next.

**D33. Prefer DiscoverCars and Welcome Pickups over Klook** (20 Nov)
- Chose: no new Klook boxes (the USJ express and private transfer ideas were not added); existing Klook links stay; skip Booking.com.
- Why: Klook's commission is low and there are already many Klook placements.

**D34. Body copy has no prices and no partner names** (20 Nov)
- Chose: the Japan guides carry neither; blocks carry them. The Typical fares line was dropped when the blocks were copied.
- Why: the rule is recorded; the reason is not.

**D35. Show a "Published" date in the hero** (20 Nov)
- Chose: "Japan · Published D Mon 2026 · N min read" on eight guides; "Last updated" unchanged until a fact check.

**D36. Link to the guides Google crawled but did not index** (20 Nov)
- Chose: short internal callouts on ten pages (New Zealand 3 to 6 inbound links, Canada 4 to 6, South Korea 5 to 8, Road Trip 1 to 4).
- Why: internal links are the cheapest signal available.

**D37. WhatsApp share: pill at bottom right, labelled "Share this"** (20 to 21 Nov)
- Chose: a green pill at the usual bottom-right spot with words.
- Instead of: a header icon (built first) and a bare icon. Why: the owner wanted the usual place and a clear label.

**D38. Reviewer fixes** (21 Nov)
- Chose: install order is add first, open from the icon online, wait for "Ready offline ✓" (iPhone keeps a separate copy for the icon); show "Saved on this phone: date" next to the checked date; an "I'm connecting" sheet that follows the airport's own pages; exact emergency labels; one `src` code per channel (up to 40 characters).
- Instead of: the old wording "open it, then add it", which was wrong on iPhone.
- Left as is: cross-links already existed in the Help tab; only an Arrive-tab line was added for Narita and Haneda.
- Facts for the connecting sheet were checked against the airports' official pages on 21 Nov.

**D39. Generator scripts, not hand edits** (build habit through Nov)
- Chose: numbered idempotent scripts in `tools/`; each fix goes into the owning script and the chain is re-run; scripts never live under `public/`.
- Why: 60+ pages must stay consistent, and regenerating a page wipes later edits.

**D40. Compact `CLAUDE.md`, PRD and decision log in the repo** (21 Nov)
- Chose: one short brief that loads every session, plus these two docs. Dated work notes stay in the Claude Project.
- Why: the old `CLAUDE.md` was a stale 323-line template.

**D41. Park the pricing page and plan limit** (21 Nov) — **Superseded by D43**
- Chose: no work now on the paid plans, the pricing copy or the free plan limit.
- Why: the owner's call ("we are not doing now"); neither is part of the current Japan and affiliate focus.

**D42. Osaka Pocket Guide renamed "Shin-Osaka and Umeda"** (21 to 22 Nov)
- Chose: keep one guide covering both stations, rename it, label the Shin-Osaka-only screens (Arrival, "At Shin-Osaka" on Leaving) and split the phone numbers by station. The `/osaka-pocket` URL stays, so shared links and QR codes still work. Post-processor `w57` carries the name into pages already patched by earlier scripts.
- Instead of: splitting it into two guides (twice the pages and facts to keep current).
- Why: a reviewer pointed out that "Osaka Station" means JR Osaka at Umeda, while several screens were about Shin-Osaka, which could send a traveller to the wrong station.

**D43. No paid plan: everything on PackSmart is free** (22 Nov)
- Chose: remove the Pro and Travel Agent plans, the Lifetime and trial mentions and the plan limits from every page; the planner, guides and Pocket Guides stay open to all.
- Instead of: keeping the parked pricing page (D41), whose limits and payment claims contradicted the Terms, Privacy Policy and homepage.
- Later, owner's call: an email list for premium travel offers (trips above about ¥50,000). Not built yet; it reverses D12 only when the owner says so.

**D44. Japan is the focus; neutral pages stay free of India framing** (22 Nov)
- Chose: Japan leads (Pocket Guides, Japan articles); Indian-passport detail lives only in the India-segment guides such as `japan-travel-packing-guide-from-india`, not as boxes on neutral pages.
- Instead of: the 19 Nov reviewer's idea of Indian airport guides, and an "Indian passport holders" box on every Japan guide.
- Why: large and growing Japan demand, including from India in cherry blossom season; neutral pages follow D21.

**D45. Shinjuku is the next Pocket Guide; the rest wait for data** (22 Nov)
- Chose: build Shinjuku Station (article + Pocket Guide) now, aiming to be live by mid-January before cherry blossom season.
- Instead of: the reviewers' longer list (Shibuya, Namba, Fukuoka, Sapporo, Hiroshima, Nagoya), bus or JR Pass pocket guides, or a Hindi phrase layer.
- Why: Shinjuku has the most confusion and footfall; the article needs time to be indexed; other guides wait for the pilot numbers (D23, B8). Hindi was declined under D44.

**D46. New partner links go through Travelpayouts** (22 Nov)
- Chose: every new partner link uses a Travelpayouts programme, which pays by PayPal.
- Instead of: Klook's direct affiliate account (ID 116473) and Trip.com's direct programme, which pay only by bank transfer to an Indian bank (Trip.com also has a US$200 minimum and pays after the trip is completed).
- Note: the direct Klook account is not deleted; it still records clicks but has no payout set up, so no new links go through it and the old one in `api/generate-plan.js` is replaced (B26). Existing direct Trip.com links stay for now. Hotels and flights: Trip.com's direct programme stays in use for PackSmart hotels and flights (its links and the index/flights widget). The owner's hotel programmes on Travelpayouts are Klook and KKday (23 Nov). The five airport-hotel links (Narita, Haneda T1/T2/T3, Kansai) go through Klook via Travelpayouts (owner, 23 Nov), in line with this decision. Three of them were made from Klook's India pages; Ari checked and they show USD prices, so they stay.

**D47. Readers never see partner names in our own words** (23 Nov)
- Chose: headings, captions, buttons, labels and body text say what a thing is ("airport transfer", "tours and tickets", "eSIM") plus "(partner link)", never the partner's name. Order: the Shinjuku guide first (with its source notes gathered into one Sources list before the FAQ), then the Japan guides and Pocket Guides through their generators, then the other articles. SafetyWing last, after checking its brand guidelines.
- Exceptions: the Affiliate Disclosure page, the eSIM comparison article, and names a traveller needs to find something on the spot (a pick-up counter, for example).
- SafetyWing keeps its name (box, card and text): the owner decided on 23 Nov that it is fine as it is. Stages 1 to 3 done 23 Nov (w58, w65, w66).
- Instead of: naming partners in copy ("as listed by GetYourGuide", "Airalo asks you to verify your ID").
- Why: readers do not need the names; names in copy read as adverts and go stale when a partner changes.

**D48. Japan only until after cherry blossom 2027** (23 Nov)
- Chose: no new countries before spring 2027. Build more Japan stations and airports, then work on traffic, aiming at the cherry blossom crowd (Tokyo peak about late March, Kyoto and Osaka about early April; searches start in January, so pages must be live by about mid-January).
- Order (owner, 23 Nov): Ueno Station, then New Chitose Airport and Sapporo Station together (ski season and the Sapporo Snow Festival in early February), then Shinagawa, then Shibuya, then Fukuoka Airport (article + Pocket Guide each, PAKUTASO photos). Then "cherry blossoms near this station" sections in every station guide and one Cherry Blossom 2027 page built from them, with dates from the official forecasts.
- Instead of: other countries' airports (Bangkok, Bali, Singapore, Seoul), or competing for "cherry blossom forecast" searches, which the big Japan sites own.
- Why: the station and airport guides answer practical questions with official facts and work offline; that crowd has booked and is about to spend on bullet-train tickets, eSIMs, transfers, hotels, tours and luggage storage.

**D49. About page: no Tripadvisor pill, no "best deals"** (23 Nov)
- Chose: remove the Tripadvisor partner pill (nothing on the site links to Tripadvisor) and say "to bring you useful travel services" instead of "the best deals".
- Why: the partner list should match the links, and "best deals" is a claim of our own.

**D50. Skyliner tickets on the Ueno guide; honest read times** (24 Nov)
- Chose: the existing Klook Skyliner link (through Travelpayouts) on the Ueno article and Pocket Guide (placement `klook-skyliner-ueno`), an exception to "avoid adding Klook placements", because Skyliner tickets are what a reader at Ueno is about to buy. Every "N min read" label is now set by `tools/w69_read_times.py` from the article's word count (230 words a minute), on the articles and their cards.
- Why: the Skyliner is the main purchase at Ueno; hand-typed read times were far off (Ueno said 10 minutes for about 4,700 words).

**D51. Pocket Guides and station guides are utility first, partner offers second** (24 Nov)
- Chose: a guide must first answer what a traveller needs on the spot (ATMs and cash, exits, platforms, lockers, help, first and last trains), from official sources with a date. Partner blocks come after that and never replace a missing fact. A gap a traveller would hit (for example ATMs) is filled before the guide is called done.
- Why: travellers save and share a guide that works when they are stuck; that trust is what makes the partner links worth anything.

**D52. JR Hokkaido's own hotels get tracked hotel links, through Travelpayouts** (24 Nov)
- Chose: the JR Hokkaido group hotels by Sapporo, Chitose, Asahikawa and Hakodate stations are listed with "Rooms and prices (partner link)" links made by the owner in Travelpayouts (Klook hotel pages). An owner-approved exception to "avoid adding Klook placements", for these hotels only. Hotel descriptions come only from JR's own hotel list. Hotel Nikko Northland Obihiro and JR Inn Obihiro wait for an eastern Hokkaido page.
- Rejected: a direct JR hotel programme (JR Hotel Group has none, owner checked); a hotel chain's own programme until its network and payout method are known.
- Why: a traveller arriving by train wants a bed next to the station, and Travelpayouts pays the way the site is already paid (D46).

**D53. The Sources list on station and airport guides folds away** (24 Nov)
- Chose: every fact keeps its official source, but the gathered list under the Sources heading opens only on tap ("Show all N official pages"). Applies to the Shinjuku, Ueno, New Chitose and Sapporo guides (w58, w68, w70, w71).
- Why: the owner found the 46 to 57-link lists too long to scroll past on a phone; readers want the guide, and the sources stay one tap away for anyone checking.

**D54. Partner links send the referrer (no `noreferrer`)** (24 Nov)
- Chose: every partner link has `rel="nofollow noopener sponsored"` and never `noreferrer`; `w72` fixes and checks it at the end of the chain.
- Why: the SafetyWing box's main buttons and the Airalo tiles carried `noreferrer` from an old template, so partners saw clicks from the site as coming from nowhere; SafetyWing's review asked why buyers did not seem to come through the website. Commission is unaffected either way (it comes from the ID in the link); `noopener` already covers security.

**D55. A Japan hub page, `/japan`** (24 Nov)
- Chose: one page with every Japan guide (trip planning, airports, stations), the ten Pocket Guides, Hokkaido-this-winter and by-season links; on `/blog`, picking the Japan chip shows a banner to it. Built by `w73` from the cards on `/blog` and `/travel-essentials`, so titles and read times stay in step. A slot is kept for the planned "Ask about Japan" assistant.
- Why: owner's mock-up; Japan is the lead topic (D48) and its guides were spread over two pages. Hubs and cross-links before new articles.

**D56. One Packy, scoped by country** (24 Nov)
- Chose: one character and one engine (`public/packy.js` pop-up, `/api/ask`), with a knowledge pack per country from official sources only. On a country's pages Packy is that country's helper ("Packy · Japan"), with example questions and a guide link for the page's topic. The homepage will ask "Where are you going?" and route to a country Packy covers, offering a note when Packy reaches other countries (email capture), rather than an open search box. An open umbrella Packy waits until three or more countries have solid knowledge.
- Rollout: stage 1 is `/japan` and the guides with solid knowledge (Japan guide, Sapporo, New Chitose, Ueno, Shinjuku, Tokyo, Kyoto, Osaka stations); Narita, Haneda and Kansai after their research notes; Pocket Guides after real questions are reviewed (they are offline-first).
- Why: Packy's edge is trust and precision, not breadth; an open box everywhere invites questions it cannot answer and compares it with search engines. Fixes to the one engine reach every page at once.

**D57. Packy gives approximate prices, and a booking button where a partner sells it** (24 Nov)
- Chose: Packy answers cost questions with an approximate price or range from official sources, what it covers, the checked date, and a short "prices change, check the latest on [official page]". When a partner sells the thing asked about (Skyliner or Narita Express tickets, Shinkansen tickets, a JR Pass, airport transfers, eSIM, travel medical insurance, bag storage, guided tours), a "Book online" button labelled "partner link" appears under the answer, using the same tracked links as the guides; hotels and car hire open the guide section that carries those offers. The server picks the button from the question; the AI never writes booking links or partner names.
- Why: travellers ask "how much?" constantly, and "prices change" alone is a weak answer. One price lives in one fact sheet with its date, so it is updated once. The guides' own text keeps the no-prices rule, because 70 pages of typed prices go stale.

**D58. Email capture returns, inside Packy only; Pocket Guide nudge in the chat** (24 Nov)
- Chose: after Packy's 3rd answer (and, from the 2nd answer until sent, an "Email me this chat" chip among the Ask next questions) a one-line card offers "Get this chat by email" (email only); after sending, Packy asks "Want trip tips before you go?" (Yes please / No thanks, the marketing consent) and, on yes, the trip month as one-tap chips. `api/email-chat.js` sends the chat from hello@packsmartapp.com through the existing Hostinger mailbox and sends hello@ a copy of the signup; that mailbox is the list until MailerLite or Kit is chosen. After the 2nd answer a card offers the matching free Pocket Guide (`?src=packy`).
- Why: owner's call. Travellers who buy one thing and leave cannot be reached again; an email they ask for, tied to their trip, is the honest way in. Site-only, rate-limited and chat-only, so it cannot be used to send arbitrary mail.
- 25 Nov, chat and email kept in step: Packy remembers the address in the traveller's own browser (localStorage, that device only; "Use another email" forgets it). After new answers the chip reads "Email the updated chat to a…@…" and sends the whole chat in one tap. The email has a "Continue this chat with Packy" button: the chat travels compressed in the link after `#packy=` (never sent to or stored on a server), and Packy reopens it on the page where it started. Replying to the email for an AI answer needs inbound email first (B54).
- 25 Nov, the email matches the chat: each answer keeps its booking button (labelled partner link) and guide link, and the email ends with the Pocket Guide card Packy showed (e.g. Narita) with `?src=packy_email`. The buttons come only from the shared list `api/_offers.js` (the email form is public, so no other link is accepted); the "Continue" link carries them back into the chat, and packy.js accepts only our own pages and the partner hosts Packy uses.
- 25 Nov: an email sent from a Vercel preview of this project links back to that preview (so the Continue link, guides and Pocket Guides can be tested before going live); from the live site it links to www.packsmartapp.com.
- 25 Nov: Packy's face is in the email (header and next to each answer), attached inline as a PNG (`api/_packy_png.js`, made from the SVG in packy.js), so it shows without loading images from the site.
- 25 Nov: the Ask box on `/japan` stays as Packy's doorway on the hub (option 1 of 3; an inline chat and removing the box were not chosen). It now looks like Packy (his face from packy.js, "travel buddy", pink Ask button), says it opens a chat, offers hub-wide starter questions, and shows "Continue your chat with Packy (n)" when a chat is going.
- 25 Nov, hub redesign wave 1 (ideas 1 and 2 of 5): an arrival hero (licensed Fushimi Inari photo with its credit, Packy's hello, a live strip with Japan time, Tokyo and Sapporo weather from /api/weather and a season line from JNTO, and an arrivals board of fastest official journey times linking to the Pocket Guides) and "Where are you landing?" boarding passes for NRT, HND, KIX and CTS. GA4 `hub_japan` events: `board_tap`, `pass_tap`, `pass_packy`, `hero_packy`. Waves 3 to 5 (station-sign cards and stamps, a Japan map, first words with audio, seasonal snow or petals) wait for the owner's go-ahead.
- 25 Nov: the hub's backdrop is Japanese on wide screens (1200px+): washi-paper colour with a faint seigaiha wave pattern, vector sakura branches on both sides and a few drifting petals (none with reduced motion). Phones get only the washi colour. w73 warns when the board and boarding-pass facts (`BOARD_CHECKED`) are over 6 months old.
- 25 Nov, big screens (option B + C with a touch of A and D, of four mock-ups): from 1000px the hero photo runs edge to edge; from 1500px the page widens to 1320px (4 boarding passes in a row, guide cards 3 across); the remaining sides get a large sakura branch on the left, a small one top right and a vector Mt Fuji with a rising sun and pagoda at the bottom right (from 1400px). Phones unchanged.
- 25 Nov, hero redrawn (owner chose option 1 of 4 lighter mock-ups): no photo; a drawn dawn scene (pink sky, rising sun, Mt Fuji, torii, hills; a sakura branch on phones), dark text, and a light arrivals board (white and cream, red time pills) instead of the black one. Fuji, sun and torii scale into the right-hand space so they never sit behind the text; on phones they form a banner above it. The side Fuji was dropped (the hero has one); the right side gets a sakura branch from the bottom.
- 25 Nov: the hero has no background block (the washi pattern and side sakura show through); text left, a more realistic drawn Fuji right (flat summit, shaded flank, snow gullies, mist, drifting clouds, a soft glow instead of the red sun, a small torii) that drifts as the page scrolls (not with reduced motion). Brand: teal stays the colour for actions (board rows now hover teal), red is the Japan highlight colour.
- 25 Nov: brand match: the hub is back on the site's pink (#FDF0F2) with a teal-tinted wave pattern; labels, outlines and the board heading use teal, red stays for highlights (time pills, torii, "Japan"). Fuji redrawn with a blue sky behind it, lit and shaded sides, ridges, a forested base and a small lake; the scene fades at its edges.
- 25 Nov: the Fuji scene follows the season (Japan date): spring cherry trees, summer green forest with little snow and festival lanterns, autumn maples and first snow, winter snow mantle, white-tipped trees and snowflakes. The falling side petals turn into maple leaves in autumn and snow in winter, and stop in summer. `?season=spring|summer|autumn|winter` previews one.
- 25 Nov: summer gets fireflies (in the scene, and rising along the sides on wide screens); the blue sky glow now fades out inside its own oval, so no edge shows.
- 25 Nov, Packy answer order (owner's call, to keep readers on PackSmart): answer, then "More in our … guide", then the booking button, then the official sources in small grey text (they open in a new tab). Same order in the emailed chat.
- 25 Nov, hub order follows the trip: welcome and arrivals board, Plan your trip, Where are you landing (airports), stations, Pocket Guides, Ask Packy, Hokkaido and seasons (before: airports first, planning fifth). The 12 Japan guides get a light Japan band under their hero (`w77`: breadcrumb to the hub, Japanese name, 確認 stamp with the page's own "Facts checked" date, washi print, also behind "What do you need first?"), so moving from the hub to a guide no longer feels like another site. The article bodies are unchanged; no site-wide redesign.
- 25 Nov: the floating Ask Packy button stays visible on the hub at all times (the old rule hid it while the inline Ask box was on screen; after the reorder that looked like Packy vanishing mid-page).
- 25 Nov: Ask Packy (with the lucky cat) moves into the hero in place of the arrivals board, which repeated the boarding passes (same four airports, Pocket Guides and journey facts); Packy's hello bubble goes too, since the box says the same. The hub now reads: welcome, Ask Packy, plan, airports, stations, Pocket Guides, seasons.
- 25 Nov: Packy's "Konnichiwa!" bubble is back in the hero (owner: it sets the Japan mood); a tap now moves to the Ask box below instead of opening the pop-up. The hub's closing line is global: visa rules depend on your passport, with Japan's official visa-exemption list (MOFA), and the India guide named as one of our country-specific guides.
- 25 Nov: the lucky cat says "こんにちは! Konnichiwa! 👋" in a speech bubble on hover (a tap on phones, for 2.5 seconds) and waves faster (GA4 `hub_japan` `cat_hello`).
- 25 Nov: a tap or click on the cat also says こんにちは out loud with the device's own speech voice (Japanese where the device has one, else "Kon-nichi-wa" in English; no sound files). Only on a tap, never on hover: browsers block sound without one. GA4 `cat_voice`.
- 25 Nov: the cat's voice is a young, bright one: a female Japanese voice where the device has one (Apple Kyoko or O-Ren, Microsoft Nanami, Haruka or Ayumi, Google 日本語), else a female English voice, pitched up (1.8). Built-in voices only; a recorded voice would need a voice actor or a paid service.
- 25 Nov: the cat speaks on every tap (Safari and iPadOS dropped a speak() straight after cancel(), so it spoke only once; now it cancels only when still talking and speaks a moment later), and its speech bubble sits above its head instead of over its face.
- 25 Nov, fix: iPad and iPhone play speech only when it starts inside the tap itself; the delayed start (a timer) made the cat silent. It now speaks at once on every tap, skips a tap while still talking, and never cancels just to restart. The bubble sits to the cat's left, level with its body, clear of Fuji and its face.
- 25 Nov: the hub's hero stays in place as a backdrop and the rest of the page slides up over it like a curtain (owner's pick over a sticky Ask bar or a still Fuji). A hero taller than the screen first scrolls until the Ask box is in view, then holds; the curtain carries the page's pink and wave print with a soft shadow, inside the page width so the side sakura stay visible. Fuji's scroll drift is smaller.
- 25 Nov, reversed the same day: the owner wanted the opposite (the top stays in front and the page scrolls behind it). The full hero is taller than most screens, so a compact copy does it: once the hero's Ask box has scrolled away, a band slides in under the menu with ようこそ Welcome to Japan, the Ask Packy box (asks open the Packy chat; GA4 `mini_ask`) and a small seasonal Fuji, and the page scrolls underneath. Curtain removed.
- 25 Nov: "Fuji through the seasons": a ‹ 秋 Autumn › switcher under the hero Fuji cycles the four drawn scenes (spring, summer, autumn, winter), starting on the current one ("· now"); the small band and the falling petals follow. GA4 `season_view`. A rainy-season (tsuyu, June to July) scene is not drawn yet.
- 25 Nov, Japan travel guide (readers stayed about 43 seconds): a "Japan in a minute" box at the top (entry, plugs and power, cash and cards, trains and IC cards, phone data, tax-free shopping, each with its official link, checked 24 Nov 2026, plus Ask Packy and the hub); best time and packing now come before visa; the visa section and its FAQ cover every passport (MOFA list, Visit Japan Web, customs, medicines) instead of US, UK, Australia and Canada; the JR Pass section follows the official pass site (Nozomi add-on ticket, local JR buses, monorail and Miyajima ferry; Hikari about 2 h 50, Nozomi about 2 h 10) and no longer prints pass prices or fares. w65's rule for the old JR "agent" sentence is retired. Budget, food and accommodation sections were not re-checked.
- 25 Nov, Japan guides step 2 (`w77`): a lighter photo tint on the 11 guides with a photo hero (New Chitose has no photo and keeps its navy hero), and an "Ask Packy about <place>" box after the "What do you need first?" tiles on the 8 guides that load Packy, with that place's starter questions from packy.js (GA4 `ask_japan` `guide_box`). Narita, Haneda, Kansai and the Kyoto and Osaka city guides get no box until their official-source notes exist (B55). Step 3, deeper fixes, only for guides GA4 shows as weak.
- 25 Nov, owner's ask (guides should feel like the hub): on wide screens (1200px+) the 12 Japan guides get the hub's washi pink and wave print, its sakura branches on both sides and the seasonal falling petals, with the article on a white panel. Phones stay plain white. Revised the same day on the owner's call: the sakura branches stay fixed at the screen edges (as on the hub), and the text panel widens like the hub, 900px, and 1320px from 1500px screens.
- 25 Nov, guides polish: the name band now reads like the hub's welcome (a ようこそ · 駅 · STATION GUIDE label, then 東京駅 *Tokyo Station* in the hub's serif, the 確認 stamp); the sakura fade in only after the photo header has scrolled away (no clash with the photo); on wide screens the Pocket Guides picker, partner boxes, section tiles and Ask box spread to the panel width, and Related Guides sit three across.
- 25 Nov: on wide screens (Japan guides) the Shinkansen box is one row (picture, route and text, button) and the airport-transfer box is the owner's option C from 1500px (photo left; benefits and the partner's booking form, in its own layout, right); on laptops (1200-1499px) the form needs the full width, so the photo sits beside the benefits with the form below. The form's fields are not re-arranged (the partner's script places its city search itself).
- 25 Nov: on wide screens (1200px+) the eSIM box shows its photo at half width beside the heading, plan tiles and note (about 290px tall instead of about 1,240px); phones unchanged.
- 25 Nov: same for the car-hire box (owner's layout): on wide screens (1200px+) the road-trip collage, its "Illustrative image" note and the three paragraphs sit in the left column; the pick-up chips and the partner's search form sit in the right column beside the photo. The driving-permit tip is a little shorter (same facts) and runs the full width under both columns. Phones unchanged.
- 25 Nov: the travel-insurance box on the 12 Japan guides: on wide screens (1200px+) the heading, text, quote button and the Complete card sit on the left and the price calculator on the right, and the box is as wide as the text panel (it ran edge to edge). About half the height. Phones unchanged; browsers without CSS :has() keep the stacked box.
- 25 Nov: the guide layer (w77) also covers the three general Japan articles: the Japan travel guide, its from-India version and the 7-day budget itinerary (band, sakura background, white panel, wider partner boxes; the Ask Packy box only on the travel guide, the one that loads Packy). The 確認 stamp shows only where the page has a real checked date (the travel guide, 24 Nov); the other two get no stamp rather than an invented date. On small phones (400px and under) the band label is tighter so the stamp never covers it.
- 25 Nov: wide-screen fixes from the owner's review: the transfer box on the three articles (it has no heading of its own) keeps the guides' layout (photo left; benefits, fares and the booking form right on 1500px+), where the form had jumped to the top; the "No eSIM?" travel SIM and pocket Wi-Fi box spreads to the panel width, and on 1500px+ each card puts its picture beside its text so the box gets no taller. Phones unchanged.
- 25 Nov: the day-tour and experience boxes on the Kyoto and Osaka city guides: on wide screens (1200px+) the photo sits on the left, filling its column (plain photos, so cropping is fine; each crop checked), and the text and button on the right. The full-width banner looked stretched. A box without a photo keeps its single column. Phones unchanged.
- 25 Nov: transfer box on the 15 Japan pages: the partner's Continue button is restyled like our own "See dates and options" buttons (white, teal border, dark bold text, teal on hover); its own pale mint read as disabled, and a red version looked heavy. On the three articles the fares line now runs full width under the photo and form, so the right column matches the guides (owner preferred the guides' look). The Osaka guide card image was re-cropped from its hero (the old crop had a black strip) under a new file name, as images are cached for a year.
- 25 Nov: the outline Continue button now covers all 43 pages with the transfer box (owner's request). The rule moved from w77 to a new site-wide post-processor, w78, so it has one source.
- 25 Nov: Packy on every Japan page (the owner found it missing on some): added to the Narita, Haneda and Kansai airport guides (with their own starter questions about getting into town, chosen from what the knowledge pack covers), the Kyoto and Osaka city guides (their city's questions) and the from-India guide and 7-day itinerary (the Japan-wide questions). With Packy, these pages also get the "Ask Packy about <place>" box from w77. Packy is now on 16 pages: the hub and the 15 Japan articles.
- 25 Nov: car-hire box on the 15 Japan pages, second pass: the three paragraphs share one text colour (#444; two were a lighter grey and looked uneven). On 1500px+ the pick-up buttons get their own row under the heading, the photo and the search form sit side by side at the same height (columns 3:2, measured with the partner's real form), and the two paragraphs and the tip run full width underneath (the search column used to end well above the text).
- 25 Nov: a Japan hub card on every article (`w79`, owner: "readers should say wow when they reach the hub"): one card near the end, just before Related posts (or above the insurance box on the two articles without them), never mid-article and never above the partner boxes. Japan pages: "Everything for your Japan trip, in one place"; all other articles, India-segment guides included (owner's call): "Thinking about Japan next?". It previews the hub's look (washi print, drawn Fuji, sakura, falling petals that stop for reduced motion) and links `/japan?src=jp_card` or `?src=art_card` with GA4 `hub_card`, so clicks per 100 views can be compared after a week or two. Instead of: a pop-up or sticky bar, which reads as an ad. The hub was checked on a phone first (first screen and load).
- 25 Nov: a small "Part of our Japan hub" callout at the top of the 12 Japan guides, to the right of the "Published · Last updated · Facts checked" line (w77; under it on phones), with a mini Fuji, linking `/japan?src=jp_top` (GA4 `hub_card`, status `jp_top`). The three general Japan articles have no such line (their dates sit in the hero) and do not get it yet.
- 25 Nov, same day, owner's review: (1) the hub card stays on the 15 Japan pages only; on other articles it is dropped, because a Germany reader would get Japan on top of the other countries' links (too many). (2) The top callout reads "Explore all our Japan guides" (clearer than "Part of our Japan hub"). (3) The affiliate disclosure stays (FTC and UK rules and the partner programmes want it before the first partner link) but on the Japan pages it is one quieter line with an ⓘ and no divider: "This guide has affiliate (partner) links: if you book through them, we may earn a small commission at no extra cost to you."
- 25 Nov: background pattern stays seigaiha (option A of six). The "Going somewhere else?" row is gone from the middle of the hub; a teal "🇯🇵 Japan ▾" switcher next to the welcome label opens the other destinations (GA4 `hub_japan` `switch_open`, `switch_go`). Removed again the same day: the top menu's Destinations ▾ does the same job on every page, so the pill only repeated it.
- 25 Nov, hub lower half: the Airports cards and the "What do you need?" filter are gone (the boarding passes, now `id="arriving"`, cover the four airports); "Plan your trip" uses compact photo cards (4 across from 1500px); stations are drawn as Japanese station-name signs (kanji, line stripe, city) with a red 確認 stamp showing the date the Pocket Guide was last checked, read from the Pocket Guide page at build time, plus Pocket Guide and station guide buttons. The lower half is about 60% shorter on a laptop. Same day, on the owner's ask for the airport feel: the stations became Japanese train tickets (乗車券) in the boarding-pass family (kanji where the airport code sits, a 確認 stamp with the checked date, "Ask Packy about…", a 改札 · GATE stub), and sections got small bilingual labels (空港 · Airports, 駅 · Stations, 旅の計画 · Plan). Characters: original ones only (famous anime characters are copyrighted and trademarked). Owner chose the maneki-neko (lucky cat) of three mock-ups (also Festival Packy and a daruma): drawn in code, it perches on the Ask Packy box and waves its paw (still with reduced motion). The site-wide menu (focus destinations instead of Destinations, Travel Essentials, Flights & Hotels) waits for GA4 numbers (B57).
- 25 Nov, focused top menu (B57, `w76`): 🇯🇵 Japan · Destinations ▾ (Germany, France, All destinations) · Packing Lists (Travel Essentials #packing) · Travel Essentials · Plan My Trip. Why: GA4 (90 days, bot rows from Singapore and China and the owner's own visits set aside) showed real readers on the Germany (about 3 minutes per visit), Japan and France guides and on the general packing lists; Flights & Hotels had few clicks and runs on the Trip.com direct programme (D46), so it left the menu (the page and its footer link stay). The open phone menu's white-on-white links on articles were fixed in the same change.
- 26 Nov, phones first (most readers are on phones): on the Japan hub at phone width the Fuji season switcher sits under the drawing with no label; the time and season pills, the "Where are you landing?" heading and the airport cards are smaller so more cards show per screen; the compact welcome band lines up with the page's 24px margin. The lucky cat shows it can be tapped: a small sound badge until the first tap, and its bubble pops up once per visit when it comes into view (no sound). The Ask Packy button on every page gets a mint glow and a soft pulsing halo (none with reduced motion), because Packy is where a reader starts and is led to guides, Pocket Guides and partner offers.
- 26 Nov, tours-and-tickets tile boxes (`w80`, preview on the Japan travel guide only): the tiles' large pastel emoji blocks (no photo, since Klook's own photos are not used) looked unfinished, and one was purple. They become compact cards: a small icon square on the left, badge, name, details and price on the right; purple becomes the brand pink. The Japan travel guide goes from five such boxes to two (attractions and train tickets); the Hokkaido winter tours, Osaka and private-car boxes are removed (off-topic in the packing section, or covered by the Osaka guide). Other pages with these boxes wait for the owner's OK on the preview.
- 26 Nov, the lucky cat teaches a few words: after a reader's second Konnichiwa, the cat offers "a few Japanese words for your trip" (once per visit; "Not now" is respected). Yes opens a card with 8 starter phrases, each playable with the device's own voice, in the same wording as the Pocket Guides' phrase list, and a link to the Tokyo Pocket Guide (`?src=hub_cat`) for the rest. GA4 `hub_japan` statuses `cat_words_offer`, `cat_words_yes`, `cat_words_no`, `cat_word_play`, `cat_words_more`. The cat's bubble is teal and sky blue and comes from behind its head (owner: not too girly).
- 26 Nov, D58 extended (owner): Packy's email is also offered from the lucky cat's word card, as "Email me these words". Same steps as the chat email (the address, then a separate yes for trip tips, then the trip month), the same guards and limits, and the same signup copy to hello@, marked "from the cat's word card". The words come from the server's own list (`api/_japan_words.js`, shared with the card), so the form cannot send other text. The email links back to `/japan#words` (opens the card), the Tokyo Pocket Guide and Packy. Why: a reader who opens the words is curious, and keeping them for the trip is a useful reason to give an email. Still no other sign-up boxes.
- 26 Nov, MailerLite for trip tips (owner): the list and the coming gift emails live in MailerLite (domain authenticated; Comfort plan before the first real send, since the free plan allows only 5 automation steps and no dynamic content or preference center). Only an explicit "Yes please" to trip tips adds a reader; Packy's questions become a few topic tags (Shinkansen, Narita, kids and so on) and are never stored. Readers who said "No thanks" are not added. The site's mail login is now an app password, and all API keys are stored as Vercel Secrets.
- 26 Nov, Packy answers better (owner: "the responses are quite bad"): the search missed health and emergency questions ("doctor", "sick" never reached the note with 119 and the Japan Visitor Hotline; "emergencies" was cut to "emergenci"), and long notes such as Haneda's filled every slot. Fixed with health synonyms, better word stemming, a light length balance, at most 4 pieces per notes file, and health cost questions kept away from the travel price sheet. New official note `docs/research/japan-health-sources.md` (JNTO's guide for when you feel ill: doctors, ambulance, payment, travel insurance, the Visitor Hotline; from the owner's screenshots). Packy's rules now forbid "the notes don't say" wording and the "I can help with" list after a partial answer, and put emergency numbers first for health questions. `tools/packy_eval.mjs` checks 35 real questions (was 25 of 29 before the fix, now 35 of 35).
- 26 Nov, Packy's booking button restyled (owner: it looked odd, then: keep offers subtle, the conversation is what matters): one slim line under the answer with an icon that fits the offer (insurance, eSIM, bags, transfer and so on; the ticket only for tours), the label, a grey "partner link" and an arrow. The Pocket Guide card became a one-line link at the foot of Packy's answer. The insurance button still goes straight to SafetyWing's quote page in a new tab: the article widget only teases a daily price and links to the same page, so an extra stop would lose readers. Health cost questions now also look for "expenses" and "estimate", and Packy gives JNTO's bill examples and the estimate tip before exceptions.
- 26 Nov, no "free" for the Pocket Guides (owner: "the user can smell something with Free"): everywhere they are now named by what they do, with "no app, works offline" or "no app, no sign-up" answering the real worry. Changed in the 10 airport and station generators (QR notes, printed QR posters, get-it bars), the article blocks (w48, w49, including blocks already on pages), the hub, Packy and both emails. "Install" became "Add it to your Home Screen". Packy's Pocket Guide footnote ("You may find this helpful: ...") shows once per place per visit, the first time an answer is about a place that has a guide (otherwise the general link once, from the second answer), and never on an answer that already carries a partner offer.
- 26 Nov, Packy knows daily life and local laws: new official note `docs/research/japan-daily-life-sources.md` (JNTO): where to buy alcohol (sake shops, supermarkets, convenience stores), drinking outdoors is legal (hanami; keep it quiet, take litter home), carry your passport, smoking only in designated areas, tattoos at onsen, pools and gyms, onsen etiquette (bathing naked, washing first, the small towel kept out of the water, hair, private baths and footbaths, tattoo seals), zero tolerance on drugs including cannabis. The legal drinking age (20, unchanged when adulthood became 18 in April 2022) comes from the National Tax Agency's page, from the owner's screenshot. A code safety net now rewrites "my notes", "the notes don't say" and "I don't have information about" in every answer, because the model sometimes ignored that rule. The search check covers 48 questions.
- 26 Nov, Packy's "Ask next" suggestions stay on the reader's subject and name an airport, station or city only if the reader named it (owner: after a general onsen question, "Where can I find an onsen at New Chitose Airport?" came from the page's own notes and confused).
- 26 Nov, Packy's "Did you know?" (owner: inspire, educate and excite instead of three follow-up questions every time): from the second answer and then at most every third answer, never next to a partner offer, a small card with one fact from the notes and an inline "Tell me more", shown below the three follow-up questions (owner: the questions come first). The model may offer one fact per answer (`FACT:`); the server shows it only if its content words appear together in a single note it was given (so true words from different notes cannot make a false claim) and it has no prices, fares or times. GA4 statuses `fact_shown` and `fact_more`. "Tell me more" uses the model's follow-up question only if it shares a content word with the fact (owner saw a tipping fact lead to an IC card answer); otherwise it asks "Tell me more: <the fact>". Found while testing: the notes do not say New Chitose Airport has a hot spring inside (they cover the bus to Noboribetsu Onsen), so such a fact is now dropped.
- 26 Nov, Packy's conversations: a steady answer shape (the direct answer first, saying who says so when it matters; two to four facts or steps; one "Tip:" when the notes hold one; no deflating caveat at the end) and memory of the last three exchanges (questions and the start of Packy's answers, phone numbers and emails masked) for follow-ups like "and from there?". Earlier answers are context only, never a source of facts. New Chitose Airport's own page now confirms an onsen and hotel inside the airport (name, floor and hours not read yet).
- 26 Nov, Packy and itinerary questions (owner: "can you plan an itinerary for 10 days, for a family of 4" got "I can help with specific travel questions…"): such questions are no longer treated as off-topic. Packy gives a short starting route from the official notes (regions, the train times between Tokyo, Kyoto and Osaka, children's fares or the season where they fit), then a "Build a day-by-day Japan plan" line under the answer opens Plan My Trip on the home page with Japan filled in (`/?dest=Japan&src=packy#plan`), since the planner already builds day-by-day plans for the reader's dates, adults and kids. Packy still invents no sights, day counts or prices. The pattern (`ITINQ` in `api/_offers.js`) skips pass, ticket and visa questions ("is the JR Pass worth it for 7 days?"). Two such questions added to `tools/packy_eval.mjs` (51/51).
- 26 Nov, Fuku's gift emails switched on (owner): the MailerLite automation "Japan gift emails (Fuku's lessons 1-4)" starts when a reader joins "Japan · trip tips" (the "Yes please" to trip tips from Packy's or the cat's email) and sends lesson 1 on day 2, lesson 2 on day 7, then weekly (stations; tipping and eating out; the konbini: cash from ATMs that take overseas cards, IC cards, konbini phrases; cherry blossoms and slow-down phrases). Onsen etiquette was dropped from lesson 3 the same day (owner: too much for a new reader; leave it for readers to discover). Each email: one lesson in romaji with the meaning, a "Did you know?" where it fits, "Next time", an "Ask Packy about your trip" button, then one rotating footer recommendation (1 Pocket Guide icons, 2 eSIM as a partner link, 3 the Japan packing list, 4 Plan My Trip with Japan filled in) and a share box (WhatsApp, MailerLite's forward link, and "Got this from a friend?" back to the cat's words on /japan). Links carry `src=gift<n>`, `gift<n>_ask`, `wa_gift` and `email_fwd`. Facts only from the official notes; the phrases still need a native-speaker check. Lessons 5 to 8 must exist before the first reader reaches lesson 4's "Next time" (about three weeks after their signup). The sequence has 8 steps, more than the free plan's 5, so the paid plan is needed before the trial ends.
- 26 Nov, Fuku's emails tuned (owner: do 1 to 4): (1) each lesson has a real plain-text version (was MailerLite's "can't display HTML" filler), which helps inbox placement and text-only readers; (2) lesson 1 asks the reader to reply with where they land and when (replies are a strong inbox signal and tell us what readers need); (3) every phrase shows the Japanese and a "🔊 Hear" button that opens `/japan?say=<lesson>-<phrase>`: the hub opens that lesson's card on the phrase, and the reader taps to hear it in the device's own Japanese voice (no autoplay: phones need a tap). The lessons live in `api/_japan_lessons.js`, read by both `tools/w73_japan_hub.py` and the email builder `tools/fuku_emails/make.py` (the footer's postal address is passed in at run time, not kept in this public repo); GA4 `hub_japan` statuses `lesson_open`, `lesson_play`, `lesson_words`, `lesson_more`; links carry `src=gift<n>_say`; (4) the 15-minute test automation is off.
- 26 Nov, Fuku's lessons 5 to 8 (owner: write them), weekly after lesson 4: 5 the quiet rules of riding a train; 6 IC cards (tap, top up, go); 7 the four seasons and what to pack; 8 help is easy to find (110, 119, the Japan Visitor Hotline, koban, carry your passport). Facts from `docs/research/japan-basics-sources.md` and `japan-daily-life-sources.md` (JNTO, JR West). Footers: 5 Pocket Guides, 6 Plan My Trip, 7 the packing list, 8 travel medical insurance (SafetyWing, partner link): the one stronger offer in eight emails, after JNTO's own "Don't forget to buy travel insurance!". Lesson 8 has no "Next time" and closes the first eight. The automation is now "Japan gift emails (Fuku's lessons 1-8)" (16 steps; needs the paid plan). The hub's lesson card covers 1 to 8; all 40 phrases and their Japanese still need the native-speaker check.
- 27 Nov, Fuku's Phrasebook (owner: WhatsApp for sharing, but no phone numbers and no channel to post in by hand): `/japan-phrasebook` (w81) is the one interactive home for Fuku's Japanese: the 8 starter words and lessons 1 to 8, each phrase with its Japanese and a 🔊 that plays it with the device's voice (email can't play sound), "📲 Send to my WhatsApp" per lesson (a wa.me link with the first phrases and a link back; the reader sends it to themselves or their trip group, `src=wa_self`), one partner offer per lesson that fits it (1 airport transfer, 2 food tours, 3 bag storage, 4 cherry blossom tours, 5 Shinkansen tickets, 6 eSIM, 8 travel medical insurance; 0 and 7 our own pages), and Packy for any Japan question. Like a Pocket Guide: no app, its own service worker (network first, works offline once opened), Add to Home Screen; noindex. The hub's word card offers "Also send to my WhatsApp" after the email step, and both hub cards link to the Phrasebook. GA4 event `phrasebook` (open, play, wa_self, offer, chip, packy). Later: the emails' 🔊 Hear links move to the Phrasebook, and real recordings replace the device voice after the native-speaker check.
- 27 Nov, the Phrasebook is a daily course (owner: if everything is revealed at once there is no reason to come back), kept separate from the weekly emails: day 1 (the first time a phone opens it) opens the starter words and lesson 1, then one lesson a day; locked lessons show their title and "opens tomorrow / in N days". A lesson opened from a link (an email's Hear button, a friend's WhatsApp) is always open. "Travelling now? Unlock all lessons" for people already in Japan. Kept on the phone (localStorage), no account; on iPhone the home-screen icon has its own memory, so its day 1 is the day it is added. Saving it like a Pocket Guide: a "Keep Fuku on your phone" card (opened from WhatsApp? open in Safari or Chrome first; Share → Add to Home Screen, or the Android prompt; then open from the icon while online), Copy link and Later. GA4 `phrasebook`: unlock_all, save_view, save_prompt, save_later, copy_link. No reminders: a web page cannot notify without more setup, so the icon and "opens tomorrow" bring people back.
- 27 Nov, the emails' 🔊 Hear buttons open the Phrasebook (`/japan-phrasebook?say=<lesson>-<phrase>&src=gift<n>_say`; the plain-text versions link `?l=<lesson>`), so a reader taps once in the email and once on the page to hear the phrase, and the lesson opens even if the daily course has not reached it. The hub's `?say=` card stays for links already sent. The testers' 10-minute copy of the sequence is off.
- 27 Nov, soft start for selling (owner: an airport transfer in lesson 1, when the reader has just learned Konnichiwa, smells of a hard sell): no partner offers in lessons 1 to 3, in the emails or the Phrasebook. Email footers: 1 Pocket Guides, 2 Fuku's Phrasebook, 3 Plan My Trip, 4 cherry blossom tours (partner), 5 Shinkansen tickets (partner), 6 eSIM (partner), 7 packing list, 8 SafetyWing travel medical insurance (partner). Phrasebook offers: 1 the station Pocket Guides, 2 the 7-day itinerary, 3 Plan My Trip, then the same partner offers as the emails for 4, 5, 6 and 8, 7 the packing list. Each offer matches its lesson. Next: per-placement tracked links (Sub IDs) once the owner creates them in Travelpayouts.
- 27 Nov, Packy has its own tracked links: its airport transfer, eSIM and bag storage buttons (`api/_offers.js`, also used in the emailed chat) now use Travelpayouts links with Sub IDs `packy-transfer`, `packy-esim`, `packy-bags-tokyo`, `packy-bags-osaka`, `packy-bags-kyoto`, so Packy's sales are counted apart from the site's. The newer short-link hosts (`tpo.lu`, `airalo.tpo.lu`, `radicalstorage.tpo.lu`) are added to the disclosure check (w67). Lesson 6's eSIM offer has its own links too: `email-l6-esim` in the email (MailerLite) and `pb-l6-esim` in the Phrasebook.
- 27 Nov, owner's phone test: (1) on the Phrasebook, Packy's bullet lists showed as narrow boxed columns because the page's phrase-row styles applied to every list; they are now scoped to the lessons. (2) "can you make a plan for me for Japan?" got Hokkaido day trips: the itinerary pattern (`ITINQ`) now also catches "make/build/suggest … a plan" and "plan … for Japan / trip / holiday", but not "data plan", "eSIM" or "plan B"; the question is in `tools/packy_eval.mjs` (52/52). (3) The Phrasebook's icon and title now show Fuku (drawn from the hub's lucky cat), under new file names (`phrasebook-fuku-*`) because images are cached for a year.
- 27 Nov, Packy leaned to Hokkaido (testers): about a third of Packy's notes (117 of 388) are Sapporo and New Chitose research, and for day trips, skiing, festivals, car hire and zoos Hokkaido is the only region in the notes, so general questions got Hokkaido answers (37% of the top notes for 25 general questions). Now: when neither the question, the page nor the earlier chat names a Hokkaido place, at most 2 Hokkaido notes reach the model (26%); and a prompt rule makes Packy say when an answer only covers one region ("In Hokkaido, …") and ask which part of Japan the traveller is visiting. The real fix is more official notes for the rest of Japan (day trips from Tokyo, Kyoto and Osaka; festivals; skiing in Nagano), see BACKLOG.
- 27 Nov, Kyoto city guide: the Kiyomizu-dera late opening (21 to 30 November 2026) expires on 1 December, so the closing-times list, the temple section and its FAQ now say it sometimes opens late for special night viewings (2026: 21 to 30 November, until 21:30) and to check the temple's own schedule. Fixed in `w41`; Last updated not changed (no new fact check). The two test copies of the gift email sequence were deleted in MailerLite; only the real one remains.
- 27 Nov, eSIM comparison article (owner: demand in this space; focus here before other work): retitled from "Best Saily Alternatives 2026" (which sent readers away from Saily, also a partner) to "Best eSIM for International Travel 2026: Yesim, Airalo, Saily, Maya and Jetpac Compared", also on the Travel Essentials and home page cards; prices now only in the comparison table, marked "checked Nov 2026"; superlatives we cannot back (best overall, cheapest in the market, smoothest, most trusted, largest) softened; Maya and Jetpac stay as honest reviews with a note that we are not partners (a direct programme only with the owner's go-ahead); new section "Using an eSIM in Japan" (JNTO facts, Pocket Guides, Packy). Next: a GigSky review (and GigSky in the title) once its Travelpayouts link exists, and per-provider Sub IDs for this article.
- 27 Nov, finding the eSIM comparison (owner could not find it): (1) `w82` adds "Not sure which eSIM? Compare travel eSIMs →" at the end of every eSIM block (43 articles, `?src=esim_block`); (2) Packy's "More in our…" line points to the comparison for eSIM, SIM, roaming and Wi-Fi questions (place names still win, e.g. a SIM at Narita goes to the Narita guide); (3) the comparison is the first card in Travel Essentials' "Before you fly"; (4) its card is back on /blog (no region, so under All); (5) the Japan hub has "Which eSIM for Japan? Compare travel eSIMs" under the airport cards, opening the article's Japan section (`?src=hub_japan`).
- 27 Nov, GigSky added (through Travelpayouts, which only offers ready-made links for it; Sub ID `esim-article-gigsky`): disclosure first (`w67`: Affiliate Disclosure and About), then a short entry in the eSIM comparison's "other providers" list, with only what GigSky itself states (several local networks per country, best one per location; inflight plans). A full review, a table column and GigSky in the title wait for facts from GigSky's own pages (the sandbox cannot open its site). Its Travelpayouts promo must never show the code itself, only the dedicated promo link.
- 27 Nov, GigSky's full review in the eSIM comparison, from GigSky's own Japan page (owner's screenshots; the sandbox cannot open its site): a mobile operator working directly with network partners, connects by itself to the best local network (5G, 4G or LTE), one eSIM for 200+ countries and 290+ cruise ships, fixed or unlimited plans with an 80% usage alert, unlimited hotspot sharing, activation in under 2 minutes on average by its own account. Added as a table column (its Japan price in the table only), a decision card (frequent travellers and cruises), a verdict line, the section menu, and the title ("…Yesim, Airalo, Saily, GigSky, Maya and Jetpac Compared"); the short "other providers" entry is removed.
- 27 Nov, eSIM comparison checked for what could upset a brand (owner asked): the China FAQ no longer says Yesim's VPN or Saily's security features help reach blocked apps (a legal grey area, and wrong for Saily), only to check each provider's China page; unverified or changeable facts removed or hedged (Airalo "no unlimited option" now "mainly fixed-data plans, check your destination"; Saily "no identity verification" removed; Yesim's 512kbps after 1-3GB now "a daily amount that varies by plan", also in the table and FAQ; the 1GB-lasts estimate labelled as ours); unsourced price comparisons about Holafly, Nomad and Ubigi replaced with neutral descriptions; tone: Saily's "shorter track record", Yesim "an easy default".
- 27 Nov, a tester's review: (1) `w83` adds share tags (og: and Twitter summary card, the guide's own 512px icon) to all 10 Pocket Guides, which are shared on WhatsApp but showed no title or picture; they stay noindex with canonicals to their blog guides, which is why no Pocket Guide is in the sitemap (intended). (2) The hub's Plan section ends with a "Build your day-by-day Japan plan" card (Plan My Trip with Japan filled in, `?src=hub_plan`); Packy stays the hub's main action. (3) `w84` adds the departure tax (JNTO: visitors pay 3,000 yen; no start date, since it could not be confirmed on an official page here) and cherry blossoms 2027 (no forecast yet; JMA average first-bloom dates for Tokyo, Kyoto, Osaka and Sapporo) to the Japan travel guide's quick-facts box, the from-India guide and the 7-day itinerary. Not done: social links and `sameAs` (only once there are active profiles), and a Japan-specific share image (with the Fuku illustrations).
- 27 Nov, share buttons beyond the articles (owner: the tester meant links to share the page, not our social profiles): `w85` adds the articles' share row (WhatsApp, X, Facebook, LinkedIn, Pinterest, copy link, same icons) to the Japan hub (before the footer), Travel Essentials (after the intro) and Fuku's Phrasebook (in its closing box), plus a "📤 Share" button that opens the phone's own share sheet where the browser offers one. Shared links carry `?src=share_japan`, `share_essentials` and `share_phrasebook`; clicks send GA4 `share_row` with the network. PackSmart's own social profiles (footer and `sameAs`) follow when the accounts are ready.

## Open decisions (not made)

- Install sheet: stop it opening by itself on first visit (`AUTO_INSTALL_SHEET`)? Recommended, owner has not said yes.
- Haruka price wording on the Kansai and Osaka guides.
- Whether to keep the Terminals tab (watch the `pg_tab` count for it).
- No airport outside Japan before spring 2027 (D48).
- Email capture: whether and how it returns.
- Whether to add a native-speaker check for the Japanese phrases before promoting the guides.
