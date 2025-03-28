"""
Example of tool calling with OpenAI-Compatible API Mimic.

This script demonstrates how to use the function/tool calling capability
with the OpenAI-Compatible API Mimic, allowing AI models to invoke functions.

Prerequisites:
- OpenAI-Compatible API Mimic running on http://localhost:8000
- Required packages: openai, requests
"""

import json
import requests
from datetime import datetime
from openai import OpenAI

# Initialize the OpenAI client with our API Mimic base URL
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="dummy-key"  # Not validated but required by the SDK
)

# Example functions that the model can call
def get_weather(location, unit="celsius"):
    """
    Get the current weather in a given location.
    
    This is a mock function - in a real application, you would call
    an actual weather API here.
    """
    # Mock weather data - in a real app, you would fetch this from a weather API
    weather_data = {
        "New York": {"temp": 22, "condition": "Sunny", "humidity": 60},
        "London": {"temp": 15, "condition": "Cloudy", "humidity": 70},
        "Tokyo": {"temp": 28, "condition": "Clear", "humidity": 55},
        "Sydney": {"temp": 20, "condition": "Rainy", "humidity": 80},
    }
    
    # Default weather if location not found
    default_weather = {"temp": 18, "condition": "Partly Cloudy", "humidity": 65}
    
    # Get weather for the specified location or use default
    weather = weather_data.get(location, default_weather)
    
    # Convert temperature if needed
    if unit.lower() == "fahrenheit":
        weather["temp"] = (weather["temp"] * 9/5) + 32
    
    return {
        "location": location,
        "temperature": f"{weather['temp']:.1f}° {'C' if unit.lower() == 'celsius' else 'F'}",
        "condition": weather["condition"],
        "humidity": f"{weather['humidity']}%",
        "retrieved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def calculate_mortgage(principal, annual_interest_rate, years):
    """
    Calculate monthly mortgage payment.
    
    Args:
        principal: The loan amount
        annual_interest_rate: Annual interest rate (percentage)
        years: Loan term in years
    
    Returns:
        Dictionary with monthly payment and loan details
    """
    # Convert annual interest rate to monthly and decimal
    monthly_interest_rate = (annual_interest_rate / 100) / 12
    
    # Calculate total number of payments
    total_payments = years * 12
    
    # Calculate monthly payment using the mortgage formula
    if monthly_interest_rate == 0:
        monthly_payment = principal / total_payments
    else:
        monthly_payment = principal * (monthly_interest_rate * (1 + monthly_interest_rate) ** total_payments) / ((1 + monthly_interest_rate) ** total_payments - 1)
    
    # Calculate total payment over the life of the loan
    total_payment = monthly_payment * total_payments
    
    # Calculate total interest paid
    total_interest = total_payment - principal
    
    return {
        "monthly_payment": f"${monthly_payment:.2f}",
        "total_payments": total_payments,
        "total_payment": f"${total_payment:.2f}",
        "total_interest": f"${total_interest:.2f}",
        "annual_interest_rate": f"{annual_interest_rate}%",
        "loan_term_years": years
    }

def main():
    print("OpenAI-Compatible API Mimic - Tool Calling Example")
    print("=" * 60)
    
    # Define the tools (functions) that the model can use
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
                            "description": "The city, e.g., New York, London, Tokyo"
                        },
                        "unit": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"],
                            "description": "The unit of temperature, either celsius or fahrenheit"
                        }
                    },
                    "required": ["location"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "calculate_mortgage",
                "description": "Calculate monthly mortgage payment details",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "principal": {
                            "type": "number",
                            "description": "The loan amount in dollars"
                        },
                        "annual_interest_rate": {
                            "type": "number",
                            "description": "Annual interest rate as a percentage, e.g., 5.5 for 5.5%"
                        },
                        "years": {
                            "type": "integer",
                            "description": "The loan term in years"
                        }
                    },
                    "required": ["principal", "annual_interest_rate", "years"]
                }
            }
        }
    ]
    
    # Ask the user for a question
    user_query = input("Ask a question that might require weather info or mortgage calculation: ")
    
    # Create a chat completion with the tools
    response = client.chat.completions.create(
        model="gpt-4o",  # Use a model that supports tool calling
        messages=[
            {"role": "system", "content": "You are a helpful assistant with access to tools for weather and mortgage calculations."},
            {"role": "user", "content": user_query}
        ],
        tools=tools,
        tool_choice="auto"  # Let the model decide when to use tools
    )
    
    # Process the response
    message = response.choices[0].message
    
    # Check if the model wants to call a function
    if message.tool_calls:
        # Process each tool call
        for tool_call in message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            print(f"\nCalling function: {function_name}")
            print(f"With arguments: {function_args}")
            
            # Call the appropriate function
            if function_name == "get_weather":
                function_response = get_weather(**function_args)
            elif function_name == "calculate_mortgage":
                function_response = calculate_mortgage(**function_args)
            else:
                function_response = {"error": "Unknown function"}
                
            print(f"Function result: {function_response}")
            
            # Add the function response to the conversation
            messages = [
                {"role": "system", "content": "You are a helpful assistant with access to tools for weather and mortgage calculations."},
                {"role": "user", "content": user_query},
                message,
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": json.dumps(function_response)
                }
            ]
            
            # Get a new response from the model
            second_response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages
            )
            
            print("\nAI Assistant's Response:")
            print(second_response.choices[0].message.content)
    else:
        # Model didn't call a function, just show the response
        print("\nAI Assistant's Response:")
        print(message.content)

if __name__ == "__main__":
    main() 