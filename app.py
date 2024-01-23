import os
import time
from contextlib import asynccontextmanager
from typing import List, Literal, Optional, Union
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from pydantic import BaseModel, Field

from utils import get_access_token, request_chat_api, request_embedding

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


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system", "tool"]
    content: Union[str, None] = None
    tool_calls: Optional[List] = None


class DeltaMessage(BaseModel):
    role: Optional[Literal["user", "assistant", "system"]] = None
    content: Optional[str] = None
    function_call: Optional[FunctionCallResponse] = None


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[dict]
    temperature: Optional[float] = 0.8
    top_p: Optional[float] = 0.8
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False
    tools: Optional[Union[dict, List[dict]]] = None
    # Additional parameters
    repetition_penalty: Optional[float] = 1.1
    tool_choice: Optional[str] = 'auto'


class ChatCompletionResponseChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: Literal["stop", "length", "function_call"]


class ChatCompletionResponseStreamChoice(BaseModel):
    index: int
    delta: DeltaMessage
    finish_reason: Optional[Literal["stop", "length", "function_call"]]


class UsageInfo(BaseModel):
    prompt_tokens: int = 0
    total_tokens: int = 0
    completion_tokens: Optional[int] = 0


class ChatCompletionResponse(BaseModel):
    model: str
    object: Literal["chat.completion", "chat.completion.chunk"]
    choices: List[Union[ChatCompletionResponseChoice, ChatCompletionResponseStreamChoice]]
    created: Optional[int] = Field(default_factory=lambda: int(time.time()))
    usage: Optional[UsageInfo] = None


@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
def create_chat_completion(request: ChatCompletionRequest):
    
    gen_params = dict(
        model=request.model,
        messages=request.messages,
        temperature=request.temperature,
        top_p=request.top_p,
        max_tokens=request.max_tokens or 1024,
        echo=False,
        stream=None,
        repetition_penalty=request.repetition_penalty,
        tools=request.tools,
        tool_choice=request.tool_choice
    )

    logger.debug(f"==== request ====\n{gen_params}")
    token = get_access_token()
    response = request_chat_api(token, gen_params)

    logger.debug(f"==== response ====\n{response}")

    usage = UsageInfo()
    finish_reason = "stop"
    tool_calls = response["data"]["content"]["tool_calls"]

    if isinstance(tool_calls, list):
        finish_reason = "function_call"

    message = ChatMessage(
        role="assistant",
        content=response["data"]["content"]["content"],
        tool_calls=tool_calls if isinstance(tool_calls, list) else None,
    )

    logger.debug(f"==== message ====\n{message}")

    choice_data = ChatCompletionResponseChoice(
        index=0,
        message=message,
        finish_reason=finish_reason,
    )
    return ChatCompletionResponse(model=request.model, choices=[choice_data], object="chat.completion", usage=usage)


class EmbeddingResponse(BaseModel):
    object: str="embedding"
    data: list=None
    model: str="text-embedding-ada-002"
    usage: Optional[UsageInfo] = None

class EmbeddingRequest(BaseModel):
    input: Union[str, List[str], List[int], List[List[int]]]
    model: Literal["text-embedding-ada-002"]
    encoding_format: Literal["float", "base64"]

@app.post("/v1/embeddings", response_model=EmbeddingResponse)
def create_embedding(request: EmbeddingRequest):
    if isinstance(request.input, list) and isinstance(request.input[0], list):
        request.input = request.input[0]
    param = dict(
        model=request.model,
        text=request.input,
        encoding_format=request.encoding_format,
        timeout=0.5
    )
    logger.debug(f"==== request ====\n{param}")
    token = get_access_token()
    response = request_embedding(token, param)
    return EmbeddingResponse(data=[response['data']['content']])


if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8000, workers=1)