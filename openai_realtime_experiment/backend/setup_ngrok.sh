#!/bin/bash

# Setup script for ngrok integration with Reverse Notebook LM

echo "🚀 Setting up Reverse Notebook LM with ngrok integration"
echo "=================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "📦 ngrok not found. Installing..."
    
    # Detect OS and install ngrok
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install ngrok/ngrok/ngrok
        else
            echo "Please install ngrok manually:"
            echo "1. Go to https://ngrok.com/download"
            echo "2. Download the macOS version"
            echo "3. Extract and move to /usr/local/bin/"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        echo "Please install ngrok manually:"
        echo "1. Go to https://ngrok.com/download"
        echo "2. Download the Linux version"
        echo "3. Extract and move to /usr/local/bin/"
        exit 1
    else
        echo "Unsupported OS. Please install ngrok manually from https://ngrok.com/download"
        exit 1
    fi
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Check if ngrok auth token is configured
if ! ngrok config check &> /dev/null; then
    echo "🔑 Configuring ngrok authentication..."
    ngrok config add-authtoken 2nMLXFpIrATnLOjNNVFc0kw1ObK_2G2vPt4uWhhn4Kc7DLjQX
    echo "✅ ngrok auth token configured"
else
    echo "✅ ngrok authentication already configured"
fi

echo "✅ Setup complete!"
echo ""
echo "🚀 To start the server with ngrok:"
echo "   python start_with_ngrok.py"
echo ""
echo "🔗 Or start just the HTTP server:"
echo "   python http_mcp_server.py"
echo ""
echo "📖 For ElevenLabs integration:"
echo "   1. Start the server with ngrok"
echo "   2. Use the public URL as your webhook endpoint"
echo "   3. Set webhook URL to: https://your-ngrok-url.ngrok.io/webhook/elevenlabs"
