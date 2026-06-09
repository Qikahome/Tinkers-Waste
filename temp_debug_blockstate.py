"""Temporarily point blockstates to TCon original models for debugging."""
import json
import os

BASE = "assets/tinkers_waste"

# Map each iron tank to its original TCon block model (the one used in the model's parent)
ORIGINALS = {
    "iron_fuel_tank":            "tconstruct:block/smeltery/tank/fuel_tank",
    "iron_fuel_gauge":           "tconstruct:block/smeltery/tank/fuel_gauge",
    "iron_ingot_tank":           "tconstruct:block/smeltery/tank/ingot_tank",
    "iron_ingot_gauge":          "tconstruct:block/smeltery/tank/ingot_gauge",
    "iron_scorched_fuel_tank":   "tconstruct:block/foundry/tank/fuel_tank",
    "iron_scorched_fuel_gauge":  "tconstruct:block/foundry/tank/fuel_gauge",
    "iron_scorched_ingot_tank":  "tconstruct:block/foundry/tank/ingot_tank",
    "iron_scorched_ingot_gauge": "tconstruct:block/foundry/tank/ingot_gauge",
}

for block_name, model in ORIGINALS.items():
    bs = {"variants": {"": {"model": model}}}
    with open(f"{BASE}/blockstates/{block_name}.json", "w", encoding="utf-8") as f:
        json.dump(bs, f, indent=2, ensure_ascii=False)
    print(f"  {block_name} -> {model}")

print("Done!")
