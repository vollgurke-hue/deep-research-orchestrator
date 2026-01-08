"""
Model Provider Abstraction Layer

Hardware-agnostic interface for LLM backends.
Allows swapping between Ollama, llama.cpp, HuggingFace, or cloud providers.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass


class ModelCapability(Enum):
    """Model capabilities for different tasks"""
    EXTRACTION = "extraction"  # Fast entity/fact extraction
    REASONING = "reasoning"    # Deep analysis, CoT
    SYNTHESIS = "synthesis"    # Combining information
    VALIDATION = "validation"  # Checking contradictions


class QualityLevel(Enum):
    """Quality/Speed tradeoff"""
    FAST = "fast"           # Tier 1: 8B models, quick responses
    BALANCED = "balanced"   # Tier 2: 14B models, good quality
    QUALITY = "quality"     # Tier 3: External/32B models, best results


@dataclass
class ModelResponse:
    """Standardized response from any provider"""
    content: str
    model_used: str
    tokens_used: int
    latency_ms: float
    metadata: Optional[Dict] = None


class ModelProvider(ABC):
    """
    Abstract interface for model backends.

    Implementations:
    - LocalOllamaProvider: Uses Ollama for local models
    - LlamaCppProvider: Direct llama.cpp integration
    - ExternalProvider: Manual Multi-AI workflow (MD files)
    """

    @abstractmethod
    def get_available_capabilities(self) -> Dict[ModelCapability, List[QualityLevel]]:
        """
        Return what this provider can do.

        Example:
        {
            ModelCapability.EXTRACTION: [QualityLevel.FAST],
            ModelCapability.REASONING: [QualityLevel.BALANCED]
        }
        """
        pass

    @abstractmethod
    def generate(
        self,
        prompt: str,
        capability: ModelCapability,
        quality: QualityLevel,
        **kwargs
    ) -> ModelResponse:
        """
        Generate response - provider selects best model.

        Args:
            prompt: The user prompt
            capability: What task type (extraction, reasoning, etc.)
            quality: Fast/Balanced/Quality
            **kwargs: Provider-specific options (temperature, max_tokens, etc.)

        Returns:
            ModelResponse with content and metadata
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is ready (models loaded, API key set, etc.)"""
        pass

    @abstractmethod
    def get_resource_usage(self) -> Dict[str, float]:
        """
        Return current resource usage.

        Returns:
            {
                "vram_mb": 9000,
                "ram_mb": 3000,
                "gpu_utilization": 0.85
            }
        """
        pass


# TODO Sprint 1 Day 2: Implement LocalOllamaProvider
# TODO Sprint 1 Day 3: Implement ModelOrchestrator (capability routing)
