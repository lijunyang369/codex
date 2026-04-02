from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    service: str
    provider: str
    version: str
    detail: str = ""


class OCRLineResponse(BaseModel):
    text: str
    confidence: float
    bounds: list[int] | None = None


class ReadTextResponse(BaseModel):
    text: str
    confidence: float
    provider: str
    elapsed_ms: int = Field(default=0, ge=0)


class ReadLinesResponse(BaseModel):
    lines: list[OCRLineResponse]
    provider: str
    elapsed_ms: int = Field(default=0, ge=0)

