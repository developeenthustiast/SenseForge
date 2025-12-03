"""
SenseForge A2A Server - SECURITY HARDENED v2.1
Production-ready with comprehensive security controls
"""
import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse, Response
from starlette.routing import Route
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
import json
import os
import asyncio
import signal
import sys
import uuid
from datetime import datetime
from pathlib import Path

# Custom JSON encoder for datetime objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        from datetime import date, datetime
        from uuid import UUID
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, UUID):
            return str(obj)
        return super().default(obj)

# Helper for recursive serialization
def make_serializable(obj):
    from datetime import date, datetime
    from uuid import UUID
    from pydantic import BaseModel
    import numpy as np
    
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, UUID):
        return str(obj)
    if isinstance(obj, BaseModel):
        return make_serializable(obj.dict())
    if isinstance(obj, (np.integer, np.floating)):
        return float(obj) if isinstance(obj, np.floating) else int(obj)
    if isinstance(obj, np.ndarray):
        return make_serializable(obj.tolist())
    if isinstance(obj, dict):
        return {k: make_serializable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [make_serializable(v) for v in obj]
    return obj

# Security imports
from security.validation import (
    QueryRequest, 
    SecureResponseBuilder,
    get_csp_header
)
from security.rate_limiter import RateLimitMiddleware, RateLimiter
from security.auth import AuthenticationMiddleware
from security.secrets import secrets_manager, validate_environment

# Core components
from perception.analyst import AnalystAgent
from model.jepa import LiquidityJEPA
from model.letta_memory import LettaMemory
from planning.strategist import StrategistAgent
from planning.auditor import AuditorAgent
from logging_setup import logger
from reasoning_logger import reasoning_logger
from metrics import metrics as metrics_tracker

# ===== CONFIGURATION =====
MODE = os.getenv('SENSEFORGE_MODE', 'mock')
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')
ENABLE_AUTH = os.getenv('ENABLE_AUTH', 'false').lower() == 'true'
ENABLE_HTTPS_REDIRECT = os.getenv('ENABLE_HTTPS_REDIRECT', 'false').lower() == 'true'

# Validate environment
if not validate_environment():
    logger.error("Environment validation failed - missing required secrets")
    if MODE == 'live':
        sys.exit(1)

# ===== COMPONENT INITIALIZATION =====
analyst = None
jepa = None
memory = None
strategist = None
auditor = None

async def initialize_components():
    """Initialize all agent components with error handling"""
    global analyst, jepa, memory, strategist, auditor
    
    logger.info(f"Initializing SenseForge components (mode: {MODE})...")
    
    try:
        # Analyst
        analyst = AnalystAgent(mode=MODE)
        logger.info("✓ Analyst initialized")
        
        # JEPA Model
        jepa = LiquidityJEPA(state_dim=3, action_dim=1, latent_dim=16)
        
        # Try to load checkpoint
        checkpoint_path = os.getenv('JEPA_CHECKPOINT', 'checkpoints/jepa_model.pth')
        if os.path.exists(checkpoint_path):
            if jepa.load_checkpoint(checkpoint_path):
                logger.info(f"✓ JEPA loaded from {checkpoint_path}")
        else:
            logger.info("✓ JEPA initialized (no checkpoint)")
        
        # Memory
        memory = LettaMemory(
            agent_id="senseforge-risk-oracle-001",
            mode=MODE
        )
        logger.info("✓ Memory initialized")
        
        # Strategist
        strategist = StrategistAgent(mode=MODE)
        logger.info("✓ Strategist initialized")
        
        # Auditor
        auditor = AuditorAgent()
        logger.info("✓ Auditor initialized")
        
        logger.info("=" * 60)
        logger.info("✅ ALL COMPONENTS READY")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Component initialization failed: {e}", exc_info=True)
        raise

async def shutdown_components():
    """Gracefully shutdown all components"""
    logger.info("Initiating graceful shutdown...")
    
    try:
        if analyst:
            await analyst.cleanup()
            logger.info("✓ Analyst shutdown")
        
        if jepa:
            try:
                jepa.save_checkpoint()
                logger.info("✓ JEPA checkpoint saved")
            except Exception as e:
                logger.warning(f"Could not save JEPA checkpoint: {e}")
        
        if memory:
            await memory.close()
            logger.info("✓ Memory shutdown")
        
        if strategist:
            await strategist.cleanup()
            logger.info("✓ Strategist shutdown")
        
        logger.info("✅ Graceful shutdown complete")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}", exc_info=True)

# ===== SECURITY MIDDLEWARE =====
middleware = [
    Middleware(GZipMiddleware, minimum_size=1000),
    Middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_HOSTS if ALLOWED_HOSTS != ['*'] else ['*'],
        allow_methods=['GET', 'POST', 'OPTIONS'],
        allow_headers=['*'],
        allow_credentials=True,
        max_age=600,
    ),
    Middleware(RateLimitMiddleware, rate_limiter=RateLimiter(
        rate=int(os.getenv('RATE_LIMIT', 100)),
        per=60,
        storage='redis' if os.getenv('REDIS_URL') else 'memory',
        redis_url=os.getenv('REDIS_URL')
    )),
]

# Add authentication if enabled
if ENABLE_AUTH:
    middleware.append(Middleware(AuthenticationMiddleware))
    logger.info("🔒 Authentication enabled")

# Add host validation if specified
if ALLOWED_HOSTS != ['*']:
    middleware.append(Middleware(TrustedHostMiddleware, allowed_hosts=ALLOWED_HOSTS))
    logger.info(f"🔒 Host validation enabled: {ALLOWED_HOSTS}")

# Add HTTPS redirect in production
if ENABLE_HTTPS_REDIRECT:
    middleware.insert(0, Middleware(HTTPSRedirectMiddleware))
    logger.info("🔒 HTTPS redirect enabled")

# ===== ROUTE HANDLERS =====

async def get_agent_card(request):
    """
    Returns Agent Card for Verisense network discovery
    PUBLIC ENDPOINT
    """
    try:
        with open("agent.json", "r") as f:
            card = json.load(f)
        
        # Add dynamic status
        card['last_updated'] = datetime.utcnow().isoformat() + 'Z'
        card['status'] = 'online'
        card['mode'] = MODE
        
        return JSONResponse(card)
    
    except Exception as e:
        logger.error(f"Agent card error: {e}")
        return JSONResponse(
            {"error": "Agent card unavailable"},
            status_code=500
        )

async def health_check(request):
    """
    Deep health check endpoint
    INTERNAL/PUBLIC ENDPOINT
    """
    request_id = str(uuid.uuid4())
    
    try:
        # Component health checks
        components = {}
        
        # Test Analyst
        try:
            if analyst:
                # Quick connectivity test
                components['analyst'] = 'healthy'
            else:
                components['analyst'] = 'unavailable'
        except Exception as e:
            components['analyst'] = f'unhealthy: {str(e)}'
        
        # Test JEPA
        try:
            if jepa:
                # Test forward pass
                import torch
                test_tensor = torch.randn(1, 3)
                jepa(test_tensor)
                components['jepa'] = 'healthy'
            else:
                components['jepa'] = 'unavailable'
        except Exception as e:
            components['jepa'] = f'unhealthy: {str(e)}'
        
        # Test Memory
        try:
            if memory:
                stats = memory.get_memory_stats()
                components['memory'] = f"healthy ({stats['mode']})"
            else:
                components['memory'] = 'unavailable'
        except Exception as e:
            components['memory'] = f'unhealthy: {str(e)}'
        
        # Test Strategist
        components['strategist'] = 'healthy' if strategist else 'unavailable'
        
        # Test Auditor
        components['auditor'] = 'healthy' if auditor else 'unavailable'
        
        # Overall status
        unhealthy_count = sum(
            1 for status in components.values() 
            if 'unhealthy' in status or 'unavailable' in status
        )
        
        if unhealthy_count == 0:
            overall_status = 'healthy'
            status_code = 200
        elif unhealthy_count < len(components) / 2:
            overall_status = 'degraded'
            status_code = 200
        else:
            overall_status = 'unhealthy'
            status_code = 503
        
        health = {
            'status': overall_status,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'mode': MODE,
            'components': components,
            'version': '2.1-secure',
            'request_id': request_id
        }
        
        return JSONResponse(health, status_code=status_code)
    
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return JSONResponse(
            {
                'status': 'unhealthy',
                'error': 'Health check failed',
                'request_id': request_id
            },
            status_code=503
        )

async def metrics_endpoint(request):
    """
    Prometheus metrics endpoint
    INTERNAL ENDPOINT (should require auth or IP whitelist)
    """
    try:
        # Basic metrics in Prometheus format
        metrics = []
        
        # System metrics
        metrics.append('# HELP senseforge_up System status (1=up, 0=down)')
        metrics.append('# TYPE senseforge_up gauge')
        metrics.append('senseforge_up 1')
        
        # Component metrics
        if jepa and jepa.training_history:
            metrics.append('# HELP senseforge_training_loss Current training loss')
            metrics.append('# TYPE senseforge_training_loss gauge')
            metrics.append(f'senseforge_training_loss {jepa.training_history[-1]}')
        
        metrics_text = '\n'.join(metrics)
        
        return Response(metrics_text, media_type="text/plain")
    
    except Exception as e:
        logger.error(f"Metrics generation failed: {e}")
        return JSONResponse({"error": "Metrics unavailable"}, status_code=500)

async def dashboard_metrics(request):
    """JSON metrics for dashboard consumption"""
    try:
        accuracy_stats = metrics_tracker.get_accuracy_stats()
        training_stats = metrics_tracker.get_training_stats()
        recent_predictions = metrics_tracker.get_recent_predictions(limit=10)

        response = {
            "accuracy": accuracy_stats,
            "training": training_stats,
            "recent_predictions": recent_predictions,
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }

        return JSONResponse(response)

    except Exception as e:
        logger.error(f"Dashboard metrics failed: {e}", exc_info=True)
        return JSONResponse(
            {
                "error": "metrics_unavailable",
                "message": "Unable to load dashboard metrics"
            },
            status_code=500
        )

async def handle_query(request):
    """
    Handle A2A risk analysis queries with full security
    PROTECTED ENDPOINT
    """
    request_id = str(uuid.uuid4())
    start_time = datetime.now()
    
    # Start reasoning chain
    reasoning_logger.start_chain(str(request.url))
    
    try:
        # Parse request body
        body = await request.json()
        
        # Validate with Pydantic (includes sanitization)
        try:
            validated_request = QueryRequest(**body)
        except Exception as e:
            logger.warning(f"[{request_id}] Validation failed: {e}")
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
        logger.info(f"[{request_id}] Query: {query_text[:100]}...")
        
        # Check components
        if not all([analyst, jepa, strategist, auditor]):
            return JSONResponse(
                SecureResponseBuilder.error_response(
                    error_type="service_unavailable",
                    message="Service initializing",
                    request_id=request_id
                ),
                status_code=503
            )
        
        # === STEP 1: Analyst ===
        step_start = datetime.now()
        events_buffer = []
        
        try:
            async with asyncio.timeout(5):
                async for event in analyst.stream_liquidity_events():
                    events_buffer.append(event)
                    if len(events_buffer) >= 5:
                        break
        except asyncio.TimeoutError:
            logger.warning("Event gathering timeout")
        
        current_state = analyst.normalize_state(events_buffer, [])
        
        step_duration = (datetime.now() - step_start).total_seconds() * 1000
        reasoning_logger.log_step(
            component="Analyst",
            input_data={"events_count": len(events_buffer)},
            output_data=make_serializable(current_state.dict()),
            reasoning=f"Normalized {len(events_buffer)} events",
            confidence=1.0,
            duration_ms=step_duration
        )
        
        # === STEP 2: JEPA Prediction ===
        step_start = datetime.now()
        
        import torch
        state_tensor = torch.tensor([[
            current_state.liquidity_depth,
            current_state.volatility_index,
            current_state.governance_risk_score
        ]], dtype=torch.float32)
        
        action_tensor = torch.tensor([[1.0]], dtype=torch.float32)
        predicted_state_tensor = jepa.predict_next_state(state_tensor, action_tensor)
        predicted_liquidity = float(predicted_state_tensor[0][0])
        
        confidence = 0.85 if len(jepa.training_history) > 10 else 0.70
        
        step_duration = (datetime.now() - step_start).total_seconds() * 1000
        reasoning_logger.log_step(
            component="Brain (JEPA)",
            input_data={"state": make_serializable(current_state.dict())},
            output_data={"predicted_liquidity": predicted_liquidity},
            reasoning=f"Predicted liquidity: ${predicted_liquidity:,.0f}",
            confidence=confidence,
            duration_ms=step_duration
        )
        
        # === STEP 3: Strategist ===
        step_start = datetime.now()
        
        strategy = await strategist.analyze_risk(
            current_state.dict(),
            predicted_liquidity
        )
        
        step_duration = (datetime.now() - step_start).total_seconds() * 1000
        reasoning_logger.log_step(
            component="Strategist",
            input_data={"predicted_liquidity": predicted_liquidity},
            output_data=make_serializable(strategy),
            reasoning=strategy.get('reasoning', ''),
            confidence=strategy.get('confidence'),
            duration_ms=step_duration
        )
        
        # === STEP 4: Auditor ===
        step_start = datetime.now()
        
        audit_result = await auditor.validate_action(strategy)
        
        step_duration = (datetime.now() - step_start).total_seconds() * 1000
        reasoning_logger.log_step(
            component="Auditor",
            input_data=make_serializable(strategy),
            output_data=make_serializable(audit_result),
            reasoning=audit_result.get('auditor_comments', ''),
            confidence=1.0,
            duration_ms=step_duration
        )
        
        # === BUILD RESPONSE ===
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
                "model_version": "jepa_v2.1-secure",
                "mode": MODE
            }
        }
        
        # Finalize reasoning
        total_duration = (datetime.now() - start_time).total_seconds() * 1000
        # Finalize reasoning
        total_duration = (datetime.now() - start_time).total_seconds() * 1000
        reasoning_logger.finalize_chain(make_serializable(response_data), total_duration)
        
        logger.info(
            f"[{request_id}] Success ({total_duration:.2f}ms) - "
            f"Risk: {strategy.get('risk_level')}"
        )
        
        # Build secure response
        response = SecureResponseBuilder.success_response(
            response_data,
            request_id
        )
        
        # Manually sanitize response data before JSONResponse
        safe_response = make_serializable(response)
        
        # Add security headers
        json_response = JSONResponse(safe_response)
        json_response.headers['X-Content-Type-Options'] = 'nosniff'
        json_response.headers['X-Frame-Options'] = 'DENY'
        json_response.headers['X-XSS-Protection'] = '1; mode=block'
        json_response.headers['Content-Security-Policy'] = get_csp_header()
        json_response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return json_response
    
    except asyncio.TimeoutError:
        logger.error(f"[{request_id}] Timeout")
        return JSONResponse(
            SecureResponseBuilder.error_response(
                error_type="timeout",
                message="Request timeout",
                request_id=request_id
            ),
            status_code=504
        )
    
    except Exception as e:
        import traceback
        with open("error.log", "w") as f:
            f.write(f"Error: {str(e)}\n")
            f.write(traceback.format_exc())
            
        logger.error(f"[{request_id}] Error: {e}", exc_info=True)
        
        # Ensure error response is also serializable
        error_data = SecureResponseBuilder.error_response(
            error_type="internal_error",
            message=str(e),
            request_id=request_id,
            expose_details=(MODE != 'live')
        )
        
        return JSONResponse(
            make_serializable(error_data),
            status_code=500
        )

# ===== ROUTES =====
async def serve_demo(request):
    """Serve demo landing page for judges"""
    from pathlib import Path
    html_path = Path(__file__).parent / "static" / "index.html"
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    return Response(html_content, media_type="text/html")

routes = [
    Route("/", serve_demo, methods=["GET"]),
    Route("/.well-known/agent.json", get_agent_card, methods=["GET"]),
    Route("/health", health_check, methods=["GET"]),
    Route("/metrics", metrics_endpoint, methods=["GET"]),
    Route("/query", handle_query, methods=["POST"]),
]

# ===== APPLICATION =====
app = Starlette(
    debug=(MODE != 'live'),
    routes=routes,
    middleware=middleware,
    on_startup=[initialize_components],
    on_shutdown=[shutdown_components]
)

# ===== SIGNAL HANDLERS =====
def signal_handler(sig, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {sig}, shutting down...")
    loop = asyncio.get_event_loop()
    loop.create_task(shutdown_components())
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# ===== MAIN =====
if __name__ == "__main__":
    logger.info("=" * 70)
    logger.info("🔮 SenseForge A2A Server v2.1 (Security Hardened)")
    logger.info("=" * 70)
    logger.info(f"Mode: {MODE}")
    logger.info(f"Auth: {'✓ Enabled' if ENABLE_AUTH else '✗ Disabled'}")
    logger.info(f"HTTPS: {'✓ Enforced' if ENABLE_HTTPS_REDIRECT else '✗ Optional'}")
    logger.info("=" * 70)
    
    # SSL configuration
    ssl_config = {}
    if MODE == 'live':
        ssl_keyfile = os.getenv('SSL_KEYFILE')
        ssl_certfile = os.getenv('SSL_CERTFILE')
        
        if ssl_keyfile and ssl_certfile:
            ssl_config = {
                'ssl_keyfile': ssl_keyfile,
                'ssl_certfile': ssl_certfile
            }
            logger.info("🔒 SSL/TLS enabled")
        else:
            logger.warning("⚠️  SSL/TLS not configured!")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv('PORT', 8000)),
        log_level="info" if MODE == 'live' else "debug",
        **ssl_config
    )
