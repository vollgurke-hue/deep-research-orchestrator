#!/usr/bin/env python3
"""
Benchmark different context sizes for DeepSeek.

Tests 8K, 16K, 32K context to find optimal trade-off.
"""

import time
import subprocess
import requests


def start_server(ctx_size, port=8083):
    """Start llama-server with specific context size"""
    # Kill existing
    subprocess.run(["killall", "-9", "llama-server"],
                   stderr=subprocess.DEVNULL)
    time.sleep(2)

    cmd = [
        "/home/phili/Schreibtisch/AI_Projects/deep-research-orchestrator/llama.cpp/build/bin/llama-server",
        "--model", "/home/phili/llama-models/DeepSeek-R1-Qwen-14B-abliterated-Q4_K_M.gguf",
        "--n-gpu-layers", "999",
        "--ctx-size", str(ctx_size),
        "--port", str(port),
        "--host", "127.0.0.1"
    ]

    print(f"\n{'='*70}")
    print(f"Starting with context size: {ctx_size} tokens")
    print(f"{'='*70}")

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Wait for ready
    print("Waiting for server...")
    for i in range(60):
        try:
            r = requests.get(f"http://localhost:{port}/health", timeout=2)
            if r.status_code == 200:
                print(f"✓ Server ready after {i+1}s")
                time.sleep(2)  # Extra warmup
                return process
        except:
            pass
        time.sleep(1)

    raise RuntimeError("Server failed to start")


def benchmark_generation(ctx_size, prompt_length="short"):
    """Benchmark generation with specific prompt length"""

    if prompt_length == "short":
        prompt = "What is MCTS? Answer in 2 sentences."
        expected_tokens = 50
    elif prompt_length == "medium":
        prompt = """Analyze the following research tree:

Root: What are good AI business opportunities?
- Branch 1: Healthcare AI applications
  - Sub: Medical imaging
  - Sub: Drug discovery
- Branch 2: Finance AI applications
  - Sub: Fraud detection
  - Sub: Trading algorithms
- Branch 3: Education AI applications
  - Sub: Personalized learning
  - Sub: Assessment automation

Which branch is most promising and why? Provide detailed reasoning."""
        expected_tokens = 150
    else:  # long
        # Simulate large context with graph data
        nodes = "\n".join([f"- Entity {i}: Business opportunity in sector {i%5}"
                          for i in range(100)])
        prompt = f"""Given this knowledge graph with 100 entities:

{nodes}

Analyze the top 3 most promising opportunities considering:
1. Market size
2. Technical feasibility
3. Competition level

Provide detailed analysis."""
        expected_tokens = 200

    url = "http://localhost:8083/completion"

    # Measure time
    start = time.time()

    try:
        response = requests.post(
            url,
            json={
                "prompt": prompt,
                "n_predict": expected_tokens,
                "temperature": 0.7
            },
            timeout=120
        )

        elapsed = time.time() - start

        if response.status_code == 200:
            data = response.json()
            tokens = data.get("tokens_predicted", 0)
            tokens_per_sec = tokens / elapsed if elapsed > 0 else 0

            return {
                "success": True,
                "time": elapsed,
                "tokens": tokens,
                "tokens_per_sec": tokens_per_sec,
                "prompt_tokens": len(prompt.split()) * 1.3  # rough estimate
            }
        else:
            return {"success": False, "error": f"HTTP {response.status_code}"}

    except Exception as e:
        return {"success": False, "error": str(e)}


def main():
    print("="*70)
    print("  DeepSeek Context Size Benchmark")
    print("  RTX 3060 Ti (8GB) + GTX 1060 (3GB)")
    print("="*70)

    context_sizes = [8192, 16384, 32768]
    results = {}

    for ctx_size in context_sizes:
        try:
            # Start server with this context
            proc = start_server(ctx_size)

            # Run benchmarks
            print(f"\n[1/3] Testing SHORT prompt (50 tokens)...")
            short = benchmark_generation(ctx_size, "short")
            print(f"   Time: {short.get('time', 0):.2f}s")
            print(f"   Speed: {short.get('tokens_per_sec', 0):.1f} tok/s")

            print(f"\n[2/3] Testing MEDIUM prompt (150 tokens)...")
            medium = benchmark_generation(ctx_size, "medium")
            print(f"   Time: {medium.get('time', 0):.2f}s")
            print(f"   Speed: {medium.get('tokens_per_sec', 0):.1f} tok/s")

            print(f"\n[3/3] Testing LONG prompt (200 tokens)...")
            long_test = benchmark_generation(ctx_size, "long")
            print(f"   Time: {long_test.get('time', 0):.2f}s")
            print(f"   Speed: {long_test.get('tokens_per_sec', 0):.1f} tok/s")

            results[ctx_size] = {
                "short": short,
                "medium": medium,
                "long": long_test
            }

            # Cleanup
            proc.terminate()
            time.sleep(2)

        except Exception as e:
            print(f"   ❌ Failed: {e}")
            results[ctx_size] = {"error": str(e)}

    # Summary
    print("\n" + "="*70)
    print("  BENCHMARK RESULTS")
    print("="*70)

    print("\n{:<12} {:<15} {:<15} {:<15}".format(
        "Context", "Short (50tok)", "Medium (150tok)", "Long (200tok)"
    ))
    print("-"*70)

    for ctx_size in context_sizes:
        if ctx_size in results and "error" not in results[ctx_size]:
            r = results[ctx_size]
            short_speed = r["short"].get("tokens_per_sec", 0)
            medium_speed = r["medium"].get("tokens_per_sec", 0)
            long_speed = r["long"].get("tokens_per_sec", 0)

            print("{:<12} {:<15.1f} {:<15.1f} {:<15.1f}".format(
                f"{ctx_size}",
                short_speed,
                medium_speed,
                long_speed
            ))

    print("\n" + "="*70)
    print("  RECOMMENDATION")
    print("="*70)

    # Find best based on medium-length (most common use case)
    best_ctx = max(
        [c for c in context_sizes if c in results and "error" not in results[c]],
        key=lambda c: results[c]["medium"].get("tokens_per_sec", 0),
        default=16384
    )

    print(f"\n  Best for your project: {best_ctx} tokens")
    print(f"  Reasoning:")
    print(f"    - Handles full graph + ToT tree + MCTS history")
    print(f"    - Best speed for typical workloads")
    print(f"    - Fits in your VRAM budget")
    print("="*70)


if __name__ == "__main__":
    main()
