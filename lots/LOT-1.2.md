# LOT 1.2: Snapshot & Benchmark Current Behavior

**Phase:** 1 - Foundation & Testing Infrastructure
**Estimated Time:** 6 hours
**Priority:** CRITICAL - Establishes baseline for all refactoring
**Dependencies:** LOT 1.1 (Test Infrastructure)
**Assigned To:** _[AI Dev will write name here]_

---

## 🎯 Objective

Capture the current behavior of the paint-by-numbers algorithm as the "source of truth" baseline. Every refactoring must produce identical results to these snapshots. Also establish performance benchmarks to ensure no regression.

---

## 📋 Context

**Current State:**
- Working algorithm that produces correct output
- No tests yet to verify behavior is preserved
- No performance baseline measurements

**Why This Matters:**
This is THE MOST CRITICAL LOT in Phase 1. These snapshots are the contract that proves refactoring doesn't break anything. If we skip this or do it poorly, we have no way to know if future changes break the algorithm.

**What "Snapshot" Means:**
A snapshot is a saved output (image, data structure, SVG) from the current working code. After refactoring, we re-run the same inputs and compare outputs. If they match → refactoring is safe. If they differ → we broke something.

---

## ✅ Deliverables

### 1. Reference Output Generation
For each test image (small.png, medium.png, complex.png), generate and save:

**Stage Outputs:**
- [ ] After K-means clustering:
  - Color palette (array of RGB values)
  - Color-mapped image (ImageData or array indices)
  - Number of clusters found

- [ ] After facet creation:
  - Facet count
  - Facet boundaries (array of points for each facet)
  - Facet color assignments

- [ ] After border tracing:
  - Border paths (exact point sequences)
  - Border orientation metadata

- [ ] After border segmentation:
  - Segmented borders
  - Reduced point counts

- [ ] Final outputs:
  - Complete SVG file
  - Rendered PNG (if applicable)
  - Facet labels with positions

**File Structure:**
```
tests/snapshots/
├── small/
│   ├── 01-clustering.json          # Color palette + metadata
│   ├── 02-facets.json              # Facet data
│   ├── 03-borders.json             # Border paths
│   ├── 04-segmented.json           # Segmented borders
│   ├── 05-final.svg                # Final SVG
│   └── 05-final.png                # Rendered output
├── medium/
│   └── [same structure]
├── complex/
│   └── [same structure]
└── README.md                       # Explains snapshot format
```

### 2. Snapshot Test Suite
Create test files that compare current output to saved snapshots:

**File: `tests/integration/pipeline.snapshot.test.ts`**
- [ ] Test each pipeline stage independently
- [ ] Load test image → run stage → compare to snapshot
- [ ] Use appropriate tolerance for each stage:
  - K-means: ±1 RGB value (floating point rounding)
  - Facets: 0 tolerance (must be exact)
  - Borders: 0 tolerance (must be exact)
  - Final SVG: String comparison (must be identical)

**Tests to Create:**
```typescript
describe('Pipeline Snapshots - Small Image', () => {
  it('should produce identical clustering output', () => {});
  it('should produce identical facet output', () => {});
  it('should produce identical border paths', () => {});
  it('should produce identical segmented borders', () => {});
  it('should produce identical final SVG', () => {});
});

// Repeat for medium and complex images
```

### 3. Benchmark Suite
Create performance tests measuring execution time:

**File: `tests/performance/benchmark.test.ts`**
- [ ] Measure time for each pipeline stage
- [ ] Test with all 3 image sizes
- [ ] Run multiple iterations (10x) and take average
- [ ] Save baseline results

**Metrics to Capture:**
```typescript
interface BenchmarkResult {
  imageName: string;
  imageSize: { width: number; height: number };
  stages: {
    clustering: { avgMs: number; minMs: number; maxMs: number };
    facetCreation: { avgMs: number; minMs: number; maxMs: number };
    borderTracing: { avgMs: number; minMs: number; maxMs: number };
    borderSegmentation: { avgMs: number; minMs: number; maxMs: number };
    facetReduction: { avgMs: number; minMs: number; maxMs: number };
    total: { avgMs: number; minMs: number; maxMs: number };
  };
  memoryUsage: {
    heapUsed: number;
    heapTotal: number;
  };
}
```

**Output File:**
```
tests/performance/BASELINE.json
```

### 4. Documentation
Create `tests/snapshots/README.md`:
- [ ] Explain what snapshots are
- [ ] How they were generated
- [ ] Format of each JSON file
- [ ] How to regenerate if needed (DANGEROUS - requires manager approval)
- [ ] Tolerance guidelines

Create `BASELINE_PERFORMANCE.md` in project root:
- [ ] Current performance metrics for each image size
- [ ] Hardware/environment specs
- [ ] Acceptable tolerance for refactoring (±5%)
- [ ] Date and commit hash when baseline was created

### 5. Snapshot Validation Tests
- [ ] Verify all snapshots were created successfully
- [ ] Verify snapshots are not empty/corrupt
- [ ] Run snapshot tests and confirm they all pass
- [ ] Document any non-deterministic behavior found

---

## 🧪 Validation Criteria

**All of these must pass for manager approval:**

### Snapshot Completeness
1. ✅ All 3 test images have complete snapshot sets
2. ✅ All pipeline stages captured (5 stages × 3 images = 15 snapshot sets)
3. ✅ Snapshot files are valid JSON/SVG
4. ✅ Snapshot files are committed to git

### Snapshot Test Suite
1. ✅ All snapshot tests pass (15+ tests)
2. ✅ Tests use appropriate tolerance levels
3. ✅ Tests are deterministic (run 10 times, all pass)
4. ✅ Test output is clear when failure occurs

### Benchmark Suite
1. ✅ Benchmarks run successfully for all 3 images
2. ✅ Results are saved to `BASELINE.json`
3. ✅ Performance metrics are reasonable (no outliers)
4. ✅ Memory usage is captured

### Documentation
1. ✅ Snapshot README is comprehensive
2. ✅ Baseline performance doc exists
3. ✅ Hardware specs are documented
4. ✅ Instructions for future developers are clear

### Code Quality
1. ✅ Snapshot generation code is clean and commented
2. ✅ Test code follows best practices
3. ✅ No hardcoded paths (use path.join)

---

## 🚀 Implementation Guide

### Step 1: Create Snapshot Generation Script (90 min)

**File: `tests/helpers/generateSnapshots.ts`**

```typescript
import { readFileSync, writeFileSync, mkdirSync } from 'fs';
import { join } from 'path';
import { processImage } from '../../src/guiprocessmanager';
import { Settings } from '../../src/settings';

interface SnapshotData {
  clustering: any;
  facets: any;
  borders: any;
  segmented: any;
  finalSVG: string;
}

async function generateSnapshotsForImage(
  imageName: string,
  settings: Settings
): Promise<SnapshotData> {
  console.log(`Generating snapshots for ${imageName}...`);

  // Load image
  const imagePath = join(__dirname, '../fixtures', imageName);
  const imageBuffer = readFileSync(imagePath);

  // Run through pipeline and capture each stage
  // You'll need to modify guiprocessmanager.ts to expose intermediate results
  // OR duplicate the pipeline logic here for snapshot purposes

  const snapshots: SnapshotData = {
    clustering: null,
    facets: null,
    borders: null,
    segmented: null,
    finalSVG: '',
  };

  // TODO: Implement pipeline execution with intermediate capture

  return snapshots;
}

async function generateAllSnapshots() {
  const testImages = ['small.png', 'medium.png', 'complex.png'];
  const defaultSettings = new Settings(); // Use default settings

  for (const imageName of testImages) {
    const baseName = imageName.replace('.png', '');
    const outputDir = join(__dirname, '../snapshots', baseName);

    // Create output directory
    mkdirSync(outputDir, { recursive: true });

    // Generate snapshots
    const snapshots = await generateSnapshotsForImage(imageName, defaultSettings);

    // Save snapshots
    writeFileSync(
      join(outputDir, '01-clustering.json'),
      JSON.stringify(snapshots.clustering, null, 2)
    );
    writeFileSync(
      join(outputDir, '02-facets.json'),
      JSON.stringify(snapshots.facets, null, 2)
    );
    writeFileSync(
      join(outputDir, '03-borders.json'),
      JSON.stringify(snapshots.borders, null, 2)
    );
    writeFileSync(
      join(outputDir, '04-segmented.json'),
      JSON.stringify(snapshots.segmented, null, 2)
    );
    writeFileSync(
      join(outputDir, '05-final.svg'),
      snapshots.finalSVG
    );

    console.log(`✓ Snapshots saved for ${imageName}`);
  }

  console.log('All snapshots generated successfully!');
}

// Run if executed directly
if (require.main === module) {
  generateAllSnapshots().catch(console.error);
}
```

**How to Capture Intermediate Stages:**

You have two options:

**Option A: Modify Pipeline (Temporary Instrumentation)**
Add hooks to `guiprocessmanager.ts` to capture intermediate state:
```typescript
// Add parameter to enable snapshot capture
processImage(settings, progressCallback, snapshotCallback?) {
  // ... existing code ...

  // After clustering
  if (snapshotCallback) {
    snapshotCallback('clustering', { palette, clusterData });
  }

  // After facet creation
  if (snapshotCallback) {
    snapshotCallback('facets', facetResult);
  }

  // etc.
}
```

**Option B: Duplicate Pipeline Logic (Cleaner)**
Copy pipeline logic into snapshot generator to avoid modifying production code.

**Recommendation:** Use Option A for speed, document that it's temporary instrumentation.

### Step 2: Generate Snapshots (30 min)

```bash
# Run snapshot generation
npx ts-node tests/helpers/generateSnapshots.ts

# Verify snapshots were created
ls -la tests/snapshots/
```

**Visual Verification:**
- Open each SVG file and verify it looks correct
- Compare SVG outputs visually

### Step 3: Create Snapshot Tests (120 min)

**File: `tests/integration/clustering.snapshot.test.ts`**
```typescript
import { readFileSync } from 'fs';
import { join } from 'path';
import { loadTestImage } from '../helpers/testUtils';
import { runClustering } from '../../src/lib/clustering'; // You may need to export this

describe('K-means Clustering Snapshots', () => {
  const testImages = ['small', 'medium', 'complex'];

  testImages.forEach(imageName => {
    it(`should match snapshot for ${imageName}`, () => {
      // Load test image
      const img = loadTestImage(`${imageName}.png`);

      // Run clustering
      const result = runClustering(img, defaultSettings);

      // Load snapshot
      const snapshotPath = join(__dirname, '../snapshots', imageName, '01-clustering.json');
      const snapshot = JSON.parse(readFileSync(snapshotPath, 'utf8'));

      // Compare with tolerance
      expect(result.palette).toMatchPaletteWithTolerance(snapshot.palette, 1);
      expect(result.clusterCount).toBe(snapshot.clusterCount);
    });
  });
});
```

Create similar test files for:
- `facets.snapshot.test.ts`
- `borders.snapshot.test.ts`
- `segmentation.snapshot.test.ts`
- `final-output.snapshot.test.ts`

**Custom Jest Matchers:**

You may need to create custom matchers for complex comparisons:

**File: `tests/helpers/customMatchers.ts`**
```typescript
expect.extend({
  toMatchPaletteWithTolerance(received, expected, tolerance) {
    // Compare color palettes with RGB tolerance
  },

  toMatchBorderPath(received, expected) {
    // Compare border paths point-by-point
  },

  toMatchFacetStructure(received, expected) {
    // Compare facet data structures
  },
});
```

### Step 4: Create Benchmark Suite (90 min)

**File: `tests/performance/benchmark.test.ts`**
```typescript
import { performance } from 'perf_hooks';
import { writeFileSync } from 'fs';
import { join } from 'path';

interface TimingResult {
  avgMs: number;
  minMs: number;
  maxMs: number;
}

function measureStage(fn: () => void, iterations: number = 10): TimingResult {
  const times: number[] = [];

  for (let i = 0; i < iterations; i++) {
    const start = performance.now();
    fn();
    const end = performance.now();
    times.push(end - start);
  }

  return {
    avgMs: times.reduce((a, b) => a + b, 0) / times.length,
    minMs: Math.min(...times),
    maxMs: Math.max(...times),
  };
}

describe('Performance Benchmarks', () => {
  // Increase timeout for performance tests
  jest.setTimeout(300000); // 5 minutes

  const testImages = ['small', 'medium', 'complex'];
  const results: BenchmarkResult[] = [];

  testImages.forEach(imageName => {
    it(`should benchmark ${imageName} image`, () => {
      // Load image
      const img = loadTestImage(`${imageName}.png`);

      // Benchmark each stage
      const clusteringTime = measureStage(() => {
        runClustering(img, defaultSettings);
      });

      const facetTime = measureStage(() => {
        runFacetCreation(/* ... */);
      });

      // ... benchmark other stages ...

      const result: BenchmarkResult = {
        imageName,
        imageSize: { width: img.width, height: img.height },
        stages: {
          clustering: clusteringTime,
          facetCreation: facetTime,
          // ... other stages ...
        },
        memoryUsage: process.memoryUsage(),
      };

      results.push(result);

      // Log results
      console.log(`\n${imageName} benchmark:`);
      console.log(`  Clustering: ${clusteringTime.avgMs.toFixed(2)}ms`);
      console.log(`  Facet Creation: ${facetTime.avgMs.toFixed(2)}ms`);
      // ... log other stages ...
    });
  });

  afterAll(() => {
    // Save baseline results
    const outputPath = join(__dirname, 'BASELINE.json');
    writeFileSync(outputPath, JSON.stringify(results, null, 2));
    console.log(`\n✓ Baseline saved to ${outputPath}`);
  });
});
```

**Run Benchmarks:**
```bash
npm test -- --testPathPattern=benchmark
```

### Step 5: Create Documentation (60 min)

**File: `tests/snapshots/README.md`**
```markdown
# Snapshot Reference Data

This directory contains reference outputs from the paint-by-numbers algorithm.
These snapshots serve as the "source of truth" for validating refactoring work.

## Snapshot Format

### 01-clustering.json
```json
{
  "palette": [[R, G, B], ...],
  "clusterCount": number,
  "colorMap": [...],
  "settings": { ... }
}
```

### 02-facets.json
[Document structure]

### 03-borders.json
[Document structure]

### 04-segmented.json
[Document structure]

### 05-final.svg
Complete SVG output.

## How Snapshots Were Generated

[Date, commit hash, command used]

## IMPORTANT: Regenerating Snapshots

⚠️ **DANGER**: Regenerating snapshots changes the "source of truth."
Only regenerate if:
1. You've validated the current algorithm is correct
2. You have manager approval
3. You understand the implications

To regenerate:
```bash
npx ts-node tests/helpers/generateSnapshots.ts
```

## Tolerance Guidelines

- **K-means clustering**: ±1 RGB value (floating point rounding)
- **Facet boundaries**: 0 tolerance (must be exact)
- **Border paths**: 0 tolerance (must be exact)
- **Final SVG**: String match (must be identical)
```

**File: `BASELINE_PERFORMANCE.md`**
```markdown
# Performance Baseline

**Created:** [Date]
**Commit:** [Hash]
**Hardware:**
- CPU: [Your CPU]
- RAM: [Your RAM]
- Node.js: [Version]

## Baseline Metrics

### Small Image (100x100)
- Clustering: X.XX ms
- Facet Creation: X.XX ms
- Border Tracing: X.XX ms
- Segmentation: X.XX ms
- **Total: X.XX ms**

[Include all metrics]

## Acceptable Tolerance

Refactored code must maintain performance within **±5%** of baseline.

Regressions beyond ±5% require investigation and optimization before proceeding.
```

### Step 6: Validation & Testing (30 min)

```bash
# Run all snapshot tests
npm test -- --testPathPattern=snapshot

# Should see: All tests passed

# Run benchmarks
npm test -- --testPathPattern=benchmark

# Verify baseline file created
cat tests/performance/BASELINE.json
```

---

## 💡 Tips & Gotchas

### Determinism is Critical
- K-means must use fixed random seed for deterministic results
- Verify by running snapshot generation twice and comparing outputs
- If outputs differ, fix non-determinism before proceeding!

### Snapshot Size
- Snapshot files may be large (especially border data)
- This is acceptable - completeness > size
- Git can handle these files

### When Snapshots Don't Match
In future LOTs, if snapshot tests fail:
1. DON'T regenerate snapshots
2. Find and fix the bug in refactored code
3. Only regenerate if you've proven original code was wrong

### Performance Variance
- Run benchmarks multiple times
- Take average of 10+ runs
- Note variance in results
- System load affects benchmarks (close other programs)

---

## 📤 Deliverables Checklist

Before marking this LOT as complete, ensure:

- [ ] All 3 test images have complete snapshot sets (5 files each)
- [ ] Snapshots are valid and non-empty
- [ ] Snapshot tests created for all stages
- [ ] All snapshot tests pass (15+ tests)
- [ ] Benchmark suite created
- [ ] Baseline performance metrics saved
- [ ] `tests/snapshots/README.md` complete
- [ ] `BASELINE_PERFORMANCE.md` created
- [ ] Visual verification done (SVGs look correct)
- [ ] Determinism verified (ran snapshot gen 2x, identical results)
- [ ] All code committed to git
- [ ] Updated `PROJECT_TRACKER.md`

---

## 🔄 Handoff Notes

**For Next AI Devs (LOT 2.x):**
- Baseline established in `tests/snapshots/`
- All refactoring MUST pass snapshot tests
- Run `npm test` after any changes
- If snapshot tests fail, you broke something - fix it!

**Known Issues:**
- [Document any non-determinism found]
- [Document any edge cases discovered]

---

## 📝 AI Dev Updates

**Started:** [Date/Time]

**Progress Notes:**
- [Update as you work]

**Completed:** [Date/Time]

**Actual Hours:** [Hours]

**Deviations:**
- [Any changes from plan]

**Issues:**
- [Problems and solutions]

---

**Last Updated:** 2025-11-05
**Version:** 1.0
