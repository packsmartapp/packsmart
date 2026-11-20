#!/usr/bin/env python3
"""w54: fixes from the 20 Nov 2026 reviewer feedback on the airport guides.

Post-processor. Run AFTER w25 / w31 / w35 (Narita, Haneda, Kansai) and w32 (Japan Sakura block),
BEFORE the pocket-guide chain. Idempotent: a replacement whose old text is gone but whose new text
is present counts as already applied.

Sources (checked 20 Nov 2026):
- Last N'EX from Narita T1, 21:44 weekdays: JR East station timetable, Dec 2026 issue.
- N'EX TOKYO Round Trip Ticket: JR East (adult 5,200 / child 2,600, 14 days, non-Japanese passports).
- Fixed-fare taxi zones: narita-airport.jp/en/access/taxi (tolls and 22:00-05:00 surcharge extra).
- Joint immigration/customs kiosks: Japan Customs kiosk_2.pdf (Kansai T1/T2 1 Apr 2025, Haneda T2 1 Apr 2025,
  Haneda T3 16 Apr 2025, Narita T3 7 Apr 2025); Narita T1/T2 from 24 Sep 2026 (Panasonic Connect, 18 Sep 2026).
- Sakura Mobile pick-up table (sakuramobile.jp): Narita T1 and T2 JAL ABC counters, T3 none; Haneda T3 JAL ABC;
  Kansai T1 1F Sakura counter 6:00-23:00, none at T2.
- JAL same-day delivery: JAL page, Haneda T3, 4,500 yen per suitcase, 4:00-18:00.
"""
import re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent / "public"
BLOG = ROOT / "blog"
report = []

def apply(path, pairs):
    p = pathlib.Path(path)
    s = p.read_text(encoding="utf-8")
    for label, old, new, *opt in pairs:
        count = opt[0] if opt else 1
        n = s.count(old)
        if n == 0:
            if new in s:
                report.append(f"  already  {p.name}: {label}")
                continue
            sys.exit(f"MISSING {p.name}: {label}")
        if n != count:
            sys.exit(f"COUNT {p.name}: {label}: expected {count}, found {n}")
        s = s.replace(old, new)
        report.append(f"  applied  {p.name}: {label}")
    p.write_text(s, encoding="utf-8")

def remove_typical_fares(path):
    p = pathlib.Path(path)
    s = p.read_text(encoding="utf-8")
    s2, n = re.subn(r'\n?    <p data-ps-anchor="pickups"[^>]*>Typical fares, airport to city centre:[^<]*</p>', "", s)
    if n:
        p.write_text(s2, encoding="utf-8")
        report.append(f"  applied  {p.name}: removed 'Typical fares' line")
    else:
        report.append(f"  already  {p.name}: no 'Typical fares' line")

def og_pinterest(path):
    p = pathlib.Path(path)
    s = p.read_text(encoding="utf-8")
    m = re.search(r'<meta property="og:image" content="([^"]+)"', s)
    if not m:
        report.append(f"  skipped  {p.name}: no og:image")
        return
    from urllib.parse import quote
    enc = quote(m.group(1), safe="")
    old = "media=https%3A%2F%2Fwww.packsmartapp.com%2Fog-default.png"
    if old in s:
        p.write_text(s.replace(old, "media=" + enc), encoding="utf-8")
        report.append(f"  applied  {p.name}: Pinterest share uses og:image")
    else:
        report.append(f"  already  {p.name}: Pinterest share")

CAR_OLD = ("Lakeside roads below Mount Fuji, mountain villages, and the open country of Hokkaido, Kyushu and Shikoku sit far from any station. "
           "With your own car you stop when the view says stop, and the luggage rides with you.")
CAR_NEW = ("A rental car helps when you are heading somewhere trains reach slowly, such as the mountains or the coast, "
           "or when you are travelling with a lot of luggage. With your own car you stop when the view says stop, and the luggage rides with you.")

QR_OLD = "register on Visit Japan Web (free) and keep the QR codes on your phone.</li>"
QR_NEW = "register on Visit Japan Web (free) and keep the QR codes on your phone. Every traveller, children included, needs their own QR code.</li>"

# ---------------------------------------------------------------- Narita
apply(BLOG / "narita-airport-guide.html", [
 ("late arrival",
  "<p><strong>Late arrival?</strong> The Narita Express and Skyliner are reported to stop around 11 pm, while buses run later. If you land late, check the last train before you book.</p>",
  "<p><strong>Late arrival?</strong> The last Narita Express leaves Terminal 1 at 21:44 on weekdays (JR East timetable, December 2026 issue). "
  "Keisei trains and some buses leave later than that, but times differ by operator and by day, so check the timetable before you rely on one. "
  "If you land after about 9 pm, a fixed-fare taxi or a pre-booked transfer is the fallback.</p>"),
 ("taxi row",
  'Very expensive, often over ¥20,000</td><td data-label="Good to know">A fixed-price private transfer (below) is usually the better car option.</td>',
  'About ¥29,000 to ¥32,500 for central Tokyo, plus tolls</td><td data-label="Good to know">Narita lists a fixed fare for each zone, and a surcharge applies from 22:00 to 5:00. '
  'Confirm the fare with the driver before you board. <a href="https://www.narita-airport.jp/en/access/taxi" target="_blank" rel="noopener">Narita Airport taxi fares</a>.</td>'),
 ("N'EX round-trip ticket",
  '</td></tr>\n</tbody>\n</table>\n</div>\n<div class="warning-box">\n    <strong>Two trains look alike.</strong>',
  '</td></tr>\n</tbody>\n</table>\n</div>\n'
  '<p><strong>Foreign passport holders: the N\'EX round-trip ticket.</strong> JR East sells an N\'EX Tokyo Round Trip Ticket for ¥5,200 (adult) or ¥2,600 (child, 6 to 11), '
  'which is ¥2,600 per adult trip. It is valid for 14 days and only for holders of non-Japanese passports. Pick it up at the JR East Travel Service Center or ticket office '
  'at Terminal 1 or Terminal 2·3 station, or buy it online. <a href="https://www.jreast.co.jp/en/multi/pass/nex.html" target="_blank" rel="noopener">JR East ticket page</a>.</p>\n'
  '<div class="warning-box">\n    <strong>Two trains look alike.</strong>'),
 ("where-staying N'EX row",
  "Direct, no changing trains, and there is room for suitcases.</td>",
  "Direct, no changing trains, and there is room for suitcases. Foreign passport holders can save with the round-trip ticket below the table.</td>"),
 ("kiosks",
  "Narita's Terminals 1 and 2 have added self-service kiosks that handle immigration and customs together for foreign visitors (reported as fully running from 24 September 2026).",
  "Narita has self-service kiosks that handle immigration and customs together for foreign visitors: Terminal 3 since April 2025, and Terminals 1 and 2 from 24 September 2026."),
 ("QR per traveller", QR_OLD, QR_NEW),
 ("Sakura pick-up",
  "at the Sakura Mobile counter at Terminal 1 (South Wing, 1st floor) or Terminal 2 (1st floor), or at a post office.",
  "at the JAL ABC counter in Terminal 1 (South Wing, 1st floor) or Terminal 2 (1st floor), open from 6:30 am until one hour after the last international arrival. "
  "Terminal 3 has no counter, so use Terminal 2. You can also pick up at a post office."),
 ("visa wording",
  "Leaving the airport means passing immigration, so check whether you need a visa, and leave plenty of time to get back.",
  "Leaving the airport means entering Japan, so you need the visa or visa exemption that applies to your passport. Check with your airline or the Japanese embassy before you book, and leave plenty of time to get back."),
 ("station name", "<td data-label=\"Train station\">Airport Terminal 2 Station</td>", "<td data-label=\"Train station\">Airport Terminal 2·3 Station</td>"),
 ("wifi return table",
  "You must return it. Return it before you reach the departures lobby, especially at Terminal 1.",
  "You must return it: post it in the envelope it comes with, or hand it in at your provider's return counter. Do this before you go through security."),
 ("wifi return list",
  "hand it back before you reach the departures lobby, especially at Terminal 1.",
  "return it before you go through security: post it in the envelope it comes with, or use your provider's return counter."),
 ("date line",
  "Last updated November 2026 · Facts checked 16 Nov 2026",
  "Last updated November 20, 2026 · Facts checked 16 and 20 Nov 2026"),
 ("change log",
  "added the find-it tool, the diagram, the train card, luggage, assistance, late arrival and Narita-or-Haneda sections.</li>\n</ul>",
  "added the find-it tool, the diagram, the train card, luggage, assistance, late arrival and Narita-or-Haneda sections.</li>\n"
  "<li><strong>20 Nov 2026:</strong> corrected the late-arrival advice (the last Narita Express leaves at 21:44), added the foreign-passport N'EX round-trip ticket and the fixed taxi fares, "
  "and corrected the kiosk and pocket Wi-Fi pick-up details.</li>\n</ul>"),
 ("car intro", CAR_OLD, CAR_NEW),
])
remove_typical_fares(BLOG / "narita-airport-guide.html")
og_pinterest(BLOG / "narita-airport-guide.html")

# ---------------------------------------------------------------- Haneda
apply(BLOG / "haneda-airport-guide.html", [
 ("QR per traveller", QR_OLD, QR_NEW),
 ("kiosks",
  "Have your passport ready, and your arrival card if you filled one in. The automatic gates do not stamp your passport",
  "Have your passport ready, and your arrival card if you filled one in. Haneda has combined immigration and customs kiosks at Terminals 2 and 3 (since April 2025): scan your Visit Japan Web QR code there. "
  "The automatic gates do not stamp your passport"),
 ("same-day delivery",
  "<li><strong>Usually next day.</strong> JAL ABC says the earliest delivery from the airport is the next day. Some same-day services exist for limited areas, with cut-off times, so do not plan around same-day.</li>",
  "<li><strong>Usually next day, with one same-day option.</strong> Most airport delivery arrives the next day. JAL runs a same-day service for any airline's passengers from the JAL ABC counter in Terminal 3 "
  "(4 am to 6 pm) to hotels in central Tokyo, at ¥4,500 per suitcase. Bags handed in before 4 pm are due at the hotel by 8 pm, and bags handed in before 6 pm by 10 pm. "
  "JAL says delivery can be late, or not possible, in bad weather or heavy traffic. <a href=\"https://www.jal.co.jp/uk/en/offers/same-day-delivery-service/\" target=\"_blank\" rel=\"noopener\">JAL same-day delivery page</a>.</li>"),
 ("visa wording",
  "leaving the airport means passing immigration, so check whether you need a visa, and leave plenty of time to get back.",
  "leaving the airport means entering Japan, so you need the visa or visa exemption that applies to your passport (check with your airline or the Japanese embassy), and you should leave plenty of time to get back."),
 ("date line",
  "Last updated November 2026 · Facts checked 18 Nov 2026",
  "Last updated November 20, 2026 · Facts checked 18 and 20 Nov 2026"),
 ("change log",
  "late arrival and Haneda-or-Narita sections.</li>\n</ul>",
  "late arrival and Haneda-or-Narita sections.</li>\n"
  "<li><strong>20 Nov 2026:</strong> added the same-day luggage delivery from Terminal 3 and the immigration and customs kiosks.</li>\n</ul>"),
 ("car intro", CAR_OLD, CAR_NEW),
])
remove_typical_fares(BLOG / "haneda-airport-guide.html")
og_pinterest(BLOG / "haneda-airport-guide.html")

# ---------------------------------------------------------------- Kansai
apply(BLOG / "kansai-airport-guide.html", [
 ("QR per traveller", QR_OLD, QR_NEW),
 ("kiosks",
  "Kansai Airport describes kiosks that handle immigration and customs together using your Visit Japan Web QR code.",
  "Kansai has combined immigration and customs kiosks at Terminals 1 and 2 (since April 2025): scan your Visit Japan Web QR code there."),
 ("Sakura pocket Wi-Fi",
  "choose a pick-up point when you order, or ask for free delivery to your hotel. We did not confirm a Sakura counter at Kansai Airport, so check Sakura's page for pick-up places and hours.",
  "pick up at the Sakura Mobile counter in the Terminal 1 arrival lobby, 1st floor (6 am to 11 pm, as Sakura lists it), or ask for free delivery to your hotel. "
  "There is no Sakura counter at Terminal 2, so take the free shuttle bus to Terminal 1."),
 ("Sakura SIM",
  "check Sakura Mobile's page for pick-up places before you order, and show your booking on your phone.",
  "the same Sakura counter in Terminal 1, with your booking on your phone."),
 ("date line",
  "Last updated November 2026 · Facts checked 18 Nov 2026",
  "Last updated November 20, 2026 · Facts checked 18 and 20 Nov 2026"),
 ("change log",
  "late arrival and getting to Osaka and Kyoto.</li>\n</ul>",
  "late arrival and getting to Osaka and Kyoto.</li>\n"
  "<li><strong>20 Nov 2026:</strong> corrected the Sakura Mobile pick-up place and the immigration and customs kiosks.</li>\n</ul>"),
 ("car intro", CAR_OLD, CAR_NEW),
])
remove_typical_fares(BLOG / "kansai-airport-guide.html")
og_pinterest(BLOG / "kansai-airport-guide.html")

# ---------------------------------------------------------------- Japan guides: Sakura pick-up sentence (also in tools/w32)
SAK_OLD = ("the travel SIM is available at Sakura Mobile counters at Narita, Haneda, Kansai and Fukuoka airports, and the pocket Wi-Fi also at New Chitose and Chubu Centrair.")
SAK_NEW = ("at the JAL ABC counters in Narita Terminals 1 and 2 and Haneda Terminal 3, at Sakura Mobile's own counters at Kansai (Terminal 1) and Fukuoka, "
           "and also at New Chitose and Chubu Centrair for the pocket Wi-Fi.")
for name in ("japan-travel-packing-guide.html", "japan-travel-packing-guide-from-india.html", "japan-7-day-itinerary-budget.html"):
    apply(BLOG / name, [("Sakura pick-up places", SAK_OLD, SAK_NEW)])
w32 = pathlib.Path(__file__).resolve().parent / "w32_japan_sakura_block.py"
t = w32.read_text(encoding="utf-8")
if SAK_OLD in t:
    w32.write_text(t.replace(SAK_OLD, SAK_NEW), encoding="utf-8"); report.append("  applied  w32_japan_sakura_block.py: pick-up sentence")
else:
    report.append("  already  w32_japan_sakura_block.py")

# ---------------------------------------------------------------- Narita pocket guide
apply(ROOT / "narita-pocket.html", [
 ("late arrival",
  "Trains are reported to stop around 11 pm.",
  "The last Narita Express leaves Terminal 1 at 21:44 on weekdays. Keisei trains and some buses run later, so check the timetable."),
])

# first occurrence only (the "to Tokyo" direction); the "to the airport" line is left as it was
_pp = ROOT / "narita-pocket.html"
_s = _pp.read_text(encoding="utf-8")
_old = "A metered taxi is often over &yen;20,000."
_new = "Taxis from the airport charge a fixed fare by zone, about &yen;29,000 to &yen;32,500 for central Tokyo plus tolls."
if _new in _s:
    report.append("  already  narita-pocket.html: taxi")
else:
    assert _s.count(_old) == 2
    _pp.write_text(_s.replace(_old, _new, 1), encoding="utf-8")
    report.append("  applied  narita-pocket.html: taxi (first occurrence)")

print("\n".join(report))
