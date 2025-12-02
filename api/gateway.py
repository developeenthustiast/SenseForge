"""Lightweight API gateway for Vercel.

This module exposes a Starlette app that proxies /query requests to an
external ML service while keeping simple metadata endpoints local.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import aiohttp
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

ML_SERVICE_URL = os.getenv("ML_SERVICE_URL", "https://your-ml-service.railway.app")
AGENT_FILE = Path(__file__).resolve().parent.parent / "agent.json"


async def agent_card(request):  # pylint: disable=unused-argument
    if not AGENT_FILE.exists():
        return JSONResponse({"error": "agent.json missing"}, status_code=500)

    with AGENT_FILE.open("r", encoding="utf-8") as file:
        return JSONResponse(json.load(file))


async def health(request):  # pylint: disable=unused-argument
    return JSONResponse({
        "status": "healthy",
        "gateway": "vercel",
        "ml_service": ML_SERVICE_URL,
    })


async def query(request):
    body = await request.json()

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{ML_SERVICE_URL}/query",
            json=body,
            timeout=aiohttp.ClientTimeout(total=30),
        ) as response:
            result = await response.json()
            return JSONResponse(result, status_code=response.status)


routes = [
    Route("/.well-known/agent.json", agent_card, methods=["GET"]),
    Route("/health", health, methods=["GET"]),
    Route("/query", query, methods=["POST"]),
]

app = Starlette(routes=routes)
