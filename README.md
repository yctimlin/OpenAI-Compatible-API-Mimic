# 🤖 OpenAI-Compatible API Mimic

<div align="center">
  
![OpenAI-Compatible API Mimic](https://raw.githubusercontent.com/yctimlin/OpenAI-Compatible-API-Mimic/main/.github/banner.png)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.0%2B-green.svg)](https://fastapi.tiangolo.com/)
[![OpenAI Compatible](https://img.shields.io/badge/OpenAI-Compatible-orange.svg)](https://platform.openai.com/docs/api-reference)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![GitHub stars](https://img.shields.io/github/stars/yctimlin/OpenAI-Compatible-API-Mimic?style=social)](https://github.com/yctimlin/OpenAI-Compatible-API-Mimic/stargazers)
[![Twitter Follow](https://img.shields.io/twitter/follow/yctimlin?style=social)](https://twitter.com/yctimlin)

**Drop-in replacement for the OpenAI API that works with any backend**
</div>

A powerful, modular proxy service that mimics the OpenAI API interface, allowing you to transform requests to any OpenAI-compatible backend while maintaining full compatibility with applications that use the OpenAI API. Perfect for AI teams working with custom LLM deployments, private models, or alternative providers.

## 🌟 Features

- **Complete OpenAI API Compatibility:** Ensures compatibility with OpenAI's API version 2024-10-21 and above, including support for:
  - ✅ Chat completions with streaming
  - ✅ Function/tool calling with structured outputs
  - ✅ JSON mode responses
  - ✅ Multimodal content (vision models)
  - ✅ Text-to-speech and speech-to-text
  - ✅ Image generation (DALL-E)
  - ✅ Latest OpenAI models support (GPT-4o, GPT-4-turbo, etc.)
  - ✅ Third-generation embeddings models
  - ✅ Full models discovery API

- **Seamless Framework Integration:** Works with any client that supports the OpenAI API:
  - ✅ Official OpenAI SDKs (Python, Node.js, etc.)
  - ✅ LangChain & LangChain.js
  - ✅ LlamaIndex
  - ✅ Semantic Kernel
  - ✅ Any other OpenAI-compatible framework

- **Enterprise-Ready:**
  - ✅ Modular, maintainable code architecture
  - ✅ Comprehensive logging
  - ✅ Error handling with automatic token refresh
  - ✅ Easy configuration through environment variables
  - ✅ Docker containerization for simple deployment
  - ✅ Built on FastAPI for high performance

## 📋 Table of Contents

- [Features](#-features)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Configuration](#configuration)
  - [Installation](#installation)
  - [Running Locally](#running-locally)
  - [Docker Deployment](#docker-deployment)
- [Project Structure](#-project-structure)
- [API Documentation](#-api-documentation)
- [Usage Examples](#-usage-examples)
- [Community & Support](#-community--support)
- [Roadmap](#-roadmap)
- [FAQ](#-faq)
- [Contributing](#-contributing)
- [License](#-license)

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- Docker (optional, for containerized deployment)

### Configuration

Create a `.env` file in the root directory with the following variables:

```
TOKEN_URL=your_url_to_get_token
CHAT_API_URL=your_url_of_base_api
EMBEDDING_API_URL=your_url_of_base_api
AUTH_CODE=your_authorization_code
VERIFY_SSL=False
PORT=8000
LOG_LEVEL=INFO
```

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yctimlin/OpenAI-Compatible-API-Mimic.git
   cd OpenAI-Compatible-API-Mimic
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

   Or use our setup script:
   ```bash
   ./setup.sh
   ```

### Running Locally

Start the API server:

```bash
python main.py
```

The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`.

### Docker Deployment

1. Build the Docker image:
   ```bash
   docker build -t openai-api-mimic .
   ```

2. Run the container:
   ```bash
   docker run -p 8000:8000 --env-file .env openai-api-mimic
   ```

## 📂 Project Structure

```
openai-api-mimic/
├── src/                    # Source code directory
│   ├── api/                # API route definitions
│   │   ├── chat.py         # Chat completions endpoint
│   │   ├── embeddings.py   # Embeddings endpoint
│   │   └── models.py       # Models listing endpoint
│   ├── config/             # Configuration management
│   │   └── settings.py     # Application settings
│   ├── models/             # Pydantic schema definitions
│   │   └── schema.py       # Request/response schemas
│   ├── utils/              # Utility functions
│   │   ├── api.py          # API interaction utilities
│   │   └── models.py       # Model handling utilities
│   ├── app.py              # FastAPI application instance
│   └── __init__.py         # Package initialization
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── Dockerfile              # Container definition
├── .env.example            # Example environment variables
└── README.md               # Project documentation
```

## 📚 API Documentation

Once the server is running, you can access the interactive API documentation at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### API Endpoints

- **GET /**  
  Health check endpoint

- **GET /v1/models**  
  List all available models

- **GET /v1/models/{model_id}**  
  Get information about a specific model

- **POST /v1/chat/completions**  
  Create a chat completion

- **POST /v1/embeddings**  
  Create embeddings from input text

## 🧩 Usage Examples

### Python with OpenAI SDK

```python
import openai

client = openai.OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="dummy-key"  # API key is not validated but required by the SDK
)

# Chat completion
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"}
    ],
    temperature=0.7
)

print(response.choices[0].message.content)

# Streaming example
for chunk in client.chat.completions.create(
    model="gpt-4-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Write a short poem about AI."}
    ],
    stream=True
):
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")

# Embeddings
embedding_response = client.embeddings.create(
    model="text-embedding-3-small",
    input="The quick brown fox jumps over the lazy dog"
)

print(f"Embedding dimension: {len(embedding_response.data[0].embedding)}")
```

### LangChain Integration

```python
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

llm = ChatOpenAI(
    openai_api_base="http://localhost:8000/v1",
    openai_api_key="dummy-key",
    model="gpt-4o"
)

messages = [
    SystemMessage(content="You are a helpful assistant."),
    HumanMessage(content="Explain how APIs work in simple terms.")
]

response = llm.invoke(messages)
print(response.content)
```

## 👥 Community & Support

- [GitHub Discussions](https://github.com/yctimlin/OpenAI-Compatible-API-Mimic/discussions) - Ask questions and share ideas
- [GitHub Issues](https://github.com/yctimlin/OpenAI-Compatible-API-Mimic/issues) - Report bugs or request features
- [Discord Server](https://discord.gg/example) - Join our community

## 🗺️ Roadmap

- [ ] Support for Azure OpenAI API compatibility
- [ ] Additional logging and monitoring options
- [ ] Helm chart for Kubernetes deployment
- [ ] Authentication and rate limiting
- [ ] Request/response validation middleware
- [ ] Support for DALL-E 3 and other image generation endpoints

## ❓ FAQ

### How does this differ from the OpenAI API?

This project creates a compatibility layer between your API backend and OpenAI's API format. It allows you to maintain your own backend implementation while providing a standard OpenAI-compatible interface for client applications.

### Can I use this with any LLM provider?

Yes, as long as your backend can fulfill the requirements of the API - typically providing chat completions and embeddings. You'll need to implement the appropriate transformations in the backend utilities.

### Is this suitable for production use?

Yes, the architecture follows best practices for production environments, including proper error handling, logging, and configuration. However, you should implement appropriate authentication and rate limiting for your specific use case.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add some amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Contributors

<a href="https://github.com/yctimlin/OpenAI-Compatible-API-Mimic/graphs/contributors">
  <img src="https://contributors-img.web.app/image?repo=yctimlin/OpenAI-Compatible-API-Mimic" />
</a>

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Related Projects

- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)
- [FastAPI](https://fastapi.tiangolo.com/)
- [LangChain](https://www.langchain.com/)

---

<p align="center">If you find this project helpful, please consider giving it a star ⭐</p>
<p align="center">Built with ❤️ for the AI developer community</p>