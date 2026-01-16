"""
Multi-Source Verifier - Verify SPO triplets across multiple sources.

Part of Cluster 2: Intelligence Layer
Enables Tiered RAG by tracking verification sources for triplets.

Design Philosophy:
- Multi-source verification increases confidence
- 2+ sources → eligible for Silver tier
- 3+ sources → eligible for Gold (with axiom pass)
- Semantic similarity for finding related triplets
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from src.models.unified_session import SPOTriplet
from src.core.graph_manager import GraphManager


@dataclass
class VerificationResult:
    """Result of triplet verification."""
    triplet_id: str
    verified: bool
    source_count: int
    verification_sources: List[str]
    should_promote: bool
    similarity_scores: Dict[str, float] = None  # Similar triplet IDs -> similarity score


class MultiSourceVerifier:
    """
    Multi-Source Verification for SPO Triplets.

    Process:
    1. New triplet extracted → Bronze tier (1 source)
    2. Similar triplet found in another source → Add verification
    3. 2+ sources → Eligible for Silver promotion
    4. 3+ sources → Eligible for Gold (needs axiom pass)

    Similarity Criteria:
    - Subject similarity (exact or semantic)
    - Predicate similarity (exact or synonym)
    - Object similarity (exact or semantic)

    Usage:
        verifier = MultiSourceVerifier(graph_manager, min_sources=2)

        # Verify triplet with new source
        result = verifier.verify_triplet(
            triplet_id="spo_123",
            new_source="tot_node_456"
        )

        if result.should_promote:
            # Trigger promotion to Silver
            tier_promoter.promote_if_eligible(triplet_id)
    """

    def __init__(
        self,
        graph_manager: GraphManager,
        min_sources_silver: int = 2,
        min_sources_gold: int = 3,
        similarity_threshold: float = 0.85
    ):
        """
        Initialize Multi-Source Verifier.

        Args:
            graph_manager: GraphManager with SPO database
            min_sources_silver: Minimum sources for Silver tier
            min_sources_gold: Minimum sources for Gold tier
            similarity_threshold: Minimum similarity for "same" triplet
        """
        self.graph = graph_manager
        self.min_sources_silver = min_sources_silver
        self.min_sources_gold = min_sources_gold
        self.similarity_threshold = similarity_threshold

        # Check SPO database available
        if not hasattr(graph_manager, 'spo_db') or not graph_manager.spo_db:
            raise RuntimeError("GraphManager must have SPO database initialized")

    def verify_triplet(
        self,
        triplet_id: str,
        new_source: str
    ) -> VerificationResult:
        """
        Verify triplet with new source.

        Adds new_source to triplet's verification sources and checks
        if promotion is now possible.

        Args:
            triplet_id: SPO triplet to verify
            new_source: Source ID (e.g., "tot_node_456")

        Returns:
            VerificationResult with verification status and promotion eligibility
        """
        # Get triplet
        triplet = self.graph.spo_db.get_by_id(triplet_id)
        if not triplet:
            return VerificationResult(
                triplet_id=triplet_id,
                verified=False,
                source_count=0,
                verification_sources=[],
                should_promote=False
            )

        # Add new source to provenance
        if new_source not in triplet.provenance.verification_sources:
            # Update in database (this updates the provenance internally)
            self.graph.spo_db.update_provenance(
                triplet_id=triplet_id,
                verified=True,
                verification_source=new_source
            )

            # Re-fetch updated triplet
            triplet = self.graph.spo_db.get_by_id(triplet_id)

        # Check promotion eligibility
        source_count = len(triplet.provenance.verification_sources) + 1  # +1 for original source
        should_promote = False

        if triplet.tier == "bronze" and source_count >= self.min_sources_silver:
            should_promote = True
        elif triplet.tier == "silver" and source_count >= self.min_sources_gold:
            # Note: Gold promotion also requires axiom pass (handled by TierPromoter)
            should_promote = True

        return VerificationResult(
            triplet_id=triplet_id,
            verified=True,
            source_count=source_count,
            verification_sources=triplet.provenance.verification_sources,
            should_promote=should_promote
        )

    def find_similar_triplets(
        self,
        triplet: SPOTriplet,
        similarity_threshold: Optional[float] = None
    ) -> List[Tuple[SPOTriplet, float]]:
        """
        Find semantically similar triplets.

        Similarity is based on:
        - Subject match (exact > semantic)
        - Predicate match (exact > synonym)
        - Object match (exact > semantic)

        Args:
            triplet: SPO triplet to find similar ones for
            similarity_threshold: Override default threshold

        Returns:
            List of (similar_triplet, similarity_score) tuples
        """
        threshold = similarity_threshold or self.similarity_threshold

        # Get all triplets (TODO: optimize with index)
        all_triplets = self.graph.get_spo_triplets(limit=1000)

        similar = []
        for other in all_triplets:
            if other.id == triplet.id:
                continue  # Skip self

            # Calculate similarity
            sim_score = self._calculate_similarity(triplet, other)

            if sim_score >= threshold:
                similar.append((other, sim_score))

        # Sort by similarity (highest first)
        similar.sort(key=lambda x: x[1], reverse=True)

        return similar

    def _calculate_similarity(
        self,
        triplet_a: SPOTriplet,
        triplet_b: SPOTriplet
    ) -> float:
        """
        Calculate similarity between two triplets.

        Simple approach:
        - Subject exact match: +0.4
        - Predicate exact match: +0.3
        - Object exact match: +0.3
        - Case-insensitive comparison

        Returns:
            Similarity score 0.0-1.0
        """
        score = 0.0

        # Subject similarity
        if triplet_a.subject.lower() == triplet_b.subject.lower():
            score += 0.4
        elif self._fuzzy_match(triplet_a.subject, triplet_b.subject):
            score += 0.2  # Partial credit for fuzzy match

        # Predicate similarity
        if triplet_a.predicate.lower() == triplet_b.predicate.lower():
            score += 0.3
        elif self._is_predicate_synonym(triplet_a.predicate, triplet_b.predicate):
            score += 0.15  # Partial credit for synonym

        # Object similarity
        if triplet_a.object.lower() == triplet_b.object.lower():
            score += 0.3
        elif self._fuzzy_match(triplet_a.object, triplet_b.object):
            score += 0.15  # Partial credit for fuzzy match

        return min(score, 1.0)  # Clamp to [0, 1]

    def _fuzzy_match(self, text_a: str, text_b: str) -> bool:
        """
        Simple fuzzy string matching.

        Returns True if strings have >70% overlap.
        """
        a = text_a.lower()
        b = text_b.lower()

        # Check if one contains the other
        if a in b or b in a:
            return True

        # Check word overlap
        words_a = set(a.split())
        words_b = set(b.split())

        if not words_a or not words_b:
            return False

        overlap = len(words_a & words_b)
        total = len(words_a | words_b)

        return (overlap / total) > 0.7 if total > 0 else False

    def _is_predicate_synonym(self, pred_a: str, pred_b: str) -> bool:
        """
        Check if predicates are synonyms.

        Simple rule-based approach.
        TODO: Use word embeddings for better semantic matching.
        """
        # Normalize
        a = pred_a.lower().replace("_", " ").replace("-", " ")
        b = pred_b.lower().replace("_", " ").replace("-", " ")

        # Exact match after normalization
        if a == b:
            return True

        # Common synonyms
        synonym_groups = [
            {"has", "contains", "includes", "possesses"},
            {"is", "equals", "represents"},
            {"reduces", "decreases", "lowers", "cuts"},
            {"increases", "raises", "boosts", "improves"},
            {"causes", "leads to", "results in", "produces"},
        ]

        for group in synonym_groups:
            if a in group and b in group:
                return True

        return False

    def get_verification_stats(self) -> Dict:
        """
        Get verification statistics.

        Returns:
            Dict with stats:
            - total_triplets
            - verified_count (>1 source)
            - avg_sources_per_triplet
            - by_tier (bronze/silver/gold counts)
        """
        stats = self.graph.get_spo_stats()

        # Get all triplets to calculate verification stats
        all_triplets = self.graph.get_spo_triplets(limit=10000)

        verified_count = 0
        total_sources = 0

        for t in all_triplets:
            source_count = len(t.provenance.verification_sources) + 1  # +1 for original
            total_sources += source_count

            if t.provenance.verified:
                verified_count += 1

        total = stats.get("total_triplets", 0)

        return {
            "total_triplets": total,
            "verified_count": verified_count,
            "verification_rate": (verified_count / total * 100) if total > 0 else 0.0,
            "avg_sources_per_triplet": (total_sources / total) if total > 0 else 0.0,
            "by_tier": {
                "bronze": stats.get("bronze_count", 0),
                "silver": stats.get("silver_count", 0),
                "gold": stats.get("gold_count", 0)
            }
        }

    def batch_verify(
        self,
        triplet_source_pairs: List[Tuple[str, str]]
    ) -> List[VerificationResult]:
        """
        Batch verification for efficiency.

        Args:
            triplet_source_pairs: List of (triplet_id, source_id) tuples

        Returns:
            List of VerificationResults
        """
        results = []

        for triplet_id, source_id in triplet_source_pairs:
            result = self.verify_triplet(triplet_id, source_id)
            results.append(result)

        return results
