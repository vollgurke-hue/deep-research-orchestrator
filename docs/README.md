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
- 📝 [Documentation Cleanup Plan](./implementation/DOCS_CLEANUP_PLAN.md) - Aufräumungs-Historie

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
- [Archived TODOs 2026-01-15](./archive/ARCHIVED_TODOS_2026-01-15.md) - Seed Graph TODOs

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
