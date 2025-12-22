# Framework Generalization: Multi-Mode Research & Planning Kit

**Version:** 1.0
**Last Updated:** 2025-12-09
**Purpose:** Von "Product Management Kit" zu flexiblem Research & Planning Framework

---

## Executive Summary

**Problem:** Dein aktuelles Kit ist fokussiert auf **Product Development / Business Case**.

**Opportunity:** Der Core-Workflow (Research → Questions → Iterations → Decisions) ist **universal anwendbar**.

**Lösung:** **Multi-Mode Framework** - gleicher Core, verschiedene "Category Sets" für verschiedene Usecases.

---

## Current State: Product Mode (v3.0)

### Struktur

```
1-description/      (Framework Docs - statisch)
2-working-state/    (Research, Iterations, State - dynamisch)
3-output/           (Decisions, MVP Definition - Ergebnisse)
```

### 6 Research Kategorien (Product-spezifisch)

1. **Technical Feasibility** - Can we build it?
2. **Market Opportunity** - Is there a market?
3. **Monetization** - Can we make money?
4. **Legal & Risk** - Can we legally operate?
5. **Product-User Fit** - Do users want it?
6. **Go-to-Market** - How do we reach users?

### Core Workflow (universell!)

```
Research (6 Kategorien, 24 Sub-Categories)
  ↓
Review (Konsistenz, Big Picture)
  ↓
Question Extraction (offene Fragen)
  ↓
GIST Iterations (Question → Decision)
  ↓
Output (Decision Log, Handoff)
```

**Das ist universal!** Nur die 6 Kategorien sind produkt-spezifisch.

---

## Generalization Proposal: Multi-Mode Framework

### Concept

**Gleicher Core Workflow, verschiedene "Category Sets":**

```
Research Framework (Core) ← UNIVERSAL
  ↓
  Mode Selection ← USER WÄHLT
  ├─ Product Mode (aktuelle 6 Kategorien)
  ├─ Research Mode (akademisches Research)
  ├─ Strategy Mode (Business Strategy)
  ├─ Thesis Mode (Thesis/Dissertation)
  └─ Custom Mode (user-defined categories)
  ↓
Question-driven Iterations (GIST) ← UNIVERSAL
  ↓
Decision Log & Output ← UNIVERSAL
```

**Was ändert sich?** Nur die **Category Names + Sub-Categories**.

**Was bleibt gleich?**
- ✅ Research Framework Struktur (0-base, 1-validation, 2-review, etc.)
- ✅ Question Extraction Process
- ✅ GIST Iterations (Goals, Ideas, Strategy, Tasks)
- ✅ RICE Scoring (2 Levels)
- ✅ Decision Router
- ✅ State Tracking (planning_state.json)
- ✅ Templates
- ✅ **Validator** (funktioniert mit ALLEN Modes!)

---

## Mode 1: Product Mode (Current)

**Use Case:** Product Development, Business Case, Startup MVP

**6 Categories:**
1. Technical Feasibility
2. Market Opportunity
3. Monetization
4. Legal & Risk
5. Product-User Fit
6. Go-to-Market

**24 Sub-Categories:** (wie aktuell)

**Output:** MVP Definition, Decision Log, Handoff to Tech

**Example Questions:**
- Q001: "Welches Frontend Framework?"
- Q002: "Local vs Hybrid Architecture?"
- Q006: "Freemium vs Paid-only?"

---

## Mode 2: Research Mode

**Use Case:** Akademisches Research, Literature Review, Thesis

**6 Categories:**

### 1. Literature Review
**Kernfrage:** What is the current state of knowledge?

**Sub-Categories (4):**
- Theoretical Foundations
- Empirical Studies
- Methodological Approaches
- Research Gaps

---

### 2. Research Design
**Kernfrage:** How will we conduct the research?

**Sub-Categories (4):**
- Research Questions & Hypotheses
- Methodology (Quantitative/Qualitative/Mixed)
- Data Collection Methods
- Sampling Strategy

---

### 3. Data & Analysis
**Kernfrage:** How will we analyze the data?

**Sub-Categories (3):**
- Data Sources & Quality
- Analysis Methods
- Validity & Reliability

---

### 4. Findings & Results
**Kernfrage:** What did we discover?

**Sub-Categories (3):**
- Descriptive Results
- Statistical/Thematic Analysis
- Interpretation

---

### 5. Implications
**Kernfrage:** What does this mean?

**Sub-Categories (4):**
- Theoretical Contributions
- Practical Implications
- Limitations
- Future Research Directions

---

### 6. Dissemination
**Kernfrage:** How will we share the findings?

**Sub-Categories (3):**
- Publication Strategy (Journals, Conferences)
- Presentation & Communication
- Knowledge Translation

---

**Example Questions (Research Mode):**
- Q001: "Quantitative or Qualitative methodology?"
- Q002: "Which theoretical framework: X or Y?"
- Q003: "Sample size: 50 or 100 participants?"
- Q004: "Which journals to target for publication?"

**Output:** Research Protocol, Data Analysis Plan, Publication Strategy

---

## Mode 3: Strategy Mode

**Use Case:** Business Strategy, Strategic Planning, Competitive Analysis

**6 Categories:**

### 1. Market Analysis
**Kernfrage:** Where are we competing?

**Sub-Categories (4):**
- Market Structure & Dynamics
- Customer Segments
- Market Trends & Forces
- Market Size & Growth

---

### 2. Competitive Landscape
**Kernfrage:** Who are we competing against?

**Sub-Categories (4):**
- Competitor Analysis (direct, indirect)
- Competitive Positioning
- Barriers to Entry
- Competitive Advantages

---

### 3. Strategic Options
**Kernfrage:** What are our strategic choices?

**Sub-Categories (4):**
- Growth Strategies (Ansoff Matrix)
- Differentiation Strategies
- Cost/Focus Strategies
- Partnership & M&A Options

---

### 4. Resources & Capabilities
**Kernfrage:** What do we have/need?

**Sub-Categories (4):**
- Core Competencies
- Resource Assessment (VRIO)
- Organizational Capabilities
- Resource Gaps

---

### 5. Implementation
**Kernfrage:** How do we execute?

**Sub-Categories (4):**
- Strategic Initiatives (OKRs)
- Roadmap & Timeline
- Resource Allocation
- Change Management

---

### 6. Performance & Risks
**Kernfrage:** How do we measure and mitigate?

**Sub-Categories (3):**
- KPIs & Metrics
- Risk Assessment
- Scenario Planning

---

**Example Questions (Strategy Mode):**
- Q001: "Market entry: Organic growth or Acquisition?"
- Q002: "Differentiation: Cost leader or Premium?"
- Q003: "Resource allocation: Which initiative first?"
- Q004: "KPI priority: Revenue growth or Profitability?"

**Output:** Strategic Plan, OKR Framework, Risk Mitigation Plan

---

## Mode 4: Thesis Mode

**Use Case:** PhD Thesis, Master Thesis, Dissertation

**6 Categories:**

### 1. Research Problem
**Kernfrage:** What is the problem?

**Sub-Categories (3):**
- Problem Statement
- Significance & Motivation
- Research Questions

---

### 2. Theoretical Framework
**Kernfrage:** What theories guide this research?

**Sub-Categories (4):**
- Conceptual Foundations
- Theoretical Models
- Hypotheses/Propositions
- Conceptual Framework

---

### 3. Methodology
**Kernfrage:** How will we investigate?

**Sub-Categories (5):**
- Research Philosophy (Positivism/Interpretivism/etc.)
- Research Design (Experimental/Survey/Case Study/etc.)
- Data Collection
- Data Analysis
- Ethical Considerations

---

### 4. Empirical Work
**Kernfrage:** What did we do?

**Sub-Categories (4):**
- Pilot Studies
- Main Study Execution
- Data Quality Assessment
- Challenges & Adaptations

---

### 5. Findings & Discussion
**Kernfrage:** What did we find and what does it mean?

**Sub-Categories (4):**
- Results (Descriptive & Analytical)
- Discussion (Theory, Literature, Implications)
- Limitations
- Future Research

---

### 6. Contribution & Dissemination
**Kernfrage:** What is the contribution?

**Sub-Categories (3):**
- Theoretical Contribution
- Practical Contribution
- Dissemination Strategy (Publications, Conference)

---

**Example Questions (Thesis Mode):**
- Q001: "Research Philosophy: Positivist or Interpretivist?"
- Q002: "Data Collection: Interviews or Surveys?"
- Q003: "Case Study: Single or Multiple cases?"
- Q004: "Theoretical Contribution: New theory or Theory extension?"

**Output:** Thesis Outline, Research Protocol, Contribution Statement

---

## Mode 5: Custom Mode

**Use Case:** User-definiert für spezielle Anwendungsfälle

**User Interface (CLI/Config):**

```yaml
# custom-mode.yaml

mode_name: "My Custom Research"

categories:
  - name: "Category 1"
    core_question: "What is X?"
    sub_categories:
      - "Sub A"
      - "Sub B"
      - "Sub C"

  - name: "Category 2"
    core_question: "How to Y?"
    sub_categories:
      - "Sub D"
      - "Sub E"

  # ... up to 6 categories

output_docs:
  - "decision-log.md"
  - "decisions-category1.md"
  - "final-report.md"
```

**Use Case Examples:**
- **Due Diligence:** Legal, Financial, Technical, Market, Team, Risks
- **Policy Analysis:** Problem, Stakeholders, Options, Impact, Implementation, Evaluation
- **Technology Evaluation:** Requirements, Options, Testing, Cost, Risk, Decision

---

## Implementation: How to Generalize?

### Option A: Mode Selection at Init

**Workflow:**

```bash
# User starts new project
python init-project.py

> Select Mode:
> 1. Product Mode (Product Development, MVP)
> 2. Research Mode (Academic Research, Thesis)
> 3. Strategy Mode (Business Strategy)
> 4. Thesis Mode (PhD/Master Thesis)
> 5. Custom Mode (Define your own)

> You selected: 2 (Research Mode)

# Creates structure with Research Mode categories:
1-description/
  ├── research-framework.md     (adapted for Research Mode)
  ├── 0-base-research/
  │   ├── 1-literature-review/
  │   ├── 2-research-design/
  │   ├── 3-data-analysis/
  │   ├── 4-findings/
  │   ├── 5-implications/
  │   └── 6-dissemination/
  └── templates.md              (adapted templates)

2-working-state/
  ├── planning_state.json       (mode: "research")
  └── ...

3-output/
  ├── decision-log.md
  ├── decisions-literature.md
  ├── decisions-methodology.md
  └── research-protocol.md
```

---

### Option B: Mode-Agnostic Core + Mode Configs

**Structure:**

```
product-management-kit/        ← Core (mode-agnostic)
├── core/
│   ├── research-framework.md     (generic)
│   ├── planning-framework.md     (generic, GIST)
│   ├── iteration-planning.md     (generic)
│   └── templates/
│       ├── iteration.md          (generic)
│       ├── decision.md           (generic)
│       └── question-backlog.md   (generic)
│
├── modes/
│   ├── product/
│   │   ├── categories.yaml       (6 categories + sub-categories)
│   │   ├── templates.md          (mode-specific)
│   │   └── example-questions.md
│   │
│   ├── research/
│   │   ├── categories.yaml
│   │   ├── templates.md
│   │   └── example-questions.md
│   │
│   ├── strategy/
│   │   └── ...
│   │
│   └── thesis/
│       └── ...
│
└── tools/
    └── validator/                ← Works with ALL modes!
```

**Workflow:**

```bash
# Init project with mode
./init.sh --mode=research

# Reads modes/research/categories.yaml
# Creates 1-description/ with Research categories
# Creates 2-working-state/ structure
# Sets planning_state.json: mode="research"
```

**Benefits:**
- ✅ Core Framework bleibt mode-agnostic (updates benefit all modes)
- ✅ Modes sind modular (einfach neue Modes hinzufügen)
- ✅ User kann Modes switchen (falls Projekt sich ändert)

---

### Option C: Hybrid (Start Simple, Generalize Later)

**Phase 1: Keep Product Mode (now)**
- Current structure bleibt
- Dokumentiere Generalisierungs-Potential (dieses File)

**Phase 2: Add Research Mode (wenn Bedarf)**
- Copy product-management/ → research-kit/
- Ersetze 6 Kategorien
- Test mit echtem Research-Projekt

**Phase 3: Abstract to Core (wenn 2+ Modes validiert)**
- Extrahiere Core Framework
- Migriere zu modes/ Structure
- Beide Modes nutzen gleichen Core

**Benefits:**
- ✅ Kein Premature Generalization
- ✅ Learn from real usage
- ✅ Beide Modes validiert before abstraction

**Recommendation:** **Option C** (start simple, generalize later)

---

## Validator in Multi-Mode Framework

**Good News:** Validator ist **bereits mode-agnostic!**

**Warum?**
- Validator nimmt **Fragen + AI-Responses** als Input
- Validiert **unabhängig vom Kontext** (Product, Research, Strategy, etc.)
- Output: Contradictions, Consensus Bias, Blind Spots, Premortem

**Example (Research Mode):**

**Question:**
```
"Sollten wir qualitative (Interviews) oder quantitative (Survey) Methodik nutzen?"
```

**AI Responses:**
- Claude: "Qualitative für exploratives Research"
- GPT-4: "Quantitative für große Sample Size"
- Gemini: "Mixed Methods für Triangulation"
- Llama: "Qualitative wenn Budget begrenzt"

**Validator Output:**
- **Contradiction:** Sample size Annahmen widersprechen sich
- **Consensus:** Alle sagen "hängt von Research Question ab" (nicht hilfreich)
- **Blind Spot:** Niemand erwähnt Zeitaufwand für Transcription (bei Interviews)
- **Premortem:** "Thesis gescheitert weil Sample zu klein (N=5) für Generalization"

**→ Works perfectly for Research Mode!**

**Same for Strategy Mode, Thesis Mode, Custom Mode.**

**Validator = Universal Research Quality Tool** ✅

---

## Comparison: Modes vs. Single Framework

### Option 1: Keep Single Product Framework ❌

**Pro:**
- ✅ Einfach, fokussiert
- ✅ Keine Komplexität

**Contra:**
- ❌ Nicht nutzbar für andere Usecases (Research, Strategy, etc.)
- ❌ Missed opportunity (Core ist universal!)

---

### Option 2: Generalize Everything ❌

**Pro:**
- ✅ Maximum Flexibilität
- ✅ Ein Framework für alles

**Contra:**
- ❌ Premature Abstraction (ohne real usage)
- ❌ Overhead (user muss alles konfigurieren)
- ❌ Verwirrend (was ist der Default?)

---

### Option 3: Multi-Mode Framework (Hybrid) ✅ RECOMMENDED

**Pro:**
- ✅ Best of both: Fokussiert + Flexibel
- ✅ Product Mode = default (weiterhin)
- ✅ Other Modes = optional (bei Bedarf)
- ✅ Core Framework bleibt gleich (bewährt)
- ✅ Validator works with all modes

**Contra:**
- ⚠️ Mehr Files (modes/ folder)
- ⚠️ Init Script nötig (mode selection)

**→ This is the sweet spot!**

---

## Roadmap: Generalization

### Phase 1: Document (NOW) ✅

- ✅ Schreibe dieses File (framework-generalization.md)
- ✅ Dokumentiere Mode-Konzepte
- ✅ Identifiziere Core vs. Mode-specific Components

**Status:** DONE (dieses File)

---

### Phase 2: Validate Need (Next 3-6 months)

**Trigger:** Du (oder jemand anderes) brauchst ein anderes Mode

**Example Scenarios:**
- "Ich will Master Thesis schreiben" → Thesis Mode
- "Ich analysiere Competitor Strategy" → Strategy Mode
- "Ich mache akademisches Research" → Research Mode

**Action:**
- Copy product-management/ → [new-mode]-kit/
- Ersetze 6 Kategorien mit mode-spezifischen
- Test mit echtem Projekt
- Dokumentiere Learnings

**Exit Criteria:** 2+ Modes erfolgreich genutzt

---

### Phase 3: Abstract Core (when 2+ modes validated)

**Trigger:** 2+ Modes existieren, viel Duplicate Code

**Action:**
- Extrahiere Core Framework:
  ```
  research-planning-kit/
  ├── core/
  ├── modes/
  └── tools/
  ```
- Migriere beide Modes zu modes/ structure
- Schreibe init.sh (mode selection)
- Test both modes

**Exit Criteria:** Beide Modes nutzen gleichen Core, kein Duplicate Code

---

### Phase 4: Community Modes (future)

**Trigger:** Other users wollen eigene Modes

**Action:**
- Custom Mode support (YAML config)
- Mode Registry (community-contributed modes)
- Examples & Documentation

**Exit Criteria:** 5+ Modes verfügbar, community-maintained

---

## Example: Research Mode in Action

### Use Case: Master Thesis

**Topic:** "Impact of Local AI Models on Privacy Perceptions"

**Mode:** Research Mode

---

**Phase 0: Base Research (6 Categories)**

```
2-working-state/0-base-research/
├── 1-literature-review/
│   ├── theoretical-foundations.md
│   ├── empirical-studies.md
│   ├── methodological-approaches.md
│   └── research-gaps.md
│
├── 2-research-design/
│   ├── research-questions.md
│   ├── methodology.md
│   ├── data-collection.md
│   └── sampling.md
│
├── 3-data-analysis/
│   ├── data-sources.md
│   ├── analysis-methods.md
│   └── validity-reliability.md
│
├── 4-findings/
│   ├── descriptive-results.md
│   ├── statistical-analysis.md
│   └── interpretation.md
│
├── 5-implications/
│   ├── theoretical-contributions.md
│   ├── practical-implications.md
│   ├── limitations.md
│   └── future-research.md
│
└── 6-dissemination/
    ├── publication-strategy.md
    ├── presentation.md
    └── knowledge-translation.md
```

---

**Phase 1: Validation (Optional)**

- POC: Pilot survey (N=10)
- Validation: Test survey instrument
- Update: research-design/ with findings

---

**Phase 2: Review Phase + Validator**

**Critical Assumption:** "Survey (N=100) or Interviews (N=20)?"

**Validator Input:**
- Question: "Methodology choice?"
- Claude Response: "Survey for quantification"
- GPT-4 Response: "Interviews for depth"
- Gemini Response: "Mixed methods"
- Llama Response: "Depends on RQ"

**Validator Output:**
- **Contradiction:** Sample size recommendations vary 5x
- **Blind Spot:** Nobody mentioned Transcription time (Interviews = 100+ hours)
- **Premortem:** "Thesis failed because Survey had low response rate (10%), N=10 unusable"

**Action:** Decide Mixed Methods (Survey N=50 + Interviews N=10)

---

**Phase 3: Question Extraction**

```markdown
# question-backlog.md

## 1. Literature Review Questions
- [ ] Q001: Which theoretical framework: TAM or UTAUT?
- [ ] Q002: Literature scope: Last 5 years or 10 years?

## 2. Research Design Questions
- [ ] Q003: Methodology: Survey, Interviews, or Mixed?
- [ ] Q004: Sample: Students or General public?

## 3. Data Analysis Questions
- [ ] Q005: Analysis: Thematic or Grounded Theory?

[... etc]
```

---

**Phase 4: GIST Iterations**

```markdown
# I001: Methodology Choice

**Question:** Survey (N=100), Interviews (N=20), or Mixed Methods?
**Priority:** CRITICAL (RICE 15.0)

## 1. Research
- Relevant: 2-research-design/methodology.md
- Validation: Mixed methods recommended (after Validator)

## 2. Goals
- **Research Goals:** Answer RQ1-3 with sufficient depth + breadth
- **Practical Goals:** Complete in 6 months
- **Quality Goals:** Publishable in Journal

## 3. Ideas (RICE)
| Idea | Reach | Impact | Confidence | Effort | RICE |
|------|-------|--------|------------|--------|------|
| Survey (N=100) | 10 | 7 | 8 | 4 | 14.0 |
| Interviews (N=20) | 6 | 9 | 7 | 8 | 4.73 |
| Mixed (N=50+10) | 9 | 10 | 8 | 6 | 12.0 ✅ |

## 4. Strategy
- Mixed Methods: Survey (N=50) for breadth → Interviews (N=10) for depth
- Sequential Explanatory Design

## 5. Roadmap
- Month 1-2: Survey design + pilot
- Month 3: Survey execution
- Month 4: Survey analysis → Identify interview candidates
- Month 5: Interviews
- Month 6: Integration + Write-up

## 6. Metrics
- Survey response rate: >40%
- Interview saturation: Achieved by N=8-10
- Data quality: >90% complete responses

## 7. Decision (D001)
**Answer:** Mixed Methods (Survey N=50 + Interviews N=10)
**Rationale:** Validator + Pilot showed need for both depth + breadth
```

---

**Phase 5: Output**

```
3-output/
├── decision-log.md
├── decisions-methodology.md
├── decisions-literature.md
├── research-protocol.md        ← NEW (Thesis-specific)
└── thesis-outline.md           ← NEW (Thesis-specific)
```

**→ Same Framework, Different Categories, Same Value!**

---

## Key Insights

### 1. Core Workflow is Universal ✅

```
Research → Review → Questions → Iterations → Decisions
```

**Works for:**
- Product Development ✅
- Academic Research ✅
- Business Strategy ✅
- Thesis Writing ✅
- Due Diligence ✅
- Policy Analysis ✅
- Technology Evaluation ✅

---

### 2. Only Categories Change

**Product Mode:** Technical, Market, Monetization, Legal, Product, GTM

**Research Mode:** Literature, Design, Data, Findings, Implications, Dissemination

**Strategy Mode:** Market, Competition, Options, Resources, Implementation, Performance

**→ Same structure (6 categories, ~20-25 sub-categories), different names/focus**

---

### 3. Validator is Mode-Agnostic ✅

**Works for ALL modes** because it validates:
- Contradictions (universal)
- Consensus Bias (universal)
- Blind Spots (universal)
- Premortem (universal)

**→ No changes needed for Validator code!**

---

### 4. Templates Adapt Easily

**Generic Template:**
```markdown
# [Category] / [Sub-Category]: Base Research

**Key Findings:**
- Finding 1
- Finding 2

**Implications:**
- For [Outcome X]
- For [Outcome Y]
```

**Product Mode:**
- Outcome X = Product Features
- Outcome Y = GTM Strategy

**Research Mode:**
- Outcome X = Research Design
- Outcome Y = Data Collection

**→ Same structure, different content!**

---

## Decision: Should You Generalize?

### If YES (later):

**When:**
- You need another mode (Research, Strategy, Thesis)
- Product Mode is proven (works well)
- You have time to abstract (1-2 days)

**How:**
- Start with Option C (Hybrid)
- Copy product-management/ → [new-mode]-kit/
- Replace 6 categories
- Test with real project
- Abstract to Core when 2+ modes validated

**Benefit:**
- ✅ One framework, multiple usecases
- ✅ Validator works everywhere
- ✅ Less maintenance (core updates benefit all)

---

### If NO (for now):

**When:**
- Product Mode is all you need
- No other usecases on horizon
- Focus on using, not building

**How:**
- Keep current structure
- Keep this file for reference
- Generalize when need arises

**Benefit:**
- ✅ Simple, focused
- ✅ No premature abstraction
- ✅ Can generalize anytime (core is already universal)

---

## Recommendation

**SHORT-TERM (now):**
- ✅ Keep Product Mode as-is
- ✅ Document generalization potential (this file)
- ✅ Integrate Validator (mode-agnostic anyway)
- ✅ Use Product Mode for AI Tutoring project

**MEDIUM-TERM (3-6 months):**
- 🔄 If you need another mode (e.g., Research for Master Thesis)
- 🔄 Copy → Adapt → Test
- 🔄 Validate that core workflow transfers

**LONG-TERM (6-12 months):**
- 📅 If 2+ modes exist and work well
- 📅 Abstract to Core + Modes structure
- 📅 Write init.sh for mode selection
- 📅 Document all modes

**→ Hybrid Approach (Option C)** = Best balance of simplicity + flexibility

---

## Summary

**Question:** Sollte man von "business case" auf generellere Usecases anpassen?

**Answer:** Ja, aber **Hybrid Approach:**

1. ✅ **Core Workflow ist bereits universal** (Research → Questions → Iterations → Decisions)
2. ✅ **Nur Kategorien sind produkt-spezifisch** (6 Kategorien ändern sich je nach Mode)
3. ✅ **Validator funktioniert mit ALLEN Modes** (keine Änderungen nötig)
4. ✅ **Start Simple:** Keep Product Mode, generalize when you need another mode
5. ✅ **Multi-Mode Support möglich:** Product, Research, Strategy, Thesis, Custom

**Next Steps:**
1. Keep Product Mode as default
2. Use it for AI Tutoring project
3. When you need another mode → Copy, adapt, test
4. When 2+ modes proven → Abstract to Core

**Benefits:**
- No premature abstraction
- Framework validated before generalization
- Maximum flexibility when needed
- Minimal complexity until needed

---

**Related Files:**
- research-validator-integration.md (Validator works with all modes)
- research-framework.md (current Product Mode)
- planning-framework.md (universal GIST process)

**Questions?** Ask Claude Code for implementation help when ready to generalize.
