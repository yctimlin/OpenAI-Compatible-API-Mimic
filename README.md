# OpenAI-Compatible API Mimic

## Introduction

This project provides a mimic API compatible with OpenAI's official API. It enables users to transform requests into callable OpenAI official API commands. This tool is particularly useful for developers who wish to integrate OpenAI's AI functionalities into their applications with ease.

## Features

- **API Compatibility:** Ensures compatibility with OpenAI's API version 1.35 and above, including support for tool calls.
- **Flexible Integration with Frameworks:** Designed for easy integration with various frameworks, including Langchain, to enhance AI application development.
- **Chat and Embedding Endpoints:** Supports chat completion and embedding functionalities.
- **Token Management:** Automated token refresh for uninterrupted service.
- **Docker Support:** Containerized for easy deployment and scalability.
- **FastAPI Framework:** Built using FastAPI for high performance and easy asynchronous support.

## Getting Started

### Prerequisites

Ensure you have Docker installed on your system to run the application as a container. Alternatively, you can run it directly with Python (version 3.9 or later).

### Installation

1. Clone the repository:

2. Navigate to the cloned directory:

3. To run using Docker:
   ```
   docker build -t openai-api-mimic .
   docker run -p 8000:8000 openai-api-mimic
   ```
   Or to run directly with Python:
   ```
   pip install -r requirements.txt
   python app.py
   ```

### Usage

Send POST requests to `/v1/chat/completions` for chat completions and `/v1/embeddings` for embeddings.

used in Langchain:
```
from langchain.chat_models import ChatOpenAI

llm = ChatOpenAI(openai_api_base="http://127.0.0.1:8000/v1",
                 openai_api_key="None",
                 model="gpt-35-turbo-16k")