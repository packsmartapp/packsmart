// Packy: "Email me this chat" (24 Nov 2026, D58).
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
    if (!process.env.EMAIL_USER || !process.env.EMAIL_PASSWORD) return res.status(500).json({ ok: false, error: 'Email is not set up yet.' });
    try {
      const t = nodemailer.createTransport({ host: 'smtp.hostinger.com', port: 465, secure: true, auth: { user: process.env.EMAIL_USER, pass: process.env.EMAIL_PASSWORD } });
      await t.sendMail({ from: '"Packy signups" <hello@packsmartapp.com>', to: 'hello@packsmartapp.com',
        subject: '[Packy signup] TRIP TIPS: YES | ' + COUNTRIES[country] + (trip2 ? ' | trip ' + trip2 : ''),
        text: 'Email: ' + email + '\nTrip tips (marketing consent): YES (tapped "Yes please" after the chat was emailed)\nTrip month: ' + (trip2 || 'not sure') +
          '\nCountry: ' + COUNTRIES[country] + '\nTime (UTC): ' + new Date().toISOString() + '\n\nImport to the email marketing service later.' });
      console.log(JSON.stringify({ ev: 'email_tips', country, trip: !!trip2, ok: true }));
      return res.status(200).json({ ok: true });
    } catch (e) {
      console.log(JSON.stringify({ ev: 'email_tips', country, ok: false }));
      return res.status(502).json({ ok: false, error: 'Sorry, that did not work. Please try again.' });
    }
  }
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
      ? '<b>&#128241; Save the free ' + POCKETS[pocket] + ' Pocket Guide</b><br>Exits, platforms, lockers and ATMs a tap away, and it works offline at the station.<br>' +
        '<a href="' + SITE + '/' + pocket + '-pocket?src=packy_email" style="display:inline-block;margin-top:10px;background:#0f0f23;color:#ffffff;text-decoration:none;font-weight:bold;border-radius:20px;padding:9px 16px;">Open the Pocket Guide</a>' +
        '<br><a href="' + SITE + '/japan?src=packy_email#pocket-hub" style="display:inline-block;margin-top:8px;color:#0a8f78;font-weight:bold;">All our Japan Pocket Guides</a></div>'
      : '<b>&#128241; Save the free Pocket Guides</b> for the airports and stations you will use: they work offline. ' +
        '<a href="' + SITE + '/japan?src=packy_email#pocket-hub" style="color:#0a8f78;font-weight:bold;">All our Japan Pocket Guides</a></div>') +
    '<p style="font-size:12px;color:#8a93a6;line-height:1.5;">You received this because you asked Packy to email this chat on packsmartapp.com.' +
    (tips ? ' You also asked for trip tips for ' + name + '; reply "stop" at any time and we will not email you again.' : ' We will not email you again unless you ask.') +
    ' <a href="' + SITE + '/privacy-policy" style="color:#8a93a6;">Privacy</a></p></div></body></html>';
  const text = 'Your Packy chat about ' + name + '\n\n' + items.map(x => 'Q: ' + x.q + '\n' + x.a + (x.o ? '\n' + x.o.label + (x.o.partner ? ' (partner link)' : '') + ': ' + (x.o.url.startsWith('/') ? SITE + x.o.url : x.o.url) : '') +
      (x.g ? '\nMore in our ' + x.g.title + ': ' + SITE + x.g.url : '')).join('\n\n') + (pocket ? '\n\nSave the free ' + POCKETS[pocket] + ' Pocket Guide: ' + SITE + '/' + pocket + '-pocket?src=packy_email' : '') +
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
