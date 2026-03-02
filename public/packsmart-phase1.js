// =====================================================================
//  PackSmart Phase 1 — Save | Share | Calendar | Trip History
//  Add to index.html:  <script src="packsmart-phase1.js"></script>
//  Place AFTER the marked.js script and BEFORE </body>
// =====================================================================

// ---- Global state ----
window._currentPlan = null;
window._currentTripInfo = null;

// ==========================
//  1. TRIP HISTORY (localStorage)
// ==========================
function psGetTrips() {
    try { return JSON.parse(localStorage.getItem('ps_trips') || '[]'); }
    catch { return []; }
}

function psSaveTrip(info, plan) {
    const trips = psGetTrips();
    const trip = {
        id: Date.now().toString(36) + Math.random().toString(36).substr(2, 5),
        destination: info.destination || 'Unknown',
        startDate: info.startDate || '',
        endDate: info.endDate || '',
        travelMode: info.travelMode || 'flight',
        adults: info.adults || 2,
        kids: info.kids || 0,
        tripType: info.tripType || '',
        budget: info.budget || '',
        currency: info.currency || 'USD',
        plan: plan,
        savedAt: new Date().toISOString()
    };
    trips.unshift(trip);
    if (trips.length > 25) trips.pop();
    localStorage.setItem('ps_trips', JSON.stringify(trips));
    return trip;
}

function psDeleteTrip(id) {
    const trips = psGetTrips().filter(t => t.id !== id);
    localStorage.setItem('ps_trips', JSON.stringify(trips));
    psRenderHistory();
}

function psLoadTrip(id) {
    const trip = psGetTrips().find(t => t.id === id);
    if (!trip) return;

    // Show plan in result area (same as after generation)
    const result = document.getElementById('result');
    const output = document.getElementById('plan-output');
    if (result && output) {
        output.innerHTML = marked.parse(trip.plan);
        result.style.display = 'block';

        window._currentPlan = trip.plan;
        window._currentTripInfo = trip;

        psShowActions();
        result.scrollIntoView({ behavior: 'smooth' });
    }
}

// ==========================
//  2. RENDER TRIP HISTORY UI
// ==========================
function psRenderHistory() {
    const el = document.getElementById('ps-history');
    if (!el) return;

    const trips = psGetTrips();
    if (!trips.length) { el.style.display = 'none'; return; }

    el.style.display = 'block';
    const icons = { flight:'✈️', car:'🚗', bus:'🚌', train:'🚆', boat:'🚢' };

    let html = '';
    trips.forEach(t => {
        const d = new Date(t.savedAt);
        const ds = d.toLocaleDateString('en-US', { month:'short', day:'numeric', year:'numeric' });
        html += `
        <div class="ps-hcard" onclick="psLoadTrip('${t.id}')">
            <span class="ps-hcard-icon">${icons[t.travelMode]||'✈️'}</span>
            <div class="ps-hcard-info">
                <div class="ps-hcard-dest">${t.destination}</div>
                <div class="ps-hcard-dates">${t.startDate}${t.startDate && t.endDate ? ' → ' : ''}${t.endDate}</div>
            </div>
            <div class="ps-hcard-right">
                <span class="ps-hcard-saved">${ds}</span>
                <button class="ps-hcard-del" onclick="event.stopPropagation();psDeleteTrip('${t.id}')" title="Delete">✕</button>
            </div>
        </div>`;
    });

    el.querySelector('.ps-hlist').innerHTML = html;
}

// ==========================
//  3. CALENDAR EXPORT (.ics)
// ==========================
function psCalendarExport(info) {
    if (!info.startDate) {
        psToast('Add travel dates first to export a calendar event.');
        return;
    }

    const dest = info.destination || 'Trip';
    const fmtDate = s => {
        const d = new Date(s);
        return isNaN(d.getTime()) ? s.replace(/-/g,'') : d.toISOString().split('T')[0].replace(/-/g,'');
    };
    const dtStart = fmtDate(info.startDate);
    // ICS DTEND is exclusive → add 1 day
    const endD = new Date(info.endDate || info.startDate);
    endD.setDate(endD.getDate() + 1);
    const dtEnd = endD.toISOString().split('T')[0].replace(/-/g,'');
    const now = new Date().toISOString().replace(/[-:]/g,'').split('.')[0] + 'Z';
    const uid = Date.now() + '@packsmartapp.com';

    const ics = [
        'BEGIN:VCALENDAR',
        'VERSION:2.0',
        'PRODID:-//PackSmart//Trip//EN',
        'CALSCALE:GREGORIAN',
        'METHOD:PUBLISH',
        'BEGIN:VEVENT',
        'UID:' + uid,
        'DTSTAMP:' + now,
        'DTSTART;VALUE=DATE:' + dtStart,
        'DTEND;VALUE=DATE:' + dtEnd,
        'SUMMARY:🧳 Trip to ' + dest + ' — PackSmart',
        'DESCRIPTION:Your PackSmart travel plan for ' + dest + '.\\nVisit packsmartapp.com to view the full plan.',
        'LOCATION:' + dest,
        'STATUS:CONFIRMED',
        // Reminder 3 days before
        'BEGIN:VALARM',
        'TRIGGER:-P3D',
        'ACTION:DISPLAY',
        'DESCRIPTION:3 days until your trip to ' + dest + '! Time to pack.',
        'END:VALARM',
        // Reminder 1 day before
        'BEGIN:VALARM',
        'TRIGGER:-P1D',
        'ACTION:DISPLAY',
        'DESCRIPTION:Tomorrow you leave for ' + dest + '! Final check.',
        'END:VALARM',
        'END:VEVENT',
        'END:VCALENDAR'
    ].join('\r\n');

    const blob = new Blob([ics], { type:'text/calendar;charset=utf-8' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'PackSmart-' + dest.replace(/[^a-zA-Z0-9]/g,'-') + '.ics';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(a.href);

    psToast('Calendar file downloaded! Open it to add to Google/Apple Calendar.');
}

// ==========================
//  4. SHARE LINK
// ==========================
async function psSharePlan(plan, info) {
    const btn = document.getElementById('ps-btn-share');
    if (btn) { btn.textContent = '⏳ Creating…'; btn.disabled = true; }

    try {
        const r = await fetch('/api/share-plan', {
            method: 'POST',
            headers: { 'Content-Type':'application/json' },
            body: JSON.stringify({ plan, tripInfo: info })
        });
        const d = await r.json();

        if (d.success && d.shareUrl) {
            await navigator.clipboard.writeText(d.shareUrl);
            if (btn) { btn.textContent = '✅ Link Copied!'; setTimeout(()=>{ btn.textContent='🔗 Share Link'; btn.disabled=false; }, 3000); }
            psToast('Share link copied to clipboard!');
        } else {
            throw new Error(d.error || 'Failed');
        }
    } catch(e) {
        if (btn) { btn.textContent = '🔗 Share Link'; btn.disabled = false; }
        // Fallback: share via WhatsApp with plan text
        psToast('Could not create link. Use WhatsApp share or Copy instead.');
    }
}

// ==========================
//  TOAST
// ==========================
function psToast(msg) {
    let t = document.getElementById('ps-toast');
    if (!t) {
        t = document.createElement('div');
        t.id = 'ps-toast';
        document.body.appendChild(t);
    }
    t.textContent = msg;
    t.className = 'ps-toast ps-toast-show';
    setTimeout(() => { t.className = 'ps-toast'; }, 3500);
}

// ==========================
//  READ CURRENT FORM VALUES
// ==========================
function psGetFormInfo() {
    // Try reading from the actual form inputs on the page
    const q = s => document.querySelector(s);
    const val = s => { const el = q(s); return el ? el.value : ''; };

    // Get selected trip types
    let tripTypes = [];
    document.querySelectorAll('input[name="tripType"]:checked, input[type="checkbox"][value]').forEach(cb => {
        if (cb.checked && ['Beach','Cultural','Adventure','Food','Nature','Nightlife','Business','Romantic','Family','Solo'].includes(cb.value)) {
            tripTypes.push(cb.value);
        }
    });

    return {
        destination: val('#destination, [name="destination"]') || window._currentTripInfo?.destination || '',
        startDate: val('#startDate, [name="startDate"]') || window._currentTripInfo?.startDate || '',
        endDate: val('#endDate, [name="endDate"]') || window._currentTripInfo?.endDate || '',
        travelMode: val('#travelMode, [name="travelMode"]') || window._currentTripInfo?.travelMode || 'flight',
        adults: parseInt(val('#adults, [name="adults"]')) || window._currentTripInfo?.adults || 2,
        kids: parseInt(val('#kids, [name="kids"]')) || window._currentTripInfo?.kids || 0,
        tripType: tripTypes.join(', ') || window._currentTripInfo?.tripType || '',
        budget: val('#budget, [name="budget"]') || window._currentTripInfo?.budget || '',
        currency: val('#currency, [name="currency"]') || window._currentTripInfo?.currency || 'USD'
    };
}

// ==========================
//  ACTION BUTTONS (injected after plan renders)
// ==========================
function psShowActions() {
    if (document.getElementById('ps-actions')) {
        document.getElementById('ps-actions').style.display = 'flex';
        return;
    }

    const result = document.getElementById('result');
    const output = document.getElementById('plan-output');
    if (!result || !output) return;

    const div = document.createElement('div');
    div.id = 'ps-actions';
    div.className = 'ps-actions';
    div.innerHTML = `
        <button class="ps-btn ps-btn-save" onclick="psHandleSave()">💾 Save Trip</button>
        <button class="ps-btn ps-btn-share-link" id="ps-btn-share" onclick="psHandleShare()">🔗 Share Link</button>
        <button class="ps-btn ps-btn-cal" onclick="psHandleCal()">📅 Add to Calendar</button>
    `;

    // Insert before plan-output (so buttons appear above the plan text, alongside existing Print/Copy/WhatsApp)
    output.parentNode.insertBefore(div, output);
}

// ---- Button handlers ----
function psHandleSave() {
    if (!window._currentPlan) { psToast('No plan to save.'); return; }
    psSaveTrip(psGetFormInfo(), window._currentPlan);

    const btn = document.querySelector('.ps-btn-save');
    if (btn) {
        btn.textContent = '✅ Saved!';
        btn.classList.add('ps-btn-done');
        setTimeout(() => { btn.textContent = '💾 Save Trip'; btn.classList.remove('ps-btn-done'); }, 2500);
    }
    psRenderHistory();
    psToast('Trip saved! Find it in "My Trips" below.');
}

function psHandleShare() {
    if (!window._currentPlan) { psToast('No plan to share.'); return; }
    psSharePlan(window._currentPlan, psGetFormInfo());
}

function psHandleCal() {
    const info = psGetFormInfo();
    if (!info.startDate) { psToast('Enter travel dates first.'); return; }
    psCalendarExport(info);
}

// ==========================
//  INTERCEPT FETCH TO CAPTURE PLAN
// ==========================
(function() {
    const _fetch = window.fetch;
    window.fetch = async function(...args) {
        const res = await _fetch.apply(this, args);
        const url = typeof args[0] === 'string' ? args[0] : args[0]?.url || '';

        if (url.includes('/api/generate-plan')) {
            const clone = res.clone();
            try {
                const d = await clone.json();
                if (d.success && d.plan) {
                    window._currentPlan = d.plan;
                    window._currentTripInfo = psGetFormInfo();
                    // Show action buttons once plan renders (small delay for marked.parse)
                    setTimeout(psShowActions, 300);
                }
            } catch(e) {}
        }
        return res;
    };
})();

// ==========================
//  INJECT STYLES + HISTORY SECTION
// ==========================
document.addEventListener('DOMContentLoaded', () => {

    // ---- Inject CSS ----
    const style = document.createElement('style');
    style.textContent = `
        /* Action buttons row */
        .ps-actions {
            display: flex; gap: .6rem; flex-wrap: wrap; justify-content: center;
            margin: 1rem 0 1.5rem; padding: 0;
        }
        .ps-btn {
            background: transparent; color: #00C9A7; border: 1px solid #00C9A7;
            padding: .6rem 1.1rem; border-radius: 8px; font-weight: 600;
            font-size: .85rem; cursor: pointer; display: inline-flex;
            align-items: center; gap: .35rem; transition: all .2s;
            font-family: inherit;
        }
        .ps-btn:hover { background: rgba(0,201,167,.1); }
        .ps-btn-save {
            background: linear-gradient(135deg,#00C9A7,#00a88a);
            color: #000; border: none;
        }
        .ps-btn-save:hover { background: linear-gradient(135deg,#00a88a,#008f72); }
        .ps-btn-done { background: #1a1a2e!important; color: #00C9A7!important; border: 1px solid #00C9A7!important; }

        /* Toast */
        .ps-toast {
            position: fixed; bottom: 2rem; left: 50%; transform: translateX(-50%);
            background: #00C9A7; color: #000; padding: .75rem 1.4rem; border-radius: 10px;
            font-weight: 600; font-size: .88rem; z-index: 9999; opacity: 0;
            transition: opacity .3s; pointer-events: none;
            box-shadow: 0 4px 20px rgba(0,201,167,.3);
        }
        .ps-toast-show { opacity: 1; }

        /* Trip history section */
        #ps-history {
            max-width: 700px; margin: 2rem auto; padding: 0 1.5rem;
        }
        .ps-htitle {
            text-align: center; font-size: 1.4rem; font-weight: 800;
            margin-bottom: .3rem; color: #fff;
        }
        .ps-htitle span { color: #00C9A7; }
        .ps-hsub {
            text-align: center; color: #8888aa; font-size: .85rem;
            margin-bottom: 1.2rem;
        }
        .ps-hcard {
            display: flex; align-items: center; gap: .9rem;
            background: #12122a; border: 1px solid #1e1e3a;
            border-radius: 12px; padding: .9rem 1.1rem;
            margin-bottom: .6rem; cursor: pointer; transition: all .2s;
        }
        .ps-hcard:hover { border-color: #00C9A7; background: #1a1a3e; transform: translateY(-1px); }
        .ps-hcard-icon { font-size: 1.4rem; flex-shrink: 0; }
        .ps-hcard-info { flex: 1; min-width: 0; }
        .ps-hcard-dest { font-weight: 700; color: #fff; font-size: .95rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .ps-hcard-dates { font-size: .78rem; color: #8888aa; margin-top: .1rem; }
        .ps-hcard-right { text-align: right; flex-shrink: 0; }
        .ps-hcard-saved { font-size: .73rem; color: #8888aa; display: block; }
        .ps-hcard-del {
            background: transparent; border: none; color: #E94560;
            font-size: 1.1rem; cursor: pointer; padding: .15rem .4rem;
            opacity: 0; transition: opacity .2s; line-height: 1;
        }
        .ps-hcard:hover .ps-hcard-del { opacity: 1; }

        @media(max-width:600px) {
            .ps-actions { gap: .5rem; }
            .ps-btn { font-size: .8rem; padding: .55rem .8rem; flex: 1 1 auto; justify-content: center; }
        }
    `;
    document.head.appendChild(style);

    // ---- Inject "My Trips" section before footer ----
    const section = document.createElement('section');
    section.id = 'ps-history';
    section.style.display = 'none';
    section.innerHTML = `
        <h2 class="ps-htitle"><span>My</span> Trips</h2>
        <p class="ps-hsub">Your saved plans — stored on this device</p>
        <div class="ps-hlist"></div>
    `;

    const footer = document.querySelector('footer');
    if (footer) footer.parentNode.insertBefore(section, footer);
    else document.body.appendChild(section);

    psRenderHistory();
});
