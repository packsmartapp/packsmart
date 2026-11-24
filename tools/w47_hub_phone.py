#!/usr/bin/env python3
"""
w47: "Your pocket guides" block on the Travel Essentials hub, version 3: white card, plain-English explanation of what a
pocket guide is, a 3-step "how to save it", and an iPhone-style home screen showing the guide icons (tappable).
Replaces the w46 block. Reads tools/pocket_guides.json (optional "short" per guide; default is the first word of the name).

Run from the repo root, after w46:  python3 tools/w47_hub_phone.py
Idempotent: rebuilds the block from the registry and writes only if it changed (22 Nov 2026: was marker-only). The section keeps the old pocket-hub-v2 marker too, so re-running w46 will not bring the old block back.
The phone has one "home screen page" per country (switch with the country buttons or the dots), each showing at most PAGE_MAX icons.
A "See all N pocket guides" button (-> ALL_URL, create that page FIRST) appears if any country has more than PAGE_MAX guides or there are more than MAX_COUNTRIES countries.
With one country it looks exactly like the single-country version (a "Japan . 6 guides" label, no buttons).
"""
import json, os, re, sys

ROOT = os.getcwd()
PUB = os.path.join(ROOT, "public")
IMG = os.path.join(PUB, "images")
REG = os.path.join(ROOT, "tools", "pocket_guides.json")
HUB = os.path.join(PUB, "travel-essentials.html")
MARK = "pocket-hub-v3"
PAGE_MAX, MAX_COUNTRIES, ALL_URL = 12, 6, "/pocket-guides"   # 12 (was 8) = three rows of four on the phone, so ten Japan guides fit without the "See all" button (no /pocket-guides page yet)


def die(msg):
    sys.exit("w47 aborted, nothing written: " + msg)


for p in (REG, HUB):
    if not os.path.isfile(p):
        die("run from the repo root (cannot find %s)" % os.path.relpath(p, ROOT))
reg = json.load(open(REG, encoding="utf-8"))
guides = reg["guides"]
for g in guides:
    for k in ("key", "name", "country", "type", "icon"):
        if not g.get(k):
            die("registry entry missing %s: %r" % (k, g))
    if not os.path.isfile(os.path.join(IMG, g["icon"])):
        die("missing icon public/images/" + g["icon"])
    if not os.path.isfile(os.path.join(PUB, g["key"] + "-pocket.html")):
        die("no pocket page for " + g["key"])

CSS = """<style id="pocket-hub-css">
.pocket-hub{margin:0 0 2rem;background:#fff;border:1px solid #E1E8EB;border-radius:28px;padding:2rem 2.2rem;box-shadow:0 12px 32px rgba(15,15,35,.07);display:grid;grid-template-columns:minmax(0,1.2fr) minmax(0,.8fr);grid-template-areas:"intro side" "more side";column-gap:2.2rem;row-gap:0;align-items:start}
.pocket-hub .ph-intro{grid-area:intro}
.pocket-hub .ph-more{grid-area:more}
.pocket-hub .ph-kick{display:inline-block;font-size:.72rem;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:#0b5d57;background:#D9F7EF;border-radius:20px;padding:4px 12px;margin-bottom:.7rem}
.pocket-hub h2{font-family:var(--font-display);font-weight:400;font-size:2.3rem;line-height:1.08;margin:0 0 .6rem;color:#0f0f23}
.pocket-hub h2 em{font-style:italic;color:#0b8f78}
.pocket-hub .ph-lead{margin:0;color:#3d4659;font-size:1.05rem;line-height:1.5;max-width:36rem}
.pocket-hub .ph-list{list-style:none;margin:1.1rem 0 0;padding:0;display:grid;gap:.75rem;max-width:36rem}
.pocket-hub .ph-list li{display:flex;gap:.75rem;align-items:flex-start;line-height:1.38;color:#1b1f33;font-size:.98rem}
.pocket-hub .ph-list li::before{content:"\\2713";flex:none;width:24px;height:24px;border-radius:50%;background:#D9F7EF;color:#0b5d57;font-weight:800;display:flex;align-items:center;justify-content:center;font-size:.82rem;margin-top:1px}
.pocket-hub .ph-list b{font-weight:800;color:#0f0f23}
.pocket-hub .ph-how{margin:1.3rem 0 0;padding:1rem 1.1rem;background:#F4F7F9;border-radius:16px;max-width:36rem}
.pocket-hub .ph-how h3{margin:0 0 .6rem;font-size:.8rem;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:#0b5d57}
.pocket-hub .ph-how ol{list-style:none;margin:0;padding:0;display:grid;gap:.55rem;counter-reset:s}
.pocket-hub .ph-how li{counter-increment:s;display:flex;gap:.7rem;align-items:flex-start;font-size:.93rem;line-height:1.35;color:#1b1f33}
.pocket-hub .ph-how li::before{content:counter(s);flex:none;width:22px;height:22px;border-radius:50%;background:#0f0f23;color:#fff;font-weight:800;font-size:.78rem;display:flex;align-items:center;justify-content:center;margin-top:1px}
.pocket-hub .ph-side{grid-area:side;justify-self:center;align-self:center;text-align:center}
.pocket-hub .ph-count{display:inline-block;font-size:.8rem;font-weight:800;color:#0f0f23;background:#F4F7F9;border-radius:20px;padding:5px 13px;margin-bottom:.9rem}
.pocket-hub .ph-phone{position:relative;width:272px;margin:0 auto;border-radius:48px;padding:10px;background:#0b0b12;box-shadow:0 0 0 2px #2c2c3a,0 26px 50px rgba(15,15,35,.28)}
.pocket-hub .ph-screen{position:relative;border-radius:39px;overflow:hidden;aspect-ratio:9/16;background:linear-gradient(165deg,#2f6fe0 0%,#6a4fd0 48%,#f0709a 100%);padding:14px 16px 16px;display:flex;flex-direction:column;text-align:left}
.pocket-hub .ph-island{position:absolute;top:10px;left:50%;transform:translateX(-50%);width:84px;height:24px;border-radius:14px;background:#000}
.pocket-hub .ph-status{display:flex;justify-content:space-between;align-items:center;color:#fff;font-weight:700;font-size:.78rem;padding:3px 8px 0}
.pocket-hub .ph-batt{display:inline-block;width:22px;height:11px;border:1.5px solid #fff;border-radius:4px;position:relative}
.pocket-hub .ph-batt::after{content:"";position:absolute;left:1.5px;top:1.5px;bottom:1.5px;width:70%;background:#fff;border-radius:2px}
.pocket-hub .ph-widget{margin-top:2.3rem;background:rgba(255,255,255,.22);border:1px solid rgba(255,255,255,.35);border-radius:20px;padding:11px 14px;color:#fff;text-shadow:0 1px 3px rgba(0,0,0,.35)}
.pocket-hub .ph-widget b{display:block;font-size:.92rem}
.pocket-hub .ph-widget span{display:block;font-size:.7rem;line-height:1.3;margin-top:2px;opacity:.95}
.pocket-hub .ph-icons{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px 8px;margin-top:1.1rem}
.pocket-hub .ph-icon{display:flex;flex-direction:column;align-items:center;gap:5px;text-decoration:none;color:#fff;font-size:.62rem;font-weight:600;text-shadow:0 1px 3px rgba(0,0,0,.45);line-height:1.1;text-align:center}
.pocket-hub .ph-icon img{width:100%;max-width:50px;aspect-ratio:1;border-radius:23%;display:block;box-shadow:0 4px 10px rgba(0,0,0,.35);transition:transform .15s}
.pocket-hub .ph-icon:hover img{transform:scale(1.08)}
.pocket-hub .ph-dots{margin-top:auto;display:flex;justify-content:center;gap:6px}
.pocket-hub .ph-dots i{width:6px;height:6px;border-radius:50%;background:rgba(255,255,255,.5);cursor:pointer}
.pocket-hub .ph-dots i.on{background:#fff}
.pocket-hub .ph-tabs{display:flex;flex-wrap:wrap;gap:6px;justify-content:center;margin:0 auto .9rem;max-width:300px}
.pocket-hub .ph-tabs button{font:inherit;font-size:.8rem;font-weight:800;border:1.5px solid #D5DCE0;background:#fff;color:#0f0f23;border-radius:20px;padding:5px 12px;cursor:pointer}
.pocket-hub .ph-tabs button[aria-pressed=true]{background:#0f0f23;color:#fff;border-color:#0f0f23}
.pocket-hub .ph-tabs i{font-style:normal;opacity:.6;margin-left:4px;font-weight:600}
.pocket-hub .ph-dense .ph-widget{margin-top:1.7rem;padding:8px 12px}
.pocket-hub .ph-dense .ph-icons{gap:10px 8px;margin-top:.8rem}
.pocket-hub .ph-home{width:92px;height:4px;border-radius:2px;background:#fff;opacity:.85;margin:12px auto 0}
.pocket-hub .ph-cap{margin:.9rem 0 0;font-size:.84rem;color:#5a6378}
.pocket-hub .ph-all{display:inline-block;margin-top:.7rem;font-weight:800;color:#0f0f23;background:#fff;border:2px solid #0f0f23;border-radius:24px;padding:8px 18px;text-decoration:none}
@media (max-width:900px){.pocket-hub{grid-template-columns:1fr;grid-template-areas:"intro" "side" "more";padding:1.6rem 1.4rem;row-gap:1.4rem}.pocket-hub h2{font-size:2rem}}
@media (max-width:480px){.pocket-hub{padding:1.3rem 1rem;border-radius:22px}.pocket-hub h2{font-size:1.75rem}.pocket-hub .ph-phone{width:250px}}
</style>
"""


def short(g):
    return g.get("short") or g["name"].split(" ")[0]


def countries():
    order = reg.get("country_order") or []
    cs = [c for c in order if any(g["country"] == c for g in guides)]
    cs += [c for c in dict.fromkeys(g["country"] for g in guides) if c not in cs]
    return cs


def icons_html(items):
    return "".join('<a class="ph-icon" href="/%s-pocket?src=hub"><img src="/images/%s" alt="" width="50" height="50" loading="lazy"><span>%s</span></a>'
                   % (g["key"], g["icon"], short(g)) for g in items[:PAGE_MAX])


JS = ("<script>(function(){var h=document.getElementById('pocket-hub');if(!h)return;"
      "var t=h.querySelectorAll('[data-ph-tab]'),p=h.querySelectorAll('[data-ph-page]'),d=h.querySelectorAll('[data-ph-dot]');if(t.length<2)return;"
      "function go(i){for(var k=0;k<p.length;k++){p[k].hidden=(k!==i);}for(k=0;k<t.length;k++){t[k].setAttribute('aria-pressed',k===i?'true':'false');}"
      "for(k=0;k<d.length;k++){d[k].className=(k===i?'on':'');}}"
      "for(var k=0;k<t.length;k++){(function(i){t[i].addEventListener('click',function(){go(i);});d[i]&&d[i].addEventListener('click',function(){go(i);});})(k);}})();</script>")


def build_section():
    cs = countries()
    multi = len(cs) > 1
    pages = []
    for n, c in enumerate(cs):
        mine = [g for g in guides if g["country"] == c]
        pages.append('<div class="ph-page" data-ph-page="%d"%s><div class="ph-icons">%s</div></div>' % (n, "" if n == 0 else " hidden", icons_html(mine)))
    dense = any(sum(1 for g in guides if g["country"] == c) > 8 for c in cs)   # three rows of icons: tighter widget and gaps so they fit the screen
    if multi:
        top = '<div class="ph-tabs" role="group" aria-label="Pocket guides by country">' + "".join(
            '<button type="button" data-ph-tab="%d" aria-pressed="%s">%s<i>%d</i></button>'
            % (n, "true" if n == 0 else "false", c, sum(1 for g in guides if g["country"] == c)) for n, c in enumerate(cs)) + "</div>"
        dots = "".join('<i data-ph-dot="%d"%s></i>' % (n, ' class="on"' if n == 0 else "") for n in range(len(cs)))
    else:
        n = len(guides)
        top = '<span class="ph-count">%s &middot; %d guide%s</span>' % (cs[0], n, "" if n == 1 else "s")
        dots = '<i class="on"></i><i></i>'
    capped = any(sum(1 for g in guides if g["country"] == c) > PAGE_MAX for c in cs) or len(cs) > MAX_COUNTRIES
    more = ('<div><a class="ph-all" href="%s">See all %d pocket guides &rsaquo;</a></div>' % (ALL_URL, len(guides))) if capped else ""
    return (
        '<section class="pocket-hub" id="pocket-hub" aria-labelledby="pocketHubT"><!-- pocket-hub-v2 ' + MARK + ' -->'
        '<div class="ph-intro"><span class="ph-kick">Offline pocket guides</span>'
        '<h2 id="pocketHubT">Your <em>pocket guides</em></h2>'
        '<p class="ph-lead">A pocket guide is a short, big-print helper for one airport or station. Open it on your phone, save it to your home screen, '
        'and it works like an app, even with no signal.</p></div>'
        '<div class="ph-more"><ul class="ph-list">'
        '<li><span><b>Finds what you need fast.</b> Toilets, lockers, food, exits and trains, a couple of taps away.</span></li>'
        '<li><span><b>Big print, plain English.</b> With a screen you can show station or airport staff in Japanese.</span></li>'
        '<li><span><b>Works with no signal</b> once it is saved, so it still helps in a basement or on a train platform.</span></li>'
        '<li><span><b>Checked against official sources.</b> The date it was last checked is at the top of every guide.</span></li>'
        '</ul>'
        '<div class="ph-how"><h3>Save it in three taps</h3><ol>'
        '<li><span>Open a guide on your phone.</span></li>'
        '<li><span>Android: tap <b>Install</b>. iPhone: tap Share, then <b>Add to Home Screen</b>.</span></li>'
        '<li><span>Open it from your home screen whenever you need it.</span></li>'
        '</ol></div></div>'
        '<div class="ph-side">' + top +
        '<div class="ph-phone" role="group" aria-label="A phone home screen with the pocket guide icons"><div class="ph-screen' + (' ph-dense' if dense else '') + '"><span class="ph-island" aria-hidden="true"></span>'
        '<div class="ph-status" aria-hidden="true"><span>9:41</span><span class="ph-batt"></span></div>'
        '<div class="ph-widget" aria-hidden="true"><b>Works offline</b><span>Saved on your phone, no signal needed</span></div>'
        + "".join(pages) +
        '<div class="ph-dots" aria-hidden="true">' + dots + '</div><div class="ph-home" aria-hidden="true"></div></div></div>'
        '<p class="ph-cap">Tap an icon to open a guide. Free, no app store, no account.</p>' + more + '</div>' + (JS if multi else "") + '</section>')


hub = open(HUB, encoding="utf-8").read()
# v3 already applied: rebuild from the registry anyway (a new guide must appear); write only if something changed
if 'id="pocket-hub"' not in hub or 'id="pocket-hub-css"' not in hub:
    die("hub block not found; run w45 and w46 first")
h2, n1 = re.subn(r'<style id="pocket-hub-css">.*?</style>\n', lambda m: CSS, hub, count=1, flags=re.S)
h2, n2 = re.subn(r'<section class="pocket-hub" id="pocket-hub".*?</section>', lambda m: build_section(), h2, count=1, flags=re.S)
if n1 != 1 or n2 != 1:
    die("could not replace the hub block cleanly")
if h2 == hub:
    print("nothing to do (already up to date)")
    sys.exit(0)
open(HUB, "w", encoding="utf-8").write(h2)
print("changed:\n  - public/travel-essentials.html (pocket guides block v3, rebuilt from the registry)")
