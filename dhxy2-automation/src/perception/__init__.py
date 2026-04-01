from .button_detection import ButtonDetection, detect_battle_command_buttons
from .interfaces import OCRReader, TemplateMatcher
from .observation import ObservationBuilder, ObservationSignalConfig
from .regions import RegionCropper, RegionSpec
from .services import (
    NullOCRReader,
    NullTemplateMatcher,
    OpenCvTemplateMatcher,
    RegionRequest,
    StaticOCRReader,
    StaticTemplateMatcher,
)
from .template_catalog import TemplateCatalog, TemplateDefinition

__all__ = [
    "ButtonDetection",
    "detect_battle_command_buttons",
    "OCRReader",
    "NullOCRReader",
    "NullTemplateMatcher",
    "ObservationBuilder",
    "ObservationSignalConfig",
    "OpenCvTemplateMatcher",
    "RegionCropper",
    "RegionRequest",
    "RegionSpec",
    "StaticOCRReader",
    "StaticTemplateMatcher",
    "TemplateCatalog",
    "TemplateDefinition",
    "TemplateMatcher",
]
