"""
Test FactQualityEvaluator - Node quality evaluation based on SPO tiers.

Tests:
1. Evaluate node with only Gold facts (score ~1.0)
2. Evaluate node with only Silver facts (score ~0.6)
3. Evaluate node with only Bronze facts (score ~0.3)
4. Evaluate node with mixed facts (score ~0.5)
5. Evaluate node with no facts (score 0.0)
6. Caching works correctly
7. Batch evaluation
8. Tier breakdown summary

Part of Cluster 3: MCTS + Tiered RAG Integration
"""

import os
import sys
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.graph_manager import GraphManager
from src.core.fact_quality_evaluator import FactQualityEvaluator
from src.models.unified_session import SPOTriplet, SPOProvenance
from datetime import datetime


def test_fact_quality_evaluator():
    """Test FactQualityEvaluator with various fact distributions."""

    print("\n" + "="*70)
    print("TEST: Fact Quality Evaluator")
    print("="*70)

    # ========== Phase 1: Setup ==========
    print("\n[Phase 1] Setup components...")

    # Create test database
    db_path = "test_fact_evaluator.db"
    if os.path.exists(db_path):
        os.remove(db_path)

    # Initialize GraphManager with SPO database
    graph = GraphManager(spo_db_path=db_path)
    print("✓ GraphManager initialized")

    # Initialize FactQualityEvaluator
    evaluator = FactQualityEvaluator(
        graph_manager=graph,
        cache_ttl=60,
        enable_caching=True
    )
    print("✓ FactQualityEvaluator initialized")
    print(f"  - Cache TTL: {evaluator.cache_ttl}s")
    print(f"  - Gold weight: {evaluator.GOLD_WEIGHT}")
    print(f"  - Silver weight: {evaluator.SILVER_WEIGHT}")
    print(f"  - Bronze weight: {evaluator.BRONZE_WEIGHT}")

    # ========== Phase 2: Node with Only Gold Facts ==========
    print("\n[Phase 2] Test node with only Gold facts...")

    # Create 5 Gold facts for node_gold
    for i in range(5):
        triplet = SPOTriplet(
            id=f"spo_gold_{i}",
            subject=f"Gold Subject {i}",
            predicate="is",
            object=f"Gold Object {i}",
            confidence=0.95,
            tier="gold",  # GOLD!
            provenance=SPOProvenance(
                source_id="node_gold",  # From node_gold
                extraction_method="llm_structured",
                model_used="deepseek-r1-14b",
                extracted_at=datetime.utcnow().isoformat(),
                verified=True,
                verification_count=3,
                verification_sources=["s1", "s2", "s3"]
            ),
            created_at=datetime.utcnow().isoformat(),
            metadata={"test": True}
        )
        graph.add_spo_triplet(triplet)

    # Evaluate
    score_gold = evaluator.evaluate_node_facts("node_gold")
    dist_gold = evaluator.get_node_fact_distribution("node_gold")

    print(f"\n✓ Node with 5 Gold facts:")
    print(f"  - Score: {score_gold:.3f} (expected: 1.0)")
    print(f"  - Distribution: {dist_gold}")

    assert score_gold == 1.0, f"Expected 1.0, got {score_gold}"
    assert dist_gold['gold'] == 5
    assert dist_gold['total'] == 5
    print("✓ Gold-only score correct!")

    # ========== Phase 3: Node with Only Silver Facts ==========
    print("\n[Phase 3] Test node with only Silver facts...")

    # Create 10 Silver facts for node_silver
    for i in range(10):
        triplet = SPOTriplet(
            id=f"spo_silver_{i}",
            subject=f"Silver Subject {i}",
            predicate="has",
            object=f"Silver Object {i}",
            confidence=0.80,
            tier="silver",  # SILVER!
            provenance=SPOProvenance(
                source_id="node_silver",  # From node_silver
                extraction_method="llm_structured",
                model_used="deepseek-r1-14b",
                extracted_at=datetime.utcnow().isoformat(),
                verified=True,
                verification_count=2,
                verification_sources=["s1", "s2"]
            ),
            created_at=datetime.utcnow().isoformat(),
            metadata={"test": True}
        )
        graph.add_spo_triplet(triplet)

    # Evaluate
    score_silver = evaluator.evaluate_node_facts("node_silver")
    dist_silver = evaluator.get_node_fact_distribution("node_silver")

    print(f"\n✓ Node with 10 Silver facts:")
    print(f"  - Score: {score_silver:.3f} (expected: 0.6)")
    print(f"  - Distribution: {dist_silver}")

    assert score_silver == 0.6, f"Expected 0.6, got {score_silver}"
    assert dist_silver['silver'] == 10
    assert dist_silver['total'] == 10
    print("✓ Silver-only score correct!")

    # ========== Phase 4: Node with Only Bronze Facts ==========
    print("\n[Phase 4] Test node with only Bronze facts...")

    # Create 20 Bronze facts for node_bronze
    for i in range(20):
        triplet = SPOTriplet(
            id=f"spo_bronze_{i}",
            subject=f"Bronze Subject {i}",
            predicate="relates",
            object=f"Bronze Object {i}",
            confidence=0.70,
            tier="bronze",  # BRONZE!
            provenance=SPOProvenance(
                source_id="node_bronze",  # From node_bronze
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

    # Evaluate
    score_bronze = evaluator.evaluate_node_facts("node_bronze")
    dist_bronze = evaluator.get_node_fact_distribution("node_bronze")

    print(f"\n✓ Node with 20 Bronze facts:")
    print(f"  - Score: {score_bronze:.3f} (expected: 0.3)")
    print(f"  - Distribution: {dist_bronze}")

    assert score_bronze == 0.3, f"Expected 0.3, got {score_bronze}"
    assert dist_bronze['bronze'] == 20
    assert dist_bronze['total'] == 20
    print("✓ Bronze-only score correct!")

    # ========== Phase 5: Node with Mixed Facts ==========
    print("\n[Phase 5] Test node with mixed facts...")

    # Create mixed facts for node_mixed
    # 5 Gold + 10 Silver + 20 Bronze = 35 facts
    # Expected score = (5*1.0 + 10*0.6 + 20*0.3) / 35 = 17/35 = 0.486

    # 5 Gold
    for i in range(5):
        triplet = SPOTriplet(
            id=f"spo_mixed_gold_{i}",
            subject=f"Mixed Subject {i}",
            predicate="is",
            object=f"Gold {i}",
            confidence=0.95,
            tier="gold",
            provenance=SPOProvenance(
                source_id="node_mixed",
                extraction_method="llm_structured",
                model_used="deepseek-r1-14b",
                extracted_at=datetime.utcnow().isoformat(),
                verified=True,
                verification_count=3,
                verification_sources=["s1", "s2", "s3"]
            ),
            created_at=datetime.utcnow().isoformat(),
            metadata={"test": True}
        )
        graph.add_spo_triplet(triplet)

    # 10 Silver
    for i in range(10):
        triplet = SPOTriplet(
            id=f"spo_mixed_silver_{i}",
            subject=f"Mixed Subject {i}",
            predicate="has",
            object=f"Silver {i}",
            confidence=0.80,
            tier="silver",
            provenance=SPOProvenance(
                source_id="node_mixed",
                extraction_method="llm_structured",
                model_used="deepseek-r1-14b",
                extracted_at=datetime.utcnow().isoformat(),
                verified=True,
                verification_count=2,
                verification_sources=["s1", "s2"]
            ),
            created_at=datetime.utcnow().isoformat(),
            metadata={"test": True}
        )
        graph.add_spo_triplet(triplet)

    # 20 Bronze
    for i in range(20):
        triplet = SPOTriplet(
            id=f"spo_mixed_bronze_{i}",
            subject=f"Mixed Subject {i}",
            predicate="relates",
            object=f"Bronze {i}",
            confidence=0.70,
            tier="bronze",
            provenance=SPOProvenance(
                source_id="node_mixed",
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

    # Evaluate
    score_mixed = evaluator.evaluate_node_facts("node_mixed")
    dist_mixed = evaluator.get_node_fact_distribution("node_mixed")

    expected_score = 17.0 / 35.0  # ~0.486

    print(f"\n✓ Node with mixed facts (5G + 10S + 20B):")
    print(f"  - Score: {score_mixed:.3f} (expected: {expected_score:.3f})")
    print(f"  - Distribution: {dist_mixed}")
    print(f"  - Weighted sum: {dist_mixed['weighted_sum']:.1f}")

    assert abs(score_mixed - expected_score) < 0.01, f"Expected {expected_score}, got {score_mixed}"
    assert dist_mixed['gold'] == 5
    assert dist_mixed['silver'] == 10
    assert dist_mixed['bronze'] == 20
    assert dist_mixed['total'] == 35
    print("✓ Mixed score correct!")

    # ========== Phase 6: Node with No Facts ==========
    print("\n[Phase 6] Test node with no facts...")

    score_empty = evaluator.evaluate_node_facts("node_empty")
    dist_empty = evaluator.get_node_fact_distribution("node_empty")

    print(f"\n✓ Node with no facts:")
    print(f"  - Score: {score_empty:.3f} (expected: 0.0)")
    print(f"  - Distribution: {dist_empty}")

    assert score_empty == 0.0, f"Expected 0.0, got {score_empty}"
    assert dist_empty['total'] == 0
    print("✓ Empty node score correct!")

    # ========== Phase 7: Test Caching ==========
    print("\n[Phase 7] Test caching...")

    # Clear cache first
    evaluator.clear_cache()
    cache_stats = evaluator.get_cache_stats()
    print(f"\n✓ Cache cleared: {cache_stats}")

    # First evaluation (cache miss)
    start = time.time()
    score1 = evaluator.evaluate_node_facts("node_mixed")
    time1 = time.time() - start

    # Second evaluation (cache hit)
    start = time.time()
    score2 = evaluator.evaluate_node_facts("node_mixed")
    time2 = time.time() - start

    cache_stats = evaluator.get_cache_stats()

    print(f"\n✓ Caching test:")
    print(f"  - First call: {time1*1000:.2f}ms (cache miss)")
    print(f"  - Second call: {time2*1000:.2f}ms (cache hit)")
    print(f"  - Speedup: {time1/time2:.1f}x")
    print(f"  - Cache stats: {cache_stats}")

    assert score1 == score2, "Cached score should match"
    assert time2 < time1, "Cached call should be faster"
    assert cache_stats['score_cache_size'] > 0, "Cache should have entries"
    print("✓ Caching works correctly!")

    # ========== Phase 8: Batch Evaluation ==========
    print("\n[Phase 8] Test batch evaluation...")

    batch_results = evaluator.evaluate_batch([
        "node_gold",
        "node_silver",
        "node_bronze",
        "node_mixed",
        "node_empty"
    ])

    print(f"\n✓ Batch evaluation results:")
    for node_id, score in batch_results.items():
        print(f"  - {node_id}: {score:.3f}")

    assert len(batch_results) == 5
    assert batch_results['node_gold'] == 1.0
    assert batch_results['node_silver'] == 0.6
    assert batch_results['node_bronze'] == 0.3
    print("✓ Batch evaluation works!")

    # ========== Phase 9: Tier Breakdown Summary ==========
    print("\n[Phase 9] Get tier breakdown summary...")

    summary = evaluator.get_tier_breakdown_summary()

    print(f"\n✓ Tier breakdown summary:")
    print(f"  - Total facts: {summary['total_facts_evaluated']}")
    print(f"  - Gold: {summary['gold_count']} ({summary['gold_percentage']:.1f}%)")
    print(f"  - Silver: {summary['silver_count']} ({summary['silver_percentage']:.1f}%)")
    print(f"  - Bronze: {summary['bronze_count']} ({summary['bronze_percentage']:.1f}%)")
    print(f"  - Avg quality score: {summary['avg_quality_score']:.3f}")

    expected_total = 5 + 10 + 20 + 35  # 70 facts
    assert summary['total_facts_evaluated'] == expected_total
    assert summary['gold_count'] == 5 + 5  # node_gold + node_mixed
    assert summary['silver_count'] == 10 + 10
    assert summary['bronze_count'] == 20 + 20
    print("✓ Summary statistics correct!")

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
    print("\nFactQualityEvaluator is working correctly!")
    print("Key features verified:")
    print("  ✓ Gold-only nodes: score 1.0")
    print("  ✓ Silver-only nodes: score 0.6")
    print("  ✓ Bronze-only nodes: score 0.3")
    print("  ✓ Mixed facts: correct weighted score")
    print("  ✓ Empty nodes: score 0.0")
    print("  ✓ Caching works and improves performance")
    print("  ✓ Batch evaluation works")
    print("  ✓ Tier breakdown summary accurate")
    print("\n✅ Sprint 1 Complete! Ready for Sprint 2 (Enhanced MCTS UCB1)")


if __name__ == "__main__":
    test_fact_quality_evaluator()
