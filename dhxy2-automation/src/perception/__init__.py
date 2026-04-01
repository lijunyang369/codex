from .battle_command_profiles import BattleCommandProfile, BattleCommandProfileCatalog
from .battle_button_semantics import (
    BattleButtonSemanticCatalog,
    BattleButtonSemanticRule,
    SemanticVerificationResult,
)
from .button_detection import (
    BattleCommandCalibrationSuggestion,
    ButtonDetection,
    build_battle_command_calibration_suggestion,
    detect_battle_command_buttons,
)
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
    "BattleCommandProfile",
    "BattleCommandProfileCatalog",
    "BattleButtonSemanticCatalog",
    "BattleButtonSemanticRule",
    "BattleCommandCalibrationSuggestion",
    "detect_battle_command_buttons",
    "build_battle_command_calibration_suggestion",
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
    "SemanticVerificationResult",
    "TemplateCatalog",
    "TemplateDefinition",
    "TemplateMatcher",
]
