"""
Profile Manager

Handles loading and validation of hardware resource profiles.
Profiles define memory limits, model preferences, and optimization strategies.
"""

import json
import psutil
from pathlib import Path
from typing import Optional


class ProfileManager:
    """
    Manages hardware resource profiles.

    Profiles define:
    - Memory limits (max_graph_nodes, max_context_tokens)
    - Model preferences (extraction: fast, reasoning: balanced)
    - Storage strategy (memory vs disk)
    - GUI settings (full_vue, pause_for_heavy_tasks)

    Example profile (config/profiles/standard.json):
    {
        "profile_name": "standard",
        "hardware_requirements": {"min_ram_gb": 16, "min_vram_gb": 11},
        "max_graph_nodes": 10000,
        "max_context_tokens": 8192,
        "model_preferences": {
            "extraction": "fast",
            "reasoning": "balanced"
        }
    }
    """

    def __init__(self, profiles_dir: str = "config/profiles"):
        """
        Initialize profile manager.

        Args:
            profiles_dir: Directory containing profile JSON files
        """
        self.profiles_dir = Path(profiles_dir)
        self.profiles = {}
        self._load_all_profiles()

    def _load_all_profiles(self):
        """Load all profile configs from directory"""
        # TODO Sprint 1 Day 3: Implement JSON loading
        # Read all *.json files from profiles_dir
        # Validate against config/schemas/profile_schema.json
        # Store in self.profiles dict
        pass

    def get_profile(self, name: str) -> dict:
        """
        Get profile configuration by name.

        Args:
            name: Profile name (e.g., "standard", "minimal", "ultra")

        Returns:
            Profile configuration dict

        Raises:
            KeyError: If profile not found
        """
        # TODO Sprint 1 Day 3: Implement profile lookup
        return self.profiles.get(name, {})

    def validate_hardware(self, profile_name: str) -> tuple[bool, Optional[str]]:
        """
        Check if current hardware meets profile requirements.

        Args:
            profile_name: Profile to validate

        Returns:
            (is_valid, error_message)

        Example:
            valid, msg = manager.validate_hardware("standard")
            if not valid:
                print(f"Hardware insufficient: {msg}")
        """
        # TODO Sprint 1 Day 3: Implement hardware check
        # Use psutil to get RAM
        # Use nvidia-smi or similar for VRAM
        # Compare against profile.hardware_requirements

        profile = self.get_profile(profile_name)
        if not profile:
            return False, f"Profile '{profile_name}' not found"

        # Placeholder: check RAM only
        ram_gb = psutil.virtual_memory().total / (1024**3)
        min_ram = profile.get("hardware_requirements", {}).get("min_ram_gb", 0)

        if ram_gb < min_ram:
            return False, f"Insufficient RAM: {ram_gb:.1f}GB < {min_ram}GB required"

        return True, None

    def recommend_profile(self) -> str:
        """
        Recommend best profile for current hardware.

        Algorithm:
        1. Detect RAM and VRAM
        2. Find profiles that fit (sorted by capability desc)
        3. Return best match

        Returns:
            Recommended profile name
        """
        # TODO Sprint 1 Day 3: Implement auto-detection
        # Detect hardware specs
        # Sort profiles by max_graph_nodes (descending)
        # Return first that fits
        return "standard"


# TODO Sprint 1 Day 4: Add profile switching (graceful degradation)
# TODO Sprint 1 Day 4: Add VRAM monitoring + warnings
