import os
import json
import time
import asyncio
from contextlib import asynccontextmanager
from typing import List, Literal, Optional, Union, Dict, Any
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from loguru import logger
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from utils import get_access_token, request_chat_api, request_embedding

# Load environment variables
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FunctionCallResponse(BaseModel):
    arguments: Optional[str] = None
    name: Optional[str] = None


class ToolCall(BaseModel):
    id: str
    type: str = "function"
    function: FunctionCallResponse


class ContentPart(BaseModel):
    type: str
    text: Optional[str] = None
    image_url: Optional[Dict[str, str]] = None


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system", "tool"]
    content: Union[str, List[ContentPart], None] = None
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None


class DeltaMessage(BaseModel):
    role: Optional[Literal["user", "assistant", "system", "tool"]] = None
    content: Optional[Union[str, List[ContentPart]]] = None
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[dict]
    temperature: Optional[float] = 0.8
    top_p: Optional[float] = 0.8
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False
    tools: Optional[List[dict]] = None
    # Additional parameters
    repetition_penalty: Optional[float] = 1.1
    tool_choice: Optional[Union[str, dict]] = 'auto'
    response_format: Optional[Dict[str, str]] = None
    seed: Optional[int] = None
    stop: Optional[Union[str, List[str]]] = None
    # Latest parameters (2024-10-21 and above)
    max_completion_tokens: Optional[int] = None  # For o1 series models
    parallel_tool_calls: Optional[bool] = None
    prediction: Optional[Dict[str, Any]] = None  # For predicted outputs
    stream_options: Optional[Dict[str, Any]] = None
    reasoning_effort: Optional[float] = None  # For reasoning models


class ChatCompletionResponseChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: Optional[Literal["stop", "length", "function_call", "content_filter", "tool_calls"]] = None


class ChatCompletionResponseStreamChoice(BaseModel):
    index: int
    delta: DeltaMessage
    finish_reason: Optional[Literal["stop", "length", "function_call", "content_filter", "tool_calls"]] = None


class UsageInfo(BaseModel):
    prompt_tokens: int = 0
    total_tokens: int = 0
    completion_tokens: Optional[int] = 0


class ChatCompletionResponse(BaseModel):
    id: str = Field(default_factory=lambda: f"chatcmpl-{int(time.time())}")
    model: str
    object: Literal["chat.completion", "chat.completion.chunk"]
    choices: List[Union[ChatCompletionResponseChoice, ChatCompletionResponseStreamChoice]]
    created: Optional[int] = Field(default_factory=lambda: int(time.time()))
    usage: Optional[UsageInfo] = None


async def generate_stream_response(gen_params):
    token = get_access_token()
    response = request_chat_api(token, gen_params)
    
    # Simulate streaming response
    finish_reason = "stop"
    content = response["data"]["content"]["content"]
    tool_calls = response["data"]["content"]["tool_calls"]
    
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
    if isinstance(tool_calls, list):
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


@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def create_chat_completion(request: ChatCompletionRequest):
    
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


class EmbeddingResponse(BaseModel):
    object: str = "list"
    data: List[Dict[str, Any]] = None
    model: str = "text-embedding-ada-002"
    usage: Optional[UsageInfo] = None


class EmbeddingRequest(BaseModel):
    input: Union[str, List[str], List[int], List[List[int]]]
    model: str = "text-embedding-ada-002"
    encoding_format: Optional[Literal["float", "base64"]] = "float"
    dimensions: Optional[int] = None
    user: Optional[str] = None  # For tracking in the Azure OpenAI platform


@app.post("/v1/embeddings", response_model=EmbeddingResponse)
def create_embedding(request: EmbeddingRequest):
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


# Models list endpoint
@app.get("/v1/models")
def list_models():
    """Return a list of available models"""
    current_time = int(time.time())
    models = [
        # GPT-4 models
        {
            "id": "gpt-4o",
            "object": "model",
            "created": current_time - 1000,
            "owned_by": "openai"
        },
        {
            "id": "gpt-4o-mini",
            "object": "model", 
            "created": current_time - 1500,
            "owned_by": "openai"
        },
        {
            "id": "gpt-4o-audio-preview",
            "object": "model",
            "created": current_time - 2000,
            "owned_by": "openai"
        },
        {
            "id": "gpt-4-turbo",
            "object": "model",
            "created": current_time - 2500,
            "owned_by": "openai"
        },
        {
            "id": "gpt-4-turbo-preview",
            "object": "model",
            "created": current_time - 3000,
            "owned_by": "openai"
        },
        {
            "id": "gpt-4-0125-preview",
            "object": "model",
            "created": current_time - 3500,
            "owned_by": "openai"
        },
        {
            "id": "gpt-4-vision-preview",
            "object": "model",
            "created": current_time - 4000,
            "owned_by": "openai"
        },
        {
            "id": "gpt-4",
            "object": "model",
            "created": current_time - 4500,
            "owned_by": "openai"
        },
        
        # GPT-3.5 models
        {
            "id": "gpt-3.5-turbo-0125",
            "object": "model",
            "created": current_time - 5000,
            "owned_by": "openai"
        },
        {
            "id": "gpt-3.5-turbo",
            "object": "model",
            "created": current_time - 5500,
            "owned_by": "openai"
        },
        
        # Embedding models
        {
            "id": "text-embedding-3-large",
            "object": "model",
            "created": current_time - 6000,
            "owned_by": "openai"
        },
        {
            "id": "text-embedding-3-small",
            "object": "model",
            "created": current_time - 6500,
            "owned_by": "openai"
        },
        {
            "id": "text-embedding-ada-002",
            "object": "model",
            "created": current_time - 7000,
            "owned_by": "openai"
        },
        
        # Audio models
        {
            "id": "whisper-1",
            "object": "model", 
            "created": current_time - 7500,
            "owned_by": "openai"
        },
        {
            "id": "tts-1",
            "object": "model", 
            "created": current_time - 8000,
            "owned_by": "openai"
        },
        {
            "id": "tts-1-hd",
            "object": "model", 
            "created": current_time - 8500,
            "owned_by": "openai"
        },
        
        # Image models
        {
            "id": "dall-e-3",
            "object": "model", 
            "created": current_time - 9000,
            "owned_by": "openai"
        },
        {
            "id": "dall-e-2",
            "object": "model", 
            "created": current_time - 9500,
            "owned_by": "openai"
        }
    ]
    
    return {
        "object": "list",
        "data": models
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host='0.0.0.0', port=port, workers=1)