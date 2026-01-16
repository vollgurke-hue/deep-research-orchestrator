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
          <span class="progress-text" v-if="percentage > 15">
            {{ totalTokens }} / {{ contextLimit }} tokens ({{ percentage.toFixed(1) }}%)
          </span>
        </div>
      </div>

      <div class="safety-badge" :class="safetyStatus.color">
        {{ safetyStatus.icon }} {{ safetyStatus.message }}
      </div>
    </div>

    <!-- Context Breakdown -->
    <div class="context-breakdown" v-if="loadedData.length > 0">
      <h5>Geladener Kontext:</h5>
      <div
        v-for="(item, idx) in loadedData"
        :key="idx"
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

const totalTokens = computed(() => props.contextInfo?.total_tokens || 0)
const contextLimit = computed(() => props.contextInfo?.context_limit || 8192)
const percentage = computed(() => props.contextInfo?.percentage || 0)
const loadedData = computed(() => props.contextInfo?.loaded_data || [])

const outputBuffer = computed(() => {
  // Get from context info or calculate 25% of limit
  return props.contextInfo?.output_buffer || Math.floor(contextLimit.value * 0.25)
})

const safetyStatus = computed(() => {
  const status = props.contextInfo?.safety_status || 'safe'

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
    examples: '📚',
    context: '📋'
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
    examples: 'Examples',
    context: 'Context Data'
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
  background: var(--bg-panel, #0A0A0A);
  border: 2px solid var(--border-medium, rgba(255, 255, 255, 0.3));
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

.context-header h4 {
  margin: 0;
  color: var(--text-main, #FFF5E6);
  font-size: 1.1rem;
}

.model-label {
  background: var(--accent-gold, #FFB347);
  color: var(--bg-panel, #0A0A0A);
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
  position: relative;
}

.progress-fill {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: width 0.5s ease, background-color 0.3s ease;
  font-weight: 600;
  font-size: 0.9rem;
  position: relative;
}

.progress-text {
  color: white;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
  z-index: 1;
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
  font-size: 0.9rem;
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
  color: var(--text-muted, #C9B299);
  font-size: 0.9rem;
  margin: 0 0 0.75rem 0;
  font-weight: 600;
}

.context-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem;
  border-bottom: 1px solid var(--border-light, rgba(255, 255, 255, 0.2));
}

.context-item:last-child {
  border-bottom: none;
}

.item-icon {
  font-size: 1.2rem;
}

.item-name {
  flex: 1;
  color: var(--text-light, #F5E6D3);
}

.item-tokens {
  color: var(--accent-gold, #FFB347);
  font-weight: 600;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
}

.output-buffer {
  padding: 1rem;
  background: rgba(255, 179, 71, 0.1);
  border: 1px solid var(--accent-gold, #FFB347);
  border-radius: 8px;
}

.buffer-label {
  color: var(--accent-gold, #FFB347);
  font-weight: 600;
  margin-bottom: 0.25rem;
  font-size: 0.9rem;
}

.buffer-estimate {
  color: var(--text-muted, #C9B299);
  font-size: 0.85rem;
}
</style>
