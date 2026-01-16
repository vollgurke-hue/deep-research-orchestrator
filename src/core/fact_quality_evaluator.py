"""
Fact Quality Evaluator - Evaluate node quality based on SPO triplet tiers.

Part of Cluster 3: MCTS + Tiered RAG Integration
Provides fact quality scores for MCTS node selection.

Design Philosophy:
- Gold facts are most valuable (weight: 1.0)
- Silver facts are verified (weight: 0.6)
- Bronze facts are raw extractions (weight: 0.3)
- Score: 0.0 (no facts) to 1.0 (all Gold)

Usage:
    evaluator = FactQualityEvaluator(graph_manager)

    # Evaluate single node
    score = evaluator.evaluate_node_facts(node_id)

    # Get detailed breakdown
    dist = evaluator.get_node_fact_distribution(node_id)
    # {"gold": 5, "silver": 10, "bronze": 20, "score": 0.486}
"""

from typing import Dict, Optional, List
import time

from src.core.graph_manager import GraphManager


class FactQualityEvaluator:
    """
    Evaluate node quality based on SPO triplet tiers.

    Used by MCTS to compute fact quality bonus in UCB1 formula.
    Higher quality facts (Gold > Silver > Bronze) lead to higher scores.

    Scoring Formula:
        weighted_sum = (gold_count * gold_weight +
                       silver_count * silver_weight +
                       bronze_count * bronze_weight)

        max_possible = total_facts * gold_weight

        score = weighted_sum / max_possible if total_facts > 0 else 0.0

    Where:
        gold_weight = 1.0    (maximum value)
        silver_weight = 0.6  (verified, but not axiom-checked)
        bronze_weight = 0.3  (raw extraction)

    Example:
        5 Gold + 10 Silver + 20 Bronze = 35 facts
        score = (5*1.0 + 10*0.6 + 20*0.3) / (35*1.0)
              = (5 + 6 + 6) / 35
              = 17 / 35
              = 0.486 (~49%)

    Performance:
        - Caching with TTL (60s default)
        - Database indexes on source_id
        - Target: <10ms per evaluation
    """

    # Tier weights (configurable)
    GOLD_WEIGHT = 1.0
    SILVER_WEIGHT = 0.6
    BRONZE_WEIGHT = 0.3

    def __init__(
        self,
        graph_manager: GraphManager,
        cache_ttl: int = 60,
        enable_caching: bool = True
    ):
        """
        Initialize Fact Quality Evaluator.

        Args:
            graph_manager: GraphManager with SPO database
            cache_ttl: Cache time-to-live in seconds (default: 60)
            enable_caching: Enable/disable caching (default: True)
        """
        self.graph = graph_manager
        self.cache_ttl = cache_ttl
        self.enable_caching = enable_caching

        # Cache: node_id -> (score, timestamp)
        self._score_cache: Dict[str, tuple[float, float]] = {}

        # Cache: node_id -> (distribution, timestamp)
        self._dist_cache: Dict[str, tuple[Dict, float]] = {}

        # Check dependencies
        if not hasattr(graph_manager, 'spo_db') or not graph_manager.spo_db:
            raise RuntimeError("GraphManager must have SPO database initialized")

    def evaluate_node_facts(self, node_id: str) -> float:
        """
        Evaluate node quality based on its SPO facts.

        Args:
            node_id: ToT node ID to evaluate

        Returns:
            Quality score 0.0-1.0
            - 0.0 = no facts
            - 0.3 = only Bronze facts
            - 0.6 = only Silver facts
            - 1.0 = only Gold facts
            - 0.486 = example mixed (5G + 10S + 20B)
        """
        # Check cache first
        if self.enable_caching and node_id in self._score_cache:
            score, timestamp = self._score_cache[node_id]
            if time.time() - timestamp < self.cache_ttl:
                return score  # Cache hit!

        # Calculate score
        distribution = self.get_node_fact_distribution(node_id)
        score = distribution['score']

        # Cache result
        if self.enable_caching:
            self._score_cache[node_id] = (score, time.time())

        return score

    def get_node_fact_distribution(self, node_id: str) -> Dict:
        """
        Get detailed fact distribution for node.

        Args:
            node_id: ToT node ID

        Returns:
            Dict with fact counts and score:
            {
                "gold": 5,
                "silver": 10,
                "bronze": 20,
                "total": 35,
                "score": 0.486,
                "weighted_sum": 17.0
            }
        """
        # Check cache first
        if self.enable_caching and node_id in self._dist_cache:
            dist, timestamp = self._dist_cache[node_id]
            if time.time() - timestamp < self.cache_ttl:
                return dist  # Cache hit!

        # Get facts for this node from SPO database
        facts = self._get_node_facts(node_id)

        # Count by tier
        gold_count = sum(1 for f in facts if f.tier == "gold")
        silver_count = sum(1 for f in facts if f.tier == "silver")
        bronze_count = sum(1 for f in facts if f.tier == "bronze")
        total_count = len(facts)

        # Calculate weighted score
        weighted_sum = (
            gold_count * self.GOLD_WEIGHT +
            silver_count * self.SILVER_WEIGHT +
            bronze_count * self.BRONZE_WEIGHT
        )

        # Normalize by maximum possible score
        max_possible = total_count * self.GOLD_WEIGHT if total_count > 0 else 1.0
        score = weighted_sum / max_possible if total_count > 0 else 0.0

        # Build result
        distribution = {
            "gold": gold_count,
            "silver": silver_count,
            "bronze": bronze_count,
            "total": total_count,
            "weighted_sum": weighted_sum,
            "score": score
        }

        # Cache result
        if self.enable_caching:
            self._dist_cache[node_id] = (distribution, time.time())

        return distribution

    def _get_node_facts(self, node_id: str) -> List:
        """
        Get all SPO triplets related to this node.

        A fact is related to a node if:
        - The fact was extracted from this node (source_id = node_id)
        - The fact was verified by this node (node_id in verification_sources)

        Args:
            node_id: ToT node ID

        Returns:
            List of SPOTriplet objects
        """
        try:
            # Get all triplets from database
            all_triplets = self.graph.get_spo_triplets(limit=10000)

            # Filter for this node
            node_facts = []
            for triplet in all_triplets:
                # Check if extracted from this node
                if triplet.provenance.source_id == node_id:
                    node_facts.append(triplet)
                    continue

                # Check if verified by this node
                if node_id in triplet.provenance.verification_sources:
                    node_facts.append(triplet)

            return node_facts

        except Exception as e:
            print(f"Warning: Failed to get facts for node {node_id}: {e}")
            return []

    def clear_cache(self):
        """Clear all caches."""
        self._score_cache.clear()
        self._dist_cache.clear()

    def get_cache_stats(self) -> Dict:
        """
        Get cache statistics.

        Returns:
            Dict with cache info:
            {
                "score_cache_size": 42,
                "dist_cache_size": 42,
                "cache_enabled": True,
                "cache_ttl": 60
            }
        """
        return {
            "score_cache_size": len(self._score_cache),
            "dist_cache_size": len(self._dist_cache),
            "cache_enabled": self.enable_caching,
            "cache_ttl": self.cache_ttl
        }

    def evaluate_batch(self, node_ids: List[str]) -> Dict[str, float]:
        """
        Batch evaluate multiple nodes for efficiency.

        Args:
            node_ids: List of node IDs to evaluate

        Returns:
            Dict mapping node_id -> score
        """
        results = {}
        for node_id in node_ids:
            results[node_id] = self.evaluate_node_facts(node_id)
        return results

    def get_tier_breakdown_summary(self) -> Dict:
        """
        Get summary statistics across all evaluated nodes.

        Useful for understanding overall knowledge base quality.

        Returns:
            Dict with summary:
            {
                "total_facts_evaluated": 350,
                "gold_count": 50,
                "silver_count": 100,
                "bronze_count": 200,
                "avg_quality_score": 0.514,
                "gold_percentage": 14.3,
                "silver_percentage": 28.6,
                "bronze_percentage": 57.1
            }
        """
        # Get all triplets from database
        all_triplets = self.graph.get_spo_triplets(limit=10000)

        if not all_triplets:
            return {
                "total_facts_evaluated": 0,
                "gold_count": 0,
                "silver_count": 0,
                "bronze_count": 0,
                "avg_quality_score": 0.0,
                "gold_percentage": 0.0,
                "silver_percentage": 0.0,
                "bronze_percentage": 0.0
            }

        # Count by tier
        gold_count = sum(1 for t in all_triplets if t.tier == "gold")
        silver_count = sum(1 for t in all_triplets if t.tier == "silver")
        bronze_count = sum(1 for t in all_triplets if t.tier == "bronze")
        total = len(all_triplets)

        # Calculate percentages
        gold_pct = (gold_count / total * 100) if total > 0 else 0.0
        silver_pct = (silver_count / total * 100) if total > 0 else 0.0
        bronze_pct = (bronze_count / total * 100) if total > 0 else 0.0

        # Calculate average quality score
        weighted_sum = (
            gold_count * self.GOLD_WEIGHT +
            silver_count * self.SILVER_WEIGHT +
            bronze_count * self.BRONZE_WEIGHT
        )
        avg_score = weighted_sum / (total * self.GOLD_WEIGHT) if total > 0 else 0.0

        return {
            "total_facts_evaluated": total,
            "gold_count": gold_count,
            "silver_count": silver_count,
            "bronze_count": bronze_count,
            "avg_quality_score": avg_score,
            "gold_percentage": gold_pct,
            "silver_percentage": silver_pct,
            "bronze_percentage": bronze_pct
        }
