# app/database.py - Simplified for Vercel (no actual database)
from fastapi import Depends
from typing import Optional, Dict, Any

# This is a placeholder - no real database connection
async def get_db():
    """
    Simple dependency that doesn't use a real database.
    For Vercel deployment, we're using in-memory storage.
    """
    # Just yield a simple dict instead of database session
    yield {"db": "placeholder", "status": "no-database-mode"}

# No database models or connections needed