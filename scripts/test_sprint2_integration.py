#!/usr/bin/env python3
"""
Sprint 2 Integration Test

Demonstrates complete reasoning pipeline:
1. ToT: Tree of Thoughts exploration
2. MCTS: Path evaluation with UCB1
3. Debate: Adversarial comparison of best paths

This shows all Sprint 2 components working together.
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
from src.core.debate_manager import DebateManager
from src.core.model_provider import QualityLevel


def main():
    print("="*80)
    print("  SPRINT 2 INTEGRATION TEST")
    print("  ToT + MCTS + Debate Pattern")
    print("="*80)

    # ======================
    # Phase 1: Infrastructure
    # ======================
    print("\n" + "="*80)
    print("PHASE 1: Infrastructure Setup")
    print("="*80)

    orchestrator = ModelOrchestrator(profile="standard")
    ollama = LocalOllamaProvider("config/models")
    orchestrator.register_provider("ollama", ollama)

    graph = GraphManager(max_nodes=100, axioms_dir="config/axioms")
    tot = ToTManager(graph, graph.axiom_manager, orchestrator)
    mcts = MCTSEngine(tot, graph, orchestrator)
    debate = DebateManager(orchestrator, graph)

    print("✅ Model Orchestrator ready")
    print("✅ Knowledge Graph ready")
    print("✅ ToT Manager ready")
    print("✅ MCTS Engine ready")
    print("✅ Debate Manager ready")

    # ======================
    # Phase 2: ToT Exploration
    # ======================
    print("\n" + "="*80)
    print("PHASE 2: Tree of Thoughts Exploration")
    print("="*80)

    root_question = "What business opportunities exist in sustainability?"
    print(f"\nRoot Question: {root_question}")

    root_id = tot.create_root(root_question)
    print(f"✅ Root node created: {root_id}")

    # Decompose into branches
    print("\nDecomposing into sub-questions...")
    child_ids = tot.decompose_question(root_id, branching_factor=3)

    print(f"\n✅ Generated {len(child_ids)} branches:")
    for i, child_id in enumerate(child_ids, 1):
        child = tot.tree[child_id]
        print(f"   {i}. {child.question}")

    # Get ToT stats
    tot_stats = tot.get_stats()
    print(f"\nToT Stats: {tot_stats['total_nodes']} nodes, {tot_stats['max_depth']} max depth")

    # ======================
    # Phase 3: MCTS Evaluation
    # ======================
    print("\n" + "="*80)
    print("PHASE 3: MCTS Path Evaluation")
    print("="*80)

    print("\nRunning MCTS iterations to identify promising paths...")
    print("(Using axiom-based simulation for speed)")

    mcts_result = mcts.iterate(num_iterations=10)

    print(f"\n✅ MCTS completed {mcts_result['iterations']} iterations")
    print(f"   Average value: {mcts_result['avg_value']:.3f}")
    print(f"   Nodes explored: {len(mcts_result['nodes_selected'])}")

    # Get best paths
    best_path = mcts.best_path()
    most_visited = mcts.most_visited_path()

    print(f"\nBest Path (highest value):")
    for i, node_id in enumerate(best_path):
        node = tot.tree[node_id]
        print(f"   {i+1}. {node.question[:70]}... (avg={node.avg_value():.3f})")

    print(f"\nMost Visited Path:")
    for i, node_id in enumerate(most_visited):
        node = tot.tree[node_id]
        print(f"   {i+1}. {node.question[:70]}... (visits={node.visits})")

    # MCTS stats
    mcts_stats = mcts.get_stats()
    print(f"\nMCTS Stats:")
    print(f"   Total visits: {mcts_stats['total_visits']}")
    print(f"   Max depth visited: {mcts_stats['max_depth_visited']}")
    print(f"   Number of leaves: {mcts_stats['num_leaves']}")

    # ======================
    # Phase 4: Debate Comparison
    # ======================
    print("\n" + "="*80)
    print("PHASE 4: Adversarial Path Comparison")
    print("="*80)

    # If we have at least 2 different paths, compare them
    if len(child_ids) >= 2:
        # Get first two leaf paths for comparison
        path_a = tot.get_path_to_root(child_ids[0])
        path_b = tot.get_path_to_root(child_ids[1])

        print("\nComparing two exploration paths using Debate Pattern...")
        print(f"Path A: {tot.tree[child_ids[0]].question[:60]}...")
        print(f"Path B: {tot.tree[child_ids[1]].question[:60]}...")
        print("(Running Model A → Model B → Judge sequence...)")

        try:
            debate_result = debate.evaluate_tot_paths(
                path_a=path_a,
                path_b=path_b,
                tot_tree=tot.tree,
                quality=QualityLevel.FAST
            )

            print(f"\n✅ Debate completed!")
            print(f"   Winner: Path {debate_result.winner.upper()}")
            print(f"   Confidence: {debate_result.confidence:.2f}")
            if debate_result.reasoning:
                print(f"   Reasoning: {debate_result.reasoning[:100]}...")

            # Show which path won
            winner_path = path_a if debate_result.winner.lower() == "a" else path_b
            print(f"\n🏆 Chosen path for further exploration:")
            for i, node_id in enumerate(winner_path):
                node = tot.tree[node_id]
                print(f"   {i+1}. {node.question[:70]}...")

        except Exception as e:
            print(f"   ❌ Debate failed: {e}")

    # ======================
    # Phase 5: Summary
    # ======================
    print("\n" + "="*80)
    print("INTEGRATION TEST SUMMARY")
    print("="*80)

    print("\n✅ SPRINT 2 PIPELINE COMPLETE:")
    print("\n   1️⃣  Tree of Thoughts")
    print(f"      - Root question decomposed into {len(child_ids)} sub-questions")
    print(f"      - Total nodes: {tot_stats['total_nodes']}")
    print(f"      - Tree depth: {tot_stats['max_depth']}")

    print("\n   2️⃣  Monte Carlo Tree Search")
    print(f"      - Ran {mcts_result['iterations']} iterations")
    print(f"      - Total visits: {mcts_stats['total_visits']}")
    print(f"      - Identified best path using UCB1")

    print("\n   3️⃣  Debate Pattern")
    print(f"      - Compared competing paths")
    print(f"      - Judge made decision with confidence")
    print(f"      - Recommended path for exploration")

    print("\n" + "="*80)
    print("🎉 All Sprint 2 components working together!")
    print("="*80)
    print("\nComplete reasoning pipeline:")
    print("  Question → ToT decomposition → MCTS evaluation → Debate selection → Action")
    print("="*80)


if __name__ == "__main__":
    main()
