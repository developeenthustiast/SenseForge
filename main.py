import asyncio
import os
import torch
from dotenv import load_dotenv

from perception.analyst import AnalystAgent, LiquidityEvent, GovernanceProposal
from model.jepa import LiquidityJEPA
from model.letta_memory import LettaMemory
from planning.ambient_agent import AmbientAgent

# Load environment variables
load_dotenv()

async def main():
    print("SenseForge: Institutional Liquidity Risk Oracle Starting...")
    
    print("Initializing 'The Analyst' (Perception)...")
    analyst = AnalystAgent(source="cambrian-mock")
    
    print("Initializing 'The Brain' (LiquidityJEPA)...")
    # State: Liquidity, Volatility, Risk Score (3 dims)
    # Action: Pass/Fail/None (1 dim)
    jepa = LiquidityJEPA(state_dim=3, action_dim=1, latent_dim=16)
    
    print("Initializing 'The Strategist' & 'Auditor'...")
    memory = LettaMemory(agent_id="senseforge-risk-001")
    planner = AmbientAgent()
    
    print("Agent Live. Monitoring Liquidity Streams...")
    
    # Mock Event Loop
    # In a real scenario, we'd gather events into a buffer, normalize, then predict.
    events_buffer = []
    proposals_buffer = []
    
    async for event in analyst.stream_liquidity_events():
        print(f"[Analyst] New Event: {event.event_type} {event.amount} {event.token_symbol}")
        events_buffer.append(event)
        
        # Every 3 events, normalize state and run prediction
        if len(events_buffer) >= 3:
            current_state = analyst.normalize_state(events_buffer, proposals_buffer)
            print(f"[Analyst] Normalized Market State: {current_state}")
            
            # Convert to tensor
            state_tensor = torch.tensor([[
                current_state.liquidity_depth, 
                current_state.volatility_index, 
                current_state.governance_risk_score
            ]], dtype=torch.float32)
            
            # Predict: What if a risky proposal passes? (Action = 1.0)
            action_tensor = torch.tensor([[1.0]], dtype=torch.float32)
            predicted_state = jepa.predict_next_state(state_tensor, action_tensor)
            
            print(f"[Brain] JEPA Prediction (Post-Proposal): {predicted_state.detach().numpy()}")
            
            # Store in Letta Memory
            await memory.store_episode(
                state=current_state.dict(),
                action="PASS_PROPOSAL",
                outcome={"predicted_liquidity": float(predicted_state[0][0])}
            )
            
            events_buffer = [] # Reset buffer
            
    # Keep alive
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
