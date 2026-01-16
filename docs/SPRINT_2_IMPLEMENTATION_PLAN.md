# Sprint 2: Intelligence Layer - Implementation Plan

**Status:** IN PROGRESS
**Date:** 2026-01-16
**Goal:** Generative CoT + Process Reward Model
**Estimated Time:** 6-7 days

---

## 📋 Gemini's Original Sprint 2 Definition

**From:** `docs/concepts/SRO_ARCHITECTURE_OVERVIEW.md`

```markdown
### Sprint 2: Intelligence Layer (Woche 3-4)
□ Generative CoT Integration
□ Process Reward Model (PRM)
□ XoT Simulator
□ Multi-variant Selection
```

**Current Status:**
- ✅ XoT Simulator (implemented)
- ❌ Generative CoT Integration (MISSING!)
- ❌ Process Reward Model (MISSING!)
- ❌ Multi-variant Selection (MISSING!)

---

## 🎯 Sprint 2 Core Concept

### The Problem We're Solving

**Current State:**
```python
# ToT expansion currently generates 1 answer:
tot.expand_node(node_id)
  → LLM generates 1 answer
  → Store in node
  → Continue
```

**Gemini's Vision:**
```python
# Sprint 2: Generate 3 CoT variants per node!
tot.expand_node(node_id)
  → CoTGenerator generates 3 reasoning chains:
      - Variant A: Analytical approach
      - Variant B: Empirical approach
      - Variant C: Theoretical approach
  → Process Reward Model scores each step of each variant
  → Best variant selected
  → Store in node
```

**Why 3 variants?**
- More exploration of reasoning space
- Better coverage of solution approaches
- Step-wise verification catches errors early
- MCTS can compare different reasoning paths

---

## 📚 Research Foundation

### Gemini's Concept Documents

**1. XOT_GENERATIVE_COT_CONCEPT.md**
- XoT as "Vor-Denker" (thought simulation)
- Generative CoT with Process Reward Modeling (PRM)
- Step-wise verification
- RLAIF (Reinforcement Learning from AI Feedback)

**Key Quote:**
> "Generate 3 alternative reasoning chains per MCTS node.
> Use Process Reward Model to score each step.
> Select best variant based on combined score."

**2. OpenAI o1 Research (2024)**
- Reasoning models use test-time compute scaling
- Multiple reasoning paths improve quality
- Step-by-step verification essential

**3. Anthropic Constitutional AI (2022)**
- RLAIF: AI evaluates AI outputs
- Principle-based scoring
- Self-improvement loop

---

## 🏗️ Architecture

### Component Overview

```
ToT Node Expansion
    ↓
CoTGenerator (NEW!)
    ↓
Generate 3 CoT Variants
    ├─── Variant A (analytical)
    ├─── Variant B (empirical)
    └─── Variant C (theoretical)
    ↓
Process Reward Model (NEW!)
    ↓
Score Each Step (0.0-1.0)
    ├─── Step 1: Check against axioms
    ├─── Step 2: Verify logical consistency
    └─── Step 3: Validate conclusions
    ↓
Multi-variant Selection (NEW!)
    ↓
Select Best Variant
    ↓
Store Best Answer in ToT Node
    ↓
Continue MCTS
```

---

## 📦 Components to Implement

### 1. CoTGenerator ⏳

**File:** `src/core/cot_generator.py`

**Purpose:** Generate multiple reasoning chain variants per ToT node.

**Class Definition:**
```python
from typing import List, Optional
from dataclasses import dataclass
from src.models.unified_session import UnifiedSession
from src.core.model_orchestrator import ModelOrchestrator


@dataclass
class CoTVariant:
    """A single Chain-of-Thought reasoning variant."""
    variant_id: str              # e.g., "variant_a"
    approach: str                # e.g., "analytical"
    steps: List[str]             # Reasoning steps
    conclusion: str              # Final answer
    raw_response: str            # Full LLM response
    confidence: float            # Self-reported confidence


class CoTGenerator:
    """
    Generate multiple reasoning chain variants for a given question.

    Inspired by:
    - OpenAI o1 (test-time compute scaling)
    - DeepMind Self-Echoing Search
    - Gemini's XoT concept

    Usage:
        generator = CoTGenerator(model_orchestrator, variant_count=3)
        variants = generator.generate_variants(
            question="What are the benefits of renewable energy?",
            parent_context="Previous reasoning..."
        )
        # Returns 3 CoT variants with different approaches
    """

    def __init__(
        self,
        model_orchestrator: ModelOrchestrator,
        variant_count: int = 3,
        enable_diversity: bool = True
    ):
        """
        Initialize CoT Generator.

        Args:
            model_orchestrator: LLM provider
            variant_count: Number of variants to generate (default: 3)
            enable_diversity: Use diversity sampling (default: True)
        """
        self.model = model_orchestrator
        self.variant_count = variant_count
        self.enable_diversity = enable_diversity

        # Approach templates
        self.approaches = [
            {
                "id": "analytical",
                "name": "Analytical Approach",
                "instruction": "Break down the problem logically step-by-step using deductive reasoning."
            },
            {
                "id": "empirical",
                "name": "Empirical Approach",
                "instruction": "Use real-world examples and empirical evidence to build your answer."
            },
            {
                "id": "theoretical",
                "name": "Theoretical Approach",
                "instruction": "Apply relevant theoretical frameworks and first principles."
            }
        ]

    def generate_variants(
        self,
        question: str,
        parent_context: Optional[str] = None,
        session: Optional[UnifiedSession] = None
    ) -> List[CoTVariant]:
        """
        Generate multiple CoT reasoning variants.

        Args:
            question: Question to answer
            parent_context: Context from parent node (optional)
            session: Current research session (optional)

        Returns:
            List of CoTVariant objects (length = variant_count)

        Example:
            variants = generator.generate_variants(
                question="What are key challenges in solar adoption?",
                parent_context="Benefits include reduced emissions..."
            )

            # variants[0]: Analytical approach (policy analysis)
            # variants[1]: Empirical approach (case studies)
            # variants[2]: Theoretical approach (economics theory)
        """
        variants = []

        for i, approach in enumerate(self.approaches[:self.variant_count]):
            # Build prompt for this variant
            prompt = self._build_variant_prompt(
                question=question,
                approach=approach,
                parent_context=parent_context
            )

            # Generate with diversity sampling if enabled
            response = self._generate_with_diversity(
                prompt=prompt,
                temperature=0.7 if self.enable_diversity else 0.2,
                variant_index=i
            )

            # Parse into CoTVariant
            variant = self._parse_response(
                response=response,
                approach=approach,
                variant_index=i
            )

            variants.append(variant)

        return variants

    def _build_variant_prompt(
        self,
        question: str,
        approach: dict,
        parent_context: Optional[str]
    ) -> str:
        """Build prompt for specific variant approach."""

        base_prompt = f"""You are answering the following question using a {approach['name']}.

Question: {question}
"""

        if parent_context:
            base_prompt += f"""
Previous Context:
{parent_context}
"""

        base_prompt += f"""
Instruction: {approach['instruction']}

Please provide your answer with clear reasoning steps:
1. First, state your approach
2. Break down your reasoning step-by-step
3. Provide your conclusion
4. Rate your confidence (0.0-1.0)

Answer:"""

        return base_prompt

    def _generate_with_diversity(
        self,
        prompt: str,
        temperature: float,
        variant_index: int
    ) -> str:
        """Generate response with diversity sampling."""

        response = self.model.generate(
            prompt=prompt,
            max_tokens=1024,
            temperature=temperature,
            stop=["Question:", "---"]
        )

        return response

    def _parse_response(
        self,
        response: str,
        approach: dict,
        variant_index: int
    ) -> CoTVariant:
        """Parse LLM response into CoTVariant structure."""

        # Simple parsing (can be enhanced with structured extraction)
        lines = response.strip().split("\n")

        # Extract steps (lines that start with numbers or bullets)
        steps = [
            line.strip() for line in lines
            if line.strip() and (
                line.strip()[0].isdigit() or
                line.strip().startswith("-") or
                line.strip().startswith("•")
            )
        ]

        # Extract conclusion (last non-empty line or explicit "Conclusion:" section)
        conclusion = ""
        for line in reversed(lines):
            if line.strip():
                conclusion = line.strip()
                break

        # Extract confidence (look for patterns like "Confidence: 0.8")
        confidence = 0.7  # Default
        for line in lines:
            if "confidence" in line.lower():
                try:
                    # Extract number from line
                    import re
                    match = re.search(r'(\d+\.?\d*)', line)
                    if match:
                        confidence = float(match.group(1))
                        if confidence > 1.0:
                            confidence /= 100  # Handle percentage format
                except:
                    pass

        return CoTVariant(
            variant_id=f"variant_{chr(97 + variant_index)}",  # a, b, c
            approach=approach['id'],
            steps=steps,
            conclusion=conclusion,
            raw_response=response,
            confidence=confidence
        )
```

**Test Cases:**
```python
# test_cot_generator.py

def test_generate_variants():
    """Test generating 3 CoT variants."""
    generator = CoTGenerator(model_orchestrator, variant_count=3)

    variants = generator.generate_variants(
        question="What are the benefits of renewable energy?"
    )

    assert len(variants) == 3
    assert variants[0].approach == "analytical"
    assert variants[1].approach == "empirical"
    assert variants[2].approach == "theoretical"

    # Each variant should have steps
    for variant in variants:
        assert len(variant.steps) > 0
        assert variant.conclusion
        assert 0.0 <= variant.confidence <= 1.0
```

---

### 2. ProcessRewardModel ⏳

**File:** `src/core/process_reward_model.py`

**Purpose:** Score each reasoning step against axioms and logical consistency.

**Class Definition:**
```python
from typing import List, Dict, Optional
from dataclasses import dataclass
from src.core.axiom_manager import AxiomManager
from src.core.model_orchestrator import ModelOrchestrator


@dataclass
class StepScore:
    """Score for a single reasoning step."""
    step_text: str
    axiom_compliance: float      # 0.0-1.0: Compliance with axioms
    logical_consistency: float   # 0.0-1.0: Internal logic
    evidence_strength: float     # 0.0-1.0: Supporting evidence
    overall_score: float         # 0.0-1.0: Weighted average
    violations: List[str]        # Axiom violations detected


class ProcessRewardModel:
    """
    Process Reward Model - Score reasoning steps.

    Inspired by:
    - OpenAI Process Reward Models (2023)
    - Anthropic Constitutional AI (RLAIF)
    - Gemini's XoT step-wise verification

    Usage:
        prm = ProcessRewardModel(axiom_manager, model_orchestrator)

        # Score single step
        score = prm.score_step(
            step="Solar panels reduce carbon emissions",
            context="Discussing renewable energy benefits"
        )
        # score.overall_score: 0.85

        # Score entire CoT variant
        variant_score = prm.score_variant(cot_variant)
        # variant_score.avg_score: 0.78
    """

    def __init__(
        self,
        axiom_manager: Optional[AxiomManager],
        model_orchestrator: ModelOrchestrator,
        enable_llm_scoring: bool = True
    ):
        """
        Initialize Process Reward Model.

        Args:
            axiom_manager: Axiom library for compliance checking
            model_orchestrator: LLM for logical consistency checking
            enable_llm_scoring: Use LLM for scoring (vs rule-based)
        """
        self.axioms = axiom_manager
        self.model = model_orchestrator
        self.enable_llm = enable_llm_scoring

    def score_step(
        self,
        step: str,
        context: Optional[str] = None
    ) -> StepScore:
        """
        Score a single reasoning step.

        Args:
            step: Reasoning step text
            context: Optional context for evaluation

        Returns:
            StepScore with detailed breakdown
        """
        # 1. Check axiom compliance
        axiom_score, violations = self._check_axiom_compliance(step)

        # 2. Check logical consistency
        logic_score = self._check_logical_consistency(step, context)

        # 3. Check evidence strength
        evidence_score = self._check_evidence_strength(step)

        # 4. Weighted average
        overall = (
            axiom_score * 0.4 +
            logic_score * 0.4 +
            evidence_score * 0.2
        )

        return StepScore(
            step_text=step,
            axiom_compliance=axiom_score,
            logical_consistency=logic_score,
            evidence_strength=evidence_score,
            overall_score=overall,
            violations=violations
        )

    def score_variant(self, variant: 'CoTVariant') -> Dict:
        """
        Score entire CoT variant.

        Returns:
            {
                "step_scores": List[StepScore],
                "avg_score": float,
                "min_score": float,
                "violations_count": int
            }
        """
        step_scores = []

        for step in variant.steps:
            score = self.score_step(step)
            step_scores.append(score)

        if not step_scores:
            return {
                "step_scores": [],
                "avg_score": 0.0,
                "min_score": 0.0,
                "violations_count": 0
            }

        avg_score = sum(s.overall_score for s in step_scores) / len(step_scores)
        min_score = min(s.overall_score for s in step_scores)
        violations_count = sum(len(s.violations) for s in step_scores)

        return {
            "step_scores": step_scores,
            "avg_score": avg_score,
            "min_score": min_score,
            "violations_count": violations_count
        }

    def _check_axiom_compliance(self, step: str) -> tuple[float, List[str]]:
        """Check if step complies with axioms."""
        if not self.axioms:
            return 1.0, []  # No axioms = always compliant

        # Get all axioms
        axioms = self.axioms.get_all_axioms()

        if not axioms:
            return 1.0, []

        # Check each axiom
        violations = []
        compliance_scores = []

        for axiom in axioms:
            # Simple keyword matching (can be enhanced with LLM)
            violates = self._check_single_axiom(step, axiom)

            if violates:
                violations.append(f"Violates: {axiom.name}")
                compliance_scores.append(0.0)
            else:
                compliance_scores.append(1.0)

        # Average compliance
        avg_compliance = sum(compliance_scores) / len(compliance_scores) if compliance_scores else 1.0

        return avg_compliance, violations

    def _check_single_axiom(self, step: str, axiom) -> bool:
        """Check if step violates a single axiom."""
        # Simplified check - can be enhanced with LLM-based verification
        step_lower = step.lower()

        # Check negative examples (violations)
        for negative_example in axiom.negative_examples:
            if negative_example.lower() in step_lower:
                return True  # Violation detected

        return False  # No violation

    def _check_logical_consistency(
        self,
        step: str,
        context: Optional[str]
    ) -> float:
        """Check logical consistency of step."""
        if not self.enable_llm:
            return 0.7  # Default score

        # Use LLM to check consistency
        prompt = f"""Evaluate the logical consistency of this reasoning step.

Step: {step}
"""
        if context:
            prompt += f"""Context: {context}
"""

        prompt += """
Is this step logically sound? Rate from 0.0 (illogical) to 1.0 (perfectly logical).

Score (0.0-1.0):"""

        try:
            response = self.model.generate(
                prompt=prompt,
                max_tokens=10,
                temperature=0.1
            )

            # Extract score
            import re
            match = re.search(r'(\d+\.?\d*)', response)
            if match:
                score = float(match.group(1))
                if score > 1.0:
                    score /= 100
                return min(1.0, max(0.0, score))
        except:
            pass

        return 0.7  # Default on error

    def _check_evidence_strength(self, step: str) -> float:
        """Check if step provides strong evidence."""
        # Simple heuristic (can be enhanced)
        evidence_indicators = [
            "research shows",
            "studies indicate",
            "data suggests",
            "evidence demonstrates",
            "according to",
            "statistics show",
            "analysis reveals"
        ]

        step_lower = step.lower()

        # Count evidence indicators
        count = sum(1 for indicator in evidence_indicators if indicator in step_lower)

        # Normalize to 0.0-1.0
        score = min(1.0, count * 0.3 + 0.3)  # Base 0.3, +0.3 per indicator

        return score
```

---

### 3. Multi-variant Selection ⏳

**Integration Point:** `src/core/tot_manager.py`

**Changes to ToTManager:**

```python
# In ToTManager class

def __init__(
    self,
    graph_manager: GraphManager,
    axiom_manager: Optional[AxiomManager],
    model_orchestrator: ModelOrchestrator,
    enable_intelligence: bool = True,
    enable_generative_cot: bool = True,  # NEW!
    cot_variant_count: int = 3            # NEW!
):
    # ... existing code ...

    # Sprint 2: Generative CoT (NEW!)
    self.enable_generative_cot = enable_generative_cot
    if enable_generative_cot:
        from src.core.cot_generator import CoTGenerator
        from src.core.process_reward_model import ProcessRewardModel

        self.cot_generator = CoTGenerator(
            model_orchestrator=model_orchestrator,
            variant_count=cot_variant_count
        )

        self.prm = ProcessRewardModel(
            axiom_manager=axiom_manager,
            model_orchestrator=model_orchestrator
        )
    else:
        self.cot_generator = None
        self.prm = None


def expand_node(self, node_id: str) -> bool:
    """
    Expand ToT node with answer.

    Sprint 2 Enhancement:
    - If enable_generative_cot=True:
      → Generate 3 CoT variants
      → Score each variant with PRM
      → Select best variant
    - Else:
      → Single answer (legacy behavior)
    """
    node = self.graph.get_node(node_id)
    if not node or node.answer:
        return False

    # Sprint 2: Multi-variant generation
    if self.enable_generative_cot and self.cot_generator:
        return self._expand_node_generative_cot(node)
    else:
        return self._expand_node_single(node)  # Legacy


def _expand_node_generative_cot(self, node) -> bool:
    """
    Sprint 2: Expand node with 3 CoT variants.
    """
    print(f"\n[Sprint 2] Generating 3 CoT variants for: {node.question[:60]}...")

    # 1. Generate 3 variants
    variants = self.cot_generator.generate_variants(
        question=node.question,
        parent_context=node.parent_context if hasattr(node, 'parent_context') else None
    )

    print(f"✓ Generated {len(variants)} variants")

    # 2. Score each variant with PRM
    variant_scores = []
    for i, variant in enumerate(variants):
        score_result = self.prm.score_variant(variant)
        variant_scores.append({
            "variant": variant,
            "score": score_result['avg_score'],
            "details": score_result
        })
        print(f"  - Variant {chr(97+i).upper()} ({variant.approach}): score={score_result['avg_score']:.3f}")

    # 3. Select best variant
    best = max(variant_scores, key=lambda x: x['score'])
    best_variant = best['variant']

    print(f"✓ Selected best: Variant {best_variant.variant_id[-1].upper()} (score={best['score']:.3f})")

    # 4. Store best answer in node
    node.answer = best_variant.conclusion
    node.reasoning_steps = best_variant.steps  # NEW field!
    node.confidence = best_variant.confidence
    node.cot_variants = variants  # NEW field! Store all variants
    node.selected_variant = best_variant.variant_id

    # 5. Extract SPO from best answer (existing Cluster 1 code)
    self._extract_spo_from_answer(node.node_id, node.answer)

    # 6. Apply intelligence layer (existing Cluster 2 code)
    if self.enable_intelligence:
        # Cross-verification and tier promotion
        pass

    return True
```

---

## 🧪 Testing Strategy

### Unit Tests

**1. test_cot_generator.py**
```python
def test_generate_3_variants():
    """Test generating 3 CoT variants."""

def test_variant_diversity():
    """Test that variants have different approaches."""

def test_parse_reasoning_steps():
    """Test parsing steps from LLM response."""
```

**2. test_process_reward_model.py**
```python
def test_score_step():
    """Test scoring a single step."""

def test_axiom_compliance():
    """Test axiom violation detection."""

def test_score_entire_variant():
    """Test scoring complete CoT variant."""
```

### Integration Tests

**3. test_sprint2_integration.py**
```python
def test_expand_node_with_generative_cot():
    """
    Test full Sprint 2 workflow:
    1. Create ToT node
    2. Expand with 3 variants
    3. PRM scores each
    4. Best variant selected
    5. SPO extraction works
    """

    tot = ToTManager(
        graph_manager=graph,
        axiom_manager=axioms,
        model_orchestrator=llm,
        enable_generative_cot=True,  # Sprint 2!
        cot_variant_count=3
    )

    # Create root question
    root_id = tot.create_root("What are the benefits of renewable energy?")

    # Decompose
    child_ids = tot.decompose_question(root_id, branching_factor=1)

    # Expand with Sprint 2
    success = tot.expand_node(child_ids[0])

    assert success

    # Check node has variants
    node = tot.graph.get_node(child_ids[0])
    assert hasattr(node, 'cot_variants')
    assert len(node.cot_variants) == 3
    assert hasattr(node, 'selected_variant')

    # Check variants have different approaches
    approaches = [v.approach for v in node.cot_variants]
    assert "analytical" in approaches
    assert "empirical" in approaches
    assert "theoretical" in approaches

    # Check best variant was selected
    assert node.answer == best_variant.conclusion
```

---

## 📊 Success Criteria

### Sprint 2 is COMPLETE when:

- [⏳] CoTGenerator implemented and tested
  - Can generate 3 variants per question
  - Variants have different approaches (analytical, empirical, theoretical)
  - Each variant has clear reasoning steps

- [⏳] ProcessRewardModel implemented and tested
  - Can score individual steps (0.0-1.0)
  - Checks axiom compliance
  - Checks logical consistency
  - Can score entire CoT variant

- [⏳] Multi-variant selection integrated
  - ToTManager.expand_node() generates 3 variants
  - PRM scores each variant
  - Best variant selected based on score
  - All variants stored for analysis

- [⏳] Integration tests passing
  - Full workflow works end-to-end
  - SPO extraction still works (Cluster 1)
  - Intelligence layer still works (Cluster 2)
  - No regressions

- [⏳] Documentation complete
  - SPRINT_2_COMPLETE.md status document
  - Code comments and docstrings
  - Usage examples

---

## 📈 Expected Benefits

### Quantitative:
- **Better reasoning quality:** 3 approaches vs 1 → +40% answer quality
- **Error detection:** Step-wise verification catches logical errors
- **Exploration coverage:** More diverse reasoning paths explored

### Qualitative:
- MCTS explores different reasoning strategies
- Process Reward Model provides fine-grained feedback
- System "learns" which approaches work best
- Aligns with OpenAI o1 test-time compute scaling

---

## 🚀 Implementation Timeline

### Week 1:
- **Day 1-2:** CoTGenerator implementation
- **Day 3-4:** ProcessRewardModel implementation
- **Day 5:** Integration with ToTManager

### Week 2:
- **Day 6:** Testing and debugging
- **Day 7:** Documentation and Sprint 2 completion

**Total:** 7 days

---

## 📝 Next Steps

1. Start with CoTGenerator implementation
2. Create test cases
3. Implement ProcessRewardModel
4. Integrate with ToTManager
5. Run integration tests
6. Document Sprint 2 completion
7. Move to Sprint 3 (Reddit Validation)

---

*Sprint 2 Implementation Plan*
*Created: 2026-01-16*
*Goal: Complete Gemini's Original Sprint 2*
