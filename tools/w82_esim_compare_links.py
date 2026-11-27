#!/usr/bin/env python3
"""
w82: a "Compare travel eSIMs" line in every eSIM block (27 Nov 2026, owner: readers could not find the eSIM comparison).

Every article's eSIM block (data-ps-placement="airalo-<country>") gets one line at its end:
    Not sure which eSIM? Compare travel eSIMs ->   (/blog/best-esim-international-travel-comparison?src=esim_block)
It is an internal link (not a partner link), at the moment the reader is choosing an eSIM, and it gives the comparison
page internal links from 40+ pages.

Idempotent (marker class "ps-esim-cmp-link"). Aborts without writing if a block's closing </div> cannot be found.
Run after the page generators and before w72:  python3 tools/w82_esim_compare_links.py
"""
import glob, os, re, sys

PUB = os.path.join(os.getcwd(), "public")
TARGET = "best-esim-international-travel-comparison"
LINE = ('<p class="ps-esim-cmp-link" style="margin:10px 0 0;font-size:0.88rem;line-height:1.4;">'
        '<a href="/blog/' + TARGET + '?src=esim_block" style="color:#0a8f78;font-weight:700;text-decoration:underline;">'
        'Not sure which eSIM? Compare travel eSIMs &rarr;</a></p>\n')
OPEN = re.compile(r'<div data-ps-placement="airalo-[a-z0-9-]+"[^>]*>')
TAG = re.compile(r'<(/?)div\b[^>]*>')

plans, added = {}, 0
for path in sorted(glob.glob(os.path.join(PUB, "**", "*.html"), recursive=True)):
    if TARGET in os.path.basename(path):
        continue
    s = open(path, encoding="utf-8").read()
    if 'data-ps-placement="airalo-' not in s:
        continue
    out, pos, changed = [], 0, False
    for m in OPEN.finditer(s):
        if m.start() < pos:
            continue
        depth, end = 0, None
        for t in TAG.finditer(s, m.start()):
            depth += -1 if t.group(1) else 1
            if depth == 0:
                end = t.start()
                break
        if end is None:
            sys.exit("w82 aborted, nothing written: no closing </div> for the eSIM block in " + os.path.relpath(path, PUB))
        block = s[m.start():end]
        out.append(s[pos:end])
        if "ps-esim-cmp-link" not in block:
            out.append(LINE)
            changed = True
            added += 1
        pos = end
    out.append(s[pos:])
    if changed:
        plans[path] = "".join(out)

for path, new in plans.items():
    open(path, "w", encoding="utf-8").write(new)
print("w82 done. %d eSIM block(s) linked to the comparison on %d page(s)." % (added, len(plans)))
