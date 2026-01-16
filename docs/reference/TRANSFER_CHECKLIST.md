# Transfer Checklist - Production System

**Zweck:** Vorbereitung für Transfer auf starkes System (2 GPUs, DDR5 RAM)
**Datum:** 2025-12-23
**Sprint Status:** Alle Sprints abgeschlossen (1-4)

---

## Hardware-Anforderungen Starkes System

### Empfohlene Specs
-  GPU 1: RTX 3060 Ti (8GB VRAM)
-  GPU 2: GTX 1060 (optional, für parallele Workloads)
-  RAM: 16GB DDR5 (minimum)
-  Storage: 50GB+ freier Speicher für Modelle

### Aktuelle Test-System Specs (zum Vergleich)
- GPU: GTX 980 (4GB VRAM)
- RAM: 8GB DDR4
- Limitierungen: Nur Tier 1 Models (8B) komplett in VRAM

---

## 1. Software-Dependencies

### Python Environment
```bash
# Python Version
python3 --version  # Should be 3.10+

# Create venv
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Dependencies in requirements.txt:**
```
pydantic>=2.0.0
beautifulsoup4>=4.12.0
pypdf2>=3.0.0
requests>=2.31.0
jsonschema>=4.20.0
```

---

### llama.cpp Build

**Wichtig:** Auf starkem System mit CUDA neu bauen!

```bash
# Clone llama.cpp (if not already present)
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp

# Build with CUDA support
mkdir build
cd build
cmake .. -DGGML_CUDA=ON
cmake --build . --config Release

# Verify binary
./bin/llama-cli --version
```

**Expected Output:**
```
llama-cli version: [version]
CUDA support: YES
```

**Test CUDA:**
```bash
./bin/llama-cli \
  -m /path/to/model.gguf \
  -p "Test prompt" \
  -n 10 \
  --n-gpu-layers 999

# Check for CUDA offload in output
# Should see: "llama_backend_init: using CUDA backend"
```

---

## 2. Model Downloads

### Modelle für Produktiv-System

**Tier 1: Fast (8B) - Llama 3.1**
```bash
# Hugging Face Model Card
# https://huggingface.co/hugging-quants/Llama-3.1-8B-Instruct-abliterated-Q6_K-GGUF

# Download
wget https://huggingface.co/hugging-quants/Llama-3.1-8B-Instruct-abliterated-Q6_K-GGUF/resolve/main/llama-3.1-8b-instruct-abliterated-q6_k.gguf \
  -O models/llama-3.1-8b-instruct-abliterated-q6_k.gguf

# Expected size: ~7GB
# VRAM usage: ~6GB (komplett in VRAM auf RTX 3060 Ti)
```

**Tier 2: Quality (32B) - Qwen 2.5**
```bash
# Hugging Face Model Card
# https://huggingface.co/Qwen/Qwen2.5-32B-Instruct-GGUF

# Download Q4_K_M (balanced size/quality)
wget https://huggingface.co/Qwen/Qwen2.5-32B-Instruct-GGUF/resolve/main/qwen2.5-32b-instruct-q4_k_m.gguf \
  -O models/qwen-2.5-32b-instruct-q4_k_m.gguf

# Expected size: ~19GB
# VRAM usage: ~8GB (16 layers), RAM: ~11GB (rest)
```

**Verify Downloads:**
```bash
ls -lh models/
# Should show both models with correct sizes
```

---

### Model Config Updates

**Update:** `config/models/tier1_fast.json`
```json
{
  "model_id": "tier1_fast",
  "type": "llama_cpp",
  "path": "models/llama-3.1-8b-instruct-abliterated-q6_k.gguf",
  "context_length": 4096,
  "n_gpu_layers": 999,
  "temperature": 0.7,
  "use_mlock": true,
  "metadata": {
    "vram_usage": "~6GB",
    "recommended_use": "Fast research, gap detection"
  }
}
```

**Update:** `config/models/tier2_quality.json`
```json
{
  "model_id": "tier2_quality",
  "type": "llama_cpp",
  "path": "models/qwen-2.5-32b-instruct-q4_k_m.gguf",
  "context_length": 4096,
  "n_gpu_layers": 16,
  "temperature": 0.3,
  "use_mlock": true,
  "metadata": {
    "vram_usage": "~8GB (16 layers in VRAM)",
    "ram_usage": "~11GB (rest in RAM)",
    "recommended_use": "Deep analysis, validation, synthesis"
  }
}
```

---

## 3. System Verification Tests

### Test 1: Python Environment
```bash
# Activate venv
source venv/bin/activate

# Test imports
python3 -c "
from src.core.orchestrator import Orchestrator
from src.core.framework_loader import FrameworkLoader
from src.models.llama_cpp_client import LlamaCppClient
print(' All imports successful')
"
```

**Expected:** No errors, " All imports successful"

---

### Test 2: llama.cpp Integration (Tier 1)
```bash
# Direct llama-cli test
./llama.cpp/build/bin/llama-cli \
  -m models/llama-3.1-8b-instruct-abliterated-q6_k.gguf \
  -p "What is 2+2?" \
  -n 20 \
  --n-gpu-layers 999 \
  --temp 0.7 \
  --no-conversation

# Should complete in <5 seconds on RTX 3060 Ti
```

**Expected Output:**
```
llama_backend_init: using CUDA backend
[... model loading ...]
What is 2+2? The answer is 4.
```

**Python Client Test:**
```python
from src.models.llama_cpp_client import LlamaCppClient

client = LlamaCppClient(
    model_path="models/llama-3.1-8b-instruct-abliterated-q6_k.gguf",
    n_gpu_layers=999
)

# Health check
if client.health_check():
    print(" Tier 1 model operational")

# Generate test
response = client.generate("What is the capital of France?", max_tokens=50)
print(f"Response: {response}")
```

---

### Test 3: llama.cpp Integration (Tier 2)
```bash
# Monitor VRAM before starting
nvidia-smi

# Python Client Test with VRAM/RAM split
python3 -c "
from src.models.llama_cpp_client import LlamaCppClient

client = LlamaCppClient(
    model_path='models/qwen-2.5-32b-instruct-q4_k_m.gguf',
    n_gpu_layers=16  # Partial GPU offload
)

if client.health_check():
    print(' Tier 2 model operational')

response = client.generate('Analyze the pros and cons of AI in education.', max_tokens=200)
print(f'Response: {response[:200]}...')
"

# Monitor VRAM after
nvidia-smi
# Should see ~8GB VRAM used
```

**Tuning `n_gpu_layers`:**
```bash
# If VRAM < 8GB used: Increase layers
# "n_gpu_layers": 20  (more VRAM, faster)

# If VRAM > 8GB or OOM: Decrease layers
# "n_gpu_layers": 12  (less VRAM, slower)
```

---

### Test 4: Agent System
```python
from src.core.orchestrator import Orchestrator

orchestrator = Orchestrator()

# List available agents
agents = orchestrator.list_agents()
print(f"Available Agents: {len(agents)}")
for agent in agents:
    print(f"  - {agent['agent_id']} (role: {agent.get('role', 'N/A')})")

# Load and test agent
fast_agent = orchestrator.load_agent("fast_researcher")
print(f" Agent loaded: {fast_agent.agent_id}")
```

**Expected Output:**
```
Available Agents: 3
  - fast_researcher (role: researcher)
  - quality_validator (role: validator)
  - synthesizer (role: synthesizer)
 Agent loaded: fast_researcher
```

---

### Test 5: Simple Workflow Execution
```python
from src.core.orchestrator import Orchestrator

orchestrator = Orchestrator()

# Execute simple sequential workflow
result = orchestrator.execute_workflow(
    workflow_id="quick_web_research",
    inputs={"query": "What is AI tutoring?"}
)

print(f"Status: {result['status']}")
print(f"Confidence: {result['confidence']:.2f}")
print(f"Outputs: {len(result['outputs'])}")

# Should complete in <30 seconds
```

**Expected Output:**
```
Status: success
Confidence: 0.72
Outputs: 1
```

---

### Test 6: Iterative Workflow (Full Test)
```python
from src.core.orchestrator import Orchestrator

orchestrator = Orchestrator()

# Execute iterative workflow with refinement
result = orchestrator.execute_workflow(
    workflow_id="deep_research",
    inputs={
        "query": "What are the main competitors in the AI tutoring market?",
        "depth": "comprehensive"
    }
)

print(f"Status: {result['status']}")
print(f"Iterations: {result['metadata']['iterations']}")
print(f"Final Confidence: {result['confidence']:.2f}")

# Should complete in 2-5 minutes (depends on iterations)
```

**Expected Output:**
```
Status: success
Iterations: 3
Final Confidence: 0.83
```

---

### Test 7: Framework Execution (Full Stack)
```python
from src.core.orchestrator import Orchestrator

orchestrator = Orchestrator()

# Execute complete framework
result = orchestrator.execute_framework(
    framework_id="framework_product_research",
    inputs={
        "product": "AI Tutoring Platform",
        "target_market": "K-12 Education"
    }
)

print(f"Framework Status: {result['status']}")
print(f"Phases Completed: {len(result['phase_results'])}")

for phase_result in result['phase_results']:
    print(f"  {phase_result['phase_id']}: Confidence {phase_result['confidence']:.2f}")

# Should complete in 10-20 minutes (3 phases, multiple workflows)
```

**Expected Output:**
```
Framework Status: success
Phases Completed: 3
  phase_0_base_research: Confidence 0.75
  phase_2_validation: Confidence 0.82
  phase_3_synthesis: Confidence 0.88
```

---

### Test 8: Multi-AI Tools (Sprint 3)
```python
from src.tools.multi_ai.prompt_generator import generate_multi_ai_prompt
from pathlib import Path

# Generate prompt
prompt_data = generate_multi_ai_prompt(
    topic="AI Tutoring Market Test",
    categories=["market_size", "competition"],
    depth="standard"
)

print(f" Prompt generated: {prompt_data['save_path']}")
print(f"Prompt length: {len(prompt_data['prompt'])} chars")

# Verify file saved
assert Path(prompt_data['save_path']).exists()
print(" Multi-AI prompt generation working")
```

---

### Test 9: Framework Loader (Sprint 4)
```python
from src.core.framework_loader import FrameworkLoader

loader = FrameworkLoader()

# Load framework
framework = loader.load_framework("framework_product_research")

# Validate
is_valid, errors = loader.validate_framework(framework)

assert is_valid, f"Validation errors: {errors}"
print(f" Framework loaded and validated")
print(f"  Phases: {framework.count_blocks()}")

# List all building blocks
print("\nAvailable building blocks:")
print(f"  Techniques: {len(loader.list_techniques())}")
print(f"  Workflows: {len(loader.list_workflows())}")
print(f"  Phases: {len(loader.list_phases())}")
print(f"  Frameworks: {len(loader.list_frameworks())}")
```

**Expected Output:**
```
 Framework loaded and validated
  Phases: 3

Available building blocks:
  Techniques: 7
  Workflows: 9
  Phases: 3
  Frameworks: 1
```

---

## 4. Performance Benchmarks

### Baseline Measurements (Schwaches System)
```
GTX 980 (4GB VRAM), 8GB RAM

TinyLlama 1.1B:
  - Load time: ~5s
  - Generation (50 tokens): ~8s
  - Total: ~13s

Mixtral 8x7B Q2_K (6.1GB):
  - Load time: ~30s
  - Generation (50 tokens): ~45s
  - Total: ~75s
```

### Expected Performance (Starkes System)

**RTX 3060 Ti (8GB VRAM), 16GB DDR5**

**Tier 1 (Llama 3.1 8B, Q6_K):**
```
Expected metrics:
  - Load time: <3s (komplett in VRAM)
  - Generation (50 tokens): <2s
  - Total: <5s

Speedup vs. TinyLlama: ~2.6x faster
Quality: Deutlich höher (8B vs 1.1B)
```

**Tier 2 (Qwen 2.5 32B Q4_K_M, 16 layers GPU):**
```
Expected metrics:
  - Load time: ~8s (VRAM + RAM split)
  - Generation (50 tokens): ~12s
  - Total: ~20s

Quality: State-of-the-art for lokale Modelle
```

### Benchmark-Script
```python
import time
from src.models.llama_cpp_client import LlamaCppClient

def benchmark_model(model_path: str, n_gpu_layers: int, name: str):
    print(f"\n=== Benchmarking {name} ===")

    # Load
    start = time.time()
    client = LlamaCppClient(model_path=model_path, n_gpu_layers=n_gpu_layers)
    load_time = time.time() - start
    print(f"Load time: {load_time:.2f}s")

    # Generate
    start = time.time()
    response = client.generate("What is 2+2?", max_tokens=50)
    gen_time = time.time() - start
    print(f"Generation time: {gen_time:.2f}s")

    print(f"Total: {load_time + gen_time:.2f}s")
    print(f"Response: {response[:100]}...")

# Run benchmarks
benchmark_model(
    "models/llama-3.1-8b-instruct-abliterated-q6_k.gguf",
    999,
    "Tier 1 Fast (8B)"
)

benchmark_model(
    "models/qwen-2.5-32b-instruct-q4_k_m.gguf",
    16,
    "Tier 2 Quality (32B)"
)
```

---

## 5. Directory Structure Verification

```bash
# Verify all directories exist
python3 -c "
from pathlib import Path

dirs = [
    'config/agents',
    'config/models',
    'config/techniques',
    'config/workflows/sequential',
    'config/workflows/iterative',
    'config/phases',
    'config/frameworks',
    'config/schemas',
    'src/core',
    'src/models',
    'src/tools/multi_ai',
    'src/utils',
    'docs/user-guide',
    'docs/architecture',
    'models',
    'logs',
    'research-data/multi-ai',
    'research-data/validations',
    'research-prompts'
]

missing = [d for d in dirs if not Path(d).exists()]

if missing:
    print('L Missing directories:')
    for d in missing:
        print(f'  - {d}')
else:
    print(' All directories present')
"
```

---

## 6. Configuration Files Checklist

### Agent Configs
```bash
ls -1 config/agents/
```
**Expected:**
- fast_researcher.json 
- quality_validator.json 
- synthesizer.json 

### Model Configs
```bash
ls -1 config/models/
```
**Expected:**
- tier1_fast.json 
- tier2_quality.json 

### Techniques
```bash
ls -1 config/techniques/ | wc -l
```
**Expected:** 7 

### Workflows
```bash
echo "Sequential: $(ls -1 config/workflows/sequential/ | wc -l)"
echo "Iterative: $(ls -1 config/workflows/iterative/ | wc -l)"
```
**Expected:**
- Sequential: 7 
- Iterative: 2 

### Phases
```bash
ls -1 config/phases/ | wc -l
```
**Expected:** 3 

### Frameworks
```bash
ls -1 config/frameworks/ | wc -l
```
**Expected:** 1 

---

## 7. Documentation Verification

```bash
# User Guide
ls -1 docs/user-guide/
```
**Expected:**
- 00_index.md 
- 01_konzepte.md 
- 02_reference.md 
- 03_use_cases.md 

**Validation:**
```bash
# Check file sizes (should be substantial)
du -h docs/user-guide/*.md

# Expected output:
# ~5K  00_index.md
# ~30K 01_konzepte.md
# ~60K 02_reference.md
# ~40K 03_use_cases.md
```

---

## 8. Git Status & Commit

```bash
# Check what's new/modified
git status

# Should show:
# - New files in docs/user-guide/
# - New phase configs (phase_2_validation.json, phase_3_synthesis.json)
# - Modified: framework_loader.py (bug fixes)

# Stage changes
git add .

# Commit
git commit -m "feat: Complete Sprint 4 + Hybrid Documentation

- Sprint 4: Logic Builder Foundation complete
  - FrameworkLoader with hierarchical blocks
  - Phase & Framework configs
  - Schema validation

- Sprint 3: Multi-AI Integration
  - prompt_generator.py
  - response_analyzer.py

- Sprint 2 Finalization:
  - Gap detection (_identify_gaps)
  - Confidence scoring (_evaluate_confidence)
  - Input refinement (_refine_inputs)

- Hybrid Documentation:
  - 00_index.md (overview)
  - 01_konzepte.md (concepts & architecture)
  - 02_reference.md (API reference)
  - 03_use_cases.md (practical examples)

- Transfer checklist for production system
"

# Push (if remote configured)
git push origin master
```

---

## 9. Final Pre-Transfer Checklist

### Code Quality
- [x] All sprints (1-4) implemented
- [x] No syntax errors in Python files
- [x] All imports resolve correctly
- [x] JSON configs valid against schemas

### Documentation
- [x] User Guide complete (3 parts + index)
- [x] Architecture plans preserved
- [x] Transfer checklist created
- [x] STATUS.md updated

### Configuration
- [x] Agent configs ready (3 agents)
- [x] Model configs ready (2 tiers)
- [x] Techniques defined (7)
- [x] Workflows defined (9)
- [x] Phases defined (3)
- [x] Frameworks defined (1)

### Testing Prep
- [x] Test scripts prepared (9 tests)
- [x] Benchmark script ready
- [x] Performance baselines documented

### Models (To Download on Strong System)
- [ ] Llama 3.1 8B Q6_K (~7GB)
- [ ] Qwen 2.5 32B Q4_K_M (~19GB)

### System Prep (To Do on Strong System)
- [ ] Python venv created
- [ ] Dependencies installed
- [ ] llama.cpp built with CUDA
- [ ] Models downloaded
- [ ] Model configs updated with correct paths
- [ ] All 9 tests executed and passing

---

## 10. Post-Transfer Actions

### Immediate (First Session on Strong System)
1. **Environment Setup** (30 min)
   - Create venv
   - Install dependencies
   - Build llama.cpp with CUDA

2. **Model Downloads** (1-2 hours, can run overnight)
   - Download Tier 1 model (7GB)
   - Download Tier 2 model (19GB)

3. **Basic Testing** (1 hour)
   - Run Tests 1-4 (environment, models, agents)
   - Verify CUDA acceleration working

### Short-Term (Week 1)
4. **Full Stack Testing** (2-3 hours)
   - Run Tests 5-9 (workflows, frameworks, tools)
   - Benchmark performance
   - Tune `n_gpu_layers` for Tier 2

5. **Real Use Cases** (ongoing)
   - Execute actual research campaigns
   - Refine workflows based on real outputs
   - Build custom frameworks for specific domains

### Medium-Term (Month 1)
6. **GUI/LiveServer** (pending)
   - Debug and test LiveServer
   - Integrate with documentation

7. **Advanced Features** (if needed)
   - Multi-GPU support (use GTX 1060 as second GPU)
   - Quality pattern learning
   - Knowledge graph integration (experimental)

---

## 11. Success Metrics

### After Transfer, System is Successful if:

**Performance:**
- [ ] Tier 1 (8B) generates 50 tokens in <5s
- [ ] Tier 2 (32B) generates 50 tokens in <20s
- [ ] Framework execution completes in <30 min

**Quality:**
- [ ] Iterative workflows reach confidence >0.8 within 3 iterations
- [ ] Multi-AI analysis successfully synthesizes responses
- [ ] Framework outputs are comprehensive (>2000 tokens)

**Stability:**
- [ ] No OOM errors during normal operation
- [ ] Models load consistently without crashes
- [ ] Long-running workflows complete without hanging

**Usability:**
- [ ] Documentation enables self-service usage
- [ ] Config changes don't require code modifications
- [ ] Custom workflows can be created via JSON

---

## 12. Troubleshooting Guide (for Strong System)

### If CUDA Not Detected:
```bash
# Check NVIDIA driver
nvidia-smi

# Reinstall CUDA toolkit if needed
sudo apt install nvidia-cuda-toolkit

# Rebuild llama.cpp
cd llama.cpp/build
rm -rf *
cmake .. -DGGML_CUDA=ON
cmake --build . --config Release
```

### If OOM on Tier 2:
```bash
# Reduce GPU layers
# In config/models/tier2_quality.json:
# "n_gpu_layers": 12  (was 16)

# Or use smaller quantization
# Download Q3_K_M instead of Q4_K_M (smaller, faster, slightly lower quality)
```

### If Performance Below Expected:
```bash
# Monitor during execution
watch -n 1 nvidia-smi

# Check GPU utilization (should be >80% during generation)
# If low: Increase n_gpu_layers
# If OOM: Decrease n_gpu_layers
```

---

## 13. Contact & Support

**Documentation:**
- User Guide: `docs/user-guide/00_index.md`
- Architecture: `docs/architecture/ARCHITECTURE_PLAN_V2.1_FINAL.md`
- Status: `STATUS.md`

**Key Files:**
- Orchestrator: `src/core/orchestrator.py:879`
- FrameworkLoader: `src/core/framework_loader.py:394`
- LlamaCppClient: `src/models/llama_cpp_client.py:173`

**This Checklist:**
- `docs/TRANSFER_CHECKLIST.md`

---

##  Ready for Transfer

Alle Sprints abgeschlossen, Dokumentation erstellt, Tests vorbereitet.
Next: Transfer auf starkes System und echte Produktiv-Tests!
