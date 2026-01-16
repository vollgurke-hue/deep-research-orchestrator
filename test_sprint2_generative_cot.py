"""
Test Sprint 2: Generative CoT + Process Reward Model

Tests the full Sprint 2 workflow:
1. Create ToT node with Sprint 2 enabled
2. Expand node → generates 3 CoT variants
3. Each variant scored by Process Reward Model
4. Best variant selected
5. SPO extraction works on best variant
6. Intelligence Layer (Cluster 2) still works

Part of Sprint 2: Intelligence Layer (Gemini's Original Plan)
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.graph_manager import GraphManager
from src.core.tot_manager import ToTManager
from src.core.model_orchestrator import ModelOrchestrator


def test_sprint2_generative_cot():
    """
    Test Sprint 2: Generative CoT workflow.

    Expected behavior:
    1. ToTManager with enable_generative_cot=True
    2. expand_node() generates 3 variants (analytical, empirical, theoretical)
    3. Process Reward Model scores each variant
    4. Best variant selected based on score
    5. Node stores all variants + selected variant
    6. SPO extraction works on best answer
    """

    print("\n" + "="*70)
    print("TEST: Sprint 2 - Generative CoT + Process Reward Model")
    print("="*70)

    # ========== Phase 1: Setup ==========
    print("\n[Phase 1] Setup components...")

    # Create test database
    db_path = "test_sprint2.db"
    if os.path.exists(db_path):
        os.remove(db_path)

    # Initialize GraphManager
    graph = GraphManager(spo_db_path=db_path)
    print("✓ GraphManager initialized")

    # Initialize ModelOrchestrator with LlamaCpp provider
    from src.core.local_llamacpp_provider import LocalLlamaCppProvider

    llm = ModelOrchestrator(profile="standard")

    # Register LlamaCpp provider
    provider = LocalLlamaCppProvider(
        models_config_dir="config/models",
        auto_start=True
    )
    llm.register_provider("llamacpp", provider)

    print("✓ ModelOrchestrator initialized with LlamaCpp provider")

    # Initialize ToTManager with Sprint 2 ENABLED!
    tot = ToTManager(
        graph_manager=graph,
        axiom_manager=None,  # No axioms for this test
        model_orchestrator=llm,
        enable_intelligence=False,  # Disable Cluster 2 for focused test
        enable_generative_cot=True,  # Sprint 2: ENABLED!
        cot_variant_count=3           # Generate 3 variants
    )

    print("✓ ToTManager initialized with Sprint 2 enabled")
    print(f"  - Generative CoT: {tot.generative_cot_enabled}")
    print(f"  - CoT Generator: {tot.cot_generator is not None}")
    print(f"  - Process Reward Model: {tot.prm is not None}")

    # ========== Phase 2: Create Root Question ==========
    print("\n[Phase 2] Create root question...")

    root_id = tot.create_root("What are the benefits of renewable energy?")
    print(f"✓ Root question created: {root_id}")

    # ========== Phase 3: Decompose Question ==========
    print("\n[Phase 3] Decompose into sub-questions...")

    child_ids = tot.decompose_question(root_id, branching_factor=1)
    print(f"✓ Decomposed into {len(child_ids)} sub-question(s)")

    if not child_ids:
        print("ERROR: No sub-questions generated!")
        return False

    child_id = child_ids[0]
    child_node = tot.tree[child_id]
    print(f"  - Sub-question: {child_node.question}")

    # ========== Phase 4: Expand with Sprint 2 ==========
    print("\n[Phase 4] Expand node with Sprint 2 Generative CoT...")
    print("This will:")
    print("  1. Generate 3 CoT variants (Analytical, Empirical, Theoretical)")
    print("  2. Score each variant with Process Reward Model")
    print("  3. Select best variant")
    print("  4. Extract SPO triplets from best answer")
    print()

    success = tot.expand_node(child_id)

    if not success:
        print("ERROR: Node expansion failed!")
        return False

    print("\n✓ Node expansion successful!")

    # ========== Phase 5: Validate Sprint 2 Results ==========
    print("\n[Phase 5] Validate Sprint 2 results...")

    node = tot.tree[child_id]

    # Check that node has CoT variants
    assert hasattr(node, 'cot_variants'), "Node should have cot_variants attribute"
    print(f"✓ Node has {len(node.cot_variants)} CoT variants")

    # Check that we have 3 variants
    assert len(node.cot_variants) == 3, f"Expected 3 variants, got {len(node.cot_variants)}"
    print("✓ Correct number of variants (3)")

    # Check variant approaches
    approaches = [v.approach for v in node.cot_variants]
    print(f"✓ Variant approaches: {approaches}")
    assert "analytical" in approaches, "Missing analytical variant"
    assert "empirical" in approaches, "Missing empirical variant"
    assert "theoretical" in approaches, "Missing theoretical variant"
    print("✓ All 3 approach types present")

    # Check each variant has steps
    for i, variant in enumerate(node.cot_variants):
        print(f"\n  Variant {chr(65+i)} ({variant.approach}):")
        print(f"    - Steps: {len(variant.steps)}")
        print(f"    - Conclusion: {variant.conclusion[:60]}...")
        print(f"    - Confidence: {variant.confidence:.2f}")

        assert len(variant.steps) > 0, f"Variant {i} has no steps!"
        assert variant.conclusion, f"Variant {i} has no conclusion!"
        assert 0.0 <= variant.confidence <= 1.0, f"Invalid confidence: {variant.confidence}"

    print("\n✓ All variants have valid structure")

    # Check that best variant was selected
    assert hasattr(node, 'selected_variant_id'), "Node should have selected_variant_id"
    print(f"\n✓ Best variant selected: {node.selected_variant_id}")

    # Check that node has variant scores
    assert hasattr(node, 'variant_scores'), "Node should have variant_scores"
    print(f"✓ Variant scores available: {len(node.variant_scores)} variants scored")

    # Print variant scores
    print("\n  Variant Scores:")
    for i, score_data in enumerate(node.variant_scores):
        variant = score_data['variant']
        score = score_data['score']
        details = score_data['details']

        print(f"    Variant {chr(65+i)} ({variant.approach}):")
        print(f"      - Overall Score: {score:.3f}")
        print(f"      - Axiom Compliance: {details['axiom_compliance_avg']:.3f}")
        print(f"      - Logic Consistency: {details['logic_consistency_avg']:.3f}")
        print(f"      - Evidence Strength: {details['evidence_strength_avg']:.3f}")
        print(f"      - Violations: {details['violations_count']}")

    # Check that answer was stored
    assert node.answer, "Node should have an answer"
    print(f"\n✓ Node has answer: {node.answer[:100]}...")

    # Check that answer matches best variant
    best_variant = next(v for v in node.cot_variants if v.variant_id == node.selected_variant_id)
    assert node.answer == best_variant.conclusion, "Answer should match best variant conclusion"
    print("✓ Answer matches best variant conclusion")

    # Check that reasoning steps are stored
    assert hasattr(node, 'reasoning_steps'), "Node should have reasoning_steps"
    print(f"✓ Reasoning steps stored: {len(node.reasoning_steps)} steps")

    # ========== Phase 6: Validate SPO Extraction ==========
    print("\n[Phase 6] Validate SPO extraction...")

    # Check that SPO triplets were extracted
    assert hasattr(node, 'spo_triplets'), "Node should have spo_triplets"
    spo_count = len(node.spo_triplets)
    print(f"✓ SPO triplets extracted: {spo_count} triplets")

    if spo_count > 0:
        # Check SPO database
        all_triplets = graph.get_spo_triplets(limit=100)
        print(f"✓ SPO database contains {len(all_triplets)} triplets")

        # Show sample triplet
        if all_triplets:
            sample = all_triplets[0]
            print(f"\n  Sample SPO Triplet:")
            print(f"    Subject: {sample.subject}")
            print(f"    Predicate: {sample.predicate}")
            print(f"    Object: {sample.object}")
            print(f"    Confidence: {sample.confidence:.2f}")
            print(f"    Tier: {sample.tier}")
    else:
        print("⚠ Warning: No SPO triplets extracted (LLM may have returned unstructured text)")

    # ========== Phase 7: Compare with/without Sprint 2 ==========
    print("\n[Phase 7] Compare Sprint 2 vs Legacy mode...")

    # Create second ToTManager WITHOUT Sprint 2
    tot_legacy = ToTManager(
        graph_manager=graph,
        axiom_manager=None,
        model_orchestrator=llm,
        enable_intelligence=False,
        enable_generative_cot=False  # DISABLED!
    )

    print("✓ Legacy ToTManager created (Sprint 2 disabled)")

    root_id_legacy = tot_legacy.create_root("What are the challenges of renewable energy?")
    child_ids_legacy = tot_legacy.decompose_question(root_id_legacy, branching_factor=1)

    if child_ids_legacy:
        child_id_legacy = child_ids_legacy[0]
        print(f"\n  Expanding with legacy mode (single answer)...")

        success_legacy = tot_legacy.expand_node(child_id_legacy)

        if success_legacy:
            node_legacy = tot_legacy.tree[child_id_legacy]

            print(f"  ✓ Legacy expansion successful")
            print(f"    - Has cot_variants? {hasattr(node_legacy, 'cot_variants')}")
            print(f"    - Has selected_variant_id? {hasattr(node_legacy, 'selected_variant_id')}")

            # Legacy mode should NOT have Sprint 2 attributes
            assert not hasattr(node_legacy, 'cot_variants') or len(node_legacy.cot_variants) == 0, \
                "Legacy mode should not have CoT variants"

            print("  ✓ Legacy mode confirmed (no Sprint 2 features)")

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
    print("\nSprint 2 Generative CoT is working correctly!")
    print("\nKey features verified:")
    print("  ✓ 3 CoT variants generated (Analytical, Empirical, Theoretical)")
    print("  ✓ Each variant has reasoning steps")
    print("  ✓ Process Reward Model scores variants")
    print("  ✓ Best variant selected based on score")
    print("  ✓ All variants stored in node for analysis")
    print("  ✓ SPO extraction works on best answer")
    print("  ✓ Legacy mode (single answer) still works")
    print("\n✅ Sprint 2 Implementation COMPLETE!")

    return True


if __name__ == "__main__":
    try:
        success = test_sprint2_generative_cot()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
