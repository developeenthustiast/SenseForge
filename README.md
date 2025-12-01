# SenseForge: Institutional Liquidity Risk Oracle

**Enterprise-Grade AI Agent for the Verisense Network**

[![Status](https://img.shields.io/badge/Status-Production--Ready-green)]()
[![Week](https://img.shields.io/badge/Week-2%2F4-blue)]()
[![Sponsors](https://img.shields.io/badge/Sponsors-4-purple)]()

SenseForge is an enterprise-grade autonomous agent that predicts liquidity crises in DeFi markets using a JEPA-inspired "Sense-Model". Built for the "Calling For All Agents!" Hackathon.

## 🎯 Core Innovation

Instead of simply retrieving data (RAG), SenseForge **understands** market dynamics by:
1. **Learning causal relationships** between governance events and liquidity flows
2. **Predicting future states** using a Joint Embedding Predictive Architecture (JEPA)
3. **Validating actions** through a Tri-Agent system (Analyst → Strategist → Auditor)

## 🏗️ Enterprise Features

-✅ **Production-Grade Dashboard**: Real-time Streamlit UI with live metrics
- ✅ **Centralized Configuration**: Environment-based config management
- ✅ **Structured Logging**: File rotation with audit trails
- ✅ **Metrics Tracking**: Prediction accuracy and model performance analytics
- ✅ **Mode Switching**: Mock (development) / Live (production)
- ✅ **Error Recovery**: Async operations with timeout handling

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip

### Installation

```bash
# Clone the repository
cd d:\Predichain\SenseForge

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys (optional for mock mode)
```

### Running the Dashboard

```bash
streamlit run interface/dashboard.py
```

Open http://localhost:8501 in your browser to see the enterprise dashboard.

### Training the Model

```bash
# Generate synthetic training data
python scripts/generate_training_data.py

# Train the JEPA model
python scripts/train_jepa.py
```

### Running the A2A Server

```bash
python server.py
```

Test with:
```bash
curl http://localhost:8000/.well-known/agent.json
curl -X POST http://localhost:8000/query -H "Content-Type: application/json" -d '{"query": "Analyze risk for Proposal PROP-456"}'
```

## 📊 Dashboard Features

The enterprise dashboard includes:

### 📈 Live Feed
- Real-time market metrics (Liquidity, Volatility, Risk)
- Event stream from Cambrian
- System health indicators

### 🧠 AI Predictions
- Prediction vs. Actual comparison chart
- Rolling accuracy metrics
- Confidence scoring

### 📉 Learning Curve
- JEPA training loss visualization
- Improvement percentage tracking
- Model statistics

### 🔍 System Logs
- Real-time audit trail
- Structured logging output
- Compliance-ready format

## 🏛️ Architecture

### The Tri-Agent System
- **The Analyst** (Perception Layer): Ingests real-time data from Cambrian MCP
- **The Brain** (JEPA Model): Predicts `LiquidityDepth` based on market state + governance actions
- **The Strategist** (Ambient LLM): Interprets predictions and formulates risk assessments
- **The Auditor** (Supervisor): Validates proposed actions for enterprise safety

### Sponsor Tools Integration
- **Cambrian**: Data stream ingestion (`perception/analyst.py`)
- **Letta**: Episodic memory for learning from past crises (`model/letta_memory.py`)
- **Ambient**: LLM reasoning for risk interpretation (`planning/strategist.py`)
- **Verisense**: A2A protocol compliance (`server.py`, `agent.json`)

## 📋 Project Structure

```
SenseForge/
├── config.py                  # Centralized configuration
├── logging_setup.py           # Enterprise logging
├── metrics.py                 # Performance tracking
├── perception/
│   └── analyst.py            # Cambrian data ingestion
├── model/
│   ├── jepa.py              # JEPA predictive model
│   └── letta_memory.py      # Letta episodic memory
├── planning/
│   ├── strategist.py        # Ambient LLM reasoning
│   └── auditor.py           # Safety validator
├── interface/
│   └── dashboard.py         # Streamlit dashboard
├── scripts/
│   ├── generate_training_data.py
│   └── train_jepa.py
├── server.py                # A2A Server wrapper
├── agent.json               # Agent Card for Verisense
└── requirements.txt         # Dependencies
```

## 🔧 Configuration

Environment variables (`.env`):

```bash
# API Keys (Optional - leave empty for mock mode)
CAMBRIAN_API_KEY=your_key_here
LETTA_API_KEY=your_key_here
AMBIENT_API_KEY=your_key_here

# Operating Mode
SENSEFORGE_MODE=mock  # Options: mock, live

# Dashboard Settings
SENSEFORGE_REFRESH_INTERVAL=5
```

## 🏆 Hackathon Compliance

✅ **A2A Compatible**: Registered with Verisense network  
✅ **4 Sponsor Tools**: Cambrian + Letta + Ambient + Verisense  
✅ **Originality**: JEPA-inspired architecture (novel)  
✅ **Autonomy**: Tri-Agent loop with safety validation  
✅ **Enterprise-Grade**: Production-ready code with logging, metrics, config management

## 📄 License

MIT License

## 🙏 Acknowledgments

Built for the "Calling For All Agents!" Hackathon hosted by Verisense.

---

**Week 2 Progress**: 7/14 days complete | Dashboard & Metrics ✅
