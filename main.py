"""
Main entry point for the OpenAI-Compatible API Mimic.

This script runs the FastAPI application using uvicorn.
Run this file to start the API server.
"""

import uvicorn
from src.config.settings import settings

if __name__ == "__main__":
    """Run the API server."""
    uvicorn.run(
        "src.app:app", 
        host=settings.APP_HOST, 
        port=settings.APP_PORT,
        reload=True
    ) 