"""Tests for Settings class."""

import json
import pytest
from paintbynumbers.core.settings import Settings, ClusteringColorSpace, OutputProfile


class TestSettings:
    """Test Settings class."""

    def test_default_settings(self) -> None:
        """Test creating Settings with default values."""
        settings = Settings()
        assert settings.kMeansNrOfClusters == 16
        assert settings.kMeansClusteringColorSpace == ClusteringColorSpace.RGB
        assert settings.removeFacetsSmallerThanNrOfPoints == 20
        assert settings.randomSeed is None

    def test_custom_settings(self) -> None:
        """Test creating Settings with custom values."""
        settings = Settings(
            kMeansNrOfClusters=24,
            kMeansClusteringColorSpace=ClusteringColorSpace.LAB,
            randomSeed=42
        )
        assert settings.kMeansNrOfClusters == 24
        assert settings.kMeansClusteringColorSpace == ClusteringColorSpace.LAB
        assert settings.randomSeed == 42

    def test_color_space_enum(self) -> None:
        """Test ColorSpace enum values."""
        assert ClusteringColorSpace.RGB.value == "RGB"
        assert ClusteringColorSpace.HSL.value == "HSL"
        assert ClusteringColorSpace.LAB.value == "LAB"

    def test_to_json(self) -> None:
        """Test converting Settings to JSON."""
        settings = Settings(
            kMeansNrOfClusters=20,
            randomSeed=42
        )
        data = settings.to_json()

        assert isinstance(data, dict)
        assert data["kMeansNrOfClusters"] == 20
        assert data["randomSeed"] == 42
        assert data["kMeansClusteringColorSpace"] == "RGB"

    def test_from_json(self) -> None:
        """Test creating Settings from JSON."""
        json_data = {
            "kMeansNrOfClusters": 24,
            "kMeansClusteringColorSpace": "LAB",
            "randomSeed": 12345,
            "removeFacetsSmallerThanNrOfPoints": 30
        }

        settings = Settings.from_json(json_data)
        assert settings.kMeansNrOfClusters == 24
        assert settings.kMeansClusteringColorSpace == ClusteringColorSpace.LAB
        assert settings.randomSeed == 12345
        assert settings.removeFacetsSmallerThanNrOfPoints == 30

    def test_round_trip_json(self) -> None:
        """Test Settings -> JSON -> Settings round trip."""
        original = Settings(
            kMeansNrOfClusters=20,
            kMeansClusteringColorSpace=ClusteringColorSpace.HSL,
            randomSeed=42,
            colorAliases={"255,0,0": "Red"}
        )

        json_data = original.to_json()
        restored = Settings.from_json(json_data)

        assert restored.kMeansNrOfClusters == original.kMeansNrOfClusters
        assert restored.kMeansClusteringColorSpace == original.kMeansClusteringColorSpace
        assert restored.randomSeed == original.randomSeed
        assert restored.colorAliases == original.colorAliases

    def test_color_restrictions(self) -> None:
        """Test color restrictions setting."""
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        settings = Settings(kMeansColorRestrictions=colors)
        assert settings.kMeansColorRestrictions == colors

    def test_output_profile(self) -> None:
        """Test OutputProfile creation."""
        profile = OutputProfile(
            name="test",
            filetype="png",
            svgShowLabels=False,
            svgSizeMultiplier=2.0
        )
        assert profile.name == "test"
        assert profile.filetype == "png"
        assert not profile.svgShowLabels
        assert profile.svgSizeMultiplier == 2.0

    def test_output_profiles_in_settings(self) -> None:
        """Test Settings with custom output profiles."""
        profiles = [
            OutputProfile(name="svg_output", filetype="svg"),
            OutputProfile(name="png_output", filetype="png")
        ]
        settings = Settings(outputProfiles=profiles)
        assert len(settings.outputProfiles) == 2
        assert settings.outputProfiles[0].name == "svg_output"
        assert settings.outputProfiles[1].filetype == "png"
