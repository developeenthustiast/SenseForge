from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import asyncio
import aiohttp
import random
from datetime import datetime
import os

# --- Data Models ---

class LiquidityEvent(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.now)
    pool_id: str
    token_symbol: str
    amount: float
    event_type: Literal["STAKE", "UNSTAKE", "SWAP"]
    tx_hash: str

class GovernanceProposal(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.now)
    proposal_id: str
    title: str
    description: str
    proposer: str
    status: Literal["ACTIVE", "PASSED", "REJECTED"]

class MarketState(BaseModel):
    """Normalized tensor-ready state for the JEPA model"""
    liquidity_depth: float
    volatility_index: float
    governance_risk_score: float
    timestamp: datetime = Field(default_factory=datetime.now)

# --- Cambrian HTTP Client ---

class CambrianHTTPClient:
    """HTTP client for Cambrian on-chain data API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.base_url = "https://opabinia.cambrian.org"
        self.api_key = api_key or os.getenv("CAMBRIAN_API_KEY")
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def _ensure_session(self):
        """Ensure aiohttp session exists"""
        if self.session is None or self.session.closed:
            headers = {}
            if self.api_key:
                headers["X-API-KEY"] = self.api_key
            self.session = aiohttp.ClientSession(headers=headers)
    
    async def close(self):
        """Close the HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def query(self, endpoint: str, params: dict = None):
        """
        Generic query method for Cambrian API
        Returns TableResponse format
        """
        await self._ensure_session()
        
        try:
            url = f"{self.base_url}{endpoint}"
            async with self.session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    print(f"[Cambrian API Error] {response.status}: {error_text}")
                    return None
        except asyncio.TimeoutError:
            print("[Cambrian API] Request timeout")
            return None
        except Exception as e:
            print(f"[Cambrian API] Error: {e}")
            return None
    
    async def get_pool_events(self, pool_address: str, limit: int = 10):
        """Get recent events for a specific pool"""
        # This is a mock endpoint - adjust based on actual Cambrian API
        return await self.query(f"/pools/{pool_address}/events", {"limit": limit})
    
    async def get_governance_proposals(self, dao_address: str, status: str = "active"):
        """Get governance proposals for a DAO"""
        return await self.query(f"/governance/{dao_address}/proposals", {"status": status})

# --- The Analyst Agent ---

class AnalystAgent:
    def __init__(self, source: str = "cambrian-api", mode: str = "mock"):
        self.source = source
        self.mode = mode  # "mock" or "live"
        self.cambrian_client = CambrianHTTPClient() if mode == "live" else None
        print(f"AnalystAgent initialized. Mode: {mode}, Source: {source}")

    async def stream_liquidity_events(self):
        """
        Streams liquidity events.
        In 'live' mode: fetches from Cambrian API
        In 'mock' mode: generates synthetic data
        """
        if self.mode == "live" and self.cambrian_client:
            # Live mode - fetch from Cambrian
            while True:
                try:
                    # Example: fetch events for a known pool
                    data = await self.cambrian_client.get_pool_events("0x...")
                    if data:
                        # Parse response and yield events
                        # This depends on actual Cambrian API response structure
                        pass
                    await asyncio.sleep(5)  # Poll every 5 seconds
                except Exception as e:
                    print(f"[Analyst] Error fetching live data: {e}")
                    await asyncio.sleep(5)
        else:
            # Mock mode - generate synthetic events
            while True:
                event_type = random.choice(["STAKE", "UNSTAKE", "SWAP"])
                amount = random.uniform(1000, 1000000)
                if event_type == "UNSTAKE":
                    amount *= 1.5  # Unstakes are larger for risk simulation
                
                event = LiquidityEvent(
                    pool_id="0x123...abc",
                    token_symbol="ETH",
                    amount=amount,
                    event_type=event_type,
                    tx_hash="0x..."
                )
                yield event
                await asyncio.sleep(2)

    async def stream_governance_proposals(self):
        """Simulates streaming governance proposals."""
        while True:
            # Mock proposal
            yield GovernanceProposal(
                proposal_id=f"PROP-{random.randint(100, 999)}",
                title="Increase Risk Parameters",
                description="Proposal to increase the debt ceiling...",
                proposer="0xDao...Member",
                status="ACTIVE"
            )
            await asyncio.sleep(10)

    def normalize_state(self, liquidity_events: List[LiquidityEvent], proposals: List[GovernanceProposal]) -> MarketState:
        """
        Converts raw events into a normalized 'MarketState' for the JEPA model.
        """
        # Simple logic for now:
        # High unstaking volume -> Lower liquidity depth
        # Active risky proposals -> Higher governance risk
        
        total_unstake = sum(e.amount for e in liquidity_events if e.event_type == "UNSTAKE")
        risk_proposals = len([p for p in proposals if "Risk" in p.title])
        
        return MarketState(
            liquidity_depth=10000000 - total_unstake,  # Base liquidity minus unstakes
            volatility_index=0.5 + (total_unstake / 10000000),
            governance_risk_score=risk_proposals * 0.2
        )
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.cambrian_client:
            await self.cambrian_client.close()
