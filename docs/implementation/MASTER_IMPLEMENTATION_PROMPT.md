# Master Implementation Prompt - SRO Hardening Phase

**Datum:** 2026-01-22
**Ziel:** Implementation der finalen SRO-Architektur
**Basis:** Gemini Strategic Planning (Woche 15.-22. Jan 2026)

---

## 🎯 Mission

Implementiere den **Sovereign Research Orchestrator (SRO)** - eine autonome Forschungs-Maschine die Logik, Struktur und persönliche Werte mathematisch vereint.

**Konsolidierte Konzepte:** 9 Dokumente, ~120K strukturierte Spezifikation

---

## 📚 Konzept-Übersicht (Lesereihenfolge)

### Basis-Konzepte (MUST READ)
1. **[SRO_ARCHITECTURE_OVERVIEW.md](./concepts/SRO_ARCHITECTURE_OVERVIEW.md)** - Gesamtarchitektur
2. **[XOT_GENERATIVE_COT_CONCEPT.md](./concepts/XOT_GENERATIVE_COT_CONCEPT.md)** - Reasoning Engine
3. **[SPO_KNOWLEDGE_GRAPH_CONCEPT.md](./concepts/SPO_KNOWLEDGE_GRAPH_CONCEPT.md)** - Wissensstruktur

### Erweiterte Konzepte
4. **[CONSTITUTIONAL_AI_AXIOM_CONCEPT.md](./concepts/CONSTITUTIONAL_AI_AXIOM_CONCEPT.md)** - Werte-System
5. **[RECURSIVE_LLM_CONCEPT.md](./concepts/RECURSIVE_LLM_CONCEPT.md)** - Skalierung (10M+ Tokens)
6. **[REDDIT_VALIDATION_CONCEPT.md](./concepts/REDDIT_VALIDATION_CONCEPT.md)** - Social Validation

### Hardening-Konzepte (NEU)
7. **[BIAS_MAPPING_STRATEGY.md](./concepts/BIAS_MAPPING_STRATEGY.md)** - Perspektiven-Graph
8. **[EPISTEMIC_MCTS_CONCEPT.md](./concepts/EPISTEMIC_MCTS_CONCEPT.md)** - Info-Gathering
9. **[PRIVACY_HARDENING_CONCEPT.md](./concepts/PRIVACY_HARDENING_CONCEPT.md)** - Cloud-Privacy

---

## 🔧 Implementation Clusters

Implementiere in **4 Clustern** (Reihenfolge beachten):

### 🔴 CLUSTER 1: Motor-Integration (RLM & XoT)

**Ziel:** Recursive Language Models als Standard-Interface + XoT-Heuristik

#### Tasks:

**1.1 RLM Environment Setup**
```python
# src/core/rlm_environment.py
class RLMEnvironment:
    """Verwaltet externe Daten für Recursive LLM"""

    def __init__(self):
        self.variables = {}  # Dataset als Python-Variablen
        self.code_history = []

    def load_dataset(self, name: str, data: Any):
        """Lädt Daten NICHT ins LLM, sondern als Variable"""

    def execute_code(self, code: str) -> ExecutionResult:
        """Führt LLM-generierten Code in Sandbox aus"""
```

**1.2 Recursive LLM Wrapper**
```python
# src/core/recursive_llm.py
class RecursiveLLM:
    """LLM das sich selbst rekursiv aufrufen kann"""

    def query_with_massive_context(
        self,
        task: str,
        dataset_name: str,
        recursion_budget: int = 5
    ) -> str:
        """Verarbeitet Daten größer als Context Window"""
```

**1.3 XoT Simulator**
```python
# src/core/xot_simulator.py
class XoTSimulator:
    """Schnelle Heuristik für MCTS-Pfad-Schätzung"""

    def simulate_path(
        self,
        node: MCTSNode,
        depth: int = 3
    ) -> Trajectory:
        """Simuliert Gedanken-Trajektorie ohne volle Ausführung"""

    def estimate_success(self, path: List[MCTSNode]) -> float:
        """Schätzt Erfolgswahrscheinlichkeit dieses Pfades"""
```

**Deliverables:**
- [ ] `src/core/rlm_environment.py` (200 LOC)
- [ ] `src/core/recursive_llm.py` (300 LOC)
- [ ] `src/core/xot_simulator.py` (250 LOC)
- [ ] Unit Tests: `tests/test_rlm.py`
- [ ] Integration Test: Reddit-Scraping mit 10k Posts

---

### 🟠 CLUSTER 2: Sequential Persistence Layer

**Ziel:** Stateful Reasoning mit Checkpoint-Logik

#### Tasks:

**2.1 State Database Schema**
```sql
-- data/schema.sql
CREATE TABLE mcts_states (
    session_id TEXT PRIMARY KEY,
    tree_structure BLOB,  -- Serialized MCTS Tree
    timestamp DATETIME,
    checkpoint_id INTEGER
);

CREATE TABLE prm_scores (
    node_id TEXT,
    step_id INTEGER,
    score FLOAT,
    reasoning TEXT,
    timestamp DATETIME
);

CREATE TABLE deep_graph_triples (
    triple_id TEXT PRIMARY KEY,
    subject TEXT,
    predicate TEXT,
    object TEXT,
    source TEXT,
    source_bias_vector BLOB,
    verified_at DATETIME,
    confidence FLOAT
);
```

**2.2 Checkpoint Manager**
```python
# src/core/checkpoint_manager.py
class CheckpointManager:
    """Verwaltet MCTS-Checkpoints für Langzeit-Prozesse"""

    def save_checkpoint(
        self,
        session_id: str,
        mcts_tree: MCTSTree,
        deep_graph: DeepGraph
    ):
        """Speichert aktuellen Zustand"""

    def restore_checkpoint(
        self,
        session_id: str
    ) -> Tuple[MCTSTree, DeepGraph]:
        """Lädt letzten validierten Zustand"""

    def list_checkpoints(self, session_id: str) -> List[Checkpoint]:
        """Zeigt alle Checkpoints für Session"""
```

**Deliverables:**
- [ ] `data/schema.sql` (150 LOC)
- [ ] `src/core/checkpoint_manager.py` (400 LOC)
- [ ] `src/core/state_persistence.py` (300 LOC)
- [ ] Migration Script: `scripts/migrate_to_stateful.py`
- [ ] Recovery Test: Simuliere Absturz + Recovery

---

### 🟡 CLUSTER 3: Perspektiven-Graph & Bias-Mapping

**Ziel:** Bias als Information, nicht als Fehler

#### Tasks:

**3.1 Bias Vector Dataclass**
```python
# src/models/bias_vector.py
@dataclass
class BiasVector:
    """Mathematische Repräsentation von Source-Perspektive"""

    risk_affinity: float  # -1.0 (konservativ) bis +1.0 (spekulativ)
    time_horizon: float  # -1.0 (kurzfristig) bis +1.0 (langfristig)
    centralization: float  # -1.0 (dezentral) bis +1.0 (zentralisiert)
    empirical_depth: float  # 0.0 (anekdotisch) bis 1.0 (datengetrieben)
    profit_motive: float  # 0.0 (neutral) bis 1.0 (kommerzielle Agenda)

    def distance_to(self, other: BiasVector) -> float:
        """Berechnet Euklidische Distanz"""

    def to_vector(self) -> np.ndarray:
        """Konvertiert zu NumPy-Array für ML"""
```

**3.2 Source Profiler**
```python
# src/validation/source_profiler.py
class SourceProfiler:
    """Extrahiert Bias-Profil aus Texten"""

    def profile_source(
        self,
        source_name: str,
        sample_texts: List[str]
    ) -> BiasVector:
        """LLM-basierte + Code-basierte Bias-Analyse"""
```

**3.3 Biased Triple (erweiterte SPO)**
```python
# src/models/biased_triple.py
@dataclass
class BiasedTriple:
    """SPO-Triplett mit Bias-Awareness"""

    subject: str
    predicate: str
    object: str

    # Provenance
    source: str
    source_bias: BiasVector

    # Sentiment
    sentiment: str  # positive | negative | neutral
    confidence: float

    # Bias-Einfluss
    bias_influence: BiasInfluence
```

**3.4 Contrastive Debate Engine**
```python
# src/reasoning/contrastive_debate.py
class ContrastiveDebate:
    """Synthetische Debatte zwischen widersprüchlichen Quellen"""

    def run_debate(
        self,
        position_a: BiasedTriple,
        position_b: BiasedTriple,
        rounds: int = 3
    ) -> DebateResult:
        """Lässt zwei Positionen gegeneinander antreten"""
```

**Deliverables:**
- [ ] `src/models/bias_vector.py` (200 LOC)
- [ ] `src/validation/source_profiler.py` (400 LOC)
- [ ] `src/models/biased_triple.py` (150 LOC)
- [ ] `src/reasoning/contrastive_debate.py` (350 LOC)
- [ ] Visualization: `scripts/visualize_bias_landscape.py`
- [ ] Case Study: AWS vs. r/Selfhosted Bias-Vergleich

---

### 🟢 CLUSTER 4: Epistemisches MCTS & Dynamic Scraping

**Ziel:** MCTS für optimale Info-Gathering-Strategie

#### Tasks:

**4.1 Uncertainty Model**
```python
# src/reasoning/uncertainty_model.py
class UncertaintyModel:
    """Berechnet Unsicherheit im Knowledge Graph"""

    def calculate_node_uncertainty(
        self,
        node: GraphNode
    ) -> float:
        """Unsicherheit basierend auf Konflikten, Bias-Varianz, Coverage"""

    def calculate_global_uncertainty(self) -> float:
        """Gesamtunsicherheit über alle Nodes"""
```

**4.2 Information Actions**
```python
# src/scraping/information_action.py
@dataclass
class InformationAction:
    """Ein möglicher Scraping/Query-Task"""

    type: str  # scrape_reddit | query_api | transcribe_youtube
    params: Dict
    cost_estimate: Dict[str, float]  # time, tokens
    expected_gain: float  # Geschätzte Unsicherheits-Reduktion

def calculate_voi(action: InformationAction) -> float:
    """Value of Information = Gain / Cost"""
```

**4.3 Epistemisches MCTS**
```python
# src/reasoning/epistemic_mcts.py
class EpistemicMCTS:
    """MCTS für Information Gathering"""

    def select_best_action(self) -> InformationAction:
        """Wähle Scraping-Aktion mit höchstem VoI"""

    def simulate_information_action(
        self,
        action: InformationAction
    ) -> float:
        """Simuliere Effekt dieser Info-Quelle"""
```

**4.4 Dynamic Scraping Queue**
```python
# src/scraping/dynamic_queue.py
class DynamicScrapingQueue:
    """Auto-priorisierte Scraping-Queue basierend auf MCTS"""

    def update_queue(self):
        """MCTS entscheidet: Top-3 Aktionen"""

    def execute_next(self) -> ScrapingResult:
        """Führe nächste Aktion aus, update Uncertainty"""
```

**Deliverables:**
- [ ] `src/reasoning/uncertainty_model.py` (300 LOC)
- [ ] `src/scraping/information_action.py` (200 LOC)
- [ ] `src/reasoning/epistemic_mcts.py` (500 LOC)
- [ ] `src/scraping/dynamic_queue.py` (350 LOC)
- [ ] Integration: Two-Level MCTS (Reasoning + Epistemic)
- [ ] Benchmark: VoI-Accuracy über 100 Queries

---

### 🔵 CLUSTER 5: Privacy Hardening (Cloud Safety)

**Ziel:** Cloud-APIs nutzen ohne Daten-Lecks

#### Tasks:

**5.1 Privacy Sanitizer**
```python
# src/privacy/sanitizer.py
class PrivacySanitizer:
    """Entfernt persönliche Infos vor Cloud-Calls"""

    def sanitize_prompt(
        self,
        prompt: str,
        context: Dict
    ) -> SanitizedPrompt:
        """Abstrahiert Locations, Amounts, Axiome"""

    def desanitize_response(
        self,
        response: str,
        entity_map: Dict
    ) -> str:
        """Setzt Original-Entities wieder ein"""
```

**5.2 Axiom Protection**
```python
# src/privacy/axiom_protection.py
AXIOM_CATEGORIES = {
    "roi_threshold": "VALUE_FINANCIAL_PRUDENCE",
    "data_sovereignty": "VALUE_PRIVACY",
    # ...
}

def sanitize_axiom(axiom_id: str) -> str:
    """Konvertiere zu generischer Kategorie"""
```

**5.3 Hybrid LLM Orchestrator**
```python
# src/core/hybrid_llm.py
class HybridLLMOrchestrator:
    """Routet Tasks zu Local oder Cloud basierend auf Sensitivity"""

    def query(self, prompt: str, task_type: str) -> str:
        if self._is_sensitive(prompt, task_type):
            return self.local_llm.query(prompt)
        else:
            sanitized = self.sanitizer.sanitize(prompt)
            return self.cloud_llm.query(sanitized)
```

**5.4 Cloud Audit Logger**
```python
# src/privacy/audit_logger.py
class CloudAuditLogger:
    """Loggt alle Cloud-Calls für Audit"""

    def log_call(self, ...):
        """Persistiere Call-Details"""

    def generate_privacy_report(self) -> str:
        """Monatlicher Privacy-Report"""
```

**Deliverables:**
- [ ] `src/privacy/sanitizer.py` (450 LOC)
- [ ] `src/privacy/axiom_protection.py` (200 LOC)
- [ ] `src/core/hybrid_llm.py` (350 LOC)
- [ ] `src/privacy/audit_logger.py` (300 LOC)
- [ ] Privacy Tests: Leak-Detection Testsuite
- [ ] GDPR Compliance Check

---

## 📋 Cross-Cutting Concerns

### Integration mit bestehendem Code

**Zu modifizieren:**
1. `src/core/mcts_engine.py`
   - Integriere XoT-Heuristik
   - Bias-Aware Selection
   - Checkpoint-Calls

2. `src/core/tot_manager.py`
   - SPO-Extraktion statt flache Responses
   - BiasedTriple statt Triple

3. `api_server.py`
   - Neue Endpoints für Bias-Profiling
   - Checkpoint-Management Routes
   - Privacy-Status Dashboard

### Neue Module

```
src/
├── core/
│   ├── rlm_environment.py           # NEU
│   ├── recursive_llm.py             # NEU
│   ├── xot_simulator.py             # NEU
│   ├── checkpoint_manager.py        # NEU
│   ├── hybrid_llm.py                # NEU
├── models/
│   ├── bias_vector.py               # NEU
│   ├── biased_triple.py             # NEU
├── reasoning/
│   ├── uncertainty_model.py         # NEU
│   ├── epistemic_mcts.py            # NEU
│   ├── contrastive_debate.py        # NEU
├── validation/
│   ├── source_profiler.py           # NEU
├── scraping/
│   ├── information_action.py        # NEU
│   ├── dynamic_queue.py             # NEU
├── privacy/
│   ├── sanitizer.py                 # NEU
│   ├── axiom_protection.py          # NEU
│   ├── audit_logger.py              # NEU
```

---

## 🎯 Success Metrics

### Funktionale Metriken
```python
@dataclass
class ImplementationSuccess:
    # RLM
    rlm_max_context_processed: int  # Ziel: >1M Tokens
    rlm_cost_reduction: float  # Ziel: >70%

    # Bias-Mapping
    source_profiles_created: int  # Ziel: >20
    bias_distance_accuracy: float  # Ziel: >0.85

    # Epistemisches MCTS
    avg_voi_prediction_error: float  # Ziel: <0.15
    scraping_efficiency_gain: float  # Ziel: >50%

    # Privacy
    sanitization_coverage: float  # Ziel: 100%
    privacy_leak_detected: int  # Ziel: 0
```

---

## 🚀 Implementation Roadmap

### Woche 1: Cluster 1 + 2
```
Tag 1-2: RLM Environment + Recursive LLM
Tag 3-4: XoT Simulator
Tag 5-7: State Persistence + Checkpoints
```

### Woche 2: Cluster 3
```
Tag 1-2: Bias Vector + Source Profiler
Tag 3-4: Biased Triple Integration
Tag 5-7: Contrastive Debate + Visualization
```

### Woche 3: Cluster 4 + 5
```
Tag 1-3: Epistemisches MCTS + VoI
Tag 4-5: Dynamic Scraping Queue
Tag 6-7: Privacy Hardening
```

### Woche 4: Integration + Testing
```
Tag 1-3: End-to-End Integration Tests
Tag 4-5: Performance Benchmarking
Tag 6-7: Documentation + Demo
```

---

## 📖 Documentation Requirements

Für jeden Cluster:
1. **Code Comments** - Inline Docstrings
2. **API Documentation** - Sphinx/MkDocs
3. **Integration Guide** - Wie andere Module nutzen
4. **Test Coverage** - Min. 80% für neue Module
5. **Example Notebook** - Jupyter mit Use-Case

---

## ⚠️ Critical Dependencies

### Externe Libraries
```bash
pip install:
- networkx  # Graph Operations
- numpy  # Bias-Vektoren
- sqlite3  # State Persistence
- praw  # Reddit Scraping
- matplotlib  # Bias Visualization
- cryptography  # Privacy (Hash, Encryption)
```

### Modell-Anforderungen
- **Lokal:** Llama-3-70B (24GB VRAM min.)
- **Cloud:** Claude Opus 4 oder GPT-4 (für CEO-Tasks)

---

## 🔒 Security Checklist

- [ ] Alle Axiome nur lokal gespeichert (niemals in Logs)
- [ ] Cloud-Prompts durchlaufen Sanitizer
- [ ] Audit-Logs für alle Cloud-Calls
- [ ] Code-Sandbox für RLM (kein `exec` von User-Input)
- [ ] Differential Privacy für Finanz-Daten
- [ ] GDPR-Compliance-Check

---

## 📊 Final Deliverable

**Ein voll-funktionsfähiges SRO-System das:**

1. ✅ 10M+ Token-Kontexte via RLM verarbeitet
2. ✅ Bias mathematisch im Perspektiven-Graph kartiert
3. ✅ Automatisch optimale Info-Quellen via MCTS findet
4. ✅ Privacy-konform Cloud-APIs nutzt
5. ✅ Mehrstündige Prozesse via Checkpoints unterbricht/fortsetzt
6. ✅ Synthetische Debatten für Konflikt-Auflösung führt

---

**Los geht's! 🚀**

**Nächster Schritt:** Cluster 1 starten mit RLM Environment Setup
