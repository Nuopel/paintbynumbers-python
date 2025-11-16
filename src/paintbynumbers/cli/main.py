"""Command-line interface for Paint by Numbers Generator.

This module provides the main CLI for processing images into paint-by-numbers artwork.
"""

from __future__ import annotations
import sys
import json
from pathlib import Path
from typing import Optional

try:
    import click
    CLICK_AVAILABLE = True
except ImportError:
    CLICK_AVAILABLE = False

from paintbynumbers.core.pipeline import PaintByNumbersPipeline
from paintbynumbers.core.settings import Settings, ClusteringColorSpace


def _progress_callback(stage: str, progress: float) -> None:
    """Display progress updates."""
    bar_width = 30
    filled = int(bar_width * progress)
    bar = "█" * filled + "░" * (bar_width - filled)
    percent = int(progress * 100)
    click.echo(f"\r{stage:.<30} [{bar}] {percent}%", nl=(progress >= 1.0))


@click.command()
@click.argument('input_path', type=click.Path(exists=True))
@click.argument('output_path', type=click.Path())
@click.option(
    '--config', '-c',
    type=click.Path(exists=True),
    help='Path to JSON configuration file'
)
@click.option(
    '--colors', '-n',
    type=int,
    help='Number of colors (K-means clusters)'
)
@click.option(
    '--color-space',
    type=click.Choice(['RGB', 'HSL', 'LAB'], case_sensitive=False),
    help='Color space for K-means clustering'
)
@click.option(
    '--max-width',
    type=int,
    help='Maximum image width (will resize if larger)'
)
@click.option(
    '--max-height',
    type=int,
    help='Maximum image height (will resize if larger)'
)
@click.option(
    '--min-facet-size',
    type=int,
    help='Minimum facet size in pixels (smaller facets will be merged)'
)
@click.option(
    '--max-facets',
    type=int,
    help='Maximum number of facets (will merge smallest if exceeded)'
)
@click.option(
    '--border-smoothing',
    type=int,
    help='Number of times to halve border segments for smoothing (0-3)'
)
@click.option(
    '--svg/--no-svg',
    default=True,
    help='Generate SVG output (default: enabled)'
)
@click.option(
    '--png',
    is_flag=True,
    help='Also generate PNG output'
)
@click.option(
    '--jpg',
    is_flag=True,
    help='Also generate JPG output'
)
@click.option(
    '--show-labels/--no-show-labels',
    default=True,
    help='Show color labels in output (default: enabled)'
)
@click.option(
    '--show-borders/--no-show-borders',
    default=True,
    help='Show borders in output (default: enabled)'
)
@click.option(
    '--fill-facets/--no-fill-facets',
    default=True,
    help='Fill facets with colors (default: enabled)'
)
@click.option(
    '--scale',
    type=float,
    default=3.0,
    help='Output scale multiplier (default: 3.0)'
)
@click.option(
    '--font-size',
    type=int,
    default=20,
    help='Label font size (default: 20)'
)
@click.option(
    '--font-color',
    default='#000000',
    help='Label font color (default: #000000)'
)
@click.option(
    '--border-width',
    type=float,
    default=1.0,
    help='Border/stroke width in SVG (default: 1.0)'
)
@click.option(
    '--seed',
    type=int,
    help='Random seed for reproducibility'
)
@click.option(
    '--quiet', '-q',
    is_flag=True,
    help='Suppress progress output'
)
@click.option(
    '--save-config',
    type=click.Path(),
    help='Save configuration to JSON file'
)
def main(
    input_path: str,
    output_path: str,
    config: Optional[str],
    colors: Optional[int],
    color_space: Optional[str],
    max_width: Optional[int],
    max_height: Optional[int],
    min_facet_size: Optional[int],
    max_facets: Optional[int],
    border_smoothing: Optional[int],
    svg: bool,
    png: bool,
    jpg: bool,
    show_labels: bool,
    show_borders: bool,
    fill_facets: bool,
    scale: float,
    font_size: int,
    font_color: str,
    border_width: float,
    seed: Optional[int],
    quiet: bool,
    save_config: Optional[str]
) -> None:
    """Generate paint-by-numbers artwork from an image.

    INPUT_PATH: Path to input image file

    OUTPUT_PATH: Base path for output files (without extension)

    Examples:

      \b
      # Basic usage - generate SVG with default settings
      $ paintbynumbers input.jpg output

      \b
      # Generate SVG and PNG with 24 colors
      $ paintbynumbers input.jpg output --colors 24 --png

      \b
      # Use custom configuration file
      $ paintbynumbers input.jpg output --config settings.json

      \b
      # Adjust output appearance
      $ paintbynumbers input.jpg output --colors 16 --scale 4.0 --font-size 24

      \b
      # Save configuration for later reuse
      $ paintbynumbers input.jpg output --colors 20 --save-config my-settings.json
    """
    if not CLICK_AVAILABLE:
        click.echo("Error: Click is required for the CLI. Install with: pip install click")
        sys.exit(1)

    try:
        # Load or create settings
        if config:
            with open(config, 'r') as f:
                config_data = json.load(f)
            settings = Settings.from_json(config_data)
            if not quiet:
                click.echo(f"Loaded configuration from {config}")
        else:
            settings = Settings()

        # Override with command-line options
        if colors is not None:
            settings.kMeansNrOfClusters = colors
        if color_space is not None:
            settings.kMeansClusteringColorSpace = ClusteringColorSpace(color_space.upper())
        if max_width is not None:
            settings.resizeImageWidth = max_width
            settings.resizeImageIfTooLarge = True
        if max_height is not None:
            settings.resizeImageHeight = max_height
            settings.resizeImageIfTooLarge = True
        if min_facet_size is not None:
            settings.removeFacetsSmallerThanNrOfPoints = min_facet_size
        if max_facets is not None:
            settings.maximumNumberOfFacets = max_facets
        if border_smoothing is not None:
            settings.nrOfTimesToHalveBorderSegments = border_smoothing
        if seed is not None:
            settings.randomSeed = seed

        # Update output profile
        from paintbynumbers.core.settings import OutputProfile
        profile = OutputProfile(
            name="cli_output",
            filetype="svg",
            svgShowLabels=show_labels,
            svgShowBorders=show_borders,
            svgFillFacets=fill_facets,
            svgSizeMultiplier=scale,
            svgFontSize=font_size,
            svgFontColor=font_color,
            svgBorderWidth=border_width
        )
        settings.outputProfiles = [profile]

        # Save configuration if requested
        if save_config:
            with open(save_config, 'w') as f:
                json.dump(settings.to_json(), f, indent=2)
            if not quiet:
                click.echo(f"Configuration saved to {save_config}")

        # Display processing info
        if not quiet:
            click.echo(f"\nProcessing: {input_path}")
            click.echo(f"Output: {output_path}")
            click.echo(f"Colors: {settings.kMeansNrOfClusters}")
            click.echo(f"Color space: {settings.kMeansClusteringColorSpace.value}")
            click.echo("")

        # Process the image
        progress = _progress_callback if not quiet else None
        PaintByNumbersPipeline.process_and_save(
            input_path=input_path,
            output_path=output_path,
            settings=settings,
            export_png=png,
            export_jpg=jpg,
            progress_callback=progress
        )

        if not quiet:
            click.echo("\n")
            outputs = []
            if svg:
                outputs.append(f"{output_path}.svg")
            if png:
                outputs.append(f"{output_path}.png")
            if jpg:
                outputs.append(f"{output_path}.jpg")
            click.echo(f"✓ Successfully generated: {', '.join(outputs)}")

    except KeyboardInterrupt:
        click.echo("\n\nProcessing interrupted by user.", err=True)
        sys.exit(130)
    except Exception as e:
        click.echo(f"\nError: {e}", err=True)
        if not quiet:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@click.command()
@click.option(
    '--output', '-o',
    type=click.Path(),
    default='settings.json',
    help='Output file path (default: settings.json)'
)
def init_config(output: str) -> None:
    """Create a default configuration file.

    This generates a JSON configuration file with all default settings
    that can be customized and used with the --config option.

    Example:

      \b
      $ paintbynumbers-config --output my-settings.json
      $ paintbynumbers input.jpg output --config my-settings.json
    """
    if not CLICK_AVAILABLE:
        click.echo("Error: Click is required. Install with: pip install click")
        sys.exit(1)

    try:
        settings = Settings()
        with open(output, 'w') as f:
            json.dump(settings.to_json(), f, indent=2)
        click.echo(f"✓ Configuration file created: {output}")
        click.echo("\nEdit this file to customize settings, then use it with:")
        click.echo(f"  paintbynumbers input.jpg output --config {output}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@click.group()
def cli_group():
    """Paint by Numbers Generator CLI tools."""
    pass


cli_group.add_command(main, 'generate')
cli_group.add_command(init_config, 'init-config')


if __name__ == '__main__':
    main()
