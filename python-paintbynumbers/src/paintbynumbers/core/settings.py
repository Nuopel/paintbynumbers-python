"""Settings and configuration for Paint by Numbers Generator."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Tuple, Dict


class ClusteringColorSpace(str, Enum):
    """Color space options for K-means clustering."""
    RGB = "RGB"
    HSL = "HSL"
    LAB = "LAB"


@dataclass
class OutputProfile:
    """Configuration for a single output file."""
    name: str
    filetype: str = "svg"  # svg, png, jpg
    svgShowLabels: bool = True
    svgShowBorders: bool = True
    svgFillFacets: bool = True
    svgSizeMultiplier: float = 3.0
    svgFontSize: int = 20
    svgFontColor: str = "#000000"
    filetypeQuality: float = 0.92  # For JPEG quality


@dataclass
class Settings:
    """Settings for paint-by-numbers generation.

    This class contains all configurable parameters for the processing pipeline.
    Settings can be loaded from/saved to JSON for reproducibility.
    """

    # K-means clustering settings
    kMeansNrOfClusters: int = 16
    kMeansMinDeltaDifference: float = 1.0
    kMeansClusteringColorSpace: ClusteringColorSpace = ClusteringColorSpace.RGB
    kMeansColorRestrictions: Optional[List[Tuple[int, int, int]]] = None

    # Color aliases (for restricted colors)
    colorAliases: Dict[str, str] = field(default_factory=dict)

    # Random seed for reproducibility
    randomSeed: Optional[int] = None

    # Facet processing settings
    removeFacetsSmallerThanNrOfPoints: int = 20
    removeFacetsFromLargeToSmall: bool = True
    maximumNumberOfFacets: Optional[int] = None

    # Strip cleanup
    narrowPixelStripCleanupRuns: int = 3

    # Border smoothing
    nrOfTimesToHalveBorderSegments: int = 2

    # Image resizing
    resizeImageIfTooLarge: bool = True
    resizeImageWidth: int = 1024
    resizeImageHeight: int = 1024

    # Output profiles
    outputProfiles: List[OutputProfile] = field(default_factory=lambda: [
        OutputProfile(
            name="default",
            filetype="svg",
            svgShowLabels=True,
            svgShowBorders=True,
            svgFillFacets=True,
            svgSizeMultiplier=3.0,
            svgFontSize=20,
            svgFontColor="#000000"
        )
    ])

    @classmethod
    def from_json(cls, data: dict) -> "Settings":
        """Create Settings from JSON dictionary.

        Args:
            data: Dictionary containing settings

        Returns:
            Settings instance
        """
        # Handle color space enum
        if "kMeansClusteringColorSpace" in data:
            data["kMeansClusteringColorSpace"] = ClusteringColorSpace(
                data["kMeansClusteringColorSpace"]
            )

        # Handle output profiles
        if "outputProfiles" in data:
            data["outputProfiles"] = [
                OutputProfile(**profile) for profile in data["outputProfiles"]
            ]

        # Handle color restrictions (convert to tuples)
        if "kMeansColorRestrictions" in data and data["kMeansColorRestrictions"]:
            data["kMeansColorRestrictions"] = [
                tuple(color) for color in data["kMeansColorRestrictions"]
            ]

        return cls(**data)

    def to_json(self) -> dict:
        """Convert Settings to JSON-serializable dictionary.

        Returns:
            Dictionary suitable for JSON serialization
        """
        data = {
            "kMeansNrOfClusters": self.kMeansNrOfClusters,
            "kMeansMinDeltaDifference": self.kMeansMinDeltaDifference,
            "kMeansClusteringColorSpace": self.kMeansClusteringColorSpace.value,
            "kMeansColorRestrictions": self.kMeansColorRestrictions,
            "colorAliases": self.colorAliases,
            "randomSeed": self.randomSeed,
            "removeFacetsSmallerThanNrOfPoints": self.removeFacetsSmallerThanNrOfPoints,
            "removeFacetsFromLargeToSmall": self.removeFacetsFromLargeToSmall,
            "maximumNumberOfFacets": self.maximumNumberOfFacets,
            "narrowPixelStripCleanupRuns": self.narrowPixelStripCleanupRuns,
            "nrOfTimesToHalveBorderSegments": self.nrOfTimesToHalveBorderSegments,
            "resizeImageIfTooLarge": self.resizeImageIfTooLarge,
            "resizeImageWidth": self.resizeImageWidth,
            "resizeImageHeight": self.resizeImageHeight,
            "outputProfiles": [
                {
                    "name": p.name,
                    "filetype": p.filetype,
                    "svgShowLabels": p.svgShowLabels,
                    "svgShowBorders": p.svgShowBorders,
                    "svgFillFacets": p.svgFillFacets,
                    "svgSizeMultiplier": p.svgSizeMultiplier,
                    "svgFontSize": p.svgFontSize,
                    "svgFontColor": p.svgFontColor,
                    "filetypeQuality": p.filetypeQuality,
                }
                for p in self.outputProfiles
            ],
        }
        return data
