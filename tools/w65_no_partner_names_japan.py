#!/usr/bin/env python3
"""
w65: no partner names in our own words on the Japan pages (D47, stage 2; 23 Nov 2026).

Readers do not need to know which company a link goes to: our headings, buttons, labels, alt text and body
text say what the thing is, plus "(partner link)". This rewrites the partner names in the Japan articles
(airport, station and city guides, the Japan guide and the 7-day itinerary) after the generators and
post-processors have run, so it sits at the end of the chain (after w64).

Kept on purpose (D47 exceptions):
  - Sakura Mobile where a traveller needs the name to find the pick-up counter ("the Sakura Mobile counter
    in the Terminal 1 arrival lobby", "Sakura lists it as closed from 1 am to 4 am"), and the Kansai changelog line.
  - "Sakura" the Shinkansen train and "Sakurabashi Gate" (not the partner).
  - Names that a partner's own widget shows inside its frame.
  - The SafetyWing box: changed last, after checking SafetyWing's brand guidelines.

Run from the repo root, last in the chain:  python3 tools/w65_no_partner_names_japan.py
Idempotent: each rule is a literal or regex substitution whose old text is gone after one run. Every rule must
match on at least one page on the first run (or its new text must already be present), and the check at the
end fails if a listed partner name is still visible outside the exceptions, so a changed page fails loudly.
"""
import html, os, re, sys

ROOT = os.getcwd()
BLOG = os.path.join(ROOT, "public", "blog")
PAGES = ["narita-airport-guide", "haneda-airport-guide", "kansai-airport-guide",
         "tokyo-station-guide", "shinjuku-station-guide", "ueno-station-guide", "kyoto-station-guide", "osaka-station-guide",
         "new-chitose-airport-guide", "sapporo-station-guide",
         "kyoto-travel-guide", "osaka-travel-guide", "japan-travel-packing-guide", "japan-7-day-itinerary-budget"]

# (old, new, is_regex). New text must not contain a partner name.
RULES = [
    # eSIM tiles (copied from the Japan guide onto every page)
    (", opens Airalo", ", opens our eSIM partner", False),
    ("Airalo asks you to verify your ID before you buy.", "The provider asks you to verify your ID before you buy.", False),
    ("<td>Airalo</td>", "<td>Online eSIM</td>", False),
    # Sakura Mobile SIM and pocket Wi-Fi block
    ("Both are from Sakura Mobile.", "Both come from one Japanese provider, with pick-up at the airport.", False),
    ("Sakura Mobile &middot; partner link", "Partner link", False),
    ('alt="Sakura Mobile Japan travel SIM card"', 'alt="Japan travel SIM card"', False),
    ('alt="Sakura Mobile pocket Wi-Fi device"', 'alt="Pocket Wi-Fi device"', False),
    # button labels
    ("Japan Bullet Train &middot; partner link", "Partner link", False),
    ("Klook &middot; partner link", "Partner link", False),
    # ticket and transfer blocks
    ("You can buy these as e-tickets on Klook.", "You can buy these as e-tickets online.", False),
    ("You can book all four on Klook.", "You can book all four online.", False),
    ("You can book both on Klook.", "You can book both online.", False),
    ("Klook prices as of 14 Nov.", "Prices as of 14 Nov.", False),
    ("Klook prices checked 14-18 Nov and they change by date.", "Prices checked 14-18 Nov and they change by date.", False),
    ("Klook prices checked 18 Nov 2026 and they change by date and route.", "Prices checked 18 Nov 2026 and they change by date and route.", False),
    ("The fares above come from the operators, not from Klook, and Klook&rsquo;s own price depends on the date and the option.",
     "The fares above come from the operators; the online price depends on the date and the option.", False),
    ("The fares above come from the operators, not from Klook, and Klook's own price depends on the date and the option.",
     "The fares above come from the operators; the online price depends on the date and the option.", False),
    ("Klook also sells a direct <a ", "You can also book a direct <a ", False),
    ("<strong>Book online.</strong> Klook lists an <a ", "<strong>Book online.</strong> There is an <a ", False),
    ("<strong>Haruka tickets online.</strong> Klook lists a <a ", "<strong>Haruka tickets online.</strong> You can book a <a ", False),
    (r"Klook lists (a|an|the) <a ", r"You can book \1 <a ", True),
    ("Klook lists <a ", "You can book <a ", False),
    # JR Pass link on the Japan guide (also gains its missing "(partner link)" label)
    (">book a JR Pass on Klook</a> before you go,", ">book a JR Pass online</a> (partner link) before you go,", False),
    ("through an agent such as Klook (", "through an agent (", False),
    # luggage storage callouts
    (r"(Store your bags in (?:Tokyo|Kyoto|Osaka)) with Radical Storage</a>", r"\1</a> (partner link)", True),
    # hotel callout: no partner name and no claim of our own ("great rates")
    ("Compare hotel deals on Trip.com</a> &mdash; great rates on hotels, guesthouses, and apartments.",
     "Compare hotel prices</a> (partner link) for hotels, guesthouses and apartments.", False),
]

NAMES = r"Airalo|GetYourGuide|Welcome Pickups|DiscoverCars|EconomyBookings|Sakura Mobile|Radical Storage|Klook|KKday|Yesim|Trip\.com|Travelpayouts|Japan Bullet Train"
ALLOWED = [  # visible text that may keep a name (D47 exceptions)
    r"Sakura Mobile counter", r"Sakura Mobile lists pick-up", r"Sakura Mobile&rsquo;s own counters", r"Sakura Mobile's own counters",
    r"corrected the Sakura Mobile pick-up place", r"Sakura Mobile.{0,40}counter",
    r"Get a Quote from SafetyWing",
]


def die(msg):
    sys.exit("w65 aborted, nothing written: " + msg)


def visible(s):
    s = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", "", s, flags=re.S)
    attrs = " ".join(re.findall(r'(?:aria-label|alt|title)="([^"]*)"', s))
    return html.unescape(re.sub(r"<[^>]+>", " ", s) + " " + attrs)


plans, used = {}, [0] * len(RULES)
for slug in PAGES:
    path = os.path.join(BLOG, slug + ".html")
    if not os.path.isfile(path):
        die("missing " + path)
    s = open(path, encoding="utf-8").read()
    o = s
    for i, (old, new, rx) in enumerate(RULES):
        if rx:
            s, n = re.subn(old, new, s)
        else:
            n = s.count(old)
            s = s.replace(old, new)
        used[i] += n
    if s != o:
        plans[path] = s

pages_now = {p: plans.get(p) or open(p, encoding="utf-8").read() for p in (os.path.join(BLOG, x + ".html") for x in PAGES)}
for i, (old, new, rx) in enumerate(RULES):
    done_marker = ("You can book" if "Klook lists" in old else "</a> (partner link)") if rx else new[:40]
    if not used[i] and not any(done_marker in s for s in pages_now.values()):
        die("rule %d matched nothing and is not already applied: %r" % (i, old))

# check: no partner name left in visible text, outside the exceptions
left = []
for path, s in pages_now.items():
    t = visible(s)
    for a in ALLOWED:
        t = re.sub(a, "", t)
    t = re.sub(r"Sakurabashi|Hikari, Sakura and Kodama", "", t)
    for m in re.finditer(NAMES, t):
        left.append("%s: ...%s..." % (os.path.basename(path), re.sub(r"\s+", " ", t[max(0, m.start() - 50):m.end() + 30])))
if left:
    die("partner names still visible:\n  " + "\n  ".join(left))

for path, s in plans.items():
    open(path, "w", encoding="utf-8").write(s)
print("w65 done. %d page(s) changed, %d substitution(s)." % (len(plans), sum(used)))
