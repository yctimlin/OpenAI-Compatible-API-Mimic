"""
Example of streaming responses from OpenAI-Compatible API Mimic.

This script demonstrates how to use the streaming capability with the OpenAI Python SDK,
showing real-time token generation with the OpenAI-Compatible API Mimic.

Prerequisites:
- OpenAI-Compatible API Mimic running on http://localhost:8000
- Required packages: openai
"""

import sys
import time
from openai import OpenAI

# Initialize the OpenAI client with our API Mimic base URL
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="dummy-key"  # Not validated but required by the SDK
)

def stream_chat_completion():
    """Example of streaming a chat completion response."""
    print("Starting streaming chat completion...\n")
    
    # Stream the response
    stream = client.chat.completions.create(
        model="gpt-4o",  # Use the model available in your backend
        messages=[
            {"role": "system", "content": "You are a helpful assistant that speaks in a poetic style."},
            {"role": "user", "content": "Write a short poem about artificial intelligence."}
        ],
        stream=True,
        temperature=0.7,
        max_tokens=150
    )
    
    # Process the stream
    full_response = ""
    
    for chunk in stream:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            full_response += content
            print(content, end="", flush=True)
            # Slow down the output to simulate real-time generation
            time.sleep(0.02) 
    
    print("\n\nStreaming complete!")
    return full_response

def animated_typing_effect(response):
    """Re-display the response with a typing animation effect."""
    print("\nReplaying response with typing effect:\n")
    
    for char in response:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.03)
    
    print("\n\nAnimation complete!")

def main():
    print("OpenAI-Compatible API Mimic - Streaming Example")
    print("=" * 50)
    
    # Get the streaming response
    full_response = stream_chat_completion()
    
    # Optional: Replay with a typing effect
    animated_typing_effect(full_response)
    
if __name__ == "__main__":
    main() 