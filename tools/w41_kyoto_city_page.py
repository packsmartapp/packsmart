#!/usr/bin/env python3
"""w41: Kyoto city guide (article only, no pocket guide).
Run from the repo root (~/packsmart):  python3 tools/w41_kyoto_city_page.py
Idempotent. Needs, in public/images: kyoto-travel-guide-hero.jpg (Pakutaso photo, 1600 px wide) and
kyoto-travel-guide-card-680.webp (card crop). Run AFTER w36 (page chrome is read from blog/osaka-station-guide.html),
w38 (Osaka guide link, blog card) and w39 (Japan guide link, sitemap entry).
Writes public/blog/kyoto-travel-guide.html, adds a link sentence to the Japan guide and the Osaka travel guide,
the sitemap entry and a card on blog.html. No prices are printed: they change by date and group size.
Klook partner links: fill the KLOOK dict (and the PLACEHOLDER facts) once Ari has generated them.
"""
import os, re, sys, json, html, urllib.parse

ROOT = os.getcwd()
PUB = os.path.join(ROOT, "public")
BLOG = os.path.join(PUB, "blog")
IMG = os.path.join(PUB, "images")
STATION = os.path.join(BLOG, "osaka-station-guide.html")
JAPAN = os.path.join(BLOG, "japan-travel-packing-guide.html")
SITEMAP = os.path.join(PUB, "sitemap.xml")
BLOGIDX = os.path.join(PUB, "blog.html")
SLUG = "kyoto-travel-guide"
OUT = os.path.join(BLOG, SLUG + ".html")
SITE = "https://www.packsmartapp.com"
URL = "%s/blog/%s" % (SITE, SLUG)
TODAY = "2026-11-19"
H1 = "Kyoto Travel Guide 2026: Private Guide, Tea Ceremony, Nara and Amanohashidate"
TITLE = "Kyoto Travel Guide 2026: Private Guide, Tea Ceremony, Nara and Amanohashidate | PackSmart"
DESC = ("Plain-English Kyoto travel guide: a private guide and car, a tea ceremony, day trips to Nara and to Amanohashidate "
        "and Ine, the main sights with opening times, and manners in Gion.")
KEYWORDS = ("Kyoto travel guide, Kyoto private guide with car, Kyoto tea ceremony, Kyoto to Nara day trip, Kyoto to Amanohashidate, "
            "Ine Funaya from Kyoto, things to do in Kyoto, Fushimi Inari, Kiyomizu-dera, Kinkaku-ji, Nijo Castle, Gion manners")
HERO = "/images/kyoto-travel-guide-hero.jpg"
GYG_PARTNER = "D7IXONS"


def die(msg):
    print("ABORT: " + msg)
    sys.exit(1)


for p in (STATION, JAPAN, SITEMAP, BLOGIDX):
    if not os.path.isfile(p):
        die("missing " + p + " (run from the repo root, after w36, w38 and w39)")
for f in ("kyoto-travel-guide-hero.jpg", "kyoto-travel-guide-card-680.webp"):
    if not os.path.isfile(os.path.join(IMG, f)):
        die("missing public/images/" + f)

st = open(STATION, encoding="utf-8").read()


# ------------------------------------------------------------------ chrome sliced from the Osaka station guide
def cut(s, a, b, incl_b=False):
    i = s.find(a)
    if i < 0:
        die("anchor not found: " + a[:60])
    j = s.find(b, i + len(a))
    if j < 0:
        die("end anchor not found: " + b[:60])
    return s[i:j + (len(b) if incl_b else 0)]


HEAD_A = cut(st, '    <link rel="preconnect" href="https://fonts.googleapis.com">', '<script type="application/ld+json">')
last_ld = st.rfind('<script type="application/ld+json">')
css_start = st.find("    <style>\n", last_ld)
if css_start < 0:
    die("site CSS block not found")
HEAD_B = st[css_start:st.index("</head>")]
if ".share-row" not in HEAD_B or ".related-grid" not in HEAD_B or ".hero-blog" not in HEAD_B:
    die("site CSS block looks wrong")
NAV = cut(st, '    <nav class="nav" id="nav">', "</nav>", True)
m = re.search(r'<p style="font-size:0\.82rem;color:#999;[^>]*>This article contains affiliate links.*?</p>', st, re.S)
if not m:
    die("affiliate disclosure paragraph not found")
DISCLOSURE = m.group(0)
SHARE = cut(st, '<div class="share-row">', "\n</div>", True)
OLD_T = "Osaka%20Station%20Guide%202026%3A%20Shin-Osaka%2C%20Osaka%2FUmeda%20and%20Getting%20Between%20Them"
if OLD_T not in SHARE or "osaka-station-guide" not in SHARE:
    die("share row not as expected")
NEW_T = urllib.parse.quote(H1, safe="")
SHARE = SHARE.replace(OLD_T, NEW_T).replace("osaka-station-guide", SLUG)
if "Station" in SHARE or "Shin-Osaka" in SHARE:
    die("share row still mentions the station guide")
TOC_CSS = cut(st, "<style>\nhtml{scroll-behavior:smooth}", "</style>", True)
TOC_CSS, n = re.subn(r"#one-page,#which-station[^{]*\{scroll-margin-top:var\(--psn-off,150px\)\}", "__SCROLL_MARGIN__", TOC_CSS)
if n != 1:
    die("scroll-margin rule not found in TOC CSS")
i = st.find("var bar=document.getElementById('psnBar')")
if i < 0:
    die("TOC script not found")
j0 = st.rfind("<script>", 0, i)
TOC_JS = st[j0:st.index("</script>", i) + len("</script>")]
FOOT = st[st.index('<footer class="footer">'):]
if not FOOT.rstrip().endswith("</html>"):
    die("footer chunk does not end with </html>")
if "psPocketBar" in FOOT:
    die("footer chunk contains the pocket bar")


def esc(s):
    return html.escape(s, quote=False)




# ------------------------------------------------------------------ page sections (Kyoto city guide)
SECTIONS = [
    # id, short chip label, full title, tile (emoji entity, title, sub) or None
    ("one-page", "On one page", "Kyoto on one page", None),
    ("areas", "Where things are", "Where things are in Kyoto", None),
    ("private-car", "Guide + car", "Private guide and car for the day", ("&#128663;", "Guide + car", "A driver for the day")),
    ("tea", "Tea + kimono", "Tea ceremony and kimono", ("&#127861;", "Tea + kimono", "In a traditional house")),
    ("day-trips", "Day trips", "Day trips from Kyoto", ("&#128646;", "Day trips", "Nara, Amanohashidate, Ine")),
    ("sights", "Sights", "The main sights in the city", ("&#9961;&#65039;", "City sights", "Fushimi Inari, Kiyomizu, more")),
    ("manners", "Manners", "Manners in Gion and at temples", ("&#128591;", "Manners", "Gion, photos, temples")),
    ("food", "Food", "What to eat", None),
    ("getting-around", "Getting around", "Getting to and around Kyoto", None),
    ("faq", "FAQ", "Frequently Asked Questions", None),
    ("about-this-guide", "About", "About this guide", None),
]

SCROLL_MARGIN = ",".join("#" + s[0] for s in SECTIONS) + "{scroll-margin-top:var(--psn-off,150px)}"

LOCAL_CSS = """<style>
.ps-card{background:#fff;border:2px solid #00C9A7;border-radius:14px;padding:22px 24px;margin:24px 0;}
.ps-card h2{margin-top:0!important;}
.ps-card ul{margin:0 0 6px 1.2rem;padding:0;}
.ps-card li{font-size:1.05rem;line-height:1.55;margin:0 0 9px;}
.ps-about{background:#f8f9fa;border-radius:12px;padding:16px 20px;margin:28px 0;font-size:0.95rem;line-height:1.6;}
.ps-about h2{margin:0 0 6px!important;font-size:1.15rem!important;}
.ps-about ul{margin:6px 0 0 1.2rem;padding:0;}
.ps-note{font-size:0.82rem;color:#777;line-height:1.5;margin:6px 0 18px;}
.ps-scroll{overflow-x:auto;-webkit-overflow-scrolling:touch;margin:0 0 20px;}
.ps-scroll table{min-width:560px;}
@media(max-width:600px){
  .ps-card{padding:16px;}
  .ps-scroll{overflow:visible;}
  .ps-scroll table{min-width:0;display:block;border:0;box-shadow:none;}
  .ps-scroll thead{display:none;}
  .ps-scroll tbody{display:block;}
  .ps-scroll tr{display:block;border:1px solid #E9ECEF;border-radius:10px;margin:0 0 12px;padding:6px 0;background:#fff;}
  .ps-scroll td{display:block;border:0!important;padding:5px 14px!important;font-size:1rem;}
  .ps-scroll td:first-child{font-size:1.08rem;padding-top:8px!important;}
  .ps-scroll td[data-label]:not(:first-child)::before{content:attr(data-label);display:block;font-size:0.72rem;font-weight:700;color:#00967d;text-transform:uppercase;letter-spacing:0.03em;}
}
.ps-exp{background:#f0faf7;border:1px solid #cdeee5;border-left:4px solid #00C9A7;border-radius:12px;padding:18px 20px;margin:18px 0;}
.ps-exp .tag{display:block;font-size:.74rem;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:#0a8f78;margin-bottom:4px;}
.ps-exp h3{margin:0 0 8px!important;font-size:1.12rem;}
.ps-exp ul{margin:0 0 12px 1.2rem;padding:0;}
.ps-exp li{margin:0 0 6px;font-size:.97rem;line-height:1.5;}
.ps-exp a.go{display:inline-block;font-weight:700;color:#0f0f23!important;background:#fff;border:2px solid #00C9A7;border-radius:10px;padding:11px 16px;text-decoration:none!important;min-height:44px;box-sizing:border-box;}
.ps-exp a.go:hover,.ps-exp a.go:focus-visible{background:#00C9A7;color:#fff!important;}
.ps-exp small{display:block;color:#777;font-size:.8rem;margin-top:8px;line-height:1.4;}
.ps-exp figure{margin:0 0 14px;}
.ps-exp figure img{display:block;width:100%;height:auto;aspect-ratio:12/5;max-height:200px;object-fit:cover;border-radius:8px;}
.ps-exp figcaption{font-size:.72rem;color:#777;line-height:1.35;margin-top:4px;}
.ps-exp figcaption a{color:#777!important;text-decoration:underline;}
.ps-gyg{margin:24px 0;font-family:"DM Sans",sans-serif}
.ps-gyg-h{display:block;text-align:center;font-size:1.05rem;font-weight:700;color:#0f0f23;margin:0 0 4px}
.ps-gyg-s{text-align:center;font-size:.85rem;color:#3f7f70;margin:0 0 14px}
.ps-gyg-w{min-height:495px;margin-bottom:-30px}
@media(max-width:600px){.ps-gyg-w{min-height:772px;margin-bottom:0}}
</style>"""

GYG_HEAD = ('<script async defer src="https://widget.getyourguide.com/dist/pa.umd.production.min.js" data-gyg-partner-id="%s"></script>\n'
            '<style>[data-gyg-widget]{overflow:hidden!important} [data-gyg-widget]>span{display:none!important} '
            '[data-gyg-widget] iframe{clip-path:inset(0 0 35px 0)!important;margin-bottom:-35px!important}</style>' % GYG_PARTNER)

GYG_TPL = """<div class="ps-gyg" data-ps-placement="__PID__">
<strong class="ps-gyg-h">__HEAD__</strong>
<p class="ps-gyg-s">__BLURB__</p>
<div class="ps-gyg-w"><div class="ps-gyg-slot" data-gyg-href="https://widget.getyourguide.com/default/activities.frame" data-gyg-locale-code="en-US" data-gyg-number-of-items="__N__" data-gyg-partner-id="__PARTNER__"></div></div>
<script>
(function(){
var root=document.currentScript.parentNode;
var ids='__IDS__',cmp='__CMP__';
var slot=root.querySelector('.ps-gyg-slot'),phone=window.matchMedia('(max-width:600px)'),started=false;
function render(){
var a=ids.split(',');
slot.setAttribute('data-gyg-widget','activities');
slot.setAttribute('data-gyg-number-of-items',String(phone.matches?Math.min(2,a.length):a.length));
slot.setAttribute('data-gyg-tour-ids',(phone.matches?a.slice(0,2):a).join(','));
slot.setAttribute('data-gyg-cmp',cmp);
var t=0;(function go(){if(window.GYG&&window.GYG.refresh){window.GYG.refresh()}else if(t++<50){setTimeout(go,200)}})();}
function start(){if(started)return;started=true;render();var n=0;(function watch(){if(slot.querySelector('iframe'))return;if(++n>15){root.style.display='none';return}setTimeout(watch,1000)})()}
if('IntersectionObserver' in window){var io=new IntersectionObserver(function(e){if(e[0].isIntersecting){io.disconnect();start()}},{rootMargin:'400px 0px'});io.observe(root)}else{start()}
if(phone.addEventListener){phone.addEventListener('change',function(){if(started)render()})}
})();
</script>
</div>"""


def gyg(pid, head, blurb, ids, cmp):
    return (GYG_TPL.replace("__PID__", pid).replace("__HEAD__", esc(head)).replace("__BLURB__", esc(blurb))
            .replace("__N__", str(len(ids))).replace("__PARTNER__", GYG_PARTNER)
            .replace("__IDS__", ",".join(ids)).replace("__CMP__", cmp))


# Klook partner links for this page. Empty until the links are generated in Travelpayouts (one Sub ID per placement).
# Placement id -> short link. A placement with no link prints nothing.
KLOOK = {
    "klook-kyoto-tour-temples": "https://klook.tpo.lu/K6lURAON",
    "klook-kyoto-dt-nara": "https://klook.tpo.lu/4h2G7ahB",
    "klook-kyoto-dt-amanohashidate": "https://klook.tpo.lu/9Met0OeS",
}


def exp(pid, tag, title, facts, label, note, img=None):
    link = KLOOK.get(pid, "")
    if not link:
        return ""
    if any("PLACEHOLDER" in x for x in facts) or "PLACEHOLDER" in note:
        die("Klook placement %s has a link but its facts are still PLACEHOLDER" % pid)
    lis = "\n".join("<li>%s</li>" % f for f in facts)
    fig = ""
    if img:
        fn, alt, credit = img
        if not os.path.isfile(os.path.join(IMG, fn)):
            die("missing public/images/" + fn)
        fig = ('\n<figure><a href="%s" target="_blank" rel="nofollow noopener sponsored" tabindex="-1" aria-hidden="true">'
               '<img src="/images/%s" alt="%s" width="1200" height="500" loading="lazy" decoding="async"></a>'
               '<figcaption>%s</figcaption></figure>' % (link, fn, alt, credit))
    return ('\n<div class="ps-exp" data-ps-placement="%s">%s\n<span class="tag">%s</span>\n<h3>%s</h3>\n<ul>\n%s\n</ul>\n'
            '<a class="go" href="%s" target="_blank" rel="nofollow noopener sponsored">%s</a>\n<small>%s</small>\n</div>'
            % (pid, fig, tag, title, lis, link, label, note))


def official(url, label):
    return '<a href="%s" target="_blank" rel="noopener">%s</a>' % (url, label)


# ---- 1. one page
ONE_PAGE = """<div class="ps-card" id="one-page">
<h2>Kyoto on one page</h2>
<ul>
<li><strong>Spread out:</strong> Kyoto Station is in the south. Higashiyama and Gion (Kiyomizu-dera) are in the east, Fushimi Inari in the south-east, Arashiyama in the west, and Kinkaku-ji in the north. Plan one or two areas a day.</li>
<li><strong>Quick trains:</strong> Fushimi Inari is 5 minutes from Kyoto Station on the JR Nara Line. Saga-Arashiyama is about 11 minutes by Rapid on the JR Sagano Line. Nara is about 35 to 45 minutes.</li>
<li><strong>Long day trip:</strong> Amanohashidate is about 2 to 2.5 hours each way, and Ine is about another hour by bus. Most visitors book a tour for it.</li>
<li><strong>Closing times:</strong> Most big temples close around 17:00. Ginkaku-ji shortens its hours from 1 December. Kiyomizu-dera stays open late from 21 to 30 November 2026.</li>
<li><strong>Manners:</strong> Do not photograph geiko and maiko without permission, and do not eat while walking in Nishiki Market.</li>
<li><strong>Arriving?</strong> See our <a href="/blog/kyoto-station-guide">Kyoto Station guide</a> if you come by train, or our <a href="/blog/kansai-airport-guide">Kansai Airport guide</a> if you fly in.</li>
</ul>
</div>"""

INTRO = """<p>Kyoto is the easiest city in Japan to love and one of the hardest to plan, because the sights are spread over a wide area and many close at 17:00. This guide starts with the options that save the most effort: a private guide and car for the day, and a tea ceremony in a townhouse. It then covers the day trips people ask about most (Nara, and Amanohashidate with Ine Funaya), the main sights with their opening times, manners, food and getting around. Facts come from official tourism, temple and castle sites, checked on 19 November 2026. We print no prices, because they change by date and group size.</p>"""

# ---- 2. areas
AREAS = """<h2 id="areas">Where things are in Kyoto</h2>
<p>Kyoto is easier to plan once you split it into areas. Pick one or two per day and keep the rest for another day.</p>
<div class="ps-scroll"><table class="checklist-table">
<thead><tr><th>Area</th><th>Known for</th><th>Getting there</th></tr></thead>
<tbody>
<tr><td><strong>Kyoto Station</strong></td><td data-label="Known for">The main hub: bullet trains, JR lines, the Haruka to Kansai Airport, the subway and the city buses.</td><td data-label="Getting there">See our <a href="/blog/kyoto-station-guide">Kyoto Station guide</a>.</td></tr>
<tr><td><strong>Higashiyama and Gion</strong></td><td data-label="Known for">Kiyomizu-dera, the Yasaka Pagoda, the old lanes of Ninenzaka and Sannenzaka, and the Gion entertainment district.</td><td data-label="Getting there">Kyoto's tourism site gives a 25-minute walk to Kiyomizu-dera from Keihan Kiyomizu-Gojo Station. City buses also run to the area.</td></tr>
<tr><td><strong>Fushimi Inari</strong></td><td data-label="Known for">The shrine and its tunnels of red torii gates up Mount Inari.</td><td data-label="Getting there">5 minutes from Kyoto Station to JR Inari Station on the JR Nara Line, then a 3-minute walk.</td></tr>
<tr><td><strong>Arashiyama</strong></td><td data-label="Known for">The bamboo grove, Tenryu-ji and the Togetsukyo Bridge.</td><td data-label="Getting there">JR Sagano Line from Kyoto Station to Saga-Arashiyama, about 11 minutes by Rapid.</td></tr>
<tr><td><strong>Central Kyoto</strong></td><td data-label="Known for">Nijo Castle, Nishiki Market and the Shijo shopping streets.</td><td data-label="Getting there">City buses and the subway. Nishiki Market is a 400-metre covered street between Teramachi and Takakura.</td></tr>
<tr><td><strong>North Kyoto</strong></td><td data-label="Known for">Kinkaku-ji (the Golden Pavilion), and Ginkaku-ji (the Silver Pavilion) in the north-east.</td><td data-label="Getting there">City buses. For Kinkaku-ji, get off at Kinkakuji-mae or Kinkakuji-michi.</td></tr>
</tbody></table></div>"""

# ---- 3. private guide and car
CAR = ("""<h2 id="private-car">Private guide and car for the day</h2>
<p>A private driver-guide suits families, small groups and anyone short of time, because Kyoto's sights are far apart and the buses fill up. Listings differ a lot, so check four things before you book: the language of the guide, the list of stops, whether entrance fees are included, and where pick-up happens. On the listings we read on 19 November 2026, days run 9 to 10 hours, usually cover Fushimi Inari, Kiyomizu-dera, Arashiyama and Gion, and some add Kinkaku-ji, Nishiki Market or Nara. Entrance fees at paid sights such as Kiyomizu-dera and Kinkaku-ji were marked as extra on at least one listing.</p>
""" + gyg("gyg-kyoto-private", "Private days in Kyoto with a guide and vehicle",
          "Private days with a guide and vehicle. Pick-up rules differ, so read each one.",
          ["1112520", "1025571", "672799"], "packsmart-kyoto-private") + """
<p><strong>Pick-up:</strong> one listing we saw offers pick-up from hotels and apartments only, not from stations or airports, while another meets you at the Central Exit of Kyoto Station. Confirm the meeting point before you pay.</p>""" +
       exp("klook-kyoto-tour-temples", "Guided day tour", "Fushimi Inari, Arashiyama and Kiyomizu-dera from Kyoto",
           ["A one-day group tour that starts at Kyoto Station, by train and then bus, with an English and Japanese guide.",
            "Stops on the listing: Fushimi Inari, Kiyomizu-dera, Kinkaku-ji and Arashiyama, with an optional Japanese lunch.",
            "The listing offers real-time voice and text translation in up to 75 languages. Bring your own earphones."],
           "See dates and options (partner link)",
           "Rated 4.6 from about 342 reviews on the booking page, 20 November 2026.",
           img=("kyoto-box-arashiyama.webp", "A path through the Arashiyama bamboo grove in Kyoto, with tall bamboo on both sides",
                "Photo: Pakutaso")))

# ---- 4. tea ceremony and kimono
TEA = ("""<h2 id="tea">Tea ceremony and kimono</h2>
<p>A tea ceremony is one of the easiest ways to slow down in Kyoto and sit inside a traditional house. The listings we read are short, usually 45 to 60 minutes. You watch the host prepare matcha, learn the basic etiquette, and whisk a bowl yourself, with a seasonal sweet. Several are in townhouses in the Higashiyama area near Ninenzaka and Sannenzaka, a short walk from Kiyomizu-dera, so they fit well before or after the temple.</p>
""" + gyg("gyg-kyoto-tea", "Tea ceremony experiences in Kyoto",
          "Short sessions in traditional townhouses, in English.", ["441136", "441138", "60894"], "packsmart-kyoto-tea") + """
<ul>
<li><strong>Kimono add-on:</strong> some tea ceremonies offer a kimono option, and the listing we read asks you to arrive 20 minutes early if you add it. Kimono and tea packages run 1.5 to 2 hours.</li>
<li><strong>Dress code:</strong> the same listing says there is none for the plain tea ceremony.</li>
<li><strong>Private or small group:</strong> several listings offer a private session, which suits families.</li>
</ul>""")

# ---- 5. day trips
DAYTRIPS = ("""<h2 id="day-trips">Day trips from Kyoto</h2>
<p>Two day trips come up most often. Nara is short and easy by train. Amanohashidate and Ine Funaya on the Sea of Japan coast are much farther, and most visitors book a tour for them.</p>
<div class="ps-scroll"><table class="checklist-table">
<thead><tr><th>Place</th><th>From Kyoto Station</th><th>Good to know</th></tr></thead>
<tbody>
<tr><td><strong>Nara</strong></td><td data-label="From Kyoto Station">JR Rapid to JR Nara Station, about 41 minutes. Kintetsu Limited Express to Kintetsu-Nara, about 34 minutes.</td><td data-label="Good to know">Todai-ji and the deer in Nara Park. Take the Rapid, not the local train, which is about 25 minutes slower.</td></tr>
<tr><td><strong>Amanohashidate</strong></td><td data-label="From Kyoto Station">Hashidate Limited Express, about 2 to 2.5 hours. An express bus from Kyoto Station takes about 2 hours.</td><td data-label="Good to know">A pine-covered sandbar and one of Japan's three scenic views. The limited express has reserved seats, so check the timetable and booking rules.</td></tr>
<tr><td><strong>Ine Funaya</strong></td><td data-label="From Kyoto Station">Train to Amanohashidate, then a local bus of about 60 minutes, roughly once an hour.</td><td data-label="Good to know">A fishing village of boat houses built at the water's edge. Remote: reached only by bus or car.</td></tr>
</tbody></table></div>

<h3>Nara: Todai-ji and the deer</h3>
<p>Nara is about 35 to 45 minutes from Kyoto, depending on the train. JR Nara and Kintetsu-Nara are different stations, and Visit Nara gives a 22-minute walk from Kintetsu-Nara to Todai-ji. The Great Buddha Hall opens 8:00 to 17:00 from November to March, and 7:30 to 17:30 from April to October, with an entrance fee. Todai-ji's own site calls it the largest wooden building in the world. Visit Nara says about 1,400 wild deer live around Nara Park. They are protected as natural monuments, and the special deer crackers (shika senbei) sold in the park are the only food you may give them. If you have no food, show your empty hands and they usually leave you alone. Read the """ + official("https://www.visitnara.jp/venues/S01487/", "official Nara deer page") + """ before you go.</p>
""" + gyg("gyg-kyoto-nara-bus", "Nara, Fushimi Inari and Arashiyama day tours",
          "Bus tours that start in Kyoto or Osaka and end in either.", ["851858", "179654"], "packsmart-kyoto-nara") +
       exp("klook-kyoto-dt-nara", "Guided day tour", "Nara and Kyoto highlights",
           ["A group bus tour of 10 to 11 hours, with an English or Mandarin guide.",
            "Stops on the listing: Fushimi Inari, Kinkaku-ji, Arashiyama, and Nara with Todai-ji and the deer.",
            "It leaves from Kyoto or Osaka. Lunch is not included unless you pick a meal option."],
           "See dates and options (partner link)",
           "Rated 4.4 from about 3,800 reviews on the booking page, 20 November 2026.",
           img=("kyoto-box-nara.webp", "Sika deer grazing and resting on the lawn in Nara Park, with a tiled-roof building behind",
                "Photo: Pakutaso")) + """

<h3>Amanohashidate and Ine Funaya</h3>
<p>Amanohashidate is a pine-covered sandbar across Miyazu Bay in northern Kyoto Prefecture. JNTO calls it one of Japan's three scenic views, with Matsushima and Miyajima. The sandbar is 3.6 kilometres long, 20 metres wide at the narrowest point and 170 metres at the widest. From Amanohashidate Station it is about 6 minutes on foot to the sandbar and 12 minutes to the Amanohashidate Viewland lookout.</p>
<p>Ine is a small fishing town of about 1,900 people on Ine Bay, known for its funaya, boat houses built at the water's edge. JNTO says it can be reached only by car or by bus from Amanohashidate Station, about 60 minutes, roughly once an hour. The bus company Tango Kairiku Kotsu also lists a limited-time sightseeing express between Miyazu or Amanohashidate and Ine that needs no reservation, so check its """ + official("https://www.tankai.jp/lp/ineex_en/", "timetable page") + """ for dates.</p>
<p>By public transport the train alone is 4 to 5 hours round trip to Amanohashidate, plus about 2 hours by bus to Ine and back, which is why many visitors choose a tour. The day tours we read run about 10 hours, with about 2 to 2.5 hours each way by van or bus. Some also stop at Miyama Kayabuki-no-Sato, a village of thatched-roof farmhouses, and many add the Ine Bay cruise or the cable car at Amanohashidate for an extra fee.</p>
""" + gyg("gyg-kyoto-amanohashidate", "Amanohashidate and Ine Funaya day tours",
          "From Kyoto or Osaka. Check the pick-up point and what the cruise or cable car adds.",
          ["1041256", "1169216", "768701"], "packsmart-kyoto-amanohashidate") +
       exp("klook-kyoto-dt-amanohashidate", "Guided day tour", "Amanohashidate and Ine Funaya",
           ["About 10 hours by dedicated bus, with Amanohashidate, Ine Funaya and Miyama Thatched Village on the listing.",
            "Two packages: board and finish in Kyoto, or board in Kyoto and finish in Osaka.",
            "Tour staff speak Chinese, English and Japanese."],
           "See dates and options (partner link)",
           "Rated 4.8 from about 1,400 reviews on the booking page, 20 November 2026.",
           img=("kyoto-box-ine.webp", "Wooden funaya boat houses at the water's edge in Ine, northern Kyoto Prefecture",
                'Photo: <a href="https://commons.wikimedia.org/wiki/File:Funaya_in_Ine_Town,_Yosa_District,_Kyoto_Prefecture_003.jpg" target="_blank" rel="noopener">Naokijp</a>, '
                '<a href="https://creativecommons.org/licenses/by-sa/4.0/" target="_blank" rel="noopener">CC BY-SA 4.0</a>, cropped, via Wikimedia Commons')))

# ---- 6. sights
SIGHTS = ("""<h2 id="sights">The main sights in the city</h2>
<p>Opening times below are from each site's own pages on 19 November 2026. Temples change hours for events and seasons, so check the site for your date.</p>
<h3>Fushimi Inari Taisha</h3>
<p>Entry is free, and JNTO says you can visit at any time of day. The path up Mount Inari is lined with about 10,000 torii gates, and JNTO gives 2 to 3 hours for the full walk. It suggests going early, when fewer people are around, or after dark when the shrine is lit up. From JR Inari Station it is a 3-minute walk to the shrine.</p>
<h3>Kiyomizu-dera</h3>
<p>The temple opens at 6:00. In 2026 it closes at 18:00 for most of the year, and at 18:30 in July and August. The autumn special night viewing runs from 21 to 30 November 2026, with the temple open until 21:30 and last entry at 21:00, and no reservation is needed. The Jojuin garden is also open specially on those dates. An entrance fee applies. Read the """ + official("https://www.kiyomizudera.or.jp/en/visit/", "temple's own schedule") + """ before you go.</p>
<h3>Kinkaku-ji (the Golden Pavilion)</h3>
<p>Kinkaku-ji, officially Rokuon-ji, is open 9:00 to 17:00 all year, although hours may change for special exhibitions. UNESCO listed it in 1994. A monk burned the pavilion in 1950 and it was rebuilt in 1955. The path is wheelchair accessible up to the pavilion, but the garden beyond has steps. See the """ + official("https://www.shokoku-ji.jp/en/kinkakuji/access/", "temple's access page") + """.</p>
<h3>Ginkaku-ji (the Silver Pavilion)</h3>
<p>Hours are 8:30 to 17:00 from 1 March to 30 November, and 9:00 to 16:30 from 1 December to the end of February. Normally only the gardens can be visited, not the buildings.</p>
<h3>Nijo Castle</h3>
<p>The castle grounds open at 8:45, with last entry at 16:00 and closing at 17:00. Ninomaru Palace admits visitors until 16:10. The castle is closed 29 to 31 December. Ninomaru Palace is also closed every Tuesday in December, from 26 to 28 December, and from 1 to 3 January. On Sunday 6 December 2026, a commemorative event marks 400 years since the Imperial visit of 1626, and last admission is brought forward to 12:00 for the grounds and 12:10 for Ninomaru Palace. See the """ + official("https://nijo-jocastle.city.kyoto.lg.jp/guide/annai/?lang=en", "castle's hours page") + """.</p>
<h3>Arashiyama</h3>
<p>Arashiyama is the western district known for the bamboo grove, Tenryu-ji and the Togetsukyo Bridge. From Kyoto Station it is about 11 minutes by Rapid on the JR Sagano Line. Kyoto City's visitor guidelines include a request to protect the bamboo, and Kyoto's tourism site lists Arashiyama among the busy areas where you should not block the road.</p>
<h3>Nishiki Market</h3>
<p>Nishiki Market is a 400-metre street between Teramachi and Takakura, known as the Kitchen of Kyoto. Eating while walking through it is prohibited. Eat at the shop where you bought the food, or in the eating areas.</p>""")

# ---- 7. manners
MANNERS = """<h2 id="manners">Manners in Gion and at temples</h2>
<p>Kyoto's tourism site asks visitors to follow a few rules, mostly because people live in the busiest areas.</p>
<ul>
<li><strong>Geiko and maiko:</strong> do not stop, touch, follow or photograph them without permission. A maiko walking in the street usually has an appointment and is in a hurry.</li>
<li><strong>Photography:</strong> it is prohibited in many Gion areas, including some private alleys, in parts of shrines and temples, and in some restaurants. Hanamikoji and Gion-Shirakawa are residential areas, so do not photograph residents.</li>
<li><strong>Do not enter private property:</strong> the residents of southern Gion ask visitors to stay out of places other than shops and roads.</li>
<li><strong>Do not block the road:</strong> Kiyomizudera Monzen, Nishiki Market and Arashiyama are busy, so step aside to take photos.</li>
<li><strong>Eating and smoking:</strong> do not eat or smoke while walking on Hanamikoji. Smoking on the street is banned in Kyoto outside designated areas, and Kyoto Station, Kiyomizu and Gion are non-smoking areas.</li>
<li><strong>Drones:</strong> most of Kyoto City is a densely populated area where drone flying is prohibited under Japan's Civil Aeronautics Act.</li>
</ul>
<p>The rules are on Kyoto's """ + official("https://kyoto.travel/en/responsible-travel/", "responsible travel page") + """.</p>"""

# ---- 8. food
FOOD = """<h2 id="food">What to eat</h2>
<p>Kyoto was the imperial capital for more than 1,200 years, and its food shows it. JNTO and Kyoto's tourism site point to these first:</p>
<ul>
<li><strong>Kyo-kaiseki:</strong> a multi-course meal of seasonal ingredients, carefully prepared. Book ahead for dinner.</li>
<li><strong>Yudofu and yuba:</strong> simmered tofu and tofu skin. Kyoto's tourism site lists several yudofu restaurants, including one at the Nanzen-ji gate.</li>
<li><strong>Obanzai:</strong> everyday Kyoto home cooking with local vegetables. Many small restaurants change the dishes daily.</li>
<li><strong>Shojin ryori:</strong> the vegetarian meal of Buddhist temples.</li>
<li><strong>Nishiki Market:</strong> shops for rolled omelettes, hamo tempura, namafu and more. Remember the rule about eating at the shop.</li>
</ul>
<p>In Kyoto it is polite to start an evening with a glass of sake, according to Kyoto's tourism site.</p>"""

# ---- 9. getting around
AROUND = """<h2 id="getting-around">Getting to and around Kyoto</h2>
<ul>
<li><strong>By bullet train:</strong> you arrive at Kyoto Station. Our <a href="/blog/kyoto-station-guide">Kyoto Station guide</a> explains the Central and Hachijo sides, the platforms and the buses.</li>
<li><strong>By plane:</strong> most international flights use Kansai Airport, and the JR Haruka reaches Kyoto Station. See our <a href="/blog/kansai-airport-guide">Kansai Airport guide</a>.</li>
<li><strong>Trains to the sights:</strong> Fushimi Inari is 5 minutes on the JR Nara Line. Arashiyama is about 11 minutes on the JR Sagano Line. Nara is 35 to 45 minutes.</li>
<li><strong>City buses:</strong> they reach Kinkaku-ji, Ginkaku-ji and the Higashiyama area. Kyoto City says they accept cash and IC cards such as ICOCA, Suica and PiTaPa, as well as the 1-day pass.</li>
<li><strong>Subway:</strong> the Karasuma Line runs north to south underground from Kyoto Station.</li>
<li><strong>On foot:</strong> Higashiyama and Gion are best explored on foot. Allow more time for slopes and steps at Kiyomizu-dera and Fushimi Inari.</li>
</ul>"""

# ---- FAQ
FAQ = [
    ("How do I get from Kyoto to Nara?",
     "Visit Nara gives about 41 minutes by JR Rapid from Kyoto Station to JR Nara Station, and about 34 minutes by Kintetsu Limited Express to Kintetsu-Nara. The Kintetsu train needs a limited express ticket. Make sure you take the Rapid, because JNTO says the local train takes about 25 minutes longer."),
    ("How long does it take to reach Amanohashidate and Ine from Kyoto?",
     "JNTO gives about 2 to 2.5 hours by Hashidate Limited Express from Kyoto Station to Amanohashidate Station. A bus from Amanohashidate Station to Ine takes about 60 minutes and runs roughly once an hour. Day tours from Kyoto run about 10 hours in total."),
    ("What time does Fushimi Inari close?",
     "Fushimi Inari Taisha can be visited at any time of day, and entry is free, according to JNTO and Kyoto's tourism site. The full walk up the mountain takes 2 to 3 hours."),
    ("Is Kiyomizu-dera open in the evening in November 2026?",
     "Yes, during the autumn special night viewing from 21 to 30 November 2026. The temple stays open until 21:30, with last entry at 21:00, and no reservation is needed. For most of the rest of 2026 it closes at 18:00."),
    ("What are the opening hours of Kinkaku-ji, Ginkaku-ji and Nijo Castle?",
     "Kinkaku-ji is open 9:00 to 17:00 all year. Ginkaku-ji is open 8:30 to 17:00 until 30 November, then 9:00 to 16:30 from 1 December. The grounds of Nijo Castle open at 8:45, with last entry at 16:00 and closing at 17:00, and the castle is closed 29 to 31 December. Last admission is at 12:00 on Sunday 6 December 2026."),
    ("Can I photograph geiko and maiko in Gion?",
     "Not without permission. Kyoto's tourism site asks visitors not to stop, touch, follow or photograph geiko and maiko, and photography is prohibited in many Gion areas, including some private alleys."),
    ("What does a private guide and car in Kyoto include?",
     "On the listings we read on 19 November 2026, the vehicle and driver-guide are included, days run 9 to 10 hours, and entrance fees at paid sights can be extra. Languages and pick-up points differ by listing, and one listing offers hotel pick-up only, not stations."),
]


def faq_html():
    out = ['<h2 id="faq">Frequently Asked Questions</h2>']
    for q, a in FAQ:
        out.append("<h3>%s</h3>\n<p>%s</p>" % (esc(q), esc(a)))
    return "\n".join(out)


ABOUT = """<div class="ps-about" id="about-this-guide">
<h2>About this guide</h2>
<p>Written by PackSmart. Facts were checked on 19 November 2026 against """ + ", ".join([
    official("https://kyoto.travel/en/", "Kyoto's official tourism site (DMO KYOTO)"),
    official("https://www.japan.travel/en/", "the Japan National Tourism Organization (JNTO)"),
    official("https://www.kiyomizudera.or.jp/en/", "Kiyomizu-dera"),
    official("https://www.shokoku-ji.jp/en/", "Shokoku-ji (Kinkaku-ji and Ginkaku-ji)"),
    official("https://nijo-jocastle.city.kyoto.lg.jp/?lang=en", "Nijo Castle"),
    official("https://www.todaiji.or.jp/en/", "Todai-ji"),
    official("https://www.visitnara.jp/", "Visit Nara"),
    official("https://www.tankai.jp/en/", "Tango Kairiku Kotsu")]) + """. We print no prices, because they change by date and group size. Descriptions of tours and experiences come from the booking pages we read on 19 November 2026 and can change. Some of the links in this guide are partner links, marked as such. If a fact has changed, please <a href="/contact">tell us</a>.</p>
<ul>
<li><strong>19 Nov 2026:</strong> first version.</li>
</ul>
</div>"""


def card(title, text, slug, tag):
    return ('        <div class="related-card">\n            <div class="related-card-body">\n                <h4>%s</h4>\n                <p>%s</p>\n'
            '                <a href="https://www.packsmartapp.com/blog/%s">Read More <span class="related-arrow">&rarr;</span></a>\n'
            '                <div class="related-tag">%s</div>\n            </div>\n        </div>\n' % (title, text, slug, tag))


RELATED = ('<div class="related-posts">\n    <h3>Related Guides</h3>\n    <div class="related-grid">\n'
           + card("Kyoto Station Guide 2026", "Central or Hachijo side? Platforms, buses, subway, luggage and the way to Nara and Fushimi Inari.", "kyoto-station-guide", "Station Guide")
           + card("Osaka Travel Guide 2026", "A private car, Kobe beef and sake tours, a sumo show and day trips from Osaka.", "osaka-travel-guide", "Destination Guide")
           + card("Japan Travel and Packing Guide 2026", "What to pack, rail passes, etiquette and a budget breakdown for Tokyo, Kyoto and Osaka.", "japan-travel-packing-guide", "Destination Guide")
           + "    </div>\n</div>")



# ------------------------------------------------------------------ contents tiles, list and chip bar
def toc_html():
    tiles = "".join('<a class="psn-tile" href="#%s" data-psn="tile-%s"><span class="em">%s</span><b>%s</b><small>%s</small></a>'
                    % (sid, sid, t[0], t[1], t[2]) for sid, _, _, t in SECTIONS if t)
    lis = "".join('<li><a href="#%s" data-psn="list-%s">%s</a></li>' % (sid, sid, esc(full)) for sid, _, full, _ in SECTIONS)
    chips = "".join('<a class="chip" href="#%s" data-id="%s" data-psn="chip-%s">%s</a>' % (sid, sid, sid, esc(short)) for sid, short, _, _ in SECTIONS)
    now = ('<div class="psn-now" id="contents"><h3>What do you need first?</h3><p class="psn-sub">Tap a card to jump straight there.</p>'
           '<div class="psn-tiles">%s</div>\n<details><summary>See all %d sections</summary><ol>%s</ol></details></div>\n' % (tiles, len(SECTIONS), lis))
    bar = ('<div id="psnBar" role="navigation" aria-label="Jump to a section"><div class="in"><button type="button" class="up" '
           'aria-label="Back to the top of the page" data-psn="up">&uarr;</button><div class="rail">%s</div></div></div>' % chips)
    return now + bar


# ------------------------------------------------------------------ JSON-LD
def ld(obj):
    return '<script type="application/ld+json">\n' + json.dumps(obj, ensure_ascii=False) + "\n</script>"


LD = "\n".join([
    ld({"@context": "https://schema.org", "@type": "Article", "headline": H1, "description": DESC,
        "image": SITE + HERO, "datePublished": TODAY, "dateModified": TODAY,
        "author": {"@type": "Organization", "name": "PackSmart"},
        "publisher": {"@type": "Organization", "name": "PackSmart", "logo": {"@type": "ImageObject", "url": SITE + "/logo.png"}},
        "mainEntityOfPage": URL}),
    ld({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE},
        {"@type": "ListItem", "position": 2, "name": "Destinations", "item": SITE + "/blog"},
        {"@type": "ListItem", "position": 3, "name": "Kyoto Travel Guide", "item": URL}]}),
    ld({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}),
])

META = """<title>%s</title>
    <meta name="description" content="%s">
    <meta name="keywords" content="%s">
    <link rel="canonical" href="%s">
    <meta property="og:title" content="%s">
    <meta property="og:description" content="%s">
    <meta property="og:url" content="%s">
    <meta property="og:type" content="article">
    <meta property="og:site_name" content="PackSmart">
    <meta property="og:image" content="%s">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="%s">
    <meta name="twitter:description" content="%s">
    <meta name="twitter:image" content="%s">
    <meta property="article:author" content="PackSmart">
    <meta property="article:section" content="Travel">
""" % tuple(html.escape(x, quote=True) for x in (TITLE, DESC, KEYWORDS, URL, TITLE, DESC, URL, SITE + HERO, TITLE, DESC, SITE + HERO))

HERO_HTML = ('    <div class="hero-blog" style="position:relative; background: linear-gradient(rgba(15,15,35,0.62), rgba(26,26,62,0.72)), '
             "url('%s'); background-size: cover; background-position: center 40%%;\">\n"
             '        <h1>%s</h1>\n        <div class="meta">Destination Guide • Japan · Published 19 Nov 2026 · 10 min read</div>\n'
             '        <div style="position:absolute;left:12px;right:12px;bottom:8px;font-size:0.7rem;opacity:0.7;text-align:center;">'
             'Photo: PAKUTASO. Illustrative image of the Fushimi Inari shrine in Kyoto.</div>\n</div>\n' % (HERO, esc(H1)))

BODY = "\n\n".join([INTRO, TOC_CSS.replace("__SCROLL_MARGIN__", SCROLL_MARGIN), toc_html(), TOC_JS,
                    ONE_PAGE, AREAS, CAR, TEA, DAYTRIPS, SIGHTS, MANNERS, FOOD, AROUND, faq_html(), ABOUT, RELATED])

PAGE = ("<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n    <meta charset=\"UTF-8\">\n"
        "    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n"
        "<meta name=\"robots\" content=\"max-image-preview:large\">\n    " + META + HEAD_A + LD + "\n" + HEAD_B
        + GYG_HEAD + "\n" + LOCAL_CSS + "\n</head>\n<body>\n" + NAV + "\n\n" + HERO_HTML + "\n    <div class=\"content\">\n\n"
        '<p style="font-size:0.85rem;color:#666;margin:0 0 0.6rem;">Published November 19, 2026 · Last updated November 2026 · Facts checked 19 Nov 2026</p>\n\n'
        + DISCLOSURE + "\n\n        " + SHARE + "\n\n" + BODY + "\n\n    </div>\n\n" + FOOT)

# ---- sanity checks on the output
for bad in ("osaka-pocket", "kyoto-pocket", "psPocketBar", "Station Pocket Guide", "India", "Klook", "GetYourGuide", "PLACEHOLDER", "&mdash;", "\u2014"):
    if bad in BODY:
        die("unwanted text in body: " + bad)
if PAGE.count("<h1") != 1:
    die("expected exactly one h1")
for sid, _, _, _ in SECTIONS:
    if len(re.findall(r'(?<![\w-])id="%s"' % sid, PAGE)) != 1:
        die("section id count wrong for " + sid)
if re.search(r"\$|US\$|\byen\b|\bJPY\b", BODY):
    die("a price slipped into the body")

changed = []
old = open(OUT, encoding="utf-8").read() if os.path.isfile(OUT) else None
if old != PAGE:
    open(OUT, "w", encoding="utf-8").write(PAGE)
    changed.append("blog/%s.html (%d bytes)" % (SLUG, len(PAGE.encode("utf-8"))))

# ---- Japan guide link sentence
jp = open(JAPAN, encoding="utf-8").read()
if 'href="/blog/%s"' % SLUG not in jp:
    anchor = '<!-- kyoto-station-guide link -->'
    i = jp.find(anchor)
    if i < 0:
        die("Japan guide: kyoto-station-guide link block not found (run w39 first)")
    j = jp.find("</p>", i) + len("</p>")
    add = ('\n\n<!-- kyoto-travel-guide link -->\n<p>Planning time in Kyoto itself? Our <a href="/blog/%s">Kyoto travel guide</a> covers a private guide and car, '
           'a tea ceremony, day trips to Nara and to Amanohashidate and Ine, the main sights with opening times, and manners in Gion.</p>' % SLUG)
    jp = jp[:j] + add + jp[j:]
    open(JAPAN, "w", encoding="utf-8").write(jp)
    changed.append("Japan guide link sentence")

# ---- Osaka travel guide: point the day-trips note at this guide
OSK = os.path.join(BLOG, "osaka-travel-guide.html")
if os.path.isfile(OSK):
    ok = open(OSK, encoding="utf-8").read()
    if 'href="/blog/%s"' % SLUG not in ok:
        old_note = "Nara and the Amanohashidate coast are also popular day trips. A private car (above) can reach both.</p>"
        if ok.count(old_note) != 1:
            die("Osaka guide: day-trips note not found (run w38 first)")
        new_note = ('Nara and the Amanohashidate coast are also popular day trips. A private car (above) can reach both, and our '
                    '<a href="/blog/%s">Kyoto travel guide</a> covers Nara and Amanohashidate with Ine Funaya from the Kyoto side.</p>' % SLUG)
        ok = ok.replace(old_note, new_note)
        open(OSK, "w", encoding="utf-8").write(ok)
        changed.append("Osaka guide link sentence")

# ---- sitemap
sm = open(SITEMAP, encoding="utf-8").read()
if "/blog/%s</loc>" % SLUG not in sm:
    k = sm.find("<loc>%s/blog/kyoto-station-guide</loc>" % SITE)
    if k < 0:
        die("sitemap: kyoto-station-guide entry not found (run w39 first)")
    a = sm.rfind("<url>", 0, k)
    b = sm.find("</url>", k) + len("</url>")
    block = sm[a:b]
    new = block.replace("kyoto-station-guide", SLUG)
    new = re.sub(r"<lastmod>[^<]*</lastmod>", "<lastmod>%s</lastmod>" % TODAY, new)
    sm = sm[:b] + "\n  " + new + sm[b:]
    open(SITEMAP, "w", encoding="utf-8").write(sm)
    changed.append("sitemap entry")

# ---- blog index card (Japan, after the Osaka travel guide card)
bx = open(BLOGIDX, encoding="utf-8").read()
if 'href="/blog/%s"' % SLUG not in bx:
    k = bx.find('<a href="/blog/osaka-travel-guide" class="blog-card"')
    if k < 0:
        die("blog.html: Osaka travel guide card not found (run w38 first)")
    e = bx.find("</a>", k) + len("</a>")
    CARD = '''

        <a href="/blog/%s" class="blog-card" data-region="Asia" data-country="japan">
            <img class="blog-card-img" src="/images/kyoto-travel-guide-card-680.webp" alt="A stone path running through a tunnel of red torii gates at Fushimi Inari, Kyoto" width="680" height="340" loading="lazy">
            <div class="blog-card-body">
                <span class="tag">Destination Guide</span>
                <h2>Kyoto Travel Guide 2026: Private Guide, Tea Ceremony, Nara and Amanohashidate</h2>
                <p>A private guide and car, a tea ceremony, day trips to Nara and to Amanohashidate and Ine, the main sights with opening times, and manners in Gion.</p>
                <span class="meta">November 19, 2026 &middot; 10 min read</span>
                <br><span class="read-more">Read more &rarr;</span>
            </div>
        </a>''' % SLUG
    bx = bx[:e] + CARD + bx[e:]
    open(BLOGIDX, "w", encoding="utf-8").write(bx)
    changed.append("blog.html card")

print("w41 done. changed: " + (", ".join(changed) if changed else "nothing (already up to date)"))
