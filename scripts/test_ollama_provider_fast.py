#!/usr/bin/env python3
"""
Fast test for LocalOllamaProvider (only Llama 3.1 8B)
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.local_ollama_provider import LocalOllamaProvider
from src.core.model_provider import ModelCapability, QualityLevel


def main():
    print("="*60)
    print("  LocalOllamaProvider Fast Test")
    print("="*60)

    # Initialize
    print("\n1. Initializing provider...")
    provider = LocalOllamaProvider(config_dir="config/models")
    print(f"   Loaded {len(provider.models)} models:")
    for mid in provider.models.keys():
        print(f"     - {mid}")

    # Capabilities
    print("\n2. Checking capabilities...")
    caps = provider.get_available_capabilities()
    for cap, quals in caps.items():
        print(f"   {cap.value}: {[q.value for q in quals]}")

    # Ollama check
    print("\n3. Checking Ollama...")
    is_avail = provider.is_available()
    print(f"   Ollama running: {is_avail}")

    if not is_avail:
        print("   ERROR: Start Ollama first!")
        return

    # Resources
    print("\n4. Checking resources...")
    res = provider.get_resource_usage()
    print(f"   RAM: {res.get('system_ram_percent', 0):.1f}%")
    print(f"   VRAM: {res.get('vram_mb', 0):.0f} / {res.get('vram_total_mb', 0):.0f} MB")

    # Fast extraction test
    print("\n5. Testing FAST extraction (Llama 3.1 8B)...")
    try:
        response = provider.generate(
            prompt="What is 2+2? Answer in one word.",
            capability=ModelCapability.EXTRACTION,
            quality=QualityLevel.FAST
        )
        print(f"   Model: {response.model_used}")
        print(f"   Latency: {response.latency_ms:.0f}ms")
        print(f"   Tokens: {response.tokens_used}")
        print(f"   Response: {response.content[:100]}")
    except Exception as e:
        print(f"   ERROR: {e}")
        return

    print("\n" + "="*60)
    print("  ✅ All fast tests passed!")
    print("="*60)


if __name__ == "__main__":
    main()
