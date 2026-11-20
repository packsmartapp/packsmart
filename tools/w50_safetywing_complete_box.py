#!/usr/bin/env python3
"""w50: add a short 'Nomad Insurance Complete' box right after the SafetyWing Essential box + price widget.

Run from the repo root:
  python3 -I tools/w50_safetywing_complete_box.py            # patch
  python3 -I tools/w50_safetywing_complete_box.py --dry-run  # report only, write nothing

Pages: every public/blog/*.html that carries the SafetyWing price widget (a <div ... safetywing-price-widget ...>)
plus its fit script (data-ps-fit="safetywing"). pricing.html is deliberately left out.
Idempotent: skips pages that already carry data-ps-placement="safetywing-complete".
All-or-nothing: if any page has an unexpected structure, nothing is written.
Link: Complete product link from the SafetyWing ambassador dashboard (referenceID 26492686).
"""
import re, sys, glob

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

WIDGET_DIV = re.compile(r'<div[^>]*safetywing-price-widget[^>]*>')
FIT = 'data-ps-fit="safetywing"'
# after the fit script: close the margin-top wrapper and the outer box, optionally followed by a closing comment
TAIL = re.compile(r'</script>\s*</div>\s*</div>(?:[ \t]*<!--\s*closes SafetyWing outer container\s*-->)?[ \t]*\n')

def plan(path):
    h = open(path, encoding='utf-8').read()
    if 'data-ps-placement="safetywing-complete"' in h:
        return ('skip', None)
    if len(WIDGET_DIV.findall(h)) == 0:
        return ('nowidget', None)
    if len(WIDGET_DIV.findall(h)) != 1 or h.count(FIT) != 1:
        raise SystemExit(f'ABORT: unexpected widget/fit count in {path}')
    j = h.index(FIT)
    m = TAIL.search(h, j)
    if not m or m.start() - j > 3000:
        raise SystemExit(f'ABORT: end of SafetyWing block not found in {path}')
    new = h[:m.end()] + BOX + h[m.end():]
    if new.count('<div') - new.count('</div>') != h.count('<div') - h.count('</div>'):
        raise SystemExit(f'ABORT: div balance changed in {path}')
    return ('patch', new)

def main():
    dry = '--dry-run' in sys.argv
    pages = sorted(p for p in glob.glob('public/blog/*.html'))
    todo, skipped, nowidget = [], [], []
    for p in pages:
        kind, new = plan(p)
        if kind == 'patch': todo.append((p, new))
        elif kind == 'skip': skipped.append(p)
        else: nowidget.append(p)
    print(f'to patch: {len(todo)} | already applied: {len(skipped)} | no widget: {len(nowidget)}')
    if dry:
        for p, _ in todo: print('  would patch:', p)
        return
    for p, new in todo:
        open(p, 'w', encoding='utf-8').write(new)
    print('done, pages changed:', len(todo))

if __name__ == '__main__':
    main()
