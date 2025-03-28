"""
Test script for the OpenAI-Compatible API.

This script tests the API endpoints to ensure they're functioning correctly.
"""

import requests
import json
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BASE_URL = f"http://localhost:{os.getenv('PORT', '8000')}/v1"
HEADERS = {"Content-Type": "application/json"}

def test_health():
    """Test the health endpoint."""
    response = requests.get(f"http://localhost:{os.getenv('PORT', '8000')}/")
    print(f"Health check: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print("-" * 50)

def test_models():
    """Test the models endpoint."""
    response = requests.get(f"{BASE_URL}/models", headers=HEADERS)
    print(f"Models endpoint: {response.status_code}")
    # Print just a subset of models to keep output manageable
    data = response.json()
    print(f"Total models: {len(data['data'])}")
    print("Sample models:")
    for model in data["data"][:3]:  # Just show first 3 models
        print(f"  - {model['id']}")
    print("-" * 50)

def test_chat_completion():
    """Test the chat completions endpoint."""
    payload = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, what time is it?"}
        ],
        "max_tokens": 50,
        "temperature": 0.7
    }
    
    try:
        print("Testing chat completion (this might take a moment)...")
        response = requests.post(f"{BASE_URL}/chat/completions", headers=HEADERS, json=payload)
        print(f"Chat completion: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response ID: {result.get('id', 'N/A')}")
            print(f"Model used: {result.get('model', 'N/A')}")
            if result.get('choices'):
                print(f"Response: {result['choices'][0]['message']['content']}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error during chat completion test: {str(e)}")
    
    print("-" * 50)

if __name__ == "__main__":
    print("Testing OpenAI-Compatible API...")
    print("=" * 50)
    
    # Run tests
    test_health()
    test_models()
    test_chat_completion()
    
    print("Tests completed!") 