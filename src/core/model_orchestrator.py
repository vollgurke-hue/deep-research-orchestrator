"""
Model Orchestrator

High-level coordinator for model selection and execution.
Manages multiple providers (Ollama, External) and routes requests.
"""

from typing import Optional, List
from .model_provider import (
    ModelProvider,
    ModelCapability,
    QualityLevel,
    ModelResponse
)


class ModelOrchestrator:
    """
    Central coordinator for all model operations.

    Responsibilities:
    - Route requests to appropriate provider (Ollama vs External)
    - Enforce resource limits (profile-based)
    - Track usage statistics
    - Handle fallbacks (if local model fails, suggest external)

    Usage:
        orchestrator = ModelOrchestrator(profile="standard")
        orchestrator.register_provider("ollama", LocalOllamaProvider())

        response = orchestrator.generate(
            prompt="What is the capital of France?",
            capability=ModelCapability.EXTRACTION,
            quality=QualityLevel.FAST
        )
    """

    def __init__(self, profile: str = "standard"):
        """
        Initialize orchestrator with resource profile.

        Args:
            profile: Resource profile name (from config/profiles/)
        """
        self.profile_name = profile
        self.profile_config = None
        self.providers: dict[str, ModelProvider] = {}
        self._load_profile()

    def _load_profile(self):
        """Load profile configuration"""
        # TODO Sprint 1 Day 3: Load from config/profiles/{profile}.json
        # Validate against profile_schema.json
        pass

    def register_provider(self, name: str, provider: ModelProvider):
        """
        Register a model provider.

        Args:
            name: Provider identifier (e.g., "ollama", "external")
            provider: ModelProvider instance
        """
        self.providers[name] = provider

    def generate(
        self,
        prompt: str,
        capability: ModelCapability,
        quality: QualityLevel,
        prefer_provider: Optional[str] = None,
        **kwargs
    ) -> ModelResponse:
        """
        Generate response, automatically selecting best provider.

        Selection logic:
        1. If prefer_provider specified, try that first
        2. Otherwise, check which providers support capability+quality
        3. Prefer local (Ollama) over external for speed
        4. If local unavailable/busy, use external

        Args:
            prompt: User prompt
            capability: Task type (extraction, reasoning, etc.)
            quality: Quality level (fast, balanced, quality)
            prefer_provider: Optional provider name to try first
            **kwargs: Additional args passed to provider

        Returns:
            ModelResponse from selected provider
        """
        # TODO Sprint 1 Day 3: Implement provider selection logic
        # TODO Sprint 1 Day 3: Add error handling + fallbacks
        # TODO Sprint 1 Day 3: Track statistics (calls per capability, etc.)

        # Placeholder: use Ollama if available
        if "ollama" in self.providers:
            return self.providers["ollama"].generate(
                prompt, capability, quality, **kwargs
            )

        raise RuntimeError("No providers available")

    def get_capabilities(self) -> dict[str, dict]:
        """
        Get all available capabilities across providers.

        Returns:
            {
                "ollama": {
                    ModelCapability.EXTRACTION: [QualityLevel.FAST],
                    ModelCapability.REASONING: [QualityLevel.BALANCED]
                },
                "external": { ... }
            }
        """
        return {
            name: provider.get_available_capabilities()
            for name, provider in self.providers.items()
        }

    def get_resource_status(self) -> dict:
        """
        Get resource usage across all providers.

        Returns:
            {
                "profile": "standard",
                "max_vram_mb": 11000,
                "current_vram_mb": 9000,
                "providers": {
                    "ollama": {"vram_mb": 9000, "ram_mb": 3000}
                }
            }
        """
        # TODO Sprint 1 Day 3: Aggregate from all providers
        return {
            "profile": self.profile_name,
            "providers": {}
        }


# TODO Sprint 1 Day 4: Add request queuing
# TODO Sprint 1 Day 4: Add circuit breaker for failing providers
