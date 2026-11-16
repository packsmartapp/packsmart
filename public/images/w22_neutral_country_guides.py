#!/usr/bin/env python3
"""w22: make six country guides neutral (no 'from India' framing) and move them to neutral URLs.

Pages: Canada, USA, Australia, South Korea, UK, New Zealand.
  * title, meta description/keywords, Open Graph, Twitter and JSON-LD (Article headline, FAQ) made neutral
  * body copy and FAQ answers rewritten for all nationalities (visa text, driving licence, budgets in USD, etc.)
  * India-designed related cards and 'visa-free for Indians' boxes removed or swapped for neutral ones
  * files renamed  <country>-travel-packing-guide-from-india.html  ->  <country>-travel-packing-guide.html
  * every link, canonical, og:url, share link and sitemap entry follows the new slug
  * vercel.json: 301 redirects old -> new (with and without .html); existing redirects retargeted to the new USA slug

Run from the repo root:   python3 public/images/w22_neutral_country_guides.py   (optional arg: repo root)
Idempotent. Everything is validated in memory first; nothing is written unless every edit matches exactly.
"""
import json, os, re, sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
BLOG = os.path.join(ROOT, "public", "blog")
BLOG_INDEX = os.path.join(ROOT, "public", "blog.html")
SITEMAP = os.path.join(ROOT, "public", "sitemap.xml")
VERCEL = os.path.join(ROOT, "vercel.json")
TODAY = "2026-11-16"
SITE = "https://www.packsmartapp.com"

SLUGS = ["canada", "usa", "australia", "south-korea", "uk", "new-zealand"]
def old_slug(c): return "%s-travel-packing-guide-from-india" % c
def new_slug(c): return "%s-travel-packing-guide" % c

# ------------------------------------------------------------------ edit operations
class Err(Exception): pass

def R(old, new, n=1):       return ("R", old, new, n)
def RX(pat, new, n=1):      return ("RX", pat, new, n)
def CUT(pat, marker):       return ("CUT", pat, marker)
def FAQ(mapping):           return ("FAQ", mapping)
def CARD(old_href, h4, p, href, tag=None): return ("CARD", old_href, (h4, p, href, tag))

def apply(s, op):
    k = op[0]
    if k == "R":
        _, old, new, n = op
        c = s.count(old)
        if c == n: return s.replace(old, new)
        if c == 0 and new in s: return s
        raise Err("R: %d matches (want %d) for %r" % (c, n, old[:70]))
    if k == "RX":
        _, pat, new, n = op
        rx = re.compile(pat); c = len(rx.findall(s))
        if c == n: return rx.sub(lambda m: new, s)
        if c == 0 and new in s: return s
        raise Err("RX: %d matches (want %d) for %r" % (c, n, pat[:70]))
    if k == "CUT":
        _, pat, marker = op
        rx = re.compile(pat); c = len(rx.findall(s))
        if c == 1: return rx.sub("", s, count=1)
        if c == 0 and marker not in s: return s
        raise Err("CUT: %d matches for %r" % (c, pat[:70]))
    if k == "CARD":
        _, old_href, (h4, p, href, tag) = op
        rx = re.compile(r'(<h4>)[^<]*(</h4>\s*<p>)[^<]*(</p>\s*<a href=")' + re.escape(old_href) +
                        r'(")(.{0,260}?<div class="related-tag">)([^<]*)(</div>)', re.S)
        c = len(rx.findall(s))
        if c == 1:
            return rx.sub(lambda m: "%s%s%s%s%s%s%s%s%s%s" % (m.group(1), h4, m.group(2), p, m.group(3), href, m.group(4), m.group(5), tag if tag else m.group(6), m.group(7)), s, count=1)
        if c == 0 and ('<a href="%s"' % href) in s: return s
        raise Err("CARD: %d matches for %s" % (c, old_href))
    if k == "FAQ":
        mapping = op[1]
        for m in re.finditer(r'(<script[^>]+application/ld\+json[^>]*>)(.*?)(</script>)', s, re.S | re.I):
            try: j = json.loads(m.group(2))
            except Exception: continue
            if j.get("@type") != "FAQPage": continue
            raw = m.group(2); lead = re.match(r"\s*", raw).group(0); tail = re.search(r"\s*$", raw).group(0)
            changed = False
            for q in j["mainEntity"]:
                name = q["name"]
                if name in mapping:
                    nq, na = mapping[name]
                    q["name"] = nq
                    if na is not None: q["acceptedAnswer"]["text"] = na
                    changed = True
            if not changed: return s            # already done
            body = raw.strip()
            compact = json.dumps(json.loads(body), ensure_ascii=False, separators=(",", ":"))
            spaced = json.dumps(json.loads(body), ensure_ascii=False)
            pretty = json.dumps(json.loads(body), ensure_ascii=False, indent=2)
            if body == compact: out = json.dumps(j, ensure_ascii=False, separators=(",", ":"))
            elif body == spaced: out = json.dumps(j, ensure_ascii=False)
            elif body == pretty: out = json.dumps(j, ensure_ascii=False, indent=2)
            else: raise Err("FAQ JSON-LD formatting not recognised")
            return s[:m.start(2)] + lead + out + tail + s[m.end(2):]
        return s
    raise Err("unknown op " + k)

# ------------------------------------------------------------------ head setters
def set_title(s, t):
    rx = re.compile(r"<title>[^<]*</title>")
    if len(rx.findall(s)) != 1: raise Err("title count")
    return rx.sub(lambda m: "<title>%s</title>" % t, s)

def set_meta(s, attr, name, content):
    rx = re.compile(r'(<meta %s="%s" content=")[^"]*(")' % (attr, re.escape(name)))
    if len(rx.findall(s)) != 1: raise Err("meta %s count %d" % (name, len(rx.findall(s))))
    return rx.sub(lambda m: m.group(1) + content + m.group(2), s)

def set_headline(s, headline):
    rx = re.compile(r'("headline":\s*")[^"]*(")')
    if len(rx.findall(s)) != 1: raise Err("headline count %d" % len(rx.findall(s)))
    return rx.sub(lambda m: m.group(1) + headline + m.group(2), s)

def set_modified(s):
    rx = re.compile(r'("dateModified":\s*")[^"]*(")')
    n = len(rx.findall(s))
    if n > 1: raise Err("dateModified count %d" % n)
    return rx.sub(lambda m: m.group(1) + TODAY + m.group(2), s) if n == 1 else s

# ------------------------------------------------------------------ per-page content
BOX_VISA_FREE = r'[ \t]*<p [^>]*>Check which countries you can visit without a visa in our <a href="/blog/visa-free-countries-indian-passport"[^>]*>[^<]*</a>\.</p>\n'
def uk_link_old(): return '<a href="/blog/uk-travel-packing-guide-from-india" style="color:#00C9A7;text-decoration:underline;">UK from India guide</a>'
def uk_link_new(): return '<a href="/blog/uk-travel-packing-guide" style="color:#00C9A7;text-decoration:underline;">UK Travel &amp; Packing Guide</a>'

JAPAN_CARD = ("Japan Travel &amp; Packing Guide 2026",
              "Complete Japan packing list with visa tips, JR Pass guide, weather by season, and cultural etiquette for Tokyo, Kyoto, and Osaka.",
              SITE + "/blog/japan-travel-packing-guide", None)

SK_VISA_Q_OLD = "Do Indians need a visa for South Korea?"
SK_VISA_Q_NEW = "Do I need a visa for South Korea?"
SK_VISA_A = ("Entry rules depend on your nationality. Many nationalities can visit South Korea visa-free for tourism, but visitors from visa-free "
             "countries normally need a K-ETA (Korea Electronic Travel Authorization) before they fly: it costs KRW 10,000 (about US$7), is valid for "
             "3 years, and is applied for online at https://www.k-eta.go.kr. Travellers from many countries (including the US, Canada, the UK, Australia, "
             "New Zealand and Japan) are temporarily exempt from the K-ETA until 31 December 2026 and complete the online e-Arrival Card instead. "
             "Citizens of other countries need a visa from a South Korean embassy or consulate. Check the K-ETA portal for your passport.")
SK_BEST_A = ("Spring (March-May) with cherry blossoms and mild weather is ideal. Fall (September-November) with beautiful foliage is equally stunning. "
             "Summer (June-August) is hot and humid with monsoon rains. Winter (December-February) brings snow and cold (-10°C in Seoul) but offers "
             "excellent skiing in Pyeongchang and fewer tourists.")
SK_COST_A = ("A 7-day South Korea trip costs approximately US$300-700 per person on a budget and US$950-1,800 for mid-range, excluding flights. "
             "South Korea is affordable, with street food and casual meals at US$3-10, hostel dorm beds from about US$20 per night, and excellent public "
             "transport. Food and accommodation are cheaper outside Seoul and Busan.")

UK_ETA_PARA = ("<p>The United Kingdom is outside the European Union and has its own visa system. Visa requirements vary by nationality. Visitors from "
               "visa-exempt countries (including the US, Canada, Australia, New Zealand, Japan, and EU countries) don't need a visa for stays of up to "
               "6 months, but since 25 February 2026 they must hold an Electronic Travel Authorisation (ETA) before they travel (£20, valid for 2 years, "
               "applied for through the UK ETA app or GOV.UK). Citizens of other countries need a Standard Visitor Visa to enter the UK for tourism purposes.</p>")
UK_FAQ_A = ("Visa requirements depend on your nationality. Visitors from visa-exempt countries (including the US, Canada, Australia, New Zealand, Japan, "
            "and EU countries) don't need a visa for stays of up to 6 months, but must hold a UK Electronic Travel Authorisation (ETA) before travelling: "
            "it costs £20 and is valid for 2 years. For other nationalities, a Standard Visitor Visa is required, costing £135 (about $170 USD) and "
            "allowing stays of up to 6 months. The application process requires biometric submission and takes 15-20 working days.")

PAGES = {
 "canada": {
   "title": "Canada Travel & Packing Guide 2026: Visa, Costs & Checklist | PackSmart",
   "desc": "Complete Canada travel and packing guide for 2026: visa and eTA rules by nationality, weather and what to pack by season, Toronto, Vancouver and Banff tips, budget breakdown, and a pre-departure checklist.",
   "kw": "Canada packing list, what to pack for Canada, Canada travel guide, Canada visa requirements, Canada eTA, Toronto checklist, Banff travel, Canada weather, Canada budget, Canada winter packing",
   "ops": [
     R("Indian citizens and most other nationalities need a <strong>Canadian", "Citizens of most other countries need a <strong>Canadian"),
     R("Canada drives on the right, the opposite of India.", "Canada drives on the right."),
     R("Carry your Indian licence with an International Driving Permit and check the rental company's licence rules before you book.",
       "Carry your home driving licence plus an International Driving Permit if it is not in English or French, and check the rental company's licence rules before you book."),
     R("See our " + uk_link_old() + " for the visa, costs and packing.", "See our " + uk_link_new() + " for the visa, costs and packing."),
     R("Indian and most other nationalities: Canadian Temporary Resident Visa (TRV) via IRCC.", "Citizens of most other countries: Canadian Temporary Resident Visa (TRV) via IRCC."),
     R("Indian and most other nationalities: Canadian Temporary Resident Visa (TRV). Apply via IRCC.", "Citizens of most other countries: Canadian Temporary Resident Visa (TRV). Apply via IRCC."),
   ]},
 "usa": {
   "title": "USA Travel & Packing Guide 2026: Visa, ESTA, Costs & Checklist | PackSmart",
   "desc": "Complete USA travel and packing guide for 2026: visa and ESTA rules by nationality, best time to visit, what to pack by season, etiquette, budget breakdown, SIM options and city tips.",
   "kw": "usa packing guide, USA travel, American visa, ESTA, usa trip cost, packing list USA, what to pack for USA, USA travel checklist",
   "ops": [
     R("Citizens of India and many other countries require a B-1/B-2 Tourist Visa through the US Embassy/Consulate.", "Citizens of many other countries require a B-1/B-2 Tourist Visa through the US Embassy/Consulate."),
     R("Interview appointment waits in India are currently about 6 to 12 months for first-time B-1/B-2 applicants, depending on the city, so apply as early as you can. The visa validity varies by country (usually 10 years for Indians).",
       "Interview appointment waits vary widely by country and consulate (some run to many months), so check the wait-times tool on travel.state.gov and apply as early as you can. The visa validity varies by country."),
     R("<strong>B-1/B-2 Visa Required:</strong> India, China, Russia, Brazil, and many other countries require", "<strong>B-1/B-2 Visa Required:</strong> China, Russia, Brazil, and many other countries require"),
     RX(r"Currently about 6 to 12 months for first-time B-1/B-2 interviews in India[^\n]*?plan well before you buy flights",
        "Wait times for first-time B-1/B-2 interviews vary widely by country and city and can run to many months (check the wait-times tool on travel.state.gov, as it changes often). Book the earliest slot available and plan well before you buy flights"),
     CUT(BOX_VISA_FREE, "visa-free-countries-indian-passport"),
     R("See our " + uk_link_old() + " for the visa, costs and packing.", "See our " + uk_link_new() + " for the visa, costs and packing."),
     R("Most flights from Asia (India, China, Japan) to USA are 15-18 hours.", "Flights from Asia to the USA typically take 11-18 hours, depending on the departure city."),
   ]},
 "australia": {
   "title": "Australia Travel & Packing Guide 2026: Visa, Costs & Checklist | PackSmart",
   "desc": "Complete Australia travel and packing guide for 2026: visa and ETA rules by nationality, best time to visit, what to pack by season, biosecurity rules, budget breakdown, SIM cards and city tips for Sydney and Melbourne.",
   "kw": "Australia packing list, Australia travel guide, tourist visa Australia, Sydney travel checklist, Great Barrier Reef, Melbourne packing, Australia travel cost, Australian biosecurity, travel insurance Australia",
   "ops": [
     R("Citizens of India and many other countries require a subclass 600 Tourist Visa, applied online", "Citizens of many other countries require a subclass 600 Tourist Visa, applied online"),
     R("Citizens of India and many other countries must apply for the", "Citizens of many other countries must apply for the"),
     R("Australia drives on the left, like India.", "Australia drives on the left."),
     R("Carry your Indian driving licence plus an International Driving Permit, and check", "Carry your home driving licence plus an International Driving Permit if it is not in English, and check"),
     R("Book flights (Delhi/Mumbai/Bangalore to Sydney)", "Book international flights"),
     CARD(SITE + "/blog/bali-travel-packing-guide-from-india", *JAPAN_CARD),
   ]},
 "new-zealand": {
   "title": "New Zealand Travel & Packing Guide 2026: Visa, Costs & Checklist | PackSmart",
   "desc": "Complete New Zealand travel and packing guide for 2026: visa and NZeTA rules by nationality, best time to visit, what to pack by season, biosecurity rules, budget breakdown and South Island driving tips.",
   "kw": "New Zealand packing list, NZ travel guide, what to pack for New Zealand, NZ visa requirements, NZeTA, best time to visit New Zealand, New Zealand biosecurity",
   "ops": [
     R("Indian citizens and most other nationalities require a visitor visa;", "Citizens of most other countries require a visitor visa;", n=2),
     R("New Zealand drives on the left, like India, but roads are narrow and winding", "New Zealand drives on the left, and roads are narrow and winding"),
     R("Carry your Indian licence with an International Driving Permit and check the rental company's licence rules before you book.",
       "Carry your home licence plus an International Driving Permit if it is not in English, and check the rental company's licence rules before you book."),
     R("Complete Australia packing guide for Indian travelers with tips for Sydney, Melbourne, and the Great Barrier Reef.", "Complete Australia packing guide with tips for Sydney, Melbourne, and the Great Barrier Reef."),
     CARD(SITE + "/blog/bali-travel-packing-guide-from-india", "Canada Travel &amp; Packing Guide 2026",
          "Complete Canada packing guide with city-specific tips for Toronto, Vancouver, and Niagara Falls.", SITE + "/blog/canada-travel-packing-guide", None),
   ]},
 "uk": {
   "title": "UK Travel & Packing Guide 2026: ETA, Visa, Costs & Checklist | PackSmart",
   "desc": "Complete UK travel and packing guide for 2026: ETA and visa rules by nationality, best time to visit, what to pack by season, London, Edinburgh and Manchester city guides, food, transport and budget breakdown.",
   "kw": "UK packing guide, what to pack for UK, UK travel tips, UK ETA, London Edinburgh Manchester packing, UK travel checklist, UK trip budget, Spring Summer Fall Winter UK packing",
   "ops": [
     CUT(BOX_VISA_FREE, "visa-free-countries-indian-passport"),
     RX(r"<p>The United Kingdom is outside the European Union and has its own visa system\.[^\n]*</p>", UK_ETA_PARA),
     FAQ({"Do I need a visa for the UK?": ("Do I need a visa for the UK?", UK_FAQ_A)}),
     R("£127 (~$160 USD) for online application", "£135 (about $170 USD) for online application"),
     R("Must visit a visa application centre in India for biometric enrolment", "Must visit a visa application centre in your country of residence for biometric enrolment"),
     R("Direct compliments are less common than in India", "Direct compliments are less common than in many countries"),
     R("Rechargeable smart card (like Delhi Metro).", "Rechargeable smart card for London's Tube, buses and trams."),
     R("(the same as in India)", "(as in Australia, New Zealand and Japan)"),
     R("<h3>Indian Food Scene in the UK</h3>", "<h3>Curry &amp; Indian Food in the UK</h3>"),
     R("The UK is a paradise for Indian food lovers! With over 8,000 Indian restaurants across the country, you'll never miss home food.",
       "Curry is a British favourite, and the UK has thousands of Indian restaurants, so excellent vegetarian and spice-forward food is easy to find in almost any city."),
     R("British Indian cuisine is different from Indian food in India (more creamier, sweeter curries for local taste). But authentic Indian restaurants exist too",
       "British Indian cuisine has its own style (often creamier, milder curries adapted to local taste), but authentic regional Indian restaurants exist too"),
     R("Cozier than bars in India", "Often cosier than a typical bar"),
     R("(cold beer, familiar to Indians)", "(cold beer, familiar almost everywhere)"),
     R("Less important than in India but growing.", "Tea is the traditional hot drink, but coffee culture is growing."),
     R("Daily hygiene; Indian brands hard to find in UK", "Daily hygiene; some favourite brands from home may be hard to find in the UK"),
     R("UK water can be harsh on skin; different climate than India", "UK water is hard in many areas and can be harsh on skin and hair"),
     R("CRITICAL. UK uses Type G: 3 rectangular pins, 230V/50Hz. India uses Type A/D/M", "CRITICAL. UK uses Type G: 3 rectangular pins, 230V/50Hz. Plugs from most other countries will not fit"),
     R("Phone numbers (Indian embassy, travel insurance, home country)", "Phone numbers (your embassy or consulate, travel insurance, home country)"),
     R("UK uses 230V/50Hz (India uses 220V/50Hz — usually compatible). Most electronics auto-convert. Use adapter for plugs",
       "UK uses 230V/50Hz. Most phone and laptop chargers are dual-voltage (100-240V) and work fine; devices rated for 110V only need a voltage converter. Use an adapter for plugs"),
   ]},
 "south-korea": {
   "title": "South Korea Travel & Packing Guide 2026: K-ETA, Costs & Checklist | PackSmart",
   "desc": "Complete South Korea travel and packing guide for 2026: K-ETA and visa rules by nationality, what to pack for Seoul, Busan and Jeju, weather by season, budget in USD and Korean etiquette.",
   "kw": "South Korea packing list, what to pack for South Korea, South Korea travel guide, K-ETA, Seoul packing list, Busan checklist, South Korea budget, South Korea travel checklist, K-drama locations Korea",
   "ops": [
     RX(r"<p>South Korea is India's hidden travel gem[^\n]*</p>",
        "<p>South Korea is one of Asia's most rewarding destinations &mdash; K-pop idols, DMZ intrigue, cherry blossoms in spring, and one of the world's most efficient transportation systems. "
        "Whether it's temple stays in the mountains, K-drama filming locations in Seoul, or powder snow skiing in winter, South Korea is easy to visit, with a simple online entry process for many nationalities. "
        "Direct flights connect Seoul with major cities across Asia, Europe, North America and Oceania, and affordable accommodation, world-class food, and cutting-edge technology make it an ideal destination.</p>"),
     RX(r"<p>This is a South Korea packing guide built specifically for Indian travelers[^\n]*</p>",
        "<p>This South Korea packing guide covers the entry process (including the K-ETA), seasonal weather patterns, city-specific tips for Seoul, Busan, and Jeju Island, and exactly what to pack (and what to leave behind). Everything you need to know for your Korean adventure.</p>"),
     R("Visa & Entry Requirements for Indians</h2>", "Visa & Entry Requirements by Nationality</h2>"),
     RX(r"<p>Great news: Indians don't need a traditional visa for South Korea\.[^\n]*</p>",
        "<p>Entry rules depend on your nationality. Many nationalities can visit South Korea visa-free for tourism, but visitors from visa-free countries normally need a <strong>K-ETA (Korea Electronic Travel Authorization)</strong> &mdash; an online travel permit valid for 3 years. "
        "Travellers from many countries (including the US, Canada, the UK, Australia, New Zealand and Japan) are temporarily exempt from the K-ETA until 31 December 2026 and complete the online e-Arrival Card instead. "
        "Citizens of other countries need a visa from a South Korean embassy or consulate. Check the K-ETA portal for your passport. Here's what you need at immigration:</p>"),
     R("Takes 5 minutes. Cost: ~₹600 (approximately $10 USD). Valid for 2 years from issuance",
       "Takes about 5 minutes. Cost: KRW 10,000 (about US$7). Valid for 3 years from issuance. Not needed if your nationality is on the temporary exemption list (until 31 December 2026), but then you must complete the e-Arrival Card"),
     R("KRW 2,000,000 (~₹1,20,000) equivalent", "KRW 2,000,000 (about US$1,500) equivalent"),
     R("<strong>&#x1F4A1; Pro Tip:</strong> Apply for K-ETA at least", "<strong>&#x1F4A1; Pro Tip:</strong> If you need a K-ETA, apply at least"),
     R("during its 2-year validity period", "during its 3-year validity period"),
     RX(r"K-ETA is NOT a visa\. It's an authorization to enter South Korea\.[^\n]*",
        "K-ETA is NOT a visa. It's an authorization to enter South Korea. Stay lengths for visa-free entry vary by nationality (commonly up to 90 days per entry). If you need to stay longer, or your nationality is not visa-free, apply for the appropriate visa at the South Korean embassy or consulate in your country before travelling."),
     R("Buy in India; it's much cheaper. Korean sun is intense", "Bring your usual brand, or buy Korean sunscreen locally (it is widely available and very good). Korean sun is intense"),
     RX(r"<strong>Medicines from India</strong> &mdash; Paracetamol/Dolo[^\n]*</li>",
        "<strong>Medicines from home</strong> &mdash; Paracetamol, stomach medicine (Imodium), oral rehydration packets, antihistamines, and any prescription medicines in their original packaging with a doctor's letter. Pharmacies in South Korea are good but familiar brands help</li>"),
     R("Indian restaurants exist in Seoul but are not necessary &mdash; you'll love Korean cuisine.", "International restaurants are easy to find in Seoul, but you'll love Korean cuisine."),
     R("Buy before leaving India. Indian plugs (Type D) won't fit", "Buy before you leave if your home plugs differ, as Type A and other plug types won't fit"),
     R("<strong>Forex card (Wise, Niyo, BookMyForex)</strong> &mdash; Load USD or KRW. Korean ATMs charge ₩2,000-3,000 (~₹130-200) per withdrawal",
       "<strong>Travel card (Wise, Revolut, or a no-foreign-fee card)</strong> &mdash; Load USD or KRW. Korean ATMs charge ₩2,000-3,000 (~US$1.50-2.25) per withdrawal"),
     R("200,000-300,000 (~₹12,000-18,000)", "200,000-300,000 (~US$150-225)"),
     R("2,500 KRW (~₹150)", "2,500 KRW (~US$2)"),
     R("Use your forex card for most transactions.", "Use your travel card for most transactions."),
     R("Exchange rates at airports are reasonable, better than Indian banks.", "Exchange rates at airports are reasonable."),
     R("Korean workplaces are more business-casual than Indian offices", "Korean workplaces are business-casual"),
     R("Cultural Etiquette: What Every Indian Should Know", "Cultural Etiquette: What Every Visitor Should Know"),
     R("Budget Guide: India to South Korea", "Budget Guide: South Korea Trip Costs in USD"),
     RX(r"<tr><td>Flights \(return, direct\)</td>[^\n]*</tr>", '<tr><td>Flights</td><td colspan="2">Vary by departure city; compare fares well in advance</td></tr>'),
     RX(r"<tr><td>Accommodation/night</td>[^\n]*</tr>", "<tr><td>Accommodation/night</td><td>US$20-45 (hostel dorm or guesthouse)</td><td>US$70-130 (3-star hotel)</td></tr>"),
     RX(r"<tr><td>Food/day</td>[^\n]*</tr>", "<tr><td>Food/day</td><td>US$15-30 (street food + casual)</td><td>US$40-70 (mix of restaurants)</td></tr>"),
     RX(r"<tr><td>Transport/day</td>[^\n]*</tr>", "<tr><td>Transport/day</td><td>US$3-8 (subway + bus)</td><td>US$8-20 (T-money + occasional taxis)</td></tr>"),
     RX(r"<tr><td>Activities/day</td>[^\n]*</tr>", "<tr><td>Activities/day</td><td>US$3-15 (palaces, temples, museums)</td><td>US$15-40 (tours, attractions)</td></tr>"),
     RX(r"<tr><td><strong>Total 7-day trip</strong></td>[^\n]*</tr>", "<tr><td><strong>Total 7-day trip (excl. flights)</strong></td><td><strong>US$300-700</strong></td><td><strong>US$950-1,800</strong></td></tr>"),
     RX(r"<strong>&#x1F4A1; Flight Hack:</strong>[^<]*",
        "<strong>&#x1F4A1; Flight Tip:</strong> Seoul Incheon (ICN) is a major hub with direct flights from many cities across Asia, Oceania, Europe and North America, and low-cost carriers serve many regional routes. "
        "Fares are usually lowest when booked 4-6 weeks ahead and outside the peak cherry-blossom (early April) and autumn-foliage (late October) weeks. "
        "Budget figures above are per-person estimates at about KRW 1,350 per US$ and exclude flights.\n"),
     R("Quick INR-to-KRW conversion while shopping", "Quick currency conversion to KRW while shopping"),
     CUT(r'[ \t]*<p [^>]*>Check <a href="/blog/visa-free-countries-indian-passport"[^>]*>visa-free countries for Indians</a> for easy travel\.</p>\n', "visa-free-countries-indian-passport"),
     R("~KRW 35,000 (~₹2,100)", "~KRW 35,000 (~US$26)"),
     R("Top Experiences for Indian Travelers", "Top Experiences for First-Time Visitors"),
     R("Apply for K-ETA (5 minutes online). Load forex card.", "Apply for K-ETA if your nationality needs one (5 minutes online). Load travel card."),
     R("K-ETA approval (screenshot)", "K-ETA approval or e-Arrival Card confirmation (screenshot)"),
     R("South Korea drives on the right, unlike India.", "South Korea drives on the right."),
     R("Carry your Indian driving licence plus an International Driving Permit, and check the rental company's rules before you book.",
       "Carry your home driving licence plus an International Driving Permit (check which type South Korea accepts), and check the rental company's rules before you book."),
     # visible FAQ
     R(">" + SK_VISA_Q_OLD + "</summary>", ">" + SK_VISA_Q_NEW + "</summary>"),
     RX(r"Indians need a K-ETA \(Korea Electronic Travel Authorization\) for South Korea, which is separate from a visa\.[^<]*</div>", SK_VISA_A + "</div>"),
     R(">What should I pack for South Korea from India?</summary>", ">What should I pack for South Korea?</summary>"),
     R(">What is the best time to visit South Korea from India?</summary>", ">What is the best time to visit South Korea?</summary>"),
     RX(r"Spring \(March-May\) with cherry blossoms and mild weather is ideal\.[^<]*Direct flights from India are available year-round\.</div>", SK_BEST_A + "</div>"),
     R(">How much does a South Korea trip cost from India?</summary>", ">How much does a South Korea trip cost?</summary>"),
     RX(r"A 7-day South Korea trip costs approximately ₹35,000-55,000[^<]*</div>", SK_COST_A + "</div>"),
     # FAQ JSON-LD
     FAQ({SK_VISA_Q_OLD: (SK_VISA_Q_NEW, SK_VISA_A),
          "What should I pack for South Korea from India?": ("What should I pack for South Korea?", None),
          "What is the best time to visit South Korea from India?": ("What is the best time to visit South Korea?", SK_BEST_A),
          "How much does a South Korea trip cost from India?": ("How much does a South Korea trip cost?", SK_COST_A)}),
     # related cards
     CARD("/blog/japan-travel-packing-guide-from-india", "Japan Travel &amp; Packing Guide 2026",
          "Complete Japan packing list with visa tips, JR Pass guide, weather by season, and cultural etiquette for Tokyo, Kyoto, and Osaka.", "/blog/japan-travel-packing-guide", None),
     CARD("/blog/thailand-travel-packing-guide-from-india", "Thailand 7-Day Itinerary 2026",
          "Comfortable 7-day Thailand itinerary covering Bangkok, Chiang Mai, and Krabi, with costs, transport tips, and where to stay.", "/blog/thailand-7-day-itinerary-mid-range", "Itinerary"),
     CARD("/blog/singapore-travel-packing-guide-from-india", "Bali 10-Day Itinerary 2026",
          "Comfortable 10-day Bali itinerary covering Ubud, Seminyak, Uluwatu, and Nusa Penida, with costs, transport tips, and where to stay.", "/blog/bali-10-day-itinerary-mid-range", "Itinerary"),
   ]},
}

REDIRECT_PAIRS = []
for c in SLUGS:
    REDIRECT_PAIRS += [("/blog/%s" % old_slug(c), "/blog/%s" % new_slug(c)), ("/blog/%s.html" % old_slug(c), "/blog/%s" % new_slug(c))]

SLUG_RX = re.compile(r"(?<![a-z0-9-])(%s)-travel-packing-guide-from-india" % "|".join(re.escape(c) for c in SLUGS))
def rewrite_slugs(s): return SLUG_RX.sub(lambda m: m.group(1) + "-travel-packing-guide", s)

# link text on other pages that still says "<X> from India guide"
LINKTEXT = {"Australia from India guide": "Australia Travel &amp; Packing Guide",
            "New Zealand from India guide": "New Zealand Travel &amp; Packing Guide",
            "UK from India guide": "UK Travel &amp; Packing Guide",
            "Canada from India guide": "Canada Travel &amp; Packing Guide",
            "USA from India guide": "USA Travel &amp; Packing Guide",
            "South Korea from India guide": "South Korea Travel &amp; Packing Guide"}
def relabel(s):
    for a, b in LINKTEXT.items():
        s = re.sub(r'(<a href="/blog/[a-z-]+-travel-packing-guide"[^>]*>)' + re.escape(a) + r'(</a>)', lambda m: m.group(1) + b + m.group(2), s)
    return s

def ld_ok(s, label):
    for m in re.finditer(r"<script[^>]+application/ld\+json[^>]*>(.*?)</script>", s, re.S | re.I):
        try: json.loads(m.group(1))
        except Exception as e: raise Err("%s: JSON-LD does not parse (%s)" % (label, e))

def rd(p): return open(p, encoding="utf-8").read()
def wr(p, s): open(p, "w", encoding="utf-8", newline="").write(s)

# ------------------------------------------------------------------ plan (nothing written yet)
final = {}          # path -> content
remove = []         # old paths to delete
report = []

for c in SLUGS:
    po, pn = os.path.join(BLOG, old_slug(c) + ".html"), os.path.join(BLOG, new_slug(c) + ".html")
    src = po if os.path.exists(po) else pn
    if not os.path.exists(src): print("ABORT: neither %s nor %s exists" % (po, pn)); sys.exit(1)
    s0 = s = rd(src)
    cfg = PAGES[c]
    try:
        s = set_title(s, cfg["title"])
        s = set_meta(s, "name", "description", cfg["desc"]); s = set_meta(s, "name", "keywords", cfg["kw"])
        for a, n in (("property", "og:title"), ("name", "twitter:title")): s = set_meta(s, a, n, cfg["title"])
        for a, n in (("property", "og:description"), ("name", "twitter:description")): s = set_meta(s, a, n, cfg["desc"])
        s = set_headline(s, cfg["title"].replace(" | PackSmart", ""))
        if src == po: s = set_modified(s)
        n_ps, n_script = s.count("data-ps-placement="), s.count("<script")
        for op in cfg["ops"]: s = apply(s, op)
        assert s.count("data-ps-placement=") == n_ps and s.count("<script") == n_script, "widget/script count changed"
        s = rewrite_slugs(s)
        ld_ok(s, c)
    except (Err, AssertionError) as e:
        print("ABORT %s: %s" % (c, e)); sys.exit(1)
    final[pn] = s
    if src == po: remove.append(po)

others = [os.path.join(BLOG, f) for f in sorted(os.listdir(BLOG)) if f.endswith(".html")] + [BLOG_INDEX]
for p in others:
    if p in final or p in remove: continue
    s0 = rd(p); s1 = relabel(rewrite_slugs(s0))
    if s1 != s0: final[p] = s1

# sitemap
sm0 = sm = rd(SITEMAP)
for c in SLUGS:
    rx = re.compile(r"(<loc>%s/blog/)%s(</loc>\s*<lastmod>)[^<]*(</lastmod>)" % (re.escape(SITE), re.escape(old_slug(c))))
    n = len(rx.findall(sm))
    if n == 1: sm = rx.sub(lambda m: m.group(1) + new_slug(c) + m.group(2) + TODAY + m.group(3), sm)
    elif n == 0 and ("%s/blog/%s</loc>" % (SITE, new_slug(c))) in sm: pass
    else: print("ABORT sitemap: %d entries for %s" % (n, c)); sys.exit(1)
if sm != sm0: final[SITEMAP] = sm

# vercel.json
v0 = v = rd(VERCEL)
v = re.sub(r'("destination":\s*"/blog/)(%s)-travel-packing-guide-from-india(")' % "|".join(re.escape(c) for c in SLUGS), lambda m: m.group(1) + m.group(2) + "-travel-packing-guide" + m.group(3), v)
missing = [(a, b) for a, b in REDIRECT_PAIRS if ('"source": "%s"' % a) not in v]
if missing:
    block = ",\n".join('    {\n      "source": "%s",\n      "destination": "%s",\n      "permanent": true\n    }' % (a, b) for a, b in missing)
    m = re.search(r"\n    \}\n  \],\n  \"headers\"", v)
    if not m: print("ABORT vercel.json: cannot find the end of the redirects array"); sys.exit(1)
    v = v[:m.start()] + "\n    },\n" + block + v[m.start() + len("\n    }"):]
try: json.loads(v)
except Exception as e: print("ABORT vercel.json no longer parses: %s" % e); sys.exit(1)
if v != v0: final[VERCEL] = v

# ------------------------------------------------------------------ neutrality report on the six pages
NEUT = re.compile(r"India|INR\b|₹|\bRs\.?\s?\d|\blakhs?\b|Delhi|Mumbai|Bangalore|Kolkata|Aadhaar|VFS|BLS", re.I)
for c in SLUGS:
    s = final.get(os.path.join(BLOG, new_slug(c) + ".html"))
    if not s: continue
    body = re.sub(r"<[^>]*>", " ", re.sub(r"<style.*?</style>|<script(?![^>]*ld\+json).*?</script>", " ", s, flags=re.S))
    hits = [re.sub(r"\s+", " ", body[max(0, m.start() - 45): m.end() + 45]) for m in NEUT.finditer(body)]
    report.append((c, hits))

# ------------------------------------------------------------------ write
changed = 0
for p, s in final.items():
    if os.path.exists(p) and rd(p) == s: continue
    wr(p, s); changed += 1
for p in remove:
    if os.path.exists(p): os.remove(p)
print("w22: %d file(s) written, %d old file(s) removed" % (changed, len(remove)))
for c, hits in report:
    print("  %-12s India-term hits left: %d" % (c, len(hits)))
    for h in hits[:12]: print("      ...%s..." % h)
