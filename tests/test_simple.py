#!/usr/bin/env python3
"""
Simple LlamaCppClient Test
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from models.llama_cpp_client import LlamaCppClient

print("=" * 70)
print("SIMPLE LLAMACPP TEST")
print("=" * 70)

try:
    print("\n1. Creating client...")
    client = LlamaCppClient(
        model_path=Path("/home/phili/llama-models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"),
        llama_cli_path=Path("llama.cpp/build/bin/llama-cli"),
        n_gpu_layers=999,
        ctx_size=2048,
        threads=4
    )
    print("✓ Client created")

    print("\n2. Running health check...")
    health = client.health_check()
    for key, value in health.items():
        print(f"   {key}: {value}")

    print("\n3. Testing generation (simple prompt, 5 tokens max)...")
    print("   Prompt: 'What is 2+2? Answer with only the number.'")

    response = client.generate(
        prompt="What is 2+2? Answer with only the number.",
        temperature=0.1,
        max_tokens=5
    )

    print(f"\n✓ Response: '{response}'")
    print("\n✓ Test successful!")

except Exception as e:
    print(f"\n✗ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
