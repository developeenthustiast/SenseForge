from typing import List, Dict, Optional
import asyncio
import aiohttp
import json
import os

class LettaMemory:
    """
    Letta Memory client for storing and retrieving crisis patterns.
    Uses Letta's archival memory API with vector similarity search.
    """
    def __init__(self, agent_id: str, mode: str = "mock", base_url: str = None):
        self.agent_id = agent_id
        self.mode = mode  # "mock" or "live"
        self.base_url = base_url or os.getenv("LETTA_API_URL", "https://api.letta.com")
        self.api_key = os.getenv("LETTA_API_KEY")
        self.session: Optional[aiohttp.ClientSession] = None
        self.memory_store = []  # Local mock storage
        print(f"LettaMemory initialized for agent {agent_id} (mode: {mode})")

    async def _ensure_session(self):
        """Ensure aiohttp session exists"""
        if self.mode == "live" and (self.session is None or self.session.closed):
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            self.session = aiohttp.ClientSession(headers=headers)
    
    async def close(self):
        """Close the HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()

    async def store_episode(self, state: dict, action: str, outcome: dict):
        """
        Stores a market episode (State -> Action -> Outcome) in Letta's archival memory.
        Uses archival_memory_insert internally.
        """
        episode = {
            "state": state,
            "action": action,
            "outcome": outcome,
            "timestamp": state.get("timestamp", "2025-10-27T10:00:00Z")
        }
        
        # Create a descriptive text representation for vector embedding
        episode_text = self._format_episode_for_storage(episode)
        
        if self.mode == "live":
            await self._insert_to_letta(episode_text, metadata=episode)
        else:
            # Mock mode - store locally
            self.memory_store.append(episode)
        
        print(f"[Memory] Stored episode: {action} -> Liquidity: {outcome.get('predicted_liquidity', 'N/A')}")

    async def retrieve_similar_episodes(self, current_state: dict, limit: int = 5) -> List[Dict]:
        """
        Retrieves past episodes that match the current market state using semantic search.
        Uses archival_memory_search internally.
        """
        # Create query from current state
        query_text = self._format_state_for_query(current_state)
        
        if self.mode == "live":
            return await self._search_letta(query_text, limit=limit)
        else:
            # Mock retrieval logic: Return random past episodes
            import random
            if not self.memory_store:
                return []
            return random.sample(self.memory_store, min(limit, len(self.memory_store)))
    
    def _format_episode_for_storage(self, episode: dict) -> str:
        """
        Converts episode dict to semantic text for vector embedding.
        Example: "Market state with liquidity 9.5M and risk 0.3. Action: PASS_PROPOSAL. Result: Liquidity dropped to 8.7M (critical)."
        """
        state = episode["state"]
        action = episode["action"]
        outcome = episode["outcome"]
        
        text = (
            f"Market state: liquidity_depth={state.get('liquidity_depth', 0):.0f}, "
            f"volatility={state.get('volatility_index', 0):.2f}, "
            f"risk={state.get('governance_risk_score', 0):.2f}. "
            f"Action: {action}. "
            f"Outcome: predicted_liquidity={outcome.get('predicted_liquidity', 0):.0f}"
        )
        return text
    
    def _format_state_for_query(self, state: dict) -> str:
        """
        Converts current state to query text for similar cases.
        """
        return (
            f"Market with liquidity {state.get('liquidity_depth', 0):.0f}, "
            f"volatility {state.get('volatility_index', 0):.2f}, "
            f"risk {state.get('governance_risk_score', 0):.2f}"
        )
    
    async def _insert_to_letta(self, content: str, metadata: dict):
        """
        Insert content into Letta archival memory via API.
        """
        await self._ensure_session()
        
        try:
            # Letta API endpoint for archival memory insert
            url = f"{self.base_url}/agents/{self.agent_id}/archival"
            payload = {
                "content": content,
                "metadata": metadata
            }
            
            async with self.session.post(url, json=payload, timeout=10) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                else:
                    error_text = await response.text()
                    print(f"[Letta API Error] Insert failed: {response.status} - {error_text}")
                    return None
        except asyncio.TimeoutError:
            print("[Letta API] Insert timeout")
            return None
        except Exception as e:
            print(f"[Letta API] Insert error: {e}")
            return None
    
    async def _search_letta(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Search Letta archival memory using vector similarity.
        """
        await self._ensure_session()
        
        try:
            # Letta API endpoint for archival memory search
            url = f"{self.base_url}/agents/{self.agent_id}/archival/search"
            payload = {
                "query": query,
                "limit": limit
            }
            
            async with self.session.post(url, json=payload, timeout=10) as response:
                if response.status == 200:
                    results = await response.json()
                    # Parse results and extract metadata
                    episodes = []
                    for result in results:
                        if "metadata" in result:
                            episodes.append(result["metadata"])
                    return episodes
                else:
                    error_text = await response.text()
                    print(f"[Letta API Error] Search failed: {response.status} - {error_text}")
                    return []
        except asyncio.TimeoutError:
            print("[Letta API] Search timeout")
            return []
        except Exception as e:
            print(f"[Letta API] Search error: {e}")
            return []
    
    def get_memory_stats(self) -> dict:
        """Get memory statistics"""
        if self.mode == "mock":
            return {
                "total_episodes": len(self.memory_store),
                "mode": "mock"
            }
        else:
            return {
                "mode": "live",
                "api_connected": self.session is not None and not self.session.closed
            }
