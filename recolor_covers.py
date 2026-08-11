from PIL import Image
import colorsys

TORCH = r"i:\.m\.minecraft\versions\1.20.1-Forge_47.3.22\thingpacks\Tinkers--Waste\assets\tinkers_waste\textures\item\part\torch_head_tinkers_waste_coal.png"
BASE = r"i:\.m\.minecraft\versions\1.20.1-Forge_47.3.22\thingpacks\Tinkers--Waste\assets\tinkers_waste\book\images\covers"
TARGETS = [
    BASE + r"\guide_cover.png",
    BASE + r"\guide_pages.png",
]

# 提取火把头色相
torch_img = Image.open(TORCH).convert("RGBA")
torch_px = torch_img.load()
torch_colors = []
for y in range(torch_img.height):
    for x in range(torch_img.width):
        r, g, b, a = torch_px[x, y]
        if a < 30:
            continue
        if r > 240 and g > 240 and b > 240:
            continue
        torch_colors.append((r/255, g/255, b/255))

torch_colors.sort(key=lambda c: 0.299*c[0] + 0.587*c[1] + 0.114*c[2])
mid = torch_colors[len(torch_colors)//2]
target_h, target_s, target_v = colorsys.rgb_to_hsv(*mid)
print(f"火把头目标色相 H={target_h:.3f} S={target_s:.3f} V={target_v:.3f}")

# 三段映射：
# 255-180: 不变（纸张）
# 180-100: 中间调，正常染色
# 100-0:   暗部映射到 255-180 区间（比中间调更亮，发光边缘）
for OUT in TARGETS:
    book_img = Image.open(OUT).convert("RGBA")
    book_px = book_img.load()

    for y in range(book_img.height):
        for x in range(book_img.width):
            r, g, b, a = book_px[x, y]
            if a == 0:
                continue
            lum = 0.299 * r + 0.587 * g + 0.114 * b

            if lum > 180:
                continue
            elif lum > 100:
                h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
                nr, ng, nb = colorsys.hsv_to_rgb(target_h, target_s, v)
            else:
                new_lum = 255 - int((lum / 100) * 75)
                v = new_lum / 255
                nr, ng, nb = colorsys.hsv_to_rgb(target_h, target_s, v)

            book_px[x, y] = (int(nr*255), int(ng*255), int(nb*255), a)

    book_img.save(OUT)
    data = [p for p in book_img.getdata() if p[3] > 0]
    avg = tuple(sum(c[i] for c in data) // len(data) for i in range(4))
    print(f"输出: {OUT} ({book_img.width}x{book_img.height})")
    print(f"avg: {avg}")
