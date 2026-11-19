#!/usr/bin/env python3
"""w29: Travel Essentials hub, Narita card: a small "Download to your phone / Narita Pocket Guide / Works offline"
button at the bottom right of the card (same look as the button at the top of the article).
Run from the repo root (~/packsmart):  python3 tools/w29_narita_card_badge.py
Idempotent. Only touches public/travel-essentials.html. Also replaces the earlier one-line pill if that is live.
"""
import os, re, sys
PAGE = "public/travel-essentials.html"
if not os.path.exists(PAGE):
    sys.exit("run this from the repo root (cannot find " + PAGE + ")")
s = open(PAGE, encoding="utf-8").read()
if "pg-badge2-css" in s:
    print("nothing to do (already applied)")
    sys.exit(0)

# 1) undo the earlier one-line pill, if it was applied
s = re.sub(r'<style id="pg-badge-css">.*?</style>\n?', "", s, flags=re.S)
i = s.find('href="/blog/narita-airport-guide" class="blog-card"')
j = s.find("</a>", i)
if i < 0 or j < 0:
    sys.exit("Narita card not found; page not changed")
seg = s[i:j]
seg = re.sub(r'\s*<span class="pg-badge">.*?</span>', "", seg, flags=re.S)
seg = seg.replace('<div class="blog-card-body pg-has-badge">', '<div class="blog-card-body">')

# 2) new markup
BR_MORE = '<br><span class="read-more">Read more &rarr;</span>'
if seg.count(BR_MORE) != 1:
    sys.exit("card markup is not what was expected; page not changed")
NEW = ('<div class="pg-row"><span class="read-more">Read more &rarr;</span>'
       '<span class="pg-badge"><span>Download to your phone</span><b>Narita Pocket Guide</b><span>Works offline</span></span></div>')
seg = seg.replace(BR_MORE, NEW, 1)
s = s[:i] + seg + s[j:]

CSS = """<style id="pg-badge2-css">
.pg-row{display:flex;justify-content:space-between;align-items:flex-end;gap:.75rem;margin-top:.5rem}
.pg-badge{display:block;background:#00C9A7;color:#0f0f23;text-align:center;border-radius:12px;padding:.5rem .9rem;line-height:1.25}
.pg-badge span{display:block;font-size:.68rem;font-weight:700;opacity:.85}
.pg-badge b{display:block;font-size:.85rem;font-weight:800}
@media (max-width:340px){.pg-row{flex-wrap:wrap}}
</style>
"""
if s.count("</head>") != 1:
    sys.exit("unexpected </head> count; page not changed")
s = s.replace("</head>", CSS + "</head>", 1)
open(PAGE, "w", encoding="utf-8").write(s)
print("changed:\n  - travel-essentials.html (Narita card: Download button)")
