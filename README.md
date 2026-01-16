# Deep Research Orchestrator (SRO)

> **Sovereign Research Orchestrator** - AI-powered research system with Multi-variant Chain-of-Thought reasoning, Reddit validation, and Knowledge Graph construction.

[![Status](https://img.shields.io/badge/Status-Sprint%203%20Complete-success)]()
[![LOC](https://img.shields.io/badge/LOC-13.6k-blue)]()
[![Tests](https://img.shields.io/badge/Tests-Passing-success)]()
[![Python](https://img.shields.io/badge/Python-3.10+-blue)]()

---

## 🎯 What is This?

SRO (Sovereign Research Orchestrator) is an advanced AI research system that combines:

- **🌲 Tree-of-Thought (ToT) Reasoning**: MCTS-guided exploration of research questions
- **🎭 Generative CoT**: 3 reasoning variants per node (Analytical, Empirical, Theoretical)
- **⚖️ Process Reward Model**: Step-wise verification of reasoning quality
- **🔍 Reddit Validation**: Compare AI hypotheses against real human experiences
- **🏆 Tiered Knowledge Graph**: Bronze/Silver/Gold fact classification
- **🧠 Multi-Source Verification**: Cross-reference facts from multiple sources
- **🔒 100% Local**: No cloud dependencies, full privacy

---

## 📊 Project Status

### Completed Sprints

| Sprint | Status | LOC | Description |
|--------|--------|-----|-------------|
| **Sprint 1: Foundation** | ✅ COMPLETE | ~5,000 | SPO Database, MCTS Engine, ToT Manager, Graph Manager |
| **Sprint 2: Intelligence** | ✅ COMPLETE | ~1,320 | Generative CoT, Process Reward Model, Multi-variant Selection |
| **Sprint 3: Verification** | ✅ COMPLETE | ~1,620 | Reddit Scraper, Friction Detector, Consensus Scorer |
| **Sprint 4: Scaling** | ⏳ PENDING | - | Recursive LLM, CEO-Worker Architecture |
| **Sprint 5: Polish** | ⏳ PENDING | - | GUI, Visualization, Export |

**Total Code:** 13,636 LOC in `src/core/`
**Version:** 0.3.0 (Sprint 3 Complete)
**Status:** Active Development

---

## 🏗️ Architecture Overview

```
User Query
    ↓
ToT Manager (Tree-of-Thought)
    ↓
MCTS Engine (Monte Carlo Tree Search)
    ↓
CoT Generator (3 reasoning variants)
    ├─ Variant A: Analytical (T=0.7)
    ├─ Variant B: Empirical (T=0.8)
    └─ Variant C: Theoretical (T=0.9)
    ↓
Process Reward Model (score each step)
    ↓
Select Best Variant
    ↓
SPO Extractor (extract facts)
    ↓
Multi-Source Verifier (cross-reference)
    ↓
Reddit Validator (compare with humans)
    ↓
Tiered Knowledge Graph (Bronze/Silver/Gold)
```

See [ARCHITECTURE_VISUAL.md](docs/ARCHITECTURE_VISUAL.md) for detailed diagrams.

---

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.10+
python3 --version

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```python
from src.core.graph_manager import GraphManager
from src.core.tot_manager import ToTManager
from src.core.model_orchestrator import ModelOrchestrator

# Setup
graph = GraphManager(spo_db_path="knowledge.db")
llm = ModelOrchestrator(profile="standard")

# Create ToT Manager with Sprint 2 features
tot = ToTManager(
    graph_manager=graph,
    model_orchestrator=llm,
    enable_generative_cot=True,  # 3 reasoning variants!
    cot_variant_count=3
)

# Research a question
root_id = tot.create_root("What are the benefits of renewable energy?")
child_ids = tot.decompose_question(root_id, branching_factor=3)

# Expand nodes (generates 3 variants, scores, selects best)
for child_id in child_ids:
    tot.expand_node(child_id)

# View results
node = tot.tree[child_ids[0]]
print(f"Generated {len(node.cot_variants)} reasoning variants")
print(f"Selected best: {node.selected_variant_id}")
```

---

## 🔥 Key Features

### 1. Generative Chain-of-Thought (Sprint 2)

Generate **3 reasoning variants** per node instead of just 1:

- **Variant A (Analytical)**: Deductive reasoning, logical structure
- **Variant B (Empirical)**: Evidence-based, real-world examples
- **Variant C (Theoretical)**: First principles, frameworks

Each variant is scored by the **Process Reward Model** and the best is selected.

### 2. Reddit Validation (Sprint 3)

Compare AI hypotheses against real human experiences:

```python
AI says: "Product X has excellent reliability"
Reddit says: 7 negative posts, 5 positive posts
→ Friction Score: 0.693
→ Verdict: FRICTION_DETECTED ⚠️
→ Downgrade confidence
```

### 3. Tiered Knowledge Graph

Facts are classified into **3 tiers**:

- **🥉 Bronze**: Unverified, low confidence
- **🥈 Silver**: Cross-verified from 3+ sources
- **🥇 Gold**: High confidence, Reddit-validated

---

## 📚 Documentation

### Quick Start
- [PROJECT_QUICK_REFERENCE.md](docs/PROJECT_QUICK_REFERENCE.md) - 5-minute overview
- [ARCHITECTURE_VISUAL.md](docs/ARCHITECTURE_VISUAL.md) - Visual diagrams

### Detailed Status
- [PROJECT_STATUS_COMPREHENSIVE.md](docs/PROJECT_STATUS_COMPREHENSIVE.md) - Full 60+ page status
- [SPRINT_2_COMPLETE.md](docs/SPRINT_2_COMPLETE.md) - Sprint 2 details
- [SPRINT_3_COMPLETE.md](docs/SPRINT_3_COMPLETE.md) - Sprint 3 details

### Concepts
- [SRO_ARCHITECTURE_OVERVIEW.md](docs/concepts/SRO_ARCHITECTURE_OVERVIEW.md) - Original architecture
- [XOT_GENERATIVE_COT_CONCEPT.md](docs/concepts/XOT_GENERATIVE_COT_CONCEPT.md) - CoT concept
- [REDDIT_VALIDATION_CONCEPT.md](docs/concepts/REDDIT_VALIDATION_CONCEPT.md) - Reddit validation

---

## 🧪 Testing

```bash
# Unit tests (fast, no LLM required)
python test_sprint2_unit.py          # Process Reward Model tests
python test_sprint3_reddit_validation.py  # Reddit validation tests

# Integration tests (requires LLM)
python test_sprint2_generative_cot.py
python test_cluster1_e2e.py
```

### Test Status

| Test Type | Status | Details |
|-----------|--------|---------|
| Unit Tests (LLM-free) | ✅ 100% | All passing |
| Integration (Mock) | ✅ 100% | Sprint 2 & 3 passing |
| Integration (LLM) | ⏳ | Awaiting hardware |

---

## 🛣️ Roadmap

### Immediate (without LLM hardware)
- [ ] MCTS Engine optimizations
- [ ] Graph visualization (NetworkX)
- [ ] CLI tools
- [ ] GUI improvements

### Future (requires LLM)
- [ ] Sprint 4: Recursive LLM
- [ ] Sprint 4: CEO-Worker Architecture
- [ ] Sprint 5: Full GUI integration
- [ ] Real Reddit API integration

---

## 🤝 Contributing

Research project exploring:
- Advanced reasoning (CoT, ToT, MCTS)
- Human-AI alignment (Reddit validation)
- Knowledge graph construction
- Test-time compute scaling (OpenAI o1-style)

---

## 🙏 Acknowledgments

Inspired by:
- OpenAI o1 (test-time compute scaling)
- DeepMind Self-Echoing Search
- Anthropic Constitutional AI
- Gemini's SRO architecture plan

---

## 📝 License

TBD

---

**Built with ❤️ and 🤖 Claude Code**

Last Updated: 2026-01-16
