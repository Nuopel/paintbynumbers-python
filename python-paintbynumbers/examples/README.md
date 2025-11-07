# Paint by Numbers Generator - Examples

This directory contains example scripts demonstrating how to use the Paint by Numbers Generator library.

## Files

### basic_usage.py

Comprehensive examples showing various usage patterns:

1. **Basic Usage** - Simple processing with default settings
2. **Custom Colors** - Adjusting color count and color space
3. **Output Profiles** - Customizing SVG appearance
4. **High Quality** - Settings for detailed, high-resolution output
5. **Progress Tracking** - Using progress callbacks
6. **Programmatic Access** - Working with results directly
7. **Configuration Files** - Loading and saving settings

## Running the Examples

1. Install the package:
   ```bash
   cd python-paintbynumbers
   pip install -e .
   ```

2. Place a test image in the examples directory:
   ```bash
   cd examples
   cp /path/to/your/image.jpg input.jpg
   ```

3. Edit `basic_usage.py` and uncomment the examples you want to run

4. Run the script:
   ```bash
   python basic_usage.py
   ```

## Using the CLI

Alternatively, you can use the command-line interface:

```bash
# Basic usage
paintbynumbers input.jpg output

# With options
paintbynumbers input.jpg output --colors 24 --png --jpg

# Create configuration file
paintbynumbers-config --output my-settings.json

# Use configuration file
paintbynumbers input.jpg output --config my-settings.json
```

See the main README for more CLI examples and options.
