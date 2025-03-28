"""
Configuration settings for the OpenAI-Compatible API.

This module loads environment variables and provides configuration settings
for the API, endpoints, and other components.
"""

import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API configuration
    API_TITLE: str = "OpenAI-Compatible API Mimic"
    API_DESCRIPTION: str = "An API-compatible service that mimics the OpenAI API"
    API_VERSION: str = "1.0.0"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = int(os.getenv("PORT", "8000"))
    
    # Authentication and endpoints
    TOKEN_URL: str = os.getenv("TOKEN_URL", "your_url_to_get_token")
    CHAT_API_URL: str = os.getenv("CHAT_API_URL", "your_url_of_base_api")
    EMBEDDING_API_URL: str = os.getenv("EMBEDDING_API_URL", "your_url_of_base_api")
    AUTH_CODE: str = os.getenv("AUTH_CODE", "your_authorization_code")
    VERIFY_SSL: bool = os.getenv("VERIFY_SSL", "False").lower() in ("true", "1", "t")
    
    # Logging configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # CORS settings
    CORS_ORIGINS: list = ["*"]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: list = ["*"]
    CORS_HEADERS: list = ["*"]


# Create a global settings object
settings = Settings() 