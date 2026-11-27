#!/usr/bin/env python3
"""
w73: the Japan hub page /japan, and a "Welcome to Japan" banner on /blog when the Japan chip is picked (24 Nov 2026).

Why: Japan is the lead topic (D48), but its guides were spread over /blog (country guides, itinerary) and
/travel-essentials (airport and station guides), and nothing showed them together with the Pocket Guides.
The owner's mock-up: pick Japan on /blog and see every Japan guide and Pocket Guide in one place.

What it does (idempotent; every run rebuilds public/japan.html from the current pages):
  1. Builds public/japan.html from public/travel-essentials.html (head, styles, nav, footer, filter script, and its
     Pocket Guide block with ?src=hub_japan), with three filterable sections of cards: Plan your trip (cards copied
     from /blog), Arriving and Stations (cards copied from /travel-essentials, so titles, photos and read times stay in
     step with w59 and w69). Below them, link lists for Hokkaido this winter and for the seasons.
     An empty slot (<!-- ask-japan-slot -->) is kept for the planned "Ask about Japan" assistant.
  2. Adds /japan to public/sitemap.xml (lastmod moves forward only when the page changed).
  3. Adds a banner to public/blog.html that shows while the Japan chip is selected (marker: id="jpHubBanner").

Run after w69 and before w72:  python3 tools/w73_japan_hub.py
Aborts without writing if an expected anchor or card is missing.
"""
import datetime, hashlib, json, os, re, sys

ROOT = os.getcwd()
PUB = os.path.join(ROOT, "public")
TE = os.path.join(PUB, "travel-essentials.html")
BLOG = os.path.join(PUB, "blog.html")
OUT = os.path.join(PUB, "japan.html")
SITEMAP = os.path.join(PUB, "sitemap.xml")
URL = "https://www.packsmartapp.com/japan"
TODAY = datetime.date.today().isoformat()

TITLE = "Japan Travel Guides: Airports, Stations, Pocket Guides &amp; Itineraries | PackSmart"
DESC = ("Every PackSmart guide for Japan in one place: trip planning, the Narita, Haneda, Kansai and New Chitose airports, "
        "Tokyo, Kyoto, Osaka and Sapporo stations, and Pocket Guides that work offline.")

PLAN = ["japan-travel-packing-guide", "japan-7-day-itinerary-budget", "kyoto-travel-guide", "osaka-travel-guide"]
ARRIVE = ["narita-airport-guide", "haneda-airport-guide", "kansai-airport-guide", "new-chitose-airport-guide"]
STATIONS = ["tokyo-station-guide", "shinjuku-station-guide", "ueno-station-guide", "kyoto-station-guide",
            "osaka-station-guide", "sapporo-station-guide"]


def die(msg):
    sys.exit("w73 aborted, nothing written: " + msg)


def sub1(s, pattern, repl, what, flags=0):
    s2, n = re.subn(pattern, lambda m: repl, s, count=1, flags=flags)
    if n != 1:
        die("anchor not found: " + what)
    return s2


def card(src, slug, where):
    m = re.search(r'\n([ \t]*)<a href="/blog/%s" class="blog-card"[^>]*>.*?</a>' % re.escape(slug), src, re.S)
    if not m:
        die("card for %s not found on %s" % (slug, where))
    c = m.group(0).lstrip("\n")
    c = re.sub(r'(<a href="/blog/%s" class="blog-card")[^>]*>' % re.escape(slug), r"\1>", c, count=1)
    return "        " + c.strip()


te = open(TE, encoding="utf-8").read()
blog = open(BLOG, encoding="utf-8").read()

# ---- head: retitle the Travel Essentials head
head = te[:te.index("</head>")]
head = sub1(head, r"<title>.*?</title>", "<title>%s</title>" % TITLE, "title")
head = sub1(head, r'<meta name="description" content="[^"]*">', '<meta name="description" content="%s">' % DESC, "description")
head = sub1(head, r'<link rel="canonical" href="[^"]*">', '<link rel="canonical" href="%s">' % URL, "canonical")
for prop in ("og:title", "twitter:title"):
    attr = "property" if prop.startswith("og") else "name"
    head = sub1(head, r'<meta %s="%s" content="[^"]*">' % (attr, prop), '<meta %s="%s" content="%s">' % (attr, prop, TITLE), prop)
for prop in ("og:description", "twitter:description"):
    attr = "property" if prop.startswith("og") else "name"
    head = sub1(head, r'<meta %s="%s" content="[^"]*">' % (attr, prop), '<meta %s="%s" content="%s">' % (attr, prop, DESC), prop)
head = sub1(head, r'<meta property="og:url" content="[^"]*">', '<meta property="og:url" content="%s">' % URL, "og:url")
LD = ('{"@context": "https://schema.org", "@type": "CollectionPage", "name": "Japan travel guides", "url": "%s", '
      '"description": "%s", "publisher": {"@type": "Organization", "name": "PackSmart"}}' % (URL, DESC.replace('"', "'")))
head = re.sub(
    r'<script type="application/ld\+json">\s*\{"@context": "https://schema.org", "@type": "CollectionPage".*?</script>',
    lambda m: '<script type="application/ld+json">\n' + LD + '\n</script>', head, count=1, flags=re.S)
if LD not in head:
    die("JSON-LD not replaced")
HUB_CSS = """<style id="jp-hub-css">
.jp-links{background:#fff;border-radius:20px;padding:1.4rem 1.5rem;margin:0 0 1.6rem;box-shadow:0 2px 10px rgba(15,15,35,.05)}
.jp-links h2{font-size:1.35rem;margin:0 0 .3rem}
.jp-links p{margin:0 0 .8rem;color:#5a6378}
.jp-links ul{list-style:none;margin:0;padding:0;display:grid;gap:8px}
.jp-links li a{display:flex;align-items:center;gap:10px;min-height:44px;padding:8px 12px;border:1.5px solid #E3E8EC;border-radius:12px;color:#0f0f23;text-decoration:none;font-weight:600}
.jp-links li a:hover{border-color:#00C9A7}
.jp-links li small{display:block;font-weight:500;color:#5a6378}
.jp-two{display:grid;grid-template-columns:1fr 1fr;gap:1.2rem}
@media (max-width:760px){.jp-two{grid-template-columns:1fr}.jp-links{padding:1.1rem 1rem}}
/* the maneki-neko (lucky cat) beckons at the Ask Packy box; its paw waves gently (still with reduced motion) */
.jp-cat{position:absolute;right:-26px;top:-86px;width:96px;cursor:pointer;filter:drop-shadow(0 6px 10px rgba(15,15,35,.12))}
.jp-cat svg{position:relative;z-index:2;width:100%;height:auto;display:block}
.jp-cat .paw{transform-box:view-box;transform-origin:146px 112px;animation:jpBeckon 2.4s ease-in-out infinite}
.jp-cat-say{position:absolute;right:58%;top:4%;z-index:1;white-space:nowrap;background:linear-gradient(135deg,#00C9A7,#2D9CDB);color:#fff;font-size:.82rem;font-weight:800;padding:8px 40px 8px 13px;border-radius:18px 6px 18px 18px;box-shadow:0 8px 20px rgba(45,156,219,.3);opacity:0;transform:translateX(6px) scale(.9);transform-origin:top right;transition:opacity .18s,transform .18s;pointer-events:none}
.jp-cat-say span{color:#FFE66D;margin-right:4px}.jp-cat-say small{display:block;font-size:.68rem;font-weight:700;color:#fff;opacity:.92;margin-top:2px}
/* after a couple of Konnichiwas the cat offers a few Japanese words (same wording as the Pocket Guides' phrase list) */
.jp-cat-offer{position:absolute;right:52px;top:-92px;z-index:2;width:236px;background:linear-gradient(135deg,#00C9A7,#2D9CDB);color:#fff;border-radius:18px 6px 18px 18px;padding:10px 40px 11px 13px;box-shadow:0 8px 20px rgba(45,156,219,.3);font-size:.84rem;font-weight:800;line-height:1.35;animation:jpOfferIn .25s ease-out}
.jp-cat-offer[hidden]{display:none}
.jp-cat.offering .jp-cat-say{opacity:0!important;transform:translateX(6px) scale(.9)!important}
.jp-cat-offer b{color:#FFE66D}
.jp-cat-offer div{display:flex;gap:6px;margin-top:8px}
.jp-cat-offer button{font:inherit;font-size:.78rem;font-weight:800;border:0;border-radius:999px;padding:6px 12px;cursor:pointer}
.jp-cat-offer .y{background:#fff;color:#0a8f78}.jp-cat-offer .n{background:rgba(255,255,255,.2);color:#fff}
@keyframes jpOfferIn{from{opacity:0;transform:translateX(8px) scale(.94)}to{opacity:1;transform:none}}
@media (max-width:600px){.jp-cat-offer{right:34px;top:-70px;width:212px;font-size:.8rem}}
.jp-words{position:fixed;inset:0;z-index:300;display:flex;align-items:center;justify-content:center;padding:16px;background:rgba(15,15,35,.45)}
.jp-words[hidden]{display:none}
.jp-words-in{position:relative;width:100%;max-width:440px;max-height:calc(100vh - 32px);overflow:auto;background:#fff;border-radius:22px;padding:18px 18px 16px;box-shadow:0 20px 50px rgba(15,15,35,.3);animation:jpOfferIn .25s ease-out}
.jp-words h3{margin:0 34px 2px 0;font-size:1.15rem;color:#0f0f23}.jp-words h3 span{color:#E94560}
.jp-words-sub{margin:0 0 12px;font-size:.82rem;color:#5a6378}
.jp-words-x{position:absolute;right:12px;top:12px;width:32px;height:32px;border:0;border-radius:50%;background:#F1F4F6;color:#0f0f23;font-size:1rem;cursor:pointer}
.jp-words ul{list-style:none;margin:0;padding:0;display:grid;gap:7px}
.jp-words li{display:grid;grid-template-columns:28px minmax(0,1fr) 38px;align-items:center;gap:8px;background:#F2FBF8;border-radius:14px;padding:7px 8px 7px 10px}
.jp-words li i{font-style:normal;font-size:1.2rem;text-align:center}
.jp-words li b{display:block;font-size:.95rem;color:#0f0f23}.jp-words li b span{display:block;font-weight:700;color:#0a8f78;font-size:.84rem;margin-top:1px}
.jp-words li small{display:block;font-size:.76rem;color:#5a6378}
.jp-words li button{width:36px;height:36px;border:0;border-radius:50%;background:#00C9A7;color:#fff;font-size:.95rem;cursor:pointer}
.jp-words li button:hover{background:#00A88C}
.jp-lesson li i{font-size:.85rem;font-weight:700;color:#0a8f78}
.jp-lesson li.hot{background:#FFF1F4;box-shadow:0 0 0 2px #E94560 inset}.jp-lesson li.hot button{background:#E94560;animation:jpPing 1.6s ease-in-out 3}
@keyframes jpPing{50%{box-shadow:0 0 0 7px rgba(233,69,96,.18)}}
@media (prefers-reduced-motion:reduce){.jp-lesson li.hot button{animation:none}}
.jp-wa{display:block;margin:10px 0 0;text-align:center;font-weight:800;font-size:.9rem;color:#fff;background:#25D366;border-radius:999px;padding:10px 14px;text-decoration:none}
.jp-words-more{display:block;margin:12px 0 0;text-align:center;font-size:.86rem;font-weight:800;color:#0a8f78;background:#E6FAF5;border-radius:12px;padding:10px;text-decoration:none}
.jp-words-note{margin:8px 0 0;font-size:.7rem;color:#8a93a6;text-align:center}
.jp-words-mail{position:sticky;bottom:-16px;z-index:2;margin:12px 0 0;background:linear-gradient(135deg,#E6FAF5,#E8F4FC);border:1.5px solid #BFEDE3;border-radius:14px;padding:12px;font-size:.88rem;color:#0f0f23;box-shadow:0 -10px 18px rgba(255,255,255,.95)}
.jp-words-mail b{display:block;margin:0 0 6px}.jp-words-mail p{margin:0 0 8px;color:#3f4a5c}
.jp-words-mbtn{display:block;width:100%;font:inherit;font-weight:800;font-size:.92rem;border:0;border-radius:999px;padding:11px 14px;background:linear-gradient(135deg,#E94560,#ff6b85);color:#fff;cursor:pointer}
.jp-words-mail .r{display:flex;gap:6px}.jp-words-mail input{flex:1;min-width:0;font:inherit;font-size:16px;border:1.5px solid #BFEDE3;border-radius:999px;padding:9px 14px;background:#fff;color:#0f0f23}
.jp-words-mail .r button{flex:none;font:inherit;font-weight:800;border:0;border-radius:999px;padding:9px 16px;background:linear-gradient(135deg,#E94560,#ff6b85);color:#fff;cursor:pointer}
.jp-words-mail .r button[disabled]{opacity:.6}
.jp-words-mail .f{display:block;margin-top:6px;font-size:.72rem;color:#5a6378}.jp-words-mail .f a{color:#5a6378}
.jp-words-mail .e{display:block;margin-top:6px;font-size:.78rem;color:#c0284a;font-weight:700}
.jp-words-mail .r2{display:flex;flex-wrap:wrap;gap:6px}
.jp-words-mail .r2 button{font:inherit;font-size:.8rem;font-weight:800;border:1.5px solid #BFEDE3;border-radius:999px;padding:7px 12px;background:#fff;color:#0a8f78;cursor:pointer}
.jp-words-mail .r2 .y{background:#00C9A7;border-color:#00C9A7;color:#fff}
@media (max-width:600px){.jp-words{align-items:flex-end;padding:0}.jp-words-in{max-width:none;border-radius:22px 22px 0 0;max-height:88vh;padding-bottom:calc(16px + env(safe-area-inset-bottom))}}
@media (prefers-reduced-motion:reduce){.jp-cat-offer,.jp-words-in{animation:none}}
/* the bubble stays from page load until the first tap, so readers know the cat can be tapped (owner, 26 Nov) */
.jp-cat:hover .jp-cat-say,.jp-cat.on .jp-cat-say,.jp-cat:not(.heard) .jp-cat-say{opacity:1;transform:none}
.jp-cat:hover .paw,.jp-cat.on .paw{animation-duration:.8s}
@keyframes jpBeckon{0%,55%,100%{transform:rotate(0)}65%{transform:rotate(-16deg)}75%{transform:rotate(4deg)}85%{transform:rotate(-12deg)}}
/* a small sound badge so phone users (no hover) know the cat can be tapped; gone once it has been */
.jp-cat-tap{position:absolute;left:2px;bottom:16%;z-index:3;width:28px;height:28px;border-radius:50%;background:#E94560;color:#fff;font-size:.8rem;line-height:1;display:flex;align-items:center;justify-content:center;border:2px solid #fff;box-shadow:0 3px 8px rgba(233,69,96,.35);animation:jpTapPulse 2.2s ease-out infinite}
.jp-cat.heard .jp-cat-tap{display:none}
.jp-cat:focus-visible{outline:2px solid #00C9A7;outline-offset:4px;border-radius:12px}
@keyframes jpTapPulse{0%{box-shadow:0 3px 8px rgba(233,69,96,.35),0 0 0 0 rgba(233,69,96,.45)}70%,100%{box-shadow:0 3px 8px rgba(233,69,96,.35),0 0 0 10px rgba(233,69,96,0)}}
@media (prefers-reduced-motion:reduce){.jp-cat .paw,.jp-cat-tap{animation:none}}
@media (max-width:600px){.jp-cat{right:6px;top:-62px;width:64px}.jp-cat-tap{width:22px;height:22px;font-size:.66rem;left:-4px}.jp-ask{margin-top:4.6rem}}
.jp-hero .jp-ask{max-width:none;margin:6.4rem 0 0}
.jp-cat{z-index:3}
@media (max-width:600px){.jp-hero .jp-ask{margin-top:4.6rem}}
.jp-ask{position:relative;max-width:760px;margin:6.2rem auto 1.8rem;background:#fff;border:1.5px solid #BFEDE3;border-radius:18px;padding:14px 16px;box-shadow:0 2px 12px rgba(15,15,35,.05)}
.jp-ask-top{display:flex;align-items:center;gap:10px;margin:0 0 10px;font-size:.95rem;color:#0f0f23}.jp-ask-top>div{display:flex;flex-wrap:wrap;align-items:baseline;column-gap:8px}
.jp-ask-top b{font-weight:800}
.jp-ask-av{flex:none;width:40px;height:40px;background:#fff;border-radius:12px;padding:2px;box-shadow:0 2px 8px rgba(15,15,35,.12)}.jp-ask-av svg{width:100%;height:100%;display:block}
.jp-ask-sub{color:#5a6378;font-size:.85rem}
.jp-ask-kick{font-size:.68rem;font-weight:800;letter-spacing:.03em;background:#E94560;color:#fff;border-radius:999px;padding:2px 8px;align-self:center}
.jp-ask-form{display:flex;gap:8px;align-items:center;background:#F5F7F9;border:1.5px solid #E3E8EC;border-radius:14px;padding:4px 4px 4px 12px}
.jp-ask-form:focus-within{border-color:#00C9A7;background:#fff}
.jp-ask-form input{flex:1;min-width:0;font:inherit;font-size:1rem;border:0;background:transparent;padding:10px 0;color:#0f0f23;outline:none}
.jp-ask-form button{flex:none;font:inherit;font-weight:800;font-size:.95rem;background:linear-gradient(135deg,#E94560,#ff6b85);color:#fff;border:0;border-radius:999px;padding:0 18px;min-height:42px;cursor:pointer;box-shadow:0 4px 12px rgba(233,69,96,.3)}
.jp-ask-form button[disabled]{opacity:.6;cursor:wait}
.jp-ask-try{display:flex;gap:6px;overflow-x:auto;-webkit-overflow-scrolling:touch;margin:8px 0 0;padding:2px 0;scrollbar-width:none}
.jp-ask-try::-webkit-scrollbar{display:none}
@media (min-width:601px){.jp-ask-try{flex-wrap:wrap;overflow:visible}}
.jp-ask-try button{flex:none;font:inherit;font-size:.82rem;font-weight:600;background:#fff;color:#0f0f23;border:1.5px solid #BFEDE3;border-radius:999px;padding:5px 11px;min-height:32px;cursor:pointer;white-space:nowrap}
.jp-ask-try button:hover{border-color:#00C9A7}
.jp-ask-hint{font-size:.82rem;color:#5a6378;margin:8px 0 0}.jp-ask-hint b{color:#0a8f78}
.jp-ask-cont{font:inherit;font-size:.85rem;font-weight:700;color:#0a8f78;background:none;border:0;padding:0;text-decoration:underline;cursor:pointer}
.jp-ask-out{margin-top:10px;background:#F8FBFA;border-radius:12px;padding:10px 12px;line-height:1.55;font-size:.95rem;color:#0f0f23}
.jp-ask-out p{margin:.25rem 0}.jp-ask-out ul{margin:.25rem 0 .25rem 1.1rem;padding:0}.jp-ask-out li{margin:.15rem 0}
.jp-ask-out a{color:#0a8f78;font-weight:700}
.jp-ask-out.busy{color:#5a6378}.jp-ask-out.err{background:#fff3f5}
.jp-ask-q{margin:0 0 .6rem auto!important;max-width:85%;width:fit-content;background:#0f0f23;color:#fff;border-radius:14px 14px 4px 14px;padding:8px 12px;font-size:.9rem}.jp-ask-q span,.jp-ask-by{display:block;font-size:.7rem;font-weight:800;letter-spacing:.05em;text-transform:uppercase;opacity:.7;margin-bottom:2px}.jp-ask-by{color:#0a8f78;opacity:1}
.jp-ask-more{border-top:1px solid #E3E8EC;padding-top:.5rem;margin-top:.5rem!important;font-size:.9rem}
.jp-ask-note{font-size:.76rem;color:#8a93a6;margin:8px 0 0;line-height:1.45}.jp-ask-note a{color:#8a93a6}
.jp-sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
@media (max-width:600px){.jp-ask{padding:12px;border-radius:16px}.jp-ask-form button{padding:0 14px}}
</style>
"""
head = head + HUB_CSS

# ---- nav (as on Travel Essentials) and the Pocket Guide block
nav = te[te.index("</head>"):te.index('<div class="page-wrapper">')]
pm = re.search(r'<section class="pocket-hub" id="pocket-hub".*?</section>', te, re.S)
if not pm:
    die("Pocket Guide block not found on Travel Essentials")
pocket = pm.group(0).replace("?src=hub\"", "?src=hub_japan\"")
if "?src=hub_japan" not in pocket:
    die("Pocket Guide links not retagged")
foot = te[te.index('<footer class="footer">'):]

plan_cards = "\n".join(card(blog, s, "blog.html") for s in PLAN)
arrive_cards = "\n".join(card(te, s, "travel-essentials.html") for s in ARRIVE)
station_cards = "\n".join(card(te, s, "travel-essentials.html") for s in STATIONS)


def section(sid, title, lead, cards):
    return ('    <section class="te-section" id="%s">\n        <h2 class="te-h">%s</h2>\n        <p class="te-sub">%s</p>\n'
            '        <div class="blog-grid">\n%s\n        </div>\n    </section>\n') % (sid, title, lead, cards)


def links(title, lead, items):
    return ('<div class="jp-links"><h2>%s</h2><p>%s</p><ul>%s</ul></div>' % (
        title, lead, "".join('<li><a href="%s"><span aria-hidden="true">%s</span><span>%s<small>%s</small></span></a></li>' % i for i in items)))


HOKKAIDO = links("Hokkaido this winter", "Snow, ski buses and day trips from Sapporo.", [
    ("/blog/sapporo-station-guide#snow-festival", "&#10052;&#65039;", "Sapporo Snow Festival 2027", "4 to 11 February 2027: the sites and how to get there"),
    ("/blog/new-chitose-airport-guide#ski", "&#9975;&#65039;", "Ski buses from the airport", "Niseko ski bus times and how to book"),
    ("/blog/sapporo-station-guide#day-trips", "&#127956;&#65039;", "Day trips from Sapporo by train", "Otaru, Noboribetsu, Asahikawa, Biei and Furano"),
    ("/blog/sapporo-station-guide#hotels", "&#127976;", "Staying by Sapporo Station", "Hotels at or near the station"),
])
SEASONS = links("By season", "When you go changes what you pack and what you book.", [
    ("/blog/japan-travel-packing-guide#best-time", "&#128197;", "Best time to visit Japan", "Season by season"),
    ("/blog/ueno-station-guide#park", "&#127800;", "Cherry blossoms at Ueno Park", "One of Tokyo's best-known spots, next to the station"),
    ("/blog/japan-travel-packing-guide#packing-by-season", "&#129523;", "What to pack by season", "Winter layers to summer heat"),
    ("/blog/japan-travel-packing-guide#jr-pass", "&#128645;", "Is a JR Pass worth it?", "How to decide"),
])

# ---- "Going somewhere else?" row: every other country on /blog, plus the regions without a country bar
_ctys = re.findall(r'<button type="button" class="cty-btn" data-country="([a-z-]+)" data-reg="([A-Za-z ]+)">([^<]+)</button>', blog)
if len(_ctys) < 10:
    die("country buttons not found on blog.html")

# ---- Packy, "Ask about Japan" (answers from /api/ask, which uses only official-source notes; see api/ask.js and w74)
def packy_face():
    js = open(os.path.join(ROOT, "public", "packy.js"), encoding="utf-8").read()
    m = re.search(r"var FACE = ((?:'[^']*'\s*\+?\s*)+);", js)
    if not m:
        die("Packy's face (var FACE) not found in public/packy.js")
    return "".join(re.findall(r"'([^']*)'", m.group(1)))

ASK = """<!-- ask-japan-slot -->
<section class="jp-ask" id="ask" aria-label="Ask Packy, your Japan travel buddy">
<span class="jp-cat" id="jpCat" role="button" tabindex="0" aria-label="Lucky cat: tap to hear Konnichiwa"><span class="jp-cat-tap" aria-hidden="true">🔊</span><span class="jp-cat-say" role="status"><span lang="ja">こんにちは!</span> Konnichiwa! 👋<small>🔊 Tap me to hear it</small></span><svg viewBox="40 20 140 165" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false"><ellipse cx="100" cy="168" rx="52" ry="12" fill="#F2D7DC"/><rect x="52" y="96" width="96" height="74" rx="40" fill="#fff" stroke="#0f0f23" stroke-width="3"/><path d="M60 64l-6-34 30 20M140 64l6-34-30 20" fill="#fff" stroke="#0f0f23" stroke-width="3" stroke-linejoin="round"/><path d="M58 32l18 14M142 32l-18 14" stroke="#F49AB0" stroke-width="6" stroke-linecap="round"/><ellipse cx="100" cy="78" rx="50" ry="40" fill="#fff" stroke="#0f0f23" stroke-width="3"/><path d="M70 76q8-8 16 0M114 76q8-8 16 0" fill="none" stroke="#0f0f23" stroke-width="4" stroke-linecap="round"/><path d="M94 90q6 5 12 0" fill="none" stroke="#0f0f23" stroke-width="3" stroke-linecap="round"/><circle cx="100" cy="87" r="3" fill="#E94560"/><path d="M62 86h-18M62 92h-16M138 86h18M138 92h16" stroke="#0f0f23" stroke-width="2"/><circle cx="124" cy="42" r="10" fill="#E94560"/><circle cx="76" cy="46" r="7" fill="#26335c"/><path d="M60 118c30 10 50 10 80 0" stroke="#E94560" stroke-width="9" fill="none"/><circle cx="100" cy="132" r="9" fill="#F5C542" stroke="#0f0f23" stroke-width="2"/><ellipse cx="100" cy="152" rx="30" ry="12" fill="#F5C542" stroke="#0f0f23" stroke-width="2"/><text x="100" y="157" font-size="12" text-anchor="middle" font-weight="800" fill="#0f0f23">千万両</text><g class="paw"><path d="M146 112q22-10 18-46" stroke="#0f0f23" stroke-width="3" fill="#fff"/><ellipse cx="162" cy="62" rx="15" ry="17" fill="#fff" stroke="#0f0f23" stroke-width="3"/><path d="M156 56v8M162 54v10M168 56v8" stroke="#F49AB0" stroke-width="2" stroke-linecap="round"/></g></svg></span>
<div class="jp-ask-top"><span class="jp-ask-av" aria-hidden="true">%%FACE%%</span><div><b>Ask Packy</b><span class="jp-ask-sub">your Japan travel buddy</span></div><span class="jp-ask-kick">Beta</span></div>
<form class="jp-ask-form" id="askForm" autocomplete="off">
<label for="askQ" class="jp-sr">Your question about travel in Japan</label>
<input id="askQ" type="text" maxlength="300" placeholder="Ask Packy about Japan…">
<button type="submit" id="askBtn">Ask &#10148;</button>
</form>
<div class="jp-ask-try" role="group" aria-label="Example questions">
<button type="button" data-q="How do I get from Ueno to Narita Airport?">✈️ Ueno to Narita Airport</button>
<button type="button" data-q="How long is the Shinkansen from Tokyo to Osaka?">🚄 Tokyo to Osaka by Shinkansen</button>
<button type="button" data-q="How do I top up a Suica card?">💳 Top up a Suica card</button>
<button type="button" data-q="How do I get from New Chitose Airport to Sapporo?">✈️ New Chitose to Sapporo</button>
<button type="button" data-q="Is there a ski bus from New Chitose Airport to Niseko?">⛷️ Ski bus to Niseko</button>
</div>
<p class="jp-ask-hint" id="askHint">💬 <b>Opens a chat with Packy</b>: ask follow-ups, and get the whole chat by email if you like.</p>
<div class="jp-ask-out" id="askOut" aria-live="polite" hidden></div>
<p class="jp-ask-note">Answers come from official sources (JR, airports, bus companies, JNTO). Times change, so check before you travel. Please don't type personal details. <a href="/privacy-policy">Privacy</a></p>
</section>
<script>
(function(){
var f=document.getElementById('askForm'),q=document.getElementById('askQ'),b=document.getElementById('askBtn'),out=document.getElementById('askOut');
function esc(s){return s.replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
function fmt(t){
  var h=esc(t).replace(/\\*\\*([^*]+)\\*\\*/g,'<b>$1</b>').replace(/\\[([^\\]]+)\\]\\(((?:https?:\\/\\/|\\/)[^\\s)]+)\\)/g,function(m,x,u){var ext=/^https?:/.test(u);return '<a href="'+u+'"'+(ext?' target="_blank" rel="noopener"':'')+'>'+x+'</a>';});
  var lines=h.split(/\\n+/),html='',inList=false;
  lines.forEach(function(l){var m=l.match(/^\\s*[-*\\u2022]\\s+(.*)/);if(m){if(!inList){html+='<ul>';inList=true;}html+='<li>'+m[1]+'</li>';}else{if(inList){html+='</ul>';inList=false;}if(l.trim())html+='<p>'+l+'</p>';}});
  return html+(inList?'</ul>':'');
}
function track(s){try{if(window.gtag)gtag('event','ask_japan',{event_category:'engagement',status:s,page_path:location.pathname});}catch(e){}}
function ask(text){
  text=(text||'').trim(); if(text.length<5){q.focus();return;}
  if(window.Packy){window.Packy.ask(text);q.value='';return;}   // the shared Packy chat (packy.js) answers, with follow-up questions
  b.disabled=true; out.hidden=false; out.className='jp-ask-out busy'; out.innerHTML='<p>Checking the official sources&hellip;</p>';
  fetch('/api/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({q:text})})
   .then(function(r){return r.json().then(function(d){return [r.ok,d];});})
   .then(function(x){var ok=x[0],d=x[1];
     if(!ok||!d.ok){out.className='jp-ask-out err';out.innerHTML='<p>'+esc((d&&d.error)||'Sorry, something went wrong.')+'</p>';track('error');return;}
     out.className='jp-ask-out';
     out.innerHTML='<p class="jp-ask-q"><span>You asked</span>'+esc(text)+'</p><div class="jp-ask-a"><span class="jp-ask-by">Packy</span>'+fmt(d.answer)+'</div>'+(d.guide?'<p class="jp-ask-more">More in our <a href="'+esc(d.guide.url)+'">'+esc(d.guide.title)+'</a></p>':'');
     track('answered');})
   .catch(function(){out.className='jp-ask-out err';out.innerHTML='<p>No connection. Please try again when you are online.</p>';track('offline');})
   .then(function(){b.disabled=false;});
}
f.addEventListener('submit',function(e){e.preventDefault();ask(q.value);});
[].forEach.call(document.querySelectorAll('.jp-ask-try button'),function(btn){btn.addEventListener('click',function(){var t=btn.getAttribute('data-q');q.value=t;ask(t);});});
// a chat already going in this visit: offer to carry on (packy.js loads after this box, so check once the page is ready)
window.addEventListener('load',function(){var n=window.Packy&&window.Packy.count?window.Packy.count():0,h=document.getElementById('askHint');
  if(n&&h){h.innerHTML='💬 <button type="button" class="jp-ask-cont">Continue your chat with Packy ('+n+(n>1?' questions':' question')+')</button>';h.querySelector('button').addEventListener('click',function(){window.Packy.open();});}});
})();
</script>"""
ASK = ASK.replace("%%FACE%%", packy_face())

# ---- Arrival hero (25 Nov 2026): photo, Packy's hello, a live strip (Japan time, weather, season) and an arrivals board
# whose rows are fastest official journey times (sources in docs/research: Keisei, Keikyu, JNTO, Kyoto City, checked
# 24 Nov 2026). Then "Where are you landing?" boarding passes for the four airports with Pocket Guides.
BOARD_CHECKED = datetime.date(2026, 11, 24)   # when the board and boarding-pass facts were last checked against the sources
if (datetime.date.today() - BOARD_CHECKED).days > 183:
    print("w73 WARNING: the arrivals board and boarding passes were last checked on %s, over 6 months ago. Re-check the "
          "times in docs/research (Keisei, Keikyu, JNTO, Kyoto City), update BOARD and PASSES, then BOARD_CHECKED." % BOARD_CHECKED)
BOARD = [  # from, to, by, time, pocket key, source
    ("NARITA", "UENO", "SKYLINER", "41 MIN", "narita", "Keisei"),
    ("HANEDA", "SHINAGAWA", "KEIKYU", "11 MIN", "haneda", "Keikyu, from Terminal 3"),
    ("NEW CHITOSE", "SAPPORO", "JR RAPID", "~40 MIN", "new-chitose", "JNTO"),
    ("KANSAI", "KYOTO", "HARUKA", "~80 MIN", "kix", "Kyoto City"),
    ("TOKYO", "SHIN-OSAKA", "SHINKANSEN", "~2H30", "tokyo", "JNTO"),
]
PASSES = [  # code, name, serves, line, pocket key, guide slug, Packy question
    ("NRT", "Narita Airport", "Tokyo", "Most international flights to Tokyo. Skyliner to Ueno in 41 minutes.", "narita", "narita-airport-guide", "How do I get from Narita Airport to Tokyo?"),
    ("HND", "Haneda Airport", "Tokyo", "The closest airport to central Tokyo, about 30 minutes by train.", "haneda", "haneda-airport-guide", "How do I get from Haneda Airport to central Tokyo?"),
    ("KIX", "Kansai Airport", "Osaka and Kyoto", "Central Osaka in just over 30 minutes by rapid train.", "kix", "kansai-airport-guide", "How do I get from Kansai Airport to Kyoto?"),
    ("CTS", "New Chitose Airport", "Sapporo and Hokkaido", "JR to Sapporo in under 40 minutes; gateway to the ski areas.", "new-chitose", "new-chitose-airport-guide", "How do I get from New Chitose Airport to Sapporo?"),
]

HERO_CSS = """
.jp-hero{position:relative;margin:0 0 1.8rem;color:#0f0f23}
.jp-hero-in{position:relative;padding:.4rem 0 0}
.jp-hero-top{display:grid;grid-template-columns:minmax(0,1.25fr) minmax(0,.75fr);gap:1rem;align-items:stretch}
.jp-scene{position:relative;min-height:280px;pointer-events:none}
/* "Fuji through the seasons": a small switcher on the scene (starts on the current season) */
.jp-seasons{position:absolute;left:50%;top:calc(100% + 10px);transform:translateX(-50%);pointer-events:auto;white-space:nowrap;display:flex;align-items:center;gap:12px}
.jp-seasons small{display:block;font-size:.66rem;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:#0a8f78;margin:0;text-align:right;line-height:1.35;white-space:normal;width:150px}
.jp-seasons small i{font-style:normal;color:#E94560;display:inline-block;animation:jpNudge 1.8s ease-in-out infinite}
@keyframes jpNudge{0%,60%,100%{transform:none}30%{transform:translateX(4px)}}
@media (prefers-reduced-motion:reduce){.jp-seasons small i{animation:none}}
@media (min-width:901px){.jp-seasons small{font-size:.72rem;width:170px}}
.jp-seasons-row{display:inline-flex;align-items:center;gap:4px;background:rgba(255,255,255,.92);border:1px solid #BFEDE3;border-radius:999px;padding:3px;box-shadow:0 6px 16px rgba(0,168,140,.12)}
.jp-seasons button{width:30px;height:30px;border:0;border-radius:50%;background:#E6FAF5;color:#0a8f78;font-size:1.25rem;line-height:1;font-weight:800;cursor:pointer}
.jp-seasons button:hover{background:#00C9A7;color:#fff}
.jp-s-lbl{min-width:104px;font-size:.88rem;color:#0f0f23}.jp-s-lbl span{color:#E94560;margin-right:5px}
.jp-scene .fuji,.jp-scene .ss{transition:opacity .35s}
.jp-hero-top .jp-scene{margin-bottom:64px}
@media (min-width:601px) and (max-width:900px){.jp-seasons{gap:8px}.jp-seasons small{width:112px;font-size:.62rem}}
.jp-hero-top .jp-scene{margin-bottom:56px}
@media (max-width:600px){.jp-hero-top .jp-scene{margin-bottom:46px}.jp-seasons{top:calc(100% + 6px)}.jp-seasons small{display:none}}
.jp-scene .fuji{position:absolute;inset:0;width:100%;height:100%;display:block;will-change:transform;-webkit-mask-image:linear-gradient(90deg,transparent 0,#000 14%,#000 86%,transparent 100%);mask-image:linear-gradient(90deg,transparent 0,#000 14%,#000 86%,transparent 100%)}
.jp-scene .cl{animation:jpDrift 26s ease-in-out infinite alternate}
.jp-scene .ss{display:none}
.jp-scene[data-season=spring] .ss-spring,.jp-scene[data-season=summer] .ss-summer,.jp-scene[data-season=autumn] .ss-autumn,.jp-scene[data-season=winter] .ss-winter{display:inline}
.jp-scene .sky0{stop-color:#8FCBEF}.jp-scene .sky1{stop-color:#BFE2F6}.jp-scene .mt0{stop-color:#4A5F8E}.jp-scene .mt1{stop-color:#7488B3}.jp-scene .mt2{stop-color:#9FB0CF}
.jp-scene .fo1{fill:#3F6E67}.jp-scene .fo2{fill:#5C918A}
.jp-scene[data-season=summer] .sky0{stop-color:#5DB6EE}.jp-scene[data-season=summer] .sky1{stop-color:#A6DAF7}
.jp-scene[data-season=summer] .mt0{stop-color:#3E4F7C}.jp-scene[data-season=summer] .mt1{stop-color:#5C7096}.jp-scene[data-season=summer] .mt2{stop-color:#7F95A8}
.jp-scene[data-season=summer] .fo1{fill:#2F7A4F}.jp-scene[data-season=summer] .fo2{fill:#55A56B}
.jp-scene[data-season=autumn] .sky0{stop-color:#93C6E8}.jp-scene[data-season=autumn] .sky1{stop-color:#F6D9C2}
.jp-scene[data-season=autumn] .fo1{fill:#A83A27}.jp-scene[data-season=autumn] .fo2{fill:#D9762F}
.jp-scene[data-season=winter] .sky0{stop-color:#B6D6EC}.jp-scene[data-season=winter] .sky1{stop-color:#DCEBF5}
.jp-scene[data-season=winter] .mt0{stop-color:#5E7196}.jp-scene[data-season=winter] .mt1{stop-color:#8C9DBE}.jp-scene[data-season=winter] .mt2{stop-color:#C3CEE2}
.jp-scene[data-season=winter] .fo1{fill:#5E7E86}.jp-scene[data-season=winter] .fo2{fill:#A9BFC5}
body[data-season=summer] .jp-petal{top:auto;bottom:-20px;width:7px;height:7px;border-radius:50%;background:#FFF6A0;box-shadow:0 0 10px 4px rgba(240,236,120,.75);animation-name:jpFly}
body[data-season=summer] .jp-petal svg{display:none}
.jp-scene .ff{animation:jpFF 7s ease-in-out infinite;transform-box:fill-box}
@keyframes jpFF{0%,100%{transform:translate(0,0);opacity:.25}30%{opacity:1}50%{transform:translate(10px,-14px);opacity:.5}75%{opacity:1}}
@keyframes jpFly{0%{transform:translate(0,0);opacity:0}15%{opacity:1}35%{opacity:.35}55%{transform:translate(28px,-50vh);opacity:1}75%{opacity:.4}100%{transform:translate(-12px,-100vh);opacity:0}}
body[data-season=autumn] .jp-petal path{fill:#E8743B;stroke:#C2501F}
body[data-season=winter] .jp-petal path{fill:#fff;stroke:#D6E2EC}
body[data-season=winter] .jp-petal svg{transform:scale(.7)}
@keyframes jpDrift{from{transform:translateX(-14px)}to{transform:translateX(18px)}}
.jp-scene .sk{display:none;position:absolute;left:-30px;top:-40px;width:130px;transform:rotate(-8deg)}.jp-scene .sk svg{width:100%;height:auto;display:block}
.jp-hero-kick{display:inline-flex;align-items:center;gap:8px;font-size:.8rem;font-weight:800;letter-spacing:.12em;text-transform:uppercase;background:#fff;color:#0a8f78;border:1px solid #BFEDE3;border-radius:999px;padding:5px 12px}
.jp-hero h1{font-family:var(--font-display);font-size:3.6rem;line-height:1.02;margin:.6rem 0 .5rem;color:#0f0f23}
.jp-hero h1 em{font-style:italic;color:#E94560}
.jp-hero-lead{font-size:1.08rem;max-width:600px;color:#3f4a5c;margin:0 0 1rem}
.jp-hello{display:flex;align-items:center;gap:10px;background:none;border:0;padding:0;color:#0f0f23;font:inherit;cursor:pointer;text-align:left;margin:0 0 1.1rem}
.jp-hello .av{flex:none;width:48px;height:48px;background:#fff;border-radius:14px;padding:3px;box-shadow:0 6px 18px rgba(233,69,96,.2)}.jp-hello .av svg{width:100%;height:100%;display:block}
.jp-hello .bub{background:#fff;color:#0f0f23;border-radius:16px 16px 16px 4px;padding:9px 14px;font-weight:600;font-size:.95rem;box-shadow:0 6px 18px rgba(233,69,96,.15)}
.jp-hello .bub b{color:#E94560}
.jp-live{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 1.2rem}
.jp-live span{display:inline-flex;align-items:center;gap:6px;font-size:.86rem;font-weight:700;background:#fff;color:#0f0f23;border:1px solid #BFEDE3;border-radius:999px;padding:6px 12px}
.jp-live span[hidden]{display:none}
/* phones: fewer words above the Ask box, so the eye goes to it (owner, 26 Nov). The greeting bubble repeats the Ask
   box right below it, and the season already shows on the Fuji switcher. */
@media (max-width:600px){.jp-hello,#jpSeason{display:none!important}.jp-ask-sub{display:none}.jp-ask-hint{font-size:.74rem}.jp-ask-note{font-size:.68rem;line-height:1.4}}
@media (max-width:600px){.jp-live{gap:6px}.jp-live span{font-size:.74rem;font-weight:600;padding:4px 10px;gap:4px}}
.jp-board{background:rgba(255,255,255,.9);border:1px solid #BFEDE3;border-radius:18px;padding:12px 12px 8px;box-shadow:0 14px 34px rgba(0,168,140,.12);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px)}
.jp-board-h{display:flex;align-items:center;justify-content:space-between;color:#0a8f78;font-weight:800;letter-spacing:.14em;font-size:.78rem;padding:2px 4px 8px}
.jp-board-h i{font-style:normal;color:#8a93a6;letter-spacing:.04em;font-weight:600}
.jp-board ol{list-style:none;margin:0;padding:0;display:grid;gap:6px}
.jp-board a{display:grid;grid-template-columns:1.2fr 1.2fr 1fr .8fr 18px;align-items:center;gap:8px;text-decoration:none;color:#0f0f23;background:#F7FCFB;border:1px solid #E1F2EE;border-radius:12px;padding:9px 12px;transition:background .15s,border-color .15s}
.jp-board a:hover,.jp-board a:focus-visible{background:#fff;border-color:#00C9A7}
.jp-board .f{position:relative;font-weight:800;font-size:.92rem;letter-spacing:.06em;font-variant-numeric:tabular-nums;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.jp-board .f.by{color:#5a6378}
.jp-board .f.t{justify-self:end;color:#C2185B;background:#FFE3E8;border-radius:999px;padding:3px 10px}
.jp-board .go{color:#00A88C;font-weight:800}
.jp-board-note{font-size:.72rem;color:#5a6378;margin:8px 4px 2px;line-height:1.4}
.jp-pass-h{text-align:center;margin:0 0 1rem}.jp-pass-h h2{font-family:var(--font-display);font-size:2.2rem;margin:0}.jp-pass-h p{color:#5a6378;margin:.2rem 0 0}
.jp-passes{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;margin:0 0 2rem}
.jp-pass{position:relative;display:flex;background:#fff;border-radius:18px;box-shadow:0 6px 20px rgba(15,15,35,.08);overflow:hidden;border:1px solid #E6ECEF}
.jp-pass-main{flex:1;min-width:0;padding:14px 16px}
.jp-pass-top{display:flex;align-items:center;justify-content:space-between;font-size:.7rem;font-weight:800;letter-spacing:.12em;color:#8a93a6;text-transform:uppercase}
.jp-pass-code{font-size:2.6rem;font-weight:800;letter-spacing:.02em;line-height:1;color:#0f0f23;margin:.35rem 0 .1rem}
.jp-pass-code small{font-size:.9rem;color:#E94560;margin-left:6px;letter-spacing:.02em;vertical-align:middle}
.jp-pass-name{font-weight:800;color:#0f0f23}.jp-pass-serves{color:#5a6378;font-size:.86rem}
.jp-pass-line{font-size:.86rem;color:#3f4a5c;margin:.45rem 0 .6rem;line-height:1.45}
.jp-pass-ask{font:inherit;font-size:.82rem;font-weight:700;color:#0a8f78;background:#E6FAF5;border:0;border-radius:999px;padding:6px 11px;cursor:pointer}
.jp-pass-stub{flex:none;width:118px;display:flex;flex-direction:column;justify-content:center;gap:8px;padding:12px 12px 12px 16px;background:linear-gradient(135deg,#00C9A7,#00A88C);color:#fff;border-left:2px dashed rgba(255,255,255,.7);position:relative}
.jp-pass-stub:before,.jp-pass-stub:after{content:"";position:absolute;left:-9px;width:16px;height:16px;border-radius:50%;background:var(--bg,#FDF0F2)}
.jp-pass-stub:before{top:-8px}.jp-pass-stub:after{bottom:-8px}
.jp-pass-stub small{font-size:.66rem;font-weight:800;letter-spacing:.12em;opacity:.85}
.jp-pass-stub a{display:block;text-align:center;background:#0f0f23;color:#fff;text-decoration:none;font-weight:800;font-size:.8rem;border-radius:10px;padding:8px 6px;line-height:1.2}
.jp-pass-stub a.g{background:rgba(255,255,255,.18)}
.jp-stamp{position:absolute;right:130px;top:12px;transform:rotate(-12deg);border:2px solid #E94560;color:#E94560;border-radius:8px;padding:2px 6px;font-size:.62rem;font-weight:800;letter-spacing:.08em;opacity:.85;text-align:center;line-height:1.15}
@media (max-width:760px){.jp-passes{grid-template-columns:1fr}}
/* phones: smaller airport cards so more of them show per screen */
@media (max-width:600px){.jp-pass-h h2{font-size:1.6rem}.jp-pass-h p{font-size:.84rem;line-height:1.45}.jp-pass-main{padding:11px 13px}.jp-pass-top{font-size:.62rem}.jp-pass-code{margin:.25rem 0 .05rem}.jp-pass-name{font-size:.95rem}.jp-pass-serves{font-size:.78rem}.jp-pass-line{font-size:.8rem;margin:.3rem 0 .5rem;line-height:1.4}.jp-pass-ask{font-size:.76rem;padding:5px 10px}.jp-pass-stub{padding-top:10px;padding-bottom:10px;gap:6px}.jp-pass-stub a{font-size:.74rem;padding:7px 4px}}
@media (max-width:600px){
 .jp-hero-top{grid-template-columns:1fr}.jp-scene{order:-1;min-height:0;height:170px;margin:0 -4px;overflow:visible}
 .jp-scene .sk{width:86px!important;left:-18px!important;top:-26px!important}
 .jp-scene .sk{display:block}.jp-hero h1{font-size:2.2rem}.jp-hero-lead{font-size:.9rem;line-height:1.5;margin-bottom:.8rem}
 .jp-board a{grid-template-columns:1fr auto;grid-template-areas:"r t" "b t";row-gap:2px}
 .jp-board .f.fr{grid-area:r;white-space:normal}.jp-board .f.fr:after{content:" → " attr(data-to);color:#0f0f23}
 .jp-board .f.to{display:none}.jp-board .f.by{grid-area:b;font-size:.74rem;color:#5a6378}.jp-board .f.t{grid-area:t;font-size:1rem}.jp-board .go{display:none}
 .jp-board-h .wide{display:none}
 .jp-pass-code{font-size:1.9rem}.jp-pass-stub{width:94px;padding-left:13px;padding-right:10px}.jp-stamp{right:104px}
}
@media (prefers-reduced-motion:reduce){.jp-board .f{transition:none}}
"""

# Drawn dawn scene for the hero (25 Nov 2026, owner chose it over photos): sky, rising sun, Mt Fuji, pink hills, torii.
FUJI_SVG = ('<svg class="fuji" viewBox="0 0 600 400" preserveAspectRatio="xMidYMax meet" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false"><defs>'
    '<radialGradient id="fjSky" cx=".5" cy=".5" r=".5"><stop offset="0" class="sky0"/><stop offset=".45" class="sky1" stop-opacity=".8"/><stop offset=".78" class="sky1" stop-opacity=".28"/><stop offset="1" class="sky1" stop-opacity="0"/></radialGradient>'
    '<linearGradient id="fjB" x1="0" y1="0" x2="0" y2="1"><stop offset="0" class="mt0"/><stop offset=".55" class="mt1"/><stop offset="1" class="mt2"/></linearGradient>'
    '<linearGradient id="fjS" x1="0" y1="0" x2="1" y2="0"><stop offset=".3" stop-color="#fff"/><stop offset="1" stop-color="#D3DEEE"/></linearGradient>'
    '<radialGradient id="ffG"><stop offset="0" stop-color="#FFF6A0" stop-opacity=".95"/><stop offset="1" stop-color="#E8F27A" stop-opacity="0"/></radialGradient><linearGradient id="fjL" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#A9D8F0"/><stop offset="1" stop-color="#D9EEF8"/></linearGradient>'
    '<linearGradient id="fjM" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FDF0F2" stop-opacity="0"/><stop offset="1" stop-color="#FDF0F2" stop-opacity=".95"/></linearGradient></defs>'
    '<ellipse cx="300" cy="200" rx="300" ry="200" fill="url(#fjSky)"/>'
    '<g class="ss ss-summer"><g transform="translate(70 34)"><path d="M0 0v8" stroke="#3a2a2a" stroke-width="1.5"/><rect x="-8" y="8" width="16" height="4" rx="1" fill="#3a2a2a"/><ellipse cx="0" cy="22" rx="11" ry="12" fill="#E94560"/><path d="M-10 18h20M-10 26h20" stroke="#fff" stroke-width="1" opacity=".5"/><rect x="-8" y="32" width="16" height="4" rx="1" fill="#3a2a2a"/></g><g transform="translate(150 44)"><path d="M0 0v8" stroke="#3a2a2a" stroke-width="1.5"/><rect x="-8" y="8" width="16" height="4" rx="1" fill="#3a2a2a"/><ellipse cx="0" cy="22" rx="11" ry="12" fill="#F2994A"/><path d="M-10 18h20M-10 26h20" stroke="#fff" stroke-width="1" opacity=".5"/><rect x="-8" y="32" width="16" height="4" rx="1" fill="#3a2a2a"/></g><g transform="translate(230 50)"><path d="M0 0v8" stroke="#3a2a2a" stroke-width="1.5"/><rect x="-8" y="8" width="16" height="4" rx="1" fill="#3a2a2a"/><ellipse cx="0" cy="22" rx="11" ry="12" fill="#E94560"/><path d="M-10 18h20M-10 26h20" stroke="#fff" stroke-width="1" opacity=".5"/><rect x="-8" y="32" width="16" height="4" rx="1" fill="#3a2a2a"/></g><g transform="translate(310 52)"><path d="M0 0v8" stroke="#3a2a2a" stroke-width="1.5"/><rect x="-8" y="8" width="16" height="4" rx="1" fill="#3a2a2a"/><ellipse cx="0" cy="22" rx="11" ry="12" fill="#F2994A"/><path d="M-10 18h20M-10 26h20" stroke="#fff" stroke-width="1" opacity=".5"/><rect x="-8" y="32" width="16" height="4" rx="1" fill="#3a2a2a"/></g><g transform="translate(390 50)"><path d="M0 0v8" stroke="#3a2a2a" stroke-width="1.5"/><rect x="-8" y="8" width="16" height="4" rx="1" fill="#3a2a2a"/><ellipse cx="0" cy="22" rx="11" ry="12" fill="#E94560"/><path d="M-10 18h20M-10 26h20" stroke="#fff" stroke-width="1" opacity=".5"/><rect x="-8" y="32" width="16" height="4" rx="1" fill="#3a2a2a"/></g><g transform="translate(470 44)"><path d="M0 0v8" stroke="#3a2a2a" stroke-width="1.5"/><rect x="-8" y="8" width="16" height="4" rx="1" fill="#3a2a2a"/><ellipse cx="0" cy="22" rx="11" ry="12" fill="#F2994A"/><path d="M-10 18h20M-10 26h20" stroke="#fff" stroke-width="1" opacity=".5"/><rect x="-8" y="32" width="16" height="4" rx="1" fill="#3a2a2a"/></g><g transform="translate(540 36)"><path d="M0 0v8" stroke="#3a2a2a" stroke-width="1.5"/><rect x="-8" y="8" width="16" height="4" rx="1" fill="#3a2a2a"/><ellipse cx="0" cy="22" rx="11" ry="12" fill="#E94560"/><path d="M-10 18h20M-10 26h20" stroke="#fff" stroke-width="1" opacity=".5"/><rect x="-8" y="32" width="16" height="4" rx="1" fill="#3a2a2a"/></g><path d="M30 30Q300 70 570 32" fill="none" stroke="#3a2a2a" stroke-width="1.4"/></g>'
    '<g class="ss ss-winter" opacity=".9"><circle cx="60" cy="60" r="2.5" fill="#fff"/><circle cx="140" cy="120" r="2" fill="#fff"/><circle cx="220" cy="40" r="3" fill="#fff"/><circle cx="420" cy="90" r="2.5" fill="#fff"/><circle cx="520" cy="140" r="2" fill="#fff"/><circle cx="560" cy="60" r="3" fill="#fff"/><circle cx="90" cy="250" r="2" fill="#fff"/><circle cx="470" cy="230" r="2.5" fill="#fff"/><circle cx="30" cy="170" r="2" fill="#fff"/><circle cx="380" cy="30" r="2" fill="#fff"/></g>'
    '<g class="mt">'
    '<path d="M20 352C128 300 210 214 260 130Q268 118 282 116L318 116Q332 118 340 130C390 214 472 300 580 352Z" fill="url(#fjB)"/>'
    '<path d="M20 352C128 300 210 214 260 130Q268 118 282 116L292 116C268 190 214 286 150 352Z" fill="#fff" opacity=".1"/>'
    '<path d="M308 116L318 116Q332 118 340 130C390 214 472 300 580 352L340 352C338 268 326 186 308 116Z" fill="#2E3B5A" opacity=".2"/>'
    '<path d="M286 140L238 300M300 150L292 330M316 146L346 320M332 140L410 300M272 150L180 320" stroke="#2E3B5A" stroke-width="1.4" opacity=".14" stroke-linecap="round"/>'
    '<path class="ss ss-winter" d="M260 130Q268 118 282 116L318 116Q332 118 340 130C372 186 404 236 440 282C430 278 424 296 414 286C406 300 398 304 390 290C380 306 370 300 364 286C354 304 342 300 336 282C326 300 312 302 304 284C294 302 282 300 276 282C266 298 254 296 248 278C238 292 226 290 222 272C212 282 200 280 196 266C186 272 176 270 172 262C206 218 236 170 260 130Z" fill="url(#fjS)"/>'
    '<path class="ss ss-spring" d="M260 130Q268 118 282 116L318 116Q332 118 340 130C352 152 364 172 376 194C369 191 365 208 357 201C351 217 345 227 337 209C331 230 323 238 315 216C309 240 301 246 295 219C288 238 280 233 273 212C267 227 260 222 255 202C248 209 241 202 236 192C232 195 229 196 226 196C238 172 250 152 260 130Z" fill="url(#fjS)"/>'
    '<path class="ss ss-autumn" d="M260 130Q268 118 282 116L318 116Q332 118 340 130C346 141 352 151 358 162C352 160 348 172 341 166C336 178 330 182 324 170C318 184 310 186 304 172C297 186 289 184 284 170C278 182 270 180 266 168C259 174 252 168 248 160C252 150 256 140 260 130Z" fill="url(#fjS)"/>'
    '<path class="ss ss-summer" d="M282 120L280 150M300 118L300 160M318 120L322 146M292 122L288 140M310 120L313 136" stroke="#fff" stroke-width="3" stroke-linecap="round" opacity=".75"/>'
    '<path class="ss ss-spring ss-winter" d="M298 232L296 262M322 228L326 254M280 226L275 248M342 218L349 240M258 216L252 234" stroke="#fff" stroke-width="2" stroke-linecap="round" opacity=".5"/>'
    '<path d="M286 117l5 4 6-3 6 3 5-4" fill="none" stroke="#C9D3E4" stroke-width="1.4"/>'
    '<path class="fo1" d="M0 360C40 346 70 352 96 340S150 344 178 334 226 342 256 330 304 340 334 330 388 342 418 332 470 344 504 334 560 344 600 338V372H0Z"/>'
    '<path class="ss ss-winter" d="M0 360C40 346 70 352 96 340S150 344 178 334 226 342 256 330 304 340 334 330 388 342 418 332 470 344 504 334 560 344 600 338" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round" opacity=".9"/>'
    '<path class="fo2" d="M0 368C50 356 90 362 128 352S200 360 240 350 320 360 360 352 440 362 480 354 560 362 600 356V376H0Z"/>'
    '<g class="ss ss-spring"><circle cx="40" cy="338" r="16" fill="#F7B6C8"/><circle cx="62" cy="330" r="18" fill="#FFCCD8"/><circle cx="84" cy="338" r="15" fill="#F49AB0"/><circle cx="54" cy="346" r="14" fill="#F7B6C8"/><circle cx="108" cy="334" r="13" fill="#FFCCD8"/><circle cx="124" cy="342" r="12" fill="#F49AB0"/><circle cx="470" cy="336" r="15" fill="#F7B6C8"/><circle cx="492" cy="328" r="17" fill="#FFCCD8"/><circle cx="514" cy="336" r="14" fill="#F49AB0"/><circle cx="536" cy="330" r="13" fill="#F7B6C8"/><circle cx="556" cy="338" r="12" fill="#FFCCD8"/></g>'
    '<g class="ss ss-autumn"><circle cx="40" cy="338" r="16" fill="#D9482B"/><circle cx="62" cy="330" r="18" fill="#F08A3C"/><circle cx="84" cy="338" r="15" fill="#E8613A"/><circle cx="54" cy="346" r="14" fill="#C2361F"/><circle cx="108" cy="334" r="13" fill="#D9482B"/><circle cx="124" cy="342" r="12" fill="#F08A3C"/><circle cx="500" cy="336" r="15" fill="#E8613A"/><circle cx="522" cy="328" r="17" fill="#C2361F"/><circle cx="544" cy="336" r="14" fill="#D9482B"/><circle cx="566" cy="332" r="13" fill="#F08A3C"/></g>'
    '<rect y="372" width="600" height="28" fill="url(#fjL)"/>'
    '<path d="M150 380h70M260 386h90M400 381h60M90 392h50M330 394h70" stroke="#fff" stroke-width="1.5" opacity=".7" stroke-linecap="round"/>'
    '<rect y="330" width="600" height="70" fill="url(#fjM)" opacity=".55"/></g>'
    '<g class="cl" fill="#fff"><g opacity=".95"><ellipse cx="110" cy="200" rx="62" ry="13"/><ellipse cx="138" cy="190" rx="34" ry="15"/><ellipse cx="92" cy="194" rx="24" ry="11"/></g>'
    '<g opacity=".9"><ellipse cx="486" cy="168" rx="54" ry="11"/><ellipse cx="508" cy="160" rx="28" ry="12"/></g></g>'
    '<g class="ss ss-summer"><g class="ff" style="animation-delay:-0s"><circle cx="70" cy="330" r="8" fill="url(#ffG)"/><circle cx="70" cy="330" r="1.8" fill="#FFF7B0"/></g><g class="ff" style="animation-delay:-2.1s"><circle cx="150" cy="300" r="8" fill="url(#ffG)"/><circle cx="150" cy="300" r="1.8" fill="#FFF7B0"/></g><g class="ff" style="animation-delay:-4.3s"><circle cx="210" cy="350" r="8" fill="url(#ffG)"/><circle cx="210" cy="350" r="1.8" fill="#FFF7B0"/></g><g class="ff" style="animation-delay:-1.2s"><circle cx="390" cy="320" r="8" fill="url(#ffG)"/><circle cx="390" cy="320" r="1.8" fill="#FFF7B0"/></g><g class="ff" style="animation-delay:-3.4s"><circle cx="455" cy="352" r="8" fill="url(#ffG)"/><circle cx="455" cy="352" r="1.8" fill="#FFF7B0"/></g><g class="ff" style="animation-delay:-5.6s"><circle cx="540" cy="306" r="8" fill="url(#ffG)"/><circle cx="540" cy="306" r="1.8" fill="#FFF7B0"/></g><g class="ff" style="animation-delay:-2.8s"><circle cx="110" cy="250" r="8" fill="url(#ffG)"/><circle cx="110" cy="250" r="1.8" fill="#FFF7B0"/></g><g class="ff" style="animation-delay:-4.9s"><circle cx="500" cy="250" r="8" fill="url(#ffG)"/><circle cx="500" cy="250" r="1.8" fill="#FFF7B0"/></g><g class="ff" style="animation-delay:-1.7s"><circle cx="300" cy="360" r="8" fill="url(#ffG)"/><circle cx="300" cy="360" r="1.8" fill="#FFF7B0"/></g></g>'
    '<g transform="translate(430 252) scale(.4)">'
    '<path d="M18 40C80 30 220 30 282 40L276 54C220 46 80 46 24 54Z" fill="#D7263D"/><rect x="30" y="54" width="240" height="10" fill="#3a2a2a"/>'
    '<rect x="50" y="80" width="200" height="14" fill="#D7263D"/><rect x="72" y="54" width="20" height="246" fill="#D7263D"/><rect x="208" y="54" width="20" height="246" fill="#D7263D"/>'
    '<rect x="66" y="288" width="32" height="14" fill="#3a2a2a"/><rect x="202" y="288" width="32" height="14" fill="#3a2a2a"/><rect x="138" y="62" width="24" height="32" fill="#3a2a2a"/></g>'
    '</svg>')

def season_of(m):
    return "spring" if m in (3, 4, 5) else "summer" if m in (6, 7, 8) else "autumn" if m in (9, 10, 11) else "winter"
TODAY_M = datetime.date.today().month

def _face_av():
    return packy_face()

def hero_html():
    rows = "".join(
        '<li><a href="/%s-pocket?src=hub_japan" data-board="%s" aria-label="%s to %s by %s, %s. Open the Pocket Guide">'
        '<span class="f fr" data-to="%s" data-v="%s">%s</span><span class="f to" data-v="%s">%s</span><span class="f by" data-v="%s">%s</span>'
        '<span class="f t" data-v="%s">%s</span><span class="go" aria-hidden="true">›</span></a></li>'
        % (pk, pk, fr.title(), to.title(), by.title(), t.replace("~", "about ").replace("MIN", "minutes").replace("2H30", "2 hours 30"),
           to, fr, fr, to, to, by, by, t, t)
        for fr, to, by, t, pk, src in BOARD)
    return ("""<section class="jp-hero" aria-labelledby="jpHeroT">
<div class="jp-hero-in">
<div class="jp-hero-top"><div class="jp-hero-text">
<span class="jp-hero-kick">🇯🇵 ようこそ · Yōkoso</span>
<h1 id="jpHeroT">Welcome to <em>Japan</em></h1>
<p class="jp-hero-lead">Every PackSmart guide for Japan in one place, from the arrivals gate to the platform. Facts come from official sources, with the date we checked them.</p>
<button type="button" class="jp-hello" id="jpHello"><span class="av" aria-hidden="true">""" + _face_av() + """</span><span class="bub"><b>Konnichiwa!</b> I'm Packy 👋 Where are you landing? Ask me anything.</span></button>
<div class="jp-live" aria-label="Japan right now"><span id="jpClock">🕗 Japan time</span><span id="jpWx" hidden></span><span id="jpSeason"></span></div>
</div><div class="jp-scene" data-season="%%SEASON%%">""" + FUJI_SVG + '<div class="sk" aria-hidden="true">' + SAKURA_SVG + """</div>
<div class="jp-seasons" role="group" aria-label="See Mt Fuji in each season"><small>See Mt Fuji through the seasons <i aria-hidden="true">→</i></small><span class="jp-seasons-row"><button type="button" class="jp-s-prev" aria-label="Previous season">&#8249;</button><b class="jp-s-lbl" aria-live="polite"></b><button type="button" class="jp-s-next" aria-label="Next season">&#8250;</button></span></div></div></div>
""" + ASK + """
</div>
</section>
<div class="jp-mini" id="jpMini" aria-label="Ask Packy about Japan"><div class="jp-mini-in">
<p class="jp-mini-t"><span lang="ja">ようこそ</span> Welcome to <em>Japan</em></p>
<form class="jp-mini-f" id="jpMiniF" autocomplete="off"><span class="av" aria-hidden="true">""" + _face_av() + """</span><label class="jp-sr" for="jpMiniQ">Ask Packy about Japan</label><input id="jpMiniQ" type="text" maxlength="300" placeholder="Ask Packy about Japan…"><button type="submit">Ask &#10148;</button></form>
<div class="jp-scene jp-mini-scene" aria-hidden="true" data-season="%%SEASON%%">""" + FUJI_SVG + """</div>
</div></div>""").replace("%%SEASON%%", season_of(TODAY_M))

def passes_html():
    cards = "".join(
        '<article class="jp-pass"><div class="jp-pass-main"><div class="jp-pass-top"><span>Arriving at</span></div>'
        '<div class="jp-pass-code">%s<small>✈</small></div><div class="jp-pass-name">%s</div><div class="jp-pass-serves">For %s</div>'
        '<p class="jp-pass-line">%s</p><button type="button" class="jp-pass-ask" data-q="%s">💬 Ask Packy about %s</button></div>'
        '<span class="jp-stamp" aria-hidden="true">確認<br>CHECKED</span>'
        '<div class="jp-pass-stub"><small>GATE</small><a href="/%s-pocket?src=hub_japan" data-pass="%s">📱 Pocket Guide</a><a class="g" href="/blog/%s">Airport guide</a></div></article>'
        % (code, name, serves, line, q, name.replace(" Airport", ""), pk, pk, slug)
        for code, name, serves, line, pk, slug, q in PASSES)
    return ("""<section id="arriving" aria-labelledby="jpPassT"><div class="jp-pass-h"><span class="jp-kick"><span lang="ja">空港</span> · Airports</span><h2 id="jpPassT">Where are you landing?</h2><p>Pick your airport: its Pocket Guide works offline at the gate, no app needed, and Packy can answer the rest.</p></div>
<div class="jp-passes">""" + cards + """</div></section>""")

def _words():   # the cat's starter words, shared with the "Email me these words" email (api/_japan_words.js)
    src = open(os.path.join(ROOT, "api", "_japan_words.js"), encoding="utf-8").read()
    m = re.search(r"export const WORDS = (\[.*?\]);", src, re.S)
    if not m:
        die("api/_japan_words.js: WORDS list not found")
    w = json.loads(m.group(1))
    if len(w) < 4 or any(len(x) != 4 for x in w):
        die("api/_japan_words.js: each word needs [emoji, meaning, Japanese, romaji]")
    return json.dumps(w, ensure_ascii=False).replace("</", "<\\/")


def _lessons():   # Fuku's emailed lessons, for the "Hear Fuku say it" card (api/_japan_lessons.js)
    src = open(os.path.join(ROOT, "api", "_japan_lessons.js"), encoding="utf-8").read()
    m = re.search(r"export const LESSONS = (\{.*?\});\s*$", src, re.S)
    if not m:
        die("api/_japan_lessons.js: LESSONS object not found")
    ls = json.loads(m.group(1))
    if not ls or any(not x.get("title") or not x.get("phrases") or any(len(p) != 3 for p in x["phrases"]) for x in ls.values()):
        die("api/_japan_lessons.js: each lesson needs a title and phrases of [romaji, Japanese, meaning]")
    return json.dumps(ls, ensure_ascii=False).replace("</", "<\\/")


HERO_JS = """<script>
(function(){
function track(s,x){try{if(window.gtag)gtag('event','hub_japan',{event_category:'engagement',status:s,item:x||'',page_path:location.pathname});}catch(e){}}
var still=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
// Japan time, every 30 seconds
var ck=document.getElementById('jpClock');
function tick(){try{ck.textContent='🕗 '+new Date().toLocaleTimeString('en-GB',{timeZone:'Asia/Tokyo',hour:'2-digit',minute:'2-digit'})+' in Japan';}catch(e){}}
tick();setInterval(tick,30000);
// the season, from JNTO's weather and season pages (docs/research/japan-basics-sources.md, checked 24 Nov 2026)
var S=['❄️ Winter: powder snow in Hokkaido','❄️ Winter: powder snow in Hokkaido','🌸 Cherry blossoms move north, March to May','🌸 Cherry blossom season, moving north','🌸 Late blossoms up north; rainy season from May to June','☔ Rainy season in much of Japan','☀️ Hot and humid summer; peak travel to August','☀️ Hot summer; typhoons possible in August and September','🌀 Typhoons possible: check the forecast','🍁 Autumn leaves, from Hokkaido south','🍁 Autumn leaves, from Hokkaido south','❄️ Snow season up north; New Year closures late Dec'];
var m=+new Date().toLocaleString('en-US',{timeZone:'Asia/Tokyo',month:'numeric'});document.getElementById('jpSeason').textContent=S[(m||1)-1];
// the drawn scene follows the season too (?season=spring|summer|autumn|winter previews one)
var q=(location.search.match(/[?&]season=(spring|summer|autumn|winter)/)||[])[1];
var sn=q||(m>=3&&m<=5?'spring':m>=6&&m<=8?'summer':m>=9&&m<=11?'autumn':'winter');
[].forEach.call(document.querySelectorAll('.jp-scene'),function(sc){sc.setAttribute('data-season',sn);});document.body.setAttribute('data-season',sn);
// weather in Tokyo and Sapporo (/api/weather), kept for 30 minutes in this visit
var wx=document.getElementById('jpWx');
function showWx(d){if(d&&d.t!=null&&d.s!=null){wx.textContent='🌡️ Tokyo '+d.t+'° · Sapporo '+d.s+'°';wx.hidden=false;}}
var c=null;try{c=JSON.parse(sessionStorage.getItem('jp_wx')||'null');}catch(e){}
if(c&&Date.now()-c.at<1800000)showWx(c);else{
 var g=function(city){return fetch('/api/weather?city='+city).then(function(r){return r.json();}).then(function(j){return j&&j.success?Math.round(j.weather.temp):null;}).catch(function(){return null;});};
 Promise.all([g('Tokyo,JP'),g('Sapporo,JP')]).then(function(v){var d={t:v[0],s:v[1],at:Date.now()};showWx(d);try{sessionStorage.setItem('jp_wx',JSON.stringify(d));}catch(e){}});
}
// the board flips into place, letter by letter (not with reduced motion)
if(!still){var A='ABCDEFGHIJKLMNOPRSTUVWXYZ0123456789';[].forEach.call(document.querySelectorAll('.jp-board .f'),function(el,i){
  var v=el.getAttribute('data-v'),n=0,steps=8+(i%5)*2;
  var id=setInterval(function(){n++;if(n>=steps){el.textContent=v;clearInterval(id);return;}
    el.textContent=v.split('').map(function(ch,k){return /[A-Z0-9]/.test(ch)&&k>=n-3?A[(Math.random()*A.length)|0]:ch;}).join('');},55);});}
// Fuji drifts as the page scrolls, like a far-away mountain (not with reduced motion)
var fj=document.querySelector('.jp-scene .fuji');
if(fj&&!still){var tk=false;window.addEventListener('scroll',function(){if(tk)return;tk=true;requestAnimationFrame(function(){var y=Math.min(window.scrollY,700);fj.style.transform='translateY('+(y*0.08).toFixed(1)+'px) scale('+(1+y*0.00008).toFixed(4)+')';tk=false;});},{passive:true});}
// the lucky cat says Konnichiwa on hover (CSS) or tap
var cat=document.getElementById('jpCat');
// a tap or click also says it out loud with the phone's or computer's own voice (Japanese if the device has one).
// Only on a tap, never on hover: browsers block sound that starts without one, and surprise audio annoys people.
// a young, bright voice to match the cat: a female Japanese voice where the device has one (Apple Kyoko / O-Ren, Google
// 日本語, Microsoft Nanami / Haruka / Ayumi), pitched up; else a female English voice saying "Kon-nichi-wa"
var jaVoice=null,enVoice=null,FEM=/kyoko|o-?ren|nanami|haruka|ayumi|mayu|google 日本語|female|samantha|karen|moira|tessa|zira|aria|jenny|google uk english female/i,MALE=/otoya|hattori|ichiro|keita|daniel|alex|fred|david|guy|(^|[^e])male/i;
function best(list){var f=list.filter(function(x){return FEM.test(x.name)&&!MALE.test(x.name);});return f[0]||list.filter(function(x){return !MALE.test(x.name);})[0]||list[0]||null;}
function pickVoice(){try{var v=speechSynthesis.getVoices();jaVoice=best(v.filter(function(x){return /^ja(-|_|$)/i.test(x.lang);}));enVoice=best(v.filter(function(x){return /^en(-|_|$)/i.test(x.lang);}));}catch(e){}}
if('speechSynthesis' in window){pickVoice();try{speechSynthesis.addEventListener('voiceschanged',pickVoice);}catch(e){}}
var catU=null,catAt=0;
function sayHello(){try{if(!('speechSynthesis' in window))return;var now=Date.now();
  if(speechSynthesis.speaking&&now-catAt<3000)return;if(speechSynthesis.speaking||speechSynthesis.pending)speechSynthesis.cancel();
  try{speechSynthesis.resume();}catch(e){}if(!jaVoice&&!enVoice)pickVoice();
  var vo=jaVoice||enVoice;catU=new SpeechSynthesisUtterance(jaVoice||!vo?'こんにちは！':'Kon-nichi-wa!');if(vo){catU.voice=vo;catU.lang=vo.lang;}else catU.lang='ja-JP';
  catU.rate=1.05;catU.pitch=1.8;catU.volume=1;catAt=now;speechSynthesis.speak(catU);track('cat_voice');}catch(e){}}
// after the second Konnichiwa the cat offers a few Japanese words: a small card with 8 starter phrases (the same wording
// as the Pocket Guides' "Say it in Japanese" list), each with a play button, and a link to the Tokyo Pocket Guide for more.
// Offered once per visit; "Not now" is remembered for the visit too.
var WORDS=%%WORDS%%,LESSONS=%%LESSONS%%;
function sayJa(ja,ro){try{if(!('speechSynthesis' in window))return;if(speechSynthesis.speaking||speechSynthesis.pending)speechSynthesis.cancel();
  try{speechSynthesis.resume();}catch(e){}if(!jaVoice&&!enVoice)pickVoice();var vo=jaVoice||enVoice,u=new SpeechSynthesisUtterance(jaVoice||!vo?ja:ro);
  if(vo){u.voice=vo;u.lang=vo.lang;}else u.lang='ja-JP';u.rate=.9;u.pitch=1.3;speechSynthesis.speak(u);}catch(e){}}
var taps=0,offered=false,offer=null,words=null,lastFocus=null;try{offered=sessionStorage.getItem('jpWordsOffer')==='1';}catch(e){}
function esc(t){return String(t).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
function closeWords(){if(!words)return;words.hidden=true;document.removeEventListener('keydown',wordsKey);if(lastFocus)try{lastFocus.focus();}catch(e){}}
function wordsKey(e){if(e.key==='Escape')closeWords();}
function openWords(){if(!words){words=document.createElement('div');words.className='jp-words';words.hidden=true;
  words.setAttribute('role','dialog');words.setAttribute('aria-modal','true');words.setAttribute('aria-labelledby','jpWordsT');
  words.innerHTML='<div class="jp-words-in"><button type="button" class="jp-words-x" aria-label="Close">✕</button>'+
   '<h3 id="jpWordsT">Your first Japanese words <span lang="ja">🇯🇵</span></h3><p class="jp-words-sub">Tap 🔊 to hear each one. A smile and a small bow go a long way.</p><ul>'+
   WORDS.map(function(w,i){return '<li><i aria-hidden="true">'+w[0]+'</i><div><b>'+esc(w[3])+'<span lang="ja">'+esc(w[2])+'</span></b><small>'+esc(w[1])+'</small></div><button type="button" data-w="'+i+'" aria-label="Play: '+esc(w[1])+'">🔊</button></li>';}).join('')+
   '</ul><div class="jp-words-mail"><button type="button" class="jp-words-mbtn">📩 Email me these words</button></div>'+
   '<a class="jp-words-more" href="/japan-phrasebook?l=0&amp;src=hub_cat">📖 Fuku’s Phrasebook: every lesson, tap to hear · works offline</a>'+
   '<p class="jp-words-note">The voice is your phone’s or computer’s own.</p></div>';
  document.body.appendChild(words);
  words.addEventListener('click',function(e){if(e.target===words||e.target.closest('.jp-words-x')){closeWords();return;}
   var b=e.target.closest('[data-w]');if(b){var w=WORDS[+b.getAttribute('data-w')];sayJa(w[2],w[3]);track('cat_word_play',w[3]);return;}
   if(e.target.closest('.jp-words-more'))track('cat_words_more');
   if(e.target.closest('.jp-words-mbtn'))mailForm();});}
 lastFocus=document.activeElement;words.hidden=false;document.addEventListener('keydown',wordsKey);try{words.querySelector('.jp-words-x').focus();}catch(e){}}
// "Email me these words": Packy's email (D58, extended to this card on 26 Nov): the address, then a separate yes for
// trip tips, then the trip month, exactly like "Email me this chat". The words themselves come from the server's own list.
function okMail(v){return /^[^@ ]+@[^@ ]+[.][^@ ]{2,}$/.test(v);}
function mailPost(b){return fetch('/api/email-chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(b)}).then(function(x){return x.json().then(function(d){return [x.ok,d];});});}
function mailForm(){var box=words.querySelector('.jp-words-mail'),known='';try{known=localStorage.getItem('packy_email')||'';}catch(e){}if(!okMail(known))known='';
 box.innerHTML='<form novalidate><b>📩 Get these words by email</b><div class="r"><input type="email" autocomplete="email" inputmode="email" placeholder="Your email" aria-label="Your email" value="'+esc(known)+'"><button type="submit">Send</button></div>'+
  '<span class="f">Just these words, with a link to hear them again. <a href="/privacy-policy">Privacy</a></span></form>';
 track('cat_words_mail');var f=box.querySelector('form'),inp=f.querySelector('input'),btn=f.querySelector('button');try{inp.focus();}catch(e){}
 f.addEventListener('submit',function(e){e.preventDefault();var em=inp.value.trim();if(!okMail(em)){inp.focus();inp.style.borderColor='#E94560';return;}
  btn.disabled=true;btn.textContent='…';
  mailPost({kind:'words',email:em,tips:false,country:'japan'}).then(function(x){
   if(!x[0]||!x[1].ok){btn.disabled=false;btn.textContent='Send';var er=f.querySelector('.e')||f.appendChild(document.createElement('span'));er.className='e';er.textContent=(x[1]&&x[1].error)||'Sorry, that did not work.';track('cat_words_mail_error');return;}
   try{localStorage.setItem('packy_email',em);}catch(e){}track('cat_words_mail_sent');
   box.innerHTML='<b>✅ Sent to '+esc(em)+'</b><p>Want trip tips for Japan before you go?</p><div class="r2"><button type="button" class="y">Yes please</button><button type="button" class="n">No thanks</button></div>';
   box.querySelector('.n').addEventListener('click',function(){box.innerHTML='<b>✅ Sent to '+esc(em)+'</b><p>Check your inbox (and spam, just in case). Safe travels! 🇯🇵</p>'+waBtn();track('cat_words_tips_no');});
   box.querySelector('.y').addEventListener('click',function(){var d=new Date();d.setDate(1);var ch='';
    for(var i=0;i<8;i++){var v=d.getFullYear()+'-'+('0'+(d.getMonth()+1)).slice(-2);ch+='<button type="button" data-m="'+v+'">'+d.toLocaleString('en',{month:'short'})+(d.getMonth()===0||i===0?' '+d.getFullYear():'')+'</button>';d.setMonth(d.getMonth()+1);}
    box.innerHTML='<b>Great! When is your trip?</b><div class="r2">'+ch+'<button type="button" data-m="">Not sure</button></div><span class="f">You can unsubscribe any time.</span>';
    [].forEach.call(box.querySelectorAll('[data-m]'),function(m){m.addEventListener('click',function(){[].forEach.call(box.querySelectorAll('[data-m]'),function(z){z.disabled=true;});
     mailPost({update:true,from:'words',email:em,tips:true,trip:m.getAttribute('data-m'),country:'japan'}).then(function(x){
      box.innerHTML=(x[0]&&x[1].ok?'<b>🎉 You’re on the list</b><p>We’ll send a few useful tips before your trip. Your words are in your inbox now.</p>':'<b>Your words are on their way</b><p>'+esc((x[1]&&x[1].error)||'We could not save the trip tips, sorry.')+'</p>')+waBtn();
      track(x[0]&&x[1].ok?'cat_words_tips_yes':'cat_words_tips_error');}).catch(function(){box.innerHTML='<b>Your words are on their way</b><p>We could not save the trip tips without a connection.</p>';});});});});
  }).catch(function(){btn.disabled=false;btn.textContent='Send';track('cat_words_mail_error');});});}
var lesson=null,sayM=/^([1-9])-([1-9])$/.exec((function(){try{return new URLSearchParams(location.search).get('say')||'';}catch(e){return '';}})());
function lessonKey(e){if(e.key==='Escape')closeLesson();}
function closeLesson(){if(!lesson)return;lesson.hidden=true;document.removeEventListener('keydown',lessonKey);}
function openLesson(n,hot){var L=LESSONS[n];if(!L)return;if(lesson)lesson.remove();
  lesson=document.createElement('div');lesson.className='jp-words jp-lesson';lesson.setAttribute('role','dialog');lesson.setAttribute('aria-modal','true');lesson.setAttribute('aria-labelledby','jpLessonT');
  lesson.innerHTML='<div class="jp-words-in"><button type="button" class="jp-words-x" aria-label="Close">✕</button>'+
   '<h3 id="jpLessonT">Fuku’s lesson '+n+': '+esc(L.title)+'</h3><p class="jp-words-sub">Tap 🔊 to hear each phrase, then say it back. Slowly is fine!</p><ul>'+
   L.phrases.map(function(p,i){return '<li'+(i===hot?' class="hot"':'')+'><i aria-hidden="true">'+(i+1)+'</i><div><b>'+esc(p[0])+'<span lang="ja">'+esc(p[1])+'</span></b><small>'+esc(p[2])+'</small></div><button type="button" data-p="'+i+'" aria-label="Play: '+esc(p[2])+'">🔊</button></li>';}).join('')+
   '</ul><div class="jp-words-mail"><button type="button" class="jp-words-mbtn jp-lesson-words">👋 Fuku’s 8 starter words</button></div>'+
   '<a class="jp-words-more" href="/japan-phrasebook?l='+n+'&amp;src=hub_lesson">📖 All of Fuku’s lessons in the Phrasebook · works offline</a>'+
   '<p class="jp-words-note">The voice is your phone’s or computer’s own.</p></div>';
  document.body.appendChild(lesson);
  lesson.addEventListener('click',function(e){if(e.target===lesson||e.target.closest('.jp-words-x')){closeLesson();return;}
   var b=e.target.closest('[data-p]');if(b){var p=L.phrases[+b.getAttribute('data-p')];var li=b.closest('li');[].forEach.call(lesson.querySelectorAll('li.hot'),function(x){if(x!==li)x.classList.remove('hot');});sayJa(p[1],p[0]);track('lesson_play',n+':'+p[0]);return;}
   if(e.target.closest('.jp-lesson-words')){closeLesson();openWords();track('lesson_words');return;}
   if(e.target.closest('.jp-words-more'))track('lesson_more');});
  document.addEventListener('keydown',lessonKey);
  var h=lesson.querySelector('li.hot');if(h)try{h.scrollIntoView({block:'nearest'});}catch(e){}
  try{lesson.querySelector('li.hot button, .jp-words-x').focus({preventScroll:true});}catch(e){}
  track('lesson_open',n+(hot>=0?'-'+(hot+1):''));}
function waBtn(){var t='🐱 Fuku’s first Japanese words for my trip:\\n'+WORDS.slice(0,4).map(function(w){return w[3]+' = '+w[1];}).join('\\n')+'\\n🔊 Hear them all (works offline): https://www.packsmartapp.com/japan-phrasebook?l=0&src=wa_self';
 return '<a class="jp-wa" href="https://wa.me/?text='+encodeURIComponent(t)+'" target="_blank" rel="noopener">📲 Also send to my WhatsApp</a>';}
document.addEventListener('click',function(e){if(e.target.closest&&e.target.closest('.jp-wa'))track('cat_words_wa');});
function hideOffer(){if(offer)offer.hidden=true;cat.classList.remove('offering');}
function showOffer(){if(offered)return;offered=true;try{sessionStorage.setItem('jpWordsOffer','1');}catch(e){}
 offer=document.createElement('div');offer.className='jp-cat-offer';offer.setAttribute('role','status');
 offer.innerHTML='Want a few <b>Japanese words</b> for your trip?<div><button type="button" class="y">Yes! 🎌</button><button type="button" class="n">Not now</button></div>';
 cat.parentNode.insertBefore(offer,cat.nextSibling);cat.classList.add('offering');track('cat_words_offer');
 offer.querySelector('.y').addEventListener('click',function(){hideOffer();track('cat_words_yes');openWords();});
 offer.querySelector('.n').addEventListener('click',function(){hideOffer();track('cat_words_no');});}
if(cat){var ct;cat.addEventListener('click',function(){cat.classList.add('on','heard');track('cat_hello');sayHello();clearTimeout(ct);
  taps++;if(taps>=2&&!offered){ct=setTimeout(function(){cat.classList.remove('on');showOffer();},1600);return;}
  ct=setTimeout(function(){cat.classList.remove('on');},2500);});
 if(location.hash==='#words'){offered=true;setTimeout(function(){openWords();track('cat_words_link');},400);}
 else if(sayM){offered=true;setTimeout(function(){openLesson(sayM[1],+sayM[2]-1);},400);}
 cat.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();cat.click();}});
 cat.addEventListener('mouseenter',function(){track('cat_hello');});
}
// the compact welcome band: slides in under the menu once the hero's Ask box has scrolled away, and the page scrolls
// underneath it (the full hero is taller than most screens, so it cannot stay at full size)
var mini=document.getElementById('jpMini'),askBox=document.getElementById('ask');
if(mini&&askBox){var mt=false;function syncMini(){mt=false;var on=askBox.getBoundingClientRect().bottom<80;if(on!==mini.classList.contains('on')){mini.classList.toggle('on',on);mini.setAttribute('aria-hidden',on?'false':'true');}}
 syncMini();window.addEventListener('scroll',function(){if(!mt){mt=true;requestAnimationFrame(syncMini);}},{passive:true});window.addEventListener('resize',syncMini);}
var mf=document.getElementById('jpMiniF');
if(mf)mf.addEventListener('submit',function(e){e.preventDefault();var i=document.getElementById('jpMiniQ'),t=(i.value||'').trim();if(t.length<5){i.focus();return;}track('mini_ask',t.slice(0,60));if(window.Packy){window.Packy.ask(t);i.value='';}});
// Fuji through the seasons: ‹ › cycle the drawn scene (hero, small band and falling petals); starts on the real season
var SEAS=[['spring','春','Spring'],['summer','夏','Summer'],['autumn','秋','Autumn'],['winter','冬','Winter']],sIx=0;
for(var si=0;si<4;si++)if(SEAS[si][0]===sn)sIx=si;
var sLbl=document.querySelector('.jp-s-lbl');
function showSeason(i,user){sIx=(i+4)%4;var k=SEAS[sIx][0];[].forEach.call(document.querySelectorAll('.jp-scene'),function(x){x.setAttribute('data-season',k);});document.body.setAttribute('data-season',k);
 if(sLbl)sLbl.innerHTML='<span lang="ja">'+SEAS[sIx][1]+'</span>'+SEAS[sIx][2]+(k===sn?' · now':'');if(user)track('season_view',k);}
if(sLbl){showSeason(sIx,false);document.querySelector('.jp-s-prev').addEventListener('click',function(){showSeason(sIx-1,true);});document.querySelector('.jp-s-next').addEventListener('click',function(){showSeason(sIx+1,true);});}
// Packy: the hello bubble and "Ask Packy about ..." on each boarding pass
function packy(q){if(window.Packy){if(q)window.Packy.ask(q);else window.Packy.open();}else{var a=document.getElementById('ask');if(a)a.scrollIntoView({behavior:'smooth'});}}
var hl=document.getElementById('jpHello');if(hl)hl.addEventListener('click',function(){track('hero_packy');var i=document.getElementById('askQ');if(i){i.scrollIntoView({behavior:still?'auto':'smooth',block:'center'});i.focus({preventScroll:true});}else packy('');});
// one listener for the whole page, so the station tickets further down (built after this script) work too
document.addEventListener('click',function(e){var t=e.target.closest&&e.target.closest('.jp-pass-ask,[data-pass]');if(!t)return;if(t.classList.contains('jp-pass-ask')){var q=t.getAttribute('data-q');track(t.closest('.jp-tk')?'ticket_packy':'pass_packy',q);packy(q);}else track(t.closest('.jp-tk')?'ticket_tap':'pass_tap',t.getAttribute('data-pass'));});
[].forEach.call(document.querySelectorAll('[data-board]'),function(a){a.addEventListener('click',function(){track('board_tap',a.getAttribute('data-board'));});});
})();
</script>"""
HERO_JS = HERO_JS.replace("%%WORDS%%", _words()).replace("%%LESSONS%%", _lessons())



# ---- Japan backdrop for wide screens (25 Nov 2026): washi-paper colour with a faint seigaiha (wave) pattern, sakura
# branches reaching in from both sides and a few drifting petals. Drawn here as vectors (no photos, no downloads); shown
# only where the page has empty sides (1200px and wider), and the petals stay still for people who prefer less motion.
_FLOWER = ('<g id="sk-f"><g fill="#FFC9D6" stroke="#F49AB0" stroke-width=".8">'
           + "".join('<path transform="rotate(%d)" d="M0 0C-5-4-6-12-2-15L0-13 2-15C6-12 5-4 0 0Z"/>' % a for a in (0, 72, 144, 216, 288))
           + '</g><circle r="2.6" fill="#E94560"/><g fill="#C2185B">'
           + "".join('<circle cx="%.1f" cy="%.1f" r=".9"/>' % (4.2 * __import__("math").cos(__import__("math").radians(a)), 4.2 * __import__("math").sin(__import__("math").radians(a))) for a in range(0, 360, 60))
           + '</g></g><g id="sk-b"><ellipse rx="3.4" ry="5" fill="#F7A8BC"/><path d="M0 4v4" stroke="#7a4b3a" stroke-width="1.2"/></g>')
_BLOOMS = [(150, 92, 1.5, 10), (118, 150, 1.2, 40), (205, 150, 1.4, 70), (92, 214, 1.1, 15), (178, 236, 1.6, 50), (232, 268, 1.1, 5),
           (60, 300, 1.3, 30), (140, 330, 1.2, 80), (210, 360, 1.5, 20), (96, 420, 1.0, 60), (168, 462, 1.3, 35), (62, 520, 1.2, 0),
           (122, 560, 1.4, 45), (40, 612, 1.0, 25), (100, 660, 1.2, 65), (250, 210, 1.0, 12), (30, 400, 1.1, 55)]
_BUDS = [(176, 112, 20), (230, 190, -30), (70, 250, 40), (190, 300, -10), (40, 470, 30), (150, 520, -25), (78, 600, 15)]
SAKURA_SVG = ('<svg viewBox="0 0 300 720" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false"><defs>' + _FLOWER + '</defs>'
    '<g fill="none" stroke="#6B4235" stroke-linecap="round">'
    '<path d="M-20 700C30 610 20 540 60 470S150 360 140 300 190 190 160 90" stroke-width="13"/>'
    '<path d="M60 470C100 450 150 470 175 462" stroke-width="6"/><path d="M95 380C60 350 40 320 60 300" stroke-width="6"/>'
    '<path d="M150 330C185 320 205 340 210 360" stroke-width="5"/><path d="M145 250C180 240 220 250 232 268" stroke-width="6"/>'
    '<path d="M150 190C140 160 120 150 118 150" stroke-width="5"/><path d="M155 150C180 140 200 145 205 150" stroke-width="5"/>'
    '<path d="M40 560C70 560 110 555 122 560" stroke-width="6"/><path d="M30 640C55 650 85 655 100 660" stroke-width="5"/>'
    '<path d="M70 250C80 230 88 220 92 214" stroke-width="4"/><path d="M178 236C190 230 230 210 250 210" stroke-width="3"/></g>'
    + "".join('<use href="#sk-f" transform="translate(%d %d) scale(%.1f) rotate(%d)"/>' % b for b in _BLOOMS)
    + "".join('<use href="#sk-b" transform="translate(%d %d) rotate(%d)"/>' % b for b in _BUDS)
    + '</svg>')
_PETAL = '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M10 2C4 6 3 13 10 18 17 13 16 6 10 2Z" fill="#FFC1D1" stroke="#F49AB0" stroke-width=".8"/></svg>'
SAKURA_BG = ('<div class="jp-bg" aria-hidden="true"><div class="jp-bg-l">' + SAKURA_SVG + '</div><div class="jp-bg-r">' + SAKURA_SVG + '</div>'
             + "".join('<i class="jp-petal" style="left:%s;animation-delay:%ss;animation-duration:%ss">%s</i>' % (l, d, t, _PETAL)
                       for l, d, t in (("4%", 0, 16), ("9%", 6, 19), ("14%", 11, 15), ("85%", 3, 18), ("90%", 9, 16), ("95%", 14, 20), ("2%", 17, 21), ("97%", 7, 17)))
             + '</div>')
SEIGAIHA = ("url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='80' height='40' viewBox='0 0 80 40'%3E"
            "%3Cg fill='none' stroke='%2300C9A7' stroke-width='1.1' opacity='.16'%3E"
            "%3Cpath d='M0 40a20 20 0 0 1 40 0M8 40a12 12 0 0 1 24 0M16 40a4 4 0 0 1 8 0'/%3E"
            "%3Cpath d='M40 40a20 20 0 0 1 40 0M48 40a12 12 0 0 1 24 0M56 40a4 4 0 0 1 8 0'/%3E"
            "%3Cpath d='M-20 20a20 20 0 0 1 40 0M-12 20a12 12 0 0 1 24 0M-4 20a4 4 0 0 1 8 0'/%3E"
            "%3Cpath d='M20 20a20 20 0 0 1 40 0M28 20a12 12 0 0 1 24 0M36 20a4 4 0 0 1 8 0'/%3E"
            "%3Cpath d='M60 20a20 20 0 0 1 40 0M68 20a12 12 0 0 1 24 0M76 20a4 4 0 0 1 8 0'/%3E%3C/g%3E%3C/svg%3E\")")
HERO_CSS += """
:root{--bg:#FDF0F2;--pw:900px}
html,body{overflow-x:clip}
.jp-bg{display:none}
/* big screens: the hero photo runs edge to edge, and from 1500px the page itself is wider (4 boarding passes in a row,
   guide cards 3 across), so the space is used for content first and decoration second */
@media (min-width:1000px){
 .jp-hero h1{font-size:4.2rem}
}
@media (min-width:1500px){
 :root{--pw:1320px}
 .page-wrapper{max-width:1320px}
 .jp-passes{grid-template-columns:repeat(4,1fr)}
 .jp-pass{flex-direction:column}
 .jp-pass-stub{width:auto;flex-direction:row;align-items:center;padding:10px 12px;border-left:0;border-top:2px dashed rgba(255,255,255,.7)}
 .jp-pass-stub small{display:none}.jp-pass-stub a{flex:1}
 .jp-pass-stub:before,.jp-pass-stub:after{display:none}
 .jp-stamp{right:14px}
 .blog-grid{grid-template-columns:repeat(3,1fr)}
 .jp-ask{max-width:1000px}
}
@media (min-width:1200px){
 body{background:#FDF0F2 """ + SEIGAIHA + """ fixed}
 .jp-bg{display:block;position:fixed;inset:0;pointer-events:none;z-index:0;overflow:hidden}
 .page-wrapper{position:relative;z-index:1}
 .jp-bg-l,.jp-bg-r{position:absolute;opacity:.95}
 .jp-bg-l{left:-10px;top:60px;width:min(520px,calc((100vw - var(--pw))/2 + 40px))}
 .jp-bg-r{right:-10px;top:auto;bottom:-60px;transform:scaleX(-1);width:min(420px,calc((100vw - var(--pw))/2 + 20px))}
 .jp-bg svg{width:100%;height:auto;display:block}
 .jp-petal{position:absolute;top:-30px;width:16px;height:16px;animation:jpFall linear infinite;opacity:.85}
 .jp-petal svg{width:100%;height:100%;display:block}
}
@keyframes jpFall{0%{transform:translate(0,0) rotate(0)}25%{transform:translate(30px,25vh) rotate(90deg)}50%{transform:translate(-10px,50vh) rotate(200deg)}75%{transform:translate(25px,75vh) rotate(290deg)}100%{transform:translate(0,110vh) rotate(380deg)}}
@media (prefers-reduced-motion:reduce){.jp-petal{display:none!important}.jp-scene .cl,.jp-scene .ff{animation:none}}
"""

# ---- lower half (25 Nov 2026): compact "Plan your trip" cards and station-sign cards. The airport cards are gone:
# the boarding passes at the top (id="arriving") link each airport guide and Pocket Guide.
def card_data(src, slug, where):
    m = re.search(r'<a href="/blog/%s" class="blog-card"[^>]*>(.*?)</a>' % re.escape(slug), src, re.S)
    if not m:
        die("card for %s not found on %s" % (slug, where))
    c = m.group(1)
    img = re.search(r'<img class="blog-card-img" src="([^"]+)" alt="([^"]*)"', c)
    meta = re.search(r'<span class="meta">([^<]*)</span>', c)
    return {"url": "/blog/" + slug, "title": re.search(r"<h2>(.*?)</h2>", c, re.S).group(1).strip(),
            "desc": re.search(r"<p>(.*?)</p>", c, re.S).group(1).strip(), "img": img.group(1) if img else "",
            "alt": img.group(2) if img else "", "read": meta.group(1).split("&middot;")[-1].strip() if meta else ""}

def short_title(t):   # "Kyoto Travel Guide 2026: Private Guide, ..." -> ("Kyoto Travel Guide", "Private Guide, ...")
    a, _, b = t.partition(":")
    return re.sub(r"\s*20\d\d\b", "", a).strip(), b.strip()

def checked_on(key):  # the date the Pocket Guide's facts were last checked, read from the guide itself
    pg = open(os.path.join(ROOT, "public", key + "-pocket.html"), encoding="utf-8").read()
    ds = re.findall(r"[Cc]hecked (?:on )?(\d{1,2} [A-Z][a-z]+ 20\d\d)", pg)
    if not ds:
        die("no checked date in %s-pocket.html" % key)
    return max(set(ds), key=ds.count)

def plan_html():
    out = []
    for slug in PLAN:
        d = card_data(blog, slug, "blog.html")
        t, sub = short_title(d["title"])
        out.append('<a class="jp-plan" href="%s"><img src="%s" alt="%s" loading="lazy" width="680" height="340">'
                   '<span class="jp-plan-b"><b>%s</b><small>%s</small><i>%s &rarr;</i></span></a>' % (d["url"], d["img"], d["alt"], t, sub, d["read"]))
    return ('<section class="jp-sec" id="plan" aria-labelledby="jpPlanT"><div class="jp-sec-h"><span class="jp-kick"><span lang="ja">旅の計画</span> · Plan</span><h2 id="jpPlanT">Plan your trip</h2>'
            '<p>Visas, seasons, budget, packing and a 7-day route.</p></div><div class="jp-plans">' + "".join(out) + '</div></section>')

KANJI = {"tokyo": "東京", "shinjuku": "新宿", "ueno": "上野", "kyoto": "京都", "osaka": "新大阪・大阪", "sapporo": "札幌"}
def stations_html():
    pk = {g["key"]: g for g in json.load(open(os.path.join(ROOT, "tools", "pocket_guides.json"), encoding="utf-8"))["guides"]}
    out = []
    for slug in STATIONS:
        key = slug.replace("-station-guide", "")
        g = pk[key]
        short = g["name"].replace(" Station", "").replace(" and Umeda", "")
        out.append('<article class="jp-pass jp-tk"><div class="jp-pass-main"><div class="jp-pass-top"><span><span lang="ja">乗車券</span> · Station ticket</span></div>'
                   '<div class="jp-pass-code" lang="ja">%s</div><div class="jp-pass-name">%s</div><div class="jp-pass-serves">In %s</div>'
                   '<p class="jp-pass-line">%s</p><button type="button" class="jp-pass-ask" data-q="What should I know about %s?">💬 Ask Packy about %s</button></div>'
                   '<span class="jp-stamp" title="Facts checked against official sources">確認<br>%s</span>'
                   '<div class="jp-pass-stub"><small><span lang="ja">改札</span> · GATE</small><a href="/%s-pocket?src=hub_japan" data-pass="%s">📱 Pocket Guide</a><a class="g" href="/blog/%s">Station guide</a></div></article>'
                   % (KANJI[key], g["name"], g["stop"], g["blurb"], g["name"], short, "%s %s<br>%s" % (lambda d: (d[0], d[1][:3].upper(), d[2]))(checked_on(key).split()), key, key, slug))
    return ('<section class="jp-sec" id="stations" aria-labelledby="jpStT"><div class="jp-sec-h"><span class="jp-kick"><span lang="ja">駅</span> · Stations</span>'
            '<h2 id="jpStT">Find your way in the big stations</h2>'
            '<p>Exits, platforms, lockers and ATMs, in a Pocket Guide that works offline, no app needed. Each stamp shows when we last checked the facts.</p></div>'
            '<div class="jp-passes jp-tks">' + "".join(out) + '</div></section>')

LOWER_CSS = """
.jp-sec{margin:0 0 2.4rem}.jp-sec-h{text-align:center;margin:0 0 1.1rem}
.jp-sec-h h2{font-family:var(--font-display);font-size:2.2rem;margin:0;line-height:1.1}.jp-sec-h p{color:#5a6378;margin:.35rem auto 0;max-width:620px}
.jp-plans{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
.jp-plan{display:flex;gap:12px;align-items:stretch;background:#fff;border:1px solid #E1F2EE;border-radius:18px;overflow:hidden;text-decoration:none;color:#0f0f23;box-shadow:0 6px 18px rgba(15,15,35,.05);transition:transform .15s,border-color .15s}
.jp-plan:hover{transform:translateY(-2px);border-color:#00C9A7}
.jp-plan img{flex:none;width:132px;height:auto;min-height:118px;object-fit:cover;background:#E6FAF5}
.jp-plan-b{display:flex;flex-direction:column;justify-content:center;padding:12px 14px 12px 0;min-width:0}
.jp-plan-b b{font-size:1.02rem;line-height:1.25}.jp-plan-b small{color:#5a6378;font-size:.84rem;line-height:1.4;margin:.25rem 0 .35rem;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.jp-plan-b i{font-style:normal;font-size:.8rem;font-weight:700;color:#0a8f78}
@media (max-width:640px){.jp-plans{grid-template-columns:1fr}.jp-plan img{width:104px}.jp-sec-h h2{font-size:1.8rem}}
@media (min-width:1500px){.jp-plans{grid-template-columns:repeat(4,minmax(0,1fr))}.jp-plan{flex-direction:column;gap:0}.jp-plan img{width:100%;height:150px}.jp-plan-b{padding:12px 14px}}
"""
LOWER_CSS += """
.jp-kick{display:inline-block;font-size:.74rem;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:#E94560;margin-bottom:.35rem}
.jp-kick span{letter-spacing:.2em}
/* station tickets: the boarding pass, in the pale green of a Japanese paper train ticket with a fine wave print */
.jp-tk .jp-pass-main{background:#F2FBF8 url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='8'%3E%3Cpath d='M0 8a8 8 0 0 1 16 0' fill='none' stroke='%2300C9A7' stroke-opacity='.12'/%3E%3C/svg%3E")}
.jp-tk .jp-pass-code{font-size:2.3rem;letter-spacing:.12em;font-weight:800}
@media (max-width:600px){.jp-tk .jp-pass-code{font-size:1.6rem;letter-spacing:.04em;white-space:nowrap;margin-top:.6rem}.jp-tk .jp-pass-ask{font-size:.78rem;white-space:nowrap}}
.jp-tk .jp-stamp{font-size:.56rem;padding:3px 5px}
.jp-tk .jp-pass-stub{background:linear-gradient(135deg,#0f0f23,#26335c)}
.jp-tk .jp-pass-stub a{background:#00C9A7}.jp-tk .jp-pass-stub a.g{background:rgba(255,255,255,.14)}
@media (min-width:1500px){.jp-tks{grid-template-columns:repeat(3,1fr)}}
"""
HERO_CSS += LOWER_CSS

HERO_CSS += (".jp-mini{position:fixed;left:0;right:0;top:72px;z-index:90;background:#FDF0F2 " + SEIGAIHA + ";border-bottom:1px solid #F3D3DA;"
 "box-shadow:0 10px 26px rgba(15,15,35,.10);transform:translateY(-130%);visibility:hidden;transition:transform .28s ease,visibility .28s}"
 ".jp-mini.on{transform:none;visibility:visible}"
 ".jp-mini-in{max-width:1320px;margin:0 auto;padding:8px 24px;display:grid;grid-template-columns:auto minmax(0,1fr) 150px;gap:18px;align-items:center}"
 ".jp-mini-t{margin:0;font-family:var(--font-display);font-size:1.7rem;line-height:1;color:#0f0f23;white-space:nowrap}"
 ".jp-mini-t span{font-family:'DM Sans',sans-serif;font-size:.78rem;font-weight:800;letter-spacing:.12em;color:#0a8f78;display:block;margin-bottom:4px}"
 ".jp-mini-t em{font-style:italic;color:#E94560}"
 ".jp-mini-f{display:flex;align-items:center;gap:8px;background:#fff;border:1.5px solid #BFEDE3;border-radius:999px;padding:4px 4px 4px 6px;box-shadow:0 4px 14px rgba(0,168,140,.08)}"
 ".jp-mini-f .av{flex:none;width:34px;height:34px;border-radius:50%;background:#E6FAF5;padding:3px}.jp-mini-f .av svg{width:100%;height:100%;display:block}"
 ".jp-mini-f input{flex:1;min-width:0;border:0;outline:0;font:inherit;font-size:16px;background:transparent;padding:8px 4px;color:#0f0f23}"
 ".jp-mini-f button{flex:none;font:inherit;font-weight:800;font-size:.92rem;border:0;border-radius:999px;padding:9px 16px;background:linear-gradient(135deg,#E94560,#ff6b85);color:#fff;cursor:pointer}"
 ".jp-mini-scene{position:relative;min-height:0;height:74px}"
 "@media (max-width:760px){.jp-mini-in{grid-template-columns:minmax(0,1fr) 96px;gap:4px 10px;padding:6px 24px 8px}"
 ".jp-mini-t{font-size:1.25rem}.jp-mini-t span{font-size:.66rem;margin-bottom:2px}.jp-mini-f{grid-column:1/-1;grid-row:2}.jp-mini-scene{height:52px;grid-row:1;grid-column:2}}"
 "@media (prefers-reduced-motion:reduce){.jp-mini{transition:none}}"
 "#plan,#arriving,#stations,#pocket-hub{scroll-margin-top:200px}")
body = """<div class="page-wrapper">
    """ + hero_html() + """
    """ + HERO_JS + """
    """ + plan_html() + """
    """ + passes_html() + """
    """ + stations_html() + """
""" + "    " + pocket + """
    <div class="jp-two">
        """ + HOKKAIDO + """
        """ + SEASONS + """
    </div>
    <p class="te-back">Visa rules depend on your passport: many nationalities can visit for up to 90 days without a visa, but check <a href="https://www.mofa.go.jp/j_info/visit/visa/short/novisa.html" target="_blank" rel="noopener">Japan's official visa-exemption list</a> before you book. We also have guides for travellers from particular countries, such as <a href="/blog/japan-travel-packing-guide-from-india">India</a>. Need help that is not about Japan? See <a href="/travel-essentials">Travel Essentials</a>.</p>
</div>

"""
page = head + '<style id="jp-hero-css">' + HERO_CSS + '</style>\n' + nav + SAKURA_BG + '\n' + body + foot
for need in ('id="plan"', 'id="arriving"', 'id="stations"', "hub_japan", "</html>"):
    if need not in page:
        die("built page lacks " + need)

old = open(OUT, encoding="utf-8").read() if os.path.isfile(OUT) else ""
# w75 adds the Packy pop-up line after this script runs; ignore it when deciding whether the page changed
old = re.sub(r'<script src="/packy\.js(?:\?v=[0-9a-f]+)?"[^>]*></script>\n', "", old)
changed = old != page

# ---- sitemap
sm = open(SITEMAP, encoding="utf-8").read()
loc = "<loc>%s</loc>" % URL
if loc not in sm:
    entry = "  <url>\n    %s\n    <lastmod>%s</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>0.8</priority>\n  </url>\n" % (loc, TODAY)
    if sm.count("</urlset>") != 1:
        die("sitemap end not found")
    sm = sm.replace("</urlset>", entry + "</urlset>")
elif changed:
    sm = re.sub(r"(%s\s*<lastmod>)([0-9-]+)(</lastmod>)" % re.escape(loc),
                lambda m: m.group(1) + max(m.group(2), TODAY) + m.group(3), sm, count=1)

# ---- blog banner (shows while the Japan chip is selected)
BANNER = ('<div class="jp-hub-banner" id="jpHubBanner" hidden><b>Welcome to Japan.</b> Airports, stations, itineraries and Pocket Guides that work offline, all together. '
          '<a href="/japan">See every Japan guide &rarr;</a></div>\n'
          '<style>.jp-hub-banner{max-width:860px;margin:10px auto 6px;padding:12px 16px;background:#f0faf7;border-left:3px solid #00C9A7;border-radius:0 12px 12px 0;font-size:.98rem;line-height:1.5}'
          '.jp-hub-banner a{color:#0a8f78;font-weight:700;white-space:nowrap}</style>\n'
          "<script>(function(){var bar=document.getElementById('countryBar'),b=document.getElementById('jpHubBanner');if(!bar||!b)return;"
          "function sync(){var on=!bar.hidden&&!!bar.querySelector('.cty-btn.active[data-country=\"japan\"]');b.hidden=!on;}"
          "new MutationObserver(sync).observe(bar,{attributes:true,subtree:true,attributeFilter:['class','hidden']});sync();"
          # /blog?region=Asia&country=vietnam opens that region and country (links from the Japan hub's "somewhere else" row)
          "document.addEventListener('DOMContentLoaded',function(){var p=new URLSearchParams(location.search),r=p.get('region'),c=p.get('country');"
          "if(!r)return;var rb=document.querySelector('.filter-btn[data-region=\"'+r.replace(/[^A-Za-z ]/g,'')+'\"]');if(!rb)return;rb.click();"
          "if(c){var cb=document.querySelector('.cty-btn[data-country=\"'+c.replace(/[^a-z-]/g,'')+'\"]');if(cb)cb.click();}"
          "var f=document.querySelector('.filter-wrap')||rb;f.scrollIntoView({block:'start'});});"
          "})();</script>\n")
BANNER = "<!-- jp-hub-banner -->\n" + BANNER + "<!-- /jp-hub-banner -->\n"
_b = re.sub(r"<!-- jp-hub-banner -->\n.*?<!-- /jp-hub-banner -->\n", "", blog, flags=re.S)
_b = re.sub(r'<div class="jp-hub-banner" id="jpHubBanner".*?</script>\n', "", _b, flags=re.S)   # first version, no markers
m = re.search(r'<div class="country-bar" id="countryBar".*?</div>\n', _b, re.S)
if not m:
    die("country bar not found on blog.html")
_b = _b[:m.end()] + BANNER + _b[m.end():]
if _b != blog:
    blog = _b
    open(BLOG, "w", encoding="utf-8").write(blog)
    print("w73: banner updated on blog.html")

# ---- privacy policy: say what "Ask about Japan" does with a question (marker: id="ask-japan-privacy")
PRIV = os.path.join(PUB, "privacy-policy.html")
pv = open(PRIV, encoding="utf-8").read()
if 'id="ask-japan-privacy"' not in pv:
    a = '    <h3>Payment Information</h3>'
    if pv.count(a) != 1 or pv.count("<p>Last updated: November 22, 2026</p>") != 1:
        die("privacy policy anchors not found")
    pv = pv.replace(a, '    <h3 id="ask-japan-privacy">Questions to Packy</h3>\n'
                    '    <p>When you type a question into Packy, our Japan travel helper on our Japan page, the question is sent to Google\'s Gemini service, together with '
                    'the official-source notes it may answer from, to write the answer. We keep a log of the questions without your IP address, and with any '
                    'email address or phone number in the question removed, so we can see what travellers ask and improve our guides. Please do not type '
                    'personal details into it. We do not store the answers.</p>\n\n' + a, 1)
    pv = pv.replace("<p>Last updated: November 22, 2026</p>", "<p>Last updated: November 24, 2026</p>", 1)
    open(PRIV, "w", encoding="utf-8").write(pv)
    print("w73: privacy policy updated")

# ---- privacy policy: emails from Packy (marker: id="packy-email-privacy")
pv = open(PRIV, encoding="utf-8").read()
if 'id="packy-email-privacy"' not in pv:
    a = '    <h3>Payment Information</h3>'
    if pv.count(a) != 1:
        die("privacy policy anchor for Packy emails not found")
    pv = pv.replace(a, '    <h3 id="packy-email-privacy">Emails from Packy</h3>\n'
                    '    <p>If you ask Packy to email you your chat, we use your email address to send that one email from hello@packsmartapp.com, '
                    'and we keep a record of the request (your email address, the trip month if you chose one, and whether you said yes to trip tips) in our mailbox. '
                    'We send trip tips only if you said yes to them, and you can stop them at any time by replying "stop". '
                    'We do not sell or share your email address. If we move this list to an email service, it will be used for the same purpose only.</p>\n\n' + a, 1)
    open(PRIV, "w", encoding="utf-8").write(pv)
    print("w73: privacy policy: Packy emails")

# ---- privacy policy: the lucky cat's "Email me these words" uses the same Packy email (marker: packy-email-words, 26 Nov)
pv = open(PRIV, encoding="utf-8").read()
if "packy-email-words" not in pv and 'id="packy-email-privacy"' in pv:
    a = '<p>If you ask Packy to email you your chat, we use your email address to send that one email from hello@packsmartapp.com, '
    b = '<p><span id="packy-email-words"></span>If you ask Packy to email you your chat, or ask for the Japanese words from the lucky cat on our Japan page, we use your email address to send that one email from hello@packsmartapp.com, '
    if pv.count(a) != 1:
        die("privacy policy: Packy email sentence not found")
    pv = pv.replace(a, b, 1)
    pv = re.sub(r"<p>Last updated: [A-Za-z]+ \d+, 2026</p>", "<p>Last updated: November 26, 2026</p>", pv, count=1)
    open(PRIV, "w", encoding="utf-8").write(pv)
    print("w73: privacy policy: the cat's words email")

# ---- privacy policy: the trip-tips list is kept at MailerLite (marker: packy-email-mailerlite, 26 Nov)
pv = open(PRIV, encoding="utf-8").read()
if "packy-email-mailerlite" not in pv:
    a = ('We send trip tips only if you said yes to them, and you can stop them at any time by replying "stop". '
         'We do not sell or share your email address. If we move this list to an email service, it will be used for the same purpose only.')
    b = ('<span id="packy-email-mailerlite"></span>We send trip tips only if you said yes to them. When you say yes, we add your email address, '
         'your trip month (if you chose one), the destination, and a few topic tags based on what you asked Packy (for example "Shinkansen" or '
         '"Narita"; never your questions themselves) to MailerLite, the email service that sends our trip tips. You can stop them at any time '
         'with the unsubscribe link in every email, or by replying "stop". We do not sell your email address or share it with anyone else, and '
         'MailerLite uses it only to send our emails.')
    if pv.count(a) != 1:
        die("privacy policy: trip tips sentence not found")
    pv = pv.replace(a, b, 1)
    pv = re.sub(r"<p>Last updated: [A-Za-z]+ \d+, 2026</p>", "<p>Last updated: November 26, 2026</p>", pv, count=1)
    open(PRIV, "w", encoding="utf-8").write(pv)
    print("w73: privacy policy: MailerLite")

# ---- privacy policy: the remembered address and the "continue" link (marker: id="packy-email-remember", 25 Nov 2026)
if 'id="packy-email-remember"' not in pv:
    a = 'it will be used for the same purpose only.</p>\n'
    if pv.count(a) != 1:
        die("privacy policy anchor for the remembered Packy email not found")
    pv = pv.replace(a, a + '    <p id="packy-email-remember">So you can send an updated chat with one tap, Packy remembers the email address you used '
                    'in your own browser on that device (not on our servers); tap "Use another email" to make it forget it. '
                    'The "Continue this chat with Packy" button in the email carries your chat inside the link itself, '
                    'so the conversation is not stored on our servers.</p>\n', 1)
    open(PRIV, "w", encoding="utf-8").write(pv)
    print("w73: privacy policy: remembered Packy email")

if changed:
    open(OUT, "w", encoding="utf-8").write(page)
open(SITEMAP, "w", encoding="utf-8").write(sm)
print("w73 done. japan.html %s (%d plan, %d airport, %d station cards)." % (
    "written" if changed else "unchanged", len(PLAN), len(ARRIVE), len(STATIONS)))
