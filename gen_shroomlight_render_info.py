import io
import json
import os
import zipfile
from collections import Counter

from PIL import Image

JAR = r"i:\.m\.minecraft\versions\1.20.1-Forge_47.3.22\1.20.1-Forge_47.3.22.jar"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "tinkers_waste", "tinkering", "materials", "shroomlight.json")
GREY_SLOTS = [0, 63, 102, 140, 178, 216, 255]


def lum(c):
    return round(0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2])


def scale(rgb, target):
    s = target / lum(rgb)
    return tuple(min(255, round(v * s)) for v in rgb)


def hexc(c):
    return f"FF{c[0]:02X}{c[1]:02X}{c[2]:02X}"


with zipfile.ZipFile(JAR) as z:
    img = Image.open(io.BytesIO(z.read("assets/minecraft/textures/block/shroomlight.png"))).convert("RGBA")
    w, h = img.size
    px = [img.getpixel((x, y)) for y in range(h) for x in range(w)]
opaque = [p for p in px if p[3] >= 128]
colors = sorted(Counter(opaque).keys(), key=lum)
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
palette = [{"color": hexc(rgb), "grey": g} for g, (lv, rgb) in zip(GREY_SLOTS, levels)]
data = {
    "color": hexc(colors[3]),
    "fallbacks": ["rock"],
    "generator": {
        "supported_stats": ["tinkers_waste:torch_head", "tconstruct:repair_kit"],
        "transformer": {
            "type": "tconstruct:recolor_sprite",
            "color_mapping": {"type": "tconstruct:grey_to_color", "palette": palette},
        },
    },
}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
    f.write("\n")
print("wrote", OUT)
for p in palette:
    print(f"  grey{p['grey']}: #{p['color'][2:]}")
