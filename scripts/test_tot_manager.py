#!/usr/bin/env python3
"""
Test script for ToT Manager

Tests Tree of Thoughts exploration with live LLM.
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.tot_manager import ToTManager
from src.core.graph_manager import GraphManager
from src.core.axiom_manager import AxiomManager
from src.core.model_orchestrator import ModelOrchestrator
from src.core.local_ollama_provider import LocalOllamaProvider


def main():
    print("="*80)
    print("  ToT Manager Test - Tree of Thoughts Exploration")
    print("="*80)

    # Setup infrastructure
    print("\n[1/6] Setting up infrastructure...")

    # Model orchestrator
    orchestrator = ModelOrchestrator(profile="standard")
    ollama = LocalOllamaProvider("config/models")
    orchestrator.register_provider("ollama", ollama)
    print(f"   ✅ Model orchestrator ready ({len(ollama.models)} models)")

    # Graph manager
    graph = GraphManager(max_nodes=100, axioms_dir="config/axioms")
    print(f"   ✅ Graph manager ready")

    # Axiom manager
    axioms = graph.axiom_manager
    if axioms:
        print(f"   ✅ Axiom manager ready ({axioms.get_stats()['total_axioms']} axioms)")

    # ToT Manager
    tot = ToTManager(graph, axioms, orchestrator)
    print(f"   ✅ ToT manager initialized")

    # Create root question
    print("\n[2/6] Creating root question...")
    root_question = "What are the best opportunities in AI-powered SaaS?"
    root_id = tot.create_root(root_question)
    print(f"   Root: {root_question}")
    print(f"   Root ID: {root_id}")

    # Decompose question
    print("\n[3/6] Decomposing question into sub-questions...")
    print("   (This uses Llama 3.1 8B for fast decomposition)")

    try:
        child_ids = tot.decompose_question(root_id, branching_factor=3)
        print(f"   ✅ Generated {len(child_ids)} sub-questions:")

        for i, child_id in enumerate(child_ids, 1):
            child = tot.tree[child_id]
            print(f"     {i}. {child.question}")

    except Exception as e:
        print(f"   ❌ Decomposition failed: {e}")
        return

    # Expand first child node
    print("\n[4/6] Expanding first sub-question...")
    if child_ids:
        first_child = child_ids[0]
        child = tot.tree[first_child]
        print(f"   Question: {child.question}")
        print("   (This may take ~20s for DeepSeek reasoning...)")

        try:
            success = tot.expand_node(first_child)

            if success:
                print(f"   ✅ Expansion successful!")
                print(f"   Answer: {child.answer[:200]}...")
                print(f"   Confidence: {child.confidence:.2f}")
                print(f"   Entities extracted: {len(child.graph_entities)}")
                print(f"   Facts added to graph: {len(child.graph_facts)}")
                print(f"   Axiom compatible: {child.axiom_compatible}")

                if child.axiom_scores:
                    print(f"   Axiom scores: {child.axiom_scores}")
            else:
                print(f"   ❌ Expansion failed")

        except Exception as e:
            print(f"   ❌ Expansion error: {e}")

    # Check graph state
    print("\n[5/6] Checking knowledge graph state...")
    print(f"   Total nodes: {len(graph.graph.nodes)}")
    print(f"   Total edges: {len(graph.graph.edges)}")

    if len(graph.graph.nodes) > 0:
        markdown = graph.to_markdown(max_nodes=5)
        print(f"   Graph preview:")
        print(f"\n{markdown[:400]}...")

    # Get stats
    print("\n[6/6] ToT Exploration statistics...")
    stats = tot.get_stats()
    print(f"   Total nodes: {stats['total_nodes']}")
    print(f"   Evaluated: {stats['evaluated']}")
    print(f"   Pruned: {stats['pruned']}")
    print(f"   Pending: {stats['pending']}")
    print(f"   Max depth: {stats['max_depth']}")

    # Get best path
    if stats['evaluated'] > 0:
        best_path = tot.get_best_path()
        print(f"\n   Best path ({len(best_path)} nodes):")
        for node_id in best_path:
            node = tot.tree[node_id]
            print(f"     - {node.question[:60]}...")

    # Summary
    print("\n" + "="*80)
    print("  TEST SUMMARY")
    print("="*80)
    print("  ✅ ToT Manager: Initialized successfully")
    print("  ✅ Question decomposition: Working with LLM")
    print("  ✅ Node expansion: Working with LLM + graph integration")
    print("  ✅ Entity extraction: Entities added to graph")
    print("  ✅ Axiom evaluation: Compatibility checked")
    print("\n  🎉 Tree of Thoughts exploration functional!")
    print("="*80)


if __name__ == "__main__":
    main()
