"""Tests for color conversion functions."""

import pytest
import math
from paintbynumbers.utils.color import (
    rgb_to_hsl,
    hsl_to_rgb,
    rgb_to_lab,
    lab_to_rgb,
)


class TestRGBToHSL:
    """Test RGB to HSL conversion."""

    def test_pure_red(self) -> None:
        """Test pure red conversion."""
        h, s, l = rgb_to_hsl(255, 0, 0)
        assert abs(h - 0.0) < 1e-10
        assert abs(s - 1.0) < 1e-10
        assert abs(l - 0.5) < 1e-10

    def test_pure_green(self) -> None:
        """Test pure green conversion."""
        h, s, l = rgb_to_hsl(0, 255, 0)
        assert abs(h - 1.0/3.0) < 1e-10  # 120 degrees / 360
        assert abs(s - 1.0) < 1e-10
        assert abs(l - 0.5) < 1e-10

    def test_pure_blue(self) -> None:
        """Test pure blue conversion."""
        h, s, l = rgb_to_hsl(0, 0, 255)
        assert abs(h - 2.0/3.0) < 1e-10  # 240 degrees / 360
        assert abs(s - 1.0) < 1e-10
        assert abs(l - 0.5) < 1e-10

    def test_black(self) -> None:
        """Test black (achromatic)."""
        h, s, l = rgb_to_hsl(0, 0, 0)
        assert abs(h - 0.0) < 1e-10
        assert abs(s - 0.0) < 1e-10
        assert abs(l - 0.0) < 1e-10

    def test_white(self) -> None:
        """Test white (achromatic)."""
        h, s, l = rgb_to_hsl(255, 255, 255)
        assert abs(h - 0.0) < 1e-10
        assert abs(s - 0.0) < 1e-10
        assert abs(l - 1.0) < 1e-10

    def test_gray(self) -> None:
        """Test gray (achromatic)."""
        h, s, l = rgb_to_hsl(128, 128, 128)
        assert abs(h - 0.0) < 1e-10
        assert abs(s - 0.0) < 1e-10
        assert abs(l - 0.5019607843137255) < 1e-10

    def test_cyan(self) -> None:
        """Test cyan."""
        h, s, l = rgb_to_hsl(0, 255, 255)
        assert abs(h - 0.5) < 1e-10  # 180 degrees / 360
        assert abs(s - 1.0) < 1e-10
        assert abs(l - 0.5) < 1e-10

    def test_magenta(self) -> None:
        """Test magenta."""
        h, s, l = rgb_to_hsl(255, 0, 255)
        assert abs(h - 5.0/6.0) < 1e-10  # 300 degrees / 360
        assert abs(s - 1.0) < 1e-10
        assert abs(l - 0.5) < 1e-10

    def test_yellow(self) -> None:
        """Test yellow."""
        h, s, l = rgb_to_hsl(255, 255, 0)
        assert abs(h - 1.0/6.0) < 1e-10  # 60 degrees / 360
        assert abs(s - 1.0) < 1e-10
        assert abs(l - 0.5) < 1e-10


class TestHSLToRGB:
    """Test HSL to RGB conversion."""

    def test_pure_red(self) -> None:
        """Test pure red conversion."""
        r, g, b = hsl_to_rgb(0.0, 1.0, 0.5)
        assert r == 255
        assert g == 0
        assert b == 0

    def test_pure_green(self) -> None:
        """Test pure green conversion."""
        r, g, b = hsl_to_rgb(1.0/3.0, 1.0, 0.5)
        assert r == 0
        assert g == 255
        assert b == 0

    def test_pure_blue(self) -> None:
        """Test pure blue conversion."""
        r, g, b = hsl_to_rgb(2.0/3.0, 1.0, 0.5)
        assert r == 0
        assert g == 0
        assert b == 255

    def test_black(self) -> None:
        """Test black."""
        r, g, b = hsl_to_rgb(0.0, 0.0, 0.0)
        assert r == 0
        assert g == 0
        assert b == 0

    def test_white(self) -> None:
        """Test white."""
        r, g, b = hsl_to_rgb(0.0, 0.0, 1.0)
        assert r == 255
        assert g == 255
        assert b == 255

    def test_gray(self) -> None:
        """Test gray (achromatic)."""
        r, g, b = hsl_to_rgb(0.0, 0.0, 0.5)
        assert r == 128
        assert g == 128
        assert b == 128


class TestRGBHSLRoundTrip:
    """Test RGB → HSL → RGB round-trip conversions."""

    def test_round_trip_red(self) -> None:
        """Test round-trip for red."""
        r1, g1, b1 = 255, 0, 0
        h, s, l = rgb_to_hsl(r1, g1, b1)
        r2, g2, b2 = hsl_to_rgb(h, s, l)
        assert r1 == r2
        assert g1 == g2
        assert b1 == b2

    def test_round_trip_green(self) -> None:
        """Test round-trip for green."""
        r1, g1, b1 = 0, 255, 0
        h, s, l = rgb_to_hsl(r1, g1, b1)
        r2, g2, b2 = hsl_to_rgb(h, s, l)
        assert r1 == r2
        assert g1 == g2
        assert b1 == b2

    def test_round_trip_blue(self) -> None:
        """Test round-trip for blue."""
        r1, g1, b1 = 0, 0, 255
        h, s, l = rgb_to_hsl(r1, g1, b1)
        r2, g2, b2 = hsl_to_rgb(h, s, l)
        assert r1 == r2
        assert g1 == g2
        assert b1 == b2

    def test_round_trip_arbitrary_colors(self) -> None:
        """Test round-trip for various colors."""
        test_colors = [
            (128, 64, 32),
            (200, 150, 100),
            (50, 100, 150),
            (255, 128, 0),
            (100, 100, 100),
        ]

        for r1, g1, b1 in test_colors:
            h, s, l = rgb_to_hsl(r1, g1, b1)
            r2, g2, b2 = hsl_to_rgb(h, s, l)

            # Allow small rounding differences
            assert abs(r1 - r2) <= 1
            assert abs(g1 - g2) <= 1
            assert abs(b1 - b2) <= 1


class TestRGBToLAB:
    """Test RGB to LAB conversion."""

    def test_pure_red(self) -> None:
        """Test pure red conversion."""
        l, a, b = rgb_to_lab(255, 0, 0)
        # Expected values from TypeScript implementation
        assert abs(l - 53.23288178584245) < 1e-6
        assert abs(a - 80.10930952982204) < 1e-6
        assert abs(b - 67.22006831026425) < 1e-6

    def test_pure_green(self) -> None:
        """Test pure green conversion."""
        l, a, b = rgb_to_lab(0, 255, 0)
        # Green has high L, negative a (green), positive b (yellow)
        assert l > 85  # Bright
        assert a < -70  # Very green
        assert b > 80   # Yellow component

    def test_pure_blue(self) -> None:
        """Test pure blue conversion."""
        l, a, b = rgb_to_lab(0, 0, 255)
        # Blue has medium L, positive a (red tint), very negative b
        assert 30 < l < 35
        assert 70 < a < 85
        assert -110 < b < -100

    def test_black(self) -> None:
        """Test black."""
        l, a, b = rgb_to_lab(0, 0, 0)
        assert abs(l - 0.0) < 1e-6
        assert abs(a - 0.0) < 1e-6
        assert abs(b - 0.0) < 1e-6

    def test_white(self) -> None:
        """Test white."""
        l, a, b = rgb_to_lab(255, 255, 255)
        assert abs(l - 100.0) < 1e-6
        assert abs(a - 0.0) < 0.02  # Near zero (allow small numerical error)
        assert abs(b - 0.0) < 0.02  # Near zero (allow small numerical error)

    def test_gray(self) -> None:
        """Test gray (achromatic)."""
        l, a, b = rgb_to_lab(128, 128, 128)
        # Gray should have L around 53, a and b near 0
        assert 53 < l < 54
        assert abs(a) < 1
        assert abs(b) < 1


class TestLABToRGB:
    """Test LAB to RGB conversion."""

    def test_pure_red_approximate(self) -> None:
        """Test converting LAB red back to RGB."""
        r, g, b = lab_to_rgb(53.23, 80.11, 67.22)
        # Should be approximately red
        assert 250 <= r <= 255
        assert 0 <= g <= 5
        assert 0 <= b <= 5

    def test_black(self) -> None:
        """Test black."""
        r, g, b = lab_to_rgb(0.0, 0.0, 0.0)
        assert r == 0
        assert g == 0
        assert b == 0

    def test_white(self) -> None:
        """Test white."""
        r, g, b = lab_to_rgb(100.0, 0.0, 0.0)
        assert r == 255
        assert g == 255
        assert b == 255


class TestRGBLABRoundTrip:
    """Test RGB → LAB → RGB round-trip conversions."""

    def test_round_trip_red(self) -> None:
        """Test round-trip for red."""
        r1, g1, b1 = 255, 0, 0
        l, a, b = rgb_to_lab(r1, g1, b1)
        r2, g2, b2 = lab_to_rgb(l, a, b)

        # Allow small differences due to color space conversion
        assert abs(r1 - r2) <= 2
        assert abs(g1 - g2) <= 2
        assert abs(b1 - b2) <= 2

    def test_round_trip_green(self) -> None:
        """Test round-trip for green."""
        r1, g1, b1 = 0, 255, 0
        l, a, b = rgb_to_lab(r1, g1, b1)
        r2, g2, b2 = lab_to_rgb(l, a, b)

        assert abs(r1 - r2) <= 2
        assert abs(g1 - g2) <= 2
        assert abs(b1 - b2) <= 2

    def test_round_trip_blue(self) -> None:
        """Test round-trip for blue."""
        r1, g1, b1 = 0, 0, 255
        l, a, b = rgb_to_lab(r1, g1, b1)
        r2, g2, b2 = lab_to_rgb(l, a, b)

        assert abs(r1 - r2) <= 2
        assert abs(g1 - g2) <= 2
        assert abs(b1 - b2) <= 2

    def test_round_trip_arbitrary_colors(self) -> None:
        """Test round-trip for various colors."""
        test_colors = [
            (128, 64, 32),
            (200, 150, 100),
            (50, 100, 150),
            (255, 128, 0),
            (100, 100, 100),
        ]

        for r1, g1, b1 in test_colors:
            l, a, b = rgb_to_lab(r1, g1, b1)
            r2, g2, b2 = lab_to_rgb(l, a, b)

            # LAB conversion can have larger errors
            assert abs(r1 - r2) <= 3
            assert abs(g1 - g2) <= 3
            assert abs(b1 - b2) <= 3

    def test_round_trip_black(self) -> None:
        """Test round-trip for black."""
        r1, g1, b1 = 0, 0, 0
        l, a, b = rgb_to_lab(r1, g1, b1)
        r2, g2, b2 = lab_to_rgb(l, a, b)

        assert r1 == r2 == 0
        assert g1 == g2 == 0
        assert b1 == b2 == 0

    def test_round_trip_white(self) -> None:
        """Test round-trip for white."""
        r1, g1, b1 = 255, 255, 255
        l, a, b = rgb_to_lab(r1, g1, b1)
        r2, g2, b2 = lab_to_rgb(l, a, b)

        assert r1 == r2 == 255
        assert g1 == g2 == 255
        assert b1 == b2 == 255


class TestColorSpaceProperties:
    """Test color space properties and relationships."""

    def test_hsl_saturation_zero_is_gray(self) -> None:
        """Test that S=0 in HSL produces gray regardless of H."""
        for h in [0.0, 0.25, 0.5, 0.75, 1.0]:
            r, g, b = hsl_to_rgb(h, 0.0, 0.5)
            assert r == g == b  # All equal = gray

    def test_hsl_lightness_extremes(self) -> None:
        """Test L=0 gives black, L=1 gives white."""
        # L=0 should give black
        r, g, b = hsl_to_rgb(0.5, 1.0, 0.0)
        assert r == g == b == 0

        # L=1 should give white
        r, g, b = hsl_to_rgb(0.5, 1.0, 1.0)
        assert r == g == b == 255

    def test_lab_achromatic_axis(self) -> None:
        """Test that grays have a* and b* near zero."""
        for gray in [0, 64, 128, 192, 255]:
            l, a, b = rgb_to_lab(gray, gray, gray)
            # a* and b* should be very close to 0 for achromatic colors
            # Allow small numerical errors from floating point conversions
            assert abs(a) < 0.01
            assert abs(b) < 0.02
