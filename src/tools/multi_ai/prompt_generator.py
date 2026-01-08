"""
Multi-AI Prompt Generator.

Generates comprehensive research prompts for manual querying of external AI services.
"""
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import json


class MultiAIPromptGenerator:
    """
    Generate comprehensive prompts for multi-AI research workflows.

    Creates detailed prompts optimized for Claude, GPT-4, and Gemini,
    incorporating research categories and structured output requirements.
    """

    def __init__(self, output_dir: Path = Path("research-prompts")):
        """
        Initialize prompt generator.

        Args:
            output_dir: Directory to save generated prompts
        """
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True)

    def create_prompt(
        self,
        topic: str,
        categories: List[str],
        output_format: str = "markdown",
        depth: str = "comprehensive",
        additional_instructions: Optional[str] = None
    ) -> str:
        """
        Create a comprehensive research prompt.

        Args:
            topic: Main research topic
            categories: Research categories to cover
            output_format: Desired output format (markdown, json, structured)
            depth: Research depth (quick, standard, comprehensive, deep)
            additional_instructions: Optional custom instructions

        Returns:
            Generated prompt text
        """
        # Build prompt sections
        sections = []

        # Header
        sections.append(self._build_header(topic, depth))

        # Context
        sections.append(self._build_context(topic))

        # Categories
        sections.append(self._build_categories_section(categories))

        # Output format requirements
        sections.append(self._build_output_format(output_format, categories))

        # Quality requirements
        sections.append(self._build_quality_requirements(depth))

        # Additional instructions
        if additional_instructions:
            sections.append(f"\n## Additional Instructions\n\n{additional_instructions}")

        # Footer
        sections.append(self._build_footer())

        return "\n\n".join(sections)

    def _build_header(self, topic: str, depth: str) -> str:
        """Build prompt header."""
        depth_descriptions = {
            "quick": "Quick Overview",
            "standard": "Standard Analysis",
            "comprehensive": "Comprehensive Research",
            "deep": "Deep Analysis with Validation"
        }

        return f"""# Research Request: {topic}

**Depth Level:** {depth_descriptions.get(depth, "Standard Analysis")}
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M")}

---"""

    def _build_context(self, topic: str) -> str:
        """Build research context section."""
        return f"""## Research Objective

Please conduct thorough research on: **{topic}**

This research will be validated against multiple AI perspectives (Claude, GPT-4, Gemini) to ensure:
- Factual accuracy through cross-validation
- Detection of contradictions or inconsistencies
- Identification of blind spots or gaps
- Synthesis of consensus insights"""

    def _build_categories_section(self, categories: List[str]) -> str:
        """Build research categories section."""
        category_map = {
            "market_size": {
                "title": "Market Size & Opportunity",
                "questions": [
                    "What is the current market size?",
                    "What is the projected growth rate?",
                    "What are the key market segments?",
                    "What is the addressable market (TAM, SAM, SOM)?"
                ]
            },
            "competition": {
                "title": "Competitive Landscape",
                "questions": [
                    "Who are the major competitors?",
                    "What are their market positions?",
                    "What are their strengths and weaknesses?",
                    "What are the competitive moats?"
                ]
            },
            "trends": {
                "title": "Market Trends",
                "questions": [
                    "What are the current market trends?",
                    "What emerging technologies are relevant?",
                    "What regulatory changes are occurring?",
                    "What are the future projections?"
                ]
            },
            "technical_feasibility": {
                "title": "Technical Feasibility",
                "questions": [
                    "What technologies are required?",
                    "What are the technical challenges?",
                    "What is the development complexity?",
                    "What existing solutions can be leveraged?"
                ]
            },
            "user_needs": {
                "title": "User Needs & Pain Points",
                "questions": [
                    "What are the primary user pain points?",
                    "What solutions currently exist?",
                    "What are the unmet needs?",
                    "What is the user willingness to pay?"
                ]
            },
            "risks": {
                "title": "Risks & Challenges",
                "questions": [
                    "What are the major risks?",
                    "What could cause failure?",
                    "What are the regulatory risks?",
                    "What are the market adoption risks?"
                ]
            }
        }

        sections = ["## Research Categories\n"]

        for i, cat in enumerate(categories, 1):
            cat_info = category_map.get(cat, {
                "title": cat.replace("_", " ").title(),
                "questions": [f"Analyze {cat.replace('_', ' ')} aspects"]
            })

            sections.append(f"### {i}. {cat_info['title']}\n")
            sections.append("Please address:")
            for q in cat_info['questions']:
                sections.append(f"- {q}")
            sections.append("")

        return "\n".join(sections)

    def _build_output_format(self, format_type: str, categories: List[str]) -> str:
        """Build output format requirements."""
        if format_type == "json":
            example = {
                "summary": "Executive summary (3-5 sentences)",
                "categories": {
                    cat: {
                        "findings": ["Finding 1", "Finding 2"],
                        "sources": ["Source 1", "Source 2"],
                        "confidence": "high/medium/low"
                    }
                    for cat in categories[:2]  # Show example for first 2
                },
                "key_insights": ["Insight 1", "Insight 2"],
                "gaps": ["Gap 1", "Gap 2"]
            }

            return f"""## Required Output Format

Please structure your response as JSON:

```json
{json.dumps(example, indent=2)}
```"""

        elif format_type == "structured":
            return f"""## Required Output Format

Please structure your response with clear sections:

1. **Executive Summary** (3-5 sentences)
2. **Category Analysis** (one section per category)
   - Key Findings
   - Supporting Evidence
   - Sources
   - Confidence Level
3. **Cross-Category Insights**
4. **Identified Gaps** (areas needing more research)
5. **Sources** (comprehensive list)"""

        else:  # markdown (default)
            return f"""## Required Output Format

Please provide a well-structured markdown response with:

- **Clear headings** for each research category
- **Bullet points** for findings
- **Data and statistics** where available
- **Source citations** (inline or footnoted)
- **Confidence indicators** (high/medium/low for each claim)
- **Identified gaps** section highlighting areas needing deeper research"""

    def _build_quality_requirements(self, depth: str) -> str:
        """Build quality requirements section."""
        depth_requirements = {
            "quick": [
                "Focus on high-level overview",
                "Prioritize breadth over depth",
                "Include key statistics and trends"
            ],
            "standard": [
                "Balance breadth and depth",
                "Include supporting evidence",
                "Cite credible sources",
                "Identify 2-3 major gaps"
            ],
            "comprehensive": [
                "Deep analysis of each category",
                "Multiple sources per claim",
                "Quantitative data where possible",
                "Identify assumptions and uncertainties",
                "Highlight contradictions in sources",
                "Comprehensive gap analysis"
            ],
            "deep": [
                "Exhaustive coverage of all aspects",
                "Critical analysis of sources",
                "Identify hidden assumptions",
                "Premortem analysis (what could go wrong)",
                "Scenario analysis (best/worst/likely cases)",
                "Meta-analysis of research quality"
            ]
        }

        requirements = depth_requirements.get(depth, depth_requirements["standard"])

        return f"""## Quality Requirements

To ensure high-quality analysis:

{chr(10).join(f'- {req}' for req in requirements)}

**Important:**
- Clearly distinguish between facts, estimates, and speculation
- Flag low-confidence claims
- Cite specific sources (not just "according to research")"""

    def _build_footer(self) -> str:
        """Build prompt footer."""
        return """---

**For Multi-AI Validation:**

This prompt will be sent to multiple AI services (Claude, GPT-4, Gemini). Your response will be:
1. Cross-validated for consistency
2. Analyzed for contradictions
3. Synthesized for consensus insights
4. Used to identify blind spots

Please provide your most thorough and well-sourced analysis."""

    def save_prompt(
        self,
        prompt: str,
        topic: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Path:
        """
        Save generated prompt to file.

        Args:
            prompt: Prompt text
            topic: Research topic (for filename)
            metadata: Optional metadata to save

        Returns:
            Path to saved prompt file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_topic = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in topic)
        safe_topic = safe_topic.replace(' ', '_')[:50]

        filename = f"prompt_{timestamp}_{safe_topic}.md"
        filepath = self.output_dir / filename

        # Save prompt
        filepath.write_text(prompt)

        # Save metadata if provided
        if metadata:
            metadata_path = filepath.with_suffix('.json')
            metadata_path.write_text(json.dumps(metadata, indent=2))

        return filepath


def generate_multi_ai_prompt(
    topic: str,
    categories: List[str],
    output_format: str = "markdown",
    depth: str = "comprehensive",
    additional_instructions: Optional[str] = None,
    save: bool = True
) -> Dict[str, Any]:
    """
    Convenience function to generate and optionally save a multi-AI prompt.

    Args:
        topic: Research topic
        categories: List of research categories
        output_format: Output format (markdown, json, structured)
        depth: Research depth level
        additional_instructions: Optional custom instructions
        save: Whether to save prompt to file

    Returns:
        Dict with prompt text, save path (if saved), and instructions

    Example:
        >>> result = generate_multi_ai_prompt(
        ...     topic="AI Tutoring Market Analysis",
        ...     categories=["market_size", "competition", "trends"],
        ...     depth="comprehensive"
        ... )
        >>> print(result['prompt'])
        >>> print(f"Saved to: {result['save_path']}")
    """
    generator = MultiAIPromptGenerator()

    prompt = generator.create_prompt(
        topic=topic,
        categories=categories,
        output_format=output_format,
        depth=depth,
        additional_instructions=additional_instructions
    )

    result = {
        "prompt": prompt,
        "instructions": (
            "1. Copy this prompt to Claude, GPT-4, and Gemini\n"
            "2. Save each response to research-data/multi-ai/\n"
            "   - claude_response.md\n"
            "   - gpt4_response.md\n"
            "   - gemini_response.md\n"
            "3. Run analyze_multi_ai_responses() to synthesize"
        ),
        "metadata": {
            "topic": topic,
            "categories": categories,
            "output_format": output_format,
            "depth": depth,
            "generated_at": datetime.now().isoformat()
        }
    }

    if save:
        save_path = generator.save_prompt(prompt, topic, result["metadata"])
        result["save_path"] = str(save_path)

    return result
