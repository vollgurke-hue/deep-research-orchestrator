"""
StateManager - File Tracking & Validation History

Tracks file changes via SHA256 hashing and maintains validation history.
Enables intelligent re-validation detection.
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class StateManager:
    """Manages validation state and file change tracking."""

    def __init__(self, state_file: Path = None):
        """
        Initialize StateManager.

        Args:
            state_file: Path to state JSON file (default: validation_state.json)
        """
        if state_file is None:
            state_file = Path("validation_state.json")

        self.state_file = Path(state_file)
        self.state = self._load_state()

    def _load_state(self) -> Dict:
        """Load state from JSON file."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to load state file: {e}. Creating new state.")
                return self._create_empty_state()
        else:
            logger.info("No state file found. Creating new state.")
            return self._create_empty_state()

    def _create_empty_state(self) -> Dict:
        """Create empty state structure."""
        return {
            "files": {},
            "metadata": {
                "last_updated": datetime.now().isoformat(),
                "total_validations": 0,
                "version": "2.0"
            }
        }

    def _save_state(self):
        """Persist state to JSON file."""
        self.state["metadata"]["last_updated"] = datetime.now().isoformat()

        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)

        logger.debug(f"State saved to {self.state_file}")

    def compute_file_hash(self, file_path: Path) -> str:
        """
        Compute SHA256 hash of file.

        Args:
            file_path: Path to file

        Returns:
            SHA256 hash as hex string
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        sha256 = hashlib.sha256()

        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)

        return sha256.hexdigest()

    def has_file_changed(self, file_path: Path) -> bool:
        """
        Check if file changed since last validation.

        Args:
            file_path: Path to file

        Returns:
            True if file changed or never validated, False otherwise
        """
        file_path = Path(file_path)
        file_key = str(file_path.resolve())

        if file_key not in self.state["files"]:
            # Never validated before
            return True

        current_hash = self.compute_file_hash(file_path)
        stored_hash = self.state["files"][file_key].get("hash")

        return current_hash != stored_hash

    def record_validation(
        self,
        file_path: Path,
        workflow_id: str,
        result: Dict[str, Any]
    ):
        """
        Record successful validation.

        Args:
            file_path: File that was validated
            workflow_id: Workflow ID used
            result: Validation result dict
        """
        file_path = Path(file_path)
        file_key = str(file_path.resolve())

        # Compute current file hash
        file_hash = self.compute_file_hash(file_path)

        # Create validation record
        validation_record = {
            "timestamp": datetime.now().isoformat(),
            "workflow": workflow_id,
            "model": result.get("model", "unknown"),
            "techniques_used": result.get("techniques_used", []),
            "status": result.get("status", "completed"),
            "report_path": result.get("report_path", None)
        }

        # Initialize file entry if needed
        if file_key not in self.state["files"]:
            self.state["files"][file_key] = {
                "hash": file_hash,
                "last_validated": datetime.now().isoformat(),
                "validations": []
            }

        # Update file entry
        self.state["files"][file_key]["hash"] = file_hash
        self.state["files"][file_key]["last_validated"] = datetime.now().isoformat()
        self.state["files"][file_key]["validations"].append(validation_record)

        # Update metadata
        self.state["metadata"]["total_validations"] += 1

        # Persist
        self._save_state()

        logger.info(f"Recorded validation for {file_path} with workflow {workflow_id}")

    def get_validation_history(self, file_path: Path) -> List[Dict]:
        """
        Get all validations for a file.

        Args:
            file_path: Path to file

        Returns:
            List of validation records (newest first)
        """
        file_path = Path(file_path)
        file_key = str(file_path.resolve())

        if file_key not in self.state["files"]:
            return []

        validations = self.state["files"][file_key].get("validations", [])

        # Return newest first
        return list(reversed(validations))

    def get_files_needing_validation(
        self,
        directory: Path,
        workflow_id: str,
        file_pattern: str = "*.md"
    ) -> List[Path]:
        """
        Find files that changed or were never validated.

        Args:
            directory: Directory to scan
            workflow_id: Workflow ID to check
            file_pattern: Glob pattern for files (default: *.md)

        Returns:
            List of file paths needing validation
        """
        directory = Path(directory)

        if not directory.exists():
            logger.warning(f"Directory not found: {directory}")
            return []

        files_needing_validation = []

        # Find all matching files
        for file_path in directory.rglob(file_pattern):
            if not file_path.is_file():
                continue

            file_key = str(file_path.resolve())

            # Check if file needs validation
            needs_validation = False

            if file_key not in self.state["files"]:
                # Never validated
                needs_validation = True
                logger.debug(f"{file_path} needs validation: never validated")
            else:
                # Check if file changed
                if self.has_file_changed(file_path):
                    needs_validation = True
                    logger.debug(f"{file_path} needs validation: file changed")
                else:
                    # Check if this specific workflow was run
                    validations = self.state["files"][file_key].get("validations", [])
                    workflow_run = any(v["workflow"] == workflow_id for v in validations)

                    if not workflow_run:
                        needs_validation = True
                        logger.debug(f"{file_path} needs validation: workflow {workflow_id} never run")

            if needs_validation:
                files_needing_validation.append(file_path)

        logger.info(f"Found {len(files_needing_validation)} files needing validation")

        return files_needing_validation

    def export_state(self) -> Dict:
        """
        Export full state for debugging.

        Returns:
            Complete state dict
        """
        return self.state.copy()

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get state statistics.

        Returns:
            Dict with statistics
        """
        total_files = len(self.state["files"])
        total_validations = self.state["metadata"]["total_validations"]

        # Count workflows
        workflow_counts = {}
        for file_data in self.state["files"].values():
            for validation in file_data.get("validations", []):
                workflow = validation["workflow"]
                workflow_counts[workflow] = workflow_counts.get(workflow, 0) + 1

        return {
            "total_files_tracked": total_files,
            "total_validations": total_validations,
            "workflow_counts": workflow_counts,
            "last_updated": self.state["metadata"]["last_updated"]
        }

    def clear_history(self, file_path: Path = None):
        """
        Clear validation history.

        Args:
            file_path: If provided, clear only this file. Otherwise clear all.
        """
        if file_path:
            file_key = str(Path(file_path).resolve())
            if file_key in self.state["files"]:
                del self.state["files"][file_key]
                logger.info(f"Cleared history for {file_path}")
        else:
            self.state = self._create_empty_state()
            logger.info("Cleared all validation history")

        self._save_state()


# Test function
def _test_state_manager():
    """Test StateManager functionality."""
    import tempfile
    import os

    # Create temp state file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        state_file = Path(f.name)

    try:
        # Initialize manager
        manager = StateManager(state_file)

        # Create test file
        test_file = Path("test_file.md")
        test_file.write_text("Test content")

        # Check if changed (should be True - never validated)
        assert manager.has_file_changed(test_file), "Should detect new file"

        # Record validation
        manager.record_validation(
            test_file,
            "research_validation",
            {
                "model": "tier1_fast",
                "techniques_used": ["contradiction", "blind_spots"],
                "status": "completed"
            }
        )

        # Check if changed (should be False - just validated)
        assert not manager.has_file_changed(test_file), "Should not detect change after validation"

        # Modify file
        test_file.write_text("Modified content")

        # Check if changed (should be True - file modified)
        assert manager.has_file_changed(test_file), "Should detect file modification"

        # Get history
        history = manager.get_validation_history(test_file)
        assert len(history) == 1, "Should have 1 validation record"

        # Get statistics
        stats = manager.get_statistics()
        print("\nStateManager Test Results:")
        print(f"✅ Total files tracked: {stats['total_files_tracked']}")
        print(f"✅ Total validations: {stats['total_validations']}")
        print(f"✅ All tests passed!")

        # Cleanup
        test_file.unlink()

    finally:
        # Cleanup
        if state_file.exists():
            state_file.unlink()


if __name__ == "__main__":
    # Run tests
    logging.basicConfig(level=logging.INFO)
    _test_state_manager()
