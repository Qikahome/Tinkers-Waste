"""
Generate tank upgrade and melting recipes for Tinkers--Waste.
Run from thingpacks/Tinkers--Waste directory.

Generates:
  1. crafting/ - workbench upgrade recipes (matching Extended-Storage chest patterns)
  2. smithing/ - netherite upgrade recipes (smithing_transform)
  3. item_application/ - interaction upgrade recipes
  4. melting/ - smeltery melting recipes
"""

import json
import os

CRAFTING_DIR = "data/tinkers_waste/recipes/generated/crafting"
SMITHING_DIR = "data/tinkers_waste/recipes/generated/smithing"
APPLICATION_DIR = "data/tinkers_waste/recipes/generated/item_application"
MELTING_DIR = "data/tinkers_waste/recipes/generated/smeltery/melting"

TANK_TYPES = [
    "fuel_tank", "fuel_gauge", "ingot_tank", "ingot_gauge",
    "scorched_fuel_tank", "scorched_fuel_gauge", "scorched_ingot_tank", "scorched_ingot_gauge",
]

TANK_CONDITION = {
    "type": "forge:or",
    "values": [
        {"type": "jsonmore:gamerule", "rule": "tinkers_waste.enable_extended_tanks"},
        {"type": "forge:mod_loaded", "modid": "extended_storage"}
    ]
}

CONDITION_MESSAGE = "tinkers_waste.recipe.disabled"

EXTENDED_ONLY_CONDITIONS = [
    {"type": "forge:mod_loaded", "modid": "extended_storage"}
]


def wrap_condition(ingredient: dict) -> dict:
    """Wrap an ingredient with jsonmore:condition for runtime gamerule check."""
    return {
        "type": "jsonmore:condition",
        "condition": TANK_CONDITION,
        "ingredient": ingredient,
        "message": CONDITION_MESSAGE
    }

# -------- TConstruct base tank melt values --------
SEARED_BASE = {
    "fuel_tank":  {"result": (2000, "tconstruct:seared_stone"), "byproducts": [(1000, "tconstruct:molten_glass")], "temp": 600, "time": 160},
    "fuel_gauge": {"result": (1000, "tconstruct:seared_stone"), "byproducts": [(5000, "tconstruct:molten_glass")], "temp": 600, "time": 107},
    "ingot_tank": {"result": (1500, "tconstruct:seared_stone"), "byproducts": [(3000, "tconstruct:molten_glass")], "temp": 600, "time": 134},
    "ingot_gauge":{"result": (1000, "tconstruct:seared_stone"), "byproducts": [(5000, "tconstruct:molten_glass")], "temp": 600, "time": 107},
}

SCORCHED_BASE = {
    "fuel_tank":  {"result": (2000, "tconstruct:scorched_stone"), "byproducts": [(100, "tconstruct:molten_quartz")], "temp": 500, "time": 150},
    "fuel_gauge": {"result": (1000, "tconstruct:scorched_stone"), "byproducts": [(500, "tconstruct:molten_quartz")], "temp": 500, "time": 100},
    "ingot_tank": {"result": (1500, "tconstruct:scorched_stone"), "byproducts": [(300, "tconstruct:molten_quartz")], "temp": 500, "time": 125},
    "ingot_gauge":{"result": (1000, "tconstruct:scorched_stone"), "byproducts": [(500, "tconstruct:molten_quartz")], "temp": 500, "time": 100},
}

TIER_METALS = {
    "iron":      {"byproducts": [(720, "tconstruct:molten_iron")],                         "temp": 800,  "time": 160},
    "gold":      {"byproducts": [(720, "tconstruct:molten_gold"), (720, "tconstruct:molten_iron")], "temp": 700,  "time": 152},
    "diamond":   {"byproducts": [(400, "tconstruct:molten_diamond"), (720, "tconstruct:molten_gold"), (720, "tconstruct:molten_iron")], "temp": 1450, "time": 200},
    "debris":    {"byproducts": [(90, "tconstruct:molten_debris"), (400, "tconstruct:molten_diamond"), (720, "tconstruct:molten_gold"), (720, "tconstruct:molten_iron")], "temp": 1175, "time": 200},
    "netherite": {"byproducts": [(90, "tconstruct:molten_netherite"), (1100, "tconstruct:molten_diamond"), (720, "tconstruct:molten_gold"), (720, "tconstruct:molten_iron")], "temp": 1250, "time": 280},
}

TIERS = ["wood", "iron", "gold", "diamond", "debris", "netherite"]


def get_source_item(from_tier: str, tank_type: str) -> str:
    if from_tier == "wood":
        if tank_type in ["fuel_tank", "fuel_gauge", "ingot_tank", "ingot_gauge"]:
            return f"tconstruct:seared_{tank_type}"
        return f"tconstruct:{tank_type}"
    return f"tinkers_waste:{from_tier}_{tank_type}"


def get_result_item(to_tier: str, tank_type: str) -> str:
    return f"tinkers_waste:{to_tier}_{tank_type}"


# -------- Crafting recipes (matching Extended-Storage chest patterns) --------

def gen_shaped_crafting():
    """Generate shaped crafting recipes (wood→iron, iron→gold, gold→diamond)."""
    recipes = [
        ("wood", "iron", ["###", "#*#", "###"], [("#", {"tag": "forge:ingots/iron"})]),
        ("iron", "gold", ["###", "#*#", "###"], [("#", {"tag": "forge:ingots/gold"})]),
        ("gold", "diamond", [" # ", "#*#", " # "], [("#", {"tag": "forge:gems/diamond"})]),
    ]
    os.makedirs(CRAFTING_DIR, exist_ok=True)
    count = 0
    for from_tier, to_tier, pattern, extra_keys in recipes:
        for tank_type in TANK_TYPES:
            source = get_source_item(from_tier, tank_type)
            result = get_result_item(to_tier, tank_type)
            nbt_copy = {"type": "jsonmore:nbt_copy", "ingredient": {"item": source}, "mode": "REPLACE"}
            key = {
                "*": wrap_condition(nbt_copy)
            }
            for c, ing in extra_keys:
                key[c] = ing
            recipe = {
                "type": "jsonmore:shaped_consuming",
                "pattern": pattern,
                "key": key,
                "result": {"item": result}
            }
            fname = f"{from_tier}_{tank_type}_to_{to_tier}.json"
            with open(os.path.join(CRAFTING_DIR, fname), "w", encoding="utf-8") as f:
                json.dump(recipe, f, indent=2, ensure_ascii=False)
            count += 1
    print(f"  Generated {count} shaped crafting recipes")


def gen_shapeless_crafting():
    """Generate shapeless crafting recipes (diamond→debris, debris→netherite)."""
    os.makedirs(CRAFTING_DIR, exist_ok=True)
    count = 0

    # diamond → debris: 1 netherite_scrap + tank
    for tank_type in TANK_TYPES:
        source = get_source_item("diamond", tank_type)
        result = get_result_item("debris", tank_type)
        nbt_copy = {"type": "jsonmore:nbt_copy", "ingredient": {"item": source}, "mode": "REPLACE"}
        recipe = {
            "type": "jsonmore:shapeless_consuming",
            "ingredients": [
                {"item": "minecraft:netherite_scrap"},
                wrap_condition(nbt_copy)
            ],
            "result": {"item": result}
        }
        fname = f"diamond_{tank_type}_to_debris.json"
        with open(os.path.join(CRAFTING_DIR, fname), "w", encoding="utf-8") as f:
            json.dump(recipe, f, indent=2, ensure_ascii=False)
        count += 1

    # debris → netherite: 3 netherite_scrap + 4 gold + smithing_template + tank
    for tank_type in TANK_TYPES:
        source = get_source_item("debris", tank_type)
        result = get_result_item("netherite", tank_type)
        nbt_copy = {"type": "jsonmore:nbt_copy", "ingredient": {"item": source}, "mode": "REPLACE"}
        recipe = {
            "type": "jsonmore:shapeless_consuming",
            "ingredients": [
                {"item": "minecraft:netherite_scrap"},
                {"item": "minecraft:netherite_scrap"},
                {"item": "minecraft:netherite_scrap"},
                {"tag": "forge:ingots/gold"},
                {"tag": "forge:ingots/gold"},
                {"tag": "forge:ingots/gold"},
                {"tag": "forge:ingots/gold"},
                {"item": "minecraft:netherite_upgrade_smithing_template"},
                wrap_condition(nbt_copy)
            ],
            "result": {"item": result}
        }
        fname = f"debris_{tank_type}_to_netherite.json"
        with open(os.path.join(CRAFTING_DIR, fname), "w", encoding="utf-8") as f:
            json.dump(recipe, f, indent=2, ensure_ascii=False)
        count += 1

    print(f"  Generated {count} shapeless crafting recipes")


# -------- Smithing recipes (diamond → netherite directly) --------

def gen_smithing_recipes():
    """Generate smithing_transform recipes for diamond → netherite."""
    os.makedirs(SMITHING_DIR, exist_ok=True)
    count = 0
    for tank_type in TANK_TYPES:
        source = get_source_item("diamond", tank_type)
        result = get_result_item("netherite", tank_type)
        recipe = {
            "type": "minecraft:smithing_transform",
            "base": wrap_condition({"item": source}),
            "addition": {"item": "minecraft:netherite_ingot"},
            "result": {"item": result},
            "template": {"item": "minecraft:netherite_upgrade_smithing_template"}
        }
        fname = f"diamond_{tank_type}_to_netherite.json"
        with open(os.path.join(SMITHING_DIR, fname), "w", encoding="utf-8") as f:
            json.dump(recipe, f, indent=2, ensure_ascii=False)
        count += 1
    print(f"  Generated {count} smithing recipes")


# -------- Item application recipes --------

def gen_application_recipes():
    os.makedirs(APPLICATION_DIR, exist_ok=True)
    count = 0
    for i, from_tier in enumerate(TIERS):
        for to_tier in TIERS[i+1:]:
            upgrade_item = f"extended_storage:{from_tier}_{to_tier}_chest_upgrade"
            for tank_type in TANK_TYPES:
                source = get_source_item(from_tier, tank_type)
                result = get_result_item(to_tier, tank_type)
                recipe = {
                    "type": "jsonmore:item_application",
                    "conditions": EXTENDED_ONLY_CONDITIONS,
                    "block": {"type": "jsonmore:nbt_copy", "ingredient": {"item": source}, "mode": "REPLACE"},
                    "tool": {"item": upgrade_item},
                    "result": {"item": result},
                    "drop_container": False,
                    "keep_block_state": True,
                    "update_block": False,
                    "sneaking": True
                }
                fname = f"{from_tier}_{tank_type}_to_{to_tier}.json"
                with open(os.path.join(APPLICATION_DIR, fname), "w", encoding="utf-8") as f:
                    json.dump(recipe, f, indent=2, ensure_ascii=False)
                count += 1
    print(f"  Generated {count} item_application recipes")


# -------- Melting recipes --------

def gen_melting_recipes():
    os.makedirs(MELTING_DIR, exist_ok=True)
    count = 0
    for tier in ["iron", "gold", "diamond", "debris", "netherite"]:
        metal = TIER_METALS[tier]
        for tank_type in TANK_TYPES:
            if tank_type in ["fuel_tank", "fuel_gauge", "ingot_tank", "ingot_gauge"]:
                base = SEARED_BASE[tank_type]
            else:
                base = SCORCHED_BASE[tank_type.replace("scorched_", "")]

            # Main result = tier metal (first byproduct of the metal)
            result_amount, result_fluid = metal["byproducts"][0]
            # Byproducts = remaining metal byproducts + base result + base byproducts
            byproducts = [{"amount": a, "fluid": f} for a, f in metal["byproducts"][1:]]
            byproducts.append({"amount": base["result"][0], "fluid": base["result"][1]})
            for a, f in base["byproducts"]:
                byproducts.append({"amount": a, "fluid": f})

            temp = max(base["temp"], metal["temp"])
            time = base["time"] + metal["time"] // 2

            tank_item = get_result_item(tier, tank_type)
            no_container = {"type": "tconstruct:no_container", "item": tank_item}
            recipe = {
                "type": "tconstruct:melting",
                "ingredient": wrap_condition(no_container),
                "result": {"amount": result_amount, "fluid": result_fluid},
                "byproducts": byproducts,
                "temperature": temp,
                "time": time
            }
            fname = f"{tier}_{tank_type}.json"
            with open(os.path.join(MELTING_DIR, fname), "w", encoding="utf-8") as f:
                json.dump(recipe, f, indent=2, ensure_ascii=False)
            count += 1
    print(f"  Generated {count} melting recipes")


# -------- Main --------

def main():
    print("Generating tank upgrade recipes (matching chest patterns)...")
    gen_shaped_crafting()
    gen_shapeless_crafting()
    gen_smithing_recipes()
    gen_application_recipes()
    gen_melting_recipes()
    print("Done!")


if __name__ == "__main__":
    main()
