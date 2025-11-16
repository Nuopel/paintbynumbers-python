"""Quality metrics for paint-by-numbers variations."""

from dataclasses import dataclass
from typing import List, Tuple
import numpy as np
from ..processing.facetmanagement import FacetResult


@dataclass
class VariationMetrics:
    """Quality metrics for a single variation."""

    # Basic statistics
    num_facets: int
    num_colors: int
    processing_time: float  # seconds

    # Facet size statistics
    min_facet_size: int
    max_facet_size: int
    mean_facet_size: float
    median_facet_size: float

    # Color diversity metrics
    color_diversity_score: float  # 0-1, higher = more diverse colors
    avg_color_saturation: float  # 0-1
    avg_color_lightness: float  # 0-1

    # Complexity metrics
    total_border_points: int
    avg_border_complexity: float  # points per facet
    edge_density: float  # border points / total pixels

    # Image statistics
    image_width: int
    image_height: int
    total_pixels: int

    def to_dict(self) -> dict:
        """Convert metrics to dictionary."""
        return {
            "num_facets": self.num_facets,
            "num_colors": self.num_colors,
            "processing_time": self.processing_time,
            "min_facet_size": self.min_facet_size,
            "max_facet_size": self.max_facet_size,
            "mean_facet_size": self.mean_facet_size,
            "median_facet_size": self.median_facet_size,
            "color_diversity_score": self.color_diversity_score,
            "avg_color_saturation": self.avg_color_saturation,
            "avg_color_lightness": self.avg_color_lightness,
            "total_border_points": self.total_border_points,
            "avg_border_complexity": self.avg_border_complexity,
            "edge_density": self.edge_density,
            "image_width": self.image_width,
            "image_height": self.image_height,
            "total_pixels": self.total_pixels,
        }


class MetricsCollector:
    """Collects quality metrics from pipeline results."""

    @staticmethod
    def collect_metrics(
        facet_result: FacetResult,
        colors: List[Tuple[int, int, int]],
        processing_time: float,
        img_width: int,
        img_height: int,
    ) -> VariationMetrics:
        """Collect all metrics from a pipeline result.

        Args:
            facet_result: The facet result from pipeline
            colors: List of RGB colors used
            processing_time: Time taken to process (seconds)
            img_width: Image width
            img_height: Image height

        Returns:
            VariationMetrics object
        """
        facets = facet_result.facets

        # Filter out None facets (can be deleted during reduction)
        active_facets = [f for f in facets if f is not None]

        # Basic statistics
        num_facets = len(active_facets)
        num_colors = len(colors)

        # Facet size statistics
        facet_sizes = [facet.pointCount for facet in active_facets]
        min_facet_size = min(facet_sizes) if facet_sizes else 0
        max_facet_size = max(facet_sizes) if facet_sizes else 0
        mean_facet_size = np.mean(facet_sizes) if facet_sizes else 0
        median_facet_size = np.median(facet_sizes) if facet_sizes else 0

        # Color diversity metrics
        color_diversity = MetricsCollector._calculate_color_diversity(colors)
        avg_saturation = MetricsCollector._calculate_avg_saturation(colors)
        avg_lightness = MetricsCollector._calculate_avg_lightness(colors)

        # Complexity metrics
        total_border_points = sum(
            len(facet.borderPath) if facet.borderPath else 0
            for facet in active_facets
        )
        avg_border_complexity = (
            total_border_points / num_facets if num_facets > 0 else 0
        )
        total_pixels = img_width * img_height
        edge_density = total_border_points / total_pixels if total_pixels > 0 else 0

        return VariationMetrics(
            num_facets=num_facets,
            num_colors=num_colors,
            processing_time=processing_time,
            min_facet_size=min_facet_size,
            max_facet_size=max_facet_size,
            mean_facet_size=mean_facet_size,
            median_facet_size=median_facet_size,
            color_diversity_score=color_diversity,
            avg_color_saturation=avg_saturation,
            avg_color_lightness=avg_lightness,
            total_border_points=total_border_points,
            avg_border_complexity=avg_border_complexity,
            edge_density=edge_density,
            image_width=img_width,
            image_height=img_height,
            total_pixels=total_pixels,
        )

    @staticmethod
    def _calculate_color_diversity(colors: List[Tuple[int, int, int]]) -> float:
        """Calculate color diversity score (0-1).

        Uses variance in HSV space as a measure of diversity.
        """
        if not colors:
            return 0.0

        # Convert RGB to HSV
        hsv_colors = []
        for r, g, b in colors:
            r_norm, g_norm, b_norm = r / 255.0, g / 255.0, b / 255.0
            max_c = max(r_norm, g_norm, b_norm)
            min_c = min(r_norm, g_norm, b_norm)
            diff = max_c - min_c

            # Hue
            if diff == 0:
                h = 0
            elif max_c == r_norm:
                h = (60 * ((g_norm - b_norm) / diff) + 360) % 360
            elif max_c == g_norm:
                h = (60 * ((b_norm - r_norm) / diff) + 120) % 360
            else:
                h = (60 * ((r_norm - g_norm) / diff) + 240) % 360

            # Saturation
            s = 0 if max_c == 0 else (diff / max_c)

            # Value
            v = max_c

            hsv_colors.append((h, s, v))

        # Calculate variance in each dimension
        hues = [h for h, s, v in hsv_colors]
        saturations = [s for h, s, v in hsv_colors]
        values = [v for h, s, v in hsv_colors]

        # For hue, handle circular nature (0° = 360°)
        hue_variance = MetricsCollector._circular_variance(hues)
        sat_variance = np.var(saturations) if len(saturations) > 1 else 0
        val_variance = np.var(values) if len(values) > 1 else 0

        # Combine variances (hue is most important for diversity)
        diversity = (hue_variance * 0.5 + sat_variance * 0.3 + val_variance * 0.2)

        # Normalize to 0-1 range
        return min(diversity, 1.0)

    @staticmethod
    def _circular_variance(angles: List[float]) -> float:
        """Calculate variance for circular data (angles in degrees)."""
        if len(angles) <= 1:
            return 0.0

        # Convert to radians and calculate mean direction
        radians = [np.deg2rad(a) for a in angles]
        cos_sum = sum(np.cos(r) for r in radians)
        sin_sum = sum(np.sin(r) for r in radians)

        # Mean resultant length
        r_length = np.sqrt(cos_sum ** 2 + sin_sum ** 2) / len(radians)

        # Circular variance (0 = all same, 1 = maximally dispersed)
        return 1 - r_length

    @staticmethod
    def _calculate_avg_saturation(colors: List[Tuple[int, int, int]]) -> float:
        """Calculate average saturation of colors."""
        if not colors:
            return 0.0

        saturations = []
        for r, g, b in colors:
            r_norm, g_norm, b_norm = r / 255.0, g / 255.0, b / 255.0
            max_c = max(r_norm, g_norm, b_norm)
            min_c = min(r_norm, g_norm, b_norm)
            diff = max_c - min_c
            s = 0 if max_c == 0 else (diff / max_c)
            saturations.append(s)

        return float(np.mean(saturations))

    @staticmethod
    def _calculate_avg_lightness(colors: List[Tuple[int, int, int]]) -> float:
        """Calculate average lightness (value) of colors."""
        if not colors:
            return 0.0

        lightness = []
        for r, g, b in colors:
            r_norm, g_norm, b_norm = r / 255.0, g / 255.0, b / 255.0
            v = max(r_norm, g_norm, b_norm)
            lightness.append(v)

        return float(np.mean(lightness))
