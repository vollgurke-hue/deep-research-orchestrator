# Implementation Roadmap: Sovereign Research Architect

**Version:** 2.0
**Date:** 2026-01-08
**Target Hardware:** 11GB VRAM, 16GB RAM
**Estimated Timeline:** 8-10 weeks (4 sprints)

---

## Overview

This roadmap transforms the existing **Deep Research Orchestrator** into the **Sovereign Research Architect** through incremental refactoring and new component development.

**Strategy:** Build new components alongside existing system, then gradually migrate.

---

## Sprint 0: Foundation & Cleanup (Week 1)

**Goal:** Prepare codebase and validate technical stack

### Tasks

#### 1. Codebase Cleanup ✅ DONE
- [x] Archive hardware guides
- [x] Organize documentation
- [x] Remove legacy viewer/
- [x] Create tests/ and scripts/ directories

#### 2. Technical Validation
- [ ] Install and test DeepSeek-R1-Distill-Qwen-7B locally
  - Test with Ollama (recommended for ease)
  - Test with vLLM (better performance)
  - Measure VRAM usage with KV-cache quantization
  - Verify inference speed (target: <5s for 500 tokens)

- [ ] Verify NetworkX performance
  - Create test graph with 10,000 nodes
  - Measure query performance
  - Test graph-to-text conversion
  - Estimate RAM usage for production graphs

- [ ] Test external API connections
  - Claude API (existing Multi-AI tools)
  - Optional: OpenAI API, Gemini API
  - Rate limits and error handling

#### 3. Schema Design
- [ ] Design axiom schema (`config/schemas/axiom_schema.json`)
- [ ] Design ToT node schema
- [ ] Design graph metadata schema
- [ ] Update technique schema for graph operations

**Deliverables:**
- ✅ Clean codebase structure
- [ ] Validated technical stack (models running)
- [ ] JSON schemas for new components
- [ ] Performance benchmarks document

---

## Sprint 1: Core Graph Infrastructure (Week 2-3)

**Goal:** Implement Knowledge Graph and Axiom system

### Phase 1.1: Graph Manager

**New Files:**
```
src/core/graph_manager.py          # Main graph wrapper
src/core/graph_utils.py            # Helper functions
tests/test_graph_manager.py        # Unit tests
```

**Implementation:**
```python
class GraphManager:
    """
    Wrapper around NetworkX for knowledge management

    Key features:
    - Add/query fact triplets
    - Extract subgraphs for context
    - Convert graph to text (VRAM-optimized)
    - Export/import graph snapshots (JSON)
    """

    def add_fact_triplet(self, subject, predicate, obj, metadata):
        """
        Add fact: (Tesla, competes_with, Rivian)
        metadata: {source: "reddit", confidence: 0.85, timestamp: ...}
        """

    def query_subgraph(self, focus_entity, depth=2, max_nodes=50):
        """
        Extract relevant subgraph centered on entity
        Use for building LLM context (stay under 2000 tokens)
        """

    def to_text(self, subgraph=None, format="markdown"):
        """
        Convert graph to text for LLM prompt
        markdown: "- Tesla competes with Rivian (confidence: 0.85)"
        """

    def calculate_axiom_alignment(self, node_id, axiom_id):
        """
        Score how well a node aligns with an axiom
        Returns: -1.0 to 1.0 (-1=contradicts, 0=neutral, 1=supports)
        """
```

**Tests:**
- Add 100 fact triplets
- Query subgraph (verify depth limit)
- Convert to text (verify <2000 tokens)
- Export/import JSON

### Phase 1.2: Axiom Library

**New Files:**
```
config/axioms/economic_principles.json
config/axioms/risk_tolerance.json
config/axioms/time_preference.json
config/schemas/axiom_schema.json
src/core/axiom_judge.py
tests/test_axiom_judge.py
```

**Axiom Schema:**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["axiom_id", "category", "statement", "application"],
  "properties": {
    "axiom_id": {
      "type": "string",
      "description": "Unique identifier"
    },
    "category": {
      "type": "string",
      "enum": ["economics", "risk", "time", "ethics", "strategy"]
    },
    "statement": {
      "type": "string",
      "description": "Core principle in 1-3 sentences"
    },
    "application": {
      "type": "string",
      "enum": ["filter", "validator", "scorer"],
      "description": "How to apply this axiom"
    },
    "priority": {
      "type": "string",
      "enum": ["critical", "high", "medium", "low"]
    },
    "metadata": {
      "type": "object",
      "properties": {
        "school": {"type": "string"},
        "reference": {"type": "string"},
        "examples": {"type": "array"}
      }
    }
  }
}
```

**Example Axioms:**
```json
{
  "axiom_id": "opportunity_cost",
  "category": "economics",
  "statement": "Evaluate all opportunities by their opportunity cost. A gain is only meaningful if it justifies the time investment compared to passive alternatives.",
  "application": "scorer",
  "priority": "high",
  "metadata": {
    "school": "austrian_economics",
    "reference": "Mises, Human Action (1949)",
    "examples": [
      "If a business requires 40h/week for €2000/month profit, compare to index fund returns + saved time"
    ]
  }
}
```

**AxiomJudge Implementation:**
```python
class AxiomJudge:
    """
    Validates graph nodes against axiom library
    """

    def __init__(self, axiom_dir="config/axioms"):
        self.axioms = self._load_axioms(axiom_dir)

    def evaluate_node(self, graph, node_id, axiom_id):
        """
        Use local LLM to judge if node aligns with axiom
        Returns: {
            "score": 0.75,
            "reasoning": "Node discusses time vs profit...",
            "verdict": "supports" | "neutral" | "contradicts"
        }
        """

    def score_path(self, graph, path_node_ids, return_details=False):
        """
        Evaluate entire ToT path against ALL axioms
        Returns aggregate score + breakdown per axiom
        """

    def filter_contradictions(self, graph, node_ids):
        """
        Remove nodes that contradict critical axioms
        Returns: filtered_node_ids
        """
```

### Phase 1.3: Integration Tests

**Test Scenarios:**
1. **Graph + Axiom Flow:**
   - Add fact: "SaaS requires 3 months to profitability"
   - Evaluate against "opportunity_cost" axiom
   - Verify score and reasoning

2. **Contradiction Detection:**
   - Add conflicting facts from different sources
   - Axiom judge flags contradiction
   - System marks nodes for review

**Deliverables:**
- ✅ GraphManager (production-ready)
- ✅ AxiomJudge (with 5 example axioms)
- ✅ Integration tests passing
- ✅ Documentation (docstrings + README)

---

## Sprint 2: ToT & MCTS Reasoning (Week 4-5)

**Goal:** Implement Tree of Thoughts and path evaluation

### Phase 2.1: ToT Manager

**New Files:**
```
src/core/tot_manager.py
src/core/tot_node.py
config/techniques/reasoning/tot_decomposer.json
tests/test_tot_manager.py
```

**ToTNode Structure:**
```python
@dataclass
class ToTNode:
    """Represents a node in Tree of Thoughts"""
    node_id: str
    parent_id: Optional[str]
    question: str
    depth: int
    status: str  # "pending", "exploring", "evaluated", "pruned"

    # Results
    answer: Optional[str] = None
    confidence: float = 0.0

    # Graph connection
    graph_entities: List[str] = field(default_factory=list)

    # MCTS metrics
    visits: int = 0
    value: float = 0.0

    # Axiom evaluation
    axiom_scores: Dict[str, float] = field(default_factory=dict)
```

**ToTManager Implementation:**
```python
class ToTManager:
    """
    Manages Tree of Thoughts exploration
    """

    def __init__(self, graph_manager, axiom_judge, llm_client):
        self.graph = graph_manager
        self.judge = axiom_judge
        self.llm = llm_client
        self.tree = {}  # node_id -> ToTNode

    def decompose_question(self, root_question, branching_factor=3):
        """
        Use local LLM to decompose root into sub-questions

        Example:
        Q: "What e-commerce niche should I pursue?"
        → Branch 1: "What markets have high friction?"
        → Branch 2: "What markets have low competition?"
        → Branch 3: "What markets align with my skills?"
        """

    def expand_node(self, node_id, external_model="claude"):
        """
        Send node's question to external model
        Extract entities into graph
        Create child nodes if needed
        """

    def prune_branch(self, node_id, reason):
        """
        Mark branch as pruned (due to friction/axiom/MCTS)
        """

    def get_active_leaves(self):
        """
        Get all leaf nodes that are still being explored
        """
```

### Phase 2.2: MCTS Engine

**New Files:**
```
src/core/mcts_engine.py
tests/test_mcts_engine.py
```

**MCTS Implementation:**
```python
class MCTSEngine:
    """
    Monte Carlo Tree Search for path evaluation
    """

    def __init__(self, tot_manager, graph_manager):
        self.tot = tot_manager
        self.graph = graph_manager

    def select(self) -> str:
        """
        Select most promising leaf node using UCB1
        UCB1 = value + C * sqrt(ln(parent_visits) / node_visits)
        """

    def simulate(self, node_id, num_steps=3) -> float:
        """
        Simulate next N steps from this node

        Methods:
        1. LLM-based: Ask local model "what happens next?"
        2. Python-based: Generate and run simulation code

        Returns: success probability (0.0 - 1.0)
        """

    def backpropagate(self, node_id, value):
        """
        Update value estimates up the tree
        """

    def best_path(self) -> List[str]:
        """
        Return path with highest value
        """
```

**Python Simulation Example:**
```python
# LLM generates this code for business model evaluation
def simulate_saas_breakeven(
    initial_cost: float,
    monthly_mrr: float,
    churn_rate: float,
    cac: float,
    conversion_rate: float
):
    """Simulate SaaS profitability"""
    months_to_breakeven = initial_cost / (monthly_mrr * (1 - churn_rate))
    ltv = monthly_mrr * (1 / churn_rate)
    ltv_cac_ratio = ltv / cac

    # Score based on metrics
    score = 0.0
    if months_to_breakeven < 12: score += 0.4
    if ltv_cac_ratio > 3: score += 0.4
    if conversion_rate > 0.02: score += 0.2

    return {
        "score": score,
        "months_to_breakeven": months_to_breakeven,
        "ltv_cac_ratio": ltv_cac_ratio,
        "verdict": "viable" if score > 0.6 else "risky"
    }
```

### Phase 2.3: Orchestrator Refactoring

**Modified Files:**
```
src/core/orchestrator.py  # Add ToT/MCTS integration
```

**New Methods:**
```python
class SovereignOrchestrator:
    """
    Refactored orchestrator with 4-phase sovereign cycle
    """

    def __init__(self):
        self.graph = GraphManager()
        self.axiom_judge = AxiomJudge()
        self.tot = ToTManager(self.graph, self.axiom_judge, llm_client)
        self.mcts = MCTSEngine(self.tot, self.graph)

    # Phase 0: EXPLORATION
    def run_exploration(self, question, external_model="claude"):
        """
        1. Decompose question with ToT
        2. Send branches to external model
        3. Extract entities into graph
        """

    # Phase 1: GROUNDING
    def run_grounding(self):
        """
        1. Search for friction (web scraping)
        2. Validate against axioms
        3. Prune branches with no friction or axiom conflicts
        """

    # Phase 2: REASONING
    def run_reasoning(self, num_simulations=10):
        """
        1. Run MCTS for N iterations
        2. Python simulations for top paths
        3. Select best path
        """

    # Phase 3: SYNTHESIS
    def run_synthesis(self):
        """
        1. Extract winning path from graph
        2. Final axiom check
        3. Generate report
        """

    # Main entry point
    def research(self, question):
        """Run full 4-phase sovereign cycle"""
        self.run_exploration(question)
        self.run_grounding()
        self.run_reasoning()
        return self.run_synthesis()
```

**Deliverables:**
- ✅ ToTManager (tree management)
- ✅ MCTSEngine (path evaluation)
- ✅ Orchestrator refactored (4-phase cycle)
- ✅ Integration tests (end-to-end)

---

## Sprint 3: Frontend & Visualization (Week 6-7)

**Goal:** Build user interfaces for ToT exploration and graph visualization

### Phase 3.1: API Endpoints

**New Endpoints:**
```python
# api_server.py

@app.route('/api/research/start', methods=['POST'])
def start_research():
    """
    Start new research session
    Body: {"question": "...", "external_model": "claude"}
    Returns: {"session_id": "...", "status": "exploring"}
    """

@app.route('/api/research/<session_id>/tot-tree', methods=['GET'])
def get_tot_tree(session_id):
    """
    Get current ToT tree structure
    Returns: {
        "nodes": [...],
        "edges": [...],
        "active_leaves": [...]
    }
    """

@app.route('/api/research/<session_id>/graph', methods=['GET'])
def get_knowledge_graph(session_id):
    """
    Get knowledge graph snapshot
    Params: ?focus=entity_id&depth=2
    """

@app.route('/api/research/<session_id>/prune', methods=['POST'])
def prune_branch(session_id):
    """
    Manually prune a ToT branch
    Body: {"node_id": "...", "reason": "..."}
    """

@app.route('/api/axioms', methods=['GET'])
def list_axioms():
    """Get all axioms"""

@app.route('/api/axioms/<axiom_id>/evaluate', methods=['POST'])
def evaluate_axiom(axiom_id):
    """
    Evaluate graph node against specific axiom
    Body: {"graph_node_id": "..."}
    """
```

### Phase 3.2: Vue Components

**New Components:**
```
gui/src/components/
├── ToTExplorer.vue              # Main ToT tree viewer
├── ToTNode.vue                  # Individual node component
├── GraphViewer.vue              # Knowledge graph (D3.js)
├── AxiomEditor.vue              # Edit/create axioms
├── AxiomScorecard.vue           # Show axiom alignment
├── MCTSProgress.vue             # MCTS simulation progress
└── PythonSimulationViewer.vue   # Show/run Python sims
```

**ToTExplorer.vue (Main Component):**
```vue
<template>
  <div class="tot-explorer">
    <!-- Question Input -->
    <div class="question-panel">
      <textarea v-model="question" placeholder="Enter research question..."></textarea>
      <button @click="startResearch">Explore</button>
    </div>

    <!-- ToT Tree Visualization -->
    <div class="tree-container">
      <ToTNode
        v-for="node in rootNodes"
        :key="node.node_id"
        :node="node"
        :children="getChildren(node.node_id)"
        @expand="expandNode"
        @prune="pruneNode"
      />
    </div>

    <!-- Side Panel: Axiom Scorecard -->
    <aside class="axiom-panel">
      <AxiomScorecard :node="selectedNode" />
    </aside>

    <!-- Bottom Panel: Graph Viewer -->
    <div class="graph-panel">
      <GraphViewer
        :graph-data="knowledgeGraph"
        :focus-entity="selectedEntity"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useResearchStore } from '@/stores/research'

const researchStore = useResearchStore()
const question = ref('')
const selectedNode = ref(null)

const startResearch = async () => {
  await researchStore.startResearch(question.value)
}

const expandNode = async (nodeId) => {
  await researchStore.expandNode(nodeId)
}

const pruneNode = async (nodeId, reason) => {
  await researchStore.pruneNode(nodeId, reason)
}
</script>
```

**GraphViewer.vue (D3.js Integration):**
```vue
<template>
  <div class="graph-viewer">
    <svg ref="svgRef" width="100%" height="500"></svg>

    <!-- Controls -->
    <div class="controls">
      <button @click="zoomIn">+</button>
      <button @click="zoomOut">-</button>
      <button @click="resetView">Reset</button>
      <select v-model="colorBy">
        <option value="axiom">Color by Axiom Alignment</option>
        <option value="source">Color by Source</option>
        <option value="confidence">Color by Confidence</option>
      </select>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import * as d3 from 'd3'

const props = defineProps({
  graphData: Object,
  focusEntity: String
})

const svgRef = ref(null)
let simulation = null

onMounted(() => {
  initGraph()
})

watch(() => props.graphData, () => {
  updateGraph()
})

const initGraph = () => {
  // D3 force-directed graph
  simulation = d3.forceSimulation()
    .force("link", d3.forceLink().id(d => d.id))
    .force("charge", d3.forceManyBody().strength(-300))
    .force("center", d3.forceCenter(width / 2, height / 2))
}

const updateGraph = () => {
  // Update nodes and edges
  // Color by axiom alignment, source, or confidence
}
</script>
```

### Phase 3.3: New Views

**New Views:**
```
gui/src/views/
├── SovereignResearch.vue        # Main research interface
├── AxiomLibrary.vue             # Manage axioms
└── GraphExplorer.vue            # Standalone graph viewer
```

**Update Router:**
```javascript
// gui/src/router/index.js
{
  path: '/research',
  name: 'SovereignResearch',
  component: () => import('@/views/SovereignResearch.vue')
},
{
  path: '/axioms',
  name: 'AxiomLibrary',
  component: () => import('@/views/AxiomLibrary.vue')
},
{
  path: '/graph',
  name: 'GraphExplorer',
  component: () => import('@/views/GraphExplorer.vue')
}
```

**Deliverables:**
- ✅ API endpoints (7 new routes)
- ✅ Vue components (ToT, Graph, Axiom viewers)
- ✅ New views integrated
- ✅ D3.js graph visualization working

---

## Sprint 4: Data Collection & Polish (Week 8-10)

**Goal:** Web scraping, final integration, testing

### Phase 4.1: Web Scraping Integration

**New Files:**
```
src/services/web_scraper.py       # Crawl4AI wrapper
src/services/friction_detector.py # Analyze scraped data
config/techniques/grounding/friction_detector.json
```

**WebScraper Implementation:**
```python
from crawl4ai import WebCrawler

class SovereignScraper:
    """
    AI-friendly web scraping for friction detection
    """

    def __init__(self):
        self.crawler = WebCrawler()

    async def scrape_reddit(self, query, subreddits, max_posts=50):
        """
        Search Reddit for friction/pain points
        Returns: [{
            "post_id": "...",
            "title": "...",
            "text": "...",
            "url": "...",
            "upvotes": 123,
            "comments": 45
        }]
        """

    async def scrape_web(self, query, max_pages=10):
        """
        General web search + scrape
        Returns markdown-formatted content
        """

class FrictionDetector:
    """
    Analyze scraped data for real-world friction
    """

    def __init__(self, llm_client, graph_manager):
        self.llm = llm_client
        self.graph = graph_manager

    def detect_friction(self, scraped_data, tot_branch):
        """
        Use local LLM to analyze scraped data
        Extract: problems, complaints, unmet needs

        Returns: {
            "friction_score": 0.0-1.0,
            "key_problems": [...],
            "entities": [...],  # For graph
            "verdict": "high_friction" | "medium" | "low"
        }
        """

    def add_to_graph(self, friction_data, tot_node_id):
        """
        Add friction entities to knowledge graph
        Link to ToT node
        """
```

### Phase 4.2: External Model Integrations

**Enhance Multi-AI Tools:**
```python
# src/tools/multi_ai/prompt_generator.py

# Add ToT-specific prompts
def generate_tot_exploration_prompt(question, depth, context):
    """
    Generate optimized prompt for ToT expansion
    Tailored per external model (Claude, GPT-4, Gemini)
    """

# src/tools/multi_ai/response_analyzer.py

# Add entity extraction
def extract_entities_for_graph(response, extraction_schema):
    """
    Parse external model response
    Extract fact triplets for knowledge graph

    Returns: [
        {
            "subject": "Tesla",
            "predicate": "competes_with",
            "object": "Rivian",
            "metadata": {...}
        }
    ]
    """
```

### Phase 4.3: End-to-End Testing

**Test Scenarios:**

1. **Complete Research Flow:**
   ```
   Question: "What e-commerce niche should I explore in 2026?"

   Phase 0 (Exploration):
   - ToT generates 3 branches
   - External model (Claude) explores each
   - Entities extracted to graph (50+ nodes)

   Phase 1 (Grounding):
   - Reddit scraping finds friction for Branch 1 & 3
   - Branch 2 pruned (no friction)
   - Axiom check: Branch 1 contradicts "time_preference"
   - Branch 1 pruned

   Phase 2 (Reasoning):
   - MCTS evaluates Branch 3 (10 simulations)
   - Python simulation: LTV/CAC ratio = 4.2 ✓
   - Break-even: 8 months ✓

   Phase 3 (Synthesis):
   - Final report generated
   - Confidence: 0.82
   - Axiom alignment: 0.95
   ```

2. **Axiom Conflict Test:**
   ```
   Axiom: "opportunity_cost" (high priority)
   Node: "Business requires 60h/week, €3k/month profit"

   Expected: Low score (poor time ROI)
   Actual: Score 0.25, verdict "contradicts"
   ```

3. **Graph Scaling Test:**
   ```
   Add 1000 entities
   Query subgraph (depth=3)
   Convert to text

   Expected: <2000 tokens, <200ms query time
   ```

### Phase 4.4: Documentation & Polish

**Documentation Updates:**
- [ ] User guide: "Getting Started with Sovereign Research"
- [ ] Developer guide: "Adding Custom Axioms"
- [ ] API documentation (Swagger/OpenAPI)
- [ ] Video tutorial (screen recording)

**Code Polish:**
- [ ] Type hints everywhere (mypy validation)
- [ ] Docstrings (Google style)
- [ ] Error handling (graceful degradation)
- [ ] Logging (structured logs with context)
- [ ] Configuration validation (pydantic schemas)

**Deliverables:**
- ✅ Web scraping working (Reddit + general web)
- ✅ External model integrations complete
- ✅ End-to-end tests passing (3+ scenarios)
- ✅ Documentation complete
- ✅ Production-ready codebase

---

## Optional: Sprint 5+ (Future Enhancements)

### Vector Database Integration
- Qdrant/ChromaDB for long-term memory
- Store graph snapshots with embeddings
- Semantic search across past research

### Advanced Reasoning
- DSPy integration (programmatic prompt optimization)
- Self-correction loops (STaR pattern)
- Multi-agent debates

### Business Features
- Export formats (PDF reports, Notion pages)
- Template library (GTM strategies, investment memos)
- Collaboration (share graphs, axioms)

### Performance Optimization
- Async/await everywhere
- Graph caching strategies
- Model quantization experiments (GGUF Q4_K_M vs Q5_K_M)

---

## Migration Strategy

### Coexistence Period (Sprint 1-3)

Keep old system running while building new:
- Old routes: `/api/v1/*` (ResearchCreator, old workflows)
- New routes: `/api/v2/*` (SovereignResearch)
- Frontend: Feature flag to toggle between modes

### Gradual Migration (Sprint 4)

Phase out old components:
1. Migrate validation techniques → graph operations
2. Convert old workflows → reasoning patterns
3. Archive `ResearchCreator.vue` → `archive/gui/`
4. Update default route to new system

### Deprecation

After Sprint 4:
- Remove `/api/v1/*` routes
- Archive old config files
- Keep only: `config/axioms/`, `config/techniques/reasoning/`

---

## Success Metrics

### Technical
- [ ] Knowledge graph: 10,000+ nodes, <500ms queries
- [ ] VRAM usage: <9GB during inference
- [ ] ToT depth: 4 levels, 3 branches per level
- [ ] MCTS simulations: 10-20 iterations in <60s

### Business
- [ ] First sovereign report generated
- [ ] Axiom library: 20+ axioms across 5 categories
- [ ] User feedback: "More objective than ChatGPT"

### Code Quality
- [ ] Test coverage: >70% (pytest)
- [ ] Type hints: 100% (mypy --strict)
- [ ] Documentation: All public APIs documented
- [ ] Performance: No regression vs. old system

---

## Risk Management

| Risk | Impact | Mitigation |
|------|--------|------------|
| DeepSeek-R1 too slow | High | Use faster model (Qwen 2.5 7B), optimize prompts |
| VRAM overflow | High | Aggressive KV-cache quantization, reduce context |
| Graph queries too slow | Medium | Add caching layer, limit subgraph depth |
| External API rate limits | Medium | Add retry logic, queue requests |
| User finds ToT too complex | Low | Add "Simple Mode" (Phase 0+3 only) |

---

## Appendix: File Structure (After Sprint 4)

```
deep-research-orchestrator/
├── config/
│   ├── axioms/                    # NEW: Value system
│   │   ├── economic_principles.json
│   │   ├── risk_tolerance.json
│   │   └── time_preference.json
│   ├── techniques/
│   │   ├── reasoning/             # NEW: ToT, MCTS
│   │   ├── grounding/             # NEW: Friction, scraping
│   │   ├── graph_extraction/      # NEW: Entity extraction
│   │   └── validation/            # KEPT: Existing techniques
│   ├── models/
│   │   ├── local/
│   │   │   └── deepseek_r1_7b.json
│   │   └── external/              # NEW
│   │       ├── claude_sonnet.json
│   │       └── gpt4o.json
│   └── schemas/
│       ├── axiom_schema.json      # NEW
│       ├── tot_node_schema.json   # NEW
│       └── graph_metadata_schema.json  # NEW
│
├── src/
│   ├── core/
│   │   ├── orchestrator.py        # REFACTORED
│   │   ├── graph_manager.py       # NEW
│   │   ├── axiom_judge.py         # NEW
│   │   ├── tot_manager.py         # NEW
│   │   ├── mcts_engine.py         # NEW
│   │   └── framework_loader.py    # KEPT
│   ├── services/
│   │   ├── web_scraper.py         # NEW
│   │   ├── friction_detector.py   # NEW
│   │   └── research_quality_helper.py  # KEPT
│   └── tools/
│       └── multi_ai/              # ENHANCED
│
├── gui/
│   └── src/
│       ├── components/
│       │   ├── ToTExplorer.vue    # NEW
│       │   ├── GraphViewer.vue    # NEW
│       │   └── AxiomEditor.vue    # NEW
│       └── views/
│           ├── SovereignResearch.vue  # NEW (main)
│           ├── AxiomLibrary.vue   # NEW
│           └── Dashboard.vue      # ENHANCED
│
├── tests/                         # NEW: Comprehensive tests
│   ├── test_graph_manager.py
│   ├── test_axiom_judge.py
│   ├── test_tot_manager.py
│   ├── test_mcts_engine.py
│   └── test_end_to_end.py
│
├── docs/
│   ├── architecture/
│   │   └── SOVEREIGN_RESEARCH_ARCHITECT.md
│   ├── guides/
│   │   ├── getting_started.md     # NEW
│   │   └── custom_axioms.md       # NEW
│   └── IMPLEMENTATION_ROADMAP.md  # This file
│
└── archive/                       # OLD: Deprecated files
    ├── implementation_reports/
    └── hardware_guides/
```

---

## Conclusion

This roadmap transforms your project from a **prompt-based research tool** into a **sovereign reasoning system** that combines the best of external AI (breadth) with local AI (depth) while maintaining independence through axiom-driven validation and graph-based truth preservation.

**Key Innovation:** The Knowledge Graph acts as a "firewall" between external bias and your values, enabling true sovereign decision-making.

**Next Step:** Begin Sprint 0 technical validation (DeepSeek-R1 setup + NetworkX testing).
