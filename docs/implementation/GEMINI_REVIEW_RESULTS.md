# Gemini Review Results - SRO Implementation

**Review Date:** 2026-01-15
**Reviewer:** Gemini Advanced
**Dokumente:** 9 Konzept-Dateien + Implementation Analysis
**Status:** ✅ Approved mit Design-Entscheidungen

---

## Executive Summary

Gemini hat das SRO-Konzept reviewed und als **technisch korrekt und umsetzbar** bestätigt. Die bestehende Code-Basis (70% Logik-Ebene implementiert) ermöglicht eine **evolutionäre Migration** statt Neuschreibung.

**Haupterkenntnis:** SPO-Extraktion muss in Cluster 1 (nicht Cluster 2) vorgezogen werden, da ohne strukturierte Tripletts der MCTS-Motor kein strukturiertes "Futter" hat.

---

## 1. Strategischer Review

### ✅ Technisches Verständnis & Kohärenz

**Gemini-Zitat:**
> "Das Zusammenspiel zwischen **epistemischem MCTS** (Suche nach Erkenntnis) und dem **Perspektiven-Graphen** (Bias-Mapping) ist das Herzstück. Die Erkenntnis, dass Bias eine *Information* ist, hebt das System weit über herkömmliche RAG-Systeme hinaus."

**Bestätigung:**
- ✅ Inference-time Compute Scaling ist für lokale Hardware optimal
- ✅ RLAIF + Abliterated Models Strategie ist korrekt
- ✅ Drei-Ebenen-Architektur (Kontrolle/Logik/Wissen) ist kohärent
- ✅ Bias-as-Information Paradigma ist technisch fundiert

---

### ⚠️ Was fehlt noch?

Gemini identifizierte 2 zusätzliche Komponenten:

#### 1. Conflict Resolution Strategy
**Problem:** Wenn zwei hoch-verifizierte Pfade zu gegensätzlichen Handlungsanweisungen führen, braucht MCTS eine "Tie-Breaker"-Logik.

**Lösung:** Gewichtete Axiom-Hierarchie
```python
class AxiomHierarchy:
    """
    Auflösung von Axiom-Konflikten durch Prioritäts-Hierarchie.

    Beispiel: "Sicherheit schlägt Rendite"
    - Axiom "risk_management" (priority: critical) > "opportunity_cost" (priority: high)
    """
    def resolve_conflict(
        self,
        path_a: List[str],
        path_b: List[str],
        axiom_scores_a: Dict[str, float],
        axiom_scores_b: Dict[str, float]
    ) -> str:
        """Returns winning path ID based on axiom priorities."""
        pass
```

**Implementation:** Cluster 2 (Axiom Judge erweitern)

---

#### 2. Token-Budget-Manager
**Problem:** MCTS/RLM könnten endlos laufen und Token verschwenden in unwichtigen Ästen.

**Lösung:** Node-spezifisches Token-Limit
```python
class TokenBudgetManager:
    """
    Verhindert "Ewigkeitsschleifen" in MCTS-Ästen.

    - Gesamtbudget pro Session (z.B. 500k Tokens)
    - Node-Budget basierend auf UCB1-Score (wichtige Nodes bekommen mehr)
    - Automatisches Pruning bei Budget-Überschreitung
    """
    def allocate_budget(self, node: ToTNode, total_budget: int) -> int:
        """Dynamische Budget-Zuteilung basierend auf Node-Wichtigkeit."""
        pass
```

**Implementation:** Cluster 1 (MCTS erweitern)

---

### ✅ Keine Widersprüche

**Gemini-Zitat:**
> "Bisher keine gravierenden Widersprüche. Die Klärung zwischen **RLAIF (Inference-time)** und **Abliterated Models** wurde sauber gelöst: Wir nutzen die Freiheit des Modells, um es dann durch ein externes 'Kritiker-Modell' (AxiomJudge) streng zu bewerten."

---

### 🔄 Implementierungs-Reihenfolge Anpassung

**Original Plan (MASTER_IMPLEMENTATION_PROMPT):**
```
Cluster 1: RLM + XoT
Cluster 2: SPO + Tiered RAG  ← SPO war hier
Cluster 3: BiasVector
Cluster 4: Epistemic MCTS
Cluster 5: Privacy
```

**Gemini-Empfehlung:**
```
Cluster 1: SPO + XoT + MCTS Token Budget  ← SPO vorgezogen!
Cluster 2: Tiered RAG + Axiom Judge + Conflict Resolution
Cluster 3: BiasVector + Perspektiven-Graph
Cluster 4: RLM + Epistemic MCTS  ← RLM verschoben
Cluster 5: Privacy (nur wenn Cloud genutzt wird)
```

**Begründung:**
> "Ohne strukturierte Fakten (Tripletts) ist der 'Motor' (MCTS) zwar stark, hat aber kein strukturiertes 'Futter' zum Verarbeiten."

---

## 2. Design-Entscheidungen (Offene Fragen beantwortet)

### Frage 1: SPO-Extraktion Storage

**Options:**
- A) Neo4j (dedizierte Graph-Datenbank)
- B) SQLite mit Graph-Wrapper
- C) NetworkX in-memory mit Serialization

**Gemini-Entscheidung: Option B (SQLite)**

**Begründung:**
> "Neo4j ist für ein lokales, souveränes System zu schwerfällig. SQLite ist portabel, extrem performant für sequentielle Prozesse und bietet mit `json1`-Extensions oder einfachen Adjazenzlisten genug Graph-Power."

**Implementation:**
```python
# SPO-Tripletts in SQLite
CREATE TABLE spo_triplets (
    id TEXT PRIMARY KEY,
    subject TEXT NOT NULL,
    predicate TEXT NOT NULL,
    object TEXT NOT NULL,
    confidence REAL,
    tier TEXT CHECK(tier IN ('bronze', 'silver', 'gold')),
    provenance_json TEXT,  -- JSON mit source_id, extraction_method, etc.
    created_at TEXT,
    verified_at TEXT
);

CREATE INDEX idx_subject ON spo_triplets(subject);
CREATE INDEX idx_tier ON spo_triplets(tier);
```

**Vorteile:**
- ✅ Portabel (eine Datei)
- ✅ Schnell für sequentielle MCTS-Prozesse
- ✅ JSON-Support für flexible Metadata
- ✅ ACID-Transaktionen für Tier-Promotions

---

### Frage 2: XoT-Simulator Model

**Options:**
- A) Eigenes schnelles LLM (Qwen-2.5-14B / Llama-3-8B)
- B) Gleiches LLM wie ToT (einfacher, aber langsamer)

**Gemini-Entscheidung: Option A (Eigenes 8B/14B Modell)**

**Begründung:**
> "Die Heuristik (XoT) *muss* deutlich schneller sein als der Denker (ToT), sonst verliert der Effizienz-Vorteil seinen Sinn. Ein 8B oder 14B Modell ist ideal für 'Bauchgefühl'-Einschätzungen."

**Recommended Models:**
1. **Qwen-2.5-14B-Instruct** (beste Reasoning/Token-Ratio)
2. **Llama-3.1-8B-Instruct** (schnellste Alternative)
3. **Phi-3-Medium-14B** (kompakt, aber gut)

**Implementation:**
```python
# config/models/xot_qwen_llamacpp.json
{
    "model_id": "xot_qwen",
    "provider": "llamacpp",
    "path": "models/qwen2.5-14b-instruct-q4_k_m.gguf",
    "capabilities": ["reasoning"],
    "context_window": 32768,
    "purpose": "xot_simulation",  # ← Neues purpose-Tag
    "n_gpu_layers": 35,
    "n_ctx": 8192  # XoT braucht weniger Context
}
```

---

### Frage 3: BiasVector Extraction

**Options:**
- A) Manuelle Kalibrierung für Sources
- B) Automatische LLM-Extraktion

**Gemini-Entscheidung: Option B (Automatische Extraktion)**

**Begründung:**
> "Die manuelle Kalibrierung für jede Quelle ist zu aufwendig. Das Modell soll den BiasVector vorschlagen (basierend auf Textanalyse), den du dann im Deep Graph manuell 'festschreiben' oder korrigieren kannst."

**Implementation Flow:**
```
1. LLM analysiert Response/Source
2. BiasVector vorgeschlagen (z.B. risk_affinity: 0.7)
3. User kann akzeptieren/editieren/verwerfen
4. Finaler BiasVector wird im Perspektiven-Graph gespeichert
5. Zukünftige Responses dieser Source nutzen cached BiasVector
```

**Prompt Template:**
```python
BIAS_EXTRACTION_PROMPT = """
Analyze the following text and extract a BiasVector with these dimensions:

1. risk_affinity: -1.0 (risk-averse) to +1.0 (risk-seeking)
2. time_horizon: -1.0 (short-term) to +1.0 (long-term)
3. centralization: -1.0 (decentralized) to +1.0 (centralized)
4. empirical_depth: 0.0 (anecdotal) to 1.0 (data-driven)
5. profit_motive: 0.0 (neutral) to 1.0 (commercial agenda)

Text: {response_text}

Respond with ONLY JSON:
{{
    "risk_affinity": 0.5,
    "time_horizon": 0.3,
    ...
}}
"""
```

---

### Frage 4: RLM Priority

**Options:**
- A) Kritisch (ohne RLM kein 10M+ Context)
- B) Optional (128k reicht für die meisten Use Cases)

**Gemini-Entscheidung: Option A (HOCH - Kritisch)**

**Begründung:**
> "Wenn du Reddit-Threads mit 50.000 Kommentaren nach 'echter Erfahrung' scannen willst, reicht ein 128k Fenster nicht aus. Für echte 'Sovereign Research' ist die Tiefe (10M+ Context) der entscheidende Vorteil gegenüber Standard-Tools."

**Use Cases die RLM brauchen:**
- ✅ Reddit Validation (50k+ Kommentare)
- ✅ PDF-Sammlung Analyse (100+ Papers)
- ✅ Multi-Source Verification (20+ Quellen vergleichen)
- ✅ Historische Datenanalyse (Jahre an Logs/Berichten)

**Neue Priorität:** Cluster 4 (nach BiasVector, weil BiasVector für Source-Profiling bei RLM wichtig ist)

---

### Frage 5: Privacy Priority

**Options:**
- A) Kritisch (auch lokal keine Axiome/Prompts loggen)
- B) Optional (nur bei Cloud-Nutzung relevant)

**Gemini-Entscheidung: Option B (Fokus auf Cloud-Sanitization)**

**Begründung:**
> "Solange du 100% lokal arbeitest, ist die interne Maskierung zweitrangig. Sie wird erst kritisch, wenn du Cloud-Modelle (wie Claude 4) als 'Workers' einsetzt."

**Implementation Plan:**
- Cluster 5 bleibt optional
- Nur implementieren wenn Cloud-APIs genutzt werden
- Fokus: Sanitization vor Cloud-Call (nicht für lokale Logs)

---

## 3. Finale Implementation Roadmap

### ✅ Cluster 1: Foundations (Woche 1-2)
**Priorität:** KRITISCH

**Komponenten:**
1. ✅ **SPOExtractor** (`src/core/spo_extractor.py`)
   - Strukturierte Triplett-Extraktion aus LLM-Responses
   - Subject-Predicate-Object Parsing
   - Provenance Tracking
   - SQLite Integration

2. ✅ **XoTSimulator** (`src/core/xot_simulator.py`)
   - Schnelle Heuristik vor MCTS-Selection
   - Eigenes 8B/14B Modell (Qwen-2.5-14B)
   - Prior Probability Estimation

3. ✅ **TokenBudgetManager** (`src/core/token_budget_manager.py`)
   - Node-spezifisches Token-Limit
   - Dynamische Budget-Zuteilung
   - Automatisches Pruning

4. ⚠️ **GraphManager SPO-Extension** (bestehende Datei erweitern)
   - SPO-Methoden hinzufügen (parallel zu Legacy)
   - SQLite Backend Integration
   - Migration Helper für alte Nodes

**Deliverables:**
- SPO-Tripletts werden extrahiert und in SQLite gespeichert
- MCTS nutzt XoT für Prior-Schätzungen
- Token-Budget verhindert Ewigkeitsschleifen

---

### ✅ Cluster 2: Verified Knowledge (Woche 3-4)
**Priorität:** HOCH

**Komponenten:**
1. ✅ **TieredRAG** (`src/core/tiered_rag.py`)
   - Bronze Tier: Raw SPO-Tripletts
   - Silver Tier: Provenance-tracked Tripletts
   - Gold Tier: Multi-Source verifizierte Tripletts
   - Promotion/Demotion Workflow

2. ✅ **AxiomJudge** (`src/core/axiom_judge.py`)
   - LLM-based Axiom Evaluation
   - RLAIF Feedback Loop
   - Explanation Generation

3. ✅ **ConflictResolver** (`src/core/conflict_resolver.py`)
   - Axiom-Hierarchie (priority: critical > high > medium)
   - Tie-Breaker Logic für MCTS
   - Conflict Detection in SPO-Graph

4. ⚠️ **AxiomManager Extension**
   - RLAIF Integration
   - Dynamische Weight Adjustment
   - Conflict Resolution Interface

**Deliverables:**
- 3-Tier Knowledge Graph funktioniert
- Axiome werden durch LLM evaluiert mit Erklärungen
- MCTS kann Pfad-Konflikte auflösen

---

### ✅ Cluster 3: Perspectives (Woche 5-6)
**Priorität:** MITTEL

**Komponenten:**
1. ✅ **BiasVectorExtractor** (`src/core/bias_vector_extractor.py`)
   - Automatische Bias-Analyse via LLM
   - User-Korrektur-Interface
   - Caching für bekannte Sources

2. ✅ **PerspectiveGraph** (`src/core/perspective_graph.py`)
   - Separater Graph für Bias-Tracking
   - Bias-Distance Calculation
   - Source Profiling

3. ⚠️ **DebateManager Extension**
   - BiasVector Integration in Arguments
   - Contrastive Debate zwischen Sources mit verschiedenen BiasVectors
   - Perspective-Aware Verdict

**Deliverables:**
- BiasVector wird für alle Responses extrahiert
- Perspektiven-Graph zeigt Source-Landschaft
- Debates berücksichtigen Bias-Distanz

---

### ✅ Cluster 4: Deep Intelligence (Woche 7-8)
**Priorität:** HOCH (RLM), MITTEL (Epistemic MCTS)

**Komponenten:**
1. ✅ **RLMEnvironment** (`src/core/rlm_environment.py`)
   - Python REPL Environment
   - Code Execution Sandbox
   - Prompt-as-Environment Architektur
   - CEO-Worker Pattern

2. ✅ **EpistemicMCTS** (`src/core/epistemic_mcts.py`)
   - Value of Information (VoI) Calculation
   - Dynamic Scraping Queue
   - Cost/Benefit Analysis
   - Stopping Criteria

3. ⚠️ **CoverageAnalyzer Extension**
   - VoI Integration
   - Uncertainty Modeling
   - Information Gain Estimation

**Deliverables:**
- 10M+ Token Context via RLM
- MCTS entscheidet intelligent, wo weitere Recherche lohnt
- VoI-basierte Priorisierung

---

### ⚠️ Cluster 5: Hardening (Woche 9-10, Optional)
**Priorität:** NIEDRIG (nur bei Cloud-Nutzung)

**Komponenten:**
1. ⚠️ **PrivacySanitizer** (`src/core/privacy_sanitizer.py`)
   - Metadata Masking vor Cloud-Calls
   - Axiom-Anonymisierung
   - Audit Logging

2. ⚠️ **RedditValidator** (`src/core/reddit_validator.py`)
   - Reddit API (PRAW) Integration
   - Experience-Node Extraction
   - Human Consensus Scoring
   - Friction-Check

**Deliverables:**
- Privacy-gehärtetes System bei Cloud-Nutzung
- Social Validation Layer (optional)

---

## 4. Geminis Finale Empfehlung

**Gemini-Zitat:**
> "Ich bin bereit! Du kannst nun Claude Code den Befehl geben, mit **Cluster 1** zu starten, wobei wir die **SPO-Extraktion** als erste Aufgabe priorisieren."

**Befehl für Claude Code:**
```
Gemini hat das Review abgeschlossen. Wir starten mit Cluster 1 (neu priorisiert).

Aufgaben:
1. Implementiere SPOExtractor in src/core/spo_extractor.py
2. SQLite Backend für SPO-Tripletts (Bronze/Silver/Gold Tiers)
3. XoTSimulator mit eigenem 8B/14B Modell
4. TokenBudgetManager für MCTS
5. GraphManager um SPO-Methoden erweitern

Design-Entscheidungen (alle beantwortet):
- SPO Storage: SQLite (Option B)
- XoT Model: Eigenes schnelles Modell (Option A)
- BiasVector: Automatische Extraktion (Option B)
- RLM Priority: Kritisch - Cluster 4 (Option A)
- Privacy: Optional - nur bei Cloud (Option B)

Zusätzliche Komponenten aus Gemini-Review:
- ConflictResolver (Cluster 2)
- TokenBudgetManager (Cluster 1)
```

---

## 5. Offene Punkte für Implementation

### Sofort benötigt (Cluster 1):
- [ ] Modell-Download: Qwen-2.5-14B-Instruct-Q4_K_M (~8GB)
- [ ] SQLite Schema Design für SPO-Tripletts
- [ ] XoT-Prompt Engineering (sehr kurz, Heuristik-Stil)
- [ ] Token-Budget Strategie (Gesamt-Budget? Node-Budget-Formula?)

### Später benötigt (Cluster 2+):
- [ ] Axiom-Hierarchie definieren (priority: critical vs. high)
- [ ] BiasVector-Extraction Prompt Engineering
- [ ] RLM-Sandbox Security (welcher Python-Executor?)

---

**Status:** ✅ Review Complete - Ready for Implementation

**Nächster Schritt:** Dokumentation aufräumen, dann Cluster 1 starten.
