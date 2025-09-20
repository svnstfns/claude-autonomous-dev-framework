#!/usr/bin/env python3
"""
Claude Autonomous Development Framework - Core Server
Coordinates Claude Code CLI operations with memory integration
"""

import os
import sys
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import redis
import uvicorn

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
MEMORY_SERVICE_URL = os.getenv('MEMORY_SERVICE_URL', 'https://memory-service:8443/mcp')
REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379')
FRAMEWORK_ENV = os.getenv('FRAMEWORK_ENV', 'development')
PORT = int(os.getenv('FRAMEWORK_PORT', 8080))

# FastAPI app
app = FastAPI(
    title="Claude Autonomous Development Framework",
    description="Core orchestration service for memory-enhanced development",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global clients
memory_client = None
redis_client = None

# Request/Response Models
class AgentRequest(BaseModel):
    agent_name: str
    task_description: str
    context: Optional[Dict[str, Any]] = None

class MemoryStoreRequest(BaseModel):
    content: str
    tags: List[str]
    context: Optional[Dict[str, Any]] = None

class MemoryRetrieveRequest(BaseModel):
    query: str
    limit: int = 10
    tags: Optional[List[str]] = None

class FrameworkStatus(BaseModel):
    status: str
    version: str
    environment: str
    services: Dict[str, str]
    uptime: str

# Memory Integration
class MemoryService:
    def __init__(self, service_url: str):
        self.service_url = service_url
        self.client = httpx.AsyncClient(verify=False)

    async def store_memory(self, content: str, tags: List[str], metadata: Optional[Dict] = None) -> Dict:
        """Store memory with framework context"""
        try:
            response = await self.client.post(
                self.service_url,
                json={
                    "method": "tools/call",
                    "params": {
                        "name": "store_memory",
                        "arguments": {
                            "content": content,
                            "tags": tags,
                            "metadata": metadata
                        }
                    }
                },
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Memory store error: {e}")
            raise HTTPException(status_code=500, detail=f"Memory storage failed: {str(e)}")

    async def retrieve_memory(self, query: str, limit: int = 10, tags: Optional[List[str]] = None) -> Dict:
        """Retrieve memory with context"""
        try:
            response = await self.client.post(
                self.service_url,
                json={
                    "method": "tools/call",
                    "params": {
                        "name": "retrieve_memory",
                        "arguments": {
                            "query": query,
                            "limit": limit,
                            "tags": tags
                        }
                    }
                },
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Memory retrieve error: {e}")
            raise HTTPException(status_code=500, detail=f"Memory retrieval failed: {str(e)}")

# Agent Coordination
class AgentCoordinator:
    def __init__(self, memory_service: MemoryService):
        self.memory = memory_service
        self.active_agents = {}

    async def execute_agent_task(self, agent_name: str, task: str, context: Optional[Dict] = None) -> Dict:
        """Execute task with specified agent and store context"""
        try:
            # Store task initiation context
            await self.memory.store_memory(
                content=f"Agent task initiated: {agent_name} - {task}",
                tags=["agent-task", "initiation", agent_name, "framework"],
                metadata={"context": context, "timestamp": datetime.now().isoformat()}
            )

            # Execute agent task (placeholder - would integrate with actual agent execution)
            result = {
                "agent": agent_name,
                "task": task,
                "status": "executed",
                "context": context,
                "timestamp": datetime.now().isoformat()
            }

            # Store task completion context
            await self.memory.store_memory(
                content=f"Agent task completed: {agent_name} - {task}",
                tags=["agent-task", "completion", agent_name, "framework"],
                metadata={"result": result, "timestamp": datetime.now().isoformat()}
            )

            return result

        except Exception as e:
            logger.error(f"Agent execution error: {e}")
            # Store error context
            await self.memory.store_memory(
                content=f"Agent task failed: {agent_name} - {task} - Error: {str(e)}",
                tags=["agent-task", "failure", agent_name, "framework"],
                metadata={"error": str(e), "timestamp": datetime.now().isoformat()}
            )
            raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")

# Initialize services
async def initialize_services():
    global memory_client, redis_client

    try:
        # Initialize memory service
        memory_client = MemoryService(MEMORY_SERVICE_URL)
        logger.info(f"Memory service initialized: {MEMORY_SERVICE_URL}")

        # Initialize Redis client
        try:
            redis_client = redis.from_url(REDIS_URL)
            redis_client.ping()
            logger.info(f"Redis connected: {REDIS_URL}")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            redis_client = None

        # Store framework startup context
        await memory_client.store_memory(
            content=f"Claude Autonomous Development Framework started in {FRAMEWORK_ENV} mode",
            tags=["framework", "startup", "system", FRAMEWORK_ENV],
            metadata={"port": PORT, "timestamp": datetime.now().isoformat()}
        )

    except Exception as e:
        logger.error(f"Service initialization failed: {e}")

# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    services = {
        "memory": "unknown",
        "redis": "unknown",
        "framework": "healthy"
    }

    # Check memory service
    try:
        if memory_client:
            test_response = await memory_client.client.post(
                memory_client.service_url,
                json={
                    "method": "tools/call",
                    "params": {
                        "name": "check_database_health",
                        "arguments": {}
                    }
                },
                timeout=5.0
            )
            if test_response.status_code == 200:
                services["memory"] = "healthy"
            else:
                services["memory"] = "unhealthy"
    except:
        services["memory"] = "unreachable"

    # Check Redis
    try:
        if redis_client:
            redis_client.ping()
            services["redis"] = "healthy"
    except:
        services["redis"] = "unhealthy"

    return {
        "status": "healthy",
        "services": services,
        "timestamp": datetime.now().isoformat(),
        "version": "0.1.0",
        "environment": FRAMEWORK_ENV
    }

@app.get("/status")
async def get_status():
    """Get comprehensive framework status"""
    return FrameworkStatus(
        status="operational",
        version="0.1.0",
        environment=FRAMEWORK_ENV,
        services={
            "memory": "integrated",
            "redis": "connected" if redis_client else "disconnected",
            "framework": "running"
        },
        uptime=datetime.now().isoformat()
    )

@app.post("/memory/store")
async def store_memory(request: MemoryStoreRequest):
    """Store information in framework memory"""
    if not memory_client:
        raise HTTPException(status_code=503, detail="Memory service not available")

    result = await memory_client.store_memory(
        content=request.content,
        tags=request.tags,
        metadata=request.context
    )
    return result

@app.post("/memory/retrieve")
async def retrieve_memory(request: MemoryRetrieveRequest):
    """Retrieve information from framework memory"""
    if not memory_client:
        raise HTTPException(status_code=503, detail="Memory service not available")

    result = await memory_client.retrieve_memory(
        query=request.query,
        limit=request.limit,
        tags=request.tags
    )
    return result

@app.post("/agents/execute")
async def execute_agent(request: AgentRequest):
    """Execute agent task with memory integration"""
    if not memory_client:
        raise HTTPException(status_code=503, detail="Memory service not available")

    coordinator = AgentCoordinator(memory_client)
    result = await coordinator.execute_agent_task(
        agent_name=request.agent_name,
        task=request.task_description,
        context=request.context
    )
    return result

@app.get("/agents/list")
async def list_agents():
    """List available agents"""
    agents = [
        "chief-architect",
        "code-implementer",
        "docs-researcher",
        "implementation-planner",
        "requirements-engineer",
        "requirements-tracker",
        "system-architect",
        "task-distributor",
        "test-automation"
    ]
    return {"agents": agents, "count": len(agents)}

# Startup event
@app.on_event("startup")
async def startup_event():
    await initialize_services()
    logger.info("Claude Autonomous Development Framework started")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    if memory_client:
        await memory_client.store_memory(
            content=f"Claude Autonomous Development Framework shutdown at {datetime.now().isoformat()}",
            tags=["framework", "shutdown", "system"],
            metadata={"timestamp": datetime.now().isoformat()}
        )
        await memory_client.client.aclose()
    logger.info("Claude Autonomous Development Framework stopped")

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT,
        log_level="info"
    )