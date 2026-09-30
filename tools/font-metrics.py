"""Compute metric-matched fallback @font-face overrides for the self-hosted web fonts.

Usage (from the project root, after `python tools/build-fonts.py`):

    python tools/font-metrics.py              # print a table + paste-ready CSS

Option B (docs/DESIGN-OPTIONS.md B2): 'Arsenal Fallback' and 'Mulish Fallback'
(both on Arial), each with size-adjust and the ascent / descent / line-gap
overrides, computed rather than guessed.

Method (the one used by Next.js next/font and Capsize):
  * Measure the average advance width, in em, of a representative lowercase
    English sample string (spaces included) in the web font and in the local
    fallback font.
        size-adjust      = web_avg_em / fallback_avg_em
  * Express the web font's vertical metrics in the fallback's adjusted em:
        ascent-override  = web_ascent  / (web_upm * size-adjust)
        descent-override = |web_descent| / (web_upm * size-adjust)
        line-gap-override= web_lineGap / (web_upm * size-adjust)
    The web font's ascent/descent come from OS/2 typo metrics when its
    USE_TYPO_METRICS bit is set, otherwise from hhea.

Web fonts are measured from the shipped WOFF2 files in assets/fonts/ (falling back
to the source TTFs in tools/font-src/). The variable fonts are measured at the
default wght 400 (Mulish also at 700, against Arial Bold). Fallback metrics are
read from C:\\Windows\\Fonts\\arial.ttf and arialbd.ttf (override the folder with
the WINFONTS environment variable).

tools/build-fonts.py imports compute() and css() from this file to generate the
fonts block in assets/css/styles.css (python tools/build-fonts.py --print-css).

Plain stdlib + fontTools. Read-only: it writes nothing.
"""

import os
import sys
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "assets" / "fonts"
SRC = ROOT / "tools" / "font-src"
WINFONTS = Path(os.environ.get("WINFONTS", r"C:\Windows\Fonts"))

# Representative lowercase English running text (letter mix close to normal
# English frequencies, with word spaces). Used only for width measurement.
SAMPLE = (
    "the salon is open most days of the week and our stylists take time to talk "
    "through every appointment with each guest before they begin so that the cut "
    "colour and finish suit the way you live and how much time you want to spend "
    "on your hair in the morning which is why so many people come back to us year "
    "after year for their regular visits and for the big occasions in their lives"
)

PAIRS = [
    # (fallback family name, web font file, source file, web wght measured,
    #  fallback local() names, fallback file, css font-style, css font-weight)
    # Arial is the fallback base everywhere: it exists on Windows and macOS, so the
    # overrides below hold on both (Optima and Candara stay later in the CSS stack).
    ("Arsenal Fallback", "arsenal-400-latin.woff2", "Arsenal-Regular.ttf", 400,
     ["Arial", "ArialMT"], "arial.ttf", "normal", "400"),
    ("Mulish Fallback", "mulish-var-latin.woff2", "Mulish[wght].ttf", 400,
     ["Arial", "ArialMT"], "arial.ttf", "normal", "400"),
    # Labels and names use Mulish 600, buttons 700. CSS weight matching sends 600 and
    # 700 requests to this 700 face, so the fallback never synthesizes a fake bold.
    ("Mulish Fallback", "mulish-var-latin.woff2", "Mulish[wght].ttf", 700,
     ["Arial Bold", "Arial-BoldMT"], "arialbd.ttf", "normal", "700"),
]


def load_web_font(woff2, src, opsz, wght):
    path = FONTS / woff2
    if not path.exists():
        path = SRC / src
    font = TTFont(path)
    if "fvar" in font:
        loc = {}
        for ax in font["fvar"].axes:
            if ax.axisTag == "wght":
                loc["wght"] = min(max(wght, ax.minValue), ax.maxValue)
            elif ax.axisTag == "opsz":
                loc["opsz"] = min(max(opsz, ax.minValue), ax.maxValue)
            else:
                loc[ax.axisTag] = ax.defaultValue
        font = instancer.instantiateVariableFont(font, loc)
    return font, path


def vertical_metrics(font):
    os2, hhea = font["OS/2"], font["hhea"]
    if os2.fsSelection & (1 << 7):  # USE_TYPO_METRICS
        return os2.sTypoAscender, os2.sTypoDescender, os2.sTypoLineGap
    return hhea.ascent, hhea.descent, hhea.lineGap


def avg_width_em(font, text):
    cmap = font.getBestCmap()
    hmtx = font["hmtx"]
    upm = font["head"].unitsPerEm
    missing = {c for c in text if ord(c) not in cmap}
    if missing:
        raise SystemExit("font lacks glyphs for %r" % "".join(sorted(missing)))
    return sum(hmtx[cmap[ord(c)]][0] for c in text) / len(text) / upm


def pct(x):
    return ("%.2f" % (x * 100)).rstrip("0").rstrip(".") + "%"


def compute(opsz=48):
    rows = []
    for family, woff2, src, wght, local_names, fb_file, style, weight in PAIRS:
        web, web_path = load_web_font(woff2, src, opsz, wght)
        fb = TTFont(WINFONTS / fb_file)
        upm = web["head"].unitsPerEm
        asc, desc, gap = vertical_metrics(web)
        web_avg = avg_width_em(web, SAMPLE)
        fb_avg = avg_width_em(fb, SAMPLE)
        size_adjust = web_avg / fb_avg
        rows.append({
            "family": family,
            "web": web_path.name,
            "fallback": fb_file,
            "local": local_names,
            "style": style,
            "weight": weight,
            "wght": wght,
            "web_avg": web_avg,
            "fb_avg": fb_avg,
            "size_adjust": size_adjust,
            "ascent": asc / (upm * size_adjust),
            "descent": abs(desc) / (upm * size_adjust),
            "line_gap": gap / (upm * size_adjust),
        })
    return rows


def css(rows, compact=False):
    """Paste-ready @font-face rules. compact=True gives one rule per line."""
    out = []
    for r in rows:
        src = ", ".join("local('%s')" % n for n in r["local"])
        if compact:
            out.append(
                "@font-face{font-family:'%s';src:%s;font-style:%s;font-weight:%s;"
                "size-adjust:%s;ascent-override:%s;descent-override:%s;line-gap-override:%s}"
                % (r["family"], src, r["style"], r["weight"], pct(r["size_adjust"]),
                   pct(r["ascent"]), pct(r["descent"]), pct(r["line_gap"])))
            continue
        out.append(
            "@font-face {\n"
            "  font-family: '%s';\n"
            "  src: %s;\n"
            "  font-style: %s;\n"
            "  font-weight: %s;\n"
            "  size-adjust: %s;\n"
            "  ascent-override: %s;\n"
            "  descent-override: %s;\n"
            "  line-gap-override: %s;\n"
            "}" % (r["family"], src, r["style"], r["weight"], pct(r["size_adjust"]),
                   pct(r["ascent"]), pct(r["descent"]), pct(r["line_gap"]))
        )
    return "\n".join(out)


def main():
    opsz = 48
    if "--opsz" in sys.argv:
        opsz = float(sys.argv[sys.argv.index("--opsz") + 1])
    rows = compute(opsz)
    print("Sample: %d chars\n" % len(SAMPLE))
    print("%-24s %-38s %-12s %8s %8s %8s %8s %8s %8s" % (
        "fallback", "web font @wght", "vs", "web em", "fb em", "size", "ascent", "descent", "gap"))
    for r in rows:
        print("%-24s %-38s %-12s %8.4f %8.4f %8s %8s %8s %8s" % (
            r["family"], "%s @%d" % (r["web"], r["wght"]), r["fallback"], r["web_avg"], r["fb_avg"],
            pct(r["size_adjust"]), pct(r["ascent"]), pct(r["descent"]), pct(r["line_gap"])))
    print()
    print(css(rows))


if __name__ == "__main__":
    main()
