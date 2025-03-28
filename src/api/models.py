"""
Models API routes.

This module handles all routes related to model listing and information.
"""

from fastapi import APIRouter, HTTPException, Path
from loguru import logger

from src.models import ModelListResponse, ModelObject
from src.utils import get_available_models

router = APIRouter(prefix="/v1", tags=["Models"])


@router.get("/models", response_model=ModelListResponse)
def list_models():
    """
    List all available models.
    
    Returns:
        ModelListResponse: List of available models.
    """
    models = get_available_models()
    logger.debug(f"Returning {len(models)} models")
    
    return ModelListResponse(data=models)


@router.get("/models/{model_id}", response_model=ModelObject)
def get_model(model_id: str = Path(..., description="The ID of the model to retrieve")):
    """
    Get information about a specific model.
    
    Args:
        model_id (str): The ID of the model to retrieve.
        
    Returns:
        ModelObject: Information about the model.
        
    Raises:
        HTTPException: If the model is not found.
    """
    models = get_available_models()
    
    for model in models:
        if model.id.lower() == model_id.lower():
            logger.debug(f"Found model: {model_id}")
            return model
    
    # If the model is not found, raise a 404 error
    logger.warning(f"Model not found: {model_id}")
    raise HTTPException(status_code=404, detail=f"Model '{model_id}' not found") 