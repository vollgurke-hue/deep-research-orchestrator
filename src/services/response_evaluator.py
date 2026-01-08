"""
Response Evaluator Service

Evaluates AI model responses using a local LLM to assess:
1. Relevance - How relevant is the response to the user's specific research question?
2. Accuracy - How accurate and fact-based is the information provided?

This enables intelligent decision-making about whether more external models are needed.
"""

import json
import logging
from typing import Dict, Any, List
from pathlib import Path

from src.models.llama_cpp_client import LlamaCppClient

logger = logging.getLogger(__name__)


class ResponseEvaluator:
    """
    Evaluates AI responses for relevance and accuracy using local LLM.

    Workflow:
    1. User pastes response from external model (Claude, GPT-4, etc.)
    2. Local model evaluates response
    3. Returns scores + recommendation (need_more_models: bool)
    """

    def __init__(self, model_config_path: str = "config/models/tier1_fast.json"):
        self.model = LlamaCppClient(model_config_path)
        self.max_responses = 3  # Maximum responses (stop after 3 regardless of quality)
        self.relevance_threshold = 75  # Minimum relevance score to proceed early
        self.accuracy_threshold = 75   # Minimum accuracy score to proceed early

    def evaluate_response(
        self,
        prompt: str,
        response_text: str = None,
        user_context: str = "",
        model_name: str = "unknown",
        response: str = None,  # Backward compatibility
        research_context: str = None  # Backward compatibility
    ) -> Dict[str, Any]:
        """
        Evaluate a single AI model response.

        Args:
            prompt: The original research prompt sent to external model
            response_text: The response received from external model
            user_context: The original user research request
            model_name: Name of the external model (e.g., "claude-opus", "gpt-4")

        Returns:
            {
                "model_name": str,
                "relevance_score": int (0-100),
                "accuracy_score": int (0-100),
                "strengths": [str],
                "weaknesses": [str],
                "confidence": float (0-1),
                "evaluation_notes": str
            }
        """

        # Backward compatibility
        if response_text is None and response is not None:
            response_text = response
        if user_context == "" and research_context is not None:
            user_context = research_context

        # Mock mode for testing (set to False to use real model)
        USE_MOCK = False

        if USE_MOCK:
            return self._mock_evaluation(model_name, response_text)

        # Real evaluation using local LLM
        evaluation_prompt = self._build_evaluation_prompt(
            prompt, response_text, user_context
        )

        try:
            result = self.model.generate(
                prompt=evaluation_prompt,
                max_tokens=500,
                temperature=0.3  # Low temperature for consistent evaluation
            )

            # Parse evaluation result
            evaluation = self._parse_evaluation(result)
            evaluation["model_name"] = model_name

            return evaluation

        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            return {
                "model_name": model_name,
                "relevance_score": 50,
                "accuracy_score": 50,
                "strengths": [],
                "weaknesses": [f"Evaluation failed: {str(e)}"],
                "confidence": 0.0,
                "evaluation_notes": "Could not evaluate response"
            }

    def _build_evaluation_prompt(
        self,
        original_prompt: str,
        response: str,
        research_context: str
    ) -> str:
        """Build evaluation prompt for local LLM"""

        prompt = f"""# EVALUATION TASK

You are evaluating an AI model's response to a research prompt.

## ORIGINAL RESEARCH CONTEXT
{research_context}

## RESEARCH PROMPT
{original_prompt}

## AI MODEL RESPONSE
{response}

## YOUR TASK
Evaluate this response on two dimensions:

1. **RELEVANCE (0-100)**
   - How relevant is this response to the specific research question?
   - Does it address what was actually asked?
   - Is it focused on the user's needs?

2. **ACCURACY (0-100)**
   - How accurate and factual is the information?
   - Are claims well-supported?
   - Are there any obvious errors or hallucinations?

## OUTPUT FORMAT (JSON)
{{
  "relevance_score": <0-100>,
  "accuracy_score": <0-100>,
  "strengths": ["strength 1", "strength 2"],
  "weaknesses": ["weakness 1", "weakness 2"],
  "confidence": <0.0-1.0>,
  "evaluation_notes": "brief summary"
}}

Respond ONLY with valid JSON.
"""
        return prompt

    def _parse_evaluation(self, llm_output: str) -> Dict[str, Any]:
        """Parse JSON evaluation from LLM output"""
        try:
            # Try to extract JSON from output
            start = llm_output.find('{')
            end = llm_output.rfind('}') + 1

            if start >= 0 and end > start:
                json_str = llm_output[start:end]
                return json.loads(json_str)
            else:
                raise ValueError("No JSON found in output")

        except Exception as e:
            logger.error(f"Failed to parse evaluation: {e}")
            return {
                "relevance_score": 50,
                "accuracy_score": 50,
                "strengths": [],
                "weaknesses": ["Could not parse evaluation"],
                "confidence": 0.0,
                "evaluation_notes": "Parsing failed"
            }

    def _mock_evaluation(self, model_name: str, response: str) -> Dict[str, Any]:
        """Mock evaluation for testing"""

        # Simulate different quality levels based on model name
        base_scores = {
            "claude-opus": (92, 88),
            "claude-sonnet": (88, 85),
            "gpt-4": (90, 87),
            "gpt-3.5": (75, 72),
            "gemini-pro": (85, 83),
            "default": (80, 78)
        }

        relevance, accuracy = base_scores.get(
            model_name.lower(),
            base_scores["default"]
        )

        # Add some variance based on response length
        response_length = len(response)
        if response_length < 200:
            relevance -= 10
            accuracy -= 5
        elif response_length > 2000:
            relevance += 5
            accuracy += 5

        return {
            "model_name": model_name,
            "relevance_score": min(100, max(0, relevance)),
            "accuracy_score": min(100, max(0, accuracy)),
            "strengths": [
                "Well-structured response",
                "Addresses key points",
                "Good depth of analysis"
            ],
            "weaknesses": [
                "Could provide more specific examples",
                "Some assertions need citations"
            ],
            "confidence": 0.85,
            "evaluation_notes": f"Response from {model_name} shows good quality overall"
        }

    def aggregate_evaluations(
        self,
        evaluations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Aggregate multiple evaluations and decide if more models are needed.

        NEW LOGIC:
        - Start with 1 response, evaluate
        - If quality is good (>= threshold) → Can proceed (early stop)
        - If quality is low → Need more models
        - MAX 3 responses → Force stop, proceed anyway

        Returns:
            {
                "total_responses": int,
                "avg_relevance": float,
                "avg_accuracy": float,
                "best_model": str,
                "worst_model": str,
                "need_more_models": bool,
                "recommendation": str,
                "can_proceed": bool
            }
        """

        if not evaluations:
            return {
                "total_responses": 0,
                "avg_relevance": 0.0,
                "avg_accuracy": 0.0,
                "best_model": None,
                "worst_model": None,
                "need_more_models": True,
                "recommendation": "No responses yet. Add your first external model response.",
                "can_proceed": False
            }

        total = len(evaluations)
        avg_relevance = sum(e["relevance_score"] for e in evaluations) / total
        avg_accuracy = sum(e["accuracy_score"] for e in evaluations) / total

        # Find best and worst
        best = max(evaluations, key=lambda e: e["relevance_score"] + e["accuracy_score"])
        worst = min(evaluations, key=lambda e: e["relevance_score"] + e["accuracy_score"])

        # Decision logic
        reached_max = total >= self.max_responses
        quality_good = (
            avg_relevance >= self.relevance_threshold and
            avg_accuracy >= self.accuracy_threshold
        )

        # Can always proceed (minimum is 1)
        can_proceed = True

        # Need more models ONLY if:
        # 1. Haven't reached max (3) AND
        # 2. Quality is below threshold
        need_more = not reached_max and not quality_good

        # Recommendation
        if reached_max:
            recommendation = (
                f"Maximum responses reached ({self.max_responses}). "
                f"Quality: Relevance {avg_relevance:.1f}%, Accuracy {avg_accuracy:.1f}%. "
                "Proceeding to synthesis."
            )
        elif quality_good:
            recommendation = (
                f"Quality threshold met (Relevance: {avg_relevance:.1f}%, Accuracy: {avg_accuracy:.1f}%). "
                f"You can proceed now or add more models (up to {self.max_responses - total} more)."
            )
        else:
            recommendation = (
                f"Quality below threshold (Relevance: {avg_relevance:.1f}%, Accuracy: {avg_accuracy:.1f}%). "
                f"Consider adding {min(2, self.max_responses - total)} more external model(s)."
            )

        return {
            "total_responses": total,
            "avg_relevance": round(avg_relevance, 1),
            "avg_accuracy": round(avg_accuracy, 1),
            "best_model": best["model_name"],
            "worst_model": worst["model_name"],
            "need_more_models": need_more,
            "recommendation": recommendation,
            "can_proceed": can_proceed
        }
