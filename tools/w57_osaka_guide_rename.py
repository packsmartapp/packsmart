#!/usr/bin/env python3
"""
w57: rename the "Osaka Station" Pocket Guide to "Shin-Osaka and Umeda" on pages that earlier scripts
already patched and will not rebuild (reviewer note, 21 Nov 2026: "Osaka Station" means JR Osaka at Umeda,
but the guide covers Shin-Osaka too).

The owners already carry the new name: w36 (the Osaka pocket page and article), w45 (cross-link cards),
tools/pocket_guides.json (w46 to w49 hub, article blocks and trip picker) and w37 (Travel Essentials strip).
Their blocks are marker-idempotent, so pages patched before this change keep the old name until this runs.

Run from the repo root, LAST (after w56):  python3 tools/w57_osaka_guide_rename.py
Idempotent: a page with none of the old strings is left alone. Fails loudly if an old string is still
left anywhere under public/ after the run (a new place the name appears that this script does not know).
"""
import os, sys, glob

ROOT = os.getcwd()
PUB = os.path.join(ROOT, "public")
if not os.path.isdir(PUB):
    sys.exit("Run from the repo root.")

OLD, NEW = "Osaka Station", "Shin-Osaka and Umeda"
PAIRS = [
    ("&quot;n&quot;:&quot;%s&quot;" % OLD, "&quot;n&quot;:&quot;%s&quot;" % NEW),   # w48/w49 data-guides JSON
    ("<b>%s</b>" % OLD, "<b>%s</b>" % NEW),                                          # w45 lists, w48/w49 tiles
    ("<b>%s Pocket Guide</b>" % OLD, "<b>%s Pocket Guide</b>" % NEW),                # w45 next-guide cards
    ("Open the %s pocket guide" % OLD, "Open the %s pocket guide" % NEW),            # w48/w49 aria-label
    ("<b>%s Pocket Guide Inside</b>" % OLD, "<b>%s Pocket Guide Inside</b>" % NEW),  # w37 Travel Essentials
    ("%s Pocket Guide" % OLD, "%s Pocket Guide" % NEW),                              # anything else
]

files = sorted(glob.glob(os.path.join(PUB, "**", "*.html"), recursive=True)
               + glob.glob(os.path.join(PUB, "*.webmanifest")) + glob.glob(os.path.join(PUB, "*-sw.js")))
changed = []
for path in files:
    s = open(path, encoding="utf-8").read()
    t = s
    for old, new in PAIRS:
        t = t.replace(old, new)
    if t != s:
        open(path, "w", encoding="utf-8").write(t)
        changed.append(os.path.relpath(path, ROOT))

# Anything left that still names the guide the old way?
left = []
for path in files:
    s = open(path, encoding="utf-8").read()
    for old, _ in PAIRS:
        if old in s:
            left.append("%s: %s" % (os.path.relpath(path, ROOT), old))
if left:
    sys.exit("w57: old name still present:\n  " + "\n  ".join(left))

print("w57 done. changed %d file(s)%s" % (len(changed), "".join("\n  - " + c for c in changed)))
