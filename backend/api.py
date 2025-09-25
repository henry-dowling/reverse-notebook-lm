from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from handlers.file_handler import FileHandler
from tools.file_tool import FileOperationTool
from config import WORKING_DIRECTORY

app = FastAPI(title="Reverse Notebook LM Tools API")

file_handler = FileHandler(WORKING_DIRECTORY)
file_tool = FileOperationTool(file_handler)


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


