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
        narita: ['How do I get from Narita Airport to Tokyo Station?', 'Skyliner or Narita Express: which is faster?', 'Is the Skyliner covered by the JR Pass?'],
        haneda: ['How do I get from Haneda to Shinjuku?', 'Monorail or Keikyu from Haneda: which should I take?', 'How do I get from Haneda to Tokyo Station?'],
        kansai: ['How do I get from Kansai Airport to Kyoto?', 'Haruka or Nankai to Osaka: which should I take?', 'Do I need cash in Japan?'],
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
    '.pk-fab{position:fixed;right:16px;bottom:calc(16px + env(safe-area-inset-bottom));z-index:100;display:flex;align-items:center;gap:8px;background:linear-gradient(135deg,#00C9A7,#00A88C);color:#fff;border:0;border-radius:999px;padding:6px 18px 6px 6px;min-height:52px;font:800 15px/1 "DM Sans","Plus Jakarta Sans",sans-serif;box-shadow:0 8px 22px rgba(15,15,35,.25),0 0 0 3px rgba(178,255,236,.7),0 0 26px 6px rgba(120,255,220,.6);cursor:pointer;transition:bottom .2s,transform .15s}' +
    '.pk-fab:after{content:"";position:absolute;inset:0;border-radius:inherit;pointer-events:none;animation:pkHalo 2.8s ease-out infinite}' +
    '@keyframes pkHalo{0%{box-shadow:0 0 0 2px rgba(150,255,228,.75)}70%,100%{box-shadow:0 0 0 18px rgba(150,255,228,0)}}' +
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
    '.pk-hb button{width:38px;height:38px;border:0;background:none;color:#C9D1F0;cursor:pointer;border-radius:10px;display:inline-flex;align-items:center;justify-content:center;padding:0}.pk-hb button:hover{background:rgba(255,255,255,.12);color:#fff}' +
    '.pk-body{position:relative;flex:1;overflow-y:auto;padding:14px 12px;display:flex;flex-direction:column;gap:10px}' +
    '.pk-row{display:flex;gap:8px;align-items:flex-end;animation:pkIn .25s ease}' +
    '.pk-row .pk-face{width:28px;height:28px}' +
    '.pk-msg{max-width:86%;padding:10px 13px;font-size:15px;line-height:1.5}' +
    '.pk-msg p{margin:.2rem 0}.pk-msg ul{margin:.2rem 0 .2rem 1.1rem;padding:0}.pk-msg li{margin:.15rem 0}.pk-msg a{color:#0a8f78;font-weight:700}' +
    '.pk-bot{background:#fff;border-radius:18px 18px 18px 6px;box-shadow:0 2px 8px rgba(15,15,35,.07)}' +
    '.pk-me{margin-left:auto;background:linear-gradient(135deg,#00C9A7,#00A88C);color:#fff;border-radius:18px 18px 6px 18px;box-shadow:0 4px 12px rgba(0,168,140,.3);animation:pkIn .2s ease}' +
    '.pk-card{background:linear-gradient(135deg,#E6FAF5,#F4FFFC);border:1.5px solid #BFEDE3;border-radius:16px;padding:12px 14px;font-size:14.5px;line-height:1.45}' +
    '.pk-card b{display:block;font-size:15.5px;margin-bottom:3px}.pk-card p{margin:0 0 8px;color:#3f4a5c}' +
    '.pk-card .pk-go{display:inline-block;background:#0f0f23;color:#fff!important;text-decoration:none;font-weight:800;border-radius:999px;padding:9px 16px}' +
    '.pk-mail{background:linear-gradient(135deg,#FFF1F4,#FFF8FA);border-color:#F7B9C6}' +
    '.pk-quick{display:flex;gap:6px;margin-top:6px}.pk-quick input{flex:1;min-width:0;font:inherit;font-size:16px;border:1.5px solid #F2C4CF;border-radius:999px;padding:9px 14px;background:#fff;outline:none}.pk-quick input:focus{border-color:#E94560}' +
    '.pk-quick button,.pk-yes{flex:none;font:inherit;font-weight:800;font-size:14.5px;border:0;border-radius:999px;padding:9px 16px;background:linear-gradient(135deg,#E94560,#ff6b85);color:#fff;cursor:pointer}.pk-quick button[disabled]{opacity:.6}' +
    '.pk-row2{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}.pk-no,.pk-mo{font:inherit;font-size:13.5px;font-weight:700;border:1.5px solid #E3E8EC;background:#fff;color:#3f4a5c;border-radius:999px;padding:7px 12px;cursor:pointer}.pk-mo:hover,.pk-no:hover{border-color:#E94560}' +
    '.pk-fine{display:block;font-size:11px;color:#8a93a6;margin-top:6px}.pk-fine a{color:#8a93a6}' +
    '.pk-offer{display:flex;align-items:center;gap:7px;margin:10px 0 0;padding:7px 10px;border-radius:10px;background:#FFFAFB;border:1px solid #F3D3DB;color:#3f4a5c!important;text-decoration:none!important;font-size:12.5px;line-height:1.35;transition:border-color .15s}' +
    '.pk-offer:hover{border-color:#E94560}.pk-offer i{font-style:normal;font-size:14px;flex:none}' +
    '.pk-offer b{flex:1;font-weight:600;color:#0f0f23}.pk-offer small{font-size:10.5px;color:#8a93a6;white-space:nowrap}.pk-offer em{font-style:normal;color:#E94560;font-weight:700}' +
    '.pk-pocket{margin:8px 0 0;padding-top:7px;border-top:1px dashed #D5DCE0}' +
    '.pk-soft{display:inline;margin:0;font-size:12.5px;font-weight:600;color:#0a8f78!important;text-decoration:none!important}.pk-soft:hover{text-decoration:underline!important}' +
    '.pk-more{font-size:14px;border-top:1px dashed #D5DCE0;margin-top:10px!important;padding-top:8px}' +
    '.pk-src{font-size:11.5px;color:#8a93a6;margin-top:8px!important;line-height:1.4}.pk-msg .pk-src a{color:#6b7a8f;font-weight:500}' +
    '.pk-err{background:#FFF1F4}' +
    '.pk-dots{display:inline-flex;gap:4px;padding:4px 2px}.pk-dots i{width:8px;height:8px;border-radius:50%;background:#00C9A7;animation:pkDot 1s infinite ease-in-out}.pk-dots i:nth-child(2){animation-delay:.15s;background:#7FE3D0}.pk-dots i:nth-child(3){animation-delay:.3s;background:#E94560}' +
    '.pk-chips{display:flex;flex-wrap:wrap;gap:6px;margin-left:36px}' +
    '.pk-chips .pk-lbl{width:100%;font-size:11.5px;font-weight:800;letter-spacing:.05em;text-transform:uppercase;color:#5a6378;margin:2px 0 0}' +
    '.pk-chips button{display:inline-flex;align-items:center;gap:6px;font:inherit;font-size:13.5px;font-weight:600;text-align:left;background:#fff;color:#0f0f23;border:1.5px solid #BFEDE3;border-radius:999px;padding:7px 12px;cursor:pointer;animation:pkIn .3s ease both;transition:border-color .15s,transform .15s}' +
    '.pk-chips .pk-mailchip{border-color:#F7B9C6;background:#FFF5F7}' +
    '.pk-sent b{overflow-wrap:anywhere}.pk-other{background:none;border:0;padding:0;color:#0a8f78;font:inherit;font-weight:700;text-decoration:underline;cursor:pointer}' +
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
    '@media (prefers-reduced-motion:reduce){.pk-panel,.pk-row,.pk-me,.pk-chips button,.pk-tip,.pk-fab.pk-hello,.pk-fab:after{animation:none!important}.pk-dots i{animation:none}}' +
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
    '<div class="pk-hb"><button type="button" class="pk-new" aria-label="Start a new chat" title="New chat"><svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 12a8 8 0 1 1-2.34-5.66"/><path d="M20 4v5h-5"/></svg></button><button type="button" class="pk-x" aria-label="Close Packy" title="Close"><svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg></button></div></div>' +
    '<div class="pk-body" aria-live="polite"></div>' +
    '<form class="pk-form" autocomplete="off"><label class="pk-sr" for="pkQ">Your question</label><input id="pkQ" type="text" maxlength="300" placeholder="Ask Packy about ' + esc(C.name) + '…"><button type="submit" class="pk-send" aria-label="Send">&#10148;</button></form>' +
    '<div class="pk-note">Answers come from official sources. Prices and times change, so check before you travel. Booking buttons may be partner links (<a href="/affiliate-disclosure">disclosure</a>). Please don’t type personal details. <a href="/privacy-policy">Privacy</a></div>';
  document.body.appendChild(fab); document.body.appendChild(panel);
  var body = panel.querySelector('.pk-body'), form = panel.querySelector('.pk-form'), input = panel.querySelector('#pkQ'), send = form.querySelector('.pk-send');
  var history = load(), started = false, busy = false;

  function botRow(html, cls) { var r = el('div', 'pk-row'); r.innerHTML = '<span class="pk-face">' + FACE + '</span>'; var m = el('div', 'pk-msg pk-bot' + (cls ? ' ' + cls : ''), html); r.appendChild(m); body.appendChild(r); return r; }
  function meRow(q) { var m = el('div', 'pk-msg pk-me', esc(q)); body.appendChild(m); return m; }
  // one icon per kind of offer (the ticket only for tours and tickets)
  var OFFER_ICON = { insurance: '🩺', esim: '📶', bags: '🧳', transfer: '🚐', limousine: '🚌', car: '🚗', hotel: '🏨', tour: '🎟️', jrpass: '🚄', shinkansen: '🚄', nex: '🚆', skyliner: '🚆' };
  function offerHtml(o) {
    if (!o || !o.url || !/^(https:\/\/|\/)/.test(o.url)) return '';
    var ext = /^https:/.test(o.url);
    return '<a class="pk-offer" data-offer="' + esc(o.id || '') + '" href="' + esc(o.url) + '"' + (ext ? ' target="_blank" rel="nofollow noopener sponsored"' : '') + '>' +
      '<i aria-hidden="true">' + (OFFER_ICON[o.id] || (o.partner ? '🎟️' : '👉')) + '</i><b>' + esc(o.label) + '</b>' + (o.partner ? '<small>partner link</small>' : '') +
      '<em aria-hidden="true">' + (ext ? '↗' : '→') + '</em></a>';
  }
  // order under an answer: our own guide first (keeps the reader on PackSmart), then the booking button, then the official
  // sources, small and last (they open in a new tab)
  function splitSrc(a) { var m = String(a || '').match(/\n?[ \t]*\**Sources?:\**[ \t]*(.+)\s*$/i); return m ? [a.slice(0, m.index).trim(), m[1]] : [a, '']; }
  function answerHtml(a, guide, offer) {
    var p = splitSrc(a);
    return fmt(p[0]) + (guide ? '<p class="pk-more">📖 More in our <a href="' + esc(guide.url) + '">' + esc(guide.title) + '</a></p>' : '') + offerHtml(offer) +
      (p[1] ? '<p class="pk-src">Source: ' + fmt(p[1]).replace(/^<p>|<\/p>$/g, '') + '</p>' : '');
  }
  function chips(list, label) {
    var old = body.querySelector('.pk-chips'); if (old) old.remove();
    if (!list || !list.length) return;
    var box = el('div', 'pk-chips'); box.appendChild(el('p', 'pk-lbl', label));
    var mailChip = history.length >= 2 && history.length > sentN() && !body.querySelector('form.pk-mail');
    var known = savedEmail();
    list.forEach(function (q, i) {
      var b = el('button', '', '<span aria-hidden="true">' + icon(q) + '</span>' + esc(q)); b.type = 'button'; b.style.animationDelay = (i * 0.07) + 's';
      b.addEventListener('click', function () { track('chip'); ask(q); }); box.appendChild(b);
    });
    if (mailChip) {
      var m = el('button', 'pk-mailchip', '<span aria-hidden="true">\uD83D\uDCE9</span>' + (known ? (sentN() ? 'Email the updated chat to ' : 'Email this chat to ') + esc(mask(known)) : 'Email me this chat')); m.type = 'button'; m.style.animationDelay = (list.length * 0.07) + 's';
      m.addEventListener('click', function () {
        track(known ? 'email_chip_resend' : 'email_chip'); m.remove();
        if (known) return resend(known);
        var c = emailCard(); if (c) setTimeout(function () { c.scrollIntoView({ block: 'center' }); var i = c.querySelector('input'); if (i) i.focus({ preventScroll: true }); }, 60);
      });
      box.appendChild(m);
    }
    body.appendChild(box);
  }
  function start() {
    if (started) return; started = true;
    botRow(fmt(C.hello));
    history.forEach(function (h) { meRow(h.q); botRow(answerHtml(h.a, h.guide, h.offer)); });
    var last = history[history.length - 1];
    chips(last && last.next && last.next.length ? last.next : STARTERS, last ? 'Ask next' : 'Try one of these');
  }

  // the Pocket Guide that matches the conversation (from the guide Packy linked last, else the page's topic)
  var POCKET = { 'sapporo-station-guide': ['sapporo', 'Sapporo Station'], 'new-chitose-airport-guide': ['new-chitose', 'New Chitose Airport'],
    'ueno-station-guide': ['ueno', 'Ueno Station'], 'shinjuku-station-guide': ['shinjuku', 'Shinjuku Station'], 'tokyo-station-guide': ['tokyo', 'Tokyo Station'],
    'kyoto-station-guide': ['kyoto', 'Kyoto Station'], 'osaka-station-guide': ['osaka', 'Shin-Osaka and Umeda'], 'narita-airport-guide': ['narita', 'Narita Airport'],
    'haneda-airport-guide': ['haneda', 'Haneda Airport'], 'kansai-airport-guide': ['kix', 'Kansai Airport'] };
  var TOPIC_POCKET = { sapporo: 'sapporo-station-guide', 'new-chitose': 'new-chitose-airport-guide', ueno: 'ueno-station-guide', shinjuku: 'shinjuku-station-guide',
    tokyo: 'tokyo-station-guide', kyoto: 'kyoto-station-guide', osaka: 'osaka-station-guide' };
  // email and chat stay in step: how many answers the last email held (this visit), and the address, remembered on this
  // device only (localStorage), so an updated chat is one tap away. "Use another email" forgets it.
  function sentN() { try { return +sessionStorage.getItem('packy_sent_n') || 0; } catch (e) { return 0; } }
  function markSent() { try { sessionStorage.setItem('packy_sent_n', String(history.length)); } catch (e) {} }
  function savedEmail() { try { var v = localStorage.getItem('packy_email') || ''; return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v) ? v : ''; } catch (e) { return ''; } }
  function keepEmail(v) { try { if (v) localStorage.setItem('packy_email', v); else localStorage.removeItem('packy_email'); } catch (e) {} }
  function mask(v) { var p = v.split('@'); return p[0].charAt(0) + '…@' + p[1]; }
  function postMail(body2) {
    return fetch('/api/email-chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body2) })
      .then(function (x) { return x.json().then(function (d) { return [x.ok, d]; }); });
  }
  function mailBody(em, again) {
    var last = history[history.length - 1];
    var g = null; history.forEach(function (h) { if (h.guide) g = h.guide; });
    return { email: em, tips: false, again: !!again, country: country, page: location.pathname, next: (last && last.next) || [], pocket: pocketFor(g),
      items: history.map(function (h) { return { q: h.q, a: h.a, offer: h.offer ? { label: h.offer.label, url: h.offer.url } : null, guide: h.guide || null }; }) };
  }
  function resend(em) {
    var r = botRow('<div class="pk-card pk-sent"><b>📩 Sending the updated chat to ' + esc(mask(em)) + '…</b></div>'); r.querySelector('.pk-msg').style.background = 'transparent';
    var ch = body.querySelector('.pk-chips'); if (ch) body.insertBefore(r, ch); scrollToQ(r);
    var c = r.querySelector('.pk-sent');
    postMail(mailBody(em, true)).then(function (x) {
      if (!x[0] || !x[1].ok) { c.innerHTML = '<b>Sorry, that did not send</b><p>' + esc((x[1] && x[1].error) || 'Please try again.') + '</p>'; track('email_error'); chips(lastNext(), 'Ask next'); return; }
      markSent(); track('email_resent');
      c.innerHTML = '<b>✅ Updated chat sent to ' + esc(mask(em)) + '</b><p>It has every question so far, and a button to carry on here. <button type="button" class="pk-other">Use another email</button></p>';
      c.querySelector('.pk-other').addEventListener('click', function () { keepEmail(''); track('email_other'); c.querySelector('p').remove(); var k = emailCard(true); if (k) { var i = k.querySelector('input'); if (i) i.focus(); } });
    }).catch(function () { c.innerHTML = '<b>Packy needs an internet connection to send the email.</b>'; chips(lastNext(), 'Ask next'); });
  }
  function lastNext() { var l = history[history.length - 1]; return l && l.next && l.next.length ? l.next : STARTERS; }
  function once(k) { try { if (sessionStorage.getItem('packy_' + k)) return false; sessionStorage.setItem('packy_' + k, '1'); } catch (e) {} return true; }
  function pocketFor(guide) {   // the Pocket Guide's key (e.g. 'narita'), or '' for none
    var slug = guide && guide.url ? guide.url.split('/').pop().split('#')[0] : '';
    var p = POCKET[slug] || POCKET[TOPIC_POCKET[topic]]; return p ? p[0] : '';
  }
  function pocketCard(guide) {
    var slug = guide && guide.url ? guide.url.split('/').pop().split('#')[0] : '';
    var p = POCKET[slug] || POCKET[TOPIC_POCKET[topic]];
    var html = p
      ? '<a class="pk-soft" href="/' + p[0] + '-pocket?src=packy">📱 Free offline Pocket Guide for ' + esc(p[1]) + '&nbsp;→</a></div>'
      : '<a class="pk-soft" href="/japan?src=packy#pocket-hub">📱 Free offline Pocket Guides for ' + esc(C.name) + '\'s airports and stations&nbsp;→</a>';
    // a quiet footnote at the end of Packy's last answer, not a card of its own (owner, 26 Nov)
    var bots = body.querySelectorAll('.pk-msg.pk-bot'), last = bots[bots.length - 1];
    if (last) { var d = el('div', 'pk-pocket', html); last.appendChild(d); } else botRow(html);
    track('pocket_card');
  }
  function emailCard(force) {
    if (!history.length) { botRow('Ask me something first, then I can email you the whole chat.'); scrollDown(); return; }
    var old = body.querySelector('form.pk-mail'); if (old) { var i0 = old.querySelector('input'); if (i0) i0.focus(); old.scrollIntoView({ block: 'center' }); return; }
    var r = botRow('<form class="pk-card pk-mail" novalidate><b>📩 Get this chat by email</b>' +
      '<div class="pk-quick"><input type="email" name="email" autocomplete="email" inputmode="email" required placeholder="Your email" aria-label="Your email"><button type="submit">Send</button></div>' +
      '<span class="pk-fine">Just this chat, with the official links. <a href="/privacy-policy">Privacy</a></span></form>');
    r.querySelector('.pk-msg').style.background = 'transparent';
    var card = r.querySelector('form'), btn = card.querySelector('button'), inp = card.querySelector('input');
    var post = postMail;
    card.addEventListener('submit', function (e) {
      e.preventDefault();
      var em = inp.value.trim(); if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(em)) { inp.focus(); inp.style.borderColor = '#E94560'; return; }
      btn.disabled = true; btn.textContent = '…';
      post(mailBody(em, !!force))
        .then(function (x) {
          if (!x[0] || !x[1].ok) { btn.disabled = false; btn.textContent = 'Send'; botRow(esc((x[1] && x[1].error) || 'Sorry, that did not work.'), 'pk-err'); track('email_error'); return; }
          track('email_sent'); markSent(); keepEmail(em);
          var mc = body.querySelector('.pk-mailchip'); if (mc) mc.remove();
          // step 2: trip tips, a clear separate yes
          card.outerHTML = '<div class="pk-card pk-mail"><b>✅ Sent to ' + esc(em) + '</b><p>Want trip tips for ' + esc(C.name) + ' before you go?</p>' +
            '<div class="pk-row2"><button type="button" class="pk-yes">Yes please</button><button type="button" class="pk-no">No thanks</button></div></div>';
          var c2 = r.querySelector('.pk-mail');
          c2.querySelector('.pk-no').addEventListener('click', function () { c2.innerHTML = '<b>✅ Sent to ' + esc(em) + '</b><p>Check your inbox (and spam, just in case). Safe travels! 🇯🇵</p>'; track('tips_no'); });
          c2.querySelector('.pk-yes').addEventListener('click', function () {
            // step 3: the trip month, one tap
            var d = new Date(); d.setDate(1); var chips = '';
            for (var i = 0; i < 8; i++) { var v = d.getFullYear() + '-' + ('0' + (d.getMonth() + 1)).slice(-2); chips += '<button type="button" class="pk-mo" data-m="' + v + '">' + d.toLocaleString('en', { month: 'short' }) + (d.getMonth() === 0 || i === 0 ? ' ' + d.getFullYear() : '') + '</button>'; d.setMonth(d.getMonth() + 1); }
            c2.innerHTML = '<b>Great! When is your trip?</b><div class="pk-row2">' + chips + '<button type="button" class="pk-mo" data-m="">Not sure</button></div><span class="pk-fine">You can unsubscribe any time.</span>';
            [].forEach.call(c2.querySelectorAll('.pk-mo'), function (m) {
              m.addEventListener('click', function () {
                var trip = m.getAttribute('data-m'); [].forEach.call(c2.querySelectorAll('.pk-mo'), function (z) { z.disabled = true; });
                post({ update: true, email: em, tips: true, trip: trip, country: country, qs: history.map(function (h) { return h.q; }).slice(-10) }).then(function (x) {
                  c2.innerHTML = x[0] && x[1].ok ? '<b>🎉 You’re on the list</b><p>We’ll send a few useful tips before your trip. Check your inbox for your chat now.</p>'
                    : '<b>Your chat is on its way</b><p>' + esc((x[1] && x[1].error) || 'We could not save the trip tips, sorry.') + '</p>';
                  track(x[0] && x[1].ok ? 'tips_yes' : 'tips_error');
                }).catch(function () { c2.innerHTML = '<b>Your chat is on its way</b><p>We could not save the trip tips without a connection.</p>'; });
              });
            });
          });
        })
        .catch(function () { btn.disabled = false; btn.textContent = 'Send'; botRow('Packy needs an internet connection to send the email.', 'pk-err'); });
    });
    track('email_card'); return r;
  }
  function scrollDown() { body.scrollTop = body.scrollHeight; }
  // show a new answer from its start: the traveller's question at the top, the answer below it, the next questions last
  function scrollToQ(m) { if (!m) return scrollDown(); var top = m.offsetTop - 10; if (still) body.scrollTop = top; else try { body.scrollTo({ top: top, behavior: 'smooth' }); } catch (e) { body.scrollTop = top; } }
  function ask(q) {
    q = (q || '').trim(); if (q.length < 5 || busy) { input.focus(); return; }
    open(true); busy = true;
    var c = body.querySelector('.pk-chips'); if (c) c.remove();
    var mine = meRow(q); var wait = botRow('<span class="pk-dots" aria-label="Packy is checking the official sources"><i></i><i></i><i></i></span>'); scrollDown();
    send.disabled = true; input.value = '';
    fetch('/api/ask', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ q: q, prev: history.length ? history[history.length - 1].q : '', country: country, topic: topic }) })
      .then(function (r) { return r.json().then(function (d) { return [r.ok, d]; }); })
      .then(function (x) {
        var ok = x[0], d = x[1]; wait.remove();
        if (!ok || !d.ok) { botRow(esc((d && d.error) || 'Sorry, something went wrong. Please try again.'), 'pk-err'); chips(STARTERS, 'Or try one of these'); track('error'); return; }
        botRow(answerHtml(d.answer, d.guide, d.offer));
        var next = (d.next && d.next.length) ? d.next : STARTERS.filter(function (s) { return s !== q; });
        history.push({ q: q, a: d.answer, guide: d.guide, offer: d.offer || null, next: d.next || [] }); save(history); track('answered');
        var n = history.length;
        if (n === 2 && once('pocket')) pocketCard(d.guide);
        if (n === 3 && !savedEmail() && once('email')) emailCard();
        chips(next, 'Ask next');
      })
      .catch(function () { wait.remove(); botRow('Packy needs an internet connection 📶 Please try again when you are online.', 'pk-err'); track('offline'); })
      .then(function () { busy = false; send.disabled = false; scrollToQ(mine); });
  }
  function open(fromAsk) {
    hideTip(); start();
    if (panel.hidden) { panel.hidden = false; fab.hidden = true; fab.setAttribute('aria-expanded', 'true'); track('open'); }
    if (!fromAsk) { var qs = body.querySelectorAll('.pk-me'); scrollToQ(qs[qs.length - 1]); setTimeout(function () { input.focus({ preventScroll: true }); }, 60); }
  }
  function close() { panel.hidden = true; fab.setAttribute('aria-expanded', 'false'); syncFab(); fab.focus(); }
  function reset() { history = []; save(history); body.innerHTML = ''; started = false; start(); input.focus(); track('new_chat'); }
  fab.addEventListener('click', function () { open(false); });
  panel.querySelector('.pk-x').addEventListener('click', close);
  panel.querySelector('.pk-new').addEventListener('click', reset);
  panel.addEventListener('keydown', function (e) { if (e.key === 'Escape') close(); });
  body.addEventListener('click', function (e) { var a = e.target.closest && e.target.closest('.pk-offer'); if (a) { try { if (window.gtag) gtag('event', 'ask_' + country, { event_category: 'engagement', status: 'offer_click', offer: a.getAttribute('data-offer'), page_path: location.pathname }); } catch (x) {} } });
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

  // "Continue this chat with Packy" from the email: the chat is in the link after #packy= (compressed), never on a server
  // a booking button or guide link from the email link: our own pages, or the partner hosts Packy uses (never any other site)
  var PARTNER_HOST = /^https:\/\/([a-z0-9]+\.tpx\.li|tpx\.li|www\.getyourguide\.com|www\.japan-bullettrain\.com|www\.safetywing\.com)\//;
  function linkOk(x, offer) {
    if (!Array.isArray(x) || typeof x[0] !== 'string' || typeof x[1] !== 'string') return null;
    var site = /^\/[a-z0-9\/#-]*$/i.test(x[1]), ext = offer && PARTNER_HOST.test(x[1]);
    if (!site && !ext) return null;
    return offer ? { id: 'email', label: x[0].slice(0, 80), url: x[1], partner: ext } : { title: x[0].slice(0, 80), url: x[1] };
  }
  function restore() {
    var m = /[#&]packy=([A-Za-z0-9_-]{8,12000})/.exec(location.hash); if (!m) return;
    try { window.history.replaceState(null, '', location.pathname + location.search); } catch (e) {}
    function welcome(t) { open(false); var ch = body.querySelector('.pk-chips'); var r = botRow(t); if (ch) body.insertBefore(r, ch); setTimeout(function () { body.scrollTop = r.offsetTop - 10; }, 150); track('email_return'); }
    if (!window.DecompressionStream || !window.Response) return welcome('👋 Welcome back! Your chat is in your email. Ask me your next question here.');
    var b64 = m[1].replace(/-/g, '+').replace(/_/g, '/'); while (b64.length % 4) b64 += '=';
    var bin = atob(b64), bytes = new Uint8Array(bin.length); for (var i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
    new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('deflate-raw'))).text().then(function (t) {
      var d = JSON.parse(t);
      if (!d || d.c !== country || !Array.isArray(d.i)) throw 0;
      var h = d.i.slice(-10).filter(function (x) { return Array.isArray(x) && typeof x[0] === 'string' && typeof x[1] === 'string'; })
        .map(function (x) { return { q: x[0].slice(0, 300), a: x[1].slice(0, 4000), offer: linkOk(x[2], true), guide: linkOk(x[3], false), next: [] }; });
      if (!h.length) throw 0;
      h[h.length - 1].next = (Array.isArray(d.n) ? d.n : []).filter(function (x) { return typeof x === 'string'; }).slice(0, 3).map(function (x) { return x.slice(0, 120); });
      history = h; save(history); markSent(); once('pocket'); once('email');
      body.innerHTML = ''; started = false;
      welcome('👋 Welcome back! Here is your chat from the email. Ask your next question below, and I can send you the updated chat.');
    }).catch(function () { welcome('👋 Welcome back! I could not open the chat from that link, but it is all in your email. Ask me your next question here.'); });
  }
  restore();

  window.Packy = { open: function () { open(false); }, ask: ask, count: function () { return history.length; } };
})();
