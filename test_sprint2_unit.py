"""
Unit Tests for Sprint 2 Components (ohne LLM)

Testet:
1. CoTVariant Dataclass
2. StepScore Dataclass
3. ProcessRewardModel Scoring Logic (rule-based)

Schneller Test ohne tatsächliche LLM-Generierung!
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.cot_generator import CoTVariant
from src.core.process_reward_model import ProcessRewardModel, StepScore


def test_cot_variant_dataclass():
    """Test CoTVariant dataclass"""
    print("\n[Test 1] CoTVariant dataclass...")

    variant = CoTVariant(
        variant_id="variant_a",
        approach="analytical",
        steps=[
            "Define renewable energy",
            "Identify emission sources",
            "Calculate reduction potential"
        ],
        conclusion="Renewable energy reduces emissions by 40%",
        raw_response="Full LLM response here...",
        confidence=0.85
    )

    assert variant.variant_id == "variant_a"
    assert variant.approach == "analytical"
    assert len(variant.steps) == 3
    assert variant.confidence == 0.85

    print("✓ CoTVariant dataclass works")


def test_step_score_dataclass():
    """Test StepScore dataclass"""
    print("\n[Test 2] StepScore dataclass...")

    score = StepScore(
        step_text="Solar panels reduce emissions",
        axiom_compliance=0.9,
        logical_consistency=0.85,
        evidence_strength=0.7,
        overall_score=0.83,
        violations=[]
    )

    assert score.overall_score == 0.83
    assert len(score.violations) == 0

    print("✓ StepScore dataclass works")


def test_process_reward_model_scoring():
    """Test ProcessRewardModel rule-based scoring"""
    print("\n[Test 3] ProcessRewardModel scoring logic...")

    # Mock model orchestrator (not used for rule-based scoring)
    class MockModel:
        pass

    prm = ProcessRewardModel(
        axiom_manager=None,  # No axioms for this test
        model_orchestrator=MockModel(),
        enable_llm_scoring=False,  # Rule-based only
        enable_axiom_check=False
    )

    # Test 1: Strong evidence step
    step1 = "Research shows that solar panels reduce emissions by 40% according to MIT study."
    score1 = prm.score_step(step1)

    print(f"\nStep 1: {step1[:60]}...")
    print(f"  - Axiom Compliance: {score1.axiom_compliance:.3f}")
    print(f"  - Logic Consistency: {score1.logical_consistency:.3f}")
    print(f"  - Evidence Strength: {score1.evidence_strength:.3f}")
    print(f"  - Overall: {score1.overall_score:.3f}")

    # Should have high evidence strength (mentions "research", "study")
    assert score1.evidence_strength > 0.5, f"Expected high evidence, got {score1.evidence_strength}"

    # Test 2: Logical step with connectors
    step2 = "Since renewable energy has zero emissions, therefore it reduces overall carbon output."
    score2 = prm.score_step(step2)

    print(f"\nStep 2: {step2[:60]}...")
    print(f"  - Logic Consistency: {score2.logical_consistency:.3f}")
    print(f"  - Evidence Strength: {score2.evidence_strength:.3f}")
    print(f"  - Overall: {score2.overall_score:.3f}")

    # Should have good logical consistency (uses "since", "therefore")
    assert score2.logical_consistency > 0.5, f"Expected good logic, got {score2.logical_consistency}"

    # Test 3: Weak step
    step3 = "I think maybe renewable energy is probably good."
    score3 = prm.score_step(step3)

    print(f"\nStep 3: {step3}")
    print(f"  - Logic Consistency: {score3.logical_consistency:.3f}")
    print(f"  - Evidence Strength: {score3.evidence_strength:.3f}")
    print(f"  - Overall: {score3.overall_score:.3f}")

    # Should have lower evidence (uses weak language "I think", "maybe", "probably")
    assert score3.evidence_strength < 0.5, f"Expected low evidence, got {score3.evidence_strength}"

    print("\n✓ ProcessRewardModel scoring logic works")


def test_variant_scoring():
    """Test scoring entire CoT variant"""
    print("\n[Test 4] Variant scoring...")

    # Mock model
    class MockModel:
        pass

    prm = ProcessRewardModel(
        axiom_manager=None,
        model_orchestrator=MockModel(),
        enable_llm_scoring=False,
        enable_axiom_check=False
    )

    # Create test variant
    variant = CoTVariant(
        variant_id="variant_test",
        approach="empirical",
        steps=[
            "Research shows solar reduces emissions by 40%",
            "Studies indicate wind power is cost-effective",
            "Data suggests renewable adoption is growing"
        ],
        conclusion="Renewable energy is beneficial",
        raw_response="...",
        confidence=0.8
    )

    # Score variant
    result = prm.score_variant(variant)

    print(f"\nVariant Scoring Results:")
    print(f"  - Average Score: {result['avg_score']:.3f}")
    print(f"  - Min Score: {result['min_score']:.3f}")
    print(f"  - Max Score: {result['max_score']:.3f}")
    print(f"  - Violations: {result['violations_count']}")
    print(f"  - Axiom Compliance Avg: {result['axiom_compliance_avg']:.3f}")
    print(f"  - Logic Consistency Avg: {result['logic_consistency_avg']:.3f}")
    print(f"  - Evidence Strength Avg: {result['evidence_strength_avg']:.3f}")

    assert len(result['step_scores']) == 3, "Should have 3 step scores"
    assert result['avg_score'] > 0.0, "Average score should be > 0"
    assert result['violations_count'] == 0, "Should have no violations (no axioms)"

    # All steps have evidence indicators → should have good evidence strength
    assert result['evidence_strength_avg'] > 0.5, f"Expected good evidence, got {result['evidence_strength_avg']}"

    print("✓ Variant scoring works")


def test_scoring_weights():
    """Test that scoring weights sum correctly"""
    print("\n[Test 5] Scoring weights...")

    from src.core.process_reward_model import ProcessRewardModel

    # Check weights
    total_weight = (
        ProcessRewardModel.AXIOM_WEIGHT +
        ProcessRewardModel.LOGIC_WEIGHT +
        ProcessRewardModel.EVIDENCE_WEIGHT
    )

    print(f"\nScoring Weights:")
    print(f"  - Axiom Compliance: {ProcessRewardModel.AXIOM_WEIGHT:.1f} (40%)")
    print(f"  - Logic Consistency: {ProcessRewardModel.LOGIC_WEIGHT:.1f} (40%)")
    print(f"  - Evidence Strength: {ProcessRewardModel.EVIDENCE_WEIGHT:.1f} (20%)")
    print(f"  - Total: {total_weight:.1f}")

    assert abs(total_weight - 1.0) < 0.01, f"Weights should sum to 1.0, got {total_weight}"

    print("✓ Scoring weights correct")


def test_cot_approach_templates():
    """Test that CoTGenerator has 3 approach templates"""
    print("\n[Test 6] CoT approach templates...")

    from src.core.cot_generator import CoTGenerator

    approaches = CoTGenerator.APPROACHES

    print(f"\nApproach Templates ({len(approaches)}):")
    for approach in approaches:
        print(f"  - {approach['id']}: {approach['name']}")
        print(f"    Instruction: {approach['instruction'][:60]}...")

    assert len(approaches) == 3, f"Expected 3 approaches, got {len(approaches)}"

    # Check IDs
    ids = [a['id'] for a in approaches]
    assert "analytical" in ids, "Missing analytical approach"
    assert "empirical" in ids, "Missing empirical approach"
    assert "theoretical" in ids, "Missing theoretical approach"

    print("✓ CoT approach templates correct")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("Sprint 2 Unit Tests (Fast, No LLM)")
    print("="*70)

    try:
        test_cot_variant_dataclass()
        test_step_score_dataclass()
        test_process_reward_model_scoring()
        test_variant_scoring()
        test_scoring_weights()
        test_cot_approach_templates()

        print("\n" + "="*70)
        print("TEST RESULT: ✅ ALL TESTS PASSED")
        print("="*70)
        print("\nSprint 2 Components are working correctly!")
        print("\nTests verified:")
        print("  ✓ CoTVariant dataclass")
        print("  ✓ StepScore dataclass")
        print("  ✓ ProcessRewardModel rule-based scoring")
        print("  ✓ Evidence strength detection")
        print("  ✓ Logical consistency detection")
        print("  ✓ Variant scoring aggregation")
        print("  ✓ Scoring weights (sum to 1.0)")
        print("  ✓ CoT approach templates (3 approaches)")
        print("\n✅ Sprint 2 Core Logic VALIDATED!")

        sys.exit(0)

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
