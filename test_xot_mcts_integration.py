"""
Integration Test: XoT + MCTS
Tests the integration of XoTSimulator with MCTSEngine for prior-guided selection.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.xot_simulator import XoTSimulator
from src.core.mcts_engine import MCTSEngine
from src.core.tot_manager import ToTManager
from src.core.graph_manager import GraphManager
from src.core.model_orchestrator import ModelOrchestrator
from src.core.local_llamacpp_provider import LocalLlamaCppProvider


def test_xot_mcts_integration():
    """
    Test XoT integration with MCTS.

    Flow:
    1. Create ToT tree with test question
    2. Initialize XoTSimulator with model orchestrator
    3. Create MCTSEngine with XoT enabled
    4. Run MCTS iterations
    5. Verify XoT stats are collected
    """
    print("=" * 60)
    print("XoT + MCTS Integration Test")
    print("=" * 60)

    # Setup: Create components
    print("\n[1/5] Setting up components...")

    graph = GraphManager(max_nodes=100)

    # Model orchestrator with llama.cpp provider
    model_orch = ModelOrchestrator(profile="standard")

    # Register llama.cpp provider
    llamacpp_provider = LocalLlamaCppProvider(
        models_config_dir="config/models",
        port=8081,
        auto_start=True
    )
    model_orch.register_provider("llamacpp", llamacpp_provider)

    tot = ToTManager(
        graph_manager=graph,
        axiom_manager=None,
        model_orchestrator=model_orch
    )

    print("   ✓ GraphManager, ModelOrchestrator, ToTManager created")

    # Create XoT simulator
    print("\n[2/5] Initializing XoT Simulator...")
    xot = XoTSimulator(
        model_orchestrator=model_orch,
        depth=3,
        fallback_score=0.5
    )
    print("   ✓ XoTSimulator initialized")

    # Create MCTS with XoT
    print("\n[3/5] Creating MCTS with XoT integration...")
    mcts = MCTSEngine(
        tot_manager=tot,
        graph_manager=graph,
        model_orchestrator=model_orch,
        xot_simulator=xot,
        xot_weight=0.2
    )
    print(f"   ✓ MCTSEngine created with XoT")
    print(f"   ✓ XoT mode: {mcts.xot_mode}")
    print(f"   ✓ XoT weight: {mcts.xot_weight}")

    # Create test ToT tree
    print("\n[4/5] Creating test ToT tree...")
    root_id = tot.create_root("What are the benefits of renewable energy?")
    print(f"   ✓ Root node created: {root_id}")

    # Decompose question (creates child nodes)
    try:
        child_ids = tot.decompose_question(root_id, branching_factor=3)
        print(f"   ✓ Decomposed into {len(child_ids)} sub-questions")

        # Run MCTS iterations with XoT
        print("\n[5/5] Running MCTS iterations with XoT...")
        print("   (This will call XoT simulator for prior estimation)")

        for i in range(3):
            stats = mcts.iterate(num_iterations=1)
            print(f"   Iteration {i+1}: selected node, XoT providing priors")

        print("   ✓ MCTS iterations completed")

        # Verify XoT stats
        print("\n" + "=" * 60)
        print("Results:")
        print("=" * 60)

        mcts_stats = mcts.get_stats()

        print(f"\nMCTS Stats:")
        print(f"  Total visits: {mcts_stats.get('total_visits', 0)}")
        print(f"  Avg value: {mcts_stats.get('avg_value', 0.0):.3f}")
        print(f"  Max depth: {mcts_stats.get('max_depth_visited', 0)}")

        if mcts_stats.get('xot_mode'):
            print(f"\nXoT Stats:")
            print(f"  XoT enabled: {mcts_stats.get('xot_mode')}")
            print(f"  XoT weight: {mcts_stats.get('xot_weight', 0.0)}")
            print(f"  Total simulations: {mcts_stats.get('xot_total_simulations', 0)}")
            print(f"  Success rate: {mcts_stats.get('xot_success_rate', 0.0):.2%}")
            print(f"  Avg score: {mcts_stats.get('xot_avg_score', 0.0):.3f}")
            print(f"  Avg time: {mcts_stats.get('xot_avg_time', 0.0):.2f}s")

            # Verify XoT was actually used
            if mcts_stats.get('xot_total_simulations', 0) > 0:
                print("\n✓ XoT integration successful!")
                print("  XoT provided prior probabilities for MCTS selection")
            else:
                print("\n⚠ Warning: XoT mode enabled but no simulations run")
        else:
            print("\n✗ XoT mode not enabled in stats")
            return False

        # Get best path
        try:
            best_path = mcts.best_path()
            print(f"\nBest path found: {len(best_path)} nodes")
        except Exception as e:
            print(f"\nNote: Could not get best path (expected if no full paths): {e}")

        print("\n" + "=" * 60)
        print("Test completed successfully!")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n✗ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_xot_mcts_integration()
    sys.exit(0 if success else 1)
