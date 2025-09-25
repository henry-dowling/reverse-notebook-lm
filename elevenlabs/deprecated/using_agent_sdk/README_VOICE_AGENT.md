# ElevenLabs Voice Agent with Tools Integration

A sophisticated voice agent built with the ElevenLabs Python SDK that integrates with file operations and script management tools. The agent can perform real-time voice conversations while using tools to help users manage markdown files and voice instruction scripts.

## Features

- 🎤 **Real-time Voice Conversation**: Powered by ElevenLabs Conversational AI
- 📁 **File Operations**: Create, read, update, delete markdown files
- 📜 **Script Management**: Load and manage voice instruction scripts
- 🔧 **Tool Integration**: Seamless integration with FastAPI backend tools
- 🎯 **Dynamic System Prompt**: System prompt with dynamic variable updates
- 🛠️ **Error Handling**: Robust error handling and user feedback

## Prerequisites

1. **ElevenLabs Account**: You need an ElevenLabs account with API access
2. **ElevenLabs Agent**: Create a conversational AI agent in the ElevenLabs dashboard
3. **FastAPI Backend**: The tools API server must be running (see main README)
4. **Python 3.8+**: Required for async/await support

## Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements_voice_agent.txt
   ```

2. **Set Environment Variables**:
   Create a `.env` file in the elevenlabs directory:
   ```bash
   # Required
   ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
   ELEVENLABS_AGENT_ID=your_agent_id_here
   
   # Optional (for enhanced functionality)
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **Start the FastAPI Backend**:
   ```bash
   # In the elevenlabs directory
   python main.py
   ```
   The backend should be running on `http://localhost:8001`

## Usage

### Basic Usage

1. **Start the Voice Agent**:
   ```bash
   python voice_agent.py
   ```

2. **Begin Conversation**:
   - The agent will start listening for your voice input
   - Speak naturally to interact with the agent
   - Use voice commands to trigger tool operations

### Available Voice Commands

#### File Operations
- "List all markdown files"
- "Read the file called [filename]"
- "Create a new file called [filename] with [content]"
- "Update the file [filename] with [new content]"
- "Delete the file [filename]"
- "Edit [filename] to [description of changes]"

#### Script Management
- "Show me all available voice scripts"
- "Get the script [scriptname]"
- "Create a new script called [name] with [instructions]"
- "Update the script [name] with [new instructions]"
- "Delete the script [name]"

#### General Commands
- "Help" - Show available commands
- "What can you do?" - Explain capabilities
- "Stop" or "Goodbye" - End conversation

### Example Conversation

```
User: "Hello, can you help me create a new markdown file?"
Agent: "I'd be happy to help you create a new markdown file. What would you like to name it and what content should it contain?"

User: "Call it 'meeting_notes.md' and add 'Meeting Notes - Project Planning'"
Agent: "I'll create that file for you right away." [Uses create_markdown_file tool]
Agent: "Perfect! I've created 'meeting_notes.md' with your specified content. Is there anything else you'd like to do with this file?"

User: "Can you show me all the available voice scripts?"
Agent: "Let me get that list for you." [Uses list_voice_scripts tool]
Agent: "Here are the available voice scripts: greeting.txt, appointment_booking.md. Would you like me to show you the content of any of these?"
```

## Architecture

### Components

1. **VoiceAgent Class**: Main agent class handling conversation and tool integration
2. **System Prompt**: Dynamic prompt with variable substitution
3. **Tool Integration**: HTTP-based tool calls to FastAPI backend
4. **Audio Interface**: ElevenLabs default audio interface for voice I/O

### Tool Integration Flow

```
Voice Input → ElevenLabs Agent → Tool Decision → HTTP Request → FastAPI Backend → Response → Voice Output
```

### Dynamic System Prompt

The system prompt (`system_prompt.md`) includes dynamic variables that are updated at runtime:
- `{{AVAILABLE_SCRIPTS}}`: Automatically populated with current script list
- Future variables can be added for other dynamic content

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ELEVENLABS_API_KEY` | Yes | Your ElevenLabs API key |
| `ELEVENLABS_AGENT_ID` | Yes | ID of your ElevenLabs agent |
| `OPENAI_API_KEY` | No | For enhanced file editing features |

### Agent Configuration

When creating your ElevenLabs agent:
1. Go to the ElevenLabs dashboard
2. Create a new Conversational AI agent
3. Configure the agent settings
4. Copy the agent ID to your `.env` file

## Troubleshooting

### Common Issues

1. **"ELEVENLABS_API_KEY not found"**
   - Ensure your `.env` file exists and contains the API key
   - Check that the key is valid and has proper permissions

2. **"ELEVENLABS_AGENT_ID not found"**
   - Create an agent in the ElevenLabs dashboard
   - Copy the agent ID to your `.env` file

3. **"Connection refused to localhost:8001"**
   - Ensure the FastAPI backend is running
   - Check that port 8001 is available
   - Verify the backend is accessible

4. **"Tool registration failed"**
   - Check that all required dependencies are installed
   - Ensure the FastAPI backend is responding
   - Verify tool endpoints are working

### Debug Mode

To enable debug logging, add this to your `.env` file:
```bash
DEBUG=true
```

## Advanced Usage

### Custom Tool Integration

You can extend the agent with custom tools by modifying the `setup_tools()` method:

```python
def setup_tools(self):
    # Add custom tool
    async def custom_tool(params):
        # Your custom tool logic
        return "Custom tool result"
    
    self.client_tools.register("custom_tool", custom_tool, is_async=True)
```

### Custom System Prompt

Modify `system_prompt.md` to customize the agent's behavior:
- Add new capabilities
- Modify communication style
- Include domain-specific instructions

### Error Handling

The agent includes comprehensive error handling:
- Network errors are caught and reported
- Tool failures are explained to the user
- Graceful degradation when tools are unavailable

## Development

### Adding New Tools

1. **Backend**: Add new endpoints to the FastAPI server
2. **Agent**: Register new tools in the `setup_tools()` method
3. **Testing**: Test tool integration with the voice agent

### Testing

```bash
# Test tool connectivity
python -c "from voice_agent import VoiceAgent; import asyncio; agent = VoiceAgent('test'); asyncio.run(agent.test_tools())"
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of the reverse-notebook-lm repository and follows the same license terms.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the ElevenLabs documentation
3. Open an issue in the repository
4. Contact the development team

---

**Note**: This voice agent requires an active internet connection and valid ElevenLabs API credentials. Ensure you have sufficient API credits for your usage needs.
