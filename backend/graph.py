"""
LangGraph orchestration for CartPilot multi-agent pipeline.
Defines the graph structure and agent execution flow.
"""
from typing import TypedDict
from state import CartPilotState
from agents import (
    intent_agent,
    planner_agent,
    dependency_agent,
    compatibility_agent,
    product_selection_agent,
    cart_composer_agent
)

# Try to import LangGraph, fallback to simple sequential execution
try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
except (ImportError, AttributeError) as e:
    # Fallback if LangGraph has import issues (e.g., CheckpointAt import error)
    LANGGRAPH_AVAILABLE = False
    StateGraph = None
    END = None
    print(f"Warning: LangGraph import failed ({type(e).__name__}), using sequential execution")


def create_cartpilot_graph():
    """
    Create and wire the CartPilot multi-agent graph.
    
    Flow:
    Intent -> Planner -> Dependency -> Compatibility -> Product Selection -> Cart Composer
    """
    if not LANGGRAPH_AVAILABLE:
        # Return a simple sequential runner
        return None
    
    # Initialize graph
    workflow = StateGraph(CartPilotState)
    
    # Add nodes (agents)
    workflow.add_node("intent", intent_agent)
    workflow.add_node("planner", planner_agent)
    workflow.add_node("dependency", dependency_agent)
    workflow.add_node("compatibility", compatibility_agent)
    workflow.add_node("product_selection", product_selection_agent)
    workflow.add_node("cart_composer", cart_composer_agent)
    
    # Define edges (linear pipeline)
    workflow.set_entry_point("intent")
    workflow.add_edge("intent", "planner")
    workflow.add_edge("planner", "dependency")
    workflow.add_edge("dependency", "compatibility")
    workflow.add_edge("compatibility", "product_selection")
    workflow.add_edge("product_selection", "cart_composer")
    workflow.add_edge("cart_composer", END)
    
    # Compile graph
    app = workflow.compile()
    
    return app


def run_sequential(state: CartPilotState) -> CartPilotState:
    """Fallback sequential execution if LangGraph is unavailable."""
    state = intent_agent(state)
    state = planner_agent(state)
    state = dependency_agent(state)
    state = compatibility_agent(state)
    state = product_selection_agent(state)
    state = cart_composer_agent(state)
    return state


# Global graph instance
cartpilot_graph = create_cartpilot_graph()


def run_cartpilot(user_goal: str) -> CartPilotState:
    """
    Execute the CartPilot pipeline with a user goal.
    Returns the final state with complete cart.
    """
    initial_state: CartPilotState = {
        "user_goal": user_goal,
        "parsed_intent": {},
        "required_components": [],
        "component_dependencies": {},
        "missing_dependencies": [],
        "compatibility_matrix": {},
        "compatibility_issues": [],
        "selected_products": {},
        "product_alternatives": {},
        "final_cart": [],
        "completeness_score": 0.0,
        "cart_summary": "",
        "validation_errors": []
    }
    
    # Execute graph or use sequential fallback
    if cartpilot_graph is not None:
        final_state = cartpilot_graph.invoke(initial_state)
    else:
        final_state = run_sequential(initial_state)
    
    return final_state

