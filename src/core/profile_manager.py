"""
Profile Manager

Handles loading and validation of hardware resource profiles.
Profiles define memory limits, model preferences, and optimization strategies.
"""

import json
import psutil
import subprocess
from pathlib import Path
from typing import Optional, Dict


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
        """
        Load all profile configs from directory.

        Reads all *.json files and stores them by profile_name.
        """
        if not self.profiles_dir.exists():
            print(f"Warning: Profiles directory {self.profiles_dir} does not exist")
            return

        for json_file in self.profiles_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                profile_name = config.get("profile_name")
                if profile_name:
                    self.profiles[profile_name] = config
                    print(f"Loaded profile: {profile_name}")
                else:
                    print(f"Warning: Profile {json_file.name} has no profile_name field")

            except json.JSONDecodeError as e:
                print(f"Error parsing {json_file}: {e}")
            except Exception as e:
                print(f"Error loading {json_file}: {e}")

    def get_profile(self, name: str) -> Optional[Dict]:
        """
        Get profile configuration by name.

        Args:
            name: Profile name (e.g., "standard", "minimal", "ultra")

        Returns:
            Profile configuration dict or None if not found
        """
        return self.profiles.get(name)

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
        profile = self.get_profile(profile_name)
        if not profile:
            return False, f"Profile '{profile_name}' not found"

        requirements = profile.get("hardware_requirements", {})
        min_ram = requirements.get("min_ram_gb", 0)
        min_vram = requirements.get("min_vram_gb", 0)

        # Check RAM
        ram_gb = psutil.virtual_memory().total / (1024**3)
        if ram_gb < min_ram:
            return False, f"Insufficient RAM: {ram_gb:.1f}GB < {min_ram}GB required"

        # Check VRAM (if nvidia-smi available)
        if min_vram > 0:
            vram_gb = self._get_vram_gb()
            if vram_gb is not None and vram_gb < min_vram:
                return False, f"Insufficient VRAM: {vram_gb:.1f}GB < {min_vram}GB required"

        return True, None

    def _get_vram_gb(self) -> Optional[float]:
        """
        Get total VRAM in GB via nvidia-smi.

        Returns:
            VRAM in GB or None if unavailable
        """
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                first_line = lines[0] if lines else "0"
                vram_mb = float(first_line.strip())
                return vram_mb / 1024.0  # Convert MB to GB

        except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
            pass

        return None

    def recommend_profile(self) -> str:
        """
        Recommend best profile for current hardware.

        Algorithm:
        1. Detect RAM and VRAM
        2. Find profiles that fit hardware requirements
        3. Sort by capability (max_graph_nodes desc)
        4. Return best match

        Returns:
            Recommended profile name (defaults to "standard" if none fit)
        """
        # Get hardware specs
        ram_gb = psutil.virtual_memory().total / (1024**3)
        vram_gb = self._get_vram_gb()

        # Find profiles that fit
        fitting_profiles = []
        for profile_name, profile in self.profiles.items():
            requirements = profile.get("hardware_requirements", {})
            min_ram = requirements.get("min_ram_gb", 0)
            min_vram = requirements.get("min_vram_gb", 0)

            # Check if hardware meets requirements
            ram_ok = ram_gb >= min_ram
            vram_ok = vram_gb is None or vram_gb >= min_vram  # Skip VRAM check if unavailable

            if ram_ok and vram_ok:
                capability_score = profile.get("max_graph_nodes", 0)
                fitting_profiles.append((profile_name, capability_score))

        if not fitting_profiles:
            print(f"Warning: No profiles fit hardware (RAM: {ram_gb:.1f}GB, VRAM: {vram_gb}GB)")
            return "standard"  # Fallback

        # Sort by capability (higher is better)
        fitting_profiles.sort(key=lambda x: x[1], reverse=True)

        recommended = fitting_profiles[0][0]
        print(f"Recommended profile: {recommended} (max_nodes={fitting_profiles[0][1]})")
        return recommended


# TODO Sprint 1 Day 4: Add profile switching (graceful degradation)
# TODO Sprint 1 Day 4: Add VRAM monitoring + warnings
