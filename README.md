# SenseForge: Institutional Liquidity Risk Oracle

**Autonomous AI Agent for the Verisense A2A Network**

[![Status](https://img.shields.io/badge/Status-Hackathon--Ready-green)]()
[![Verisense](https://img.shields.io/badge/Verisense-Registered-blue)](https://dashboard.verisense.network/)
[![Week](https://img.shields.io/badge/Week-4%2F4-brightgreen)]()
[![Sponsors](https://img.shields.io/badge/Sponsors-4-purple)](https://verisense.network)

SenseForge is an autonomous AI agent that predicts liquidity crises in DeFi markets using a **JEPA-inspired "Sense-Model"**. Successfully registered on the **Verisense A2A Network** for the "Calling For All Agents!" hackathon.

🏆 **Hackathon**: "Calling For All Agents!" - Verisense  
🔗 **Agent ID**: `kGjGpNDσysz3As8mb9FdMFqBNdLZ97WBkRNRzqFqnYEDQCcN`  
📍 **Network Status**: ✅ Live & Discoverable

---

## 🎯 Core Innovation

Instead of simply retrieving data (RAG), SenseForge **understands** market dynamics by:
1. **Learning causal relationships** between governance events and liquidity flows
2. **Predicting future states** using a Joint Embedding Predictive Architecture (JEPA)
3. **Validating actions** through a Tri-Agent system (Analyst → Strategist → Auditor)

---

## 🏗️ Key Features

### ✅ **Security & Reliability**
- **Input Validation**: Comprehensive sanitization and security checks
- **Error Handling**: Retry logic with exponential backoff, circuit breakers
- **Testing Coverage**: Unit tests, integration tests, 80%+ coverage
- **Monitoring**: Structured logging, metrics tracking, audit trails

### ✅ **AI/ML Implementation**
- **JEPA Model**: Fully functional training loop with experience replay
- **Episodic Memory**: Letta integration for learning from historical data
- **LLM Reasoning**: Ambient LLM for natural language risk analysis
- **Performance Tracking**: Prediction accuracy metrics and analytics

### ✅ **User Experience**
- **Interactive Dashboard**: Real-time Streamlit UI with live visualizations
- **Transparency**: JSON audit trails showing agent reasoning
- **API Documentation**: Clear endpoints with example queries

### ✅ **A2A Compliance**
- **Verisense Registration**: Successfully registered and discoverable
- **Standard Agent Card**: Compliant `/.well-known/agent.json`
- **Query Endpoint**: Functional POST `/query` for risk analysis
- **Health Checks**: Status monitoring endpoint

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/developeenthustiast/SenseForge.git
cd SenseForge

# Install dependencies
pip install -r requirements.txt

# Configure environment (optional for mock mode)
cp .env.example .env
```

### Running the A2A Server

```bash
python server.py
```

**Server runs on**: `http://localhost:8000`

Test endpoints:
```bash
# Agent Card (Verisense discovery)
curl http://localhost:8000/.well-known/agent.json

# Health Check
curl http://localhost:8000/health

# Risk Analysis Query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Analyze risk for Proposal PROP-456"}'
```

### Running the Dashboard

```bash
streamlit run interface/dashboard.py
```

Open **http://localhost:8501** in your browser.

---

## 📊 Dashboard Features

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
- Verisense compliance-ready format

---

## 🏛️ Architecture

### The Tri-Agent System
1. **The Analyst** (Perception): Ingests real-time data from Cambrian
2. **The Brain** (JEPA Model): Predicts liquidity depth based on governance events
3. **The Strategist** (Ambient LLM): Interprets predictions and formulates risk assessments
4. **The Auditor** (Supervisor): Validates proposed actions for enterprise safety

### Sponsor Tools Integration
- **Cambrian**: Real-time on-chain data ingestion
- **Letta**: Episodic memory for learning from historical crises
- **Ambient**: LLM reasoning for natural language risk analysis
- **Verisense**: A2A protocol compliance and network discoverability

### Technical Implementation
- **ML Framework**: PyTorch for JEPA model
- **Backend**: Starlette (async ASGI server)
- **Frontend**: Streamlit dashboard
- **Storage**: JSON-based persistence
- **Security**: Input validation, rate limiting, circuit breakers

---

## 📋 Project Structure

```
SenseForge/
├── server.py                  # A2A Server (Starlette)
├── agent.json                 # Agent Card (Verisense)
├── config.py                  # Centralized configuration
├── logging_setup.py           # Enterprise logging
├── metrics.py                 # Performance tracking
├── reasoning_logger.py        # Audit trail generation
├── resilience.py             # Circuit breakers, retries
├── ambient_client.py         # Ambient LLM integration
├── perception/
│   └── analyst.py            # Cambrian data ingestion
├── model/
│   ├── jepa.py              # JEPA predictive model
│   └── letta_memory.py      # Letta episodic memory
├── planning/
│   ├── strategist.py        # Ambient LLM reasoning
│   └── auditor.py           # Safety validator
├── security/
│   ├── auth.py              # API key authentication
│   ├── rate_limiter.py      # Rate limiting middleware
│   ├── secrets.py           # Secrets management
│   └── validation.py        # Input sanitization
├── database/
│   └── repository.py        # Checkpoint persistence
├── interface/
│   └── dashboard.py         # Streamlit dashboard
├── tests/
│   ├── test_jepa.py         # JEPA unit tests
│   ├── test_resilience.py   # Resilience tests
│   └── test_integration.py  # End-to-end tests
├── docs/
│   ├── ARCHITECTURE.md       # Technical architecture
│   ├── DEMO_SCRIPT.md        # Demo video script
│   ├── JUDGE_QA.md           # Judge Q&A preparation
│   └── VERISENSE_REGISTRATION.md  # Registration guide
└── scripts/
    ├── generate_training_data.py
    └── train_jepa.py
```

---

## 🔧 Configuration

Environment variables (`.env`):

```bash
# Operating Mode
SENSEFORGE_MODE=mock  # Options: mock, live

# API Keys (Optional - leave empty for mock mode)
CAMBRIAN_API_KEY=your_key_here
LETTA_API_KEY=your_key_here
AMBIENT_API_KEY=your_key_here

# Security
ENABLE_AUTH=false
ENABLE_HTTPS_REDIRECT=false
ALLOWED_HOSTS=*
RATE_LIMIT=100

# Dashboard Settings
SENSEFORGE_REFRESH_INTERVAL=5
```

---

## 📚 Documentation

- **[Technical Architecture](docs/ARCHITECTURE.md)**: Deep dive into system design
- **[Demo Script](docs/DEMO_SCRIPT.md)**: Video production guide
- **[Judge Q&A](docs/JUDGE_QA.md)**: Anticipated questions and answers
- **[Verisense Registration](docs/VERISENSE_REGISTRATION.md)**: Registration walkthrough

---

## 🏆 Hackathon Submission

**Core Requirements Met**:
- ✅ **A2A Compatible**: Registered on Verisense network (ID: `kGjGp...QCcN`)  
- ✅ **4 Sponsor Tools**: Cambrian + Letta + Ambient + Verisense integration
- ✅ **Novel Approach**: JEPA-inspired architecture for predictive modeling  
- ✅ **Autonomous Operation**: Tri-Agent system with safety validation  
- ✅ **Functional Demo**: Working server, dashboard, and test suite
- ✅ **Documentation**: Technical architecture, setup guides, and reasoning logs

**What Makes This Special**:
- Real ML training loop (not just API calls)
- Episodic memory for learning from past events
- Transparent reasoning with audit trails
- Comprehensive error handling and testing

---

## 🧪 Testing

Run the test suite:

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=. --cov-report=html

# Specific test module
pytest tests/test_jepa.py -v
```

---

## 🚀 Running & Testing

### Local Development
```bash
# Start the A2A server
python server.py

# Start the dashboard (separate terminal)
streamlit run interface/dashboard.py
```

### Testing the Agent

**Query the agent**:
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Analyze risk for Proposal PROP-123"}'
```

**View the dashboard**: Open http://localhost:8501

### Run Tests
```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=. --cov-report=html
```

---

## 📄 License

MIT License

---

## 🙏 Acknowledgments

Built for the **"Calling For All Agents!"** Hackathon hosted by Verisense.

**Sponsor Technologies**:
- [Cambrian](https://cambrian.org) - On-chain data access
- [Letta](https://letta.ai) - Episodic memory
- [Ambient](https://ambient.ai) - LLM reasoning
- [Verisense](https://verisense.network) - A2A protocol

---

**Hackathon**: "Calling For All Agents!" by Verisense | **Status**: Submission Ready ✅

