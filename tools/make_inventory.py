#!/usr/bin/env python3
"""make_inventory: regenerate docs/INVENTORY.md from the repo (what exists, where, and what each script does).

Run from the repo root:  python3 -I tools/make_inventory.py
Read-only on everything except docs/INVENTORY.md. Safe to re-run any time; do it after adding a script,
a page type or a doc, then commit the result. The "what it does" column is the first line of each
script's docstring, so keep that line accurate.
"""
import ast
import datetime
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "INVENTORY.md")


def first_doc_line(path):
    try:
        doc = ast.get_docstring(ast.parse(open(path, encoding="utf-8").read())) or ""
    except SyntaxError:
        return "(could not read docstring)"
    line = doc.strip().split("\n")[0].strip() if doc.strip() else ""
    if not line:
        return "(no docstring)"
    return line.replace("|", "/")[:140]


def ls(rel, ext=None):
    d = os.path.join(ROOT, rel)
    if not os.path.isdir(d):
        return []
    names = sorted(n for n in os.listdir(d) if os.path.isfile(os.path.join(d, n)))
    return [n for n in names if not n.startswith(".") and (ext is None or n.endswith(ext))]


def num_key(name):
    m = re.match(r"w(\d+)_", name)
    return int(m.group(1)) if m else 10 ** 6


lines = []
w = lines.append
today = datetime.date.today().strftime("%d %b %Y")

w("# PackSmart: file inventory")
w("")
w(f"Generated {today} by `tools/make_inventory.py` (re-run it after adding scripts, pages or docs).")
w("Every file below is already saved in git (`packsmartapp/packsmart`, branch `main`); `git clone` is the full backup.")
w("This page says what exists and where. It does not repeat file contents, because git always has the latest version.")
w("")
w("## Where things live")
w("")
w("| Place | What is there |")
w("|---|---|")
w("| This repo, `public/` | everything deployed to packsmartapp.com |")
w("| This repo, `tools/` | Python generators and post-processors, plus `pocket_guides.json` |")
w("| This repo, `api/` | Vercel serverless functions |")
w("| This repo, `docs/` | product spec, decisions, backlog, this inventory |")
w("| This repo, root | `CLAUDE.md` (loaded every Claude Code session), `BLOG_STYLE_GUIDE.md`, `vercel.json`, `package.json` |")
w("| Claude Project \"Packsmart\" | about 170 dated build notes, fact sheets and link requests (`AFFILIATE_*`, `POCKET_*`, `*_BUILD_NOTES`, `*_FACTS`, `KLOOK_*`); not in the repo |")
w("| Gitignored, not in this folder | `PROJECT_CONTEXT.md` (private context; only the Claude Project copy was found on 21 Nov, last written 10 Nov), `backlink-outreach/`, `pinterest-pins/` |")
w("")

w("## Root files")
w("")
for n in ls("", None) + [".gitignore"]:
    w(f"- `{n}`")
w("")

w("## api/ (Vercel functions)")
w("")
for n in ls("api"):
    w(f"- `api/{n}`")
w("")

w("## docs/")
w("")
for n in ls("docs"):
    w(f"- `docs/{n}`")
w("")

w("## tools/")
w("")
w("Run order for a full rebuild of the Japan pages is in `CLAUDE.md` (\"Generator scripts\"). Regenerating a page wipes edits made by later post-processors.")
w("")
w("| Script | What it does (first docstring line) |")
w("|---|---|")
scripts = sorted([n for n in ls("tools", ".py")], key=lambda n: (num_key(n), n))
for n in scripts:
    w(f"| `{n}` | {first_doc_line(os.path.join(ROOT, 'tools', n))} |")
other = [n for n in ls("tools") if not n.endswith(".py")]
for n in other:
    w(f"| `{n}` | data file read by the scripts above |")
w("")

w("## public/ pages")
w("")
top = ls("public", ".html")
pocket = [n for n in top if n.endswith("-pocket.html")]
rest = [n for n in top if n not in pocket]
w(f"**Top-level pages ({len(rest)}):** " + ", ".join(f"`{n}`" for n in rest))
w("")
w(f"**Pocket Guides ({len(pocket)}):** " + ", ".join(f"`{n}`" for n in pocket))
w("Each also has `<key>-sw.js` (service worker) and `<key>-pocket.webmanifest`.")
w("")
blog = ls("public/blog", ".html")
japan_keys = ("narita", "haneda", "kansai", "tokyo", "kyoto", "osaka", "japan")
jp = [n for n in blog if any(k in n for k in japan_keys)]
w(f"**Blog and guides (`public/blog/`, {len(blog)} pages).** Japan-related ({len(jp)}): " + ", ".join(f"`{n}`" for n in jp))
w("")
ws = ls("public/web-stories", ".html")
w(f"**Web stories ({len(ws)}):** " + ", ".join(f"`{n}`" for n in ws))
w("")
imgs = ls("public/images")
w(f"**Images:** {len(imgs)} files in `public/images/`; site icons and logos in `public/`.")
w("")
other_pub = [n for n in ls("public") if not n.endswith(".html") and not n.endswith("-sw.js") and not n.endswith(".webmanifest") and not n.endswith(".png")]
w("**Other public files:** " + ", ".join(f"`{n}`" for n in other_pub))
w("")
w("## How to save everything to disk")
w("")
w("```")
w("git clone git@github.com-packsmart:packsmartapp/packsmart.git   # or your usual remote alias")
w("```")
w("The Project notes are not in git: open the Claude Project \"Packsmart\" and download or copy the ones you want.")

os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("wrote", OUT, len(lines), "lines")
