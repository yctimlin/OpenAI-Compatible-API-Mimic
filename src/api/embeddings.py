"""
Embeddings API routes.

This module handles all routes related to embeddings.
"""

from typing import List, Dict, Any
from fastapi import APIRouter
from loguru import logger

from src.models import (
    EmbeddingRequest, 
    EmbeddingResponse,
    UsageInfo
)
from src.utils import get_access_token, request_embedding

router = APIRouter(prefix="/v1", tags=["Embeddings"])


@router.post("/embeddings", response_model=EmbeddingResponse)
def create_embedding(request: EmbeddingRequest):
    """
    Create embeddings for the input text(s).
    
    Args:
        request (EmbeddingRequest): The embedding request.
        
    Returns:
        EmbeddingResponse: The embedding response.
    """
    inputs = request.input
    if isinstance(inputs, str):
        inputs = [inputs]
    elif isinstance(inputs, list) and isinstance(inputs[0], list):
        inputs = inputs[0]
    
    all_embeddings = []
    token = get_access_token()
    
    # Process each input
    for i, text in enumerate(inputs):
        param = dict(
            model=request.model,
            text=text,
            encoding_format=request.encoding_format,
            dimensions=request.dimensions,
            timeout=0.5
        )
        
        # Add user parameter if provided
        if request.user:
            param["user"] = request.user
            
        logger.debug(f"==== embedding request {i} ====\n{param}")
        
        response = request_embedding(token, param)
        
        embedding_data = {
            "object": "embedding",
            "embedding": response['data']['content'],
            "index": i
        }
        all_embeddings.append(embedding_data)
    
    # Calculate token usage (simplified)
    input_tokens = sum(len(str(input_text).split()) for input_text in inputs) * 4  # rough estimate
    
    usage = UsageInfo(
        prompt_tokens=input_tokens,
        total_tokens=input_tokens
    )
    
    return EmbeddingResponse(
        data=all_embeddings,
        model=request.model,
        usage=usage
    ) 