"""Generate parameter variations for exploration."""

from itertools import product
from typing import Any, Dict, List
import random
from copy import deepcopy

from .config import ExplorerConfig, ExplorationStrategy


class VariationGenerator:
    """Generates parameter variations based on exploration strategy."""

    def __init__(self, config: ExplorerConfig):
        """Initialize with exploration configuration."""
        self.config = config

    def generate_variations(self) -> List[Dict[str, Any]]:
        """Generate all parameter variations based on strategy."""
        if self.config.strategy == ExplorationStrategy.GRID:
            return self._generate_grid_variations()
        elif self.config.strategy == ExplorationStrategy.STAR:
            return self._generate_star_variations()
        elif self.config.strategy == ExplorationStrategy.RANDOM:
            return self._generate_random_variations()
        else:
            raise ValueError(f"Unknown strategy: {self.config.strategy}")

    def _generate_grid_variations(self) -> List[Dict[str, Any]]:
        """Generate all combinations of parameters (Cartesian product)."""
        variations = []

        # Get parameter names and their values
        param_names = list(self.config.vary.keys())
        param_values = [self.config.vary[name] for name in param_names]

        # Generate all combinations
        for combination in product(*param_values):
            variation = deepcopy(self.config.baseline)
            variation.update(self.config.fixed)

            # Apply this combination
            for param_name, param_value in zip(param_names, combination):
                variation[param_name] = param_value

            variations.append(variation)

        return variations

    def _generate_star_variations(self) -> List[Dict[str, Any]]:
        """Generate variations by changing one parameter at a time from baseline."""
        variations = []

        # Start with baseline (center of the star)
        baseline = deepcopy(self.config.baseline)
        baseline.update(self.config.fixed)
        variations.append(baseline)

        # For each parameter, vary it while keeping others at baseline
        for param_name, param_values in self.config.vary.items():
            # Get baseline value for this parameter
            baseline_value = baseline.get(param_name)

            for value in param_values:
                # Skip if this value is the same as baseline
                if value == baseline_value:
                    continue

                # Create variation with only this parameter changed
                variation = deepcopy(baseline)
                variation[param_name] = value
                variations.append(variation)

        return variations

    def _generate_random_variations(self) -> List[Dict[str, Any]]:
        """Generate random sampling of parameter combinations."""
        variations = []
        param_names = list(self.config.vary.keys())

        for _ in range(self.config.random_samples):
            variation = deepcopy(self.config.baseline)
            variation.update(self.config.fixed)

            # Randomly select a value for each varied parameter
            for param_name in param_names:
                param_values = self.config.vary[param_name]
                variation[param_name] = random.choice(param_values)

            variations.append(variation)

        return variations

    def get_variation_label(self, variation: Dict[str, Any], index: int) -> str:
        """Generate a descriptive label for a variation.

        Args:
            variation: The parameter variation
            index: The variation index (1-based)

        Returns:
            A human-readable label like "var_001_clusters-16_colorspace-LAB"
        """
        # Start with index
        parts = [f"var_{index:03d}"]

        # Add only the parameters that differ from baseline
        baseline = self.config.baseline
        for param_name, param_value in sorted(variation.items()):
            # Skip if not a varied parameter
            if param_name not in self.config.vary:
                continue

            # Skip if same as baseline
            baseline_value = baseline.get(param_name)
            if param_value == baseline_value:
                continue

            # Add to label (shorten common parameter names)
            short_name = self._shorten_param_name(param_name)
            short_value = self._format_param_value(param_value)
            parts.append(f"{short_name}-{short_value}")

        return "_".join(parts)

    def _shorten_param_name(self, name: str) -> str:
        """Shorten parameter names for labels."""
        replacements = {
            "kMeansNrOfClusters": "clusters",
            "kMeansClusteringColorSpace": "colorspace",
            "kMeansMinDeltaDifference": "delta",
            "removeFacetsSmallerThanNrOfPoints": "minfacet",
            "maximumNumberOfFacets": "maxfacet",
            "narrowPixelStripCleanupRuns": "cleanup",
            "nrOfTimesToHalveBorderSegments": "smooth",
            "resizeImageWidth": "width",
            "resizeImageHeight": "height",
        }
        return replacements.get(name, name)

    def _format_param_value(self, value: Any) -> str:
        """Format parameter value for labels."""
        if isinstance(value, bool):
            return "T" if value else "F"
        elif isinstance(value, float):
            return f"{value:.1f}"
        else:
            return str(value)

    def get_variation_differences(
        self, variation: Dict[str, Any]
    ) -> Dict[str, tuple]:
        """Get parameters that differ from baseline.

        Returns:
            Dict mapping parameter name to (baseline_value, variation_value)
        """
        differences = {}
        baseline = self.config.baseline

        for param_name in self.config.vary.keys():
            baseline_value = baseline.get(param_name)
            variation_value = variation.get(param_name)

            if baseline_value != variation_value:
                differences[param_name] = (baseline_value, variation_value)

        return differences
