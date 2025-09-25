# Pure MCP Server with Ngrok

This document explains how to run the pure MCP server with ngrok tunneling for remote access.

## Overview

We now have two ways to run the MCP server:

1. **HTTP Wrapper Server** (`start_with_ngrok.py`) - Full HTTP API with REST endpoints
2. **Pure MCP Server** (`start_mcp_with_ngrok.py`) - Actual MCP protocol with HTTP bridge

## Pure MCP Server Setup

### Prerequisites

1. Install ngrok: https://ngrok.com/download
2. Get your ngrok auth token and configure it:
   ```bash
   ngrok config add-authtoken YOUR_TOKEN
   ```

### Running the Pure MCP Server

```bash
cd backend
python start_mcp_with_ngrok.py
```

This script will:
- Start the pure MCP server in the background
- Create an HTTP bridge for web clients
- Start ngrok tunnel pointing to the HTTP bridge
- Provide both local and public URLs

### Available Endpoints

Once running, you'll have access to:

- **Health Check**: `GET /health`
- **List Scripts**: `GET /scripts` 
- **List Files**: `GET /files`
- **Call Tools**: `POST /` with JSON payload

### Example Tool Call

```bash
curl -X POST http://localhost:8000/ \
  -H "Content-Type: application/json" \
  -d '{"name": "list_scripts", "arguments": {}}'
```

## CORS Configuration

The HTTP wrapper server now includes enhanced CORS support:

### Automatically Allowed Origins

- `http://localhost:*` - All localhost ports
- `https://elevenlabs.io` - ElevenLabs main domain
- `https://app.elevenlabs.io` - ElevenLabs app domain
- `https://*.ngrok.io` - All ngrok URLs (dynamic)
- `http://localhost:6274` - MCP Inspector default port

### Custom Origins

You can add custom origins via environment variable:

```bash
export ALLOWED_ORIGINS="https://myapp.com,https://another-domain.com"
python http_mcp_server.py --port 8000
```

## MCP Inspector Integration

### Using the Inspector with HTTP Server

1. Start the HTTP server:
   ```bash
   python http_mcp_server.py --port 8000
   ```

2. The inspector can connect via HTTP at `http://localhost:8000`

### Using the Inspector with Pure MCP Server

1. Start the pure MCP server:
   ```bash
   python start_mcp_with_ngrok.py
   ```

2. Use the HTTP bridge endpoint for web-based testing

## ElevenLabs Integration

The server is now configured to work with ElevenLabs:

- CORS headers automatically allow ElevenLabs domains
- Dynamic ngrok URL support for remote access
- Proper preflight request handling

### Testing with ElevenLabs

1. Start server with ngrok:
   ```bash
   python start_with_ngrok.py  # or start_mcp_with_ngrok.py
   ```

2. Use the public ngrok URL in ElevenLabs configuration

3. The server will automatically handle CORS for ElevenLabs requests

## Configuration Files

- `ngrok.yml` - Configuration for HTTP wrapper server
- `ngrok_mcp.yml` - Configuration for pure MCP server
- Environment variables for custom CORS origins

## Troubleshooting

### CORS Issues

If you encounter CORS errors:

1. Check that the requesting domain is in the allowed origins
2. Verify the server is returning proper CORS headers
3. Use browser dev tools to inspect preflight requests

### Ngrok Issues

If ngrok fails to start:

1. Verify your auth token is configured: `ngrok config check`
2. Check if the port is already in use
3. Try using a different subdomain in the config file

### MCP Inspector Issues

If the inspector can't connect:

1. Ensure the server is running on the expected port
2. Check that the server responds to health checks
3. Verify the MCP protocol is properly implemented

## Security Notes

- The pure MCP server includes basic HTTP bridging for web compatibility
- CORS is configured permissive for development
- Consider adding authentication for production use
- Ngrok URLs are temporary and change on restart
