#!/usr/bin/env python3
"""
w79: a "Japan hub" card near the end of the 15 Japan pages, so readers find the /japan hub (25 Nov 2026).

The hub is the site's best-designed page and the owner wants readers to see it. Each Japan page gets one card, just
before "Related posts" (or, on the two articles without related posts, just before the travel-insurance box), so it
never interrupts the article or pushes down the partner boxes:

  * on the 15 Japan pages (the w77 list): "Everything for your Japan trip, in one place", link /japan?src=jp_card;
  * not on other articles: tried on all of them (25 Nov, "Thinking about Japan next?", /japan?src=art_card), then
    dropped the same day at the owner's call (a Germany reader would get Japan on top of the other countries' links).
    The script removes the card from any article outside the Japan list. The "art" copy is kept for a later trial.

The card previews the hub's look: washi pink with the wave print, a drawn Mount Fuji with a red sun and a sakura
branch, a few falling petals (still when the reader prefers reduced motion), what the hub holds (4 airports,
6 stations, 10 offline Pocket Guides, Ask Packy) and a button in our outline style. A click sends the GA4 event
"hub_card" (status = jp or art). It is one link, with no partner links and no prices.

The card sits between <!-- ps-hub-card --> markers and its CSS is one <style id="ps-hubc-css"> block in <head>; both are
replaced as a whole, so re-running is safe. w69 leaves the card out of the read time.
Run after w77 and w78, before w76 and w72:  python3 tools/w79_hub_card.py
Stops without writing if an article has neither anchor, or no single </head> line.
"""
import glob, os, re, sys

ROOT = os.getcwd()
BLOG = os.path.join(ROOT, "public", "blog")
JAPAN = {  # the w77 pages
    "tokyo-station-guide", "shinjuku-station-guide", "ueno-station-guide", "kyoto-station-guide", "osaka-station-guide",
    "sapporo-station-guide", "narita-airport-guide", "haneda-airport-guide", "kansai-airport-guide",
    "new-chitose-airport-guide", "kyoto-travel-guide", "osaka-travel-guide", "japan-travel-packing-guide",
    "japan-travel-packing-guide-from-india", "japan-7-day-itinerary-budget",
}
WAVE = ("url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='40' height='20'%3E%3Cg fill='none' "
        "stroke='%2300C9A7' stroke-opacity='.16'%3E%3Cpath d='M0 20a10 10 0 0 1 20 0M5 20a5 5 0 0 1 10 0M20 20a10 10 0 0 1 20 0M25 20a5 5 0 0 1 10 0"
        "M-10 10a10 10 0 0 1 20 0M10 10a10 10 0 0 1 20 0M30 10a10 10 0 0 1 20 0'/%3E%3C/g%3E%3C/svg%3E\")")

PETAL = '<path d="M0 0C-3-2-4-8-1.2-10L0-8.8 1.2-10C4-8 3-2 0 0Z"/>'
FLOWER = lambda x, y, s: ('<g transform="translate(%s %s) scale(%s)" fill="#F7A8BC">' % (x, y, s)
                          + "".join('<g transform="rotate(%d)">%s</g>' % (a, PETAL) for a in (0, 72, 144, 216, 288))
                          + '<circle r="1.6" fill="#E94560"/></g>')
ART = ('<svg viewBox="0 0 220 160" preserveAspectRatio="xMidYMax slice" role="img" aria-label="Mount Fuji with a red sun and cherry blossoms">'
       '<defs><linearGradient id="hubcM" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6f86b8"/><stop offset="1" stop-color="#3f5a96"/></linearGradient>'
       '<linearGradient id="hubcS" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#e6edf8"/></linearGradient></defs>'
       '<circle cx="152" cy="52" r="22" fill="#E94560" opacity=".9"/>'
       '<path d="M58 44q10-8 22-2q8-6 16 2" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round" opacity=".9"/>'
       '<path d="M8 138 82 58q14-14 28-14t28 14l74 80z" fill="url(#hubcM)"/>'
       '<path d="M82 58q14-14 28-14t28 14l-9 10-7-6-7 8-6-7-7 7-7-6-6 6z" fill="url(#hubcS)"/>'
       '<path d="M0 138h220v22H0z" fill="#9fd8cf"/><path d="M0 141q55-8 110 0t110 0" fill="none" stroke="#fff" stroke-width="2" opacity=".7"/>'
       '<path d="M168 138v-30M190 138v-30M162 108h34M164 116h30" stroke="#E94560" stroke-width="5" stroke-linecap="round"/>'
       '<path d="M-4 22q30 4 50 22t26 30" fill="none" stroke="#6b4a3a" stroke-width="4" stroke-linecap="round"/>'
       '<path d="M30 33q4 14 0 22" fill="none" stroke="#6b4a3a" stroke-width="2.5" stroke-linecap="round"/>'
       + FLOWER(12, 26, 1.1) + FLOWER(34, 36, 1.3) + FLOWER(52, 52, 1) + FLOWER(28, 58, 1.1) + FLOWER(66, 70, .9) + FLOWER(46, 24, .8)
       + '</svg>')
FALL = "".join('<i class="hubc-pt" style="left:%d%%;animation-delay:%ss;animation-duration:%ss"></i>' % (l, d, t)
               for l, d, t in ((14, 0, 7), (38, 2.4, 8), (62, 1.1, 6.5), (84, 3.6, 7.5)))

COPY = {
    "jp": ('<span lang="ja">ようこそ</span> · Your Japan hub', 'Everything for your <em>Japan</em> trip, in one place',
           "All our airport, station and city guides together, offline Pocket Guides for your phone, and Packy, your Japan "
           "travel buddy. Facts checked against official sources."),
    "art": ('<span lang="ja">日本</span> · The Japan hub', 'Thinking about <em>Japan</em> next?',
            "Arrive and get around with ease: airport and station guides, offline Pocket Guides for your phone, and Packy, "
            "your Japan travel buddy. Facts checked against official sources."),
}


def card(kind):
    kick, title, text = COPY[kind]
    return ('<!-- ps-hub-card -->\n'
            '<aside class="hubc" aria-label="The PackSmart Japan hub"><a class="hubc-in" href="/japan?src=%s_card" '
            "onclick=\"try{if(window.gtag)gtag('event','hub_card',{event_category:'navigation',status:'%s',page_path:location.pathname});}catch(e){}\">"
            '<span class="hubc-art" aria-hidden="true">%s%s</span>'
            '<span class="hubc-txt"><small class="hubc-k">%s</small><b class="hubc-t">%s</b><span class="hubc-p">%s</span>'
            '<span class="hubc-chips"><i>✈️ 4 airports</i><i>🚉 6 stations</i><i>📱 10 offline Pocket Guides</i><i>💬 Ask Packy</i></span>'
            '<span class="hubc-btn">Explore the Japan hub <span aria-hidden="true">→</span></span></span></a></aside>\n'
            '<!-- /ps-hub-card -->\n') % (kind, kind, ART, FALL, kick, title, text)


CSS = """<style id="ps-hubc-css">
@import url("https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&display=swap");
.hubc{max-width:800px;margin:2.6rem auto 0;padding:0 2rem;box-sizing:border-box}
:is(.content,.article) .hubc{max-width:none;padding:0}
@media (min-width:1200px){:is(.content,.article) .hubc-in{grid-template-columns:260px minmax(0,1fr);gap:28px;padding:22px 28px 22px 22px}}
.hubc-in{position:relative;display:grid;grid-template-columns:200px minmax(0,1fr);gap:22px;align-items:center;background:#FDF0F2 """ + WAVE + """;border:1px solid #F3D3DA;border-radius:22px;padding:20px 24px 20px 20px;text-decoration:none!important;color:#0f0f23;overflow:hidden;box-shadow:0 10px 30px rgba(233,69,96,.08);transition:transform .2s,box-shadow .2s}
.hubc-in:hover,.hubc-in:focus-visible{transform:translateY(-2px);box-shadow:0 16px 38px rgba(233,69,96,.16)}
.hubc-art{position:relative;display:block;background:linear-gradient(180deg,#fff7f0 0%,#fde6ea 100%);border-radius:16px;overflow:hidden;aspect-ratio:11/8}
.hubc-art svg{display:block;width:100%;height:100%}
.hubc-pt{position:absolute;top:-10px;width:9px;height:9px;background:#F7A8BC;border-radius:9px 0 9px 0;opacity:.9;animation:hubcFall linear infinite}
@keyframes hubcFall{0%{transform:translate(0,0) rotate(0)}100%{transform:translate(-30px,170px) rotate(300deg);opacity:.2}}
@media (prefers-reduced-motion:reduce){.hubc-pt{animation:none;display:none}.hubc-in{transition:none}}
.hubc-txt{display:block;min-width:0}
.hubc-k{display:inline-block;font-size:.72rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:#0a8f78;background:#fff;border:1px solid #BFEDE3;border-radius:999px;padding:4px 11px;margin-bottom:8px}
.hubc-t{display:block;font-size:1.45rem;line-height:1.2;font-weight:700;margin:0 0 6px;color:#0f0f23!important}
.hubc-t em{font-family:'Instrument Serif',Georgia,serif;font-style:italic;font-weight:400;color:#E94560;font-size:1.2em}
.hubc-p{display:block;font-size:.93rem;line-height:1.55;color:#4a5160!important;margin:0 0 10px}
.hubc-chips{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 14px}
.hubc-chips i{font-style:normal;font-size:.78rem;font-weight:600;color:#0f0f23;background:#fff;border:1px solid #F3D3DA;border-radius:999px;padding:4px 10px}
.hubc-btn{display:inline-block;font-weight:700;font-size:.95rem;color:#0f0f23;background:#fff;border:2px solid #00C9A7;border-radius:10px;padding:10px 18px;transition:background .15s,color .15s}
.hubc-in:hover .hubc-btn,.hubc-in:focus-visible .hubc-btn{background:#00C9A7;color:#fff}
@media (max-width:640px){.hubc{padding:0 1rem}:is(.content,.article) .hubc{padding:0}
 .hubc-in{grid-template-columns:1fr;gap:14px;padding:14px 14px 18px}
 .hubc-art{aspect-ratio:auto;height:160px}
 .hubc-t{font-size:1.25rem}.hubc-btn{display:block;text-align:center}}
</style>
"""
BLOCK = re.compile(r"<!-- ps-hub-card -->.*?<!-- /ps-hub-card -->\n", re.S)
CSSBLOCK = re.compile(r'<style id="ps-hubc-css">.*?</style>\n', re.S)
ANCHORS = ('<div class="related-posts">', "<!-- SAFETYWING INSURANCE WIDGET -->")

plans, problems, counts = {}, [], {"jp": 0, "art": 0}
for path in sorted(glob.glob(os.path.join(BLOG, "*.html"))):
    slug = os.path.basename(path)[:-5]
    s = open(path, encoding="utf-8").read()
    new = CSSBLOCK.sub("", BLOCK.sub("", s))
    kind = "jp" if slug in JAPAN else "art"
    if kind == "art":   # owner, 25 Nov: a Germany reader would see Japan plus other countries' links, too many
        if new != s:
            plans[path] = new
        continue
    at = next((new.find(a) for a in ANCHORS if new.find(a) >= 0), -1)
    if at < 0:
        problems.append(slug + " (no anchor)")
        continue
    line = new.rfind("\n", 0, at) + 1
    new = new[:line] + card(kind) + new[line:]
    heads = list(re.finditer(r"(?m)^[ \t]*</head>", new))
    if len(heads) != 1:
        problems.append(slug + " (</head>)")
        continue
    new = new[:heads[0].start()] + CSS + new[heads[0].start():]
    counts[kind] += 1
    if new != s:
        plans[path] = new
missing = JAPAN - {os.path.basename(p)[:-5] for p in glob.glob(os.path.join(BLOG, "*.html"))}
if missing:
    problems.append("Japan page missing: " + ", ".join(sorted(missing)))
if problems:
    sys.exit("w79 aborted, nothing written: " + "; ".join(problems))
for path, s in plans.items():
    open(path, "w", encoding="utf-8").write(s)
print("w79 done. Japan hub card on %d Japan page(s), none on other articles; %d file(s) changed."
      % (counts["jp"], len(plans)))
