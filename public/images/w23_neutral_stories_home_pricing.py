#!/usr/bin/env python3
"""w23: neutral web stories (Vietnam, Thailand, Sri Lanka, Malaysia, Bali), homepage guide cards, and Pricing.

  * web stories: titles, meta, OG/Twitter, JSON-LD, amp-story title, slides and CTA made neutral; budgets in USD;
    visa slides written for all nationalities; Sri Lanka ETA corrected (free for 40 countries since 25 May 2026,
    otherwise ~US$50, official site eta.gov.lk); CTAs no longer point at India-designed guides
  * homepage: five India-designed guide cards replaced by neutral guides (UK, USA, South Korea, Australia, Canada)
  * pricing: INR price lines and the 'UPI payments for Indian customers' wording removed (text and FAQ JSON-LD)
  * sitemap lastmod bumped for the pages changed

Run from the repo root:  python3 public/images/w23_neutral_stories_home_pricing.py   (optional arg: repo root)
Idempotent. Everything is validated in memory first; nothing is written unless every edit matches exactly.
"""
import json, os, re, sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
PUB = os.path.join(ROOT, "public")
TODAY = "2026-11-16"
SITE = "https://www.packsmartapp.com"

class Err(Exception): pass

def R(old, new, n=1): return ("R", old, new, n)
def RX(pat, new, n=1): return ("RX", pat, new, n)

def apply(s, op):
    k = op[0]
    if k == "R":
        _, old, new, n = op
        c = s.count(old)
        if c == n: return s.replace(old, new)
        if c == 0 and s.count(new) >= 1: return s
        raise Err("R: %d matches (want %d) for %r" % (c, n, old[:80]))
    if k == "RX":
        _, pat, new, n = op
        rx = re.compile(pat, re.S); c = len(rx.findall(s))
        if c == n: return rx.sub(lambda m: new, s)
        if c == 0 and (new == "" or new in s): return s
        raise Err("RX: %d matches (want %d) for %r" % (c, n, pat[:80]))
    raise Err("unknown op")

def ld_ok(s, label):
    for m in re.finditer(r"<script[^>]+application/ld\+json[^>]*>(.*?)</script>", s, re.S | re.I):
        try: json.loads(m.group(1))
        except Exception as e: raise Err("%s: JSON-LD does not parse (%s)" % (label, e))

def rd(p): return open(p, encoding="utf-8").read()
def wr(p, s): open(p, "w", encoding="utf-8", newline="").write(s)

HL = lambda t: '<span class="highlight">%s</span>' % t

def story(slug, old_title, new_title, name, cover_old, cover_new, extra, cta):
    ops = [
        R(old_title, new_title, 5),
        R("Planning a trip to %s from India?" % name, "Planning a trip to %s?" % name),
        R(cover_old, cover_new),
        RX(r'"dateModified": "[^"]*"', '"dateModified": "%s"' % TODAY),
    ] + extra + cta
    return ops

CTA_HOME = [R('<a href="https://www.packsmartapp.com/blog/%s-travel-packing-guide-from-india" class="cta-btn">Read the Full Guide</a>',
              '<a href="https://www.packsmartapp.com/" class="cta-btn">Build Your Packing List</a>')]
def cta_home(slug):
    return [R('<a href="%s/blog/%s-travel-packing-guide-from-india" class="cta-btn">Read the Full Guide</a>' % (SITE, slug),
              '<a href="%s/" class="cta-btn">Build Your Packing List</a>' % SITE)]
def cta_itin(slug, itin, name):
    return [R('<a href="%s/blog/%s-travel-packing-guide-from-india" class="cta-btn">Read the Full Guide</a>' % (SITE, slug),
              '<a href="%s/blog/%s" class="cta-btn">Read the Itinerary</a>' % (SITE, itin)),
            R('Get Your Full <span>%s Packing List</span>' % name, 'Plan Your <span>%s Trip</span>' % name),
            R('Personalized checklist, visa info, weather tips, and city guides — all in one place.',
              'Day-by-day itinerary, costs, transport tips, and where to stay — all in one place.')]

STORIES = {
 "thailand": story("thailand",
    "Thailand Travel Guide 2026: 7 Things Indian Travelers Must Know", "Thailand Travel Guide 2026: 7 Things Every Traveler Should Know", "Thailand",
    "7 things every Indian traveler needs to know", "7 things every traveler needs to know",
    [R("Visa-free entry, ₹35K budget trips, and the best time to visit Thailand — swipe through our quick guide.",
       "Visa-free entry for many nationalities, budget trips from about US$400, and the best time to visit Thailand — swipe through our quick guide."),
     R("Visa-free entry, ₹35K budget trips, and the best time to visit Thailand.",
       "Visa-free entry for many nationalities, trips from about US$400, and the best time to visit Thailand."),
     R("Indian passport holders get %s (cut from 60 on 15 Sept 2026). Bring a return ticket and file the free arrival card online." % HL("30 days visa-free"),
       "Visitors from many countries get %s (cut from 60 on 15 Sept 2026). Check the rule for your passport, bring a return ticket and file the free arrival card online." % HL("30 days visa-free")),
     R("₹35,000–55,000 for 7 Days", "US$400–650 for 7 Days"),
     R("Street food runs %s. Thailand is one of the most affordable destinations from India." % HL("₹100–200 per meal"),
       "Street food runs %s. Thailand is one of the most affordable destinations in Southeast Asia." % HL("US$1–2.50 per meal")),
     R("Laundry costs just %s." % HL("₹95–145 per kg"), "Laundry costs just %s." % HL("US$1–2 per kg"))],
    cta_itin("thailand", "thailand-7-day-itinerary-mid-range", "Thailand")),
 "vietnam": story("vietnam",
    "Vietnam Travel Guide 2026: 7 Essentials for Indian Travelers", "Vietnam Travel Guide 2026: 7 Essentials for First-Time Visitors", "Vietnam",
    "7 essentials every Indian traveler needs", "7 essentials every first-time visitor needs",
    [R("E-Visa $25–50, ₹30K–50K budget trips, and the best time to visit Vietnam — swipe through our quick guide.",
       "E-Visa $25–50, budget trips from about US$350, and the best time to visit Vietnam — swipe through our quick guide."),
     R("E-Visa $25–50, ₹30K–50K budget trips, and the best time to visit Vietnam.",
       "E-Visa $25–50, budget trips from about US$350, and the best time to visit Vietnam."),
     R("Apply on %s for %s. Single entry approved within %s." % (HL("evisa.gov.vn"), HL("$25–50"), HL("24 hours online")),
       "If you need a visa, apply on %s for %s. Many nationalities are visa-exempt, so check yours. Processing usually takes about 3 working days, so apply early." % (HL("evisa.gov.vn"), HL("$25–50"))),
     R("₹30,000–50,000 for 10 Days", "US$350–600 for 10 Days"),
     R("Street food costs %s." % HL("₹50–150"), "Street food costs %s." % HL("US$1–2")),
     R("pho runs just ₹60–100.", "pho runs just US$1–1.50.")],
    cta_itin("vietnam", "vietnam-10-day-itinerary-mid-range", "Vietnam")),
 "sri-lanka": story("sri-lanka",
    "Sri Lanka Travel Guide 2026: 7 Things Indian Travelers Must Know", "Sri Lanka Travel Guide 2026: 7 Things Every Traveler Should Know", "Sri Lanka",
    "7 things every Indian traveler must know", "7 things every traveler must know",
    [R("ETA $35, ₹25K–40K budget trips, and the cheapest SE Asia destination — swipe through our quick Sri Lanka guide.",
       "Free ETA for 40 countries, budget trips from about US$300, and one of Asia's cheapest destinations — swipe through our quick Sri Lanka guide."),
     R("ETA $35, ₹25K–40K budget trips, and the cheapest SE Asia destination.",
       "Free ETA for 40 countries, budget trips from about US$300, and one of Asia's cheapest destinations."),
     R("ETA Online ($35)", "ETA Online (Free or $50)"),
     R("Apply at %s for just %s. Approved within %s. Print and carry it with your passport." % (HL("eTouristVisa.com"), HL("USD $35"), HL("24 hours")),
       "Apply only on the official site, %s. Free for nationals of %s since 25 May 2026, otherwise about %s. Usually approved within hours, but allow up to 72. Print and carry it with your passport." % (HL("eta.gov.lk"), HL("40 countries"), HL("US$50"))),
     R("₹25,000–40,000 for 7 Days", "US$300–470 for 7 Days"),
     R("%s. Flights from India: ₹8,000–15,000. Stay for ₹600–1,500/night. Meals: ₹100–200." % HL("Cheapest SE Asia destination"),
       "%s. Stay for US$7–18/night. Meals: US$1–2.50." % HL("One of Asia's cheapest destinations")),
     R("LKR 400–1,000/kg (₹130–330)", "LKR 400–1,000/kg (about US$1.30–3.30)"),
     R("Reserved seats: %s." % HL("₹500–830"), "Reserved seats: %s." % HL("US$6–10"))],
    cta_home("sri-lanka")),
 "malaysia": story("malaysia",
    "Malaysia Travel Guide 2026: 7 Tips for Indian Travelers", "Malaysia Travel Guide 2026: 7 Tips for First-Time Visitors", "Malaysia",
    "7 tips every Indian traveler needs to know", "7 tips every traveler needs to know",
    [R("30-day visa-free entry, ₹30K–50K budget trips, and amazing street food — swipe through our quick Malaysia guide.",
       "Visa-free entry for many nationalities, budget trips from about US$350, and amazing street food — swipe through our quick Malaysia guide."),
     R("30-day visa-free entry, ₹30K–50K budget trips, and amazing street food.",
       "Visa-free entry for many nationalities, trips from about US$350, and amazing street food."),
     R("30 Days Visa-Free", "Visa-Free for Many Nationalities"),
     R("%s for stays up to %s, valid until 31 Dec 2026. File the free %s online within 3 days before you land." % (HL("No visa fee"), HL("30 days"), HL("MDAC arrival card")),
       "%s for many nationalities, with stays of %s depending on your passport. File the free %s online within 3 days before you land." % (HL("No visa fee"), HL("30 to 90 days"), HL("MDAC arrival card"))),
     R("₹30,000–50,000 for 7 Days", "US$350–600 for 7 Days"),
     R("Meals cost %s." % HL("₹100–250"), "Meals cost %s." % HL("US$1–3")),
     R("MYR 5–10 (₹95–190)", "MYR 5–10 (about US$1–2.50)")],
    cta_home("malaysia")),
 "bali": story("bali",
    "Bali Travel Guide 2026: 7 Tips for Indian Travelers", "Bali Travel Guide 2026: 7 Tips for First-Time Visitors", "Bali",
    "7 tips every Indian traveler needs to know", "7 tips every traveler needs to know",
    [R("Visa-on-arrival, ₹50K–80K budget trips, and the best time to visit Bali — swipe through our quick guide.",
       "Visa-on-arrival, budget trips from about US$600, and the best time to visit Bali — swipe through our quick guide."),
     R("Visa-on-arrival, ₹50K–80K budget trips, and the best time to visit Bali.",
       "Visa-on-arrival, budget trips from about US$600, and the best time to visit Bali."),
     R("Get your visa at the airport for %s. Single entry, %s." % (HL("IDR 500,000 (₹2,700)"), HL("30 days extendable to 60")),
       "Many nationalities get their visa at the airport for %s. Single entry, %s. Some countries must apply in advance, so check yours." % (HL("IDR 500,000 (about US$30)"), HL("30 days extendable to 60"))),
     R("₹50,000–80,000 for 7 Days", "US$600–950 for 7 Days"),
     R("Meals run %s." % HL("₹150–500 per plate"), "Meals run %s." % HL("US$2–6 per plate")),
     R("from ₹1,500–3,000/night", "from US$18–35/night"),
     R("Rent sarongs locally for %s" % HL("₹150–400"), "Rent sarongs locally for %s" % HL("US$2–5"))],
    cta_itin("bali", "bali-10-day-itinerary-mid-range", "Bali")),
}

# ---- homepage cards
def card(ind, href, img, alt, tag, h3, desc):
    return ('{i}<a href="{h}" class="guide-card">\n{i}    <img src="https://images.unsplash.com/{im}?w=600&h=340&fit=crop&auto=format&q=75" width="600" height="340" alt="{a}" loading="lazy">\n'
            '{i}    <div class="guide-card-body">\n{i}        <span class="gc-tag">{t}</span>\n{i}        <h3>{h3}</h3>\n{i}        <p class="gc-desc">{d}</p>\n'
            '{i}        <span class="gc-link">Read guide &rarr;</span>\n{i}    </div>\n{i}</a>').format(i=ind, h=href, im=img, a=alt, t=tag, h3=h3, d=desc)

HOME_SWAPS = [
 ("/blog/schengen-visa-guide-for-indians", "/blog/uk-travel-packing-guide", "photo-1513635269975-59663e0ac1ad", "UK — London travel guide",
  "Destination Guide", "UK Travel &amp; Packing Guide 2026", "London, Edinburgh, Manchester. ETA and visa rules, seasonal packing, city guides and budget."),
 ("/blog/baku-azerbaijan-from-india", "/blog/usa-travel-packing-guide", "photo-1501594907352-04cda38ebc29", "USA — travel guide",
  "Destination Guide", "USA Travel &amp; Packing Guide 2026", "NYC, LA, San Francisco. Visa and ESTA rules, tipping culture, voltage and budget tips."),
 ("/blog/bali-travel-packing-guide-from-india", "/blog/south-korea-travel-packing-guide", "photo-1517154421773-0529f29ea451", "South Korea — Seoul travel guide",
  "Destination Guide", "South Korea Travel &amp; Packing Guide 2026", "Seoul, Busan, Jeju. K-ETA rules, seasonal packing, K-drama locations and etiquette."),
 ("/blog/thailand-travel-packing-guide-from-india", "/blog/australia-travel-packing-guide", "photo-1506973035872-a4ec16b8e8d9", "Australia — travel guide",
  "Destination Guide", "Australia Travel &amp; Packing Guide 2026", "Sydney, Melbourne, Great Barrier Reef. Visa rules, biosecurity, seasonal packing and budget."),
 ("/blog/dubai-travel-packing-guide-from-india", "/blog/canada-travel-packing-guide", "photo-1517935706615-2717063c2225", "Canada — travel guide",
  "Destination Guide", "Canada Travel &amp; Packing Guide 2026", "Vancouver, Toronto, Banff. eTA and visa rules, extreme-cold packing and city guides."),
]
def home_ops(s):
    for old, new, img, alt, tag, h3, desc in HOME_SWAPS:
        rx = re.compile(r'(?P<i>[ \t]*)<a href="%s" class="guide-card">.*?</a>' % re.escape(old), re.S)
        c = len(rx.findall(s))
        if c == 1:
            s = rx.sub(lambda m: card(m.group("i"), new, img, alt, tag, h3, desc), s, count=1)
        elif c == 0 and ('<a href="%s" class="guide-card">' % new) in s: pass
        else: raise Err("homepage card for %s: %d matches" % (old, c))
    return s

# ---- pricing
PRICING = [
    RX(r'[ \t]*<div class="price-alt">₹[^<]*</div>\n', "", 5),
    R("We accept all major credit cards (Visa, Mastercard, American Express), PayPal, and UPI payments for Indian customers.",
      "We accept all major credit cards (Visa, Mastercard, American Express) and PayPal.", 2),
]

# ---- plan
final = {}
for slug, ops in STORIES.items():
    p = os.path.join(PUB, "web-stories", "%s-travel-guide.html" % slug)
    s = rd(p)
    try:
        for op in ops: s = apply(s, op)
        ld_ok(s, slug)
        assert "amp-story-page" in s and s.count("<amp-story-page") == rd(p).count("<amp-story-page"), "slide count changed"
    except (Err, AssertionError) as e:
        print("ABORT %s: %s" % (slug, e)); sys.exit(1)
    final[p] = s

p = os.path.join(PUB, "index.html"); s = rd(p)
try:
    n_cards = s.count('class="guide-card"'); s = home_ops(s); ld_ok(s, "index")
    assert s.count('class="guide-card"') == n_cards, "guide-card count changed"
except (Err, AssertionError) as e: print("ABORT index: %s" % e); sys.exit(1)
final[p] = s

p = os.path.join(PUB, "pricing.html"); s = rd(p)
try:
    for op in PRICING: s = apply(s, op)
    ld_ok(s, "pricing")
except Err as e: print("ABORT pricing: %s" % e); sys.exit(1)
final[p] = s

# sitemap lastmod
sp = os.path.join(PUB, "sitemap.xml"); sm = rd(sp)
for loc in ["/", "/pricing"] + ["/web-stories/%s-travel-guide" % k for k in STORIES]:
    url = SITE + (loc if loc != "/" else "")
    rx = re.compile(r"(<loc>%s/?</loc>\s*<lastmod>)[^<]*(</lastmod>)" % re.escape(url))
    if rx.search(sm): sm = rx.sub(lambda m: m.group(1) + TODAY + m.group(2), sm, count=1)
final[sp] = sm

# ---- scan
NEUT = re.compile(r"\bIndia(?:n|ns)?\b|\bINR\b|₹|&#8377;|\bRs\.?\s?\d|\brupees?\b|\blakhs?\b|Delhi|Mumbai|Bangalore|Chennai|Kolkata|Aadhaar|\bUPI\b|VFS|\bBLS\b", re.I)
report = []
for p, s in final.items():
    if p == sp: continue
    t = re.sub(r"<[^>]*>", " ", re.sub(r"<style.*?</style>|<script(?![^>]*ld\+json).*?</script>", " ", s, flags=re.S))
    hits = [re.sub(r"\s+", " ", t[max(0, m.start() - 40): m.end() + 40]) for m in NEUT.finditer(t)]
    report.append((os.path.relpath(p, ROOT), hits))

changed = 0
for p, s in final.items():
    if rd(p) == s: continue
    wr(p, s); changed += 1
print("w23: %d file(s) written" % changed)
for name, hits in report:
    print("  %-40s India-term hits left: %d" % (name, len(hits)))
    for h in hits[:8]: print("      ...%s..." % h)
