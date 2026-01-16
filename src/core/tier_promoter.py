"""
Tier Promoter - Automatic promotion of SPO triplets across tiers.

Part of Cluster 2: Intelligence Layer
Handles Bronze → Silver → Gold promotion based on verification and axioms.

Design Philosophy:
- Automatic promotion based on rules
- Bronze → Silver: 2+ verified sources
- Silver → Gold: 3+ sources + axiom pass
- Tracks promotion history
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

from src.core.graph_manager import GraphManager
from src.core.multi_source_verifier import MultiSourceVerifier
from src.models.unified_session import SPOTriplet


@dataclass
class PromotionResult:
    """Result of tier promotion attempt."""
    triplet_id: str
    old_tier: str
    new_tier: str
    promoted: bool
    reason: str
    promoted_at: Optional[str] = None


class TierPromoter:
    """
    Automatic Tier Promotion for SPO Triplets.

    Promotion Rules:
    - Bronze → Silver: 2+ verified sources, confidence >= 0.7
    - Silver → Gold: 3+ sources, confidence >= 0.85, axiom pass

    Process:
    1. Check if triplet meets source requirements
    2. Check confidence threshold
    3. For Gold: Check axiom pass (if AxiomJudge available)
    4. Update tier in database
    5. Record promotion history

    Usage:
        promoter = TierPromoter(
            graph_manager=graph,
            verifier=verifier,
            axiom_judge=None  # Optional
        )

        # Try to promote single triplet
        result = promoter.promote_if_eligible("spo_123")

        # Batch promotion
        results = promoter.auto_promote_batch(["spo_123", "spo_456"])
    """

    # Promotion thresholds
    BRONZE_TO_SILVER = {
        "min_sources": 2,
        "min_confidence": 0.7
    }

    SILVER_TO_GOLD = {
        "min_sources": 3,
        "min_confidence": 0.85,
        "requires_axiom_pass": True
    }

    def __init__(
        self,
        graph_manager: GraphManager,
        verifier: MultiSourceVerifier,
        axiom_judge: Optional[Any] = None  # AxiomJudge will be implemented later
    ):
        """
        Initialize Tier Promoter.

        Args:
            graph_manager: GraphManager with SPO database
            verifier: MultiSourceVerifier for checking sources
            axiom_judge: Optional AxiomJudge for Gold promotion
        """
        self.graph = graph_manager
        self.verifier = verifier
        self.axiom_judge = axiom_judge

        # Check dependencies
        if not hasattr(graph_manager, 'spo_db') or not graph_manager.spo_db:
            raise RuntimeError("GraphManager must have SPO database initialized")

    def promote_if_eligible(
        self,
        triplet_id: str,
        force: bool = False
    ) -> PromotionResult:
        """
        Check and promote triplet if eligible.

        Args:
            triplet_id: SPO triplet to check
            force: Skip confidence checks (useful for testing)

        Returns:
            PromotionResult with promotion status
        """
        # Get triplet
        triplet = self.graph.spo_db.get_by_id(triplet_id)
        if not triplet:
            return PromotionResult(
                triplet_id=triplet_id,
                old_tier="unknown",
                new_tier="unknown",
                promoted=False,
                reason="Triplet not found"
            )

        old_tier = triplet.tier
        source_count = len(triplet.provenance.verification_sources) + 1  # +1 for original

        # Check Bronze → Silver
        if triplet.tier == "bronze":
            return self._try_promote_to_silver(triplet, source_count, force)

        # Check Silver → Gold
        elif triplet.tier == "silver":
            return self._try_promote_to_gold(triplet, source_count, force)

        # Already Gold or unknown tier
        else:
            return PromotionResult(
                triplet_id=triplet_id,
                old_tier=old_tier,
                new_tier=old_tier,
                promoted=False,
                reason=f"Already at tier '{old_tier}' or unknown tier"
            )

    def _try_promote_to_silver(
        self,
        triplet: SPOTriplet,
        source_count: int,
        force: bool
    ) -> PromotionResult:
        """Try to promote Bronze → Silver."""
        rules = self.BRONZE_TO_SILVER

        # Check source requirement
        if source_count < rules["min_sources"]:
            return PromotionResult(
                triplet_id=triplet.id,
                old_tier="bronze",
                new_tier="bronze",
                promoted=False,
                reason=f"Need {rules['min_sources']} sources, have {source_count}"
            )

        # Check confidence (unless forced)
        if not force and triplet.confidence < rules["min_confidence"]:
            return PromotionResult(
                triplet_id=triplet.id,
                old_tier="bronze",
                new_tier="bronze",
                promoted=False,
                reason=f"Confidence {triplet.confidence:.2f} below threshold {rules['min_confidence']}"
            )

        # Promote to Silver!
        success = self.graph.spo_db.update_tier(triplet.id, "silver")

        if success:
            return PromotionResult(
                triplet_id=triplet.id,
                old_tier="bronze",
                new_tier="silver",
                promoted=True,
                reason=f"Promoted with {source_count} sources, confidence {triplet.confidence:.2f}",
                promoted_at=datetime.utcnow().isoformat()
            )
        else:
            return PromotionResult(
                triplet_id=triplet.id,
                old_tier="bronze",
                new_tier="bronze",
                promoted=False,
                reason="Database update failed"
            )

    def _try_promote_to_gold(
        self,
        triplet: SPOTriplet,
        source_count: int,
        force: bool
    ) -> PromotionResult:
        """Try to promote Silver → Gold."""
        rules = self.SILVER_TO_GOLD

        # Check source requirement
        if source_count < rules["min_sources"]:
            return PromotionResult(
                triplet_id=triplet.id,
                old_tier="silver",
                new_tier="silver",
                promoted=False,
                reason=f"Need {rules['min_sources']} sources for Gold, have {source_count}"
            )

        # Check confidence (unless forced)
        if not force and triplet.confidence < rules["min_confidence"]:
            return PromotionResult(
                triplet_id=triplet.id,
                old_tier="silver",
                new_tier="silver",
                promoted=False,
                reason=f"Confidence {triplet.confidence:.2f} below Gold threshold {rules['min_confidence']}"
            )

        # Check axiom pass (if AxiomJudge available and required)
        if rules["requires_axiom_pass"] and self.axiom_judge and not force:
            # TODO: Call AxiomJudge when implemented
            return PromotionResult(
                triplet_id=triplet.id,
                old_tier="silver",
                new_tier="silver",
                promoted=False,
                reason="Axiom evaluation required but AxiomJudge not available yet"
            )

        # Promote to Gold!
        success = self.graph.spo_db.update_tier(triplet.id, "gold")

        if success:
            return PromotionResult(
                triplet_id=triplet.id,
                old_tier="silver",
                new_tier="gold",
                promoted=True,
                reason=f"Promoted to Gold with {source_count} sources, confidence {triplet.confidence:.2f}",
                promoted_at=datetime.utcnow().isoformat()
            )
        else:
            return PromotionResult(
                triplet_id=triplet.id,
                old_tier="silver",
                new_tier="silver",
                promoted=False,
                reason="Database update failed"
            )

    def auto_promote_batch(
        self,
        triplet_ids: List[str],
        force: bool = False
    ) -> Dict[str, Any]:
        """
        Batch promotion with statistics.

        Args:
            triplet_ids: List of triplet IDs to check
            force: Skip confidence/axiom checks

        Returns:
            Dict with results and stats:
            {
                "results": [PromotionResult, ...],
                "stats": {
                    "total": 10,
                    "promoted": 5,
                    "bronze_to_silver": 3,
                    "silver_to_gold": 2
                }
            }
        """
        results = []
        stats = {
            "total": len(triplet_ids),
            "promoted": 0,
            "bronze_to_silver": 0,
            "silver_to_gold": 0,
            "failed": 0
        }

        for triplet_id in triplet_ids:
            result = self.promote_if_eligible(triplet_id, force=force)
            results.append(result)

            if result.promoted:
                stats["promoted"] += 1

                if result.old_tier == "bronze" and result.new_tier == "silver":
                    stats["bronze_to_silver"] += 1
                elif result.old_tier == "silver" and result.new_tier == "gold":
                    stats["silver_to_gold"] += 1
            else:
                stats["failed"] += 1

        return {
            "results": results,
            "stats": stats
        }

    def get_promotion_candidates(
        self,
        target_tier: str = "silver"
    ) -> List[SPOTriplet]:
        """
        Find triplets eligible for promotion.

        Args:
            target_tier: Target tier ("silver" or "gold")

        Returns:
            List of eligible triplets
        """
        # Get all triplets
        all_triplets = self.graph.get_spo_triplets(limit=10000)

        candidates = []

        for triplet in all_triplets:
            source_count = len(triplet.provenance.verification_sources) + 1

            # Check Bronze → Silver candidates
            if target_tier == "silver" and triplet.tier == "bronze":
                if (source_count >= self.BRONZE_TO_SILVER["min_sources"] and
                    triplet.confidence >= self.BRONZE_TO_SILVER["min_confidence"]):
                    candidates.append(triplet)

            # Check Silver → Gold candidates
            elif target_tier == "gold" and triplet.tier == "silver":
                if (source_count >= self.SILVER_TO_GOLD["min_sources"] and
                    triplet.confidence >= self.SILVER_TO_GOLD["min_confidence"]):
                    candidates.append(triplet)

        return candidates

    def get_stats(self) -> Dict[str, Any]:
        """
        Get promotion statistics.

        Returns:
            Dict with tier distribution and promotion candidates
        """
        spo_stats = self.graph.get_spo_stats()

        # Find promotion candidates
        silver_candidates = len(self.get_promotion_candidates("silver"))
        gold_candidates = len(self.get_promotion_candidates("gold"))

        return {
            "tier_distribution": {
                "bronze": spo_stats.get("bronze_count", 0),
                "silver": spo_stats.get("silver_count", 0),
                "gold": spo_stats.get("gold_count", 0)
            },
            "promotion_candidates": {
                "silver": silver_candidates,
                "gold": gold_candidates
            },
            "rules": {
                "bronze_to_silver": self.BRONZE_TO_SILVER,
                "silver_to_gold": self.SILVER_TO_GOLD
            }
        }
