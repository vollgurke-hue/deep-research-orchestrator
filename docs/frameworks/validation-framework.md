# Validation Framework

**Version:** 3.0
**Last Updated:** 2025-12-12
**Purpose:** Complete framework for AI-assisted research validation with abliterated local models

---

## Table of Contents

### Part I: Overview
1. [Philosophy & Core Principles](#1-philosophy--core-principles)
2. [Complete Workflow Overview](#2-complete-workflow-overview)
3. [Validation Techniques Matrix](#3-validation-techniques-matrix)

### Part II: Phase-by-Phase Workflows
4. [Phase 0: Base Research (Multi-AI)](#4-phase-0-base-research-multi-ai)
5. [Phase 2: Review + Validation](#5-phase-2-review--validation)
6. [Phase 2.5: Research Excurse](#6-phase-25-research-excurse-optional)
7. [Phase 3: GIST Planning with Validation](#7-phase-3-gist-planning-with-validation)

### Part III: Integration & Usage
8. [Integration Points (When to Use Validator)](#8-integration-points-when-to-use-validator)
9. [Model Strategy (3-Tier)](#9-model-strategy-3-tier)
10. [Setup & Installation](#10-setup--installation)

### Part IV: Guidelines
11. [Decision Tree: Should I Validate?](#11-decision-tree-should-i-validate)
12. [Best Practices](#12-best-practices)
13. [Time Budget & ROI](#13-time-budget--roi)

---

## 1. Philosophy & Core Principles

### Core Idea
Use **abliterated/uncensored local models** (Dolphin-Llama3, Mixtral) to **critically validate** AI-generated research from commercial services (Claude, GPT-4, Gemini).

### Why Abliterated Models?
- ✅ **Brutal Honesty**: No corporate-speak, no "helpful" conditioning
- ✅ **Local Privacy**: No data sent to cloud services
- ✅ **Zero Cost**: Run on your hardware, €0 per validation
- ✅ **Adversarial**: Designed to challenge, not to please

### Key Principles
1. **Sparse Validation**: Don't validate everything - only high-impact, low-confidence decisions
2. **Timeboxed**: Max 1-2 hours per validation (no infinite rabbit holes)
3. **Actionable**: Every validation must produce concrete actions
4. **Multi-Perspective**: Combine commercial AIs (research) + local models (validation)

### The Gap This Fills
Commercial AIs (Claude, GPT-4) have **consensus bias** and **helpfulness conditioning**. Abliterated local models provide **critical second opinion** without these biases.

---

## 2. Complete Workflow Overview

```
Phase 0: Base Research (Multi-AI in ONE Prompt)
├─ Human: Erstellt EINEN großen Prompt (alle 24 Sub-Categories)
├─ Human: Fragt mehrere AIs (Claude, GPT, Gemini)
├─ Claude Code: Strukturiert responses → einzelne Files
└─ Output: Multi-perspective Base Research Files

Phase 2: Review + Validation
├─ Techniques: Contradiction, Consensus Bias, Blind Spots, Red Flags, Sanity Check
├─ Human: Actions basierend auf Validator Findings
└─ Output: VALIDATED Base Research

Phase 2.5: Research Excurse (optional, bei Bedarf)
├─ Techniques: Contradiction, Blind Spots, Premortem, Red Flags
└─ Output: Deep-dive Findings

Phase 3: GIST Framework (Planning)
├─ Techniques: Scenario Analysis (Bull/Bear/Base), Premortem, Blind Spots, Sanity Check
└─ Output: Validated Decisions + MVP Definition
```

**Key Insight**: Validation happens AFTER Multi-AI research, not during. Separation of concerns: research vs critique.

---

## 3. Validation Techniques Matrix

| # | Technique | Phase 0 | Phase 2 (Review) | Phase 2.5 (Excurse) | Phase 3 (GIST/Planning) |
|---|-----------|---------|------------------|---------------------|-------------------------|
| 1 | **Contradiction Detection** | ❌ | ✅✅✅ PRIMARY | ✅✅ if Multi-AI | 🟡 optional |
| 2 | **Consensus Bias Detection** | ❌ | ✅✅✅ PRIMARY | 🟡 bei Bedarf | ❌ not relevant |
| 3 | **Blind Spot Detection** | ❌ | ✅✅✅ PRIMARY | ✅✅✅ CRITICAL | ✅✅ for Questions |
| 4 | **Premortem Analysis** | ❌ | 🟡 Big Picture only | ✅✅✅ PRIMARY (failures) | ✅✅✅ PRIMARY (decisions) |
| 5 | **Red Flags Detection** | ❌ | ✅✅ IMPORTANT | ✅✅ IMPORTANT | 🟡 optional |
| 6 | **Sanity Check** | ❌ | ✅✅ IMPORTANT | ✅✅ for Claims | ✅✅ for Estimates |
| 7 | **Scenario Analysis (Bull/Bear/Base)** | ❌ | 🟡 Strategic only | ❌ | ✅✅✅ PRIMARY |

**Legend:**
- ✅✅✅ PRIMARY = Haupttechnik für diese Phase (immer nutzen)
- ✅✅ IMPORTANT = Sehr wichtig (fast immer nutzen)
- ✅ = Nutzen wenn relevant
- 🟡 = Optional (bei Bedarf)
- ❌ = Nicht anwendbar

### Technique Descriptions

**1. Contradiction Detection**
- **What**: Find where AI responses contradict each other
- **Example**: Claude says "React 45KB", Gemini says "React 140KB"
- **Action**: Research which is correct, update with verified data

**2. Consensus Bias Detection**
- **What**: Challenge what ALL AIs agree on (suspicious unanimity)
- **Example**: All say "React has largest community" → but is that relevant for your use case?
- **Action**: Validate if consensus matters for your specific context

**3. Blind Spot Detection**
- **What**: Find what NOBODY mentions (missing aspects)
- **Example**: All discuss tech stack, none mention HMR performance
- **Action**: Research blind spots, add to analysis

**4. Premortem Analysis**
- **What**: Imagine project failed, why did it fail?
- **Example**: "Local AI failed because quality gap couldn't be closed"
- **Action**: Identify critical assumptions, plan mitigations

**5. Red Flags Detection**
- **What**: Spot warning signals in responses
- **Example**: Vague estimates without breakdown, missing sources for critical claims
- **Action**: Do due diligence on red flags

**6. Sanity Check**
- **What**: Test plausibility of estimates/claims
- **Example**: "3 months MVP" → 480h total → realistic for solo dev?
- **Action**: Correct implausible estimates

**7. Scenario Analysis (Bull/Bear/Base)**
- **What**: Adversarial prompting for strategic decisions
- **Example**: Bull case (optimistic), Bear case (pessimistic), Base case (realistic)
- **Action**: Compare probabilities, choose most likely path

---

## 4. Phase 0: Base Research (Multi-AI)

### Goal
Collect multi-perspective research **efficiently** (ONE big prompt, not 24 small prompts).

### Step 1: Create ONE Big Prompt (alle Categories/Sub-Categories)

**Time**: 30-60 min (one-time creation)

**Template Structure**:
```markdown
# Complete Base Research Prompt - [Your Project]

## Project Context
- Product: [what]
- Approach: [how]
- Target Market: [who]
- Team: [resources]
- Budget: [constraints]

## CATEGORY 1: Technical Feasibility (5 Sub-Categories)
### 1.1 Tech Stack Options
**Question:** [specific question with criteria]
**Output:** [desired format]

### 1.2 Architecture & Data Flow
...

## CATEGORY 2: Market Opportunity (4 Sub-Categories)
...

## CATEGORY 3: Monetization & Economics (4 Sub-Categories)
...

## CATEGORY 4: Legal & Risk (3 Sub-Categories)
...

## CATEGORY 5: Product-User Fit (4 Sub-Categories)
...

## CATEGORY 6: Go-to-Market (4 Sub-Categories)
...

## OUTPUT FORMAT
For EACH sub-category:
1. Executive Summary (2-3 sentences)
2. Key Findings (bullet points)
3. Recommendations (specific, actionable)
4. Confidence Level (HIGH/MEDIUM/LOW + rationale)
5. Sources (if any)
6. Open Questions (what needs clarification?)

## IMPORTANT
- Be specific (numbers, names, examples)
- Be honest about uncertainty
- Cite sources when possible
- Consider trade-offs
- Focus on ACTIONABLE insights
```

**See**: `templates.md` for full prompt template

---

### Step 2: Query Multiple AIs (with ONE Prompt)

**Time**: 20-30 min

**Process**:
1. Copy-paste big prompt into **Claude** → save `claude-complete-research.md`
2. Copy-paste big prompt into **GPT-4** → save `gpt4-complete-research.md`
3. Copy-paste big prompt into **Gemini** → save `gemini-complete-research.md`
4. (Optional) Query **Llama** locally → save `llama-complete-research.md`

**Save in**:
```
2-working-state/research-data/multi-ai-complete/
├── prompt.md
├── claude-complete-research.md
├── gpt4-complete-research.md
├── gemini-complete-research.md
└── llama-complete-research.md (optional)
```

**Benefit**: Only 3-4 free-tier requests (instead of 24×3 = 72 requests!)

---

### Step 3: Structure Responses into Individual Files

**Time**: 2-3 hours (Claude Code assisted)

**Task for Claude Code**:
```
"Parse the Multi-AI responses and structure them into individual Base Research files.

Input:
- research-data/multi-ai-complete/*.md

Output:
- 0-base-research/1-technical-feasibility/tech-stack.md
- 0-base-research/1-technical-feasibility/architecture.md
- ... (all 24 Sub-Categories)

Format per file:
## Executive Summary
[Synthesize all AIs]

## Multi-AI Perspectives
### Claude's Analysis
### GPT-4's Analysis
### Gemini's Analysis

## Synthesis
[Agreement/Disagreement/Conclusion]

## Confidence Level
[HIGH/MEDIUM/LOW based on agreement]

## Open Questions
[What needs validation?]
"
```

**Output Structure**:
```
2-working-state/0-base-research/
├── 1-technical-feasibility/ (5 files)
├── 2-market-opportunity/ (4 files)
├── 3-monetization/ (4 files)
├── 4-legal-risk/ (3 files)
├── 5-product-user-fit/ (4 files)
└── 6-go-to-market/ (4 files)
```

**Total Phase 0 Time**: 3-5 hours (vs 8-14h individual prompting)

---

## 5. Phase 2: Review + Validation

### Validation Techniques Used (5 PRIMARY)

| Technique | Usage | Output |
|-----------|-------|--------|
| **Contradiction Detection** | ✅✅✅ ALWAYS | List contradictions → research |
| **Consensus Bias Detection** | ✅✅✅ ALWAYS | Alternative hypotheses |
| **Blind Spot Detection** | ✅✅✅ ALWAYS | Missing aspects → research |
| **Red Flags Detection** | ✅✅ ALWAYS | Due diligence actions |
| **Sanity Check** | ✅✅ ALWAYS | Correct implausible claims |
| **Premortem Analysis** | 🟡 BIG PICTURE ONLY | Strategic failure scenarios |

---

### Step 1: Category-by-Category Review (Human)

**Time**: 1-2 hours

For each category:
- Read all Sub-Category files
- Note: Contradictions? Open Questions? Low Confidence areas?

---

### Step 2: Run Validator

**Option A: Per Category (Recommended)**

```bash
cd tools/validator

# Category 1: Technical Feasibility
python cli.py validate \
  ../../2-working-state/research-data/multi-ai-complete/prompt.md \
  ../../2-working-state/research-data/multi-ai-complete/ \
  ../../2-working-state/research-data/validations/category1/ \
  --focus "Category 1: Technical Feasibility"

# Repeat for Categories 2-6
```

**Option B: All at Once (faster, but huge report)**

```bash
python cli.py validate \
  ../../2-working-state/research-data/multi-ai-complete/prompt.md \
  ../../2-working-state/research-data/multi-ai-complete/ \
  ../../2-working-state/research-data/validations/complete/
```

**Time**: 2-5 min per category (Fast model) | 5-10 min (Deep model)

---

### Step 3: Analyze Validation Report

**Validator Output Structure**:

```markdown
# Validation Report - Category [X]

## 1️⃣ CONTRADICTIONS DETECTED
**CONTRADICTION 1: [Topic]**
- **AI 1** says: [claim]
- **AI 2** says: [different claim]
- **Severity:** [LOW/MODERATE/HIGH]
- **Implication:** [why it matters]
- **Action:** [what to do]

## 2️⃣ CONSENSUS BIAS DETECTED
**CONSENSUS 1: [What all AIs agree on]**
- **Evidence:** [All 3 AIs mention this]
- **Why suspicious:** [Standard narrative, but is it actually true?]
- **Contrarian view:** [Alternative hypothesis]
- **How to test:** [Validation method]
- **Action:** [Research action]

## 3️⃣ BLIND SPOTS DETECTED
**BLIND SPOT 1: [What nobody mentions]**
- **Category:** [Technical/Market/Risk/etc]
- **Severity:** [CRITICAL/IMPORTANT/MINOR]
- **Why matters:** [Impact on project]
- **How to research:** [Method]
- **Action:** [Specific action]

## 5️⃣ RED FLAGS DETECTED
**RED FLAG 1: [Warning signal]** 🚩🚩
- **Where:** [Which response/claim]
- **Why concerning:** [Risk]
- **Underlying issue:** [Root cause]
- **Due diligence:** [What to investigate]

## 6️⃣ SANITY CHECK
**CLAIM 1: [Estimate or assertion]**
- **Sanity:** [PLAUSIBLE/QUESTIONABLE/IMPLAUSIBLE]
- **Reasoning:** [Why it passes/fails test]
- **Benchmark:** [Comparison to known data]
- **Verdict/Correction:** [Result]

## SUMMARY
**Total Issues Found:** [count per category]
**Recommendation:** [GO/CAUTION/STOP]
**Critical Actions:** [Must-do list before moving forward]
**Confidence After Validation:** [LOW/MEDIUM/HIGH]
```

---

### Step 4: Take Actions (Human)

**Time**: 4-8 hours per category validation

**Action Types**:
1. **Resolve Contradictions**: Research which AI is correct, update with verified data
2. **Challenge Consensus**: Validate if unanimous opinion applies to your context
3. **Research Blind Spots**: Investigate missing aspects
4. **Due Diligence on Red Flags**: Deep-dive on warning signals
5. **Correct Failed Sanity Checks**: Update implausible estimates

**Track in**: `planning_state.json` → `validations_run`

---

### Step 5: Update Base Research

**After actions**, update original files:

```markdown
# In 0-base-research/1-technical-feasibility/tech-stack.md

## VALIDATION FINDINGS (2025-12-12)

**Validator Report:** `research-data/validations/category1/validation-report.md`

**Contradictions Resolved:**
- ✅ Bundle size measured: React 42KB, Vue 30KB, Svelte 12KB
- ✅ Timeline breakdown: 4-5 months realistic (not 3)

**Blind Spots Investigated:**
- ✅ HMR Performance: Tested → all equal (~1-2s)
- ✅ Update strategy: Planned (Tauri auto-updater)

**Consensus Challenged:**
- ✅ React community largest → but Vue more active in Tauri ecosystem

**Red Flags Mitigated:**
- ✅ Performance benchmarks: Measured (35-50 tok/s)
- ✅ Timeline detailed: WBS created

**Updated Scores:**
- React: 28/50 (down, bundle concerns)
- Vue: 35/50 (up, Tauri ecosystem validated)
- Svelte: 30/50 (up, bundle validated)

**Confidence:** LOW → HIGH (after validation)
```

---

### Phase 2 Output
- ✅ Validation Reports (per category or complete)
- ✅ Actions taken (contradictions resolved, blind spots researched)
- ✅ Base Research updated with findings
- ✅ Confidence increased (LOW/MEDIUM → HIGH)

**Total Phase 2 Time**: 6-12 hours

---

## 6. Phase 2.5: Research Excurse (Optional)

### When to Use
- Competitor failures (why did Q-Chat fail?)
- Deep-dive contradictions (conflicting market data)
- Complex trade-offs requiring detailed analysis

### Validation Techniques Used (4)

| Technique | Usage | Output |
|-----------|-------|--------|
| **Contradiction Detection** | ✅✅ if Multi-AI | Resolve conflicts |
| **Blind Spot Detection** | ✅✅✅ ALWAYS | Missing aspects |
| **Premortem Analysis** | ✅✅✅ PRIMARY | Failure scenarios |
| **Red Flags Detection** | ✅✅ IMPORTANT | Warning signals |

---

### Template Workflow

**File**: `2-working-state/research-excurse/TEMPLATE.md`

```markdown
# Research Excurse: [Topic]

**Trigger:** [What discovered during Review?]
**Question:** [Specific question to answer]
**Time Budget:** 1-4 hours

## Step 1: Multi-AI Research (20-30 min)

**Prompt:** [Focused prompt on excurse topic]

**Collect Responses:**
- Claude: `research-data/excurse-[topic]/claude.md`
- GPT-4: `research-data/excurse-[topic]/gpt4.md`
- Gemini: `research-data/excurse-[topic]/gemini.md`

## Step 2: Validator Analysis (5-10 min)

```bash
python tools/validator/cli.py validate \
  research-data/excurse-[topic]/prompt.md \
  research-data/excurse-[topic]/ \
  research-data/validations/excurse-[topic]/ \
  --techniques "contradiction,blind_spots,premortem,red_flags"
```

**Key Findings:**
- Contradictions: [list]
- Blind Spots: [list]
- Premortem: [failure scenario]
- Red Flags: [warnings]

## Step 3: Human Investigation (30-120 min)

**Actions Taken:**
- [ ] Resolved contradiction X
- [ ] Investigated blind spot Y
- [ ] Validated premortem scenario

**Findings:** [What learned]

## Step 4: Implications

**For Base Research:** [Updates needed]
**For Planning:** [Affects which decisions?]

## Recommendation

[Clear actionable recommendation]
```

**Phase 2.5 Time**: 2-8 hours (1-2 excurses per project)

---

## 7. Phase 3: GIST Planning with Validation

### Validation Techniques Used (4)

| Technique | Usage | Output |
|-----------|-------|--------|
| **Scenario Analysis (Bull/Bear/Base)** | ✅✅✅ PRIMARY | Strategic decision analysis |
| **Premortem Analysis** | ✅✅✅ PRIMARY | Decision failure scenarios |
| **Blind Spot Detection** | ✅✅ For Questions | Alternative options |
| **Sanity Check** | ✅✅ For Estimates | Corrected numbers |

### Techniques NOT Used (and why)
- ❌ **Contradiction Detection** - Not applicable (no Multi-AI in iterations)
- ❌ **Consensus Bias** - Not applicable (you're making decisions, not AIs)
- ❌ **Red Flags** - Optional (only if specific decision needs it)

---

### Workflow: GIST + Validation

**For critical Questions/Iterations:**

#### Example: I001 "Local vs Hybrid Architecture?"

**Step 1: Research** (from Base Research)

Link to relevant validated Base Research findings.

---

**Step 2: Adversarial Prompting (Bull/Bear/Base)**

**BULL CASE (Optimistic):**
```
"You are a Local-First advocate. Argue why Local-First is the BEST choice:
- Privacy = Killer feature
- Zero cloud costs = Profitability
- Performance adequate
- Competitive moat

What's the best-case scenario?"
```

**BEAR CASE (Pessimistic):**
```
"You are a Cloud-First advocate. Argue why Local-First is a MISTAKE:
- Quality too low
- Installation friction
- Support burden
- Market too small

What's the worst-case scenario?"
```

**BASE CASE (Realistic):**
```
"Objective analysis: Local-first vs Hybrid vs Cloud-first.

Given:
- [Your specific constraints/data]

What's the most likely outcome?"
```

**Collect**: 3 cases × 3 AIs = 9 responses

---

**Step 3: Run Scenario Analysis Validator**

```bash
python tools/validator/cli.py scenario-analysis \
  research-data/iterations/I001-architecture/bull-case/ \
  research-data/iterations/I001-architecture/bear-case/ \
  research-data/iterations/I001-architecture/base-case/ \
  research-data/validations/I001-architecture/
```

**Validator Output**:
```markdown
## BULL CASE (Optimistic)
- Key assumptions: [list]
- Best outcome: [scenario]
- Probability: [%]

## BEAR CASE (Pessimistic)
- Key assumptions: [list]
- Worst outcome: [scenario]
- Probability: [%]

## BASE CASE (Realistic)
- Key assumptions: [list]
- Expected outcome: [scenario]
- Probability: [%]

## COMPARISON
- Agreement: [what all scenarios see]
- Divergence: [key difference]
- Most realistic: [which case?]
- Critical variable: [what determines outcome?]

## RECOMMENDATION
- Course of action: [decision]
- Risk mitigation: [how to hedge bear case]
- Success factors: [what must be true]
```

---

**Step 4: Premortem Analysis**

```
"It is [Year + 2]. The [Decision] FAILED. Write post-mortem."
```

**Validator Output**:
```markdown
## PREMORTEM: [Decision] Failed

**Failure Description:** [What happened]
**Root Cause:** [Why it failed]
**Ignored Warning Signals:** [What was missed]
**Fundamental Flawed Assumption:** [Critical error in thinking]
**What Should Have Been Done:** [Correct approach]
```

---

**Step 5: Blind Spot Detection (for Question)**

**Validator checks**: "What aspects are missing from this decision analysis?"

**Output**:
```markdown
## BLIND SPOTS

**BLIND SPOT 1: [What wasn't considered]**
- Category: [type]
- Severity: [CRITICAL/IMPORTANT/MINOR]
- Why matters: [impact]
- Action: [what to investigate]
```

---

**Step 6: Sanity Check (Estimates)**

**Validator checks**: "Are these estimates plausible?"

**Output**:
```markdown
## SANITY CHECK

**CLAIM 1: [Estimate]**
- Sanity: [PLAUSIBLE/QUESTIONABLE/IMPLAUSIBLE]
- Reasoning: [why]
- Benchmark: [comparison]
- Verdict/Correction: [result]
```

---

**Step 7: Make Decision (with Validation-Informed Confidence)**

```markdown
## Final Decision: [Your Choice]

**Rationale:** [Why chosen]

**Validation informed decision by:**
- ✅ Scenario Analysis: [insights]
- ✅ Premortem: [risks identified]
- ✅ Blind Spots: [missing aspects found]
- ✅ Sanity Check: [estimates corrected]

**Risk Mitigation:** [How addressing bear case]
**Success Metrics:** [How measuring if working]
```

**Phase 3 Time**: 11-22 hours (validation adds ~30% to GIST process, but prevents failures)

---

## 8. Integration Points (When to Use Validator)

### 4 Strategic Points

```
Phase 0: Base Research
  ├─ Per-Category Validation ← INTEGRATION POINT 1 (sparsam, high-impact only)

Phase 2: Base Research Review
  ├─ Cross-Category Consistency ← INTEGRATION POINT 2 (critical assumptions)

Phase 2.5: Research Excurse (Optional)
  ├─ Deep-Dive Topics ← INTEGRATION POINT 3 (bei Bedarf)

Phase 1/3: Validation Phase / GIST Iterations
  └─ POC/Strategic Decisions ← INTEGRATION POINT 4 (specific hypotheses)
```

---

### Integration Point 1: Base Research (Per-Category Validation)

**When**: AFTER completing a category (all Sub-Categories done)

**Why Sparsam**: Base Research = broad, validating everything = too much effort

**Workflow**:
1. Identify **critical finding** per category (highest impact, lowest confidence)
2. Collect AI responses (3-4 models, same question)
3. Run Validator
4. Take actions (resolve contradictions, research blind spots)
5. Update Base Research
6. Document in `planning_state.json`

**Which Categories to Validate**:
- ✅ **MUST VALIDATE** (High Impact):
  - Category 1: Technical Feasibility (if tech stack unclear)
  - Category 2: Market Opportunity (if market size contradicts)
  - Category 3: Monetization (if pricing unclear)

- ⚪ **SKIP** (Lower Impact):
  - Category 4: Legal & Risk (meist clear: GDPR yes/no)
  - Category 5: Product-User Fit (if personas clear)
  - Category 6: Go-to-Market (if channels obvious)

**→ 2-3 Category Validations per project** (not all 6!)

---

### Integration Point 2: Base Research Review Phase

**When**: AFTER Base Research 100% complete, BEFORE Question Extraction

**What**: Validate **Big Picture Questions** (strategic decisions)

**Workflow**:
1. Identify Big Picture Questions (2-4 per project)
   - Architecture decisions (Local vs Hybrid)
   - Market positioning (Privacy-first vs Cost-leader)
   - Pricing model (Freemium vs Paid-only)

2. Use **Adversarial Prompting** (Bull/Bear/Base cases)

3. Run Validator with all 9 responses (3 cases × 3 AIs)

4. Make Strategic Decision informed by validation

**Which Questions to Validate**:
- ✅ **MUST VALIDATE**:
  - Architecture Decisions
  - Market Positioning
  - Pricing Model

- 🟡 **CAN VALIDATE** (if uncertain):
  - Target Segment (if multiple options)
  - MVP Scope (if unclear what's Must-Have)

- ⚪ **SKIP**:
  - Framework Choice (not strategic enough)

**→ 2-3 Big Picture Validations per Review Phase**

---

### Integration Point 3: Research Excurse (Deep-Dive)

**When**: During Review Phase, when excurse needed

**Triggers**:
- Contradiction between categories
- Competitor failure analysis
- Complex trade-offs needing deep research

**Workflow**:
1. Identify excurse need (e.g., "Why did Q-Chat fail?")
2. Collect hypotheses from AIs
3. Validator finds Contradictions + Blind Spots
4. Research blind spots (manual investigation)
5. Document excurse with validation

**Which Excurses to Validate**:
- ✅ **VALIDATE** (if multiple theories):
  - Competitor failures
  - Technology trade-offs
  - Market hypotheses

- ⚪ **SKIP** (if single clear answer):
  - Factual research (e.g., GDPR requirements)
  - Simple benchmarks (e.g., bundle size - measure yourself)

**→ 1-2 Excurse Validations per project** (sparsam!)

---

### Integration Point 4: Validation Phase / GIST Iterations

**When**: BEFORE or AFTER POC/User Interviews, or for critical GIST iterations

**Use Cases**:

**BEFORE POC:**
- Validate test hypotheses (which metrics? what criteria?)
- Blind Spots in test plan

**AFTER POC:**
- Interpret results (good enough? pivot?)
- Next steps (prompt optimization? model switch?)

**BEFORE User Interviews:**
- Validate interview questions (Blind Spots?)

**AFTER User Interviews:**
- Interpret insights (what do responses mean?)

**Critical GIST Iterations:**
- Strategic decisions (see Integration Point 2 workflow)

**→ 2-4 Validations per Validation Phase / Critical Iterations**

---

### Summary: When to Use Validator

| Phase | Frequency | Purpose | Examples |
|-------|-----------|---------|----------|
| **Base Research (per Category)** | 2-3x per project | Validate critical findings | Tech Stack, Market Size, Pricing |
| **Review Phase (Big Picture)** | 2-3x per project | Validate strategic decisions | Architecture, Positioning |
| **Research Excurse** | 1-2x per project | Deep-dive contradictions | Competitor failures |
| **Validation Phase / Iterations** | 2-4x per project | Hypothesis testing + interpretation | POC, Strategic iterations |

**Total Validations per Project:** ~8-12 (sparsam, fokussiert, high-impact)

**Time Budget per Validation:** 1-2 hours
**Total Validation Time per Project:** 8-24 hours

---

## 9. Model Strategy (3-Tier)

### Overview

```
┌─────────────────────────────────────────────┐
│  TIER 1: PRIMARY (Fast - 90% der Zeit)     │
│  → Dolphin-Llama3:8b                       │
│  → 30-50 tok/s                             │
│  → 2-5 min per report                      │
└─────────────────────────────────────────────┘
                    │
                    │ (if high-priority)
                    ▼
┌─────────────────────────────────────────────┐
│  TIER 2: SECONDARY (Deep - 10% der Zeit)   │
│  → Qwen2.5:14b-instruct                    │
│  → 12-20 tok/s                             │
│  → 5-10 min per report                     │
└─────────────────────────────────────────────┘
                    │
                    │ (overnight only)
                    ▼
┌─────────────────────────────────────────────┐
│  TIER 3: OVERNIGHT (Deepest - nightly)     │
│  → Dolphin-Mixtral:8x7b OR Qwen2.5:32b     │
│  → 5-10 tok/s                              │
│  → 5-15 min per report                     │
└─────────────────────────────────────────────┘
```

---

### Tier 1: PRIMARY - Dolphin-Llama3:8b

**Model:** `dolphin-llama3:8b`
**Size:** 8B parameters (~5GB with Q6 quantization)
**VRAM:** ~6GB (Q6), ~5GB (Q5)
**Speed:** 30-50 tok/s (GPU), 10-15 tok/s (CPU)
**License:** Llama 3 (commercial OK <700M users)

**Features:**
- ✅ Abliterated (brutal honest, no corporate speak)
- ✅ Fast (30-50 tok/s on 8GB VRAM GPU)
- ✅ Quality (good reasoning for 8B)
- ✅ Fits 8GB comfortably
- ✅ Active maintenance (Eric Hartford's Dolphin project)

**Use Cases (90% of time):**
- Base Research Validation (Phase 2)
- Contradiction Detection
- Consensus Bias Detection
- Blind Spot Detection
- Red Flags Detection
- Sanity Checks
- Excurse Validation (Phase 2.5)
- Quick iterations

**Installation:**
```bash
ollama pull dolphin-llama3:8b
```

---

### Tier 2: SECONDARY - Qwen2.5:14b-instruct

**Model:** `qwen2.5:14b-instruct-q4_K_M`
**Size:** 14B parameters (~8GB with Q4)
**VRAM:** ~7-8GB (Q4 required for 8GB VRAM)
**Speed:** 12-20 tok/s (GPU)
**License:** Apache 2.0 (fully open, commercial OK)

**Features:**
- ✅ Better reasoning than 8B models
- ✅ Partially uncensored (less RLHF)
- ✅ Apache 2.0 (no restrictions)
- ⚠️ Tight fit (Q4 quantization required)

**Use Cases (10% of time - high-priority only):**
- Premortem Analysis (strategic decisions)
- Scenario Analysis (Bull/Bear/Base)
- Strategic Decisions (Local vs Hybrid, etc.)
- Second Pass (when Fast Model uncertain)
- Final Validation (before critical decisions)

**When to Use Deep Model:**
```
├─ Impact 9-10/10? → Use Deep
├─ Confidence after Fast < 7/10? → Second pass with Deep
└─ Strategic decision? → Use Deep (better reasoning)
```

**Installation:**
```bash
ollama pull qwen2.5:14b-instruct-q4_K_M
```

---

### Tier 3: OVERNIGHT - Dolphin-Mixtral:8x7b

**Model:** `dolphin-mixtral:8x7b`
**Size:** 8x7B = 47B parameters (~25-30GB with Q4)
**VRAM:** ~8GB (partial offload to RAM)
**Speed:** 5-10 tok/s (GPU + CPU offloading)
**License:** Apache 2.0 (fully open)

**Features:**
- ✅ Best quality for 8GB VRAM setups
- ✅ Abliterated (Dolphin uncensored)
- ✅ Mixtral MoE architecture (efficient)
- ⚠️ Slow on 8GB (needs CPU offloading)

**Alternative: Qwen2.5:32b**
- Similar performance
- Apache 2.0 license
- 3-8 tok/s on 8GB VRAM

**Use Cases (Overnight only):**
- 🌙 Overnight Re-Validation (automatic)
- 🌙 Deep Analysis (while you sleep)
- 🌙 Second opinion (compare Fast vs Overnight)
- 🌙 Final Validation (before MVP launch)

**Installation:**
```bash
# Option 1: Dolphin-Mixtral (recommended)
ollama pull dolphin-mixtral:8x7b

# Option 2: Qwen 32B (alternative)
ollama pull qwen2.5:32b-instruct-q4
```

**Note**: For overnight validation setup, see `validation-advanced.md`

---

### Model Comparison Matrix

| Model | Size | Speed | VRAM | Quality | Uncensored | Use Case |
|-------|------|-------|------|---------|------------|----------|
| **Dolphin-Llama3:8b** | 8B | 30-50 tok/s | 6GB | Good | ✅ YES | PRIMARY (90%) |
| **Qwen2.5:14b** | 14B | 12-20 tok/s | 8GB | Better | 🟡 Partial | HIGH-PRIORITY (10%) |
| **Dolphin-Mixtral:8x7b** | 47B | 5-10 tok/s | 8GB* | Best | ✅ YES | OVERNIGHT |
| **Qwen2.5:32b** | 32B | 3-8 tok/s | 8GB* | Best | 🟡 Partial | OVERNIGHT (alt) |

*With CPU offloading (slower)

---

### Recommended Setup

**Minimal (Start Here)** ✅
```bash
ollama pull dolphin-llama3:8b
```
**Use for**: All validations (fast workflow)

**Recommended (Day + High-Priority)** ✅✅
```bash
ollama pull dolphin-llama3:8b
ollama pull qwen2.5:14b-instruct-q4_K_M
```
**Use for**: Primary (90%) + Secondary (10% strategic)

**Complete (Day + Night)** ✅✅✅
```bash
ollama pull dolphin-llama3:8b
ollama pull qwen2.5:14b-instruct-q4_K_M
ollama pull dolphin-mixtral:8x7b
```
**Use for**: Primary + Secondary + Overnight re-validation

---

### CLI Usage

**Fast Model (Default):**
```bash
python cli.py validate category1/ output/
```

**Deep Model (High-Priority):**
```bash
python cli.py validate category1/ output/ --model deep
```

**Overnight Model (Manual):**
```bash
python cli.py validate category1/ output/ --model overnight
```

**Both (Sequential, compare results):**
```bash
python cli.py validate category1/ output/ --model both
```

---

## 10. Setup & Installation

### Prerequisites
- **Hardware**: 8GB+ RAM, GPU with 6GB+ VRAM (optional but faster)
- **OS**: Linux, macOS, or Windows
- **Python**: 3.8+

---

### Step 1: Install Ollama

```bash
# Linux/Mac
curl -fsSL https://ollama.com/install.sh | sh

# Verify
ollama --version
```

**Windows**: Download from https://ollama.com

---

### Step 2: Pull Models

**Minimal Setup (Start Here)**:
```bash
ollama pull dolphin-llama3:8b
```

**Recommended Setup (Day + High-Priority)**:
```bash
ollama pull dolphin-llama3:8b
ollama pull qwen2.5:14b-instruct-q4_K_M
```

**Verify**:
```bash
ollama list
# Should show: dolphin-llama3:8b (and qwen2.5:14b if installed)
```

---

### Step 3: Test Models

```bash
# Test Fast Model
ollama run dolphin-llama3:8b "Analyze these contradictions: AI 1 says X, AI 2 says Y."

# Test Deep Model (if installed)
ollama run qwen2.5:14b-instruct-q4_K_M "Perform premortem analysis: Project failed, why?"
```

---

### Step 4: Setup Validator (Python)

**Navigate to validator**:
```bash
cd product-management/tools/validator
```

**Option A: System Packages (Debian/Ubuntu)**:
```bash
sudo apt install python3-flask python3-livereload
```

**Option B: Virtual Environment (Recommended)**:
```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

pip install flask livereload
```

---

### Step 5: Verify Setup

```bash
# Check if validator can connect to Ollama
python -c "import requests; print(requests.get('http://localhost:11434/api/tags').json())"
# Should show list of models
```

---

### Step 6: Run First Validation (Test)

**Create test files**:
```bash
mkdir -p test-validation
echo "Test question: Which is better, A or B?" > test-validation/question.md
echo "Claude says: A is better because..." > test-validation/claude.md
echo "GPT says: B is better because..." > test-validation/gpt.md
```

**Run validator**:
```bash
python cli.py validate \
  test-validation/question.md \
  test-validation/ \
  test-validation/output/
```

**Check output**:
```bash
cat test-validation/output/validation-report-*.md
# Should show contradictions detected!
```

---

### Troubleshooting

**Issue: "Ollama not running"**
```bash
# Start Ollama daemon
ollama serve
```

**Issue: "Out of Memory with Qwen 14B"**
```bash
# Use Q3 instead of Q4
ollama pull qwen2.5:14b-instruct-q3_K_M
```

**Issue: "GPU not detected"**
```bash
# Check GPU
nvidia-smi  # NVIDIA
rocm-smi    # AMD

# Check Ollama GPU usage
ollama ps
```

---

## 11. Decision Tree: Should I Validate?

```
START: Should I use Validator for this topic?

├─ Is it HIGH IMPACT (9-10/10)?
│  ├─ YES → Continue
│  └─ NO → SKIP (don't validate low-impact decisions)
│
├─ Is CONFIDENCE LOW/MEDIUM (<8/10)?
│  ├─ YES → Continue
│  └─ NO → SKIP (high confidence = no need)
│
├─ Are there MULTIPLE OPTIONS/THEORIES?
│  ├─ YES → Continue
│  └─ NO → SKIP (single clear answer = no need)
│
├─ Do AI RESPONSES DIFFER?
│  ├─ YES → VALIDATE ✅
│  └─ NO → MAYBE (use if strategically critical)
```

---

### Examples

**VALIDATE ✅:**
- Architecture Decision (High Impact + Low Confidence + Multiple Options)
- Market Positioning (High Impact + Multiple Theories)
- POC Results Interpretation (High Impact + Different AI opinions)

**SKIP ❌:**
- GDPR Requirements (Low Impact for local-first + High Confidence + Single Answer)
- Bundle Size (Can measure yourself faster than validation)
- Framework naming conventions (Low Impact)

---

## 12. Best Practices

### Do's ✅

✅ **Validate HIGH IMPACT decisions** (9-10/10) mit LOW CONFIDENCE (<8/10)

✅ **Timebox validations** (max 1-2h, nicht Tage)

✅ **Use Adversarial Prompting** für Big Picture Questions (Bull/Bear/Neutral)

✅ **Dokumentiere Actions** nach Validation (was hast du getan?)

✅ **Update Base Research** mit Findings

✅ **Track in planning_state.json** (validation history)

✅ **Use Fast Model first** (90% of time), Deep Model nur wenn nötig

---

### Don'ts ❌

❌ **Nicht alles validieren** (sparsam = 8-12 Validations pro Projekt, nicht 50)

❌ **Nicht ohne Follow-up** (Validation ohne Actions = wertlos)

❌ **Nicht nur 1 AI** (minimum 3 für gute Contradictions)

❌ **Nicht bei Low Impact** (<7/10 Impact = skip validation)

❌ **Nicht wenn Zeit fehlt** (Validation braucht 1-2h - wenn du nur 15 min hast, skip it)

❌ **Nicht Validator reports ignorieren** (wenn du validated, dann auch Findings umsetzen!)

---

## 13. Time Budget & ROI

### Time Investment

| Phase | Validations | Time per Validation | Total Time |
|-------|-------------|---------------------|------------|
| **Base Research (Categories)** | 2-3 | 1-2h | 2-6h |
| **Review Phase (Big Picture)** | 2-3 | 1-2h | 2-6h |
| **Research Excurse** | 1-2 | 2-4h | 2-8h |
| **Validation Phase / Iterations** | 2-4 | 1-2h | 2-8h |
| **TOTAL** | **8-12** | - | **8-28h** |

**Total Validation Time per Project**: 8-28 hours (spread across all phases)

**Total Project Time with Validation**: 30-75 hours (Base Research + Validation + Planning)

---

### ROI Analysis

**Without Validation:**
- Risk: 2-5 wrong decisions (Architecture, Market, Pricing)
- Cost per wrong decision: €1K-10K (time wasted, pivot costs)
- Total Risk: €2K-50K

**With Validation:**
- Time Investment: 8-28 hours
- Cost: €0 (local models) + 8-28h time
- Prevented failures: 1-3 critical decisions saved
- Value: €5K-30K (conservative estimate)

**ROI**: ~10-50x return on time invested

---

### Success Metrics

**Short Term (after first validation):**
- ✅ Found contradictions? (at least 1-2)
- ✅ Identified blind spots? (at least 1-2)
- ✅ Took actions? (resolved issues)
- ✅ Updated confidence? (LOW → MEDIUM/HIGH)

**Medium Term (after 5-10 validations):**
- ✅ Prevented 1+ wrong decision
- ✅ Workflow smooth (not experimental)
- ✅ Time per validation < 2h
- ✅ Clear ROI ("This saved me from X mistake")

**Long Term (after project completion):**
- ✅ 10+ validations across all phases
- ✅ Documented learnings (what works, what doesn't)
- ✅ Reusable templates for next project

---

## Appendix A: File Structure

```
product-management/
├── 1-description/
│   ├── validation-framework.md         ← This file
│   ├── validation-advanced.md          ← Overnight re-validation
│   ├── research-framework.md
│   ├── planning-framework.md
│   └── templates.md
│
├── 2-working-state/
│   ├── 0-base-research/               ← Phase 0 output
│   │   ├── 1-technical-feasibility/ (5 files)
│   │   ├── 2-market-opportunity/ (4 files)
│   │   └── ... (6 categories total)
│   │
│   ├── research-data/
│   │   ├── multi-ai-complete/         ← Phase 0 raw responses
│   │   │   ├── prompt.md
│   │   │   ├── claude-complete-research.md
│   │   │   ├── gpt4-complete-research.md
│   │   │   └── gemini-complete-research.md
│   │   │
│   │   ├── validations/               ← All validation reports
│   │   │   ├── category1/
│   │   │   │   └── validation-report-TIMESTAMP.md
│   │   │   ├── category2/
│   │   │   ├── excurse-[topic]/
│   │   │   └── I001-architecture/
│   │   │
│   │   └── overnight-reports/         ← Overnight validation reports
│   │
│   ├── research-excurse/              ← Phase 2.5 output
│   │   └── [topic].md
│   │
│   ├── 2-iterations/                  ← Phase 3 output (GIST)
│   │   └── I001-[question].md
│   │
│   └── planning_state.json            ← Tracks validations
│
└── tools/validator/
    ├── cli.py                         ← Command Line Interface
    ├── validator.py                   ← Core Logic
    ├── prompts.py                     ← Validation Prompts
    ├── config.py                      ← Model Config
    ├── viewer/                        ← Live Viewer
    └── README.md                      ← Tool Documentation
```

---

## Appendix B: Related Files

**Framework Documentation:**
- `research-framework.md` - Phase 0 (Base Research) details
- `planning-framework.md` - Phase 3 (GIST Framework) details
- `templates.md` - All templates (Prompt, Iteration, etc.)
- `validation-advanced.md` - Overnight re-validation system

**Tool Documentation:**
- `tools/validator/README.md` - Validator tool setup & usage
- `tools/validator/DOCS/` - (Will be removed after migration)

**Implementation:**
- `2-working-state/planning_state.json` - Track validation history
- `tools/validator/config.py` - Model configuration

---

## Changelog

**v3.0 (2025-12-12)**
- Consolidated from WORKFLOW_V2_FINAL.md, INTEGRATION_POINTS.md, MODELS_FINAL.md, ROADMAP.md
- Complete framework documentation in one place
- Added Table of Contents for navigation
- Separated advanced features (overnight) to validation-advanced.md

**v2.0 (2025-12-09)**
- Multi-AI in ONE Prompt approach
- 7 Validation Techniques defined
- Integration Points documented
- 3-Tier Model Strategy

**v1.0 (2025-12-08)**
- Initial concept

---

**Next Steps:**
1. Read this framework ✅
2. Setup Ollama + Models (see Section 10)
3. Run first test validation
4. Use in real project (Base Research → Validation → Planning)
5. Iterate based on learnings

---

**For Advanced Features (Overnight Re-Validation):**
See `validation-advanced.md`
