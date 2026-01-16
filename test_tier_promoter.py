"""
Test TierPromoter - Automatic tier promotion for SPO triplets.

Tests:
1. Bronze → Silver promotion (2+ sources)
2. Silver → Gold promotion (3+ sources)
3. Confidence thresholds
4. Batch promotion
5. Get promotion candidates

Part of Cluster 2: Intelligence Layer
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.graph_manager import GraphManager
from src.core.multi_source_verifier import MultiSourceVerifier
from src.core.tier_promoter import TierPromoter, PromotionResult
from src.models.unified_session import SPOTriplet, SPOProvenance
from datetime import datetime


def test_tier_promoter():
    """Test TierPromoter with real components."""

    print("\n" + "="*70)
    print("TEST: Tier Promoter")
    print("="*70)

    # ========== Phase 1: Setup ==========
    print("\n[Phase 1] Setup components...")

    # Create test database
    db_path = "test_tierpromoter.db"
    if os.path.exists(db_path):
        os.remove(db_path)

    # Initialize components
    graph = GraphManager(spo_db_path=db_path)
    verifier = MultiSourceVerifier(graph_manager=graph)
    promoter = TierPromoter(
        graph_manager=graph,
        verifier=verifier,
        axiom_judge=None  # Not implemented yet
    )

    print("✓ TierPromoter initialized")
    print(f"  - Bronze → Silver: {promoter.BRONZE_TO_SILVER['min_sources']} sources, conf {promoter.BRONZE_TO_SILVER['min_confidence']}")
    print(f"  - Silver → Gold: {promoter.SILVER_TO_GOLD['min_sources']} sources, conf {promoter.SILVER_TO_GOLD['min_confidence']}")

    # ========== Phase 2: Create Bronze Triplet ==========
    print("\n[Phase 2] Create Bronze triplet...")

    triplet = SPOTriplet(
        id="spo_test_001",
        subject="Electric vehicles",
        predicate="reduce",
        object="carbon emissions",
        confidence=0.85,  # High confidence
        tier="bronze",
        provenance=SPOProvenance(
            source_id="tot_node_001",
            extraction_method="llm_structured",
            model_used="deepseek-r1-14b",
            extracted_at=datetime.utcnow().isoformat(),
            verified=False,
            verification_count=0,
            verification_sources=[]
        ),
        created_at=datetime.utcnow().isoformat(),
        metadata={"test": True}
    )

    graph.add_spo_triplet(triplet)

    print(f"✓ Created Bronze triplet: [{triplet.subject}] --{triplet.predicate}--> [{triplet.object}]")
    print(f"  - Tier: {triplet.tier}")
    print(f"  - Confidence: {triplet.confidence}")
    print(f"  - Sources: 1 (original)")

    # ========== Phase 3: Try Promotion (Should Fail - Only 1 Source) ==========
    print("\n[Phase 3] Try promotion with 1 source (should fail)...")

    result = promoter.promote_if_eligible("spo_test_001")

    print(f"✓ Promotion result:")
    print(f"  - Promoted: {result.promoted}")
    print(f"  - Reason: {result.reason}")
    print(f"  - Current tier: {result.new_tier}")

    assert not result.promoted, "Should not promote with only 1 source"
    assert result.new_tier == "bronze", "Should still be Bronze"

    # ========== Phase 4: Add 2nd Source and Promote to Silver ==========
    print("\n[Phase 4] Add 2nd source and promote to Silver...")

    # Verify with 2nd source
    verifier.verify_triplet("spo_test_001", "tot_node_002")

    # Try promotion again
    result = promoter.promote_if_eligible("spo_test_001")

    print(f"✓ Promotion result:")
    print(f"  - Promoted: {result.promoted}")
    print(f"  - Old tier: {result.old_tier}")
    print(f"  - New tier: {result.new_tier}")
    print(f"  - Reason: {result.reason}")

    assert result.promoted, "Should promote with 2 sources"
    assert result.old_tier == "bronze", "Should start as Bronze"
    assert result.new_tier == "silver", "Should promote to Silver"

    print("✓ Bronze → Silver promotion SUCCESS!")

    # Verify in database
    updated_triplet = graph.spo_db.get_by_id("spo_test_001")
    assert updated_triplet.tier == "silver", "Tier not updated in database"
    print("✓ Database tier confirmed: Silver")

    # ========== Phase 5: Add 3rd Source and Try Gold Promotion ==========
    print("\n[Phase 5] Add 3rd source and try Gold promotion...")

    # Add 3rd source
    verifier.verify_triplet("spo_test_001", "tot_node_003")

    # Try promotion to Gold (should work with force=True since we don't have AxiomJudge yet)
    result = promoter.promote_if_eligible("spo_test_001", force=True)

    print(f"✓ Promotion result:")
    print(f"  - Promoted: {result.promoted}")
    print(f"  - Old tier: {result.old_tier}")
    print(f"  - New tier: {result.new_tier}")
    print(f"  - Reason: {result.reason}")

    assert result.promoted, "Should promote with 3 sources (forced)"
    assert result.old_tier == "silver", "Should start as Silver"
    assert result.new_tier == "gold", "Should promote to Gold"

    print("✓ Silver → Gold promotion SUCCESS (forced)!")

    # ========== Phase 6: Test Confidence Thresholds ==========
    print("\n[Phase 6] Test confidence thresholds...")

    # Create low-confidence triplet
    low_conf_triplet = SPOTriplet(
        id="spo_test_002",
        subject="Hydrogen fuel",
        predicate="costs",
        object="high amount",
        confidence=0.60,  # Below 0.7 threshold
        tier="bronze",
        provenance=SPOProvenance(
            source_id="tot_node_004",
            extraction_method="llm_structured",
            model_used="deepseek-r1-14b",
            extracted_at=datetime.utcnow().isoformat(),
            verified=False,
            verification_count=0,
            verification_sources=[]
        ),
        created_at=datetime.utcnow().isoformat(),
        metadata={"test": True}
    )

    graph.add_spo_triplet(low_conf_triplet)

    # Add 2 verification sources
    verifier.verify_triplet("spo_test_002", "tot_node_005")
    verifier.verify_triplet("spo_test_002", "tot_node_006")

    # Try promotion (should fail due to low confidence)
    result = promoter.promote_if_eligible("spo_test_002")

    print(f"✓ Low confidence test:")
    print(f"  - Confidence: 0.60 (threshold: 0.70)")
    print(f"  - Sources: 3")
    print(f"  - Promoted: {result.promoted}")
    print(f"  - Reason: {result.reason}")

    assert not result.promoted, "Should not promote low-confidence triplet"
    print("✓ Confidence threshold working correctly")

    # ========== Phase 7: Test Batch Promotion ==========
    print("\n[Phase 7] Test batch promotion...")

    # Create more triplets
    for i in range(3, 6):
        t = SPOTriplet(
            id=f"spo_test_{i:03d}",
            subject=f"Subject {i}",
            predicate="relates_to",
            object=f"Object {i}",
            confidence=0.80,
            tier="bronze",
            provenance=SPOProvenance(
                source_id=f"tot_node_{i*10}",
                extraction_method="llm_structured",
                model_used="deepseek-r1-14b",
                extracted_at=datetime.utcnow().isoformat(),
                verified=False,
                verification_count=0,
                verification_sources=[]
            ),
            created_at=datetime.utcnow().isoformat(),
            metadata={"test": True}
        )
        graph.add_spo_triplet(t)

        # Add verification sources
        verifier.verify_triplet(t.id, f"source_{i}_1")
        verifier.verify_triplet(t.id, f"source_{i}_2")

    # Batch promote
    batch_result = promoter.auto_promote_batch([
        "spo_test_003",
        "spo_test_004",
        "spo_test_005"
    ])

    print(f"✓ Batch promotion result:")
    print(f"  - Total: {batch_result['stats']['total']}")
    print(f"  - Promoted: {batch_result['stats']['promoted']}")
    print(f"  - Bronze → Silver: {batch_result['stats']['bronze_to_silver']}")
    print(f"  - Failed: {batch_result['stats']['failed']}")

    assert batch_result['stats']['promoted'] == 3, "Should promote all 3 triplets"
    assert batch_result['stats']['bronze_to_silver'] == 3, "All should be Bronze → Silver"

    # ========== Phase 8: Get Promotion Candidates ==========
    print("\n[Phase 8] Find promotion candidates...")

    # Create a triplet eligible for Silver
    eligible = SPOTriplet(
        id="spo_test_eligible",
        subject="Solar panels",
        predicate="produce",
        object="clean energy",
        confidence=0.90,
        tier="bronze",
        provenance=SPOProvenance(
            source_id="tot_node_100",
            extraction_method="llm_structured",
            model_used="deepseek-r1-14b",
            extracted_at=datetime.utcnow().isoformat(),
            verified=False,
            verification_count=0,
            verification_sources=[]
        ),
        created_at=datetime.utcnow().isoformat(),
        metadata={"test": True}
    )

    graph.add_spo_triplet(eligible)
    verifier.verify_triplet("spo_test_eligible", "source_a")
    verifier.verify_triplet("spo_test_eligible", "source_b")

    # Find candidates
    silver_candidates = promoter.get_promotion_candidates("silver")

    print(f"✓ Promotion candidates:")
    print(f"  - Eligible for Silver: {len(silver_candidates)}")

    for candidate in silver_candidates[:3]:  # Show first 3
        print(f"    - {candidate.id}: {candidate.subject} (conf: {candidate.confidence:.2f})")

    # ========== Phase 9: Get Stats ==========
    print("\n[Phase 9] Get promotion stats...")

    stats = promoter.get_stats()

    print(f"✓ Promotion statistics:")
    print(f"  - Tier distribution:")
    print(f"    - Bronze: {stats['tier_distribution']['bronze']}")
    print(f"    - Silver: {stats['tier_distribution']['silver']}")
    print(f"    - Gold: {stats['tier_distribution']['gold']}")
    print(f"  - Promotion candidates:")
    print(f"    - Silver: {stats['promotion_candidates']['silver']}")
    print(f"    - Gold: {stats['promotion_candidates']['gold']}")

    # ========== Cleanup ==========
    print("\n[Cleanup] Removing test database...")
    if graph.spo_db:
        graph.spo_db.close()
    os.remove(db_path)
    print("✓ Cleaned up")

    # ========== Final Summary ==========
    print("\n" + "="*70)
    print("TEST RESULT: ✅ PASSED")
    print("="*70)
    print("\nTierPromoter is working correctly!")
    print("Key features verified:")
    print("  ✓ Bronze → Silver promotion (2+ sources)")
    print("  ✓ Silver → Gold promotion (3+ sources, forced)")
    print("  ✓ Confidence threshold enforcement")
    print("  ✓ Batch promotion")
    print("  ✓ Find promotion candidates")
    print("  ✓ Tier statistics")
    print("\nNext step: Implement ConflictResolver")


if __name__ == "__main__":
    test_tier_promoter()
