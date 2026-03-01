#!/bin/bash
# Add GA4 to all PackSmart HTML files (macOS compatible)
# Run from packsmart folder: bash add-ga4-fix.sh

GA4='<head>\
<!-- Google Analytics 4 -->\
<script async src="https://www.googletagmanager.com/gtag/js?id=G-0C4Z7VVGPE"></script>\
<script>\
  window.dataLayer = window.dataLayer || [];\
  function gtag(){dataLayer.push(arguments);}\
  gtag("js", new Date());\
  gtag("config", "G-0C4Z7VVGPE");\
</script>'

for file in $(find public -name "*.html"); do
    if grep -q "G-0C4Z7VVGPE" "$file"; then
        echo "SKIP: $file"
    else
        sed -i '' "s|<head>|$GA4|" "$file"
        if grep -q "G-0C4Z7VVGPE" "$file"; then
            echo "ADDED: $file"
        else
            echo "FAILED: $file"
        fi
    fi
done

echo ""
echo "Done! Verify with: grep -l G-0C4Z7VVGPE public/*.html public/blog/*.html"
