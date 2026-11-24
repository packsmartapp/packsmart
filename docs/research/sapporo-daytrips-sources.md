# Day trips from Sapporo by train + ski buses from New Chitose Airport: sources and facts

Research for the Sapporo Station Pocket Guide ("Day trips from Sapporo by train") and the New Chitose Airport (CTS) guide (ski buses).
Started 24 Nov 2026. Every fact names its source; all fetched 24 Nov 2026 from the cloud sandbox ("checked 24 Nov 2026").
No prices are carried over on purpose (they go stale; the blocks carry them).
Local copies of the pages, PDFs and timetable JSON are in `dl/` next to this file (file names in brackets).

**How the timetable facts were read.** The JR station timetable page
`https://www3.jrhokkaido.co.jp/webunkou/timetable_en.html?id=<station>` is filled by JavaScript from JSON files on the same
host: `json/timetable/core/<id>_core_en.json` (departures for "today" and "tomorrow") and
`json/daiya/daiya_<line>_en.json` (stop-by-stop times, the same data the page shows when you click a time cell).
Journey times below are computed from those stop times for **Tue 24 Nov 2026** (Wed 25 Nov is identical for Sapporo).
Station ids: Sapporo 091, Otaru 076, Noboribetsu 205, Shiraoi 210, Asahikawa 118, Biei 507, Furano 500, Naka-Furano 503,
Takikawa 111, Kutchan 068, Niseko 066, New Chitose Airport 246. [core091_en.json, daiya_00/02/05/06/09_en.json]
Timetables change (JR's next big change was 14 Mar 2026; the winter-only changes are listed below), so print
"checked 24 Nov 2026" next to any time and link the station timetable.

---

## ALL DESTINATIONS: rules that apply to every limited express

- "From March 14, 2026, all seats will be reserved on all limited express trains in Hokkaido. There are no non-reserved seats.
  When boarding, a reserved seat limited express ticket is required in addition to a basic fare ticket."
  "Passengers without a seat number may need to stand. If there are vacant seats in the ordinary cars, you may use them
  temporarily. However, if a passenger with a reserved seat ticket comes, you will need to move to another seat."
  Source: https://www.jrhokkaido.co.jp/CM/Info/notice_en/pdf/all_reserved_202602_en.pdf (linked from
  https://www.jrhokkaido.co.jp/CM/Info/notice_en/index.html, dated 2026.02.05), checked 24 Nov 2026. [notice_en_pdf_all_reserved_202602_en.pdf]
- The list of all-reserved limited expresses includes "Ltd. Exp. Suzuran (Sapporo – Noboribetsu – Higashi-Muroran)",
  "Ltd. Exp. Kamui / Lilac (Sapporo – Asahikawa)", "Ltd. Exp. Hokuto (Sapporo – Hakodate)" and
  "Furano Lavender Express (Sapporo – Takikawa – Furano)".
  Rail pass holders: "Please make sure to receive a reserved seat ticket in advance. You cannot assign seats on the train."
  If the train is full, a pass holder "can take the train only with your rail pass (a reserved seat ticket not required)" and
  "may stand on the train except in the Green Car".
  Source: https://www.jrhokkaido.co.jp/global/english/ticket/usage/usage03.html, checked 24 Nov 2026. [english_ticket_usage_usage03.html]
- New from 1 Dec 2026: "Limited Express E-tickets will be available for the Limited Express Kamui and Lilac operating between
  Sapporo and Asahikawa", bought through JR-EAST Train Reservation; "simply tap your IC card such as Suica or Kitaca or Mobile
  Suica at the automatic ticket gate". Sales "From 10 am one month before the boarding date until the departure time".
  Source: https://www.jrhokkaido.co.jp/CM/Info/news_en/pdf/ltdexp_eticket_202611_en.pdf (news dated 2026.11.19), checked 24 Nov 2026. [news_en_pdf_ltdexp_eticket_202611_en.pdf]
- Rapid Airport (the Sapporo–Otaru train): "6 cars in total, only Car No. 4 is reserved"; "Cars 1-3 and 5-6 Non-reserved
  Seats … No reservation required". IC cards such as Suica work between the airport and Otaru; "For Yoichi, Kutchan, Niseko
  IC cards such as Suica cannot be used. Please purchase your ticket at the station before boarding."
  Source: https://www.jrhokkaido.co.jp/global/english/travel/airport.html and
  https://www.jrhokkaido.co.jp/global/english/train/guide/muroran.html, checked 24 Nov 2026. [english_travel_airport.html, train_guide_muroran.html]
  (JR's recommended-route pages label the Rapid Airport "(Reserved)" because they assume the Car 4 seat; it is not compulsory.)
- Journey times on JR's recommended routes: "*Travel time is an approximate time. It differs depending on the train and the
  time of the day." Source: https://www.jrhokkaido.co.jp/global/english/travel/model/noboribetsu.html, checked 24 Nov 2026.
- Local buses are never covered by the two area passes: "The Sapporo-Noboribetsu Area Pass and Sapporo-Furano Area Pass cannot
  be used for buses." Source: https://www.jrhokkaido.co.jp/global/english/faq/faq04.html, checked 24 Nov 2026. [faq_faq04.html]

### Rail passes (which pass covers which day trip)
Source for all bullets: https://www.jrhokkaido.co.jp/global/english/ticket/railpass/index.html, checked 24 Nov 2026
(valid-area maps `images/ticket/railpass/e-rail02.png` and `e-rail03.png` on the same page, viewed).
[https___www.jrhokkaido.co.jp_global_english_ticket_railpass_index.html, e-rail02.png, e-rail03.png]
- **Sapporo-Noboribetsu Area Pass**: 4 consecutive days; "convenient for travel between New Chitose Airport, Sapporo, Otaru and
  Noboribetsu". Map: Otaru – Sapporo – Hokkaido-Iryodaigaku, Sapporo – Iwamizawa, Sapporo – New Chitose Airport/Minami-Chitose –
  Shiraoi – Noboribetsu. "Toya is not included." Sold/exchanged only at New Chitose Airport, Sapporo and Noboribetsu stations.
  **Covers: Otaru, Shiraoi (Upopoy), Noboribetsu. Not Asahikawa, Biei, Furano or Niseko.**
- **Sapporo-Furano Area Pass**: 4 consecutive days; "convenient for travel between New Chitose Airport, Sapporo, Otaru, Furano,
  Biei and Asahikawa". Map: Otaru – Sapporo – Bibai – Takikawa – Asahikawa, Takikawa – Furano – Biei – Asahikawa, Sapporo –
  New Chitose Airport. "Tomamu is not included." Sold/exchanged only at New Chitose Airport, Sapporo and Asahikawa stations.
  **Covers: Otaru, Asahikawa, Biei, Furano. Not Noboribetsu or Niseko.**
- **Hokkaido Rail Pass**: 5, 7 or 10 consecutive days; "unlimited rides on all JR Hokkaido Lines (except Hokkaido Shinkansen)".
  **Covers all five day trips, and Niseko.** It also covers some JR Hokkaido Bus routes, incl. "an express bus between Sapporo
  and Otaru. (Limited to JR Hokkaido Bus. Chuo Bus is not available.)" (https://www.jrhokkaido.co.jp/global/pdf/e-railpass-busroute.pdf, Dec 2024)
- All three: "The rail pass cannot be used for JR Hokkaido Bus [area passes], the streetcar and the subway in Sapporo";
  "All non-Japanese passport holders can use the rail passes"; reserved seats in ordinary cars included.
- Passport-reader ticket machines (from 20 Oct 2026): Sapporo Station 3 machines (2 West Concourse, 1 East Concourse),
  5:30–23:50; New Chitose Airport Station 1 machine next to the JR Information Desk, 7:00–22:00. Same page.

---

## 1. OTARU

- **Train:** Rapid Airport runs through from Sapporo to Otaru. JR route: "Sapporo Sta – 35min Rapid Airport – Otaru Sta".
  Source: https://www.jrhokkaido.co.jp/global/english/travel/model/noboribetsu.html (Day 2) and
  https://www.jrhokkaido.co.jp/global/english/travel/model/furano.html (Day 4), checked 24 Nov 2026. [model_noboribetsu.html, model_furano.html]
- Airport page: "Some trains run directly from New Chitose Airport to Otaru"; "73 mins to Otaru (fastest)" from the airport.
  Source: https://www.jrhokkaido.co.jp/global/english/travel/airport.html, checked 24 Nov 2026.
- **Timetable, Sapporo → Otaru, 24 Nov 2026** (station timetable id=091 + daiya_05/06):
  - Rapid / Special Rapid Airport to Otaru: every 30 min from 09:10 to 16:30 (Special Rapid at :30, 34–35 min; Rapid at :00,
    about 41 min), then 17:11, 17:40, 18:09, 18:40, 19:12, 19:38, 20:17, 21:05, last 22:53 (34–46 min).
  - Local trains Sapporo → Otaru: 47 departures, first 06:28, last 23:50; about 45–55 min.
  - Otaru → Sapporo by Rapid/Special Rapid Airport: first 05:51, then roughly every 30 min 09:22–19:56 (last Rapid 19:56);
    local trains run later.
  Source: https://www3.jrhokkaido.co.jp/webunkou/timetable_en.html?id=091 and https://www3.jrhokkaido.co.jp/webunkou/timetable_en.html?id=076, checked 24 Nov 2026.
- **Seats/IC:** no limited express on this route; Rapid Airport mostly unreserved (Car 4 reserved); IC cards work to Otaru (see above).
- **Passes:** in both area passes and the Hokkaido Rail Pass (see Rail passes).
- **If trains stop:** JR lists a bus alternative Sapporo – Otaru "Approx. 60–80 min" (boarding around Sapporo Station and around
  Otaru Station); "Travel time may increase or services may be suspended depending on weather and road conditions."
  Source: https://www.jrhokkaido.co.jp/global/english/travel/airport_disruption.html, checked 24 Nov 2026. [travel_airport_disruption.html]
- **Winter:** JR lists "Otaru Snow Light Path (Early to mid Feb)" on its Otaru day.
  Source: https://www.jrhokkaido.co.jp/global/english/travel/model/noboribetsu.html, checked 24 Nov 2026. (Exact 2027 dates: Gap.)
- Onward step in Otaru: JR shows "Minami-Otaru Station" and "Otaru Canal" photos but gives no walking time. Gap.

## 2. NOBORIBETSU (and Shiraoi / Upopoy on the way)

- **Train:** Limited Express Suzuran (Sapporo – Higashi-Muroran/Muroran) or Hokuto (Sapporo – Hakodate), all seats reserved.
  JR route: "Noboribetsu Sta – 1hr 15min Ltd. Exp. Hokuto/Suzuran (Reserved) – Sapporo Sta"; another JR route gives
  "Sapporo Sta – 1hr 20min Ltd. Exp. Suzuran (Reserved) – Noboribetsu Sta".
  Source: https://www.jrhokkaido.co.jp/global/english/travel/model/noboribetsu.html (Day 4) and
  https://www.jrhokkaido.co.jp/global/english/travel/model/winter03.html (Day 7), checked 24 Nov 2026. [model_noboribetsu.html, model_winter03.html]
- **Timetable, Sapporo → Noboribetsu, 24 Nov 2026** (computed from daiya_00): 16 limited expresses stop, 70–82 min.
  First 06:53 (Hokuto No.4, arr 08:03), then 07:30 Suzuran 2, 08:43, 09:21, 09:45, 10:56, 12:09, 13:26, 13:46, 14:46, 15:45,
  16:07, 16:51, 18:46, 19:14, last 21:12 (Suzuran 12, arr 22:26). Note: Hokuto No.2 (06:00) does not stop at Noboribetsu.
  **Back, Noboribetsu → Sapporo:** first 05:54, last limited express 21:21 (Hokuto 21, arr Sapporo 22:41); a local at 20:45 takes 2 h 25 min.
  Source: https://www3.jrhokkaido.co.jp/webunkou/timetable_en.html?id=091 and https://www3.jrhokkaido.co.jp/webunkou/timetable_en.html?id=205, checked 24 Nov 2026.
- **Onward to Noboribetsu Onsen (hot-spring town):** JR: "Noboribetsu Sta – 20min Bus (*1) – Noboribetsu Hot Springs";
  "*1 Sapporo-Noboribetsu Area Pass does not cover the fares for local bus. Additional charge is required."
  Source: https://www.jrhokkaido.co.jp/global/english/travel/model/noboribetsu.html, checked 24 Nov 2026.
  JNTO: "Noboribetsu Onsen is located around eight kilometers from JR Noboribetsu Station and is best accessed via car or bus
  from the station." Many hotel baths "are open to both overnight guests and day visitors, making it an accessible destination
  even if just for a day trip." Source: https://www.japan.travel/en/destinations/hokkaido/hokkaido/noboribetsu-upopoy-and-around/, checked 24 Nov 2026. [jt_noboribetsu-upopoy-and-around.html]
  Bus operator, its timetable and winter frequency: Gap (operator host blocked).
- **Shiraoi stop for Upopoy (National Ainu Museum and Park):** JR: "Sapporo Sta – 1hr 3min Ltd. Exp. Suzuran – Shiraoi Sta –
  10min On foot – National Ainu Museum and Park"; then "Shiraoi Sta – 18min Local train – Noboribetsu Sta".
  Source: https://www.jrhokkaido.co.jp/global/english/travel/model/noboribetsu.html (Day 3), checked 24 Nov 2026.
  JNTO: "Upopoy is around a 10-minute walk from the North Exit of JR Shiraoi Station." Source: japan.travel page above.
  Timetable note: not every limited express stops at Shiraoi (24 Nov 2026: e.g. 07:30 Suzuran 2 arr 08:32, 08:43 Hokuto 6 arr 09:42).
- **Passes:** Sapporo-Noboribetsu Area Pass or Hokkaido Rail Pass. Not the Sapporo-Furano Area Pass.
- **IC cards:** "IC cards cannot be used" to Noboribetsu (JR FAQ, already in `docs/research/sapporo-sources.md`). Buy a paper ticket.

## 3. ASAHIKAWA (and Asahiyama Zoo)

- **Train:** Limited Express Lilac or Kamui, all seats reserved. JR: "Sapporo Sta – 1hr 25min Ltd. Exp. Lilac/Kamui (Reserved) –
  Asahikawa Sta". Source: https://www.jrhokkaido.co.jp/global/english/travel/model/furano.html (Day 3), checked 24 Nov 2026.
  Train guide: Kamui is a "5 car train", Lilac a "6-car high-speed train", both "【All seats reserved】".
  Source: https://www.jrhokkaido.co.jp/global/english/train/guide/asahikawa.html ("Information is current as of March 2026"), checked 24 Nov 2026. [train_guide_asahikawa.html]
  Sapporo tourism site: "Two limited express trains connecting Sapporo and Asahikawa in 1 hour and 25 minutes the quickest.
  Over 20 round trips operate per day." Source: https://www.sapporo.travel/en/info/about/transportation/, checked 24 Nov 2026. [st_transport.html]
- **Timetable, Sapporo → Asahikawa, 24 Nov 2026** (daiya_00): Lilac/Kamui hourly or half-hourly; first 06:29 (Lilac 1, arr 07:56),
  last 22:00 (Kamui 45, arr 23:25); daytime trains take 85 min. (Okhotsk 06:52 and 15:30 and Soya 07:30 also stop, 90–99 min.)
  **Back:** first 06:00, last 22:00 (Lilac 46, arr Sapporo 23:25); most 85 min.
  Source: https://www3.jrhokkaido.co.jp/webunkou/timetable_en.html?id=091 and https://www3.jrhokkaido.co.jp/webunkou/timetable_en.html?id=118, checked 24 Nov 2026.
- **Asahiyama Zoo onward:** JR: "Asahikawa Sta – 40min Bus (*2) – Asahiyama Zoo"; "*2 Sapporo-Furano Area Pass does not cover the
  fares for local bus." Same in JR's winter route ("Photogenic winter spots", Day 5).
  Sources: https://www.jrhokkaido.co.jp/global/english/travel/model/furano.html and
  https://www.jrhokkaido.co.jp/global/english/travel/model/winter02.html, checked 24 Nov 2026. [model_winter02.html]
  JNTO: "The zoo is a day trip from Sapporo and 40 minutes by bus from Asahikawa Station"; winter highlight "The daily penguin walk
  (held during the snowy season)". Source: https://www.japan.travel/en/spot/1891/, checked 24 Nov 2026. [jt_spot1891.html]
  **Do not use** that page's line about "special Asahikawa Zoo express trains" on weekends: no current JR page mentions such a train.
  JR discontinued the "Asahiyama Zoo Ticket" and "Asahiyama Zoo Access Ticket" (last use 13 Mar 2026).
  Source: https://www.jrhokkaido.co.jp/CM/Info/news_en/pdf/timetable_change_202603_en.pdf, checked 24 Nov 2026.
  Zoo winter opening dates/hours, bus stop and bus number: Gap (zoo and city hosts blocked).
- **Passes:** Sapporo-Furano Area Pass or Hokkaido Rail Pass. Not the Sapporo-Noboribetsu Area Pass.
- **E-ticket option** for Kamui/Lilac from 1 Dec 2026 (see top).

## 4. FURANO and BIEI (winter relevance)

- **No direct train in winter.** The Furano Lavender Express (Sapporo – Iwamizawa – Takikawa – Ashibetsu – Furano, "2 hours with
  no transfer", all seats reserved) runs "June to September 2026" only.
  Source: https://www.jrhokkaido.co.jp/global/english/travel/furanobiei/train/index.html, checked 24 Nov 2026. [fb_train_index.html]
  JR's winter sightseeing-train notice for Jan–Mar 2027 lists only the SL Fuyu-no-Shitsugen, Ryuhyo Monogatari and two AKAIHOSHI
  trains (eastern Hokkaido), **no Furano/Biei train**.
  Source: https://www.jrhokkaido.co.jp/CM/Info/news_en/pdf/winter_train_2026_en.pdf (dated 27 Oct 2026), checked 24 Nov 2026. [news_en_pdf_winter_train_2026_en.pdf]
- **Winter route JR gives:** "You can also go to Biei and Furano via Asahikawa when the Furano Lavender Express is not operated.
  Sapporo (Ltd. Exp. Lilac/Kamui) → Asahikawa (Local train) → Biei (Local train) → Furano (Local train) → Asahikawa (Ltd. Exp.
  Lilac/Kamui) → Sapporo". Source: https://www.jrhokkaido.co.jp/global/english/travel/model/furano.html, checked 24 Nov 2026.
  JR's own winter example ("【Stay overnight in Furano】Farm Tomita in winter", labelled "Winter only" and "A recommended route for
  winter 2025"): Sapporo 10:00 Ltd. Exp. Lilac No.11 → Asahikawa 11:25/11:33 local → Naka-Furano 12:34, "25 min on foot" to Farm
  Tomita; back Furano 11:20 local → Takikawa 12:18/12:32 Ltd. Exp. Lilac No.20 → Sapporo 13:25. The JR page treats it as an
  overnight trip, not a day trip. Source: https://www.jrhokkaido.co.jp/global/english/travel/furanobiei/course/3b.html, checked 24 Nov 2026. [fb_course_3b.html]
  (Those times still match the 24 Nov 2026 timetable.)
- JR FAQ: "The closest station to Farm Tomita is Lavender-Farm Station which is available to use from June to September. For other
  periods, please use Naka-Furano Station. It is a 25-minute walk from there." Furano Line: "the area where you cannot use an IC
  card"; local trains "one-man operated … Only the very front door opens"; pay "by cash" in the fare box with a numbered ticket.
  Source: https://www.jrhokkaido.co.jp/global/english/faq/faq09.html, checked 24 Nov 2026. [faq_faq09.html]
- JR's Biei Blue Pond day trip (bus from Biei Station) is marked "Season without snow accumulation" / "Recommended to visit before
  snow piles up!" Do not offer it as a winter trip. Source: https://www.jrhokkaido.co.jp/global/english/travel/furanobiei/index.html
  and .../furanobiei/course/3a.html, checked 24 Nov 2026. [global_english_travel_furanobiei_index.html, fb_course_3a.html]
- **Local train times, 24 Nov 2026** (daiya_09 and daiya_02):
  - Asahikawa → Biei: 18 trains, 05:44 to 22:34, 33–42 min. Biei → Asahikawa: 06:39 to 21:19, 28–40 min.
  - Biei → Furano: 12 trains, 06:18 to 23:07, 33–44 min. Furano → Biei: 05:59 to 20:47.
  - Asahikawa → Furano (through): 12 trains, 05:44 to 22:34, 66–83 min. Furano → Asahikawa: 05:59 to 20:47, 60–82 min.
    Gaps of up to 2 hours mid-morning (e.g. Biei → Furano nothing between 10:14 and 12:09).
  - Takikawa → Furano: 9 trains, about 58–62 min; Furano → Takikawa: 8 trains, last 21:00 (arr 21:58).
  Sources: https://www3.jrhokkaido.co.jp/webunkou/timetable_en.html?id=118, ?id=507, ?id=500, ?id=111, checked 24 Nov 2026.
  So a Sapporo day trip to Biei only (via Asahikawa) is about 85 + 35 min each way; Biei + Furano in one day is possible but
  depends on these sparse local trains.
- **Passes:** Sapporo-Furano Area Pass or Hokkaido Rail Pass (local buses extra).

## 5. NISEKO by train (optional; weak as a day trip)

- JNTO: Niseko "is accessible from Sapporo or New Chitose International Airport by car, train or bus … There are buses from both
  points and trains via Otaru to Niseko Station." Source: https://www.japan.travel/en/destinations/hokkaido/hokkaido/niseko-and-nearby-ski-resorts/, checked 24 Nov 2026.
- **Timetable, 24 Nov 2026** (daiya_06): no limited express. The only through train is the **Rapid Niseko Liner**: Sapporo 17:50 →
  Otaru 18:43 → Kutchan 19:52 (does not run on to Niseko), and Niseko 06:38 → Otaru 08:05 → Sapporo 08:50. Otherwise change at
  Otaru (and often at Kutchan): Otaru → Niseko direct locals only at 17:46 (arr 19:31) and 19:30 (arr 21:20); Kutchan – Niseko
  about 16–17 min, a handful of trains a day.
  Source: https://www3.jrhokkaido.co.jp/webunkou/timetable_en.html?id=076 and ?id=066, checked 24 Nov 2026.
- IC cards cannot be used to Kutchan/Niseko (see top). Only the Hokkaido Rail Pass covers it.
- Recommendation for the guide: point skiers to the reserved ski buses (Part 2) rather than the train.

## WINTER NOTES (JR)

- JR's winter route pages note: "the information on the events and the season for flowers, autumn leaves and drift ice may change
  depending on the conditions." Source: https://www.jrhokkaido.co.jp/global/english/travel/model/winter02.html, checked 24 Nov 2026.
- JR gives "Sapporo White Illumination (Late Nov to mid March)", "Sapporo Snow Festival (Early to mid Feb)" and "Otaru Snow Light
  Path (Early to mid Feb)" as winter sights. Source: model/winter02.html and model/winter03.html, checked 24 Nov 2026.
- Delays: JR's live status pages: https://www3.jrhokkaido.co.jp/webunkou/area_spo_en.html (Sapporo area) and
  https://www3.jrhokkaido.co.jp/webunkou/area_doo_en.html (Central Hokkaido). On delays and cancellations JR says it does "not
  refund or compensate for meals, or other transportation fares, lodging fees". Source:
  https://www.jrhokkaido.co.jp/global/english/faq/faq10.html, checked 24 Nov 2026. A delay certificate "can be issued upon request
  at the station". Source: travel/airport_disruption.html.
- No JR English page found that states a general winter-delay warning (e.g. snow suspensions on the Furano Line). Gap.

---

## PART 2: SKI BUSES FROM NEW CHITOSE AIRPORT

### What the airport says
- Bus page, "Platform Information For Other Buses": "Ski Bus: Niseko / Rusutsu – Niseko Bus – [View the timetable →
  https://www.nisekobus.co.jp/timetable/] – 12 [domestic] – ー [international]" and "Ski Bus operates in winter only."
  "Furano – HOKKAIDO BUS – [http://www.hokkaidoubus-newstar.jp/furano] – 23 – ー".
  Contacts: Niseko Bus TEL 0136-44-2001, https://www.nisekobus.co.jp/; HOKKAIDO BUS TEL 011-888-7600, http://www.hokkaidoubus-newstar.jp/.
  Source: https://www.hokkaido-airports.com/en/new-chitose/access/bus/, checked 24 Nov 2026. [cts_bus.html]
- Both timetable hosts refuse the sandbox (proxy 403), re-tested 24 Nov 2026. **Times, journey times, reservation rules and
  2026–27 dates for these two buses are a Gap.**

### Hokkaido Chuo Bus (www.chuo-bus.co.jp, reachable)
- Ski bus page lists three reserved ski routes for 2026–27:
  - "札幌⇔ニセコ線 予約制 運行期間：2026年12月12日 ～ 2027年3月22日" (Sapporo ⇔ Niseko, reservation required, runs 12 Dec 2026 – 22 Mar 2027)
  - "千歳⇔ニセコ線 予約制 運行期間：2026年12月12日 ～ 2027年3月22日" (Chitose ⇔ Niseko, reservation required, same dates)
  - "札幌都心⇔札幌国際スキー場 予約制 運行期間：2026年11月20日 ～ 2027年5月5日（スキー場オープン日より運行）" (central Sapporo ⇔
    Sapporo Kokusai ski area, reservation required, 20 Nov 2026 – 5 May 2027, from the ski area's opening day)
  - Rule: "スキー、スノーブーツでのご乗車はできません。スキー・スノーボードは専用の袋やケースに入れるか…" (no boarding in ski boots;
    skis and boards in a bag/case or bound together).
  - Details for each are on https://teikan.chuo-bus.co.jp/course/18958 (Niseko) and https://teikan.chuo-bus.co.jp/course/16756
    (Sapporo Kokusai) — **host blocked**, so times, stops (incl. whether "Chitose" means the airport and which airport stop) are a Gap.
  Source: https://www.chuo-bus.co.jp/feature/ski/, checked 24 Nov 2026. [chuo_ski.html]
- Live suspension list for ski buses exists: https://www.chuo-bus.co.jp/support/stop/?ope=list&g=20 (on 24 Nov 2026 08:56 it showed
  the Sapporo Kokusai line suspended because the ski area closed for strong wind; a snapshot, not for the guide). [chuo_stop_ski.html]
- **Winter airport timetable status:** Chuo Bus changes to its winter timetable on **Fri 11 Dec 2026** (moved from the usual 1 Dec
  "積雪状況や道路交通環境の変化を踏まえた対応"). The main item: "新千歳空港連絡バス 札幌都心線のリニューアル" (Sapporo city-centre airport
  bus renewed: routes and stops change). Detailed timetables were to be published "11 月中旬以降" (from mid-November).
  Source: notice PDF dated 30 Oct 2026, https://www.chuo-bus.co.jp/%E4%BB%A4%E5%92%8C%EF%BC%98%E5%B9%B412%E6%9C%8811%E6%97%A5%08%E9%87%91%09%E5%86%AC%E3%83%80%E3%82%A4%E3%83%A4%E6%94%B9%E6%AD%A3%E3%81%AE%E3%81%8A%E7%9F%A5%E3%82%89%E3%81%9B/main_info/2417 (serves a PDF; linked from
  the Chuo Bus home page as "令和８年12月11日（金）冬ダイヤ改正のお知らせ", 2026.11.02), checked 24 Nov 2026. [chuo_winter_dia_20261211.pdf]
  The airport-bus page https://www.chuo-bus.co.jp/feature/airport/ (Chuo Bus and Hokuto Kotsu) says "2026年12月11日より札幌都心便を
  3つのルートに再編" (from 11 Dec 2026 the city-centre service becomes three routes: Sapporo Station/Susukino, city hotels loop,
  Susukino direct) and "予約なしでOK" (no reservation needed); it already carries the timetables (not transcribed here; that is CTS
  guide work, not ski buses). The older page https://www.chuo-bus.co.jp/airport/ still shows "2026年4月1日更新（夏ダイヤ）" (summer timetable).
  Checked 24 Nov 2026. [chuo_feature_airport.html, chuo_airport.html]
- Not found on Chuo Bus: any Rusutsu, Kiroro or Furano ski bus.

---

## Gaps
| Item | Why | Where it would be |
|---|---|---|
| Niseko Bus ski bus from CTS stop 12: dates, times, journey time, booking | host blocked | https://www.nisekobus.co.jp/timetable/ |
| Hokkaido Bus Furano bus from CTS stop 23: times, winter dates, booking | host blocked | http://www.hokkaidoubus-newstar.jp/furano |
| Chuo Bus Niseko ski buses (Sapporo and Chitose): times, stops, journey time, how to book | host blocked | https://teikan.chuo-bus.co.jp/course/18958 |
| Rusutsu ski bus details (operator, times) | only the airport's one-line listing; resort host blocked | https://www.rusutsu.com/ |
| Noboribetsu Station → Onsen bus: operator, stop, timetable, winter frequency | JR gives only "20min Bus"; operator host blocked | https://www.donanbus.co.jp/ |
| Asahiyama Zoo winter season dates, hours, bus number/stop at Asahikawa Station | zoo/city hosts blocked | https://www.city.asahikawa.hokkaido.jp/asahiyamazoo/ |
| Otaru Snow Light Path 2027 exact dates; walking time station → canal | JR gives "Early to mid Feb" only; Otaru tourism host blocked | https://otaru.gr.jp/ |
| Sapporo Snow Festival 2027 dates | www.snowfes.com/en/ still shows the 2025 period | https://www.snowfes.com/en/ (re-check later) |
| JR "Access Map to Major Sightseeing Spots" PDF (Sep 2026) | text uses fonts that do not extract or render in the sandbox; the map is readable only as pictures without station names or times | https://www.jrhokkaido.co.jp/global/pdf/e-AccessMap.pdf (Ari to look on a real device) |
| JR general winter-delay warning in English | none found on the English pages read | — |
| Weekend/holiday timetables | only 24–25 Nov 2026 (weekdays) were read | JR station timetable pages |
| Furano/Biei tourism facts in winter (Biei bus, Furano ski area access) | tourism hosts blocked | https://www.biei-hokkaido.jp/en/, https://www.furanotourism.com/en/ |

## Blocked hosts (proxy 403, 24 Nov 2026)
Ask Ari to approve the ones that matter (first three are the ski-bus timetables):
- `www.nisekobus.co.jp`
- `www.hokkaidoubus-newstar.jp`
- `teikan.chuo-bus.co.jp`
- `www.donanbus.co.jp` (Noboribetsu bus)
- `www.city.asahikawa.hokkaido.jp` (Asahiyama Zoo)
- `www.asahiyamazoo-asahikawa.jp` (guessed zoo host; also refused)
- `otaru.gr.jp`
- `www.noboribetsu-spa.jp`
- `www.furanotourism.com`, `www.biei-hokkaido.jp`, `www.furanobus.jp`, `www.atca.jp`
- `www.niseko-ta.jp`, `www.niseko.ne.jp`, `www.rusutsu.com`
- `www.visit-hokkaido.jp`
- Also refused when probed (no fact depended on them): `www.niseko-bus.co.jp`, `www.hokkaido-bus.co.jp`, `www.hokkaidobus.co.jp`,
  `www.asahikawabus.co.jp`, `www.dohokubus.com`, `www.jhb.jp`, `resortliner.com`.
Reachable: www.jrhokkaido.co.jp, www3.jrhokkaido.co.jp, www.chuo-bus.co.jp, www.sapporo.travel, www.japan.travel,
www.hokkaido-airports.com, www.snowfes.com.
