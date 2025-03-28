"""
Chat completion API routes.

This module handles all routes related to chat completions.
"""

import json
import time
import asyncio
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from loguru import logger

from src.models import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionResponseChoice,
    ChatCompletionResponseStreamChoice,
    ChatMessage,
    DeltaMessage,
    ToolCall,
    FunctionCallResponse,
    UsageInfo
)
from src.utils import (
    get_access_token,
    request_chat_api,
    is_streaming_supported
)

router = APIRouter(prefix="/v1", tags=["Chat Completions"])


async def generate_stream_response(gen_params: Dict[str, Any]):
    """
    Generate a streaming response for chat completions.
    
    Args:
        gen_params (Dict[str, Any]): Parameters for the chat completion.
        
    Yields:
        str: Chunks of the streaming response.
    """
    token = get_access_token()
    response = request_chat_api(token, gen_params)
    
    # Simulate streaming response
    finish_reason = "stop"
    content = response["data"]["content"]["content"]
    tool_calls = response["data"]["content"].get("tool_calls", [])
    
    # First chunk with role
    delta = DeltaMessage(role="assistant")
    choice = ChatCompletionResponseStreamChoice(index=0, delta=delta, finish_reason=None)
    yield f"data: {json.dumps(ChatCompletionResponse(model=gen_params['model'], choices=[choice], object='chat.completion.chunk').dict())}\n\n"
    
    # Content chunks (simulate streaming by breaking content into pieces)
    if content:
        chunk_size = max(len(content) // 5, 1)  # Divide content into ~5 chunks
        for i in range(0, len(content), chunk_size):
            chunk = content[i:i+chunk_size]
            delta = DeltaMessage(content=chunk)
            choice = ChatCompletionResponseStreamChoice(index=0, delta=delta, finish_reason=None)
            yield f"data: {json.dumps(ChatCompletionResponse(model=gen_params['model'], choices=[choice], object='chat.completion.chunk').dict())}\n\n"
            await asyncio.sleep(0.05)  # Small delay to simulate streaming
    
    # Tool calls if present
    if tool_calls and isinstance(tool_calls, list):
        finish_reason = "tool_calls"
        delta = DeltaMessage(tool_calls=[ToolCall(
            id=f"call_{time.time()}",
            type="function",
            function=FunctionCallResponse(
                name=tool_call.get("name", ""),
                arguments=tool_call.get("arguments", "{}")
            )
        ) for tool_call in tool_calls])
        choice = ChatCompletionResponseStreamChoice(index=0, delta=delta, finish_reason=None)
        yield f"data: {json.dumps(ChatCompletionResponse(model=gen_params['model'], choices=[choice], object='chat.completion.chunk').dict())}\n\n"
    
    # Final chunk
    delta = DeltaMessage()
    choice = ChatCompletionResponseStreamChoice(index=0, delta=delta, finish_reason=finish_reason)
    yield f"data: {json.dumps(ChatCompletionResponse(model=gen_params['model'], choices=[choice], object='chat.completion.chunk').dict())}\n\n"
    
    # End of stream marker
    yield "data: [DONE]\n\n"


@router.post("/chat/completions", response_model=ChatCompletionResponse)
async def create_chat_completion(request: ChatCompletionRequest):
    """
    Create a chat completion.
    
    Args:
        request (ChatCompletionRequest): The chat completion request.
        
    Returns:
        ChatCompletionResponse: The chat completion response.
    """
    if request.stream and not is_streaming_supported(request.model):
        raise HTTPException(
            status_code=400,
            detail=f"Streaming is not supported for model: {request.model}"
        )
    
    gen_params = dict(
        model=request.model,
        messages=request.messages,
        temperature=request.temperature,
        top_p=request.top_p,
        max_tokens=request.max_tokens or 1024,
        echo=False,
        stream=request.stream,
        repetition_penalty=request.repetition_penalty,
        tools=request.tools,
        tool_choice=request.tool_choice,
        response_format=request.response_format,
        seed=request.seed,
        stop=request.stop
    )
    
    # Add latest parameters if provided
    if request.max_completion_tokens is not None:
        gen_params["max_completion_tokens"] = request.max_completion_tokens
    
    if request.parallel_tool_calls is not None:
        gen_params["parallel_tool_calls"] = request.parallel_tool_calls
        
    if request.prediction is not None:
        gen_params["prediction"] = request.prediction
        
    if request.stream_options is not None:
        gen_params["stream_options"] = request.stream_options
        
    if request.reasoning_effort is not None:
        gen_params["reasoning_effort"] = request.reasoning_effort
    
    if request.user is not None:
        gen_params["user"] = request.user

    logger.debug(f"==== request ====\n{gen_params}")
    
    # Handle streaming response
    if request.stream:
        return StreamingResponse(
            generate_stream_response(gen_params),
            media_type="text/event-stream"
        )
    
    # Handle normal response
    token = get_access_token()
    response = request_chat_api(token, gen_params)

    logger.debug(f"==== response ====\n{response}")

    usage = UsageInfo()
    finish_reason = "stop"
    
    # Check for tool_calls in the response
    tool_calls_data = response["data"]["content"].get("tool_calls", [])
    
    formatted_tool_calls = None
    if tool_calls_data and isinstance(tool_calls_data, list):
        finish_reason = "tool_calls"
        formatted_tool_calls = [
            ToolCall(
                id=f"call_{i}_{int(time.time())}",
                type="function",
                function=FunctionCallResponse(
                    name=tool_call.get("name", ""),
                    arguments=tool_call.get("arguments", "{}")
                )
            ) for i, tool_call in enumerate(tool_calls_data)
        ]

    # Handle different content types (text vs. multimodal)
    content = response["data"]["content"].get("content")
    
    message = ChatMessage(
        role="assistant",
        content=content,
        tool_calls=formatted_tool_calls,
    )

    logger.debug(f"==== message ====\n{message}")

    choice_data = ChatCompletionResponseChoice(
        index=0,
        message=message,
        finish_reason=finish_reason,
    )
    
    return ChatCompletionResponse(
        id=f"chatcmpl-{int(time.time())}",
        model=request.model, 
        choices=[choice_data], 
        object="chat.completion", 
        usage=usage
    ) 