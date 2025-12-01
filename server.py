import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
import json
import os
import asyncio
from dotenv import load_dotenv
import torch

# Import Core Components
from perception.analyst import AnalystAgent, LiquidityEvent, GovernanceProposal
from model.jepa import LiquidityJEPA
from model.letta_memory import LettaMemory
from planning.strategist import StrategistAgent
from planning.auditor import AuditorAgent

load_dotenv()

# Initialize Components Globally
analyst = AnalystAgent(source="cambrian-mock")
jepa = LiquidityJEPA(state_dim=3, action_dim=1, latent_dim=16)
memory = LettaMemory(agent_id="senseforge-risk-001")
strategist = StrategistAgent()
auditor = AuditorAgent()

async def get_agent_card(request):
    """Returns the Agent Card for discovery."""
    with open("agent.json", "r") as f:
        card = json.load(f)
    return JSONResponse(card)

async def handle_query(request):
    """
    Handles A2A queries (e.g., "Analyze Risk for Proposal X").
    Triggers the Tri-Agent Loop on demand.
    """
    body = await request.json()
    query_text = body.get("query", "")
    print(f"[Server] Received Query: {query_text}")
    
    # 1. Analyst: Fetch latest market state (Mocked here as current state)
    # In real implementation, Analyst would query Cambrian for specific proposal data
    events_buffer = [] 
    proposals_buffer = []
    
    # Simulate gathering some data
    async for event in analyst.stream_liquidity_events():
        events_buffer.append(event)
        if len(events_buffer) >= 3:
            break
            
    current_state = analyst.normalize_state(events_buffer, proposals_buffer)
    
    # 2. Brain: Predict Outcome
    state_tensor = torch.tensor([[
        current_state.liquidity_depth, 
        current_state.volatility_index, 
        current_state.governance_risk_score
    ]], dtype=torch.float32)
    
    action_tensor = torch.tensor([[1.0]], dtype=torch.float32) # Assume "Pass Proposal"
    predicted_state = jepa.predict_next_state(state_tensor, action_tensor)
    predicted_liquidity = float(predicted_state[0][0])
    
    # 3. Strategist: Analyze Risk
    strategy = await strategist.analyze_risk(current_state.dict(), predicted_liquidity)
    
    # 4. Auditor: Validate Action
    audit_result = await auditor.validate_action(strategy)
    
    response = {
        "status": "success",
        "analysis": {
            "current_liquidity": current_state.liquidity_depth,
            "predicted_liquidity_if_passed": predicted_liquidity,
            "risk_assessment": strategy,
            "audit_verification": audit_result
        }
    }
    
    return JSONResponse(response)

routes = [
    Route("/.well-known/agent.json", get_agent_card, methods=["GET"]),
    Route("/query", handle_query, methods=["POST"]),
]

app = Starlette(debug=True, routes=routes)

if __name__ == "__main__":
    print("SenseForge A2A Server Starting on port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
