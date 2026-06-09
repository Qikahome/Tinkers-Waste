"""Fix: gauge should have same capacity as tank."""
import json, os

BLOCK_DIR = "things/tinkers_waste/block"

CAPS = {
    "iron":      {"fuel": 11000, "ingot": 11520},
    "gold":      {"fuel": 18000, "ingot": 18360},
    "diamond":   {"fuel": 25000, "ingot": 25920},
    "debris":    {"fuel": 27000, "ingot": 27360},
    "netherite": {"fuel": 34000, "ingot": 34560},
}

for fname in os.listdir(BLOCK_DIR):
    if not fname.endswith(".json"):
        continue
    parts = fname[:-5].split("_")
    tier = parts[0]
    if tier not in CAPS:
        continue
    ttype = "_".join(parts[1:])
    if "fuel" in ttype:
        key = "fuel"
    elif "ingot" in ttype:
        key = "ingot"
    else:
        continue
    fp = os.path.join(BLOCK_DIR, fname)
    with open(fp, "r", encoding="utf-8") as f:
        data = json.load(f)
    old = data.get("capacity")
    data["capacity"] = CAPS[tier][key]
    with open(fp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  {fname}: {old} -> {data['capacity']}")

print("Done!")
