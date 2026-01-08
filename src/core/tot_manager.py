"""
Tree of Thoughts Manager

Manages exploration of complex questions via Tree of Thoughts approach.
Integrates with GraphManager for entity extraction and AxiomManager for filtering.
"""

import uuid
from typing import Dict, List, Optional
from .tot_node import ToTNode
from .graph_manager import GraphManager
from .axiom_manager import AxiomManager
from .model_orchestrator import ModelOrchestrator, ModelCapability, QualityLevel


class ToTManager:
    """
    Manages Tree of Thoughts exploration.

    Workflow:
    1. User asks complex question (root)
    2. decompose_question() → creates sub-questions (branches)
    3. expand_node() → explores sub-question with LLM
    4. Extracts entities → adds to GraphManager
    5. Evaluates with axioms → prunes bad branches
    6. MCTS selects next node to explore
    7. Repeat until satisfied

    Example:
        tot = ToTManager(graph, axiom_mgr, orchestrator)

        # Create root question
        root_id = tot.create_root("What e-commerce niche should I pursue?")

        # Decompose into sub-questions
        tot.decompose_question(root_id, branching_factor=3)

        # Explore a branch
        tot.expand_node(child_id)

        # Get best path
        path = tot.get_best_path()
    """

    def __init__(
        self,
        graph_manager: GraphManager,
        axiom_manager: Optional[AxiomManager],
        model_orchestrator: ModelOrchestrator
    ):
        """
        Initialize ToT Manager.

        Args:
            graph_manager: Knowledge graph for entity storage
            axiom_manager: Optional axiom filter (None = no pruning)
            model_orchestrator: LLM orchestrator for question decomposition
        """
        self.graph = graph_manager
        self.axioms = axiom_manager
        self.llm = model_orchestrator
        self.tree: Dict[str, ToTNode] = {}

    def create_root(self, question: str) -> str:
        """
        Create root node for exploration tree.

        Args:
            question: The main research question

        Returns:
            Root node ID
        """
        node_id = f"tot_root_{uuid.uuid4().hex[:8]}"

        root = ToTNode(
            node_id=node_id,
            parent_id=None,
            question=question,
            depth=0,
            status="pending"
        )

        self.tree[node_id] = root
        return node_id

    def decompose_question(
        self,
        node_id: str,
        branching_factor: int = 3,
        max_depth: int = 3
    ) -> List[str]:
        """
        Decompose question into sub-questions using LLM.

        Args:
            node_id: Node to decompose
            branching_factor: Number of sub-questions to generate
            max_depth: Maximum tree depth (prevents infinite expansion)

        Returns:
            List of child node IDs

        Example:
            Q: "What e-commerce niche should I pursue?"
            →
            1. "What markets have high customer friction?"
            2. "What markets have low competition?"
            3. "What markets align with my skills?"
        """
        node = self.tree.get(node_id)
        if not node:
            raise ValueError(f"Node {node_id} not found")

        # Check depth limit
        if node.depth >= max_depth:
            print(f"Max depth {max_depth} reached for node {node_id}")
            return []

        # Update status
        node.status = "exploring"
        node.update_timestamp()

        # Generate sub-questions using LLM
        prompt = self._create_decomposition_prompt(node.question, branching_factor)

        try:
            response = self.llm.generate(
                prompt=prompt,
                capability=ModelCapability.REASONING,
                quality=QualityLevel.FAST  # Fast model for decomposition
            )

            # Parse sub-questions from response
            sub_questions = self._parse_sub_questions(response.content)

            # Create child nodes
            child_ids = []
            for i, sub_q in enumerate(sub_questions[:branching_factor]):
                child_id = f"tot_{node_id}_{i}_{uuid.uuid4().hex[:6]}"

                child = ToTNode(
                    node_id=child_id,
                    parent_id=node_id,
                    question=sub_q,
                    depth=node.depth + 1,
                    status="pending"
                )

                self.tree[child_id] = child
                node.add_child(child_id)
                child_ids.append(child_id)

            node.status = "evaluated"
            node.update_timestamp()

            return child_ids

        except Exception as e:
            print(f"Decomposition failed for {node_id}: {e}")
            node.status = "pending"
            return []

    def _create_decomposition_prompt(self, question: str, n: int) -> str:
        """Create prompt for question decomposition"""
        return f"""You are a research question decomposer. Break down complex questions into simpler sub-questions.

Main Question: "{question}"

Generate exactly {n} sub-questions that, when answered, would help answer the main question.
Each sub-question should be:
- Specific and focused
- Answerable independently
- Complementary (covering different aspects)

Format your response as a numbered list:
1. [First sub-question]
2. [Second sub-question]
3. [Third sub-question]

Sub-questions:"""

    def _parse_sub_questions(self, llm_response: str) -> List[str]:
        """
        Parse sub-questions from LLM response.

        Expects numbered list format:
        1. Question one
        2. Question two
        3. Question three
        """
        questions = []
        lines = llm_response.strip().split('\n')

        for line in lines:
            line = line.strip()
            # Match "1. Question" or "1) Question" format
            if line and (line[0].isdigit() or line.startswith('-')):
                # Remove number prefix
                question = line.split('.', 1)[-1].split(')', 1)[-1].strip()
                if question and len(question) > 10:  # Valid question
                    questions.append(question)

        return questions

    def expand_node(
        self,
        node_id: str,
        use_quality: QualityLevel = QualityLevel.BALANCED
    ) -> bool:
        """
        Expand node by answering its question with LLM.

        Args:
            node_id: Node to expand
            use_quality: LLM quality level (FAST/BALANCED/QUALITY)

        Returns:
            True if expansion successful

        Process:
        1. Get relevant graph context
        2. Generate answer with LLM
        3. Extract entities from answer
        4. Add entities to graph
        5. Evaluate with axioms
        6. Update node with results
        """
        node = self.tree.get(node_id)
        if not node:
            return False

        node.status = "exploring"
        node.update_timestamp()

        try:
            # Get relevant graph context
            graph_context = self._get_graph_context(node)

            # Create expansion prompt
            prompt = self._create_expansion_prompt(node.question, graph_context)

            # Generate answer
            response = self.llm.generate(
                prompt=prompt,
                capability=ModelCapability.REASONING,
                quality=use_quality
            )

            # Store answer
            node.answer = response.content
            node.confidence = 0.8  # TODO: Extract from LLM metadata
            node.reasoning = f"Generated by {response.model_used}"

            # Extract entities (simplified - in production use NER)
            entities = self._extract_entities(response.content)
            node.graph_entities = entities

            # Add facts to graph
            fact_ids = self._add_facts_to_graph(node, entities)
            node.graph_facts = fact_ids

            # Evaluate with axioms
            if self.axioms:
                node.axiom_compatible = self._check_axiom_compatibility(node)

            node.status = "evaluated"
            node.update_timestamp()

            return True

        except Exception as e:
            print(f"Expansion failed for {node_id}: {e}")
            node.status = "pending"
            return False

    def _get_graph_context(self, node: ToTNode) -> str:
        """
        Get relevant graph context for node expansion.

        Uses parent node's entities to find relevant facts.
        """
        if not node.parent_id:
            return ""

        parent = self.tree.get(node.parent_id)
        if not parent or not parent.graph_entities:
            return ""

        # Get subgraph around parent entities (if any exist in graph)
        try:
            # Take first entity as center
            center = parent.graph_entities[0]
            if center in self.graph.graph.nodes:
                subgraph = self.graph.get_ego_graph(center, depth=1)
                return self.graph.to_markdown(node_ids=list(subgraph.nodes), max_nodes=10)
        except Exception:
            pass

        return ""

    def _create_expansion_prompt(self, question: str, graph_context: str) -> str:
        """Create prompt for node expansion"""
        if graph_context:
            return f"""Answer the following research question based on the provided context.

Context:
{graph_context}

Question: {question}

Provide a clear, concise answer (2-3 sentences). Focus on actionable insights."""
        else:
            return f"""Answer the following research question.

Question: {question}

Provide a clear, concise answer (2-3 sentences). Focus on actionable insights."""

    def _extract_entities(self, text: str) -> List[str]:
        """
        Extract entities from text.

        Simplified implementation: extracts capitalized phrases.
        In production, use proper NER (spaCy, transformers).
        """
        # Placeholder: extract words starting with capital letters
        words = text.split()
        entities = []

        for word in words:
            cleaned = word.strip('.,!?()[]{}":;')
            if cleaned and cleaned[0].isupper() and len(cleaned) > 2:
                entities.append(cleaned.lower())

        return list(set(entities))[:10]  # Limit to 10 entities

    def _add_facts_to_graph(self, node: ToTNode, entities: List[str]) -> List[str]:
        """
        Add extracted facts to knowledge graph.

        Creates fact nodes and relationships.
        """
        fact_ids = []

        if not node.answer:
            return fact_ids

        # Create main fact node
        fact_id = f"fact_{node.node_id}"

        success = self.graph.add_node(
            node_id=fact_id,
            node_type="fact",
            content=node.answer[:200],  # Limit content
            confidence=node.confidence,
            source=f"ToT exploration (node {node.node_id})",
            metadata={
                "tot_node": node.node_id,
                "question": node.question
            }
        )

        if success:
            fact_ids.append(fact_id)

        return fact_ids

    def _check_axiom_compatibility(self, node: ToTNode) -> bool:
        """
        Check if node's answer is compatible with axioms.

        Returns:
            True if compatible, False if should be pruned
        """
        if not self.axioms or not node.graph_facts:
            return True

        # Check each fact against axioms
        for fact_id in node.graph_facts:
            node_data = self.graph.get_node(fact_id)
            if not node_data:
                continue

            # Score with axioms
            score = self.axioms.score_node(node_data)
            node.axiom_scores[fact_id] = score

            # If any fact scores too low, mark incompatible
            if score < 0.3:
                return False

        return True

    def prune_branch(self, node_id: str, reason: str = "low_value"):
        """
        Prune branch starting from node.

        Args:
            node_id: Node to prune
            reason: Reason for pruning (for logging)
        """
        node = self.tree.get(node_id)
        if not node:
            return

        node.status = "pruned"
        node.reasoning = f"Pruned: {reason}"
        node.update_timestamp()

        # Recursively prune children
        for child_id in node.children:
            self.prune_branch(child_id, reason)

    def get_active_leaves(self) -> List[str]:
        """
        Get all leaf nodes that haven't been pruned.

        Returns:
            List of node IDs
        """
        leaves = []

        for node_id, node in self.tree.items():
            if node.is_leaf() and not node.is_pruned():
                leaves.append(node_id)

        return leaves

    def get_path_to_root(self, node_id: str) -> List[str]:
        """
        Get path from node to root.

        Returns:
            List of node IDs from root to node
        """
        path = []
        current_id = node_id

        while current_id:
            path.insert(0, current_id)
            current = self.tree.get(current_id)
            if not current:
                break
            current_id = current.parent_id

        return path

    def get_best_path(self) -> List[str]:
        """
        Get best path through tree (highest average value).

        Uses MCTS values to select path.

        Returns:
            List of node IDs from root to best leaf
        """
        # Find best leaf (highest avg value)
        best_leaf = None
        best_value = -1.0

        for node_id, node in self.tree.items():
            if node.is_leaf() and not node.is_pruned():
                avg_val = node.avg_value()
                if avg_val > best_value:
                    best_value = avg_val
                    best_leaf = node_id

        if not best_leaf:
            return []

        return self.get_path_to_root(best_leaf)

    def get_stats(self) -> Dict:
        """
        Get exploration statistics.

        Returns:
            Stats dict
        """
        total = len(self.tree)
        evaluated = sum(1 for n in self.tree.values() if n.is_explored())
        pruned = sum(1 for n in self.tree.values() if n.is_pruned())
        pending = sum(1 for n in self.tree.values() if n.status == "pending")

        return {
            "total_nodes": total,
            "evaluated": evaluated,
            "pruned": pruned,
            "pending": pending,
            "max_depth": max((n.depth for n in self.tree.values()), default=0)
        }
