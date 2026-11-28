// Recent economy return fares to Japan for the budget calculator (/japan-budget), 28 Nov 2026.
// Uses Travelpayouts' flight price data (the lowest fares travellers found in recent flight searches, cached by the
// data service), not live booking prices. Key: Vercel env var TRAVELPAYOUTS_TOKEN (never in the repo).
// GET /api/flight-price?from=SIN&to=TYO  ->  { ok, lo, hi, n, checked }  (yen, return, per person)
// Only the listed cities are accepted, so the function cannot be used as an open proxy.
const ORIGINS = new Set(['SIN', 'KUL', 'BKK', 'HKG', 'BOM', 'DEL', 'BLR', 'SYD', 'LON', 'LAX', 'NYC']);
const DESTS = new Set(['TYO', 'OSA', 'SPK']);   // Tokyo (Narita and Haneda), Osaka (Kansai), Sapporo (New Chitose)
const API = 'https://api.travelpayouts.com';

async function prices(url, token, pick) {
  const r = await fetch(url, { headers: { 'X-Access-Token': token, 'Accept-Encoding': 'gzip, deflate' } });
  if (!r.ok) return [];
  const j = await r.json();
  return (j && j.success !== false && Array.isArray(j.data) ? j.data : []).map(pick).filter(p => Number.isFinite(p) && p > 0);
}

export default async function handler(req, res) {
  const from = String(req.query.from || '').toUpperCase(), to = String(req.query.to || '').toUpperCase();
  if (!ORIGINS.has(from) || !DESTS.has(to)) return res.status(400).json({ ok: false, reason: 'route' });
  const token = process.env.TRAVELPAYOUTS_TOKEN;
  if (!token) return res.status(503).json({ ok: false, reason: 'not set up' });
  try {
    const q = 'origin=' + from + '&destination=' + to + '&currency=jpy&one_way=false&sorting=price&limit=30';
    let p = await prices(API + '/aviasales/v3/prices_for_dates?' + q, token, x => +x.price);
    if (p.length < 3) p = p.concat(await prices(API + '/v2/prices/latest?' + q + '&period_type=year', token, x => +x.value));
    p.sort((a, b) => a - b);
    if (p.length < 3) return res.status(200).json({ ok: false, reason: 'few fares', n: p.length });
    const round = v => Math.round(v / 1000) * 1000;
    // the lowest fare found, and the middle of the fares found: a range most travellers can book in
    const lo = round(p[0]), hi = Math.max(round(p[Math.floor(p.length / 2)]), lo);
    res.setHeader('Cache-Control', 's-maxage=21600, stale-while-revalidate=86400');
    return res.status(200).json({ ok: true, lo, hi, n: p.length, checked: new Date().toISOString().slice(0, 10) });
  } catch (e) {
    return res.status(502).json({ ok: false, reason: 'source' });
  }
}
