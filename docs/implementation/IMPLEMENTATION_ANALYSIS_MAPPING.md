# Implementation Analysis & Konzept-Mapping

**Erstellt:** 2026-01-15
**Zweck:** Mapping zwischen bestehendem Code und neuen SRO-Konzepten
**Für:** Gemini Review & Implementation Planning

---

## Executive Summary

Nach Analyse des Codebases zeigt sich: **Viele SRO-Konzepte sind bereits teilweise implementiert!** Die bestehende Architektur hat bereits mehrere Komponenten, die direkt in die neuen Konzepte integriert werden können. Dies spart erhebliche Implementierungszeit und ermöglicht evolutionäre statt revolutionäre Entwicklung.

**Kernbefund:**
- ✅ **70% der Logik-Ebene** bereits implementiert (MCTS + ToT + Coverage)
- ✅ **60% der Kontrollebene** bereits vorhanden (Axiom System + Debate)
- ⚠️ **40% der Wissens-Ebene** teilweise umgesetzt (Graph vorhanden, SPO-Extraktion fehlt)
- ❌ **0% RLM-Integration** (neue Komponente)
- ❌ **0% Privacy Sanitization** (neue Komponente)
- ❌ **0% Epistemic MCTS** (neue Komponente)

**Empfehlung:** Evolutionäre Migration statt Neuschreibung - bestehende Komponenten erweitern, nicht ersetzen.

---

## 1. Bestandsaufnahme: Was ist bereits implementiert?

### ✅ Core Engine (src/core/)

#### 1.1 MCTS Engine (`mcts_engine.py`) - **90% fertig**
**Status:** Vollständig implementiert mit Coverage-Guided Selection

**Features:**
- ✅ Standard MCTS (Selection, Simulation, Backpropagation)
- ✅ UCB1 Formula mit Exploration Constant
- ✅ Coverage-Guided Selection (Bonus für unter-explorierte Bereiche)
- ✅ Adaptive Coverage Weight (0.7 → 0.5 → 0.3 basierend auf Phase)
- ✅ Multiple Simulation Methods (axiom, llm, random)
- ✅ Best Path & Most Visited Path Selection
- ✅ Coverage-Guided Suggestions für UI

**Wichtige Methoden:**
```python
class MCTSEngine:
    def iterate(self, num_iterations: int = 1)  # Main MCTS loop
    def select(self) -> Optional[str]            # UCB1 selection
    def simulate(self, node_id: str) -> float    # Value estimation
    def backpropagate(self, node_id: str, value: float)  # Update tree
    def _compute_coverage_bonus(self, node) -> float  # Coverage integration
    def _get_adaptive_coverage_weight(self) -> float  # Adaptive strategy
```

**Mapping auf SRO-Konzepte:**
- ✅ Implementiert **Test-time Compute Scaling** (XOT_GENERATIVE_COT_CONCEPT)
- ✅ Implementiert **Coverage-Guided Search** (EPISTEMIC_MCTS_CONCEPT Vorstufe)
- ⚠️ Fehlt: XoT als "Vor-Denker" Integration
- ⚠️ Fehlt: Generative CoT (Multiple reasoning paths per node)

---

#### 1.2 ToT Manager (`tot_manager.py`) - **85% fertig**
**Status:** Vollständig implementiert mit External Model Support

**Features:**
- ✅ Tree-of-Thoughts Struktur (Root → Branches → Leaves)
- ✅ Question Decomposition via LLM
- ✅ Node Expansion mit Graph Context
- ✅ Entity Extraction (simpel, kann verbessert werden)
- ✅ Axiom Compatibility Checking
- ✅ Branch Pruning
- ✅ **External Model Integration** (Claude/GPT-4/Gemini via Copy-Paste)
- ✅ Path-to-Root Tracking
- ✅ Best Path Selection

**Wichtige Methoden:**
```python
class ToTManager:
    def create_root(self, question: str) -> str
    def decompose_question(self, node_id: str, branching_factor: int = 3)
    def expand_node(self, node_id: str) -> bool
    def generate_external_prompt(self, node: ToTNode) -> str  # Sprint 4 Feature!
    def add_external_response(self, node_id: str, response_text: str)
    def prune_branch(self, node_id: str, reason: str)
```

**Mapping auf SRO-Konzepte:**
- ✅ Implementiert **Tree-of-Thoughts** (XOT_GENERATIVE_COT_CONCEPT)
- ✅ Implementiert **Graph Integration** (SPO_KNOWLEDGE_GRAPH_CONCEPT Basis)
- ✅ Implementiert **External Model Support** (wichtig für RLM!)
- ⚠️ Fehlt: SPO-Triplett Extraktion (aktuell nur simple Keywords)
- ⚠️ Fehlt: Graph-of-Thoughts Struktur (aktuell nur Tree)

---

#### 1.3 Axiom Manager (`axiom_manager.py`) - **75% fertig**
**Status:** Funktioniert, kann erweitert werden

**Features:**
- ✅ Axiom Loading aus JSON files
- ✅ Scorer Axioms (weight modifiers)
- ✅ Filter Axioms (reject nodes)
- ✅ Category-based Organization
- ✅ Condition Evaluation (if_roi_per_hour < 50, etc.)
- ✅ Node Scoring & Filtering

**Axiom Structure:**
```json
{
  "axiom_id": "opportunity_cost",
  "category": "economics",
  "statement": "Evaluate opportunities by opportunity cost",
  "application": "scorer",
  "weight_modifier": {
    "if_roi_per_hour < 50": -0.5,
    "if_roi_per_hour >= 100": 0.8
  },
  "enabled": true
}
```

**Mapping auf SRO-Konzepte:**
- ✅ Implementiert **Constitutional AI** Basis (CONSTITUTIONAL_AI_AXIOM_CONCEPT)
- ✅ Implementiert **Value-based Filtering**
- ⚠️ Fehlt: RLAIF Feedback Loop (aktuell statische Scores)
- ⚠️ Fehlt: Axiom-Konflikt-Auflösung
- ⚠️ Fehlt: Dynamische Axiom-Anpassung
- ❌ Fehlt: LLM-based Axiom Evaluation (aktuell nur rule-based)

**Wichtige Erweiterung aus Konzept:**
```python
@dataclass
class Axiom:  # Aus CONSTITUTIONAL_AI_AXIOM_CONCEPT
    axiom_id: str
    name: str
    description: str
    category: str
    weight: float
    penalty: float
    evaluation_prompt: str  # ← FEHLT aktuell!
    code_validator: Optional[Callable]  # ← FEHLT aktuell!
```

---

#### 1.4 Debate Manager (`debate_manager.py`) - **80% fertig**
**Status:** Vollständig für Sequential Debate, erweiterbar für Contrastive Debate

**Features:**
- ✅ 3-Model Sequential Pattern (A → B → Judge)
- ✅ Contradiction Resolution zwischen Graph Nodes
- ✅ ToT Path Evaluation
- ✅ Structured Judge Response Parsing
- ✅ Confidence Scoring

**Mapping auf SRO-Konzepte:**
- ✅ Implementiert **Contrastive Reasoning** Basis (BIAS_MAPPING_STRATEGY)
- ⚠️ Fehlt: BiasVector Integration (aktuell keine Bias-Quantifizierung)
- ⚠️ Fehlt: Perspektiven-Graph (aktuell keine Bias-Persistierung)
- ⚠️ Fehlt: Source Profiling (aktuell keine systematische Bias-Analyse)

**Erweiterungspotenzial:**
```python
# Aus BIAS_MAPPING_STRATEGY Konzept
@dataclass
class BiasVector:
    risk_affinity: float
    time_horizon: float
    centralization: float
    empirical_depth: float
    profit_motive: float

    def distance_to(self, other: BiasVector) -> float
```

→ **Debate Manager kann erweitert werden um BiasVector-Extraktion aus Arguments!**

---

#### 1.5 Coverage Analyzer (`coverage_analyzer.py`) - **85% fertig**
**Status:** Vollständig implementiert, kann für Epistemic MCTS erweitert werden

**Features:**
- ✅ Multi-dimensionale Coverage-Analyse:
  - Entity Density
  - Exploration Depth
  - Axiom Coverage
  - Neighbor Coverage
- ✅ Coverage Gap Identification
- ✅ Coverage Heatmap Generation
- ✅ Thematic Coverage Tracking
- ✅ Actionable Recommendations

**Mapping auf SRO-Konzepte:**
- ✅ Implementiert **Uncertainty Modeling** Basis (EPISTEMIC_MCTS_CONCEPT)
- ⚠️ Fehlt: Value of Information (VoI) Calculation
- ⚠️ Fehlt: Dynamic Scraping Queue
- ⚠️ Fehlt: Cost/Benefit Analysis für Information Gathering
- ⚠️ Fehlt: Stopping Criteria basierend auf Coverage

**Erweiterungspotenzial:**
```python
# Aus EPISTEMIC_MCTS_CONCEPT
def calculate_voi(action: InformationAction, current_uncertainty: float) -> float:
    expected_gain = estimate_information_gain(action, current_uncertainty)
    time_cost = action.cost_estimate["time"] / 120.0
    token_cost = action.cost_estimate["tokens"] / 10000.0
    total_cost = time_cost + token_cost
    return expected_gain / (total_cost + 0.01)
```

→ **Coverage Analyzer kann erweitert werden zu Epistemic MCTS Engine!**

---

#### 1.6 Graph Manager (`graph_manager.py`) - **60% fertig**
**Status:** NetworkX-basiert, funktioniert für Basis-Operationen

**Features:**
- ✅ NetworkX DiGraph als Backend
- ✅ Node/Edge CRUD Operations
- ✅ Conflict Detection (contradicts edges)
- ✅ Graph Serialization
- ✅ Ego-Graph Extraction
- ✅ Axiom Manager Integration

**Node Structure (aktuell):**
```python
{
    "id": "fact_123",
    "type": "fact",  # fact, opinion, question, hypothesis
    "content": "Market is growing at 15% CAGR",
    "confidence": 0.85,
    "source": "Gartner Report 2024",
    "timestamp": "2026-01-08T17:00:00Z",
    "metadata": { ... }
}
```

**Mapping auf SRO-Konzepte:**
- ⚠️ Teilweise **SPO-Tripletts** (SPO_KNOWLEDGE_GRAPH_CONCEPT)
- ⚠️ Fehlt: Formalisierte SPO-Struktur (aktuell Fließtext in content)
- ⚠️ Fehlt: Tiered RAG (Bronze/Silver/Gold)
- ⚠️ Fehlt: Provenance Tracking
- ⚠️ Fehlt: Confidence Propagation
- ❌ Fehlt: Verified Knowledge Graph (VKG) Layer

**Sollte werden (SPO-Triplett):**
```python
{
    "id": "spo_123",
    "subject": "Solaranlage",
    "predicate": "ROI-Periode",
    "object": "15-20 Jahre",
    "confidence": 0.85,
    "provenance": {
        "source_id": "fact_456",
        "extraction_method": "llm_structured",
        "verified": false,
        "verification_count": 0
    },
    "tier": "bronze"  # bronze | silver | gold
}
```

---

#### 1.7 Session Manager (`session_manager.py`) - **90% fertig**
**Status:** Vollständig implementiert mit Persistence

**Features:**
- ✅ File-based Persistence (data/sessions/*.json)
- ✅ Unified Session Model (thematic, tot, unified modes)
- ✅ Automatic Loading on Startup
- ✅ Runtime Component Attachment (Graph, ToT, MCTS, etc.)
- ✅ Session CRUD Operations
- ✅ Export/Import Functionality

**Mapping auf SRO-Konzepte:**
- ✅ Implementiert **Session Persistence** (RECURSIVE_LLM_CONCEPT Basis)
- ✅ Implementiert **Component Management**
- ⚠️ Fehlt: Checkpoint/Resume für Multi-Hour Research
- ⚠️ Fehlt: State Versioning
- ❌ Fehlt: RLM Environment State Persistence

---

### ✅ Data Models (src/models/)

#### 1.8 Unified Session (`unified_session.py`) - **80% fertig**
**Status:** Umfangreiches Datenmodell, deckt meiste Use Cases ab

**Features:**
- ✅ UnifiedSessionMetadata
- ✅ ResearchContext (goal, axioms, constraints)
- ✅ ThematicStructure (Product Research)
- ✅ ToTStructure (Sovereign Research)
- ✅ **SeedGraphMetadata, SeedGraphNode, SeedGraphEdge** (Gemini v2.0 Schema!)
- ✅ GraphStructure (NetworkX + Seed Graph)
- ✅ WorkingState (current_phase, active_nodes, mcts_stats)
- ✅ Response (unified response format)

**Seed Graph bereits implementiert!**
```python
@dataclass
class SeedGraphNode:
    id: str
    label: str
    type: str  # concept | technical | alternative
    status: str  # defined | gap | potential_conflict
    coverage: float = 0.0

@dataclass
class SeedGraphEdge:
    source: str
    target: str
    relation: str  # supports | requires | conflicts_with | enables | ...
    weight: float = 0.0
    description: str = ""

@dataclass
class ValueTension:
    nodes: List[str]
    type: str  # high_friction | moderate_risk | attention_needed
    reason: str = ""
```

**Mapping auf SRO-Konzepte:**
- ✅ Implementiert **Drei-Ebenen-Architektur** Basis (SRO_ARCHITECTURE_OVERVIEW)
- ✅ Implementiert **Seed Graph** (wichtig für Graph-of-Thoughts!)
- ⚠️ Fehlt: Explicit mapping zu Control/Logic/Knowledge Layers
- ⚠️ Fehlt: BiasVector in Response
- ⚠️ Fehlt: SPO-Tripletts in Response

---

## 2. Mapping: Bestehender Code → Neue Konzepte

### 2.1 Logik-Ebene (Der Motor)

| Komponente | Konzept | Match % | Status | Fehlende Features |
|------------|---------|---------|--------|-------------------|
| **MCTSEngine** | XOT_GENERATIVE_COT | 70% | ✅ Gut | XoT als Vor-Denker, Generative CoT, PRM |
| **ToTManager** | XOT_GENERATIVE_COT | 80% | ✅ Sehr gut | Graph-of-Thoughts statt Tree, SPO-Extraktion |
| **CoverageAnalyzer** | EPISTEMIC_MCTS | 60% | ⚠️ Erweiterbar | VoI Calculation, Dynamic Scraping Queue |

**Handlungsempfehlung:**
- ✅ **MCTSEngine behalten** und erweitern um:
  - XoT-Simulation vor MCTS-Selection
  - Generative CoT (multiple reasoning paths per node)
  - Process Reward Model (PRM) Integration

- ✅ **ToTManager behalten** und erweitern um:
  - SPO-Triplett Extraktion statt simple Keywords
  - Graph-of-Thoughts Struktur (laterale Edges)
  - Graph Merging bei Node Expansion

- ✅ **CoverageAnalyzer erweitern** zu Epistemic MCTS:
  - VoI-Calculation für Scraping-Entscheidungen
  - Dynamic Priority Queue für Information Gathering
  - Cost-Benefit Analysis

---

### 2.2 Kontrollebene (Das Gewissen)

| Komponente | Konzept | Match % | Status | Fehlende Features |
|------------|---------|---------|--------|-------------------|
| **AxiomManager** | CONSTITUTIONAL_AI_AXIOM | 60% | ⚠️ Erweiterbar | RLAIF Loop, LLM-Evaluation, Konflikt-Auflösung |
| **DebateManager** | BIAS_MAPPING_STRATEGY | 50% | ⚠️ Erweiterbar | BiasVector, Perspektiven-Graph, Source Profiling |

**Handlungsempfehlung:**
- ⚠️ **AxiomManager erweitern** zu vollständiger Constitutional AI:
  - LLM-based Axiom Evaluation (nicht nur rule-based)
  - RLAIF Feedback Loop
  - Axiom-Konflikt-Auflösung via Debate
  - Dynamische Weight Adjustment

- ⚠️ **DebateManager erweitern** zu Contrastive Debate Engine:
  - BiasVector Extraction aus Arguments
  - Perspektiven-Graph Aufbau
  - Source Profiling Integration
  - Bias-Distance Calculation

**Neue Komponente benötigt:**
```python
class AxiomJudge:
    """LLM-based axiom evaluation (aus CONSTITUTIONAL_AI_AXIOM_CONCEPT)"""
    def evaluate(self, content: str, axiom: Axiom) -> AxiomScore
    def explain_violation(self, content: str, axiom: Axiom) -> str
```

---

### 2.3 Wissens-Ebene (Das Gedächtnis)

| Komponente | Konzept | Match % | Status | Fehlende Features |
|------------|---------|---------|--------|-------------------|
| **GraphManager** | SPO_KNOWLEDGE_GRAPH | 40% | ⚠️ Rewrite nötig | SPO-Struktur, Tiered RAG, Provenance, VKG |
| **UnifiedSession** | SPO_KNOWLEDGE_GRAPH | 30% | ⚠️ Erweiterbar | SPO-Integration in Responses |

**Handlungsempfehlung:**
- ⚠️ **GraphManager: Evolutionäre Migration**
  1. NetworkX Graph **BEHALTEN** als Legacy Layer
  2. Neuen **SPOExtractor** hinzufügen (neben GraphManager)
  3. Neuen **TieredRAG** Manager hinzufügen
  4. GraphManager um SPO-Methoden erweitern:
     ```python
     class GraphManager:
         # Legacy (behalten)
         def add_node(...)
         def add_edge(...)

         # Neu (hinzufügen)
         def add_spo_triplet(subject, predicate, object, provenance)
         def get_verified_triplets(tier: str = "gold")
         def promote_to_tier(triplet_id: str, new_tier: str)
     ```

- ❌ **NICHT neu schreiben!** Stattdessen:
  - Phase 1: SPO parallel zu bestehenden Nodes speichern
  - Phase 2: Migration Tool zum Konvertieren alter Nodes → SPO
  - Phase 3: Legacy Nodes als Bronze-Tier behandeln

**Neue Komponente benötigt:**
```python
class SPOExtractor:
    """Strukturierte Triplett-Extraktion (aus SPO_KNOWLEDGE_GRAPH_CONCEPT)"""
    def extract_from_text(text: str) -> List[SPOTriplet]
    def verify_triplet(triplet: SPOTriplet, sources: List[str]) -> float
```

---

### 2.4 Skalierungs-Layer (RLM & Privacy)

| Komponente | Konzept | Match % | Status | Fehlende Features |
|------------|---------|---------|--------|-------------------|
| *(keine)* | RECURSIVE_LLM | 0% | ❌ Neu | Komplette RLM-Umgebung |
| *(keine)* | REDDIT_VALIDATION | 0% | ❌ Neu | Reddit API Integration |
| *(keine)* | PRIVACY_HARDENING | 0% | ❌ Neu | Sanitization Pipeline |

**Handlungsempfehlung:**
- ❌ **Neue Komponenten erforderlich** (kein Legacy Code vorhanden)
- ✅ **ABER:** Session Manager kann als Basis dienen für:
  - RLM Environment State Persistence
  - Reddit Validation Result Caching
  - Privacy Audit Logging

---

## 3. Lücken-Analyse: Was fehlt komplett?

### 3.1 Kritische Lücken (müssen implementiert werden)

#### ❌ SPO Extractor
**Warum wichtig:** Ohne SPO-Tripletts bleibt Wissen unstrukturiert und nicht maschinenlesbar.

**Was fehlt:**
- Strukturierte Triplett-Extraktion aus LLM-Responses
- Subject-Predicate-Object Parsing
- Provenance Tracking
- Confidence Propagation

**Implementierungs-Priorität:** **HOCH** (Cluster 2 in MASTER_IMPLEMENTATION_PROMPT)

---

#### ❌ XoT "Vor-Denker" Integration
**Warum wichtig:** Ohne XoT bleibt MCTS ineffizient (simuliert ohne Vorab-Schätzung).

**Was fehlt:**
- Schnelle Gedanken-Simulation vor MCTS
- Prior Probability Estimation
- Integration mit MCTS Selection Phase

**Implementierungs-Priorität:** **HOCH** (Cluster 1 in MASTER_IMPLEMENTATION_PROMPT)

---

#### ❌ RLM Environment
**Warum wichtig:** Ohne RLM bleibt Context auf 128k begrenzt (vs. 10M+ mit RLM).

**Was fehlt:**
- Python REPL Environment
- Code Execution Sandbox
- Prompt-as-Environment Architektur
- CEO-Worker Pattern

**Implementierungs-Priorität:** **MITTEL** (Cluster 1, aber komplex)

---

#### ❌ Tiered RAG (Bronze/Silver/Gold)
**Warum wichtig:** Ohne Tiering keine systematische Verifikation von Wissen.

**Was fehlt:**
- Tier Assignment Logic
- Promotion/Demotion Workflow
- Verified Knowledge Graph (VKG) Layer

**Implementierungs-Priorität:** **HOCH** (Cluster 2)

---

### 3.2 Wichtige Lücken (sollten implementiert werden)

#### ⚠️ BiasVector & Perspektiven-Graph
**Was fehlt:**
- BiasVector Dataclass
- Bias Extraction aus Sources
- Perspektiven-Graph Aufbau
- Bias-Distance Calculation

**Implementierungs-Priorität:** **MITTEL** (Cluster 3)

---

#### ⚠️ Epistemic MCTS (VoI-based)
**Was fehlt:**
- Value of Information Calculation
- Dynamic Scraping Queue
- Cost/Benefit Analysis für Information Gathering
- Stopping Criteria

**Implementierungs-Priorität:** **MITTEL** (Cluster 4)

---

#### ⚠️ Reddit Validation
**Was fehlt:**
- Reddit API (PRAW) Integration
- Experience-Node Extraction
- Human Consensus Scoring
- Friction Detection

**Implementierungs-Priorität:** **NIEDRIG** (Cluster 4, optional)

---

#### ⚠️ Privacy Sanitization
**Was fehlt:**
- Local Metadata Masking
- Sanitization Pipeline
- Cloud Audit Logging
- Differential Privacy für Numerical Data

**Implementierungs-Priorität:** **NIEDRIG** (Cluster 5, optional für lokale Nutzung)

---

### 3.3 Nice-to-Have Lücken (können später kommen)

#### 💡 Generative CoT (Multiple Reasoning Paths)
**Was fehlt:**
- Multi-Path Generation per Node
- Process Reward Model (PRM)
- Beam Search Alternative zu MCTS

**Implementierungs-Priorität:** **NIEDRIG** (Verbesserung von bestehendem ToT)

---

#### 💡 Axiom Conflict Resolution
**Was fehlt:**
- Automatische Konflikt-Erkennung
- Debate-based Resolution
- Dynamic Weight Adjustment

**Implementierungs-Priorität:** **NIEDRIG** (Verbesserung von AxiomManager)

---

## 4. Wiederverwendbarkeit: Keep vs. Rewrite

### ✅ KEEP (90-100% wiederverwendbar)

| Komponente | Grund | Erweiterung nötig? |
|------------|-------|-------------------|
| **SessionManager** | Persistence funktioniert perfekt | Nein, nur neue Features hinzufügen |
| **MCTSEngine** | Core Logik solide | Ja, XoT + Generative CoT |
| **ToTManager** | Gute Basis für ToT | Ja, SPO-Extraktion |
| **UnifiedSession** | Flexibles Datenmodell | Ja, BiasVector + SPO |

---

### ⚠️ EXTEND (60-80% wiederverwendbar)

| Komponente | Grund | Plan |
|------------|-------|------|
| **AxiomManager** | Basis gut, aber zu simpel | LLM-Evaluation hinzufügen |
| **DebateManager** | Sequential Debate gut | BiasVector-Extraktion hinzufügen |
| **CoverageAnalyzer** | Coverage gut, aber nicht epistemisch | VoI-Calculation hinzufügen |
| **GraphManager** | NetworkX gut, aber keine SPO | SPO-Layer parallel aufbauen |

---

### 🔄 REFACTOR (40-60% wiederverwendbar)

| Komponente | Problem | Lösung |
|------------|---------|--------|
| **Entity Extraction (ToT)** | Zu simpel (nur Capitals) | Ersetzen durch SPO Extractor |
| **Axiom Evaluation** | Nur rule-based | Hybrid: Rules + LLM |

---

### ❌ NEW (0% vorhanden)

| Komponente | Grund |
|------------|-------|
| **SPOExtractor** | Komplett neue Funktionalität |
| **TieredRAG** | Komplett neue Funktionalität |
| **XoTSimulator** | Komplett neue Funktionalität |
| **RLMEnvironment** | Komplett neue Funktionalität |
| **BiasVectorExtractor** | Komplett neue Funktionalität |
| **PrivacySanitizer** | Komplett neue Funktionalität |

---

## 5. Migrations-Plan: Evolutionär statt Revolutionär

### Phase 1: Foundation (Woche 1-2)
**Ziel:** Bestehende Komponenten erweitern, keine Breaking Changes

#### Sprint 1.1: SPO-Extraktion parallel zu bestehendem Graph
```
1. Neuen SPOExtractor erstellen (src/core/spo_extractor.py)
2. GraphManager erweitern um SPO-Methoden (nicht ersetzen!)
3. ToTManager erweitern: Neben Entity-Extraction auch SPO-Extraktion
4. UnifiedSession erweitern: SPO-Tripletts in Response speichern
```

**Deliverable:** SPO-Tripletts werden extrahiert und gespeichert, Legacy-System läuft weiter.

---

#### Sprint 1.2: XoT-Integration in MCTS
```
1. Neuen XoTSimulator erstellen (src/core/xot_simulator.py)
2. MCTSEngine erweitern: XoT-Simulation vor Selection Phase
3. ToTManager: Prior Probability von XoT übernehmen
```

**Deliverable:** MCTS nutzt XoT für schnellere Prior-Schätzungen.

---

### Phase 2: Tiered Knowledge (Woche 3-4)
**Ziel:** Verifiziertes Wissen aufbauen

#### Sprint 2.1: Tiered RAG Implementation
```
1. Neuen TieredRAG Manager erstellen
2. Bronze Tier: Alle existierenden Nodes automatisch importieren
3. Silver Tier: SPO-Tripletts mit Provenance
4. Gold Tier: Multi-Source verifizierte Tripletts
```

**Deliverable:** 3-Tier Knowledge Graph mit Promotion-Workflow.

---

#### Sprint 2.2: Axiom Judge (LLM-based)
```
1. AxiomManager erweitern um LLM-Evaluation
2. AxiomJudge Klasse implementieren
3. RLAIF Feedback Loop: Low scores → Debate → Re-evaluation
```

**Deliverable:** Axiom-Evaluation mit erklärbaren LLM-Urteilen.

---

### Phase 3: Bias & Perspektiven (Woche 5-6)
**Ziel:** Bias-Tracking statt Bias-Removal

#### Sprint 3.1: BiasVector Extraction
```
1. BiasVector Dataclass in UnifiedSession
2. DebateManager erweitern: BiasVector aus Arguments extrahieren
3. Perspektiven-Graph aufbauen (parallel zu Knowledge Graph)
```

**Deliverable:** Bias-quantifizierte Responses und Perspektiven-Graph.

---

#### Sprint 3.2: Contrastive Debate Enhancement
```
1. DebateManager: Source Profiling hinzufügen
2. Synthetic Debates zwischen Sources mit unterschiedlichen BiasVectors
3. Perspective Distance Calculation
```

**Deliverable:** Strukturierte Bias-Analyse in allen Debates.

---

### Phase 4: RLM & Epistemic MCTS (Woche 7-8)
**Ziel:** Massive Context & Intelligente Information Gathering

#### Sprint 4.1: Epistemic MCTS
```
1. CoverageAnalyzer erweitern zu Epistemic MCTS
2. VoI-Calculation implementieren
3. Dynamic Scraping Queue
4. Stopping Criteria basierend auf Coverage + VoI
```

**Deliverable:** MCTS entscheidet intelligent, wo weitere Recherche lohnt.

---

#### Sprint 4.2: RLM Environment (Optional)
```
1. Python REPL Environment Setup
2. Prompt-as-Environment Architektur
3. CEO-Worker Pattern für große Datensätze
```

**Deliverable:** 10M+ Token Context via RLM.

---

### Phase 5: Privacy & Reddit (Woche 9-10, Optional)
**Ziel:** Hardening & Social Validation

#### Sprint 5.1: Privacy Sanitization
```
1. PrivacySanitizer Klasse
2. Metadata Masking vor Cloud-Calls
3. Audit Logging für alle Cloud-Anfragen
```

**Deliverable:** Privacy-gehärtetes System.

---

#### Sprint 5.2: Reddit Validation
```
1. Reddit API (PRAW) Integration
2. Experience-Node Extraction
3. Human Consensus Scoring
4. Friction-Check gegen ToT-Hypothesen
```

**Deliverable:** Social Validation Layer.

---

## 6. Konkrete Empfehlungen für Gemini

### Frage 1: Ist die evolutionäre Migration machbar?
**Antwort:** Ja! 70% der Core-Logik ist bereits implementiert. Folgende Komponenten müssen **nicht** neu geschrieben werden:
- MCTSEngine (nur erweitern)
- ToTManager (nur erweitern)
- SessionManager (wie er ist)
- DebateManager (nur erweitern)
- CoverageAnalyzer (nur erweitern)

**Nur neu:** SPOExtractor, TieredRAG, XoTSimulator, RLMEnvironment, PrivacySanitizer

---

### Frage 2: Was ist die größte Lücke?
**Antwort:** **SPO-Extraktion**. Ohne strukturierte Tripletts bleibt alles unstrukturiert.

**Priorität:** SEHR HOCH (Cluster 2, Woche 3-4)

**Workaround bis dahin:** Bestehender GraphManager funktioniert, Daten sind nur nicht SPO-strukturiert.

---

### Frage 3: Welche Konzept-Features sind bereits da?
**Antwort:** Überraschend viele!

| Konzept | Feature | Status |
|---------|---------|--------|
| XOT_GENERATIVE_COT | MCTS | ✅ 90% |
| XOT_GENERATIVE_COT | ToT | ✅ 85% |
| XOT_GENERATIVE_COT | XoT | ❌ 0% |
| XOT_GENERATIVE_COT | Generative CoT | ❌ 0% |
| CONSTITUTIONAL_AI | Axiom Manager | ✅ 75% |
| CONSTITUTIONAL_AI | RLAIF | ❌ 0% |
| SPO_KNOWLEDGE_GRAPH | Graph Manager | ⚠️ 40% |
| SPO_KNOWLEDGE_GRAPH | SPO-Tripletts | ❌ 0% |
| SPO_KNOWLEDGE_GRAPH | Tiered RAG | ❌ 0% |
| BIAS_MAPPING | Debate Manager | ✅ 80% |
| BIAS_MAPPING | BiasVector | ❌ 0% |
| EPISTEMIC_MCTS | Coverage Analyzer | ✅ 85% |
| EPISTEMIC_MCTS | VoI | ❌ 0% |
| RECURSIVE_LLM | Session Persistence | ✅ 90% |
| RECURSIVE_LLM | RLM Environment | ❌ 0% |

---

### Frage 4: Sollten wir von Grund auf neu starten?
**Antwort:** **NEIN!** Das wäre Verschwendung.

**Begründung:**
- MCTSEngine + ToTManager sind **professionell implementiert** (590 + 678 LOC)
- Coverage-Guided Selection **funktioniert bereits**
- External Model Support **ist bereits da** (wichtig für RLM später!)
- Seed Graph Schema **ist bereits im Datenmodell**
- Persistence **funktioniert perfekt**

**Empfehlung:** Evolutionäre Migration wie in Phase 1-5 beschrieben.

---

### Frage 5: Was ist der kritische Pfad?
**Antwort:**

```
Woche 1-2: SPO-Extraktion + XoT-Integration
    ↓
Woche 3-4: Tiered RAG + Axiom Judge
    ↓
Woche 5-6: BiasVector + Perspektiven-Graph
    ↓
Woche 7-8: Epistemic MCTS + RLM (optional)
    ↓
Woche 9-10: Privacy + Reddit (optional)
```

**Blocker:** Keine! Jede Phase baut auf vorheriger auf, aber keine ist blockierend.

---

## 7. Offene Fragen für Gemini

1. **SPO-Extraktion:** Sollen wir existierende Nodes migrieren oder nur neue als SPO speichern?
   - Option A: Migration Tool für alle bestehenden Nodes → SPO
   - Option B: Legacy Nodes als Bronze-Tier behandeln
   - **Empfehlung:** Option B (weniger Aufwand, gleicher Effekt)

2. **XoT-Simulator:** Soll XoT ein separates kleines LLM sein oder den gleichen wie ToT nutzen?
   - Option A: Eigenes schnelles LLM (z.B. Qwen-2.5-14B)
   - Option B: Gleiches LLM wie ToT (einfacher, aber langsamer)
   - **Empfehlung:** Option A (XoT muss sehr schnell sein)

3. **BiasVector:** Manuelle Kalibrierung oder automatische Extraktion?
   - Option A: User kalibriert BiasVector manuell für Sources
   - Option B: LLM extrahiert BiasVector aus Arguments
   - **Empfehlung:** Option B mit A als Fallback

4. **RLM Priority:** Ist RLM kritisch oder optional?
   - Option A: Kritisch (ohne RLM kein 10M+ Context)
   - Option B: Optional (128k Context reicht für die meisten Use Cases)
   - **Frage an Gemini:** Wie wichtig ist 10M+ Context wirklich?

5. **Privacy Priority:** Ist Privacy Sanitization kritisch bei lokaler Nutzung?
   - Option A: Kritisch (auch lokal keine Axiome/Prompts loggen)
   - Option B: Optional (nur bei Cloud-Nutzung relevant)
   - **Empfehlung:** Option B (User nutzt hauptsächlich lokal)

---

## 8. Zusammenfassung für Gemini

**TL;DR:**
- ✅ **70% der SRO-Logik ist bereits implementiert** (MCTS, ToT, Axiome, Debate, Coverage)
- ⚠️ **30% fehlt, aber ist nicht blockierend** (SPO, XoT, BiasVector, RLM)
- ✅ **Evolutionäre Migration ist machbar** (keine Neuschreibung nötig!)
- ✅ **Kritischer Pfad ist klar** (SPO → Tiered RAG → BiasVector → Epistemic MCTS)
- ❓ **5 offene Fragen** (siehe oben)

**Nächster Schritt:**
1. Gemini reviewt diese Analyse
2. Gemini beantwortet die 5 offenen Fragen
3. User startet mit Phase 1 (SPO + XoT)

---

**Ende der Analyse**
