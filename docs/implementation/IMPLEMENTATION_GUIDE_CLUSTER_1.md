# Implementation Guide - Cluster 1: Foundations

**Start Date:** 2026-01-15
**Estimated Duration:** 1-2 Wochen
**Status:** 🟡 Ready to Start
**Priority:** KRITISCH

---

## Überblick

Cluster 1 implementiert die **Foundations** des SRO-Systems:
- ✅ SPO-Extraktion (strukturierte Tripletts statt Fließtext)
- ✅ XoT-Simulator (schnelle Heuristik vor MCTS)
- ✅ Token-Budget-Manager (verhindert Ewigkeitsschleifen)
- ⚠️ GraphManager SPO-Extension (evolutionär erweitern)

**Warum Cluster 1 zuerst?**
> "Ohne strukturierte Fakten (Tripletts) ist der 'Motor' (MCTS) zwar stark, hat aber kein strukturiertes 'Futter' zum Verarbeiten." - Gemini Review

---

## Komponenten-Übersicht

### 1. SPOExtractor (`src/core/spo_extractor.py`) - NEU
**Zweck:** Strukturierte Triplett-Extraktion aus LLM-Responses

**Input:**
```python
response_text = "Die Solaranlage hat eine ROI-Periode von 15-20 Jahren, abhängig von der Strompreisentwicklung."
```

**Output:**
```python
[
    SPOTriplet(
        subject="Solaranlage",
        predicate="ROI-Periode",
        object="15-20 Jahre",
        confidence=0.85,
        provenance={
            "source_id": "response_123",
            "extraction_method": "llm_structured",
            "model_used": "qwen-2.5-14b"
        }
    ),
    SPOTriplet(
        subject="ROI-Periode",
        predicate="abhängig_von",
        object="Strompreisentwicklung",
        confidence=0.75,
        provenance={...}
    )
]
```

**Anforderungen:**
- LLM-based Extraktion (kein Regex/NER)
- Multiple Tripletts pro Response
- Provenance Tracking (woher kommt das Triplet?)
- Confidence Scoring
- Tier Assignment (Bronze by default)

**Dependencies:**
- ModelOrchestrator (für LLM-Calls)
- SQLite (für Persistence)

---

### 2. XoTSimulator (`src/core/xot_simulator.py`) - NEU
**Zweck:** Schnelle Gedanken-Simulation vor MCTS-Selection

**Konzept:**
XoT ist ein **"Vor-Denker"** - er schätzt schnell ab, welche MCTS-Nodes vielversprechend sind, OHNE aufwendige Simulation.

**Flow:**
```
1. MCTS ruft select() auf
2. BEVOR UCB1 berechnet wird:
   → XoT simuliert 3-Step-Vorschau für jeden Child
   → XoT gibt Prior Probability (0-1) zurück
3. MCTS nutzt Prior für UCB1-Boost
4. Node mit höchstem boosted UCB1 wird selected
```

**Beispiel:**
```python
# Ohne XoT
node_a.ucb1 = 0.5 + 0.3 = 0.8  # exploitation + exploration

# Mit XoT
xot_prior = xot.simulate_quick(node_a)  # → 0.9 (looks promising!)
node_a.ucb1 = 0.5 + 0.3 + (xot_prior * 0.2) = 0.98  # boosted!
```

**Anforderungen:**
- Eigenes schnelles LLM (Qwen-2.5-14B oder Llama-3.1-8B)
- Sehr kurze Prompts (<500 Tokens)
- Heuristik-Stil (Bauchgefühl, nicht perfekt)
- Latenz <2 Sekunden pro Simulation
- Integration in MCTSEngine._compute_ucb1()

**Dependencies:**
- ModelOrchestrator (für XoT-Modell)
- ToTManager (für Node-Kontext)

---

### 3. TokenBudgetManager (`src/core/token_budget_manager.py`) - NEU
**Zweck:** Verhindert Token-Verschwendung in unwichtigen MCTS-Ästen

**Problem:**
MCTS könnte endlos in Nebenpfaden explorieren und dabei Tokens verschwenden.

**Lösung:**
```python
# Gesamt-Budget pro Session
total_budget = 500_000  # 500k Tokens

# Node-Budget basierend auf Wichtigkeit
important_node.token_budget = 50_000  # High-priority node
unimportant_node.token_budget = 5_000  # Low-priority node

# Automatisches Pruning bei Überschreitung
if node.tokens_used > node.token_budget:
    tot_manager.prune_branch(node.node_id, reason="token_budget_exceeded")
```

**Anforderungen:**
- Dynamische Budget-Zuteilung (wichtige Nodes bekommen mehr)
- Token-Tracking pro Node
- Integration mit MCTSEngine.simulate()
- Pruning bei Budget-Überschreitung
- Konfigurierbare Budgets (Profile-basiert)

**Dependencies:**
- MCTSEngine (für Simulation-Tracking)
- ToTManager (für Pruning)

---

### 4. GraphManager SPO-Extension - ERWEITERN
**Zweck:** SPO-Methoden hinzufügen (parallel zu Legacy NetworkX)

**Plan:**
```python
class GraphManager:
    def __init__(self, ...):
        self.graph = nx.DiGraph()  # Legacy (BEHALTEN!)
        self.spo_db = SPODatabase()  # NEU: SQLite Backend

    # === Legacy Methods (BEHALTEN) ===
    def add_node(self, node_id, node_type, content, ...):
        """Alte Methode - bleibt für Backward Compatibility"""
        self.graph.add_node(node_id, type=node_type, content=content, ...)

    def add_edge(self, source, target, edge_type, ...):
        """Alte Methode - bleibt"""
        self.graph.add_edge(source, target, type=edge_type, ...)

    # === NEU: SPO Methods ===
    def add_spo_triplet(self, triplet: SPOTriplet) -> str:
        """Neuer SPO-Triplett hinzufügen (Bronze-Tier)"""
        triplet_id = self.spo_db.insert(triplet)
        return triplet_id

    def get_spo_triplets(
        self,
        subject: Optional[str] = None,
        tier: Optional[str] = None
    ) -> List[SPOTriplet]:
        """SPO-Tripletts abfragen (mit Filter)"""
        return self.spo_db.query(subject=subject, tier=tier)

    def promote_triplet(self, triplet_id: str, new_tier: str) -> bool:
        """Triplet zu höherem Tier befördern (Bronze → Silver → Gold)"""
        return self.spo_db.promote(triplet_id, new_tier)

    def verify_triplet(
        self,
        triplet_id: str,
        sources: List[str]
    ) -> float:
        """Multi-Source Verification für Tier-Promotion"""
        # Cluster 2 Feature (stub for now)
        pass
```

**Anforderungen:**
- Keine Breaking Changes zu bestehendem Code!
- SQLite Backend für SPO (siehe SPODatabase unten)
- Migration Helper für alte Nodes → SPO (später)
- Tier-System (Bronze/Silver/Gold)

---

## Technische Spezifikationen

### SPODatabase (SQLite Backend)

**Schema:**
```sql
-- SPO-Tripletts mit Tiered RAG
CREATE TABLE spo_triplets (
    id TEXT PRIMARY KEY,  -- spo_uuid
    subject TEXT NOT NULL,
    predicate TEXT NOT NULL,
    object TEXT NOT NULL,
    confidence REAL CHECK(confidence >= 0.0 AND confidence <= 1.0),
    tier TEXT CHECK(tier IN ('bronze', 'silver', 'gold')) DEFAULT 'bronze',
    created_at TEXT NOT NULL,
    updated_at TEXT,

    -- Provenance (JSON)
    provenance_json TEXT NOT NULL,
    -- {
    --   "source_id": "response_123",
    --   "extraction_method": "llm_structured",
    --   "model_used": "qwen-2.5-14b",
    --   "verified": false,
    --   "verification_count": 0,
    --   "verification_sources": []
    -- }

    -- Metadata (JSON)
    metadata_json TEXT
    -- {
    --   "domain": "economics",
    --   "axiom_scores": {"opportunity_cost": 0.85},
    --   "bias_vector": {...}
    -- }
);

-- Indizes für Performance
CREATE INDEX idx_subject ON spo_triplets(subject);
CREATE INDEX idx_predicate ON spo_triplets(predicate);
CREATE INDEX idx_object ON spo_triplets(object);
CREATE INDEX idx_tier ON spo_triplets(tier);
CREATE INDEX idx_confidence ON spo_triplets(confidence DESC);

-- Full-Text-Search (optional, für Queries)
CREATE VIRTUAL TABLE spo_fts USING fts5(
    subject, predicate, object,
    content=spo_triplets
);
```

**Location:** `data/sessions/{session_id}/spo_graph.db`

---

### XoT Model Configuration

**Model:** Qwen-2.5-14B-Instruct-Q4_K_M
**Download:**
```bash
# Via llama.cpp
wget https://huggingface.co/Qwen/Qwen2.5-14B-Instruct-GGUF/resolve/main/qwen2.5-14b-instruct-q4_k_m.gguf -P models/
```

**Config:** `config/models/xot_qwen_llamacpp.json`
```json
{
    "model_id": "xot_qwen",
    "provider": "llamacpp",
    "path": "models/qwen2.5-14b-instruct-q4_k_m.gguf",
    "capabilities": ["reasoning"],
    "context_window": 32768,
    "purpose": "xot_simulation",
    "temperature": 0.3,
    "max_tokens": 100,
    "n_gpu_layers": 35,
    "n_ctx": 8192,
    "n_batch": 512
}
```

**Alternative:** Llama-3.1-8B (wenn VRAM knapp)
```json
{
    "model_id": "xot_llama",
    "provider": "llamacpp",
    "path": "models/llama-3.1-8b-instruct-q4_k_m.gguf",
    ...
}
```

---

### XoT Prompt Template

**Stil:** Sehr kurz, Heuristik, <500 Tokens

```python
XOT_SIMULATION_PROMPT = """You are a research heuristic. Quickly estimate if this path is promising.

Current Path:
{path_summary}

Next Question:
{node_question}

Rate likelihood of success (0.0 = dead end, 1.0 = very promising).
Consider: relevance, actionability, logical flow.

Respond with ONLY a number: 0.0-1.0
"""
```

**Beispiel:**
```
Input:
  Path: "What e-commerce niche?" → "High friction markets?"
  Next: "Research solar installation pain points"

Output: 0.85
```

---

## Implementation Checklist

### Phase 1: SPO Foundation (Woche 1)

#### Sprint 1.1: SQLite Backend
- [ ] Create `src/core/spo_database.py`
- [ ] Implement SPODatabase class
  - [ ] `insert(triplet: SPOTriplet) -> str`
  - [ ] `query(subject, predicate, object, tier) -> List[SPOTriplet]`
  - [ ] `promote(triplet_id, new_tier) -> bool`
  - [ ] `get_by_id(triplet_id) -> SPOTriplet`
- [ ] Create SQLite Schema (siehe oben)
- [ ] Add FTS5 Full-Text-Search
- [ ] Unit Tests (pytest)

**Deliverable:** SQLite Backend funktioniert mit CRUD operations

---

#### Sprint 1.2: SPO Extractor
- [ ] Create `src/core/spo_extractor.py`
- [ ] Implement SPOExtractor class
  - [ ] `extract_from_text(text: str, context: Dict) -> List[SPOTriplet]`
  - [ ] LLM-Prompt Engineering (strukturierte Extraktion)
  - [ ] JSON Parsing mit Fallback
  - [ ] Confidence Scoring
  - [ ] Provenance Tracking
- [ ] Integration mit ModelOrchestrator
- [ ] Add SPOTriplet Dataclass to `src/models/unified_session.py`
- [ ] Unit Tests mit Mock-Responses

**Deliverable:** SPO-Tripletts werden aus Text extrahiert

---

#### Sprint 1.3: GraphManager Extension
- [ ] Extend `src/core/graph_manager.py`
  - [ ] Add `self.spo_db = SPODatabase()` in `__init__`
  - [ ] Implement `add_spo_triplet(triplet)` method
  - [ ] Implement `get_spo_triplets(subject, tier)` method
  - [ ] Implement `promote_triplet(triplet_id, new_tier)` method
- [ ] Keep all existing methods (NO breaking changes!)
- [ ] Add migration helper (stub for Cluster 2)
- [ ] Integration Tests

**Deliverable:** GraphManager unterstützt SPO parallel zu Legacy

---

#### Sprint 1.4: ToTManager Integration
- [ ] Extend `src/core/tot_manager.py`
  - [ ] In `expand_node()`: Call SPOExtractor zusätzlich zu Entity-Extraction
  - [ ] Store extracted SPO-Tripletts in GraphManager
  - [ ] Add triplet IDs to node.graph_facts
- [ ] Update UnifiedSession.Response to include `spo_triplets: List[str]`
- [ ] Integration Tests

**Deliverable:** ToT expansion extrahiert und speichert SPO-Tripletts

---

### Phase 2: XoT Integration (Woche 2)

#### Sprint 2.1: XoT Model Setup
- [ ] Download Qwen-2.5-14B-Instruct-Q4_K_M
- [ ] Create `config/models/xot_qwen_llamacpp.json`
- [ ] Test model loading with llama-cpp-python
- [ ] Benchmark inference speed (target: <2s per call)
- [ ] Add to ModelOrchestrator (new purpose: "xot_simulation")

**Deliverable:** XoT-Modell läuft mit <2s Latenz

---

#### Sprint 2.2: XoT Simulator
- [ ] Create `src/core/xot_simulator.py`
- [ ] Implement XoTSimulator class
  - [ ] `simulate_quick(node: ToTNode, depth: int = 3) -> float`
  - [ ] Build path summary (last 3 nodes)
  - [ ] Generate XoT prompt
  - [ ] Call XoT model
  - [ ] Parse prior probability (0.0-1.0)
- [ ] Prompt Engineering (sehr kurz, <500 Tokens)
- [ ] Error handling (fallback to 0.5)
- [ ] Unit Tests

**Deliverable:** XoT-Simulator gibt Prior Probabilities zurück

---

#### Sprint 2.3: MCTS Integration
- [ ] Extend `src/core/mcts_engine.py`
  - [ ] Add `xot_simulator: Optional[XoTSimulator]` to `__init__`
  - [ ] Add `xot_weight: float = 0.2` (boost factor)
  - [ ] In `_compute_ucb1()`: Add XoT prior boost
    ```python
    if self.xot_simulator:
        xot_prior = self.xot_simulator.simulate_quick(node)
        ucb1 += xot_prior * self.xot_weight
    ```
- [ ] Add XoT stats to `get_stats()`
- [ ] Integration Tests

**Deliverable:** MCTS nutzt XoT für bessere Node-Selection

---

### Phase 3: Token Budget (Woche 2)

#### Sprint 3.1: Token Budget Manager
- [ ] Create `src/core/token_budget_manager.py`
- [ ] Implement TokenBudgetManager class
  - [ ] `__init__(total_budget: int, default_node_budget: int)`
  - [ ] `allocate_budget(node: ToTNode, ucb1_score: float) -> int`
  - [ ] `track_tokens(node_id: str, tokens_used: int)`
  - [ ] `check_budget(node_id: str) -> bool`
  - [ ] `get_remaining_budget(node_id: str) -> int`
- [ ] Dynamic allocation formula:
  ```python
  node_budget = base_budget * (1 + ucb1_score)
  # High UCB1 → more budget
  ```
- [ ] Unit Tests

**Deliverable:** Token Budget Manager funktioniert standalone

---

#### Sprint 3.2: MCTS Integration
- [ ] Extend `src/core/mcts_engine.py`
  - [ ] Add `token_budget_manager: Optional[TokenBudgetManager]` to `__init__`
  - [ ] In `simulate()`: Track token usage
  - [ ] Before simulation: Check if budget available
  - [ ] If budget exceeded: Auto-prune node
- [ ] Add budget stats to `get_stats()`
- [ ] Integration Tests

**Deliverable:** MCTS respektiert Token-Budgets und pruned bei Überschreitung

---

#### Sprint 3.3: Configuration
- [ ] Add token_budget config to Value Profiles
  ```json
  {
    "profile_id": "balanced",
    "token_budget": {
      "total_budget": 500000,
      "default_node_budget": 10000,
      "min_node_budget": 1000,
      "max_node_budget": 100000
    }
  }
  ```
- [ ] Load from config in SessionManager
- [ ] Documentation

**Deliverable:** Token Budgets sind konfigurierbar per Profile

---

## Testing Strategy

### Unit Tests
Jede Komponente hat eigene Unit Tests:
- `tests/test_spo_extractor.py`
- `tests/test_xot_simulator.py`
- `tests/test_token_budget_manager.py`
- `tests/test_spo_database.py`

### Integration Tests
Testen Zusammenspiel:
- `tests/integration/test_tot_spo_extraction.py` (ToT → SPO → DB)
- `tests/integration/test_mcts_xot_integration.py` (MCTS + XoT)
- `tests/integration/test_mcts_token_budget.py` (MCTS + Budget)

### End-to-End Test
Kompletter Flow:
```python
def test_cluster_1_e2e():
    # 1. Create session
    session = session_mgr.create_session(...)

    # 2. Create ToT root
    root_id = tot_mgr.create_root("Test question")

    # 3. Decompose with XoT
    tot_mgr.decompose_question(root_id)  # Uses XoT internally

    # 4. Expand node (extracts SPO)
    tot_mgr.expand_node(child_id)

    # 5. Verify SPO in DB
    triplets = graph_mgr.get_spo_triplets(subject="...")
    assert len(triplets) > 0

    # 6. Run MCTS with budget
    mcts.iterate(10)

    # 7. Verify budget respected
    assert token_budget_mgr.get_remaining_budget(session_id) > 0
```

---

## Dependencies & Prerequisites

### Python Packages
```bash
pip install llama-cpp-python  # XoT model
pip install pytest pytest-asyncio  # Testing
# Alle anderen bereits installiert
```

### Models
```bash
# Qwen-2.5-14B (~8GB)
wget https://huggingface.co/Qwen/Qwen2.5-14B-Instruct-GGUF/resolve/main/qwen2.5-14b-instruct-q4_k_m.gguf -P models/
```

### Hardware Requirements
- **VRAM:** 10GB+ (für Qwen-14B)
  - Falls knapp: Llama-3.1-8B (~5GB)
- **RAM:** 16GB+
- **Disk:** 10GB+ (für Model + SQLite DBs)

---

## Success Criteria

### Cluster 1 ist erfolgreich wenn:

1. ✅ **SPO-Extraktion funktioniert**
   - Tripletts werden aus Responses extrahiert
   - SQLite DB speichert Tripletts korrekt
   - Provenance ist nachvollziehbar

2. ✅ **XoT beschleunigt MCTS**
   - Prior Probabilities verbessern Node-Selection
   - Latenz <2 Sekunden pro XoT-Call
   - MCTS findet bessere Pfade schneller

3. ✅ **Token-Budget verhindert Verschwendung**
   - Unwichtige Nodes werden früh gepruned
   - Budget-Überschreitungen werden geloggt
   - Gesamtbudget wird nicht überschritten

4. ✅ **Keine Breaking Changes**
   - Alle alten Tests laufen weiter
   - Legacy NetworkX-Graph funktioniert parallel
   - Backward Compatibility gewährleistet

---

## Troubleshooting

### Problem: XoT zu langsam (>5s)
**Lösung:**
- Reduce n_ctx to 4096
- Use Llama-3.1-8B instead
- Increase n_batch to 1024

### Problem: SPO-Extraktion zu ungenau
**Lösung:**
- Improve prompt (add examples)
- Use better model (Qwen-2.5-32B)
- Add confidence threshold (nur >0.7 speichern)

### Problem: Token-Budget zu restriktiv
**Lösung:**
- Increase total_budget in config
- Lower base_budget allocation
- Disable for critical nodes (flag in ToTNode)

---

## Next Steps (nach Cluster 1)

Nach erfolgreichem Abschluss von Cluster 1:
→ **Cluster 2: Tiered RAG + Axiom Judge**

Siehe: `docs/IMPLEMENTATION_GUIDE_CLUSTER_2.md` (wird erstellt nach Cluster 1 Completion)

---

**Status:** 🟡 Bereit zum Start
**Review:** ✅ Gemini Approved
**Let's Build!** 🚀
