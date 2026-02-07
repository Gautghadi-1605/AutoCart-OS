"""
Test script for CartPilot API endpoint.
Run this while api.py is running.
"""
import requests
import json

def test_generate_cart():
    """Test the /generate-cart endpoint."""
    url = "http://localhost:8000/generate-cart"
    
    test_cases = [
        "I want to set up a home office for remote work",
        "I need a gaming setup",
        "I want to create a creative workspace"
    ]
    
    for goal in test_cases:
        print(f"\n{'='*60}")
        print(f"Testing: {goal}")
        print('='*60)
        
        try:
            response = requests.post(
                url,
                json={"user_goal": goal},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Success!")
                print(f"  Cart Items: {len(data['cart'])}")
                print(f"  Total Price: ${data['total_price']:.2f}")
                print(f"  Completeness Score: {data['completeness_score']:.2%}")
                print(f"  Summary: {data['cart_summary']}")
                
                if data['validation_errors']:
                    print(f"  ⚠ Validation Errors: {len(data['validation_errors'])}")
                    for error in data['validation_errors']:
                        print(f"    - {error}")
                else:
                    print("  ✓ No validation errors")
                    
            else:
                print(f"✗ Error: {response.status_code}")
                print(f"  {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("✗ Error: Could not connect to server. Is api.py running?")
            break
        except Exception as e:
            print(f"✗ Error: {e}")

if __name__ == "__main__":
    test_generate_cart()

