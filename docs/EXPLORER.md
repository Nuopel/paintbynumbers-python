# Paint-by-Numbers Explorer

The Explorer is a powerful tool for systematically testing different parameter combinations and finding the optimal settings for your specific images.

## Overview

Instead of manually adjusting parameters one at a time, the Explorer:
- Generates multiple variations with different parameter settings
- Collects quality metrics for each variation
- Creates an interactive HTML report for easy comparison
- Supports multiple exploration strategies (grid, star, random)

## Quick Start

### Using Presets (Easiest)

```bash
# Quick test with a few variations
paintbynumbers explore input.jpg --preset quick_test

# For detailed photos
paintbynumbers explore input.jpg --preset detailed_photos

# Compare color spaces
paintbynumbers explore input.jpg --preset color_space_comparison

# Explore cluster counts
paintbynumbers explore input.jpg --preset cluster_exploration
```

### Custom Configuration

```bash
# Create a configuration file
paintbynumbers init-explorer-config --output my-config.json --preset quick_test

# Edit my-config.json to customize parameters

# Run exploration
paintbynumbers explore input.jpg --config my-config.json
```

## Exploration Strategies

### Star Strategy (Default)

Varies **one parameter at a time** from a baseline configuration.

**Best for:**
- Understanding individual parameter effects
- Quick exploration
- When you have a good baseline configuration

**Example:**
```json
{
  "strategy": "star",
  "baseline": {
    "kMeansNrOfClusters": 16,
    "kMeansClusteringColorSpace": "RGB"
  },
  "vary": {
    "kMeansNrOfClusters": [8, 16, 24],
    "kMeansClusteringColorSpace": ["RGB", "LAB", "HSL"]
  }
}
```

**Generates:**
- 1 baseline (16 clusters, RGB)
- 2 cluster variations (8 clusters, 24 clusters - both with RGB)
- 2 color space variations (LAB, HSL - both with 16 clusters)
- **Total: 5 variations**

### Grid Strategy

Tests **all combinations** (Cartesian product).

**Best for:**
- Comprehensive testing
- Finding optimal combinations
- When parameter interactions are important

**Same configuration as above generates:**
- 8 clusters + RGB
- 8 clusters + LAB
- 8 clusters + HSL
- 16 clusters + RGB
- 16 clusters + LAB
- 16 clusters + HSL
- 24 clusters + RGB
- 24 clusters + LAB
- 24 clusters + HSL
- **Total: 9 variations**

**Warning:** Combinations grow exponentially (3 params × 5 values each = 125 variations)

### Random Strategy

Randomly samples from the parameter space.

**Best for:**
- Very large parameter spaces
- Initial exploration
- When grid search would generate too many variations

**Example:**
```json
{
  "strategy": "random",
  "random_samples": 20,
  "vary": {
    "kMeansNrOfClusters": [6, 8, 10, 12, 14, 16, 18, 20, 24, 28, 32],
    "kMeansClusteringColorSpace": ["RGB", "LAB", "HSL"],
    "removeFacetsSmallerThanNrOfPoints": [10, 15, 20, 25, 30, 40, 50]
  }
}
```

**Generates:** 20 random combinations (from 11 × 3 × 7 = 231 possible)

## Available Presets

### `quick_test`
Fast exploration for testing (star strategy, 3 variations)
- Varies: clusters (8, 16, 24), min facet size (10, 20)

### `detailed_photos`
Optimized for photographs (grid strategy, 9 variations)
- Uses LAB color space
- Varies: clusters (16, 24, 32), min facet size (20, 30, 40)

### `simple_illustrations`
For cartoons and simple graphics (grid strategy, 6 variations)
- Fewer colors, larger facets
- Varies: clusters (6, 8, 12), min facet size (50, 100)

### `color_space_comparison`
Compare RGB, LAB, and HSL (star strategy, 3 variations)
- Only varies color space

### `cluster_exploration`
Find optimal cluster count (star strategy, 7 variations)
- Varies: clusters (4, 8, 12, 16, 20, 24, 32)

## Parameters You Can Vary

### K-means Clustering
- `kMeansNrOfClusters` (int): Number of colors (default: 16)
- `kMeansClusteringColorSpace` (str): "RGB", "LAB", or "HSL"
- `kMeansMinDeltaDifference` (float): Convergence threshold

### Facet Processing
- `removeFacetsSmallerThanNrOfPoints` (int): Min facet size in pixels
- `removeFacetsFromLargeToSmall` (bool): Merge order
- `maximumNumberOfFacets` (int): Max facets (merges smallest)

### Border Smoothing
- `nrOfTimesToHalveBorderSegments` (int): Smoothing iterations (0-3)
- `narrowPixelStripCleanupRuns` (int): Cleanup passes

### Image Resizing
- `resizeImageWidth` (int): Target width
- `resizeImageHeight` (int): Target height

## Quality Metrics

The Explorer automatically collects these metrics for each variation:

### Basic Statistics
- **num_facets**: Total number of regions
- **num_colors**: Number of colors used
- **processing_time**: Time to generate (seconds)

### Facet Statistics
- **min/max/mean/median_facet_size**: Facet size distribution

### Color Metrics
- **color_diversity_score**: Color variety (0-1, higher = more diverse)
- **avg_color_saturation**: Average saturation (0-1)
- **avg_color_lightness**: Average brightness (0-1)

### Complexity Metrics
- **total_border_points**: Total border point count
- **avg_border_complexity**: Border points per facet
- **edge_density**: Border points / total pixels

## Interactive HTML Report

The generated report includes:

### Filter Controls
- Filter by facet count, color count, processing time
- Show only variations in specific ranges

### Sorting
- Sort by any metric (facets, colors, time, diversity, complexity)
- Ascending or descending order

### Comparison Mode
- Select up to 4 variations
- View side-by-side with highlighted differences
- Perfect for final decision making

### Image Preview
- Thumbnail grid for quick overview
- Click to zoom to full size
- Hover to see details

## Configuration File Format

```json
{
  "strategy": "star",
  "random_samples": 20,
  "baseline": {
    "kMeansNrOfClusters": 16,
    "kMeansClusteringColorSpace": "RGB",
    "removeFacetsSmallerThanNrOfPoints": 20
  },
  "vary": {
    "kMeansNrOfClusters": [8, 16, 24],
    "kMeansClusteringColorSpace": ["RGB", "LAB", "HSL"]
  },
  "fixed": {
    "randomSeed": 42
  },
  "output_dir": null,
  "save_intermediate": true,
  "parallel_processing": true,
  "max_workers": null,
  "warn_threshold": 50
}
```

## Command-Line Options

```bash
paintbynumbers explore [OPTIONS] INPUT_PATH

Options:
  -c, --config PATH       JSON configuration file
  --preset NAME           Use preset configuration
  -o, --output-dir PATH   Output directory
  --strategy [grid|star|random]  Override strategy
  --parallel / --sequential      Parallel processing (default: on)
  --workers N             Number of parallel workers
  --no-save               Skip intermediate outputs (faster, less disk)
  -q, --quiet             Suppress progress output
```

## Usage Examples

### Example 1: Find Best Cluster Count
```bash
paintbynumbers explore photo.jpg --preset cluster_exploration
```

### Example 2: Compare All Settings
```bash
paintbynumbers explore photo.jpg --preset detailed_photos --strategy grid
```

### Example 3: Fast Preview (No Intermediate Files)
```bash
paintbynumbers explore photo.jpg --preset quick_test --no-save
```

### Example 4: Custom Parameters
```json
// my-config.json
{
  "strategy": "star",
  "baseline": {
    "kMeansNrOfClusters": 20,
    "kMeansClusteringColorSpace": "LAB"
  },
  "vary": {
    "kMeansNrOfClusters": [16, 20, 24, 28],
    "removeFacetsSmallerThanNrOfPoints": [15, 20, 25, 30]
  }
}
```

```bash
paintbynumbers explore photo.jpg --config my-config.json
```

### Example 5: Batch Multiple Images
```bash
for img in images/*.jpg; do
    paintbynumbers explore "$img" --preset quick_test
done
```

## Progressive Workflow

For best results, use a progressive refinement approach:

### Step 1: Coarse Exploration
```bash
# Test wide range of cluster counts
paintbynumbers explore input.jpg --preset cluster_exploration
```

Review the HTML report and identify the best cluster count (e.g., 20 clusters).

### Step 2: Fine-Tuning
Create a custom config to explore around the best value:

```json
{
  "strategy": "grid",
  "vary": {
    "kMeansNrOfClusters": [18, 20, 22],
    "removeFacetsSmallerThanNrOfPoints": [15, 20, 25],
    "nrOfTimesToHalveBorderSegments": [1, 2, 3]
  }
}
```

### Step 3: Color Space Comparison
```bash
# Test different color spaces with your optimal settings
paintbynumbers explore input.jpg --preset color_space_comparison
```

### Step 4: Final Generation
Use the optimal parameters to generate the final output:

```bash
paintbynumbers generate input.jpg output --colors 20 --color-space LAB \
    --min-facet-size 20 --border-smoothing 2
```

## Performance Tips

### Speed Up Exploration
1. Use `--no-save` to skip intermediate files
2. Reduce image size with smaller `resizeImageWidth/Height`
3. Use `star` strategy instead of `grid`
4. Limit variations (fewer parameter values)
5. Use `--workers` to control parallelism

### Reduce Disk Usage
1. Use `--no-save` flag
2. Delete `variations/` subdirectory after reviewing HTML report
3. Only keep `report.html` and `results_summary.json`

### Parallel Processing
```bash
# Default: uses all CPU cores
paintbynumbers explore input.jpg --preset quick_test

# Limit to 4 workers (useful on shared machines)
paintbynumbers explore input.jpg --preset quick_test --workers 4

# Sequential processing (debugging)
paintbynumbers explore input.jpg --preset quick_test --sequential
```

## Programmatic Usage

```python
from pathlib import Path
from paintbynumbers.explorer import (
    ExplorerConfig,
    ExplorationEngine,
    HTMLReportGenerator,
    ExplorationStrategy,
)

# Create configuration
config = ExplorerConfig(
    strategy=ExplorationStrategy.STAR,
    baseline={"kMeansNrOfClusters": 16},
    vary={"kMeansNrOfClusters": [8, 12, 16, 20, 24]},
)

# Run exploration
engine = ExplorationEngine(
    config=config,
    input_image=Path("photo.jpg"),
)

results = engine.run()

# Generate report
report = HTMLReportGenerator(results, engine.output_dir)
report.generate(engine.output_dir / "report.html")

# Access results programmatically
for result in results:
    if result.success:
        print(f"{result.variation_id}: {result.metrics.num_facets} facets")
```

## Troubleshooting

### "Too many variations" warning
- Switch to `star` strategy
- Reduce number of values per parameter
- Use `random` strategy with sampling

### Out of memory
- Reduce `resizeImageWidth/Height`
- Use `--sequential` instead of parallel
- Reduce `--workers`

### Slow processing
- Enable `--parallel` (default)
- Use `--no-save` to skip file I/O
- Reduce image size
- Use fewer variations

### Missing PNG previews in report
- Install cairosvg: `pip install cairosvg`
- Or view SVG files directly from `variations/` directory

## Output Structure

```
results/
  image_name/
    2025-11-16_143022/           # Timestamp
      report.html                # Interactive HTML report
      results_summary.json       # All results data
      exploration_config.json    # Configuration used
      variations/                # Individual results
        var_001_clusters-8/
          output.svg
          preview.png
          metadata.json
        var_002_clusters-16/
          ...
```

## Tips for Different Image Types

### Photographs
- Use LAB color space (better perceptual accuracy)
- 16-32 clusters
- Smaller min facet size (15-25 pixels)

### Illustrations/Cartoons
- Use RGB color space
- 6-12 clusters
- Larger min facet size (50-100 pixels)

### Landscapes
- LAB color space
- 20-32 clusters
- Medium facet size (20-30 pixels)

### Portraits
- LAB color space
- 16-24 clusters
- Smaller facet size (15-20 pixels)
- More border smoothing (2-3 iterations)

## See Also

- [Main README](../README.md) - General usage
- [Examples](../examples/) - Code examples
- [API Documentation](API.md) - Detailed API reference
