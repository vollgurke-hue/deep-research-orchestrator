"""
MCTS Engine - Monte Carlo Tree Search with Coverage-Guided Selection

Evaluates paths through Tree of Thoughts using MCTS algorithm.
Enhanced with Coverage Analysis to prioritize under-explored areas.

Concept: "Coverage Analysis tells MCTS where to dig" (Gemini suggestion)
"""

import math
import random
from typing import Optional, List, Dict
from .tot_manager import ToTManager
from .graph_manager import GraphManager
from .model_orchestrator import ModelOrchestrator, ModelCapability, QualityLevel
from .xot_simulator import XoTSimulator
from .token_budget_manager import TokenBudgetManager


class MCTSEngine:
    """
    Monte Carlo Tree Search for ToT path evaluation.
    Enhanced with Coverage-Guided Selection, XoT Prior Estimation, and Token Budget Management.

    MCTS Algorithm (4 phases):
    1. SELECTION: Pick most promising leaf using enhanced UCB1
    2. SIMULATION: Estimate value of this path (with token tracking)
    3. BACKPROPAGATION: Update values up tree
    4. REPEAT until convergence (or budget exhausted)

    Enhanced UCB1 Formula:
        UCB1 = exploitation + exploration + coverage_bonus + xot_prior
             = (value / visits)
               + C * sqrt(ln(parent_visits) / visits)
               + (1.0 - coverage_score) * coverage_weight
               + xot_prior * xot_weight

    Where:
    - value/visits = exploitation (choose known good paths)
    - C * sqrt(...) = exploration (try uncertain paths)
    - coverage_bonus = prioritize under-explored areas (optional)
    - xot_prior = fast heuristic boost for promising paths (optional)

    Token Budget Management:
    - Dynamic allocation: high UCB1 nodes get more tokens
    - Auto-pruning when node budget exhausted
    - Stops search when total budget exceeded

    Usage:
        # Basic MCTS
        mcts = MCTSEngine(tot_manager, graph_manager, model_orchestrator)

        # With XoT
        xot = XoTSimulator(model_orchestrator)
        mcts = MCTSEngine(tot_manager, graph_manager, model_orchestrator,
                         xot_simulator=xot, xot_weight=0.2)

        # With Token Budgets (NEW!)
        budget_mgr = TokenBudgetManager(total_budget=500_000, default_node_budget=10_000)
        mcts = MCTSEngine(tot_manager, graph_manager, model_orchestrator,
                         token_budget_manager=budget_mgr)

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
        exploration_constant: float = math.sqrt(2),
        coverage_analyzer=None,
        coverage_weight: float = 0.5,
        adaptive_weight: bool = True,
        xot_simulator: Optional[XoTSimulator] = None,
        xot_weight: float = 0.2,
        token_budget_manager: Optional[TokenBudgetManager] = None
    ):
        """
        Initialize MCTS engine with optional coverage-guided selection, XoT, and token budgets.

        Args:
            tot_manager: ToT tree to search
            graph_manager: Knowledge graph for context
            model_orchestrator: LLM for simulations
            exploration_constant: UCB1 exploration parameter (default: √2)
            coverage_analyzer: Optional CoverageAnalyzer for intelligent exploration
            coverage_weight: Base weight for coverage bonus (0-1, default: 0.5)
            adaptive_weight: Use adaptive coverage weight based on exploration phase (default: True)
            xot_simulator: Optional XoT simulator for prior estimation (default: None)
            xot_weight: Weight for XoT prior boost (default: 0.2)
            token_budget_manager: Optional TokenBudgetManager for budget tracking (default: None)
        """
        self.tot = tot_manager
        self.graph = graph_manager
        self.llm = model_orchestrator
        self.C = exploration_constant

        # Coverage-guided selection
        self.coverage_analyzer = coverage_analyzer
        self.coverage_weight = coverage_weight
        self.coverage_mode = coverage_analyzer is not None
        self.adaptive_weight = adaptive_weight

        # XoT-guided selection
        self.xot_simulator = xot_simulator
        self.xot_weight = xot_weight
        self.xot_mode = xot_simulator is not None

        # Token budget management (NEW!)
        self.token_budget_manager = token_budget_manager
        self.budget_mode = token_budget_manager is not None

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
            # Check total budget (NEW!)
            if self.budget_mode and self.token_budget_manager.is_total_budget_exceeded():
                print("⚠ Total token budget exceeded, stopping MCTS iterations")
                break

            # Phase 1: Selection
            leaf_id = self.select()
            if not leaf_id:
                break

            # Check node budget before simulation (NEW!)
            if self.budget_mode and not self.token_budget_manager.check_budget(leaf_id):
                # Node has no budget left, prune it
                node = self.tot.tree.get(leaf_id)
                if node:
                    self.tot.prune_branch(leaf_id, reason="token_budget_exceeded")
                continue

            stats["nodes_selected"].append(leaf_id)

            # Allocate budget if needed (NEW!)
            if self.budget_mode:
                node = self.tot.tree.get(leaf_id)
                if node and hasattr(node, 'ucb1_score'):
                    self.token_budget_manager.allocate_budget(leaf_id, node.ucb1_score)

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
        Compute UCB1 score with optional coverage bonus and XoT prior.

        Standard UCB1:
            UCB1 = exploitation + exploration
                 = (value / visits) + C * sqrt(ln(parent_visits) / visits)

        Coverage-Guided UCB1:
            UCB1 = exploitation + exploration + coverage_bonus
                 = (value / visits)
                   + C * sqrt(ln(parent_visits) / visits)
                   + (1.0 - coverage_score) * coverage_weight

        XoT-Enhanced UCB1 (NEW!):
            UCB1 = exploitation + exploration + coverage_bonus + xot_prior
                 = (value / visits)
                   + C * sqrt(ln(parent_visits) / visits)
                   + (1.0 - coverage_score) * coverage_weight
                   + xot_prior * xot_weight

        The xot_prior (0-1) gives fast heuristic boost to promising paths.
        Higher xot_prior = more promising = higher UCB1 score.

        Special cases:
        - If visits == 0: return infinity (explore unvisited)
        - If parent_visits == 0: return 0

        Args:
            node: Child node
            parent: Parent node

        Returns:
            UCB1 score (with coverage bonus and XoT prior if enabled)
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

        # Standard UCB1
        ucb1 = exploitation + exploration

        # Coverage bonus
        if self.coverage_mode and self.coverage_analyzer:
            coverage_bonus = self._compute_coverage_bonus(node)
            ucb1 += coverage_bonus

        # XoT prior boost (NEW!)
        if self.xot_mode and self.xot_simulator:
            xot_prior = self._compute_xot_prior(node)
            ucb1 += xot_prior * self.xot_weight

        return ucb1

    def _compute_coverage_bonus(self, node) -> float:
        """
        Compute coverage bonus for node.

        Formula:
            coverage_bonus = (1.0 - coverage_score) * coverage_weight

        Where:
        - coverage_score: 0-1 (from CoverageAnalyzer)
        - coverage_weight: 0-1 (configuration parameter, adaptive if enabled)

        Example:
        - If coverage_score = 0.2 (low coverage/gap):
          bonus = (1.0 - 0.2) * 0.5 = 0.4 (HIGH bonus)

        - If coverage_score = 0.9 (well covered):
          bonus = (1.0 - 0.9) * 0.5 = 0.05 (LOW bonus)

        Adaptive Weight Strategy (Gemini recommendation):
        - Early exploration (coverage < 0.4): weight = 0.7 (prioritize breadth)
        - Mid exploration (0.4 <= coverage < 0.7): weight = 0.5 (balanced)
        - Late exploration (coverage >= 0.7): weight = 0.3 (prioritize depth)

        This makes MCTS prioritize under-explored areas!

        Args:
            node: Node to calculate bonus for

        Returns:
            Coverage bonus (0.0 - coverage_weight)
        """
        try:
            # Get coverage analysis for this node
            coverage = self.coverage_analyzer.analyze_node_coverage(node.node_id)
            coverage_score = coverage.get("overall_coverage", 0.5)

            # Invert coverage: low coverage = high bonus
            gap_score = 1.0 - coverage_score

            # Get adaptive weight (or use static weight)
            current_weight = self._get_adaptive_coverage_weight() if self.adaptive_weight else self.coverage_weight

            # Apply weight
            bonus = gap_score * current_weight

            return bonus

        except Exception as e:
            # If coverage analysis fails, return 0 (no bonus)
            return 0.0

    def _get_adaptive_coverage_weight(self) -> float:
        """
        Calculate adaptive coverage weight based on overall research coverage.

        Strategy (Gemini's recommendation):
        - Early phase (coverage < 0.4): weight = 0.7
          → Maximize exploration breadth, find all major gaps
        - Mid phase (0.4 <= coverage < 0.7): weight = 0.5
          → Balanced approach
        - Late phase (coverage >= 0.7): weight = 0.3
          → Focus on depth in profitable areas

        Returns:
            Adaptive weight (0.3 - 0.7)
        """
        try:
            # Get overall coverage
            overall_coverage = self.coverage_analyzer.get_overall_research_coverage()
            coverage = overall_coverage.get("overall_coverage", 0.0)

            # Adaptive thresholds
            if coverage < 0.4:
                return 0.7  # Early: prioritize breadth
            elif coverage < 0.7:
                return 0.5  # Mid: balanced
            else:
                return 0.3  # Late: prioritize depth

        except Exception:
            # Fallback to base weight
            return self.coverage_weight

    def _compute_xot_prior(self, node) -> float:
        """
        Compute XoT prior probability for node.

        Calls XoTSimulator to get fast heuristic estimate (0-1).
        This prior boosts UCB1 for promising paths.

        Formula:
            xot_boost = xot_prior * xot_weight

        Where:
        - xot_prior: 0-1 (from XoTSimulator)
        - xot_weight: 0-1 (configuration parameter, default 0.2)

        Example:
        - If xot_prior = 0.85 (looks very promising):
          boost = 0.85 * 0.2 = 0.17 (HIGH boost)

        - If xot_prior = 0.2 (likely dead end):
          boost = 0.2 * 0.2 = 0.04 (LOW boost)

        Args:
            node: Node to calculate prior for

        Returns:
            XoT prior score (0.0 - 1.0)
        """
        try:
            # Get quick simulation from XoT
            prior = self.xot_simulator.simulate_quick(node)
            return prior

        except Exception as e:
            # If XoT fails, return neutral prior (no boost)
            print(f"XoT prior calculation failed: {e}")
            return 0.5

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

        # Estimate token usage for simulation
        estimated_tokens = 0

        if method == "axiom":
            value = self._simulate_axiom(node)
            estimated_tokens = 0  # No LLM call
        elif method == "llm":
            value = self._simulate_llm(node)
            estimated_tokens = 1000  # LLM call ~1000 tokens
        elif method == "random":
            value = random.random()
            estimated_tokens = 0
        else:
            value = 0.5
            estimated_tokens = 0

        # Track tokens if budget mode enabled (NEW!)
        if self.budget_mode and estimated_tokens > 0:
            self.token_budget_manager.track_tokens(node_id, estimated_tokens)

        return value

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
        Get MCTS statistics including coverage, XoT, and budget info.

        Returns:
            {
                "total_visits": 42,
                "max_depth_visited": 3,
                "avg_value": 0.75,
                "best_leaf_visits": 10,
                "coverage_mode": true,
                "adaptive_weight": true,
                "current_coverage_weight": 0.7,
                "avg_coverage": 0.65,  (if coverage mode enabled)
                "xot_mode": true,  (if XoT enabled)
                "xot_weight": 0.2,
                "xot_total_simulations": 150,
                "xot_success_rate": 0.95,
                "xot_avg_score": 0.67,
                "xot_avg_time": 1.8,
                "budget_mode": true,  (if budget enabled)
                "budget_nodes_tracked": 25,
                "budget_nodes_exhausted": 3,
                "budget_total_used": 45000,
                "budget_total_remaining": 455000,
                "budget_utilization": 9.0,
                "budget_exhaustion_rate": 12.0
            }
        """
        total_visits = sum(n.visits for n in self.tot.tree.values())
        total_value = sum(n.value for n in self.tot.tree.values())

        visited_nodes = [n for n in self.tot.tree.values() if n.visits > 0]
        max_depth = max((n.depth for n in visited_nodes), default=0)

        leaves = [n for n in self.tot.tree.values() if n.is_leaf() and not n.is_pruned()]
        best_leaf_visits = max((n.visits for n in leaves), default=0)

        stats = {
            "total_visits": total_visits,
            "total_value": total_value,
            "avg_value": total_value / max(total_visits, 1),
            "max_depth_visited": max_depth,
            "best_leaf_visits": best_leaf_visits,
            "num_leaves": len(leaves),
            "coverage_mode": self.coverage_mode,
            "adaptive_weight": self.adaptive_weight
        }

        # Add coverage stats if enabled
        if self.coverage_mode and self.coverage_analyzer:
            try:
                overall_coverage = self.coverage_analyzer.get_overall_research_coverage()
                stats["avg_coverage"] = overall_coverage.get("overall_coverage", 0.0)
                stats["gaps_count"] = overall_coverage.get("gaps_count", 0)
                stats["recommendations"] = overall_coverage.get("recommendations", [])

                # Add current adaptive weight
                if self.adaptive_weight:
                    stats["current_coverage_weight"] = self._get_adaptive_coverage_weight()
                else:
                    stats["current_coverage_weight"] = self.coverage_weight

            except Exception:
                pass

        # Add XoT stats if enabled
        if self.xot_mode and self.xot_simulator:
            try:
                xot_stats = self.xot_simulator.get_stats()
                stats["xot_mode"] = True
                stats["xot_weight"] = self.xot_weight
                stats["xot_total_simulations"] = xot_stats.get("total_simulations", 0)
                stats["xot_success_rate"] = xot_stats.get("success_rate", 0.0)
                stats["xot_avg_score"] = xot_stats.get("avg_score", 0.0)
                stats["xot_avg_time"] = xot_stats.get("avg_time", 0.0)
            except Exception:
                stats["xot_mode"] = True
                stats["xot_error"] = "Failed to get XoT stats"

        # Add budget stats if enabled (NEW!)
        if self.budget_mode and self.token_budget_manager:
            try:
                budget_stats = self.token_budget_manager.get_stats()
                stats["budget_mode"] = True
                stats["budget_nodes_tracked"] = budget_stats.get("nodes_tracked", 0)
                stats["budget_nodes_exhausted"] = budget_stats.get("nodes_exhausted", 0)
                stats["budget_total_used"] = budget_stats.get("total_tokens_used", 0)
                stats["budget_total_remaining"] = budget_stats.get("total_remaining", 0)
                stats["budget_utilization"] = budget_stats.get("budget_utilization", 0.0)
                stats["budget_exhaustion_rate"] = budget_stats.get("exhaustion_rate", 0.0)
            except Exception:
                stats["budget_mode"] = True
                stats["budget_error"] = "Failed to get budget stats"

        return stats

    def get_coverage_guided_suggestions(self, top_n: int = 5) -> List[Dict]:
        """
        Get top N nodes to explore next based on coverage analysis.

        This is useful for UI to show "suggested next steps".

        Args:
            top_n: Number of suggestions to return

        Returns:
            List of dicts with node info and priority
        """
        if not self.coverage_mode or not self.coverage_analyzer:
            return []

        try:
            # Get coverage gaps
            gaps = self.coverage_analyzer.identify_coverage_gaps(threshold=0.5)

            # Take top N
            suggestions = []
            for gap in gaps[:top_n]:
                node_id = gap["node_id"]
                node = self.tot.tree.get(node_id)

                if node:
                    suggestions.append({
                        "node_id": node_id,
                        "question": node.question,
                        "depth": node.depth,
                        "status": node.status,
                        "priority": gap["priority"],
                        "coverage": gap["coverage"]["overall_coverage"],
                        "reason": self._explain_low_coverage(gap["coverage"])
                    })

            return suggestions

        except Exception as e:
            print(f"Failed to get coverage suggestions: {e}")
            return []

    def _explain_low_coverage(self, coverage: Dict[str, float]) -> str:
        """Generate human-readable explanation for low coverage."""
        reasons = []

        if coverage["entity_density"] < 0.3:
            reasons.append("few entities extracted")

        if coverage["exploration_depth"] < 0.4:
            reasons.append("shallow exploration")

        if coverage["axiom_coverage"] < 0.5:
            reasons.append("axioms not tested")

        if coverage["neighbor_coverage"] < 0.3:
            reasons.append("isolated from graph")

        if not reasons:
            return "general low coverage"

        return ", ".join(reasons)
