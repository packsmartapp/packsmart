// =====================================================================
//  PackSmart Interactive Widgets V2
//  1. Interactive Packing Checklist with progress bar
//  2. Trip Countdown Timer (live ticking)
//  3. Currency Converter with dropdown + flags
//  4. Weather Widget (requires OPENWEATHER_API_KEY)
//  5. Enhanced Plan Styling (section cards, tabular info, icons)
//  Load AFTER packsmart-phase1.js in index.html
// =====================================================================

(function () {
  'use strict';

  // ── Shared helpers ──
  function showToast(msg) {
    var t = document.getElementById('ps-toast');
    if (!t) {
      t = document.createElement('div');
      t.id = 'ps-toast';
      t.style.cssText = 'position:fixed;bottom:30px;left:50%;transform:translateX(-50%);background:#00C9A7;color:#fff;padding:12px 28px;border-radius:30px;font-weight:600;font-size:15px;z-index:99999;opacity:0;transition:opacity .3s;box-shadow:0 4px 20px rgba(0,201,167,.4);pointer-events:none;';
      document.body.appendChild(t);
    }
    t.textContent = msg;
    t.style.opacity = '1';
    setTimeout(function () { t.style.opacity = '0'; }, 2500);
  }

  function getFormVal(id) { return (document.getElementById(id) || {}).value || ''; }

  // ── Popular currencies with flags ──
  var CURRENCIES = [
    { code: 'USD', flag: '🇺🇸', name: 'US Dollar' },
    { code: 'EUR', flag: '🇪🇺', name: 'Euro' },
    { code: 'GBP', flag: '🇬🇧', name: 'British Pound' },
    { code: 'INR', flag: '🇮🇳', name: 'Indian Rupee' },
    { code: 'JPY', flag: '🇯🇵', name: 'Japanese Yen' },
    { code: 'AUD', flag: '🇦🇺', name: 'Australian Dollar' },
    { code: 'CAD', flag: '🇨🇦', name: 'Canadian Dollar' },
    { code: 'CHF', flag: '🇨🇭', name: 'Swiss Franc' },
    { code: 'CNY', flag: '🇨🇳', name: 'Chinese Yuan' },
    { code: 'SGD', flag: '🇸🇬', name: 'Singapore Dollar' },
    { code: 'AED', flag: '🇦🇪', name: 'UAE Dirham' },
    { code: 'THB', flag: '🇹🇭', name: 'Thai Baht' },
    { code: 'MYR', flag: '🇲🇾', name: 'Malaysian Ringgit' },
    { code: 'IDR', flag: '🇮🇩', name: 'Indonesian Rupiah' },
    { code: 'PHP', flag: '🇵🇭', name: 'Philippine Peso' },
    { code: 'KRW', flag: '🇰🇷', name: 'South Korean Won' },
    { code: 'BRL', flag: '🇧🇷', name: 'Brazilian Real' },
    { code: 'MXN', flag: '🇲🇽', name: 'Mexican Peso' },
    { code: 'ZAR', flag: '🇿🇦', name: 'South African Rand' },
    { code: 'SEK', flag: '🇸🇪', name: 'Swedish Krona' },
    { code: 'NOK', flag: '🇳🇴', name: 'Norwegian Krone' },
    { code: 'DKK', flag: '🇩🇰', name: 'Danish Krone' },
    { code: 'NZD', flag: '🇳🇿', name: 'New Zealand Dollar' },
    { code: 'TRY', flag: '🇹🇷', name: 'Turkish Lira' },
    { code: 'SAR', flag: '🇸🇦', name: 'Saudi Riyal' },
    { code: 'HKD', flag: '🇭🇰', name: 'Hong Kong Dollar' },
    { code: 'TWD', flag: '🇹🇼', name: 'Taiwan Dollar' },
    { code: 'EGP', flag: '🇪🇬', name: 'Egyptian Pound' },
    { code: 'VND', flag: '🇻🇳', name: 'Vietnamese Dong' },
    { code: 'LKR', flag: '🇱🇰', name: 'Sri Lankan Rupee' }
  ];

  function buildCurrencyOptions(selectedCode) {
    var opts = '';
    for (var i = 0; i < CURRENCIES.length; i++) {
      var c = CURRENCIES[i];
      var sel = (c.code === selectedCode) ? ' selected' : '';
      opts += '<option value="' + c.code + '"' + sel + '>' + c.flag + '  ' + c.code + ' — ' + c.name + '</option>';
    }
    return opts;
  }

  // ── Section icons mapping ──
  var SECTION_ICONS = {
    'packing checklist': '🧳',
    'packing': '🧳',
    'destination briefing': '📋',
    'briefing': '📋',
    'local customs': '🙏',
    'customs & etiquette': '🙏',
    'etiquette': '🙏',
    'activity recommendations': '🎯',
    'activities': '🎯',
    'activity': '🎯',
    'travel day guide': '🗓️',
    'travel day': '🗓️',
    'smart reminders': '⏰',
    'reminders & timeline': '⏰',
    'timeline': '⏰',
    'safety & health': '🛡️',
    'safety': '🛡️',
    'health': '🛡️',
    'budget tips': '💰',
    'budget': '💰',
    'hotel recommendations': '🏨',
    'hotel': '🏨',
    'accommodation': '🏨',
    'day-by-day': '📅',
    'itinerary': '📅',
    'hidden gems': '💎',
    'must-see': '⭐'
  };

  var SECTION_COLORS = [
    { bg: '#f0fdf9', border: '#c6f0e4', accent: '#00C9A7' },
    { bg: '#eff6ff', border: '#bfdbfe', accent: '#3b82f6' },
    { bg: '#fef3f2', border: '#fecaca', accent: '#ef4444' },
    { bg: '#fefce8', border: '#fde68a', accent: '#eab308' },
    { bg: '#f5f3ff', border: '#ddd6fe', accent: '#8b5cf6' },
    { bg: '#fff7ed', border: '#fed7aa', accent: '#f97316' },
    { bg: '#fdf2f8', border: '#fbcfe8', accent: '#ec4899' },
    { bg: '#f0fdf4', border: '#bbf7d0', accent: '#22c55e' },
    { bg: '#ecfeff', border: '#a5f3fc', accent: '#06b6d4' },
    { bg: '#faf5ff', border: '#e9d5ff', accent: '#a855f7' }
  ];

  function getSectionIcon(title) {
    var lower = title.toLowerCase();
    for (var key in SECTION_ICONS) {
      if (lower.indexOf(key) !== -1) return SECTION_ICONS[key];
    }
    return '📌';
  }

  // ================================================================
  //  FEATURE 5: Enhanced Plan Styling
  // ================================================================
  function enhancePlanStyling() {
    var resBody = document.getElementById('resBody');
    if (!resBody) return;

    // Inject enhanced CSS
    if (!document.getElementById('ps-enhanced-css')) {
      var style = document.createElement('style');
      style.id = 'ps-enhanced-css';
      style.textContent =
        '.ps-section-card{background:#fff;border-radius:16px;padding:24px 28px;margin:20px 0;box-shadow:0 2px 16px rgba(0,0,0,.06);border-left:4px solid #00C9A7;transition:box-shadow .2s;}' +
        '.ps-section-card:hover{box-shadow:0 4px 24px rgba(0,0,0,.1);}' +
        '.ps-section-header{display:flex;align-items:center;gap:10px;margin-bottom:16px;padding-bottom:12px;border-bottom:1px solid #f0f0f0;}' +
        '.ps-section-icon{font-size:24px;width:40px;height:40px;display:flex;align-items:center;justify-content:center;border-radius:12px;flex-shrink:0;}' +
        '.ps-section-title{font-size:18px;font-weight:800;color:#0f0f23;margin:0;letter-spacing:-0.3px;}' +
        '.ps-info-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px;margin:12px 0;}' +
        '.ps-info-item{background:#f8f9fa;border-radius:10px;padding:12px 14px;border:1px solid #eee;}' +
        '.ps-info-label{font-size:11px;text-transform:uppercase;letter-spacing:1px;color:#888;font-weight:600;margin-bottom:4px;}' +
        '.ps-info-value{font-size:14px;font-weight:600;color:#0f0f23;}' +
        '.ps-section-card h4{color:#0f0f23;font-size:15px;font-weight:700;margin:16px 0 8px;padding:6px 0;border-bottom:1px dashed #e0e0e0;}' +
        '.ps-section-card ul{padding-left:0;list-style:none;}' +
        '.ps-section-card ul li{padding:6px 0 6px 24px;position:relative;border-bottom:1px solid #f5f5f5;font-size:14px;line-height:1.5;}' +
        '.ps-section-card ul li:last-child{border-bottom:none;}' +
        '.ps-section-card ul li::before{content:"›";position:absolute;left:8px;color:#00C9A7;font-weight:bold;font-size:16px;}' +
        '.ps-section-card p{font-size:14px;line-height:1.7;color:#444;}' +
        '.ps-section-card strong{color:#0f0f23;}' +
        '@media(max-width:600px){.ps-info-grid{grid-template-columns:1fr;}.ps-section-card{padding:18px 16px;}}';
      document.head.appendChild(style);
    }

    // Wrap each h3 section in a card
    var h3s = resBody.querySelectorAll('h3');
    if (h3s.length === 0) return;

    for (var i = 0; i < h3s.length; i++) {
      var h3 = h3s[i];
      // Skip if already wrapped
      if (h3.parentElement && h3.parentElement.classList.contains('ps-section-card')) continue;

      var title = h3.textContent.trim();
      var icon = getSectionIcon(title);
      var colorSet = SECTION_COLORS[i % SECTION_COLORS.length];

      // Collect all sibling elements until next h3
      var siblings = [];
      var next = h3.nextElementSibling;
      while (next && next.tagName !== 'H3') {
        siblings.push(next);
        next = next.nextElementSibling;
      }

      // Create card
      var card = document.createElement('div');
      card.className = 'ps-section-card';
      card.style.borderLeftColor = colorSet.accent;

      // Create header
      var header = document.createElement('div');
      header.className = 'ps-section-header';
      header.innerHTML = '<div class="ps-section-icon" style="background:' + colorSet.bg + ';">' + icon + '</div>' +
        '<div class="ps-section-title">' + title + '</div>';
      card.appendChild(header);

      // Move content into card
      for (var j = 0; j < siblings.length; j++) {
        card.appendChild(siblings[j]);
      }

      // Replace h3 with card
      h3.parentNode.replaceChild(card, h3);

      // Convert "Destination Briefing" section bullet points to info grid
      if (title.toLowerCase().indexOf('briefing') !== -1 || title.toLowerCase().indexOf('destination') !== -1) {
        convertToInfoGrid(card);
      }
    }
  }

  function convertToInfoGrid(card) {
    var uls = card.querySelectorAll('ul');
    for (var u = 0; u < uls.length; u++) {
      var ul = uls[u];
      var lis = ul.querySelectorAll('li');
      // Only convert if items look like "**Label:** Value" pattern
      var hasLabelPattern = false;
      for (var k = 0; k < lis.length; k++) {
        if (lis[k].innerHTML.indexOf('<strong>') !== -1 && lis[k].innerHTML.indexOf(':') !== -1) {
          hasLabelPattern = true;
          break;
        }
      }
      if (!hasLabelPattern || lis.length < 3) continue;

      var grid = document.createElement('div');
      grid.className = 'ps-info-grid';

      for (var m = 0; m < lis.length; m++) {
        var li = lis[m];
        var html = li.innerHTML;
        // Parse "**Label:** Value" or "<strong>Label:</strong> Value"
        var match = html.match(/<strong>([^<]+)<\/strong>\s*:?\s*(.*)/);
        if (match) {
          var label = match[1].replace(/:$/, '').trim();
          var value = match[2].replace(/^:\s*/, '').trim();
          var item = document.createElement('div');
          item.className = 'ps-info-item';
          item.innerHTML = '<div class="ps-info-label">' + label + '</div><div class="ps-info-value">' + value + '</div>';
          grid.appendChild(item);
        }
      }

      if (grid.children.length > 0) {
        ul.parentNode.replaceChild(grid, ul);
      }
    }
  }

  // ================================================================
  //  FEATURE 1: Interactive Packing Checklist
  // ================================================================
  var CHECKLIST_KEY = 'ps_checklist';

  function activateChecklist() {
    var resBody = document.getElementById('resBody');
    if (!resBody) return;

    var html = resBody.innerHTML;
    if (html.indexOf('\u2610') === -1 && html.indexOf('☐') === -1) return;

    var dest = getFormVal('destination');
    var saved = {};
    try { saved = JSON.parse(localStorage.getItem(CHECKLIST_KEY) || '{}'); } catch (e) { saved = {}; }
    var destChecked = (saved[dest] || {}).items || {};

    var itemIndex = 0;
    html = resBody.innerHTML; // re-read after styling changes
    html = html.replace(/☐\s*([^<\n]+)/g, function (match, itemText) {
      var idx = itemIndex++;
      var isChecked = destChecked[idx] === true;
      var checkedAttr = isChecked ? 'checked' : '';
      var strikeStyle = isChecked ? 'text-decoration:line-through;color:#999;' : '';
      return '<label class="ps-check-item" data-idx="' + idx + '" style="display:flex;align-items:center;gap:10px;padding:6px 8px;cursor:pointer;transition:all .2s;border-radius:8px;margin:2px 0;" onmouseover="this.style.background=\'#f0fdf9\'" onmouseout="this.style.background=\'transparent\'">' +
        '<input type="checkbox" class="ps-checkbox" data-idx="' + idx + '" ' + checkedAttr +
        ' style="width:20px;height:20px;accent-color:#00C9A7;cursor:pointer;flex-shrink:0;border-radius:4px;">' +
        '<span class="ps-check-text" style="' + strikeStyle + 'font-size:14px;">' + itemText.trim() + '</span></label>';
    });

    resBody.innerHTML = html;
    injectProgressBar(resBody, dest);

    var checkboxes = resBody.querySelectorAll('.ps-checkbox');
    for (var i = 0; i < checkboxes.length; i++) {
      checkboxes[i].addEventListener('change', function () {
        var textSpan = this.parentElement.querySelector('.ps-check-text');
        if (this.checked) {
          textSpan.style.textDecoration = 'line-through';
          textSpan.style.color = '#999';
        } else {
          textSpan.style.textDecoration = 'none';
          textSpan.style.color = '';
        }
        saveChecklistState(dest);
        updateProgress(dest);
      });
    }
  }

  function injectProgressBar(resBody, dest) {
    var old = document.getElementById('ps-progress-wrap');
    if (old) old.remove();

    var checkboxes = resBody.querySelectorAll('.ps-checkbox');
    if (checkboxes.length === 0) return;

    var wrap = document.createElement('div');
    wrap.id = 'ps-progress-wrap';
    wrap.style.cssText = 'background:linear-gradient(135deg,#f0fdf9,#e8faf4);border:1px solid #c6f0e4;border-radius:16px;padding:18px 22px;margin:16px 0 20px 0;';
    wrap.innerHTML = '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">' +
      '<span style="font-weight:700;font-size:15px;color:#0f0f23;">✅ Packing Progress</span>' +
      '<span id="ps-progress-text" style="font-size:14px;font-weight:600;color:#00C9A7;">0 / ' + checkboxes.length + '</span></div>' +
      '<div style="background:#e0e0e0;border-radius:10px;height:10px;overflow:hidden;">' +
      '<div id="ps-progress-bar" style="background:linear-gradient(90deg,#00C9A7,#00e6b8);height:100%;border-radius:10px;transition:width .4s ease;width:0%;"></div></div>' +
      '<div style="margin-top:10px;text-align:right;">' +
      '<button id="ps-reset-checklist" style="background:none;border:1px solid #E94560;color:#E94560;cursor:pointer;font-size:12px;font-weight:600;padding:4px 12px;border-radius:15px;transition:all .2s;" onmouseover="this.style.background=\'#E94560\';this.style.color=\'#fff\'" onmouseout="this.style.background=\'none\';this.style.color=\'#E94560\'">Reset All</button></div>';

    // Insert at the top of the first packing section card, or at top
    var packingCard = null;
    var cards = resBody.querySelectorAll('.ps-section-card');
    for (var c = 0; c < cards.length; c++) {
      var titleEl = cards[c].querySelector('.ps-section-title');
      if (titleEl && titleEl.textContent.toLowerCase().indexOf('packing') !== -1) {
        packingCard = cards[c];
        break;
      }
    }

    if (packingCard) {
      var header = packingCard.querySelector('.ps-section-header');
      if (header && header.nextSibling) {
        packingCard.insertBefore(wrap, header.nextSibling);
      } else {
        packingCard.appendChild(wrap);
      }
    } else {
      resBody.insertBefore(wrap, resBody.firstChild);
    }

    document.getElementById('ps-reset-checklist').addEventListener('click', function () {
      var cbs = resBody.querySelectorAll('.ps-checkbox');
      for (var i = 0; i < cbs.length; i++) {
        cbs[i].checked = false;
        var txt = cbs[i].parentElement.querySelector('.ps-check-text');
        txt.style.textDecoration = 'none';
        txt.style.color = '';
      }
      saveChecklistState(dest);
      updateProgress(dest);
      showToast('Checklist reset!');
    });

    updateProgress(dest);
  }

  function saveChecklistState(dest) {
    var checkboxes = document.querySelectorAll('.ps-checkbox');
    var items = {};
    for (var i = 0; i < checkboxes.length; i++) {
      if (checkboxes[i].checked) {
        items[checkboxes[i].getAttribute('data-idx')] = true;
      }
    }
    var saved = {};
    try { saved = JSON.parse(localStorage.getItem(CHECKLIST_KEY) || '{}'); } catch (e) { saved = {}; }
    saved[dest] = { items: items, updatedAt: new Date().toISOString() };
    localStorage.setItem(CHECKLIST_KEY, JSON.stringify(saved));
  }

  function updateProgress() {
    var checkboxes = document.querySelectorAll('.ps-checkbox');
    var total = checkboxes.length;
    var checked = 0;
    for (var i = 0; i < checkboxes.length; i++) {
      if (checkboxes[i].checked) checked++;
    }
    var pct = total > 0 ? Math.round((checked / total) * 100) : 0;
    var bar = document.getElementById('ps-progress-bar');
    var text = document.getElementById('ps-progress-text');
    if (bar) bar.style.width = pct + '%';
    if (text) text.textContent = checked + ' / ' + total + ' (' + pct + '%)';
    if (pct === 100 && total > 0) {
      showToast('🎉 All packed! You\'re ready to go!');
    }
  }

  // ================================================================
  //  FEATURE 2: Trip Countdown Timer
  // ================================================================
  function injectCountdown() {
    var old = document.getElementById('ps-countdown-wrap');
    if (old) old.remove();

    var startDate = getFormVal('startDate');
    var dest = getFormVal('destination');
    if (!startDate || !dest) return;

    var tripDate = new Date(startDate + 'T00:00:00');
    var now = new Date();
    if (tripDate - now <= 0) return;

    var wrap = document.createElement('div');
    wrap.id = 'ps-countdown-wrap';
    wrap.style.cssText = 'background:linear-gradient(135deg,#1a1a2e,#16213e);border-radius:16px;padding:28px;margin:16px 0;text-align:center;color:#fff;';
    wrap.innerHTML = '<div style="font-size:12px;color:#888;margin-bottom:4px;text-transform:uppercase;letter-spacing:2px;">Your trip to</div>' +
      '<div style="font-size:22px;font-weight:800;color:#00C9A7;margin-bottom:20px;letter-spacing:0.5px;">' + dest.toUpperCase() + '</div>' +
      '<div id="ps-countdown-timer" style="display:flex;justify-content:center;gap:14px;flex-wrap:wrap;"></div>';

    var resBody = document.getElementById('resBody');
    if (resBody && resBody.parentNode) {
      resBody.parentNode.insertBefore(wrap, resBody);
    }

    function tick() {
      var remaining = tripDate - new Date();
      if (remaining <= 0) {
        document.getElementById('ps-countdown-timer').innerHTML = '<div style="font-size:24px;font-weight:700;">🎉 Trip day is here!</div>';
        return;
      }
      var d = Math.floor(remaining / 86400000);
      var h = Math.floor((remaining % 86400000) / 3600000);
      var m = Math.floor((remaining % 3600000) / 60000);
      var s = Math.floor((remaining % 60000) / 1000);

      var box = 'background:rgba(255,255,255,0.06);border-radius:14px;padding:14px 18px;min-width:70px;backdrop-filter:blur(4px);border:1px solid rgba(255,255,255,0.08);';
      var num = 'font-size:30px;font-weight:800;color:#00C9A7;line-height:1;';
      var lbl = 'font-size:10px;color:#666;margin-top:6px;text-transform:uppercase;letter-spacing:1.5px;';

      document.getElementById('ps-countdown-timer').innerHTML =
        '<div style="' + box + '"><div style="' + num + '">' + d + '</div><div style="' + lbl + '">Days</div></div>' +
        '<div style="' + box + '"><div style="' + num + '">' + h + '</div><div style="' + lbl + '">Hours</div></div>' +
        '<div style="' + box + '"><div style="' + num + '">' + m + '</div><div style="' + lbl + '">Mins</div></div>' +
        '<div style="' + box + '"><div style="' + num + '">' + s + '</div><div style="' + lbl + '">Secs</div></div>';
    }

    tick();
    setInterval(tick, 1000);
  }

  // ================================================================
  //  FEATURE 3: Currency Converter with Dropdowns
  // ================================================================
  function injectCurrencyConverter() {
    var old = document.getElementById('ps-currency-wrap');
    if (old) old.remove();

    var homeCurrency = getFormVal('currency') || 'USD';
    var selectStyle = 'width:100%;padding:10px 12px;border:2px solid #eee;border-radius:10px;font-size:14px;font-weight:600;outline:none;background:#fff;cursor:pointer;appearance:auto;transition:border-color .2s;';

    var wrap = document.createElement('div');
    wrap.id = 'ps-currency-wrap';
    wrap.style.cssText = 'background:linear-gradient(135deg,#fff7ed,#fef3e2);border:1px solid #fde8c8;border-radius:16px;padding:22px 24px;margin:16px 0;';
    wrap.innerHTML =
      '<div style="font-weight:700;font-size:16px;color:#0f0f23;margin-bottom:16px;display:flex;align-items:center;gap:8px;">💱 Quick Currency Converter</div>' +
      '<div style="display:flex;gap:10px;align-items:flex-end;flex-wrap:wrap;">' +
        '<div style="flex:1;min-width:100px;">' +
          '<label style="font-size:11px;color:#888;display:block;margin-bottom:5px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;">Amount</label>' +
          '<input id="ps-curr-amount" type="number" value="100" min="0" step="any" style="width:100%;padding:10px 12px;border:2px solid #eee;border-radius:10px;font-size:16px;font-weight:700;outline:none;transition:border-color .2s;" onfocus="this.style.borderColor=\'#f97316\'" onblur="this.style.borderColor=\'#eee\'">' +
        '</div>' +
        '<div style="flex:1.3;min-width:140px;">' +
          '<label style="font-size:11px;color:#888;display:block;margin-bottom:5px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;">From</label>' +
          '<select id="ps-curr-from" style="' + selectStyle + '" onfocus="this.style.borderColor=\'#f97316\'" onblur="this.style.borderColor=\'#eee\'">' +
            buildCurrencyOptions(homeCurrency) +
          '</select>' +
        '</div>' +
        '<button id="ps-curr-swap" style="background:#fff;border:2px solid #eee;width:40px;height:40px;border-radius:50%;cursor:pointer;font-size:18px;display:flex;align-items:center;justify-content:center;flex-shrink:0;transition:all .2s;margin-bottom:2px;" title="Swap currencies" onmouseover="this.style.borderColor=\'#f97316\';this.style.background=\'#fff7ed\'" onmouseout="this.style.borderColor=\'#eee\';this.style.background=\'#fff\'">⇄</button>' +
        '<div style="flex:1.3;min-width:140px;">' +
          '<label style="font-size:11px;color:#888;display:block;margin-bottom:5px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;">To</label>' +
          '<select id="ps-curr-to" style="' + selectStyle + '" onfocus="this.style.borderColor=\'#f97316\'" onblur="this.style.borderColor=\'#eee\'">' +
            '<option value="">Select currency...</option>' +
            buildCurrencyOptions('') +
          '</select>' +
        '</div>' +
        '<button id="ps-curr-convert" style="background:linear-gradient(135deg,#f97316,#ea580c);color:#fff;border:none;padding:11px 24px;border-radius:25px;cursor:pointer;font-weight:700;font-size:14px;flex-shrink:0;box-shadow:0 3px 12px rgba(249,115,22,.3);transition:all .2s;" onmouseover="this.style.transform=\'translateY(-1px)\';this.style.boxShadow=\'0 5px 18px rgba(249,115,22,.4)\'" onmouseout="this.style.transform=\'none\';this.style.boxShadow=\'0 3px 12px rgba(249,115,22,.3)\'">Convert</button>' +
      '</div>' +
      '<div id="ps-curr-result" style="margin-top:16px;padding:16px;background:#fff;border-radius:12px;font-size:20px;font-weight:700;color:#0f0f23;text-align:center;display:none;box-shadow:0 1px 4px rgba(0,0,0,.06);"></div>' +
      '<div id="ps-curr-rate" style="text-align:center;font-size:11px;color:#999;margin-top:6px;display:none;"></div>';

    var resBody = document.getElementById('resBody');
    if (resBody && resBody.parentNode) {
      var countdown = document.getElementById('ps-countdown-wrap');
      if (countdown && countdown.nextSibling) {
        countdown.parentNode.insertBefore(wrap, countdown.nextSibling);
      } else if (countdown) {
        countdown.parentNode.appendChild(wrap);
      } else {
        resBody.parentNode.insertBefore(wrap, resBody);
      }
    }

    document.getElementById('ps-curr-convert').addEventListener('click', doConvert);
    document.getElementById('ps-curr-swap').addEventListener('click', function () {
      var from = document.getElementById('ps-curr-from');
      var to = document.getElementById('ps-curr-to');
      var temp = from.value;
      from.value = to.value;
      to.value = temp;
    });

    // Enter key on amount
    document.getElementById('ps-curr-amount').addEventListener('keydown', function (e) {
      if (e.key === 'Enter') doConvert();
    });
  }

  function doConvert() {
    var amount = parseFloat(document.getElementById('ps-curr-amount').value);
    var from = document.getElementById('ps-curr-from').value;
    var to = document.getElementById('ps-curr-to').value;
    var resultDiv = document.getElementById('ps-curr-result');
    var rateDiv = document.getElementById('ps-curr-rate');

    if (!amount || !from || !to) {
      resultDiv.textContent = 'Please fill in all fields';
      resultDiv.style.display = 'block';
      resultDiv.style.color = '#E94560';
      resultDiv.style.fontSize = '15px';
      rateDiv.style.display = 'none';
      return;
    }

    resultDiv.textContent = 'Converting...';
    resultDiv.style.display = 'block';
    resultDiv.style.color = '#999';
    resultDiv.style.fontSize = '15px';
    rateDiv.style.display = 'none';

    // Find flag for display
    var fromFlag = '', toFlag = '';
    for (var i = 0; i < CURRENCIES.length; i++) {
      if (CURRENCIES[i].code === from) fromFlag = CURRENCIES[i].flag;
      if (CURRENCIES[i].code === to) toFlag = CURRENCIES[i].flag;
    }

    fetch('https://api.exchangerate-api.com/v4/latest/' + from)
      .then(function (resp) { return resp.json(); })
      .then(function (data) {
        if (data.rates && data.rates[to]) {
          var rate = data.rates[to];
          var converted = (amount * rate).toFixed(2);
          resultDiv.innerHTML = '<span style="color:#0f0f23;">' + fromFlag + ' ' + amount.toFixed(2) + ' ' + from + '</span>' +
            '<span style="color:#888;margin:0 10px;">→</span>' +
            '<span style="color:#f97316;font-size:24px;">' + toFlag + ' ' + converted + ' ' + to + '</span>';
          resultDiv.style.fontSize = '18px';
          rateDiv.textContent = '1 ' + from + ' = ' + rate.toFixed(4) + ' ' + to + '  •  ' + new Date().toLocaleTimeString();
          rateDiv.style.display = 'block';
        } else {
          resultDiv.textContent = 'Currency not found — try another';
          resultDiv.style.color = '#E94560';
        }
      })
      .catch(function () {
        resultDiv.textContent = 'Conversion failed — check connection';
        resultDiv.style.color = '#E94560';
      });
  }

  // ================================================================
  //  FEATURE 4: Weather Widget
  // ================================================================
  function injectWeatherWidget() {
    var old = document.getElementById('ps-weather-wrap');
    if (old) old.remove();

    var dest = getFormVal('destination');
    if (!dest) return;

    var wrap = document.createElement('div');
    wrap.id = 'ps-weather-wrap';
    wrap.style.cssText = 'background:linear-gradient(135deg,#e3f2fd,#e8eaf6);border:1px solid #c5cae9;border-radius:16px;padding:22px 24px;margin:16px 0;';
    wrap.innerHTML = '<div style="font-weight:700;font-size:16px;color:#0f0f23;margin-bottom:14px;display:flex;align-items:center;gap:8px;">🌤️ Current Weather in ' + dest + '</div>' +
      '<div id="ps-weather-content" style="text-align:center;color:#888;font-size:14px;padding:10px 0;">Loading weather data...</div>';

    var resBody = document.getElementById('resBody');
    if (resBody && resBody.parentNode) {
      var currency = document.getElementById('ps-currency-wrap');
      var countdown = document.getElementById('ps-countdown-wrap');
      var insertAfter = currency || countdown;
      if (insertAfter && insertAfter.nextSibling) {
        insertAfter.parentNode.insertBefore(wrap, insertAfter.nextSibling);
      } else if (insertAfter) {
        insertAfter.parentNode.appendChild(wrap);
      } else {
        resBody.parentNode.insertBefore(wrap, resBody);
      }
    }

    fetch('/api/weather?city=' + encodeURIComponent(dest))
      .then(function (resp) { return resp.json(); })
      .then(function (data) {
        if (data.success) {
          var w = data.weather;
          var iconUrl = 'https://openweathermap.org/img/wn/' + w.icon + '@2x.png';
          document.getElementById('ps-weather-content').innerHTML =
            '<div style="display:flex;align-items:center;justify-content:center;gap:24px;flex-wrap:wrap;">' +
            '<div><img src="' + iconUrl + '" alt="weather" style="width:80px;height:80px;filter:drop-shadow(0 2px 4px rgba(0,0,0,.1));"></div>' +
            '<div style="text-align:left;">' +
            '<div style="font-size:40px;font-weight:800;color:#0f0f23;line-height:1;">' + Math.round(w.temp) + '<span style="font-size:20px;color:#666;">°C</span></div>' +
            '<div style="font-size:15px;color:#444;text-transform:capitalize;margin-top:2px;">' + w.description + '</div>' +
            '<div style="font-size:12px;color:#888;margin-top:3px;">Feels like ' + Math.round(w.feelsLike) + '°C</div>' +
            '</div>' +
            '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">' +
            '<div style="background:#fff;border-radius:10px;padding:10px 14px;text-align:center;min-width:80px;"><div style="font-size:10px;color:#888;text-transform:uppercase;">Humidity</div><div style="font-size:16px;font-weight:700;color:#3b82f6;">' + w.humidity + '%</div></div>' +
            '<div style="background:#fff;border-radius:10px;padding:10px 14px;text-align:center;min-width:80px;"><div style="font-size:10px;color:#888;text-transform:uppercase;">Wind</div><div style="font-size:16px;font-weight:700;color:#22c55e;">' + w.windSpeed + ' km/h</div></div>' +
            '<div style="background:#fff;border-radius:10px;padding:10px 14px;text-align:center;"><div style="font-size:10px;color:#888;text-transform:uppercase;">High</div><div style="font-size:16px;font-weight:700;color:#ef4444;">' + Math.round(w.tempMax) + '°</div></div>' +
            '<div style="background:#fff;border-radius:10px;padding:10px 14px;text-align:center;"><div style="font-size:10px;color:#888;text-transform:uppercase;">Low</div><div style="font-size:16px;font-weight:700;color:#6366f1;">' + Math.round(w.tempMin) + '°</div></div>' +
            '</div></div>';
        } else {
          document.getElementById('ps-weather-content').innerHTML =
            '<div style="color:#888;">Weather unavailable. <a href="https://www.google.com/search?q=weather+' + encodeURIComponent(dest) + '" target="_blank" style="color:#3b82f6;text-decoration:none;font-weight:600;">Check on Google →</a></div>';
        }
      })
      .catch(function () {
        document.getElementById('ps-weather-content').innerHTML =
          '<div style="color:#888;">Weather unavailable. <a href="https://www.google.com/search?q=weather+' + encodeURIComponent(dest) + '" target="_blank" style="color:#3b82f6;text-decoration:none;font-weight:600;">Check on Google →</a></div>';
      });
  }

  // ================================================================
  //  MAIN: Poll for plan generation and activate all features
  // ================================================================
  var _widgetLastContent = '';

  function startWidgetPolling() {
    setInterval(function () {
      var resBody = document.getElementById('resBody');
      if (!resBody) return;
      var content = resBody.innerHTML.trim();
      if (content.length > 100 && content !== _widgetLastContent) {
        _widgetLastContent = content;
        setTimeout(function () {
          enhancePlanStyling();
          injectCountdown();
          injectCurrencyConverter();
          injectWeatherWidget();
          activateChecklist();
          _widgetLastContent = resBody.innerHTML.trim(); // update after our changes
        }, 800);
      }
    }, 600);
  }

  function init() {
    startWidgetPolling();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
