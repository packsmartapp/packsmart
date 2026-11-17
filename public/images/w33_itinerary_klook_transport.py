#!/usr/bin/env python3
"""w33: add the Klook Narita train/bus ticket cards to the Japan 7-day itinerary (Day 1 arrival).

Run from the repo root:  python3 public/images/w33_itinerary_klook_transport.py
Optional: pass a directory that holds japan-7-day-itinerary-budget.html (dry runs).
Idempotent: refreshes the block if it is already there.
"""
import sys, os, re

BASE = sys.argv[1] if len(sys.argv) > 1 else "public/blog"
PAGE = "japan-7-day-itinerary-budget.html"
MARK = "<!-- klook-japan-transport-itinerary -->"

KL_SKY = '<svg aria-hidden="true" focusable="false" style="display:block;width:100%;height:auto;" viewBox="0 0 320 150" xmlns="http://www.w3.org/2000/svg"><rect width="320" height="150" fill="#E7FAF5"/><circle cx="262" cy="38" r="20" fill="#FDE9C8"/><path d="M0 112 L40 86 L62 100 L96 70 L128 104 L160 112Z" fill="#cdeee5"/><path d="M150 112 L196 78 L226 98 L262 66 L320 112Z" fill="#bfe6dc"/><rect y="112" width="320" height="38" fill="#d6f1ea"/><rect y="124" width="320" height="4" fill="#9bd7c9"/><g><path d="M26 118 C26 96 40 86 62 86 L258 86 C276 86 292 100 298 118 Z" fill="#fff" stroke="#0f0f23" stroke-width="2.5"/><path d="M26 108 L298 108 L298 114 L26 114Z" fill="#00C9A7"/><g fill="#0f0f23"><path d="M262 92 C274 92 284 100 288 108 L262 108Z"/></g><g fill="#7fd9ea" stroke="#0f0f23" stroke-width="1.5"><rect x="70" y="93" width="26" height="12" rx="3"/><rect x="104" y="93" width="26" height="12" rx="3"/><rect x="138" y="93" width="26" height="12" rx="3"/><rect x="172" y="93" width="26" height="12" rx="3"/><rect x="206" y="93" width="26" height="12" rx="3"/></g><g fill="#0f0f23"><circle cx="70" cy="122" r="5"/><circle cx="110" cy="122" r="5"/><circle cx="214" cy="122" r="5"/><circle cx="254" cy="122" r="5"/></g></g><g stroke="#00C9A7" stroke-width="3" stroke-linecap="round"><path d="M6 96h22"/><path d="M2 106h18"/><path d="M8 116h14"/></g></svg>'
KL_NEX = '<svg aria-hidden="true" focusable="false" style="display:block;width:100%;height:auto;" viewBox="0 0 320 150" xmlns="http://www.w3.org/2000/svg"><rect width="320" height="150" fill="#FDECEC"/><g fill="#f6cfcf"><rect x="20" y="60" width="26" height="52"/><rect x="52" y="44" width="30" height="68"/><rect x="88" y="68" width="22" height="44"/><rect x="214" y="52" width="28" height="60"/><rect x="248" y="70" width="24" height="42"/><rect x="278" y="48" width="30" height="64"/></g><rect y="112" width="320" height="38" fill="#f3dcdc"/><rect y="124" width="320" height="4" fill="#e3b4b4"/><g><path d="M20 118 L20 92 C20 88 24 86 28 86 L252 86 C276 86 292 98 300 118 Z" fill="#fff" stroke="#0f0f23" stroke-width="2.5"/><path d="M20 106 L300 106 L300 112 L20 112Z" fill="#E5484D"/><g fill="#9ad8e8" stroke="#0f0f23" stroke-width="1.5"><rect x="34" y="93" width="22" height="11" rx="2"/><rect x="62" y="93" width="22" height="11" rx="2"/><rect x="90" y="93" width="22" height="11" rx="2"/><rect x="118" y="93" width="22" height="11" rx="2"/><rect x="146" y="93" width="22" height="11" rx="2"/><rect x="174" y="93" width="22" height="11" rx="2"/><rect x="202" y="93" width="22" height="11" rx="2"/></g><path d="M254 92 C270 92 284 100 290 106 L254 106Z" fill="#0f0f23"/><g fill="#0f0f23"><circle cx="60" cy="122" r="5"/><circle cx="100" cy="122" r="5"/><circle cx="210" cy="122" r="5"/><circle cx="250" cy="122" r="5"/></g></g></svg>'
KL_BUS = '<svg aria-hidden="true" focusable="false" style="display:block;width:100%;height:auto;" viewBox="0 0 320 150" xmlns="http://www.w3.org/2000/svg"><rect width="320" height="150" fill="#FFF1E2"/><g fill="#fbd9b6"><rect x="14" y="40" width="40" height="74"/><rect x="60" y="62" width="28" height="52"/><rect x="236" y="34" width="44" height="80"/><rect x="284" y="64" width="26" height="50"/></g><g fill="#fff3e6"><rect x="22" y="50" width="8" height="8"/><rect x="38" y="50" width="8" height="8"/><rect x="22" y="66" width="8" height="8"/><rect x="38" y="66" width="8" height="8"/><rect x="246" y="46" width="8" height="8"/><rect x="262" y="46" width="8" height="8"/><rect x="246" y="62" width="8" height="8"/><rect x="262" y="62" width="8" height="8"/></g><rect y="116" width="320" height="34" fill="#efd3b3"/><rect y="132" width="320" height="3" fill="#fff" opacity=".6"/><g><rect x="52" y="64" width="216" height="56" rx="10" fill="#fff" stroke="#0f0f23" stroke-width="2.5"/><rect x="52" y="104" width="216" height="8" fill="#F97316"/><g fill="#9ad8e8" stroke="#0f0f23" stroke-width="1.5"><rect x="64" y="72" width="26" height="22" rx="3"/><rect x="96" y="72" width="26" height="22" rx="3"/><rect x="128" y="72" width="26" height="22" rx="3"/><rect x="160" y="72" width="26" height="22" rx="3"/><rect x="192" y="72" width="26" height="22" rx="3"/><rect x="228" y="72" width="30" height="30" rx="3"/></g><circle cx="94" cy="122" r="11" fill="#0f0f23"/><circle cx="94" cy="122" r="4" fill="#bbb"/><circle cx="226" cy="122" r="11" fill="#0f0f23"/><circle cx="226" cy="122" r="4" fill="#bbb"/></g></svg>'
KL_LBL = "display:block;font-weight:700;color:#0a8f78;font-size:0.76rem;letter-spacing:.03em;text-transform:uppercase;"
KL_VAL = "display:block;font-size:0.92rem;line-height:1.35;color:#0f0f23;"
KL_ROWS = [
    ("skyliner", "Keisei Skyliner", "Ueno, Nippori", "40 to 45 min", "&yen;2,500 to &yen;2,600", "Fastest train. Seats are reserved.", "https://klook.tpx.li/gIYih1CY", "See Skyliner tickets", KL_SKY),
    ("nex", "JR Narita Express (N'EX)", "Tokyo Station, Shinjuku, Shibuya, Yokohama", "About 1 hour to Tokyo Station", "&yen;3,100 to &yen;3,300", "Direct, with luggage racks. Seats are reserved.", "https://klook.tpx.li/tX4jclRv", "See N'EX tickets", KL_NEX),
    ("limousine", "Airport Limousine Bus", "Major hotels, Tokyo Disney Resort", "75 to 90 min", "&yen;3,200 or more", "Hotel-direct; easy with heavy luggage.", "https://klook.tpx.li/SISnlOYP", "See Limousine tickets", KL_BUS),
]


def kl_row(label, text):
    return '<div style="margin:0 0 7px;"><span style="%s">%s</span><span style="%s">%s</span></div>' % (KL_LBL, label, KL_VAL, text)


def kl_tile(r):
    pid, name, to, mins, price, note, link, btn, svg = r
    return (
        '<div data-ps-placement="klook-japan-transport-itinerary-%s" style="display:flex;flex-direction:column;background:#fff;border:1.5px solid #cdeee5;border-radius:12px;padding:12px 12px 14px;">' % pid
        + '<a href="%s" target="_blank" rel="nofollow noopener sponsored" tabindex="-1" aria-hidden="true" style="display:block;margin:0 0 10px;border-radius:12px;overflow:hidden;">%s</a>' % (link, svg)
        + '<strong style="display:block;font-size:1.1rem;color:#0f0f23;margin:0 0 8px;">%s</strong>' % name
        + kl_row("Goes to", to) + kl_row("About how long", mins) + kl_row("About how much", price)
        + '<p style="margin:0 0 12px;font-size:0.88rem;color:#555;line-height:1.4;">%s</p><span style="flex:1;min-height:4px;display:block;"></span>' % note
        + '<a class="ps-kl-btn" href="%s" target="_blank" rel="nofollow noopener sponsored" style="display:block;box-sizing:border-box;background:#00C9A7;color:#0f0f23;text-align:center;text-decoration:none;border-radius:12px;padding:11px 14px;min-height:48px;line-height:1.25;"><span style="display:block;font-weight:800;font-size:1.02rem;">%s</span><span style="display:block;font-weight:600;font-size:0.8rem;opacity:0.8;margin-top:2px;">Klook &middot; partner link</span></a></div>' % (link, btn)
    )


KLOOK_TRANSPORT = (
    '<div data-ps-placement="klook-japan-transport-itinerary" style="max-width:800px;margin:20px auto;padding:20px;background:#f0faf7;border:1px solid #cdeee5;border-left:4px solid #00C9A7;border-radius:12px;">'
    '<style>.ps-kl-btn{transition:background .15s,box-shadow .15s}.ps-kl-btn:hover,.ps-kl-btn:focus-visible{background:#00B396!important;box-shadow:0 4px 14px rgba(0,201,167,.35)}</style>'
    '<strong style="display:block;font-size:1.1rem;color:#0f0f23;margin:0 0 6px;">Landing at Narita? Want your train or bus ticket sorted before you fly?</strong>'
    '<p style="margin:0 0 14px;font-size:0.95rem;color:#333;line-height:1.5;">You can buy these as e-tickets on Klook. You can also buy at the station or bus counter when you arrive, so booking ahead is a convenience, not a must.</p>'
    '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin:0 0 12px;">'
    + "".join(kl_tile(r) for r in KL_ROWS) +
    '</div>'
    '<p style="margin:0;font-size:0.85rem;color:#555;line-height:1.5;">Before you pay, read each listing\'s change and cancellation rules. Some Skyliner options cannot be cancelled, and Limousine Bus bookings cannot be amended: you cancel and rebook. Buses can run late in traffic, so leave a buffer. We earn a small commission if you book through these links, at no extra cost to you.</p>'
    '</div>'
)


block = MARK + "\n" + KLOOK_TRANSPORT + "\n"
path = os.path.join(BASE, PAGE)
s = open(path, encoding="utf-8").read()
if MARK in s:
    pat = re.compile(re.escape(MARK) + r".*?</div>\n(?=\s*<h4>)", re.S)
    ms = list(pat.finditer(s))
    assert len(ms) == 1, ("block count", len(ms))
    new = s[:ms[0].start()] + block + s[ms[0].end():]
    print("up to date" if new == s else "refreshed")
else:
    # insert right after the Day 1 "Arrive at Narita or Haneda" paragraph
    h = s.find("Morning: Arrive at Narita or Haneda</h4>")
    assert h > 0, "Day 1 arrival heading not found"
    p_end = s.find("</p>", h)
    assert p_end > 0
    p_end += len("</p>")
    # skip to end of line so the block starts on its own line
    nl = s.find("\n", p_end)
    new = s[:nl + 1] + block + s[nl + 1:]
    print("added")
open(path, "w", encoding="utf-8").write(new)
