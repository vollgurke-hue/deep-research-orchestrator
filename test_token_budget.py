"""
Quick test for TokenBudgetManager
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.token_budget_manager import TokenBudgetManager


def test_token_budget_manager():
    """Test TokenBudgetManager basic functionality."""
    print("=" * 60)
    print("TokenBudgetManager Test")
    print("=" * 60)

    # Create manager
    budget_mgr = TokenBudgetManager(
        total_budget=100_000,
        default_node_budget=10_000,
        min_node_budget=1_000,
        max_node_budget=50_000
    )

    print("\n[1] Initialize TokenBudgetManager")
    print(f"  Total budget: {budget_mgr.total_budget:,}")
    print(f"  Default node budget: {budget_mgr.default_node_budget:,}")

    # Test allocation with different UCB1 scores
    print("\n[2] Allocate budgets based on UCB1 scores")

    node1_budget = budget_mgr.allocate_budget("node1", ucb1_score=0.5)
    print(f"  Node1 (UCB1=0.5): {node1_budget:,} tokens")

    node2_budget = budget_mgr.allocate_budget("node2", ucb1_score=1.5)
    print(f"  Node2 (UCB1=1.5): {node2_budget:,} tokens (higher UCB1 → more budget)")

    node3_budget = budget_mgr.allocate_budget("node3", ucb1_score=0.1)
    print(f"  Node3 (UCB1=0.1): {node3_budget:,} tokens (lower UCB1 → less budget)")

    # Test token tracking
    print("\n[3] Track token usage")
    budget_mgr.track_tokens("node1", tokens_used=5_000)
    print(f"  Node1 used 5,000 tokens")
    print(f"  Node1 remaining: {budget_mgr.get_remaining_budget('node1'):,} tokens")
    print(f"  Node1 has budget: {budget_mgr.check_budget('node1')}")

    # Exceed budget
    print("\n[4] Exceed node budget")
    budget_mgr.track_tokens("node1", tokens_used=20_000)  # Exceeds allocation
    print(f"  Node1 used 20,000 more tokens (total: 25,000)")
    print(f"  Node1 remaining: {budget_mgr.get_remaining_budget('node1'):,} tokens")
    print(f"  Node1 has budget: {budget_mgr.check_budget('node1')}")
    if not budget_mgr.check_budget('node1'):
        print(f"  → Node1 should be pruned!")

    # Get stats
    print("\n[5] Budget Statistics")
    stats = budget_mgr.get_stats()
    print(f"  Nodes tracked: {stats['nodes_tracked']}")
    print(f"  Nodes exhausted: {stats['nodes_exhausted']}")
    print(f"  Total tokens used: {stats['total_tokens_used']:,}")
    print(f"  Total remaining: {stats['total_remaining']:,}")
    print(f"  Budget utilization: {stats['budget_utilization']:.1f}%")
    print(f"  Exhaustion rate: {stats['exhaustion_rate']:.1f}%")

    # Test node info
    print("\n[6] Node Budget Details")
    info = budget_mgr.get_node_budget_info("node1")
    if info:
        print(f"  Node1 info:")
        print(f"    Allocated: {info['allocated_budget']:,}")
        print(f"    Used: {info['tokens_used']:,}")
        print(f"    Remaining: {info['remaining']:,}")
        print(f"    Exhausted: {info['is_exhausted']}")
        print(f"    Utilization: {info['utilization']:.1f}%")

    print("\n" + "=" * 60)
    print("✓ TokenBudgetManager test completed!")
    print("=" * 60)

    # Verify key behaviors
    assert node2_budget > node1_budget, "Higher UCB1 should get more budget"
    assert node1_budget > node3_budget, "Lower UCB1 should get less budget"
    assert not budget_mgr.check_budget("node1"), "Node1 should be exhausted"
    assert stats["nodes_exhausted"] == 1, "Should have 1 exhausted node"

    print("\n✓ All assertions passed!")

    return True


if __name__ == "__main__":
    success = test_token_budget_manager()
    sys.exit(0 if success else 1)
