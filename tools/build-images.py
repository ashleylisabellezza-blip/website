"""Build responsive image derivatives for the Bellezza redesign.

Usage (from the project root):

    python tools/build-images.py            # build whatever is out of date
    python tools/build-images.py --force    # rebuild everything
    python tools/build-images.py --only team,sheets
    python tools/build-images.py --strict   # exit 1 if a portrait's outer 8px
                                            # mean luma is above 3% (brief 2.6)

Groups (for --only): team, sheets, owners, brand, about, join, brows, slay, og

What it makes (all new files; no source image is modified or overwritten):

  team    assets/img/team/{slug}-{180,360,540}.{avif,webp,jpg}
          3:4 centre crop at native resolution, EXIF-transposed, metadata
          stripped, never upscaled. AVIF quality is searched downward until the
          file fits the budget in BUDGETS (540w <= 45KB, 180w <= 6KB).
          Also reports each portrait's outer-8px mean luma (brief wants <= 3%
          so tiles sit on #000). Faces are never regraded. The only fix is
          EDGE_FADES: a smooth edge-only fade to black on sides whose band was
          profiled as pure backdrop (taylor-f top, lisa-jeffries top), with a
          brightness guard that skips the fade if the band reaches the
          subject. Every other portrait that exceeds does so because the
          subject (arms, clothing, a white coat) touches the frame edge. The
          report names each offending edge and whether it looks like subject
          or backdrop (anything brighter than luma 40 within 24px of that
          edge counts as subject; a lifted grey backdrop can trip this).
  sheets  assets/img/team/contact-sheet-{1540,1100}.{avif,webp,jpg}  (7x4, all 28)
          assets/img/team/contact-sheet-800.{avif,webp,jpg}         (4x3, 12 people)
  owners  assets/img/team/{slug}-720.{avif,webp,jpg} for every 720-wide source, and
          {slug}-{native}.{avif,webp,jpg} for the narrower ones (emilie-600 ...)
  brand   assets/img/brand/wordmark.png, wordmark-on-dark.png (56px tall = 2x of
          a 28px header lockup), logo.png, logo-on-dark.png (#faf8f5)
  about   assets/img/about/team-group-{560,1120}.{avif,webp,jpg}  (from join-1.jpg,
          4:3, gentle de-vignette + clarity reduction)
  join    assets/img/join/{join-2,join-3,gallery-1..4}-{400,800}.{avif,webp,jpg}
          assets/img/join/gallery-3-sq-{400,800,900}.{avif,webp,jpg} (1:1 from the top),
          gallery-1-1200 and gallery-4-900 (native width, for the About bento)
  brows   assets/img/work/brows-{before,after}-{400,470}.{avif,webp,jpg}
          (the two photos cut out of services/bella-brows.png without the baked
          text; the source only has ~470px of clean width, so the large variant
          is 470w rather than 800w; nothing is upscaled)
  slay    assets/img/slay/shannon-{360,497}.{avif,webp,jpg} (source is 497 wide,
          so no 540), assets/img/slay/slay-logo-{240,480}.{png,webp}
  og      assets/img/og-image.jpg (1200x630)

Idempotent: an output is skipped when it exists and is newer than both its
source(s) and this script. Every run ends with a table of every output path,
its pixel size and byte size.

Requires Python 3 and Pillow with AVIF + WebP support. Standard library only
otherwise.
"""

from __future__ import annotations

import argparse
import io
import os
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageFilter, ImageOps, features

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "assets" / "img"
SCRIPT = Path(__file__).resolve()

BLACK = (0, 0, 0)
PAPER = (0xFA, 0xF8, 0xF5)

# Default team order (brief 5.4).
TEAM_ORDER = [
    "ashley-basham", "lisa-jeffries", "devon", "stephanie", "janet", "moriah",
    "emilie", "austyn", "lizbeth", "cherish", "liv", "taylor-f", "mya", "kat",
    "paige", "madison", "shelbi", "raegan", "rissa", "hope", "jesyca", "emma",
    "mia", "shannon-francis", "melissa", "aubree", "grace", "aeriannah",
]
MOBILE_SHEET = [
    "ashley-basham", "lisa-jeffries", "devon", "stephanie", "moriah", "emilie",
    "austyn", "paige", "madison", "jesyca", "emma", "mia",
]
OWNERS = ["ashley-basham", "lisa-jeffries"]
# Every portrait also gets a large variant (720w, or its native width): see build_owners.

PORTRAIT_WIDTHS = (180, 360, 540)
EDGE_PX = 8
EDGE_LIMIT = 3.0  # percent

# AVIF byte budgets by output key. Quality is lowered in steps until it fits.
KB = 1000  # budgets are decimal KB
BUDGETS = {
    "portrait-180": 6 * KB,
    "portrait-360": 20 * KB,
    "portrait-540": 45 * KB,
    "portrait-720": 70 * KB,
    "sheet-1540": 160 * KB,
    "sheet-1100": 95 * KB,
    "sheet-800": 70 * KB,
}
AVIF_Q_START = 60
AVIF_Q_MIN = 28
WEBP_Q = 78
JPEG_Q = 80

# Crop boxes measured on the source files (see module docstring).
# logo.png is 786x257: EST. 2009 sits at y 51-78, x 324-448; the wordmark
# (BELLEZZA + "& Co" script) spans y 72-186; the frame's side rules restart at
# y 187 and the tagline is y 192-214.
LOGO_WORDMARK_BOX = (14, 72, 772, 187)
LOGO_EST_BOX = (300, 40, 460, 92)  # cleared inside the wordmark crop
LOGO_TAGLINE_BOX = (150, 188, 625, 218)
WORDMARK_H = 56  # 2x of the 28px desktop header lockup

# bella-brows.png is 1080x800. AFTER photo interior x 106-985, y 133-496 with
# the AFTER pill at x 807-1040, y >= 381; BEFORE photo interior x 203-855,
# y 518-786 with the BEFORE pill at x 153-356, y 717-763. These two boxes frame
# the same eye and brow in each photo at the same size, clear of pills,
# borders and rounded corners.
BROWS_BEFORE_BOX = (362, 522, 832, 782)
BROWS_AFTER_BOX = (297, 177, 767, 437)

report_rows: list[tuple[str, int, int, int, str]] = []
edge_rows: list[tuple[str, float, float, dict]] = []
FORCE = False


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


def up_to_date(outputs: list[Path], sources: list[Path]) -> bool:
    if FORCE:
        return False
    if not all(o.exists() for o in outputs):
        return False
    newest_src = max([s.stat().st_mtime for s in sources] + [SCRIPT.stat().st_mtime])
    return min(o.stat().st_mtime for o in outputs) >= newest_src


def record(path: Path, note: str = "") -> None:
    with Image.open(path) as im:
        w, h = im.size
    report_rows.append((rel(path), w, h, path.stat().st_size, note))


def load_rgb(path: Path) -> Image.Image:
    """Open, apply EXIF orientation, convert to sRGB RGB, drop metadata."""
    im = Image.open(path)
    im = ImageOps.exif_transpose(im)
    icc = im.info.get("icc_profile")
    if icc:
        try:
            from PIL import ImageCms
            prof = ImageCms.ImageCmsProfile(io.BytesIO(icc))
            if "srgb" not in ImageCms.getProfileDescription(prof).lower():
                im = ImageCms.profileToProfile(
                    im.convert("RGB"), prof, ImageCms.createProfile("sRGB"),
                    outputMode="RGB")
        except Exception:
            pass
    im = im.convert("RGB")
    clean = Image.new("RGB", im.size)
    clean.paste(im)
    return clean


def crop_to_ratio(im: Image.Image, rw: int, rh: int, anchor_y: float = 0.5,
                  anchor_x: float = 0.5) -> Image.Image:
    """Largest crop of ratio rw:rh. anchor 0 = top/left, 1 = bottom/right."""
    w, h = im.size
    if w * rh > h * rw:  # too wide
        nw = round(h * rw / rh)
        x = round((w - nw) * anchor_x)
        return im.crop((x, 0, x + nw, h))
    nh = round(w * rh / rw)
    y = round((h - nh) * anchor_y)
    return im.crop((0, y, w, y + nh))


def cover(im: Image.Image, w: int, h: int, anchor_y: float = 0.35) -> Image.Image:
    """Crop to the box ratio then resize to exactly w x h."""
    return crop_to_ratio(im, w, h, anchor_y=anchor_y).resize((w, h), Image.LANCZOS)


def resize_w(im: Image.Image, w: int) -> Image.Image:
    if w >= im.width:
        return im.copy()
    h = round(im.height * w / im.width)
    return im.resize((w, h), Image.LANCZOS)


def encode_avif(im: Image.Image, path: Path, budget: int | None) -> str:
    q = AVIF_Q_START
    while True:
        buf = io.BytesIO()
        im.save(buf, "AVIF", quality=q, speed=4, subsampling="4:2:0")
        if budget is None or buf.tell() <= budget or q <= AVIF_Q_MIN:
            break
        q -= 4
    path.write_bytes(buf.getvalue())
    over = "  OVER BUDGET" if budget and buf.tell() > budget else ""
    return f"avif q{q}" + (f" (budget {budget // KB}KB)" if budget else "") + over


def save_set(im: Image.Image, base: Path, budget_key: str | None = None) -> list[Path]:
    """Write base.avif / base.webp / base.jpg from an RGB image."""
    base.parent.mkdir(parents=True, exist_ok=True)
    avif, webp, jpg = (base.with_name(base.name + e) for e in (".avif", ".webp", ".jpg"))
    note = encode_avif(im, avif, BUDGETS.get(budget_key) if budget_key else None)
    im.save(webp, "WEBP", quality=WEBP_Q, method=6)
    im.save(jpg, "JPEG", quality=JPEG_Q, optimize=True, progressive=True,
            subsampling="4:2:0")
    print(f"  wrote {rel(base)}.{{avif,webp,jpg}}  [{note}]")
    return [avif, webp, jpg]


def set_paths(base: Path) -> list[Path]:
    return [base.with_name(base.name + e) for e in (".avif", ".webp", ".jpg")]


def build_set(base: Path, sources: list[Path], make, budget_key: str | None = None) -> None:
    outs = set_paths(base)
    if not up_to_date(outs, sources):
        save_set(make(), base, budget_key)
    for o in outs:
        record(o)


def mono_png(alpha: Image.Image, color: tuple[int, int, int], path: Path) -> None:
    """Save a single-colour image as an indexed PNG whose palette index is the
    alpha value (exact colour, full 8-bit alpha, much smaller than RGBA)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    a = alpha.convert("L")
    p = Image.frombytes("P", a.size, a.tobytes())
    p.putpalette(list(color) * 256)
    p.save(path, "PNG", optimize=True, transparency=bytes(range(256)))
    print(f"  wrote {rel(path)}")


# --------------------------------------------------------------------------
# a) team portraits
# --------------------------------------------------------------------------

def team_slugs() -> list[str]:
    return sorted(p.stem for p in (IMG / "team").glob("*.jpg")
                  if "-" not in p.stem or not p.stem.rsplit("-", 1)[-1].isdigit())


# Edge-only backdrop fades. Each entry darkens one side with a smooth ramp
# (black at the frame edge, untouched at `depth` px in). The bands were
# profiled row by row and contain only a smooth backdrop: taylor-f's hair
# starts at y ~115 and lisa-jeffries' at y ~48. As a safety net a fade is
# skipped (and reported) if any pixel in its band is brighter than
# FADE_MAX_LUMA, which would mean it reaches the subject.
EDGE_FADES = {
    "taylor-f": {"top": 64},
    "lisa-jeffries": {"top": 32},
}
FADE_MAX_LUMA = 72
fade_notes: dict[str, str] = {}


def edge_fade(slug: str, im: Image.Image) -> Image.Image:
    w, h = im.size
    for side, depth in EDGE_FADES.get(slug, {}).items():
        box = {"top": (0, 0, w, depth), "bottom": (0, h - depth, w, h),
               "left": (0, 0, depth, h), "right": (w - depth, 0, w, h)}[side]
        peak = max(im.convert("L").crop(box).get_flattened_data())
        if peak > FADE_MAX_LUMA:
            fade_notes[f"{slug} {side}"] = (f"SKIPPED: band peak luma {peak} > "
                                            f"{FADE_MAX_LUMA} (would touch subject)")
            continue
        ramp = []
        for i in range(depth):
            t = (i + 0.5) / depth
            ramp.append(round(255 * t * t * (3 - 2 * t)))
        mask = Image.new("L", im.size, 255)
        if side in ("top", "bottom"):
            line = Image.new("L", (1, depth))
            line.putdata(ramp if side == "top" else ramp[::-1])
            mask.paste(line.resize((w, depth)), box[:2])
        else:
            line = Image.new("L", (depth, 1))
            line.putdata(ramp if side == "left" else ramp[::-1])
            mask.paste(line.resize((depth, h)), box[:2])
        im = ImageChops.multiply(im, Image.merge("RGB", (mask, mask, mask)))
        fade_notes[f"{slug} {side}"] = (f"faded {depth}px backdrop band "
                                        f"(peak luma {peak})")
    return im


def portrait(slug: str) -> Image.Image:
    return edge_fade(slug, crop_to_ratio(load_rgb(IMG / "team" / f"{slug}.jpg"), 3, 4))


def srgb_to_linear(v: float) -> float:
    v /= 255.0
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


LIN = [srgb_to_linear(i) for i in range(256)]


def edge_stats(im: Image.Image) -> tuple[float, float, dict]:
    """Mean of the outer EDGE_PX band: (luma %, linear luminance %, per side)."""
    w, h = im.size
    e = EDGE_PX
    boxes = {"top": (0, 0, w, e), "bottom": (0, h - e, w, h),
             "left": (0, e, e, h - e), "right": (w - e, e, w, h - e)}
    luma = im.convert("L")
    total = n = tot_lin = 0.0
    sides = {}
    for name, box in boxes.items():
        vals = list(luma.crop(box).get_flattened_data())
        s = sum(vals)
        # likely cause: anything clearly brighter than a backdrop (luma > 40)
        # within 24px of this edge means the subject reaches the frame edge.
        deep = {"top": (0, 0, w, 24), "bottom": (0, h - 24, w, h),
                "left": (0, 0, 24, h), "right": (w - 24, 0, w, h)}[name]
        dv = list(luma.crop(deep).get_flattened_data())
        bright = sum(1 for v in dv if v > 40) / len(dv)
        sides[name] = (s / len(vals) / 2.55, "subject" if bright > 0.02 else "backdrop")
        total += s
        tot_lin += sum(LIN[v] for v in vals)
        n += len(vals)
    return total / n / 2.55, tot_lin / n * 100, sides


def build_team() -> None:
    print("team portraits")
    for slug in team_slugs():
        src = IMG / "team" / f"{slug}.jpg"
        crop = portrait(slug)
        edge_rows.append((slug, *edge_stats(crop)))
        for w in PORTRAIT_WIDTHS:
            if w > crop.width:
                continue
            build_set(IMG / "team" / f"{slug}-{w}", [src],
                      lambda w=w: resize_w(crop, w), f"portrait-{w}")


def build_owners() -> None:
    print("large portraits (720w, or the native width when the source is narrower)")
    # Option B's 3-up team cards render about 382 CSS px wide, so every card
    # offers its source's full width (section 0: 2x the rendered width, up to
    # the native size). 720w for 720-wide sources; the narrower sources get
    # one set at their own width (e.g. emilie-600). Nothing is upscaled.
    for slug in team_slugs():
        src = IMG / "team" / f"{slug}.jpg"
        crop = portrait(slug)
        w = min(720, crop.width)
        if w <= 540:
            continue
        build_set(IMG / "team" / f"{slug}-{w}", [src],
                  lambda c=crop, w=w: resize_w(c, w), "portrait-720")


# --------------------------------------------------------------------------
# b) contact sheets
# --------------------------------------------------------------------------

def compose_sheet(slugs: list[str], cols: int, rows: int, width: int,
                  height: int | None = None) -> Image.Image:
    if height is None:
        height = round(width * rows * 4 / (cols * 3))
    sheet = Image.new("RGB", (width, height), BLACK)
    xs = [round(i * width / cols) for i in range(cols + 1)]
    ys = [round(j * height / rows) for j in range(rows + 1)]
    for i, slug in enumerate(slugs):
        c, r = i % cols, i // cols
        tw, th = xs[c + 1] - xs[c], ys[r + 1] - ys[r]
        sheet.paste(cover(portrait(slug), tw, th), (xs[c], ys[r]))
    return sheet


def build_sheets() -> None:
    print("contact sheets")
    srcs_all = [IMG / "team" / f"{s}.jpg" for s in TEAM_ORDER]
    srcs_m = [IMG / "team" / f"{s}.jpg" for s in MOBILE_SHEET]
    for w in (1540, 1100):
        build_set(IMG / "team" / f"contact-sheet-{w}", srcs_all,
                  lambda w=w: compose_sheet(TEAM_ORDER, 7, 4, w), f"sheet-{w}")
    build_set(IMG / "team" / "contact-sheet-800", srcs_m,
              lambda: compose_sheet(MOBILE_SHEET, 4, 3, 800), "sheet-800")


# --------------------------------------------------------------------------
# c) brand
# --------------------------------------------------------------------------

def logo_alpha() -> Image.Image:
    return Image.open(IMG / "logo.png").convert("RGBA").getchannel("A")


def wordmark_alpha() -> Image.Image:
    a = logo_alpha()
    x0, y0, x1, y1 = LOGO_WORDMARK_BOX
    wm = a.crop(LOGO_WORDMARK_BOX)
    ex0, ey0, ex1, ey1 = LOGO_EST_BOX
    wm.paste(0, (ex0 - x0, ey0 - y0, ex1 - x0, ey1 - y0))
    bbox = wm.point(lambda v: 255 if v > 8 else 0).getbbox()
    return wm.crop(bbox)


def build_brand() -> None:
    print("brand")
    src = IMG / "logo.png"
    out = IMG / "brand"
    targets = {
        "wordmark.png": ("wm", BLACK),
        "wordmark-on-dark.png": ("wm", PAPER),
        "logo.png": ("logo", BLACK),
        "logo-on-dark.png": ("logo", PAPER),
    }
    paths = [out / n for n in targets]
    if not up_to_date(paths, [src]):
        wm = wordmark_alpha()
        wm = wm.resize((round(wm.width * WORDMARK_H / wm.height), WORDMARK_H), Image.LANCZOS)
        full = logo_alpha()
        for name, (kind, color) in targets.items():
            mono_png(wm if kind == "wm" else full, color, out / name)
    for p in paths:
        record(p)


# --------------------------------------------------------------------------
# d) about + join photos
# --------------------------------------------------------------------------

def radial_gain(size: tuple[int, int], strength: float, start: float = 0.35) -> Image.Image:
    """L mask holding 255*(gain-1): 0 inside `start` (fraction of the
    centre-to-corner distance), rising smoothly to `strength` at the corners."""
    sw, sh = 160, 120
    data = []
    for y in range(sh):
        for x in range(sw):
            dx = (x + 0.5) / sw - 0.5
            dy = (y + 0.5) / sh - 0.5
            r = ((dx * dx + dy * dy) ** 0.5) / (0.5 ** 0.5)
            t = min(1.0, max(0.0, (r - start) / (1 - start)))
            t = t * t * (3 - 2 * t)
            data.append(round(255 * strength * t))
    m = Image.new("L", (sw, sh))
    m.putdata(data)
    return m.resize(size, Image.BICUBIC)


def soften_grade(im: Image.Image, devignette: float = 0.30, clarity: float = 0.30) -> Image.Image:
    """Gentle global correction for the phone-HDR look: lift the vignetted
    corners with a smooth radial gain and remove part of the mid-scale local
    contrast ('clarity') band. No colour or skin changes."""
    m = radial_gain(im.size, devignette)
    boost = ImageChops.multiply(im, Image.merge("RGB", (m, m, m)))
    im = ImageChops.add(im, boost)
    small = im.filter(ImageFilter.GaussianBlur(4))
    large = im.filter(ImageFilter.GaussianBlur(40))
    band = ImageChops.subtract(small, large, scale=1, offset=128)
    band = band.point(lambda v: round(128 + clarity * (v - 128)))
    return ImageChops.subtract(im, band, scale=1, offset=128)


def build_about() -> None:
    print("about group photo")
    src = IMG / "join" / "join-1.jpg"

    def base() -> Image.Image:
        im = soften_grade(load_rgb(src))
        # 1120x840 from 1200x900: centred horizontally, and the 60 spare rows
        # are taken from the ceiling (top) so no feet are cut.
        return crop_to_ratio(im.crop((40, 60, 1160, 900)), 4, 3)

    cache: dict[str, Image.Image] = {}

    def get() -> Image.Image:
        if "b" not in cache:
            cache["b"] = base()
        return cache["b"]

    for w in (560, 1120):
        build_set(IMG / "about" / f"team-group-{w}", [src], lambda w=w: resize_w(get(), w))


def build_join() -> None:
    print("join / gallery photos")
    for name in ("join-2", "join-3", "gallery-1", "gallery-2", "gallery-3", "gallery-4"):
        src = IMG / "join" / f"{name}.jpg"
        for w in (400, 800):
            build_set(IMG / "join" / f"{name}-{w}", [src],
                      lambda s=src, w=w: resize_w(load_rgb(s), w))
    # gallery-3 is only ever shown as a 1:1 crop from the top (DESIGN-OPTIONS section 0):
    # it keeps the sign and both faces and drops the retail packaging and the
    # "$70" counter card lower in the frame. 900x1200 source -> 900x900 -> 800/400.
    src = IMG / "join" / "gallery-3.jpg"
    for w in (400, 800, 900):
        build_set(IMG / "join" / f"gallery-3-sq-{w}", [src],
                  lambda s=src, w=w: resize_w(crop_to_ratio(load_rgb(s), 1, 1, anchor_y=0.0), w))
    # Option B's About bento shows gallery-1 at two thirds and gallery-4 at one third of
    # the container, so both also get a set at their native width (2x rule, never upscaled).
    for name, w in (("gallery-1", 1200), ("gallery-4", 900)):
        src = IMG / "join" / f"{name}.jpg"
        build_set(IMG / "join" / f"{name}-{w}", [src], lambda s=src, w=w: resize_w(load_rgb(s), w))


# --------------------------------------------------------------------------
# e) brows, f) slay
# --------------------------------------------------------------------------

def build_brows() -> None:
    print("bella brows before/after")
    src = IMG / "services" / "bella-brows.png"
    for label, box in (("before", BROWS_BEFORE_BOX), ("after", BROWS_AFTER_BOX)):
        native = box[2] - box[0]
        for w in (400, native):
            build_set(IMG / "work" / f"brows-{label}-{w}", [src],
                      lambda b=box, w=w: resize_w(load_rgb(src).crop(b), w))


def build_slay() -> None:
    print("slay")
    src = IMG / "services" / "shannon-francis.jpg"
    native = Image.open(src).width
    for w in (360, min(540, native)):
        build_set(IMG / "slay" / f"shannon-{w}", [src],
                  lambda w=w: resize_w(load_rgb(src), w))
    logo = IMG / "services" / "slay-logo.png"
    for w in (240, 480):
        png = IMG / "slay" / f"slay-logo-{w}.png"
        webp = png.with_suffix(".webp")
        if not up_to_date([png, webp], [logo]):
            png.parent.mkdir(parents=True, exist_ok=True)
            im = Image.open(logo).convert("RGBA")
            im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
            clean = Image.new("RGBA", im.size)
            clean.paste(im)
            clean.save(png, "PNG", optimize=True)
            clean.save(webp, "WEBP", lossless=True, method=6)
            print(f"  wrote {rel(png)} + .webp")
        record(png)
        record(webp)


# --------------------------------------------------------------------------
# h) OG image
# --------------------------------------------------------------------------

def build_og() -> None:
    print("og image")
    out = IMG / "og-image.jpg"
    srcs = [IMG / "logo.png"] + [IMG / "team" / f"{s}.jpg" for s in TEAM_ORDER]
    if not up_to_date([out], srcs):
        W, H, PANEL = 1200, 630, 480
        og = Image.new("RGB", (W, H), PAPER)
        # right: 6x4 contact sheet on black, full bleed (first 24 in team order)
        og.paste(compose_sheet(TEAM_ORDER[:24], 6, 4, W - PANEL, H), (PANEL, 0))
        # left: black wordmark centred, logo tagline beneath
        wm = wordmark_alpha()
        ww = 360
        wm = wm.resize((ww, round(wm.height * ww / wm.width)), Image.LANCZOS)
        tag = logo_alpha().crop(LOGO_TAGLINE_BOX)
        tag = tag.crop(tag.point(lambda v: 255 if v > 8 else 0).getbbox())
        tw = 236
        tag = tag.resize((tw, round(tag.height * tw / tag.width)), Image.LANCZOS)
        gap = 22
        block_h = wm.height + gap + tag.height
        y = (H - block_h) // 2
        ink = Image.new("RGB", (W, H), BLACK)
        og.paste(ink.crop((0, 0) + wm.size), ((PANEL - ww) // 2, y), wm)
        og.paste(ink.crop((0, 0) + tag.size), ((PANEL - tw) // 2, y + wm.height + gap), tag)
        og.save(out, "JPEG", quality=86, optimize=True, progressive=True)
        print(f"  wrote {rel(out)}")
    record(out)


# --------------------------------------------------------------------------

GROUPS = {
    "team": build_team, "sheets": build_sheets, "owners": build_owners,
    "brand": build_brand, "about": build_about, "join": build_join,
    "brows": build_brows, "slay": build_slay, "og": build_og,
}


def main() -> int:
    global FORCE
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--force", action="store_true", help="rebuild everything")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 when a portrait edge is above 3%% luma")
    ap.add_argument("--only", default="", help="comma list: " + ",".join(GROUPS))
    args = ap.parse_args()
    FORCE = args.force

    for f in ("avif", "webp"):
        if not features.check(f):
            print(f"Pillow lacks {f.upper()} support", file=sys.stderr)
            return 2

    groups = [g.strip() for g in args.only.split(",") if g.strip()] or list(GROUPS)
    for g in groups:
        if g not in GROUPS:
            print(f"unknown group {g!r}", file=sys.stderr)
            return 2
    if "team" not in groups:
        # edge report still wanted for --strict; compute cheaply.
        if args.strict:
            for slug in team_slugs():
                edge_rows.append((slug, *edge_stats(portrait(slug))))
    for g in groups:
        GROUPS[g]()

    print("\noutputs")
    print(f"{'path':58s} {'w x h':>11s} {'bytes':>8s}")
    for path, w, h, size, _ in report_rows:
        print(f"{path:58s} {f'{w}x{h}':>11s} {size:8d}")

    failed = []
    if edge_rows:
        print(f"\nportrait outer-{EDGE_PX}px mean (luma % of 255; linear luminance %); limit {EDGE_LIMIT}%")
        for slug, luma, lin, sides in edge_rows:
            flag = ""
            if luma > EDGE_LIMIT:
                hot = [f"{k} {v:.1f}% ({cause})" for k, (v, cause) in
                       sorted(sides.items(), key=lambda kv: -kv[1][0]) if v > EDGE_LIMIT]
                flag = f"  EXCEEDS by {luma - EDGE_LIMIT:.2f} pts: " + ", ".join(hot)
                failed.append(slug)
            side_s = " ".join(f"{k[0]}={v:.1f}" for k, (v, _) in sides.items())
            print(f"  {slug:18s} {luma:5.2f}%  lin {lin:5.2f}%  [{side_s}]{flag}")
        print(f"  {len(failed)} of {len(edge_rows)} exceed {EDGE_LIMIT}%. Not regraded: "
              "'subject' edges cannot be darkened without touching the person.")
        for k, v in fade_notes.items():
            print(f"  edge fade {k}: {v}")
    return 1 if (args.strict and failed) else 0


if __name__ == "__main__":
    sys.exit(main())
