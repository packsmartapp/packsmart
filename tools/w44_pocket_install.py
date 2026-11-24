#!/usr/bin/env python3
"""
w44: easier install for every offline pocket guide (Haneda, Narita, KIX, Osaka, Kyoto, Tokyo).

Run from the repo root, AFTER the pocket generators:  python3 tools/w44_pocket_install.py

What it changes in each public/<guide>-pocket.html (idempotent, marker: install-v2):
  * Android Chrome/Edge/Samsung: when the browser says the guide is installable, the sheet is one big
    "Install" button (no three-dot steps), and the "Add this to your home screen" strip installs in one tap.
    If the browser's signal arrives late, an open sheet switches to the Install button by itself.
  * Pages opened inside another app (Instagram, Facebook, TikTok, Line and similar): a clear "open it in
    Safari / Chrome" screen with a Copy link button instead of steps that cannot work there.
  * iPhone: same steps as before (Apple gives websites no install button), plus a short reason to do it.
  * First-visit sheet: opens straight away when the person arrived by tapping a "Save to your phone" button
    (?src=hero, box or bar). Otherwise it opens by itself on Android only; iPhone users see the strip.
  * Bumps each guide's cache name by one (xxx-pocket-vN -> N+1) in the page and in its service worker, so phones pick up the new page.
Aborts without writing anything if an expected anchor is missing in any guide.
"""
import os, re, sys

PUB = os.path.join(os.getcwd(), "public")
GUIDES = {"haneda": "hnd", "narita": "nrt", "kix": "kix", "osaka": "osk", "kyoto": "kyo", "tokyo": "tok", "shinjuku": "sjk", "ueno": "uen", "new-chitose": "cts", "sapporo": "spr"}
MARK = "install-v2"


def die(msg):
    sys.exit("w44 aborted, nothing written: " + msg)


NEW_BLOCK = r'''var strip=$('instStrip'), dp=null;
  var STRIP_HOW=strip.innerHTML;
  var UA=navigator.userAgent||'';
  var inApp=/FBAN|FBAV|FB_IAB|Instagram|Line\/|Snapchat|TikTok|musical_ly|MicroMessenger|LinkedInApp|Pinterest|GSA\//.test(UA)||(isAnd&&/; wv\)/.test(UA));
  function needed(){ return mobile&&!standalone&&flag('__K__Installed')!=='1'; }
  function refresh(){
    var n=needed(); strip.hidden=!n;
    $('instHow').hidden=!n; $('instDesk').hidden=mobile;
    if(standalone||flag('__K__Installed')==='1'){ $('install').hidden=true; }
    updateStrip();
  }
  function updateStrip(){
    if(dp&&!isIOS){ strip.innerHTML='<span class="ico" aria-hidden="true">&#128242;</span><span><b>Install this guide</b><br>so it works with no internet</span><span class="go">Install</span>'; }
    else { strip.innerHTML=STRIP_HOW; }
  }
  var SHARE='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3v12"/><path d="M8 7l4-4 4 4"/><path d="M6 11H5a1 1 0 0 0-1 1v8a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-8a1 1 0 0 0-1-1h-1"/></svg>';
  var PLUS='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><rect x="4" y="4" width="16" height="16" rx="3"/><path d="M12 8v8M8 12h8"/></svg>';
  var DOTS='<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><circle cx="12" cy="5" r="2"/><circle cx="12" cy="12" r="2"/><circle cx="12" cy="19" r="2"/></svg>';
  var DOWN='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 4v11"/><path d="M7 11l5 5 5-5"/><path d="M5 20h14"/></svg>';
  function steps(list){ return '<ol class="istep">'+list.map(function(x,i){ return '<li><span class="n">'+(i+1)+'</span>'+x[0]+'<span>'+x[1]+'</span></li>'; }).join('')+'</ol>'; }
  function guideUrl(){ return location.origin+location.pathname; }
  function runInstall(){
    if(!dp) return false;
    var p=dp; dp=null; updateStrip();
    try{ p.prompt(); }catch(e){ return false; }
    try{ p.userChoice.then(function(r){ if(r&&r.outcome) pgTrack('pg_install_prompt',{outcome:r.outcome}); if(r&&r.outcome==='accepted') markInstalled(); }); }catch(e){}
    return true;
  }
  function openInst(quiet){
    if(!quiet) pgTrack('pg_install_view',{via:instVia});
    instVia='help';
    var h='', title='Add to your home screen', one=false;
    if(isIOS&&inApp){
      one=true;
      h+='<p class="lede">This page is open inside another app, which cannot add it to your home screen. Open it in <b>Safari</b> first.</p>';
      h+=steps([['','Tap <b>Copy link</b> below'],['','Open <b>Safari</b> and paste the link in the address bar'],['','Then add it to your home screen']]);
      h+='<button type="button" class="close" id="instCopy">Copy link</button>';
    } else if(isIOS){
      h+='<p class="lede">Do this once, now, while you have signal. Then it opens like an app, even with no internet.</p>';
      h+=steps([[SHARE,'Tap the <b>Share</b> button (a square with an arrow) in Safari'],[PLUS,'Scroll down and tap <b>Add to Home Screen</b>'],['','Tap <b>Add</b>']]);
      h+='<div class="tipbox">Cannot see Share? Tap the <b>&middot;&middot;&middot;</b> button first. Not in Safari? Open this page in <b>Safari</b> first.</div>';
      h+='<p class="small">Your phone may clear a saved copy you have not opened for a while, so open the guide again the day before you fly.</p>';
    } else if(dp){
      title='Install this guide'; one=true;
      h+='<p class="lede">One tap. Then it opens like an app, even with no internet.</p>';
      h+='<button type="button" class="close" id="instGo">Install</button>';
    } else if(inApp){
      one=true;
      h+='<p class="lede">This page is open inside another app. Open it in <b>Chrome</b> to install it.</p>';
      h+=steps([['','Tap <b>Copy link</b> below'],['','Open <b>Chrome</b> and paste the link in the address bar'],['','Then tap <b>Install</b>']]);
      h+='<button type="button" class="close" id="instCopy">Copy link</button>';
    } else {
      h+='<p class="lede">Do this once, now, while you have signal. Then it opens like an app, even with no internet.</p>';
      h+=steps([[DOTS,'Tap the menu <b>&#8942;</b> (three dots) in your browser'],[DOWN,'Tap <b>Install app</b> or <b>Add to Home screen</b>'],['','Tap <b>Install</b> or <b>Add</b>']]);
      h+='<div class="tipbox">Do not see it? Open this page in Chrome and try again.</div><p class="small">Open the guide again the day before you fly, so the saved copy is fresh.</p>';
    }
    h+=one?'<div class="row2"><button type="button" class="close ghost" id="instLater">Later</button></div>':'<div class="row2"><button type="button" class="close ghost" id="instLater">Later</button><button type="button" class="close" id="instDone">I added it</button></div>';
    $('instT').innerHTML='<span aria-hidden="true">&#128242;</span>'+title;
    $('instBody').innerHTML=h;
    if(!quiet){ lastTile=document.activeElement&&document.activeElement.focus?document.activeElement:null; }
    hideAll(); inst.hidden=false; scrim.hidden=false; inst.scrollTop=0;
    var go=$('instGo'); if(go){ go.addEventListener('click',function(){ runInstall(); closeSheet(); }); }
    var cp=$('instCopy'); if(cp){ cp.addEventListener('click',function(){
      var u=guideUrl(), done=function(){ cp.textContent='Link copied'; pgTrack('pg_install_copylink',{}); };
      try{ navigator.clipboard.writeText(u).then(done,function(){ cp.textContent=u; }); }catch(e){ cp.textContent=u; }
    }); }
    $('instLater').addEventListener('click',closeSheet);
    var dn=$('instDone'); if(dn){ dn.addEventListener('click',function(){ markInstalled(); closeSheet(); }); }
    (go||cp||dn||$('instLater')).focus();
  }
  function markInstalled(){ flag('__K__Installed','1'); refresh(); }
  strip.addEventListener('click',function(){ instVia='strip'; if(dp&&!isIOS){ pgTrack('pg_install_tap',{via:'strip'}); runInstall(); } else { openInst(); } });
  $('instBtn').addEventListener('click',function(){ instVia='help'; openInst(); });
  '''

OLD_BIP = "window.addEventListener('beforeinstallprompt',function(e){ e.preventDefault(); dp=e; });"
NEW_BIP = ("window.addEventListener('beforeinstallprompt',function(e){ e.preventDefault(); dp=e; updateStrip();\n"
           "    if(!inst.hidden&&!isIOS&&!inApp&&!$('instGo')) openInst(true); });")

AUTO_OLD_RE = r"if\(needed\(\)&&!flag\('(\w+)Intro'\)&&AUTO_INSTALL_SHEET\)\{ flag\('\1Intro','1'\); setTimeout\(function\(\)\{ if\(sheet\.hidden&&inst\.hidden\)\{ instVia='auto'; openInst\(\); \} \},700\); \}"


def auto_new(k):
    return ("(function(){ var m=location.search.match(/[?&]src=([^&]*)/), src=m?m[1]:'', intent=/^(hero|box|bar)$/.test(src);\n"
            "    if(needed()&&AUTO_INSTALL_SHEET&&(intent||(isAnd&&!flag('%sIntro')))){ flag('%sIntro','1'); var waited=false;\n"
            "      var go=function(){ if(isAnd&&!dp&&!inApp&&!waited){ waited=true; setTimeout(go,800); return; }\n"
            "        if(sheet.hidden&&inst.hidden){ instVia='auto'; openInst(); } };\n"
            "      setTimeout(go,700); } })();") % (k, k)


def bump(text):
    return re.sub(r"(\b[a-z]+-pocket-v)(\d+)", lambda m: m.group(1) + str(int(m.group(2)) + 1), text)


plan = {}
for g, k in GUIDES.items():
    pp = os.path.join(PUB, g + "-pocket.html")
    sp = os.path.join(PUB, g + "-sw.js")
    for p in (pp, sp):
        if not os.path.isfile(p):
            die("missing " + p)
    s = open(pp, encoding="utf-8").read()
    sw = open(sp, encoding="utf-8").read()
    if MARK in s:
        continue
    a = s.find("var strip=$('instStrip'), dp=null;")
    b = s.find("/* show this to staff */")
    if a < 0 or b < a:
        die("%s: install block not found" % g)
    old_block = s[a:b]
    if ("flag('%sInstalled')" % k) not in old_block:
        die("%s: unexpected storage prefix in the install block" % g)
    if s.count(OLD_BIP) != 1:
        die("%s: beforeinstallprompt line not found exactly once" % g)
    if not re.search(AUTO_OLD_RE, s):
        die("%s: first-visit line not found" % g)
    if s.count('id="instStrip"') != 1:
        die("%s: install strip not found" % g)
    if "pocket-v" not in sw or not re.search(r"\b%s-pocket-v\d+" % g, s):
        die("%s: cache name not found" % g)
    s = s[:a] + NEW_BLOCK.replace("__K__", k) + s[b:]
    s = s.replace(OLD_BIP, NEW_BIP)
    s = re.sub(AUTO_OLD_RE, lambda m: auto_new(m.group(1)), s)
    s = s.replace("var AUTO_INSTALL_SHEET=true;", "var AUTO_INSTALL_SHEET=true; /* " + MARK + " */", 1)
    s = bump(s)
    sw = bump(sw)
    plan[g] = (pp, s, sp, sw)

changed = []
for g, (pp, s, sp, sw) in plan.items():
    open(pp, "w", encoding="utf-8").write(s)
    open(sp, "w", encoding="utf-8").write(sw)
    changed.append("%s-pocket.html and %s-sw.js (cache bumped)" % (g, g))
print("changed:" if changed else "nothing to do (already applied)")
for c in changed:
    print("  - " + c)
