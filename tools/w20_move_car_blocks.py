#!/usr/bin/env python3
"""w20: move the car-rental block so it never sits directly after another widget.
Each block moves (unchanged, with its leading '<!-- DiscoverCars Car Rental Widget -->' comment when present) to sit directly
before a chosen heading inside the article, with copy on both sides and no widget touching it. Blocks that were outside the
article wrapper (Australia, Canada, Vietnam, Greece, Portugal) end up inside it, so they render inset like the USA page.
Run from repo root:  python3 tools/w20_move_car_blocks.py   (optional arg: blog dir)
Idempotent (skips a page whose block already sits directly before its anchor). Validates every page first and writes nothing if any check fails.
"""
import os, re, sys

BLOG = sys.argv[1] if len(sys.argv) > 1 else "public/blog"
PREDEP = r'<h2[^>]*>[^<]*Pre-Departure Checklist[^<]*</h2>'

PAGES = [
    dict(file="australia-travel-packing-guide-from-india.html", placement="discovercars-australia", anchor=PREDEP),
    dict(file="canada-travel-packing-guide-from-india.html", placement="economybookings-canada", anchor=PREDEP),
    dict(file="vietnam-travel-packing-guide-from-india.html", placement="economybookings-vietnam", anchor=PREDEP),
    dict(file="dubai-travel-packing-guide-from-india.html", placement="discovercars-dubai", anchor=PREDEP),
    dict(file="japan-travel-packing-guide-from-india.html", placement="discovercars-japan-guide-india", anchor=PREDEP),
    dict(file="greece-travel-packing-guide.html", placement="discovercars-greece", anchor=r'<h2 id="ferry-logistics">'),
    dict(file="portugal-travel-packing-guide.html", placement="discovercars-portugal", anchor=r'<h3>Walking &amp; Cycling</h3>|<h3>Walking & Cycling</h3>'),
    dict(file="japan-travel-packing-guide.html", placement="discovercars-japan-guide", anchor=r'<h2 id="jr-pass">'),
]

TOK = re.compile(r'<script\b.*?</script>|<style\b.*?</style>|<div\b|</div>', re.S | re.I)
COMMENT = "<!-- DiscoverCars Car Rental Widget -->"

def find_block(s, placement):
    """Return (start, end) of the block: from the line start of its leading comment (or of the div) to the end of its closing </div> line."""
    key = '<div data-ps-placement="%s"' % placement
    if s.count(key) != 1:
        raise ValueError("block count %d != 1" % s.count(key))
    d = s.index(key)
    start = s.rfind("\n", 0, d) + 1  # line start of the div
    head = s[:start].rstrip()
    if head.endswith(COMMENT):
        start = head.rfind(COMMENT)
        start = s.rfind("\n", 0, start) + 1
    depth = 0
    for m in TOK.finditer(s, d):
        t = m.group(0).lower()
        if t.startswith("<script") or t.startswith("<style"):
            continue
        depth += 1 if t == "<div" else -1
        if depth == 0:
            end = s.find("\n", m.end())
            end = len(s) if end == -1 else end + 1
            return start, end
    raise ValueError("unbalanced block")

def plan(p):
    path = os.path.join(BLOG, p["file"])
    s = open(path, encoding="utf-8").read()
    a = re.compile(p["anchor"])
    if len(a.findall(s)) != 1:
        raise ValueError("anchor matches %d != 1" % len(a.findall(s)))
    start, end = find_block(s, p["placement"])
    blk = s[start:end]
    am = a.search(s)
    anchor_line = s.rfind("\n", 0, am.start()) + 1
    if s[end:anchor_line].strip() == "" and end <= anchor_line:
        return path, s, None, "already in place"
    if start < am.start() < end:
        raise ValueError("anchor inside block")
    rest = s[:start] + s[end:]
    am2 = a.search(rest)
    al2 = rest.rfind("\n", 0, am2.start()) + 1
    new = rest[:al2] + blk.rstrip("\n") + "\n\n" + rest[al2:]
    # sanity: nothing lost or duplicated
    assert new.count('data-ps-placement="%s"' % p["placement"]) == s.count('data-ps-placement="%s"' % p["placement"])
    assert new.count("<div") == s.count("<div") and new.count("</div>") == s.count("</div>")
    assert new.count("<script") == s.count("<script")
    assert new.count(blk.rstrip("\n")) == 1
    return path, s, new, "move"

plans = []
for p in PAGES:
    path = os.path.join(BLOG, p["file"])
    if not os.path.exists(path):
        print("ABORT: %s not found" % path); sys.exit(1)
    try:
        plans.append((p, plan(p)))
    except Exception as e:
        print("ABORT %s: %s" % (p["file"], e)); sys.exit(1)

for p, (path, old, new, what) in plans:
    if new is None:
        print("SKIP %s: %s" % (p["file"], what)); continue
    open(path, "w", encoding="utf-8").write(new)
    print("OK %s: block moved before its anchor (%d -> %d bytes)" % (p["file"], len(old), len(new)))
