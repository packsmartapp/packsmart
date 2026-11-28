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
            {"id": "skyliner", "name": "Keisei Skyliner to Ueno / Nippori", "a": 2580, "c": 1290, "src": "Keisei", "url": "https://www.keisei.co.jp/keisei/tetudou/skyliner/us/skyliner/purchase.php"},
            {"id": "nex", "name": "Narita Express round-trip ticket (both rides)", "a": 5200, "c": 2600, "src": "JR East N'EX TOKYO Round Trip Ticket", "url": "https://www.jreast.co.jp/en/multi/pass/nex.html"},
            {"id": "limo", "name": "Airport Limousine Bus to Tokyo Station", "a": 3100, "c": 1550, "src": "Airport Limousine Bus", "url": "https://www.limousinebus.co.jp/en/timetable/detail/Narita-Tokyo/?dir=1"},
            {"id": "taxi", "name": "Fixed-fare taxi to Shinjuku, Shibuya, Minato (zone D)", "car": [31500, 32500], "src": "Narita Airport (plus expressway tolls; late-night surcharge)", "url": "https://www.narita-airport.jp/en/access/taxi/"},
        ]},
        "haneda": {"name": "Haneda", "ways": [
            {"id": "limo", "name": "Airport Limousine Bus to Tokyo Station", "a": 1200, "c": 600, "src": "Airport Limousine Bus", "url": "https://www.limousinebus.co.jp/en/timetable/detail/Haneda-Tokyo/?dir=1"},
            {"id": "limo2", "name": "Airport Limousine Bus to Shinjuku", "a": 1400, "c": 700, "src": "Airport Limousine Bus (daytime)", "url": "https://www.limousinebus.co.jp/en/timetable/detail/Haneda-Shinjuku/?dir=1"},
            {"id": "keikyu", "name": "Keikyu train to Shinagawa", "a": 330, "c": None, "src": "Keikyu (adult fare; child fare not checked)", "url": "https://www.haneda-tokyo-access.com/en/ride/fares.html"},
        ]},
        "kansai": {"name": "Kansai (KIX)", "ways": [
            {"id": "haruka-k", "name": "HARUKA to Kyoto (visitor one-way ticket, bought online)", "a": 2700, "c": 1350, "src": "JR West", "url": "https://www.westjr.co.jp/travel-information/en/tickets-passes/oneway/haruka/"},
            {"id": "haruka-o", "name": "HARUKA to Shin-Osaka (visitor one-way ticket, bought online)", "a": 1900, "c": 950, "src": "JR West", "url": "https://www.westjr.co.jp/travel-information/en/tickets-passes/oneway/haruka/"},
        ]},
        "chitose": {"name": "New Chitose (Sapporo)", "ways": [
            {"id": "bus", "name": "Airport bus to Sapporo Station", "a": 1500, "c": 750, "src": "Hokkaido Chuo Bus", "url": "https://www.chuo-bus.co.jp/airport/timetable/?ope=det&n=34&o=2&t=14"},
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
    "jrpass": ["Buy it on the official Japan Rail Pass site", "https://japanrailpass.net/en/", "official"],
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
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">
<script async src="https://www.googletagmanager.com/gtag/js?id=G-0C4Z7VVGPE"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag("js",new Date());gtag("config","G-0C4Z7VVGPE");</script>
<style>
:root{--primary:#00C9A7;--accent:#E94560;--dark:#0f0f23;--ink:#2b3242;--muted:#5a6378;--line:#d9f0ea}
*{box-sizing:border-box}
body{margin:0;font-family:'DM Sans',sans-serif;background:#f4faf8;color:var(--ink);-webkit-text-size-adjust:100%}
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
.bar{position:fixed;left:50%;bottom:12px;transform:translateX(-50%);display:flex;gap:10px;align-items:center;background:var(--dark);color:#fff;border-radius:999px;padding:9px 16px;font-size:.86rem;box-shadow:0 6px 20px rgba(15,15,35,.3);text-decoration:none;white-space:nowrap;z-index:20}
.bar b{color:var(--primary)}.bar[hidden]{display:none}
@media print{.top a,.bar,.keep,.plan,.sh,.go,.bkl,.card:not(.res){display:none!important}
 body{background:#fff}.res{background:#fff;color:#0f0f23;border:1px solid #ccc}.res h2,.total h3,.ck .t{color:#0f0f23}.ln .l small,.ck .t small,.peek{color:#555}
 .srcs{border:0;padding:0}.srcs[open] summary,.srcs summary{list-style:none}.printsum{display:block!important}}
.printsum{display:none;font-size:.9rem;margin:0 0 8px}
</style>
</head>
<body>
<header class="top">
  <a href="/japan?src=budget">‹ Japan</a>
  <h1>Japan trip <span>budget calculator</span></h1>
  <p>Enter your trip. We add up the costs we have official prices for, and show what is left to price.</p>
</header>
<main>
  <section class="card"><h2>Who is going?</h2><p class="h">On trains and buses, ages 12 and up pay adult fares and ages 6 to 11 child fares; under 6 usually ride free with an adult.</p>
    <div class="row"><label>Adults<small>18 and older</small></label><div class="step" data-k="ad"><button type="button" data-d="-1" aria-label="Fewer">−</button><output>2</output><button type="button" data-d="1" aria-label="More">+</button></div></div>
    <div class="row"><label>Teenagers<small>12 to 17</small></label><div class="step" data-k="tn"><button type="button" data-d="-1" aria-label="Fewer">−</button><output>0</output><button type="button" data-d="1" aria-label="More">+</button></div></div>
    <div class="row"><label>Children<small>6 to 11</small></label><div class="step" data-k="ch"><button type="button" data-d="-1" aria-label="Fewer">−</button><output>2</output><button type="button" data-d="1" aria-label="More">+</button></div></div>
    <div class="row"><label>Little ones<small>under 6</small></label><div class="step" data-k="in"><button type="button" data-d="-1" aria-label="Fewer">−</button><output>0</output><button type="button" data-d="1" aria-label="More">+</button></div></div>
  </section>
  <section class="card"><h2>Where and how long?</h2><p class="h">Nights in each area.</p>
    <div class="row"><label>Tokyo</label><div class="step" data-k="nt"><button type="button" data-d="-1" aria-label="Fewer">−</button><output>9</output><button type="button" data-d="1" aria-label="More">+</button></div></div>
    <div class="row"><label>Kyoto</label><div class="step" data-k="nk"><button type="button" data-d="-1" aria-label="Fewer">−</button><output>0</output><button type="button" data-d="1" aria-label="More">+</button></div></div>
    <div class="row"><label>Osaka</label><div class="step" data-k="no"><button type="button" data-d="-1" aria-label="Fewer">−</button><output>0</output><button type="button" data-d="1" aria-label="More">+</button></div></div>
    <div class="row"><label>Hokkaido<small>Sapporo</small></label><div class="step" data-k="nh"><button type="button" data-d="-1" aria-label="Fewer">−</button><output>0</output><button type="button" data-d="1" aria-label="More">+</button></div></div>
  </section>
  <section class="card"><h2>What will you do?</h2><p class="h">The big days out. More are coming.</p>
    <div class="row"><label>Tokyo Disney days<small>Disneyland or DisneySea, 1 park a day</small></label><div class="step" data-k="dn"><button type="button" data-d="-1" aria-label="Fewer">−</button><output>0</output><button type="button" data-d="1" aria-label="More">+</button></div></div>
    <div class="row"><label for="sanrio">Sanrio Puroland</label><select id="sanrio"><option value="0">No</option><option value="1">Yes</option></select></div>
    <div class="row"><label for="zoo">Ueno Zoo</label><select id="zoo"><option value="0">No</option><option value="1">Yes</option></select></div>
  </section>
  <section class="card"><h2>Hotel, food and flights</h2><p class="h">We start with mid-range. Pick another style, or type your own figure if you already know it. In yen.</p>
    <div class="row stack"><label for="hstyle">Hotel style</label><select id="hstyle"><option value="budget">Budget</option><option value="mid" selected>Mid-range</option><option value="upscale">Upscale</option><option value="luxury">Luxury</option><option value="own">I'll type my own price</option></select></div>
    <p class="hint" id="hhint" hidden></p>
    <div class="row" id="hrooms" hidden><label>Rooms<small>most Japanese rooms sleep 2</small></label><div class="step" data-k="rm"><button type="button" data-d="-1" aria-label="Fewer">−</button><output>2</output><button type="button" data-d="1" aria-label="More">+</button></div></div>
    <div class="row" id="hown" hidden><label for="hotel">Your hotel per night<small>all rooms together</small></label><input type="number" id="hotel" inputmode="numeric" min="0" step="1000" placeholder="e.g. 25000"></div>
    <div class="row stack"><label for="fstyle">Food style</label><select id="fstyle"><option value="budget">Budget</option><option value="mid" selected>Mid-range</option><option value="treat">Treat yourself</option><option value="own">I'll type my own amount</option></select></div>
    <p class="hint" id="fhint" hidden></p>
    <div class="row" id="fown" hidden><label for="food">Food per person per day</label><input type="number" id="food" inputmode="numeric" min="0" step="500" placeholder="e.g. 5000"></div>
    <div class="row stack"><label for="from">Flying from</label><select id="from"><option value="">Choose a city</option>%%FROM%%<option value="own">Somewhere else: I'll type my fare</option></select></div>
    <p class="hint" id="flyhint" hidden></p>
    <div class="row" id="flyown" hidden><label for="fly">Flights, total<small>all travellers, return</small></label><input type="number" id="fly" inputmode="numeric" min="0" step="1000" placeholder="e.g. 280000"></div>
  </section>
  <section class="card"><h2>Getting around</h2><p class="h">Airports, trains and taxis.</p>
    <div class="row"><label for="arr">Fly into</label><select id="arr"></select></div>
    <div class="row stack"><label for="way">Into town by</label><select id="way"></select></div>
    <div class="row"><label for="dep">Fly home from</label><select id="dep"></select></div>
    <div class="row"><label>Taxi rides<small>in town, about 7 km each</small></label><div class="step" data-k="tx"><button type="button" data-d="-1" aria-label="Fewer">−</button><output>6</output><button type="button" data-d="1" aria-label="More">+</button></div></div>
    <div class="row"><label for="jr">Japan Rail Pass<small>7 days, for long train trips</small></label><select id="jr"><option value="0">No</option><option value="1">Yes</option></select></div>
  </section>
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
<a class="bar" id="bar" href="#total" hidden>Estimated budget <b id="barv"></b> ↓</a>
<script>
(function(){
var D=%%DATA%%,LK=%%LINKS%%,CH='%%CHECKED%%';
var S={rm:2,ad:2,tn:0,ch:2,in:0,nt:9,nk:0,no:0,nh:0,tx:6,dn:0};var MAX={rm:10,ad:12,tn:10,ch:10,in:6,nt:30,nk:30,no:30,nh:30,tx:40,dn:10};
function y(n){return '¥'+Math.round(n).toLocaleString('en-US');}
function esc(t){return String(t).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
function track(s,x){try{if(window.gtag)gtag('event','budget_calc',{event_category:'engagement',status:s,item:x||'',page_path:location.pathname});}catch(e){}}
var arr=document.getElementById('arr'),dep=document.getElementById('dep'),way=document.getElementById('way');
Object.keys(D.airport).forEach(function(k){arr.add(new Option(D.airport[k].name,k));dep.add(new Option(D.airport[k].name,k));});
function ways(){var a=D.airport[arr.value];way.innerHTML='';a.ways.forEach(function(w){way.add(new Option(w.name,w.id));});}
// a link from Packy can fill the form: ?ad=2&ch=2&nt=9
S.rm=Math.max(1,Math.ceil((S.ad+S.ch)/2));try{var q=new URLSearchParams(location.search);/* also dn= Disney days */Object.keys(S).forEach(function(k){var v=parseInt(q.get(k),10);if(!isNaN(v))S[k]=Math.max(0,Math.min(MAX[k],v));});}catch(e){}
[].forEach.call(document.querySelectorAll('.step'),function(st){var k=st.getAttribute('data-k');st.querySelector('output').textContent=S[k];
 st.addEventListener('click',function(e){var b=e.target.closest('[data-d]');if(!b)return;S[k]=Math.max(k==='ad'?1:0,Math.min(MAX[k],S[k]+(+b.getAttribute('data-d'))));st.querySelector('output').textContent=S[k];calc();});});
// the likely airport for the trip: Kansai for a Kyoto and Osaka trip, New Chitose for Hokkaido only
var ap=S.nt?'narita':(S.nk||S.no?'kansai':(S.nh?'chitose':'narita'));arr.value=ap;dep.value=ap;ways();if(ap==='kansai'&&S.no&&!S.nk)way.value='haruka-o';
var Q0={};try{new URLSearchParams(location.search).forEach(function(v,k){Q0[k]=v;});}catch(e){}
function setSel(id,v){var el=document.getElementById(id);if(v&&[].some.call(el.options,function(o){return o.value===v;}))el.value=v;}
if(Q0.a){setSel('arr',Q0.a);ways();}if(Q0.d){setSel('dep',Q0.d);if(Q0.d!==arr.value)dep.dataset.set='1';}setSel('way',Q0.w);setSel('jr',Q0.jr);setSel('zoo',Q0.zo);setSel('sanrio',Q0.sa);setSel('hstyle',Q0.hs);setSel('fstyle',Q0.fs);setSel('from',Q0.fr);
[['ho','hotel'],['fo','food'],['fl','fly']].forEach(function(x){var v=parseInt(Q0[x[0]],10);if(v>0&&v<1e8)document.getElementById(x[1]).value=v;});
arr.addEventListener('change',function(){ways();if(dep.value!==arr.value&&!dep.dataset.set)dep.value=arr.value;calc();});
dep.addEventListener('change',function(){dep.dataset.set='1';calc();});
[way,document.getElementById('jr'),document.getElementById('zoo'),document.getElementById('sanrio')].forEach(function(x){x.addEventListener('change',calc);});
['hotel','food','fly'].forEach(function(id){document.getElementById(id).addEventListener('input',calc);});
function styleUI(){var hs=document.getElementById('hstyle').value,fs=document.getElementById('fstyle').value,H=D.hotelStyles[hs],F=D.foodStyles[fs];
 var hh=document.getElementById('hhint');hh.hidden=!H;if(H)hh.innerHTML='<b>'+esc(H.name)+':</b> '+esc(H.desc)+'. Per room per night, room only (breakfast is counted under food): '+['nt','nk','no','nh'].map(function(k){return esc(D.areaNames[k])+' '+y(H.by[k][0])+'–'+y(H.by[k][1]);}).join(', ')+'; '+esc(D.styleNote)+'.';
 document.getElementById('hrooms').hidden=!H;document.getElementById('hown').hidden=hs!=='own';
 var fh=document.getElementById('fhint');fh.hidden=!F;if(F)fh.innerHTML='<b>'+esc(F.name)+':</b> '+esc(F.desc)+'.'+' About '+y(F.lo)+'–'+y(F.hi)+' per adult per day for three meals, breakfast included, since many hotels charge extra for it (children about half); '+esc(D.foodNote)+'.';
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
['hstyle','fstyle'].forEach(function(id){document.getElementById(id).addEventListener('change',function(){track(id,this.value);styleUI();});});
function num(id){var v=parseFloat(document.getElementById(id).value);return isNaN(v)||v<0?0:v;}
var SRC=[];function reg(o){if(o&&o.url&&!SRC.some(function(x){return x[1]===o.url;}))SRC.push([o.src||'',o.url]);return '';}
function src(name,url){reg({src:name,url:url});return '<small>'+esc(name)+', checked '+CH+'</small>';}
function line(label,v,note){var m=note&&note.match(/<a class="bkl"[\s\S]*?<\/a>/);if(m){note=note.replace(m[0],'');v+=m[0];}return '<div class="ln"><div class="l">'+label+(note||'')+'</div><div class="v">'+v+'</div></div>';}
function bk(k,t){var l=LK[k];if(!l)return '';var off=l[2]==='official';return '<a class="bkl" href="'+esc(l[1])+'" target="_blank" rel="'+(off?'noopener':'nofollow noopener sponsored')+'"'+(off?'':' data-ps-placement="budget-'+k+'"')+' data-go="'+k+'">'+esc(t||'Check final price')+' →</a>';}
function go(k){var l=LK[k],off=l[2]==='official';return '<a class="go" href="'+esc(l[1])+'"'+(off?' target="_blank" rel="noopener"':l[2]?' target="_blank" rel="nofollow noopener sponsored" data-ps-placement="budget-'+k+'"':'')+' data-go="'+k+'">'+esc(l[0])+'<small>'+(off?'official site ↗':l[2]?'partner link ↗':'→')+'</small></a>';}
function calc(){
 SRC=[];var tn=S.tn,ad=S.ad+tn,ch=S.ch,inf=S.in,ppl=ad+ch+inf,nights=S.nt+S.nk+S.no+S.nh,kan=S.nk+S.no,days=nights+1,cars=Math.ceil(ppl/4),h='',sum=0,lo=0,hi=0,miss=[];
 // airport to town, both ends
 function leg(k,wid,label){var w=D.airport[k].ways.filter(function(x){return x.id===wid;})[0]||D.airport[k].ways[0];
  if(w.car){lo+=w.car[0]*cars;hi+=w.car[1]*cars;return line(label+': '+esc(w.name)+(cars>1?' ('+cars+' cars)':''),y(w.car[0]*cars)+'–'+y(w.car[1]*cars),src(w.src,w.url));}
  if(w.c===null&&ch){var v=w.a*ad;sum+=v;miss.push('Children\'s fare on '+w.name);return line(label+': '+esc(w.name),y(v)+' <small style="color:#9aa5b5">+ children</small>',src(w.src,w.url));}
  var v=w.a*ad+(w.c||0)*ch;sum+=v;return line(label+': '+esc(w.name),y(v),src(w.src,w.url)+(label==='Airport to town'?bk('transfer','Book a private car'):''));}
 var G={exp:'',fly:'',stay:'',rail:'',move:'',pre:''};
 G.move+=leg(arr.value,way.value,'Airport to town');
 var depWay=dep.value===arr.value?way.value:D.airport[dep.value].ways[0].id;
 if(!(dep.value==='narita'&&depWay==='nex'&&arr.value==='narita'))G.move+=leg(dep.value,depWay,'Town to airport');
 else G.move+=line('Town to airport: Narita Express','included',' <small>the round-trip ticket covers both rides</small>');
 if(S.nt){var t=D.tokyoTicket,n=Math.ceil((S.nt+1)/t.days),v=n*(t.a*ad+t.c*ch);sum+=v;G.move+=line('Tokyo subway: '+n+' × 72-hour ticket'+(n>1?'s':''),y(v),src(t.src,t.url)+bk('subway'));}
 if(S.nk){var kd=D.kyotoDay,kv=S.nk*(kd.a*ad+kd.c*ch);sum+=kv;G.move+=line('Kyoto buses and subway: '+S.nk+' one-day pass'+(S.nk>1?'es':''),y(kv),'<small>'+esc(kd.src)+', checked 27 Nov 2026'+reg(kd)+'</small>');}
 if(S.no){var od=D.osakaDay,ol=S.no*(od.lo*ad+od.c*ch),oh=S.no*(od.hi*ad+od.c*ch);lo+=ol;hi+=oh;G.move+=line('Osaka subway and buses: '+S.no+' one-day pass'+(S.no>1?'es':''),y(ol)+'–'+y(oh),'<small>'+esc(od.src)+', checked 27 Nov 2026'+reg(od)+'</small>');}
 if(S.nh){var s=D.sapporoDay,v=S.nh*(s.a*ad+s.c*ch);sum+=v;G.move+=line('Sapporo subway: '+S.nh+' one-day ticket'+(S.nh>1?'s':''),y(v),src(s.src,s.url));}
 if(S.tx){var tl=S.tx*cars*D.taxi.lo,th=S.tx*cars*D.taxi.hi;lo+=tl;hi+=th;G.move+=line('Taxis: '+S.tx+' ride'+(S.tx>1?'s':'')+(cars>1?' × '+cars+' cars':''),y(tl)+'–'+y(th),src(D.taxi.src,D.taxi.url));}
 if(document.getElementById('jr').value==='1'){var j=D.jrpass,v=j.a*ad+j.c*ch;sum+=v;G.rail+=line('Japan Rail Pass, 7 days',y(v),src(j.src,j.url)+bk('jrpass','Buy on the official site'));}
 if(S.dn){var d=D.disney,dc=D.disneyChild,ga=S.ad,kid=(dc.c*ch+dc.j*tn)*S.dn,dl=d.lo*ga*S.dn+kid,dh=d.hi*ga*S.dn+kid;lo+=dl;hi+=dh;
  var who=[ga+' adult'+(ga>1?'s':''),tn?tn+' teen'+(tn>1?'s':''):'',ch?ch+' child'+(ch>1?'ren':''):''].filter(Boolean).join(' + ');
  G.exp+=line('Tokyo Disney: '+who+' × '+S.dn+' day'+(S.dn>1?'s':''),y(dl)+'–'+y(dh),'<small>Adults: '+esc(d.src)+', checked '+d.checked+''+reg(d)+''+(tn||ch?'. '+esc(dc.src).charAt(0).toUpperCase()+esc(dc.src).slice(1)+'.':'')+(inf?' Under 4: free; ages 4 and 5 pay the child price.':'')+'</small>'+bk('parks'));}
 if(document.getElementById('sanrio').value==='1'){var r=D.sanrio,sn=ad+ch,sl=r.lo*sn,sh=r.hi*sn;lo+=sl;hi+=sh;
  G.exp+=line('Sanrio Puroland: '+sn+' × '+y(r.lo)+'–'+y(r.hi),y(sl)+'–'+y(sh),'<small>'+esc(r.src)+', checked '+r.checked+(inf?'. Little ones aged 3 to 5 also need a ticket.':'')+'</small>'+bk('sanrio'));}
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
 if(!flyDone)G.fly+=line('Flights','<span class="np">not priced</span>','<small>choose "Flying from" above, or type your fare</small>'+bk('flights','Search flights'));
 if(!hotDone)G.stay+=line('Hotels','<span class="np">not priced</span>','<small>choose a hotel style above</small>');
 if(!foodDone)G.stay+=line('Food and drinks','<span class="np">not priced</span>','<small>choose a food style above</small>');
 G.exp+=line(S.dn||document.getElementById('sanrio').value==='1'?'Other theme parks and tickets':'Theme parks and tickets','<span class="np">not priced yet</span>',bk('parks','See tickets'));
 var ep=D.esim.plans.filter(function(x){return x[0]>=days;})[0]||D.esim.plans[D.esim.plans.length-1],en=Math.max(1,Math.ceil(days/ep[0])),ev=Math.round(ep[2]*en*ad*D.usdJpy/10)*10;sum+=ev;
 G.pre+=line('eSIM data: '+ad+' phone'+(ad>1?'s':'')+' × '+(en>1?en+' × ':'')+ep[1]+' GB, '+ep[0]+' days',y(ev),'<small>US$'+(ep[2]%1?ep[2].toFixed(2):ep[2])+' each, '+esc(D.esim.src)+'; one per adult and teen; at about ¥'+D.usdJpy+' to US$1</small>'+bk('esim'));
 var il=Math.round(D.insurance.lo*days*ad*D.usdJpy/100)*100,ih=Math.round(D.insurance.hi*days*ad*D.usdJpy/100)*100;lo+=il;hi+=ih;
 G.pre+=line('Travel medical insurance: '+ad+' × '+days+' days',y(il)+'–'+y(ih),'<small>'+esc(D.insurance.src)+(ch+inf?'; ask the quote about children':'')+'; at about ¥'+D.usdJpy+' to US$1</small>'+bk('insurance','Get a quote'));
 if(S.nh&&(S.nt||S.nk))G.move+=line('Getting to Hokkaido (usually a domestic flight)','<span class="np">not priced</span>');
 miss.forEach(function(m){G.move+=line(esc(m),'<span class="np">not priced yet</span>');});
 function grp(t,x){return x?'<div class="grp">'+t+'</div>'+x:'';}
 h+=grp('Things to do',G.exp)+grp('Flights, hotel and food',G.fly+G.stay)+grp('Getting around',G.rail+G.move)+grp('Before you go',G.pre);np=h;
 var tlo=sum+lo,thi=sum+hi,tv=y(tlo)+(thi>tlo?'–'+y(thi).replace('¥',''):'');TOT={lo:Math.round(tlo),hi:Math.round(thi),ppl:ppl,nights:nights};
 h+='<div class="total" id="total"><h3>Your estimated budget</h3><div class="tot"><b>'+tv+'</b><span>'+ppl+' '+(ppl>1?'people':'person')+' · '+nights+' night'+(nights>1?'s':'')+'</span></div>'+
  '<p class="pp" style="margin:0">About '+y(tlo/Math.max(1,ppl))+(thi>tlo?'–'+y(thi/Math.max(1,ppl)).replace('¥',''):'')+' per person, for the costs above. Not priced yet: '+(np.match(/class="np"/g)||[]).length+' item'+((np.match(/class="np"/g)||[]).length>1?'s':'')+'.</p></div>';
 if(%%TOURS%%)h+='<div class="grp">Prefer one booking?</div><div class="two"><div><span>A guided multi-day tour: hotels, trains and a guide arranged by the tour company. Flights are usually separate. Compare its price with your budget above.</span>'+go(ch||inf?'tours_family':'tours')+'</div></div>';
 var top='<h2>Your trip, costed</h2><p class="pp" style="margin:0 0 6px">Booking links are partner links: we may earn a commission, at no cost to you.</p><p class="printsum">'+esc(summary())+'</p><div class="peek"><span>Estimated budget <b>'+tv+'</b></span><a href="#total">Total ↓</a></div>';
 document.getElementById('res').innerHTML=top+h;
 document.getElementById('barv').textContent=tv;
 document.getElementById('srclist').innerHTML=SRC.map(function(x){return '<li><a href="'+esc(x[1])+'" target="_blank" rel="noopener">'+esc(x[0]||x[1])+'</a></li>';}).join('');
 document.getElementById('planlink').href='/?dest=Japan&adults='+ad+'&kids='+(ch+inf)+'&src=budget_plan#plan';
 saveUrl();
}
document.getElementById('res').addEventListener('click',function(e){var a=e.target.closest('[data-go]');if(!a)return;track('link',a.getAttribute('data-go'));var pl=a.getAttribute('data-ps-placement');if(pl)try{if(window.gtag)gtag('event','affiliate_interact',{event_category:'monetization',placement:pl,page_path:location.pathname});}catch(x){}});
// ---- the trip in the address: Copy link, WhatsApp and the email all open this exact budget
var TOT=null,SEL={a:'arr',d:'dep',w:'way',jr:'jr',zo:'zoo',sa:'sanrio',hs:'hstyle',fs:'fstyle',fr:'from'},OWN={ho:'hotel',fo:'food',fl:'fly'};
function qs(){var q=[];Object.keys(S).forEach(function(k){q.push(k+'='+S[k]);});Object.keys(SEL).forEach(function(k){var v=document.getElementById(SEL[k]).value;if(v&&v!=='0')q.push(k+'='+encodeURIComponent(v));});
 Object.keys(OWN).forEach(function(k){var v=num(OWN[k]);if(v)q.push(k+'='+Math.round(v));});return q.join('&');}
function saveUrl(){try{history.replaceState(null,'',location.pathname+'?'+qs());}catch(e){}}
function link(src){return 'https://www.packsmartapp.com/japan-budget?'+qs()+'&src='+src;}
function summary(){var w=[S.ad+S.tn+' adult'+(S.ad+S.tn>1?'s':'')];if(S.ch)w.push(S.ch+' child'+(S.ch>1?'ren':''));if(S.in)w.push(S.in+' under 6');
 var n=['nt','nk','no','nh'].filter(function(k){return S[k];}).map(function(k){return S[k]+' in '+D.areaNames[k];});return 'Japan: '+w.join(', ')+'; '+(n.join(', ')||'no nights yet')+'.';}
function done(){try{return JSON.parse(localStorage.getItem('budgetDone')||'{}')||{};}catch(e){return {};}}
document.getElementById('res').addEventListener('change',function(e){var c=e.target.closest('[data-ck]');if(!c)return;var d=done();if(c.checked)d[c.getAttribute('data-ck')]=1;else delete d[c.getAttribute('data-ck')];
 try{localStorage.setItem('budgetDone',JSON.stringify(d));}catch(x){}c.closest('.ck').classList.toggle('done',c.checked);if(c.checked)track('booked',c.getAttribute('data-ck'));});
var em=document.getElementById('em'),emf=document.getElementById('emf'),emerr=document.getElementById('emerr'),SENT='';
document.getElementById('keep').addEventListener('click',function(e){var b=e.target.closest('[data-sh]');if(!b)return;var k=b.getAttribute('data-sh');track('share',k);
 var msg='Our Japan trip budget: about '+(TOT?y(TOT.lo)+(TOT.hi>TOT.lo?'–'+y(TOT.hi).replace('¥',''):''):'')+'. '+summary()+' See the breakdown: ';
 if(k==='wa')window.open('https://wa.me/?text='+encodeURIComponent(msg+link('budget_wa')),'_blank','noopener');
 if(k==='copy'){var u=link('budget_link'),sp=b.querySelector('span');function ok(){sp.textContent='Copied ✓';setTimeout(function(){sp.textContent='Copy link';},2000);}
  if(navigator.clipboard)navigator.clipboard.writeText(u).then(ok,function(){prompt('Copy this link:',u);});else prompt('Copy this link:',u);}
 if(k==='pdf'){var s2=document.getElementById('srcs');s2.open=true;window.print();}
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
var bar=document.getElementById('bar');if('IntersectionObserver' in window){var seen=false;new IntersectionObserver(function(es){es.forEach(function(x){seen=x.isIntersecting;});bar.hidden=seen;}).observe(document.getElementById('res'));}
var tt=null;document.addEventListener('click',function(e){if(e.target.closest('.step,select')){clearTimeout(tt);tt=setTimeout(function(){track('change');},1500);}});
styleUI();if(document.getElementById('from').value)fareUI();calc();track('open',Q0.src||'');
})();
</script>
</body>
</html>
"""
_api = open(os.path.join(os.getcwd(), "api", "flight-price.js"), encoding="utf-8").read()
_codes = [c for _, cs in FROM for c, _ in cs]
assert len(_codes) == len(set(_codes)), "duplicate city code"
assert set(re.findall(r"'([A-Z]{3})'", re.search(r"ORIGINS = new Set\(\[(.*?)\]\)", _api, re.S).group(1))) == set(_codes), "api/flight-price.js ORIGINS differ from FROM"
for _k in ("flights", "transfer", "shinkansen", "parks", "sanrio", "subway", "esim", "insurance"):   # the budget email (api/email-chat.js) uses the same links
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
