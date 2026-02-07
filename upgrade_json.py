import json

# load your huge scraped file
with open("catalog.json","r") as f:
    data = json.load(f)

def enrich(product):
    name = product["name"].lower()

    # ---------- CATEGORY DETECTION ----------
    if any(x in name for x in ["helmet","glove","respirator","goggles","hearing","fall","first aid","fire","gas","spill","lockout"]):
        category = "safety"
    elif any(x in name for x in ["camera","metal detector","safe","lock","gate","security"]):
        category = "security"
    elif any(x in name for x in ["hammer","pliers","wrench","screwdriver","drill","grinder","saw","tool","socket","bit"]):
        category = "tools"
    elif any(x in name for x in ["multimeter","clamp","oscilloscope","thermal","thermometer","air quality","pressure","sound","tachometer","data logger","inspection"]):
        category = "test_instruments"
    elif "kh-" in product["id"]:
        category = "guide"
    else:
        category = "safety"

    product["category"] = category

    # ---------- PRICE + SPECS ----------
    if product["price"] == 0:
        if category == "safety":
            product["price"] = 49.99
            product["specs"] = {"type":"ppe"}
            product["compatibility_tags"] = ["ppe","workplace_safety"]

        elif category == "security":
            product["price"] = 299.99
            product["specs"] = {"type":"facility_security"}
            product["compatibility_tags"] = ["security","access_control"]

        elif category == "tools":
            product["price"] = 59.99
            product["specs"] = {"material":"steel"}
            product["compatibility_tags"] = ["hand_tool"]

        elif category == "test_instruments":
            product["price"] = 249.99
            product["specs"] = {"usage":"diagnostics"}
            product["compatibility_tags"] = ["testing"]

        elif category == "guide":
            product["price"] = 0
            product["specs"] = {"type":"knowledge_article"}
            product["compatibility_tags"] = ["guide","documentation"]

for p in data["products"]["grainger"]:
    enrich(p)

# save upgraded file
with open("grainger_catalog_enriched.json","w") as f:
    json.dump(data,f,indent=2)

print("✅ Catalog successfully enriched!")
