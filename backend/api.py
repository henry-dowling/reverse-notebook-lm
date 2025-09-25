from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from handlers.file_handler import FileHandler
from tools.file_tool import FileOperationTool
from config import WORKING_DIRECTORY
import json
import os
from pathlib import Path

app = FastAPI(title="Reverse Notebook LM Tools API")

file_handler = FileHandler(WORKING_DIRECTORY)
file_tool = FileOperationTool(file_handler)

# Scripts directory
SCRIPTS_DIR = Path(__file__).parent / "scripts"


class FileOpPayload(BaseModel):
    operation: str
    filename: str | None = None
    content: str | None = None
    line_number: int | None = None
    pattern: str | None = None
    replacement: str | None = None


@app.post("/tools/file_operation")
async def file_operation(payload: FileOpPayload):
    try:
        result = await file_tool.execute(
            operation=payload.operation,
            filename=payload.filename or "output.md",
            content=payload.content,
            line_number=payload.line_number,
            pattern=payload.pattern,
            replacement=payload.replacement,
        )
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/scripts")
async def list_scripts():
    """List all available scripts"""
    try:
        script_files = list(SCRIPTS_DIR.glob("*.json"))
        script_names = [f.stem for f in script_files]
        return script_names
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/scripts/{script_name}")
async def get_script(script_name: str):
    """Get a specific script by name"""
    try:
        script_path = SCRIPTS_DIR / f"{script_name}.json"
        if not script_path.exists():
            raise HTTPException(status_code=404, detail=f"Script '{script_name}' not found")
        
        with open(script_path, 'r', encoding='utf-8') as f:
            script_data = json.load(f)
        
        return script_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


