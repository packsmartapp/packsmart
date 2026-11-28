#!/usr/bin/env python3
"""
w86: Japan trip budget calculator, /japan-budget (27 Nov 2026; launched the same day).

Owner's idea: Packy gets "total cost for a family of 4, 10 days, mostly Tokyo" questions; a calculator where the
reader enters their trip and gets an itemised result fits them better than the itinerary planner.

How it works: the reader enters travellers (adults, children 6-11, under 6), nights per area (Tokyo, Kyoto/Osaka,
Hokkaido), the airports, how they get into town, taxi rides, and (optionally) their own hotel, food and flight
figures. The result lists:
  - costs we have CHECKED prices for, each with its official source and checked date (all from
    docs/research/japan-prices-sources.md, checked 24 Nov 2026): airport to city, Tokyo and Sapporo transport day
    tickets, taxis (JNTO's range), the Japan Rail Pass, the departure tax;
  - costs the reader typed in (hotel, food, flights);
  - costs not priced yet (flights unless typed, theme parks and zoos, Kyoto and Osaka city transport, regular
    Shinkansen fares), each with a way to find the price (internal page or partner link).
The total says what it covers. No made-up numbers: anything without an official figure says "not priced yet".

Partner links use the page's own Travelpayouts Sub IDs: budget-esim (eSIM) and budget-transfer (airport transfer), 28 Nov 2026.
Writes public/japan-budget.html. Run after w85 and before w72:  python3 tools/w86_japan_budget.py
"""
import json, os, re

PUB = os.path.join(os.getcwd(), "public")
# Guided multi-day tours (TourRadar): off until TourRadar confirms the links credit the PackSmartApp partner account
# and allows naming them on /affiliate-disclosure (their terms, 6.6). When on, also add TourRadar to w67 and set
# the "multitour" offer in api/_offers.js to on.
TOURS_ON = True
CHECKED = "24 Nov 2026"

# "Flying from": cities whose travellers often visit Japan, grouped by region. Codes are Travelpayouts city codes
# (metro codes where a city has several airports). api/flight-price.js only accepts these; w86 checks they match.
FROM = [
    ("Southeast Asia", [("SIN", "Singapore"), ("KUL", "Kuala Lumpur"), ("BKK", "Bangkok"), ("JKT", "Jakarta"), ("DPS", "Bali (Denpasar)"),
                        ("MNL", "Manila"), ("SGN", "Ho Chi Minh City"), ("HAN", "Hanoi")]),
    ("East Asia", [("HKG", "Hong Kong"), ("TPE", "Taipei"), ("SEL", "Seoul"), ("PUS", "Busan"), ("SHA", "Shanghai"), ("BJS", "Beijing")]),
    ("South Asia", [("BOM", "Mumbai"), ("DEL", "Delhi"), ("BLR", "Bengaluru"), ("MAA", "Chennai"), ("HYD", "Hyderabad"), ("CCU", "Kolkata"),
                    ("CMB", "Colombo"), ("KTM", "Kathmandu"), ("DAC", "Dhaka")]),
    ("Australia and New Zealand", [("SYD", "Sydney"), ("MEL", "Melbourne"), ("BNE", "Brisbane"), ("PER", "Perth"), ("AKL", "Auckland")]),
    ("Middle East", [("DXB", "Dubai"), ("AUH", "Abu Dhabi"), ("DOH", "Doha"), ("RUH", "Riyadh"), ("IST", "Istanbul")]),
    ("Europe", [("LON", "London"), ("PAR", "Paris"), ("FRA", "Frankfurt"), ("MUC", "Munich"), ("BER", "Berlin"), ("AMS", "Amsterdam"),
                ("ZRH", "Zurich"), ("VIE", "Vienna"), ("MAD", "Madrid"), ("BCN", "Barcelona"), ("ROM", "Rome"), ("MIL", "Milan"),
                ("HEL", "Helsinki"), ("WAW", "Warsaw")]),
    ("North America", [("LAX", "Los Angeles"), ("SFO", "San Francisco"), ("SEA", "Seattle"), ("NYC", "New York"), ("CHI", "Chicago"),
                       ("HNL", "Honolulu"), ("YVR", "Vancouver"), ("YTO", "Toronto")]),
]

# Every price here is copied from docs/research/japan-prices-sources.md (official pages). [adult, child 6-11] in yen.
DATA = {
    "airport": {
        "narita": {"name": "Narita", "ways": [
            {"id": "skyliner", "k": "train", "s": "Keisei Skyliner", "q": "keisei skyliner", "name": "Keisei Skyliner to Ueno / Nippori", "a": 2580, "c": 1290, "src": "Keisei", "url": "https://www.keisei.co.jp/keisei/tetudou/skyliner/us/skyliner/purchase.php"},
            {"id": "nex", "k": "train", "s": "Narita Express", "q": "narita express", "name": "Narita Express round-trip ticket", "a": 5200, "c": 2600, "src": "JR East N'EX TOKYO Round Trip Ticket", "url": "https://www.jreast.co.jp/en/multi/pass/nex.html"},
            {"id": "limo", "k": "bus", "s": "Limousine Bus to Tokyo Station", "q": "airport limousine bus", "name": "Airport Limousine Bus to Tokyo Station", "a": 3100, "c": 1550, "src": "Airport Limousine Bus", "url": "https://www.limousinebus.co.jp/en/timetable/detail/Narita-Tokyo/?dir=1"},
            {"id": "taxi", "k": "taxi", "s": "Fixed-fare taxi", "name": "Fixed-fare taxi to Shinjuku, Shibuya, Minato (zone D)", "car": [31500, 32500], "src": "Narita Airport (plus expressway tolls; late-night surcharge)", "url": "https://www.narita-airport.jp/en/access/taxi/"},
        ]},
        "haneda": {"name": "Haneda", "ways": [
            {"id": "limo", "k": "bus", "s": "Limousine Bus to Tokyo Station", "q": "airport limousine bus", "name": "Airport Limousine Bus to Tokyo Station", "a": 1200, "c": 600, "src": "Airport Limousine Bus", "url": "https://www.limousinebus.co.jp/en/timetable/detail/Haneda-Tokyo/?dir=1"},
            {"id": "limo2", "k": "bus", "s": "Limousine Bus to Shinjuku", "q": "airport limousine bus", "name": "Airport Limousine Bus to Shinjuku", "a": 1400, "c": 700, "src": "Airport Limousine Bus (daytime)", "url": "https://www.limousinebus.co.jp/en/timetable/detail/Haneda-Shinjuku/?dir=1"},
            {"id": "keikyu", "k": "train", "s": "Keikyu train", "name": "Keikyu train to Shinagawa", "a": 330, "c": None, "src": "Keikyu (adult fare; child fare not checked)", "url": "https://www.haneda-tokyo-access.com/en/ride/fares.html"},
        ]},
        "kansai": {"name": "Kansai (KIX)", "ways": [
            {"id": "haruka-k", "k": "train", "s": "HARUKA to Kyoto", "q": "haruka express", "name": "HARUKA to Kyoto (visitor one-way ticket, bought online)", "a": 2700, "c": 1350, "src": "JR West", "url": "https://www.westjr.co.jp/travel-information/en/tickets-passes/oneway/haruka/"},
            {"id": "haruka-o", "k": "train", "s": "HARUKA to Shin-Osaka", "q": "haruka express", "name": "HARUKA to Shin-Osaka (visitor one-way ticket, bought online)", "a": 1900, "c": 950, "src": "JR West", "url": "https://www.westjr.co.jp/travel-information/en/tickets-passes/oneway/haruka/"},
        ]},
        "chitose": {"name": "New Chitose (Sapporo)", "ways": [
            {"id": "bus", "k": "bus", "s": "Airport bus", "name": "Airport bus to Sapporo Station", "a": 1500, "c": 750, "src": "Hokkaido Chuo Bus", "url": "https://www.chuo-bus.co.jp/airport/timetable/?ope=det&n=34&o=2&t=14"},
        ]},
    },
    "tokyoTicket": {"a": 2000, "c": 1000, "days": 3, "src": "Tokyo Subway Ticket, 72 hours (Toei and Tokyo Metro)", "url": "https://www.kotsu.metro.tokyo.jp/eng/tickets/"},
    "kyotoDay": {"a": 1100, "c": 550, "src": "Kyoto Subway & Bus One-Day Pass (city subway and buses)", "url": "https://www.city.kyoto.lg.jp/kotsu/"},
    "osakaDay": {"lo": 620, "hi": 820, "c": 310, "src": "Osaka Metro / Osaka City Bus 1-day pass (weekends 620 yen, weekdays 820 yen)", "url": "https://subway.osakametro.co.jp/en/"},
    "sapporoDay": {"a": 830, "c": 420, "src": "Sapporo subway one-day ticket (weekday)", "url": "https://www.city.sapporo.jp/st/s109/23564.html"},
    "taxi": {"lo": 2500, "hi": 3000, "src": "JNTO: a 7 km daytime ride in Tokyo, about 25 minutes", "url": "https://www.japan.travel/en/plan/getting-around/taxis/"},
    "jrpass": {"a": 50000, "c": 25000, "src": "Japan Rail Pass, 7 days, ordinary, bought online", "url": "https://japanrailpass.net/en/purchase/price/"},
    "disney": {"lo": 10900, "hi": 12400, "src": "Tokyo Disney Resort 1-Day Passport, adult, by date (28 Nov to 5 Dec 2026 shown)", "url": "https://www.tokyodisneyresort.jp/en/", "checked": "27 Nov 2026"},
    "disneyChild": {"j": 10200, "c": 5900, "src": "juniors 12 to 17 about 10,200 yen, children 4 to 11 about 5,900 yen, from a ticket seller's listing for 28 Nov 2026", "checked": "27 Nov 2026"},
    "sanrio": {"lo": 3400, "hi": 4900, "src": "Sanrio Puroland 1-day ticket, age 3 and up: retail 4,900 yen, 3,400 to 3,600 yen discounted on a ticket seller's site", "checked": "27 Nov 2026"},
    "usj": {"a": 8400, "src": "Universal Studios Japan 1 Day Studio Pass: adult from 8,400 yen incl. tax; prices vary by date", "url": "https://www.usj.co.jp/web/en/us", "checked": "28 Nov 2026"},
    "shibuyasky": {"lo": 2700, "hi": 3400, "c": 1200, "src": "Shibuya Sky: 12 and over 2,700 yen before 15:00, 3,400 yen from 15:00 (web); children 1,200 yen at the counter on the day; under 6 free", "url": "https://www.shibuya-scramble-square.com/sky/", "checked": "28 Nov 2026"},
    "skytree": {"alo": 1800, "ahi": 3000, "clo": 900, "chi": 1500, "src": "Tokyo Skytree: 15 and over from 1,800 yen (Tembo Deck) to from 3,000 yen (both decks); 6 to 14 from 900 to 1,500 yen; 5 and under free", "url": "https://www.tokyo-skytree.jp/en/", "checked": "28 Nov 2026"},
    "ghibli": {"a": 1000, "t": 700, "c": 400, "i": 100, "src": "Ghibli Museum, Mitaka: 19 and over 1,000 yen, 13 to 18 700 yen, 7 to 12 400 yen, 4 to 6 100 yen, 3 and under free; advance reservation only", "url": "https://www.ghibli-museum.jp/en/", "checked": "28 Nov 2026"},
    "uenozoo": {"a": 600, "src": "Ueno Zoo: general 600 yen, junior high 200 yen, free up to 6th grade", "url": "https://www.tokyo-zoo.net/english/ueno/", "checked": "27 Nov 2026"},
    "shinkansen": {"a": 13970, "c": 6980, "src": "Smart EX Service, Nozomi, reserved seat, normal season (off-peak 200 yen less, busiest 400 yen more; children half that)", "url": "https://smart-ex.jp/en/", "checked": "27 Nov 2026"},
    "shinkansenOsaka": {"a": 14520, "c": 7250},
    "hotelStyles": {
        "budget": {"name": "Budget", "desc": "business hotels and simple twin rooms", "by": {"nt": [10000, 18000], "nk": [9000, 16000], "no": [8000, 14000], "nh": [7000, 12000]}},
        "mid": {"name": "Mid-range", "desc": "3-star and good business hotels", "by": {"nt": [18000, 35000], "nk": [16000, 30000], "no": [14000, 25000], "nh": [12000, 22000]}},
        "upscale": {"name": "Upscale", "desc": "4-star hotels, including the Disney partner hotels", "by": {"nt": [35000, 70000], "nk": [30000, 60000], "no": [25000, 50000], "nh": [22000, 45000]}},
        "luxury": {"name": "Luxury", "desc": "5-star hotels and top ryokan", "by": {"nt": [80000, 150000], "nk": [70000, 130000], "no": [60000, 110000], "nh": [50000, 100000]}}},
    "foodStyles": {
        "budget": {"name": "Budget", "desc": "convenience stores, bakeries and casual chains (ramen, curry, gyudon)", "lo": 3000, "hi": 5000},
        "mid": {"name": "Mid-range", "desc": "a cafe lunch and an izakaya or family restaurant dinner", "lo": 5000, "hi": 9000},
        "treat": {"name": "Treat yourself", "desc": "sit-down sushi, wagyu or kaiseki dinners", "lo": 12000, "hi": 20000}},
    "styleNote": "a rough guide (November 2026); prices rise in cherry blossom season, Golden Week, New Year and ski season",
    "foodNote": "a rough guide (November 2026)",
    "areaNames": {"nt": "Tokyo", "nk": "Kyoto", "no": "Osaka", "nh": "Hokkaido"},
    # Partner prices in US dollars, as the site already shows them (28 Nov 2026): the Japan eSIM plan tiles on the
    # Japan guides, and SafetyWing's own "from around $2 a day for travelers under 40 (roughly $56-63 per 4 weeks)".
    # Converted at a round rate so the total stays in yen; the line says so. Update usdJpy if the yen moves a lot.
    "usdJpy": 155,
    "inrJpy": 1.8,   # rough, stated on the page; update with usdJpy
    "esim": {"plans": [[3, 1, 4.0], [7, 3, 8.0], [15, 5, 10.5]], "src": "our Japan eSIM partner's plans as listed on our Japan guides"},
    "insurance": {"lo": 2.0, "hi": 2.25, "src": "SafetyWing: from around US$2 a day for travellers under 40 (about US$56 to 63 per 4 weeks); it rises with age"},
    "tax": {"each": 3000, "src": "JNTO: International Tourist Tax", "url": "https://www.japan.travel/en/plan/international-tourist-tax/"},
}
# Ways to find what we do not price. Partner links carry the page's own Sub IDs (budget-esim, budget-transfer).
LINKS = {
    "parks": ["Compare Tokyo Disney and theme park tickets", "https://www.getyourguide.com/s/?q=tokyo%20disney%20tickets&partner_id=D7IXONS&cmp=ps-budget-disney", True],
    "sanrio": ["Sanrio Puroland tickets", "https://www.getyourguide.com/s/?q=sanrio%20puroland&partner_id=D7IXONS&cmp=ps-budget-sanrio", True],
    "subway": ["Tokyo Subway Ticket", "https://www.getyourguide.com/s/?q=tokyo%20subway%20ticket&partner_id=D7IXONS&cmp=ps-budget-subway", True],
    "shinkansen": ["Book Shinkansen tickets online", "https://www.japan-bullettrain.com/?via=packsmart", True],
    "transfer": ["Book a private airport transfer", "https://tpo.lu/hPV4u7AE", True],
    "tours": ["Compare guided multi-day Japan tours", "https://www.tourradar.com/d/japan?utm_source=partner-traveller-1471305&utm_medium=ambassador&utm_campaign=budget-tours", True],
    "tours_family": ["Compare family-friendly multi-day Japan tours", "https://www.tourradar.com/srp/d-japan?age_range=13-17%2C7-12&adults=2&children=2&utm_source=partner-traveller-1471305&utm_medium=ambassador&utm_campaign=family-tours", True],
    "esim": ["See eSIM data plans for Japan", "https://airalo.tpo.lu/u2N5qgJl", True],
    "flights": ["Search flights", "https://aviasales.tpo.lu/E6VxsbuE", True],   # Aviasales, Sub ID budget-flights (28 Nov 2026)
    "jrpass": ["Japan Rail Pass", "https://www.getyourguide.com/s/?q=japan%20rail%20pass&partner_id=D7IXONS&cmp=ps-budget-jrpass", True],
    "insurance": ["Get a travel medical insurance quote", "https://www.safetywing.com/nomad-insurance?referenceID=26492686&utm_source=26492686&utm_medium=Ambassador", True],
}

PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Japan Trip Cost Calculator: Trains, Disney, Taxis and More | PackSmart</title>
<meta name="description" content="Work out what your Japan trip costs: airport trains, city transport, taxis, rail passes and the departure tax from official prices, plus your own hotel and flights.">
<meta property="og:type" content="website">
<meta property="og:site_name" content="PackSmart">
<meta property="og:title" content="Japan Trip Cost Calculator">
<meta property="og:description" content="What will your Japan trip cost? Airport trains, day passes, the Shinkansen, taxis, Disney and the departure tax from official prices, plus your own hotel and flights.">
<meta property="og:url" content="https://www.packsmartapp.com/japan-budget">
<meta property="og:image" content="https://www.packsmartapp.com/og-default.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="https://www.packsmartapp.com/og-default.png">
<link rel="canonical" href="https://www.packsmartapp.com/japan-budget">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600;700&family=Nunito:wght@500;600;700;800&display=swap" rel="stylesheet">
<script async src="https://www.googletagmanager.com/gtag/js?id=G-0C4Z7VVGPE"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag("js",new Date());gtag("config","G-0C4Z7VVGPE");</script>
<style>
:root{--primary:#00C9A7;--accent:#E94560;--dark:#0f0f23;--ink:#2b3242;--muted:#5a6378;--line:#d9f0ea}
*{box-sizing:border-box}
body{margin:0;font-family:'Nunito',sans-serif;background:#f4faf8;color:var(--ink);-webkit-text-size-adjust:100%}
a{color:#0a8f78}
.top{background:linear-gradient(135deg,#0f0f23,#1a1a3e);color:#fff;padding:14px 16px 18px}
.top a{color:#bfeee4;text-decoration:none;font-size:.85rem;font-weight:700}
.top h1{margin:8px 0 4px;font-size:1.35rem;line-height:1.25}
.top h1 span{color:var(--primary)}
.top p{margin:0;color:#cfd6e6;font-size:.9rem;line-height:1.45}
main{max-width:640px;margin:0 auto;padding:4px 16px 60px}
.card{background:#fff;border:1.5px solid var(--line);border-radius:18px;padding:16px;margin:16px 0 0}
.card h2{margin:0 0 4px;font-size:1.05rem;color:var(--dark)}
.card .h{margin:0 0 12px;font-size:.85rem;color:var(--muted)}
.row{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:8px 0;border-top:1px solid #eef3f2}
.row:first-of-type{border-top:0}
.row label{font-size:.92rem;font-weight:700;color:var(--dark)}
.row.stack{flex-direction:column;align-items:stretch;gap:6px}.row.stack select{max-width:100%;width:100%}
.row label small{display:block;font-weight:500;font-size:.76rem;color:var(--muted)}
.step{display:flex;align-items:center;gap:6px}
.step button{width:36px;height:36px;border-radius:12px;border:1.5px solid var(--line);background:#f4faf8;font:inherit;font-size:1.2rem;font-weight:700;color:var(--dark);cursor:pointer}
.step output{min-width:28px;text-align:center;font-weight:700;font-size:1.05rem}
select,input[type=number]{font:inherit;font-size:.92rem;border:1.5px solid var(--line);border-radius:12px;padding:8px 10px;background:#fff;color:var(--dark);max-width:58%}
input[type=number]{width:130px}
.res{background:var(--dark);color:#fff;border:0}
.res h2{color:#fff}
.tot{display:flex;align-items:baseline;justify-content:space-between;gap:10px;margin:4px 0 2px}
.tot b{font-size:1.9rem;color:var(--primary)}
.tot span{font-size:.85rem;color:#bfc6d6}
.pp{font-size:.85rem;color:#bfc6d6;margin:0 0 12px}
.ln{display:flex;justify-content:space-between;gap:12px;padding:9px 0;border-top:1px solid rgba(255,255,255,.1);font-size:.9rem}
.ln .l{min-width:0}
.ln .l small{display:block;color:#9aa5b5;font-size:.74rem;margin-top:2px;line-height:1.35}
.ln .l small a{color:#7fe6d3}
.ln .v{flex:0 0 auto;font-weight:700;text-align:right}
.grp{margin:14px 0 2px;font-size:.72rem;letter-spacing:.8px;text-transform:uppercase;font-weight:700;color:#7fe6d3}
.np{color:#ffb3c0;font-weight:700}
.go{display:flex;align-items:center;justify-content:space-between;gap:10px;margin:8px 0 0;padding:11px 13px;border-radius:14px;background:#fff;border:1.5px solid #e3e8ec;color:var(--dark);text-decoration:none;font-weight:700;font-size:.9rem}
.go small{flex:0 0 auto;font-weight:500;font-size:.72rem;color:#8a93a6}
.next{display:flex;align-items:center;justify-content:space-between;gap:10px;margin:18px 0 2px;padding:14px 16px;border-radius:16px;background:linear-gradient(135deg,#E94560,#ff6b85);color:#fff;text-decoration:none;font-weight:700;font-size:.98rem}.next i{font-style:normal;font-size:1.3rem}
.two{display:grid;gap:8px;margin:6px 0 2px}.two>div{background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.12);border-radius:14px;padding:12px 13px}
.row[hidden],.hint[hidden]{display:none}
.hint{margin:2px 0 8px;font-size:.84rem;line-height:1.45;color:var(--muted)}.hint a{font-weight:700}.hint b{color:var(--dark)}
.ln .v{max-width:50%}.bkl{display:block;width:fit-content;margin:6px 0 0 auto;text-align:right;font-size:.8rem;font-weight:700;color:#7fe6d3;text-decoration:underline;text-underline-offset:2px}.ln .l .bkl small,.bkl small{font-weight:500;color:#9aa5b5;text-decoration:none;display:inline;margin:0 0 0 4px;font-size:.72rem}
.kinds{display:grid;grid-template-columns:repeat(4,1fr);gap:6px}.kinds button{font:inherit;font-size:.8rem;font-weight:700;padding:9px 2px 7px;border-radius:12px;border:1.5px solid var(--line);background:#fff;color:var(--dark);cursor:pointer;line-height:1.2}.kinds button span{display:block;font-size:1.15rem;margin-bottom:2px}.kinds button[aria-checked=true]{border-color:var(--primary);background:#e6faf5}.kinds button[disabled]{opacity:.35;cursor:default}
#way[hidden]{display:none}
.q{margin:16px 0 2px;font-weight:700;color:var(--dark);font-size:.98rem}.q:first-of-type{margin-top:6px}.q small{display:block;font-weight:500;font-size:.78rem;color:var(--muted)}
.styles{grid-template-columns:repeat(3,1fr);margin-top:8px}.styles button small{display:block;font-weight:500;font-size:.7rem;color:var(--muted);margin-top:2px}
.sec h2{display:flex;justify-content:space-between;align-items:baseline;gap:8px}.sec h2 .sub{font-size:.92rem;color:#0a8f78;white-space:nowrap}
.cost{margin:12px -16px -16px;padding:4px 16px 10px;background:#f4faf8;border-top:1.5px solid var(--line);border-radius:0 0 16px 16px}
.cost:empty{display:none}
.cost .ln{border-top:1px solid #e1efeb;color:var(--dark)}.cost .ln:first-child{border-top:0}
.cost .ln .l small{color:var(--muted)}.cost .bkl{color:#0a8f78}.cost .np{color:#c0293f}
.res .tot b{font-size:2.1rem}
.lab{margin:14px 0 6px;font-weight:700;font-size:.9rem;color:var(--dark)}.lab small{font-weight:500;color:var(--muted);font-size:.74rem}
.chips{display:flex;flex-wrap:wrap;gap:6px}.chips[hidden]{display:none}
.chips button,.tiles button{font:inherit;font-size:.86rem;font-weight:700;padding:8px 12px;border-radius:999px;border:1.5px solid var(--line);background:#fff;color:var(--dark);cursor:pointer;transition:background .15s,border-color .15s,transform .1s}
.chips button:active,.tiles button:active{transform:scale(.95)}
.chips button[aria-pressed=true]{border-color:var(--primary);background:#e6faf5;color:#07624f}
.chips.sm{margin-top:6px}.chips.sm button{font-size:.78rem;padding:6px 10px}
.tiles{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:8px}
.tiles button{border-radius:16px;padding:12px 4px 10px;font-size:.8rem;line-height:1.25}.tiles button span{display:block;font-size:1.6rem;margin-bottom:4px}
.tiles button[aria-pressed=true]{border-color:var(--primary);background:#e6faf5;box-shadow:0 2px 8px rgba(0,201,167,.18)}
.tiles button[disabled]{opacity:.45;cursor:default}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:0 14px}.grid2 .row{border-top:0;padding:6px 0;flex-direction:column;align-items:flex-start;gap:4px}.grid2 .row label{font-size:.88rem}
.grid2 .step button{width:32px;height:32px}.grid2 .step output{min-width:20px}
details.more summary,details.info summary{cursor:pointer;font-size:.8rem;font-weight:700;color:#0a8f78;margin:8px 0 2px}
details.info[hidden]{display:none}
.bd{margin:12px -16px -16px;border-top:1.5px solid var(--line)}
.bd summary{cursor:pointer;list-style:none;padding:10px 16px;font-size:.84rem;font-weight:700;color:#0a8f78;background:#f4faf8;border-radius:0 0 16px 16px}
.bd summary::-webkit-details-marker{display:none}.bd summary::after{content:' ▾'}.bd[open] summary::after{content:' ▴'}.bd[open] summary{border-radius:0}
.bd .cost{margin:0;border-top:0}
.bar.tick b{animation:tick .45s}@keyframes tick{0%{transform:scale(1)}40%{transform:scale(1.12)}100%{transform:scale(1)}}.bar b{display:inline-block}
.hrow{display:flex;justify-content:space-between;align-items:center}.reset{font:inherit;font-size:.78rem;font-weight:700;color:#c0293f;background:#fff0f3;border:1.5px solid #ffd1da;border-radius:999px;padding:6px 10px;cursor:pointer}
.menu{padding-top:12px}
.mtabs{display:flex;gap:8px;overflow-x:auto;margin:0 -16px 12px;padding:2px 16px 6px;scrollbar-width:none}.mtabs::-webkit-scrollbar{display:none}
.mtabs button{flex:0 0 auto;font:inherit;font-weight:800;font-size:.86rem;padding:9px 14px;border-radius:14px;border:1.5px solid var(--line);background:#fff;color:var(--dark);cursor:pointer}
.mtabs button[aria-selected=true]{background:#ffd166;border-color:#ffd166;box-shadow:0 3px 0 #e0a800}
.mhead{display:flex;align-items:center;gap:8px;flex-wrap:wrap}.mhead h2{margin:0;font-size:1.25rem;font-weight:800}
.mcount{font-size:.74rem;font-weight:800;background:#fff3c4;color:#6b4e00;border-radius:999px;padding:3px 9px}
.items{display:grid;grid-template-columns:1fr;gap:12px;margin-top:10px}@media(min-width:620px){.items{grid-template-columns:1fr 1fr}}
.it{display:flex;flex-direction:column;border:1.5px solid #eef2f1;border-radius:20px;padding:14px 14px 0;background:#fff;box-shadow:0 4px 16px rgba(15,15,35,.05);transition:border-color .15s,box-shadow .15s}
.it.on{border-color:var(--primary);box-shadow:0 6px 18px rgba(0,201,167,.18)}
.it .tags{display:flex;flex-wrap:wrap;gap:5px;align-items:flex-start}.it .tags span{font-size:.7rem;font-weight:800;padding:3px 8px;border-radius:999px;border:1px solid #e3ecea;background:#fff;color:var(--muted)}
.it .tags .fav{margin-left:auto;background:#fff3c4;border-color:#fff3c4;color:#6b4e00}
.it .art{width:96px;height:96px;margin:10px auto 8px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:3rem}
.it h3{margin:0;font-size:1.12rem;font-weight:800;line-height:1.2;color:var(--dark)}.it p{margin:4px 0 12px;font-size:.86rem;color:var(--muted);line-height:1.4;flex:1}
.it .foot{display:flex;align-items:center;justify-content:space-between;gap:10px;border-top:1px solid #f0f3f2;margin:0 -14px;padding:12px 14px 14px}
.it .pr{font-weight:800;font-size:1.2rem;color:var(--dark);line-height:1.15}.it .pr small{display:block;font-size:.66rem;font-weight:800;letter-spacing:.6px;text-transform:uppercase;color:#8a93a6;margin-bottom:2px}.it .pr i{display:block;font-style:normal;font-weight:600;font-size:.72rem;color:var(--muted)}
.it .add{flex:0 0 auto;font:inherit;font-weight:800;font-size:.92rem;border:0;border-radius:14px;padding:11px 14px;background:#ffd166;color:#3a2a00;cursor:pointer;box-shadow:0 3px 0 #e0a800;white-space:nowrap}
.it .add.rm{background:#e6faf5;color:#07624f;box-shadow:none;border:1.5px solid var(--primary)}
.it .qty{flex:0 0 auto;display:flex;align-items:center;gap:6px;border:1.5px solid #ffd166;border-radius:14px;background:#fff8e1;padding:4px}
.it .qty button{width:34px;height:34px;border:0;border-radius:10px;font:inherit;font-size:1.15rem;font-weight:800;cursor:pointer;background:#fff;color:#c0293f}.it .qty button+b+button{background:var(--primary);color:#fff}
.it .qty b{font-size:.88rem;min-width:52px;text-align:center}
.bar.tray{left:0;right:0;bottom:0;transform:none;max-width:none;border-radius:18px 18px 0 0;padding:10px 12px calc(10px + env(safe-area-inset-bottom));gap:10px;white-space:normal}
.tbadge{position:relative;font-size:1.6rem;line-height:1;margin-right:6px}.tbadge i{position:absolute;top:-6px;right:-8px;font-style:normal;font-size:.68rem;font-weight:800;background:var(--accent);color:#fff;border-radius:999px;min-width:18px;height:18px;display:flex;align-items:center;justify-content:center;padding:0 4px}
.tmid{flex:1;min-width:0}.tt{display:block;color:#ffd166;font-size:.9rem}.tchips{display:flex;gap:4px;overflow:hidden;white-space:nowrap;mask-image:linear-gradient(90deg,#000 80%,transparent)}.tchips span{font-size:.68rem;background:rgba(255,255,255,.1);border-radius:999px;padding:2px 7px}
.ttot{text-align:right}.ttot small{display:block;font-size:.62rem;color:#bfc6d6;text-transform:uppercase;letter-spacing:.5px}.ttot b{font-size:1rem}
.tgo{background:var(--primary);color:#0f0f23;font-weight:800;text-decoration:none;border-radius:12px;padding:10px 11px;font-size:.84rem;white-space:nowrap}
main{padding-bottom:110px}
body{background:#fffbf0}
.top.toy{position:sticky;top:0;z-index:15;background:#fff;color:var(--dark);padding:10px 16px 12px;border-bottom:3px solid #ffe7a3;box-shadow:0 4px 14px rgba(15,15,35,.05)}
.top.toy .back{color:#0a8f78;font-size:.78rem}
.brand{display:flex;align-items:center;gap:12px;margin:4px 0 10px}.logo{width:48px;height:48px;border-radius:14px;background:#ffd166;padding:6px;box-shadow:0 3px 0 #e0a800;flex:0 0 auto}
.top.toy h1{margin:0;font-size:1.45rem;font-weight:800;letter-spacing:-.5px;color:#1f2937}.top.toy h1 span{color:#f2a900}.top.toy p{margin:0;color:var(--muted);font-size:.84rem}
.ctrls{display:flex;gap:8px;flex-wrap:wrap;align-items:stretch}
.seg{display:flex;gap:4px;padding:4px;border:2px solid #ffe08a;background:#fff8e1;border-radius:16px}
.seg button{font:inherit;font-weight:800;font-size:.84rem;border:0;background:transparent;border-radius:12px;padding:8px 10px;color:#4b5563;cursor:pointer;white-space:nowrap}.seg button span{margin-right:4px}
.seg button[aria-checked=true]{background:#ffd166;color:#1f2937;box-shadow:0 2px 0 #e0a800}
.easy{display:flex;align-items:center;gap:8px;font:inherit;text-align:left;border:2px solid #9be7d3;background:#f0fcf8;border-radius:16px;padding:5px 12px 5px 8px;cursor:pointer}.easy .ei{width:30px;height:30px}
.easy small{display:block;font-size:.62rem;font-weight:800;letter-spacing:.8px;text-transform:uppercase;color:#0a8f78}.easy b{font-size:.84rem;color:#1f2937}
.easy[aria-pressed=false]{border-color:#e5e7eb;background:#f9fafb}.easy[aria-pressed=false] small{color:#9ca3af}
.reset{font:inherit;font-size:.84rem;font-weight:800;color:#c0293f;background:#fff0f3;border:2px solid #ffd1da;border-radius:16px;padding:8px 12px;cursor:pointer}
.card{border:0;box-shadow:0 6px 20px rgba(15,15,35,.06);border-radius:22px}
.card h2{font-weight:800;letter-spacing:-.3px;font-size:1.15rem}
.it{border:2px solid transparent;box-shadow:0 6px 18px rgba(15,15,35,.07)}.it.on{border-color:#ffd166;box-shadow:0 0 0 3px #fff3c4,0 6px 18px rgba(15,15,35,.07)}
.it .art{padding:14px}.it h3{font-size:1.2rem;letter-spacing:-.3px}
.it .tags span.t0{border-color:#bfe9d9;background:#effbf6;color:#0a7a62}.it .tags span.t1{border-color:#fde7b0;background:#fffaf0;color:#8a5a00}.it .tags span.t2{border-color:#cfe3fb;background:#f2f8ff;color:#2457a6}
.it .pr{font-size:1.35rem;letter-spacing:-.4px}
.mtabs button{border-width:2px;padding:10px 14px}.mtabs button[aria-selected=true]{background:#ffd166;border-color:#f2b300}
.bar.tray{background:#2f3a4f;border-top:3px solid #ffd166;border-radius:22px 22px 0 0;align-items:center}
.tbadge{width:46px;height:46px;border-radius:14px;background:#ffd166;padding:6px;margin-right:4px}.tbadge svg{display:block}
.tth{display:flex;align-items:center;gap:6px}.tt{font-size:1.05rem;font-weight:800;color:#ffd166;white-space:nowrap}.tmode{font-size:.6rem;font-weight:800;letter-spacing:.8px;text-transform:uppercase;background:#47546b;color:#e5e7eb;border-radius:8px;padding:2px 6px}
.tchips{margin-top:4px}.tchips span{display:inline-flex;align-items:center;gap:4px;border:1px solid #5b6880;background:#38445a;color:#fff;font-weight:700;font-size:.68rem;padding:3px 6px 3px 3px;border-radius:10px}
.tchips span i{font-style:normal;width:18px;height:18px;border-radius:50%;background:#fff;display:inline-flex;align-items:center;justify-content:center;font-size:.7rem}.tchips span em{font-style:normal;background:#ffd166;color:#1f2937;border-radius:5px;padding:0 4px;font-size:.62rem}
.ttot small{color:#cbd5e1}.ttot b{font-size:1.1rem;font-weight:800}
.tgo{background:#6ee7b7;color:#0f2f26;border-radius:14px;padding:11px 12px;font-weight:800;box-shadow:0 3px 0 #34b98a}
.bar.tray .tt{color:#ffd166}.bar.tray .ttot b{color:#fff}
@media(max-width:700px){.top.toy{padding:8px 12px 0}.top.toy .back{display:none}.brand{margin:0 0 8px;gap:10px}.logo{width:36px;height:36px;padding:4px;border-radius:11px}.top.toy h1{font-size:1.15rem}.top.toy .brand p{font-size:.74rem}
 .ctrls{flex-wrap:nowrap}.seg{flex:1;justify-content:space-between}.reset{padding:8px 10px;font-size:.78rem}}
@media(max-width:560px){.tchips{display:none}.tbadge{width:40px;height:40px}.ttot b{font-size:1rem;white-space:nowrap}.tgo{padding:10px 10px}.tth{flex-wrap:wrap;gap:2px 6px}}
@media(max-width:400px){.seg button{padding:8px 7px;font-size:.78rem}.seg button span{display:none}.easy{padding:5px 8px}.top.toy h1{font-size:1.25rem}}
h1,h2,h3,.tt,.mtabs button,.add,.tgol,.pr,.seg button,.mcount{font-family:'Fredoka','Nunito',sans-serif}
button,input,select{font-family:inherit}
.pill{display:inline-flex;align-items:center;gap:6px;font:inherit;font-weight:800;font-size:.86rem;border:2px solid #efece4;background:#fff;border-radius:16px;padding:8px 12px;cursor:pointer;color:#1e2433}.pill b{font-weight:800}
.sheet{background:#fff;border:2px solid #ffe7a3;border-radius:18px;padding:6px 14px 12px;margin-top:10px;box-shadow:0 10px 24px rgba(30,36,51,.08)}.sheet[hidden]{display:none}.easy[hidden]{display:none}#kinds[hidden]{display:none}
.done{margin-top:10px;font:inherit;font-weight:800;border:0;border-radius:12px;padding:9px 16px;background:#facc15;color:#1e2433;cursor:pointer;box-shadow:0 3px 0 #d6a50c}
.planner{margin:16px 0 0}
.mtabs{margin:0 -16px 14px;padding:2px 16px 8px}.mtabs button{font-weight:600;font-size:.95rem;padding:10px 14px;border-radius:16px;border:2px solid #efece4;background:#fff}.mtabs button i{font-style:normal;font-size:.7rem;background:#ef4444;color:#fff;border-radius:999px;padding:1px 6px;margin-left:2px}
.mtabs button[aria-selected=true]{background:#facc15;border-color:#f59e0b;box-shadow:0 3px 0 #d6a50c}
.mhead{display:flex;align-items:center;gap:8px;flex-wrap:wrap}.memo{font-size:1.6rem}.mhead h2{font-size:1.6rem;font-weight:700;margin:0;letter-spacing:-.3px}.mcount{background:#fef3c7;color:#92400e;font-weight:600;font-size:.8rem;border-radius:999px;padding:4px 10px}
.msub{margin:4px 0 10px;color:#5a6378;font-size:.92rem}
.filters{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin-bottom:12px}.fchips{display:flex;flex-wrap:wrap;gap:6px;background:#fff;border:2px solid #efece4;border-radius:18px;padding:6px}
.fchips button{font:inherit;font-weight:800;font-size:.78rem;border-radius:999px;padding:6px 10px;cursor:pointer;border:2px solid #d1fae5;background:#ecfdf5;color:#047857}
.fchips button[data-fil=rail]{border-color:#fecdd3;background:#fff1f2;color:#be123c}.fchips button[data-fil=nocar]{border-color:#fde68a;background:#fffbeb;color:#92400e}.fchips button[data-fil=budget]{border-color:#bae6fd;background:#f0f9ff;color:#0369a1}
.fchips button[aria-pressed=true]{box-shadow:0 0 0 2px #1e2433}
.rdef{font:inherit;font-weight:800;font-size:.84rem;color:#b45309;background:none;border:0;text-decoration:underline;cursor:pointer}
.extra{background:#fff;border:2px solid #efece4;border-radius:18px;padding:4px 14px 12px;margin-bottom:12px}.extra[hidden]{display:none}.extra .lab:first-child{margin-top:10px}
.items{margin-top:0}@media(min-width:620px){.items{grid-template-columns:1fr 1fr}}@media(min-width:980px){.items{grid-template-columns:1fr 1fr 1fr}}
.it{border:2px solid #efece4;border-radius:22px;box-shadow:0 4px 16px -2px rgba(30,36,51,.05)}.it.on{border-color:#f59e0b;box-shadow:0 8px 24px -4px rgba(245,158,11,.18)}.it.off{opacity:.5}
.it .tags span{font-size:.66rem;font-weight:800;text-transform:uppercase;letter-spacing:.4px;border:0}.it .tags span.tf{background:#fef3c7;color:#92400e}.it .tags span.t0{background:#ecfdf5;color:#047857}.it .tags span.t1{background:#f0f9ff;color:#0369a1}.it .tags span.t2{background:#fff1f2;color:#be123c}
.it .art{width:92px;height:92px;padding:16px}.it h3{font-size:1.15rem;font-weight:700}.it.on h3{color:#d97706}
.it .pr small{font-family:'Nunito',sans-serif;text-transform:uppercase;font-size:.64rem}.it .pr{font-size:1.25rem;font-weight:700}.it .pr em{font-style:normal;font-size:.85rem;color:#5a6378;font-family:'Nunito',sans-serif;font-weight:700}
.it .add{background:#facc15;box-shadow:0 3px 0 #d6a50c;font-weight:600}.it .add[disabled]{cursor:default}.it .add.rm{font-weight:600}
.it .qty{border-color:#f59e0b;background:#fffbeb}.it .qty button{background:#fff}.it .qty button+b+button{background:#facc15;color:#1e2433}
.none{background:#fff;border-radius:18px;padding:16px;color:#5a6378}.none button{font:inherit;font-weight:800;color:#b45309;background:none;border:0;text-decoration:underline;cursor:pointer}
.bar.tray{background:#1e2433;border-top:0;box-shadow:0 -6px 24px -4px rgba(30,36,51,.25);align-items:center;gap:10px}
.tbadge{background:#2a3246;border:2px solid #3a4560}.tt{font-size:1.1rem;font-weight:700}.tmode{background:#2a3246;border:1px solid #3a4560;color:#cbd5e1}
.tsum{font-size:.74rem;color:#cbd5e1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.tgo{display:flex;flex-direction:column;align-items:flex-end;gap:2px;background:#22c55e;color:#06210f;padding:8px 12px;border-radius:16px;box-shadow:0 3px 0 #15803d;text-decoration:none}
.tgo .ttot small{display:block;font-size:.58rem;letter-spacing:.6px;color:#064e2a;text-transform:uppercase;text-align:right;font-family:'Nunito',sans-serif;font-weight:800}.bar.tray .tgo .ttot b{color:#06210f;font-size:1rem;font-family:'Fredoka',sans-serif;white-space:nowrap}
.tgol{font-weight:700;font-size:.86rem;white-space:nowrap}
.tmid{min-width:0}
@media(min-width:700px){.tgo{flex-direction:row;align-items:center;gap:14px;padding:12px 18px}.tgo .ttot b{font-size:1.25rem}.tgol{font-size:1rem}}
.bar.tray{background:#1e2433;border-top:4px solid #facc15;border-radius:0;padding:12px 16px calc(12px + env(safe-area-inset-bottom));gap:12px;align-items:center;box-shadow:0 -6px 24px -4px rgba(30,36,51,.25)}
.bar.tray .tbadge{width:52px;height:52px;border-radius:16px;background:#facc15;border:0;padding:8px;flex:0 0 auto;margin:0}
.bar.tray .tbadge i{top:-7px;right:-7px;background:#ef4444;border:2px solid #fff;min-width:22px;height:22px;font-size:.72rem}
.bar.tray .tt{font-family:'Fredoka',sans-serif;font-size:1.35rem;font-weight:700;color:#facc15;line-height:1}
.bar.tray .tmode{font-family:'Nunito',sans-serif;font-size:.66rem;font-weight:800;letter-spacing:.8px;background:#2a3246;border:0;color:#fde68a;border-radius:8px;padding:3px 8px;white-space:nowrap}
.bar.tray .tsum{font-size:.84rem;font-weight:700;color:#e5e7eb;margin-top:4px}
.bar.tray .ttot{flex:0 0 auto;text-align:right}.bar.tray .ttot small{display:block;font-size:.66rem;font-weight:800;letter-spacing:.8px;color:#cbd5e1;text-transform:uppercase}
.bar.tray .ttot b{font-family:'Fredoka',sans-serif;font-size:1.5rem;font-weight:700;color:#fff;white-space:nowrap;line-height:1.1}
.bar.tray .tgo{flex:0 0 auto;font-family:'Fredoka',sans-serif;font-size:1.05rem;font-weight:700;border:0;border-radius:16px;padding:12px 18px;background:#34d399;color:#1e2433;box-shadow:0 4px 0 #059669;cursor:pointer;white-space:nowrap;display:inline-flex;align-items:center;gap:6px}
@media(max-width:560px){.bar.tray{gap:8px;padding:10px 10px calc(10px + env(safe-area-inset-bottom))}.bar.tray .tbadge{width:42px;height:42px;border-radius:13px;padding:6px}.bar.tray .tt{font-size:1.05rem}.bar.tray .tmode{display:none}
 .bar.tray .tsum{font-size:.7rem}.bar.tray .ttot b{font-size:1.02rem}.bar.tray .ttot small{font-size:.56rem}.bar.tray .tgo{font-size:.9rem;padding:10px 11px}.bar.tray .tgo .long{display:none}.rsum{padding:8px 12px}.rsum div{font-size:.82rem}.rsum .gt{font-size:1.1rem;white-space:nowrap}.rgo{font-size:1.05rem;padding:13px}.rfoot{padding:10px 12px calc(10px + env(safe-area-inset-bottom))}}
@media(max-width:400px){.bar.tray .tgo span[aria-hidden]{display:none}}
.rsheet{position:fixed;inset:0;z-index:40;background:#fffdf7;display:flex;flex-direction:column}.rsheet[hidden]{display:none}
.rhead{display:flex;align-items:center;gap:12px;background:#1e2433;color:#fff;padding:14px 16px}.rico{width:40px;height:40px;flex:0 0 auto}
.rhead h2{margin:0;font-family:'Fredoka',sans-serif;font-size:1.5rem;color:#facc15;line-height:1.1}.rhead p{margin:2px 0 0;font-weight:700;font-size:.84rem;color:#e5e7eb}
.rx{margin-left:auto;width:46px;height:46px;border-radius:14px;border:2px solid #3a4560;background:transparent;color:#fff;font-size:1.3rem;cursor:pointer}
.rlist{flex:1;overflow-y:auto;padding:14px 16px;display:flex;flex-direction:column;gap:12px;max-width:760px;width:100%;margin:0 auto;box-sizing:border-box}
.rrow{display:flex;align-items:center;gap:12px;background:#fff;border:2px solid #f3f1ea;border-radius:20px;padding:12px;box-shadow:0 2px 10px rgba(30,36,51,.04)}
.rrow .ri{width:56px;height:56px;border-radius:16px;padding:9px;flex:0 0 auto;border:2px solid #fdf3d0}
.rrow .rt{flex:1;min-width:0}.rrow h3{margin:0;font-family:'Fredoka',sans-serif;font-size:1.05rem;color:#1e2433;line-height:1.2}
.rrow .rp{font-family:'Fredoka',sans-serif;font-weight:700;color:#d97706;font-size:1rem}.rrow .rp small{font-family:'Nunito',sans-serif;font-size:.74rem;color:#8a93a6;font-weight:700;margin-left:4px}
.rrow .rs{font-size:.74rem;color:#8a93a6;font-weight:700}
.rq{display:flex;align-items:center;gap:6px;border:2px solid #fde68a;background:#fffbeb;border-radius:16px;padding:4px;flex:0 0 auto}
.rq button{width:36px;height:36px;border:0;border-radius:11px;font:inherit;font-size:1.15rem;font-weight:800;cursor:pointer;background:#fff;color:#ef4444}.rq button.p{background:#34d399;color:#1e2433}.rq b{min-width:22px;text-align:center;font-family:'Fredoka',sans-serif;font-size:1.05rem}
.rch{flex:0 0 auto;font:inherit;font-weight:800;font-size:.8rem;border:2px solid #fde68a;background:#fffbeb;color:#92400e;border-radius:12px;padding:8px 10px;cursor:pointer}
.rfoot{border-top:4px solid #fde68a;background:#fff;padding:14px 16px calc(14px + env(safe-area-inset-bottom))}.rfoot>*{max-width:728px;margin-left:auto;margin-right:auto}
.rsum{background:#fffbeb;border:2px solid #fde68a;border-radius:18px;padding:12px 14px}.rsum div{display:flex;justify-content:space-between;gap:10px;font-weight:700;font-size:.9rem;padding:3px 0}
.rsum .pill{background:#facc15;border:0;border-radius:10px;padding:2px 10px;font-weight:800;font-size:.84rem}.rsum .gt{border-top:1px solid #fde68a;margin-top:6px;padding-top:10px;font-family:'Fredoka',sans-serif;font-size:1.35rem;font-weight:700}
.rgo{display:block;width:100%;margin-top:12px;font-family:'Fredoka',sans-serif;font-size:1.2rem;font-weight:700;border:0;border-radius:18px;padding:15px;background:#34d399;color:#1e2433;box-shadow:0 5px 0 #059669;cursor:pointer}
.card.res{background:#fffdf7;color:#1e2433;padding:0;overflow:hidden;border:2px solid #f3f1ea}
.res .ihead{border-radius:0}.res .ihead h2{font-size:1.35rem}.res .ihead p{font-size:.8rem;line-height:1.35}
.res .grp{margin:16px 16px 6px;color:#92400e;font-size:.74rem}
.res .ln{display:flex;align-items:center;gap:12px;margin:0 12px 10px;background:#fff;border:2px solid #f3f1ea;border-radius:20px;padding:12px;box-shadow:0 2px 10px rgba(30,36,51,.04);color:#1e2433;font-size:.9rem}
.res .ln .li{width:52px;height:52px;border-radius:15px;padding:8px;flex:0 0 auto;border:2px solid #fdf3d0;box-sizing:border-box}
.res .ln .l{flex:1;min-width:0}.res .ln .lt{display:block;font-family:'Fredoka',sans-serif;font-weight:600;font-size:1rem;line-height:1.25}
.res .ln .lp{font-family:'Fredoka',sans-serif;font-weight:700;color:#d97706;font-size:1.02rem;margin-top:2px}.res .ln .lp small{color:#8a93a6}
.res .ln .l small{display:block;color:#8a93a6;font-size:.74rem;font-weight:700;line-height:1.35;margin-top:2px}
.res .ln .lk{flex:0 0 auto;display:flex;flex-direction:column;gap:6px;align-items:stretch;max-width:42%}
.res .ln .lk .bkl{margin:0;display:block;text-align:center;text-decoration:none;font-family:'Fredoka',sans-serif;font-weight:600;font-size:.84rem;color:#1e2433;background:#fffbeb;border:2px solid #fde68a;border-radius:14px;padding:8px 10px}
.res .ln .lk .bkl:first-child{background:#facc15;border-color:#facc15;box-shadow:0 3px 0 #d6a50c}
.res .np{color:#ef4444}
.res .rsum.total{margin:14px 12px 12px;padding:12px 14px}.res .rsum .soft{color:#8a93a6;font-size:.82rem}
.res .rsum .gt span:last-child{color:#1e2433}
.res .two{margin:0 12px 14px}.res .two>div{background:#fff;border:2px solid #f3f1ea;color:#1e2433}.res .two span{color:#5a6378}
.res .ln{align-items:flex-start}.res .rsum.total{background:#fffbeb;border-color:#fde68a}.res .rsum .gt{flex-wrap:wrap}.res .ln .lt{overflow-wrap:anywhere}
@media(max-width:560px){.res .ln{flex-wrap:wrap;gap:10px;padding:12px}.res .ln .li{width:44px;height:44px;padding:6px}.res .ln .l{flex:1 1 calc(100% - 60px)}
 .res .ln .lk{max-width:none;flex:1 1 100%;flex-direction:row;padding-left:54px}.res .ln .lk .bkl{flex:1;font-size:.84rem}
 .res .rsum .gt{font-size:1.15rem}}
.pill[hidden]{display:none}
.mtabs button{border-radius:999px;padding:10px 16px}.mtabs button[aria-selected=true]{border-color:#2563eb;box-shadow:none}
.mhead .mcount{font-family:'Nunito',sans-serif;font-weight:800}
.fchips{border:0;background:none;padding:0}.fchips button{background:#fff;border:2px solid #efece4;color:#1e2433}.fchips button[aria-pressed=true]{background:#facc15;border-color:#facc15;box-shadow:0 3px 0 #d6a50c}
.panel .phead{display:flex;justify-content:space-between;align-items:center;gap:8px;margin-top:8px}.panel .phead .lab{margin:0;text-transform:uppercase;letter-spacing:.6px;font-size:.8rem;color:#5a6378}.psel{font-weight:800;font-size:.84rem;color:#b45309}
.panel .chips button[aria-pressed=true]{background:#facc15;border-color:#facc15;color:#1e2433}
.it .qty button[disabled]{opacity:.35;cursor:default}
.top.toy .mtabs{margin:10px -16px 0;padding:2px 16px 10px;border-top:1px solid #f3f1ea;padding-top:10px}
@media(max-width:700px){.top.toy .mtabs{margin:8px -12px 0;padding:8px 12px 8px}.top.toy .mtabs button{padding:8px 13px;font-size:.86rem}}
.planner{margin-top:14px}
@media(max-width:700px){.filters{flex-wrap:nowrap;overflow-x:auto;margin:0 -16px 12px;padding:0 16px 4px;scrollbar-width:none}.filters::-webkit-scrollbar{display:none}.fchips{flex-wrap:nowrap}.fchips button,.rdef{white-space:nowrap;flex:0 0 auto}}
.rscroll{flex:1;overflow-y:auto;-webkit-overflow-scrolling:touch}.rscroll .rlist{flex:none;overflow:visible}
.rmore{max-width:760px;margin:0 auto;padding:0 12px 20px;box-sizing:border-box}.rmore .card{margin-top:12px}
@media print{.rsheet{position:static}.rscroll{overflow:visible}.rhead .rx,.rfoot .rgo,.rlist{display:none!important}}
.hrow2{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap}.flag{font-size:1.5rem;line-height:1}.brand{margin:0}
.top.toy h1{font-size:1.45rem}.top.toy .brand p{font-size:.84rem}
.hright{display:flex;gap:8px;align-items:center}.cur{display:flex;gap:2px;border:1.5px solid #efece4;border-radius:999px;padding:3px;background:#fff}
.cur button{font:inherit;font-weight:800;font-size:.8rem;border:0;background:none;border-radius:999px;padding:6px 10px;cursor:pointer;color:#374151}.cur button[aria-checked=true]{background:#facc15;color:#1e2433}
.top.toy .reset{border-radius:999px;border:1.5px solid #efece4;background:#fff;color:#9a3412;font-size:.84rem;padding:8px 14px}
.prow{display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap;padding:6px 0}.prow .lab{margin:0;text-transform:uppercase;letter-spacing:.6px;font-size:.78rem;color:#5a6378}
.prow .seg{border-radius:999px;border-width:1.5px;padding:3px}.prow .seg button{border-radius:999px;padding:7px 12px}
.it{border:1.5px solid #f0ece2;border-radius:22px;background:#fff;box-shadow:0 4px 16px -2px rgba(30,36,51,.05);padding:18px 20px 0}
.it.on{background:#fffbeb;border:2px solid #f59e0b;box-shadow:0 8px 24px -4px rgba(245,158,11,.18)}
.it .tags span,.it .tags span.t0,.it .tags span.t1,.it .tags span.t2,.it .tags span.tf{background:#fef3c7;color:#92400e;border:0;font-size:.66rem;letter-spacing:.5px;padding:4px 9px}
.it .tags .fav{margin-left:0}
.it .art{width:84px;height:84px;padding:18px;margin:12px auto 10px}
.it h3{font-size:1.15rem;margin-top:2px}.it.on h3{color:#b45309}.it p{color:#4b5563;font-size:.86rem;margin-bottom:14px}
.it .foot{margin:0 -20px;padding:14px 20px 18px;border-top:1px solid #f3eee2}
.it .pr small{font-size:.62rem;letter-spacing:.7px;color:#6b7280}.it .pr{font-size:1.3rem}
.it .add{border-radius:999px;padding:10px 18px;font-size:.92rem;background:#facc15;box-shadow:none;color:#1e2433}
.it .add.rm{background:#fffbeb;border:2px solid #f59e0b;color:#1e2433}
.it .qty{border-radius:999px;border:2px solid #f59e0b;background:#fffbeb;padding:4px;gap:8px}
.it .qty button{width:32px;height:32px;border-radius:50%;background:#fff;color:#1e2433;box-shadow:0 1px 3px rgba(0,0,0,.08)}.it .qty button+b+button{background:#facc15;color:#1e2433}
.it .qty b{font-family:'Fredoka',sans-serif;font-size:.95rem;min-width:56px}
.mhead h2{font-size:1.6rem}.mhead .mcount{background:#fef3c7;color:#92400e;font-size:.82rem;padding:4px 12px}
.bar.tray .tpp{font-family:'Nunito',sans-serif;font-weight:800;font-size:.72rem;letter-spacing:.6px;text-transform:uppercase;background:#facc15;color:#1e2433;border-radius:999px;padding:3px 10px;white-space:nowrap}
.bar.tray .tper{font-size:.8rem;color:#cbd5e1;font-weight:700;white-space:nowrap}
.bar.tray .tsum{font-size:.82rem;color:#e5e7eb;margin-top:5px}
.bar.tray .ttot small{color:#facc15}.bar.tray #barv{display:none}.bar.tray #barfull{display:block;font-family:'Fredoka',sans-serif;font-size:1.6rem;font-weight:700;color:#fff;white-space:nowrap;line-height:1.1}
@media(max-width:700px){.hright{width:100%;justify-content:space-between}.top.toy h1{font-size:1.1rem}.it{padding:14px 16px 0}.it .foot{margin:0 -16px;padding:12px 16px 14px}}
.bar.tray .tt[hidden],.bar.tray .tmode[hidden]{display:none!important}
@media(min-width:900px){main{max-width:1180px}}
@media(min-width:900px){.planner{display:grid;grid-template-columns:1fr auto;column-gap:16px}.planner>.mhead,.planner>.msub{grid-column:1}.planner>.filters{grid-column:2;grid-row:1/3;align-self:center;margin:0}.planner>.extra,.planner>.items{grid-column:1/-1}}
@media(max-width:700px){.top.toy .brand p{display:none}.flag{font-size:1.2rem}.hrow2{gap:8px}.cur button{padding:5px 9px;font-size:.76rem}.top.toy .reset{padding:6px 11px;font-size:.78rem}}
@media(max-width:560px){.bar.tray #barv{display:block}.bar.tray #barfull{display:none}.bar.tray .tper{display:none}.bar.tray .tpp{font-size:.62rem;padding:2px 8px}.bar.tray .tsum{font-size:.7rem}}
.mtabs button[data-tab=review]{background:#d1fae5;border-color:#6ee7b7;color:#065f46}.mtabs button[data-tab=review][aria-selected=true]{background:#34d399;border-color:#2563eb;color:#06210f}.mtabs button[data-tab=book]{background:#E94560;border-color:#E94560;color:#fff}.mtabs button[data-tab=book][aria-selected=true]{background:#c9304b;border-color:#2563eb}
.rpanel[hidden],.filters[hidden]{display:none}.rpanel{margin-top:6px}.rpanel .rlist{padding:0;max-width:none}.rpanel .rsum{margin-top:14px}.rpanel .rgo{margin-top:12px}.rpanel .rmore{padding:0;max-width:none}
.cgrp{grid-column:1/-1;margin:10px 0 -2px;font-family:'Fredoka',sans-serif;font-size:1.1rem;color:#1e2433}.cgrp small{font-family:'Nunito',sans-serif;font-weight:700;font-size:.8rem;color:#8a93a6;margin-left:4px}
.msub{display:none}
@media(max-width:700px){.items{gap:10px}
 .it{display:grid;grid-template-columns:56px 1fr;grid-template-areas:"art tags" "art h" "art p" "foot foot";column-gap:12px;padding:12px 14px 0;border-radius:18px}
 .it .tags{grid-area:tags;gap:4px;min-height:0}.it .tags span{font-size:.58rem;padding:2px 7px}
 .it .art{grid-area:art;width:56px;height:56px;padding:10px;margin:2px 0 0;align-self:start}
 .it h3{grid-area:h;font-size:1rem;margin:3px 0 0}.it p{grid-area:p;font-size:.78rem;margin:2px 0 10px;line-height:1.35}
 .it .foot{grid-area:foot;margin:0 -14px;padding:9px 14px 11px}
 .it .pr{font-size:1.08rem}.it .pr small{font-size:.56rem}
 .it .add{padding:8px 14px;font-size:.84rem}.it .qty{padding:3px;gap:4px}.it .qty button{width:30px;height:30px}.it .qty b{font-size:.84rem;min-width:46px}
 .cgrp{margin:6px 0 -4px;font-size:1rem}}
@media(max-width:700px){.planner>.mhead{display:none}.planner{margin-top:10px}
 .extra .chips{flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none;margin:0 -14px;padding:0 14px 2px}.extra .chips::-webkit-scrollbar{display:none}.extra .chips button{flex:0 0 auto;white-space:nowrap}
 .prow{flex-wrap:nowrap;padding:4px 0}.prow .lab{display:none}.prow .seg{flex:1}.prow .chips{margin:0;padding:0}}
.note{font-size:.78rem;color:var(--muted);line-height:1.5;margin:14px 2px 0}
.peek{display:flex;justify-content:space-between;align-items:baseline;gap:10px;margin:0 0 4px;font-size:.9rem;color:#bfc6d6}.peek b{color:var(--primary);font-size:1.05rem}.peek a{color:#7fe6d3;font-weight:700;text-decoration:none;font-size:.82rem}
.total{margin:16px -16px 0;padding:16px;background:rgba(0,201,167,.1);border-top:1px solid rgba(0,201,167,.35);border-bottom:1px solid rgba(0,201,167,.35)}
.total h3{margin:0;font-size:1rem;color:#fff}
.ck{display:flex;gap:10px;align-items:flex-start;padding:12px 0;border-top:1px solid rgba(255,255,255,.1)}
.ck .n{flex:0 0 24px;height:24px;border-radius:50%;background:rgba(0,201,167,.18);color:#7fe6d3;font-size:.8rem;font-weight:700;display:flex;align-items:center;justify-content:center;margin-top:1px}
.ck.done .n{background:#00C9A7;color:#0f0f23}
.bk{display:inline-flex;align-items:center;gap:7px;margin-top:9px;font-size:.8rem;color:#bfc6d6;cursor:pointer}.bk input{width:17px;height:17px;margin:0;accent-color:#00C9A7}
.ck .t{flex:1;min-width:0;font-size:.9rem}.ck .t small{display:block;color:#9aa5b5;font-size:.76rem;margin-top:2px}
.ck .t .go{margin-top:8px}
.ck.done .t>b{color:#9aa5b5}.ck.done .t>b::after{content:' · booked ✓';color:#7fe6d3;font-size:.8rem}
.two b{display:block;margin-bottom:2px}.two span{display:block;font-size:.84rem;color:#cfd6e6;line-height:1.4}
.keep h2{margin:0 0 4px}
.sh{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:10px 0 0}
.sh button{display:flex;align-items:center;justify-content:center;gap:7px;padding:11px 8px;border-radius:14px;border:1.5px solid var(--line);background:#f4faf8;font:inherit;font-size:.9rem;font-weight:700;color:var(--dark);cursor:pointer}
.sh button svg{width:18px;height:18px;flex:0 0 auto}
.em{margin:12px 0 0}.em[hidden]{display:none}
.em form{display:flex;gap:8px}.em input[type=email]{flex:1;min-width:0;font:inherit;font-size:.95rem;border:1.5px solid var(--line);border-radius:12px;padding:10px 12px}
.em button.send{border:0;border-radius:12px;background:var(--accent);color:#fff;font:inherit;font-weight:700;padding:10px 16px;cursor:pointer}
.em .f{display:block;font-size:.76rem;color:var(--muted);margin-top:6px;line-height:1.4}
.em .ok{font-size:.9rem;color:var(--dark);margin:0}.em .tips{margin-top:8px;border:1.5px solid var(--primary);background:#fff;color:#0a8f78;border-radius:12px;font:inherit;font-weight:700;padding:9px 14px;cursor:pointer}
.em .err{color:#c0293f;font-size:.84rem;margin:6px 0 0}
.plan{margin:14px 2px 0;font-size:.9rem;color:var(--muted)}
.srcs{margin:14px 0 0;background:#fff;border:1.5px solid var(--line);border-radius:14px;padding:4px 14px}
.srcs summary{cursor:pointer;font-weight:700;color:var(--dark);font-size:.9rem;padding:10px 0}
.srcs ul{margin:0 0 12px;padding-left:1.1rem;font-size:.84rem;line-height:1.6}
.bar{position:fixed;left:50%;bottom:12px;transform:translateX(-50%);max-width:calc(100% - 24px);display:flex;gap:10px;align-items:center;background:var(--dark);color:#fff;border-radius:999px;padding:9px 16px;font-size:.86rem;box-shadow:0 6px 20px rgba(15,15,35,.3);text-decoration:none;white-space:nowrap;z-index:20}
.bar b{color:var(--primary)}@media(max-width:380px){#barp{display:none}}.bar[hidden]{display:none}
@media print{.ctrls,.planner .mtabs,.filters,.sheet,.extra{display:none!important}.items,.reset,#items{display:none!important}.bd summary,.chips,.tiles,details.info summary,details.more{display:none!important}.bd{margin:0;border:0}.top a,.bar,.keep,.plan,.sh,.go,.bkl,.row,.kinds,.hint,.q,.card .h,#way{display:none!important}.card{border:0;padding:0;margin:8px 0}.cost{margin:0;background:#fff;border:0}
 body{background:#fff}.res{background:#fff;color:#0f0f23;border:1px solid #ccc}.res h2,.total h3,.ck .t{color:#0f0f23}.ln .l small,.ck .t small,.peek{color:#555}
 .srcs{border:0;padding:0}.srcs[open] summary,.srcs summary{list-style:none}.printsum{display:block!important}}
.printsum{display:none;font-size:.9rem;margin:0 0 8px}
</style>
</head>
<body>
<header class="top toy">
  <a class="back" href="/japan?src=budget">‹ Japan</a>
  <div class="hrow2"><div class="brand"><span class="flag" aria-hidden="true">🇯🇵</span><div><h1>Japan Trip Budget Planner</h1><p>Tap cards to build your trip and see a live cost estimate</p></div></div><div class="hright"><div class="cur" id="cur" role="radiogroup" aria-label="Currency"></div><button type="button" class="reset" id="reset">Reset defaults</button></div></div>
  <div class="ctrls">
    <button type="button" class="pill" id="whob" hidden aria-expanded="false" aria-controls="whosheet"><span aria-hidden="true">👨‍👩‍👧‍👦</span> <b id="whol"></b> ▾</button>
    <button type="button" class="pill" id="fromb" hidden aria-expanded="false" aria-controls="fromsheet"><span aria-hidden="true">🛫</span> <b id="froml">Flying from</b> ▾</button>
    <button type="button" class="easy" id="kidsw" hidden><b id="kidsl"></b></button>
  </div>
  <div class="mtabs" id="mtabs" role="tablist" aria-label="Plan your trip"></div>
  <div class="sheet" id="whosheet" hidden></div><div class="sheet" id="fromsheet" hidden></div>
</header>
<main>
  <section class="planner">
    <div class="mhead"><span class="memo" id="memo" aria-hidden="true"></span><h2 id="mtitle"></h2><span class="mcount" id="mcount"></span></div><p class="msub" id="msub"></p>
    <div class="filters"><div class="fchips" id="fchips"></div></div>
    <div class="extra" data-tab="trav"><div class="prow"><p class="lab">Quick group preset</p><div class="chips" data-g="who"></div></div><div class="prow"><p class="lab">Travel style</p><div class="seg" id="styles" role="radiogroup" aria-label="Travel style"></div></div></div>
    <div class="extra" data-tab="stays">
    <details class="info" id="hinfo"><summary>ⓘ How we price this</summary><p class="hint" id="hhint"></p></details>
    <div class="row" id="hrooms" hidden><label>Rooms<small>most Japanese rooms sleep 2</small></label><div class="step" data-k="rm"><button type="button" data-d="-1" aria-label="Fewer">−</button><output>2</output><button type="button" data-d="1" aria-label="More">+</button></div></div>
    <div class="row" id="hown" hidden><label for="hotel">Your hotel per night<small>all rooms together</small></label><input type="number" id="hotel" inputmode="numeric" min="0" step="1000" placeholder="e.g. 25000"></div>
    </div>
    <div class="extra panel" data-tab="flight"><div class="phead"><p class="lab">🛫 Flying from</p><span class="psel" id="psel"></span></div><div class="chips" data-g="from"></div>
    <div class="row stack" id="fromrow" hidden><label for="from">Other city</label><select id="from"><option value="">Choose a city</option>%%FROM%%<option value="own">Somewhere else: I'll type my fare</option></select></div>
    <p class="hint" id="flyhint" hidden></p>
    <div class="row" id="flyown" hidden><label for="fly">Flights, total<small>all travellers, return</small></label><input type="number" id="fly" inputmode="numeric" min="0" step="1000" placeholder="e.g. 280000"></div>
    </div>
    <div class="extra" data-tab="food"><details class="info" id="finfo"><summary>ⓘ How we price this</summary><p class="hint" id="fhint"></p></details>
      <div class="row" id="fown" hidden><label for="food">Food per person per day</label><input type="number" id="food" inputmode="numeric" min="0" step="500" placeholder="e.g. 5000"></div>
    </div>
    <div class="extra" data-tab="move"><p class="lab">🛬 Land at</p><div class="chips" data-g="arr"></div><p class="lab">🛫 Fly home from</p><div class="chips" data-g="dep"></div><div class="kinds" id="kinds" hidden></div><p class="lab" id="waylab">Which one</p><div class="chips sm" data-g="way"></div></div>
    <div class="items" id="items"></div>
    <div class="rpanel" id="rpanel" hidden></div>
    <div class="rpanel" id="bpanel" hidden></div>
  </section>
  <div id="raw" hidden>
    <div class="row"><label>Adults<small>18 and older</small></label><div class="step" data-k="ad"><button type="button" data-d="-1" aria-label="Fewer">−</button><output>2</output><button type="button" data-d="1" aria-label="More">+</button></div></div>
    <div class="row"><label>Teenagers<small>12 to 17</small></label><div class="step" data-k="tn"><button type="button" data-d="-1" aria-label="Fewer">−</button><output>0</output><button type="button" data-d="1" aria-label="More">+</button></div></div>
    <div class="row"><label>Children<small>6 to 11</small></label><div class="step" data-k="ch"><button type="button" data-d="-1" aria-label="Fewer">−</button><output>2</output><button type="button" data-d="1" aria-label="More">+</button></div></div>
    <div class="row"><label>Little ones<small>under 6</small></label><div class="step" data-k="in"><button type="button" data-d="-1" aria-label="Fewer">−</button><output>0</output><button type="button" data-d="1" aria-label="More">+</button></div></div>
    <div class="row"><label>🗼 Tokyo</label><div class="step" data-k="nt"><button type="button" data-d="-1" aria-label="Fewer">−</button><output>9</output><button type="button" data-d="1" aria-label="More">+</button></div></div>
    <div class="row"><label>⛩️ Kyoto</label><div class="step" data-k="nk"><button type="button" data-d="-1" aria-label="Fewer">−</button><output>0</output><button type="button" data-d="1" aria-label="More">+</button></div></div>
    <div class="row"><label>🏯 Osaka</label><div class="step" data-k="no"><button type="button" data-d="-1" aria-label="Fewer">−</button><output>0</output><button type="button" data-d="1" aria-label="More">+</button></div></div>
    <div class="row"><label>❄️ Hokkaido<small>Sapporo</small></label><div class="step" data-k="nh"><button type="button" data-d="-1" aria-label="Fewer">−</button><output>0</output><button type="button" data-d="1" aria-label="More">+</button></div></div>
    <div class="row"><label>Tokyo Disney days<small>Disneyland or DisneySea, 1 park a day</small></label><div class="step" data-k="dn"><button type="button" data-d="-1" aria-label="Fewer">−</button><output>0</output><button type="button" data-d="1" aria-label="More">+</button></div></div>
    <div class="row"><label for="sanrio">Sanrio Puroland</label><select id="sanrio"><option value="0">No</option><option value="1">Yes</option></select></div>
    <div class="row"><label for="zoo">Ueno Zoo</label><select id="zoo"><option value="0">No</option><option value="1">Yes</option></select></div>
    <div class="row stack"><label for="hstyle">Hotel style</label><select id="hstyle"><option value="budget">Budget</option><option value="mid" selected>Mid-range</option><option value="upscale">Upscale</option><option value="luxury">Luxury</option><option value="own">I'll type my own price</option></select></div>
    <div class="row stack"><label for="fstyle">Food style</label><select id="fstyle"><option value="budget">Budget</option><option value="mid" selected>Mid-range</option><option value="treat">Treat yourself</option><option value="own">I'll type my own amount</option></select></div>
    <div class="row"><label for="arr">Fly into</label><select id="arr"></select></div>
    <div class="row"><label for="dep">Fly home from</label><select id="dep"></select></div>
    <select id="way" aria-label="Which one"></select>
    <div class="row"><label>Taxi rides in town<small>about 7 km each</small></label><div class="step" data-k="tx"><button type="button" data-d="-1" aria-label="Fewer">−</button><output>6</output><button type="button" data-d="1" aria-label="More">+</button></div></div>
    <div class="row"><label for="jr">Japan Rail Pass<small>7 days, for long train trips</small></label><select id="jr"><option value="0">No</option><option value="1">Yes</option></select></div>
    <div class="row"><label>Rental car days<small>good for Hokkaido and the countryside; most visitors need an International Driving Permit (check current rules)</small></label><div class="step" data-k="cr"><button type="button" data-d="-1" aria-label="Fewer">−</button><output>0</output><button type="button" data-d="1" aria-label="More">+</button></div></div>
  </div>
  <section class="card res" id="res" aria-live="polite"></section>
  <section class="card keep" id="keep"><h2>Keep it, share it</h2><p class="h">Send this budget to the people you travel with, or keep a copy with its booking links. The link opens this exact budget.</p>
    <div class="sh">
      <button type="button" data-sh="wa"><svg viewBox="0 0 24 24" aria-hidden="true"><path fill="#25D366" d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2z"/><path fill="#fff" d="M8.6 7.3c.2-.4.4-.4.7-.4h.5c.2 0 .4 0 .6.5l.8 1.9c.1.2.1.4 0 .6l-.5.7c-.1.2-.2.3 0 .6.5.9 1.2 1.6 2.1 2.1.3.2.4.1.6-.1l.7-.8c.2-.2.3-.2.6-.1l1.8.9c.3.1.4.2.4.4 0 .5-.2 1.2-.7 1.6-.5.4-1.4.7-2.5.4a9 9 0 0 1-5.4-5c-.5-1.3-.2-2.4.3-3.3z"/></svg>WhatsApp</button>
      <button type="button" data-sh="copy"><svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="#0a8f78" stroke-width="2" stroke-linecap="round"><path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1"/><path d="M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/></svg><span>Copy link</span></button>
      <button type="button" data-sh="pdf"><svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="#E94560" stroke-width="2" stroke-linejoin="round"><path d="M6 2h9l5 5v15H6z"/><path d="M14 2v6h6"/></svg>Save as PDF</button>
      <button type="button" data-sh="email"><svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="#0f0f23" stroke-width="2" stroke-linejoin="round"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>Email it to me</button>
    </div>
    <div class="em" id="em" hidden>
      <form id="emf"><input type="email" id="emaddr" required autocomplete="email" placeholder="you@example.com" aria-label="Your email"><button class="send" type="submit">Send</button></form>
      <span class="f">Just this budget, with the link to open it and the booking links. <a href="/privacy-policy#packy-email-privacy">Privacy</a></span>
      <p class="err" id="emerr" hidden></p>
    </div>
  </section>
  <p class="plan">Want a day-by-day plan too? <a id="planlink" href="/?dest=Japan&amp;src=budget_plan#plan" data-go="plan">Try Plan My Trip</a>.</p>
  <details class="srcs" id="srcs"><summary>Where these prices come from</summary><ul id="srclist"></ul></details>
  <p class="note">Prices are from the operators' and JNTO's official pages (listed under "Where these prices come from"), checked %%CHECKED%%, and are rounded: they change, so check the official page before you buy. Amounts are in Japanese yen. Partner links are marked; we may earn a commission at no cost to you.</p>
</main>
<div class="bar tray" id="bar"><span class="tbadge" aria-hidden="true"><svg viewBox="0 0 64 64" width="100%" height="100%" aria-hidden="true"><rect x="12" y="18" width="40" height="38" rx="7" fill="#7cc4f5" stroke="#1f2937" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/><path d="M24 18v-6a4 4 0 0 1 4-4h8a4 4 0 0 1 4 4v6" fill="none" stroke="#1f2937" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/><path d="M22 18v38M42 18v38" fill="none" stroke="#1f2937" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/><circle cx="32" cy="34" r="5" fill="#ffd166" stroke="#1f2937" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/></svg><i id="tcount">0</i></span><div class="tmid"><div class="tth"><span class="tpp" id="tpp"></span><span class="tper" id="tper"></span><b class="tt" hidden>My Japan Trip</b><span class="tmode" id="tmode" hidden></span></div><div class="tsum" id="tsum"></div><div class="tchips" id="tchips" hidden></div></div><div class="ttot"><small>Est. budget</small><b id="barv"></b><b id="barfull"></b></div><button type="button" class="tgo" id="review">Review<span class="long"> Plan</span> <span aria-hidden="true">👉</span></button></div>
<div class="rsheet" id="rsheet" hidden role="dialog" aria-modal="true" aria-labelledby="rtitle"><div class="rhead"><span class="rico" aria-hidden="true"><svg viewBox="0 0 64 64" width="100%" height="100%" aria-hidden="true"><rect x="12" y="18" width="40" height="38" rx="7" fill="#7cc4f5" stroke="#1f2937" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/><path d="M24 18v-6a4 4 0 0 1 4-4h8a4 4 0 0 1 4 4v6" fill="none" stroke="#1f2937" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/><path d="M22 18v38M42 18v38" fill="none" stroke="#1f2937" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/><circle cx="32" cy="34" r="5" fill="#ffd166" stroke="#1f2937" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/></svg></span><div><h2 id="rtitle">Your Japan Trip</h2><p>Check your trip before you book.</p></div><button type="button" class="rx" id="rclose" aria-label="Close">✕</button></div><div class="rscroll" id="rscroll"><div class="rlist" id="rlist"></div><div class="rmore" id="rmore"></div></div><div class="rfoot"><div class="rsum" id="rsum"></div><button type="button" class="rgo" id="rgo">Next: Book <span aria-hidden="true">→</span></button></div></div>
<script>
(function(){
var D=%%DATA%%,LK=%%LINKS%%,CH='%%CHECKED%%';
var S={rm:2,ad:2,tn:0,ch:2,in:0,nt:9,nk:0,no:0,nh:0,tx:0,dn:0,cr:0,es:1,ins:1,us:0,sk:0,tr:0,gh:0,np:0,fi:0};var MAX={rm:10,ad:12,tn:10,ch:10,in:6,nt:30,nk:30,no:30,nh:30,tx:40,dn:10,cr:30,es:1,ins:1,us:5,sk:1,tr:1,gh:1,np:1,fi:1};
var CUR='JPY',CURS={JPY:['¥',1,1],USD:['$',D.usdJpy,1],INR:['₹',D.inrJpy,10]};
function y(n){var c=CURS[CUR],v=n/c[1];v=Math.round(v/c[2])*c[2];return c[0]+Math.round(v).toLocaleString('en-US');}
function esc(t){return String(t).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
function track(s,x){try{if(window.gtag)gtag('event','budget_calc',{event_category:'engagement',status:s,item:x||'',page_path:location.pathname});}catch(e){}}
var arr=document.getElementById('arr'),dep=document.getElementById('dep'),way=document.getElementById('way');
Object.keys(D.airport).forEach(function(k){arr.add(new Option(D.airport[k].name,k));dep.add(new Option(D.airport[k].name,k));});
var STY={budget:['Budget','simple hotels, konbini','budget','budget','cheap'],mid:['Mid-range','3-star, cafés','mid','mid','train'],comfort:['Comfort','4-star, dinners out','upscale','treat','taxi']},STYLE='mid';
var SEMO={budget:'💰',mid:'✨',comfort:'💎'};function styleBtns(){document.getElementById('styles').innerHTML=Object.keys(STY).map(function(k){return '<button type="button" role="radio" data-sty="'+k+'" aria-checked="'+(k===STYLE)+'"><span aria-hidden="true">'+SEMO[k]+'</span>'+STY[k][0]+'</button>';}).join('');}
function cheapest(k){var best=null;D.airport[k].ways.forEach(function(w){if(w.car)return;var v=w.a*2+(w.c||0);if(!best||v<best.v)best={w:w,v:v};});return best&&best.w;}
document.getElementById('styles').addEventListener('click',function(e){var b=e.target.closest('[data-sty]');if(!b)return;STYLE=b.getAttribute('data-sty');var st=STY[STYLE];
 document.getElementById('hstyle').value=st[2];document.getElementById('fstyle').value=st[3];
 var av=kindsOf(arr.value);if(st[4]==='cheap'){var c=cheapest(arr.value);if(c){KIND=c.k;ways();way.value=c.id;}}else{KIND=av[st[4]]?st[4]:'train';if(!av[KIND])KIND=D.airport[arr.value].ways[0].k;ways();}
 styleBtns();track('style',STYLE);styleUI();});
var KINDS=[['train','🚆','Train'],['bus','🚌','Bus'],['taxi','🚕','Taxi'],['private','🚐','Private car']],KIND='';
function kindsOf(k){var a=D.airport[k].ways,o={private:1};a.forEach(function(w){o[w.k]=1;});return o;}
function ways(keep){var a=D.airport[arr.value],have=kindsOf(arr.value);if(!have[KIND])KIND=a.ways[0].k;
 document.getElementById('kinds').innerHTML=KINDS.map(function(x){return '<button type="button" role="radio" data-kind="'+x[0]+'" aria-checked="'+(x[0]===KIND)+'"'+(have[x[0]]?'':' disabled')+'><span aria-hidden="true">'+x[1]+'</span>'+x[2]+'</button>';}).join('');
 var list=a.ways.filter(function(w){return w.k===KIND;}),cur=way.value;way.innerHTML='';list.forEach(function(w){way.add(new Option(w.s,w.id));});
 if(KIND==='private')way.add(new Option('Private car','private'));if(keep&&[].some.call(way.options,function(o){return o.value===cur;}))way.value=cur;way.hidden=way.options.length<2;}
document.getElementById('kinds').addEventListener('click',function(e){var b=e.target.closest('[data-kind]');if(!b||b.disabled)return;KIND=b.getAttribute('data-kind');ways();track('kind',KIND);calc();});
// a link from Packy can fill the form: ?ad=2&ch=2&nt=9
S.rm=Math.max(1,Math.ceil((S.ad+S.ch)/2));try{var q=new URLSearchParams(location.search);/* also dn= Disney days */Object.keys(S).forEach(function(k){var v=parseInt(q.get(k),10);if(!isNaN(v))S[k]=Math.max(0,Math.min(MAX[k],v));});}catch(e){}
[].forEach.call(document.querySelectorAll('.step'),function(st){var k=st.getAttribute('data-k');st.querySelector('output').textContent=S[k];
 st.addEventListener('click',function(e){var b=e.target.closest('[data-d]');if(!b)return;S[k]=Math.max(k==='ad'?1:0,Math.min(MAX[k],S[k]+(+b.getAttribute('data-d'))));st.querySelector('output').textContent=S[k];calc();});});
// the likely airport for the trip: Kansai for a Kyoto and Osaka trip, New Chitose for Hokkaido only
var ap=S.nt?'narita':(S.nk||S.no?'kansai':(S.nh?'chitose':'narita'));arr.value=ap;dep.value=ap;ways();if(ap==='kansai'&&S.no&&!S.nk)way.value='haruka-o';
var Q0={};try{new URLSearchParams(location.search).forEach(function(v,k){Q0[k]=v;});}catch(e){}
function setSel(id,v){var el=document.getElementById(id);if(v&&[].some.call(el.options,function(o){return o.value===v;}))el.value=v;}
if(Q0.a){setSel('arr',Q0.a);ways();}if(Q0.w){if(Q0.w==='private')KIND='private';else D.airport[arr.value].ways.forEach(function(x){if(x.id===Q0.w)KIND=x.k;});ways();}if(Q0.d){setSel('dep',Q0.d);if(Q0.d!==arr.value)dep.dataset.set='1';}setSel('way',Q0.w);setSel('jr',Q0.jr);setSel('zoo',Q0.zo);setSel('sanrio',Q0.sa);setSel('hstyle',Q0.hs);setSel('fstyle',Q0.fs);setSel('from',Q0.fr);
[['ho','hotel'],['fo','food'],['fl','fly']].forEach(function(x){var v=parseInt(Q0[x[0]],10);if(v>0&&v<1e8)document.getElementById(x[1]).value=v;});
arr.addEventListener('change',function(){ways();if(dep.value!==arr.value&&!dep.dataset.set)dep.value=arr.value;calc();});
dep.addEventListener('change',function(){dep.dataset.set='1';calc();});
[way,document.getElementById('jr'),document.getElementById('zoo'),document.getElementById('sanrio')].forEach(function(x){x.addEventListener('change',calc);});
['hotel','food','fly'].forEach(function(id){document.getElementById(id).addEventListener('input',calc);});
function styleUI(){var hs=document.getElementById('hstyle').value,fs=document.getElementById('fstyle').value,H=D.hotelStyles[hs],F=D.foodStyles[fs];
 var hh=document.getElementById('hhint');document.getElementById('hinfo').hidden=!H;if(H)hh.innerHTML='<b>'+esc(H.name)+':</b> '+esc(H.desc)+'. Per room per night, room only (breakfast is counted under food): '+['nt','nk','no','nh'].map(function(k){return esc(D.areaNames[k])+' '+y(H.by[k][0])+'–'+y(H.by[k][1]);}).join(', ')+'; '+esc(D.styleNote)+'.';
 document.getElementById('hrooms').hidden=!H;document.getElementById('hown').hidden=hs!=='own';
 var fh=document.getElementById('fhint');document.getElementById('finfo').hidden=!F;if(F)fh.innerHTML='<b>'+esc(F.name)+':</b> '+esc(F.desc)+'.'+' About '+y(F.lo)+'–'+y(F.hi)+' per adult per day for three meals, breakfast included, since many hotels charge extra for it (children about half); '+esc(D.foodNote)+'.';
 document.getElementById('fown').hidden=fs!=='own';calc();}
var FARE=null,fareKey='';
function dt(iso){try{return new Date(iso+'T00:00:00').toLocaleDateString('en-GB',{day:'numeric',month:'short',year:'numeric'});}catch(e){return iso;}}
function cityTo(){return {narita:'TYO',haneda:'TYO',kansai:'OSA',chitose:'SPK'}[arr.value]||'TYO';}
function fareUI(){var f=document.getElementById('from').value,fh=document.getElementById('flyhint');
 document.getElementById('flyown').hidden=f!=='own';fh.hidden=!f||f==='own';if(!f||f==='own'){FARE=null;calc();return;}
 var key=f+'-'+cityTo();if(key===fareKey&&FARE){calc();return;}fareKey=key;FARE=null;fh.textContent='Looking up recent fares…';calc();
 fetch('/api/flight-price?from='+f+'&to='+cityTo()).then(function(r){return r.json();}).then(function(j){if(key!==fareKey)return;
  if(j&&j.ok){FARE=j;fh.innerHTML='<b>Economy, return:</b> about '+y(j.lo)+'–'+y(j.hi)+' per person, from recent fares found in flight searches (checked '+esc(dt(j.checked))+'). Fares change daily.';}
  else{fh.textContent='No recent fare found for this route yet. Choose "Somewhere else" to type your own.';}calc();})
 .catch(function(){if(key===fareKey){fh.textContent='Fares could not be loaded right now. Choose "Somewhere else" to type your own.';calc();}});}
document.getElementById('from').addEventListener('change',function(){track('from',this.value);fareUI();});
arr.addEventListener('change',function(){if(FARE||fareKey)fareUI();});
['hstyle','fstyle'].forEach(function(id){document.getElementById(id).addEventListener('change',function(){track(id,this.value);STYLE='';styleBtns();styleUI();});});
function num(id){var v=parseFloat(document.getElementById(id).value);return isNaN(v)||v<0?0:v;}
var SRC=[];function reg(o){if(o&&o.url&&!SRC.some(function(x){return x[1]===o.url;}))SRC.push([o.src||'',o.url]);return '';}
function src(name,url){reg({src:name,url:url});return '<small>'+esc(name)+', checked '+CH+'</small>';}
var LICON=[[/Universal/,'globe','#e6efff'],[/Shibuya Sky/,'sky','#efe9ff'],[/Skytree/,'tower','#e6efff'],[/Ghibli/,'leaf','#e6faf5'],[/Nara/,'deer','#fff3c4'],[/Fushimi/,'torii','#ffe3e3'],[/Disney|theme park|Theme park/,'castle','#fff3c4'],[/Sanrio/,'bow','#ffe3ea'],[/Zoo/,'panda','#e6f6ea'],[/^Flights/,'plane','#e6efff'],[/^Hotel/,'bag','#fff3c4'],[/^Food/,'coffee','#fff3c4'],
 [/Shinkansen|Rail Pass/,'train','#e6efff'],[/Private car/,'van','#ffe3e3'],[/taxi × 2|Fixed-fare/,'taxi','#fff3c4'],[/Limousine|bus/i,'bus','#e6faf5'],[/Airport|subway|Keikyu|Children/,'train','#e6efff'],
 [/Taxi/,'taxi','#fff3c4'],[/Rental car/,'car','#ffe3e3'],[/Departure tax/,'receipt','#f4faf8'],[/eSIM/,'phone','#e6efff'],[/insurance/,'health','#e6faf5'],[/Hokkaido/,'mount','#e6efff']];
function line(label,v,note){var links='',m=note&&note.match(/<a class="bkl"[\s\S]*?<\/a>/g);if(m)m.forEach(function(a){note=note.replace(a,'');links+=a;});
 var t=String(label).replace(/<[^>]+>/g,''),ic=LICON.filter(function(x){return x[0].test(t);})[0]||['receipt','receipt','#f4faf8'];
 return '<div class="ln"><span class="li" style="background:'+ic[2]+'" aria-hidden="true">'+((window.__ICON||{})[ic[1]]||'')+'</span><div class="l"><b class="lt">'+label+'</b><div class="lp">'+v+'</div>'+(note||'')+'</div>'+(links?'<div class="lk">'+links+'</div>':'')+'</div>';}
function bk(k,t){var l=LK[k];if(!l)return '';var off=l[2]==='official';return '<a class="bkl" href="'+esc(l[1])+'" target="_blank" rel="'+(off?'noopener':'nofollow noopener sponsored')+'"'+(off?'':' data-ps-placement="budget-'+k+'"')+' data-go="'+k+'">'+esc(t||'Check final price')+' →</a>';}
function gyg(q,tag,t){return '<a class="bkl" href="https://www.getyourguide.com/s/?q='+encodeURIComponent(q)+'&partner_id=D7IXONS&cmp=ps-budget-'+tag+'" target="_blank" rel="nofollow noopener sponsored" data-ps-placement="budget-'+tag+'" data-go="'+tag+'">'+esc(t||'Check final price')+' →</a>';}
function go(k){var l=LK[k],off=l[2]==='official';return '<a class="go" href="'+esc(l[1])+'"'+(off?' target="_blank" rel="noopener"':l[2]?' target="_blank" rel="nofollow noopener sponsored" data-ps-placement="budget-'+k+'"':'')+' data-go="'+k+'">'+esc(l[0])+'<small>'+(off?'official site ↗':l[2]?'partner link ↗':'→')+'</small></a>';}
function calc(){
 SRC=[];var tn=S.tn,ad=S.ad+tn,ch=S.ch,inf=S.in,ppl=ad+ch+inf,nights=S.nt+S.nk+S.no+S.nh,kan=S.nk+S.no,days=nights+1,cars=Math.ceil(ppl/4),h='',sum=0,lo=0,hi=0,miss=[];
 // airport to town, both ends
 // the airport trips, both ways, as one line: the way back is the same kind from the airport you fly home from
 function pick(k,wid){var a=D.airport[k].ways;return a.filter(function(x){return x.id===wid;})[0]||a.filter(function(x){return x.k===KIND;})[0]||a[0];}
 function cost(w){if(!w)return null;if(w.car)return {lo:w.car[0]*cars,hi:w.car[1]*cars};var v=w.a*ad+(w.c||0)*ch;if(w.c===null&&ch&&miss.indexOf(w.s)<0)miss.push('Children\'s fare on the '+w.s);return {lo:v,hi:v};}
 function airLine(){var wi=KIND==='private'?null:pick(arr.value,way.value),wo=KIND==='private'?null:(dep.value===arr.value?wi:pick(dep.value,''));
  var bkCar=bk('transfer',KIND==='taxi'?'Pre-book a private car':KIND==='private'?'Check final price':'Or a private car');
  if(!wi||!wo){var t=KIND==='private'?'Private car, both ways':'Airport transfers';return line(t+(cars>1&&KIND==='private'?' ('+cars+' cars)':''),'<span class="np">not priced yet</span>','<small>'+(KIND==='private'?'a pre-booked car meets you at arrivals':'choose how you will get to and from the airport')+'</small>'+bkCar);}
  var both=wi===wo,nexBoth=both&&wi.id==='nex',ci=cost(wi),co=nexBoth?{lo:0,hi:0}:cost(wo),l=ci.lo+co.lo,h=ci.hi+co.hi;if(l===h)sum+=l;else{lo+=l;hi+=h;}
  var what=nexBoth?'Narita Express round trip':both?wi.s+' × 2':wi.s+' in, '+wo.s+' out';
  return line('Airport transfers, both ways: '+esc(what)+(wi.car&&cars>1?' ('+cars+' cars)':''),l===h?y(l):y(l)+'–'+y(h),src(wi.src,wi.url)+(both?'':src(wo.src,wo.url))+(wi.id==='nex'&&!both?'<small>the Narita Express visitor ticket is a round trip</small>':'')+(wi.q?gyg(wi.q,'air-'+wi.id.split('-')[0]):'')+bkCar);}
 var G={exp:'',fly:'',stay:'',rail:'',move:'',pre:''};
 G.move+=airLine();
 if(S.cr)G.move+=line('Rental car: '+S.cr+' day'+(S.cr>1?'s':''),'<span class="np">not priced yet</span>','<small>plus fuel, tolls and parking; most visitors need an International Driving Permit (check current rules)</small>'+bk('car'));
 if(S.nt){var t=D.tokyoTicket,n=Math.ceil((S.nt+1)/t.days),v=n*(t.a*ad+t.c*ch);sum+=v;G.move+=line('Tokyo subway: '+n+' × 72-hour ticket'+(n>1?'s':''),y(v),src(t.src,t.url)+bk('subway'));}
 if(S.nk){var kd=D.kyotoDay,kv=S.nk*(kd.a*ad+kd.c*ch);sum+=kv;G.move+=line('Kyoto buses and subway: '+S.nk+' one-day pass'+(S.nk>1?'es':''),y(kv),'<small>'+esc(kd.src)+', checked 27 Nov 2026'+reg(kd)+'</small>');}
 if(S.no){var od=D.osakaDay,ol=S.no*(od.lo*ad+od.c*ch),oh=S.no*(od.hi*ad+od.c*ch);lo+=ol;hi+=oh;G.move+=line('Osaka subway and buses: '+S.no+' one-day pass'+(S.no>1?'es':''),y(ol)+'–'+y(oh),'<small>'+esc(od.src)+', checked 27 Nov 2026'+reg(od)+'</small>');}
 if(S.nh){var s=D.sapporoDay,v=S.nh*(s.a*ad+s.c*ch);sum+=v;G.move+=line('Sapporo subway: '+S.nh+' one-day ticket'+(S.nh>1?'s':''),y(v),src(s.src,s.url));}
 if(S.tx){var tl=S.tx*cars*D.taxi.lo,th=S.tx*cars*D.taxi.hi;lo+=tl;hi+=th;G.move+=line('Taxi rides in town: '+S.tx+' ride'+(S.tx>1?'s':'')+(cars>1?' × '+cars+' cars':''),y(tl)+'–'+y(th),src(D.taxi.src,D.taxi.url));}
 if(document.getElementById('jr').value==='1'){var j=D.jrpass,v=j.a*ad+j.c*ch;sum+=v;G.rail+=line('Japan Rail Pass, 7 days',y(v),src(j.src,j.url)+bk('jrpass'));}
 if(S.dn){var d=D.disney,dc=D.disneyChild,ga=S.ad,kid=(dc.c*ch+dc.j*tn)*S.dn,dl=d.lo*ga*S.dn+kid,dh=d.hi*ga*S.dn+kid;lo+=dl;hi+=dh;
  var who=[ga+' adult'+(ga>1?'s':''),tn?tn+' teen'+(tn>1?'s':''):'',ch?ch+' child'+(ch>1?'ren':''):''].filter(Boolean).join(' + ');
  G.exp+=line('Tokyo Disney: '+who+' × '+S.dn+' day'+(S.dn>1?'s':''),y(dl)+'–'+y(dh),'<small>Adults: '+esc(d.src)+', checked '+d.checked+''+reg(d)+''+(tn||ch?'. '+esc(dc.src).charAt(0).toUpperCase()+esc(dc.src).slice(1)+'.':'')+(inf?' Under 4: free; ages 4 and 5 pay the child price.':'')+'</small>'+bk('parks'));}
 if(document.getElementById('sanrio').value==='1'){var r=D.sanrio,sn=ad+ch,sl=r.lo*sn,sh=r.hi*sn;lo+=sl;hi+=sh;
  G.exp+=line('Sanrio Puroland: '+sn+' × '+y(r.lo)+'–'+y(r.hi),y(sl)+'–'+y(sh),'<small>'+esc(r.src)+', checked '+r.checked+(inf?'. Little ones aged 3 to 5 also need a ticket.':'')+'</small>'+bk('sanrio'));}
 if(S.us){var u=D.usj,ul=u.a*ad*S.us;sum+=ul;if(ch)miss.push('Children\'s USJ tickets');G.exp+=line('Universal Studios Japan: '+ad+' × from '+y(u.a)+' × '+S.us+' day'+(S.us>1?'s':''),'from '+y(ul),'<small>'+esc(u.src)+', checked '+u.checked+reg(u)+'</small>'+gyg('universal studios japan tickets','usj'));}
 if(S.sk){var k2=D.shibuyasky,sl2=k2.lo*ad+k2.c*ch,sh2=k2.hi*ad+k2.c*ch;lo+=sl2;hi+=sh2;G.exp+=line('Shibuya Sky: '+ad+' × '+y(k2.lo)+'–'+y(k2.hi)+(ch?', '+ch+' × '+y(k2.c):''),y(sl2)+'–'+y(sh2),'<small>'+esc(k2.src)+', checked '+k2.checked+reg(k2)+'</small>'+gyg('shibuya sky','shibuyasky'));}
 if(S.tr){var t2=D.skytree,tl2=t2.alo*ad+t2.clo*ch,th2=t2.ahi*ad+t2.chi*ch;lo+=tl2;hi+=th2;G.exp+=line('Tokyo Skytree: '+ad+' adult'+(ad>1?'s':'')+(ch?' + '+ch+' child'+(ch>1?'ren':''):''),y(tl2)+'–'+y(th2),'<small>'+esc(t2.src)+', checked '+t2.checked+'; teens 12 to 14 pay the child price'+reg(t2)+'</small>'+gyg('tokyo skytree','skytree'));}
 if(S.gh){var g2=D.ghibli,gl2=g2.a*S.ad+g2.t*tn+g2.c*ch,gh2=gl2+g2.i*inf;lo+=gl2;hi+=gh2;G.exp+=line('Ghibli Museum, Mitaka',y(gl2)+(gh2>gl2?'–'+y(gh2):''),'<small>'+esc(g2.src)+', checked '+g2.checked+reg(g2)+'</small>');}
 if(S.np)G.exp+=line('Nara Park and its deer','Free','<small>the park is free; deer crackers are sold in the park</small>');
 if(S.fi)G.exp+=line('Fushimi Inari Taisha, Kyoto','Free','<small>the shrine and its gates are free to walk</small>');
 if(document.getElementById('zoo').value==='1'){var z=D.uenozoo,v=z.a*ad;sum+=v;G.exp+=line('Ueno Zoo: '+ad+' × '+y(z.a)+(ch||inf?' (children up to 6th grade free)':''),y(v),'<small>'+esc(z.src)+', checked '+z.checked+''+reg(z)+'</small>');}
 // Shinkansen between Tokyo and Kyoto: one ride if the trip flies into one and out of the other, else there and back
 var REG={narita:'t',haneda:'t',kansai:'k',chitose:'h'},jrp=document.getElementById('jr').value==='1';
 if(S.nt&&kan&&!jrp){var sk=S.nk?D.shinkansen:{a:D.shinkansenOsaka.a,c:D.shinkansenOsaka.c,src:D.shinkansen.src,url:D.shinkansen.url,checked:D.shinkansen.checked},rides=REG[arr.value]!==REG[dep.value]?1:2,bl=((sk.a-200)*ad+(sk.c-100)*ch)*rides,bh=((sk.a+400)*ad+(sk.c+200)*ch)*rides;lo+=bl;hi+=bh;
  G.rail+=line('Shinkansen Tokyo ⇄ '+(S.nk?'Kyoto':'Shin-Osaka')+': '+rides+' ride'+(rides>1?'s':'')+' each',y(bl)+'–'+y(bh),'<small>'+esc(sk.src)+', checked '+sk.checked+(inf?'; under 6 free on a lap':'')+''+reg(sk)+'</small>'+bk('shinkansen'));}
 if(S.nt&&kan&&jrp)G.rail+=line('Shinkansen Tokyo ⇄ Kyoto','with the pass','<small>The Japan Rail Pass covers Hikari and Kodama trains; Nozomi needs an extra ticket (4,960 yen per ride between Tokyo and Kyoto, japanrailpass.net, checked 24 Nov 2026).</small>');
 var tx=D.tax.each*ppl;sum+=tx;G.pre+=line('Departure tax: '+ppl+' × '+y(D.tax.each),y(tx),'<small>JNTO, checked '+CH+'; check JNTO for who is exempt'+reg(D.tax)+'</small>');
 // the reader's own numbers
 var hs=document.getElementById('hstyle').value,fs=document.getElementById('fstyle').value,H=D.hotelStyles[hs],F=D.foodStyles[fs];
 var fr=document.getElementById('from').value,hot=hs==='own'?num('hotel'):0,food=fs==='own'?num('food'):0,fly=fr==='own'?num('fly'):0,own='',hotDone=!!hot,foodDone=!!food,flyDone=!!fly;
 if(hot){G.stay+=line('Hotel: '+nights+' nights × '+y(hot),y(hot*nights));sum+=hot*nights;}
 if(H&&H.by&&nights){var hl=0,hh2=0,hw=[];['nt','nk','no','nh'].forEach(function(k){if(S[k]){hl+=H.by[k][0]*S.rm*S[k];hh2+=H.by[k][1]*S.rm*S[k];hw.push(S[k]+' in '+D.areaNames[k]);}});lo+=hl;hi+=hh2;hotDone=true;G.stay+=line('Hotel, '+esc(H.name.toLowerCase())+': '+S.rm+' room'+(S.rm>1?'s':'')+', '+nights+' night'+(nights>1?'s':''),y(hl)+'–'+y(hh2),'<small>'+esc(hw.join(', '))+'; '+esc(D.styleNote)+'</small>');}
 if(food){G.stay+=line('Food: '+(ad+ch+inf)+' people × '+days+' days × '+y(food),y(food*ppl*days));sum+=food*ppl*days;}
 if(F&&F.lo){var fw=ad+(ch+inf)/2,fl=Math.round(F.lo*fw*days),fh2=Math.round(F.hi*fw*days);lo+=fl;hi+=fh2;foodDone=true;G.stay+=line('Food, '+esc(F.name.toLowerCase())+': '+ppl+' '+(ppl>1?'people':'person')+' × '+days+' days',y(fl)+'–'+y(fh2),'<small>'+y(F.lo)+'–'+y(F.hi)+' per adult per day, three meals including breakfast'+(ch+inf?'; children about half':'')+'; '+esc(D.foodNote)+'</small>');}
 if(fly){G.fly+=line('Flights',y(fly),bk('flights'));sum+=fly;}
 if(FARE&&fr&&fr!=='own'){var fp=ppl,fl2=FARE.lo*fp,fh3=FARE.hi*fp;lo+=fl2;hi+=fh3;flyDone=true;G.fly+=line('Flights, economy return: '+fp+' × '+y(FARE.lo)+'–'+y(FARE.hi),y(fl2)+'–'+y(fh3),'<small>Recent fares found in flight searches, checked '+esc(dt(FARE.checked))+'. Babies under 2 usually pay much less; fares change daily.</small>'+bk('flights'));}
 // what is not priced
 var np='';
 if(!flyDone)G.fly+=line('Flights','<span class="np">not priced</span>','<small>choose your city in the Flight tab, or type your fare</small>'+bk('flights','Search flights'));
 if(!hotDone)G.stay+=line('Hotels','<span class="np">not priced</span>','<small>choose a hotel level in the Stays tab</small>');
 if(!foodDone)G.stay+=line('Food and drinks','<span class="np">not priced</span>','<small>choose a food style in the Food tab</small>');
 G.exp+=line(S.dn||document.getElementById('sanrio').value==='1'?'Other theme parks and tickets':'Theme parks and tickets','<span class="np">not priced yet</span>',bk('parks','See tickets'));
 if(S.es){var ep=D.esim.plans.filter(function(x){return x[0]>=days;})[0]||D.esim.plans[D.esim.plans.length-1],en=Math.max(1,Math.ceil(days/ep[0])),ev=Math.round(ep[2]*en*ad*D.usdJpy/10)*10;sum+=ev;
 G.pre+=line('eSIM data: '+ad+' phone'+(ad>1?'s':'')+' × '+(en>1?en+' × ':'')+ep[1]+' GB, '+ep[0]+' days',y(ev),'<small>US$'+(ep[2]%1?ep[2].toFixed(2):ep[2])+' each, '+esc(D.esim.src)+'; one per adult and teen; at about ¥'+D.usdJpy+' to US$1</small>'+bk('esim'));}
 if(S.ins){var il=Math.round(D.insurance.lo*days*ad*D.usdJpy/100)*100,ih=Math.round(D.insurance.hi*days*ad*D.usdJpy/100)*100;lo+=il;hi+=ih;
 G.pre+=line('Travel medical insurance: '+ad+' × '+days+' days',y(il)+'–'+y(ih),'<small>'+esc(D.insurance.src)+(ch+inf?'; ask the quote about children':'')+'; at about ¥'+D.usdJpy+' to US$1</small>'+bk('insurance','Get a quote'));}
 if(S.nh&&(S.nt||S.nk))G.move+=line('Getting to Hokkaido (usually a domestic flight)','<span class="np">not priced</span>');
 miss.forEach(function(m){G.move+=line(esc(m),'<span class="np">not priced yet</span>');});
  // each section shows its own lines and subtotal (from the line amounts); the summary card adds them up
  function grp(t,x){return x?'<div class="grp">'+t+'</div>'+x:'';}
  var all=G.exp+G.fly+G.stay+G.rail+G.move+G.pre,npn=(all.match(/class="np"/g)||[]).length;
  var tlo=sum+lo,thi=sum+hi,tv=y(tlo)+(thi>tlo?'–'+y(thi).replace(/^[¥$₹]/,''):'');TOT={lo:Math.round(tlo),hi:Math.round(thi),ppl:ppl,nights:nights};
  h='<div class="rhead ihead"><span class="rico" aria-hidden="true">'+(window.__ICON||{}).bag+'</span><div><h2>Your trip, itemised</h2><p>Check each price, then book. Booking links are partner links: we may earn a commission, at no cost to you.</p></div></div>'+grp('Things to do',G.exp)+grp('Flights, hotel and food',G.fly+G.stay)+grp('Getting around',G.rail+G.move)+grp('Before you go',G.pre)+'<div class="rsum total" id="total"><p class="printsum">'+esc(summary())+'</p><div><span>🧭 Travel style</span><span class="pill">'+esc(STYLE?STY[STYLE][0]:'Custom')+'</span></div><div><span>👨‍👩‍👧‍👦 Who and how long</span><span>'+ppl+' '+(ppl>1?'people':'person')+' · '+nights+' night'+(nights>1?'s':'')+'</span></div>'+
    '<div><span>🙋 Per person</span><span>'+y(tlo/Math.max(1,ppl))+(thi>tlo?'–'+y(thi/Math.max(1,ppl)).replace(/^[¥$₹]/,''):'')+'</span></div>'+(npn?'<div class="soft"><span>Not priced yet</span><span>'+npn+' item'+(npn>1?'s':'')+'</span></div>':'')+
    '<div class="gt"><span>Estimated total</span><span>'+tv+'</span></div>'+(CUR!=='JPY'?'<div class="soft"><span>Rates</span><span>about ¥'+D.usdJpy+' = US$1, ¥'+D.inrJpy+' = ₹1</span></div>':'')+'</div>';
  if(%%TOURS%%)h+='<div class="grp">Prefer one booking?</div><div class="two"><div><span>A guided multi-day tour: hotels, trains and a guide arranged by the tour company. Flights are usually separate. Compare its price with your budget above.</span>'+go(ch||inf?'tours_family':'tours')+'</div></div>';
  document.getElementById('res').innerHTML=h;
  var cc=CURS[CUR];function k(n){n=n/cc[1];return n>=995000?(n/1e6).toFixed(2).replace(/\.?0+$/,'')+'M':n>=1e4?Math.round(n/1000)+'K':Math.round(n).toLocaleString('en-US');}document.getElementById('barv').textContent=cc[0]+k(tlo)+(thi>tlo?'–'+k(thi):'');document.getElementById('barv').setAttribute('data-full',tv);document.getElementById('barfull').textContent=tv;document.getElementById('tpp').textContent=ppl+' people · '+nights+' nights';document.getElementById('tper').textContent='~'+y(tlo/Math.max(1,ppl))+(thi>tlo?'–'+y(thi/Math.max(1,ppl)).replace(/^[¥$₹]/,''):'')+' / person';
  document.getElementById('srclist').innerHTML=SRC.map(function(x){return '<li><a href="'+esc(x[1])+'" target="_blank" rel="noopener">'+esc(x[0]||x[1])+'</a></li>';}).join('');
  sync();items();kidsUI();if(TAB==='review')rrows();var bb=document.getElementById('bar');if(bb.getAttribute('data-v')!==tv){bb.setAttribute('data-v',tv);bb.classList.remove('tick');void bb.offsetWidth;bb.classList.add('tick');}
 document.getElementById('planlink').href='/?dest=Japan&adults='+ad+'&kids='+(ch+inf)+'&src=budget_plan#plan';
 saveUrl();
}
document.getElementById('res').addEventListener('click',function(e){var a=e.target.closest('[data-go]');if(!a)return;track('link',a.getAttribute('data-go'));var pl=a.getAttribute('data-ps-placement');if(pl)try{if(window.gtag)gtag('event','affiliate_interact',{event_category:'monetization',placement:pl,page_path:location.pathname});}catch(x){}});
// ---- the trip in the address: Copy link, WhatsApp and the email all open this exact budget
var TOT=null,SEL={a:'arr',d:'dep',w:'way',jr:'jr',zo:'zoo',sa:'sanrio',hs:'hstyle',fs:'fstyle',fr:'from'},OWN={ho:'hotel',fo:'food',fl:'fly'};
function qs(){var q=[];Object.keys(S).forEach(function(k){q.push(k+'='+S[k]);});Object.keys(SEL).forEach(function(k){var v=document.getElementById(SEL[k]).value;if(v&&v!=='0')q.push(k+'='+encodeURIComponent(v));});
 Object.keys(OWN).forEach(function(k){var v=num(OWN[k]);if(v)q.push(k+'='+Math.round(v));});q.push('st='+(STYLE||'x'));if(CUR!=='JPY')q.push('cu='+CUR);return q.join('&');}
function saveUrl(){try{history.replaceState(null,'',location.pathname+'?'+qs());}catch(e){}}
function link(src){return 'https://www.packsmartapp.com/japan-budget?'+qs()+'&src='+src;}
function summary(){var w=[S.ad+S.tn+' adult'+(S.ad+S.tn>1?'s':'')];if(S.ch)w.push(S.ch+' child'+(S.ch>1?'ren':''));if(S.in)w.push(S.in+' under 6');
 var n=['nt','nk','no','nh'].filter(function(k){return S[k];}).map(function(k){return S[k]+' in '+D.areaNames[k];});return 'Japan: '+w.join(', ')+'; '+(n.join(', ')||'no nights yet')+'.';}
function done(){try{return JSON.parse(localStorage.getItem('budgetDone')||'{}')||{};}catch(e){return {};}}
document.getElementById('res').addEventListener('change',function(e){var c=e.target.closest('[data-ck]');if(!c)return;var d=done();if(c.checked)d[c.getAttribute('data-ck')]=1;else delete d[c.getAttribute('data-ck')];
 try{localStorage.setItem('budgetDone',JSON.stringify(d));}catch(x){}c.closest('.ck').classList.toggle('done',c.checked);if(c.checked)track('booked',c.getAttribute('data-ck'));});
var em=document.getElementById('em'),emf=document.getElementById('emf'),emerr=document.getElementById('emerr'),SENT='';
document.getElementById('keep').addEventListener('click',function(e){var b=e.target.closest('[data-sh]');if(!b)return;var k=b.getAttribute('data-sh');track('share',k);
 var msg='Our Japan trip budget: about '+(TOT?y(TOT.lo)+(TOT.hi>TOT.lo?'–'+y(TOT.hi).replace(/^[¥$₹]/,''):''):'')+'. '+summary()+' See the breakdown: ';
 if(k==='wa')window.open('https://wa.me/?text='+encodeURIComponent(msg+link('budget_wa')),'_blank','noopener');
 if(k==='copy'){var u=link('budget_link'),sp=b.querySelector('span');function ok(){sp.textContent='Copied ✓';setTimeout(function(){sp.textContent='Copy link';},2000);}
  if(navigator.clipboard)navigator.clipboard.writeText(u).then(ok,function(){prompt('Copy this link:',u);});else prompt('Copy this link:',u);}
 if(k==='pdf'){[].forEach.call(document.querySelectorAll('details'),function(d){d.open=true;});window.print();}
 if(k==='email'){em.hidden=!em.hidden;if(!em.hidden){try{var m=localStorage.getItem('packyEmail');if(m)document.getElementById('emaddr').value=m;}catch(x){}document.getElementById('emaddr').focus();}}});
function post(body){return fetch('/api/email-chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}).then(function(r){return r.json();});}
function topics(){var t=[];if(S.nt)t.push('tokyo');if(S.nk)t.push('kyoto');if(S.no)t.push('osaka');if(S.nh)t.push('hokkaido');if(S.ch||S.in||S.dn)t.push('kids');if(document.getElementById('jr').value==='1')t.push('rail_pass');
 if(S.nt&&(S.nk||S.no))t.push('shinkansen');t.push(document.getElementById('arr').value);return t;}
emf.addEventListener('submit',function(e){e.preventDefault();var addr=document.getElementById('emaddr').value.trim(),btn=emf.querySelector('.send');emerr.hidden=true;btn.disabled=true;btn.textContent='Sending…';
 post({kind:'budget',country:'japan',email:addr,q:qs(),lo:TOT&&TOT.lo,hi:TOT&&TOT.hi}).then(function(j){btn.disabled=false;btn.textContent='Send';
  if(!j||!j.ok){emerr.textContent=(j&&j.error)||'Sorry, that did not work. Please try again.';emerr.hidden=false;track('email','failed');return;}
  try{localStorage.setItem('packyEmail',addr);}catch(x){}SENT=addr;track('email','sent');
  em.innerHTML='<p class="ok">Sent to <b>'+esc(addr)+'</b> ✓ Check your inbox (and the spam folder, just in case).</p><p class="ok" style="margin-top:10px">Would you like a few Japan trip tips before you go? Only for your trip, stop any time.</p><button type="button" class="tips" id="tipsyes">Yes please</button>';
  document.getElementById('tipsyes').addEventListener('click',function(){var t=this;t.disabled=true;post({update:true,tips:true,from:'budget',country:'japan',email:SENT,topics:topics()}).then(function(r){
   t.outerHTML=r&&r.ok?'<p class="ok" style="margin-top:8px">Done. Your first trip tip is on its way ✓</p>':'<p class="err">Sorry, that did not work. Please try again later.</p>';track('tips',r&&r.ok?'yes':'failed');},function(){t.disabled=false;});});
 },function(){btn.disabled=false;btn.textContent='Send';emerr.textContent='Sorry, that did not work. Please try again.';emerr.hidden=false;});});
// the floating total while the reader fills in the form; hidden once the full total is on screen
var bar=document.getElementById('bar');  // the tray stays on screen, like the owner's reference
// ---- tap controls (28 Nov): each group sets the original control behind it, so prices, links and shared links work as before
function $(id){return document.getElementById(id);}
function fire(x){x.dispatchEvent(new Event('change'));}
function setS(k,v){S[k]=v;var o=document.querySelector('.step[data-k="'+k+'"] output');if(o)o.textContent=v;}
var WHO={solo:[1,0,0,0,'👤 Solo'],couple:[2,0,0,0,'💑 Couple'],family:[2,0,2,0,'👨‍👩‍👧‍👦 Family'],friends:[4,0,0,0,'👯 Friends']};
var POP=['LAX','NYC','LON','SYD','SIN','HKG','SEL','BKK','BOM','TPE'],OTHER=false;
function cityName(c){var o=[].filter.call($('from').options,function(x){return x.value===c;})[0];return o?o.text:c;}
function short(o){return o.map(function(x){return [x[0],x[1].replace(/ \(.*\)/,'')];});}
function opts(sel){return [].map.call(sel.options,function(o){return [o.value,o.text];});}
function GROUPS(){var fv=$('from').value;return {
 who:{o:Object.keys(WHO).map(function(k){return [k,WHO[k][4]];}),v:Object.keys(WHO).filter(function(k){var w=WHO[k];return w[0]===S.ad&&w[1]===S.tn&&w[2]===S.ch&&w[3]===S.in;})[0]||'',
  set:function(v){var w=WHO[v];setS('ad',w[0]);setS('tn',w[1]);setS('ch',w[2]);setS('in',w[3]);setS('rm',Math.max(1,Math.ceil((w[0]+w[1]+w[2])/2)));calc();}},
 from:{o:POP.map(function(c){return [c,cityName(c)];}).concat([['other','Other city ▾']]),v:OTHER?'other':(POP.indexOf(fv)>=0?fv:(fv?'other':'')),
  set:function(v){if(v==='other'){OTHER=true;sync();$('from').focus();return;}OTHER=false;$('from').value=v;fire($('from'));}},
 hstyle:{o:[['budget','Budget'],['mid','Mid-range'],['upscale','Upscale'],['luxury','Luxury'],['own','✏️ My own']],v:$('hstyle').value,set:function(v){$('hstyle').value=v;fire($('hstyle'));}},
 fstyle:{o:[['budget','🍙 Konbini & casual'],['mid','☕ Cafés & izakaya'],['treat','🍣 Treat yourself'],['own','✏️ My own']],v:$('fstyle').value,set:function(v){$('fstyle').value=v;fire($('fstyle'));}},
 arr:{o:short(opts(arr)),v:arr.value,set:function(v){arr.value=v;fire(arr);}},
 dep:{o:short(opts(dep)),v:dep.value,set:function(v){dep.value=v;fire(dep);}},
 way:{o:opts(way),v:way.value,hide:way.options.length<2,set:function(v){way.value=v;fire(way);}},
 tx:{o:[[0,'None'],[3,'A few'],[6,'Some'],[12,'Lots']],v:S.tx,set:function(v){setS('tx',+v);calc();}},
 cr:{o:[[0,'None'],[2,'2 days'],[4,'4 days'],[7,'A week']],v:S.cr,set:function(v){setS('cr',+v);calc();}},
 todo:{tiles:[['dn','🏰','Tokyo Disney'+(S.dn?' ×'+S.dn:''),S.dn>0],['sanrio','🎀','Sanrio Puroland',$('sanrio').value==='1'],['zoo','🐼','Ueno Zoo',$('zoo').value==='1']],
  set:function(v){if(v==='dn'){setS('dn',S.dn>=3?0:S.dn+1);calc();}else{$(v).value=$(v).value==='1'?'0':'1';fire($(v));}}},
 extras:{tiles:[['jr','🎫','Japan Rail Pass, 7 days',$('jr').value==='1']],set:function(v){$(v).value=$(v).value==='1'?'0':'1';fire($(v));}}
};}
function sync(){var G=GROUPS();[].forEach.call(document.querySelectorAll('[data-g]'),function(c){var g=G[c.getAttribute('data-g')];if(!g)return;c.hidden=!!g.hide;
  c.innerHTML=g.tiles?g.tiles.map(function(t){return '<button type="button" data-v="'+t[0]+'" aria-pressed="'+!!t[3]+'"'+(t[4]?' disabled':'')+'><span aria-hidden="true">'+t[1]+'</span>'+esc(t[2])+'</button>';}).join('')
   :g.o.map(function(x){return '<button type="button" data-v="'+esc(x[0])+'" aria-pressed="'+(String(x[0])===String(g.v))+'">'+esc(x[1])+'</button>';}).join('');});
 var fv=$('from').value;$('fromrow').hidden=!(OTHER||(fv&&POP.indexOf(fv)<0));}
document.addEventListener('click',function(e){var b=e.target.closest('[data-g] button');if(!b||b.disabled)return;var g=b.closest('[data-g]').getAttribute('data-g');GROUPS()[g].set(b.getAttribute('data-v'));track('tap',g);});
// ---- The planner (28 Nov, after the owner's design file): five tabs, every piece of the trip is a card with its price for the group
function ppl0(){return {ad:S.ad+S.tn,ch:S.ch,inf:S.in,tn:S.tn,cars:Math.ceil((S.ad+S.tn+S.ch+S.in)/4),days:S.nt+S.nk+S.no+S.nh+1};}
function rng(a,b){return y(a)+(b>a?'–'+y(b).replace(/^[¥$₹]/,''):'');}
var ICON=window.__ICON={"castle": "<svg viewBox=\"0 0 64 64\" width=\"100%\" height=\"100%\" aria-hidden=\"true\"><path d=\"M14 54V30h8v-8l4-6 4 6v8h4v-8l4-6 4 6v8h8v24z\" fill=\"#f4c95d\" fill=\"none\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><path d=\"M26 54V44a6 6 0 0 1 12 0v10\" fill=\"#e9707a\" fill=\"none\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><path d=\"M26 10v-6l6 3-6 3M42 10v-6l6 3-6 3\" fill=\"#e9707a\" fill=\"none\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/></svg>", "bow": "<svg viewBox=\"0 0 64 64\" width=\"100%\" height=\"100%\" aria-hidden=\"true\"><path d=\"M32 30 12 18c-4-2-8 2-6 8l4 12c2 6 10 4 22-8z\" fill=\"#f28ca0\" fill=\"none\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><path d=\"M32 30l20-12c4-2 8 2 6 8l-4 12c-2 6-10 4-22-8z\" fill=\"#f28ca0\" fill=\"none\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><circle cx=\"32\" cy=\"30\" r=\"6\" fill=\"#e9707a\" fill=\"none\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><path d=\"M28 36l-6 18 8-4 2 6 2-20\" fill=\"#f28ca0\" fill=\"none\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/></svg>", "panda": "<svg viewBox=\"0 0 64 64\" width=\"100%\" height=\"100%\" aria-hidden=\"true\"><circle cx=\"16\" cy=\"16\" r=\"8\" fill=\"#374151\" fill=\"none\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><circle cx=\"48\" cy=\"16\" r=\"8\" fill=\"#374151\" fill=\"none\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><circle cx=\"32\" cy=\"34\" r=\"22\" fill=\"#fff\" fill=\"none\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><ellipse cx=\"23\" cy=\"32\" rx=\"5\" ry=\"7\" fill=\"#374151\" transform=\"rotate(-20 23 32)\"/><ellipse cx=\"41\" cy=\"32\" rx=\"5\" ry=\"7\" fill=\"#374151\" transform=\"rotate(20 41 32)\"/><circle cx=\"24\" cy=\"31\" r=\"2\" fill=\"#fff\"/><circle cx=\"40\" cy=\"31\" r=\"2\" fill=\"#fff\"/><path d=\"M29 42q3 3 6 0\" fill=\"none\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><ellipse cx=\"32\" cy=\"39\" rx=\"3\" ry=\"2\" fill=\"#374151\"/></svg>", "ticket": "<svg viewBox=\"0 0 64 64\" width=\"100%\" height=\"100%\" aria-hidden=\"true\"><path d=\"M8 18h48v8a6 6 0 0 0 0 12v8H8v-8a6 6 0 0 0 0-12z\" fill=\"#7cc4f5\" fill=\"none\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><path d=\"M22 20v24\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-dasharray=\"3 4\"/><path d=\"M30 28h16M30 36h10\" fill=\"none\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/></svg>", "taxi": "<svg viewBox=\"0 0 64 64\" width=\"100%\" height=\"100%\" aria-hidden=\"true\"><path d=\"M10 40l4-14h36l4 14v10H10z\" fill=\"#f4c95d\" fill=\"none\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><path d=\"M18 26l3-8h22l3 8\" fill=\"#cfe9fb\" fill=\"none\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><rect x=\"26\" y=\"10\" width=\"12\" height=\"6\" rx=\"2\" fill=\"#e9707a\" fill=\"none\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><circle cx=\"20\" cy=\"50\" r=\"5\" fill=\"#374151\" fill=\"none\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><circle cx=\"44\" cy=\"50\" r=\"5\" fill=\"#374151\" fill=\"none\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><path d=\"M10 40h44\" fill=\"none\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/></svg>", "car": "<svg viewBox=\"0 0 64 64\" width=\"100%\" height=\"100%\" aria-hidden=\"true\"><path d=\"M8 42l6-14h36l6 14v8H8z\" fill=\"#e9707a\" fill=\"none\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><path d=\"M18 28l4-8h20l4 8\" fill=\"#cfe9fb\" fill=\"none\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><circle cx=\"20\" cy=\"50\" r=\"5\" fill=\"#374151\" fill=\"none\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><circle cx=\"44\" cy=\"50\" r=\"5\" fill=\"#374151\" fill=\"none\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><path d=\"M30 20v8\" fill=\"none\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/></svg>", "phone": "<svg viewBox=\"0 0 64 64\" width=\"100%\" height=\"100%\" aria-hidden=\"true\"><rect x=\"18\" y=\"6\" width=\"28\" height=\"52\" rx=\"6\" fill=\"#7cc4f5\" fill=\"none\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><rect x=\"23\" y=\"14\" width=\"18\" height=\"30\" rx=\"2\" fill=\"#fff\" fill=\"none\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><path d=\"M28 30l3 3 6-7\" fill=\"none\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><circle cx=\"32\" cy=\"51\" r=\"2.5\" fill=\"#1f2937\"/></svg>", "health": "<svg viewBox=\"0 0 64 64\" width=\"100%\" height=\"100%\" aria-hidden=\"true\"><path d=\"M32 56S8 42 8 24a12 12 0 0 1 24-4 12 12 0 0 1 24 4c0 18-24 32-24 32z\" fill=\"#7ad3b8\" fill=\"none\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><path d=\"M32 24v16M24 32h16\" stroke=\"#fff\" stroke-width=\"5\" stroke-linecap=\"round\"/></svg>", "tower": "<svg viewBox=\"0 0 64 64\" width=\"100%\" height=\"100%\" aria-hidden=\"true\"><path d=\"M32 6v8M26 54l6-40 6 40\" fill=\"none\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><path d=\"M22 54h20M27 40h10M29 28h6\" fill=\"none\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><path d=\"M24 54l2-14h12l2 14z\" fill=\"#f28c8c\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><rect x=\"28\" y=\"22\" width=\"8\" height=\"6\" fill=\"#f28c8c\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/></svg>", "torii": "<svg viewBox=\"0 0 64 64\" width=\"100%\" height=\"100%\" aria-hidden=\"true\"><path d=\"M8 14q24 6 48 0v6q-24 5-48 0z\" fill=\"#e9707a\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><path d=\"M14 26h36\" fill=\"none\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><path d=\"M20 20v38M44 20v38\" fill=\"none\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><path d=\"M30 26v-6M34 26v-6\" fill=\"none\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/></svg>", "castle2": "<svg viewBox=\"0 0 64 64\" width=\"100%\" height=\"100%\" aria-hidden=\"true\"><path d=\"M14 30l18-12 18 12z\" fill=\"#7ad3b8\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><rect x=\"20\" y=\"30\" width=\"24\" height=\"10\" fill=\"#fff\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><path d=\"M10 46l22-8 22 8z\" fill=\"#7ad3b8\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><rect x=\"16\" y=\"46\" width=\"32\" height=\"12\" fill=\"#fff\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><path d=\"M30 58v-6h4v6\" fill=\"none\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/></svg>", "mount": "<svg viewBox=\"0 0 64 64\" width=\"100%\" height=\"100%\" aria-hidden=\"true\"><path d=\"M6 54l18-30 10 14 6-8 18 24z\" fill=\"#7cc4f5\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><path d=\"M18 34l6-10 6 9-4 3-3-3-3 3z\" fill=\"#fff\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><circle cx=\"48\" cy=\"14\" r=\"5\" fill=\"#ffd166\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/></svg>", "plane": "<svg viewBox=\"0 0 64 64\" width=\"100%\" height=\"100%\" aria-hidden=\"true\"><path d=\"M8 36l18-4 12-18c2-3 6-2 6 2l-4 14 14 4c3 1 3 5 0 6l-14 4 4 14c0 4-4 5-6 2L26 42 8 38z\" fill=\"#7cc4f5\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/></svg>", "onigiri": "<svg viewBox=\"0 0 64 64\" width=\"100%\" height=\"100%\" aria-hidden=\"true\"><path d=\"M32 10c8 0 22 30 22 36s-10 10-22 10-22-4-22-10 14-36 22-36z\" fill=\"#fff\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><rect x=\"22\" y=\"40\" width=\"20\" height=\"16\" rx=\"2\" fill=\"#374151\"/></svg>", "coffee": "<svg viewBox=\"0 0 64 64\" width=\"100%\" height=\"100%\" aria-hidden=\"true\"><path d=\"M14 26h30v14a14 14 0 0 1-28 0z\" fill=\"#f4c95d\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><path d=\"M44 30h4a6 6 0 0 1 0 12h-4\" fill=\"none\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><path d=\"M24 12q-3 4 0 8M32 10q-3 4 0 8\" fill=\"none\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/></svg>", "sushi": "<svg viewBox=\"0 0 64 64\" width=\"100%\" height=\"100%\" aria-hidden=\"true\"><ellipse cx=\"32\" cy=\"40\" rx=\"22\" ry=\"10\" fill=\"#fff\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><path d=\"M12 36q20-16 40 0\" fill=\"#f28c8c\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><path d=\"M20 30l4 6M30 27l3 7M40 28l2 7\" stroke=\"#fff\" stroke-width=\"2\"/></svg>", "pen": "<svg viewBox=\"0 0 64 64\" width=\"100%\" height=\"100%\" aria-hidden=\"true\"><path d=\"M14 50l4-12 26-26 8 8-26 26z\" fill=\"#ffd166\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><path d=\"M38 18l8 8\" fill=\"none\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><path d=\"M14 50l12-4\" fill=\"none\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/></svg>", "train": "<svg viewBox=\"0 0 64 64\" width=\"100%\" height=\"100%\" aria-hidden=\"true\"><rect x=\"14\" y=\"8\" width=\"36\" height=\"40\" rx=\"8\" fill=\"#7cc4f5\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><rect x=\"20\" y=\"14\" width=\"24\" height=\"12\" rx=\"2\" fill=\"#fff\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><circle cx=\"22\" cy=\"38\" r=\"3\" fill=\"#1f2937\"/><circle cx=\"42\" cy=\"38\" r=\"3\" fill=\"#1f2937\"/><path d=\"M20 48l-6 8M44 48l6 8\" fill=\"none\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/></svg>", "bus": "<svg viewBox=\"0 0 64 64\" width=\"100%\" height=\"100%\" aria-hidden=\"true\"><rect x=\"10\" y=\"12\" width=\"44\" height=\"36\" rx=\"6\" fill=\"#7ad3b8\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><path d=\"M10 30h44\" fill=\"none\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><rect x=\"16\" y=\"18\" width=\"14\" height=\"8\" fill=\"#fff\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><rect x=\"34\" y=\"18\" width=\"14\" height=\"8\" fill=\"#fff\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><circle cx=\"20\" cy=\"50\" r=\"4\" fill=\"#374151\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><circle cx=\"44\" cy=\"50\" r=\"4\" fill=\"#374151\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/></svg>", "van": "<svg viewBox=\"0 0 64 64\" width=\"100%\" height=\"100%\" aria-hidden=\"true\"><path d=\"M8 44V22h30l12 10h6v12z\" fill=\"#f4c95d\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><path d=\"M38 22v10h12\" fill=\"none\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><rect x=\"14\" y=\"26\" width=\"18\" height=\"8\" fill=\"#fff\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><circle cx=\"18\" cy=\"46\" r=\"5\" fill=\"#374151\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><circle cx=\"46\" cy=\"46\" r=\"5\" fill=\"#374151\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/></svg>", "receipt": "<svg viewBox=\"0 0 64 64\" width=\"100%\" height=\"100%\" aria-hidden=\"true\"><path d=\"M16 6h32v52l-6-4-5 4-5-4-5 4-5-4-6 4z\" fill=\"#fff\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><path d=\"M22 18h20M22 26h20M22 34h12\" fill=\"none\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><text x=\"32\" y=\"50\" text-anchor=\"middle\" font-size=\"12\" font-weight=\"800\" fill=\"#1f2937\">¥</text></svg>", "bag": "<svg viewBox=\"0 0 64 64\" width=\"100%\" height=\"100%\" aria-hidden=\"true\"><rect x=\"12\" y=\"18\" width=\"40\" height=\"38\" rx=\"7\" fill=\"#7cc4f5\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><path d=\"M24 18v-6a4 4 0 0 1 4-4h8a4 4 0 0 1 4 4v6\" fill=\"none\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><path d=\"M22 18v38M42 18v38\" fill=\"none\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><circle cx=\"32\" cy=\"34\" r=\"5\" fill=\"#ffd166\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/></svg>", "people": "<svg viewBox=\"0 0 64 64\" width=\"100%\" height=\"100%\" aria-hidden=\"true\"><circle cx=\"24\" cy=\"22\" r=\"8\" fill=\"#f4c95d\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><circle cx=\"42\" cy=\"22\" r=\"8\" fill=\"#f4c95d\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><path d=\"M10 50c0-9 6-15 14-15s14 6 14 15z\" fill=\"#7cc4f5\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><path d=\"M28 50c0-9 6-15 14-15s14 6 14 15z\" fill=\"#f28ca0\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/></svg>", "child": "<svg viewBox=\"0 0 64 64\" width=\"100%\" height=\"100%\" aria-hidden=\"true\"><circle cx=\"32\" cy=\"26\" r=\"10\" fill=\"#f4c95d\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><path d=\"M20 20l12-8 12 8\" fill=\"#ffd166\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><path d=\"M16 54c0-9 7-15 16-15s16 6 16 15z\" fill=\"#7ad3b8\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><circle cx=\"28\" cy=\"26\" r=\"1.6\" fill=\"#1f2937\"/><circle cx=\"36\" cy=\"26\" r=\"1.6\" fill=\"#1f2937\"/><path d=\"M29 31q3 2 6 0\" fill=\"none\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/></svg>", "teen": "<svg viewBox=\"0 0 64 64\" width=\"100%\" height=\"100%\" aria-hidden=\"true\"><circle cx=\"32\" cy=\"24\" r=\"10\" fill=\"#f4c95d\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><path d=\"M20 22a12 12 0 0 1 24 0\" fill=\"none\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><rect x=\"17\" y=\"21\" width=\"5\" height=\"9\" rx=\"2\" fill=\"#7cc4f5\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><rect x=\"42\" y=\"21\" width=\"5\" height=\"9\" rx=\"2\" fill=\"#7cc4f5\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><path d=\"M16 54c0-9 7-15 16-15s16 6 16 15z\" fill=\"#b9a7f5\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/></svg>", "baby": "<svg viewBox=\"0 0 64 64\" width=\"100%\" height=\"100%\" aria-hidden=\"true\"><circle cx=\"32\" cy=\"28\" r=\"12\" fill=\"#f4c95d\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><path d=\"M32 16q-4-6 2-8\" fill=\"none\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><circle cx=\"27\" cy=\"27\" r=\"1.6\" fill=\"#1f2937\"/><circle cx=\"37\" cy=\"27\" r=\"1.6\" fill=\"#1f2937\"/><circle cx=\"32\" cy=\"34\" r=\"2.5\" fill=\"#f28ca0\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><path d=\"M20 56c0-7 5-12 12-12s12 5 12 12z\" fill=\"#7cc4f5\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/></svg>", "hotel": "<svg viewBox=\"0 0 64 64\" width=\"100%\" height=\"100%\" aria-hidden=\"true\"><rect x=\"16\" y=\"10\" width=\"32\" height=\"46\" rx=\"3\" fill=\"#ffd166\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><rect x=\"22\" y=\"18\" width=\"7\" height=\"7\" fill=\"#fff\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><rect x=\"35\" y=\"18\" width=\"7\" height=\"7\" fill=\"#fff\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><rect x=\"22\" y=\"31\" width=\"7\" height=\"7\" fill=\"#fff\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><rect x=\"35\" y=\"31\" width=\"7\" height=\"7\" fill=\"#fff\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><path d=\"M28 56V46h8v10\" fill=\"#e9707a\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/></svg>", "globe": "<svg viewBox=\"0 0 64 64\" width=\"100%\" height=\"100%\" aria-hidden=\"true\"><circle cx=\"32\" cy=\"30\" r=\"18\" fill=\"#7cc4f5\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><path d=\"M14 30h36M32 12c-6 6-6 30 0 36M32 12c6 6 6 30 0 36\" fill=\"none\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><ellipse cx=\"32\" cy=\"30\" rx=\"27\" ry=\"8\" fill=\"none\" stroke=\"#ffd166\" stroke-width=\"4\"/><path d=\"M22 56h20\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/></svg>", "sky": "<svg viewBox=\"0 0 64 64\" width=\"100%\" height=\"100%\" aria-hidden=\"true\"><rect x=\"22\" y=\"14\" width=\"20\" height=\"42\" rx=\"2\" fill=\"#b9a7f5\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><path d=\"M18 14h28\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><path d=\"M28 22v4M36 22v4M28 32v4M36 32v4M28 42v4M36 42v4\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><circle cx=\"50\" cy=\"12\" r=\"5\" fill=\"#ffd166\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/></svg>", "leaf": "<svg viewBox=\"0 0 64 64\" width=\"100%\" height=\"100%\" aria-hidden=\"true\"><path d=\"M14 50C14 26 30 12 52 12c0 22-14 38-38 38z\" fill=\"#7ad3b8\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><path d=\"M14 50L40 24\" fill=\"none\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/></svg>", "deer": "<svg viewBox=\"0 0 64 64\" width=\"100%\" height=\"100%\" aria-hidden=\"true\"><path d=\"M20 30q12-6 24 0v14q-12 6-24 0z\" fill=\"#e0a96d\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><circle cx=\"46\" cy=\"22\" r=\"7\" fill=\"#e0a96d\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><path d=\"M44 15l-4-7M48 15l3-7M40 8l-3 1M51 8l3 1\" fill=\"none\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><path d=\"M24 44v10M40 44v10\" stroke=\"#1f2937\" stroke-width=\"3\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/><circle cx=\"28\" cy=\"36\" r=\"1.8\" fill=\"#fff\"/><circle cx=\"34\" cy=\"34\" r=\"1.8\" fill=\"#fff\"/></svg>"};
var TABS=[['trav','👨‍👩‍👧‍👦','Travelers','Who is going, and your travel style. Ages change train, park and flight prices.'],
 ['cities','🗾','Cities','Add the places you will stay and tap + / − for the nights in each. More cities are coming.'],
 ['stays','🏨','Stays','Your hotel level and rooms. Prices are per room a night in your first city.'],
 ['flight','✈️','Flight','Where you fly from. Economy return fares from recent searches.'],
 ['food','🍜','Food','How you like to eat, per day for the group.'],
 ['fun','🎢','Attractions','Big parks, indoor worlds and easy days out. Tap + for more days at Disney or USJ.'],
 ['move','🚆','Transit','Airport trips, the rail pass, taxis and a car.'],
 ['pre','🧳','Essentials','eSIM, insurance and the departure tax.'],
 ['review','🧾','Review','Your whole trip. Change anything here or in the tabs above.'],
 ['book','🛒','Book','Check today\'s price and book each piece, or share and keep your budget.']],TAB='trav',FIL='';
var FILS=[['kid','🧸','Kid-Friendly'],['rail','🚄','JR Pass / Rail'],['nocar','🚶','No Car Needed'],['budget','🪙','Budget Pick']];
function hotelBy(){return D.hotelStyles[$('hstyle').value];}
function airCost(k){var g=ppl0();function pickK(ap,cur){var a=D.airport[ap].ways;return (cur&&a.filter(function(x){return x.id===cur&&x.k===k;})[0])||a.filter(function(x){return x.k===k;})[0]||null;}
 var wi=pickK(arr.value,KIND===k?way.value:''),wo=dep.value===arr.value?wi:pickK(dep.value,'');if(!wi)return null;if(!wo)wo=D.airport[dep.value].ways[0];
 function c(w){return w.car?[w.car[0]*g.cars,w.car[1]*g.cars]:[w.a*g.ad+(w.c||0)*g.ch,w.a*g.ad+(w.c||0)*g.ch];}
 var x=c(wi),z=(wi===wo&&wi.id==='nex')?[0,0]:c(wo);return [x[0]+z[0],x[1]+z[1]];}
var CARDS=[
 ['trav','ad','people','#e6efff','Adults (18+)','Adult fares on trains and flights, adult park tickets and full daily meals',['Primary','18+ yrs'],[]],
 ['trav','ch','child','#fff3c4','Children (6–11)','Child fares on trains and buses (about half), child park tickets, about half on food',['Kid fav','Child fares'],['kid']],
 ['trav','tn','teen','#efe9ff','Teenagers (12–17)','Adult fares on trains and flights; junior tickets at Tokyo Disney',['Youth','12–17 yrs'],['kid']],
 ['trav','in','baby','#ffe9f3','Little ones (under 6)','Usually ride free with an adult; Tokyo Disney is free under 4',['Kid fav','Free on most trains'],['kid']],
 // stays: nights per city; the hotel price follows the hotel style and rooms
 ['cities','nt','tower','#ffe3e3','Tokyo','Shinjuku, Ueno or Tokyo Bay: the base for most first trips',['Kid fav','No car','Per night'],['kid','nocar']],
 ['cities','nk','torii','#fff3c4','Kyoto','Temples, shrines and old streets; easy by bus and subway',['No car','Rail'],['nocar','rail']],
 ['cities','no','castle2','#e6faf5','Osaka','Street food, Osaka Castle and easy day trips',['Kid fav','No car'],['kid','nocar']],
 ['cities','nh','mount','#e6efff','Hokkaido (Sapporo)','Snow, open countryside and fresh food; a car helps outside the city',['Countryside'],[]],
 ['stays','h:budget','hotel','#fff3c4','Hotel: Budget','Business hotels and simple twin rooms',['Budget pick','Hotel tier'],['budget']],
 ['stays','h:mid','hotel','#e6efff','Hotel: Mid-range','3-star and good business hotels',['Popular','Hotel tier'],['kid']],
 ['stays','h:upscale','hotel','#efe9ff','Hotel: Upscale','4-star hotels, including the Disney partner hotels',['Comfort','Hotel tier'],['kid']],
 ['stays','h:luxury','hotel','#ffe9f3','Hotel: Luxury','5-star hotels and top ryokan',['Treat','Hotel tier'],[]],
 ['stays','h:own','hotel','#e6faf5','Hotel: My own rate','Type what you expect to pay a night, all rooms together',['Custom','Hotel tier'],[]],
 ['fun','dn','castle','#fff3c4','Tokyo Disney','Disneyland or DisneySea, one park a day',['Kid fav','Tokyo','1 park a day'],['kid','nocar'],'big'],
 ['fun','us','globe','#e6efff','Universal Studios Japan','Osaka\'s big theme park; prices vary by date',['Kid fav','Osaka','By date'],['kid','nocar'],'big'],
 ['fun','sanrio','bow','#ffe3ea',"Sanrio Puroland","Hello Kitty's indoor theme park",['Kid fav','Tokyo','Indoors'],['kid','nocar','budget'],'indoor'],
 ['fun','sk','sky','#efe9ff','Shibuya Sky','Open-air rooftop deck above Shibuya; cheaper before 15:00',['Tokyo','Views'],['nocar'],'indoor'],
 ['fun','tr','tower','#e6efff','Tokyo Skytree','Japan\'s tallest tower; one deck or both',['Tokyo','Views'],['kid','nocar'],'indoor'],
 ['fun','gh','leaf','#e6faf5','Ghibli Museum, Mitaka','Advance reservation only; tickets are not sold at the museum',['Tokyo','Book ahead'],['kid','nocar','budget'],'easy'],
 ['fun','zoo','panda','#e6f6ea','Ueno Zoo','A city zoo in Ueno Park; up to 6th grade free',['Kid fav','Tokyo','Outdoors'],['kid','nocar','budget'],'easy'],
 ['fun','np','deer','#fff3c4','Nara Park','Friendly deer and big temples; a day trip from Kyoto or Osaka',['Nara','Free'],['kid','nocar','budget'],'easy'],
 ['fun','fi','torii','#ffe3e3','Fushimi Inari Taisha','Thousands of red gates up the hill in Kyoto',['Kyoto','Free'],['nocar','budget'],'easy'],
 ['flight','flight','plane','#e6efff','Flights','Economy, return, for everyone',['Round trip'],[]],
 ['food','f:budget','onigiri','#f4faf8','Konbini & casual eats','Convenience stores, bakeries, ramen and gyudon',['Budget pick'],['budget','kid']],
 ['food','f:mid','coffee','#fff3c4','Cafés & family izakaya','A café lunch and an izakaya or family restaurant dinner',['Kid fav'],['kid']],
 ['food','f:treat','sushi','#ffe3e3','Treat yourself','Sit-down sushi, wagyu or kaiseki dinners',['Splurge'],[]],
 ['food','f:own','pen','#f4faf8','My own amount','Type what you expect to spend per person a day',['Your figure'],[]],
 ['move','a:train','train','#e6efff','Airport by train','Both ways; the fastest way into town',['Rail','Both ways'],['rail','nocar','budget']],
 ['move','a:bus','bus','#e6faf5','Airport by bus','Both ways; door to the big hotels and stations',['Both ways'],['nocar','kid']],
 ['move','a:taxi','taxi','#fff3c4','Airport taxi','Both ways; the airport\'s fixed fare',['Both ways'],['nocar','kid']],
 ['move','a:private','van','#ffe3e3','Private car','Both ways; a pre-booked car meets you at arrivals',['Both ways'],['nocar','kid']],
 ['move','jr','ticket','#e6efff','Japan Rail Pass','7 days of JR trains, for long trips',['Rail','7 days'],['rail','nocar']],
 ['move','tx','taxi','#fff3c4','Taxi rides in town','About 7 km each',['City'],['nocar','kid']],
 ['move','cr','car','#ffe3e3','Rental car','Most visitors need an International Driving Permit (check current rules)',['Hokkaido','Countryside'],[]],
 ['pre','es','phone','#e6efff','eSIM data','Maps and messages from landing; one per adult and teen',['Before you fly','Per phone'],['kid','budget']],
 ['pre','ins','health','#e6faf5','Travel medical insurance','From about US$2 a day under 40; rises with age',['Before you fly','Per person'],['kid']],
 ['pre','tax','receipt','#f4faf8','Departure tax','Japan\'s international tourist tax, usually added to your flight ticket',['Always included'],['budget']]];
var NIGHTS={nt:'Tokyo',nk:'Kyoto',no:'Osaka',nh:'Hokkaido'},ADD={nt:3,nk:2,no:2,nh:3,dn:1,tx:4,cr:2,us:1};
function state(c){var k=c[1],g=ppl0();
 var PPL={ad:['adult',1],ch:['child',0],tn:['teen',0],in:['little one',0]};
 if(PPL[k]){var pn=S[k],w=PPL[k][0];return {n:pn,q:1,ppl:1,unit:w,min:PPL[k][1],label:'Group count',big:pn+' '+(pn===1?w:(w==='child'?'children':w+'s')).replace(/^./,function(c){return c.toUpperCase();})};}
 if(k.indexOf('h:')===0){var hk=k.slice(2),on=$('hstyle').value===hk,Hs=D.hotelStyles[hk],city=['nt','nk','no','nh'].filter(function(x){return S[x];})[0]||'nt';
  if(hk==='own')return {n:on?1:0,radio:1,label:'Per night, all rooms',pr:on&&num('hotel')?[num('hotel'),num('hotel')]:null,note:'type it below'};
  return {n:on?1:0,radio:1,label:'Per room a night, '+NIGHTS[city],pr:[Hs.by[city][0],Hs.by[city][1]]};}
 if(k.indexOf('c:')===0){var ck=k.slice(2),cn=S[ck],Hc=hotelBy(),rr=S.rm;return {n:cn?1:0,city:1,label:cn?cn+' night'+(cn>1?'s':'')+' · set in Nights':'Hotel per night, '+rr+' room'+(rr>1?'s':''),pr:Hc&&Hc.by?(cn?[Hc.by[ck][0]*rr*cn,Hc.by[ck][1]*rr*cn]:[Hc.by[ck][0]*rr,Hc.by[ck][1]*rr]):null,note:'your own hotel figure'};}
 if(NIGHTS[k]){var n=S[k],H=hotelBy(),r=S.rm;var pr=H&&H.by?(n?[H.by[k][0]*r*n,H.by[k][1]*r*n]:[H.by[k][0]*r,H.by[k][1]*r]):null;
  return {n:n,q:1,unit:'night',label:n?n+' night'+(n>1?'s':'')+', '+r+' room'+(r>1?'s':''):'Per night, '+r+' room'+(r>1?'s':''),pr:pr,note:H&&H.by?'':'your own hotel figure'};}
 if(k==='dn'){var d=D.disney,dc=D.disneyChild,kid=dc.c*g.ch+dc.j*g.tn,n2=S.dn||1;return {n:S.dn,q:1,unit:'day',label:S.dn?S.dn+' day'+(S.dn>1?'s':'')+', group':'1 day, group',pr:[(d.lo*S.ad+kid)*n2,(d.hi*S.ad+kid)*n2]};}
 if(k==='sanrio'){var r2=D.sanrio,m=g.ad+g.ch;return {n:$('sanrio').value==='1'?1:0,label:'Group tickets',pr:[r2.lo*m,r2.hi*m]};}
 if(k==='us'){var un=S.us||1,uv=D.usj.a*g.ad*un;return {n:S.us,q:1,unit:'day',label:(S.us?S.us+' day'+(S.us>1?'s':''):'1 day')+', adults, from',pr:[uv,uv],note:''};}
 if(k==='sk')return {n:S.sk,label:'Group, web tickets',pr:[D.shibuyasky.lo*g.ad+D.shibuyasky.c*g.ch,D.shibuyasky.hi*g.ad+D.shibuyasky.c*g.ch]};
 if(k==='tr')return {n:S.tr,label:'Group, one deck or both',pr:[D.skytree.alo*g.ad+D.skytree.clo*g.ch,D.skytree.ahi*g.ad+D.skytree.chi*g.ch]};
 if(k==='gh'){var gg=D.ghibli.a*S.ad+D.ghibli.t*g.tn+D.ghibli.c*g.ch;return {n:S.gh,label:'Group entry',pr:[gg,gg+D.ghibli.i*g.inf]};}
 if(k==='np'||k==='fi')return {n:S[k],label:'Entry',pr:null,note:'Free'};
 if(k==='zoo')return {n:$('zoo').value==='1'?1:0,label:'Group entry',pr:[D.uenozoo.a*g.ad,D.uenozoo.a*g.ad]};
 if(k==='jr'){var j=D.jrpass,v=j.a*g.ad+j.c*g.ch;return {n:$('jr').value==='1'?1:0,label:'7 days, group',pr:[v,v]};}
 if(k==='tx'){var t=Math.max(1,S.tx);return {n:S.tx,q:1,unit:'ride',label:S.tx?S.tx+' ride'+(S.tx>1?'s':''):'Per ride',pr:[D.taxi.lo*g.cars*t,D.taxi.hi*g.cars*t]};}
 if(k==='cr')return {n:S.cr,q:1,unit:'day',label:S.cr?S.cr+' day'+(S.cr>1?'s':''):'Per day',pr:null,note:'price on the booking site'};
 if(k==='es'){var ep=D.esim.plans.filter(function(x){return x[0]>=g.days;})[0]||D.esim.plans[D.esim.plans.length-1],en=Math.max(1,Math.ceil(g.days/ep[0])),ev=Math.round(ep[2]*en*g.ad*D.usdJpy/10)*10;return {n:S.es,label:g.ad+' phone'+(g.ad>1?'s':'')+', '+g.days+' days',pr:[ev,ev]};}
 if(k==='ins')return {n:S.ins,label:g.ad+' adult'+(g.ad>1?'s':'')+', '+g.days+' days',pr:[Math.round(D.insurance.lo*g.days*g.ad*D.usdJpy/100)*100,Math.round(D.insurance.hi*g.days*g.ad*D.usdJpy/100)*100]};
 if(k==='tax'){var pp=g.ad+g.ch+g.inf;return {n:1,fixed:1,label:pp+' × ¥'+D.tax.each.toLocaleString('en-US'),pr:[D.tax.each*pp,D.tax.each*pp]};}
 if(k==='flight'){var fr=$('from').value,pp2=g.ad+g.ch+g.inf;if(fr==='own'&&num('fly'))return {n:1,flight:1,label:'Your figure',pr:[num('fly'),num('fly')]};
  if(FARE&&fr&&fr!=='own')return {n:1,flight:1,label:pp2+' × economy return, from '+cityName(fr),pr:[FARE.lo*pp2,FARE.hi*pp2]};return {n:0,flight:1,label:'Choose your city',pr:null,note:'fares from your city'};}
 if(k.indexOf('f:')===0){var fk=k.slice(2),F=D.foodStyles[fk],fw=g.ad+(g.ch+g.inf)/2,on=$('fstyle').value===fk;
  if(fk==='own')return {n:on?1:0,radio:1,label:'Per person a day',pr:on&&num('food')?[num('food')*(g.ad+g.ch+g.inf)*g.days,num('food')*(g.ad+g.ch+g.inf)*g.days]:null,note:'type it below'};
  return {n:on?1:0,radio:1,label:g.days+' days, group',pr:[Math.round(F.lo*fw*g.days),Math.round(F.hi*fw*g.days)]};}
 if(k.indexOf('a:')===0){var ak=k.slice(2),have=kindsOf(arr.value),on2=KIND===ak;if(!have[ak])return {n:0,radio:1,off:1,label:'Not at this airport',pr:null};
  var pr2=ak==='private'?null:airCost(ak);return {n:on2?1:0,radio:1,label:'Both ways, group',pr:pr2,note:ak==='private'?'price on the booking site':''};}
 return {n:0};}
function items(){var cur=TABS.filter(function(t){return t[0]===TAB;})[0]||TABS[0],g=ppl0();if(cur[0]!==TAB)TAB=cur[0];
 $('mtabs').innerHTML=TABS.map(function(t){var n=CARDS.filter(function(c){var st=state(c);return c[0]===t[0]&&st.n&&!st.fixed&&!st.radio&&!st.ppl;}).length;return '<button type="button" role="tab" data-tab="'+t[0]+'" aria-selected="'+(t[0]===TAB)+'"><span aria-hidden="true">'+t[1]+'</span> '+t[2]+(n?' <i>'+n+'</i>':'')+'</button>';}).join('');
 $('memo').textContent=cur[1];$('mtitle').textContent=cur[2];$('msub').textContent=cur[3]+' Prices are for your group.';
 $('fchips').innerHTML='<button type="button" data-fil="" aria-pressed="'+(!FIL)+'" class="all">All options</button>'+FILS.map(function(f){return '<button type="button" data-fil="'+f[0]+'" aria-pressed="'+(FIL===f[0])+'"><span aria-hidden="true">'+f[1]+'</span> '+f[2]+'</button>';}).join('');
 [].forEach.call(document.querySelectorAll('.extra'),function(x){x.hidden=x.getAttribute('data-tab')!==TAB;});var isR=TAB==='review',isB=TAB==='book';$('rpanel').hidden=!isR;$('bpanel').hidden=!isB;document.querySelector('.filters').hidden=['fun','move'].indexOf(TAB)<0;if(isR)rrows();
 var list=(TAB==='review'||TAB==='book')?[]:CARDS.filter(function(c){return c[0]===TAB&&(!FIL||c[7].indexOf(FIL)>=0);});var pp0=g.ad+g.ch+g.inf,nn0=S.nt+S.nk+S.no+S.nh,fr0=$('from').value,FSN={budget:'Konbini & casual',mid:'Cafés & izakaya',treat:'Treat yourself',own:'Your food figure'};
 var ncity=['nt','nk','no','nh'].filter(function(x){return S[x];}).length,hsn0={budget:'Budget',mid:'Mid-range',upscale:'Upscale',luxury:'Luxury',own:'Your rate'}[$('hstyle').value]||'';
 $('mcount').textContent={trav:pp0+' travellers · '+(STYLE?STY[STYLE][0]:'Custom'),cities:ncity+' cit'+(ncity===1?'y':'ies')+' · '+nn0+' nights',stays:hsn0+' · '+S.rm+' room'+(S.rm>1?'s':'')+' · '+nn0+' nights',
  flight:fr0&&fr0!=='own'?cityName(fr0)+' · economy return':'Choose your city',food:(FSN[$('fstyle').value]||'')+' · '+(nn0+1)+' days',fun:'Kid-friendly parks',
  move:'Arrival: '+(D.airport[arr.value]||{name:''}).name.replace(/ \(.*\)/,'')+' · '+({train:'Train',bus:'Bus',taxi:'Taxi',private:'Private car'}[KIND]||''),pre:'Before you fly',review:'Estimate '+($('barv').getAttribute('data-full')||$('barv').textContent),book:'Estimate '+($('barv').getAttribute('data-full')||$('barv').textContent)}[TAB]||'';
 if($('psel'))$('psel').textContent=fr0&&fr0!=='own'?'Selected: '+cityName(fr0):'';
 var GRPN={big:['🎢','Big theme parks','the full-day splurge'],indoor:['✨','Indoor worlds & views','half a day, good in rain'],easy:['🌸','Easy days out','cheap or free']},lastG='';
 $('items').innerHTML=list.length?list.map(function(c){var st=state(c),k=c[1],on=st.n>0,gh='';if(c[8]&&c[8]!==lastG){lastG=c[8];var gn=GRPN[c[8]];gh='<h3 class="cgrp"><span aria-hidden="true">'+gn[0]+'</span> '+gn[1]+' <small>'+gn[2]+'</small></h3>';}
  var price=st.big?esc(st.big):st.pr?rng(st.pr[0],st.pr[1]):'<em>'+esc(st.note||'')+'</em>';
  var act=st.fixed?'<button type="button" class="add rm" disabled>✓ Included</button>'
   :st.flight?'<button type="button" class="add'+(on?' rm':'')+'" data-act="from">'+(on?'✎ Change city':'Choose city')+'</button>'
   :st.off?'<button type="button" class="add" disabled>Not here</button>'
   :st.radio?(on?'<button type="button" class="add rm" disabled>✓ Selected</button>':'<button type="button" class="add" data-act="pick" data-k="'+k+'">Choose</button>')
   :st.ppl?'<div class="qty"><button type="button" data-act="dec" data-k="'+k+'" aria-label="Fewer"'+(st.n<=st.min?' disabled':'')+'>−</button><b>'+st.n+'</b><button type="button" data-act="inc" data-k="'+k+'" aria-label="More">+</button></div>'
   :st.q&&on?'<div class="qty"><button type="button" data-act="dec" data-k="'+k+'" aria-label="Fewer">−</button><b>'+st.n+' '+st.unit+(st.n>1?'s':'')+'</b><button type="button" data-act="inc" data-k="'+k+'" aria-label="More">+</button></div>'
   :st.city?(on?'<button type="button" class="add rm" data-act="crm" data-k="'+k+'">✓ Added</button>':'<button type="button" class="add" data-act="cadd" data-k="'+k+'">+ Add</button>')
   :on?'<button type="button" class="add rm" data-act="rm" data-k="'+k+'">✓ Added</button>':'<button type="button" class="add" data-act="add" data-k="'+k+'">+ Add to Trip</button>';
  return gh+'<div class="it'+(on&&!st.fixed&&(!st.ppl||st.n>0)?' on':'')+(st.off?' off':'')+'"><div class="tags">'+c[6].map(function(x,i){return '<span class="t'+(x==='Kid fav'?'f':Math.min(i,2))+'">'+esc(x)+'</span>';}).join('')+'</div>'+
   '<div class="art" style="background:'+c[3]+'" aria-hidden="true">'+ICON[c[2]]+'</div><h3>'+esc(c[4])+'</h3><p>'+esc(c[5])+'</p><div class="foot"><div class="pr"><small>'+esc(st.label||'')+'</small>'+price+'</div>'+act+'</div></div>';}).join('')
  :(TAB==='review'||TAB==='book')?'':'<p class="none">Nothing here matches that filter. <button type="button" data-fil="'+FIL+'">Show all</button></p>';
 // the tray
 var cities=['nt','nk','no','nh'].filter(function(k){return S[k];}).map(function(k){return NIGHTS[k]+' ('+S[k]+'n)';}),pp=g.ad+g.ch+g.inf,nn=S.nt+S.nk+S.no+S.nh,cnt=0;
 CARDS.forEach(function(c){var st=state(c);if(st.n&&!st.ppl&&!st.city)cnt++;});
 $('tcount').textContent=cnt;$('tmode').textContent=(STYLE?STY[STYLE][0]:'Custom').toUpperCase();
 var fs=$('fstyle').value,fsn={budget:'Konbini & casual eats',mid:'Cafés & izakaya',treat:'Treat yourself',own:'Your food figure'}[fs]||'';
 var hsn={budget:'Budget stays',mid:'Mid-range stays',upscale:'Upscale stays',luxury:'Luxury stays',own:'Your hotel rate'}[$('hstyle').value]||'',frn=$('from').value&&$('from').value!=='own'?cityName($('from').value)+' flights':'';
 $('tsum').textContent=cities.length?[cities.join(' · '),hsn,frn||fsn].filter(Boolean).join(' · '):'Tap "+ Add" on a city to start!';
 if($('whol'))$('whol').textContent=S.ad+S.tn+' adult'+(S.ad+S.tn>1?'s':'')+(S.ch+S.in?', '+(S.ch+S.in)+' kid'+(S.ch+S.in>1?'s':''):'');
 var fr=$('from').value;if($('froml'))$('froml').textContent=fr&&fr!=='own'?cityName(fr):fr==='own'?'Your own fare':'Flying from';
 var wl=document.querySelector('[data-g="way"]');$('waylab').hidden=!wl||wl.hidden;}
function openSheet(id){['whosheet','fromsheet'].forEach(function(x){var o=x===id&&$(x).hidden;$(x).hidden=!o;$(x==='whosheet'?'whob':'fromb').setAttribute('aria-expanded',o);});}


[].forEach.call(document.querySelectorAll('[data-close]'),function(b){b.addEventListener('click',function(){openSheet('');});});
$('mtabs').addEventListener('click',function(e){var b=e.target.closest('[data-tab]');if(!b)return;TAB=b.getAttribute('data-tab');FIL='';items();track('tab',TAB);scrollTo(0,0);var sel=document.querySelector('#mtabs [aria-selected=true]');if(sel&&sel.scrollIntoView)sel.scrollIntoView({inline:'center',block:'nearest'});});
document.querySelector('.planner').addEventListener('click',function(e){if(e.target.closest('#rpanel,#bpanel'))return;var f=e.target.closest('[data-fil]');if(f){var v=f.getAttribute('data-fil');FIL=(!v||FIL===v)?'':v;items();track('filter',FIL);return;}
 var b=e.target.closest('[data-act]');if(!b)return;var k=b.getAttribute('data-k'),a=b.getAttribute('data-act');
 if(a==='from'){var pl=document.querySelector('.panel');if(pl)pl.scrollIntoView({behavior:'smooth',block:'center'});return;}
 if(a==='cadd'||a==='crm'){var ck2=k.slice(2);setS(ck2,a==='cadd'?(ADD[ck2]||2):0);calc();track(a==='cadd'?'add':'remove',k);return;}
 if(a==='pick'){if(k.indexOf('h:')===0){$('hstyle').value=k.slice(2);fire($('hstyle'));}else if(k.indexOf('f:')===0){$('fstyle').value=k.slice(2);fire($('fstyle'));}else{KIND=k.slice(2);ways();calc();}track('pick',k);return;}
 if(['sanrio','zoo','jr'].indexOf(k)>=0){$(k).value=a==='add'?'1':'0';fire($(k));}
 else{var n=S[k];n=a==='add'?(ADD[k]||1):a==='rm'?0:a==='inc'?Math.min(MAX[k],n+1):Math.max(k==='ad'?1:0,n-1);setS(k,n);if(['ad','tn','ch','in'].indexOf(k)>=0)setS('rm',Math.max(1,Math.ceil((S.ad+S.tn+S.ch)/2)));calc();}
 track(a==='add'||a==='inc'?'add':'remove',k);});
function rrows(){var g=ppl0(),out=[];CARDS.forEach(function(c){var st=state(c);if(!st.n||st.off||st.ppl||st.city)return;var k=c[1],per='';
  if(st.q&&st.pr&&st.n>1)per='('+rng(st.pr[0]/st.n,st.pr[1]/st.n)+' a '+st.unit+')';
  var right=st.q?'<div class="rq"><button type="button" data-act="'+(st.n>1?'dec':'rm')+'" data-k="'+k+'" aria-label="'+(st.n>1?'Fewer':'Remove')+'">'+(st.n>1?'−':'🗑')+'</button><b>'+st.n+'</b><button type="button" class="p" data-act="inc" data-k="'+k+'" aria-label="More">+</button></div>'
   :(['sanrio','zoo','jr','es','ins','sk','tr','gh','np','fi'].indexOf(k)>=0)?'<div class="rq"><button type="button" data-act="rm" data-k="'+k+'" aria-label="Remove">🗑</button><b>1</b></div>'
   :st.fixed?'':'<button type="button" class="rch" data-tabgo="'+c[0]+'">Change</button>';
  out.push('<div class="rrow"><span class="ri" style="background:'+c[3]+'" aria-hidden="true">'+ICON[c[2]]+'</span><div class="rt"><h3>'+esc(c[4])+'</h3><div class="rp">'+(st.pr?rng(st.pr[0],st.pr[1]):'<small style="margin:0">'+esc(st.note||'not priced yet')+'</small>')+(per?'<small>'+per+'</small>':'')+'</div><div class="rs">'+esc(st.label||'')+'</div></div>'+right+'</div>');});
 $('rlist').innerHTML=out.join('');
 var pp=g.ad+g.ch+g.inf,nn=S.nt+S.nk+S.no+S.nh;
 $('rsum').innerHTML='<div><span>🧭 Travel style</span><span class="pill">'+esc(STYLE?STY[STYLE][0]:'Custom')+'</span></div><div><span>👨‍👩‍👧‍👦 Who and how long</span><span>'+pp+' people · '+nn+' nights</span></div>'+
  '<div><span>🧳 In your trip</span><span>'+out.length+' items</span></div><div class="gt"><span>Estimated total</span><span>'+esc($('barv').getAttribute('data-full')||$('barv').textContent)+'</span></div>';}
function openReview(){TAB='review';FIL='';items();scrollTo(0,0);var sel=document.querySelector('#mtabs [aria-selected=true]');if(sel&&sel.scrollIntoView)sel.scrollIntoView({inline:'center',block:'nearest'});track('review','open');}
function closeReview(){$('rsheet').hidden=true;document.body.style.overflow='';}
$('review').addEventListener('click',openReview);$('rclose').addEventListener('click',closeReview);
$('rgo').addEventListener('click',function(){track('review','book');TAB='book';FIL='';items();scrollTo(0,0);var sel=document.querySelector('#mtabs [aria-selected=true]');if(sel&&sel.scrollIntoView)sel.scrollIntoView({inline:'center',block:'nearest'});});
(function(){var rp=$('rpanel');rp.appendChild($('rlist'));rp.appendChild($('rsum'));rp.appendChild($('rgo'));$('bpanel').appendChild($('rmore'));var m=$('rmore');[$('res'),$('keep'),document.querySelector('.plan'),$('srcs'),document.querySelector('main > .note')].forEach(function(x){if(x)m.appendChild(x);});})();
$('rpanel').addEventListener('click',function(e){var t=e.target.closest('[data-tabgo]');if(t){TAB=t.getAttribute('data-tabgo');FIL='';closeReview();items();document.querySelector('.planner').scrollIntoView({behavior:'smooth'});return;}
 var b=e.target.closest('[data-act]');if(!b)return;var k=b.getAttribute('data-k'),a=b.getAttribute('data-act');
 if(['sanrio','zoo','jr'].indexOf(k)>=0){$(k).value='0';fire($(k));}else{var n=S[k];n=a==='rm'?0:a==='inc'?Math.min(MAX[k],n+1):Math.max(0,n-1);setS(k,n);calc();}
 rrows();track(a==='inc'?'add':'remove',k);});
document.addEventListener('keydown',function(e){if(e.key==='Escape'&&!$('rsheet').hidden)closeReview();});

function kidsUI(){var on=S.ch+S.in+S.tn>0;$('kidsw').setAttribute('aria-pressed',on);$('kidsl').textContent='With kids: '+(on?'ON':'OFF');}
$('kidsw').addEventListener('click',function(){var on=S.ch+S.in+S.tn>0;if(on){setS('ch',0);setS('in',0);setS('tn',0);}else{setS('ch',2);}setS('rm',Math.max(1,Math.ceil((S.ad+S.tn+S.ch)/2)));track('kids',on?'off':'on');calc();});
function curBtns(){$('cur').innerHTML=[['JPY','JPY ¥'],['INR','INR ₹'],['USD','USD $']].map(function(c){return '<button type="button" role="radio" data-cur="'+c[0]+'" aria-checked="'+(CUR===c[0])+'">'+c[1]+'</button>';}).join('');}
$('cur').addEventListener('click',function(e){var b=e.target.closest('[data-cur]');if(!b)return;CUR=b.getAttribute('data-cur');curBtns();track('currency',CUR);styleUI();});
$('reset').addEventListener('click',function(){track('reset');location.href=location.pathname;});
var tt=null;document.addEventListener('click',function(e){if(e.target.closest('.step,select')){clearTimeout(tt);tt=setTimeout(function(){track('change');},1500);}});
if(CURS[Q0.cu])CUR=Q0.cu;curBtns();if(Q0.st&&(STY[Q0.st]||Q0.st==='x'))STYLE=Q0.st==='x'?'':Q0.st;styleBtns();styleUI();if(document.getElementById('from').value)fareUI();calc();track('open',Q0.src||'');
})();
</script>
</body>
</html>
"""
_api = open(os.path.join(os.getcwd(), "api", "flight-price.js"), encoding="utf-8").read()
_codes = [c for _, cs in FROM for c, _ in cs]
assert len(_codes) == len(set(_codes)), "duplicate city code"
assert set(re.findall(r"'([A-Z]{3})'", re.search(r"ORIGINS = new Set\(\[(.*?)\]\)", _api, re.S).group(1))) == set(_codes), "api/flight-price.js ORIGINS differ from FROM"
for _k in ("flights", "jrpass", "transfer", "shinkansen", "parks", "sanrio", "subway", "esim", "insurance"):   # the budget email (api/email-chat.js) uses the same links
    assert "'" + LINKS[_k][1] + "'" in open(os.path.join(os.getcwd(), "api", "email-chat.js"), encoding="utf-8").read(), "email-chat.js link differs: " + _k
FROM_HTML = "".join('<optgroup label="' + g + '">' + "".join('<option value="' + c + '">' + n + "</option>" for c, n in cs) + "</optgroup>" for g, cs in FROM)
LINKS_OUT = {k: v for k, v in LINKS.items() if TOURS_ON or not k.startswith("tours")}
html = (PAGE.replace("%%TOURS%%", "true" if TOURS_ON else "false").replace("%%DATA%%", json.dumps(DATA, ensure_ascii=False))
        .replace("%%LINKS%%", json.dumps(LINKS_OUT, ensure_ascii=False)).replace("%%CHECKED%%", CHECKED).replace("%%FROM%%", FROM_HTML))
assert "%%" not in html
open(os.path.join(PUB, "japan-budget.html"), "w", encoding="utf-8").write(html)
# ---- privacy policy: "Email it to me" on the calculator uses the same email and consent (marker: budget-email-privacy, 28 Nov)
PRIV = os.path.join(PUB, "privacy-policy.html")
pv = open(PRIV, encoding="utf-8").read()
if "budget-email-privacy" not in pv:
    for a, b in [
        ("or ask for the Japanese words from the lucky cat on our Japan page, we use your email address",
         "ask for the Japanese words from the lucky cat on our Japan page, or ask our <span id=\"budget-email-privacy\"></span>Japan budget calculator to email you your budget, we use your email address"),
        ("never your questions themselves) to MailerLite",
         "never your questions themselves; from the budget calculator, tags based on the trip you entered, such as the cities and whether children travel) to MailerLite"),
        ("So you can send an updated chat with one tap, Packy remembers the email address you used in your own browser on that device (not on our servers)",
         "So you can send an updated chat with one tap, Packy (and the budget calculator) remembers the email address you used in your own browser on that device (not on our servers)")]:
        assert pv.count(a) == 1, "privacy policy changed: " + a[:50]
        pv = pv.replace(a, b, 1)
    pv = re.sub(r"<p>Last updated: [A-Za-z]+ \d+, 2026</p>", "<p>Last updated: November 28, 2026</p>", pv, count=1)
    open(PRIV, "w", encoding="utf-8").write(pv)
    print("w86: privacy policy: the budget email")
print("w86 done. public/japan-budget.html written.")
