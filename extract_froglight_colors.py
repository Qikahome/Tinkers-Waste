import io
import json
import os
import zipfile
from collections import Counter

from PIL import Image

JAR = r"i:\.m\.minecraft\versions\1.20.1-Forge_47.3.22\1.20.1-Forge_47.3.22.jar"
THINGPACK = r"i:\.m\.minecraft\versions\1.20.1-Forge_47.3.22\thingpacks\Tinkers--Waste"
MATERIALS_DIR = os.path.join(THINGPACK, "assets", "tinkers_waste", "tinkering", "materials")

FACES = ("top", "side")
TEXTURES = {
    "verdant": [f"assets/minecraft/textures/block/verdant_froglight_{f}.png" for f in FACES],
    "ochre": [f"assets/minecraft/textures/block/ochre_froglight_{f}.png" for f in FACES],
    "pearlescent": [f"assets/minecraft/textures/block/pearlescent_froglight_{f}.png" for f in FACES],
}
GREY_SLOTS = [0, 63, 102, 140, 178, 216, 255]


def lum(c):
    return round(0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2])


def scale(rgb, target_lum):
    s = target_lum / lum(rgb)
    return tuple(min(255, round(v * s)) for v in rgb)


def hexc(c):
    return f"FF{c[0]:02X}{c[1]:02X}{c[2]:02X}"


def build_palette(colors):
    """colors: 8 colors sorted by luminance asc. Drop the 3 brightest, keep the 5 darkest
    for the lightest 5 grey slots, derive the darkest 2 grey slots from the darkest kept color
    by arithmetic ladder, ensuring the darkest slot stays bright (~80-128)."""
    kept = colors[:5]
    lums = [lum(c) for c in kept]
    avg_diff = sum(lums[i + 1] - lums[i] for i in range(4)) / 4
    # widen the step if needed so the darkest slot is no darker than ~128
    step = max(round(avg_diff), (lums[0] - 128 + 1) // 2)
    step = max(step, 1)
    l63 = lums[0] - step
    l0 = max(lums[0] - 2 * step, 80)  # keep darkest reasonably bright
    if l63 <= l0:
        step = (lums[0] - 80) // 3 or 1
        l63 = lums[0] - step
        l0 = lums[0] - 2 * step
    levels = [(l0, scale(kept[0], l0)), (l63, scale(kept[0], l63))]
    levels += [(lums[i], kept[i]) for i in range(5)]
    return [{"color": hexc(rgb), "grey": grey} for grey, (lv, rgb) in zip(GREY_SLOTS, levels)]


def render_info(color, palette):
    return {
        "color": hexc(color),
        "fallbacks": ["rock"],
        "generator": {
            "supported_stats": ["tinkers_waste:torch_head"],
            "transformer": {
                "type": "tconstruct:recolor_sprite",
                "color_mapping": {
                    "type": "tconstruct:grey_to_color",
                    "palette": palette,
                },
            },
        },
    }


def main():
    infos = {}
    with zipfile.ZipFile(JAR) as z:
        for label, paths in TEXTURES.items():
            pixels = []
            for path in paths:
                img = Image.open(io.BytesIO(z.read(path))).convert("RGBA")
                w, h = img.size
                pixels.extend(img.getpixel((x, y)) for y in range(h) for x in range(w))
            opaque = [p for p in pixels if p[3] >= 128]
            counts = Counter(opaque)
            colors = sorted(counts.keys(), key=lum)  # darkest first
            print(f"=== {label} ({len(opaque)} opaque px, {len(counts)} colors) ===")
            for c, count in counts.most_common():
                print(f"  #{c[0]:02X}{c[1]:02X}{c[2]:02X}  rgb({c[0]},{c[1]},{c[2]})  lum={lum(c):3d}  count={count}")
            palette = build_palette(colors)
            # main color = grey 216 slot (kept[3])
            main_color = colors[3]
            infos[label] = render_info(main_color, palette)
            print(f"  -> palette: " + ", ".join(f"grey{p['grey']}:{p['color'][2:]}" for p in palette))

    # base material (no variant) uses the verdant render info; verdant variant keeps its own
    verdant = infos["verdant"]
    outputs = {
        os.path.join(MATERIALS_DIR, "froglight.json"): verdant,
        os.path.join(MATERIALS_DIR, "froglight", "verdant.json"): verdant,
        os.path.join(MATERIALS_DIR, "froglight", "ochre.json"): infos["ochre"],
        os.path.join(MATERIALS_DIR, "froglight", "pearlescent.json"): infos["pearlescent"],
    }
    for path, data in outputs.items():
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.write("\n")
        print(f"wrote {os.path.relpath(path, THINGPACK)}")


if __name__ == "__main__":
    main()
