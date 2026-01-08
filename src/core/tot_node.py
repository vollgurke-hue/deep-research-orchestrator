"""
Tree of Thoughts Node

Represents a single node in the ToT exploration tree.
Each node is a question/sub-question with exploration state.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict
from datetime import datetime


@dataclass
class ToTNode:
    """
    A node in the Tree of Thoughts exploration.

    Attributes:
        node_id: Unique identifier
        parent_id: Parent node ID (None for root)
        question: The question this node explores
        depth: Distance from root (0 = root)
        status: Exploration status

    Status values:
        - "pending": Not yet explored
        - "exploring": Currently being explored
        - "evaluated": Exploration complete
        - "pruned": Branch pruned (low value/violates axioms)

    Results:
        answer: LLM-generated answer (if evaluated)
        confidence: Confidence in answer (0.0-1.0)
        reasoning: Explanation of answer

    Graph Integration:
        graph_entities: Entity IDs extracted from answer
        graph_facts: Fact node IDs added to graph

    MCTS Metrics:
        visits: Number of times node selected
        value: Cumulative value from simulations
        ucb1_score: Upper Confidence Bound score

    Axiom Evaluation:
        axiom_scores: Dict mapping axiom_id -> score
        axiom_compatible: Whether node passes all axioms
    """

    # Core attributes
    node_id: str
    parent_id: Optional[str]
    question: str
    depth: int
    status: str = "pending"

    # Metadata
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    # Results (populated after exploration)
    answer: Optional[str] = None
    confidence: float = 0.0
    reasoning: Optional[str] = None

    # Graph integration
    graph_entities: List[str] = field(default_factory=list)
    graph_facts: List[str] = field(default_factory=list)

    # MCTS metrics
    visits: int = 0
    value: float = 0.0
    ucb1_score: float = 0.0

    # Axiom evaluation
    axiom_scores: Dict[str, float] = field(default_factory=dict)
    axiom_compatible: bool = True

    # Children tracking
    children: List[str] = field(default_factory=list)

    def is_leaf(self) -> bool:
        """Check if node is a leaf (no children)"""
        return len(self.children) == 0

    def is_explored(self) -> bool:
        """Check if node has been explored"""
        return self.status == "evaluated"

    def is_pruned(self) -> bool:
        """Check if node is pruned"""
        return self.status == "pruned"

    def avg_value(self) -> float:
        """Get average value per visit"""
        if self.visits == 0:
            return 0.0
        return self.value / self.visits

    def add_child(self, child_id: str):
        """Add child node ID"""
        if child_id not in self.children:
            self.children.append(child_id)

    def update_timestamp(self):
        """Update last modified timestamp"""
        self.updated_at = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "node_id": self.node_id,
            "parent_id": self.parent_id,
            "question": self.question,
            "depth": self.depth,
            "status": self.status,
            "answer": self.answer,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "graph_entities": self.graph_entities,
            "graph_facts": self.graph_facts,
            "visits": self.visits,
            "value": self.value,
            "ucb1_score": self.ucb1_score,
            "axiom_scores": self.axiom_scores,
            "axiom_compatible": self.axiom_compatible,
            "children": self.children,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "ToTNode":
        """Create ToTNode from dictionary"""
        return cls(
            node_id=data["node_id"],
            parent_id=data.get("parent_id"),
            question=data["question"],
            depth=data["depth"],
            status=data.get("status", "pending"),
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
            updated_at=data.get("updated_at", datetime.utcnow().isoformat()),
            answer=data.get("answer"),
            confidence=data.get("confidence", 0.0),
            reasoning=data.get("reasoning"),
            graph_entities=data.get("graph_entities", []),
            graph_facts=data.get("graph_facts", []),
            visits=data.get("visits", 0),
            value=data.get("value", 0.0),
            ucb1_score=data.get("ucb1_score", 0.0),
            axiom_scores=data.get("axiom_scores", {}),
            axiom_compatible=data.get("axiom_compatible", True),
            children=data.get("children", [])
        )
