"""Fix item type for all tank blocks: add jsonmore:fluid_tank type."""
import json
import os

BLOCK_DIR = "things/tinkers_waste/block"

for fname in os.listdir(BLOCK_DIR):
    if not fname.endswith(".json"):
        continue
    fp = os.path.join(BLOCK_DIR, fname)
    with open(fp, "r", encoding="utf-8") as f:
        data = json.load(f)
    if data.get("type") != "jsonmore:fluid_tank":
        continue
    if data.get("item") == {} or data.get("item") is None:
        data["item"] = {"type": "jsonmore:fluid_tank"}
        with open(fp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"  Fixed {fname}")
    else:
        print(f"  Skipped {fname} (already has item config)")

print("Done!")
