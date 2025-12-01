# Verisense Dashboard Registration Guide

**Purpose**: Register SenseForge as an A2A-compliant agent on the Verisense network.

---

## Prerequisites

Before registering, ensure:

- ✅ Agent is running locally (`python server.py`)
- ✅ Agent Card is accessible at `http://localhost:8000/.well-known/agent.json`
- ✅ You have a wallet (MetaMask or similar) for authentication
- ✅ Agent is deployed on a public URL (or use ngrok for testing)

---

## Step 1: Deploy Agent Publicly (If Testing Locally)

### Option A: Using ngrok (Recommended for Testing)

```bash
# Install ngrok (if not installed)
# Download from https://ngrok.com/download

# Start your agent server
python server.py

# In a new terminal, create public tunnel
ngrok http 8000
```

**Output**:
```
Forwarding  https://abc123.ngrok.io -> http://localhost:8000
```

**Copy the HTTPS URL** (e.g., `https://abc123.ngrok.io`)

### Option B: Deploy to Production

Deploy to a cloud provider with a public IP:
- **Render**: https://render.com
- **Railway**: https://railway.app
- **Fly.io**: https://fly.io
- **AWS/GCP/Azure**: Traditional cloud deployment

---

## Step 2: Verify Agent Card is Accessible

Test your agent card endpoint:

```bash
# Test locally first
curl http://localhost:8000/.well-known/agent.json

# Test public URL
curl https://YOUR-PUBLIC-URL/.well-known/agent.json
```

**Expected Response**:
```json
{
  "id": "senseforge-risk-oracle",
  "name": "SenseForge Risk Oracle",
  "description": "Autonomous liquidity risk prediction for DeFi protocols",
  "url": "https://YOUR-PUBLIC-URL",
  "capabilities": [
    "protocol.verisense.risk-analysis",
    "protocol.verisense.liquidity-prediction"
  ]
}
```

---

## Step 3: Access Verisense Dashboard

1. Navigate to: **https://dashboard.verisense.network/**

2. **Connect Wallet**
   - Click "Connect Wallet" button (top right)
   - Select MetaMask (or your preferred wallet)
   - Approve connection
   - Sign the authentication message

---

## Step 4: Register Your Agent

### Navigate to Registration

1. Click **"Register Agent"** or **"Add Agent"** (from dashboard menu)
2. You'll see a registration form

### Fill in Agent Details

**Agent URL**: `https://YOUR-PUBLIC-URL`
- Example: `https://abc123.ngrok.io` (ngrok)
- Example: `https://senseforge.onrender.com` (Render)

**Agent Card Verification**:
- The dashboard will automatically fetch `/.well-known/agent.json` from your URL
- It will parse and display your agent's metadata

**Verify Information**:
- **Name**: SenseForge Risk Oracle
- **ID**: senseforge-risk-oracle
- **Capabilities**: risk-analysis, liquidity-prediction

### Submit Registration

1. Review all details
2. Click **"Register"** or **"Submit"**
3. **Sign the transaction** (if required - may involve a blockchain tx)
4. Wait for confirmation

---

## Step 5: Verify Registration

### Check Agent Status

1. Go to **"My Agents"** or **"Dashboard"**
2. You should see **SenseForge Risk Oracle** listed
3. Status should show: ✅ **Active** or **Verified**

### Test A2A Discoverability

```bash
# Query Verisense network for your agent
# (Exact API may vary - check Verisense docs)
curl https://api.verisense.network/agents/search?capability=risk-analysis
```

Your agent should appear in the results.

---

## Step 6: Test Cross-Agent Communication

### Send a Test Query

If Verisense provides a test interface:

1. Go to **"Test Agent"** section
2. Select your agent: **SenseForge Risk Oracle**
3. Send a test query:
   ```json
   {
     "query": "Analyze risk for test proposal"
   }
   ```
4. Verify you receive a response

### Via Command Line

```bash
# Direct query to your agent
curl -X POST https://YOUR-PUBLIC-URL/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Analyze risk for Proposal PROP-123"}'
```

---

## Troubleshooting

### Issue 1: Agent Card Not Found

**Error**: `Failed to fetch agent card`

**Solution**:
- Ensure server is running: `python server.py`
- Check URL is correct (include `https://`)
- Verify firewall/CORS settings allow external access
- Test manually: `curl https://YOUR-URL/.well-known/agent.json`

### Issue 2: Invalid Agent Card Format

**Error**: `Agent card schema validation failed`

**Solution**:
- Validate `agent.json` format
- Ensure all required fields are present:
  - `id` (string)
  - `name` (string)
  - `description` (string)
  - `url` (string, must match registration URL)
  - `capabilities` (array of strings)

### Issue 3: ngrok URL Changes

**Problem**: ngrok URLs are temporary and change on restart

**Solutions**:
- **Paid ngrok**: Get a static domain
- **Deploy to Cloud**: Use a permanent URL (Render, Railway, etc.)
- **Update Registration**: Re-register with new ngrok URL each time

### Issue 4: Wallet Connection Issues

**Error**: `Failed to connect wallet`

**Solution**:
- Ensure MetaMask is installed and unlocked
- Switch to correct network (check Verisense requirements)
- Clear cache and try again
- Try a different browser

---

## Production Deployment Checklist

Before final registration:

- [ ] Agent deployed on stable, public URL
- [ ] SSL/TLS enabled (HTTPS)
- [ ] Agent Card endpoint tested and accessible
- [ ] Query endpoint returns valid responses
- [ ] Logging enabled for monitoring
- [ ] Error handling tested (circuit breakers, retries)
- [ ] Wallet connected to Verisense Dashboard
- [ ] Agent registered and verified

---

## Need Help?

- **Verisense Docs**: https://docs.verisense.network/
- **Verisense Discord**: (Check hackathon materials)
- **GitHub Issues**: https://github.com/verisense/docs/issues
- **Hackathon Support**: (Check "Calling For All Agents!" Discord)

---

## Quick Reference

| Step | Action | Command/URL |
|---|---|---|
| 1 | Start server | `python server.py` |
| 2 | Create tunnel | `ngrok http 8000` |
| 3 | Test locally | `curl http://localhost:8000/.well-known/agent.json` |
| 4 | Access dashboard | https://dashboard.verisense.network/ |
| 5 | Register agent | Paste ngrok URL, submit |
| 6 | Verify | Check "My Agents" section |

---

**Last Updated**: December 2025  
**Version**: 1.0
