# Multi-AI Workflow - Quickstart Guide

**Last Updated:** 2025-12-31
**Status:** ✅ Fully Implemented and Tested

---

## Overview

The Multi-AI Workflow allows you to leverage the best of multiple AI models (Claude, GPT-4, Gemini) by:
1. Generating a high-quality research prompt locally
2. Manually querying multiple cloud AIs
3. Analyzing their responses for contradictions and blind spots
4. Generating a synthesis report combining the best insights

**Total Time:** ~15-30 minutes (depending on AI response times)

---

## Prerequisites

- ✅ Deep Research Orchestrator installed
- ✅ Access to at least 2 of: Claude, GPT-4, Gemini (free tiers work!)
- ✅ TinyLlama or better model for local analysis

---

## Step 1: Generate Research Prompt

### Option A: Python Script

```python
from pathlib import Path
from src.tools.multi_ai.prompt_generator import MultiAIPromptGenerator

# Create generator
generator = MultiAIPromptGenerator()

# Generate prompt
prompt = generator.create_prompt(
    topic="AI Tutoring Apps Market Analysis",
    categories=[
        "market_size",
        "competition",
        "trends",
        "technical_feasibility",
        "monetization"
    ],
    output_format="markdown",
    depth="comprehensive"
)

# Save to file
save_path = generator.save_prompt(
    prompt=prompt,
    topic="AI Tutoring Apps Market Analysis"
)

print(f"Prompt saved to: {save_path}")
print("\nNext steps:")
print("1. Open the file")
print("2. Copy the prompt")
print("3. Query Claude, GPT-4, and Gemini")
```

**Run:**
```bash
cd deep-research-orchestrator
python3 -c "from src.tools.multi_ai.prompt_generator import MultiAIPromptGenerator; \
g = MultiAIPromptGenerator(); \
p = g.create_prompt('AI Tutoring Market', ['market_size', 'competition']); \
path = g.save_prompt(p, 'AI Tutoring Market'); \
print(f'Saved to: {path}')"
```

### Option B: Interactive Python

```bash
cd deep-research-orchestrator
python3

>>> from src.tools.multi_ai.prompt_generator import MultiAIPromptGenerator
>>> generator = MultiAIPromptGenerator()
>>> prompt = generator.create_prompt(
...     topic="Your Topic Here",
...     categories=["market_size", "competition", "trends"]
... )
>>> path = generator.save_prompt(prompt, "Your Topic")
>>> print(path)
```

**Available Categories:**
- `market_size` - Market size, TAM/SAM/SOM, growth projections
- `competition` - Competitive landscape, top players, market share
- `trends` - Technology trends, regulatory trends, future outlook
- `technical_feasibility` - Tech stack, challenges, timeline
- `monetization` - Pricing models, unit economics, revenue
- `user_needs` - Pain points, personas, willingness to pay
- `risks` - Market, technical, regulatory risks
- `go_to_market` - Channels, launch strategy, partnerships

---

## Step 2: Query External AIs

### 2.1 Open the Prompt File

```bash
# The prompt was saved to research-prompts/
cat research-prompts/prompt_*.md

# Or find the latest:
ls -lt research-prompts/ | head -2
```

### 2.2 Query Claude

1. Open https://claude.ai
2. Start a new conversation
3. Paste the ENTIRE prompt
4. Wait for response (30-60 seconds)
5. Copy the response
6. Save to `research-data/multi-ai/claude_response.md`

```bash
# Create directory if needed
mkdir -p research-data/multi-ai/

# Save Claude's response
# (Copy-paste into a text editor, then save as claude_response.md)
```

### 2.3 Query GPT-4

1. Open https://chat.openai.com
2. Start a new conversation
3. Paste the SAME prompt
4. Wait for response
5. Copy the response
6. Save to `research-data/multi-ai/gpt4_response.md`

### 2.4 Query Gemini

1. Open https://gemini.google.com
2. Start a new conversation
3. Paste the SAME prompt
4. Wait for response
5. Copy the response
6. Save to `research-data/multi-ai/gemini_response.md`

**Tips:**
- Use the exact same prompt for all AIs
- Use the best available model (Claude 3.5 Sonnet, GPT-4, Gemini 1.5 Pro)
- Free tiers work fine!
- If an AI refuses or gives incomplete answer, rephrase slightly

---

## Step 3: Analyze Responses

### Option A: Full Analysis with Orchestrator

```python
from pathlib import Path
from src.tools.multi_ai.response_analyzer import analyze_multi_ai_responses

# Analyze all responses
analysis = analyze_multi_ai_responses(
    response_dir=Path("research-data/multi-ai/")
)

# View contradictions
print("\n=== CONTRADICTIONS ===")
for contradiction in analysis.get("contradictions", []):
    print(f"\nTopic: {contradiction.get('topic')}")
    print(f"Details: {contradiction.get('details')}")

# View blind spots
print("\n=== BLIND SPOTS ===")
for ai_name, spots in analysis.get("blind_spots", {}).items():
    print(f"\n{ai_name} missed:")
    for spot in spots:
        print(f"  - {spot}")

# View synthesis
print("\n=== SYNTHESIS ===")
print(analysis.get("synthesis", "No synthesis generated"))

# Confidence score
print(f"\n=== CONFIDENCE: {analysis.get('confidence_score', 0):.0%} ===")
```

**Run:**
```bash
cd deep-research-orchestrator

python3 << 'EOF'
from pathlib import Path
from src.tools.multi_ai.response_analyzer import analyze_multi_ai_responses

analysis = analyze_multi_ai_responses(Path("research-data/multi-ai/"))

print("\n" + "="*70)
print("MULTI-AI ANALYSIS RESULTS")
print("="*70)
print(f"\nSources: {', '.join(analysis['sources'])}")
print(f"Confidence: {analysis['confidence_score']:.0%}")
print(f"\nSynthesis:\n{analysis['analyses']['synthesis']}")
EOF
```

### Option B: Manual Analysis (No LLM Required)

```python
from pathlib import Path
from src.tools.multi_ai.response_analyzer import MultiAIResponseAnalyzer

analyzer = MultiAIResponseAnalyzer()

# Load responses
responses = analyzer._load_responses(Path("research-data/multi-ai/"))

print(f"Loaded {len(responses)} responses:")
for ai_name, content in responses.items():
    print(f"  - {ai_name}: {len(content)} characters")

# You can now manually compare them
```

---

## Step 4: Save Results

The analysis automatically saves a synthesis report to:
```
research-data/validations/synthesis_TIMESTAMP.md
```

To find the latest:
```bash
ls -lt research-data/validations/ | head -2
cat research-data/validations/synthesis_*.md
```

---

## Example: Complete Workflow

```bash
# 1. Generate prompt
cd deep-research-orchestrator

python3 << 'EOF'
from src.tools.multi_ai.prompt_generator import MultiAIPromptGenerator

g = MultiAIPromptGenerator()
p = g.create_prompt(
    topic="AI Code Assistants Market 2025",
    categories=["market_size", "competition", "trends", "monetization"]
)
path = g.save_prompt(p, "AI Code Assistants")
print(f"\n✓ Prompt saved: {path}")
print(f"\n{'='*70}")
print("NEXT: Copy this prompt to Claude, GPT-4, and Gemini")
print(f"{'='*70}\n")
print(p)
EOF

# 2. Open the prompt
cat research-prompts/prompt_*Code_Assistants*.md

# 3. Query AIs manually (copy-paste prompt to each AI)
# 4. Save responses to research-data/multi-ai/

# 5. Analyze
python3 << 'EOF'
from pathlib import Path
from src.tools.multi_ai.response_analyzer import analyze_multi_ai_responses

analysis = analyze_multi_ai_responses(Path("research-data/multi-ai/"))
print(analysis["analyses"]["synthesis"])
EOF
```

---

## Troubleshooting

### "No responses found"

Make sure you saved the AI responses with the correct filenames:
- `claude_response.md`
- `gpt4_response.md`
- `gemini_response.md`

And they're in: `research-data/multi-ai/`

### "Orchestrator not found" or import errors

Make sure you're in the project root:
```bash
cd deep-research-orchestrator
pwd  # Should show: .../deep-research-orchestrator
```

### LLM analysis fails

The local LLM (TinyLlama, Qwen, etc.) needs to be running. If you get errors:
1. Check llama-server is accessible
2. Or use the manual analysis (Option B) to just load and view responses

### Responses are in different format

The analyzer works with markdown files. If you have JSON or other formats:
1. Convert to markdown, or
2. Paste the content into a `.md` file

---

## Tips for Best Results

### Prompt Quality
- Use specific, focused topics
- Include 3-5 categories (not too many)
- Add additional context if needed

### AI Selection
- Use the latest models (Claude 3.5 Sonnet, GPT-4 Turbo, Gemini 1.5 Pro)
- Free tiers work, but paid gives better quality
- Query all 3 for best cross-validation

### Response Handling
- Copy the full response (don't truncate)
- Save immediately (don't lose them)
- Use consistent filenames

### Analysis
- Review contradictions carefully - they may reveal biases
- Blind spots are valuable - each AI has different knowledge
- Synthesis combines best of all - use this as your final source

---

## What You Get

**From the Synthesis Report:**

1. **Consensus Facts** - What all AIs agree on (high confidence)
2. **Contradictions** - Where AIs disagree (needs further research)
3. **Unique Insights** - What only one AI mentioned (may be blind spots for others)
4. **Confidence Scores** - How reliable each claim is
5. **Comprehensive Analysis** - Best-of-all-worlds report

**Why This Matters:**
- Reduces hallucinations (if all 3 say same thing → likely true)
- Finds gaps (what one AI missed)
- Balances biases (each AI has different training data)
- Saves costs (only 3 queries instead of 100)

---

## Next Steps

After getting your synthesis:

1. **Act on high-confidence consensus** - These are likely facts
2. **Research contradictions** - Look up primary sources
3. **Fill blind spots** - Do targeted research on gaps
4. **Iterate** - Generate follow-up prompts for deep dives

---

## Advanced: Automating with API Keys (Optional)

If you have API keys for Claude/GPT-4/Gemini, you could automate Step 2:

```python
# NOT IMPLEMENTED YET - Future feature
# For now, manual copy-paste is intentional (gives you control)
```

**Why manual?**
- ✅ No API costs (use free tiers)
- ✅ No rate limits
- ✅ You control what gets sent
- ✅ You can edit responses before analysis

---

**Questions?** Check the full documentation in `docs/` or the Implementation Report.
