#!/usr/bin/env python3
"""
w62: fix article photos that do not show what they say, and move out-of-place cross-links (23 Nov 2026).

A visual check of every <figure> photo on the articles (by Claude, 23 Nov 2026; list in
tools/w62_photo_fixes.json) found 92 problems: photos that show a different place or thing than the
alt text and caption claim (e.g. Machu Picchu as Granada, a raccoon as a toucan), one broken image,
three with faces in close-up, and a few right photos under the wrong heading.

What it does:
  1. Removes every <figure> listed with action "remove" (matched by page + exact alt + caption, so the
     same stock photo used correctly elsewhere is untouched).
  2. Moves the figures listed with action "move" to just after the named <h3>.
  3. Moves "Also visiting <country>?" style callouts out of unrelated sections (city, weather,
     religious sites) to just before the page's FAQ heading, so readers meet them at the end.

Run from the repo root:  python3 tools/w62_fix_article_photos.py
Idempotent: a figure or callout already removed or moved is skipped. Aborts without writing if a
listed item is found in an unexpected state (for example a move target heading is missing).
Replacement photos are a separate, later step (each one checked visually before it goes in).
"""
import html, json, os, re, sys

ROOT = os.getcwd()
BLOG = os.path.join(ROOT, "public", "blog")
FIXES = json.load(open(os.path.join(ROOT, "tools", "w62_photo_fixes.json"), encoding="utf-8"))

# page -> list of callout text starts to move before the FAQ
CALLOUTS = {
    "italy-travel-packing-guide.html": ["Also visiting Greece?", "Extend to Switzerland"],
    "france-travel-packing-guide.html": ["Also visiting Spain?"],
    "germany-travel-packing-guide.html": ["Also visiting Switzerland or France?"],
    "portugal-travel-packing-guide.html": ["Also visiting Spain?"],
    "switzerland-travel-packing-guide.html": ["Also visiting France or Italy?"],
    "greece-travel-packing-guide.html": ["Also visiting Spain?"],
    "singapore-travel-packing-guide-from-india.html": ["Also visiting Malaysia?"],
    "china-travel-packing-guide.html": ["Planning to explore more of Asia?"],
}


def die(msg):
    sys.exit("w62 aborted, nothing written: " + msg)


def text(h):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", h)).strip()


FIG = re.compile(r"[ \t]*<figure\b.*?</figure>[ \t]*\n?", re.S)
CALLOUT = re.compile(r'[ \t]*<p style="background:#f0faf7;border-left:3px solid #00C9A7[^>]*>.*?</p>[ \t]*\n?', re.S)


def find_fig(s, alt, cap):
    hits = []
    for m in FIG.finditer(s):
        a = re.search(r'alt="([^"]*)"', m.group(0))
        c = re.search(r"<figcaption[^>]*>(.*?)</figcaption>", m.group(0), re.S)
        if a and html.unescape(a.group(1)) == html.unescape(alt) and html.unescape(text(c.group(1) if c else "")) == html.unescape(cap):
            hits.append(m)
    return hits


def unesc(x):
    return (x.replace("&amp;", "&").replace("&#39;", "'").replace("&quot;", '"'))


pages = {}
for f in FIXES:
    pages.setdefault(f["page"], []).append(f)
for p in CALLOUTS:
    pages.setdefault(p, [])

plans, report = {}, []
for page, items in sorted(pages.items()):
    path = os.path.join(BLOG, page)
    if not os.path.isfile(path):
        die("missing " + page)
    s = open(path, encoding="utf-8").read()
    orig = s
    for it in items:
        hits = find_fig(s, it["alt"], it["cap"])
        if not hits:
            hits = find_fig(s, unesc(it["alt"]), unesc(it["cap"]))
        if it["action"] == "remove":
            if len(hits) > 1:
                die("%s: %d figures match %r" % (page, len(hits), it["alt"]))
            if hits:
                m = hits[0]
                s = s[:m.start()] + s[m.end():]
                report.append("removed  %s: %s" % (page, it["alt"]))
        elif it["action"] == "move":
            target = re.search(r"<h3[^>]*>\s*%s\s*</h3>\n?" % re.escape(it["to_h3"]), s)
            if not target:
                die("%s: target heading %r not found" % (page, it["to_h3"]))
            if not hits:
                continue
            fig = hits[0].group(0)
            if s[target.end():target.end() + len(fig) + 4].lstrip().startswith(fig.strip()[:60]):
                continue  # already right after the target
            s = s[:hits[0].start()] + s[hits[0].end():]
            target = re.search(r"<h3[^>]*>\s*%s\s*</h3>\n?" % re.escape(it["to_h3"]), s)
            s = s[:target.end()] + "\n" + fig.strip() + "\n" + s[target.end():]
            report.append("moved    %s: %s -> %s" % (page, it["alt"], it["to_h3"]))
    starts = CALLOUTS.get(page, [])
    if starts:
        faq = re.search(r"<h2[^>]*>\s*Frequently Asked Questions", s)
        if not faq:
            die(page + ": FAQ heading not found")
        moved = []
        for st in starts:
            ms = [m for m in CALLOUT.finditer(s) if text(m.group(0)).startswith(st)]
            if len(ms) != 1:
                if ms or st not in text(s):
                    die("%s: callout %r found %d times" % (page, st, len(ms)))
                continue
            m = ms[0]
            if m.start() > faq.start() - 2000 and s[m.end():faq.start()].count("<h2") == 0:
                continue  # already in the end spot
            moved.append(m.group(0).strip())
            s = s[:m.start()] + s[m.end():]
            faq = re.search(r"<h2[^>]*>\s*Frequently Asked Questions", s)
        if moved:
            s = s[:faq.start()] + "\n".join(moved) + "\n\n" + s[faq.start():]
            report.append("callouts %s: %d moved before the FAQ" % (page, len(moved)))
    if s != orig:
        plans[path] = s

for path, s in plans.items():
    open(path, "w", encoding="utf-8").write(s)
print("w62 done. %d page(s) changed, %d action(s)" % (len(plans), len(report)))
for r in report:
    print("  " + r)
