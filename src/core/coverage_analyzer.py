"""
Coverage Analyzer - Identifies gaps in knowledge graph exploration.

Analyzes ToT nodes and knowledge graph to identify under-explored areas.
Provides coverage scores that can guide MCTS exploration.

Concept from Gemini's suggestion: "Coverage Analysis tells MCTS where to dig"
"""
from typing import Dict, List, Set, Optional, Tuple
import networkx as nx
from collections import defaultdict


class CoverageAnalyzer:
    """
    Analyzes coverage of knowledge graph and ToT exploration.

    Coverage Dimensions:
    1. Thematic Coverage - How well themes are explored
    2. Entity Coverage - Density of entities in graph regions
    3. Question Depth - How deep sub-questions go
    4. Axiom Coverage - How well axioms are tested across branches
    """

    def __init__(self, graph_manager, tot_manager, axiom_manager=None):
        self.graph = graph_manager
        self.tot = tot_manager
        self.axioms = axiom_manager

        # Coverage cache (updated when nodes change)
        self._coverage_cache = {}
        self._last_update_count = 0

    def analyze_node_coverage(self, node_id: str) -> Dict[str, float]:
        """
        Analyze coverage for a specific ToT node.

        Returns coverage scores across multiple dimensions:
        - entity_density: How many entities in this node's subgraph
        - exploration_depth: How deep this branch goes
        - axiom_coverage: How many axioms tested in this branch
        - neighbor_coverage: Coverage of neighboring graph regions
        - overall_coverage: Combined score (0-1)
        """
        node = self.tot.tree.get(node_id)
        if not node:
            return self._empty_coverage()

        # Check cache
        cache_key = f"{node_id}_{len(self.tot.tree)}"
        if cache_key in self._coverage_cache:
            return self._coverage_cache[cache_key]

        # Calculate coverage dimensions
        entity_density = self._calculate_entity_density(node)
        exploration_depth = self._calculate_exploration_depth(node)
        axiom_coverage = self._calculate_axiom_coverage(node)
        neighbor_coverage = self._calculate_neighbor_coverage(node)

        # Combined score (weighted average)
        overall = (
            entity_density * 0.3 +      # 30% weight on entities
            exploration_depth * 0.2 +   # 20% weight on depth
            axiom_coverage * 0.3 +      # 30% weight on axioms
            neighbor_coverage * 0.2     # 20% weight on neighbors
        )

        coverage = {
            "entity_density": entity_density,
            "exploration_depth": exploration_depth,
            "axiom_coverage": axiom_coverage,
            "neighbor_coverage": neighbor_coverage,
            "overall_coverage": overall
        }

        # Cache result
        self._coverage_cache[cache_key] = coverage

        return coverage

    def _calculate_entity_density(self, node) -> float:
        """
        Calculate entity density for node's subgraph.

        Returns 0-1 where:
        - 0 = no entities extracted
        - 1 = rich entity network
        """
        if not node.graph_entities:
            return 0.0

        # Get entities for this node
        entities = node.graph_entities

        if not entities:
            return 0.0

        # Calculate density in graph
        try:
            # Get subgraph around these entities
            subgraph_nodes = set()
            for entity in entities:
                if self.graph.graph.has_node(entity):
                    # Add entity and its neighbors
                    subgraph_nodes.add(entity)
                    subgraph_nodes.update(self.graph.graph.neighbors(entity))

            if not subgraph_nodes:
                return 0.1  # Entities exist but not in graph yet

            # Calculate density of subgraph
            subgraph = self.graph.graph.subgraph(subgraph_nodes)

            if len(subgraph.nodes()) < 2:
                return 0.2  # Too small to measure density

            # Density = actual_edges / possible_edges
            n = len(subgraph.nodes())
            possible_edges = n * (n - 1) / 2  # Undirected graph
            actual_edges = len(subgraph.edges())

            if possible_edges == 0:
                return 0.3

            density = min(actual_edges / possible_edges, 1.0)

            # Scale: 0.3-1.0 (we know entities exist)
            return 0.3 + (density * 0.7)

        except Exception as e:
            # If calculation fails, return partial credit
            return 0.15 if entities else 0.0

    def _calculate_exploration_depth(self, node) -> float:
        """
        Calculate exploration depth score.

        Returns 0-1 where:
        - 0 = shallow (depth 0-1)
        - 1 = deep (depth >= max_depth)
        """
        if node.depth == 0:
            return 0.0

        max_depth = getattr(self.tot, 'max_depth', 3)

        # Normalize depth to 0-1
        depth_score = min(node.depth / max_depth, 1.0)

        # Check if node has children (explored further)
        has_children = len(node.children) > 0

        # Bonus for having evaluated children
        children_evaluated = 0
        for child_id in node.children:
            child = self.tot.tree.get(child_id)
            if child and child.status == "evaluated":
                children_evaluated += 1

        if len(node.children) > 0:
            children_ratio = children_evaluated / len(node.children)
        else:
            children_ratio = 0.0

        # Combined: depth + children exploration
        return depth_score * 0.6 + children_ratio * 0.4

    def _calculate_axiom_coverage(self, node) -> float:
        """
        Calculate axiom coverage for this branch.

        Returns 0-1 where:
        - 0 = no axioms tested
        - 1 = all active axioms tested
        """
        if not self.axioms:
            return 1.0  # No axioms = full coverage

        # Get scorer axioms (the ones we evaluate against)
        try:
            active_axioms = self.axioms.get_scorer_axioms()
        except AttributeError:
            # Fallback: get all axioms
            active_axioms = self.axioms.axioms if hasattr(self.axioms, 'axioms') else []

        if not active_axioms:
            return 1.0

        # Get axiom scores for this node
        axiom_scores = node.axiom_scores or {}

        # Count how many axioms tested
        tested_axioms = len(axiom_scores)
        total_axioms = len(active_axioms)

        if total_axioms == 0:
            return 1.0

        # Basic coverage: tested / total
        basic_coverage = tested_axioms / total_axioms

        # Bonus for high scores (axioms well-aligned)
        if axiom_scores:
            avg_score = sum(axiom_scores.values()) / len(axiom_scores)
            score_bonus = avg_score * 0.3  # Up to 30% bonus
        else:
            score_bonus = 0.0

        return min(basic_coverage + score_bonus, 1.0)

    def _calculate_neighbor_coverage(self, node) -> float:
        """
        Calculate coverage of neighboring graph regions.

        Returns 0-1 where:
        - 0 = isolated, no neighbors explored
        - 1 = well-connected, neighbors explored
        """
        if not node.graph_entities:
            return 0.0

        try:
            # Get entities for this node
            entities = node.graph_entities

            # Find neighboring entities in graph
            neighbor_entities = set()
            for entity in entities:
                if self.graph.graph.has_node(entity):
                    neighbor_entities.update(self.graph.graph.neighbors(entity))

            if not neighbor_entities:
                return 0.0

            # Check which neighbors are covered by other ToT nodes
            covered_neighbors = 0
            for neighbor in neighbor_entities:
                # Check if any other node has this entity
                for other_node in self.tot.tree.values():
                    if neighbor in (other_node.graph_entities or []):
                        covered_neighbors += 1
                        break

            # Coverage = covered / total
            if len(neighbor_entities) == 0:
                return 0.0

            return covered_neighbors / len(neighbor_entities)

        except Exception:
            return 0.0

    def identify_coverage_gaps(self, threshold: float = 0.5) -> List[Dict]:
        """
        Identify nodes with low coverage (gaps to explore).

        Args:
            threshold: Coverage threshold (0-1). Nodes below this are "gaps"

        Returns:
            List of gaps sorted by priority (lowest coverage first)
        """
        gaps = []

        for node_id, node in self.tot.tree.items():
            # Skip completed/pruned nodes
            if node.status in ["pruned"]:
                continue

            coverage = self.analyze_node_coverage(node_id)
            overall = coverage["overall_coverage"]

            if overall < threshold:
                gaps.append({
                    "node_id": node_id,
                    "question": node.question,
                    "depth": node.depth,
                    "status": node.status,
                    "coverage": coverage,
                    "priority": 1.0 - overall  # Lower coverage = higher priority
                })

        # Sort by priority (highest first)
        gaps.sort(key=lambda g: g["priority"], reverse=True)

        return gaps

    def get_coverage_heatmap(self) -> Dict[str, float]:
        """
        Get coverage scores for all nodes (for visualization).

        Returns:
            Dict mapping node_id → overall_coverage (0-1)
        """
        heatmap = {}

        for node_id in self.tot.tree.keys():
            coverage = self.analyze_node_coverage(node_id)
            heatmap[node_id] = coverage["overall_coverage"]

        return heatmap

    def get_thematic_coverage(self, themes: List[Dict]) -> Dict[str, float]:
        """
        Calculate coverage for thematic structure (Product Research mode).

        Args:
            themes: Thematic hierarchy from Product Research

        Returns:
            Dict mapping theme_id → coverage (0-1)
        """
        coverage_map = {}

        for theme in themes:
            theme_id = theme.get("id") or theme.get("theme_id")

            # Find ToT nodes related to this theme
            related_nodes = self._find_nodes_for_theme(theme)

            if not related_nodes:
                coverage_map[theme_id] = 0.0
                continue

            # Average coverage of related nodes
            total_coverage = 0.0
            for node_id in related_nodes:
                node_coverage = self.analyze_node_coverage(node_id)
                total_coverage += node_coverage["overall_coverage"]

            coverage_map[theme_id] = total_coverage / len(related_nodes)

            # Recursively handle children themes
            if "children" in theme and theme["children"]:
                child_coverage = self.get_thematic_coverage(theme["children"])
                coverage_map.update(child_coverage)

        return coverage_map

    def _find_nodes_for_theme(self, theme: Dict) -> List[str]:
        """Find ToT nodes that relate to a theme."""
        # Simple keyword matching (can be improved with embeddings)
        theme_keywords = theme.get("title", "").lower().split()

        related_nodes = []

        for node_id, node in self.tot.tree.items():
            question_lower = node.question.lower()

            # Check if theme keywords appear in question
            matches = sum(1 for keyword in theme_keywords if keyword in question_lower)

            if matches >= len(theme_keywords) * 0.5:  # 50% keyword match
                related_nodes.append(node_id)

        return related_nodes

    def get_overall_research_coverage(self) -> Dict[str, any]:
        """
        Calculate overall research coverage across all dimensions.

        Returns comprehensive coverage report for the entire session.
        """
        all_nodes = list(self.tot.tree.keys())

        if not all_nodes:
            return {
                "overall_coverage": 0.0,
                "total_nodes": 0,
                "avg_entity_density": 0.0,
                "avg_exploration_depth": 0.0,
                "avg_axiom_coverage": 0.0,
                "gaps_count": 0,
                "recommendations": ["Start exploring by decomposing the root question"]
            }

        # Calculate averages across all nodes
        total_coverage = 0.0
        total_entity_density = 0.0
        total_exploration_depth = 0.0
        total_axiom_coverage = 0.0

        for node_id in all_nodes:
            coverage = self.analyze_node_coverage(node_id)
            total_coverage += coverage["overall_coverage"]
            total_entity_density += coverage["entity_density"]
            total_exploration_depth += coverage["exploration_depth"]
            total_axiom_coverage += coverage["axiom_coverage"]

        n = len(all_nodes)

        # Identify gaps
        gaps = self.identify_coverage_gaps(threshold=0.5)

        # Generate recommendations
        recommendations = self._generate_recommendations(gaps, n)

        return {
            "overall_coverage": total_coverage / n,
            "total_nodes": n,
            "avg_entity_density": total_entity_density / n,
            "avg_exploration_depth": total_exploration_depth / n,
            "avg_axiom_coverage": total_axiom_coverage / n,
            "gaps_count": len(gaps),
            "top_gaps": gaps[:5],  # Top 5 priority gaps
            "recommendations": recommendations
        }

    def _generate_recommendations(self, gaps: List[Dict], total_nodes: int) -> List[str]:
        """Generate actionable recommendations based on coverage analysis."""
        recommendations = []

        if not total_nodes:
            recommendations.append("Start exploring by decomposing the root question")
            return recommendations

        if len(gaps) == 0:
            recommendations.append("Excellent coverage! Consider synthesis phase.")
            return recommendations

        # Analyze gap patterns
        shallow_gaps = [g for g in gaps if g["depth"] <= 1]
        deep_gaps = [g for g in gaps if g["depth"] >= 2]

        if len(shallow_gaps) > len(gaps) * 0.6:
            recommendations.append(
                f"Focus on depth: {len(shallow_gaps)} shallow nodes need deeper exploration"
            )

        if deep_gaps:
            top_deep_gap = deep_gaps[0]
            recommendations.append(
                f"High-priority gap at depth {top_deep_gap['depth']}: \"{top_deep_gap['question'][:50]}...\""
            )

        # Entity density recommendations
        low_entity_gaps = [g for g in gaps if g["coverage"]["entity_density"] < 0.3]
        if len(low_entity_gaps) > 3:
            recommendations.append(
                f"{len(low_entity_gaps)} nodes have low entity density - consider more detailed responses"
            )

        # Axiom coverage recommendations
        if self.axioms:
            low_axiom_gaps = [g for g in gaps if g["coverage"]["axiom_coverage"] < 0.5]
            if len(low_axiom_gaps) > 2:
                recommendations.append(
                    f"{len(low_axiom_gaps)} nodes need axiom validation - run MCTS to prioritize"
                )

        return recommendations

    def _empty_coverage(self) -> Dict[str, float]:
        """Return empty coverage dict."""
        return {
            "entity_density": 0.0,
            "exploration_depth": 0.0,
            "axiom_coverage": 0.0,
            "neighbor_coverage": 0.0,
            "overall_coverage": 0.0
        }
