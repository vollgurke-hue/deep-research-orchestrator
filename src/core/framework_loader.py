"""
Framework Loader for Logic Builder.

Loads and validates hierarchical research frameworks:
- Frameworks (chains of phases)
- Phases (collections of workflows)
- Workflows (sequences of techniques)
- Techniques (atomic validation/research tasks)
"""
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import json

from src.utils.json_loader import JSONLoader
from src.utils.logger import setup_logger


@dataclass
class BuildingBlock:
    """Base class for composable logic blocks."""

    block_id: str
    name: str
    block_type: str
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Technique(BuildingBlock):
    """Atomic validation/research technique."""

    prompt: str = ""
    agent_role: str = "researcher"
    temperature: float = 0.7
    max_tokens: int = 2048

    def __post_init__(self):
        self.block_type = "technique"


@dataclass
class Workflow(BuildingBlock):
    """Sequence of techniques."""

    mode: str = "sequential"  # sequential | iterative
    steps: List[Dict[str, Any]] = field(default_factory=list)
    building_blocks: List[Dict[str, Any]] = field(default_factory=list)
    exit_criteria: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.block_type = "workflow"


@dataclass
class Phase(BuildingBlock):
    """Collection of workflows addressing specific research areas."""

    building_blocks: List[Dict[str, Any]] = field(default_factory=list)
    exit_criteria: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.block_type = "phase"

    def count_blocks(self) -> int:
        """Count total building blocks in this phase."""
        return len(self.building_blocks)


@dataclass
class Framework(BuildingBlock):
    """Complete research framework (chain of phases)."""

    building_blocks: List[Dict[str, Any]] = field(default_factory=list)
    global_exit_criteria: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.block_type = "framework"

    def count_blocks(self) -> int:
        """Count total building blocks (phases) in this framework."""
        return len(self.building_blocks)

    def count_total_steps(self) -> int:
        """Count total workflow steps across all phases."""
        # This would require loading all nested blocks
        # For now, return phase count
        return self.count_blocks()


class FrameworkLoader:
    """
    Loader for hierarchical research frameworks.

    Supports loading:
    - Individual techniques
    - Workflows (composed of techniques)
    - Phases (composed of workflows)
    - Frameworks (composed of phases)
    """

    def __init__(self, config_dir: Path = Path("config")):
        """
        Initialize framework loader.

        Args:
            config_dir: Root config directory
        """
        self.config_dir = config_dir
        self.logger = setup_logger("framework_loader")

        # Cache loaded blocks
        self._techniques_cache: Dict[str, Technique] = {}
        self._workflows_cache: Dict[str, Workflow] = {}
        self._phases_cache: Dict[str, Phase] = {}
        self._frameworks_cache: Dict[str, Framework] = {}

    def load_technique(self, technique_id: str) -> Technique:
        """
        Load a technique definition.

        Args:
            technique_id: Technique ID (e.g., "contradiction")

        Returns:
            Technique object
        """
        if technique_id in self._techniques_cache:
            return self._techniques_cache[technique_id]

        technique_path = self.config_dir / "techniques" / f"{technique_id}.json"

        if not technique_path.exists():
            raise FileNotFoundError(f"Technique not found: {technique_path}")

        config = JSONLoader.load(technique_path)

        technique = Technique(
            block_id=config["technique_id"],
            name=config.get("name", config["technique_id"]),
            block_type="technique",
            description=config.get("description"),
            prompt=config.get("prompt", ""),
            agent_role=config.get("agent_role", "researcher"),
            temperature=config.get("temperature", 0.7),
            max_tokens=config.get("max_tokens", 2048),
            metadata=config.get("metadata", {})
        )

        self._techniques_cache[technique_id] = technique
        return technique

    def load_workflow(self, workflow_id: str) -> Workflow:
        """
        Load a workflow definition.

        Args:
            workflow_id: Workflow ID (e.g., "research_validation")

        Returns:
            Workflow object
        """
        if workflow_id in self._workflows_cache:
            return self._workflows_cache[workflow_id]

        # Check sequential workflows
        workflow_path = self.config_dir / "workflows" / "sequential" / f"{workflow_id}.json"

        if not workflow_path.exists():
            # Check iterative workflows
            workflow_path = self.config_dir / "workflows" / "iterative" / f"{workflow_id}.json"

        if not workflow_path.exists():
            raise FileNotFoundError(f"Workflow not found: {workflow_id}")

        config = JSONLoader.load(workflow_path)

        workflow = Workflow(
            block_id=config["workflow_id"],
            name=config.get("name", config["workflow_id"]),
            block_type="workflow",
            description=config.get("description"),
            mode=config.get("mode", "sequential"),
            steps=config.get("steps", []),
            building_blocks=config.get("building_blocks", []),
            exit_criteria=config.get("exit_criteria", {}),
            metadata=config.get("metadata", {})
        )

        self._workflows_cache[workflow_id] = workflow
        return workflow

    def load_phase(self, phase_id: str) -> Phase:
        """
        Load a phase definition.

        Args:
            phase_id: Phase ID (e.g., "phase_0_base_research")

        Returns:
            Phase object
        """
        if phase_id in self._phases_cache:
            return self._phases_cache[phase_id]

        phase_path = self.config_dir / "phases" / f"{phase_id}.json"

        if not phase_path.exists():
            raise FileNotFoundError(f"Phase not found: {phase_path}")

        config = JSONLoader.load(phase_path)

        phase = Phase(
            block_id=config["phase_id"],
            name=config.get("name", config["phase_id"]),
            block_type="phase",
            description=config.get("description"),
            building_blocks=config.get("building_blocks", []),
            exit_criteria=config.get("exit_criteria", {}),
            metadata=config.get("metadata", {})
        )

        self._phases_cache[phase_id] = phase
        return phase

    def load_framework(self, framework_id: str) -> Framework:
        """
        Load a complete framework definition.

        Args:
            framework_id: Framework ID (e.g., "framework_product_research")

        Returns:
            Framework object
        """
        if framework_id in self._frameworks_cache:
            return self._frameworks_cache[framework_id]

        framework_path = self.config_dir / "frameworks" / f"{framework_id}.json"

        if not framework_path.exists():
            raise FileNotFoundError(f"Framework not found: {framework_path}")

        config = JSONLoader.load(framework_path)

        framework = Framework(
            block_id=config["framework_id"],
            name=config.get("name", config["framework_id"]),
            block_type="framework",
            description=config.get("description"),
            building_blocks=config.get("building_blocks", []),
            global_exit_criteria=config.get("global_exit_criteria", {}),
            metadata=config.get("metadata", {})
        )

        self._frameworks_cache[framework_id] = framework
        return framework

    def load(self, block_id: str, block_type: Optional[str] = None) -> BuildingBlock:
        """
        Load any type of building block.

        Auto-detects type if not specified.

        Args:
            block_id: ID of the block
            block_type: Optional type hint (technique/workflow/phase/framework)

        Returns:
            Loaded building block
        """
        if block_type == "technique":
            return self.load_technique(block_id)
        elif block_type == "workflow":
            return self.load_workflow(block_id)
        elif block_type == "phase":
            return self.load_phase(block_id)
        elif block_type == "framework":
            return self.load_framework(block_id)
        else:
            # Auto-detect
            if block_id.startswith("technique_") or not ("_" in block_id or block_id.startswith("phase") or block_id.startswith("framework")):
                try:
                    return self.load_technique(block_id)
                except FileNotFoundError:
                    pass

            if block_id.startswith("phase_"):
                try:
                    return self.load_phase(block_id)
                except FileNotFoundError:
                    pass

            if block_id.startswith("framework_"):
                try:
                    return self.load_framework(block_id)
                except FileNotFoundError:
                    pass

            # Try workflow last
            try:
                return self.load_workflow(block_id)
            except FileNotFoundError:
                raise ValueError(f"Could not find block: {block_id}")

    def list_techniques(self) -> List[Dict[str, str]]:
        """List all available techniques."""
        techniques_dir = self.config_dir / "techniques"
        if not techniques_dir.exists():
            return []

        return [
            {
                "technique_id": f.stem,
                "path": str(f)
            }
            for f in techniques_dir.glob("*.json")
        ]

    def list_workflows(self) -> List[Dict[str, str]]:
        """List all available workflows."""
        workflows = []

        for subdir in ["sequential", "iterative"]:
            workflows_dir = self.config_dir / "workflows" / subdir
            if workflows_dir.exists():
                workflows.extend([
                    {
                        "workflow_id": f.stem,
                        "mode": subdir,
                        "path": str(f)
                    }
                    for f in workflows_dir.glob("*.json")
                ])

        return workflows

    def list_phases(self) -> List[Dict[str, str]]:
        """List all available phases."""
        phases_dir = self.config_dir / "phases"
        if not phases_dir.exists():
            return []

        return [
            {
                "phase_id": f.stem,
                "path": str(f)
            }
            for f in phases_dir.glob("*.json")
        ]

    def list_frameworks(self) -> List[Dict[str, str]]:
        """List all available frameworks."""
        frameworks_dir = self.config_dir / "frameworks"
        if not frameworks_dir.exists():
            return []

        return [
            {
                "framework_id": f.stem,
                "path": str(f)
            }
            for f in frameworks_dir.glob("*.json")
        ]

    def validate_framework(self, framework: Framework) -> tuple[bool, List[str]]:
        """
        Validate framework structure.

        Checks that all referenced blocks exist.

        Args:
            framework: Framework to validate

        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []

        # Check all phases exist
        for block in framework.building_blocks:
            if block.get("block_type") == "phase":
                phase_id = block.get("block_id")
                try:
                    self.load_phase(phase_id)
                except FileNotFoundError:
                    errors.append(f"Phase not found: {phase_id}")

        return (len(errors) == 0, errors)

    def clear_cache(self):
        """Clear all cached blocks."""
        self._techniques_cache.clear()
        self._workflows_cache.clear()
        self._phases_cache.clear()
        self._frameworks_cache.clear()
