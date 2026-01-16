# Multi-GPU Testing Plan

**Hardware**: RTX 3060 Ti (8GB) + GTX 1060 (3GB) = 11GB VRAM total + 16GB RAM
**Current Location**: Development machine (GTX 980 4GB)
**Test Location**: Production machine

---

## Objective

Test if llama.cpp can split models across 2 GPUs efficiently for running larger models or multiple models simultaneously.

---

## llama.cpp Multi-GPU Configuration

### Method 1: Tensor Parallelism (`--split-mode`)

```bash
# Example: Split model across GPUs
llama-server \
  --model /path/to/model.gguf \
  --split-mode row \
  --tensor-split 8,3 \
  --n-gpu-layers 999
```

**Parameters:**
- `--split-mode row|layer|none`: How to split tensors
  - `row`: Split rows across GPUs (recommended)
  - `layer`: Split layers across GPUs
  - `none`: No splitting (single GPU)
- `--tensor-split 8,3`: Proportion for each GPU (8GB:3GB ratio)
- `--n-gpu-layers 999`: Load all layers to GPU (split across both)

### Method 2: Environment Variable

```bash
export CUDA_VISIBLE_DEVICES=0,1
llama-server --model model.gguf --n-gpu-layers 999
```

---

## Test Cases

### Test 1: Single Large Model Split

**Model**: DeepSeek-R1-Distill-Qwen-14B Q4_K_M (~9GB)

**Expected**: Model should fit across 11GB total VRAM

```bash
./llama.cpp/build/bin/llama-server \
  --model ~/llama-models/deepseek-r1-distill-qwen-14b.Q4_K_M.gguf \
  --host 0.0.0.0 \
  --port 8080 \
  --ctx-size 8192 \
  --n-gpu-layers 999 \
  --split-mode row \
  --tensor-split 8,3
```

**Verify:**
```bash
# Monitor GPU usage
nvidia-smi -l 1

# Check which GPUs are being used
nvidia-smi --query-gpu=index,name,memory.used,memory.total --format=csv
```

**Success Criteria:**
- Model loads without OOM errors
- Both GPUs show memory usage
- Inference works and produces output
- Performance is acceptable (measure tokens/sec)

---

### Test 2: Two Models Simultaneously (Optional)

**Setup:**
- GPU 0 (RTX 3060 Ti): Llama 3.1 8B (~7GB)
- GPU 1 (GTX 1060): Qwen 2.5 7B (~5GB) - **Won't fit, 3GB only**

❌ **Likely won't work** - GTX 1060 only has 3GB VRAM

---

### Test 3: Optimal Configuration for Deep Research

**Strategy**: Use tensor splitting for single large model

**Tier 1 (Fast Research)**:
```bash
# Llama 3.1 8B Q6_K (~7GB) - fits in GPU 0 alone
llama-server \
  --model ~/llama-models/llama-3.1-8b-abliterated.Q6_K.gguf \
  --port 8080 \
  --n-gpu-layers 999 \
  --ctx-size 8192
```

**Tier 2 (Deep Reasoning)**:
```bash
# DeepSeek-R1-Distill-14B Q4_K_M (~9GB) - split across both GPUs
llama-server \
  --model ~/llama-models/deepseek-r1-distill-qwen-14b.Q4_K_M.gguf \
  --port 8081 \
  --n-gpu-layers 999 \
  --ctx-size 8192 \
  --split-mode row \
  --tensor-split 8,3
```

**Or try Q5_K_M (~10.5GB)**:
```bash
# DeepSeek-R1-Distill-14B Q5_K_M (~10.5GB) - better quality
llama-server \
  --model ~/llama-models/deepseek-r1-distill-qwen-14b.Q5_K_M.gguf \
  --port 8081 \
  --n-gpu-layers 999 \
  --ctx-size 8192 \
  --split-mode row \
  --tensor-split 8,3
```

---

## Benchmarking

After each test, measure:

1. **Load Time**: How long to load model
2. **Inference Speed**: Tokens/second
3. **Memory Usage**: VRAM on each GPU
4. **Quality**: Does split affect output quality?

```bash
# Simple benchmark
time curl -X POST http://localhost:8080/completion \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain quantum computing in simple terms.",
    "n_predict": 200,
    "temperature": 0.7
  }'
```

---

## Expected Results

### Single GPU (RTX 3060 Ti 8GB only):
- ✅ Llama 3.1 8B Q6_K (~7GB) - **Fits perfectly**
- ❌ DeepSeek-R1-Distill-14B Q4_K_M (~9GB) - **OOM**
- ❌ Qwen 2.5 32B Q4_K_M (~20GB) - **OOM**

### Multi-GPU Split (8GB + 3GB = 11GB):
- ✅ Llama 3.1 8B Q6_K (~7GB) - **Fits in GPU 0 alone**
- ✅ DeepSeek-R1-Distill-14B Q4_K_M (~9GB) - **Should fit split**
- ✅ DeepSeek-R1-Distill-14B Q5_K_M (~10.5GB) - **Should fit split**
- ❌ Qwen 2.5 32B Q4_K_M (~20GB) - **Still too large even with RAM offload**

### Tier 2 Alternative if Multi-GPU doesn't work well:
- **Qwen 2.5 14B Q6_K** (~10GB with partial offload)
- **DeepSeek-R1-Distill-7B Q6_K** (~6GB, fits in GPU 0)

---

## Fallback Plan

If multi-GPU splitting doesn't work or is too slow:

**Option A: Model Switching** (single GPU 0)
- Run Tier 1 OR Tier 2, switch via server restart
- Fast restart (~5-10 seconds)
- Simple, reliable

**Option B: Smaller Tier 2**
- Use DeepSeek-R1-Distill-7B instead of 14B
- Fits in single GPU
- Still very capable (55.5% AIME, way better than Llama 8B)

---

## Recommended Model Downloads (Post-Testing)

### Scenario 1: Multi-GPU Works Well ✅
```
Tier 1: Llama 3.1 8B Abliterated Q6_K (~7GB)
Tier 2: DeepSeek-R1-Distill-Qwen-14B Q5_K_M (~10.5GB)
```

### Scenario 2: Multi-GPU Too Slow or Doesn't Work ❌
```
Tier 1: Llama 3.1 8B Abliterated Q6_K (~7GB)
Tier 2: DeepSeek-R1-Distill-Qwen-7B Q6_K (~6GB)
```

### Scenario 3: Maximum Quality (if multi-GPU works) 🚀
```
Tier 1: Qwen 2.5 7B Abliterated Q6_K (~6GB)
Tier 2: DeepSeek-R1-Distill-Qwen-14B Q5_K_M (~10.5GB)
Tier 3: Qwen 2.5 32B Q4_K_M (~20GB) - CPU/RAM offload for rare ultra-complex tasks
```

---

## Testing Checklist

- [ ] Test 1: DeepSeek-R1-Distill-14B Q4_K_M with tensor split
- [ ] Test 2: DeepSeek-R1-Distill-14B Q5_K_M with tensor split (if Test 1 works)
- [ ] Benchmark: Measure tokens/sec for each configuration
- [ ] Verify: Both GPUs show memory usage in nvidia-smi
- [ ] Document: Actual VRAM usage on each GPU
- [ ] Decide: Final model selection based on performance
- [ ] Download: Production models
- [ ] Update: Config files with actual production model paths

---

## Model Comparison Reference

| Model | Size (Q4_K_M) | MATH-500 | AIME 2024 | Best For |
|-------|---------------|----------|-----------|----------|
| **DeepSeek-R1-Distill-14B** | ~9GB | **93.9%** | **69.7%** | Deep Reasoning, CoT |
| **Qwen 2.5 32B** | ~20GB | 83% | ~65% | Large context, quality |
| **DeepSeek-R1-Distill-7B** | ~6GB | ~89% | 55.5% | Balanced reasoning |
| **Llama 3.1 8B** | ~7GB | ~70% | ~30% | Fast research |
| **Qwen 2.5 7B** | ~5.5GB | ~75% | ~35% | Fast research |

**Winner for Tier 2**: DeepSeek-R1-Distill-14B (best reasoning in class)

---

## Next Steps

1. **Transfer to production machine** (RTX 3060 Ti + GTX 1060)
2. **Run Test 1** (DeepSeek-R1-Distill-14B Q4_K_M with split)
3. **If successful**: Download Q5_K_M version for better quality
4. **If unsuccessful**: Download DeepSeek-R1-Distill-7B Q6_K as fallback
5. **Update model configs** in `config/models/`
6. **Re-run full test suite** on production hardware
7. **Document final configuration** in STATUS.md

---

**Status**: Documented, ready to test on production hardware
**Priority**: High - blocking production model downloads
**Estimated Time**: 1-2 hours testing + downloads
