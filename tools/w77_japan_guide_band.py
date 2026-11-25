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
CHECKED = re.compile(r"[Cc]hecked (?:on )?(\d{1,2})(?: and (\d{1,2}))? ([A-Z][a-z]+) (20\d\d)")
HERO = re.compile(r'<div class="hero-blog".*?\n</div>\n', re.S)
BAND = re.compile(r"<!-- jp-band -->.*?<!-- /jp-band -->\n", re.S)

WAVE = ("url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='40' height='20'%3E%3Cg fill='none' "
        "stroke='%2300C9A7' stroke-opacity='.18'%3E%3Cpath d='M0 20a10 10 0 0 1 20 0M5 20a5 5 0 0 1 10 0M20 20a10 10 0 0 1 20 0M25 20a5 5 0 0 1 10 0"
        "M-10 10a10 10 0 0 1 20 0M10 10a10 10 0 0 1 20 0M30 10a10 10 0 0 1 20 0'/%3E%3C/g%3E%3C/svg%3E\")")
CSS = """<style id="jp-guide-css">
.jp-band{background:#FDF0F2 """ + WAVE + """;border-bottom:1px solid #F3D3DA;padding:14px 16px 18px}
.jp-band-in{max-width:760px;margin:0 auto}
.jp-crumb{font-size:.82rem;color:#5a6378;margin:0 0 10px}.jp-crumb a{color:#0a8f78;font-weight:700;text-decoration:none}.jp-crumb a:hover{text-decoration:underline}
.jp-crumb span{margin:0 6px;color:#b4bccb}
.jp-namesign{position:relative;display:flex;align-items:center;gap:14px;background:#fff;border:1px solid #BFEDE3;border-radius:16px;padding:12px 16px;box-shadow:0 8px 20px rgba(0,168,140,.08)}
.jp-namesign-k{font-size:1.9rem;font-weight:800;letter-spacing:.08em;color:#0f0f23;line-height:1.1}
.jp-namesign-e{display:flex;flex-direction:column;min-width:0}
.jp-namesign-e small{font-size:.7rem;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:#E94560}
.jp-namesign-e b{font-size:1rem;color:#0f0f23}
.jp-namesign-bar{flex:1;align-self:stretch;min-width:12px;border-radius:4px;background:linear-gradient(90deg,#00C9A7,#7FE3D0);height:6px;margin:auto 0}
.jp-namesign-st{flex:none;transform:rotate(-10deg);border:2px solid #E94560;color:#E94560;border-radius:8px;padding:3px 6px;font-size:.6rem;font-weight:800;letter-spacing:.05em;text-align:center;line-height:1.15;opacity:.85}
.psn-now{background-image:""" + WAVE + """!important}
@media (max-width:600px){.jp-namesign{flex-wrap:wrap;gap:8px 12px}.jp-namesign-k{font-size:1.5rem}.jp-namesign-bar{display:none}.jp-namesign-st{position:absolute;right:12px;top:-12px;background:#fff}}
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
            '<div class="jp-namesign"><span class="jp-namesign-k" lang="ja">%s</span><span class="jp-namesign-e"><small><span lang="ja">%s</span> · %s</small><b>%s</b></span>'
            '<span class="jp-namesign-bar" aria-hidden="true"></span>'
            '<span class="jp-namesign-st" title="Checked against official sources">確認<br>%s</span></div>'
            '</div></div>\n<!-- /jp-band -->\n') % (href, sec, en, ja, k, label, en, checked.strftime("%-d %b %Y").upper().replace(" 20", "<br>20", 1))


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
