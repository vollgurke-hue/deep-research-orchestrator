"""
CoT Generator - Generate multiple Chain-of-Thought reasoning variants.

Part of Sprint 2: Intelligence Layer (Gemini's Original Plan)

Inspired by:
- OpenAI o1 (test-time compute scaling)
- DeepMind Self-Echoing Search
- Anthropic Constitutional AI (RLAIF)

Core Concept:
  Instead of generating 1 answer per ToT node, generate 3 reasoning variants:
  - Variant A: Analytical approach (deductive reasoning)
  - Variant B: Empirical approach (evidence-based)
  - Variant C: Theoretical approach (first principles)

  Each variant is then scored by ProcessRewardModel to select the best.

Usage:
    generator = CoTGenerator(model_orchestrator, variant_count=3)

    variants = generator.generate_variants(
        question="What are the benefits of renewable energy?",
        parent_context="Previous reasoning about energy..."
    )

    # Returns 3 CoTVariant objects with different reasoning approaches
    # Each variant has: steps, conclusion, confidence, approach

Design Philosophy:
- Test-time compute scaling: More thinking = Better answers
- Diversity over single-path: Explore multiple reasoning strategies
- Step-wise reasoning: Clear, verifiable steps (not black box)
- Approach-guided: Each variant uses a different reasoning style

Performance:
- 3 variants × ~1000 tokens each = ~3000 tokens per node expansion
- With DeepSeek-R1-14B: ~3s per variant = ~9s total
- Trade-off: 3x cost for higher quality
"""

from typing import List, Optional
from dataclasses import dataclass
import re

from src.core.model_orchestrator import ModelOrchestrator
from src.models.unified_session import UnifiedSession


@dataclass
class CoTVariant:
    """
    A single Chain-of-Thought reasoning variant.

    Attributes:
        variant_id: Unique identifier (e.g., "variant_a")
        approach: Reasoning approach used (analytical/empirical/theoretical)
        steps: List of reasoning steps
        conclusion: Final answer/conclusion
        raw_response: Full LLM response (for debugging)
        confidence: Self-reported confidence (0.0-1.0)
    """
    variant_id: str
    approach: str
    steps: List[str]
    conclusion: str
    raw_response: str
    confidence: float


class CoTGenerator:
    """
    Generate multiple Chain-of-Thought reasoning variants.

    Sprint 2 Component: Generative CoT Integration

    Why multiple variants?
    - Better exploration of reasoning space
    - Different approaches find different insights
    - Step-wise verification catches errors early
    - MCTS can compare reasoning paths

    Approach Types:
    1. Analytical: Break down problem logically, deductive reasoning
    2. Empirical: Use real-world examples and evidence
    3. Theoretical: Apply frameworks and first principles

    Integration with MCTS:
    - ToT node expansion generates 3 variants
    - ProcessRewardModel scores each variant
    - Best variant selected based on score
    - All variants stored for potential reuse
    """

    # Approach templates
    APPROACHES = [
        {
            "id": "analytical",
            "name": "Analytical Approach",
            "instruction": (
                "Break down the problem logically step-by-step using deductive reasoning. "
                "Start with general principles, then derive specific conclusions. "
                "Focus on logical structure and internal consistency."
            ),
            "example_structure": "1. Define key terms → 2. Identify assumptions → 3. Apply logic → 4. Conclude"
        },
        {
            "id": "empirical",
            "name": "Empirical Approach",
            "instruction": (
                "Use real-world examples, case studies, and empirical evidence to build your answer. "
                "Reference specific data, studies, or observed patterns. "
                "Focus on what has actually been observed or measured."
            ),
            "example_structure": "1. Gather evidence → 2. Analyze patterns → 3. Draw inferences → 4. Conclude"
        },
        {
            "id": "theoretical",
            "name": "Theoretical Approach",
            "instruction": (
                "Apply relevant theoretical frameworks and first principles. "
                "Use established theories, models, or conceptual frameworks. "
                "Focus on fundamental mechanisms and causal relationships."
            ),
            "example_structure": "1. Identify theory → 2. Apply framework → 3. Derive implications → 4. Conclude"
        }
    ]

    def __init__(
        self,
        model_orchestrator: ModelOrchestrator,
        variant_count: int = 3,
        enable_diversity: bool = True,
        diversity_temperature: float = 0.7
    ):
        """
        Initialize CoT Generator.

        Args:
            model_orchestrator: LLM provider for text generation
            variant_count: Number of variants to generate (1-3)
            enable_diversity: Use higher temperature for diversity
            diversity_temperature: Temperature for diversity sampling (default: 0.7)
        """
        self.model = model_orchestrator
        self.variant_count = min(variant_count, len(self.APPROACHES))
        self.enable_diversity = enable_diversity
        self.diversity_temperature = diversity_temperature

    def generate_variants(
        self,
        question: str,
        parent_context: Optional[str] = None,
        session: Optional[UnifiedSession] = None
    ) -> List[CoTVariant]:
        """
        Generate multiple CoT reasoning variants for a question.

        Args:
            question: Question to answer
            parent_context: Context from parent ToT node (optional)
            session: Current research session (optional)

        Returns:
            List of CoTVariant objects (length = variant_count)

        Example:
            variants = generator.generate_variants(
                question="What are key challenges in solar adoption?",
                parent_context="Benefits include reduced emissions..."
            )

            # variants[0]: Analytical - policy analysis
            # variants[1]: Empirical - case studies from Germany, California
            # variants[2]: Theoretical - economics of infrastructure investment
        """
        variants = []

        for i, approach in enumerate(self.APPROACHES[:self.variant_count]):
            try:
                # Build prompt for this variant
                prompt = self._build_variant_prompt(
                    question=question,
                    approach=approach,
                    parent_context=parent_context
                )

                # Generate with diversity sampling
                response = self._generate_with_diversity(
                    prompt=prompt,
                    variant_index=i
                )

                # Parse into CoTVariant
                variant = self._parse_response(
                    response=response,
                    approach=approach,
                    variant_index=i
                )

                variants.append(variant)

            except Exception as e:
                print(f"Warning: Failed to generate variant {i}: {e}")
                # Create fallback variant
                variants.append(self._create_fallback_variant(
                    approach=approach,
                    variant_index=i,
                    error=str(e)
                ))

        return variants

    def _build_variant_prompt(
        self,
        question: str,
        approach: dict,
        parent_context: Optional[str]
    ) -> str:
        """
        Build prompt for specific variant approach.

        Prompt structure:
        1. Approach instruction
        2. Context (if available)
        3. Question
        4. Output format instructions
        """
        prompt = f"""You are answering the following question using a {approach['name']}.

{approach['instruction']}

"""

        if parent_context:
            prompt += f"""Previous Context:
{parent_context}

"""

        prompt += f"""Question: {question}

Please provide your answer with clear reasoning steps:

1. **Approach**: Briefly state your reasoning strategy
2. **Step-by-Step Reasoning**: Break down your thinking into numbered steps
3. **Conclusion**: Provide your final answer
4. **Confidence**: Rate your confidence in this answer (0.0 = no confidence, 1.0 = very confident)

Answer:
"""

        return prompt

    def _generate_with_diversity(
        self,
        prompt: str,
        variant_index: int
    ) -> str:
        """
        Generate response with diversity sampling.

        Args:
            prompt: Prompt to send to LLM
            variant_index: Index of variant (0, 1, 2)

        Returns:
            LLM response text
        """
        # Use higher temperature for diversity
        temperature = self.diversity_temperature if self.enable_diversity else 0.2

        # Slight temperature variation per variant
        if self.enable_diversity:
            temperature += variant_index * 0.1  # 0.7, 0.8, 0.9

        response = self.model.generate(
            prompt=prompt,
            max_tokens=1024,
            temperature=min(temperature, 1.0),
            stop=["Question:", "---", "\n\n\n"]
        )

        return response

    def _parse_response(
        self,
        response: str,
        approach: dict,
        variant_index: int
    ) -> CoTVariant:
        """
        Parse LLM response into CoTVariant structure.

        Extracts:
        - Reasoning steps (numbered or bulleted)
        - Conclusion (last paragraph or explicit "Conclusion:" section)
        - Confidence (pattern: "Confidence: 0.8" or "80%")

        Args:
            response: Raw LLM response
            approach: Approach dict
            variant_index: Index (0, 1, 2)

        Returns:
            CoTVariant object
        """
        lines = response.strip().split("\n")

        # Extract steps (lines that start with numbers, bullets, or **Step**)
        steps = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            # Check for step indicators
            if (stripped[0].isdigit() or
                stripped.startswith("-") or
                stripped.startswith("•") or
                stripped.startswith("*") or
                "Step" in stripped):

                # Clean up step text
                step_text = stripped
                # Remove numbering/bullets
                step_text = re.sub(r'^[\d\.\)\-\*\•]+\s*', '', step_text)
                # Remove markdown bold
                step_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', step_text)

                if step_text and len(step_text) > 10:  # Avoid empty steps
                    steps.append(step_text)

        # Extract conclusion
        conclusion = self._extract_conclusion(lines)

        # Extract confidence
        confidence = self._extract_confidence(lines)

        return CoTVariant(
            variant_id=f"variant_{chr(97 + variant_index)}",  # a, b, c
            approach=approach['id'],
            steps=steps if steps else ["No clear steps extracted"],
            conclusion=conclusion,
            raw_response=response,
            confidence=confidence
        )

    def _extract_conclusion(self, lines: List[str]) -> str:
        """Extract conclusion from response lines."""
        # Look for explicit "Conclusion:" section
        for i, line in enumerate(lines):
            if "conclusion" in line.lower() and ":" in line:
                # Get next non-empty line
                for j in range(i + 1, len(lines)):
                    if lines[j].strip():
                        return lines[j].strip()

        # Fallback: last substantial paragraph
        for line in reversed(lines):
            if line.strip() and len(line.strip()) > 20:
                # Skip confidence lines
                if "confidence" not in line.lower():
                    return line.strip()

        return "No clear conclusion extracted"

    def _extract_confidence(self, lines: List[str]) -> float:
        """
        Extract confidence score from response.

        Patterns:
        - "Confidence: 0.8"
        - "Confidence: 80%"
        - "I am 80% confident"
        """
        for line in lines:
            if "confidence" in line.lower():
                # Try to extract number
                match = re.search(r'(\d+\.?\d*)', line)
                if match:
                    value = float(match.group(1))
                    # Handle percentage format
                    if value > 1.0:
                        value /= 100.0
                    return min(1.0, max(0.0, value))

        # Default: moderate confidence
        return 0.7

    def _create_fallback_variant(
        self,
        approach: dict,
        variant_index: int,
        error: str
    ) -> CoTVariant:
        """Create fallback variant on error."""
        return CoTVariant(
            variant_id=f"variant_{chr(97 + variant_index)}",
            approach=approach['id'],
            steps=[f"Error generating variant: {error}"],
            conclusion="Unable to generate answer",
            raw_response="",
            confidence=0.0
        )
