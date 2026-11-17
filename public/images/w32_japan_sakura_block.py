#!/usr/bin/env python3
"""w32: add the Sakura Mobile travel SIM + pocket Wi-Fi block to the 3 Japan articles.

Run from the repo root:  python3 public/images/w32_japan_sakura_block.py
Optional: pass a directory that holds the three html files (dry runs).
Idempotent: skips a page that already has the marker.
"""
import sys, os, re

BASE = sys.argv[1] if len(sys.argv) > 1 else "public/blog"
MARK = "<!-- sakura-japan -->"
LINK = "https://p.sakuramobile.jp/idevaffiliate.php?id=728"
SIM_LINK = LINK  # TODO: swap for a link to Sakura's travel SIM page if the programme gives one (this one opens Sakura's home page)

LBL = 'display:block;font-weight:700;color:#0a8f78;font-size:0.78rem;letter-spacing:.03em;text-transform:uppercase;'
VAL = 'display:block;font-size:0.93rem;line-height:1.4;color:#0f0f23;'


def row(label, text):
    return f'<div style="margin:0 0 8px;"><span style="{LBL}">{label}</span><span style="{VAL}">{text}</span></div>'


def card(pid, tag, title, desc, rows, btn, link):
    body = "".join(row(a, b) for a, b in rows)
    return (
        f'<div data-ps-placement="{pid}" style="display:flex;flex-direction:column;background:#fff;border:1.5px solid #cdeee5;border-radius:12px;padding:16px 16px 14px;">'
        f'<span style="align-self:flex-start;background:#E7FAF5;color:#0a8f78;font-size:0.72rem;font-weight:700;letter-spacing:.03em;padding:3px 10px;border-radius:999px;margin:0 0 8px;">{tag}</span>'
        f'<strong style="display:block;font-size:1.15rem;color:#0f0f23;margin:0 0 4px;">{title}</strong>'
        f'<p style="margin:0 0 12px;font-size:0.93rem;line-height:1.45;color:#333;">{desc}</p>'
        f'{body}'
        f'<span style="flex:1;min-height:8px;display:block;"></span>'
        f'<a class="ps-sk-btn" href="{link}" target="_blank" rel="sponsored nofollow noopener" style="display:block;box-sizing:border-box;background:#00C9A7;color:#0f0f23;text-align:center;text-decoration:none;border-radius:12px;padding:11px 14px;min-height:48px;line-height:1.25;">'
        f'<span style="display:block;font-weight:800;font-size:1.05rem;">{btn}</span>'
        f'<span style="display:block;font-weight:600;font-size:0.82rem;opacity:0.8;margin-top:2px;">Sakura Mobile &middot; partner link</span></a></div>'
    )


def block(suffix):
    sim = card(
        "sakura-japan-sim" + suffix, "FOR ONE TRAVELLER", "Travel SIM card",
        "A small SIM card you put in your phone. Data only, with no phone number.",
        [
            ("Price", "From &yen;3,500 before tax. The price depends on how many days you choose."),
            ("Data", "Sakura offers 3 GB a day on docomo, or unlimited data on au (a fair use policy may apply)."),
            ("Pick up", "At a Sakura Mobile counter at Narita, Haneda, Kansai or Fukuoka airport, or have it sent to your hotel. Nothing to return: throw the SIM away after your trip."),
        ],
        "Get a travel SIM", SIM_LINK)
    wifi = card(
        "sakura-japan-wifi" + suffix, "FOR FAMILIES AND GROUPS", "Pocket Wi-Fi",
        "One small device connects every phone, and it works with any phone. When your trip ends, post it back in the envelope that comes with it.",
        [
            ("Price", "The price depends on your dates. Sakura shows the total once you choose them. It runs on the docomo network, and Sakura describes the data as unlimited, so check the plan terms when you book."),
            ("Pick up", "At a Sakura Mobile counter at Narita, Haneda, Kansai, Fukuoka, New Chitose or Chubu Centrair airport, or have it sent to your hotel or a post office."),
        ],
        "Rent a pocket Wi-Fi", LINK)
    return (
        MARK + "\n"
        '<div style="max-width:800px;margin:24px auto;padding:22px 24px;background:#f0faf7;border:1px solid #cdeee5;border-left:4px solid #00C9A7;border-radius:12px;">\n'
        '  <style>.ps-sk-btn{transition:background .15s,box-shadow .15s}.ps-sk-btn:hover,.ps-sk-btn:focus-visible{background:#00B396!important;box-shadow:0 4px 14px rgba(0,201,167,.35)}</style>\n'
        '  <strong style="display:block;font-size:1.1rem;color:#0f0f23;margin:0 0 6px 0;">No eSIM? Two other ways to get online</strong>\n'
        '  <p style="margin:0 0 16px 0;font-size:0.95rem;color:#333;line-height:1.5;">An eSIM needs a compatible phone. If yours is not, or you would rather hold something real, choose a travel SIM card or a pocket Wi-Fi. Both are from Sakura Mobile.</p>\n'
        '  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:12px;margin:0 0 12px 0;">\n'
        f'  {sim}\n  {wifi}\n  </div>\n'
        '  <p style="margin:0;font-size:0.85rem;color:#666;line-height:1.5;">Order ahead: same-day orders are possible, but stock is limited.</p>\n'
        '</div>\n'
    )


PAGES = {
    "japan-travel-packing-guide.html": {
        "suffix": "",
        "after": None,
        "edits": [],
    },
    "japan-travel-packing-guide-from-india.html": {
        "suffix": "-india",
        "after": None,
        "edits": [(
            "<li>Pocket WiFi rental: &#xA5;1,000-1,500/day from Narita/Kansai airport rental counters (counter locations at Narita are in our <a href=\"/blog/narita-airport-guide\">Narita Airport guide</a>)</li>",
            "<li>Pocket WiFi rental: priced by the day, so the total depends on your dates. You can collect it at the airport (counter locations at Narita are in our <a href=\"/blog/narita-airport-guide\">Narita Airport guide</a>)</li>",
        )],
    },
    "japan-7-day-itinerary-budget.html": {
        "suffix": "-itinerary",
        "after": None,
        "edits": [
            (
                "<p>Japan has excellent 4G/5G coverage, but pocket Wi-Fi rentals are overpriced ($8&ndash;12/day). An eSIM is cheaper and more convenient &mdash; activate it before you land and you have data the moment you clear immigration.</p>",
                "<p>Japan has excellent 4G/5G coverage. An eSIM is usually the easiest way to get online &mdash; activate it before you land and you have data the moment you clear immigration.</p>",
            ),
            (
                "<li><strong>Skip the pocket Wi-Fi.</strong> An eSIM is cheaper, easier, and you do not have to carry (or return) a device.</li>",
                "<li><strong>Start with an eSIM.</strong> It is easy, and you do not have to carry (or return) a device. If your phone cannot use one, a travel SIM or pocket Wi-Fi works too.</li>",
            ),
        ],
    },
}

AFTER_RE = re.compile(r"Airalo asks you to verify your ID before you buy\.</p>\s*</div>[ \t]*\n")
MAP_ANCHOR = "        'airalo.tpx.li': 'Airalo',\n"
MAP_NEW = MAP_ANCHOR + "        'p.sakuramobile.jp': 'Sakura_Mobile',\n"

for name, cfg in PAGES.items():
    path = os.path.join(BASE, name)
    s = open(path, encoding="utf-8").read()
    if MARK in s:
        print("skip (already done):", name)
        continue
    # 1. insert block after the Airalo block (exactly one place)
    ms = list(AFTER_RE.finditer(s))
    assert len(ms) == 1, (name, "anchor count", len(ms))
    m = ms[0]
    s = s[:m.end()] + block(cfg["suffix"]) + s[m.end():]
    # 2. wording edits
    for old, new in cfg["edits"]:
        assert s.count(old) == 1, (name, "edit count", s.count(old), old[:60])
        s = s.replace(old, new)
    # 3. GA4 click-name map
    assert s.count(MAP_ANCHOR) == 1, (name, "map anchor", s.count(MAP_ANCHOR))
    s = s.replace(MAP_ANCHOR, MAP_NEW)
    open(path, "w", encoding="utf-8").write(s)
    print("updated:", name)
