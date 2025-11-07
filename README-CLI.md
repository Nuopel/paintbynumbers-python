# Paint by Numbers Generator - CLI Usage

This document explains how to build and use the CLI version of the Paint by Numbers Generator.

## Prerequisites

- Node.js 20+ (recommended) or Node.js 16+
- System dependencies for canvas (on Linux):
  ```bash
  sudo apt-get install libcairo2-dev libjpeg-dev libpng-dev libgif-dev libpango1.0-dev
  ```

## Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Build the CLI:**
   ```bash
   npm run build
   ```

   This compiles the TypeScript files to JavaScript. The CLI requires the compiled JavaScript files to run.

   Alternatively, if you only want to build the CLI (not the web version):
   ```bash
   npm run build:cli
   ```

## Usage

After building, you can run the CLI from anywhere:

```bash
./paint-by-numbers-cli -i <input_image> -o <output_file> [-c <settings_json>]
```

### Parameters

- `-i <input_image>`: Path to the input image (required)
- `-o <output_file>`: Path to the output file (required)
- `-c <settings_json>`: Path to settings JSON file (optional, defaults to `./settings.json`)

### Examples

**Basic usage:**
```bash
./paint-by-numbers-cli -i input.png -o output.svg
```

**With custom settings:**
```bash
./paint-by-numbers-cli -i input.png -o output.svg -c my-settings.json
```

**Using absolute paths:**
```bash
/path/to/paintbynumbersgenerator/paint-by-numbers-cli -i /path/to/input.png -o /path/to/output.svg
```

## Configuration

Create a `settings.json` file to customize the output. See `src-cli/settings.json` for an example.

Key settings include:
- `nrOfColors`: Number of colors to reduce the image to
- `kMeansNrOfClusters`: Number of clusters for k-means
- `outputProfiles`: Array of output profiles with different settings
  - `name`: Profile name
  - `filetype`: "svg", "png", or "jpg"
  - `svgShowLabels`: Show color labels
  - `svgFillFacets`: Fill the facets with colors
  - `svgShowBorders`: Show borders between facets

## Output

The CLI generates multiple output files based on your output profiles:
- SVG files (vector graphics)
- PNG files (raster images)
- JPG files (raster images)
- JSON file with color palette information

## Troubleshooting

### Error: Cannot find module './src-cli/main.js'

This means you haven't built the project yet. Run:
```bash
npm run build
```

### Canvas installation errors

Make sure you have the system dependencies installed:
```bash
sudo apt-get install libcairo2-dev libjpeg-dev libpng-dev libgif-dev libpango1.0-dev
```

### Node version issues

This project requires Node.js 20 or higher. Check your version:
```bash
node --version
```

If you're using an older version, consider using nvm to install a newer version.
