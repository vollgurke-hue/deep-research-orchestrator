# Unified Architecture Concept - Deep Research Orchestrator

**Version**: 2.0 - Vollständige Backend-Frontend Integration
**Datum**: 2026-01-02
**Status**: Konzeptionelle Überarbeitung basierend auf Product Management Pattern

---

## 🎯 Vision

Ein **universelles Research Framework System**, das:
- ✅ Generische Workflows (Base → Excurse → Validation → Synthesis) auf beliebige Domänen anwendet
- ✅ Spezifische Techniques pro Use Case ermöglicht (Product Research, Scientific Research, Competitive Analysis, etc.)
- ✅ Klare Trennung: **Description** (was), **Working State** (wie läuft es), **Output** (Ergebnis)
- ✅ Visuelles GUI zur Framework-Erstellung und Prompt-Komposition

---

## 📊 Das Drei-Schichten-Pattern (aus Product Management übernommen)

### Layer 1: DESCRIPTION (Statisch - "Was soll gemacht werden?")

**Zweck**: Deklarative Definition ohne Execution-Details

**Struktur**:
```
1-description/
├── frameworks/                    # Generelle Framework-Templates
│   ├── product-research.json      # Template für Product Research
│   ├── scientific-research.json   # Template für Scientific Research
│   └── competitive-analysis.json  # Template für Competitive Analysis
│
├── phases/                        # Generische Phasen (4 Universal Patterns)
│   ├── phase-0-base-research.json
│   ├── phase-1-excurse.json       # Gap Refinement Loop
│   ├── phase-2-validation.json
│   └── phase-3-synthesis.json
│
├── workflows/                     # Wiederverwendbare Workflow-Templates
│   ├── research-collection.json   # Parallel Data Collection
│   ├── research-validation.json   # Quality Assurance
│   ├── gap-detection.json         # Identify Missing Info
│   └── synthesis-planning.json    # Consolidation
│
└── techniques/                    # Atomic Prompts (Universal Tools)
    ├── contradiction_check.json
    ├── blind_spots.json
    ├── sanity_check.json
    ├── market_research.json       # Spezifisch: Product Domain
    ├── scientific_review.json     # Spezifisch: Science Domain
    └── ...
```

**Jede Datei enthält**:
```json
{
  "block_id": "unique_identifier",
  "type": "technique|workflow|phase|framework",
  "name": "Human-readable Name",
  "description": "Was macht dieser Block?",
  "category": "market_opportunity|technical_feasibility|...",

  "prompt_template": {
    "context": "...",
    "input": "{placeholder_name}",
    "task": "...",
    "output_format": "...",
    "quality_criteria": ["..."]
  },

  "metadata": {
    "agent_role": "quality_validator",
    "recommended_model": "tier1_fast",
    "temperature": 0.3,
    "max_tokens": 2000
  },

  "exit_criteria": {
    "type": "completion|confidence_threshold|all_complete",
    "threshold": 0.8
  }
}
```

**Generisch vs. Spezifisch**:
- **Generisch**: contradiction_check, blind_spots, sanity_check → Überall anwendbar
- **Spezifisch**: market_research, scientific_review → Domänen-spezifisch

---

### Layer 2: WORKING STATE (Dynamisch - "Wie läuft die Execution?")

**Zweck**: Live-Tracking während der Ausführung

**Struktur**:
```
2-working-state/
├── executions/                    # Eine Execution = Ein Framework Run
│   ├── exec_20260102_143052/      # Timestamp-basiert
│   │   ├── execution_state.json   # Master State
│   │   ├── phase_0_state.json     # Phase-Level State
│   │   ├── workflow_1_state.json  # Workflow-Level State
│   │   └── logs/
│   │       ├── technique_contradiction.log
│   │       └── workflow_validation.log
│   │
│   └── exec_20260102_150234/
│       └── ...
│
└── current_execution.json         # Symlink zu aktueller Execution
```

**execution_state.json**:
```json
{
  "execution_id": "exec_20260102_143052",
  "framework_id": "framework_product_research",
  "started_at": "2026-01-02T14:30:52Z",
  "updated_at": "2026-01-02T14:35:12Z",

  "overall_status": "in_progress",
  "overall_progress": 45,
  "current_phase": "phase_0_base_research",
  "current_step": "Running market_research_collection workflow...",

  "phases": [
    {
      "phase_id": "phase_0_base_research",
      "status": "in_progress",
      "progress": 60,
      "started_at": "2026-01-02T14:30:52Z",
      "updated_at": "2026-01-02T14:35:12Z",
      "current_workflow": "market_research_collection"
    },
    {
      "phase_id": "phase_1_excurse",
      "status": "pending",
      "progress": 0
    },
    // ...
  ],

  "metadata": {
    "total_tokens_used": 12450,
    "total_execution_time_ms": 280000,
    "models_used": ["tier1_fast", "tier2_quality"]
  }
}
```

**Visualisierung im GUI**:
- Live Progress Bar
- Timeline mit Phase-Übergängen
- Current Step Anzeige
- Token/Time Tracking

---

### Layer 3: OUTPUT (Resultat - "Was ist das Ergebnis?")

**Zweck**: Persistierte Ergebnisse nach Completion

**Struktur**:
```
3-output/
├── executions/                    # Archivierte Execution Results
│   ├── exec_20260102_143052/
│   │   ├── final_output.md        # Consolidated Report
│   │   ├── decisions/             # Routing nach Kategorien
│   │   │   ├── technical-decisions.md
│   │   │   ├── market-decisions.md
│   │   │   ├── monetization-decisions.md
│   │   │   ├── legal-risk-decisions.md
│   │   │   ├── product-decisions.md
│   │   │   └── gtm-decisions.md
│   │   ├── confidence_report.json # Alle Confidence Scores
│   │   └── execution_summary.json # Metadata + Stats
│   │
│   └── exec_20260102_150234/
│       └── ...
│
└── templates/                     # Output Templates
    ├── product-mvp-definition.md
    ├── research-report.md
    └── competitive-analysis.md
```

**final_output.md** (Beispiel für Product Research):
```markdown
# Product Research Report

**Framework**: Product Research Framework
**Execution**: exec_20260102_143052
**Completed**: 2026-01-02 15:42:18
**Confidence**: 0.87/1.0

---

## Executive Summary
[Synthesized from Phase 3]

## Technical Feasibility
[Routed from decisions/technical-decisions.md]

## Market Opportunity
[Routed from decisions/market-decisions.md]

## Monetization Strategy
[Routed from decisions/monetization-decisions.md]

## Risk Assessment
[Routed from decisions/legal-risk-decisions.md]

## Product Definition
[Routed from decisions/product-decisions.md]

## Go-to-Market Plan
[Routed from decisions/gtm-decisions.md]

---

## Appendix
- **Validation Results**: See confidence_report.json
- **Identified Gaps**: [Liste aus Phase 1 Excurse]
- **Total Tokens Used**: 45,230
- **Execution Time**: 42min 15sec
```

---

## 🔄 Das 4-Phasen Universal Pattern

### Phase 0: BASE RESEARCH (Parallel Collection)

**Zweck**: Breite, parallele Datensammlung über alle relevanten Kategorien

**Workflow**:
```
Input: Research Question/Topic
  ↓
Parallel Workflows (je nach Framework):
  ├─ market_research_collection
  ├─ tech_feasibility_collection
  ├─ competitor_analysis_collection
  └─ user_needs_collection
  ↓
Output: Raw Research Data (6 categories, 24 sub-categories à la Product Management)
```

**Techniques verwendet**:
- Domain-spezifisch: market_research, tech_analysis, competitor_scan
- Tools: web_scraper, pdf_extractor, search_local_docs

**Exit Criteria**: Alle Workflows complete OR Confidence > 0.7

---

### Phase 1: EXCURSE (Gap Refinement Loop) ⭐ NEU

**Zweck**: Identifizierte Gaps aus Base Research schließen

**Workflow**:
```
Input: Base Research Results + Gaps
  ↓
Gap Detection:
  ├─ blind_spots.json      → Finde fehlende Informationen
  ├─ confidence_scoring    → Bewerte jede Kategorie
  └─ question_extraction   → Extrahiere konkrete Fragen
  ↓
IF gaps_detected AND confidence < threshold:
  ├─ Priorisiere Gaps (RICE Scoring)
  ├─ Für Top 3 Gaps:
  │   └─ Deep Dive Research (targeted collection)
  └─ Loop zurück zu Gap Detection
ELSE:
  → Gehe zu Phase 2
```

**Techniques verwendet**:
- blind_spots (gap detection)
- Domain-spezifische Deep Dive Techniques

**Exit Criteria**: Confidence > 0.8 OR Max 3 Iterations

---

### Phase 2: VALIDATION (Quality Assurance)

**Zweck**: Research validieren, Widersprüche auflösen, Sanity Checks

**Workflow**:
```
Input: Complete Research (Base + Excurse)
  ↓
Sequential Validation:
  ├─ contradiction_check → Finde Widersprüche
  ├─ sanity_check → Reality Check
  ├─ red_flags → Risiken identifizieren
  └─ premortem → "Was könnte schiefgehen?"
  ↓
Output: Validated Research + Confidence Scores
```

**Techniques verwendet**:
- contradiction_check
- sanity_check
- red_flags
- premortem

**Exit Criteria**: Alle Validation Checks passed

---

### Phase 3: SYNTHESIS (Consolidation & Planning)

**Zweck**: Insights konsolidieren, Entscheidungen treffen, Handoff vorbereiten

**Workflow**:
```
Input: Validated Research
  ↓
Synthesis:
  ├─ Extract Key Insights
  ├─ Route Decisions (6 Kategorien)
  ├─ Generate Recommendations
  └─ Create Actionable Plan
  ↓
Output: Final Report (routed by categories)
```

**Techniques verwendet**:
- consensus (find agreement across sources)
- scenario_analysis (explore options)
- decision_router (categorize decisions)

**Exit Criteria**: Final Report generated

---

## 🏗️ Framework Creation Workflow (GUI)

### Schritt 1: Framework Definition (Dashboard)

**User Action**: Klick "Create New Framework"

**GUI Workflow**:
```
┌─────────────────────────────────────────┐
│ Create New Framework                    │
├─────────────────────────────────────────┤
│ Name: [Product Research Framework v2]  │
│ Description: [...]                      │
│ Use Case: [Dropdown: Product|Science|..]│
│ Base Template: [None|Existing]          │
│                                         │
│ [Cancel] [Next: Select Phases]          │
└─────────────────────────────────────────┘
```

**Backend**: Erstellt `config/frameworks/{framework_id}.json`

---

### Schritt 2: Phase Selection (Builder)

**GUI**:
```
Available Phases:           Selected Phases (Order):
┌──────────────────┐       ┌────────────────────────┐
│ ☐ Base Research  │       │ 1. Base Research       │
│ ☐ Excurse        │  →→   │ 2. Excurse             │
│ ☐ Validation     │       │ 3. Validation          │
│ ☐ Synthesis      │       │ 4. Synthesis           │
│ ☐ Custom Phase   │       └────────────────────────┘
└──────────────────┘
        [Drag & Drop to reorder]
```

**Backend**: Aktualisiert `building_blocks` in Framework JSON

---

### Schritt 3: Workflow Composition (Vue Flow Canvas)

**GUI** (per Phase):
```
Phase: Base Research
┌─────────────────────────────────────────┐
│ ┌──────────────┐                        │
│ │ Market       │                        │
│ │ Research     │──┐                     │
│ │ Collection   │  │                     │
│ └──────────────┘  │                     │
│                   ▼                     │
│ ┌──────────────┐ ┌──────────────┐      │
│ │ Tech         │ │ Aggregator   │      │
│ │ Feasibility  │→│              │      │
│ │ Collection   │ └──────────────┘      │
│ └──────────────┘                        │
│                                         │
│ ┌──────────────┐                        │
│ │ Competitor   │                        │
│ │ Analysis     │──┘                     │
│ └──────────────┘                        │
└─────────────────────────────────────────┘

[Add Workflow] [Connect Nodes] [Configure]
```

**Features**:
- Drag Workflows aus Library
- Connect mit Edges (Dependencies)
- Parallel vs. Sequential konfigurieren

**Backend**: Aktualisiert Phase JSON `building_blocks`

---

### Schritt 4: Technique Selection (per Workflow)

**GUI**:
```
Workflow: Market Research Collection

Available Techniques:          Selected (Order):
┌──────────────────────┐       ┌─────────────────┐
│ Universal:           │       │ 1. web_scraper  │
│  ☐ web_scraper       │  →→   │ 2. market_      │
│  ☐ pdf_extractor     │       │    research     │
│  ☐ text_cleaner      │       │ 3. consensus    │
│                      │       └─────────────────┘
│ Domain-Specific:     │
│  ☐ market_research   │
│  ☐ competitor_scan   │
│  ☐ user_interview    │
└──────────────────────┘

[Prompts bearbeiten] [Test Technique]
```

**Backend**: Aktualisiert Workflow JSON `building_blocks`

---

### Schritt 5: Prompt Customization (Template Editor)

**GUI** (TemplatePromptEditor.vue):
```
┌─────────────────────────────────────────┐
│ Technique: market_research              │
│ [📝 Template Mode] [📄 Raw Mode]        │
├─────────────────────────────────────────┤
│ 📋 Context:                             │
│ [You are a market research analyst...]  │
│                                         │
│ 📥 Input:                               │
│ {research_topic}                        │
│ Placeholders: [research_topic] [+Add]   │
│                                         │
│ 🎯 Task:                                │
│ [Research market size, competitors...]  │
│                                         │
│ 📤 Output Format:                       │
│ [Markdown with sections:...]            │
│                                         │
│ ✅ Quality Criteria:                    │
│ - Cite sources                          │
│ - Include numbers                       │
│                                         │
│ 💡 Examples: (optional)                 │
│ [...]                                   │
├─────────────────────────────────────────┤
│ ⚙️ Settings:                            │
│ Category: [market_opportunity ▼]        │
│ Agent Role: [market_researcher]         │
│ Temperature: [0.3] Max Tokens: [2000]   │
│                                         │
│ 🚪 Exit Criteria:                       │
│ Type: [completion ▼] Threshold: [0.8]   │
│                                         │
│ [Save Changes] [Test Prompt]            │
└─────────────────────────────────────────┘
```

**Backend**: PATCH `/api/technique/{id}` → Speichert in `config/techniques/{id}.json`

---

### Schritt 6: Framework Execution (Execution Tab)

**GUI**:
```
┌─────────────────────────────────────────┐
│ Execute Framework                       │
├─────────────────────────────────────────┤
│ Framework: [Product Research v2 ▼]     │
│ Input Topic: [AI Tutoring Platform]     │
│                                         │
│ [▶ Start Execution]                     │
└─────────────────────────────────────────┘

Live Working State:
┌─────────────────────────────────────────┐
│ ▶️ IN PROGRESS                          │
│ ████████████░░░░░░░░ 60%                │
│                                         │
│ Current Phase: Base Research (2/4)      │
│ Current Step: Running market_research...│
│                                         │
│ Timeline:                               │
│ ✅ Base Research    [60%] 12min         │
│ ⏳ Excurse         [0%]  -              │
│ ⏳ Validation      [0%]  -              │
│ ⏳ Synthesis       [0%]  -              │
│                                         │
│ Metadata:                               │
│ Model: tier1_fast | Tokens: 3,240       │
│ Confidence: 0.73 | Time: 12m 34s        │
└─────────────────────────────────────────┘
```

**Backend**:
1. POST `/api/execute/{framework_id}` mit Input
2. Orchestrator startet Master-Worker Execution
3. WebSocket/SSE streamt Working State Updates → GUI
4. Bei Completion: Output wird in `3-output/` gespeichert

---

## 🎨 Frontend-Backend Mapping

### API Endpoints (vollständig)

| Endpoint | Method | Zweck | Request | Response |
|----------|--------|-------|---------|----------|
| `/api/frameworks` | GET | Liste aller Frameworks | - | `{frameworks: [{id, name, path}]}` |
| `/api/framework/:id` | GET | Framework Details | - | Framework JSON |
| `/api/framework` | POST | Neues Framework | Framework JSON | Created Framework |
| `/api/framework/:id` | PATCH | Framework Update | Partial JSON | Updated Framework |
| `/api/framework/:id` | DELETE | Framework löschen | - | Success |
| `/api/phases` | GET | Liste aller Phases | - | `{phases: [...]}` |
| `/api/phase/:id` | GET | Phase Details | - | Phase JSON |
| `/api/phase/:id` | PATCH | Phase Update | Partial JSON | Updated Phase |
| `/api/workflows` | GET | Liste aller Workflows | - | `{workflows: [...]}` |
| `/api/workflow/:id` | GET | Workflow Details | - | Workflow JSON |
| `/api/workflow/:id` | PATCH | Workflow Update | Partial JSON | Updated Workflow |
| `/api/techniques` | GET | Liste aller Techniques | - | `{techniques: [...]}` |
| `/api/technique/:id` | GET | Technique Details | - | Technique JSON |
| `/api/technique/:id` | PATCH | Technique Update | Partial JSON | Updated Technique |
| `/api/execute/:framework_id` | POST | Framework ausführen | `{input: {...}}` | `{execution_id}` |
| `/api/execution/:id/status` | GET | Execution Status | - | Working State JSON |
| `/api/execution/:id/output` | GET | Execution Output | - | Output JSON |
| `/api/orchestrator/reload` | POST | Orchestrator neu laden | - | Success |

---

## 🔧 Generisch vs. Spezifisch - Trennung

### Generische Bausteine (Universal, wiederverwendbar)

**Workflows**:
- research_validation (Quality Checks)
- gap_detection (Blind Spot Analysis)
- synthesis_planning (Consolidation)

**Techniques**:
- contradiction_check
- blind_spots
- sanity_check
- red_flags
- premortem
- consensus
- scenario_analysis

**Verwendung**: In JEDEM Framework anwendbar

---

### Spezifische Bausteine (Domänen-abhängig)

**Product Research**:
- market_research (TAM/SAM/SOM)
- user_needs (JTBD, Pain Points)
- pricing_analysis (Unit Economics)

**Scientific Research**:
- literature_review (Paper Analysis)
- methodology_check (Scientific Method)
- statistical_analysis (P-Values, Confidence Intervals)

**Competitive Analysis**:
- competitor_scan (SWOT, Features)
- market_positioning (Differentiation)
- pricing_strategy (Competitive Pricing)

**Verwendung**: Nur in spezifischem Framework

---

### Wie entscheidet man?

**Faustregel**:
- **Generisch**: Technique fragt NICHT nach Domain-Wissen → Jeder kann es nutzen
- **Spezifisch**: Technique braucht Domain-Kontext → Nur in bestimmten Frameworks sinnvoll

**Beispiel**:
- `contradiction_check`: Generisch (funktioniert bei jedem Text)
- `market_research`: Spezifisch (braucht Business-Kontext)

**GUI-Feature**:
```
Technique Library:
┌──────────────────────────────────────┐
│ 🌍 Universal (7)                     │
│  • contradiction_check               │
│  • blind_spots                       │
│  • sanity_check                      │
│                                      │
│ 🎯 Product Domain (5)                │
│  • market_research                   │
│  • user_needs                        │
│  • pricing_analysis                  │
│                                      │
│ 🔬 Science Domain (3)                │
│  • literature_review                 │
│  • methodology_check                 │
│                                      │
│ [+ Create New Technique]             │
└──────────────────────────────────────┘
```

---

## 📊 Status & Next Steps

### ✅ Was funktioniert bereits

1. **Backend Core**:
   - ✅ Orchestrator (Master-Worker)
   - ✅ 7 Universal Techniques (Schema komplett)
   - ✅ LlamaCppClient (HTTP Integration)
   - ✅ Tool System (@tool decorator)
   - ✅ Framework Loader (Hierarchical)

2. **Frontend Core**:
   - ✅ 4 Main Tabs (Dashboard, Builder, Execution, Docs)
   - ✅ TemplatePromptEditor (Dual Mode)
   - ✅ WorkingStateViewer (Live Progress)
   - ✅ Pinia Store (State Management)

3. **Integration**:
   - ✅ Flask API (CRUD Endpoints)
   - ✅ Vue Router (Tab Navigation)
   - ✅ 7/7 Integration Tests passing

---

### 🚧 Was fehlt noch (Priorität)

#### High Priority (1-2 Tage)

1. **Excurse Phase implementieren**
   - `config/phases/phase_1_excurse.json` erstellen
   - Gap Detection Workflow
   - Iterative Loop Logic

2. **Schema Completion**
   - 4 Workflows aktualisieren (building_blocks)
   - 3 Phases aktualisieren (working_state, output)
   - 1 Framework aktualisieren (global exit_criteria)

3. **Frontend-Backend Sync**
   - Store lädt jetzt vollständige Daten ✅ (gerade gefixt)
   - FrameworkTree zeigt Hierarchie
   - Test: Kann ich ein Framework öffnen und Techniques sehen?

#### Medium Priority (2-3 Tage)

4. **Framework Creation Workflow**
   - "Create New Framework" Button im Dashboard
   - Phase Selection UI
   - Workflow Drag & Drop (Vue Flow)
   - Technique Assignment

5. **Execution Integration**
   - POST `/api/execute/{framework_id}`
   - SSE/WebSocket für Live Updates
   - Working State Streaming

6. **Output Routing**
   - Decision Router (6 Kategorien)
   - Final Report Generator
   - Download/Export Funktionalität

#### Lower Priority (optional)

7. **Advanced Features**:
   - Multi-GPU Support
   - Technique Testing UI
   - Framework Templates Library
   - Execution History Browser

---

## 🎯 Nächste konkrete Schritte

### Schritt 1: Schemas vervollständigen (1-2h)

```bash
# Workflows aktualisieren
python3 update_workflows_schema.py  # Fix für alle Workflows

# Phases aktualisieren
python3 update_phases_schema.py     # Neu erstellen

# Framework aktualisieren
# Manuell: config/frameworks/framework_product_research.json
```

### Schritt 2: Excurse Phase erstellen (2h)

```bash
# Phase JSON erstellen
config/phases/phase_1_excurse.json

# Gap Detection Workflow erstellen
config/workflows/sequential/gap_detection.json

# Techniques zuweisen:
# - blind_spots (existing)
# - confidence_scorer (new)
# - question_extractor (new)
```

### Schritt 3: Frontend testen (1h)

```bash
# Server starten
./start_dev.sh

# Testen:
# 1. Dashboard → Framework klicken
# 2. Builder → Framework Tree sehen
# 3. Technique klicken → Template Editor öffnet
# 4. Prompt ändern → Save → Reload

# Debugging:
# - Browser Console checken
# - Network Tab → API Calls
# - Vue DevTools → Pinia State
```

### Schritt 4: Framework Creation Workflow (3-4h)

```bash
# Vue Flow installieren
cd gui && npm install @vue-flow/core @vue-flow/background @vue-flow/controls

# Components erstellen:
# - FrameworkCreator.vue
# - PhaseSelector.vue
# - WorkflowCanvas.vue
# - TechniqueLibrary.vue

# API erweitern:
# - POST /api/framework
# - DELETE /api/framework/:id
```

---

## 💡 Erkenntnisse aus Product Management Pattern

### Was wir übernehmen

1. **Drei-Schichten-Trennung**:
   - `1-description` → Config JSONs (statisch)
   - `2-working-state` → Execution Tracking (dynamisch)
   - `3-output` → Results (persistiert)

2. **Category-basiertes Routing**:
   - 6 Standard-Kategorien (market, technical, monetization, legal, product, gtm)
   - Decisions werden automatisch in richtige Kategorie geroutet

3. **Question-driven Iterations**:
   - Phase 1 Excurse = Question-driven Gap Refinement
   - RICE Scoring für Prioritisierung
   - Iterative Loops bis Confidence-Threshold

4. **Exit Criteria**:
   - Jede Phase/Workflow/Technique hat klare Exit-Bedingung
   - Confidence Scores steuern Iterations

---

## 📝 Zusammenfassung

**Vision**: Ein universelles, GUI-gesteuertes Research Framework System

**Pattern**:
1. **Description** (Config JSONs) - Was
2. **Working State** (Live Tracking) - Wie
3. **Output** (Results) - Ergebnis

**4 Phasen**: Base → Excurse → Validation → Synthesis

**Generisch vs. Spezifisch**:
- Universal Techniques (überall)
- Domain Techniques (nur spezifisch)

**Workflow**: Framework GUI erstellen → Prompts customizen → Execute → Output routing

**Status**: Backend 80% ✅ | Frontend 60% ✅ | Integration 70% ✅

**Next**: Schemas vervollständigen → Excurse Phase → Frontend Testing → Creation Workflow

---

**Ready to build! 🚀**
