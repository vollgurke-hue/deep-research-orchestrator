# Validation Framework - Advanced Features

**Version:** 1.0
**Last Updated:** 2025-12-12
**Purpose:** Advanced validation features - Overnight Re-Validation, Automation, State Tracking

**Prerequisites:** Read `validation-framework.md` first

---

## Table of Contents

1. [Overnight Re-Validation System](#1-overnight-re-validation-system)
2. [Validation State Tracking](#2-validation-state-tracking)
3. [Cron Job Setup](#3-cron-job-setup)
4. [Overnight Script Implementation](#4-overnight-script-implementation)
5. [Example Overnight Report](#5-example-overnight-report)

---

## 1. Overnight Re-Validation System

### Concept: Day/Night Workflow

```
┌─────────────── DAY WORKFLOW ───────────────┐
│                                             │
│  1. Fast Model (8B) validates              │
│     → Quick results (2-5 min)              │
│                                             │
│  2. State Updated:                         │
│     validation_state.json tracks:          │
│     - Which files validated                │
│     - When (timestamp)                     │
│     - By which model (8B)                  │
│     - Hash (to detect changes)             │
│                                             │
│  3. You work with Fast Results             │
│     → No waiting!                          │
│                                             │
└─────────────────────────────────────────────┘
                      │
                      │ (evening: 22:00)
                      ▼
┌─────────────── NIGHT WORKFLOW ──────────────┐
│                                             │
│  1. Cron Job starts                        │
│     → Runs automatically                   │
│                                             │
│  2. Check State:                           │
│     - What validated today? (new/changed)  │
│     - Which files need deep re-validation? │
│                                             │
│  3. Deep Model (70B/Mixtral) re-validates  │
│     → Slow but thorough (5-10 min each)    │
│     → Runs overnight (you sleep!)          │
│                                             │
│  4. Compare Results:                       │
│     Fast Report vs Deep Report             │
│     → Extract DIFF (what's NEW?)           │
│                                             │
│  5. Generate Overnight Report:             │
│     "3 new findings from Deep Model"       │
│     → Only shows NEW insights              │
│                                             │
└─────────────────────────────────────────────┘
                      │
                      │ (morning: 08:00)
                      ▼
┌─────────────── MORNING ─────────────────────┐
│                                             │
│  You check: overnight-report.md            │
│                                             │
│  "Deep Model found 3 NEW insights:         │
│   - New blind spot: X                      │
│   - Deeper contradiction: Y                │
│   - Alternative hypothesis: Z"             │
│                                             │
│  → Integrate if useful                     │
│  → Ignore if not relevant                  │
│                                             │
└─────────────────────────────────────────────┘
```

---

### Benefits

**1. Zero Workflow Impact** ✅
- Day: Fast model (2-5 min) → work immediately
- Night: Deep model (5-10 min each) → you sleep
- Morning: Check overnight report → integrate if useful

**2. Incremental Validation** ✅
- Only re-validates new/changed files
- Tracks state (no duplicate work)
- Smart queue prioritization

**3. Diff-Based Findings** ✅
- Compares Fast vs Deep reports
- Shows only NEW insights
- No redundant information

**4. Cost-Effective** ✅
- Uses local models (€0)
- Utilizes overnight compute (free time)
- No cloud API costs

**5. Continuous Improvement** ✅
- Every night: Deeper analysis
- Catches what Fast model missed
- Builds validation history

---

### Time Budget

**Day Workflow:**
- Validation: 2-5 min (fast model)
- Work continues: 0 min wait

**Night Workflow:**
- Per validation: 5-10 min (deep model)
- 2-3 validations/night: 10-30 min total
- You sleep: 0 impact

**Morning:**
- Check overnight report: 5-10 min
- Integrate findings: 10-30 min (if useful)

**Total Impact:** 15-40 min/day (mostly morning review)

---

### Comparison: With vs Without Overnight

**Without Overnight (Day Only):**
```
Day: Fast model (8B) validates → 5 findings
Evening: Done

Total findings: 5
Total time: 3-5 hours (your active time)
```

**With Overnight:**
```
Day: Fast model (8B) validates → 5 findings
Night: Deep model (Mixtral) re-validates → 3 NEW findings
Morning: Review overnight report → integrate useful ones

Total findings: 8 (60% more!)
Total time: 3-5 hours (your active time) + overnight (free)
```

**ROI:** +60% findings, +0 active time

---

## 2. Validation State Tracking

### File: validation_state.json

**Location:** `2-working-state/validation_state.json`

**Purpose:** Track all validations, enable incremental overnight re-validation

---

### Structure

```json
{
  "meta": {
    "last_updated": "2025-12-12T18:30:00Z",
    "total_validations": 12,
    "models_used": ["dolphin-llama3:8b", "qwen2.5:14b", "dolphin-mixtral:8x7b"]
  },

  "validations": [
    {
      "id": "val_001",
      "timestamp": "2025-12-12T14:30:00Z",
      "type": "category",
      "target": "0-base-research/1-technical-feasibility/",
      "files": [
        "tech-stack.md",
        "architecture.md",
        "performance.md",
        "hardware.md",
        "timeline.md"
      ],
      "file_hashes": {
        "tech-stack.md": "a1b2c3d4...",
        "architecture.md": "e5f6g7h8...",
        "performance.md": "i9j0k1l2...",
        "hardware.md": "m3n4o5p6...",
        "timeline.md": "q7r8s9t0..."
      },
      "model": "dolphin-llama3:8b",
      "model_version": "8b-q6",
      "report": "research-data/validations/category1/validation-report-20251212-1430.md",
      "techniques": ["contradiction", "consensus_bias", "blind_spots", "red_flags", "sanity_check"],
      "findings_count": {
        "contradictions": 2,
        "consensus_biases": 2,
        "blind_spots": 3,
        "red_flags": 3,
        "sanity_failures": 2
      },
      "status": "completed",
      "revalidated_by": null,
      "overnight_pending": true
    },

    {
      "id": "val_002",
      "timestamp": "2025-12-12T16:00:00Z",
      "type": "excurse",
      "target": "research-excurse/competitor-failure-analysis.md",
      "files": ["competitor-failure-analysis.md"],
      "file_hashes": {
        "competitor-failure-analysis.md": "u1v2w3x4..."
      },
      "model": "dolphin-llama3:8b",
      "report": "research-data/validations/excurse-competitor/validation-report.md",
      "techniques": ["contradiction", "blind_spots", "premortem", "red_flags"],
      "findings_count": {
        "contradictions": 1,
        "blind_spots": 2,
        "premortem_scenarios": 1,
        "red_flags": 1
      },
      "status": "completed",
      "revalidated_by": null,
      "overnight_pending": true
    },

    {
      "id": "val_003",
      "timestamp": "2025-12-12T17:30:00Z",
      "type": "iteration",
      "target": "2-iterations/I001-architecture-decision.md",
      "files": ["I001-architecture-decision.md"],
      "file_hashes": {
        "I001-architecture-decision.md": "y5z6a7b8..."
      },
      "model": "qwen2.5:14b",
      "report": "research-data/validations/I001/validation-report.md",
      "techniques": ["scenario_analysis", "premortem", "blind_spots", "sanity_check"],
      "findings_count": {
        "bull_case_probability": 0.25,
        "base_case_probability": 0.40,
        "bear_case_probability": 0.35,
        "premortem_scenarios": 1,
        "blind_spots": 3,
        "sanity_failures": 2
      },
      "status": "completed",
      "revalidated_by": null,
      "overnight_pending": false,
      "priority": "critical",
      "reason_no_overnight": "Already used deep model (14B)"
    }
  ],

  "overnight_queue": [
    {
      "validation_id": "val_001",
      "priority": "high",
      "reason": "Category validation, only used fast model (8B)"
    },
    {
      "validation_id": "val_002",
      "priority": "medium",
      "reason": "Excurse, fast model (8B)"
    }
  ],

  "overnight_history": [
    {
      "date": "2025-12-11",
      "validations_rerun": 3,
      "new_findings": 5,
      "report": "research-data/overnight-reports/overnight-report-20251211.md"
    }
  ]
}
```

---

### Key Fields

**Per Validation:**
- `id`: Unique identifier
- `timestamp`: When validation ran
- `type`: category | excurse | iteration
- `target`: What was validated
- `files`: List of files validated
- `file_hashes`: SHA256 hashes (detect changes)
- `model`: Which model used
- `techniques`: Which validation techniques applied
- `findings_count`: Summary of findings
- `overnight_pending`: Should be re-validated overnight?
- `revalidated_by`: Overnight model that re-validated (if done)

**Overnight Queue:**
- Tracks which validations need overnight re-validation
- Prioritized: high → medium → low

**Overnight History:**
- Log of all overnight runs
- Track new findings over time

---

## 3. Cron Job Setup

### Linux/Mac

**Edit crontab:**
```bash
crontab -e
```

**Add line (runs every night at 22:00):**
```bash
0 22 * * * cd /path/to/product-management/tools/validator && python overnight_validator.py --model dolphin-mixtral:8x7b >> overnight.log 2>&1
```

**Alternative: Use Qwen 14B (faster than Mixtral):**
```bash
0 22 * * * cd /path/to/product-management/tools/validator && python overnight_validator.py --model qwen2.5:14b >> overnight.log 2>&1
```

---

### Windows

**Create batch file:** `overnight_validation.bat`

```batch
cd C:\path\to\product-management\tools\validator
python overnight_validator.py --model dolphin-mixtral:8x7b
```

**Setup Task Scheduler:**
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily at 22:00
4. Action: Start program → `overnight_validation.bat`

---

## 4. Overnight Script Implementation

### File: overnight_validator.py

**Location:** `tools/validator/overnight_validator.py`

**Key Functions:**

1. **load_state()**: Load validation_state.json
2. **get_overnight_queue()**: Get validations pending re-validation
3. **check_file_changed()**: Detect if files changed since validation
4. **revalidate()**: Run validator with deep model
5. **compare_reports()**: Compare Fast vs Deep, extract NEW findings
6. **generate_overnight_report()**: Summary report
7. **save_state()**: Update validation_state.json

---

### Script Overview (Pseudocode)

```python
#!/usr/bin/env python3
"""
Overnight Re-Validation Script

Runs automatically (cron job) at night:
1. Checks validation_state.json for new validations
2. Re-validates with deep model (Mixtral/Qwen 14B)
3. Compares Fast vs Deep reports
4. Generates Diff Report (only NEW findings)
5. Updates state

Usage:
  python overnight_validator.py --model dolphin-mixtral:8x7b
  python overnight_validator.py --model qwen2.5:14b --max-validations 5
"""

class OvernightValidator:
    def __init__(self, deep_model, max_validations):
        self.deep_model = deep_model
        self.max_validations = max_validations
        self.state_file = Path("../../2-working-state/validation_state.json")

    def run(self):
        # Load state
        state = self.load_state()

        # Get queue (validations pending overnight)
        queue = self.get_overnight_queue(state)

        if not queue:
            print("No validations pending overnight re-validation")
            return

        # Process queue
        revalidations = []
        for validation in queue:
            # Check if files changed
            changed_files = self.check_file_changed(validation)

            # Re-validate with deep model
            success = self.revalidate(validation)

            if success:
                # Compare reports
                new_findings = self.compare_reports(
                    fast_report=validation['report'],
                    deep_report=f"...overnight/{validation['id']}_deep/validation-report.md"
                )

                revalidations.append({
                    'validation_id': validation['id'],
                    'new_findings': new_findings,
                    'changed_files': changed_files
                })

                # Update state
                validation['revalidated_by'] = {
                    'model': self.deep_model,
                    'timestamp': now(),
                    'new_findings_count': len(new_findings)
                }
                validation['overnight_pending'] = False

        # Generate overnight report
        report = self.generate_overnight_report(date, revalidations)
        save(report, f"overnight-reports/overnight-report-{date}.md")

        # Update state
        state['overnight_history'].append({...})
        self.save_state(state)
```

**Full implementation:** See `tools/validator/overnight_validator.py` (to be created)

---

## 5. Example Overnight Report

### File: overnight-report-2025-12-12.md

```markdown
# Overnight Validation Report - 2025-12-12

**Deep Model Used:** dolphin-mixtral:8x7b
**Validations Re-run:** 2
**Total New Findings:** 5

---

## Summary

### val_001: 0-base-research/1-technical-feasibility/

**Original Model:** dolphin-llama3:8b (fast)
**Files Changed:** None

**New Findings:**
- **blind_spots:** 2 new
- **contradictions:** 1 new (deeper analysis)
- **premortem_insights:** 1 new

**Details:**

#### NEW BLIND SPOT 1: Desktop-Specific Accessibility
- **What:** Nobody mentioned accessibility features (screen readers, keyboard navigation)
- **Why Matters:** Desktop apps must support OS accessibility (EU legal requirement)
- **How to Research:** Check WCAG 2.1 guidelines, Tauri accessibility APIs
- **Action:** Add accessibility to roadmap (Phase 1)

#### NEW BLIND SPOT 2: Cross-Platform Testing Burden
- **What:** Testing on Windows + Mac + Linux = 3x effort
- **Why Matters:** Solo dev = time constraint, might miss platform-specific bugs
- **How to Research:** Automated testing strategies, CI/CD for multi-platform
- **Action:** Decide: Support all 3 or start with 1 platform?

#### DEEPER CONTRADICTION: Timeline Estimates
- **Fast Model (8B)** found: "3 months vs 6 months" (from AIs)
- **Deep Model (Mixtral)** found: "Actually 4 different estimates: 3mo, 4mo, 6mo, 8mo depending on scope assumptions"
- **Implication:** Need to clarify scope before timeline estimate valid
- **Action:** Define exact MVP scope (features list), then re-estimate

#### NEW PREMORTEM INSIGHT: "App-Store Rejection Risk"
- **Scenario:** App rejected from app stores (Microsoft Store, Mac App Store)
- **Reason:** LLM content generation = "potentially unsafe" (store policy)
- **Probability:** 20-30% (some AI apps rejected)
- **Mitigation:** Research store policies NOW, consider direct distribution
- **Action:** Check Microsoft Store + Mac App Store AI app policies

**Full Report:** `research-data/validations/overnight/val_001_deep/validation-report.md`

---

### val_002: research-excurse/competitor-failure-analysis.md

**Original Model:** dolphin-llama3:8b (fast)
**Files Changed:** None

**New Findings:**
- **other:** 1 new (alternative hypothesis)

**Details:**

#### ALTERNATIVE HYPOTHESIS: "Competitor Failed Due to Paywall Backlash"
- **Fast Model:** Identified API costs + core business conflict
- **Deep Model:** Additional hypothesis: User backlash against paywall
  - Competitor was FREE for 10 years
  - New feature launched as $4/mo (premium only)
  - Reddit/Twitter showed anger: "Making features paid!"
  - Timing: 2024 = many paywalls = user fatigue
- **Implication:** Launch pricing strategy critical
  - Consider: FREE tier with limitations (vs paid-only)
  - Avoid: "Taking away free features" perception
- **Action:** Review pricing strategy, consider generous free tier

**Full Report:** `research-data/validations/overnight/val_002_deep/validation-report.md`

---

## Action Items

Review overnight findings and integrate if useful:

- [ ] Review val_001: 4 new findings
  - [ ] Add accessibility to roadmap (Phase 1)
  - [ ] Decide multi-platform strategy (all 3 or start with 1?)
  - [ ] Define exact MVP scope (for timeline clarity)
  - [ ] Research app store policies for AI apps

- [ ] Review val_002: 1 new finding
  - [ ] Re-evaluate pricing strategy (free tier vs paid-only)
  - [ ] Research paywall backlash cases

---

**Next Overnight Run:** 2025-12-13 at 22:00
**Model:** dolphin-mixtral:8x7b
**Estimated Duration:** 2-3 hours (for 2 validations)
```

---

## Appendix A: When to Use Overnight Validation

### Recommended For:
- ✅ Projects with 10+ validations (enough volume)
- ✅ Multi-week projects (overnight runs accumulate value)
- ✅ High-stakes decisions (extra scrutiny worth it)
- ✅ When you have 8GB+ VRAM (can run Mixtral/Qwen 32B)

### Skip If:
- ❌ Small project (1-2 validations only)
- ❌ Time-sensitive (need results immediately)
- ❌ Low VRAM (<6GB, can't run deep models efficiently)
- ❌ One-off validation (not worth automation setup)

---

## Appendix B: Model Recommendations for Overnight

**For 8GB VRAM:**
1. **Dolphin-Mixtral:8x7b** (Best quality, abliterated)
2. **Qwen2.5:14b** (Faster, still good quality)
3. **Qwen2.5:32b** (Slower but better than Mixtral on some tasks)

**For 16GB+ VRAM:**
1. **Llama3.3:70b** (Excellent reasoning)
2. **Qwen2.5:32b-q5** (Better quantization, faster)

**For 32GB+ VRAM:**
1. **Llama3.3:70b-q5** (Best quality)

---

## Appendix C: Setup Checklist

**Prerequisites:**
- [ ] Main validator setup complete (see validation-framework.md)
- [ ] Fast model installed (dolphin-llama3:8b)
- [ ] Deep/Overnight model installed (dolphin-mixtral:8x7b or qwen2.5:14b)

**Implementation:**
- [ ] Create `validation_state.json` structure
- [ ] Implement `overnight_validator.py` script
- [ ] Test overnight script manually
- [ ] Setup cron job (Linux/Mac) or Task Scheduler (Windows)
- [ ] Monitor first overnight run

**Ongoing:**
- [ ] Check overnight reports each morning
- [ ] Integrate useful findings
- [ ] Track ROI (new findings vs time spent reviewing)
- [ ] Adjust queue priorities based on learnings

---

## Changelog

**v1.0 (2025-12-12)**
- Initial documentation
- Extracted from STATE_TRACKING.md
- Integrated with validation-framework.md

---

**Related Files:**
- `validation-framework.md` - Core validation framework (read first!)
- `tools/validator/overnight_validator.py` - Implementation (to be created)
- `2-working-state/validation_state.json` - State tracking file

---

**Next Steps:**
1. Complete main validation framework first
2. Run 5-10 day validations (get comfortable with workflow)
3. Decide if overnight validation valuable for your project
4. If yes: Implement `overnight_validator.py` + setup cron job
5. Monitor first week of overnight runs, adjust as needed
