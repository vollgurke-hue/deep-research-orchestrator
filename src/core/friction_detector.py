"""
Friction Detector - Compare AI hypotheses vs Human experiences

Part of Sprint 3: Verification Layer (Gemini's Original Plan)

Detects "friction" = difference between theory (AI) and practice (humans).

Example:
    AI says: "Inverter X has 10-year MTBF"
    Reddit says: "My Inverter X died after 3 years"
    → FRICTION DETECTED!
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from src.models.unified_session import SPOTriplet


@dataclass
class FrictionReport:
    """
    Report of friction between AI hypothesis and human experiences.

    Attributes:
        hypothesis: The AI-generated SPO triplet being validated
        supporting_evidence: Number of experiences that support it
        contradicting_evidence: Number of experiences that contradict it
        friction_score: 0.0 (perfect match) to 1.0 (total contradiction)
        verdict: "confirmed", "friction_detected", or "contradicted"
        confidence: How confident are we in this assessment (0.0-1.0)
        top_supporting: Most upvoted supporting experiences
        top_contradicting: Most upvoted contradicting experiences
    """
    hypothesis: SPOTriplet
    supporting_evidence: int
    contradicting_evidence: int
    friction_score: float
    verdict: str
    confidence: float
    top_supporting: List['ExperienceNode']
    top_contradicting: List['ExperienceNode']


class FrictionDetector:
    """
    Detect friction between AI hypotheses and human experiences.

    Core idea:
    - AI generates hypothesis from docs/data
    - Humans report real-world experiences
    - Friction = when they disagree

    Usage:
        detector = FrictionDetector()

        # AI hypothesis
        hypothesis = SPOTriplet(
            subject="Inverter_X",
            predicate="has_reliability",
            object="excellent"
        )

        # Human experiences from Reddit
        experiences = [...]  # List of ExperienceNode

        # Detect friction
        report = detector.detect_friction(hypothesis, experiences)

        if report.verdict == "friction_detected":
            print(f"WARNING: Friction score {report.friction_score:.2f}")
            print(f"AI says: {hypothesis}")
            print(f"But {report.contradicting_evidence} users report problems!")
    """

    def detect_friction(
        self,
        hypothesis: SPOTriplet,
        experiences: List['ExperienceNode']
    ) -> FrictionReport:
        """
        Detect friction between hypothesis and experiences.

        Args:
            hypothesis: AI-generated SPO triplet
            experiences: Human experiences from Reddit/forums

        Returns:
            FrictionReport with detailed analysis
        """
        if not experiences:
            # No data to compare
            return FrictionReport(
                hypothesis=hypothesis,
                supporting_evidence=0,
                contradicting_evidence=0,
                friction_score=0.0,
                verdict="unvalidated",
                confidence=0.0,
                top_supporting=[],
                top_contradicting=[]
            )

        # Classify experiences as supporting or contradicting
        supporting = []
        contradicting = []
        neutral = []

        for exp in experiences:
            relevance = self._check_relevance(hypothesis, exp)

            if relevance == "supporting":
                supporting.append(exp)
            elif relevance == "contradicting":
                contradicting.append(exp)
            else:
                neutral.append(exp)

        # Calculate friction score
        friction_score = self._calculate_friction_score(
            supporting, contradicting, neutral
        )

        # Determine verdict
        if friction_score < 0.3:
            verdict = "confirmed"
        elif friction_score < 0.7:
            verdict = "friction_detected"
        else:
            verdict = "contradicted"

        # Calculate confidence
        confidence = self._calculate_confidence(supporting, contradicting, neutral)

        # Get top experiences (by upvotes)
        top_supporting = sorted(supporting, key=lambda e: e.upvotes, reverse=True)[:5]
        top_contradicting = sorted(contradicting, key=lambda e: e.upvotes, reverse=True)[:5]

        return FrictionReport(
            hypothesis=hypothesis,
            supporting_evidence=len(supporting),
            contradicting_evidence=len(contradicting),
            friction_score=friction_score,
            verdict=verdict,
            confidence=confidence,
            top_supporting=top_supporting,
            top_contradicting=top_contradicting
        )

    def _check_relevance(
        self,
        hypothesis: SPOTriplet,
        experience: 'ExperienceNode'
    ) -> str:
        """
        Check if experience supports, contradicts, or is neutral to hypothesis.

        Returns: "supporting", "contradicting", or "neutral"
        """
        # Extract key terms from hypothesis
        subject = hypothesis.subject.lower()
        predicate = hypothesis.predicate.lower()
        obj = hypothesis.object.lower()

        # Check if experience is about the same subject
        claim_lower = experience.claim.lower()

        # Must mention the subject
        if subject not in claim_lower:
            # Try to match brand name (e.g., "SolarEdge" in "Inverter_SolarEdge")
            brand = self._extract_brand(subject)
            if brand and brand.lower() not in claim_lower:
                return "neutral"

        # Check sentiment alignment
        if predicate in ["has_reliability", "is_reliable", "has_quality"]:
            # Positive predicate
            if obj in ["high", "excellent", "good", "reliable"]:
                # AI says: positive quality
                if experience.sentiment == "positive":
                    return "supporting"
                elif experience.sentiment == "negative":
                    return "contradicting"
            elif obj in ["low", "poor", "bad", "unreliable"]:
                # AI says: negative quality
                if experience.sentiment == "negative":
                    return "supporting"
                elif experience.sentiment == "positive":
                    return "contradicting"

        elif predicate in ["has_lifespan", "has_mtbf", "lasts"]:
            # Lifespan claims
            if "year" in obj:
                # Extract years from object
                years_match = re.search(r'(\d+)', obj)
                if years_match:
                    expected_years = int(years_match.group(1))

                    # Check if experience mentions failure
                    if experience.sentiment == "negative" and experience.timeframe:
                        # Extract actual years from experience
                        actual_match = re.search(r'(\d+)\s*years?', experience.timeframe)
                        if actual_match:
                            actual_years = int(actual_match.group(1))

                            if actual_years < expected_years * 0.5:
                                # Failed much earlier than expected
                                return "contradicting"

        elif predicate in ["has_price", "costs"]:
            # Price claims
            # Extract price from object and experience
            ai_price = self._extract_price(obj)
            exp_price = self._extract_price(experience.claim + " " + str(experience.context))

            if ai_price and exp_price:
                # Compare prices
                if abs(ai_price - exp_price) / ai_price < 0.2:  # Within 20%
                    return "supporting"
                elif exp_price > ai_price * 1.5:  # 50% more expensive
                    return "contradicting"

        # Default: check sentiment alignment
        if experience.sentiment == "positive":
            return "supporting"
        elif experience.sentiment == "negative":
            return "contradicting"

        return "neutral"

    def _calculate_friction_score(
        self,
        supporting: List['ExperienceNode'],
        contradicting: List['ExperienceNode'],
        neutral: List['ExperienceNode']
    ) -> float:
        """
        Calculate friction score (0.0 = no friction, 1.0 = total friction).

        Weighted by:
        - Number of experiences
        - Upvotes (community agreement)
        - Quality scores
        """
        # Weight experiences by quality and upvotes
        support_weight = sum(
            exp.quality_score * (1 + exp.upvotes / 100.0)
            for exp in supporting
        )

        contradict_weight = sum(
            exp.quality_score * (1 + exp.upvotes / 100.0)
            for exp in contradicting
        )

        total_weight = support_weight + contradict_weight

        if total_weight == 0:
            return 0.5  # Neutral if no evidence

        # Friction = proportion of contradicting evidence
        friction = contradict_weight / total_weight

        return friction

    def _calculate_confidence(
        self,
        supporting: List['ExperienceNode'],
        contradicting: List['ExperienceNode'],
        neutral: List['ExperienceNode']
    ) -> float:
        """
        Calculate confidence in the assessment (0.0-1.0).

        Higher confidence = more evidence, higher quality.
        """
        total_experiences = len(supporting) + len(contradicting) + len(neutral)

        if total_experiences == 0:
            return 0.0

        # Confidence increases with:
        # 1. More experiences
        sample_confidence = min(total_experiences / 20.0, 1.0)  # Max at 20 experiences

        # 2. Higher average quality
        relevant = supporting + contradicting
        if relevant:
            avg_quality = sum(exp.quality_score for exp in relevant) / len(relevant)
        else:
            avg_quality = 0.5

        # 3. More upvotes
        total_upvotes = sum(exp.upvotes for exp in relevant)
        upvote_confidence = min(total_upvotes / 200.0, 1.0)  # Max at 200 upvotes

        # Combined confidence
        confidence = (sample_confidence + avg_quality + upvote_confidence) / 3.0

        return confidence

    def _extract_brand(self, subject: str) -> Optional[str]:
        """Extract brand name from subject (e.g., 'SolarEdge' from 'Inverter_SolarEdge')."""
        import re
        match = re.search(r'([A-Z][a-z]+(?:[A-Z][a-z]+)*)', subject)
        return match.group(1) if match else None

    def _extract_price(self, text: str) -> Optional[float]:
        """Extract price from text (€1234 or $1234)."""
        import re
        match = re.search(r'[€$](\d+(?:,\d{3})*(?:\.\d{2})?)', text)
        if match:
            price_str = match.group(1).replace(',', '')
            return float(price_str)
        return None


# Import at end to avoid circular dependency
import re
