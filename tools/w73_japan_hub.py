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
.jp-ask-top{display:flex;align-items:center;gap:8px;margin:0 0 8px;font-size:.95rem;color:#0f0f23}
.jp-ask-top b{font-weight:800}
.jp-ask-kick{font-size:.68rem;font-weight:800;letter-spacing:.05em;text-transform:uppercase;background:#E6FAF5;color:#0a8f78;border-radius:999px;padding:2px 8px}
.jp-ask-form{display:flex;gap:8px;align-items:center;background:#F5F7F9;border:1.5px solid #E3E8EC;border-radius:14px;padding:4px 4px 4px 12px}
.jp-ask-form:focus-within{border-color:#00C9A7;background:#fff}
.jp-ask-form input{flex:1;min-width:0;font:inherit;font-size:1rem;border:0;background:transparent;padding:10px 0;color:#0f0f23;outline:none}
.jp-ask-form button{flex:none;font:inherit;font-weight:800;font-size:.95rem;background:#00C9A7;color:#fff;border:0;border-radius:11px;padding:0 18px;min-height:42px;cursor:pointer}
.jp-ask-form button[disabled]{opacity:.6;cursor:wait}
.jp-ask-try{display:flex;gap:6px;overflow-x:auto;-webkit-overflow-scrolling:touch;margin:8px 0 0;padding:2px 0;scrollbar-width:none}
.jp-ask-try::-webkit-scrollbar{display:none}
.jp-ask-try button{flex:none;font:inherit;font-size:.82rem;background:#fff;color:#3f4a5c;border:1px solid #E3E8EC;border-radius:999px;padding:5px 11px;min-height:32px;cursor:pointer;white-space:nowrap}
.jp-ask-try button:hover{border-color:#00C9A7;color:#0f0f23}
.jp-ask-out{margin-top:10px;background:#F8FBFA;border-radius:12px;padding:10px 12px;line-height:1.55;font-size:.95rem;color:#0f0f23}
.jp-ask-out p{margin:.25rem 0}.jp-ask-out ul{margin:.25rem 0 .25rem 1.1rem;padding:0}.jp-ask-out li{margin:.15rem 0}
.jp-ask-out a{color:#0a8f78;font-weight:700}
.jp-ask-out.busy{color:#5a6378}.jp-ask-out.err{background:#fff3f5}
.jp-ask-q{font-weight:700;margin-bottom:.4rem!important}
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

# ---- "Ask about Japan" (answers from /api/ask, which uses only official-source notes; see api/ask.js and w74)
ASK = """<!-- ask-japan-slot -->
<section class="jp-ask" id="ask" aria-label="Ask about Japan">
<div class="jp-ask-top"><span aria-hidden="true">&#128172;</span><b>Ask about Japan</b><span class="jp-ask-kick">Beta</span></div>
<form class="jp-ask-form" id="askForm" autocomplete="off">
<label for="askQ" class="jp-sr">Your question about travel in Japan</label>
<input id="askQ" type="text" maxlength="300" placeholder="e.g. How do I get from New Chitose Airport to Sapporo?">
<button type="submit" id="askBtn">Ask</button>
</form>
<div class="jp-ask-try" role="group" aria-label="Example questions">
<button type="button">New Chitose to Sapporo</button>
<button type="button">Ski bus to Niseko</button>
<button type="button">ATMs at Sapporo Station</button>
<button type="button">Ueno to Narita Airport</button>
</div>
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
  b.disabled=true; out.hidden=false; out.className='jp-ask-out busy'; out.innerHTML='<p>Checking the official sources&hellip;</p>';
  fetch('/api/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({q:text})})
   .then(function(r){return r.json().then(function(d){return [r.ok,d];});})
   .then(function(x){var ok=x[0],d=x[1];
     if(!ok||!d.ok){out.className='jp-ask-out err';out.innerHTML='<p>'+esc((d&&d.error)||'Sorry, something went wrong.')+'</p>';track('error');return;}
     out.className='jp-ask-out';
     out.innerHTML='<p class="jp-ask-q">'+esc(text)+'</p>'+fmt(d.answer)+(d.guide?'<p class="jp-ask-more">More in our <a href="'+esc(d.guide.url)+'">'+esc(d.guide.title)+'</a></p>':'');
     track('answered');})
   .catch(function(){out.className='jp-ask-out err';out.innerHTML='<p>No connection. Please try again when you are online.</p>';track('offline');})
   .then(function(){b.disabled=false;});
}
f.addEventListener('submit',function(e){e.preventDefault();ask(q.value);});
var EX={'New Chitose to Sapporo':'How do I get from New Chitose Airport to Sapporo?','Ski bus to Niseko':'Is there a ski bus from New Chitose Airport to Niseko?','ATMs at Sapporo Station':'Where are the ATMs at Sapporo Station?','Ueno to Narita Airport':'How do I get from Ueno to Narita Airport?'};
[].forEach.call(document.querySelectorAll('.jp-ask-try button'),function(btn){btn.addEventListener('click',function(){var t=EX[btn.textContent]||btn.textContent;q.value=t;ask(t);});});
})();
</script>"""

body = """<div class="page-wrapper">
    <div class="page-header">
        <h1>Welcome to <em style="font-family:var(--font-display);font-style:italic;">Japan</em></h1>
        <p>Every PackSmart guide for Japan in one place. Plan the trip, then save the free Pocket Guides for the airports and stations you will use: they work offline. Station and airport facts come from official sources, with the date we checked them.</p>
    </div>
    """ + OTHER + """
    """ + ASK + """
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
page = head + nav + body + foot
for need in ('id="plan"', 'id="arriving"', 'id="stations"', "hub_japan", "</html>"):
    if need not in page:
        die("built page lacks " + need)

old = open(OUT, encoding="utf-8").read() if os.path.isfile(OUT) else ""
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
    pv = pv.replace(a, '    <h3 id="ask-japan-privacy">Questions to "Ask about Japan"</h3>\n'
                    '    <p>When you type a question into "Ask about Japan" on our Japan page, the question is sent to Google\'s Gemini service, together with '
                    'the official-source notes it may answer from, to write the answer. We keep a log of the questions without your IP address, and with any '
                    'email address or phone number in the question removed, so we can see what travellers ask and improve our guides. Please do not type '
                    'personal details into it. We do not store the answers.</p>\n\n' + a, 1)
    pv = pv.replace("<p>Last updated: November 22, 2026</p>", "<p>Last updated: November 24, 2026</p>", 1)
    open(PRIV, "w", encoding="utf-8").write(pv)
    print("w73: privacy policy updated")

if changed:
    open(OUT, "w", encoding="utf-8").write(page)
open(SITEMAP, "w", encoding="utf-8").write(sm)
print("w73 done. japan.html %s (%d plan, %d airport, %d station cards)." % (
    "written" if changed else "unchanged", len(PLAN), len(ARRIVE), len(STATIONS)))
