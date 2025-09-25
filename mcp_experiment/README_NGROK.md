# Reverse Notebook LM - ngrok Integration

This guide explains how to run the Reverse Notebook LM MCP server with ngrok for remote access, particularly for ElevenLabs integration.

## Quick Start

### 1. Setup

```bash
# Run the setup script
./setup_ngrok.sh

# Or manually install dependencies
pip install -r requirements.txt
```

### 2. Start with ngrok

```bash
# Start server with ngrok tunnel
python start_with_ngrok.py

# Or start HTTP server only (for local testing)
python http_mcp_server.py
```

### 3. ElevenLabs Integration

Once running, you'll get a public URL at `https://allegory.ngrok.app`. Use this for ElevenLabs:

**For ElevenLabs MCP Integration:**
1. **Discovery URL**: `https://allegory.ngrok.app/mcp/info`
2. **Tools URL**: `https://allegory.ngrok.app/mcp/tools`
3. **Webhook URL**: `https://allegory.ngrok.app/webhook/elevenlabs`

**ElevenLabs Configuration:**
- Set the MCP server URL to your ngrok URL
- ElevenLabs will discover tools via `/mcp/info` and `/mcp/tools`
- Voice input will be sent to `/webhook/elevenlabs`
- For streaming responses, use `/webhook/elevenlabs/stream` (SSE)

**Server-Sent Events (SSE) Support:**
- Real-time streaming of MCP tool responses
- Progress updates during tool execution
- Continuous data flow for better user experience
- Compatible with ElevenLabs streaming requirements

## Architecture

```
ElevenLabs Voice Input
         ↓
    ngrok Tunnel
         ↓
   HTTP MCP Server
         ↓
    MCP Server Core
         ↓
   Script & File Tools
```

## Available Endpoints

### Core MCP Tools
- `GET /tools` - List all available MCP tools
- `POST /tools/call` - Call any MCP tool directly

### Script Management
- `GET /scripts` - List available scripts
- `GET /scripts/{name}` - Get script details
- `POST /scripts/{name}/load` - Load a script
- `GET /scripts/progress` - Get script progress

### File Operations
- `GET /files` - List markdown files
- `GET /files/{name}` - Read a file
- `POST /files/{name}` - Write to a file
- `PUT /files/{name}` - Append to a file
- `POST /files/{name}/edit-lines` - Edit specific lines
- `POST /files/{name}/replace` - Replace content
- `GET /files/{name}/info` - Get file info
- `POST /files/{name}/backup` - Create backup

### ElevenLabs Integration
- `GET /mcp/info` - MCP server information for ElevenLabs discovery
- `GET /mcp/tools` - MCP tools in ElevenLabs-compatible format
- `GET /mcp/tools/stream` - Stream MCP tools as Server-Sent Events (SSE)
- `POST /mcp/tools/call/stream` - Stream tool execution as SSE
- `POST /webhook/elevenlabs` - Receive voice input from ElevenLabs
- `POST /webhook/elevenlabs/stream` - Stream voice input processing as SSE

## ElevenLabs Webhook Format

The webhook expects JSON data with voice input:

```json
{
  "text": "User's spoken text",
  "user_id": "user123",
  "session_id": "session456",
  "metadata": {
    "language": "en",
    "confidence": 0.95
  }
}
```

## Example Usage

### 1. List Available Scripts
```bash
curl https://allegory.ngrok.app/scripts
```

### 2. Load a Script
```bash
curl -X POST https://allegory.ngrok.app/scripts/blog_writer/load
```

### 3. Read a File
```bash
curl https://allegory.ngrok.app/files/output.md
```

### 4. Write to a File
```bash
curl -X POST https://allegory.ngrok.app/files/notes.md \
  -H "Content-Type: application/json" \
  -d '{"content": "# My Notes\n\nThis is a test note."}'
```

### 5. Edit Specific Lines
```bash
curl -X POST https://allegory.ngrok.app/files/notes.md/edit-lines \
  -H "Content-Type: application/json" \
  -d '{
    "line_edits": [
      {"line_number": 1, "new_content": "# Updated Notes"},
      {"line_number": 3, "new_content": "This line was edited!"}
    ]
  }'
```

## Configuration

### Environment Variables
- `PORT` - Server port (default: 8000)
- `HOST` - Server host (default: 0.0.0.0)

### ngrok Configuration
- Sign up at https://ngrok.com
- Get your auth token from https://dashboard.ngrok.com/get-started/your-authtoken
- Run: `ngrok config add-authtoken YOUR_TOKEN`

## Security Considerations

⚠️ **Important**: The current setup allows all origins (`allow_origins=["*"]`). For production:

1. Configure specific origins in `http_mcp_server.py`
2. Add authentication/API keys
3. Use HTTPS with ngrok Pro for custom domains
4. Implement rate limiting

## Troubleshooting

### ngrok Issues
- **"ngrok not found"**: Install ngrok from https://ngrok.com/download
- **"Auth token required"**: Run `ngrok config add-authtoken YOUR_TOKEN`
- **"Tunnel failed"**: Check if port 8000 is available

### Server Issues
- **"Port already in use"**: Change port with `python http_mcp_server.py --port 8001`
- **"Module not found"**: Run `pip install -r requirements.txt`

### ElevenLabs Integration
- **Webhook not receiving data**: Check ngrok URL is accessible
- **CORS errors**: Verify CORS settings in the server
- **Timeout errors**: Increase ElevenLabs webhook timeout

## Development

### Local Testing
```bash
# Start HTTP server locally
python http_mcp_server.py --reload

# Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/tools
```

### Debugging
- Check server logs for errors
- Use ngrok web interface at http://localhost:4040
- Test webhook with curl or Postman

## Production Deployment

For production use:

1. **Use ngrok Pro** for custom domains and better reliability
2. **Add authentication** (API keys, JWT tokens)
3. **Configure CORS** for specific origins
4. **Add rate limiting** to prevent abuse
5. **Use HTTPS** with proper SSL certificates
6. **Monitor logs** and set up alerting

## Support

For issues or questions:
1. Check the logs in the terminal
2. Verify ngrok tunnel is active at http://localhost:4040
3. Test endpoints with curl or Postman
4. Check ElevenLabs webhook configuration
