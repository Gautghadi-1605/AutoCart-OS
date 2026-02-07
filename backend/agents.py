"""
CartPilot Agent Implementations — Industrial Version (FINAL)
Each agent has a single responsibility and updates shared state.
"""

import json
from typing import Dict, Any
from pathlib import Path
from state import CartPilotState
from rules import get_dependencies, check_compatibility, get_all_dependencies


# ============================================================
# 1️⃣ INTENT AGENT — user text → industrial scenario
# ============================================================

def intent_agent(state: CartPilotState) -> CartPilotState:
    """Convert user goal into industrial scenario"""

    user_goal = state["user_goal"].lower()

    if "electrical" in user_goal or "voltage" in user_goal:
        scenario = "electrical_work"
    elif "construction" in user_goal or "workshop" in user_goal:
        scenario = "construction_work"
    elif "fire" in user_goal:
        scenario = "fire_risk_environment"
    elif "height" in user_goal or "ladder" in user_goal:
        scenario = "working_at_height"
    elif "gas" in user_goal or "confined" in user_goal:
        scenario = "confined_space"
    elif "chemical" in user_goal or "spill" in user_goal:
        scenario = "chemical_environment"
    elif "security" in user_goal or "warehouse" in user_goal:
        scenario = "facility_security"
    elif "diagnostic" in user_goal or "testing" in user_goal:
        scenario = "equipment_diagnostics"
    else:
        scenario = "tool_usage"

    state["parsed_intent"] = {"scenario": scenario}
    return state


# ============================================================
# 2️⃣ PLANNER AGENT — scenario → required components
# ============================================================

def planner_agent(state: CartPilotState) -> CartPilotState:
    """Map industrial scenario → required product categories"""

    scenario = state["parsed_intent"]["scenario"]

    scenario_mapping = {
        "electrical_work": ["digital-multimeters", "clamp-meters"],
        "construction_work": ["hard-hats-and-helmets", "safety-gloves"],
        "fire_risk_environment": ["fire-extinguishers"],
        "working_at_height": ["fall-protection"],
        "confined_space": ["portable-gas-detectors"],
        "chemical_environment": ["respirators", "spill-kits"],
        "facility_security": ["video-surveillance", "locks"],
        "equipment_diagnostics": ["thermal-cameras", "air-quality-sensors"],
        "tool_usage": ["power-drills", "wrenches", "pliers"]
    }

    state["required_components"] = scenario_mapping.get(scenario, ["power-drills"])
    return state


# ============================================================
# 3️⃣ DEPENDENCY AGENT
# ============================================================

def dependency_agent(state: CartPilotState) -> CartPilotState:
    """Find missing dependencies using rules.py"""

    required_components = state["required_components"]

    component_dependencies = get_all_dependencies(required_components)

    all_required_deps = set()
    for deps in component_dependencies.values():
        all_required_deps.update(deps)

    existing_components = set(required_components)
    missing_dependencies = [dep for dep in all_required_deps if dep not in existing_components]

    state["component_dependencies"] = component_dependencies
    state["missing_dependencies"] = missing_dependencies

    return state


# ============================================================
# 4️⃣ COMPATIBILITY AGENT
# ============================================================

def compatibility_agent(state: CartPilotState) -> CartPilotState:
    """Check compatibility between components"""

    required_components = state["required_components"]
    missing_deps = state["missing_dependencies"]
    all_components = required_components + missing_deps

    compatibility_matrix = {}
    compatibility_issues = []

    for comp1 in all_components:
        compatibility_matrix[comp1] = {}
        for comp2 in all_components:
            if comp1 != comp2:
                is_compatible = check_compatibility(comp1, comp2)
                compatibility_matrix[comp1][comp2] = is_compatible
                if not is_compatible:
                    compatibility_issues.append({
                        "component1": comp1,
                        "component2": comp2,
                        "issue": "Incompatible components"
                    })

    state["compatibility_matrix"] = compatibility_matrix
    state["compatibility_issues"] = compatibility_issues
    return state


# ============================================================
# 5️⃣ PRODUCT SELECTION AGENT (FIXED FOR GRAINGER CATALOG)
# ============================================================

def product_selection_agent(state: CartPilotState) -> CartPilotState:
    """
    Select products from Grainger catalog by matching component → product.id
    THIS FIXES THE EMPTY CART BUG 🔥
    """

    catalog_path = Path(__file__).parent / "catalog.json"
    with open(catalog_path) as f:
        catalog = json.load(f)

    grainger_products = catalog["products"]["grainger"]
    all_components = state["required_components"] + state["missing_dependencies"]

    selected_products = {}
    product_alternatives = {}

    for component in all_components:
        # Find products whose ID contains the component keyword
        matches = [
            p for p in grainger_products
            if component.lower() in p["id"].lower()
        ]

        if matches:
            selected_products[component] = matches[0]
            product_alternatives[component] = matches[1:] if len(matches) > 1 else []

    state["selected_products"] = selected_products
    state["product_alternatives"] = product_alternatives
    return state


# ============================================================
# 6️⃣ CART COMPOSER AGENT
# ============================================================

def cart_composer_agent(state: CartPilotState) -> CartPilotState:
    """Create final cart"""

    selected_products = state["selected_products"]

    final_cart = []
    total_price = 0.0

    for component, product in selected_products.items():
        product_copy = product.copy()
        product_copy["component"] = component
        final_cart.append(product_copy)
        total_price += product.get("price", 0.0)

    state["final_cart"] = final_cart
    state["total_price"] = total_price
    state["cart_summary"] = f"{len(final_cart)} items selected. Total ${total_price:.2f}"

    return state
