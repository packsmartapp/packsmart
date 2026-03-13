export default async function handler(req, res) {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, GET, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') return res.status(200).end();

    if (req.method === 'POST') {
        const { email } = req.body || {};

        if (!email || !email.includes('@') || !email.includes('.')) {
            return res.status(400).json({ success: false, error: 'Please enter a valid email address.' });
        }

        const cleanEmail = email.trim().toLowerCase();
        const timestamp = new Date().toISOString();

        // Log to Vercel function logs (visible in Vercel Dashboard > Logs)
        console.log(`[NEW SUBSCRIBER] ${cleanEmail} at ${timestamp}`);

        return res.status(200).json({
            success: true,
            message: 'Thanks for subscribing!'
        });
    }

    if (req.method === 'GET') {
        return res.status(200).json({ success: true, message: 'Subscribe API is active.' });
    }

    return res.status(405).json({ success: false, error: 'Method not allowed' });
}
