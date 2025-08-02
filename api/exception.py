from urllib.request import Request

from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

from api.schema import ErrorResponse, ModelResponse, ErrorDetail


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Bắt lỗi RequestValidationError và định dạng lại theo cấu trúc ModelResponse.
    """
    details = [
        ErrorDetail(
            loc=[str(loc) for loc in err.get("loc", [])],
            msg=err.get("msg"),
            type=err.get("type")
        ) for err in exc.errors()
    ]

    error_response = ErrorResponse(
        code="VALIDATION_ERROR",
        message="Input validation failed.",
        details=details
    )
    response_content = ModelResponse(success=False, error=error_response).model_dump()

    return JSONResponse(
        status_code=422,
        content=response_content,
    )


async def generic_exception_handler(request: Request, exc: Exception):
    error_response = ErrorResponse(
        code="UNEXPECTED_ERROR",
        message="An unexpected internal server error occurred."
    )
    response_content = ModelResponse(success=False, error=error_response).model_dump()

    return JSONResponse(
        status_code=500,
        content=response_content
    )