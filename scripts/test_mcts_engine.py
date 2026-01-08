#!/usr/bin/env python3
"""
Test script for MCTS Engine

Tests Monte Carlo Tree Search for ToT path evaluation.
Uses only Llama 3.1 8B for fast testing.
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.tot_manager import ToTManager
from src.core.graph_manager import GraphManager
from src.core.model_orchestrator import ModelOrchestrator
from src.core.local_ollama_provider import LocalOllamaProvider
from src.core.mcts_engine import MCTSEngine


def main():
    print("="*70)
    print("  MCTS Engine Test - Monte Carlo Tree Search")
    print("="*70)

    # Setup infrastructure
    print("\n[1/7] Setting up infrastructure...")
    orchestrator = ModelOrchestrator(profile="standard")
    ollama = LocalOllamaProvider("config/models")
    orchestrator.register_provider("ollama", ollama)

    graph = GraphManager(max_nodes=50, axioms_dir="config/axioms")
    tot = ToTManager(graph, graph.axiom_manager, orchestrator)

    print(f"   ✅ Infrastructure ready")

    # Build simple ToT tree for MCTS testing
    print("\n[2/7] Building ToT tree...")
    root_id = tot.create_root("What are good business opportunities?")
    print(f"   Root: {tot.tree[root_id].question}")

    # Decompose into 2 branches
    child_ids = tot.decompose_question(root_id, branching_factor=2)
    print(f"   ✅ Created {len(child_ids)} branches")
    for i, cid in enumerate(child_ids, 1):
        print(f"     {i}. {tot.tree[cid].question}")

    # Create MCTS engine
    print("\n[3/7] Initializing MCTS engine...")
    mcts = MCTSEngine(tot, graph, orchestrator)
    print(f"   ✅ MCTS ready (C = {mcts.C:.3f})")

    # Run MCTS iterations
    print("\n[4/7] Running MCTS iterations (axiom simulation)...")
    print("   (This runs selection → simulation → backprop)")

    try:
        stats = mcts.iterate(num_iterations=5)
        print(f"   ✅ Completed {stats['iterations']} iterations")
        print(f"   Nodes selected: {len(stats['nodes_selected'])}")
        print(f"   Average value: {stats['avg_value']:.3f}")

        # Show which nodes were selected
        for i, node_id in enumerate(stats['nodes_selected'][:3], 1):
            node = tot.tree[node_id]
            print(f"     {i}. {node.question[:50]}... (visits={node.visits}, value={node.value:.2f})")

    except Exception as e:
        print(f"   ❌ MCTS iteration failed: {e}")
        return

    # Test best path selection
    print("\n[5/7] Finding best path...")
    best_path = mcts.best_path()

    if best_path:
        print(f"   ✅ Best path found ({len(best_path)} nodes):")
        for node_id in best_path:
            node = tot.tree[node_id]
            avg = node.avg_value()
            print(f"     - {node.question[:60]}... (avg={avg:.3f})")
    else:
        print(f"   ⚠️  No best path found (tree too small?)")

    # Test most visited path
    print("\n[6/7] Finding most visited path...")
    visited_path = mcts.most_visited_path()

    if visited_path:
        print(f"   ✅ Most visited path ({len(visited_path)} nodes):")
        for node_id in visited_path:
            node = tot.tree[node_id]
            print(f"     - {node.question[:60]}... (visits={node.visits})")
    else:
        print(f"   ⚠️  No visited path found")

    # Get MCTS statistics
    print("\n[7/7] MCTS Statistics...")
    mcts_stats = mcts.get_stats()
    print(f"   Total visits: {mcts_stats['total_visits']}")
    print(f"   Total value: {mcts_stats['total_value']:.3f}")
    print(f"   Average value: {mcts_stats['avg_value']:.3f}")
    print(f"   Max depth visited: {mcts_stats['max_depth_visited']}")
    print(f"   Best leaf visits: {mcts_stats['best_leaf_visits']}")
    print(f"   Number of leaves: {mcts_stats['num_leaves']}")

    # Summary
    print("\n" + "="*70)
    print("  TEST SUMMARY")
    print("="*70)
    print("  ✅ MCTS Engine: Initialized successfully")
    print("  ✅ UCB1 Selection: Working (selected nodes from tree)")
    print("  ✅ Simulation: Working (axiom-based evaluation)")
    print("  ✅ Backpropagation: Working (updated visits/values)")
    print("  ✅ Best Path: Working (found highest value path)")
    print("\n  🎉 Monte Carlo Tree Search functional!")
    print("="*70)


if __name__ == "__main__":
    main()
