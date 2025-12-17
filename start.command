#!/bin/bash

cd "/Users/matthewmacosko/Desktop/Divine Tribe Email Assistant"

echo "📧 DIVINE TRIBE EMAIL ASSISTANT"
echo "================================"
echo ""

# Check for virtual environment
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

echo ""
echo "🚀 Starting Email Assistant..."
echo "   Press Ctrl+C to stop"
echo ""

python email_assistant.py
