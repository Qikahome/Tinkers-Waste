"""Generate tank models using tank_with_trim / tank_knob_with_trim templates."""
import json
import os

BASE = "assets/tinkers_waste"
TRIM_TEMPLATES = {
    "fuel_tank":  "tinkers_waste:block/template/tank_knob_with_trim",
    "fuel_gauge": "tinkers_waste:block/template/tank_with_trim",
    "ingot_tank": "tinkers_waste:block/template/tank_knob_with_trim",
    "ingot_gauge":"tinkers_waste:block/template/tank_with_trim",
}

TIERS = ["iron", "gold", "diamond", "debris", "netherite"]

# TCon original model parents (to resolve correct textures path)
SEARED_PARENTS = {
    "fuel_tank":  "tconstruct:block/smeltery/tank/fuel_tank",
    "fuel_gauge": "tconstruct:block/smeltery/tank/fuel_gauge",
    "ingot_tank": "tconstruct:block/smeltery/tank/ingot_tank",
    "ingot_gauge":"tconstruct:block/smeltery/tank/ingot_gauge",
}
SCORCHED_PARENTS = {
    "fuel_tank":  "tconstruct:block/foundry/tank/fuel_tank",
    "fuel_gauge": "tconstruct:block/foundry/tank/fuel_gauge",
    "ingot_tank": "tconstruct:block/foundry/tank/ingot_tank",
    "ingot_gauge":"tconstruct:block/foundry/tank/ingot_gauge",
}


def make_textures(tier, tank_type, is_scorched):
    """Resolve texture paths matching what TCon original models use."""
    if is_scorched:
        top = "tconstruct:block/foundry/tank/"
        side = "tconstruct:block/foundry/tank/"
    else:
        top = "tconstruct:block/smeltery/tank/"
        side = "tconstruct:block/smeltery/tank/"

    if tank_type in ("fuel_tank", "ingot_tank"):
        top += "tank_top"
        if tank_type == "fuel_tank":
            side += "fuel_tank"
        else:
            side += "ingot_tank"
    else:  # gauge
        top += "gauge_top"
        if tank_type == "fuel_gauge":
            side += "fuel_gauge"
        else:
            side += "ingot_gauge"

    return {
        "top": top,
        "side": side,
        "trim": f"tinkers_waste:block/{tier}_tank_trim"
    }


def gen_all():
    for tier in TIERS:
        for key, parent in SEARED_PARENTS.items():
            block_name = f"{tier}_{key}"
            ttype = key

            model = {
                "parent": TRIM_TEMPLATES[ttype],
                "textures": make_textures(tier, ttype, False)
            }
            with open(f"{BASE}/models/block/{block_name}.json", "w", encoding="utf-8") as f:
                json.dump(model, f, indent=2, ensure_ascii=False)

            bs = {"variants": {"": {"model": f"tinkers_waste:block/{block_name}"}}}
            with open(f"{BASE}/blockstates/{block_name}.json", "w", encoding="utf-8") as f:
                json.dump(bs, f, indent=2, ensure_ascii=False)

            bf = {"variants": {"": "tconstruct:templates/tank"}}
            with open(f"{BASE}/mantle/model/block_fluids/{block_name}.json", "w", encoding="utf-8") as f:
                json.dump(bf, f, indent=2, ensure_ascii=False)

            item = {"parent": f"tinkers_waste:block/{block_name}"}
            with open(f"{BASE}/models/item/{block_name}.json", "w", encoding="utf-8") as f:
                json.dump(item, f, indent=2, ensure_ascii=False)

            print(f"  {block_name}")

        # Scorched variants
        for key, parent in SCORCHED_PARENTS.items():
            block_name = f"{tier}_scorched_{key}"
            ttype = key

            model = {
                "parent": TRIM_TEMPLATES[ttype],
                "textures": make_textures(tier, ttype, True)
            }
            with open(f"{BASE}/models/block/{block_name}.json", "w", encoding="utf-8") as f:
                json.dump(model, f, indent=2, ensure_ascii=False)

            bs = {"variants": {"": {"model": f"tinkers_waste:block/{block_name}"}}}
            with open(f"{BASE}/blockstates/{block_name}.json", "w", encoding="utf-8") as f:
                json.dump(bs, f, indent=2, ensure_ascii=False)

            bf = {"variants": {"": "tconstruct:templates/tank"}}
            with open(f"{BASE}/mantle/model/block_fluids/{block_name}.json", "w", encoding="utf-8") as f:
                json.dump(bf, f, indent=2, ensure_ascii=False)

            item = {"parent": f"tinkers_waste:block/{block_name}"}
            with open(f"{BASE}/models/item/{block_name}.json", "w", encoding="utf-8") as f:
                json.dump(item, f, indent=2, ensure_ascii=False)

            print(f"  {block_name}")

    # Clean up no-longer-needed per-tier trim overlay models
    for tier in TIERS:
        fp = f"{BASE}/models/block/{tier}_tank_trim.json"
        if os.path.exists(fp):
            os.remove(fp)
            print(f"  Removed {tier}_tank_trim.json")

    print("Done!")


if __name__ == "__main__":
    os.makedirs(f"{BASE}/models/block", exist_ok=True)
    os.makedirs(f"{BASE}/blockstates", exist_ok=True)
    os.makedirs(f"{BASE}/mantle/model/block_fluids", exist_ok=True)
    os.makedirs(f"{BASE}/models/item", exist_ok=True)
    gen_all()
