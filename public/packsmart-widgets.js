// =====================================================================
//  PackSmart Interactive Widgets
//  Feature 1: Interactive Packing Checklist
//  Feature 2: Trip Countdown Timer
//  Feature 3: Currency Converter
//  Feature 4: Weather Widget (requires OPENWEATHER_API_KEY)
//  Load AFTER packsmart-phase1.js in index.html
// =====================================================================

(function () {
  'use strict';

  // ── Shared: Toast (reuse from phase1 if available) ──
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

  // ── Helper: Get form values ──
  function getFormVal(id) { return (document.getElementById(id) || {}).value || ''; }

  // ================================================================
  //  FEATURE 1: Interactive Packing Checklist
  // ================================================================
  var CHECKLIST_KEY = 'ps_checklist';

  function activateChecklist() {
    var resBody = document.getElementById('resBody');
    if (!resBody) return;

    // Find all ☐ items in the rendered plan and convert to checkboxes
    var html = resBody.innerHTML;
    if (html.indexOf('\u2610') === -1 && html.indexOf('☐') === -1) return; // No checkbox items

    // Get saved state for current destination
    var dest = getFormVal('destination');
    var saved = {};
    try { saved = JSON.parse(localStorage.getItem(CHECKLIST_KEY) || '{}'); } catch (e) { saved = {}; }
    var destChecked = (saved[dest] || {}).items || {};

    // Replace ☐ with interactive checkboxes
    var itemIndex = 0;
    html = html.replace(/☐\s*([^<\n]+)/g, function (match, itemText) {
      var idx = itemIndex++;
      var isChecked = destChecked[idx] === true;
      var checkedAttr = isChecked ? 'checked' : '';
      var strikeStyle = isChecked ? 'text-decoration:line-through;color:#999;' : '';
      return '<label class="ps-check-item" data-idx="' + idx + '" style="display:flex;align-items:center;gap:8px;padding:4px 0;cursor:pointer;transition:all .2s;">' +
        '<input type="checkbox" class="ps-checkbox" data-idx="' + idx + '" ' + checkedAttr +
        ' style="width:18px;height:18px;accent-color:#00C9A7;cursor:pointer;flex-shrink:0;">' +
        '<span class="ps-check-text" style="' + strikeStyle + '">' + itemText.trim() + '</span></label>';
    });

    resBody.innerHTML = html;

    // Inject progress bar
    injectProgressBar(resBody, dest);

    // Attach checkbox handlers
    var checkboxes = resBody.querySelectorAll('.ps-checkbox');
    for (var i = 0; i < checkboxes.length; i++) {
      checkboxes[i].addEventListener('change', function () {
        var idx = parseInt(this.getAttribute('data-idx'));
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
      '<button id="ps-reset-checklist" style="background:none;border:none;color:#E94560;cursor:pointer;font-size:12px;font-weight:600;">Reset All</button></div>';

    // Insert before the first h3 (which is usually "Packing Checklist")
    var firstH3 = resBody.querySelector('h3');
    if (firstH3) {
      firstH3.parentNode.insertBefore(wrap, firstH3.nextSibling);
    } else {
      resBody.insertBefore(wrap, resBody.firstChild);
    }

    // Reset button
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

  function updateProgress(dest) {
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

    // Celebration when 100%
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
    if (!startDate) return;

    var dest = getFormVal('destination');
    if (!dest) return;

    var tripDate = new Date(startDate + 'T00:00:00');
    var now = new Date();

    // Only show countdown for future trips
    var diff = tripDate - now;
    if (diff <= 0) return;

    var wrap = document.createElement('div');
    wrap.id = 'ps-countdown-wrap';
    wrap.style.cssText = 'background:linear-gradient(135deg,#1a1a2e,#16213e);border-radius:16px;padding:24px;margin:16px 0;text-align:center;color:#fff;';

    wrap.innerHTML = '<div style="font-size:14px;color:#aaa;margin-bottom:6px;">YOUR TRIP TO</div>' +
      '<div style="font-size:22px;font-weight:700;color:#00C9A7;margin-bottom:16px;">' + dest.toUpperCase() + '</div>' +
      '<div id="ps-countdown-timer" style="display:flex;justify-content:center;gap:16px;"></div>';

    // Insert into results section
    var resBody = document.getElementById('resBody');
    if (resBody && resBody.parentNode) {
      resBody.parentNode.insertBefore(wrap, resBody);
    }

    function updateCountdown() {
      var now2 = new Date();
      var remaining = tripDate - now2;
      if (remaining <= 0) {
        document.getElementById('ps-countdown-timer').innerHTML = '<div style="font-size:24px;font-weight:700;">🎉 Trip day is here!</div>';
        return;
      }
      var days = Math.floor(remaining / (1000 * 60 * 60 * 24));
      var hours = Math.floor((remaining % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      var mins = Math.floor((remaining % (1000 * 60 * 60)) / (1000 * 60));
      var secs = Math.floor((remaining % (1000 * 60)) / 1000);

      var boxStyle = 'background:rgba(255,255,255,0.08);border-radius:12px;padding:12px 16px;min-width:65px;';
      var numStyle = 'font-size:28px;font-weight:800;color:#00C9A7;';
      var labelStyle = 'font-size:11px;color:#888;margin-top:4px;text-transform:uppercase;letter-spacing:1px;';

      document.getElementById('ps-countdown-timer').innerHTML =
        '<div style="' + boxStyle + '"><div style="' + numStyle + '">' + days + '</div><div style="' + labelStyle + '">Days</div></div>' +
        '<div style="' + boxStyle + '"><div style="' + numStyle + '">' + hours + '</div><div style="' + labelStyle + '">Hours</div></div>' +
        '<div style="' + boxStyle + '"><div style="' + numStyle + '">' + mins + '</div><div style="' + labelStyle + '">Mins</div></div>' +
        '<div style="' + boxStyle + '"><div style="' + numStyle + '">' + secs + '</div><div style="' + labelStyle + '">Secs</div></div>';
    }

    updateCountdown();
    setInterval(updateCountdown, 1000);
  }

  // ================================================================
  //  FEATURE 3: Currency Converter
  // ================================================================
  function injectCurrencyConverter() {
    var old = document.getElementById('ps-currency-wrap');
    if (old) old.remove();

    var homeCurrency = getFormVal('currency') || 'USD';

    var wrap = document.createElement('div');
    wrap.id = 'ps-currency-wrap';
    wrap.style.cssText = 'background:linear-gradient(135deg,#fff7ed,#fef3e2);border:1px solid #fde8c8;border-radius:16px;padding:20px 22px;margin:16px 0;';

    wrap.innerHTML = '<div style="font-weight:700;font-size:15px;color:#0f0f23;margin-bottom:14px;">💱 Quick Currency Converter</div>' +
      '<div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;">' +
      '<div style="flex:1;min-width:120px;">' +
      '<label style="font-size:12px;color:#666;display:block;margin-bottom:4px;">Amount</label>' +
      '<input id="ps-curr-amount" type="number" value="100" min="0" step="any" style="width:100%;padding:10px 12px;border:2px solid #ddd;border-radius:10px;font-size:15px;font-weight:600;outline:none;transition:border-color .2s;" onfocus="this.style.borderColor=\'#00C9A7\'" onblur="this.style.borderColor=\'#ddd\'">' +
      '</div>' +
      '<div style="flex:1;min-width:120px;">' +
      '<label style="font-size:12px;color:#666;display:block;margin-bottom:4px;">From</label>' +
      '<input id="ps-curr-from" type="text" value="' + homeCurrency + '" maxlength="3" style="width:100%;padding:10px 12px;border:2px solid #ddd;border-radius:10px;font-size:15px;font-weight:600;text-transform:uppercase;outline:none;transition:border-color .2s;" onfocus="this.style.borderColor=\'#00C9A7\'" onblur="this.style.borderColor=\'#ddd\'">' +
      '</div>' +
      '<button id="ps-curr-swap" style="background:#f0f0f0;border:none;padding:8px;border-radius:50%;cursor:pointer;font-size:18px;margin-top:18px;" title="Swap">⇄</button>' +
      '<div style="flex:1;min-width:120px;">' +
      '<label style="font-size:12px;color:#666;display:block;margin-bottom:4px;">To</label>' +
      '<input id="ps-curr-to" type="text" value="" maxlength="3" placeholder="EUR" style="width:100%;padding:10px 12px;border:2px solid #ddd;border-radius:10px;font-size:15px;font-weight:600;text-transform:uppercase;outline:none;transition:border-color .2s;" onfocus="this.style.borderColor=\'#00C9A7\'" onblur="this.style.borderColor=\'#ddd\'">' +
      '</div>' +
      '<button id="ps-curr-convert" style="background:#00C9A7;color:#fff;border:none;padding:10px 20px;border-radius:25px;cursor:pointer;font-weight:700;font-size:14px;margin-top:18px;box-shadow:0 2px 10px rgba(0,201,167,.3);">Convert</button>' +
      '</div>' +
      '<div id="ps-curr-result" style="margin-top:14px;font-size:18px;font-weight:700;color:#0f0f23;text-align:center;display:none;"></div>' +
      '<div id="ps-curr-rate" style="text-align:center;font-size:12px;color:#999;margin-top:4px;display:none;"></div>';

    // Insert into results section after countdown
    var resBody = document.getElementById('resBody');
    if (resBody && resBody.parentNode) {
      var countdown = document.getElementById('ps-countdown-wrap');
      if (countdown) {
        countdown.parentNode.insertBefore(wrap, countdown.nextSibling);
      } else {
        resBody.parentNode.insertBefore(wrap, resBody);
      }
    }

    // Convert button handler
    document.getElementById('ps-curr-convert').addEventListener('click', doConvert);

    // Enter key handler
    var inputs = wrap.querySelectorAll('input');
    for (var i = 0; i < inputs.length; i++) {
      inputs[i].addEventListener('keydown', function (e) {
        if (e.key === 'Enter') doConvert();
      });
    }

    // Swap button
    document.getElementById('ps-curr-swap').addEventListener('click', function () {
      var from = document.getElementById('ps-curr-from');
      var to = document.getElementById('ps-curr-to');
      var temp = from.value;
      from.value = to.value;
      to.value = temp;
    });
  }

  function doConvert() {
    var amount = parseFloat(document.getElementById('ps-curr-amount').value);
    var from = document.getElementById('ps-curr-from').value.toUpperCase().trim();
    var to = document.getElementById('ps-curr-to').value.toUpperCase().trim();
    var resultDiv = document.getElementById('ps-curr-result');
    var rateDiv = document.getElementById('ps-curr-rate');

    if (!amount || !from || !to) {
      resultDiv.textContent = 'Please fill in all fields';
      resultDiv.style.display = 'block';
      resultDiv.style.color = '#E94560';
      rateDiv.style.display = 'none';
      return;
    }

    resultDiv.textContent = 'Converting...';
    resultDiv.style.display = 'block';
    resultDiv.style.color = '#999';
    rateDiv.style.display = 'none';

    // Using free API (no key needed)
    fetch('https://api.exchangerate-api.com/v4/latest/' + from)
      .then(function (resp) { return resp.json(); })
      .then(function (data) {
        if (data.rates && data.rates[to]) {
          var rate = data.rates[to];
          var converted = (amount * rate).toFixed(2);
          resultDiv.innerHTML = '<span style="color:#00C9A7;">' + amount.toFixed(2) + ' ' + from + '</span> = <span style="color:#E94560;">' + converted + ' ' + to + '</span>';
          resultDiv.style.color = '#0f0f23';
          rateDiv.textContent = '1 ' + from + ' = ' + rate.toFixed(4) + ' ' + to + ' • Updated: ' + new Date().toLocaleTimeString();
          rateDiv.style.display = 'block';
        } else {
          resultDiv.textContent = 'Currency code not found. Try USD, EUR, INR, GBP, etc.';
          resultDiv.style.color = '#E94560';
        }
      })
      .catch(function () {
        resultDiv.textContent = 'Conversion failed — check your connection';
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
    wrap.style.cssText = 'background:linear-gradient(135deg,#e3f2fd,#e8eaf6);border:1px solid #c5cae9;border-radius:16px;padding:20px 22px;margin:16px 0;';
    wrap.innerHTML = '<div style="font-weight:700;font-size:15px;color:#0f0f23;margin-bottom:12px;">🌤️ Weather in ' + dest + '</div>' +
      '<div id="ps-weather-content" style="text-align:center;color:#666;font-size:14px;">Loading weather data...</div>';

    // Insert after currency converter or countdown
    var resBody = document.getElementById('resBody');
    if (resBody && resBody.parentNode) {
      var currency = document.getElementById('ps-currency-wrap');
      var countdown = document.getElementById('ps-countdown-wrap');
      var insertAfter = currency || countdown;
      if (insertAfter) {
        insertAfter.parentNode.insertBefore(wrap, insertAfter.nextSibling);
      } else {
        resBody.parentNode.insertBefore(wrap, resBody);
      }
    }

    // Fetch weather via serverless function
    fetch('/api/weather?city=' + encodeURIComponent(dest))
      .then(function (resp) { return resp.json(); })
      .then(function (data) {
        if (data.success) {
          var w = data.weather;
          var iconUrl = 'https://openweathermap.org/img/wn/' + w.icon + '@2x.png';
          document.getElementById('ps-weather-content').innerHTML =
            '<div style="display:flex;align-items:center;justify-content:center;gap:20px;flex-wrap:wrap;">' +
            '<div><img src="' + iconUrl + '" alt="weather" style="width:80px;height:80px;"></div>' +
            '<div style="text-align:left;">' +
            '<div style="font-size:36px;font-weight:800;color:#0f0f23;">' + Math.round(w.temp) + '°C</div>' +
            '<div style="font-size:15px;color:#444;text-transform:capitalize;">' + w.description + '</div>' +
            '<div style="font-size:12px;color:#888;margin-top:4px;">Feels like ' + Math.round(w.feelsLike) + '°C</div>' +
            '</div>' +
            '<div style="text-align:left;font-size:13px;color:#555;line-height:1.8;">' +
            '💧 Humidity: ' + w.humidity + '%<br>' +
            '💨 Wind: ' + w.windSpeed + ' km/h<br>' +
            '🌡️ High/Low: ' + Math.round(w.tempMax) + '° / ' + Math.round(w.tempMin) + '°' +
            '</div></div>';
        } else {
          document.getElementById('ps-weather-content').innerHTML =
            '<div style="color:#E94560;">Could not load weather. <a href="https://weather.com/weather/today/l/' + encodeURIComponent(dest) + '" target="_blank" style="color:#00C9A7;">Check on Weather.com →</a></div>';
        }
      })
      .catch(function () {
        document.getElementById('ps-weather-content').innerHTML =
          '<div style="color:#E94560;">Weather unavailable. <a href="https://weather.com/weather/today/l/' + encodeURIComponent(dest) + '" target="_blank" style="color:#00C9A7;">Check on Weather.com →</a></div>';
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
        // Wait for plan to fully render + phase1 buttons
        setTimeout(function () {
          injectCountdown();
          injectCurrencyConverter();
          injectWeatherWidget();
          activateChecklist();
        }, 800);
      }
    }, 600);
  }

  // ── Init ──
  function init() {
    startWidgetPolling();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
