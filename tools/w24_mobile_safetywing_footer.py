#!/usr/bin/env python3
"""w24: mobile layout fixes found by measuring every page at 390px wide.

1. SafetyWing price widget: the widget script lays itself out 450px wide and only scales it down
   to 0.7, so on a phone it sticks out past the right edge (57 blog pages + Pricing). The page then
   becomes ~17px wider than the screen, which also makes the footer look misaligned on those pages.
   Fix: add the same small "fit" script that the Germany and France pages already use. It scales the
   widget to the width of its container and re-applies after the widget script re-renders.
2. Pricing: on top of 1, the comparison table is wider than the phone and was cut off / forced a
   sideways scroll. Fix: html/body overflow-x hidden and tighter table padding under 600px.
3. New Zealand guide: its footer was the only one collapsing to a single column on phones; the
   other pages use two columns. Restored to two columns.

Run from repo root:  python3 tools/w24_mobile_safetywing_footer.py   (optional arg: public dir)
Idempotent. Validates every page first and writes nothing if any edit does not match exactly once.
"""
import glob, os, sys

PUB = sys.argv[1] if len(sys.argv) > 1 else "public"

LOAD = '<script defer type="text/javascript" src="https://storage.googleapis.com/safetywing-static/widget/safetywing-price-widget.js"></script>'
MARK = 'data-ps-fit="safetywing"'
FIT = ("<script data-ps-fit=\"safetywing\">(function(){var w=document.querySelector('.safetywing-price-widget'); if(!w) return;"
       "var busy=false, obs=null;function fit(){if(busy) return;var W=w.offsetWidth, p=w.parentElement; if(!W||!p) return;"
       "var cs=getComputedStyle(p), pw=p.clientWidth-parseFloat(cs.paddingLeft)-parseFloat(cs.paddingRight);if(pw>=W) return;"
       "var s=pw/W, h=w.offsetHeight;busy=true;w.style.setProperty('transform-origin','left top','important');"
       "w.style.setProperty('transform','scale('+s+')','important');"
       "w.style.setProperty('margin','0 0 '+(-(h*(1-s)))+'px 0','important');if(obs) obs.takeRecords();busy=false;}"
       "obs=new MutationObserver(fit);obs.observe(w,{attributes:true,attributeFilter:['style']});"
       "window.addEventListener('resize',fit);window.addEventListener('load',function(){fit();setTimeout(fit,1500);setTimeout(fit,4000);});})();</script>")

PRICING_OLD = "<style>.safetywing-price-widget{display:block!important;margin:0 auto;max-width:100%;overflow:hidden;} @media(max-width:500px){.safetywing-price-widget{transform:scale(0.85);transform-origin:center top;margin-bottom:-40px;}}</style>"
PRICING_CSS = ("<style>html,body{overflow-x:hidden;max-width:100vw}@media(max-width:600px){.comparison-section{padding:0 .75rem}"
               ".comparison-table th,.comparison-table td{padding:.7rem .35rem;font-size:.78rem}"
               ".comparison-table .check,.comparison-table .cross{font-size:.95rem}.comparison-table .feature-name{width:auto}}</style>")

NZ_OLD = "            .footer-inner { grid-template-columns: 1fr; gap: 2rem; }\n            .footer-bottom { flex-direction: column; text-align: center; }"
NZ_NEW = "            .footer-inner { grid-template-columns: 1fr 1fr; gap: 2rem; }\n            .footer-bottom { flex-direction: column; text-align: center; }"


def read(p):
    with open(p, encoding="utf-8", newline="") as f:
        return f.read()


def plan():
    edits, notes, errors = {}, [], []
    files = sorted(glob.glob(os.path.join(PUB, "blog", "*.html"))) + [os.path.join(PUB, "pricing.html")]
    for p in files:
        s = read(p)
        orig = s
        if 'class="safetywing-price-widget"' in s and MARK not in s:
            if s.count(LOAD) != 1 or s.count('class="safetywing-price-widget"') != 1:
                errors.append("%s: expected 1 widget + 1 loader, got %d + %d" % (p, s.count('class="safetywing-price-widget"'), s.count(LOAD)))
                continue
            i = s.index(LOAD)
            ls = s.rfind("\n", 0, i) + 1
            indent = s[ls:i]
            indent = indent if indent.strip() == "" else ""
            s = s.replace(LOAD, LOAD + "\n" + indent + FIT, 1)
        if p.endswith("pricing.html"):
            if PRICING_CSS not in s:
                if s.count(PRICING_OLD) != 1:
                    errors.append("%s: pricing style anchor count %d" % (p, s.count(PRICING_OLD)))
                    continue
                s = s.replace(PRICING_OLD, PRICING_OLD + "\n" + PRICING_CSS, 1)
        if os.path.basename(p) == "new-zealand-travel-packing-guide.html" or os.path.basename(p) == "new-zealand-travel-packing-guide-from-india.html":
            if NZ_OLD in s:
                if s.count(NZ_OLD) != 1:
                    errors.append("%s: NZ footer anchor count %d" % (p, s.count(NZ_OLD)))
                    continue
                s = s.replace(NZ_OLD, NZ_NEW, 1)
        if s != orig:
            edits[p] = s
    return edits, errors


def main():
    edits, errors = plan()
    if errors:
        print("ABORT - nothing written:")
        for e in errors:
            print("  ", e)
        sys.exit(1)
    for p, s in edits.items():
        with open(p, "w", encoding="utf-8", newline="") as f:
            f.write(s)
    print("files changed: %d" % len(edits))
    fit_added = sum(1 for p in edits if MARK in edits[p])
    print("  fit script added to %d pages" % fit_added)
    print("  pricing.html changed: %s" % any(p.endswith("pricing.html") for p in edits))
    print("  NZ footer changed: %s" % any("new-zealand" in p for p in edits))
    # post-check
    left = [p for p in glob.glob(os.path.join(PUB, "blog", "*.html")) + [os.path.join(PUB, "pricing.html")]
            if 'class="safetywing-price-widget"' in read(p) and MARK not in read(p)]
    print("pages with widget but no fit script: %d" % len(left))


if __name__ == "__main__":
    main()
