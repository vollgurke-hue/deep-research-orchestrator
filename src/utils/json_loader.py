"""JSON configuration loader utilities."""
import json
from pathlib import Path
from typing import Dict, Any, List


class JSONLoader:
    """Load and validate JSON configuration files."""

    @staticmethod
    def load(path: Path) -> Dict[str, Any]:
        """Load JSON file."""
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def load_all(directory: Path, pattern: str = "*.json") -> List[Dict[str, Any]]:
        """Load all JSON files from directory."""
        configs = []
        for file_path in directory.glob(pattern):
            configs.append(JSONLoader.load(file_path))
        return configs

    @staticmethod
    def save(data: Dict[str, Any], path: Path) -> None:
        """Save data to JSON file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
