"""
Axiom Manager

Manages user-defined axioms (values, principles) for filtering and scoring.
Axioms represent the user's decision-making framework.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any


class AxiomManager:
    """
    Manages axioms for value-based filtering and scoring.

    Axioms define:
    - Core values and principles (e.g., opportunity cost, risk tolerance)
    - Scoring rules (weight modifiers based on node attributes)
    - Filtering rules (accept/reject nodes based on criteria)

    Example axiom (opportunity_cost):
    {
        "axiom_id": "opportunity_cost",
        "category": "economics",
        "statement": "Evaluate opportunities by opportunity cost",
        "application": "scorer",
        "priority": "critical",
        "weight_modifier": {
            "if_roi_per_hour < 50": -0.5,
            "if_roi_per_hour >= 100": 0.8
        },
        "enabled": true
    }

    Usage:
        manager = AxiomManager("config/axioms")

        # Score a node
        score = manager.score_node(node_data)

        # Filter nodes
        relevant = manager.filter_nodes(nodes, min_score=0.5)
    """

    def __init__(self, axioms_dir: str = "config/axioms"):
        """
        Initialize axiom manager.

        Args:
            axioms_dir: Directory containing axiom JSON files
        """
        self.axioms_dir = Path(axioms_dir)
        self.axioms: Dict[str, Dict] = {}
        self._load_axioms()

    def _load_axioms(self):
        """
        Load all axiom configs from directory.

        Filters for enabled=true axioms only.
        """
        if not self.axioms_dir.exists():
            print(f"Warning: Axioms directory {self.axioms_dir} does not exist")
            return

        for json_file in self.axioms_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    axiom = json.load(f)

                # Only load enabled axioms
                if axiom.get("enabled", False):
                    axiom_id = axiom.get("axiom_id")
                    if axiom_id:
                        self.axioms[axiom_id] = axiom
                        print(f"Loaded axiom: {axiom_id} ({axiom.get('category')})")

            except json.JSONDecodeError as e:
                print(f"Error parsing {json_file}: {e}")
            except Exception as e:
                print(f"Error loading {json_file}: {e}")

    def get_axiom(self, axiom_id: str) -> Optional[Dict]:
        """
        Get axiom by ID.

        Args:
            axiom_id: Axiom identifier

        Returns:
            Axiom dict or None if not found
        """
        return self.axioms.get(axiom_id)

    def get_all_axioms(self) -> List[Dict]:
        """
        Get all loaded axioms.

        Returns:
            List of all axiom dicts
        """
        return list(self.axioms.values())

    def get_axioms_by_category(self, category: str) -> List[Dict]:
        """
        Get all axioms in a category.

        Args:
            category: Category name (e.g., "economics", "risk")

        Returns:
            List of axiom dicts
        """
        return [
            axiom for axiom in self.axioms.values()
            if axiom.get("category") == category
        ]

    def get_scorer_axioms(self) -> List[Dict]:
        """
        Get axioms with application="scorer".

        Returns:
            List of scorer axioms
        """
        return [
            axiom for axiom in self.axioms.values()
            if axiom.get("application") == "scorer"
        ]

    def get_filter_axioms(self) -> List[Dict]:
        """
        Get axioms with application="filter".

        Returns:
            List of filter axioms
        """
        return [
            axiom for axiom in self.axioms.values()
            if axiom.get("application") == "filter"
        ]

    def score_node(self, node_data: Dict[str, Any]) -> float:
        """
        Score a node based on all scorer axioms.

        Algorithm:
        1. Start with base score = node confidence
        2. For each scorer axiom:
           - Check if axiom applies to node
           - Apply weight modifier if conditions met
        3. Clamp final score to [0, 1]

        Args:
            node_data: Node attributes dict

        Returns:
            Final score (0.0 - 1.0)
        """
        # Base score from node confidence
        base_score = node_data.get("confidence", 0.5)
        final_score = base_score

        # Apply scorer axioms
        for axiom in self.get_scorer_axioms():
            modifier = self._evaluate_axiom(axiom, node_data)
            final_score += modifier

        # Clamp to [0, 1]
        return max(0.0, min(1.0, final_score))

    def _evaluate_axiom(self, axiom: Dict, node_data: Dict[str, Any]) -> float:
        """
        Evaluate axiom weight modifier for a node.

        Args:
            axiom: Axiom dict
            node_data: Node attributes

        Returns:
            Weight modifier (can be negative)
        """
        weight_modifiers = axiom.get("weight_modifier", {})

        for condition, modifier in weight_modifiers.items():
            if self._check_condition(condition, node_data):
                # Return first matching condition
                return float(modifier)

        return 0.0  # No conditions matched

    def _check_condition(self, condition: str, node_data: Dict[str, Any]) -> bool:
        """
        Check if a condition applies to node data.

        Supports simple comparisons:
        - "if_roi_per_hour < 50"
        - "if_roi_per_hour >= 100"
        - "if_max_loss > 20%"

        Args:
            condition: Condition string
            node_data: Node attributes

        Returns:
            True if condition met
        """
        # Parse condition (simple implementation)
        # Format: "if_<attribute> <operator> <value>"

        if not condition.startswith("if_"):
            return False

        condition = condition[3:]  # Remove "if_"

        # Extract attribute, operator, value
        for op in [">=", "<=", ">", "<", "=="]:
            if op in condition:
                parts = condition.split(op)
                if len(parts) == 2:
                    attr_name = parts[0].strip()
                    value_str = parts[1].strip()

                    # Get attribute from node metadata
                    node_value = node_data.get("metadata", {}).get(attr_name)
                    if node_value is None:
                        return False

                    # Parse value (handle % suffix)
                    if value_str.endswith("%"):
                        target_value = float(value_str[:-1]) / 100.0
                    else:
                        try:
                            target_value = float(value_str)
                        except ValueError:
                            return False

                    # Evaluate comparison
                    try:
                        if op == ">=":
                            return float(node_value) >= target_value
                        elif op == "<=":
                            return float(node_value) <= target_value
                        elif op == ">":
                            return float(node_value) > target_value
                        elif op == "<":
                            return float(node_value) < target_value
                        elif op == "==":
                            return float(node_value) == target_value
                    except (ValueError, TypeError):
                        return False

        return False

    def filter_nodes(
        self,
        nodes: List[Dict[str, Any]],
        min_score: float = 0.0,
        apply_filters: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Filter nodes based on axioms.

        Args:
            nodes: List of node dicts (with 'id' and attributes)
            min_score: Minimum score threshold
            apply_filters: Apply filter axioms (reject nodes)

        Returns:
            Filtered list of nodes
        """
        filtered = []

        for node in nodes:
            # Score node
            score = self.score_node(node)
            node["axiom_score"] = score

            # Check minimum score
            if score < min_score:
                continue

            # Apply filter axioms (if enabled)
            if apply_filters:
                reject = False
                for axiom in self.get_filter_axioms():
                    # If any filter axiom rejects, skip node
                    if self._should_reject(axiom, node):
                        reject = True
                        break

                if reject:
                    continue

            filtered.append(node)

        return filtered

    def _should_reject(self, axiom: Dict, node_data: Dict[str, Any]) -> bool:
        """
        Check if filter axiom rejects a node.

        For now, uses same weight_modifier logic:
        - If modifier is -1.0, reject the node

        Args:
            axiom: Filter axiom
            node_data: Node attributes

        Returns:
            True if node should be rejected
        """
        modifier = self._evaluate_axiom(axiom, node_data)
        return modifier == -1.0

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about loaded axioms.

        Returns:
            {
                "total_axioms": 2,
                "scorers": 1,
                "filters": 1,
                "by_category": {"economics": 1, "risk": 1}
            }
        """
        by_category = {}
        for axiom in self.axioms.values():
            cat = axiom.get("category", "unknown")
            by_category[cat] = by_category.get(cat, 0) + 1

        return {
            "total_axioms": len(self.axioms),
            "scorers": len(self.get_scorer_axioms()),
            "filters": len(self.get_filter_axioms()),
            "by_category": by_category,
            "axiom_ids": list(self.axioms.keys())
        }
