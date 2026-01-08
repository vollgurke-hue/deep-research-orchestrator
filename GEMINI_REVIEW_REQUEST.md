# Gemini Review Request: Sovereign Research Architect v2.0

**Date:** 2026-01-08
**Status:** Ready for Final Review
**Purpose:** Validate architecture before implementation Sprint 1

---

## Executive Summary

We have transformed the **Deep Research Orchestrator** from a linear prompt-based system into the **Sovereign Research Architect** - a graph-based, axiom-driven reasoning system that combines local abliterated models with manual multi-AI orchestration.

**Core Innovation:**
- **Knowledge Graph** (NetworkX) as "truth buffer" separating facts from opinions
- **Axiom-Library** as configurable value filter (user defines their worldview)
- **Tree of Thoughts (ToT)** for exploration + **MCTS** for path evaluation
- **Conflict Resolution** system for contradictory data
- **Resource Orchestration** for 11GB VRAM / 16GB RAM constraints

---

## 1. System Overview

### Architecture: The Three-Layer Pattern

```
┌─────────────────────────────────────────────────────┐
│ LAYER 1: DESCRIPTION (Static - "What")              │
│                                                      │
│ config/                                              │
│ ├── axioms/           NEW: User's value system      │
│ ├── techniques/       Reasoning operations          │
│ ├── workflows/        Reasoning patterns (ToT/MCTS) │
│ └── models/          Local model configs            │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ LAYER 2: WORKING STATE (Dynamic - "How")            │
│                                                      │
│ working_state/                                       │
│ ├── knowledge_graph/  NetworkX (in-memory, 16GB RAM)│
│ │   ├── nodes/        Entities (facts, hypotheses)  │
│ │   └── edges/        Relationships (weighted!)     │
│ ├── tot_tree/         Tree of Thoughts structure    │
│ ├── mcts_state/       Monte Carlo search state      │
│ └── conflicts/        Unresolved contradictions     │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ LAYER 3: OUTPUT (Result - "What was produced")      │
│                                                      │
│ output/                                              │
│ ├── market_opportunity/   Structured reports        │
│ ├── risk_analysis/        Graph-based insights      │
│ ├── synthesis/            Final recommendations     │
│ └── graph_snapshots/      JSON exports              │
└─────────────────────────────────────────────────────┘
```

### The Sovereign Cycle (4 Phases)

| Phase | Technique | Purpose | Input → Output |
|-------|-----------|---------|----------------|
| **0: EXPLORATION** | ToT + Manual Multi-AI | Generate breadth | Question → ToT branches + MD responses |
| **1: GROUNDING** | Scraping + Axiom Filter | Reality check + values | External data → Weighted graph edges |
| **2: REASONING** | MCTS + Python Sims | Deep evaluation | Graph paths → Success probabilities |
| **3: SYNTHESIS** | Graph-to-Report | Sovereign decision | Winning path → Structured report |

---

## 2. Critical Design Decisions

### A. Hardware Constraints & Model Strategy

**Hardware:**
- 11GB VRAM (RTX 3060 Ti or similar)
- 16GB RAM
- No cloud dependencies (100% local-first)

**Model Tier Strategy:**

```python
TIER_1_EXTRACTION = {
    "model": "llama-3.1-8b-instruct-q4_k_m",
    "vram": "5-6GB",
    "use_cases": [
        "Entity extraction (Text → Graph triplets)",
        "Fact verification",
        "Simple contradiction detection"
    ]
}

TIER_2_REASONING = {
    "model": "deepseek-r1-distill-qwen-14b-q4_k_m",  # ← KEY DECISION
    "vram": "9GB (fits in 11GB with buffer)",
    "use_cases": [
        "ToT decomposition",
        "MCTS simulation",
        "Axiom evaluation",
        "Final synthesis"
    ]
}

# NO TIER 3 (No external API calls)
# Multi-AI is MANUAL: User copies prompts to Claude/GPT, pastes MD responses back
```

**Why DeepSeek-R1-14B?**
- ✅ Fits in 11GB VRAM (Qwen 32B needs 18GB → SWAP death)
- ✅ Strong reasoning capabilities (better than Llama 8B)
- ✅ Good cost/benefit at 14B parameters
- ✅ Q4_K_M quantization maintains quality

**Why NO External APIs?**
- User preference: Manual Multi-AI orchestration
- External models used via: Copy prompt → Paste to Claude → Save MD → Upload to system
- No API costs, no rate limits, full control

### B. Knowledge Graph Strategy

**Why NetworkX?**
- Lightweight (pure Python, no heavy database)
- In-memory (16GB RAM handles 10,000+ nodes easily)
- Rich algorithms (PageRank, ego_graph, shortest_path)
- Easy to export (JSON snapshots)

**Graph Structure:**

```python
# Node (Entity)
{
    "node_id": "Tesla",
    "type": "company",
    "confidence": 0.85,
    "sources": ["reuters.com", "reddit.com/r/teslamotors"],
    "timestamp": "2026-01-08T14:32:00"
}

# Edge (Relationship) - WEIGHTED!
{
    "source": "Tesla",
    "target": "Rivian",
    "predicate": "competes_with",
    "weight": 0.75,  # ← Axiom-based weighting!
    "axiom_scores": {
        "opportunity_cost": 0.8,
        "risk_tolerance": 0.6
    },
    "evidence": "Multiple Reddit threads discussing competition",
    "source_url": "reddit.com/r/electricvehicles/...",
    "disputed": false
}
```

**Key Innovation: Weighted Edges**
- Every edge evaluated against user's axioms
- Weight = Base confidence × Axiom alignment
- MCTS uses weights to navigate graph
- Negative weights = paths contradicting user's values

---

## 3. The 7 Critical Gaps (SOLVED)

### Gap 1: Graph-to-Prompt Translation ⚠️ HIGH

**Problem:** LLM cannot read Python NetworkX object directly.

**Solution: GraphToPromptSerializer**

```python
class GraphToPromptSerializer:
    """
    Converts graph subgraph to text (max 2000 tokens)

    Methods:
    1. Ego-graph extraction (focus entity + depth N)
    2. PageRank-based importance (top-K nodes)
    3. Keyword-based filtering (question → relevant nodes)

    Formats:
    - Markdown (most readable for LLMs)
    - Narrative (natural language for synthesis)
    - JSON (structured for analysis)
    """

    def serialize_with_context(self, graph, question, focus_entities=None):
        # 1. Extract relevant subgraph (<50 nodes)
        # 2. Convert to markdown
        # 3. Ensure <2000 tokens
        # 4. Return text for prompt
        pass
```

**Example Output (Markdown):**

```markdown
## Entities
- **Tesla** (company, confidence: 0.95)
- **Rivian** (company, confidence: 0.85)
- **Model 3** (product, confidence: 0.90)

## Relationships
- Tesla → competes_with → Rivian (weight: 0.75, source: reddit.com)
- Tesla → produces → Model 3 (weight: 0.90, source: tesla.com)
- Model 3 → has_price → $45,000 (weight: 0.80, source: tesla.com)
```

**Implementation Priority:** Sprint 1 - CRITICAL (cannot build graph system without this!)

---

### Gap 2: Conflict Resolution 🔴 CRITICAL

**Problem:** Contradictory facts in graph (e.g., "Market growing" vs "Market shrinking").

**Solution: 3-Tier Conflict Resolution System**

```python
class ConflictResolver:
    """
    Detects and resolves contradictions in knowledge graph

    Detection:
    - Antonym pairs (growing ↔ shrinking)
    - Numerical contradictions (5% ↔ -3%)
    - LLM-based for complex cases

    Resolution (3 tiers):
    """

    # TIER 1: Source Authority (Automatic)
    def resolve_by_source_authority(self, conflict):
        """
        Hierarchy:
        1.0: sec.gov, statista.com (official data)
        0.9: bloomberg.com, reuters.com
        0.7: forbes.com, techcrunch.com
        0.5: reddit.com, twitter.com

        Winner = Highest (authority × confidence)
        """
        pass

    # TIER 2: Temporal Resolution (Automatic)
    def resolve_by_recency(self, conflict):
        """
        If sources differ by >6 months:
        → Newer source wins (market data changes!)
        """
        pass

    # TIER 3: Active Research (NEW ToT Branch!)
    def resolve_by_research(self, conflict):
        """
        Cannot auto-resolve → Create ToT research branch

        Process:
        1. Generate research question
        2. Create high-priority ToT node
        3. Trigger targeted web scraping
        4. User manually reviews results
        5. User decides winner or both kept as "disputed"

        This is CORE of sovereign logic!
        """
        pass
```

**Why Tier 3 is powerful:**
- System doesn't "guess" or "hallucinate"
- Contradictions trigger active research
- User stays in control (sovereign!)
- Graph marked as "incomplete" until resolved

**Implementation Priority:** Sprint 1 - CRITICAL (fundamental to graph integrity)

---

### Gap 3: Resource Orchestrator (RAM Trap) 🔴 CRITICAL

**Problem:** 14B model (9GB) + Graph (500MB) + Vue GUI (1GB) + Browser (2GB) = 12.5GB → Swap hell!

**Solution: Dynamic Resource Orchestrator**

```python
class ResourceOrchestrator:
    """
    Prevents system from swapping (death by slowness)

    Strategies:
    1. Adaptive model selection (14B → 8B if RAM tight)
    2. Service pausing (GUI frozen during heavy inference)
    3. Graph memory limits (max 10k nodes, then archive oldest)
    4. VRAM monitoring (unload model if not used >5min)
    """

    def execute_with_resource_management(self, task_type, task_func):
        # 1. Check current RAM/VRAM
        if self.check_resources()["swap_used"] > 1:  # >1GB swap = abort
            raise ResourceError("System already swapping!")

        # 2. Select model (14B or downgrade to 8B?)
        model_tier = self.select_optimal_model(task_type)

        # 3. Pause GUI if Tier 2 model loading
        if model_tier == "tier2":
            self.pause_non_essential_services()  # Vue GUI pauses!

        # 4. Execute task
        try:
            result = task_func(model_tier)
        finally:
            # 5. Resume GUI
            self.resume_services()

        return result
```

**User accepts GUI freeze:**
- During final synthesis (30-60 seconds)
- During MCTS heavy simulations
- Trade-off: Reliability > UX smoothness

**Implementation Priority:** Sprint 1 - CRITICAL (prevents system crashes)

---

### Gap 4: Graph Visualization 🔴 MOVED TO SPRINT 1

**Problem:** Cannot build graph system blind!

**Original Plan:** Graph viewer in Sprint 3
**New Plan:** Vue GUI component in Sprint 1

**Solution: Minimal Viable Graph Viewer (Vue Component)**

```vue
<!-- GraphViewerMinimal.vue -->
<template>
  <div class="graph-viewer">
    <!-- Simple force-directed graph with vis.js (not fancy D3) -->
    <div ref="networkContainer" style="height: 600px;"></div>

    <!-- Controls -->
    <div class="controls">
      <button @click="focusEntity">Focus on Entity</button>
      <button @click="showConflicts">Highlight Conflicts</button>
      <select v-model="colorMode">
        <option value="axiom">Color by Axiom Alignment</option>
        <option value="confidence">Color by Confidence</option>
        <option value="source">Color by Source</option>
      </select>
    </div>

    <!-- Stats -->
    <div class="stats">
      <p>Nodes: {{ graphStats.nodes }}</p>
      <p>Edges: {{ graphStats.edges }}</p>
      <p>Conflicts: {{ graphStats.conflicts }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Network } from 'vis-network'  // Simpler than D3!

// Load graph from API
const loadGraph = async () => {
  const response = await fetch('/api/graph/current')
  const data = await response.json()
  renderGraph(data)
}

const renderGraph = (data) => {
  const container = networkContainer.value

  // vis-network automatically handles layout
  const network = new Network(container, {
    nodes: data.nodes,
    edges: data.edges
  }, {
    physics: {
      enabled: true,
      stabilization: { iterations: 100 }
    }
  })

  // Color nodes by axiom alignment
  data.nodes.forEach(node => {
    if (node.axiom_alignment < 0.3) {
      node.color = '#ff4444'  // Red = contradicts axioms
    } else if (node.axiom_alignment < 0.7) {
      node.color = '#ffaa00'  // Yellow = neutral
    } else {
      node.color = '#44ff44'  // Green = aligns with axioms
    }
  })
}
</script>
```

**Why vis.js instead of D3.js?**
- ✅ Much simpler (force-directed graph out-of-the-box)
- ✅ Good enough for Sprint 1
- ✅ Can upgrade to D3.js later if needed

**Implementation Priority:** Sprint 1 - DAY 3 (after GraphManager works)

---

### Gap 5: MCTS Utility Function ⚠️ MEDIUM

**Problem:** Current MCTS only uses confidence. Economic decisions need **ROI/Time**!

**Solution: Multi-Dimensional Utility Function**

```python
class EnhancedMCTSUtility:
    """
    Economic utility scoring for MCTS node selection

    Formula:
    U = w1*Confidence + w2*(ROI/Hour) + w3*(1-Risk) + w4*AxiomAlign

    Weights (configurable in axioms):
    - Confidence: 15%
    - ROI/Hour: 35% (MOST IMPORTANT!)
    - Risk (inverse): 20%
    - Axiom Alignment: 30%
    """

    def calculate_utility(self, node, graph, axioms):
        # 1. Confidence from graph edges
        confidence = self._get_node_confidence(node, graph)

        # 2. ROI per Hour (from simulations or estimates)
        roi_per_hour = self._estimate_roi_per_hour(node, graph)
        roi_normalized = min(1.0, roi_per_hour / 100)  # €100/h = 1.0

        # 3. Risk (from contradiction count, axiom violations)
        risk = self._assess_risk(node, graph)
        risk_inverse = 1.0 - risk

        # 4. Axiom Alignment (weighted by priority)
        axiom_score = self._evaluate_axioms(node, graph, axioms)

        # Combine with weights
        utility = (
            0.15 * confidence +
            0.35 * roi_normalized +
            0.20 * risk_inverse +
            0.30 * axiom_score
        )

        return utility
```

**Example:**

```
Path A: "SaaS Business"
- Confidence: 0.85
- ROI/Hour: €75 → Normalized: 0.75
- Risk: 0.4 → Inverse: 0.6
- Axiom: 0.9 (aligns with "opportunity_cost")

Utility = 0.15*0.85 + 0.35*0.75 + 0.20*0.6 + 0.30*0.9
        = 0.128 + 0.263 + 0.12 + 0.27
        = 0.781 (GOOD!)

Path B: "Consulting Business"
- Confidence: 0.90
- ROI/Hour: €45 → Normalized: 0.45
- Risk: 0.3 → Inverse: 0.7
- Axiom: 0.5 (time investment borderline)

Utility = 0.15*0.90 + 0.35*0.45 + 0.20*0.7 + 0.30*0.5
        = 0.135 + 0.158 + 0.14 + 0.15
        = 0.583 (WORSE despite higher confidence!)
```

**Implementation Priority:** Sprint 2 (after MCTS basics work)

---

### Gap 6: Output Veredler (Business Formats) ⚠️ MEDIUM

**Problem:** Graph + JSON output ≠ usable business document.

**Solution: Template-Based Export System**

```python
class OutputVeredler:
    """
    Transforms graph + synthesis into business formats

    Formats:
    1. Investment Memo (for investors)
    2. GTM Strategy (go-to-market)
    3. Risk Assessment Report
    4. Market Opportunity Brief
    """

    def export_investment_memo(self, graph, synthesis):
        """
        Template structure:

        # Executive Summary
        - Opportunity: {extracted from winning MCTS path}
        - Market Size: {from graph entities tagged 'market_size'}
        - Competitive Advantage: {from axiom-aligned edges}
        - Risk Factors: {from conflict resolver + low-confidence nodes}

        # Market Analysis
        {Graph visualization screenshot + key insights}

        # Financial Projections
        {From Python simulations in MCTS}

        # Risks & Mitigation
        {Contradictions + disputed edges + axiom violations}

        # Recommendation
        {Synthesis with confidence score}
        """
        pass
```

**Implementation Priority:** Sprint 4 (nice-to-have, not critical for MVP)

---

### Gap 7: Human Intervention Interface ⚠️ MEDIUM

**Problem:** When does user intervene? Currently unclear.

**Solution: Defined Intervention Points**

```python
class HumanInterventionInterface:
    """
    4 intervention points where user must decide

    1. CONFLICT: Auto-resolution failed → User chooses winner
    2. AXIOM_VIOLATION: Path contradicts critical axiom → Continue or prune?
    3. UNCERTAINTY: MCTS cannot decide (multiple paths tied) → User picks
    4. MANUAL_PRUNING: User wants to cut ToT branch manually
    """

    def request_intervention(self, type, context):
        # Vue GUI shows modal:
        # "Conflict detected: Source A says X, Source B says Y"
        # Buttons: [Keep A] [Keep B] [Keep Both as Disputed] [Research More]
        pass
```

**Vue Component:**

```vue
<!-- InterventionModal.vue -->
<template>
  <div v-if="intervention" class="modal">
    <h2>{{ intervention.type }}: Manual Decision Required</h2>

    <div v-if="intervention.type === 'CONFLICT'">
      <p>Contradiction detected:</p>
      <div class="claim">
        <strong>Source A:</strong> {{ intervention.claim1.text }}
        <br><small>{{ intervention.claim1.source }}</small>
      </div>
      <div class="claim">
        <strong>Source B:</strong> {{ intervention.claim2.text }}
        <br><small>{{ intervention.claim2.source }}</small>
      </div>

      <div class="actions">
        <button @click="resolve('keep_a')">Trust Source A</button>
        <button @click="resolve('keep_b')">Trust Source B</button>
        <button @click="resolve('both_disputed')">Keep Both (Disputed)</button>
        <button @click="resolve('research')">Research More</button>
      </div>
    </div>
  </div>
</template>
```

**Implementation Priority:** Sprint 3 (after MCTS + Conflict Resolver stable)

---

## 4. Updated Tech Stack

### Backend (Python)

```
src/
├── core/
│   ├── orchestrator.py              # REFACTORED: 4-phase cycle
│   ├── graph_manager.py             # NEW: NetworkX wrapper
│   ├── graph_serializer.py          # NEW: Graph → Text
│   ├── axiom_judge.py               # NEW: Axiom evaluation
│   ├── conflict_resolver.py         # NEW: Contradiction handling
│   ├── resource_orchestrator.py     # NEW: RAM/VRAM management
│   ├── tot_manager.py               # NEW: Tree of Thoughts
│   └── mcts_engine.py               # NEW: Monte Carlo search
│
├── models/
│   ├── llama_cpp_client.py          # EXISTING: llama.cpp wrapper
│   └── model_manager.py             # NEW: Tier 1/2 loading
│
├── services/
│   ├── web_scraper.py               # NEW: Crawl4AI wrapper
│   ├── friction_detector.py         # NEW: Scraping analysis
│   └── research_quality_helper.py   # EXISTING
│
├── tools/
│   └── multi_ai/
│       ├── prompt_generator.py      # EXISTING: Generate prompts
│       └── response_parser.py       # NEW: Parse MD responses
│
└── utils/
    ├── token_counter.py             # EXISTING
    └── graph_validator.py           # NEW: Schema validation
```

### Frontend (Vue 3)

```
gui/src/
├── components/
│   ├── GraphViewerMinimal.vue       # NEW: vis.js graph (Sprint 1)
│   ├── ToTExplorer.vue              # NEW: Tree navigator
│   ├── AxiomEditor.vue              # NEW: Edit user axioms
│   ├── ConflictResolutionModal.vue  # NEW: User decisions
│   └── InterventionModal.vue        # NEW: Manual interventions
│
├── views/
│   ├── SovereignResearch.vue        # NEW: Main interface
│   ├── AxiomLibrary.vue             # NEW: Manage values
│   └── Dashboard.vue                # ENHANCED
│
└── stores/
    ├── researchStore.js             # NEW: Pinia store for research
    └── graphStore.js                # NEW: Graph state management
```

### Models

```
models/
├── llama-3.1-8b-instruct-q4_k_m.gguf       (~5GB)
└── deepseek-r1-distill-qwen-14b-q4_k_m.gguf (~9GB)

Serving: Ollama (recommended) or llama.cpp directly
```

---

## 5. Updated Implementation Roadmap

### Sprint 0: Foundation (Week 1) ✅ DONE

- [x] Codebase cleanup
- [ ] Install DeepSeek-R1-14B locally
- [ ] Test VRAM usage (must be <10GB)
- [ ] NetworkX performance validation (10k nodes)
- [ ] Create schemas (axiom, conflict, graph metadata)

### Sprint 1: Core Infrastructure (Week 2-3)

**Priority Order:**

1. **GraphManager** (Day 1-2)
   - NetworkX wrapper
   - Add/query fact triplets
   - Export/import JSON

2. **GraphToPromptSerializer** (Day 3) ⚠️ CRITICAL
   - Ego-graph extraction
   - Markdown conversion
   - Token budget enforcement

3. **AxiomJudge** (Day 4-5)
   - Load axiom configs
   - Evaluate node against axiom
   - Calculate weighted scores

4. **ConflictResolver** (Day 6-8) ⚠️ CRITICAL
   - Detect contradictions
   - 3-tier resolution
   - ToT branch creation (Tier 3)

5. **ResourceOrchestrator** (Day 9) ⚠️ CRITICAL
   - RAM/VRAM monitoring
   - Model tier selection
   - Service pausing

6. **GraphViewerMinimal (Vue)** (Day 10-12)
   - vis.js integration
   - API endpoints for graph data
   - Basic interaction (click node, highlight conflicts)

**Deliverables:**
- Graph with 1000+ nodes runs smoothly
- Conflicts detected and resolved
- No system slowdown (no swapping)
- Graph visible in Vue GUI

---

### Sprint 2: Reasoning Engines (Week 4-5)

1. **ToTManager**
   - Tree decomposition
   - Branch creation/pruning
   - Priority management

2. **MCTSEngine**
   - UCB1 selection
   - Python simulation execution
   - Backpropagation
   - Enhanced utility function (ROI/Time)

3. **Orchestrator Refactor**
   - 4-phase cycle
   - Integration of all components
   - Error handling

**Deliverables:**
- ToT tree with 4 levels
- MCTS evaluates paths (20 iterations <60s)
- Python simulations run successfully

---

### Sprint 3: GUI & User Interaction (Week 6-7)

1. **ToTExplorer (Vue)**
   - Interactive tree
   - Expand/prune branches
   - Show MCTS scores

2. **AxiomEditor (Vue)**
   - CRUD operations for axioms
   - Priority management
   - Live preview of impact

3. **InterventionInterface**
   - Conflict resolution modal
   - Axiom violation warnings
   - Manual pruning controls

4. **Graph Viewer Upgrade**
   - D3.js (optional, if vis.js insufficient)
   - Axiom alignment coloring
   - Conflict highlighting

**Deliverables:**
- Full user interface functional
- User can manage axioms
- User can intervene in research flow

---

### Sprint 4: Data Collection & Polish (Week 8-10)

1. **Web Scraping**
   - Crawl4AI integration
   - Reddit scraper
   - Friction detection

2. **Multi-AI Integration**
   - Prompt templates for Claude/GPT
   - MD file parser for responses
   - Entity extraction from MD

3. **Output Veredler**
   - Investment memo template
   - GTM strategy template
   - Export formats (MD, PDF)

4. **Testing & Documentation**
   - End-to-end tests
   - User guide
   - Video tutorial

**Deliverables:**
- Full research flow works
- Professional output formats
- Production-ready system

---

## 6. Key Architectural Patterns

### Pattern 1: Weighted Graph Navigation

```python
# Every edge has axiom-based weight
edge = {
    "source": "Business X",
    "target": "High profit potential",
    "weight": 0.85,  # Base confidence
    "axiom_scores": {
        "opportunity_cost": 0.9,   # Good ROI/Time
        "risk_tolerance": 0.6,     # Medium risk
        "time_preference": 0.8     # Fast break-even
    }
}

# Final weight = Base × Avg(axiom_scores weighted by priority)
# MCTS uses this weight for UCB1 calculation
```

### Pattern 2: Active Research (Conflict → ToT)

```python
# When conflict cannot auto-resolve:
if not resolved:
    # Create new ToT branch for research
    research_branch = tot_manager.create_branch(
        question=f"Resolve: {conflict.description}",
        priority="high",
        type="conflict_resolution"
    )

    # Trigger targeted scraping
    scraper.search(
        query=conflict.entities,
        sources=["official_data", "primary_sources"]
    )

    # User reviews results and decides
    # → Graph updated with resolution
```

### Pattern 3: Resource-Aware Execution

```python
# Heavy task (final synthesis with 14B model)
def synthesize_final_report():
    # 1. Check resources
    if swap_used > 1GB:
        raise ResourceError("System swapping!")

    # 2. Pause GUI
    orchestrator.pause_services(["vue_gui", "graph_viewer"])

    # 3. Load 14B model
    model = model_manager.load("tier2_reasoning")

    # 4. Execute (30-60 seconds)
    result = model.generate(synthesis_prompt)

    # 5. Resume GUI
    orchestrator.resume_services()

    return result
```

---

## 7. Validation Questions for Gemini

### Critical Architecture Questions

1. **Graph-to-Prompt Strategy:**
   - Is the approach (ego-graph + PageRank + markdown) sound?
   - Are we missing a better serialization method?
   - 2000 token limit - too conservative or too aggressive?

2. **Conflict Resolution Logic:**
   - Is the 3-tier approach (Authority → Recency → Research) complete?
   - Are we missing edge cases?
   - Should we add "User always decides" as Tier 0?

3. **Resource Management:**
   - Is pausing GUI acceptable UX trade-off?
   - Should we implement model swap (unload 14B → load 8B) instead?
   - Are there better RAM optimization strategies?

4. **MCTS Utility Function:**
   - Are the weights reasonable (35% ROI/Time, 30% Axiom, ...)?
   - Should weights be user-configurable per research?
   - Missing dimensions (e.g., market size, competition)?

5. **Axiom System:**
   - Is JSON config sufficient for complex axioms?
   - Should axioms have "code" field for Python logic?
   - How to handle axiom contradictions (user has conflicting values)?

### Implementation Concerns

6. **Sprint 1 Feasibility:**
   - Are we doing too much in Sprint 1?
   - Should Conflict Resolver be "basic" version first?
   - Is GraphViewer too ambitious for Sprint 1?

7. **Performance:**
   - 10,000 node graph - is NetworkX fast enough?
   - MCTS 20 iterations in <60s - realistic with 14B model?
   - Graph serialization - will it bottleneck?

8. **Missing Components:**
   - Do we need vector DB (Qdrant) for semantic search?
   - Should we implement graph persistence (SQLite)?
   - Long-term memory system for past research?

### Business Logic

9. **Multi-AI Orchestration:**
   - Manual workflow (MD files) - is this sustainable?
   - Should we add semi-automated API mode as option?
   - How to track which external model produced which nodes?

10. **Monetization:**
    - Is the architecture suitable for SaaS?
    - Can we add multi-tenancy later?
    - Export formats - which are most valuable?

---

## 8. Open Questions & Decisions Needed

### Technical Decisions

- [ ] **Model Serving:** Ollama or direct llama.cpp?
  - Ollama: Easier setup, more abstraction
  - llama.cpp: More control, slightly faster

- [ ] **Graph Persistence:** In-memory only or add SQLite?
  - In-memory: Faster, simpler
  - SQLite: Survives crashes, history tracking

- [ ] **Vue State Management:** Pinia or Vuex?
  - Pinia: Modern, simpler
  - Vuex: More established

- [ ] **Graph Library:** vis.js or D3.js for Sprint 1?
  - vis.js: Simpler, good enough
  - D3.js: More powerful, steeper learning curve

### Business Decisions

- [ ] **Open Source Strategy:** What to open source?
  - Core framework: Yes
  - Axiom templates: Premium?
  - Output templates: Premium?

- [ ] **Multi-AI Integration:** Support API mode later?
  - User preference: Manual (MD files) now
  - Future: Optional API integration?

---

## 9. Success Criteria

### Technical Metrics

- [ ] Graph: 10,000+ nodes, <500ms queries
- [ ] VRAM: Peak usage <10GB (with 14B model)
- [ ] RAM: No swapping (<14GB total usage)
- [ ] MCTS: 20 iterations in <60s
- [ ] Conflicts: 95% auto-resolved (Tier 1+2)

### User Experience

- [ ] Graph visible in real-time
- [ ] Axioms editable via GUI
- [ ] Conflicts resolvable with <5 clicks
- [ ] Final report generated in <2 minutes
- [ ] No system freezes >60s

### Quality Metrics

- [ ] Axiom alignment: User reports "matches my values"
- [ ] Contradiction detection: No false positives >5%
- [ ] Output quality: Better than "just asking ChatGPT"

---

## 10. Request for Gemini

Please review this architecture and provide:

1. **Critical Flaws:** What will definitely break in production?
2. **Missing Components:** What am I not seeing that's essential?
3. **Overengineering:** What can be simplified without losing core value?
4. **Performance Risks:** Where are the bottlenecks?
5. **Alternative Approaches:** Is there a better way to solve any of these problems?

**Specific focus areas:**
- Graph-to-Prompt serialization (Gap 1)
- Conflict resolution logic (Gap 2)
- Resource orchestration for 11GB VRAM (Gap 3)
- MCTS utility function for economic decisions (Gap 5)

---

## Appendix: Example Workflow

### User Story: "Should I start a SaaS business?"

**Phase 0: EXPLORATION**

1. User enters question in Vue GUI
2. ToT generates 3 branches:
   - Branch A: "What's the market size for SaaS in my niche?"
   - Branch B: "What's the typical time-to-profitability?"
   - Branch C: "What are the main risks?"

3. System generates prompts for each branch
4. User copies prompts → pastes to Claude → saves responses as MD files
5. System parses MD files → extracts entities → adds to graph

**Graph after Phase 0:**
- 50+ nodes (markets, competitors, technologies)
- 120+ edges (relationships)

**Phase 1: GROUNDING**

6. System detects: "Source A says 'SaaS market growing 20%', Source B says 'SaaS market saturated'"
7. Conflict Resolver:
   - Tier 1: Source A = statista.com (0.95), Source B = medium.com (0.45) → A wins
   - Edge marked: weight = 0.85

8. Axiom Judge evaluates all edges:
   - Edge "SaaS → requires → 60h/week" → axiom "opportunity_cost" → score 0.3 (BAD!)
   - Edge "SaaS → break-even → 18 months" → axiom "time_preference" → score 0.2 (BAD!)

**Phase 2: REASONING**

9. MCTS explores paths:
   - Path A (Full SaaS): Utility = 0.45 (mediocre)
   - Path B (Micro-SaaS): Utility = 0.78 (GOOD!)
   - Path C (Consulting): Utility = 0.55 (ok)

10. Python simulation for Path B:
    ```python
    # LLM generates this code
    def simulate_micro_saas():
        monthly_revenue = 5000
        time_per_week = 15
        break_even_months = 6

        roi_per_hour = (monthly_revenue * 12) / (time_per_week * 52)
        # = €76.92/hour → Good!

        return {"score": 0.82, "verdict": "viable"}
    ```

**Phase 3: SYNTHESIS**

11. System generates report:

```markdown
# Research Report: SaaS Business Opportunity

## Recommendation: PURSUE (Confidence: 0.78)
Micro-SaaS variant is viable based on your axioms.

## Key Findings
- Market: Growing 20% annually (statista.com, confidence: 0.95)
- Time Investment: 15h/week (acceptable per "opportunity_cost" axiom)
- Break-Even: 6 months (acceptable per "time_preference" axiom)
- ROI: €77/hour (exceeds €50 threshold)

## Risks
- Competition: High in generic SaaS (disputed data)
- Technical Complexity: Moderate

## Axiom Alignment
✅ opportunity_cost: 0.85 (GOOD)
✅ time_preference: 0.75 (ACCEPTABLE)
⚠️ risk_tolerance: 0.55 (BORDERLINE)

## Graph Snapshot
[Exported JSON with 50 nodes, 120 edges]
```

**User sees:**
- Interactive graph (colored by axiom alignment)
- ToT tree (Path B highlighted as winner)
- Structured report
- Download options (MD, JSON, PDF)

---

**End of Review Request**

This architecture represents 8 days of iterative design, incorporating:
- Original Deep Research Orchestrator strengths
- Gemini's sovereignty + reasoning concepts
- Critical gap analysis and solutions
- Hardware reality (11GB VRAM, 16GB RAM)
- User preferences (manual Multi-AI, Vue GUI, full complexity)

**Ready for final validation before Sprint 1 implementation.**
