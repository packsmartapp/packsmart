#!/usr/bin/env python3
"""w32: add the Sakura Mobile travel SIM + pocket Wi-Fi block to the 3 Japan articles.

Run from the repo root:  python3 tools/w32_japan_sakura_block.py
Optional: pass a directory that holds the three html files (dry runs).
Idempotent: skips a page that already has the marker.
"""
import sys, os, re

BASE = sys.argv[1] if len(sys.argv) > 1 else "public/blog"
MARK = "<!-- sakura-japan -->"
LINK = "https://p.sakuramobile.jp/idevaffiliate.php?id=728"
SIM_LINK = LINK  # TODO: swap for a link to Sakura's travel SIM page if the programme gives one (this one opens Sakura's home page)


def tile(pid, link, pill, img, w, h, alt, name, sub, price, note, label):
    return (
        f'<a class="ps-sk-tile" data-ps-placement="{pid}" href="{link}" target="_blank" rel="sponsored nofollow noopener" style="position:relative;display:flex;flex-direction:column;background:#fff;border:1.5px solid #cdeee5;border-radius:12px;padding:22px 16px 16px;text-decoration:none;text-align:center;color:#0f0f23;">'
        f'<span style="position:absolute;top:-10px;left:50%;transform:translateX(-50%);background:#00C9A7;color:#fff;font-size:0.68rem;font-weight:700;letter-spacing:.03em;padding:2px 10px;border-radius:999px;white-space:nowrap;">{pill}</span>'
        f'<span style="display:block;max-width:340px;width:100%;margin:0 auto 12px;"><picture><source type="image/webp" srcset="/images/{img}.webp">'
        f'<img src="/images/{img}.png" width="{w}" height="{h}" loading="lazy" alt="{alt}" style="display:block;width:100%;height:auto;border-radius:12px;"></picture></span>'
        f'<span style="display:block;font-size:1.5rem;font-weight:700;line-height:1.15;">{name}</span>'
        f'<span style="display:block;font-size:0.85rem;color:#666;line-height:1.35;margin:4px 0 10px;">{sub}</span>'
        f'<span style="display:block;font-size:1.05rem;font-weight:700;color:#0a8f78;">{price}</span>'
        f'<span style="display:block;font-size:0.78rem;color:#777;line-height:1.3;margin:6px 0 10px;">{note}</span>'
        f'<span style="flex:1;min-height:2px;display:block;"></span>'
        f'<span class="ps-sk-ghost" style="display:block;box-sizing:border-box;border:1.5px solid #00C9A7;color:#0a8f78;font-weight:700;font-size:1rem;border-radius:12px;padding:10px 14px;margin-top:6px;">{label} &rarr;</span>'
        f'<span style="display:block;font-size:0.76rem;color:#777;margin-top:6px;">Sakura Mobile &middot; partner link</span></a>'
    )


FOOT_PICK = (
    '<p style="margin:0 0 8px;font-size:0.82rem;color:#666;line-height:1.5;"><strong style="color:#0a8f78;">Pick up:</strong> '
    'the travel SIM is available at Sakura Mobile counters at Narita, Haneda, Kansai and Fukuoka airports, and the pocket Wi-Fi also at New Chitose and Chubu Centrair. '
    'Both can be sent to your hotel, and the pocket Wi-Fi to a post office. The SIM needs no return: throw it away after your trip. '
    'Post the pocket Wi-Fi back in the envelope that comes with it. A fair use policy may apply to unlimited data.</p>'
)


def block(suffix):
    sim = tile("sakura-japan-sim" + suffix, SIM_LINK, "FOR ONE TRAVELLER", "sakura-sim-banner", 380, 364,
               "Sakura Mobile Japan travel SIM card", "Travel SIM card", "Data only, no phone number",
               "From &yen;3,500 before tax", "3 GB a day on docomo, or unlimited on au", "Get a travel SIM")
    wifi = tile("sakura-japan-wifi" + suffix, LINK, "FOR FAMILIES AND GROUPS", "sakura-wifi-banner", 570, 546,
                "Sakura Mobile pocket Wi-Fi device", "Pocket Wi-Fi", "One device for every phone",
                "The price depends on your dates", "Docomo network, data described as unlimited", "Rent a pocket Wi-Fi")
    return (
        MARK + "\n"
        '<div style="max-width:800px;margin:24px auto;padding:22px 24px;background:#f0faf7;border:1px solid #cdeee5;border-left:4px solid #00C9A7;border-radius:12px;">\n'
        '  <style>.ps-sk-tile{transition:border-color .15s,box-shadow .15s}.ps-sk-tile:hover,.ps-sk-tile:focus-visible{border-color:#00C9A7!important;box-shadow:0 2px 10px rgba(0,201,167,.25)}.ps-sk-ghost{transition:background .15s}.ps-sk-tile:hover .ps-sk-ghost,.ps-sk-tile:focus-visible .ps-sk-ghost{background:#E7FAF5}</style>\n'
        '  <strong style="display:block;font-size:1.1rem;color:#0f0f23;margin:0 0 6px 0;">No eSIM? Two other ways to get online</strong>\n'
        '  <p style="margin:0 0 18px 0;font-size:0.9rem;color:#555;line-height:1.5;">An eSIM needs a compatible phone. If yours is not, or you would rather hold something real, choose a travel SIM card or a pocket Wi-Fi. Both are from Sakura Mobile.</p>\n'
        '  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:18px 12px;margin:14px 0 16px 0;">\n'
        f'  {sim}\n  {wifi}\n  </div>\n'
        f'  {FOOT_PICK}\n'
        '  <p style="margin:0;font-size:0.82rem;color:#666;line-height:1.5;">Order ahead: same-day orders are possible, but stock is limited.</p>\n'
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
        # already has the block: refresh it in place (wording, banners) so re-running always brings it up to date
        pat = re.compile(re.escape(MARK) + r".*?Order ahead: same-day orders are possible, but stock is limited\.</p>\n</div>\n", re.S)
        ms = list(pat.finditer(s))
        assert len(ms) == 1, (name, "block count", len(ms))
        fresh = block(cfg["suffix"])
        if ms[0].group(0) == fresh:
            print("up to date:", name)
        else:
            s = s[:ms[0].start()] + fresh + s[ms[0].end():]
            open(path, "w", encoding="utf-8").write(s)
            print("refreshed:", name)
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
