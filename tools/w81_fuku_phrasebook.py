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
SWV = "japan-phrasebook-v1"
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
OFFERS = {
    "0": ("📱", "80+ more phrases, plus exits, platforms and lockers: the Pocket Guides (no app, works offline)", "/japan?src=phrasebook#pocket-hub", False),
    "1": ("🚐", "Book a private airport transfer", "https://tpx.li/qYFLwgZ8", True),
    "2": ("🎟️", "Compare food tours in Tokyo", GYG % ("tokyo%20food%20tour", "2"), True),
    "3": ("🧳", "Store your bags in Tokyo", "https://radicalstorage.tpx.li/d0Eds67a", True),
    "4": ("🌸", "Compare cherry blossom tours in Japan", GYG % ("japan%20cherry%20blossom%20tour", "4"), True),
    "5": ("🚄", "Book Shinkansen tickets online", "https://www.japan-bullettrain.com/?via=packsmart", True),
    "6": ("📶", "See eSIM data plans for Japan", "https://airalo.tpx.li/4TNBGGOO", True),
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

chips = "".join('<a class="ch" href="#l%s" data-l="%s">%s</a>' % (k, k, ("👋 Start" if k == "0" else k + " · " + e(v["title"]))) for k, v in DATA.items())

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
<link rel="apple-touch-icon" href="/images/phrasebook-apple-touch-180.png">
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
.top p{margin:0;color:#cfd6e6;font-size:.9rem}
.st{display:inline-block;margin-top:9px;font-size:.78rem;font-weight:700;background:rgba(255,255,255,.1);border-radius:999px;padding:4px 10px;color:#bfeee4}
.chips{position:sticky;top:0;z-index:5;display:flex;gap:7px;overflow-x:auto;padding:10px 16px;background:#f4faf8;border-bottom:1px solid var(--line);scrollbar-width:none}
.chips::-webkit-scrollbar{display:none}
.ch{flex:0 0 auto;white-space:nowrap;text-decoration:none;font-size:.82rem;font-weight:700;color:var(--dark);background:#fff;border:1.5px solid var(--line);border-radius:999px;padding:6px 12px}
.ch.on{background:var(--dark);color:#fff;border-color:var(--dark)}
main{max-width:640px;margin:0 auto;padding:6px 16px 120px}
.inst{margin:14px 0 0;background:#fff;border:1.5px dashed #bfe8dc;border-radius:14px;padding:11px 13px;font-size:.86rem;line-height:1.45}
.inst b{color:var(--dark)}
section{scroll-margin-top:62px;margin:22px 0 0}
section h2{margin:0 0 3px;font-size:1.12rem;color:var(--dark)}
section h2 small{display:block;font-size:.72rem;letter-spacing:1px;text-transform:uppercase;color:var(--accent);font-weight:700;margin-bottom:2px}
ul{list-style:none;margin:10px 0 0;padding:0;display:grid;gap:7px}
li{display:grid;grid-template-columns:minmax(0,1fr) 44px;align-items:center;gap:8px;background:#fff;border:1px solid var(--line);border-radius:14px;padding:9px 8px 9px 13px}
li b{display:block;font-size:1rem;color:var(--dark)}
li .ja{display:block;font-weight:700;color:#0a8f78;font-size:.92rem;margin-top:1px}
li small{display:block;font-size:.8rem;color:var(--muted);margin-top:1px}
li button{width:42px;height:42px;border:0;border-radius:50%;background:var(--primary);color:#fff;font-size:1.05rem;cursor:pointer}
li button:active{transform:scale(.94)}
li.hot{background:#FFF1F4;border-color:#F7B9C6;box-shadow:0 0 0 2px var(--accent) inset}
li.hot button{background:var(--accent);animation:ping 1.6s ease-in-out 3}
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
@media (prefers-reduced-motion:reduce){li.hot button{animation:none}}
</style>
</head>
<body>
<header class="top">
  <a class="bk" href="/japan?src=phrasebook">← Japan hub</a>
  <h1>🐱 Fuku’s <span>Japanese</span> Phrasebook</h1>
  <p>Tap 🔊 to hear each phrase, then say it back. Slowly is fine!</p>
  <span class="st" id="st">No app · works offline once opened</span>
</header>
<nav class="chips" id="chips" aria-label="Lessons">%%CHIPS%%</nav>
<main>
  <div class="inst" id="inst"><b>📲 Keep it on your phone:</b> <span id="instHow">open the browser’s Share or ⋮ menu and choose “Add to Home Screen”. Open it once from the icon while online, and it works with no signal.</span></div>
  <div id="lessons"></div>
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
function waText(k){var L=D[k],a=L.phrases.slice(0,3).map(function(p){return p[0]+' = '+p[2];}).join('\\n');
 return '🐱 Fuku’s Japanese, '+(k==='0'?'first words':'lesson '+k+': '+L.title)+'\\n'+a+'\\n🔊 Hear them all (works offline): '+SITE+'/japan-phrasebook?l='+k+'&src=wa_self';}
var out=[];
Object.keys(D).forEach(function(k){var L=D[k],o=L.offer;
 out.push('<section id="l'+k+'"><h2><small>'+(k==='0'?'Start here':'Lesson '+k)+'</small>'+esc(L.title)+'</h2><ul>'+
  L.phrases.map(function(p,i){return '<li id="p'+k+'-'+(i+1)+'"><div><b>'+esc(p[0])+'</b><span class="ja" lang="ja">'+esc(p[1])+'</span><small>'+esc(p[2])+'</small></div><button type="button" data-k="'+k+'" data-i="'+i+'" aria-label="Play: '+esc(p[2])+'">🔊</button></li>';}).join('')+
  '</ul><div class="act"><a class="wa" data-wa="'+k+'" href="https://wa.me/?text='+encodeURIComponent(waText(k))+'" target="_blank" rel="noopener">📲 Send to my WhatsApp</a></div>'+
  (o?'<a class="off" data-off="'+k+'" href="'+esc(o.u)+'"'+(o.p?' target="_blank" rel="nofollow noopener sponsored" data-ps-placement="phrasebook-l'+k+'"':'')+'><i aria-hidden="true">'+o.i+'</i><span>'+esc(o.t)+'</span>'+(o.p?'<small>partner link ↗</small>':'<small>→</small>')+'</a>':'')+
  '</section>');});
document.getElementById('lessons').innerHTML=out.join('');
document.addEventListener('click',function(ev){var t=ev.target;
 var b=t.closest&&t.closest('[data-i]');if(b){var k=b.getAttribute('data-k'),p=D[k].phrases[+b.getAttribute('data-i')];say(p[1],p[0]);track('play',k+':'+p[0]);return;}
 var w=t.closest&&t.closest('[data-wa]');if(w){track('wa_self',w.getAttribute('data-wa'));return;}
 var o=t.closest&&t.closest('[data-off]');if(o){track('offer',o.getAttribute('data-off'));return;}
 var c=t.closest&&t.closest('.ch');if(c){track('chip',c.getAttribute('data-l'));}});
document.getElementById('askPacky').addEventListener('click',function(){track('packy');if(window.Packy)window.Packy.open();else location.href='/japan?src=phrasebook#ask';});
// the chip of the lesson on screen
var chips=[].slice.call(document.querySelectorAll('.ch'));
if('IntersectionObserver' in window){var io=new IntersectionObserver(function(es){es.forEach(function(x){if(x.isIntersecting){var k=x.target.id.slice(1);chips.forEach(function(c){var on=c.getAttribute('data-l')===k;c.classList.toggle('on',on);if(on)try{c.scrollIntoView({block:'nearest',inline:'center'});}catch(e){}});}});},{rootMargin:'-70px 0px -70% 0px'});
 [].forEach.call(document.querySelectorAll('section'),function(s){io.observe(s);});}
// deep links: ?l=1&p=3 or ?say=1-3 (the emails), #l3
var q=new URLSearchParams(location.search),m=/^([0-9])-([1-9])$/.exec(q.get('say')||''),lk=m?m[1]:(q.get('l')||''),pk=m?m[2]:(q.get('p')||'');
if(!D[lk])lk='';var src=(q.get('src')||'').toLowerCase().replace(/[^a-z0-9_-]/g,'').slice(0,40);
track('open',(lk||'all')+(src?' '+src:''));
if(lk){var el=document.getElementById(pk?'p'+lk+'-'+pk:'l'+lk)||document.getElementById('l'+lk);if(el){if(pk&&el.tagName==='LI')el.classList.add('hot');setTimeout(function(){el.scrollIntoView({block:pk?'center':'start'});},60);}}
// offline: the service worker keeps a copy; say so once it is ready
var standalone=!!(navigator.standalone||(window.matchMedia&&matchMedia('(display-mode: standalone)').matches));
if(standalone)document.getElementById('inst').hidden=true;
else if(/iPad|iPhone|iPod/.test(navigator.userAgent)||(navigator.platform==='MacIntel'&&navigator.maxTouchPoints>1))document.getElementById('instHow').textContent='tap Share, then “Add to Home Screen”. Open it once from the icon while online, and it works with no signal.';
if('serviceWorker' in navigator){navigator.serviceWorker.register('/japan-phrasebook-sw.js',{scope:'%%PAGE%%',updateViaCache:'none'})
 .then(function(){return navigator.serviceWorker.ready;}).then(function(){return caches.has('%%SWV%%');})
 .then(function(ok){if(ok)document.getElementById('st').textContent='Ready offline ✓';}).catch(function(){});}
})();
</script>
</body>
</html>
"""
PAGE_HTML = (PAGE_HTML.replace("%%CHIPS%%", chips).replace("%%DATA%%", DJSON)
             .replace("%%PAGE%%", PAGE).replace("%%SWV%%", SWV))
for tok in ("%%",):
    if tok in PAGE_HTML:
        die("a placeholder was left in the page")

SW = """/* Fuku's Phrasebook service worker (tools/w81_fuku_phrasebook.py). Network first, saved copy when offline. */
var V='%s';
var PAGE='%s';
var SHELL=[PAGE,'/japan-phrasebook.webmanifest','/favicon-32.png','/images/phrasebook-icon-192.png','/images/phrasebook-icon-512.png'];
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
    "icons": [{"src": "/images/phrasebook-icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
              {"src": "/images/phrasebook-icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
              {"src": "/images/phrasebook-icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]},
    indent=2, ensure_ascii=False)

for f in ("images/phrasebook-icon-192.png", "images/phrasebook-icon-512.png", "images/phrasebook-icon-maskable-512.png", "images/phrasebook-apple-touch-180.png"):
    if not os.path.exists(os.path.join(PUB, f)):
        die("missing icon " + f)
open(os.path.join(PUB, "japan-phrasebook.html"), "w", encoding="utf-8").write(PAGE_HTML)
open(os.path.join(PUB, "japan-phrasebook-sw.js"), "w", encoding="utf-8").write(SW)
open(os.path.join(PUB, "japan-phrasebook.webmanifest"), "w", encoding="utf-8").write(MANIFEST + "\n")
print("w81 done. Phrasebook: %d starter words, %d lessons." % (len(WORDS), len(LESSONS)))
