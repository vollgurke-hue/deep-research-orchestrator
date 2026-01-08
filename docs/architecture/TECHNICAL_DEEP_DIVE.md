# Technical Deep Dive: MCTS, Hardware-Tiering & DSPy

**Version:** 1.0
**Date:** 2026-01-08
**Purpose:** Mathematische und technische Details der Implementierung

---

## 1. MCTS (Monte Carlo Tree Search): Die Mathematik

### UCB1 Formel (Upper Confidence Bound)

Die Kernformel für die Auswahl des nächsten zu explorierenden Knotens:

```
UCB1(node) = Q(node) + C * sqrt(ln(N) / n(node))
```

**Komponenten:**
- **Q(node):** Durchschnittlicher Wert des Knotens (0.0 - 1.0)
  - Im Kontext: Axiom-Alignment-Score + Faktensicherheit
- **N:** Gesamtzahl aller Simulationen (Parent visits)
- **n(node):** Anzahl Besuche dieses spezifischen Knotens
- **C:** Explorations-Konstante (typisch: √2 ≈ 1.414)
  - Höheres C = mehr Exploration (riskanter, breiter)
  - Niedrigeres C = mehr Exploitation (sicherer, tiefer)

### Die vier MCTS Phasen

```python
class MCTSEngine:
    """
    Monte Carlo Tree Search für Knowledge Graph Navigation
    """

    def __init__(self, graph, axiom_judge, exploration_constant=1.414):
        self.graph = graph
        self.judge = axiom_judge
        self.C = exploration_constant
        self.nodes = {}  # node_id -> MCTSNode

    # === PHASE 1: SELECTION ===
    def select(self) -> str:
        """
        Wähle vielversprechendsten Knoten mit UCB1

        Startet beim Root und traversiert den Baum,
        bis ein nicht-voll-expandierter Knoten gefunden wird.
        """
        current = self.root_id

        while self.is_fully_expanded(current) and not self.is_terminal(current):
            # Berechne UCB1 für alle Kinder
            children = self.graph.get_children(current)
            ucb_scores = {}

            for child_id in children:
                child_node = self.nodes[child_id]
                parent_node = self.nodes[current]

                # UCB1 Formel
                exploitation = child_node.value / child_node.visits if child_node.visits > 0 else 0
                exploration = self.C * math.sqrt(
                    math.log(parent_node.visits) / child_node.visits
                ) if child_node.visits > 0 else float('inf')

                ucb_scores[child_id] = exploitation + exploration

            # Wähle Kind mit höchstem UCB1
            current = max(ucb_scores, key=ucb_scores.get)

        return current

    # === PHASE 2: EXPANSION ===
    def expand(self, node_id: str) -> str:
        """
        Generiere neue Hypothese / Frage / Sub-Graph

        Im ToT-Kontext: LLM generiert neue Sub-Frage
        Im Graph-Kontext: Scraper holt neue Daten
        """
        node = self.nodes[node_id]

        # Generiere neue Kindknoten (z.B. via LLM)
        new_question = self.llm.generate_subquestion(
            parent_question=node.question,
            depth=node.depth + 1
        )

        child_id = f"{node_id}_child_{len(node.children)}"
        child_node = MCTSNode(
            node_id=child_id,
            parent_id=node_id,
            question=new_question,
            depth=node.depth + 1
        )

        self.nodes[child_id] = child_node
        node.children.append(child_id)

        return child_id

    # === PHASE 3: SIMULATION ===
    def simulate(self, node_id: str) -> float:
        """
        Führe "Rollout" durch - simuliere bis zum Ende

        Zwei Methoden:
        1. LLM-basiert: "Was passiert, wenn wir diesen Pfad verfolgen?"
        2. Python-basiert: Generiere Code, führe echte Simulation aus
        """
        node = self.nodes[node_id]

        # Methode 2 (bevorzugt): Python-Simulation
        if node.simulation_type == "python":
            # LLM generiert Python-Code für Business-Simulation
            code = self.llm.generate_simulation_code(
                scenario=node.question,
                graph_context=self.graph.get_subgraph(node_id, depth=2)
            )

            # Führe Code aus
            try:
                simulation_result = self._execute_simulation(code)
                score = simulation_result['success_probability']
            except Exception as e:
                score = 0.0  # Simulation failed

        # Methode 1 (Fallback): LLM-basiert
        else:
            reasoning = self.llm.simulate_outcome(
                question=node.question,
                graph_context=self.graph.get_subgraph(node_id, depth=2)
            )
            score = reasoning.confidence

        # Axiom-Check: Bewerte Simulation gegen Axiome
        axiom_scores = {}
        for axiom in self.judge.get_all_axioms():
            axiom_score = self.judge.evaluate_simulation(
                simulation_result if node.simulation_type == "python" else reasoning,
                axiom
            )
            axiom_scores[axiom.id] = axiom_score

        # Gewichteter Final Score
        final_score = self._combine_scores(score, axiom_scores)

        return final_score

    # === PHASE 4: BACKPROPAGATION ===
    def backpropagate(self, node_id: str, value: float):
        """
        Update Werte den Baum hinauf
        """
        current = node_id

        while current is not None:
            node = self.nodes[current]
            node.visits += 1
            node.total_value += value

            # Update durchschnittlichen Wert
            node.value = node.total_value / node.visits

            current = node.parent_id

    # === HELPER METHODS ===
    def _combine_scores(self, base_score: float, axiom_scores: dict) -> float:
        """
        Kombiniere Simulations-Score mit Axiom-Alignment

        Formel: 0.6 * base_score + 0.4 * weighted_axiom_score

        Rationale: Axiome sind wichtiger als "Erfolgswahrscheinlichkeit"
        """
        weighted_axiom_score = 0.0
        total_weight = 0.0

        for axiom_id, score in axiom_scores.items():
            axiom = self.judge.get_axiom(axiom_id)
            weight = {"critical": 1.0, "high": 0.7, "medium": 0.4, "low": 0.2}[axiom.priority]

            weighted_axiom_score += score * weight
            total_weight += weight

        avg_axiom_score = weighted_axiom_score / total_weight if total_weight > 0 else 0.5

        # 40% Axiome, 60% Simulation
        return 0.6 * base_score + 0.4 * avg_axiom_score

    def _execute_simulation(self, code: str) -> dict:
        """
        Führe generiertes Python aus (sicher in Sandbox)
        """
        # Sicherer Namespace
        safe_globals = {
            'math': math,
            'random': random,
            'np': np,
            '__builtins__': {}
        }

        local_vars = {}
        exec(code, safe_globals, local_vars)

        return local_vars.get('result', {'success_probability': 0.0})


@dataclass
class MCTSNode:
    """MCTS Knoten mit Statistiken"""
    node_id: str
    parent_id: Optional[str]
    question: str
    depth: int

    # MCTS Stats
    visits: int = 0
    total_value: float = 0.0
    value: float = 0.0  # Average

    # Children
    children: List[str] = field(default_factory=list)

    # Simulation
    simulation_type: str = "python"  # or "llm"
```

### MCTS Hyperparameter Tuning

```python
# Exploration vs Exploitation Trade-off
configs = {
    "aggressive_exploration": {
        "C": 2.0,           # Hohe Exploration
        "max_depth": 5,
        "simulations": 20,
        "use_case": "Frühe Phase, viele Möglichkeiten"
    },
    "balanced": {
        "C": 1.414,         # Standard (√2)
        "max_depth": 4,
        "simulations": 15,
        "use_case": "Standard Research"
    },
    "conservative_exploitation": {
        "C": 0.7,           # Wenig Exploration
        "max_depth": 3,
        "simulations": 10,
        "use_case": "Finalisierung, tiefe Analyse"
    }
}
```

---

## 2. Hardware-Tiering: 11GB VRAM Optimierung

### Das Problem

**VRAM ist knapp:** 11GB reichen nicht für:
- ❌ 70B Modell (braucht ~40GB)
- ❌ Mehrere Modelle gleichzeitig
- ❌ Große Kontexte (32k+ tokens)

### Die Lösung: Sequentielles Tiering

```
┌────────────────────────────────────────────────┐
│  TIER 1: Fast Workers (8B Modelle)            │
│  ├─ Llama 3.1 8B Instruct Q4_K_M              │
│  ├─ DeepSeek-R1-Distill-Qwen-7B Q4_K_M        │
│  └─ Mistral 7B Instruct Q4_K_M                │
│                                                │
│  Aufgaben:                                     │
│  • Fact Extraction (Text → Graph Triplets)    │
│  • Entity Recognition                          │
│  • Quick Reasoning (ToT decomposition)         │
│  • Contradiction Detection                     │
│                                                │
│  VRAM: ~5-6GB pro Modell                       │
│  Speed: 20-40 tokens/s                         │
└────────────────────────────────────────────────┘

┌────────────────────────────────────────────────┐
│  TIER 2: Quality Masters (32B Modelle)        │
│  ├─ Qwen 2.5 32B Instruct Q4_K_M              │
│  └─ Command-R 32B Q4_K_M                       │
│                                                │
│  Aufgaben:                                     │
│  • Final Synthesis                             │
│  • Complex Reasoning (MCTS evaluation)         │
│  • Report Writing                              │
│  • Axiom Evaluation (kritische Entscheidungen) │
│                                                │
│  VRAM: ~18-20GB (SWAP zu RAM bei 11GB!)        │
│  Speed: 5-10 tokens/s                          │
└────────────────────────────────────────────────┘

┌────────────────────────────────────────────────┐
│  TIER 3: External Giants (Cloud API)          │
│  ├─ Claude 3.5 Sonnet                          │
│  ├─ GPT-4o                                     │
│  └─ Gemini 1.5 Pro                             │
│                                                │
│  Aufgaben:                                     │
│  • ToT Exploration (Breite generieren)         │
│  • Creative Ideation                           │
│  • Multi-perspective Analysis                  │
│                                                │
│  VRAM: 0GB (Cloud)                             │
│  Cost: $0.01-0.03 per 1k tokens                │
└────────────────────────────────────────────────┘
```

### Implementierung: Model Manager

```python
class ModelManager:
    """
    Verwaltet Model-Loading/Unloading für 11GB VRAM
    """

    def __init__(self, vram_limit_gb=11):
        self.vram_limit = vram_limit_gb * 1024  # MB
        self.loaded_models = {}
        self.model_configs = self._load_configs()

    def get_model(self, task_type: str):
        """
        Lade passendes Modell basierend auf Task

        Task Types:
        - "extraction": Tier 1 (8B)
        - "reasoning": Tier 1 (DeepSeek-R1)
        - "synthesis": Tier 2 (32B)
        - "exploration": Tier 3 (External)
        """
        model_id = self._select_model_for_task(task_type)

        # Prüfe VRAM
        if not self._has_vram_space(model_id):
            self._unload_least_recently_used()

        # Lade Modell
        if model_id not in self.loaded_models:
            self._load_model(model_id)

        return self.loaded_models[model_id]

    def _load_model(self, model_id: str):
        """
        Lade Modell mit optimalen Settings für 11GB VRAM
        """
        config = self.model_configs[model_id]

        if config['tier'] == 1:  # 8B Modelle
            model = Llama(
                model_path=config['path'],
                n_ctx=4096,           # Context window
                n_gpu_layers=-1,      # Alle Layers auf GPU
                n_batch=512,
                use_mlock=True,
                # KV-Cache Optimierung
                type_k=1,             # Q4_0 quantization für keys
                type_v=1              # Q4_0 quantization für values
            )

        elif config['tier'] == 2:  # 32B Modelle (VRAM overflow!)
            # Mit 11GB VRAM: Nutze CPU offloading
            model = Llama(
                model_path=config['path'],
                n_ctx=2048,           # Kleinerer Context
                n_gpu_layers=20,      # Nur 20 Layers auf GPU (Rest CPU)
                n_batch=256,
                use_mmap=True,
                # Aggressive KV-Cache Quantization
                type_k=0,             # Q2_K für keys
                type_v=0              # Q2_K für values
            )

        self.loaded_models[model_id] = model
        self._log_vram_usage()

    def _select_model_for_task(self, task_type: str) -> str:
        """
        Task → Model Mapping
        """
        task_model_map = {
            # Tier 1: Fast extraction
            "extraction": "llama-3.1-8b-instruct",
            "entity_recognition": "llama-3.1-8b-instruct",
            "contradiction_check": "mistral-7b-instruct",

            # Tier 1: Reasoning
            "tot_decomposition": "deepseek-r1-7b",
            "axiom_evaluation_simple": "deepseek-r1-7b",

            # Tier 2: Quality
            "synthesis": "qwen-2.5-32b",
            "final_report": "qwen-2.5-32b",
            "axiom_evaluation_critical": "qwen-2.5-32b",
            "mcts_simulation": "qwen-2.5-32b",

            # Tier 3: External
            "exploration": "claude-3.5-sonnet",
            "creative_ideation": "gpt-4o"
        }

        return task_model_map.get(task_type, "llama-3.1-8b-instruct")

    def _has_vram_space(self, model_id: str) -> bool:
        """
        Prüfe ob genug VRAM für Modell verfügbar
        """
        required = self.model_configs[model_id]['vram_mb']
        current_usage = sum(
            self.model_configs[m]['vram_mb']
            for m in self.loaded_models
        )

        return (current_usage + required) < self.vram_limit

    def _unload_least_recently_used(self):
        """
        Entlade ältestes Modell (LRU cache)
        """
        if not self.loaded_models:
            return

        # Finde LRU
        lru_model = min(
            self.loaded_models.keys(),
            key=lambda m: self.loaded_models[m].last_used
        )

        # Unload
        del self.loaded_models[lru_model]
        torch.cuda.empty_cache()
```

### VRAM Optimierungs-Techniken

```python
# 1. KV-Cache Quantization (llama.cpp)
# Spart 30-40% VRAM bei minimalem Quality-Loss
loader_kwargs = {
    "type_k": 1,  # Q4_0 for keys
    "type_v": 1   # Q4_0 for values
}

# 2. Context Window Reduktion
# Statt 32k → 4k Context (nutze Graph als "External Memory")
n_ctx = 4096  # Reicht für subgraph-to-text

# 3. Batch Size Reduktion
# Spart VRAM, kostet Speed
n_batch = 256  # Statt 512

# 4. CPU Offloading für große Modelle
# 32B Modell: 20 Layers GPU, Rest CPU
n_gpu_layers = 20

# 5. Model Quantization
# Q4_K_M statt Q8_0 (50% Speicher-Ersparnis)
# Llama 3.1 8B: ~5GB statt ~9GB
```

---

## 3. DSPy: Programmatisches Prompting

### Was ist DSPy?

**Problem mit klassischem Prompting:**
```python
# Fragil, nicht optimierbar
prompt = f"""
Analyze this market data and find opportunities.
Data: {data}
"""
```

**DSPy Ansatz:**
```python
import dspy

# Definition: WAS soll passieren (nicht WIE)
class MarketAnalysis(dspy.Signature):
    """Analyze market data for economic opportunities"""
    market_data = dspy.InputField(desc="Market facts from knowledge graph")
    axioms = dspy.InputField(desc="User's economic axioms")
    analysis = dspy.OutputField(desc="Structured analysis with opportunities")

# Nutzung: DSPy optimiert Prompts automatisch
analyzer = dspy.Predict(MarketAnalysis)
result = analyzer(market_data=graph_text, axioms=axiom_text)
```

### Integration in den Sovereign Architect

```python
class SovereignDSPy:
    """
    DSPy-basierte Reasoning Patterns
    """

    def __init__(self, model_manager):
        self.models = model_manager

        # DSPy Signatures definieren
        self.signatures = {
            "tot_decomposition": self._create_tot_signature(),
            "axiom_evaluation": self._create_axiom_signature(),
            "graph_extraction": self._create_extraction_signature()
        }

    def _create_tot_signature(self):
        """
        ToT Decomposition Signature
        """
        class ToTDecomposition(dspy.Signature):
            """
            Decompose research question into tree of sub-questions
            using Tree of Thoughts methodology
            """
            root_question = dspy.InputField(
                desc="Main research question to decompose"
            )
            axioms = dspy.InputField(
                desc="User's axioms to guide question generation"
            )
            branching_factor = dspy.InputField(
                desc="Number of sub-questions per level (default: 3)"
            )

            sub_questions = dspy.OutputField(
                desc="List of sub-questions with relevance scores",
                format="json"
            )

        return ToTDecomposition

    def decompose_question(self, question, axioms, branching=3):
        """
        Nutze DSPy für ToT Decomposition
        """
        # DSPy optimiert automatisch das Prompting
        predictor = dspy.ChainOfThought(self.signatures["tot_decomposition"])

        result = predictor(
            root_question=question,
            axioms=json.dumps([a.to_dict() for a in axioms]),
            branching_factor=branching
        )

        return json.loads(result.sub_questions)

    def _create_axiom_signature(self):
        """
        Axiom Evaluation Signature
        """
        class AxiomEvaluation(dspy.Signature):
            """
            Evaluate graph triplet against user axiom
            Return alignment score and reasoning
            """
            triplet = dspy.InputField(
                desc="Fact triplet: (subject, predicate, object)"
            )
            axiom = dspy.InputField(
                desc="Axiom to evaluate against"
            )

            alignment_score = dspy.OutputField(
                desc="Score from -1.0 (contradicts) to 1.0 (supports)",
                format="float"
            )
            reasoning = dspy.OutputField(
                desc="Explanation of alignment judgment"
            )

        return AxiomEvaluation

    def evaluate_axiom(self, triplet, axiom):
        """
        Bewerte Triplet gegen Axiom mit DSPy
        """
        predictor = dspy.ChainOfThought(self.signatures["axiom_evaluation"])

        result = predictor(
            triplet=f"{triplet[0]} → {triplet[1]} → {triplet[2]}",
            axiom=axiom.statement
        )

        return {
            "score": float(result.alignment_score),
            "reasoning": result.reasoning
        }
```

### DSPy Optimierung (Auto-Prompting)

```python
# DSPy kann Prompts automatisch optimieren basierend auf Beispielen
class AxiomOptimizer:
    """
    Optimiert Axiom-Evaluation Prompts basierend auf gelabelten Beispielen
    """

    def optimize(self, training_examples):
        """
        Training Examples:
        [
            (triplet, axiom, expected_score, expected_reasoning),
            ...
        ]
        """
        # DSPy Optimizer
        optimizer = dspy.BootstrapFewShot(
            metric=self._axiom_accuracy_metric,
            max_bootstrapped_demos=5
        )

        # Trainiere
        optimized_predictor = optimizer.compile(
            student=dspy.ChainOfThought(AxiomEvaluation),
            trainset=training_examples
        )

        return optimized_predictor

    def _axiom_accuracy_metric(self, example, prediction):
        """
        Metrik: Wie genau war die Axiom-Bewertung?
        """
        score_diff = abs(example.expected_score - float(prediction.alignment_score))
        return 1.0 - score_diff  # Perfect = 1.0, Worst = 0.0
```

---

## 4. Zusammenfassung: Tech-Stack

```python
# Complete Tech Stack
stack = {
    "reasoning": {
        "tot": "Tree of Thoughts (LLM-based decomposition)",
        "mcts": "Monte Carlo Tree Search (UCB1 navigation)",
        "dspy": "Programmatic prompt optimization"
    },
    "storage": {
        "graph": "NetworkX (in-memory, 16GB RAM)",
        "vector_db": "Qdrant (optional, long-term memory)",
        "snapshots": "JSON exports"
    },
    "models": {
        "tier1_extraction": [
            "Llama 3.1 8B Q4_K_M",
            "DeepSeek-R1-Distill-Qwen-7B Q4_K_M"
        ],
        "tier2_synthesis": [
            "Qwen 2.5 32B Q4_K_M (CPU offloaded)"
        ],
        "tier3_external": [
            "Claude 3.5 Sonnet (API)",
            "GPT-4o (API)"
        ]
    },
    "serving": {
        "local": "llama.cpp / Ollama",
        "alternative": "vLLM (faster, more complex)"
    },
    "scraping": {
        "reddit": "PRAW + Crawl4AI",
        "web": "Crawl4AI",
        "structured": "Beautiful Soup 4"
    },
    "validation": {
        "axioms": "Custom AxiomJudge class",
        "simulations": "exec() in sandboxed environment",
        "metrics": "DSPy optimization metrics"
    }
}
```

---

## Nächste Schritte

1. **MCTS Implementation:** Start with `src/core/mcts_engine.py`
2. **Model Manager:** `src/core/model_manager.py` (Hardware-Tiering)
3. **DSPy Integration:** `src/utils/dspy_helpers.py`

**Testing:**
- MCTS: 20 iterations, measure selection time
- VRAM: Load/unload cycles, check leaks
- DSPy: Optimize on 10 examples, measure improvement
