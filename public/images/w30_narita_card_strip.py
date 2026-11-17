#!/usr/bin/env python3
"""w30 (v3): Travel Essentials hub, Narita card. A one-block mint strip, no icon:
   "Narita Pocket Guide Inside" with "Works offline" under it; "Read more ->" sits beside "8 min read".
Run from the repo root (~/packsmart):  python3 public/images/w30_narita_card_strip.py
Idempotent. Only touches public/travel-essentials.html. Works from any earlier state of the card
(untouched, early pill, w29 button, or the earlier w30 strip with the download icon).
"""
import os, re, sys
PAGE = "public/travel-essentials.html"
if not os.path.exists(PAGE):
    sys.exit("run this from the repo root (cannot find " + PAGE + ")")
s = open(PAGE, encoding="utf-8").read()
if 'id="pg-strip-css3"' in s:
    print("nothing to do (already applied)")
    sys.exit(0)

# 1) remove every earlier stylesheet for this card
for sid in ("pg-badge-css", "pg-badge2-css", "pg-strip-css"):
    s = re.sub(r'<style id="%s">.*?</style>\n?' % sid, "", s, flags=re.S)

i = s.find('href="/blog/narita-airport-guide" class="blog-card"')
j = s.find("</a>", i)
if i < 0 or j < 0:
    sys.exit("Narita card not found; page not changed")
seg = s[i:j]

META = '<span class="meta">November 16, 2026 &middot; 8 min read</span>'
BR_MORE = '<br><span class="read-more">Read more &rarr;</span>'

# 2) take the card back to its plain form (meta, then "Read more")
seg = seg.replace('<div class="blog-card-body pg-has-badge">', '<div class="blog-card-body">')
seg = seg.replace('<div class="blog-card-body pg-body">', '<div class="blog-card-body">')
# earlier w30 strip (with icon, with or without arrow)
seg = re.sub(r'\s*<span class="pg-strip">.*?<span class="pg-tx">.*?</span>(?:<span class="pg-go">.*?</span>)?</span>', "", seg, flags=re.S)
seg = re.sub(r'<div class="pg-meta">(.*?)<span class="read-more">.*?</span></div>', lambda m: m.group(1) + BR_MORE, seg, flags=re.S)
# w29 button row
seg = re.sub(r'<div class="pg-row">.*?</div>', BR_MORE, seg, flags=re.S)
# early one-line pill
seg = re.sub(r'\s*<span class="pg-badge">.*?</span>', "", seg, flags=re.S)
if "pg-" in seg.replace("pg-body", "").replace("pg-meta", "").replace("pg-strip", ""):
    pass
if seg.count(META) != 1 or seg.count(BR_MORE) != 1:
    sys.exit("card markup is not what was expected; page not changed")

# 3) new markup
NEW = ('<div class="pg-meta">' + META + '<span class="read-more">Read more &rarr;</span></div>\n'
       '                <span class="pg-strip"><b>Narita Pocket Guide Inside</b><i>Works offline</i></span>')
seg, n = re.subn(re.escape(META) + r"\s*" + re.escape(BR_MORE), lambda m: NEW, seg, count=1)
if n != 1:
    sys.exit("card markup is not in the expected order; page not changed")
seg = seg.replace('<div class="blog-card-body">', '<div class="blog-card-body pg-body">', 1)
s = s[:i] + seg + s[j:]

CSS = """<style id="pg-strip-css3">
.pg-meta{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:baseline;column-gap:.6rem;row-gap:.25rem}
.pg-meta .read-more{white-space:nowrap}
.pg-strip{display:block;margin-top:1rem;background:#E7FAF5;border:1px solid #bfeee2;color:#0f0f23;border-radius:12px;padding:.6rem .9rem;text-align:center;line-height:1.25}
.pg-strip b{display:block;font-weight:800;font-size:.92rem}
.pg-strip i{display:block;font-style:normal;font-weight:600;font-size:.76rem;opacity:.75;margin-top:2px}
@media (max-width:480px){.blog-card-body.pg-body{padding-left:1.3rem;padding-right:1.3rem}.pg-meta .read-more{font-size:.85rem}}
</style>
"""
if s.count("</head>") != 1:
    sys.exit("unexpected </head> count; page not changed")
s = s.replace("</head>", CSS + "</head>", 1)
open(PAGE, "w", encoding="utf-8").write(s)
print("changed:\n  - travel-essentials.html (Narita card: text-only Pocket Guide strip; Read more beside 8 min read)")
