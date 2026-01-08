"""
Multi-AI Response Analyzer.

Analyzes responses from multiple AI services (Claude, GPT-4, Gemini)
using local abliterated models for validation and synthesis.
"""
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from src.core.agent import Agent, Task, AgentOutput
from src.utils.logger import setup_logger


class MultiAIResponseAnalyzer:
    """
    Analyze responses from multiple AI services.

    Uses local quality agent to detect contradictions, identify blind spots,
    and synthesize consensus insights from Claude, GPT-4, and Gemini responses.
    """

    def __init__(self, orchestrator=None):
        """
        Initialize response analyzer.

        Args:
            orchestrator: Reference to Orchestrator (for accessing quality agent)
        """
        self.orchestrator = orchestrator
        self.logger = setup_logger("multi_ai_analyzer")

    def analyze_responses(
        self,
        response_dir: Path,
        analysis_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze multiple AI responses.

        Args:
            response_dir: Directory containing AI response files
            analysis_types: Types of analysis to run
                          (default: ["contradiction", "blind_spots", "synthesis"])

        Returns:
            Analysis results including contradictions, blind spots, and synthesis
        """
        if analysis_types is None:
            analysis_types = ["contradiction", "blind_spots", "consensus", "synthesis"]

        self.logger.info(f"Analyzing responses from: {response_dir}")

        # Load responses
        responses = self._load_responses(response_dir)

        if not responses:
            self.logger.error(f"No responses found in {response_dir}")
            return {
                "error": "No responses found",
                "response_dir": str(response_dir)
            }

        self.logger.info(f"Loaded {len(responses)} responses: {list(responses.keys())}")

        # Run analyses
        results = {
            "sources": list(responses.keys()),
            "analysis_timestamp": datetime.now().isoformat(),
            "analyses": {}
        }

        if "contradiction" in analysis_types:
            results["analyses"]["contradictions"] = self._detect_contradictions(responses)

        if "blind_spots" in analysis_types:
            results["analyses"]["blind_spots"] = self._identify_blind_spots(responses)

        if "consensus" in analysis_types:
            results["analyses"]["consensus"] = self._find_consensus(responses)

        if "synthesis" in analysis_types:
            results["analyses"]["synthesis"] = self._generate_synthesis(
                responses,
                results["analyses"]
            )

        # Calculate overall confidence
        results["confidence_score"] = self._calculate_confidence(results["analyses"])

        return results

    def _load_responses(self, response_dir: Path) -> Dict[str, str]:
        """
        Load AI responses from directory.

        Args:
            response_dir: Directory containing response files

        Returns:
            Dict mapping AI service name to response text
        """
        if not response_dir.exists():
            self.logger.warning(f"Response directory does not exist: {response_dir}")
            return {}

        responses = {}

        # Expected filenames
        expected_files = {
            "claude": ["claude_response.md", "claude.md"],
            "gpt4": ["gpt4_response.md", "gpt4.md", "openai_response.md"],
            "gemini": ["gemini_response.md", "gemini.md", "google_response.md"]
        }

        for ai_name, possible_files in expected_files.items():
            for filename in possible_files:
                file_path = response_dir / filename
                if file_path.exists():
                    try:
                        responses[ai_name] = file_path.read_text()
                        self.logger.debug(f"Loaded {ai_name} response from {filename}")
                        break
                    except Exception as e:
                        self.logger.error(f"Error loading {filename}: {e}")

        # Also check for any other .md files
        for file_path in response_dir.glob("*.md"):
            if file_path.stem not in responses:
                try:
                    responses[file_path.stem] = file_path.read_text()
                    self.logger.debug(f"Loaded additional response: {file_path.stem}")
                except Exception as e:
                    self.logger.error(f"Error loading {file_path}: {e}")

        return responses

    def _detect_contradictions(self, responses: Dict[str, str]) -> Dict[str, Any]:
        """
        Detect contradictions between AI responses.

        Args:
            responses: Dict of AI responses

        Returns:
            Contradiction analysis results
        """
        self.logger.info("Detecting contradictions...")

        if not self.orchestrator:
            return {
                "error": "Orchestrator not available",
                "fallback": "Manual contradiction detection not implemented"
            }

        # Get quality validator agent
        quality_agent = self._get_quality_agent()

        if not quality_agent:
            return {"error": "Quality agent not available"}

        # Build task for contradiction detection
        task = Task(
            task_id="multi_ai_contradiction_detection",
            description=self._build_contradiction_prompt(responses),
            technique="contradiction",
            inputs={"responses": responses},
            temperature=0.7,
            max_tokens=2048
        )

        # Execute
        output = quality_agent.execute_task(task)

        return {
            "raw_output": output.output,
            "success": output.success,
            "metadata": output.metadata
        }

    def _identify_blind_spots(self, responses: Dict[str, str]) -> Dict[str, Any]:
        """
        Identify blind spots (topics missing from all responses).

        Args:
            responses: Dict of AI responses

        Returns:
            Blind spot analysis results
        """
        self.logger.info("Identifying blind spots...")

        quality_agent = self._get_quality_agent()

        if not quality_agent:
            return {"error": "Quality agent not available"}

        task = Task(
            task_id="multi_ai_blind_spot_detection",
            description=self._build_blind_spots_prompt(responses),
            technique="blind_spots",
            inputs={"responses": responses},
            temperature=0.8,
            max_tokens=2048
        )

        output = quality_agent.execute_task(task)

        return {
            "raw_output": output.output,
            "success": output.success,
            "metadata": output.metadata
        }

    def _find_consensus(self, responses: Dict[str, str]) -> Dict[str, Any]:
        """
        Find consensus insights across all AI responses.

        Args:
            responses: Dict of AI responses

        Returns:
            Consensus analysis results
        """
        self.logger.info("Finding consensus...")

        quality_agent = self._get_quality_agent()

        if not quality_agent:
            return {"error": "Quality agent not available"}

        task = Task(
            task_id="multi_ai_consensus",
            description=self._build_consensus_prompt(responses),
            technique="consensus",
            inputs={"responses": responses},
            temperature=0.5,
            max_tokens=2048
        )

        output = quality_agent.execute_task(task)

        return {
            "raw_output": output.output,
            "success": output.success,
            "metadata": output.metadata
        }

    def _generate_synthesis(
        self,
        responses: Dict[str, str],
        analyses: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate synthesis report from all responses and analyses.

        Args:
            responses: Original AI responses
            analyses: Analysis results (contradictions, blind spots, consensus)

        Returns:
            Synthesis report
        """
        self.logger.info("Generating synthesis...")

        quality_agent = self._get_quality_agent()

        if not quality_agent:
            return {"error": "Quality agent not available"}

        task = Task(
            task_id="multi_ai_synthesis",
            description=self._build_synthesis_prompt(responses, analyses),
            inputs={
                "responses": responses,
                "analyses": analyses
            },
            temperature=0.6,
            max_tokens=4096
        )

        output = quality_agent.execute_task(task)

        return {
            "raw_output": output.output,
            "success": output.success,
            "metadata": output.metadata
        }

    def _get_quality_agent(self) -> Optional[Agent]:
        """Get quality validator agent from orchestrator."""
        if not self.orchestrator:
            self.logger.warning("No orchestrator available")
            return None

        # Try to get quality_validator agent
        if "quality_validator" in self.orchestrator.agents:
            return self.orchestrator.agents["quality_validator"]

        # Fallback: any validator role
        for agent in self.orchestrator.agents.values():
            if agent.role == "validator":
                return agent

        # Fallback: first agent
        if self.orchestrator.agents:
            return list(self.orchestrator.agents.values())[0]

        return None

    def _build_contradiction_prompt(self, responses: Dict[str, str]) -> str:
        """Build prompt for contradiction detection."""
        prompt_parts = [
            "# Contradiction Detection Across Multiple AI Responses\n",
            "Analyze the following responses from different AI services and identify any contradictions.\n",
            "## AI Responses\n"
        ]

        for ai_name, response in responses.items():
            prompt_parts.append(f"### {ai_name.upper()} Response:\n")
            prompt_parts.append(response[:2000])  # Limit to avoid token overflow
            prompt_parts.append("\n---\n")

        prompt_parts.append("""
## Task

1. Identify SPECIFIC contradictions between the responses
2. For each contradiction:
   - Quote the conflicting statements
   - Identify which AI services disagree
   - Rate severity (high/medium/low)
   - Suggest which claim is more credible (if possible)

3. Output format:
```markdown
## Contradictions Found

### 1. [Topic]
- **Claude says:** [quote]
- **GPT-4 says:** [quote]
- **Severity:** high/medium/low
- **Analysis:** [which is more credible and why]

### 2. [Next contradiction]
...
```

If no contradictions found, state: "No significant contradictions detected."
""")

        return "".join(prompt_parts)

    def _build_blind_spots_prompt(self, responses: Dict[str, str]) -> str:
        """Build prompt for blind spot identification."""
        prompt_parts = [
            "# Blind Spot Detection Across Multiple AI Responses\n",
            "Identify topics, perspectives, or analyses that are MISSING from ALL responses.\n",
            "## AI Responses\n"
        ]

        for ai_name, response in responses.items():
            prompt_parts.append(f"### {ai_name.upper()}:\n")
            prompt_parts.append(response[:2000])
            prompt_parts.append("\n---\n")

        prompt_parts.append("""
## Task

What important aspects are ALL responses missing?

Consider:
- Critical perspectives not explored
- Important stakeholders not mentioned
- Potential risks not analyzed
- Alternative scenarios not considered
- Data sources not consulted
- Counterarguments not addressed

Output format:
```markdown
## Identified Blind Spots

### 1. [Blind Spot Topic]
- **What's missing:** [description]
- **Why it matters:** [impact]
- **Severity:** critical/important/minor

### 2. [Next blind spot]
...
```
""")

        return "".join(prompt_parts)

    def _build_consensus_prompt(self, responses: Dict[str, str]) -> str:
        """Build prompt for consensus identification."""
        prompt_parts = [
            "# Consensus Identification Across Multiple AI Responses\n",
            "Identify insights where ALL AI services AGREE.\n",
            "## AI Responses\n"
        ]

        for ai_name, response in responses.items():
            prompt_parts.append(f"### {ai_name.upper()}:\n")
            prompt_parts.append(response[:2000])
            prompt_parts.append("\n---\n")

        prompt_parts.append("""
## Task

Find consensus insights:

1. Identify claims/insights present in ALL responses
2. Verify they are substantially the same (not just superficially similar)
3. Rate confidence based on agreement quality

Output format:
```markdown
## Consensus Insights

### 1. [Consensus Topic]
- **Agreement:** [what all AIs agree on]
- **Supporting quotes:**
  - Claude: [quote]
  - GPT-4: [quote]
  - Gemini: [quote]
- **Confidence:** high/medium/low

### 2. [Next consensus]
...
```
""")

        return "".join(prompt_parts)

    def _build_synthesis_prompt(
        self,
        responses: Dict[str, str],
        analyses: Dict[str, Any]
    ) -> str:
        """Build prompt for synthesis generation."""
        prompt_parts = [
            "# Multi-AI Research Synthesis\n",
            "Synthesize insights from multiple AI responses into a coherent analysis.\n",
            "## Original Responses\n"
        ]

        for ai_name in responses.keys():
            prompt_parts.append(f"- {ai_name.upper()}\n")

        prompt_parts.append("\n## Analysis Results\n")

        if "contradictions" in analyses:
            prompt_parts.append(f"### Contradictions\n{analyses['contradictions'].get('raw_output', 'N/A')}\n\n")

        if "blind_spots" in analyses:
            prompt_parts.append(f"### Blind Spots\n{analyses['blind_spots'].get('raw_output', 'N/A')}\n\n")

        if "consensus" in analyses:
            prompt_parts.append(f"### Consensus\n{analyses['consensus'].get('raw_output', 'N/A')}\n\n")

        prompt_parts.append("""
## Task

Create a comprehensive synthesis report:

1. **Executive Summary** (3-5 sentences)
   - Overall assessment of AI responses
   - Key consensus insights
   - Critical contradictions/gaps

2. **Consensus Insights**
   - What can we trust (all AIs agree)
   - Confidence level for each

3. **Contradictions & Resolution**
   - Key disagreements
   - Recommended resolution approach
   - Areas needing human judgment

4. **Identified Blind Spots**
   - Critical gaps in coverage
   - Recommended additional research

5. **Overall Confidence Score**
   - Rate 0.0-1.0 based on:
     - Agreement level
     - Number of contradictions
     - Severity of blind spots

6. **Recommended Next Steps**

Output in clear markdown format.
""")

        return "".join(prompt_parts)

    def _calculate_confidence(self, analyses: Dict[str, Any]) -> float:
        """
        Calculate overall confidence score.

        Args:
            analyses: Analysis results

        Returns:
            Confidence score (0.0-1.0)
        """
        # Simple heuristic - can be made more sophisticated
        score = 1.0

        # Penalize for contradictions
        if "contradictions" in analyses:
            # If analysis failed, moderate penalty
            if not analyses["contradictions"].get("success", True):
                score -= 0.1
            # TODO: Parse output and count contradictions for better scoring

        # Penalize for blind spots
        if "blind_spots" in analyses:
            if not analyses["blind_spots"].get("success", True):
                score -= 0.1

        # Bonus for consensus
        if "consensus" in analyses:
            if analyses["consensus"].get("success", True):
                score += 0.1

        return max(0.0, min(1.0, score))


def analyze_multi_ai_responses(
    response_dir: Path,
    orchestrator=None,
    analysis_types: Optional[List[str]] = None,
    save_results: bool = True
) -> Dict[str, Any]:
    """
    Convenience function to analyze multi-AI responses.

    Args:
        response_dir: Directory containing AI response files
        orchestrator: Orchestrator instance (for accessing quality agent)
        analysis_types: Types of analysis to run
        save_results: Whether to save results to file

    Returns:
        Analysis results

    Example:
        >>> from pathlib import Path
        >>> from src.core.orchestrator import Orchestrator
        >>>
        >>> orchestrator = Orchestrator()
        >>> results = analyze_multi_ai_responses(
        ...     response_dir=Path("research-data/multi-ai/run_001"),
        ...     orchestrator=orchestrator
        ... )
        >>> print(results['confidence_score'])
        >>> print(results['analyses']['synthesis'])
    """
    analyzer = MultiAIResponseAnalyzer(orchestrator=orchestrator)

    results = analyzer.analyze_responses(
        response_dir=Path(response_dir),
        analysis_types=analysis_types
    )

    if save_results:
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path("research-data/validations") / f"multi_ai_analysis_{timestamp}.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        output_path.write_text(json.dumps(results, indent=2))
        results["saved_to"] = str(output_path)

    return results
