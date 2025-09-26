# ElevenLabs Tools API

A FastAPI server that provides endpoints for ElevenLabs tools integration, supporting CRUD operations on markdown files and voice agent instruction script management.

## Setup and Installation

1. Install dependencies:
```bash
pip install fastapi uvicorn openai python-dotenv
```

2. Set up OpenAI API key (required for the "Edit with Description" tool):
   
   **Option A: Using .env file (recommended)**
   ```bash
   # Edit the .env file and replace 'your_openai_api_key_here' with your actual API key
   nano .env
   ```
   
   **Option B: Using environment variable**
   ```bash
   export OPENAI_API_KEY=your_api_key_here
   ```

3. Run the server:
```bash
python main.py
```

The server will start on `http://localhost:8001` locally, but all tool configurations use the public URL `https://allegory.ngrok.app`

## ElevenLabs Tool Configuration

**Quick Start**: Run `python load_tools_to_elevenlabs_sdk.py` to automatically create 2 basic tools (list functions).

For the remaining 13 tools, each should be added manually in the ElevenLabs UI with the following details:

### 1. List Markdown Files

**Name**: List Markdown Files  
**Description**: Get a list of all markdown files in the workspace  
**Method**: GET  
**URL**: `https://allegory.ngrok.app/workspace/files`  
**Query Parameters**: None  
**Path Parameters**: None  

### 2. Read Markdown File

**Name**: Read Markdown File  
**Description**: Read the content of a specific markdown file  
**Method**: GET  
**URL**: `https://allegory.ngrok.app/workspace/files/{filename}`  
**Query Parameters**: None  
**Path Parameters**:
- `filename` (string, required): Name of the markdown file (with or without .md extension)

### 3. Create Markdown File

**Name**: Create Markdown File  
**Description**: Create a new markdown file with specified content  
**Method**: POST  
**URL**: `https://allegory.ngrok.app/workspace/files/{filename}`  
**Query Parameters**: None  
**Path Parameters**:
- `filename` (string, required): Name of the markdown file to create  
**Request Body**:
```json
{
  "content": "string - the markdown content"
}
```

### 4. Update Markdown File

**Name**: Update Markdown File  
**Description**: Update the entire content of an existing markdown file  
**Method**: PUT  
**URL**: `https://allegory.ngrok.app/workspace/files/{filename}`  
**Query Parameters**: None  
**Path Parameters**:
- `filename` (string, required): Name of the markdown file to update  
**Request Body**:
```json
{
  "content": "string - the new markdown content"
}
```

### 5. Delete Markdown File

**Name**: Delete Markdown File  
**Description**: Delete a markdown file from the workspace  
**Method**: DELETE  
**URL**: `https://allegory.ngrok.app/workspace/files/{filename}`  
**Query Parameters**: None  
**Path Parameters**:
- `filename` (string, required): Name of the markdown file to delete

### 6. Get File Lines

**Name**: Get File Lines  
**Description**: Get all lines of a markdown file with line numbers for editing  
**Method**: GET  
**URL**: `https://allegory.ngrok.app/workspace/files/{filename}/lines`  
**Query Parameters**: None  
**Path Parameters**:
- `filename` (string, required): Name of the markdown file

### 7. Edit Specific Line

**Name**: Edit File Line  
**Description**: Edit a specific line in a markdown file by line number  
**Method**: PUT  
**URL**: `https://allegory.ngrok.app/workspace/files/{filename}/lines/{line_number}`  
**Query Parameters**: None  
**Path Parameters**:
- `filename` (string, required): Name of the markdown file
- `line_number` (integer, required): Line number to edit (1-based)  
**Request Body**:
```json
{
  "line_number": 1,
  "new_content": "string - the new content for this line"
}
```

### 8. Edit with Description

**Name**: Edit with Description  
**Description**: Edit a markdown file using natural language description (powered by AI)  
**Method**: PUT  
**URL**: `https://allegory.ngrok.app/workspace/files/{filename}/edit`  
**Query Parameters**: None  
**Path Parameters**:
- `filename` (string, required): Name of the markdown file to edit  
**Request Body**:
```json
{
  "description": "string - natural language description of how to edit the file"
}
```

### 9. Generate Document with AI

**Name**: Generate Document with AI  
**Description**: Generate a new document using AI based on plain language description  
**Method**: POST  
**URL**: `https://allegory.ngrok.app/workspace/files/{filename}/generate`  
**Query Parameters**: None  
**Path Parameters**:
- `filename` (string, required): Name of the document file to create  
**Request Body**:
```json
{
  "description": "string - plain language description of what the document should contain"
}
```

Response (local mode):
```json
{
  "message": "Document <filename> generated successfully using AI",
  "created": true,
  "filename": "<filename>.md",
  "description": "<original description>",
  "preview": "<first 200 chars>"
}
```

Response (google mode):
```json
{
  "message": "Google Doc <title> generated successfully using AI",
  "created": true,
  "filename": "<title>",
  "file_id": "<google file id>",
  "web_url": "https://docs.google.com/document/d/...",
  "description": "<original description>",
  "preview": "<first 200 chars>"
}
```

Note (google mode): Subsequent operations like read/update/delete accept either the Google file ID or the exact document title in the `{filename}` path parameter.

### 10. Summarize Document with AI

**Name**: Summarize Document with AI  
**Description**: Summarize an existing document using AI  
**Method**: GET  
**URL**: `https://allegory.ngrok.app/workspace/files/{filename}/summarize`  
**Query Parameters**: None  
**Path Parameters**:
- `filename` (string, required): Name of the document file to summarize

### 11. List Voice Scripts

**Name**: List Voice Scripts  
**Description**: Get a list of all voice agent instruction script files (.txt, .md) in the scripts directory  
**Method**: GET  
**URL**: `https://allegory.ngrok.app/scripts`  
**Query Parameters**: None  
**Path Parameters**: None

### 12. Get Voice Script

**Name**: Get Voice Script  
**Description**: Retrieve the content of a specific voice agent instruction script  
**Method**: GET  
**URL**: `https://allegory.ngrok.app/scripts/{filename}`  
**Query Parameters**: None  
**Path Parameters**:
- `filename` (string, required): Name of the script file including extension (.txt or .md)

### 13. Create Voice Script

**Name**: Create Voice Script  
**Description**: Create a new voice agent instruction script  
**Method**: POST  
**URL**: `https://allegory.ngrok.app/scripts/{filename}`  
**Query Parameters**: None  
**Path Parameters**:
- `filename` (string, required): Name of the script file to create  
**Request Body**:
```json
{
  "content": "string - the voice agent instruction content"
}
```

### 14. Update Voice Script

**Name**: Update Voice Script  
**Description**: Update an existing voice agent instruction script  
**Method**: PUT  
**URL**: `https://allegory.ngrok.app/scripts/{filename}`  
**Query Parameters**: None  
**Path Parameters**:
- `filename` (string, required): Name of the script file to update  
**Request Body**:
```json
{
  "content": "string - the updated voice agent instruction content"
}
```

### 15. Delete Voice Script

**Name**: Delete Voice Script  
**Description**: Delete a voice agent instruction script  
**Method**: DELETE  
**URL**: `https://allegory.ngrok.app/scripts/{filename}`  
**Query Parameters**: None  
**Path Parameters**:
- `filename` (string, required): Name of the script file to delete

## API Response Formats

### Success Responses

**File List Response**:
```json
["file1.md", "file2.md", "file3.md"]
```

**File Content Response**:
```json
{
  "filename": "example.md",
  "content": "# Title\n\nContent here..."
}
```

**File Lines Response**:
```json
{
  "filename": "example.md",
  "lines": [
    {"line_number": 1, "content": "# Title"},
    {"line_number": 2, "content": ""},
    {"line_number": 3, "content": "Content here..."}
  ]
}
```

**Voice Script Content Response**:
```json
{
  "filename": "greeting.txt",
  "content": "You are a friendly customer service representative. When someone calls:\n1. Greet them warmly and ask how you can help\n2. Listen carefully to their request...",
  "size": 256,
  "type": "voice_instruction",
  "description": "Natural language instructions for voice agent"
}
```

**Operation Success Response**:
```json
{
  "message": "File example.md created successfully"
}
```

**Edit with Description Response**:
```json
{
  "message": "File example.md edited successfully using natural language description",
  "description": "Add a new section about installation",
  "preview": "# Updated Test Document\n\nThis is a test markdown file.\n\n## Installation\n\nTo install this project..."
}
```

**Generate Document Response**:
```json
{
  "message": "Document user-guide.md generated successfully using AI",
  "description": "Create a comprehensive user guide for our API",
  "preview": "# User Guide\n\nWelcome to our API! This guide will help you get started with using our service.\n\n## Getting Started\n\n..."
}
```

**Document Summary Response**:
```json
{
  "filename": "technical-spec.md",
  "summary": "This technical specification document outlines the architecture and implementation details for a REST API service. The document covers authentication methods, endpoint definitions, data models, and error handling procedures.",
  "original_length": 2847,
  "summary_length": 156
}
```

### Error Responses

```json
{
  "detail": "File not found"
}
```

## Directory Structure

```
elevenlabs/
├── main.py          # FastAPI server
├── README.md        # This file
├── .env             # Environment variables (OpenAI API key)
├── workspace/       # Markdown files storage
└── scripts/         # Voice agent instruction scripts storage
```

## Usage Examples

### cURL Examples

```bash
# List all markdown files
curl -X GET "https://allegory.ngrok.app/workspace/files"

# Read a file
curl -X GET "https://allegory.ngrok.app/workspace/files/example.md"

# Create a new file
curl -X POST "https://allegory.ngrok.app/workspace/files/newfile.md" \
     -H "Content-Type: application/json" \
     -d '{"content": "# New File\n\nThis is new content."}'

# Update a file
curl -X PUT "https://allegory.ngrok.app/workspace/files/example.md" \
     -H "Content-Type: application/json" \
     -d '{"content": "# Updated Title\n\nUpdated content."}'

# Get file with line numbers
curl -X GET "https://allegory.ngrok.app/workspace/files/example.md/lines"

# Edit a specific line
curl -X PUT "https://allegory.ngrok.app/workspace/files/example.md/lines/1" \
     -H "Content-Type: application/json" \
     -d '{"line_number": 1, "new_content": "# New Title"}'

# Edit with natural language description
curl -X PUT "https://allegory.ngrok.app/workspace/files/example.md/edit" \
     -H "Content-Type: application/json" \
     -d '{"description": "Add a new section about installation instructions after the title"}'

# Generate a new document with AI
curl -X POST "https://allegory.ngrok.app/workspace/files/user-guide.md/generate" \
     -H "Content-Type: application/json" \
     -d '{"description": "Create a comprehensive user guide for our API with installation, authentication, and usage examples"}'

# Summarize an existing document with AI
curl -X GET "https://allegory.ngrok.app/workspace/files/technical-spec.md/summarize"

# List voice scripts
curl -X GET "https://allegory.ngrok.app/scripts"

# Get a voice script
curl -X GET "https://allegory.ngrok.app/scripts/greeting.txt"

# Create a voice script
curl -X POST "https://allegory.ngrok.app/scripts/new_script.txt" \
     -H "Content-Type: application/json" \
     -d '{"content": "You are a helpful assistant. Always be polite and professional."}'

# Update a voice script
curl -X PUT "https://allegory.ngrok.app/scripts/greeting.txt" \
     -H "Content-Type: application/json" \
     -d '{"content": "Updated instructions for the voice agent..."}'
```

## Notes

- The server automatically creates the `workspace` and `scripts` directories if they don't exist
- File names can be provided with or without the `.md` extension for markdown operations
- Line numbers are 1-based (not 0-based)
- The server runs on port 8001 locally by default, but tools are configured to use the public ngrok URL
- All responses are in JSON format
- The API includes comprehensive error handling with appropriate HTTP status codes
- The "Edit with Description" tool requires an OpenAI API key set as the `OPENAI_API_KEY` environment variable
- You can set the API key either in the `.env` file or as an environment variable
- Natural language edits are powered by GPT-4o-mini for cost-effectiveness and speed
