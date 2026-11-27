#!/usr/bin/env python3
"""
w81: Fuku's Phrasebook (27 Nov 2026), the one interactive home for Fuku's Japanese: /japan-phrasebook.

One self-contained page like a Pocket Guide: the 8 starter words (api/_japan_words.js) and every emailed lesson
(api/_japan_lessons.js), each phrase with its Japanese and a 🔊 button that plays it with the device's own Japanese
voice; per lesson "Send to my WhatsApp" (the reader sends it to themselves or their trip group; we collect no numbers)
and one partner offer that fits the lesson; Packy (added by w75) for any Japan question. Works offline once opened
(service worker japan-phrasebook-sw.js, network first), and can be added to the Home Screen.

Links into it: ?l=<lesson>&p=<phrase> (or ?say=<lesson>-<phrase>) opens that lesson on that phrase; l=0 is the starter
words. src= codes as everywhere (gift<n>_say from the emails, wa_self from WhatsApp, hub_card from the hub).

Writes public/japan-phrasebook.html, public/japan-phrasebook-sw.js and public/japan-phrasebook.webmanifest.
Run after w73 and before w75 (Packy) and w72:  python3 tools/w81_fuku_phrasebook.py
Rebuilds the files from scratch every time, so it is idempotent. Bump SWV when the page's shell changes.
"""
import html, json, os, re, sys

ROOT = os.getcwd()
PUB = os.path.join(ROOT, "public")
SWV = "japan-phrasebook-v4"
PAGE = "/japan-phrasebook"

def die(m):
    sys.exit("w81 aborted, nothing written: " + m)

def js_obj(path, name, opener):
    src = open(os.path.join(ROOT, "api", path), encoding="utf-8").read()
    m = re.search(r"export const " + name + r" = (\%s.*?\%s);\s*$" % (opener, "]" if opener == "[" else "}"), src, re.S | re.M)
    if not m:
        die("api/%s: %s not found" % (path, name))
    return json.loads(m.group(1))

WORDS = js_obj("_japan_words.js", "WORDS", "[")
LESSONS = js_obj("_japan_lessons.js", "LESSONS", "{")
if any(len(w) != 4 for w in WORDS):
    die("each starter word needs [emoji, meaning, Japanese, romaji]")
for k, l in LESSONS.items():
    if not l.get("title") or any(len(p) != 3 for p in l.get("phrases", [])):
        die("lesson %s needs a title and phrases of [romaji, Japanese, meaning]" % k)

# One offer per lesson, fitting what the lesson is about (owner, 27 Nov: the emails and the phrasebook must also sell).
# Our own words never name a partner (D47; SafetyWing is the exception); partner links say "partner link".
GYG = "https://www.getyourguide.com/s/?q=%s&partner_id=D7IXONS&cmp=ps-phrasebook-%s"
OFFERS = {   # soft start (owner, 27 Nov): lessons 1 to 3 point to our own help; partner offers from lesson 4, each matching its lesson
    "1": ("📱", "Exits, platforms, lockers and ATMs, offline: the station Pocket Guides", "/japan?src=phrasebook#pocket-hub", False),
    "2": ("🗺️", "A 7-day Japan itinerary with costs", "/blog/japan-7-day-itinerary-budget?src=phrasebook", False),
    "3": ("📅", "Plan My Trip: a day-by-day plan for your dates", "/?dest=Japan&src=phrasebook#plan", False),
    "4": ("🌸", "Compare cherry blossom tours in Japan", GYG % ("japan%20cherry%20blossom%20tour", "4"), True),
    "5": ("🚄", "Book Shinkansen tickets online", "https://www.japan-bullettrain.com/?via=packsmart", True),
    "6": ("📶", "See eSIM data plans for Japan", "https://airalo.tpo.lu/Y1kIv39w", True),   # Sub ID pb-l6-esim
    "7": ("🧳", "Open the Japan packing list", "/blog/japan-travel-packing-guide?src=phrasebook", False),
    "8": ("🩺", "Get a SafetyWing travel medical insurance quote", "https://www.safetywing.com/nomad-insurance?referenceID=26492686&utm_source=26492686&utm_medium=Ambassador", True),
}
for k in LESSONS:
    if k not in OFFERS:
        die("lesson %s has no offer in OFFERS" % k)

# lesson 0 = the starter words, in the same shape as the lessons
DATA = {"0": {"title": "Your first words", "phrases": [[w[3], w[2], w[1]] for w in WORDS]}}
DATA.update(LESSONS)
for k, o in OFFERS.items():
    if k in DATA:
        DATA[k]["offer"] = {"i": o[0], "t": o[1], "u": o[2], "p": o[3]}
DJSON = json.dumps(DATA, ensure_ascii=False).replace("</", "<\\/")
e = html.escape


PAGE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Fuku’s Japanese Phrasebook | PackSmart</title>
<meta name="description" content="Japanese for your trip: starter words and Fuku's lessons for stations, food, the konbini, trains and getting help. Tap to hear each phrase. No app, works offline.">
<meta name="robots" content="noindex,follow">
<link rel="canonical" href="https://www.packsmartapp.com/japan-phrasebook">
<meta name="theme-color" content="#0f0f23">
<link rel="manifest" href="/japan-phrasebook.webmanifest">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="apple-touch-icon" href="/images/phrasebook-fuku-apple-touch-180.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Phrasebook">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">
<script async src="https://www.googletagmanager.com/gtag/js?id=G-0C4Z7VVGPE"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag("js",new Date());gtag("config","G-0C4Z7VVGPE");</script>
<style>
:root{--primary:#00C9A7;--accent:#E94560;--dark:#0f0f23;--ink:#2b3242;--muted:#5a6378;--line:#d9f0ea}
*{box-sizing:border-box}
body{margin:0;font-family:'DM Sans',sans-serif;background:#f4faf8;color:var(--ink);-webkit-text-size-adjust:100%}
a{color:#0a8f78}
.top{background:linear-gradient(135deg,#0f0f23,#1a1a3e);color:#fff;padding:14px 16px 16px;padding-top:calc(14px + env(safe-area-inset-top))}
.top .bk{color:#bfeee4;text-decoration:none;font-size:.85rem;font-weight:700}
.top h1{margin:10px 0 2px;font-size:1.45rem;line-height:1.2}
.top h1 span{color:var(--primary)}
.top h1 .fk{display:inline-block;vertical-align:-6px;margin-right:8px;border-radius:9px}
.top p{margin:0;color:#cfd6e6;font-size:.9rem}
.st{display:inline-block;margin-top:9px;font-size:.78rem;font-weight:700;background:rgba(255,255,255,.1);border-radius:999px;padding:4px 10px;color:#bfeee4}
.chips{position:sticky;top:0;z-index:5;display:flex;gap:7px;overflow-x:auto;padding:10px 16px;background:#f4faf8;border-bottom:1px solid var(--line);scrollbar-width:none}
.chips::-webkit-scrollbar{display:none}
.ch{flex:0 0 auto;white-space:nowrap;text-decoration:none;font-size:.82rem;font-weight:700;color:var(--dark);background:#fff;border:1.5px solid var(--line);border-radius:999px;padding:6px 12px}
.ch.on{background:var(--dark);color:#fff;border-color:var(--dark)}
main{max-width:640px;margin:0 auto;padding:6px 16px 120px}
.inst{margin:14px 0 0;background:#fff;border:1.5px solid #bfe8dc;border-radius:16px;padding:13px 14px;font-size:.88rem;line-height:1.45;box-shadow:0 2px 10px rgba(15,15,35,.05)}
.inst h2{margin:0 0 6px;font-size:1rem;color:var(--dark)}
.inst .l1{margin:0 0 4px;color:#555}.inst ol{margin-top:6px!important}
.inst ol{margin:0;padding:0 0 0 20px}.inst li{display:list-item;background:none;border:0;padding:0;margin:0 0 5px;border-radius:0}
.inst li b{display:inline;font-size:inherit}
.inst .r{display:flex;flex-wrap:wrap;gap:8px;margin-top:8px}
.inst button{border:0;border-radius:999px;font:inherit;font-weight:700;font-size:.86rem;padding:8px 14px;cursor:pointer;background:var(--primary);color:#fff}
.inst button.gh{background:#eef3f6;color:var(--dark)}
.pg{display:inline-block;margin:9px 0 0 6px;font-size:.78rem;font-weight:700;background:rgba(233,69,96,.22);border-radius:999px;padding:4px 10px;color:#ffd6de}
.ch.lk{color:#8a93a6;background:#f0f3f5}
section.lock h2{color:#5a6378}
.lkx{margin:8px 0 0;background:#fff;border:1.5px dashed #d6dde3;border-radius:14px;padding:12px 14px;font-size:.88rem;color:#5a6378}
.nx{margin:22px 0 0;background:#FFF5F7;border:1px solid #F7D3DC;border-radius:16px;padding:14px;font-size:.9rem;line-height:1.5}
.nx b{color:var(--dark)}
.nx button{margin-top:8px;border:0;background:none;padding:0;font:inherit;font-weight:700;font-size:.86rem;color:#0a8f78;text-decoration:underline;cursor:pointer}
section{scroll-margin-top:62px;margin:22px 0 0}
#lessons{display:flex;align-items:flex-start;overflow-x:auto;overflow-y:hidden;scroll-snap-type:x mandatory;overscroll-behavior-x:contain;scrollbar-width:none;margin:0 -16px;transition:height .25s ease}
#lessons::-webkit-scrollbar{display:none}
#lessons>section{flex:0 0 100%;min-width:0;scroll-snap-align:start;scroll-snap-stop:always;margin:0;padding:16px 16px 4px}
.pager{display:flex;align-items:center;justify-content:space-between;gap:10px;margin:14px 0 0}
.nxt{display:flex;align-items:center;justify-content:space-between;gap:8px;width:100%;margin:14px 0 0;border:0;border-radius:14px;background:var(--dark);color:#fff;font:inherit;font-weight:700;font-size:.9rem;padding:13px 16px;text-align:left;cursor:pointer}
.nxt span{font-size:1.4rem;line-height:1;color:var(--primary)}
.pager>button{flex:0 0 42px;height:42px;border-radius:50%;border:1.5px solid var(--line);background:#fff;color:var(--dark);font:inherit;font-size:1.6rem;line-height:1;font-weight:500;cursor:pointer;box-shadow:0 2px 8px rgba(15,15,35,.06)}
.pager>button:disabled{opacity:.3;cursor:default}
.pager .mid{flex:1;text-align:center;min-width:0}
#cnt{display:block;font-size:.8rem;font-weight:700;color:var(--muted);margin-bottom:6px}
#dots{display:flex;justify-content:center;gap:4px;flex-wrap:wrap}
#dots button{width:8px;height:8px;padding:0;border:0;border-radius:4px;background:#bfe3d9;cursor:pointer;transition:width .2s}
#dots button.lk{background:#e2e7eb}
#dots button.on{width:22px;background:var(--accent)}
@media (prefers-reduced-motion:reduce){#lessons{scroll-behavior:auto;transition:none}}
section h2{margin:0 0 3px;font-size:1.12rem;color:var(--dark)}
section h2 small{display:block;font-size:.72rem;letter-spacing:1px;text-transform:uppercase;color:var(--accent);font-weight:700;margin-bottom:2px}
#lessons ul{list-style:none;margin:10px 0 0;padding:0;display:grid;gap:7px}
#lessons li{display:grid;grid-template-columns:minmax(0,1fr) 44px;align-items:center;gap:8px;background:#fff;border:1px solid var(--line);border-radius:14px;padding:9px 8px 9px 13px}
#lessons li b{display:block;font-size:1rem;color:var(--dark)}
#lessons li .ja{display:block;font-weight:700;color:#0a8f78;font-size:.92rem;margin-top:1px}
#lessons li small{display:block;font-size:.8rem;color:var(--muted);margin-top:1px}
#lessons li button{width:42px;height:42px;border:0;border-radius:50%;background:var(--primary);color:#fff;font-size:1.05rem;cursor:pointer}
#lessons li button:active{transform:scale(.94)}
#lessons li.hot{background:#FFF1F4;border-color:#F7B9C6;box-shadow:0 0 0 2px var(--accent) inset}
#lessons li.hot button{background:var(--accent);animation:ping 1.6s ease-in-out 3}
@keyframes ping{50%{box-shadow:0 0 0 8px rgba(233,69,96,.18)}}
.act{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0 0}
.wa{display:inline-flex;align-items:center;gap:6px;border:0;border-radius:999px;background:#25D366;color:#fff;font:inherit;font-weight:700;font-size:.86rem;padding:8px 14px;cursor:pointer;text-decoration:none}
.off{display:flex;align-items:center;gap:8px;margin:10px 0 0;padding:9px 12px;border-radius:12px;background:#fff;border:1px solid #e3e8ec;text-decoration:none;color:var(--dark);font-size:.86rem;font-weight:700;line-height:1.35}
.off i{font-style:normal}
.off small{margin-left:auto;flex:0 0 auto;font-size:.7rem;font-weight:500;color:#8a93a6}
.end{margin:30px 0 0;background:linear-gradient(135deg,#e6faf5,#e8f4fc);border:1.5px solid #bfede3;border-radius:16px;padding:16px}
.end h2{margin:0 0 6px;font-size:1.05rem;color:var(--dark)}
.end p{margin:0 0 10px;font-size:.9rem;line-height:1.5}
.btn{display:inline-block;border:0;border-radius:999px;background:var(--accent);color:#fff;font:inherit;font-weight:700;font-size:.92rem;padding:10px 16px;cursor:pointer;text-decoration:none;margin:0 6px 8px 0}
.btn.alt{background:var(--dark)}
.note{font-size:.76rem;color:#8a93a6;margin:16px 0 0;line-height:1.5}
@media (prefers-reduced-motion:reduce){#lessons li.hot button{animation:none}}
</style>
</head>
<body>
<header class="top">
  <a class="bk" href="/japan?src=phrasebook">← Japan hub</a>
  <h1><img src="/images/phrasebook-fuku-icon-192.png" width="34" height="34" alt="" class="fk">Fuku’s <span>Japanese</span> Phrasebook</h1>
  <p>Tap 🔊 to hear each phrase, then say it back. Slowly is fine!</p>
  <span class="st" id="st">No app · works offline once saved</span><span class="pg" id="pg" hidden></span>
</header>
<nav class="chips" id="chips" aria-label="Lessons"></nav>
<main>
  <div class="inst" id="inst" hidden></div>
  <div class="pager"><button type="button" id="prev" aria-label="Previous lesson">‹</button><div class="mid"><span id="cnt"></span><div id="dots"></div></div><button type="button" id="next" aria-label="Next lesson">›</button></div>
  <div id="lessons" aria-roledescription="carousel" aria-label="Fuku’s lessons"></div>
  <div class="end">
    <h2>💬 Any other Japan question?</h2>
    <p>Ask Packy, PackSmart’s Japan travel buddy: trains, airports, money, luggage and more, from official sources.</p>
    <button type="button" class="btn" id="askPacky">Ask Packy</button>
    <a class="btn alt" href="/japan?src=phrasebook#words">📩 Get Fuku’s lessons by email</a>
    <p class="note">The voice is your phone’s or computer’s own, so it can sound a little robotic. Phrases are in polite, everyday Japanese.</p>
  </div>
</main>
<script>
(function(){
var D=%%DATA%%,SITE='https://www.packsmartapp.com';
function track(s,x){try{if(window.gtag)gtag('event','phrasebook',{event_category:'engagement',status:s,item:x||'',page_path:location.pathname});}catch(e){}}
function esc(t){return String(t).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
// the device's own voice, Japanese when it has one (same as the hub's word card)
var jaVoice=null,enVoice=null;
function best(v){return v.filter(function(x){return x.localService;})[0]||v[0]||null;}
function pickVoice(){try{var v=speechSynthesis.getVoices();jaVoice=best(v.filter(function(x){return /^ja(-|_|$)/i.test(x.lang);}));enVoice=best(v.filter(function(x){return /^en(-|_|$)/i.test(x.lang);}));}catch(e){}}
if('speechSynthesis' in window){pickVoice();try{speechSynthesis.addEventListener('voiceschanged',pickVoice);}catch(e){}}
function say(ja,ro){try{if(!('speechSynthesis' in window))return;if(speechSynthesis.speaking||speechSynthesis.pending)speechSynthesis.cancel();
 try{speechSynthesis.resume();}catch(e){}if(!jaVoice&&!enVoice)pickVoice();var vo=jaVoice||enVoice,u=new SpeechSynthesisUtterance(jaVoice||!vo?ja:ro);
 if(vo){u.voice=vo;u.lang=vo.lang;}else u.lang='ja-JP';u.rate=.9;speechSynthesis.speak(u);}catch(e){}}
function waText(k){var L=D[k],a=L.phrases.slice(0,3).map(function(p){return '*'+p[0].replace(/[.。]$/,'')+'* · '+p[2];}).join('\\n');
 return '🇯🇵 *Fuku’s Japanese, '+(k==='0'?'first words':'lesson '+k+': '+L.title)+'*\\n\\n'+a+'\\n\\n🔊 Hear them all, works offline:\\n'+SITE+'/japan-phrasebook?l='+k+'&src=wa_self';}
// The course (owner, 27 Nov): one new lesson a day on this phone, separate from the emails. Day 1 is the first time
// this phone opens the Phrasebook (on iPhone the home-screen icon keeps its own memory, so its day 1 is the day it is
// added). A lesson opened from a link (an email's Hear button, a friend's WhatsApp) is always open. "Unlock all" is
// for people already travelling.
function ls(k,v){try{if(v===undefined)return localStorage.getItem(k);localStorage.setItem(k,v);}catch(e){}return null;}
function ymd(d){return d.getFullYear()+'-'+('0'+(d.getMonth()+1)).slice(-2)+'-'+('0'+d.getDate()).slice(-2);}
var TODAY=ymd(new Date()),START=ls('fukuStart');if(!/^[0-9]{4}-[0-9]{2}-[0-9]{2}$/.test(START||'')){START=TODAY;ls('fukuStart',START);}
var DAY=Math.max(1,Math.round((new Date(TODAY+'T00:00:00')-new Date(START+'T00:00:00'))/864e5)+1);
var ALL=ls('fukuAll')==='1',OPEN={};try{OPEN=JSON.parse(ls('fukuOpen')||'{}')||{};}catch(e){OPEN={};}
var KEYS=Object.keys(D);
// deep links: ?l=1&p=3 or ?say=1-3 (the emails), #l3
var q=new URLSearchParams(location.search),m=/^([0-9])-([1-9])$/.exec(q.get('say')||''),lk=m?m[1]:(q.get('l')||''),pk=m?m[2]:(q.get('p')||'');
if(!D[lk])lk='';var src=(q.get('src')||'').toLowerCase().replace(/[^a-z0-9_-]/g,'').slice(0,40);
if(lk&&!OPEN[lk]){OPEN[lk]=1;ls('fukuOpen',JSON.stringify(OPEN));}
function isOpen(k){return ALL||k==='0'||+k<=DAY||!!OPEN[k];}
function when(k){var d=+k-DAY;return d<=1?'tomorrow':'in '+d+' days';}
var IX=0,rail=null;
function slideHTML(k,firstShut){var L=D[k],o=L.offer;
 if(!isOpen(k))return '<section id="l'+k+'" class="lock" aria-roledescription="slide"><h2><small>Lesson '+k+'</small>'+esc(L.title)+'</h2><div class="lkx">🔒 '+L.phrases.length+' phrases · opens '+when(k)+'</div>'+
  '<div class="nx">'+(k===firstShut?'<b>🗓️ A new lesson every day.</b> Come back from Fuku’s icon on your Home Screen.<br>':'')+'<button type="button" class="unlockAll">Travelling now? Unlock all lessons</button></div></section>';
 return '<section id="l'+k+'" aria-roledescription="slide"><h2><small>'+(k==='0'?'Start here':'Lesson '+k)+'</small>'+esc(L.title)+'</h2><ul>'+
  L.phrases.map(function(p,i){return '<li id="p'+k+'-'+(i+1)+'"><div><b>'+esc(p[0])+'</b><span class="ja" lang="ja">'+esc(p[1])+'</span><small>'+esc(p[2])+'</small></div><button type="button" data-k="'+k+'" data-i="'+i+'" aria-label="Play: '+esc(p[2])+'">🔊</button></li>';}).join('')+
  '</ul><div class="act"><a class="wa" data-wa="'+k+'" href="https://wa.me/?text='+encodeURIComponent(waText(k))+'" target="_blank" rel="noopener">📲 Send to my WhatsApp</a></div>'+
  (o?'<a class="off" data-off="'+k+'" href="'+esc(o.u)+'"'+(o.p?' target="_blank" rel="nofollow noopener sponsored" data-ps-placement="phrasebook-l'+k+'"':'')+'><i aria-hidden="true">'+o.i+'</i><span>'+esc(o.t)+'</span>'+(o.p?'<small>partner link ↗</small>':'<small>→</small>')+'</a>':'')+
  nextBtn(k)+'</section>';}
function nextBtn(k){var i=KEYS.indexOf(k)+1;if(i>=KEYS.length)return '';var n=KEYS[i];
 return '<button type="button" class="nxt" data-go="'+i+'">Next: Lesson '+n+' · '+esc(D[n].title)+(isOpen(n)?'':' 🔒')+' <span aria-hidden="true">›</span></button>';}
// The lessons are a slider (owner, 27 Nov: "feels like an app"): swipe, the tabs, the arrows or the dots move one
// lesson at a time (CSS scroll snap, so the swipe is the phone's own). The slider takes the height of the lesson shown.
function render(){
 var shut=KEYS.filter(function(k){return !isOpen(k);});
 rail=document.getElementById('lessons');rail.innerHTML=KEYS.map(function(k){return slideHTML(k,shut[0]);}).join('');
 document.getElementById('chips').innerHTML=KEYS.map(function(k){var op=isOpen(k);return '<a class="ch'+(op?'':' lk')+'" href="#l'+k+'" data-l="'+k+'">'+(op?'':'🔒 ')+(k==='0'?'👋 Start':k+' · '+esc(D[k].title))+'</a>';}).join('');
 document.getElementById('dots').innerHTML=KEYS.map(function(k,i){return '<button type="button" data-go="'+i+'" class="'+(isOpen(k)?'':'lk')+'" aria-label="'+(k==='0'?'Start':'Lesson '+k)+'"></button>';}).join('');
 var n=KEYS.filter(isOpen).length,pg=document.getElementById('pg');pg.hidden=false;pg.textContent=n>=KEYS.length?'All '+KEYS.length+' lessons open':'Day '+DAY+' · '+n+' of '+KEYS.length+' lessons open';
 [].forEach.call(document.querySelectorAll('.unlockAll'),function(u){u.addEventListener('click',function(){ALL=true;ls('fukuAll','1');track('unlock_all','day '+DAY);render();go(IX,false);});});
}
function fit(){var s=rail.children[IX];if(s)rail.style.height=s.offsetHeight+'px';}
function show(i){IX=i;var k=KEYS[i];
 [].forEach.call(document.querySelectorAll('.ch'),function(c){var on=c.getAttribute('data-l')===k;c.classList.toggle('on',on);c.setAttribute('aria-current',on?'true':'false');
  if(on){var bar=c.parentNode;try{bar.scrollTo({left:c.offsetLeft-(bar.clientWidth-c.offsetWidth)/2,behavior:'smooth'});}catch(e){bar.scrollLeft=c.offsetLeft;}}});
 [].forEach.call(document.querySelectorAll('#dots button'),function(d,j){d.classList.toggle('on',j===i);});
 document.getElementById('prev').disabled=i===0;document.getElementById('next').disabled=i===KEYS.length-1;
 document.getElementById('cnt').textContent=(k==='0'?'Start':'Lesson '+k)+' · '+(i+1)+' of '+KEYS.length;
 [].forEach.call(rail.children,function(s,j){s.setAttribute('aria-hidden',j===i?'false':'true');});
 fit();ls('fukuAt',k);}
function go(i,smooth){i=Math.max(0,Math.min(KEYS.length-1,i));
 var top=document.querySelector('.pager').getBoundingClientRect().top;if(top<58)window.scrollBy({top:top-62,behavior:smooth?'smooth':'auto'});
 try{rail.scrollTo({left:i*rail.clientWidth,behavior:smooth?'smooth':'auto'});}catch(e){rail.scrollLeft=i*rail.clientWidth;}
 if(!smooth)show(i);}
document.addEventListener('click',function(ev){var t=ev.target;
 var b=t.closest&&t.closest('[data-i]');if(b){var k=b.getAttribute('data-k'),p=D[k].phrases[+b.getAttribute('data-i')];say(p[1],p[0]);track('play',k+':'+p[0]);return;}
 var w=t.closest&&t.closest('[data-wa]');if(w){track('wa_self',w.getAttribute('data-wa'));return;}
 var o=t.closest&&t.closest('[data-off]');if(o){track('offer',o.getAttribute('data-off'));return;}
 var c=t.closest&&t.closest('.ch');if(c){ev.preventDefault();var i=KEYS.indexOf(c.getAttribute('data-l'));go(i,true);track('chip',c.getAttribute('data-l'));return;}
 var d=t.closest&&t.closest('[data-go]');if(d){go(+d.getAttribute('data-go'),true);track(d.classList.contains('nxt')?'next_btn':'dot',KEYS[+d.getAttribute('data-go')]);}});
render();
document.getElementById('prev').addEventListener('click',function(){go(IX-1,true);track('arrow','prev');});
document.getElementById('next').addEventListener('click',function(){go(IX+1,true);track('arrow','next');});
var st=null;rail.addEventListener('scroll',function(){clearTimeout(st);st=setTimeout(function(){var i=Math.round(rail.scrollLeft/rail.clientWidth);if(i!==IX){show(i);track('slide',KEYS[i]);}},90);},{passive:true});
window.addEventListener('resize',function(){rail.scrollLeft=IX*rail.clientWidth;fit();});
document.addEventListener('keydown',function(e){if(/INPUT|TEXTAREA/.test((e.target||{}).tagName||''))return;if(e.key==='ArrowRight')go(IX+1,true);else if(e.key==='ArrowLeft')go(IX-1,true);});
document.getElementById('askPacky').addEventListener('click',function(){track('packy');if(window.Packy)window.Packy.open();else location.href='/japan?src=phrasebook#ask';});
track('open',(lk||'all')+(src?' '+src:'')+' day '+DAY);
// start on: the lesson a link names; else a lesson that opened since the last visit; else where the reader left off
var hk=(/^#l([0-9])$/.exec(location.hash)||[])[1],at=ls('fukuAt'),seen=+(ls('fukuSeen')||-1),newest=KEYS.filter(isOpen).pop();
var sk=lk||(D[hk]?hk:'')||(at!==null&&+newest>seen&&seen>=0?newest:'')||(at&&D[at]&&isOpen(at)?at:'0');
ls('fukuSeen',String(Math.max(seen,+newest)));
go(KEYS.indexOf(sk),false);
if(lk&&pk){var el=document.getElementById('p'+lk+'-'+pk);if(el){el.classList.add('hot');setTimeout(function(){var r=el.getBoundingClientRect();window.scrollBy({top:r.top-innerHeight/2+r.height/2});},80);}}
setTimeout(fit,400);if(document.fonts&&document.fonts.ready)document.fonts.ready.then(fit);
// Keep Fuku on your phone: the Pocket Guides' way (Add to Home Screen, then open from the icon while online).
// Links from WhatsApp often open inside WhatsApp's own browser, which cannot add to the Home Screen, so say how to
// open the page in the phone's browser first. We cannot always tell we are inside WhatsApp, so the step is always shown.
var UA=navigator.userAgent||'',isIOS=/iPad|iPhone|iPod/.test(UA)||(navigator.platform==='MacIntel'&&navigator.maxTouchPoints>1),isAnd=/Android/.test(UA);
var standalone=!!(navigator.standalone||(window.matchMedia&&matchMedia('(display-mode: standalone)').matches)),dp=null,inst=document.getElementById('inst');
function later(){try{return sessionStorage.getItem('fukuLater')==='1';}catch(e){return false;}}
function showInst(){
 if(standalone||later()||!(isIOS||isAnd)){inst.hidden=true;return;}
 var steps=isIOS?'<li>In WhatsApp? Tap <b>Open in Safari</b> first.</li><li>Tap <b>Share</b> ⬆️, then <b>Add to Home Screen</b>.</li>'
               :'<li>In WhatsApp? Tap <b>⋮</b>, <b>Open in Chrome</b> first.</li><li>Tap <b>⋮</b>, then <b>Add to Home screen</b>.</li>';
 var h='<h2>📲 Keep Fuku on your phone</h2><p class="l1">Works with no signal. A new lesson every day.</p>'+
  '<ol id="instHow" hidden>'+steps+'<li>Open Fuku from the new icon once while online.</li></ol><div class="r">'+
  '<button type="button" id="instGo">'+(dp?'Add to Home Screen':'Show me how')+'</button><button type="button" class="gh" id="instLater">Later</button></div>';
 inst.innerHTML=h;inst.hidden=false;
 document.getElementById('instGo').addEventListener('click',function(){
  if(dp){var p=dp;dp=null;try{p.prompt();p.userChoice.then(function(r){track('save_prompt',r&&r.outcome);});}catch(e){}showInst();return;}
  var o=document.getElementById('instHow');o.hidden=false;this.hidden=true;track('save_how');});
 document.getElementById('instLater').addEventListener('click',function(){try{sessionStorage.setItem('fukuLater','1');}catch(e){}inst.hidden=true;track('save_later');});
}
window.addEventListener('beforeinstallprompt',function(e){e.preventDefault();dp=e;showInst();});
showInst();if(!inst.hidden)track('save_view',isIOS?'ios':'android');
// offline: the service worker keeps a copy; say so once it is ready
if('serviceWorker' in navigator){navigator.serviceWorker.register('/japan-phrasebook-sw.js',{scope:'%%PAGE%%',updateViaCache:'none'})
 .then(function(){return navigator.serviceWorker.ready;}).then(function(){return caches.has('%%SWV%%');})
 .then(function(ok){if(ok)document.getElementById('st').textContent='Ready offline ✓';}).catch(function(){});}
})();
</script>
</body>
</html>
"""
PAGE_HTML = (PAGE_HTML.replace("%%DATA%%", DJSON)
             .replace("%%PAGE%%", PAGE).replace("%%SWV%%", SWV))
for tok in ("%%",):
    if tok in PAGE_HTML:
        die("a placeholder was left in the page")

SW = """/* Fuku's Phrasebook service worker (tools/w81_fuku_phrasebook.py). Network first, saved copy when offline. */
var V='%s';
var PAGE='%s';
var SHELL=[PAGE,'/japan-phrasebook.webmanifest','/favicon-32.png','/images/phrasebook-fuku-icon-192.png','/images/phrasebook-fuku-icon-512.png'];
self.addEventListener('install',function(e){
  e.waitUntil(caches.open(V).then(function(c){return c.addAll(SHELL);}).then(function(){return self.skipWaiting();}));
});
self.addEventListener('activate',function(e){
  e.waitUntil(caches.keys().then(function(ks){
    return Promise.all(ks.filter(function(k){return k.indexOf('japan-phrasebook-')===0&&k!==V;}).map(function(k){return caches.delete(k);}));
  }).then(function(){return self.clients.claim();}));
});
function pageFirst(req){
  return new Promise(function(resolve){
    var done=false;
    function fromCache(){ return caches.match(PAGE).then(function(m){ if(m&&!done){done=true;resolve(m);} return m; }); }
    var t=setTimeout(fromCache,3000);
    fetch(req).then(function(res){
      clearTimeout(t);
      var cp=(res&&res.ok)?res.clone():null;
      if(!done){done=true;resolve(res);}
      if(cp){ caches.open(V).then(function(c){c.put(PAGE,cp);}); }
    }).catch(function(){
      clearTimeout(t);
      fromCache().then(function(m){ if(!m&&!done){done=true;resolve(Response.error());} });
    });
  });
}
self.addEventListener('fetch',function(e){
  var r=e.request;
  if(r.method!=='GET') return;
  var u=new URL(r.url);
  if(u.origin!==location.origin) return;
  if(r.mode==='navigate'){
    if(u.pathname!==PAGE) return;
    e.respondWith(pageFirst(r));
    return;
  }
  e.respondWith(caches.match(r).then(function(m){return m||fetch(r);}));
});
""" % (SWV, PAGE)

MANIFEST = json.dumps({
    "name": "Fuku's Japanese Phrasebook", "short_name": "Phrasebook",
    "description": "Japanese for your trip. Tap to hear each phrase. Works offline.",
    "start_url": PAGE + "?src=homescreen", "scope": PAGE, "display": "standalone",
    "background_color": "#0f0f23", "theme_color": "#0f0f23", "lang": "en",
    "icons": [{"src": "/images/phrasebook-fuku-icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
              {"src": "/images/phrasebook-fuku-icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
              {"src": "/images/phrasebook-fuku-icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]},
    indent=2, ensure_ascii=False)

for f in ("images/phrasebook-fuku-icon-192.png", "images/phrasebook-fuku-icon-512.png", "images/phrasebook-fuku-icon-maskable-512.png", "images/phrasebook-fuku-apple-touch-180.png"):
    if not os.path.exists(os.path.join(PUB, f)):
        die("missing icon " + f)
open(os.path.join(PUB, "japan-phrasebook.html"), "w", encoding="utf-8").write(PAGE_HTML)
open(os.path.join(PUB, "japan-phrasebook-sw.js"), "w", encoding="utf-8").write(SW)
open(os.path.join(PUB, "japan-phrasebook.webmanifest"), "w", encoding="utf-8").write(MANIFEST + "\n")
print("w81 done. Phrasebook: %d starter words, %d lessons." % (len(WORDS), len(LESSONS)))
