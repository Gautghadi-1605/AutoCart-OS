"""
Industrial Dependency and Compatibility Rules Engine
Same architecture as before — but using Grainger product categories
"""

from typing import Dict, List, Set, Tuple

# ---------------------------------------------------
# 🔗 PRODUCT DEPENDENCY RULES (Industrial version)
# ---------------------------------------------------

DEPENDENCY_RULES: Dict[str, List[str]] = {

    # Electrical diagnostics kit
    "digital-multimeters": ["safety-goggles", "electrical-insulating-gloves"],
    "clamp-meters": ["safety-goggles"],
    "oscilloscopes": ["safety-goggles"],

    # Working at height
    "fall-protection": ["hard-hats-and-helmets"],
    "safety-harnesses-for-general-fall-arrest": ["hard-hats-and-helmets"],

    # Fire safety
    "fire-extinguishers": ["safety-alarms-warning-lights"],

    # Tool usage requires PPE
    "power-drills": ["safety-goggles", "safety-gloves"],
    "angle-grinders": ["safety-goggles", "hearing-protection"],
    "circular-saws": ["safety-goggles", "hearing-protection"],

    # Gas / confined space
    "portable-gas-detectors": ["full-face-respirators"],
    "confined-space": ["portable-gas-detectors", "safety-alarms-warning-lights"],

    # Security systems dependencies
    "video-surveillance": ["video-surveillance-monitors"],
    "keyless-access-locksets": ["locks"],
}

# ---------------------------------------------------
# 🤝 COMPATIBILITY RULES
# ---------------------------------------------------

COMPATIBILITY_RULES: Dict[Tuple[str, str], bool] = {

    # Positive compatibilities
    ("power-drills", "safety-goggles"): True,
    ("angle-grinders", "hearing-protection"): True,
    ("fall-protection", "hard-hats-and-helmets"): True,
    ("video-surveillance", "security-alarms-warnings"): True,
    ("digital-multimeters", "clamp-meters"): True,

    # Incompatibilities (realistic safety conflicts)
    ("flammable_environment", "angle-grinders"): False,
    ("confined-space", "no_gas_detector"): False,
}

# ---------------------------------------------------
# 🏭 CATEGORY ECOSYSTEMS
# ---------------------------------------------------

CATEGORY_COMPATIBILITY: Dict[str, Set[str]] = {
    "ppe_ecosystem": {
        "hard-hats-and-helmets",
        "safety-gloves",
        "safety-goggles",
        "hearing-protection",
        "full-face-respirators",
        "fall-protection",
    },
    "tool_ecosystem": {
        "power-drills",
        "angle-grinders",
        "circular-saws",
        "hammers",
        "pliers",
        "wrenches",
        "screwdrivers",
    },
    "security_ecosystem": {
        "video-surveillance",
        "security-alarms-warnings",
        "keyless-access-locksets",
        "locks",
        "security-safes",
    },
    "testing_ecosystem": {
        "digital-multimeters",
        "clamp-meters",
        "oscilloscopes",
        "thermal-cameras",
        "infrared-thermometers",
        "air-quality-sensors",
    }
}

# ---------------------------------------------------
# 🧠 FUNCTIONS (UNCHANGED ARCHITECTURE)
# ---------------------------------------------------

def get_dependencies(component: str) -> List[str]:
    return DEPENDENCY_RULES.get(component, [])


def check_compatibility(component1: str, component2: str) -> bool:

    if (component1, component2) in COMPATIBILITY_RULES:
        return COMPATIBILITY_RULES[(component1, component2)]
    if (component2, component1) in COMPATIBILITY_RULES:
        return COMPATIBILITY_RULES[(component2, component1)]

    # ecosystem compatibility
    for category, components in CATEGORY_COMPATIBILITY.items():
        if component1 in components and component2 in components:
            return True

    return True


def validate_component_set(components: List[str]) -> Tuple[List[str], List[Tuple[str, str, str]]]:

    missing_deps = []
    compatibility_issues = []

    # check dependencies
    all_required = set()
    for component in components:
        deps = get_dependencies(component)
        all_required.update(deps)

    missing_deps = [dep for dep in all_required if dep not in components]

    # check compatibility
    for i, comp1 in enumerate(components):
        for comp2 in components[i+1:]:
            if not check_compatibility(comp1, comp2):
                compatibility_issues.append((comp1, comp2, "Incompatible components"))

    return missing_deps, compatibility_issues


def get_all_dependencies(components: List[str]) -> Dict[str, List[str]]:
    result = {}
    for component in components:
        result[component] = get_dependencies(component)
    return result
