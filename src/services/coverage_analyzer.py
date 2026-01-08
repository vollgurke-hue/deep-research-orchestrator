#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
coverage_analyzer.py - Local Coverage Analysis Service

Analyzes external model responses (text) and extracts structured coverage data.
Uses LOCAL model to maintain control over coverage calculation.
"""
import json
import re
from pathlib import Path
from typing import Dict, Any, List

from src.models.llama_cpp_client import LlamaCppClient


class CoverageAnalyzer:
    """
    Analyzes coverage responses from external models using local LLM.

    Key principle: NEVER trust external JSON - always analyze text locally.
    """

    def __init__(self, model_config_path: str = None):
        """Initialize with local model configuration."""
        if model_config_path is None:
            # Use tier1_fast for quick analysis
            config_dir = Path(__file__).parents[2] / "config" / "models"
            model_config_path = str(config_dir / "tier1_fast.json")

        self.client = LlamaCppClient(model_config_path)

    def analyze_external_coverage(
        self,
        external_text: str,
        current_themes: List[Dict[str, Any]],
        research_goal: str,
        research_type: str = "product"
    ) -> Dict[str, Any]:
        """
        Analyze external model's coverage response and extract structured data.

        Args:
            external_text: Raw text response from external model (Claude, GPT-4, etc.)
            current_themes: Current thematic hierarchy
            research_goal: User's research goal
            research_type: Type of research

        Returns:
            {
                "coverage_percentage": int,
                "covered_aspects": [str],
                "missing_critical_aspects": [str],
                "rationale": str,
                "recommendation": str,
                "suggested_themes": [...]
            }
        """

        # Build analysis prompt for LOCAL model
        themes_json = json.dumps(current_themes, indent=2)

        prompt = f"""# COVERAGE EXTRACTION TASK

You are analyzing a coverage analysis report from an external AI model. Your task is to extract structured information from their text response.

## EXTERNAL MODEL'S ANALYSIS
{external_text}

## ORIGINAL CONTEXT
Research Goal: {research_goal}
Research Type: {research_type}
Current Themes Count: {len(current_themes)}

## YOUR TASK
Extract the following information from the external analysis:

1. **Coverage Percentage** (0-100):
   - What coverage % did they estimate or suggest?
   - If not explicitly stated, infer from their assessment
   - Be conservative - round down if uncertain

2. **Covered Aspects** (list):
   - Which aspects did they say ARE adequately covered?
   - Extract specific mentions

3. **Missing Critical Aspects** (list):
   - Which aspects did they identify as MISSING or gaps?
   - Prioritize by importance

4. **Rationale** (text):
   - Summarize WHY they gave this coverage assessment
   - Keep it concise (2-3 sentences)

5. **Recommendation** (text):
   - What did they recommend to improve coverage?
   - Concise summary

6. **Suggested Themes** (structured):
   - Did they suggest specific new themes to add?
   - Extract theme names and descriptions
   - If not explicit, infer from their "missing aspects" and recommendations

## OUTPUT FORMAT
Return ONLY valid JSON (no markdown, no explanation):

{{
  "coverage_percentage": 65,
  "covered_aspects": [
    "Aspect 1 mentioned as covered",
    "Aspect 2 they said is addressed"
  ],
  "missing_critical_aspects": [
    "Gap 1 they identified",
    "Gap 2 they highlighted"
  ],
  "rationale": "Brief summary of their reasoning",
  "recommendation": "Their key recommendation",
  "suggested_themes": [
    {{
      "theme_id": "theme_regulatory_compliance",
      "theme_name": "Regulatory Compliance & Data Protection",
      "description": "Analysis of GDPR, data protection laws, and regulatory requirements",
      "relevance_score": 85,
      "sub_themes": []
    }}
  ]
}}

Be accurate to the external analysis. If coverage % not stated, estimate conservatively based on tone (e.g., "good coverage" = 75%, "significant gaps" = 50%).
"""

        try:
            # Call local model
            response = self.client.generate(prompt, max_tokens=2000, temperature=0.3)

            # Extract JSON from response
            result = self._extract_json(response)

            # Validate and clean
            result = self._validate_and_clean(result)

            return result

        except Exception as e:
            print(f"Error in coverage analysis: {e}")
            # Return safe fallback
            return {
                "coverage_percentage": 50,
                "covered_aspects": ["Unable to parse external analysis"],
                "missing_critical_aspects": ["Analysis failed - please review manually"],
                "rationale": f"Error analyzing external response: {str(e)}",
                "recommendation": "Please try again or review coverage manually",
                "suggested_themes": []
            }

    def _extract_json(self, text: str) -> Dict[str, Any]:
        """
        Extract JSON from LOCAL model's response.

        The LOCAL model should return JSON, but we handle various formats.
        """
        # Try 1: Find JSON code block (```json ... ```)
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError as e:
                print(f"⚠️  JSON decode error in code block: {e}")
                pass

        # Try 2: Find raw JSON object
        json_match = re.search(r'(\{[^\{]*?"coverage_percentage".*?\})', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError as e:
                print(f"⚠️  JSON decode error in raw JSON: {e}")
                pass

        # Try 3: Extract just the main object (greedy match)
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError as e:
                print(f"⚠️  JSON decode error in greedy match: {e}")
                pass

        # Fallback: If LOCAL model failed to produce JSON, raise error
        print(f"❌ LOCAL model did not produce valid JSON. Response preview: {text[:200]}")
        raise ValueError("Local model failed to produce valid JSON structure")

    def _validate_and_clean(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean extracted data."""
        # Ensure coverage percentage is 0-100
        coverage = data.get('coverage_percentage', 50)
        coverage = max(0, min(100, int(coverage)))

        return {
            "coverage_percentage": coverage,
            "covered_aspects": data.get('covered_aspects', []),
            "missing_critical_aspects": data.get('missing_critical_aspects', []),
            "rationale": data.get('rationale', ''),
            "recommendation": data.get('recommendation', ''),
            "suggested_themes": data.get('suggested_themes', [])
        }
