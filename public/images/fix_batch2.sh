#!/bin/bash
# PackSmart batch 2: Iran/Cape Verde/Henley, Malaysia visa-free + MDAC, Thai baht/ATM, Singapore fee in USD, Nov-2026 dates
set -e
if [ -z "$PS_ROOT" ]; then cd ~/packsmart && git pull -q; export PS_ROOT="$PWD"; REAL=1; fi
python3 - <<'PYEOF'
import os, re, sys, json, glob
ROOT = os.environ['PS_ROOT']
BLOG = os.path.join(ROOT, 'public/blog')
files = {}      # path -> new text
orig = {}
def get(p):
    if p not in files:
        with open(p, encoding='utf-8') as f: t = f.read()
        orig[p] = t; files[p] = t
    return files[p]
def abort(msg): print('ABORT:', msg); sys.exit(2)
def rep(p, old, new, n=1, why=''):
    t = get(p); c = t.count(old)
    if new and old in new and new in t: return
    if c == n: files[p] = t.replace(old, new); return
    if c == 0 and (new == '' or new in t): return
    abort('%s | %s | found %d expected %d' % (os.path.basename(p), why, c, n))
def rx(p, pat, new, n=1, why='', flags=re.S):
    t = get(p); ms = list(re.finditer(pat, t, flags))
    if len(ms) == n: files[p] = re.sub(pat, lambda m: new, t, flags=flags); return
    if len(ms) == 0 and new in t: return
    abort('%s | %s | regex found %d expected %d' % (os.path.basename(p), why, len(ms), n))
B = lambda s: os.path.join(BLOG, s)

# ---------- Thailand itinerary: baht rate and ATM fee ----------
IT = B('thailand-7-day-itinerary-mid-range.html')
rep(IT, 'ATMs charge a ฿220 ($6) foreign fee per withdrawal', 'ATMs charge a ฿220–350 ($7–10) foreign fee per withdrawal', why='atm jsonld')
rep(IT, 'ATMs charge a flat ฿220 (~$6) foreign card fee per withdrawal', 'ATMs charge a foreign card fee of ฿220&ndash;350 (~$7&ndash;10) per withdrawal, depending on the bank', why='atm note')
rep(IT, 'ATMs charge ฿220 ($6) per foreign withdrawal', 'ATMs charge ฿220&ndash;350 ($7&ndash;10) per foreign withdrawal', why='atm faq')
rep(IT, 'has been stable at roughly ฿35&ndash;37 to $1 USD through early 2026', 'has traded at roughly ฿31&ndash;34 to $1 USD during 2026 (about ฿33.5 in mid-November)', why='baht rate')

# ---------- Singapore guide: fee shown in USD first, INR in brackets ----------
SG = B('singapore-travel-packing-guide-from-india.html')
rep(SG, "The government fee is about ₹2,100 plus the agent's service charge (up to about ₹1,300)", "The government fee is about US$22 (₹2,100) plus the agent's service charge (up to about US$14, or ₹1,300)", n=2, why='sg fee faq')
rep(SG, "Government fee about &#x20B9;2,100 plus the agent's service charge of up to about &#x20B9;1,300.", "Government fee about US$22 (&#x20B9;2,100) plus the agent's service charge of up to about US$14 (&#x20B9;1,300).", why='sg fee row')
rep(SG, '<td>&#x20B9;2,600&ndash;3,400</td><td>&#x20B9;2,600&ndash;3,400</td>', '<td>&#x20B9;2,600&ndash;3,400 (~US$28&ndash;36)</td><td>&#x20B9;2,600&ndash;3,400 (~US$28&ndash;36)</td>', why='sg budget visa row')

# ---------- Malaysia guide: visa-free + MDAC (eNTRI is obsolete) ----------
MY = B('malaysia-travel-packing-guide-from-india.html')
rep(MY, 'Covers eNTRI visa,', 'Covers 30-day visa-free entry and the MDAC arrival card,', why='my desc')
rep(MY, "Best part? Indians get an <strong>eNTRI visa that's valid for 15 days and completely free</strong> (or pay for eVisa for longer stays).",
    "Best part? Indians can currently enter <strong>visa-free for up to 30 days</strong> (the exemption runs to 31 December 2026, so check whether it has been extended if you travel later). The only advance paperwork is the free Malaysia Digital Arrival Card (MDAC); longer stays need an eVisa.", why='my intro')
rep(MY, "<p>Indian citizens can enter Malaysia with an <strong>eNTRI visa</strong> or the standard <strong>eVisa</strong>. The eNTRI is the most popular option &mdash; it's free, quick to process, and valid for 15 days (single entry).</p>",
    "<p>Indian citizens can currently enter Malaysia <strong>without a visa</strong> for tourism, short business or family visits of up to 30 days. This exemption is in force until <strong>31 December 2026</strong>, so check the Malaysian Immigration Department or the High Commission before booking trips beyond that date. The old eNTRI scheme is not needed for visa-free stays, but you must still file the free <strong>Malaysia Digital Arrival Card (MDAC)</strong> online.</p>", why='my visa para')
rx(MY, r'<table class="checklist-table">\s*<tr><th>Visa Type</th>.*?</table>',
   '<table class="checklist-table">\n<tr><th>Entry route</th><th>Cost</th><th>Stay</th><th>What to do</th></tr>\n<tr><td><strong>Visa-free entry</strong></td><td>Free</td><td>Up to 30 days (until 31 Dec 2026)</td><td>No application. Show your passport, return ticket, accommodation and funds at immigration</td></tr>\n<tr><td><strong>MDAC arrival card</strong></td><td>Free</td><td>Not a visa</td><td>File online within 3 days before arrival and keep the confirmation</td></tr>\n<tr><td><strong>eVisa</strong></td><td>Check the official portal</td><td>Longer stays, work or study</td><td>Apply at malaysiavisa.imi.gov.my before you travel</td></tr>\n</table>', why='my table')
rx(MY, r'<div class="tip-box">\s*<strong>&#x1F4A1; Pro Tip:</strong> Apply for eNTRI.*?</div>',
   '<div class="tip-box">\n    <strong>&#x1F4A1; Pro Tip:</strong> File the MDAC only on the official Immigration Department site (imigresen-online.imi.gov.my/mdac/main). It is free, so never pay a third-party site. It can only be submitted within 3 days before you arrive, so do it 1&ndash;2 days before your flight. At immigration, officers can ask for a return or onward ticket, a hotel booking and proof of funds, so carry them (printed or on your phone).\n</div>', why='my tip')
rep(MY, '<tr><td>Visa (eNTRI/eVisa)</td><td>Free (eNTRI)</td><td>&#x20B9;3,800&ndash;5,700 (eVisa)</td></tr>', '<tr><td>Visa</td><td>Free (visa-free entry)</td><td>Free (visa-free entry)</td></tr>', why='my budget visa')
rx(MY, r'No, Indians can enter Malaysia visa-free for up to 30 days through the eNTRI.*?one of the easiest destinations from India\.',
   'No, not for stays of up to 30 days. Indian passport holders can enter Malaysia visa-free for tourism for up to 30 days, and the exemption is currently valid until 31 December 2026 (check whether it has been extended if you travel later). You must file the free Malaysia Digital Arrival Card (MDAC) online within 3 days before arrival, and carry a passport valid for at least 6 months, a return or onward ticket, accommodation details and proof of sufficient funds. Longer stays, work or study need a visa.', n=2, why='my faq')
rep(MY, "<tr><td>6 weeks before</td><td>Apply for eNTRI visa online. Book return flights. Block first few nights' accommodation in KL</td></tr>", "<tr><td>6 weeks before</td><td>Book return flights (check the visa-free rule is still in force for your dates). Block first few nights' accommodation in KL</td></tr>", why='my checklist 6w')
rep(MY, '<tr><td>1 day before</td><td>Print eNTRI approval letter. Online check-in.', '<tr><td>1 day before</td><td>File the free MDAC online (within 3 days of arrival) and screenshot the confirmation. Online check-in.', why='my checklist 1d')
rx(MY, r'Last updated: March 2026', 'Last updated: November 2026 &middot; Entry rules checked 15 Nov 2026', why='my stamp')

# ---------- Visa-free countries page ----------
VF = B('visa-free-countries-indian-passport.html')
rep(VF, '<tr><td>Iran</td><td>Middle East</td><td>30 days</td><td><span class="badge badge-free">Visa-Free</span></td></tr>', '', why='iran row')
rep(VF, '<tr><td>Cape Verde</td><td>Africa</td><td>30 days</td><td>&euro;30</td></tr>', '', why='cape verde row')
voa_old = "<p>These countries issue a visa when you land at the airport. You'll usually need a return ticket, proof of accommodation, and sometimes a fee in local currency or USD.</p>"
rep(VF, voa_old, voa_old + '\n<p><strong>Recent changes:</strong> Cape Verde ended visa on arrival for Indians on 1 January 2026, so a visa is now needed before you travel. Iran suspended its visa waiver for Indians from 22 November 2025 and is no longer visa-free. Bolivia and Nicaragua have also reportedly ended visa on arrival. Check the embassy site before booking.</p>', why='recent changes note')
rep(VF, "India's visa-free access to Malaysia is extended until December 2026.", "India's visa-free access to Malaysia is extended until 31 December 2026. File the free Malaysia Digital Arrival Card (MDAC) online within 3 days before you arrive.", why='malaysia card')
rep(VF, 'Good news &mdash; Indian passport holders can now visit over 60 countries without applying for a visa in advance.', 'Good news &mdash; Indian passport holders can now visit around 55 destinations without applying for a visa in advance.', why='intro count')
rep(VF, 'the list of hassle-free destinations keeps growing every year', 'the list changes every year, so always check the latest rules before you book', why='intro list')
rep(VF, 'The Indian passport has climbed to 80th place on the Henley Passport Index in 2026, up from 85th the previous year. Indian citizens now have access to approximately 60 destinations through visa-free entry, visa-on-arrival, or electronic travel authorisation.',
    'The Indian passport ranks 84th on the Henley Passport Index (October 2026 edition), with access to 55 destinations through visa-free entry, visa-on-arrival, or electronic travel authorisation. That is down from 57 a year earlier, after Iran, Cape Verde, Bolivia and Nicaragua tightened their rules for Indian travellers.', why='henley para')
rep(VF, 'Singapore (192 destinations), Japan (188)', 'Singapore (over 190 destinations), Japan and South Korea (around 188)', why='henley leaders')
rep(VF, "India's improving ranking reflects growing diplomatic relationships and trade agreements that are making international travel increasingly accessible for Indian travellers.", 'Access still changes quickly: some countries have added visa-free entry for Indians, while others have recently withdrawn it.', why='henley trend')
rep(VF, 'India now offers better travel mobility than neighbouring Pakistan (98th, 31 destinations) and Bangladesh (95th, 37 destinations), making it the strongest passport in South Asia alongside Malaysia.', "Henley's October 2026 count is 55 destinations for Indian passport holders (visa-free, visa-on-arrival or electronic authorisation). The tables below list the main ones, but always confirm with the embassy before you book.", why='key stat')
rep(VF, 'With 60+ destinations available', 'With around 55 destinations available', why='closing')
rep(VF, 'Complete list of 60+ visa-free', 'Complete list of visa-free', n=2, why='meta desc')
rep(VF, 'content="60+ countries Indians can visit without a visa in 2026.', 'content="Around 55 destinations Indians can visit without a visa in 2026.', why='og desc')
rep(VF, '<div class="meta">Last updated: March 2026</div>', '<div class="meta">Last updated: November 2026 &middot; Re-checked 15 Nov 2026: Thailand, Malaysia, Iran, Cape Verde</div>', why='vf stamp')

# ---------- Malaysia web story ----------
WS = os.path.join(ROOT, 'public/web-stories/malaysia-travel-guide.html')
if os.path.exists(WS):
    rep(WS, 'Free eNTRI visa, ₹30K–50K budget trips, and amazing street food — swipe through our quick Malaysia guide.', '30-day visa-free entry, ₹30K–50K budget trips, and amazing street food — swipe through our quick Malaysia guide.', why='ws og')
    rep(WS, 'Free eNTRI visa, ₹30K–50K budget trips, and amazing street food.', '30-day visa-free entry, ₹30K–50K budget trips, and amazing street food.', why='ws tw')
    rep(WS, 'eNTRI is Completely FREE', '30 Days Visa-Free', why='ws h2')
    rep(WS, '<span class="highlight">Zero cost, instant approval</span> on entri.gov.my. Valid for <span class="highlight">15 days, single entry</span>. Best visa deal in Southeast Asia.', '<span class="highlight">No visa fee</span> for stays up to <span class="highlight">30 days</span>, valid until 31 Dec 2026. File the free <span class="highlight">MDAC arrival card</span> online within 3 days before you land.', why='ws p')
    rep(WS, '"dateModified": "2026-04-03"', '"dateModified": "2026-11-15"', why='ws dm')
else:
    print('note: Malaysia web story not found, skipped')

# ---------- Generic: stale "Last updated" stamps -> November 2026 ----------
stamp_pat = re.compile(r'Last updated: (March|April|August) 2026')
dm_pat = re.compile(r'("dateModified":\s*")\d{4}-\d{2}-\d{2}(")')
restamped = []
for p in sorted(glob.glob(os.path.join(BLOG, '*.html'))):
    t = get(p)
    if stamp_pat.search(t):
        t = stamp_pat.sub('Last updated: November 2026', t)
        t = dm_pat.sub(r'\g<1>2026-11-15\2', t)
        files[p] = t; restamped.append(os.path.basename(p))
# pages edited above for facts also get the new dateModified
JA = B('japan-travel-packing-guide-from-india.html')   # fully reviewed earlier today; it has no visible stamp, so only the structured date is updated
for p in (IT, SG, MY, VF, JA):
    files[p] = dm_pat.sub(r'\g<1>2026-11-15\2', files[p])

# ---------- Sitemap lastmod ----------
SM = os.path.join(ROOT, 'public/sitemap.xml')
slugs = set(restamped) | {os.path.basename(p) for p in (IT, SG, MY, VF, JA)}
sm_done = 0
if os.path.exists(SM):
    s = get(SM)
    for f in sorted(slugs):
        slug = f[:-5]
        pat = r'(<loc>https://www\.packsmartapp\.com/blog/' + re.escape(slug) + r'</loc>\s*<lastmod>)[^<]+(</lastmod>)'
        ns, k = re.subn(pat, r'\g<1>2026-11-15\2', s)
        if k: s = ns; sm_done += 1
    if os.path.exists(WS):
        ns, k = re.subn(r'(<loc>https://www\.packsmartapp\.com/web-stories/malaysia-travel-guide</loc>\s*<lastmod>)[^<]+(</lastmod>)', r'\g<1>2026-11-15\2', s)
        if k: s = ns
    files[SM] = s

# ---------- Validate JSON-LD, then write ----------
changed = [p for p in files if files[p] != orig[p]]
for p in changed:
    if p.endswith('.html'):
        for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', files[p], re.S):
            try: json.loads(m.group(1))
            except Exception as e: abort('invalid JSON-LD in %s: %s' % (os.path.basename(p), e))
if not changed:
    print('Nothing to change (already applied)'); sys.exit(0)
for p in changed:
    with open(p, 'w', encoding='utf-8') as f: f.write(files[p])
print('Files changed: %d | restamped pages: %d | sitemap entries updated: %d' % (len(changed), len(restamped), sm_done))
for p in changed:
    if not os.path.basename(p) in restamped: print('   ', os.path.relpath(p, ROOT))
PYEOF
if [ -n "$REAL" ]; then
  cd ~/packsmart
  git add -A public
  if git diff --cached --quiet; then echo "Nothing to commit."; else
    git commit -q -m "Iran/Cape Verde/Henley fixes, Malaysia visa-free + MDAC (eNTRI retired), Thai baht/ATM, Singapore fee in USD, Nov 2026 last-updated dates" -m "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01AjjcPdQ12tVHZaMa63W4kF"
    git push -q && echo "Pushed."
  fi
fi
