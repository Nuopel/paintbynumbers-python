# Paint by Numbers Generator - Python Migration WBS

## Project Overview
**Objective**: Create a functionally identical Python CLI version of the TypeScript paint-by-numbers generator
**Target**: Python 3.11+
**Scope**: CLI application with perceptually identical output to TypeScript version

---

## Work Breakdown Structure

### PHASE 1: Project Foundation & Setup (2-3 hours)
**Goal**: Establish Python project structure and development environment

#### 1.1 Project Structure Setup
- [ ] Create Python package structure:
  ```
  python-paintbynumbers/
  ├── src/
  │   └── paintbynumbers/
  │       ├── __init__.py
  │       ├── cli/
  │       ├── core/
  │       ├── algorithms/
  │       ├── structs/
  │       └── utils/
  ├── tests/
  ├── examples/
  ├── pyproject.toml
  ├── setup.cfg
  ├── README.md
  └── .gitignore
  ```
- [ ] Create `pyproject.toml` with dependencies
- [ ] Create `setup.cfg` for package metadata
- [ ] Add `.gitignore` for Python
- [ ] Create `requirements.txt` and `requirements-dev.txt`

#### 1.2 Development Environment
- [ ] Set up pytest configuration
- [ ] Set up mypy for type checking
- [ ] Configure ruff/pylint for linting
- [ ] Create basic CI/CD workflow (optional)

#### 1.3 Dependencies Installation
**Runtime Dependencies**:
- `numpy>=1.24.0` - Array operations
- `Pillow>=10.0.0` - Image processing
- `scikit-learn>=1.3.0` - K-means (or custom implementation)
- `svgwrite>=1.4.0` - SVG generation
- `click>=8.1.0` - CLI framework
- `cairosvg>=2.7.0` - SVG to PNG/JPG conversion

**Dev Dependencies**:
- `pytest>=7.4.0`
- `pytest-cov>=4.1.0`
- `pytest-benchmark>=4.0.0`
- `mypy>=1.5.0`
- `ruff>=0.1.0`

**Deliverable**: Working Python project skeleton with dependencies installed

---

### PHASE 2: Core Data Structures (3-4 hours)
**Goal**: Build foundational classes that other components depend on
**Validation**: Unit tests for each class

#### 2.1 Basic Structures (`src/paintbynumbers/structs/`)
- [ ] **2.1.1**: `point.py` - Point class
  - Properties: `x`, `y`
  - Methods: `__eq__`, `__hash__`, `__repr__`
  - Test: Create, compare, hash points

- [ ] **2.1.2**: `boundingbox.py` - BoundingBox class
  - Properties: `minX`, `minY`, `maxX`, `maxY`
  - Methods: `width`, `height`, `contains()`, `expand()`
  - Test: Containment, expansion

- [ ] **2.1.3**: `typed_arrays.py` - NumPy 2D array wrappers
  - Classes: `Uint8Array2D`, `Uint32Array2D`, `BooleanArray2D`
  - Methods: `get()`, `set()`, `shape`, indexing
  - Purpose: Match TypeScript TypedArray API
  - Test: Array operations, bounds checking

#### 2.2 Core Types (`src/paintbynumbers/core/types.py`)
- [ ] **2.2.1**: Type definitions
  - `RGB` (NamedTuple or dataclass)
  - `ColorSpace` enum (RGB, HSL, LAB)
  - `OrientationEnum` for border tracing
  - `IMap` generic type hint

- [ ] **2.2.2**: Common utilities (`common.py`)
  - `delay()` function (async sleep)
  - `CancellationToken` class
  - Progress callback types

**Deliverable**: Tested data structure classes matching TypeScript API

---

### PHASE 3: Core Algorithms (Independent) (8-10 hours)
**Goal**: Port standalone algorithms with no dependencies on pipeline
**Validation**: Unit tests comparing outputs with TypeScript test cases

#### 3.1 Color Utilities (`src/paintbynumbers/utils/color.py`)
- [ ] **3.1.1**: `Color` class
  - RGB/HSL/LAB conversion methods
  - Distance calculation
  - Test: Match TypeScript conversions (tolerance: 1e-6)

- [ ] **3.1.2**: Color conversion functions
  - `rgb_to_hsl()`, `hsl_to_rgb()`
  - `rgb_to_lab()`, `lab_to_rgb()`
  - Test against TypeScript `colorconversion.test.ts`

#### 3.2 K-means Clustering (`src/paintbynumbers/algorithms/clustering.py`)
- [ ] **3.2.1**: `Vector` class
  - Properties: `values`, `weight`
  - Methods: `distance()`, `weighted_average()`
  - Test: Vector math operations

- [ ] **3.2.2**: `KMeans` class
  - Lloyd's algorithm with weighted vectors
  - Support for RGB/HSL/LAB color spaces
  - Seeded random initialization
  - Convergence detection
  - Test: Compare clusters with TypeScript (same seed)

**Critical Validation**: Run clustering on test image, compare cluster centers (tolerance: 5%)

#### 3.3 Flood Fill Algorithm (`src/paintbynumbers/algorithms/flood_fill.py`)
- [ ] **3.3.1**: Stack-based flood fill
  - 4-connectivity
  - Return list of points
  - Callback version for memory efficiency
  - Test: Match TypeScript output exactly

#### 3.4 Pole of Inaccessibility (`src/paintbynumbers/algorithms/polylabel.py`)
- [ ] **3.4.1**: Port polylabel algorithm
  - Grid-based optimization
  - Find largest inscribed circle in polygon
  - Handle polygon with holes
  - Test: Compare label positions (tolerance: 2 pixels)

#### 3.5 Utility Functions
- [ ] **3.5.1**: `boundary_utils.py`
  - `get_neighbors_4()` - 4-connected neighbors
  - `get_neighbors_8()` - 8-connected neighbors
  - `is_in_bounds()` - Bounds checking
  - Test: Edge cases, corner cases

- [ ] **3.5.2**: `random.py`
  - Seeded PRNG wrapper (use `random.Random()`)
  - Ensure deterministic behavior
  - Test: Same seed → same sequence

**Deliverable**: All core algorithms tested and validated against TypeScript

---

### PHASE 4: Configuration & Settings (2-3 hours)
**Goal**: Port settings system and constants

#### 4.1 Constants (`src/paintbynumbers/core/constants.py`)
- [ ] **4.1.1**: Port all constants from TypeScript
  - `CLUSTERING_DEFAULTS`
  - `FACET_THRESHOLDS`
  - `SEGMENTATION_CONSTANTS`
  - `IMAGE_CONSTANTS`
  - `SVG_CONSTANTS`
  - Test: Validate constant types

#### 4.2 Settings Class (`src/paintbynumbers/core/settings.py`)
- [ ] **4.2.1**: `Settings` dataclass
  - All 15+ configuration options
  - Type hints for all fields
  - Default values from constants
  - Validation methods

- [ ] **4.2.2**: JSON serialization/deserialization
  - `from_json()` class method
  - `to_json()` instance method
  - Handle color restrictions, aliases
  - Test: Load/save settings JSON

- [ ] **4.2.3**: Output profile configuration
  - `OutputProfile` dataclass
  - Support SVG/PNG/JPG options
  - Test: Profile validation

**Deliverable**: Settings system with JSON I/O

---

### PHASE 5: Processing Pipeline - Part A (10-12 hours)
**Goal**: Core processing components

#### 5.1 Facet Data Structures (`src/paintbynumbers/core/facet.py`)
- [ ] **5.1.1**: `PathPoint` class
  - Properties: `point`, `orientation`
  - Test: Creation, equality

- [ ] **5.1.2**: `Facet` class
  - Properties: `id`, `color`, `points_in_facet`, `border_points`
  - Properties: `neighbours`, `bounding_box`, `label_pos`
  - Lazy neighbor array computation
  - Test: Facet creation, neighbor management

- [ ] **5.1.3**: `FacetResult` class
  - Collection of facets
  - Width/height
  - Methods to access facets
  - Test: Facet collection operations

#### 5.2 Color Reduction (`src/paintbynumbers/core/color_reduction.py`)
- [ ] **5.2.1**: `ColorReducer` class
  - `process()` method: Main entry point
  - K-means clustering on image
  - Create color map (pixel → cluster index)
  - Progress callbacks
  - Test: Compare color map with TypeScript

- [ ] **5.2.2**: Narrow pixel strip cleanup
  - `remove_narrow_strips()` method
  - Iterative cleanup (N runs)
  - Assign strip pixels to closest neighbor color
  - Test: Compare cleaned color map

**Critical Validation**: Process test image, compare color-reduced output visually

#### 5.3 Facet Creation (`src/paintbynumbers/core/facet_creator.py`)
- [ ] **5.3.1**: `FacetCreator` class
  - `create_facets()` method
  - Flood fill to find regions
  - Identify border points (adjacent to different color)
  - Build neighbor relationships
  - Progress callbacks
  - Test: Compare facet count, sizes, neighbors

**Critical Validation**: Verify facet boundaries are correct

#### 5.4 Facet Reduction (`src/paintbynumbers/core/facet_reducer.py`)
- [ ] **5.4.1**: `FacetReducer` class
  - `reduce()` method
  - Remove facets smaller than threshold
  - Voronoi-like filling (assign pixels to nearest neighbor)
  - Support largest-to-smallest or reverse processing
  - Maximum facet count enforcement
  - Test: Compare reduced facet count, color distributions

**Critical Validation**: Verify no gaps in output, all pixels assigned

---

### PHASE 6: Processing Pipeline - Part B (12-15 hours)
**Goal**: Border tracing, segmentation, and label placement (most complex)

#### 6.1 Border Tracing (`src/paintbynumbers/core/border_tracer.py`)
- [ ] **6.1.1**: `FacetBorderTracer` class
  - `trace()` method: Main entry point
  - Wall-following algorithm
  - State machine for orientation tracking
  - Handle corners, rotations, diagonals
  - Create ordered `PathPoint` sequences
  - Progress callbacks

- [ ] **6.1.2**: Orientation handling
  - `OrientationEnum` states (LEFT, TOP, RIGHT, BOTTOM)
  - Rotation logic (clockwise/counterclockwise)
  - Corner detection

- [ ] **6.1.3**: Complex case handling
  - Single-pixel facets
  - Diagonal connections
  - Inner facets (holes)

**Critical Validation**: This is THE most complex algorithm
- Test: Verify closed loops (start == end)
- Test: Compare path sequences with TypeScript
- Visual: Render borders, check for gaps

#### 6.2 Border Segmentation (`src/paintbynumbers/core/border_segmenter.py`)
- [ ] **6.2.1**: `PathSegment` class
  - Ordered list of points
  - Start/end points
  - Length calculation

- [ ] **6.2.2**: `FacetBoundarySegment` class
  - Links segment to neighbor facet
  - Properties: `facetId`, `neighbourFacetId`, `segment`

- [ ] **6.2.3**: `FacetBorderSegmenter` class
  - `segment()` method
  - Split borders into shared edges
  - Match segments between neighbors
  - Haar wavelet smoothing
  - Progress callbacks

- [ ] **6.2.4**: Haar wavelet smoothing
  - `smooth_segment()` method
  - Iteratively average point pairs
  - N iterations (configurable)
  - Test: Compare smoothed coordinates

**Critical Validation**:
- Test: Each segment shared by exactly 2 facets
- Visual: Check for border gaps after smoothing

#### 6.3 Label Placement (`src/paintbynumbers/core/label_placer.py`)
- [ ] **6.3.1**: `FacetLabelPlacer` class
  - `place()` method
  - Use polylabel algorithm
  - Convert facet points to polygon
  - Handle inner facets (holes)
  - Test: Compare label positions (tolerance: 5 pixels)

**Deliverable**: Complete processing pipeline from image → labeled facets

---

### PHASE 7: I/O and CLI (8-10 hours)
**Goal**: Image loading, SVG generation, CLI interface

#### 7.1 Image I/O (`src/paintbynumbers/utils/image_io.py`)
- [ ] **7.1.1**: Image loading
  - `load_image()` function
  - Support PNG, JPG, common formats
  - Auto-resize if too large
  - Convert to RGB numpy array
  - Test: Load various image formats

- [ ] **7.1.2**: Image data conversion
  - `image_to_array()` - PIL Image → numpy array
  - `array_to_image()` - numpy array → PIL Image
  - Test: Round-trip conversion

#### 7.2 SVG Generation (`src/paintbynumbers/output/svg_builder.py`)
- [ ] **7.2.1**: `SVGBuilder` class
  - `build()` method: Create SVG from facets
  - Draw facet paths (polygons)
  - Fill with colors (optional)
  - Draw borders (optional)
  - Add labels (optional)

- [ ] **7.2.2**: Path conversion
  - Convert `PathPoint[]` to SVG path string
  - Handle smoothed segments
  - Close paths properly

- [ ] **7.2.3**: Label rendering
  - Position text at label_pos
  - Font size, color customization
  - Ensure labels fit in facets

- [ ] **7.2.4**: SVG configuration
  - Size multiplier
  - Show/hide layers (borders, fills, labels)
  - Test: Generate SVG, validate structure

**Critical Validation**: Visual comparison with TypeScript SVG output

#### 7.3 Raster Export (`src/paintbynumbers/output/raster_export.py`)
- [ ] **7.3.1**: SVG to PNG/JPG conversion
  - Use cairosvg or Pillow
  - `export_png()` function
  - `export_jpg()` function (with quality)
  - Test: Generate raster outputs

#### 7.4 JSON Palette Export (`src/paintbynumbers/output/palette_export.py`)
- [ ] **7.4.1**: `export_palette()` function
  - Extract colors from facets
  - Calculate area percentages
  - Include color aliases if defined
  - Output JSON format matching TypeScript
  - Test: Validate JSON structure

#### 7.5 CLI Application (`src/paintbynumbers/cli/main.py`)
- [ ] **7.5.1**: Click-based CLI
  - Command: `paint-by-numbers`
  - Options:
    - `-i, --input PATH` (required)
    - `-o, --output PATH` (required)
    - `-s, --settings PATH` (optional JSON settings file)
    - `--colors N` (number of colors, default: 16)
    - `--format [svg|png|jpg|all]` (output format)
    - `--profile PATH` (output profile JSON)
    - `--seed N` (random seed)
    - `--verbose` (show progress)

- [ ] **7.5.2**: Progress reporting
  - ASCII progress bars (use `tqdm` or custom)
  - Stage indicators (clustering, tracing, etc.)
  - Time estimates

- [ ] **7.5.3**: Error handling
  - File not found
  - Invalid settings
  - Image processing errors
  - Graceful exit with messages

**Deliverable**: Working CLI matching TypeScript functionality

---

### PHASE 8: Testing & Validation (6-8 hours)
**Goal**: Comprehensive test suite ensuring equivalence with TypeScript

#### 8.1 Unit Tests (ongoing throughout development)
- [ ] All classes have 90%+ coverage
- [ ] Algorithm tests match TypeScript test cases
- [ ] Edge cases handled (empty images, single color, etc.)

#### 8.2 Integration Tests (`tests/integration/`)
- [ ] **8.2.1**: End-to-end pipeline test
  - Load test image
  - Process with default settings
  - Generate all output formats
  - Validate outputs exist and are valid

- [ ] **8.2.2**: Settings variation tests
  - Test different K-means cluster counts
  - Test color spaces (RGB, HSL, LAB)
  - Test facet reduction thresholds
  - Test smoothing iterations

#### 8.3 Comparison Tests with TypeScript (`tests/comparison/`)
- [ ] **8.3.1**: Setup comparison framework
  - Run TypeScript CLI on test images
  - Store reference outputs
  - Run Python CLI on same images
  - Compare outputs

- [ ] **8.3.2**: Visual comparison tests
  - Load reference SVG and Python SVG
  - Convert to images
  - Compute perceptual similarity (SSIM, MSE)
  - Threshold: 95% similarity

- [ ] **8.3.3**: Numerical comparison tests
  - Compare cluster centers (within 5%)
  - Compare facet counts (within 10%)
  - Compare border point counts (within 5%)
  - Compare label positions (within 5 pixels)

- [ ] **8.3.4**: JSON palette comparison
  - Compare color values (within 2 RGB units)
  - Compare area percentages (within 2%)

#### 8.4 Performance Benchmarks (`tests/benchmarks/`)
- [ ] **8.4.1**: Benchmark each algorithm
  - K-means clustering
  - Flood fill
  - Border tracing
  - Full pipeline

- [ ] **8.4.2**: Compare with TypeScript
  - Target: Within 2x of TypeScript performance
  - Identify bottlenecks
  - Document performance characteristics

**Deliverable**: Test suite with >90% coverage, validation against TypeScript

---

### PHASE 9: Examples & Documentation (3-4 hours)
**Goal**: Usage examples and minimal documentation

#### 9.1 Example Scripts (`examples/`)
- [ ] **9.1.1**: `basic_usage.py`
  - Load image, process with defaults, save SVG
  - Minimal example (~20 lines)

- [ ] **9.1.2**: `custom_settings.py`
  - Load settings from JSON
  - Process image
  - Save multiple output formats

- [ ] **9.1.3**: `settings_example.json`
  - Documented JSON settings file
  - Show all available options

- [ ] **9.1.4**: `batch_process.py`
  - Process multiple images
  - Different settings per image

#### 9.2 Documentation
- [ ] **9.2.1**: `README.md`
  - Installation instructions
  - Quick start example
  - CLI usage
  - Settings JSON format
  - Link to TypeScript project

- [ ] **9.2.2**: `MIGRATION_NOTES.md`
  - Differences from TypeScript version
  - Known limitations
  - Performance notes
  - Python-specific considerations

**Deliverable**: Working examples and minimal documentation

---

### PHASE 10: Packaging & Distribution (2-3 hours)
**Goal**: Prepare for distribution

#### 10.1 Package Configuration
- [ ] **10.1.1**: Finalize `pyproject.toml`
  - Metadata (name, version, author, license)
  - Dependencies with version constraints
  - Entry points for CLI
  - Build system configuration

- [ ] **10.1.2**: Finalize `setup.cfg`
  - Package discovery
  - Include package data
  - Classifiers

#### 10.2 Build & Install
- [ ] **10.2.1**: Test local installation
  - `pip install -e .` (editable mode)
  - Verify CLI command works
  - Test in clean virtualenv

- [ ] **10.2.2**: Build distribution
  - `python -m build`
  - Generate wheel and sdist
  - Test installation from wheel

#### 10.3 Quality Checks
- [ ] **10.3.1**: Run linters
  - ruff check
  - mypy type checking
  - Fix all issues

- [ ] **10.3.2**: Run full test suite
  - pytest with coverage
  - All tests pass
  - Coverage >90%

**Deliverable**: Installable Python package

---

## Task Execution Order (Smart Dependencies)

### Week 1: Foundation & Core
```
Day 1-2: Phase 1 (Setup) + Phase 2 (Data Structures)
Day 3-4: Phase 3.1-3.3 (Color utils, K-means, Flood fill)
Day 5-6: Phase 3.4-3.5 (Polylabel, utilities) + Phase 4 (Settings)
Day 7: Phase 5.1 (Facet structures)
```

### Week 2: Processing Pipeline
```
Day 8-9: Phase 5.2-5.3 (Color reduction, Facet creation)
Day 10: Phase 5.4 (Facet reduction)
Day 11-12: Phase 6.1 (Border tracing - COMPLEX!)
Day 13-14: Phase 6.2-6.3 (Segmentation, Label placement)
```

### Week 3: I/O, Testing, Polish
```
Day 15-16: Phase 7 (I/O, SVG, CLI)
Day 17-18: Phase 8 (Testing & validation)
Day 19: Phase 9 (Examples & docs)
Day 20: Phase 10 (Packaging)
```

**Total Estimated Time**: 60-80 hours (3-4 weeks part-time)

---

## Critical Success Factors

### ⚠️ High-Risk Areas (Need Extra Attention)
1. **Border Tracing Algorithm** (Phase 6.1)
   - Most complex state machine
   - Many edge cases
   - Must produce identical paths
   - Recommendation: Implement incrementally, test each case

2. **K-means Clustering** (Phase 3.2)
   - Numerical precision differences
   - Random initialization must be deterministic
   - Recommendation: Validate cluster centers match within 5%

3. **Border Segmentation & Smoothing** (Phase 6.2)
   - Segment matching between neighbors
   - Haar wavelet smoothing
   - Risk: Border gaps or overlaps
   - Recommendation: Visual validation at each step

### ✅ Validation Gates
- **After Phase 3**: All algorithms tested independently
- **After Phase 5**: Color reduction produces equivalent output
- **After Phase 6**: Full pipeline produces valid facets with borders
- **After Phase 7**: CLI generates SVG matching TypeScript
- **After Phase 8**: All comparison tests pass

### 🎯 Testing Strategy
- **Unit tests**: Each class/function (ongoing)
- **Integration tests**: After each phase
- **Comparison tests**: After Phase 7 (CLI complete)
- **Visual validation**: Manual review at key milestones

---

## Development Guidelines

### Code Style
- Python 3.11+ type hints throughout
- Docstrings for all public methods (Google style)
- Black formatting (or ruff format)
- Maximum line length: 100 chars

### Naming Conventions
- Classes: `PascalCase`
- Functions/methods: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private members: `_leading_underscore`

### Type Hints
```python
from typing import List, Dict, Optional, Tuple, Protocol
from numpy.typing import NDArray

def process_image(
    image: NDArray[np.uint8],
    settings: Settings,
    progress_callback: Optional[Callable[[float], None]] = None
) -> FacetResult:
    ...
```

### Error Handling
- Raise specific exceptions (ValueError, FileNotFoundError, etc.)
- Don't catch generic Exception unless re-raising
- Validate inputs early

### Testing
- Test file for each module: `test_<module>.py`
- Fixtures in `conftest.py`
- Use pytest parametrize for multiple cases
- Aim for 90%+ coverage

---

## Deliverables Checklist

- [ ] Python package structure (`src/`, `tests/`, `examples/`)
- [ ] All core algorithms ported and tested
- [ ] Complete processing pipeline
- [ ] CLI application with all TypeScript features
- [ ] SVG/PNG/JPG output generation
- [ ] JSON palette export
- [ ] Settings JSON I/O
- [ ] Example scripts with settings
- [ ] Unit test suite (>90% coverage)
- [ ] Integration tests
- [ ] Comparison tests vs TypeScript (perceptual equivalence)
- [ ] Performance benchmarks
- [ ] README with usage instructions
- [ ] `pyproject.toml` and `setup.cfg`
- [ ] Installable package (wheel + sdist)

---

## Next Steps

1. **Review this WBS** - Confirm scope and ordering
2. **Set up Phase 1** - Create project structure
3. **Implement incrementally** - Follow phase order
4. **Test continuously** - Don't defer testing
5. **Validate frequently** - Compare with TypeScript at milestones

**Ready to begin?** 🚀
