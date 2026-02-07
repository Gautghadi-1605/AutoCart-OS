import json
import time
from serpapi import GoogleSearch

# 🔑 PASTE YOUR SERPAPI KEY HERE
SERP_API_KEY = "c491683ad2faaf4524132f048258cf1399a5917717767dd026df79fb347b4c7d"

# All product keywords (Safety + Security + Tools + Test Instruments)
PRODUCT_KEYWORDS = [
    # SAFETY
    "safety helmet","safety gloves","fire extinguisher","first aid kit",
    "respirator mask","safety goggles","ear protection","fall protection harness",
    "lockout tagout kit","gas detector","safety alarm","spill kit",

    # SECURITY
    "security camera","metal detector","security safe","door access control",
    "security lock","security gate",

    # TOOLS
    "hammer","screwdriver","pliers","wrench","electric drill","angle grinder",
    "circular saw","tool box","socket set","drill bits",

    # TEST INSTRUMENTS
    "digital multimeter","clamp meter","oscilloscope","thermal camera",
    "infrared thermometer","air quality meter","pressure gauge",
    "sound level meter","tachometer","data logger","inspection camera",
]

def search_grainger_products(keyword):
    """Search Google via SerpAPI"""
    params = {
        "engine": "google",
        "q": f"site:grainger.com {keyword}",
        "api_key": SERP_API_KEY,
        "num": 5
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    products = []

    if "organic_results" in results:
        for r in results["organic_results"]:
            link = r.get("link", "")
            title = r.get("title", keyword)

            if "grainger.com" in link:
                product = {
                    "id": link.split("/")[-1],
                    "name": title,
                    "price": 0.0,
                    "category": "grainger",
                    "specs": {},
                    "compatibility_tags": []
                }
                products.append(product)

    return products


def build_catalog():
    all_products = []

    for keyword in PRODUCT_KEYWORDS:
        print(f"🔎 Searching Grainger for: {keyword}")
        products = search_grainger_products(keyword)
        all_products.extend(products)
        time.sleep(1)  # avoid hitting rate limit

    catalog = {
        "products": {
            "grainger": all_products
        }
    }

    with open("catalog.json", "w") as f:
        json.dump(catalog, f, indent=2)

    print(f"\n✅ DONE! Saved {len(all_products)} Grainger products to catalog.json")


if __name__ == "__main__":
    build_catalog()

