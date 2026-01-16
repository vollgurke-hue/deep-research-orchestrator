"""
Test script for LlamaCppClient.

This tests basic functionality with TinyLlama model.
"""
from src.models.llama_cpp_client import LlamaCppClient
from pathlib import Path

def test_health_check():
    """Test 1: Health Check"""
    print("=" * 60)
    print("TEST 1: Health Check")
    print("=" * 60)

    client = LlamaCppClient(
        model_path="models/tinyllama-1.1b.gguf",
        llama_cli_path="./llama.cpp/build/bin/llama-cli",
        n_gpu_layers=999,
        ctx_size=2048
    )

    status = client.health_check()
    print("Health Check Results:")
    for key, value in status.items():
        print(f"  {key}: {value}")

    return client

def test_simple_generation(client):
    """Test 2: Simple Generation"""
    print("\n" + "=" * 60)
    print("TEST 2: Simple Generation (no system prompt)")
    print("=" * 60)

    prompt = "What is the capital of France?"
    print(f"Prompt: {prompt}")
    print("\nGenerating...")

    try:
        response = client.generate(
            prompt=prompt,
            temperature=0.1,
            max_tokens=50
        )
        print(f"\nResponse:\n{response}")
        return True
    except Exception as e:
        print(f"\nERROR: {e}")
        return False

def test_system_prompt(client):
    """Test 3: Generation with System Prompt"""
    print("\n" + "=" * 60)
    print("TEST 3: Generation with System Prompt")
    print("=" * 60)

    system_prompt = "You are a helpful math tutor. Answer concisely."
    prompt = "What is 15 + 27?"

    print(f"System: {system_prompt}")
    print(f"Prompt: {prompt}")
    print("\nGenerating...")

    try:
        response = client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.1,
            max_tokens=30
        )
        print(f"\nResponse:\n{response}")
        return True
    except Exception as e:
        print(f"\nERROR: {e}")
        return False

if __name__ == "__main__":
    print("Testing LlamaCppClient with TinyLlama")
    print("Note: TinyLlama is weak, expect basic/incorrect answers\n")

    # Test 1: Health Check
    client = test_health_check()

    # Test 2: Simple Generation
    success_simple = test_simple_generation(client)

    # Test 3: System Prompt
    success_system = test_system_prompt(client)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Health Check: ✓")
    print(f"Simple Generation: {'✓' if success_simple else '✗'}")
    print(f"System Prompt: {'✓' if success_system else '✗'}")
    print("\nConclusion: LlamaCppClient infrastructure is " +
          ("WORKING" if (success_simple and success_system) else "BROKEN"))
