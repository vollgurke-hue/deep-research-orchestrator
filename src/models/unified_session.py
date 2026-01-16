"""
Unified Session Model - Single source of truth for all research types.

This model bridges Product Research, Sovereign Research, and Legacy Orchestrator
into one unified session structure with flexible mode selection.
"""
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from pathlib import Path


# ========================================================================
# SPO Knowledge Graph (Cluster 1 - SRO Implementation)
# ========================================================================

@dataclass
class SPOProvenance:
    """Provenance tracking for SPO tripletts."""
    source_id: str  # response_id or external source identifier
    extraction_method: str  # llm_structured | manual | imported
    model_used: Optional[str] = None  # Model that extracted this triplet
    extracted_at: Optional[str] = None  # ISO timestamp
    verified: bool = False
    verification_count: int = 0
    verification_sources: List[str] = field(default_factory=list)


@dataclass
class SPOTriplet:
    """
    Subject-Predicate-Object triplet for structured knowledge representation.

    Core of the SPO Knowledge Graph concept - atomic facts that are:
    - Machine-readable
    - Verifiable
    - Composable into complex knowledge structures

    Example:
        subject="Solaranlage"
        predicate="ROI-Periode"
        object="15-20 Jahre"
        confidence=0.85
        tier="bronze"
    """
    id: str  # Unique triplet ID (spo_uuid)
    subject: str  # The entity being described
    predicate: str  # The relationship/property
    object: str  # The value/target entity
    confidence: float  # 0.0-1.0 confidence score

    # Tiered RAG (Bronze/Silver/Gold)
    tier: str = "bronze"  # bronze | silver | gold

    # Provenance
    provenance: SPOProvenance = field(default_factory=lambda: SPOProvenance(
        source_id="unknown",
        extraction_method="unknown"
    ))

    # Timestamps
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    # Metadata (flexible JSON storage)
    metadata: Dict[str, Any] = field(default_factory=dict)  # domain, axiom_scores, bias_vector, etc.


# ========================================================================
# Session Metadata & Structure
# ========================================================================

@dataclass
class UnifiedSessionMetadata:
    """Session metadata common to all research modes."""
    session_id: str
    title: str
    created_at: str  # ISO format timestamp
    updated_at: str
    status: str  # wizard | exploring | validating | synthesis | complete
    mode: str  # thematic | tot | workflow | unified
    creator: str = "user"  # user | system | agent


@dataclass
class ResearchContext:
    """Research context and constraints."""
    goal: str  # Primary research goal/question
    description: str = ""  # Detailed description (for Product Research)
    research_type: str = "product"  # product | market | scientific | business | technical
    axioms: List[str] = field(default_factory=list)  # Active axiom IDs
    constraints: Dict[str, Any] = field(default_factory=dict)  # vram_limit, max_budget, etc.
    user_input: str = ""  # Original user input (for legacy)


@dataclass
class ThematicStructure:
    """Thematic hierarchy from Product Research."""
    themes: List[Dict[str, Any]] = field(default_factory=list)  # {id, label, coverage, children}
    coverage_percentage: float = 0.0
    missing_aspects: List[str] = field(default_factory=list)
    suggested_themes: List[str] = field(default_factory=list)


@dataclass
class ToTStructure:
    """Tree of Thoughts structure from Sovereign Research."""
    root_node_id: Optional[str] = None
    total_nodes: int = 0
    max_depth: int = 3
    branching_factor: int = 3
    active_leaves: List[str] = field(default_factory=list)
    pruned_branches: List[str] = field(default_factory=list)


@dataclass
class SeedGraphMetadata:
    """Metadata for seed graph generation."""
    version: str = "2.0"
    generated_at: Optional[str] = None
    root_node_id: Optional[str] = None
    active_value_profile: Optional[str] = None
    generation_method: str = "llm_extraction"
    model_used: Optional[str] = None


@dataclass
class SeedGraphNode:
    """Individual node in the seed graph."""
    id: str
    label: str
    type: str  # concept | technical | alternative
    status: str  # defined | gap | potential_conflict
    coverage: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SeedGraphEdge:
    """Edge/relationship in the seed graph."""
    source: str  # node ID
    target: str  # node ID
    relation: str  # supports | requires | conflicts_with | enables | informs | constrains | risks
    weight: float = 0.0  # -1.0 to 1.0 (negative for conflicts)
    description: str = ""


@dataclass
class ValueTension:
    """Represents a conflict between research nodes and value profiles."""
    nodes: List[str]  # List of node IDs involved
    type: str  # high_friction | moderate_risk | attention_needed
    reason: str = ""


@dataclass
class GraphStructure:
    """
    Seed Graph structure for graph-based research definition.
    Replaces hierarchical themes with relational graph.
    """
    # Seed graph components (Gemini v2.0 schema)
    metadata: Optional[SeedGraphMetadata] = None
    nodes: List[SeedGraphNode] = field(default_factory=list)
    edges: List[SeedGraphEdge] = field(default_factory=list)
    value_tensions: List[ValueTension] = field(default_factory=list)

    # Legacy NetworkX graph metadata (for backward compatibility)
    graph_file: Optional[str] = None  # Path to exported NetworkX graph
    node_count: int = 0
    edge_count: int = 0
    density: float = 0.0
    max_nodes: int = 10000


@dataclass
class WorkingState:
    """Current execution state."""
    current_phase: int = 0  # 0=wizard, 1=exploration, 2=validation, 3=synthesis
    active_nodes: List[str] = field(default_factory=list)  # Currently processing nodes
    completed_nodes: List[str] = field(default_factory=list)
    mcts_stats: Dict[str, Any] = field(default_factory=dict)  # iterations, best_path_score
    technique_stack: List[str] = field(default_factory=list)  # Active techniques/skills
    progress_metrics: Dict[str, float] = field(default_factory=dict)  # Custom progress tracking


@dataclass
class Response:
    """Unified response format for all AI responses."""
    response_id: str
    node_id: Optional[str]  # ToT node or theme ID
    source: str  # claude-opus | gpt-4 | gemini-pro | local-llm
    content: str
    timestamp: str

    # Evaluation metrics
    relevance_score: float = 0.0  # 0-1 (Product Research)
    accuracy_score: float = 0.0  # 0-1 (Product Research)
    confidence: float = 0.0  # 0-1 (Sovereign Research)

    # Extraction results
    entities_extracted: List[str] = field(default_factory=list)
    triplets_extracted: bool = False
    graph_facts_added: List[str] = field(default_factory=list)

    # Axiom evaluation
    axiom_evaluation: Dict[str, Any] = field(default_factory=dict)  # {score, conflicts, verdict}
    axiom_compatible: bool = True

    # Quality metrics
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)


@dataclass
class UnifiedSession:
    """
    Unified Session Object - Single source of truth for all research modes.

    Modes:
    - thematic: Product Research Framework (wizard-driven, coverage-focused)
    - tot: Sovereign Research (ToT/Graph/MCTS exploration)
    - workflow: Legacy Orchestrator (config-driven automation)
    - unified: New hybrid mode combining all three
    """
    # Core metadata
    metadata: UnifiedSessionMetadata

    # Research context
    context: ResearchContext

    # Structure (mode-specific, but all can coexist)
    thematic: Optional[ThematicStructure] = None
    tot: Optional[ToTStructure] = None
    graph: Optional[GraphStructure] = None

    # Working state
    state: WorkingState = field(default_factory=WorkingState)

    # Responses (unified across all modes)
    responses: List[Response] = field(default_factory=list)

    # Prompts generated
    prompts: List[Dict[str, Any]] = field(default_factory=list)  # {prompt_id, theme_id/node_id, text}

    # Component references (not serialized - runtime only)
    _graph_manager: Any = field(default=None, repr=False)
    _tot_manager: Any = field(default=None, repr=False)
    _axiom_manager: Any = field(default=None, repr=False)
    _mcts_engine: Any = field(default=None, repr=False)
    _orchestrator: Any = field(default=None, repr=False)

    def to_dict(self) -> Dict[str, Any]:
        """Export session to dictionary (excludes runtime components)."""
        data = asdict(self)
        # Remove runtime components
        for key in ['_graph_manager', '_tot_manager', '_axiom_manager', '_mcts_engine', '_orchestrator']:
            data.pop(key, None)
        return data

    def to_json(self) -> str:
        """Export session to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UnifiedSession':
        """Load session from dictionary."""
        # Reconstruct nested dataclasses
        metadata = UnifiedSessionMetadata(**data['metadata'])
        context = ResearchContext(**data['context'])
        state = WorkingState(**data.get('state', {}))

        # Optional structures
        thematic = ThematicStructure(**data['thematic']) if data.get('thematic') else None
        tot = ToTStructure(**data['tot']) if data.get('tot') else None

        # Graph structure (with nested seed graph components)
        graph = None
        if data.get('graph'):
            graph_data = data['graph']
            graph_metadata = None
            if graph_data.get('metadata'):
                graph_metadata = SeedGraphMetadata(**graph_data['metadata'])

            nodes = [SeedGraphNode(**n) for n in graph_data.get('nodes', [])]
            edges = [SeedGraphEdge(**e) for e in graph_data.get('edges', [])]
            value_tensions = [ValueTension(**vt) for vt in graph_data.get('value_tensions', [])]

            graph = GraphStructure(
                metadata=graph_metadata,
                nodes=nodes,
                edges=edges,
                value_tensions=value_tensions,
                graph_file=graph_data.get('graph_file'),
                node_count=graph_data.get('node_count', len(nodes)),
                edge_count=graph_data.get('edge_count', len(edges)),
                density=graph_data.get('density', 0.0),
                max_nodes=graph_data.get('max_nodes', 10000)
            )

        # Responses
        responses = [Response(**r) for r in data.get('responses', [])]

        return cls(
            metadata=metadata,
            context=context,
            thematic=thematic,
            tot=tot,
            graph=graph,
            state=state,
            responses=responses,
            prompts=data.get('prompts', [])
        )

    @classmethod
    def from_json(cls, json_str: str) -> 'UnifiedSession':
        """Load session from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def update_timestamp(self):
        """Update the updated_at timestamp."""
        self.metadata.updated_at = datetime.utcnow().isoformat()

    def add_response(self, response: Response):
        """Add a response and update timestamp."""
        self.responses.append(response)
        self.update_timestamp()

    def add_prompt(self, prompt_id: str, node_id: str, text: str, **metadata):
        """Add a generated prompt."""
        prompt = {
            "prompt_id": prompt_id,
            "node_id": node_id,
            "text": text,
            "created_at": datetime.utcnow().isoformat(),
            **metadata
        }
        self.prompts.append(prompt)
        self.update_timestamp()

    def get_coverage_metrics(self) -> Dict[str, float]:
        """Calculate coverage metrics across all modes."""
        metrics = {}

        # Thematic coverage
        if self.thematic:
            metrics['thematic_coverage'] = self.thematic.coverage_percentage

        # ToT coverage (explored vs total possible)
        if self.tot and self.tot.total_nodes > 0:
            explored_ratio = len(self.state.completed_nodes) / self.tot.total_nodes
            metrics['tot_exploration'] = explored_ratio

        # Response quality (average scores)
        if self.responses:
            avg_relevance = sum(r.relevance_score for r in self.responses) / len(self.responses)
            avg_accuracy = sum(r.accuracy_score for r in self.responses) / len(self.responses)
            avg_confidence = sum(r.confidence for r in self.responses) / len(self.responses)

            metrics['avg_relevance'] = avg_relevance
            metrics['avg_accuracy'] = avg_accuracy
            metrics['avg_confidence'] = avg_confidence

        return metrics

    def get_axiom_alignment(self) -> Dict[str, Any]:
        """Calculate axiom alignment across all responses."""
        if not self.responses:
            return {"overall_score": 0.0, "conflicts": [], "supports": 0, "contradicts": 0}

        total_score = 0.0
        conflicts = []
        supports = 0
        contradicts = 0
        neutral = 0

        for response in self.responses:
            if response.axiom_evaluation:
                score = response.axiom_evaluation.get('score', 0.0)
                total_score += score

                verdict = response.axiom_evaluation.get('verdict', 'neutral')
                if verdict == 'supports':
                    supports += 1
                elif verdict == 'contradicts':
                    contradicts += 1
                    conflicts.append({
                        "response_id": response.response_id,
                        "source": response.source,
                        "conflict": response.axiom_evaluation.get('conflicts', [])
                    })
                else:
                    neutral += 1

        return {
            "overall_score": total_score / len(self.responses) if self.responses else 0.0,
            "conflicts": conflicts,
            "supports": supports,
            "contradicts": contradicts,
            "neutral": neutral
        }

    def export_for_frontend(self) -> Dict[str, Any]:
        """Export minimal session data for frontend display."""
        return {
            "session_id": self.metadata.session_id,
            "title": self.metadata.title,
            "status": self.metadata.status,
            "mode": self.metadata.mode,
            "created_at": self.metadata.created_at,
            "goal": self.context.goal,
            "current_phase": self.state.current_phase,
            "responses_count": len(self.responses),
            "prompts_count": len(self.prompts),
            "coverage_metrics": self.get_coverage_metrics(),
            "axiom_alignment": self.get_axiom_alignment()
        }


# Factory functions for different modes

def create_thematic_session(
    session_id: str,
    title: str,
    goal: str,
    description: str = "",
    research_type: str = "product"
) -> UnifiedSession:
    """Create a new Product Research (thematic) session."""
    return UnifiedSession(
        metadata=UnifiedSessionMetadata(
            session_id=session_id,
            title=title,
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
            status="wizard",
            mode="thematic"
        ),
        context=ResearchContext(
            goal=goal,
            description=description,
            research_type=research_type
        ),
        thematic=ThematicStructure(),
        graph=GraphStructure()  # Product Research also builds a graph
    )


def create_tot_session(
    session_id: str,
    title: str,
    question: str,
    axioms: List[str] = None
) -> UnifiedSession:
    """Create a new Sovereign Research (ToT) session."""
    return UnifiedSession(
        metadata=UnifiedSessionMetadata(
            session_id=session_id,
            title=title,
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
            status="exploring",
            mode="tot"
        ),
        context=ResearchContext(
            goal=question,
            axioms=axioms or []
        ),
        tot=ToTStructure(),
        graph=GraphStructure()
    )


def create_unified_session(
    session_id: str,
    title: str,
    goal: str,
    description: str = "",
    axioms: List[str] = None,
    research_type: str = "product"
) -> UnifiedSession:
    """Create a new Unified session (combines all modes)."""
    return UnifiedSession(
        metadata=UnifiedSessionMetadata(
            session_id=session_id,
            title=title,
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
            status="wizard",
            mode="unified"
        ),
        context=ResearchContext(
            goal=goal,
            description=description,
            research_type=research_type,
            axioms=axioms or []
        ),
        thematic=ThematicStructure(),
        tot=ToTStructure(),
        graph=GraphStructure()
    )
