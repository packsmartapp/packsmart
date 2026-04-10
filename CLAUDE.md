# PackSmart Blog Article Template — Style Reference

**Benchmark article:** `public/blog/portugal-travel-packing-guide.html`

Use this document as the canonical style reference for ALL new blog articles. Every article must match this template exactly in structure, colors, fonts, nav, footer, and section ordering.

---

## Brand Colors & Fonts

```css
:root {
    --primary: #00C9A7;     /* PackSmart green — use everywhere */
    --accent: #E94560;       /* Red accent — tags, warnings */
    --dark: #0f0f23;         /* Dark navy — headings, hero bg */
    --light-gray: #f5f5f5;   /* Card backgrounds */
    --text: #333;            /* Body text */
}
font-family: 'DM Sans', sans-serif;
```

**NEVER use:** `#667eea` (purple), system font stacks (`-apple-system, BlinkMacSystemFont...`), or any other color palette.

---

## `<head>` Section Order

1. `<meta charset="UTF-8">`
2. `<meta name="viewport">`
3. `<title>` — format: `{Country} Travel & Packing Guide 2026: Complete Checklist for Indian Travelers | PackSmart Blog`
4. `<meta name="description">` — 160 chars max
5. `<meta name="keywords">`
6. `<link rel="canonical">`
7. OG tags (`og:title`, `og:description`, `og:url`, `og:type`, `og:site_name`, `og:image`)
   - `og:image` → `https://www.packsmartapp.com/og-default.png` (NOT Unsplash URLs)
8. Twitter Card tags (`twitter:card`, `twitter:title`, `twitter:description`, `twitter:image`)
   - `twitter:image` → `https://www.packsmartapp.com/og-default.png`
9. Pinterest Rich Pins: `<meta property="article:author" content="PackSmart">` + `article:section`
10. Google Fonts: `<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">`
11. **GA4 Script:**
```html
<script async src="https://www.googletagmanager.com/gtag/js?id=G-0C4Z7VVGPE"></script>
<script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-0C4Z7VVGPE');
</script>
```
12. **Travelpayouts Verification Script:**
```html
<script data-noptimize="1" data-cfasync="false" data-wpfc-render="false">
  (function () {
      var script = document.createElement("script");
      script.async = 1;
      script.src = 'https://emrld.ltd/NTA4NzQ3.js?t=508747';
      document.head.appendChild(script);
  })();
</script>
<script async src="https://emrld.ltd/NTA4NzQ3.js?t=508747"></script>
```
13. Article Schema (JSON-LD) — use `"@name"` for author/publisher
14. BreadcrumbList Schema (JSON-LD)
15. `<style>` block (see CSS section below)
16. FAQPage Schema (JSON-LD) — before `</head>`

---

## CSS Classes (Must Match Exactly)

### Navigation
```css
.nav { position: fixed; top: 0; left: 0; right: 0; z-index: 100; padding: 0 3rem; height: 72px; display: flex; align-items: center; justify-content: space-between; background: transparent; transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1); }
.nav.scrolled { background: rgba(253,240,242,0.88); backdrop-filter: blur(20px) saturate(180%); -webkit-backdrop-filter: blur(20px) saturate(180%); border-bottom: 1px solid #eee; }
.nav-brand { font-family: 'DM Sans', sans-serif; font-weight: 800; font-size: 1.2rem; color: #fff; text-decoration: none; letter-spacing: -0.3px; }
.nav-brand em { font-style: normal; color: #00C9A7; }
.nav.scrolled .nav-brand { color: #333; }
.nav.scrolled .nav-brand em { color: #00C9A7; }
.nav.scrolled .nav-links a { color: #666; }
.nav.scrolled .mobile-menu-btn span { background: #333; }
```

### Hero
```css
.hero-blog { background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 100%); background-size: cover; background-position: center; color: white; padding: 180px 2rem; text-align: center; }
```

### Content Area
```css
.content { max-width: 800px; margin: 0 auto; padding: 3rem 2rem; }
.content h2 { color: var(--dark); font-size: 1.8rem; margin-top: 2.5rem; margin-bottom: 1rem; border-left: 4px solid var(--primary); padding-left: 1rem; }
.content h3 { color: var(--dark); font-size: 1.2rem; margin-top: 1.5rem; margin-bottom: 0.7rem; }
```

### Tables
```css
.checklist-table th { background: var(--primary); color: white; padding: 1rem; text-align: left; font-weight: 600; }
```
Table header bg is `--primary` (#00C9A7 green), NOT `--dark`.

### Season/Weather Cards
```css
.weather-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; margin: 1.5rem 0; }
.weather-card { background: var(--light-gray); padding: 1.5rem; border-radius: 8px; border-top: 3px solid var(--primary); }
.weather-card h4 { color: var(--primary); margin-bottom: 0.5rem; }
```

### Tip & Warning Boxes
```css
.tip-box { background: #f0fef9; border-left: 4px solid var(--primary); padding: 1.5rem; margin: 1.5rem 0; border-radius: 4px; }
.tip-box strong { color: var(--primary); }
.warning-box { background: #fff5f5; border-left: 4px solid var(--accent); padding: 1.5rem; margin: 1.5rem 0; border-radius: 4px; }
.warning-box strong { color: var(--accent); }
```

### CTA Box
```css
.cta-box { background: linear-gradient(135deg, var(--primary) 0%, #00a080 100%); color: white; padding: 2rem; border-radius: 8px; text-align: center; margin: 3rem 0; }
.cta-box a { background: var(--accent); color: white; padding: 0.8rem 2rem; text-decoration: none; border-radius: 4px; display: inline-block; font-weight: 600; }
```
CTA box bg is **green gradient**, button is **red accent**. NOT dark navy.

### Footer
```css
.footer { padding: 60px 2rem 40px; background: rgba(248,249,250,0.75); border-top: 1px solid #eee; }
.footer-inner { max-width: 1100px; margin: 0 auto; display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 3rem; }
```

### Mobile Menu
```css
@media (max-width: 600px) {
    .nav { padding: 0 1.5rem; }
    .nav-links { display: none; }
    .nav-links.open { display: flex; flex-direction: column; position: fixed; top: 72px; left: 0; right: 0; background: rgba(255,255,255,0.98); backdrop-filter: blur(20px); padding: 2rem; gap: 1.5rem; box-shadow: 0 10px 40px rgba(0,0,0,0.08); }
    .mobile-menu-btn { display: block; }
}
```

---

## Nav HTML (Exact)

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
    <button class="mobile-menu-btn" id="menuBtn" aria-label="Menu">
        <span></span><span></span><span></span>
    </button>
</nav>
```

---

## Hero HTML

```html
<div class="hero-blog" style="background: linear-gradient(rgba(15,15,35,0.7), rgba(26,26,62,0.7)), url('{HERO_IMAGE_URL}'); background-size: cover; background-position: center;">
    <h1>{Article Title}</h1>
    <div class="meta">{Date} · {Read Time}</div>
    <div class="meta">Destination Guide</div>
    <div class="meta">Last updated: March 2026</div>
</div>
```

---

## Article Body Section Order

1. `<div class="content">` opening
2. Affiliate disclosure paragraph
3. Share buttons row (WhatsApp, X, Facebook, LinkedIn, Copy Link)
4. Main content sections (Visa, Best Time, Packing, City Guides, Budget, Apps, etc.)
5. Inline images as `<figure>` with `<figcaption>`
6. Internal link callout boxes (green left border)
7. Share buttons row (bottom, repeated)
8. FAQ section with `<details>/<summary>`
9. CTA box
10. `</div>` (close .content)
11. Localrent widget (if applicable for that country)
12. Related posts grid
13. Travel Essentials affiliate grid
14. SafetyWing widget (on India-targeted articles)
15. Newsletter CTA
16. Footer
17. Nav scroll + mobile menu JS

---

## Internal Link Callout Box Format

```html
<p style="background:#f0faf7;border-left:3px solid #00C9A7;padding:12px 16px;border-radius:0 8px 8px 0;font-size:0.92rem;margin:20px 0;">
    <a href="/flights.html" style="color:#00C9A7;text-decoration:underline;">Compare flight prices</a> to {Country}.
</p>
```

---

## Inline Image Format

```html
<figure style="margin:28px 0;text-align:center;">
    <img src="https://images.unsplash.com/{PHOTO_ID}?w=800&h=450&fit=crop&auto=format&q=75" alt="{descriptive alt}" style="width:100%;border-radius:12px;object-fit:cover;" loading="lazy">
    <figcaption style="font-size:0.82rem;color:#999;margin-top:8px;font-style:italic;">{Caption text}</figcaption>
</figure>
```

Always verify Unsplash image IDs return HTTP 200 before using.

---

## Footer HTML (Exact)

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

---

## Closing JS (Exact)

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

## Affiliate Links (Current as of March 2026)

| Partner | URL | Commission |
|---|---|---|
| GetYourGuide | `https://www.getyourguide.com?partner_id=D7IXONS&cmp=share_to_earn` | 16% |
| Yesim eSIM | `https://yesim.tpx.li/cCWg3rkx` (TP short link — old p=8310 program is BROKEN, redirects to Airalo. Always use this tpx.li short link instead) | — |
| SafetyWing | `https://safetywing.com/?referenceID=26492686&utm_source=26492686&utm_medium=Ambassador` | 10% |
| Welcome Pickups | `https://tpx.li/qYFLwgZ8` | 8-9% |
| Localrent | TP widget (country-specific `country=` param) | 7.5-12% |
| Klook | `https://affiliate.klook.com/redirect?aid=116473&aff_adid=1241039&k_site=...` (city-specific) | 2-5% |
| 12Go | Widget with `agent=15357692` (SE Asia articles only) | ~5% |
| Tiqets | Country-specific TP short links (EU/Dubai only) | 3.5-8% |

**Priority order for placement:** GetYourGuide > Yesim > SafetyWing > Welcome Pickups > Localrent > Others

---

## Localrent Widget Code

```html
<div style="margin: 40px 0; padding: 35px 30px; background: #f0f8f5; border-radius: 12px; border: 1px solid #e0f0ea;">
    <h3 style="margin: 0 0 14px 0; color: #0f0f23; font-size: 1.3rem;">Rent a Car in {Country}</h3>
    <p style="margin: 0 0 24px 0; color: #666; font-size: 0.95rem;">Compare local car rental deals — no hidden fees, free cancellation.</p>
    <script async src="https://tpwdg.com/content?trs=508747&shmarker=711400&powered_by=true&country={COUNTRY_CODE}&lang=en&width=100&background=transparent&logo=false&header=true&gearbox=true&cars=false&border=false&footer=false&campaign_id=87&promo_id=4322" charset="utf-8"></script>
</div>
```

Known country codes: Thailand=9, Bali=251, UAE=14, Greece=18, Italy=13, Spain=35, Portugal=17, Mexico=25, Malaysia=2, Sri Lanka=132, Costa Rica=173, Australia=1, Germany=29, France=12, Switzerland=59, South Korea=3, Vietnam=11, USA=N/A (404), Canada=N/A.

---

## Travelpayouts IDs

- Marker: `711400`
- TRS: `508747`
- GA4: `G-0C4Z7VVGPE`
- 12Go agent: `15357692`

---

## Git Workflow

- Fresh clone at `/sessions/amazing-wonderful-mayer/packsmart-fresh/`
- All commits: `git -c user.name="Ari" -c user.email="swarnali.rc@gmail.com"`
- Remote: `https://github.com/packsmartapp/packsmart.git` (use token from git config)
- Vercel auto-deploys from main branch
- Always verify Unsplash images (HTTP 200) before committing
- Always add new articles to `public/blog.html` listing page

---

## Blog Card Format (for blog.html)

```html
<a href="/blog/{filename}.html" class="blog-card">
    <img class="blog-card-img" src="https://images.unsplash.com/{PHOTO_ID}?w=800&h=400&fit=crop&auto=format&q=75" alt="{Title}" loading="lazy">
    <div class="blog-card-body">
        <span class="tag">Destination Guide</span>
        <h2>{Title with &amp; entities}</h2>
        <p>{Short description with &mdash; entities}</p>
        <span class="meta">{Date} &middot; {Read Time}</span>
        <br><span class="read-more">Read more &rarr;</span>
    </div>
</a>
```
