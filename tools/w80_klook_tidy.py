#!/usr/bin/env python3
"""
w80: tidy the "tours and tickets" tile boxes (class ps-kd, Klook partner links) (26 Nov 2026).

The owner found the boxes looked unfinished: each tile had a large pastel block with one emoji where a photo would
be (Klook's own photos may not be used: CLAUDE.md, "Never scrape Klook photos"), and one gradient was purple (not a
brand colour). Five boxes on one page also added clutter, and CLAUDE.md says to avoid Klook placements.

This script, for the pages in PAGES:
  * removes the boxes listed in TRIM (a whole <div ... data-ps-placement="..."> with its nested divs);
  * adds one <style id="ps-kd-v2"> block to <head> that turns each tile into a compact card: a small rounded icon
    square on the left (the same emoji, at icon size), the badge, name, details and price on the right; the purple
    gradient becomes the brand pink. Phones get the same card, one per row.

Preview first on the Japan travel guide (owner, 26 Nov); add more pages to PAGES once approved.
Run after w79 and before w76 and w72:  python3 tools/w80_klook_tidy.py
Idempotent: a removed box stays removed, and the style block is replaced as a whole. Stops without writing if a page
is missing or has no </head> line.
"""
import os, re, sys

ROOT = os.getcwd()
BLOG = os.path.join(ROOT, "public", "blog")
PAGES = ["japan-travel-packing-guide"]
TRIM = {  # page: placements to remove
    "japan-travel-packing-guide": ["klook-deals-japan-winter", "klook-japan-osaka", "klook-japan-fuji-car"],
}
CSS = """<style id="ps-kd-v2">
/* w80: compact tour and ticket cards, no empty picture block */
.ps-kd-img .ps-kd-t{display:grid!important;grid-template-columns:52px minmax(0,1fr);grid-auto-rows:auto;column-gap:14px;row-gap:3px;align-content:start;padding:16px 18px!important}
.ps-kd-img .ps-kd-ph{grid-column:1;grid-row:1/span 4;width:52px;height:52px;aspect-ratio:auto!important;border-radius:14px;font-size:1.6rem!important;margin:0!important;align-self:start}
.ps-kd-img .ps-kd-b{position:static!important;grid-column:2;justify-self:start;margin:0 0 2px!important}
.ps-kd-img .ps-kd-n,.ps-kd-img .ps-kd-m,.ps-kd-img .ps-kd-p{grid-column:2;margin-left:0!important;margin-right:0!important}
.ps-kd-img .g5{background:linear-gradient(135deg,#fde4f0,#f6bcd9)!important}
@media (min-width:700px){.ps-kd-img .ps-kd-t{flex:1 1 300px!important;max-width:420px!important}}
</style>
"""
STYLE = re.compile(r'<style id="ps-kd-v2">.*?</style>\n', re.S)


def remove_box(s, placement):
    m = re.search(r'<div\b[^>]*data-ps-placement="%s"[^>]*>' % re.escape(placement), s)
    if not m:
        return s, False
    depth, end = 0, None
    for t in re.finditer(r"<div\b|</div>", s[m.start():]):
        depth += 1 if t.group(0) != "</div>" else -1
        if depth == 0:
            end = m.start() + t.end()
            break
    if end is None:
        sys.exit("w80 aborted: box %s has no closing </div>" % placement)
    nl = end + 1 if s[end:end + 1] == "\n" else end
    return s[:m.start()] + s[nl:], True


plans, problems, removed = {}, [], 0
for slug in PAGES:
    path = os.path.join(BLOG, slug + ".html")
    if not os.path.isfile(path):
        problems.append(slug + " (missing)")
        continue
    s = open(path, encoding="utf-8").read()
    new = s
    for pl in TRIM.get(slug, []):
        new, did = remove_box(new, pl)
        removed += did
    new = STYLE.sub("", new)
    heads = list(re.finditer(r"(?m)^[ \t]*</head>", new))
    if len(heads) != 1:
        problems.append(slug + " (</head>)")
        continue
    new = new[:heads[0].start()] + CSS + new[heads[0].start():]
    if new != s:
        plans[path] = new
if problems:
    sys.exit("w80 aborted, nothing written: " + ", ".join(problems))
for path, s in plans.items():
    open(path, "w", encoding="utf-8").write(s)
print("w80 done. Tour and ticket cards tidied on %d page(s); %d box(es) removed; %d file(s) changed."
      % (len(PAGES), removed, len(plans)))
