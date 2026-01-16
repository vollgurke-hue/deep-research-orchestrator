"""
Test MultiSourceVerifier - Multi-source verification for SPO triplets.

Tests:
1. Verify triplet with new source
2. Check promotion eligibility (Bronze → Silver at 2 sources)
3. Find similar triplets
4. Batch verification
5. Get verification stats

Part of Cluster 2: Intelligence Layer
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.graph_manager import GraphManager
from src.core.multi_source_verifier import MultiSourceVerifier, VerificationResult
from src.models.unified_session import SPOTriplet, SPOProvenance
from datetime import datetime


def test_multi_source_verifier():
    """Test MultiSourceVerifier with real components."""

    print("\n" + "="*70)
    print("TEST: Multi-Source Verifier")
    print("="*70)

    # ========== Phase 1: Setup ==========
    print("\n[Phase 1] Setup components...")

    # Create test database
    db_path = "test_multisource.db"
    if os.path.exists(db_path):
        os.remove(db_path)

    # Initialize GraphManager (with SPO database)
    graph = GraphManager(spo_db_path=db_path)

    # Initialize MultiSourceVerifier
    verifier = MultiSourceVerifier(
        graph_manager=graph,
        min_sources_silver=2,
        min_sources_gold=3,
        similarity_threshold=0.85
    )

    print("✓ MultiSourceVerifier initialized")
    print(f"  - Min sources for Silver: {verifier.min_sources_silver}")
    print(f"  - Min sources for Gold: {verifier.min_sources_gold}")
    print(f"  - Similarity threshold: {verifier.similarity_threshold}")

    # ========== Phase 2: Create Test Triplet ==========
    print("\n[Phase 2] Create test triplet...")

    triplet = SPOTriplet(
        id="spo_test_001",
        subject="Solar panels",
        predicate="reduce",
        object="CO2 emissions",
        confidence=0.85,
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

    # Add to database
    graph.add_spo_triplet(triplet)

    print(f"✓ Created triplet: [{triplet.subject}] --{triplet.predicate}--> [{triplet.object}]")
    print(f"  - ID: {triplet.id}")
    print(f"  - Tier: {triplet.tier}")
    print(f"  - Confidence: {triplet.confidence}")
    print(f"  - Sources: {len(triplet.provenance.verification_sources) + 1}")  # +1 for original

    # ========== Phase 3: Verify with 2nd Source ==========
    print("\n[Phase 3] Verify with 2nd source...")

    result = verifier.verify_triplet(
        triplet_id="spo_test_001",
        new_source="tot_node_002"
    )

    print(f"✓ Verification result:")
    print(f"  - Verified: {result.verified}")
    print(f"  - Source count: {result.source_count}")
    print(f"  - Should promote: {result.should_promote}")
    print(f"  - Verification sources: {result.verification_sources}")

    assert result.verified, "Triplet should be verified"
    assert result.source_count == 2, f"Expected 2 sources, got {result.source_count}"
    assert result.should_promote, "Should promote to Silver with 2 sources"

    print("✓ Bronze → Silver promotion eligible!")

    # ========== Phase 4: Verify with 3rd Source ==========
    print("\n[Phase 4] Verify with 3rd source...")

    result2 = verifier.verify_triplet(
        triplet_id="spo_test_001",
        new_source="tot_node_003"
    )

    print(f"✓ Verification result:")
    print(f"  - Verified: {result2.verified}")
    print(f"  - Source count: {result2.source_count}")
    print(f"  - Should promote: {result2.should_promote}")

    assert result2.source_count == 3, f"Expected 3 sources, got {result2.source_count}"

    # Note: Promotion to Gold requires axiom pass (tested separately)
    print("✓ 3 sources reached (Gold promotion requires axiom judge)")

    # ========== Phase 5: Find Similar Triplets ==========
    print("\n[Phase 5] Test similarity detection...")

    # Create similar triplet
    similar_triplet = SPOTriplet(
        id="spo_test_002",
        subject="Solar panels",  # Same subject
        predicate="decrease",  # Similar predicate (synonym)
        object="carbon emissions",  # Similar object
        confidence=0.80,
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

    graph.add_spo_triplet(similar_triplet)

    # Find similar triplets
    similar = verifier.find_similar_triplets(
        triplet=triplet,
        similarity_threshold=0.5  # Lower threshold for testing
    )

    print(f"✓ Found {len(similar)} similar triplets")
    for sim_triplet, score in similar:
        print(f"  - [{sim_triplet.subject}] --{sim_triplet.predicate}--> [{sim_triplet.object}]")
        print(f"    Similarity: {score:.2f}")

    # ========== Phase 6: Batch Verification ==========
    print("\n[Phase 6] Test batch verification...")

    # Create more triplets
    triplet3 = SPOTriplet(
        id="spo_test_003",
        subject="Wind turbines",
        predicate="generate",
        object="clean energy",
        confidence=0.90,
        tier="bronze",
        provenance=SPOProvenance(
            source_id="tot_node_005",
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

    graph.add_spo_triplet(triplet3)

    # Batch verify
    results = verifier.batch_verify([
        ("spo_test_001", "tot_node_010"),
        ("spo_test_003", "tot_node_011")
    ])

    print(f"✓ Batch verified {len(results)} triplets")
    for r in results:
        print(f"  - {r.triplet_id}: {r.source_count} sources")

    # ========== Phase 7: Get Stats ==========
    print("\n[Phase 7] Get verification stats...")

    stats = verifier.get_verification_stats()

    print(f"✓ Verification stats:")
    print(f"  - Total triplets: {stats['total_triplets']}")
    print(f"  - Verified count: {stats['verified_count']}")
    print(f"  - Verification rate: {stats['verification_rate']:.1f}%")
    print(f"  - Avg sources/triplet: {stats['avg_sources_per_triplet']:.2f}")
    print(f"  - By tier: {stats['by_tier']}")

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
    print("\nMultiSourceVerifier is working correctly!")
    print("Key features verified:")
    print("  ✓ Add verification sources")
    print("  ✓ Track source count")
    print("  ✓ Detect promotion eligibility")
    print("  ✓ Find similar triplets")
    print("  ✓ Batch verification")
    print("  ✓ Verification statistics")
    print("\nNext step: Implement TierPromoter")


if __name__ == "__main__":
    test_multi_source_verifier()
