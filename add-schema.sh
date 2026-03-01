#!/bin/bash
# Add Schema Markup to all PackSmart pages
# Run from packsmart folder: bash add-schema.sh

echo "Adding schema markup to PackSmart pages..."

# === HOMEPAGE (WebApplication + Organization) ===
perl -i -pe 'BEGIN{$done=0} if (/<\/head>/ && !$done) { s/<\/head>/<script type="application\/ld+json">\n{\n  "\@context": "https:\/\/schema.org",\n  "\@type": "WebApplication",\n  "name": "PackSmart",\n  "url": "https:\/\/packsmartapp.com",\n  "description": "AI-powered travel planning tool that generates personalized packing lists, visa info, hotel recommendations, safety alerts, and budget breakdowns.",\n  "applicationCategory": "TravelApplication",\n  "operatingSystem": "Web",\n  "offers": {\n    "\@type": "Offer",\n    "price": "0",\n    "priceCurrency": "USD"\n  },\n  "creator": {\n    "\@type": "Organization",\n    "name": "PackSmart",\n    "url": "https:\/\/packsmartapp.com",\n    "logo": "https:\/\/packsmartapp.com\/favicon.ico"\n  }\n}\n<\/script>\n<\/head>/; $done=1; }' public/index.html
if grep -q "WebApplication" public/index.html; then echo "ADDED: public/index.html (WebApplication)"; else echo "FAILED: public/index.html"; fi

# === ABOUT PAGE ===
perl -i -pe 'BEGIN{$done=0} if (/<\/head>/ && !$done) { s/<\/head>/<script type="application\/ld+json">\n{\n  "\@context": "https:\/\/schema.org",\n  "\@type": "AboutPage",\n  "name": "About PackSmart",\n  "url": "https:\/\/packsmartapp.com\/about.html",\n  "description": "Learn about PackSmart - the AI-powered travel planning tool that helps you pack smarter and travel better.",\n  "isPartOf": {\n    "\@type": "WebSite",\n    "name": "PackSmart",\n    "url": "https:\/\/packsmartapp.com"\n  }\n}\n<\/script>\n<\/head>/; $done=1; }' public/about.html
if grep -q "AboutPage" public/about.html; then echo "ADDED: public/about.html (AboutPage)"; else echo "FAILED: public/about.html"; fi

# === CONTACT PAGE ===
perl -i -pe 'BEGIN{$done=0} if (/<\/head>/ && !$done) { s/<\/head>/<script type="application\/ld+json">\n{\n  "\@context": "https:\/\/schema.org",\n  "\@type": "ContactPage",\n  "name": "Contact PackSmart",\n  "url": "https:\/\/packsmartapp.com\/contact.html",\n  "description": "Get in touch with the PackSmart team for questions, feedback, or partnership inquiries.",\n  "isPartOf": {\n    "\@type": "WebSite",\n    "name": "PackSmart",\n    "url": "https:\/\/packsmartapp.com"\n  }\n}\n<\/script>\n<\/head>/; $done=1; }' public/contact.html
if grep -q "ContactPage" public/contact.html; then echo "ADDED: public/contact.html (ContactPage)"; else echo "FAILED: public/contact.html"; fi

# === BLOG LISTING PAGE ===
perl -i -pe 'BEGIN{$done=0} if (/<\/head>/ && !$done) { s/<\/head>/<script type="application\/ld+json">\n{\n  "\@context": "https:\/\/schema.org",\n  "\@type": "Blog",\n  "name": "PackSmart Travel Blog",\n  "url": "https:\/\/packsmartapp.com\/blog.html",\n  "description": "Expert travel tips, packing guides, and destination advice from PackSmart.",\n  "publisher": {\n    "\@type": "Organization",\n    "name": "PackSmart",\n    "url": "https:\/\/packsmartapp.com"\n  }\n}\n<\/script>\n<\/head>/; $done=1; }' public/blog.html
if grep -q '"Blog"' public/blog.html; then echo "ADDED: public/blog.html (Blog)"; else echo "FAILED: public/blog.html"; fi

# === BLOG POSTS (Article schema) ===

# Function to add article schema
add_article_schema() {
    local file=$1
    local title=$2
    local url=$3
    local description=$4
    local date=$5

    perl -i -pe "BEGIN{\$done=0} if (/<\/head>/ && !\$done) { s/<\/head>/<script type=\"application\/ld+json\">\n{\n  \"\\\@context\": \"https:\/\/schema.org\",\n  \"\\\@type\": \"Article\",\n  \"headline\": \"$title\",\n  \"url\": \"$url\",\n  \"description\": \"$description\",\n  \"datePublished\": \"$date\",\n  \"dateModified\": \"$date\",\n  \"author\": {\n    \"\\\@type\": \"Organization\",\n    \"name\": \"PackSmart\"\n  },\n  \"publisher\": {\n    \"\\\@type\": \"Organization\",\n    \"name\": \"PackSmart\",\n    \"url\": \"https:\/\/packsmartapp.com\"\n  }\n}\n<\/script>\n<\/head>/; \$done=1; }" "$file"

    if grep -q '"Article"' "$file"; then echo "ADDED: $file (Article)"; else echo "FAILED: $file"; fi
}

add_article_schema "public/blog/solo-travel-tips-beginners.html" \
    "Solo Travel Tips for Beginners" \
    "https://packsmartapp.com/blog/solo-travel-tips-beginners.html" \
    "Essential tips and advice for first-time solo travelers." \
    "2026-02-24"

add_article_schema "public/blog/ship-cruise-travel-tips.html" \
    "Ship and Cruise Travel Tips" \
    "https://packsmartapp.com/blog/ship-cruise-travel-tips.html" \
    "Everything you need to know about cruise and ship travel." \
    "2026-02-24"

add_article_schema "public/blog/first-time-flying.html" \
    "First Time Flying Tips" \
    "https://packsmartapp.com/blog/first-time-flying.html" \
    "Complete guide for first-time flyers with airport tips and packing advice." \
    "2026-02-24"

add_article_schema "public/blog/road-trip-packing-checklist.html" \
    "Road Trip Packing Checklist" \
    "https://packsmartapp.com/blog/road-trip-packing-checklist.html" \
    "The ultimate road trip packing checklist to ensure you never forget essentials." \
    "2026-02-25"

add_article_schema "public/blog/visa-free-countries-indian-passport.html" \
    "Visa-Free Countries for Indian Passport Holders" \
    "https://packsmartapp.com/blog/visa-free-countries-indian-passport.html" \
    "Complete list of visa-free and visa-on-arrival countries for Indian passport holders." \
    "2026-02-25"

add_article_schema "public/blog/train-travel-tips-beginners.html" \
    "Train Travel Tips for Beginners" \
    "https://packsmartapp.com/blog/train-travel-tips-beginners.html" \
    "Essential tips for first-time train travelers including booking and comfort advice." \
    "2026-02-25"

add_article_schema "public/blog/tropical-travel-hacks.html" \
    "Tropical Travel Hacks" \
    "https://packsmartapp.com/blog/tropical-travel-hacks.html" \
    "Smart hacks and tips for traveling to tropical destinations." \
    "2026-02-25"

add_article_schema "public/blog/cold-weather-travel-hacks.html" \
    "Cold Weather Travel Hacks" \
    "https://packsmartapp.com/blog/cold-weather-travel-hacks.html" \
    "Essential tips for packing and traveling in cold weather destinations." \
    "2026-02-25"

add_article_schema "public/budget-travel-destinations-2026.html" \
    "Budget Travel Destinations 2026" \
    "https://packsmartapp.com/budget-travel-destinations-2026.html" \
    "Top 15 affordable travel destinations for 2026 with daily budget breakdowns." \
    "2026-03-01"

add_article_schema "public/carry-on-packing-list.html" \
    "Ultimate Carry-On Packing List" \
    "https://packsmartapp.com/carry-on-packing-list.html" \
    "The complete carry-on packing list with capsule wardrobe tips and airline size limits." \
    "2026-03-01"

echo ""
echo "Done! Now run:"
echo "  git add ."
echo "  git commit -m 'Add schema markup to all pages'"
echo "  git push origin main"
