import { createHash } from 'crypto';

// In-memory store. On Vercel serverless, this persists only within a single
// function instance. For a small free-tier app this is fine — links work for
// the lifetime of the warm instance (minutes to hours). For permanent links,
// upgrade to Vercel KV or Upstash Redis later.
const planStore = new Map();

export default async function handler(req, res) {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, GET, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') return res.status(200).end();

    // ---- GET: Retrieve a shared plan ----
    if (req.method === 'GET') {
        const { id } = req.query;
        if (!id) return res.status(400).json({ success: false, error: 'Missing plan ID' });

        const plan = planStore.get(id);
        if (!plan) {
            return res.status(404).json({
                success: false,
                error: 'Plan not found or expired. Shared plans are temporary — generate a new one at packsmartapp.com'
            });
        }
        return res.status(200).json({ success: true, ...plan });
    }

    // ---- POST: Save a plan and return share ID ----
    if (req.method === 'POST') {
        const { plan, tripInfo } = req.body;
        if (!plan) return res.status(400).json({ success: false, error: 'No plan data' });

        const id = createHash('md5')
            .update(plan + Date.now().toString())
            .digest('hex')
            .substring(0, 10);

        planStore.set(id, {
            plan,
            tripInfo: tripInfo || {},
            createdAt: new Date().toISOString()
        });

        // Cleanup: drop entries over 500 to prevent memory bloat
        if (planStore.size > 500) {
            const oldest = planStore.keys().next().value;
            planStore.delete(oldest);
        }

        return res.status(200).json({
            success: true,
            id,
            shareUrl: `https://packsmartapp.com/share.html?id=${id}`
        });
    }

    return res.status(405).json({ success: false, error: 'Method not allowed' });
}
