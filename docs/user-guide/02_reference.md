# Teil 2: Komponenten-Referenz

**Zweck:** Detaillierte technische Dokumentation aller Klassen, Methoden und Konfigurationen

---

## Inhaltsverzeichnis

1. [Core Components](#1-core-components)
2. [Models & Clients](#2-models--clients)
3. [Tools & Utilities](#3-tools--utilities)
4. [Configuration System](#4-configuration-system)
5. [File Structure](#5-file-structure)

---

## 1. Core Components

### 1.1 Agent System

**File:** `src/core/agent.py` (173 lines)

#### Class: `Task`
```python
@dataclass
class Task:
    task_id: str
    technique: str
    inputs: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
```

**Purpose:** Represents a single atomic task for an agent.

**Attributes:**
- `task_id`: Unique identifier
- `technique`: Technique to apply (e.g., "contradiction", "blind_spots")
- `inputs`: Task-specific inputs (queries, data, etc.)
- `metadata`: Optional additional context

---

#### Class: `AgentOutput`
```python
@dataclass
class AgentOutput:
    task_id: str
    result: str
    status: str  # "success" | "failure"
    execution_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)
```

**Purpose:** Output from agent execution.

**Attributes:**
- `task_id`: Corresponding task ID
- `result`: LLM-generated output text
- `status`: Execution status
- `execution_time`: Duration in seconds
- `metadata`: Additional execution info (tokens, errors, etc.)

---

#### Class: `Agent`
```python
class Agent:
    def __init__(
        self,
        agent_id: str,
        role: str,
        llm_client: LLMClient,
        config: Optional[Dict[str, Any]] = None
    )
```

**Purpose:** Represents a specialized research agent.

**Attributes:**
- `agent_id`: Unique identifier (e.g., "fast_researcher")
- `role`: Agent role (researcher, validator, synthesizer)
- `llm_client`: LLM client instance
- `config`: Agent configuration (system prompt, temperature, etc.)

**Methods:**

```python
def execute_task(self, task: Task) -> AgentOutput:
    """
    Execute a single task using LLM client.

    Args:
        task: Task to execute

    Returns:
        AgentOutput with result and metadata
    """
```

**Example:**
```python
from src.core.agent import Agent, Task
from src.models.llama_cpp_client import LlamaCppClient

client = LlamaCppClient(model_path="models/llama-8b.gguf")
agent = Agent(
    agent_id="researcher_1",
    role="researcher",
    llm_client=client
)

task = Task(
    task_id="research_001",
    technique="quick_research",
    inputs={"query": "What is the AI tutoring market size?"}
)

output = agent.execute_task(task)
print(output.result)
```

---

### 1.2 Orchestrator

**File:** `src/core/orchestrator.py` (879 lines)

#### Class: `Orchestrator`
```python
class Orchestrator:
    def __init__(self, config_dir: Path = Path("config"))
```

**Purpose:** Master coordinator for all agents and workflows.

**Attributes:**
- `config_dir`: Root config directory
- `agents`: Dict of loaded Agent instances
- `models`: Dict of loaded LLM clients
- `logger`: Logger instance

**Key Methods:**

##### 1. Workflow Execution
```python
def execute_workflow(
    self,
    workflow_id: str,
    inputs: Dict[str, Any],
    agent_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Execute a workflow (sequential or iterative).

    Args:
        workflow_id: Workflow to execute
        inputs: Initial inputs
        agent_id: Optional specific agent to use

    Returns:
        Dict with outputs, confidence, metadata
    """
```

**Location:** Line 194

**Example:**
```python
orchestrator = Orchestrator()
result = orchestrator.execute_workflow(
    workflow_id="deep_research",
    inputs={"topic": "AI Market Analysis"}
)
print(f"Confidence: {result['confidence']}")
print(f"Outputs: {result['outputs']}")
```

---

##### 2. Framework Execution
```python
def execute_framework(
    self,
    framework_id: str,
    inputs: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Execute a complete framework (chain of phases).

    Args:
        framework_id: Framework to execute
        inputs: Initial inputs

    Returns:
        Dict with phase results, final outputs, metadata
    """
```

**Location:** Line 298

**Example:**
```python
result = orchestrator.execute_framework(
    framework_id="framework_product_research",
    inputs={"product": "AI Tutoring Platform"}
)

for phase_result in result['phase_results']:
    print(f"Phase: {phase_result['phase_id']}")
    print(f"Confidence: {phase_result['confidence']}")
```

---

##### 3. Gap Detection (Sprint 2)
```python
def _identify_gaps(
    self,
    outputs: List[AgentOutput],
    inputs: Dict[str, Any]
) -> List[str]:
    """
    Identify information gaps in outputs.

    Uses 3 methods:
    1. Failed tasks ’ automatic gaps
    2. LLM-based gap analysis (quality agent)
    3. Heuristic: low-confidence outputs

    Args:
        outputs: Agent outputs to analyze
        inputs: Original inputs for context

    Returns:
        List of identified gaps
    """
```

**Location:** Line 531

**Gap Detection Logic:**
```python
# 1. Failed tasks
gaps = [
    f"Failed task: {o.task_id}"
    for o in outputs
    if o.status == "failure"
]

# 2. LLM-based analysis
quality_agent = self._get_quality_agent()
gap_prompt = f"""
Analyze the following research outputs and identify information gaps:

{output_summary}

What critical information is missing?
Format: "Gap: [description]"
"""

# 3. Heuristic: low-confidence outputs
for output in outputs:
    if len(output.result) < 100:  # Proxy for quality
        gaps.append(f"Insufficient detail in {output.task_id}")
```

---

##### 4. Confidence Scoring (Sprint 2)
```python
def _evaluate_confidence(
    self,
    outputs: List[AgentOutput],
    inputs: Dict[str, Any]
) -> float:
    """
    Evaluate overall confidence in outputs.

    5 weighted factors:
    - Success Rate (30%)
    - Output Quality (20%)
    - Consistency (10%)
    - Gap Score (20%)
    - LLM Assessment (20%, optional)

    Args:
        outputs: Agent outputs to evaluate
        inputs: Original inputs

    Returns:
        Confidence score (0.0-1.0)
    """
```

**Location:** Line 579

**Scoring Formula:**
```python
# Factor 1: Success Rate (30%)
success_rate = successful_tasks / total_tasks

# Factor 2: Output Quality (20%)
avg_length = mean([len(o.result) for o in outputs])
quality_score = min(avg_length / 500, 1.0)  # Normalized

# Factor 3: Consistency (10%)
length_variance = variance([len(o.result) for o in outputs])
consistency_score = 1.0 / (1.0 + length_variance / 1000)

# Factor 4: Gap Score (20%)
gaps = self._identify_gaps(outputs, inputs)
gap_score = max(0.0, 1.0 - len(gaps) * 0.1)

# Factor 5: LLM Assessment (20%, optional)
if use_llm_assessment:
    llm_score = quality_agent.assess(outputs)
else:
    llm_score = 0.5  # Neutral

# Final confidence
confidence = (
    0.3 * success_rate +
    0.2 * quality_score +
    0.1 * consistency_score +
    0.2 * gap_score +
    0.2 * llm_score
)
```

---

##### 5. Input Refinement (Sprint 2)
```python
def _refine_inputs(
    self,
    inputs: Dict[str, Any],
    gaps: List[str]
) -> Dict[str, Any]:
    """
    Refine inputs based on identified gaps.

    Uses quality agent to generate focused sub-queries.

    Args:
        inputs: Original inputs
        gaps: Identified information gaps

    Returns:
        Refined inputs with additional queries
    """
```

**Location:** Line 648

**Refinement Process:**
```python
# Generate focused queries from gaps
quality_agent = self._get_quality_agent()

refinement_prompt = f"""
Original query: {inputs['query']}

Identified gaps:
{chr(10).join(gaps)}

Generate 3-5 specific, focused queries to address these gaps.
Format: "Query: [specific question]"
"""

# Parse LLM response
refined_queries = parse_queries(agent_output)

# Extend inputs
refined_inputs = inputs.copy()
refined_inputs.update({
    "refined_queries": refined_queries,
    "priority_gaps": gaps[:3],  # Top 3
    "detail_level": "deep"
})

return refined_inputs
```

---

##### 6. Agent & Model Loading
```python
def load_agent(self, agent_id: str) -> Agent:
    """Load agent from config."""

def load_model(self, model_id: str) -> LLMClient:
    """Load LLM client from config."""

def list_agents(self) -> List[Dict[str, str]]:
    """List all available agents."""

def list_workflows(self) -> List[Dict[str, str]]:
    """List all available workflows."""
```

---

### 1.3 WorkflowEngine

**File:** `src/core/workflow_engine.py` (347 lines)

#### Class: `WorkflowEngine`
```python
class WorkflowEngine:
    def __init__(self, orchestrator: Orchestrator)
```

**Purpose:** Executes workflows in sequential or iterative mode.

**Methods:**

##### 1. Execute Workflow
```python
def execute(
    self,
    workflow: Dict[str, Any],
    agent: Agent,
    inputs: Dict[str, Any]
) -> List[AgentOutput]:
    """
    Execute workflow based on mode.

    Args:
        workflow: Workflow config
        agent: Agent to use
        inputs: Initial inputs

    Returns:
        List of agent outputs
    """
```

**Modes:**
- `sequential`: Execute steps in order (A ’ B ’ C)
- `iterative`: Execute with refinement loops

---

##### 2. Sequential Execution
```python
def _execute_sequential(
    self,
    workflow: Dict[str, Any],
    agent: Agent,
    inputs: Dict[str, Any]
) -> List[AgentOutput]:
    """Execute steps sequentially without loops."""
```

**Logic:**
```python
outputs = []
for step in workflow["steps"]:
    # Check condition (if any)
    if not self._evaluate_condition(step, inputs):
        continue

    # Execute technique
    task = Task(
        task_id=f"{workflow['workflow_id']}_{step['technique']}",
        technique=step["technique"],
        inputs=inputs
    )
    output = agent.execute_task(task)
    outputs.append(output)

    # Update inputs for next step
    inputs["previous_output"] = output.result

return outputs
```

---

##### 3. Iterative Execution
```python
def _execute_iterative(
    self,
    workflow: Dict[str, Any],
    agent: Agent,
    inputs: Dict[str, Any]
) -> List[AgentOutput]:
    """
    Execute with refinement loops.

    Loop until exit criteria met or max iterations reached.
    """
```

**Loop Structure:**
```python
iteration = 0
max_iterations = workflow.get("max_iterations", 3)
all_outputs = []

while iteration < max_iterations:
    # Execute all steps
    outputs = self._execute_sequential(workflow, agent, inputs)
    all_outputs.extend(outputs)

    # Check exit criteria
    if self._check_exit_criteria(workflow, outputs, inputs):
        break

    # Refine inputs for next iteration
    gaps = orchestrator._identify_gaps(outputs, inputs)
    inputs = orchestrator._refine_inputs(inputs, gaps)

    iteration += 1

return all_outputs
```

---

##### 4. Exit Criteria Evaluation
```python
def _check_exit_criteria(
    self,
    workflow: Dict[str, Any],
    outputs: List[AgentOutput],
    inputs: Dict[str, Any]
) -> bool:
    """
    Check if workflow should exit.

    Supported criteria:
    - all_complete: All steps successful
    - confidence_threshold: Confidence >= threshold
    - custom: User-defined logic
    """
```

**Examples:**
```python
# all_complete
exit_criteria = {"type": "all_complete"}
’ Returns True if all outputs.status == "success"

# confidence_threshold
exit_criteria = {"type": "confidence_threshold", "threshold": 0.8}
’ Returns True if confidence >= 0.8

# custom
exit_criteria = {"type": "custom", "criteria_id": "my_criteria"}
’ Loads and executes custom logic
```

---

### 1.4 FrameworkLoader

**File:** `src/core/framework_loader.py` (394 lines)

#### Class: `FrameworkLoader`
```python
class FrameworkLoader:
    def __init__(self, config_dir: Path = Path("config"))
```

**Purpose:** Loads and validates hierarchical building blocks.

**Dataclasses:**

```python
@dataclass
class BuildingBlock:
    block_id: str
    name: str
    block_type: str
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Technique(BuildingBlock):
    prompt: str = ""
    agent_role: str = "researcher"
    temperature: float = 0.7
    max_tokens: int = 2048

@dataclass
class Workflow(BuildingBlock):
    mode: str = "sequential"
    steps: List[Dict[str, Any]] = field(default_factory=list)
    exit_criteria: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Phase(BuildingBlock):
    building_blocks: List[Dict[str, Any]] = field(default_factory=list)
    exit_criteria: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Framework(BuildingBlock):
    building_blocks: List[Dict[str, Any]] = field(default_factory=list)
    global_exit_criteria: Dict[str, Any] = field(default_factory=dict)
```

**Methods:**

```python
def load_technique(self, technique_id: str) -> Technique:
    """Load technique from config/techniques/"""

def load_workflow(self, workflow_id: str) -> Workflow:
    """Load workflow from config/workflows/{sequential|iterative}/"""

def load_phase(self, phase_id: str) -> Phase:
    """Load phase from config/phases/"""

def load_framework(self, framework_id: str) -> Framework:
    """Load framework from config/frameworks/"""

def load(self, block_id: str, block_type: Optional[str] = None) -> BuildingBlock:
    """Auto-detect and load any block type."""

def validate_framework(self, framework: Framework) -> tuple[bool, List[str]]:
    """Validate framework structure (check all referenced blocks exist)."""

def list_techniques() -> List[Dict[str, str]]:
def list_workflows() -> List[Dict[str, str]]:
def list_phases() -> List[Dict[str, str]]:
def list_frameworks() -> List[Dict[str, str]]:
    """List all available blocks."""

def clear_cache():
    """Clear internal caches."""
```

**Caching:**
- All loaded blocks are cached in `_techniques_cache`, `_workflows_cache`, etc.
- Second load of same block returns cached instance (performance)

**Example:**
```python
from src.core.framework_loader import FrameworkLoader

loader = FrameworkLoader()

# Load framework
framework = loader.load_framework("framework_product_research")
print(f"Phases: {framework.count_blocks()}")

# Validate
is_valid, errors = loader.validate_framework(framework)
if not is_valid:
    print(f"Errors: {errors}")

# Load phase
phase = loader.load_phase("phase_0_base_research")
for block in phase.building_blocks:
    workflow = loader.load_workflow(block["block_id"])
    print(f"Workflow: {workflow.name}")
```

---

### 1.5 Tool Decorator

**File:** `src/core/tool_decorator.py` (215 lines)

#### Decorator: `@tool`
```python
def tool(description: str):
    """
    Decorator to register functions as LLM-callable tools.

    Generates JSON schema from function signature and docstring.
    """
```

**Example:**
```python
from src.core.tool_decorator import tool

@tool("Extract text content from a PDF file")
def pdf_extractor(file_path: str, pages: Optional[List[int]] = None) -> dict:
    """
    Extract text from PDF.

    Args:
        file_path: Path to PDF file
        pages: Optional list of page numbers to extract

    Returns:
        Dict with extracted text and metadata
    """
    # Implementation...
    return {"text": extracted_text, "pages": num_pages}
```

**Generated Schema:**
```json
{
  "name": "pdf_extractor",
  "description": "Extract text content from a PDF file",
  "parameters": {
    "type": "object",
    "properties": {
      "file_path": {"type": "string"},
      "pages": {"type": "array", "items": {"type": "integer"}}
    },
    "required": ["file_path"]
  }
}
```

#### Class: `ToolRegistry`
```python
class ToolRegistry:
    """Singleton registry for all decorated tools."""

    @classmethod
    def register(cls, func: Callable, description: str):
        """Register a tool function."""

    @classmethod
    def get_tool(cls, tool_name: str) -> Optional[Callable]:
        """Get tool by name."""

    @classmethod
    def list_tools(cls) -> List[Dict[str, Any]]:
        """List all registered tools with schemas."""

    @classmethod
    def generate_tool_prompt(cls) -> str:
        """Generate LLM prompt describing all available tools."""
```

**Usage in Agent:**
```python
# Get tools for LLM context
tools_prompt = ToolRegistry.generate_tool_prompt()
system_prompt = f"{agent_prompt}\n\nAvailable tools:\n{tools_prompt}"

# Execute tool from LLM output
tool_name = "pdf_extractor"
tool_args = {"file_path": "report.pdf"}
tool_func = ToolRegistry.get_tool(tool_name)
result = tool_func(**tool_args)
```

---

## 2. Models & Clients

### 2.1 LlamaCppClient

**File:** `src/models/llama_cpp_client.py` (173 lines)

#### Class: `LlamaCppClient`
```python
class LlamaCppClient(LLMClient):
    def __init__(
        self,
        model_path: str,
        llama_cli_path: str = "./llama.cpp/build/bin/llama-cli",
        context_length: int = 2048,
        n_gpu_layers: int = 999,
        **kwargs
    )
```

**Purpose:** Subprocess-based wrapper around llama-cli binary.

**Attributes:**
- `model_path`: Path to .gguf model file
- `llama_cli_path`: Path to llama-cli binary
- `context_length`: Context window size
- `n_gpu_layers`: Layers to offload to GPU (999 = all)
- `temperature`, `top_p`, `top_k`: Generation parameters

**Methods:**

```python
def generate(
    self,
    prompt: str,
    system_prompt: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: int = 512
) -> str:
    """
    Generate completion using llama-cli subprocess.

    Args:
        prompt: User prompt
        system_prompt: Optional system context
        temperature: Override default temperature
        max_tokens: Max output tokens

    Returns:
        Generated text
    """
```

**Command Construction:**
```python
cmd = [
    self.llama_cli_path,
    "-m", self.model_path,
    "-p", full_prompt,
    "-n", str(max_tokens),
    "--ctx-size", str(self.context_length),
    "--n-gpu-layers", str(self.n_gpu_layers),
    "--temp", str(temperature),
    "--no-conversation"  # One-shot mode
]

result = subprocess.run(cmd, capture_output=True, text=True)
return self._parse_output(result.stdout)
```

**Health Check:**
```python
def health_check(self) -> bool:
    """Test if model is loadable."""
    try:
        output = self.generate("Test", max_tokens=5)
        return len(output) > 0
    except Exception:
        return False
```

**Example:**
```python
from src.models.llama_cpp_client import LlamaCppClient

client = LlamaCppClient(
    model_path="models/llama-8b.gguf",
    n_gpu_layers=999,  # All layers in VRAM
    temperature=0.7
)

response = client.generate(
    prompt="What is 2+2?",
    system_prompt="You are a helpful math tutor.",
    max_tokens=50
)
print(response)
```

---

### 2.2 Base LLMClient Interface

**File:** `src/models/base.py`

```python
from abc import ABC, abstractmethod

class LLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate text completion."""
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Check if client is operational."""
        pass
```

**Purpose:** Allows multiple backends (llama.cpp, vLLM, OpenAI API, etc.)

---

## 3. Tools & Utilities

### 3.1 Registered Tools

**File:** `src/tools/registered_tools.py` (182 lines)

All tools use `@tool` decorator for automatic registration.

#### Tool: `web_scraper`
```python
@tool("Extract clean text content from a URL")
def web_scraper(url: str, timeout: int = 10) -> dict:
    """
    Scrape and clean web page content.

    Args:
        url: Target URL
        timeout: Request timeout (seconds)

    Returns:
        Dict with text, title, metadata
    """
```

#### Tool: `pdf_extractor`
```python
@tool("Extract text from PDF file")
def pdf_extractor(file_path: str) -> dict:
    """Extract all text from PDF."""
```

#### Tool: `text_cleaner`
```python
@tool("Clean and normalize text content")
def text_cleaner(text: str, remove_urls: bool = True) -> str:
    """Remove noise from text."""
```

#### Tool: `search_local_docs`
```python
@tool("Search local documentation for relevant information")
def search_local_docs(query: str, limit: int = 5) -> list[dict]:
    """Full-text search through markdown docs."""
```

#### Tool: `calculate_statistics`
```python
@tool("Calculate basic statistics on numeric data")
def calculate_statistics(values: List[float]) -> dict:
    """
    Compute mean, median, std, min, max.

    Returns:
        Dict with statistical measures
    """
```

---

### 3.2 Multi-AI Tools (Sprint 3)

#### Tool: `generate_multi_ai_prompt`

**File:** `src/tools/multi_ai/prompt_generator.py` (391 lines)

```python
@tool("Generate comprehensive research prompt for multi-AI querying")
def generate_multi_ai_prompt(
    topic: str,
    categories: List[str],
    output_format: str = "markdown",
    depth: str = "comprehensive",
    save: bool = True
) -> Dict[str, Any]:
    """
    Generate optimized prompt for Claude/GPT-4/Gemini.

    Args:
        topic: Research topic
        categories: List of research categories (market_size, competition, etc.)
        output_format: markdown | json | structured
        depth: quick | standard | comprehensive | deep
        save: Save to research-prompts/ directory

    Returns:
        Dict with prompt text, save path, instructions
    """
```

**Categories:**
- `market_size`: TAM, SAM, SOM analysis
- `competition`: Competitor landscape
- `trends`: Market trends and dynamics
- `technical_feasibility`: Tech requirements
- `user_needs`: User research insights
- `risks`: Risk assessment

**Depth Levels:**
- `quick`: 1-2 paragraphs per category
- `standard`: 3-5 paragraphs
- `comprehensive`: 1-2 pages (default)
- `deep`: 3-5 pages with citations

**Example:**
```python
from src.tools.multi_ai.prompt_generator import generate_multi_ai_prompt

prompt_data = generate_multi_ai_prompt(
    topic="AI Tutoring Market Analysis",
    categories=["market_size", "competition", "trends"],
    depth="comprehensive",
    output_format="markdown"
)

print(f"Saved to: {prompt_data['save_path']}")
print(prompt_data['instructions'])
# ’ "Copy this prompt to Claude, GPT-4, and Gemini..."
```

---

#### Tool: `analyze_multi_ai_responses`

**File:** `src/tools/multi_ai/response_analyzer.py` (578 lines)

```python
@tool("Analyze responses from multiple AI services")
def analyze_multi_ai_responses(
    response_dir: Path,
    analysis_types: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Analyze Claude/GPT-4/Gemini responses using local quality agent.

    Args:
        response_dir: Directory with AI responses (*.md files)
        analysis_types: List of analyses to run
            - "contradiction": Find conflicting statements
            - "blind_spots": Identify missing information
            - "consensus": Extract common findings
            - "synthesis": Generate unified report

    Returns:
        Dict with analysis results and confidence scores
    """
```

**Analysis Process:**
```python
# 1. Load responses
responses = {
    "claude": Path("claude_response.md").read_text(),
    "gpt4": Path("gpt4_response.md").read_text(),
    "gemini": Path("gemini_response.md").read_text()
}

# 2. Run analyses (using quality agent)
analyzer = MultiAIResponseAnalyzer(orchestrator.get_quality_agent())

contradictions = analyzer.find_contradictions(responses)
# ’ [{"source_a": "claude", "source_b": "gpt4", "topic": "market_size", "conflict": "..."}]

blind_spots = analyzer.find_blind_spots(responses)
# ’ ["Missing: regulatory considerations", "Missing: geographical breakdown"]

consensus = analyzer.find_consensus(responses)
# ’ {"market_growth": "All agree 15-20% CAGR", ...}

synthesis = analyzer.generate_synthesis(responses, contradictions, consensus)
# ’ Unified report text

# 3. Confidence scoring
confidence = analyzer.calculate_confidence(contradictions, consensus)
# ’ 0.0-1.0 based on agreement level
```

**Example:**
```python
from pathlib import Path
from src.tools.multi_ai.response_analyzer import analyze_multi_ai_responses

analysis = analyze_multi_ai_responses(
    response_dir=Path("research-data/multi-ai/run_001/")
)

print(f"Contradictions: {len(analysis['contradictions'])}")
print(f"Blind Spots: {analysis['blind_spots']}")
print(f"Confidence: {analysis['confidence_score']:.2f}")
print(f"\nSynthesis:\n{analysis['synthesis']}")
```

---

### 3.3 Utility Modules

#### JSONLoader

**File:** `src/utils/json_loader.py`

```python
class JSONLoader:
    @staticmethod
    def load(file_path: Path) -> Dict[str, Any]:
        """
        Load and validate JSON config.

        Automatically validates against schema if available.
        """

    @staticmethod
    def validate(config: Dict[str, Any], schema_path: Path) -> bool:
        """Validate config against JSON schema."""
```

#### Logger

**File:** `src/utils/logger.py`

```python
def setup_logger(
    name: str,
    level: str = "INFO",
    log_file: Optional[Path] = None
) -> logging.Logger:
    """
    Create configured logger.

    Args:
        name: Logger name
        level: DEBUG | INFO | WARNING | ERROR
        log_file: Optional file path

    Returns:
        Configured logger instance
    """
```

---

## 4. Configuration System

### 4.1 Agent Configs

**Location:** `config/agents/`

**Schema:** `config/schemas/agent_schema.json` (nicht implementiert, aber folgt Pattern)

**Example:** `fast_researcher.json`
```json
{
  "agent_id": "fast_researcher",
  "role": "researcher",
  "model_id": "tier1_fast",
  "system_prompt": "You are a fast research assistant specializing in gathering information quickly and efficiently.",
  "temperature": 0.7,
  "max_tokens": 2048,
  "metadata": {
    "use_case": "Quick research, initial data gathering"
  }
}
```

**Fields:**
- `agent_id`: Unique identifier
- `role`: researcher | validator | synthesizer
- `model_id`: Reference to model config
- `system_prompt`: Agent personality/instructions
- `temperature`: Generation randomness (0.0-1.0)
- `max_tokens`: Max output length

---

### 4.2 Model Configs

**Location:** `config/models/`

**Schema:** `config/schemas/model_schema.json`

**Example:** `tier2_quality.json`
```json
{
  "model_id": "tier2_quality",
  "type": "llama_cpp",
  "path": "models/qwen-2.5-32b-instruct-abliterated.Q4_K_M.gguf",
  "context_length": 4096,
  "n_gpu_layers": 16,
  "temperature": 0.3,
  "top_p": 0.9,
  "top_k": 40,
  "use_mlock": true,
  "metadata": {
    "tier": "quality",
    "vram_usage": "~8GB",
    "ram_usage": "~7GB",
    "recommended_use": "Deep analysis, validation, synthesis"
  }
}
```

**Fields:**
- `model_id`: Unique identifier
- `type`: llama_cpp (extensible for vllm, openai, etc.)
- `path`: Path to .gguf file
- `context_length`: Context window
- `n_gpu_layers`: GPU offload (16 = partial, 999 = all)
- `use_mlock`: Lock model in RAM (prevents swapping)

---

### 4.3 Technique Configs

**Location:** `config/techniques/`

**Schema:** `config/schemas/technique_schema.json`

**Example:** `contradiction.json`
```json
{
  "technique_id": "contradiction",
  "name": "Contradiction Detection",
  "description": "Identify logical contradictions in research outputs",
  "prompt": "Analyze the following research outputs and identify any logical contradictions, inconsistencies, or conflicting claims:\n\n{input_data}\n\nFor each contradiction found, specify:\n1. The contradicting statements\n2. The sources\n3. Why they conflict\n4. Potential resolution",
  "agent_role": "validator",
  "temperature": 0.3,
  "max_tokens": 2048
}
```

---

### 4.4 Workflow Configs

**Location:** `config/workflows/{sequential|iterative}/`

**Schema:** `config/schemas/workflow_schema.json`

**Example:** `deep_research.json` (iterative)
```json
{
  "workflow_id": "deep_research",
  "name": "Deep Research with Iterative Refinement",
  "mode": "iterative",
  "max_iterations": 3,
  "steps": [
    {
      "technique": "quick_research",
      "order": 1
    },
    {
      "technique": "contradiction",
      "order": 2
    },
    {
      "technique": "blind_spots",
      "order": 3
    }
  ],
  "exit_criteria": {
    "type": "confidence_threshold",
    "threshold": 0.8
  }
}
```

---

### 4.5 Phase Configs

**Location:** `config/phases/`

**Schema:** `config/schemas/phase_schema.json`

**Example:** `phase_0_base_research.json`
```json
{
  "phase_id": "phase_0_base_research",
  "name": "Base Research Phase",
  "description": "Initial research collection across multiple categories",
  "type": "phase",
  "building_blocks": [
    {
      "block_type": "workflow",
      "block_id": "market_research_collection",
      "category": "market_opportunity"
    },
    {
      "block_type": "workflow",
      "block_id": "tech_feasibility_collection",
      "category": "technical_feasibility"
    }
  ],
  "exit_criteria": {
    "type": "all_complete",
    "required_outputs": ["market_research", "tech_feasibility"]
  }
}
```

---

### 4.6 Framework Configs

**Location:** `config/frameworks/`

**Schema:** `config/schemas/framework_schema.json`

**Example:** `framework_product_research.json`
```json
{
  "framework_id": "framework_product_research",
  "name": "Product Research Framework",
  "description": "Complete product research workflow from initial research to validated planning",
  "type": "framework",
  "building_blocks": [
    {
      "block_type": "phase",
      "block_id": "phase_0_base_research",
      "order": 1
    },
    {
      "block_type": "phase",
      "block_id": "phase_2_validation",
      "order": 2,
      "depends_on": "phase_0_base_research"
    },
    {
      "block_type": "phase",
      "block_id": "phase_3_synthesis",
      "order": 3,
      "depends_on": "phase_2_validation"
    }
  ],
  "global_exit_criteria": {
    "type": "all_phases_complete"
  }
}
```

---

## 5. File Structure

```
deep-research-orchestrator/
   config/
      agents/
         fast_researcher.json
         quality_validator.json
         synthesizer.json
      models/
         tier1_fast.json
         tier2_quality.json
         test_mixtral.json
      techniques/
         contradiction.json
         blind_spots.json
         ... (7 total)
      workflows/
         sequential/
            research_validation.json
            ... (7 total)
         iterative/
             deep_research.json
             validation_loop.json
      phases/
         phase_0_base_research.json
         phase_2_validation.json
         phase_3_synthesis.json
      frameworks/
         framework_product_research.json
      schemas/
          technique_schema.json
          workflow_schema.json
          phase_schema.json
          framework_schema.json
          model_schema.json

   src/
      core/
         agent.py (173 lines)
         orchestrator.py (879 lines)
         workflow_engine.py (347 lines)
         framework_loader.py (394 lines)
         tool_decorator.py (215 lines)
      models/
         base.py
         llama_cpp_client.py (173 lines)
      tools/
         registered_tools.py (182 lines)
         multi_ai/
            prompt_generator.py (391 lines)
            response_analyzer.py (578 lines)
         web_scraper.py
         pdf_extractor.py
         text_cleaner.py
      utils/
          json_loader.py
          logger.py

   docs/
      user-guide/
         00_index.md
         01_konzepte.md
         02_reference.md (this file)
         03_use_cases.md
      architecture/
         ARCHITECTURE_PLAN_V2.1_FINAL.md
      frameworks/
          ... (framework docs)

   llama.cpp/
      build/bin/llama-cli

   models/
      ... (.gguf files)

   logs/
      ... (log files)

   research-data/
       multi-ai/
          run_001/
              claude_response.md
              gpt4_response.md
              gemini_response.md
       validations/
           synthesis_report.md
```

---

## Zusammenfassung

**Core:**
- `Agent`: Task executor with LLM client
- `Orchestrator`: Master coordinator (879 lines)
- `WorkflowEngine`: Sequential/iterative execution
- `FrameworkLoader`: Hierarchical block loading
- `ToolDecorator`: Function ’ LLM tool registration

**Models:**
- `LlamaCppClient`: Subprocess wrapper for llama.cpp
- Supports VRAM/RAM split via `--n-gpu-layers`

**Tools:**
- Basic: web_scraper, pdf_extractor, text_cleaner
- Advanced: generate_multi_ai_prompt, analyze_multi_ai_responses

**Config System:**
- JSON-based config-driven architecture
- Schemas for validation
- 4-level hierarchy: Technique ’ Workflow ’ Phase ’ Framework

**Nächster Schritt:** Siehe `03_use_cases.md` für praktische Anwendungsbeispiele.
