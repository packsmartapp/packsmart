#!/usr/bin/env python3
"""Wave 2d: Airalo eSIM tiles on Baku, Mexico (guide + 7-day itinerary), Sri Lanka; Radical Storage lines on all of them;
Klook deal tiles on Baku.
Idempotent. Usage: python3 w6_baku_mexico_sri_lanka.py [blog_dir]   (default: public/blog)

Templates (eSIM block, Radical line, Klook tile CSS) are read from the live Thailand guide, so styling stays in sync.
Replaces the Yesim eSIM text/links and strip cards on these three pages (Yesim retired as Airalo goes in).
Airalo prices read from the Fixed data tab, Klook "from" prices from Klook en-US search listings, both on 15 Nov 2026.
Maldives is untouched (Airalo sells only a 30-day 20 GB plan there; no Radical or Klook fit). Mexico and Sri Lanka get no Klook block (thin catalogues).
"""
import re, sys, os

ROOT = sys.argv[1] if len(sys.argv) > 1 else 'public/blog'
TH = 'thailand-travel-packing-guide-from-india.html'
FOOT = 'Klook prices as of 15 Nov. We may earn a commission, at no extra cost to you.'


def rd(p):
    with open(p, encoding='utf-8') as f:
        return f.read()


def wr(p, s):
    with open(p, 'w', encoding='utf-8', newline='') as f:
        f.write(s)


def div_at(s, i):
    d = 0
    for t in re.finditer(r'<(/?)div\b', s[i:]):
        d += -1 if t.group(1) else 1
        if d == 0:
            return s.find('>', i + t.end()) + 1
    raise SystemExit('unbalanced div')


def find_div(s, marker):
    m = re.search(r'<div[^>]*%s' % re.escape(marker), s)
    if not m:
        return None
    return m.start(), div_at(s, m.start())


# ---- templates from Thailand ---------------------------------------------------
th = rd(os.path.join(ROOT, TH))
a, b = find_div(th, 'data-ps-placement="airalo-thailand"')
ESIM_TPL = th[a:b]
for k in ('Choose your Thailand eSIM', 'airalo.tpx.li/jpsQJDtb', 'airalo.tpx.li/zN9sG7t2', 'airalo.tpx.li/A56Hrmvp'):
    assert k in ESIM_TPL, k
i = th.find('<p data-ps-placement="bags-thailand"')
BAGS_TPL = th[i:th.find('</p>', i) + 4]
BAGS_OPEN = BAGS_TPL[:BAGS_TPL.find('>') + 1]
BAGS_LINK_STYLE = re.search(r'<a href="[^"]*" target="_blank" rel="nofollow noopener sponsored" style="([^"]*)"', BAGS_TPL).group(1)
j = th.index('data-ps-placement="klook-deals-thailand-guide"')
CSS = th[th.index('<style>', j):th.index('</style>', j) + len('</style>')]
assert '.ps-kd-t{' in CSS and '.ps-kd-img' in CSS


def esim_block(pid, headline, ids, prices):
    t = ESIM_TPL.replace('data-ps-placement="airalo-thailand"', 'data-ps-placement="%s"' % pid)
    t = t.replace('US$7.50', '@@P3@@').replace('US$6', '@@P2@@').replace('US$4', '@@P1@@')
    t = t.replace('Choose your Thailand eSIM', 'Choose your %s eSIM' % headline)
    t = t.replace('Thailand eSIM,', '%s eSIM,' % headline)
    for old, new in (('jpsQJDtb', ids[0]), ('zN9sG7t2', ids[1]), ('A56Hrmvp', ids[2])):
        t = t.replace('airalo.tpx.li/' + old, 'airalo.tpx.li/' + new)
    for n, p in enumerate(prices, 1):
        t = t.replace('@@P%d@@' % n, p)
    assert 'Thailand' not in t and '@@' not in t
    return t


def bags_line(pid, cities):
    links = ['<a href="https://radicalstorage.tpx.li/%s" target="_blank" rel="nofollow noopener sponsored" style="%s">%s</a>' % (cid, BAGS_LINK_STYLE, name) for name, cid in cities]
    where = ', '.join(links[:-1]) + ' or ' + links[-1] if len(links) > 1 else links[0]
    return (BAGS_OPEN.replace('bags-thailand', pid) +
            '\n        &#129523; Checked out but your flight or overnight train is hours away? Store your bags in %s with Radical Storage and explore hands-free.\n    </p>' % where)


# id -> (tracked id, name, meta, price, emoji entity, gradient, badge)
T = {
    'azerbaijan-att-gobustan': ('tE06pC6E', 'Gobustan and Absheron day trip from Baku', 'Baku &middot; Gobustan and the Absheron peninsula &middot; Day trip', 15, '&#128293;', 'g1', ''),
    'azerbaijan-att-shahdag': ('fHTCkYph', 'Guba, Shahdag Resort and Candy Cane Mountain tour', 'Baku &middot; Guba, Shahdag and the Candy Cane Mountains &middot; Day tour', 52, '&#127956;', 'g4', ''),
}


def tile(aid):
    tid, name, meta, price, emo, g, badge = T[aid]
    bd = '<span class="ps-kd-b">%s</span>' % badge if badge else ''
    return ('<a class="ps-kd-t" data-aid="%s" href="https://klook.tpx.li/%s" target="_blank" rel="nofollow noopener sponsored">'
            '<span class="ps-kd-ph %s" aria-hidden="true">%s</span>%s<strong class="ps-kd-n">%s</strong>'
            '<span class="ps-kd-m">%s</span><span class="ps-kd-p">from US$%d</span></a>') % (aid, tid, g, emo, bd, name, meta, price)


def klook_block(pid, head, sub, aids):
    return ('<div class="ps-kd ps-kd-img" data-ps-placement="%s">\n%s\n<strong class="ps-kd-h">%s</strong>\n<p class="ps-kd-s">%s</p>\n'
            '<div class="ps-kd-g">\n%s\n</div>\n<p class="ps-kd-f">%s</p>\n</div>\n\n') % (
        pid, CSS, head, sub, '\n'.join(tile(x) for x in aids), FOOT)


ESIM = {
    'az': dict(pid='airalo-azerbaijan', headline='Azerbaijan', ids=['L1t1uzLT', 'qd8eIS4H', 'vucXBDp8'], prices=['US$5', 'US$14', 'US$20']),
    'mx': dict(pid='airalo-mexico', headline='Mexico', ids=['whUdL8mS', 'ehKTvCFD', 'zlg1zk1A'], prices=['US$4', 'US$8.50', 'US$12.50']),
    'mxi': dict(pid='airalo-mexico-itinerary', headline='Mexico', ids=['whUdL8mS', 'ehKTvCFD', 'zlg1zk1A'], prices=['US$4', 'US$8.50', 'US$12.50']),
    'lk': dict(pid='airalo-sri-lanka', headline='Sri Lanka', ids=['meyLWcb4', 'sfSYSMXL', 'T4zVpcE9'], prices=['US$4.50', 'US$6.50', 'US$8.50']),
}
RAD = {
    'az': ('bags-azerbaijan', 'pickups-baku', [('Baku', '589RQmJK')]),
    'mx': ('bags-mexico', 'pickups-mexico', [('Mexico City', 'yv2JP1wf'), ('Canc&uacute;n', 'Gy12nUrX'), ('Oaxaca', 'dcYcy5DQ')]),
    'mxi': ('bags-mexico-itinerary', 'pickups-mexico-itinerary', [('Mexico City', 'yv2JP1wf'), ('Oaxaca', 'dcYcy5DQ'), ('Tulum', 'm9irfNZC')]),
    'lk': ('bags-sri-lanka', 'kiwitaxi-sri-lanka', [('Colombo', 'CpjkTLxn')]),
}
KLOOK = {
    'az': ('klook-deals-baku-guide', 'Suggested 4-Day Itinerary',
           "Book Baku's day trips ahead", 'Gobustan and Absheron, plus the Guba and Shahdag mountains, booked before you go.',
           ['azerbaijan-att-gobustan', 'azerbaijan-att-shahdag']),
}

PAGES = [
    ('baku-azerbaijan-from-india', 'az'),
    ('mexico-travel-packing-guide', 'mx'),
    ('mexico-7-day-itinerary-mid-range', 'mxi'),
    ('sri-lanka-travel-packing-guide-from-india', 'lk'),
]

# Yesim text spots -> Airalo wording
AZ_SENT = re.compile(r'Get <a href="https://yesim\.tpx\.li/[^"]*"[^>]*>a Yesim eSIM</a> before you fly so you land connected — data packs for Azerbaijan are cheap\.</p>')
AZ_SENT_NEW = 'Install an eSIM before you fly so you land connected, with plans from about US$5 (see the plan tiles below).</p>'
MX_BULLET = re.compile(r'<li><strong>Yesim eSIM:</strong> Local data without SIM card switching \(\$3-8 for several GB\)\. Works in Mexico</li>')
MX_BULLET_NEW = '<li><strong>eSIM (Airalo):</strong> Local data without swapping SIM cards, from about US$4 for 1 GB (see the plan tiles below). Works in Mexico</li>'
MXI_CALLOUT = re.compile(r'[ \t]*<p[^>]*>\s*&#128241; Stay connected throughout your trip\. <a href="https://yesim\.tpx\.li/[^"]*"[^>]*>Get a Yesim eSIM for Mexico</a> &mdash; activate before you fly, data ready at landing\.\s*</p>\s*')
# the Yesim strip card: the flex "pill" link only (never an inline text link)
YESIM_CARD = re.compile(r'[ \t]*<a href="https://yesim\.tpx\.li/[^"]*"[^>]*?style="display:flex(?:(?!</a>).)*?Yesim eSIM(?:(?!</a>).)*?</a>[ \t]*\n?', re.S)


def pickups_end(s, pid):
    r = find_div(s, 'data-ps-placement="%s"' % pid)
    if not r:
        raise SystemExit('block %s missing' % pid)
    j = r[1]
    return j + 2 if s[j:j + 2] == '\n\n' else j


def after_list(s, m_end):
    return s.index('</ul>', m_end) + len('</ul>')


def h2_by_text(s, text):
    hs = [h for h in re.finditer(r'<h2[^>]*>(.*?)</h2>', s, re.S) if text in re.sub('<[^>]+>', '', h.group(1))]
    if len(hs) != 1:
        raise SystemExit('%d h2 match(es) for %r' % (len(hs), text))
    return hs[0]


for stem, key in PAGES:
    p = os.path.join(ROOT, stem + '.html')
    s = orig = rd(p)
    notes = []
    c = ESIM[key]
    blk = esim_block(c['pid'], c['headline'], c['ids'], c['prices'])
    # ---- eSIM ----
    if 'data-ps-placement="%s"' % c['pid'] in s:
        notes.append('eSIM present')
    else:
        if key == 'az':
            m = AZ_SENT.search(s)
            if not m:
                raise SystemExit(stem + ': Baku Yesim sentence not found')
            s = s[:m.start()] + AZ_SENT_NEW + '\n\n' + blk + s[m.end():]
        elif key == 'mx':
            m = MX_BULLET.search(s)
            if not m:
                raise SystemExit(stem + ': Communication bullet not found')
            s = s[:m.start()] + MX_BULLET_NEW + s[m.end():]
            k = after_list(s, m.start())
            s = s[:k] + '\n\n' + blk + s[k:]
        elif key == 'mxi':
            ms = list(MXI_CALLOUT.finditer(s))
            if len(ms) != 2:
                raise SystemExit('%s: expected 2 Yesim callouts, found %d' % (stem, len(ms)))
            # later callout (Essential Apps) becomes the tiles; earlier one (between Day 3 and Day 4) is removed
            s = s[:ms[1].start()] + blk + '\n\n' + s[ms[1].end():]
            s = s[:ms[0].start()] + s[ms[0].end():]
            notes.append('callouts replaced')
        else:  # lk: end of Essential Apps, before the Quick Tips heading
            h = h2_by_text(s, 'Quick Tips for Indian')
            s = s[:h.start()] + blk + '\n\n' + s[h.start():]
        notes.append('eSIM tiles')
    # ---- Radical ----
    pid, pk, cities = RAD[key]
    if 'data-ps-placement="%s"' % pid in s:
        notes.append(pid + ' present')
    else:
        pos = pickups_end(s, pk)
        s = s[:pos] + bags_line(pid, cities) + '\n\n' + s[pos:]
        notes.append(pid)
    # ---- Klook (Baku) ----
    if key in KLOOK:
        kid, anchor, head_, sub, aids = KLOOK[key]
        if 'data-ps-placement="%s"' % kid in s:
            notes.append(kid + ' present')
        else:
            h = h2_by_text(s, anchor)
            s = s[:h.start()] + klook_block(kid, head_, sub, aids) + s[h.start():]
            notes.append(kid)
    # ---- Yesim strip card ----
    strip = list(YESIM_CARD.finditer(s))
    if len(strip) == 1:
        m = strip[0]; s = s[:m.start()] + s[m.end():]; notes.append('strip card removed')
    elif len(strip) > 1:
        notes.append('!! %d strip cards matched, none removed' % len(strip))
    left = len(re.findall(r'(?i)yesim', re.sub(r'<script.*?</script>', '', s, flags=re.S)))
    if left:
        notes.append('!! %d Yesim mention(s) left' % left)
    # ---- click-tracker labels ----
    key_ = "'radicalstorage.tpx.li': 'Radical_Storage',"
    add = ''
    if "'airalo.tpx.li'" not in s:
        add += " 'airalo.tpx.li': 'Airalo',"
    if key in KLOOK and "'klook.tpx.li'" not in s:
        add += " 'klook.tpx.li': 'Klook',"
    if add:
        if key_ not in s:
            raise SystemExit(stem + ': click map anchor missing')
        s = s.replace(key_, key_ + add, 1)
        notes.append('click labels')
    if s != orig:
        wr(p, s)
    print('OK   %-44s %s' % (stem, '; '.join(notes)))
