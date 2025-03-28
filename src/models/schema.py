"""
Schema definitions for the OpenAI-Compatible API.

This module contains all the Pydantic models for request and response schemas
used in the API endpoints, matching the official OpenAI API specifications.
"""

import time
from typing import List, Literal, Optional, Union, Dict, Any
from pydantic import BaseModel, Field


class FunctionCallResponse(BaseModel):
    """Schema for function call responses in tool calls."""
    arguments: Optional[str] = None
    name: Optional[str] = None


class ToolCall(BaseModel):
    """Schema for tool calls in chat completions."""
    id: str
    type: str = "function"
    function: FunctionCallResponse


class ContentPart(BaseModel):
    """Schema for multimodal content parts in messages."""
    type: str
    text: Optional[str] = None
    image_url: Optional[Dict[str, str]] = None


class ChatMessage(BaseModel):
    """Schema for chat messages in completions."""
    role: Literal["user", "assistant", "system", "tool"]
    content: Union[str, List[ContentPart], None] = None
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None


class DeltaMessage(BaseModel):
    """Schema for delta messages in streaming responses."""
    role: Optional[Literal["user", "assistant", "system", "tool"]] = None
    content: Optional[Union[str, List[ContentPart]]] = None
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None


class ChatCompletionRequest(BaseModel):
    """Schema for chat completion requests."""
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
    user: Optional[str] = None  # For tracking


class ChatCompletionResponseChoice(BaseModel):
    """Schema for chat completion response choices."""
    index: int
    message: ChatMessage
    finish_reason: Optional[Literal["stop", "length", "function_call", "content_filter", "tool_calls"]] = None


class ChatCompletionResponseStreamChoice(BaseModel):
    """Schema for streaming chat completion response choices."""
    index: int
    delta: DeltaMessage
    finish_reason: Optional[Literal["stop", "length", "function_call", "content_filter", "tool_calls"]] = None


class UsageInfo(BaseModel):
    """Schema for token usage information."""
    prompt_tokens: int = 0
    total_tokens: int = 0
    completion_tokens: Optional[int] = 0


class ChatCompletionResponse(BaseModel):
    """Schema for chat completion responses."""
    id: str = Field(default_factory=lambda: f"chatcmpl-{int(time.time())}")
    model: str
    object: Literal["chat.completion", "chat.completion.chunk"]
    choices: List[Union[ChatCompletionResponseChoice, ChatCompletionResponseStreamChoice]]
    created: Optional[int] = Field(default_factory=lambda: int(time.time()))
    usage: Optional[UsageInfo] = None


class EmbeddingRequest(BaseModel):
    """Schema for embedding requests."""
    input: Union[str, List[str], List[int], List[List[int]]]
    model: str = "text-embedding-ada-002"
    encoding_format: Optional[Literal["float", "base64"]] = "float"
    dimensions: Optional[int] = None
    user: Optional[str] = None  # For tracking in the Azure OpenAI platform


class EmbeddingResponse(BaseModel):
    """Schema for embedding responses."""
    object: str = "list"
    data: List[Dict[str, Any]] = None
    model: str = "text-embedding-ada-002"
    usage: Optional[UsageInfo] = None


class ModelObject(BaseModel):
    """Schema for model objects."""
    id: str
    object: str = "model"
    created: int = Field(default_factory=lambda: int(time.time()))
    owned_by: str = "openai"


class ModelListResponse(BaseModel):
    """Schema for model list responses."""
    object: str = "list"
    data: List[ModelObject] = [] 