#!/usr/bin/env python3
"""
Test script for ProfileManager
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.profile_manager import ProfileManager


def main():
    print("="*60)
    print("  ProfileManager Test")
    print("="*60)

    # Initialize
    print("\n1. Initializing ProfileManager...")
    manager = ProfileManager(profiles_dir="config/profiles")
    print(f"   Loaded {len(manager.profiles)} profiles:")
    for profile_name in manager.profiles.keys():
        print(f"     - {profile_name}")

    # Get specific profile
    print("\n2. Getting 'standard' profile...")
    standard = manager.get_profile("standard")
    if standard:
        print(f"   Profile name: {standard.get('profile_name')}")
        print(f"   Max nodes: {standard.get('max_graph_nodes')}")
        print(f"   Max tokens: {standard.get('max_context_tokens')}")
        print(f"   Requirements: {standard.get('hardware_requirements')}")
        print(f"   Model preferences: {standard.get('model_preferences')}")
    else:
        print("   ERROR: Standard profile not found!")
        return

    # Validate hardware
    print("\n3. Validating hardware for 'standard'...")
    valid, msg = manager.validate_hardware("standard")
    if valid:
        print("   ✅ Hardware meets requirements")
    else:
        print(f"   ❌ Hardware insufficient: {msg}")

    # Recommend profile
    print("\n4. Getting recommended profile...")
    recommended = manager.recommend_profile()
    print(f"   Recommended: {recommended}")

    print("\n" + "="*60)
    print("  ✅ ProfileManager tests passed!")
    print("="*60)


if __name__ == "__main__":
    main()
