#!/usr/bin/env python3
"""
w61: backlog B28 pilot (23 Nov 2026): contextual offers instead of the generic grid, on the Italy, Spain and
Portugal guides. Germany and France already had this layout (no grid, a GetYourGuide city box) since the
November pilot, so they serve as the comparison pages.

On each pilot page:
  1. Removes the generic "Travel Essentials for Your <Country> Trip" grid (SafetyWing, GetYourGuide, Radical
     Storage cards). Each of those partners already has its own block in the right section of the page.
  2. Adds a GetYourGuide "Tours and tickets" box at the end of the city section, with one button per city
     covered by the page. The widget shows GetYourGuide's own top results for a search on that city
     (data-gyg-q), so no tour IDs are hand-picked. cmp = "ps-<page>-gyg-<city>" so clicks can be split by city.
     Placement id: gyg-<country>-cities. The box hides itself if the widget does not load.

Run from the repo root:  python3 tools/w61_b28_city_tours_pilot.py
Idempotent (marker: the placement id). Aborts without writing anything if an anchor is missing.
"""
import os, re, sys

ROOT = os.getcwd()
BLOG = os.path.join(ROOT, "public", "blog")
PARTNER = "D7IXONS"

PAGES = {
    "italy": ("Italy", [("Rome", "Rome"), ("Florence", "Florence"), ("Venice", "Venice"), ("Milan", "Milan"), ("Amalfi Coast", "Amalfi Coast")]),
    "spain": ("Spain", [("Barcelona", "Barcelona"), ("Madrid", "Madrid"), ("Seville", "Seville"), ("San Sebastián", "San Sebastian"), ("Mallorca", "Mallorca")]),
    "portugal": ("Portugal", [("Lisbon", "Lisbon"), ("Porto", "Porto"), ("Sintra", "Sintra"), ("Algarve", "Algarve"), ("Madeira", "Madeira")]),
}


def die(msg):
    sys.exit("w61 aborted, nothing written: " + msg)


def box(key, country, cities, slug):
    pid = "gyg-%s-cities" % key
    data = ",".join("['%s','%s','%s']" % (label.replace("'", "\\'"), q.replace("'", "\\'"),
                                          "ps-%s-gyg-%s" % (slug, re.sub(r"[^a-z0-9]+", "-", q.lower()).strip("-")))
                    for label, q in cities)
    return ('<div class="ps-gyg" data-ps-placement="%s">\n'
            '<style>\n'
            '.ps-gyg{margin:28px 0;font-family:"DM Sans",sans-serif}\n'
            '.ps-gyg-h{display:block;text-align:center;font-size:1.05rem;font-weight:700;color:#0f0f23;margin:0 0 4px}\n'
            '.ps-gyg-s{text-align:center;font-size:.85rem;color:#3f7f70;margin:0 0 14px}\n'
            '.ps-gyg-pills{display:flex;flex-wrap:wrap;justify-content:center;gap:8px;margin:0 0 16px}\n'
            '.ps-gyg-pills button{font:inherit;font-size:.85rem;font-weight:600;color:#0f0f23;background:#fff;border:1px solid #cdeee5;border-radius:999px;padding:7px 15px;cursor:pointer}\n'
            '.ps-gyg-pills button[aria-pressed="true"]{background:#e8faf6;border-color:#00c9a7}\n'
            '.ps-gyg-w{min-height:495px;margin-bottom:-30px}\n'
            '@media(max-width:600px){.ps-gyg-pills{flex-wrap:nowrap;justify-content:flex-start;overflow-x:auto;padding:2px 2px 6px;scrollbar-width:none;-webkit-overflow-scrolling:touch}.ps-gyg-pills::-webkit-scrollbar{display:none}.ps-gyg-pills button{flex:0 0 auto}.ps-gyg-w{min-height:772px;margin-bottom:0}}\n'
            '</style>\n'
            '<strong class="ps-gyg-h">Tours and tickets in %s</strong>\n'
            '<p class="ps-gyg-s ps-gyg-blurb">Pick a city to see popular tours, as listed by our partner.</p>\n'
            '<div class="ps-gyg-pills" role="group" aria-label="Choose a city in %s"></div>\n'
            '<div class="ps-gyg-w"><div class="ps-gyg-slot" data-gyg-href="https://widget.getyourguide.com/default/activities.frame" data-gyg-locale-code="en-US" data-gyg-number-of-items="3" data-gyg-partner-id="%s"></div></div>\n'
            '<script>\n'
            '(function(){\n'
            'var root=document.currentScript.parentNode;\n'
            'var cities=[%s];\n'
            'var pills=root.querySelector(".ps-gyg-pills"),slot=root.querySelector(".ps-gyg-slot");\n'
            'var phone=window.matchMedia("(max-width:600px)"),cur=0,started=false;\n'
            'cities.forEach(function(c,i){var b=document.createElement("button");b.type="button";b.textContent=c[0];'
            'b.setAttribute("aria-pressed",i===0?"true":"false");b.addEventListener("click",function(){pick(i)});pills.appendChild(b);});\n'
            'function render(){var c=cities[cur];slot.setAttribute("data-gyg-widget","activities");'
            'slot.setAttribute("data-gyg-number-of-items",phone.matches?"2":"3");slot.setAttribute("data-gyg-q",c[1]);'
            'slot.setAttribute("data-gyg-cmp",c[2]);var t=0;(function go(){if(window.GYG&&window.GYG.refresh){window.GYG.refresh()}else if(t++<50){setTimeout(go,200)}})();}\n'
            'function pick(i){cur=i;[].forEach.call(pills.children,function(b,j){b.setAttribute("aria-pressed",j===i?"true":"false")});'
            'try{window.gtag&&gtag("event","gyg_city",{event_category:"affiliate",placement:"%s",city:cities[i][0]})}catch(e){}render();}\n'
            'function start(){if(started)return;started=true;render();var n=0;(function watch(){if(slot.querySelector("iframe"))return;'
            'if(++n>15){root.style.display="none";return}setTimeout(watch,1000)})()}\n'
            'if("IntersectionObserver" in window){var io=new IntersectionObserver(function(e){if(e[0].isIntersecting){io.disconnect();start()}},{rootMargin:"400px 0px"});io.observe(root)}else{start()}\n'
            'if(phone.addEventListener){phone.addEventListener("change",function(){if(started)render()})}\n'
            '})();\n'
            '</script>\n'
            '</div>\n') % (pid, country, country, PARTNER, data, pid)


GRID_START = re.compile(r'<div style="background:linear-gradient\(135deg,#F0FAF7,#E8FFF9\);[^"]*">\s*<h3[^>]*>(?:🛒 )?Travel Essentials for Your [^<]+</h3>')
GRID_END = "<!-- closes Travel Essentials outer container -->"

plans, done = {}, []
for key, (country, cities) in PAGES.items():
    slug = "%s-travel-packing-guide" % key
    path = os.path.join(BLOG, slug + ".html")
    if not os.path.isfile(path):
        die("missing " + path)
    s = open(path, encoding="utf-8").read()
    pid = "gyg-%s-cities" % key
    if pid in s and "Travel Essentials for Your" not in s:
        done.append(slug)
        continue
    # 1. remove the grid
    m = GRID_START.search(s)
    if not m:
        die(slug + ": grid start not found")
    depth, e = 0, None
    for t in re.finditer(r"<(/?)div\b[^>]*>", s[m.start():]):
        depth += -1 if t.group(1) else 1
        if depth == 0:
            e = m.start() + t.end()
            break
    if e is None:
        die(slug + ": grid end not found")
    grid = s[m.start():e]
    links = re.findall(r'href="([^"]+)"', grid)
    if len(links) != 3 or not all(any(k in l for k in ("safetywing.com", "getyourguide.com", "radicalstorage")) for l in links):
        die(slug + ": grid does not hold exactly the SafetyWing, GetYourGuide and Radical Storage cards: %r" % links)
    if s[e:].lstrip().startswith(GRID_END):
        e = s.index(GRID_END, e) + len(GRID_END)
    s = s[:m.start()] + s[e:]
    # 2. add the city box at the end of the city section (just before the next h2, which is Cultural Etiquette)
    anchor = re.search(r'<h2[^>]*>\s*Cultural Etiquette &(?:amp;)? Dress Codes\s*</h2>', s)
    if not anchor:
        die(slug + ": Cultural Etiquette heading not found")
    s = s[:anchor.start()] + box(key, country, cities, slug) + "\n" + s[anchor.start():]
    plans[path] = s

for path, s in plans.items():
    open(path, "w", encoding="utf-8").write(s)
print("w61 done. changed: %s | already applied: %s" % (
    ", ".join(os.path.basename(p)[:-5] for p in plans) or "none", ", ".join(done) or "none"))
