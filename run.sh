#!/bin/bash

echo "Starting AI Task Assistant..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.8+ from https://python.org"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo
    echo "Warning: .env file not found!"
    echo "Please copy .env.example to .env and add your OpenAI API key"
    echo
    read -p "Press Enter to continue..."
fi

# Run the application
echo
echo "Starting AI Task Assistant..."
python main.py