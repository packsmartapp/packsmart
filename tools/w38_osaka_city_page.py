#!/usr/bin/env python3
"""w38: Osaka city guide (article only, no pocket guide).
Run from the repo root (~/packsmart):  python3 tools/w38_osaka_city_page.py
Idempotent. Needs, in public/images: osaka-travel-guide-hero.jpg (Pakutaso photo, 1600 px wide) and
osaka-travel-guide-card-680.webp (card crop). Run AFTER w36 (reads the page chrome from blog/osaka-station-guide.html).
Writes public/blog/osaka-travel-guide.html, adds a link sentence to the Japan guide, adds the sitemap entry and a card on blog.html.
No prices are printed: they change by date and group size.
"""
import os, re, sys, json, html

ROOT = os.getcwd()
PUB = os.path.join(ROOT, "public")
BLOG = os.path.join(PUB, "blog")
IMG = os.path.join(PUB, "images")
STATION = os.path.join(BLOG, "osaka-station-guide.html")
JAPAN = os.path.join(BLOG, "japan-travel-packing-guide.html")
SITEMAP = os.path.join(PUB, "sitemap.xml")
BLOGIDX = os.path.join(PUB, "blog.html")
SLUG = "osaka-travel-guide"
OUT = os.path.join(BLOG, SLUG + ".html")
SITE = "https://www.packsmartapp.com"
URL = "%s/blog/%s" % (SITE, SLUG)
TODAY = "2026-11-19"
MODIFIED = "2026-11-20"
H1 = "Osaka Travel Guide 2026: Private Car, Kobe Beef, Sumo and Day Trips"
TITLE = "Osaka Travel Guide 2026: Private Car, Kobe Beef, Sumo and Day Trips | PackSmart"
DESC = ("Plain-English Osaka travel guide: a private car with driver, Kobe beef and sake tours, a sumo show with wagyu "
        "sukiyaki, day trips to Himeji, Kobe, Koyasan and Hiroshima, plus the main sights and food.")
KEYWORDS = ("Osaka travel guide, Osaka private car with driver, Kobe beef and sake tour from Osaka, Osaka sumo show wagyu sukiyaki, "
            "day trips from Osaka, Osaka to Himeji, Osaka to Koyasan, Osaka to Hiroshima Miyajima, things to do in Osaka, "
            "Osaka Castle, Dotonbori, Umeda Sky Building, Kaiyukan, USJ")
HERO = "/images/osaka-travel-guide-hero.jpg"
GYG_PARTNER = "D7IXONS"


def die(msg):
    print("ABORT: " + msg)
    sys.exit(1)


for p in (STATION, JAPAN, SITEMAP, BLOGIDX):
    if not os.path.isfile(p):
        die("missing " + p + " (run from the repo root, after w36)")
for f in ("osaka-travel-guide-hero.jpg", "osaka-travel-guide-card-680.webp"):
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
NEW_T = "Osaka%20Travel%20Guide%202026%3A%20Private%20Car%2C%20Kobe%20Beef%2C%20Sumo%20and%20Day%20Trips"
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


# ------------------------------------------------------------------ page sections
SECTIONS = [
    # id, short chip label, full title, tile (emoji entity, title, sub) or None
    ("one-page", "On one page", "Osaka on one page", None),
    ("areas", "Where things are", "Where things are in Osaka", None),
    ("private-car", "Private car", "Private car with driver", ("&#128663;", "Private car", "A driver for the day")),
    ("kobe-beef", "Kobe beef + sake", "Kobe beef and sake: private tours", ("&#127863;", "Kobe beef + sake", "Private tours")),
    ("sumo", "Sumo show", "Sumo show with wagyu sukiyaki", ("&#129351;", "Sumo show", "With wagyu sukiyaki")),
    ("day-trips", "Day trips", "Day trips from Osaka", ("&#128646;", "Day trips", "Himeji, Koyasan, Hiroshima")),
    ("sights", "Sights", "The main sights in the city", ("&#127983;", "City sights", "Castle, Dotonbori, views")),
    ("food", "Food", "What to eat", None),
    ("getting-around", "Getting around", "Getting to and around Osaka", ("&#128652;", "Getting around", "Airport, trains, passes")),
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


def exp(pid, tag, title, facts, link, label, note, img=None):
    lis = "\n".join("<li>%s</li>" % f for f in facts)
    fig = ""
    if img:
        fn, alt, credit = img
        if not os.path.isfile(os.path.join(IMG, fn)):
            die("missing public/images/" + fn)
        fig = ('\n<figure><a href="%s" target="_blank" rel="nofollow noopener sponsored" tabindex="-1" aria-hidden="true">'
               '<img src="/images/%s" alt="%s" width="1200" height="500" loading="lazy" decoding="async"></a>'
               '<figcaption>%s</figcaption></figure>' % (link, fn, alt, credit))
    return ('<div class="ps-exp" data-ps-placement="%s">%s\n<span class="tag">%s</span>\n<h3>%s</h3>\n<ul>\n%s\n</ul>\n'
            '<a class="go" href="%s" target="_blank" rel="nofollow noopener sponsored">%s</a>\n<small>%s</small>\n</div>'
            % (pid, fig, tag, title, lis, link, label, note))


def partner_line(pid, text, link, label):
    return ('<p data-ps-placement="%s">%s <a href="%s" target="_blank" rel="nofollow noopener sponsored">%s</a> (partner link).</p>'
            % (pid, text, link, label))


def official(url, label):
    return '<a href="%s" target="_blank" rel="noopener">%s</a>' % (url, label)


# ---- 1. one page
ONE_PAGE = """<div class="ps-card" id="one-page">
<h2>Osaka on one page</h2>
<ul>
<li><strong>Two centres:</strong> Umeda (also called Kita), around Osaka Station in the north, and Namba and Dotonbori (Minami) in the south. The Midosuji subway line links them in about 15 minutes.</li>
<li><strong>Bay area:</strong> Universal Studios Japan (USJ) and the Kaiyukan aquarium. USJ is about 10 to 11 minutes by JR train from Osaka Station. Kaiyukan is a 5-minute walk from Osakako Station.</li>
<li><strong>Easy day trips:</strong> Kobe about 20 to 25 minutes by train. Nara about 40 minutes from Namba. Himeji about 30 minutes by Shinkansen from Shin-Osaka. Hiroshima about 1 hour 25 minutes by Shinkansen. Koyasan at least 90 minutes from Namba, plus a 5-minute cable car.</li>
<li><strong>Hard to arrange alone:</strong> a private car with a driver, a Kobe beef and sake tour, and a sumo show with wagyu sukiyaki. They come first in this guide.</li>
<li><strong>Food:</strong> takoyaki, okonomiyaki and kushikatsu are the three Osaka classics.</li>
<li><strong>Arriving?</strong> See our <a href="/blog/kansai-airport-guide">Kansai Airport guide</a> if you fly in, or our <a href="/blog/osaka-station-guide">Osaka station guide</a> if you come by bullet train.</li>
</ul>
</div>"""

INTRO = """<p>Osaka is Japan's big food city and the easiest base for the wider Kansai region. This guide starts with the experiences that are hardest to organise on your own: a private car with a driver, Kobe beef and sake tours, and a sumo show with wagyu sukiyaki. It then covers the day trips people make most often, and the main sights in the city. Facts come from official tourism and attraction sites, checked on 19 November 2026. We print no prices, because they change by date and group size.</p>"""

# ---- 2. areas
AREAS = """<h2 id="areas">Where things are in Osaka</h2>
<p>Osaka is easier to plan once you know four areas. Most of the city's trains and subway lines run through the first two.</p>
<div class="ps-scroll"><table>
<thead><tr><th>Area</th><th>Known for</th><th>Getting there</th></tr></thead>
<tbody>
<tr><td><strong>Umeda (Kita)</strong></td><td data-label="Known for">Osaka Station, large department stores, the Umeda Sky Building viewpoint.</td><td data-label="Getting there">JR Osaka Station, Osaka Metro Umeda, and the Hankyu and Hanshin Umeda stations.</td></tr>
<tr><td><strong>Namba and Dotonbori (Minami)</strong></td><td data-label="Known for">Neon streets, food, and the Dotonbori and Shinsaibashi shopping areas.</td><td data-label="Getting there">Namba, Nipponbashi and Shinsaibashi stations. From Umeda, take the Midosuji subway line to Namba (about 15 minutes).</td></tr>
<tr><td><strong>Osaka Castle</strong></td><td data-label="Known for">The castle museum and a large park.</td><td data-label="Getting there">About a 20-minute walk to the keep from JR Osakajokoen Station or from Morinomiya Station.</td></tr>
<tr><td><strong>Bay area</strong></td><td data-label="Known for">USJ, the Kaiyukan aquarium and the Tempozan Ferris wheel.</td><td data-label="Getting there">JR Universal City Station for USJ (about 10 minutes from Osaka Station, no change). Osaka Metro Chuo Line to Osakako Station for Kaiyukan.</td></tr>
</tbody></table></div>"""

# ---- 3. private car
CAR = ("""<h2 id="private-car">Private car with driver</h2>
<p>A car charter suits a group, a family, or anyone who wants several stops in one day without working out trains. The driver collects you in Osaka and the day follows a route you choose from the listing. Entrance fees are not included in either option below, and the driver's language works differently in each, so read that line before you book.</p>
""" + exp("klook-osaka-car-charter", "Private car with driver",
          "Osaka car charter with driver: Nara, Kobe, Kyoto and more",
          ["A 10-hour day, with vehicles from 7 to 30 seats.",
           "Free pick-up and drop-off inside Osaka city. Overtime is charged by the hour.",
           "Routes on the listing include Kyoto and Nara, Kyoto and Kobe, Amanohashidate and Funaya, Awaji Island, Lake Biwa, and Wakayama and Shirahama.",
           "Drivers speak Mandarin or Japanese, with a translator device for English.",
           "Admission to sights is not included."],
          "https://klook.tpo.lu/x5X6T67m", "See dates and options (partner link)",
          "Rated 4.6 from about 820 reviews on the booking page, 18 November 2026.",
          img=("osaka-box-car1.webp", "Kobe Port Tower, a red lattice tower, beside a tall hotel on the Kobe waterfront", "Photo: Pakutaso"))
       + "\n" +
       exp("klook-osaka-car-charter-2", "Private car with driver",
           "Kansai private chartered car: a customised day tour",
           ["From 8 to 18 hours, so you can plan a short or a long day.",
            "Hotel pick-up, with the day starting and ending in Osaka City. Starting or ending at Kansai Airport or Izumi City adds a surcharge.",
            "The driver's language (Chinese, Japanese or English) is assigned at random, with translation software if needed.",
            "A Golden Week surcharge applies from 29 April to 6 May."],
           "https://klook.tpo.lu/8KjPkooL", "See dates and options (partner link)",
           "Rated 4.7 from about 246 reviews on the booking page, 18 November 2026.",
           img=("osaka-box-car2.webp", "Aerial view of central Osaka seen from a high tower, with rail lines and dense city blocks", "Photo: Pakutaso"))
       + """
<p>How to choose: the first suits a fixed 10-hour day with a bigger choice of vehicle sizes. The second suits a day whose length you want to set yourself.</p>""")

# ---- 4. Kobe beef and sake
KOBE = ("""<h2 id="kobe-beef">Kobe beef and sake: private tours</h2>
<p>Kobe is about 20 to 25 minutes from Osaka by train, and two famous things meet there: Kobe beef and the Nada sake district. Several operators run private tours from Osaka that combine them, with hotel pick-up, so you do not need to arrange trains and restaurant tables yourself. The tours below are for private or small groups. Some are newly listed and have few reviews, so read the reviews, the meeting point and the cancellation terms before you book.</p>
""" + gyg("gyg-osaka-kobe-private", "Kobe beef and sake tours from Osaka",
          "Private days with hotel pick-up.", ["1331528", "1483085", "1071586"], "packsmart-osaka-kobe-private") + """
<h3>What counts as Kobe beef</h3>
<p>The Kobe Beef Marketing and Distribution Promotion Association defines Kobe beef as beef from Tajima cattle raised in Hyogo Prefecture, and the name is registered as a geographical indication in Japan. Its FAQ says Kobe beef is less than about 0.2 percent of the beef eaten in Japan. When you book a beef lunch or dinner, ask whether the beef is certified Kobe beef, and which cut and portion you are getting. The association explains the rules on """ + official("https://www.kobe-niku.jp/en/contents/faq/index.html", "its English FAQ page") + """.</p>
<h3>Nada sake: the do-it-yourself version</h3>
<p>Nada-Gogo, the "five villages of Nada" between Kobe and Nishinomiya, is Japan's biggest sake-producing area, according to """ + official("https://www.feel-kobe.jp/en/stories/japanesesake", "VISIT KOBE") + """. Displays and shops at the larger breweries are free to visit, but special tours and some facilities need advance booking. From Umeda it takes about 20 minutes on the direct Hanshin line, and VISIT KOBE publishes a walking route of about five hours if you want to plan it yourself.</p>""")

# ---- 5. sumo
SUMO = ("""<h2 id="sumo">Sumo show with wagyu sukiyaki</h2>
<p>A sumo show is a live demonstration by former professional wrestlers, with an explanation of the rules and rituals, usually a chance for guests to step into the ring, and an optional meal. The two listings below offer wagyu sukiyaki, and one also offers chanko nabe, the traditional sumo hot pot. The Konishiki listing says that former Ozeki Konishiki supervises the show but does not appear in the regular performances. The Konishiki listing offers child rates, and children aged 6 and under enter free.</p>
""" + gyg("gyg-osaka-sumo", "Sumo shows with a meal",
          "Front-row seats with wagyu sukiyaki, or the longer Konishiki-supervised show.", ["1188270", "713952"], "packsmart-osaka-sumo") + """
<p><strong>Where it is:</strong> the listings we saw on 18 and 19 November place these shows in Tajiri or Izumisano, in the south of Osaka Prefecture near Kansai Airport, not in central Osaka. Check the meeting point and the travel time before you book. The front-row listing runs about 2.5 hours, and the Konishiki listing 1.5 to 4 hours depending on the options you add.</p>
<h3>Want the real tournament?</h3>
<p>The Grand Sumo tournament in Osaka is held every March at EDION Arena Osaka, a five-minute walk from Nankai Namba Station. The Japan Sumo Association lists the 2027 March tournament as 14 to 28 March 2027, with advance tickets on sale from 6 February 2027. Tickets are sold through the association's """ + official("https://sumo.or.jp/EnTicket/year_schedule", "ticket pages") + """. That is a different event from the shows above.</p>""")

# ---- 6. day trips
DAYTRIPS = ("""<h2 id="day-trips">Day trips from Osaka</h2>
<p>These are the trips most visitors make from Osaka. Times are the train ride only, from official tourism pages.</p>
<div class="ps-scroll"><table>
<thead><tr><th>Place</th><th>By train from Osaka</th><th>Good to know</th></tr></thead>
<tbody>
<tr><td><strong>Kobe</strong></td><td data-label="By train from Osaka">About 20 to 25 minutes on the JR Kobe Line to Sannomiya.</td><td data-label="Good to know">Kobe beef and the Nada sake district (see above).</td></tr>
<tr><td><strong>Nara</strong></td><td data-label="By train from Osaka">About 40 minutes from Osaka Namba on the Kintetsu line, or about 50 minutes from Osaka Station on the JR Yamatoji Rapid.</td><td data-label="Good to know">Todai-ji and the deer in Nara Park (see below).</td></tr>
<tr><td><strong>Himeji</strong></td><td data-label="By train from Osaka">About 30 minutes by Shinkansen from Shin-Osaka, or about 1 hour by JR Special Rapid from Osaka.</td><td data-label="Good to know">The castle opens 9:00 to 17:00, with the last entry at 16:00.</td></tr>
<tr><td><strong>Hiroshima and Miyajima</strong></td><td data-label="By train from Osaka">About 1 hour 25 minutes by Shinkansen to Hiroshima, then a local train and a ferry for Miyajima.</td><td data-label="Good to know">A full day. Miyajima is reached by a ferry of about 10 minutes.</td></tr>
<tr><td><strong>Koyasan</strong></td><td data-label="By train from Osaka">At least 90 minutes from Namba on the Nankai Koya Line to Gokurakubashi, then a 5-minute cable car.</td><td data-label="Good to know">A mountain temple town. Start early.</td></tr>
</tbody></table></div>
<p class="ps-note">The Amanohashidate coast is also a popular day trip. We cover it, with Ine Funaya, in our <a href="/blog/kyoto-travel-guide">Kyoto travel guide</a>. A private car (above) can reach it.</p>

<h3>Himeji Castle, with Arima Onsen and Mount Rokko</h3>
<p>Osaka Info calls Himeji Castle arguably the best-preserved castle in Japan, and UNESCO listed it in 1993. The castle is open daily 9:00 to 17:00, with the last entry at 16:00, and it closes on 29 and 30 December. From Himeji Station it is a 15 to 20 minute walk, or about 5 minutes by bus. The city says a visit usually takes 90 to 120 minutes. The castle's official pages recommend digital time-slot tickets, and the city's page says same-day tickets may not be on sale at some times of day. Read the """ + official("https://www.himejicastle.jp/en/", "official Himeji Castle page") + """ for the day you go.</p>
""" + exp("klook-osaka-dt-himeji", "Guided day tour",
          "Himeji Castle, Arima Onsen and Mount Rokko from Osaka",
          ["About 10 hours, with two package options (with or without a tempura set meal).",
           "You may share a vehicle with guests who need English guidance.",
           "Times can change with weather and traffic."],
          "https://klook.tpo.lu/yWBIrbA5", "See dates and options (partner link)",
          "Rated 4.7 from about 451 reviews on the booking page, 18 November 2026.",
          img=("osaka-box-himeji.webp", "Himeji Castle's white keep rising above its stone walls", "Photo: Pakutaso")) + """

<h3>Koyasan and Okunoin</h3>
<p>Koyasan is the birthplace of Shingon Buddhism, brought to Japan by the monk Kukai (also known as Kobo Daishi), and Okunoin Temple is his mausoleum. JNTO gives the route from Osaka as the Nankai Koya Line from Namba to Gokurakubashi, taking at least 90 minutes, then a 5-minute cable car up the mountain. It is a long day by train, so a guided small-group tour that handles the transfers is a common choice.</p>
""" + exp("klook-osaka-dt-koyasan", "Small-group day tour",
          "Koyasan and Okunoin day tour from Osaka",
          ["About 10 hours, from 07:45 to 18:00.",
           "Small group of up to 18, with an English, Chinese or Japanese guide.",
           "Free cancellation up to 24 hours before, according to the listing."],
          "https://klook.tpo.lu/TILP1tbk", "See dates and options (partner link)",
          "Rated 4.9 from about 188 reviews on the booking page, 18 November 2026.",
          img=("osaka-box-koyasan.webp", "Moss-covered stone pagodas among cedar trees at Okunoin, Koyasan", "Photo: Pakutaso")) + """

<h3>Hiroshima and Miyajima</h3>
<p>From Shin-Osaka the Shinkansen reaches Hiroshima in about 1 hour 25 minutes, according to JNTO. Hiroshima Peace Memorial Park remembers the 1945 atomic bombing, and Itsukushima Shrine on Miyajima Island is known for its torii gate standing in the sea. From Hiroshima Station a local train to Miyajimaguchi takes about 25 to 30 minutes, then the ferry takes about 10 minutes.</p>
""" + exp("klook-osaka-dt-hiroshima-2", "Guided day tour",
          "Hiroshima and Miyajima by bus, with the Shinkansen from Osaka",
          ["About 7 hours 40 minutes. Pick the \"From Osaka: Round-Trip by Shinkansen\" package. A staff member gives you the Shinkansen tickets and a briefing at the station meeting point.",
           "Arrive 15 minutes early. The bus leaves on schedule and does not wait for late guests.",
           "English-speaking guide, with an okonomiyaki lunch included. A multilingual audio-guide plan is also offered.",
           "The listing names the Atomic Bomb Dome area in Peace Memorial Park and Itsukushima Shrine on Miyajima. It involves a lot of walking and is not wheelchair accessible."],
          "https://klook.tpo.lu/tbYN8Quz", "See dates and options (partner link)",
          "Rated 4.8 from about 537 reviews on the booking page, 20 November 2026.",
          img=("osaka-box-hiroshima.webp", "Itsukushima Shrine's vermilion halls and five-storey pagoda on Miyajima at low tide", "Photo: Pakutaso")) + """

<h3>Nara</h3>
<p>Nara is the easiest day trip from Osaka. Nara City's tourism site gives about 40 minutes from Osaka Namba to Kintetsu-Nara on a direct Kintetsu service, and about 50 minutes from Osaka Station to Nara on the direct JR Yamatoji Rapid. Todai-ji and about 1,400 wild deer, according to Visit Nara, are in and around Nara Park. Our <a href="/blog/kyoto-travel-guide">Kyoto travel guide</a> has the Todai-ji opening hours and the deer rules.</p>
""" + exp("klook-osaka-dt-nara", "Guided day tour",
          "Kyoto and Nara highlights from Osaka",
          ["A group bus tour of 10 to 11 hours, with an English or Mandarin guide.",
           "Stops on the listing: Fushimi Inari, Kinkaku-ji, Arashiyama, and Nara with Todai-ji and the deer.",
           "The tour leaves from Osaka or Kyoto. Lunch is not included unless you pick a meal option."],
          "https://klook.tpo.lu/HAAIsP51", "See dates and options (partner link)",
          "Rated 4.4 from about 3,800 reviews on the booking page, 20 November 2026.",
          img=("osaka-box-nara.webp", "Sika deer grazing on the lawn in Nara Park", "Photo: Pakutaso")))

# ---- 7. sights
SIGHTS = ("""<h2 id="sights">The main sights in the city</h2>
<h3>Osaka Castle</h3>
<p>Toyotomi Hideyoshi began the castle in 1583. The main tower you see today was rebuilt in 1931 and has 8 floors inside, with a view of the city from the top. Osaka Info gives a walk of just under 20 minutes to the keep from JR Osakajokoen Station, over Gokuraku-bashi Bridge, or from Morinomiya Station. Its pages list the museum hours as 9:00 to 17:00 or 18:00 depending on the season, with the last entry 30 minutes before closing, and the castle is closed from 28 December to 1 January. Check the """ + official("https://www.osakacastle.net/", "castle's own site") + """ for your date.</p>
<h3>Dotonbori and Namba</h3>
<p>Dotonbori is Osaka's best-known dining and entertainment district, with neon signs along the canal, the Glico sign and the giant crab above the Kani Doraku restaurant. JNTO suggests walking it at night. It is in the Minami area, close to Namba.</p>
<h3>Umeda Sky Building</h3>
<p>The Floating Garden Observatory is an open-air rooftop 173 metres above the ground, reached by a see-through escalator from the 35th to the 39th floor. Osaka Info lists it as open 9:30 to 22:30, last entry 22:00. Hours can be shorter on event days. If you buy an Osaka e-Pass, admission is free until 3 pm.</p>
<h3>Shinsekai and Tsutenkaku</h3>
<p>Tsutenkaku Tower's main observation deck is open every day from 9:00 to 21:45, with the last entry at 21:15, according to Osaka Info. The Shinsekai streets below are where kushikatsu began.</p>
""" + exp("klook-osaka-food-shinsekai", "Night food tour",
          "Shinsekai night food tour with 15 dishes and 3 drinks",
          ["3 hours from 17:30, in a small group of 2 to 9 with an English guide.",
           "Meets at Dobutsuen-mae Station. The route on the listing has five restaurants, with a stop to see the Tsutenkaku area.",
           "Dishes on the listing include takoyaki, oden, yakitori, gyoza and kushikatsu.",
           "Free cancellation up to 24 hours before, according to the listing."],
          "https://klook.tpo.lu/Ln7odlHx", "See dates and options (partner link)",
          "Rated 4.9 from about 172 reviews on the booking page, 20 November 2026.",
          img=("osaka-box-shinsekai.webp", "Tsutenkaku Tower rising above food signs and a bronze statue in Shinsekai, Osaka", "Photo: Pakutaso")) + """
<h3>Osaka Aquarium Kaiyukan</h3>
<p>Kaiyukan shows about 30,000 animals of around 620 species, and its whale shark is the best known. It opens 10:00 to 20:00 with the last entry an hour before closing, hours vary by season, and it closes for two days in January. The aquarium recommends booking a timed e-ticket, and Osaka Info lists about two hours for a visit.</p>
""" + partner_line("klook-osaka-kaiyukan", "Prefer to buy ahead?", "https://klook.tpo.lu/HUkHu5x0", "Kaiyukan tickets") + """
<h3>Universal Studios Japan</h3>
<p>USJ is about 10 to 11 minutes by JR train from Osaka Station to Universal City Station, with no change. Opening hours change from day to day, so check the park's official calendar for the day you plan to go.</p>
""" + exp("klook-osaka-usj", "Park ticket",
          "Universal Studios Japan Studio Pass",
          ["An entry ticket with a QR code. The listing suggests 1 to 2 days at the park.",
           "Prices change by date, so check the calendar on the booking page before you choose a day.",
           "The listing says the QR code can be scanned into the official USJ app from the day after you buy, so do not leave it to the last minute.",
           "Super Nintendo World may need a separate timed-entry or standby ticket, depending on the day. The listing points to the park's official site and app for the rules.",
           "Some attractions have height and health limits. Check them in advance."],
          "https://klook.tpo.lu/zfzbTTzX", "See dates and options (partner link)",
          "Rated 4.8 from about 91,300 reviews on the booking page, 20 November 2026."))

# ---- 8. food
FOOD = ("""<h2 id="food">What to eat</h2>
<p>Osakans are known for the saying <em>kuidaore</em>, which JNTO translates as "eat until you fall over". Three dishes come first:</p>
<ul>
<li><strong>Takoyaki:</strong> octopus dumplings cooked in a round pan and sold at street stalls. Osaka Info says shops began to appear in the city in the 1950s.</li>
<li><strong>Okonomiyaki:</strong> a savoury pancake of batter and cabbage with pork, seafood or both. The name means "grill what you like".</li>
<li><strong>Kushikatsu:</strong> skewered meat and vegetables, battered and deep-fried. Many restaurants have a "no double dipping" rule for the shared sauce. Kushikatsu started in Shinsekai.</li>
</ul>
<p>Dotonbori and Shinsekai are the two best places to try all three on one evening. A guided food tour is the easy way to do it, because the guide picks the stalls and bars for you.</p>
""" + exp("klook-osaka-food-dotonbori", "Food tour",
          "Dotonbori food tour with 12 dishes and 2 drinks",
          ["2.5 hours in a small group of up to 15, with an English guide. The listing has sessions at 12:00, 17:30 and 18:30.",
           "Meet in front of the Don Quijote Dotonbori Midosuji store, 15 minutes before the start.",
           "The route on the listing includes an izakaya and street food stops.",
           "Free cancellation up to 24 hours before, according to the listing."],
          "https://klook.tpo.lu/UYUq1j4T", "See dates and options (partner link)",
          "Rated 4.9 from about 302 reviews on the booking page, 20 November 2026.",
          img=("osaka-box-food.webp", "Takoyaki balls being turned with a skewer on a hot griddle", "Photo: Pakutaso")))

# ---- 9. getting around
AROUND = """<h2 id="getting-around">Getting to and around Osaka</h2>
<ul>
<li><strong>By plane:</strong> most international flights use Kansai Airport. Our <a href="/blog/kansai-airport-guide">Kansai Airport guide</a> covers the terminals, SIM options and the trains and buses into the city.</li>
<li><strong>By bullet train:</strong> you arrive at Shin-Osaka, not at Osaka Station. Our <a href="/blog/osaka-station-guide">Osaka station guide</a> explains the difference and how to get between them.</li>
<li><strong>Across the city:</strong> JR lines, Osaka Metro and the private railways all connect. The Midosuji subway line runs from Umeda to Namba in about 15 minutes. ICOCA works on JR trains in Kansai.</li>
<li><strong>Passes:</strong> Osaka Info runs the """ + official("https://www.e-pass.osaka-info.jp/en/", "Osaka e-Pass") + """ and the """ + official("https://www.osp.osaka-info.jp/en/", "Osaka Amazing Pass") + """. Each lists the sights it covers, so compare it with your plan before buying.</li>
</ul>"""

# ---- FAQ
FAQ = [
    ("How far are Kobe, Himeji, Hiroshima and Koyasan from Osaka?",
     "Kobe is about 20 to 25 minutes by JR train to Sannomiya. Himeji is about 30 minutes by Shinkansen from Shin-Osaka, or about 1 hour by JR Special Rapid from Osaka. Hiroshima is about 1 hour 25 minutes by Shinkansen from Shin-Osaka, according to JNTO, and Miyajima needs a local train and a ferry on top. Koyasan is at least 90 minutes from Namba on the Nankai Koya Line, then a 5-minute cable car."),
    ("What does a private car with driver in Osaka include?",
     "On the two booking listings we checked on 18 November 2026, the driver and vehicle are included, and admission to sights is not. One is a 10-hour charter with free pick-up and drop-off inside Osaka city, and the other runs 8 to 18 hours with hotel pick-up. Drivers speak Mandarin or Japanese on the first, and a language (Chinese, Japanese or English) assigned at random on the second, with a translation device or software for English, so confirm the language before you book."),
    ("What is the difference between a sumo show and the Grand Sumo tournament?",
     "A sumo show is a demonstration by former professional wrestlers, with an explanation of the rules, a chance to try the ring and an optional meal. The Grand Sumo tournament is the official competition. In Osaka it is held every March at EDION Arena Osaka, and the Japan Sumo Association lists the 2027 tournament as 14 to 28 March 2027."),
    ("What is Kobe beef?",
     "The Kobe Beef Marketing and Distribution Promotion Association defines it as beef from Tajima cattle raised in Hyogo Prefecture. It is registered as a geographical indication in Japan and is less than about 0.2 percent of the beef eaten there. Ask a restaurant whether its beef is certified Kobe beef."),
    ("How do I get to USJ and Kaiyukan?",
     "USJ is about 10 to 11 minutes by JR train from Osaka Station to Universal City Station, with no change. Kaiyukan is a 5-minute walk from Osakako Station on the Osaka Metro Chuo Line."),
    ("When is the Osaka sumo tournament?",
     "Every March at EDION Arena Osaka. The Japan Sumo Association lists the 2027 March tournament as 14 to 28 March 2027, with advance tickets on sale from 6 February 2027."),
]


def faq_html():
    out = ['<h2 id="faq">Frequently Asked Questions</h2>']
    for q, a in FAQ:
        out.append("<h3>%s</h3>\n<p>%s</p>" % (esc(q), esc(a)))
    return "\n".join(out)


ABOUT = """<div class="ps-about" id="about-this-guide">
<h2>About this guide</h2>
<p>Written by PackSmart. Facts were checked on 19 and 20 November 2026 against """ + ", ".join([
    official("https://osaka-info.jp/en/", "Osaka Info"),
    official("https://www.japan.travel/en/", "the Japan National Tourism Organization (JNTO)"),
    official("https://www.himejicastle.jp/en/", "Himeji Castle"),
    official("https://www.feel-kobe.jp/en/", "VISIT KOBE"),
    official("https://www.kobe-niku.jp/en/", "the Kobe Beef Marketing and Distribution Promotion Association"),
    official("https://sumo.or.jp/EnTicket/year_schedule", "the Japan Sumo Association")]) + """. We print no prices, because they change by date and group size. Ratings and review counts come from the booking pages on 18, 19 and 20 November 2026 and change. Some of the links in this guide are partner links, marked as such. If a fact has changed, please <a href="/contact">tell us</a>.</p>
<ul>
<li><strong>19 Nov 2026:</strong> first version.</li>
</ul>
</div>"""


def card(title, text, slug, tag):
    return ('        <div class="related-card">\n            <div class="related-card-body">\n                <h4>%s</h4>\n                <p>%s</p>\n'
            '                <a href="https://www.packsmartapp.com/blog/%s">Read More <span class="related-arrow">&rarr;</span></a>\n'
            '                <div class="related-tag">%s</div>\n            </div>\n        </div>\n' % (title, text, slug, tag))


RELATED = ('<div class="related-posts">\n    <h3>Related Guides</h3>\n    <div class="related-grid">\n'
           + card("Osaka Station Guide 2026", "Shin-Osaka or Umeda? Platforms, lockers, ICOCA and how to get between the stations.", "osaka-station-guide", "Station Guide")
           + card("Kansai Airport Guide 2026", "Flying into Osaka? Terminals, arrival steps, SIM and the trains and buses to Osaka and Kyoto.", "kansai-airport-guide", "Airport Guide")
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
        "image": SITE + HERO, "datePublished": TODAY, "dateModified": MODIFIED,
        "author": {"@type": "Organization", "name": "PackSmart"},
        "publisher": {"@type": "Organization", "name": "PackSmart", "logo": {"@type": "ImageObject", "url": SITE + "/logo.png"}},
        "mainEntityOfPage": URL}),
    ld({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE},
        {"@type": "ListItem", "position": 2, "name": "Destinations", "item": SITE + "/blog"},
        {"@type": "ListItem", "position": 3, "name": "Osaka Travel Guide", "item": URL}]}),
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
             '        <h1>%s</h1>\n        <div class="meta">Destination Guide • Japan · 9 min read</div>\n'
             '        <div style="position:absolute;left:12px;right:12px;bottom:8px;font-size:0.7rem;opacity:0.7;text-align:center;">'
             'Photo: PAKUTASO. Illustrative image of Osaka.</div>\n</div>\n' % (HERO, esc(H1)))

BODY = "\n\n".join([INTRO, TOC_CSS.replace("__SCROLL_MARGIN__", SCROLL_MARGIN), toc_html(), TOC_JS,
                    ONE_PAGE, AREAS, CAR, KOBE, SUMO, DAYTRIPS, SIGHTS, FOOD, AROUND, faq_html(), ABOUT, RELATED])

PAGE = ("<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n    <meta charset=\"UTF-8\">\n"
        "    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n"
        "<meta name=\"robots\" content=\"max-image-preview:large\">\n    " + META + HEAD_A + LD + "\n" + HEAD_B
        + GYG_HEAD + "\n" + LOCAL_CSS + "\n</head>\n<body>\n" + NAV + "\n\n" + HERO_HTML + "\n    <div class=\"content\">\n\n"
        '<p style="font-size:0.85rem;color:#666;margin:0 0 0.6rem;">Published November 19, 2026 · Last updated November 20, 2026 · Facts checked 19 and 20 Nov 2026</p>\n\n'
        + DISCLOSURE + "\n\n        " + SHARE + "\n\n" + BODY + "\n\n    </div>\n\n" + FOOT)

# ---- sanity checks on the output
for bad in ("osaka-pocket", "psPocketBar", "Station Pocket Guide", "India", "Klook", "GetYourGuide", "&mdash;", "\u2014"):
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
    anchor = '<!-- osaka-station-guide link -->'
    i = jp.find(anchor)
    if i < 0:
        die("Japan guide: osaka-station-guide link block not found (run w36 first)")
    j = jp.find("</p>", i) + len("</p>")
    add = ('\n\n<!-- osaka-travel-guide link -->\n<p>Planning time in Osaka itself? Our <a href="/blog/%s">Osaka travel guide</a> covers a private car with a driver, '
           'Kobe beef and sake tours, a sumo show with wagyu sukiyaki, day trips to Himeji, Koyasan and Hiroshima, and the main sights.</p>' % SLUG)
    jp = jp[:j] + add + jp[j:]
    open(JAPAN, "w", encoding="utf-8").write(jp)
    changed.append("Japan guide link sentence")

# ---- sitemap
sm = open(SITEMAP, encoding="utf-8").read()
if "/blog/%s</loc>" % SLUG not in sm:
    k = sm.find("<loc>%s/blog/osaka-station-guide</loc>" % SITE)
    if k < 0:
        die("sitemap: osaka-station-guide entry not found")
    a = sm.rfind("<url>", 0, k)
    b = sm.find("</url>", k) + len("</url>")
    block = sm[a:b]
    new = block.replace("osaka-station-guide", SLUG)
    new = re.sub(r"<lastmod>[^<]*</lastmod>", "<lastmod>%s</lastmod>" % MODIFIED, new)
    sm = sm[:b] + "\n  " + new + sm[b:]
    open(SITEMAP, "w", encoding="utf-8").write(sm)
    changed.append("sitemap entry")

# ---- blog index card (Japan, after the Japan 7-day itinerary card)
bx = open(BLOGIDX, encoding="utf-8").read()
if 'href="/blog/%s"' % SLUG not in bx:
    k = bx.find('<a href="/blog/japan-7-day-itinerary-budget" class="blog-card"')
    if k < 0:
        die("blog.html: Japan itinerary card not found")
    e = bx.find("</a>", k) + len("</a>")
    CARD = '''

        <a href="/blog/%s" class="blog-card" data-region="Asia" data-country="japan">
            <img class="blog-card-img" src="/images/osaka-travel-guide-card-680.webp" alt="Aerial view of Osaka's skyline and parks under a cloudy sky" width="680" height="340" loading="lazy">
            <div class="blog-card-body">
                <span class="tag">Destination Guide</span>
                <h2>Osaka Travel Guide 2026: Private Car, Kobe Beef, Sumo and Day Trips</h2>
                <p>A private car with a driver, Kobe beef and sake tours, a sumo show with wagyu sukiyaki, and day trips to Himeji, Koyasan and Hiroshima.</p>
                <span class="meta">November 19, 2026 &middot; 9 min read</span>
                <br><span class="read-more">Read more &rarr;</span>
            </div>
        </a>''' % SLUG
    bx = bx[:e] + CARD + bx[e:]
    open(BLOGIDX, "w", encoding="utf-8").write(bx)
    changed.append("blog.html card")

print("w38 done. changed: " + (", ".join(changed) if changed else "nothing (already up to date)"))
