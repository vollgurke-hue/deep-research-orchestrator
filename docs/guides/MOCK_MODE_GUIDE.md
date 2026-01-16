# Mock Mode Configuration Guide

## Overview

The Deep Research Orchestrator now supports **Mock Mode** - a testing mode that allows you to test the complete workflow without needing functional local models. This is essential for:

- Testing on weak hardware (e.g., GTX 980 with limited VRAM)
- Verifying workflow logic without waiting for model inference
- Frontend development and UI testing
- Functionality testing (not quality testing)

## Current Status

✅ **Mock Mode is ACTIVE by default** (as of 2026-01-04)

### Components in Mock Mode:

1. **ResearchQualityHelper** (`src/services/research_quality_helper.py`)
   - Returns realistic quality scores and improvement suggestions
   - No llama-server started

2. **ResearchGenerator** (`src/services/research_generator.py`)
   - Returns mock thematic structures with realistic data
   - Returns mock blindspot detection results
   - Returns mock deep research prompts
   - No llama-server started

### Tested Functionality:

- ✅ Step 0: Quality Evaluation - WORKING
- ✅ Step 1: Theme Generation - WORKING
- ⏳ Step 2-6: Coverage, blindspots, prompts - READY (not yet tested)

## How to Switch Between Modes

### Option 1: Change Default in Code (Recommended)

**For ResearchQualityHelper:**

Edit `src/services/research_quality_helper.py`, line 27:

```python
# MOCK MODE:
def __init__(self, model_config_path: str = None, use_mock: bool = True):  # <-- Change to False for real mode
```

**For ResearchGenerator:**

Edit `src/services/research_generator.py`, line 29:

```python
# MOCK MODE:
def __init__(self, use_mock: bool = True):  # <-- Change to False for real mode
```

**For Backend API:**

Edit `viewer/serve_gui.py`, replace all instances:

```python
generator = ResearchGenerator(use_mock=True)  # <-- Change to False for real mode
```

### Option 2: Environment Variable (Future Enhancement)

*Not yet implemented - consider adding:*

```python
import os
USE_MOCK = os.getenv("USE_MOCK_MODE", "true").lower() == "true"
```

## Testing Mock Mode

### Test Step 0 (Quality Evaluation):

```bash
python3 << 'EOF'
from src.services.research_quality_helper import ResearchQualityHelper

helper = ResearchQualityHelper(use_mock=True)
result = helper.evaluate_research_input(
    description="AI Tutoring SaaS for education",
    goal="Market validation and feasibility study",
    research_type="product"
)
print(f"Quality Score: {result['quality_score']}%")
print(f"Suggestions: {len(result['suggestions'])}")
EOF
```

Expected Output:
```
Quality Score: 75%
Suggestions: 5
```

### Test Step 1 (Theme Generation):

```bash
python3 << 'EOF'
from src.services.research_generator import ResearchGenerator

generator = ResearchGenerator(use_mock=True)
result = generator.generate_thematic_structure(
    user_input="AI Tutoring SaaS",
    research_goal="Market validation",
    research_type="product"
)
print(f"Themes: {len(result['thematic_hierarchy'])}")
print(f"First theme: {result['thematic_hierarchy'][0]['theme_name']}")
EOF
```

Expected Output:
```
Themes: 3
First theme: Marktanalyse
```

## Mock Data Structure

### Quality Evaluation Response:

```json
{
  "quality_score": 75,
  "description_score": 70,
  "goal_score": 80,
  "strengths": ["Clear target audience", "Specific features", "Well-defined segment"],
  "weaknesses": ["Missing budget", "No team size", "Timeline not specified"],
  "suggestions": ["Add budget range", "Clarify metrics", "Specify outcomes", ...],
  "improved_description": "Enhanced version...",
  "improved_goal": "Enhanced version..."
}
```

### Theme Generation Response:

```json
{
  "thematic_hierarchy": [
    {
      "theme_id": "market_analysis",
      "theme_name": "Marktanalyse",
      "description": "Comprehensive market analysis",
      "relevance_score": 95,
      "confidence": 0.92,
      "sub_themes": [...]
    },
    ...
  ]
}
```

## Known Issues & Limitations

### Current Limitations:

1. **tiktoken dependency optional**: If not installed, token counting uses approximation
2. **No model quality testing**: Mock data is realistic but not AI-generated
3. **Fixed responses**: Same input always produces same mock output

### Why Mock Mode is Needed:

**Problem**: On weak hardware (GTX 980 with 4GB VRAM):
- TinyLlama (1.1B) - Too weak for structured JSON output
- Phi-3 Mini (3.8B) - Can load but prompts too complex for reliable JSON generation

**Solution**: Use Mock Mode for **functionality testing** now, switch to Real Mode with better hardware later for **quality testing**.

## Migration Plan: Mock → Real

When you have access to better hardware (e.g., RTX 4090, more VRAM):

1. **Install better model** (e.g., Mixtral 8x7B, Llama 3 70B)
2. **Update model config** in `config/models/tier1_fast.json`
3. **Switch mode flags** to `use_mock=False` in:
   - `src/services/research_quality_helper.py`
   - `src/services/research_generator.py`
   - `viewer/serve_gui.py` (all 6 endpoints)
4. **Install tiktoken**: `pip install tiktoken`
5. **Test with real model** using same test scripts above
6. **Compare quality**: Real AI responses vs Mock responses

## Architecture Benefits

### Key Design Decisions:

✅ **Separation of Concerns**: Mock logic in same file as real logic
✅ **No Code Duplication**: One flag controls mode switching
✅ **Easy Testing**: Mock mode requires zero dependencies
✅ **Gradual Migration**: Can switch services individually

### Files Modified for Mock Mode:

- `src/services/research_quality_helper.py` - Quality evaluation with mock support
- `src/services/research_generator.py` - Theme generation with mock support
- `src/models/llama_cpp_client.py` - Better error handling, won't crash on weak hardware
- `viewer/serve_gui.py` - All 6 research endpoints use mock mode by default

## Troubleshooting

### "Address already in use" Error:

```bash
fuser -k 8002/tcp
pkill -9 -f serve_gui
pkill -9 llama-server
./start_gui.sh --port 8002 --host 0.0.0.0
```

### "llama-server crashed" Error in Mock Mode:

This shouldn't happen in mock mode. Check:
1. Is `use_mock=True` set in the service initialization?
2. Did you clear Python cache after changes? `find . -type d -name "__pycache__" -exec rm -rf {} +`
3. Are you using the system Python or venv? Backend uses system Python3.

### Import Errors:

Mock mode should work without any special dependencies. If you see import errors, the code is trying to use real mode features.

## Next Steps

1. ✅ Activate Mock Mode (DONE)
2. ✅ Test Step 0 Quality Evaluation (DONE)
3. ✅ Test Step 1 Theme Generation (DONE)
4. ⏳ Test complete workflow end-to-end (Steps 2-6)
5. ⏳ Switch to Real Mode when better hardware available
6. ⏳ Compare Mock vs Real quality outputs

---

**Last Updated**: 2026-01-04
**Mock Mode Version**: 1.0
**Status**: ACTIVE and WORKING ✅
