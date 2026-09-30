"""Build the self-hosted WOFF2 web font for the Bellezza & Co. site, Option C
(Bronze & Sand, docs/DESIGN-OPTIONS.md section C2: Manrope only, 400 and 600).

Usage (from the project root):

    python tools/build-fonts.py              # download sources if missing, build, verify
    python tools/build-fonts.py --refresh    # re-download the source TTFs first
    python tools/build-fonts.py --print-css  # ... and print the CSS fonts block

What it does:
  1. Makes sure the official variable TTF from the google/fonts GitHub repo is in
     tools/font-src/ (downloads it from raw.githubusercontent.com if missing),
     together with the family's OFL.txt licence.
  2. Instances it with fontTools.varLib.instancer, keeping the wght axis but
     limiting its range:
       Manrope roman : wght 400-700 (the site uses 400 and 600)
  3. Subsets to Latin (the Google Fonts "latin" range plus a few extra punctuation
     code points) keeping only the OpenType features the site can use.
  4. Writes WOFF2 files to assets/fonts/ and copies the OFL licences next to them.
  5. Parses every output back with fontTools, checks glyph coverage for a test
     string and prints the size of each file against the budget in the brief.
  6. With --print-css: prints the CSS fonts block for assets/css/styles.css (to go
     between /* fonts:start */ and /* fonts:end */; this script never edits the
     stylesheet). It holds the @font-face rule, whose URLs carry
     ?v=HASH, the same sha1[:8] content hash tools/build-partials.py puts on the font
     preloads, so preload and stylesheet request the same URL and each font downloads
     once. It also holds the metric-matched fallback faces computed by tools/font-metrics.py.

Needs only Python 3 + fontTools + brotli. Idempotent: re-running overwrites the outputs
with identical results.
"""

import hashlib
import importlib.util
import io
import shutil
import sys
import urllib.request
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "tools" / "font-src"
OUT = ROOT / "assets" / "fonts"

RAW = "https://raw.githubusercontent.com/google/fonts/main/ofl/"
SOURCES = {
    "Manrope[wght].ttf": RAW + "manrope/Manrope%5Bwght%5D.ttf",
    "Manrope-OFL.txt": RAW + "manrope/OFL.txt",
}

# Google Fonts "latin" unicode-range, plus the extras the brief asks for.
# U+2000-206F already covers en/em dashes, curly quotes, bullet, ellipsis.
UNICODE_RANGE = (
    "U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, "
    "U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, "
    "U+FEFF, U+FFFD"
)

# Features kept in the subset (only those present in each font survive anyway):
# fontTools' default shaping set (ccmp, locl, mark, mkmk, calt, frac, ...) plus the
# typographic features the site uses. Manrope's default figures are proportional;
# prices and hours switch on its tnum feature (font-variant-numeric: tabular-nums).
EXTRA_FEATURES = ["kern", "liga", "lnum", "tnum", "onum", "pnum", "case"] + [
    "ss%02d" % i for i in range(1, 21)
]
FEATURES = sorted(set(subset.Options().layout_features) | set(EXTRA_FEATURES))

BUILDS = [
    # (source, output, axis limits, budget in KB)
    ("Manrope[wght].ttf", "manrope-var-latin.woff2", {"wght": (400, 700)}, 30),
]

LICENCES = [
    ("Manrope-OFL.txt", "manrope-OFL.txt"),
]

TEST_STRING = "Beauty & relaxation, tailored to you. $37–60 • é"

# (output file, CSS family, font-style, font-weight range)
FACES = [
    ("manrope-var-latin.woff2", "Manrope", "normal", "400 700"),
]


def parse_ranges(spec):
    """Turn a CSS unicode-range string into a sorted list of code points."""
    cps = set()
    for part in spec.split(","):
        part = part.strip().upper().replace("U+", "")
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-")
            cps.update(range(int(a, 16), int(b, 16) + 1))
        else:
            cps.add(int(part, 16))
    return sorted(cps)


def fetch_sources(refresh=False):
    SRC.mkdir(parents=True, exist_ok=True)
    for name, url in SOURCES.items():
        dest = SRC / name
        if dest.exists() and not refresh:
            continue
        print("download", url)
        with urllib.request.urlopen(url, timeout=60) as r:
            data = r.read()
        dest.write_bytes(data)


def clamp_limits(font, limits):
    """Clamp the requested axis limits to what the variable font actually offers."""
    axes = {a.axisTag: a for a in font["fvar"].axes}
    out = {}
    for tag, (lo, hi) in limits.items():
        ax = axes[tag]
        lo2, hi2 = max(lo, ax.minValue), min(hi, ax.maxValue)
        default = min(max(ax.defaultValue, lo2), hi2)
        if (lo2, hi2) != (lo, hi):
            print("  note: %s %g-%g clamped to font range %g-%g" % (tag, lo, hi, lo2, hi2))
        out[tag] = instancer.AxisTriple(lo2, default, hi2)
    return out


def build_one(src_name, out_name, limits):
    font = TTFont(SRC / src_name)
    axis_limits = clamp_limits(font, limits)
    font = instancer.instantiateVariableFont(
        font, axis_limits, updateFontNames=False, optimize=True
    )
    # Round-trip through bytes so the subsetter sees fully compiled tables
    # (subsetting the in-memory instancer result trips over lazy gvar data).
    tmp = io.BytesIO()
    font.recalcTimestamp = False  # keep head.modified from the source: reproducible output
    font.save(tmp)
    tmp.seek(0)
    font = TTFont(tmp, recalcTimestamp=False)

    opts = subset.Options()
    opts.layout_features = FEATURES
    opts.flavor = "woff2"
    opts.name_IDs = ["*"]          # keep names (licence/copyright strings included)
    opts.name_languages = [0x409]
    opts.notdef_outline = True
    opts.recalc_bounds = True
    opts.drop_tables += ["DSIG"]
    opts.hinting = False           # hinting adds size and is ignored by most browsers
    opts.desubroutinize = False

    sub = subset.Subsetter(opts)
    sub.populate(unicodes=parse_ranges(UNICODE_RANGE))
    sub.subset(font)

    OUT.mkdir(parents=True, exist_ok=True)
    buf = io.BytesIO()
    font.flavor = "woff2"
    font.recalcTimestamp = False
    font.save(buf)
    (OUT / out_name).write_bytes(buf.getvalue())
    return axis_limits


def verify(out_name, budget_kb):
    path = OUT / out_name
    size_kb = path.stat().st_size / 1024
    font = TTFont(path)
    cmap = font.getBestCmap()
    missing = sorted({c for c in TEST_STRING if ord(c) not in cmap})
    axes = ", ".join(
        "%s %g-%g" % (a.axisTag, a.minValue, a.maxValue) for a in font["fvar"].axes
    ) if "fvar" in font else "static"
    feats = sorted({fr.FeatureTag for fr in font["GSUB"].table.FeatureList.FeatureRecord}
                   | {fr.FeatureTag for fr in font["GPOS"].table.FeatureList.FeatureRecord}
                   ) if "GSUB" in font and "GPOS" in font else []
    status = "OK" if size_kb <= budget_kb else "OVER BUDGET"
    print("%-34s %6.1f KB / %d KB  %-11s glyphs=%d  axes: %s" % (
        out_name, size_kb, budget_kb, status, len(font.getGlyphOrder()), axes))
    print("    features: %s" % " ".join(feats))
    if missing:
        print("    MISSING glyphs for: %r" % "".join(missing))
    return size_kb <= budget_kb and not missing


def content_hash(path):
    """8-char cache-busting hash. Must match content_hash() in tools/build-partials.py."""
    return hashlib.sha1(path.read_bytes()).hexdigest()[:8]


def fallback_css():
    """Fallback @font-face rules, computed by tools/font-metrics.py (never hand-typed)."""
    spec = importlib.util.spec_from_file_location(
        "font_metrics", ROOT / "tools" / "font-metrics.py")
    fm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fm)
    return fm.css(fm.compute(), compact=True)


def css_block():
    lines = ["/* generated by python tools/build-fonts.py --print-css; do not edit by hand */"]
    for out_name, family, style, weight in FACES:
        lines.append(
            "@font-face{font-family:'%s';src:url('../fonts/%s?v=%s') format('woff2');"
            "font-style:%s;font-weight:%s;font-display:swap;unicode-range:%s}"
            % (family, out_name, content_hash(OUT / out_name), style, weight, UNICODE_RANGE))
    lines.append("/* metric-matched fallbacks (tools/font-metrics.py) */")
    lines.append(fallback_css())
    return "\n".join(lines)


def main():
    refresh = "--refresh" in sys.argv
    fetch_sources(refresh)
    for src_name, out_name, limits, _ in BUILDS:
        print("build", out_name)
        build_one(src_name, out_name, limits)
    for src_name, out_name in LICENCES:
        shutil.copyfile(SRC / src_name, OUT / out_name)
    print()
    ok = True
    for _, out_name, _, budget in BUILDS:
        ok &= verify(out_name, budget)
    print()
    print("coverage test string: %s" % ascii(TEST_STRING))
    print("ALL OK" if ok else "PROBLEMS FOUND (see above)")
    if ok and "--print-css" in sys.argv:
        print()
        print(css_block())
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
