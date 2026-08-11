# 生成火把头铸模贴图（修正版）：
# 铸模 = TCon 空白铸模贴图（满铺颗粒底板）+ 火把头部件形状位置镂空
from PIL import Image
import os

TCON = r'i:\.m\.minecraft\versions\1.20.1-Forge_47.3.22\tcon\assets\tconstruct\textures\item'
OUT = r'i:\.m\.minecraft\versions\1.20.1-Forge_47.3.22\thingpacks\Tinkers--Waste\assets\tinkers_waste\textures\item'
PART = OUT + r'\part\torch_head.png'

# 火把头部件形状（无 offset 模型，镂空用原位）
part = Image.open(PART).convert('RGBA')
ppx = part.load()
shape = {(x, y) for y in range(16) for x in range(16) if ppx[x, y][3] > 0}
print(f'火把头形状: {len(shape)} 像素')

for name, src in [('torch_head_sand_cast', 'sand_cast'),
                  ('torch_head_red_sand_cast', 'red_sand_cast'),
                  ('torch_head_gold_cast', 'cast')]:
    base_img = Image.open(TCON + rf'\{src}\blank.png').convert('RGBA')
    bpx = base_img.load()

    out = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    opx = out.load()
    n = 0
    for y in range(16):
        for x in range(16):
            r, g, b, a = bpx[x, y]
            if (x, y) in shape:
                continue            # 火把头形状位置挖洞
            opx[x, y] = (r, g, b, a)
            n += 1
    out.save(os.path.join(OUT, name + '.png'))
    print(f'{name}.png: 底板像素={n}, 镂空={256 - n}')
print('done')
