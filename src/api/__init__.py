"""
API routes module initialization.

This module exports all API route handlers.
"""

from src.api.chat import router as chat_router
from src.api.embeddings import router as embeddings_router
from src.api.models import router as models_router 