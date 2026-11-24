/* Packy: PackSmart's travel buddy, as a pop-up on any page (24 Nov 2026, D56).
   One Packy, scoped by country: each page loads this file with the country it belongs to, e.g.
     <script src="/packy.js" data-country="japan" data-topic="sapporo" defer></script>
   data-topic picks the starter questions and the guide Packy points to; data-hide-when="#ask" hides the
   floating button while that element (the inline Packy box on /japan) is on screen.
   After each answer Packy offers 2-3 follow-up questions (from /api/ask, which only uses checked official sources).
   window.Packy.open() and window.Packy.ask(question) let a page's own box hand questions to the pop-up.
   Added to pages by tools/w75_packy_rollout.py; edit here, not in the pages. */
(function () {
  var me = document.currentScript;
  if (!me || window.Packy) return;
  var country = (me.getAttribute('data-country') || 'japan').toLowerCase();
  var topic = (me.getAttribute('data-topic') || '').toLowerCase();
  var hideWhen = me.getAttribute('data-hide-when');

  var COUNTRIES = {
    japan: {
      name: 'Japan', flag: '🇯🇵',
      hello: 'Konnichiwa! 👋 I’m Packy, your Japan travel buddy. Ask me about getting around: trains, airports, money, luggage and more. My answers come from official sources like JR, the airports and JNTO.',
      starters: {
        '': ['How long is the Shinkansen from Tokyo to Osaka?', 'How do I top up a Suica card?', 'Can I use the JR Pass on the Nozomi?'],
        sapporo: ['How do I get from Sapporo Station to New Chitose Airport?', 'Where are the ATMs at Sapporo Station?', 'How do I get to Otaru from Sapporo?'],
        'new-chitose': ['How do I get from New Chitose Airport to Sapporo?', 'Is there a ski bus from the airport to Niseko?', 'What time is the last train to Sapporo?'],
        ueno: ['How do I get from Ueno to Narita Airport?', 'Where are the ATMs at Ueno Station?', 'How do I get to Ueno Park from the station?'],
        shinjuku: ['How do I get from Shinjuku to Narita Airport?', 'Where is the Shinjuku bus terminal?', 'Which exit for the West side of Shinjuku?'],
        tokyo: ['Where are the ATMs at Tokyo Station?', 'Which exit for Ginza from Tokyo Station?', 'How long is the Shinkansen from Tokyo to Kyoto?'],
        kyoto: ['Where are the ATMs at Kyoto Station?', 'How do I get from Kyoto to Osaka?', 'Where do the airport buses leave from at Kyoto Station?'],
        osaka: ['Where are the ATMs at Shin-Osaka Station?', 'How do I get from Osaka to Kyoto?', 'How long is the Shinkansen from Shin-Osaka to Hakata?'],
        japan: ['How long is the Shinkansen from Tokyo to Osaka?', 'How do I top up a Suica card?', 'Do I need cash in Japan?']
      }
    }
  };
  var C = COUNTRIES[country];
  if (!C) return;
  var STARTERS = C.starters[topic] || C.starters[''];
  var KEY = 'packy_' + country, HINT = 'packy_hint';
  var still = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Packy: a little teal backpack with a face
  var FACE = '<svg viewBox="0 0 40 40" aria-hidden="true"><path d="M14 9c0-3.3 2.7-6 6-6s6 2.7 6 6" fill="none" stroke="#0f0f23" stroke-width="2.6" stroke-linecap="round"/>' +
    '<rect x="7" y="8" width="26" height="28" rx="9" fill="#00C9A7"/><rect x="11" y="24" width="18" height="9" rx="4" fill="#00A88C"/>' +
    '<circle cx="15.5" cy="17" r="3.2" fill="#fff"/><circle cx="24.5" cy="17" r="3.2" fill="#fff"/><circle cx="16.2" cy="17.6" r="1.6" fill="#0f0f23"/><circle cx="25.2" cy="17.6" r="1.6" fill="#0f0f23"/>' +
    '<path d="M17 21.4c1.7 1.5 4.3 1.5 6 0" fill="none" stroke="#0f0f23" stroke-width="1.6" stroke-linecap="round"/><circle cx="12.6" cy="21" r="1.4" fill="#E94560" opacity=".55"/><circle cx="27.4" cy="21" r="1.4" fill="#E94560" opacity=".55"/></svg>';

  var css = '' +
    '.pk-fab{position:fixed;right:16px;bottom:calc(16px + env(safe-area-inset-bottom));z-index:100;display:flex;align-items:center;gap:8px;background:linear-gradient(135deg,#00C9A7,#00A88C);color:#fff;border:0;border-radius:999px;padding:6px 18px 6px 6px;min-height:52px;font:800 15px/1 "DM Sans","Plus Jakarta Sans",sans-serif;box-shadow:0 10px 28px rgba(0,168,140,.45),0 2px 6px rgba(15,15,35,.2);cursor:pointer;transition:bottom .2s,transform .15s}' +
    '.pk-fab:hover{transform:translateY(-2px)}.pk-fab:active{transform:scale(.97)}' +
    '.pk-fab .pk-face{width:40px;height:40px;background:#fff;border-radius:50%;padding:3px}' +
    '.pk-fab.pk-hello{animation:pkBounce 1s ease 1}' +
    '.pk-tip{position:fixed;right:16px;z-index:100;max-width:230px;background:#0f0f23;color:#fff;font:600 14px/1.35 "DM Sans",sans-serif;padding:10px 32px 10px 12px;border-radius:14px 14px 4px 14px;box-shadow:0 8px 22px rgba(15,15,35,.3);animation:pkPop .3s ease}' +
    '.pk-tip button{position:absolute;top:4px;right:4px;background:none;border:0;color:#C9D1F0;font-size:18px;width:26px;height:26px;cursor:pointer}' +
    '.pk-fab[hidden],.pk-panel[hidden],.pk-tip[hidden]{display:none!important}' +
    '.pk-face{display:inline-block;flex:none;width:34px;height:34px}.pk-face svg{width:100%;height:100%;display:block}' +
    '.pk-panel{position:fixed;right:20px;bottom:20px;z-index:101;width:390px;max-width:calc(100vw - 24px);height:600px;max-height:calc(100vh - 40px);display:flex;flex-direction:column;background:#F4FAF8;border-radius:24px;box-shadow:0 24px 60px rgba(15,15,35,.35);font-family:"DM Sans","Plus Jakarta Sans",sans-serif;color:#0f0f23;overflow:hidden;transform-origin:bottom right;animation:pkOpen .22s cubic-bezier(.2,.9,.3,1.2)}' +
    '.pk-head{position:relative;display:flex;align-items:center;gap:10px;padding:14px 10px 16px 14px;background:linear-gradient(135deg,#0f0f23 0%,#1d2b5a 100%);color:#fff}' +
    '.pk-head:after{content:"";position:absolute;left:0;right:0;bottom:0;height:4px;background:linear-gradient(90deg,#00C9A7,#7FE3D0,#E94560)}' +
    '.pk-head .pk-face{width:44px;height:44px;background:#fff;border-radius:14px;padding:3px}' +
    '.pk-head b{font-size:18px;letter-spacing:-.01em}.pk-head small{display:block;font-size:12.5px;color:#C9D1F0;font-weight:500;margin-top:2px}' +
    '.pk-tag{display:inline-block;font-size:11px;font-weight:800;background:rgba(255,255,255,.12);border-radius:999px;padding:3px 8px;margin-left:6px;vertical-align:2px}' +
    '.pk-beta{background:#E94560}' +
    '.pk-hb{margin-left:auto;display:flex;gap:2px}' +
    '.pk-hb button{width:38px;height:38px;border:0;background:none;color:#C9D1F0;font-size:20px;line-height:1;cursor:pointer;border-radius:10px}.pk-hb button:hover{background:rgba(255,255,255,.1);color:#fff}' +
    '.pk-body{flex:1;overflow-y:auto;padding:14px 12px;display:flex;flex-direction:column;gap:10px}' +
    '.pk-row{display:flex;gap:8px;align-items:flex-end;animation:pkIn .25s ease}' +
    '.pk-row .pk-face{width:28px;height:28px}' +
    '.pk-msg{max-width:86%;padding:10px 13px;font-size:15px;line-height:1.5}' +
    '.pk-msg p{margin:.2rem 0}.pk-msg ul{margin:.2rem 0 .2rem 1.1rem;padding:0}.pk-msg li{margin:.15rem 0}.pk-msg a{color:#0a8f78;font-weight:700}' +
    '.pk-bot{background:#fff;border-radius:18px 18px 18px 6px;box-shadow:0 2px 8px rgba(15,15,35,.07)}' +
    '.pk-me{margin-left:auto;background:linear-gradient(135deg,#00C9A7,#00A88C);color:#fff;border-radius:18px 18px 6px 18px;box-shadow:0 4px 12px rgba(0,168,140,.3);animation:pkIn .2s ease}' +
    '.pk-more{font-size:13px;border-top:1px dashed #D5DCE0;margin-top:8px!important;padding-top:6px}' +
    '.pk-err{background:#FFF1F4}' +
    '.pk-dots{display:inline-flex;gap:4px;padding:4px 2px}.pk-dots i{width:8px;height:8px;border-radius:50%;background:#00C9A7;animation:pkDot 1s infinite ease-in-out}.pk-dots i:nth-child(2){animation-delay:.15s;background:#7FE3D0}.pk-dots i:nth-child(3){animation-delay:.3s;background:#E94560}' +
    '.pk-chips{display:flex;flex-wrap:wrap;gap:6px;margin-left:36px}' +
    '.pk-chips .pk-lbl{width:100%;font-size:11.5px;font-weight:800;letter-spacing:.05em;text-transform:uppercase;color:#5a6378;margin:2px 0 0}' +
    '.pk-chips button{display:inline-flex;align-items:center;gap:6px;font:inherit;font-size:13.5px;font-weight:600;text-align:left;background:#fff;color:#0f0f23;border:1.5px solid #BFEDE3;border-radius:999px;padding:7px 12px;cursor:pointer;animation:pkIn .3s ease both;transition:border-color .15s,transform .15s}' +
    '.pk-chips button:hover{border-color:#00C9A7;transform:translateY(-1px)}' +
    '.pk-form{display:flex;gap:8px;align-items:center;padding:10px 12px 8px;background:#fff;border-top:1px solid #E6EEF0}' +
    '.pk-form input{flex:1;min-width:0;font:inherit;font-size:16px;border:1.5px solid #E3E8EC;background:#F7F9FA;border-radius:999px;padding:11px 16px;outline:none}.pk-form input:focus{border-color:#00C9A7;background:#fff}' +
    '.pk-send{flex:none;width:46px;height:46px;border:0;border-radius:50%;background:linear-gradient(135deg,#E94560,#ff6b85);color:#fff;font-size:19px;cursor:pointer;box-shadow:0 4px 12px rgba(233,69,96,.35)}.pk-send[disabled]{opacity:.55;cursor:wait}' +
    '.pk-note{font-size:11.5px;color:#8a93a6;padding:0 14px 10px;background:#fff;line-height:1.4}.pk-note a{color:#8a93a6}' +
    '.pk-sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}' +
    '@keyframes pkOpen{from{opacity:0;transform:scale(.85) translateY(20px)}to{opacity:1;transform:none}}' +
    '@keyframes pkIn{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}' +
    '@keyframes pkPop{from{opacity:0;transform:scale(.9)}to{opacity:1;transform:none}}' +
    '@keyframes pkDot{0%,80%,100%{transform:translateY(0);opacity:.6}40%{transform:translateY(-5px);opacity:1}}' +
    '@keyframes pkBounce{0%,100%{transform:none}30%{transform:translateY(-8px)}60%{transform:translateY(0)}80%{transform:translateY(-3px)}}' +
    '@media (prefers-reduced-motion:reduce){.pk-panel,.pk-row,.pk-me,.pk-chips button,.pk-tip,.pk-fab.pk-hello{animation:none!important}.pk-dots i{animation:none}}' +
    '@media (max-width:600px){.pk-panel{right:0;left:0;bottom:0;width:auto;max-width:none;height:88vh;max-height:none;border-radius:24px 24px 0 0;transform-origin:bottom center}.pk-fab{right:12px}.pk-tip{right:12px}}' +
    '@media print{.pk-fab,.pk-panel,.pk-tip{display:none!important}}';
  var st = document.createElement('style'); st.id = 'packy-css'; st.textContent = css; document.head.appendChild(st);

  function el(tag, cls, html) { var e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function fmt(t) {
    var h = esc(t).replace(/\*\*([^*]+)\*\*/g, '<b>$1</b>').replace(/\[([^\]]+)\]\(((?:https?:\/\/|\/)[^\s)]+)\)/g, function (m, x, u) {
      return '<a href="' + u + '"' + (/^https?:/.test(u) ? ' target="_blank" rel="noopener"' : '') + '>' + x + '</a>';
    });
    var out = '', list = false;
    h.split(/\n+/).forEach(function (l) {
      var m = l.match(/^\s*[-*•]\s+(.*)/);
      if (m) { if (!list) { out += '<ul>'; list = true; } out += '<li>' + m[1] + '</li>'; }
      else { if (list) { out += '</ul>'; list = false; } if (l.trim()) out += '<p>' + l + '</p>'; }
    });
    return out + (list ? '</ul>' : '');
  }
  function icon(q) {
    var s = q.toLowerCase();
    if (/ski|snow|niseko/.test(s)) return '⛷️';
    if (/atm|cash|money|yen|card|pay/.test(s) && !/suica|pasmo|ic card/.test(s)) return '💴';
    if (/suica|pasmo|icoca|ic card|top up/.test(s)) return '💳';
    if (/locker|luggage|bag|suitcase/.test(s)) return '🧳';
    if (/airport|flight|narita|haneda|chitose|kix/.test(s)) return '✈️';
    if (/bus/.test(s)) return '🚌';
    if (/shinkansen|train|jr|rail|nozomi|line/.test(s)) return '🚄';
    if (/exit|gate|where|which/.test(s)) return '🧭';
    if (/visa|customs|passport|bring/.test(s)) return '🛂';
    if (/blossom|weather|season|rain|zoo|park|festival/.test(s)) return '🌸';
    return '✨';
  }
  function track(status) { try { if (window.gtag) gtag('event', 'ask_' + country, { event_category: 'engagement', status: status, page_path: location.pathname }); } catch (e) {} }
  function load() { try { return JSON.parse(sessionStorage.getItem(KEY) || '[]'); } catch (e) { return []; } }
  function save(h) { try { sessionStorage.setItem(KEY, JSON.stringify(h.slice(-10))); } catch (e) {} }

  var fab = el('button', 'pk-fab', '<span class="pk-face">' + FACE + '</span>Ask Packy');
  fab.type = 'button'; fab.setAttribute('aria-label', 'Ask Packy, your ' + C.name + ' travel buddy'); fab.setAttribute('aria-expanded', 'false');
  var panel = el('div', 'pk-panel');
  panel.hidden = true; panel.setAttribute('role', 'dialog'); panel.setAttribute('aria-labelledby', 'pkT');
  panel.innerHTML = '<div class="pk-head"><span class="pk-face">' + FACE + '</span><div><b id="pkT">Packy</b><span class="pk-tag">' + C.flag + ' ' + esc(C.name) + '</span><span class="pk-tag pk-beta">Beta</span><small>Your ' + esc(C.name) + ' travel buddy</small></div>' +
    '<div class="pk-hb"><button type="button" class="pk-new" aria-label="Start a new chat" title="New chat">&#8635;</button><button type="button" class="pk-x" aria-label="Close Packy" title="Close">&times;</button></div></div>' +
    '<div class="pk-body" aria-live="polite"></div>' +
    '<form class="pk-form" autocomplete="off"><label class="pk-sr" for="pkQ">Your question</label><input id="pkQ" type="text" maxlength="300" placeholder="Ask Packy about ' + esc(C.name) + '…"><button type="submit" class="pk-send" aria-label="Send">&#10148;</button></form>' +
    '<div class="pk-note">Answers come from official sources. Times change, so check before you travel. Please don’t type personal details. <a href="/privacy-policy">Privacy</a></div>';
  document.body.appendChild(fab); document.body.appendChild(panel);
  var body = panel.querySelector('.pk-body'), form = panel.querySelector('.pk-form'), input = panel.querySelector('#pkQ'), send = form.querySelector('.pk-send');
  var history = load(), started = false, busy = false;

  function botRow(html, cls) { var r = el('div', 'pk-row'); r.innerHTML = '<span class="pk-face">' + FACE + '</span>'; var m = el('div', 'pk-msg pk-bot' + (cls ? ' ' + cls : ''), html); r.appendChild(m); body.appendChild(r); return r; }
  function meRow(q) { body.appendChild(el('div', 'pk-msg pk-me', esc(q))); }
  function answerHtml(a, guide) { return fmt(a) + (guide ? '<p class="pk-more">📖 More in our <a href="' + esc(guide.url) + '">' + esc(guide.title) + '</a></p>' : ''); }
  function chips(list, label) {
    var old = body.querySelector('.pk-chips'); if (old) old.remove();
    if (!list || !list.length) return;
    var box = el('div', 'pk-chips'); box.appendChild(el('p', 'pk-lbl', label));
    list.forEach(function (q, i) {
      var b = el('button', '', '<span aria-hidden="true">' + icon(q) + '</span>' + esc(q)); b.type = 'button'; b.style.animationDelay = (i * 0.07) + 's';
      b.addEventListener('click', function () { track('chip'); ask(q); }); box.appendChild(b);
    });
    body.appendChild(box);
  }
  function start() {
    if (started) return; started = true;
    botRow(fmt(C.hello));
    history.forEach(function (h) { meRow(h.q); botRow(answerHtml(h.a, h.guide)); });
    var last = history[history.length - 1];
    chips(last && last.next && last.next.length ? last.next : STARTERS, last ? 'Ask next' : 'Try one of these');
  }
  function scrollDown() { body.scrollTop = body.scrollHeight; }
  function ask(q) {
    q = (q || '').trim(); if (q.length < 5 || busy) { input.focus(); return; }
    open(true); busy = true;
    var c = body.querySelector('.pk-chips'); if (c) c.remove();
    meRow(q); var wait = botRow('<span class="pk-dots" aria-label="Packy is checking the official sources"><i></i><i></i><i></i></span>'); scrollDown();
    send.disabled = true; input.value = '';
    fetch('/api/ask', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ q: q, prev: history.length ? history[history.length - 1].q : '', country: country, topic: topic }) })
      .then(function (r) { return r.json().then(function (d) { return [r.ok, d]; }); })
      .then(function (x) {
        var ok = x[0], d = x[1]; wait.remove();
        if (!ok || !d.ok) { botRow(esc((d && d.error) || 'Sorry, something went wrong. Please try again.'), 'pk-err'); chips(STARTERS, 'Or try one of these'); track('error'); return; }
        botRow(answerHtml(d.answer, d.guide));
        var next = (d.next && d.next.length) ? d.next : STARTERS.filter(function (s) { return s !== q; });
        chips(next, 'Ask next');
        history.push({ q: q, a: d.answer, guide: d.guide, next: d.next || [] }); save(history); track('answered');
      })
      .catch(function () { wait.remove(); botRow('Packy needs an internet connection 📶 Please try again when you are online.', 'pk-err'); track('offline'); })
      .then(function () { busy = false; send.disabled = false; scrollDown(); });
  }
  function open(fromAsk) {
    hideTip(); start();
    if (panel.hidden) { panel.hidden = false; fab.hidden = true; fab.setAttribute('aria-expanded', 'true'); track('open'); }
    scrollDown(); if (!fromAsk) setTimeout(function () { input.focus(); }, 60);
  }
  function close() { panel.hidden = true; fab.setAttribute('aria-expanded', 'false'); syncFab(); fab.focus(); }
  function reset() { history = []; save(history); body.innerHTML = ''; started = false; start(); input.focus(); track('new_chat'); }
  fab.addEventListener('click', function () { open(false); });
  panel.querySelector('.pk-x').addEventListener('click', close);
  panel.querySelector('.pk-new').addEventListener('click', reset);
  panel.addEventListener('keydown', function (e) { if (e.key === 'Escape') close(); });
  form.addEventListener('submit', function (e) { e.preventDefault(); ask(input.value); });

  // a one-time hello bubble next to the button, once per visit
  var tip = el('div', 'pk-tip', 'Questions about ' + esc(C.name) + '? Ask me! 👋<button type="button" aria-label="Dismiss">&times;</button>');
  tip.hidden = true; document.body.appendChild(tip);
  function hideTip() { tip.hidden = true; }
  tip.querySelector('button').addEventListener('click', hideTip);
  tip.addEventListener('click', function (e) { if (e.target === tip) open(false); });

  // keep the button clear of the guides' bottom "Pocket Guide" bar, and hidden while an inline Packy box is on screen
  var inlineOn = false, bar = document.getElementById('psPocketBar');
  function syncFab() {
    if (!panel.hidden) return;
    fab.hidden = inlineOn;
    var lift = (bar && bar.classList.contains('on')) ? bar.getBoundingClientRect().height : 0;
    var b = lift ? (lift + 12) : 16;
    fab.style.bottom = lift ? b + 'px' : '';
    tip.style.bottom = (b + 62) + 'px';
    if (fab.hidden) hideTip();
  }
  if (bar && 'MutationObserver' in window) new MutationObserver(syncFab).observe(bar, { attributes: true, attributeFilter: ['class', 'hidden', 'style'] });
  window.addEventListener('resize', syncFab);
  var target = hideWhen && document.querySelector(hideWhen);
  if (target && 'IntersectionObserver' in window) new IntersectionObserver(function (e) { inlineOn = e[0].isIntersecting; syncFab(); }).observe(target);
  syncFab();
  var seen = false; try { seen = sessionStorage.getItem(HINT) === '1'; } catch (e) {}
  if (!seen && !history.length) setTimeout(function () {
    if (!panel.hidden || fab.hidden) return;
    tip.hidden = false; if (!still) { fab.classList.add('pk-hello'); }
    try { sessionStorage.setItem(HINT, '1'); } catch (e) {}
    setTimeout(hideTip, 7000);
  }, 5000);

  window.Packy = { open: function () { open(false); }, ask: ask };
})();
