"""Paint-by-Numbers parameter exploration tool."""

from .config import ExplorerConfig, ExplorationStrategy, get_preset, PRESETS
from .engine import ExplorationEngine, VariationResult
from .metrics import MetricsCollector, VariationMetrics
from .report import HTMLReportGenerator
from .variations import VariationGenerator

__all__ = [
    "ExplorerConfig",
    "ExplorationStrategy",
    "ExplorationEngine",
    "VariationResult",
    "MetricsCollector",
    "VariationMetrics",
    "HTMLReportGenerator",
    "VariationGenerator",
    "get_preset",
    "PRESETS",
]
