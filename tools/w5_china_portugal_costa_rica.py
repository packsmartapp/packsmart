#!/usr/bin/env python3
"""Wave 2c: Airalo eSIM tiles on China, Portugal, Costa Rica; Radical Storage lines on Portugal and Costa Rica;
Klook deal tiles on China and Portugal.
Idempotent. Usage: python3 w5_china_portugal_costa_rica.py [blog_dir]   (default: public/blog)

Templates (eSIM block, Radical line, Klook tile CSS) are read from the live Thailand guide, so styling stays in sync.
Replaces the Yesim eSIM text/links and strip cards on these three pages (Yesim retired as Airalo goes in).
Airalo prices read from the Fixed data tab, Klook "from" prices from Klook en-US search listings, both on 15 Nov 2026.
China gets no Radical line (no mainland Radical Storage city pages); Costa Rica gets no Klook block (thin catalogue).
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
    'china-att-greatwall': ('j1iTxqlf', 'Mutianyu Great Wall day tour from Beijing', 'Beijing &middot; Great Wall at Mutianyu &middot; Day tour', 21, '&#129521;', 'g1', ''),
    'china-att-palace': ('JfEsurrW', 'Palace Museum (Forbidden City) ticket', 'Beijing &middot; Imperial palace complex &middot; Entry ticket', 7, '&#127983;', 'g3', ''),
    'china-att-disney': ('iiEsoVhh', 'Shanghai Disney Resort ticket', 'Shanghai &middot; Theme park &middot; Entry ticket', 66, '&#127905;', 'g2', ''),
    'china-att-panda': ('eGzwcjG5', 'Giant Panda Breeding Research Base ticket', 'Chengdu &middot; Panda base &middot; Entry ticket', 6, '&#128060;', 'g6', ''),
    'portugal-att-sintra': ('ykI8gd8z', 'Sintra, Pena Palace, Regaleira and Cascais day tour', 'Lisbon &middot; Palaces and the coast &middot; Full-day tour', 45, '&#127984;', 'g1', ''),
    'portugal-att-douro': ('rYHOMDpf', 'Douro Valley wine tour with lunch and river cruise', 'Porto &middot; Tastings and a river cruise &middot; Full-day tour', 113, '&#127863;', 'g5', ''),
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
    'cn': dict(pid='airalo-china', headline='China', ids=['p3RmgRFk', 'QPe3FFTb', 'IZcqxJRk'], prices=['US$4', 'US$10.50', 'US$15']),
    'pt': dict(pid='airalo-portugal', headline='Portugal', ids=['QIl1QvGv', 'prJwSHlg', 'nmq9jtmy'], prices=['US$4', 'US$6.50', 'US$8']),
    'cr': dict(pid='airalo-costa-rica', headline='Costa Rica', ids=['4uy2cXjn', 'YTATa6PU', 'n1znAJoH'], prices=['US$7.50', 'US$19', 'US$26']),
}
RAD = {
    'pt': ('bags-portugal', 'pickups-portugal', [('Lisbon', 'HIBv1FFg'), ('Porto', 'gCJCr2k6'), ('Faro', 'REqIZzlr')]),
    'cr': ('bags-costa-rica', 'pickups-costa-rica', [('San Jos&eacute;', 'aUt76AdI')]),
}
KLOOK = {
    'cn': ('klook-deals-china-guide', 'Pro Tips for China Travel',
           "Book China's big days out ahead", "The Great Wall, the Palace Museum, Shanghai Disney Resort and Chengdu's pandas, booked before you go.",
           ['china-att-greatwall', 'china-att-palace', 'china-att-disney', 'china-att-panda']),
    'pt': ('klook-deals-portugal-guide', 'Pro Tips for Portugal Travel',
           "Book Portugal's big days out ahead", 'A Sintra and Cascais day trip from Lisbon and a Douro Valley wine day from Porto, booked before you go.',
           ['portugal-att-sintra', 'portugal-att-douro']),
}

PAGES = [
    ('china-travel-packing-guide', 'cn'),
    ('portugal-travel-packing-guide', 'pt'),
    ('costa-rica-packing-list', 'cr'),
]

# Yesim text spots -> Airalo wording
CN_BULLET = re.compile(r'<li><strong>Yesim eSIM:</strong> Local data without SIM card switching\. 3-8 USD for several GB in China</li>')
CN_BULLET_NEW = '<li><strong>eSIM (Airalo):</strong> Install it before you fly and switch it on when you land, with plans from about US$4 (see the plan tiles below). A handy backup alongside a local SIM</li>'
PT_BULLET = re.compile(r'<li><strong>Yesim eSIM:</strong> Local data without SIM card switching \(\$3-8 for several GB\)</li>')
PT_BULLET_NEW = '<li><strong>eSIM (Airalo):</strong> Local data without swapping SIM cards, from about US$4 for 1 GB (see the plan tiles below)</li>'
CR_PACK_OLD = 'Yesim eSIM offers coverage in Costa Rica at reasonable rates.'
CR_PACK_NEW = 'An Airalo eSIM covers Costa Rica from about US$7.50 for 1 GB (see the plan tiles in the Apps section).'
CR_BULLET = re.compile(r'<li><strong>Yesim:</strong> eSIM data service; 150\+ country coverage \(\$3\.99-29\.99/month for Costa Rica\)\.</li>')
CR_BULLET_NEW = '<li><strong>Airalo:</strong> eSIM data service with Costa Rica plans from US$7.50 (1 GB, 3 days) to US$26 (5 GB, 15 days).</li>'
YESIM_CARD = re.compile(r'[ \t]*<a href="https://yesim\.tpx\.li/[^"]*"(?:(?!</a>).)*?Yesim eSIM(?:(?!</a>).)*?</a>[ \t]*\n?', re.S)


def pickups_end(s, pid):
    r = find_div(s, 'data-ps-placement="%s"' % pid)
    if not r:
        raise SystemExit('pickups block %s missing' % pid)
    j = r[1]
    return j + 2 if s[j:j + 2] == '\n\n' else j


def after_list(s, m_end):
    """Position just after the </ul> that closes the list containing offset m_end."""
    return s.index('</ul>', m_end) + len('</ul>')


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
        if key == 'pt':
            # remove the green Yesim callout at the top of the Apps section
            mk = 'Stay connected from the moment you land'
            if mk not in s:
                raise SystemExit(stem + ': Portugal callout not found')
            a0 = s.rfind('<div', 0, s.index(mk))
            b0 = div_at(s, a0)
            while s[b0:b0 + 1] == '\n':
                b0 += 1
            s = s[:a0] + s[b0:]
            notes.append('callout removed')
        pat, new = {'cn': (CN_BULLET, CN_BULLET_NEW), 'pt': (PT_BULLET, PT_BULLET_NEW), 'cr': (CR_BULLET, CR_BULLET_NEW)}[key]
        m = pat.search(s)
        if not m:
            raise SystemExit(stem + ': Communication bullet not found')
        s = s[:m.start()] + new + s[m.end():]
        k = after_list(s, m.start())
        s = s[:k] + '\n\n' + blk + s[k:]
        notes.append('eSIM tiles')
        if key == 'cr':
            if CR_PACK_OLD not in s:
                raise SystemExit(stem + ': packing-list Yesim sentence not found')
            s = s.replace(CR_PACK_OLD, CR_PACK_NEW, 1)
            notes.append('gear-list line')
    # ---- Radical (Portugal, Costa Rica) ----
    if key in RAD:
        pid, pk, cities = RAD[key]
        if 'data-ps-placement="%s"' % pid in s:
            notes.append(pid + ' present')
        else:
            pos = pickups_end(s, pk)
            s = s[:pos] + bags_line(pid, cities) + '\n\n' + s[pos:]
            notes.append(pid)
    # ---- Klook (China, Portugal) ----
    if key in KLOOK:
        kid, anchor, head_, sub, aids = KLOOK[key]
        if 'data-ps-placement="%s"' % kid in s:
            notes.append(kid + ' present')
        else:
            hs = [h for h in re.finditer(r'<h2[^>]*>(.*?)</h2>', s, re.S) if anchor in re.sub('<[^>]+>', '', h.group(1))]
            if len(hs) != 1:
                raise SystemExit('%s: %d h2 match(es) for %r' % (stem, len(hs), anchor))
            s = s[:hs[0].start()] + klook_block(kid, head_, sub, aids) + s[hs[0].start():]
            notes.append(kid)
    # ---- Yesim strip card (last 15% only) ----
    strip = [m for m in YESIM_CARD.finditer(s) if m.start() > 0.85 * len(s)]
    if len(strip) == 1:
        m = strip[0]; s = s[:m.start()] + s[m.end():]; notes.append('strip card removed')
    left = len(re.findall(r'href="https://yesim\.tpx\.li', s)) + len(re.findall(r'(?i)yesim', re.sub(r'<script.*?</script>', '', s, flags=re.S)))
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
    print('OK   %-40s %s' % (stem, '; '.join(notes)))
