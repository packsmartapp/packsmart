#!/usr/bin/env python3
"""
w77: a light Japan band at the top of the Japan station, airport and city guides (25 Nov 2026).

The /japan hub uses seasonal Fuji, sakura, kanji signs, train tickets and checked stamps; the guides it links to opened
on a dark photo hero and a plain article, which felt like another site. Without redesigning the articles, this adds,
right under each guide's hero:

  * a breadcrumb back to the hub (Japan hub > Stations > Tokyo Station);
  * a name sign in the hub's ticket style: the name in Japanese, the kind of guide, and a red 確認 stamp with the date
    in the page's own "Facts checked" line (else the date its sources were most often checked);
  * the hub's washi wave print behind the band and behind the guide's "What do you need first?" panel.

Step 2 (25 Nov 2026), same script:
  * a lighter photo hero (the dark navy tint is now light at the top and darker only under the title);
  * an "Ask Packy about <place>" box right after the guide's "What do you need first?" tiles, with that place's own
    starter questions (read from public/packy.js), on the guides that load Packy (w75). Questions open the Packy chat.

Step 2b: on wide screens (1200px and up) the guide sits in the hub's world: washi pink with the wave print behind
a white "paper" panel for the text (which keeps its 800px reading width), the hub's sakura branches on both sides
(copied from public/japan.html, so run after w73) and the seasonal falling petals. Phones stay plain white.

The article body is not touched. The band sits between <!-- jp-band --> markers and is replaced as a whole, and the CSS
is one <style id="jp-guide-css"> block in <head>, so re-running is safe.

Run after the page generators and w73/w75, before w76 and w72:  python3 tools/w77_japan_guide_band.py
Aborts without writing if a listed page, its hero or its checked date is missing.
"""
import datetime, os, re, sys

ROOT = os.getcwd()
BLOG = os.path.join(ROOT, "public", "blog")
GUIDES = {  # slug: (Japanese name, English name, kind)
    "tokyo-station-guide": ("東京駅", "Tokyo Station", "station"),
    "shinjuku-station-guide": ("新宿駅", "Shinjuku Station", "station"),
    "ueno-station-guide": ("上野駅", "Ueno Station", "station"),
    "kyoto-station-guide": ("京都駅", "Kyoto Station", "station"),
    "osaka-station-guide": ("新大阪駅・大阪駅", "Shin-Osaka and Osaka Stations", "station"),
    "sapporo-station-guide": ("札幌駅", "Sapporo Station", "station"),
    "narita-airport-guide": ("成田空港", "Narita Airport", "airport"),
    "haneda-airport-guide": ("羽田空港", "Haneda Airport", "airport"),
    "kansai-airport-guide": ("関西国際空港", "Kansai Airport", "airport"),
    "new-chitose-airport-guide": ("新千歳空港", "New Chitose Airport", "airport"),
    "kyoto-travel-guide": ("京都", "Kyoto", "city"),
    "osaka-travel-guide": ("大阪", "Osaka", "city"),
}
KIND = {"station": ("駅", "Station guide", "Stations", "/japan#stations"),
        "airport": ("空港", "Airport guide", "Airports", "/japan#arriving"),
        "city": ("観光", "City guide", "Plan your trip", "/japan#plan")}
MONTHS = {m: i for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}
OLD_TINT = "linear-gradient(rgba(15,15,35,0.62), rgba(26,26,62,0.72))"
NEW_TINT = "linear-gradient(rgba(15,15,35,0.14) 0%, rgba(15,15,35,0.32) 45%, rgba(15,15,35,0.66) 100%)"
BG = re.compile(r'<!-- jp-guide-bg -->.*?<!-- /jp-guide-bg -->\n', re.S)
_hub = open(os.path.join(ROOT, "public", "japan.html"), encoding="utf-8").read()
_i = _hub.find('<div class="jp-bg"'); _j = _hub.find('\n<div class="page-wrapper">', _i)
if _i < 0 or _j < 0:
    sys.exit("w77 aborted: the sakura backdrop was not found on public/japan.html (run w73 first)")
SAKURA_BG = ("<!-- jp-guide-bg -->\n" + _hub[_i:_j] + "\n"
    "<script>(function(){var m=+new Date().toLocaleString('en-US',{timeZone:'Asia/Tokyo',month:'numeric'});"
    "document.body.setAttribute('data-season',m>=3&&m<=5?'spring':m>=6&&m<=8?'summer':m>=9&&m<=11?'autumn':'winter');"
    "var t=false;function f(){t=false;var bg=document.querySelector('.jp-bg'),h=document.querySelector('.hero-blog');if(bg)bg.classList.toggle('on',!h||h.getBoundingClientRect().bottom<90);}"
    "window.addEventListener('scroll',function(){if(!t){t=true;requestAnimationFrame(f);}},{passive:true});window.addEventListener('load',f);document.addEventListener('DOMContentLoaded',f);})();</script>\n"
    "<!-- /jp-guide-bg -->\n")
ASK = re.compile(r"<!-- jp-ask-guide -->.*?<!-- /jp-ask-guide -->\n", re.S)
TOPIC = re.compile(r'<script src="/packy\.js[^"]*" data-country="japan" data-topic="([a-z-]+)"')
PACKY = open(os.path.join(ROOT, "public", "packy.js"), encoding="utf-8").read()
FACE = "".join(re.findall(r"'([^']*)'", re.search(r"var FACE = ((?:'[^']*'\s*\+?\s*)+);", PACKY).group(1)))


def starters(topic):
    m = re.search(r"\n\s*'?%s'?: \[(.*?)\],?\n" % re.escape(topic), PACKY)
    return re.findall(r"'((?:[^'\\]|\\.)*)'", m.group(1)) if m else []


def ask_box(en, topic):
    qs = starters(topic)
    if not qs:
        return ""
    esc = lambda t: t.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")
    chips = "".join('<button type="button" data-q="%s">%s</button>' % (esc(q), esc(q)) for q in qs)
    return ('<!-- jp-ask-guide -->\n<section class="jg-ask" aria-label="Ask Packy about %s"><div class="jg-h"><span class="av" aria-hidden="true">%s</span>'
            '<div><b>Ask Packy about %s</b><small>Your Japan travel buddy · answers from official sources</small></div></div>'
            '<form class="jg-f" autocomplete="off"><label class="jg-sr" for="jgQ">Your question</label><input id="jgQ" type="text" maxlength="300" placeholder="Ask about %s…">'
            '<button type="submit">Ask &#10148;</button></form><div class="jg-chips">%s</div></section>\n'
            "<script>(function(){var b=document.querySelector('.jg-ask');if(!b)return;function go(q){q=(q||'').trim();if(q.length<5)return;"
            "try{if(window.gtag)gtag('event','ask_japan',{event_category:'engagement',status:'guide_box',page_path:location.pathname});}catch(e){}"
            "if(window.Packy)window.Packy.ask(q);}b.querySelector('form').addEventListener('submit',function(e){e.preventDefault();var i=b.querySelector('input');go(i.value);i.value='';});"
            "[].forEach.call(b.querySelectorAll('[data-q]'),function(c){c.addEventListener('click',function(){go(c.getAttribute('data-q'));});});})();</script>\n"
            '<!-- /jp-ask-guide -->\n') % (en, FACE, en, en, chips)


CHECKED = re.compile(r"[Cc]hecked (?:on )?(\d{1,2})(?: and (\d{1,2}))? ([A-Z][a-z]+) (20\d\d)")
HERO = re.compile(r'<div class="hero-blog".*?\n</div>\n', re.S)
BAND = re.compile(r"<!-- jp-band -->.*?<!-- /jp-band -->\n", re.S)

WAVE = ("url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='40' height='20'%3E%3Cg fill='none' "
        "stroke='%2300C9A7' stroke-opacity='.18'%3E%3Cpath d='M0 20a10 10 0 0 1 20 0M5 20a5 5 0 0 1 10 0M20 20a10 10 0 0 1 20 0M25 20a5 5 0 0 1 10 0"
        "M-10 10a10 10 0 0 1 20 0M10 10a10 10 0 0 1 20 0M30 10a10 10 0 0 1 20 0'/%3E%3C/g%3E%3C/svg%3E\")")
CSS = """<style id="jp-guide-css">
@import url("https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&display=swap");
.jp-band{background:#FDF0F2 """ + WAVE + """;border-bottom:1px solid #F3D3DA;padding:14px 16px 18px}
.jp-band-in{max-width:760px;margin:0 auto}
.jp-crumb{font-size:.82rem;color:#5a6378;margin:0 0 10px}.jp-crumb a{color:#0a8f78;font-weight:700;text-decoration:none}.jp-crumb a:hover{text-decoration:underline}
.jp-crumb span{margin:0 6px;color:#b4bccb}
.jp-namesign{position:relative;display:flex;align-items:center;gap:18px;padding:6px 0 4px}
.jp-namesign-e{display:flex;flex-direction:column;min-width:0;flex:1}
.jp-namesign-e small{align-self:flex-start;font-size:.74rem;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:#0a8f78;background:#fff;border:1px solid #BFEDE3;border-radius:999px;padding:5px 12px}
.jp-welcome{display:block;font-family:'Instrument Serif',serif;font-size:3rem;line-height:1.05;color:#0f0f23;margin-top:8px}
.jp-namesign-k{font-family:'DM Sans',sans-serif;font-weight:800;letter-spacing:.06em;font-size:.82em;margin-right:6px}
.jp-welcome em{font-style:italic;color:#E94560}
.jp-namesign-st{flex:none;transform:rotate(-10deg);border:2px solid #E94560;color:#E94560;border-radius:8px;padding:3px 6px;font-size:.6rem;font-weight:800;letter-spacing:.05em;text-align:center;line-height:1.15;opacity:.85}
.hero-blog h1,.hero-blog .meta{text-shadow:0 2px 14px rgba(0,0,0,.55)}
.jg-ask{margin:22px 0 26px;background:#FDF0F2 """ + WAVE + """;border:1px solid #F3D3DA;border-radius:20px;padding:16px 16px 14px}
.jg-h{display:flex;align-items:center;gap:12px;margin-bottom:10px}.jg-h .av{flex:none;width:42px;height:42px;background:#fff;border-radius:12px;padding:3px;box-shadow:0 4px 12px rgba(0,168,140,.15)}
.jg-h .av svg{width:100%;height:100%;display:block}.jg-h b{display:block;font-size:1.08rem;color:#0f0f23}.jg-h small{color:#5a6378;font-size:.82rem}
.jg-f{display:flex;gap:8px;align-items:center;background:#fff;border:1.5px solid #BFEDE3;border-radius:999px;padding:4px 4px 4px 14px}
.jg-f input{flex:1;min-width:0;border:0;outline:0;font:inherit;font-size:16px;background:transparent;padding:8px 0;color:#0f0f23}
.jg-f button{flex:none;font:inherit;font-weight:800;font-size:.92rem;border:0;border-radius:999px;padding:9px 16px;background:linear-gradient(135deg,#E94560,#ff6b85);color:#fff;cursor:pointer}
.jg-chips{display:flex;flex-wrap:wrap;gap:6px;margin-top:10px}.jg-chips button{font:inherit;font-size:.84rem;font-weight:600;text-align:left;background:#fff;color:#0f0f23;border:1.5px solid #BFEDE3;border-radius:999px;padding:6px 12px;cursor:pointer}
.jg-chips button:hover{border-color:#00C9A7}.jg-sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
.jp-bg{display:none}
@media (min-width:1200px){
 html{background:#FDF0F2 """ + WAVE + """ fixed}body{background:transparent!important}
 .jp-bg{display:block;position:fixed;inset:0;pointer-events:none;z-index:-1;overflow:hidden}
 .jp-bg-l,.jp-bg-r{position:absolute;opacity:.95}
 .jp-bg-l{left:-10px;top:60px;width:min(420px,calc((100vw - var(--gw))/2 + 20px))}
 .jp-bg-r{right:-10px;bottom:-60px;transform:scaleX(-1);width:min(360px,calc((100vw - var(--gw))/2 + 20px))}
 .jp-bg svg{width:100%;height:auto;display:block}
 .jp-petal{position:absolute;top:-30px;width:16px;height:16px;animation:jpFall linear infinite;opacity:.85}.jp-petal svg{width:100%;height:100%;display:block}
 :root{--gw:900px}
 .content{max-width:900px;background:#fff;border-radius:28px;margin-top:28px!important;margin-bottom:28px;box-shadow:0 14px 40px rgba(15,15,35,.07)}
 .jp-band{border-bottom:0;padding:22px 16px 6px}
 .jp-bg{opacity:0;transition:opacity .5s}.jp-bg.on{opacity:1}
 .content .pga,.content [data-ps-placement],.content .ps-kd,.content .related-posts,.content .psn-now,.content .jg-ask{max-width:none!important}
 .content .related-posts{padding:0;margin:2.4rem 0 1rem}
 .content .related-grid{grid-template-columns:repeat(3,minmax(0,1fr));gap:1.1rem}
 .content .related-card-body{padding:1.1rem 1.2rem}
}
/* wide screens: the airport-transfer box as photo | benefits and booking form (owner's pick, option C, 25 Nov). The
   partner's form keeps its own field layout; its city search re-positions itself every 0.4 s, so it follows */
@media (min-width:1200px) and (max-width:1499px){.ps-pickups{display:grid!important;grid-template-columns:minmax(0,1fr) minmax(0,1fr);column-gap:28px;align-items:center}
 .ps-pickups>*{grid-column:1/-1}.ps-pickups>h3{grid-row:1}
 .ps-pickups>picture{grid-column:1;grid-row:2/4;margin-bottom:16px}.ps-pickups>picture img{margin:0!important}
 .ps-pickups>picture+strong{grid-column:2;grid-row:2;align-self:end}
 .ps-pickups>picture+strong+div{grid-column:2;grid-row:3;align-self:start;max-width:none!important}}
/* laptops (1200-1499 px) keep the form full width below; it needs about 800 px for its fields */
@media (min-width:1500px){.ps-pickups{display:grid!important;grid-template-columns:minmax(0,1fr) minmax(0,1fr);column-gap:24px;align-items:start}
 .ps-pickups>*{grid-column:1/-1}
 .ps-pickups>h3{grid-row:1}
 .ps-pickups>picture{grid-column:1;grid-row:2/5}.ps-pickups>picture img{margin:0!important}
 .ps-pickups>picture+strong{grid-column:2;grid-row:2}
 .ps-pickups>picture+strong+div{grid-column:2;grid-row:3;max-width:none!important}
 .ps-pickups>picture+strong+div+*{grid-column:2;grid-row:4}}
/* wide screens: the Shinkansen box in one band (picture | route and text | button), so the button sits up top */
@media (min-width:1500px){[data-ps-placement^="jw-shinkansen"]{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr) 280px;column-gap:28px;align-items:start}
 [data-ps-placement^="jw-shinkansen"]>strong{grid-column:1/-1}
 [data-ps-placement^="jw-shinkansen"] .jb-grid,[data-ps-placement^="jw-shinkansen"] .jb-row{display:contents}
 [data-ps-placement^="jw-shinkansen"] .jb-grid>a{grid-column:1;grid-row:2/4}
 [data-ps-placement^="jw-shinkansen"] .jb-grid>div{grid-column:2;grid-row:2;margin-bottom:12px}
 [data-ps-placement^="jw-shinkansen"] .jb-tx{grid-column:2;grid-row:3}
 [data-ps-placement^="jw-shinkansen"] .jb-bt{grid-column:3;grid-row:2/4;align-self:center}}
@media (min-width:1500px){:root{--gw:1320px}.content{max-width:1320px}.jp-band-in{max-width:1256px}}
@keyframes jpFall{0%{transform:translate(0,0) rotate(0)}25%{transform:translate(30px,25vh) rotate(90deg)}50%{transform:translate(-10px,50vh) rotate(200deg)}75%{transform:translate(25px,75vh) rotate(290deg)}100%{transform:translate(0,110vh) rotate(380deg)}}
@keyframes jpFly{0%{transform:translate(0,0);opacity:0}15%{opacity:1}35%{opacity:.35}55%{transform:translate(28px,-50vh);opacity:1}75%{opacity:.4}100%{transform:translate(-12px,-100vh);opacity:0}}
body[data-season=summer] .jp-petal{top:auto;bottom:-20px;width:7px;height:7px;border-radius:50%;background:#FFF6A0;box-shadow:0 0 10px 4px rgba(240,236,120,.75);animation-name:jpFly}
body[data-season=summer] .jp-petal svg{display:none}
body[data-season=autumn] .jp-petal path{fill:#E8743B;stroke:#C2501F}
body[data-season=winter] .jp-petal path{fill:#fff;stroke:#D6E2EC}body[data-season=winter] .jp-petal svg{transform:scale(.7)}
@media (prefers-reduced-motion:reduce){.jp-petal{display:none!important}}
.psn-now{background-image:""" + WAVE + """!important}
@media (max-width:600px){.jp-welcome{font-size:2.1rem}.jp-namesign{gap:8px 12px}.jp-namesign-k{font-size:1.5rem}.jp-namesign-bar{display:none}.jp-namesign-st{position:absolute;right:12px;top:-12px;background:#fff}}
</style>
"""


def _dates(text):
    out = []
    for d1, d2, mon, yr in CHECKED.findall(text):
        m = MONTHS.get(mon[:3].lower())
        for d in (d1, d2):
            if m and d:
                try:
                    out.append(datetime.date(int(yr), m, int(d)))
                except ValueError:
                    pass
    return out


def last_checked(page):
    # the page's own summary line ("... · Facts checked 16 and 20 Nov 2026") wins, so the stamp says what the page says;
    # without one, the date the page's sources were most often checked
    line = re.search(r"Facts checked[^<]{0,60}", page)
    if line:
        ds = _dates(line.group(0))
        if ds:
            return max(ds)
    ds = _dates(page)
    return max(set(ds), key=lambda d: (ds.count(d), d)) if ds else None


def band(ja, en, kind, checked):
    k, label, sec, href = KIND[kind]
    return ('<!-- jp-band -->\n<div class="jp-band"><div class="jp-band-in">'
            '<p class="jp-crumb"><a href="/japan">🇯🇵 Japan hub</a><span>›</span><a href="%s">%s</a><span>›</span>%s</p>'
            '<div class="jp-namesign"><span class="jp-namesign-e"><small>🇯🇵 <span lang="ja">ようこそ · %s</span> · %s</small>'
            '<span class="jp-welcome"><span class="jp-namesign-k" lang="ja">%s</span> <em>%s</em></span></span>'
            '<span class="jp-namesign-st" title="Checked against official sources">確認<br>%s</span></div>'
            '</div></div>\n<!-- /jp-band -->\n') % (href, sec, en, k, label, ja, en, checked.strftime("%-d %b %Y").upper().replace(" 20", "<br>20", 1))


plans, problems = {}, []
for slug, (ja, en, kind) in GUIDES.items():
    path = os.path.join(BLOG, slug + ".html")
    if not os.path.isfile(path):
        problems.append(slug + " (missing)")
        continue
    s = open(path, encoding="utf-8").read()
    new = BAND.sub("", s)
    checked = last_checked(new)
    hero = HERO.search(new)
    if not checked or not hero:
        problems.append(slug + (" (no checked date)" if not checked else " (no hero)"))
        continue
    new = new[:hero.end()] + band(ja, en, kind, checked) + new[hero.end():]
    hero_old = new[hero.start():hero.end()]
    if OLD_TINT in hero_old:
        new = new[:hero.start()] + hero_old.replace(OLD_TINT, NEW_TINT, 1) + new[hero.end():]
    elif NEW_TINT not in hero_old and "url(" in hero_old:   # a hero without a photo (New Chitose) keeps its own colour
        problems.append(slug + " (hero tint not recognised)")
        continue
    new = BG.sub("", new)
    bm = re.search(r"<body[^>]*>\n?", new)
    if not bm:
        problems.append(slug + " (<body>)")
        continue
    new = new[:bm.end()] + SAKURA_BG + new[bm.end():]
    new = ASK.sub("", new)
    tm = TOPIC.search(new)
    if tm:
        bar = new.find('\n<div id="psnBar"')
        if bar < 0:
            problems.append(slug + " (no section bar)")
            continue
        new = new[:bar + 1] + ask_box(en, tm.group(1)) + new[bar + 1:]
    if 'id="jp-guide-css"' in new:
        new = re.sub(r'<style id="jp-guide-css">.*?</style>\n', lambda m: CSS, new, count=1, flags=re.S)
    else:
        heads = list(re.finditer(r"(?m)^[ \t]*</head>", new))
        if len(heads) != 1:
            problems.append(slug + " (</head>)")
            continue
        new = new[:heads[0].start()] + CSS + new[heads[0].start():]
    if new != s:
        plans[path] = new
if problems:
    sys.exit("w77 aborted, nothing written: " + ", ".join(problems))
for path, s in plans.items():
    open(path, "w", encoding="utf-8").write(s)
print("w77 done. Japan band on %d guides; %d file(s) changed." % (len(GUIDES), len(plans)))
