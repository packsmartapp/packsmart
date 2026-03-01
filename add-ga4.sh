#!/bin/bash
# Add Google Analytics 4 tracking to all PackSmart HTML pages
# Usage: cd packsmart && bash add-ga4.sh

GA4_CODE='<!-- Google Analytics 4 -->\
<script async src="https://www.googletagmanager.com/gtag/js?id=G-0C4Z7VVGPE"><\/script>\
<script>\
  window.dataLayer = window.dataLayer || [];\
  function gtag(){dataLayer.push(arguments);}\
  gtag('\''js'\'', new Date());\
  gtag('\''config'\'', '\''G-0C4Z7VVGPE'\'');\
<\/script>'

# Find all HTML files in public/ and public/blog/
find public -name "*.html" | while read file; do
    # Check if GA4 is already added
    if grep -q "G-0C4Z7VVGPE" "$file"; then
        echo "SKIP (already has GA4): $file"
    else
        # Insert GA4 code right after <head> tag
        sed -i '' "s|<head>|<head>\\
<!-- Google Analytics 4 -->\\
<script async src=\"https://www.googletagmanager.com/gtag/js?id=G-0C4Z7VVGPE\"></script>\\
<script>\\
  window.dataLayer = window.dataLayer || [];\\
  function gtag(){dataLayer.push(arguments);}\\
  gtag('js', new Date());\\
  gtag('config', 'G-0C4Z7VVGPE');\\
</script>|" "$file"
        echo "ADDED GA4: $file"
    fi
done

echo ""
echo "Done! Now run:"
echo "  git add ."
echo "  git commit -m 'Add Google Analytics 4 tracking to all pages'"
echo "  git push origin main"
