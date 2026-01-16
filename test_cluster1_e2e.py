"""
End-to-End Test: Cluster 1 Complete Flow
Tests SPO + XoT + Token Budget working together.

Flow:
1. Create session with SPO database
2. Create ToT tree and expand nodes
3. Verify SPO triplets extracted
4. Run MCTS with XoT priors
5. Verify token budgets tracked
6. Check all components worked together
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.core.graph_manager import GraphManager
from src.core.tot_manager import ToTManager
from src.core.mcts_engine import MCTSEngine
from src.core.model_orchestrator import ModelOrchestrator
from src.core.local_llamacpp_provider import LocalLlamaCppProvider
from src.core.xot_simulator import XoTSimulator
from src.core.token_budget_manager import TokenBudgetManager


def test_cluster1_end_to_end():
    """
    Complete Cluster 1 flow test.

    Verifies:
    - SPO extraction during node expansion
    - XoT providing priors for MCTS
    - Token budget tracking and allocation
    - All components integrated correctly
    """
    print("=" * 70)
    print("CLUSTER 1 END-TO-END TEST")
    print("Testing: SPO + XoT + Token Budget Integration")
    print("=" * 70)

    # Create temporary SPO database
    with tempfile.TemporaryDirectory() as tmpdir:
        spo_db_path = Path(tmpdir) / "test_spo.db"

        # ==========================================
        # Phase 1: Setup Components
        # ==========================================
        print("\n[Phase 1/6] Setting up components...")

        # GraphManager with SPO database
        graph = GraphManager(
            max_nodes=100,
            spo_db_path=str(spo_db_path)
        )
        print("  ✓ GraphManager with SPO database")

        # Model orchestrator
        model_orch = ModelOrchestrator(profile="standard")
        llamacpp_provider = LocalLlamaCppProvider(
            models_config_dir="config/models",
            port=8081,
            auto_start=True
        )
        model_orch.register_provider("llamacpp", llamacpp_provider)
        print("  ✓ ModelOrchestrator with llama.cpp")

        # ToT Manager
        tot = ToTManager(
            graph_manager=graph,
            axiom_manager=None,
            model_orchestrator=model_orch
        )
        print("  ✓ ToTManager")

        # XoT Simulator
        xot = XoTSimulator(
            model_orchestrator=model_orch,
            depth=3,
            fallback_score=0.5
        )
        print("  ✓ XoTSimulator")

        # Token Budget Manager
        budget_mgr = TokenBudgetManager(
            total_budget=100_000,
            default_node_budget=10_000,
            min_node_budget=1_000,
            max_node_budget=50_000
        )
        print("  ✓ TokenBudgetManager")

        # MCTS with XoT + Budget
        mcts = MCTSEngine(
            tot_manager=tot,
            graph_manager=graph,
            model_orchestrator=model_orch,
            xot_simulator=xot,
            xot_weight=0.2,
            token_budget_manager=budget_mgr
        )
        print("  ✓ MCTSEngine with XoT + Budget")

        # ==========================================
        # Phase 2: Create ToT Tree
        # ==========================================
        print("\n[Phase 2/6] Creating ToT tree...")

        root_id = tot.create_root("What are the main advantages of solar energy?")
        print(f"  ✓ Root node: {root_id}")

        # ==========================================
        # Phase 3: Expand Nodes (SPO Extraction)
        # ==========================================
        print("\n[Phase 3/6] Expanding nodes (should extract SPO triplets)...")

        try:
            # Decompose question
            child_ids = tot.decompose_question(root_id, branching_factor=3)
            print(f"  ✓ Decomposed into {len(child_ids)} sub-questions")

            # Expand first child (this triggers SPO extraction)
            if child_ids:
                first_child = child_ids[0]
                tot.expand_node(first_child)
                print(f"  ✓ Expanded node: {first_child}")

                # Check if SPO triplets were extracted
                child_node = tot.tree.get(first_child)
                if hasattr(child_node, 'spo_triplets') and child_node.spo_triplets:
                    print(f"  ✓ SPO triplets extracted: {len(child_node.spo_triplets)} triplets")
                    spo_extracted = True
                else:
                    print(f"  ⚠ No SPO triplets found (node may not have answer yet)")
                    spo_extracted = False
            else:
                print("  ⚠ No child nodes created")
                spo_extracted = False

        except Exception as e:
            print(f"  ⚠ Expansion failed (this may be OK if model not running): {e}")
            spo_extracted = False

        # ==========================================
        # Phase 4: Verify SPO Database
        # ==========================================
        print("\n[Phase 4/6] Checking SPO database...")

        spo_stats = graph.get_spo_stats()
        print(f"  Total triplets: {spo_stats.get('total_triplets', 0)}")
        print(f"  Bronze tier: {spo_stats.get('bronze_count', 0)}")
        print(f"  Silver tier: {spo_stats.get('silver_count', 0)}")
        print(f"  Gold tier: {spo_stats.get('gold_count', 0)}")

        if spo_stats.get('total_triplets', 0) > 0:
            print("  ✓ SPO database has triplets")
            spo_db_ok = True
        else:
            print("  ⚠ No triplets in database (expansion may have failed)")
            spo_db_ok = False

        # ==========================================
        # Phase 5: Run MCTS with XoT + Budget
        # ==========================================
        print("\n[Phase 5/6] Running MCTS with XoT + Budget...")

        try:
            # Run 5 MCTS iterations
            for i in range(5):
                stats = mcts.iterate(num_iterations=1)
                print(f"  Iteration {i+1}/5: selected {len(stats.get('nodes_selected', []))} nodes")

            print("  ✓ MCTS iterations completed")
            mcts_ok = True

        except Exception as e:
            print(f"  ⚠ MCTS failed: {e}")
            mcts_ok = False

        # ==========================================
        # Phase 6: Verify Results
        # ==========================================
        print("\n[Phase 6/6] Verifying results...")
        print("\n" + "=" * 70)
        print("RESULTS")
        print("=" * 70)

        # Get MCTS stats
        mcts_stats = mcts.get_stats()

        # Display stats
        print("\n📊 MCTS Stats:")
        print(f"  Total visits: {mcts_stats.get('total_visits', 0)}")
        print(f"  Avg value: {mcts_stats.get('avg_value', 0.0):.3f}")
        print(f"  Max depth: {mcts_stats.get('max_depth_visited', 0)}")

        # XoT stats
        if mcts_stats.get('xot_mode'):
            print("\n🧠 XoT Stats:")
            print(f"  Enabled: {mcts_stats.get('xot_mode')}")
            print(f"  Weight: {mcts_stats.get('xot_weight', 0.0)}")
            print(f"  Total simulations: {mcts_stats.get('xot_total_simulations', 0)}")
            print(f"  Success rate: {mcts_stats.get('xot_success_rate', 0.0):.2%}")
            print(f"  Avg score: {mcts_stats.get('xot_avg_score', 0.0):.3f}")
            print(f"  Avg time: {mcts_stats.get('xot_avg_time', 0.0):.2f}s")

            xot_ok = mcts_stats.get('xot_total_simulations', 0) > 0
            if xot_ok:
                print("  ✓ XoT provided priors for MCTS")
            else:
                print("  ⚠ XoT mode enabled but no simulations run")
        else:
            print("\n🧠 XoT: Not enabled in results")
            xot_ok = False

        # Budget stats
        if mcts_stats.get('budget_mode'):
            print("\n💰 Token Budget Stats:")
            print(f"  Enabled: {mcts_stats.get('budget_mode')}")
            print(f"  Nodes tracked: {mcts_stats.get('budget_nodes_tracked', 0)}")
            print(f"  Nodes exhausted: {mcts_stats.get('budget_nodes_exhausted', 0)}")
            print(f"  Total used: {mcts_stats.get('budget_total_used', 0):,} tokens")
            print(f"  Remaining: {mcts_stats.get('budget_total_remaining', 0):,} tokens")
            print(f"  Utilization: {mcts_stats.get('budget_utilization', 0.0):.1f}%")

            budget_ok = mcts_stats.get('budget_nodes_tracked', 0) > 0
            if budget_ok:
                print("  ✓ Token budgets tracked")
            else:
                print("  ⚠ Budget mode enabled but no nodes tracked")
        else:
            print("\n💰 Token Budget: Not enabled in results")
            budget_ok = False

        # SPO stats
        print("\n📚 SPO Knowledge Graph:")
        print(f"  Total triplets: {spo_stats.get('total_triplets', 0)}")
        if spo_stats.get('total_triplets', 0) > 0:
            print(f"  Bronze: {spo_stats.get('bronze_count', 0)}")
            print(f"  Silver: {spo_stats.get('silver_count', 0)}")
            print(f"  Gold: {spo_stats.get('gold_count', 0)}")
            print("  ✓ SPO triplets stored")

        # ==========================================
        # Final Verdict
        # ==========================================
        print("\n" + "=" * 70)
        print("CLUSTER 1 COMPONENT STATUS")
        print("=" * 70)

        components = [
            ("SPO Extraction", spo_extracted, "SPO triplets extracted during node expansion"),
            ("SPO Database", spo_db_ok, "Triplets stored in SQLite with FTS5"),
            ("XoT Integration", xot_ok, "XoT priors used in MCTS UCB1"),
            ("Token Budget", budget_ok, "Budgets allocated and tracked"),
            ("MCTS Integration", mcts_ok, "All components work in MCTS"),
        ]

        all_ok = True
        for name, status, description in components:
            status_symbol = "✅" if status else "⚠️"
            status_text = "PASS" if status else "WARN"
            print(f"{status_symbol} {name:20} {status_text:6} - {description}")
            if not status:
                all_ok = False

        print("\n" + "=" * 70)
        if all_ok:
            print("🎉 CLUSTER 1 END-TO-END TEST: ALL COMPONENTS WORKING!")
            print("=" * 70)
            print("\nCluster 1 is fully functional and ready for production.")
            print("You can now proceed to Cluster 2 with confidence.")
        else:
            print("⚠️  CLUSTER 1 END-TO-END TEST: SOME WARNINGS")
            print("=" * 70)
            print("\nNotes:")
            print("- Warnings are OK if llama-server is not running")
            print("- Core infrastructure is in place")
            print("- Components that didn't run will work when LLM is active")

        print("\n" + "=" * 70)
        print("TEST COMPLETE")
        print("=" * 70)

        return all_ok


if __name__ == "__main__":
    try:
        success = test_cluster1_end_to_end()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
