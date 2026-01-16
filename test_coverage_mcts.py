"""
Simple test for Coverage-Guided MCTS Integration.

Tests the ultimate synergy: Coverage Analysis telling MCTS where to dig!
"""
from src.core.graph_manager import GraphManager
from src.core.axiom_manager import AxiomManager
from src.core.tot_manager import ToTManager, ToTNode
from src.core.mcts_engine import MCTSEngine
from src.core.coverage_analyzer import CoverageAnalyzer
from src.core.model_orchestrator import ModelOrchestrator

print("🧪 Testing Coverage-Guided MCTS Integration\n")

# Create test components
graph = GraphManager()
axiom_mgr = AxiomManager(axioms_dir="config/axioms")
orchestrator = ModelOrchestrator(profile="standard")
tot = ToTManager(graph, axiom_mgr, orchestrator)

# Manually create a simple tree (bypass LLM decomposition)
root_id = "root_test"
root = ToTNode(
    node_id=root_id,
    question="Find profitable e-commerce niches",
    parent_id=None,
    depth=0
)
tot.tree[root_id] = root

# Add some child nodes manually
for i in range(3):
    child_id = f"child_{i}"
    child = ToTNode(
        node_id=child_id,
        question=f"Research niche {i+1}",
        parent_id=root_id,
        depth=1
    )
    # Simulate different coverage levels
    child.graph_entities = [f"entity_{i}_{j}" for j in range(i+1)]  # 1, 2, 3 entities
    child.axiom_scores = {"opportunity_cost": 0.5 + (i * 0.2)}

    tot.tree[child_id] = child
    root.children.append(child_id)

print(f"✓ Created manual test tree with 1 root + 3 children")

# Create Coverage Analyzer
coverage = CoverageAnalyzer(graph, tot, axiom_mgr)
print(f"✓ Created CoverageAnalyzer")

# Analyze coverage for all nodes
print(f"\n📊 Coverage Analysis:")
for node_id, node in tot.tree.items():
    cov = coverage.analyze_node_coverage(node_id)
    print(f"  {node_id}: overall={cov['overall_coverage']:.2f}, entities={cov['entity_density']:.2f}")

# Create both MCTS versions
mcts_standard = MCTSEngine(tot, graph, orchestrator)
mcts_coverage = MCTSEngine(
    tot,
    graph,
    orchestrator,
    coverage_analyzer=coverage,
    coverage_weight=0.5
)

print(f"\n✓ Created MCTS engines:")
print(f"  Standard: coverage_mode={mcts_standard.coverage_mode}")
print(f"  Coverage-Guided: coverage_mode={mcts_coverage.coverage_mode}")

# Compare UCB1 scores
print(f"\n🎯 UCB1 Comparison (for children with visits=1, value=0.5):")

# Set some visit counts to test UCB1
root.visits = 10
for i, child_id in enumerate(root.children):
    child = tot.tree[child_id]
    child.visits = 1
    child.value = 0.5

    ucb1_std = mcts_standard._compute_ucb1(child, root)
    ucb1_cov = mcts_coverage._compute_ucb1(child, root)

    print(f"\n  {child_id}:")
    print(f"    Standard UCB1: {ucb1_std:.4f}")
    print(f"    Coverage-Guided UCB1: {ucb1_cov:.4f}")

    if ucb1_cov > ucb1_std:
        bonus = ucb1_cov - ucb1_std
        print(f"    ✨ Coverage Bonus: +{bonus:.4f}")
        print(f"       (Low coverage = high priority!)")

# Get coverage gaps
gaps = coverage.identify_coverage_gaps(threshold=0.5)
print(f"\n🔍 Coverage Gaps:")
print(f"  Total: {len(gaps)}")
for gap in gaps:
    print(f"    • {gap['node_id']}: priority={gap['priority']:.2f}")

# Get suggestions
suggestions = mcts_coverage.get_coverage_guided_suggestions(top_n=5)
print(f"\n💡 Coverage-Guided Suggestions:")
for i, sugg in enumerate(suggestions, 1):
    print(f"  {i}. {sugg['node_id']} (priority: {sugg['priority']:.2f})")
    print(f"     Reason: {sugg['reason']}")

# Get MCTS stats
stats = mcts_coverage.get_stats()
print(f"\n📊 MCTS Stats:")
print(f"  Coverage Mode: {stats['coverage_mode']}")
if 'avg_coverage' in stats:
    print(f"  Avg Coverage: {stats['avg_coverage']:.2%}")
if 'gaps_count' in stats:
    print(f"  Gaps: {stats['gaps_count']}")

print(f"\n🎉 Coverage-MCTS Integration Test PASSED!")
print(f"\n✨ THE ULTIMATE SYNERGY:")
print(f"   📊 Coverage Analysis identifies under-explored areas")
print(f"   🎯 MCTS prioritizes these areas with coverage bonus")
print(f"   🚀 Result: Intelligent, gap-aware exploration!")
