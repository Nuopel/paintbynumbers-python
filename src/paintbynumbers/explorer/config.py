"""Configuration for the parameter exploration tool."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import json


class ExplorationStrategy(str, Enum):
    """Strategy for generating parameter combinations."""
    GRID = "grid"  # Test all combinations (exhaustive)
    STAR = "star"  # Vary one parameter at a time from baseline
    RANDOM = "random"  # Random sampling when grid would be too large


@dataclass
class ExplorerConfig:
    """Configuration for parameter exploration."""

    # Exploration strategy
    strategy: ExplorationStrategy = ExplorationStrategy.STAR

    # For random strategy: number of samples to generate
    random_samples: int = 20

    # Baseline configuration (starting point for star exploration)
    baseline: Dict[str, Any] = field(default_factory=lambda: {
        "kMeansNrOfClusters": 16,
        "kMeansMinDeltaDifference": 1.0,
        "kMeansClusteringColorSpace": "RGB",
        "removeFacetsSmallerThanNrOfPoints": 20,
        "removeFacetsFromLargeToSmall": True,
        "narrowPixelStripCleanupRuns": 3,
        "nrOfTimesToHalveBorderSegments": 2,
        "resizeImageWidth": 1024,
        "resizeImageHeight": 1024,
    })

    # Parameters to vary with their possible values
    vary: Dict[str, List[Any]] = field(default_factory=lambda: {
        "kMeansNrOfClusters": [8, 16, 24],
        "kMeansClusteringColorSpace": ["RGB", "LAB", "HSL"],
    })

    # Fixed parameters (won't be varied)
    fixed: Dict[str, Any] = field(default_factory=dict)

    # Output settings
    output_dir: Optional[Path] = None
    save_intermediate: bool = True  # Save each variation's output
    parallel_processing: bool = True
    max_workers: Optional[int] = None  # None = use CPU count

    # Warnings
    warn_threshold: int = 50  # Warn if combinations exceed this

    @classmethod
    def from_json(cls, json_path: Union[str, Path]) -> "ExplorerConfig":
        """Load configuration from JSON file."""
        with open(json_path, 'r') as f:
            data = json.load(f)

        # Convert strategy string to enum
        if "strategy" in data:
            data["strategy"] = ExplorationStrategy(data["strategy"])

        # Convert output_dir to Path
        if "output_dir" in data and data["output_dir"] is not None:
            data["output_dir"] = Path(data["output_dir"])

        return cls(**data)

    def to_json(self, json_path: Union[str, Path]) -> None:
        """Save configuration to JSON file."""
        data = {
            "strategy": self.strategy.value,
            "random_samples": self.random_samples,
            "baseline": self.baseline,
            "vary": self.vary,
            "fixed": self.fixed,
            "output_dir": str(self.output_dir) if self.output_dir else None,
            "save_intermediate": self.save_intermediate,
            "parallel_processing": self.parallel_processing,
            "max_workers": self.max_workers,
            "warn_threshold": self.warn_threshold,
        }

        with open(json_path, 'w') as f:
            json.dump(data, f, indent=2)

    def get_total_combinations(self) -> int:
        """Calculate total number of combinations based on strategy."""
        if self.strategy == ExplorationStrategy.RANDOM:
            return self.random_samples
        elif self.strategy == ExplorationStrategy.STAR:
            # One baseline + one variation per value per parameter
            total = 1  # baseline
            for param_values in self.vary.values():
                total += len(param_values) - 1  # -1 because baseline already counted
            return total
        else:  # GRID
            total = 1
            for param_values in self.vary.values():
                total *= len(param_values)
            return total


# Preset configurations for common use cases
PRESETS = {
    "quick_test": ExplorerConfig(
        strategy=ExplorationStrategy.STAR,
        baseline={
            "kMeansNrOfClusters": 16,
            "kMeansClusteringColorSpace": "RGB",
            "removeFacetsSmallerThanNrOfPoints": 20,
        },
        vary={
            "kMeansNrOfClusters": [8, 16, 24],
            "removeFacetsSmallerThanNrOfPoints": [10, 20],
        },
    ),

    "detailed_photos": ExplorerConfig(
        strategy=ExplorationStrategy.GRID,
        baseline={
            "kMeansNrOfClusters": 24,
            "kMeansClusteringColorSpace": "LAB",
            "removeFacetsSmallerThanNrOfPoints": 30,
        },
        vary={
            "kMeansNrOfClusters": [16, 24, 32],
            "kMeansClusteringColorSpace": ["LAB"],
            "removeFacetsSmallerThanNrOfPoints": [20, 30, 40],
        },
    ),

    "simple_illustrations": ExplorerConfig(
        strategy=ExplorationStrategy.GRID,
        baseline={
            "kMeansNrOfClusters": 8,
            "kMeansClusteringColorSpace": "RGB",
            "removeFacetsSmallerThanNrOfPoints": 50,
        },
        vary={
            "kMeansNrOfClusters": [6, 8, 12],
            "removeFacetsSmallerThanNrOfPoints": [50, 100],
        },
    ),

    "color_space_comparison": ExplorerConfig(
        strategy=ExplorationStrategy.STAR,
        baseline={
            "kMeansNrOfClusters": 16,
            "kMeansClusteringColorSpace": "RGB",
        },
        vary={
            "kMeansClusteringColorSpace": ["RGB", "LAB", "HSL"],
        },
    ),

    "cluster_exploration": ExplorerConfig(
        strategy=ExplorationStrategy.STAR,
        baseline={
            "kMeansNrOfClusters": 16,
        },
        vary={
            "kMeansNrOfClusters": [4, 8, 12, 16, 20, 24, 32],
        },
    ),
}


def get_preset(name: str) -> ExplorerConfig:
    """Get a preset configuration by name."""
    if name not in PRESETS:
        available = ", ".join(PRESETS.keys())
        raise ValueError(f"Unknown preset '{name}'. Available: {available}")
    return PRESETS[name]
