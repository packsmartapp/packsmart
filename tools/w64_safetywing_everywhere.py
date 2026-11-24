#!/usr/bin/env python3
"""
w64: the SafetyWing travel medical insurance block on every article, and a check that keeps it there (23 Nov 2026).

58 articles carry the SafetyWing block (headline, quote button, price widget, "Nomad Insurance Complete" card).
11 never had it: the Japan airport, station and city guides (their generators copy only the eSIM and airport
transfer blocks from the Japan guide) and two list articles. Nobody decided to leave it out; it was missed.

What it does:
  1. Copies the block exactly as it stands on public/blog/japan-travel-packing-guide.html (marker comment
     "<!-- SAFETYWING INSURANCE WIDGET -->", one balanced <div>) and inserts it just before <footer class="footer">
     on each page in TARGETS that does not have it, which is where it sits on the Japan guide.
  2. Adds the widget's size rules (CSS and the centring script the other articles carry) and the GA4 placement script (affiliate_view / affiliate_interact) before </body> where a page lacks it.
  3. CHECK: every public/blog/*.html must now have the SafetyWing price widget, except pages listed in EXEMPT (with a reason).
     A new article or a new generated page without it makes this script fail, so it is noticed before a push.

Run it last in the chain (after w59), and after adding any article:  python3 tools/w64_safetywing_everywhere.py
Idempotent (marker: the comment above). Aborts without writing if the source block or an anchor is missing.
"""
import glob, os, re, sys

ROOT = os.getcwd()
BLOG = os.path.join(ROOT, "public", "blog")
SRC = os.path.join(BLOG, "japan-travel-packing-guide.html")
MARK = "<!-- SAFETYWING INSURANCE WIDGET -->"
HAS = 'class="safetywing-price-widget" data-safetywingaffiliateid'   # the widget itself (some pages lack the comment)
TARGETS = [
    "narita-airport-guide", "haneda-airport-guide", "kansai-airport-guide",
    "tokyo-station-guide", "shinjuku-station-guide", "ueno-station-guide", "kyoto-station-guide", "osaka-station-guide",
    "new-chitose-airport-guide", "sapporo-station-guide",
    "kyoto-travel-guide", "osaka-travel-guide",
    "budget-travel-destinations-2026", "carry-on-packing-list",
]
EXEMPT = {}   # "page-slug": "reason it has no SafetyWing block"


def die(msg):
    sys.exit("w64 aborted, nothing written: " + msg)


def block(s):
    c = s.find(MARK)
    if c < 0:
        return None
    d = s.find("<div", c)
    depth = 0
    for t in re.finditer(r"<(/?)div\b[^>]*>", s[d:]):
        depth += -1 if t.group(1) else 1
        if depth == 0:
            return s[c:d + t.end()]
    die("unbalanced SafetyWing block")


src = open(SRC, encoding="utf-8").read()
SW = block(src)
if not SW or "safetywing-price-widget" not in SW or "safetywing-complete" not in SW:
    die("SafetyWing block not found as expected on the Japan guide")
m = re.search(r"<script>\s*\(function\(\)\{\s*if\(!\('IntersectionObserver' in window\)\|\|typeof gtag!=='function'\)return;.*?</script>", src, re.S)
if not m or "affiliate_view" not in m.group(0):
    die("GA4 placement script not found on the Japan guide")
PLACE_JS = m.group(0)
# the size rules the other articles carry for the widget (without them it is 450px wide on a 390px phone)
FIT_CSS = '<style>html,body{overflow-x:hidden;max-width:100vw;} .safetywing-price-widget{max-width:100%;}</style>'
m2 = re.search(r"if\(document\.querySelector\('\.safetywing-price-widget'\)\)\{const swObs=.*?\n", src)
if FIT_CSS not in src or not m2:
    die("widget size rules not found on the Japan guide")
FIT_JS = "<script>\n" + m2.group(0) + "</script>"

plans, added = {}, []
for slug in TARGETS:
    path = os.path.join(BLOG, slug + ".html")
    if not os.path.isfile(path):
        die("missing " + path)
    s = open(path, encoding="utf-8").read()
    o = s
    if HAS not in s:
        if s.count('<footer class="footer">') != 1:
            die(slug + ": footer anchor not found exactly once")
        s = s.replace('<footer class="footer">', SW + "\n\n\n" + '<footer class="footer">', 1)
        added.append(slug)
    if FIT_CSS not in s:
        if s.count("</head>") != 1:
            die(slug + ": </head> not found exactly once")
        s = s.replace("</head>", FIT_CSS + "\n</head>", 1)
    if "const swObs=" not in s:
        s = s.replace("</body>", FIT_JS + "\n</body>", 1)
    if "affiliate_view" not in s:
        if s.count("</body>") != 1:
            die(slug + ": </body> not found exactly once")
        s = s.replace("</body>", PLACE_JS + "\n</body>", 1)
    if s != o:
        plans[path] = s

for path, s in plans.items():
    open(path, "w", encoding="utf-8").write(s)

# check: every article has the block
missing = []
for path in sorted(glob.glob(os.path.join(BLOG, "*.html"))):
    slug = os.path.basename(path)[:-5]
    if slug in EXEMPT:
        continue
    if HAS not in open(path, encoding="utf-8").read():
        missing.append(slug)
print("w64 done. SafetyWing block added to %d page(s)%s" % (len(added), "".join("\n  - " + a for a in added)))
if missing:
    sys.exit("w64 CHECK FAILED: no SafetyWing block on %s. Add the page to TARGETS (or to EXEMPT with a reason)."
             % ", ".join(missing))
print("w64 check: every article has the SafetyWing block.")
