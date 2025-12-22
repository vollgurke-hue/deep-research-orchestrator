# Deep Research Orchestrator - Architecture Plan V2.1 FINAL

**Date:** 2025-12-21
**Version:** 2.1 (Hardware-Corrected + GUI Logic Builder Concept)
**Status:** FINAL - Ready for Implementation

---

## Table of Contents

1. [Hardware Configuration](#1-hardware-configuration)
2. [Core Architecture](#2-core-architecture)
3. [Model Strategy (llama.cpp)](#3-model-strategy-llamacpp)
4. [Multi-AI Workflow](#4-multi-ai-workflow-manual-orchestration)
5. [GUI Logic Builder Concept](#5-gui-logic-builder-concept-new)
6. [Future Features (Documented)](#6-future-features-documented)
7. [Project Structure](#7-project-structure)
8. [Migration Strategy](#8-migration-strategy)
9. [Implementation Phases](#9-implementation-phases)

---

## 1. Hardware Configuration

### Actual System Specs

**GPUs:**
- **GPU 1:** NVIDIA GeForce RTX 3060 Ti - **8GB VRAM**
- **GPU 2:** NVIDIA GeForce GTX 1060 - **3GB VRAM**
- **Total VRAM:** 11GB (8GB + 3GB)

**Memory:**
- **System RAM:** 15GB (14.3GB actual)
- **Swap:** 11GB
- **Total Available Memory:** ~26GB (15GB RAM + 11GB Swap)

**Usable Strategy:**
- Primary GPU (RTX 3060 Ti 8GB) for main workload
- Secondary GPU (GTX 1060 3GB) for auxiliary tasks or offloading
- RAM + Swap for large model layers

---

## 2. Core Architecture

### High-Level System Design

```
┌─────────────────────────────────────────────────────────┐
│  USER LAYER                                             │
│  - Manual prompt creation                               │
│  - External AI queries (Claude, GPT, Gemini)            │
│  - GUI (minimal, existing gui/app.py)                   │
│  - Logic Builder GUI (future enhancement)               │
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
│  (8B Abliterated)│              │  (32B Abliterated)│
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
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  LLM BACKEND (llama.cpp)                                │
│  - Fast: Llama-3.1-8B-Abliterated (GPU 1: 8GB VRAM)     │
│  - Quality: 32B Abliterated (GPU 1 + RAM split)         │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  STORAGE LAYER                                          │
│  - research-data/ (Multi-AI responses, validations)     │
│  - planning_state.json (Progress tracking)              │
└─────────────────────────────────────────────────────────┘
```

---

## 3. Model Strategy (llama.cpp)

### Hardware-Optimized Configuration

**GPU Setup:**
- Use RTX 3060 Ti (8GB) as primary
- GTX 1060 (3GB) as auxiliary or disabled (too small for current models)
- Strategy: Single-GPU with RAM offloading

### Model Tiers

#### Tier 1: Fast Agent (Fully in VRAM)

**Model:** Llama-3.1-8B-Instruct-Abliterated
**Quantization:** Q6_K
**Size:** ~7GB
**Deployment:**
- **VRAM (RTX 3060 Ti):** 7GB
- **RAM:** 0GB
- **Speed:** 50-80 tok/s

**llama.cpp Command:**
```bash
./llama-cli \
  --model models/Llama-3.1-8B-Instruct-Abliterated-Q6_K.gguf \
  --n-gpu-layers 999 \       # All layers on GPU
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

**Model Options:**

**Option A: Qwen2.5-32B-Instruct-Abliterated** (Recommended)
- **Quantization:** Q4_K_M
- **Total Size:** ~20GB
- **Deployment:**
  - VRAM (RTX 3060 Ti): 8GB (~16-18 layers)
  - RAM: ~12GB (remaining layers)
- **Speed:** 3-8 tok/s
- **Quality:** Excellent reasoning

**Option B: Mixtral-8x7B-Instruct-Abliterated** (Alternative)
- **Quantization:** Q4_K_M
- **Total Size:** ~26GB
- **Deployment:**
  - VRAM: 8GB (~10-12 layers)
  - RAM: ~18GB (remaining layers)
- **Speed:** 2-5 tok/s
- **Quality:** Very good multi-task performance

**Option C: Llama-3.1-70B-Instruct-Abliterated** (Maximum Quality)
- **Quantization:** Q3_K_S (aggressive)
- **Total Size:** ~26GB
- **Deployment:**
  - VRAM: 8GB (~8-10 layers)
  - RAM: ~18GB (remaining layers)
- **Speed:** 1-3 tok/s
- **Quality:** Best possible
- **Note:** May use Swap if RAM pressure high

**Recommended Start:** Option A (Qwen 32B)

**llama.cpp Command (Qwen 32B):**
```bash
./llama-cli \
  --model models/Qwen2.5-32B-Instruct-Abliterated-Q4_K_M.gguf \
  --n-gpu-layers 16 \        # ~8GB VRAM, rest in RAM
  --ctx-size 8192 \
  --threads 8 \
  --batch-size 512
```

**Use Cases:**
- Deep validation (contradiction, blind spots)
- Research synthesis
- Premortem analysis
- Complex reasoning tasks

---

### GPU Selection Strategy

**Single-GPU Approach (Recommended):**
```bash
# Use only RTX 3060 Ti (8GB)
export CUDA_VISIBLE_DEVICES=0

# Or specify in llama.cpp
--main-gpu 0
```

**Dual-GPU Approach (Experimental):**
```bash
# Distribute across both GPUs
export CUDA_VISIBLE_DEVICES=0,1

# Fast model on RTX 3060 Ti, auxiliary on GTX 1060
# (Requires manual layer distribution - complex)
```

**Decision:** Start with single-GPU (RTX 3060 Ti). Dual-GPU later if needed.

---

### Memory Monitoring

**Before running Quality Agent:**
```bash
# Check available VRAM
nvidia-smi

# Check available RAM
free -h

# Monitor during execution
watch -n 1 nvidia-smi
```

**Adjust `--n-gpu-layers` based on actual VRAM usage:**
- Start with 16 layers
- If VRAM < 8GB used: increase layers
- If VRAM > 8GB or OOM: decrease layers

---

## 4. Multi-AI Workflow (Manual Orchestration)

### Workflow Overview

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

Step 4: Quality Pattern Learning (Optional - Future)
  ↓
  Analyze response quality patterns across many prompts
  Extract what makes good responses
  Feed insights back into prompt generation
```

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
    from src.tools.multi_ai.prompt_generator import MultiAIPromptGenerator

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

---

## 5. GUI Logic Builder Concept (NEW)

### Problem Statement

**Current Situation:**
- Product Management frameworks define complex CoT workflows in Markdown
- Workflows consist of:
  - **Phases** (e.g., Phase 0: Base Research, Phase 2: Review)
  - **Categories** (e.g., Technical Feasibility, Market Opportunity)
  - **Sub-Categories** (e.g., Tech Stack, Architecture)
  - **Techniques** (e.g., contradiction, blind_spots)
  - **Exit Criteria** (e.g., "All 24 files complete")

**Goal:**
- Break down these complex workflows into **small logic building blocks**
- Create a **GUI** where users can:
  - View existing logic blocks (Techniques, Workflows, Phases)
  - Combine blocks to create new workflows
  - Load and execute complex workflows built from small pieces

### Conceptual Architecture

```
┌─────────────────────────────────────────────────────────┐
│  LOGIC LIBRARY (Small Building Blocks)                  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  1. ATOMIC TECHNIQUES                                    │
│     - contradiction.json                                 │
│     - blind_spots.json                                   │
│     - premortem.json                                     │
│                                                          │
│  2. COMPOSITE WORKFLOWS (Technique Chains)               │
│     - research_validation.json                           │
│       = contradiction + blind_spots + premortem          │
│                                                          │
│  3. PHASES (Workflow + Exit Criteria)                    │
│     - phase_0_base_research.json                         │
│       = workflow_id + exit_criteria_id + categories      │
│                                                          │
│  4. COMPLETE FRAMEWORKS (Phase Chains)                   │
│     - product_research_framework.json                    │
│       = Phase 0 → Phase 2 → Phase 3                      │
│                                                          │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  GUI LOGIC BUILDER                                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  [SIDEBAR]                    [CANVAS]                  │
│                                                          │
│  📦 Techniques                 ┌──────────────┐         │
│    - contradiction             │ Workflow 1   │         │
│    - blind_spots               │              │         │
│    - premortem                 │ [Technique]  │         │
│                                │      ↓       │         │
│  🔗 Workflows                  │ [Technique]  │         │
│    - research_validation       │      ↓       │         │
│    - planning_validation       │ [Technique]  │         │
│                                └──────────────┘         │
│  🎯 Phases                                              │
│    - Phase 0: Base Research    [+ Add Technique]        │
│    - Phase 2: Review           [+ Save Workflow]        │
│                                                          │
│  📋 Frameworks                 ┌──────────────┐         │
│    - Product Research          │ Framework    │         │
│                                │              │         │
│                                │  Phase 0     │         │
│                                │     ↓        │         │
│                                │  Phase 2     │         │
│                                │     ↓        │         │
│                                │  Phase 3     │         │
│                                └──────────────┘         │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Logic Hierarchy

**Level 1: Atomic Techniques**
```json
// config/techniques/contradiction.json
{
  "technique_id": "contradiction",
  "name": "Contradiction Detection",
  "type": "atomic",
  "prompt": "...",
  "inputs": ["responses"],
  "outputs": ["contradictions"]
}
```

**Level 2: Composite Workflows**
```json
// config/workflows/research_validation.json
{
  "workflow_id": "research_validation",
  "name": "Research Validation Workflow",
  "type": "composite",
  "building_blocks": [
    {
      "block_type": "technique",
      "block_id": "contradiction",
      "order": 1
    },
    {
      "block_type": "technique",
      "block_id": "blind_spots",
      "order": 2,
      "input_from": "contradiction"
    },
    {
      "block_type": "technique",
      "block_id": "premortem",
      "order": 3,
      "input_from": "blind_spots"
    }
  ],
  "exit_criteria": {
    "type": "all_complete"
  }
}
```

**Level 3: Phases**
```json
// config/phases/phase_0_base_research.json
{
  "phase_id": "phase_0_base_research",
  "name": "Base Research Phase",
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
    "type": "custom",
    "criteria_id": "base_research_complete"
  }
}
```

**Level 4: Complete Frameworks**
```json
// config/frameworks/product_research_framework.json
{
  "framework_id": "product_research_framework",
  "name": "Product Research Framework",
  "type": "framework",
  "building_blocks": [
    {
      "block_type": "phase",
      "block_id": "phase_0_base_research",
      "order": 1
    },
    {
      "block_type": "phase",
      "block_id": "phase_2_review",
      "order": 2,
      "depends_on": "phase_0_base_research"
    },
    {
      "block_type": "phase",
      "block_id": "phase_3_planning",
      "order": 3,
      "depends_on": "phase_2_review"
    }
  ]
}
```

### GUI Features (Future Implementation)

**A. Block Browser**
- View all available blocks by type
- Search/filter blocks
- Preview block details (inputs, outputs, description)

**B. Workflow Canvas**
- Drag-and-drop techniques onto canvas
- Connect blocks (output → input)
- Visual flow representation
- Validation (missing inputs, circular dependencies)

**C. Block Composer**
- Create new workflows from techniques
- Save custom workflows as new blocks
- Test workflows before saving

**D. Framework Runner**
- Load complete frameworks
- Execute phase-by-phase
- Track progress in real-time
- Pause/resume execution

### Implementation Notes

**Priority:** LOW (Document now, implement later)

**Technical Approach:**
- Backend: JSON-based block definitions (already have this!)
- Frontend: JavaScript canvas library (e.g., jsPlumb, React Flow)
- Validation: Check block compatibility (output types match input types)

**Why This Matters:**
- Makes complex Product Management workflows **visual and composable**
- Users can create custom research workflows **without coding**
- Enables **reusable logic libraries** across projects

---

## 6. Future Features (Documented)

### A. Knowledge Graphs (DEFERRED)

**Concept:** Structure all research contexts as entity-relationship graphs

**Use Cases (Unclear - To Explore Later):**
- Visualize relationships between concepts
- Query graph for insights
- Track entity evolution over time

**Status:** Documented for future exploration, no immediate implementation

**Notes:**
- Unclear exactly how to use in research context
- Potential for organizing complex domain knowledge
- Revisit after core functionality is stable

---

### B. Quality Pattern Learning (FUTURE)

**Concept:** Analyze response quality patterns from large AI models

**Workflow:**
1. Collect many Multi-AI responses over time
2. Analyze what makes high-quality responses
3. Extract patterns (tone, structure, depth)
4. Feed insights back into prompt generation

**Status:** Documented, implement when sufficient data collected

---

## 7. Project Structure

### Directory Layout

```
deep-research-orchestrator/
├── README.md
├── pyproject.toml
├── .env.example
├── .gitignore
│
├── config/
│   ├── agents/
│   │   ├── fast_researcher.json
│   │   └── quality_validator.json
│   │
│   ├── models/
│   │   ├── tier1_fast.json
│   │   └── tier2_quality.json
│   │
│   ├── workflows/
│   │   ├── sequential/
│   │   │   ├── research_validation.json
│   │   │   └── planning_validation.json
│   │   └── iterative/
│   │       ├── deep_research.json
│   │       └── market_analysis.json
│   │
│   ├── phases/                   # NEW (for Logic Builder)
│   │   ├── phase_0_base_research.json
│   │   ├── phase_2_review.json
│   │   └── phase_3_planning.json
│   │
│   ├── frameworks/               # NEW (for Logic Builder)
│   │   └── product_research_framework.json
│   │
│   ├── techniques/
│   │   ├── contradiction.json
│   │   ├── blind_spots.json
│   │   ├── premortem.json
│   │   ├── consensus.json
│   │   ├── red_flags.json
│   │   ├── sanity_check.json
│   │   └── scenario_analysis.json
│   │
│   ├── tools/
│   │   ├── web_scraper.json
│   │   ├── pdf_extractor.json
│   │   └── contradiction_detector.json
│   │
│   └── schemas/
│       ├── agent_schema.json
│       ├── workflow_schema.json
│       ├── phase_schema.json          # NEW
│       └── framework_schema.json      # NEW
│
├── src/
│   ├── __init__.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── orchestrator.py
│   │   ├── agent.py
│   │   ├── task.py
│   │   ├── workflow_engine.py
│   │   └── state_manager.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── llama_cpp_client.py
│   │   ├── model_loader.py
│   │   └── prompt_templates.py
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   │
│   │   ├── data_collection/
│   │   │   ├── __init__.py
│   │   │   ├── web_scraper.py
│   │   │   ├── pdf_extractor.py
│   │   │   └── markdown_reader.py
│   │   │
│   │   ├── validation/
│   │   │   ├── __init__.py
│   │   │   ├── contradiction.py
│   │   │   ├── blind_spots.py
│   │   │   ├── premortem.py
│   │   │   ├── consensus.py
│   │   │   ├── red_flags.py
│   │   │   └── sanity_check.py
│   │   │
│   │   ├── processing/
│   │   │   ├── __init__.py
│   │   │   ├── text_cleaner.py
│   │   │   ├── structurer.py
│   │   │   └── summarizer.py
│   │   │
│   │   └── multi_ai/
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
├── gui/                          # Existing GUI (preserve as-is)
│   ├── app.py
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
│   ├── frameworks/
│   │   ├── research-framework.md
│   │   ├── validation-framework.md
│   │   └── planning-framework.md
│   ├── guides/
│   │   ├── quickstart.md
│   │   ├── llama-cpp-setup.md
│   │   └── multi-ai-workflow.md
│   └── architecture/
│       ├── ARCHITECTURE_PLAN_V1.md
│       ├── ARCHITECTURE_PLAN_V2.md
│       └── ARCHITECTURE_PLAN_V2.1_FINAL.md
│
├── research-data/
│   ├── multi-ai/
│   ├── validations/
│   └── iterations/
│
├── research-prompts/
│
├── models/
│   ├── Llama-3.1-8B-Instruct-Abliterated-Q6_K.gguf
│   └── Qwen2.5-32B-Instruct-Abliterated-Q4_K_M.gguf
│
├── llama.cpp/
│   └── llama-cli
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
└── scripts/
    ├── setup_llama_cpp.sh
    ├── download_models.sh
    ├── migrate_from_old.py
    └── start_server.sh
```

---

## 8. Migration Strategy

### Phase 1: Bootstrap New Project (Day 1)

**A. Create Structure**
```bash
# Clone fresh
mkdir deep-research-orchestrator
cd deep-research-orchestrator

# Initialize
git init
touch README.md pyproject.toml .gitignore

# Create directories (see structure above)
./scripts/create_structure.sh
```

**B. Setup llama.cpp**
```bash
# Download llama.cpp
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp

# Build with CUDA support (single-GPU setup)
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

# Download quality model (32B - Qwen recommended)
huggingface-cli download Qwen/Qwen2.5-32B-Instruct-GGUF \
  Qwen2.5-32B-Instruct-Q4_K_M.gguf \
  --local-dir models/

# Note: Check for abliterated versions on HuggingFace
```

**D. Test Single-GPU Setup**
```bash
# Ensure only RTX 3060 Ti is used
export CUDA_VISIBLE_DEVICES=0

# Test fast model
./llama.cpp/llama-cli \
  --model models/Llama-3.1-8B-Abliterated.gguf \
  --prompt "Explain AI in 2 sentences" \
  --n-gpu-layers 999

# Test quality model with RAM offloading
./llama.cpp/llama-cli \
  --model models/Qwen2.5-32B-Abliterated.gguf \
  --prompt "Explain AI in 2 sentences" \
  --n-gpu-layers 16 \  # Start with 16, adjust based on VRAM usage
  --ctx-size 8192
```

---

### Phase 2: Migrate Core Components (Day 2-3)

**Priority Order:**

**1. JSON Configs (High Priority)**
```bash
# Copy logic library
cp -r ../ai-tutoring-app/product-management/tools/validator/logic_library/techniques/ config/techniques/
cp -r ../ai-tutoring-app/product-management/tools/validator/logic_library/workflows/ config/workflows/sequential/
cp -r ../ai-tutoring-app/product-management/tools/validator/logic_library/sources/ config/tools/

# Update model configs for llama.cpp
python scripts/migrate_from_old.py --update-model-configs
```

**2. Core Python Files**
```bash
# Migrate core
cp ../ai-tutoring-app/product-management/tools/validator/src/orchestrator.py src/core/
cp ../ai-tutoring-app/product-management/tools/validator/src/workflow_engine.py src/core/
cp ../ai-tutoring-app/product-management/tools/validator/src/state_manager.py src/core/

# Migrate tools
cp ../ai-tutoring-app/product-management/tools/validator/src/sources/web_scraper.py src/tools/data_collection/
cp ../ai-tutoring-app/product-management/tools/validator/src/sources/pdf_extractor.py src/tools/data_collection/
cp ../ai-tutoring-app/product-management/tools/validator/src/processors/text_cleaner.py src/tools/processing/

# Adapt orchestrator to use LlamaCppClient
# (Manual editing required)
```

**3. GUI (Use As-Is)**
```bash
# Copy existing GUI
cp ../ai-tutoring-app/product-management/tools/validator/gui/app.py gui/
cp -r ../ai-tutoring-app/product-management/tools/validator/gui/templates/ gui/
cp -r ../ai-tutoring-app/product-management/tools/validator/gui/static/ gui/

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
# Implement Agent class (custom)
```

**B. Iterative Workflows**
```python
# src/core/workflow_engine.py
# Add iterative mode support
```

**C. llama.cpp Integration**
```python
# src/models/llama_cpp_client.py
# Implement LlamaCppClient with single-GPU optimization
```

**D. Multi-AI Tools**
```python
# src/tools/multi_ai/prompt_generator.py
# src/tools/multi_ai/response_analyzer.py
```

---

## 9. Implementation Phases

### Sprint 1: Foundation (Week 1)

**Goals:**
- ✅ New project structure created
- ✅ llama.cpp installed and tested
- ✅ Models downloaded and verified (8B + 32B)
- ✅ Single-GPU setup optimized (RTX 3060 Ti)
- ✅ Core classes implemented (Agent, Task, Orchestrator)
- ✅ LlamaCppClient working

**Deliverables:**
```python
# Basic test
from src.core.agent import Agent
from src.models.llama_cpp_client import LlamaCppClient

# Test fast model (fully in VRAM)
client_fast = LlamaCppClient(
    model_path="models/Llama-3.1-8B-Abliterated.gguf",
    n_gpu_layers=999
)
response = client_fast.generate("Explain AI in 2 sentences")
print(response)

# Test quality model (VRAM + RAM split)
client_quality = LlamaCppClient(
    model_path="models/Qwen2.5-32B-Abliterated.gguf",
    n_gpu_layers=16  # Adjust based on VRAM monitoring
)
response = client_quality.generate("Perform deep analysis of AI impact")
print(response)
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

# After manual querying...
analysis = analyze_multi_ai_responses(
    response_dir=Path("research-data/multi-ai/run_001/")
)

print(f"Contradictions: {len(analysis['contradictions'])}")
print(f"Synthesis: {analysis['synthesis']}")
```

---

### Sprint 4: Logic Builder Foundation (Week 4+)

**Goals:**
- ✅ Phase and Framework JSONs defined
- ✅ Block composition logic implemented
- ✅ Basic block validation working

**Deliverables:**
```python
from src.core.framework_loader import FrameworkLoader

loader = FrameworkLoader()
framework = loader.load("product_research_framework")

print(f"Phases: {len(framework.phases)}")
print(f"Total building blocks: {framework.count_blocks()}")
```

---

### Future: GUI Logic Builder (Month 2+)

**Deferred until core functionality is stable**

---

## 10. Key Takeaways

### Hardware-Optimized Strategy
- Use RTX 3060 Ti (8GB) as primary GPU
- Fast model (8B): Fully in VRAM
- Quality model (32B): Split VRAM + RAM (adjust `--n-gpu-layers` based on monitoring)
- Single-GPU setup (simpler, more stable)

### Development Priorities
1. ⭐ Iterative workflows (Sprint 2)
2. ⭐ Multi-AI integration (Sprint 3)
3. ⭐ Logic Builder foundation (Sprint 4)
4. GUI enhancements (Later)
5. Knowledge Graphs (Future exploration)

### Deferred Features
- Knowledge Graphs (unclear use case - revisit later)
- Quality Pattern Learning (needs data collection first)
- GUI Logic Builder UI (foundation first, UI later)

---

**END OF DOCUMENT**

**Status:** FINAL
**Action:** Bootstrap project and start Sprint 1
**Hardware:** Confirmed for RTX 3060 Ti (8GB) + 15GB RAM
**Next:** Create project structure and test llama.cpp setup
