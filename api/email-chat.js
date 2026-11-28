// Packy: "Email me this chat" (24 Nov 2026, D58), and "Email me these words" from the lucky cat's word card on the Japan
// hub (kind: 'words', 26 Nov 2026): the same form, consent and guards; the words come from api/_japan_words.js, never
// from the request. And (28 Nov 2026) "Email it to me" on the Japan budget calculator (kind: 'budget'): the total, the
// trip, a link that reopens the exact budget and the booking links; only numbers and the calculator's own settings are
// accepted, and the partner links come from this file, never from the request.
// Sends the traveller their Packy conversation from hello@packsmartapp.com (the site's Hostinger mailbox, already used by
// subscribe.js; EMAIL_USER / EMAIL_PASSWORD in Vercel), and sends hello@packsmartapp.com a copy of the signup: the email,
// whether they ticked "trip tips" (marketing consent), their trip month and the page. That mailbox is the list until an
// email marketing service (MailerLite or Kit) is chosen and the signups are imported there.
// Guarded like /api/ask: only the site may call it, a few emails per visitor per hour, a daily cap, a non-empty chat only,
// and only Packy's own conversation goes out (so it cannot be used to send arbitrary mail). No email address is written
// to the logs.
import nodemailer from 'nodemailer';
import { deflateRawSync } from 'zlib';
import { knownOffer } from './_offers.js';
import PACKY_PNG from './_packy_png.js';
import { WORDS } from './_japan_words.js';

const ORIGIN_OK = /^https:\/\/(www\.)?packsmartapp\.com$|^https:\/\/packsmart-[a-z0-9-]+-packsmartapps-projects\.vercel\.app$|^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/;
const PER_IP = 5, WINDOW_MS = 60 * 60 * 1000, DAILY_CAP = 100;
const COUNTRIES = { japan: 'Japan' };
const hits = new Map();
let day = '', dayCount = 0;

function limited(ip) {
  const now = Date.now(), today = new Date().toISOString().slice(0, 10);
  if (today !== day) { day = today; dayCount = 0; }
  if (dayCount >= DAILY_CAP) return true;
  const list = (hits.get(ip) || []).filter(t => now - t < WINDOW_MS);
  if (list.length >= PER_IP) { hits.set(ip, list); return true; }
  list.push(now); hits.set(ip, list); dayCount++;
  return false;
}
const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const LIVE = 'https://www.packsmartapp.com';
// Links in the email go to the live site, except for an email sent from a Vercel preview of this project: those link back
// to that preview, so a change can be tested end to end (the "Continue" link, Pocket Guide, guides) before it goes live.
const PREVIEW = /^https:\/\/packsmart-[a-z0-9-]+-packsmartapps-projects\.vercel\.app$/;
function md(t, SITE) {   // the same small Markdown Packy uses: **bold**, [links](url), "- " lists
  let h = esc(t).replace(/\*\*([^*]+)\*\*/g, '<b>$1</b>').replace(/\[([^\]]+)\]\(((?:https?:\/\/|\/)[^\s)]+)\)/g, (m, x, u) =>
    '<a href="' + (u.startsWith('/') ? SITE + u : u) + '" style="color:#0a8f78;font-weight:bold;">' + x + '</a>');
  let out = '', list = false;
  for (const l of h.split(/\n+/)) {
    const m = l.match(/^\s*[-*•]\s+(.*)/);
    if (m) { if (!list) { out += '<ul style="margin:6px 0 6px 18px;padding:0;">'; list = true; } out += '<li style="margin:3px 0;">' + m[1] + '</li>'; }
    else { if (list) { out += '</ul>'; list = false; } if (l.trim()) out += '<p style="margin:6px 0;">' + l + '</p>'; }
  }
  return out + (list ? '</ul>' : '');
}
// Packy ends an answer with "Source: [title](url) | ...": shown small and last, under our guide link and the booking button
function srcSplit(a) { const m = String(a).match(/\n?[ \t]*\**Sources?:\**[ \t]*(.+)\s*$/i); return m ? [a.slice(0, m.index).trim(), m[1]] : [a, '']; }
// "Continue this chat with Packy": the chat travels in the link itself (after the #, so it never reaches a server and is
// not stored anywhere). packy.js reads #packy=..., restores the conversation and opens Packy. The oldest questions are
// dropped if the link would be very long, so it works in every mail app.
// The Pocket Guides Packy may point to (the same list as packy.js), and the guide links it may carry: site paths only.
const POCKETS = { sapporo: 'Sapporo Station', 'new-chitose': 'New Chitose Airport', ueno: 'Ueno Station', shinjuku: 'Shinjuku Station',
  tokyo: 'Tokyo Station', kyoto: 'Kyoto Station', osaka: 'Shin-Osaka and Umeda', narita: 'Narita Airport', haneda: 'Haneda Airport', kix: 'Kansai Airport' };
function guideOk(g) {
  if (!g || typeof g.url !== 'string' || !/^\/blog\/[a-z0-9-]+(#[a-z0-9-]+)?$/.test(g.url)) return null;
  const title = String(g.title || '').replace(/[^\w .,'&()-]/g, '').slice(0, 80).trim();
  return title ? { title, url: g.url } : null;
}
function continueLink(items, next, page, country, SITE) {
  const base = SITE + (/^\/[a-z0-9-]+(\/[a-z0-9-]+)*$/i.test(page) ? page : '/japan') + '?src=packy_email#packy=';
  let list = items.slice();
  while (list.length) {
    const data = deflateRawSync(Buffer.from(JSON.stringify({ v: 1, c: country, i: list.map(x => [x.q, x.a, x.o ? [x.o.label, x.o.url] : 0, x.g ? [x.g.title, x.g.url] : 0]), n: next }), 'utf8')).toString('base64url');
    if (data.length <= 8000 || list.length === 1) return base + data;
    list = list.slice(1);
  }
  return SITE + '/japan?src=packy_email';
}

export default async function handler(req, res) {
  const origin = req.headers.origin || '';
  if (ORIGIN_OK.test(origin)) { res.setHeader('Access-Control-Allow-Origin', origin); res.setHeader('Vary', 'Origin'); }
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  res.setHeader('Cache-Control', 'no-store');
  if (req.method === 'OPTIONS') return res.status(204).end();
  if (req.method !== 'POST') return res.status(405).json({ ok: false, error: 'Method not allowed' });
  if (!ORIGIN_OK.test(origin)) return res.status(403).json({ ok: false, error: 'Not allowed' });

  const b = req.body || {};
  const email = String(b.email || '').trim().toLowerCase();
  if (!/^[^\s@<>"]{1,64}@[^\s@<>"]{1,190}\.[a-z]{2,}$/i.test(email)) return res.status(400).json({ ok: false, error: 'Please check your email address.' });
  const country = COUNTRIES[String(b.country || 'japan').toLowerCase()] ? String(b.country || 'japan').toLowerCase() : null;
  if (!country) return res.status(400).json({ ok: false, error: 'Not available.' });
  // step 2 in the chat: the traveller said "yes" to trip tips (and maybe picked a trip month) after the chat was sent.
  // Only hello@ gets a note; nothing is sent to the traveller.
  if (b.update === true) {
    const trip2 = /^\d{4}-\d{2}$/.test(String(b.trip || '')) ? String(b.trip) : '';
    if (b.tips !== true) return res.status(400).json({ ok: false, error: 'Nothing to update.' });
    const ip2 = String(req.headers['x-forwarded-for'] || '').split(',')[0].trim() || 'unknown';
    if (limited(ip2)) return res.status(429).json({ ok: false, error: 'Too many requests for now. Please try again later.' });
    const door = b.from === 'words' ? 'fuku' : b.from === 'budget' ? 'budget' : 'packy';
    const known = TOPIC_TAGS.map(t => t[0]);
    const topics = door === 'fuku' ? ['words'] : door === 'budget' ? [...new Set((Array.isArray(b.topics) ? b.topics : []).map(String).filter(t => known.includes(t)))] : topicsOf(b.qs);
    // the trip-tips list itself: MailerLite (26 Nov, D58). Only this explicit "Yes please" adds anyone to it.
    const ml = await mlAdd({ email, country, door, trip: trip2, topics });
    // the hello@ note stays as a backup while MailerLite is new
    let noted = false;
    if (process.env.EMAIL_USER && process.env.EMAIL_PASSWORD) {
      try {
        const t = nodemailer.createTransport({ host: 'smtp.hostinger.com', port: 465, secure: true, auth: { user: process.env.EMAIL_USER, pass: process.env.EMAIL_PASSWORD } });
        await t.sendMail({ from: '"Packy signups" <hello@packsmartapp.com>', to: 'hello@packsmartapp.com',
          subject: '[Packy signup] TRIP TIPS: YES | ' + COUNTRIES[country] + (trip2 ? ' | trip ' + trip2 : '') + (b.from === 'words' ? ' | from the cat\'s word card' : b.from === 'budget' ? ' | from the budget calculator' : ''),
          text: 'Email: ' + email + '\nTrip tips (marketing consent): YES (tapped "Yes please" after the ' + (b.from === 'words' ? 'cat\'s words were' : 'chat was') + ' emailed)\nTrip month: ' + (trip2 || 'not sure') +
            '\nCountry: ' + COUNTRIES[country] + '\nTopics: ' + (topics.join(', ') || '-') + '\nMailerLite: ' + ml + '\nTime (UTC): ' + new Date().toISOString() +
            (ml === 'added' ? '' : '\n\nNot in MailerLite yet: add this subscriber by hand or ask Claude to import it.') });
        noted = true;
      } catch (e) { /* logged below */ }
    }
    console.log(JSON.stringify({ ev: 'email_tips', country, door, trip: !!trip2, topics: topics.length, ml, noted }));
    if (ml === 'added' || noted) return res.status(200).json({ ok: true });
    return res.status(502).json({ ok: false, error: 'Sorry, that did not work. Please try again.' });
  }
  if (b.kind === 'words') return sendWords(req, res, b, email, country, origin);
  if (b.kind === 'budget') return sendBudget(req, res, b, email, country, origin);
  const items = (Array.isArray(b.items) ? b.items : []).slice(-10)
    .map(x => ({ q: String((x && x.q) || '').slice(0, 300), a: String((x && x.a) || '').slice(0, 4000), o: knownOffer(x && x.offer), g: guideOk(x && x.guide) }))
    .filter(x => x.q && x.a);
  if (!items.length) return res.status(400).json({ ok: false, error: 'Ask Packy a question first.' });
  const tips = b.tips === true;
  const trip = /^\d{4}-\d{2}$/.test(String(b.trip || '')) ? String(b.trip) : '';
  const page = String(b.page || '').replace(/[^a-z0-9\-\/]/gi, '').slice(0, 80);
  const next = (Array.isArray(b.next) ? b.next : []).slice(0, 3).map(x => String(x || '').slice(0, 120)).filter(Boolean);
  const again = b.again === true;
  const pocket = POCKETS[String(b.pocket || '')] ? String(b.pocket) : '';   // the traveller sent an updated chat to the address Packy remembered

  const ip = String(req.headers['x-forwarded-for'] || '').split(',')[0].trim() || 'unknown';
  if (limited(ip)) return res.status(429).json({ ok: false, error: 'Too many emails for now. Please try again later.' });
  if (!process.env.EMAIL_USER || !process.env.EMAIL_PASSWORD) return res.status(500).json({ ok: false, error: 'Email is not set up yet.' });

  const name = COUNTRIES[country];
  const SITE = PREVIEW.test(origin) ? origin : LIVE;
  const chat = items.map(x =>
    '<div style="margin:0 0 18px;">' +
    '<p style="margin:0 0 6px;"><span style="display:inline-block;background:#00C9A7;color:#fff;border-radius:12px;padding:6px 12px;font-weight:bold;">' + esc(x.q) + '</span></p>' +
    '<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%"><tr><td width="36" valign="top" style="padding:4px 8px 0 0;"><img src="cid:packy" width="28" height="28" alt="Packy" style="display:block;border-radius:8px;"></td><td valign="top">' +
    '<div style="background:#ffffff;border:1px solid #e3e8ec;border-radius:12px;padding:10px 14px;color:#0f0f23;font-size:15px;line-height:1.55;">' + md(srcSplit(x.a)[0], SITE) +
    // the same booking button and guide link Packy showed in the chat
    (x.g ? '<p style="margin:10px 0 0;font-size:14px;border-top:1px dashed #D5DCE0;padding-top:8px;">&#128214; More in our <a href="' + SITE + esc(x.g.url) + '" style="color:#0a8f78;font-weight:bold;">' + esc(x.g.title) + '</a></p>' : '') +
    (x.o ? '<p style="margin:10px 0 4px;"><a href="' + esc(x.o.url.startsWith('/') ? SITE + x.o.url : x.o.url) + '"' + (x.o.partner ? ' rel="nofollow noopener sponsored"' : '') +
      ' style="display:block;background:#FFF1F4;border:1.5px solid #F7B9C6;border-radius:12px;padding:10px 12px;color:#0f0f23;text-decoration:none;font-weight:bold;">' +
      (x.o.partner ? '&#127903;&#65039; ' : '&#128073; ') + esc(x.o.label) + (x.o.partner ? ' <span style="font-weight:normal;font-size:12px;color:#8a5563;">(partner link)</span>' : '') + '</a></p>' : '') +
    (srcSplit(x.a)[1] ? '<p style="margin:8px 0 0;font-size:11px;color:#8a93a6;">Source: ' + md(srcSplit(x.a)[1], SITE).replace(/^<p[^>]*>|<\/p>$/g, '').replace(/font-weight:bold;/g, '') + '</p>' : '') +
    '</div></td></tr></table></div>').join('');
  const html = '<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>' +
    '<body style="margin:0;padding:0;background:#f4faf8;font-family:Arial,Helvetica,sans-serif;"><div style="max-width:600px;margin:0 auto;padding:28px 16px;">' +
    '<p style="font-size:22px;font-weight:800;color:#0f0f23;margin:0 0 4px;">Pack<span style="color:#00C9A7;">Smart</span></p>' +
    '<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin:14px 0 6px;"><tr><td valign="middle" style="padding-right:12px;"><img src="cid:packy" width="56" height="56" alt="Packy" style="display:block;border-radius:16px;box-shadow:0 2px 8px rgba(15,15,35,.12);"></td>' +
    '<td valign="middle"><h1 style="font-size:20px;color:#0f0f23;margin:0;">Your Packy chat about ' + name + '</h1><p style="margin:2px 0 0;color:#5a6378;font-size:13px;">From Packy, your ' + name + ' travel buddy</p></td></tr></table>' +
    '<p style="color:#5a6378;font-size:14px;margin:0 0 18px;">Here is what you asked Packy, with the official sources. Prices and times change, so check the source before you travel.</p>' +
    chat +
    '<p style="text-align:center;margin:22px 0;"><a href="' + esc(continueLink(items, next, page, country, SITE)) + '" style="display:inline-block;background:#E94560;color:#ffffff;text-decoration:none;font-weight:bold;font-size:16px;padding:13px 22px;border-radius:24px;">\uD83D\uDCAC Continue this chat with Packy</a></p>' +
    '<div style="background:#e6faf5;border-radius:12px;padding:14px 16px;margin:20px 0;font-size:14px;color:#0f0f23;">' +
    (pocket
      ? '<b>&#128241; Save the ' + POCKETS[pocket] + ' Pocket Guide</b><br>Exits, platforms, lockers and ATMs a tap away, and it works offline at the station.<br>' +
        '<a href="' + SITE + '/' + pocket + '-pocket?src=packy_email" style="display:inline-block;margin-top:10px;background:#0f0f23;color:#ffffff;text-decoration:none;font-weight:bold;border-radius:20px;padding:9px 16px;">Open the Pocket Guide</a>' +
        '<br><a href="' + SITE + '/japan?src=packy_email#pocket-hub" style="display:inline-block;margin-top:8px;color:#0a8f78;font-weight:bold;">All our Japan Pocket Guides</a></div>'
      : '<b>&#128241; Save the Pocket Guides</b> for the airports and stations you will use: no app to install, and they work offline. ' +
        '<a href="' + SITE + '/japan?src=packy_email#pocket-hub" style="color:#0a8f78;font-weight:bold;">All our Japan Pocket Guides</a></div>') +
    '<p style="font-size:12px;color:#8a93a6;line-height:1.5;">You received this because you asked Packy to email this chat on packsmartapp.com.' +
    (tips ? ' You also asked for trip tips for ' + name + '; reply "stop" at any time and we will not email you again.' : ' We will not email you again unless you ask.') +
    ' <a href="' + SITE + '/privacy-policy" style="color:#8a93a6;">Privacy</a></p></div></body></html>';
  const text = 'Your Packy chat about ' + name + '\n\n' + items.map(x => 'Q: ' + x.q + '\n' + x.a + (x.o ? '\n' + x.o.label + (x.o.partner ? ' (partner link)' : '') + ': ' + (x.o.url.startsWith('/') ? SITE + x.o.url : x.o.url) : '') +
      (x.g ? '\nMore in our ' + x.g.title + ': ' + SITE + x.g.url : '')).join('\n\n') + (pocket ? '\n\nSave the ' + POCKETS[pocket] + ' Pocket Guide: ' + SITE + '/' + pocket + '-pocket?src=packy_email' : '') +
    '\n\nPrices and times change, so check the source before you travel.\nContinue this chat with Packy: ' + continueLink(items, next, page, country, SITE);

  let step = 'connect';
  try {
    const t = nodemailer.createTransport({ host: 'smtp.hostinger.com', port: 465, secure: true, auth: { user: process.env.EMAIL_USER, pass: process.env.EMAIL_PASSWORD } });
    step = 'traveller';
    await t.sendMail({ from: '"Packy from PackSmart" <hello@packsmartapp.com>', replyTo: 'hello@packsmartapp.com', to: email, subject: (again ? 'Your updated Packy chat about ' : 'Your Packy chat about ') + name, html, text,
      attachments: [{ filename: 'packy.png', content: Buffer.from(PACKY_PNG, 'base64'), contentType: 'image/png', cid: 'packy', contentDisposition: 'inline' }] });
    step = 'copy';
    await t.sendMail({
      from: '"Packy signups" <hello@packsmartapp.com>', to: 'hello@packsmartapp.com',
      subject: '[Packy signup] ' + (tips ? 'TRIP TIPS: YES' : again ? 'updated chat re-sent' : 'chat only') + ' | ' + name + (trip ? ' | trip ' + trip : ''),
      text: 'Email: ' + email + '\nTrip tips (marketing consent): ' + (tips ? 'YES (ticked the box)' : 'no') + '\nTrip month: ' + (trip || 'not given') +
        '\nCountry: ' + name + '\nPage: ' + (page || '-') + '\nTime (UTC): ' + new Date().toISOString() + '\nQuestions asked: ' + items.length +
        '\n\nImport to the email marketing service later. Only "YES" signups may get trip tips.',
    });
    console.log(JSON.stringify({ ev: 'email_chat', country, tips, again, trip: !!trip, items: items.length, ok: true }));
    return res.status(200).json({ ok: true });
  } catch (e) {
    // the mail server's reason, without any email address, so a failed send can be fixed
    const why = String((e && (e.response || e.message)) || '').replace(/[\w.+-]+@[\w-]+\.[\w.]+/g, '[email]').slice(0, 200);
    console.log(JSON.stringify({ ev: 'email_chat', country, ok: false, step, code: e && e.code, smtp: e && e.responseCode, why }));
    return res.status(502).json({ ok: false, error: 'Sorry, the email could not be sent. Please try again later.' });
  }
}

// "Email me these words": the cat's 8 starter phrases, a link back to hear them, the Tokyo Pocket Guide for more, and Packy.
async function sendWords(req, res, b, email, country, origin) {
  const tips = b.tips === true;
  const ip = String(req.headers['x-forwarded-for'] || '').split(',')[0].trim() || 'unknown';
  if (limited(ip)) return res.status(429).json({ ok: false, error: 'Too many emails for now. Please try again later.' });
  if (!process.env.EMAIL_USER || !process.env.EMAIL_PASSWORD) return res.status(500).json({ ok: false, error: 'Email is not set up yet.' });
  const name = COUNTRIES[country];
  const SITE = PREVIEW.test(origin) ? origin : LIVE;
  const hear = SITE + '/japan?src=packy_email#words', ask = SITE + '/japan?src=packy_email#ask';
  const rows = WORDS.map(w =>
    '<tr><td width="40" valign="top" style="padding:10px 0 10px 12px;font-size:22px;">' + w[0] + '</td>' +
    '<td style="padding:10px 12px 10px 6px;"><div style="font-weight:bold;font-size:16px;color:#0f0f23;">' + esc(w[3]) + '</div>' +
    '<div lang="ja" style="font-size:15px;color:#0a8f78;font-weight:bold;margin-top:2px;">' + esc(w[2]) + '</div>' +
    '<div style="font-size:13px;color:#5a6378;margin-top:2px;">' + esc(w[1]) + '</div></td></tr>').join(
    '<tr><td colspan="2" style="border-top:1px solid #d9f0ea;font-size:0;line-height:0;">&nbsp;</td></tr>');
  const html = '<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>' +
    '<body style="margin:0;padding:0;background:#f4faf8;font-family:Arial,Helvetica,sans-serif;"><div style="max-width:600px;margin:0 auto;padding:28px 16px;">' +
    '<p style="font-size:22px;font-weight:800;color:#0f0f23;margin:0 0 4px;">Pack<span style="color:#00C9A7;">Smart</span></p>' +
    '<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin:14px 0 6px;"><tr><td valign="middle" style="padding-right:12px;"><img src="cid:packy" width="56" height="56" alt="Packy" style="display:block;border-radius:16px;"></td>' +
    '<td valign="middle"><h1 style="font-size:20px;color:#0f0f23;margin:0;">Your first Japanese words &#127471;&#127477;</h1><p style="margin:2px 0 0;color:#5a6378;font-size:13px;">From Packy, your ' + name + ' travel buddy</p></td></tr></table>' +
    '<p style="color:#5a6378;font-size:14px;margin:0 0 14px;">Eight words that go a long way. A smile and a small bow help too.</p>' +
    '<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background:#ffffff;border:1px solid #d9f0ea;border-radius:14px;">' + rows + '</table>' +
    '<p style="text-align:center;margin:22px 0 10px;"><a href="' + esc(hear) + '" style="display:inline-block;background:#E94560;color:#ffffff;text-decoration:none;font-weight:bold;font-size:16px;padding:13px 22px;border-radius:24px;">&#128266; Hear them again</a></p>' +
    '<div style="background:#e6faf5;border-radius:12px;padding:16px 12px 10px;margin:20px 0;font-size:14px;color:#0f0f23;">' +
    '<p style="margin:0 4px 4px;"><b>&#128241; 80+ more phrases in every Pocket Guide</b></p>' +
    '<p style="margin:0 4px 12px;color:#3f4a5c;">No app to install, and they work without a signal: phrases, plus exits, platforms, lockers and ATMs. Tap the airport or station you will use.</p>' +
    iconRow('Airports', POCKET_ICONS.slice(0, 4), SITE) + iconRow('Stations', POCKET_ICONS.slice(4), SITE) + '</div>' +
    '<div style="background:#ffffff;border:1px solid #e3e8ec;border-radius:12px;padding:14px 16px;margin:0 0 20px;font-size:14px;color:#0f0f23;">' +
    '<b>&#128172; Got a question about your trip?</b><br>Ask Packy about trains, airports, money and luggage in ' + name + '. Answers come from official sources.<br>' +
    '<a href="' + esc(ask) + '" style="display:inline-block;margin-top:8px;color:#0a8f78;font-weight:bold;">Ask Packy</a></div>' +
    '<p style="font-size:12px;color:#8a93a6;line-height:1.5;">You received this because you asked for these words on packsmartapp.com.' +
    (tips ? ' You also asked for trip tips for ' + name + '; reply "stop" at any time and we will not email you again.' : ' We will not email you again unless you ask.') +
    ' <a href="' + SITE + '/privacy-policy" style="color:#8a93a6;">Privacy</a></p></div></body></html>';
  const text = 'Your first Japanese words, from Packy\n\n' + WORDS.map(w => w[3] + '  ' + w[2] + '  (' + w[1] + ')').join('\n') +
    '\n\nHear them again: ' + hear + '\n\n80+ more phrases in every Pocket Guide (no app, works offline):\n' + POCKET_ICONS.map(g => g[1] + ': ' + SITE + '/' + g[0] + '-pocket?src=packy_email').join('\n') + '\n\nAsk Packy about your trip: ' + ask;
  let step = 'connect';
  try {
    const t = nodemailer.createTransport({ host: 'smtp.hostinger.com', port: 465, secure: true, auth: { user: process.env.EMAIL_USER, pass: process.env.EMAIL_PASSWORD } });
    step = 'traveller';
    await t.sendMail({ from: '"Packy from PackSmart" <hello@packsmartapp.com>', replyTo: 'hello@packsmartapp.com', to: email, subject: 'Your first Japanese words, from Packy', html, text,
      attachments: [{ filename: 'packy.png', content: Buffer.from(PACKY_PNG, 'base64'), contentType: 'image/png', cid: 'packy', contentDisposition: 'inline' }] });
    step = 'copy';
    await t.sendMail({
      from: '"Packy signups" <hello@packsmartapp.com>', to: 'hello@packsmartapp.com',
      subject: '[Packy signup] ' + (tips ? 'TRIP TIPS: YES' : 'words only') + ' | ' + name + ' | from the cat\'s word card',
      text: 'Email: ' + email + '\nTrip tips (marketing consent): ' + (tips ? 'YES (ticked the box)' : 'no') + '\nFrom: the lucky cat\'s word card on /japan ("Email me these words")' +
        '\nCountry: ' + name + '\nTime (UTC): ' + new Date().toISOString() + '\n\nImport to the email marketing service later. Only "YES" signups may get trip tips.',
    });
    console.log(JSON.stringify({ ev: 'email_words', country, tips, ok: true }));
    return res.status(200).json({ ok: true });
  } catch (e) {
    const why = String((e && (e.response || e.message)) || '').replace(/[\w.+-]+@[\w-]+\.[\w.]+/g, '[email]').slice(0, 200);
    console.log(JSON.stringify({ ev: 'email_words', country, ok: false, step, code: e && e.code, smtp: e && e.responseCode, why }));
    return res.status(502).json({ ok: false, error: 'Sorry, the email could not be sent. Please try again later.' });
  }
}

// "Email it to me" on the budget calculator: the estimate, the trip, a link back to the exact budget, the booking links.
// The calculator's settings come in as its own short query string (letters, numbers, = and &) and are checked here; the
// partner links are fixed below (the same Sub IDs as the page; w86 checks they match).
const BUDGET_LINKS = [
  ['flights', 'Flights', 'Search flights', 'https://aviasales.tpo.lu/E6VxsbuE'],
  ['jrpass', 'Japan Rail Pass', 'Check today\'s price and book', 'https://www.getyourguide.com/s/?q=japan%20rail%20pass&partner_id=D7IXONS&cmp=ps-budget-jrpass'],
  ['shinkansen', 'Shinkansen tickets', 'Book Shinkansen tickets online', 'https://www.japan-bullettrain.com/?via=packsmart'],
  ['subway', 'Tokyo Subway Ticket', 'Check today\'s price and book', 'https://www.getyourguide.com/s/?q=tokyo%20subway%20ticket&partner_id=D7IXONS&cmp=ps-budget-subway'],
  ['parks', 'Tokyo Disney tickets', 'Compare Tokyo Disney and theme park tickets', 'https://www.getyourguide.com/s/?q=tokyo%20disney%20tickets&partner_id=D7IXONS&cmp=ps-budget-disney'],
  ['sanrio', 'Sanrio Puroland tickets', 'Check today\'s price and book', 'https://www.getyourguide.com/s/?q=sanrio%20puroland&partner_id=D7IXONS&cmp=ps-budget-sanrio'],
  ['esim', 'eSIM data', 'See eSIM data plans for Japan', 'https://airalo.tpo.lu/u2N5qgJl'],
  ['insurance', 'Travel medical insurance', 'Get a travel medical insurance quote', 'https://www.safetywing.com/nomad-insurance?referenceID=26492686&utm_source=26492686&utm_medium=Ambassador'],
  ['transfer', 'Airport to town (a private car; trains are sold at the airport)', 'Book a private airport transfer', 'https://tpo.lu/hPV4u7AE']];
async function sendBudget(req, res, b, email, country, origin) {
  const q = String(b.q || '');
  if (!/^[a-z]{1,3}=[A-Za-z0-9_-]{1,12}(&[a-z]{1,3}=[A-Za-z0-9_-]{1,12}){0,45}$/.test(q)) return res.status(400).json({ ok: false, error: 'Please work out your budget first.' });
  const P = Object.fromEntries(q.split('&').map(x => x.split('=')));
  const n = k => Math.max(0, Math.min(40, parseInt(P[k], 10) || 0));
  const lo = Math.round(Number(b.lo)), hi = Math.round(Number(b.hi));
  if (!(lo > 0 && hi >= lo && hi < 1e8)) return res.status(400).json({ ok: false, error: 'Please work out your budget first.' });
  const ip = String(req.headers['x-forwarded-for'] || '').split(',')[0].trim() || 'unknown';
  if (limited(ip)) return res.status(429).json({ ok: false, error: 'Too many emails for now. Please try again later.' });
  if (!process.env.EMAIL_USER || !process.env.EMAIL_PASSWORD) return res.status(500).json({ ok: false, error: 'Email is not set up yet.' });
  const SITE = PREVIEW.test(origin) ? origin : LIVE;
  const open = SITE + '/japan-budget?' + q + '&src=budget_email';
  const yen = v => '¥' + v.toLocaleString('en-US');
  const total = yen(lo) + (hi > lo ? '–' + yen(hi).slice(1) : '');
  const ad = n('ad') + n('tn'), ch = n('ch'), inf = n('in'), ppl = ad + ch + inf;
  const areas = [['nt', 'Tokyo'], ['nk', 'Kyoto'], ['no', 'Osaka'], ['nh', 'Hokkaido']].filter(a => n(a[0])).map(a => n(a[0]) + ' in ' + a[1]);
  const nights = ['nt', 'nk', 'no', 'nh'].reduce((t, k) => t + n(k), 0);
  const who = [ad + ' adult' + (ad > 1 ? 's' : ''), ch ? ch + ' child' + (ch > 1 ? 'ren' : '') : '', inf ? inf + ' under 6' : ''].filter(Boolean).join(', ');
  const trip = who + ' · ' + nights + ' night' + (nights > 1 ? 's' : '') + (areas.length ? ' (' + areas.join(', ') + ')' : '');
  const kan = n('nk') + n('no'), jr = P.jr === '1';
  const want = ['flights'].concat(jr ? ['jrpass'] : [], n('nt') && kan && !jr ? ['shinkansen'] : [], n('nt') ? ['subway'] : [], n('dn') ? ['parks'] : [], P.sa === '1' ? ['sanrio'] : [], ['esim', 'insurance', 'transfer']);
  const rows = BUDGET_LINKS.filter(l => want.includes(l[0])).map(l =>
    '<tr><td style="padding:12px 14px;border-top:1px solid #e3e8ec;"><div style="font-weight:bold;color:#0f0f23;">&#9744; ' + esc(l[1]) + '</div>' +
    '<a href="' + esc(l[3]) + '" style="color:#0a8f78;font-weight:bold;font-size:14px;">' + esc(l[2]) + '</a></td></tr>').join('');
  const plain = ['Hotels: book early, with your usual booking site'];
  const tips = false;
  const html = '<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>' +
    '<body style="margin:0;padding:0;background:#f4faf8;font-family:Arial,Helvetica,sans-serif;"><div style="max-width:600px;margin:0 auto;padding:28px 16px;">' +
    '<p style="font-size:22px;font-weight:800;color:#0f0f23;margin:0 0 4px;">Pack<span style="color:#00C9A7;">Smart</span></p>' +
    '<h1 style="font-size:20px;color:#0f0f23;margin:14px 0 4px;">Your Japan trip budget &#127471;&#127477;</h1>' +
    '<p style="color:#5a6378;font-size:14px;margin:0 0 14px;">' + esc(trip) + '</p>' +
    '<div style="background:#0f0f23;border-radius:14px;padding:18px 16px;color:#ffffff;">' +
    '<div style="font-size:13px;color:#bfc6d6;">Your estimated budget</div><div style="font-size:28px;font-weight:bold;color:#00C9A7;margin:4px 0;">' + total + '</div>' +
    '<div style="font-size:13px;color:#bfc6d6;">About ' + yen(Math.round(lo / Math.max(1, ppl))) + ' per person, for the costs priced on the page. Prices from official pages where we have them, rounded.</div></div>' +
    '<p style="text-align:center;margin:22px 0 10px;"><a href="' + esc(open) + '" style="display:inline-block;background:#E94560;color:#ffffff;text-decoration:none;font-weight:bold;font-size:16px;padding:13px 22px;border-radius:24px;">Open your budget</a></p>' +
    '<p style="text-align:center;color:#5a6378;font-size:13px;margin:0 0 22px;">The full breakdown, and you can change anything. Fares and prices may have moved since.</p>' +
    '<h2 style="font-size:16px;color:#0f0f23;margin:0 0 8px;">To book</h2>' +
    '<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background:#ffffff;border:1px solid #d9f0ea;border-radius:14px;">' +
    plain.map(t => '<tr><td style="padding:12px 14px;border-top:1px solid #e3e8ec;color:#0f0f23;">&#9744; <b>' + esc(t.split(':')[0]) + '</b>:' + esc(t.slice(t.indexOf(':') + 1)) + '</td></tr>').join('') + rows + '</table>' +
    '<p style="font-size:12px;color:#8a93a6;line-height:1.5;margin-top:20px;">Partner links are marked; we may earn a commission at no cost to you. You received this because you asked for your budget on packsmartapp.com. We will not email you again unless you ask. ' +
    '<a href="' + SITE + '/privacy-policy" style="color:#8a93a6;">Privacy</a></p></div></body></html>';
  const text = 'Your Japan trip budget\n' + trip + '\n\nYour estimated budget: ' + total + '\n\nOpen your budget: ' + open + '\n\nTo book:\n' +
    plain.map(t => '- ' + t).join('\n') + '\n' + BUDGET_LINKS.filter(l => want.includes(l[0])).map(l => '- ' + l[1] + ': ' + l[3]).join('\n');
  let step = 'connect';
  try {
    const t = nodemailer.createTransport({ host: 'smtp.hostinger.com', port: 465, secure: true, auth: { user: process.env.EMAIL_USER, pass: process.env.EMAIL_PASSWORD } });
    step = 'traveller';
    await t.sendMail({ from: '"PackSmart" <hello@packsmartapp.com>', replyTo: 'hello@packsmartapp.com', to: email, subject: 'Your Japan trip budget: ' + total, html, text });
    step = 'copy';
    await t.sendMail({
      from: '"Packy signups" <hello@packsmartapp.com>', to: 'hello@packsmartapp.com',
      subject: '[Packy signup] budget only | Japan | from the budget calculator',
      text: 'Email: ' + email + '\nTrip tips (marketing consent): no (they can say yes after the email is sent)\nFrom: the budget calculator ("Email it to me")' +
        '\nTrip: ' + trip + '\nEstimate: ' + total + '\nTime (UTC): ' + new Date().toISOString() + '\n\nOnly "YES" signups may get trip tips.',
    });
    console.log(JSON.stringify({ ev: 'email_budget', country, tips, ok: true }));
    return res.status(200).json({ ok: true });
  } catch (e) {
    const why = String((e && (e.response || e.message)) || '').replace(/[\w.+-]+@[\w-]+\.[\w.]+/g, '[email]').slice(0, 200);
    console.log(JSON.stringify({ ev: 'email_budget', country, ok: false, step, code: e && e.code, smtp: e && e.responseCode, why }));
    return res.status(502).json({ ok: false, error: 'Sorry, the email could not be sent. Please try again later.' });
  }
}

// The Pocket Guides' own home-screen icons (the ones their web manifests use), airports first, then stations.
// [key, name, icon file, short label]
const POCKET_ICONS = [
  ['haneda', 'Haneda Airport', 'haneda-icon-v2-192.png', 'Haneda'], ['narita', 'Narita Airport', 'narita-icon-v2-192.png', 'Narita'],
  ['kix', 'Kansai Airport', 'kix-icon-192.png', 'Kansai'], ['new-chitose', 'New Chitose Airport', 'new-chitose-icon-192.png', 'New Chitose'],
  ['tokyo', 'Tokyo Station', 'tokyo-icon-192.png', 'Tokyo'], ['shinjuku', 'Shinjuku Station', 'shinjuku-icon-192.png', 'Shinjuku'],
  ['ueno', 'Ueno Station', 'ueno-icon-192.png', 'Ueno'], ['kyoto', 'Kyoto Station', 'kyoto-icon-192.png', 'Kyoto'],
  ['osaka', 'Shin-Osaka and Umeda', 'osaka-icon-192.png', 'Osaka'], ['sapporo', 'Sapporo Station', 'sapporo-icon-192.png', 'Sapporo']];
// one row of tappable icons in an email-safe table (images load from the site; the name shows if images are blocked)
function iconRow(title, list, SITE) {
  const w = Math.floor(100 / 6);
  return '<p style="margin:4px 4px 6px;font-size:11px;font-weight:bold;letter-spacing:1px;text-transform:uppercase;color:#5a6378;">' + title + '</p>' +
    '<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="margin:0 0 10px;"><tr>' +
    list.map(g => '<td width="' + w + '%" align="center" valign="top" style="padding:0 1px 6px;">' +
      '<a href="' + SITE + '/' + g[0] + '-pocket?src=packy_email" style="text-decoration:none;color:#0f0f23;">' +
      '<img src="' + SITE + '/images/' + g[2] + '" width="46" height="46" alt="' + esc(g[1]) + ' Pocket Guide" style="display:block;margin:0 auto;border-radius:12px;border:0;">' +
      '<span style="display:block;margin-top:5px;font-size:11px;font-weight:bold;color:#0f0f23;line-height:1.2;">' + esc(g[3]) + '</span></a></td>').join('') +
    (list.length < 6 ? '<td width="' + (100 - w * list.length) + '%">&nbsp;</td>' : '') + '</tr></table>';
}

// ---- MailerLite: the trip-tips list (26 Nov 2026). Group ids are not secret; the key is MAILERLITE_API_KEY (a Vercel Secret).
const ML = 'https://connect.mailerlite.com/api';
const ML_GROUPS = { japan: '205198435303818809' };   // "Japan · trip tips": joining it starts that country's sequence
// Packy's questions become a few topic tags here; the questions themselves are never stored or sent anywhere.
const TOPIC_TAGS = [
  ['shinkansen', /shinkansen|bullet train|nozomi|hikari/i], ['rail_pass', /jr pass|rail pass|japan rail pass/i],
  ['narita', /narita/i], ['haneda', /haneda/i], ['kansai', /kansai|\bkix\b/i], ['hokkaido', /new chitose|sapporo|hokkaido|niseko/i],
  ['tokyo', /tokyo|shinjuku|ueno|shibuya/i], ['kyoto', /kyoto/i], ['osaka', /osaka|umeda|namba/i],
  ['kids', /\bkids?\b|child|children|family|disney|stroller|baby/i], ['ic_card', /suica|pasmo|icoca|ic card/i],
  ['luggage', /luggage|locker|baggage|suitcase/i], ['connectivity', /esim|\bsim\b|wi-?fi|data plan/i], ['money', /\batm\b|cash|yen|money|card payment/i]];
function topicsOf(qs) {
  const text = (Array.isArray(qs) ? qs : []).slice(-10).map(q => String(q || '').slice(0, 300)).join(' \n ');
  return TOPIC_TAGS.filter(([, rx]) => rx.test(text)).map(([tag]) => tag);
}
async function mlAdd({ email, country, door, trip, topics }) {
  const key = process.env.MAILERLITE_API_KEY, group = ML_GROUPS[country];
  if (!key || !group) return 'off';
  const H = { Authorization: 'Bearer ' + key, 'Content-Type': 'application/json', Accept: 'application/json' };
  try {
    // one person, one record: keep their first door, merge topic tags, keep a known trip month when they pick "Not sure"
    let old = {};
    const g = await fetch(ML + '/subscribers/' + encodeURIComponent(email), { headers: H });
    if (g.ok) old = ((await g.json()).data || {}).fields || {};
    const tags = [...new Set(String(old.topics || '').split(',').map(x => x.trim()).filter(Boolean).concat(topics))].join(',');
    const fields = { destination: COUNTRIES[country], door: old.door || door, topics: tags || null };
    if (trip) fields.trip_month = trip + '-01';
    const r = await fetch(ML + '/subscribers', { method: 'POST', headers: H, body: JSON.stringify({ email, fields, groups: [group], resubscribe: true }) });
    return r.ok ? 'added' : 'failed ' + r.status;
  } catch (e) {
    return 'failed';
  }
}
