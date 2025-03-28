# Usage Guide

This guide provides detailed instructions on how to use the OpenAI-Compatible API Mimic effectively.

## Table of Contents

- [Configuration](#configuration)
- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
- [Client Libraries](#client-libraries)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)

## Configuration

### Environment Variables

The following environment variables can be configured in your `.env` file:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `TOKEN_URL` | URL to obtain access tokens from your backend | - | Yes |
| `CHAT_API_URL` | Base URL for chat completion API | - | Yes |
| `EMBEDDING_API_URL` | Base URL for embedding API | - | Yes |
| `AUTH_CODE` | Authorization code for token retrieval | - | Yes |
| `VERIFY_SSL` | Whether to verify SSL certificates | True | No |
| `PORT` | Port to run the API server on | 8000 | No |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | INFO | No |

### Configuration Example

```
TOKEN_URL=https://your-backend.com/api/token
CHAT_API_URL=https://your-backend.com/api
EMBEDDING_API_URL=https://your-backend.com/api
AUTH_CODE=your-auth-code
VERIFY_SSL=True
PORT=8000
LOG_LEVEL=INFO
```

## Authentication

The API Mimic handles authentication to your backend internally. When clients connect to the API Mimic, they can use any string as the API key - it is not validated. Instead, the API Mimic will use the configured `AUTH_CODE` to authenticate with your backend.

```python
import openai

# The API key can be any string - it's not validated
client = openai.OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="sk-any-string"  # This is ignored but required by the client
)
```

## API Endpoints

### Chat Completions

The chat completions endpoint follows the OpenAI API specification to create a model response for the given chat conversation.

**Endpoint**: `POST /v1/chat/completions`

**Request Parameters**:

- `model` (string): ID of the model to use (passes through to your backend)
- `messages` (array): A list of messages in the conversation
- `temperature` (number, optional): What sampling temperature to use, between 0 and 2
- `top_p` (number, optional): Alternative to sampling with temperature
- `n` (integer, optional): How many chat completion choices to generate
- `stream` (boolean, optional): If set, partial message deltas will be sent
- `max_tokens` (integer, optional): Maximum number of tokens to generate
- `tools` (array, optional): A list of tools the model may call
- `tool_choice` (string or object, optional): Controls which (if any) tool is called by the model
- `user` (string, optional): A unique identifier representing your end-user

**Example Request**:

```json
{
  "model": "gpt-4o",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Tell me about the solar system."}
  ],
  "temperature": 0.7,
  "max_tokens": 500
}
```

### Embeddings

The embeddings endpoint generates vector representations of input text that can be used for search, clustering, recommendations, and other natural language processing tasks.

**Endpoint**: `POST /v1/embeddings`

**Request Parameters**:

- `model` (string): ID of the model to use (passes through to your backend)
- `input` (string or array): The text to generate embeddings for
- `encoding_format` (string, optional): The format of the output data, either "float" or "base64"
- `dimensions` (integer, optional): The number of dimensions the resulting output embeddings should have
- `user` (string, optional): A unique identifier representing your end-user

**Example Request**:

```json
{
  "model": "text-embedding-3-small",
  "input": "The food was delicious and the service was excellent."
}
```

### Models

The models endpoint lists the available models and provides information about them.

**Endpoint**: `GET /v1/models`

**Response**:

```json
{
  "object": "list",
  "data": [
    {
      "id": "gpt-4o",
      "object": "model",
      "created": 1677610602,
      "owned_by": "openai"
    },
    {
      "id": "gpt-4-turbo",
      "object": "model",
      "created": 1677649963,
      "owned_by": "openai"
    },
    {
      "id": "text-embedding-3-small",
      "object": "model",
      "created": 1677610602,
      "owned_by": "openai"
    }
  ]
}
```

## Client Libraries

### Python

```python
import openai

client = openai.OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="sk-any-string"  # This is ignored but required
)

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"}
    ]
)

print(response.choices[0].message.content)
```

### TypeScript/JavaScript

```typescript
import OpenAI from "openai";

const openai = new OpenAI({
  baseURL: "http://localhost:8000/v1",
  apiKey: "sk-any-string", // This is ignored but required
});

async function main() {
  const completion = await openai.chat.completions.create({
    model: "gpt-4o",
    messages: [
      { role: "system", content: "You are a helpful assistant." },
      { role: "user", content: "What is the capital of France?" }
    ],
  });

  console.log(completion.choices[0].message.content);
}

main();
```

## Advanced Usage

### Streaming Responses

```python
import openai

client = openai.OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="sk-any-string"
)

stream = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Write a short poem about AI."}
    ],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

### Function/Tool Calling

```python
import openai
import json

client = openai.OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="sk-any-string"
)

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"]
                    }
                },
                "required": ["location"]
            }
        }
    }
]

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What's the weather like in Boston?"}
    ],
    tools=tools,
    tool_choice="auto"
)

tool_call = response.choices[0].message.tool_calls[0]
print(f"Function call: {tool_call.function.name}")
print(f"Arguments: {tool_call.function.arguments}")

# Parse the arguments
arguments = json.loads(tool_call.function.arguments)
print(f"Location: {arguments.get('location')}")
print(f"Unit: {arguments.get('unit', 'celsius')}")
```

## Troubleshooting

### Common Issues

#### Invalid Authentication

If you see authentication errors:
1. Check that your `AUTH_CODE` in the `.env` file is correct
2. Verify that the `TOKEN_URL` is accessible and returning valid tokens
3. Check your backend logs for authentication issues

#### Timeout Errors

If requests are timing out:
1. Increase the timeout setting in your client
2. Check if your backend is responding within the expected timeframe
3. For streaming responses, ensure your backend supports streaming

#### Model Not Found

If you receive "model not found" errors:
1. Verify that the model you're requesting is available in your backend
2. Check the response from the `/v1/models` endpoint to see available models
3. Update the model name in your request to match an available model

### Debug Mode

To enable more detailed logging, set the `LOG_LEVEL` environment variable to `DEBUG`:

```
LOG_LEVEL=DEBUG
```

This will output additional information about requests and responses, which can help troubleshoot issues.

### Support Resources

If you encounter issues not covered in this guide:
1. Check the [GitHub Issues](https://github.com/yctimlin/OpenAI-Compatible-API-Mimic/issues) page
2. Search for similar issues or submit a new one
3. Join the community Discord for real-time support 