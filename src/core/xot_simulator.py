"""
XoT Simulator - Fast heuristic for MCTS prior estimation.

Part of Cluster 1: Foundations (SRO Implementation)
Provides quick 0-1 scores for path likelihood without full simulation.

Design Philosophy:
- Fast heuristic, not perfect reasoning (<2s per call)
- Uses lightweight 8B model (Llama-3.1-8B)
- Minimal context (last 3 nodes only)
- Simple 0-1 score output
"""

import re
from typing import Optional, List
from datetime import datetime

from src.core.tot_node import ToTNode
from src.core.model_orchestrator import ModelOrchestrator, ModelCapability, QualityLevel


class XoTSimulator:
    """
    XoT (Everything of Thoughts) Simulator.

    Provides fast heuristic estimates for MCTS node selection.
    Instead of full simulation, XoT gives a quick "gut feeling" score.

    Process:
    1. Build path summary (last 3 nodes)
    2. Generate XoT prompt (very short, <500 tokens)
    3. Call fast LLM (Llama-3.1-8B)
    4. Parse 0-1 score
    5. Return prior for UCB1 boost

    Usage:
        xot = XoTSimulator(model_orchestrator)
        prior = xot.simulate_quick(node, depth=3)
        ucb1_boosted = ucb1 + (prior * xot_weight)
    """

    # XoT prompt template (very short for speed)
    XOT_SIMULATION_PROMPT = """You are a research heuristic. Quickly estimate if this path is promising.

Current Path:
{path_summary}

Next Question:
{node_question}

Rate likelihood of success (0.0 = dead end, 1.0 = very promising).
Consider: relevance, actionability, logical flow.

Respond with ONLY a number: 0.0-1.0
"""

    def __init__(
        self,
        model_orchestrator: ModelOrchestrator,
        depth: int = 3,
        fallback_score: float = 0.5,
        timeout: float = 3.0
    ):
        """
        Initialize XoT Simulator.

        Args:
            model_orchestrator: LLM orchestrator for fast model access
            depth: How many parent nodes to include in path summary
            fallback_score: Default score if parsing fails (neutral)
            timeout: Maximum time to wait for LLM response
        """
        self.llm = model_orchestrator
        self.depth = depth
        self.fallback_score = fallback_score
        self.timeout = timeout

        # Stats tracking
        self.stats = {
            "total_simulations": 0,
            "successful_parses": 0,
            "failed_parses": 0,
            "avg_score": 0.0,
            "total_time": 0.0
        }

    def simulate_quick(
        self,
        node: ToTNode,
        depth: Optional[int] = None
    ) -> float:
        """
        Quick simulation for MCTS prior estimation.

        Args:
            node: ToTNode to evaluate
            depth: Override default depth

        Returns:
            Prior probability (0.0-1.0) indicating path promise

        Example:
            prior = xot.simulate_quick(node)
            # prior = 0.85 → looks very promising!
            # prior = 0.2 → probably dead end
        """
        start_time = datetime.utcnow()
        depth = depth or self.depth

        try:
            # Build path summary
            path_summary = self._build_path_summary(node, depth)

            # Generate XoT prompt
            prompt = self.XOT_SIMULATION_PROMPT.format(
                path_summary=path_summary,
                node_question=node.question or "Unknown question"
            )

            # Call fast LLM
            response = self.llm.generate(
                prompt=prompt,
                capability=ModelCapability.REASONING,
                quality=QualityLevel.FAST,  # Selects XoT model (8B, fast)
                max_tokens=50,  # Very short response
                temperature=0.3  # Low temperature for consistent scores
            )

            # Parse 0-1 score
            score = self._parse_score(response.content)

            # Update stats
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            self._update_stats(score, elapsed, success=True)

            return score

        except Exception as e:
            print(f"XoT simulation failed: {e}")
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            self._update_stats(self.fallback_score, elapsed, success=False)
            return self.fallback_score

    def _build_path_summary(self, node: ToTNode, depth: int) -> str:
        """
        Build path summary from node ancestry.

        Walks up parent chain to build context.
        Limits to 'depth' nodes to keep prompt short.

        Args:
            node: Starting node
            depth: Number of parent nodes to include

        Returns:
            Formatted path summary string
        """
        path_nodes = []
        current = node

        # Walk up parent chain
        for _ in range(depth):
            if current is None:
                break
            path_nodes.append(current)
            # Note: This requires parent reference in ToTNode
            # For now, we'll just use the current node
            break  # TODO: Implement parent traversal when available

        # Build summary (most recent last)
        path_nodes.reverse()

        summary_lines = []
        for i, n in enumerate(path_nodes):
            level = "→ " * i
            question = n.question or "Unknown"
            answer = n.answer[:100] if n.answer else "Not answered yet"
            summary_lines.append(f"{level}{question}")
            if n.answer:
                summary_lines.append(f"   Answer: {answer}...")

        return "\n".join(summary_lines) if summary_lines else "Root node"

    def _parse_score(self, response_text: str) -> float:
        """
        Parse 0-1 score from LLM response.

        Handles various formats:
        - "0.85"
        - "Score: 0.85"
        - "I would rate this 0.85"
        - "0.85/1.0"
        - "```0.85```" (code blocks)
        - "```\n0.85\n```" (multi-line code blocks)

        Returns:
            Parsed score (0.0-1.0) or fallback_score if parsing fails
        """
        # Clean response
        response_text = response_text.strip()

        # Remove code block markers (```)
        response_text = re.sub(r'```[\w]*\n?', '', response_text)
        response_text = response_text.strip()

        # Try to extract number with regex
        patterns = [
            r'^(0?\.\d+|1\.0+|0)$',  # Just the number: "0.85"
            r'(0?\.\d+|1\.0+|0)\s*(?:/|$)',  # With slash or end: "0.85/1.0"
            r'(?:score|rate|likelihood)[:\s]+(0?\.\d+|1\.0+|0)',  # With label
            r'(0?\.\d+|1\.0+|0)',  # Any number anywhere (fallback)
        ]

        for pattern in patterns:
            match = re.search(pattern, response_text, re.IGNORECASE)
            if match:
                try:
                    score = float(match.group(1))
                    # Clamp to [0, 1]
                    score = max(0.0, min(1.0, score))
                    return score
                except ValueError:
                    continue

        # Try simple float conversion of first line
        try:
            first_line = response_text.split('\n')[0].strip()
            score = float(first_line)
            score = max(0.0, min(1.0, score))
            return score
        except ValueError:
            pass

        # Parsing failed
        print(f"Failed to parse XoT score from: {response_text[:100]}")
        return self.fallback_score

    def _update_stats(self, score: float, elapsed: float, success: bool):
        """
        Update internal statistics.

        Args:
            score: Score returned
            elapsed: Time taken (seconds)
            success: Whether parsing succeeded
        """
        self.stats["total_simulations"] += 1

        if success:
            self.stats["successful_parses"] += 1
        else:
            self.stats["failed_parses"] += 1

        # Update running average score
        total = self.stats["total_simulations"]
        old_avg = self.stats["avg_score"]
        self.stats["avg_score"] = (old_avg * (total - 1) + score) / total

        # Update total time
        self.stats["total_time"] += elapsed

    def get_stats(self) -> dict:
        """
        Get XoT simulation statistics.

        Returns:
            Dict with stats (total_simulations, success_rate, avg_score, etc.)
        """
        total = self.stats["total_simulations"]

        if total == 0:
            return {
                "total_simulations": 0,
                "success_rate": 0.0,
                "avg_score": 0.0,
                "avg_time": 0.0
            }

        return {
            "total_simulations": total,
            "success_rate": self.stats["successful_parses"] / total,
            "avg_score": self.stats["avg_score"],
            "avg_time": self.stats["total_time"] / total,
            "failed_parses": self.stats["failed_parses"]
        }

    def reset_stats(self):
        """Reset statistics."""
        self.stats = {
            "total_simulations": 0,
            "successful_parses": 0,
            "failed_parses": 0,
            "avg_score": 0.0,
            "total_time": 0.0
        }
