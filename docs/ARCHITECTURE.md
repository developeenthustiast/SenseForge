# SenseForge Technical Architecture

**Enterprise-Grade Autonomous Risk Oracle**  
Version: 1.0 | Date: December 2025

---

## Executive Summary

SenseForge is an autonomous AI agent that predicts liquidity crises in DeFi protocols using a novel JEPA-inspired architecture. Unlike traditional RAG systems that retrieve information, SenseForge **understands** market dynamics by learning causal relationships between governance events and liquidity flows.

**Key Innovation**: Predictive world modeling for institutional risk assessment.

---

## System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     VERISENSE NETWORK                       │
│                    (A2A Protocol Layer)                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  SENSEFORGE A2A SERVER                      │
│                    (server.py)                              │
└──────────────────────┬──────────────────────────────────────┘
                       │
       ┌───────────────┼───────────────┐
       ▼               ▼               ▼
   [Analyst]       [Brain]       [Strategist]
   Cambrian        JEPA          Ambient LLM
       │               │               │
       └───────────────┴───────────────┘
                       │
                       ▼
                  [Auditor]
                  Validator
```

### Component Stack

| Layer | Component | Technology | Purpose |
|---|---|---|---|
| **Network** | A2A Server | Starlette | Verisense protocol compliance |
| **Perception** | Analyst Agent | aiohttp | Cambrian data ingestion |
| **Cognition** | JEPA Model | PyTorch | Predictive understanding |
| **Memory** | Letta Integration | REST API | Episodic crisis patterns |
| **Reasoning** | Strategist | Ambient LLM | Natural language analysis |
| **Safety** | Auditor | Rule Engine | Enterprise validation |

---

## Core Components

### 1. The Analyst (Perception Layer)

**File**: `perception/analyst.py`

**Purpose**: Ingest and normalize on-chain/off-chain data from Cambrian.

**Architecture**:
```python
CambrianHTTPClient
    ├── WebSocket/HTTP polling for live events
    ├── Error handling with exponential backoff
    └── Rate limiting (configurable)

AnalystAgent
    ├── stream_liquidity_events() → async generator
    ├── stream_governance_proposals() → async generator
    └── normalize_state() → MarketState (tensor-ready)
```

**Data Models** (Pydantic):
- `LiquidityEvent`: Stake/unstake/swap events
- `GovernanceProposal`: DAO proposals with metadata
- `MarketState`: Normalized state vector (3D)

**Enterprise Features**:
- ✅ Mode switching (mock/live)
- ✅ Async streaming with backpressure
- ✅ Auto-reconnection on disconnect
- ✅ Structured logging

---

### 2. The Brain (JEPA Model)

**File**: `model/jepa.py`

**Purpose**: Learn world model to predict future market states.

**Architecture**:
```
Input: MarketState (liquidity, volatility, risk)
         ↓
    [Encoder] (3 → 32 → 16)
         ↓
    Latent Representation z_t
         ↓
    [Predictor] (z_t + action → z_{t+1})
         ↓
    [Projector] (z_{t+1} → MarketState')
         ↓
Output: Predicted MarketState
```

**Training Loop**:
1. Experience Replay Buffer (10K capacity)
2. Batch sampling (32 samples)
3. MSE loss on predicted vs. actual states
4. Adam optimizer with learning rate 0.001

**Key Methods**:
- `predict_next_state(state, action)` → Tensor
- `train_epoch(batch_size, num_batches)` → float (loss)
- `save_checkpoint()` / `load_checkpoint()`

**Enterprise Features**:
- ✅ Checkpoint persistence
- ✅ Training statistics tracking
- ✅ Experience replay for stability

---

### 3. Letta Memory (Episodic Storage)

**File**: `model/letta_memory.py`

**Purpose**: Store and retrieve past crisis patterns using vector search.

**Architecture**:
```
episode = {
    state: {...},
    action: "PASS_PROPOSAL",
    outcome: {predicted_liquidity: X}
}
    ↓
format_for_embedding()
    ↓
"Market with liquidity $X, volatility Y, risk Z..."
    ↓
Letta API → Vector Database
    ↓
retrieve_similar_episodes(current_state, limit=5)
```

**Enterprise Features**:
- ✅ JSONL persistence for audit trails
- ✅ Vector similarity search
- ✅ Mode switching (mock/live)
- ✅ Graceful API failure handling

---

### 4. The Strategist (Ambient LLM)

**File**: `planning/strategist.py`, `ambient_client.py`

**Purpose**: Natural language risk analysis powered by LLM.

**Prompt Template**:
```
Current Market State:
- Liquidity: $9.5M
- Volatility: 0.52
- Risk Score: 0.35

JEPA Prediction:
- Predicted Liquidity: $8.7M
- Change: -8.4%

Respond in JSON:
{
  "risk_level": "CRITICAL",
  "recommended_action": "ALERT_DAO_TREASURY",
  "reasoning": "...",
  "confidence": 0.85
}
```

**Enterprise Features**:
- ✅ Circuit breaker (prevents cascading failures)
- ✅ Retry with exponential backoff
- ✅ Rate limiting (10 req/min)
- ✅ Fallback to rule-based logic
- ✅ Structured JSON parsing

---

### 5. The Auditor (Safety Layer)

**File**: `planning/auditor.py`

**Purpose**: Validate Strategist recommendations against safety rules.

**Validation Rules**:
1. CRITICAL risk requires active intervention (not just monitoring)
2. Cannot alert treasury for non-critical events
3. All actions must have reasoning

**Enterprise Features**:
- ✅ Deterministic validation
- ✅ Audit trail generation
- ✅ Rejection with explanations

---

## Enterprise Resilience

### Circuit Breaker Pattern

**File**: `resilience.py`

**States**:
- `CLOSED`: Normal operation
- `OPEN`: Blocking requests (service is down)
- `HALF_OPEN`: Testing recovery

**Configuration**:
```python
CircuitBreaker(
    name="AmbientLLM",
    failure_threshold=5,     # Open after 5 failures
    recovery_timeout=60      # Test recovery after 60s
)
```

### Retry with Backoff

**Algorithm**:
```
delay = min(initial_delay * (2 ** attempt), max_delay)
if jitter:
    delay *= (0.5 + random())
```

**Default Settings**:
- Max attempts: 3
- Initial delay: 1s
- Max delay: 60s
- Exponential base: 2

### Rate Limiting

**Algorithm**: Token Bucket

**Configuration**:
```python
RateLimiter(rate=10, per=60)  # 10 requests per 60 seconds
```

---

## Data Flow

### Risk Analysis Query

```
1. External Agent → POST /query {"query": "Analyze PROP-456"}
2. Server → Analyst.stream_liquidity_events()
3. Analyst → normalize_state() → MarketState
4. JEPA → predict_next_state(state, action=PASS) → predicted_liquidity
5. Strategist → analyze_risk(state, prediction) → risk_assessment
6. Auditor → validate_action(risk_assessment) → approved/rejected
7. Server → JSON Response
```

**Example Response**:
```json
{
  "status": "success",
  "analysis": {
    "current_liquidity": 9500000.0,
    "predicted_liquidity": 8750000.0,
    "risk_assessment": {
      "risk_level": "CRITICAL",
      "recommended_action": "ALERT_DAO_TREASURY",
      "reasoning": "Predicted 7.9% liquidity drop exceeds threshold",
      "confidence": 0.87
    },
    "audit_verification": {
      "approved": true,
      "auditor_comments": "Action within safety parameters"
    }
  }
}
```

---

## Configuration Management

**File**: `config.py`

**Environment Variables**:
```bash
# API Keys
CAMBRIAN_API_KEY=...
LETTA_API_KEY=...
AMBIENT_API_KEY=...

# Mode
SENSEFORGE_MODE=live  # or "mock"

# Logging
SENSEFORGE_LOG_LEVEL=INFO
```

**Validation**: Pydantic models ensure type safety and defaults.

---

## Observability

### Structured Logging

**Format**:
```
2025-12-01 22:00:00 - senseforge - INFO - [PREDICTION] Created pred_20251201_220000 - Risk: CRITICAL
```

**Log Files**:
- `logs/senseforge.log` (rotating, 10MB max, 5 backups)

### Metrics Tracking

**File**: `metrics.py`

**Tracked Metrics**:
- Prediction accuracy (MAE, RMSE, %)
- Training loss over time
- API call success rates
- Circuit breaker states

### Proof of Reasoning

**File**: `reasoning_logger.py`

**Output**: JSON audit trails for every decision

**Example**:
```json
{
  "chain_id": "chain_20251201_220000",
  "steps": [
    {
      "step_number": 1,
      "component": "Analyst",
      "reasoning": "Normalized 5 liquidity events",
      "confidence": 1.0
    },
    {
      "step_number": 2,
      "component": "Brain",
      "reasoning": "JEPA predicted 8.4% drop",
      "confidence": 0.85
    }
  ]
}
```

---

## Testing Strategy

### Unit Tests

**Coverage**: 80%+

**Test Files**:
- `tests/test_jepa.py`: JEPA model behavior
- `tests/test_resilience.py`: Circuit breakers, retry, rate limiting

**Example**:
```python
def test_circuit_opens_on_failures():
    cb = CircuitBreaker("test", failure_threshold=3)
    # Trigger 3 failures
    assert cb.state == CircuitState.OPEN
```

### Integration Tests

**File**: `tests/test_integration.py`

**Scenarios**:
- Full Tri-Agent workflow (Analyst → JEPA → Strategist → Auditor)
- Error recovery (API failures, fallbacks)
- Training convergence

---

## Deployment

### Prerequisites

```bash
Python 3.9+
pip install -r requirements.txt
pip install -r tests/requirements-test.txt  # For testing
```

### Running the Agent

**Dashboard**:
```bash
streamlit run interface/dashboard.py
```

**A2A Server**:
```bash
python server.py
```

**Training**:
```bash
python scripts/generate_training_data.py
python scripts/train_jepa.py
```

### Testing

```bash
pytest tests/ -v --cov=. --cov-report=html
```

---

## Security Considerations

1. **API Keys**: Never committed to git, loaded from `.env`
2. **Rate Limiting**: Prevents abuse and quota exhaustion
3. **Input Validation**: Pydantic models validate all inputs
4. **Audit Trails**: Every decision is logged for compliance
5. **Circuit Breakers**: Prevent cascading failures

---

## Performance Characteristics

- **Latency**: ~200-500ms per query (with LLM)
- **Throughput**: 10 queries/min (rate limited)
- **Memory**: ~500MB (model + buffers)
- **Training**: ~5 min for 50 epochs on 150 episodes

---

## Future Enhancements

1. **Multi-Pool Analysis**: Extend to multiple liquidity pools
2. **Real-Time Alerts**: Push notifications to DAOs
3. **Confidence Calibration**: Improve uncertainty quantification
4. **Active Learning**: Query oracle for uncertain predictions
5. **Cross-Chain Support**: Expand beyond single blockchain

---

## References

- JEPA Paper: [LeCun et al., 2022]
- Verisense A2A Protocol: https://verisense.network/docs
- Cambrian API: https://docs.cambrian.org
- Letta Memory: https://letta.com/docs

---

**Document Version**: 1.0  
**Last Updated**: December 2025  
**Maintained by**: SenseForge Team
