# The Sovereign Research Architect

**Version:** 2.0
**Date:** 2026-01-08
**Status:** Design Phase

---

## Executive Summary

The **Sovereign Research Architect** is a hybrid AI system that combines the creative breadth of large external models (GPT-5, Claude 3.5) with the critical, value-aligned reasoning of local abliterated models (DeepSeek-R1-7B). It uses a Knowledge Graph as the central "truth buffer" to separate facts from opinions and bias, enabling sovereign economic decision-making.

**Core Innovation:** External models propose, local models validate, Knowledge Graph preserves truth.

---

## 1. System Philosophy

### The Four Pillars

1. **Hybrid Intelligence**
   - **External Models (Cloud):** Creative divergence, breadth of possibilities (ToT exploration)
   - **Local Models (Abliterated):** Critical convergence, value-aligned analysis (MCTS validation)
   - **Human:** Strategic decisions, axiom definition, final synthesis

2. **Axiom-Library (Values as Filter)**
   - Modular library of core values and economic principles
   - Examples: Austrian Economics, Risk Tolerance, Time Preference
   - Acts as systematic filter to neutralize Big Tech bias
   - Stored as structured JSON, not long texts (VRAM optimization)

3. **Graph-based Knowledge Buffer**
   - NetworkX Knowledge Graph as "exoskeletal memory"
   - Facts stored as triplets: `(Subject, Predicate, Object)`
   - **Separation principle:** Information ≠ Opinion
   - Local model extracts only fact-triplets from external sources

4. **Multi-Technique Reasoning**
   - **Tree of Thoughts (ToT):** Decompose topics into research paths
   - **Monte Carlo Tree Search (MCTS):** Evaluate path success probability
   - **Chain of Thought (CoT):** Rigid specification for calculations
   - **GIST Framework:** Qualitative evaluation of research reports

---

## 2. Architecture: The Three-Layer Pattern (Enhanced)

### Layer 1: DESCRIPTION (Static - "What")

**Purpose:** Define rules, values, and building blocks

**Components:**
```
config/
├── axioms/                    # NEW: Value system
│   ├── economic_principles.json   # Austrian Economics, etc.
│   ├── risk_tolerance.json        # Personal risk profile
│   └── time_preference.json       # Short vs. long-term focus
│
├── techniques/                # REFACTORED: Now graph-operations
│   ├── graph_extraction/
│   │   ├── entity_extractor.json
│   │   └── relationship_mapper.json
│   ├── validation/
│   │   ├── axiom_validator.json
│   │   ├── contradiction_check.json
│   │   └── friction_detector.json
│   └── reasoning/
│       ├── tot_decomposer.json
│       └── mcts_evaluator.json
│
├── workflows/                 # REPLACED: Now "Reasoning Patterns"
│   ├── tot_exploration.json       # ToT-based market exploration
│   ├── mcts_validation.json       # MCTS path evaluation
│   └── sovereign_synthesis.json   # Final synthesis with axioms
│
└── models/
    ├── external/              # NEW: External model configs
    │   ├── claude_sonnet.json
    │   └── gpt4o.json
    └── local/
        └── deepseek_r1_7b.json
```

**Axiom Example (`economic_principles.json`):**
```json
{
  "axiom_id": "opportunity_cost",
  "category": "economics",
  "statement": "Evaluate opportunities by opportunity cost. A gain is only a gain if it justifies time investment compared to passive investments.",
  "application": "filter",
  "priority": "high",
  "metadata": {
    "school": "austrian_economics",
    "reference": "Human Action, Mises 1949"
  }
}
```

### Layer 2: WORKING STATE (Dynamic - "How")

**Purpose:** Live execution state as Knowledge Graph

**NEW Architecture:**
```python
# Core components
working_state/
├── knowledge_graph/           # NetworkX graph (in-memory)
│   ├── nodes/                 # Entities (facts, hypotheses)
│   ├── edges/                 # Relationships
│   └── metadata/              # Source, confidence, timestamp
│
├── tot_tree/                  # Tree of Thoughts structure
│   ├── root_question/
│   ├── branches/              # Exploration paths
│   └── pruned_paths/          # Rejected branches
│
├── mcts_state/                # Monte Carlo search state
│   ├── visited_paths/
│   ├── simulations/           # Python simulation results
│   └── scores/                # Path evaluation scores
│
└── execution_log/             # Traditional logs (for debugging)
```

**Graph Structure:**
- **Nodes:** Entities (companies, markets, technologies, hypotheses)
- **Edges:** Relationships (competes_with, depends_on, contradicts, supports)
- **Attributes:** confidence_score, source, axiom_alignment, friction_level

**Hybrid Strategy (VRAM Optimization):**
- Graph lives in RAM (16GB system RAM)
- Only "active subgraphs" loaded into LLM context
- Graph-to-Text translation for prompts (max 2000 tokens)

### Layer 3: OUTPUT (Result - "What was produced")

**Purpose:** Directed decision synthesis

**Category-based Routing (Enhanced):**
```
output/
├── market_opportunity/        # Market analysis
├── technical_feasibility/     # Technical assessment
├── monetization/              # Business model
├── risk_analysis/             # Risk + friction
├── strategic_synthesis/       # Final recommendation
└── raw_graphs/                # Graph snapshots (JSON export)
```

**Output Format:**
```json
{
  "output_id": "analysis_xyz",
  "category": "market_opportunity",
  "synthesis": {
    "recommendation": "Pursue Path B (Local Services)",
    "confidence": 0.78,
    "reasoning_chain": [
      "ToT identified 5 paths",
      "MCTS simulated success probability",
      "Path A pruned due to high friction (Reddit data)",
      "Path B aligns with axiom 'opportunity_cost'"
    ]
  },
  "graph_snapshot": {
    "nodes": 42,
    "edges": 87,
    "key_insights": [...]
  },
  "axiom_alignment": {
    "passed": ["opportunity_cost", "risk_tolerance"],
    "failed": [],
    "warnings": ["time_preference: borderline"]
  }
}
```

---

## 3. The Sovereign Cycle (4 Phases)

### Phase 0: EXPLORATION (ToT & External Breadth)

**Goal:** Generate breadth of possibilities using external models

**Process:**
1. User defines research question
2. Local DeepSeek-R1 generates ToT decomposition
   - Example: "E-Commerce Niche" → 5 sub-questions
3. External models (Claude/GPT-4) answer each branch
4. **Sovereignty Check:** Immediate fact-triplet extraction
   - External text discarded, only graph structure remains

**Techniques:**
- `tot_decomposer.json`
- `entity_extractor.json`
- Multi-AI orchestration (existing)

### Phase 1: GROUNDING (Human Friction & Reality Check)

**Goal:** Validate ToT branches against reality and axioms

**Process:**
1. For each ToT branch, search for "friction" (real problems)
   - Web scraping: Reddit, forums, review sites
2. **Friction Check:** If branch has no real-world friction → prune
3. **Axiom Validation:** Check graph nodes against axiom library
   - Mark: "Contradicts Axiom X" or "Supports Axiom Y"

**Techniques:**
- `friction_detector.json` (scraping + analysis)
- `axiom_validator.json`
- `contradiction_check.json` (existing)

**Example:**
```
Branch: "SaaS for Project Management"
→ Friction detected: 127 Reddit posts "PM tools too expensive"
→ Axiom check: ✓ Aligns with "opportunity_cost"
→ Status: KEEP
```

### Phase 2: REASONING (MCTS & Simulation)

**Goal:** Deep evaluation of surviving branches

**Process:**
1. MCTS navigates remaining ToT branches
2. For each path, local model simulates next 3 steps
3. **Python Intervention:** LLM generates simulation code
   - Example: Break-even analysis, market size estimation
4. If math says "No" → prune branch (regardless of LLM opinion)

**Techniques:**
- `mcts_evaluator.json`
- Python code generation (existing tool system)
- CoT for rigid calculations

**Example:**
```python
# LLM-generated simulation
def simulate_break_even(initial_cost, monthly_revenue, churn_rate):
    months_to_profit = initial_cost / (monthly_revenue * (1 - churn_rate))
    return months_to_profit

result = simulate_break_even(5000, 500, 0.05)
# Result: 10.5 months → Acceptable per "time_preference" axiom
```

### Phase 3: SOVEREIGN SYNTHESIS

**Goal:** Create final report based on "surviving" graph

**Process:**
1. Extract winning path from graph
2. **Axiom Final Check:** Does result align with all core axioms?
3. Generate structured output per category
4. Human review and decision

**Techniques:**
- `sovereign_synthesis.json`
- Category-based routing (existing)
- Output templates

---

## 4. Technical Implementation

### 4.1 Stack

**Backend (Python):**
- **Orchestrator:** Manages ToT/MCTS flow (refactor existing)
- **GraphManager:** NetworkX wrapper for graph operations (NEW)
- **AxiomJudge:** Validates graph nodes against axioms (NEW)
- **LlamaClient:** Existing, enhanced for DeepSeek-R1

**Frontend (Vue 3):**
- **ToT Explorer:** Interactive tree visualization (NEW)
- **Graph Viewer:** D3.js network graph (NEW)
- **Axiom Editor:** Manage personal values (NEW)
- **Dashboard:** Enhanced with graph metrics

**Models:**
- **Local:** DeepSeek-R1-Distill-Qwen-7B (via Ollama/vLLM)
  - KV-Cache quantization for VRAM optimization
- **External:** Claude Sonnet, GPT-4o (via Multi-AI tools)

### 4.2 Key Classes (Python)

```python
# NEW: Graph Manager
class GraphManager:
    """Manages the Knowledge Graph using NetworkX"""
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_fact_triplet(self, subject, predicate, object, metadata):
        """Add fact from external source"""
        pass

    def query_subgraph(self, focus_entity, depth=2):
        """Extract relevant subgraph for prompt"""
        pass

    def to_text(self, max_tokens=2000):
        """Convert graph to text for LLM context"""
        pass

# NEW: Axiom Judge
class AxiomJudge:
    """Validates graph nodes against axiom library"""
    def __init__(self, axiom_dir):
        self.axioms = load_axioms(axiom_dir)

    def evaluate_node(self, node, axiom_id):
        """Check if node aligns with axiom"""
        pass

    def score_path(self, path_nodes):
        """Score entire ToT path against all axioms"""
        pass

# REFACTORED: Orchestrator with ToT/MCTS
class SovereignOrchestrator:
    """Master coordinator for Sovereign Research"""
    def __init__(self):
        self.graph_manager = GraphManager()
        self.axiom_judge = AxiomJudge("config/axioms")
        self.tot_manager = ToTManager()
        self.mcts_engine = MCTSEngine()

    def run_exploration(self, question):
        """Phase 0: ToT + External models"""
        pass

    def run_grounding(self):
        """Phase 1: Friction + Axiom validation"""
        pass

    def run_reasoning(self):
        """Phase 2: MCTS + Simulations"""
        pass

    def run_synthesis(self):
        """Phase 3: Final report"""
        pass
```

### 4.3 VRAM Optimization Strategy

**Hardware:** 11GB VRAM, 16GB RAM

**Strategies:**
1. **Sequential Execution:** One agent at a time (no parallel)
2. **KV-Cache Quantization:** Enable in llama.cpp/vLLM
3. **Graph-based Compression:** Store facts in graph (RAM), not prompts
4. **Selective Context:** Only load relevant subgraph (max 2000 tokens)
5. **Python Logic:** LLM outputs JSON/code, Python executes

---

## 5. Migration from Old to New

### What to Keep (Minimal Changes)
- ✅ Flask API server
- ✅ Vue 3 frontend structure (refactor views)
- ✅ Config system (add axioms/, refactor techniques/)
- ✅ Multi-AI tools (prompt_generator, response_analyzer)
- ✅ Validation techniques (adapt to graph operations)

### What to Refactor
- 🔄 Orchestrator: Add ToT/MCTS logic
- 🔄 Workflows → Reasoning Patterns
- 🔄 Working State: JSON logs → Graph snapshots
- 🔄 ResearchCreator.vue → ToT Explorer

### What to Build New
- ⭐ GraphManager (NetworkX wrapper)
- ⭐ AxiomJudge (value validation)
- ⭐ ToTManager (tree decomposition)
- ⭐ MCTSEngine (path evaluation)
- ⭐ Graph Viewer (D3.js frontend)
- ⭐ Axiom Editor (values management)

---

## 6. Business Model

### Target Market
- **Primary:** Individual knowledge workers, solopreneurs, indie hackers
- **Secondary:** Small consultancies, niche analysts

### Products

1. **Insights-as-a-Service**
   - Weekly/monthly sovereign reports for specific niches
   - Priced at fraction of traditional consulting (€200-500/report)

2. **Open Core + Premium**
   - **Free:** Core framework (GitHub)
   - **Patreon/Premium:** Curated axiom libraries, specialized workflows, output templates

3. **Verticalized Analysis Products**
   - GTM Strategies (market entry plans)
   - Investment Memos (risk-transparent analysis)
   - Niche Opportunity Reports

### Competitive Advantage
- **Speed:** Hours instead of weeks
- **Objectivity:** Graph separates fact from opinion, shows sources
- **Sovereignty:** No Big Tech bias, user-defined values
- **Cost:** 10-20x cheaper than traditional consulting

---

## 7. Open Source Integrations

### Recommended Libraries

**Graph & RAG:**
- [microsoft/graphrag](https://github.com/microsoft/graphrag) - Entity/relationship extraction
- [WhyHow.AI GraphRAG](https://github.com/whyhow-ai/whyhow) - Structured graph queries

**Reasoning:**
- [stanfordnlp/dspy](https://github.com/stanfordnlp/dspy) - Programmatic prompt optimization
- [SakanaAI/AI-Scientist](https://github.com/SakanaAI/AI-Scientist) - Research loop patterns

**Infrastructure:**
- [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) - Cyclic workflow graphs
- [unclecode/crawl4ai](https://github.com/unclecode/crawl4ai) - AI-friendly web scraping
- [ollama/ollama](https://github.com/ollama/ollama) or [vllm-project/vllm](https://github.com/vllm-project/vllm) - Local model serving

**Vector Storage (for Long-term Memory):**
- [qdrant/qdrant](https://github.com/qdrant/qdrant) or [chroma-core/chroma](https://github.com/chroma-core/chroma)

---

## 8. Next Steps

See `IMPLEMENTATION_ROADMAP.md` for detailed sprint plan.

**Immediate priorities:**
1. Implement GraphManager (NetworkX wrapper)
2. Create axiom schema + example axioms
3. Refactor Orchestrator with ToT stub
4. Build ToT Explorer (Vue component)
5. Integrate DeepSeek-R1 model

---

## Appendix: Terminology

- **Abliterated Model:** Uncensored LLM with removed safety guardrails
- **ToT:** Tree of Thoughts - reasoning technique for exploration
- **MCTS:** Monte Carlo Tree Search - path evaluation algorithm
- **Axiom:** Core value/principle used as filter
- **Fact Triplet:** (Subject, Predicate, Object) knowledge representation
- **Friction:** Real-world problems/pain points found in user data
- **Sovereign:** Independent, bias-free, value-aligned decision-making
