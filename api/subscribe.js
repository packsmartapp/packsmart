import nodemailer from 'nodemailer';

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

        // Log subscriber
        console.log(`[NEW SUBSCRIBER] ${cleanEmail} at ${timestamp}`);

        // Send welcome email
        try {
            const transporter = nodemailer.createTransport({
                host: 'smtp.hostinger.com',
                port: 465,
                secure: true,
                auth: {
                    user: process.env.EMAIL_USER,     // hello@packsmartapp.com
                    pass: process.env.EMAIL_PASSWORD   // Hostinger email password
                }
            });

            // Welcome email to subscriber
            await transporter.sendMail({
                from: '"PackSmart" <hello@packsmartapp.com>',
                to: cleanEmail,
                subject: 'Welcome to PackSmart! 🧳 Your Travel Guides Await',
                html: `
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#f8f9fa;font-family:Arial,Helvetica,sans-serif;">
<div style="max-width:560px;margin:0 auto;padding:40px 20px;">

<div style="text-align:center;margin-bottom:30px;">
    <span style="font-size:24px;font-weight:800;color:#212529;">Pack<span style="color:#00C9A7;">Smart</span></span>
</div>

<div style="background:#ffffff;border-radius:16px;padding:40px 30px;border:1px solid #e9ecef;">
    <h1 style="font-size:22px;color:#212529;margin:0 0 16px;text-align:center;">Welcome aboard! ✈️</h1>
    <p style="font-size:15px;color:#555;line-height:1.7;margin:0 0 20px;">
        Thanks for subscribing to PackSmart. You'll receive our latest travel guides, packing checklists, and destination tips — everything you need to travel smarter.
    </p>

    <div style="background:#f0faf7;border-radius:12px;padding:20px;margin:20px 0;">
        <p style="font-size:14px;color:#212529;font-weight:600;margin:0 0 12px;">Popular guides to get you started:</p>
        <p style="margin:6px 0;font-size:14px;"><a href="https://www.packsmartapp.com/blog/summer-vacation-packing-list.html" style="color:#00C9A7;text-decoration:none;">☀️ Summer Vacation Packing List 2026</a></p>
        <p style="margin:6px 0;font-size:14px;"><a href="https://www.packsmartapp.com/blog/bali-travel-packing-guide-from-india.html" style="color:#00C9A7;text-decoration:none;">🏝️ Bali Travel & Packing Guide</a></p>
        <p style="margin:6px 0;font-size:14px;"><a href="https://www.packsmartapp.com/blog/europe-travel-packing-list.html" style="color:#00C9A7;text-decoration:none;">🇪🇺 Europe Travel Packing List</a></p>
        <p style="margin:6px 0;font-size:14px;"><a href="https://www.packsmartapp.com/blog/minimalist-packing-guide.html" style="color:#00C9A7;text-decoration:none;">🎒 Minimalist Packing Guide</a></p>
    </div>

    <div style="text-align:center;margin:25px 0 10px;">
        <a href="https://www.packsmartapp.com/#plan" style="display:inline-block;background:#00C9A7;color:#ffffff;padding:14px 32px;border-radius:30px;text-decoration:none;font-weight:600;font-size:15px;">Plan Your Next Trip →</a>
    </div>
</div>

<div style="text-align:center;margin-top:30px;">
    <p style="font-size:12px;color:#999;">
        <a href="https://www.packsmartapp.com/blog.html" style="color:#00C9A7;text-decoration:none;">Browse All Guides</a> &nbsp;•&nbsp;
        <a href="https://www.packsmartapp.com/about.html" style="color:#00C9A7;text-decoration:none;">About</a> &nbsp;•&nbsp;
        <a href="https://www.packsmartapp.com/contact.html" style="color:#00C9A7;text-decoration:none;">Contact</a>
    </p>
    <p style="font-size:11px;color:#bbb;margin-top:8px;">© 2026 PackSmart • AI-Powered Travel Preparation</p>
</div>

</div>
</body>
</html>
                `
            });

            // Notification to admin
            await transporter.sendMail({
                from: '"PackSmart Notifications" <hello@packsmartapp.com>',
                to: 'hello@packsmartapp.com',
                subject: `New Subscriber: ${cleanEmail}`,
                text: `New newsletter subscriber!\n\nEmail: ${cleanEmail}\nDate: ${timestamp}\n\n— PackSmart`
            });

        } catch (emailError) {
            console.log(`[EMAIL ERROR] ${emailError.message}`);
            // Still return success — subscription is logged even if email fails
        }

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
