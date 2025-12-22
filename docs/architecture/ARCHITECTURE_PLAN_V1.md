# Deep Research Orchestrator - Architecture Plan V1

**Date:** 2025-12-21
**Purpose:** Comprehensive architecture document for fresh start
**Status:** DRAFT - Review & Adjust

---

## Table of Contents

1. [Vision & Philosophy](#1-vision--philosophy)
2. [Current State Analysis](#2-current-state-analysis)
3. [Framework Research Summary](#3-framework-research-summary)
4. [Gemini Concepts Integration](#4-gemini-concepts-integration)
5. [Proposed Architecture](#5-proposed-architecture)
6. [Model Strategy](#6-model-strategy)
7. [Project Structure](#7-project-structure)
8. [Migration Plan](#8-migration-plan)
9. [Implementation Phases](#9-implementation-phases)
10. [Open Questions](#10-open-questions)

---

## 1. Vision & Philosophy

### Core Mission
Build a **local-first, privacy-focused Deep Research Orchestrator** that combines:
- Multi-agent orchestration (inspired by GPT-Researcher, CrewAI)
- Abliterated models for unbiased research (Gemini insight)
- Product Management CoT workflows (existing framework)
- Structured validation & reasoning (existing validator)

### Key Principles

**1. Independence (Gemini: Anti-ELIZA)**
- Local models only (Ollama/LM Studio)
- No cloud dependencies for core functionality
- Abliterated models for truthful, unbiased outputs
- Anti-anthropomorphization: Technical interface, not conversational

**2. Modularity**
- Agents are composable (CrewAI pattern)
- Workflows are data-driven (JSON/YAML configs)
- Tools are reusable across agents
- Clear separation: Structural Logic vs Executable Logic

**3. Transparency**
- Source citations for every claim
- Confidence scores for all outputs
- Validation trails (who validated what, when)
- No "black box" reasoning

**4. Quality over Speed**
- Multi-model validation (fast model + deep model)
- Iterative refinement loops (GPT-Researcher pattern)
- Human-in-the-loop checkpoints
- Abliteration + Reasoning model strategy

---

## 2. Current State Analysis

### What We Have (Assets to Migrate)

#### A. Logic Library (30 JSON Files)
**Location:** `product-management/tools/validator/logic_library/`

```
✅ techniques/          (7 files)
   - contradiction.json, blind_spots.json, premortem.json
   - consensus.json, red_flags.json, sanity_check.json
   - scenario_analysis.json

✅ workflows/           (7 files)
   - research_validation.json
   - planning_validation.json
   - general_chat.json
   - market_research_collection.json
   - tech_feasibility_collection.json
   - competitor_analysis_collection.json
   - quick_web_research.json

✅ models/              (3 files)
   - tier1_fast.json (dolphin-llama3:8b)
   - tier2_deep.json (qwen2.5:14b)
   - tier3_overnight.json (dolphin-mixtral:8x7b)

✅ sources/             (5 files)
   - web_article.json, pdf_document.json
   - local_markdown.json, tech_blog.json, market_report.json

✅ schemas/             (4 files)
   - technique_schema.json, workflow_schema.json
   - model_schema.json, reasoning_schema.json
```

#### B. Python Backend (15 Core Files)
**Location:** `product-management/tools/validator/src/`

```
✅ orchestrator.py       - Multi-workflow execution
✅ workflow_engine.py    - JSON workflow interpreter
✅ ollama_client.py      - Local LLM integration
✅ reasoning.py          - CoT, ToT, Self-Correction
✅ data_collector.py     - Web scraping, PDF extraction
✅ state_manager.py      - Progress tracking

✅ sources/
   - web_scraper.py
   - pdf_extractor.py
   - local_file_processor.py

✅ processors/
   - ai_summarizer.py
   - text_cleaner.py
   - structurer.py
```

#### C. GUI/Server Infrastructure
**Location:** `product-management/tools/validator/viewer/`

```
✅ serve_live.py         - Flask + livereload server
✅ templates/            - Jinja2 HTML templates
   - index.html, validate.html, workflows.html
   - chat.html, collect.html
✅ static/               - CSS, JS assets
✅ API Endpoints:
   - /api/validate, /api/chat, /api/workflows
   - /api/collect, /api/status, /api/stats
```

#### D. Framework Documentation (9 MD Files)
**Location:** `product-management/1-description/`

```
✅ research-framework.md       - 6-Category Base Research
✅ validation-framework.md     - 7 Validation Techniques
✅ planning-framework.md       - GIST Iterations
✅ templates.md                - Prompt & workflow templates
✅ framework-generalization.md - Abstraction guidelines
```

### What's Missing (Gaps to Fill)

```
❌ Agent-based Architecture (no role definitions)
❌ Iterative Research Loops (workflows are linear)
❌ Model Role Assignment (Searcher vs Analyst)
❌ Abliteration Strategy (no model selection logic)
❌ Tool Decorator System (no @tool pattern)
❌ Structural Logic Layer (phases, exit criteria not executable)
❌ Clean Project Structure (everything in tools/ subfolder)
```

---

## 3. Framework Research Summary

### GPT-Researcher (Master-Worker Pattern)

**Key Takeaway:** Hierarchical orchestration with iterative refinement

**Architecture:**
```
Master Agent (Orchestrator)
  ↓
  ├─ Plan: Break query into sub-tasks
  ├─ Dispatch: Assign to worker agents
  ├─ Aggregate: Consolidate findings
  └─ Iterate: Refine based on gaps
```

**What We Adopt:**
- ✅ Master = Our Orchestrator
- ✅ Workers = Our Techniques/Agents
- ✅ Iterative loop with gap detection
- ✅ Config-driven research plans (JSON)

**GitHub:** https://github.com/run-llm/gpt-researcher

---

### CrewAI (Role-based Multi-Agent)

**Key Takeaway:** Clear role separation with task chaining

**Core Concepts:**
- **Agent:** Role + Goal + Tools + LLM
- **Task:** Description + Expected Output + Agent
- **Crew:** Orchestrates agents through sequential/parallel tasks

**Example:**
```python
researcher = Agent(
    role="Researcher",
    goal="Find relevant information",
    tools=[web_search, pdf_extract],
    llm=ollama_model
)

research_task = Task(
    description="Research topic X",
    agent=researcher,
    expected_output="Detailed findings"
)

crew = Crew(
    agents=[researcher, analyst, editor],
    tasks=[research_task, analysis_task, edit_task],
    process=Process.sequential
)
```

**What We Adopt:**
- ✅ Agent = Model + Role + Capabilities
- ✅ Task chaining with output passing
- ✅ Role-based model selection (Searcher vs Analyst)
- ✅ Native Ollama support

**GitHub:** https://github.com/joaomdmoura/crewai

---

### LangGraph (State Machine for Conditional Logic)

**Key Takeaway:** Use only when we need branching/loops

**When to Use:**
- Conditional routing (if confidence < 0.7 → refine)
- Research loops (ask → answer → refine question → loop)
- Error recovery with retry logic

**When NOT to Use:**
- Linear sequential workflows (90% of our cases)
- Simple task chains (CrewAI pattern is simpler)

**Decision:** Start without LangGraph, add later if needed

**Docs:** https://langchain-ai.github.io/langgraph/

---

### smolagents (Code Over Prompts)

**Key Takeaway:** Code generation for precision

**Philosophy:**
- Agents generate Python code to call tools
- 30% fewer LLM calls vs JSON-based approaches
- Natural control flow (loops, conditionals)

**Example:**
```python
@tool
def validate_market_size(data: dict) -> dict:
    """Validates market size calculations."""
    # Logic here
    return {"valid": True, "confidence": 0.85}
```

**What We Adopt:**
- ✅ Tool decorator pattern for custom validators
- ⚠️ Code generation (optional, needs sandboxing)
- ✅ Lightweight approach (~1K lines)

**GitHub:** https://github.com/huggingface/smolagents

---

## 4. Gemini Concepts Integration

### A. Abliteration & Orthogonalization

**Problem:** Standard models have "refusal directions" baked in
- Refuse certain research topics (controversial, sensitive)
- Add moral commentary to factual queries
- Introduce bias through RLHF alignment

**Solution:** Abliterated models (FailSpy, uncensored variants)
- Remove refusal vectors from model weights
- Truthful outputs without censorship
- No moralizing or corporate-speak

**Integration:**
```json
// models/searcher_agent.json
{
  "model_id": "searcher_8b",
  "agent_role": "researcher",
  "model_name": "llama-3.1-8b-abliterated",
  "purpose": "Unbiased data collection",
  "temperature": 0.3,
  "capabilities": ["web_search", "pdf_extract", "summarize"]
}
```

---

### B. Anti-ELIZA Effect

**Problem:** Users anthropomorphize AI outputs
- Assign human intent to statistical patterns
- Over-trust "confident" but wrong outputs
- Mistake fluency for accuracy

**Solutions:**

**1. Depersonalize Language**
```python
# System prompt template
ANTI_ELIZA_PROMPT = """
You are an analytical system, not a person.
Use factual, impersonal language:
- "The data shows..." (not "I found...")
- "Analysis indicates..." (not "I think...")
- Output in structured format (JSON/tables)
"""
```

**2. Output Design**
- Prefer JSON/tables over prose
- Source citations mandatory
- Confidence scores visible
- No "friendly" chat interface

**3. Chain of Verification (CoVe)**
```
Research Agent → Analyst Agent (critiques research)
                              ↓
                        Show both perspectives
```

---

### C. Model Strategy (Gemini Recommendation)

**Two-Model Approach:**

**Searcher (Fast & Abliterated)**
- Model: Llama-3.1-8B-Abliterated
- VRAM: ~6GB (fits in 11GB)
- Speed: 30-50 tok/s
- Role: Data collection without censorship
- Tools: web_search, pdf_extract, summarize

**Analyst (Deep Reasoning)**
- Model: DeepSeek-R1-Distill-Qwen-32B (Q4_K_M)
- VRAM: ~8GB, RAM: ~12GB (split mode)
- Speed: 1-3 tok/s (acceptable for analysis)
- Role: Validation, contradiction detection, reasoning
- Tools: contradiction, blind_spots, premortem

**Hardware Fit (Your System):**
- 11GB VRAM + 16GB RAM
- Searcher: Fully in VRAM (fast)
- Analyst: Split VRAM+RAM (slower but smart)

---

### D. Quality Assurance Frameworks

**RAGAS (RAG Assessment)**
- Faithfulness: Does output match sources?
- Answer Relevance: Does it answer the question?
- Context Precision: Are sources relevant?

**DeepEval (Unit Testing for AI)**
- Hallucination detection
- Bias measurement
- Factual consistency checks

**Integration:**
```python
# After research step
from ragas import evaluate

results = evaluate(
    question=query,
    answer=research_output,
    contexts=sources,
    metrics=["faithfulness", "answer_relevance"]
)

if results["faithfulness"] < 0.7:
    trigger_human_review()
```

---

## 5. Proposed Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────┐
│  GUI Layer (Flask + Templates)                          │
│  /gui/dashboard, /gui/validate, /gui/research           │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  API Layer (REST Endpoints)                             │
│  /api/research, /api/validate, /api/chat               │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  Orchestrator Layer                                      │
│  - Master Agent (Research Coordinator)                   │
│  - Task Dispatcher                                       │
│  - State Manager                                         │
└─────────────────────────────────────────────────────────┘
                         ↓
        ┌────────────────┴─────────────────┐
        ↓                                   ↓
┌──────────────────┐              ┌──────────────────┐
│  Searcher Agent  │              │  Analyst Agent   │
│  (Abliterated)   │              │  (Reasoning)     │
│  - Web Search    │              │  - Validation    │
│  - PDF Extract   │              │  - Critique      │
│  - Summarize     │              │  - Synthesis     │
└──────────────────┘              └──────────────────┘
        ↓                                   ↓
┌─────────────────────────────────────────────────────────┐
│  Tool Library                                           │
│  - @tool decorators (smolagents pattern)                │
│  - Reusable across agents                               │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  Logic Library (JSON Configs)                           │
│  - Workflows, Techniques, Models, Sources               │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  LLM Backend (Ollama)                                   │
│  - Llama-3.1-8B-Abliterated (Searcher)                  │
│  - DeepSeek-R1-32B (Analyst)                            │
└─────────────────────────────────────────────────────────┘
```

---

### Component Architecture

#### 1. Agent System (NEW - CrewAI inspired)

**Agent Definition (JSON):**
```json
{
  "agent_id": "searcher_agent",
  "role": "researcher",
  "goal": "Collect unbiased data from multiple sources",
  "backstory": "Specialized in rapid information gathering without censorship",
  "model_tier": "tier1_fast_abliterated",
  "tools": ["web_search", "pdf_extract", "markdown_reader"],
  "temperature": 0.3,
  "max_tokens": 4096,
  "system_prompt_template": "anti_eliza_researcher"
}
```

**Agent Implementation (Python):**
```python
from dataclasses import dataclass
from typing import List

@dataclass
class Agent:
    agent_id: str
    role: str
    goal: str
    model_tier: str
    tools: List[str]
    temperature: float

    def execute_task(self, task: Task) -> AgentOutput:
        # Load model
        # Apply tools
        # Return structured output
        pass
```

---

#### 2. Task System (NEW - CrewAI inspired)

**Task Definition (JSON):**
```json
{
  "task_id": "research_market_size",
  "description": "Research market size for {product_category} in {region}",
  "agent": "searcher_agent",
  "context_from": ["previous_task_id"],
  "expected_output": {
    "format": "json",
    "schema": {
      "TAM": "number",
      "SAM": "number",
      "SOM": "number",
      "sources": "array"
    }
  },
  "validation": {
    "required_fields": ["TAM", "SAM", "SOM"],
    "min_sources": 3
  }
}
```

---

#### 3. Workflow Engine (ENHANCED - GPT-Researcher loops)

**Linear Workflow (Existing):**
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

**Iterative Workflow (NEW):**
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
      "agent": "searcher_agent",
      "task": "web_research",
      "save_to": "raw_findings"
    },
    {
      "step": 2,
      "agent": "analyst_agent",
      "task": "evaluate_findings",
      "input": "raw_findings",
      "output": "confidence_score"
    },
    {
      "step": 3,
      "condition": "confidence_score < 0.8",
      "agent": "analyst_agent",
      "task": "identify_gaps",
      "loop_to": 1
    }
  ]
}
```

---

#### 4. Tool System (NEW - smolagents pattern)

**Tool Decorator:**
```python
from smolagents import tool

@tool
def web_search(query: str, max_results: int = 10) -> list:
    """Search the web for information.

    Args:
        query: Search query
        max_results: Maximum number of results to return

    Returns:
        List of search results with title, url, snippet
    """
    # Implementation
    pass

@tool
def contradiction_detector(responses: list[str]) -> dict:
    """Detect contradictions between multiple AI responses.

    Args:
        responses: List of AI-generated texts

    Returns:
        Dict with contradictions, severity, resolution steps
    """
    # Use Analyst model
    pass
```

**Tool Registry:**
```json
{
  "tool_id": "web_search",
  "name": "Web Search",
  "category": "data_collection",
  "input_schema": {
    "query": "string",
    "max_results": "integer"
  },
  "output_schema": {
    "results": "array"
  },
  "requires_model": false,
  "python_module": "tools.web_search"
}
```

---

#### 5. Structural Logic Layer (NEW - Executable Phases)

**Phase Definition:**
```json
{
  "phase_id": "phase_0_base_research",
  "name": "Base Research Phase",
  "order": 0,
  "categories": [
    "technical_feasibility",
    "market_opportunity",
    "monetization"
  ],
  "workflow_id": "market_research_collection",
  "exit_criteria_id": "base_research_complete",
  "next_phase": "phase_2_review"
}
```

**Exit Criteria (Executable):**
```json
{
  "criteria_id": "base_research_complete",
  "type": "phase_completion",
  "conditions": {
    "all_of": [
      {
        "type": "file_count",
        "path": "research/base/",
        "expected": 24
      },
      {
        "type": "validation_passed",
        "workflow_id": "research_validation",
        "min_confidence": 0.7
      }
    ]
  }
}
```

---

## 6. Model Strategy

### Hardware Configuration
- **GPU VRAM:** 11GB (RTX 2080 Ti / RTX 3060)
- **System RAM:** 16GB
- **Backend:** Ollama

### Model Tiers (UPDATED with Gemini recommendations)

#### Tier 1: Searcher (Abliterated, Fast)
```json
{
  "model_id": "tier1_searcher",
  "model_name": "llama-3.1-8b-abliterated",
  "source": "FailSpy/Dolphin",
  "quantization": "Q6_K",
  "vram_usage": "~6GB",
  "speed": "30-50 tok/s",
  "agent_role": "researcher",
  "use_cases": [
    "Web research",
    "PDF extraction",
    "Data summarization",
    "Controversial topic research"
  ],
  "temperature": 0.3,
  "system_prompt": "anti_eliza_researcher"
}
```

**Ollama Install:**
```bash
ollama pull llama3.1:8b-instruct-abliterated
```

---

#### Tier 2: Analyst (Reasoning, Deep)
```json
{
  "model_id": "tier2_analyst",
  "model_name": "deepseek-r1-distill-qwen-32b",
  "quantization": "Q4_K_M",
  "vram_usage": "~8GB (VRAM) + ~12GB (RAM)",
  "speed": "1-3 tok/s",
  "agent_role": "analyst",
  "use_cases": [
    "Validation",
    "Contradiction detection",
    "Reasoning",
    "Synthesis"
  ],
  "temperature": 0.5,
  "system_prompt": "anti_eliza_analyst"
}
```

**Ollama Install:**
```bash
ollama pull deepseek-r1:32b-distill-qwen-q4_K_M
```

---

#### Tier 3: Overnight (Optional, Highest Quality)
```json
{
  "model_id": "tier3_overnight",
  "model_name": "dolphin-mixtral-8x7b",
  "quantization": "Q4_K_M",
  "vram_usage": "~8GB (VRAM) + ~20GB (RAM)",
  "speed": "5-10 tok/s",
  "agent_role": "deep_analyst",
  "use_cases": [
    "Overnight re-validation",
    "Final quality check",
    "Complex reasoning"
  ],
  "temperature": 0.5
}
```

---

### Model Selection Logic

**Agent → Model Mapping:**
```python
AGENT_MODEL_MAP = {
    "researcher": "tier1_searcher",
    "summarizer": "tier1_searcher",
    "analyst": "tier2_analyst",
    "validator": "tier2_analyst",
    "deep_analyst": "tier3_overnight"
}
```

**Workflow Example:**
```json
{
  "workflow_id": "complete_research_pipeline",
  "steps": [
    {
      "agent": "researcher",        // Uses tier1_searcher
      "task": "collect_data"
    },
    {
      "agent": "analyst",           // Uses tier2_analyst
      "task": "validate_findings"
    },
    {
      "agent": "summarizer",        // Uses tier1_searcher
      "task": "write_report"
    }
  ]
}
```

---

## 7. Project Structure

### Proposed Directory Layout

```
deep-research-orchestrator/
├── README.md
├── pyproject.toml               # Poetry/pip dependencies
├── .env.example                 # Ollama URL, etc.
│
├── config/
│   ├── agents/                  # Agent definitions
│   │   ├── searcher_agent.json
│   │   ├── analyst_agent.json
│   │   └── summarizer_agent.json
│   │
│   ├── models/                  # Model configurations
│   │   ├── tier1_searcher.json
│   │   ├── tier2_analyst.json
│   │   └── tier3_overnight.json
│   │
│   ├── workflows/               # Workflow definitions
│   │   ├── sequential/
│   │   │   ├── research_validation.json
│   │   │   └── planning_validation.json
│   │   └── iterative/
│   │       ├── deep_research.json
│   │       └── market_analysis.json
│   │
│   ├── phases/                  # Structural logic (NEW)
│   │   ├── phase_0_base_research.json
│   │   ├── phase_2_review.json
│   │   └── phase_3_planning.json
│   │
│   ├── techniques/              # Validation techniques
│   │   ├── contradiction.json
│   │   ├── blind_spots.json
│   │   └── premortem.json
│   │
│   ├── tools/                   # Tool configurations
│   │   ├── web_search.json
│   │   ├── pdf_extract.json
│   │   └── contradiction_detector.json
│   │
│   └── schemas/                 # JSON schemas
│       ├── agent_schema.json
│       ├── task_schema.json
│       ├── workflow_schema.json
│       └── phase_schema.json
│
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── orchestrator.py      # Master agent
│   │   ├── agent.py             # Agent class
│   │   ├── task.py              # Task class
│   │   ├── workflow_engine.py   # Workflow executor
│   │   └── state_manager.py     # State tracking
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── ollama_client.py     # Ollama integration
│   │   ├── model_loader.py      # Load model configs
│   │   └── prompt_templates.py  # Anti-ELIZA prompts
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── base.py              # @tool decorator
│   │   ├── data_collection/
│   │   │   ├── web_search.py
│   │   │   ├── pdf_extract.py
│   │   │   └── markdown_reader.py
│   │   ├── validation/
│   │   │   ├── contradiction.py
│   │   │   ├── blind_spots.py
│   │   │   └── premortem.py
│   │   └── processing/
│   │       ├── summarizer.py
│   │       ├── structurer.py
│   │       └── text_cleaner.py
│   │
│   ├── evaluation/              # Quality assurance (NEW)
│   │   ├── __init__.py
│   │   ├── ragas_evaluator.py
│   │   └── deepeval_checks.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── json_loader.py
│       ├── logger.py
│       └── validators.py
│
├── api/
│   ├── __init__.py
│   ├── app.py                   # Flask application
│   ├── routes/
│   │   ├── research.py          # /api/research
│   │   ├── validate.py          # /api/validate
│   │   ├── chat.py              # /api/chat
│   │   └── status.py            # /api/status
│   └── middleware/
│       ├── auth.py              # CSRF protection
│       └── rate_limit.py        # Rate limiting
│
├── gui/
│   ├── templates/
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── research.html
│   │   ├── validate.html
│   │   └── workflows.html
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── img/
│   └── utils/
│       └── sidebar_generator.py
│
├── docs/
│   ├── frameworks/              # Migrated from product-management
│   │   ├── research-framework.md
│   │   ├── validation-framework.md
│   │   └── planning-framework.md
│   ├── guides/
│   │   ├── quickstart.md
│   │   ├── agent-creation.md
│   │   └── workflow-design.md
│   └── architecture/
│       └── ARCHITECTURE_PLAN_V1.md  # This file
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
└── scripts/
    ├── setup_ollama.sh          # Install models
    ├── migrate_from_old.py      # Migration helper
    └── start_server.sh          # Launch everything
```

---

### Key Differences from Old Structure

**Old (product-management/tools/validator/):**
```
❌ Everything nested in tools/ subfolder
❌ No agent concept
❌ No clear separation: structural vs executable
❌ GUI mixed with backend logic
```

**New (deep-research-orchestrator/):**
```
✅ Clean top-level structure
✅ Agents as first-class citizens
✅ config/ for all JSON logic
✅ src/ for all Python code
✅ api/ and gui/ separated
✅ docs/ for frameworks
```

---

## 8. Migration Plan

### Phase 1: Setup New Project (Day 1)
```bash
# Create new project
mkdir deep-research-orchestrator
cd deep-research-orchestrator

# Initialize git
git init

# Setup Python environment
poetry init
poetry add flask ollama-python pydantic jinja2 requests beautifulsoup4

# Create directory structure
./scripts/create_structure.sh
```

### Phase 2: Migrate Logic Library (Day 1-2)

**A. Copy & Restructure JSONs:**
```bash
# Old location
product-management/tools/validator/logic_library/

# New location
deep-research-orchestrator/config/

# Migration script
python scripts/migrate_from_old.py --step logic_library
```

**B. Enhance JSONs with Agent Roles:**
```python
# Add agent_role to all technique JSONs
{
  "technique_id": "contradiction",
  "agent_role": "analyst",  # NEW
  ...
}
```

### Phase 3: Migrate Python Backend (Day 2-3)

**Priority Order:**
1. ✅ ollama_client.py → src/models/
2. ✅ workflow_engine.py → src/core/
3. ✅ orchestrator.py → src/core/ (enhance with agent support)
4. ✅ state_manager.py → src/core/
5. ✅ Data collection tools → src/tools/data_collection/
6. ✅ Validation tools → src/tools/validation/

**Enhancements:**
- Add Agent class
- Add Task class
- Implement iterative workflow mode
- Add tool decorator system

### Phase 4: Migrate GUI/Server (Day 3-4)

**A. Flask App:**
```bash
# Old: serve_live.py (monolithic)
# New: api/app.py + api/routes/*.py (modular)

python scripts/migrate_from_old.py --step gui
```

**B. Templates:**
```bash
# Copy templates, update paths
cp -r old/viewer/templates/ gui/templates/
# Update base URLs, API endpoints
```

### Phase 5: Test & Validate (Day 4-5)

**A. Unit Tests:**
```python
# tests/unit/test_agent.py
def test_agent_initialization():
    agent = Agent.from_json("config/agents/searcher_agent.json")
    assert agent.role == "researcher"

# tests/unit/test_workflow.py
def test_sequential_workflow():
    workflow = Workflow.load("config/workflows/sequential/research_validation.json")
    result = workflow.execute()
    assert result.status == "completed"
```

**B. Integration Tests:**
```bash
# Start Ollama
ollama serve

# Test full pipeline
pytest tests/integration/test_research_pipeline.py
```

---

## 9. Implementation Phases

### Sprint 1: Foundation (Week 1)

**Goals:**
- ✅ New project structure created
- ✅ Core classes implemented (Agent, Task, Workflow)
- ✅ Ollama integration working
- ✅ JSON configs migrated

**Deliverables:**
```python
# Basic usage
from src.core.agent import Agent
from src.core.task import Task

searcher = Agent.from_json("config/agents/searcher_agent.json")
task = Task.from_json("config/tasks/web_research.json")

result = searcher.execute_task(task)
print(result.output)
```

---

### Sprint 2: Agent System (Week 2)

**Goals:**
- ✅ Multi-agent orchestration working
- ✅ Task chaining implemented
- ✅ Tool decorator system functional
- ✅ Searcher + Analyst agents tested

**Deliverables:**
```python
# Multi-agent workflow
from src.core.orchestrator import Orchestrator

orchestrator = Orchestrator()
workflow = orchestrator.load_workflow("config/workflows/deep_research.json")

result = workflow.execute({
    "query": "What is the market size for AI tutoring apps?"
})

print(result.final_report)
print(result.confidence_score)
```

---

### Sprint 3: Iterative Workflows (Week 3)

**Goals:**
- ✅ Iterative loop logic implemented
- ✅ Exit criteria evaluation working
- ✅ Gap detection & refinement loops
- ✅ Confidence-based iteration

**Deliverables:**
```json
// Iterative workflow in action
{
  "workflow_id": "deep_research",
  "iterations": 3,
  "confidence_progression": [0.4, 0.65, 0.82],
  "exit_reason": "confidence_threshold_reached"
}
```

---

### Sprint 4: GUI & API (Week 4)

**Goals:**
- ✅ Flask API endpoints functional
- ✅ GUI templates migrated
- ✅ Live server with auto-reload
- ✅ Dashboard showing agent activity

**Deliverables:**
- Working web interface at http://localhost:8000/gui
- API endpoints documented
- Real-time workflow monitoring

---

### Sprint 5: Quality & Evaluation (Week 5)

**Goals:**
- ✅ RAGAS evaluation integrated
- ✅ Anti-ELIZA prompts deployed
- ✅ Model strategy implemented (Searcher vs Analyst)
- ✅ Abliterated models tested

**Deliverables:**
```python
# Quality metrics
from src.evaluation.ragas_evaluator import evaluate_research

metrics = evaluate_research(
    query="...",
    output="...",
    sources=[...]
)

assert metrics["faithfulness"] > 0.7
assert metrics["answer_relevance"] > 0.8
```

---

## 10. Open Questions

### For Review & Decision

**A. Framework Choices:**
- [ ] Should we integrate smolagents as a dependency or just adopt the @tool pattern?
- [ ] Do we need LangGraph now or wait until we have conditional workflows?
- [ ] CrewAI dependency or just implement the agent pattern ourselves?

**B. Model Strategy:**
- [ ] Can we source Llama-3.1-8B-Abliterated models reliably?
- [ ] Should we test DeepSeek-R1-32B on your hardware first?
- [ ] Fallback strategy if models don't fit in VRAM?

**C. Migration:**
- [ ] Migrate incrementally or fresh start?
- [ ] Keep old project running during migration?
- [ ] Timeline: 2 weeks or 4 weeks?

**D. Features:**
- [ ] Priority: Iterative workflows or multi-agent first?
- [ ] GUI complexity: Full dashboard or minimal interface?
- [ ] Authentication needed for local-only use?

---

## Next Steps

### Immediate Actions (This Session)

1. **Review this document**
   - Read through all sections
   - Mark sections for adjustment: ✏️ ADJUST or ✅ APPROVED
   - Add comments/questions inline

2. **Prioritize features**
   - Rank Sprint 1-5 features
   - Identify must-haves vs nice-to-haves

3. **Make decisions on open questions**
   - Answer A, B, C, D sections
   - Clarify preferences

### After Review

4. **Create refined architecture doc (V2)**
   - Incorporate your feedback
   - Finalize decisions
   - Add implementation details

5. **Start implementation**
   - Bootstrap new project
   - Implement Sprint 1
   - Test with real workflows

---

## Appendix: Resources

### External Projects
- GPT-Researcher: https://github.com/run-llm/gpt-researcher
- CrewAI: https://github.com/joaomdmoura/crewai
- LangGraph: https://langchain-ai.github.io/langgraph/
- smolagents: https://github.com/huggingface/smolagents

### Model Sources
- Llama Abliterated: https://huggingface.co/FailSpy
- DeepSeek R1: https://huggingface.co/deepseek-ai
- Ollama Models: https://ollama.com/library

### Quality Frameworks
- RAGAS: https://github.com/explodinggradients/ragas
- DeepEval: https://github.com/confident-ai/deepeval

---

**END OF DOCUMENT**

**Status:** Ready for Review
**Action Required:** Please read, annotate, and provide feedback on all sections.
**Next Version:** V2 will incorporate your decisions and refinements.
