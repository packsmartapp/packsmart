#!/usr/bin/env python3
"""Sri Lanka: replace the Localrent car widget with the DiscoverCars search form (Colombo airport, CMB).
DiscoverCars serves Sri Lanka (Hertz, Europcar, Green Motion at CMB). Single airport, so no pick-up chips.
Idempotent. Usage: python3 w7_sri_lanka_discovercars.py [blog_dir]   (default: public/blog)
"""
import re, sys, os

ROOT = sys.argv[1] if len(sys.argv) > 1 else 'public/blog'
P = os.path.join(ROOT, 'sri-lanka-travel-packing-guide-from-india.html')
PID = 'discovercars-sri-lanka'

WIDGET = ('https://tpwdg.com/content?trs=508747&shmarker=711400&country=sri-lanka&city=colombo&place=cmb&locale=en&powered_by=false'
          '&bg_color=%23f0f8f5&font_color=%23333333&button_color=%2300C9A7&button_font_color=%23ffffff&button_text=Search&rounded_corners=true'
          '&benefits=false&dc_powered_by=false&supplier_logos=false&top_logo=false&logo_style=dark&top_color=%23007ac2&campaign_id=117&promo_id=3873')

BLOCK = '''<!-- DiscoverCars Car Rental Widget -->
<div data-ps-placement="%s" style="max-width: 800px; margin: 40px auto; padding: 35px 30px 22px; background: #f0f8f5; border-radius: 12px; border: 1px solid #e0f0ea;">
<h3 style="margin: 0 0 14px 0; color: #0f0f23; font-size: 1.3rem;">Rent a Car in Sri Lanka</h3>
    <style>.ps-dc-mount{min-height:362px;}</style>
    <p style="margin: 0 0 10px 0; color: #444; font-size: 0.95rem; line-height: 1.7;">Sri Lanka drives on the left, as in India. A car lets you reach the hill country, the south coast and the cultural triangle at your own pace, but foreign visitors need a temporary Sri Lankan driving licence on top of their home licence, so check the current process before you book. Prefer not to drive? A private transfer with a driver is just below.</p>
    <p style="margin: 0 0 16px 0; color: #666; font-size: 0.95rem; line-height: 1.7;">Pick-up is at Colombo airport (CMB). Compare prices below and check the rental company's rules before you book.</p>
    <div class="ps-dc-mount"><script async src="%s" charset="utf-8"></script></div>
</div>
''' % (PID, WIDGET)


def div_at(s, i):
    d = 0
    for t in re.finditer(r'<(/?)div\b', s[i:]):
        d += -1 if t.group(1) else 1
        if d == 0:
            return s.find('>', i + t.end()) + 1
    raise SystemExit('unbalanced div')


with open(P, encoding='utf-8') as f:
    s = orig = f.read()
if 'data-ps-placement="%s"' % PID in s:
    print('OK   sri-lanka: DiscoverCars block present')
    sys.exit(0)
m = re.search(r'<!-- Localrent Car Rental Widget -->\s*', s)
if not m:
    raise SystemExit('Localrent comment not found')
a = m.start()
d0 = s.index('<div', m.end())
b = div_at(s, d0)
old = s[a:b]
if 'country=132' not in old or 'Rent a Car in Sri Lanka' not in old:
    raise SystemExit('unexpected Localrent block content')
s = s[:a] + BLOCK.rstrip('\n') + s[b:]
with open(P, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('OK   sri-lanka: Localrent block replaced by DiscoverCars (%d -> %d bytes)' % (len(old), len(BLOCK)))
