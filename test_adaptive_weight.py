#!/usr/bin/env python3
"""
Test Adaptive Coverage Weight System

Validates that MCTS adapts coverage_weight based on exploration phase:
- Early (coverage < 0.4): weight = 0.7
- Mid (0.4 <= coverage < 0.7): weight = 0.5
- Late (coverage >= 0.7): weight = 0.3
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.graph_manager import GraphManager
from src.core.axiom_manager import AxiomManager
from src.core.tot_manager import ToTManager
from src.core.mcts_engine import MCTSEngine
from src.core.coverage_analyzer import CoverageAnalyzer
from src.core.model_orchestrator import ModelOrchestrator


def create_test_tree_with_coverage(tot, graph, num_nodes=4):
    """Create a test tree with varying coverage levels."""
    nodes = []

    # Create root
    root_id = tot.create_root("What are the main factors?")
    root = tot.tree[root_id]
    nodes.append(root)

    # Create children with different coverage levels
    for i in range(num_nodes - 1):
        question = f"Sub-question {i+1}"
        child_id = tot.decompose_question(root_id, [question])[0]
        child = tot.tree[child_id]
        nodes.append(child)

        # Simulate varying entity extraction
        if i < 2:
            # Low coverage: few entities
            child.graph_entities = [f"entity_{i}_1"]
        else:
            # Higher coverage: more entities
            child.graph_entities = [f"entity_{i}_1", f"entity_{i}_2", f"entity_{i}_3"]

            # Add to graph
            for entity in child.graph_entities:
                graph.add_node(entity, "concept", f"Node {i}")

    return nodes


def test_adaptive_weight():
    """Test that adaptive weight changes based on coverage."""
    print("🧪 Testing Adaptive Coverage Weight\n")

    # Setup
    graph = GraphManager()
    axiom_mgr = AxiomManager("config/axioms")
    orchestrator = ModelOrchestrator(profile="standard")
    tot = ToTManager(graph, axiom_mgr, orchestrator)

    # Create test tree
    print("✓ Creating test tree...")
    nodes = create_test_tree_with_coverage(tot, graph, num_nodes=4)

    # Create Coverage Analyzer
    coverage = CoverageAnalyzer(graph, tot, axiom_mgr)

    # Test 1: Adaptive Weight Enabled
    print("\n📊 Test 1: Adaptive Weight Enabled")
    print("=" * 50)

    mcts_adaptive = MCTSEngine(
        tot,
        graph,
        orchestrator,
        coverage_analyzer=coverage,
        coverage_weight=0.5,
        adaptive_weight=True
    )

    # Get overall coverage (should be low initially)
    overall = coverage.get_overall_research_coverage()
    current_coverage = overall["overall_coverage"]

    print(f"Current Coverage: {current_coverage:.2%}")

    # Get adaptive weight
    adaptive_weight = mcts_adaptive._get_adaptive_coverage_weight()
    print(f"Adaptive Weight: {adaptive_weight}")

    # Verify logic
    if current_coverage < 0.4:
        expected = 0.7
        phase = "Early"
    elif current_coverage < 0.7:
        expected = 0.5
        phase = "Mid"
    else:
        expected = 0.3
        phase = "Late"

    print(f"Exploration Phase: {phase}")
    print(f"Expected Weight: {expected}")

    if adaptive_weight == expected:
        print("✅ Adaptive weight matches expected value!")
    else:
        print(f"❌ Mismatch: got {adaptive_weight}, expected {expected}")

    # Test 2: Static Weight
    print("\n📊 Test 2: Static Weight (Disabled)")
    print("=" * 50)

    mcts_static = MCTSEngine(
        tot,
        graph,
        orchestrator,
        coverage_analyzer=coverage,
        coverage_weight=0.5,
        adaptive_weight=False
    )

    stats = mcts_static.get_stats()
    print(f"Adaptive Weight Mode: {stats['adaptive_weight']}")
    print(f"Static Weight: {stats.get('current_coverage_weight', 0.5)}")

    if not stats['adaptive_weight'] and stats.get('current_coverage_weight') == 0.5:
        print("✅ Static weight mode working correctly!")
    else:
        print("❌ Static weight mode not working as expected")

    # Test 3: Coverage Bonus Calculation
    print("\n📊 Test 3: Coverage Bonus Calculation")
    print("=" * 50)

    # Get a node with low coverage
    node = tot.tree[nodes[1].node_id]  # Should have low coverage
    node_coverage = coverage.analyze_node_coverage(node.node_id)

    print(f"Node: {node.question}")
    print(f"Node Coverage: {node_coverage['overall_coverage']:.2%}")

    # Calculate bonus
    bonus = mcts_adaptive._compute_coverage_bonus(node)
    gap_score = 1.0 - node_coverage['overall_coverage']
    expected_bonus = gap_score * adaptive_weight

    print(f"Gap Score: {gap_score:.3f}")
    print(f"Current Adaptive Weight: {adaptive_weight}")
    print(f"Coverage Bonus: {bonus:.3f}")
    print(f"Expected Bonus: {expected_bonus:.3f}")

    if abs(bonus - expected_bonus) < 0.01:
        print("✅ Coverage bonus calculated correctly!")
    else:
        print(f"❌ Bonus mismatch: got {bonus}, expected {expected_bonus}")

    # Test 4: MCTS Stats Export
    print("\n📊 Test 4: MCTS Stats Export")
    print("=" * 50)

    stats = mcts_adaptive.get_stats()

    print(f"Coverage Mode: {stats['coverage_mode']}")
    print(f"Adaptive Weight: {stats['adaptive_weight']}")
    print(f"Current Weight: {stats.get('current_coverage_weight', 'N/A')}")
    print(f"Average Coverage: {stats.get('avg_coverage', 0):.2%}")
    print(f"Gaps Count: {stats.get('gaps_count', 0)}")

    if 'current_coverage_weight' in stats and stats['adaptive_weight']:
        print("✅ Adaptive weight exposed in stats!")
    else:
        print("❌ Adaptive weight not in stats")

    # Summary
    print("\n" + "=" * 50)
    print("🎉 ADAPTIVE WEIGHT TEST COMPLETE!")
    print("=" * 50)

    print(f"""
✨ Key Findings:
- Coverage: {current_coverage:.2%} → Phase: {phase}
- Adaptive Weight: {adaptive_weight}
- Coverage Bonus: {bonus:.3f} (for low-coverage nodes)
- System: {"✅ Working" if adaptive_weight == expected else "❌ Needs fix"}

🎯 Gemini's Strategy Implemented:
- Early (< 40%): weight = 0.7 → Prioritize breadth
- Mid (40-70%): weight = 0.5 → Balanced
- Late (> 70%): weight = 0.3 → Prioritize depth
""")


if __name__ == "__main__":
    try:
        test_adaptive_weight()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
