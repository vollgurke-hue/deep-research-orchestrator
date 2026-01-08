"""
Debate Pattern Manager

Implements 3-model sequential debate pattern for:
- Resolving contradictions in knowledge graph
- Evaluating competing ToT paths
- Making difficult decisions with adversarial reasoning

Pattern:
1. Model A: Argues for Position A
2. Model B: Counter-argues for Position B
3. Judge Model: Makes final decision

This is NOT parallel agents - it's a sequential discussion pattern.
"""

from dataclasses import dataclass
from typing import Dict, Optional, List, Any
from .model_orchestrator import ModelOrchestrator, ModelCapability, QualityLevel
from .graph_manager import GraphManager


@dataclass
class DebateResult:
    """
    Result of a debate between two positions.

    Attributes:
        topic: The debate topic/question
        argument_a: Pro argument (Model A)
        argument_b: Counter argument (Model B)
        verdict: Judge's decision
        winner: Which side won ("A", "B", or "tie")
        confidence: Judge's confidence in verdict (0.0-1.0)
        reasoning: Judge's reasoning
    """
    topic: str
    argument_a: str
    argument_b: str
    verdict: str
    winner: str  # "A", "B", or "tie"
    confidence: float
    reasoning: Optional[str] = None


class DebateManager:
    """
    Manages adversarial debate pattern for decision-making.

    Use Cases:
    1. Resolve contradictions in knowledge graph
    2. Evaluate competing ToT exploration paths
    3. Make difficult decisions with diverse perspectives

    Pattern:
        Model A → Model B → Judge
        (Sequential, not parallel)

    Example:
        debate_mgr = DebateManager(orchestrator, graph)

        # Resolve contradiction
        result = debate_mgr.resolve_contradiction(node_a_id, node_b_id)
        if result.winner == "A":
            graph.prune_node(node_b_id)

        # Evaluate ToT paths
        result = debate_mgr.evaluate_tot_paths(path_1, path_2)
        chosen_path = path_1 if result.winner == "A" else path_2
    """

    def __init__(
        self,
        model_orchestrator: ModelOrchestrator,
        graph_manager: Optional[GraphManager] = None
    ):
        """
        Initialize Debate Manager.

        Args:
            model_orchestrator: LLM orchestrator for debate
            graph_manager: Optional knowledge graph for context
        """
        self.llm = model_orchestrator
        self.graph = graph_manager

    def debate(
        self,
        topic: str,
        position_a: str,
        position_b: str,
        context: Optional[str] = None,
        quality: QualityLevel = QualityLevel.BALANCED
    ) -> DebateResult:
        """
        Run debate between two positions.

        Args:
            topic: Question/decision to debate
            position_a: First position description
            position_b: Second position description
            context: Optional background context
            quality: LLM quality level for debate

        Returns:
            DebateResult with verdict and reasoning

        Example:
            result = debate_mgr.debate(
                topic="Which framework should we use?",
                position_a="React - widely adopted, good ecosystem",
                position_b="Vue - simpler, better documentation",
                quality=QualityLevel.QUALITY  # Use best model for important decision
            )
        """
        # Phase 1: Model A argues for Position A
        argument_a = self._generate_argument(
            topic=topic,
            position=position_a,
            context=context,
            quality=quality
        )

        # Phase 2: Model B counter-argues for Position B
        argument_b = self._generate_counter_argument(
            topic=topic,
            position=position_b,
            opposing_argument=argument_a,
            context=context,
            quality=quality
        )

        # Phase 3: Judge evaluates both arguments
        verdict_data = self._judge_debate(
            topic=topic,
            argument_a=argument_a,
            argument_b=argument_b,
            context=context,
            quality=quality
        )

        return DebateResult(
            topic=topic,
            argument_a=argument_a,
            argument_b=argument_b,
            verdict=verdict_data["verdict"],
            winner=verdict_data["winner"],
            confidence=verdict_data["confidence"],
            reasoning=verdict_data["reasoning"]
        )

    def _generate_argument(
        self,
        topic: str,
        position: str,
        context: Optional[str],
        quality: QualityLevel
    ) -> str:
        """Generate argument for Position A"""
        context_section = f"\n\nContext:\n{context}" if context else ""

        prompt = f"""You are Model A in a debate. Argue FOR the following position.

Topic: {topic}

Your Position: {position}
{context_section}

Provide a strong, reasoned argument (2-3 sentences) supporting this position.
Focus on:
- Key benefits and advantages
- Evidence or reasoning
- Addressing potential concerns

Your argument:"""

        response = self.llm.generate(
            prompt=prompt,
            capability=ModelCapability.REASONING,
            quality=quality
        )

        return response.content.strip()

    def _generate_counter_argument(
        self,
        topic: str,
        position: str,
        opposing_argument: str,
        context: Optional[str],
        quality: QualityLevel
    ) -> str:
        """Generate counter-argument for Position B"""
        context_section = f"\n\nContext:\n{context}" if context else ""

        prompt = f"""You are Model B in a debate. You have heard Model A's argument. Now argue FOR your position.

Topic: {topic}

Your Position: {position}

Model A's Argument:
{opposing_argument}
{context_section}

Provide a strong counter-argument (2-3 sentences) supporting your position.
You may address weaknesses in Model A's argument, but focus primarily on the strengths of your own position.

Your counter-argument:"""

        response = self.llm.generate(
            prompt=prompt,
            capability=ModelCapability.REASONING,
            quality=quality
        )

        return response.content.strip()

    def _judge_debate(
        self,
        topic: str,
        argument_a: str,
        argument_b: str,
        context: Optional[str],
        quality: QualityLevel
    ) -> Dict[str, Any]:
        """
        Judge evaluates both arguments and makes decision.

        Returns:
            {
                "verdict": str,
                "winner": "A" | "B" | "tie",
                "confidence": float,
                "reasoning": str
            }
        """
        context_section = f"\n\nContext:\n{context}" if context else ""

        prompt = f"""You are an impartial judge evaluating a debate between two positions.

Topic: {topic}

Position A's Argument:
{argument_a}

Position B's Argument:
{argument_b}
{context_section}

Evaluate both arguments objectively and decide which position is stronger.

Format your response EXACTLY as:
WINNER: [A, B, or TIE]
CONFIDENCE: [0.0-1.0]
REASONING: [2-3 sentences explaining your decision]

Your judgment:"""

        # Judge always uses BALANCED or better (needs VALIDATION capability)
        judge_quality = quality if quality != QualityLevel.FAST else QualityLevel.BALANCED

        response = self.llm.generate(
            prompt=prompt,
            capability=ModelCapability.VALIDATION,
            quality=judge_quality
        )

        # Parse judge response
        return self._parse_judge_response(response.content)

    def _parse_judge_response(self, response: str) -> Dict[str, Any]:
        """Parse judge's structured response"""
        winner = "tie"
        confidence = 0.5
        reasoning = ""
        verdict = response.strip()

        lines = response.strip().split('\n')
        for line in lines:
            line = line.strip()

            if line.startswith("WINNER:"):
                winner_text = line.split(":", 1)[1].strip().upper()
                if winner_text in ["A", "B", "TIE"]:
                    winner = winner_text.lower()

            elif line.startswith("CONFIDENCE:"):
                try:
                    conf_text = line.split(":", 1)[1].strip()
                    confidence = float(conf_text)
                    confidence = max(0.0, min(1.0, confidence))
                except ValueError:
                    pass

            elif line.startswith("REASONING:"):
                reasoning = line.split(":", 1)[1].strip()

        return {
            "verdict": verdict,
            "winner": winner,
            "confidence": confidence,
            "reasoning": reasoning
        }

    def resolve_contradiction(
        self,
        node_a_id: str,
        node_b_id: str,
        quality: QualityLevel = QualityLevel.QUALITY
    ) -> DebateResult:
        """
        Resolve contradiction between two graph nodes.

        Args:
            node_a_id: First contradicting node
            node_b_id: Second contradicting node
            quality: LLM quality (use QUALITY for important decisions)

        Returns:
            DebateResult indicating which node is more reliable

        Example:
            result = debate_mgr.resolve_contradiction(
                node_a_id="fact_123",
                node_b_id="fact_456",
                quality=QualityLevel.QUALITY
            )

            if result.winner == "A":
                graph.prune_node(node_b_id)
            elif result.winner == "B":
                graph.prune_node(node_a_id)
        """
        if not self.graph:
            raise ValueError("GraphManager required for resolve_contradiction")

        node_a = self.graph.get_node(node_a_id)
        node_b = self.graph.get_node(node_b_id)

        if not node_a or not node_b:
            raise ValueError(f"Nodes not found: {node_a_id}, {node_b_id}")

        # Extract content and metadata
        content_a = node_a.get("content", "")
        content_b = node_b.get("content", "")
        source_a = node_a.get("source", "unknown")
        source_b = node_b.get("source", "unknown")
        conf_a = node_a.get("confidence", 0.5)
        conf_b = node_b.get("confidence", 0.5)

        topic = f"Which fact is more reliable?"

        position_a = f"Fact A: {content_a} (source: {source_a}, confidence: {conf_a:.2f})"
        position_b = f"Fact B: {content_b} (source: {source_b}, confidence: {conf_b:.2f})"

        context = "These two facts contradict each other. Evaluate based on source reliability, confidence, and content quality."

        return self.debate(
            topic=topic,
            position_a=position_a,
            position_b=position_b,
            context=context,
            quality=quality
        )

    def evaluate_tot_paths(
        self,
        path_a: List[str],
        path_b: List[str],
        tot_tree: Dict[str, Any],
        quality: QualityLevel = QualityLevel.BALANCED
    ) -> DebateResult:
        """
        Evaluate two competing ToT exploration paths.

        Args:
            path_a: First path (list of node IDs)
            path_b: Second path (list of node IDs)
            tot_tree: ToT tree dict for looking up nodes
            quality: LLM quality level

        Returns:
            DebateResult indicating which path is more promising

        Example:
            result = debate_mgr.evaluate_tot_paths(
                path_a=["root", "node_a", "node_a1"],
                path_b=["root", "node_b", "node_b1"],
                tot_tree=tot_manager.tree,
                quality=QualityLevel.BALANCED
            )

            chosen_path = path_a if result.winner == "A" else path_b
        """
        # Extract questions from paths
        questions_a = [tot_tree[nid].question for nid in path_a if nid in tot_tree]
        questions_b = [tot_tree[nid].question for nid in path_b if nid in tot_tree]

        # Calculate path metrics
        avg_conf_a = sum(tot_tree[nid].confidence for nid in path_a if nid in tot_tree) / max(len(path_a), 1)
        avg_conf_b = sum(tot_tree[nid].confidence for nid in path_b if nid in tot_tree) / max(len(path_b), 1)

        topic = "Which research path is more promising to explore?"

        position_a = f"Path A ({len(path_a)} steps, avg confidence {avg_conf_a:.2f}): " + " → ".join(questions_a)
        position_b = f"Path B ({len(path_b)} steps, avg confidence {avg_conf_b:.2f}): " + " → ".join(questions_b)

        context = "Evaluate based on question quality, logical progression, and likelihood of leading to valuable insights."

        return self.debate(
            topic=topic,
            position_a=position_a,
            position_b=position_b,
            context=context,
            quality=quality
        )
