# Cluster 2 Implementation Plan: Intelligence Layer

**Status:** Planning Phase
**Date:** 2026-01-15
**Dependencies:** Cluster 1 Complete ✅

---

## Overview

Cluster 2 baut auf der Cluster 1 Foundation auf und fügt Intelligence hinzu:
- **Multi-Source Verification** für SPO Triplets
- **Tiered RAG** mit automatischer Promotion
- **Conflict Resolution** bei widersprüchlichen Facts
- **Axiom Judge** für LLM-basierte Axiom-Bewertung

---

## Architecture

```
SPO Triplet (Bronze)
    ↓
Multi-Source Verifier
    ├─→ Verify with 2+ sources
    └─→ If verified: Promote to Silver
         ↓
    Conflict Detection
         ├─→ Check for contradictions
         └─→ If conflict: ConflictResolver
              ├─→ Confidence-based resolution
              └─→ Keep higher confidence
         ↓
    Axiom Judge (optional)
         ├─→ LLM evaluates against axioms
         └─→ If passes: Promote to Gold
```

---

## Components

### 1. MultiSourceVerifier (`src/core/multi_source_verifier.py`)

**Purpose:** Verify SPO triplets across multiple sources

**Interface:**
```python
class MultiSourceVerifier:
    def __init__(self, graph_manager: GraphManager):
        self.graph = graph_manager
        self.min_sources = 2  # Minimum sources for Silver promotion

    def verify_triplet(
        self,
        triplet_id: str,
        new_source: str
    ) -> VerificationResult:
        """
        Verify triplet with new source.

        Returns:
            VerificationResult with:
            - verified: bool
            - source_count: int
            - should_promote: bool (if >= min_sources)
        """
        pass

    def find_similar_triplets(
        self,
        triplet: SPOTriplet,
        similarity_threshold: float = 0.8
    ) -> List[SPOTriplet]:
        """
        Find semantically similar triplets.
        Uses subject/predicate/object similarity.
        """
        pass
```

**Key Methods:**
- `verify_triplet()` - Add verification source
- `find_similar_triplets()` - Semantic similarity search
- `get_verification_stats()` - Stats per triplet

**Promotion Logic:**
- 1 source = Bronze
- 2+ sources = Silver
- 3+ sources + Axiom pass = Gold

---

### 2. TierPromoter (`src/core/tier_promoter.py`)

**Purpose:** Automatic promotion Bronze → Silver → Gold

**Interface:**
```python
class TierPromoter:
    def __init__(
        self,
        graph_manager: GraphManager,
        verifier: MultiSourceVerifier,
        axiom_judge: Optional[AxiomJudge] = None
    ):
        self.graph = graph_manager
        self.verifier = verifier
        self.axiom_judge = axiom_judge

    def promote_if_eligible(self, triplet_id: str) -> bool:
        """
        Check and promote triplet if eligible.

        Bronze → Silver: 2+ verified sources
        Silver → Gold: 3+ sources + axiom pass
        """
        pass

    def auto_promote_batch(self, triplet_ids: List[str]) -> Dict:
        """
        Batch promotion with stats.
        """
        pass
```

**Promotion Rules:**
```python
PROMOTION_RULES = {
    "bronze_to_silver": {
        "min_sources": 2,
        "min_confidence": 0.7
    },
    "silver_to_gold": {
        "min_sources": 3,
        "min_confidence": 0.85,
        "requires_axiom_pass": True
    }
}
```

---

### 3. ConflictResolver (`src/core/conflict_resolver.py`)

**Purpose:** Detect and resolve contradicting triplets

**Interface:**
```python
class ConflictResolver:
    def __init__(self, graph_manager: GraphManager):
        self.graph = graph_manager

    def detect_conflicts(
        self,
        triplet: SPOTriplet
    ) -> List[Conflict]:
        """
        Detect contradictions with existing triplets.

        Example conflicts:
        - [Solar] --cost--> [high] vs [Solar] --cost--> [low]
        - [X] --is--> [Y] vs [X] --is_not--> [Y]
        """
        pass

    def resolve_conflict(
        self,
        conflict: Conflict,
        strategy: str = "confidence"
    ) -> Resolution:
        """
        Resolve conflict using strategy:
        - "confidence": Keep higher confidence
        - "sources": Keep more sources
        - "recency": Keep newer
        - "manual": Flag for human review
        """
        pass
```

**Conflict Detection:**
- Same subject + predicate, different object
- Negation predicates (is vs is_not)
- Semantic opposites (high vs low, yes vs no)

**Resolution Strategies:**
1. **Confidence-based:** Keep higher confidence triplet
2. **Source-based:** Keep triplet with more sources
3. **Recency-based:** Keep newer triplet
4. **Manual:** Flag for human review

---

### 4. AxiomJudge (`src/core/axiom_judge.py`)

**Purpose:** LLM-based evaluation of triplets against axioms

**Interface:**
```python
class AxiomJudge:
    def __init__(
        self,
        model_orchestrator: ModelOrchestrator,
        axiom_manager: AxiomManager
    ):
        self.llm = model_orchestrator
        self.axioms = axiom_manager

    def evaluate_triplet(
        self,
        triplet: SPOTriplet,
        relevant_axioms: List[Axiom]
    ) -> JudgmentResult:
        """
        Evaluate triplet against axioms using LLM.

        Returns:
            JudgmentResult with:
            - passes: bool
            - axiom_scores: Dict[axiom_id, float]
            - reasoning: str (LLM explanation)
        """
        pass

    def batch_evaluate(
        self,
        triplets: List[SPOTriplet]
    ) -> List[JudgmentResult]:
        """
        Batch evaluation for efficiency.
        """
        pass
```

**Evaluation Prompt:**
```python
AXIOM_EVAL_PROMPT = """Evaluate if this fact aligns with our values.

Fact: [{subject}] --{predicate}--> [{object}]
Confidence: {confidence}

Values to check:
{axioms_list}

Does this fact violate any values?
Respond: YES/NO and explain briefly.
"""
```

---

## Implementation Order

### Phase 1: Multi-Source Verification (Week 1)

**Sprint 1.1: MultiSourceVerifier Core**
- [ ] Create `multi_source_verifier.py`
- [ ] Implement `verify_triplet()`
- [ ] Implement `find_similar_triplets()`
- [ ] Unit tests

**Sprint 1.2: TierPromoter**
- [ ] Create `tier_promoter.py`
- [ ] Implement `promote_if_eligible()`
- [ ] Implement promotion rules
- [ ] Integration with SPODatabase

**Sprint 1.3: Integration Test**
- [ ] Create test: Bronze → Silver promotion
- [ ] Verify 2+ sources triggers promotion
- [ ] Check database tier updated

---

### Phase 2: Conflict Resolution (Week 2)

**Sprint 2.1: Conflict Detection**
- [ ] Create `conflict_resolver.py`
- [ ] Implement `detect_conflicts()`
- [ ] Semantic conflict detection
- [ ] Unit tests

**Sprint 2.2: Resolution Strategies**
- [ ] Implement confidence-based resolution
- [ ] Implement source-based resolution
- [ ] Conflict logging
- [ ] Integration tests

---

### Phase 3: Axiom Judge (Week 2-3)

**Sprint 3.1: AxiomJudge Core**
- [ ] Create `axiom_judge.py`
- [ ] Implement `evaluate_triplet()`
- [ ] LLM prompt engineering
- [ ] Unit tests

**Sprint 3.2: Gold Promotion**
- [ ] Integrate AxiomJudge with TierPromoter
- [ ] Silver → Gold promotion logic
- [ ] End-to-end test

---

## Data Models

### VerificationResult
```python
@dataclass
class VerificationResult:
    triplet_id: str
    verified: bool
    source_count: int
    verification_sources: List[str]
    should_promote: bool
    similarity_scores: Dict[str, float]
```

### Conflict
```python
@dataclass
class Conflict:
    triplet_a: SPOTriplet
    triplet_b: SPOTriplet
    conflict_type: str  # "contradiction", "semantic_opposite", "negation"
    severity: float  # 0.0-1.0
    detected_at: str
```

### Resolution
```python
@dataclass
class Resolution:
    conflict: Conflict
    strategy_used: str
    kept_triplet_id: str
    removed_triplet_id: Optional[str]
    reasoning: str
    resolved_at: str
```

### JudgmentResult
```python
@dataclass
class JudgmentResult:
    triplet_id: str
    passes: bool
    axiom_scores: Dict[str, float]  # axiom_id -> score
    reasoning: str
    evaluated_at: str
```

---

## Database Changes

### New Table: verification_sources
```sql
CREATE TABLE verification_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    triplet_id TEXT NOT NULL,
    source_id TEXT NOT NULL,
    verified_at TEXT NOT NULL,
    confidence_delta REAL,  -- How much confidence changed
    FOREIGN KEY (triplet_id) REFERENCES spo_triplets(id)
);

CREATE INDEX idx_verification_triplet ON verification_sources(triplet_id);
```

### New Table: conflicts
```sql
CREATE TABLE conflicts (
    id TEXT PRIMARY KEY,
    triplet_a_id TEXT NOT NULL,
    triplet_b_id TEXT NOT NULL,
    conflict_type TEXT NOT NULL,
    severity REAL NOT NULL,
    status TEXT DEFAULT 'unresolved',  -- unresolved, resolved, flagged
    resolution_json TEXT,
    detected_at TEXT NOT NULL,
    resolved_at TEXT,
    FOREIGN KEY (triplet_a_id) REFERENCES spo_triplets(id),
    FOREIGN KEY (triplet_b_id) REFERENCES spo_triplets(id)
);
```

### New Table: axiom_judgments
```sql
CREATE TABLE axiom_judgments (
    id TEXT PRIMARY KEY,
    triplet_id TEXT NOT NULL,
    passes BOOLEAN NOT NULL,
    axiom_scores_json TEXT NOT NULL,
    reasoning TEXT,
    evaluated_at TEXT NOT NULL,
    FOREIGN KEY (triplet_id) REFERENCES spo_triplets(id)
);
```

---

## Integration Points

### With Cluster 1

**ToTManager Integration:**
```python
# In expand_node(), after SPO extraction:
spo_triplet_ids = self._extract_spo_triplets(node, response)

# NEW: Trigger verification (if previous node had same fact)
if self.tier_promoter:
    for triplet_id in spo_triplet_ids:
        self.tier_promoter.promote_if_eligible(triplet_id)
```

**GraphManager Extension:**
```python
# Add to GraphManager:
def verify_triplet(
    self,
    triplet_id: str,
    verification_source: str
) -> bool:
    """Verify triplet with new source, maybe promote tier."""
    if not self.multi_source_verifier:
        return False

    result = self.multi_source_verifier.verify_triplet(
        triplet_id, verification_source
    )

    if result.should_promote:
        self.tier_promoter.promote_if_eligible(triplet_id)

    return result.verified
```

---

## Testing Strategy

### Unit Tests
- `test_multi_source_verifier.py`
- `test_tier_promoter.py`
- `test_conflict_resolver.py`
- `test_axiom_judge.py`

### Integration Tests
```python
def test_tier_promotion_flow():
    """Test Bronze → Silver → Gold flow"""
    # 1. Create Bronze triplet
    # 2. Add 2nd source → Should promote to Silver
    # 3. Add 3rd source + axiom pass → Should promote to Gold
    pass

def test_conflict_resolution():
    """Test conflict detection and resolution"""
    # 1. Create triplet A
    # 2. Create contradicting triplet B
    # 3. Conflict should be detected
    # 4. Higher confidence triplet should win
    pass
```

---

## Success Criteria

| Component | Criterion | Target |
|-----------|-----------|--------|
| Multi-Source Verifier | Detects similar triplets | >80% accuracy |
| Tier Promotion | Bronze → Silver | Automatic with 2+ sources |
| Tier Promotion | Silver → Gold | Automatic with 3+ sources + axiom |
| Conflict Detection | Finds contradictions | >90% recall |
| Conflict Resolution | Resolves correctly | >85% accuracy |
| Axiom Judge | LLM evaluation | <5s per triplet |

---

## Next Steps

1. **Start with MultiSourceVerifier** (most foundational)
2. **Then TierPromoter** (uses verifier)
3. **Then ConflictResolver** (independent)
4. **Finally AxiomJudge** (most complex)

---

**Ready to start implementation?**
→ Begin with `MultiSourceVerifier` in Sprint 1.1

*Document created: 2026-01-15*
