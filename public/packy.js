/* Packy: PackSmart's travel helper, as a pop-up on any page (24 Nov 2026, D56).
   One Packy, scoped by country: each page loads this file with the country it belongs to, e.g.
     <script src="/packy.js" data-country="japan" data-topic="sapporo" defer></script>
   data-topic picks the example questions and the guide Packy points to; data-hide-when="#ask" hides the
   floating button while that element (an inline Packy box) is on screen.
   Answers come from /api/ask, which only uses checked official sources for that country.
   Added to pages by tools/w75_packy_rollout.py; edit here, not in the pages. */
(function () {
  var me = document.currentScript;
  if (!me || window.__packy) return;
  window.__packy = true;
  var country = (me.getAttribute('data-country') || 'japan').toLowerCase();
  var topic = (me.getAttribute('data-topic') || '').toLowerCase();
  var hideWhen = me.getAttribute('data-hide-when');

  var COUNTRIES = {
    japan: {
      name: 'Japan',
      hello: 'Hi, I’m Packy, your Japan travel helper. Ask me about getting around: stations, airports, trains, buses, money or luggage. My answers come from official sources such as JR, the airports and JNTO.',
      suggest: {
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
  var SUG = C.suggest[topic] || C.suggest[''];
  var KEY = 'packy_' + country;

  var css = '' +
    '.packy-fab{position:fixed;right:16px;bottom:calc(16px + env(safe-area-inset-bottom));z-index:100;display:flex;align-items:center;gap:8px;background:#0f0f23;color:#fff;border:0;border-radius:999px;padding:8px 16px 8px 8px;min-height:48px;font:800 15px/1 "DM Sans","Plus Jakarta Sans",sans-serif;box-shadow:0 8px 24px rgba(15,15,35,.28);cursor:pointer;transition:bottom .2s}' +
    '.packy-fab[hidden],.packy-panel[hidden]{display:none!important}' +
    '.packy-av{width:30px;height:30px;flex:none;border-radius:50%;background:#00C9A7;color:#fff;font-weight:800;font-size:14px;display:inline-flex;align-items:center;justify-content:center}' +
    '.packy-panel{position:fixed;right:20px;bottom:20px;z-index:101;width:380px;max-width:calc(100vw - 24px);height:560px;max-height:calc(100vh - 40px);display:flex;flex-direction:column;background:#fff;border-radius:20px;box-shadow:0 18px 48px rgba(15,15,35,.3);font-family:"DM Sans","Plus Jakarta Sans",sans-serif;color:#0f0f23;overflow:hidden}' +
    '.packy-head{display:flex;align-items:center;gap:10px;padding:12px 12px 12px 14px;border-bottom:1px solid #E3E8EC}' +
    '.packy-head b{font-size:16px}.packy-head small{display:block;font-size:12px;color:#5a6378;font-weight:500}' +
    '.packy-beta{font-size:10px;font-weight:800;letter-spacing:.05em;text-transform:uppercase;background:#E6FAF5;color:#0a8f78;border-radius:999px;padding:2px 7px;margin-left:4px;vertical-align:2px}' +
    '.packy-x{margin-left:auto;width:40px;height:40px;border:0;background:none;font-size:26px;line-height:1;color:#5a6378;cursor:pointer;border-radius:10px}.packy-x:hover{background:#F5F7F9}' +
    '.packy-body{flex:1;overflow-y:auto;padding:14px;display:flex;flex-direction:column;gap:10px;background:#F8FBFA}' +
    '.packy-msg{max-width:90%;padding:9px 12px;border-radius:14px;font-size:15px;line-height:1.5}' +
    '.packy-msg p{margin:.2rem 0}.packy-msg ul{margin:.2rem 0 .2rem 1.1rem;padding:0}.packy-msg li{margin:.12rem 0}.packy-msg a{color:#0a8f78;font-weight:700}' +
    '.packy-bot{align-self:flex-start;background:#fff;border:1px solid #E3E8EC;border-radius:14px 14px 14px 4px}' +
    '.packy-me{align-self:flex-end;background:#0f0f23;color:#fff;border-radius:14px 14px 4px 14px}' +
    '.packy-more{font-size:13px;border-top:1px solid #E3E8EC;margin-top:6px!important;padding-top:6px}' +
    '.packy-busy{color:#5a6378;font-style:italic}.packy-err{background:#fff3f5}' +
    '.packy-sug{display:flex;flex-direction:column;gap:6px;align-items:flex-start}' +
    '.packy-sug button{font:inherit;font-size:13.5px;text-align:left;background:#fff;color:#0f0f23;border:1px solid #BFEDE3;border-radius:12px;padding:7px 11px;cursor:pointer}.packy-sug button:hover{border-color:#00C9A7}' +
    '.packy-form{display:flex;gap:8px;padding:10px 12px;border-top:1px solid #E3E8EC;background:#fff}' +
    '.packy-form input{flex:1;min-width:0;font:inherit;font-size:16px;border:1.5px solid #E3E8EC;border-radius:12px;padding:10px 12px;outline:none}.packy-form input:focus{border-color:#00C9A7}' +
    '.packy-form button{flex:none;font:inherit;font-weight:800;font-size:15px;background:#00C9A7;color:#fff;border:0;border-radius:12px;padding:0 16px;min-height:44px;cursor:pointer}.packy-form button[disabled]{opacity:.6;cursor:wait}' +
    '.packy-note{font-size:11.5px;color:#8a93a6;padding:0 12px 10px;background:#fff;line-height:1.4}.packy-note a{color:#8a93a6}' +
    '@media (max-width:600px){.packy-panel{right:0;left:0;bottom:0;width:auto;max-width:none;height:85vh;max-height:none;border-radius:20px 20px 0 0}.packy-fab{right:12px}}' +
    '@media print{.packy-fab,.packy-panel{display:none!important}}';
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
  function track(status) { try { if (window.gtag) gtag('event', 'ask_' + country, { event_category: 'engagement', status: status, page_path: location.pathname }); } catch (e) {} }
  function load() { try { return JSON.parse(sessionStorage.getItem(KEY) || '[]'); } catch (e) { return []; } }
  function save(h) { try { sessionStorage.setItem(KEY, JSON.stringify(h.slice(-10))); } catch (e) {} }

  var fab = el('button', 'packy-fab', '<span class="packy-av" aria-hidden="true">P</span>Ask Packy');
  fab.type = 'button'; fab.setAttribute('aria-label', 'Ask Packy, your ' + C.name + ' travel helper'); fab.setAttribute('aria-expanded', 'false');
  var panel = el('div', 'packy-panel');
  panel.hidden = true; panel.setAttribute('role', 'dialog'); panel.setAttribute('aria-labelledby', 'packyT');
  panel.innerHTML = '<div class="packy-head"><span class="packy-av" aria-hidden="true">P</span><div><b id="packyT">Packy &middot; ' + esc(C.name) + '<span class="packy-beta">Beta</span></b><small>Your ' + esc(C.name) + ' travel helper</small></div><button type="button" class="packy-x" aria-label="Close Packy">&times;</button></div>' +
    '<div class="packy-body" aria-live="polite"></div>' +
    '<form class="packy-form" autocomplete="off"><label class="packy-sr" style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)" for="packyQ">Your question</label><input id="packyQ" type="text" maxlength="300" placeholder="Ask about travel in ' + esc(C.name) + '"><button type="submit">Ask</button></form>' +
    '<div class="packy-note">Answers come from official sources. Times change, so check before you travel. Please don’t type personal details. <a href="/privacy-policy">Privacy</a></div>';
  document.body.appendChild(fab); document.body.appendChild(panel);
  var body = panel.querySelector('.packy-body'), form = panel.querySelector('.packy-form'), input = panel.querySelector('#packyQ'), send = form.querySelector('button');
  var history = load(), started = false;

  function addMe(q) { body.appendChild(el('div', 'packy-msg packy-me', esc(q))); }
  function addBot(a, guide) {
    var m = el('div', 'packy-msg packy-bot', fmt(a) + (guide ? '<p class="packy-more">More in our <a href="' + esc(guide.url) + '">' + esc(guide.title) + '</a></p>' : ''));
    body.appendChild(m); return m;
  }
  function suggestions() {
    var box = el('div', 'packy-sug');
    SUG.forEach(function (q) { var b = el('button', '', esc(q)); b.type = 'button'; b.addEventListener('click', function () { box.remove(); ask(q); }); box.appendChild(b); });
    body.appendChild(box);
  }
  function start() {
    if (started) return; started = true;
    addBot(C.hello, null);
    history.forEach(function (h) { addMe(h.q); addBot(h.a, h.guide); });
    if (!history.length) suggestions();
  }
  function scrollDown() { body.scrollTop = body.scrollHeight; }
  function ask(q) {
    q = (q || '').trim(); if (q.length < 5) { input.focus(); return; }
    var sug = body.querySelector('.packy-sug'); if (sug) sug.remove();
    addMe(q); var wait = addBot('Checking the official sources…'); wait.classList.add('packy-busy'); scrollDown();
    send.disabled = true; input.value = '';
    fetch('/api/ask', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ q: q, country: country, topic: topic }) })
      .then(function (r) { return r.json().then(function (d) { return [r.ok, d]; }); })
      .then(function (x) {
        var ok = x[0], d = x[1]; wait.remove();
        if (!ok || !d.ok) { addBot((d && d.error) || 'Sorry, something went wrong. Please try again.').classList.add('packy-err'); track('error'); return; }
        addBot(d.answer, d.guide); history.push({ q: q, a: d.answer, guide: d.guide }); save(history); track('answered');
      })
      .catch(function () { wait.remove(); addBot('Packy needs an internet connection. Please try again when you are online.').classList.add('packy-err'); track('offline'); })
      .then(function () { send.disabled = false; scrollDown(); });
  }
  function open() { start(); panel.hidden = false; fab.hidden = true; fab.setAttribute('aria-expanded', 'true'); scrollDown(); setTimeout(function () { input.focus(); }, 50); track('open'); }
  function close() { panel.hidden = true; fab.setAttribute('aria-expanded', 'false'); syncFab(); fab.focus(); }
  fab.addEventListener('click', open);
  panel.querySelector('.packy-x').addEventListener('click', close);
  panel.addEventListener('keydown', function (e) { if (e.key === 'Escape') close(); });
  form.addEventListener('submit', function (e) { e.preventDefault(); ask(input.value); });

  // keep the button clear of the guides' bottom "Pocket Guide" bar, and hidden while an inline Packy box is on screen
  var inlineOn = false, bar = document.getElementById('psPocketBar');
  function syncFab() {
    if (!panel.hidden) return;
    fab.hidden = inlineOn;
    var lift = 0;
    if (bar && bar.classList.contains('on')) lift = bar.getBoundingClientRect().height;
    fab.style.bottom = lift ? 'calc(' + (lift + 12) + 'px)' : '';
  }
  if (bar && 'MutationObserver' in window) new MutationObserver(syncFab).observe(bar, { attributes: true, attributeFilter: ['class', 'hidden', 'style'] });
  window.addEventListener('resize', syncFab);
  var target = hideWhen && document.querySelector(hideWhen);
  if (target && 'IntersectionObserver' in window) new IntersectionObserver(function (e) { inlineOn = e[0].isIntersecting; syncFab(); }).observe(target);
  syncFab();
})();
