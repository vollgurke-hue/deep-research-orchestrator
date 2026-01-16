# Context Window Monitoring System

**Datum**: 2026-01-02
**Status**: Konzept → Implementierung

---

## 🎯 Ziel

Vollständige Transparenz über Context-Nutzung während der Research-Execution:
- Welche Daten werden in den Prompt geladen?
- Wie viele Tokens pro Context-Teil?
- Wie viel Platz ist noch im Context-Fenster?
- Wann besteht Halluzinations-Gefahr?

---

## 📊 Context Window Struktur

### Komponenten eines Prompts

```
┌─────────────────────────────────────────┐
│ 1. System Prompt                        │ (statisch, ~500 tokens)
├─────────────────────────────────────────┤
│ 2. Technique Prompt Template            │ (statisch, ~200-800 tokens)
├─────────────────────────────────────────┤
│ 3. Previous Phase Outputs               │ (dynamisch, 0-10k tokens)
├─────────────────────────────────────────┤
│ 4. Current Phase Context                │ (dynamisch, 0-5k tokens)
├─────────────────────────────────────────┤
│ 5. User Input / Query                   │ (dynamisch, ~100-2k tokens)
├─────────────────────────────────────────┤
│ 6. Examples (optional)                  │ (statisch, ~500 tokens)
├─────────────────────────────────────────┤
│ 7. Output Buffer (reserved for answer)  │ (reserved, ~2k-8k tokens)
└─────────────────────────────────────────┘
```

---

## 🚦 Ampel-System für Token Usage

### Grün (Safe Zone): 0-60% des Context Window
```
████████████░░░░░░░░░░░░░░░░░░░░  40% (4096 / 10240 tokens)
✅ Safe - Genug Platz für Output
```

### Gelb (Warning Zone): 60-85% des Context Window
```
████████████████████████░░░░░░░░  75% (7680 / 10240 tokens)
⚠️  Warning - Context wird knapp, Output könnte gekürzt werden
```

### Rot (Danger Zone): 85-100% des Context Window
```
██████████████████████████████░░  92% (9420 / 10240 tokens)
🚨 Danger - Halluzinations-Gefahr! Context reduzieren!
```

---

## 📐 Modell-Spezifische Limits

```json
{
  "models": {
    "tier1_fast": {
      "model_id": "mistral-7b-instruct",
      "context_window": 8192,
      "safe_limit": 4915,     // 60%
      "warning_limit": 6963,   // 85%
      "output_buffer": 2048    // Reserved for answer
    },
    "tier2_quality": {
      "model_id": "mixtral-8x7b-instruct",
      "context_window": 32768,
      "safe_limit": 19661,
      "warning_limit": 27853,
      "output_buffer": 4096
    },
    "tier3_deep": {
      "model_id": "llama-70b-instruct",
      "context_window": 4096,
      "safe_limit": 2458,
      "warning_limit": 3482,
      "output_buffer": 1024
    }
  }
}
```

---

## 🔍 Context Loading Anzeige

### Während der Execution

```
┌───────────────────────────────────────────────────────────┐
│ 🔄 Loading Context for: Phase 0 → Workflow 2 → Step 3    │
├───────────────────────────────────────────────────────────┤
│                                                           │
│ ✅ System Prompt                           482 tokens    │
│ ✅ Technique: market_need_detector         356 tokens    │
│ ✅ Previous: competitor_analysis          2104 tokens    │
│ ✅ Previous: customer_interviews          1823 tokens    │
│ ✅ User Query: "AI tutoring app"           142 tokens    │
│ ⏳ Loading: Examples...                                   │
│                                                           │
├───────────────────────────────────────────────────────────┤
│ Total Context:                            4907 / 8192    │
│ ████████████░░░░░░░░░░░░░░░░░░░░  60% ✅ Safe           │
│                                                           │
│ Output Buffer Reserved:                   2048 tokens    │
│ Estimated Max Output:                     ~1500 words    │
└───────────────────────────────────────────────────────────┘
```

---

## 🔄 Iteration State Tracking

### Phase 1 (Excurse) - Iterative Loop

```json
{
  "iteration_state": {
    "current_phase": "phase_1_excurse",
    "current_iteration": 2,
    "max_iterations": 5,
    "iteration_history": [
      {
        "iteration": 1,
        "gaps_detected": [
          "Missing competitor pricing data",
          "No user retention metrics"
        ],
        "techniques_executed": ["gap_detector", "quick_web_research"],
        "context_loaded": {
          "previous_outputs": ["phase_0_output"],
          "tokens": 3420
        },
        "result": "gaps_found"
      },
      {
        "iteration": 2,
        "gaps_detected": [],
        "techniques_executed": ["validation_check"],
        "context_loaded": {
          "previous_outputs": ["phase_0_output", "iteration_1_output"],
          "tokens": 5840
        },
        "result": "complete"
      }
    ]
  }
}
```

### UI Visualization

```
┌─────────────────────────────────────────────────────────┐
│ 🔄 Phase 1: Excurse (Iteration 2 / 5)                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Iteration 1: ✅ Complete                                │
│   ├─ Gaps Detected: 2                                   │
│   ├─ Context Size: 3420 tokens                          │
│   └─ Duration: 12.4s                                    │
│                                                         │
│ Iteration 2: ⏳ In Progress...                          │
│   ├─ Current Step: validation_check                     │
│   ├─ Context Size: 5840 tokens (71% 🟡)                 │
│   └─ Elapsed: 8.2s                                      │
│                                                         │
│ Estimated Remaining: 0-3 iterations                     │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠️ Implementierung

### Backend: Token Counting

```python
# src/utils/token_counter.py

import tiktoken

class TokenCounter:
    def __init__(self, model_name: str):
        # Use appropriate encoding for model
        self.encoding = tiktoken.encoding_for_model(model_name)

    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.encoding.encode(text))

    def estimate_context_size(self, prompt_parts: dict) -> dict:
        """
        Estimate total context size from parts.

        Args:
            prompt_parts: {
                "system_prompt": str,
                "technique_prompt": str,
                "previous_outputs": [str],
                "user_input": str,
                "examples": str
            }

        Returns:
            {
                "breakdown": {
                    "system_prompt": 482,
                    "technique_prompt": 356,
                    "previous_outputs": 3927,
                    "user_input": 142,
                    "examples": 0
                },
                "total": 4907,
                "percentage": 59.9
            }
        """
        breakdown = {}
        total = 0

        for key, value in prompt_parts.items():
            if isinstance(value, list):
                tokens = sum(self.count_tokens(v) for v in value)
            else:
                tokens = self.count_tokens(value) if value else 0

            breakdown[key] = tokens
            total += tokens

        return {
            "breakdown": breakdown,
            "total": total,
            "percentage": (total / self.get_context_limit()) * 100
        }

    def get_context_limit(self) -> int:
        """Get context window limit for model."""
        # Model-specific limits
        limits = {
            "mistral-7b-instruct": 8192,
            "mixtral-8x7b-instruct": 32768,
            "llama-70b-instruct": 4096
        }
        return limits.get(self.model_name, 4096)

    def get_safety_status(self, token_count: int) -> dict:
        """
        Get safety status (green/yellow/red).

        Returns:
            {
                "status": "safe|warning|danger",
                "color": "green|yellow|red",
                "message": "descriptive message"
            }
        """
        limit = self.get_context_limit()
        percentage = (token_count / limit) * 100

        if percentage < 60:
            return {
                "status": "safe",
                "color": "green",
                "message": "Safe - Genug Platz für Output"
            }
        elif percentage < 85:
            return {
                "status": "warning",
                "color": "yellow",
                "message": "Warning - Context wird knapp"
            }
        else:
            return {
                "status": "danger",
                "color": "red",
                "message": "Danger - Halluzinations-Gefahr!"
            }
```

### Backend: Working State Extension

```python
# Extend working_state with context info

{
  "working_state": {
    "status": "in_progress",
    "progress": 45,
    "current_step": "Executing gap_detector...",
    "started_at": "2026-01-02T10:30:00Z",
    "updated_at": "2026-01-02T10:30:45Z",

    # NEW: Context info
    "context": {
      "loaded_data": [
        {"type": "system_prompt", "tokens": 482},
        {"type": "technique_prompt", "tokens": 356},
        {"type": "previous_output", "name": "competitor_analysis", "tokens": 2104},
        {"type": "user_input", "tokens": 142}
      ],
      "total_tokens": 3084,
      "context_limit": 8192,
      "percentage": 37.6,
      "safety_status": "safe"
    },

    # NEW: Iteration info (for Phase 1)
    "iteration": {
      "current": 2,
      "max": 5,
      "history": [...]
    }
  }
}
```

---

## 🎨 Frontend: Context Monitoring Component

### ContextMonitor.vue

```vue
<template>
  <div class="context-monitor">
    <div class="context-header">
      <h4>📊 Context Window</h4>
      <span class="model-label">{{ modelName }}</span>
    </div>

    <!-- Progress Bar with Traffic Light -->
    <div class="context-progress">
      <div class="progress-bar">
        <div
          class="progress-fill"
          :class="safetyStatus.color"
          :style="{ width: percentage + '%' }"
        >
          <span class="progress-text">
            {{ totalTokens }} / {{ contextLimit }} tokens ({{ percentage.toFixed(1) }}%)
          </span>
        </div>
      </div>

      <div class="safety-badge" :class="safetyStatus.color">
        {{ safetyStatus.icon }} {{ safetyStatus.message }}
      </div>
    </div>

    <!-- Context Breakdown -->
    <div class="context-breakdown">
      <h5>Geladener Kontext:</h5>
      <div
        v-for="item in loadedData"
        :key="item.type + item.name"
        class="context-item"
      >
        <span class="item-icon">{{ getIcon(item.type) }}</span>
        <span class="item-name">{{ getLabel(item) }}</span>
        <span class="item-tokens">{{ item.tokens }} tokens</span>
      </div>
    </div>

    <!-- Output Buffer Info -->
    <div class="output-buffer">
      <div class="buffer-label">
        Reserved für Output: {{ outputBuffer }} tokens
      </div>
      <div class="buffer-estimate">
        Geschätzte Max. Länge: ~{{ estimateWords(outputBuffer) }} Wörter
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  contextInfo: {
    type: Object,
    required: true
  },
  modelName: {
    type: String,
    default: 'mistral-7b-instruct'
  }
})

const totalTokens = computed(() => props.contextInfo.total_tokens || 0)
const contextLimit = computed(() => props.contextInfo.context_limit || 8192)
const percentage = computed(() => props.contextInfo.percentage || 0)
const loadedData = computed(() => props.contextInfo.loaded_data || [])

const outputBuffer = computed(() => {
  // Reserve 25% of context for output
  return Math.floor(contextLimit.value * 0.25)
})

const safetyStatus = computed(() => {
  const status = props.contextInfo.safety_status || 'safe'

  const statusMap = {
    safe: { color: 'green', icon: '✅', message: 'Safe - Genug Platz für Output' },
    warning: { color: 'yellow', icon: '⚠️', message: 'Warning - Context wird knapp' },
    danger: { color: 'red', icon: '🚨', message: 'Danger - Halluzinations-Gefahr!' }
  }

  return statusMap[status] || statusMap.safe
})

function getIcon(type) {
  const icons = {
    system_prompt: '⚙️',
    technique_prompt: '📝',
    previous_output: '📤',
    user_input: '👤',
    examples: '📚'
  }
  return icons[type] || '📄'
}

function getLabel(item) {
  if (item.name) return item.name

  const labels = {
    system_prompt: 'System Prompt',
    technique_prompt: 'Technique Prompt',
    previous_output: 'Previous Output',
    user_input: 'User Input',
    examples: 'Examples'
  }
  return labels[item.type] || item.type
}

function estimateWords(tokens) {
  // Rough estimate: 1 token ≈ 0.75 words
  return Math.floor(tokens * 0.75)
}
</script>

<style scoped>
.context-monitor {
  background: var(--bg-panel);
  border: 2px solid var(--border-medium);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1rem;
}

.context-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.model-label {
  background: var(--accent-gold);
  color: var(--bg-panel);
  padding: 0.25rem 0.75rem;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
}

.context-progress {
  margin-bottom: 1.5rem;
}

.progress-bar {
  height: 40px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.progress-fill {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: width 0.5s ease, background-color 0.3s ease;
  font-weight: 600;
  font-size: 0.9rem;
}

.progress-fill.green {
  background: linear-gradient(90deg, #22c55e, #16a34a);
}

.progress-fill.yellow {
  background: linear-gradient(90deg, #eab308, #f59e0b);
}

.progress-fill.red {
  background: linear-gradient(90deg, #ef4444, #dc2626);
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.safety-badge {
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-weight: 600;
  text-align: center;
}

.safety-badge.green {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
  border: 1px solid #22c55e;
}

.safety-badge.yellow {
  background: rgba(234, 179, 8, 0.2);
  color: #eab308;
  border: 1px solid #eab308;
}

.safety-badge.red {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
  border: 1px solid #ef4444;
}

.context-breakdown {
  margin-bottom: 1.5rem;
}

.context-breakdown h5 {
  color: var(--text-muted);
  font-size: 0.9rem;
  margin-bottom: 0.75rem;
}

.context-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem;
  border-bottom: 1px solid var(--border-light);
}

.item-icon {
  font-size: 1.2rem;
}

.item-name {
  flex: 1;
  color: var(--text-light);
}

.item-tokens {
  color: var(--accent-gold);
  font-weight: 600;
  font-family: 'Courier New', monospace;
}

.output-buffer {
  padding: 1rem;
  background: rgba(255, 179, 71, 0.1);
  border: 1px solid var(--accent-gold);
  border-radius: 8px;
}

.buffer-label {
  color: var(--accent-gold);
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.buffer-estimate {
  color: var(--text-muted);
  font-size: 0.9rem;
}
</style>
```

---

## 🔄 Integration in Execution Flow

### 1. Backend: Add to working_state

```python
# src/core/orchestrator.py

async def execute_technique(self, technique_id: str, context: dict):
    # Build prompt
    prompt_parts = {
        "system_prompt": self.system_prompt,
        "technique_prompt": technique.prompt,
        "previous_outputs": [output.content for output in context.get("previous_outputs", [])],
        "user_input": context.get("user_input", ""),
        "examples": technique.get("examples", "")
    }

    # Count tokens
    token_counter = TokenCounter(technique.model)
    context_info = token_counter.estimate_context_size(prompt_parts)

    # Update working state with context info
    technique.working_state.context = {
        "loaded_data": [
            {"type": "system_prompt", "tokens": context_info["breakdown"]["system_prompt"]},
            {"type": "technique_prompt", "tokens": context_info["breakdown"]["technique_prompt"]},
            # ... etc
        ],
        "total_tokens": context_info["total"],
        "context_limit": token_counter.get_context_limit(),
        "percentage": context_info["percentage"],
        "safety_status": token_counter.get_safety_status(context_info["total"])["status"]
    }

    # Execute...
```

### 2. Frontend: Add to ExecutionView

```vue
<template>
  <div class="execution-view">
    <!-- Context Monitor -->
    <ContextMonitor
      v-if="currentExecution?.working_state?.context"
      :context-info="currentExecution.working_state.context"
      :model-name="currentExecution.model"
    />

    <!-- Iteration State (for Phase 1) -->
    <IterationViewer
      v-if="currentExecution?.working_state?.iteration"
      :iteration-state="currentExecution.working_state.iteration"
    />

    <!-- Working State -->
    <WorkingStateViewer :execution-state="currentExecution" />
  </div>
</template>
```

---

## ✅ Success Metrics

- ✅ Token count für jeden Context-Teil
- ✅ Ampel-Visualisierung (grün/gelb/rot)
- ✅ Modell-spezifische Limits
- ✅ Echtzeit-Tracking während Execution
- ✅ Halluzinations-Warnung bei >85%
- ✅ Reserved Output Buffer anzeigen
- ✅ Iteration State für Phase 1

---

## 🚀 Next Steps

1. Implement `TokenCounter` class in backend
2. Extend `working_state` schema with `context` field
3. Create `ContextMonitor.vue` component
4. Create `IterationViewer.vue` component
5. Integrate into ExecutionView
6. Test with verschiedenen Models (tier1/tier2/tier3)

---

**Status**: Konzept abgeschlossen → Ready for Implementation 🚀
