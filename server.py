"""
SenseForge A2A Server
Enterprise-grade production server with security, observability, and resilience.
"""
import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.exceptions import HTTPException
import json
import os
import asyncio
import signal
import sys
import uuid
from datetime import datetime
from pathlib import Path
import torch

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

# Import security components
from config.security import api_config
from security.validation import (
    QueryRequest, 
    SecureResponseBuilder,
    validate_api_key
)
from security.rate_limiter import RateLimitMiddleware, RateLimiter
from security.auth import AuthenticationMiddleware

# Import core components
from perception.analyst import AnalystAgent
from model.jepa import LiquidityJEPA
from model.letta_memory import LettaMemory
from planning.strategist import StrategistAgent
from planning.auditor import AuditorAgent
from logging_setup import logger
from metrics import metrics_registry
from reasoning_logger import reasoning_logger

# Load environment
MODE = os.getenv('SENSEFORGE_MODE', 'mock')
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')
ENABLE_AUTH = os.getenv('ENABLE_AUTH', 'false').lower() == 'true'

# Initialize components
analyst = None
jepa = None
memory = None
strategist = None
auditor = None

async def initialize_components():
    """Initialize all agent components"""
    global analyst, jepa, memory, strategist, auditor
    
    logger.info(f"Initializing SenseForge components (mode: {MODE})...")
    
    try:
        analyst = AnalystAgent(mode=MODE)
        
        jepa = LiquidityJEPA(state_dim=3, action_dim=1, latent_dim=16)
        # Try to load existing checkpoint
        checkpoint_path = os.getenv('JEPA_CHECKPOINT', 'checkpoints/jepa_model.pth')
        if os.path.exists(checkpoint_path):
            jepa.load_checkpoint(checkpoint_path)
            logger.info(f"Loaded JEPA checkpoint from {checkpoint_path}")
        
        memory = LettaMemory(agent_id="senseforge-risk-oracle-001", mode=MODE)
        strategist = StrategistAgent(mode=MODE)
        auditor = AuditorAgent()
        
        logger.info("✅ All components initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize components: {e}", exc_info=True)
        raise

async def shutdown_components():
    """Gracefully shutdown all components"""
    logger.info("Shutting down components...")
    
    try:
        if analyst:
            await analyst.cleanup()
        
        if jepa:
            # Save final checkpoint
            jepa.save_checkpoint()
            logger.info("Saved final JEPA checkpoint")
        
        if memory:
            await memory.close()
        
        if strategist:
            await strategist.cleanup()
        
        logger.info("✅ All components shut down successfully")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}", exc_info=True)

# Middleware configuration
middleware = [
    Middleware(GZipMiddleware, minimum_size=1000),
    Middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_HOSTS if ALLOWED_HOSTS != ['*'] else ['*'],
        allow_methods=['GET', 'POST', 'OPTIONS'],
        allow_headers=['*'],
        max_age=600,
    ),
    Middleware(RateLimitMiddleware, rate_limiter=RateLimiter(
        rate=100,  # 100 requests
        per=60,    # per minute
        storage='memory'  # Use Redis in production
    )),
]

if ENABLE_AUTH:
    middleware.append(Middleware(AuthenticationMiddleware))

if ALLOWED_HOSTS != ['*']:
    middleware.append(Middleware(TrustedHostMiddleware, allowed_hosts=ALLOWED_HOSTS))

# Route handlers

async def get_agent_card(request):
    """
    Returns the Agent Card for Verisense network discovery.
    Endpoint: GET /.well-known/agent.json
    """
    try:
        with open("agent.json", "r") as f:
            card = json.load(f)
        
        # Add dynamic information
        card['last_updated'] = datetime.utcnow().isoformat()
        card['status'] = 'online'
        card['mode'] = MODE
        
        return JSONResponse(card)
    
    except Exception as e:
        logger.error(f"Error serving agent card: {e}")
        return JSONResponse(
            {"error": "Agent card unavailable"},
            status_code=500
        )

async def health_check(request):
    """
    Health check endpoint for orchestration.
    Endpoint: GET /health
    """
    request_id = str(uuid.uuid4())
    
    try:
        # Check all components
        components_health = {
            "analyst": "ok" if analyst else "unavailable",
            "jepa": "ok" if jepa else "unavailable",
            "memory": memory.get_memory_stats()['mode'] if memory else "unavailable",
            "strategist": "ok" if strategist else "unavailable",
            "auditor": "ok" if auditor else "unavailable",
        }
        
        all_healthy = all(
            status in ["ok", "mock", "live"] 
            for status in components_health.values()
        )
        
        health = {
            "status": "healthy" if all_healthy else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "mode": MODE,
            "components": components_health,
            "version": "2.0"
        }
        
        status_code = 200 if all_healthy else 503
        
        return JSONResponse(health, status_code=status_code)
    
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return JSONResponse(
            {
                "status": "unhealthy",
                "error": "Health check failed",
                "request_id": request_id
            },
            status_code=503
        )

async def metrics_endpoint(request):
    """
    Prometheus-compatible metrics endpoint.
    Endpoint: GET /metrics
    """
    try:
        metrics_text = metrics_registry.generate()
        return Response(metrics_text, media_type="text/plain")
    
    except Exception as e:
        logger.error(f"Metrics generation failed: {e}")
        return JSONResponse({"error": "Metrics unavailable"}, status_code=500)

async def handle_query(request):
    """
    Handle A2A risk analysis queries.
    Endpoint: POST /query
    
    This implements the core Tri-Agent workflow:
    1. Analyst: Gather and normalize market data
    2. Brain (JEPA): Predict future state
    3. Strategist: Analyze risk using LLM
    4. Auditor: Validate proposed action
    """
    request_id = str(uuid.uuid4())
    start_time = datetime.now()
    
    # Start reasoning chain for audit trail
    reasoning_logger.start_chain(str(request.url))
    
    try:
        # Parse and validate request
        body = await request.json()
        
        # Validate using Pydantic
        try:
            validated_request = QueryRequest(**body)
        except Exception as e:
            logger.warning(f"Invalid request: {e}")
            return JSONResponse(
                SecureResponseBuilder.error_response(
                    error_type="validation_error",
                    message=str(e),
                    request_id=request_id,
                    expose_details=(MODE != 'live')
                ),
                status_code=400
            )
        
        query_text = validated_request.query
        logger.info(f"[{request_id}] Processing query: {query_text[:100]}...")
        
        # Check components are initialized
        if not all([analyst, jepa, strategist, auditor]):
            return JSONResponse(
                SecureResponseBuilder.error_response(
                    error_type="service_unavailable",
                    message="Service is initializing, please retry",
                    request_id=request_id
                ),
                status_code=503
            )
        
        # ===== STEP 1: Analyst - Gather Market Data =====
        step_start = datetime.now()
        
        events_buffer = []
        proposals_buffer = []
        
        # Gather events (limited to prevent timeout)
        timeout_seconds = 5
        try:
            async with asyncio.timeout(timeout_seconds):
                async for event in analyst.stream_liquidity_events():
                    events_buffer.append(event)
                    if len(events_buffer) >= 5:
                        break
        except asyncio.TimeoutError:
            logger.warning(f"Event gathering timed out after {timeout_seconds}s")
        
        # Normalize market state
        current_state = analyst.normalize_state(events_buffer, proposals_buffer)
        
        step_duration = (datetime.now() - step_start).total_seconds() * 1000
        reasoning_logger.log_step(
            component="Analyst",
            input_data={"events_count": len(events_buffer)},
            output_data=current_state.dict(),
            reasoning=f"Normalized {len(events_buffer)} liquidity events into market state",
            confidence=1.0,
            duration_ms=step_duration
        )
        
        # ===== STEP 2: Brain (JEPA) - Predict Future State =====
        step_start = datetime.now()
        
        state_tensor = torch.tensor([[
            current_state.liquidity_depth,
            current_state.volatility_index,
            current_state.governance_risk_score
        ]], dtype=torch.float32)
        
        # Predict what happens if proposal passes
        action_tensor = torch.tensor([[1.0]], dtype=torch.float32)
        predicted_state_tensor = jepa.predict_next_state(state_tensor, action_tensor)
        predicted_liquidity = float(predicted_state_tensor[0][0])
        
        # Calculate prediction confidence based on training history
        confidence = 0.85 if len(jepa.training_history) > 10 else 0.70
        
        step_duration = (datetime.now() - step_start).total_seconds() * 1000
        reasoning_logger.log_step(
            component="Brain (JEPA)",
            input_data={
                "state": current_state.dict(),
                "action": "PASS_PROPOSAL"
            },
            output_data={"predicted_liquidity": predicted_liquidity},
            reasoning=(
                f"JEPA model predicted liquidity change from "
                f"${current_state.liquidity_depth:,.0f} to "
                f"${predicted_liquidity:,.0f}"
            ),
            confidence=confidence,
            duration_ms=step_duration
        )
        
        # ===== STEP 3: Strategist - Analyze Risk =====
        step_start = datetime.now()
        
        strategy = await strategist.analyze_risk(
            current_state.dict(),
            predicted_liquidity
        )
        
        step_duration = (datetime.now() - step_start).total_seconds() * 1000
        reasoning_logger.log_step(
            component="Strategist",
            input_data={
                "current_liquidity": current_state.liquidity_depth,
                "predicted_liquidity": predicted_liquidity
            },
            output_data=strategy,
            reasoning=strategy.get('reasoning', ''),
            confidence=strategy.get('confidence'),
            duration_ms=step_duration
        )
        
        # ===== STEP 4: Auditor - Validate Action =====
        step_start = datetime.now()
        
        audit_result = await auditor.validate_action(strategy)
        
        step_duration = (datetime.now() - step_start).total_seconds() * 1000
        reasoning_logger.log_step(
            component="Auditor",
            input_data=strategy,
            output_data=audit_result,
            reasoning=audit_result.get('auditor_comments', ''),
            confidence=1.0,
            duration_ms=step_duration
        )
        
        # ===== Build Response =====
        
        response_data = {
            "analysis": {
                "current_state": {
                    "liquidity_depth": current_state.liquidity_depth,
                    "volatility_index": current_state.volatility_index,
                    "governance_risk_score": current_state.governance_risk_score,
                },
                "prediction": {
                    "predicted_liquidity": predicted_liquidity,
                    "change_amount": predicted_liquidity - current_state.liquidity_depth,
                    "change_percent": (
                        ((predicted_liquidity - current_state.liquidity_depth) / 
                         current_state.liquidity_depth * 100)
                        if current_state.liquidity_depth > 0 else 0
                    ),
                    "confidence": confidence
                },
                "risk_assessment": strategy,
                "audit_verification": audit_result
            },
            "metadata": {
                "events_processed": len(events_buffer),
                "model_version": "jepa_v2.0",
                "mode": MODE
            }
        }
        
        # Finalize reasoning chain
        total_duration = (datetime.now() - start_time).total_seconds() * 1000
        reasoning_logger.finalize_chain(response_data, total_duration)
        
        # Log metrics
        metrics_registry.track_prediction(
            predicted=predicted_liquidity,
            actual=None,
            request_id=request_id
        )
        
        logger.info(
            f"[{request_id}] Query processed successfully in {total_duration:.2f}ms. "
            f"Risk: {strategy.get('risk_level')}"
        )
        
        return JSONResponse(
            SecureResponseBuilder.success_response(response_data, request_id)
        )
    
    except asyncio.TimeoutError:
        logger.error(f"[{request_id}] Request timeout")
        return JSONResponse(
            SecureResponseBuilder.error_response(
                error_type="timeout",
                message="Request processing timeout",
                request_id=request_id
            ),
            status_code=504
        )
    
    except Exception as e:
        logger.error(f"[{request_id}] Query processing failed: {e}", exc_info=True)
        
        return JSONResponse(
            SecureResponseBuilder.error_response(
                error_type="internal_error",
                message=str(e),
                request_id=request_id,
                expose_details=(MODE != 'live')
            ),
            status_code=500
        )

# Route configuration
routes = [
    Route("/.well-known/agent.json", get_agent_card, methods=["GET"]),
    Route("/health", health_check, methods=["GET"]),
    Route("/metrics", metrics_endpoint, methods=["GET"]),
    Route("/query", handle_query, methods=["POST"]),
]

# Create application
app = Starlette(
    debug=(MODE != 'live'),
    routes=routes,
    middleware=middleware,
    on_startup=[initialize_components],
    on_shutdown=[shutdown_components]
)

# Graceful shutdown handling
def signal_handler(sig, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {sig}, initiating graceful shutdown...")
    
    # Trigger async shutdown
    loop = asyncio.get_event_loop()
    loop.create_task(shutdown_components())
    
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("SenseForge A2A Server v2.0")
    logger.info(f"Mode: {MODE}")
    logger.info(f"Authentication: {'Enabled' if ENABLE_AUTH else 'Disabled'}")
    logger.info("=" * 60)
    
    # SSL/TLS configuration for production
    ssl_config = {}
    if MODE == 'live':
        ssl_keyfile = os.getenv('SSL_KEYFILE')
        ssl_certfile = os.getenv('SSL_CERTFILE')
        
        if ssl_keyfile and ssl_certfile:
ssl_config = {
'ssl_keyfile': ssl_keyfile,
'ssl_certfile': ssl_certfile
}
logger.info("✅ SSL/TLS enabled")
else:
logger.warning("⚠️ SSL/TLS not configured in live mode!")
uvicorn.run(
    app,
    host="0.0.0.0",
    port=int(os.getenv('PORT', 8000)),
    log_level="info" if MODE == 'live' else "debug",
    **ssl_config
)
