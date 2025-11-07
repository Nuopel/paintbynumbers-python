# Python CLI Examples

## Installation

```bash
# Install from source
cd python-paintbynumbers
pip install -e .

# Or install from wheel
pip install paintbynumbers-1.0.0-py3-none-any.whl
```

## Basic Usage

### Simple command (like TypeScript CLI)

```bash
# Basic usage - input and output
python3 -m paintbynumbers -i input.jpg -o output

# Or using the installed CLI command
paint-by-numbers -i input.jpg -o output
```

This will create:
- `output.svg` - Vector paint-by-numbers
- `output_palette.json` - Color palette info

### Specify output format

```bash
# SVG only (default)
paint-by-numbers -i input.jpg -o output.svg

# PNG output
paint-by-numbers -i input.jpg -o output.png

# JPG output
paint-by-numbers -i input.jpg -o output.jpg

# All formats
paint-by-numbers -i input.jpg -o output --format all
```

### Quick color adjustment

```bash
# Use 24 colors instead of default 16
paint-by-numbers -i input.jpg -o output --colors 24

# Use 8 colors for simpler output
paint-by-numbers -i input.jpg -o output --colors 8
```

### Use settings JSON file

```bash
# Load all settings from JSON
paint-by-numbers -i input.jpg -o output -s my_settings.json

# Settings file overrides defaults
paint-by-numbers -i photo.png -o result -s precise_settings.json
```

### Control randomness (reproducibility)

```bash
# Use random seed for reproducible results
paint-by-numbers -i input.jpg -o output --seed 42

# Same seed = same output every time
paint-by-numbers -i input.jpg -o output --seed 12345
```

### Verbose output

```bash
# Show progress and details
paint-by-numbers -i input.jpg -o output --verbose

# Example output:
# [1/7] Loading image... ✓
# [2/7] Clustering colors (K-means)... 45% [=========>     ]
# [3/7] Removing narrow strips... ✓
# [4/7] Creating facets... 67% [============>  ]
# [5/7] Reducing facets... ✓
# [6/7] Tracing borders... 89% [===============> ]
# [7/7] Placing labels... ✓
#
# Output saved to: output.svg
# Processing time: 12.4s
```

---

## Settings JSON Format

### Example: `settings.json`

```json
{
  "kMeansNrOfClusters": 16,
  "kMeansMinDeltaDifference": 1.0,
  "kMeansClusteringColorSpace": "RGB",
  "removeFacetsSmallerThanNrOfPoints": 20,
  "removeFacetsFromLargeToSmall": true,
  "maximumNumberOfFacets": null,
  "narrowPixelStripCleanupRuns": 3,
  "nrOfTimesToHalveBorderSegments": 2,
  "resizeImageIfTooLarge": true,
  "resizeImageWidth": 1024,
  "resizeImageHeight": 1024,
  "randomSeed": 42
}
```

### Color Space Options

```json
{
  "kMeansClusteringColorSpace": "LAB"
}
```

Available: `"RGB"`, `"HSL"`, `"LAB"`
- **RGB**: Fast, good for most images
- **HSL**: Hue-based grouping
- **LAB**: Perceptually accurate (recommended for photos)

### Facet Control

```json
{
  "kMeansNrOfClusters": 12,
  "removeFacetsSmallerThanNrOfPoints": 50,
  "maximumNumberOfFacets": 200
}
```

- Fewer clusters = simpler output
- Larger min size = bigger regions
- Max facets = limit complexity

### Border Smoothing

```json
{
  "nrOfTimesToHalveBorderSegments": 3
}
```

- 0 = No smoothing (pixelated borders)
- 2 = Default (balanced)
- 3-4 = Very smooth (may lose detail)

### Color Restrictions (Advanced)

```json
{
  "kMeansNrOfClusters": 8,
  "kMeansColorRestrictions": [
    [255, 0, 0],
    [0, 255, 0],
    [0, 0, 255],
    [255, 255, 0],
    [255, 0, 255],
    [0, 255, 255],
    [255, 255, 255],
    [0, 0, 0]
  ],
  "colorAliases": {
    "255,0,0": "Red",
    "0,255,0": "Green",
    "0,0,255": "Blue",
    "255,255,0": "Yellow",
    "255,0,255": "Magenta",
    "0,255,255": "Cyan",
    "255,255,255": "White",
    "0,0,0": "Black"
  }
}
```

This forces specific colors (e.g., primary colors only).

---

## Output Profile JSON (Multiple Outputs)

### Example: `output_profiles.json`

```json
{
  "outputProfiles": [
    {
      "name": "full_labeled",
      "svgShowLabels": true,
      "svgShowBorders": true,
      "svgFillFacets": true,
      "svgSizeMultiplier": 3,
      "svgFontSize": 20,
      "svgFontColor": "#000000"
    },
    {
      "name": "outline_only",
      "svgShowLabels": false,
      "svgShowBorders": true,
      "svgFillFacets": false,
      "svgSizeMultiplier": 2
    },
    {
      "name": "preview_png",
      "filetype": "png",
      "svgShowLabels": true,
      "svgFillFacets": true,
      "svgSizeMultiplier": 2
    }
  ]
}
```

Usage:

```bash
paint-by-numbers -i input.jpg -o output -s settings.json --profile output_profiles.json
```

This generates:
- `output_full_labeled.svg`
- `output_outline_only.svg`
- `output_preview_png.png`

---

## Advanced Examples

### Batch Processing Script

**File: `batch_process.py`**

```python
#!/usr/bin/env python3
"""Batch process multiple images with different settings."""

from pathlib import Path
from paintbynumbers import Settings, process_image, save_svg
from PIL import Image
import json

def batch_process(input_dir: str, output_dir: str, settings_file: str):
    """Process all images in directory with given settings."""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Load settings
    with open(settings_file) as f:
        settings = Settings.from_json(json.load(f))

    # Process each image
    for image_file in input_path.glob("*.{jpg,png,jpeg}"):
        print(f"Processing {image_file.name}...")

        # Load image
        image = Image.open(image_file)

        # Process
        result = process_image(image, settings)

        # Save
        output_file = output_path / f"{image_file.stem}_pbn.svg"
        save_svg(result, output_file, settings)

        print(f"  → Saved to {output_file}")

if __name__ == "__main__":
    batch_process("./input_images", "./output", "settings.json")
```

Usage:

```bash
python3 batch_process.py
```

### Custom Processing Script

**File: `custom_process.py`**

```python
#!/usr/bin/env python3
"""Custom processing with settings from JSON."""

from paintbynumbers import Settings, process_image_from_file
import json
import sys

def main():
    # Load settings from JSON
    with open("settings.json") as f:
        config = json.load(f)

    settings = Settings(
        kMeansNrOfClusters=config.get("colors", 16),
        kMeansClusteringColorSpace=config.get("colorSpace", "RGB"),
        removeFacetsSmallerThanNrOfPoints=config.get("minFacetSize", 20),
        randomSeed=config.get("seed", 42),
        # ... more settings
    )

    # Process image
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    print(f"Processing {input_file}...")
    result = process_image_from_file(input_file, settings, verbose=True)

    # Save all formats
    result.save_svg(output_file.replace(".svg", ".svg"))
    result.save_png(output_file.replace(".svg", ".png"))
    result.save_palette_json(output_file.replace(".svg", "_palette.json"))

    print(f"Done! Outputs saved.")

if __name__ == "__main__":
    main()
```

**File: `settings.json`**

```json
{
  "colors": 20,
  "colorSpace": "LAB",
  "minFacetSize": 30,
  "seed": 12345,
  "smoothing": 2
}
```

Usage:

```bash
python3 custom_process.py input.jpg output.svg
```

---

## Output Files

### SVG Output (`output.svg`)

Vector format with:
- Numbered facets
- Smooth borders
- Color fills (optional)
- Scalable to any size

### Palette JSON (`output_palette.json`)

```json
{
  "width": 1024,
  "height": 768,
  "colors": [
    {
      "id": 1,
      "rgb": [34, 56, 78],
      "hex": "#22384e",
      "alias": "Dark Blue",
      "count": 15234,
      "area_percent": 19.4
    },
    {
      "id": 2,
      "rgb": [245, 220, 180],
      "hex": "#f5dcb4",
      "alias": "Beige",
      "count": 8721,
      "area_percent": 11.1
    }
  ],
  "total_pixels": 786432,
  "settings": {
    "clusters": 16,
    "color_space": "LAB",
    "seed": 42
  }
}
```

Use this to:
- Create paint color shopping list
- Analyze color distribution
- Track processing settings

---

## Environment Variables

```bash
# Control log level
export PAINTBYNUMBERS_LOG_LEVEL=DEBUG

# Disable progress bars
export PAINTBYNUMBERS_NO_PROGRESS=1

# Use specific number of threads
export PAINTBYNUMBERS_THREADS=4
```

---

## Comparison with TypeScript CLI

### TypeScript Command:

```bash
node dist/src-cli/main.js -i input.jpg -o output --config settings.json
```

### Python Equivalent:

```bash
paint-by-numbers -i input.jpg -o output -s settings.json
```

### Feature Parity

| Feature | TypeScript | Python |
|---------|-----------|--------|
| Input formats | ✓ PNG, JPG | ✓ PNG, JPG |
| Output SVG | ✓ | ✓ |
| Output PNG/JPG | ✓ | ✓ |
| Settings JSON | ✓ | ✓ |
| Color clustering | ✓ RGB/HSL/LAB | ✓ RGB/HSL/LAB |
| Facet reduction | ✓ | ✓ |
| Border smoothing | ✓ | ✓ |
| Label placement | ✓ | ✓ |
| Color restrictions | ✓ | ✓ |
| Random seed | ✓ | ✓ |
| Progress display | ✓ | ✓ |
| Output profiles | ✓ Multiple | ✓ Multiple |
| Palette JSON | ✓ | ✓ |

---

## Quick Start Checklist

1. **Install package**
   ```bash
   pip install -e .
   ```

2. **Create settings file** (optional)
   ```bash
   cp examples/settings_example.json my_settings.json
   ```

3. **Process first image**
   ```bash
   paint-by-numbers -i photo.jpg -o result.svg --verbose
   ```

4. **Adjust settings** as needed
   - Increase/decrease colors
   - Try different color space
   - Adjust facet sizes

5. **Generate production outputs**
   ```bash
   paint-by-numbers -i photo.jpg -o final -s my_settings.json --format all
   ```

---

## FAQ

**Q: Will output be identical to TypeScript version?**
A: Perceptually identical, but small numerical differences may exist due to floating-point precision differences between JavaScript and Python.

**Q: Which color space should I use?**
A:
- **LAB** for photos (perceptually accurate)
- **RGB** for graphics (fast, predictable)
- **HSL** for artistic control (hue-based)

**Q: How do I make simpler outputs?**
A:
- Reduce `kMeansNrOfClusters` (fewer colors)
- Increase `removeFacetsSmallerThanNrOfPoints` (larger facets)
- Set `maximumNumberOfFacets` limit

**Q: Can I use this in a Python script?**
A: Yes! See `examples/custom_process.py`

**Q: How do I reproduce exact results?**
A: Use `--seed` with a fixed number (e.g., `--seed 42`)

---

Ready to start? 🎨
