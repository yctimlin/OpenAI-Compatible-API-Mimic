"""
Model utilities for the OpenAI-Compatible API.

This module provides utilities for handling AI models, including
listing available models and their properties.
"""

import time
from typing import List, Dict, Any

from src.models.schema import ModelObject


def get_available_models() -> List[ModelObject]:
    """
    Get a list of all available AI models.
    
    Returns:
        List[ModelObject]: List of available model objects.
    """
    current_time = int(time.time())
    
    models = [
        # GPT-4 models
        ModelObject(id="gpt-4o", created=current_time - 1000),
        ModelObject(id="gpt-4o-mini", created=current_time - 1500),
        ModelObject(id="gpt-4o-audio-preview", created=current_time - 2000),
        ModelObject(id="gpt-4-turbo", created=current_time - 2500),
        ModelObject(id="gpt-4-turbo-preview", created=current_time - 3000),
        ModelObject(id="gpt-4-0125-preview", created=current_time - 3500),
        ModelObject(id="gpt-4-vision-preview", created=current_time - 4000),
        ModelObject(id="gpt-4", created=current_time - 4500),
        
        # GPT-3.5 models
        ModelObject(id="gpt-3.5-turbo-0125", created=current_time - 5000),
        ModelObject(id="gpt-3.5-turbo", created=current_time - 5500),
        
        # Embedding models
        ModelObject(id="text-embedding-3-large", created=current_time - 6000),
        ModelObject(id="text-embedding-3-small", created=current_time - 6500),
        ModelObject(id="text-embedding-ada-002", created=current_time - 7000),
        
        # Audio models
        ModelObject(id="whisper-1", created=current_time - 7500),
        ModelObject(id="tts-1", created=current_time - 8000),
        ModelObject(id="tts-1-hd", created=current_time - 8500),
        
        # Image models
        ModelObject(id="dall-e-3", created=current_time - 9000),
        ModelObject(id="dall-e-2", created=current_time - 9500),
    ]
    
    return models


def get_model_categories() -> Dict[str, List[str]]:
    """
    Get model categories and their available models.
    
    Returns:
        Dict[str, List[str]]: Dictionary of model categories and lists of model IDs.
    """
    return {
        "chat": [
            "gpt-4o", "gpt-4o-mini", "gpt-4o-audio-preview",
            "gpt-4-turbo", "gpt-4-turbo-preview", "gpt-4-0125-preview", 
            "gpt-4-vision-preview", "gpt-4", 
            "gpt-3.5-turbo-0125", "gpt-3.5-turbo"
        ],
        "embedding": [
            "text-embedding-3-large", "text-embedding-3-small", "text-embedding-ada-002"
        ],
        "audio": [
            "whisper-1", "tts-1", "tts-1-hd"
        ],
        "image": [
            "dall-e-3", "dall-e-2"
        ]
    }


def is_streaming_supported(model_id: str) -> bool:
    """
    Check if streaming is supported for the given model.
    
    Args:
        model_id (str): The model ID to check.
        
    Returns:
        bool: True if streaming is supported, False otherwise.
    """
    # All chat models support streaming
    return model_id.lower() in get_model_categories()["chat"]


def is_vision_model(model_id: str) -> bool:
    """
    Check if the model supports vision/multimodal inputs.
    
    Args:
        model_id (str): The model ID to check.
        
    Returns:
        bool: True if the model supports vision, False otherwise.
    """
    vision_models = ["gpt-4-vision-preview", "gpt-4o"]
    return model_id.lower() in vision_models 