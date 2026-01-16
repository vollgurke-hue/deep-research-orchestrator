# Teil 3: Use Cases & Workflows

**Zweck:** Praktische End-to-End Beispiele für typische Anwendungsfälle

---

## Inhaltsverzeichnis

1. [Use Case 1: Product Research](#use-case-1-product-research)
2. [Use Case 2: Multi-AI Research Campaign](#use-case-2-multi-ai-research-campaign)
3. [Use Case 3: Iterative Deep Research](#use-case-3-iterative-deep-research)
4. [Use Case 4: Custom Workflow Creation](#use-case-4-custom-workflow-creation)
5. [Use Case 5: Framework Composition](#use-case-5-framework-composition)
6. [Troubleshooting](#troubleshooting)

---

## Use Case 1: Product Research

### Szenario
Du willst ein neues Produkt (z.B. "AI Tutoring Platform") erforschen und brauchst:
- Marktanalyse
- Technische Machbarkeit
- Wettbewerbsanalyse
- Validierung der Erkenntnisse
- Abschlussbericht

### Lösung: Framework Execution

#### Schritt 1: Framework verstehen
```bash
# Zeige verfügbare Frameworks
python3 -c "
from src.core.framework_loader import FrameworkLoader
loader = FrameworkLoader()
print(loader.list_frameworks())
"
```

**Output:**
```
[
  {
    "framework_id": "framework_product_research",
    "path": "config/frameworks/framework_product_research.json"
  }
]
```

#### Schritt 2: Framework-Struktur inspizieren
```python
from src.core.framework_loader import FrameworkLoader

loader = FrameworkLoader()
framework = loader.load_framework("framework_product_research")

print(f"Framework: {framework.name}")
print(f"Description: {framework.description}")
print("\nPhasen:")

for block in framework.building_blocks:
    phase = loader.load_phase(block["block_id"])
    print(f"\n{phase.name} ({phase.block_id})")
    print(f"  Order: {block['order']}")
    print(f"  Workflows:")
    for wb in phase.building_blocks:
        print(f"    - {wb['block_id']} ({wb.get('category', 'N/A')})")
```

**Output:**
```
Framework: Product Research Framework
Description: Complete product research workflow from initial research to validated planning

Phasen:

Base Research Phase (phase_0_base_research)
  Order: 1
  Workflows:
    - market_research_collection (market_opportunity)
    - tech_feasibility_collection (technical_feasibility)
    - competitor_analysis_collection (competition)

Validation Phase (phase_2_validation)
  Order: 2
  Workflows:
    - research_validation (quality_assurance)
    - validation_loop (iterative_refinement)

Synthesis & Planning Phase (phase_3_synthesis)
  Order: 3
  Workflows:
    - planning_validation (strategic_planning)
```

#### Schritt 3: Framework ausführen
```python
from src.core.orchestrator import Orchestrator

orchestrator = Orchestrator()

# Execute complete framework
result = orchestrator.execute_framework(
    framework_id="framework_product_research",
    inputs={
        "product": "AI Tutoring Platform",
        "target_market": "K-12 Education",
        "focus_areas": ["market_size", "competition", "tech_requirements"]
    }
)

# Inspect results
print(f"Framework Status: {result['status']}")
print(f"Phases Completed: {len(result['phase_results'])}\n")

for phase_result in result['phase_results']:
    print(f"Phase: {phase_result['phase_id']}")
    print(f"  Status: {phase_result['status']}")
    print(f"  Confidence: {phase_result['confidence']:.2f}")
    print(f"  Outputs: {len(phase_result['outputs'])} items")
    print()

# Access final synthesis
final_output = result['final_output']
print("Final Report:")
print(final_output)
```

**Expected Output:**
```
Framework Status: success
Phases Completed: 3

Phase: phase_0_base_research
  Status: success
  Confidence: 0.72
  Outputs: 3 items

Phase: phase_2_validation
  Status: success
  Confidence: 0.85
  Outputs: 2 items

Phase: phase_3_synthesis
  Status: success
  Confidence: 0.91
  Outputs: 1 items

Final Report:
[Comprehensive research synthesis with market data, validation results, and strategic recommendations]
```

#### Schritt 4: Speichern & Weiterverarbeiten
```python
from pathlib import Path
import json

# Save results
output_dir = Path("research-data/product-research/")
output_dir.mkdir(parents=True, exist_ok=True)

# Save full result
with open(output_dir / "full_result.json", "w") as f:
    json.dump(result, f, indent=2)

# Save final report
with open(output_dir / "final_report.md", "w") as f:
    f.write(f"# Product Research: AI Tutoring Platform\n\n")
    f.write(result['final_output'])

print(f"Results saved to: {output_dir}")
```

---

## Use Case 2: Multi-AI Research Campaign

### Szenario
Du brauchst hochqualitative Marktanalyse und willst Claude, GPT-4 und Gemini nutzen, dann die Antworten lokal zusammenführen.

### Workflow

#### Phase 1: Prompt Generation (Lokal)

```python
from src.tools.multi_ai.prompt_generator import generate_multi_ai_prompt

# Generate comprehensive prompt
prompt_data = generate_multi_ai_prompt(
    topic="AI Tutoring Market Analysis 2025",
    categories=[
        "market_size",
        "competition",
        "trends",
        "technical_feasibility",
        "user_needs"
    ],
    depth="comprehensive",
    output_format="markdown"
)

print(f"Prompt saved to: {prompt_data['save_path']}")
print("\nInstructions:")
print(prompt_data['instructions'])
print("\n" + "="*60)
print("PROMPT:")
print("="*60)
print(prompt_data['prompt'])
```

**Output:**
```
Prompt saved to: research-prompts/prompt_20250123_1430.md

Instructions:
Copy this prompt to Claude, GPT-4, and Gemini.
Save each response to research-data/multi-ai/run_001/ as:
  - claude_response.md
  - gpt4_response.md
  - gemini_response.md

============================================================
PROMPT:
============================================================

# AI Tutoring Market Analysis 2025

Please provide a comprehensive analysis covering:

## 1. Market Size & Opportunity
- Total Addressable Market (TAM)
- Serviceable Available Market (SAM)
- Serviceable Obtainable Market (SOM)
- Growth rate (CAGR 2020-2030)
- Market drivers and barriers

## 2. Competitive Landscape
[... detailed prompt continues ...]
```

#### Phase 2: Manual Querying (User Action)

1. **Claude (claude.ai):**
   - Paste prompt
   - Copy response ’ `research-data/multi-ai/run_001/claude_response.md`

2. **GPT-4 (chat.openai.com):**
   - Paste prompt
   - Copy response ’ `research-data/multi-ai/run_001/gpt4_response.md`

3. **Gemini (gemini.google.com):**
   - Paste prompt
   - Copy response ’ `research-data/multi-ai/run_001/gemini_response.md`

#### Phase 3: Local Analysis (Automatisch)

```python
from pathlib import Path
from src.tools.multi_ai.response_analyzer import analyze_multi_ai_responses

# Analyze all responses
analysis = analyze_multi_ai_responses(
    response_dir=Path("research-data/multi-ai/run_001/"),
    analysis_types=["contradiction", "blind_spots", "consensus", "synthesis"]
)

# Inspect results
print("=== Multi-AI Analysis Results ===\n")

print(f"Responses analyzed: {len(analysis['responses'])}")
print(f"Confidence Score: {analysis['confidence_score']:.2f}\n")

print("Contradictions:")
for i, contradiction in enumerate(analysis['contradictions'], 1):
    print(f"{i}. Topic: {contradiction['topic']}")
    print(f"   {contradiction['source_a']} says: {contradiction['statement_a']}")
    print(f"   {contradiction['source_b']} says: {contradiction['statement_b']}")
    print(f"   Severity: {contradiction.get('severity', 'medium')}\n")

print("\nBlind Spots (Missing Information):")
for spot in analysis['blind_spots']:
    print(f"  - {spot}")

print("\nConsensus Findings:")
for topic, finding in analysis['consensus'].items():
    print(f"  - {topic}: {finding}")

print("\n" + "="*60)
print("SYNTHESIS REPORT:")
print("="*60)
print(analysis['synthesis'])

# Save synthesis
output_path = Path("research-data/validations/synthesis_report.md")
output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(analysis['synthesis'])
print(f"\nSynthesis saved to: {output_path}")
```

**Expected Output:**
```
=== Multi-AI Analysis Results ===

Responses analyzed: 3
Confidence Score: 0.87

Contradictions:
1. Topic: market_size_estimate
   claude says: TAM is $15B by 2025
   gpt4 says: TAM is $12B by 2025
   Severity: medium

Blind Spots (Missing Information):
  - Missing: regulatory considerations for K-12 AI usage
  - Missing: geographical breakdown beyond US market
  - Missing: pricing strategy analysis

Consensus Findings:
  - growth_rate: All agree 15-20% CAGR 2020-2030
  - top_competitors: Consistent identification of Duolingo, Khan Academy, Coursera
  - key_trend: Personalized adaptive learning highlighted by all

============================================================
SYNTHESIS REPORT:
============================================================

# AI Tutoring Market Analysis - Multi-Source Synthesis

## Market Overview
Based on analysis of Claude, GPT-4, and Gemini responses, the AI tutoring
market shows strong consensus on growth trajectory (15-20% CAGR) but varies
in TAM estimates ($12-15B range). The variance is within acceptable bounds
and likely reflects different segmentation approaches.

[... comprehensive synthesis continues ...]
```

---

## Use Case 3: Iterative Deep Research

### Szenario
Du hast eine komplexe Fragestellung und brauchst mehrere Refinement-Loops, bis die Confidence hoch genug ist.

### Workflow

#### Schritt 1: Iterativen Workflow ausführen

```python
from src.core.orchestrator import Orchestrator

orchestrator = Orchestrator()

# Execute iterative workflow with gap detection
result = orchestrator.execute_workflow(
    workflow_id="deep_research",
    inputs={
        "query": "What are the main technical challenges in building a real-time AI tutoring system?",
        "depth": "comprehensive"
    }
)

print("=== Iterative Research Results ===\n")
print(f"Status: {result['status']}")
print(f"Iterations Completed: {result['metadata']['iterations']}")
print(f"Final Confidence: {result['confidence']:.2f}\n")

# Show iteration details
for i, iteration in enumerate(result['metadata']['iteration_details'], 1):
    print(f"Iteration {i}:")
    print(f"  Confidence: {iteration['confidence']:.2f}")
    print(f"  Gaps Found: {len(iteration['gaps'])}")
    if iteration['gaps']:
        print("  Top Gaps:")
        for gap in iteration['gaps'][:3]:
            print(f"    - {gap}")
    print()
```

**Expected Output:**
```
=== Iterative Research Results ===

Status: success
Iterations Completed: 3
Final Confidence: 0.83

Iteration 1:
  Confidence: 0.45
  Gaps Found: 7
  Top Gaps:
    - No discussion of latency requirements
    - Missing: scalability considerations
    - Incomplete: data privacy aspects

Iteration 2:
  Confidence: 0.68
  Gaps Found: 3
  Top Gaps:
    - Missing: cost analysis for real-time inference
    - Incomplete: infrastructure requirements
    - No mention of fallback strategies

Iteration 3:
  Confidence: 0.83
  Gaps Found: 0
```

#### Schritt 2: Detaillierte Gap Analysis verstehen

```python
# Inspect how gaps were refined
for i, iteration in enumerate(result['metadata']['iteration_details'], 1):
    print(f"\n=== Iteration {i} Gap Refinement ===")

    print("Identified Gaps:")
    for gap in iteration['gaps']:
        print(f"  - {gap}")

    if 'refined_inputs' in iteration:
        print("\nRefined Queries Generated:")
        for query in iteration['refined_inputs'].get('refined_queries', []):
            print(f"  ’ {query}")
```

**Expected Output:**
```
=== Iteration 1 Gap Refinement ===
Identified Gaps:
  - No discussion of latency requirements
  - Missing: scalability considerations

Refined Queries Generated:
  ’ What are the maximum acceptable latency requirements for real-time AI tutoring interactions?
  ’ How do leading AI tutoring platforms handle scaling to millions of concurrent users?

=== Iteration 2 Gap Refinement ===
[...]
```

---

## Use Case 4: Custom Workflow Creation

### Szenario
Du willst einen eigenen spezialisierten Workflow erstellen für "Competitive Intelligence Analysis".

### Schritt 1: Workflow-Datei erstellen

```bash
# Create custom workflow file
touch config/workflows/sequential/competitive_intelligence.json
```

#### Schritt 2: Workflow definieren

**File:** `config/workflows/sequential/competitive_intelligence.json`
```json
{
  "workflow_id": "competitive_intelligence",
  "name": "Competitive Intelligence Analysis",
  "description": "Deep dive into competitor strategies, strengths, weaknesses",
  "mode": "sequential",
  "steps": [
    {
      "technique": "quick_research",
      "order": 1,
      "inputs": {
        "focus": "competitor_identification"
      }
    },
    {
      "technique": "contradiction",
      "order": 2,
      "inputs": {
        "focus": "competitor_claims_vs_reality"
      }
    },
    {
      "technique": "scenario_analysis",
      "order": 3,
      "inputs": {
        "scenarios": ["competitor_launches_new_feature", "price_war", "acquisition"]
      }
    },
    {
      "technique": "premortem",
      "order": 4,
      "inputs": {
        "hypothesis": "Our product will fail to compete"
      }
    }
  ],
  "exit_criteria": {
    "type": "all_complete"
  },
  "metadata": {
    "estimated_duration": "2-3 hours",
    "recommended_agent": "quality_validator"
  }
}
```

#### Schritt 3: Workflow testen

```python
from src.core.orchestrator import Orchestrator

orchestrator = Orchestrator()

# Execute custom workflow
result = orchestrator.execute_workflow(
    workflow_id="competitive_intelligence",
    inputs={
        "competitors": ["Duolingo", "Khan Academy", "Coursera"],
        "our_product": "AI Tutoring Platform"
    },
    agent_id="quality_validator"
)

print(f"Analysis completed with confidence: {result['confidence']:.2f}")
print(f"Outputs generated: {len(result['outputs'])}")

for output in result['outputs']:
    print(f"\nTechnique: {output.task_id}")
    print(f"Result preview: {output.result[:200]}...")
```

#### Schritt 4: Workflow zu Phase hinzufügen (optional)

```json
{
  "phase_id": "phase_1_competitive_deep_dive",
  "name": "Competitive Deep Dive",
  "building_blocks": [
    {
      "block_type": "workflow",
      "block_id": "competitive_intelligence",
      "category": "competition"
    }
  ]
}
```

---

## Use Case 5: Framework Composition

### Szenario
Du willst ein komplett neues Framework für "Startup Validation" erstellen, das mehrere Phasen kombiniert.

### Schritt 1: Benötigte Phasen identifizieren

```
Phase 1: Problem Validation
    Workflows: user_needs_research, pain_point_analysis

Phase 2: Solution Validation
    Workflows: tech_feasibility_collection, competitive_intelligence

Phase 3: Market Validation
    Workflows: market_research_collection, scenario_analysis

Phase 4: Final Assessment
    Workflows: validation_loop, planning_validation
```

### Schritt 2: Phasen-Configs erstellen

**Phase 1:** `config/phases/phase_problem_validation.json`
```json
{
  "phase_id": "phase_problem_validation",
  "name": "Problem Validation",
  "description": "Validate that the problem is real and significant",
  "type": "phase",
  "building_blocks": [
    {
      "block_type": "workflow",
      "block_id": "quick_web_research",
      "category": "user_needs"
    },
    {
      "block_type": "technique",
      "block_id": "sanity_check",
      "category": "validation"
    }
  ],
  "exit_criteria": {
    "type": "confidence_threshold",
    "threshold": 0.7
  }
}
```

**Wiederholen für Phase 2, 3, 4...**

### Schritt 3: Framework-Config erstellen

**File:** `config/frameworks/framework_startup_validation.json`
```json
{
  "framework_id": "framework_startup_validation",
  "name": "Startup Validation Framework",
  "description": "Comprehensive startup idea validation from problem to market",
  "type": "framework",
  "building_blocks": [
    {
      "block_type": "phase",
      "block_id": "phase_problem_validation",
      "order": 1
    },
    {
      "block_type": "phase",
      "block_id": "phase_solution_validation",
      "order": 2,
      "depends_on": "phase_problem_validation"
    },
    {
      "block_type": "phase",
      "block_id": "phase_market_validation",
      "order": 3,
      "depends_on": "phase_solution_validation"
    },
    {
      "block_type": "phase",
      "block_id": "phase_final_assessment",
      "order": 4,
      "depends_on": "phase_market_validation"
    }
  ],
  "global_exit_criteria": {
    "type": "all_phases_complete"
  },
  "metadata": {
    "use_case": "Startup idea validation",
    "estimated_total_duration": "6-8 hours"
  }
}
```

### Schritt 4: Framework validieren

```python
from src.core.framework_loader import FrameworkLoader

loader = FrameworkLoader()

# Load and validate
framework = loader.load_framework("framework_startup_validation")
is_valid, errors = loader.validate_framework(framework)

if is_valid:
    print(" Framework is valid")
    print(f"Phases: {framework.count_blocks()}")
else:
    print("L Validation errors:")
    for error in errors:
        print(f"  - {error}")
```

### Schritt 5: Framework ausführen

```python
from src.core.orchestrator import Orchestrator

orchestrator = Orchestrator()

result = orchestrator.execute_framework(
    framework_id="framework_startup_validation",
    inputs={
        "startup_idea": "AI-powered personal finance coach for Gen Z",
        "target_market": "US, ages 18-25",
        "budget": "$50k seed"
    }
)

# Generate executive summary
print("=== Startup Validation Report ===\n")
for phase_result in result['phase_results']:
    print(f"{phase_result['phase_id']}: {' PASS' if phase_result['confidence'] >= 0.7 else 'L FAIL'}")
    print(f"  Confidence: {phase_result['confidence']:.2f}\n")

if result['metadata']['all_phases_passed']:
    print("<‰ Startup idea VALIDATED - proceed to build MVP")
else:
    print("  Startup idea needs refinement - review phase results")
```

---

## Use Case 6: Batch Processing

### Szenario
Du willst 10 verschiedene Produkt-Ideen validieren und vergleichen.

### Lösung

```python
from src.core.orchestrator import Orchestrator
import json
from pathlib import Path

orchestrator = Orchestrator()

# List of ideas to validate
product_ideas = [
    "AI Tutoring Platform",
    "Blockchain-based Supply Chain",
    "AR Fitness Coaching",
    "Mental Health Chatbot",
    # ... 6 more
]

results = []

for i, idea in enumerate(product_ideas, 1):
    print(f"\n[{i}/{len(product_ideas)}] Validating: {idea}")

    result = orchestrator.execute_framework(
        framework_id="framework_startup_validation",
        inputs={"startup_idea": idea}
    )

    results.append({
        "idea": idea,
        "overall_confidence": result['metadata'].get('overall_confidence', 0.0),
        "phase_results": [
            {
                "phase": pr['phase_id'],
                "confidence": pr['confidence']
            }
            for pr in result['phase_results']
        ]
    })

    print(f"  ’ Confidence: {result['metadata'].get('overall_confidence', 0.0):.2f}")

# Sort by confidence
results.sort(key=lambda x: x['overall_confidence'], reverse=True)

# Save ranking
output_path = Path("research-data/batch-validation/ranking.json")
output_path.parent.mkdir(parents=True, exist_ok=True)
with open(output_path, "w") as f:
    json.dump(results, f, indent=2)

# Print ranking
print("\n=== Validation Ranking ===")
for i, result in enumerate(results, 1):
    print(f"{i}. {result['idea']} (Confidence: {result['overall_confidence']:.2f})")
```

---

## Troubleshooting

### Problem 1: Low Confidence Scores

**Symptom:**
```
Confidence: 0.32
Gaps Found: 12
```

**Diagnose:**
```python
# Inspect gaps
print("Identified Gaps:")
for gap in result['metadata']['gaps']:
    print(f"  - {gap}")
```

**Solutions:**

1. **Increase iterations:**
```json
{
  "max_iterations": 5  // was 3
}
```

2. **Lower threshold:**
```json
{
  "exit_criteria": {
    "type": "confidence_threshold",
    "threshold": 0.7  // was 0.8
  }
}
```

3. **Use better model:**
```python
result = orchestrator.execute_workflow(
    workflow_id="deep_research",
    inputs=inputs,
    agent_id="quality_validator"  // Use 32B instead of 8B
)
```

---

### Problem 2: Framework Validation Fails

**Symptom:**
```
L Validation errors:
  - Phase not found: phase_xyz
```

**Solution:**
```python
# Check if phase file exists
from pathlib import Path
phase_path = Path("config/phases/phase_xyz.json")
print(f"Exists: {phase_path.exists()}")

# If missing, create it
if not phase_path.exists():
    # Create phase config...
```

---

### Problem 3: Out of Memory (OOM)

**Symptom:**
```
RuntimeError: CUDA out of memory
```

**Solutions:**

1. **Reduce GPU layers:**
```json
{
  "n_gpu_layers": 8  // was 16
}
```

2. **Monitor VRAM:**
```bash
watch -n 1 nvidia-smi
```

3. **Use smaller model:**
```python
# Switch from tier2_quality (32B) to tier1_fast (8B)
result = orchestrator.execute_workflow(
    workflow_id="deep_research",
    inputs=inputs,
    agent_id="fast_researcher"
)
```

---

### Problem 4: Slow Execution

**Symptom:**
```
Execution Time: 45 minutes (expected: 10 min)
```

**Diagnose:**
```python
# Check execution times per task
for output in result['outputs']:
    print(f"{output.task_id}: {output.execution_time:.2f}s")
```

**Solutions:**

1. **More GPU layers (if VRAM available):**
```json
{
  "n_gpu_layers": 32  // was 16
}
```

2. **Reduce max_tokens:**
```json
{
  "max_tokens": 1024  // was 2048
}
```

3. **Use parallel execution (if multi-GPU):**
```python
# Currently sequential, future enhancement
```

---

### Problem 5: Missing Tool

**Symptom:**
```
KeyError: 'web_scraper' not in ToolRegistry
```

**Solution:**
```python
# Ensure registered_tools is imported
from src.tools import registered_tools

# Or import specific tool
from src.tools.web_scraper import web_scraper

# Verify registration
from src.core.tool_decorator import ToolRegistry
print(ToolRegistry.list_tools())
```

---

### Problem 6: JSON Schema Validation Error

**Symptom:**
```
JSONSchemaValidationError: 'workflow_id' is a required property
```

**Solution:**
```json
// Ensure all required fields are present
{
  "workflow_id": "my_workflow",  //  Missing this
  "name": "My Workflow",
  "mode": "sequential",
  // ...
}
```

**Validate manually:**
```python
from src.utils.json_loader import JSONLoader

try:
    config = JSONLoader.load("config/workflows/sequential/my_workflow.json")
    print(" Valid")
except Exception as e:
    print(f"L Invalid: {e}")
```

---

## Best Practices

### 1. Start Small, Scale Up
```python
# L Don't start with full framework
result = orchestrator.execute_framework("framework_product_research", ...)

#  Start with single technique
result = orchestrator.execute_workflow("quick_web_research", ...)

#  Then workflow
result = orchestrator.execute_workflow("research_validation", ...)

#  Finally framework
result = orchestrator.execute_framework("framework_product_research", ...)
```

### 2. Monitor Resource Usage
```python
import subprocess

# Before execution
subprocess.run(["nvidia-smi"])

# During execution (separate terminal)
subprocess.Popen(["watch", "-n", "1", "nvidia-smi"])
```

### 3. Save Intermediate Results
```python
# After each phase
for phase_result in result['phase_results']:
    output_path = Path(f"research-data/intermediate/{phase_result['phase_id']}.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(phase_result, f, indent=2)
```

### 4. Use Appropriate Models
```
Quick Research ’ tier1_fast (8B)
Deep Analysis ’ tier2_quality (32B)
Validation ’ tier2_quality (32B)
Synthesis ’ tier2_quality (32B)
```

### 5. Leverage Caching
```python
# FrameworkLoader caches loaded blocks
loader = FrameworkLoader()

# First load: reads file
framework = loader.load_framework("framework_product_research")

# Second load: returns cached instance (fast)
framework = loader.load_framework("framework_product_research")

# Clear cache if configs changed
loader.clear_cache()
```

---

## Zusammenfassung

**Use Cases behandelt:**
1. **Product Research:** Framework execution für komplette Kampagne
2. **Multi-AI Research:** Prompt Generation ’ Manual Querying ’ Local Analysis
3. **Iterative Deep Research:** Gap Detection & Refinement Loops
4. **Custom Workflows:** Eigene Workflows erstellen
5. **Framework Composition:** Neue Frameworks aus Phasen zusammenbauen
6. **Batch Processing:** Mehrere Ideen parallel validieren

**Troubleshooting:**
- Low Confidence ’ Mehr Iterationen, besseres Modell
- Validation Errors ’ Fehlende Configs erstellen
- OOM ’ GPU-Layers reduzieren, kleineres Modell
- Slow Execution ’ Mehr GPU-Layers, weniger Tokens
- Missing Tools ’ Import sicherstellen
- Schema Errors ’ Required Fields ergänzen

**Next:** Transfer auf starkes System für echte Tests!
