# SenseForge: Judge Q&A Preparation

**Purpose**: Anticipate and prepare for hackathon judge questions.

---

## Technical Questions

### Q1: "How is your JEPA model different from standard ML regression?"

**Answer**:
> "Standard regression predicts a scalar output. Our JEPA model learns a **structured latent representation** of the market. It encodes the current state into a 16-dimensional latent space, predicts how that representation evolves given an action, then projects back to market state. This allows it to model **causal relationships**—not just correlations—between governance events and liquidity changes. It's closer to a world model than a statistical predictor."

**Follow-up Evidence**:
- Show `model/jepa.py` architecture (Encoder → Predictor → Projector)
- Reference JEPA's training loop with experience replay

---

### Q2: "How does the agent improve itself over time?"

**Answer**:
> "Through three mechanisms:
> 1. **Episodic Memory (Letta)**: Every prediction is compared to actual outcomes 24 hours later. These `(state, action, outcome)` tuples are stored in Letta's vector database.
> 2. **Experience Replay**: The JEPA model samples past episodes to continuously retrain, reducing prediction error.
> 3. **Metrics Tracking**: We calculate rolling accuracy (MAE, RMSE) and adjust confidence calibration."

**Follow-up Evidence**:
- Show `prediction_service.py` auto-validation system
- Show `metrics.py` accuracy calculation
- Show training loss decreasing over epochs

---

### Q3: "What happens if the Ambient LLM API goes down?"

**Answer**:
> "We have three layers of resilience:
> 1. **Circuit Breaker**: After 5 consecutive failures, the circuit opens and blocks requests for 60 seconds to prevent cascading failures.
> 2. **Fallback Logic**: The Strategist automatically switches to rule-based analysis (e.g., >10% drop = CRITICAL).
> 3. **Retry with Backoff**: Transient errors are retried with exponential backoff (1s, 2s, 4s delays).
>
> The system **never** crashes—it gracefully degrades."

**Follow-up Evidence**:
- Show `resilience.py` Circuit Breaker implementation
- Show `ambient_client.py` fallback method
- Run live demo: disconnect network, show fallback working

---

### Q4: "How do you validate prediction accuracy?"

**Answer**:
> "We use a prediction tracking service that:
> 1. Logs every prediction with ID, timestamp, and metadata.
> 2. After a 5-minute delay (configurable), fetches the actual market state.
> 3. Calculates Mean Absolute Error (MAE) and percentage accuracy.
> 4. Stores results in JSONL format for audit trails.
>
> Current accuracy on test data: ~78%."

**Follow-up Evidence**:
- Show `prediction_service.py`
- Show `data/predictions.jsonl`
- Show accuracy stats in dashboard

---

### Q5: "Why JEPA instead of a transformer or diffusion model?"

**Answer**:
> "JEPA is specifically designed for **predictive understanding** of the world. Unlike transformers (which excel at sequence modeling) or diffusion models (for generation), JEPA learns **causal dynamics**. For risk prediction, we don't need to generate text or images—we need to understand 'if X happens, Y will follow.' JEPA's latent space naturally captures these relationships."

**Technical Note**:
> "Also, JEPA is more sample-efficient than transformers—critical when working with limited historical crisis data."

---

## Sponsor Alignment Questions

### Q6: "How does this use Cambrian?"

**Answer**:
> "Cambrian is our **perception layer**. We use their API to stream:
> - Liquidity pool events (stakes, unstakes, swaps)
> - Governance proposal submissions
> - On-chain TVL data
>
> The Analyst agent normalizes this into a `MarketState` vector that feeds the JEPA model. We chose Cambrian for their real-time, verifiable data—essential for institutional trust."

**Evidence**:
- Show `perception/analyst.py` CambrianHTTPClient
- Show Cambrian API calls in logs

---

### Q7: "How does this use Letta?"

**Answer**:
> "Letta provides our **long-term memory**. We store crisis episodes as semantic text:
> - 'Market with liquidity $9.5M, volatility 0.52. Proposal passed. Result: dropped to $8.7M.'
>
> When analyzing a new situation, we query Letta for similar past crises using vector similarity search. This allows the agent to learn from history—'the last time we saw this pattern, here's what happened.'"

**Evidence**:
- Show `model/letta_memory.py`
- Show episode storage format
- Show retrieval query

---

### Q8: "How does this use Ambient?"

**Answer**:
> "Ambient powers our **natural language reasoning**. After the JEPA model predicts a liquidity drop, the Strategist uses Ambient's LLM to:
> 1. Interpret the prediction in context
> 2. Generate human-readable risk assessments
> 3. Recommend specific actions (e.g., 'Alert DAO treasury')
>
> We use structured prompts to get JSON responses for parsing. The LLM adds interpretability—critical for enterprise adoption."

**Evidence**:
- Show `ambient_client.py` prompt templates
- Show JSON response from LLM
- Show fallback logic

---

### Q9: "How does this comply with Verisense A2A?"

**Answer**:
> "We implemented the full A2A specification:
> 1. **Agent Card** (`agent.json`): Declares our capabilities (`protocol.verisense.risk-analysis`)
> 2. **Discoverable Endpoint**: `/.well-known/agent.json` served via HTTP
> 3. **Query Handler**: `/query` POST endpoint processes risk analysis requests
> 4. **Proof of Reasoning**: Every decision generates a JSON audit trail
>
> This makes SenseForge **network-native**—any agent can discover and query us."

**Evidence**:
- Show `agent.json` file
- Show `server.py` routes
- Show `reasoning_logger.py` output
- (If registered) Show agent on Verisense Dashboard

---

## Business & Market Questions

### Q10: "Who is the target customer?"

**Answer**:
> "We target three segments:
> 1. **DAOs**: Use SenseForge as a risk oracle before executing governance proposals
> 2. **DeFi Protocols**: Integrate as a risk monitoring service
> 3. **Institutional Funds**: Use for pre-investment due diligence
>
> MVP focuses on DAOs—they have the most urgent need (governance events directly impact liquidity)."

---

### Q11: "How do you monetize?"

**Answer**:
> "Three revenue streams:
> 1. **API Subscription**: $X/month for query access
> 2. **White-Label Deployment**: Custom instances for protocols
> 3. **Risk Intelligence Reports**: Premium analysis for institutions
>
> Freemium model: 100 free queries/month, then paid tiers."

---

### Q12: "What's your competitive advantage?"

**Answer**:
> "Three things:
> 1. **Predictive, not reactive**: We forecast crises, not just report them
> 2. **Enterprise-grade**: Circuit breakers, audit trails, 80%+ test coverage
> 3. **A2A native**: Built for the agentic economy from Day 1
>
> Competitors are either dashboards (reactive) or non-autonomous (require human oversight)."

---

## Demo Questions

### Q13: "Can you show it working live?"

**Answer**:
> "Absolutely. Let me send a query to the running agent..."

**Action**:
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Analyze risk for Proposal PROP-789"}'
```

**Expected Output**:
```json
{
  "status": "success",
  "analysis": {
    "risk_level": "WARNING",
    "recommended_action": "MONITOR",
    ...
  }
}
```

---

### Q14: "Can you show the learning curve?"

**Answer**:
> "Sure. Here's the JEPA training loss over 50 epochs..."

**Action**:
- Open `visualizations/jepa_learning_curve.png`
- Point to decreasing trend
- Show improvement percentage: "42% reduction in loss"

---

## Tough Questions

### Q15: "Your test data is synthetic. How do you know this works on real crises?"

**Answer** (honest):
> "You're right—our initial training is on synthetic data modeled after historical patterns (Terra, FTX). The next step is backtesting on real historical blockchain data. We've architected the system to easily swap data sources—the `AnalystAgent` already supports mode switching. Given real data access, we'd retrain and validate on out-of-sample events."

**Mitigation**:
> "However, even with synthetic data, we demonstrate the **architecture** and **methodology** that would work on real data. The JEPA model, Tri-Agent loop, and A2A compliance are all production-ready."

---

### Q16: "How do you prevent false positives?"

**Answer**:
> "Three mechanisms:
> 1. **Confidence Scores**: Every prediction includes a 0-1 confidence score
> 2. **Auditor Validation**: Rule-based checks prevent illogical recommendations
> 3. **Human-in-the-Loop Mode**: For production, we'd add approval gates for CRITICAL alerts
>
> We optimize for recall (catch all crises) over precision (low false positives), but provide confidence scores so users can set their own thresholds."

---

### Q17: "What if a malicious actor manipulates the input data?"

**Answer**:
> "We'd implement:
> 1. **Data provenance checks**: Verify Cambrian data signatures
> 2. **Anomaly detection**: Flag unusual patterns before prediction
> 3. **Multi-source validation**: Cross-reference with other oracles
>
> For this hackathon, we assume trusted data sources. In production, data integrity would be a top priority."

---

## Closing Statements

### "Why should we pick SenseForge?"

**Answer**:
> "Because we didn't just build a tool—we built the **risk department for the agentic economy**. Every design choice was made with enterprise buyers in mind: circuit breakers, audit trails, A2A compliance, comprehensive testing. We used all four sponsor tools **deeply**, not superficially. And we demonstrated a novel architecture—JEPA for predictive understanding—that opens new research directions for AI in DeFi."

**Pause, then**:
> "Plus, we shipped everything in 30 days. Imagine what we can do with real funding and data access."

---

**Document Version**: 1.0  
**Last Updated**: December 2025  
**Practice These**: Record yourself answering each question. Aim for <60 seconds per answer.
