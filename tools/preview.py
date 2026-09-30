"""Assemble the design-comparison preview site (used by .github/workflows/preview.yml).

Every design lives on its own git branch (listed in preview/designs.json). This
script takes one checked-out folder per branch, rebuilds it, and writes a single
static site:

    _site/index.html           chooser page linking every design
    _site/<slug>/...           one full copy of the site per design

Preview copies are kept out of search engines (noindex), their links are made to
work inside a sub-folder, and each page gets a slim bar to jump to the same page
in another design. Nothing here changes the real site.

Usage (CI does this; locally you can too):
    python tools/preview.py --designs preview/designs.json --src-root <dir with one folder per slug> --out _site --base /website/
"""
import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys

SKIP_DIRS = {'.git', '.github', 'tools', 'docs', 'preview', '.playwright-mcp', '.worktrees'}  # top level only
SKIP_ANYWHERE = {'__pycache__', 'node_modules'}  # assets/docs (the PDFs) must still be copied
SKIP_FILES = {'netlify.toml', '_redirects', '_headers', 'README.md', 'IMAGE-MANIFEST.txt', 'PAGE-TEMPLATE.html',
              '.gitignore', '.gitattributes', 'robots.txt', 'sitemap.xml'}

BAR_CSS = """<style id="preview-bar-css">
.preview-bar{position:relative;z-index:1000;display:flex;flex-wrap:wrap;align-items:center;gap:6px 14px;padding:8px 16px;background:#1c1c1c;color:#e7e2d9;font:500 13px/1.4 system-ui,-apple-system,Segoe UI,sans-serif;letter-spacing:.02em}
.preview-bar b{color:#b8985f;font-weight:600}
.preview-bar nav{display:flex;flex-wrap:wrap;gap:4px}
.preview-bar a{color:#e7e2d9;text-decoration:none;padding:4px 10px;border:1px solid rgb(231 226 217/.3);border-radius:999px}
.preview-bar a:hover{border-color:#b8985f;color:#fff}
.preview-bar a[aria-current]{background:#b8985f;border-color:#b8985f;color:#1c1c1c}
.preview-bar .pv-home{margin-left:auto;border:0;text-decoration:underline;padding:4px 0}
</style>"""


def run_build(src):
    """Re-stamp partials and structured data so dates and hours are current."""
    for script in ('build-partials.py', 'build-schema.py'):
        path = os.path.join(src, 'tools', script)
        if os.path.exists(path):
            subprocess.run([sys.executable, path], cwd=src, check=True)


def copy_site(src, dst):
    for base, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d not in SKIP_ANYWHERE
                   and not (base == src and (d in SKIP_DIRS or d.startswith('.')))]
        rel = os.path.relpath(base, src)
        for f in files:
            if base == src and (f in SKIP_FILES or f.startswith('_qa')):
                continue
            os.makedirs(os.path.join(dst, rel), exist_ok=True)
            shutil.copy2(os.path.join(base, f), os.path.join(dst, rel, f))


def bar_html(designs, current, page):
    links = []
    for d in designs:
        cur = ' aria-current="page"' if d['slug'] == current['slug'] else ''
        links.append(f'<a href="../{d["slug"]}/{page}"{cur} title="{html.escape(d["name"])}">'
                     f'{html.escape(d["label"])}</a>')
    return (f'<div class="preview-bar" role="region" aria-label="Design preview">'
            f'<span>Previewing <b>{html.escape(current["label"])}</b> · {html.escape(current["name"])}</span>'
            f'<nav aria-label="Switch design">{"".join(links)}</nav>'
            f'<a class="pv-home" href="../index.html">All options</a></div>')


def transform(path, designs, current, base_path):
    page = os.path.basename(path)
    s = open(path, encoding='utf-8').read()
    # keep previews out of search results
    s = re.sub(r'<meta name="robots"[^>]*>\s*', '', s)
    s = re.sub(r'<link rel="canonical"[^>]*>\s*', '', s)
    s = s.replace('<head>', '<head>\n<meta name="robots" content="noindex, nofollow">', 1)
    # root-relative URLs assume the site sits at "/"; here it sits in a sub-folder
    s = re.sub(r'(action|href)="/(?!/)', r'\1="', s)  # turns <base href="/"> into href=""
    s = s.replace('<base href="">', f'<base href="{base_path}{current["slug"]}/">')
    s = s.replace('</head>', BAR_CSS + '\n</head>', 1)
    s = re.sub(r'(<body\b[^>]*>)', lambda m: m.group(1) + '\n' + bar_html(designs, current, page), s, count=1)
    open(path, 'w', encoding='utf-8', newline='\n').write(s)


def chooser(designs, out):
    cards = ''.join(
        f'<li><a href="{d["slug"]}/index.html"><span class="lbl">{html.escape(d["label"])}</span>'
        f'<span class="nm">{html.escape(d["name"])}</span><span class="bl">{html.escape(d.get("blurb", ""))}</span>'
        f'<span class="go">Open {html.escape(d["label"])} &rarr;</span></a></li>' for d in designs)
    page = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow"><title>Bellezza &amp; Co. · Design options</title>
<style>
*{{box-sizing:border-box}}body{{margin:0;background:#faf8f5;color:#1c1c1c;font:400 17px/1.6 system-ui,-apple-system,Segoe UI,sans-serif}}
main{{max-width:1200px;margin:0 auto;padding:clamp(24px,5vw,72px) clamp(20px,4vw,48px)}}
.eb{{font-size:13px;letter-spacing:.3em;text-transform:uppercase;color:#7a6232;margin:0 0 12px}}
h1{{font:400 clamp(2rem,1.4rem + 3vw,3.6rem)/1.1 Georgia,serif;margin:0 0 16px}}
p.lead{{max-width:60ch;color:#555;margin:0 0 40px}}
ul{{list-style:none;margin:0;padding:0;display:grid;gap:20px;grid-template-columns:repeat(auto-fit,minmax(260px,1fr))}}
a{{display:grid;gap:8px;height:100%;padding:28px;background:#fff;border:1px solid #e7e2d9;color:inherit;text-decoration:none}}
a:hover{{border-color:#9c7f4c}}a:focus-visible{{outline:3px solid #1c1c1c;outline-offset:3px}}
.lbl{{font-size:13px;letter-spacing:.3em;text-transform:uppercase;color:#7a6232}}
.nm{{font:400 1.5rem/1.2 Georgia,serif}}.bl{{color:#555;font-size:15px}}.go{{margin-top:8px;font-weight:600;color:#1c1c1c}}
</style></head><body><main>
<p class="eb">Bellezza &amp; Co. · private preview</p>
<h1>Design options</h1>
<p class="lead">The same real content, prices and photos in each design. Open one, then use the bar at the top of every page to switch to the same page in another design. These previews are hidden from search engines; forms don't send here.</p>
<ul>{cards}</ul>
</main></body></html>
"""
    open(os.path.join(out, 'index.html'), 'w', encoding='utf-8', newline='\n').write(page)
    open(os.path.join(out, '.nojekyll'), 'w').close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--designs', required=True)
    ap.add_argument('--src-root', required=True, help='folder containing one checked-out folder per design slug')
    ap.add_argument('--out', required=True)
    ap.add_argument('--base', default='/website/', help='URL path the preview site is served from')
    ap.add_argument('--no-build', action='store_true')
    a = ap.parse_args()
    designs = [d for d in json.load(open(a.designs, encoding='utf-8'))['designs']
               if os.path.isdir(os.path.join(a.src_root, d['slug']))]
    if os.path.exists(a.out):
        shutil.rmtree(a.out)
    os.makedirs(a.out)
    for d in designs:
        src = os.path.join(a.src_root, d['slug'])
        if not a.no_build:
            run_build(src)
        dst = os.path.join(a.out, d['slug'])
        copy_site(src, dst)
        for f in os.listdir(dst):
            if f.endswith('.html'):
                transform(os.path.join(dst, f), designs, d, a.base)
        print(f'{d["label"]}: {d["branch"]} -> {d["slug"]}/')
    chooser(designs, a.out)
    print(f'preview site written to {a.out} ({len(designs)} designs)')


if __name__ == '__main__':
    main()
