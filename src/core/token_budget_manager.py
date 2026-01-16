"""
Token Budget Manager - Prevents token waste in MCTS exploration.

Part of Cluster 1: Foundations (SRO Implementation)
Manages token budgets for MCTS nodes to prevent endless exploration in unimportant branches.

Design Philosophy:
- Dynamic allocation based on node importance (UCB1 score)
- Automatic pruning when budget exceeded
- Profile-based configuration
"""

from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class NodeBudget:
    """Budget tracking for a single ToT node."""
    node_id: str
    allocated_budget: int
    tokens_used: int = 0
    is_exhausted: bool = False


class TokenBudgetManager:
    """
    Manages token budgets for MCTS exploration.

    Purpose:
    - Prevent MCTS from wasting tokens in unimportant branches
    - Dynamically allocate more budget to promising paths (high UCB1)
    - Auto-prune nodes that exceed their budget

    Budget Allocation Strategy:
        node_budget = base_budget * (1 + ucb1_score)

    Where:
    - base_budget: Default budget for average nodes (e.g., 10,000)
    - ucb1_score: UCB1 score from MCTS (typically 0-2)
    - Higher UCB1 → more promising → larger budget

    Example:
        - Node with UCB1 = 0.5:  budget = 10k * (1 + 0.5) = 15k tokens
        - Node with UCB1 = 1.5:  budget = 10k * (1 + 1.5) = 25k tokens
        - Node with UCB1 = 0.1:  budget = 10k * (1 + 0.1) = 11k tokens

    Usage:
        budget_mgr = TokenBudgetManager(
            total_budget=500_000,
            default_node_budget=10_000,
            min_node_budget=1_000,
            max_node_budget=100_000
        )

        # Allocate budget for node based on UCB1
        budget = budget_mgr.allocate_budget(node, ucb1_score=1.2)

        # Track token usage
        budget_mgr.track_tokens(node_id, tokens_used=1500)

        # Check if node has budget remaining
        if not budget_mgr.check_budget(node_id):
            tot_manager.prune_branch(node_id, reason="token_budget_exceeded")
    """

    def __init__(
        self,
        total_budget: int,
        default_node_budget: int,
        min_node_budget: int = 1000,
        max_node_budget: int = 100000
    ):
        """
        Initialize Token Budget Manager.

        Args:
            total_budget: Total token budget for entire session/search
            default_node_budget: Base budget for average node
            min_node_budget: Minimum budget any node can get
            max_node_budget: Maximum budget any node can get
        """
        self.total_budget = total_budget
        self.default_node_budget = default_node_budget
        self.min_node_budget = min_node_budget
        self.max_node_budget = max_node_budget

        # Budget tracking
        self.node_budgets: Dict[str, NodeBudget] = {}
        self.total_tokens_used = 0

        # Stats
        self.stats = {
            "nodes_tracked": 0,
            "nodes_exhausted": 0,
            "avg_tokens_per_node": 0.0,
            "total_allocated": 0
        }

    def allocate_budget(self, node_id: str, ucb1_score: float) -> int:
        """
        Allocate token budget for node based on UCB1 score.

        Dynamic allocation formula:
            budget = base_budget * (1 + ucb1_score)

        Higher UCB1 = more promising = larger budget

        Special case: If UCB1 = infinity (unvisited node), allocate max budget.

        Args:
            node_id: Node to allocate budget for
            ucb1_score: UCB1 score from MCTS (indicates node promise)

        Returns:
            Allocated budget (tokens)
        """
        # Handle infinity (unvisited nodes get max priority)
        import math
        if math.isinf(ucb1_score):
            raw_budget = self.max_node_budget
        else:
            # Calculate dynamic budget
            raw_budget = int(self.default_node_budget * (1 + ucb1_score))

        # Clamp to [min, max]
        budget = max(self.min_node_budget, min(raw_budget, self.max_node_budget))

        # Check if total budget would be exceeded
        if self.total_tokens_used + budget > self.total_budget:
            # Reduce to remaining budget
            budget = max(0, self.total_budget - self.total_tokens_used)

        # Create budget entry
        self.node_budgets[node_id] = NodeBudget(
            node_id=node_id,
            allocated_budget=budget,
            tokens_used=0,
            is_exhausted=False
        )

        # Update stats
        self.stats["nodes_tracked"] += 1
        self.stats["total_allocated"] += budget

        return budget

    def track_tokens(self, node_id: str, tokens_used: int):
        """
        Track token usage for node.

        Updates node's token counter and checks if budget exhausted.

        Args:
            node_id: Node that used tokens
            tokens_used: Number of tokens consumed
        """
        if node_id not in self.node_budgets:
            # Node not tracked yet - allocate default budget
            self.allocate_budget(node_id, ucb1_score=0.5)

        budget = self.node_budgets[node_id]
        budget.tokens_used += tokens_used
        self.total_tokens_used += tokens_used

        # Check if budget exhausted
        if budget.tokens_used >= budget.allocated_budget:
            budget.is_exhausted = True
            self.stats["nodes_exhausted"] += 1

        # Update average
        if self.stats["nodes_tracked"] > 0:
            self.stats["avg_tokens_per_node"] = (
                self.total_tokens_used / self.stats["nodes_tracked"]
            )

    def check_budget(self, node_id: str) -> bool:
        """
        Check if node has remaining budget.

        Args:
            node_id: Node to check

        Returns:
            True if node has budget remaining, False if exhausted
        """
        if node_id not in self.node_budgets:
            # Not tracked yet - has budget
            return True

        budget = self.node_budgets[node_id]
        return not budget.is_exhausted

    def get_remaining_budget(self, node_id: str) -> int:
        """
        Get remaining token budget for node.

        Args:
            node_id: Node to check

        Returns:
            Remaining budget (tokens), or 0 if exhausted
        """
        if node_id not in self.node_budgets:
            # Not allocated yet - return default
            return self.default_node_budget

        budget = self.node_budgets[node_id]
        remaining = budget.allocated_budget - budget.tokens_used
        return max(0, remaining)

    def get_total_remaining_budget(self) -> int:
        """
        Get total remaining budget for entire session.

        Returns:
            Remaining budget (tokens)
        """
        return max(0, self.total_budget - self.total_tokens_used)

    def is_total_budget_exceeded(self) -> bool:
        """
        Check if total session budget exceeded.

        Returns:
            True if total budget exceeded
        """
        return self.total_tokens_used >= self.total_budget

    def get_stats(self) -> Dict:
        """
        Get budget statistics.

        Returns:
            Dict with budget stats:
            - nodes_tracked: Number of nodes with budgets
            - nodes_exhausted: Number of nodes that hit budget
            - total_tokens_used: Total tokens consumed
            - total_remaining: Remaining session budget
            - avg_tokens_per_node: Average tokens per node
            - budget_utilization: % of total budget used
        """
        utilization = 0.0
        if self.total_budget > 0:
            utilization = (self.total_tokens_used / self.total_budget) * 100

        return {
            "nodes_tracked": self.stats["nodes_tracked"],
            "nodes_exhausted": self.stats["nodes_exhausted"],
            "total_tokens_used": self.total_tokens_used,
            "total_remaining": self.get_total_remaining_budget(),
            "total_budget": self.total_budget,
            "avg_tokens_per_node": self.stats["avg_tokens_per_node"],
            "budget_utilization": utilization,
            "exhaustion_rate": (
                self.stats["nodes_exhausted"] / max(1, self.stats["nodes_tracked"])
            ) * 100
        }

    def reset(self):
        """Reset all budget tracking (for new session)."""
        self.node_budgets.clear()
        self.total_tokens_used = 0
        self.stats = {
            "nodes_tracked": 0,
            "nodes_exhausted": 0,
            "avg_tokens_per_node": 0.0,
            "total_allocated": 0
        }

    def get_node_budget_info(self, node_id: str) -> Optional[Dict]:
        """
        Get detailed budget info for specific node.

        Args:
            node_id: Node to get info for

        Returns:
            Dict with budget details or None if not tracked
        """
        if node_id not in self.node_budgets:
            return None

        budget = self.node_budgets[node_id]
        return {
            "node_id": node_id,
            "allocated_budget": budget.allocated_budget,
            "tokens_used": budget.tokens_used,
            "remaining": budget.allocated_budget - budget.tokens_used,
            "is_exhausted": budget.is_exhausted,
            "utilization": (budget.tokens_used / budget.allocated_budget * 100)
                          if budget.allocated_budget > 0 else 0
        }
