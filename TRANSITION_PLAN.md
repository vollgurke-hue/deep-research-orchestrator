# Transition Plan: Deep Research Orchestrator → Sovereign Research Architect

**Date:** 2026-01-08
**Status:** Ready to Begin

---

## Was ist passiert?

### Alte Vision (Deep Research Orchestrator)
- Linear workflows (Phase 0→1→2→3)
- Prompt-basierte Forschung
- Mock-Mode für Testing
- Focus: Allgemeine Research-Aufgaben

### Neue Vision (Sovereign Research Architect)
- **Hybrid Intelligence:** Externe Modelle für Breite, lokale Modelle für Tiefe
- **Knowledge Graph:** Trennung von Fakten und Meinungen
- **Axiom-Library:** Deine Werte als Filter gegen Big Tech Bias
- **ToT + MCTS:** Moderne Reasoning-Techniken statt lineare Workflows
- **Focus:** Wirtschaftliche Entscheidungen mit souveräner Kontrolle

---

## Was wurde behalten?

✅ **Software-Architektur:**
- 3-Layer-Struktur (Description, Working State, Output)
- Flask API + Vue 3 Frontend
- JSON-basiertes Config-System
- Multi-AI Orchestration Tools

✅ **Bewährte Komponenten:**
- Validation Techniques (contradiction_check, blind_spots, premortem)
- Category-based Routing
- Template-based Prompts
- LlamaCppClient

---

## Was ist neu?

⭐ **Core-Änderungen:**
1. **Knowledge Graph (NetworkX):** Zentrale "Wahrheits-Buffer" im RAM
2. **Axiom-Library:** Deine Werte als JSON (z.B. Österreichische Ökonomie)
3. **ToT Manager:** Tree of Thoughts statt linearer Workflows
4. **MCTS Engine:** Monte Carlo Search für Pfad-Bewertung
5. **Friction Detector:** Web-Scraping für Real-World-Validierung

⭐ **Neue Techniken:**
- Tree of Thoughts (ToT) - Exploration
- Monte Carlo Tree Search (MCTS) - Bewertung
- GraphRAG - Entity-Extraction
- Python-Simulationen - Mathematische Validierung

---

## Die neuen 4 Phasen

| Alt | Neu | Zweck |
|-----|-----|-------|
| Phase 0: Base Research | **Phase 0: EXPLORATION** | ToT + externe Modelle (Breite) |
| Phase 1: Excurse | **Phase 1: GROUNDING** | Friction + Axiom-Check (Realität) |
| Phase 2: Validation | **Phase 2: REASONING** | MCTS + Python-Sims (Tiefe) |
| Phase 3: Synthesis | **Phase 3: SYNTHESIS** | Souveräne Entscheidung |

---

## Umsetzungsplan (8-10 Wochen)

### ✅ Sprint 0: Foundation (DONE)
- [x] Codebase aufgeräumt
- [ ] DeepSeek-R1-7B lokal testen
- [ ] NetworkX Performance validieren
- [ ] Schemas designen

### Sprint 1: Core Graph Infrastructure (Woche 2-3)
**Ziel:** Knowledge Graph + Axiom-System

**Zu implementieren:**
1. `src/core/graph_manager.py` - NetworkX Wrapper
2. `src/core/axiom_judge.py` - Werte-Validierung
3. `config/axioms/*.json` - Erste Axiome (Beispiele)
4. Unit Tests

**Deliverables:**
- Graph mit 10,000 Nodes läuft
- Axiom-Evaluation funktioniert
- Query-Performance <500ms

### Sprint 2: ToT & MCTS (Woche 4-5)
**Ziel:** Reasoning-Engines

**Zu implementieren:**
1. `src/core/tot_manager.py` - Tree of Thoughts
2. `src/core/mcts_engine.py` - Monte Carlo Search
3. `src/core/orchestrator.py` - Refactoring für 4-Phasen-Cycle
4. Python-Simulation Framework

**Deliverables:**
- ToT-Baum mit 4 Ebenen funktioniert
- MCTS evaluiert Pfade
- Python-Sims laufen

### Sprint 3: Frontend (Woche 6-7)
**Ziel:** User Interfaces

**Zu implementieren:**
1. API-Endpoints (`/api/v2/research/*`)
2. `ToTExplorer.vue` - Baum-Visualisierung
3. `GraphViewer.vue` - D3.js Knowledge Graph
4. `AxiomEditor.vue` - Werte-Management

**Deliverables:**
- ToT-Baum visualisiert
- Graph interaktiv
- Axiome editierbar

### Sprint 4: Integration & Polish (Woche 8-10)
**Ziel:** Production-Ready

**Zu implementieren:**
1. Web-Scraping (Crawl4AI)
2. Friction Detection
3. End-to-End Tests
4. Documentation

**Deliverables:**
- Kompletter Research-Flow funktioniert
- Reddit-Scraping arbeitet
- Dokumentation vollständig

---

## Nächste Schritte (JETZT)

### 1. Sprint 0 abschließen

```bash
# DeepSeek-R1 installieren und testen
cd ~/Schreibtisch/AI_Projects/deep-research-orchestrator

# Option A: Ollama (empfohlen, einfacher)
ollama pull deepseek-r1:7b
ollama run deepseek-r1:7b "Test: Erkläre Opportunity Cost in 2 Sätzen"

# Option B: vLLM (schneller, komplexer)
# ... siehe docs/guides/model_setup.md

# NetworkX testen
python3 << EOF
import networkx as nx
import time

# Test graph creation
G = nx.DiGraph()
start = time.time()
for i in range(10000):
    G.add_node(f"node_{i}", data={"type": "test"})
    if i > 0:
        G.add_edge(f"node_{i-1}", f"node_{i}")

# Test query
subgraph = nx.ego_graph(G, "node_5000", radius=2)
elapsed = time.time() - start

print(f"Created 10k nodes in {elapsed:.2f}s")
print(f"Subgraph size: {len(subgraph.nodes())}")
EOF
```

### 2. Review Dokumentation

Lies diese Dateien:
1. `docs/architecture/SOVEREIGN_RESEARCH_ARCHITECT.md` - Vollständige Architektur
2. `docs/IMPLEMENTATION_ROADMAP.md` - Detaillierter Umsetzungsplan (dieses Dokument)
3. Alte Konzepte archiviert in `archive/`

### 3. Entscheidung treffen

**Option A: Schrittweise Migration (empfohlen)**
- Behalte altes System parallel
- Baue neue Komponenten inkrementell
- Teste gründlich vor Migration
- Zeitaufwand: 8-10 Wochen

**Option B: Fresh Start**
- Neues Repo basierend auf Sovereign Architect
- Portiere nur bewährte Komponenten
- Schnellerer Start, mehr Risiko
- Zeitaufwand: 6-8 Wochen

**Option C: Hybrid**
- Neue Backend-Komponenten (Graph, ToT, MCTS)
- Alte Frontend-Views behalten und schrittweise ersetzen
- Balance zwischen Geschwindigkeit und Sicherheit
- Zeitaufwand: 7-9 Wochen

---

## Entscheidungshilfe

### Gründe für Option A (Schrittweise Migration)
- ✅ Kein Datenverlust
- ✅ Altes System bleibt funktional
- ✅ Weniger Risiko
- ✅ Lernkurve flacher
- ❌ Komplexität durch Coexistence

### Gründe für Option B (Fresh Start)
- ✅ Saubere Architektur von Anfang an
- ✅ Keine Legacy-Altlasten
- ✅ Schnellerer Start
- ❌ Mehr initial work
- ❌ Alte Komponenten manuell portieren

### Gründe für Option C (Hybrid)
- ✅ Beste Balance
- ✅ Backend-Innovation, Frontend-Stabilität
- ✅ Flexibel
- ❌ Braucht klare Interface-Definition

---

## Empfehlung

**Für dich: Option C (Hybrid)**

**Begründung:**
1. Du hast bereits ein funktionierendes Frontend (Vue 3 GUI ist gut)
2. Die Kernänderungen sind im Backend (Graph, ToT, MCTS)
3. Du kannst Frontend schrittweise austauschen (ein View nach dem anderen)
4. Weniger Overhead als Option A, weniger Risiko als Option B

**Konkret:**
- **Sprint 1-2:** Neue Backend-Komponenten (graph_manager, tot_manager, mcts_engine)
- **Sprint 3:** Neue API-Endpoints (`/api/v2/*`)
- **Sprint 3:** EINE neue Vue-View (`SovereignResearch.vue`)
- **Sprint 4:** Wenn alles funktioniert → alte Views nach und nach ersetzen

---

## Quick Start (Option C)

```bash
# 1. Branch erstellen
git checkout -b feature/sovereign-architect

# 2. Neue Verzeichnisse anlegen
mkdir -p config/axioms
mkdir -p src/core/reasoning
mkdir -p tests/unit tests/integration

# 3. Schemas erstellen
# (Siehe docs/IMPLEMENTATION_ROADMAP.md Sprint 1)

# 4. Erste Axiome schreiben
# config/axioms/economic_principles.json
# config/axioms/risk_tolerance.json

# 5. GraphManager implementieren
# src/core/graph_manager.py (siehe Roadmap)

# 6. Tests schreiben
# tests/unit/test_graph_manager.py
```

---

## Monitoring & Success Metrics

### Sprint 1 Erfolg:
- [ ] GraphManager läuft mit 10k Nodes
- [ ] AxiomJudge evaluiert Nodes
- [ ] Unit Tests: >80% Coverage
- [ ] Dokumentation: Alle Public APIs

### Sprint 2 Erfolg:
- [ ] ToT-Baum mit 4 Ebenen
- [ ] MCTS läuft 10+ Iterationen
- [ ] Python-Simulation generiert und ausführt
- [ ] Orchestrator 4-Phasen-Cycle

### Sprint 3 Erfolg:
- [ ] ToTExplorer zeigt Baum an
- [ ] GraphViewer visualisiert Graph
- [ ] API-Endpoints alle funktional
- [ ] User kann Research starten

### Sprint 4 Erfolg:
- [ ] Reddit-Scraping findet Friction
- [ ] End-to-End Test: Kompletter Research-Flow
- [ ] VRAM <9GB während Inference
- [ ] Dokumentation komplett

---

## Fragen & Entscheidungen

**Beantworte diese Fragen, bevor du startest:**

1. **Welche Option?** A / B / **C** (empfohlen)

2. **Welches lokale Modell?**
   - [ ] DeepSeek-R1-7B (empfohlen für Reasoning)
   - [ ] Qwen 2.5 7B (schneller, weniger Reasoning)
   - [ ] Beides testen und entscheiden

3. **Welches Model-Serving?**
   - [ ] Ollama (einfacher Setup)
   - [ ] vLLM (bessere Performance)

4. **Erste Axiome?** (Welche Werte sind dir wichtig?)
   - [ ] Opportunity Cost (Zeit vs. Profit)
   - [ ] Österreichische Ökonomie
   - [ ] Risiko-Toleranz
   - [ ] Andere: _______________

5. **Zeitbudget?**
   - [ ] Full-time (4 Wochen)
   - [ ] Part-time (8-10 Wochen)
   - [ ] Wochenenden (12+ Wochen)

---

## Support & Resources

**Dokumentation:**
- `docs/architecture/SOVEREIGN_RESEARCH_ARCHITECT.md` - Vollständige Architektur
- `docs/IMPLEMENTATION_ROADMAP.md` - Sprint-Details
- `docs/guides/` - Setup-Guides (neu zu erstellen)

**Code-Referenzen:**
- [microsoft/graphrag](https://github.com/microsoft/graphrag)
- [stanfordnlp/dspy](https://github.com/stanfordnlp/dspy)
- [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph)
- [unclecode/crawl4ai](https://github.com/unclecode/crawl4ai)

**Community:**
- DeepSeek-R1 Discussions
- Sovereign Tech Fund (Inspiration)
- Austrian Economics Resources

---

## Fazit

Du hast jetzt:
- ✅ Aufgeräumten Code
- ✅ Klare Vision (Sovereign Research Architect)
- ✅ Detaillierten Plan (4 Sprints)
- ✅ Architektur-Dokument
- ✅ Migrations-Strategie

**Nächster Schritt:** Entscheide dich für Option A/B/C und starte Sprint 0 (Technische Validierung).

**Mein Vorschlag:** Option C, DeepSeek-R1-7B via Ollama, 8 Wochen Part-time.

---

Bereit zum Start? 🚀
