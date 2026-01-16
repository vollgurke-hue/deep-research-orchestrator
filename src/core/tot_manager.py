"""
Tree of Thoughts Manager

Manages exploration of complex questions via Tree of Thoughts approach.
Integrates with GraphManager for entity extraction and AxiomManager for filtering.
"""

import uuid
from typing import Any, Dict, List, Optional
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
        model_orchestrator: ModelOrchestrator,
        enable_intelligence: bool = True,
        enable_generative_cot: bool = True,  # Sprint 2: NEW!
        cot_variant_count: int = 3            # Sprint 2: NEW!
    ):
        """
        Initialize ToT Manager.

        Args:
            graph_manager: Knowledge graph for entity storage
            axiom_manager: Optional axiom filter (None = no pruning)
            model_orchestrator: LLM orchestrator for question decomposition
            enable_intelligence: Enable Cluster 2 Intelligence Layer (default: True)
            enable_generative_cot: Enable Sprint 2 Generative CoT (default: True)
            cot_variant_count: Number of CoT variants to generate (default: 3)
        """
        self.graph = graph_manager
        self.axioms = axiom_manager
        self.llm = model_orchestrator
        self.tree: Dict[str, ToTNode] = {}

        # Cluster 2: Intelligence Layer (optional)
        self.intelligence_enabled = enable_intelligence
        self.verifier = None
        self.promoter = None
        self.resolver = None

        if enable_intelligence and hasattr(graph_manager, 'spo_db') and graph_manager.spo_db:
            try:
                from src.core.multi_source_verifier import MultiSourceVerifier
                from src.core.tier_promoter import TierPromoter

                self.verifier = MultiSourceVerifier(graph_manager=graph_manager)
                self.promoter = TierPromoter(
                    graph_manager=graph_manager,
                    verifier=self.verifier,
                    axiom_judge=None  # AxiomJudge is optional (expensive)
                )
                print("✓ Cluster 2 Intelligence Layer enabled (Verification + Promotion)")
            except ImportError as e:
                print(f"Warning: Could not load Cluster 2 components: {e}")
                self.intelligence_enabled = False

        # Sprint 2: Generative CoT + Process Reward Model (NEW!)
        self.generative_cot_enabled = enable_generative_cot
        self.cot_generator = None
        self.prm = None

        if enable_generative_cot:
            try:
                from src.core.cot_generator import CoTGenerator
                from src.core.process_reward_model import ProcessRewardModel

                self.cot_generator = CoTGenerator(
                    model_orchestrator=model_orchestrator,
                    variant_count=cot_variant_count,
                    enable_diversity=True
                )

                self.prm = ProcessRewardModel(
                    axiom_manager=axiom_manager,
                    model_orchestrator=model_orchestrator,
                    enable_llm_scoring=False,  # Use rule-based for speed
                    enable_axiom_check=axiom_manager is not None
                )

                print(f"✓ Sprint 2 Generative CoT enabled ({cot_variant_count} variants)")
            except ImportError as e:
                print(f"Warning: Could not load Sprint 2 components: {e}")
                self.generative_cot_enabled = False

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

        Sprint 2 Enhancement:
        - If generative_cot_enabled=True:
          → Generate 3 CoT variants (analytical, empirical, theoretical)
          → Score each variant with Process Reward Model
          → Select best variant based on score
        - Else:
          → Single answer generation (legacy behavior)

        Args:
            node_id: Node to expand
            use_quality: LLM quality level (FAST/BALANCED/QUALITY)

        Returns:
            True if expansion successful
        """
        node = self.tree.get(node_id)
        if not node:
            return False

        node.status = "exploring"
        node.update_timestamp()

        try:
            # Sprint 2: Multi-variant generation
            if self.generative_cot_enabled and self.cot_generator:
                success = self._expand_node_generative_cot(node, use_quality)
            else:
                success = self._expand_node_single(node, use_quality)

            if not success:
                node.status = "pending"
                return False

            # Evaluate with axioms (existing)
            if self.axioms:
                node.axiom_compatible = self._check_axiom_compatibility(node)

            node.status = "evaluated"
            node.update_timestamp()

            return True

        except Exception as e:
            print(f"Expansion failed for {node_id}: {e}")
            import traceback
            traceback.print_exc()
            node.status = "pending"
            return False

    def _expand_node_single(
        self,
        node: ToTNode,
        use_quality: QualityLevel
    ) -> bool:
        """
        Legacy expansion: Single answer generation.

        Used when generative_cot_enabled=False.
        """
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

        # Extract SPO triplets (Cluster 1)
        spo_triplet_ids = self._extract_spo_triplets(node, response)
        if not hasattr(node, 'spo_triplets'):
            node.spo_triplets = []
        node.spo_triplets.extend(spo_triplet_ids)

        return True

    def _expand_node_generative_cot(
        self,
        node: ToTNode,
        use_quality: QualityLevel
    ) -> bool:
        """
        Sprint 2: Expand node with 3 CoT variants.

        Process:
        1. Generate 3 reasoning variants (analytical, empirical, theoretical)
        2. Score each variant with Process Reward Model
        3. Select best variant based on score
        4. Store best answer in node
        5. Extract SPO triplets from best answer
        6. Apply intelligence layer (existing Cluster 2)
        """
        print(f"\n[Sprint 2] Generating CoT variants for: {node.question[:80]}...")

        # 1. Get graph context (for context-aware generation)
        graph_context = self._get_graph_context(node)

        # 2. Generate 3 CoT variants
        variants = self.cot_generator.generate_variants(
            question=node.question,
            parent_context=graph_context if graph_context else None
        )

        print(f"✓ Generated {len(variants)} CoT variants")

        # 3. Score each variant with Process Reward Model
        variant_scores = []
        for i, variant in enumerate(variants):
            score_result = self.prm.score_variant(variant)
            variant_scores.append({
                "variant": variant,
                "score": score_result['avg_score'],
                "details": score_result
            })

            approach_name = variant.approach.capitalize()
            print(f"  - Variant {chr(65+i)} ({approach_name}): "
                  f"score={score_result['avg_score']:.3f}, "
                  f"steps={len(variant.steps)}, "
                  f"violations={score_result['violations_count']}")

        # 4. Select best variant
        best = max(variant_scores, key=lambda x: x['score'])
        best_variant = best['variant']

        print(f"✓ Selected: Variant {best_variant.variant_id[-1].upper()} "
              f"({best_variant.approach}) with score {best['score']:.3f}")

        # 5. Store results in node
        node.answer = best_variant.conclusion
        node.confidence = best_variant.confidence
        node.reasoning = f"Generative CoT ({best_variant.approach} approach)"

        # Store Sprint 2 metadata
        node.cot_variants = variants  # Store all variants for analysis
        node.selected_variant_id = best_variant.variant_id
        node.reasoning_steps = best_variant.steps  # Step-by-step reasoning
        node.variant_scores = variant_scores  # Detailed scores

        # 6. Extract entities (from best answer)
        entities = self._extract_entities(best_variant.conclusion)
        node.graph_entities = entities

        # 7. Add facts to graph
        fact_ids = self._add_facts_to_graph(node, entities)
        node.graph_facts = fact_ids

        # 8. Extract SPO triplets (existing Cluster 1 integration)
        # Create mock response object for compatibility
        class MockResponse:
            def __init__(self, content):
                self.content = content
                self.model_used = "Sprint2-GenerativeCoT"

        mock_response = MockResponse(best_variant.conclusion)
        spo_triplet_ids = self._extract_spo_triplets(node, mock_response)
        if not hasattr(node, 'spo_triplets'):
            node.spo_triplets = []
        node.spo_triplets.extend(spo_triplet_ids)

        print(f"✓ Extracted {len(spo_triplet_ids)} SPO triplets from best variant")

        return True

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

    # ========================================================================
    # EXTERNAL MODEL INTEGRATION (Sprint 4)
    # ========================================================================

    def generate_external_prompt(self, node: ToTNode) -> str:
        """
        Generate optimized prompt for external model (Claude, GPT-4, Gemini).

        User copies this prompt to external AI and pastes response back.

        Args:
            node: ToTNode to generate prompt for

        Returns:
            Formatted prompt string optimized for external model

        Example:
            prompt = tot.generate_external_prompt(node)
            # User copies to Claude, gets response
            tot.add_external_response(node.node_id, response, "claude-opus")
        """
        # Get graph context
        graph_context = self._get_graph_context(node)

        # Get path context (parent questions)
        path = self.get_path_to_root(node.node_id)
        path_context = ""

        if len(path) > 1:
            parent_questions = []
            for node_id in path[:-1]:  # Exclude current node
                parent = self.tree.get(node_id)
                if parent:
                    parent_questions.append(f"- {parent.question}")

            if parent_questions:
                path_context = "\n\nParent Questions:\n" + "\n".join(parent_questions)

        # Build comprehensive prompt
        prompt = f"""# Research Question

{node.question}
{path_context}"""

        if graph_context:
            prompt += f"""

# Knowledge Context

{graph_context}"""

        prompt += """

# Task

Provide a comprehensive, well-researched answer to this question. Include:

1. **Direct Answer** (2-3 sentences)
2. **Key Insights** (3-5 bullet points with specific examples)
3. **Entities** (List any important entities, companies, concepts, or technologies mentioned)
4. **Confidence** (Your confidence level: Low/Medium/High)

Focus on actionable, specific information rather than generalizations.
"""

        return prompt

    def add_external_response(
        self,
        node_id: str,
        response_text: str,
        model_name: str = "external"
    ) -> bool:
        """
        Add response from external model (manually pasted by user).

        Args:
            node_id: Node that was sent to external model
            response_text: Response from external model (user pasted)
            model_name: Name of external model used

        Returns:
            True if response added successfully

        Process:
        1. Parse response
        2. Extract entities
        3. Add to graph
        4. Evaluate with axioms
        5. Update node status
        """
        node = self.tree.get(node_id)
        if not node:
            return False

        try:
            # Store response
            node.answer = response_text
            node.reasoning = f"Answer from {model_name}"
            node.confidence = self._estimate_confidence(response_text)

            # Extract entities
            entities = self._extract_entities(response_text)
            node.graph_entities = entities

            # Add facts to graph
            fact_ids = self._add_facts_to_graph(node, entities)
            node.graph_facts = fact_ids

            # Evaluate with axioms
            if self.axioms:
                axiom_scores = self._evaluate_node_axioms(node)
                node.axiom_scores = axiom_scores
                node.axiom_compatible = all(score >= 0.3 for score in axiom_scores.values())

            # Update status
            node.status = "evaluated"
            node.update_timestamp()

            return True

        except Exception as e:
            print(f"Failed to add external response for {node_id}: {e}")
            return False

    def _estimate_confidence(self, text: str) -> float:
        """
        Estimate confidence from response text.

        Looks for explicit confidence markers or hedging language.
        """
        text_lower = text.lower()

        # Explicit confidence markers
        if "high confidence" in text_lower or "very confident" in text_lower:
            return 0.9
        elif "medium confidence" in text_lower or "moderately confident" in text_lower:
            return 0.7
        elif "low confidence" in text_lower or "uncertain" in text_lower:
            return 0.5

        # Hedging language reduces confidence
        hedging_words = ["maybe", "possibly", "might", "could", "perhaps", "probably"]
        hedge_count = sum(1 for word in hedging_words if word in text_lower)

        if hedge_count == 0:
            return 0.85
        elif hedge_count <= 2:
            return 0.7
        else:
            return 0.6

    def _evaluate_node_axioms(self, node: ToTNode) -> Dict[str, float]:
        """
        Evaluate node against all active axioms.

        Returns:
            Dict mapping axiom_id to score (0.0-1.0)
        """
        if not self.axioms:
            return {}

        scores = {}

        try:
            # Get all active axioms
            active_axioms = self.axioms.list_axioms()

            for axiom in active_axioms:
                if not axiom.get("enabled", True):
                    continue

                axiom_id = axiom["axiom_id"]

                # Evaluate this node against axiom
                result = self.axioms.evaluate_tot_node(node, axiom_id)

                if result:
                    scores[axiom_id] = result.get("score", 0.5)

        except Exception as e:
            print(f"Axiom evaluation failed for {node.node_id}: {e}")

        return scores

    # ========================================================================
    # SPO Extraction Integration (Cluster 1 - SRO Implementation)
    # ========================================================================

    def _extract_spo_triplets(self, node: ToTNode, response: Any) -> List[str]:
        """
        Extract SPO tripletts from node's answer and store in graph.

        This is the NEW structured knowledge extraction (parallel to entities).

        Args:
            node: ToTNode with answer
            response: LLM response object (for model metadata)

        Returns:
            List of triplet IDs added to graph

        Process:
        1. Check if SPOExtractor available
        2. Extract tripletts from node.answer
        3. Store in GraphManager's SPO database
        4. Return triplet IDs for tracking
        """
        # Check if SPOExtractor is available (lazy import to avoid circular)
        try:
            from src.core.spo_extractor import SPOExtractor
        except ImportError:
            return []

        # Check if GraphManager has SPO database
        if not hasattr(self.graph, 'spo_db') or not self.graph.spo_db:
            return []  # SPO not initialized, skip

        # Create SPOExtractor (reuse LLM orchestrator)
        extractor = SPOExtractor(self.llm, min_confidence=0.6)

        # Extract tripletts from answer
        triplets = extractor.extract_from_text(
            text=node.answer or "",
            context={
                "source_id": node.node_id,
                "node_id": node.node_id,
                "model_used": response.model_used if hasattr(response, 'model_used') else "unknown",
                "question": node.question
            },
            quality=QualityLevel.BALANCED  # Use DeepSeek for better JSON output
        )

        # Store tripletts in graph
        triplet_ids = []
        for triplet in triplets:
            try:
                triplet_id = self.graph.add_spo_triplet(triplet)
                triplet_ids.append(triplet_id)

                # Cluster 2: Intelligence Layer Integration
                if self.intelligence_enabled and self.verifier and self.promoter:
                    self._apply_intelligence_layer(triplet, node.node_id)

            except Exception as e:
                print(f"Failed to store SPO triplet: {e}")

        return triplet_ids

    def _apply_intelligence_layer(self, triplet, current_node_id: str):
        """
        Apply Cluster 2 Intelligence Layer to newly extracted triplet.

        Process:
        1. Find similar existing triplets (cross-verification)
        2. If similar triplet found → add current node as verification source
        3. Try automatic tier promotion

        Args:
            triplet: The newly extracted SPOTriplet
            current_node_id: ID of the ToT node that extracted this triplet
        """
        try:
            # Step 1: Find similar triplets
            similar_triplets = self.verifier.find_similar_triplets(
                triplet=triplet,
                similarity_threshold=0.8  # High threshold for cross-verification
            )

            # Step 2: Cross-verify similar triplets
            for similar_triplet, similarity_score in similar_triplets:
                if similar_triplet.id != triplet.id:  # Don't self-verify
                    # Add current node as verification source
                    result = self.verifier.verify_triplet(
                        triplet_id=similar_triplet.id,
                        new_source=current_node_id
                    )

                    if result.should_promote:
                        # Step 3: Try automatic promotion
                        promo_result = self.promoter.promote_if_eligible(similar_triplet.id)

                        if promo_result.promoted:
                            print(f"  [Cluster 2] Auto-promoted {similar_triplet.id}: "
                                  f"{promo_result.old_tier} → {promo_result.new_tier}")

            # Also check if the newly added triplet can be promoted
            # (it might have been verified by other nodes already)
            promo_result = self.promoter.promote_if_eligible(triplet.id)
            if promo_result.promoted:
                print(f"  [Cluster 2] Auto-promoted {triplet.id}: "
                      f"{promo_result.old_tier} → {promo_result.new_tier}")

        except Exception as e:
            # Intelligence layer errors should not break ToT expansion
            print(f"  [Cluster 2] Intelligence layer error: {e}")
