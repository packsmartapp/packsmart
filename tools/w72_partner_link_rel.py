#!/usr/bin/env python3
"""
w72: partner links tell the partner where the click came from (24 Nov 2026, D54).

Why: the SafetyWing box's two main buttons (all articles) and the Airalo eSIM tiles carried rel="noopener noreferrer
sponsored". "noreferrer" stops the browser from sending packsmartapp.com as the referrer, so the partner sees the click
as coming from nowhere (SafetyWing's review on 24 Nov 2026 found buyers "not coming through the website"). It does
not affect commission (that comes from the ID in the link), and "noopener" already covers the security side.

What it does, on every public/**/*.html (articles, Pocket Guides and their JS strings):
  1. For each <a> whose href goes to a partner host (same host list as w67), removes "noreferrer" from rel and makes
     sure rel has "nofollow", "noopener" and "sponsored" (CLAUDE.md: rel="nofollow noopener sponsored"). Adds the rel
     attribute if a partner link has none.
  2. CHECK: fails if any partner link still has "noreferrer" or lacks "sponsored".
Links to official sources (JR, airports, Seven Bank ...) are not partner links and are left alone.

Run it last in the chain (after w69), and after adding any partner block:  python3 tools/w72_partner_link_rel.py
Idempotent: a second run changes nothing.
"""
import glob, os, re, sys

ROOT = os.getcwd()
PUB = os.path.join(ROOT, "public")
# keep in step with PARTNER_HOSTS in tools/w67_disclosure_partners.py
PARTNER_HOSTS = re.compile(r"tpx\.li|tpo\.lu|tp\.media|safetywing|getyourguide|klook|welcomepickups|discovercars|airalo|yesim|"
                           r"tiqets|radicalstorage|sakuramobile|bullettrain|trip\.com|12go|book\.packsmartapp|economybookings|"
                           r"kiwitaxi|saily|aviasales|kiwi\.com|tripadvisor")
A_TAG = re.compile(r"<a\b[^>]*>", re.I)
HREF = re.compile(r'\bhref="(https?://[^"/]+)')
REL = re.compile(r'\brel="([^"]*)"')
NEED = ["nofollow", "noopener", "sponsored"]


def fix(tag):
    m = HREF.search(tag)
    if not m or not PARTNER_HOSTS.search(m.group(1).lower()):
        return tag
    r = REL.search(tag)
    if r:
        toks = [t for t in r.group(1).split() if t.lower() != "noreferrer"]
        for t in NEED:
            if t not in toks:
                toks.append(t)
        return tag[:r.start()] + 'rel="%s"' % " ".join(toks) + tag[r.end():]
    return tag[:2] + ' rel="nofollow noopener sponsored"' + tag[2:]


changed, n_links = {}, 0
for f in sorted(glob.glob(os.path.join(PUB, "**", "*.html"), recursive=True)):
    s = open(f, encoding="utf-8").read()
    new = A_TAG.sub(lambda m: fix(m.group(0)), s)
    if new != s:
        changed[f] = new

for f, s in changed.items():
    open(f, "w", encoding="utf-8").write(s)

bad = []
for f in sorted(glob.glob(os.path.join(PUB, "**", "*.html"), recursive=True)):
    for tag in A_TAG.findall(open(f, encoding="utf-8").read()):
        m = HREF.search(tag)
        if not m or not PARTNER_HOSTS.search(m.group(1).lower()):
            continue
        n_links += 1
        r = REL.search(tag)
        toks = r.group(1).split() if r else []
        if "noreferrer" in toks or "sponsored" not in toks:
            bad.append("%s: %s" % (os.path.relpath(f, ROOT), tag[:120]))
print("w72 done. %d page(s) changed; %d partner links checked." % (len(changed), n_links))
if bad:
    sys.exit("w72 CHECK FAILED: partner links with noreferrer or without sponsored:\n  " + "\n  ".join(bad[:20]))
print("w72 check: every partner link sends the referrer and is labelled sponsored.")
