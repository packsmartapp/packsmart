// =====================================================================
//  PackSmart Phase 1 — Save | Share | Calendar | Trip History
//  FIXED: Works with actual index.html (#resBody, mdToHtml)
// =====================================================================

(function () {
  'use strict';

  // ── Storage key ──
  const STORAGE_KEY = 'ps_trips';

  // ── Grab form values helper ──
  function getTripInfo() {
    const dest = (document.getElementById('destination') || {}).value || '';
    const start = (document.getElementById('startDate') || {}).value || '';
    const end = (document.getElementById('endDate') || {}).value || '';
    const mode = (document.getElementById('travelMode') || {}).value || 'flight';
    const adults = (document.getElementById('adults') || {}).value || '2';
    const kids = (document.getElementById('kids') || {}).value || '0';
    const budget = (document.getElementById('budget') || {}).value || 'mid-range';
    // Trip type checkboxes
    var tripTypes = [];
    document.querySelectorAll('input[name="tripType"]:checked, input[type="checkbox"]:checked').forEach(function(cb) {
      if (cb.value && cb.value !== 'on') tripTypes.push(cb.value);
    });
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

  // ── Action buttons (injected after plan renders) ──
  function injectButtons() {
    if (document.getElementById('ps-actions')) return;
    var resBody = document.getElementById('resBody');
    if (!resBody || !resBody.innerHTML.trim()) return;

    var bar = document.createElement('div');
    bar.id = 'ps-actions';
    bar.style.cssText = 'display:flex;gap:10px;flex-wrap:wrap;margin:18px 0 10px 0;';
    bar.innerHTML = '<button onclick="window._psSave()" style="background:#00C9A7;color:#fff;border:none;padding:10px 20px;border-radius:25px;cursor:pointer;font-weight:600;font-size:14px;display:flex;align-items:center;gap:6px;box-shadow:0 2px 10px rgba(0,201,167,.3);">' +
      '<span style="font-size:18px;">💾</span> Save Trip</button>' +
      '<button onclick="window._psShare()" style="background:#E94560;color:#fff;border:none;padding:10px 20px;border-radius:25px;cursor:pointer;font-weight:600;font-size:14px;display:flex;align-items:center;gap:6px;box-shadow:0 2px 10px rgba(233,69,96,.3);">' +
      '<span style="font-size:18px;">🔗</span> Share Link</button>' +
      '<button onclick="window._psCal()" style="background:#1a1a2e;color:#fff;border:none;padding:10px 20px;border-radius:25px;cursor:pointer;font-weight:600;font-size:14px;display:flex;align-items:center;gap:6px;box-shadow:0 2px 10px rgba(0,0,0,.2);">' +
      '<span style="font-size:18px;">📅</span> Add to Calendar</button>';

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
        '<div style="font-size:13px;color:#666;">' + (t.startDate || '') + (t.endDate ? ' → ' + t.endDate : '') + '</div></div>' +
        '<button onclick="event.stopPropagation();window._psDelete(' + i + ')" style="background:none;border:none;cursor:pointer;font-size:18px;color:#ccc;padding:0;" title="Delete">✕</button>' +
        '</div><div style="margin-top:8px;font-size:12px;color:#999;">Saved ' + new Date(t.savedAt).toLocaleDateString() + '</div></div>';
    }

    section.innerHTML = '<h2 style="font-size:28px;margin-bottom:20px;color:#0f0f23;"><span style="margin-right:8px;">🧳</span> My Trips</h2>' +
      '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:16px;">' + cardsHtml + '</div>';

    // Click to load saved plan
    var cards = section.querySelectorAll('.ps-trip-card');
    for (var j = 0; j < cards.length; j++) {
      cards[j].addEventListener('click', function () {
        var idx = parseInt(this.getAttribute('data-idx'));
        var trip = trips[idx];
        if (!trip) return;
        var resBody = document.getElementById('resBody');
        if (resBody) {
          resBody.innerHTML = trip.planHtml;
          var resultSection = resBody.closest('section') || resBody.parentElement;
          if (resultSection) resultSection.style.display = '';
          resBody.scrollIntoView({ behavior: 'smooth', block: 'start' });
          var old = document.getElementById('ps-actions');
          if (old) old.remove();
          injectButtons();
          showToast('Loaded: ' + trip.destination);
        }
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

  // ── Watch for plan generation (MutationObserver on #resBody) ──
  function watchForPlan() {
    var resBody = document.getElementById('resBody');
    if (!resBody) {
      setTimeout(watchForPlan, 500);
      return;
    }

    var observer = new MutationObserver(function () {
      if (resBody.innerHTML.trim().length > 100) {
        var old = document.getElementById('ps-actions');
        if (old) old.remove();
        setTimeout(injectButtons, 300);
      }
    });

    observer.observe(resBody, { childList: true, subtree: true, characterData: true });
  }

  // ── Expose functions globally ──
  window._psSave = saveTrip;
  window._psShare = shareLink;
  window._psCal = exportCalendar;
  window._psDelete = deleteTrip;

  // ── Init on DOM ready ──
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      renderHistory();
      watchForPlan();
    });
  } else {
    renderHistory();
    watchForPlan();
  }

})();
