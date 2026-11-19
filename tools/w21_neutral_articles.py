#!/usr/bin/env python3
"""w21: make the non-India articles neutral (no 'from India' framing).
Removes 'Flying from India?' cross-promo callouts and the 'Indian passport holders' visa sentences (visible text AND the FAQ JSON-LD),
swaps the India related-article cards for neutral ones, and rewords a few India-specific phrases.
India-designed pages and the web stories are NOT touched here.
Run from repo root:  python3 tools/w21_neutral_articles.py   (optional arg: blog dir)
Idempotent. Validates every page first and writes nothing if any edit does not match exactly once.
"""
import json, os, re, sys

BLOG = sys.argv[1] if len(sys.argv) > 1 else "public/blog"

def R(old, new):            # exact string replace, must match once
    return ("replace", old, new)
def CUT(pattern):           # remove a whole line/paragraph matched by regex (must match once)
    return ("cut", pattern, "")
def CARD(old_h4, new_h4, new_p, new_href, new_tag):
    return ("card", old_h4, (new_h4, new_p, new_href, new_tag))

CARD_RE = r'(<h4>%s</h4>)(\s*)(<p>[^<]*</p>)(\s*)<a href="[^"]*">(Read More <span class="related-arrow">[^<]*</span></a>)(\s*)(<div class="related-tag">)[^<]*(</div>)'

PAGES = {
 "bali-10-day-itinerary-mid-range.html": [
    R("Most nationalities (US, UK, EU, Australia, India) can get a Visa on Arrival", "Most nationalities (US, UK, EU, Australia) can get a Visa on Arrival"),
    R("Most nationalities (US, UK, EU, Australia, India) get a 30-day Visa on Arrival", "Most nationalities (US, UK, EU, Australia) get a 30-day Visa on Arrival"),
    CUT(r'[ \t]*<p [^>]*>Flying from India\? Our <a href="/blog/bali-travel-packing-guide-from-india"[^>]*>[^<]*</a> covers[^<]*</p>\n'),
 ],
 "thailand-7-day-itinerary-mid-range.html": [
    CUT(r'[ \t]*<p [^>]*>Flying from India\? Our <a href="/blog/thailand-travel-packing-guide-from-india"[^>]*>[^<]*</a> covers[^<]*</p>\n'),
    ("regex", r'"text": "Indian passport holders can enter Thailand visa-free[^"]*"',
        '"text": "Most nationalities (US, UK, EU, Australia) get 30–60 days visa-free. Rules differ for other nationalities (some can get a visa on arrival, others need a tourist visa in advance), so check Thailand’s e-visa portal for the latest requirements."'),
    R("Indian passport holders can get a visa on arrival (VOA) for 15 days ($30 fee) or apply for a 60-day tourist visa in advance. Check Thailand&rsquo;s e-visa portal for the latest requirements.",
      "Rules differ for other nationalities (some can get a visa on arrival, others need a tourist visa in advance), so check Thailand&rsquo;s e-visa portal for the latest requirements."),
 ],
 "japan-travel-packing-guide.html": [
    CUT(r'[ \t]*<p [^>]*>Travelling from India\? See our <a href="/blog/japan-travel-packing-guide-from-india"[^>]*>[^<]*</a>\.</p>\n'),
 ],
 "italy-7-day-itinerary-mid-range.html": [
    R("Indian passport holders need a Schengen visa — apply through the Italian embassy or VFS Global at least 4–6 weeks before travel.",
      "Other nationalities should check whether they need a Schengen visa; if so, apply through the Italian embassy or its visa application centre at least 4–6 weeks before travel."),
    R("Indian passport holders need a Schengen visa &mdash; apply through the Italian embassy or VFS Global 4&ndash;6 weeks ahead.",
      "Other nationalities should check whether they need a Schengen visa; if so, apply through the Italian embassy or its visa application centre 4&ndash;6 weeks ahead."),
 ],
 "spain-10-day-itinerary-mid-range.html": [
    R("Indian passport holders need a Schengen visa — apply through the Spanish embassy or BLS International at least 4–6 weeks before travel.",
      "Other nationalities should check whether they need a Schengen visa; if so, apply through the Spanish embassy or its visa application centre at least 4–6 weeks before travel."),
    R("Indian passport holders need a Schengen visa &mdash; apply through the Spanish embassy or BLS International 4&ndash;6 weeks ahead.",
      "Other nationalities should check whether they need a Schengen visa; if so, apply through the Spanish embassy or its visa application centre 4&ndash;6 weeks ahead."),
 ],
 "mexico-7-day-itinerary-mid-range.html": [
    R("Indian passport holders need a Mexican visa — apply at the Mexican embassy 4–6 weeks ahead.", "Other nationalities may need a Mexican visa — apply at the Mexican embassy 4–6 weeks ahead."),
    R("Indian passport holders need a Mexican visa, but if you hold", "Other nationalities may need a Mexican visa, but if you hold"),
 ],
 "vietnam-10-day-itinerary-mid-range.html": [
    R("Indian passport holders need an e-visa — apply online at evisa.xuatnhapcanh.gov.vn ($25, processed in 3 business days).",
      "Other nationalities can apply for an e-visa online at evisa.xuatnhapcanh.gov.vn ($25, processed in 3 business days)."),
    R("Indian passport holders need an e-visa ($25, processed in 3 business days at evisa.xuatnhapcanh.gov.vn).",
      "Other nationalities can apply for an e-visa ($25, processed in 3 business days at evisa.xuatnhapcanh.gov.vn)."),
 ],
 "japan-7-day-itinerary-budget.html": [
    R("Indian passport holders need a visa in advance — apply through the Japanese embassy or VFS Global.",
      "Other nationalities need a visa in advance — apply through the Japanese embassy or consulate."),
    R("Indian passport holders need a tourist visa in advance &mdash; apply through the Japanese embassy or VFS Global.",
      "Other nationalities need a tourist visa in advance &mdash; apply through the Japanese embassy or consulate."),
    CARD("Japan Guide for Indian Travellers", "International Travel Checklist",
         "The complete pre-trip checklist for flying abroad — passport, visa, insurance, currency, and more.",
         "https://www.packsmartapp.com/blog/international-travel-checklist", "Travel Tips"),
 ],
 "solo-travel-tips-beginners.html": [
    R("Visa-free for Indian passport holders (60 days).", "Visa rules vary by nationality, so check before you book."),
    R("Friendly locals, affordable, and visa-free for Indian passport holders.", "Friendly locals and affordable prices."),
    R("No visa needed for Indians.", "Check the current visa rules for your nationality."),
    R("can cost lakhs.", "can cost tens of thousands of dollars."),
 ],
 "budget-travel-destinations-2026.html": [
    CUT(r'[ \t]*<p [^>]*>Indian passport holders have many affordable options[^<]*<a href="/blog/visa-free-countries-indian-passport"[^>]*>[^<]*</a>\.</p>\n'),
 ],
 "family-travel-tips-with-kids.html": [
    CARD("Visa-Free Countries for Indian Passport 2026", "Carry-On Packing List",
         "Everything you need in your carry-on so you never lose essentials to checked bag mishaps.",
         "/blog/carry-on-packing-list", "Prep"),
 ],
 "international-travel-checklist.html": [
    CARD("Visa-Free Countries for Indian Passport 2026", "First Time Flying Guide",
         "Everything first-time flyers need to know — security, boarding, ear pressure, and what to do during turbulence.",
         "/blog/first-time-flying", "Prep"),
 ],
 "first-time-flying.html": [
    R("driver's license, Aadhaar card, or passport", "driver's license, national ID card, or passport"),
 ],
 "best-esim-international-travel-comparison.html": [
    R("international esim, esim for india, best travel esim", "international esim, best travel esim"),
 ],
}

def apply(s, op):
    kind = op[0]
    if kind == "replace":
        _, old, new = op
        if s.count(old) == 1: return s.replace(old, new), True
        if s.count(old) == 0 and s.count(new) >= 1: return s, False
        raise ValueError("replace: %d matches for %r" % (s.count(old), old[:60]))
    if kind == "cut":
        pat = re.compile(op[1])
        m = pat.findall(s)
        if len(m) == 1: return pat.sub("", s, count=1), True
        if len(m) == 0: return s, False       # already gone
        raise ValueError("cut: %d matches for %r" % (len(m), op[1][:60]))
    if kind == "regex":
        pat = re.compile(op[1]); m = pat.findall(s)
        if len(m) == 1: return pat.sub(lambda _: op[2], s, count=1), True
        if len(m) == 0 and op[2] in s: return s, False
        raise ValueError("regex: %d matches for %r" % (len(m), op[1][:60]))
    if kind == "card":
        old_h4, (h4, p, href, tag) = op[1], op[2]
        pat = re.compile(CARD_RE % re.escape(old_h4), re.S)
        m = pat.findall(s)
        if len(m) == 1:
            def rep(mo):
                g = mo.groups()
                return "<h4>%s</h4>%s<p>%s</p>%s<a href=\"%s\">%s%s%s%s%s" % (h4, g[1], p, g[3], href, g[4], g[5], g[6], tag, g[7])
            return pat.sub(rep, s, count=1), True
        if len(m) == 0 and ("<h4>%s</h4>" % h4) in s: return s, False
        raise ValueError("card: %d matches for %r" % (len(m), old_h4))
    raise ValueError(kind)

def ldjson_ok(s):
    for m in re.finditer(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', s, re.S | re.I):
        json.loads(m.group(1))

plans = []
for f, ops in PAGES.items():
    path = os.path.join(BLOG, f)
    if not os.path.exists(path):
        print("ABORT: %s not found" % path); sys.exit(1)
    s = o = open(path, encoding="utf-8").read()
    changed = 0
    try:
        for op in ops:
            s, did = apply(s, op); changed += did
        ldjson_ok(s)
    except Exception as e:
        print("ABORT %s: %s" % (f, e)); sys.exit(1)
    plans.append((f, path, o, s, changed))

for f, path, o, s, changed in plans:
    if s == o:
        print("SKIP %s: already neutral" % f); continue
    open(path, "w", encoding="utf-8").write(s)
    print("OK %s: %d edit(s) (%d -> %d bytes)" % (f, changed, len(o), len(s)))
