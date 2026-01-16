#!/usr/bin/env python3
"""
Test llama.cpp Multi-GPU Support

Tests tensor-split across RTX 3060 Ti (8GB) + GTX 1060 (3GB).
"""

import sys
import subprocess
import time
import threading
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.model_orchestrator import ModelOrchestrator
from src.core.local_llamacpp_provider import LocalLlamaCppProvider
from src.core.model_provider import ModelCapability, QualityLevel


def monitor_gpu_usage(duration=40, interval=2):
    """Monitor GPU usage"""
    print(f"\n{'='*70}")
    print(f"GPU Monitoring (every {interval}s)")
    print(f"{'='*70}\n")

    max_gpu0_mem = 0
    max_gpu1_mem = 0
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
                        gpu_idx = int(parts[0].strip())
                        gpu_name = parts[1].strip()
                        mem_used = int(parts[2].strip())
                        util = parts[3].strip()

                        print(f"  GPU {gpu_idx} ({gpu_name}): {mem_used}MB VRAM, {util}% util")

                        if gpu_idx == 0:
                            max_gpu0_mem = max(max_gpu0_mem, mem_used)
                        elif gpu_idx == 1:
                            max_gpu1_mem = max(max_gpu1_mem, mem_used)

        except Exception as e:
            print(f"  Monitor error: {e}")

        time.sleep(interval)

    print(f"\n{'='*70}")
    print(f"Peak VRAM Usage:")
    print(f"  GPU 0: {max_gpu0_mem}MB")
    print(f"  GPU 1: {max_gpu1_mem}MB")
    print(f"{'='*70}")


def run_inference():
    """Run llama.cpp inference"""
    print("\n" + "="*70)
    print("Starting llama.cpp with Phi-3 Mini")
    print("="*70)

    # Setup orchestrator with llama.cpp provider
    orchestrator = ModelOrchestrator(profile="standard")
    llamacpp = LocalLlamaCppProvider("config/models", port=8081, auto_start=True)
    orchestrator.register_provider("llamacpp", llamacpp)

    print("\n✓ LocalLlamaCppProvider registered")
    print("  This will use --tensor-split for both GPUs")

    # Run inference
    prompt = """Explain the concept of Monte Carlo Tree Search in 3 sentences."""

    print("\n" + "="*70)
    print("Generating response...")
    print("="*70)
    print("(Watch GPU usage above - both should show activity!)")

    try:
        response = orchestrator.generate(
            prompt=prompt,
            capability=ModelCapability.REASONING,
            quality=QualityLevel.BALANCED,
            prefer_provider="llamacpp"
        )

        print("\n" + "="*70)
        print("Response Generated")
        print("="*70)
        print(f"\nProvider: {response.provider}")
        print(f"Content: {response.content[:200]}...")

    except Exception as e:
        print(f"\n❌ Inference failed: {e}")
        import traceback
        traceback.print_exc()


def main():
    print("="*70)
    print("  llama.cpp Multi-GPU Test with Phi-3 Mini")
    print("="*70)
    print("\nSetup:")
    print("  GPU 0: RTX 3060 Ti (8GB VRAM)")
    print("  GPU 1: GTX 1060 3GB (3GB VRAM)")
    print("  Model: Phi-3 Mini Q4 (2.3GB)")
    print("  Tensor split: 8192,3072 (proportional to VRAM)")
    print("\nExpected:")
    print("  Both GPUs should show VRAM usage during inference")
    print("="*70)

    # Start GPU monitoring in background
    monitor_thread = threading.Thread(target=monitor_gpu_usage, args=(45, 2), daemon=True)
    monitor_thread.start()

    time.sleep(3)

    # Run inference
    run_inference()

    # Wait for monitoring to finish
    time.sleep(5)

    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)
    print("\nAnalysis:")
    print("  ✓ If both GPUs show increased VRAM: Multi-GPU working!")
    print("  ✗ If only GPU 0 increases: Single GPU only")
    print("="*70)


if __name__ == "__main__":
    main()
