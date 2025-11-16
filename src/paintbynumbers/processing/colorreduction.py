"""Color reduction management for paint-by-numbers generation.

This module handles color quantization using K-means clustering and creation
of color maps that assign each pixel to a color index.
"""

from __future__ import annotations
from typing import List, Dict, Tuple
import numpy as np
from numpy.typing import NDArray

from paintbynumbers.core.types import RGB
from paintbynumbers.core.settings import Settings, ClusteringColorSpace
from paintbynumbers.structs.typed_arrays import Uint8Array2D
from paintbynumbers.algorithms.kmeans import KMeans
from paintbynumbers.algorithms.vector import Vector
from paintbynumbers.utils.random import Random
from paintbynumbers.utils.color import rgb_to_hsl, hsl_to_rgb, rgb_to_lab, lab_to_rgb


class ColorMapResult:
    """Result of color map creation.

    Attributes:
        imgColorIndices: 2D array mapping pixels to color indices
        colorsByIndex: Array of RGB colors indexed by color index
        width: Image width
        height: Image height

    Example:
        >>> result = ColorMapResult()
        >>> result.width = 100
        >>> result.height = 100
        >>> result.imgColorIndices = Uint8Array2D(100, 100)
        >>> result.colorsByIndex = [(255, 0, 0), (0, 255, 0)]
    """

    def __init__(self) -> None:
        """Create a new color map result."""
        self.imgColorIndices: Uint8Array2D = None  # type: ignore
        self.colorsByIndex: List[RGB] = []
        self.width: int = 0
        self.height: int = 0


class ColorReducer:
    """Color reduction using K-means clustering.

    Provides static methods for reducing colors in an image using K-means
    clustering in various color spaces (RGB, HSL, LAB).
    """

    @staticmethod
    def create_color_map(img_data: NDArray[np.uint8], width: int, height: int) -> ColorMapResult:
        """Create a map of the various colors used in an image.

        Args:
            img_data: Image data as numpy array (height, width, 3) with RGB values
            width: Image width
            height: Image height

        Returns:
            ColorMapResult with color indices and color palette

        Example:
            >>> img_data = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
            >>> result = ColorReducer.create_color_map(img_data, 100, 100)
            >>> print(f"Found {len(result.colorsByIndex)} unique colors")
        """
        # OPTIMIZED: Use NumPy vectorization for 10-100x speedup
        # Reshape image to (height*width, 3) for processing
        pixels_flat = img_data.reshape(-1, 3)

        # Find unique colors and their inverse mapping (indices)
        # unique_colors: array of unique RGB tuples
        # indices: maps each pixel to its unique color index
        unique_colors, indices = np.unique(pixels_flat, axis=0, return_inverse=True)

        # Reshape indices back to 2D image shape
        indices_2d = indices.reshape(height, width).astype(np.uint8)

        # Create Uint8Array2D from numpy array
        img_color_indices = Uint8Array2D(width, height)
        for j in range(height):
            for i in range(width):
                img_color_indices.set(i, j, int(indices_2d[j, i]))

        # Convert unique colors to list of RGB tuples
        colors_by_index: List[RGB] = [
            (int(color[0]), int(color[1]), int(color[2]))
            for color in unique_colors
        ]

        result = ColorMapResult()
        result.imgColorIndices = img_color_indices
        result.colorsByIndex = colors_by_index
        result.width = width
        result.height = height

        return result

    @staticmethod
    def apply_kmeans_clustering(
        img_data: NDArray[np.uint8],
        width: int,
        height: int,
        settings: Settings
    ) -> Tuple[NDArray[np.uint8], KMeans]:
        """Apply K-means clustering to reduce colors in an image.

        Args:
            img_data: Image data as numpy array (height, width, 3) with RGB values
            width: Image width
            height: Image height
            settings: Settings with K-means parameters

        Returns:
            Tuple of (reduced image data, kmeans object)

        Example:
            >>> img_data = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
            >>> settings = Settings()
            >>> settings.kMeansNrOfClusters = 16
            >>> output, kmeans = ColorReducer.apply_kmeans_clustering(img_data, 100, 100, settings)
        """
        # OPTIMIZED: Use NumPy vectorization for color grouping
        bits_to_chop_off = 2  # Round r,g,b to every 4 values (0, 4, 8, ...)

        # Reduce bit depth for color grouping
        img_reduced = (img_data >> bits_to_chop_off) << bits_to_chop_off

        # Reshape to (height*width, 3) and find unique colors with counts
        pixels_flat = img_reduced.reshape(-1, 3)
        unique_colors, inverse_indices, counts = np.unique(
            pixels_flat, axis=0, return_inverse=True, return_counts=True
        )

        # Build pixel position lookup for each unique color
        # This is needed for updating the output image later
        points_by_color: Dict[Tuple[int, int, int], List[int]] = {}
        for i, color_idx in enumerate(inverse_indices):
            color_tuple = tuple(unique_colors[color_idx])
            if color_tuple not in points_by_color:
                points_by_color[color_tuple] = []
            points_by_color[color_tuple].append(i)

        # Build vectors for K-means
        total_pixels = width * height
        vectors: List[Vector] = []

        for color, count in zip(unique_colors, counts):
            r, g, b = int(color[0]), int(color[1]), int(color[2])

            # Convert to appropriate color space
            if settings.kMeansClusteringColorSpace == ClusteringColorSpace.RGB:
                data = [float(r), float(g), float(b)]
            elif settings.kMeansClusteringColorSpace == ClusteringColorSpace.HSL:
                hsl_result = rgb_to_hsl(r, g, b)
                data = [hsl_result[0], hsl_result[1], hsl_result[2]]  # h, s, l
            elif settings.kMeansClusteringColorSpace == ClusteringColorSpace.LAB:
                lab_result = rgb_to_lab(r, g, b)
                data = [lab_result[0], lab_result[1], lab_result[2]]  # l, a, b
            else:
                data = [float(r), float(g), float(b)]

            # Weight by frequency
            weight = float(count) / total_pixels

            vec = Vector(data, weight)
            vec.tag = (r, g, b)  # Store original RGB as tuple
            vectors.append(vec)

        # Run K-means
        random = Random(settings.randomSeed)
        kmeans = KMeans(vectors, settings.kMeansNrOfClusters, random)

        # Iterate until convergence
        kmeans.step()
        while kmeans.current_delta_distance_difference > settings.kMeansMinDeltaDifference:
            kmeans.step()

        # Update output image data
        output_data = ColorReducer._update_kmeans_output_image_data(
            kmeans,
            settings,
            points_by_color,
            img_data,
            width,
            height
        )

        return output_data, kmeans

    @staticmethod
    def _update_kmeans_output_image_data(
        kmeans: KMeans,
        settings: Settings,
        points_by_color: Dict[str, List[int]],
        img_data: NDArray[np.uint8],
        width: int,
        height: int
    ) -> NDArray[np.uint8]:
        """Update image data from K-means centroids.

        Args:
            kmeans: Trained K-means object
            settings: Settings
            points_by_color: Mapping of colors to pixel indices
            img_data: Original image data
            width: Image width
            height: Image height

        Returns:
            Updated image data with reduced colors
        """
        output_data = np.zeros((height, width, 3), dtype=np.uint8)

        for c in range(len(kmeans.centroids)):
            centroid = kmeans.centroids[c]

            # For each cluster
            for v in kmeans.points_per_category[c]:
                # Convert centroid back to RGB
                if settings.kMeansClusteringColorSpace == ClusteringColorSpace.RGB:
                    rgb = centroid.values
                elif settings.kMeansClusteringColorSpace == ClusteringColorSpace.HSL:
                    hsl_values = centroid.values
                    rgb_tuple = hsl_to_rgb(hsl_values[0], hsl_values[1], hsl_values[2])
                    rgb = [rgb_tuple[0], rgb_tuple[1], rgb_tuple[2]]  # r, g, b
                elif settings.kMeansClusteringColorSpace == ClusteringColorSpace.LAB:
                    lab_values = centroid.values
                    rgb_tuple = lab_to_rgb(lab_values[0], lab_values[1], lab_values[2])
                    rgb = [rgb_tuple[0], rgb_tuple[1], rgb_tuple[2]]  # r, g, b
                else:
                    rgb = centroid.values

                # Remove decimals
                rgb = [int(val) for val in rgb]

                # Get original color from vector tag (already a tuple)
                point_rgb = v.tag

                # Replace all pixels of the old color with new centroid color
                for pt in points_by_color[point_rgb]:
                    ptx = pt % width
                    pty = pt // width
                    output_data[pty, ptx, 0] = rgb[0]
                    output_data[pty, ptx, 1] = rgb[1]
                    output_data[pty, ptx, 2] = rgb[2]

        return output_data

    @staticmethod
    def build_color_distance_matrix(colors_by_index: List[RGB]) -> List[List[float]]:
        """Build a distance matrix for each color to each other.

        Uses Euclidean distance in RGB space.

        Args:
            colors_by_index: List of RGB colors

        Returns:
            2D matrix where [i][j] is distance from color i to color j

        Example:
            >>> colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
            >>> matrix = ColorReducer.build_color_distance_matrix(colors)
            >>> print(f"Distance red to green: {matrix[0][1]:.2f}")
        """
        n = len(colors_by_index)
        color_distances: List[List[float]] = [[0.0] * n for _ in range(n)]

        for j in range(n):
            for i in range(j, n):
                c1 = colors_by_index[j]
                c2 = colors_by_index[i]
                distance = ((c1[0] - c2[0]) ** 2 +
                           (c1[1] - c2[1]) ** 2 +
                           (c1[2] - c2[2]) ** 2) ** 0.5

                color_distances[i][j] = distance
                color_distances[j][i] = distance

        return color_distances

    @staticmethod
    def process_narrow_pixel_strip_cleanup(color_map_result: ColorMapResult) -> int:
        """Remove narrow pixel strips by merging with closest neighbor color.

        Finds single pixels that are isolated horizontally or vertically and
        replaces them with the closest neighboring color.

        Args:
            color_map_result: Color map result to process

        Returns:
            Number of pixels replaced

        Example:
            >>> result = ColorMapResult()
            >>> # ... populate result ...
            >>> count = ColorReducer.process_narrow_pixel_strip_cleanup(result)
            >>> print(f"{count} pixels replaced")
        """
        # OPTIMIZED: Build NumPy color distance matrix once
        n_colors = len(color_map_result.colorsByIndex)
        if n_colors == 0:
            return 0

        # Build vectorized color distance matrix using NumPy
        colors_array = np.asarray(color_map_result.colorsByIndex, dtype=np.float64)
        diff = colors_array[:, None, :] - colors_array[None, :, :]
        color_distances = np.sqrt(np.einsum('ijk,ijk->ij', diff, diff))

        count = 0
        img_color_indices = color_map_result.imgColorIndices

        for j in range(1, color_map_result.height - 1):
            for i in range(1, color_map_result.width - 1):
                top = img_color_indices.get(i, j - 1)
                bottom = img_color_indices.get(i, j + 1)
                left = img_color_indices.get(i - 1, j)
                right = img_color_indices.get(i + 1, j)
                cur = img_color_indices.get(i, j)

                if cur != top and cur != bottom and cur != left and cur != right:
                    # Single pixel - skip for now
                    pass
                elif cur != top and cur != bottom:
                    # Horizontally isolated
                    top_color_distance = color_distances[cur, top]
                    bottom_color_distance = color_distances[cur, bottom]
                    new_color = top if top_color_distance < bottom_color_distance else bottom
                    img_color_indices.set(i, j, new_color)
                    count += 1
                elif cur != left and cur != right:
                    # Vertically isolated
                    left_color_distance = color_distances[cur, left]
                    right_color_distance = color_distances[cur, right]
                    new_color = left if left_color_distance < right_color_distance else right
                    img_color_indices.set(i, j, new_color)
                    count += 1

        return count
