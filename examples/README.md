# Paint by Numbers Generator - Examples

This directory contains example scripts demonstrating various ways to use the Paint by Numbers Generator library.

## Getting Started

First, install the package:

```bash
cd python-paintbynumbers
pip install -e .
```

## Example Files

### 1. `simple_cli_usage.py` - Minimal Example (10 lines)

The simplest possible example - just process an image with default settings.

```bash
python examples/simple_cli_usage.py
```

**What it does:**
- Loads `input.jpg`
- Uses default settings (16 colors)
- Saves as `output.svg`

**Perfect for:** First-time users, quick tests

### 2. `basic_usage.py` - Comprehensive Examples

Seven complete examples showing different usage patterns:

1. **Basic Usage** - Default settings
2. **Custom Colors** - 24 colors with LAB color space
3. **Output Profiles** - Custom SVG appearance (outline only, no fill)
4. **High Quality** - 32 colors, detailed output
5. **Progress Tracking** - Real-time progress updates
6. **Programmatic Access** - Work with results directly
7. **Configuration Files** - Load/save settings

```bash
# Edit the file and uncomment the examples you want to run
python examples/basic_usage.py
```

**Perfect for:** Learning the API, understanding options

### 3. `custom_settings.py` - JSON Configuration

Demonstrates loading settings from a JSON file and generating multiple output formats.

```bash
python examples/custom_settings.py
```

**Requires:** `settings_example.json` (included)

**What it does:**
- Loads settings from JSON
- Processes image
- Generates SVG, PNG, and JPG outputs
- Shows progress

**Perfect for:** Production use, reproducible settings

### 4. `batch_process.py` - Batch Processing

Process multiple images with different settings for each.

```bash
python examples/batch_process.py
```

**What it does:**
- Processes 3 images with different settings:
  - Low detail (8 colors)
  - Medium detail (16 colors)
  - High detail (32 colors)
- Tracks overall progress
- Handles errors gracefully

**Perfect for:** Processing many images, automation

### 5. `settings_example.json` - Configuration Reference

Fully documented JSON settings file showing all available options with explanations.

**Use it as:**
- Template for your own settings
- Reference guide for all parameters
- Copy and customize

## Quick Examples

### CLI Usage

```bash
# Basic
paintbynumbers input.jpg output

# Custom colors
paintbynumbers input.jpg output --colors 24 --png

# From config file
paintbynumbers input.jpg output --config settings_example.json

# High quality
paintbynumbers input.jpg output \
  --colors 32 \
  --color-space LAB \
  --border-smoothing 3 \
  --scale 4.0
```

### Python API

#### Minimal Example
```python
from paintbynumbers.core.pipeline import PaintByNumbersPipeline
from paintbynumbers.core.settings import Settings

settings = Settings()
PaintByNumbersPipeline.process_and_save(
    'input.jpg', 'output', settings
)
```

#### With Custom Settings
```python
from paintbynumbers.core.settings import Settings, ClusteringColorSpace

settings = Settings()
settings.kMeansNrOfClusters = 24
settings.kMeansClusteringColorSpace = ClusteringColorSpace.LAB
settings.removeFacetsSmallerThanNrOfPoints = 15

PaintByNumbersPipeline.process_and_save(
    'input.jpg', 'output', settings, export_png=True
)
```

#### With Progress Callback
```python
def progress(stage, pct):
    print(f"\r{stage}: {int(pct*100)}%", end='')

result = PaintByNumbersPipeline.process(
    'input.jpg', settings, progress_callback=progress
)
```

## Common Use Cases

### 1. Quick Test

```bash
paintbynumbers test.jpg output --colors 8 --quiet
```

### 2. High Quality Print

```bash
paintbynumbers photo.jpg output \
  --colors 32 \
  --color-space LAB \
  --min-facet-size 10 \
  --border-smoothing 3 \
  --scale 5.0 \
  --png
```

### 3. Coloring Book Style

```bash
paintbynumbers drawing.jpg output \
  --colors 12 \
  --no-fill-facets \
  --show-labels \
  --show-borders
```

### 4. Reproducible Output

```bash
paintbynumbers photo.jpg output --seed 42
# Always produces same result with seed 42
```

### 5. Batch Convert Directory

```python
from pathlib import Path
from paintbynumbers.core.pipeline import PaintByNumbersPipeline
from paintbynumbers.core.settings import Settings

settings = Settings()
settings.kMeansNrOfClusters = 16

for img_path in Path('images/').glob('*.jpg'):
    out_path = f"output/{img_path.stem}"
    print(f"Processing {img_path}...")
    PaintByNumbersPipeline.process_and_save(
        str(img_path), out_path, settings
    )
```

## Tips & Tricks

### Choosing Number of Colors

- **4-8 colors**: Very simple, bold regions
- **12-16 colors**: Good balance (default: 16)
- **20-32 colors**: Detailed, complex images
- **32+ colors**: Very detailed, many small facets

### Color Spaces

- **RGB**: Fast, good for most images
- **HSL**: Better for images with varying brightness
- **LAB**: Best perceptual quality, slightly slower

### Performance Tuning

**Faster processing:**
```python
settings.kMeansNrOfClusters = 8  # Fewer colors
settings.narrowPixelStripCleanupRuns = 1  # Less cleanup
settings.nrOfTimesToHalveBorderSegments = 1  # Less smoothing
settings.resizeImageWidth = 512  # Smaller image
```

**Better quality:**
```python
settings.kMeansNrOfClusters = 32  # More colors
settings.removeFacetsSmallerThanNrOfPoints = 10  # Keep details
settings.nrOfTimesToHalveBorderSegments = 3  # Smoother borders
settings.kMeansClusteringColorSpace = ClusteringColorSpace.LAB
```

### Output Scaling

The `svgSizeMultiplier` affects file size and rendering:

- **1.0-2.0**: Small files, may look pixelated when zoomed
- **3.0**: Default, good balance
- **4.0-5.0**: Large files, crisp at any zoom level

### Memory Considerations

Large images consume more memory:

```python
# Automatically resize large images
settings.resizeImageIfTooLarge = True
settings.resizeImageWidth = 1024
settings.resizeImageHeight = 1024
```

## Troubleshooting

### ImportError: No module named 'paintbynumbers'

```bash
# Install in development mode
cd python-paintbynumbers
pip install -e .
```

### Command not found: paintbynumbers

```bash
# Reinstall with entry points
pip install -e .

# Or use Python module directly
python -m paintbynumbers.cli.main input.jpg output
```

### Image file not found

```bash
# Use absolute paths
paintbynumbers /full/path/to/input.jpg /full/path/to/output

# Or navigate to image directory
cd path/to/images
paintbynumbers input.jpg output
```

### PNG/JPG export fails

```bash
# Install cairosvg
pip install cairosvg

# On Ubuntu/Debian
sudo apt-get install libcairo2-dev

# On macOS
brew install cairo
```

### Out of memory

```bash
# Resize image first
paintbynumbers input.jpg output --max-width 800 --max-height 800

# Or reduce colors
paintbynumbers input.jpg output --colors 8
```

## Next Steps

1. **Try the examples** - Run each example script
2. **Customize settings** - Edit `settings_example.json`
3. **Read the API docs** - Check docstrings in source code
4. **Explore options** - Run `paintbynumbers --help`
5. **Check main README** - See `../README.md`

## Resources

- **Main Documentation**: `../README.md`
- **Migration Guide**: `../MIGRATION_NOTES.md`
- **API Reference**: Docstrings in `src/paintbynumbers/`
- **Tests**: `../tests/` for more examples

## Support

Having issues? Check:

1. This README for common solutions
2. Main README for installation help
3. GitHub issues for known problems
4. Source code docstrings for API details

---

**Happy painting! 🎨**
