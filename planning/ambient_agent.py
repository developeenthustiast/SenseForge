class AmbientAgent:
    def __init__(self, model_name: str = "ambient-1"):
        self.model_name = model_name
        print("AmbientAgent initialized")

    async def reason(self, context: str, prediction: dict):
        """
        Uses Ambient LLM to interpret the JEPA prediction and decide on an action.
        """
        # TODO: Implement Ambient LLM call
        return "No action needed"
