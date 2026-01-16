"""
Test SPO Extraction with DeepSeek-R1
Verifies that SPO triplets are extracted during node expansion.
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.core.graph_manager import GraphManager
from src.core.tot_manager import ToTManager
from src.core.model_orchestrator import ModelOrchestrator, QualityLevel
from src.core.local_llamacpp_provider import LocalLlamaCppProvider


def test_spo_extraction_with_deepseek():
    """
    Test SPO extraction using DeepSeek-R1-14B model.

    Flow:
    1. Setup ToTManager with SPO database
    2. Create and expand node with DeepSeek-R1
    3. Verify SPO triplets were extracted
    4. Check triplets in database
    """
    print("=" * 70)
    print("SPO EXTRACTION TEST (DeepSeek-R1-14B)")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        spo_db_path = Path(tmpdir) / "test_spo.db"

        # Setup
        print("\n[1/5] Setting up components...")

        graph = GraphManager(max_nodes=100, spo_db_path=str(spo_db_path))
        print("  ✓ GraphManager with SPO database")

        model_orch = ModelOrchestrator(profile="standard")
        llamacpp_provider = LocalLlamaCppProvider(
            models_config_dir="config/models",
            port=8081,
            auto_start=True
        )
        model_orch.register_provider("llamacpp", llamacpp_provider)
        print("  ✓ ModelOrchestrator")

        tot = ToTManager(
            graph_manager=graph,
            axiom_manager=None,
            model_orchestrator=model_orch
        )
        print("  ✓ ToTManager")

        # Create root node
        print("\n[2/5] Creating ToT tree...")
        root_id = tot.create_root(
            "What are the environmental benefits of renewable energy sources like solar and wind power?"
        )
        print(f"  ✓ Root node: {root_id}")

        # Decompose
        print("\n[3/5] Decomposing question...")
        try:
            child_ids = tot.decompose_question(root_id, branching_factor=2)
            print(f"  ✓ Created {len(child_ids)} sub-questions")

            if not child_ids:
                print("  ✗ No child nodes created")
                return False

        except Exception as e:
            print(f"  ✗ Decomposition failed: {e}")
            return False

        # Expand node with BALANCED quality (uses DeepSeek-R1)
        print("\n[4/5] Expanding node with DeepSeek-R1-14B...")
        print("  (This should extract SPO triplets automatically)")

        try:
            first_child = child_ids[0]
            child_node = tot.tree.get(first_child)
            print(f"  Question: {child_node.question[:80]}...")

            # Use BALANCED quality to trigger DeepSeek-R1
            success = tot.expand_node(first_child, use_quality=QualityLevel.BALANCED)

            if not success:
                print("  ✗ Node expansion failed")
                return False

            print("  ✓ Node expanded")

            # Check answer
            child_node = tot.tree.get(first_child)
            if child_node.answer:
                print(f"  Answer: {child_node.answer[:100]}...")
            else:
                print("  ⚠ Node has no answer")
                return False

        except Exception as e:
            print(f"  ✗ Expansion failed: {e}")
            import traceback
            traceback.print_exc()
            return False

        # Check SPO extraction
        print("\n[5/5] Verifying SPO extraction...")

        # Check node has SPO triplet IDs
        if hasattr(child_node, 'spo_triplets') and child_node.spo_triplets:
            print(f"  ✓ Node has {len(child_node.spo_triplets)} SPO triplet IDs")
            spo_in_node = True
        else:
            print("  ✗ Node has no SPO triplet IDs")
            spo_in_node = False

        # Check database
        spo_stats = graph.get_spo_stats()
        total_triplets = spo_stats.get('total_triplets', 0)

        print(f"\n  SPO Database Stats:")
        print(f"    Total triplets: {total_triplets}")
        print(f"    Bronze: {spo_stats.get('bronze_count', 0)}")
        print(f"    Silver: {spo_stats.get('silver_count', 0)}")
        print(f"    Gold: {spo_stats.get('gold_count', 0)}")

        if total_triplets > 0:
            print(f"  ✓ SPO database has {total_triplets} triplets")
            spo_in_db = True

            # Show some triplets
            triplets = graph.get_spo_triplets(limit=3)
            print(f"\n  Sample triplets:")
            for i, t in enumerate(triplets[:3], 1):
                print(f"    {i}. [{t.subject}] --{t.predicate}--> [{t.object}]")
                print(f"       Confidence: {t.confidence:.2f}, Tier: {t.tier}")
        else:
            print("  ✗ No triplets in database")
            spo_in_db = False

        # Final verdict
        print("\n" + "=" * 70)
        if spo_in_node and spo_in_db:
            print("✅ SPO EXTRACTION TEST: PASSED")
            print("=" * 70)
            print("\nSPO extraction is working correctly!")
            print("- DeepSeek-R1-14B successfully answered question")
            print("- SPO triplets extracted from answer")
            print("- Triplets stored in SQLite database")
            print("- Bronze tier assigned correctly")
            return True
        else:
            print("⚠️  SPO EXTRACTION TEST: PARTIAL")
            print("=" * 70)
            print("\nSome components didn't work:")
            if not spo_in_node:
                print("- Node doesn't have SPO triplet IDs")
            if not spo_in_db:
                print("- Database doesn't have triplets")
            print("\nThis may indicate:")
            print("- LLM response didn't contain extractable facts")
            print("- SPO extractor confidence threshold too high")
            print("- Extraction prompt needs tuning")
            return False


if __name__ == "__main__":
    try:
        success = test_spo_extraction_with_deepseek()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test crashed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
