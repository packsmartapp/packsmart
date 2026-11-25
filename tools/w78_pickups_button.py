#!/usr/bin/env python3
"""
w78: the airport-transfer box's Continue button in our own button style, on every page that has the box (25 Nov 2026).

The transfer partner's booking form (it replaces its loader script with a div#powered_by_<promo>_<n> inside
.ps-pickups) draws its Continue button in a pale mint that reads as disabled. This restyles it like our own
"See dates and options" buttons: white, a 2px teal border, dark bold text, rounded corners, and teal with white text
on hover or keyboard focus. Only the look changes; the button, its label and what it does stay the partner's.

The owner first approved it on the 15 Japan pages (w77), then asked for every page with the box. The rule lives here
alone, as one <style id="ps-pickups-btn"> block in <head>, added to pages with a .ps-pickups box and removed from
pages that no longer have one.

Run after the page generators and w77, before w72:  python3 tools/w78_pickups_button.py
Idempotent: the block is replaced as a whole. Stops without writing if a page with the box has no single </head> line.
"""
import glob, os, re, sys

PUB = os.path.join(os.getcwd(), "public")
BTN = '.ps-pickups [id^="powered_by_"] button[type="submit"]'
CSS = ('<style id="ps-pickups-btn">\n'
       '/* the transfer partner\'s Continue button in our own outline button style (w78) */\n'
       + BTN + '{background:#fff!important;color:#0f0f23!important;font-weight:700!important;border:2px solid #00C9A7!important;'
       'border-radius:10px!important;box-shadow:none!important;transition:background .15s,color .15s}\n'
       + BTN + ' *{color:inherit!important}\n'
       + BTN + ':hover,' + BTN + ':focus-visible{background:#00C9A7!important;color:#fff!important}\n'
       '</style>\n')
BLOCK = re.compile(r'<style id="ps-pickups-btn">.*?</style>\n', re.S)

plans, problems, with_box = {}, [], 0
for path in sorted(glob.glob(os.path.join(PUB, "**", "*.html"), recursive=True)):
    s = open(path, encoding="utf-8").read()
    has_box = 'class="ps-pickups' in s
    new = BLOCK.sub("", s)
    if has_box:
        with_box += 1
        heads = list(re.finditer(r"(?m)^[ \t]*</head>", new))   # the real one sits on its own line
        if len(heads) != 1:
            problems.append(os.path.relpath(path, PUB))
            continue
        new = new[:heads[0].start()] + CSS + new[heads[0].start():]
    if new != s:
        plans[path] = new
if problems:
    sys.exit("w78 aborted, nothing written. No single </head> line in: " + ", ".join(problems))
for path, s in plans.items():
    open(path, "w", encoding="utf-8").write(s)
print("w78 done. Continue button styled on %d page(s) with the transfer box; %d file(s) changed." % (with_box, len(plans)))
