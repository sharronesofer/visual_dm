from fastapi import HTTPException, status
from typing import Optional, Dict, Any, List
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)

# Standard error responses
class ErrorResponseModel:
    @staticmethod
    def error(error_msg: str, code: int, error_details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {
            "error": True,
            "message": error_msg,
            "code": code,
            "details": error_details or {}
        }


# Exception handlers to register with the application
def add_exception_handlers(app: FastAPI) -> None:
    """
    Add exception handlers to the FastAPI application
    """
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """
        Handle validation errors in a standardized way
        """
        errors = []
        for error in exc.errors():
            error_details = {
                "loc": error.get("loc", []),
                "msg": error.get("msg", ""),
                "type": error.get("type", "")
            }
            errors.append(error_details)
        
        logger.warning(f"Validation error: {errors}")
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ErrorResponseModel.error(
                "Validation error",
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                {"errors": errors}
            )
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """
        Handle HTTP exceptions in a standardized way
        """
        headers = getattr(exc, "headers", None)
        
        logger.warning(f"HTTP error {exc.status_code}: {exc.detail}")
        
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponseModel.error(
                exc.detail,
                exc.status_code
            ),
            headers=headers
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """
        Handle all other exceptions in a standardized way
        """
        logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponseModel.error(
                "Internal server error",
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                {"detail": str(exc) if app.debug else "An unexpected error occurred"}
            )
        )


# Common exceptions
class NotFoundError(HTTPException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class BadRequestError(HTTPException):
    def __init__(self, detail: str = "Bad request"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class UnauthorizedError(HTTPException):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class ForbiddenError(HTTPException):
    def __init__(self, detail: str = "Access forbidden"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail) 