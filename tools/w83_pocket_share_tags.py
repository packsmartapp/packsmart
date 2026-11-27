#!/usr/bin/env python3
"""
w83: share tags (Open Graph and Twitter) on every Pocket Guide (27 Nov 2026, a tester: /sapporo-pocket had none).

Pocket Guides are shared on WhatsApp by design, but had no og: tags, so a shared link showed no title, text or picture.
This adds og:title, og:description, og:url, og:image (the guide's own 512px home-screen icon, from its web manifest),
og:site_name, and a Twitter "summary" card, right after the page's description. The guides stay noindex (they point
search engines to their full blog guides); share tags do not change that.

Idempotent (skips a page that already has og:title). Aborts without writing if a page lacks a title, description or
a 512px icon in its manifest. Run after the Pocket Guide generators and w44-w49, before w72:
    python3 tools/w83_pocket_share_tags.py
"""
import glob, html, json, os, re, sys

PUB = os.path.join(os.getcwd(), "public")
SITE = "https://www.packsmartapp.com"
plans = {}
for path in sorted(glob.glob(os.path.join(PUB, "*-pocket.html"))):
    s = open(path, encoding="utf-8").read()
    if 'property="og:title"' in s:
        continue
    key = os.path.basename(path)[:-len("-pocket.html")]
    t = re.search(r"<title>(.*?)</title>", s, re.S)
    d = re.search(r'(<meta name="description" content="([^"]*)">)\n', s)
    man = os.path.join(PUB, key + "-pocket.webmanifest")
    if not t or not d or not os.path.exists(man):
        sys.exit("w83 aborted, nothing written: title, description or manifest missing for " + key)
    icons = [i["src"] for i in json.load(open(man, encoding="utf-8")).get("icons", [])
             if i.get("sizes") == "512x512" and i.get("purpose", "any") == "any"]
    if not icons:
        sys.exit("w83 aborted, nothing written: no 512px icon in " + key + "-pocket.webmanifest")
    title = html.unescape(t.group(1)).replace(" | PackSmart", "").strip()
    desc = html.unescape(d.group(2))
    e = lambda x: html.escape(x, quote=True)
    tags = (
        '<meta property="og:type" content="website">\n'
        f'<meta property="og:site_name" content="PackSmart">\n'
        f'<meta property="og:title" content="{e(title)}: no app, works offline">\n'
        f'<meta property="og:description" content="{e(desc)}">\n'
        f'<meta property="og:url" content="{SITE}/{key}-pocket">\n'
        f'<meta property="og:image" content="{SITE}{icons[0]}">\n'
        '<meta property="og:image:width" content="512">\n<meta property="og:image:height" content="512">\n'
        '<meta name="twitter:card" content="summary">\n'
        f'<meta name="twitter:title" content="{e(title)}: no app, works offline">\n'
        f'<meta name="twitter:description" content="{e(desc)}">\n'
        f'<meta name="twitter:image" content="{SITE}{icons[0]}">\n'
    )
    plans[path] = s.replace(d.group(1) + "\n", d.group(1) + "\n" + tags, 1)

for path, new in plans.items():
    open(path, "w", encoding="utf-8").write(new)
print("w83 done. Share tags added to %d Pocket Guide(s)." % len(plans))
