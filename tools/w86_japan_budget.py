#!/usr/bin/env python3
"""
w86: Japan trip budget calculator, a SKETCH for the owner's review (27 Nov 2026). Preview branch only for now.

Owner's idea: Packy gets "total cost for a family of 4, 10 days, mostly Tokyo" questions; a calculator where the
reader enters their trip and gets an itemised result fits them better than the itinerary planner.

How it works: the reader enters travellers (adults, children 6-11, under 6), nights per area (Tokyo, Kyoto/Osaka,
Hokkaido), the airports, how they get into town, taxi rides, and (optionally) their own hotel, food and flight
figures. The result lists:
  - costs we have CHECKED prices for, each with its official source and checked date (all from
    docs/research/japan-prices-sources.md, checked 24 Nov 2026): airport to city, Tokyo and Sapporo transport day
    tickets, taxis (JNTO's range), the Japan Rail Pass, the departure tax;
  - costs the reader typed in (hotel, food, flights);
  - costs not priced yet (flights unless typed, theme parks and zoos, Kyoto and Osaka city transport, regular
    Shinkansen fares), each with a way to find the price (internal page or partner link).
The total says what it covers. No made-up numbers: anything without an official figure says "not priced yet".

Partner links here reuse existing tracked links for the sketch; before launch they need the page's own Sub IDs.
Writes public/japan-budget.html (noindex while it is a sketch). Run:  python3 tools/w86_japan_budget.py
"""
import json, os

PUB = os.path.join(os.getcwd(), "public")
CHECKED = "24 Nov 2026"

# Every price here is copied from docs/research/japan-prices-sources.md (official pages). [adult, child 6-11] in yen.
DATA = {
    "airport": {
        "narita": {"name": "Narita", "ways": [
            {"id": "skyliner", "name": "Keisei Skyliner to Ueno / Nippori", "a": 2580, "c": 1290, "src": "Keisei", "url": "https://www.keisei.co.jp/keisei/tetudou/skyliner/us/skyliner/purchase.php"},
            {"id": "nex", "name": "Narita Express round-trip ticket (both rides)", "a": 5200, "c": 2600, "src": "JR East N'EX TOKYO Round Trip Ticket", "url": "https://www.jreast.co.jp/en/multi/pass/nex.html"},
            {"id": "limo", "name": "Airport Limousine Bus to Tokyo Station", "a": 3100, "c": 1550, "src": "Airport Limousine Bus", "url": "https://www.limousinebus.co.jp/en/timetable/detail/Narita-Tokyo/?dir=1"},
            {"id": "taxi", "name": "Fixed-fare taxi to Shinjuku, Shibuya, Minato (zone D)", "car": [31500, 32500], "src": "Narita Airport (plus expressway tolls; late-night surcharge)", "url": "https://www.narita-airport.jp/en/access/taxi/"},
        ]},
        "haneda": {"name": "Haneda", "ways": [
            {"id": "limo", "name": "Airport Limousine Bus to Tokyo Station", "a": 1200, "c": 600, "src": "Airport Limousine Bus", "url": "https://www.limousinebus.co.jp/en/timetable/detail/Haneda-Tokyo/?dir=1"},
            {"id": "limo2", "name": "Airport Limousine Bus to Shinjuku", "a": 1400, "c": 700, "src": "Airport Limousine Bus (daytime)", "url": "https://www.limousinebus.co.jp/en/timetable/detail/Haneda-Shinjuku/?dir=1"},
            {"id": "keikyu", "name": "Keikyu train to Shinagawa", "a": 330, "c": None, "src": "Keikyu (adult fare; child fare not checked)", "url": "https://www.haneda-tokyo-access.com/en/ride/fares.html"},
        ]},
        "kansai": {"name": "Kansai (KIX)", "ways": [
            {"id": "haruka-k", "name": "HARUKA to Kyoto (visitor one-way ticket, bought online)", "a": 2700, "c": 1350, "src": "JR West", "url": "https://www.westjr.co.jp/travel-information/en/tickets-passes/oneway/haruka/"},
            {"id": "haruka-o", "name": "HARUKA to Shin-Osaka (visitor one-way ticket, bought online)", "a": 1900, "c": 950, "src": "JR West", "url": "https://www.westjr.co.jp/travel-information/en/tickets-passes/oneway/haruka/"},
        ]},
        "chitose": {"name": "New Chitose (Sapporo)", "ways": [
            {"id": "bus", "name": "Airport bus to Sapporo Station", "a": 1500, "c": 750, "src": "Hokkaido Chuo Bus", "url": "https://www.chuo-bus.co.jp/airport/timetable/?ope=det&n=34&o=2&t=14"},
        ]},
    },
    "tokyoTicket": {"a": 2000, "c": 1000, "days": 3, "src": "Tokyo Subway Ticket, 72 hours (Toei and Tokyo Metro)", "url": "https://www.kotsu.metro.tokyo.jp/eng/tickets/"},
    "sapporoDay": {"a": 830, "c": 420, "src": "Sapporo subway one-day ticket (weekday)", "url": "https://www.city.sapporo.jp/st/s109/23564.html"},
    "taxi": {"lo": 2500, "hi": 3000, "src": "JNTO: a 7 km daytime ride in Tokyo, about 25 minutes", "url": "https://www.japan.travel/en/plan/getting-around/taxis/"},
    "jrpass": {"a": 50000, "c": 25000, "src": "Japan Rail Pass, 7 days, ordinary, bought online", "url": "https://japanrailpass.net/en/purchase/price/"},
    "disney": {"lo": 10900, "hi": 12400, "src": "Tokyo Disney Resort 1-Day Passport, adult, by date (28 Nov to 5 Dec 2026 shown)", "url": "https://www.tokyodisneyresort.jp/en/", "checked": "27 Nov 2026"},
    "disneyChild": {"j": 10200, "c": 5900, "src": "juniors 12 to 17 about 10,200 yen, children 4 to 11 about 5,900 yen, from a ticket seller's listing for 28 Nov 2026", "checked": "27 Nov 2026"},
    "sanrio": {"lo": 3400, "hi": 4900, "src": "Sanrio Puroland 1-day ticket, age 3 and up: retail 4,900 yen, 3,400 to 3,600 yen discounted on a ticket seller's site", "checked": "27 Nov 2026"},
    "uenozoo": {"a": 600, "src": "Ueno Zoo: general 600 yen, junior high 200 yen, free up to 6th grade", "url": "https://www.tokyo-zoo.net/english/ueno/", "checked": "27 Nov 2026"},
    "shinkansen": {"a": 13970, "c": 6980, "src": "Smart EX Service, Nozomi, reserved seat, normal season (off-peak 200 yen less, busiest 400 yen more; children half that)", "url": "https://smart-ex.jp/en/", "checked": "27 Nov 2026"},
    "tax": {"each": 3000, "src": "JNTO: International Tourist Tax", "url": "https://www.japan.travel/en/plan/international-tourist-tax/"},
}
# Ways to find what we do not price. Partner links reuse existing tracked links for the sketch (own Sub IDs before launch).
LINKS = {
    "flights": ["Compare flights to Japan", "/flights?src=budget", False],
    "parks": ["Compare Tokyo Disney and theme park tickets", "https://www.getyourguide.com/s/?q=tokyo%20theme%20park%20tickets&partner_id=D7IXONS&cmp=ps-budget", True],
    "shinkansen": ["Book Shinkansen tickets online", "https://www.japan-bullettrain.com/?via=packsmart", True],
    "transfer": ["Book a private airport transfer", "https://tpo.lu/5TSGg9Tf", True],
    "tours": ["Compare guided multi-day Japan tours", "https://www.tourradar.com/d/japan?utm_source=partner-traveller-1471305&utm_medium=ambassador&utm_campaign=budget-tours", True],
    "tours_family": ["Compare family-friendly multi-day Japan tours", "https://www.tourradar.com/srp/d-japan?age_range=13-17%2C7-12&adults=2&children=2&utm_source=partner-traveller-1471305&utm_medium=ambassador&utm_campaign=family-tours", True],
    "esim": ["See eSIM data plans for Japan", "https://airalo.tpo.lu/ndZAMVI0", True],
    "insurance": ["Get a travel medical insurance quote", "https://www.safetywing.com/nomad-insurance?referenceID=26492686&utm_source=26492686&utm_medium=Ambassador", True],
}

PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Japan Trip Budget Calculator | PackSmart</title>
<meta name="description" content="Work out what your Japan trip costs: airport trains, city transport, taxis, rail passes and the departure tax from official prices, plus your own hotel and flights.">
<meta name="robots" content="noindex,follow">
<link rel="canonical" href="https://www.packsmartapp.com/japan-budget">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">
<script async src="https://www.googletagmanager.com/gtag/js?id=G-0C4Z7VVGPE"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag("js",new Date());gtag("config","G-0C4Z7VVGPE");</script>
<style>
:root{--primary:#00C9A7;--accent:#E94560;--dark:#0f0f23;--ink:#2b3242;--muted:#5a6378;--line:#d9f0ea}
*{box-sizing:border-box}
body{margin:0;font-family:'DM Sans',sans-serif;background:#f4faf8;color:var(--ink);-webkit-text-size-adjust:100%}
a{color:#0a8f78}
.top{background:linear-gradient(135deg,#0f0f23,#1a1a3e);color:#fff;padding:14px 16px 18px}
.top a{color:#bfeee4;text-decoration:none;font-size:.85rem;font-weight:700}
.top h1{margin:8px 0 4px;font-size:1.35rem;line-height:1.25}
.top h1 span{color:var(--primary)}
.top p{margin:0;color:#cfd6e6;font-size:.9rem;line-height:1.45}
.sketch{display:inline-block;margin-top:8px;font-size:.72rem;font-weight:700;background:rgba(233,69,96,.25);color:#ffd6de;border-radius:999px;padding:3px 10px}
main{max-width:640px;margin:0 auto;padding:4px 16px 60px}
.card{background:#fff;border:1.5px solid var(--line);border-radius:18px;padding:16px;margin:16px 0 0}
.card h2{margin:0 0 4px;font-size:1.05rem;color:var(--dark)}
.card .h{margin:0 0 12px;font-size:.85rem;color:var(--muted)}
.row{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:8px 0;border-top:1px solid #eef3f2}
.row:first-of-type{border-top:0}
.row label{font-size:.92rem;font-weight:700;color:var(--dark)}
.row.stack{flex-direction:column;align-items:stretch;gap:6px}.row.stack select{max-width:100%;width:100%}
.row label small{display:block;font-weight:500;font-size:.76rem;color:var(--muted)}
.step{display:flex;align-items:center;gap:6px}
.step button{width:36px;height:36px;border-radius:12px;border:1.5px solid var(--line);background:#f4faf8;font:inherit;font-size:1.2rem;font-weight:700;color:var(--dark);cursor:pointer}
.step output{min-width:28px;text-align:center;font-weight:700;font-size:1.05rem}
select,input[type=number]{font:inherit;font-size:.92rem;border:1.5px solid var(--line);border-radius:12px;padding:8px 10px;background:#fff;color:var(--dark);max-width:58%}
input[type=number]{width:130px}
.res{background:var(--dark);color:#fff;border:0}
.res h2{color:#fff}
.tot{display:flex;align-items:baseline;justify-content:space-between;gap:10px;margin:4px 0 2px}
.tot b{font-size:1.9rem;color:var(--primary)}
.tot span{font-size:.85rem;color:#bfc6d6}
.pp{font-size:.85rem;color:#bfc6d6;margin:0 0 12px}
.ln{display:flex;justify-content:space-between;gap:12px;padding:9px 0;border-top:1px solid rgba(255,255,255,.1);font-size:.9rem}
.ln .l{min-width:0}
.ln .l small{display:block;color:#9aa5b5;font-size:.74rem;margin-top:2px;line-height:1.35}
.ln .l small a{color:#7fe6d3}
.ln .v{flex:0 0 auto;font-weight:700;text-align:right}
.grp{margin:14px 0 2px;font-size:.72rem;letter-spacing:.8px;text-transform:uppercase;font-weight:700;color:#7fe6d3}
.np{color:#ffb3c0;font-weight:700}
.go{display:flex;align-items:center;justify-content:space-between;gap:10px;margin:8px 0 0;padding:11px 13px;border-radius:14px;background:#fff;border:1.5px solid #e3e8ec;color:var(--dark);text-decoration:none;font-weight:700;font-size:.9rem}
.go small{flex:0 0 auto;font-weight:500;font-size:.72rem;color:#8a93a6}
.next{display:flex;align-items:center;justify-content:space-between;gap:10px;margin:18px 0 2px;padding:14px 16px;border-radius:16px;background:linear-gradient(135deg,#E94560,#ff6b85);color:#fff;text-decoration:none;font-weight:700;font-size:.98rem}.next i{font-style:normal;font-size:1.3rem}
.two{display:grid;gap:8px;margin:6px 0 2px}.two>div{background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.12);border-radius:14px;padding:12px 13px}
.two b{display:block;font-size:.95rem}.two span{display:block;font-size:.82rem;color:#bfc6d6;line-height:1.45;margin-top:3px}.two .go{margin-top:10px}
.note{font-size:.78rem;color:var(--muted);line-height:1.5;margin:14px 2px 0}
</style>
</head>
<body>
<header class="top">
  <a href="/japan?src=budget">‹ Japan</a>
  <h1>Japan trip <span>budget calculator</span></h1>
  <p>Enter your trip. We add up the costs we have official prices for, and show what is left to price.</p>
  <span class="sketch">Sketch for review · not live</span>
</header>
<main>
  <section class="card"><h2>Who is going?</h2><p class="h">On trains and buses, ages 12 and up pay adult fares and ages 6 to 11 child fares; under 6 usually ride free with an adult.</p>
    <div class="row"><label>Adults<small>18 and older</small></label><div class="step" data-k="ad"><button type="button" data-d="-1" aria-label="Fewer">−</button><output>2</output><button type="button" data-d="1" aria-label="More">+</button></div></div>
    <div class="row"><label>Teenagers<small>12 to 17</small></label><div class="step" data-k="tn"><button type="button" data-d="-1" aria-label="Fewer">−</button><output>0</output><button type="button" data-d="1" aria-label="More">+</button></div></div>
    <div class="row"><label>Children<small>6 to 11</small></label><div class="step" data-k="ch"><button type="button" data-d="-1" aria-label="Fewer">−</button><output>2</output><button type="button" data-d="1" aria-label="More">+</button></div></div>
    <div class="row"><label>Little ones<small>under 6</small></label><div class="step" data-k="in"><button type="button" data-d="-1" aria-label="Fewer">−</button><output>0</output><button type="button" data-d="1" aria-label="More">+</button></div></div>
  </section>
  <section class="card"><h2>Where and how long?</h2><p class="h">Nights in each area.</p>
    <div class="row"><label>Tokyo</label><div class="step" data-k="nt"><button type="button" data-d="-1" aria-label="Fewer">−</button><output>9</output><button type="button" data-d="1" aria-label="More">+</button></div></div>
    <div class="row"><label>Kyoto and Osaka</label><div class="step" data-k="nk"><button type="button" data-d="-1" aria-label="Fewer">−</button><output>0</output><button type="button" data-d="1" aria-label="More">+</button></div></div>
    <div class="row"><label>Hokkaido<small>Sapporo</small></label><div class="step" data-k="nh"><button type="button" data-d="-1" aria-label="Fewer">−</button><output>0</output><button type="button" data-d="1" aria-label="More">+</button></div></div>
    <div class="row"><label for="arr">Fly into</label><select id="arr"></select></div>
    <div class="row stack"><label for="way">Into town by</label><select id="way"></select></div>
    <div class="row"><label for="dep">Fly home from</label><select id="dep"></select></div>
    <div class="row"><label>Taxi rides<small>in town, about 7 km each</small></label><div class="step" data-k="tx"><button type="button" data-d="-1" aria-label="Fewer">−</button><output>6</output><button type="button" data-d="1" aria-label="More">+</button></div></div>
    <div class="row"><label>Tokyo Disney days<small>Disneyland or DisneySea, 1 park a day</small></label><div class="step" data-k="dn"><button type="button" data-d="-1" aria-label="Fewer">−</button><output>0</output><button type="button" data-d="1" aria-label="More">+</button></div></div>
    <div class="row"><label for="sanrio">Sanrio Puroland</label><select id="sanrio"><option value="0">No</option><option value="1">Yes</option></select></div>
    <div class="row"><label for="zoo">Ueno Zoo</label><select id="zoo"><option value="0">No</option><option value="1">Yes</option></select></div>
    <div class="row"><label for="jr">Japan Rail Pass<small>7 days, for long train trips</small></label><select id="jr"><option value="0">No</option><option value="1">Yes</option></select></div>
  </section>
  <section class="card"><h2>Your own numbers <span style="font-weight:500;font-size:.8rem;color:var(--muted)">(optional, in yen)</span></h2><p class="h">We can't price these for you. Add them if you know them.</p>
    <div class="row"><label for="hotel">Hotel per night<small>for the whole group</small></label><input type="number" id="hotel" inputmode="numeric" min="0" step="1000" placeholder="e.g. 25000"></div>
    <div class="row"><label for="food">Food per person per day</label><input type="number" id="food" inputmode="numeric" min="0" step="500" placeholder="e.g. 5000"></div>
    <div class="row"><label for="fly">Flights, total</label><input type="number" id="fly" inputmode="numeric" min="0" step="1000" placeholder="after comparing"></div>
  </section>
  <section class="card res" id="res" aria-live="polite"></section>
  <p class="note">Prices are from the operators' and JNTO's official pages, checked %%CHECKED%%, and are rounded: they change, so check the linked page before you buy. Amounts are in Japanese yen. Partner links are marked; we may earn a commission at no cost to you.</p>
</main>
<script>
(function(){
var D=%%DATA%%,LK=%%LINKS%%,CH='%%CHECKED%%';
var S={ad:2,tn:0,ch:2,in:0,nt:9,nk:0,nh:0,tx:6,dn:0};var MAX={ad:12,tn:10,ch:10,in:6,nt:30,nk:30,nh:30,tx:40,dn:10};
function y(n){return '¥'+Math.round(n).toLocaleString('en-US');}
function esc(t){return String(t).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
function track(s,x){try{if(window.gtag)gtag('event','budget_calc',{event_category:'engagement',status:s,item:x||'',page_path:location.pathname});}catch(e){}}
var arr=document.getElementById('arr'),dep=document.getElementById('dep'),way=document.getElementById('way');
Object.keys(D.airport).forEach(function(k){arr.add(new Option(D.airport[k].name,k));dep.add(new Option(D.airport[k].name,k));});
function ways(){var a=D.airport[arr.value];way.innerHTML='';a.ways.forEach(function(w){way.add(new Option(w.name,w.id));});}
// a link from Packy can fill the form: ?ad=2&ch=2&nt=9
try{var q=new URLSearchParams(location.search);/* also dn= Disney days */Object.keys(S).forEach(function(k){var v=parseInt(q.get(k),10);if(!isNaN(v))S[k]=Math.max(0,Math.min(MAX[k],v));});}catch(e){}
[].forEach.call(document.querySelectorAll('.step'),function(st){var k=st.getAttribute('data-k');st.querySelector('output').textContent=S[k];
 st.addEventListener('click',function(e){var b=e.target.closest('[data-d]');if(!b)return;S[k]=Math.max(k==='ad'?1:0,Math.min(MAX[k],S[k]+(+b.getAttribute('data-d'))));st.querySelector('output').textContent=S[k];calc();});});
// the likely airport for the trip: Kansai for a Kyoto and Osaka trip, New Chitose for Hokkaido only
var ap=S.nt?'narita':(S.nk?'kansai':(S.nh?'chitose':'narita'));arr.value=ap;dep.value=ap;ways();
arr.addEventListener('change',function(){ways();if(dep.value!==arr.value&&!dep.dataset.set)dep.value=arr.value;calc();});
dep.addEventListener('change',function(){dep.dataset.set='1';calc();});
[way,document.getElementById('jr'),document.getElementById('zoo'),document.getElementById('sanrio')].forEach(function(x){x.addEventListener('change',calc);});
['hotel','food','fly'].forEach(function(id){document.getElementById(id).addEventListener('input',calc);});
function num(id){var v=parseFloat(document.getElementById(id).value);return isNaN(v)||v<0?0:v;}
function src(name,url){return '<small>'+esc(name)+', checked '+CH+' · <a href="'+url+'" target="_blank" rel="noopener">official price</a></small>';}
function line(label,v,note){return '<div class="ln"><div class="l">'+label+(note||'')+'</div><div class="v">'+v+'</div></div>';}
function go(k){var l=LK[k];return '<a class="go" href="'+esc(l[1])+'"'+(l[2]?' target="_blank" rel="nofollow noopener sponsored" data-ps-placement="budget-'+k+'"':'')+' data-go="'+k+'">'+esc(l[0])+'<small>'+(l[2]?'partner link ↗':'→')+'</small></a>';}
function calc(){
 var tn=S.tn,ad=S.ad+tn,ch=S.ch,inf=S.in,ppl=ad+ch+inf,nights=S.nt+S.nk+S.nh,days=nights+1,cars=Math.ceil(ppl/4),h='',sum=0,lo=0,hi=0,miss=[];
 // airport to town, both ends
 function leg(k,wid,label){var w=D.airport[k].ways.filter(function(x){return x.id===wid;})[0]||D.airport[k].ways[0];
  if(w.car){lo+=w.car[0]*cars;hi+=w.car[1]*cars;return line(label+': '+esc(w.name)+(cars>1?' ('+cars+' cars)':''),y(w.car[0]*cars)+'–'+y(w.car[1]*cars),src(w.src,w.url));}
  if(w.c===null&&ch){var v=w.a*ad;sum+=v;miss.push('Children\'s fare on '+w.name);return line(label+': '+esc(w.name),y(v)+' <small style="color:#9aa5b5">+ children</small>',src(w.src,w.url));}
  var v=w.a*ad+(w.c||0)*ch;sum+=v;return line(label+': '+esc(w.name),y(v),src(w.src,w.url));}
 h+='<div class="grp">Checked prices</div>';
 h+=leg(arr.value,way.value,'Airport to town');
 var depWay=dep.value===arr.value?way.value:D.airport[dep.value].ways[0].id;
 if(!(dep.value==='narita'&&depWay==='nex'&&arr.value==='narita'))h+=leg(dep.value,depWay,'Town to airport');
 else h+=line('Town to airport: Narita Express','included',' <small>the round-trip ticket covers both rides</small>');
 if(S.nt){var t=D.tokyoTicket,n=Math.ceil((S.nt+1)/t.days),v=n*(t.a*ad+t.c*ch);sum+=v;h+=line('Tokyo subway: '+n+' × 72-hour ticket'+(n>1?'s':''),y(v),src(t.src,t.url));}
 if(S.nh){var s=D.sapporoDay,v=S.nh*(s.a*ad+s.c*ch);sum+=v;h+=line('Sapporo subway: '+S.nh+' one-day ticket'+(S.nh>1?'s':''),y(v),src(s.src,s.url));}
 if(S.tx){var tl=S.tx*cars*D.taxi.lo,th=S.tx*cars*D.taxi.hi;lo+=tl;hi+=th;h+=line('Taxis: '+S.tx+' ride'+(S.tx>1?'s':'')+(cars>1?' × '+cars+' cars':''),y(tl)+'–'+y(th),src(D.taxi.src,D.taxi.url));}
 if(document.getElementById('jr').value==='1'){var j=D.jrpass,v=j.a*ad+j.c*ch;sum+=v;h+=line('Japan Rail Pass, 7 days',y(v),src(j.src,j.url));}
 if(S.dn){var d=D.disney,dc=D.disneyChild,ga=S.ad,kid=(dc.c*ch+dc.j*tn)*S.dn,dl=d.lo*ga*S.dn+kid,dh=d.hi*ga*S.dn+kid;lo+=dl;hi+=dh;
  var who=[ga+' adult'+(ga>1?'s':''),tn?tn+' teen'+(tn>1?'s':''):'',ch?ch+' child'+(ch>1?'ren':''):''].filter(Boolean).join(' + ');
  h+=line('Tokyo Disney: '+who+' × '+S.dn+' day'+(S.dn>1?'s':''),y(dl)+'–'+y(dh),'<small>Adults: '+esc(d.src)+', checked '+d.checked+' · <a href="'+d.url+'" target="_blank" rel="noopener">price calendar</a>'+(tn||ch?'. '+esc(dc.src).charAt(0).toUpperCase()+esc(dc.src).slice(1)+'.':'')+(inf?' Under 4: free; ages 4 and 5 pay the child price.':'')+'</small>');}
 if(document.getElementById('sanrio').value==='1'){var r=D.sanrio,sn=ad+ch,sl=r.lo*sn,sh=r.hi*sn;lo+=sl;hi+=sh;
  h+=line('Sanrio Puroland: '+sn+' × '+y(r.lo)+'–'+y(r.hi),y(sl)+'–'+y(sh),'<small>'+esc(r.src)+', checked '+r.checked+(inf?'. Little ones aged 3 to 5 also need a ticket.':'')+'</small>');}
 if(document.getElementById('zoo').value==='1'){var z=D.uenozoo,v=z.a*ad;sum+=v;h+=line('Ueno Zoo: '+ad+' × '+y(z.a)+(ch||inf?' (children up to 6th grade free)':''),y(v),'<small>'+esc(z.src)+', checked '+z.checked+' · <a href="'+z.url+'" target="_blank" rel="noopener">official page</a></small>');}
 // Shinkansen between Tokyo and Kyoto: one ride if the trip flies into one and out of the other, else there and back
 var REG={narita:'t',haneda:'t',kansai:'k',chitose:'h'},jrp=document.getElementById('jr').value==='1';
 if(S.nt&&S.nk&&!jrp){var sk=D.shinkansen,rides=REG[arr.value]!==REG[dep.value]?1:2,bl=((sk.a-200)*ad+(sk.c-100)*ch)*rides,bh=((sk.a+400)*ad+(sk.c+200)*ch)*rides;lo+=bl;hi+=bh;
  h+=line('Shinkansen Tokyo ⇄ Kyoto: '+rides+' ride'+(rides>1?'s':'')+' each',y(bl)+'–'+y(bh),'<small>'+esc(sk.src)+', checked '+sk.checked+(inf?'; under 6 free on a lap':'')+' · <a href="'+sk.url+'" target="_blank" rel="noopener">official site</a></small>')+go('shinkansen');}
 if(S.nt&&S.nk&&jrp)h+=line('Shinkansen Tokyo ⇄ Kyoto','with the pass','<small>The Japan Rail Pass covers Hikari and Kodama trains; Nozomi needs an extra ticket (4,960 yen per ride between Tokyo and Kyoto, japanrailpass.net, checked 24 Nov 2026).</small>');
 var tx=D.tax.each*ppl;sum+=tx;h+=line('Departure tax: '+ppl+' × '+y(D.tax.each),y(tx),'<small>JNTO, checked '+CH+'; check JNTO for who is exempt · <a href="'+D.tax.url+'" target="_blank" rel="noopener">official page</a></small>');
 // the reader's own numbers
 var hot=num('hotel'),food=num('food'),fly=num('fly'),own='';
 if(hot){own+=line('Hotel: '+nights+' nights × '+y(hot),y(hot*nights));sum+=hot*nights;}
 if(food){own+=line('Food: '+(ad+ch+inf)+' people × '+days+' days × '+y(food),y(food*ppl*days));sum+=food*ppl*days;}
 if(fly){own+=line('Flights',y(fly));sum+=fly;}
 if(own)h+='<div class="grp">Your numbers</div>'+own;
 // what is not priced
 var np='';
 if(!fly)np+=line('Flights','<span class="np">not priced</span>')+go('flights');
 if(!hot)np+=line('Hotels','<span class="np">not priced</span>');
 if(!food)np+=line('Food and drinks','<span class="np">not priced</span>');
 np+=line(S.dn||document.getElementById('sanrio').value==='1'?'Other theme parks and tickets':'Theme parks and tickets','<span class="np">not priced yet</span>')+go('parks');
 if(S.nk)np+=line('Kyoto and Osaka buses and trains','<span class="np">not priced yet</span>');
 if(S.nh&&(S.nt||S.nk))np+=line('Getting to Hokkaido (usually a domestic flight)','<span class="np">not priced</span>');
 miss.forEach(function(m){np+=line(esc(m),'<span class="np">not priced yet</span>');});
 h+='<div class="grp">Still to price</div>'+np;
 // two ways to book (owner, 27 Nov): piece by piece with the buttons above, or one booking with a tour company
 h+='<div class="grp">Two ways to book</div><div class="two"><div><b>Book it yourself</b><span>Use the buttons above for each piece: trains, tickets, transfers.</span></div>'+
  '<div><b>Prefer one booking?</b><span>A guided multi-day tour: hotels, trains and a guide arranged by the tour company. Flights are usually separate.</span>'+go(ch||inf?'tours_family':'tours')+'</div></div>';
 h+='<div class="grp">Also worth having</div>'+go('esim')+go('transfer')+go('insurance');
 var top='<h2>Your estimate</h2><div class="tot"><b>'+y(sum+lo)+(hi>lo?'–'+y(sum+hi).replace('¥',''):'')+'</b><span>'+ppl+' people · '+nights+' nights</span></div>'+
  '<p class="pp">For the costs listed below only. About '+y((sum+lo)/Math.max(1,ppl))+' per person.</p>';
 h+='<a class="next" href="/?dest=Japan&adults='+ad+'&kids='+(ch+inf)+'&src=budget_plan#plan" data-go="plan"><span>Next: turn this into a day-by-day plan</span><i aria-hidden="true">→</i></a>';
 document.getElementById('res').innerHTML=top+h;
}
document.getElementById('res').addEventListener('click',function(e){var a=e.target.closest('[data-go]');if(a)track('link',a.getAttribute('data-go'));});
var tt=null;document.addEventListener('click',function(e){if(e.target.closest('.step,select')){clearTimeout(tt);tt=setTimeout(function(){track('change');},1500);}});
calc();track('open');
})();
</script>
</body>
</html>
"""
html = (PAGE.replace("%%DATA%%", json.dumps(DATA, ensure_ascii=False))
        .replace("%%LINKS%%", json.dumps(LINKS, ensure_ascii=False)).replace("%%CHECKED%%", CHECKED))
assert "%%" not in html
open(os.path.join(PUB, "japan-budget.html"), "w", encoding="utf-8").write(html)
print("w86 done. public/japan-budget.html written (sketch).")
