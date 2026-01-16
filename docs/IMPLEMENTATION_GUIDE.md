# Node-Based Pipeline Implementation Guide

**Date:** 2025-12-24  
**Focus:** Concrete code examples and step-by-step implementation

---

## Quick Start Example

### Define a Simple DAG (JSON)

```json
{
  "pipeline_id": "simple_research",
  "name": "Simple Research Pipeline",
  "nodes": [
    {
      "node_id": "start",
      "node_type": "input",
      "config": {
        "variables": ["topic", "depth"]
      }
    },
    {
      "node_id": "research",
      "node_type": "agent",
      "config": {
        "agent_id": "fast_researcher",
        "task_template": "Research the topic: {topic}\nDepth: {depth}"
      }
    },
    {
      "node_id": "validate",
      "node_type": "technique",
      "config": {
        "technique_id": "blind_spots"
      }
    },
    {
      "node_id": "end",
      "node_type": "output"
    }
  ],
  "edges": [
    {"from_node": "start", "from_port": "topic", "to_node": "research", "to_port": "input"},
    {"from_node": "research", "from_port": "output", "to_node": "validate", "to_port": "input"},
    {"from_node": "validate", "from_port": "output", "to_node": "end", "to_port": "result"}
  ]
}
```

### Execute It

```python
from src.core.orchestrator import Orchestrator
from pathlib import Path

# Initialize orchestrator
orchestrator = Orchestrator(config_dir=Path("config"))

# Load and execute DAG
dag = orchestrator.load_dag_from_json(Path("config/pipelines/simple_research.json"))

result = orchestrator.execute_dag(
    dag=dag,
    inputs={
        "topic": "Machine Learning Applications",
        "depth": "comprehensive"
    }
)

print(result["outputs"])  # See results
print(result["execution_graph"])  # See execution timeline
```

---

## Step 1: Create Pipeline Module

### New File: `src/core/pipeline.py`

```python
"""Node-based pipeline execution system."""

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class NodeType(Enum):
    """Supported node types."""
    INPUT = "input"
    OUTPUT = "output"
    AGENT = "agent"
    TECHNIQUE = "technique"
    MODEL = "model"
    CONDITION = "condition"
    LOOP = "loop"
    MERGE = "merge"


@dataclass
class NodePort:
    """Input/output port for a node."""
    port_name: str
    data_type: str = "any"
    required: bool = True
    source_node: Optional[str] = None
    source_port: Optional[str] = None


@dataclass
class PipelineNode(ABC):
    """Base class for all node types."""
    node_id: str
    node_type: str
    config: Dict[str, Any] = field(default_factory=dict)
    inputs: List[NodePort] = field(default_factory=list)
    outputs: List[NodePort] = field(default_factory=list)
    on_fail: str = "stop"  # stop | continue | skip
    
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute node and return output."""
        pass


@dataclass
class InputNode(PipelineNode):
    """Pipeline input node."""
    node_type: str = "input"
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        # Return input variables
        return {var: input_data.get(var) for var in self.config.get("variables", [])}


@dataclass
class OutputNode(PipelineNode):
    """Pipeline output node."""
    node_type: str = "output"
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        # Just pass through
        return input_data


@dataclass
class AgentNode(PipelineNode):
    """Execute task with specific agent."""
    node_type: str = "agent"
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        from src.core.agent import Task
        
        orchestrator = self.config.get("_orchestrator")
        agent_id = self.config["agent_id"]
        
        if not orchestrator or agent_id not in orchestrator.agents:
            raise ValueError(f"Agent not found: {agent_id}")
        
        agent = orchestrator.agents[agent_id]
        
        # Build task
        task_template = self.config.get("task_template", "")
        task_description = task_template.format(**input_data)
        
        task = Task(
            task_id=self.node_id,
            description=task_description,
            inputs=input_data,
            temperature=self.config.get("temperature"),
            max_tokens=self.config.get("max_tokens", 2048)
        )
        
        # Execute
        output = agent.execute_task(task)
        
        return {
            "output": output.output,
            "success": output.success,
            "error": output.error,
            "metadata": output.metadata
        }


@dataclass
class TechniqueNode(PipelineNode):
    """Apply research technique."""
    node_type: str = "technique"
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        from src.core.framework_loader import FrameworkLoader
        from src.core.agent import Task
        
        orchestrator = self.config.get("_orchestrator")
        technique_id = self.config["technique_id"]
        
        # Load technique
        loader = FrameworkLoader()
        technique = loader.load_technique(technique_id)
        
        # Find agent with matching role
        agent = None
        for a in orchestrator.agents.values():
            if a.role == technique.agent_role:
                agent = a
                break
        
        if not agent:
            raise ValueError(f"No agent for role: {technique.agent_role}")
        
        # Build task from technique
        task_description = technique.prompt.format(**input_data)
        
        task = Task(
            task_id=self.node_id,
            description=task_description,
            technique=technique_id,
            inputs=input_data,
            temperature=technique.temperature,
            max_tokens=technique.max_tokens
        )
        
        # Execute
        output = agent.execute_task(task)
        
        return {
            "output": output.output,
            "success": output.success,
            "metadata": output.metadata
        }


@dataclass
class ConditionNode(PipelineNode):
    """Conditional branching."""
    node_type: str = "condition"
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        condition = self.config["condition"]
        
        try:
            namespace = {"__builtins__": {}, **input_data}
            result = eval(condition, namespace)
        except Exception as e:
            logger.warning(f"Condition eval failed: {e}")
            result = False
        
        return {
            "branch": "true" if result else "false",
            "condition_result": result
        }


@dataclass
class MergeNode(PipelineNode):
    """Merge parallel outputs."""
    node_type: str = "merge"
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        strategy = self.config.get("merge_strategy", "combine")
        
        if strategy == "combine":
            # Merge all inputs
            return {"merged": input_data}
        elif strategy == "first_success":
            # Return first successful input
            for key, value in input_data.items():
                if isinstance(value, dict) and value.get("success", True):
                    return value
        
        return {"output": input_data}


@dataclass
class NodeConnection:
    """Edge connecting two nodes."""
    from_node: str
    from_port: str
    to_node: str
    to_port: str


@dataclass
class PipelineDAG:
    """Complete node-based pipeline (DAG)."""
    pipeline_id: str
    nodes: Dict[str, PipelineNode]
    edges: List[NodeConnection]
    entry_point: str = "input"
    exit_points: List[str] = field(default_factory=lambda: ["output"])
    
    def validate(self) -> Tuple[bool, List[str]]:
        """Validate DAG structure."""
        errors = []
        
        # Check entry point
        if self.entry_point not in self.nodes:
            errors.append(f"Entry point not found: {self.entry_point}")
        
        # Check exit points
        for exit_point in self.exit_points:
            if exit_point not in self.nodes:
                errors.append(f"Exit point not found: {exit_point}")
        
        # Check edges
        for edge in self.edges:
            if edge.from_node not in self.nodes:
                errors.append(f"Edge from unknown node: {edge.from_node}")
            if edge.to_node not in self.nodes:
                errors.append(f"Edge to unknown node: {edge.to_node}")
        
        # Check for cycles
        if self._has_cycle():
            errors.append("DAG contains cycle")
        
        return (len(errors) == 0, errors)
    
    def _has_cycle(self) -> bool:
        """Detect cycles using DFS."""
        # Build adjacency list
        graph = {node_id: [] for node_id in self.nodes}
        for edge in self.edges:
            graph[edge.from_node].append(edge.to_node)
        
        # DFS
        visited = set()
        rec_stack = set()
        
        def dfs(node):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        for node in self.nodes:
            if node not in visited:
                if dfs(node):
                    return True
        
        return False


@dataclass
class NodeExecution:
    """Record of node execution."""
    node_id: str
    status: str  # success | failed | skipped
    result: Dict[str, Any]
    duration_ms: float = 0


@dataclass
class PipelineResult:
    """Result from pipeline execution."""
    pipeline_id: str
    status: str  # completed | failed
    outputs: Dict[str, Any]
    execution_graph: Dict[str, NodeExecution]


class PipelineExecutor:
    """Execute node-based pipelines."""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.logger = logging.getLogger("pipeline_executor")
    
    async def execute(
        self,
        dag: PipelineDAG,
        inputs: Dict[str, Any],
        timeout: int = 3600
    ) -> PipelineResult:
        """Execute a DAG."""
        self.logger.info(f"Executing DAG: {dag.pipeline_id}")
        
        # Validate
        valid, errors = dag.validate()
        if not valid:
            raise ValueError(f"Invalid DAG: {errors}")
        
        # Topological sort
        exec_order = self._topological_sort(dag)
        
        # Execute nodes
        node_results = {}
        exec_graph = {}
        
        for node_id in exec_order:
            node = dag.nodes[node_id]
            
            # Gather inputs
            node_inputs = self._gather_inputs(node, dag, node_results, inputs)
            
            # Inject orchestrator reference
            if hasattr(node, 'config'):
                node.config["_orchestrator"] = self.orchestrator
            
            # Execute
            try:
                result = await asyncio.wait_for(
                    node.execute(node_inputs),
                    timeout=timeout
                )
                node_results[node_id] = result
                
                exec_graph[node_id] = NodeExecution(
                    node_id=node_id,
                    status="success",
                    result=result
                )
            
            except Exception as e:
                self.logger.error(f"Node {node_id} failed: {e}")
                
                if node.on_fail == "stop":
                    raise
                
                node_results[node_id] = {
                    "error": str(e),
                    "success": False
                }
        
        # Collect outputs
        final_outputs = {}
        for exit_node_id in dag.exit_points:
            final_outputs[exit_node_id] = node_results.get(exit_node_id, {})
        
        return PipelineResult(
            pipeline_id=dag.pipeline_id,
            status="completed",
            outputs=final_outputs,
            execution_graph=exec_graph
        )
    
    def _topological_sort(self, dag: PipelineDAG) -> List[str]:
        """Topologically sort nodes."""
        graph = {node_id: [] for node_id in dag.nodes}
        in_degree = {node_id: 0 for node_id in dag.nodes}
        
        for edge in dag.edges:
            graph[edge.from_node].append(edge.to_node)
            in_degree[edge.to_node] += 1
        
        queue = [nid for nid, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            node_id = queue.pop(0)
            result.append(node_id)
            
            for neighbor in graph[node_id]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        return result
    
    def _gather_inputs(
        self,
        node: PipelineNode,
        dag: PipelineDAG,
        node_results: Dict[str, Any],
        pipeline_inputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Gather inputs for a node."""
        inputs = {}
        
        # Find edges feeding into this node
        for edge in dag.edges:
            if edge.to_node == node.node_id:
                if edge.from_node == "pipeline":
                    inputs[edge.to_port] = pipeline_inputs.get(edge.from_port)
                else:
                    source_result = node_results.get(edge.from_node, {})
                    inputs[edge.to_port] = source_result.get(edge.from_port)
        
        return inputs
```

---

## Step 2: Add to Orchestrator

### Modify: `src/core/orchestrator.py`

```python
# In Orchestrator.__init__():
def __init__(self, ...):
    # ... existing code ...
    
    # ADD: Initialize pipeline executor
    from src.core.pipeline import PipelineExecutor
    self.pipeline_executor = PipelineExecutor(self)
    self.logger.info("PipelineExecutor initialized")


# ADD: New methods
def load_dag_from_json(self, dag_path: Path) -> 'PipelineDAG':
    """Load DAG from JSON file."""
    from src.core.pipeline import PipelineDAG
    
    config = JSONLoader.load(dag_path)
    dag = self._parse_dag_config(config)
    
    # Validate
    valid, errors = dag.validate()
    if not valid:
        raise ValueError(f"Invalid DAG: {errors}")
    
    return dag


def execute_dag(
    self,
    dag: 'PipelineDAG',
    inputs: Dict[str, Any]
) -> Dict[str, Any]:
    """Execute a node-based pipeline."""
    import asyncio
    
    self.logger.info(f"Executing DAG: {dag.pipeline_id}")
    
    result = asyncio.run(
        self.pipeline_executor.execute(dag, inputs)
    )
    
    return {
        "status": result.status,
        "outputs": result.outputs,
        "execution_graph": {
            node_id: {
                "status": exec.status,
                "result": exec.result
            }
            for node_id, exec in result.execution_graph.items()
        }
    }


def _parse_dag_config(self, config: Dict) -> 'PipelineDAG':
    """Parse DAG config into PipelineDAG object."""
    from src.core.pipeline import (
        PipelineDAG, InputNode, OutputNode, AgentNode,
        TechniqueNode, ConditionNode, MergeNode,
        NodeConnection
    )
    
    nodes = {}
    
    # Parse nodes
    for node_config in config.get("nodes", []):
        node_type = node_config["node_type"]
        node_id = node_config["node_id"]
        
        # Create appropriate node type
        if node_type == "input":
            node = InputNode(
                node_id=node_id,
                config=node_config.get("config", {})
            )
        elif node_type == "output":
            node = OutputNode(
                node_id=node_id,
                config=node_config.get("config", {})
            )
        elif node_type == "agent":
            node = AgentNode(
                node_id=node_id,
                config=node_config.get("config", {})
            )
        elif node_type == "technique":
            node = TechniqueNode(
                node_id=node_id,
                config=node_config.get("config", {})
            )
        elif node_type == "condition":
            node = ConditionNode(
                node_id=node_id,
                config=node_config.get("config", {})
            )
        elif node_type == "merge":
            node = MergeNode(
                node_id=node_id,
                config=node_config.get("config", {})
            )
        else:
            raise ValueError(f"Unknown node type: {node_type}")
        
        nodes[node_id] = node
    
    # Parse edges
    edges = [
        NodeConnection(
            from_node=edge["from_node"],
            from_port=edge["from_port"],
            to_node=edge["to_node"],
            to_port=edge["to_port"]
        )
        for edge in config.get("edges", [])
    ]
    
    # Create DAG
    return PipelineDAG(
        pipeline_id=config["pipeline_id"],
        nodes=nodes,
        edges=edges,
        entry_point=config.get("entry_point", "input"),
        exit_points=config.get("exit_points", ["output"])
    )
```

---

## Step 3: Configuration Schema

### New File: `config/schemas/pipeline_schema.json`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Pipeline DAG Schema",
  "description": "Schema for node-based pipeline definitions",
  "type": "object",
  "required": ["pipeline_id", "nodes", "edges"],
  "properties": {
    "pipeline_id": {
      "type": "string",
      "description": "Unique pipeline identifier"
    },
    "name": {
      "type": "string"
    },
    "description": {
      "type": "string"
    },
    "entry_point": {
      "type": "string",
      "default": "input"
    },
    "exit_points": {
      "type": "array",
      "items": {"type": "string"},
      "default": ["output"]
    },
    "nodes": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["node_id", "node_type"],
        "properties": {
          "node_id": {"type": "string"},
          "node_type": {
            "type": "string",
            "enum": ["input", "output", "agent", "technique", "model", "condition", "loop", "merge"]
          },
          "config": {"type": "object"},
          "on_fail": {
            "type": "string",
            "enum": ["stop", "continue", "skip"],
            "default": "stop"
          }
        }
      }
    },
    "edges": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["from_node", "from_port", "to_node", "to_port"],
        "properties": {
          "from_node": {"type": "string"},
          "from_port": {"type": "string"},
          "to_node": {"type": "string"},
          "to_port": {"type": "string"}
        }
      }
    }
  }
}
```

---

## Step 4: Example DAGs

### Create Directory

```bash
mkdir -p config/pipelines
```

### Example 1: Simple Research (`config/pipelines/simple_research.json`)

See Quick Start Example above.

### Example 2: Parallel Validation (`config/pipelines/parallel_validation.json`)

```json
{
  "pipeline_id": "parallel_validation",
  "name": "Parallel Validation Pipeline",
  "description": "Research with parallel validation paths",
  "nodes": [
    {"node_id": "input", "node_type": "input", "config": {"variables": ["topic"]}},
    {
      "node_id": "research",
      "node_type": "agent",
      "config": {
        "agent_id": "fast_researcher",
        "task_template": "Research: {topic}"
      }
    },
    {
      "node_id": "validate_gaps",
      "node_type": "technique",
      "config": {"technique_id": "blind_spots"}
    },
    {
      "node_id": "validate_contradictions",
      "node_type": "technique",
      "config": {"technique_id": "contradiction"}
    },
    {
      "node_id": "merge",
      "node_type": "merge",
      "config": {"merge_strategy": "combine"}
    },
    {"node_id": "output", "node_type": "output"}
  ],
  "edges": [
    {"from_node": "input", "from_port": "topic", "to_node": "research", "to_port": "input"},
    {"from_node": "research", "from_port": "output", "to_node": "validate_gaps", "to_port": "input"},
    {"from_node": "research", "from_port": "output", "to_node": "validate_contradictions", "to_port": "input"},
    {"from_node": "validate_gaps", "from_port": "output", "to_node": "merge", "to_port": "path1"},
    {"from_node": "validate_contradictions", "from_port": "output", "to_node": "merge", "to_port": "path2"},
    {"from_node": "merge", "from_port": "merged", "to_node": "output", "to_port": "result"}
  ]
}
```

---

## Testing

### Unit Test: `tests/test_pipeline.py`

```python
import pytest
from pathlib import Path
from src.core.orchestrator import Orchestrator
from src.core.pipeline import PipelineDAG, InputNode, OutputNode


@pytest.fixture
def orchestrator():
    return Orchestrator(config_dir=Path("config"))


def test_simple_pipeline(orchestrator):
    """Test simple 3-node pipeline."""
    # Load DAG
    dag = orchestrator.load_dag_from_json(
        Path("config/pipelines/simple_research.json")
    )
    
    # Validate
    valid, errors = dag.validate()
    assert valid, f"DAG validation failed: {errors}"
    
    # Execute
    result = orchestrator.execute_dag(
        dag=dag,
        inputs={"topic": "AI", "depth": "basic"}
    )
    
    assert result["status"] == "completed"
    assert "output" in result["outputs"]


def test_dag_validation():
    """Test DAG validation."""
    from src.core.pipeline import PipelineDAG, InputNode, OutputNode, NodeConnection
    
    # Valid DAG
    dag = PipelineDAG(
        pipeline_id="test",
        nodes={
            "input": InputNode(node_id="input"),
            "output": OutputNode(node_id="output")
        },
        edges=[
            NodeConnection(
                from_node="input",
                from_port="data",
                to_node="output",
                to_port="data"
            )
        ]
    )
    
    valid, errors = dag.validate()
    assert valid


def test_cycle_detection():
    """Test cycle detection in DAG."""
    from src.core.pipeline import PipelineDAG, InputNode, NodeConnection
    
    # DAG with cycle
    node1 = InputNode(node_id="node1")
    node2 = InputNode(node_id="node2")
    
    dag = PipelineDAG(
        pipeline_id="cyclic",
        nodes={"node1": node1, "node2": node2},
        edges=[
            NodeConnection("node1", "out", "node2", "in"),
            NodeConnection("node2", "out", "node1", "in")  # Cycle!
        ]
    )
    
    valid, errors = dag.validate()
    assert not valid
    assert any("cycle" in e.lower() for e in errors)
```

---

## Usage Examples

### Example 1: Execute DAG from API

```python
from fastapi import FastAPI
from src.core.orchestrator import Orchestrator
from pathlib import Path

app = FastAPI()
orchestrator = Orchestrator()

@app.post("/pipelines/{pipeline_id}/execute")
async def execute_pipeline(pipeline_id: str, inputs: dict):
    """Execute a pipeline."""
    dag_path = Path(f"config/pipelines/{pipeline_id}.json")
    
    if not dag_path.exists():
        return {"error": f"Pipeline not found: {pipeline_id}"}
    
    try:
        dag = orchestrator.load_dag_from_json(dag_path)
        result = orchestrator.execute_dag(dag, inputs)
        return result
    except Exception as e:
        return {"error": str(e)}
```

### Example 2: CLI Interface

```python
# cli.py
import click
from pathlib import Path
from src.core.orchestrator import Orchestrator
import json

@click.command()
@click.argument("pipeline_id")
@click.option("--input", "-i", multiple=True, help="Input: key=value")
@click.option("--config", "-c", default="config", help="Config directory")
def execute(pipeline_id, input, config):
    """Execute a pipeline."""
    orchestrator = Orchestrator(config_dir=Path(config))
    
    # Parse inputs
    inputs = {k: v for k, v in [i.split("=") for i in input]}
    
    # Load and execute
    dag_path = Path(config) / "pipelines" / f"{pipeline_id}.json"
    dag = orchestrator.load_dag_from_json(dag_path)
    result = orchestrator.execute_dag(dag, inputs)
    
    # Output
    click.echo(json.dumps(result, indent=2))

if __name__ == "__main__":
    execute()
```

Usage:
```bash
python cli.py simple_research --input topic="AI" --input depth="comprehensive"
```

---

## Checklist for Implementation

- [ ] **Module Creation** - Create `src/core/pipeline.py` with all node types
- [ ] **Orchestrator Integration** - Add methods and initialize PipelineExecutor
- [ ] **Configuration** - Create pipeline schema and example DAGs
- [ ] **Testing** - Unit tests for nodes, DAG validation, execution
- [ ] **Documentation** - Update README with pipeline examples
- [ ] **Migration** - Convert existing workflows to DAGs
- [ ] **Performance** - Benchmark against traditional workflows

---

## Next Steps

1. Copy the pipeline.py code above
2. Add methods to orchestrator.py
3. Create config/schemas/pipeline_schema.json
4. Test with simple_research.json
5. Run unit tests
6. Iterate on node types based on feedback

