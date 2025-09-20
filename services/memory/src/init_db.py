#!/usr/bin/env python3
"""
Database initialization for Claude Memory Service
"""

import os
import sys
import sqlite3
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_memory_database():
    """Initialize the memory database with required tables and indexes"""

    db_path = os.getenv('MEMORY_DB_PATH', '/app/data/memories.db')

    try:
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        logger.info("Initializing Claude Memory Database...")

        # Create memories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                tags TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT,
                content_hash TEXT,
                embedding BLOB
            )
        """)

        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON memories(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_updated_at ON memories(updated_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tags ON memories(tags)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_content_hash ON memories(content_hash)")

        # Create full-text search table
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
                id UNINDEXED,
                content,
                tags,
                content = memories,
                content_rowid = rowid
            )
        """)

        # Create framework metadata table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS framework_metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Insert initial framework metadata
        cursor.execute("""
            INSERT OR REPLACE INTO framework_metadata (key, value)
            VALUES (?, ?)
        """, ("database_version", "1.0.0"))

        cursor.execute("""
            INSERT OR REPLACE INTO framework_metadata (key, value)
            VALUES (?, ?)
        """, ("initialized_at", datetime.now().isoformat()))

        cursor.execute("""
            INSERT OR REPLACE INTO framework_metadata (key, value)
            VALUES (?, ?)
        """, ("framework_name", "claude-autonomous-dev-framework"))

        # Commit changes
        conn.commit()
        conn.close()

        logger.info(f"✅ Memory database initialized successfully at: {db_path}")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        return False

if __name__ == "__main__":
    success = init_memory_database()
    sys.exit(0 if success else 1)