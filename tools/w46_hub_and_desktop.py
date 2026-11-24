#!/usr/bin/env python3
"""
w46: (1) livelier "Offline pocket guides" block on the Travel Essentials hub, built from tools/pocket_guides.json;
     (2) the "Keep this on your phone" card shows ONE line on a computer (it used to show two near-identical lines).

Run from the repo root, after w45:  python3 tools/w46_hub_and_desktop.py
Idempotent. Markers: pocket-hub-v2 (hub) and id="instP" (desktop card).
Touches public/travel-essentials.html and the six public/<guide>-pocket.html + <guide>-sw.js (cache bumped once).

Hub layout rules (so it keeps working as guides are added):
  * one labelled row per country; country chips appear once there is more than one country;
  * if there are more than MAX_ON_HUB guides, each country shows at most PER_COUNTRY and a
    "See all N pocket guides" button links to ALL_URL (create that page before it is needed).
"""
import json, os, re, sys

ROOT = os.getcwd()
PUB = os.path.join(ROOT, "public")
IMG = os.path.join(PUB, "images")
REG = os.path.join(ROOT, "tools", "pocket_guides.json")
HUB = os.path.join(PUB, "travel-essentials.html")
MARK = "pocket-hub-v2"
MAX_ON_HUB, PER_COUNTRY, ALL_URL = 12, 6, "/pocket-guides"
GUIDES_WITH_PAGE = ["haneda", "narita", "kix", "osaka", "kyoto", "tokyo", "shinjuku", "ueno", "new-chitose", "sapporo"]  # guides that have their own pocket page today


def die(msg):
    sys.exit("w46 aborted, nothing written: " + msg)


for p in (REG, HUB):
    if not os.path.isfile(p):
        die("run from the repo root (cannot find %s)" % os.path.relpath(p, ROOT))
reg = json.load(open(REG, encoding="utf-8"))
guides = reg["guides"]
for g in guides:
    for k in ("key", "name", "country", "type", "icon", "blurb"):
        if not g.get(k):
            die("registry entry missing %s: %r" % (k, g))
    if not os.path.isfile(os.path.join(IMG, g["icon"])):
        die("missing icon public/images/" + g["icon"])
    if not os.path.isfile(os.path.join(PUB, g["key"] + "-pocket.html")):
        die("no pocket page for " + g["key"])

CSS = """<style id="pocket-hub-css">
.pocket-hub{margin:0 0 2rem;padding:1.5rem 1.6rem 1.4rem;border-radius:24px;background:linear-gradient(180deg,#E7FAF5 0%,#F4FCFA 100%);border:1px solid #bfeee2}
.pocket-hub .ph-head{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:flex-end;gap:.6rem 1rem;margin-bottom:1rem}
.pocket-hub h2{font-family:var(--font-display);font-weight:400;font-size:2rem;line-height:1.1;margin:0;color:#0f0f23}
.pocket-hub h2 em{font-style:italic;color:#0b8f78}
.pocket-hub .ph-head p{margin:.3rem 0 0;color:#3d4659;max-width:34rem}
.pocket-hub .ph-pill{font-size:.8rem;font-weight:800;background:#0f0f23;color:#fff;border-radius:20px;padding:6px 14px;white-space:nowrap}
.pocket-hub .ph-chips{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 .4rem}
.pocket-hub .ph-chips a{font-size:.88rem;font-weight:700;padding:7px 14px;border-radius:22px;border:1.5px solid #bfeee2;background:#fff;color:#0f0f23;text-decoration:none}
.pocket-hub .ph-chips i{font-style:normal;opacity:.6;margin-left:4px;font-weight:600}
.pocket-hub .ph-cty{font-size:.8rem;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:#0b5d57;margin:1rem 0 .7rem;display:flex;align-items:center;gap:10px}
.pocket-hub .ph-cty::after{content:"";flex:1;height:1px;background:#bfeee2}
.pocket-hub .ph-shelf{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:14px}
.pocket-hub .ph-app{display:flex;flex-direction:column;align-items:center;text-align:center;text-decoration:none;color:#0f0f23;line-height:1.2;padding:6px 2px;border-radius:16px;transition:transform .15s}
.pocket-hub .ph-app:hover{transform:translateY(-3px)}
.pocket-hub .ph-app img{width:84px;height:84px;border-radius:21px;display:block;box-shadow:0 8px 18px rgba(15,15,35,.22);margin-bottom:.6rem}
.pocket-hub .ph-app b{font-size:.95rem}
.pocket-hub .ph-app small{font-size:.74rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:#0b5d57;margin-top:2px}
.pocket-hub .ph-all{display:flex;justify-content:center;margin-top:1.2rem}
.pocket-hub .ph-all a{font-weight:800;color:#0f0f23;background:#fff;border:2px solid #0f0f23;border-radius:24px;padding:9px 20px;text-decoration:none}
.pocket-hub .ph-foot{margin:1.2rem 0 0;font-size:.88rem;color:#3d4659;text-align:center}
@media (max-width:900px){.pocket-hub .ph-shelf{grid-template-columns:repeat(3,minmax(0,1fr));row-gap:18px}}
@media (max-width:480px){.pocket-hub{padding:1.2rem 1rem}.pocket-hub h2{font-size:1.7rem}.pocket-hub .ph-app img{width:72px;height:72px;border-radius:18px}}
</style>
"""


def build_section():
    order = reg.get("country_order") or []
    countries = [c for c in order if any(g["country"] == c for g in guides)]
    countries += [c for c in dict.fromkeys(g["country"] for g in guides) if c not in countries]
    crowded = len(guides) > MAX_ON_HUB
    out = ['<section class="pocket-hub" id="pocket-hub" aria-labelledby="pocketHubT"><!-- %s -->' % MARK,
           '<div class="ph-head"><div><h2 id="pocketHubT">Your <em>pocket guides</em></h2>'
           '<p>Big-print helpers for the airport or station. Open one on your phone and save it to your home screen.</p></div>'
           '<span class="ph-pill">Free &middot; Works offline</span></div>']
    if len(countries) > 1:
        out.append('<nav class="ph-chips" aria-label="Pocket guides by country">' +
                   "".join('<a href="#ph-%s">%s <i>%d</i></a>' % (re.sub(r"\W+", "-", c.lower()), c, sum(1 for g in guides if g["country"] == c))
                           for c in countries) + "</nav>")
    for c in countries:
        mine = [g for g in guides if g["country"] == c]
        shown = mine[:PER_COUNTRY] if crowded else mine
        out.append('<div class="ph-cty" id="ph-%s">%s</div><div class="ph-shelf">' % (re.sub(r"\W+", "-", c.lower()), c))
        for g in shown:
            out.append('<a class="ph-app" href="/%s-pocket?src=hub"><img src="/images/%s" alt="" width="84" height="84" loading="lazy">'
                       '<b>%s</b><small>%s</small></a>' % (g["key"], g["icon"], g["name"], g["type"]))
        out.append("</div>")
    if crowded:
        out.append('<div class="ph-all"><a href="%s">See all %d pocket guides &rsaquo;</a></div>' % (ALL_URL, len(guides)))
    out.append('<p class="ph-foot">No app store and no account. Add it to your home screen once, then it works with no signal.</p></section>')
    return "".join(out)


def bump(text):
    return re.sub(r"(\b[a-z]+-pocket-v)(\d+)", lambda m: m.group(1) + str(int(m.group(2)) + 1), text)


writes = {}  # path -> new text

# ---- 1. hub
hub = open(HUB, encoding="utf-8").read()
if MARK not in hub:
    if 'id="pocket-hub"' not in hub or 'id="pocket-hub-css"' not in hub:
        die("w45 hub strip not found; run w45 first")
    h2, n1 = re.subn(r'<style id="pocket-hub-css">.*?</style>\n', lambda m: CSS, hub, count=1, flags=re.S)
    h2, n2 = re.subn(r'<section class="pocket-hub" id="pocket-hub".*?</section>', lambda m: build_section(), h2, count=1, flags=re.S)
    if n1 != 1 or n2 != 1:
        die("could not replace the hub strip cleanly")
    writes[HUB] = h2

# ---- 2. desktop card (one line on a computer)
OLD_P = '<p>Add it to your home screen. Works offline.</p><p class="small" id="instDesk">Open this page on your phone, then add it to your home screen.</p>'
NEW_P = '<p id="instP">Add it to your home screen. Works offline.</p><p id="instDesk">Open this page on your phone to save it for offline use.</p>'
OLD_J = "$('instDesk').hidden=mobile;"
NEW_J = "$('instDesk').hidden=mobile; $('instP').hidden=!mobile;"
for g in GUIDES_WITH_PAGE:
    pp = os.path.join(PUB, g + "-pocket.html")
    sp = os.path.join(PUB, g + "-sw.js")
    s = open(pp, encoding="utf-8").read()
    if 'id="instP"' in s:
        continue
    if s.count(OLD_P) != 1 or s.count(OLD_J) != 1:
        die("%s: install card anchors not found exactly once" % g)
    sw = open(sp, encoding="utf-8").read()
    s = s.replace(OLD_P, NEW_P, 1).replace(OLD_J, NEW_J, 1)
    writes[pp] = bump(s)
    writes[sp] = bump(sw)

if not writes:
    print("nothing to do (already applied)")
    sys.exit(0)
for p, t in writes.items():
    open(p, "w", encoding="utf-8").write(t)
print("changed:")
for p in writes:
    print("  - " + os.path.relpath(p, ROOT))
