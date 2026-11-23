#!/usr/bin/env python3
"""
w45: cross-links between the offline pocket guides (Haneda, Narita, KIX, Osaka, Kyoto, Tokyo).

Run from the repo root, AFTER the pocket generators and AFTER w44:
    python3 tools/w45_pocket_crosslinks.py

What it changes (idempotent, marker: xguide-v1):
  * Each public/<guide>-pocket.html
      - "Next stop" card: airports (Narita, Haneda, KIX) at the end of the Arrival tab;
        stations (Tokyo, Kyoto, Osaka) in the Leaving tab, "Before you go".
      - "More pocket guides" list in the Help tab, just above "Keep this on your phone".
      - Header line becomes "by PackSmart . Checked <date>" (the date already in the header; it only
        changes when the facts in that guide are rechecked).
      - Taps are counted as pg_xguide_tap (to, via=card|list, where). Links carry ?src=pk_<from guide>.
      - Offline, a tap on one of these links shows a short "no signal" note instead of a browser error page.
      - Cache name bumped by one (page and service worker) so phones pick up the change.
  * public/travel-essentials.html: a small "Offline pocket guides" strip above the section filter.
Aborts without writing anything if an expected anchor is missing.
"""
import os, re, sys

PUB = os.path.join(os.getcwd(), "public")
MARK = "xguide-v1"

# key: (page name, emoji, one-line blurb, kind)
G = {
    "haneda": ("Haneda Airport", "✈️", "Terminals, prayer rooms, nursing rooms, lockers", "air"),
    "narita": ("Narita Airport", "✈️", "Terminals, prayer rooms, baby rooms, lockers", "air"),
    "kix": ("Kansai Airport", "✈️", "Trains and buses to Osaka and Kyoto, lockers, showers", "air"),
    "osaka": ("Shin-Osaka and Umeda", "\U0001F689", "Shin-Osaka and Osaka/Umeda, platforms, lockers", "stn"),
    "kyoto": ("Kyoto Station", "\U0001F689", "Central and Hachijo sides, platforms, buses, lockers", "stn"),
    "tokyo": ("Tokyo Station", "\U0001F689", "Marunouchi and Yaesu sides, Shinkansen platforms, lockers", "stn"),
    "shinjuku": ("Shinjuku Station", "\U0001F689", "West and East sides, Narita Express, airport buses, lockers", "stn"),
    "ueno": ("Ueno Station", "\U0001F689", "Ueno Park gates, Skyliner to Narita, platforms by floor, lockers", "stn"),
}
ORDER = ["haneda", "narita", "kix", "tokyo", "shinjuku", "ueno", "kyoto", "osaka"]
NEXT = {
    "narita": ["tokyo", "shinjuku", "ueno"], "haneda": ["tokyo", "shinjuku"], "kix": ["osaka", "kyoto"],
    "tokyo": ["kyoto", "osaka"], "kyoto": ["osaka", "kix"], "osaka": ["kyoto", "kix"],
    "shinjuku": ["narita", "haneda"],
    "ueno": ["narita", "haneda"],
}
HEAD = {
    "narita": ("Heading into Tokyo?", "Your next pocket guides."),
    "haneda": ("Heading into Tokyo?", "Your next pocket guides."),
    "kix": ("Heading into the city?", "Your next pocket guides."),
    "tokyo": ("Heading on by Shinkansen?", "Your next pocket guides."),
    "kyoto": ("Heading on?", "Your next pocket guides."),
    "osaka": ("Heading on?", "Your next pocket guides."),
    "shinjuku": ("Flying out?", "Your airport pocket guides."),
    "ueno": ("Flying out?", "Your airport pocket guides."),
}
SAVE_LINE = " Open it while you have signal, then add it to your home screen."

CSS = """
.nx{border-color:#BFE9DF;background:#F3FBF9}
.nx h2{margin:0 0 2px}
.nxa{display:flex;align-items:center;gap:12px;text-decoration:none;color:#0f0f23;background:#fff;border:2px solid #D5DCE0;border-radius:14px;padding:10px 12px;margin:8px 0 0;min-height:60px}
.nxa .ni{font-size:1.6rem;line-height:1;flex:none}
.nxa .nt{display:flex;flex-direction:column;min-width:0;line-height:1.2;flex:1}
.nxa .nt b{font-size:1rem}
.nxa .nt span{font-size:.82rem;color:#444;margin-top:2px}
.nxa .go{flex:none;font-weight:800;font-size:.9rem;color:#0b5d57}
.nxl{display:flex;align-items:center;gap:10px;text-decoration:none;color:#0f0f23;padding:9px 0;border-top:1px solid #D5DCE0;font-size:.92rem;min-height:44px}
.nxl.first{border-top:0}
.nxl b{flex:1}
.nxoff{margin:8px 0 0;font-weight:700;color:#3a2400;background:#FFE7BF;border-radius:10px;padding:6px 10px}
.nxoff[hidden]{display:none}
"""

JS = r"""
  /* xguide-v1: links to the other pocket guides. Needs signal, so say so when offline. */
  document.addEventListener('click',function(e){
    var a=e.target&&e.target.closest?e.target.closest('a[data-xg]'):null; if(!a) return;
    if(navigator.onLine===false){
      e.preventDefault();
      var n=document.getElementById('nxOff'); if(!n){ n=document.createElement('p'); n.id='nxOff'; n.className='nxoff'; n.setAttribute('role','status'); }
      n.textContent='No signal right now. Open this guide when you are back online, then save it to your phone.';
      a.parentNode.insertBefore(n,a.nextSibling); n.hidden=false;
    }
  },true);
"""


def die(msg):
    sys.exit("w45 aborted, nothing written: " + msg)


def link(g, frm, cls, via):
    n, ic, bl, _ = G[g]
    if cls == "nxa":
        return ('<a class="nxa" href="/%s-pocket?src=pk_%s" data-xg="%s" data-via="%s"><span class="ni" aria-hidden="true">%s</span>'
                '<span class="nt"><b>%s Pocket Guide</b><span>%s</span></span><span class="go">Open &rsaquo;</span></a>') % (g, frm, g, via, ic, n, bl)
    return ('<a class="%s" href="/%s-pocket?src=pk_%s" data-xg="%s" data-via="%s"><span aria-hidden="true">%s</span><b>%s</b>'
            '<span aria-hidden="true">&rsaquo;</span></a>') % (cls, g, frm, g, via, ic, n)


def bump(text):
    return re.sub(r"(\b[a-z]+-pocket-v)(\d+)", lambda m: m.group(1) + str(int(m.group(2)) + 1), text)


plan = {}
for g in G:
    pp = os.path.join(PUB, g + "-pocket.html")
    sp = os.path.join(PUB, g + "-sw.js")
    for p in (pp, sp):
        if not os.path.isfile(p):
            die("missing " + p)
    s = open(pp, encoding="utf-8").read()
    sw = open(sp, encoding="utf-8").read()
    if MARK in s:
        continue
    if "install-v2" not in s:
        die("%s: run w44 first (install-v2 marker missing)" % g)
    for need in ('id="p-arrive"', 'id="p-depart"', '<div class="card slim install" id="install">', "</style>",
                 "if(/^mailto:/i.test(h)) return;", "var AUTO_INSTALL_SHEET=true;"):
        if s.count(need) != 1:
            die("%s: anchor not found exactly once: %s" % (g, need))
    if not re.search(r'<span class="by">by PackSmart &middot; \d{1,2} [A-Z][a-z]{2} \d{4}', s):
        die("%s: header date line not found" % g)
    if "pocket-v" not in sw or not re.search(r"\b%s-pocket-v\d+" % g, s):
        die("%s: cache name not found" % g)

    # header date -> "Checked <date>"
    s = re.sub(r'(<span class="by">by PackSmart &middot; )(\d{1,2} [A-Z][a-z]{2} \d{4})', r"\1Checked \2", s, count=1)
    # css
    s = s.replace("</style>", CSS + "</style>", 1)
    # next-stop card
    h, sub = HEAD[g]
    card = ('<div class="card nx" id="nextCard"><h2>%s</h2><p class="small">%s%s</p>%s</div>'
            % (h, sub, SAVE_LINE, "".join(link(x, g, "nxa", "card") for x in NEXT[g])))
    if G[g][3] == "air":
        i = s.index('id="p-arrive"')
        j = s.index("</section>", i)
        s = s[:j] + card + "\n" + s[j:]
    else:
        i = s.index('id="p-depart"')
        d = s.find('id="depBefore"', i)
        k = s.find('<p class="hint">', d)
        if d < 0 or k < 0:
            die("%s: Leaving tab hint line not found" % g)
        k = s.index("</p>", k) + 4
        s = s[:k] + "\n" + card + s[k:]
    # help list
    others = [x for x in ORDER if x != g]
    rows = "".join(link(x, g, "nxl first" if n == 0 else "nxl", "list") for n, x in enumerate(others))
    lst = '<div class="card slim" id="allGuides"><h2>More pocket guides</h2>%s</div>\n' % rows
    s = s.replace('<div class="card slim install" id="install">', lst + '<div class="card slim install" id="install">', 1)
    # analytics
    s = s.replace("if(/^mailto:/i.test(h)) return;",
                  "if(/^mailto:/i.test(h)) return;\n    if(a.hasAttribute('data-xg')){ pgTrack('pg_xguide_tap',{to:a.getAttribute('data-xg'),via:a.getAttribute('data-via')||'',where:whereNow()}); return; }", 1)
    # offline note + marker (after the AUTO_INSTALL line so the marker sits with the other one)
    s = s.replace("var AUTO_INSTALL_SHEET=true; /* install-v2 */", "var AUTO_INSTALL_SHEET=true; /* install-v2 */" + JS, 1)
    if MARK not in s:
        die("%s: marker did not land (install-v2 comment not as expected)" % g)
    s = bump(s)
    sw = bump(sw)
    plan[g] = (pp, s, sp, sw)

# ---- hub strip on travel-essentials
HUB = os.path.join(PUB, "travel-essentials.html")
if not os.path.isfile(HUB):
    die("missing " + HUB)
hub = open(HUB, encoding="utf-8").read()
hub_new = None
if 'id="pocket-hub"' not in hub:
    anchor = '<div class="filter-wrap te-filter" id="teFilter">'
    if hub.count(anchor) != 1 or hub.count("</head>") != 1:
        die("travel-essentials.html: anchors not found")
    hub_css = ('<style id="pocket-hub-css">\n'
               '.pocket-hub{margin:0 0 1.6rem;padding:1rem 1.1rem;background:#E7FAF5;border:1px solid #bfeee2;border-radius:16px}\n'
               '.pocket-hub h2{font-size:1.05rem;font-weight:800;margin:0 0 .15rem;color:#0f0f23}\n'
               '.pocket-hub p{margin:0 0 .7rem;font-size:.92rem;color:#3d4659}\n'
               '.pocket-hub .ph-row{display:flex;flex-wrap:wrap;gap:8px}\n'
               '.pocket-hub .ph-row a{display:inline-flex;align-items:center;gap:6px;padding:8px 14px;border-radius:22px;background:#fff;border:1.5px solid #bfeee2;color:#0f0f23;font-weight:700;font-size:.9rem;text-decoration:none;min-height:40px}\n'
               '.pocket-hub .ph-row a:hover{border-color:#0b5d57}\n'
               '</style>\n')
    chips = "".join('<a href="/%s-pocket?src=hub">%s %s</a>' % (x, G[x][1], G[x][0]) for x in ORDER)
    strip = ('<section class="pocket-hub" id="pocket-hub" aria-labelledby="pocketHubT"><h2 id="pocketHubT">Offline pocket guides</h2>'
             '<p>Short, big-print helpers for the airport or station. Open one on your phone and save it to your home screen. It works with no signal.</p>'
             '<div class="ph-row">%s</div></section>\n    ' % chips)
    hub_new = hub.replace("</head>", hub_css + "</head>", 1).replace(anchor, strip + anchor, 1)

changed = []
for g, (pp, s, sp, sw) in plan.items():
    open(pp, "w", encoding="utf-8").write(s)
    open(sp, "w", encoding="utf-8").write(sw)
    changed.append("%s-pocket.html and %s-sw.js (cache bumped)" % (g, g))
if hub_new is not None:
    open(HUB, "w", encoding="utf-8").write(hub_new)
    changed.append("travel-essentials.html (Offline pocket guides strip)")
print("changed:" if changed else "nothing to do (already applied)")
for c in changed:
    print("  - " + c)
