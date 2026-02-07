# AutoCartOS: Multi-Agent System Design Document

## 1. High-Level Architecture

AutoCartOS is a deterministic multi-agent system that transforms high-level user goals into complete, validated product bundles. The system uses a controlled pipeline of six specialized agents, each with a single responsibility, operating on shared state. Agents communicate through structured JSON state updates rather than direct messaging, ensuring traceability and explainability. The architecture prioritizes rule-based logic over probabilistic reasoning, using LLMs only for natural language understanding and component planning. LangGraph orchestrates the agent execution flow, while FastAPI exposes the system as a REST API.

```
┌─────────────┐
│  User Goal  │
│  (NLP)      │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  Intent Agent   │ ──► Parses goal → structured intent (LLM)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Planner Agent  │ ──► Generates component list (LLM)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Dependency Agent│ ──► Identifies dependencies (rule-based)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│Compatibility    │ ──► Validates compatibility (rule-based)
│    Agent        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│Product Selection│ ──► Selects products from catalog (LLM/rule-based)
│     Agent       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Cart Composer   │ ──► Builds final cart + validation (rule-based)
└────────┬────────┘
         │
         ▼
┌─────────────┐
│ Final Cart  │
│  (JSON)     │
└─────────────┘
```

## 2. Shared State Definition

```python
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
```

## 3. Agent Specifications

### Agent 1: Intent Agent
- **Purpose**: Parse natural language user goal into structured intent
- **Input**: `user_goal` (string)
- **Output**: `parsed_intent` (dict with category, use_case, constraints)
- **Uses LLM**: Yes (natural language understanding)

### Agent 2: Planner Agent
- **Purpose**: Generate list of required components based on parsed intent
- **Input**: `parsed_intent`
- **Output**: `required_components` (list of component names)
- **Uses LLM**: Yes (component planning from intent)

### Agent 3: Dependency Agent
- **Purpose**: Identify all dependencies for required components
- **Input**: `required_components`
- **Output**: `component_dependencies`, `missing_dependencies`
- **Uses LLM**: No (rule-based lookup)

### Agent 4: Compatibility Agent
- **Purpose**: Validate compatibility between all components
- **Input**: `required_components`, `missing_dependencies`
- **Output**: `compatibility_matrix`, `compatibility_issues`
- **Uses LLM**: No (rule-based compatibility checks)

### Agent 5: Product Selection Agent
- **Purpose**: Select specific products from catalog for each component
- **Input**: `required_components`, `missing_dependencies`, `compatibility_issues`
- **Output**: `selected_products`, `product_alternatives`
- **Uses LLM**: Yes (intelligent product matching, can be rule-based for demo)

### Agent 6: Cart Composer Agent
- **Purpose**: Compose final cart, validate completeness, calculate score
- **Input**: All previous agent outputs
- **Output**: `final_cart`, `completeness_score`, `cart_summary`, `validation_errors`
- **Uses LLM**: No (deterministic composition)

## 4. LangGraph Node Implementations

See `agents.py` for full implementations. Each agent is a function that:
- Takes `CartPilotState` as input
- Returns updated `CartPilotState`
- Updates specific fields in the state

Key implementation details:
- LLM calls abstracted through `LLMInterface.invoke()`
- Rule-based agents use deterministic logic from `rules.py`
- Product selection queries `catalog.json`

## 5. Dependency & Compatibility Rules

**Dependency Rules** (`rules.py`):
```python
DEPENDENCY_RULES = {
    "monitor": ["monitor_stand", "hdmi_cable"],
    "desktop_computer": ["monitor", "keyboard", "mouse", "power_cable"],
    "laptop": ["laptop_stand", "external_keyboard", "external_mouse"],
    "gaming_setup": ["gaming_monitor", "gaming_keyboard", "gaming_mouse", "gaming_headset"],
}
```

**Compatibility Rules**:
```python
COMPATIBILITY_RULES = {
    ("macbook", "usb_c_adapter"): True,
    ("macbook", "windows_keyboard"): False,
    ("gaming_monitor", "gaming_keyboard"): True,
}
```

**Category-Based Compatibility**:
- `mac_ecosystem`: macbook, mac_keyboard, mac_mouse, thunderbolt_dock
- `windows_ecosystem`: windows_laptop, windows_keyboard, windows_mouse
- `gaming_ecosystem`: gaming_monitor, gaming_keyboard, gaming_mouse, gaming_headset

## 6. LangGraph Wiring

```python
workflow = StateGraph(CartPilotState)
workflow.add_node("intent", intent_agent)
workflow.add_node("planner", planner_agent)
workflow.add_node("dependency", dependency_agent)
workflow.add_node("compatibility", compatibility_agent)
workflow.add_node("product_selection", product_selection_agent)
workflow.add_node("cart_composer", cart_composer_agent)

workflow.set_entry_point("intent")
workflow.add_edge("intent", "planner")
workflow.add_edge("planner", "dependency")
workflow.add_edge("dependency", "compatibility")
workflow.add_edge("compatibility", "product_selection")
workflow.add_edge("product_selection", "cart_composer")
workflow.add_edge("cart_composer", END)
```

## 7. FastAPI Integration

**Endpoint**: `POST /generate-cart`

**Request Schema**:
```python
class CartRequest(BaseModel):
    user_goal: str
```

**Response Schema**:
```python
class CartResponse(BaseModel):
    cart: List[CartItem]
    total_price: float
    completeness_score: float
    cart_summary: str
    validation_errors: List[str]
    metadata: Dict[str, Any]
```

See `api.py` for full implementation.

## 8. Final Output Example

See `OUTPUT_EXAMPLE.md` for complete JSON output example for "home office setup" goal.

Key characteristics:
- All required components included
- All dependencies satisfied
- Zero compatibility issues
- Completeness score: 95%+
- Total price calculated
- Validation errors: empty

