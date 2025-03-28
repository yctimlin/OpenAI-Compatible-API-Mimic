#!/bin/bash

# Setup script for OpenAI-Compatible API Mimic
echo "Setting up OpenAI-Compatible API Mimic..."

# Check if Python is installed
if command -v python3 &>/dev/null; then
    echo "✅ Python is installed"
else
    echo "❌ Python is not installed. Please install Python 3.10 or higher."
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️ Please edit the .env file with your actual API credentials."
else
    echo "✅ .env file already exists"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the API server, run:"
echo "  source venv/bin/activate  # If not already activated"
echo "  python main.py"
echo ""
echo "To test the API, run:"
echo "  python test_api.py" 