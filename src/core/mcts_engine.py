"""
MCTS Engine - Monte Carlo Tree Search

Evaluates paths through Tree of Thoughts using MCTS algorithm.
Helps identify most promising exploration branches.
"""

import math
import random
from typing import Optional, List, Dict
from .tot_manager import ToTManager
from .graph_manager import GraphManager
from .model_orchestrator import ModelOrchestrator, ModelCapability, QualityLevel


class MCTSEngine:
    """
    Monte Carlo Tree Search for ToT path evaluation.

    MCTS Algorithm (4 phases):
    1. SELECTION: Pick most promising leaf using UCB1
    2. SIMULATION: Estimate value of this path
    3. BACKPROPAGATION: Update values up tree
    4. REPEAT until convergence

    UCB1 Formula:
        UCB1 = (value / visits) + C * sqrt(ln(parent_visits) / visits)

    Where:
    - value/visits = exploitation (choose known good paths)
    - C * sqrt(...) = exploration (try uncertain paths)
    - C = exploration constant (default: sqrt(2) ≈ 1.414)

    Usage:
        mcts = MCTSEngine(tot_manager, graph_manager, model_orchestrator)

        # Run iterations
        for i in range(100):
            mcts.iterate()

        # Get best path
        best = mcts.best_path()
    """

    def __init__(
        self,
        tot_manager: ToTManager,
        graph_manager: GraphManager,
        model_orchestrator: ModelOrchestrator,
        exploration_constant: float = math.sqrt(2)
    ):
        """
        Initialize MCTS engine.

        Args:
            tot_manager: ToT tree to search
            graph_manager: Knowledge graph for context
            model_orchestrator: LLM for simulations
            exploration_constant: UCB1 exploration parameter (default: √2)
        """
        self.tot = tot_manager
        self.graph = graph_manager
        self.llm = model_orchestrator
        self.C = exploration_constant

    def iterate(self, num_iterations: int = 1) -> Dict:
        """
        Run MCTS iterations.

        Args:
            num_iterations: Number of iterations to run

        Returns:
            Stats dict with iteration results
        """
        stats = {
            "iterations": num_iterations,
            "nodes_selected": [],
            "avg_value": 0.0
        }

        for i in range(num_iterations):
            # Phase 1: Selection
            leaf_id = self.select()
            if not leaf_id:
                break

            stats["nodes_selected"].append(leaf_id)

            # Phase 2: Simulation
            value = self.simulate(leaf_id)

            # Phase 3: Backpropagation
            self.backpropagate(leaf_id, value)

            stats["avg_value"] += value

        if num_iterations > 0:
            stats["avg_value"] /= num_iterations

        return stats

    def select(self) -> Optional[str]:
        """
        Select most promising leaf node using UCB1.

        Algorithm:
        1. Start at root
        2. While node has children:
           - Compute UCB1 for each child
           - Select child with highest UCB1
        3. Return leaf node

        UCB1 = exploitation + exploration
             = (node.value / node.visits)
               + C * sqrt(ln(parent.visits) / node.visits)

        Returns:
            Leaf node ID or None if tree empty
        """
        # Find root node
        root = None
        for node in self.tot.tree.values():
            if node.parent_id is None and not node.is_pruned():
                root = node
                break

        if not root:
            return None

        # Traverse tree using UCB1
        current = root

        while not current.is_leaf():
            # Get non-pruned children
            children = [
                self.tot.tree[cid]
                for cid in current.children
                if cid in self.tot.tree and not self.tot.tree[cid].is_pruned()
            ]

            if not children:
                break

            # Compute UCB1 for each child
            best_child = None
            best_ucb1 = -float('inf')

            for child in children:
                ucb1 = self._compute_ucb1(child, current)

                if ucb1 > best_ucb1:
                    best_ucb1 = ucb1
                    best_child = child

            if not best_child:
                break

            # Store UCB1 score
            best_child.ucb1_score = best_ucb1
            current = best_child

        return current.node_id

    def _compute_ucb1(self, node, parent) -> float:
        """
        Compute UCB1 score for node.

        UCB1 = exploitation + exploration
             = (value / visits) + C * sqrt(ln(parent_visits) / visits)

        Special cases:
        - If visits == 0: return infinity (explore unvisited)
        - If parent_visits == 0: return 0

        Args:
            node: Child node
            parent: Parent node

        Returns:
            UCB1 score
        """
        # Unvisited nodes get highest priority
        if node.visits == 0:
            return float('inf')

        if parent.visits == 0:
            return 0.0

        # Exploitation term
        exploitation = node.value / node.visits

        # Exploration term
        exploration = self.C * math.sqrt(math.log(parent.visits) / node.visits)

        return exploitation + exploration

    def simulate(self, node_id: str, method: str = "axiom") -> float:
        """
        Simulate value of this path.

        Methods:
        1. "axiom": Use axiom scores from graph facts
        2. "llm": Ask LLM to estimate success probability
        3. "random": Random value (for testing)

        Args:
            node_id: Node to simulate from
            method: Simulation method

        Returns:
            Estimated value (0.0 - 1.0)
        """
        node = self.tot.tree.get(node_id)
        if not node:
            return 0.0

        if method == "axiom":
            return self._simulate_axiom(node)
        elif method == "llm":
            return self._simulate_llm(node)
        elif method == "random":
            return random.random()
        else:
            return 0.5

    def _simulate_axiom(self, node) -> float:
        """
        Simulate using axiom scores.

        If node has axiom scores, use average.
        Otherwise, use confidence.
        """
        if node.axiom_scores:
            # Average axiom scores
            avg_score = sum(node.axiom_scores.values()) / len(node.axiom_scores)
            return avg_score

        # Fallback to confidence
        return node.confidence

    def _simulate_llm(self, node) -> float:
        """
        Simulate by asking LLM to estimate success.

        Prompt: "Given this path, estimate probability of success (0.0-1.0)"

        This is expensive but more accurate.
        """
        try:
            # Build path summary
            path = self.tot.get_path_to_root(node.node_id)
            path_questions = [self.tot.tree[nid].question for nid in path]

            prompt = f"""Evaluate the following research path and estimate its probability of leading to a valuable insight.

Path:
{chr(10).join(f'{i+1}. {q}' for i, q in enumerate(path_questions))}

Estimate the probability of success (0.0 = very unlikely, 1.0 = very likely) based on:
- Question quality
- Logical progression
- Actionability

Respond with ONLY a number between 0.0 and 1.0."""

            response = self.llm.generate(
                prompt=prompt,
                capability=ModelCapability.REASONING,
                quality=QualityLevel.FAST  # Fast for simulation
            )

            # Parse value
            try:
                value = float(response.content.strip())
                return max(0.0, min(1.0, value))  # Clamp to [0, 1]
            except ValueError:
                return 0.5

        except Exception as e:
            print(f"LLM simulation failed: {e}")
            return 0.5

    def backpropagate(self, node_id: str, value: float):
        """
        Backpropagate value up the tree.

        Updates all ancestors with:
        - visits += 1
        - value += simulation_value

        Args:
            node_id: Leaf node where simulation started
            value: Simulation result
        """
        current_id = node_id

        while current_id:
            node = self.tot.tree.get(current_id)
            if not node:
                break

            # Update metrics
            node.visits += 1
            node.value += value
            node.update_timestamp()

            # Move to parent
            current_id = node.parent_id

    def best_path(self) -> List[str]:
        """
        Get path with highest average value.

        Returns:
            List of node IDs from root to best leaf
        """
        # Find leaf with highest avg value
        best_leaf = None
        best_avg = -float('inf')

        for node in self.tot.tree.values():
            if node.is_leaf() and not node.is_pruned():
                avg = node.avg_value()
                if avg > best_avg:
                    best_avg = avg
                    best_leaf = node

        if not best_leaf:
            return []

        return self.tot.get_path_to_root(best_leaf.node_id)

    def most_visited_path(self) -> List[str]:
        """
        Get path to most visited leaf.

        Alternative to best_path() - uses visit count instead of value.

        Returns:
            List of node IDs from root to most visited leaf
        """
        best_leaf = None
        max_visits = 0

        for node in self.tot.tree.values():
            if node.is_leaf() and not node.is_pruned():
                if node.visits > max_visits:
                    max_visits = node.visits
                    best_leaf = node

        if not best_leaf:
            return []

        return self.tot.get_path_to_root(best_leaf.node_id)

    def get_stats(self) -> Dict:
        """
        Get MCTS statistics.

        Returns:
            {
                "total_visits": 42,
                "max_depth_visited": 3,
                "avg_value": 0.75,
                "best_leaf_visits": 10
            }
        """
        total_visits = sum(n.visits for n in self.tot.tree.values())
        total_value = sum(n.value for n in self.tot.tree.values())

        visited_nodes = [n for n in self.tot.tree.values() if n.visits > 0]
        max_depth = max((n.depth for n in visited_nodes), default=0)

        leaves = [n for n in self.tot.tree.values() if n.is_leaf() and not n.is_pruned()]
        best_leaf_visits = max((n.visits for n in leaves), default=0)

        return {
            "total_visits": total_visits,
            "total_value": total_value,
            "avg_value": total_value / max(total_visits, 1),
            "max_depth_visited": max_depth,
            "best_leaf_visits": best_leaf_visits,
            "num_leaves": len(leaves)
        }
