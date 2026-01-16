"""
Process Reward Model - Score reasoning steps for quality.

Part of Sprint 2: Intelligence Layer (Gemini's Original Plan)

Inspired by:
- OpenAI Process Reward Models (2023)
- Anthropic Constitutional AI (RLAIF - Reinforcement Learning from AI Feedback)
- DeepMind step-wise verification

Core Concept:
  Instead of scoring only the final answer, score EACH reasoning step:
  - Axiom compliance: Does step align with user's principles?
  - Logical consistency: Is the step logically sound?
  - Evidence strength: Does step provide strong evidence?

  This enables:
  - Early error detection (catch bad reasoning before conclusion)
  - Fine-grained feedback (which steps are weak?)
  - Better variant selection (compare reasoning quality, not just answers)

Usage:
    prm = ProcessRewardModel(axiom_manager, model_orchestrator)

    # Score single step
    score = prm.score_step(
        step="Solar panels reduce carbon emissions by replacing fossil fuels.",
        context="Discussing renewable energy benefits"
    )
    # score.overall_score: 0.85 (high quality step)

    # Score entire CoT variant
    variant_score = prm.score_variant(cot_variant)
    # variant_score['avg_score']: 0.78

Design Philosophy:
- Process > Outcome: Good reasoning matters, not just right answer
- Transparent scoring: 3 dimensions (axiom, logic, evidence)
- Violation detection: Explicitly flag axiom violations
- Configurable: Can use LLM or rule-based scoring

Performance:
- Rule-based scoring: <5ms per step
- LLM-based scoring: ~500ms per step
- Recommended: Rule-based for speed, LLM for critical steps
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
import re

from src.core.axiom_manager import AxiomManager
from src.core.model_orchestrator import ModelOrchestrator


@dataclass
class StepScore:
    """
    Score for a single reasoning step.

    Attributes:
        step_text: The reasoning step being scored
        axiom_compliance: 0.0-1.0 (1.0 = perfect compliance)
        logical_consistency: 0.0-1.0 (1.0 = perfectly logical)
        evidence_strength: 0.0-1.0 (1.0 = strong evidence)
        overall_score: 0.0-1.0 (weighted average)
        violations: List of axiom violations detected
    """
    step_text: str
    axiom_compliance: float
    logical_consistency: float
    evidence_strength: float
    overall_score: float
    violations: List[str]


class ProcessRewardModel:
    """
    Process Reward Model - Score reasoning steps.

    Sprint 2 Component: Process Reward Model (PRM)

    Why step-wise scoring?
    - Catch errors early (before reaching wrong conclusion)
    - Compare reasoning quality (not just final answers)
    - Provide feedback for improvement
    - Align with Constitutional AI principles

    Scoring Dimensions:
    1. Axiom Compliance (40%): Aligns with user's principles
    2. Logical Consistency (40%): Step is logically sound
    3. Evidence Strength (20%): Step provides strong support

    Integration with CoT Generator:
    - CoTGenerator produces 3 variants
    - PRM scores each variant's steps
    - Variant with highest avg score selected
    - Violations logged for review
    """

    # Scoring weights
    AXIOM_WEIGHT = 0.4
    LOGIC_WEIGHT = 0.4
    EVIDENCE_WEIGHT = 0.2

    def __init__(
        self,
        axiom_manager: Optional[AxiomManager],
        model_orchestrator: ModelOrchestrator,
        enable_llm_scoring: bool = False,  # Default: rule-based (faster)
        enable_axiom_check: bool = True
    ):
        """
        Initialize Process Reward Model.

        Args:
            axiom_manager: Axiom library for compliance checking (optional)
            model_orchestrator: LLM for logical consistency checking
            enable_llm_scoring: Use LLM for scoring (slower but more accurate)
            enable_axiom_check: Check axiom compliance (requires axiom_manager)
        """
        self.axioms = axiom_manager
        self.model = model_orchestrator
        self.enable_llm = enable_llm_scoring
        self.enable_axiom_check = enable_axiom_check and axiom_manager is not None

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

        Example:
            score = prm.score_step(
                step="Solar panels reduce emissions by 50%",
                context="Discussing renewable energy"
            )

            print(f"Axiom compliance: {score.axiom_compliance}")
            print(f"Logical consistency: {score.logical_consistency}")
            print(f"Evidence strength: {score.evidence_strength}")
            print(f"Overall: {score.overall_score}")
        """
        # 1. Check axiom compliance
        if self.enable_axiom_check:
            axiom_score, violations = self._check_axiom_compliance(step)
        else:
            axiom_score, violations = 1.0, []

        # 2. Check logical consistency
        logic_score = self._check_logical_consistency(step, context)

        # 3. Check evidence strength
        evidence_score = self._check_evidence_strength(step)

        # 4. Weighted average
        overall = (
            axiom_score * self.AXIOM_WEIGHT +
            logic_score * self.LOGIC_WEIGHT +
            evidence_score * self.EVIDENCE_WEIGHT
        )

        return StepScore(
            step_text=step,
            axiom_compliance=axiom_score,
            logical_consistency=logic_score,
            evidence_strength=evidence_score,
            overall_score=overall,
            violations=violations
        )

    def score_variant(self, variant) -> Dict:
        """
        Score entire CoT variant.

        Args:
            variant: CoTVariant object (from CoTGenerator)

        Returns:
            {
                "step_scores": List[StepScore],
                "avg_score": float,          # Average of all step scores
                "min_score": float,          # Weakest step score
                "max_score": float,          # Best step score
                "violations_count": int,     # Total axiom violations
                "axiom_compliance_avg": float,
                "logic_consistency_avg": float,
                "evidence_strength_avg": float
            }

        Example:
            result = prm.score_variant(variant_a)

            if result['avg_score'] > 0.7:
                print("High quality reasoning!")

            if result['violations_count'] > 0:
                print(f"Warning: {result['violations_count']} axiom violations")
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
                "max_score": 0.0,
                "violations_count": 0,
                "axiom_compliance_avg": 0.0,
                "logic_consistency_avg": 0.0,
                "evidence_strength_avg": 0.0
            }

        # Aggregate statistics
        avg_score = sum(s.overall_score for s in step_scores) / len(step_scores)
        min_score = min(s.overall_score for s in step_scores)
        max_score = max(s.overall_score for s in step_scores)
        violations_count = sum(len(s.violations) for s in step_scores)

        # Dimension averages
        axiom_avg = sum(s.axiom_compliance for s in step_scores) / len(step_scores)
        logic_avg = sum(s.logical_consistency for s in step_scores) / len(step_scores)
        evidence_avg = sum(s.evidence_strength for s in step_scores) / len(step_scores)

        return {
            "step_scores": step_scores,
            "avg_score": avg_score,
            "min_score": min_score,
            "max_score": max_score,
            "violations_count": violations_count,
            "axiom_compliance_avg": axiom_avg,
            "logic_consistency_avg": logic_avg,
            "evidence_strength_avg": evidence_avg
        }

    def _check_axiom_compliance(self, step: str) -> tuple[float, List[str]]:
        """
        Check if step complies with axioms.

        Strategy:
        1. Get all active axioms
        2. Check step against each axiom's negative examples
        3. If negative example found in step → violation
        4. Return compliance score and violations

        Args:
            step: Reasoning step text

        Returns:
            (compliance_score, violations_list)
        """
        if not self.axioms:
            return 1.0, []  # No axioms = always compliant

        # Get all axioms
        try:
            axioms = self.axioms.get_all_axioms()
        except:
            return 1.0, []

        if not axioms:
            return 1.0, []

        # Check each axiom
        violations = []
        compliance_scores = []

        step_lower = step.lower()

        for axiom in axioms:
            violates = self._check_single_axiom(step_lower, axiom)

            if violates:
                violations.append(f"Violates axiom: {axiom.name}")
                compliance_scores.append(0.0)
            else:
                compliance_scores.append(1.0)

        # Average compliance
        avg_compliance = sum(compliance_scores) / len(compliance_scores) if compliance_scores else 1.0

        return avg_compliance, violations

    def _check_single_axiom(self, step_lower: str, axiom) -> bool:
        """
        Check if step violates a single axiom.

        Uses negative examples from axiom as violation patterns.

        Args:
            step_lower: Step text (lowercased)
            axiom: Axiom object

        Returns:
            True if violation detected, False otherwise
        """
        # Check negative examples (patterns to avoid)
        if hasattr(axiom, 'negative_examples') and axiom.negative_examples:
            for negative_example in axiom.negative_examples:
                if negative_example.lower() in step_lower:
                    return True  # Violation detected

        # Check for specific anti-patterns based on axiom name
        # (Can be expanded with more sophisticated checking)
        if "sovereignty" in axiom.name.lower():
            # Check for cloud/proprietary patterns
            cloud_patterns = ["rely on cloud", "use proprietary", "vendor lock-in"]
            if any(pattern in step_lower for pattern in cloud_patterns):
                return True

        return False  # No violation

    def _check_logical_consistency(
        self,
        step: str,
        context: Optional[str]
    ) -> float:
        """
        Check logical consistency of step.

        Rule-based heuristics:
        - Has logical connectors (therefore, because, thus)
        - No contradictions (but, however followed by opposite claim)
        - Has causal structure (if-then, cause-effect)

        LLM-based (if enabled):
        - Ask LLM to rate logical soundness 0.0-1.0

        Args:
            step: Reasoning step text
            context: Optional context

        Returns:
            Consistency score 0.0-1.0
        """
        if self.enable_llm:
            return self._llm_check_consistency(step, context)
        else:
            return self._rule_based_consistency(step)

    def _rule_based_consistency(self, step: str) -> float:
        """Rule-based logical consistency check."""
        step_lower = step.lower()
        score = 0.5  # Base score

        # Positive indicators
        logical_connectors = [
            "therefore", "thus", "hence", "because", "since",
            "as a result", "consequently", "which means",
            "this shows", "this indicates", "this suggests"
        ]

        if any(conn in step_lower for conn in logical_connectors):
            score += 0.2

        # Causal structure
        if "if" in step_lower and "then" in step_lower:
            score += 0.15

        if any(word in step_lower for word in ["causes", "leads to", "results in"]):
            score += 0.15

        # Negative indicators
        contradiction_patterns = [
            ("but", "however"),
            ("although", "despite"),
            ("even though", "nevertheless")
        ]

        # Penalize if step contains contradictory structure without resolution
        for pattern_pair in contradiction_patterns:
            if any(p in step_lower for p in pattern_pair):
                # Check if there's a resolution
                if "therefore" not in step_lower and "thus" not in step_lower:
                    score -= 0.1

        return min(1.0, max(0.0, score))

    def _llm_check_consistency(
        self,
        step: str,
        context: Optional[str]
    ) -> float:
        """LLM-based logical consistency check."""
        prompt = f"""Evaluate the logical consistency of this reasoning step.

Step: {step}
"""
        if context:
            prompt += f"""
Context: {context}
"""

        prompt += """
Is this step logically sound and consistent?
Rate from 0.0 (completely illogical) to 1.0 (perfectly logical).

Provide only the numerical score (e.g., 0.8).

Score:"""

        try:
            response = self.model.generate(
                prompt=prompt,
                max_tokens=10,
                temperature=0.1
            )

            # Extract score
            match = re.search(r'(\d+\.?\d*)', response)
            if match:
                score = float(match.group(1))
                if score > 1.0:
                    score /= 100.0  # Handle percentage format
                return min(1.0, max(0.0, score))
        except Exception as e:
            print(f"Warning: LLM consistency check failed: {e}")

        return 0.7  # Default on error

    def _check_evidence_strength(self, step: str) -> float:
        """
        Check if step provides strong evidence.

        Evidence indicators:
        - References to research/studies
        - Data/statistics mentioned
        - Specific examples given
        - Expert opinion cited
        - Causal mechanisms explained

        Args:
            step: Reasoning step text

        Returns:
            Evidence strength 0.0-1.0
        """
        step_lower = step.lower()
        score = 0.3  # Base score

        # Strong evidence indicators
        strong_evidence = [
            "research shows", "study found", "studies indicate",
            "data suggests", "data shows", "statistics show",
            "evidence demonstrates", "proven", "verified",
            "according to", "analysis reveals", "meta-analysis"
        ]

        # Moderate evidence indicators
        moderate_evidence = [
            "example", "instance", "case", "experience",
            "observed", "measured", "recorded",
            "reported", "documented"
        ]

        # Weak evidence indicators (claims without support)
        weak_patterns = [
            "i think", "i believe", "probably", "maybe",
            "might", "could", "seems like"
        ]

        # Count strong evidence
        strong_count = sum(1 for indicator in strong_evidence if indicator in step_lower)
        moderate_count = sum(1 for indicator in moderate_evidence if indicator in step_lower)
        weak_count = sum(1 for indicator in weak_patterns if indicator in step_lower)

        # Scoring
        score += strong_count * 0.25  # +0.25 per strong evidence
        score += moderate_count * 0.15  # +0.15 per moderate evidence
        score -= weak_count * 0.1  # -0.1 per weak pattern

        # Check for specific numbers/data (indicates empirical backing)
        if re.search(r'\d+%', step) or re.search(r'\$\d+', step):
            score += 0.1

        return min(1.0, max(0.0, score))
