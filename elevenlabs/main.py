from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel
from typing import List, Optional
from contextlib import asynccontextmanager
import os
import glob
from pathlib import Path
import openai
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
from google_drive_operations import initialize_google_drive_manager, get_google_drive_manager

# Load environment variables from .env file
load_dotenv()

# Setup logging
LOGGING_DIR = "./logging"
os.makedirs(LOGGING_DIR, exist_ok=True)

# Configure logging
log_filename = os.path.join(LOGGING_DIR, f"http_requests_{datetime.now().strftime('%Y%m%d')}.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Starting ElevenLabs Tools API in {OPERATION_MODE} mode")
    
    if OPERATION_MODE == "google" and google_drive_manager:
        # Try to load existing credentials
        if google_drive_manager.load_credentials():
            logger.info("Successfully loaded existing Google credentials")
        else:
            logger.warning("No valid Google credentials found. Authentication required.")
            logger.warning("Visit /auth/google to authenticate with Google Drive")
    
    yield
    
    # Shutdown
    logger.info("Shutting down ElevenLabs Tools API")

app = FastAPI(
    title="ElevenLabs Tools API",
    description="API for CRUD operations on markdown files and script retrieval",
    version="1.0.0",
    lifespan=lifespan
)

# HTTP request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = datetime.now()
    
    # Log request details
    client_ip = request.client.host
    method = request.method
    url = str(request.url)
    headers = dict(request.headers)
    
    logger.info(f"REQUEST - {method} {url} from {client_ip}")
    logger.info(f"HEADERS - {headers}")
    
    # Process the request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = (datetime.now() - start_time).total_seconds()
    
    # Log response details
    logger.info(f"RESPONSE - {response.status_code} in {process_time:.4f}s")
    
    return response

WORKSPACE_DIR = "./workspace"
SCRIPTS_DIR = "./scripts"

# Initialize OpenAI client (will use OPENAI_API_KEY environment variable)
openai_client = openai.OpenAI() if os.getenv("OPENAI_API_KEY") else None

# Configuration
OPERATION_MODE = os.getenv("OPERATION_MODE", "local").lower()
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/callback")

# Initialize Google Drive manager if in Google mode
google_drive_manager = None
if OPERATION_MODE == "google":
    if not all([GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET]):
        logger.error("Google mode requires GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env file")
    else:
        google_drive_manager = initialize_google_drive_manager(
            GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI, "caplog"
        )

class FileContent(BaseModel):
    content: str

class LineEdit(BaseModel):
    line_number: int
    new_content: str

class FileInfo(BaseModel):
    filename: str
    size: int
    modified: str

class NaturalLanguageEdit(BaseModel):
    description: str

class DocumentGenerationRequest(BaseModel):
    description: str

class DocumentSummarizationRequest(BaseModel):
    pass

@app.get("/")
async def root():
    status_info = {"message": "ElevenLabs Tools API - Ready to serve!", "mode": OPERATION_MODE}
    
    if OPERATION_MODE == "google":
        if google_drive_manager and google_drive_manager.is_authenticated():
            status_info["google_auth"] = "authenticated"
        else:
            status_info["google_auth"] = "not_authenticated"
            status_info["auth_url"] = "/auth/google"
    
    return status_info

@app.get("/auth/google")
async def google_auth():
    """Initiate Google OAuth flow."""
    if OPERATION_MODE != "google":
        raise HTTPException(status_code=400, detail="Google authentication only available in Google mode")
    
    if not google_drive_manager:
        raise HTTPException(status_code=500, detail="Google Drive manager not initialized")
    
    try:
        auth_url = google_drive_manager.get_auth_url()
        return {"auth_url": auth_url, "message": "Visit this URL to authenticate with Google"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create auth URL: {str(e)}")

@app.get("/auth/callback")
async def google_auth_callback(code: str):
    """Handle Google OAuth callback."""
    if OPERATION_MODE != "google":
        raise HTTPException(status_code=400, detail="Google authentication only available in Google mode")
    
    if not google_drive_manager:
        raise HTTPException(status_code=500, detail="Google Drive manager not initialized")
    
    try:
        success = google_drive_manager.handle_auth_callback(code)
        if success:
            return {"message": "Successfully authenticated with Google Drive and Docs!", "status": "authenticated"}
        else:
            raise HTTPException(status_code=400, detail="Failed to authenticate with Google")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication error: {str(e)}")

@app.get("/auth/status")
async def auth_status():
    """Check authentication status."""
    if OPERATION_MODE == "local":
        return {"mode": "local", "status": "no_auth_required"}
    elif OPERATION_MODE == "google":
        if google_drive_manager and google_drive_manager.is_authenticated():
            return {"mode": "google", "status": "authenticated"}
        else:
            return {"mode": "google", "status": "not_authenticated", "auth_url": "/auth/google"}
    else:
        return {"mode": OPERATION_MODE, "status": "unknown"}

@app.post("/")
async def root_post(request: Request):
    """Handle POST requests to root endpoint from ElevenLabs"""
    try:
        body = await request.json()
        logger.info(f"POST / received data: {body}")
        return {"status": "received", "data": body}
    except Exception as e:
        logger.error(f"Error processing POST /: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

# File CRUD operations (works with both local files and Google Drive)
@app.get("/workspace/files")
async def list_files():
    """List files based on current operation mode"""
    try:
        if OPERATION_MODE == "local":
            pattern = os.path.join(WORKSPACE_DIR, "*.md")
            files = [os.path.basename(f) for f in glob.glob(pattern)]
            return [{"name": f, "type": "local"} for f in files]
        
        elif OPERATION_MODE == "google":
            if not google_drive_manager or not google_drive_manager.is_authenticated():
                raise HTTPException(status_code=401, detail="Not authenticated with Google Drive")
            
            files = google_drive_manager.list_files(file_type="documents")
            return [{"name": f["name"], "id": f["id"], "type": "google"} for f in files]
        
        else:
            raise HTTPException(status_code=400, detail=f"Unknown operation mode: {OPERATION_MODE}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/workspace/files/{filename}")
async def read_file(filename: str):
    """Read the content of a file based on current operation mode"""
    try:
        if OPERATION_MODE == "local":
            if not filename.endswith('.md'):
                filename += '.md'
            
            file_path = os.path.join(WORKSPACE_DIR, filename)
            
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail="File not found")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return {"filename": filename, "content": content}
        
        elif OPERATION_MODE == "google":
            if not google_drive_manager or not google_drive_manager.is_authenticated():
                raise HTTPException(status_code=401, detail="Not authenticated with Google Drive")
            
            # In Google mode, filename is actually the file ID
            file_id = filename
            content = google_drive_manager.get_file_content(file_id)
            return {"filename": file_id, "content": content}
        
        else:
            raise HTTPException(status_code=400, detail=f"Unknown operation mode: {OPERATION_MODE}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/workspace/files/{filename}")
async def create_file(filename: str, file_content: FileContent):
    """Create a new file based on current operation mode"""
    try:
        if OPERATION_MODE == "local":
            if not filename.endswith('.md'):
                filename += '.md'
            
            file_path = os.path.join(WORKSPACE_DIR, filename)
            
            if os.path.exists(file_path):
                raise HTTPException(status_code=400, detail="File already exists")
            
            os.makedirs(WORKSPACE_DIR, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file_content.content)
            return {"message": f"File {filename} created successfully"}
        
        elif OPERATION_MODE == "google":
            if not google_drive_manager or not google_drive_manager.is_authenticated():
                raise HTTPException(status_code=401, detail="Not authenticated with Google Drive")
            
            # Create Google Doc
            file_info = google_drive_manager.create_file(
                filename, file_content.content, 'application/vnd.google-apps.document'
            )
            return {"message": f"Google Doc {filename} created successfully", "file_id": file_info["id"]}
        
        else:
            raise HTTPException(status_code=400, detail=f"Unknown operation mode: {OPERATION_MODE}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/workspace/files/{filename}")
async def update_file(filename: str, file_content: FileContent):
    """Update an existing file based on current operation mode"""
    try:
        if OPERATION_MODE == "local":
            if not filename.endswith('.md'):
                filename += '.md'
            
            file_path = os.path.join(WORKSPACE_DIR, filename)
            
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail="File not found")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file_content.content)
            return {"message": f"File {filename} updated successfully"}
        
        elif OPERATION_MODE == "google":
            if not google_drive_manager or not google_drive_manager.is_authenticated():
                raise HTTPException(status_code=401, detail="Not authenticated with Google Drive")
            
            # In Google mode, filename is actually the file ID
            file_id = filename
            file_info = google_drive_manager.update_file(file_id, file_content.content)
            return {"message": f"Google Doc updated successfully", "file_id": file_info["id"]}
        
        else:
            raise HTTPException(status_code=400, detail=f"Unknown operation mode: {OPERATION_MODE}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/workspace/files/{filename}")
async def delete_file(filename: str):
    """Delete a file based on current operation mode"""
    try:
        if OPERATION_MODE == "local":
            if not filename.endswith('.md'):
                filename += '.md'
            
            file_path = os.path.join(WORKSPACE_DIR, filename)
            
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail="File not found")
            
            os.remove(file_path)
            return {"message": f"File {filename} deleted successfully"}
        
        elif OPERATION_MODE == "google":
            if not google_drive_manager or not google_drive_manager.is_authenticated():
                raise HTTPException(status_code=401, detail="Not authenticated with Google Drive")
            
            # In Google mode, filename is actually the file ID
            file_id = filename
            success = google_drive_manager.delete_file(file_id)
            if success:
                return {"message": f"Google Doc deleted successfully"}
            else:
                raise HTTPException(status_code=500, detail="Failed to delete file")
        
        else:
            raise HTTPException(status_code=400, detail=f"Unknown operation mode: {OPERATION_MODE}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/workspace/files/{filename}/lines")
async def get_file_lines(filename: str):
    """Get all lines of a markdown file with line numbers"""
    if not filename.endswith('.md'):
        filename += '.md'
    
    file_path = os.path.join(WORKSPACE_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        numbered_lines = []
        for i, line in enumerate(lines, 1):
            numbered_lines.append({"line_number": i, "content": line.rstrip('\n\r')})
        
        return {"filename": filename, "lines": numbered_lines}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/workspace/files/{filename}/lines/{line_number}")
async def edit_line(filename: str, line_number: int, line_edit: LineEdit):
    """Edit a specific line in a markdown file"""
    if not filename.endswith('.md'):
        filename += '.md'
    
    file_path = os.path.join(WORKSPACE_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if line_number < 1 or line_number > len(lines):
            raise HTTPException(status_code=400, detail="Line number out of range")
        
        lines[line_number - 1] = line_edit.new_content + '\n'
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        return {"message": f"Line {line_number} updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def apply_natural_language_edit(filename: str, current_content: str, description: str) -> str:
    """Use LLM to apply natural language edits to file content"""
    if not openai_client:
        raise HTTPException(status_code=503, detail="OpenAI API not configured. Please set OPENAI_API_KEY environment variable.")
    
    system_prompt = """You are an expert text editor. You will be given the current content of a file and a natural language description of how to edit it. 

Your task is to:
1. Understand the edit request
2. Apply the requested changes to the content
3. Return ONLY the complete modified content (no explanations, no markdown code blocks)
4. Preserve the original formatting and structure unless the edit request specifically asks to change it
5. If the edit request is unclear or impossible, return the original content unchanged

Remember: Return ONLY the modified file content, nothing else."""

    user_prompt = f"""Current file content:
```
{current_content}
```

Edit request: {description}

Please apply the requested edit and return the complete modified content."""

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            max_tokens=4000
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM processing error: {str(e)}")

@app.put("/workspace/files/{filename}/edit")
async def edit_with_description(filename: str, edit_request: NaturalLanguageEdit):
    """Edit a file using natural language description based on current operation mode"""
    try:
        if OPERATION_MODE == "local":
            if not filename.endswith('.md'):
                filename += '.md'
            
            file_path = os.path.join(WORKSPACE_DIR, filename)
            
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail="File not found")
            
            # Read current content
            with open(file_path, 'r', encoding='utf-8') as f:
                current_content = f.read()
            
            # Apply natural language edit using LLM
            modified_content = await apply_natural_language_edit(filename, current_content, edit_request.description)
            
            # Write modified content back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            
            return {
                "message": f"File {filename} edited successfully using natural language description",
                "description": edit_request.description,
                "preview": modified_content[:200] + "..." if len(modified_content) > 200 else modified_content
            }
        
        elif OPERATION_MODE == "google":
            if not google_drive_manager or not google_drive_manager.is_authenticated():
                raise HTTPException(status_code=401, detail="Not authenticated with Google Drive")
            
            # In Google mode, filename is actually the file ID
            file_id = filename
            
            # Get current content
            current_content = google_drive_manager.get_file_content(file_id)
            
            # Apply natural language edit using LLM
            modified_content = await apply_natural_language_edit(file_id, current_content, edit_request.description)
            
            # Update the file
            file_info = google_drive_manager.update_file(file_id, modified_content)
            
            return {
                "message": f"Google Doc edited successfully using natural language description",
                "description": edit_request.description,
                "preview": modified_content[:200] + "..." if len(modified_content) > 200 else modified_content,
                "file_id": file_info["id"]
            }
        
        else:
            raise HTTPException(status_code=400, detail=f"Unknown operation mode: {OPERATION_MODE}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def generate_document_with_ai(filename: str, description: str) -> str:
    """Use LLM to generate document content based on description"""
    if not openai_client:
        raise HTTPException(status_code=503, detail="OpenAI API not configured. Please set OPENAI_API_KEY environment variable.")
    
    system_prompt = """You are an expert technical writer and content creator. You will be given a filename and a plain language description of what the document should contain.

Your task is to:
1. Understand the document purpose from the filename and description
2. Create comprehensive, well-structured content that fulfills the description
3. Use appropriate markdown formatting for the document type
4. Return ONLY the complete document content (no explanations, no markdown code blocks around the content)
5. Make the content professional, clear, and useful

Consider the filename extension and context to determine the appropriate format and style."""

    user_prompt = f"""Filename: {filename}

Document description: {description}

Please generate the complete document content based on this description."""

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=4000
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM processing error: {str(e)}")

@app.post("/workspace/files/{filename}/generate")
async def generate_document_with_description(filename: str, generation_request: DocumentGenerationRequest):
    """Generate a new document using AI based on plain language description"""
    if not filename.endswith('.md'):
        filename += '.md'
    
    file_path = os.path.join(WORKSPACE_DIR, filename)
    
    if os.path.exists(file_path):
        raise HTTPException(status_code=400, detail="File already exists. Use PUT /workspace/files/{filename} to update existing files.")
    
    try:
        os.makedirs(WORKSPACE_DIR, exist_ok=True)
        
        # Generate document content using AI
        generated_content = await generate_document_with_ai(filename, generation_request.description)
        
        # Write generated content to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(generated_content)
        
        return {
            "message": f"Document {filename} generated successfully using AI",
            "description": generation_request.description,
            "preview": generated_content[:200] + "..." if len(generated_content) > 200 else generated_content
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def summarize_document_with_ai(filename: str, content: str) -> str:
    """Use LLM to summarize document content"""
    if not openai_client:
        raise HTTPException(status_code=503, detail="OpenAI API not configured. Please set OPENAI_API_KEY environment variable.")
    
    system_prompt = """You are an expert at reading and summarizing documents. You will be given the content of a document and should provide a concise, comprehensive summary.

Your task is to:
1. Read and understand the document content
2. Identify the main topics, key points, and important information
3. Create a well-structured summary that captures the essence of the document
4. Return ONLY the summary text (no explanations, no markdown code blocks around the content)
5. Make the summary clear, informative, and proportionate to the original content length

The summary should be much shorter than the original while preserving all critical information."""

    user_prompt = f"""Document filename: {filename}

Document content:
{content}

Please provide a comprehensive summary of this document."""

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            max_tokens=2000
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM processing error: {str(e)}")

@app.get("/workspace/files/{filename}/summarize")
async def summarize_document_with_ai_endpoint(filename: str):
    """Summarize an existing document using AI"""
    if not filename.endswith('.md'):
        filename += '.md'
    
    file_path = os.path.join(WORKSPACE_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        # Read current content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.strip():
            raise HTTPException(status_code=400, detail="Cannot summarize empty file")
        
        # Generate summary using AI
        summary = await summarize_document_with_ai(filename, content)
        
        return {
            "filename": filename,
            "summary": summary,
            "original_length": len(content),
            "summary_length": len(summary)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Voice agent script operations
@app.get("/scripts", response_model=List[str])
async def list_voice_scripts():
    """List all voice agent instruction scripts in the scripts directory"""
    try:
        if not os.path.exists(SCRIPTS_DIR):
            return []
        
        files = []
        for ext in ['*.txt', '*.md']:
            pattern = os.path.join(SCRIPTS_DIR, ext)
            files.extend([os.path.basename(f) for f in glob.glob(pattern)])
        return files
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/scripts/{filename}")
async def get_voice_script(filename: str):
    """Retrieve a specific voice agent instruction script"""
    file_path = os.path.join(SCRIPTS_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Voice script not found")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        file_stat = os.stat(file_path)
        return {
            "filename": filename,
            "content": content,
            "size": file_stat.st_size,
            "type": "voice_instruction",
            "description": "Natural language instructions for voice agent"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scripts/{filename}")
async def create_voice_script(filename: str, file_content: FileContent):
    """Create a new voice agent instruction script"""
    if not (filename.endswith('.txt') or filename.endswith('.md')):
        filename += '.txt'
    
    file_path = os.path.join(SCRIPTS_DIR, filename)
    
    if os.path.exists(file_path):
        raise HTTPException(status_code=400, detail="Script already exists")
    
    try:
        os.makedirs(SCRIPTS_DIR, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(file_content.content)
        return {"message": f"Voice script {filename} created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/scripts/{filename}")
async def update_voice_script(filename: str, file_content: FileContent):
    """Update an existing voice agent instruction script"""
    file_path = os.path.join(SCRIPTS_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Script not found")
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(file_content.content)
        return {"message": f"Voice script {filename} updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/scripts/{filename}")
async def delete_voice_script(filename: str):
    """Delete a voice agent instruction script"""
    file_path = os.path.join(SCRIPTS_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Script not found")
    
    try:
        os.remove(file_path)
        return {"message": f"Voice script {filename} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)