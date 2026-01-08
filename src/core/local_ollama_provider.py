"""
Local Ollama Provider Implementation

Implements ModelProvider interface for Ollama-based local models.
Handles model selection, loading, and resource management.
"""

import time
import json
import ollama
import psutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from .model_provider import (
    ModelProvider,
    ModelCapability,
    QualityLevel,
    ModelResponse
)


class LocalOllamaProvider(ModelProvider):
    """
    Ollama backend for local LLM inference.

    Automatically selects best available model based on:
    - Requested capability (extraction/reasoning/synthesis)
    - Requested quality level (fast/balanced/quality)
    - Available VRAM
    - Model configurations from config/models/
    """

    def __init__(self, config_dir: str = "config/models"):
        """
        Initialize Ollama provider.

        Args:
            config_dir: Directory containing model JSON configs
        """
        self.config_dir = config_dir
        self.models = {}  # model_id -> config mapping
        self._load_model_configs()

    def _load_model_configs(self):
        """
        Load all model configs from JSON files.

        Filters for:
        - provider == "ollama"
        - enabled == true

        Stores in self.models as: {model_id: config_dict}
        """
        config_path = Path(self.config_dir)

        if not config_path.exists():
            print(f"Warning: Config directory {self.config_dir} does not exist")
            return

        for json_file in config_path.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                # Filter: only Ollama models that are enabled
                if config.get("provider") == "ollama" and config.get("enabled", False):
                    model_id = config.get("model_id")
                    if model_id:
                        self.models[model_id] = config
                        print(f"Loaded model config: {model_id}")

            except json.JSONDecodeError as e:
                print(f"Error parsing {json_file}: {e}")
            except Exception as e:
                print(f"Error loading {json_file}: {e}")

    def get_available_capabilities(self) -> Dict[ModelCapability, List[QualityLevel]]:
        """
        Return capabilities based on loaded models.

        Example output:
        {
            ModelCapability.EXTRACTION: [QualityLevel.FAST],
            ModelCapability.REASONING: [QualityLevel.BALANCED]
        }
        """
        capabilities = {}

        for model_id, config in self.models.items():
            # Get capabilities from config (list of strings)
            model_capabilities = config.get("capabilities", [])
            quality_level_str = config.get("quality_level", "balanced")

            # Convert string to enum
            try:
                quality_level = QualityLevel(quality_level_str)
            except ValueError:
                print(f"Warning: Invalid quality level '{quality_level_str}' in {model_id}")
                continue

            # Map each capability to quality level
            for cap_str in model_capabilities:
                try:
                    capability = ModelCapability(cap_str)

                    if capability not in capabilities:
                        capabilities[capability] = []

                    if quality_level not in capabilities[capability]:
                        capabilities[capability].append(quality_level)

                except ValueError:
                    print(f"Warning: Invalid capability '{cap_str}' in {model_id}")

        return capabilities

    def generate(
        self,
        prompt: str,
        capability: ModelCapability,
        quality: QualityLevel,
        **kwargs
    ) -> ModelResponse:
        """
        Generate response using best matching Ollama model.

        Algorithm:
        1. Find models with requested capability + quality
        2. Sort by VRAM requirement (prefer smaller for efficiency)
        3. Call ollama.generate() with selected model
        4. Return standardized ModelResponse

        Raises:
            RuntimeError: If no suitable model found
        """
        start_time = time.time()

        # Step 1: Filter models by capability and quality
        matching_models = []
        for model_id, config in self.models.items():
            model_capabilities = config.get("capabilities", [])
            model_quality = config.get("quality_level", "balanced")

            # Check if model supports requested capability and quality
            if capability.value in model_capabilities and model_quality == quality.value:
                matching_models.append((model_id, config))

        if not matching_models:
            raise RuntimeError(
                f"No model found for capability={capability.value}, "
                f"quality={quality.value}. Available: {list(self.models.keys())}"
            )

        # Step 2: Sort by VRAM requirement (prefer smaller = more efficient)
        matching_models.sort(key=lambda x: x[1].get("vram_mb", 999999))

        # Step 3: Select best model and get its Ollama path
        selected_model_id, selected_config = matching_models[0]
        ollama_model_path = selected_config.get("model_path")

        if not ollama_model_path:
            raise RuntimeError(f"Model {selected_model_id} has no model_path configured")

        # Step 4: Prepare parameters (merge config defaults with kwargs)
        parameters = selected_config.get("parameters", {}).copy()
        parameters.update(kwargs)  # kwargs override defaults

        # Step 5: Call Ollama
        try:
            response = ollama.generate(
                model=ollama_model_path,
                prompt=prompt,
                options=parameters
            )
        except Exception as e:
            raise RuntimeError(f"Ollama generate failed for {ollama_model_path}: {e}")

        latency_ms = (time.time() - start_time) * 1000

        # Step 6: Return standardized response
        return ModelResponse(
            content=response.get("response", ""),
            model_used=selected_model_id,
            tokens_used=response.get("eval_count", 0),
            latency_ms=latency_ms,
            metadata={
                "ollama_model_path": ollama_model_path,
                "vram_mb": selected_config.get("vram_mb"),
                "quality_level": quality.value,
                "capability": capability.value,
                "raw_response": response
            }
        )

    def is_available(self) -> bool:
        """Check if Ollama is running and models are available"""
        # TODO Sprint 1 Day 2: Implement health check
        try:
            ollama.list()
            return True
        except Exception:
            return False

    def get_resource_usage(self) -> Dict[str, float]:
        """
        Get current GPU/RAM usage.

        Returns:
            {
                "vram_mb": 9000.0,
                "ram_mb": 3000.0,
                "gpu_utilization": 0.85,
                "system_ram_percent": 45.2
            }
        """
        usage = {}

        # System RAM usage
        memory = psutil.virtual_memory()
        usage["system_ram_percent"] = memory.percent
        usage["system_ram_available_gb"] = memory.available / (1024**3)

        # Try to get GPU info via nvidia-smi
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.used,memory.total,utilization.gpu",
                 "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode == 0:
                # Parse output: "9000, 11264, 85" (might have multiple GPUs, take first line)
                lines = result.stdout.strip().split('\n')
                first_line = lines[0] if lines else ""
                values = first_line.split(',')

                if len(values) >= 3:
                    usage["vram_mb"] = float(values[0].strip())
                    usage["vram_total_mb"] = float(values[1].strip())
                    usage["gpu_utilization"] = float(values[2].strip()) / 100.0
                else:
                    usage["vram_mb"] = 0.0
                    usage["gpu_utilization"] = 0.0
            else:
                usage["vram_mb"] = 0.0
                usage["gpu_utilization"] = 0.0

        except (subprocess.TimeoutExpired, FileNotFoundError):
            # nvidia-smi not available or timed out
            usage["vram_mb"] = 0.0
            usage["gpu_utilization"] = 0.0
            usage["gpu_available"] = False

        return usage


# TODO Sprint 1 Day 3: Add model swapping (unload/load based on VRAM)
# TODO Sprint 1 Day 3: Add request queuing if model busy
