# Cluster 3: MCTS + Tiered RAG Integration - Implementation Plan

**Date:** 2026-01-16
**Status:** Planning Phase
**Goal:** Integrate Cluster 2 (Tiered RAG) with Cluster 1 (MCTS + XoT)

---

## Overview

**Cluster 3** bringt die Intelligence Layer (Cluster 2) mit dem MCTS Reasoning (Cluster 1) zusammen.

**Core Idea:**
> MCTS sollte **höher-qualitative Facts bevorzugen** bei der Node-Auswahl!

**Enhanced UCB1 Formula:**
```
UCB1 = exploitation + exploration + coverage_bonus + xot_prior + fact_quality_bonus
     = (value / visits)
       + C * sqrt(ln(parent_visits) / visits)
       + (1.0 - coverage_score) * coverage_weight
       + xot_prior * xot_weight
       + fact_quality_score * fact_weight      ← NEW!
```

Wo:
- `fact_quality_score`: 0.0-1.0 basierend auf Gold/Silver/Bronze facts
- `fact_weight`: Konfigurierbar (default: 0.15)

---

## Architecture

### Current State (Cluster 1 + 2)

```
ToT Expansion
    ↓
SPO Extraction ───────────┐
    ↓                     │
Multi-Source Verification │  Cluster 2
    ↓                     │  (Intelligence)
Tier Promotion            │
    ↓                     │
SPO Database ─────────────┘
(Bronze/Silver/Gold)

MCTS Selection ───────────┐
(UCB1 with XoT + Coverage)│  Cluster 1
    ↓                     │  (Reasoning)
Node Expansion            │
    ↓                     │
Value Propagation ────────┘
```

### Cluster 3 Integration

```
MCTS Selection
    ↓
Get Node Facts ───→ Query SPO Database ← Cluster 2
    ↓                   (Get Gold/Silver/Bronze)
Compute Fact Quality
    ↓
Enhanced UCB1 ────→ fact_quality_bonus ← NEW!
    ↓
Select Best Node (facts matter!)
    ↓
Expand & Extract SPO
    ↓
Tier Promotion ───→ Better facts for next iteration
```

---

## Components to Implement

### 1. FactQualityEvaluator ⏳

**File:** `src/core/fact_quality_evaluator.py`

**Purpose:** Calculate fact quality score for ToT nodes based on SPO triplets.

**Key Methods:**
```python
class FactQualityEvaluator:
    def __init__(self, graph_manager: GraphManager):
        self.graph = graph_manager

    def evaluate_node_facts(self, node_id: str) -> float:
        """
        Get quality score for all facts related to this node.

        Returns:
            0.0-1.0 score (0.0 = no facts, 1.0 = all Gold)
        """

    def get_node_fact_distribution(self, node_id: str) -> Dict:
        """
        Get breakdown of fact tiers for node.

        Returns:
            {"gold": 5, "silver": 10, "bronze": 20, "score": 0.65}
        """
```

**Scoring Algorithm:**
```python
# Weighted scoring
gold_weight = 1.0
silver_weight = 0.6
bronze_weight = 0.3

weighted_sum = (gold_count * gold_weight +
                silver_count * silver_weight +
                bronze_count * bronze_weight)

total_facts = gold_count + silver_count + bronze_count

fact_quality_score = weighted_sum / (total_facts * gold_weight) if total_facts > 0 else 0.0

# Example:
# 5 Gold + 10 Silver + 20 Bronze = 35 facts
# score = (5*1.0 + 10*0.6 + 20*0.3) / (35*1.0)
#       = (5 + 6 + 6) / 35
#       = 17 / 35
#       = 0.486 (~50%)
```

---

### 2. Enhanced MCTS UCB1 ⏳

**File:** `src/core/mcts_engine.py` (modify existing)

**Changes:**
```python
class MCTSEngine:
    def __init__(
        self,
        ...,
        fact_evaluator: Optional[FactQualityEvaluator] = None,  # NEW!
        fact_weight: float = 0.15  # NEW!
    ):
        self.fact_evaluator = fact_evaluator
        self.fact_weight = fact_weight
        self.fact_mode = fact_evaluator is not None

    def _compute_ucb1(self, node, parent) -> float:
        """
        Enhanced UCB1 with fact quality bonus.
        """
        # ... existing code ...

        # Fact quality bonus (NEW!)
        if self.fact_mode and self.fact_evaluator:
            fact_bonus = self._compute_fact_quality_bonus(node)
            ucb1 += fact_bonus * self.fact_weight

        return ucb1

    def _compute_fact_quality_bonus(self, node) -> float:
        """
        Compute bonus based on node's fact quality.

        Nodes with more Gold/Silver facts get higher priority!
        """
        try:
            fact_score = self.fact_evaluator.evaluate_node_facts(node.node_id)
            return fact_score  # 0.0-1.0
        except Exception as e:
            return 0.0  # Neutral if error
```

---

### 3. Adaptive Fact Weight ⏳

**Concept:** Weight should change based on exploration phase.

**Strategy:**
```python
# Early exploration (few facts extracted yet)
# → Low fact_weight (0.05) - explore broadly
if total_facts < 50:
    fact_weight = 0.05

# Mid exploration (building knowledge)
# → Medium fact_weight (0.15) - balanced
elif total_facts < 200:
    fact_weight = 0.15

# Late exploration (rich knowledge base)
# → High fact_weight (0.25) - exploit quality facts
else:
    fact_weight = 0.25
```

**Implementation:**
```python
class MCTSEngine:
    def _get_adaptive_fact_weight(self) -> float:
        """Get fact weight based on total facts in database."""
        if not self.fact_evaluator:
            return 0.0

        # Get total fact count
        stats = self.graph.get_spo_stats()
        total_facts = stats.get('total', 0)

        # Adaptive strategy
        if total_facts < 50:
            return 0.05  # Explore
        elif total_facts < 200:
            return 0.15  # Balance
        else:
            return 0.25  # Exploit quality
```

---

### 4. Fact-Guided Node Expansion ⏳

**Concept:** When expanding a node, use Gold/Silver facts as context.

**Current Expansion:**
```python
# In ToTManager.expand_node()
prompt = f"Question: {node.question}\nAnswer:"
response = llm.generate(prompt)
```

**Cluster 3 Enhancement:**
```python
# In ToTManager.expand_node()
# Get high-quality facts related to this node
gold_facts = get_related_facts(node, tier="gold")
silver_facts = get_related_facts(node, tier="silver")

# Build context from facts
context = format_facts_as_context(gold_facts + silver_facts)

# Enhanced prompt with fact context
prompt = f"""Context (verified facts):
{context}

Question: {node.question}

Use the context above to provide a well-grounded answer.

Answer:"""

response = llm.generate(prompt)
```

**Benefits:**
- Better quality answers (grounded in verified facts)
- More consistency across ToT branches
- Reinforcement learning (good facts → better answers → more good facts)

---

## Implementation Phases

### Sprint 1: Fact Quality Evaluator (2-3 days)

**Tasks:**
1. Create `FactQualityEvaluator` class
2. Implement `evaluate_node_facts()` method
3. Implement weighted scoring algorithm
4. Add caching for performance
5. Unit tests

**Success Criteria:**
- ✅ Can score any node based on its facts
- ✅ Score reflects Gold > Silver > Bronze priority
- ✅ Performance: <10ms per node evaluation

---

### Sprint 2: Enhanced MCTS UCB1 (2-3 days)

**Tasks:**
1. Modify `MCTSEngine.__init__()` to accept `FactQualityEvaluator`
2. Add `_compute_fact_quality_bonus()` method
3. Integrate into `_compute_ucb1()` formula
4. Add adaptive fact weight strategy
5. Integration tests with existing MCTS

**Success Criteria:**
- ✅ UCB1 score includes fact quality bonus
- ✅ Nodes with Gold facts rank higher
- ✅ Adaptive weighting works
- ✅ Existing MCTS tests still pass

---

### Sprint 3: Fact-Guided Expansion (3-4 days)

**Tasks:**
1. Add `get_related_facts()` method to GraphManager
2. Implement fact-to-context formatting
3. Modify `ToTManager.expand_node()` to use fact context
4. Add toggle for fact-guided mode (optional)
5. E2E integration test

**Success Criteria:**
- ✅ Node expansion uses Gold/Silver facts as context
- ✅ Answer quality improves (measurable)
- ✅ Can toggle on/off for comparison

---

### Sprint 4: Integration & Testing (2-3 days)

**Tasks:**
1. Full MCTS + Tiered RAG integration test
2. Performance benchmarking
3. Compare with/without Cluster 3
4. Documentation updates
5. Final validation

**Success Criteria:**
- ✅ All tests passing
- ✅ Demonstrable quality improvement
- ✅ Performance acceptable (<20% overhead)
- ✅ Documentation complete

---

## Success Metrics

### Quantitative Metrics

| Metric | Before Cluster 3 | Target After Cluster 3 |
|--------|------------------|------------------------|
| Avg UCB1 stability | Baseline | +15% |
| Gold facts per node | 0-2 | 3-5 |
| Answer consistency | Baseline | +25% |
| MCTS convergence speed | 100 iterations | 75 iterations |

### Qualitative Metrics

- ✅ Nodes with more Gold facts explored deeper
- ✅ High-quality branches prioritized
- ✅ Knowledge base quality improves over time
- ✅ MCTS "learns" to prefer verified information

---

## Integration Points

### With Cluster 1 (MCTS + XoT + Token Budget)

```python
# Full integration example
mcts = MCTSEngine(
    tot_manager=tot,
    graph_manager=graph,
    model_orchestrator=llm,

    # Cluster 1 features
    xot_simulator=xot,           # Prior estimation
    xot_weight=0.2,
    token_budget_manager=budget, # Budget tracking

    # Cluster 2 features (via graph_manager)
    # graph.spo_db has tiered facts

    # Cluster 3 features (NEW!)
    fact_evaluator=evaluator,    # Fact quality scoring
    fact_weight=0.15             # Adaptive weight
)
```

### With Cluster 2 (Intelligence Layer)

```python
# Cluster 2 runs during ToT expansion
tot.expand_node(node_id)
    ↓
SPO extraction
    ↓
Cross-verification (MultiSourceVerifier)
    ↓
Tier promotion (TierPromoter)
    ↓
SPO Database updated (Gold/Silver/Bronze)
    ↓
# Cluster 3 uses this in next MCTS iteration
mcts.iterate()
    ↓
Fact quality evaluation (FactQualityEvaluator)
    ↓
Enhanced UCB1 with fact bonus
    ↓
Better node selection!
```

---

## Testing Strategy

### Unit Tests

```
test_fact_quality_evaluator.py
  ✓ Evaluate node with Gold facts (score ~1.0)
  ✓ Evaluate node with Bronze facts (score ~0.3)
  ✓ Evaluate node with mixed facts (score ~0.5-0.7)
  ✓ Evaluate node with no facts (score 0.0)
  ✓ Caching works correctly
```

### Integration Tests

```
test_mcts_fact_quality.py
  ✓ MCTS with fact evaluator selects high-quality nodes
  ✓ Adaptive weight changes over time
  ✓ UCB1 formula correct with all bonuses
  ✓ Performance acceptable (<20% overhead)
```

### E2E Tests

```
test_cluster3_e2e.py
  ✓ Full workflow: ToT → SPO → Tier Promotion → MCTS → Fact-guided
  ✓ Quality improves over iterations
  ✓ Gold facts accumulate
  ✓ MCTS converges faster with fact guidance
```

---

## Performance Considerations

### Caching Strategy

```python
class FactQualityEvaluator:
    def __init__(self):
        self._cache = {}  # node_id -> (score, timestamp)
        self._cache_ttl = 60  # seconds

    def evaluate_node_facts(self, node_id: str) -> float:
        # Check cache first
        if node_id in self._cache:
            score, ts = self._cache[node_id]
            if time.time() - ts < self._cache_ttl:
                return score  # Cache hit!

        # Calculate and cache
        score = self._calculate_score(node_id)
        self._cache[node_id] = (score, time.time())
        return score
```

### Database Optimization

```sql
-- Index for fast fact lookup by source
CREATE INDEX idx_spo_source ON spo_triplets(source_id);

-- Index for tier filtering
CREATE INDEX idx_spo_tier ON spo_triplets(tier);
```

---

## Risks & Mitigation

### Risk 1: Over-Exploitation of Gold Facts
**Problem:** MCTS might only explore nodes with existing Gold facts.
**Mitigation:** Keep fact_weight moderate (0.15), adaptive strategy ensures exploration phase.

### Risk 2: Performance Overhead
**Problem:** Fact evaluation on every UCB1 calculation might be slow.
**Mitigation:** Aggressive caching, database indexes, can toggle off if needed.

### Risk 3: Cold Start Problem
**Problem:** Early iterations have no Gold facts yet.
**Mitigation:** Adaptive weighting (low weight early), XoT prior still works.

---

## Next Steps

1. **Review Plan** - Validate approach
2. **Sprint 1** - Implement FactQualityEvaluator
3. **Sprint 2** - Enhance MCTS UCB1
4. **Sprint 3** - Fact-guided expansion
5. **Sprint 4** - Integration & testing

**Estimated Time:** 9-13 days total

---

## Success Definition

**Cluster 3 is complete when:**
- ✅ FactQualityEvaluator implemented and tested
- ✅ MCTS uses fact quality in UCB1
- ✅ Adaptive weighting works
- ✅ Fact-guided node expansion implemented
- ✅ All integration tests passing
- ✅ Demonstrable quality improvement
- ✅ Documentation complete

---

*Plan created: 2026-01-16*
*Target: Cluster 3 Complete*
