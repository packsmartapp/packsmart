#!/usr/bin/env python3
"""
w76: the focused top menu on every page (25 Nov 2026, B57).

GA4 (90 days, bots and the owner's own visits set aside) showed real readers on Germany, Japan and France guides and
on the general packing lists (which live on Travel Essentials, #packing), with few clicks on Flights & Hotels. So the
menu changes from "Destinations · Travel Essentials · Flights & Hotels · Plan My Trip" to:

    🇯🇵 Japan · Destinations ▾ (Germany, France, All destinations) · Packing Lists · Travel Essentials · [Plan My Trip]

Flights & Hotels leaves the menu but keeps its page (the footer still links it). "Destinations" stays a real link to
/blog, styled by each page's own menu CSS; its small dropdown opens on hover or keyboard focus on wide screens and is
listed under it in the phone menu. The CSS is one shared block (<style id="ps-menu-css">) added to each page.

Run after w75 and before w72 (and after any page generator, which copies an old menu):  python3 tools/w76_focused_menu.py
Idempotent: the menu sits between <!-- ps-menu --> markers and is replaced as a whole; an unmarked menu must match one
of the known old menus exactly, or the script stops without writing (so a changed page fails loudly).
"""
import glob, os, re, sys

ROOT = os.getcwd()
PUB = os.path.join(ROOT, "public")
FEATURED = [("🇩🇪", "Germany", "/blog/germany-travel-packing-guide"), ("🇫🇷", "France", "/blog/france-travel-packing-guide")]

MENU = ('<!-- ps-menu -->\n'
        '        <a href="/japan" class="nav-jp"><span aria-hidden="true">🇯🇵</span> Japan</a>\n'
        '        <div class="nav-dd"><a href="/blog" class="nav-dd-top">Destinations <span class="nav-dd-c" aria-hidden="true">▾</span></a>'
        '<div class="nav-dd-menu" aria-label="Featured destinations">'
        + "".join('<a href="%s"><span aria-hidden="true">%s</span> %s</a>' % (u, f, n) for f, n, u in FEATURED)
        + '<a href="/blog" class="nav-dd-all">All destinations &rarr;</a></div></div>\n'
        '        <a href="/travel-essentials#packing">Packing Lists</a>\n'
        '        <a href="/travel-essentials">Travel Essentials</a>\n'
        '        <a href="/#plan" class="nav-cta-btn">Plan My Trip</a>\n'
        '        <!-- /ps-menu -->')

CSS = """<style id="ps-menu-css">
.nav-dd{position:relative;display:inline-flex;align-items:center}
.nav-dd-c{font-size:.7em;margin-left:2px;display:inline-block;transition:transform .15s}
.nav-dd:hover .nav-dd-c,.nav-dd:focus-within .nav-dd-c{transform:rotate(180deg)}
.nav-dd-menu{display:none;position:absolute;top:100%;left:50%;transform:translateX(-50%);padding-top:14px;z-index:1000}
.nav-dd-menu:before{content:"";position:absolute;inset:14px 0 0;background:#fff;border:1px solid #BFEDE3;border-radius:14px;box-shadow:0 14px 34px rgba(15,15,35,.14);z-index:-1}
.nav-dd:hover .nav-dd-menu,.nav-dd:focus-within .nav-dd-menu{display:flex;flex-direction:column;min-width:200px;padding:22px 10px 10px}
.nav-links .nav-dd-menu a{color:#0f0f23!important;font-weight:600;padding:8px 10px;border-radius:10px;white-space:nowrap}
.nav-links .nav-dd-menu a:hover{background:#E6FAF5;color:#0a8f78!important}
.nav-links .nav-dd-menu a::after{display:none}
.nav-links .nav-dd-menu a.nav-dd-all{color:#0a8f78!important;font-weight:800;border-top:1px solid #E6EEF0;border-radius:0 0 10px 10px;margin-top:4px}
/* the open phone menu is a white panel: dark links even before the page scrolls (white-on-white bug before 25 Nov) */
.nav-links.open a:not(.nav-cta-btn){color:#333!important}
.nav-links.open .nav-dd-menu a.nav-dd-all{color:#0a8f78!important}
.nav-links.open .nav-dd{flex-direction:column;align-items:center}
.nav-links.open .nav-dd-c{display:none}
.nav-links.open .nav-dd-menu{display:flex;flex-direction:column;align-items:center;position:static;transform:none;padding:6px 0 0;min-width:0;gap:2px}
.nav-links.open .nav-dd-menu:before{display:none}
.nav-links.open .nav-dd-menu a{padding:6px 0;font-weight:500}
.nav-links.open .nav-dd-menu a.nav-dd-all{border:0;margin:0}
</style>
"""

OLD = [  # the menus in use before 25 Nov 2026 (whitespace-normalised)
    '<a href="/blog">Destinations</a> <a href="/travel-essentials">Travel Essentials</a> <a href="/flights">Flights & Hotels</a> <a href="/#plan" class="nav-cta-btn">Plan My Trip</a>',
    '<a href="/blog">Destinations</a> <a href="/travel-essentials">Travel Essentials</a> <a href="/flights">Flights &amp; Hotels</a> <a href="/#plan" class="nav-cta-btn">Plan My Trip</a>',
    '<a href="blog.html">Destinations</a> <a href="travel-essentials.html">Travel Essentials</a> <a href="flights.html">Flights & Hotels</a> <a href="#plan" class="nav-cta-btn">Plan My Trip</a>',
]
OPEN = re.compile(r'(<div class="nav-links" id="navLinks">)(\s*)')
MARKED = re.compile(r'<!-- ps-menu -->.*?<!-- /ps-menu -->', re.S)

plans, problems = {}, []
for path in sorted(glob.glob(os.path.join(PUB, "**", "*.html"), recursive=True)):
    s = open(path, encoding="utf-8").read()
    if 'id="navLinks"' not in s:
        continue
    rel = os.path.relpath(path, PUB)
    if "<!-- ps-menu -->" in s:
        new = MARKED.sub(lambda m: MENU, s, count=1)
    else:
        m = OPEN.search(s)
        end = s.find("</div>", m.end()) if m else -1
        if not m or end < 0 or re.sub(r"\s+", " ", s[m.end():end]).strip() not in OLD:
            problems.append(rel)
            continue
        new = s[:m.end()] + MENU + "\n    " + s[end:]
    if 'id="ps-menu-css"' in new:
        new = re.sub(r'<style id="ps-menu-css">.*?</style>\n', CSS, new, count=1, flags=re.S)
    else:
        heads = list(re.finditer(r"(?m)^[ \t]*</head>", new))   # the real one sits on its own line (index.html has one in a script)
        if len(heads) != 1:
            problems.append(rel + " (</head>)")
            continue
        new = new[:heads[0].start()] + CSS + new[heads[0].start():]
    if new != s:
        plans[path] = new
if problems:
    sys.exit("w76 aborted, nothing written. Menu not recognised in: " + ", ".join(problems))
for path, s in plans.items():
    open(path, "w", encoding="utf-8").write(s)
print("w76 done. Focused menu on all pages; %d file(s) changed." % len(plans))
