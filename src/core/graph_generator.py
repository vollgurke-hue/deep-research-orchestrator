"""
Seed Graph Generator - LLM-based extraction of research graph from description.

This module transforms a textual research description into a structured graph
of concepts, relationships, and value tensions.
"""
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import asdict

from src.models.unified_session import (
    SeedGraphMetadata,
    SeedGraphNode,
    SeedGraphEdge,
    ValueTension,
    GraphStructure
)


class GraphGenerator:
    """Generates seed graphs from research descriptions using LLM."""

    def __init__(self, llm_provider):
        """
        Initialize graph generator.

        Args:
            llm_provider: LLM provider instance (UnifiedLLMProvider)
        """
        self.llm_provider = llm_provider

    def generate_from_description(
        self,
        description: str,
        goal: str,
        value_profile_id: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a seed graph from research description.

        Args:
            description: Research description text
            goal: Research goal/question
            value_profile_id: Optional value profile for tension detection
            params: Generation parameters (max_nodes, edge_density, etc.)

        Returns:
            Dictionary matching Gemini v2.0 Seed Graph schema
        """
        params = params or {}
        max_nodes = params.get('max_nodes', 8)
        min_nodes = params.get('min_nodes', 3)
        edge_density = params.get('edge_density', 'medium')
        include_value_tensions = params.get('include_value_tensions', True)

        # Build extraction prompt
        extraction_prompt = self._build_extraction_prompt(
            description=description,
            goal=goal,
            max_nodes=max_nodes,
            min_nodes=min_nodes,
            edge_density=edge_density,
            value_profile_id=value_profile_id,
            include_value_tensions=include_value_tensions
        )

        # Get LLM response
        try:
            response = self.llm_provider.query(
                extraction_prompt,
                temperature=0.7,
                max_tokens=4000
            )

            # Parse JSON from response
            graph_data = self._parse_llm_response(response)

            # Validate and enhance
            graph_data = self._validate_and_enhance(graph_data, value_profile_id)

            return graph_data

        except Exception as e:
            print(f"Error generating seed graph: {e}")
            # Return minimal fallback graph
            return self._create_fallback_graph(description, goal)

    def _build_extraction_prompt(
        self,
        description: str,
        goal: str,
        max_nodes: int,
        min_nodes: int,
        edge_density: str,
        value_profile_id: Optional[str],
        include_value_tensions: bool
    ) -> str:
        """Build the LLM prompt for graph extraction."""

        prompt = f"""You are a research structuring AI. Extract a knowledge graph from the research description below.

**Research Goal:** {goal}

**Research Description:**
{description}

---

**Task:** Generate a JSON object representing a seed graph for this research. The graph should:
1. Identify {min_nodes}-{max_nodes} KEY CONCEPTS, TECHNICAL AREAS, and ALTERNATIVES
2. Define RELATIONSHIPS between them (supports, requires, conflicts_with, enables, informs, constrains, risks)
3. Assign each node a STATUS (defined, gap, potential_conflict)
4. Use edge WEIGHTS from -1.0 to 1.0 (negative for conflicts)

**Node Types:**
- "concept": Main ideas, core concepts, primary research areas
- "technical": Technical details, implementation specifics, methodologies
- "alternative": Alternative approaches, competing solutions, different perspectives

**Node Status:**
- "defined": Clear, well-scoped concept
- "gap": Identified but needs investigation
- "potential_conflict": May conflict with values or constraints

**Edge Relations:**
- "supports": A helps/strengthens B (weight: 0.1-1.0)
- "requires": A needs B (mandatory, weight: 1.0)
- "enables": A makes B possible (weight: 0.5-1.0)
- "informs": A provides data for B (weight: 0.1-0.5)
- "conflicts_with": A contradicts B (weight: -1.0 to -0.1)
- "constrains": A limits B (weight: -0.5 to 0.0)
- "risks": A threatens B (weight: -1.0 to -0.5)

**Edge Density:** {edge_density} (low=sparse connections, medium=balanced, high=highly connected)
"""

        if value_profile_id:
            prompt += f"""
**Value Profile:** {value_profile_id}
- Look for nodes that might conflict with this value profile
- Mark those nodes as status="potential_conflict"
- Add entries to "value_tensions" array
"""

        prompt += """
**Output Format (strict JSON):**
```json
{
  "metadata": {
    "version": "2.0",
    "generated_at": "<ISO timestamp>",
    "root_node_id": "<id of most central concept>",
    "active_value_profile": "<value profile id or null>"
  },
  "nodes": [
    {
      "id": "node_001",
      "label": "Concise node label",
      "type": "concept",
      "status": "defined",
      "coverage": 0.0,
      "metadata": {
        "description": "Detailed description",
        "keywords": ["keyword1", "keyword2"],
        "priority": "high",
        "estimated_effort": "medium"
      }
    }
  ],
  "edges": [
    {
      "source": "node_001",
      "target": "node_002",
      "relation": "supports",
      "weight": 0.8,
      "description": "How this relationship works"
    }
  ],
  "value_tensions": [
    {
      "nodes": ["node_001", "node_003"],
      "type": "high_friction",
      "reason": "Explanation of the conflict"
    }
  ]
}
```

**IMPORTANT:**
- Output ONLY valid JSON, no markdown code blocks
- Include AT LEAST {min_nodes} nodes
- Create meaningful relationships (edge_density: {edge_density})
- Root node should be the most central concept
- Ensure all source/target node IDs exist in nodes array
"""

        return prompt

    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse and clean LLM JSON response."""
        # Remove markdown code blocks if present
        response = response.strip()
        if response.startswith('```'):
            lines = response.split('\n')
            # Remove first and last lines (```json and ```)
            response = '\n'.join(lines[1:-1])

        # Parse JSON
        try:
            graph_data = json.loads(response)
            return graph_data
        except json.JSONDecodeError as e:
            # Try to extract JSON from response
            print(f"JSON parse error: {e}")
            print(f"Response: {response[:500]}...")

            # Try to find JSON object boundaries
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)

            raise ValueError("Could not extract valid JSON from LLM response")

    def _validate_and_enhance(
        self,
        graph_data: Dict[str, Any],
        value_profile_id: Optional[str]
    ) -> Dict[str, Any]:
        """Validate and enhance the graph data."""

        # Ensure metadata exists
        if 'metadata' not in graph_data:
            graph_data['metadata'] = {}

        metadata = graph_data['metadata']
        metadata['version'] = '2.0'
        metadata['generated_at'] = datetime.utcnow().isoformat()
        metadata['active_value_profile'] = value_profile_id

        # Find root node if not specified
        if not metadata.get('root_node_id') and graph_data.get('nodes'):
            # Root is node with most connections
            node_ids = {n['id'] for n in graph_data['nodes']}
            edge_counts = {nid: 0 for nid in node_ids}

            for edge in graph_data.get('edges', []):
                if edge['source'] in edge_counts:
                    edge_counts[edge['source']] += 1
                if edge['target'] in edge_counts:
                    edge_counts[edge['target']] += 1

            root_id = max(edge_counts.items(), key=lambda x: x[1])[0] if edge_counts else graph_data['nodes'][0]['id']
            metadata['root_node_id'] = root_id

        # Ensure all nodes have required fields
        for node in graph_data.get('nodes', []):
            if 'coverage' not in node:
                node['coverage'] = 0.0
            if 'metadata' not in node:
                node['metadata'] = {}

        # Ensure all edges have required fields
        for edge in graph_data.get('edges', []):
            if 'weight' not in edge:
                # Default weight based on relation
                if edge['relation'] in ['supports', 'enables', 'requires']:
                    edge['weight'] = 0.7
                elif edge['relation'] in ['conflicts_with', 'risks']:
                    edge['weight'] = -0.7
                else:
                    edge['weight'] = 0.5

        # Ensure value_tensions array exists
        if 'value_tensions' not in graph_data:
            graph_data['value_tensions'] = []

        return graph_data

    def _create_fallback_graph(self, description: str, goal: str) -> Dict[str, Any]:
        """Create a minimal fallback graph if LLM fails."""

        root_id = f"node_{uuid.uuid4().hex[:8]}"

        return {
            "metadata": {
                "version": "2.0",
                "generated_at": datetime.utcnow().isoformat(),
                "root_node_id": root_id,
                "active_value_profile": None
            },
            "nodes": [
                {
                    "id": root_id,
                    "label": "Main Research Area",
                    "type": "concept",
                    "status": "gap",
                    "coverage": 0.0,
                    "metadata": {
                        "description": description[:200],
                        "keywords": [],
                        "priority": "high"
                    }
                }
            ],
            "edges": [],
            "value_tensions": []
        }

    def graph_to_dataclass(self, graph_data: Dict[str, Any]) -> GraphStructure:
        """Convert graph dictionary to GraphStructure dataclass."""

        metadata = SeedGraphMetadata(**graph_data['metadata'])

        nodes = [
            SeedGraphNode(**node_data)
            for node_data in graph_data.get('nodes', [])
        ]

        edges = [
            SeedGraphEdge(**edge_data)
            for edge_data in graph_data.get('edges', [])
        ]

        value_tensions = [
            ValueTension(**vt_data)
            for vt_data in graph_data.get('value_tensions', [])
        ]

        return GraphStructure(
            metadata=metadata,
            nodes=nodes,
            edges=edges,
            value_tensions=value_tensions,
            node_count=len(nodes),
            edge_count=len(edges),
            density=len(edges) / (len(nodes) * (len(nodes) - 1)) if len(nodes) > 1 else 0.0
        )
