# PackSmart Blog Article Style Guide

**Benchmark article:** `portugal-travel-packing-guide.html`
**Last updated:** March 24, 2026

Every new blog article MUST follow this guide exactly. When in doubt, copy from Portugal.

---

## Brand

| Token | Value |
|---|---|
| Primary (teal) | `#00C9A7` |
| Accent (coral) | `#E94560` |
| Dark navy | `#0f0f23` |
| Text | `#333` |
| Light gray | `#f5f5f5` |
| Font | `DM Sans` 400 / 500 / 700 |
| GA4 ID | `G-0C4Z7VVGPE` |
| TP marker | `711400` |
| TP trs | `508747` |

---

## Article Section Order

1. `<head>` — meta, OG, Twitter, Pinterest, fonts, GA4, Travelpayouts, structured data
2. `<style>` — all CSS (see CSS Reference below)
3. Nav
4. Hero
5. `<div class="content">`
6. Affiliate disclosure
7. Share row (top)
8. Article body (h2 sections)
9. CTA box ("Ready to Pack for [Country]?")
10. `</div>` close content
11. SafetyWing insurance widget
12. Car rental section (Localrent OR DiscoverCars)
13. Related Packing Guides
14. Newsletter CTA
15. Share row (bottom)
16. FAQ section (details/summary)
17. Footer
18. Nav scroll + mobile menu script

---

## Head Section

```html
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>[Country] Travel & Packing Guide 2026: Complete Checklist | PackSmart Blog</title>
<meta name="description" content="...">
<meta name="keywords" content="...">
<link rel="canonical" href="https://www.packsmartapp.com/blog/[slug].html">

<!-- Open Graph -->
<meta property="og:title" content="...">
<meta property="og:description" content="...">
<meta property="og:url" content="https://www.packsmartapp.com/blog/[slug].html">
<meta property="og:type" content="article">
<meta property="og:site_name" content="PackSmart">
<meta property="og:image" content="https://www.packsmartapp.com/og-default.png">

<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="...">
<meta name="twitter:description" content="...">
<meta name="twitter:image" content="https://www.packsmartapp.com/og-default.png">

<!-- Pinterest Rich Pins -->
<meta property="article:author" content="PackSmart">
<meta property="article:section" content="Travel">

<!-- Fonts -->
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">

<!-- GA4 -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-0C4Z7VVGPE"></script>
<script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-0C4Z7VVGPE');
</script>

<!-- Travelpayouts -->
<script data-noptimize="1" data-cfasync="false" data-wpfc-render="false">
  (function () {
      var script = document.createElement("script");
      script.async = 1;
      script.src = 'https://emrld.ltd/NTA4NzQ3.js?t=508747';
      document.head.appendChild(script);
  })();
</script>
<script async src="https://emrld.ltd/NTA4NzQ3.js?t=508747"></script>

<!-- Structured Data: Article, BreadcrumbList, FAQPage -->
<!-- (see Portugal for format) -->
```

---

## CSS Reference

```css
:root {
    --primary: #00C9A7;
    --accent: #E94560;
    --dark: #0f0f23;
    --light-gray: #f5f5f5;
    --text: #333;
}
```

### Nav
```css
.nav { position: fixed; top: 0; left: 0; right: 0; z-index: 100; padding: 0 3rem; height: 72px; display: flex; align-items: center; justify-content: space-between; background: transparent; transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1); }
.nav.scrolled { background: rgba(253,240,242,0.88); backdrop-filter: blur(20px) saturate(180%); -webkit-backdrop-filter: blur(20px) saturate(180%); border-bottom: 1px solid #eee; }
.nav-brand { font-family: 'DM Sans', sans-serif; font-weight: 800; font-size: 1.2rem; color: #333; text-decoration: none; letter-spacing: -0.3px; }
.nav-brand em { font-style: normal; color: #00C9A7; }
.nav-links { display: flex; align-items: center; gap: 2.5rem; }
.nav-links a { font-size: 0.875rem; font-weight: 500; color: #666; text-decoration: none; transition: color 0.2s; position: relative; }
.nav-links a:hover { color: #00C9A7; }
.nav-links a::after { content: ''; position: absolute; bottom: -4px; left: 0; right: 0; height: 1.5px; background: #00C9A7; transform: scaleX(0); transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1); }
.nav-links a:hover::after { transform: scaleX(1); }
.nav-cta-btn { font-size: 0.85rem !important; font-weight: 600 !important; color: #fff !important; background: #00C9A7; padding: 9px 22px; border-radius: 50px; transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important; }
.nav-cta-btn::after { display: none !important; }
.nav-cta-btn:hover { background: #00b396 !important; transform: translateY(-1px); }
.mobile-menu-btn { display: none; background: none; border: none; cursor: pointer; width: 32px; height: 32px; position: relative; }
.mobile-menu-btn span { position: absolute; left: 4px; width: 24px; height: 1.5px; background: #333; border-radius: 2px; transition: 0.3s; }
.mobile-menu-btn span:nth-child(1) { top: 10px; }
.mobile-menu-btn span:nth-child(2) { top: 16px; }
.mobile-menu-btn span:nth-child(3) { top: 22px; }
```

### Hero
```css
.hero-blog { background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 100%); background-size: cover; background-position: center; color: white; padding: 140px 2rem; text-align: center; margin-top: 72px; }
.hero-blog h1 { font-size: 2.5rem; margin-bottom: 1rem; line-height: 1.2; }
.hero-blog .meta { font-size: 0.9rem; opacity: 0.95; margin-bottom: 0.5rem; }
```

### Content
```css
.content { max-width: 800px; margin: 0 auto; padding: 3rem 2rem; }
.content h2 { color: var(--dark); font-size: 1.8rem; margin-top: 2.5rem; margin-bottom: 1rem; border-left: 4px solid var(--primary); padding-left: 1rem; }
.content h3 { color: var(--dark); font-size: 1.2rem; margin-top: 1.5rem; margin-bottom: 0.7rem; }
.content p { margin-bottom: 1rem; font-size: 1rem; }
.content ul { margin-left: 1.5rem; margin-bottom: 1.5rem; }
.content li { margin-bottom: 0.6rem; }
```

### Boxes
```css
.tip-box { background: #f0fef9; border-left: 4px solid var(--primary); padding: 1.5rem; margin: 1.5rem 0; border-radius: 4px; }
.tip-box strong { color: var(--primary); }
.warning-box { background: #fff5f5; border-left: 4px solid var(--accent); padding: 1.5rem; margin: 1.5rem 0; border-radius: 4px; }
.warning-box strong { color: var(--accent); }
```

### Tables
```css
.checklist-table { width: 100%; border-collapse: collapse; margin: 1.5rem 0; background: white; border: 1px solid #ddd; }
.checklist-table th { background: var(--primary); color: white; padding: 1rem; text-align: left; font-weight: 600; }
.checklist-table td { padding: 0.8rem 1rem; border-bottom: 1px solid #eee; }
.checklist-table tr:hover { background: var(--light-gray); }
```

### Weather Cards
```css
.weather-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; margin: 1.5rem 0; }
.weather-card { background: var(--light-gray); padding: 1.5rem; border-radius: 8px; border-top: 3px solid var(--primary); }
.weather-card h4 { color: var(--primary); margin-bottom: 0.5rem; }
```

### CTA Box
```css
.cta-box { background: linear-gradient(135deg, var(--primary) 0%, #00a080 100%); color: white; padding: 2rem; border-radius: 8px; text-align: center; margin: 3rem 0; }
.cta-box h3 { color: white; margin-bottom: 1rem; }
.cta-box a { background: var(--accent); color: white; padding: 0.8rem 2rem; text-decoration: none; border-radius: 4px; display: inline-block; font-weight: 600; transition: opacity 0.3s; }
.cta-box a:hover { opacity: 0.9; }
```

### Share Row
```css
.share-row { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; padding: 12px 0; }
.share-row span { font-size: 0.85rem; color: #999; font-weight: 500; }
.share-btn { display: inline-flex; align-items: center; justify-content: center; width: 38px; height: 38px; border-radius: 8px; border: 1px solid #E9ECEF; background: #fff; text-decoration: none; color: #555; transition: all 0.2s; }
.share-btn:hover { border-color: #ccc; color: #333; background: #f8f9fa; }
.share-btn.copy-link { width: auto; padding: 0 12px; gap: 4px; font-size: 0.8rem; font-weight: 500; cursor: pointer; font-family: inherit; }
```

### Related Guides
```css
.related-posts { max-width: 800px; margin: 3rem auto; padding: 0 2rem; }
.related-posts h3 { color: var(--dark); font-size: 1.5rem; margin-bottom: 2rem; text-align: center; }
.related-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 2rem; }
.related-card { background: white; border: 1px solid #ddd; border-radius: 8px; overflow: hidden; transition: box-shadow 0.3s; }
.related-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
.related-card-body { padding: 1.5rem; }
.related-card h4 { color: var(--dark); margin-bottom: 0.5rem; font-size: 1.1rem; }
.related-card a { color: var(--primary); text-decoration: none; font-weight: 600; }
.related-card a:hover { text-decoration: underline; }
.related-tag { display: inline-block; background: var(--light-gray); color: var(--dark); padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.8rem; margin-top: 1rem; }
.related-arrow { color: var(--accent); margin-left: 0.5rem; }
```

### Footer
```css
.footer { padding: 60px 2rem 40px; background: rgba(248,249,250,0.75); border-top: 1px solid #eee; }
.footer-inner { max-width: 1100px; margin: 0 auto; display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 3rem; }
.footer-brand-col .footer-logo { font-weight: 800; font-size: 1.15rem; color: #333; margin-bottom: 0.8rem; }
.footer-brand-col .footer-logo em { font-style: normal; color: #00C9A7; }
.footer-brand-col p { font-size: 0.85rem; color: #666; line-height: 1.6; max-width: 280px; }
.footer-col h4 { font-size: 0.78rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; color: #666; margin-bottom: 1.2rem; }
.footer-col a { display: block; font-size: 0.88rem; color: #999; text-decoration: none; margin-bottom: 0.7rem; transition: color 0.2s; }
.footer-col a:hover { color: #00C9A7; }
.footer-bottom { max-width: 1100px; margin: 3rem auto 0; padding-top: 1.5rem; border-top: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; }
.footer-bottom span { font-size: 0.8rem; color: #999; }
```

### Responsive
```css
@media (max-width: 768px) {
    .hero-blog h1 { font-size: 1.8rem; }
    .content { padding: 2rem 1rem; }
    .content h2 { font-size: 1.5rem; }
    .nav { padding: 1rem; }
    .footer-inner { grid-template-columns: 1fr 1fr; gap: 2rem; }
    .footer-bottom { flex-direction: column; gap: 0.5rem; text-align: center; }
}
@media (max-width: 600px) {
    .nav { padding: 0 1.5rem; }
    .nav-links { display: none; }
    .nav-links.open { display: flex; flex-direction: column; position: fixed; top: 72px; left: 0; right: 0; background: rgba(255,255,255,0.98); backdrop-filter: blur(20px); padding: 2rem; gap: 1.5rem; box-shadow: 0 10px 40px rgba(0,0,0,0.08); }
    .mobile-menu-btn { display: block; }
}
```

---

## HTML Components

### Nav
```html
<nav class="nav" id="nav">
    <a href="/" class="nav-brand">Pack<em>Smart</em></a>
    <div class="nav-links" id="navLinks">
        <a href="/flights.html">Flights & Hotels</a>
        <a href="/#how">How It Works</a>
        <a href="/#features">Features</a>
        <a href="/blog.html">Blog</a>
        <a href="/#plan" class="nav-cta-btn">Plan My Trip</a>
    </div>
    <button class="mobile-menu-btn" id="menuBtn" aria-label="Menu"><span></span><span></span><span></span></button>
</nav>
```

### Hero (background image via inline style)
```html
<div class="hero-blog" style="background: linear-gradient(rgba(15,15,35,0.7), rgba(26,26,62,0.7)), url('[UNSPLASH_URL]?w=1200&h=600&fit=crop&auto=format&q=75'); background-size: cover; background-position: center;">
    <h1>[Country] Travel & Packing Guide 2026: Complete Checklist</h1>
    <div class="meta">[Date] · [X] min read</div>
    <div class="meta">Destination Guide</div>
    <div class="meta">Last updated: March 2026</div>
</div>
```

### Affiliate Disclosure (first thing inside content div)
```html
<p style="font-size:0.82rem;color:#999;margin-bottom:0.5rem;padding-bottom:0.8rem;border-bottom:1px solid #eee;">This article contains affiliate links. If you make a purchase through these links, we may earn a small commission at no extra cost to you. <a href="/affiliate-disclosure.html" style="color:#00C9A7;">Learn more</a></p>
```

### Share Row (icon-based, used top and bottom)
```html
<div class="share-row">
    <span>Share this guide ✨</span>
    <a class="share-btn whatsapp" href="https://wa.me/?text=[ENCODED_TITLE]%20[ENCODED_URL]" target="_blank" rel="noopener" title="WhatsApp"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg></a>
    <a class="share-btn twitter" href="https://twitter.com/intent/tweet?text=[ENCODED_TITLE]&url=[ENCODED_URL]" target="_blank" rel="noopener" title="X"><svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg></a>
    <a class="share-btn facebook" href="https://www.facebook.com/sharer/sharer.php?u=[ENCODED_URL]" target="_blank" rel="noopener" title="Facebook"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/></svg></a>
    <a class="share-btn linkedin" href="https://www.linkedin.com/sharing/share-offsite/?url=[ENCODED_URL]" target="_blank" rel="noopener" title="LinkedIn"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"/><rect x="2" y="9" width="4" height="12"/><circle cx="4" cy="4" r="2"/></svg></a>
    <button class="share-btn copy-link" onclick="navigator.clipboard.writeText('[FULL_URL]').then(()=>this.textContent='Copied!')" title="Copy Link"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg> Link</button>
</div>
```

### SafetyWing Insurance Widget (center-aligned, placed after closing content div)
```html
<!-- SAFETYWING INSURANCE WIDGET -->
<div style="background:linear-gradient(135deg,#F0FAF7 0%,#E8F8F5 100%);border-radius:16px;padding:24px;margin:30px 0;text-align:center;border:1px solid #C8E6DC;">
    <h3 style="font-size:1.2rem;margin:0 0 6px;color:#212529;">🛡️ Get Travel Insurance in 2 Minutes</h3>
    <p style="color:#6C757D;font-size:0.85rem;margin:0 0 16px;">Trusted by 1M+ travelers. Coverage starts from $1.50/day.</p>
    <a href="https://www.safetywing.com/nomad-insurance?referenceID=26492686&utm_source=26492686&utm_medium=Ambassador" target="_blank" rel="noopener noreferrer sponsored" style="display:inline-block;background:#00C9A7;color:#fff;padding:14px 32px;border-radius:8px;text-decoration:none;font-weight:600;font-size:0.95rem;transition:background 0.2s;">Get a Quote from SafetyWing &rarr;</a>
    <div style="margin-top:20px;">
        <div class="safetywing-price-widget" data-safetywingaffiliateid="26492686" data-scale="1.0"></div>
        <script type="text/javascript" src="https://storage.googleapis.com/safetywing-static/widget/safetywing-price-widget.js"></script>
    </div>
</div>
```

### Car Rental — Localrent Widget (countries where available)
```html
<!-- Localrent Car Rental Widget -->
<div style="margin: 40px 0; padding: 35px 30px; background: #f0f8f5; border-radius: 12px; border: 1px solid #e0f0ea;">
    <h3 style="margin: 0 0 14px 0; color: #0f0f23; font-size: 1.3rem;">Rent a Car in [Country]</h3>
    <p style="margin: 0 0 24px 0; color: #666; font-size: 0.95rem;">Compare local car rental deals — no hidden fees, free cancellation.</p>
    <script async src="https://tpwdg.com/content?trs=508747&shmarker=711400&powered_by=true&country=[CODE]&lang=en&width=100&background=transparent&logo=false&header=true&gearbox=true&cars=false&border=false&footer=false&campaign_id=87&promo_id=4322" charset="utf-8"></script>
</div>
```

### Car Rental — DiscoverCars (countries where Localrent unavailable)
```html
<!-- Car Rental — [Country] (Localrent not available) -->
<div style="margin: 40px 0; padding: 35px 30px; background: #f0f8f5; border-radius: 12px; border: 1px solid #e0f0ea;">
    <h3 style="margin: 0 0 14px 0; color: #0f0f23; font-size: 1.3rem;">Rent a Car in [Country]</h3>
    <p style="margin: 0 0 10px 0; color: #666; font-size: 0.95rem; line-height: 1.7;">[Country-specific description about why renting is great.]</p>
    <p style="margin: 0 0 20px 0; color: #666; font-size: 0.95rem; line-height: 1.7;"><strong>Tip:</strong> [Booking tip relevant to this country.]</p>
    <a href="https://www.discovercars.com/[country-slug]?a_aid=packsmart" target="_blank" rel="noopener noreferrer sponsored" style="display: inline-block; background: #00C9A7; color: #fff; padding: 12px 28px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 0.95rem; transition: background 0.2s;">Compare Car Rentals in [Country] &rarr;</a>
</div>
```

### Related Packing Guides (3 cards, placed after car rental)
```html
<div class="related-posts">
    <h3>Related Packing Guides</h3>
    <div class="related-grid">
        <div class="related-card">
            <div class="related-card-body">
                <h4>[Title]</h4>
                <p>[1-2 sentence description]</p>
                <a href="https://www.packsmartapp.com/blog/[slug].html">Read More <span class="related-arrow">→</span></a>
                <div class="related-tag">Destination Guide</div>
            </div>
        </div>
        <!-- repeat for 2 more cards -->
    </div>
</div>
```

### Newsletter CTA
```html
<div class="newsletter-cta" style="background:linear-gradient(135deg,#0f0f23,#1a1a3e);color:#fff;padding:40px;border-radius:16px;text-align:center;margin:50px 0 30px;">
    <h3 style="font-size:1.4rem;margin-bottom:8px;">Never Miss a Travel Guide</h3>
    <p style="color:#ccc;margin-bottom:20px;font-size:0.95rem;">Get the latest packing lists, destination guides, and travel tips delivered to your inbox.</p>
    <form id="nlForm" onsubmit="return nlSub(event)" style="display:flex;justify-content:center;gap:10px;flex-wrap:wrap;max-width:480px;margin:0 auto;">
        <input type="email" id="nlEmail" placeholder="Your email address" required style="flex:1;min-width:200px;padding:12px 16px;border-radius:30px;border:none;font-size:0.95rem;font-family:inherit;">
        <button type="submit" id="nlBtn" style="display:inline-block;background:#00C9A7;color:#fff;padding:12px 28px;border-radius:30px;border:none;font-size:0.95rem;font-weight:600;cursor:pointer;white-space:nowrap;font-family:inherit;">Subscribe Free</button>
    </form>
    <p id="nlMsg" style="color:#00C9A7;font-size:0.85rem;margin-top:12px;display:none;"></p>
    <p id="nlNote" style="color:#777;font-size:0.75rem;margin-top:12px;">No spam. Unsubscribe anytime.</p>
    <script>function nlSub(e){e.preventDefault();var b=document.getElementById('nlBtn'),m=document.getElementById('nlMsg'),em=document.getElementById('nlEmail');b.textContent='Subscribing...';b.disabled=true;fetch('/api/subscribe',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:em.value})}).then(r=>r.json()).then(d=>{if(d.success){m.style.display='block';m.style.color='#00C9A7';m.textContent='You\'re subscribed! We\'ll send you our latest guides.';em.value='';document.getElementById('nlNote').style.display='none';}else{m.style.display='block';m.style.color='#E94560';m.textContent=d.error||'Something went wrong. Please try again.';}b.textContent='Subscribe Free';b.disabled=false;}).catch(()=>{m.style.display='block';m.style.color='#E94560';m.textContent='Something went wrong. Please try again.';b.textContent='Subscribe Free';b.disabled=false;});return false;}</script>
</div>
```

### FAQ Section (details/summary)
```html
<div class="faq-section" style="margin:50px 0 30px;padding:30px 0;border-top:2px solid #f0f0f0;">
    <h2 style="font-size:1.6rem;color:#0f0f23;margin-bottom:20px;padding-bottom:8px;border-bottom:3px solid #00C9A7;display:inline-block;">Frequently Asked Questions</h2>
    <details style="margin-bottom:12px;background:#f8f9fa;border-radius:10px;border:1px solid #e9ecef;">
      <summary style="padding:16px 20px;font-weight:600;cursor:pointer;color:#0f0f23;font-size:1.05rem;">[Question]</summary>
      <div style="padding:0 20px 16px;color:#555;font-size:0.98rem;line-height:1.8;">[Answer]</div>
    </details>
    <!-- repeat for each FAQ -->
</div>
```

### Footer
```html
<footer class="footer">
    <div class="footer-inner">
        <div class="footer-brand-col">
            <div class="footer-logo">Pack<em>Smart</em></div>
            <p>Effortless travel preparation. Get personalized packing lists, visa info, and local tips for any destination in the world.</p>
        </div>
        <div class="footer-col"><h4>Product</h4><a href="/#how">How It Works</a><a href="/#features">Features</a><a href="/#plan">Plan a Trip</a></div>
        <div class="footer-col"><h4>Company</h4><a href="/about.html">About</a><a href="/flights.html">Flights & Hotels</a><a href="/blog.html">Blog</a><a href="/pricing.html">Pricing</a><a href="/contact.html">Contact</a></div>
        <div class="footer-col"><h4>Legal</h4><a href="/privacy-policy.html">Privacy Policy</a><a href="/terms.html">Terms of Service</a><a href="/affiliate-disclosure.html">Affiliate Disclosure</a></div>
    </div>
    <div class="footer-bottom">
        <span>&copy; 2026 PackSmart. All rights reserved.</span>
        <span>Made for travelers.</span>
    </div>
</footer>
```

### Closing Script (end of body)
```html
<script>
const nav = document.getElementById('nav');
window.addEventListener('scroll', () => nav.classList.toggle('scrolled', window.scrollY > 50));
const menuBtn = document.getElementById('menuBtn');
menuBtn.addEventListener('click', () => document.getElementById('navLinks').classList.toggle('open'));
document.querySelectorAll('.nav-links a').forEach(a => a.addEventListener('click', () => document.getElementById('navLinks').classList.remove('open')));
</script>
```

---

## Affiliate Links Reference

### SafetyWing (ID: 26492686)
- CTA button: `https://www.safetywing.com/nomad-insurance?referenceID=26492686&utm_source=26492686&utm_medium=Ambassador`
- Widget: `data-safetywingaffiliateid="26492686"`
- Widget script: `https://storage.googleapis.com/safetywing-static/widget/safetywing-price-widget.js`
- DO NOT USE: `https://widget.safetywing.com/out/widget.js` (dead)

### GetYourGuide
- `https://www.getyourguide.com?partner_id=D7IXONS&cmp=share_to_earn`

### Klook (aid: 116473, aff_adid: 1241039)
- `https://affiliate.klook.com/redirect?aid=116473&aff_adid=1241039&k_site=[ENCODED_URL]`

### Welcome Pickups
- `https://www.welcomepickups.com/?utm_source=affiliate&utm_medium=packsmart`

### DiscoverCars (for countries without Localrent)
- `https://www.discovercars.com/[country-slug]?a_aid=packsmart`

### Yesim eSIM (BROKEN — no tracking currently)
- Currently: `https://yesim.app/` (no affiliate tracking)
- Needs: TP campaign p=8310 subscription or direct Yesim affiliate link

### Localrent Country Codes (via Travelpayouts)
| Country | Code |
|---|---|
| Australia | 1 |
| Malaysia | 2 |
| South Korea | 3 |
| Thailand | 9 |
| Italy | 13 |
| UAE (Dubai) | 14 |
| Portugal | 17 |
| Greece | 18 |
| Mexico | 25 |
| Spain | 35 |
| Sri Lanka | 132 |
| Costa Rica | 173 |
| Bali (Indonesia) | 251 |

### Countries WITHOUT Localrent (use DiscoverCars)
- Japan, Canada, USA, New Zealand, Nepal

### Localrent Widget URL Template
```
https://tpwdg.com/content?trs=508747&shmarker=711400&powered_by=true&country=[CODE]&lang=en&width=100&background=transparent&logo=false&header=true&gearbox=true&cars=false&border=false&footer=false&campaign_id=87&promo_id=4322
```

---

## Checklist for New Articles

Before publishing, verify:

- [ ] Nav links: Flights & Hotels | How It Works | Features | Blog | Plan My Trip
- [ ] Hero: inline background image, padding-based (no fixed height), 3 meta divs
- [ ] Affiliate disclosure present
- [ ] Share row (top): icon-based with WhatsApp, X, Facebook, LinkedIn, Copy Link
- [ ] All h2s have `border-left: 4px solid var(--primary)`
- [ ] CTA box present
- [ ] SafetyWing widget: center-aligned, gradient bg, CTA button + interactive widget
- [ ] Car rental: Localrent widget (check country code) OR DiscoverCars link
- [ ] Related Guides: 3 cards, div-based with `related-card-body`, descriptions, tags
- [ ] Newsletter CTA: dark gradient, rounded inputs
- [ ] Share row (bottom): same as top
- [ ] FAQ: details/summary with gray background, rounded corners
- [ ] Footer: 4-column grid, correct links
- [ ] Mobile responsive: check 768px and 600px breakpoints
