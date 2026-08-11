from PIL import Image
import os

BASE = os.path.dirname(os.path.abspath(__file__))
MC_ASSETS = os.path.join(os.path.dirname(os.path.dirname(BASE)), "assets", "minecraft", "textures")
BLOCK_DIR = os.path.join(BASE, "assets", "tinkers_waste", "textures", "block")
ITEM_DIR = os.path.join(BASE, "assets", "tinkers_waste", "textures", "item")
os.makedirs(BLOCK_DIR, exist_ok=True)
os.makedirs(ITEM_DIR, exist_ok=True)

# coal palette from tinkers_waste/materials/coal.json (grey -> color)
COAL_PALETTE = [
    (0, (16, 16, 21)),
    (32, (31, 23, 33)),
    (64, (28, 28, 30)),
    (96, (38, 30, 36)),
    (128, (37, 37, 37)),
    (160, (46, 46, 46)),
    (192, (50, 50, 50)),
    (224, (54, 54, 54)),
    (255, (57, 62, 70)),
]

# soul_coal palette from tinkers_waste/materials/soul_coal.json (grey -> color)
SOUL_PALETTE = [
    (0, (7, 124, 126)),
    (63, (7, 133, 136)),
    (102, (8, 143, 146)),
    (140, (19, 175, 179)),
    (178, (35, 192, 198)),
    (216, (91, 227, 232)),
    (255, (124, 242, 245)),
]


def coal_to_grey(color):
    # reverse-lookup coal palette: nearest palette color -> its grey
    best_g = 0
    best_d = None
    for g, c in COAL_PALETTE:
        d = sum((color[i] - c[i]) ** 2 for i in range(3))
        if best_d is None or d < best_d:
            best_d = d
            best_g = g
    return best_g


def grey_to_soul(g):
    # linear interpolation across palette slots
    if g <= SOUL_PALETTE[0][0]:
        return SOUL_PALETTE[0][1]
    for i in range(1, len(SOUL_PALETTE)):
        g0, c0 = SOUL_PALETTE[i - 1]
        g1, c1 = SOUL_PALETTE[i]
        if g <= g1:
            t = (g - g0) / (g1 - g0)
            return tuple(round(c0[k] + (c1[k] - c0[k]) * t) for k in range(3))
    return SOUL_PALETTE[-1][1]


def remap(src_rel, dst_path, use_grey_to_soul):
    src = Image.open(src_rel if os.path.isabs(src_rel) else os.path.join(MC_ASSETS, src_rel)).convert("RGBA")
    px = src.load()
    w, h = src.size
    out = Image.new("RGBA", (w, h))
    opx = out.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a == 0:
                opx[x, y] = (0, 0, 0, 0)
                continue
            if use_grey_to_soul:
                grey = round(0.2126 * r + 0.7152 * g + 0.0722 * b)
            else:
                grey = coal_to_grey((r, g, b))
            sr, sg, sb = grey_to_soul(grey)
            opx[x, y] = (sr, sg, sb, a)
    out.save(dst_path)
    print("wrote", os.path.basename(dst_path))


remap("item/coal.png", os.path.join(ITEM_DIR, "soul_coal.png"), use_grey_to_soul=False)
# TCon fake material block texture (grayscale palette) -> soul palette
remap(os.path.join(BASE, "..", "..", "tcon", "assets", "tconstruct", "textures", "block", "storage", "fallback.png"),
      os.path.join(BLOCK_DIR, "soul_coal_block.png"), use_grey_to_soul=True)
