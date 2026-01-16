"""
Conflict Resolver - Detect and resolve contradicting SPO triplets.

Part of Cluster 2: Intelligence Layer
Handles conflicts between triplets with contradictory information.

Design Philosophy:
- Automatic conflict detection based on semantic rules
- Multiple resolution strategies (confidence, sources, recency, manual)
- Conflict logging for transparency
- Preserves higher-quality information
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from src.core.graph_manager import GraphManager
from src.models.unified_session import SPOTriplet


class ConflictType(Enum):
    """Types of conflicts between triplets."""
    CONTRADICTION = "contradiction"  # Same S+P, opposite O
    SEMANTIC_OPPOSITE = "semantic_opposite"  # Same S+P, semantically opposite O
    NEGATION = "negation"  # S+P vs S+NOT_P
    VALUE_CONFLICT = "value_conflict"  # Same S+P, different numeric values


class ResolutionStrategy(Enum):
    """Strategies for resolving conflicts."""
    CONFIDENCE = "confidence"  # Keep higher confidence
    SOURCES = "sources"  # Keep more sources
    RECENCY = "recency"  # Keep newer
    TIER = "tier"  # Keep higher tier
    MANUAL = "manual"  # Flag for human review


@dataclass
class Conflict:
    """Detected conflict between two triplets."""
    id: str
    triplet_a: SPOTriplet
    triplet_b: SPOTriplet
    conflict_type: ConflictType
    severity: float  # 0.0-1.0 (1.0 = high severity)
    detected_at: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class Resolution:
    """Result of conflict resolution."""
    conflict: Conflict
    strategy_used: ResolutionStrategy
    kept_triplet_id: str
    removed_triplet_id: Optional[str]
    reasoning: str
    resolved_at: str
    manual_review_needed: bool = False


class ConflictResolver:
    """
    Detect and Resolve Contradicting SPO Triplets.

    Conflict Detection:
    1. Same subject + predicate, different object
    2. Negation predicates (is vs is_not, has vs lacks)
    3. Semantic opposites (high vs low, yes vs no)

    Resolution Strategies:
    1. Confidence-based: Keep higher confidence triplet
    2. Source-based: Keep triplet with more verification sources
    3. Recency-based: Keep newer triplet (for time-sensitive facts)
    4. Tier-based: Keep higher tier (Gold > Silver > Bronze)
    5. Manual: Flag for human review

    Usage:
        resolver = ConflictResolver(graph_manager)

        # Detect conflicts for a triplet
        conflicts = resolver.detect_conflicts(triplet)

        # Resolve conflict
        resolution = resolver.resolve_conflict(
            conflict,
            strategy=ResolutionStrategy.CONFIDENCE
        )

        # Auto-resolve all conflicts
        results = resolver.auto_resolve_all()
    """

    # Semantic opposite pairs
    OPPOSITE_PAIRS = [
        {"high", "low"},
        {"yes", "no"},
        {"true", "false"},
        {"increase", "decrease"},
        {"up", "down"},
        {"good", "bad"},
        {"positive", "negative"},
        {"expensive", "cheap"},
        {"hot", "cold"},
        {"fast", "slow"}
    ]

    # Negation predicate pairs
    NEGATION_PAIRS = [
        ("is", "is_not"),
        ("has", "lacks"),
        ("contains", "excludes"),
        ("supports", "opposes"),
        ("includes", "omits")
    ]

    def __init__(
        self,
        graph_manager: GraphManager,
        conflict_threshold: float = 0.7
    ):
        """
        Initialize Conflict Resolver.

        Args:
            graph_manager: GraphManager with SPO database
            conflict_threshold: Minimum severity to consider as conflict
        """
        self.graph = graph_manager
        self.conflict_threshold = conflict_threshold

        # Check dependencies
        if not hasattr(graph_manager, 'spo_db') or not graph_manager.spo_db:
            raise RuntimeError("GraphManager must have SPO database initialized")

        # Conflict cache (in production, use database)
        self._detected_conflicts: Dict[str, Conflict] = {}

    def detect_conflicts(
        self,
        triplet: SPOTriplet,
        check_all: bool = False
    ) -> List[Conflict]:
        """
        Detect conflicts for a triplet.

        Args:
            triplet: SPO triplet to check
            check_all: If True, check against all triplets (slower)

        Returns:
            List of detected conflicts
        """
        conflicts = []

        # Get all triplets (TODO: optimize with index on subject)
        all_triplets = self.graph.get_spo_triplets(limit=10000)

        for other in all_triplets:
            if other.id == triplet.id:
                continue  # Skip self

            # Check for different conflict types
            conflict = self._check_conflict(triplet, other)

            if conflict and conflict.severity >= self.conflict_threshold:
                conflicts.append(conflict)

        return conflicts

    def _check_conflict(
        self,
        triplet_a: SPOTriplet,
        triplet_b: SPOTriplet
    ) -> Optional[Conflict]:
        """
        Check if two triplets conflict.

        Returns:
            Conflict object if conflict detected, None otherwise
        """
        # Normalize for comparison
        subj_a = triplet_a.subject.lower().strip()
        pred_a = triplet_a.predicate.lower().strip()
        obj_a = triplet_a.object.lower().strip()

        subj_b = triplet_b.subject.lower().strip()
        pred_b = triplet_b.predicate.lower().strip()
        obj_b = triplet_b.object.lower().strip()

        # Must have same subject
        if not self._is_same_subject(subj_a, subj_b):
            return None

        # Check Type 1: Same predicate, opposite object
        if self._is_same_predicate(pred_a, pred_b):
            if self._is_opposite_object(obj_a, obj_b):
                return Conflict(
                    id=f"conflict_{triplet_a.id}_{triplet_b.id}",
                    triplet_a=triplet_a,
                    triplet_b=triplet_b,
                    conflict_type=ConflictType.SEMANTIC_OPPOSITE,
                    severity=0.9,
                    detected_at=datetime.utcnow().isoformat(),
                    metadata={
                        "subject": subj_a,
                        "predicate": pred_a,
                        "object_a": obj_a,
                        "object_b": obj_b
                    }
                )

            # Check for value conflict (numeric)
            if self._is_numeric_conflict(obj_a, obj_b):
                return Conflict(
                    id=f"conflict_{triplet_a.id}_{triplet_b.id}",
                    triplet_a=triplet_a,
                    triplet_b=triplet_b,
                    conflict_type=ConflictType.VALUE_CONFLICT,
                    severity=0.75,
                    detected_at=datetime.utcnow().isoformat(),
                    metadata={
                        "subject": subj_a,
                        "predicate": pred_a,
                        "value_a": obj_a,
                        "value_b": obj_b
                    }
                )

        # Check Type 2: Negation predicates
        if self._is_negation_pair(pred_a, pred_b):
            return Conflict(
                id=f"conflict_{triplet_a.id}_{triplet_b.id}",
                triplet_a=triplet_a,
                triplet_b=triplet_b,
                conflict_type=ConflictType.NEGATION,
                severity=1.0,  # High severity
                detected_at=datetime.utcnow().isoformat(),
                metadata={
                    "subject": subj_a,
                    "predicate_a": pred_a,
                    "predicate_b": pred_b,
                    "object_a": obj_a,
                    "object_b": obj_b
                }
            )

        return None

    def _is_same_subject(self, subj_a: str, subj_b: str) -> bool:
        """Check if subjects are the same (exact or fuzzy match)."""
        # Exact match
        if subj_a == subj_b:
            return True

        # Fuzzy match (one contains the other)
        if subj_a in subj_b or subj_b in subj_a:
            return True

        return False

    def _is_same_predicate(self, pred_a: str, pred_b: str) -> bool:
        """Check if predicates are the same."""
        return pred_a == pred_b

    def _is_opposite_object(self, obj_a: str, obj_b: str) -> bool:
        """Check if objects are semantic opposites."""
        # Check against known opposite pairs
        for pair in self.OPPOSITE_PAIRS:
            if obj_a in pair and obj_b in pair and obj_a != obj_b:
                return True

        return False

    def _is_negation_pair(self, pred_a: str, pred_b: str) -> bool:
        """Check if predicates are negation pairs."""
        for pos, neg in self.NEGATION_PAIRS:
            if (pred_a == pos and pred_b == neg) or (pred_a == neg and pred_b == pos):
                return True

        return False

    def _is_numeric_conflict(self, obj_a: str, obj_b: str) -> bool:
        """Check if objects are conflicting numeric values."""
        try:
            # Extract numeric values
            import re
            nums_a = re.findall(r'\d+\.?\d*', obj_a)
            nums_b = re.findall(r'\d+\.?\d*', obj_b)

            if nums_a and nums_b:
                val_a = float(nums_a[0])
                val_b = float(nums_b[0])

                # Conflict if difference > 20%
                avg = (val_a + val_b) / 2
                diff_pct = abs(val_a - val_b) / avg if avg > 0 else 0

                return diff_pct > 0.2

        except (ValueError, IndexError):
            pass

        return False

    def resolve_conflict(
        self,
        conflict: Conflict,
        strategy: ResolutionStrategy = ResolutionStrategy.CONFIDENCE
    ) -> Resolution:
        """
        Resolve conflict using specified strategy.

        Args:
            conflict: Conflict to resolve
            strategy: Resolution strategy to use

        Returns:
            Resolution result
        """
        triplet_a = conflict.triplet_a
        triplet_b = conflict.triplet_b

        # Apply strategy
        if strategy == ResolutionStrategy.CONFIDENCE:
            return self._resolve_by_confidence(conflict)

        elif strategy == ResolutionStrategy.SOURCES:
            return self._resolve_by_sources(conflict)

        elif strategy == ResolutionStrategy.RECENCY:
            return self._resolve_by_recency(conflict)

        elif strategy == ResolutionStrategy.TIER:
            return self._resolve_by_tier(conflict)

        elif strategy == ResolutionStrategy.MANUAL:
            return Resolution(
                conflict=conflict,
                strategy_used=strategy,
                kept_triplet_id=triplet_a.id,  # Keep first by default
                removed_triplet_id=None,  # Don't remove
                reasoning="Flagged for manual review",
                resolved_at=datetime.utcnow().isoformat(),
                manual_review_needed=True
            )

        else:
            raise ValueError(f"Unknown strategy: {strategy}")

    def _resolve_by_confidence(self, conflict: Conflict) -> Resolution:
        """Resolve by keeping higher confidence triplet."""
        triplet_a = conflict.triplet_a
        triplet_b = conflict.triplet_b

        if triplet_a.confidence > triplet_b.confidence:
            kept = triplet_a.id
            removed = triplet_b.id
            reason = f"Kept higher confidence: {triplet_a.confidence:.2f} > {triplet_b.confidence:.2f}"
        elif triplet_b.confidence > triplet_a.confidence:
            kept = triplet_b.id
            removed = triplet_a.id
            reason = f"Kept higher confidence: {triplet_b.confidence:.2f} > {triplet_a.confidence:.2f}"
        else:
            # Equal confidence - keep first, flag for manual review
            kept = triplet_a.id
            removed = None
            reason = f"Equal confidence ({triplet_a.confidence:.2f}) - needs manual review"
            return Resolution(
                conflict=conflict,
                strategy_used=ResolutionStrategy.CONFIDENCE,
                kept_triplet_id=kept,
                removed_triplet_id=removed,
                reasoning=reason,
                resolved_at=datetime.utcnow().isoformat(),
                manual_review_needed=True
            )

        return Resolution(
            conflict=conflict,
            strategy_used=ResolutionStrategy.CONFIDENCE,
            kept_triplet_id=kept,
            removed_triplet_id=removed,
            reasoning=reason,
            resolved_at=datetime.utcnow().isoformat()
        )

    def _resolve_by_sources(self, conflict: Conflict) -> Resolution:
        """Resolve by keeping triplet with more sources."""
        triplet_a = conflict.triplet_a
        triplet_b = conflict.triplet_b

        sources_a = len(triplet_a.provenance.verification_sources) + 1
        sources_b = len(triplet_b.provenance.verification_sources) + 1

        if sources_a > sources_b:
            kept = triplet_a.id
            removed = triplet_b.id
            reason = f"Kept more sources: {sources_a} > {sources_b}"
        elif sources_b > sources_a:
            kept = triplet_b.id
            removed = triplet_a.id
            reason = f"Kept more sources: {sources_b} > {sources_a}"
        else:
            # Equal sources - fallback to confidence
            return self._resolve_by_confidence(conflict)

        return Resolution(
            conflict=conflict,
            strategy_used=ResolutionStrategy.SOURCES,
            kept_triplet_id=kept,
            removed_triplet_id=removed,
            reasoning=reason,
            resolved_at=datetime.utcnow().isoformat()
        )

    def _resolve_by_recency(self, conflict: Conflict) -> Resolution:
        """Resolve by keeping newer triplet."""
        triplet_a = conflict.triplet_a
        triplet_b = conflict.triplet_b

        # Compare timestamps
        if triplet_a.created_at > triplet_b.created_at:
            kept = triplet_a.id
            removed = triplet_b.id
            reason = f"Kept newer triplet: {triplet_a.created_at} > {triplet_b.created_at}"
        else:
            kept = triplet_b.id
            removed = triplet_a.id
            reason = f"Kept newer triplet: {triplet_b.created_at} >= {triplet_a.created_at}"

        return Resolution(
            conflict=conflict,
            strategy_used=ResolutionStrategy.RECENCY,
            kept_triplet_id=kept,
            removed_triplet_id=removed,
            reasoning=reason,
            resolved_at=datetime.utcnow().isoformat()
        )

    def _resolve_by_tier(self, conflict: Conflict) -> Resolution:
        """Resolve by keeping higher tier triplet."""
        triplet_a = conflict.triplet_a
        triplet_b = conflict.triplet_b

        tier_order = {"gold": 3, "silver": 2, "bronze": 1}
        tier_a = tier_order.get(triplet_a.tier, 0)
        tier_b = tier_order.get(triplet_b.tier, 0)

        if tier_a > tier_b:
            kept = triplet_a.id
            removed = triplet_b.id
            reason = f"Kept higher tier: {triplet_a.tier} > {triplet_b.tier}"
        elif tier_b > tier_a:
            kept = triplet_b.id
            removed = triplet_a.id
            reason = f"Kept higher tier: {triplet_b.tier} > {triplet_a.tier}"
        else:
            # Equal tier - fallback to confidence
            return self._resolve_by_confidence(conflict)

        return Resolution(
            conflict=conflict,
            strategy_used=ResolutionStrategy.TIER,
            kept_triplet_id=kept,
            removed_triplet_id=removed,
            reasoning=reason,
            resolved_at=datetime.utcnow().isoformat()
        )

    def auto_resolve_all(
        self,
        strategy: ResolutionStrategy = ResolutionStrategy.TIER,
        delete_losers: bool = False
    ) -> Dict[str, Any]:
        """
        Auto-resolve all detected conflicts.

        Args:
            strategy: Default resolution strategy
            delete_losers: If True, delete losing triplets from database

        Returns:
            Dict with results and stats
        """
        # Get all triplets
        all_triplets = self.graph.get_spo_triplets(limit=10000)

        # Detect all conflicts
        all_conflicts = []
        checked_pairs = set()

        for triplet in all_triplets:
            conflicts = self.detect_conflicts(triplet)

            for conflict in conflicts:
                # Avoid duplicate conflicts (A-B and B-A)
                pair_id = tuple(sorted([conflict.triplet_a.id, conflict.triplet_b.id]))
                if pair_id not in checked_pairs:
                    all_conflicts.append(conflict)
                    checked_pairs.add(pair_id)

        # Resolve all conflicts
        resolutions = []
        stats = {
            "total_conflicts": len(all_conflicts),
            "resolved": 0,
            "manual_review": 0,
            "deleted": 0
        }

        for conflict in all_conflicts:
            resolution = self.resolve_conflict(conflict, strategy=strategy)
            resolutions.append(resolution)

            if resolution.manual_review_needed:
                stats["manual_review"] += 1
            else:
                stats["resolved"] += 1

                # Delete loser if requested
                if delete_losers and resolution.removed_triplet_id:
                    self.graph.spo_db.delete(resolution.removed_triplet_id)
                    stats["deleted"] += 1

        return {
            "conflicts": all_conflicts,
            "resolutions": resolutions,
            "stats": stats
        }

    def get_stats(self) -> Dict[str, Any]:
        """
        Get conflict statistics.

        Returns:
            Dict with conflict stats
        """
        # Detect all conflicts
        result = self.auto_resolve_all(strategy=ResolutionStrategy.MANUAL, delete_losers=False)

        # Count by type
        by_type = {}
        for conflict in result["conflicts"]:
            conflict_type = conflict.conflict_type.value
            by_type[conflict_type] = by_type.get(conflict_type, 0) + 1

        return {
            "total_conflicts": result["stats"]["total_conflicts"],
            "by_type": by_type,
            "conflict_threshold": self.conflict_threshold
        }
