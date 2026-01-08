"""
llama.cpp Client for local LLM inference.

Provides interface to llama.cpp server for running abliterated models locally.
Uses HTTP API for reliable, non-interactive inference.
"""
import subprocess
import json
import time
import requests
import atexit
import signal
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class LlamaConfig:
    """Configuration for llama.cpp model."""

    model_path: Path
    n_gpu_layers: int = 999
    ctx_size: int = 4096
    temperature: float = 0.7
    max_tokens: int = 2048
    threads: int = 4


class LlamaCppClient:
    """Client for llama.cpp inference using HTTP API."""

    def __init__(
        self,
        model_path: str | Path,
        llama_server_path: str | Path = None,
        llama_cli_path: str | Path = None,
        n_gpu_layers: int = 999,
        ctx_size: int = 4096,
        threads: int = 4,
        port: int = 8080,
        auto_start_server: bool = True
    ):
        """
        Initialize llama.cpp client.

        Args:
            model_path: Path to GGUF model file
            llama_server_path: Path to llama-server binary (defaults to project's build)
            llama_cli_path: Path to llama-cli binary (for compatibility)
            n_gpu_layers: Number of layers to offload to GPU (999 = all)
            ctx_size: Context size
            threads: Number of CPU threads
            port: HTTP port for llama-server
            auto_start_server: Automatically start server if not running
        """
        self.model_path = Path(model_path)

        # Default to project's llama.cpp build
        if llama_server_path is None:
            project_root = Path(__file__).parents[2]
            llama_server_path = project_root / "llama.cpp" / "build" / "bin" / "llama-server"

        if llama_cli_path is None:
            project_root = Path(__file__).parents[2]
            llama_cli_path = project_root / "llama.cpp" / "build" / "bin" / "llama-cli"

        self.llama_server = Path(llama_server_path)
        self.llama_cli = Path(llama_cli_path)  # Keep for backward compatibility
        self.n_gpu_layers = n_gpu_layers
        self.ctx_size = ctx_size
        self.threads = threads
        self.port = port
        self.base_url = f"http://127.0.0.1:{port}"
        self.server_process = None

        # Validate paths
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model not found: {self.model_path}")
        if not self.llama_server.exists():
            raise FileNotFoundError(f"llama-server not found: {self.llama_server}")

        # Auto-start server if requested
        if auto_start_server:
            self._ensure_server_running()

        # Register cleanup
        atexit.register(self.shutdown)

    def _ensure_server_running(self):
        """Start llama-server if not already running."""
        # Check if server is already running
        if self._is_server_healthy():
            print(f"✓ llama-server already running on port {self.port}")
            return

        print(f"Starting llama-server on port {self.port}...")

        # Start server
        cmd = [
            str(self.llama_server),
            "--model", str(self.model_path),
            "--n-gpu-layers", str(self.n_gpu_layers),
            "--ctx-size", str(self.ctx_size),
            "--threads", str(self.threads),
            "--port", str(self.port),
            "--host", "127.0.0.1"
        ]

        self.server_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Wait for server to be ready
        # Increased timeout for weaker hardware (GTX 980 needs more time to load model)
        max_wait = 180  # seconds (3 minutes)

        print("⏳ Waiting for llama-server to load model (this can take 10-20s on GTX 980)...")

        for i in range(max_wait):
            # Only check for crashes after 5 seconds (model needs time to load)
            if i >= 5 and self.server_process.poll() is not None:
                # Process exited - get error output
                stdout, stderr = self.server_process.communicate()
                print(f"❌ llama-server died during startup!")
                print(f"Exit code: {self.server_process.returncode}")
                print(f"STDOUT: {stdout[:1000]}")
                print(f"STDERR: {stderr[:1000]}")
                raise RuntimeError(f"llama-server crashed on startup (exit code: {self.server_process.returncode}). Check logs above.")

            if self._is_server_healthy():
                print(f"✓ llama-server ready after {i+1}s")
                return

            if i % 5 == 0 and i > 0:
                print(f"  Still loading... ({i}s elapsed)")

            time.sleep(1)

        raise RuntimeError("Failed to start llama-server (timeout after 180s)")

    def _is_server_healthy(self) -> bool:
        """Check if server is responding."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=2)
            return response.status_code == 200
        except:
            return False

    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        system_prompt: Optional[str] = None,
        stop_sequences: Optional[list[str]] = None
    ) -> str:
        """
        Generate text using llama.cpp server API.

        Args:
            prompt: Input prompt
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens to generate
            system_prompt: Optional system prompt
            stop_sequences: Optional list of stop sequences

        Returns:
            Generated text
        """
        # Ensure server is running
        if not self._is_server_healthy():
            raise RuntimeError("llama-server is not running. Call _ensure_server_running() first.")

        # Build request payload
        payload = {
            "prompt": prompt,
            "temperature": temperature,
            "n_predict": max_tokens,
            "stop": stop_sequences or [],
            "stream": False
        }

        # Add system prompt if provided (in messages format)
        if system_prompt:
            # Convert to chat completion format
            endpoint = "/v1/chat/completions"
            payload = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False
            }
            if stop_sequences:
                payload["stop"] = stop_sequences
        else:
            endpoint = "/completion"

        # Send request
        try:
            response = requests.post(
                f"{self.base_url}{endpoint}",
                json=payload,
                timeout=300  # 5 minute timeout
            )
            response.raise_for_status()

            # Parse response
            data = response.json()

            if endpoint == "/v1/chat/completions":
                # Chat completion format
                return data["choices"][0]["message"]["content"].strip()
            else:
                # Regular completion format
                return data["content"].strip()

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"llama.cpp generation failed: {e}")

    def _format_prompt(self, prompt: str) -> str:
        """Format prompt for llama.cpp (basic)."""
        return f"<s>[INST] {prompt} [/INST]"

    def _format_prompt_with_system(self, prompt: str, system_prompt: str) -> str:
        """Format prompt with system message."""
        return f"<s>[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n\n{prompt} [/INST]"

    def health_check(self) -> Dict[str, Any]:
        """
        Check if llama.cpp server and model are accessible.

        Returns:
            Dict with status information
        """
        status = {
            "llama_server_exists": self.llama_server.exists(),
            "model_exists": self.model_path.exists(),
            "model_path": str(self.model_path),
            "n_gpu_layers": self.n_gpu_layers,
            "port": self.port,
            "server_healthy": self._is_server_healthy()
        }

        # Try to get server info
        if status["server_healthy"]:
            try:
                response = requests.get(f"{self.base_url}/props", timeout=5)
                if response.status_code == 200:
                    props = response.json()
                    status["model_loaded"] = True
                    status["ctx_size_actual"] = props.get("default_generation_settings", {}).get("n_ctx")
            except Exception as e:
                status["props_error"] = str(e)

        return status

    def shutdown(self):
        """Shutdown llama-server if we started it."""
        if self.server_process:
            print("Shutting down llama-server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
            print("✓ llama-server stopped")

    @classmethod
    def from_config(cls, config: LlamaConfig, llama_server_path: str | Path = "./llama.cpp/build/bin/llama-server"):
        """Create client from config object."""
        return cls(
            model_path=config.model_path,
            llama_server_path=llama_server_path,
            n_gpu_layers=config.n_gpu_layers,
            ctx_size=config.ctx_size,
            threads=config.threads
        )
