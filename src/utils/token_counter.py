"""
Token counting utility for context window management.

Provides accurate token counting for different models and context window tracking.
"""

import tiktoken
from typing import Dict, List, Any, Optional
from pathlib import Path
import json


class TokenCounter:
    """Token counter with model-specific limits and safety thresholds."""

    # Model configurations with context limits
    MODEL_CONFIGS = {
        "tier1_fast": {
            "model_id": "mistral-7b-instruct",
            "context_window": 8192,
            "safe_limit_percent": 60,
            "warning_limit_percent": 85,
            "output_buffer_percent": 25
        },
        "tier2_quality": {
            "model_id": "mixtral-8x7b-instruct",
            "context_window": 32768,
            "safe_limit_percent": 60,
            "warning_limit_percent": 85,
            "output_buffer_percent": 25
        },
        "tier3_deep": {
            "model_id": "llama-70b-instruct",
            "context_window": 4096,
            "safe_limit_percent": 60,
            "warning_limit_percent": 85,
            "output_buffer_percent": 25
        }
    }

    def __init__(self, model_config_id: str = "tier1_fast"):
        """
        Initialize token counter.

        Args:
            model_config_id: ID from MODEL_CONFIGS or path to model config JSON
        """
        # Load model config
        if model_config_id in self.MODEL_CONFIGS:
            self.config = self.MODEL_CONFIGS[model_config_id]
            self.model_name = self.config["model_id"]
        else:
            # Try to load from config file
            config_path = Path(model_config_id)
            if config_path.exists():
                with open(config_path) as f:
                    model_data = json.load(f)
                    self.model_name = model_data.get("model_id", "mistral-7b-instruct")
                    self.config = self._extract_config(model_data)
            else:
                # Fallback to tier1_fast
                self.config = self.MODEL_CONFIGS["tier1_fast"]
                self.model_name = self.config["model_id"]

        # Initialize tokenizer
        try:
            # Try to get encoding for specific model
            self.encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")  # Fallback
        except Exception:
            # Use cl100k_base as fallback (works for most models)
            self.encoding = tiktoken.get_encoding("cl100k_base")

    def _extract_config(self, model_data: dict) -> dict:
        """Extract config from model JSON file."""
        return {
            "model_id": model_data.get("model_id", "unknown"),
            "context_window": model_data.get("context_window", 4096),
            "safe_limit_percent": 60,
            "warning_limit_percent": 85,
            "output_buffer_percent": 25
        }

    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text.

        Args:
            text: Text to count tokens for

        Returns:
            Number of tokens
        """
        if not text:
            return 0

        return len(self.encoding.encode(text))

    def estimate_context_size(self, prompt_parts: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estimate total context size from prompt parts.

        Args:
            prompt_parts: Dictionary with prompt components:
                {
                    "system_prompt": str,
                    "technique_prompt": str,
                    "previous_outputs": [str] or str,
                    "user_input": str,
                    "examples": str
                }

        Returns:
            {
                "breakdown": {
                    "system_prompt": 482,
                    "technique_prompt": 356,
                    "previous_outputs": 3927,
                    "user_input": 142,
                    "examples": 0
                },
                "total": 4907,
                "percentage": 59.9,
                "context_limit": 8192,
                "safety_status": "safe"
            }
        """
        breakdown = {}
        total = 0

        for key, value in prompt_parts.items():
            if value is None:
                tokens = 0
            elif isinstance(value, list):
                # Sum tokens for list of strings
                tokens = sum(self.count_tokens(str(v)) for v in value if v)
            else:
                tokens = self.count_tokens(str(value))

            breakdown[key] = tokens
            total += tokens

        context_limit = self.get_context_limit()
        percentage = (total / context_limit * 100) if context_limit > 0 else 0

        return {
            "breakdown": breakdown,
            "total": total,
            "percentage": round(percentage, 1),
            "context_limit": context_limit,
            "safety_status": self.get_safety_status(total)["status"]
        }

    def get_context_limit(self) -> int:
        """Get context window limit for current model."""
        return self.config.get("context_window", 4096)

    def get_safe_limit(self) -> int:
        """Get safe limit (60% of context window)."""
        return int(self.get_context_limit() * self.config["safe_limit_percent"] / 100)

    def get_warning_limit(self) -> int:
        """Get warning limit (85% of context window)."""
        return int(self.get_context_limit() * self.config["warning_limit_percent"] / 100)

    def get_output_buffer(self) -> int:
        """Get recommended output buffer size (25% of context window)."""
        return int(self.get_context_limit() * self.config["output_buffer_percent"] / 100)

    def get_safety_status(self, token_count: int) -> Dict[str, str]:
        """
        Get safety status based on token count.

        Args:
            token_count: Current token count

        Returns:
            {
                "status": "safe|warning|danger",
                "color": "green|yellow|red",
                "icon": "✅|⚠️|🚨",
                "message": "descriptive message"
            }
        """
        limit = self.get_context_limit()
        percentage = (token_count / limit * 100) if limit > 0 else 0

        if percentage < self.config["safe_limit_percent"]:
            return {
                "status": "safe",
                "color": "green",
                "icon": "✅",
                "message": "Safe - Genug Platz für Output"
            }
        elif percentage < self.config["warning_limit_percent"]:
            return {
                "status": "warning",
                "color": "yellow",
                "icon": "⚠️",
                "message": "Warning - Context wird knapp"
            }
        else:
            return {
                "status": "danger",
                "color": "red",
                "icon": "🚨",
                "message": "Danger - Halluzinations-Gefahr!"
            }

    def build_context_info(
        self,
        loaded_data: List[Dict[str, Any]],
        total_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Build context info object for working_state.

        Args:
            loaded_data: List of loaded data items with type, name, tokens
            total_tokens: Optional override for total tokens (will be calculated if None)

        Returns:
            Context info dict ready for working_state.context
        """
        if total_tokens is None:
            total_tokens = sum(item.get("tokens", 0) for item in loaded_data)

        context_limit = self.get_context_limit()
        percentage = (total_tokens / context_limit * 100) if context_limit > 0 else 0
        safety = self.get_safety_status(total_tokens)

        return {
            "loaded_data": loaded_data,
            "total_tokens": total_tokens,
            "context_limit": context_limit,
            "percentage": round(percentage, 1),
            "safety_status": safety["status"],
            "output_buffer": self.get_output_buffer()
        }


# Global instance for easy access
_default_counter = None


def get_token_counter(model_config_id: str = "tier1_fast") -> TokenCounter:
    """
    Get or create a token counter instance.

    Args:
        model_config_id: Model config ID or path

    Returns:
        TokenCounter instance
    """
    global _default_counter

    # For default model, reuse global instance
    if model_config_id == "tier1_fast":
        if _default_counter is None:
            _default_counter = TokenCounter(model_config_id)
        return _default_counter

    # For other models, create new instance
    return TokenCounter(model_config_id)


def count_tokens(text: str, model_config_id: str = "tier1_fast") -> int:
    """
    Quick token count function.

    Args:
        text: Text to count
        model_config_id: Model config ID

    Returns:
        Token count
    """
    counter = get_token_counter(model_config_id)
    return counter.count_tokens(text)
