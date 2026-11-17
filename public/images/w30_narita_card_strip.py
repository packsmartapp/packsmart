#!/usr/bin/env python3
"""w30: Travel Essentials hub, Narita card. Replaces the three-line Download button (w29) with a one-line mint
strip "Narita Pocket Guide Inside", and moves "Read more ->" up beside "8 min read".
Run from the repo root (~/packsmart):  python3 public/images/w30_narita_card_strip.py
Idempotent. Only touches public/travel-essentials.html. Works whether the page is untouched, has the early pill,
or has the w29 button.
"""
import os, re, sys
PAGE = "public/travel-essentials.html"
if not os.path.exists(PAGE):
    sys.exit("run this from the repo root (cannot find " + PAGE + ")")
s = open(PAGE, encoding="utf-8").read()
if "pg-strip-css" in s:
    print("nothing to do (already applied)")
    sys.exit(0)

# 1) remove earlier CSS (early pill and w29 button)
s = re.sub(r'<style id="pg-badge-css">.*?</style>\n?', "", s, flags=re.S)
s = re.sub(r'<style id="pg-badge2-css">.*?</style>\n?', "", s, flags=re.S)

i = s.find('href="/blog/narita-airport-guide" class="blog-card"')
j = s.find("</a>", i)
if i < 0 or j < 0:
    sys.exit("Narita card not found; page not changed")
seg = s[i:j]

# 2) remove earlier markup (early pill / w29 row), back to the plain "<br>Read more" form
seg = re.sub(r'\s*<span class="pg-badge">.*?</span>\s*(?=\n|<)', "", seg, flags=re.S) if "pg-row" not in seg else seg
seg = seg.replace('<div class="blog-card-body pg-has-badge">', '<div class="blog-card-body">')
seg = seg.replace('<div class="blog-card-body">', '<div class="blog-card-body pg-body">', 1)
seg = re.sub(r'<div class="pg-row">.*?</div>', '<br><span class="read-more">Read more &rarr;</span>', seg, flags=re.S)

# 3) new markup: meta line with Read more, then the strip
META = '<span class="meta">November 16, 2026 &middot; 8 min read</span>'
BR_MORE = '<br><span class="read-more">Read more &rarr;</span>'
if seg.count(META) != 1 or seg.count(BR_MORE) != 1:
    sys.exit("card markup is not what was expected; page not changed")
ICON = ('<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" '
        'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 4v11M7 11l5 5 5-5M5 20h14"/></svg>')
NEW = ('<div class="pg-meta">' + META + '<span class="read-more">Read more &rarr;</span></div>\n'
       '                <span class="pg-strip"><span class="pg-ic">' + ICON + '</span>'
       '<span class="pg-tx">Narita Pocket Guide Inside</span></span>')
seg, n = re.subn(re.escape(META) + r"\s*" + re.escape(BR_MORE), lambda m: NEW, seg, count=1)
if n != 1:
    sys.exit("card markup is not in the expected order; page not changed")
s = s[:i] + seg + s[j:]

CSS = """<style id="pg-strip-css">
.pg-meta{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:baseline;column-gap:.6rem;row-gap:.25rem}
.pg-meta .read-more{white-space:nowrap}
.pg-strip{display:flex;align-items:center;gap:.65rem;margin-top:1rem;background:#E7FAF5;border:1px solid #bfeee2;color:#0f0f23;border-radius:12px;padding:.5rem .8rem .5rem .55rem}
.pg-ic{flex:none;width:30px;height:30px;border-radius:9px;background:#00C9A7;display:flex;align-items:center;justify-content:center}
.pg-tx{flex:1;font-weight:800;font-size:.9rem;line-height:1.25}
@media (max-width:480px){.blog-card-body.pg-body{padding-left:1.3rem;padding-right:1.3rem}.pg-meta .read-more{font-size:.85rem}}
</style>
"""
if s.count("</head>") != 1:
    sys.exit("unexpected </head> count; page not changed")
s = s.replace("</head>", CSS + "</head>", 1)
open(PAGE, "w", encoding="utf-8").write(s)
print("changed:\n  - travel-essentials.html (Narita card: Pocket Guide strip; Read more beside 8 min read)")
