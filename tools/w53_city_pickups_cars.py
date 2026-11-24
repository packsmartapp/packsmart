#!/usr/bin/env python3
"""w53: Welcome Pickups and DiscoverCars blocks for the Osaka and Kyoto city guides.

Run from the repo root, AFTER w38 / w41 (those scripts regenerate the pages and would drop these blocks).
Idempotent: a page that already has its placement id is skipped.

 - Osaka city guide: Welcome Pickups (Kansai Airport to an Osaka hotel) + DiscoverCars (Osaka Kansai default pick-up).
 - Station guides (added later on 20 Nov 2026): Osaka station = Welcome Pickups + DiscoverCars (Osaka Kansai default);
   Kyoto station = DiscoverCars (Kyoto Station default); Tokyo station = Welcome Pickups (Narita/Haneda) + DiscoverCars
   (Haneda default); Shinjuku station (22 Nov 2026) and Ueno station (23 Nov 2026) = the same pair as Tokyo. New Chitose Airport and
   Sapporo Station (24 Nov 2026) = transfer to a Sapporo hotel + DiscoverCars (New Chitose / Sapporo Station default). Blocks go before the "Leaving ..." section (Tokyo transfer: before "Local trains, Metro and Disney").
   Re-run this script after w36 / w39 / w42 as well, because those regenerate the station pages.
 - Kyoto city guide: DiscoverCars only (Kyoto Station default pick-up). The Welcome Pickups destination list has no
   Kyoto entry (checked on the live Kansai guide widget on 20 Nov 2026), so no transfer block is added there.

Blocks are copied from the Japan packing guide (the same template w35 uses for the Kansai airport guide) and adapted.
No fares are printed (the template's fare line is removed).
"""
import os, re, sys

BLOG = os.path.join(os.getcwd(), "public", "blog")
TEMPLATE = os.path.join(BLOG, "japan-travel-packing-guide.html")


def die(msg):
    sys.stderr.write("w53 FAILED: " + msg + "\n")
    sys.exit(1)


if not os.path.isfile(TEMPLATE):
    die("template not found: " + TEMPLATE)
t = open(TEMPLATE, encoding="utf-8").read().split("\n")


def block(pid):
    start = None
    for i, l in enumerate(t):
        if ('data-ps-placement="%s"' % pid) in l and l.lstrip().startswith("<div"):
            start = i
            break
    if start is None:
        die("placement block not found in template: " + pid)
    depth = 0
    for j in range(start, len(t)):
        depth += len(re.findall(r"<div\b", t[j])) - len(re.findall(r"</div>", t[j]))
        if depth == 0:
            return "\n".join(t[start:j + 1])
    die("unbalanced block: " + pid)


def rep(s, old, new, count=1):
    if s.count(old) < 1:
        die("text not found: " + old[:70])
    return s.replace(old, new, count) if count else s.replace(old, new)


def pickups_block(pid, heading, local=None):
    b = block("pickups-japan")
    b = b.replace("pickups-japan", pid)
    if local:
        old = "var LOCAL=['Tokyo','Osaka','Sapporo']"
        if b.count(old) != 1:
            die("pickups LOCAL list not found")
        b = b.replace(old, "var LOCAL=[%s]" % ",".join("'%s'" % c for c in local), 1)
    m = re.search(r'<p data-ps-anchor="pickups"[^>]*>Typical fares[^<]*</p>\n?', b)
    if not m:
        die("pickups fare line not found")
    b = b.replace(m.group(0), "")
    k = b.find("</style>")
    if k < 0:
        die("pickups style close not found")
    k += len("</style>")
    h3 = ('\n    <h3 style="margin:0 0 16px 0;color:#0f0f23;font-size:1.3rem;line-height:1.3;">' + heading + "</h3>")
    return b[:k] + h3 + b[k:]


def cars_block(pid, heading, p1, p2, default):
    """default: 'hnd', 'kix', 'kyoto', or a (city, place, label) tuple for a pick-up place the template has no chip for.
    Tuple places must be checked in the DiscoverCars widget first: widget.discovercars.com/locations/japan/<city>/<place>
    must show that place, not just the city (a wrong place silently falls back to the whole city)."""
    b = block("discovercars-japan-guide").replace("discovercars-japan-guide", pid)
    b = rep(b, '<div id="rent-a-car" data-ps-placement="%s"' % pid,
            '<div id="rent-a-car" data-ps-placement="%s"' % pid)
    b = rep(b, "Rent a Car in Japan: Go Where Trains and Buses Don't", heading)
    old1 = re.search(r'(<p style="margin: 0 0 10px 0; color: #444[^>]*>)([^<]*)(</p>)', b)
    old2 = re.search(r'(<p style="margin: 0 0 10px 0; color: #666[^>]*>)([^<]*)(</p>)', b)
    if not old1 or not old2:
        die("car intro paragraphs not found")
    b = b.replace(old1.group(0), old1.group(1) + p1 + old1.group(3), 1)
    b = b.replace(old2.group(0), old2.group(1) + p2 + old2.group(3), 1)
    on_hnd = 'class="ps-dc-chip on" data-country="japan" data-city="tokyo" data-place="hnd" aria-pressed="true"'
    off_hnd = 'class="ps-dc-chip" data-country="japan" data-city="tokyo" data-place="hnd" aria-pressed="false"'
    if default == "hnd":
        if on_hnd not in b:
            die("Haneda chip is not the default in the template any more")
        init_old = init_new = None
        if "India" in b.replace("Australia and India", ""):
            die("India framing left in the car block")
        return b
    b = rep(b, on_hnd, off_hnd)
    if isinstance(default, tuple):
        city, place, label = default
        first = 'class="ps-dc-chip" data-country="japan" data-city="tokyo" data-place="hnd" aria-pressed="false">'
        i = b.find('<button type="button" ' + first)
        if i < 0:
            die("Haneda chip not found for inserting " + label)
        chip = ('<button type="button" class="ps-dc-chip on" data-country="japan" data-city="%s" data-place="%s" '
                'aria-pressed="true">%s</button>\n        ' % (city, place, label))
        b = b[:i] + chip + b[i:]
        init_old, init_new = "&city=tokyo&place=hnd&locale=en", "&city=%s&place=%s&locale=en" % (city, place)
        if b.count(init_old) != 1:
            die("initial widget place not found exactly once")
        b = b.replace(init_old, init_new, 1)
        if "India" in b:
            die("India framing left in the car block")
        return b
    if default == "kix":
        off = 'class="ps-dc-chip" data-country="japan" data-city="osaka" data-place="kix" aria-pressed="false"'
        on = 'class="ps-dc-chip on" data-country="japan" data-city="osaka" data-place="kix" aria-pressed="true"'
        init_old, init_new = "&city=tokyo&place=hnd&locale=en", "&city=osaka&place=kix&locale=en"
    else:
        off = 'class="ps-dc-chip" data-country="japan" data-city="kyoto" data-place="kyoto-railway-station" aria-pressed="false"'
        on = 'class="ps-dc-chip on" data-country="japan" data-city="kyoto" data-place="kyoto-railway-station" aria-pressed="true"'
        init_old, init_new = "&city=tokyo&place=hnd&locale=en", "&city=kyoto&place=kyoto-railway-station&locale=en"
    b = rep(b, off, on)
    if b.count(init_old) != 1:
        die("initial widget place not found exactly once")
    b = b.replace(init_old, init_new, 1)
    if "India" in b:
        die("India framing left in the car block")
    return b


def insert_before_faq(path, pid, html, marker, anchor='<h2 id="faq">'):
    s = open(path, encoding="utf-8").read()
    if ('data-ps-placement="%s"' % pid) in s:
        return False, s
    if s.count(anchor) != 1:
        die("anchor not unique in %s: %s" % (path, anchor))
    return True, s.replace(anchor, marker + html + "\n\n" + anchor, 1)


# ---------------------------------------------------------------- Osaka
osaka_path = os.path.join(BLOG, "osaka-travel-guide.html")
if not os.path.isfile(osaka_path):
    die("osaka page not found")
o_pick = pickups_block("pickups-osaka-city", "Your Driver at Kansai Airport, to Your Osaka Hotel")
o_cars = cars_block(
    "discovercars-osaka-city",
    "Rent a Car near Osaka: Go Where Trains and Buses Don't",
    "The mountain roads and coast of Wakayama, and other places around Kansai, sit a long way from any station. "
    "With your own car you stop when you like, and the luggage rides with you.",
    "Skip the car inside Osaka and Kyoto, where trains are quicker. Choose a pick-up point, collect the car as you "
    "leave town, then compare prices below. Japan drives on the left.",
    "kix")
o_intro = ('<h3>Airport transfer and car rental</h3>\n'
           '<p>If you land at Kansai Airport, you can book a private driver to your Osaka hotel before you fly. '
           'For day trips by road, compare self-drive rentals below.</p>\n')
changed_o, s_o = insert_before_faq(osaka_path, "pickups-osaka-city", o_pick + "\n" + o_cars, o_intro)
if changed_o:
    if s_o.count('data-ps-placement="discovercars-osaka-city"') < 1:
        die("osaka cars block missing after insert")
    open(osaka_path, "w", encoding="utf-8").write(s_o)

# ---------------------------------------------------------------- Kyoto
kyoto_path = os.path.join(BLOG, "kyoto-travel-guide.html")
if not os.path.isfile(kyoto_path):
    die("kyoto page not found")
k_cars = cars_block(
    "discovercars-kyoto-city",
    "Rent a Car near Kyoto: Go Where Trains and Buses Don't",
    "Amanohashidate and Ine, in the north of Kyoto Prefecture, are a long way from the city's main stations. "
    "With your own car you set your own timetable, and the luggage rides with you.",
    "Skip the car inside Kyoto, where trains and buses are quicker. Choose a pick-up point, collect the car as you "
    "leave town, then compare prices below. Japan drives on the left.",
    "kyoto")
k_intro = ('<h3>Car rental for day trips by road</h3>\n'
           '<p>For trips outside the city, such as the northern coast, compare self-drive rentals below.</p>\n')
changed_k, s_k = insert_before_faq(kyoto_path, "discovercars-kyoto-city", k_cars, k_intro)
if changed_k:
    open(kyoto_path, "w", encoding="utf-8").write(s_k)


# ---------------------------------------------------------------- Station guides
def add(path, pid, html, marker, anchor):
    ch, txt = insert_before_faq(path, pid, html, marker, anchor)
    if ch:
        open(path, "w", encoding="utf-8").write(txt)
    return ch


LEAVE = '<h2 id="leaving">'
st = {}
p = os.path.join(BLOG, "osaka-station-guide.html")
if not os.path.isfile(p):
    die("osaka station page not found")
ch1 = add(p, "pickups-osaka-station",
          pickups_block("pickups-osaka-station", "Your Driver at Kansai Airport, to Your Osaka Hotel")
          + "\n" + cars_block("discovercars-osaka-station",
                              "Rent a Car near Osaka: Go Where Trains and Buses Don't",
                              "The mountain roads and coast of Wakayama, and other places around Kansai, sit a long way from any station. "
                              "With your own car you stop when you like, and the luggage rides with you.",
                              "Skip the car inside Osaka and Kyoto, where trains are quicker. Choose a pick-up point, collect the car as you "
                              "leave town, then compare prices below. Japan drives on the left.", "kix"),
          '<h2 id="car-and-transfer">Airport transfer and car rental</h2>\n'
          '<p>If you land at Kansai Airport, you can book a private driver to your Osaka hotel before you fly. '
          'For day trips by road, compare self-drive rentals below.</p>\n', LEAVE)

p = os.path.join(BLOG, "kyoto-station-guide.html")
if not os.path.isfile(p):
    die("kyoto station page not found")
ch2 = add(p, "discovercars-kyoto-station",
          cars_block("discovercars-kyoto-station",
                     "Rent a Car near Kyoto: Go Where Trains and Buses Don't",
                     "Amanohashidate and Ine, in the north of Kyoto Prefecture, are a long way from the city's main stations. "
                     "With your own car you set your own timetable, and the luggage rides with you.",
                     "Skip the car inside Kyoto, where trains and buses are quicker. Choose a pick-up point, collect the car as you "
                     "leave town, then compare prices below. Japan drives on the left.", "kyoto"),
          '<h2 id="car-rental">Car rental for day trips by road</h2>\n'
          '<p>For trips outside the city, such as the northern coast, compare self-drive rentals below.</p>\n', LEAVE)

p = os.path.join(BLOG, "tokyo-station-guide.html")
if not os.path.isfile(p):
    die("tokyo station page not found")
ch3 = add(p, "pickups-tokyo-station",
          pickups_block("pickups-tokyo-station", "Your Driver at Narita or Haneda, to Your Tokyo Hotel"),
          '<h2 id="transfer">Private airport transfer</h2>\n'
          '<p>If you would rather have a driver than a train after a long flight, you can book a private transfer from '
          'Narita or Haneda to your Tokyo hotel before you fly.</p>\n', '<h2 id="rail">')
ch4 = add(p, "discovercars-tokyo-station",
          cars_block("discovercars-tokyo-station",
                     "Rent a Car near Tokyo: Go Where Trains and Buses Don't",
                     "Lakeside roads below Mount Fuji and mountain villages sit a long way from any station. "
                     "With your own car you stop when you like, and the luggage rides with you.",
                     "Skip the car inside Tokyo, where trains are quicker. Choose a pick-up point, collect the car as you "
                     "leave town, then compare prices below. Japan drives on the left.", "hnd"),
          '<h2 id="car-rental">Car rental for trips outside Tokyo</h2>\n'
          '<p>For trips by road, compare self-drive rentals below.</p>\n', LEAVE)

p = os.path.join(BLOG, "shinjuku-station-guide.html")
if not os.path.isfile(p):
    die("shinjuku station page not found")
ch5 = add(p, "pickups-shinjuku-station",
          pickups_block("pickups-shinjuku-station", "Your Driver at Narita or Haneda, to Your Shinjuku Hotel"),
          '<h2 id="transfer">Private airport transfer</h2>\n'
          '<p>If you would rather have a driver than a train or bus after a long flight, you can book a private transfer from '
          'Narita or Haneda to your hotel in Shinjuku before you fly.</p>\n', '<h2 id="lines">')
ch6 = add(p, "discovercars-shinjuku-station",
          cars_block("discovercars-shinjuku-station",
                     "Rent a Car near Tokyo: Go Where Trains and Buses Don't",
                     "Lakeside roads below Mount Fuji and mountain villages sit a long way from any station. "
                     "With your own car you stop when you like, and the luggage rides with you.",
                     "Skip the car inside Tokyo, where trains are quicker. Choose a pick-up point, collect the car as you "
                     "leave town, then compare prices below. Japan drives on the left.", "hnd"),
          '<h2 id="car-rental">Car rental for trips outside Tokyo</h2>\n'
          '<p>For trips by road, compare self-drive rentals below.</p>\n', LEAVE)

p = os.path.join(BLOG, "ueno-station-guide.html")
if not os.path.isfile(p):
    die("ueno station page not found (run w68 first)")
ch7 = add(p, "pickups-ueno-station",
          pickups_block("pickups-ueno-station", "Your Driver at Narita or Haneda, to Your Ueno Hotel"),
          '<h2 id="transfer">Private airport transfer</h2>\n'
          '<p>If you would rather have a driver than a train after a long flight, you can book a private transfer from '
          'Narita or Haneda to your hotel in Ueno before you fly.</p>\n', '<h2 id="metro">')
ch8 = add(p, "discovercars-ueno-station",
          cars_block("discovercars-ueno-station",
                     "Rent a Car near Tokyo: Go Where Trains and Buses Don't",
                     "Lakeside roads below Mount Fuji and mountain villages sit a long way from any station. "
                     "With your own car you stop when you like, and the luggage rides with you.",
                     "Skip the car inside Tokyo, where trains are quicker. Choose a pick-up point, collect the car as you "
                     "leave town, then compare prices below. Japan drives on the left.", "hnd"),
          '<h2 id="car-rental">Car rental for trips outside Tokyo</h2>\n'
          '<p>For trips by road, compare self-drive rentals below.</p>\n', LEAVE)

# New Chitose Airport and Sapporo Station (24 Nov 2026, owner's request). Pick-up places checked in the DiscoverCars
# widget on 24 Nov 2026: chitose/cts shows "Chitose Airport, Chitose, Japan"; sapporo/sapporo-railway-station shows
# "Sapporo Train Station, Sapporo, Japan" (sapporo/cts is NOT a place; it falls back to the whole city). The transfer
# widget's suggested cities include Sapporo (checked on the live widget on 20 Nov 2026), so Sapporo goes first here.
HOK_P1 = ("Ski resorts, lakes and the open country of Hokkaido sit a long way from the train lines. "
          "With your own car you stop when you like, and the skis and luggage ride with you.")
HOK_P2 = ("Skip the car inside Sapporo, where the subway is quicker. In winter, ask the rental company about winter tyres "
          "and driving on snow before you book. Choose a pick-up point, then compare prices below. Japan drives on the left.")
CTS_PLACE = ('chitose', 'cts', 'New Chitose Airport (CTS)')
SPK_PLACE = ('sapporo', 'sapporo-railway-station', 'Sapporo Station')
p = os.path.join(BLOG, "new-chitose-airport-guide.html")
if not os.path.isfile(p):
    die("new chitose page not found (run w70 first)")
ch9 = add(p, "pickups-new-chitose",
          pickups_block("pickups-new-chitose", "Your Driver at New Chitose Airport, to Your Sapporo Hotel",
                        ["Sapporo", "Tokyo", "Osaka"])
          + "\n" + cars_block("discovercars-new-chitose", "Rent a Car at New Chitose: Go Where Trains and Buses Don't",
                              HOK_P1, HOK_P2, CTS_PLACE),
          '<h2 id="transfer-car">Private transfer and car hire</h2>\n'
          '<p>If you would rather have a driver than a train or bus after a long flight, you can book a private transfer '
          'to your hotel in Sapporo before you fly. For ski resorts and the countryside, compare self-drive rentals below.</p>\n',
          '<h2 id="money">')
p = os.path.join(BLOG, "sapporo-station-guide.html")
if not os.path.isfile(p):
    die("sapporo station page not found (run w71 first)")
ch10 = add(p, "pickups-sapporo-station",
           pickups_block("pickups-sapporo-station", "Your Driver at New Chitose Airport, to Your Sapporo Hotel",
                         ["Sapporo", "Tokyo", "Osaka"]),
           '<h2 id="transfer">Private airport transfer</h2>\n'
           '<p>If you would rather have a driver than the Airport train after a long flight, you can book a private transfer '
           'from New Chitose Airport to your hotel in Sapporo before you fly.</p>\n', '<h2 id="long-distance">')
ch11 = add(p, "discovercars-sapporo-station",
           cars_block("discovercars-sapporo-station", "Rent a Car in Sapporo: Go Where Trains and Buses Don't",
                      HOK_P1, HOK_P2, SPK_PLACE),
           '<h2 id="car-rental">Car rental for trips outside Sapporo</h2>\n'
           '<p>For ski resorts and trips by road, compare self-drive rentals below.</p>\n', LEAVE)

print("w53 stations. osaka:", ch1, "| kyoto:", ch2, "| tokyo transfer:", ch3, "| tokyo rental:", ch4,
      "| shinjuku transfer:", ch5, "| shinjuku rental:", ch6, "| ueno transfer:", ch7, "| ueno rental:", ch8,
      "| new chitose transfer+rental:", ch9, "| sapporo transfer:", ch10, "| sapporo rental:", ch11)

print("w53 done. osaka:", "added" if changed_o else "already applied", "| kyoto:", "added" if changed_k else "already applied")
