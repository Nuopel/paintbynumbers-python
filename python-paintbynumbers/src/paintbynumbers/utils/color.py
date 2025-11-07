"""Color space conversion utilities.

This module provides functions to convert between RGB, HSL, and LAB color spaces.
The implementations match the TypeScript version exactly to ensure identical
K-means clustering results across color spaces.

References:
- RGB ↔ HSL: http://en.wikipedia.org/wiki/HSL_color_space
- RGB ↔ LAB: https://github.com/antimatter15/rgb-lab
"""

from __future__ import annotations
from typing import Tuple
import math

# Type aliases
HSL = Tuple[float, float, float]  # Hue, Saturation, Lightness (all 0-1)
LAB = Tuple[float, float, float]  # L*, a*, b*
RGB = Tuple[int, int, int]        # Red, Green, Blue (0-255)


def rgb_to_hsl(r: int, g: int, b: int) -> HSL:
    """Convert RGB color to HSL.

    Conversion formula adapted from http://en.wikipedia.org/wiki/HSL_color_space.
    Assumes r, g, and b are in [0, 255] and returns h, s, and l in [0, 1].

    Args:
        r: Red component (0-255)
        g: Green component (0-255)
        b: Blue component (0-255)

    Returns:
        Tuple of (hue, saturation, lightness) each in range [0, 1]

    Example:
        >>> rgb_to_hsl(255, 0, 0)  # Pure red
        (0.0, 1.0, 0.5)
        >>> rgb_to_hsl(128, 128, 128)  # Gray
        (0.0, 0.0, 0.5019607843137255)
    """
    # Normalize to [0, 1]
    r_norm = r / 255.0
    g_norm = g / 255.0
    b_norm = b / 255.0

    max_val = max(r_norm, g_norm, b_norm)
    min_val = min(r_norm, g_norm, b_norm)
    l = (max_val + min_val) / 2.0

    if max_val == min_val:
        # Achromatic (gray)
        h = 0.0
        s = 0.0
    else:
        d = max_val - min_val
        s = d / (2.0 - max_val - min_val) if l > 0.5 else d / (max_val + min_val)

        # Calculate hue
        if max_val == r_norm:
            h = (g_norm - b_norm) / d + (6.0 if g_norm < b_norm else 0.0)
        elif max_val == g_norm:
            h = (b_norm - r_norm) / d + 2.0
        else:  # max_val == b_norm
            h = (r_norm - g_norm) / d + 4.0

        h /= 6.0

    return (h, s, l)


def hsl_to_rgb(h: float, s: float, l: float) -> RGB:
    """Convert HSL color to RGB.

    Conversion formula adapted from http://en.wikipedia.org/wiki/HSL_color_space.
    Assumes h, s, and l are in [0, 1] and returns r, g, and b in [0, 255].

    Args:
        h: Hue (0-1)
        s: Saturation (0-1)
        l: Lightness (0-1)

    Returns:
        Tuple of (red, green, blue) each in range [0, 255]

    Example:
        >>> hsl_to_rgb(0.0, 1.0, 0.5)  # Pure red
        (255, 0, 0)
        >>> hsl_to_rgb(0.0, 0.0, 0.5)  # Gray
        (127, 127, 127)
    """
    if s == 0.0:
        # Achromatic (gray)
        r = g = b = l
    else:
        def hue2rgb(p: float, q: float, t: float) -> float:
            """Helper function for HSL to RGB conversion."""
            if t < 0.0:
                t += 1.0
            if t > 1.0:
                t -= 1.0
            if t < 1.0 / 6.0:
                return p + (q - p) * 6.0 * t
            if t < 1.0 / 2.0:
                return q
            if t < 2.0 / 3.0:
                return p + (q - p) * (2.0 / 3.0 - t) * 6.0
            return p

        q = l * (1.0 + s) if l < 0.5 else l + s - l * s
        p = 2.0 * l - q

        r = hue2rgb(p, q, h + 1.0 / 3.0)
        g = hue2rgb(p, q, h)
        b = hue2rgb(p, q, h - 1.0 / 3.0)

    return (
        int(round(r * 255.0)),
        int(round(g * 255.0)),
        int(round(b * 255.0))
    )


def rgb_to_lab(r: int, g: int, b: int) -> LAB:
    """Convert RGB color to LAB.

    Uses D65 illuminant and sRGB color space.
    Based on https://github.com/antimatter15/rgb-lab

    Args:
        r: Red component (0-255)
        g: Green component (0-255)
        b: Blue component (0-255)

    Returns:
        Tuple of (L*, a*, b*) where:
        - L*: Lightness (0-100)
        - a*: Green-red axis
        - b*: Blue-yellow axis

    Example:
        >>> rgb_to_lab(255, 0, 0)  # Pure red
        (53.23288178584245, 80.10930952982204, 67.22006831026425)
    """
    # Normalize to [0, 1]
    r_norm = r / 255.0
    g_norm = g / 255.0
    b_norm = b / 255.0

    # Apply sRGB gamma correction
    r_linear = math.pow((r_norm + 0.055) / 1.055, 2.4) if r_norm > 0.04045 else r_norm / 12.92
    g_linear = math.pow((g_norm + 0.055) / 1.055, 2.4) if g_norm > 0.04045 else g_norm / 12.92
    b_linear = math.pow((b_norm + 0.055) / 1.055, 2.4) if b_norm > 0.04045 else b_norm / 12.92

    # Convert to XYZ using D65 illuminant
    x = (r_linear * 0.4124 + g_linear * 0.3576 + b_linear * 0.1805) / 0.95047
    y = (r_linear * 0.2126 + g_linear * 0.7152 + b_linear * 0.0722) / 1.00000
    z = (r_linear * 0.0193 + g_linear * 0.1192 + b_linear * 0.9505) / 1.08883

    # Apply LAB transformation
    x = math.pow(x, 1.0 / 3.0) if x > 0.008856 else (7.787 * x) + 16.0 / 116.0
    y = math.pow(y, 1.0 / 3.0) if y > 0.008856 else (7.787 * y) + 16.0 / 116.0
    z = math.pow(z, 1.0 / 3.0) if z > 0.008856 else (7.787 * z) + 16.0 / 116.0

    return (
        (116.0 * y) - 16.0,  # L*
        500.0 * (x - y),      # a*
        200.0 * (y - z)       # b*
    )


def lab_to_rgb(l: float, a: float, b: float) -> RGB:
    """Convert LAB color to RGB.

    Uses D65 illuminant and sRGB color space.
    Based on https://github.com/antimatter15/rgb-lab

    Args:
        l: L* (lightness) typically 0-100
        a: a* (green-red axis)
        b: b* (blue-yellow axis)

    Returns:
        Tuple of (red, green, blue) each in range [0, 255]

    Example:
        >>> lab_to_rgb(53.23, 80.11, 67.22)  # Approximately pure red
        (255, 0, 0)
    """
    # Convert LAB to XYZ
    y = (l + 16.0) / 116.0
    x = a / 500.0 + y
    z = y - b / 200.0

    # Apply inverse LAB transformation
    x = 0.95047 * (math.pow(x, 3.0) if x * x * x > 0.008856 else (x - 16.0 / 116.0) / 7.787)
    y = 1.00000 * (math.pow(y, 3.0) if y * y * y > 0.008856 else (y - 16.0 / 116.0) / 7.787)
    z = 1.08883 * (math.pow(z, 3.0) if z * z * z > 0.008856 else (z - 16.0 / 116.0) / 7.787)

    # Convert XYZ to linear RGB
    r_linear = x *  3.2406 + y * -1.5372 + z * -0.4986
    g_linear = x * -0.9689 + y *  1.8758 + z *  0.0415
    b_linear = x *  0.0557 + y * -0.2040 + z *  1.0570

    # Apply sRGB gamma correction
    r = 1.055 * math.pow(r_linear, 1.0 / 2.4) - 0.055 if r_linear > 0.0031308 else 12.92 * r_linear
    g = 1.055 * math.pow(g_linear, 1.0 / 2.4) - 0.055 if g_linear > 0.0031308 else 12.92 * g_linear
    b = 1.055 * math.pow(b_linear, 1.0 / 2.4) - 0.055 if b_linear > 0.0031308 else 12.92 * b_linear

    # Clamp to [0, 1] and convert to [0, 255]
    return (
        int(round(max(0.0, min(1.0, r)) * 255.0)),
        int(round(max(0.0, min(1.0, g)) * 255.0)),
        int(round(max(0.0, min(1.0, b)) * 255.0))
    )
