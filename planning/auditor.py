class AuditorAgent:
    def __init__(self):
        print("AuditorAgent initialized.")

    async def validate_action(self, strategy: dict) -> dict:
        """
        Validates the Strategist's proposed action against safety rules.
        """
        proposal = strategy.get("recommended_action")
        risk_level = strategy.get("risk_level")
        
        # Enterprise Safety Rules
        approved = True
        comments = "Action within safety parameters."
        
        if proposal == "ALERT_DAO_TREASURY" and risk_level != "CRITICAL":
            approved = False
            comments = "REJECTED: Cannot alert treasury for non-critical risk."
            
        if risk_level == "CRITICAL" and proposal == "MONITOR":
            approved = False
            comments = "REJECTED: Critical risk requires active intervention."

        return {
            "approved": approved,
            "auditor_comments": comments,
            "timestamp": "2025-10-27T10:05:00Z" # Mock
        }
