"""
Consensus Scorer - Calculate weighted consensus from human experiences

Part of Sprint 3: Verification Layer (Gemini's Original Plan)

Not all Reddit posts are equal!
- 100 upvotes > 1 upvote
- Personal experience > hearsay
- Recent > old
- Expert > novice

This module calculates a weighted consensus score.
"""

from typing import List, Dict
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class ConsensusScore:
    """
    Weighted consensus from human experiences.

    Attributes:
        sentiment: Overall sentiment (-1.0 negative to +1.0 positive)
        confidence: How confident are we (0.0-1.0)
        sample_size: Number of experiences analyzed
        dominant_verdict: "positive", "negative", or "mixed"
        breakdown: Detailed breakdown by sentiment
    """
    sentiment: float  # -1.0 to +1.0
    confidence: float  # 0.0 to 1.0
    sample_size: int
    dominant_verdict: str
    breakdown: Dict[str, int]  # {"positive": 10, "negative": 5, "neutral": 3}


class ConsensusScorer:
    """
    Calculate weighted consensus from human experiences.

    Weighting factors:
    1. Upvotes (community agreement)
    2. Evidence type (personal > hearsay)
    3. Confidence (certain > speculative)
    4. Expertise (technical knowledge)
    5. Recency (recent > old)
    6. Quality score

    Usage:
        scorer = ConsensusScorer()

        experiences = [...]  # List of ExperienceNode

        consensus = scorer.calculate_consensus(experiences)

        print(f"Sentiment: {consensus.sentiment:.2f}")
        print(f"Verdict: {consensus.dominant_verdict}")
        print(f"Confidence: {consensus.confidence:.2f}")
    """

    # Weighting factors
    UPVOTE_WEIGHT_MULTIPLIER = 0.02  # Each upvote adds 2% to weight
    PERSONAL_EXPERIENCE_MULTIPLIER = 2.0
    HEARSAY_MULTIPLIER = 0.5
    CERTAIN_MULTIPLIER = 1.5
    SPECULATIVE_MULTIPLIER = 0.5
    EXPERTISE_MULTIPLIER = 0.1  # Per technical term
    RECENCY_DAYS = 180  # Posts within 6 months get bonus

    def calculate_consensus(
        self,
        experiences: List['ExperienceNode']
    ) -> ConsensusScore:
        """
        Calculate weighted consensus from experiences.

        Args:
            experiences: List of ExperienceNode objects

        Returns:
            ConsensusScore with overall sentiment and confidence
        """
        if not experiences:
            return ConsensusScore(
                sentiment=0.0,
                confidence=0.0,
                sample_size=0,
                dominant_verdict="unknown",
                breakdown={"positive": 0, "negative": 0, "neutral": 0}
            )

        # Calculate weighted sentiment
        total_weight = 0.0
        sentiment_sum = 0.0

        # Count sentiments for breakdown
        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}

        for exp in experiences:
            # Base weight
            weight = 1.0

            # Factor 1: Upvotes (community agreement)
            weight *= (1.0 + exp.upvotes * self.UPVOTE_WEIGHT_MULTIPLIER)

            # Factor 2: Evidence type
            if exp.evidence_type == "personal_experience":
                weight *= self.PERSONAL_EXPERIENCE_MULTIPLIER
            elif exp.evidence_type == "hearsay":
                weight *= self.HEARSAY_MULTIPLIER

            # Factor 3: Confidence
            if exp.confidence == "certain":
                weight *= self.CERTAIN_MULTIPLIER
            elif exp.confidence == "speculative":
                weight *= self.SPECULATIVE_MULTIPLIER

            # Factor 4: Expertise indicators
            expertise_count = len(exp.expertise_indicators)
            weight *= (1.0 + expertise_count * self.EXPERTISE_MULTIPLIER)

            # Factor 5: Recency
            if exp.timestamp:
                age_days = (datetime.now() - exp.timestamp).days
                if age_days < self.RECENCY_DAYS:
                    # Recent posts get 50% bonus
                    weight *= 1.5
                elif age_days > 365 * 3:  # > 3 years
                    # Old posts get 50% penalty
                    weight *= 0.5

            # Factor 6: Quality score
            weight *= exp.quality_score

            # Convert sentiment to numeric value
            sentiment_value = self._sentiment_to_value(exp.sentiment)

            # Accumulate
            total_weight += weight
            sentiment_sum += sentiment_value * weight

            # Count for breakdown
            sentiment_counts[exp.sentiment] += 1

        # Calculate final sentiment score
        if total_weight > 0:
            sentiment = sentiment_sum / total_weight
        else:
            sentiment = 0.0

        # Calculate confidence
        confidence = self._calculate_confidence(experiences, total_weight)

        # Determine dominant verdict
        if sentiment > 0.3:
            dominant_verdict = "positive"
        elif sentiment < -0.3:
            dominant_verdict = "negative"
        else:
            dominant_verdict = "mixed"

        return ConsensusScore(
            sentiment=sentiment,
            confidence=confidence,
            sample_size=len(experiences),
            dominant_verdict=dominant_verdict,
            breakdown=sentiment_counts
        )

    def _sentiment_to_value(self, sentiment: str) -> float:
        """Convert sentiment string to numeric value."""
        mapping = {
            "positive": 1.0,
            "neutral": 0.0,
            "negative": -1.0
        }
        return mapping.get(sentiment, 0.0)

    def _calculate_confidence(
        self,
        experiences: List['ExperienceNode'],
        total_weight: float
    ) -> float:
        """
        Calculate confidence in consensus (0.0-1.0).

        Higher confidence = more evidence, better quality, stronger agreement.
        """
        # Factor 1: Sample size (more experiences = higher confidence)
        sample_confidence = min(len(experiences) / 20.0, 1.0)  # Max at 20

        # Factor 2: Total weight (higher weight = more credible sources)
        weight_confidence = min(total_weight / 100.0, 1.0)  # Max at weight 100

        # Factor 3: Agreement (are sentiments aligned or mixed?)
        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
        for exp in experiences:
            sentiment_counts[exp.sentiment] += 1

        # Calculate agreement as percentage of most common sentiment
        max_count = max(sentiment_counts.values()) if sentiment_counts else 0
        agreement = max_count / len(experiences) if experiences else 0

        # Factor 4: Average quality
        avg_quality = sum(exp.quality_score for exp in experiences) / len(experiences)

        # Combine factors
        confidence = (
            sample_confidence * 0.3 +
            weight_confidence * 0.2 +
            agreement * 0.3 +
            avg_quality * 0.2
        )

        return min(1.0, confidence)
