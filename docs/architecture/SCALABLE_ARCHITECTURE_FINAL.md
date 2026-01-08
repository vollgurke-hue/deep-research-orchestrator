# Scalable Architecture: Hardware-Agnostic Sovereign Research Architect

**Version:** 2.1 FINAL
**Date:** 2026-01-08
**Status:** Ready for Implementation
**Philosophy:** Architecture before Hardware

---

## Executive Summary

Based on Gemini's critical feedback, we have evolved the architecture from "optimized for 11GB VRAM" to **"hardware-agnostic framework that scales with resources"**.

**Core Principle:** The logic stays constant, the models scale.

**Today's Reality:**
- 11GB VRAM, 16GB RAM
- DeepSeek-R1-14B for reasoning
- Accept latency for quality

**Tomorrow's Potential:**
- 24GB+ VRAM, 64GB+ RAM
- 70B/405B models
- Multi-GPU setups
- Zero code changes needed

---

## 1. The Abstraction Layer: Model-Provider-Switcher

### Philosophy

The system must never care *which* model provides the intelligence. It only cares about:
1. **Capability tier** (extraction, reasoning, synthesis)
2. **Quality level** (fast, balanced, quality)
3. **Resource constraints** (current hardware)

### Implementation: ModelProvider Interface

```python
from abc import ABC, abstractmethod
from enum import Enum

class ModelCapability(Enum):
    """What the model is good at"""
    EXTRACTION = "extraction"          # Text → Graph triplets
    REASONING = "reasoning"            # ToT decomposition, MCTS
    SYNTHESIS = "synthesis"            # Final report writing
    VALIDATION = "validation"          # Axiom evaluation, conflict resolution

class QualityLevel(Enum):
    """Speed vs Quality trade-off"""
    FAST = "fast"           # Quick, good enough (7-8B)
    BALANCED = "balanced"   # Good balance (14B)
    QUALITY = "quality"     # Best results (32B+)
    ULTRA = "ultra"         # State-of-the-art (70B+)

class ModelProvider(ABC):
    """
    Abstract interface for any model backend

    Implementations:
    - LocalOllamaProvider (Ollama local models)
    - LocalVLLMProvider (vLLM local models)
    - ExternalAPIProvider (Claude, GPT-4 via API)
    - MultiGPUProvider (vLLM distributed across GPUs)
    """

    @abstractmethod
    def get_available_capabilities(self) -> dict[ModelCapability, list[QualityLevel]]:
        """
        Return what this provider can do

        Example (local 14B):
        {
            ModelCapability.EXTRACTION: [QualityLevel.FAST, QualityLevel.BALANCED],
            ModelCapability.REASONING: [QualityLevel.BALANCED],
            ModelCapability.SYNTHESIS: [QualityLevel.BALANCED],
            ModelCapability.VALIDATION: [QualityLevel.BALANCED]
        }
        """
        pass

    @abstractmethod
    def generate(self, prompt: str, capability: ModelCapability,
                 quality: QualityLevel, **kwargs) -> str:
        """
        Generate response

        Provider internally selects best model for capability + quality
        """
        pass

    @abstractmethod
    def get_resource_usage(self) -> dict:
        """Return current VRAM/RAM usage"""
        pass


class LocalOllamaProvider(ModelProvider):
    """
    Local models via Ollama

    Configuration:
    models = {
        "fast": "llama-3.1-8b-instruct",
        "balanced": "deepseek-r1-14b",
        "quality": None  # Not available with 11GB VRAM
    }
    """

    def __init__(self, config_path="config/models/local_ollama.json"):
        self.config = self._load_config(config_path)
        self.loaded_models = {}

    def get_available_capabilities(self):
        """Check what current hardware supports"""
        vram_available = self._check_vram()

        capabilities = {
            ModelCapability.EXTRACTION: [],
            ModelCapability.REASONING: [],
            ModelCapability.SYNTHESIS: [],
            ModelCapability.VALIDATION: []
        }

        # Fast (8B) - Always available
        if vram_available >= 6:
            for cap in capabilities:
                capabilities[cap].append(QualityLevel.FAST)

        # Balanced (14B) - Needs 9GB
        if vram_available >= 9:
            for cap in capabilities:
                capabilities[cap].append(QualityLevel.BALANCED)

        # Quality (32B) - Needs 18GB (not available now)
        if vram_available >= 18:
            for cap in capabilities:
                capabilities[cap].append(QualityLevel.QUALITY)

        return capabilities

    def generate(self, prompt, capability, quality, **kwargs):
        """Route to appropriate model"""
        model_id = self._select_model(capability, quality)

        # Load if not loaded
        if model_id not in self.loaded_models:
            self._load_model(model_id)

        # Generate
        response = self.loaded_models[model_id].generate(prompt, **kwargs)

        return response

    def _select_model(self, capability, quality):
        """
        Select best available model for task

        Fallback chain:
        QUALITY → BALANCED → FAST
        """
        model_map = {
            QualityLevel.FAST: "llama-3.1-8b-instruct",
            QualityLevel.BALANCED: "deepseek-r1-14b",
            QualityLevel.QUALITY: "qwen-2.5-32b",  # Not available now!
            QualityLevel.ULTRA: None  # Never local with 11GB
        }

        # Try requested quality
        model_id = model_map.get(quality)
        if model_id and self._can_load_model(model_id):
            return model_id

        # Fallback to lower quality
        fallback_order = [
            QualityLevel.QUALITY,
            QualityLevel.BALANCED,
            QualityLevel.FAST
        ]

        for fallback in fallback_order:
            model_id = model_map[fallback]
            if model_id and self._can_load_model(model_id):
                logging.warning(
                    f"Requested {quality}, falling back to {fallback} "
                    f"(hardware constraint)"
                )
                return model_id

        raise RuntimeError("No suitable model available!")


class ExternalAPIProvider(ModelProvider):
    """
    Optional: External APIs for ultra-quality when needed

    Use case: User has critical synthesis, wants best possible
    → System offers to use Claude Opus or GPT-4o via API
    → User approves cost
    → System executes
    """

    def __init__(self, api_keys=None):
        self.apis = {
            "claude": ClaudeAPIClient(api_keys.get("anthropic")),
            "openai": OpenAIClient(api_keys.get("openai"))
        }

    def get_available_capabilities(self):
        """External APIs support ULTRA quality for all capabilities"""
        return {
            cap: [QualityLevel.ULTRA]
            for cap in ModelCapability
        }

    def generate(self, prompt, capability, quality, **kwargs):
        """Route to best external API"""
        # For reasoning/synthesis: Claude Opus
        if capability in [ModelCapability.REASONING, ModelCapability.SYNTHESIS]:
            return self.apis["claude"].generate(
                prompt,
                model="claude-opus-3",
                **kwargs
            )

        # For extraction: GPT-4o (faster, cheaper)
        return self.apis["openai"].generate(
            prompt,
            model="gpt-4o",
            **kwargs
        )


class ModelOrchestrator:
    """
    High-level interface: Request capability, get best provider

    User code never sees providers!
    """

    def __init__(self, providers: list[ModelProvider],
                 resource_profile: str = "balanced"):
        self.providers = providers
        self.profile = resource_profile
        self.quality_preferences = self._load_profile(resource_profile)

    def generate(self, prompt: str, capability: ModelCapability,
                 prefer_local: bool = True) -> str:
        """
        Main interface: Generate using best available provider

        Logic:
        1. Check what quality current profile requests
        2. Find provider that supports it
        3. If not available and prefer_local=False: Try external
        4. Execute with chosen provider
        """
        requested_quality = self.quality_preferences[capability]

        # Try local providers first
        for provider in self.providers:
            if self._provider_supports(provider, capability, requested_quality):
                return provider.generate(prompt, capability, requested_quality)

        # If not available locally and external allowed
        if not prefer_local:
            external = self._get_external_provider()
            if external:
                logging.warning(
                    f"Local providers insufficient for {capability} at "
                    f"{requested_quality}. Using external API."
                )
                return external.generate(prompt, capability, QualityLevel.ULTRA)

        # Fallback: Lower quality locally
        logging.warning("Falling back to lower quality model (local only)")
        for quality in [QualityLevel.BALANCED, QualityLevel.FAST]:
            for provider in self.providers:
                if self._provider_supports(provider, capability, quality):
                    return provider.generate(prompt, capability, quality)

        raise RuntimeError(f"No provider available for {capability}!")

    def _load_profile(self, profile_name):
        """
        Load resource profile

        Profiles:
        - "minimal": All FAST (for testing, low-end hardware)
        - "balanced": BALANCED for reasoning, FAST for extraction
        - "quality": BALANCED for extraction, QUALITY for reasoning
        - "ultra": QUALITY everywhere (requires high-end hardware or API)
        """
        profiles = {
            "minimal": {
                ModelCapability.EXTRACTION: QualityLevel.FAST,
                ModelCapability.REASONING: QualityLevel.FAST,
                ModelCapability.SYNTHESIS: QualityLevel.FAST,
                ModelCapability.VALIDATION: QualityLevel.FAST
            },
            "balanced": {
                ModelCapability.EXTRACTION: QualityLevel.FAST,
                ModelCapability.REASONING: QualityLevel.BALANCED,
                ModelCapability.SYNTHESIS: QualityLevel.BALANCED,
                ModelCapability.VALIDATION: QualityLevel.BALANCED
            },
            "quality": {
                ModelCapability.EXTRACTION: QualityLevel.BALANCED,
                ModelCapability.REASONING: QualityLevel.QUALITY,
                ModelCapability.SYNTHESIS: QualityLevel.QUALITY,
                ModelCapability.VALIDATION: QualityLevel.QUALITY
            },
            "ultra": {
                ModelCapability.EXTRACTION: QualityLevel.QUALITY,
                ModelCapability.REASONING: QualityLevel.ULTRA,
                ModelCapability.SYNTHESIS: QualityLevel.ULTRA,
                ModelCapability.VALIDATION: QualityLevel.ULTRA
            }
        }

        return profiles.get(profile_name, profiles["balanced"])
```

### Usage in Orchestrator

```python
# In SovereignOrchestrator.__init__()
class SovereignOrchestrator:
    def __init__(self, config):
        # Setup providers
        local_provider = LocalOllamaProvider()
        # external_provider = ExternalAPIProvider(api_keys)  # Optional

        # Create orchestrator
        self.model_orchestrator = ModelOrchestrator(
            providers=[local_provider],
            resource_profile=config.get("profile", "balanced")
        )

    def run_tot_decomposition(self, question):
        """
        ToT decomposition - needs reasoning capability

        System automatically uses:
        - Today: DeepSeek-R1-14B (BALANCED)
        - Tomorrow with 24GB VRAM: Qwen-32B (QUALITY)
        - Or with API access: Claude Opus (ULTRA)

        NO CODE CHANGES!
        """
        prompt = f"Decompose this question using ToT: {question}"

        response = self.model_orchestrator.generate(
            prompt=prompt,
            capability=ModelCapability.REASONING,
            prefer_local=True  # User preference: Stay local if possible
        )

        return response
```

---

## 2. Memory-Management Profiles

### Philosophy

RAM is the second bottleneck. With 16GB, we must be smart. With 64GB, we can be luxurious.

### Implementation: ProfileManager

```python
class MemoryProfile(Enum):
    """Memory management strategies"""
    MINIMAL = "minimal"      # <8GB RAM (graph in SQLite, small context)
    LOW = "low"              # 8-16GB RAM (graph in RAM, limited context)
    STANDARD = "standard"    # 16-32GB RAM (full graph, normal context)
    HIGH = "high"            # 32-64GB RAM (large graphs, big context)
    ULTRA = "ultra"          # 64GB+ RAM (unlimited, everything in memory)

class ProfileManager:
    """
    Adapt system behavior to available resources
    """

    def __init__(self, profile: MemoryProfile):
        self.profile = profile
        self.limits = self._get_limits(profile)

    def _get_limits(self, profile):
        """Define constraints per profile"""
        profiles = {
            MemoryProfile.MINIMAL: {
                "max_graph_nodes": 1000,
                "max_context_tokens": 2048,
                "graph_storage": "sqlite",  # On-disk
                "cache_strategy": "minimal",
                "gui_mode": "text"  # Terminal only
            },
            MemoryProfile.LOW: {
                "max_graph_nodes": 5000,
                "max_context_tokens": 4096,
                "graph_storage": "memory",
                "cache_strategy": "lru",
                "gui_mode": "minimal_vue"  # Basic GUI
            },
            MemoryProfile.STANDARD: {
                "max_graph_nodes": 10000,
                "max_context_tokens": 8192,
                "graph_storage": "memory",
                "cache_strategy": "aggressive",
                "gui_mode": "full_vue"
            },
            MemoryProfile.HIGH: {
                "max_graph_nodes": 50000,
                "max_context_tokens": 16384,
                "graph_storage": "memory",
                "cache_strategy": "unlimited",
                "gui_mode": "full_vue"
            },
            MemoryProfile.ULTRA: {
                "max_graph_nodes": None,  # Unlimited
                "max_context_tokens": 128000,  # Full context
                "graph_storage": "memory",
                "cache_strategy": "unlimited",
                "gui_mode": "full_vue"
            }
        }

        return profiles[profile]

    def should_offload_graph(self):
        """Should graph be in SQLite or RAM?"""
        return self.limits["graph_storage"] == "sqlite"

    def get_max_subgraph_size(self):
        """How many nodes can we load for LLM context?"""
        # Based on token budget
        return min(
            100,  # Never more than 100 nodes at once
            self.limits["max_context_tokens"] // 20  # ~20 tokens per node
        )

    def can_run_gui(self):
        """Should we start Vue GUI?"""
        return self.limits["gui_mode"] in ["minimal_vue", "full_vue"]

    def pause_gui_for_task(self, task_type):
        """
        Should GUI pause for this task?

        STANDARD profile: Yes (tight RAM)
        HIGH/ULTRA profile: No (plenty of RAM)
        """
        if self.profile in [MemoryProfile.HIGH, MemoryProfile.ULTRA]:
            return False  # No need to pause

        # For STANDARD and below: Pause for heavy tasks
        heavy_tasks = ["synthesis", "mcts_simulation", "conflict_resolution"]
        return task_type in heavy_tasks
```

---

## 3. Enhanced Conflict Resolution: Debate Pattern

### Philosophy

Two models arguing find better truth than one model judging.

### Implementation: DebateResolver

```python
class DebateResolver:
    """
    Let two model instances debate contradictions

    Process:
    1. Model A (Advocate): Argues for Claim 1
    2. Model B (Skeptic): Argues for Claim 2
    3. Model A rebuts Model B
    4. Model B rebuts Model A
    5. Judge (same or higher quality model) decides winner

    Requires: At least BALANCED quality (14B+)
    """

    def __init__(self, model_orchestrator):
        self.models = model_orchestrator

    def resolve_by_debate(self, conflict, rounds=2):
        """
        Resolve conflict through multi-round debate

        conflict = {
            "subject": "Market X",
            "claim_1": ("growing", source_data_1),
            "claim_2": ("shrinking", source_data_2)
        }
        """
        claim1, data1 = conflict["claim_1"]
        claim2, data2 = conflict["claim_2"]

        # Round 1: Initial arguments
        advocate_prompt = f"""
        You are defending the claim: "{conflict['subject']} is {claim1}"

        Evidence:
        {self._format_evidence(data1)}

        Construct the strongest possible argument for this claim.
        """

        skeptic_prompt = f"""
        You are defending the claim: "{conflict['subject']} is {claim2}"

        Evidence:
        {self._format_evidence(data2)}

        Construct the strongest possible argument for this claim.
        """

        advocate_arg = self.models.generate(
            advocate_prompt,
            capability=ModelCapability.REASONING,
            prefer_local=True
        )

        skeptic_arg = self.models.generate(
            skeptic_prompt,
            capability=ModelCapability.REASONING,
            prefer_local=True
        )

        # Round 2: Rebuttals
        for round_num in range(rounds):
            # Advocate rebuts Skeptic
            rebuttal_prompt_a = f"""
            The opposing argument claims:
            {skeptic_arg}

            Rebut this argument. Point out logical flaws, cite stronger evidence,
            or show why your position ({claim1}) is more credible.
            """

            advocate_rebuttal = self.models.generate(
                rebuttal_prompt_a,
                capability=ModelCapability.REASONING,
                prefer_local=True
            )

            # Skeptic rebuts Advocate
            rebuttal_prompt_b = f"""
            The opposing argument claims:
            {advocate_arg}

            Additionally, they rebut your position with:
            {advocate_rebuttal}

            Counter-argue. Show why your position ({claim2}) remains stronger.
            """

            skeptic_rebuttal = self.models.generate(
                rebuttal_prompt_b,
                capability=ModelCapability.REASONING,
                prefer_local=True
            )

            # Update arguments for next round
            advocate_arg = advocate_rebuttal
            skeptic_arg = skeptic_rebuttal

        # Final: Judge evaluates
        judge_prompt = f"""
        Two claims have been debated:

        CLAIM A: "{conflict['subject']} is {claim1}"
        Final argument:
        {advocate_arg}

        CLAIM B: "{conflict['subject']} is {claim2}"
        Final argument:
        {skeptic_arg}

        As an impartial judge, evaluate:
        1. Which argument is logically stronger?
        2. Which has better evidence quality?
        3. Are there unresolved contradictions?

        Return JSON:
        {{
            "winner": "A" or "B" or "undecided",
            "confidence": 0.0-1.0,
            "reasoning": "...",
            "recommendation": "accept_winner" or "keep_both_disputed" or "research_more"
        }}
        """

        judgment = self.models.generate(
            judge_prompt,
            capability=ModelCapability.VALIDATION,
            prefer_local=True
        )

        judgment_data = json.loads(judgment)

        # If undecided or low confidence → Tier 3 (active research)
        if judgment_data["winner"] == "undecided" or judgment_data["confidence"] < 0.7:
            return {
                "resolution": "active_research",
                "reason": "Debate inconclusive, requires external evidence"
            }

        # Clear winner
        winner_claim = claim1 if judgment_data["winner"] == "A" else claim2
        return {
            "resolution": "debate",
            "winner": winner_claim,
            "confidence": judgment_data["confidence"],
            "reasoning": judgment_data["reasoning"]
        }
```

---

## 4. Dynamic Subgraph Extraction (Context Optimization)

### Philosophy

Even with 128k context, relevance beats volume. Extract *smart*, not *all*.

### Implementation: RelevanceScorer

```python
class DynamicSubgraphExtractor:
    """
    Extract most relevant subgraph for current question

    Methods:
    1. Keyword matching (fast)
    2. Embedding similarity (if vector DB available)
    3. PageRank + Ego-graph (structural importance)
    """

    def __init__(self, graph_manager, profile_manager):
        self.graph = graph_manager
        self.profile = profile_manager

    def extract_for_question(self, graph, question, max_tokens=2000):
        """
        Extract relevant subgraph optimized for question

        Steps:
        1. Find seed nodes (keywords/entities in question)
        2. Expand via ego-graph (depth 2-3)
        3. Score nodes by relevance
        4. Take top-N until token budget
        """
        # 1. Seed nodes
        keywords = self._extract_keywords(question)
        seed_nodes = self._find_nodes_by_keywords(graph, keywords)

        if not seed_nodes:
            # Fallback: PageRank top nodes
            seed_nodes = self._get_top_pagerank_nodes(graph, k=5)

        # 2. Expand ego-graphs
        subgraphs = []
        for seed in seed_nodes:
            ego = nx.ego_graph(graph, seed, radius=2)
            subgraphs.append(ego)

        # Merge
        merged = nx.compose_all(subgraphs)

        # 3. Score nodes by relevance to question
        relevance_scores = {}
        for node_id in merged.nodes():
            score = self._calculate_relevance(node_id, question, graph)
            relevance_scores[node_id] = score

        # 4. Take top-N nodes within token budget
        sorted_nodes = sorted(
            relevance_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        selected_nodes = []
        estimated_tokens = 0
        max_tokens_budget = self.profile.limits["max_context_tokens"] // 2

        for node_id, score in sorted_nodes:
            node_tokens = self._estimate_node_tokens(graph, node_id)

            if estimated_tokens + node_tokens > max_tokens_budget:
                break

            selected_nodes.append(node_id)
            estimated_tokens += node_tokens

        # Extract subgraph with selected nodes
        final_subgraph = graph.subgraph(selected_nodes)

        return final_subgraph

    def _calculate_relevance(self, node_id, question, graph):
        """
        Score node relevance to question

        Factors:
        1. Keyword overlap (node text vs question)
        2. PageRank (structural importance)
        3. Edge weights (axiom alignment)
        4. Recency (newer = more relevant)
        """
        node_data = graph.nodes[node_id]

        # 1. Keyword overlap
        node_text = f"{node_id} {node_data.get('description', '')}".lower()
        question_keywords = set(self._extract_keywords(question))
        node_keywords = set(node_text.split())
        keyword_overlap = len(question_keywords & node_keywords) / len(question_keywords)

        # 2. PageRank
        pagerank = nx.pagerank(graph)
        structural_score = pagerank.get(node_id, 0)

        # 3. Average edge weight
        edges = list(graph.edges(node_id, data=True))
        avg_weight = np.mean([d.get('weight', 0.5) for _, _, d in edges]) if edges else 0.5

        # 4. Recency
        timestamp = node_data.get('timestamp', datetime.min)
        age_days = (datetime.now() - timestamp).days
        recency_score = 1.0 / (1.0 + age_days / 30)  # Decay over months

        # Combine
        relevance = (
            0.4 * keyword_overlap +
            0.2 * structural_score * 100 +  # Scale PageRank
            0.2 * avg_weight +
            0.2 * recency_score
        )

        return relevance
```

---

## 5. Updated Sprint 1 Tasks (Final)

### Phase 1: Foundation (Days 1-3)

**Day 1: Model Abstraction Layer**
- [ ] Implement `ModelProvider` abstract class
- [ ] Implement `LocalOllamaProvider`
- [ ] Implement `ModelOrchestrator`
- [ ] Create resource profiles config
- [ ] Test: Switch between 8B and 14B models

**Day 2: GraphManager + Profile System**
- [ ] Implement `GraphManager` (NetworkX wrapper)
- [ ] Implement `ProfileManager` (memory profiles)
- [ ] Add profile-aware graph limits
- [ ] Test: 10k nodes in STANDARD profile

**Day 3: Graph Serialization**
- [ ] Implement `DynamicSubgraphExtractor`
- [ ] Implement `GraphToPromptSerializer`
- [ ] Test: Extract + serialize subgraph <2000 tokens

### Phase 2: Conflict Resolution (Days 4-6)

**Day 4: Basic Conflict Detection**
- [ ] Implement `ConflictResolver` (Tier 1+2 only)
- [ ] Source authority resolution
- [ ] Temporal resolution
- [ ] Test: Auto-resolve 80% of synthetic conflicts

**Day 5: Debate Pattern**
- [ ] Implement `DebateResolver`
- [ ] Multi-round argument/rebuttal
- [ ] Judge evaluation
- [ ] Test: Debate resolves ambiguous conflicts

**Day 6: Integration**
- [ ] Connect ConflictResolver to GraphManager
- [ ] Add conflict tracking to graph
- [ ] API endpoints for conflict review

### Phase 3: Axiom System (Days 7-9)

**Day 7: AxiomJudge**
- [ ] Implement `AxiomJudge`
- [ ] Load axiom configs (JSON)
- [ ] Evaluate node against axiom
- [ ] Test: Score 100 nodes against 5 axioms

**Day 8: Weighted Edges**
- [ ] Add axiom scoring to edge creation
- [ ] Implement weighted score calculation
- [ ] Update GraphManager to store axiom scores

**Day 9: Axiom Editor (Vue)**
- [ ] Create `AxiomEditor.vue` component
- [ ] CRUD operations for axioms
- [ ] Live preview of impact on graph

### Phase 4: Graph Viewer (Days 10-12)

**Day 10: Minimal Viewer**
- [ ] Create `GraphViewerMinimal.vue`
- [ ] Integrate vis.js
- [ ] API endpoint: `/api/graph/current`
- [ ] Test: Display 100 nodes

**Day 11: Interaction**
- [ ] Click node → Show details
- [ ] Color by axiom alignment
- [ ] Highlight conflicts
- [ ] Focus on entity

**Day 12: Polish**
- [ ] Performance optimization
- [ ] Error handling
- [ ] User feedback

---

## 6. Hardware Scaling Roadmap

### Current: 11GB VRAM, 16GB RAM

**Profile:** STANDARD
**Models:**
- Tier 1: Llama-3.1-8B (FAST)
- Tier 2: DeepSeek-R1-14B (BALANCED)

**Capabilities:**
- Graph: 10k nodes
- MCTS: 20 iterations (~60s)
- Context: 8k tokens

**Limitations:**
- No QUALITY tier (32B won't fit)
- GUI pauses during heavy tasks
- Limited parallel processing

---

### Future: 24GB VRAM, 32GB RAM (RTX 4090)

**Profile:** HIGH
**Models:**
- Tier 1: Llama-3.1-8B (FAST)
- Tier 2: DeepSeek-R1-14B (BALANCED)
- Tier 3: Qwen-2.5-32B (QUALITY)

**Capabilities:**
- Graph: 50k nodes
- MCTS: 50 iterations (~45s)
- Context: 16k tokens
- No GUI pausing needed

**Code Changes:** ZERO! Just change profile in config:

```json
{
  "profile": "high",
  "models": {
    "fast": "llama-3.1-8b",
    "balanced": "deepseek-r1-14b",
    "quality": "qwen-2.5-32b"  // ← Now available!
  }
}
```

---

### Future: Multi-GPU Setup (2x RTX 4090, 128GB RAM)

**Profile:** ULTRA
**Models:**
- Tier 1: Llama-3.1-8B
- Tier 2: Qwen-2.5-32B
- Tier 3: Llama-3.1-70B (distributed)

**Capabilities:**
- Graph: Unlimited
- MCTS: 100+ iterations (~30s)
- Context: 128k tokens
- Parallel ToT exploration
- Real-time graph updates

**Code Changes:** Swap provider:

```python
# Before (single GPU)
provider = LocalOllamaProvider()

# After (multi-GPU)
provider = MultiGPUVLLMProvider(gpus=[0, 1])

# Everything else: SAME!
```

---

## 7. Conclusion: Architecture First

**Today's Constraints:**
- ✅ Accept latency (14B model slower than 8B)
- ✅ Accept GUI pauses (tight RAM)
- ✅ Accept token limits (8k context)

**In Exchange:**
- ✅ Superior reasoning quality (ToT + MCTS + Graph)
- ✅ Sovereign decisions (Axiom filtering)
- ✅ Scalable architecture (upgrade hardware, not code)

**Tomorrow's Reality:**
- 🚀 Faster hardware → Instant benefits
- 🚀 Larger models → Better reasoning
- 🚀 More RAM → Bigger graphs
- 🚀 Zero refactoring

---

## 8. Implementation Checklist

### Sprint 1 Ready?

**Before starting Sprint 1, verify:**

- [ ] DeepSeek-R1-14B installed and tested (VRAM <10GB)
- [ ] NetworkX performance validated (10k nodes <500ms queries)
- [ ] Vue dev environment working (Vite + Pinia)
- [ ] Resource monitoring working (psutil for RAM/VRAM)
- [ ] Config schemas defined (axiom, profile, model)

### Sprint 1 Success Criteria

**By end of Sprint 1 (12 days), must have:**

- [ ] Graph with 1000+ nodes running smoothly
- [ ] Model abstraction working (switch 8B ↔ 14B)
- [ ] Conflict detection functional (80%+ auto-resolution)
- [ ] Graph viewer showing nodes in Vue GUI
- [ ] Axiom editor working (CRUD operations)
- [ ] No system crashes (swap <1GB at all times)
- [ ] Profile switching works (MINIMAL ↔ STANDARD)

---

**Status:** Architecture finalized. Ready for implementation.

**Next:** Begin Sprint 1 Day 1 (Model Abstraction Layer).
