#!/usr/bin/env python3
"""
Claude Memory Service - MCP Protocol Implementation
Semantic memory storage with SQLite-vec backend
"""

import os
import sys
import json
import sqlite3
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
DB_PATH = os.getenv('MEMORY_DB_PATH', '/app/data/memories.db')
PORT = int(os.getenv('MCP_SERVER_PORT', 8443))
HOST = '0.0.0.0'

# FastAPI app
app = FastAPI(
    title="Claude Memory Service",
    description="Memory service for Claude Autonomous Development Framework",
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

# Pydantic models
class StoreMemoryRequest(BaseModel):
    content: str
    tags: List[str]
    metadata: Optional[Dict[str, Any]] = None

class RetrieveMemoryRequest(BaseModel):
    query: str
    limit: int = 10
    tags: Optional[List[str]] = None

class Memory(BaseModel):
    id: str
    content: str
    tags: List[str]
    created_at: str
    metadata: Optional[Dict[str, Any]] = None

# Database operations
class MemoryDatabase:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initialize database with required tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create memories table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    tags TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            """)

            # Create index for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON memories(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tags ON memories(tags)")

            conn.commit()
            conn.close()
            logger.info(f"Database initialized at {self.db_path}")

        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise

    def store_memory(self, content: str, tags: List[str], metadata: Optional[Dict] = None) -> str:
        """Store a memory entry"""
        memory_id = f"mem_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO memories (id, content, tags, metadata)
                VALUES (?, ?, ?, ?)
            """, (
                memory_id,
                content,
                json.dumps(tags),
                json.dumps(metadata) if metadata else None
            ))

            conn.commit()
            conn.close()
            logger.info(f"Memory stored: {memory_id}")
            return memory_id

        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            raise

    def retrieve_memories(self, query: str, limit: int = 10, tags: Optional[List[str]] = None) -> List[Dict]:
        """Retrieve memories based on query"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Simple text search for now (can be enhanced with semantic search)
            sql = """
                SELECT id, content, tags, created_at, metadata
                FROM memories
                WHERE content LIKE ?
            """
            params = [f"%{query}%"]

            if tags:
                tag_conditions = " OR ".join(["tags LIKE ?" for _ in tags])
                sql += f" AND ({tag_conditions})"
                params.extend([f"%{tag}%" for tag in tags])

            sql += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)

            cursor.execute(sql, params)
            rows = cursor.fetchall()
            conn.close()

            results = []
            for row in rows:
                results.append({
                    "id": row[0],
                    "content": row[1],
                    "tags": json.loads(row[2]),
                    "created_at": row[3],
                    "metadata": json.loads(row[4]) if row[4] else None
                })

            logger.info(f"Retrieved {len(results)} memories for query: {query}")
            return results

        except Exception as e:
            logger.error(f"Failed to retrieve memories: {e}")
            raise

# Initialize database
db = MemoryDatabase(DB_PATH)

# API endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "claude-memory-service", "timestamp": datetime.now().isoformat()}

@app.post("/mcp")
async def mcp_endpoint(request: Dict[str, Any]):
    """MCP protocol endpoint"""
    try:
        method = request.get("method")
        params = request.get("params", {})

        if method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})

            if tool_name == "store_memory":
                content = arguments.get("content")
                tags = arguments.get("tags", [])
                metadata = arguments.get("metadata")

                if not content:
                    raise HTTPException(status_code=400, detail="Content is required")

                memory_id = db.store_memory(content, tags, metadata)
                return {
                    "success": True,
                    "memory_id": memory_id,
                    "message": "Memory stored successfully"
                }

            elif tool_name == "retrieve_memory":
                query = arguments.get("query")
                limit = arguments.get("limit", 10)
                tags = arguments.get("tags")

                if not query:
                    raise HTTPException(status_code=400, detail="Query is required")

                results = db.retrieve_memories(query, limit, tags)
                return {
                    "success": True,
                    "results": results,
                    "count": len(results)
                }

            elif tool_name == "check_database_health":
                # Simple health check for database
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM memories")
                count = cursor.fetchone()[0]
                conn.close()

                return {
                    "success": True,
                    "database_status": "healthy",
                    "total_memories": count,
                    "database_path": DB_PATH
                }

            else:
                raise HTTPException(status_code=400, detail=f"Unknown tool: {tool_name}")

        else:
            raise HTTPException(status_code=400, detail=f"Unsupported method: {method}")

    except Exception as e:
        logger.error(f"MCP endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    """Get memory service statistics"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM memories")
        total_memories = cursor.fetchone()[0]

        cursor.execute("SELECT created_at FROM memories ORDER BY created_at DESC LIMIT 1")
        latest = cursor.fetchone()
        latest_memory = latest[0] if latest else None

        conn.close()

        return {
            "total_memories": total_memories,
            "latest_memory": latest_memory,
            "database_path": DB_PATH,
            "uptime": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Stats endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    logger.info(f"Starting Claude Memory Service on {HOST}:{PORT}")
    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        ssl_keyfile=None,  # For development - use proper SSL in production
        ssl_certfile=None,
        log_level="info"
    )