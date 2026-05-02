from __future__ import annotations

from typing import Any

from fastapi import FastAPI, UploadFile, File, Depends
from pydantic import BaseModel

from backend.shared import ApiResponse, require_internal_token

from .service import extract_pdf_text, validate_fields, VALIDATION_PROFILES


class ValidateRequest(BaseModel):
    profile: str
    fields: dict[str, Any]


def register(app: FastAPI) -> None:
    @app.post(
        "/extract",
        response_model=ApiResponse,
        dependencies=[Depends(require_internal_token)],
        tags=["document-ai"],
    )
    async def extract(file: UploadFile = File(...)):
        content = await file.read()
        pages = extract_pdf_text(content)
        total_chars = sum(p["chars"] for p in pages)
        return ApiResponse(data={"filename": file.filename, "pages": pages, "total_chars": total_chars})

    @app.post(
        "/validate",
        response_model=ApiResponse,
        dependencies=[Depends(require_internal_token)],
        tags=["document-ai"],
    )
    async def validate(req: ValidateRequest):
        return ApiResponse(data=validate_fields(req.profile, req.fields))

    @app.get("/profiles", response_model=ApiResponse, tags=["document-ai"])
    async def profiles():
        return ApiResponse(data={"profiles": VALIDATION_PROFILES})
