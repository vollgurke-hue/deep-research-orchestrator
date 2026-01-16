# Documentation Cleanup Plan

**Datum:** 2026-01-15
**Grund:** Vorbereitung für Cluster 1 Implementation
**Strategie:** Archivieren statt Löschen (für Historie)

---

## Kategorisierung (37 Docs)

### ✅ KEEP (11 Docs) - Aktiv & Relevant

**Neu erstellt (SRO-Projekt):**
- `GEMINI_REVIEW_RESULTS.md` (14K) - Review & Design-Entscheidungen
- `IMPLEMENTATION_ANALYSIS_MAPPING.md` (28K) - Bestandsaufnahme & Mapping
- `IMPLEMENTATION_GUIDE_CLUSTER_1.md` (17K) - Detaillierte Anleitung für Cluster 1
- `MASTER_IMPLEMENTATION_PROMPT.md` (15K) - 5-Cluster Roadmap
- `concepts/` (9 Dateien) - Alle Konzept-Dokumente
- `ARCHIVED_TODOS_2026-01-15.md` (3.3K) - Archiv der Seed Graph TODOs

**Technische Referenz (behalten):**
- `API_V2_UNIFIED_ENDPOINTS.md` (11K) - API-Dokumentation
- `COVERAGE_MCTS_INTEGRATION.md` (12K) - Relevant für MCTS
- `CONTEXT_WINDOW_MONITORING.md` (20K) - Nützlich für RLM
- `MULTI_GPU_TESTING_PLAN.md` (6.6K) - Nützlich für Model-Setup
- `TRANSFER_CHECKLIST.md` (19K) - Nützlich als Checkliste

---

### 📦 ARCHIVE (26 Docs) - Veraltet oder Redundant

#### Implementation Snapshots (veraltet)
- `IMPLEMENTATION_COMPLETE_2026-01-02.md` (7.7K)
- `IMPLEMENTATION_COMPLETE_2026-01-10.md` (40K)
- `IMPLEMENTATION_COMPLETE_2026-01-11.md` (5.8K)
- `TODO_NEXT_SESSION.md` (11K)
→ **Grund:** Veraltet, durch neue Roadmap ersetzt

#### Alte Implementation Guides (ersetzt)
- `IMPLEMENTATION_GUIDE.md` (25K)
- `IMPLEMENTATION_ROADMAP.md` (27K)
→ **Grund:** Ersetzt durch MASTER_IMPLEMENTATION_PROMPT + CLUSTER_1

#### Alte Schemas (integriert oder ersetzt)
- `SEED_GRAPH_SCHEMA.md` (21K) - Bereits in UnifiedSession integriert
- `VALUE_GRAPH_SCHEMA.md` (23K) - Ersetzt durch SPO-Konzept
- `WORKING_STATE_TIMELINE_SCHEMA.md` (19K) - Veraltet
→ **Grund:** In neues Datenmodell integriert

#### Alte Konzepte (ersetzt durch SRO-Konzepte)
- `THEMATIC_WORKFLOWS_CONCEPT.md` (20K)
- `UNIFIED_ORCHESTRATOR_CONCEPT.md` (12K)
→ **Grund:** Ersetzt durch SRO_ARCHITECTURE_OVERVIEW

#### Frontend-Docs (verschieben zu gui/)
- `FRONTEND_TODO.md` (13K)
- `FRONTEND_REDESIGN_BRIEF.md` (9.3K)
- `FRONTEND_DEPENDENCY_REPORT.md` (4.8K)
- `VUE_GUI_IMPLEMENTATION_GUIDE.md` (14K)
- `UNIFIED_DASHBOARD_V2.md` (20K)
→ **Grund:** Gehören zu gui/ Subprojekt, nicht root docs/

#### Analyse-Docs (veraltet)
- `ANALYSIS_SUMMARY.md` (6.7K)
- `BACKEND_CONSOLIDATION_PLAN.md` (5.1K)
- `INTEGRATION_ANALYSIS.md` (14K)
- `MIGRATION_PLAN.md` (7.3K)
- `NODE_BASED_PIPELINE_ANALYSIS.md` (50K)
- `README_ANALYSIS.md` (8.2K)
- `UNIFICATION_PROGRESS.md` (11K)
- `WORKFLOW_ANALYSIS_AND_UNIFICATION.md` (37K)
→ **Grund:** Analyse aus alten Planungsphasen, nicht mehr relevant

#### Workflow-Docs (veraltet)
- `RESEARCH_CREATION_WORKFLOW.md` (26K)
- `RESPONSE_COLLECTION_WORKFLOW.md` (15K)
- `PROMPT_BASED_RESEARCH_GENERATOR.md` (26K)
→ **Grund:** Alte Workflows, durch SRO-Konzepte ersetzt

#### Sonstiges
- `GEMINI_PROMPT.md` (2.0K) - Veraltet, war für initiales Prompting

---

## Neue Struktur (nach Cleanup)

```
docs/
├── README.md (NEU ERSTELLEN - Navigation)
│
├── concepts/  (9 Dateien - SRO Konzepte)
│   ├── README.md
│   ├── SRO_ARCHITECTURE_OVERVIEW.md
│   ├── XOT_GENERATIVE_COT_CONCEPT.md
│   ├── SPO_KNOWLEDGE_GRAPH_CONCEPT.md
│   ├── CONSTITUTIONAL_AI_AXIOM_CONCEPT.md
│   ├── RECURSIVE_LLM_CONCEPT.md
│   ├── REDDIT_VALIDATION_CONCEPT.md
│   ├── BIAS_MAPPING_STRATEGY.md
│   ├── EPISTEMIC_MCTS_CONCEPT.md
│   └── PRIVACY_HARDENING_CONCEPT.md
│
├── implementation/  (NEU - Active Implementation Docs)
│   ├── MASTER_IMPLEMENTATION_PROMPT.md
│   ├── IMPLEMENTATION_ANALYSIS_MAPPING.md
│   ├── GEMINI_REVIEW_RESULTS.md
│   ├── IMPLEMENTATION_GUIDE_CLUSTER_1.md
│   └── (später: CLUSTER_2, CLUSTER_3, ...)
│
├── reference/  (NEU - Technical Reference)
│   ├── API_V2_UNIFIED_ENDPOINTS.md
│   ├── COVERAGE_MCTS_INTEGRATION.md
│   ├── CONTEXT_WINDOW_MONITORING.md
│   ├── MULTI_GPU_TESTING_PLAN.md
│   └── TRANSFER_CHECKLIST.md
│
└── archive/  (NEU - Old/Deprecated Docs)
    ├── 2026-01-15-cleanup/  (heute's Archivierung)
    │   ├── implementation-snapshots/
    │   ├── old-guides/
    │   ├── old-schemas/
    │   ├── old-concepts/
    │   ├── frontend-docs/
    │   ├── analysis-docs/
    │   └── workflow-docs/
    └── ARCHIVED_TODOS_2026-01-15.md (bereits archiviert)
```

---

## Durchführungsplan

### Step 1: Archiv erstellen
```bash
mkdir -p docs/archive/2026-01-15-cleanup/{implementation-snapshots,old-guides,old-schemas,old-concepts,frontend-docs,analysis-docs,workflow-docs}
```

### Step 2: Dateien verschieben
```bash
# Implementation Snapshots
mv docs/IMPLEMENTATION_COMPLETE_2026-01-*.md docs/archive/2026-01-15-cleanup/implementation-snapshots/
mv docs/TODO_NEXT_SESSION.md docs/archive/2026-01-15-cleanup/implementation-snapshots/

# Old Guides
mv docs/IMPLEMENTATION_GUIDE.md docs/archive/2026-01-15-cleanup/old-guides/
mv docs/IMPLEMENTATION_ROADMAP.md docs/archive/2026-01-15-cleanup/old-guides/

# Old Schemas
mv docs/SEED_GRAPH_SCHEMA.md docs/archive/2026-01-15-cleanup/old-schemas/
mv docs/VALUE_GRAPH_SCHEMA.md docs/archive/2026-01-15-cleanup/old-schemas/
mv docs/WORKING_STATE_TIMELINE_SCHEMA.md docs/archive/2026-01-15-cleanup/old-schemas/

# Old Concepts
mv docs/THEMATIC_WORKFLOWS_CONCEPT.md docs/archive/2026-01-15-cleanup/old-concepts/
mv docs/UNIFIED_ORCHESTRATOR_CONCEPT.md docs/archive/2026-01-15-cleanup/old-concepts/

# Frontend Docs
mv docs/FRONTEND_*.md docs/archive/2026-01-15-cleanup/frontend-docs/
mv docs/VUE_GUI_IMPLEMENTATION_GUIDE.md docs/archive/2026-01-15-cleanup/frontend-docs/
mv docs/UNIFIED_DASHBOARD_V2.md docs/archive/2026-01-15-cleanup/frontend-docs/

# Analysis Docs
mv docs/ANALYSIS_SUMMARY.md docs/archive/2026-01-15-cleanup/analysis-docs/
mv docs/BACKEND_CONSOLIDATION_PLAN.md docs/archive/2026-01-15-cleanup/analysis-docs/
mv docs/INTEGRATION_ANALYSIS.md docs/archive/2026-01-15-cleanup/analysis-docs/
mv docs/MIGRATION_PLAN.md docs/archive/2026-01-15-cleanup/analysis-docs/
mv docs/NODE_BASED_PIPELINE_ANALYSIS.md docs/archive/2026-01-15-cleanup/analysis-docs/
mv docs/README_ANALYSIS.md docs/archive/2026-01-15-cleanup/analysis-docs/
mv docs/UNIFICATION_PROGRESS.md docs/archive/2026-01-15-cleanup/analysis-docs/
mv docs/WORKFLOW_ANALYSIS_AND_UNIFICATION.md docs/archive/2026-01-15-cleanup/analysis-docs/

# Workflow Docs
mv docs/RESEARCH_CREATION_WORKFLOW.md docs/archive/2026-01-15-cleanup/workflow-docs/
mv docs/RESPONSE_COLLECTION_WORKFLOW.md docs/archive/2026-01-15-cleanup/workflow-docs/
mv docs/PROMPT_BASED_RESEARCH_GENERATOR.md docs/archive/2026-01-15-cleanup/workflow-docs/

# Sonstiges
mv docs/GEMINI_PROMPT.md docs/archive/2026-01-15-cleanup/
```

### Step 3: Neue Struktur aufbauen
```bash
# Implementation Ordner
mkdir -p docs/implementation
mv docs/MASTER_IMPLEMENTATION_PROMPT.md docs/implementation/
mv docs/IMPLEMENTATION_ANALYSIS_MAPPING.md docs/implementation/
mv docs/GEMINI_REVIEW_RESULTS.md docs/implementation/
mv docs/IMPLEMENTATION_GUIDE_CLUSTER_1.md docs/implementation/

# Reference Ordner
mkdir -p docs/reference
mv docs/API_V2_UNIFIED_ENDPOINTS.md docs/reference/
mv docs/COVERAGE_MCTS_INTEGRATION.md docs/reference/
mv docs/CONTEXT_WINDOW_MONITORING.md docs/reference/
mv docs/MULTI_GPU_TESTING_PLAN.md docs/reference/
mv docs/TRANSFER_CHECKLIST.md docs/reference/
```

### Step 4: README erstellen
Neues `docs/README.md` mit Navigation (siehe unten)

### Step 5: Archive README
`docs/archive/2026-01-15-cleanup/README.md` mit Erklärung

---

## Nach dem Cleanup

**Vorher:** 37 Docs in docs/ (unübersichtlich)

**Nachher:**
- `docs/` Root: 1 Datei (README.md)
- `docs/concepts/`: 10 Dateien (9 Konzepte + README)
- `docs/implementation/`: 4 Dateien (aktive Guides)
- `docs/reference/`: 5 Dateien (technische Referenz)
- `docs/archive/`: 26 Dateien (archiviert)

**Total:** 46 Dateien (10 mehr wegen READMEs, aber strukturiert!)

---

## docs/README.md (NEU)

```markdown
# Sovereign Research Orchestrator - Documentation

**Status:** Active Development (Cluster 1)
**Last Updated:** 2026-01-15

---

## 🚀 Quick Start

**Neu hier?** Start mit:
1. [SRO Architecture Overview](./concepts/SRO_ARCHITECTURE_OVERVIEW.md)
2. [Implementation Analysis & Mapping](./implementation/IMPLEMENTATION_ANALYSIS_MAPPING.md)
3. [Gemini Review Results](./implementation/GEMINI_REVIEW_RESULTS.md)
4. [Cluster 1 Implementation Guide](./implementation/IMPLEMENTATION_GUIDE_CLUSTER_1.md)

---

## 📚 Dokumentation

### [concepts/](./concepts/) - SRO Konzepte (9 Dateien)
Die vollständige theoretische Grundlage des SRO-Systems:
- 🏗️ [SRO Architecture Overview](./concepts/SRO_ARCHITECTURE_OVERVIEW.md) - Gesamtarchitektur
- 🧠 [XoT & Generative CoT](./concepts/XOT_GENERATIVE_COT_CONCEPT.md) - Test-time Compute Scaling
- 🔗 [SPO Knowledge Graph](./concepts/SPO_KNOWLEDGE_GRAPH_CONCEPT.md) - Strukturiertes Wissen
- ⚖️ [Constitutional AI & Axioms](./concepts/CONSTITUTIONAL_AI_AXIOM_CONCEPT.md) - Werte-System
- 🔄 [Recursive Language Models](./concepts/RECURSIVE_LLM_CONCEPT.md) - 10M+ Token Context
- 👥 [Reddit Validation](./concepts/REDDIT_VALIDATION_CONCEPT.md) - Social Grounding
- 🎯 [Bias Mapping Strategy](./concepts/BIAS_MAPPING_STRATEGY.md) - Perspektiven-Graph
- 🔍 [Epistemic MCTS](./concepts/EPISTEMIC_MCTS_CONCEPT.md) - Intelligente Recherche
- 🔒 [Privacy Hardening](./concepts/PRIVACY_HARDENING_CONCEPT.md) - Daten-Souveränität

Siehe [concepts/README.md](./concepts/README.md) für Details.

---

### [implementation/](./implementation/) - Implementation Guides

**Aktuelle Phase:** Cluster 1 - Foundations

- 📋 [Master Implementation Prompt](./implementation/MASTER_IMPLEMENTATION_PROMPT.md) - 5-Cluster Roadmap
- 🗺️ [Implementation Analysis & Mapping](./implementation/IMPLEMENTATION_ANALYSIS_MAPPING.md) - Bestandsaufnahme
- ✅ [Gemini Review Results](./implementation/GEMINI_REVIEW_RESULTS.md) - Design-Entscheidungen
- 🛠️ [Cluster 1 Implementation Guide](./implementation/IMPLEMENTATION_GUIDE_CLUSTER_1.md) - Detaillierte Anleitung

**Nächste Schritte:**
- Cluster 2: Tiered RAG + Axiom Judge (nach Cluster 1)
- Cluster 3: BiasVector + Perspektiven-Graph
- Cluster 4: RLM + Epistemic MCTS
- Cluster 5: Privacy Sanitization (optional)

---

### [reference/](./reference/) - Technical Reference

Technische Referenz-Dokumentation:
- [API v2 Unified Endpoints](./reference/API_V2_UNIFIED_ENDPOINTS.md)
- [Coverage-MCTS Integration](./reference/COVERAGE_MCTS_INTEGRATION.md)
- [Context Window Monitoring](./reference/CONTEXT_WINDOW_MONITORING.md)
- [Multi-GPU Testing Plan](./reference/MULTI_GPU_TESTING_PLAN.md)
- [Transfer Checklist](./reference/TRANSFER_CHECKLIST.md)

---

### [archive/](./archive/) - Archived Documents

Alte/veraltete Dokumentation (für Historie):
- [2026-01-15 Cleanup](./archive/2026-01-15-cleanup/) - Pre-SRO Dokumentation

---

## 🎯 Aktueller Status

**Phase:** Cluster 1 Implementation (Woche 1-2)
**Fokus:** SPO-Extraktion + XoT-Simulator + Token-Budget

**Fertiggestellt:**
- ✅ 9 SRO-Konzepte dokumentiert
- ✅ Gemini Review abgeschlossen
- ✅ Implementation Analysis & Mapping
- ✅ Cluster 1 Guide geschrieben
- ✅ Dokumentation aufgeräumt

**In Arbeit:**
- 🔄 SPOExtractor Implementation
- 🔄 XoTSimulator Setup
- 🔄 TokenBudgetManager

**Nächste Milestones:**
- SPO-Tripletts funktionieren
- XoT beschleunigt MCTS
- Token-Budget verhindert Verschwendung

---

## 📖 Weitere Ressourcen

- **Codebase:** `src/` (Python Backend)
- **GUI:** `gui/` (Vue.js Frontend)
- **Config:** `config/` (Models, Axioms, Profiles)
- **Tests:** `tests/` (Unit & Integration Tests)

---

**Dokumentiert von:** Claude Code
**Basierend auf:** Gemini Strategic Planning (Januar 2026)
**Status:** 🟢 Active Development
```

---

## docs/archive/2026-01-15-cleanup/README.md (NEU)

```markdown
# Archived Documentation - 2026-01-15 Cleanup

**Archiviert am:** 2026-01-15
**Grund:** Vorbereitung für SRO Cluster 1 Implementation
**Strategie:** Archivieren statt Löschen

---

## Warum archiviert?

Diese Dokumente waren Teil der **Pre-SRO Entwicklung** (vor Gemini Strategic Planning). Sie sind veraltet oder wurden durch die neuen SRO-Konzepte ersetzt, aber werden aus historischen Gründen aufbewahrt.

---

## Archiv-Struktur

### implementation-snapshots/
Tages-Snapshots alter Implementation-Fortschritte:
- IMPLEMENTATION_COMPLETE_2026-01-02.md
- IMPLEMENTATION_COMPLETE_2026-01-10.md
- IMPLEMENTATION_COMPLETE_2026-01-11.md
- TODO_NEXT_SESSION.md

**Ersetzt durch:** `docs/implementation/IMPLEMENTATION_GUIDE_CLUSTER_1.md`

---

### old-guides/
Alte Implementation Guides:
- IMPLEMENTATION_GUIDE.md (25K)
- IMPLEMENTATION_ROADMAP.md (27K)

**Ersetzt durch:** `docs/implementation/MASTER_IMPLEMENTATION_PROMPT.md`

---

### old-schemas/
Alte Datenmodell-Schemas:
- SEED_GRAPH_SCHEMA.md - Integriert in UnifiedSession
- VALUE_GRAPH_SCHEMA.md - Ersetzt durch SPO-Konzept
- WORKING_STATE_TIMELINE_SCHEMA.md - Veraltet

**Ersetzt durch:** `docs/concepts/SPO_KNOWLEDGE_GRAPH_CONCEPT.md`

---

### old-concepts/
Alte Architektur-Konzepte:
- THEMATIC_WORKFLOWS_CONCEPT.md
- UNIFIED_ORCHESTRATOR_CONCEPT.md

**Ersetzt durch:** `docs/concepts/SRO_ARCHITECTURE_OVERVIEW.md`

---

### frontend-docs/
Frontend-bezogene Dokumentation (gehört zu gui/ Subprojekt):
- FRONTEND_TODO.md
- FRONTEND_REDESIGN_BRIEF.md
- FRONTEND_DEPENDENCY_REPORT.md
- VUE_GUI_IMPLEMENTATION_GUIDE.md
- UNIFIED_DASHBOARD_V2.md

**Hinweis:** Diese sollten zu `gui/docs/` verschoben werden (separate Frontend-Doku)

---

### analysis-docs/
Analyse-Dokumente aus alten Planungsphasen:
- ANALYSIS_SUMMARY.md
- BACKEND_CONSOLIDATION_PLAN.md
- INTEGRATION_ANALYSIS.md
- MIGRATION_PLAN.md
- NODE_BASED_PIPELINE_ANALYSIS.md (50K!)
- README_ANALYSIS.md
- UNIFICATION_PROGRESS.md
- WORKFLOW_ANALYSIS_AND_UNIFICATION.md

**Ersetzt durch:** `docs/implementation/IMPLEMENTATION_ANALYSIS_MAPPING.md`

---

### workflow-docs/
Alte Workflow-Beschreibungen:
- RESEARCH_CREATION_WORKFLOW.md
- RESPONSE_COLLECTION_WORKFLOW.md
- PROMPT_BASED_RESEARCH_GENERATOR.md

**Ersetzt durch:** SRO-Konzepte (XoT, MCTS, SPO)

---

## Nützlichkeit dieser Dokumente

**Historischer Wert:** Zeigen Entwicklungs-Evolution des Projekts

**Praktischer Wert:** Gering - meiste Konzepte wurden in SRO-Architektur neu gedacht

**Empfehlung:** Behalten für Historie, aber nicht für aktive Implementation nutzen

---

**Für aktive Dokumentation siehe:** [docs/README.md](../../README.md)
```

---

## Status

**Plan erstellt:** ✅
**Bereit für Ausführung:** ✅

**Nächster Schritt:** Bash-Befehle ausführen (mit Bestätigung)
