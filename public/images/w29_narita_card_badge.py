#!/usr/bin/env python3
"""w29: Travel Essentials hub, Narita card: a small "Narita Guide Inside" pill at the bottom right of the card.
Run from the repo root (~/packsmart):  python3 public/images/w29_narita_card_badge.py
Idempotent. Only touches public/travel-essentials.html.
"""
import os, sys
PAGE = "public/travel-essentials.html"
if not os.path.exists(PAGE):
    sys.exit("run this from the repo root (cannot find " + PAGE + ")")
s = open(PAGE, encoding="utf-8").read()
if "pg-badge-css" in s:
    if "Free offline guide" in s:   # earlier wording already pushed: just change the words
        open(PAGE, "w", encoding="utf-8").write(s.replace("Free offline guide", "Narita Guide Inside"))
        print("changed:\n  - travel-essentials.html (pill wording updated)")
    else:
        print("nothing to do (already applied)")
    sys.exit(0)
i = s.find('href="/blog/narita-airport-guide" class="blog-card"')
j = s.find("</a>", i)
if i < 0 or j < 0:
    sys.exit("Narita card not found; page not changed")
seg = s[i:j]
BODY_OLD = '<div class="blog-card-body">'
MORE_OLD = '<span class="read-more">Read more &rarr;</span>'
if seg.count(BODY_OLD) != 1 or seg.count(MORE_OLD) != 1:
    sys.exit("card markup is not what was expected; page not changed")
seg = seg.replace(BODY_OLD, '<div class="blog-card-body pg-has-badge">', 1)
seg = seg.replace(MORE_OLD, MORE_OLD + '\n                <span class="pg-badge">&#128241; Narita Guide Inside</span>', 1)
CSS = """<style id="pg-badge-css">
.pg-has-badge{position:relative}
.pg-badge{position:absolute;right:2rem;bottom:2rem;background:#00C9A7;color:#0f0f23;font-size:.8rem;font-weight:800;padding:.4rem .75rem;border-radius:999px;line-height:1.1;white-space:nowrap}
@media (max-width:420px){.pg-badge{font-size:.72rem;padding:.35rem .6rem;right:1.5rem;bottom:2rem}}
@media (max-width:340px){.pg-badge{position:static;display:inline-block;margin-top:.8rem}}
</style>
"""
s = s[:i] + seg + s[j:]
if s.count("</head>") != 1:
    sys.exit("unexpected </head> count; page not changed")
s = s.replace("</head>", CSS + "</head>", 1)
open(PAGE, "w", encoding="utf-8").write(s)
print("changed:\n  - travel-essentials.html (Narita card: Narita Guide Inside pill)")
