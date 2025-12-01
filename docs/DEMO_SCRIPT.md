# SenseForge Demo Video Script
**Duration**: 2 minutes  
**Target Audience**: Hackathon judges, VCs, enterprise users

---

## Pre-Production Checklist

- [ ] Dashboard running (`streamlit run interface/dashboard.py`)
- [ ] Server running (`python server.py`)
- [ ] Training visualization ready (`visualizations/jepa_learning_curve.png`)
- [ ] Screen recorder configured (1080p, 60fps)
- [ ] Microphone tested
- [ ] Browser tabs prepared (Verisense Dashboard, GitHub repo)

---

## Script

### 0:00-0:20 | HOOK & PROBLEM

**Visual**: Terminal with ASCII art logo

**Voiceover**:
> "What if an AI agent could predict a market crash... before it happens?"

**Action**:
- Show SenseForge logo
- Cut to news headlines about DeFi liquidity crises (Terra, FTX)

**Voiceover**:
> "Traditional risk systems react to crises. SenseForge *predicts* them using a JEPA-inspired world model that learns causal relationships between governance and liquidity."

---

### 0:20-0:40 | ARCHITECTURE WALKTHROUGH

**Visual**: Split screen showing `docs/ARCHITECTURE.md` diagram

**Voiceover**:
> "Here's how it works. The Analyst agent ingests live data from Cambrian. The Brain—a JEPA model—predicts future liquidity, not just pattern-matches. The Strategist interprets predictions using Ambient LLM. And the Auditor validates every action for enterprise safety."

**Action**:
- Highlight each component as mentioned
- Show `agent.json` file (A2A compliance)

---

### 0:40-1:20 | LIVE DEMO (THE MONEY SHOT)

**Visual**: Dashboard in action

**Setup**:
```bash
# Terminal 1
streamlit run interface/dashboard.py

# Terminal 2
python server.py

# Terminal 3 (for demo query)
curl -X POST http://localhost:8000/query -H "Content-Type: application/json" -d '{"query": "Analyze risk for PROP-456: Increase Debt Ceiling"}'
```

**Voiceover** (while demonstrating):
> "Watch this. A DAO submits a risky governance proposal."

**Action 1**: Send curl query (0:40-0:50)
- Show terminal command
- Show server logs in real-time

**Visual**: Dashboard updates

**Voiceover**:
> "The Analyst normalizes the market state. Current liquidity: 9.5 million. Volatility: 0.52."

**Action 2**: Point to Live Feed tab (0:50-1:00)
- Show current metrics updating

**Voiceover**:
> "The JEPA model predicts: if this proposal passes, liquidity drops to 8.7 million—an 8.4% decline."

**Action 3**: Switch to AI Predictions  tab (1:00-1:10)
- Show prediction chart
- Highlight the drop

**Voiceover**:
> "The Strategist, powered by Ambient LLM, flags this as CRITICAL and recommends alerting the treasury."

**Action 4**: Show JSON response (1:10-1:15)
```json
{
  "risk_level": "CRITICAL",
  "recommended_action": "ALERT_DAO_TREASURY",
  "reasoning": "Predicted 8.4% drop exceeds safety threshold",
  "confidence": 0.87
}
```

**Voiceover**:
> "The Auditor validates: approved. The DAO now has actionable intelligence."

**Action 5**: Switch to System Logs tab (1:15-1:20)
- Show Proof of Reasoning log
- Highlight audit trail

---

### 1:20-1:40 | LEARNING DEMONSTRATION

**Visual**: Learning Curve tab

**Voiceover**:
> "But here's what makes this enterprise-grade: it learns."

**Action**:
- Show training loss curve decreasing
- Show improvement: 42%

**Voiceover**:
> "The JEPA model trained on 150 historical episodes. Loss decreased by 42%. Every prediction is compared to reality—stored in Letta's memory—so it gets smarter over time."

**Visual**: Split screen: Code + Metrics

**Action**:
- Show `model/jepa.py` briefly
- Show `metrics.py` accuracy stats

---

### 1:40-1:55 | A2A COMPLIANCE

**Visual**: Browser → Verisense Dashboard (or agent.json)

**Voiceover**:
> "SenseForge is fully A2A compliant. Registered on the Verisense network, discoverable by any agent."

**Action**:
- Show `agent.json` endpoint in browser
- (If registered) Show agent on Verisense Dashboard

**Voiceover**:
> "Circuit breakers prevent cascading failures. Retry logic handles transient errors. Proof of reasoning logs every decision for compliance."

**Visual**: Quick montage
- `resilience.py` code
- `reasoning_logger.py` output
- Test results (pytest passing)

---

### 1:55-2:00 | CLOSE

**Visual**: GitHub repo README

**Voiceover**:
> "We didn't build a chatbot. We built the risk department for the agentic economy."

**Action**:
- Show README badges: Production-Ready, 4 Sponsors, Enterprise-Grade
- Fade to logo + tagline

**Text Overlay**:
```
SenseForge
Institutional Liquidity Risk Oracle

Built for "Calling For All Agents!" Hackathon
Powered by: Cambrian | Letta | Ambient | Verisense

github.com/[YOUR_REPO]
```

**End Screen**: 2 seconds

---

## Post-Production

### Editing Notes

1. **Music**: Low-key, future bass (no lyrics)
2. **Transitions**: Quick cuts (<0.5s) for demo sections
3. **Captions**: Add for key stats ("8.4% drop", "42% improvement")
4. **Annotations**: Highlight JSON keys, code functions

### Export Settings

- **Resolution**: 1080p (1920x1080)
- **Frame Rate**: 30fps
- **Format**: MP4 (H.264)
- **Bitrate**: 8-10 Mbps
- **Audio**: AAC, 192 kbps

### Thumbnail

**Design**:
- SenseForge logo
- Text: "AI That Predicts Crisis"
- Visual: Graph showing prediction vs. actual

---

## Backup Script (If Live Demo Fails)

**Plan B**: Use pre-recorded screen capture

**Prepare**:
1. Record successful demo run in advance
2. Have it ready in video editor
3. Narrate over it live (safer)

---

## Review Checklist

- [ ] All timestamps accurate
- [ ] Audio levels consistent
- [ ] No sensitive data visible (API keys, etc.)
- [ ] GitHub repo public and clean
- [ ] Video under 2:00 exactly
- [ ] Thumbnail created
- [ ] YouTube/Loom upload ready

---

**Script Version**: 1.0  
**Author**: SenseForge Team  
**Last Updated**: December 2025
