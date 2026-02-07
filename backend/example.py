"""
Example usage of CartPilot system.
Demonstrates the end-to-end flow.
"""
from graph import run_cartpilot
import json


def example_home_office():
    """Example: Home office setup"""
    user_goal = "I want to set up a home office for remote work"
    
    print(f"User Goal: {user_goal}\n")
    print("=" * 60)
    print("Executing CartPilot Multi-Agent Pipeline...")
    print("=" * 60)
    
    final_state = run_cartpilot(user_goal)
    
    print("\n1. PARSED INTENT:")
    print(json.dumps(final_state["parsed_intent"], indent=2))
    
    print("\n2. REQUIRED COMPONENTS:")
    print(final_state["required_components"])
    
    print("\n3. DEPENDENCIES:")
    print(f"Component Dependencies: {json.dumps(final_state['component_dependencies'], indent=2)}")
    print(f"Missing Dependencies: {final_state['missing_dependencies']}")
    
    print("\n4. COMPATIBILITY:")
    print(f"Compatibility Issues: {len(final_state['compatibility_issues'])}")
    if final_state["compatibility_issues"]:
        for issue in final_state["compatibility_issues"]:
            print(f"  - {issue}")
    
    print("\n5. SELECTED PRODUCTS:")
    for component, product in final_state["selected_products"].items():
        print(f"  {component}: {product['name']} (${product['price']})")
    
    print("\n6. FINAL CART:")
    print(f"Total Items: {len(final_state['final_cart'])}")
    print(f"Total Price: ${sum(item['price'] for item in final_state['final_cart']):.2f}")
    print(f"Completeness Score: {final_state['completeness_score']:.2%}")
    print(f"\nCart Summary: {final_state['cart_summary']}")
    
    if final_state["validation_errors"]:
        print("\nValidation Errors:")
        for error in final_state["validation_errors"]:
            print(f"  - {error}")
    
    print("\n" + "=" * 60)
    print("Cart Items:")
    print("=" * 60)
    for item in final_state["final_cart"]:
        print(f"  [{item['component']}] {item['name']} - ${item['price']}")


if __name__ == "__main__":
    example_home_office()

