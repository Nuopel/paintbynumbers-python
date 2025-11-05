# 🔍 MANAGER VALIDATION PROTOCOL

**Version:** 1.0
**Last Updated:** 2025-11-05

---

## Purpose

This document defines the validation process that the AI Manager must follow when reviewing each completed LOT before approving handoff to the next AI Dev instance.

---

## General Validation Process

### Step 1: Pre-Validation Checklist
- [ ] LOT status is marked as 🟢 COMPLETE in `PROJECT_TRACKER.md`
- [ ] AI Dev has provided completion summary
- [ ] All deliverables are checked off in the LOT file
- [ ] Actual hours are logged

### Step 2: Code Review
- [ ] Read all modified/created files
- [ ] Check code quality and readability
- [ ] Verify proper TypeScript typing (no `any` types without justification)
- [ ] Ensure consistent code style
- [ ] Check for proper error handling
- [ ] Verify no commented-out code or TODO comments left unresolved

### Step 3: Test Validation
- [ ] All tests pass: `npm test`
- [ ] Test coverage meets requirements (check LOT-specific requirements)
- [ ] Tests are well-written and meaningful (not just for coverage)
- [ ] Edge cases are covered

### Step 4: Integration Validation
- [ ] Code integrates properly with existing codebase
- [ ] No breaking changes to other modules
- [ ] Dependencies are properly managed
- [ ] No circular dependencies introduced

### Step 5: Documentation Review
- [ ] Code is properly commented
- [ ] JSDoc/TSDoc comments for public APIs
- [ ] README or docs updated if needed
- [ ] Changes logged in LOT completion notes

### Step 6: Functional Validation
- [ ] Run the application (Web UI or CLI)
- [ ] Test the refactored functionality manually
- [ ] Verify output matches baseline/snapshots
- [ ] Check for any runtime errors or warnings

### Step 7: Performance Check
- [ ] No obvious performance regressions
- [ ] If benchmarks exist, performance is within acceptable range
- [ ] No memory leaks introduced

---

## LOT-Specific Validation Criteria

### Phase 1: Foundation & Testing

#### LOT 1.1: Test Infrastructure Setup

**Critical Checks:**
- [ ] Jest is properly installed and configured
- [ ] `npm test` command works
- [ ] Can run tests in watch mode: `npm test -- --watch`
- [ ] Test fixtures directory created with sample images
- [ ] Image comparison utility works correctly
- [ ] Tests can load Canvas API (browser) or node-canvas (Node.js)

**Validation Commands:**
```bash
npm test
npm test -- --coverage
```

**Expected Output:**
- Tests run successfully (even if no tests yet)
- No error messages about missing dependencies
- Coverage report generates

**Files to Review:**
- `jest.config.js` or `jest.config.ts`
- `package.json` (devDependencies)
- `tests/` or `__tests__/` directory structure
- Test helper utilities

**Approval Criteria:**
- ✅ All commands run without errors
- ✅ Test infrastructure is properly set up
- ✅ Documentation on how to run tests is clear

---

#### LOT 1.2: Snapshot & Benchmark Current Behavior

**Critical Checks:**
- [ ] Reference outputs generated for all 3 test images
- [ ] Snapshots stored in version control
- [ ] Snapshot tests pass when run
- [ ] Baseline benchmarks documented
- [ ] Performance metrics are reproducible

**Validation Commands:**
```bash
npm test -- --testPathPattern=snapshot
npm run benchmark # or appropriate command
```

**Expected Output:**
- All snapshot tests pass
- Benchmark results show execution times
- Reference images are pixel-perfect

**Files to Review:**
- `tests/snapshots/` directory
- Benchmark test files
- `BASELINE_PERFORMANCE.md` or similar documentation

**Manual Validation:**
- Open reference images and verify they look correct
- Compare outputs from multiple runs to ensure determinism

**Approval Criteria:**
- ✅ Snapshots are comprehensive (cover all pipeline stages)
- ✅ Benchmarks are documented and reproducible
- ✅ Reference outputs are visually correct
- ✅ Tests are deterministic (same input = same output)

---

### Phase 2: Utilities

#### LOT 2.1: Configuration & Constants Module

**Critical Checks:**
- [ ] All magic numbers replaced with named constants
- [ ] Constants are properly typed
- [ ] Constants are documented with JSDoc
- [ ] No hardcoded values remain in refactored code
- [ ] Snapshot tests still pass

**Validation Commands:**
```bash
npm test
npm run lint # if available
```

**Search for Remaining Magic Numbers:**
```bash
# Look for suspicious numeric literals
grep -r "[^a-zA-Z0-9_]\d\+[^a-zA-Z0-9_]" src/ --exclude-dir=node_modules
```

**Files to Review:**
- `src/lib/constants.ts`
- `src/lib/config.ts`
- All files that previously had magic numbers

**Approval Criteria:**
- ✅ All magic numbers are replaced
- ✅ Constants are well-organized and documented
- ✅ All snapshot tests pass (no regressions)
- ✅ Code is more readable than before

---

#### LOT 2.2: Boundary & Validation Utilities

**Critical Checks:**
- [ ] Utility functions are pure and side-effect free
- [ ] Edge cases are tested (0, negative, overflow, undefined)
- [ ] Functions are properly typed
- [ ] All boundary checks in codebase use utilities
- [ ] Test coverage ≥95%

**Validation Commands:**
```bash
npm test -- --coverage --testPathPattern=boundaryUtils
npm test # all tests should still pass
```

**Files to Review:**
- `src/lib/boundaryUtils.ts`
- Files that use boundary utilities (facetCreator, facetBorderTracer, etc.)
- Test files for boundary utilities

**Manual Test Cases to Verify:**
```typescript
// Expected behaviors:
isInBounds(0, 0, 10, 10) === true
isInBounds(-1, 0, 10, 10) === false
isInBounds(10, 10, 10, 10) === false
clamp(5, 0, 10) === 5
clamp(-5, 0, 10) === 0
clamp(15, 0, 10) === 10
```

**Approval Criteria:**
- ✅ Utilities are well-tested with ≥95% coverage
- ✅ All pipeline snapshots still pass
- ✅ Code using utilities is cleaner than before
- ✅ No duplicate boundary checking logic remains

---

#### LOT 2.3: Color Space Utilities Refactor

**Critical Checks:**
- [ ] Color conversions produce identical results (±0.1 tolerance)
- [ ] Color distance calculations are accurate
- [ ] All color spaces supported (RGB, HSL, LAB)
- [ ] K-means clustering produces identical output
- [ ] Test coverage ≥90%

**Validation Commands:**
```bash
npm test -- --testPathPattern=color
npm test # K-means tests must pass
```

**Manual Validation:**
Test known color conversions:
```typescript
// RGB(255, 0, 0) = HSL(0°, 100%, 50%)
// RGB(128, 128, 128) = LAB(53.59, 0, 0)
```

**Files to Review:**
- Refactored `src/lib/colorconversion.ts`
- `colorreductionmanagement.ts` (should use new Color class)
- Color conversion tests

**Approval Criteria:**
- ✅ Color conversions are mathematically correct
- ✅ K-means clustering snapshot tests pass
- ✅ API is cleaner and easier to use
- ✅ No color-related code duplication remains

---

### Phase 3: Core Algorithms

#### LOT 3.1: K-Means Clustering Refactor

**Critical Checks:**
- [ ] Clustering produces identical results with same seed
- [ ] Refactored code is more modular
- [ ] Vector class is in separate file
- [ ] Clustering strategies are extensible
- [ ] All downstream tests pass

**Validation Commands:**
```bash
npm test -- --testPathPattern=clustering
npm test # all pipeline tests
```

**Determinism Test:**
```bash
# Run clustering multiple times with same seed - should produce identical output
npm test -- --testPathPattern=clustering-determinism
```

**Files to Review:**
- `src/lib/clustering.ts`
- `src/lib/Vector.ts` (if separated)
- `colorreductionmanagement.ts`

**Approval Criteria:**
- ✅ Clustering is deterministic (same seed = same result)
- ✅ Code is more modular and maintainable
- ✅ All snapshot tests pass
- ✅ Performance is within ±5% of baseline

---

#### LOT 3.2: Facet Creation Refactor

**Critical Checks:**
- [ ] Facet output identical to baseline (same count, same boundaries)
- [ ] Flood-fill algorithm is in separate class
- [ ] Uses boundary utilities from LOT 2.2
- [ ] Test coverage ≥90%
- [ ] Performance within ±5%

**Validation Commands:**
```bash
npm test -- --testPathPattern=facet
npm run benchmark-facet # if available
```

**Manual Validation:**
- Run pipeline on test images
- Verify facet count matches baseline
- Visually inspect facet boundaries

**Files to Review:**
- `src/facetCreator.ts`
- `src/lib/FloodFillAlgorithm.ts` (if separated)
- Facet creation tests

**Approval Criteria:**
- ✅ Facet output is pixel-perfect identical
- ✅ Code is cleaner and more modular
- ✅ All tests pass
- ✅ No performance regression

---

#### LOT 3.3: Facet Border Tracer - Orientation Strategy ⚠️

**⚠️ CRITICAL LOT - Extra Scrutiny Required**

**Critical Checks:**
- [ ] Border paths are EXACTLY identical to baseline
- [ ] Code reduction ≥40% achieved
- [ ] No code duplication between orientations
- [ ] Strategy pattern is properly implemented
- [ ] All edge cases tested (corners, single-pixel facets, etc.)
- [ ] Test coverage ≥95%
- [ ] Performance within ±5%

**Validation Commands:**
```bash
npm test -- --testPathPattern=borderTracer
npm test # all snapshot tests MUST pass
npm run benchmark-border-tracing # critical performance check
```

**Manual Validation:**
- Run pipeline on all test images
- Compare border paths point-by-point with baseline
- Visual inspection of traced borders
- Test with edge cases (very small images, single-color images, etc.)

**Files to Review:**
- `src/facetBorderTracer.ts` (should be ~250 lines, down from 502)
- Orientation strategy implementations
- Extensive test files

**Point-by-Point Validation:**
```bash
# Export border points to JSON and diff with baseline
# Any difference is a regression!
diff baseline-borders.json current-borders.json
```

**Approval Criteria:**
- ✅ Border paths are EXACTLY identical (zero tolerance)
- ✅ Code is dramatically cleaner (≥40% reduction)
- ✅ No duplication between orientations
- ✅ All tests pass with ≥95% coverage
- ✅ Performance is maintained
- ❌ REJECT if ANY border path differs from baseline

**Escalation:**
If this LOT fails validation, pause the project and investigate thoroughly before proceeding.

---

#### LOT 3.4: Facet Border Segmenter Refactor

**Critical Checks:**
- [ ] Segmented borders identical to baseline
- [ ] Haar wavelet reduction is in separate class
- [ ] Nesting depth reduced from 8+ to ≤4 levels
- [ ] Test coverage ≥90%
- [ ] Performance maintained

**Validation Commands:**
```bash
npm test -- --testPathPattern=segmenter
npm test # all tests
```

**Code Quality Check:**
```bash
# Check nesting depth (should be ≤4)
# Use complexity analysis tools
npm run lint -- --rule 'complexity: [error, 10]'
```

**Files to Review:**
- `src/facetBorderSegmenter.ts`
- `src/lib/WaveletReducer.ts` (if separated)

**Approval Criteria:**
- ✅ Output identical to baseline
- ✅ Code complexity reduced significantly
- ✅ Nesting depth ≤4 levels
- ✅ All tests pass

---

#### LOT 3.5: Facet Reducer Refactor

**Critical Checks:**
- [ ] Facet reduction produces identical results
- [ ] Small facet detection logic is clear
- [ ] Merge strategy is extensible
- [ ] Test coverage ≥90%

**Validation Commands:**
```bash
npm test -- --testPathPattern=facetReducer
npm test # all tests
```

**Files to Review:**
- `src/facetReducer.ts`
- Merge strategy implementations

**Approval Criteria:**
- ✅ Output identical to baseline
- ✅ Code is self-documenting
- ✅ All tests pass

---

### Phase 4: Pipeline Orchestration

#### LOT 4.1: Pipeline Manager Refactor

**Critical Checks:**
- [ ] Complete pipeline produces identical SVG output
- [ ] Each stage can be tested independently
- [ ] Progress callbacks work correctly
- [ ] Test coverage ≥85%
- [ ] Pipeline is easy to extend

**Validation Commands:**
```bash
npm test -- --testPathPattern=pipeline
npm test # all integration tests
```

**Manual Validation:**
- Run full pipeline on all test images
- Verify progress updates display correctly
- Test cancellation/interruption (if supported)

**Files to Review:**
- `src/guiprocessmanager.ts` (should be cleaner)
- Pipeline stage implementations
- Integration tests

**Approval Criteria:**
- ✅ End-to-end output is identical
- ✅ Pipeline is modular and extensible
- ✅ Progress reporting works
- ✅ All tests pass

---

#### LOT 4.2: Settings & Configuration Refactor

**Critical Checks:**
- [ ] Configuration validation works correctly
- [ ] Invalid settings are rejected with clear errors
- [ ] Default settings produce identical output
- [ ] Test coverage ≥95%

**Validation Commands:**
```bash
npm test -- --testPathPattern=settings
```

**Manual Validation:**
Test invalid configurations:
```typescript
// Should reject:
{ numberOfColors: -1 }  // negative
{ numberOfColors: 1000 } // too high
{ kMeansNrOfClusters: 'invalid' } // wrong type
```

**Files to Review:**
- `src/settings.ts`
- Settings validation logic

**Approval Criteria:**
- ✅ Validation catches all invalid inputs
- ✅ Error messages are clear
- ✅ All tests pass

---

### Phase 5: Interface & Documentation

#### LOT 5.1: CLI Interface Update

**Critical Checks:**
- [ ] CLI produces identical outputs to baseline
- [ ] All CLI options work correctly
- [ ] Error messages are clear
- [ ] Integration tests pass

**Validation Commands:**
```bash
npm run build-cli # or appropriate command
./dist/cli --help
./dist/cli --input tests/fixtures/testinput.png --output test-output.svg
diff test-output.svg baseline-output.svg
```

**Manual Testing:**
- Test all CLI flags
- Test with invalid inputs
- Test help documentation

**Files to Review:**
- `src-cli/main.ts`
- CLI tests

**Approval Criteria:**
- ✅ CLI produces identical output
- ✅ All options work
- ✅ User experience is good

---

#### LOT 5.2: Web UI Integration

**Critical Checks:**
- [ ] Web UI produces identical outputs
- [ ] Progress bar updates smoothly
- [ ] No console errors
- [ ] Works in Chrome, Firefox, Safari

**Validation Commands:**
```bash
npm start # or lite-server
# Manual browser testing required
```

**Manual Testing Checklist:**
- [ ] Upload image and process
- [ ] Try all settings
- [ ] Verify progress bar
- [ ] Check for console errors
- [ ] Test in multiple browsers
- [ ] Test with various image sizes

**Files to Review:**
- `src/gui.ts`
- `index.html`

**Approval Criteria:**
- ✅ UI works perfectly
- ✅ No regressions
- ✅ Tested in all browsers

---

#### LOT 5.3: API Documentation & Code Comments

**Critical Checks:**
- [ ] Every public method has JSDoc
- [ ] Documentation is accurate
- [ ] README is up-to-date
- [ ] Architecture docs are clear

**Validation:**
```bash
# Generate documentation (if using typedoc or similar)
npm run docs

# Check for missing JSDoc
# (can use linting rules)
```

**Manual Review:**
- Read all documentation
- Verify examples work
- Check for typos and clarity

**Files to Review:**
- All source files (for JSDoc)
- `README.md`
- `ARCHITECTURE.md`

**Approval Criteria:**
- ✅ Documentation is comprehensive
- ✅ Examples are correct
- ✅ Easy for new developers to understand

---

#### LOT 5.4: Performance Optimization & Benchmarking

**Critical Checks:**
- [ ] Performance is within ±5% of baseline
- [ ] No memory leaks detected
- [ ] Benchmark results documented
- [ ] Performance tests are automated

**Validation Commands:**
```bash
npm run benchmark
npm test -- --testPathPattern=performance
```

**Manual Performance Testing:**
- Test with large images (2000x2000+)
- Monitor memory usage
- Compare execution times with baseline

**Approval Criteria:**
- ✅ Performance maintained or improved
- ✅ No memory leaks
- ✅ Benchmarks documented

---

### Phase 6: Final Validation

#### LOT 6.1: End-to-End Integration Testing

**Critical Checks:**
- [ ] ALL tests pass (100%)
- [ ] Test coverage ≥90% overall
- [ ] No visual regressions
- [ ] Performance acceptable

**Validation Commands:**
```bash
npm test -- --coverage
npm run test:e2e # if available
npm run benchmark
```

**Comprehensive Testing:**
- Run full pipeline on diverse images
- Test edge cases
- Stress testing with large images
- Browser compatibility testing

**Approval Criteria:**
- ✅ Zero test failures
- ✅ Coverage ≥90%
- ✅ All edge cases handled
- ✅ Performance acceptable

---

#### LOT 6.2: Code Quality & Cleanup

**Critical Checks:**
- [ ] Zero linting errors
- [ ] Zero TypeScript errors in strict mode
- [ ] No dead code
- [ ] Consistent code style

**Validation Commands:**
```bash
npm run lint
tsc --noEmit --strict
# Check for dead code
npx ts-prune # or similar tool
```

**Manual Review:**
- Scan for commented-out code
- Check for console.log statements
- Verify consistent formatting

**Approval Criteria:**
- ✅ Perfect code quality
- ✅ Zero linting/TS errors
- ✅ No dead code

---

#### LOT 6.3: Deployment & Rollout Plan

**Critical Checks:**
- [ ] All documentation updated
- [ ] CHANGELOG.md created
- [ ] Version number updated
- [ ] Release properly tagged

**Validation:**
- Review rollout plan
- Verify deployment documentation
- Check rollback plan

**Approval Criteria:**
- ✅ Ready for deployment
- ✅ All docs updated
- ✅ Rollback plan exists

---

## Decision Matrix

### When to APPROVE ✅
- All critical checks pass
- All tests pass
- Code quality is excellent
- Documentation is clear
- No performance regressions
- Deliverables are complete

### When to REQUEST CHANGES 🔄
- Minor issues that can be quickly fixed
- Missing documentation
- Test coverage slightly below target
- Minor code style issues
- Small performance concerns

### When to REJECT ❌
- Tests fail
- Visual/functional regressions
- Significant performance degradation
- Incomplete deliverables
- Major code quality issues
- Security vulnerabilities
- **LOT 3.3 fails (border tracing) - PROJECT PAUSE REQUIRED**

---

## Validation Report Template

After validating each LOT, add this to `PROJECT_TRACKER.md`:

```markdown
## LOT X.X Validation Report

**Validator:** [Manager Name]
**Date:** [Date]
**Time Spent on Validation:** [Hours]

**Status:** ✅ APPROVED / 🔄 CHANGES REQUESTED / ❌ REJECTED

**What Was Validated:**
- [ ] Code review
- [ ] Tests pass
- [ ] Manual testing
- [ ] Performance check
- [ ] Documentation review

**Issues Found:**
1. [Issue 1]
2. [Issue 2]

**Actions Required:**
- [Action 1]
- [Action 2]

**Overall Assessment:**
[Brief summary of quality, whether it meets requirements, any concerns]

**Approved for Next Stage:** YES / NO
```

---

## Emergency Procedures

### If Critical Bug Found After Approval
1. Immediately mark LOT as 🔴 BLOCKED in tracker
2. Roll back to previous working state
3. Document the bug thoroughly
4. Re-assign to AI Dev for fix
5. Re-validate completely

### If Multiple LOTs Fail Validation
1. Pause project
2. Review process and requirements
3. Consider if specifications need clarification
4. Hold project retrospective
5. Adjust approach if needed

---

**Remember:** Your role as manager is to ensure quality and continuity. When in doubt, request changes rather than approving substandard work. A little extra time for quality now saves massive debugging time later.

---

**Last Updated:** 2025-11-05
**Version:** 1.0
