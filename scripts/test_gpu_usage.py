#!/usr/bin/env python3
"""
Test GPU usage during Ollama inference.

Checks if DeepSeek-R1-14B uses both GPUs (RTX 3060 Ti + GTX 1060).
"""

import sys
import subprocess
import time
import threading
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.model_orchestrator import ModelOrchestrator
from src.core.local_ollama_provider import LocalOllamaProvider
from src.core.model_provider import ModelCapability, QualityLevel


def monitor_gpu_usage(duration=30, interval=2):
    """Monitor GPU usage for specified duration"""
    print(f"\n{'='*70}")
    print(f"GPU Monitoring (every {interval}s for {duration}s)")
    print(f"{'='*70}\n")

    gpu_samples = []
    start_time = time.time()

    while time.time() - start_time < duration:
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=index,name,memory.used,utilization.gpu",
                 "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                timestamp = time.time() - start_time
                print(f"\n[{timestamp:.1f}s]")

                for line in result.stdout.strip().split('\n'):
                    parts = line.split(',')
                    if len(parts) >= 4:
                        gpu_idx = parts[0].strip()
                        gpu_name = parts[1].strip()
                        mem_used = parts[2].strip()
                        util = parts[3].strip()

                        print(f"  GPU {gpu_idx} ({gpu_name}): {mem_used}MB VRAM, {util}% utilization")

                        gpu_samples.append({
                            "time": timestamp,
                            "gpu": gpu_idx,
                            "mem_used": int(mem_used),
                            "util": int(util)
                        })

        except Exception as e:
            print(f"  Monitor error: {e}")

        time.sleep(interval)

    return gpu_samples


def run_inference():
    """Run DeepSeek inference"""
    print("\n" + "="*70)
    print("Starting DeepSeek-R1-14B Inference")
    print("="*70)

    # Setup orchestrator
    orchestrator = ModelOrchestrator(profile="standard")
    ollama = LocalOllamaProvider("config/models")
    orchestrator.register_provider("ollama", ollama)

    # Run inference with REASONING (should use DeepSeek)
    prompt = """Analyze the following business opportunity:

A startup wants to create a marketplace for sustainable products.
They have 3 options:
1. B2C marketplace targeting consumers
2. B2B marketplace for businesses
3. Hybrid approach

Which option is best and why? Provide detailed reasoning."""

    print("\nGenerating response (this takes 20-30s)...")
    print("(Monitor GPU usage above)")

    response = orchestrator.generate(
        prompt=prompt,
        capability=ModelCapability.REASONING,
        quality=QualityLevel.BALANCED  # Uses DeepSeek
    )

    print("\n" + "="*70)
    print("Response Generated")
    print("="*70)
    print(f"\nModel: {response.model}")
    print(f"Content length: {len(response.content)} chars")
    print(f"\nFirst 200 chars:")
    print(response.content[:200] + "...")


def main():
    print("="*70)
    print("  GPU Usage Test - Ollama with DeepSeek-R1-14B")
    print("="*70)
    print("\nThis test will:")
    print("  1. Monitor GPU usage every 2s")
    print("  2. Run DeepSeek inference in parallel")
    print("  3. Check if both GPUs are used\n")

    # Start GPU monitoring in background thread
    monitor_thread = threading.Thread(target=monitor_gpu_usage, args=(35, 2), daemon=True)
    monitor_thread.start()

    # Wait a bit for initial GPU state
    time.sleep(3)

    # Run inference
    try:
        run_inference()
    except Exception as e:
        print(f"\n❌ Inference failed: {e}")
        import traceback
        traceback.print_exc()

    # Wait for monitoring to finish
    time.sleep(5)

    print("\n" + "="*70)
    print("Test Complete")
    print("="*70)
    print("\nAnalysis:")
    print("  - If GPU 0 shows high usage and GPU 1 shows 0: Single GPU only")
    print("  - If both GPUs show usage: Multi-GPU working")
    print("  - DeepSeek-R1-14B needs 9GB, so should use both (8GB + 3GB)")
    print("="*70)


if __name__ == "__main__":
    main()
