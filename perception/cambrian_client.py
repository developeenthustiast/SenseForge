class CambrianClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        print("CambrianClient initialized")

    async def stream_data(self, topic: str):
        """
        Connects to Cambrian MCP and yields real-time data events.
        """
        # TODO: Implement actual MCP connection
        print(f"Subscribing to {topic}...")
        while True:
            # Mock data for now
            yield {"type": "event", "content": "mock_data"}
            await asyncio.sleep(1)
