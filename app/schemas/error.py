from pydantic import BaseModel
from typing import Optional


class ErrorResponse(BaseModel):
    status_code: int
    error: str
    detail: Optional[str] = None
    timestamp: Optional[str] = None


class ValidationErrorResponse(ErrorResponse):
    field: Optional[str] = None
    value: Optional[str] = None
