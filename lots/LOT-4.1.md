# LOT 4.1: Pipeline Manager Refactor

**Phase:** 4 - Pipeline Orchestration
**Estimated Time:** 7 hours
**Priority:** HIGH
**Dependencies:** LOT 3.1, 3.2, 3.3, 3.4, 3.5 (All Core Algorithms)
**Assigned To:** _[AI Dev will write name here]_

---

## 🎯 Objective

Refactor pipeline manager to create modular, testable pipeline stages that can be composed, tested independently, and easily extended.

---

## 📋 Context

**Current:** `guiprocessmanager.ts` (429 lines) - Monolithic pipeline
**Goal:** Modular stages, clear interfaces, testable components

---

## ✅ Deliverables

### 1. Create PipelineStage Interface (60 min)
```typescript
export interface PipelineStage<TInput, TOutput> {
  name: string;
  execute(input: TInput, progress: ProgressCallback): Promise<TOutput>;
}
```

### 2. Implement Pipeline Stages (180 min)
- [ ] ResizeStage
- [ ] ClusteringStage
- [ ] FacetCreationStage
- [ ] BorderTracingStage
- [ ] BorderSegmentationStage
- [ ] FacetReductionStage
- [ ] LabelPlacementStage
- [ ] SVGGenerationStage

### 3. Create Pipeline Class (90 min)
- [ ] Compose stages
- [ ] Centralized progress reporting
- [ ] Error handling
- [ ] Stage skipping/configuration

### 4. Refactor guiprocessmanager.ts (60 min)
- [ ] Use new Pipeline class
- [ ] Simplify orchestration logic
- [ ] Maintain backward compatibility

### 5. Tests (90 min)
- [ ] Unit tests for each stage
- [ ] Integration tests for full pipeline
- [ ] End-to-end tests
- [ ] Snapshot comparison

### 6. Documentation (30 min)
- [ ] Pipeline architecture
- [ ] Stage documentation
- [ ] Usage examples

---

## 🧪 Validation Criteria

1. ✅ Complete pipeline produces IDENTICAL SVG output
2. ✅ Each stage testable independently
3. ✅ Progress callbacks work correctly
4. ✅ Test coverage ≥85%
5. ✅ All snapshot tests pass

---

## 🚀 Implementation Example

```typescript
// Pipeline Stage
export class ClusteringStage implements PipelineStage<ImageData, ClusteringResult> {
  name = 'Clustering';

  constructor(private quantizer: ColorQuantizer) {}

  async execute(
    input: ImageData,
    progress: ProgressCallback
  ): Promise<ClusteringResult> {
    progress(0, 'Starting color clustering...');

    const result = this.quantizer.quantize(input, 16);

    progress(100, 'Clustering complete');
    return result;
  }
}

// Pipeline Composition
export class Pipeline {
  private stages: PipelineStage<any, any>[] = [];

  addStage(stage: PipelineStage<any, any>): this {
    this.stages.push(stage);
    return this;
  }

  async execute(
    initialInput: any,
    progressCallback: ProgressCallback
  ): Promise<any> {
    let output = initialInput;

    for (let i = 0; i < this.stages.length; i++) {
      const stage = this.stages[i];
      const stageProgress = (percent: number, msg: string) => {
        const overallPercent = ((i + percent / 100) / this.stages.length) * 100;
        progressCallback(overallPercent, `[${stage.name}] ${msg}`);
      };

      output = await stage.execute(output, stageProgress);
    }

    return output;
  }
}

// Usage
const pipeline = new Pipeline()
  .addStage(new ResizeStage(settings))
  .addStage(new ClusteringStage(quantizer))
  .addStage(new FacetCreationStage())
  .addStage(new BorderTracingStage())
  .addStage(new BorderSegmentationStage())
  .addStage(new SVGGenerationStage());

const result = await pipeline.execute(imageData, progressCallback);
```

---

## 📤 Deliverables Checklist

- [ ] PipelineStage interface
- [ ] All 8 stages implemented
- [ ] Pipeline class created
- [ ] guiprocessmanager.ts refactored
- [ ] Unit tests for each stage
- [ ] Integration tests
- [ ] E2E tests pass
- [ ] Snapshot tests pass
- [ ] Progress reporting works
- [ ] Documentation complete
- [ ] Code committed
- [ ] PROJECT_TRACKER.md updated

---

## 🔄 Handoff Notes

**For Manager:**
- Verify end-to-end output matches baseline
- Test progress callbacks
- Ensure each stage independently testable

**For Next AI Devs:**
- Pipeline is now modular
- Easy to add new stages
- Each stage has clear interface

---

**Last Updated:** 2025-11-05
**Version:** 1.0
