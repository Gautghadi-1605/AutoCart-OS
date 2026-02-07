"""
FastAPI backend for CartPilot.
Exposes /generate-cart endpoint for cart generation.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from graph import run_cartpilot

app = FastAPI(
    title="CartPilot API",
    description="Multi-agent autonomous purchasing agent system",
    version="1.0.0"
)


class CartRequest(BaseModel):
    """Request schema for cart generation."""
    user_goal: str = Field(..., description="High-level user goal (e.g., 'I want to set up a home office for remote work')")


class CartItem(BaseModel):
    """Individual cart item schema."""
    id: str
    name: str
    price: float
    category: str
    component: str
    specs: Dict[str, Any]
    compatibility_tags: List[str]


class CartResponse(BaseModel):
    """Response schema for cart generation."""
    cart: List[CartItem]
    total_price: float
    completeness_score: float
    cart_summary: str
    validation_errors: List[str]
    metadata: Dict[str, Any] = Field(default_factory=dict)


@app.get("/")
def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "CartPilot"}


@app.post("/generate-cart", response_model=CartResponse)
def generate_cart(request: CartRequest):
    """
    Generate a complete, compatible product bundle from user goal.
    
    This endpoint orchestrates the multi-agent pipeline:
    1. Intent Agent - parses user goal
    2. Planner Agent - identifies required components
    3. Dependency Agent - finds dependencies
    4. Compatibility Agent - validates compatibility
    5. Product Selection Agent - selects products
    6. Cart Composer Agent - composes final cart
    """
    try:
        # Execute multi-agent pipeline
        final_state = run_cartpilot(request.user_goal)
        
        # Calculate total price
        total_price = sum(item.get("price", 0.0) for item in final_state["final_cart"])
        
        # Format cart items
        cart_items = []
        for item in final_state["final_cart"]:
            cart_items.append(CartItem(
                id=item["id"],
                name=item["name"],
                price=item["price"],
                category=item["category"],
                component=item.get("component", ""),
                specs=item.get("specs", {}),
                compatibility_tags=item.get("compatibility_tags", [])
            ))
        
        # Build metadata
        metadata = {
            "parsed_intent": final_state["parsed_intent"],
            "required_components": final_state["required_components"],
            "selected_components": list(final_state["selected_products"].keys()),
            "compatibility_issues_count": len(final_state["compatibility_issues"])
        }
        
        return CartResponse(
            cart=cart_items,
            total_price=total_price,
            completeness_score=final_state["completeness_score"],
            cart_summary=final_state["cart_summary"],
            validation_errors=final_state["validation_errors"],
            metadata=metadata
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cart generation failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

