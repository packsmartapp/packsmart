// =====================================================================
//  PackSmart Phase 1 — Save | Share | Calendar | Trip History
//  FIXED V2: Polling approach — works even when results section is hidden
// =====================================================================

(function () {
  'use strict';

  var STORAGE_KEY = 'ps_trips';

  // ── Grab form values helper ──
  function getTripInfo() {
    var dest = (document.getElementById('destination') || {}).value || '';
    var start = (document.getElementById('startDate') || {}).value || '';
    var end = (document.getElementById('endDate') || {}).value || '';
    var mode = (document.getElementById('travelMode') || {}).value || 'flight';
    var adults = (document.getElementById('adults') || {}).value || '2';
    var kids = (document.getElementById('kids') || {}).value || '0';
    var budget = (document.getElementById('budget') || {}).value || 'mid-range';
    var tripTypes = [];
    var checks = document.querySelectorAll('input[name="tripType"]:checked, input[type="checkbox"]:checked');
    for (var i = 0; i < checks.length; i++) {
      if (checks[i].value && checks[i].value !== 'on') tripTypes.push(checks[i].value);
    }
    return { destination: dest, startDate: start, endDate: end, travelMode: mode, adults: adults, kids: kids, budget: budget, tripType: tripTypes.join(', ') || 'General' };
  }

  // ── Toast notification ──
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
    setTimeout(function() { t.style.opacity = '0'; }, 2500);
  }

  // ── Save trip to localStorage ──
  function saveTrip() {
    var resBody = document.getElementById('resBody');
    if (!resBody || !resBody.innerHTML.trim()) { showToast('Generate a plan first!'); return; }
    var info = getTripInfo();
    if (!info.destination) { showToast('No destination found'); return; }
    var trips = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
    var trip = {
      id: Date.now().toString(36),
      destination: info.destination,
      startDate: info.startDate,
      endDate: info.endDate,
      travelMode: info.travelMode,
      adults: info.adults,
      kids: info.kids,
      budget: info.budget,
      tripType: info.tripType,
      planHtml: resBody.innerHTML,
      savedAt: new Date().toISOString()
    };
    trips.unshift(trip);
    if (trips.length > 25) trips.pop();
    localStorage.setItem(STORAGE_KEY, JSON.stringify(trips));
    showToast('Trip saved!');
    renderHistory();
  }

  // ── Calendar export (.ics) ──
  function exportCalendar() {
    var info = getTripInfo();
    if (!info.destination || !info.startDate) { showToast('Need destination & dates'); return; }
    var fmtDate = function(d) { return d.replace(/-/g, ''); };
    var start = fmtDate(info.startDate);
    var endDt = new Date(info.endDate || info.startDate);
    endDt.setDate(endDt.getDate() + 1);
    var endStr = endDt.toISOString().slice(0, 10).replace(/-/g, '');
    var ics = [
      'BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//PackSmart//EN',
      'BEGIN:VEVENT',
      'DTSTART;VALUE=DATE:' + start,
      'DTEND;VALUE=DATE:' + endStr,
      'SUMMARY:PackSmart Trip — ' + info.destination,
      'DESCRIPTION:Travel mode: ' + info.travelMode + '\\nAdults: ' + info.adults + '\\nBudget: ' + info.budget,
      'BEGIN:VALARM', 'TRIGGER:-P3D', 'ACTION:DISPLAY', 'DESCRIPTION:3 days until your trip to ' + info.destination + '!', 'END:VALARM',
      'BEGIN:VALARM', 'TRIGGER:-P1D', 'ACTION:DISPLAY', 'DESCRIPTION:Tomorrow you leave for ' + info.destination + '!', 'END:VALARM',
      'END:VEVENT', 'END:VCALENDAR'
    ].join('\r\n');
    var blob = new Blob([ics], { type: 'text/calendar' });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'PackSmart-' + info.destination.replace(/[^a-zA-Z0-9]/g, '-') + '.ics';
    a.click();
    showToast('Calendar file downloaded!');
  }

  // ── Share link ──
  function shareLink() {
    var resBody = document.getElementById('resBody');
    if (!resBody || !resBody.innerHTML.trim()) { showToast('Generate a plan first!'); return; }
    var info = getTripInfo();
    showToast('Creating share link...');
    fetch('/api/share-plan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ plan: resBody.innerHTML, tripInfo: info })
    }).then(function(resp) { return resp.json(); })
    .then(function(data) {
      if (data.shareUrl) {
        navigator.clipboard.writeText(data.shareUrl).then(function() {
          showToast('Link copied to clipboard!');
        });
      } else {
        showToast('Share failed — try again');
      }
    }).catch(function() {
      showToast('Share failed — try again');
    });
  }

  // ── Action buttons (injected above plan) ──
  function injectButtons() {
    var old = document.getElementById('ps-actions');
    if (old) old.remove();

    var resBody = document.getElementById('resBody');
    if (!resBody || !resBody.innerHTML.trim()) return;

    var bar = document.createElement('div');
    bar.id = 'ps-actions';
    bar.style.cssText = 'display:flex;gap:10px;flex-wrap:wrap;margin:18px 0 10px 0;justify-content:center;';

    var saveBtn = document.createElement('button');
    saveBtn.innerHTML = '<span style="font-size:18px;">&#x1F4BE;</span> Save Trip';
    saveBtn.style.cssText = 'background:#00C9A7;color:#fff;border:none;padding:10px 20px;border-radius:25px;cursor:pointer;font-weight:600;font-size:14px;display:flex;align-items:center;gap:6px;box-shadow:0 2px 10px rgba(0,201,167,.3);';
    saveBtn.addEventListener('click', saveTrip);

    var shareBtn = document.createElement('button');
    shareBtn.innerHTML = '<span style="font-size:18px;">&#x1F517;</span> Share Link';
    shareBtn.style.cssText = 'background:#E94560;color:#fff;border:none;padding:10px 20px;border-radius:25px;cursor:pointer;font-weight:600;font-size:14px;display:flex;align-items:center;gap:6px;box-shadow:0 2px 10px rgba(233,69,96,.3);';
    shareBtn.addEventListener('click', shareLink);

    var calBtn = document.createElement('button');
    calBtn.innerHTML = '<span style="font-size:18px;">&#x1F4C5;</span> Add to Calendar';
    calBtn.style.cssText = 'background:#1a1a2e;color:#fff;border:none;padding:10px 20px;border-radius:25px;cursor:pointer;font-weight:600;font-size:14px;display:flex;align-items:center;gap:6px;box-shadow:0 2px 10px rgba(0,0,0,.2);';
    calBtn.addEventListener('click', exportCalendar);

    bar.appendChild(saveBtn);
    bar.appendChild(shareBtn);
    bar.appendChild(calBtn);

    resBody.parentNode.insertBefore(bar, resBody);
  }

  // ── Trip History section ──
  function renderHistory() {
    var trips = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
    var section = document.getElementById('ps-history');

    if (trips.length === 0) {
      if (section) section.remove();
      return;
    }

    if (!section) {
      section = document.createElement('section');
      section.id = 'ps-history';
      section.style.cssText = 'max-width:900px;margin:40px auto;padding:0 20px;';
      var footer = document.querySelector('footer');
      if (footer) footer.parentNode.insertBefore(section, footer);
      else document.body.appendChild(section);
    }

    var modeIcons = { flight: '✈️', car: '🚗', bus: '🚌', train: '🚆', boat: '🚢' };
    var cardsHtml = '';
    for (var i = 0; i < trips.length; i++) {
      var t = trips[i];
      cardsHtml += '<div class="ps-trip-card" data-idx="' + i + '" style="background:#fff;border-radius:16px;padding:20px;cursor:pointer;box-shadow:0 2px 12px rgba(0,0,0,.08);border:2px solid transparent;transition:border-color .2s,transform .15s;">' +
        '<div style="display:flex;justify-content:space-between;align-items:start;">' +
        '<div><div style="font-size:20px;font-weight:700;color:#0f0f23;margin-bottom:4px;">' +
        (modeIcons[t.travelMode] || '✈️') + ' ' + t.destination + '</div>' +
        '<div style="font-size:13px;color:#666;">' + (t.startDate || '') + (t.endDate ? ' &rarr; ' + t.endDate : '') + '</div></div>' +
        '<button class="ps-delete-btn" data-delidx="' + i + '" style="background:none;border:none;cursor:pointer;font-size:18px;color:#ccc;padding:0;" title="Delete">&#10005;</button>' +
        '</div><div style="margin-top:8px;font-size:12px;color:#999;">Saved ' + new Date(t.savedAt).toLocaleDateString() + '</div></div>';
    }

    section.innerHTML = '<h2 style="font-size:28px;margin-bottom:20px;color:#0f0f23;"><span style="margin-right:8px;">&#x1F9F3;</span> My Trips</h2>' +
      '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:16px;">' + cardsHtml + '</div>';

    // Attach click handlers for trip cards
    var cards = section.querySelectorAll('.ps-trip-card');
    for (var j = 0; j < cards.length; j++) {
      cards[j].addEventListener('click', function () {
        var idx = parseInt(this.getAttribute('data-idx'));
        var savedTrips = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
        var trip = savedTrips[idx];
        if (!trip) return;
        var resBody = document.getElementById('resBody');
        var resultsSection = document.getElementById('results');
        if (resBody && resultsSection) {
          resBody.innerHTML = trip.planHtml;
          resultsSection.style.display = 'block';
          resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
          injectButtons();
          showToast('Loaded: ' + trip.destination);
        }
      });
    }

    // Attach delete handlers
    var delBtns = section.querySelectorAll('.ps-delete-btn');
    for (var k = 0; k < delBtns.length; k++) {
      delBtns[k].addEventListener('click', function (e) {
        e.stopPropagation();
        var idx = parseInt(this.getAttribute('data-delidx'));
        deleteTrip(idx);
      });
    }
  }

  // ── Delete a saved trip ──
  function deleteTrip(idx) {
    var trips = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
    if (idx >= 0 && idx < trips.length) {
      var name = trips[idx].destination;
      trips.splice(idx, 1);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(trips));
      showToast('Deleted: ' + name);
      renderHistory();
    }
  }

  // ── POLLING: Check every 500ms if #resBody has new content ──
  var _lastContent = '';

  function startPolling() {
    setInterval(function () {
      var resBody = document.getElementById('resBody');
      if (!resBody) return;
      var content = resBody.innerHTML.trim();
      if (content.length > 100 && content !== _lastContent) {
        _lastContent = content;
        // Wait for results section to become visible (line 1117 sets display:block)
        setTimeout(injectButtons, 600);
      }
    }, 500);
  }

  // ── Init on DOM ready ──
  function init() {
    renderHistory();
    startPolling();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
