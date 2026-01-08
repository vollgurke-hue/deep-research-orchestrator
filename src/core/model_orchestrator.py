"""
Model Orchestrator

High-level coordinator for model selection and execution.
Manages multiple providers (Ollama, External) and routes requests.
"""

from typing import Optional, List, Dict
from .model_provider import (
    ModelProvider,
    ModelCapability,
    QualityLevel,
    ModelResponse
)
from .profile_manager import ProfileManager


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

    def __init__(self, profile: str = "standard", profiles_dir: str = "config/profiles"):
        """
        Initialize orchestrator with resource profile.

        Args:
            profile: Resource profile name (from config/profiles/)
            profiles_dir: Directory containing profile configs
        """
        self.profile_name = profile
        self.profile_manager = ProfileManager(profiles_dir=profiles_dir)
        self.profile_config = None
        self.providers: dict[str, ModelProvider] = {}
        self.stats = {
            "total_requests": 0,
            "requests_by_capability": {},
            "requests_by_provider": {}
        }
        self._load_profile()

    def _load_profile(self):
        """
        Load profile configuration and validate hardware.

        Raises:
            RuntimeError: If profile not found or hardware insufficient
        """
        self.profile_config = self.profile_manager.get_profile(self.profile_name)

        if not self.profile_config:
            raise RuntimeError(f"Profile '{self.profile_name}' not found")

        # Validate hardware
        valid, msg = self.profile_manager.validate_hardware(self.profile_name)
        if not valid:
            print(f"Warning: {msg}")
            print(f"Continuing anyway, but performance may be degraded")

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
        5. Track statistics

        Args:
            prompt: User prompt
            capability: Task type (extraction, reasoning, etc.)
            quality: Quality level (fast, balanced, quality)
            prefer_provider: Optional provider name to try first
            **kwargs: Additional args passed to provider

        Returns:
            ModelResponse from selected provider

        Raises:
            RuntimeError: If no suitable provider found
        """
        self.stats["total_requests"] += 1

        # Track by capability
        cap_key = capability.value
        self.stats["requests_by_capability"][cap_key] = \
            self.stats["requests_by_capability"].get(cap_key, 0) + 1

        # Step 1: Try preferred provider first
        if prefer_provider and prefer_provider in self.providers:
            try:
                response = self.providers[prefer_provider].generate(
                    prompt, capability, quality, **kwargs
                )
                self._track_success(prefer_provider)
                return response
            except Exception as e:
                print(f"Warning: Preferred provider '{prefer_provider}' failed: {e}")
                # Continue to fallback logic

        # Step 2: Find providers that support this capability+quality
        suitable_providers = self._find_suitable_providers(capability, quality)

        if not suitable_providers:
            raise RuntimeError(
                f"No provider supports capability={capability.value}, "
                f"quality={quality.value}. "
                f"Available providers: {list(self.providers.keys())}"
            )

        # Step 3: Try providers in order (local first)
        provider_order = self._order_providers(suitable_providers)

        for provider_name in provider_order:
            provider = self.providers[provider_name]

            try:
                response = provider.generate(prompt, capability, quality, **kwargs)
                self._track_success(provider_name)
                return response

            except Exception as e:
                print(f"Warning: Provider '{provider_name}' failed: {e}")
                continue  # Try next provider

        # If we get here, all providers failed
        raise RuntimeError(
            f"All providers failed for capability={capability.value}, "
            f"quality={quality.value}"
        )

    def _find_suitable_providers(
        self,
        capability: ModelCapability,
        quality: QualityLevel
    ) -> List[str]:
        """
        Find providers that support given capability and quality.

        Returns:
            List of provider names
        """
        suitable = []

        for name, provider in self.providers.items():
            caps = provider.get_available_capabilities()

            if capability in caps and quality in caps[capability]:
                suitable.append(name)

        return suitable

    def _order_providers(self, provider_names: List[str]) -> List[str]:
        """
        Order providers by preference (local first, then external).

        Args:
            provider_names: List of provider names to order

        Returns:
            Ordered list of provider names
        """
        # Preferred order: ollama, then others
        ordered = []

        if "ollama" in provider_names:
            ordered.append("ollama")

        for name in provider_names:
            if name not in ordered:
                ordered.append(name)

        return ordered

    def _track_success(self, provider_name: str):
        """Track successful request by provider"""
        self.stats["requests_by_provider"][provider_name] = \
            self.stats["requests_by_provider"].get(provider_name, 0) + 1

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

    def get_resource_status(self) -> Dict:
        """
        Get resource usage across all providers.

        Returns:
            {
                "profile": "standard",
                "max_graph_nodes": 10000,
                "max_context_tokens": 8192,
                "providers": {
                    "ollama": {"vram_mb": 9000, "ram_mb": 3000}
                },
                "stats": {
                    "total_requests": 42,
                    "requests_by_capability": {...},
                    "requests_by_provider": {...}
                }
            }
        """
        # Aggregate resource usage from all providers
        provider_resources = {}
        for name, provider in self.providers.items():
            try:
                provider_resources[name] = provider.get_resource_usage()
            except Exception as e:
                provider_resources[name] = {"error": str(e)}

        return {
            "profile": self.profile_name,
            "max_graph_nodes": self.profile_config.get("max_graph_nodes", 0) if self.profile_config else 0,
            "max_context_tokens": self.profile_config.get("max_context_tokens", 0) if self.profile_config else 0,
            "providers": provider_resources,
            "stats": self.stats
        }


# TODO Sprint 1 Day 4: Add request queuing
# TODO Sprint 1 Day 4: Add circuit breaker for failing providers
