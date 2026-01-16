"""
Axiom Judge - LLM-based evaluation of SPO triplets against axioms.

Part of Cluster 2: Intelligence Layer
Evaluates triplets for Gold promotion using axiom alignment.

Design Philosophy:
- LLM-based value judgment
- Multiple axioms per evaluation
- Score per axiom (0.0-1.0)
- Reasoning transparency (LLM explains decision)
- Required for Silver → Gold promotion
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime

from src.core.model_orchestrator import ModelOrchestrator, ModelCapability, QualityLevel
from src.core.axiom_manager import AxiomManager
from src.models.unified_session import SPOTriplet


@dataclass
class JudgmentResult:
    """Result of axiom evaluation."""
    triplet_id: str
    passes: bool
    axiom_scores: Dict[str, float]  # axiom_id -> score (0.0-1.0)
    reasoning: str
    evaluated_at: str
    overall_score: float  # Average of axiom scores


class AxiomJudge:
    """
    LLM-based Axiom Evaluation for SPO Triplets.

    Process:
    1. Get relevant axioms for triplet domain
    2. Create evaluation prompt with triplet + axioms
    3. LLM evaluates alignment (YES/NO + reasoning)
    4. Parse response and calculate scores
    5. Return judgment result

    Evaluation Criteria:
    - Does triplet support axiom values?
    - Does triplet contradict axiom values?
    - Overall alignment score >= threshold?

    Usage:
        judge = AxiomJudge(
            model_orchestrator=llm,
            axiom_manager=axioms
        )

        # Evaluate single triplet
        result = judge.evaluate_triplet(
            triplet=spo_triplet,
            relevant_axioms=axiom_list
        )

        # Batch evaluation
        results = judge.batch_evaluate(triplet_list)
    """

    # Evaluation prompt template
    EVALUATION_PROMPT = """Evaluate if this fact aligns with our values.

Fact to evaluate:
Subject: {subject}
Predicate: {predicate}
Object: {object}
Confidence: {confidence}

Values to check:
{axioms_text}

Question: Does this fact align with ALL values listed above?

Consider:
1. Does the fact support or contradict any value?
2. Is the fact neutral (neither supports nor contradicts)?
3. Overall alignment with values

Respond in this format:
ALIGNMENT: [YES/NO]
SCORE: [0.0-1.0]
REASONING: [Brief explanation]

Your response:"""

    def __init__(
        self,
        model_orchestrator: ModelOrchestrator,
        axiom_manager: AxiomManager,
        pass_threshold: float = 0.7,
        quality: QualityLevel = QualityLevel.BALANCED
    ):
        """
        Initialize Axiom Judge.

        Args:
            model_orchestrator: LLM for evaluation
            axiom_manager: Axiom manager
            pass_threshold: Minimum score to pass (0.0-1.0)
            quality: LLM quality level
        """
        self.llm = model_orchestrator
        self.axioms = axiom_manager
        self.pass_threshold = pass_threshold
        self.quality = quality

    def evaluate_triplet(
        self,
        triplet: SPOTriplet,
        relevant_axioms: Optional[List[Any]] = None
    ) -> JudgmentResult:
        """
        Evaluate triplet against axioms.

        Args:
            triplet: SPO triplet to evaluate
            relevant_axioms: List of relevant Axiom objects (None = use all)

        Returns:
            JudgmentResult with pass/fail and reasoning
        """
        # Get relevant axioms
        if relevant_axioms is None:
            relevant_axioms = self.axioms.get_all_axioms()

        if not relevant_axioms:
            # No axioms to evaluate against - pass by default
            return JudgmentResult(
                triplet_id=triplet.id,
                passes=True,
                axiom_scores={},
                reasoning="No axioms to evaluate against",
                evaluated_at=datetime.utcnow().isoformat(),
                overall_score=1.0
            )

        # Build axioms text
        axioms_text = self._format_axioms(relevant_axioms)

        # Create prompt
        prompt = self.EVALUATION_PROMPT.format(
            subject=triplet.subject,
            predicate=triplet.predicate,
            object=triplet.object,
            confidence=triplet.confidence,
            axioms_text=axioms_text
        )

        try:
            # Call LLM
            response = self.llm.generate(
                prompt=prompt,
                capability=ModelCapability.VALIDATION,
                quality=self.quality
            )

            # Parse response
            alignment, score, reasoning = self._parse_response(response.content)

            # Calculate per-axiom scores (simplified - all same for now)
            axiom_scores = {}
            for axiom in relevant_axioms:
                if isinstance(axiom, dict):
                    axiom_id = axiom.get("axiom_id", axiom.get("id", "unknown"))
                else:
                    axiom_id = getattr(axiom, "id", "unknown")
                axiom_scores[axiom_id] = score

            passes = score >= self.pass_threshold

            return JudgmentResult(
                triplet_id=triplet.id,
                passes=passes,
                axiom_scores=axiom_scores,
                reasoning=reasoning,
                evaluated_at=datetime.utcnow().isoformat(),
                overall_score=score
            )

        except Exception as e:
            # Evaluation failed - default to pass (conservative)
            return JudgmentResult(
                triplet_id=triplet.id,
                passes=True,
                axiom_scores={},
                reasoning=f"Evaluation failed: {str(e)}",
                evaluated_at=datetime.utcnow().isoformat(),
                overall_score=0.5
            )

    def _format_axioms(self, axioms: List[Any]) -> str:
        """Format axioms for prompt."""
        lines = []
        for i, axiom in enumerate(axioms, 1):
            # Handle both Dict and object axioms
            if isinstance(axiom, dict):
                name = axiom.get("name", axiom.get("axiom_id", "Unknown"))
                description = axiom.get("description", "No description")
            else:
                name = getattr(axiom, "name", "Unknown")
                description = getattr(axiom, "description", "No description")

            lines.append(f"{i}. {name}: {description}")
        return "\n".join(lines)

    def _parse_response(self, response_text: str) -> tuple[str, float, str]:
        """
        Parse LLM response.

        Returns:
            (alignment, score, reasoning) tuple
        """
        import re

        response_text = response_text.strip()

        # Extract ALIGNMENT
        alignment_match = re.search(r'ALIGNMENT:\s*(YES|NO)', response_text, re.IGNORECASE)
        alignment = alignment_match.group(1).upper() if alignment_match else "YES"

        # Extract SCORE
        score_match = re.search(r'SCORE:\s*(0?\.\d+|1\.0+|0)', response_text)
        if score_match:
            try:
                score = float(score_match.group(1))
                score = max(0.0, min(1.0, score))  # Clamp to [0, 1]
            except ValueError:
                score = 0.8 if alignment == "YES" else 0.3
        else:
            # Default based on alignment
            score = 0.8 if alignment == "YES" else 0.3

        # Extract REASONING
        reasoning_match = re.search(r'REASONING:\s*(.+)', response_text, re.DOTALL)
        reasoning = reasoning_match.group(1).strip() if reasoning_match else "No reasoning provided"

        # Truncate reasoning to 500 chars
        if len(reasoning) > 500:
            reasoning = reasoning[:497] + "..."

        return alignment, score, reasoning

    def batch_evaluate(
        self,
        triplets: List[SPOTriplet],
        relevant_axioms: Optional[List[Any]] = None
    ) -> List[JudgmentResult]:
        """
        Batch evaluation for efficiency.

        Args:
            triplets: List of triplets to evaluate
            relevant_axioms: Shared axioms for all (None = use all)

        Returns:
            List of JudgmentResults
        """
        results = []

        for triplet in triplets:
            result = self.evaluate_triplet(triplet, relevant_axioms)
            results.append(result)

        return results

    def get_stats(self, results: List[JudgmentResult]) -> Dict[str, Any]:
        """
        Get statistics from evaluation results.

        Args:
            results: List of JudgmentResults

        Returns:
            Dict with stats
        """
        if not results:
            return {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "pass_rate": 0.0,
                "avg_score": 0.0
            }

        passed = sum(1 for r in results if r.passes)
        failed = len(results) - passed
        avg_score = sum(r.overall_score for r in results) / len(results)

        return {
            "total": len(results),
            "passed": passed,
            "failed": failed,
            "pass_rate": (passed / len(results) * 100) if results else 0.0,
            "avg_score": avg_score
        }

    def evaluate_for_gold_promotion(
        self,
        triplet: SPOTriplet
    ) -> bool:
        """
        Quick check if triplet is eligible for Gold promotion.

        Args:
            triplet: Triplet to evaluate

        Returns:
            True if passes axiom evaluation
        """
        result = self.evaluate_triplet(triplet)
        return result.passes
