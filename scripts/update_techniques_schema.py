#!/usr/bin/env python3
"""
Update all technique JSON files with the new schema pattern:
- Add type, category, agent_role
- Add working_state structure
- Add output structure
- Add exit_criteria
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
TECHNIQUES_DIR = PROJECT_ROOT / "config" / "techniques"

# Category mapping based on technique purpose
CATEGORY_MAP = {
    "contradiction": "quality_assurance",
    "blind_spots": "quality_assurance",
    "sanity_check": "quality_assurance",
    "market_research": "market_opportunity",
    "user_needs": "market_opportunity",
    "competition": "competition",
    "tech_feasibility": "technical_feasibility",
    "synthesis": "strategic_planning",
}

# Agent role mapping
ROLE_MAP = {
    "contradiction": "quality_validator",
    "blind_spots": "critical_analyst",
    "sanity_check": "reality_checker",
    "market_research": "market_researcher",
    "user_needs": "user_researcher",
    "competition": "competitive_analyst",
    "tech_feasibility": "technical_analyst",
    "synthesis": "strategic_synthesizer",
}

def update_technique_file(technique_path: Path):
    """Update a single technique file with new schema."""
    print(f"Updating: {technique_path.name}")

    with open(technique_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    technique_id = data.get("technique_id", technique_path.stem)

    # Add type if missing
    if "type" not in data:
        data["type"] = "technique"

    # Add category if missing
    if "category" not in data:
        data["category"] = CATEGORY_MAP.get(technique_id, "general")

    # Add agent_role if missing
    if "agent_role" not in data:
        data["agent_role"] = ROLE_MAP.get(technique_id, "general_analyst")

    # Add working_state if missing
    if "working_state" not in data:
        data["working_state"] = {
            "status": "pending",
            "progress": 0,
            "current_step": "",
            "started_at": None,
            "updated_at": None
        }

    # Add output if missing
    if "output" not in data:
        data["output"] = {
            "format": "markdown",
            "content": "",
            "metadata": {
                "confidence_score": 0.0,
                "model_used": "",
                "token_count": 0,
                "execution_time_ms": 0
            }
        }

    # Add exit_criteria if missing
    if "exit_criteria" not in data:
        data["exit_criteria"] = {
            "type": "completion",
            "threshold": None,
            "required_outputs": ["content"]
        }

    # Reorder keys for consistency
    ordered_data = {
        "technique_id": data["technique_id"],
        "type": data["type"],
        "name": data["name"],
        "description": data["description"],
        "category": data["category"],
        "prompt": data["prompt"],
    }

    # Add optional fields
    for key in ["placeholders", "recommended_model", "temperature", "max_tokens", "agent_role"]:
        if key in data:
            ordered_data[key] = data[key]

    # Add arrays
    for key in ["use_cases", "tags"]:
        if key in data:
            ordered_data[key] = data[key]

    # Add structures
    ordered_data["working_state"] = data["working_state"]
    ordered_data["output"] = data["output"]
    ordered_data["exit_criteria"] = data["exit_criteria"]

    # Write back
    with open(technique_path, 'w', encoding='utf-8') as f:
        json.dump(ordered_data, f, indent=2, ensure_ascii=False)

    print(f"  ✓ Added: type, category, working_state, output, exit_criteria")

def main():
    """Update all technique files."""
    print("🔄 Updating Technique JSON Schemas\n")

    technique_files = list(TECHNIQUES_DIR.glob("*.json"))

    if not technique_files:
        print(f"❌ No technique files found in {TECHNIQUES_DIR}")
        return

    print(f"Found {len(technique_files)} technique files\n")

    for technique_file in technique_files:
        try:
            update_technique_file(technique_file)
        except Exception as e:
            print(f"  ❌ Error: {e}")

    print(f"\n✅ Updated {len(technique_files)} technique files")
    print("\nNew schema includes:")
    print("  - type: 'technique'")
    print("  - category: (market_opportunity, technical_feasibility, etc.)")
    print("  - working_state: { status, progress, current_step, timestamps }")
    print("  - output: { format, content, metadata }")
    print("  - exit_criteria: { type, threshold, required_outputs }")

if __name__ == "__main__":
    main()
