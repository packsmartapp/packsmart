#!/usr/bin/env python3
"""
w49: trip picker ("which guides do you need?") in the Japan articles. Replaces the w48 journey-line card.

Two questions, answered by tapping chips: where do you land (one airport, or "not sure yet"), and where are you going
after that (Tokyo, Kyoto, Osaka, any number). The guides that fit appear below as tiles, the arrival airport first with
a "Start here" tag. Each page can pre-pick answers it already knows (the 7-day itinerary: Tokyo and Kyoto), and the six
airport and station guides leave their own guide out.

Data comes from tools/pocket_guides.json: type (Airport/Station), stop (Tokyo/Kyoto/Osaka), label, chip (the airport's
chip text), chip_rank (order of the airport chips), icon, blurb; "stop_order" for the order of the cities. Add a guide there and re-run to add it to the picker.

Links carry ?src=art_<tag>. Two anonymous GA4 events when gtag is on the page: pg_article_pick (article, arrival,
stops, guides) when someone answers, and pg_article_tap (to, article, page_path) when they open a guide. No accounts,
no storage, no partner links. Without JavaScript the pre-picked guides are plain links.

Run from the repo root, after w48:   python3 tools/w49_trip_picker.py
Idempotent (marker data-pga="japan-v4"; replaces a v3 picker in place). Writes nothing at all if any page is not ready (needs the w48 card, which it
replaces in place, or is missing).

To change the colours: edit the block below and re-run on a clean checkout (or replace the <style id="pga-css"> block).
"""
import html
import json
import os
import sys

ROOT = os.getcwd()
PUB = os.path.join(ROOT, "public")
BLOG = os.path.join(PUB, "blog")
IMG = os.path.join(PUB, "images")
REG = os.path.join(ROOT, "tools", "pocket_guides.json")
OLDS = ('data-pga="japan-v2"', 'data-pga="japan-v3"')   # w48 card, or the v3 picker (one station per city; fixed 24 Nov 2026)
MARK = 'data-pga="japan-v4"'
COUNTRY = "Japan"

# ---- colours (one place to change) -------------------------------------------------------------------------
BG = "linear-gradient(160deg,#2f6fe0 0%,#6a4fd0 55%,#9a46b0 100%)"   # card top. Brand alternative: linear-gradient(160deg,#0f0f23 0%,#0f2f3f 55%,#0b5d57 100%)
KICK = "background:rgba(255,255,255,.22);border:1px solid rgba(255,255,255,.35);color:#fff"
CHIP_BG, CHIP_LINE = "rgba(15,10,60,.22)", "rgba(255,255,255,.6)"      # chip not picked
CHIP_ON_BG, CHIP_ON_FG = "#fff", "#2a2f8f"                             # chip picked
OPEN_BG = "#2f6fe0"                                                    # "Open" button. Brand alternative: #0b5d57
PILL_BG, PILL_FG = "#D9F7EF", "#0b5d57"                                # "Start here" tag
# -------------------------------------------------------------------------------------------------------------

TITLE = "Landing in Japan? Get the airport and station guides on your phone."
SUB = ("Find the ATMs, trains, buses, toilets, lockers, exits, emergency phone numbers, and easy Japanese words "
       "to talk or show to staff, all in one place. Add it to your Home Screen and it works even offline.")
Q1 = "Where do you land in Japan?"
Q2 = "Where are you going after that?"
EMPTY = "Your guides show up here as soon as you pick where you land and where you are headed."
FOOT = ("<b>Save each in three taps:</b> open it, then on Android tap Install, "
        "or on iPhone tap Share and then Add to Home Screen.")

# slug: dict(tag, title, anchor, pre = cities ticked already, exclude = guide keys left out, arrivals = airports offered)
#   anchor: insert-before string is not needed: the picker takes the exact place of the w48 card.
PAGES = {
    "japan-travel-packing-guide": dict(tag="japan-packing", title=TITLE),
    "japan-travel-packing-guide-from-india": dict(tag="japan-packing-in", title=TITLE),
    "japan-7-day-itinerary-budget": dict(tag="japan-7day", pre=["Tokyo", "Kyoto"], arrivals=["narita", "haneda"],
                                         title="Landing in Tokyo, then on to Kyoto? Get the guides on your phone."),
    "kyoto-travel-guide": dict(tag="kyoto-city", pre=["Kyoto"],
                               title="Arriving in Kyoto? Get the airport and station guides on your phone."),
    "osaka-travel-guide": dict(tag="osaka-city", pre=["Osaka"],
                               title="Arriving in Osaka? Get the airport and station guides on your phone."),
    "narita-airport-guide": dict(tag="narita-airport", pre=["Tokyo"], exclude=["narita"],
                                 title="Heading into Tokyo? Get the next guides on your phone."),
    "haneda-airport-guide": dict(tag="haneda-airport", pre=["Tokyo"], exclude=["haneda"],
                                 title="Heading into Tokyo? Get the next guides on your phone."),
    "kansai-airport-guide": dict(tag="kansai-airport", pre=["Osaka", "Kyoto"], exclude=["kix"],
                                 title="Heading into the city? Get the next guides on your phone."),
    "tokyo-station-guide": dict(tag="tokyo-station", pre=["Kyoto", "Osaka"], exclude=["tokyo"],
                                title="Heading on by bullet train? Get the next guides on your phone."),
    "kyoto-station-guide": dict(tag="kyoto-station", pre=["Osaka"], exclude=["kyoto"],
                                title="Heading on? Get the next guides on your phone."),
    "osaka-station-guide": dict(tag="osaka-station", pre=["Kyoto"], exclude=["osaka"],
                                title="Heading on? Get the next guides on your phone."),
    "shinjuku-station-guide": dict(tag="shinjuku-station", pre=["Kyoto"], exclude=["shinjuku"],
                                   title="Heading on? Get the next guides on your phone."),
    "ueno-station-guide": dict(tag="ueno-station", pre=["Kyoto"], exclude=["ueno"],
                               title="Heading on? Get the next guides on your phone."),
    "new-chitose-airport-guide": dict(tag="new-chitose-airport", pre=["Sapporo"], exclude=["new-chitose"],
                                      title="Heading into Sapporo? Get the next guides on your phone."),
    "sapporo-station-guide": dict(tag="sapporo-station", exclude=["sapporo"],
                                  title="Heading on? Get the next guides on your phone."),
}

CSS = """<style id="pga-css">
.pga{max-width:800px;margin:28px auto;border-radius:26px;overflow:hidden;background:#fff;border:1px solid #dfe8e5;box-shadow:0 12px 30px rgba(15,15,35,.14);font-family:"DM Sans",sans-serif;color:#1b1f33;line-height:1.45}
.pga *{box-sizing:border-box}
.pga-top{padding:26px 28px 24px;background:@BG@;color:#fff}
.pga .pga-kick{display:inline-block;font-size:11px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;border-radius:20px;padding:4px 12px;margin:0 0 10px;line-height:1.4;@KICK@}
.pga .pga-title{text-wrap:balance;margin:0 0 6px;font-size:25px;line-height:1.2;font-weight:800;color:#fff}
.pga .pga-sub{margin:0 0 22px;font-size:15px;line-height:1.5;color:#fff;max-width:600px}
.pgp-qs{display:flex;gap:32px}
.pgp-q{flex:1;min-width:0}
.pga .pgp-ql{margin:0 0 10px;font-size:15px;font-weight:800;line-height:1.3;color:#fff}
.pga .pgp-ql span{font-weight:500;opacity:.92;white-space:nowrap}
.pgp-chips{display:flex;flex-wrap:wrap;gap:8px}
.pga button.pgp-chip{appearance:none;cursor:pointer;font:inherit;font-size:14.5px;font-weight:700;line-height:1;color:#fff;background:@CHIP_BG@;border:1.5px solid @CHIP_LINE@;border-radius:22px;padding:10px 16px;display:inline-flex;align-items:center;gap:6px;transition:background .12s,color .12s}
.pga button.pgp-chip:hover{border-color:#fff}
.pga button.pgp-chip:focus-visible{outline:3px solid #fff;outline-offset:2px}
.pga button.pgp-chip[aria-pressed="true"]{background:@CHIP_ON_BG@;color:@CHIP_ON_FG@;border-color:#fff}
.pga button.pgp-chip[aria-pressed="true"]::before{content:"\\2713";font-weight:800}
.pgp-res{padding:20px 28px 22px}
.pga .pgp-h{margin:0 0 12px;font-size:15px;font-weight:800;color:#0f0f23}
.pga .pgp-empty{margin:0;font-size:14px;line-height:1.5;color:#5b6378}
.pgp-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}
.pga a.pgp-g{display:flex;flex-direction:column;align-items:flex-start;gap:6px;padding:14px 12px;border:1px solid #e3eae8;border-radius:14px;text-decoration:none!important;color:#0f0f23!important;transition:border-color .12s,box-shadow .12s}
.pga a.pgp-g:hover,.pga a.pgp-g:focus-visible{border-color:#9db3ff;box-shadow:0 4px 12px rgba(47,111,224,.18)}
.pga a.pgp-g img{width:52px;height:52px;border-radius:23%;display:block}
.pgp-gt{display:flex;flex-direction:column;gap:2px;flex:1;min-width:0}
.pga .pgp-gt b{font-size:14.5px;font-weight:800;line-height:1.2}
.pga .pgp-gt i{font-style:normal;font-size:12.5px;line-height:1.35;color:#4a5268}
.pga .pgp-gt em{align-self:flex-start;font-style:normal;font-size:10px;font-weight:800;letter-spacing:.05em;text-transform:uppercase;background:@PILL_BG@;color:@PILL_FG@;border-radius:10px;padding:2px 8px;line-height:1.5;margin-bottom:2px}
.pga .pgp-open{font-size:13px;font-weight:800;color:#fff;background:@OPEN_BG@;border-radius:18px;padding:8px 18px;margin-top:4px}
.pga .pga-foot{margin:16px 0 0;padding-top:14px;border-top:1px solid #edf1f0;font-size:13.5px;line-height:1.5;color:#4a5268}
.pga .pga-foot b{color:#0f0f23}
@media (max-width:700px){
.pga{margin:22px 0;border-radius:20px}
.pga-top{padding:20px 16px 18px}
.pga .pga-title{font-size:21px}
.pga .pga-sub{font-size:14.5px;margin-bottom:20px}
.pgp-qs{display:block}
.pgp-q+.pgp-q{margin-top:20px}
.pgp-res{padding:16px}
.pgp-grid{display:block}
.pga a.pgp-g{flex-direction:row;align-items:center;gap:12px;padding:10px 0;border:0;border-top:1px solid #edf1f0;border-radius:0;box-shadow:none!important}
.pga a.pgp-g img{width:46px;height:46px;flex:none}
.pga .pgp-open{margin-top:0;flex:none;padding:8px 14px}
}
@media print{.pga{display:none!important}}
</style>
"""

JS = r"""<script>(function(){var b=document.getElementById('pocket-guides-japan');if(!b)return;
var D=JSON.parse(b.getAttribute('data-guides')),art=b.getAttribute('data-pga-article'),O=b.getAttribute('data-order').split('|'),
arr='',st=(b.getAttribute('data-pre')||'').split('|').filter(Boolean),out=b.querySelector('.pgp-res'),isx=b.querySelector('.pgp-foot');
function E(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;')}
function pick(){var l=[],i,j,g;if(arr)for(i=0;i<D.length;i++)if(D[i].t==='Airport'&&D[i].k===arr)l.push([D[i],1]);
for(i=0;i<O.length;i++)if(st.indexOf(O[i])>-1)for(j=0;j<D.length;j++){g=D[j];if(g.t==='Station'&&g.s===O[i])l.push([g,0])}return l}
function tile(g,lead){return '<a class="pgp-g" href="/'+g.k+'-pocket?src=art_'+E(art)+'" data-pga-to="'+g.k+'" aria-label="Open the '+E(g.n)+' pocket guide"><img src="/images/'+E(g.i)+'" alt="" width="52" height="52" loading="lazy"><span class="pgp-gt">'+(lead?'<em>Start here</em>':'')+'<b>'+E(g.n)+'</b><i>'+E(g.d)+'</i></span><span class="pgp-open">Open</span></a>'}
function draw(){var l=pick(),h;if(!l.length){out.innerHTML='<p class="pgp-empty">'+out.getAttribute('data-empty')+'</p>';return l}
h='<p class="pgp-h">Your '+l.length+' guide'+(l.length>1?'s':'')+'</p><div class="pgp-grid">';for(var i=0;i<l.length;i++)h+=tile(l[i][0],l[i][1]);
out.innerHTML=h+'</div><p class="pga-foot">'+out.getAttribute('data-foot')+'</p>';return l}
b.addEventListener('click',function(e){var c=e.target.closest&&e.target.closest('.pgp-chip'),a,l;
if(c){var v=c.getAttribute('data-v');if(c.getAttribute('data-q')==='1'){arr=arr===v?'':v;b.querySelectorAll('[data-q="1"]').forEach(function(x){x.setAttribute('aria-pressed',x.getAttribute('data-v')===arr?'true':'false')})}
else{var i=st.indexOf(v);if(i>-1)st.splice(i,1);else st.push(v);c.setAttribute('aria-pressed',i>-1?'false':'true')}
l=draw();try{if(window.gtag)gtag('event','pg_article_pick',{event_category:'engagement',article:art,arrival:arr||'none',stops:O.filter(function(s){return st.indexOf(s)>-1}).join(',').toLowerCase()||'none',guides:l.length})}catch(x){}return}
a=e.target.closest&&e.target.closest('[data-pga-to]');if(!a)return;
try{if(window.gtag)gtag('event','pg_article_tap',{event_category:'engagement',to:a.getAttribute('data-pga-to'),article:art,page_path:location.pathname})}catch(x){}});})();</script>
"""


def die(msg):
    sys.exit("w49 aborted, nothing written: " + msg)


if not os.path.isfile(REG):
    die("run from the repo root (cannot find tools/pocket_guides.json)")
reg = json.load(open(REG, encoding="utf-8"))
guides = [g for g in reg["guides"] if g["country"] == COUNTRY]
by_key = {g["key"]: g for g in guides}
order = (reg.get("stop_order") or {}).get(COUNTRY) or []
if not order:
    die('registry has no "stop_order" for ' + COUNTRY)
for g in guides:
    if g.get("stop") not in order:
        die("guide %s has no valid \"stop\" (got %r; stops are %s)" % (g["key"], g.get("stop"), order))
    if g.get("type") not in ("Airport", "Station"):
        die("guide %s: type must be Airport or Station (got %r)" % (g["key"], g.get("type")))
    if g["type"] == "Airport" and not g.get("chip"):
        die("airport %s has no \"chip\" text in the registry" % g["key"])
    if not os.path.isfile(os.path.join(IMG, g["icon"])):
        die("missing icon public/images/" + g["icon"])
    if not os.path.isfile(os.path.join(PUB, g["key"] + "-pocket.html")):
        die("no pocket page for " + g["key"])
stations = {}   # stop -> every station guide in that city (Tokyo has several: Tokyo Station, Shinjuku, Ueno)
for g in guides:
    if g["type"] == "Station":
        stations.setdefault(g["stop"], []).append(g)


def esc(s):
    return html.escape(s, quote=True)


def tile(g, tag, lead):
    return ('<a class="pgp-g" href="/%s-pocket?src=art_%s" data-pga-to="%s" aria-label="Open the %s pocket guide">'
            '<img src="/images/%s" alt="" width="52" height="52" loading="lazy"><span class="pgp-gt">%s<b>%s</b><i>%s</i></span>'
            '<span class="pgp-open">Open</span></a>'
            % (g["key"], tag, g["key"], esc(g["name"]), g["icon"], "<em>Start here</em>" if lead else "", esc(g["name"]), esc(g["blurb"])))


def block(slug, cfg):
    tag, pre = cfg["tag"], cfg.get("pre", [])
    exclude = set(cfg.get("exclude", []))
    for k in exclude:
        if k not in by_key:
            die("%s: excluded guide %s is not in the registry" % (slug, k))
    for s in pre:
        if s not in order:
            die("%s: pre-picked stop %r is not in stop_order" % (slug, s))
    airports = sorted([g for g in guides if g["type"] == "Airport" and g["key"] not in exclude
                       and (not cfg.get("arrivals") or g["key"] in cfg["arrivals"])], key=lambda g: g.get("chip_rank", 99))
    cities = [s for s in order if any(g["key"] not in exclude for g in stations.get(s, []))]
    pre = [s for s in pre if s in cities]
    pool = [{"k": g["key"], "n": g["name"], "d": g["blurb"], "i": g["icon"], "t": g["type"], "s": g["stop"]}
            for g in guides if g["key"] not in exclude]
    c1 = "".join('<button type="button" class="pgp-chip" data-q="1" data-v="%s" aria-pressed="false">%s</button>' % (g["key"], esc(g["chip"])) for g in airports)
    c2 = "".join('<button type="button" class="pgp-chip" data-q="2" data-v="%s" aria-pressed="%s">%s</button>'
                 % (esc(s), "true" if s in pre else "false", esc(s)) for s in cities)
    q2note = ' <span>Pre-picked</span>' if pre else ' <span>Pick any</span>'
    shown = [g for s in cities if s in pre for g in stations[s] if g["key"] not in exclude]
    if shown:
        res = ('<p class="pgp-h">Your %d guide%s</p><div class="pgp-grid">%s</div><p class="pga-foot">%s</p>'
               % (len(shown), "s" if len(shown) > 1 else "", "".join(tile(g, tag, False) for g in shown), FOOT))
    else:
        res = '<p class="pgp-empty">%s</p>' % EMPTY
    return ('<aside class="pga" id="pocket-guides-japan" %s data-pga-article="%s" data-pre="%s" data-order="%s" data-guides="%s" '
            'role="complementary" aria-label="Offline pocket guides for Japan">'
            '<div class="pga-top"><span class="pga-kick">Pocket guides that work offline</span>'
            '<p class="pga-title">%s</p><p class="pga-sub">%s</p>'
            '<div class="pgp-qs"><div class="pgp-q" role="group" aria-labelledby="pgp-q1"><p class="pgp-ql" id="pgp-q1">1. %s</p><div class="pgp-chips">%s</div></div>'
            '<div class="pgp-q" role="group" aria-labelledby="pgp-q2"><p class="pgp-ql" id="pgp-q2">2. %s%s</p><div class="pgp-chips">%s</div></div></div></div>'
            '<div class="pgp-res" aria-live="polite" data-empty="%s" data-foot="%s">%s</div></aside>\n'
            % (MARK, tag, "|".join(esc(s) for s in pre), "|".join(esc(s) for s in cities),
               esc(json.dumps(pool, separators=(",", ":"), ensure_ascii=False)),
               cfg["title"], SUB, Q1, c1, Q2, q2note, c2, esc(EMPTY), esc(FOOT), res))


css = (CSS.replace("@BG@", BG).replace("@KICK@", KICK).replace("@CHIP_BG@", CHIP_BG).replace("@CHIP_LINE@", CHIP_LINE)
       .replace("@CHIP_ON_BG@", CHIP_ON_BG).replace("@CHIP_ON_FG@", CHIP_ON_FG).replace("@OPEN_BG@", OPEN_BG)
       .replace("@PILL_BG@", PILL_BG).replace("@PILL_FG@", PILL_FG))

plans = []
for slug, cfg in PAGES.items():
    path = os.path.join(BLOG, slug + ".html")
    if not os.path.isfile(path):
        die("missing article " + os.path.relpath(path, ROOT))
    s = open(path, encoding="utf-8").read()
    if MARK in s:
        # wording kept in step on blocks built earlier (26 Nov): no "free", and no "install" next to "no app"
        fixed = s
        for a_, b_ in (('<span class="pga-kick">Free offline pocket guides</span>', '<span class="pga-kick">Pocket guides that work offline</span>'),
                       ('Install and it works even offline.', 'Add it to your Home Screen and it works even offline.')):
            fixed = fixed.replace(a_, b_)
        plans.append((path, fixed if fixed != s else None, slug))
        continue
    a = s.find('<style id="pga-css">')
    e = s.find("</aside>")
    j = s.find("</script>\n", e)
    OLD = next((o for o in OLDS if o in s), None)
    if OLD is None or a < 0 or e < 0 or j < 0 or not a < s.find(OLD) < e < j:
        die("%s: the w48 card (css + aside + script) was not found in one piece; run w48 first" % slug)
    if s.count('<style id="pga-css">') != 1 or s.count(OLD) != 1:
        die("%s: expected exactly one w48 card" % slug)
    end = j + len("</script>\n")
    plans.append((path, s[:a] + css + block(slug, cfg) + JS + s[end:], slug))

for path, new, slug in plans:
    if new is None:
        print("unchanged (already done):", slug)
        continue
    open(path, "w", encoding="utf-8").write(new)
    print("updated:", slug)
