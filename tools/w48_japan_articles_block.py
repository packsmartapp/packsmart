#!/usr/bin/env python3
"""
w48: "Pocket guides" journey-line card inside the Japan articles.

One card per article, built from tools/pocket_guides.json (guides of one country, grouped by their "stop" in the
country's "stop_order", for Japan: Tokyo, Kyoto, Osaka). The guides that fit the article carry a "Start here" tag.
Under the route sits a short "what's inside" strip and the three-tap save line.

Links carry ?src=art_<tag>; a tap sends one anonymous GA4 event (pg_article_tap: to, article) when gtag is on the page.
No partner links in this card: it only sends people to the guides, and the offers live inside the guides.

Run from the repo root, after w47:   python3 tools/w48_japan_articles_block.py
Idempotent (marker data-pga="japan-v2"). Writes nothing at all if any article is missing its insertion point.

Eleven pages. Every card sits near the top: after the visa section (packing guides), before the itinerary (7-day), right
after the "on one page" summary (city guides, and the six airport and station guides, where the page's own guide is left
out and the next stops lead).

To add a guide: add it to tools/pocket_guides.json with "country": "Japan" and a "stop" (a new stop goes into
"stop_order" too), then re-run. To change the colours: edit the BG / ACCENT block below and re-run on a clean checkout
(or replace the block between the <style id="pga-css"> tags by hand).
"""
import json
import os
import sys

ROOT = os.getcwd()
PUB = os.path.join(ROOT, "public")
BLOG = os.path.join(PUB, "blog")
IMG = os.path.join(PUB, "images")
REG = os.path.join(ROOT, "tools", "pocket_guides.json")
MARK = 'data-pga="japan-v2"'
COUNTRY = "Japan"

# ---- colours (one place to change) -------------------------------------------------------------------------
BG = "linear-gradient(160deg,#2f6fe0 0%,#6a4fd0 55%,#9a46b0 100%)"   # card top. Brand alternative: linear-gradient(160deg,#0f0f23 0%,#0f2f3f 55%,#0b5d57 100%)
LINE = "rgba(255,255,255,.7)"          # route line. Brand alternative: rgba(0,201,167,.75)
DOT = "#fff"                           # route dot and its halo colour
DOT_HALO = "rgba(255,255,255,.3)"
PILL_BG, PILL_FG = "#fff", "#0b5d57"   # "Start here" tag. Brand alternative: #00C9A7 on #0f0f23
RING = "#fff"                          # ring round the "Start here" icons. Brand alternative: #00C9A7
KICK = "background:rgba(255,255,255,.22);border:1px solid rgba(255,255,255,.35);color:#fff"
# -------------------------------------------------------------------------------------------------------------

TITLE = "Landing in Japan? Keep the guide in your pocket."
SUB = ("Short, big-print helpers for Japan's airports and stations. Open one, save it to your home screen, "
       "and it works with no signal. Free, no app store, no account.")
SUB_TRIP = ("Pocket guides for the airport you land at and the stations on the way to Kyoto. Open one, save it to your home screen, "
            "and it works with no signal. Free, no app store, no account.")
SUB_NEXT = ("Short, big-print helpers for the next stops. Open one, save it to your home screen, "
            "and it works with no signal. Free, no app store, no account.")
TICKS = ["<b>Finds things fast.</b> Toilets, lockers, food, exits and trains.",
         "<b>Big print.</b> Easy to show station or airport staff.",
         "<b>No signal needed</b> once it is saved."]
FOOT = ("<b>Save it in three taps:</b> open a guide, then on Android tap Install, "
        "or on iPhone tap Share and then Add to Home Screen.")

# slug: (tag for ?src=, "Start here" guide keys, title, sub, anchor kind, anchor)
#   "before": insert before the anchor string (must occur exactly once)
#   "after_list": insert after the first </ul> that follows the anchor string (anchor must occur exactly once)
ARTICLES = {
    "japan-travel-packing-guide": ("japan-packing", ["narita", "haneda"], TITLE, SUB,
                                   "before", "<!-- narita-airport-guide link -->"),
    "japan-travel-packing-guide-from-india": ("japan-packing-in", ["narita", "haneda"], TITLE, SUB,
                                              "before", '<h2 id="weather">'),
    "japan-7-day-itinerary-budget": ("japan-7day", ["narita", "haneda"],
                                     "Landing in Tokyo, then on to Kyoto? Keep the guides in your pocket.", SUB_TRIP,
                                     "before", '<h2 id="itinerary">'),
    "kyoto-travel-guide": ("kyoto-city", ["kyoto", "kix"],
                           "Arriving in Kyoto? Keep the guide on your phone.", SUB,
                           "before", '<h2 id="areas">'),
    "osaka-travel-guide": ("osaka-city", ["osaka", "kix"],
                           "Arriving in Osaka? Keep the guide on your phone.", SUB,
                           "before", '<h2 id="areas">'),
    # airport and station guides: card right after the "on one page" box and its QR code; the page's own guide is left out; the next stops lead
    "narita-airport-guide": ("narita-airport", ["tokyo"], "Heading into Tokyo? Keep the guides in your pocket.", SUB_NEXT,
                             "before", '<h2 id="terminals">', ["narita"]),
    "haneda-airport-guide": ("haneda-airport", ["tokyo"], "Heading into Tokyo? Keep the guides in your pocket.", SUB_NEXT,
                             "before", '<h2 id="terminals">', ["haneda"]),
    "kansai-airport-guide": ("kansai-airport", ["osaka", "kyoto"], "Heading into the city? Keep the guides in your pocket.", SUB_NEXT,
                             "before", '<h2 id="terminals">', ["kix"]),
    "tokyo-station-guide": ("tokyo-station", ["kyoto", "osaka"], "Heading on by bullet train? Keep the guides in your pocket.", SUB_NEXT,
                            "before", '<h2 id="which-side">', ["tokyo"]),
    "kyoto-station-guide": ("kyoto-station", ["osaka", "kix"], "Heading on? Keep the guides in your pocket.", SUB_NEXT,
                            "before", '<h2 id="which-side">', ["kyoto"]),
    "osaka-station-guide": ("osaka-station", ["kyoto", "kix"], "Heading on? Keep the guides in your pocket.", SUB_NEXT,
                            "before", '<h2 id="which-station">', ["osaka"]),
}

CSS = """<style id="pga-css">
.pga{max-width:800px;margin:28px auto;border-radius:26px;overflow:hidden;background:#fff;border:1px solid #dfe8e5;box-shadow:0 12px 30px rgba(15,15,35,.14);font-family:"DM Sans",sans-serif;color:#1b1f33;line-height:1.45}
.pga *{box-sizing:border-box}
.pga-top{padding:26px 28px 22px;background:@BG@;color:#fff}
.pga .pga-kick{display:inline-block;font-size:11px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;border-radius:20px;padding:4px 12px;margin:0 0 10px;line-height:1.4;@KICK@}
.pga .pga-title{margin:0 0 6px;font-size:25px;line-height:1.2;font-weight:800;color:#fff}
.pga .pga-sub{margin:0 0 20px;font-size:15px;line-height:1.5;color:#fff;max-width:560px}
.pga-route{display:flex;align-items:flex-start;padding-top:6px}
.pga-stop{display:grid;grid-template-columns:16px auto 1fr;grid-template-rows:auto auto;align-items:center;min-width:0;flex-shrink:1}
.pga-dot{width:16px;height:16px;border-radius:50%;background:@DOT@;box-shadow:0 0 0 4px @HALO@}
.pga .pga-city{margin-left:10px;font-size:12px;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:#fff;line-height:16px}
.pga-ln{height:2px;background:@LINE@;margin:0 14px 0 12px}
.pga-icons{grid-column:1/-1;margin-top:22px;display:flex;flex-wrap:wrap;gap:6px;align-self:start}
.pga a.pga-t{display:flex;flex-direction:column;align-items:center;gap:6px;position:relative;padding-top:24px;width:86px;text-decoration:none!important;color:#fff!important}
.pga a.pga-t img{width:64px;height:64px;border-radius:23%;display:block;box-shadow:0 6px 14px rgba(0,0,0,.35);transition:transform .15s}
.pga a.pga-t.lead img{box-shadow:0 0 0 3px @RING@,0 6px 14px rgba(0,0,0,.35)}
.pga a.pga-t:hover img,.pga a.pga-t:focus-visible img{transform:scale(1.07)}
.pga a.pga-t b{font-size:13px;font-weight:700;line-height:1.1;text-align:center}
.pga a.pga-t em{position:absolute;top:0;left:50%;transform:translateX(-50%);font-style:normal;font-size:10px;font-weight:800;letter-spacing:.05em;text-transform:uppercase;background:@PILL_BG@;color:@PILL_FG@;border-radius:10px;padding:2px 8px;white-space:nowrap;line-height:1.4}
.pga-ticks{padding:16px 28px;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px 18px}
.pga-tick{display:flex;gap:9px;align-items:flex-start;font-size:14px;line-height:1.35;color:#1b1f33}
.pga-tick::before{content:"\\2713";flex:none;width:22px;height:22px;border-radius:50%;background:#D9F7EF;color:#0b5d57;font-weight:800;font-size:12px;display:flex;align-items:center;justify-content:center}
.pga .pga-foot{margin:0;padding:12px 28px 14px;border-top:1px solid #edf1f0;font-size:13.5px;line-height:1.5;color:#4a5268}
.pga .pga-foot b{color:#0f0f23}
@media (max-width:700px){
.pga{margin:22px 0;border-radius:20px}
.pga-top{padding:20px 16px 18px}
.pga .pga-title{font-size:21px}
.pga .pga-sub{font-size:14.5px;margin-bottom:18px}
.pga-route{display:block;padding-top:0}
.pga-stop{display:grid;grid-template-columns:16px 1fr;grid-template-rows:auto auto;column-gap:12px;align-items:start;padding-bottom:20px}
.pga-stop:last-child{padding-bottom:0}
.pga-dot{grid-column:1;grid-row:1}
.pga .pga-city{grid-column:2;grid-row:1;margin-left:0}
.pga-ln{grid-column:1;grid-row:2;width:2px;height:auto;margin:4px 0 0;justify-self:center;align-self:stretch}
.pga-icons{grid-column:2;grid-row:2;margin-top:12px;gap:4px}
.pga a.pga-t{width:78px}
.pga-icons:not(.hl) a.pga-t{padding-top:0}
.pga a.pga-t img{width:56px;height:56px}
.pga-ticks{grid-template-columns:1fr;padding:16px}
.pga .pga-foot{padding:12px 16px 14px}
}
@media print{.pga{display:none!important}}
</style>
"""

JS = ("<script>(function(){var b=document.getElementById('pocket-guides-japan');if(!b)return;"
      "b.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('[data-pga-to]');if(!a)return;"
      "try{if(window.gtag)gtag('event','pg_article_tap',{event_category:'engagement',to:a.getAttribute('data-pga-to'),"
      "article:b.getAttribute('data-pga-article'),page_path:location.pathname});}catch(x){}});})();</script>\n")


def die(msg):
    sys.exit("w48 aborted, nothing written: " + msg)


if not os.path.isfile(REG):
    die("run from the repo root (cannot find tools/pocket_guides.json)")
reg = json.load(open(REG, encoding="utf-8"))
guides = [g for g in reg["guides"] if g["country"] == COUNTRY]
by_key = {g["key"]: g for g in guides}
stop_order = (reg.get("stop_order") or {}).get(COUNTRY) or []
if not stop_order:
    die('registry has no "stop_order" for ' + COUNTRY)
for g in guides:
    if g.get("stop") not in stop_order:
        die("guide %s has no valid \"stop\" (got %r; stops are %s)" % (g["key"], g.get("stop"), stop_order))
    if not os.path.isfile(os.path.join(IMG, g["icon"])):
        die("missing icon public/images/" + g["icon"])
    if not os.path.isfile(os.path.join(PUB, g["key"] + "-pocket.html")):
        die("no pocket page for " + g["key"])


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def tile(g, tag, lead):
    pill = "<em>Start here</em>" if lead else ""
    return ('<a class="pga-t%s" href="/%s-pocket?src=art_%s" data-pga-to="%s">%s<img src="/images/%s" alt="" width="64" height="64" loading="lazy"><b>%s</b></a>'
            % (" lead" if lead else "", g["key"], tag, g["key"], pill, g["icon"], esc(g.get("label") or g["name"])))


def block(slug, tag, lead, title, sub, exclude=()):
    for k in lead:
        if k not in by_key:
            die("%s: Start-here guide %s is not in the registry" % (slug, k))
    stops = []
    pool = [g for g in guides if g["key"] not in exclude]
    shown = [s for s in stop_order if any(g["stop"] == s for g in pool)]
    for i, s in enumerate(shown):
        mine = [g for g in pool if g["stop"] == s]
        mine.sort(key=lambda g: (0, lead.index(g["key"])) if g["key"] in lead else (1, 0))
        last = i == len(shown) - 1
        stops.append('<div class="pga-stop" style="flex:%s 1 0"><span class="pga-dot"></span><span class="pga-city">%s</span>%s<div class="pga-icons%s">%s</div></div>'
                     % (len(mine) + 0.7, esc(s), "" if last else '<span class="pga-ln"></span>',
                        " hl" if any(g["key"] in lead for g in mine) else "",
                        "".join(tile(g, tag, g["key"] in lead) for g in mine)))
    ticks = "".join('<div class="pga-tick"><span>%s</span></div>' % t for t in TICKS)
    return ('<aside class="pga" id="pocket-guides-japan" %s data-pga-article="%s" role="complementary" aria-label="Offline pocket guides for Japan">'
            '<div class="pga-top"><span class="pga-kick">Free offline pocket guides</span>'
            '<p class="pga-title">%s</p><p class="pga-sub">%s</p><div class="pga-route">%s</div></div>'
            '<div class="pga-ticks">%s</div><p class="pga-foot">%s</p></aside>\n' % (MARK, tag, title, sub, "".join(stops), ticks, FOOT))


css = (CSS.replace("@BG@", BG).replace("@KICK@", KICK).replace("@DOT@", DOT).replace("@HALO@", DOT_HALO)
       .replace("@LINE@", LINE).replace("@RING@", RING).replace("@PILL_BG@", PILL_BG).replace("@PILL_FG@", PILL_FG))

plans = []
for slug, spec in ARTICLES.items():
    tag, lead, title, sub, kind, anchor = spec[:6]
    exclude = spec[6] if len(spec) > 6 else []
    path = os.path.join(BLOG, slug + ".html")
    if not os.path.isfile(path):
        die("missing article " + os.path.relpath(path, ROOT))
    s = open(path, encoding="utf-8").read()
    if MARK in s:
        plans.append((path, None, slug))
        continue
    if s.count(anchor) != 1:
        die("%s: insertion point %r found %d times (need exactly 1)" % (slug, anchor, s.count(anchor)))
    i = s.index(anchor)
    if kind == "after_list":
        j = s.find("</ul>", i)
        if j < 0:
            die("%s: no </ul> after %r" % (slug, anchor))
        i = j + len("</ul>")
        i = i + 1 if s[i:i + 1] == "\n" else i
    new = s[:i] + ("" if "pga-css" in s else css) + block(slug, tag, lead, title, sub, exclude) + JS + s[i:]
    plans.append((path, new, slug))

for path, new, slug in plans:
    if new is None:
        print("unchanged (already done):", slug)
        continue
    open(path, "w", encoding="utf-8").write(new)
    print("updated:", slug)
