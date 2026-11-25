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
import datetime, hashlib, os, re, sys

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
        "Tokyo, Kyoto, Osaka and Sapporo stations, and free offline Pocket Guides.")

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
.jp-other{display:flex;align-items:center;gap:10px;max-width:860px;margin:-.4rem auto 1.4rem;font-size:.92rem}
.jp-other>span{flex:none;font-weight:700;color:#0f0f23}
.jp-other-row{display:flex;gap:8px;overflow-x:auto;-webkit-overflow-scrolling:touch;padding:4px 2px;scrollbar-width:thin}
.jp-other-row a{flex:none;padding:7px 14px;min-height:38px;display:flex;align-items:center;border:1.5px solid #D5DCE0;border-radius:999px;background:#fff;color:#0f0f23;text-decoration:none;font-weight:600}
.jp-other-row a:hover{border-color:#00C9A7}
.jp-other-row a.all{border-color:#00C9A7;color:#0a8f78}
@media (max-width:600px){.jp-other{flex-direction:column;align-items:stretch;gap:6px}.jp-other>span{text-align:center}}
.jp-ask{max-width:760px;margin:0 auto 1.8rem;background:#fff;border:1.5px solid #BFEDE3;border-radius:18px;padding:14px 16px;box-shadow:0 2px 12px rgba(15,15,35,.05)}
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
OTHER = ('<nav class="jp-other" aria-label="Other destinations"><span>Going somewhere else?</span><div class="jp-other-row">'
         + "".join('<a href="/blog?region=%s&amp;country=%s">%s</a>' % (r.replace(" ", "%20"), c, n) for c, r, n in _ctys if c != "japan")
         + "".join('<a href="/blog?region=%s">%s</a>' % (r.replace(" ", "%20"), r) for r in ("Americas", "Middle East", "Pacific"))
         + '<a href="/blog" class="all">All destinations &rarr;</a></div></nav>')

# ---- Packy, "Ask about Japan" (answers from /api/ask, which uses only official-source notes; see api/ask.js and w74)
def packy_face():
    js = open(os.path.join(ROOT, "public", "packy.js"), encoding="utf-8").read()
    m = re.search(r"var FACE = ((?:'[^']*'\s*\+?\s*)+);", js)
    if not m:
        die("Packy's face (var FACE) not found in public/packy.js")
    return "".join(re.findall(r"'([^']*)'", m.group(1)))

ASK = """<!-- ask-japan-slot -->
<section class="jp-ask" id="ask" aria-label="Ask Packy, your Japan travel buddy">
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
.jp-hero{position:relative;overflow:hidden;border-radius:26px;margin:0 0 1.6rem;color:#0f0f23;background:linear-gradient(180deg,#FFE3E8 0%,#FFF1E6 60%,#FBF5EE 100%);box-shadow:0 14px 40px rgba(233,69,96,.12)}
.jp-scene{position:absolute;inset:0;pointer-events:none}
.jp-scene>svg{position:absolute;display:block}
.jp-scene .hills{left:0;right:0;bottom:0;width:100%;height:32%}
.jp-scene .art{right:0;bottom:0;width:48%;height:85%}
.jp-scene .sk{display:none}
.jp-scene .sk{position:absolute;left:-40px;top:-60px;width:250px;transform:rotate(-8deg)}.jp-scene .sk svg{width:100%;height:auto;display:block}
.jp-hero-in{position:relative;padding:2.2rem 2rem 1.4rem;max-width:980px;margin:0 auto}
.jp-hero-kick{display:inline-flex;align-items:center;gap:8px;font-size:.8rem;font-weight:800;letter-spacing:.12em;text-transform:uppercase;background:#fff;color:#0f0f23;border:1px solid #F3C6CF;border-radius:999px;padding:5px 12px}
.jp-hero h1{font-family:var(--font-display);font-size:3.6rem;line-height:1.02;margin:.6rem 0 .5rem;color:#0f0f23}
.jp-hero h1 em{font-style:italic;color:#E94560}
.jp-hero-lead{font-size:1.08rem;max-width:600px;color:#3f4a5c;margin:0 0 1rem}
.jp-hello{display:flex;align-items:center;gap:10px;background:none;border:0;padding:0;color:#0f0f23;font:inherit;cursor:pointer;text-align:left;margin:0 0 1.1rem}
.jp-hello .av{flex:none;width:48px;height:48px;background:#fff;border-radius:14px;padding:3px;box-shadow:0 6px 18px rgba(233,69,96,.2)}.jp-hello .av svg{width:100%;height:100%;display:block}
.jp-hello .bub{background:#fff;color:#0f0f23;border-radius:16px 16px 16px 4px;padding:9px 14px;font-weight:600;font-size:.95rem;box-shadow:0 6px 18px rgba(233,69,96,.15)}
.jp-hello .bub b{color:#E94560}
.jp-live{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 1.2rem}
.jp-live span{display:inline-flex;align-items:center;gap:6px;font-size:.86rem;font-weight:700;background:#fff;color:#0f0f23;border:1px solid #F0D9DD;border-radius:999px;padding:6px 12px}
.jp-live span[hidden]{display:none}
.jp-board{background:rgba(255,255,255,.88);border:1px solid #F3D3DA;border-radius:18px;padding:12px 12px 8px;box-shadow:0 14px 34px rgba(233,69,96,.14);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px)}
.jp-board-h{display:flex;align-items:center;justify-content:space-between;color:#E94560;font-weight:800;letter-spacing:.14em;font-size:.78rem;padding:2px 4px 8px}
.jp-board-h i{font-style:normal;color:#8a93a6;letter-spacing:.04em;font-weight:600}
.jp-board ol{list-style:none;margin:0;padding:0;display:grid;gap:6px}
.jp-board a{display:grid;grid-template-columns:1.2fr 1.2fr 1fr .8fr 18px;align-items:center;gap:8px;text-decoration:none;color:#0f0f23;background:#FFF8F4;border:1px solid #F6E3E6;border-radius:12px;padding:9px 12px;transition:background .15s,border-color .15s}
.jp-board a:hover,.jp-board a:focus-visible{background:#fff;border-color:#E94560}
.jp-board .f{position:relative;font-weight:800;font-size:.92rem;letter-spacing:.06em;font-variant-numeric:tabular-nums;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.jp-board .f.by{color:#5a6378}
.jp-board .f.t{justify-self:end;color:#C2185B;background:#FFE3E8;border-radius:999px;padding:3px 10px}
.jp-board .go{color:#E94560;font-weight:800}
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
@media (max-width:600px){
 .jp-hero{border-radius:20px;margin-left:-4px;margin-right:-4px}.jp-hero-in{padding:0 1rem 1rem}
 .jp-scene{position:relative;inset:auto;height:190px}.jp-scene .art{width:100%;height:100%}.jp-scene .hills{height:40%}
 .jp-scene .sk{display:block;width:130px;left:-24px;top:-34px}.jp-hero h1{font-size:2.6rem}.jp-hero-lead{font-size:.98rem}
 .jp-board a{grid-template-columns:1fr auto;grid-template-areas:"r t" "b t";row-gap:2px}
 .jp-board .f.fr{grid-area:r;white-space:normal}.jp-board .f.fr:after{content:" → " attr(data-to);color:#0f0f23}
 .jp-board .f.to{display:none}.jp-board .f.by{grid-area:b;font-size:.74rem;color:#5a6378}.jp-board .f.t{grid-area:t;font-size:1rem}.jp-board .go{display:none}
 .jp-board-h .wide{display:none}
 .jp-pass-code{font-size:2.2rem}.jp-pass-stub{width:104px;padding-left:14px}.jp-stamp{right:114px}
}
@media (prefers-reduced-motion:reduce){.jp-board .f{transition:none}}
"""

# Drawn dawn scene for the hero (25 Nov 2026, owner chose it over photos): sky, rising sun, Mt Fuji, pink hills, torii.
HILLS_SVG = ('<svg class="hills" viewBox="0 0 1600 600" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">'
    '<path d="M0 600V505C200 480 380 492 560 512S900 545 1120 518 1450 485 1600 498V600Z" fill="#F2D7DC"/>'
    '<path d="M0 600V550C250 532 500 545 760 560S1250 578 1600 552V600Z" fill="#E9C3CB"/>'
    '</svg>')
ART_SVG = ('<svg class="art" viewBox="940 100 660 500" preserveAspectRatio="xMaxYMax meet" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">'
    '<circle cx="1225" cy="200" r="84" fill="#E94560" opacity=".9"/>'
    '<path d="M955 600L1205 300C1218 284 1242 284 1255 300L1505 600Z" fill="#8FA2C0"/>'
    '<path d="M1205 300C1218 284 1242 284 1255 300L1297 352C1281 341 1270 359 1255 346 1242 359 1228 342 1215 355 1200 342 1188 357 1168 344Z" fill="#fff"/>'
    '<g transform="translate(1395 352) scale(.62)">'
    '<path d="M18 40C80 30 220 30 282 40L276 54C220 46 80 46 24 54Z" fill="#D7263D"/><rect x="30" y="54" width="240" height="10" fill="#3a2a2a"/>'
    '<rect x="50" y="80" width="200" height="14" fill="#D7263D"/><rect x="72" y="54" width="20" height="246" fill="#D7263D"/><rect x="208" y="54" width="20" height="246" fill="#D7263D"/>'
    '<rect x="66" y="288" width="32" height="14" fill="#3a2a2a"/><rect x="202" y="288" width="32" height="14" fill="#3a2a2a"/><rect x="138" y="62" width="24" height="32" fill="#3a2a2a"/></g>'
    '</svg>')

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
<div class="jp-scene" aria-hidden="true">""" + HILLS_SVG + ART_SVG + '<div class="sk">' + SAKURA_SVG + """</div></div>
<div class="jp-hero-in">
<span class="jp-hero-kick">🇯🇵 ようこそ · Yōkoso</span>
<h1 id="jpHeroT">Welcome to <em>Japan</em></h1>
<p class="jp-hero-lead">Every PackSmart guide for Japan in one place, from the arrivals gate to the platform. Facts come from official sources, with the date we checked them.</p>
<button type="button" class="jp-hello" id="jpHello"><span class="av" aria-hidden="true">""" + _face_av() + """</span><span class="bub"><b>Konnichiwa!</b> I'm Packy 👋 Where are you landing? Ask me anything.</span></button>
<div class="jp-live" aria-label="Japan right now"><span id="jpClock">🕗 Japan time</span><span id="jpWx" hidden></span><span id="jpSeason"></span></div>
<div class="jp-board" role="region" aria-label="Arrivals board: fastest trains from the airports">
<div class="jp-board-h"><span>ARRIVALS · 到着</span><i>Fastest trains<span class="wide"> · tap for the Pocket Guide</span></i></div>
<ol>""" + rows + """</ol>
<p class="jp-board-note">Journey times from Keisei, Keikyu (from Terminal 3), JNTO and Kyoto City, checked """ + BOARD_CHECKED.strftime("%-d %B %Y") + """. Times change, so check before you travel.</p>
</div>
</div>
</section>""")

def passes_html():
    cards = "".join(
        '<article class="jp-pass"><div class="jp-pass-main"><div class="jp-pass-top"><span>Arriving at</span></div>'
        '<div class="jp-pass-code">%s<small>✈</small></div><div class="jp-pass-name">%s</div><div class="jp-pass-serves">For %s</div>'
        '<p class="jp-pass-line">%s</p><button type="button" class="jp-pass-ask" data-q="%s">💬 Ask Packy about %s</button></div>'
        '<span class="jp-stamp" aria-hidden="true">確認<br>CHECKED</span>'
        '<div class="jp-pass-stub"><small>GATE</small><a href="/%s-pocket?src=hub_japan" data-pass="%s">📱 Pocket Guide</a><a class="g" href="/blog/%s">Airport guide</a></div></article>'
        % (code, name, serves, line, q, name.replace(" Airport", ""), pk, pk, slug)
        for code, name, serves, line, pk, slug, q in PASSES)
    return ("""<section aria-labelledby="jpPassT"><div class="jp-pass-h"><h2 id="jpPassT">Where are you landing?</h2><p>Pick your airport: the free Pocket Guide works offline at the gate, and Packy can answer the rest.</p></div>
<div class="jp-passes">""" + cards + """</div></section>""")

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
// Packy: the hello bubble and "Ask Packy about ..." on each boarding pass
function packy(q){if(window.Packy){if(q)window.Packy.ask(q);else window.Packy.open();}else{var a=document.getElementById('ask');if(a)a.scrollIntoView({behavior:'smooth'});}}
document.getElementById('jpHello').addEventListener('click',function(){track('hero_packy');packy('');});
[].forEach.call(document.querySelectorAll('.jp-pass-ask'),function(b){b.addEventListener('click',function(){track('pass_packy',b.getAttribute('data-q'));packy(b.getAttribute('data-q'));});});
[].forEach.call(document.querySelectorAll('[data-board]'),function(a){a.addEventListener('click',function(){track('board_tap',a.getAttribute('data-board'));});});
[].forEach.call(document.querySelectorAll('[data-pass]'),function(a){a.addEventListener('click',function(){track('pass_tap',a.getAttribute('data-pass'));});});
})();
</script>"""



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
            "%3Cg fill='none' stroke='%23E9C9C9' stroke-width='1.2' opacity='.55'%3E"
            "%3Cpath d='M0 40a20 20 0 0 1 40 0M8 40a12 12 0 0 1 24 0M16 40a4 4 0 0 1 8 0'/%3E"
            "%3Cpath d='M40 40a20 20 0 0 1 40 0M48 40a12 12 0 0 1 24 0M56 40a4 4 0 0 1 8 0'/%3E"
            "%3Cpath d='M-20 20a20 20 0 0 1 40 0M-12 20a12 12 0 0 1 24 0M-4 20a4 4 0 0 1 8 0'/%3E"
            "%3Cpath d='M20 20a20 20 0 0 1 40 0M28 20a12 12 0 0 1 24 0M36 20a4 4 0 0 1 8 0'/%3E"
            "%3Cpath d='M60 20a20 20 0 0 1 40 0M68 20a12 12 0 0 1 24 0M76 20a4 4 0 0 1 8 0'/%3E%3C/g%3E%3C/svg%3E\")")
HERO_CSS += """
:root{--bg:#FBF5EE;--pw:900px}
html,body{overflow-x:clip}
.jp-bg{display:none}
/* big screens: the hero photo runs edge to edge, and from 1500px the page itself is wider (4 boarding passes in a row,
   guide cards 3 across), so the space is used for content first and decoration second */
@media (min-width:1000px){
 .jp-hero{width:100vw;margin-left:calc(50% - 50vw);border-radius:0;box-shadow:none;margin-top:-1.5rem}
 .jp-hero-in{max-width:1200px;padding:3rem 2rem 1.8rem}
 .jp-hero h1{font-size:4.2rem}
 .jp-hero-in>*{max-width:640px}
}
@media (min-width:1500px){
 :root{--pw:1320px}
 .jp-hero-in>*{max-width:760px}
 .page-wrapper{max-width:1320px}
 .jp-passes{grid-template-columns:repeat(4,1fr)}
 .jp-pass{flex-direction:column}
 .jp-pass-stub{width:auto;flex-direction:row;align-items:center;padding:10px 12px;border-left:0;border-top:2px dashed rgba(255,255,255,.7)}
 .jp-pass-stub small{display:none}.jp-pass-stub a{flex:1}
 .jp-pass-stub:before,.jp-pass-stub:after{display:none}
 .jp-stamp{right:14px}
 .blog-grid{grid-template-columns:repeat(3,1fr)}
 .jp-ask,.jp-other{max-width:1000px}
}
@media (min-width:1200px){
 body{background:#FBF5EE """ + SEIGAIHA + """ fixed}
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
@media (prefers-reduced-motion:reduce){.jp-petal{display:none}}
"""

body = """<div class="page-wrapper">
    """ + hero_html() + """
    """ + passes_html() + """
    """ + HERO_JS + """
    """ + ASK + """
    """ + OTHER + """
""" + "    " + pocket + """
    <div class="filter-wrap te-filter" id="teFilter">
        <div class="filter-label" id="teFilterLabel">What do you need?</div>
        <div class="filter-bar" role="group" aria-labelledby="teFilterLabel">
            <a href="#all" class="filter-btn active" data-sec="all" aria-pressed="true">All <i class="cnt"></i></a>
            <a href="#plan" class="filter-btn" data-sec="plan" aria-pressed="false">Plan your trip <i class="cnt"></i></a>
            <a href="#arriving" class="filter-btn" data-sec="arriving" aria-pressed="false">Airports <i class="cnt"></i></a>
            <a href="#stations" class="filter-btn" data-sec="stations" aria-pressed="false">Stations <i class="cnt"></i></a>
        </div>
    </div>
""" + section("plan", "Plan your trip", "Visas, seasons, budget, packing and a 7-day route.", plan_cards) \
    + section("arriving", "Airports", "Landing in Japan: terminals, trains and buses into town, money and SIM cards. Each guide has a free Pocket Guide.", arrive_cards) \
    + section("stations", "Stations", "The big stations, side by side: exits, platforms, lockers and ATMs. Each guide has a free Pocket Guide.", station_cards) \
    + """    <div class="jp-two">
        """ + HOKKAIDO + """
        """ + SEASONS + """
    </div>
    <p class="te-back">Travelling from India? See our <a href="/blog/japan-travel-packing-guide-from-india">Japan guide for travellers from India</a>, with visa and cost details. Need help that is not about Japan? See <a href="/travel-essentials">Travel Essentials</a>.</p>
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
BANNER = ('<div class="jp-hub-banner" id="jpHubBanner" hidden><b>Welcome to Japan.</b> Airports, stations, itineraries and free offline Pocket Guides, all together. '
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
