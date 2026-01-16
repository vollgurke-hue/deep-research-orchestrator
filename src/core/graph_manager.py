"""
Graph Manager

Manages the NetworkX knowledge graph (truth buffer).
Handles node/edge operations, conflict detection, and serialization.
"""

import networkx as nx
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path

from .axiom_manager import AxiomManager
from .spo_database import SPODatabase
from src.models.unified_session import SPOTriplet


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

    def __init__(
        self,
        max_nodes: int = 10000,
        axioms_dir: Optional[str] = None,
        spo_db_path: Optional[str] = None
    ):
        """
        Initialize graph manager.

        Args:
            max_nodes: Maximum nodes allowed (from profile)
            axioms_dir: Directory for axioms (None = no axiom filtering)
            spo_db_path: Path to SPO database (Cluster 1 addition)
        """
        # Legacy NetworkX graph (KEEP for backward compatibility)
        self.graph = nx.DiGraph()
        self.max_nodes = max_nodes
        self.axiom_manager = None

        if axioms_dir:
            self.axiom_manager = AxiomManager(axioms_dir)

        # NEW: SPO Database (Cluster 1 - SRO Implementation)
        self.spo_db = None
        if spo_db_path:
            self.spo_db = SPODatabase(spo_db_path)

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
            True if added, False if max_nodes reached or node exists

        Raises:
            ValueError: If confidence not in range [0, 1]
        """
        # Validate confidence
        if not 0.0 <= confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0 and 1, got {confidence}")

        # Check if node already exists
        if node_id in self.graph.nodes:
            print(f"Warning: Node {node_id} already exists, skipping")
            return False

        # Check max_nodes limit
        if len(self.graph.nodes) >= self.max_nodes:
            print(f"Warning: Max nodes ({self.max_nodes}) reached")
            return False

        # Add node with timestamp
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

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """
        Get node data by ID.

        Args:
            node_id: Node identifier

        Returns:
            Dict of node attributes or None if not found
        """
        if node_id not in self.graph.nodes:
            return None

        return dict(self.graph.nodes[node_id])

    def update_node(self, node_id: str, **updates) -> bool:
        """
        Update node attributes.

        Args:
            node_id: Node to update
            **updates: Attributes to update

        Returns:
            True if updated, False if node not found
        """
        if node_id not in self.graph.nodes:
            return False

        # Update timestamp
        updates["updated_at"] = datetime.utcnow().isoformat()

        for key, value in updates.items():
            self.graph.nodes[node_id][key] = value

        return True

    def delete_node(self, node_id: str) -> bool:
        """
        Delete node and all connected edges.

        Args:
            node_id: Node to delete

        Returns:
            True if deleted, False if node not found
        """
        if node_id not in self.graph.nodes:
            return False

        self.graph.remove_node(node_id)
        return True

    def add_edge(
        self,
        source_id: str,
        target_id: str,
        edge_type: str,
        weight: float = 0.5,
        **metadata
    ) -> bool:
        """
        Add edge between two nodes.

        Args:
            source_id: Source node ID
            target_id: Target node ID
            edge_type: supports, contradicts, relates_to
            weight: Edge strength (0.0-1.0)
            **metadata: Additional edge attributes

        Returns:
            True if added, False if nodes don't exist

        Raises:
            ValueError: If weight not in range [0, 1]
        """
        # Validate weight
        if not 0.0 <= weight <= 1.0:
            raise ValueError(f"Weight must be between 0 and 1, got {weight}")

        # Validate nodes exist
        if source_id not in self.graph.nodes:
            print(f"Warning: Source node {source_id} does not exist")
            return False

        if target_id not in self.graph.nodes:
            print(f"Warning: Target node {target_id} does not exist")
            return False

        # Add edge with timestamp
        self.graph.add_edge(
            source_id,
            target_id,
            type=edge_type,
            weight=weight,
            created_at=datetime.utcnow().isoformat(),
            **metadata
        )
        return True

    def get_edge(self, source_id: str, target_id: str) -> Optional[Dict[str, Any]]:
        """
        Get edge data.

        Args:
            source_id: Source node ID
            target_id: Target node ID

        Returns:
            Dict of edge attributes or None if not found
        """
        if not self.graph.has_edge(source_id, target_id):
            return None

        return dict(self.graph.edges[source_id, target_id])

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
        if len(self.graph.nodes) == 0:
            return []

        if algorithm == "pagerank":
            if len(self.graph.edges) == 0:
                # PageRank needs edges, fallback to all nodes
                return list(self.graph.nodes)[:n]
            ranks = nx.pagerank(self.graph)
            return sorted(ranks, key=ranks.get, reverse=True)[:n]

        elif algorithm == "degree":
            # Sort by total degree (in + out)
            degrees = dict(self.graph.degree())
            return sorted(degrees, key=degrees.get, reverse=True)[:n]

        elif algorithm == "betweenness":
            if len(self.graph.edges) == 0:
                return list(self.graph.nodes)[:n]
            centrality = nx.betweenness_centrality(self.graph)
            return sorted(centrality, key=centrality.get, reverse=True)[:n]

        else:
            raise ValueError(f"Unknown algorithm: {algorithm}. Use 'pagerank', 'degree', or 'betweenness'")

    def to_markdown(self, node_ids: Optional[List[str]] = None, max_nodes: int = 50) -> str:
        """
        Serialize (sub)graph to markdown for LLM prompts.

        Args:
            node_ids: Specific nodes to include (None = all, limited by max_nodes)
            max_nodes: Maximum nodes to include (prevents token overflow)

        Returns:
            Markdown string representation

        Format:
        # Knowledge Graph

        ## Facts (confidence ≥ 0.7)
        - **fact_1** (0.85): Market growing at 15% CAGR
          - Source: Gartner Report 2024
          - Supports: fact_2, fact_3

        ## Opinions (confidence < 0.7)
        - **opinion_1** (0.60): AI will dominate
          - Source: Expert interview

        ## Contradictions
        - fact_1 ←→ fact_5 (Market shrinking)
        """
        # Select nodes to include
        if node_ids is None:
            # Use top nodes by PageRank
            node_ids = self.get_top_nodes(n=max_nodes, algorithm="pagerank")
        else:
            node_ids = node_ids[:max_nodes]  # Limit to max

        if not node_ids:
            return "# Knowledge Graph\n\n(Empty)"

        # Build markdown
        lines = ["# Knowledge Graph\n"]

        # Group nodes by type and confidence
        facts_high = []  # confidence >= 0.7
        facts_low = []   # confidence < 0.7
        opinions = []
        questions = []
        hypotheses = []

        for node_id in node_ids:
            node_data = self.graph.nodes.get(node_id, {})
            node_type = node_data.get("type", "unknown")
            confidence = node_data.get("confidence", 0.0)
            content = node_data.get("content", "")
            source = node_data.get("source", "Unknown")

            # Format node line
            node_line = f"- **{node_id}** ({confidence:.2f}): {content}"
            if source:
                node_line += f"\n  - Source: {source}"

            # Add edges (outgoing relationships)
            out_edges = list(self.graph.out_edges(node_id, data=True))
            if out_edges:
                supports = [t for s, t, d in out_edges if d.get("type") == "supports"]
                contradicts = [t for s, t, d in out_edges if d.get("type") == "contradicts"]

                if supports:
                    node_line += f"\n  - Supports: {', '.join(supports)}"
                if contradicts:
                    node_line += f"\n  - Contradicts: {', '.join(contradicts)}"

            # Categorize
            if node_type == "fact":
                if confidence >= 0.7:
                    facts_high.append(node_line)
                else:
                    facts_low.append(node_line)
            elif node_type == "opinion":
                opinions.append(node_line)
            elif node_type == "question":
                questions.append(node_line)
            elif node_type == "hypothesis":
                hypotheses.append(node_line)

        # Add sections
        if facts_high:
            lines.append("\n## Facts (High Confidence ≥ 0.7)\n")
            lines.extend(facts_high)

        if facts_low:
            lines.append("\n## Facts (Low Confidence < 0.7)\n")
            lines.extend(facts_low)

        if opinions:
            lines.append("\n## Opinions\n")
            lines.extend(opinions)

        if hypotheses:
            lines.append("\n## Hypotheses\n")
            lines.extend(hypotheses)

        if questions:
            lines.append("\n## Questions\n")
            lines.extend(questions)

        # Add contradiction summary
        contradictions = self.find_contradictions()
        if contradictions:
            lines.append("\n## ⚠️ Contradictions Detected\n")
            for node1, node2 in contradictions:
                content1 = self.graph.nodes[node1].get("content", node1)
                content2 = self.graph.nodes[node2].get("content", node2)
                lines.append(f"- **{node1}** ←→ **{node2}**")
                lines.append(f"  - {content1}")
                lines.append(f"  - {content2}")

        return "\n".join(lines)

    def save(self, path: str):
        """Save graph to disk (GraphML format)"""
        # TODO Sprint 1 Day 6: Implement persistence
        nx.write_graphml(self.graph, path)

    def load(self, path: str):
        """Load graph from disk"""
        # TODO Sprint 1 Day 6: Implement loading
        self.graph = nx.read_graphml(path)


    def apply_axiom_scoring(self) -> Dict[str, float]:
        """
        Apply axiom-based scoring to all nodes in graph.

        Updates each node with an 'axiom_score' attribute.

        Returns:
            Dict mapping node_id -> axiom_score
        """
        if not self.axiom_manager:
            print("Warning: No axiom manager configured")
            return {}

        scores = {}

        for node_id in self.graph.nodes:
            node_data = dict(self.graph.nodes[node_id])
            score = self.axiom_manager.score_node(node_data)

            # Update node with score
            self.graph.nodes[node_id]["axiom_score"] = score
            scores[node_id] = score

        return scores

    def filter_by_axioms(self, min_score: float = 0.5) -> List[str]:
        """
        Get node IDs that pass axiom filtering.

        Args:
            min_score: Minimum axiom score threshold

        Returns:
            List of node IDs that pass filtering
        """
        if not self.axiom_manager:
            # No filtering, return all nodes
            return list(self.graph.nodes)

        # Score all nodes first
        self.apply_axiom_scoring()

        # Convert graph nodes to list format
        nodes_list = []
        for node_id in self.graph.nodes:
            node_data = dict(self.graph.nodes[node_id])
            node_data["id"] = node_id
            nodes_list.append(node_data)

        # Filter using axiom manager
        filtered = self.axiom_manager.filter_nodes(
            nodes_list,
            min_score=min_score,
            apply_filters=True
        )

        return [node["id"] for node in filtered]

    def get_relevant_subgraph(
        self,
        center_node: Optional[str] = None,
        depth: int = 2,
        min_axiom_score: float = 0.5,
        max_nodes: int = 50
    ) -> nx.DiGraph:
        """
        Get relevant subgraph using axioms and graph algorithms.

        Algorithm:
        1. If center_node specified, use ego-graph
        2. Otherwise, use top nodes by PageRank
        3. Filter by axiom scores
        4. Limit to max_nodes

        Args:
            center_node: Optional center for ego-graph
            depth: Depth for ego-graph
            min_axiom_score: Minimum axiom score threshold
            max_nodes: Maximum nodes to include

        Returns:
            Filtered subgraph
        """
        # Get candidate nodes
        if center_node and center_node in self.graph.nodes:
            # Use ego-graph around center
            subgraph = self.get_ego_graph(center_node, depth=depth)
            candidate_nodes = list(subgraph.nodes)
        else:
            # Use top nodes by PageRank
            candidate_nodes = self.get_top_nodes(n=max_nodes * 2, algorithm="pagerank")

        # Filter by axioms
        if self.axiom_manager:
            # Convert to node data format
            nodes_list = []
            for node_id in candidate_nodes:
                if node_id in self.graph.nodes:
                    node_data = dict(self.graph.nodes[node_id])
                    node_data["id"] = node_id
                    nodes_list.append(node_data)

            # Apply axiom filtering
            filtered = self.axiom_manager.filter_nodes(
                nodes_list,
                min_score=min_axiom_score,
                apply_filters=True
            )

            relevant_nodes = [node["id"] for node in filtered][:max_nodes]
        else:
            relevant_nodes = candidate_nodes[:max_nodes]

        # Create subgraph
        return self.graph.subgraph(relevant_nodes).copy()

    # ========================================================================
    # SPO Knowledge Graph Methods (Cluster 1 - SRO Implementation)
    # ========================================================================

    def add_spo_triplet(self, triplet: SPOTriplet) -> str:
        """
        Add SPO triplet to knowledge graph.

        This is the NEW way of storing structured knowledge (parallel to legacy).

        Args:
            triplet: SPOTriplet instance

        Returns:
            Triplet ID

        Raises:
            RuntimeError: If SPO database not initialized
        """
        if not self.spo_db:
            raise RuntimeError("SPO database not initialized. Pass spo_db_path to __init__")

        return self.spo_db.insert(triplet)

    def get_spo_triplets(
        self,
        subject: Optional[str] = None,
        predicate: Optional[str] = None,
        object: Optional[str] = None,
        tier: Optional[str] = None,
        min_confidence: float = 0.0,
        limit: int = 100
    ) -> List[SPOTriplet]:
        """
        Query SPO triplets with filters.

        Args:
            subject: Filter by subject (exact match)
            predicate: Filter by predicate (exact match)
            object: Filter by object (exact match)
            tier: Filter by tier (bronze|silver|gold)
            min_confidence: Minimum confidence threshold
            limit: Maximum results

        Returns:
            List of SPOTriplet instances
        """
        if not self.spo_db:
            return []

        return self.spo_db.query(
            subject=subject,
            predicate=predicate,
            object=object,
            tier=tier,
            min_confidence=min_confidence,
            limit=limit
        )

    def search_spo(self, query_text: str, limit: int = 50) -> List[SPOTriplet]:
        """
        Full-text search in SPO triplets.

        Args:
            query_text: Search query
            limit: Maximum results

        Returns:
            List of SPOTriplet instances ranked by relevance
        """
        if not self.spo_db:
            return []

        return self.spo_db.search(query_text, limit=limit)

    def promote_triplet(self, triplet_id: str, new_tier: str) -> bool:
        """
        Promote triplet to higher tier (Bronze → Silver → Gold).

        Part of Tiered RAG workflow (Cluster 2).

        Args:
            triplet_id: Triplet to promote
            new_tier: New tier (silver | gold)

        Returns:
            True if promoted, False if not found
        """
        if not self.spo_db:
            return False

        return self.spo_db.promote(triplet_id, new_tier)

    def verify_triplet(
        self,
        triplet_id: str,
        verification_source: str
    ) -> bool:
        """
        Mark triplet as verified by a source.

        Used for multi-source verification (Cluster 2).

        Args:
            triplet_id: Triplet to verify
            verification_source: Source that verified this

        Returns:
            True if updated, False if not found
        """
        if not self.spo_db:
            return False

        return self.spo_db.update_provenance(
            triplet_id,
            verified=True,
            verification_source=verification_source
        )

    def get_spo_stats(self) -> Dict[str, Any]:
        """
        Get SPO database statistics.

        Returns:
            Stats dict with triplet counts, tiers, etc.
        """
        if not self.spo_db:
            return {"error": "SPO database not initialized"}

        return self.spo_db.get_stats()

    def migrate_legacy_to_spo(self, limit: int = 100) -> int:
        """
        Migrate legacy NetworkX nodes to SPO triplets.

        This is a helper for gradual migration (Cluster 2 task).

        Args:
            limit: Maximum nodes to migrate

        Returns:
            Number of triplets created
        """
        if not self.spo_db:
            return 0

        migrated = 0

        # Get fact nodes from legacy graph
        fact_nodes = [
            (nid, data) for nid, data in self.graph.nodes(data=True)
            if data.get("type") == "fact"
        ][:limit]

        for node_id, node_data in fact_nodes:
            # Simple heuristic: content as subject-predicate-object
            # In production, use SPOExtractor here
            content = node_data.get("content", "")

            # Create simple triplet (placeholder logic)
            # TODO Cluster 2: Use SPOExtractor for proper parsing
            from src.models.unified_session import SPOProvenance

            triplet = SPOTriplet(
                id=f"migrated_{node_id}",
                subject="Legacy_Node",
                predicate="has_content",
                object=content[:100],  # Truncate
                confidence=node_data.get("confidence", 0.5),
                tier="bronze",
                provenance=SPOProvenance(
                    source_id=node_id,
                    extraction_method="legacy_migration",
                    model_used=None,
                    extracted_at=datetime.utcnow().isoformat()
                ),
                metadata={
                    "legacy_node_id": node_id,
                    "legacy_type": node_data.get("type")
                }
            )

            try:
                self.spo_db.insert(triplet)
                migrated += 1
            except Exception as e:
                print(f"Failed to migrate {node_id}: {e}")

        return migrated


# TODO Sprint 2: Add MCTS for path exploration
