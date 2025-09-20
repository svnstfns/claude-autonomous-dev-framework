#!/usr/bin/env python3
"""
Claude Autonomous Development Framework - Dashboard Service
Real-time monitoring and reporting interface
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import httpx
import uvicorn

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
FRAMEWORK_API_URL = os.getenv('FRAMEWORK_API_URL', 'http://framework:8080')
MEMORY_API_URL = os.getenv('MEMORY_API_URL', 'https://memory-service:8443/mcp')
PORT = int(os.getenv('DASHBOARD_PORT', 8081))

# FastAPI app
app = FastAPI(
    title="Claude Framework Dashboard",
    description="Real-time monitoring and reporting for Claude Autonomous Development Framework",
    version="0.1.0"
)

# Templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# HTTP clients
framework_client = httpx.AsyncClient(timeout=10.0)
memory_client = httpx.AsyncClient(verify=False, timeout=10.0)

@app.get("/health")
async def health_check():
    """Dashboard health check"""
    return {
        "status": "healthy",
        "service": "dashboard",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request):
    """Main dashboard view"""
    try:
        # Get framework status
        framework_status = await get_framework_status()

        # Get recent memory entries
        recent_memories = await get_recent_memories()

        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "framework_status": framework_status,
            "recent_memories": recent_memories,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": str(e)
        })

@app.get("/api/status")
async def get_status():
    """Get comprehensive system status"""
    try:
        framework_status = await get_framework_status()
        memory_stats = await get_memory_stats()

        return {
            "framework": framework_status,
            "memory": memory_stats,
            "dashboard": {
                "status": "operational",
                "uptime": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Status API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/metrics")
async def get_metrics():
    """Get framework metrics"""
    try:
        return {
            "agents": await get_agent_metrics(),
            "memory": await get_memory_metrics(),
            "system": await get_system_metrics()
        }
    except Exception as e:
        logger.error(f"Metrics API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions
async def get_framework_status():
    """Get framework service status"""
    try:
        response = await framework_client.get(f"{FRAMEWORK_API_URL}/status")
        return response.json()
    except Exception as e:
        logger.warning(f"Framework status error: {e}")
        return {"status": "unreachable", "error": str(e)}

async def get_recent_memories(limit: int = 10):
    """Get recent memory entries"""
    try:
        response = await memory_client.post(
            MEMORY_API_URL,
            json={
                "method": "tools/call",
                "params": {
                    "name": "retrieve_memory",
                    "arguments": {
                        "query": "framework recent",
                        "limit": limit
                    }
                }
            }
        )
        result = response.json()
        return result.get("results", [])
    except Exception as e:
        logger.warning(f"Memory retrieval error: {e}")
        return []

async def get_memory_stats():
    """Get memory service statistics"""
    try:
        response = await memory_client.get(f"{MEMORY_API_URL}/stats")
        return response.json()
    except Exception as e:
        logger.warning(f"Memory stats error: {e}")
        return {"status": "unreachable", "error": str(e)}

async def get_agent_metrics():
    """Get agent execution metrics"""
    try:
        response = await framework_client.get(f"{FRAMEWORK_API_URL}/agents/list")
        agents = response.json()
        return {"available_agents": agents.get("count", 0), "agents": agents.get("agents", [])}
    except Exception as e:
        logger.warning(f"Agent metrics error: {e}")
        return {"status": "unreachable", "error": str(e)}

async def get_memory_metrics():
    """Get memory usage metrics"""
    try:
        memories = await get_recent_memories(100)
        return {
            "recent_entries": len(memories),
            "last_update": datetime.now().isoformat()
        }
    except Exception as e:
        logger.warning(f"Memory metrics error: {e}")
        return {"status": "error", "error": str(e)}

async def get_system_metrics():
    """Get system performance metrics"""
    return {
        "uptime": datetime.now().isoformat(),
        "status": "operational"
    }

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT,
        log_level="info"
    )