"""
Shared state definition for CartPilot multi-agent system.
Uses TypedDict for LangGraph state management.
"""
from typing import TypedDict, List, Dict, Optional, Any


class CartPilotState(TypedDict):
    """Shared state passed between agents in the pipeline."""
    
    # Input
    user_goal: str
    
    # Intent Agent output
    parsed_intent: Dict[str, Any]  # {category, use_case, constraints}
    
    # Planner Agent output
    required_components: List[str]  # e.g., ["monitor", "keyboard", "mouse", "desk"]
    
    # Dependency Agent output
    component_dependencies: Dict[str, List[str]]  # component -> [dependencies]
    missing_dependencies: List[str]
    
    # Compatibility Agent output
    compatibility_matrix: Dict[str, Dict[str, bool]]  # component -> {other_component: compatible}
    compatibility_issues: List[Dict[str, str]]  # [{component1, component2, issue}]
    
    # Product Selection Agent output
    selected_products: Dict[str, Dict[str, Any]]  # component -> product_data
    product_alternatives: Dict[str, List[Dict[str, Any]]]  # component -> [alternatives]
    
    # Cart Composer output
    final_cart: List[Dict[str, Any]]  # Complete cart items
    completeness_score: float  # 0.0 - 1.0
    cart_summary: str
    validation_errors: List[str]

