import json
import os
from collections import Counter

from PIL import Image

ASSETS = r"i:\.m\.minecraft\versions\1.20.1-Forge_47.3.22\assets\minecraft\textures\block"
THINGPACK = r"i:\.m\.minecraft\versions\1.20.1-Forge_47.3.22\thingpacks\Tinkers--Waste"
MATERIALS_DIR = os.path.join(THINGPACK, "assets", "tinkers_waste", "tinkering", "materials")

# soul-themed block textures, read from the extracted vanilla assets dir
TEXTURES = {
    "soul_lantern": "soul_lantern.png",
    "soul_torch": "soul_torch.png",
    "soul_campfire_fire": "soul_campfire_fire.png",
    "soul_fire_0": "soul_fire_0.png",
    "soul_fire_1": "soul_fire_1.png",
    "soul_sand": "soul_sand.png",
    "soul_soil": "soul_soil.png",
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
    """Same ladder logic as the froglight script."""
    kept = colors[:5]
    lums = [lum(c) for c in kept]
    avg_diff = sum(lums[i + 1] - lums[i] for i in range(4)) / 4
    step = max(round(avg_diff), (lums[0] - 128 + 1) // 2)
    step = max(step, 1)
    l63 = lums[0] - step
    l0 = max(lums[0] - 2 * step, 80)
    if l63 <= l0:
        step = (lums[0] - 80) // 3 or 1
        l63 = lums[0] - step
        l0 = lums[0] - 2 * step
    levels = [(l0, scale(kept[0], l0)), (l63, scale(kept[0], l63))]
    levels += [(lums[i], kept[i]) for i in range(5)]
    return [{"color": hexc(rgb), "grey": grey} for grey, (lv, rgb) in zip(GREY_SLOTS, levels)]


def render_info(color, palette, supported_stats):
    return {
        "color": hexc(color),
        "fallbacks": ["coal"],
        "generator": {
            "supported_stats": supported_stats,
            "transformer": {
                "type": "tconstruct:recolor_sprite",
                "color_mapping": {
                    "type": "tconstruct:grey_to_color",
                    "palette": palette,
                },
            },
        },
    }


SUPPORTED_STATS = [
    "tinkers_waste:torch_head",
    "tconstruct:binding",
    "tconstruct:arrow_head",
    "tconstruct:handle",
    "tconstruct:head",
    "tconstruct:grip",
]


def main():
    stats = {}
    for label, name in TEXTURES.items():
        path = os.path.join(ASSETS, name)
        if not os.path.exists(path):
            print(f"=== {label}: MISSING at {path}, skipped ===")
            continue
        img = Image.open(path).convert("RGBA")
        w, h = img.size
        pixels = [img.getpixel((x, y)) for y in range(h) for x in range(w)]
        opaque = [p for p in pixels if p[3] >= 128]
        counts = Counter(opaque)
        colors = sorted(counts.keys(), key=lum)  # darkest first
        print(f"=== {label} ({w}x{h}, {len(opaque)} opaque px, {len(counts)} colors) ===")
        for c, count in counts.most_common(10):
            print(f"  #{c[0]:02X}{c[1]:02X}{c[2]:02X}  rgb({c[0]},{c[1]},{c[2]})  lum={lum(c):3d}  count={count}")
        stats[label] = (colors, counts)

    # build a single soul palette from the pure flame texture (campfire fire layer),
    # main color = flame center blue #13AFB3 (2nd darkest)
    source = "soul_campfire_fire"
    colors, counts = stats[source]
    palette = build_palette(colors)
    main_color = colors[1]
    print(f"\n=== palette source: {source} ===")
    print(f"  -> main color: #{main_color[0]:02X}{main_color[1]:02X}{main_color[2]:02X}")
    print("  -> palette: " + ", ".join(f"grey{p['grey']}:{p['color'][2:]}" for p in palette))

    data = render_info(main_color, palette, SUPPORTED_STATS)
    path = os.path.join(MATERIALS_DIR, "soul_coal.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    print(f"wrote {os.path.relpath(path, THINGPACK)}")


if __name__ == "__main__":
    main()
