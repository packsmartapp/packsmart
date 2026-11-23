#!/usr/bin/env python3
"""
w66: no partner names in our own words on the other articles and top-level pages (D47, stage 3; 23 Nov 2026).

Same rule as w65 (Japan pages): our headings, card titles, buttons, labels, alt text and body text say what a
thing is, plus "(partner link)" or "Partner link", never the partner's name.

Not touched here:
  - Japan pages and Pocket Guides (w65 handles them).
  - D47 exceptions: affiliate-disclosure, about (its partner list is a disclosure), terms and privacy (legal),
    the eSIM comparison article and the cards/titles that name it, gyg-preview (internal, noindex).
  - SafetyWing anywhere (box, cards and text): changed last, after checking SafetyWing's brand guidelines.
  - Non-partner names (Skyscanner, Viator, Holafly, Booking.com...): editorial, not ours to hide.

Plus ONEOFFS: exact old -> new pairs for single sentences (app lists, checklists), each found exactly once.
Run from the repo root (any time; these pages are not regenerated):  python3 tools/w66_no_partner_names_articles.py
  --dry   print what would change and what partner names are left, write nothing
Idempotent. Fails without writing if a rule matches nothing anywhere and is not already applied, or if a partner
name (other than SafetyWing) is still visible on a page in scope.
"""
import glob, html, os, re, sys

ROOT = os.getcwd()
PUB = os.path.join(ROOT, "public")
DRY = "--dry" in sys.argv
JP = ("japan-", "narita-", "haneda-", "kansai-", "tokyo-", "kyoto-", "osaka-", "shinjuku-")
EXEMPT = {"affiliate-disclosure.html", "about.html", "terms.html", "privacy-policy.html", "gyg-preview.html",
          "best-esim-international-travel-comparison.html"}

S = r'<strong style="font-size:0\.9rem;">'
# (pattern, replacement, done-marker). All regex.
RULES = [
    # card grid titles (the line under each title says what it is)
    (S + r"GetYourGuide</strong>", '<strong style="font-size:0.9rem;">Tours and activities</strong>', ">Tours and activities</strong>"),
    (S + r"Klook</strong>", '<strong style="font-size:0.9rem;">Tours and tickets</strong>', ">Tours and tickets</strong>"),
    (S + r"Radical Storage</strong>", '<strong style="font-size:0.9rem;">Luggage storage</strong>', ">Luggage storage</strong>"),
    (S + r"Welcome Pickups</strong>", '<strong style="font-size:0.9rem;">Airport transfers</strong>', ">Airport transfers</strong>"),
    (S + r"Trip\.com Hotels</strong>", '<strong style="font-size:0.9rem;">Hotels</strong>', '<strong style="font-size:0.9rem;">Hotels</strong>'),
    (S + r"Yesim eSIM</strong>", '<strong style="font-size:0.9rem;">eSIM offer</strong>', ">eSIM offer</strong>"),
    (r"<strong>12Go Asia</strong></a> &mdash; ", "<strong>Train, bus and ferry tickets</strong></a> (partner link) &mdash; ", "<strong>Train, bus and ferry tickets</strong>"),
    # eSIM tiles
    (r", opens Airalo\"", ', opens our eSIM partner"', ", opens our eSIM partner"),
    (r"Airalo (may ask|asks) you to verify your ID before you buy", r"The provider \1 you to verify your ID before you buy", "The provider "),
    # price notes in the tour boxes
    (r"Klook prices (as of|checked) ", r"Prices \1 ", "Prices as of "),
    # luggage storage callouts
    (r"(Store your bags in [^<]{2,60}?) with Radical Storage</a>", r"\1</a> (partner link)", "</a> (partner link)"),
    # hotel callouts: no partner name, no claim of our own ("great rates")
    (r"Compare (hotel|accommodation|resort) deals on Trip\.com</a> &mdash; great rates on ([^<.]+)\.",
     r"Compare \1 prices</a> (partner link) for \2.", "prices</a> (partner link) for "),
    (r"</a> with Radical Storage and ", "</a> (partner link) and ", "</a> (partner link) and "),
    # tour links in the itineraries and guides: drop the partner name and the claims after it (not our promise)
    (r"(Book [^<]{3,90}?) on GetYourGuide</a> (?:&mdash;|\u2014) [^<]*", r"\1</a> (partner link).", "</a> (partner link)."),
    (r"(Browse All [^<]*?) on Tiqets ", r"\1 (partner link) ", " (partner link) &rarr;"),
    (S + r"Klook USA Tours</strong>", '<strong style="font-size:0.9rem;">Tours and tickets</strong>', ">Tours and tickets</strong>"),
]

ONEOFFS = [
 ("australia-travel-packing-guide.html", ">Book Sydney tours via Klook</a>.", ">Book Sydney tours</a> (partner link)."),
 ("australia-travel-packing-guide.html", ">GetYourGuide offers reef tours</a>.", ">Book reef tours</a> (partner link)."),
 ("bali-10-day-itinerary-mid-range.html", ">Book Ubud waterfall and temple tours</a> on GetYourGuide &mdash; includes hotel pickup and lunch.", ">Book Ubud waterfall and temple tours</a> (partner link)."),
 ("bali-10-day-itinerary-mid-range.html", ">Book Uluwatu temple &amp; Kecak dance tours</a> on GetYourGuide &mdash; includes hotel pickup and Jimbaran dinner.", ">Book Uluwatu temple &amp; Kecak dance tours</a> (partner link)."),
 ("bali-10-day-itinerary-mid-range.html", ">Book Nusa Penida day tours and snorkeling trips</a> on GetYourGuide &mdash; fast boat, driver, and lunch included.", ">Book Nusa Penida day tours and snorkeling trips</a> (partner link)."),
 ("bali-10-day-itinerary-mid-range.html", "<tr><td>Klook</td><td>Book tours, attractions, and transfers at discounted rates</td>", "<tr><td>Tour booking app</td><td>Book tours, attractions and transfers</td>"),
 ("bali-travel-packing-guide-from-india.html", "<strong>Klook</strong></a> &mdash; Book activities, day trips, and attraction tickets at discounted rates", "<strong>Tours and tickets</strong></a> (partner link) &mdash; Book activities, day trips, and attraction tickets ahead"),
 ("carry-on-packing-list.html", "get an eSIM (Airalo, Holafly) before you leave.", "get an eSIM before you leave."),
 ("china-travel-packing-guide.html", "<strong>Ctrip (Trip.com):</strong> Book trains, flights, hotels.", "<strong>Ctrip:</strong> Book trains, flights, hotels."),
 ("china-travel-packing-guide.html", "<strong>eSIM (Airalo):</strong>", "<strong>eSIM:</strong>"),
 ("costa-rica-packing-list.html", "An Airalo eSIM covers Costa Rica", "An eSIM covers Costa Rica"),
 ("costa-rica-packing-list.html", "<li><strong>GetYourGuide:</strong> Skip-the-line attraction access; pre-book", "<li><strong>Tour booking apps:</strong> Pre-book"),
 ("costa-rica-packing-list.html", "<li><strong>Airalo:</strong> eSIM data service with Costa Rica plans", "<li><strong>eSIM:</strong> Costa Rica data plans"),
 ("france-travel-packing-guide.html", "<strong>eSIM (Airalo):</strong>", "<strong>eSIM:</strong>"),
 ("greece-travel-packing-guide.html", "<li><strong>Viator/GetYourGuide:</strong> Book tours and activities. Often cheaper than booking locally.</li>", "<li><strong>Tour booking apps:</strong> Book tours and activities ahead.</li>"),
 ("international-travel-checklist.html", " — Services like Airalo or Holafly offer affordable eSIMs for most countries.", " — eSIMs are sold for most countries and installed on your phone before you fly."),
 ("italy-7-day-itinerary-mid-range.html", ">Book skip-the-line Colosseum &amp; Vatican tours</a> on GetYourGuide &mdash; avoid the 2-hour queues.", ">Book skip-the-line Colosseum &amp; Vatican tours</a> (partner link)."),
 ("italy-7-day-itinerary-mid-range.html", ">Book Uffizi &amp; Duomo skip-the-line tours</a> on GetYourGuide &mdash; skip 2-hour queues at Florence&rsquo;s top attractions.", ">Book Uffizi &amp; Duomo skip-the-line tours</a> (partner link)."),
 ("italy-7-day-itinerary-mid-range.html", ">Book Venice walking tours &amp; Burano day trips</a> on GetYourGuide &mdash; skip-the-line St. Mark&rsquo;s and island boat tours.", ">Book Venice walking tours &amp; Burano day trips</a> (partner link)."),
 ("italy-7-day-itinerary-mid-range.html", "<tr><td>GetYourGuide</td><td>Skip-the-line tickets for museums and attractions</td>", "<tr><td>Tour booking app</td><td>Skip-the-line tickets for museums and attractions</td>"),
 ("italy-travel-packing-guide.html", "<strong>Airalo eSIM:</strong>", "<strong>eSIM:</strong>"),
 ("malaysia-travel-packing-guide-from-india.html", "<strong>Klook</strong></a> &mdash; Discounted tickets for attractions", "<strong>Tours and tickets</strong></a> (partner link) &mdash; Tickets for attractions"),
 ("malaysia-travel-packing-guide-from-india.html", ">Book train tickets on 12Go</a>", ">Book train tickets</a> (partner link)"),
 ("malaysia-travel-packing-guide-from-india.html", "tickets on <a href=\"https://klook.tpx.li/7g3wF1iF\" target=\"_blank\" rel=\"nofollow noopener sponsored\">Klook</a> for discounts</td>", "tickets <a href=\"https://klook.tpx.li/7g3wF1iF\" target=\"_blank\" rel=\"nofollow noopener sponsored\">online</a> (partner link)</td>"),
 ("mexico-7-day-itinerary-mid-range.html", ">Book Teotihuac&aacute;n tours with transport</a> on GetYourGuide &mdash; hotel pickup included.", ">Book Teotihuac&aacute;n tours with transport</a> (partner link)."),
 ("mexico-7-day-itinerary-mid-range.html", ">Book Oaxaca food tours &amp; mezcal experiences</a> on GetYourGuide &mdash; small-group tours with local guides.", ">Book Oaxaca food tours &amp; mezcal experiences</a> (partner link)."),
 ("mexico-7-day-itinerary-mid-range.html", ">Book Tulum cenote tours &amp; Sian Ka&rsquo;an trips</a> on GetYourGuide &mdash; skip-the-line ruins and private cenote access.", ">Book Tulum cenote tours &amp; Sian Ka&rsquo;an trips</a> (partner link)."),
 ("mexico-7-day-itinerary-mid-range.html", "<tr><td>GetYourGuide</td><td>Skip-the-line tickets for ruins and tours</td>", "<tr><td>Tour booking app</td><td>Skip-the-line tickets for ruins and tours</td>"),
 ("mexico-travel-packing-guide.html", "<strong>eSIM (Airalo):</strong>", "<strong>eSIM:</strong>"),
 ("new-zealand-travel-packing-guide.html", ">Book activities through GetYourGuide</a> - Milford Sound cruises, Hobbiton tours, and adventure sports at discounted rates.", ">Book activities</a> (partner link): Milford Sound cruises, Hobbiton tours and adventure sports."),
 ("new-zealand-travel-packing-guide.html", ">GetYourGuide for best prices</a>.", ">a tour booking site</a> (partner link)."),
 ("portugal-travel-packing-guide.html", "<strong>eSIM (Airalo):</strong>", "<strong>eSIM:</strong>"),
 ("singapore-travel-packing-guide-from-india.html", "<li><strong>Klook</strong> &mdash; Discounted attraction tickets (often 20&ndash;30% cheaper than walk-in)", "<li><strong>Tour booking apps</strong> &mdash; Attraction tickets you can book ahead"),
 ("singapore-travel-packing-guide-from-india.html", ">Night Safari</a> tickets on Klook.", ">Night Safari</a> tickets online (partner link)."),
 ("singapore-travel-packing-guide-from-india.html", "For cross-border travel, 12Go covers popular routes:", "For cross-border travel, you can book popular routes online:"),
 ("south-korea-travel-packing-guide.html", "rel=\"nofollow noopener sponsored\">Klook</a> / GetYourGuide</strong> &mdash; Book K-pop concerts, DMZ tours, palace entries, and activities at discounted rates", "rel=\"nofollow noopener sponsored\">Tours and tickets</a></strong> (partner link) &mdash; Book K-pop concerts, DMZ tours, palace entries and activities ahead"),
 ("south-korea-travel-packing-guide.html", "entries on <a href=\"https://www.getyourguide.com/s/?q=DMZ%20Seoul&partner_id=D7IXONS&cmp=ps-south-korea-travel-packing-guide-1\" target=\"_blank\" rel=\"nofollow noopener sponsored\">GetYourGuide</a></td></tr>", "entries <a href=\"https://www.getyourguide.com/s/?q=DMZ%20Seoul&partner_id=D7IXONS&cmp=ps-south-korea-travel-packing-guide-1\" target=\"_blank\" rel=\"nofollow noopener sponsored\">online</a> (partner link)</td></tr>"),
 ("south-korea-travel-packing-guide.html", "Book through <a href=\"https://www.getyourguide.com/s/?q=DMZ%20Seoul&partner_id=D7IXONS&cmp=ps-south-korea-travel-packing-guide-2\" target=\"_blank\" rel=\"nofollow noopener sponsored\">GetYourGuide</a>. Emotional", "<a href=\"https://www.getyourguide.com/s/?q=DMZ%20Seoul&partner_id=D7IXONS&cmp=ps-south-korea-travel-packing-guide-2\" target=\"_blank\" rel=\"nofollow noopener sponsored\">Book online</a> (partner link). Emotional"),
 ("south-korea-travel-packing-guide.html", "&mdash; Book on <a href=\"https://klook.tpx.li/b0GFFpOX\" target=\"_blank\" rel=\"nofollow noopener sponsored\">Klook</a>.", "&mdash; <a href=\"https://klook.tpx.li/b0GFFpOX\" target=\"_blank\" rel=\"nofollow noopener sponsored\">Book online</a> (partner link)."),
 ("spain-10-day-itinerary-mid-range.html", ">Book skip-the-line Sagrada Familia &amp; Park G&uuml;ell tours</a> on GetYourGuide &mdash; avoid the 2-hour queues.", ">Book skip-the-line Sagrada Familia &amp; Park G&uuml;ell tours</a> (partner link)."),
 ("spain-10-day-itinerary-mid-range.html", ">Book Madrid walking tours &amp; Toledo day trips</a> on GetYourGuide &mdash; skip-the-line Prado and palace tours.", ">Book Madrid walking tours &amp; Toledo day trips</a> (partner link)."),
 ("spain-10-day-itinerary-mid-range.html", ">Book Alhambra skip-the-line tours &amp; flamenco shows</a> on GetYourGuide &mdash; guaranteed Nasrid Palace entry.", ">Book Alhambra skip-the-line tours &amp; flamenco shows</a> (partner link)."),
 ("spain-10-day-itinerary-mid-range.html", "If sold out, GetYourGuide guided tours often have remaining allocations.", "If sold out, guided tours sold by tour companies sometimes still have places."),
 ("spain-10-day-itinerary-mid-range.html", "<tr><td>GetYourGuide</td><td>Skip-the-line tickets for museums and attractions</td>", "<tr><td>Tour booking app</td><td>Skip-the-line tickets for museums and attractions</td>"),
 ("spain-travel-packing-guide.html", "<strong>Airalo eSIM:</strong>", "<strong>eSIM:</strong>"),
 ("sri-lanka-travel-packing-guide-from-india.html", "<strong>Klook</strong></a> or Viator &mdash; Book day trips, tea plantation tours, and temple visits at discounted rates", "<strong>Tours and day trips</strong></a> (partner link) &mdash; Book day trips, tea plantation tours and temple visits ahead"),
 ("sri-lanka-travel-packing-guide-from-india.html", ">Book reserved seats on 12Go</a>;", ">Book reserved seats</a> (partner link);"),
 ("switzerland-travel-packing-guide.html", "<strong>Airalo eSIM:</strong>", "<strong>eSIM:</strong>"),
 ("thailand-7-day-itinerary-mid-range.html", ">Book skip-the-line Bangkok temple tours</a> on GetYourGuide &mdash; includes hotel pickup and a licensed guide.", ">Book skip-the-line Bangkok temple tours</a> (partner link)."),
 ("thailand-7-day-itinerary-mid-range.html", ">Book Chiang Mai elephant sanctuary visits</a> on GetYourGuide &mdash; includes hotel pickup and lunch.", ">Book Chiang Mai elephant sanctuary visits</a> (partner link)."),
 ("thailand-7-day-itinerary-mid-range.html", ">Book 4 Islands and Phi Phi tours from Krabi</a> on GetYourGuide &mdash; free cancellation up to 24 hours.", ">Book 4 Islands and Phi Phi tours from Krabi</a> (partner link)."),
 ("thailand-7-day-itinerary-mid-range.html", "is a classic experience. Book through 12Go.asia.", "is a classic experience. Book ahead online."),
 ("thailand-7-day-itinerary-mid-range.html", "<tr><td>12Go</td><td>Book trains, buses, and ferries across Thailand</td>", "<tr><td>Transport booking app</td><td>Book trains, buses, and ferries across Thailand</td>"),
 ("thailand-travel-packing-guide-from-india.html", "<li><strong>Klook</strong> / GetYourGuide &mdash; Book day trips, island hopping, and activities at discounted rates</li>", "<li><strong>Tour booking apps</strong> &mdash; Book day trips, island hopping and activities ahead</li>"),
 ("thailand-travel-packing-guide-from-india.html", "install an eSIM through Airalo before you fly", "install an eSIM before you fly"),
 ("thailand-travel-packing-guide-from-india.html", "tours on <a href=\"https://klook.tpx.li/PFWXpnlR\" target=\"_blank\" rel=\"nofollow noopener sponsored\">Klook</a></td></tr>", "tours <a href=\"https://klook.tpx.li/PFWXpnlR\" target=\"_blank\" rel=\"nofollow noopener sponsored\">online</a> (partner link)</td></tr>"),
 ("uk-travel-packing-guide.html", "(an Airalo eSIM works well / $9-15)", "(an eSIM, $9-15)"),
 ("uk-travel-packing-guide.html", "<li><strong>Airalo:</strong> eSIM for data and calls", "<li><strong>eSIM:</strong> Data and calls"),
 ("uk-travel-packing-guide.html", "<li><strong>Trip.com or Skyscanner:</strong>", "<li><strong>Skyscanner:</strong>"),
 ("usa-travel-packing-guide.html", ">GetYourGuide offers Grand Canyon tours →</a>", ">Grand Canyon tours (partner link) →</a>"),
 ("vietnam-10-day-itinerary-mid-range.html", ">Book Hanoi street food tours &amp; Old Quarter walks</a> on GetYourGuide &mdash; local guides who know the best stalls.", ">Book Hanoi street food tours &amp; Old Quarter walks</a> (partner link)."),
 ("vietnam-10-day-itinerary-mid-range.html", ">Book Ha Long Bay overnight cruises</a> on GetYourGuide &mdash; hotel pickup, all meals included.", ">Book Ha Long Bay overnight cruises</a> (partner link)."),
 ("vietnam-10-day-itinerary-mid-range.html", ">Book Cu Chi Tunnels &amp; Mekong Delta tours</a> on GetYourGuide &mdash; hotel pickup and English guides included.", ">Book Cu Chi Tunnels &amp; Mekong Delta tours</a> (partner link)."),
 ("vietnam-10-day-itinerary-mid-range.html", "<tr><td>GetYourGuide</td><td>Book tours, cruises, and activities</td>", "<tr><td>Tour booking app</td><td>Book tours, cruises, and activities</td>"),
 ("vietnam-travel-packing-guide-from-india.html", "rel=\"nofollow noopener sponsored\">12Go Asia</a>).", "rel=\"nofollow noopener sponsored\">partner link</a>)."),
 ("flights.html", "Search and compare hotel deals from Trip.com — great prices worldwide.", "Search and compare hotel prices."),
 ("index.html", "Book tours, day trips, and experiences worldwide. Best price guarantee by GetYourGuide.", "Book tours, day trips, and experiences worldwide."),
]

NAMES = r"Airalo|GetYourGuide|Get Your Guide|Welcome Pickups|DiscoverCars|EconomyBookings|Radical Storage|Klook|KKday|Yesim|12Go|Trip\.com|Travelpayouts|Tiqets|Japan Bullet Train|Sakura Mobile"
ALLOWED = [r"Best Saily Alternatives 2026:[^.]{0,80}", r"Yesim vs Airalo vs Saily[^.]{0,40}",
           r"trusted booking platforms Agoda Trip\.com Kiwi\.com"]   # flights.html: the sources the search widget fetches


def die(msg):
    sys.exit("w66 aborted, nothing written: " + msg)


def visible(s):
    s = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", "", s, flags=re.S)
    attrs = " ".join(re.findall(r'(?:aria-label|alt|title)="([^"]*)"', s))
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s) + " " + attrs))


files = [f for f in sorted(glob.glob(os.path.join(PUB, "blog", "*.html"))) + sorted(glob.glob(os.path.join(PUB, "*.html")))
         if not os.path.basename(f).startswith(JP) and not f.endswith("-pocket.html") and os.path.basename(f) not in EXEMPT]
plans, used, now = {}, [0] * len(RULES), {}
for f in files:
    s = open(f, encoding="utf-8").read()
    o = s
    for i, (pat, rep, _) in enumerate(RULES):
        s, n = re.subn(pat, rep, s)
        used[i] += n
    now[f] = s
    if s != o:
        plans[f] = s
for f in files:
    b = os.path.basename(f)
    for (fb, old, new) in ONEOFFS:
        if fb != b:
            continue
        n = now[f].count(old)
        if n > 1 or (n == 0 and new not in now[f]):
            die("%s: one-off text found %d times: %r" % (b, n, old[:80]))
        if n == 1:
            now[f] = now[f].replace(old, new)
            plans[f] = now[f]
            used.append(1)
for i, (pat, rep, mark) in enumerate(RULES):
    if not used[i] and not any(mark in s for s in now.values()):
        die("rule %d matched nothing and is not already applied: %r" % (i, pat))

left = []
for f, s in now.items():
    t = visible(s)
    for a in ALLOWED:
        t = re.sub(a, "", t)
    for m in re.finditer(NAMES, t):
        left.append("%s: ...%s..." % (os.path.basename(f), t[max(0, m.start() - 70):m.end() + 50]))
if DRY:
    print("dry run: %d page(s) would change, %d substitution(s); %d name(s) left:" % (len(plans), sum(used), len(left)))
    print("\n".join(left))
    sys.exit(0)
if left:
    die("partner names still visible:\n  " + "\n  ".join(left))
for f, s in plans.items():
    open(f, "w", encoding="utf-8").write(s)
print("w66 done. %d page(s) changed, %d substitution(s)." % (len(plans), sum(used)))
