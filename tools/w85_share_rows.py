#!/usr/bin/env python3
"""
w85: a "Share this" row on the Japan hub and Travel Essentials (the Phrasebook has its own ❤️ button since 27 Nov) (27 Nov 2026, a tester: no social
sharing links on these pages; articles already have one).

Same buttons as the articles' share row (WhatsApp, X, Facebook, LinkedIn, Pinterest, copy link; the icons are taken
from the Japan travel guide's row so they always match), plus a "Share" button that opens the phone's own share sheet
where the browser has one (navigator.share). Every shared link carries ?src=share_<page> so GA4 shows which page is
shared; clicks send the GA4 event "share_row" with the network.

Idempotent (marker "ps-share-row"); on a page that already has the row, only its label and styles are brought up to date.
Label: "Made with ❤️ ..." (27 Nov 2026, owner: "hub" means nothing to readers). Aborts without writing if an anchor or the article icons are missing.
Run after w73 and w81, before w72:  python3 tools/w85_share_rows.py
"""
import html, os, re, sys, urllib.parse

PUB = os.path.join(os.getcwd(), "public")
SITE = "https://www.packsmartapp.com"
MARK = "ps-share-row"
PAGES = [  # file, page path, label, share text, anchor, insert before (True) or after
    ("japan.html", "/japan", "Made with ❤️. Know someone going to Japan? Send them this\u00a0page.", "Japan, the easy way: airports, stations, Packy and offline Pocket Guides",
     '<footer class="footer">', True),
    ("travel-essentials.html", "/travel-essentials", "Made with ❤️. Travelling with someone? Send them this so you're both\u00a0ready.", "Travel Essentials: Pocket Guides, visas, eSIMs and packing lists",
     '<section class="pocket-hub"', True),
]

guide = open(os.path.join(PUB, "blog", "japan-travel-packing-guide.html"), encoding="utf-8").read()
ICONS = {}
for net in ("whatsapp", "twitter", "facebook", "linkedin", "pinterest", "copy-link"):
    m = re.search(r'class="share-btn ' + net + r'".*?(<svg.*?</svg>)', guide, re.S)
    if not m:
        sys.exit("w85 aborted, nothing written: no %s icon in the Japan travel guide's share row" % net)
    ICONS[net] = m.group(1)

CSS = ('<style id="ps-share-css">.ps-share-row{display:flex;align-items:center;justify-content:center;gap:10px;flex-wrap:wrap;'
       'max-width:760px;margin:28px auto;padding:12px 16px;font-family:\'DM Sans\',sans-serif}'
       '.ps-share-row>span{font-size:1rem;line-height:1.5;color:#4a4f5c;font-weight:400;width:100%;text-align:center}.ps-share-row>span em{display:block;font-style:normal;font-size:.8rem;letter-spacing:.03em;color:#0a8f78;font-weight:600;margin-bottom:2px}'
       '.ps-share-row a,.ps-share-row button{display:inline-flex;align-items:center;justify-content:center;gap:5px;min-width:40px;height:40px;'
       'padding:0 10px;border-radius:10px;border:1px solid #E3E8EC;background:#fff;color:#555;text-decoration:none;font:inherit;'
       'font-size:.84rem;font-weight:600;cursor:pointer}'
       '.ps-share-row a:hover,.ps-share-row button:hover{border-color:#00C9A7;color:#0f0f23}'
       '.ps-share-row .ps-native{background:#00C9A7;border-color:#00C9A7;color:#fff;padding:0 16px}'
       '.ps-share-row .ps-native[hidden]{display:none}</style>')
JS = ('<script>(function(){var r=document.currentScript.previousElementSibling;if(!r)return;'
      'function t(n){try{if(window.gtag)gtag("event","share_row",{event_category:"engagement",network:n,page_path:location.pathname});}catch(e){}}'
      'var nb=r.querySelector(".ps-native");if(nb&&navigator.share){nb.hidden=false;nb.addEventListener("click",function(){'
      'navigator.share({title:document.title,text:r.getAttribute("data-text"),url:r.getAttribute("data-url")}).then(function(){t("native");}).catch(function(){});});}'
      'r.addEventListener("click",function(e){var a=e.target.closest("[data-net]");if(!a)return;var n=a.getAttribute("data-net");'
      'if(n==="copy"){e.preventDefault();var u=r.getAttribute("data-url");try{navigator.clipboard.writeText(u).then(function(){a.lastChild.textContent=" Copied!";});}catch(x){}}t(n);});})();</script>')

def lab(label):
    """'Made with ... . The question' -> a small teal 'Made with' line over the question in plain text."""
    kick, rest = label.split(". ", 1)
    return "<em>" + html.escape(kick, quote=True) + "</em>" + html.escape(rest, quote=True)

def row(path, label, text, key):
    url = SITE + path + "?src=share_" + key
    q = urllib.parse.quote
    e = lambda x: html.escape(x, quote=True)
    links = [
        ("whatsapp", "https://wa.me/?text=" + q(text + " " + url), "WhatsApp"),
        ("x", "https://twitter.com/intent/tweet?text=" + q(text) + "&url=" + q(url, safe=""), "X"),
        ("facebook", "https://www.facebook.com/sharer/sharer.php?u=" + q(url, safe=""), "Facebook"),
        ("linkedin", "https://www.linkedin.com/sharing/share-offsite/?url=" + q(url, safe=""), "LinkedIn"),
        ("pinterest", "https://pinterest.com/pin/create/button/?url=" + q(url, safe="") + "&media=" + q(SITE + "/og-default.png", safe="")
         + "&description=" + q(text), "Pinterest"),
    ]
    icon = {"whatsapp": "whatsapp", "x": "twitter", "facebook": "facebook", "linkedin": "linkedin", "pinterest": "pinterest"}
    out = ['<div class="' + MARK + ' ps-share-row" data-url="' + e(url) + '" data-text="' + e(text) + '"><span>' + lab(label) + '</span>',
           '<button type="button" class="ps-native" hidden>📤 Share</button>']
    for net, href, name in links:
        out.append('<a href="' + e(href) + '" target="_blank" rel="noopener" data-net="' + net + '" title="' + name + '" aria-label="Share on ' + name + '">' + ICONS[icon[net]] + '</a>')
    out.append('<a href="' + e(url) + '" data-net="copy" title="Copy link" aria-label="Copy link">' + ICONS["copy-link"] + ' Link</a></div>')
    return "".join(out) + JS + "\n"

plans = {}
for name, path, label, text, anchor, before in PAGES:
    f = os.path.join(PUB, name)
    s = open(f, encoding="utf-8").read()
    old = s
    if 'class="' + MARK in s:   # the row itself (the page generators can keep the <head>, so the styles alone do not count)
        # keep an existing row's label and styles current (travel-essentials.html is not regenerated, so its row stays)
        m = re.search(r'(<div class="' + MARK + r' ps-share-row"[^>]*><span>)(.*?)(</span>)', s)
        c = re.search(r'<style id="ps-share-css">.*?</style>', s, re.S)
        if not m or not c:
            sys.exit("w85 aborted, nothing written: share row in " + name + " has no label or no styles")
        s = s[:c.start()] + CSS + s[c.end():]
        m = re.search(r'(<div class="' + MARK + r' ps-share-row"[^>]*><span>)(.*?)(</span>)', s)
        s = s[:m.start(2)] + lab(label) + s[m.end(2):]
        if s != old:
            plans[f] = s
        continue
    if s.count(anchor) != 1 or s.count("</head>") != 1:
        sys.exit("w85 aborted, nothing written: anchor or </head> not found exactly once in " + name)
    key = path.strip("/").replace("-", "_").replace("japan_phrasebook", "phrasebook").replace("travel_essentials", "essentials")
    s = s.replace(anchor, row(path, label, text, key) + anchor, 1)
    c = re.search(r'<style id="ps-share-css">.*?</style>', s, re.S)
    s = s[:c.start()] + CSS + s[c.end():] if c else s.replace("</head>", CSS + "\n</head>", 1)
    plans[f] = s
for f, s in plans.items():
    open(f, "w", encoding="utf-8").write(s)
print("w85 done. Share row added or relabelled on %d page(s)." % len(plans))
