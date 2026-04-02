from dataclasses import asdict
import logging
from time import perf_counter

from fastapi import APIRouter, Depends, HTTPException

from ocr_service.app.dependencies import get_ocr_service, get_settings
from ocr_service.config.settings import Settings
from ocr_service.models.request_models import OCRReadRequest
from ocr_service.models.response_models import HealthResponse, ReadLinesResponse, ReadTextResponse
from ocr_service.providers.base import OCRProviderError
from ocr_service.services.image_loader import InvalidImageInputError
from ocr_service.services.ocr_service import OCRService


router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health", response_model=HealthResponse)
def health(
    settings: Settings = Depends(get_settings),
) -> HealthResponse:
    return HealthResponse(
        status="ok",
        service=settings.service_name,
        provider=settings.provider,
        version=settings.version,
        detail="service is running",
    )


@router.get("/readiness", response_model=HealthResponse)
def readiness(
    settings: Settings = Depends(get_settings),
    service: OCRService = Depends(get_ocr_service),
) -> HealthResponse:
    readiness_status = service.readiness()
    return HealthResponse(
        status=readiness_status.status,
        service=settings.service_name,
        provider=readiness_status.provider,
        version=settings.version,
        detail=readiness_status.detail,
    )


@router.post("/v1/ocr/read-text", response_model=ReadTextResponse)
def read_text(
    request: OCRReadRequest,
    service: OCRService = Depends(get_ocr_service),
) -> ReadTextResponse:
    started_at = perf_counter()
    try:
        result = service.read_text(request)
    except InvalidImageInputError as exc:
        logger.warning("ocr_request_invalid", extra={"route": "read-text", "error": str(exc)})
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        logger.warning("ocr_request_missing_file", extra={"route": "read-text", "error": str(exc)})
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except OCRProviderError as exc:
        logger.error("ocr_provider_failed", extra={"route": "read-text", "error": str(exc)})
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    elapsed_ms = int((perf_counter() - started_at) * 1000)
    return ReadTextResponse(
        text=result.text,
        confidence=result.confidence,
        provider=result.provider,
        elapsed_ms=elapsed_ms,
    )


@router.post("/v1/ocr/read-lines", response_model=ReadLinesResponse)
def read_lines(
    request: OCRReadRequest,
    service: OCRService = Depends(get_ocr_service),
) -> ReadLinesResponse:
    started_at = perf_counter()
    try:
        result = service.read_lines(request)
    except InvalidImageInputError as exc:
        logger.warning("ocr_request_invalid", extra={"route": "read-lines", "error": str(exc)})
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        logger.warning("ocr_request_missing_file", extra={"route": "read-lines", "error": str(exc)})
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except OCRProviderError as exc:
        logger.error("ocr_provider_failed", extra={"route": "read-lines", "error": str(exc)})
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    elapsed_ms = int((perf_counter() - started_at) * 1000)
    return ReadLinesResponse(
        lines=[asdict(line) for line in result.lines],
        provider=result.provider,
        elapsed_ms=elapsed_ms,
    )
