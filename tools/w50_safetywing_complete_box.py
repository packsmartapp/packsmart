#!/usr/bin/env python3
"""w50: add a short 'Nomad Insurance Complete' box after the SafetyWing Essential box + price widget.

Run from the repo root:  python3 -I tools/w50_safetywing_complete_box.py
Idempotent: skips pages that already carry data-ps-placement="safetywing-complete".
Aborts without writing if the anchor (the SAFETYWING INSURANCE WIDGET block) is not found exactly once.
Link: Complete product link from the SafetyWing ambassador dashboard (referenceID 26492686).
"""
import re, sys, pathlib

PAGES = ["public/blog/travel-insurance-guide.html"]

LINK = ("https://explore.safetywing.com/nomad-insurance-complete?selectedPlan=NOMAD_INSURANCE_COMPLETE"
        "&amp;referenceID=26492686&amp;utm_source=26492686&amp;utm_medium=Ambassador")

BOX = f'''
<!-- SAFETYWING COMPLETE -->
<div data-ps-placement="safetywing-complete" style="background:#fff;border-radius:16px;padding:22px 24px;margin:0 0 30px;border:1px solid #C8E6DC;border-left:4px solid #00C9A7;">
    <h3 style="font-size:1.1rem;margin:0 0 8px;color:#212529;">Staying abroad longer? See Nomad Insurance Complete</h3>
    <p style="color:#495057;font-size:0.92rem;line-height:1.6;margin:0 0 14px;">Full health insurance for nomads, expats and families abroad. Renewable, with cover up to US$1,500,000 and year-round home country cover. It costs more than Essential, has a 12-month commitment, and does not cover pre-existing conditions.</p>
    <a href="{LINK}" target="_blank" rel="noopener noreferrer sponsored" style="display:inline-block;background:#00C9A7;color:#fff;padding:12px 26px;border-radius:8px;text-decoration:none;font-weight:600;font-size:0.92rem;">See Nomad Insurance Complete &rarr;</a>
</div>
'''

ANCHOR = '<!-- SAFETYWING INSURANCE WIDGET -->'
END = re.compile(r'</script>\s*</div>\s*</div>\n')

def main():
    changed = 0
    plans = []
    for rel in PAGES:
        p = pathlib.Path(rel)
        h = p.read_text(encoding='utf-8')
        if 'data-ps-placement="safetywing-complete"' in h:
            print('skip (already applied):', rel); continue
        if h.count(ANCHOR) != 1:
            sys.exit(f'ABORT: anchor count {h.count(ANCHOR)} in {rel}')
        i = h.index(ANCHOR)
        m = END.search(h, i)
        if not m:
            sys.exit(f'ABORT: end of widget block not found in {rel}')
        plans.append((p, h[:m.end()] + BOX + h[m.end():]))
    for p, new in plans:
        p.write_text(new, encoding='utf-8'); changed += 1; print('patched:', p)
    print('done, pages changed:', changed)

if __name__ == '__main__':
    main()
