import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from ocr_service.app.routes import router


logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(
        title="OCR Service",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    app.include_router(router)

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        logger.warning(
            "ocr_request_validation_failed",
            extra={"path": str(request.url.path), "errors": exc.errors()},
        )
        return JSONResponse(status_code=400, content={"detail": exc.errors()})

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        logger.exception(
            "ocr_unexpected_error",
            extra={"path": str(request.url.path), "error": str(exc)},
        )
        return JSONResponse(status_code=500, content={"detail": "internal server error"})

    return app


app = create_app()
