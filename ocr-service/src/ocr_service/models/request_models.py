from pydantic import BaseModel, Field, model_validator


class OCRReadRequest(BaseModel):
    image_path: str | None = None
    image_base64: str | None = None
    profile: str = Field(default="default", max_length=64)
    allowlist: str | None = Field(default=None, max_length=256)

    @model_validator(mode="after")
    def validate_source(self) -> "OCRReadRequest":
        if bool(self.image_path) == bool(self.image_base64):
            raise ValueError("exactly one of image_path or image_base64 must be provided")
        return self

