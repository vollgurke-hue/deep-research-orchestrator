"""
llama.cpp Client for local LLM inference.

Provides interface to llama.cpp for running abliterated models locally.
"""
import subprocess
import json
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
    """Client for llama.cpp inference."""

    def __init__(
        self,
        model_path: str | Path,
        llama_cli_path: str | Path = "./llama.cpp/llama-cli",
        n_gpu_layers: int = 999,
        ctx_size: int = 4096,
        threads: int = 4
    ):
        """
        Initialize llama.cpp client.

        Args:
            model_path: Path to GGUF model file
            llama_cli_path: Path to llama-cli binary
            n_gpu_layers: Number of layers to offload to GPU (999 = all)
            ctx_size: Context size
            threads: Number of CPU threads
        """
        self.model_path = Path(model_path)
        self.llama_cli = Path(llama_cli_path)
        self.n_gpu_layers = n_gpu_layers
        self.ctx_size = ctx_size
        self.threads = threads

        # Validate paths
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model not found: {self.model_path}")
        if not self.llama_cli.exists():
            raise FileNotFoundError(f"llama-cli not found: {self.llama_cli}")

    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        system_prompt: Optional[str] = None,
        stop_sequences: Optional[list[str]] = None
    ) -> str:
        """
        Generate text using llama.cpp.

        Args:
            prompt: Input prompt
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens to generate
            system_prompt: Optional system prompt
            stop_sequences: Optional list of stop sequences

        Returns:
            Generated text
        """
        # Build full prompt with system prompt if provided
        if system_prompt:
            full_prompt = self._format_prompt_with_system(prompt, system_prompt)
        else:
            full_prompt = self._format_prompt(prompt)

        # Build command
        cmd = [
            str(self.llama_cli),
            "--model", str(self.model_path),
            "--n-gpu-layers", str(self.n_gpu_layers),
            "--ctx-size", str(self.ctx_size),
            "--threads", str(self.threads),
            "--prompt", full_prompt,
            "--temp", str(temperature),
            "--n-predict", str(max_tokens),
            "--color"  # Colored output for better readability
        ]

        # Add stop sequences if provided
        if stop_sequences:
            for seq in stop_sequences:
                cmd.extend(["--stop", seq])

        # Execute
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=300  # 5 minute timeout
            )

            # Extract generated text (llama-cli includes prompt in output)
            output = result.stdout.strip()

            # Remove prompt from output if present
            if full_prompt in output:
                output = output.replace(full_prompt, "").strip()

            return output

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"llama.cpp generation failed: {e.stderr}")
        except subprocess.TimeoutExpired:
            raise RuntimeError("Generation timeout (5 minutes)")

    def _format_prompt(self, prompt: str) -> str:
        """Format prompt for llama.cpp (basic)."""
        return f"<s>[INST] {prompt} [/INST]"

    def _format_prompt_with_system(self, prompt: str, system_prompt: str) -> str:
        """Format prompt with system message."""
        return f"<s>[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n\n{prompt} [/INST]"

    def health_check(self) -> Dict[str, Any]:
        """
        Check if llama.cpp and model are accessible.

        Returns:
            Dict with status information
        """
        status = {
            "llama_cli_exists": self.llama_cli.exists(),
            "model_exists": self.model_path.exists(),
            "model_path": str(self.model_path),
            "n_gpu_layers": self.n_gpu_layers
        }

        # Try to get llama-cli version
        try:
            result = subprocess.run(
                [str(self.llama_cli), "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            status["llama_version"] = result.stdout.strip()
        except Exception as e:
            status["llama_version_error"] = str(e)

        return status

    @classmethod
    def from_config(cls, config: LlamaConfig, llama_cli_path: str | Path = "./llama.cpp/llama-cli"):
        """Create client from config object."""
        return cls(
            model_path=config.model_path,
            llama_cli_path=llama_cli_path,
            n_gpu_layers=config.n_gpu_layers,
            ctx_size=config.ctx_size,
            threads=config.threads
        )
