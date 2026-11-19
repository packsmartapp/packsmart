#!/usr/bin/env python3
"""w34: add the Shinkansen box (picture, route, partner button) to the three Japan articles.

Run from the repo root:  python3 tools/w34_japan_shinkansen_box.py
Optional: pass a directory that holds the three articles (dry runs).
In the itinerary the box goes under the Day 4 Shinkansen paragraph; in the two packing guides it goes straight after the existing Klook rail card.
Idempotent: refreshes the box if it is already there. Also adds Japan_Bullet_Train to each
page's GA4 click map.
"""
import sys, os, re

BASE = sys.argv[1] if len(sys.argv) > 1 else "public/blog"
PAGES = [
    ("japan-7-day-itinerary-budget.html", "itinerary"),
    ("japan-travel-packing-guide.html", "packing"),
    ("japan-travel-packing-guide-from-india.html", "packing-india"),
]
# itinerary: sits under the Day 4 "Shinkansen to Kyoto" paragraph; packing guides: straight after the Klook rail card
DAY4 = "<h4>&#128644; Morning: Shinkansen to Kyoto</h4>"
MARK = "<!-- jb-shinkansen-tokyo -->"
END = "<!-- /jb-shinkansen-tokyo -->"

JB_LINK = "https://www.japan-bullettrain.com/?via=packsmart"
JB_SHIN = '<svg style="display:block;width:100%;height:auto;" aria-hidden="true" focusable="false" viewBox="0 0 320 170" xmlns="http://www.w3.org/2000/svg"><rect width="320" height="170" fill="#E8F1FE"/><circle cx="64" cy="40" r="20" fill="#FFE3CC"/><path d="M120 120 L188 44 L204 60 L214 52 L282 120Z" fill="#b9cdf0"/><path d="M174 62 L188 44 L204 60 L196 64 L188 58 L181 66Z" fill="#fff"/><path d="M0 124 L60 96 L110 120 L150 104 L200 124Z" fill="#d3e0f7"/><g fill="#f7b9cf"><circle cx="262" cy="104" r="14"/><circle cx="276" cy="112" r="12"/><circle cx="250" cy="114" r="11"/></g><rect x="260" y="112" width="4" height="22" fill="#8b5a3c"/><rect y="132" width="320" height="38" fill="#d3e0f7"/><rect y="146" width="320" height="4" fill="#9db8e6"/><g><path d="M14 138 L14 110 C14 104 20 100 28 100 L214 100 C250 100 286 118 306 138 Z" fill="#fff" stroke="#0f0f23" stroke-width="2.5"/><path d="M14 124 L300 124 L304 130 L14 130Z" fill="#2563EB"/><g fill="#7fb4f5" stroke="#0f0f23" stroke-width="1.5"><rect x="34" y="106" width="20" height="11" rx="2"/><rect x="62" y="106" width="20" height="11" rx="2"/><rect x="90" y="106" width="20" height="11" rx="2"/><rect x="118" y="106" width="20" height="11" rx="2"/><rect x="146" y="106" width="20" height="11" rx="2"/><rect x="174" y="106" width="20" height="11" rx="2"/></g><path d="M214 101 C238 102 262 112 282 124 L214 124Z" fill="#0f0f23" opacity=".9"/><g fill="#0f0f23"><circle cx="60" cy="140" r="5"/><circle cx="104" cy="140" r="5"/><circle cx="200" cy="140" r="5"/><circle cx="244" cy="140" r="5"/></g></g><g stroke="#2563EB" stroke-width="3" stroke-linecap="round"><path d="M4 108h22"/><path d="M0 118h16"/><path d="M6 128h12"/></g></svg>'
JB_TRAIN = '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M5 16V8a5 5 0 0 1 5-5h4a5 5 0 0 1 5 5v8a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2z"/><path d="M5 11h14M9 15h.01M15 15h.01M8 18l-2 3M16 18l2 3"/></svg>'


def jb_node(text):
    return '<div class="jb-rn"><span class="jb-dot"></span><strong style="color:#0f0f23;font-size:1rem;">%s</strong></div>' % text


def jb_leg(text, icon="", blue=False):
    return '<div class="jb-lg%s"><span class="jb-ln"></span><span class="jb-lt">%s%s</span></div>' % (" jb-blue" if blue else "", icon, text)




def box(suffix):
    return (
        '<div data-ps-placement="jw-shinkansen-' + suffix + '" style="max-width:800px;margin:20px auto;padding:20px;background:#f0faf7;border:1px solid #cdeee5;border-left:4px solid #00C9A7;border-radius:12px;">'
        '<style>.ps-jb-ghost{transition:background .15s,box-shadow .15s}.ps-jb-btn:hover .ps-jb-ghost,.ps-jb-btn:focus-visible .ps-jb-ghost{background:#E7FAF5!important;box-shadow:0 2px 10px rgba(0,201,167,.25)}'
        '.jb-grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:22px;align-items:center;margin:0 0 16px}'
        '.jb-row{display:flex;gap:22px;align-items:flex-start}.jb-row .jb-tx{flex:1 1 0;min-width:0}.jb-row .jb-bt{flex:0 0 280px}'
        '@media(max-width:640px){.jb-grid{grid-template-columns:1fr;gap:14px}.jb-row{flex-direction:column;align-items:stretch;gap:12px}.jb-row .jb-bt{flex:none}}'
        '.jb-rn{display:flex;gap:10px;align-items:center;padding:2px 0}'
        '.jb-dot{width:14px;height:14px;border-radius:50%;background:#00C9A7;border:3px solid #fff;box-shadow:0 0 0 2px #00C9A7;flex:none;margin:0 2px}'
        '.jb-lg{display:flex;gap:14px;align-items:stretch;padding:3px 0 3px 8px}'
        '.jb-ln{width:4px;height:30px;border-radius:2px;flex:none;background:repeating-linear-gradient(180deg,#00C9A7 0 8px,transparent 8px 13px)}'
        '.jb-blue .jb-ln{background:repeating-linear-gradient(180deg,#2563EB 0 8px,transparent 8px 13px)}'
        '.jb-lt{display:flex;align-items:center;gap:6px;align-self:center;font-size:.85rem;font-weight:700;color:#0a8f78;line-height:1.25}'
        '.jb-blue .jb-lt{color:#2563EB}</style>'
        '<strong style="display:block;font-size:1.1rem;color:#0f0f23;margin:0 0 12px;">Going on to Kyoto or Osaka?</strong>'
        '<div class="jb-grid">'
        '<a href="' + JB_LINK + '" target="_blank" rel="nofollow noopener sponsored" tabindex="-1" aria-hidden="true" style="display:block;border-radius:12px;overflow:hidden;">' + JB_SHIN + '</a>'
        '<div>'
        + jb_node("Tokyo Station") + jb_leg("Shinkansen (bullet train), from about 2 hr 15 min", JB_TRAIN, True) + jb_node("Kyoto") + jb_node("Osaka") +
        '</div></div>'
        '<div class="jb-row"><div class="jb-tx">'
        '<p style="margin:0;font-size:0.95rem;line-height:1.5;color:#333;">' + ("" if suffix == "itinerary" else "The Shinkansen leaves from Tokyo Station. ") + 'If you want your tickets sorted before you travel, you can book them online. The company says its tickets cover the JR East, JR West, JR Central and JR Kyushu Shinkansen lines and are collected with a QR code.</p>'
        '</div><div class="jb-bt">'
        '<a class="ps-jb-btn" href="' + JB_LINK + '" target="_blank" rel="nofollow noopener sponsored" style="display:block;box-sizing:border-box;text-decoration:none;"><span class="ps-jb-ghost" style="display:block;border:1.5px solid #00C9A7;background:#fff;color:#0a8f78;text-align:center;font-weight:700;font-size:1rem;border-radius:12px;padding:11px 14px;min-height:46px;line-height:1.25;">Book Shinkansen tickets &rarr;</span><span style="display:block;text-align:center;font-size:0.76rem;color:#777;margin-top:6px;">Japan Bullet Train &middot; partner link</span></a>'
        '<p style="margin:10px 0 0;font-size:0.85rem;line-height:1.5;color:#555;">You can also buy at a station on the day, so check the price and the change and cancellation rules before you pay.</p>'
        '</div></div></div>'
    )


def klook_block_end(s):
    i = s.index('data-aid="japan-rail-shinkansen"')
    k = s.index("We may earn a commission", i)
    e = s.index("</div>", k)
    return e + len("</div>")


for page, suffix in PAGES:
    path = os.path.join(BASE, page)
    s = open(path, encoding="utf-8").read()
    new = MARK + "\n" + box(suffix) + "\n" + END
    if MARK in s:
        a = s.index(MARK)
        b = s.index(END) + len(END)
        s2 = s[:a] + new + s[b:]
    elif suffix == "itinerary":
        a = s.index(DAY4)
        e = s.index("</p>", a) + len("</p>")
        s2 = s[:e] + "\n" + new + s[e:]
    else:
        e = klook_block_end(s)
        s2 = s[:e] + "\n" + new + s[e:]
    if "'japan-bullettrain.com'" not in s2:
        if "'klook.tpx.li': 'Klook'," not in s2:
            raise SystemExit("click map anchor missing in " + page)
        s2 = s2.replace("'klook.tpx.li': 'Klook',", "'japan-bullettrain.com': 'Japan_Bullet_Train',\n        'klook.tpx.li': 'Klook',", 1)
    if page == "japan-travel-packing-guide.html":
        vis = re.sub(r"<script[^>]*>.*?</script>", "", new, flags=re.S)
        if re.search(r"\b(India|Indian|INR|rupee)\b", vis):
            raise SystemExit("neutral-rule violation in " + page)
    if s2 != s:
        open(path, "w", encoding="utf-8").write(s2)
        print("updated", page)
    else:
        print("unchanged", page)
