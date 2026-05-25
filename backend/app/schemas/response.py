"""
Doctor Booking Platform — Standardized API Response Schemas

Every API endpoint returns one of these structures.
Ensures consistency across the entire API surface.

Success:  {"success": true,  "message": "...", "data": {...}}
Error:    {"success": false, "message": "...", "error_code": "..."}
Paginated: {"success": true, "data": [...], "pagination": {...}}
"""

from typing import Any

from pydantic import BaseModel, Field


class APIResponse(BaseModel):
    """Standard success response wrapper."""

    success: bool = True
    message: str = "Success"
    data: Any = None


class APIErrorResponse(BaseModel):
    """Standard error response wrapper (for OpenAPI docs)."""

    success: bool = False
    message: str
    error_code: str
    details: Any = None


class PaginationMeta(BaseModel):
    """Pagination metadata included in paginated responses."""

    total: int = Field(description="Total number of records")
    page: int = Field(description="Current page number (1-indexed)")
    page_size: int = Field(description="Number of records per page")
    total_pages: int = Field(description="Total number of pages")


class PaginatedResponse(BaseModel):
    """Standard paginated response wrapper."""

    success: bool = True
    message: str = "Success"
    data: list[Any] = []
    pagination: PaginationMeta


# ---- Helper Functions ----
# Use these in route handlers instead of constructing dicts manually.

def success(data: Any = None, message: str = "Success") -> dict:
    """Build a success response dict."""
    return {"success": True, "message": message, "data": data}


def paginated(
    items: list,
    total: int,
    page: int,
    page_size: int,
    message: str = "Success",
) -> dict:
    """Build a paginated response dict."""
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    return {
        "success": True,
        "message": message,
        "data": items,
        "pagination": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        },
    }
