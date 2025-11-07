# Paint by Numbers Generator (Python)

Python CLI implementation of the Paint by Numbers Generator - convert any image into a paint-by-numbers style image with numbered regions.

This is a Python port of the [TypeScript Paint by Numbers Generator](https://github.com/Nuopel/paintbynumbersgenerator) with perceptually identical output.

## Features

- 🎨 Convert any image to paint-by-numbers format
- 🔢 Smart K-means color clustering (RGB/HSL/LAB color spaces)
- 📐 Vector SVG output with smooth borders
- 🖼️ Raster PNG/JPG export
- ⚙️ Highly configurable via settings JSON
- 🎯 Optimal label placement using pole-of-inaccessibility algorithm
- 🔄 Reproducible results with random seed
- 📊 Color palette JSON export

## Installation

### From source

```bash
cd python-paintbynumbers
pip install -e .
```

### With development dependencies

```bash
pip install -e ".[dev]"
```

## Quick Start

### Basic usage

```bash
# Convert image to paint-by-numbers SVG
paint-by-numbers -i input.jpg -o output.svg

# With custom number of colors
paint-by-numbers -i input.jpg -o output.svg --colors 24

# Generate all formats (SVG, PNG, JPG, palette JSON)
paint-by-numbers -i input.jpg -o output --format all

# Show progress
paint-by-numbers -i input.jpg -o output.svg --verbose
```

### Using settings file

```bash
# Load settings from JSON
paint-by-numbers -i input.jpg -o output.svg -s settings.json

# Use random seed for reproducibility
paint-by-numbers -i input.jpg -o output.svg --seed 42
```

## Settings Configuration

Create a `settings.json` file to customize processing:

```json
{
  "kMeansNrOfClusters": 16,
  "kMeansClusteringColorSpace": "LAB",
  "removeFacetsSmallerThanNrOfPoints": 20,
  "nrOfTimesToHalveBorderSegments": 2,
  "randomSeed": 42
}
```

See [`example_settings.json`](../example_settings.json) for all available options.

## CLI Options

```
Options:
  -i, --input PATH        Input image file (required)
  -o, --output PATH       Output file path (required)
  -s, --settings PATH     Settings JSON file
  --colors INTEGER        Number of colors (default: 16)
  --format [svg|png|jpg|all]  Output format (default: svg)
  --seed INTEGER          Random seed for reproducibility
  --verbose              Show progress information
  --help                 Show this message and exit
```

## Python API

You can also use the package programmatically:

```python
from paintbynumbers import Settings, process_image_from_file
from paintbynumbers.core.settings import ClusteringColorSpace

# Create settings
settings = Settings(
    kMeansNrOfClusters=20,
    kMeansClusteringColorSpace=ClusteringColorSpace.LAB,
    randomSeed=42
)

# Process image
result = process_image_from_file("input.jpg", settings, verbose=True)

# Save outputs
result.save_svg("output.svg")
result.save_png("output.png")
result.save_palette_json("palette.json")
```

## Development

### Running tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=paintbynumbers

# Run specific test categories
pytest -m "not slow"  # Skip slow tests
pytest -m integration  # Only integration tests
```

### Type checking

```bash
mypy src/paintbynumbers
```

### Linting

```bash
ruff check src/paintbynumbers
```

### Running benchmarks

```bash
pytest tests/benchmarks/ --benchmark-only
```

## Algorithm Overview

The processing pipeline consists of 7 main stages:

1. **Color Quantization**: K-means clustering to reduce colors
2. **Strip Cleanup**: Remove narrow pixel strips
3. **Facet Creation**: Flood-fill to find color regions
4. **Facet Reduction**: Remove small regions, merge with neighbors
5. **Border Tracing**: Wall-following algorithm to trace boundaries
6. **Border Segmentation**: Haar wavelet smoothing
7. **Label Placement**: Find optimal label positions

## Project Structure

```
python-paintbynumbers/
├── src/paintbynumbers/
│   ├── cli/              # CLI application
│   ├── core/             # Core processing pipeline
│   ├── algorithms/       # K-means, flood fill, etc.
│   ├── structs/          # Data structures
│   ├── utils/            # Color conversion, I/O
│   └── output/           # SVG/PNG/JPG generation
├── tests/
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   ├── comparison/       # Comparison with TypeScript
│   └── benchmarks/       # Performance benchmarks
└── examples/             # Usage examples
```

## Requirements

- Python 3.11 or higher
- NumPy >= 1.24.0
- Pillow >= 10.0.0
- scikit-learn >= 1.3.0
- svgwrite >= 1.4.0
- click >= 8.1.0
- cairosvg >= 2.7.0
- tqdm >= 4.65.0

## Differences from TypeScript Version

- CLI-only (no web GUI)
- Perceptually identical output (small numerical differences due to floating-point precision)
- Python 3.11+ type hints instead of TypeScript types
- Uses NumPy arrays instead of TypedArrays

## License

MIT License - see LICENSE file

## Original Project

This is a Python port of the TypeScript project:
https://github.com/Nuopel/paintbynumbersgenerator

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Acknowledgments

- Original TypeScript implementation
- K-means clustering algorithm
- Polylabel algorithm for pole of inaccessibility
- Haar wavelet smoothing technique
