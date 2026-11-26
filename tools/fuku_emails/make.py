"""Fuku's gift emails (MailerLite automation "Japan gift emails (Fuku's lessons 1-4)", 26 Nov 2026).
Builds the HTML of each lesson email (lesson<n>.html) and its plain text (lesson<n>.txt) into an output folder, to paste
into MailerLite with update_automation_email_content / update_automation_email (plain text max 1000 characters).
The phrases come from api/_japan_lessons.js (the same list the /japan "Hear Fuku say it" card uses).
The postal address for the legally required footer is NOT in this public repo: pass it in FUKU_POSTAL, lines split by
"|" (for example FUKU_POSTAL="Company|Street, City|Country"). Run from the repo root:
    FUKU_POSTAL="..." python3 -I tools/fuku_emails/make.py /path/to/out
Facts only from docs/research/*-sources.md; no partner names in our own words; no prices. Lessons 5-8 go in EM below.
"""
import sys
import html, json, urllib.parse, os, re
LES = json.loads(re.search(r"export const LESSONS = (\{.*?\});\s*$", open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'api', '_japan_lessons.js'), encoding='utf-8').read(), re.S).group(1))
OUT = sys.argv[1] if len(sys.argv) > 1 else sys.exit('usage: make.py OUT_DIR')
POSTAL = [x.strip() for x in os.environ.get('FUKU_POSTAL', '').split('|') if x.strip()]
if len(POSTAL) < 2: sys.exit('set FUKU_POSTAL (the footer address, lines split by |)')
os.makedirs(OUT, exist_ok=True)
SITE = 'https://www.packsmartapp.com'
F = "font-family:'DM Sans',Arial,Helvetica,sans-serif;"
e = html.escape
POCKET = [('haneda','Haneda Airport','haneda-icon-v2-192.png','Haneda'),('narita','Narita Airport','narita-icon-v2-192.png','Narita'),
  ('kix','Kansai Airport','kix-icon-192.png','Kansai'),('new-chitose','New Chitose Airport','new-chitose-icon-192.png','New Chitose'),
  ('tokyo','Tokyo Station','tokyo-icon-192.png','Tokyo'),('shinjuku','Shinjuku Station','shinjuku-icon-192.png','Shinjuku'),
  ('ueno','Ueno Station','ueno-icon-192.png','Ueno'),('kyoto','Kyoto Station','kyoto-icon-192.png','Kyoto'),
  ('osaka','Shin-Osaka and Umeda','osaka-icon-192.png','Osaka'),('sapporo','Sapporo Station','sapporo-icon-192.png','Sapporo')]

def icon_row(title, lst, n):
    w = 100 // 6
    cells = ''.join(f'<td width="{w}%" align="center" valign="top" style="padding:0 1px 6px;"><a href="{SITE}/{k}-pocket?src=gift{n}" style="text-decoration:none;color:#0f0f23;">'
        f'<img src="{SITE}/images/{img}" width="46" height="46" alt="{e(name)} Pocket Guide" style="display:block;margin:0 auto;border-radius:12px;border:0;">'
        f'<span style="display:block;margin-top:5px;font-size:11px;font-weight:bold;color:#0f0f23;line-height:1.2;{F}">{e(short)}</span></a></td>' for k, name, img, short in lst)
    pad = f'<td width="{100 - w*len(lst)}%">&nbsp;</td>' if len(lst) < 6 else ''
    return (f'<p style="margin:4px 4px 6px;font-size:11px;font-weight:bold;letter-spacing:1px;text-transform:uppercase;color:#5a6378;{F}">{title}</p>'
            f'<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="margin:0 0 10px;"><tr>{cells}{pad}</tr></table>')

def box(inner, bg='#e6faf5', border=''):
    return f'<div style="background:{bg};{border}border-radius:14px;padding:16px;margin:22px 0;font-size:14px;line-height:1.55;color:#0f0f23;{F}">{inner}</div>'

def footer_offer(kind, n):
    if kind == 'pocket':
        return box('<p style="margin:0 4px 4px;"><b>&#128241; Fuku&rsquo;s phrases, offline, at the station</b></p>'
                   '<p style="margin:0 4px 12px;color:#3f4a5c;">Every Pocket Guide has 80+ phrases plus exits, platforms, lockers and ATMs. No app, works offline. Tap the one you&rsquo;ll use:</p>'
                   + icon_row('Airports', POCKET[:4], n) + icon_row('Stations', POCKET[4:], n))
    if kind == 'esim':
        return box('<b>&#128246; Data from the minute you land</b><br>Maps, train apps and Packy need data at the airport. '
                   f'<a href="https://airalo.tpx.li/4TNBGGOO" rel="nofollow noopener sponsored" style="color:#0a8f78;font-weight:bold;">See eSIM data plans for Japan</a> '
                   '<span style="color:#8a93a6;font-size:12px;">(partner link)</span>', '#ffffff', 'border:1px solid #e3e8ec;')
    if kind == 'packing':
        return box('<b>&#129523; Packing for Japan?</b><br>Our checklist covers the small things that matter there, like cash for small shops and good socks (you&rsquo;ll take your shoes off more than you think). '
                   f'<a href="{SITE}/blog/japan-travel-packing-guide?src=gift{n}" style="color:#0a8f78;font-weight:bold;">Open the Japan packing list</a>', '#ffffff', 'border:1px solid #e3e8ec;')
    if kind == 'plan':
        return box('<b>&#128506;&#65039; Want the whole trip laid out?</b><br>Plan My Trip builds a day-by-day plan for your dates and your group, with weather and a packing list. '
                   f'<a href="{SITE}/?dest=Japan&amp;src=gift{n}#plan" style="color:#0a8f78;font-weight:bold;">Build my Japan plan</a>', '#ffffff', 'border:1px solid #e3e8ec;')

    if kind == 'insurance':
        return box('<b>&#129658; Don&rsquo;t forget travel insurance</b><br>Japan&rsquo;s tourism body ends its guide for visitors who fall ill with: &ldquo;Don&rsquo;t forget to buy travel insurance!&rdquo; '
                   '<a href="https://www.safetywing.com/nomad-insurance?referenceID=26492686&amp;utm_source=26492686&amp;utm_medium=Ambassador" rel="nofollow noopener sponsored" style="color:#0a8f78;font-weight:bold;">See SafetyWing travel medical insurance</a> '
                   '<span style="color:#8a93a6;font-size:12px;">(partner link)</span>', '#ffffff', 'border:1px solid #e3e8ec;')

def share(n):
    msg = 'Fuku the lucky cat teaches a few Japanese travel phrases by email. Handy for our trip: ' + SITE + '/japan?src=wa_gift#words'
    wa = 'https://wa.me/?text=' + urllib.parse.quote(msg)
    return box('<b>&#128140; Travelling with someone?</b><br>Send them Fuku&rsquo;s lessons so you both know what to say.'
               '<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin-top:10px;"><tr>'
               f'<td style="padding:0 8px 0 0;"><a href="{e(wa)}" style="display:inline-block;background:#25D366;color:#ffffff;text-decoration:none;font-weight:bold;font-size:14px;padding:9px 16px;border-radius:20px;white-space:nowrap;{F}">WhatsApp</a></td>'
               f'<td><a href="{{$forward}}" style="display:inline-block;background:#0f0f23;color:#ffffff;text-decoration:none;font-weight:bold;font-size:14px;padding:9px 16px;border-radius:20px;white-space:nowrap;{F}">Email a friend</a></td>'
               '</tr></table>'
               f'<p style="margin:10px 0 0;font-size:13px;color:#5a6378;">Got this from a friend? <a href="{SITE}/japan?src=email_fwd#words" style="color:#0a8f78;font-weight:bold;">Get Fuku&rsquo;s lessons yourself</a></p>',
               '#FFF5F7', 'border:1px solid #F7D3DC;')

def phrases(n):
    sep = '<tr><td colspan="2" style="border-top:1px solid #d9f0ea;font-size:0;line-height:0;">&nbsp;</td></tr>'
    rows = []
    for i, (r, ja, m) in enumerate(LES[str(n)]['phrases']):
        url = f'{SITE}/japan?say={n}-{i+1}&amp;src=gift{n}_say'
        rows.append(f'<tr><td style="padding:11px 4px 11px 14px;{F}"><div style="font-weight:bold;font-size:17px;color:#0f0f23;">{e(r)}</div>'
                    f'<div lang="ja" style="font-size:15px;color:#0a8f78;font-weight:bold;margin-top:2px;">{e(ja)}</div>'
                    f'<div style="font-size:14px;color:#5a6378;margin-top:2px;">{e(m)}</div></td>'
                    f'<td width="64" align="right" valign="middle" style="padding:0 12px 0 0;"><a href="{url}" title="Hear Fuku say it" style="display:inline-block;background:#00C9A7;color:#ffffff;text-decoration:none;font-weight:bold;font-size:12px;line-height:1;padding:8px 9px;border-radius:16px;white-space:nowrap;{F}">&#128266; Hear</a></td></tr>')
    return (f'<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background:#ffffff;border:1px solid #d9f0ea;border-radius:14px;margin:6px 0 4px;">{sep.join(rows)}</table>'
            f'<p style="margin:6px 2px 0;font-size:12px;color:#8a93a6;{F}">Tap &#128266; Hear and Fuku says it out loud (with your phone&rsquo;s own voice).</p>')

def p(t, extra=''):
    return f'<p style="margin:0 0 14px;font-size:16px;line-height:1.6;color:#2b3242;{F}{extra}">{t}</p>'

def fact(t):
    return (f'<div style="background:#ffffff;border-left:3px solid #00C9A7;border-radius:0 12px 12px 0;padding:12px 16px;margin:20px 0;{F}">'
            f'<div style="font-size:11px;font-weight:bold;letter-spacing:1px;color:#0a8f78;">DID YOU KNOW?</div><div style="font-size:15px;line-height:1.55;color:#0f0f23;margin-top:4px;">{t}</div></div>')

def page(n, kicker, title, body, nxt, offer, preheader):
    btn = (f'<p style="text-align:center;margin:24px 0 6px;"><a href="{SITE}/japan?src=gift{n}_ask#ask" style="display:inline-block;background:#E94560;color:#ffffff;text-decoration:none;'
           f'font-weight:bold;font-size:16px;padding:13px 24px;border-radius:24px;{F}">&#128172; Ask Packy about your trip</a></p>')
    return ('<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        '<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet"><title>' + e(title) + '</title></head>'
        f'<body style="margin:0;padding:0;background:#f4faf8;{F}">'
        f'<div style="display:none;max-height:0;overflow:hidden;opacity:0;">{e(preheader)}</div>'
        '<div style="max-width:600px;margin:0 auto;padding:26px 16px 30px;">'
        f'<p style="font-size:22px;font-weight:800;color:#0f0f23;margin:0;{F}">Pack<span style="color:#00C9A7;">Smart</span> <span style="font-size:13px;font-weight:bold;color:#5a6378;">&middot; Japan</span></p>'
        f'<div style="background:#ffffff;border-radius:18px;padding:22px 20px 18px;margin:16px 0 0;box-shadow:0 2px 10px rgba(15,15,35,.06);">'
        f'<p style="margin:0 0 6px;font-size:12px;font-weight:bold;letter-spacing:1px;text-transform:uppercase;color:#E94560;{F}">{kicker}</p>'
        f'<h1 style="margin:0 0 14px;font-size:24px;line-height:1.25;color:#0f0f23;{F}">{title}</h1>'
        + body +
        f'<p style="margin:18px 0 0;font-size:15px;color:#2b3242;{F}">Mata ne! (See you soon!)<br><b>Fuku</b> &#128049; <span style="color:#8a93a6;">with Packy</span></p>'
        + (f'<p style="margin:14px 0 0;padding-top:12px;border-top:1px dashed #d9e2e8;font-size:14px;color:#5a6378;{F}"><b>Next time:</b> {nxt}</p>' if nxt else '')
        + btn + '</div>'
        + footer_offer(offer, n) + share(n) +
        f'<div style="font-size:12px;line-height:1.6;color:#8a93a6;padding:6px 4px 0;{F}">'
        'You&rsquo;re getting this because you asked Packy or Fuku for Japan trip tips on packsmartapp.com. Facts come from official sources such as JNTO; rules change, so check before you travel.<br>'
        'Questions? Just reply to this email.<br><br><b>' + e(POSTAL[0]) + '</b><br>' + '<br>'.join(e(x) for x in POSTAL[1:]) + '<br><br>'
        '<a href="{$unsubscribe}" style="color:#8a93a6;text-decoration:underline;">Unsubscribe</a> &middot; '
        f'<a href="{SITE}/privacy-policy" style="color:#8a93a6;text-decoration:underline;">Privacy</a></div>'
        '</div></body></html>')

EM = [
 dict(n=1, kicker="Fuku's lesson 1 &middot; at the station", title="Fuku&rsquo;s station survival kit",
  pre="Plus the one thing you can do on a Shinkansen that surprises everyone.",
  body=p("Konnichiwa again! Fuku here. Packy said I&rsquo;m allowed one lesson a week, so I picked the place you&rsquo;ll be lost first: the station.")
   + phrases(1)
   + fact("Eating and drinking are generally allowed on Shinkansen trains, so a picnic on the bullet train is completely normal. &#127857;")
   + p("<b>One small favour:</b> hit reply and tell me where you&rsquo;re landing and when. Packy and I read every reply, and it helps us choose your next lessons."),
  nxt="should you tip in Japan? Fuku has opinions.", offer='pocket'),
 dict(n=2, kicker="Fuku's lesson 2 &middot; eating out", title="Should you tip in Japan?",
  pre="The answer, and 5 phrases for your first meal out.",
  body=p("Short answer: no. Japan&rsquo;s tourism body says &ldquo;it&rsquo;s not common to tip for services such as those provided in bars, cafes, restaurants, taxis, and hotels.&rdquo; A warm <b>arigatou gozaimasu</b> does the job.")
   + p("One exception: if you tip a private guide, it&rsquo;s customary to put it in an envelope.")
   + p("<b>Your first meal out:</b>", 'margin-bottom:6px;')
   + phrases(2),
  nxt="the little shop on every corner that you&rsquo;ll visit every single day.", offer='esim'),
 dict(n=3, kicker="Fuku's lesson 3 &middot; the konbini", title="Meet the konbini, your new best friend",
  pre="Cash, snacks and your IC card, around the corner. Plus 5 phrases.",
  body=p("Japan&rsquo;s convenience stores are called <b>konbini</b>, and you&rsquo;ll pop into one more often than you think. Three ways they help a traveller:")
   + '<ol style="margin:0 0 14px 20px;padding:0;font-size:16px;line-height:1.6;color:#2b3242;' + F + '">'
     '<li style="margin-bottom:6px;"><b>Cash.</b> Japan&rsquo;s tourism body lists Seven Bank ATMs, mainly inside 7-Eleven stores, among the ATMs that take overseas cards, in 12 languages. Withdrawals often cost a fee, and not every ATM is open 24 hours.</li>'
     '<li style="margin-bottom:6px;"><b>Tap to pay.</b> The IC card you use on trains (like Suica) also works at many convenience stores.</li>'
     '<li><b>Snacks and drinks</b> for the train, a hotel-room picnic or a rainy afternoon.</li></ol>'
   + p("<b>Fuku&rsquo;s konbini phrases:</b>", 'margin-bottom:6px;')
   + phrases(3),
  nxt="when do the cherry blossoms bloom, and why does it depend on where you are?", offer='packing'),
 dict(n=4, kicker="Fuku's lesson 4 &middot; spring and slowing down", title="Chasing the cherry blossoms",
  pre="They move north. Plus 5 phrases that buy you time.",
  body=p("Japan&rsquo;s cherry blossoms don&rsquo;t open all at once. &ldquo;Starting in the south and gradually moving north, the blossoms bloom between March and May depending on your location.&rdquo;")
   + fact("Drinking outdoors doesn&rsquo;t break any law in Japan, so a picnic under the blossoms, drink in hand, is part of the fun. Keep it quiet and take your litter home. &#127800;")
   + p("<b>When Japanese comes at you fast:</b>", 'margin-bottom:6px;')
   + phrases(4),
  nxt="the quiet rules of riding a Japanese train.", offer='plan'),
 dict(n=5, kicker="Fuku's lesson 5 &middot; on the train", title="The quiet rules of riding a Japanese train",
  pre="Five small habits, and the one place you can take that call.",
  body=p("Japanese trains are famously calm, and a few small habits keep them that way. Japan&rsquo;s tourism body and the rail companies ask riders to:")
   + '<ol style="margin:0 0 14px 20px;padding:0;font-size:16px;line-height:1.6;color:#2b3242;' + F + '">'
     '<li style="margin-bottom:6px;"><b>Put your phone on silent.</b> Phone calls are &ldquo;generally frowned upon&rdquo; on trains and buses.</li>'
     '<li style="margin-bottom:6px;"><b>Line up to the side of the doors</b> and let people off before you get on.</li>'
     '<li style="margin-bottom:6px;"><b>Leave priority seats</b> for older, pregnant or disabled passengers.</li>'
     '<li style="margin-bottom:6px;"><b>Take your backpack off</b> on the Shinkansen, and don&rsquo;t leave suitcases by the doors.</li>'
     '<li style="margin-bottom:6px;"><b>Save the snacks</b> for the Shinkansen: eating on local and subway trains is generally considered impolite.</li>'
     + '</ol>'
   + fact("On the Shinkansen it&rsquo;s okay to step into the corridor between cars to take a call. &#128222;")
   + p("<b>Fuku&rsquo;s train phrases:</b>", 'margin-bottom:6px;')
   + phrases(5),
  nxt="your IC card does a lot more than open ticket gates.", offer='pocket'),
 dict(n=6, kicker="Fuku's lesson 6 &middot; tickets and IC cards", title="Tap, top up, go: your IC card",
  pre="The little card that saves you from ticket machines. Plus 5 phrases.",
  body=p("Japan&rsquo;s rechargeable IC cards (Suica, PASMO, ICOCA and friends) are the easiest way to ride. Tap in at the gate, tap out at your destination, and the fare comes off the card.")
   + '<ol style="margin:0 0 14px 20px;padding:0;font-size:16px;line-height:1.6;color:#2b3242;' + F + '">'
     '<li style="margin-bottom:6px;"><b>Made for visitors:</b> Welcome Suica and TOURIST PASMO need no deposit. (Welcome Suica is sold in the Tokyo area and is valid for up to 28 days.)</li>'
     '<li style="margin-bottom:6px;"><b>Top up at almost any station:</b> put the card into a ticket machine, choose an amount, add cash.</li>'
     '<li style="margin-bottom:6px;"><b>Gate won&rsquo;t open?</b> The tap missed or the balance is low. Top up at a ticket machine or a fare adjustment machine.</li>'
     '<li style="margin-bottom:6px;"><b>On buses</b> tap when you get on and again when you get off. Some areas and highway buses don&rsquo;t take IC cards, so look for the IC logo.</li>'
     + '</ol>'
   + fact("IC cards also pay at many vending machines, shops and station lockers. &#129683;")
   + p("<b>Fuku&rsquo;s ticket phrases:</b>", 'margin-bottom:6px;')
   + phrases(6),
  nxt="what Japan&rsquo;s four seasons feel like, and what to pack for each.", offer='plan'),
 dict(n=7, kicker="Fuku's lesson 7 &middot; the seasons", title="Japan&rsquo;s four seasons, and what to pack",
  pre="From cherry blossoms to powder snow, in one email.",
  body=p("Japan has four very different seasons. Japan&rsquo;s tourism body gives these averages for Tokyo:")
   + '<ol style="margin:0 0 14px 20px;padding:0;font-size:16px;line-height:1.6;color:#2b3242;' + F + '">'
     '<li style="margin-bottom:6px;"><b>Spring (March to May):</b> about 10&ndash;20&deg;C. Cherry blossoms, and Golden Week crowds at the end of April.</li>'
     '<li style="margin-bottom:6px;"><b>Summer (June to August):</b> about 25&ndash;35&deg;C and humid. The rainy season begins in May to June, and August and September may bring typhoons.</li>'
     '<li style="margin-bottom:6px;"><b>Autumn (September to November):</b> about 15&ndash;25&deg;C. The autumn leaves move south from Hokkaido between late September and early December.</li>'
     '<li style="margin-bottom:6px;"><b>Winter (December to February):</b> about 0&ndash;10&deg;C. Snow is rare in Tokyo, but the north and the mountains get Japan&rsquo;s famous powder snow.</li>'
     + '</ol>'
   + fact("Over the New Year holidays most restaurants and attractions shut down, so plan your meals around them. &#127885;")
   + p("<b>Weather makes perfect small talk:</b>", 'margin-bottom:6px;')
   + phrases(7),
  nxt="who to call if something goes wrong. (Good news: Japan makes it easy.)", offer='packing'),
 dict(n=8, kicker="Fuku's lesson 8 &middot; help", title="Help is easy to find in Japan",
  pre="Two numbers, one hotline and five phrases you hope you won&rsquo;t need.",
  body=p("Japan&rsquo;s tourism body says Japan &ldquo;is considered one of the safest countries in the world,&rdquo; and the tap water is safe to drink. Still, it&rsquo;s good to know who to call:")
   + '<ol style="margin:0 0 14px 20px;padding:0;font-size:16px;line-height:1.6;color:#2b3242;' + F + '">'
     '<li style="margin-bottom:6px;"><b>110</b> for the police, <b>119</b> for fire or an ambulance.</li>'
     '<li style="margin-bottom:6px;"><b>Japan Visitor Hotline: 050-3816-2787.</b> Open 24 hours, every day, in English, Chinese and Korean, for emergencies and everyday travel questions.</li>'
     '<li style="margin-bottom:6px;"><b>Had something stolen?</b> Go to a <i>koban</i>, the small local police box. You&rsquo;ll need a police report for a new passport or an insurance claim.</li>'
     '<li style="margin-bottom:6px;"><b>Carry your passport.</b> Japan asks visitors to keep it with them at all times.</li>'
     + '</ol>'
   + p("<b>Tip:</b> save the hotline number in your phone before you fly.")
   + p("<b>Five phrases you hope you won&rsquo;t need:</b>", 'margin-bottom:6px;')
   + phrases(8)
   + p("That&rsquo;s the end of my first eight lessons. Keep them handy for your trip, and I&rsquo;ll be back when there&rsquo;s something worth knowing.", 'margin-top:16px;'),
  nxt="", offer='insurance'),
]
for m in EM:
    # escaped phrase text: undo double escaping of entities we wrote on purpose
    h = page(m['n'], m['kicker'], m['title'], m['body'], m['nxt'], m['offer'], m['pre']).replace('&amp;rsquo;', '&rsquo;')
    open(os.path.join(OUT, f'lesson{m["n"]}.html'), 'w').write(h)
print('ok')

# ---- plain text versions (MailerLite allows 1000 characters)
S = SITE
T = {
 1: ("Fuku's station survival kit", "Konnichiwa again! Fuku here. One lesson a week, starting where you'll be lost first: the station.",
     "Did you know? Eating and drinking are generally allowed on Shinkansen trains.\n\nOne small favour: hit reply and tell me where you're landing and when.",
     "should you tip in Japan?"),
 2: ("Should you tip in Japan?", "Short answer: no. Japan's tourism body says it's not common to tip in bars, cafes, restaurants, taxis and hotels. A warm arigatou gozaimasu does the job.",
     "", "the little shop on every corner you'll visit every day."),
 3: ("Meet the konbini, your new best friend", "Japan's convenience stores (konbini) help with cash (JNTO lists Seven Bank ATMs, mainly in 7-Eleven stores, for overseas cards), tap-to-pay with your IC card, and snacks for the train.",
     "", "when do the cherry blossoms bloom?"),
 4: ("Chasing the cherry blossoms", "They don't open all at once: starting in the south and moving north, they bloom between March and May depending on where you are.",
     "", "the quiet rules of riding a Japanese train."),
 5: ("The quiet rules of riding a Japanese train", "Japanese trains are calm. Put your phone on silent (calls are frowned upon), line up beside the doors and let people off first, leave priority seats free, and save snacks for the Shinkansen.",
     "Did you know? On the Shinkansen it's okay to take a call in the corridor between cars.", "your IC card does more than open ticket gates."),
 6: ("Tap, top up, go: your IC card", "Tap in, tap out, and the fare comes off the card. Welcome Suica and TOURIST PASMO need no deposit. Top up at station ticket machines. Gate won't open? Top up at a fare adjustment machine.",
     "", "Japan's four seasons, and what to pack."),
 7: ("Japan's four seasons, and what to pack", "Tokyo averages (JNTO): spring about 10-20C, summer 25-35C and humid, autumn 15-25C, winter 0-10C. Rainy season from May to June; typhoons possible in August and September.",
     "Did you know? Over New Year most restaurants and attractions shut down.", "who to call if something goes wrong."),
 8: ("Help is easy to find in Japan", "Police 110. Fire or ambulance 119. Japan Visitor Hotline 050-3816-2787 (24 hours, English, Chinese, Korean). Something stolen? Go to a koban (police box). Carry your passport.",
     "That's the end of my first eight lessons. Keep them handy for your trip!", ""),
}
for n, (title, intro, extra, nxt) in T.items():
    ph = "\n".join(f"- {r} = {m}" for r, ja, m in LES[str(n)]['phrases'])
    t = (f"{title}\n\n{intro}\n\n{ph}\nHear Fuku say them: {S}/japan?say={n}-1&src=gift{n}_say\n\n" + (extra + "\n\n" if extra else "") +
         (f"Next time: {nxt}\n\n" if nxt else "") + f"Ask Packy about your trip: {S}/japan?src=gift{n}_ask#ask\n\nMata ne! Fuku\n\n"
         + ", ".join(POSTAL) + "\nUnsubscribe: {$unsubscribe}")
    open(os.path.join(OUT, f'lesson{n}.txt'), 'w').write(t)
    print('lesson', n, 'plain text', len(t), 'characters' + ('  TOO LONG (max 1000)' if len(t) > 1000 else ''))
