#!/usr/bin/env python3
"""
w69: honest read times (24 Nov 2026, owner's request).

The "N min read" labels were typed by hand in the generators and card scripts, and many were far off
(the Ueno guide said 10 minutes for about 4,700 words). This sets every label from the words actually on
the article.

What it does:
  1. For each public/blog/*.html that already shows "N min read": count the words in its main text
     (the <div class="content"> block, or <main>/<article>/<body> if there is none), without scripts and styles,
     and set the label to round(words / 230), at least 3. Pages with no label are left alone.
  2. On public/blog.html, public/travel-essentials.html and public/index.html, every "N min read" that belongs
     to a card linking to /blog/<slug> gets that article's number (the nearest /blog/ link before the label,
     within the same card).

Run it last in the chain (after w65), and after editing any article:  python3 tools/w69_read_times.py
Idempotent: a second run changes nothing. Aborts without writing if an article shows more than one label.
"""
import glob, html, os, re, sys

ROOT = os.getcwd()
PUB = os.path.join(ROOT, "public")
WPM = 230
LABEL = re.compile(r"(\d+)(\s*min read)")


def die(msg):
    sys.exit("w69 aborted, nothing written: " + msg)


def main_text(s):
    m = re.search(r'<div class="content"[^>]*>', s)
    if m:
        d, depth, end = m.start(), 0, None
        for t in re.finditer(r"<(/?)div\b[^>]*>", s[d:]):
            depth += -1 if t.group(1) else 1
            if depth == 0:
                end = d + t.end()
                break
        s = s[d:end] if end else s[d:]
    else:
        m = re.search(r"<(main|article)\b.*?</\1>", s, re.S) or re.search(r"<body\b.*?</body>", s, re.S)
        s = m.group(0) if m else s
    s = re.sub(r"<script\b.*?</script>|<style\b.*?</style>|<!--.*?-->", " ", s, flags=re.S)
    return html.unescape(re.sub(r"<[^>]+>", " ", s))


minutes, plans = {}, {}
for f in sorted(glob.glob(os.path.join(PUB, "blog", "*.html"))):
    s = open(f, encoding="utf-8").read()
    labels = LABEL.findall(s)
    if not labels:
        continue
    if len(labels) > 1:
        die("%s shows %d read-time labels" % (os.path.basename(f), len(labels)))
    words = len(main_text(s).split())
    n = max(3, int(words / WPM + 0.5))
    slug = os.path.basename(f)[:-5]
    minutes[slug] = n
    new = LABEL.sub(lambda m: "%d%s" % (n, m.group(2)), s)
    if new != s:
        plans[f] = new

for name in ("blog.html", "travel-essentials.html", "index.html"):
    f = os.path.join(PUB, name)
    if not os.path.isfile(f):
        continue
    s = open(f, encoding="utf-8").read()
    out, last = [], 0
    for m in LABEL.finditer(s):
        before = s[max(0, m.start() - 3000):m.start()]
        links = re.findall(r'href="(?:https://www\.packsmartapp\.com)?/blog/([a-z0-9-]+?)(?:\.html)?"', before)
        slug = links[-1] if links else None
        out.append(s[last:m.start()])
        out.append("%d%s" % (minutes[slug], m.group(2)) if slug in minutes else m.group(0))
        last = m.end()
    out.append(s[last:])
    new = "".join(out)
    if new != s:
        plans[f] = new

for f, s in plans.items():
    open(f, "w", encoding="utf-8").write(s)
print("w69 done. %d file(s) changed." % len(plans))
for f in sorted(plans):
    print("  - " + os.path.relpath(f, ROOT))
