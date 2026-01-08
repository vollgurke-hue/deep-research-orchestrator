"""
Graph Manager

Manages the NetworkX knowledge graph (truth buffer).
Handles node/edge operations, conflict detection, and serialization.
"""

import networkx as nx
from typing import Optional, List, Dict, Any
from datetime import datetime


class GraphManager:
    """
    Manages the knowledge graph (NetworkX DiGraph).

    Responsibilities:
    - CRUD operations on nodes/edges
    - Conflict detection (contradictory facts)
    - Graph serialization for prompts (ego-graph, PageRank)
    - Persistence (save/load)

    Node structure:
    {
        "id": "fact_123",
        "type": "fact",  # fact, opinion, question, hypothesis
        "content": "Market is growing at 15% CAGR",
        "confidence": 0.85,
        "source": "Gartner Report 2024",
        "timestamp": "2026-01-08T17:00:00Z",
        "metadata": { ... }
    }

    Edge structure:
    {
        "type": "supports",  # supports, contradicts, relates_to
        "weight": 0.8,
        "reasoning": "Both mention same market trend"
    }
    """

    def __init__(self, max_nodes: int = 10000):
        """
        Initialize graph manager.

        Args:
            max_nodes: Maximum nodes allowed (from profile)
        """
        self.graph = nx.DiGraph()
        self.max_nodes = max_nodes

    def add_node(
        self,
        node_id: str,
        node_type: str,
        content: str,
        confidence: float,
        source: Optional[str] = None,
        **metadata
    ) -> bool:
        """
        Add node to knowledge graph.

        Args:
            node_id: Unique identifier
            node_type: fact, opinion, question, hypothesis
            content: The actual information
            confidence: 0.0-1.0 confidence score
            source: Where this came from (optional)
            **metadata: Additional attributes

        Returns:
            True if added, False if max_nodes reached
        """
        # TODO Sprint 1 Day 4: Implement node addition
        # Check max_nodes limit
        # Add with timestamp
        # Validate required fields

        if len(self.graph.nodes) >= self.max_nodes:
            return False

        self.graph.add_node(
            node_id,
            type=node_type,
            content=content,
            confidence=confidence,
            source=source,
            timestamp=datetime.utcnow().isoformat(),
            **metadata
        )
        return True

    def add_edge(
        self,
        source_id: str,
        target_id: str,
        edge_type: str,
        weight: float = 0.5,
        **metadata
    ):
        """
        Add edge between two nodes.

        Args:
            source_id: Source node ID
            target_id: Target node ID
            edge_type: supports, contradicts, relates_to
            weight: Edge strength (0.0-1.0)
            **metadata: Additional edge attributes
        """
        # TODO Sprint 1 Day 4: Implement edge addition
        # Validate nodes exist
        # Add edge with type and weight
        self.graph.add_edge(
            source_id,
            target_id,
            type=edge_type,
            weight=weight,
            **metadata
        )

    def find_contradictions(self) -> List[tuple[str, str]]:
        """
        Find contradictory fact pairs in graph.

        Returns:
            List of (node_id_1, node_id_2) tuples

        Detection:
        - Look for "contradicts" edges
        - Look for facts with semantic similarity but opposite sentiment
        """
        # TODO Sprint 1 Day 5: Implement contradiction detection
        # Find all edges with type="contradicts"
        # TODO Sprint 2: Add semantic analysis
        contradictions = []
        for u, v, data in self.graph.edges(data=True):
            if data.get("type") == "contradicts":
                contradictions.append((u, v))
        return contradictions

    def get_ego_graph(self, center_node: str, depth: int = 2) -> nx.DiGraph:
        """
        Extract subgraph around a center node.

        Args:
            center_node: Node to center on
            depth: How many hops to include

        Returns:
            Subgraph containing center + neighbors up to depth
        """
        # TODO Sprint 1 Day 5: Implement ego-graph extraction
        # Use nx.ego_graph()
        # Limit by depth
        return nx.ego_graph(self.graph, center_node, radius=depth)

    def get_top_nodes(self, n: int = 10, algorithm: str = "pagerank") -> List[str]:
        """
        Get most important nodes by ranking algorithm.

        Args:
            n: Number of top nodes to return
            algorithm: "pagerank", "degree", "betweenness"

        Returns:
            List of node IDs sorted by importance
        """
        # TODO Sprint 1 Day 5: Implement ranking
        # pagerank: nx.pagerank()
        # degree: graph.degree()
        # betweenness: nx.betweenness_centrality()

        if algorithm == "pagerank":
            ranks = nx.pagerank(self.graph)
            return sorted(ranks, key=ranks.get, reverse=True)[:n]
        return []

    def to_markdown(self, node_ids: Optional[List[str]] = None) -> str:
        """
        Serialize (sub)graph to markdown for LLM prompts.

        Args:
            node_ids: Specific nodes to include (None = all)

        Returns:
            Markdown string representation
        """
        # TODO Sprint 1 Day 6: Implement markdown serialization
        # Format as bullet list with confidence scores
        # Include edges (X supports Y, A contradicts B)
        return "# Knowledge Graph\n\n(TODO: Implement serialization)"

    def save(self, path: str):
        """Save graph to disk (GraphML format)"""
        # TODO Sprint 1 Day 6: Implement persistence
        nx.write_graphml(self.graph, path)

    def load(self, path: str):
        """Load graph from disk"""
        # TODO Sprint 1 Day 6: Implement loading
        self.graph = nx.read_graphml(path)


# TODO Sprint 1 Day 7-9: Integrate with Axiom System
# TODO Sprint 2: Add MCTS for path exploration
