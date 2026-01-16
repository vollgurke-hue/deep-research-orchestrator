#!/usr/bin/env python3
"""
Manually create a test Unified Session via API v2

This script creates a session that should appear in the /unified Dashboard
"""
import requests
import json

API_BASE = "http://localhost:5000"

def create_test_session():
    """Create a test unified session."""
    print("🧪 Creating test session via API v2\n")

    # Step 1: Create Session
    print("Step 1: Creating session...")

    session_data = {
        "mode": "unified",
        "title": "E-Commerce Niche Analysis (TEST)",
        "goal": "Find profitable Micro-SaaS niches in the e-commerce space",
        "description": "Deep analysis of market gaps, competitor landscape, and monetization potential for AI-powered e-commerce tools.",
        "axioms": ["opportunity_cost", "risk_tolerance"]
    }

    response = requests.post(f"{API_BASE}/api/v2/sessions", json=session_data)

    if response.status_code not in [200, 201]:
        print(f"❌ Failed to create session: {response.status_code}")
        print(response.text)
        return None

    session = response.json()
    session_id = session.get("session_id")

    print(f"✅ Session created: {session_id}")
    print(f"   Title: {session_data['title']}")
    print(f"   Mode: {session_data['mode']}")
    print()

    # Step 2: Initialize Session (ToT, MCTS, Coverage)
    print("Step 2: Initializing session components...")

    init_response = requests.post(
        f"{API_BASE}/api/v2/sessions/{session_id}/initialize",
        json={
            "branching_factor": 3,
            "max_depth": 3
        }
    )

    if init_response.status_code != 200:
        print(f"⚠️ Failed to initialize: {init_response.status_code}")
        print(init_response.text)
    else:
        print("✅ Session initialized (ToT, MCTS, Coverage)")
        init_data = init_response.json()
        print(f"   Root Node: {init_data.get('root_node_id')}")
        print(f"   Components: {', '.join(init_data.get('components_initialized', []))}")
    print()

    # Step 3: Verify session exists
    print("Step 3: Verifying session...")

    get_response = requests.get(f"{API_BASE}/api/v2/sessions/{session_id}")

    if get_response.status_code == 200:
        session_full = get_response.json()
        print("✅ Session verified!")
        print(f"   Status: {session_full.get('status', 'unknown')}")

        # Check if data has the expected structure
        if 'metadata' in session_full:
            print(f"   Status: {session_full['metadata']['status']}")
            print(f"   ToT Nodes: {session_full.get('tot', {}).get('total_nodes', 0)}")
            print(f"   Responses: {len(session_full.get('responses', []))}")
        else:
            print(f"   Session data: {json.dumps(session_full, indent=2)}")
    print()

    # Step 4: Get coverage (optional - might fail if no data yet)
    print("Step 4: Checking coverage analysis...")

    try:
        coverage_response = requests.get(f"{API_BASE}/api/v2/sessions/{session_id}/coverage")

        if coverage_response.status_code == 200:
            coverage = coverage_response.json()
            print("✅ Coverage analysis available!")
            print(f"   Overall Coverage: {coverage.get('overall_coverage', 0):.1%}")
            print(f"   Total Nodes: {coverage.get('total_nodes', 0)}")
            print(f"   Gaps: {coverage.get('gaps_count', 0)}")
        else:
            print(f"⚠️ Coverage not available yet (status: {coverage_response.status_code})")
    except Exception as e:
        print(f"⚠️ Coverage check failed: {e}")
    print()

    # Summary
    print("=" * 60)
    print("🎉 TEST SESSION CREATED!")
    print("=" * 60)
    print()
    print("✅ Next Steps:")
    print(f"   1. Open: http://localhost:5173/unified")
    print(f"   2. Look for: '{session_data['title']}'")
    print(f"   3. Session ID: {session_id}")
    print()
    print("You should see:")
    print("   - Session in the left panel (Active Sessions)")
    print("   - Click it to see details in center panel")
    print("   - Coverage panel on the right")
    print()

    return session_id


if __name__ == "__main__":
    try:
        session_id = create_test_session()

        if session_id:
            print(f"✨ Success! Session ID: {session_id}")
            print()
            print("Now go to: http://localhost:5173/unified")
        else:
            print("❌ Session creation failed!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
