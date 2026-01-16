#!/usr/bin/env python3
"""
Update all workflow JSON files with the new building block pattern:
- Add type, category
- Convert steps to building_blocks
- Add working_state, output, exit_criteria
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
WORKFLOWS_DIR = PROJECT_ROOT / "config" / "workflows" / "sequential"

def update_workflow_file(workflow_path: Path):
    """Update a single workflow file with new schema."""
    print(f"Updating: {workflow_path.name}")

    with open(workflow_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Add type if missing
    if "type" not in data:
        data["type"] = "workflow"

    # Add category if missing (infer from workflow type)
    if "category" not in data:
        if "validation" in data.get("mode", "").lower() or "validation" in data.get("name", "").lower():
            data["category"] = "quality_assurance"
        elif "synthesis" in data.get("name", "").lower():
            data["category"] = "strategic_planning"
        else:
            data["category"] = "general"

    # Convert steps to building_blocks if needed
    if "steps" in data and "building_blocks" not in data:
        building_blocks = []
        for step in data["steps"]:
            building_blocks.append({
                "block_type": "technique",
                "block_id": step["technique"],
                "order": step["step"]
            })
        data["building_blocks"] = building_blocks

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
            "format": "structured",
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
            "type": "all_complete",
            "threshold": None,
            "required_outputs": [block["block_id"] for block in data.get("building_blocks", [])]
        }

    # Reorder keys for consistency
    ordered_data = {
        "workflow_id": data["workflow_id"],
        "type": data["type"],
        "name": data["name"],
        "description": data["description"],
        "category": data["category"],
        "mode": data.get("mode", "sequential"),
    }

    # Add building_blocks
    if "building_blocks" in data:
        ordered_data["building_blocks"] = data["building_blocks"]

    # Keep legacy steps for backward compatibility
    if "steps" in data:
        ordered_data["steps"] = data["steps"]

    # Add optional fields
    for key in ["reasoning_strategy", "recommended_model", "output_aggregation", "temperature"]:
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
    with open(workflow_path, 'w', encoding='utf-8') as f:
        json.dump(ordered_data, f, indent=2, ensure_ascii=False)

    print(f"  ✓ Added: type, category, building_blocks, working_state, output, exit_criteria")

def main():
    """Update all workflow files."""
    print("🔄 Updating Workflow JSON Schemas\n")

    workflow_files = list(WORKFLOWS_DIR.glob("*.json"))

    if not workflow_files:
        print(f"❌ No workflow files found in {WORKFLOWS_DIR}")
        return

    print(f"Found {len(workflow_files)} workflow files\n")

    for workflow_file in workflow_files:
        try:
            update_workflow_file(workflow_file)
        except Exception as e:
            print(f"  ❌ Error: {e}")

    print(f"\n✅ Updated {len(workflow_files)} workflow files")

if __name__ == "__main__":
    main()
