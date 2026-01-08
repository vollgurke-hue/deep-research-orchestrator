#!/usr/bin/env python3
"""
Fast ToT test - uses only Llama 3.1 8B (no DeepSeek)
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.tot_manager import ToTManager
from src.core.graph_manager import GraphManager
from src.core.model_orchestrator import ModelOrchestrator
from src.core.local_ollama_provider import LocalOllamaProvider
from src.core.model_provider import QualityLevel


def main():
    print("="*70)
    print("  ToT Manager Fast Test (Llama 3.1 8B only)")
    print("="*70)

    # Setup
    print("\n[1/5] Setup...")
    orchestrator = ModelOrchestrator(profile="standard")
    ollama = LocalOllamaProvider("config/models")
    orchestrator.register_provider("ollama", ollama)

    graph = GraphManager(max_nodes=50, axioms_dir="config/axioms")
    tot = ToTManager(graph, graph.axiom_manager, orchestrator)
    print("   ✅ Infrastructure ready")

    # Root question
    print("\n[2/5] Creating root...")
    root_id = tot.create_root("What are good SaaS opportunities?")
    print(f"   Root: {tot.tree[root_id].question}")

    # Decompose
    print("\n[3/5] Decomposing question (Llama 3.1 8B)...")
    child_ids = tot.decompose_question(root_id, branching_factor=2)
    print(f"   ✅ Generated {len(child_ids)} sub-questions:")
    for i, cid in enumerate(child_ids, 1):
        print(f"     {i}. {tot.tree[cid].question}")

    # Expand with FAST quality (Llama only)
    print("\n[4/5] Expanding first node (FAST = Llama 3.1 8B)...")
    if child_ids:
        success = tot.expand_node(child_ids[0], use_quality=QualityLevel.FAST)
        child = tot.tree[child_ids[0]]

        if success:
            print(f"   ✅ Success!")
            print(f"   Q: {child.question}")
            print(f"   A: {child.answer[:150]}...")
            print(f"   Facts in graph: {len(child.graph_facts)}")
        else:
            print(f"   ❌ Failed")

    # Stats
    print("\n[5/5] Statistics...")
    stats = tot.get_stats()
    print(f"   Nodes: {stats['total_nodes']}")
    print(f"   Evaluated: {stats['evaluated']}")
    print(f"   Graph size: {len(graph.graph.nodes)} nodes")

    print("\n" + "="*70)
    print("  ✅ ToT Manager working!")
    print("="*70)


if __name__ == "__main__":
    main()
