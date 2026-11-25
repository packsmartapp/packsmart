#!/usr/bin/env python3
"""
w77: a light Japan band at the top of the Japan station, airport and city guides, and the three general Japan articles
(travel guide, its from-India version, the 7-day itinerary) (25 Nov 2026).

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
    # the three general Japan articles (added 25 Nov 2026); without a checked date the band shows no stamp
    "japan-travel-packing-guide": ("日本", "Japan", "trip"),
    "japan-travel-packing-guide-from-india": ("日本", "Japan", "trip"),
    "japan-7-day-itinerary-budget": ("日本・7日間", "Japan in 7 days", "itinerary"),
}
OPTIONAL_STAMP = {"japan-travel-packing-guide", "japan-travel-packing-guide-from-india", "japan-7-day-itinerary-budget"}
KIND = {"station": ("駅", "Station guide", "Stations", "/japan#stations"),
        "airport": ("空港", "Airport guide", "Airports", "/japan#arriving"),
        "city": ("観光", "City guide", "Plan your trip", "/japan#plan"),
        "trip": ("旅の準備", "Travel guide", "Plan your trip", "/japan#plan"),
        "itinerary": ("旅程", "Itinerary", "Plan your trip", "/japan#plan")}
MONTHS = {m: i for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}
OLD_TINT = "linear-gradient(rgba(15,15,35,0.62), rgba(26,26,62,0.72))"
OLD_TINTS = (OLD_TINT, "linear-gradient(rgba(15,15,35,0.7), rgba(26,26,62,0.7))")
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
class _Hero:
    """The hero <div class="hero-blog"> up to its own closing </div> and line end (nested divs counted)."""
    def __init__(self, start, end): self._s, self._e = start, end
    def start(self): return self._s
    def end(self): return self._e


def find_hero(page):
    i = page.find('<div class="hero-blog"')
    if i < 0:
        return None
    depth, pos = 0, i
    for m in re.finditer(r"<div\b|</div>", page[i:]):
        depth += 1 if m.group(0) != "</div>" else -1
        if depth == 0:
            end = i + m.end()
            nl = page.find("\n", end)
            return _Hero(i, nl + 1 if nl >= 0 else end)
    return None
BAND = re.compile(r"<!-- jp-band -->.*?<!-- /jp-band -->\n", re.S)

WAVE = ("url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='40' height='20'%3E%3Cg fill='none' "
        "stroke='%2300C9A7' stroke-opacity='.18'%3E%3Cpath d='M0 20a10 10 0 0 1 20 0M5 20a5 5 0 0 1 10 0M20 20a10 10 0 0 1 20 0M25 20a5 5 0 0 1 10 0"
        "M-10 10a10 10 0 0 1 20 0M10 10a10 10 0 0 1 20 0M30 10a10 10 0 0 1 20 0'/%3E%3C/g%3E%3C/svg%3E\")")
CSS_RAW = """<style id="jp-guide-css">
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
 article.article{padding-top:48px;padding-bottom:48px}
 .jp-band{border-bottom:0;padding:22px 16px 6px}
 .jp-bg{opacity:0;transition:opacity .5s}.jp-bg.on{opacity:1}
 .content .pga,.content [data-ps-placement],.content .ps-kd,.content .related-posts,.content .psn-now,.content .jg-ask{max-width:none!important}
 .content .related-posts{padding:0;margin:2.4rem 0 1rem}
 .content .related-grid{grid-template-columns:repeat(3,minmax(0,1fr));gap:1.1rem}
 .content .related-card-body{padding:1.1rem 1.2rem}
}
/* the partner's city search overlay is positioned from the box edge, so it must not be a grid item */
.ps-pickups>.ps-dest{grid-column:auto!important;grid-row:auto!important}
/* wide screens: the airport-transfer box as photo | benefits and booking form (owner's pick, option C, 25 Nov). The
   partner's form keeps its own field layout; its city search re-positions itself every 0.4 s, so it follows */
@media (min-width:1200px) and (max-width:1499px){.ps-pickups{display:grid!important;grid-template-columns:minmax(0,1fr) minmax(0,1fr);column-gap:28px;align-items:center}
 .ps-pickups>:where(:not(.ps-dest)){grid-column:1/-1}.ps-pickups>h3{grid-row:1}
 .ps-pickups>picture{grid-column:1;grid-row:2/4;margin-bottom:16px}.ps-pickups>picture img{margin:0!important}
 .ps-pickups>picture+strong{grid-column:2;grid-row:2;align-self:end}
 .ps-pickups>picture+strong+div{grid-column:2;grid-row:3;align-self:start;max-width:none!important}}
/* laptops (1200-1499 px) keep the form full width below; it needs about 800 px for its fields */
@media (min-width:1500px){.ps-pickups{display:grid!important;grid-template-columns:minmax(0,1fr) minmax(0,1fr);column-gap:24px;align-items:start}
 .ps-pickups>:where(:not(.ps-dest)){grid-column:1/-1}
 .ps-pickups>h3{grid-row:1}
 .ps-pickups>picture{grid-column:1;grid-row:2/5}.ps-pickups>picture img{margin:0!important}
 .ps-pickups>picture+strong{grid-column:2;grid-row:2}
 .ps-pickups>picture+strong+div{grid-column:2;grid-row:3;max-width:none!important}
 .ps-pickups>picture+strong+div+*{grid-column:2;grid-row:4}
 /* half width: the city search on its own row, From and To side by side under it (they overlapped) */
 .content .ps-pickups.ps-pickups form>div:nth-child(1){grid-column:1/-1!important}
 .content .ps-pickups.ps-pickups form>div:nth-child(2)>div:nth-child(1),.content .ps-pickups.ps-pickups form>div:nth-child(2)>div:nth-child(3){grid-column:span 12!important}}
/* wide screens: the eSIM box as photo | heading, plans and note (the photo was a full-width poster) */
@media (min-width:1200px){[data-ps-placement^="airalo-"]{display:grid!important;grid-template-columns:minmax(0,1fr) minmax(0,1fr);column-gap:28px;align-items:center}
 [data-ps-placement^="airalo-"]>:where(*){grid-column:2}
 [data-ps-placement^="airalo-"]>picture{grid-column:1;grid-row:1/6;display:block}[data-ps-placement^="airalo-"]>picture img{margin:0!important}
 [data-ps-placement^="airalo-"]>style{display:none}}
/* (the photo spans the chips' row and the next, so the search form starts right under the chips, not under the photo)
   the driving-permit tip runs the full width under both columns (owner, 25 Nov)
   wide screens: the car-hire box as photo, note and text on the left | pick-up choices and the partner's search form on
   the right (owner's layout, 25 Nov); the form is responsive (it already works at phone width) */
@media (min-width:1200px){[data-ps-placement^="discovercars-"]{display:grid!important;grid-template-columns:minmax(0,1fr) minmax(0,1fr);grid-template-rows:auto auto auto auto auto auto auto 1fr;column-gap:28px;align-items:start;padding-bottom:20px!important}
 [data-ps-placement^="discovercars-"]>:where(*){grid-column:1/-1}
 [data-ps-placement^="discovercars-"]>style,[data-ps-placement^="discovercars-"]>script{display:none}
 [data-ps-placement^="discovercars-"]>picture{grid-column:1;grid-row:2/4;display:block}
 [data-ps-placement^="discovercars-"]>p:nth-of-type(1){grid-column:1;grid-row:4;margin:6px 0 10px!important}
 [data-ps-placement^="discovercars-"]>p:nth-of-type(2){grid-column:1;grid-row:5}
 [data-ps-placement^="discovercars-"]>p:nth-of-type(3){grid-column:1;grid-row:6}
 [data-ps-placement^="discovercars-"]>p:nth-of-type(4){grid-column:1/-1;grid-row:9;margin:14px 0 0!important}
 [data-ps-placement^="discovercars-"]>.ps-dc-chips{grid-column:2;grid-row:2}
 [data-ps-placement^="discovercars-"]>.ps-dc-mount{grid-column:2;grid-row:3/9;margin-top:6px}}
/* wide screens: the travel-insurance box in two columns (owner, 25 Nov): heading, text, button and the Complete card on the
   left, the price calculator on the right, so the box is much shorter, and as wide as the text panel above it (it ran
   edge to edge); browsers without :has() keep the stacked box */
@media (min-width:1200px){div:has(>div>.safetywing-price-widget){display:grid;grid-template-columns:minmax(0,1fr) auto;grid-template-rows:auto auto auto auto 1fr;column-gap:36px;align-items:start;text-align:left!important;padding:28px 32px!important;max-width:var(--gw);box-sizing:border-box;margin:30px auto!important}
 div:has(>div>.safetywing-price-widget)>*{grid-column:1}
 div:has(>div>.safetywing-price-widget)>a{justify-self:start}
 div:has(>div>.safetywing-price-widget)>div:has(>.safetywing-price-widget){grid-column:2;grid-row:1/6;margin-top:0!important}
 div:has(>div>.safetywing-price-widget)>[data-ps-placement="safetywing-complete"]{grid-row:5;margin:20px 0 0!important;max-width:none!important}}
/* the transfer box without its own heading (the three general Japan articles): everything moves up a row, the fares line
   on 1500px+ the partner's form (its loader script is replaced by a div#powered_by_<promo>_<n>) joins the right column as
   on the guides and the fares line runs full width under the photo and form (owner preferred the guides' look);
   the slack goes under them (the form had jumped to the top) */
@media (min-width:1200px) and (max-width:1499px){.ps-pickups:not(:has(>h3))>picture{grid-row:1/3}.ps-pickups:not(:has(>h3))>picture+strong{grid-row:1}.ps-pickups:not(:has(>h3))>picture+strong+div{grid-row:2}}
@media (min-width:1500px){.ps-pickups:not(:has(>h3)){grid-template-rows:auto auto auto 1fr}
 .ps-pickups:not(:has(>h3))>picture{grid-row:1/5}.ps-pickups:not(:has(>h3))>picture+strong{grid-row:1}.ps-pickups:not(:has(>h3))>picture+strong+div{grid-row:2}
 .ps-pickups:not(:has(>h3))>[id^="powered_by_"]{grid-column:2;grid-row:3}
 .ps-pickups:not(:has(>h3))>picture+strong+div+p{grid-column:1/-1;grid-row:5;margin:14px auto 0!important}.ps-pickups:not(:has(>h3))>p:last-of-type{grid-row:6}}
/* wide screens: the fares line and the "Best when…" line run the full box width, one line each where they fit (owner, 25 Nov) */
@media (min-width:1200px){.ps-pickups>p{max-width:none!important}.ps-pickups>picture+strong+div+p{margin:12px auto 0!important}.ps-pickups>p:last-of-type{margin-top:8px!important}}
/* (the partner's Continue button style moved to w78, which covers every page with the transfer box) */
/* wide screens: the "No eSIM?" travel SIM and pocket Wi-Fi box spreads to the panel, and each card puts its picture beside
   its text on 1500px+, so the wider box does not get taller (owner, 25 Nov; at 1280px the cards were too narrow) */
@media (min-width:1200px){div:has(>div>.ps-sk-tile){max-width:none!important}}
@media (min-width:1500px){div:has(>div>.ps-sk-tile) .ps-sk-tile{display:grid!important;grid-template-columns:minmax(150px,40%) minmax(0,1fr);column-gap:18px;align-items:center;text-align:left!important;padding:22px 18px 16px!important}
 div:has(>div>.ps-sk-tile) .ps-sk-tile>span:nth-child(2){grid-column:1;grid-row:1/9;margin:0!important}
 div:has(>div>.ps-sk-tile) .ps-sk-tile>span:not(:nth-child(-n+2)){grid-column:2}
 div:has(>div>.ps-sk-tile) .ps-sk-tile>span[style*="flex:1"]{display:none!important}}
/* wide screens: the day-tour and experience boxes (.ps-exp, Kyoto and Osaka city guides) put the photo on the left and the
   text on the right (owner, 25 Nov; the full-width banner looked stretched). The photo fills its column (a plain photo,
   so cropping is fine); the credit stays under it. A box without a photo (the park ticket) stays as it is */
@media (min-width:1200px){.ps-exp:has(>figure){display:grid;grid-template-columns:minmax(0,5fr) minmax(0,6fr);grid-template-rows:auto auto auto auto 1fr;column-gap:28px;align-items:start}
 .ps-exp:has(>figure)>*{grid-column:2}
 .ps-exp>figure{grid-column:1;grid-row:1/7;align-self:stretch;display:flex;flex-direction:column;margin:0!important}
 .ps-exp>figure>a{flex:1;display:block;min-height:200px}
 .ps-exp>figure img{height:100%!important;max-height:none!important;aspect-ratio:auto!important;object-fit:cover}
 .ps-exp:has(>figure)>a.go{justify-self:start}}
/* car-hire box, second pass (owner, 25 Nov): one text colour for the three paragraphs (they were #444, #666, #666 and
   looked uneven); on 1500px+ the pick-up buttons get their own row under the heading, the photo and the search form sit
   side by side at the same height (columns 3:2), and the two paragraphs and the tip run full width under them, so the box is shorter and the text lines longer */
@media (min-width:1200px){[data-ps-placement^="discovercars-"]>p:nth-of-type(n+2){color:#444!important}}
@media (min-width:1500px){[data-ps-placement^="discovercars-"]{grid-template-columns:minmax(0,3fr) minmax(0,2fr);grid-template-rows:auto auto auto auto auto auto auto}
 [data-ps-placement^="discovercars-"]>h3{grid-column:1/-1;grid-row:1}
 [data-ps-placement^="discovercars-"]>.ps-dc-chips{grid-column:1/-1;grid-row:2;margin:0 0 16px!important}
 [data-ps-placement^="discovercars-"]>picture{grid-column:1;grid-row:3}
 [data-ps-placement^="discovercars-"]>.ps-dc-mount{grid-column:2;grid-row:3;margin-top:0}
 [data-ps-placement^="discovercars-"]>p:nth-of-type(1){grid-column:1;grid-row:4;margin:6px 0 10px!important}
 [data-ps-placement^="discovercars-"]>p:nth-of-type(2){grid-column:1/-1;grid-row:5}
 [data-ps-placement^="discovercars-"]>p:nth-of-type(3){grid-column:1/-1;grid-row:6}
 [data-ps-placement^="discovercars-"]>p:nth-of-type(4){grid-column:1/-1;grid-row:7;margin:6px 0 0!important}}
/* the "Explore all our Japan guides" callout beside the Published line (owner, 25 Nov) */
p.jg-disc{font-size:.72rem!important;color:#8a8f9c!important;margin:.2rem 0 1.2rem!important;line-height:1.5!important}.jg-disc span{color:#b4bccb;margin-right:2px}.jg-disc a{color:#0a8f78;text-decoration:underline}
.jg-meta{display:grid;grid-template-columns:minmax(0,1fr) auto;column-gap:28px;align-items:start;margin:0 0 1.6rem}
.jg-meta>p{grid-column:1;margin:0!important}
.jg-meta>p.jg-disc{margin:10px 0 0!important}
.jg-meta>.jg-hubp{grid-column:2;grid-row:1/3;align-self:start;margin:-4px 0 0}
.jg-hubp{display:inline-flex;align-items:center;gap:10px;background:#FDF0F2 """ + WAVE + """;border:1px solid #F3D3DA;border-radius:14px;padding:7px 12px 7px 8px;text-decoration:none!important;color:#0f0f23!important;box-shadow:0 4px 14px rgba(233,69,96,.08);transition:transform .15s,box-shadow .15s}
.jg-hubp:hover,.jg-hubp:focus-visible{transform:translateY(-1px);box-shadow:0 8px 20px rgba(233,69,96,.16)}
.jg-hubp-i{flex:none;width:44px;height:36px;background:linear-gradient(180deg,#fff7f0,#fde6ea);border-radius:9px;overflow:hidden}
.jg-hubp-i svg{display:block;width:100%;height:100%}
.jg-hubp-t{display:flex;flex-direction:column;line-height:1.25}
.jg-hubp-t b{font-size:.9rem;font-weight:700;color:#0f0f23}
.jg-hubp-t em{font-family:'Instrument Serif',Georgia,serif;font-style:italic;font-weight:400;color:#E94560;font-size:1.15em}
.jg-hubp-t small{font-size:.74rem;color:#5a6378}
.jg-hubp-a{flex:none;width:28px;height:28px;border-radius:50%;border:2px solid #00C9A7;display:grid;place-items:center;font-weight:700;color:#0a8f78;transition:background .15s,color .15s}
.jg-hubp:hover .jg-hubp-a,.jg-hubp:focus-visible .jg-hubp-a{background:#00C9A7;color:#fff}
@media (max-width:900px){.jg-meta{grid-template-columns:1fr}.jg-meta>.jg-hubp{grid-column:1;grid-row:2;margin:14px 0 0}.jg-meta>p.jg-disc{grid-row:3}}
@media (max-width:600px){.jg-hubp{width:100%;box-sizing:border-box}.jg-hubp-t{flex:1}}
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
/* small phones: a tighter label so the stamp never covers it (360px) */
@media (max-width:400px){.jp-namesign-e small{letter-spacing:.06em;padding:5px 10px;font-size:.7rem}}
</style>
"""
CSS = CSS_RAW.replace(".content", ":is(.content,.article)")  # the from-India page uses <article class="article">


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


# A small "Explore all our Japan guides" callout (to the hub) to the right of the guide's "Published · Last updated · Facts checked" line (owner,
# 25 Nov): the line and the callout share one row on wide screens; on phones the callout sits under the line.
# The date line and the disclosure line sit in the left column, the callout on the right, top-aligned with the date
# line (owner, 25 Nov); on phones: date line, callout, disclosure.
META = re.compile(r'(<p style="font-size:0\.85rem;color:#666;margin:0 0 0\.6rem;">Published [^<]*</p>\s*<p class="jg-disc">.*?</p>)', re.S)
META_OLD = re.compile(r'<!-- jg-meta --><div class="jg-meta">(?:<!-- jg-in -->)?(.*?)(?:<!-- /jg-in -->)?<!-- jg-hubp -->.*?<!-- /jg-hubp --></div><!-- /jg-meta -->', re.S)
HUBP = ('<!-- jg-hubp --><a class="jg-hubp" href="/japan?src=jp_top" '
        "onclick=\"try{if(window.gtag)gtag('event','hub_card',{event_category:'navigation',status:'jp_top',page_path:location.pathname});}catch(e){}\">"
        '<span class="jg-hubp-i" aria-hidden="true"><svg viewBox="0 0 44 36"><circle cx="31" cy="11" r="6" fill="#E94560"/>'
        '<path d="M2 32 16 15q6-6 12 0l14 17z" fill="#4f6aa6"/><path d="M16 15q6-6 12 0l-2.5 3-2-2-2 2.5-1.5-2-2 2-2-1.5z" fill="#fff"/>'
        '<path d="M0 32h44v4H0z" fill="#9fd8cf"/></svg></span>'
        '<span class="jg-hubp-t"><b>Explore all our <em>Japan</em> guides</b><small>Airports, stations, offline Pocket Guides and Ask Packy</small></span>'
        '<span class="jg-hubp-a" aria-hidden="true">→</span></a><!-- /jg-hubp -->')


def band(ja, en, kind, checked):
    k, label, sec, href = KIND[kind]
    stamp = ('<span class="jp-namesign-st" title="Checked against official sources">確認<br>%s</span>'
             % checked.strftime("%-d %b %Y").upper().replace(" 20", "<br>20", 1)) if checked else ""
    return ('<!-- jp-band -->\n<div class="jp-band"><div class="jp-band-in">'
            '<p class="jp-crumb"><a href="/japan">🇯🇵 Japan hub</a><span>›</span><a href="%s">%s</a><span>›</span>%s</p>'
            '<div class="jp-namesign"><span class="jp-namesign-e"><small>🇯🇵 <span lang="ja">ようこそ · %s</span> · %s</small>'
            '<span class="jp-welcome"><span class="jp-namesign-k" lang="ja">%s</span> <em>%s</em></span></span>'
            '%s</div>'
            '</div></div>\n<!-- /jp-band -->\n') % (href, sec, en, k, label, ja, en, stamp)


# The affiliate disclosure stays (FTC and UK rules, and the partner programmes, want it before the first partner link),
# but on these pages as one quieter line without the divider (owner, 25 Nov: the old one "disturbed the design").
DISC_OLD = ('<p style="font-size:0.82rem;color:#999;margin-bottom:0.5rem;padding-bottom:0.8rem;border-bottom:1px solid #eee;">'
            'This article contains affiliate links. If you make a purchase through these links, we may earn a small commission '
            'at no extra cost to you. <a href="/affiliate-disclosure" style="color:#00C9A7;">Learn more</a></p>')
DISC_RX = re.compile(re.escape(DISC_OLD[:-len('</a></p>')]) + r'</a>\.?</p>')   # the guides end with "Learn more</a>."
DISC_NEW = ('<p class="jg-disc"><span aria-hidden="true">ⓘ</span> This guide has affiliate (partner) links: if you book through '
            'them, we may earn a small commission at no extra cost to you. <a href="/affiliate-disclosure">Learn more</a></p>')
TIP_OLD = ("<strong>Tip:</strong> Most visitors need an International Driving Permit under the 1949 Geneva Convention (drivers "
           "from a few countries, such as Germany and France, use an official Japanese translation instead), plus their home "
           "licence and passport. Arrange it before you fly; it cannot be issued in Japan.")
TIP_NEW = ("<strong>Tip:</strong> Most visitors need an International Driving Permit (1949 Geneva Convention; drivers from Germany, "
           "France and a few other countries use an official Japanese translation instead), plus their licence and passport. "
           "Get it before you fly: it cannot be issued in Japan.")
plans, problems = {}, []
for slug, (ja, en, kind) in GUIDES.items():
    path = os.path.join(BLOG, slug + ".html")
    if not os.path.isfile(path):
        problems.append(slug + " (missing)")
        continue
    s = open(path, encoding="utf-8").read()
    new = BAND.sub("", s)
    checked = last_checked(new)
    hero = find_hero(new)
    if (not checked and slug not in OPTIONAL_STAMP) or not hero:
        problems.append(slug + (" (no checked date)" if not checked else " (no hero)"))
        continue
    new = new[:hero.end()] + band(ja, en, kind, checked) + new[hero.end():]
    hero_old = new[hero.start():hero.end()]
    old_tint = next((t for t in OLD_TINTS if t in hero_old), None)
    if old_tint:
        new = new[:hero.start()] + hero_old.replace(old_tint, NEW_TINT, 1) + new[hero.end():]
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
    new = new.replace(TIP_OLD, TIP_NEW)
    new = DISC_RX.sub(DISC_NEW, new)
    new = META_OLD.sub(r"\1", new)
    new, n = META.subn(lambda m: '<!-- jg-meta --><div class="jg-meta"><!-- jg-in -->' + m.group(1) + '<!-- /jg-in -->' + HUBP + '</div><!-- /jg-meta -->', new, count=1)
    if not n and '<p style="font-size:0.85rem;color:#666;margin:0 0 0.6rem;">Published ' in new:
        problems.append(slug + " (date line and disclosure not found together)")
        continue
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
print("w77 done. Japan band on %d pages; %d file(s) changed." % (len(GUIDES), len(plans)))
