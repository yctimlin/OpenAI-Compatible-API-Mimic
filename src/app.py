"""
Main application module.

This is the main entry point for the OpenAI-Compatible API Mimic service,
which configures the FastAPI application and includes all routes.
"""

import sys
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from src.config.settings import settings
from src.api import chat_router, embeddings_router, models_router


# Configure logging
logger.remove()
logger.add(
    sys.stderr,
    level=settings.LOG_LEVEL,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)

# Include API routers
app.include_router(chat_router)
app.include_router(embeddings_router)
app.include_router(models_router)


@app.get("/", tags=["Health"])
async def root():
    """
    Root endpoint, serves as a health check.
    
    Returns:
        dict: Basic API information.
    """
    return {
        "service": settings.API_TITLE,
        "version": settings.API_VERSION,
        "status": "healthy",
        "documentation": "/docs"
    }


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware to log all incoming requests.
    
    Args:
        request (Request): The incoming request.
        call_next: The next middleware or route handler.
        
    Returns:
        Response: The response from the next middleware or route handler.
    """
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    return response 