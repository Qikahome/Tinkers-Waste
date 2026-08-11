# -*- coding: utf-8 -*-
"""为 throwing_torch_duplicate 复制配方生成黏液材料变体。
模板: throwing_torch_duplicate/slime_ball.json
每个变体: 替换输入黏液材料 + 设置 result count, 输出到同目录下 <物品名>.json
"""
import json
import os

TEMPLATE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "data", "tinkers_waste", "recipes", "throwing_torch_duplicate", "slime_ball.json",
)
OUTPUT_DIR = os.path.dirname(TEMPLATE_PATH)

# (物品 id, 复制数量, 返还物品 (id, count) 或 None)
VARIANTS = [
    ("minecraft:slime_ball", 4, None),
    ("minecraft:slime_block", 36, None),
    ("tconstruct:earth_slime_bottle", 4, None),
    ("tconstruct:earth_congealed_slime", 16, None),
    ("tconstruct:ender_slime_ball", 16, None),
    ("tconstruct:ender_slime", 64, ("tconstruct:ender_slime_ball", 5)),
    ("tconstruct:ender_slime_bottle", 16, None),
    ("tconstruct:ender_congealed_slime", 64, None),
    ("tconstruct:ichor_slime_ball", 20, None),
    ("tconstruct:ichor_slime", 60, ("tconstruct:ichor_slime_ball", 6)),
    ("tconstruct:ichor_slime_bottle", 20, None),
    ("tconstruct:ichor_congealed_slime", 60, ("tconstruct:ichor_slime_ball", 1)),
    ("tconstruct:sky_slime_ball", 10, None),
    ("tconstruct:sky_slime", 60, ("tconstruct:sky_slime_ball", 3)),
    ("tconstruct:sky_slime_bottle", 10, None),
    ("tconstruct:sky_congealed_slime", 40, None),
]

with open(TEMPLATE_PATH, encoding="utf-8") as f:
    template = json.load(f)

for item_id, count, remainder in VARIANTS:
    # 深拷贝模板
    recipe = json.loads(json.dumps(template))
    # 第 0 个输入为黏液材料; 需要返还时用 remainder_override 包裹
    if remainder is not None:
        recipe["ingredients"][0] = {
            "type": "jsonmore:remainder_override",
            "ingredient": {"item": item_id},
            "remainder_override": {"id": remainder[0], "Count": remainder[1]},
        }
    else:
        recipe["ingredients"][0] = {"item": item_id}
    recipe["result"]["count"] = count

    file_name = item_id.split(":")[-1] + ".json"
    if file_name == "slime_ball.json":
        # 模板本身已存在且为手写格式, 跳过
        print(f"skip (template): {os.path.join(OUTPUT_DIR, file_name)}")
        continue
    out_path = os.path.join(OUTPUT_DIR, file_name)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(recipe, f, ensure_ascii=False, indent=4)
    print(f"wrote: {out_path}  (count={count})")
