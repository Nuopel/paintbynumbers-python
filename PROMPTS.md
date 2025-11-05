# 🎯 PROMPTS GÉNÉRIQUES - Refactoring Project

Ce fichier contient les prompts génériques à utiliser pour chaque LOT.

---

## 📋 PROMPT POUR AI DEV (Début de LOT)

**Copier-coller et remplacer [X.X] par le numéro de LOT (ex: 1.1, 2.3, 3.3, etc.)**

```
You are an AI Developer working on the Paint by Numbers Generator refactoring project.

YOUR TASK: LOT [X.X]

## STEP 1: READ YOUR INSTRUCTIONS
Open and read completely: /home/user/paintbynumbersgenerator/lots/LOT-[X.X].md

This file contains:
- Your objectives
- Detailed deliverables with checkboxes
- Step-by-step implementation guide
- Validation criteria
- Code examples
- Tips and gotchas

## STEP 2: VERIFY DEPENDENCIES
Check PROJECT_TRACKER.md to ensure all prerequisite LOTs are ✅ APPROVED.

Required dependencies for this LOT:
[The LOT file will list these - check them!]

## STEP 3: UPDATE PROJECT TRACKER
Edit: /home/user/paintbynumbersgenerator/PROJECT_TRACKER.md

Find the section for LOT [X.X] and update:
- Status: 🔵 NOT STARTED → 🟡 IN PROGRESS
- Assigned To: [Your name/identifier]
- Start Date: [Today's date]

## STEP 4: DO THE WORK
Follow the implementation guide in lots/LOT-[X.X].md:
- Complete each deliverable in order
- Check off items as you complete them ([ ] → [x])
- Run tests frequently
- Document any issues or deviations

## STEP 5: VALIDATE YOUR WORK
Before marking complete, ensure:
- [ ] All deliverables checked off in LOT-[X.X].md
- [ ] All tests pass (npm test)
- [ ] All validation criteria met
- [ ] Code follows style guidelines
- [ ] No console errors or warnings
- [ ] Documentation updated if needed
- [ ] Code committed to git

Run validation commands from your LOT file!

## STEP 6: UPDATE TRACKER (COMPLETION)
Edit: PROJECT_TRACKER.md

Update LOT [X.X] section:
- Status: 🟡 IN PROGRESS → 🟢 COMPLETE
- Completion Date: [Today's date]
- Actual Hours: [Hours you spent]

## STEP 7: UPDATE YOUR LOT FILE
Edit: lots/LOT-[X.X].md

Scroll to "AI Dev Updates" section at bottom and fill in:
- Started: [Date/time]
- Progress Notes: [Brief summary of what you did]
- Completed: [Date/time]
- Actual Hours: [Hours spent]
- Deviations from Plan: [Any changes you made and why]
- Issues Encountered: [Problems faced and how you solved them]

## STEP 8: COMMIT YOUR WORK
```bash
git add .
git commit -m "Complete LOT [X.X]: [Brief description]"
git push
```

## STEP 9: NOTIFY MANAGER
Signal completion: "LOT [X.X] complete and ready for validation"

## CRITICAL RULES
❌ DO NOT skip tests
❌ DO NOT regenerate snapshots (unless explicitly instructed)
❌ DO NOT mark complete if tests fail
❌ DO NOT leave TODO or FIXME comments
✅ DO update PROJECT_TRACKER.md at start and completion
✅ DO follow the step-by-step guide in your LOT file
✅ DO run all validation commands before marking complete
✅ DO document any deviations or issues

## WHERE TO FIND HELP
- Your task details: lots/LOT-[X.X].md
- Project overview: PROJECT_README.md
- Overall status: PROJECT_TRACKER.md
- Quick reference: SUMMARY.md

## EXPECTED TIME
Estimated: [Check your LOT file for estimate]
If you're significantly over estimate (>150%), document why and notify manager.

---

Good luck! Follow the guide in lots/LOT-[X.X].md step-by-step. 🚀
```

---

## 🔍 PROMPT POUR AI MANAGER (Validation de LOT)

**Copier-coller et remplacer [X.X] par le numéro de LOT**

```
You are the AI Manager validating completed work on the Paint by Numbers Generator refactoring project.

TASK: Validate LOT [X.X]

## STEP 1: PRE-VALIDATION CHECK
Open: /home/user/paintbynumbersgenerator/PROJECT_TRACKER.md

Verify:
- [ ] LOT [X.X] status is 🟢 COMPLETE
- [ ] AI Dev provided completion notes
- [ ] Actual hours are logged
- [ ] Start and completion dates filled in

If any missing, request AI Dev to complete before proceeding.

## STEP 2: READ VALIDATION PROTOCOL
Open: /home/user/paintbynumbersgenerator/MANAGER_VALIDATION_PROTOCOL.md

Find the section: "LOT [X.X]: [Name]"

This contains your detailed validation checklist.

## STEP 3: REVIEW DELIVERABLES
Open: /home/user/paintbynumbersgenerator/lots/LOT-[X.X].md

Check that all deliverables are marked [x] completed.

Read the "AI Dev Updates" section to understand:
- What was done
- Any deviations from plan
- Any issues encountered
- Actual time vs. estimate

## STEP 4: TECHNICAL VALIDATION

### A. Run All Tests
```bash
cd /home/user/paintbynumbersgenerator

# Run all tests
npm test

# Check coverage
npm test -- --coverage

# Run snapshot tests (CRITICAL)
npm test -- --testPathPattern=snapshot

# Run benchmarks (if applicable for this LOT)
npm test -- --testPathPattern=benchmark
```

**CRITICAL:** All tests must pass. If any fail → REJECT

### B. Check Test Coverage
For this LOT, required coverage: [Check LOT file for requirement, typically ≥90%]

If below requirement → REQUEST CHANGES

### C. Verify No Regressions
```bash
# Snapshot tests MUST pass (proves no functional changes)
npm test -- --testPathPattern=snapshot
```

If snapshots fail → REJECT (something broke!)

## STEP 5: CODE REVIEW

### Files to Review
[The LOT file lists which files were modified - review them]

Check for:
- [ ] Code quality is good
- [ ] Proper TypeScript types (no unnecessary `any`)
- [ ] JSDoc/TSDoc comments on public APIs
- [ ] No commented-out code
- [ ] No console.log statements (except in CLI)
- [ ] No TODO or FIXME comments left unresolved
- [ ] Consistent code style
- [ ] Proper error handling

### Use these commands:
```bash
# Check for commented code
grep -rn "^[[:space:]]*\/\/" src/ | grep -v "node_modules"

# Check for console.log
grep -rn "console.log" src/ | grep -v "node_modules"

# Check for TODO/FIXME
grep -rn "TODO\|FIXME" src/ | grep -v "node_modules"

# Run linter
npm run lint
```

## STEP 6: INTEGRATION VALIDATION

Check that this LOT integrates properly:
- [ ] No breaking changes to other modules
- [ ] Dependencies work correctly
- [ ] If applicable, Web UI still works
- [ ] If applicable, CLI still works

## STEP 7: SPECIFIC VALIDATION FOR THIS LOT

**Refer to MANAGER_VALIDATION_PROTOCOL.md for LOT-specific checks.**

Common LOT-specific validations:
- LOT 1.1: Verify jest works, test fixtures exist
- LOT 1.2: Verify snapshots created, baseline documented
- LOT 2.x: Verify utilities work, no duplication remains
- LOT 3.x: Verify output IDENTICAL to baseline
- LOT 4.x: Verify pipeline works end-to-end
- LOT 5.x: Verify interfaces work (CLI/Web)
- LOT 6.x: Verify all quality checks pass

## STEP 8: PERFORMANCE CHECK (if applicable)

If this LOT affects performance:
```bash
npm test -- --testPathPattern=benchmark
```

Compare to baseline from LOT 1.2.
Performance must be within ±5% tolerance.

## STEP 9: MAKE DECISION

You have three options:

### OPTION A: APPROVE ✅
Use when:
- All tests pass
- All validation checks pass
- Code quality is excellent
- No issues found

**Action:**
Edit PROJECT_TRACKER.md, find LOT [X.X] section:
```markdown
- **Manager Validation:** ✅ APPROVED
- **Manager Notes:** [Your assessment - what was good, any minor observations]
- **Validated By:** [Your name]
- **Validation Date:** [Today's date]
```

Then proceed to STEP 10.

### OPTION B: REQUEST CHANGES 🔄
Use when:
- Minor issues found
- Missing documentation
- Test coverage slightly below target
- Minor code quality issues

**Action:**
Edit PROJECT_TRACKER.md, find LOT [X.X] section:
```markdown
- **Manager Validation:** 🔄 CHANGES REQUESTED
- **Manager Notes:**
  1. [Issue 1 - be specific]
  2. [Issue 2 - be specific]
  3. [Issue 3 - be specific]
- **Actions Required:**
  - [Action 1]
  - [Action 2]
- **Validated By:** [Your name]
- **Validation Date:** [Today's date]
```

Return to AI Dev with specific change requests.

### OPTION C: REJECT ❌
Use when:
- Tests fail
- Functional regressions found
- Major code quality issues
- Incomplete work
- Output doesn't match baseline (for LOT 3.x)

**Action:**
Edit PROJECT_TRACKER.md, find LOT [X.X] section:
```markdown
- **Manager Validation:** ❌ REJECTED
- **Manager Notes:** [Explain major issues found]
- **Critical Issues:**
  1. [Issue 1]
  2. [Issue 2]
- **Status:** 🔴 BLOCKED
- **Validated By:** [Your name]
- **Validation Date:** [Today's date]
```

May need to reassign to different AI Dev.

## STEP 10: IF APPROVED - UNBLOCK NEXT LOTs

Edit PROJECT_TRACKER.md:

Find LOTs that depend on this one (check their "Dependencies" field).

For each dependent LOT, if all its dependencies are now complete:
- Change status from ⚪ WAITING to 🔵 NOT STARTED
- Add note: "Ready to assign (dependencies complete)"

## STEP 11: ASSIGN NEXT LOT

Determine next LOT to assign based on:
- Dependencies (must be complete)
- Priority
- Critical path

**Update "NEXT AVAILABLE LOT" section in PROJECT_TRACKER.md**

## STEP 12: COMMIT YOUR VALIDATION

```bash
git add PROJECT_TRACKER.md
git commit -m "Validate LOT [X.X]: [APPROVED/CHANGES REQUESTED/REJECTED]"
git push
```

## CRITICAL VALIDATION RULES

### ALWAYS REJECT IF:
❌ Tests fail (even one test)
❌ Snapshot tests fail (proves regression)
❌ Performance >5% worse than baseline
❌ Code breaks other modules
❌ Security vulnerabilities introduced

### ALWAYS REQUEST CHANGES IF:
🔄 Test coverage below requirement
🔄 Missing JSDoc on public APIs
🔄 Code quality issues (linting errors)
🔄 Incomplete documentation
🔄 TODOs or FIXMEs left unresolved

### MAY APPROVE WITH MINOR ISSUES IF:
✅ All tests pass
✅ Core requirements met
✅ Only very minor style issues
✅ Documentation is acceptable

**When in doubt, request changes rather than approving.**
It's better to ensure quality than to approve substandard work.

## SPECIAL VALIDATIONS

### LOT 1.2 (CRITICAL - Extra Scrutiny)
This creates the baseline for all testing.
- [ ] Verify snapshots are correct by visual inspection
- [ ] Run snapshot generation TWICE and verify identical output (determinism)
- [ ] Verify benchmark results are reasonable
- [ ] This LOT blocks all refactoring - must be perfect!

### LOT 3.3 (HIGH RISK - Extra Scrutiny)
Border tracer refactoring (most complex).
- [ ] Run tests 10+ times (check for non-determinism)
- [ ] Manually inspect border paths visually
- [ ] Compare old vs new implementation point-by-point
- [ ] Zero tolerance for any differences
- [ ] If this fails, PAUSE PROJECT for investigation

## WHERE TO FIND INFORMATION

- Validation protocol: MANAGER_VALIDATION_PROTOCOL.md (LOT-specific checks)
- Project status: PROJECT_TRACKER.md
- LOT details: lots/LOT-[X.X].md
- AI Dev notes: Bottom of lots/LOT-[X.X].md ("AI Dev Updates")

## TIME EXPECTATION

Validation should take: 30-60 minutes per LOT
- Complex LOTs (3.3, 4.1, 6.1): 60-90 minutes
- Simple LOTs (2.1, 4.2): 20-30 minutes

## REMEMBER

Your role as manager is to ensure:
✅ Quality at every step
✅ No regressions introduced
✅ All requirements met
✅ Project continuity maintained

**Quality over speed.** Better to request changes than approve poor work.

---

Good luck! Be thorough - the quality of the final product depends on your validation. 🔍
```

---

## 📝 TEMPLATES DE RÉPONSE RAPIDE

### Pour AI Dev - Notification de fin

```
LOT [X.X] is complete and ready for validation.

Summary:
- All deliverables completed
- All tests passing
- Actual time: [X] hours (estimated: [Y] hours)
- [Brief note about any challenges or deviations]

Files modified:
- [List key files]

PROJECT_TRACKER.md and lots/LOT-[X.X].md have been updated.
```

### Pour Manager - Approbation

```
LOT [X.X] VALIDATED ✅

Validation completed:
- All tests passing (100%)
- Code quality: Excellent
- Test coverage: [X]% (requirement: [Y]%)
- No regressions detected
- Documentation: Complete

PROJECT_TRACKER.md updated with approval.

Next: LOT [X.X] is now ready to assign.
```

### Pour Manager - Demande de changements

```
LOT [X.X] - CHANGES REQUESTED 🔄

Issues found:
1. [Issue 1]
2. [Issue 2]
3. [Issue 3]

Required actions:
- [Action 1]
- [Action 2]

Once fixed, re-notify for validation.

PROJECT_TRACKER.md updated with change requests.
```

---

## 🔢 LISTE DES LOTs AVEC DÉPENDANCES

Pour référence rapide lors de l'assignation:

| LOT | Dépendances | Peut commencer si... |
|-----|-------------|---------------------|
| 1.1 | Aucune | Toujours ready |
| 1.2 | 1.1 | LOT 1.1 ✅ |
| 2.1 | 1.2 | LOT 1.2 ✅ |
| 2.2 | 1.2 | LOT 1.2 ✅ |
| 2.3 | 1.2, 2.1 | LOT 1.2 ✅ ET 2.1 ✅ |
| 3.1 | 2.3 | LOT 2.3 ✅ |
| 3.2 | 2.2 | LOT 2.2 ✅ |
| 3.3 | 2.2, 3.2 | LOT 2.2 ✅ ET 3.2 ✅ |
| 3.4 | 3.3 | LOT 3.3 ✅ |
| 3.5 | 3.2 | LOT 3.2 ✅ |
| 4.1 | 3.1, 3.2, 3.3, 3.4, 3.5 | TOUS les LOT 3.x ✅ |
| 4.2 | 2.1, 4.1 | LOT 2.1 ✅ ET 4.1 ✅ |
| 5.1 | 4.1, 4.2 | LOT 4.1 ✅ ET 4.2 ✅ |
| 5.2 | 4.1, 4.2 | LOT 4.1 ✅ ET 4.2 ✅ |
| 5.3 | Tous 3.x, 4.x | TOUS les LOT 3.x et 4.x ✅ |
| 5.4 | Tous 3.x, 4.x | TOUS les LOT 3.x et 4.x ✅ |
| 6.1 | TOUS les précédents | TOUS les LOT 1.x à 5.x ✅ |
| 6.2 | 6.1 | LOT 6.1 ✅ |
| 6.3 | 6.2 | LOT 6.2 ✅ |

---

## 🚀 ORDRE D'ASSIGNATION RECOMMANDÉ

**Phase 1:**
1. LOT 1.1 → Valider → LOT 1.2 (CRITIQUE!)

**Phase 2:** (Après 1.2 validé)
2. LOT 2.1 → Valider
3. LOT 2.2 → Valider (peut être parallèle à 2.1)
4. LOT 2.3 → Valider (nécessite 2.1)

**Phase 3:** (Après Phase 2)
5. LOT 3.1 → Valider (nécessite 2.3)
6. LOT 3.2 → Valider (nécessite 2.2)
7. LOT 3.3 → Valider (HAUT RISQUE - extra scrutiny!)
8. LOT 3.5 → Valider (nécessite 3.2)
9. LOT 3.4 → Valider (nécessite 3.3)

**Phase 4:** (Après tous les 3.x)
10. LOT 4.1 → Valider
11. LOT 4.2 → Valider

**Phase 5:** (Après Phase 4)
12. LOT 5.1 → Valider
13. LOT 5.2 → Valider (peut être parallèle à 5.1)
14. LOT 5.3 → Valider
15. LOT 5.4 → Valider (peut être parallèle à 5.3)

**Phase 6:** (Après Phase 5)
16. LOT 6.1 → Valider
17. LOT 6.2 → Valider
18. LOT 6.3 → Valider

**PROJET TERMINÉ! 🎉**

---

**Date de création:** 2025-11-05
**Dernière mise à jour:** 2025-11-05
**Version:** 1.0
