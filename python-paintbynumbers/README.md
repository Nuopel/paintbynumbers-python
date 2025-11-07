# Paint by Numbers Generator (Python)

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Test Coverage](https://img.shields.io/badge/coverage-92%25-brightgreen.svg)](https://github.com/Nuopel/paintbynumbersgenerator)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Python CLI implementation of the Paint by Numbers Generator - convert any image into a paint-by-numbers style artwork with numbered regions.

This is a Python port of the [TypeScript Paint by Numbers Generator](https://github.com/Nuopel/paintbynumbersgenerator) with functionally identical output.

![Example Output](https://via.placeholder.com/800x300.png?text=Paint+by+Numbers+Example)

## ✨ Features

- 🎨 **Smart Color Reduction**: K-means clustering in RGB/HSL/LAB color spaces
- 🖼️ **Multiple Output Formats**: SVG (vector), PNG, JPG (raster)
- 📐 **Smooth Borders**: Haar wavelet smoothing for clean edges
- 🎯 **Optimal Label Placement**: Pole-of-inaccessibility algorithm
- ⚙️ **Highly Configurable**: JSON settings for all parameters
- 🔄 **Reproducible**: Random seed support
- 🚀 **Fast**: Optimized NumPy operations
- ✅ **Well Tested**: 92% test coverage, 420+ tests

## 🚀 Quick Start

### Installation

```bash
# From source
cd python-paintbynumbers
pip install -e .
```

### Basic Usage (CLI)

```bash
# Simple conversion
paintbynumbers input.jpg output

# With 24 colors
paintbynumbers input.jpg output --colors 24

# Generate PNG and JPG too
paintbynumbers input.jpg output --png --jpg

# Show progress
paintbynumbers input.jpg output --colors 16
```

### Basic Usage (Python API)

```python
from paintbynumbers.core.pipeline import PaintByNumbersPipeline
from paintbynumbers.core.settings import Settings

# Create default settings
settings = Settings()

# Process image
PaintByNumbersPipeline.process_and_save(
    input_path='input.jpg',
    output_path='output',
    settings=settings,
    export_png=True
)
```

## 📖 Documentation

### CLI Commands

**Main Command**: `paintbynumbers`

```bash
paintbynumbers INPUT OUTPUT [OPTIONS]
```

**Options:**

```
Required Arguments:
  INPUT                   Path to input image file
  OUTPUT                  Base path for output files (without extension)

Color Settings:
  --colors, -n INTEGER    Number of colors (default: 16)
  --color-space [RGB|HSL|LAB]  Color space for clustering
  --seed INTEGER          Random seed for reproducibility

Image Processing:
  --max-width INTEGER     Maximum image width
  --max-height INTEGER    Maximum image height
  --min-facet-size INTEGER  Minimum facet size in pixels
  --max-facets INTEGER    Maximum number of facets
  --border-smoothing INTEGER  Border smoothing iterations (0-3)

Output Options:
  --svg / --no-svg        Generate SVG (default: enabled)
  --png                   Also generate PNG
  --jpg                   Also generate JPG
  --show-labels / --no-show-labels  Show numbered labels
  --show-borders / --no-show-borders  Show borders
  --fill-facets / --no-fill-facets  Fill facets with colors
  --scale FLOAT           Output scale multiplier (default: 3.0)
  --font-size INTEGER     Label font size (default: 20)
  --font-color TEXT       Label color (default: #000000)

Configuration:
  --config, -c PATH       Load settings from JSON file
  --save-config PATH      Save configuration to JSON file
  --quiet, -q             Suppress progress output

Other:
  --help                  Show help message
```

**Configuration Command**: `paintbynumbers-config`

```bash
# Create a default configuration file
paintbynumbers-config --output my-settings.json
```

### Examples

#### Simple Conversion
```bash
paintbynumbers photo.jpg output
# Creates: output.svg
```

#### Custom Colors and Format
```bash
paintbynumbers photo.jpg output --colors 32 --png --jpg
# Creates: output.svg, output.png, output.jpg
```

#### Using Configuration File
```bash
# Create config
paintbynumbers-config --output settings.json

# Use config
paintbynumbers photo.jpg output --config settings.json
```

#### Reproducible Results
```bash
paintbynumbers photo.jpg output --seed 42
# Same seed = identical output
```

#### High Quality Output
```bash
paintbynumbers photo.jpg output \
  --colors 32 \
  --color-space LAB \
  --min-facet-size 10 \
  --border-smoothing 3 \
  --scale 4.0 \
  --png
```

#### Outline Only (Coloring Book Style)
```bash
paintbynumbers photo.jpg output \
  --no-fill-facets \
  --show-labels \
  --show-borders
```

### Python API

#### Basic Processing

```python
from paintbynumbers.core.pipeline import PaintByNumbersPipeline
from paintbynumbers.core.settings import Settings

# Default settings
settings = Settings()

# Process and save
PaintByNumbersPipeline.process_and_save(
    input_path='input.jpg',
    output_path='output',
    settings=settings,
    export_png=True,
    export_jpg=True
)
```

#### Custom Settings

```python
from paintbynumbers.core.settings import Settings, ClusteringColorSpace

settings = Settings()
settings.kMeansNrOfClusters = 24
settings.kMeansClusteringColorSpace = ClusteringColorSpace.LAB
settings.removeFacetsSmallerThanNrOfPoints = 15
settings.nrOfTimesToHalveBorderSegments = 3
settings.randomSeed = 42

PaintByNumbersPipeline.process_and_save(
    input_path='input.jpg',
    output_path='output',
    settings=settings
)
```

#### Programmatic Result Access

```python
# Get results without saving
result = PaintByNumbersPipeline.process(
    input_path='input.jpg',
    settings=settings
)

# Access results
print(f"Image: {result.width}x{result.height}")
print(f"Colors: {len(result.colors_by_index)}")
print(f"Facets: {len([f for f in result.facet_result.facets if f])}")

# Save manually
with open('output.svg', 'w') as f:
    f.write(result.svg_content)
```

#### Progress Callbacks

```python
def progress_callback(stage: str, progress: float):
    print(f"{stage}: {int(progress*100)}%")

result = PaintByNumbersPipeline.process(
    input_path='input.jpg',
    settings=settings,
    progress_callback=progress_callback
)
```

#### Configuration Files

```python
import json
from paintbynumbers.core.settings import Settings

# Save configuration
settings = Settings()
settings.kMeansNrOfClusters = 20

with open('config.json', 'w') as f:
    json.dump(settings.to_json(), f, indent=2)

# Load configuration
with open('config.json', 'r') as f:
    config_data = json.load(f)

settings = Settings.from_json(config_data)
```

### Settings Reference

See `examples/settings_example.json` for a fully documented settings file with all available options.

**Key Settings:**

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `kMeansNrOfClusters` | int | 16 | Number of colors (4-64 recommended) |
| `kMeansClusteringColorSpace` | str | "RGB" | Color space: RGB, HSL, or LAB |
| `removeFacetsSmallerThanNrOfPoints` | int | 20 | Min facet size in pixels |
| `maximumNumberOfFacets` | int\|null | null | Hard limit on facet count |
| `narrowPixelStripCleanupRuns` | int | 3 | Strip cleanup passes (0-5) |
| `nrOfTimesToHalveBorderSegments` | int | 2 | Smoothing iterations (0-3) |
| `resizeImageWidth` | int | 1024 | Max width when resizing |
| `resizeImageHeight` | int | 1024 | Max height when resizing |
| `randomSeed` | int\|null | null | Random seed for reproducibility |

### Examples Directory

The `examples/` directory contains:

- `simple_cli_usage.py` - Minimal 10-line example
- `basic_usage.py` - 7 comprehensive usage examples
- `custom_settings.py` - Using JSON configuration files
- `batch_process.py` - Processing multiple images
- `settings_example.json` - Fully documented settings file

## 🏗️ Architecture

### Processing Pipeline

The pipeline consists of 11 stages:

1. **Image Loading** - Load and optionally resize image
2. **K-means Clustering** - Reduce colors using k-means
3. **Color Map Creation** - Assign pixels to color indices
4. **Strip Cleanup** - Remove narrow pixel strips
5. **Facet Building** - Find connected color regions (flood fill)
6. **Neighbor Building** - Build facet adjacency relationships
7. **Facet Reduction** - Merge small/similar facets
8. **Border Tracing** - Trace facet boundaries (wall-following)
9. **Border Segmentation** - Smooth borders (Haar wavelets)
10. **Label Placement** - Find optimal label positions (polylabel)
11. **SVG Generation** - Generate final SVG with Bezier curves

### Project Structure

```
python-paintbynumbers/
├── src/paintbynumbers/
│   ├── algorithms/          # Core algorithms
│   │   ├── kmeans.py       # K-means clustering
│   │   ├── flood_fill.py   # Flood fill algorithm
│   │   ├── polylabel.py    # Label placement
│   │   └── vector.py       # Vector math
│   ├── cli/                # CLI application
│   │   └── main.py         # Click-based CLI
│   ├── core/               # Core processing
│   │   ├── pipeline.py     # Main pipeline
│   │   ├── settings.py     # Configuration
│   │   └── types.py        # Type definitions
│   ├── processing/         # Processing modules
│   │   ├── colorreduction.py
│   │   ├── facetbuilder.py
│   │   ├── facetreduction.py
│   │   ├── facetbordertracer.py
│   │   ├── facetbordersegmenter.py
│   │   └── facetlabelplacer.py
│   ├── output/             # Output generation
│   │   ├── svgbuilder.py   # SVG generation
│   │   └── rasterexport.py # PNG/JPG export
│   ├── structs/            # Data structures
│   └── utils/              # Utilities
├── tests/
│   ├── unit/               # 370+ unit tests
│   ├── integration/        # End-to-end tests
│   ├── benchmarks/         # Performance tests
│   └── ...
└── examples/               # Usage examples
```

## 🧪 Development

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=paintbynumbers --cov-report=html

# Specific test categories
pytest tests/unit/              # Unit tests only
pytest tests/integration/       # Integration tests only
pytest tests/benchmarks/        # Performance benchmarks

# Ignore slow tests
pytest --ignore=tests/benchmarks
```

### Code Quality

```bash
# Type checking
mypy src/paintbynumbers

# Linting
ruff check src/paintbynumbers

# Format code
ruff format src/paintbynumbers
```

### Benchmarks

```bash
# Run performance benchmarks
pytest tests/benchmarks/ --benchmark-only

# Compare with previous results
pytest tests/benchmarks/ --benchmark-compare
```

## 📋 Requirements

- **Python**: 3.11 or higher
- **Core Dependencies**:
  - `numpy>=1.24.0` - Array operations
  - `Pillow>=10.0.0` - Image I/O
  - `scikit-learn>=1.3.0` - K-means clustering
  - `svgwrite>=1.4.0` - SVG generation
  - `click>=8.1.0` - CLI framework
- **Optional**:
  - `cairosvg>=2.7.0` - PNG/JPG export (preferred)
  - Falls back to Pillow if unavailable

## 🔄 Migration from TypeScript

See [MIGRATION_NOTES.md](MIGRATION_NOTES.md) for:
- API differences
- Known limitations
- Performance comparison
- Python-specific considerations

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass (`pytest`)
5. Maintain 90%+ coverage
6. Submit a pull request

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

- Original [TypeScript implementation](https://github.com/Nuopel/paintbynumbersgenerator)
- K-means clustering algorithm
- [Polylabel](https://github.com/mapbox/polylabel) algorithm by Mapbox
- Haar wavelet smoothing technique

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Nuopel/paintbynumbersgenerator/issues)
- **Documentation**: This README + docstrings in code
- **Examples**: See `examples/` directory

---

**Made with ❤️ using Python** | [TypeScript Version](https://github.com/Nuopel/paintbynumbersgenerator)
