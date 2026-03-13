import { kv } from '@vercel/kv';

export default async function handler(req, res) {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, GET, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') return res.status(200).end();

    // POST — new subscriber
    if (req.method === 'POST') {
        const { email } = req.body || {};

        if (!email || !email.includes('@') || !email.includes('.')) {
            return res.status(400).json({ success: false, error: 'Please enter a valid email address.' });
        }

        const cleanEmail = email.trim().toLowerCase();
        const timestamp = new Date().toISOString();

        try {
            // Try Vercel KV if available
            if (typeof kv !== 'undefined' && kv.sadd) {
                await kv.sadd('packsmart:subscribers', cleanEmail);
                await kv.hset(`packsmart:sub:${cleanEmail}`, { email: cleanEmail, subscribedAt: timestamp });
            }
        } catch (e) {
            // KV not configured — fall through to JSON response
        }

        // Always log to Vercel function logs (visible in Vercel dashboard > Logs)
        console.log(`[NEW SUBSCRIBER] ${cleanEmail} at ${timestamp}`);

        return res.status(200).json({
            success: true,
            message: 'Thanks for subscribing! You\'ll receive our latest travel guides.'
        });
    }

    // GET — check subscriber count (for admin use)
    if (req.method === 'GET') {
        try {
            if (typeof kv !== 'undefined' && kv.scard) {
                const count = await kv.scard('packsmart:subscribers');
                return res.status(200).json({ success: true, count });
            }
        } catch (e) {
            // KV not available
        }
        return res.status(200).json({ success: true, message: 'Subscribe API is active. Set up Vercel KV for persistent storage.' });
    }

    return res.status(405).json({ success: false, error: 'Method not allowed' });
}
