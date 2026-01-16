"""
Local llama.cpp Provider with Multi-GPU Support

Implements ModelProvider interface for llama.cpp with automatic
tensor splitting across multiple GPUs.
"""

import json
import subprocess
import time
import requests
import atexit
from pathlib import Path
from typing import Optional, Dict, Any, List
from .model_provider import ModelProvider, ModelResponse, ModelCapability, QualityLevel


class LocalLlamaCppProvider(ModelProvider):
    """
    llama.cpp provider with multi-GPU tensor splitting.

    Features:
    - Automatic tensor split across multiple GPUs
    - Hardware-aware model selection
    - Profile-based capability/quality routing

    Multi-GPU Example:
        GPU 0: RTX 3060 Ti (8GB) → 8/11 = 72.7% of layers
        GPU 1: GTX 1060 3GB (3GB) → 3/11 = 27.3% of layers

        For 9GB model, splits intelligently across both GPUs
    """

    def __init__(
        self,
        models_config_dir: str | Path,
        llama_server_path: Optional[str | Path] = None,
        port: int = 8081,  # Different from Ollama (8080)
        auto_start: bool = True
    ):
        """
        Initialize llama.cpp provider.

        Args:
            models_config_dir: Directory with model config JSON files
            llama_server_path: Path to llama-server binary
            port: HTTP port for llama-server
            auto_start: Auto-start server on first generate()
        """
        self.models_config_dir = Path(models_config_dir)
        self.port = port
        self.base_url = f"http://127.0.0.1:{port}"
        self.server_process = None
        self.current_model = None
        self.auto_start = auto_start

        # Default to project's llama.cpp build
        if llama_server_path is None:
            project_root = Path(__file__).parents[2]
            llama_server_path = project_root / "llama.cpp" / "build" / "bin" / "llama-server"

        self.llama_server = Path(llama_server_path)

        # Load model configs
        self.models = self._load_model_configs()

        # Detect GPUs for tensor splitting
        self.gpus = self._detect_gpus()

        print(f"LocalLlamaCppProvider initialized:")
        print(f"  Models: {len(self.models)}")
        print(f"  GPUs: {len(self.gpus)}")
        for i, gpu in enumerate(self.gpus):
            print(f"    GPU {i}: {gpu['name']} ({gpu['vram_mb']}MB)")

        # Register cleanup
        atexit.register(self.shutdown)

    def _load_model_configs(self) -> Dict[str, Dict[str, Any]]:
        """Load model configs from JSON files"""
        models = {}

        if not self.models_config_dir.exists():
            print(f"Warning: Models config dir not found: {self.models_config_dir}")
            return models

        for config_file in self.models_config_dir.glob("*.json"):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    model_id = config_file.stem

                    # Only load if llama.cpp compatible
                    if config.get("backend") == "llamacpp" or config.get("gguf_path"):
                        models[model_id] = config
                        print(f"Loaded model config: {model_id}")
            except Exception as e:
                print(f"Warning: Failed to load {config_file}: {e}")

        return models

    def _detect_gpus(self) -> List[Dict[str, Any]]:
        """Detect available GPUs and their VRAM"""
        gpus = []

        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=index,name,memory.total", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        parts = line.split(',')
                        gpus.append({
                            "index": int(parts[0].strip()),
                            "name": parts[1].strip(),
                            "vram_mb": int(parts[2].strip())
                        })
        except Exception as e:
            print(f"Warning: Could not detect GPUs: {e}")

        return gpus

    def _calculate_tensor_split(self, model_vram_mb: int) -> Optional[str]:
        """
        Calculate optimal tensor split for multi-GPU.

        Returns tensor split string like "8192,3072" for --tensor-split
        """
        if len(self.gpus) <= 1:
            return None

        # Calculate proportional split based on VRAM
        total_vram = sum(gpu['vram_mb'] for gpu in self.gpus)

        if model_vram_mb > total_vram:
            print(f"Warning: Model needs {model_vram_mb}MB but only {total_vram}MB available")

        # Create split proportional to VRAM
        splits = [str(gpu['vram_mb']) for gpu in self.gpus]
        tensor_split = ",".join(splits)

        print(f"Multi-GPU tensor split: {tensor_split}")
        return tensor_split

    def _start_server(self, model_id: str):
        """Start llama-server with specified model"""
        config = self.models[model_id]

        # Get model path
        gguf_path = config.get("gguf_path")
        if not gguf_path:
            raise ValueError(f"No gguf_path in config for {model_id}")

        model_path = Path(gguf_path)
        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")

        if not self.llama_server.exists():
            raise FileNotFoundError(f"llama-server not found: {self.llama_server}")

        # Stop existing server if different model
        if self.current_model != model_id and self.server_process:
            print(f"Switching from {self.current_model} to {model_id}...")
            self.shutdown()

        # Check if already running with this model
        if self._is_server_healthy() and self.current_model == model_id:
            print(f"✓ llama-server already running with {model_id}")
            return

        print(f"Starting llama-server with {model_id}...")

        # Build command
        cmd = [
            str(self.llama_server),
            "--model", str(model_path),
            "--ctx-size", str(config.get("ctx_size", 8192)),
            "--port", str(self.port),
            "--host", "127.0.0.1"
        ]

        # Add GPU layers (999 = all layers)
        n_gpu_layers = config.get("n_gpu_layers", 999)
        cmd.extend(["--n-gpu-layers", str(n_gpu_layers)])

        # Multi-GPU: llama.cpp auto-detects and splits automatically
        # Don't use --tensor-split for now (can cause crashes with mixed GPUs)
        if len(self.gpus) > 1:
            print(f"  Multi-GPU detected: {len(self.gpus)} GPUs will be used automatically")

        # Start server
        print(f"  Command: {' '.join(cmd)}")
        self.server_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Wait for server to be ready
        print("⏳ Waiting for llama-server to load model (10-30s for multi-GPU)...")

        max_wait = 180
        for i in range(max_wait):
            # Check for crashes after 5s
            if i >= 5 and self.server_process.poll() is not None:
                stdout, stderr = self.server_process.communicate()
                print(f"❌ llama-server crashed!")
                print(f"Exit code: {self.server_process.returncode}")
                print(f"STDERR: {stderr[:2000]}")
                raise RuntimeError(f"llama-server crashed (exit {self.server_process.returncode})")

            if self._is_server_healthy():
                print(f"✓ llama-server ready after {i+1}s")
                self.current_model = model_id
                return

            if i % 10 == 0 and i > 0:
                print(f"  Still loading... ({i}s elapsed)")

            time.sleep(1)

        raise RuntimeError("Failed to start llama-server (timeout after 180s)")

    def _is_server_healthy(self) -> bool:
        """Check if server is responding"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=2)
            return response.status_code == 200
        except:
            return False

    def generate(
        self,
        prompt: str,
        capability: ModelCapability,
        quality: QualityLevel,
        **kwargs
    ) -> ModelResponse:
        """
        Generate response using llama.cpp.

        Args:
            prompt: Input prompt
            capability: Required model capability
            quality: Quality level
            **kwargs: Additional args (temperature, max_tokens, etc)

        Returns:
            ModelResponse with generated content
        """
        # Select best model for capability + quality
        matching_models = []

        for model_id, config in self.models.items():
            model_capabilities = config.get("capabilities", [])
            model_quality = config.get("quality_level", "balanced")

            if capability.value in model_capabilities and model_quality == quality.value:
                matching_models.append((model_id, config))

        if not matching_models:
            raise ValueError(
                f"No llama.cpp model supports capability={capability.value}, quality={quality.value}"
            )

        # Sort by VRAM (prefer smaller)
        matching_models.sort(key=lambda x: x[1].get("vram_mb", 999999))

        selected_model_id, selected_config = matching_models[0]

        print(f"Selected model: {selected_model_id} ({selected_config.get('vram_mb')}MB VRAM)")

        # Start server with this model if needed
        if self.auto_start:
            self._start_server(selected_model_id)

        if not self._is_server_healthy():
            raise RuntimeError("llama-server not running. Set auto_start=True or call _start_server() manually")

        # Build request
        temperature = kwargs.get("temperature", 0.7)
        max_tokens = kwargs.get("max_tokens", 2048)

        payload = {
            "prompt": prompt,
            "temperature": temperature,
            "n_predict": max_tokens,
            "stream": False
        }

        # Send request
        try:
            response = requests.post(
                f"{self.base_url}/completion",
                json=payload,
                timeout=kwargs.get("timeout", 300)
            )
            response.raise_for_status()

            data = response.json()
            content = data.get("content", "").strip()

            return ModelResponse(
                content=content,
                model_used=selected_model_id,
                tokens_used=data.get("tokens_predicted", 0),
                latency_ms=0.0,  # TODO: track actual latency
                metadata={
                    "provider": "llamacpp",
                    "stop_reason": data.get("stop", "length")
                }
            )

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"llama.cpp generation failed: {e}")

    def shutdown(self):
        """Shutdown llama-server"""
        if self.server_process:
            print("Shutting down llama-server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
            print("✓ llama-server stopped")
            self.server_process = None
            self.current_model = None

    def get_available_capabilities(self) -> Dict[ModelCapability, List[QualityLevel]]:
        """Return available capabilities from loaded models"""
        capabilities = {}

        for model_id, config in self.models.items():
            model_capabilities = config.get("capabilities", [])
            quality = config.get("quality_level", "balanced")

            for cap_str in model_capabilities:
                try:
                    cap = ModelCapability(cap_str)
                    quality_level = QualityLevel(quality)

                    if cap not in capabilities:
                        capabilities[cap] = []

                    if quality_level not in capabilities[cap]:
                        capabilities[cap].append(quality_level)

                except ValueError:
                    pass

        return capabilities

    def is_available(self) -> bool:
        """Check if llama-server is running"""
        return self._is_server_healthy()

    def get_resource_usage(self) -> Dict[str, float]:
        """Get current GPU/RAM usage"""
        usage = {
            "vram_mb": 0.0,
            "ram_mb": 0.0,
            "gpu_utilization": 0.0
        }

        try:
            # Get GPU usage from nvidia-smi
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.used,utilization.gpu",
                 "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                total_vram = 0
                total_util = 0
                gpu_count = 0

                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        parts = line.split(',')
                        total_vram += float(parts[0].strip())
                        total_util += float(parts[1].strip())
                        gpu_count += 1

                usage["vram_mb"] = total_vram
                usage["gpu_utilization"] = total_util / max(gpu_count, 1) / 100.0

        except Exception:
            pass

        return usage
