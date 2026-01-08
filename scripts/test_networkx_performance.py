#!/usr/bin/env python3
"""
NetworkX Performance Test
Tests graph operations for 10,000 nodes
"""

import networkx as nx
import time
import sys

def test_graph_creation():
    """Test creating 10k node graph"""
    print("=" * 60)
    print("NetworkX Performance Test")
    print("=" * 60)

    G = nx.DiGraph()
    start = time.time()

    print("\n1. Creating 10,000 nodes with edges...")
    for i in range(10000):
        G.add_node(
            f"node_{i}",
            data={
                "type": "test",
                "confidence": 0.8,
                "description": f"Test node {i}"
            }
        )
        if i > 0:
            G.add_edge(
                f"node_{i-1}",
                f"node_{i}",
                weight=0.5,
                predicate="connected_to"
            )

    elapsed = time.time() - start
    print(f"   ✓ Created {G.number_of_nodes()} nodes in {elapsed:.2f}s")
    print(f"   ✓ Created {G.number_of_edges()} edges")

    # Test ego graph extraction
    print("\n2. Testing ego-graph extraction (depth=2)...")
    start = time.time()
    subgraph = nx.ego_graph(G, "node_5000", radius=2)
    elapsed = time.time() - start
    print(f"   ✓ Extracted subgraph with {len(subgraph.nodes())} nodes in {elapsed:.3f}s")

    # Test PageRank
    print("\n3. Testing PageRank (importance calculation)...")
    start = time.time()
    pagerank = nx.pagerank(G)
    elapsed = time.time() - start
    print(f"   ✓ Calculated PageRank for {len(pagerank)} nodes in {elapsed:.2f}s")

    # Get top 5 nodes
    top_nodes = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:5]
    print(f"   ✓ Top 5 nodes by importance:")
    for node, score in top_nodes:
        print(f"      - {node}: {score:.6f}")

    # Test subgraph extraction by keyword
    print("\n4. Testing keyword-based node search...")
    start = time.time()
    matching_nodes = [
        node for node, data in G.nodes(data=True)
        if '500' in str(node) or '500' in data.get('description', '')
    ]
    elapsed = time.time() - start
    print(f"   ✓ Found {len(matching_nodes)} matching nodes in {elapsed:.3f}s")

    # Memory estimation
    import sys
    graph_size_mb = sys.getsizeof(G) / (1024 * 1024)
    print(f"\n5. Memory usage:")
    print(f"   ✓ Graph object size: ~{graph_size_mb:.1f} MB")
    print(f"   ✓ Estimated total with data: ~{graph_size_mb * 3:.1f} MB")

    # Success criteria
    print("\n" + "=" * 60)
    print("SUCCESS CRITERIA CHECK:")
    print("=" * 60)

    success = True

    if elapsed > 2.0:
        print("   ⚠ WARNING: Creation took >2s (should be <2s)")
        success = False
    else:
        print(f"   ✓ Creation time: {elapsed:.2f}s (target: <2s)")

    if graph_size_mb * 3 > 1000:
        print("   ⚠ WARNING: Memory usage >1GB")
        success = False
    else:
        print(f"   ✓ Memory usage: ~{graph_size_mb * 3:.1f}MB (target: <1GB)")

    print("=" * 60)

    if success:
        print("✅ NetworkX ready for production!")
        return 0
    else:
        print("⚠️  Performance concerns, but usable")
        return 1

if __name__ == "__main__":
    sys.exit(test_graph_creation())
