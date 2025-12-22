# Deep Research Orchestrator - Architecture Plan V2

**Date:** 2025-12-21
**Version:** 2.0 (User-Reviewed & Adjusted)
**Status:** FINAL - Ready for Implementation

---

## Table of Contents

1. [User Feedback Integration](#1-user-feedback-integration)
2. [Core Architecture](#2-core-architecture)
3. [Model Strategy (llama.cpp)](#3-model-strategy-llamacpp)
4. [Multi-AI Workflow](#4-multi-ai-workflow-manual-orchestration)
5. [Knowledge Graphs & Tree-of-Thought](#5-knowledge-graphs--tree-of-thought)
6. [Project Structure](#6-project-structure)
7. [Migration Strategy](#7-migration-strategy)
8. [Implementation Phases](#8-implementation-phases)
9. [Existing Assets to Preserve](#9-existing-assets-to-preserve)

---

## 1. User Feedback Integration

### Key Decisions (User Input)

**A. Framework Approach**
- ❌ No external dependencies (CrewAI, smolagents)
- ✅ Custom implementation, learn from their patterns
- ✅ LangGraph: Later iterations only (when conditional workflows needed)
- ✅ Full control over all components

**B. Model Backend**
- ✅ **llama.cpp** (not Ollama) for better VRAM/RAM splitting control
- ✅ Two-tier strategy:
  - **Tier 1**: Fast model (fully in VRAM, ~8GB)
  - **Tier 2**: Maximum quality model (VRAM+RAM split, ~27GB total)
- ✅ Both abliterated for unbiased research

**C. Migration Approach**
- ✅ Fresh start with clean structure
- ✅ Migrate existing components incrementally
- ✅ Preserve existing GUI (gui/app.py) for later evolution

**D. GUI Priority**
- ✅ Minimal GUI now (API-first)
- ✅ Use existing GUI (gui/app.py) as-is
- ✅ Enhance GUI later once functionality is solid

**E. Development Priority**
- ⭐ **Priority 1**: Iterative workflows
- ⭐ **Priority 2**: Multi-agent system
- ⭐ **Priority 3**: GUI enhancements (later)

---

### Missing Concepts from Product Management Docs

**1. Multi-AI Prompt Orchestration (Manual Workflow)**
```
User generates ONE big prompt
  ↓
Paste to Claude, GPT-4, Gemini (manually)
  ↓
Save responses to research-data/multi-ai/
  ↓
Local analysis with abliterated model
  ↓
Synthesize findings + detect contradictions
```

**2. Knowledge Graphs**
- Extract entities and relationships from research
- Build graph structures for complex domains
- Query graphs for insights

**3. Tree-of-Thought (ToT)**
- Multi-path reasoning exploration
- Branch evaluation and pruning
- Best path selection

**4. Large Model Quality Analysis**
- Analyze patterns in Claude/GPT outputs over time
- Learn what makes high-quality responses
- Feed insights back into prompts

---

## 2. Core Architecture

### High-Level System Design

```
┌─────────────────────────────────────────────────────────┐
│  USER LAYER                                             │
│  - Manual prompt creation                               │
│  - External AI queries (Claude, GPT, Gemini)            │
│  - GUI (minimal, existing gui/app.py)                   │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  ORCHESTRATION LAYER                                    │
│  - Master Orchestrator (GPT-Researcher pattern)         │
│  - Workflow Engine (Iterative + Sequential)             │
│  - Task Dispatcher                                      │
│  - State Manager (planning_state.json)                  │
└─────────────────────────────────────────────────────────┘
                         ↓
        ┌────────────────┴─────────────────┐
        ↓                                   ↓
┌──────────────────┐              ┌──────────────────┐
│  Fast Agent      │              │  Quality Agent   │
│  (8B Abliterated)│              │  (32B+ Abliterated)│
│  - Research      │              │  - Validation    │
│  - Summarization │              │  - Synthesis     │
│  - Quick Tasks   │              │  - Deep Reasoning│
└──────────────────┘              └──────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  TOOL LIBRARY                                           │
│  - Data Collection: web_scraper, pdf_extractor          │
│  - Validation: contradiction, blind_spots, premortem    │
│  - Processing: text_cleaner, structurer, summarizer     │
│  - Knowledge: graph_builder, tot_explorer               │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  LLM BACKEND (llama.cpp)                                │
│  - Fast: Llama-3.1-8B-Abliterated (VRAM only)           │
│  - Quality: 32B+ Abliterated (VRAM+RAM split)           │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  STORAGE LAYER                                          │
│  - research-data/ (Multi-AI responses, validations)     │
│  - knowledge-graphs/ (Entity-relationship graphs)       │
│  - planning_state.json (Progress tracking)              │
└─────────────────────────────────────────────────────────┘
```

---

### Component Breakdown

#### 1. Orchestrator (Custom, GPT-Researcher Inspired)

**Role:** Master coordinator for all research workflows

```python
class Orchestrator:
    """Master agent coordinating all research activities."""

    def __init__(self):
        self.workflow_engine = WorkflowEngine()
        self.state_manager = StateManager()
        self.llm_fast = LlamaCppClient(model="tier1_fast")
        self.llm_quality = LlamaCppClient(model="tier2_quality")

    def execute_workflow(self, workflow_id: str, inputs: dict):
        """Execute a workflow with iterative refinement."""
        workflow = self.workflow_engine.load(workflow_id)

        if workflow.mode == "iterative":
            return self._execute_iterative(workflow, inputs)
        else:
            return self._execute_sequential(workflow, inputs)

    def _execute_iterative(self, workflow, inputs):
        """Iterative execution with gap detection and refinement."""
        iteration = 0
        confidence = 0.0

        while iteration < workflow.max_iterations:
            # Execute workflow steps
            results = self.workflow_engine.run_steps(workflow.steps, inputs)

            # Evaluate confidence
            confidence = self._evaluate_confidence(results)

            # Check exit criteria
            if confidence >= workflow.exit_threshold:
                break

            # Identify gaps and refine
            gaps = self._identify_gaps(results)
            inputs = self._refine_inputs(inputs, gaps)

            iteration += 1

        return {
            "results": results,
            "confidence": confidence,
            "iterations": iteration
        }
```

---

#### 2. Agent System (Role-Based, CrewAI Pattern)

**No external dependencies - custom implementation**

```python
@dataclass
class Agent:
    """Autonomous agent with specific role and capabilities."""

    agent_id: str
    role: str  # "researcher", "validator", "synthesizer"
    llm_client: LlamaCppClient
    tools: List[Tool]
    system_prompt: str

    def execute_task(self, task: Task) -> AgentOutput:
        """Execute a task using available tools."""
        # Apply system prompt
        full_prompt = self._build_prompt(task)

        # Generate response
        response = self.llm_client.generate(
            prompt=full_prompt,
            temperature=task.temperature
        )

        # Apply tools if needed
        if task.requires_tools:
            response = self._apply_tools(response, task)

        return AgentOutput(
            agent_id=self.agent_id,
            task_id=task.task_id,
            output=response,
            metadata={"timestamp": datetime.now()}
        )
```

**Agent Configuration (JSON):**
```json
{
  "agent_id": "fast_researcher",
  "role": "researcher",
  "model_tier": "tier1_fast",
  "tools": ["web_scraper", "pdf_extractor", "text_cleaner"],
  "system_prompt_template": "anti_eliza_researcher",
  "temperature": 0.3,
  "description": "Fast research agent for data collection"
}
```

---

#### 3. Workflow Engine (Enhanced with Iterative Mode)

**Sequential Mode (Existing):**
```json
{
  "workflow_id": "research_validation",
  "mode": "sequential",
  "steps": [
    {"technique": "contradiction"},
    {"technique": "blind_spots"},
    {"technique": "premortem"}
  ]
}
```

**Iterative Mode (NEW):**
```json
{
  "workflow_id": "deep_research",
  "mode": "iterative",
  "max_iterations": 5,
  "exit_criteria": {
    "type": "confidence_threshold",
    "threshold": 0.8
  },
  "steps": [
    {
      "step": 1,
      "agent": "fast_researcher",
      "task": "collect_data",
      "output_key": "raw_data"
    },
    {
      "step": 2,
      "agent": "quality_validator",
      "task": "evaluate_quality",
      "input": "raw_data",
      "output_key": "evaluation"
    },
    {
      "step": 3,
      "condition": "evaluation.confidence < 0.8",
      "agent": "quality_validator",
      "task": "identify_gaps",
      "output_key": "gaps"
    },
    {
      "step": 4,
      "condition": "gaps exists",
      "agent": "fast_researcher",
      "task": "refine_research",
      "input": "gaps",
      "loop_to": 1
    }
  ]
}
```

---

#### 4. Tool System (Custom @tool decorator)

**Inspired by smolagents, but custom:**

```python
from functools import wraps
from typing import Callable, Any

class ToolRegistry:
    """Registry for all available tools."""
    _tools = {}

    @classmethod
    def register(cls, func: Callable) -> Callable:
        """Register a tool."""
        cls._tools[func.__name__] = func
        return func

    @classmethod
    def get(cls, tool_name: str) -> Callable:
        """Retrieve a tool by name."""
        return cls._tools.get(tool_name)

def tool(description: str = None):
    """Decorator to register a function as a tool."""
    def decorator(func: Callable) -> Callable:
        func.is_tool = True
        func.tool_description = description or func.__doc__
        ToolRegistry.register(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper
    return decorator


# Example usage:

@tool("Search the web for information")
def web_search(query: str, max_results: int = 10) -> list:
    """
    Search the web and return results.

    Args:
        query: Search query
        max_results: Maximum number of results

    Returns:
        List of search results with title, url, snippet
    """
    from src.sources.web_scraper import WebScraper
    scraper = WebScraper()
    return scraper.search(query, max_results)


@tool("Detect contradictions between multiple texts")
def contradiction_detector(texts: list[str]) -> dict:
    """
    Analyze multiple texts for contradictions.

    Args:
        texts: List of text passages to analyze

    Returns:
        Dict with contradictions, severity levels, resolutions
    """
    # Use Quality Agent for deep analysis
    from src.core.orchestrator import get_quality_agent
    agent = get_quality_agent()

    prompt = f"""Analyze these texts for contradictions:

    {'\n\n---\n\n'.join(texts)}

    Output JSON with: contradictions (list), severity (CRITICAL/MODERATE/MINOR), resolution_steps (list)
    """

    response = agent.llm_client.generate(prompt)
    return json.loads(response)
```

---

## 3. Model Strategy (llama.cpp)

### Why llama.cpp over Ollama?

**Advantages:**
- ✅ Fine-grained control over VRAM/RAM split (`--n-gpu-layers`)
- ✅ Better performance with large models on mixed memory
- ✅ Direct model loading (no daemon required)
- ✅ More transparent resource usage

**Disadvantages:**
- ⚠️ More manual setup (no auto-download)
- ⚠️ Lower-level API (more code needed)

### Hardware Configuration

**Your System:**
- GPU VRAM: 11GB (RTX 2080 Ti / RTX 3060)
- System RAM: 16GB
- Total Available: 27GB

### Model Tiers

#### Tier 1: Fast Agent (Fully in VRAM)

**Model:** Llama-3.1-8B-Instruct-Abliterated
**Quantization:** Q6_K (best quality for 8B)
**Size:** ~7GB
**VRAM:** 7GB (fully in GPU)
**Speed:** 50-80 tok/s

**llama.cpp Command:**
```bash
./llama-cli \
  --model models/Llama-3.1-8B-Instruct-Abliterated-Q6_K.gguf \
  --n-gpu-layers 999 \  # All layers on GPU
  --ctx-size 4096 \
  --threads 4
```

**Use Cases:**
- Web research
- PDF extraction
- Text summarization
- Quick validation tasks

---

#### Tier 2: Quality Agent (VRAM + RAM Split)

**Model Options (choose based on availability):**

**Option A: Qwen2.5-32B-Instruct-Abliterated** (Recommended)
- Quantization: Q4_K_M
- Size: ~20GB
- VRAM: 11GB (~16 layers)
- RAM: ~9GB (remaining layers)
- Speed: 3-8 tok/s
- Quality: Excellent reasoning

**Option B: Llama-3.1-70B-Instruct-Abliterated** (Maximum Quality)
- Quantization: Q3_K_M (aggressive to fit)
- Size: ~27GB
- VRAM: 11GB (~12 layers)
- RAM: ~16GB (remaining layers)
- Speed: 1-3 tok/s
- Quality: Best possible

**llama.cpp Command (Option A - Qwen 32B):**
```bash
./llama-cli \
  --model models/Qwen2.5-32B-Instruct-Abliterated-Q4_K_M.gguf \
  --n-gpu-layers 16 \  # ~11GB VRAM, rest in RAM
  --ctx-size 8192 \
  --threads 8
```

**Use Cases:**
- Deep validation (contradiction, blind spots)
- Research synthesis
- Premortem analysis
- Complex reasoning tasks

---

### Model Selection Logic

```python
class ModelSelector:
    """Selects appropriate model based on task requirements."""

    TASK_MODEL_MAP = {
        "research": "tier1_fast",
        "summarize": "tier1_fast",
        "extract": "tier1_fast",
        "validate": "tier2_quality",
        "synthesize": "tier2_quality",
        "reason": "tier2_quality"
    }

    @classmethod
    def select_model(cls, task_type: str, priority: str = "auto") -> str:
        """
        Select model tier based on task.

        Args:
            task_type: Type of task (research, validate, etc.)
            priority: "fast", "quality", or "auto"

        Returns:
            Model tier ID
        """
        if priority == "fast":
            return "tier1_fast"
        elif priority == "quality":
            return "tier2_quality"
        else:  # auto
            return cls.TASK_MODEL_MAP.get(task_type, "tier1_fast")
```

---

### llama.cpp Python Integration

**Client Implementation:**
```python
import subprocess
import json
from pathlib import Path

class LlamaCppClient:
    """Client for llama.cpp inference."""

    def __init__(self, model_path: Path, n_gpu_layers: int = 999):
        self.model_path = model_path
        self.n_gpu_layers = n_gpu_layers
        self.llama_cli = Path("./llama.cpp/llama-cli")

    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        system_prompt: str = None
    ) -> str:
        """Generate text using llama.cpp."""

        # Build full prompt
        if system_prompt:
            full_prompt = f"<s>[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n\n{prompt} [/INST]"
        else:
            full_prompt = f"<s>[INST] {prompt} [/INST]"

        # Build command
        cmd = [
            str(self.llama_cli),
            "--model", str(self.model_path),
            "--n-gpu-layers", str(self.n_gpu_layers),
            "--prompt", full_prompt,
            "--temp", str(temperature),
            "--n-predict", str(max_tokens),
            "--ctx-size", "4096"
        ]

        # Execute
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        return result.stdout.strip()

    def health_check(self) -> bool:
        """Check if llama.cpp is available."""
        return self.llama_cli.exists() and self.model_path.exists()
```

**Configuration (JSON):**
```json
{
  "model_id": "tier1_fast",
  "name": "Llama-3.1-8B-Abliterated",
  "path": "models/Llama-3.1-8B-Instruct-Abliterated-Q6_K.gguf",
  "n_gpu_layers": 999,
  "ctx_size": 4096,
  "temperature": 0.3,
  "agent_role": "researcher"
}
```

---

## 4. Multi-AI Workflow (Manual Orchestration)

### Concept from Product Management Docs

**Problem:** Want to leverage large commercial models (Claude, GPT-4) without API costs

**Solution:** Manual prompt orchestration with local analysis

### Workflow

```
Step 1: Prompt Creation (Local Tool)
  ↓
  Tool generates comprehensive research prompt
  Output: research-prompts/prompt_20250121_1430.md

Step 2: Manual Multi-AI Querying (User)
  ↓
  User copies prompt to:
  - Claude (Anthropic)
  - GPT-4 (OpenAI)
  - Gemini (Google)

  User saves responses to:
  - research-data/multi-ai/claude_response.md
  - research-data/multi-ai/gpt4_response.md
  - research-data/multi-ai/gemini_response.md

Step 3: Local Analysis (Automated)
  ↓
  Quality Agent (32B Abliterated) analyzes all responses:
  - Detect contradictions
  - Find blind spots
  - Identify consensus
  - Generate synthesis

  Output: research-data/validations/synthesis_report.md

Step 4: Quality Pattern Learning (Optional)
  ↓
  Analyze response quality patterns across many prompts
  Extract what makes good responses
  Feed insights back into prompt generation
```

---

### Implementation

**A. Prompt Generator Tool**
```python
@tool("Generate comprehensive research prompt for multi-AI querying")
def generate_multi_ai_prompt(
    topic: str,
    research_categories: list[str],
    output_format: str = "markdown"
) -> dict:
    """
    Generate a detailed prompt for external AI services.

    Args:
        topic: Research topic
        research_categories: Categories to cover (e.g., market, tech, legal)
        output_format: Desired format of responses

    Returns:
        Dict with prompt text, metadata, save path
    """
    from src.tools.prompt_generator import MultiAIPromptGenerator

    generator = MultiAIPromptGenerator()
    prompt = generator.create_prompt(
        topic=topic,
        categories=research_categories,
        format=output_format
    )

    # Save prompt
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_path = Path(f"research-prompts/prompt_{timestamp}.md")
    save_path.parent.mkdir(exist_ok=True)
    save_path.write_text(prompt)

    return {
        "prompt": prompt,
        "save_path": str(save_path),
        "instructions": "Copy this prompt to Claude, GPT-4, and Gemini. Save responses to research-data/multi-ai/"
    }
```

**B. Multi-AI Analysis Tool**
```python
@tool("Analyze multiple AI responses for synthesis")
def analyze_multi_ai_responses(
    response_dir: Path,
    analysis_type: str = "comprehensive"
) -> dict:
    """
    Analyze responses from multiple AI services.

    Args:
        response_dir: Directory containing AI responses
        analysis_type: "quick" or "comprehensive"

    Returns:
        Analysis report with contradictions, synthesis, confidence
    """
    from src.core.orchestrator import get_quality_agent

    # Load all responses
    responses = {}
    for file in response_dir.glob("*.md"):
        ai_name = file.stem.replace("_response", "")
        responses[ai_name] = file.read_text()

    # Run analysis workflow
    agent = get_quality_agent()

    # Contradiction detection
    contradictions = agent.execute_task(Task(
        task_id="contradiction_detection",
        technique="contradiction",
        inputs={"responses": list(responses.values())}
    ))

    # Blind spot detection
    blind_spots = agent.execute_task(Task(
        task_id="blind_spot_detection",
        technique="blind_spots",
        inputs={"responses": list(responses.values())}
    ))

    # Synthesis
    synthesis = agent.execute_task(Task(
        task_id="synthesis",
        technique="synthesize",
        inputs={
            "responses": responses,
            "contradictions": contradictions,
            "blind_spots": blind_spots
        }
    ))

    return {
        "contradictions": contradictions,
        "blind_spots": blind_spots,
        "synthesis": synthesis,
        "confidence_score": _calculate_confidence(contradictions)
    }
```

**C. Quality Pattern Analyzer (Future)**
```python
@tool("Analyze quality patterns across multiple AI responses")
def analyze_response_quality_patterns(
    history_dir: Path,
    min_samples: int = 10
) -> dict:
    """
    Learn what makes high-quality AI responses by analyzing past data.

    Args:
        history_dir: Directory with historical multi-AI data
        min_samples: Minimum samples needed for pattern analysis

    Returns:
        Insights about response quality patterns
    """
    # Load historical data
    samples = _load_historical_samples(history_dir, min_samples)

    # Analyze patterns
    patterns = {
        "high_quality_indicators": [],
        "low_quality_indicators": [],
        "model_strengths": {},  # Which model excels at what
        "consensus_reliability": 0.0
    }

    # Use Quality Agent for analysis
    agent = get_quality_agent()

    for sample in samples:
        analysis = agent.analyze_quality(sample)
        patterns = _update_patterns(patterns, analysis)

    return patterns
```

---

## 5. Knowledge Graphs & Tree-of-Thought

### A. Knowledge Graph Builder

**Purpose:** Extract structured knowledge from unstructured research

**Implementation:**
```python
@tool("Build knowledge graph from research documents")
def build_knowledge_graph(
    documents: list[Path],
    entity_types: list[str] = None
) -> dict:
    """
    Extract entities and relationships to build knowledge graph.

    Args:
        documents: List of document paths
        entity_types: Types of entities to extract (Person, Company, Concept, etc.)

    Returns:
        Graph structure with nodes (entities) and edges (relationships)
    """
    from src.tools.knowledge_graph import KnowledgeGraphBuilder

    builder = KnowledgeGraphBuilder()

    # Extract entities from each document
    for doc in documents:
        text = doc.read_text()
        entities = builder.extract_entities(text, entity_types)
        relationships = builder.extract_relationships(text, entities)

        builder.add_entities(entities)
        builder.add_relationships(relationships)

    # Build graph
    graph = builder.build()

    # Save graph
    graph_path = Path("knowledge-graphs") / f"graph_{datetime.now():%Y%m%d_%H%M}.json"
    graph_path.parent.mkdir(exist_ok=True)
    builder.save(graph_path)

    return {
        "graph": graph,
        "node_count": len(graph["nodes"]),
        "edge_count": len(graph["edges"]),
        "save_path": str(graph_path)
    }
```

**Graph Structure:**
```json
{
  "nodes": [
    {
      "id": "ent_001",
      "type": "Company",
      "name": "OpenAI",
      "properties": {
        "founded": "2015",
        "industry": "AI Research"
      }
    },
    {
      "id": "ent_002",
      "type": "Product",
      "name": "GPT-4",
      "properties": {
        "release_date": "2023",
        "model_size": "unknown"
      }
    }
  ],
  "edges": [
    {
      "id": "rel_001",
      "source": "ent_001",
      "target": "ent_002",
      "type": "develops",
      "properties": {
        "confidence": 0.95
      }
    }
  ]
}
```

---

### B. Tree-of-Thought Explorer

**Purpose:** Multi-path reasoning with branch evaluation

**Implementation:**
```python
@tool("Explore multiple reasoning paths using Tree-of-Thought")
def tree_of_thought_explore(
    problem: str,
    num_paths: int = 3,
    max_depth: int = 4
) -> dict:
    """
    Generate and evaluate multiple reasoning paths.

    Args:
        problem: Problem statement
        num_paths: Number of parallel reasoning paths
        max_depth: Maximum depth of reasoning tree

    Returns:
        Best path, all paths, evaluation scores
    """
    from src.core.orchestrator import get_quality_agent

    agent = get_quality_agent()

    # Generate initial paths
    paths = []
    for i in range(num_paths):
        path = {
            "id": f"path_{i}",
            "steps": [],
            "score": 0.0
        }

        # Generate reasoning steps
        current_state = problem
        for depth in range(max_depth):
            step = agent.execute_task(Task(
                task_id=f"tot_step_{i}_{depth}",
                technique="reasoning_step",
                inputs={
                    "problem": problem,
                    "current_state": current_state,
                    "path_id": i
                }
            ))

            path["steps"].append(step)
            current_state = step["next_state"]

            # Evaluate step quality
            step_score = agent.execute_task(Task(
                task_id=f"tot_eval_{i}_{depth}",
                technique="evaluate_reasoning",
                inputs={"step": step}
            ))

            path["score"] += step_score["score"]

            # Prune if score too low
            if step_score["score"] < 0.3:
                break

        paths.append(path)

    # Select best path
    best_path = max(paths, key=lambda p: p["score"])

    return {
        "best_path": best_path,
        "all_paths": paths,
        "reasoning": best_path["steps"]
    }
```

---

## 6. Project Structure

### Clean Directory Layout

```
deep-research-orchestrator/
├── README.md
├── pyproject.toml                # Python dependencies
├── .env.example                  # llama.cpp paths, etc.
├── .gitignore
│
├── config/
│   ├── agents/                   # Agent definitions
│   │   ├── fast_researcher.json
│   │   └── quality_validator.json
│   │
│   ├── models/                   # Model configurations
│   │   ├── tier1_fast.json
│   │   └── tier2_quality.json
│   │
│   ├── workflows/                # Workflow definitions
│   │   ├── sequential/
│   │   │   ├── research_validation.json
│   │   │   └── planning_validation.json
│   │   └── iterative/
│   │       ├── deep_research.json
│   │       └── market_analysis.json
│   │
│   ├── techniques/               # Validation techniques
│   │   ├── contradiction.json
│   │   ├── blind_spots.json
│   │   ├── premortem.json
│   │   ├── consensus.json
│   │   ├── red_flags.json
│   │   ├── sanity_check.json
│   │   └── scenario_analysis.json
│   │
│   ├── tools/                    # Tool configurations
│   │   ├── web_scraper.json
│   │   ├── pdf_extractor.json
│   │   ├── contradiction_detector.json
│   │   ├── knowledge_graph_builder.json
│   │   └── tree_of_thought_explorer.json
│   │
│   └── schemas/                  # JSON schemas
│       ├── agent_schema.json
│       ├── workflow_schema.json
│       └── tool_schema.json
│
├── src/
│   ├── __init__.py
│   │
│   ├── core/                     # Core orchestration
│   │   ├── __init__.py
│   │   ├── orchestrator.py       # Master orchestrator
│   │   ├── agent.py              # Agent class
│   │   ├── task.py               # Task class
│   │   ├── workflow_engine.py    # Workflow executor
│   │   └── state_manager.py      # State tracking
│   │
│   ├── models/                   # LLM integration
│   │   ├── __init__.py
│   │   ├── llama_cpp_client.py   # llama.cpp integration
│   │   ├── model_loader.py       # Load model configs
│   │   └── prompt_templates.py   # Anti-ELIZA prompts
│   │
│   ├── tools/                    # All tools
│   │   ├── __init__.py
│   │   ├── base.py               # @tool decorator
│   │   │
│   │   ├── data_collection/      # Data gathering
│   │   │   ├── __init__.py
│   │   │   ├── web_scraper.py
│   │   │   ├── pdf_extractor.py
│   │   │   └── markdown_reader.py
│   │   │
│   │   ├── validation/           # Validation techniques
│   │   │   ├── __init__.py
│   │   │   ├── contradiction.py
│   │   │   ├── blind_spots.py
│   │   │   ├── premortem.py
│   │   │   ├── consensus.py
│   │   │   ├── red_flags.py
│   │   │   └── sanity_check.py
│   │   │
│   │   ├── processing/           # Data processing
│   │   │   ├── __init__.py
│   │   │   ├── text_cleaner.py
│   │   │   ├── structurer.py
│   │   │   └── summarizer.py
│   │   │
│   │   ├── knowledge/            # Advanced tools (NEW)
│   │   │   ├── __init__.py
│   │   │   ├── graph_builder.py
│   │   │   └── tot_explorer.py
│   │   │
│   │   └── multi_ai/             # Multi-AI workflows (NEW)
│   │       ├── __init__.py
│   │       ├── prompt_generator.py
│   │       └── response_analyzer.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── json_loader.py
│       ├── logger.py
│       └── validators.py
│
├── gui/                          # Existing GUI (preserve)
│   ├── app.py                    # Flask app (from old project)
│   ├── templates/
│   │   ├── index.html
│   │   ├── validate.html
│   │   ├── workflows.html
│   │   ├── chat.html
│   │   └── collect.html
│   └── static/
│       ├── css/
│       └── js/
│
├── docs/
│   ├── frameworks/               # Migrated frameworks
│   │   ├── research-framework.md
│   │   ├── validation-framework.md
│   │   └── planning-framework.md
│   ├── guides/
│   │   ├── quickstart.md
│   │   ├── llama-cpp-setup.md
│   │   └── multi-ai-workflow.md
│   └── architecture/
│       ├── ARCHITECTURE_PLAN_V1.md
│       └── ARCHITECTURE_PLAN_V2.md
│
├── research-data/                # Research outputs
│   ├── multi-ai/                 # Multi-AI responses
│   ├── validations/              # Validation reports
│   ├── iterations/               # GIST iterations
│   └── knowledge-graphs/         # Graph structures
│
├── research-prompts/             # Generated prompts (NEW)
│
├── models/                       # llama.cpp models
│   ├── Llama-3.1-8B-Instruct-Abliterated-Q6_K.gguf
│   └── Qwen2.5-32B-Instruct-Abliterated-Q4_K_M.gguf
│
├── llama.cpp/                    # llama.cpp binary
│   └── llama-cli
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
└── scripts/
    ├── setup_llama_cpp.sh        # Install llama.cpp
    ├── download_models.sh        # Download models
    ├── migrate_from_old.py       # Migration helper
    └── start_server.sh           # Launch GUI
```

---

## 7. Migration Strategy

### Phase 1: Bootstrap New Project (Day 1)

**A. Create Structure**
```bash
# Clone fresh
mkdir deep-research-orchestrator
cd deep-research-orchestrator

# Initialize
git init
touch README.md pyproject.toml .gitignore

# Create directories
mkdir -p {config/{agents,models,workflows/{sequential,iterative},techniques,tools,schemas},src/{core,models,tools/{data_collection,validation,processing,knowledge,multi_ai},utils},gui/{templates,static/{css,js}},docs/{frameworks,guides,architecture},research-data/{multi-ai,validations,iterations,knowledge-graphs},research-prompts,models,tests/{unit,integration,fixtures},scripts}
```

**B. Setup llama.cpp**
```bash
# Download llama.cpp
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp

# Build with CUDA support (for your NVIDIA GPU)
make LLAMA_CUDA=1

# Verify
./llama-cli --version
```

**C. Download Models**
```bash
# Download fast model (8B)
huggingface-cli download FailSpy/Llama-3.1-8B-Instruct-Abliterated-GGUF \
  Llama-3.1-8B-Instruct-Abliterated-Q6_K.gguf \
  --local-dir models/

# Download quality model (32B)
huggingface-cli download Qwen/Qwen2.5-32B-Instruct-GGUF \
  Qwen2.5-32B-Instruct-Q4_K_M.gguf \
  --local-dir models/

# Note: For abliterated version, check FailSpy or similar sources
```

---

### Phase 2: Migrate Core Components (Day 2-3)

**Priority Order:**

**1. JSON Configs (High Priority)**
```bash
# Copy logic library
cp -r ../ai-tutoring-app/product-management/tools/validator/logic_library/techniques/ config/techniques/
cp -r ../ai-tutoring-app/product-management/tools/validator/logic_library/workflows/ config/workflows/sequential/
cp -r ../ai-tutoring-app/product-management/tools/validator/logic_library/models/ config/models/
cp -r ../ai-tutoring-app/product-management/tools/validator/logic_library/sources/ config/tools/

# Update model configs to use llama.cpp paths
python scripts/migrate_from_old.py --update-model-configs
```

**2. Core Python Files (High Priority)**
```bash
# Migrate core orchestration
cp ../ai-tutoring-app/product-management/tools/validator/src/orchestrator.py src/core/
cp ../ai-tutoring-app/product-management/tools/validator/src/workflow_engine.py src/core/
cp ../ai-tutoring-app/product-management/tools/validator/src/state_manager.py src/core/

# Migrate tools
cp ../ai-tutoring-app/product-management/tools/validator/src/sources/web_scraper.py src/tools/data_collection/
cp ../ai-tutoring-app/product-management/tools/validator/src/sources/pdf_extractor.py src/tools/data_collection/

# Adapt orchestrator.py to use LlamaCppClient instead of OllamaClient
# (Manual editing required)
```

**3. GUI (Low Priority - Use As-Is)**
```bash
# Copy existing GUI
cp ../ai-tutoring-app/product-management/tools/validator/gui/app.py gui/
cp -r ../ai-tutoring-app/product-management/tools/validator/gui/templates/ gui/

# Update import paths in gui/app.py
# (from src.orchestrator → from ../src/core/orchestrator)
```

**4. Documentation**
```bash
cp ../ai-tutoring-app/product-management/1-description/*.md docs/frameworks/
```

---

### Phase 3: Implement New Features (Day 3-5)

**A. Agent System**
```python
# src/core/agent.py
# Implement Agent class (custom, no dependencies)
```

**B. Iterative Workflows**
```python
# src/core/workflow_engine.py
# Add iterative mode support
```

**C. llama.cpp Integration**
```python
# src/models/llama_cpp_client.py
# Implement LlamaCppClient
```

**D. Multi-AI Tools**
```python
# src/tools/multi_ai/prompt_generator.py
# src/tools/multi_ai/response_analyzer.py
```

**E. Knowledge Tools**
```python
# src/tools/knowledge/graph_builder.py
# src/tools/knowledge/tot_explorer.py
```

---

### Phase 4: Test & Validate (Day 5-6)

**A. Unit Tests**
```python
# tests/unit/test_agent.py
def test_agent_initialization():
    agent = Agent.from_json("config/agents/fast_researcher.json")
    assert agent.role == "researcher"

# tests/unit/test_llama_cpp_client.py
def test_generation():
    client = LlamaCppClient(model_path="models/test.gguf")
    response = client.generate("Hello")
    assert len(response) > 0
```

**B. Integration Tests**
```bash
# Start llama.cpp server mode (optional)
./llama.cpp/llama-server --model models/Llama-3.1-8B-Abliterated.gguf --port 8080

# Test full workflow
pytest tests/integration/test_research_workflow.py
```

---

## 8. Implementation Phases

### Sprint 1: Foundation (Week 1)

**Goals:**
- ✅ New project structure created
- ✅ llama.cpp installed and tested
- ✅ Models downloaded and verified
- ✅ Core classes (Agent, Task, Orchestrator) implemented
- ✅ LlamaCppClient working

**Deliverables:**
```python
# Basic test
from src.core.agent import Agent
from src.models.llama_cpp_client import LlamaCppClient

client = LlamaCppClient(model_path="models/Llama-3.1-8B-Abliterated.gguf")
response = client.generate("Explain AI in 2 sentences")
print(response)
# Output: AI (Artificial Intelligence) refers to...
```

---

### Sprint 2: Iterative Workflows (Week 2)

**Goals:**
- ✅ Workflow engine supports iterative mode
- ✅ Exit criteria evaluation working
- ✅ Gap detection implemented
- ✅ Confidence scoring functional

**Deliverables:**
```python
from src.core.orchestrator import Orchestrator

orchestrator = Orchestrator()
result = orchestrator.execute_workflow(
    workflow_id="deep_research",
    inputs={"query": "Market size for AI tutoring apps"}
)

print(f"Iterations: {result['iterations']}")
print(f"Confidence: {result['confidence']}")
print(f"Report: {result['report']}")
```

---

### Sprint 3: Multi-AI Integration (Week 3)

**Goals:**
- ✅ Prompt generator tool implemented
- ✅ Multi-AI response analyzer working
- ✅ Contradiction detection across models
- ✅ Synthesis generation functional

**Deliverables:**
```python
from src.tools.multi_ai.prompt_generator import generate_multi_ai_prompt
from src.tools.multi_ai.response_analyzer import analyze_multi_ai_responses

# Generate prompt
prompt_data = generate_multi_ai_prompt(
    topic="AI Tutoring Market Analysis",
    research_categories=["market_size", "competition", "trends"]
)

print(f"Prompt saved to: {prompt_data['save_path']}")
print(prompt_data['instructions'])

# After manual querying and saving responses...
analysis = analyze_multi_ai_responses(
    response_dir=Path("research-data/multi-ai/run_001/")
)

print(f"Contradictions: {len(analysis['contradictions'])}")
print(f"Synthesis: {analysis['synthesis']}")
```

---

### Sprint 4: Knowledge & Reasoning (Week 4)

**Goals:**
- ✅ Knowledge graph builder implemented
- ✅ Tree-of-Thought explorer working
- ✅ Graph querying functional
- ✅ ToT path evaluation accurate

**Deliverables:**
```python
from src.tools.knowledge.graph_builder import build_knowledge_graph
from src.tools.knowledge.tot_explorer import tree_of_thought_explore

# Build graph
graph = build_knowledge_graph(
    documents=[Path("research-data/iterations/I001.md")],
    entity_types=["Company", "Product", "Technology"]
)

print(f"Nodes: {graph['node_count']}, Edges: {graph['edge_count']}")

# Explore reasoning paths
tot_result = tree_of_thought_explore(
    problem="Should we target B2B or B2C market first?",
    num_paths=3
)

print(f"Best path score: {tot_result['best_path']['score']}")
print(f"Reasoning: {tot_result['reasoning']}")
```

---

### Sprint 5: GUI Enhancement (Week 5+)

**Goals:**
- ✅ Existing GUI adapted to new backend
- ✅ Multi-AI workflow UI added
- ✅ Knowledge graph visualization
- ✅ ToT explorer interface

**Deferred to later - Priority on functionality first**

---

## 9. Existing Assets to Preserve

### From Old Project

**A. Fully Functional (Use As-Is)**
```
✅ gui/app.py                    - Complete Flask GUI
✅ src/sources/web_scraper.py    - BeautifulSoup4 implementation
✅ src/sources/pdf_extractor.py  - PDF text extraction
✅ src/processors/text_cleaner.py - Text preprocessing
✅ config/techniques/*.json      - All 7 validation techniques
✅ config/workflows/sequential/  - Sequential workflows
```

**B. Needs Adaptation**
```
⚠️ src/core/orchestrator.py     - Replace OllamaClient → LlamaCppClient
⚠️ src/core/workflow_engine.py  - Add iterative mode support
⚠️ config/models/*.json          - Update paths for llama.cpp
```

**C. Framework Docs (Preserve All)**
```
✅ docs/frameworks/research-framework.md
✅ docs/frameworks/validation-framework.md
✅ docs/frameworks/planning-framework.md
```

---

## 10. Key Implementation Notes

### A. Anti-ELIZA Prompts

**System Prompt Template:**
```
You are a research analysis system.

Output requirements:
- Use impersonal language ("The data shows..." not "I found...")
- Provide structured output (JSON or tables)
- Cite sources for all claims
- Include confidence scores
- No conversational filler

Focus on factual analysis, not persuasion.
```

### B. llama.cpp Best Practices

**Memory Optimization:**
```bash
# For 8B model (fully in VRAM)
--n-gpu-layers 999

# For 32B model (split VRAM/RAM)
--n-gpu-layers 16  # Adjust based on VRAM usage monitoring
```

**Performance Tuning:**
```bash
--threads 8           # Use all CPU cores
--ctx-size 8192       # Larger context for complex tasks
--batch-size 512      # Optimize throughput
```

### C. Model Selection Heuristics

```python
def select_model_for_task(task: Task) -> str:
    """Select appropriate model based on task characteristics."""

    # Fast model for high-volume tasks
    if task.volume == "high" or task.latency_requirement == "low":
        return "tier1_fast"

    # Quality model for reasoning tasks
    if task.complexity == "high" or task.type in ["validate", "reason", "synthesize"]:
        return "tier2_quality"

    # Default to fast
    return "tier1_fast"
```

---

## Next Steps

### Immediate (This Week)

1. **Bootstrap project** (Day 1)
   - Create directory structure
   - Install llama.cpp
   - Download models
   - Test basic inference

2. **Migrate core** (Day 2-3)
   - Copy JSON configs
   - Adapt orchestrator.py
   - Implement LlamaCppClient
   - Port tools (web_scraper, pdf_extractor)

3. **Implement agents** (Day 3-4)
   - Agent class
   - Task class
   - Tool decorator system

4. **Test workflows** (Day 4-5)
   - Sequential workflows
   - Basic iterative workflow
   - Multi-AI prompt generation

### Short-Term (Week 2-3)

5. **Iterative workflows**
   - Exit criteria evaluation
   - Gap detection
   - Confidence scoring

6. **Multi-AI integration**
   - Response analyzer
   - Contradiction detection
   - Synthesis generation

### Medium-Term (Week 4+)

7. **Knowledge tools**
   - Graph builder
   - ToT explorer

8. **GUI enhancements**
   - Adapt existing GUI
   - Add new features

---

## Appendix: llama.cpp Resources

### Installation
- GitHub: https://github.com/ggerganov/llama.cpp
- Build Guide: https://github.com/ggerganov/llama.cpp#build

### Model Sources
- Llama Abliterated: https://huggingface.co/FailSpy
- Qwen Models: https://huggingface.co/Qwen
- GGUF Quantizations: https://huggingface.co/TheBloke

### Python Bindings (Optional)
- llama-cpp-python: https://github.com/abetlen/llama-cpp-python
  (If you prefer Python bindings over subprocess calls)

---

**END OF DOCUMENT**

**Status:** FINAL - Ready for Implementation
**Action:** Bootstrap project and start Sprint 1
**Next Document:** Implementation progress tracking
