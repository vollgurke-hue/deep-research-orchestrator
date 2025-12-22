# Deep Research Orchestrator

Local-first deep research system with abliterated models for unbiased analysis.

## Features

- 🤖 **Multi-Agent System**: Fast researcher + Quality validator agents
- 🔄 **Iterative Workflows**: Automatic gap detection and refinement
- 🌐 **Multi-AI Integration**: Manual orchestration with Claude, GPT-4, Gemini
- 🧠 **Abliterated Models**: Unbiased research without censorship
- 🔒 **100% Local**: No cloud dependencies, full privacy
- 📊 **Logic Builder**: Composable workflow building blocks

## Hardware Requirements

- **GPU**: NVIDIA RTX 3060 Ti (8GB VRAM) or similar
- **RAM**: 15GB+ system RAM
- **Disk**: ~30GB for models

## Quick Start

```bash
# 1. Clone and setup
git clone <repo>
cd deep-research-orchestrator

# 2. Install dependencies
pip install -e .

# 3. Setup llama.cpp
./scripts/setup_llama_cpp.sh

# 4. Download models
./scripts/download_models.sh

# 5. Start GUI
python gui/app.py
```

## Documentation

See `docs/` for:
- Architecture plans
- Framework documentation
- Setup guides

## Project Status

**Version:** 0.1.0 (Sprint 1)
**Status:** Active Development

## License

TBD
