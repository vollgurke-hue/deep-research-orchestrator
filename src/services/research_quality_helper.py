#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
research_quality_helper.py - Research Input Quality Helper

Helps users improve their research description and goals BEFORE starting.
Uses local LLM to evaluate and suggest improvements.
"""
import json
import re
from pathlib import Path
from typing import Dict, Any

from src.models.llama_cpp_client import LlamaCppClient


class ResearchQualityHelper:
    """
    Evaluates and improves research input quality.

    Provides:
    - Quality score (0-100%) for description + goal
    - Specific suggestions for improvement
    - Iterative refinement
    """

    def __init__(self, model_config_path: str = None, use_mock: bool = True):
        """Initialize with local model configuration."""
        self.use_mock = use_mock

        if not use_mock:
            if model_config_path is None:
                # Use tier1_fast for quick analysis
                config_dir = Path(__file__).parents[2] / "config" / "models"
                model_config_path = str(config_dir / "tier1_fast.json")

            self.client = LlamaCppClient(model_config_path)
        else:
            self.client = None  # No model needed in mock mode

    def evaluate_research_input(
        self,
        description: str,
        goal: str,
        research_type: str = "product"
    ) -> Dict[str, Any]:
        """
        Evaluate quality of research description and goal.

        Args:
            description: User's research description
            goal: User's explicit research goal
            research_type: Type of research

        Returns:
            {
                "quality_score": int (0-100),
                "description_score": int (0-100),
                "goal_score": int (0-100),
                "strengths": [str],
                "weaknesses": [str],
                "suggestions": [str],
                "improved_description": str (optional),
                "improved_goal": str (optional)
            }
        """

        # MOCK MODE: Return realistic test data
        if self.use_mock:
            return {
                "quality_score": 75,
                "description_score": 70,
                "goal_score": 80,
                "strengths": [
                    "Clear target audience identified (students, schools)",
                    "Specific product features mentioned (personalized learning, adaptive exercises)",
                    "Well-defined market segment (German education sector)"
                ],
                "weaknesses": [
                    "Missing information about budget constraints",
                    "No mention of team size or technical expertise",
                    "Timeline not specified for market validation"
                ],
                "suggestions": [
                    "Add specific budget range (e.g., '€50k-100k development budget')",
                    "Clarify what 'comprehensive market analysis' means - which metrics?",
                    "Specify desired validation outcome (e.g., '100 beta users in 3 months')",
                    "Mention competitor landscape awareness (e.g., 'aware of Duolingo, want to differentiate')",
                    "Define technical feasibility scope (MVP vs full product)"
                ],
                "improved_description": """Ich möchte ein SaaS-Produkt für AI-gestütztes Tutoring im Bildungsbereich validieren, speziell für MINT-Fächer in Klassen 7-12. Das Produkt soll Schülern und Studenten personalisierte Lernhilfe bieten durch automatische Schwachstellenanalyse und adaptive Übungsgenerierung. Unser Team hat 2 Entwickler mit ML-Erfahrung. Budget: €75k für 6-monatiges MVP. Zielgruppe sind zunächst deutsche Gymnasien (200+ Schulen) und Universitäten (50+ Unis) mit ersten Partnerschaften geplant.""",
                "improved_goal": """Ich brauche eine umfassende Marktanalyse (TAM/SAM/SOM für deutsche Bildungstech), Wettbewerbsanalyse (Top 5 Konkurrenten + Differenzierung), technische Machbarkeit (ML-Modell-Auswahl, Infrastruktur-Kosten) und Geschäftsmodell-Validierung (Pricing 10-30€/Schüler/Monat, Break-Even nach 18 Monaten). Ziel: Go/No-Go Entscheidung in 8 Wochen."""
            }

        # REAL MODE: Use local model
        prompt = f"""# RESEARCH INPUT QUALITY EVALUATION

You are an expert research consultant. Evaluate the quality of this research input and provide constructive feedback.

## USER'S INPUT

**Research Type:** {research_type}

**Description:**
{description}

**Goal:**
{goal}

## YOUR TASK

Evaluate the input quality across these dimensions:

### 1. DESCRIPTION Quality (0-100%):
- **Clarity:** Is it clear what they want to research?
- **Specificity:** Is it specific enough or too vague?
- **Scope:** Is the scope well-defined?
- **Context:** Does it provide sufficient background?

### 2. GOAL Quality (0-100%):
- **Clarity:** Is the goal explicit and measurable?
- **Actionability:** Can you determine what success looks like?
- **Alignment:** Does the goal match the description?
- **Completeness:** Are all desired outcomes stated?

### 3. OVERALL Quality (average of both)

## EVALUATION CRITERIA

**High Quality (80-100%):**
- Clear, specific, well-scoped
- Explicit, measurable goals
- Provides context and constraints
- Actionable and realistic

**Medium Quality (50-79%):**
- Somewhat clear but could be more specific
- Goals stated but not fully explicit
- Missing some important context
- Needs refinement

**Low Quality (0-49%):**
- Vague or too broad
- Goals unclear or missing
- Insufficient context
- Needs major improvement

## OUTPUT FORMAT

Return ONLY valid JSON:

{{
  "quality_score": 75,
  "description_score": 70,
  "goal_score": 80,
  "strengths": [
    "Clear target audience identified",
    "Specific industry mentioned"
  ],
  "weaknesses": [
    "Description too broad - needs narrower scope",
    "Goal doesn't specify success criteria"
  ],
  "suggestions": [
    "Add specific market segment (e.g., 'B2B SaaS for enterprise')",
    "Define what 'validation' means - MVP testing? Market research?",
    "Specify timeframe or budget constraints if relevant"
  ],
  "improved_description": "Optional: Improved version if score < 70%",
  "improved_goal": "Optional: Improved version if score < 70%"
}}

Be constructive and specific. Focus on making the research MORE actionable and focused.
"""

        try:
            # Call local model
            response = self.client.generate(prompt, max_tokens=1500, temperature=0.3)

            # Extract JSON
            result = self._extract_json(response)

            # Validate
            result = self._validate_quality_data(result)

            return result

        except Exception as e:
            print(f"Error in quality evaluation: {e}")
            # Return safe fallback
            return {
                "quality_score": 50,
                "description_score": 50,
                "goal_score": 50,
                "strengths": [],
                "weaknesses": ["Unable to evaluate - try again"],
                "suggestions": ["Please review your input manually"],
                "improved_description": "",
                "improved_goal": ""
            }

    def _extract_json(self, text: str) -> Dict[str, Any]:
        """Extract JSON from LOCAL model response."""
        # Try JSON code block
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except:
                pass

        # Try raw JSON
        json_match = re.search(r'(\{[^\{]*?"quality_score".*?\})', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except:
                pass

        # Greedy match
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except:
                pass

        raise ValueError("Local model failed to produce valid JSON")

    def _validate_quality_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean quality evaluation data."""
        # Ensure scores are 0-100
        quality = max(0, min(100, int(data.get('quality_score', 50))))
        desc_score = max(0, min(100, int(data.get('description_score', 50))))
        goal_score = max(0, min(100, int(data.get('goal_score', 50))))

        return {
            "quality_score": quality,
            "description_score": desc_score,
            "goal_score": goal_score,
            "strengths": data.get('strengths', [])[:5],  # Max 5
            "weaknesses": data.get('weaknesses', [])[:5],
            "suggestions": data.get('suggestions', [])[:5],
            "improved_description": data.get('improved_description', ''),
            "improved_goal": data.get('improved_goal', '')
        }
