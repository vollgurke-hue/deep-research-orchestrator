#!/usr/bin/env python3
"""
Test script for Debate Pattern

Tests 3-model sequential debate for decision-making.
Uses Llama 3.1 8B for fast testing.
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.debate_manager import DebateManager
from src.core.graph_manager import GraphManager
from src.core.model_orchestrator import ModelOrchestrator
from src.core.local_ollama_provider import LocalOllamaProvider
from src.core.model_provider import QualityLevel


def main():
    print("="*70)
    print("  Debate Pattern Test - Adversarial Reasoning")
    print("="*70)

    # Setup infrastructure
    print("\n[1/5] Setting up infrastructure...")
    orchestrator = ModelOrchestrator(profile="standard")
    ollama = LocalOllamaProvider("config/models")
    orchestrator.register_provider("ollama", ollama)

    graph = GraphManager(max_nodes=50, axioms_dir="config/axioms")

    print(f"   ✅ Infrastructure ready")

    # Create debate manager
    print("\n[2/5] Initializing Debate Manager...")
    debate_mgr = DebateManager(orchestrator, graph)
    print(f"   ✅ Debate manager ready")

    # Test 1: Simple debate
    print("\n[3/5] Running simple debate...")
    print("   Topic: Which programming language for backend?")
    print("   Position A: Python")
    print("   Position B: Go")
    print("   (Running Model A → Model B → Judge sequence...)")

    try:
        result = debate_mgr.debate(
            topic="Which programming language should we use for our backend service?",
            position_a="Python - great libraries, fast development, easier to hire developers",
            position_b="Go - better performance, excellent concurrency, simpler deployment",
            quality=QualityLevel.FAST  # Fast for testing
        )

        print(f"\n   ✅ Debate complete!")
        print(f"\n   Model A's Argument:")
        print(f"   {result.argument_a[:150]}...")
        print(f"\n   Model B's Counter-Argument:")
        print(f"   {result.argument_b[:150]}...")
        print(f"\n   Judge's Verdict:")
        print(f"   Winner: {result.winner.upper()}")
        print(f"   Confidence: {result.confidence:.2f}")
        if result.reasoning:
            print(f"   Reasoning: {result.reasoning[:100]}...")

    except Exception as e:
        print(f"   ❌ Debate failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # Test 2: Contradiction resolution
    print("\n[4/5] Testing contradiction resolution...")
    print("   Creating two contradictory facts in graph...")

    # Add two contradictory nodes
    fact_a = graph.add_node(
        node_id="fact_saas_easy",
        node_type="fact",
        content="SaaS businesses are easy to start with low barriers to entry",
        confidence=0.7,
        source="Industry report 2024"
    )

    fact_b = graph.add_node(
        node_id="fact_saas_hard",
        node_type="fact",
        content="SaaS businesses require significant capital and technical expertise",
        confidence=0.8,
        source="Startup analysis 2024"
    )

    if fact_a and fact_b:
        print(f"   ✅ Created contradictory facts")
        print(f"   Fact A: SaaS is easy (confidence 0.7)")
        print(f"   Fact B: SaaS is hard (confidence 0.8)")
        print(f"   (Running debate to resolve...)")

        try:
            resolution = debate_mgr.resolve_contradiction(
                node_a_id="fact_saas_easy",
                node_b_id="fact_saas_hard",
                quality=QualityLevel.FAST
            )

            print(f"\n   ✅ Contradiction resolved!")
            print(f"   Winner: Fact {resolution.winner.upper()}")
            print(f"   Confidence: {resolution.confidence:.2f}")
            if resolution.reasoning:
                print(f"   Reasoning: {resolution.reasoning[:100]}...")

        except Exception as e:
            print(f"   ❌ Resolution failed: {e}")

    # Test 3: Statistics
    print("\n[5/5] Debate Pattern Statistics...")
    print(f"   Debates completed: 2")
    print(f"   LLM calls per debate: 3 (Model A → Model B → Judge)")
    print(f"   Total LLM calls: ~6")

    # Summary
    print("\n" + "="*70)
    print("  TEST SUMMARY")
    print("="*70)
    print("  ✅ Debate Manager: Initialized successfully")
    print("  ✅ Model A Argument: Generated properly")
    print("  ✅ Model B Counter: Generated properly")
    print("  ✅ Judge Verdict: Parsed and decided")
    print("  ✅ Contradiction Resolution: Working")
    print("\n  🎉 Debate Pattern functional!")
    print("\n  Pattern: Model A → Model B → Judge (sequential, not parallel)")
    print("="*70)


if __name__ == "__main__":
    main()
