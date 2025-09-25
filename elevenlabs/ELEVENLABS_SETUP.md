# ElevenLabs Tool Setup Guide

This guide explains how to automatically load all 13 tools into your ElevenLabs voice agent workspace.

## Prerequisites

1. **ElevenLabs API Key**: Get your API key from [ElevenLabs Dashboard](https://elevenlabs.io/app/settings/api-keys)
2. **Running FastAPI Server**: Make sure your local server is running on `https://allegory.ngrok.app`

## Setup Steps

### 1. Configure API Key

Edit the `.env` file and add your ElevenLabs API key:

```bash
# Edit .env file
nano .env

# Replace this line:
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# With your actual API key:
ELEVENLABS_API_KEY=sk_abc123...
```

### 2. Start Your FastAPI Server

Make sure your FastAPI server is running:

```bash
python main.py
```

You should see: `Uvicorn running on http://0.0.0.0:8001`

### 3. Run the Tool Loader Script

```bash
python load_tools_to_elevenlabs.py
```

The script will:
- Automatically create all 13 tools in your ElevenLabs workspace
- Show progress for each tool being created
- Report success/failure for each tool

### 4. Verify in ElevenLabs Dashboard

1. Go to [ElevenLabs Conversational AI](https://elevenlabs.io/app/conversational-ai)
2. Navigate to your agent settings
3. Check the "Tools" section
4. You should see all 13 tools listed

## Tools Created

The script creates these 13 tools:

### Markdown File Management (8 tools)
1. **List Markdown Files** - GET `/workspace/files`
2. **Read Markdown File** - GET `/workspace/files/{filename}`
3. **Create Markdown File** - POST `/workspace/files/{filename}`
4. **Update Markdown File** - PUT `/workspace/files/{filename}`
5. **Delete Markdown File** - DELETE `/workspace/files/{filename}`
6. **Get File Lines** - GET `/workspace/files/{filename}/lines`
7. **Edit File Line** - PUT `/workspace/files/{filename}/lines/{line_number}`
8. **Edit with Description** - PUT `/workspace/files/{filename}/edit` (AI-powered)

### Voice Script Management (5 tools)
9. **List Voice Scripts** - GET `/scripts`
10. **Get Voice Script** - GET `/scripts/{filename}`
11. **Create Voice Script** - POST `/scripts/{filename}`
12. **Update Voice Script** - PUT `/scripts/{filename}`
13. **Delete Voice Script** - DELETE `/scripts/{filename}`

## Troubleshooting

### Invalid API Key Error
```
❌ Failed to create tool: List Markdown Files
Status: 401
Error: {"detail":{"status":"invalid_api_key","message":"Invalid API key"}}
```

**Solution**: Verify your ElevenLabs API key in the `.env` file.

### Server Connection Error
```
❌ Failed to create tool: List Markdown Files
Status: Connection error
```

**Solution**: Make sure your FastAPI server is running on `https://allegory.ngrok.app`.

### Port Already in Use
If you get a port conflict, update the `BASE_URL` in `load_tools_to_elevenlabs.py`:

```python
BASE_URL = "http://localhost:8002"  # Change port as needed
```

## Testing Your Tools

After successful setup, test your tools by:

1. Creating a new conversational AI agent
2. Adding the tools to your agent
3. Testing with voice commands like:
   - "List my markdown files"
   - "Read the test.md file"
   - "Create a new file called notes.md with some content"
   - "Show me the voice scripts"

## Script Customization

You can modify `load_tools_to_elevenlabs.py` to:
- Change tool descriptions
- Modify the server URL
- Add or remove tools
- Customize tool behavior

The script is well-commented and easy to modify for your specific needs.

## Support

If you encounter issues:
1. Check that your API key is valid
2. Ensure the FastAPI server is running
3. Verify network connectivity to ElevenLabs API
4. Check the console output for specific error messages